import json, re, shutil, time, traceback
from pathlib import Path
from . import adapters, gates
from .db import ROOT, STATE, connect, event, add_task
from .router import load_config, pick_model

RATE_LIMIT = re.compile(r"(rate.?limit|usage limit|limit reached|too many requests|\b429\b|try again (in|at|later)|quota)", re.I)
STOP = STATE / "STOP"

def mem_available_mb():
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable"):
                return int(line.split()[1]) // 1024
    return 10**9

def build_prompt(role_name, task, workdir, inline=False):
    role = (ROOT / "roles" / f"{role_name}.md").read_text()
    return (f"{role}\n\n---\nTASK #{task['id']}: {task['title']}\n"
            f"Hypothesis: {task['hypothesis'] or '-'}\n"
            f"Working directory: {workdir}\n"
            f"Spec (spec.json in the working directory):\n{task['spec']}\n\n"
            "When finished, write result.json in the working directory: "
            '{"status":"ok|blocked|failed","summary":"...","artifacts":["relative/path"]'
            ',"new_tasks":[{"role":"...","title":"...","spec":{}}]} '
            "`new_tasks` is honoured only for the chief role. Never print secrets.\n"
            + inline_files(task, workdir, inline))

def inline_files(task, workdir, inline):
    """Tool-less (api) models can't read files, so paste small ones into the prompt."""
    if not inline:
        return ""
    out = ""
    for name in json.loads(task["spec"]).get("inline", []) + (["digest.md"] if (Path(workdir) / "digest.md").exists() else []):
        f = Path(workdir) / name
        if f.is_file():
            out += f"\n=== {name} ===\n{f.read_text(errors='replace')[:12000]}\n"
    return out

def digest(c, cfg):
    """Compact state snapshot for the chief: no need to read the whole history."""
    lines = ["# State digest", ""]
    for r in c.execute("SELECT status, COUNT(*) n FROM tasks GROUP BY status"):
        lines.append(f"- {r['status']}: {r['n']}")
    lines += ["", "## Hypotheses"] + [f"- {r['slug']}: {r['status']}" for r in c.execute("SELECT * FROM hypotheses")]
    lines += ["", "## Recent results (newest first)"]
    for r in c.execute("SELECT id,role,status,title,hypothesis,result FROM tasks WHERE status IN ('done','blocked','failed') ORDER BY updated DESC LIMIT 20"):
        summ = (json.loads(r["result"]).get("summary", "") if r["result"] else "")[:300]
        lines.append(f"- #{r['id']} [{r['role']}/{r['status']}] {r['hypothesis'] or '-'}: {r['title']} :: {summ}")
    for name in ("knowledge/dead-ends.md", "GOAL.md"):
        f = ROOT / name
        if f.is_file():
            lines += ["", f"## {name}", f.read_text()[:4000]]
    return "\n".join(lines)

def heartbeat(c, cfg):
    """Keep the system thinking: if idle past heartbeat_s, wake the chief of staff."""
    lim = cfg["limits"]
    busy = c.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('queued','running')").fetchone()[0]
    last = c.execute("SELECT MAX(created) FROM tasks WHERE role='chief'").fetchone()[0] or 0
    if not busy and time.time() - last >= lim["heartbeat_s"]:
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
    lim = cfg["limits"]
    n = 0
    for nt in result.get("new_tasks", []):
        queued = c.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('queued','running')").fetchone()[0]
        if queued >= lim["max_queued"] or task["depth"] + 1 > lim["max_depth"] or nt.get("role") not in cfg["roles"]:
            event(c, "runner", "task.spawn_refused", task["id"], title=nt.get("title"))
            continue
        add_task(c, nt["role"], nt.get("title", "(untitled)"), nt.get("spec"), parent_id=task["id"],
                 hypothesis=nt.get("hypothesis", task["hypothesis"]), depth=task["depth"] + 1, actor=f"task:{task['id']}")
        n += 1
    return n

def execute(c, cfg, task):
    role = cfg["roles"][task["role"]]
    # Deterministic gate: backtests cannot start without a complete preregistration.
    if role.get("requires_prereg"):
        prereg = json.loads(task["spec"]).get("prereg")
        missing = gates.prereg_missing(ROOT / prereg) if prereg else ["<no prereg in spec>"]
        if missing:
            return finish(c, task, "blocked", {"summary": "prereg incomplete"}, missing=missing)
    model, nmodels = pick_model(c, cfg, task)
    workdir = STATE / "workspaces" / f"task-{task['id']}"
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "spec.json").write_text(task["spec"])
    (workdir / "result.json").unlink(missing_ok=True)
    if role.get("digest"):
        (workdir / "digest.md").write_text(digest(c, cfg))
    log_path = workdir / f"run-{task['attempts'] + 1}.log"
    c.execute("UPDATE tasks SET status='running', updated=? WHERE id=?", (time.time(), task["id"]))
    run_id = c.execute("INSERT INTO runs(task_id,model,started,log_path) VALUES(?,?,?,?)",
                       (task["id"], model, time.time(), str(log_path))).lastrowid
    event(c, "runner", "run.started", task["id"], model=model, run=run_id)
    rc, timed_out = adapters.run(model, build_prompt(task["role"], task, workdir, inline=model.startswith("api:")), workdir,
                                 role.get("timeout_s", 900), log_path, role.get("tools", ["Read", "Write"]))
    result = read_result(workdir)
    log_tail = log_path.read_text(errors="replace")[-4000:] if log_path.exists() else ""
    if result is None and RATE_LIMIT.search(log_tail) and not timed_out:
        outcome = "rate_limited"           # not the task's fault: wait, don't burn an attempt
        c.execute("UPDATE tasks SET status='queued', not_before=?, model_idx=?, updated=? WHERE id=?",
                  (time.time() + cfg["limits"]["rate_limit_backoff_s"], min(task["model_idx"] + 1, nmodels - 1),
                   time.time(), task["id"]))
        event(c, "runner", "task.rate_limited", task["id"], model=model)
    elif result is not None and result["status"] in ("ok", "blocked"):
        outcome = "ok" if result["status"] == "ok" else "blocked"
        spawned = enqueue_children(c, cfg, task, result) if outcome == "ok" else 0
        finish(c, task, "done" if outcome == "ok" else "blocked", result, model=model, spawned=spawned)
    else:                                  # timeout, crash, invalid output, or status=failed
        outcome = "timeout" if timed_out else "invalid"
        attempts = task["attempts"] + 1
        if attempts >= task["max_attempts"]:
            finish(c, task, "failed", result, model=model, reason=outcome)
        else:                              # escalate down the fallback chain
            c.execute("UPDATE tasks SET status='queued', attempts=?, model_idx=?, not_before=?, updated=? WHERE id=?",
                      (attempts, min(task["model_idx"] + 1, nmodels - 1), time.time() + 30, time.time(), task["id"]))
            event(c, "runner", "task.retry", task["id"], model=model, reason=outcome)
    c.execute("UPDATE runs SET ended=?, rc=?, outcome=? WHERE id=?", (time.time(), rc, outcome, run_id))

def tick(c, cfg):
    """One scheduling step. Returns 'ran', 'idle', 'stopped' or 'low_mem'."""
    if STOP.exists():
        return "stopped"
    if mem_available_mb() < cfg["limits"]["min_mem_mb"]:
        return "low_mem"
    if runs_last_day(c) >= cfg["limits"]["max_runs_per_day"]:
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
