import json, os, sys, tempfile, time, unittest
from pathlib import Path

class Core(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["KB_STATE"] = self.tmp
        for m in [m for m in sys.modules if m.startswith("kb")]: del sys.modules[m]
        from kb import db, runner
        self.db, self.runner = db, runner
        self.c = db.connect()
        self.cfg = {"limits": {"min_mem_mb": 0, "heartbeat_s": 10**9, "max_runs_per_day": 100, "max_queued": 50, "max_depth": 3, "rate_limit_backoff_s": 100},
                    "roles": {"chief": {"models": ["shell:true"], "can_spawn": True},
                              "curator": {"models": ["shell:true", "shell:true"], "timeout_s": 5},
                              "backtester": {"models": ["shell:true"], "requires_prereg": True}}}

    def test_invalid_output_retries_then_fails(self):
        self.cfg["roles"]["curator"]["models"] = ["shell:true", "shell:true"]
        tid = self.db.add_task(self.c, "curator", "x", max_attempts=2)
        self.assertEqual(self.runner.tick(self.c, self.cfg), "ran")
        self.assertEqual(self.c.execute("SELECT status,model_idx FROM tasks").fetchone()[:], ("queued", 1))
        self.c.execute("UPDATE tasks SET not_before=0")
        self.runner.tick(self.c, self.cfg)
        self.assertEqual(self.c.execute("SELECT status FROM tasks WHERE id=?", (tid,)).fetchone()[0], "failed")

    def test_success_and_spawn_limits(self):
        script = Path(self.tmp) / "ok.sh"
        script.write_text("#!/bin/sh\ncat > result.json <<'J'\n"
            '{"status":"ok","summary":"s","new_tasks":[{"role":"curator","title":"a"},{"role":"nope","title":"b"}]}\nJ\n')
        script.chmod(0o755)
        self.cfg["roles"]["chief"]["models"] = [f"shell:{script}"]
        self.db.add_task(self.c, "chief", "plan", depth=0)
        self.runner.tick(self.c, self.cfg)
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM tasks WHERE role='curator'").fetchone()[0], 1)
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM events WHERE kind='task.spawn_refused'").fetchone()[0], 1)

    def test_prereg_gate_blocks_backtest(self):
        self.db.add_task(self.c, "backtester", "bt", {"prereg": "knowledge/index.md"})
        self.runner.tick(self.c, self.cfg)
        self.assertEqual(self.c.execute("SELECT status FROM tasks").fetchone()[0], "blocked")

    def test_stop_flag_and_rate_limit(self):
        self.db.add_task(self.c, "curator", "x")
        self.runner.STOP.touch()
        self.assertEqual(self.runner.tick(self.c, self.cfg), "stopped")
        self.runner.STOP.unlink()
        self.cfg["roles"]["curator"]["models"] = ["shell:sh -c 'echo usage limit reached'", "shell:true"]
        self.runner.tick(self.c, self.cfg)
        row = self.c.execute("SELECT status,attempts,not_before FROM tasks").fetchone()
        self.assertEqual((row["status"], row["attempts"]), ("queued", 0))
        self.assertGreater(row["not_before"], time.time() + 50)

    def test_heartbeat_wakes_chief_when_idle_and_budget_stops(self):
        self.cfg["limits"]["heartbeat_s"] = 0
        self.cfg["roles"]["chief"].update(models=["shell:true"], digest=True)
        self.runner.tick(self.c, self.cfg)
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM tasks WHERE role='chief'").fetchone()[0], 1)
        self.assertTrue((Path(self.tmp) / "workspaces" / "task-1" / "digest.md").exists())
        self.cfg["limits"]["max_runs_per_day"] = 1
        self.assertEqual(self.runner.tick(self.c, self.cfg), "budget")

    def test_api_backend_extracts_result_json(self):
        import threading, http.server
        class H(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                body = json.dumps({"choices": [{"message": {"content":
                    'Sure!\n{"status":"ok","summary":"from api"}'}}]}).encode()
                self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers()
                self.wfile.write(body)
            def log_message(self, *a): pass
        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        from kb import adapters, router
        router.load_config = lambda: {"providers": {"t": {"base_url": f"http://127.0.0.1:{srv.server_port}", "key_env": "NOPE"}}}
        wd = Path(self.tmp) / "wd"; wd.mkdir()
        rc, to = adapters.run("api:t/model", "hi", wd, 5, wd / "log", [])
        srv.shutdown()
        self.assertEqual((rc, to), (0, False))
        self.assertEqual(json.loads((wd / "result.json").read_text())["summary"], "from api")

if __name__ == "__main__":
    unittest.main()
