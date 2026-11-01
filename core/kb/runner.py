import json, os, shutil, threading, time, traceback
from pathlib import Path
from . import adapters, fleet, gates, gitops, jobs, lifecycle
from .db import ROOT, STATE, connect, event, add_task
from .router import load_config, pick_model

RATE_LIMIT = adapters.LIMIT_TEXT          # strict: the CLIs' own quota errors only
STOP = STATE / "STOP"
PRIORS = Path(os.environ.get("KB_PRIORS", Path.home() / ".config" / "kbrain" / "priors.md"))
CORPUS = {"corpus": Path.home() / "repos" / "claude-code-memory" / "proj-trading",   # ~650 findings + topics
          "projects": Path.home() / "repos" / "proj"}                              # trading code + handoffs
ALIVE = STATE / "runner.alive"
STATUS = "starting"                       # what the runner is doing; published to ALIVE

def lim(cfg, key, default):
    return cfg.get("limits", {}).get(key, default)

def mem_available_mb():
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable"):
                return int(line.split()[1]) // 1024
    return 10**9

def role_text(role_name, cfg=None):
    """Shared brief + the role's contract. Desks share roles/desk.md plus their own focus line."""
    common = (ROOT / "roles" / "_common.md").read_text() if (ROOT / "roles" / "_common.md").is_file() else ""
    own = ROOT / "roles" / f"{role_name}.md"
    rcfg = ((cfg or load_config())["roles"].get(role_name) or {})
    if own.is_file():
        body = own.read_text()
    elif rcfg.get("venue_bro"):
        body = (ROOT / "roles" / "venue.md").read_text() + f"\nYOUR VENUE: {role_name}\nFOCUS: {rcfg.get('focus', '')}\n"
    else:
        body = (ROOT / "roles" / "desk.md").read_text()
    if rcfg.get("desk"):
        body += f"\nYOUR DESK: {role_name}\nFOCUS: {rcfg.get('focus', '')}\n"
    if rcfg.get("collector_rules") and role_name != "engineer":
        body += "\n--- collector rules (from the engineer brief) ---\n" + (ROOT / "roles" / "engineer.md").read_text()
    return common + "\n---\n" + body

def build_prompt(role_name, task, workdir, inline=False):
    role = role_text(role_name)
    inputs = Path(workdir) / "inputs"
    names = sorted(p.name for p in inputs.iterdir()) if inputs.is_dir() else []
    return (f"{role}\n\n---\nTASK #{task['id']}: {task['title']}\n"
            f"Hypothesis: {task['hypothesis'] or '-'}\n"
            f"Working directory: {workdir}\n"
            f"Input files (in inputs/): {', '.join(names) or 'none'}\n"
            + ("Read priors.md FIRST: closed branches, estimator traps and venue facts from prior work.\n"
               if (Path(workdir) / "priors.md").is_file() else "")
            + ("Your git worktree is repo/ (commit there; the harness merges).\n"
               if (Path(workdir) / "repo").is_dir() else "")
            + ("The venue's dossier is staged as dossier.md: read it before anything else.\n"
               if (Path(workdir) / "dossier.md").is_file() else "")
            + (f"Datasets (read them under data/ in your working directory; never fetch from the network yourself):\n{task['_catalog']}\n" if task.get('_catalog') else "")
            + f"Spec (spec.json):\n{task['spec']}\n\n"
            "When finished, write result.json in the working directory: "
            '{"status":"ok|blocked|failed","summary":"...","artifacts":["relative/path"]} '
            "plus any role-specific fields your instructions require. Never print secrets. "
            "Use your file read/write tools rather than shell commands unless the task requires running code.\n"
            + inline_files(task, workdir, inline))

