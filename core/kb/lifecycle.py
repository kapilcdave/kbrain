"""Deterministic hypothesis pipeline. LLMs propose and do work; this code decides what happens next.

idea --researcher writes complete prereg--> prereg (frozen + hashed) --> backtest
backtest --blocked on data--> data (engineer builds collectors; harness runs them) --> backtest again
backtest --metrics graded by code--> review (skeptic) | rejected | parked
review --skeptic verdict--> validated | rejected | parked
Anti-spiral: dedup, per-hypothesis caps, max open hypotheses, stall detection.
"""
import hashlib, json, re, shutil, time
from datetime import date
from pathlib import Path
from . import gates
from .db import STATE, event, add_task
from . import jobs

TERMINAL = ("validated", "rejected", "parked")
STOPWORDS = {"the", "a", "an", "of", "for", "and", "to", "in", "on", "with", "test", "draft", "prereg", "hypothesis"}
SLUG = re.compile(r"[a-z0-9][a-z0-9-]{2,60}")

def L(cfg, sec, key, default):
    return cfg.get(sec, {}).get(key, default)

def fingerprint(role, hypothesis, title):
    words = sorted(set(re.findall(r"[a-z0-9]+", title.lower())) - STOPWORDS)
    return hashlib.sha1(f"{role}|{hypothesis or ''}|{' '.join(words)}".encode()).hexdigest()[:16]

def hyp(c, slug):
    return c.execute("SELECT * FROM hypotheses WHERE slug=?", (slug,)).fetchone()

def open_count(c):
    return c.execute(f"SELECT COUNT(*) FROM hypotheses WHERE status NOT IN {TERMINAL}").fetchone()[0]

def waiting_on_data(c):
    return c.execute("SELECT COUNT(*) FROM hypotheses WHERE status='data'").fetchone()[0]

def is_author(cfg, role):
    """Roles that write preregistrations: the generic researcher or a venue bro."""
    return role == "researcher" or bool(cfg["roles"].get(role, {}).get("venue_bro"))

def venue_of(c, cfg, slug):
    h = hyp(c, slug) if slug else None
    v = h["domain"] if h else None
    return v if v and cfg["roles"].get(v, {}).get("venue_bro") else None

def open_slots(c, cfg):
    return max(0, L(cfg, "limits", "max_open_hypotheses", 5) - open_count(c))

def set_status(c, slug, status, reason=None, path=None, prereg_sha=None):
    c.execute("UPDATE hypotheses SET status=?, reason=COALESCE(?,reason), path=COALESCE(?,path),"
              " prereg_sha=COALESCE(?,prereg_sha), updated=? WHERE slug=?",
              (status, reason, path, prereg_sha, time.time(), slug))
    event(c, "lifecycle", "hyp.status", None, hypothesis=slug, status=status, reason=reason)
    if status == "rejected":
        STATE.mkdir(parents=True, exist_ok=True)
        with open(STATE / "dead-ends.md", "a") as f:
            f.write(f"- {date.today()} {slug}: rejected. {reason}\n")
    if status == "validated":
        event(c, "lifecycle", "alert.validated", None, hypothesis=slug)

def spawn(c, parent, role, title, spec):
    return add_task(c, role, title, spec, parent_id=parent["id"], hypothesis=parent["hypothesis"],
                    depth=parent["depth"] + 1, actor="lifecycle",
                    fingerprint=fingerprint(role, parent["hypothesis"], title))

