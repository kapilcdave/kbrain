"""Deterministic hypothesis pipeline. LLMs propose and do work; this code decides what happens next.

idea --researcher writes complete prereg--> prereg (frozen + hashed) --> backtest
backtest --metrics graded by code--> review (skeptic) | rejected | parked
review --skeptic verdict--> validated | rejected | parked
Anti-spiral: dedup, per-hypothesis caps, max open hypotheses, stall detection.
"""
import hashlib, re, shutil, time
from datetime import date
from pathlib import Path
from . import gates
from .db import STATE, event, add_task

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
    if role == "researcher":
        if not slug or not SLUG.fullmatch(slug):
            return "researcher task needs a new kebab-case hypothesis slug"
        if (h := hyp(c, slug)):
            return f"hypothesis {slug} already exists ({h['status']})"
        if open_slots(c, cfg) <= 0:
            return "no open hypothesis slots; finish existing work first"
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
    """No hypothesis changed state for `stall_runs` runs -> spinning. Returns (stalled, last_progress_event_id)."""
    row = c.execute("SELECT id, ts FROM events WHERE kind IN ('hyp.status','user.ack') ORDER BY id DESC LIMIT 1").fetchone()
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
    slug = task["hypothesis"]
    h = hyp(c, slug) if slug else None
    if not h or h["status"] in TERMINAL:
        return
    if result["status"] == "blocked":
        return set_status(c, slug, "parked", f"{task['role']} blocked: {result.get('summary', '')[:240]}")
    wd, role = Path(workdir), task["role"]
    if role == "researcher":
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
        elif c.execute("SELECT COUNT(*) FROM tasks WHERE hypothesis=? AND role='researcher'", (slug,)).fetchone()[0] \
                >= L(cfg, "gates", "max_prereg_attempts", 2):
            set_status(c, slug, "parked", f"prereg incomplete after retries: missing {', '.join(missing)}")
        else:
            spawn(c, task, "researcher", f"Complete the prereg for {slug}",
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