def inline_files(task, workdir, inline):
    """Tool-less (api) models can't read files, so paste small ones into the prompt."""
    if not inline:
        return ""
    wd, out = Path(workdir), ""
    files = [wd / n for n in json.loads(task["spec"]).get("inline", [])] + [wd / "digest.md", wd / "priors.md"]
    files += sorted((wd / "inputs").glob("*")) if (wd / "inputs").is_dir() else []
    for f in files:
        if f.is_file():
            out += f"\n=== {f.name} ===\n{f.read_text(errors='replace')[:12000]}\n"
    return out

def digest(c, cfg):
    """Compact state snapshot for the chief, so it never needs the whole history."""
    lines = ["# State digest", ""]
    uses_fleet = any(r.get("with_fleet") for r in cfg.get("roles", {}).values())
    if uses_fleet and (fl := fleet.cached_md()):   # live VMs, runners and bets (trading setups only)
        lines += [fl, ""]
    waiting = lifecycle.waiting_on_data(c)
    lines += [f"Open hypothesis slots: {lifecycle.open_slots(c, cfg)}",
              f"Hypotheses waiting on data: {waiting} (new hypotheses are refused while this is >= "
              f"{lim(cfg, 'max_waiting_on_data', 3)}; get these unblocked or closed first)", ""]
    if lifecycle.domains(cfg):
        counts = dict(c.execute("SELECT domain, COUNT(*) FROM hypotheses GROUP BY domain").fetchall())
        lines += ["## Research domains (hypotheses so far)"] + [f"- {d}: {counts.get(d, 0)}" for d in lifecycle.domains(cfg)] + [""]
    ideas = c.execute("SELECT * FROM ideas WHERE status='new' ORDER BY created DESC LIMIT 15").fetchall()
    if ideas:
        lines += ["## Scouted ideas waiting for you (promote the best by proposing researcher tasks with these slugs)"]
        lines += [f"- {i['slug']} [{i['domain']}]: {i['idea'][:220]} | mechanism: {i['mechanism'][:160]} | data: {i['data'][:120]}" for i in ideas] + [""]
    lines += ["## Datasets", jobs.catalog(c, 20), ""]
    for r in c.execute("SELECT status, COUNT(*) n FROM tasks GROUP BY status"):
        lines.append(f"- tasks {r['status']}: {r['n']}")
    lines += ["", "## Hypotheses (slug: status. reason)"]
    lines += [f"- {r['slug']}: {r['status']}. {r['reason'] or ''}"
              for r in c.execute("SELECT * FROM hypotheses ORDER BY updated DESC LIMIT 60")]
    lines += ["", "## Recent results (newest first)"]
    roles = list(cfg.get("roles", {}))
    for r in c.execute(f"SELECT id,role,status,title,hypothesis,result FROM tasks WHERE status IN ('done','blocked','failed') "
                       f"AND role IN ({','.join('?' * len(roles))}) AND (hypothesis IS NULL OR hypothesis IN (SELECT slug FROM hypotheses)) AND COALESCE(json_extract(result,'$.summary'),'') NOT LIKE 'stopped by operator%' "
                       "ORDER BY updated DESC LIMIT 15", roles):
        summ = (json.loads(r["result"]).get("summary", "") if r["result"] else "")[:300]
        lines.append(f"- #{r['id']} [{r['role']}/{r['status']}] {r['hypothesis'] or '-'}: {r['title']} :: {summ}")
    for f in (STATE / "dead-ends.md", ROOT / "knowledge" / "dead-ends.md", ROOT.parent / "lessons" / "negative-results.md", ROOT / "GOAL.md"):
        if f.is_file():
            lines += ["", f"## {f.name}", f.read_text()[-5000:]]
    return "\n".join(lines)