def admit(c, cfg, parent, nt):
    """Why a chief-proposed task is refused, or None to accept."""
    roles, role, title = cfg["roles"], nt.get("role"), nt.get("title") or ""
    if role not in roles:
        return "unknown role"
    allowed = roles[parent["role"]].get("spawnable")
    if allowed is not None and role not in allowed:
        return f"{parent['role']} may not spawn {role}"
    if parent["depth"] + 1 > L(cfg, "limits", "max_depth", 3):
        return "too deep"
    if c.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('queued','running')").fetchone()[0] >= L(cfg, "limits", "max_queued", 50):
        return "queue full"
    slug = nt.get("hypothesis")
    if is_author(cfg, role):
        if not slug or not SLUG.fullmatch(slug):
            return "a prereg task needs a new kebab-case hypothesis slug"
        if (h := hyp(c, slug)):
            return f"hypothesis {slug} already exists ({h['status']})"
        if open_slots(c, cfg) <= 0:
            return "no open hypothesis slots; finish existing work first"
        if (w := waiting_on_data(c)) >= L(cfg, "limits", "max_waiting_on_data", 3):
            return f"{w} hypotheses are waiting on data; unblock or close them before starting new ones"
    elif slug:
        if (h := hyp(c, slug)) and h["status"] in TERMINAL:
            return f"hypothesis {slug} is {h['status']}"
        if c.execute("SELECT COUNT(*) FROM tasks WHERE hypothesis=?", (slug,)).fetchone()[0] >= L(cfg, "limits", "max_tasks_per_hypothesis", 8):
            return "hypothesis task cap reached"
    since = time.time() - 86400 * L(cfg, "limits", "dedup_days", 14)
    if c.execute("SELECT 1 FROM tasks WHERE fingerprint=? AND status!='failed' AND created>?",
                 (fingerprint(role, slug, title), since)).fetchone():
        return "duplicate of a recent task"
    return None

def stalled(c, cfg):
    """No progress for `stall_runs` runs -> spinning. Returns (stalled, last_progress_event_id)."""
    row = c.execute("SELECT id, ts FROM events WHERE kind IN ('hyp.status','user.ack','dataset.ready','ideas.added',"
                    "'dataset.validated','git.merged') ORDER BY id DESC LIMIT 1").fetchone()
    last_id, last_ts = (row["id"], row["ts"]) if row else (0, 0)
    runs = c.execute("SELECT COUNT(*) FROM runs WHERE started>?", (last_ts,)).fetchone()[0]
    return runs >= L(cfg, "limits", "stall_runs", 40), last_id

def verdict(m, cfg):
    need = ("net_mean", "ci_low", "ci_high", "n_units")
    if not isinstance(m, dict) or any(not isinstance(m.get(k), (int, float)) for k in need):
        return "invalid", "backtest returned no numeric metrics (net_mean, ci_low, ci_high, n_units)"
    n, lo = m["n_units"], m["ci_low"]
    if n < L(cfg, "gates", "min_units", 30):
        return "invalid", f"underpowered: {n} independent units"
    if lo <= 0:
        return "fail", f"net-of-cost CI lower bound {lo:.4g} <= 0 over {n} units"
    ex = m.get("net_mean_ex_top")
    if isinstance(ex, (int, float)) and ex <= 0:
        return "fail", "positive mean disappears without the best observations"
    return "pass", f"CI lower bound {lo:.4g} > 0 over {n} units"

def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def on_result(c, cfg, task, result, workdir):
    """Route a finished task. When a hypothesis reaches a verdict, its venue bro records it in the dossier;
    a validated one then goes to the chief for a DRY deploy."""
    slug, spec = task["hypothesis"], json.loads(task["spec"])
    kind = spec.get("kind")
    if kind == "verdict":
        h = hyp(c, slug) if slug else None
        if h and h["status"] == "validated" and "chief" in cfg["roles"]:
            # the brief is merged to main by the venue bro's worktree; start after that merge has landed
            tid = spawn(c, task, "chief", f"Deploy {slug} in DRY mode",
                        {"kind": "deploy", "venue": task["role"], "slug": slug,
                         "brief": f"repo/desks/{task['role']}/deploy-{slug}.md"})
            c.execute("UPDATE tasks SET not_before=? WHERE id=?", (time.time() + 180, tid))
        return
    if kind in ("deploy", "seed", "idea"):
        return
    before = hyp(c, slug) if slug else None
    _route(c, cfg, task, result, workdir)
    after = hyp(c, slug) if slug else None
    if before and after and before["status"] not in TERMINAL and after["status"] in TERMINAL:
        v = venue_of(c, cfg, slug)
        if v:
            files = [after["path"]] if after["path"] else []
            files += [str(Path(workdir) / a) for a in result.get("artifacts", []) if isinstance(a, str)
                      and (Path(workdir) / a).is_file()][:5]
            spawn(c, task, v, f"Verdict: {slug} {after['status']}",
                  {"kind": "verdict", "status": after["status"], "reason": after["reason"], "metrics": result.get("metrics"),
                   "files": files})

