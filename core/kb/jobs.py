"""Background collectors. The data engineer writes a script; the harness runs it here, outside any
agent sandbox, so agents never block on data collection and nobody waits on a collector.

A job is `python3 -I <script.py> [args]` inside the engineer's workspace, with a scrubbed environment,
KB_DATA_DIR pointing at its dataset directory, lower priority, a memory ceiling and a hard time limit.
"""
import json, os, resource, signal, subprocess, time
from pathlib import Path
from .adapters import clean_env
from .db import STATE, event

DATA = STATE / "data"
PY = next((str(p) for p in (Path.home() / ".local/share/kbrain/sci/bin/python", Path.home() / ".local/share/kbrain/venv/bin/python")
           if p.exists()), "python3")             # collector env: the science venv
_procs = {}                                # job id -> Popen (this process only)

def _limits(mem_mb):
    def fn():
        os.nice(10)
        resource.setrlimit(resource.RLIMIT_AS, (mem_mb * 2**20, mem_mb * 2**20))
    return fn

def submit(c, task, spec, workdir, cfg):
    """Validate and queue a job the engineer asked for. Returns an error string or None."""
    wd = Path(workdir).resolve()
    script = (wd / str(spec.get("script", ""))).resolve()
    name = str(spec.get("dataset") or spec.get("name") or "").strip()
    if not name or not name.replace("-", "").replace("_", "").isalnum():
        return "job needs a dataset name (letters, digits, - or _)"
    if script.suffix != ".py" or not script.is_file() or not script.is_relative_to(wd):
        return f"job script must be a .py file inside the workspace: {spec.get('script')}"
    args = [str(a) for a in spec.get("args", [])][:20]
    max_s = min(int(spec.get("max_minutes", 60)) * 60, cfg.get("limits", {}).get("max_job_s", 14400))
    c.execute("INSERT INTO jobs(task_id,hypothesis,name,script,args,cwd,dataset,blocking,max_s,created) VALUES(?,?,?,?,?,?,?,?,?,?)",
              (task["id"], task["hypothesis"], str(spec.get("name") or name)[:80], str(script), json.dumps(args), str(wd),
               name, 1 if spec.get("blocking", True) else 0, max_s, time.time()))
    c.execute("INSERT INTO datasets(name,path,description,domain,status,updated) VALUES(?,?,?,?,'pending',?) "
              "ON CONFLICT(name) DO UPDATE SET description=COALESCE(excluded.description,description), updated=excluded.updated",
              (name, str(DATA / name), str(spec.get("description", ""))[:500] or None, spec.get("domain"), time.time()))
    event(c, "jobs", "job.queued", task["id"], dataset=name, script=script.name, blocking=bool(spec.get("blocking", True)))
    return None

def pump(c, cfg, on_done):
    """Start queued jobs up to the limit, reap finished ones, kill overdue ones."""
    now = time.time()
    for j in c.execute("SELECT * FROM jobs WHERE status='running'").fetchall():
        p = _procs.get(j["id"])
        if p is None:                      # runner restarted mid-job: we lost the handle, rerun it
            c.execute("UPDATE jobs SET status='queued', pid=NULL WHERE id=?", (j["id"],)); continue
        if p.poll() is None and now - j["started"] > j["max_s"]:
            os.killpg(p.pid, signal.SIGKILL); p.wait()
        rc = p.poll()
        if rc is None:
            continue
        _procs.pop(j["id"], None)
        ok = rc == 0 and any((DATA / j["dataset"]).glob("*"))
        c.execute("UPDATE jobs SET status=?, ended=?, rc=? WHERE id=?", ("done" if ok else "failed", now, rc, j["id"]))
        c.execute("UPDATE datasets SET status=?, updated=? WHERE name=?", ("ready" if ok else "failed", now, j["dataset"]))
        event(c, "jobs", "job.done" if ok else "job.failed", j["task_id"], dataset=j["dataset"], rc=rc)
        if ok:
            event(c, "jobs", "dataset.ready", j["task_id"], dataset=j["dataset"])
        on_done(c, cfg, dict(j), ok)
    running = c.execute("SELECT COUNT(*) FROM jobs WHERE status='running'").fetchone()[0]
    for j in c.execute("SELECT * FROM jobs WHERE status='queued' ORDER BY id LIMIT ?",
                       (max(0, cfg.get("limits", {}).get("max_jobs", 2) - running),)).fetchall():
        out = DATA / j["dataset"]; out.mkdir(parents=True, exist_ok=True)
        log = Path(j["cwd"]) / f"job-{j['id']}.log"
        env = clean_env() | {"KB_DATA_DIR": str(out), "PYTHONDONTWRITEBYTECODE": "1"}
        with open(log, "ab") as lf:
            p = subprocess.Popen([PY, "-I", j["script"], *json.loads(j["args"])], cwd=j["cwd"], env=env,
                                 stdout=lf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True,
                                 preexec_fn=_limits(cfg.get("limits", {}).get("job_mem_mb", 1024)))
        _procs[j["id"]] = p
        c.execute("UPDATE jobs SET status='running', pid=?, started=?, log_path=? WHERE id=?", (p.pid, time.time(), str(log), j["id"]))
        event(c, "jobs", "job.started", j["task_id"], dataset=j["dataset"])

def catalog(c, limit=40):
    rows = c.execute("SELECT * FROM datasets ORDER BY updated DESC LIMIT ?", (limit,)).fetchall()
    return "\n".join(f"- {r['name']} [{r['status']}{', validated' if r['validated'] else ''}] data/{r['name']}/ : "
                     f"{(r['description'] or '')[:160]}" for r in rows) or "(no datasets yet)"