def heartbeat(c, cfg):
    """Keep thinking: wake the chief when idle, unless the system is spinning (then alert and wait)."""
    stalled, last_progress = lifecycle.stalled(c, cfg)
    if stalled:
        if not c.execute("SELECT 1 FROM events WHERE kind='alert.stall' AND id>?", (last_progress,)).fetchone():
            event(c, "runner", "alert.stall", None, msg="no hypothesis progressed recently; chief paused until `kb ack`")
        return
    starving = not c.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('queued','running') AND role IN ('chief','researcher') "
                             "AND json_extract(spec,'$.standing') IS NULL").fetchone()[0]
    last = c.execute("SELECT MAX(created) FROM tasks WHERE role='chief'").fetchone()[0] or 0
    has_work = lifecycle.open_slots(c, cfg) > 0 or c.execute("SELECT 1 FROM ideas WHERE status='new'").fetchone()
    if starving and has_work and time.time() - last >= lim(cfg, "heartbeat_s", 900):
        add_task(c, "chief", "Pick the next idea (pipeline idle)", {"kind": "plan"}, actor="heartbeat")

def runs_last_day(c):
    """Runs counted against max_runs_per_day: the last 24 h, or since the last `kb budget-reset` if later."""
    reset = c.execute("SELECT MAX(ts) FROM events WHERE kind='budget.reset'").fetchone()[0] or 0
    return c.execute("SELECT COUNT(*) FROM runs WHERE started>?", (max(time.time() - 86400, reset),)).fetchone()[0]

def read_result(workdir):
    p = Path(workdir) / "result.json"
    if not p.is_file():
        return None
    try:
        r = json.loads(p.read_text())
    except json.JSONDecodeError:
        return None
    if not isinstance(r, dict) or r.get("status") not in ("ok", "blocked", "failed") or "summary" not in r:
        return None
    return r

def pick(c, role=None):
    """Atomically claim the oldest ready task (for one role's lane, if given)."""
    q = "SELECT id FROM tasks WHERE status='queued' AND not_before<=?" + (" AND role=?" if role else "") + " ORDER BY id LIMIT 1"
    return c.execute(f"UPDATE tasks SET status='running', updated=? WHERE id=({q}) AND status='queued' RETURNING *",
                     (time.time(), time.time(), *([role] if role else []))).fetchone()

def finish(c, task, status, result=None, **ev):
    c.execute("UPDATE tasks SET status=?, result=?, updated=? WHERE id=?",
              (status, json.dumps(result) if result else None, time.time(), task["id"]))
    event(c, "runner", f"task.{status}", task["id"], **ev)

def enqueue_children(c, cfg, task, result):
    if cfg["roles"][task["role"]].get("can_spawn") is not True:
        return 0
    n = 0
    for nt in result.get("new_tasks", [])[:10]:
        if not isinstance(nt, dict):
            continue
        reason = lifecycle.admit(c, cfg, task, nt)
        if reason:
            event(c, "runner", "task.spawn_refused", task["id"], title=nt.get("title"), reason=reason)
            continue
        slug = nt.get("hypothesis") or None
        add_task(c, nt["role"], str(nt.get("title", "(untitled)"))[:300], nt.get("spec") if isinstance(nt.get("spec"), dict) else {},
                 parent_id=task["id"], hypothesis=slug, depth=task["depth"] + 1, actor=f"task:{task['id']}",
                 fingerprint=lifecycle.fingerprint(nt["role"], slug, str(nt.get("title", ""))))
        n += 1
    return n