def _route(c, cfg, task, result, workdir):
    slug = task["hypothesis"]
    h = hyp(c, slug) if slug else None
    if not h or h["status"] in TERMINAL:
        return
    wd, role = Path(workdir), task["role"]
    if result["status"] == "blocked" and role == "backtester" and "engineer" in cfg["roles"]:
        tries = c.execute("SELECT COUNT(*) FROM tasks WHERE hypothesis=? AND role='engineer'", (slug,)).fetchone()[0]
        if tries < L(cfg, "gates", "max_data_attempts", 2):
            set_status(c, slug, "data", "waiting for data: " + result.get("summary", "")[:200])
            return spawn(c, task, "engineer", f"Get the data {slug} needs",
                         {"needs": result.get("summary", "")[:3000], "files": [h["path"]] if h["path"] else []})
    if result["status"] == "blocked":
        return set_status(c, slug, "parked", f"{task['role']} blocked: {result.get('summary', '')[:240]}")
    if is_author(cfg, role):
        draft = wd / "prereg.md"
        missing = gates.prereg_missing(draft)
        if not missing:
            frozen = STATE / "prereg" / f"{slug}.md"
            frozen.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(draft, frozen)
            sha = sha256(frozen)
            set_status(c, slug, "prereg", None, path=str(frozen), prereg_sha=sha)
            spawn(c, task, "backtester", f"Backtest {slug} per frozen prereg",
                  {"prereg": str(frozen), "prereg_sha": sha, "files": [str(frozen)]})
            set_status(c, slug, "backtest")
        elif c.execute("SELECT COUNT(*) FROM tasks WHERE hypothesis=? AND role=? AND json_extract(spec,'$.kind') IS NULL",
                       (slug, role)).fetchone()[0] >= L(cfg, "gates", "max_prereg_attempts", 2):
            set_status(c, slug, "parked", f"prereg incomplete after retries: missing {', '.join(missing)}")
        else:
            spawn(c, task, role, f"Complete the prereg for {slug}",
                  {"fix_missing": missing, "files": [str(draft)] if draft.is_file() else []})
    elif role == "backtester":
        m = result.get("metrics")
        v, why = verdict(m, cfg)
        event(c, "lifecycle", "verdict", task["id"], hypothesis=slug, verdict=v, why=why)
        if v == "fail":
            set_status(c, slug, "rejected", why)
        elif v == "invalid":
            set_status(c, slug, "parked", why)
        else:
            arts = [str(wd / a) for a in result.get("artifacts", []) if isinstance(a, str) and (wd / a).is_file()][:10]
            spawn(c, task, "skeptic", f"Audit the backtest of {slug}",
                  {"metrics": m, "backtest_task": task["id"], "files": [h["path"]] + arts})
            set_status(c, slug, "review", why)
    elif role == "engineer":
        queued = 0
        for spec in result.get("jobs", [])[:5]:
            err = jobs.submit(c, task, spec if isinstance(spec, dict) else {}, workdir, cfg)
            if err: event(c, "lifecycle", "job.refused", task["id"], reason=err)
            else: queued += 1
        record_datasets(c, result)
        if not queued and h["status"] == "data":      # data was already obtainable without a job
            rerun_backtest(c, task, slug, h)
    elif role == "skeptic":
        v = str(result.get("verdict", "")).upper()
        summ = result.get("summary", "")[:240]
        if v == "SURVIVES":
            set_status(c, slug, "validated", "survived skeptic; forward paper test needs human approval")
        elif v == "FAILS":
            set_status(c, slug, "rejected", f"skeptic: {summ}")
        else:
            set_status(c, slug, "parked", f"skeptic inconclusive: {summ}")

def on_failed(c, task, reason):
    slug = task["hypothesis"]
    if slug and (h := hyp(c, slug)) and h["status"] not in TERMINAL:
        set_status(c, slug, "parked", f"{task['role']} task #{task['id']} failed ({reason})")


