import json, os, sys, tempfile, threading, time, unittest, urllib.request, urllib.error
from pathlib import Path

PREREG = """# Prereg
## Hypothesis
x
## Universe
x
## Evaluation window / holdout
x
## Entry and exit rules
x
## Fees and slippage
x
## Independent unit and clustering
x
## Primary endpoint
x
## Controls and baseline
x
## Pass / fail / underpowered / blocked responses
x
"""

def script(tmp, name, body):
    p = Path(tmp) / name
    p.write_text("#!/bin/sh\n" + body)
    p.chmod(0o755)
    return f"shell:{p}"

def result(obj):
    return "cat > result.json <<'J'\n" + json.dumps(obj) + "\nJ\n"

class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["KB_STATE"] = self.tmp
        for m in [m for m in sys.modules if m.startswith("kb")]:
            del sys.modules[m]
        from kb import db, runner, lifecycle
        self.db, self.runner, self.lc = db, runner, lifecycle
        self.c = db.connect()
        self.cfg = {"limits": {"min_mem_mb": 0, "heartbeat_s": 10**12, "max_runs_per_day": 100, "stall_runs": 100,
                               "max_open_hypotheses": 5},
                    "gates": {"min_units": 30, "max_prereg_attempts": 2},
                    "roles": {"chief": {"models": ["shell:true"], "can_spawn": True, "spawnable": ["researcher", "curator"]},
                              "researcher": {"models": ["shell:true"]}, "curator": {"models": ["shell:true"]},
                              "backtester": {"models": ["shell:true"], "requires_prereg": True, "with_stats": True},
                              "skeptic": {"models": ["shell:true"], "with_stats": True}}}

    def drain(self, n=10):
        for _ in range(n):
            self.c.execute("UPDATE tasks SET not_before=0")
            if self.runner.tick(self.c, self.cfg) != "ran":
                break

    def hstatus(self, slug):
        return self.c.execute("SELECT status, reason FROM hypotheses WHERE slug=?", (slug,)).fetchone()

class Pipeline(Base):
    def setup_roles(self, metrics, verdict="SURVIVES"):
        r = self.cfg["roles"]
        r["researcher"]["models"] = [script(self.tmp, "res.sh", "cat > prereg.md <<'P'\n" + PREREG + "P\n" + result({"status": "ok", "summary": "prereg"}))]
        r["backtester"]["models"] = [script(self.tmp, "bt.sh", "test -f kbstats.py && test -d inputs || exit 1\n" + result({"status": "ok", "summary": "bt", "metrics": metrics}))]
        r["skeptic"]["models"] = [script(self.tmp, "sk.sh", result({"status": "ok", "summary": "audit", "verdict": verdict}))]

    def test_full_pipeline_validates(self):
        self.setup_roles({"net_mean": 1, "ci_low": 0.2, "ci_high": 2, "n_units": 40, "net_mean_ex_top": 0.5})
        self.db.add_task(self.c, "researcher", "idea", {}, hypothesis="funding-revert")
        self.drain()
        self.assertEqual(self.hstatus("funding-revert")["status"], "validated")
        roles = [r[0] for r in self.c.execute("SELECT role FROM tasks ORDER BY id")]
        self.assertEqual(roles, ["researcher", "backtester", "skeptic"])
        self.assertTrue((Path(self.tmp) / "prereg" / "funding-revert.md").is_file())

    def test_negative_ci_rejected_and_recorded(self):
        self.setup_roles({"net_mean": 0.1, "ci_low": -0.3, "ci_high": 0.5, "n_units": 60})
        self.db.add_task(self.c, "researcher", "idea", {}, hypothesis="bad-idea")
        self.drain()
        self.assertEqual(self.hstatus("bad-idea")["status"], "rejected")
        self.assertIn("bad-idea", (Path(self.tmp) / "dead-ends.md").read_text())
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM tasks WHERE role='skeptic' AND json_extract(spec,'$.standing') IS NULL").fetchone()[0], 0)

    def test_missing_metrics_parks(self):
        self.setup_roles(None)
        self.db.add_task(self.c, "researcher", "idea", {}, hypothesis="no-metrics")
        self.drain()
        self.assertEqual(self.hstatus("no-metrics")["status"], "parked")

    def test_tampered_prereg_blocks_backtest(self):
        self.setup_roles({"net_mean": 1, "ci_low": 0.2, "ci_high": 2, "n_units": 40})
        self.db.add_task(self.c, "researcher", "idea", {}, hypothesis="tamper")
        self.runner.tick(self.c, self.cfg)                          # researcher only
        frozen = Path(self.tmp) / "prereg" / "tamper.md"
        frozen.write_text(frozen.read_text() + "\nedited after freezing\n")
        self.drain()
        self.assertEqual(self.hstatus("tamper")["status"], "parked")
        self.assertIn("modified", self.hstatus("tamper")["reason"])

    def test_incomplete_prereg_retried_once_then_parked(self):
        self.cfg["roles"]["researcher"]["models"] = [script(self.tmp, "r.sh", "echo '# just a hypothesis' > prereg.md\n" + result({"status": "ok", "summary": "s"}))]
        self.db.add_task(self.c, "researcher", "idea", {}, hypothesis="vague")
        self.drain()
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM tasks WHERE role='researcher'").fetchone()[0], 2)
        self.assertEqual(self.hstatus("vague")["status"], "parked")