def prepare(task, role, workdir, cfg, c):
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "spec.json").write_text(task["spec"])
    (workdir / "result.json").unlink(missing_ok=True)
    spec = json.loads(task["spec"])
    files = [Path(f) for f in spec.get("files", []) if isinstance(f, str)]
    if files:
        (workdir / "inputs").mkdir(exist_ok=True)
        for f in files:
            if f.is_file() and f.resolve().is_relative_to(STATE.resolve()):   # only harness-owned files
                shutil.copyfile(f, workdir / "inputs" / f.name)
    if role.get("with_data"):
        jobs.DATA.mkdir(parents=True, exist_ok=True)
        link = workdir / "data"
        if not link.exists():
            link.symlink_to(jobs.DATA, target_is_directory=True)
    if role.get("with_stats"):
        shutil.copyfile(ROOT / "kb" / "stats.py", workdir / "kbstats.py")
    lab = ROOT.parent / "lab"                          # the trusted evaluator: every role gets the same copy
    if lab.is_dir():
        for f in lab.glob("*.py"):
            shutil.copyfile(f, workdir / f.name)
    if role.get("digest"):
        (workdir / "digest.md").write_text(digest(c, cfg))
    if role.get("with_corpus"):                        # the trading corpus, read-only by convention
        for name, src in CORPUS.items():
            link = workdir / name
            if src.is_dir() and not link.exists():
                link.symlink_to(src, target_is_directory=True)
    venues = cfg.get("venues", {}).get("list", [])
    if venues and (role.get("with_dossier") or role.get("with_dossiers") or role.get("venue_bro")):   # venue context, from main
        cfg_all = cfg
        if role.get("with_dossiers"):
            mine = venues
        else:
            v = task["role"] if role.get("venue_bro") else lifecycle.venue_of(c, cfg_all, task["hypothesis"])
            mine = [v] if v else []
        for v in mine:
            text = gitops.git("show", f"origin/main:fields/{v}/DOSSIER.md", check=False)
            if text:
                dest = workdir / "dossiers" / f"{v}.md" if role.get("with_dossiers") else workdir / "dossier.md"
                dest.parent.mkdir(parents=True, exist_ok=True); dest.write_text(text)
    if role.get("worktree"):                           # own git worktree; harness merges at the end
        wt = gitops.create(task, workdir)
        if role.get("desk"):
            (workdir / "board.md").write_text(gitops.board(wt))
    if role.get("with_fleet"):                         # ./kbssh (gated box shell) + the fleet map
        shutil.copyfile(ROOT / "bin" / "kbssh", workdir / "kbssh"); (workdir / "kbssh").chmod(0o755)
        if fleet.FLEET_MD.is_file():
            shutil.copyfile(fleet.FLEET_MD, workdir / "fleet.md")
    if role.get("with_priors") and PRIORS.is_file():   # distilled closed branches and traps
        shutil.copyfile(PRIORS, workdir / "priors.md")