def record_datasets(c, result):
    for d in result.get("datasets", [])[:10]:
        if isinstance(d, dict) and d.get("name"):
            c.execute("INSERT INTO datasets(name,path,description,domain,status,updated) VALUES(?,?,?,?,'ready',?) "
                      "ON CONFLICT(name) DO UPDATE SET description=excluded.description, status='ready', updated=excluded.updated",
                      (str(d["name"])[:80], str(jobs.DATA / str(d["name"])), str(d.get("description", ""))[:500], d.get("domain"), time.time()))

def rerun_backtest(c, task, slug, h):
    set_status(c, slug, "backtest", "data ready")
    spawn(c, task, "backtester", f"Backtest {slug} per frozen prereg (data ready)",
          {"prereg": h["path"], "prereg_sha": h["prereg_sha"], "files": [h["path"]]})

def on_job_done(c, cfg, job, ok):
    """When an engineer's blocking jobs have all finished, rerun the backtest (or retry / park)."""
    slug = job["hypothesis"]
    h = hyp(c, slug) if slug else None
    if not h or h["status"] != "data":
        return
    open_jobs = c.execute("SELECT COUNT(*) FROM jobs WHERE task_id=? AND blocking=1 AND status IN ('queued','running')",
                          (job["task_id"],)).fetchone()[0]
    if open_jobs:
        return
    task = c.execute("SELECT * FROM tasks WHERE id=?", (job["task_id"],)).fetchone()
    failed = c.execute("SELECT COUNT(*) FROM jobs WHERE task_id=? AND blocking=1 AND status='failed'", (job["task_id"],)).fetchone()[0]
    if not failed:
        return rerun_backtest(c, task, slug, h)
    tries = c.execute("SELECT COUNT(*) FROM tasks WHERE hypothesis=? AND role='engineer'", (slug,)).fetchone()[0]
    if tries >= L(cfg, "gates", "max_data_attempts", 2):
        return set_status(c, slug, "parked", "data collection failed after retries")
    log = Path(job["log_path"] or "")
    spawn(c, task, "engineer", f"Fix the collector for {slug}",
          {"needs": json.loads(task["spec"]).get("needs", ""), "failed_job_log": log.read_text(errors="replace")[-3000:] if log.is_file() else "",
           "files": [h["path"]] if h["path"] else []})

# ---------- standing orders: what an idle lane does when nothing is queued for it ----------
def domains(cfg):
    return cfg.get("domains", {}).get("list", [])

def _recent(c, role, since_s, where="", args=()):
    return c.execute(f"SELECT COUNT(*) FROM tasks WHERE role=? AND created>? {where}", (role, time.time() - since_s, *args)).fetchone()[0]

def _least_recent_domain(c, cfg, role, cooldown_s):
    best = None
    for d in domains(cfg):
        last = c.execute("SELECT MAX(created) FROM tasks WHERE role=? AND json_extract(spec,'$.domain')=?", (role, d)).fetchone()[0] or 0
        if time.time() - last >= cooldown_s and (best is None or last < best[1]):
            best = (d, last)
    return best[0] if best else None