class VenueFlow(Base):
    """Operator idea -> chief -> venue bro -> backtester -> skeptic -> venue bro (verdict) -> chief (dry deploy)."""
    def test_idea_runs_through_the_venue_bro_and_comes_back_to_the_chief(self):
        r = self.cfg["roles"]
        for v in r.values(): v["standing_orders"] = False      # production: no background work
        r["chief"].update({"spawnable": ["kalshi"], "models": [script(self.tmp, "chief.sh",
            'if grep -q deploy spec.json; then ' + result({"status": "ok", "summary": "deployed dry"}).replace("\n", "\n") + 'else\n'
            + result({"status": "ok", "summary": "triaged", "new_tasks": [{"role": "kalshi", "hypothesis": "penny-jump-eth",
                      "title": "Prereg: penny jump", "spec": {"domain": "kalshi", "idea": "x"}}]}) + 'fi\n')]})
        r["kalshi"] = {"venue_bro": True, "models": [script(self.tmp, "k.sh", "cat > prereg.md <<'P'\n" + PREREG + "P\n"
                       + result({"status": "ok", "summary": "venue work"}))]}
        r["backtester"]["models"] = [script(self.tmp, "bt.sh", result({"status": "ok", "summary": "bt",
            "metrics": {"net_mean": 1, "ci_low": 0.2, "ci_high": 2, "n_units": 40, "net_mean_ex_top": 0.5}}))]
        r["skeptic"]["models"] = [script(self.tmp, "sk.sh", result({"status": "ok", "summary": "ok", "verdict": "SURVIVES"}))]
        self.db.add_task(self.c, "chief", "Idea: penny jump on ETH 15M", {"kind": "idea", "idea": "penny jump"})
        self.drain(12)
        roles = [x[0] for x in self.c.execute("SELECT role FROM tasks ORDER BY id")]
        self.assertEqual(roles, ["chief", "kalshi", "backtester", "skeptic", "kalshi", "chief"])
        self.assertEqual(self.hstatus("penny-jump-eth")["status"], "validated")
        kinds = [json.loads(x[0]).get("kind") for x in self.c.execute("SELECT spec FROM tasks ORDER BY id")]
        self.assertEqual(kinds[4:], ["verdict", "deploy"])

    def test_rejected_idea_still_gets_a_verdict_but_no_deploy(self):
        r = self.cfg["roles"]
        for v in r.values(): v["standing_orders"] = False      # production: no background work
        r["chief"].update({"spawnable": ["kalshi"], "models": [script(self.tmp, "c2.sh", result({"status": "ok", "summary": "t",
            "new_tasks": [{"role": "kalshi", "hypothesis": "bad-fade", "title": "Prereg: fade", "spec": {"domain": "kalshi", "idea": "x"}}]}))]})
        r["kalshi"] = {"venue_bro": True, "models": [script(self.tmp, "k2.sh", "cat > prereg.md <<'P'\n" + PREREG + "P\n"
                       + result({"status": "ok", "summary": "v"}))]}
        r["backtester"]["models"] = [script(self.tmp, "bt2.sh", result({"status": "ok", "summary": "bt",
            "metrics": {"net_mean": 0.1, "ci_low": -0.3, "ci_high": 0.5, "n_units": 60}}))]
        self.db.add_task(self.c, "chief", "Idea: fade", {"kind": "idea", "idea": "fade"})
        self.drain(12)
        roles = [x[0] for x in self.c.execute("SELECT role FROM tasks ORDER BY id")]
        self.assertEqual(roles, ["chief", "kalshi", "backtester", "kalshi"])
        self.assertEqual(self.hstatus("bad-fade")["status"], "rejected")