def execute(c, cfg, task):
    role = cfg["roles"][task["role"]]
    spec = json.loads(task["spec"])
    if role.get("requires_prereg"):        # deterministic gate: complete AND unmodified since frozen
        p = spec.get("prereg")
        missing = gates.prereg_missing(ROOT / p) if p else ["<no prereg in spec>"]
        if not missing and spec.get("prereg_sha") and lifecycle.sha256(ROOT / p) != spec["prereg_sha"]:
            missing = ["<prereg modified after freezing>"]
        if missing:
            finish(c, task, "blocked", {"status": "blocked", "summary": "prereg gate"}, missing=missing)
            return lifecycle.on_failed(c, task, "prereg gate: " + ", ".join(missing))
    model, nmodels, model_idx, next_at = pick_model(c, cfg, task)
    if model is None:
        c.execute("UPDATE tasks SET status='queued', not_before=?, updated=? WHERE id=?",
                  (next_at, time.time(), task["id"]))
        event(c, "runner", "task.model_cooldown", task["id"], until=next_at, role=task["role"])
        return
    workdir = STATE / "workspaces" / f"task-{task['id']}"
    prepare(task, role, workdir, cfg, c)
    log_path = workdir / f"run-{time.time_ns()}.log"
    c.execute("UPDATE tasks SET status='running', updated=? WHERE id=?", (time.time(), task["id"]))
    run_id = c.execute("INSERT INTO runs(task_id,model,started,log_path) VALUES(?,?,?,?)",
                       (task["id"], model, time.time(), str(log_path))).lastrowid
    event(c, "runner", "run.started", task["id"], model=model, run=run_id, role=task["role"])
    task = dict(task)
    if role.get("with_data"):
        task["_catalog"] = jobs.catalog(c)
    rc, timed_out = adapters.run(model, build_prompt(task["role"], task, workdir, inline=model.startswith("api:")),
                                 workdir, role.get("timeout_s", 900), log_path, role.get("tools", ["Read", "Write"]))
    result = read_result(workdir)
    log_tail = log_path.read_text(errors="replace")[-4000:] if log_path.exists() else ""
    if result is None and (rc == adapters.RATE_LIMITED_RC or RATE_LIMIT.search(log_tail)):
        outcome = "rate_limited"           # not the task's fault: wait, don't burn an attempt
        cooldown_until = time.time() + lim(cfg, "rate_limit_backoff_s", 1800)
        c.execute("INSERT INTO model_cooldowns(model,until_ts) VALUES(?,?) "
                  "ON CONFLICT(model) DO UPDATE SET until_ts=max(until_ts,excluded.until_ts)",
                  (model, cooldown_until))
        c.execute("UPDATE tasks SET status='queued', not_before=?, model_idx=?, updated=? WHERE id=?",
                  (time.time() + 30, model_idx + 1 if model_idx + 1 < nmodels else 0,
                   time.time(), task["id"]))
        event(c, "runner", "task.rate_limited", task["id"], model=model, role=task["role"])
    elif result is not None and result["status"] in ("ok", "blocked"):
        outcome = "ok" if result["status"] == "ok" else "blocked"
        spawned = enqueue_children(c, cfg, task, result) if outcome == "ok" else 0
        finish(c, task, "done" if outcome == "ok" else "blocked", result, model=model, spawned=spawned, role=task["role"])
        if spec.get("standing"):
            lifecycle.on_standing_result(c, cfg, task, result, workdir)
        else:
            lifecycle.on_result(c, cfg, task, result, workdir)
    else:                                  # timeout, crash, invalid output, or status=failed
        outcome = "timeout" if timed_out else "invalid"
        attempts = task["attempts"] + 1
        if attempts >= task["max_attempts"]:
            finish(c, task, "failed", result, model=model, reason=outcome, role=task["role"])
            lifecycle.on_failed(c, task, outcome)
        else:                              # escalate down the fallback chain
            c.execute("UPDATE tasks SET status='queued', attempts=?, model_idx=?, not_before=?, updated=? WHERE id=?",
                      (attempts, min(model_idx + 1, nmodels - 1), time.time() + 30, time.time(), task["id"]))
            event(c, "runner", "task.retry", task["id"], model=model, reason=outcome, role=task["role"])
    c.execute("UPDATE runs SET ended=?, rc=?, outcome=? WHERE id=?", (time.time(), rc, outcome, run_id))
    if role.get("worktree"):                           # commits made before a timeout still count
        status = gitops.integrate(c, task, workdir, task["role"])
        event(c, "runner", "task.git", task["id"], role=task["role"], git=status)

def gate(cfg, c):
    """None if the runner may launch work now, else a reason (also published as STATUS)."""
    if STOP.exists():
        return "stopped"
    if (mem := mem_available_mb()) < lim(cfg, "min_mem_mb", 900):
        return f"waiting: low memory ({mem}MB free)"
    if runs_last_day(c) >= lim(cfg, "max_runs_per_day", 300):
        return "waiting: daily run budget used"
    return None

def plan(c, cfg):
    """Heartbeat for the chief, plus standing orders for every idle lane that has nothing queued."""
    heartbeat(c, cfg)
    stalled, _ = lifecycle.stalled(c, cfg)
    for role, rcfg in cfg["roles"].items():
        if role == "chief" or rcfg.get("heartbeat_only"):
            continue
        if c.execute("SELECT 1 FROM tasks WHERE role=? AND status IN ('queued','running')", (role,)).fetchone():
            continue
        if rcfg.get("desk"):                            # standing desk: next shift as soon as the last one ends
            last = c.execute("SELECT MAX(updated) FROM tasks WHERE role=?", (role,)).fetchone()[0] or 0
            if time.time() - last >= lim(cfg, "desk_gap_s", 90):
                add_task(c, role, f"{role} desk: shift", {"standing": 1, "kind": "shift"}, actor="desk", max_attempts=2)
            continue
        if stalled or rcfg.get("standing_orders") is False:
            continue
        w = lifecycle.idle_work(c, cfg, role)
        if w:
            add_task(c, role, w[0], w[1], hypothesis=w[2], actor="standing", max_attempts=2)

