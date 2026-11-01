import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def sh(*a, cwd):
    return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()

class GitOps(unittest.TestCase):
    """Worktree + gated integration against a throwaway bare origin (never the real remote)."""
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        os.environ["KB_STATE"] = str(self.tmp / "state")
        from kb import db, gitops
        self.db, self.g = db, gitops
        bare, seed = self.tmp / "origin.git", self.tmp / "seed"
        sh("git", "init", "-q", "--bare", "-b", "main", str(bare), cwd=self.tmp)
        sh("git", "clone", "-q", str(bare), str(seed), cwd=self.tmp)
        (seed / "core" / "tests").mkdir(parents=True); (seed / "core" / "kb").mkdir()
        (seed / "core" / "tests" / "test_ok.py").write_text("import unittest\nclass T(unittest.TestCase):\n    def test(self): pass\n")
        (seed / "core" / "kb" / "engine.py").write_text("x = 1\n")
        (seed / "README.md").write_text("hi\n")
        for a in (("add", "-A"), ("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "seed"), ("push", "-q", "origin", "main")):
            sh("git", *a, cwd=seed)
        gitops.REPO = seed                     # the "operator checkout"
        gitops.LOCK = self.tmp / "git.lock"
        self.c = db.connect()

    def task(self, n):
        wd = self.tmp / f"ws{n}"; wd.mkdir()
        t = {"id": n}
        wt = self.g.create(t, wd)
        sh("git", "config", "user.email", "kb@local", cwd=wt)
        return t, wd, wt

    def remote_log(self):
        return sh("git", "log", "origin/main", "--format=%s", cwd=self.g.REPO) if not sh("git", "fetch", "-q", "origin", cwd=self.g.REPO) else ""

    def test_clean_change_merges_and_uncommitted_work_is_kept(self):
        t, wd, wt = self.task(1)
        (wt / "desks" / "kalshi").mkdir(parents=True)
        (wt / "desks" / "kalshi" / "NOTEBOOK.md").write_text("# kalshi\n- scored 40 windows\n")
        status = self.g.integrate(self.c, t, wd, "kalshi")         # never committed: harness commits it
        self.assertTrue(status.startswith("merged"), status)
        self.assertIn("kalshi: work left uncommitted", self.remote_log())
        self.assertFalse(wt.exists())

    def test_protected_path_secret_and_data_are_refused(self):
        for n, (path, body) in enumerate([("core/kb/engine.py", "x = 2\n"),
                                          ("desks/a/n.md", 'api_key = "abcdefghijklmnopqrstuvwx"\n'),
                                          ("desks/a/tape.jsonl", "{}\n")], start=10):
            t, wd, wt = self.task(n)
            (wt / path).parent.mkdir(parents=True, exist_ok=True); (wt / path).write_text(body)
            sh("git", "add", "-A", cwd=wt); sh("git", "commit", "-qm", "x", cwd=wt)
            status = self.g.integrate(self.c, t, wd, "a")
            self.assertTrue(status.startswith("refused"), (path, status))
        self.assertEqual(self.remote_log(), "seed")

    def test_two_desks_race_both_land(self):
        (t1, wd1, wt1), (t2, wd2, wt2) = self.task(21), self.task(22)
        for wt, name in ((wt1, "hl"), (wt2, "predx")):
            (wt / "desks" / name).mkdir(parents=True); (wt / "desks" / name / "NOTEBOOK.md").write_text(name)
            sh("git", "add", "-A", cwd=wt); sh("git", "commit", "-qm", f"{name}: note", cwd=wt)
        self.assertTrue(self.g.integrate(self.c, t1, wd1, "hl").startswith("merged"))
        self.assertTrue(self.g.integrate(self.c, t2, wd2, "predx").startswith("merged"))   # rebases onto hl's push
        log = self.remote_log()
        self.assertIn("hl: note", log); self.assertIn("predx: note", log)

    def test_conflict_keeps_branch(self):
        (t1, wd1, wt1), (t2, wd2, wt2) = self.task(31), self.task(32)
        for wt, txt in ((wt1, "one\n"), (wt2, "two\n")):
            (wt / "README.md").write_text(txt); sh("git", "commit", "-qam", txt.strip(), cwd=wt)
        self.assertTrue(self.g.integrate(self.c, t1, wd1, "a").startswith("merged"))
        self.assertIn("conflict", self.g.integrate(self.c, t2, wd2, "b"))
        self.assertIn("kb/task-32", sh("git", "branch", "--list", "kb/task-32", cwd=self.g.REPO))

if __name__ == "__main__":
    unittest.main()