class AntiSpiral(Base):
    def chief_proposes(self, tasks):
        self.cfg["roles"]["chief"]["models"] = [script(self.tmp, f"c{time.time_ns()}.sh", result({"status": "ok", "summary": "plan", "new_tasks": tasks}))]
        self.db.add_task(self.c, "chief", f"plan {time.time_ns()}")
        self.runner.tick(self.c, self.cfg)

    def refusals(self):
        return [json.loads(r[0])["reason"] for r in self.c.execute("SELECT data FROM events WHERE kind='task.spawn_refused' ORDER BY id")]

    def test_admission_rules(self):
        self.chief_proposes([
            {"role": "researcher", "hypothesis": "alpha-one", "title": "a"},
            {"role": "researcher", "hypothesis": "alpha-one", "title": "dup slug"},
            {"role": "researcher", "title": "no slug"},
            {"role": "backtester", "hypothesis": "alpha-one", "title": "sneaky"},
            {"role": "curator", "title": "compact memory"},
            {"role": "curator", "title": "Compact the memory"},
        ])
        r = self.refusals()
        self.assertEqual(len(r), 4, r)
        self.assertTrue(any("already exists" in x for x in r))
        self.assertTrue(any("slug" in x for x in r))
        self.assertTrue(any("may not spawn backtester" in x for x in r))
        self.assertTrue(any("duplicate" in x for x in r))

    def test_open_slots_cap(self):
        self.cfg["limits"]["max_open_hypotheses"] = 1
        self.chief_proposes([{"role": "researcher", "hypothesis": "h-one", "title": "a"},
                             {"role": "researcher", "hypothesis": "h-two", "title": "b"}])
        self.assertTrue(any("slots" in x for x in self.refusals()))

    def test_stall_pauses_chief_until_ack(self):
        self.cfg["limits"].update(stall_runs=2, heartbeat_s=0)
        for _ in range(2):
            self.c.execute("INSERT INTO runs(task_id,model,started) VALUES(0,'x',?)", (time.time(),))
        self.runner.heartbeat(self.c, self.cfg)
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM tasks WHERE role='chief'").fetchone()[0], 0)
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM events WHERE kind='alert.stall'").fetchone()[0], 1)
        self.runner.heartbeat(self.c, self.cfg)                       # alert only once
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM events WHERE kind='alert.stall'").fetchone()[0], 1)
        time.sleep(0.01)
        self.db.event(self.c, "user", "user.ack")
        self.runner.heartbeat(self.c, self.cfg)
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM tasks WHERE role='chief'").fetchone()[0], 1)

    def test_spec_files_outside_state_not_copied(self):
        self.db.add_task(self.c, "curator", "x", {"files": [str(Path.home() / ".bashrc")]})
        self.runner.tick(self.c, self.cfg)
        self.assertFalse((Path(self.tmp) / "workspaces" / "task-1" / "inputs" / ".bashrc").exists())

