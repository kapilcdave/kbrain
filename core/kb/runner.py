import json, re, shutil, time, traceback
from pathlib import Path
from . import adapters, gates, lifecycle
from .db import ROOT, STATE, connect, event, add_task
from .router import load_config, pick_model

RATE_LIMIT = re.compile(r"(rate.?limit|usage limit|limit reached|too many requests|\b429\b|try again (in|at|later)|quota)", re.I)
STOP = STATE / "STOP"
ALIVE = STATE / "runner.alive"

def lim(cfg, key, default):
    return cfg.get("limits", {}).get(key, default)

def mem_available_mb():
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable"):
                return int(line.split()[1]) // 1024
    return 10**9

def build_prompt(role_name, task, workdir, inline=False):
    role = (ROOT / "roles" / f"{role_name}.md").read_text()
    inputs = Path(workdir) / "inputs"
    names = sorted(p.name for p in inputs.iterdir()) if inputs.is_dir() else []
    return (f"{role}\n\n---\nTASK #{task['id']}: {task['title']}\n"
            f"Hypothesis: {task['hypothesis'] or '-'}\n"
            f"Working directory: {workdir}\n"
            f"Input files (in inputs/): {', '.join(names) or 'none'}\n"
            f"Spec (spec.json):\n{task['spec']}\n\n"
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
    files = [wd / n for n in json.loads(task["spec"]).get("inline", [])] + [wd / "digest.md"]
    files += sorted((wd / "inputs").glob("*")) if (wd / "inputs").is_dir() else []
    for f in files:
        if f.is_file():
            out += f"\n=== {f.name} ===\n{f.read_text(errors='replace')[:12000]}\n"
    return out

def digest(c, cfg):
    """Compact state snapshot for the chief, so it never needs the whole history."""
    lines = ["# State digest", "", f"Open hypothesis slots: {lifecycle.open_slots(c, cfg)}", ""]
    for r in c.execute("SELECT status, COUNT(*) n FROM tasks GROUP BY status"):
        lines.append(f"- tasks {r['status']}: {r['n']}")
    lines += ["", "## Hypotheses (slug: status. reason)"]
    lines += [f"- {r['slug']}: {r['status']}. {r['reason'] or ''}"
              for r in c.execute("SELECT * FROM hypotheses ORDER BY updated DESC LIMIT 60")]
    lines += ["", "## Recent results (newest first)"]
    for r in c.execute("SELECT id,role,status,title,hypothesis,result FROM tasks WHERE status IN ('done','blocked','failed') ORDER BY updated DESC LIMIT 15"):
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
    busy = c.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('queued','running')").fetchone()[0]
    last = c.execute("SELECT MAX(created) FROM tasks WHERE role='chief'").fetchone()[0] or 0
    if not busy and time.time() - last >= lim(cfg, "heartbeat_s", 900):
        add_task(c, "chief", "heartbeat: review state and plan next tasks", {}, actor="heartbeat")

def runs_last_day(c):
    return c.execute("SELECT COUNT(*) FROM runs WHERE started>?", (time.time() - 86400,)).fetchone()[0]

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

def pick(c):
    return c.execute("SELECT * FROM tasks WHERE status='queued' AND not_before<=? ORDER BY id LIMIT 1",
                     (time.time(),)).fetchone()

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
    if role.get("with_stats"):
        shutil.copyfile(ROOT / "kb" / "stats.py", workdir / "kbstats.py")
    if role.get("digest"):
        (workdir / "digest.md").write_text(digest(c, cfg))

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
    model, nmodels = pick_model(c, cfg, task)
    workdir = STATE / "workspaces" / f"task-{task['id']}"
    prepare(task, role, workdir, cfg, c)
    log_path = workdir / f"run-{task['attempts'] + 1}.log"
    c.execute("UPDATE tasks SET status='running', updated=? WHERE id=?", (time.time(), task["id"]))
    run_id = c.execute("INSERT INTO runs(task_id,model,started,log_path) VALUES(?,?,?,?)",
                       (task["id"], model, time.time(), str(log_path))).lastrowid
    event(c, "runner", "run.started", task["id"], model=model, run=run_id, role=task["role"])
    rc, timed_out = adapters.run(model, build_prompt(task["role"], task, workdir, inline=model.startswith("api:")),
                                 workdir, role.get("timeout_s", 900), log_path, role.get("tools", ["Read", "Write"]))
    result = read_result(workdir)
    log_tail = log_path.read_text(errors="replace")[-4000:] if log_path.exists() else ""
    if result is None and RATE_LIMIT.search(log_tail) and not timed_out:
        outcome = "rate_limited"           # not the task's fault: wait, don't burn an attempt
        c.execute("UPDATE tasks SET status='queued', not_before=?, model_idx=?, updated=? WHERE id=?",
                  (time.time() + lim(cfg, "rate_limit_backoff_s", 1800), min(task["model_idx"] + 1, nmodels - 1),
                   time.time(), task["id"]))
        event(c, "runner", "task.rate_limited", task["id"], model=model, role=task["role"])
    elif result is not None and result["status"] in ("ok", "blocked"):
        outcome = "ok" if result["status"] == "ok" else "blocked"
        spawned = enqueue_children(c, cfg, task, result) if outcome == "ok" else 0
        finish(c, task, "done" if outcome == "ok" else "blocked", result, model=model, spawned=spawned, role=task["role"])
        lifecycle.on_result(c, cfg, task, result, workdir)
    else:                                  # timeout, crash, invalid output, or status=failed
        outcome = "timeout" if timed_out else "invalid"
        attempts = task["attempts"] + 1
        if attempts >= task["max_attempts"]:
            finish(c, task, "failed", result, model=model, reason=outcome, role=task["role"])
            lifecycle.on_failed(c, task, outcome)
        else:                              # escalate down the fallback chain
            c.execute("UPDATE tasks SET status='queued', attempts=?, model_idx=?, not_before=?, updated=? WHERE id=?",
                      (attempts, min(task["model_idx"] + 1, nmodels - 1), time.time() + 30, time.time(), task["id"]))
            event(c, "runner", "task.retry", task["id"], model=model, reason=outcome, role=task["role"])
    c.execute("UPDATE runs SET ended=?, rc=?, outcome=? WHERE id=?", (time.time(), rc, outcome, run_id))

def tick(c, cfg):
    """One scheduling step: 'ran', 'idle', 'stopped', 'low_mem' or 'budget'."""
    STATE.mkdir(parents=True, exist_ok=True)
    ALIVE.touch()
    if STOP.exists():
        return "stopped"
    if mem_available_mb() < lim(cfg, "min_mem_mb", 1200):
        return "low_mem"
    if runs_last_day(c) >= lim(cfg, "max_runs_per_day", 300):
        return "budget"
    heartbeat(c, cfg)
    task = pick(c)
    if not task:
        return "idle"
    try:
        execute(c, cfg, task)
    except Exception:
        c.execute("UPDATE tasks SET status='failed', updated=? WHERE id=?", (time.time(), task["id"]))
        event(c, "runner", "task.crashed", task["id"], error=traceback.format_exc()[-1500:])
        lifecycle.on_failed(c, task, "crash")
    return "ran"

def serve(poll_s=10):
    adapters.load_env()
    c = connect()
    c.execute("UPDATE tasks SET status='queued' WHERE status='running'")   # crash recovery
    event(c, "runner", "runner.started")
    while True:
        cfg = load_config()                 # hot-reload routing without restart
        if tick(c, cfg) != "ran":
            time.sleep(poll_s)
