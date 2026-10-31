"""kbrain HQ: local-only web server (stdlib). The LARP view and dashboard both read the event log."""
import json, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from . import runner, lifecycle
from .db import STATE, connect, add_task, event
from .router import load_config

STATIC = Path(__file__).parent / "static"

def rows(cur):
    return [dict(r) for r in cur]

def state(c):
    cfg, now = load_config(), time.time()
    alive = runner.ALIVE.stat().st_mtime if runner.ALIVE.exists() else 0
    stalled, _ = lifecycle.stalled(c, cfg)
    return {
        "now": now, "stop": runner.STOP.exists(), "mem_mb": runner.mem_available_mb(),
        "runner_age_s": (now - alive) if alive else None,
        "runs_today": runner.runs_last_day(c), "max_runs": cfg["limits"].get("max_runs_per_day"),
        "stalled": stalled, "open_slots": lifecycle.open_slots(c, cfg),
        "counts": {r["status"]: r["n"] for r in c.execute("SELECT status, COUNT(*) n FROM tasks GROUP BY status")},
        "running": rows(c.execute("SELECT t.id,t.role,t.title,t.hypothesis,r.model,r.started FROM tasks t "
                                  "LEFT JOIN runs r ON r.task_id=t.id AND r.ended IS NULL WHERE t.status='running'")),
        "queued": rows(c.execute("SELECT id,role,title,hypothesis,not_before FROM tasks WHERE status='queued' ORDER BY id LIMIT 40")),
        "last_by_role": {r["role"]: dict(r) for r in c.execute(
            "SELECT id,role,title,status,hypothesis FROM tasks WHERE id IN (SELECT MAX(id) FROM tasks GROUP BY role)")},
        "hypotheses": rows(c.execute("SELECT slug,status,reason,updated FROM hypotheses ORDER BY updated DESC LIMIT 200")),
        "roles": {k: {"models": v.get("models", [])} for k, v in cfg["roles"].items()},
        "stats": rows(c.execute("SELECT model, COUNT(*) n, SUM(outcome='ok') ok, AVG(ended-started) avg_s FROM runs "
                                "WHERE ended IS NOT NULL GROUP BY model ORDER BY n DESC")),
    }

def task_detail(c, tid):
    t = c.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone()
    if not t:
        return None
    runs = rows(c.execute("SELECT * FROM runs WHERE task_id=? ORDER BY id", (tid,)))
    log = ""
    if runs and runs[-1]["log_path"]:
        p = Path(runs[-1]["log_path"])
        if p.is_file() and p.resolve().is_relative_to(STATE.resolve()):
            log = p.read_text(errors="replace")[-8000:]
    return {"task": dict(t), "runs": runs, "log": log,
            "events": rows(c.execute("SELECT * FROM events WHERE task_id=? ORDER BY id", (tid,)))}

class Handler(BaseHTTPRequestHandler):
    server_version = "kbrain"

    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def host_ok(self):                      # blocks DNS-rebinding: only loopback host names
        return (self.headers.get("Host") or "").rsplit(":", 1)[0] in ("127.0.0.1", "localhost")

    def do_GET(self):
        if not self.host_ok():
            return self.send(403, {"error": "host"})
        u, c = urlparse(self.path), connect()
        q = parse_qs(u.query)
        try:
            if u.path in ("/", "/index.html"):
                return self.send(200, (STATIC / "index.html").read_bytes(), "text/html; charset=utf-8")
            if u.path == "/api/state":
                return self.send(200, state(c))
            if u.path == "/api/events":
                after, limit = int(q.get("after", ["0"])[0]), min(int(q.get("limit", ["200"])[0]), 500)
                if after:
                    r = rows(c.execute("SELECT * FROM events WHERE id>? ORDER BY id LIMIT ?", (after, limit)))
                else:
                    r = rows(c.execute("SELECT * FROM (SELECT * FROM events ORDER BY id DESC LIMIT ?) ORDER BY id", (limit,)))
                return self.send(200, r)
            if u.path.startswith("/api/task/"):
                d = task_detail(c, int(u.path.rsplit("/", 1)[1]))
                return self.send(200, d) if d else self.send(404, {"error": "no such task"})
            return self.send(404, {"error": "not found"})
        except ValueError:
            return self.send(400, {"error": "bad request"})
        finally:
            c.close()

    def do_POST(self):
        # Custom header forces a CORS preflight, so other sites can't post here.
        if not self.host_ok() or self.headers.get("X-KB") != "1":
            return self.send(403, {"error": "forbidden"})
        n = int(self.headers.get("Content-Length") or 0)
        if n > 65536:
            return self.send(413, {"error": "too large"})
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            return self.send(400, {"error": "bad json"})
        c, path = connect(), urlparse(self.path).path
        try:
            if path == "/api/task":
                cfg = load_config()
                role, title = body.get("role"), str(body.get("title") or "").strip()[:300]
                spec, slug = body.get("spec") or {}, (body.get("hypothesis") or None)
                if role not in cfg["roles"] or not title or not isinstance(spec, dict):
                    return self.send(400, {"error": "need a known role, a title and an object spec"})
                if slug and not lifecycle.SLUG.fullmatch(slug):
                    return self.send(400, {"error": "hypothesis slug must be kebab-case"})
                return self.send(200, {"id": add_task(c, role, title, spec, hypothesis=slug, actor="user:web")})
            if path == "/api/stop":
                STATE.mkdir(parents=True, exist_ok=True); runner.STOP.touch(); event(c, "user:web", "user.stop")
            elif path == "/api/resume":
                runner.STOP.unlink(missing_ok=True); event(c, "user:web", "user.resume")
            elif path == "/api/ack":
                event(c, "user:web", "user.ack")
            else:
                return self.send(404, {"error": "not found"})
            return self.send(200, {"ok": True})
        finally:
            c.close()

def make_server(port=7777):
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)

def serve(port=7777):
    srv = make_server(port)
    print(f"  kbrain HQ  →  http://127.0.0.1:{port}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