class Stats(unittest.TestCase):
    def test_evaluate(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from kb.stats import evaluate
        m = evaluate({i: 1.0 + (i % 3) * 0.1 for i in range(40)})
        self.assertGreater(m["ci_low"], 0)
        self.assertEqual(m["n_units"], 40)
        m = evaluate([(-1) ** i for i in range(40)])
        self.assertLess(m["ci_low"], 0)

class Web(Base):
    def test_api(self):
        from kb import web
        srv = web.make_server(0)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{srv.server_port}"
        try:
            st = json.load(urllib.request.urlopen(base + "/api/state"))
            self.assertIn("hypotheses", st)
            body = json.dumps({"role": "chief", "title": "hello", "spec": {}}).encode()
            with self.assertRaises(urllib.error.HTTPError) as e:
                urllib.request.urlopen(urllib.request.Request(base + "/api/task", data=body))
            self.assertEqual(e.exception.code, 403)
            req = urllib.request.Request(base + "/api/task", data=body, headers={"X-KB": "1", "Content-Type": "application/json"})
            self.assertIn("id", json.load(urllib.request.urlopen(req)))
            self.assertIn(b"<title>kbrain HQ</title>", urllib.request.urlopen(base + "/").read())
        finally:
            srv.shutdown()

class Firm(Base):
    """Parallel lanes, the data engineer + background jobs, and standing orders."""
    def setUp(self):
        super().setUp()
        self.cfg["roles"]["engineer"] = {"models": ["shell:true"], "with_data": True}
        self.cfg["limits"].update(idle_cooldown_s=900, scout_cooldown_s=3600, max_jobs=2, max_job_s=60)
        self.cfg["gates"]["max_data_attempts"] = 2
        from kb import jobs
        self.jobs = jobs

    def test_claim_is_per_role_and_atomic(self):
        self.db.add_task(self.c, "researcher", "r"); self.db.add_task(self.c, "curator", "c")
        t = self.runner.pick(self.c, "curator")
        self.assertEqual(t["role"], "curator")
        self.assertIsNone(self.runner.pick(self.c, "curator"))
        self.assertEqual(self.runner.pick(self.c)["role"], "researcher")

    def test_blocked_backtest_goes_to_engineer_job_then_reruns(self):
        r = self.cfg["roles"]
        r["researcher"]["models"] = [script(self.tmp, "res.sh", "cat > prereg.md <<'P'\n" + PREREG + "P\n" + result({"status": "ok", "summary": "p"}))]
        r["backtester"]["models"] = [script(self.tmp, "bt.sh", result({"status": "blocked", "summary": "need kalshi trades"}))]
        r["engineer"]["models"] = [script(self.tmp, "en.sh", "test -L data || exit 1\ncat > collect.py <<'P'\n"
            "import os, pathlib\npathlib.Path(os.environ['KB_DATA_DIR'], 'trades.csv').write_text('t,p\\n1,2\\n')\nP\n"
            + result({"status": "ok", "summary": "collector", "jobs": [{"script": "collect.py", "dataset": "kalshi-trades", "description": "trades"}]}))]
        self.db.add_task(self.c, "researcher", "idea", {}, hypothesis="needs-data")
        for _ in range(3):
            self.c.execute("UPDATE tasks SET not_before=0"); self.runner.tick(self.c, self.cfg)
        self.assertEqual(self.hstatus("needs-data")["status"], "data")
        self.assertEqual(self.c.execute("SELECT status FROM jobs").fetchone()[0], "queued")
        for _ in range(50):
            self.jobs.pump(self.c, self.cfg, self.lc.on_job_done)
            if self.c.execute("SELECT status FROM jobs").fetchone()[0] in ("done", "failed"): break
            time.sleep(0.05)
        self.assertEqual(self.c.execute("SELECT status FROM jobs").fetchone()[0], "done")
        self.assertEqual(self.c.execute("SELECT status FROM datasets WHERE name='kalshi-trades'").fetchone()[0], "ready")
        self.assertEqual(self.hstatus("needs-data")["status"], "backtest")
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM tasks WHERE role='backtester' AND status='queued'").fetchone()[0], 1)

    def test_job_script_must_live_in_workspace(self):
        wd = Path(self.tmp) / "w"; wd.mkdir()
        task = {"id": 1, "hypothesis": None}
        self.assertIn("inside the workspace", self.jobs.submit(self.c, task, {"script": "/etc/passwd.py", "dataset": "x"}, wd, self.cfg))
        self.assertIn("dataset name", self.jobs.submit(self.c, task, {"script": "a.py", "dataset": "../x"}, wd, self.cfg))

    def test_standing_orders_scout_with_cooldown_and_feed_chief(self):
        self.cfg["domains"] = {"list": ["crypto perps", "prediction markets"]}
        self.cfg["limits"]["heartbeat_s"] = 0
        self.cfg["roles"]["researcher"]["models"] = [script(self.tmp, "scout.sh", result({"status": "ok", "summary": "s",
            "ideas": [{"slug": "funding-flip", "idea": "i", "mechanism": "m", "data": "d"}, {"slug": "Bad Slug", "idea": "x"}]}))]
        self.runner.plan(self.c, self.cfg)
        scouts = self.c.execute("SELECT spec FROM tasks WHERE role='researcher'").fetchall()
        self.assertEqual(len(scouts), 1)
        self.c.execute("UPDATE tasks SET status='done' WHERE role!='researcher'")
        t = self.runner.pick(self.c, "researcher"); self.runner.execute(self.c, self.cfg, t)
        self.assertEqual([r[0] for r in self.c.execute("SELECT slug FROM ideas")], ["funding-flip"])
        self.runner.plan(self.c, self.cfg)                         # cooldown: no second scout yet
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM tasks WHERE role='researcher'").fetchone()[0], 1)
        self.assertGreaterEqual(self.c.execute("SELECT COUNT(*) FROM tasks WHERE role='chief'").fetchone()[0], 1)

if __name__ == "__main__":
    unittest.main()