def idle_work(c, cfg, role):
    """(title, spec, hypothesis) for an idle lane, or None. Cooldowns keep this from churning."""
    cool = L(cfg, "limits", "idle_cooldown_s", 900)
    if _recent(c, role, cool, "AND json_extract(spec,'$.standing')=1"):
        return None
    if role == "researcher":
        d = _least_recent_domain(c, cfg, role, L(cfg, "limits", "scout_cooldown_s", 21600))
        if d:
            return (f"Scout for new edges: {d}", {"standing": 1, "kind": "scout", "domain": d}, None)
    if role == "engineer":
        have = {r[0] for r in c.execute("SELECT DISTINCT domain FROM datasets WHERE domain IS NOT NULL")}
        d = next((d for d in domains(cfg) if d not in have and not _recent(
            c, role, 86400, "AND json_extract(spec,'$.domain')=?", (d,))), None)
        if d:
            return (f"Bootstrap public data: {d}", {"standing": 1, "kind": "bootstrap", "domain": d}, None)
        stale = c.execute("SELECT name FROM datasets WHERE status='ready' AND updated<? ORDER BY updated LIMIT 1",
                          (time.time() - L(cfg, "limits", "refresh_after_s", 86400),)).fetchone()
        if stale:
            return (f"Refresh dataset {stale[0]}", {"standing": 1, "kind": "refresh", "dataset": stale[0]}, None)
    if role == "backtester":
        r = c.execute("SELECT name FROM datasets WHERE status='ready' AND validated=0 ORDER BY updated LIMIT 1").fetchone()
        if r:
            return (f"Validate dataset {r[0]}", {"standing": 1, "kind": "validate", "dataset": r[0]}, None)
    if role == "skeptic":
        r = c.execute("SELECT * FROM hypotheses WHERE status IN ('rejected','parked') AND COALESCE(reason,'') NOT LIKE 'off-focus%' AND slug NOT IN "
                      "(SELECT json_extract(spec,'$.audit') FROM tasks WHERE role='skeptic' AND json_extract(spec,'$.audit') IS NOT NULL) "
                      "ORDER BY updated DESC LIMIT 1").fetchone()
        if r:
            return (f"Audit the {r['status']} verdict on {r['slug']}",
                    {"standing": 1, "kind": "audit", "audit": r["slug"], "reason": r["reason"], "files": [r["path"]] if r["path"] else []}, None)
    if role == "curator":
        last = c.execute("SELECT MAX(created) FROM tasks WHERE role='curator'").fetchone()[0] or 0
        if c.execute("SELECT COUNT(*) FROM tasks WHERE status='done' AND updated>?", (last,)).fetchone()[0] >= 6:
            return ("Compact memory: index results and dead ends", {"standing": 1, "kind": "compact"}, None)
    return None

def on_standing_result(c, cfg, task, result, workdir):
    spec = json.loads(task["spec"])
    kind = spec.get("kind")
    if kind == "shift":                                # desk shifts land in git; nothing else to route
        return
    if kind == "scout":
        n = 0
        for i in result.get("ideas", [])[:8]:
            if isinstance(i, dict) and SLUG.fullmatch(str(i.get("slug", ""))) and not hyp(c, i["slug"]):
                c.execute("INSERT OR IGNORE INTO ideas(slug,domain,idea,mechanism,data,created) VALUES(?,?,?,?,?,?)",
                          (i["slug"], spec.get("domain"), str(i.get("idea", ""))[:600], str(i.get("mechanism", ""))[:600],
                           str(i.get("data", ""))[:400], time.time())); n += 1
        if n: event(c, "lifecycle", "ideas.added", task["id"], n=n, domain=spec.get("domain"))
    elif kind in ("bootstrap", "refresh"):
        for js in result.get("jobs", [])[:5]:
            js = dict(js) if isinstance(js, dict) else {}
            js.setdefault("domain", spec.get("domain")); js["blocking"] = False
            err = jobs.submit(c, task, js, workdir, cfg)
            if err: event(c, "lifecycle", "job.refused", task["id"], reason=err)
        record_datasets(c, result)
    elif kind == "validate":
        ok = str(result.get("verdict", "")).upper() != "BAD"
        c.execute("UPDATE datasets SET validated=?, notes=?, status=CASE WHEN ? THEN status ELSE 'failed' END WHERE name=?",
                  (1 if ok else 0, result.get("summary", "")[:800], ok, spec.get("dataset")))
        event(c, "lifecycle", "dataset.validated" if ok else "dataset.bad", task["id"], dataset=spec.get("dataset"))
    elif kind == "audit" and str(result.get("verdict", "")).upper() == "REOPEN":
        slug = spec.get("audit"); h = hyp(c, slug)
        if h and h["status"] in ("rejected", "parked"):
            set_status(c, slug, "idea", "reopened by skeptic audit: " + result.get("summary", "")[:200])
            add_task(c, "researcher", f"Revise the prereg for {slug} (audit found a defect)",
                     {"defect": result.get("summary", "")[:2000], "files": [h["path"]] if h["path"] else []},
                     hypothesis=slug, actor="lifecycle")