def _run(task, cfg):
    c = connect()                           # each lane gets its own connection
    try:
        execute(c, cfg, task)
    except Exception:
        c.execute("UPDATE tasks SET status='failed', updated=? WHERE id=?", (time.time(), task["id"]))
        event(c, "runner", "task.crashed", task["id"], error=traceback.format_exc()[-1500:])
        lifecycle.on_failed(c, task, "crash")
    finally:
        c.close()

def tick(c, cfg):
    """One synchronous step (tests, `kb once`): 'ran', 'idle', 'stopped', 'low_mem' or 'budget'."""
    global STATUS
    STATE.mkdir(parents=True, exist_ok=True)
    why = gate(cfg, c)
    if why:
        STATUS = why
        return {"stopped": "stopped"}.get(why, "low_mem" if "memory" in why else "budget")
    plan(c, cfg)
    task = pick(c)
    if not task:
        STATUS = "idle"; return "idle"
    STATUS = f"working on #{task['id']} ({task['role']})"
    try:
        execute(c, cfg, task)
    except Exception:
        c.execute("UPDATE tasks SET status='failed', updated=? WHERE id=?", (time.time(), task["id"]))
        event(c, "runner", "task.crashed", task["id"], error=traceback.format_exc()[-1500:])
        lifecycle.on_failed(c, task, "crash")
    return "ran"

def _publish():
    while True:                             # liveness even while long tasks run
        try:
            ALIVE.write_text(STATUS)
        except OSError:
            pass
        time.sleep(10)

def _fleet_loop():
    """Read-only ssh checks of the VMs on their own thread, so a slow box never stalls the queue."""
    c = connect()
    while True:
        try:
            fleet.maybe_refresh(c)
        except Exception:
            event(c, "fleet", "fleet.error", None, error=traceback.format_exc()[-1500:])
        time.sleep(60)

def serve(poll_s=5):
    """Parallel lanes: one task per role at a time, up to max_workers, launched only when memory allows.
    Background data jobs are pumped every loop and never occupy a lane."""
    global STATUS
    adapters.load_env()
    STATE.mkdir(parents=True, exist_ok=True)
    threading.Thread(target=_publish, daemon=True).start()
    threading.Thread(target=_fleet_loop, daemon=True).start()
    c = connect()
    c.execute("UPDATE tasks SET status='queued' WHERE status='running'")   # crash recovery
    event(c, "runner", "runner.started")
    lanes, last_launch = {}, 0.0
    while True:
        cfg = load_config()                 # hot-reload routing without restart
        lanes = {r: t for r, t in lanes.items() if t.is_alive()}
        try:
            jobs.pump(c, cfg, lifecycle.on_job_done)
        except Exception:
            event(c, "runner", "jobs.error", None, error=traceback.format_exc()[-1500:])
        why = gate(cfg, c)
        if not why:
            plan(c, cfg)
            for role in cfg["roles"]:
                if role in lanes or len(lanes) >= lim(cfg, "max_workers", 3):
                    continue
                if time.time() - last_launch < lim(cfg, "launch_spacing_s", 8) or gate(cfg, c):
                    break                   # let the last agent's memory show up before judging again
                task = pick(c, role)
                if task:
                    t = threading.Thread(target=_run, args=(task, cfg), daemon=True)
                    t.start(); lanes[role] = t; last_launch = time.time()
        busy = ", ".join(sorted(lanes)) or "idle"
        running_jobs = c.execute("SELECT COUNT(*) FROM jobs WHERE status='running'").fetchone()[0]
        STATUS = (why + (f" · {busy} finishing" if lanes else "")) if why else \
            (f"working: {busy}" if lanes else "idle") + (f" · {running_jobs} collectors" if running_jobs else "")
        time.sleep(poll_s)
