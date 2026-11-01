"""Git worktrees for agents, and harness-gated integration into main.

Each task with `worktree = true` gets <workspace>/repo: a fresh worktree of kbrain on branch kb/task-N from
origin/main. Agents commit there and never push. When the task ends, integrate():
  1. commits anything the agent left uncommitted (agents forget);
  2. refuses protected paths (engine code, config, roles), large or raw-data files, and anything that looks
     like a credential;
  3. runs the test suite;
  4. under a lock, rebases onto the latest origin/main and pushes HEAD:main (retries on a race);
  5. removes the worktree. A refused or conflicting branch is kept (kb/task-N) and reported.
The operator's checkout (~/proj/kbrain) is never touched: the daemon keeps running the code it started with.
"""
import fcntl, re, subprocess, time
from pathlib import Path
from .db import ROOT, STATE, event

REPO = ROOT.parent                                   # the kbrain checkout
LOCK = STATE / "git.lock"
PROTECTED = ("core/kb/", "core/bin/", "core/config/", "core/roles/", "core/ops/", "core/systemd/",
             "core/tests/", ".gitignore", ".gitleaks.toml", ".github/")
DATA_EXT = (".jsonl", ".ndjson", ".parquet", ".gz", ".zip", ".tgz", ".sqlite", ".db", ".pkl", ".npy", ".feather")
MAX_FILE = 1_000_000
SECRET_RX = re.compile("|".join([
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"\bAKIA[0-9A-Z]{16}\b",
    r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_\-]{20,}",
    r"\bgh[pousr]_[A-Za-z0-9]{30,}",
    r"\bxox[abp]-[A-Za-z0-9-]{20,}",
    r"\b0x[0-9a-fA-F]{64}\b",                                    # raw EVM private key
    r"(?i:(api[_-]?key|secret|private[_-]?key|passphrase|password|token)\s*[:=]\s*['\"][A-Za-z0-9+/=_\-]{16,}['\"])",
]))

def git(*args, cwd=None, check=True, timeout=120):
    p = subprocess.run(["git", *args], cwd=cwd or REPO, capture_output=True, text=True, timeout=timeout)
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip()[-500:]}")
    return p.stdout.strip()

class _Lock:
    def __enter__(self):
        LOCK.parent.mkdir(parents=True, exist_ok=True)
        self.f = open(LOCK, "w"); fcntl.flock(self.f, fcntl.LOCK_EX); return self
    def __exit__(self, *a):
        fcntl.flock(self.f, fcntl.LOCK_UN); self.f.close()

def branch(task):
    return f"kb/task-{task['id']}"

def create(task, workdir):
    """Fresh worktree at workdir/repo on kb/task-N from origin/main. Returns its path."""
    wt = Path(workdir) / "repo"
    with _Lock():
        git("fetch", "-q", "origin", "main", timeout=90)
        if wt.exists():
            git("worktree", "remove", "--force", str(wt), check=False)
        git("worktree", "prune", check=False)
        git("branch", "-D", branch(task), check=False)
        git("worktree", "add", "-q", "-b", branch(task), str(wt), "origin/main")
    git("config", "user.name", "kbrain", cwd=wt, check=False)
    return wt

def check_changes(wt, base):
    """Reasons to refuse this branch (empty list = OK)."""
    bad = []
    files = [f for f in git("diff", "--name-only", f"{base}..HEAD", cwd=wt).splitlines() if f]
    for f in files:
        if f.startswith(PROTECTED):
            bad.append(f"protected path {f} (engine changes go through the operator)")
        p = Path(wt) / f
        if p.is_file():
            if p.stat().st_size > MAX_FILE:
                bad.append(f"{f} is {p.stat().st_size // 1000} kB (raw data stays out of git)")
            if f.endswith(DATA_EXT):
                bad.append(f"{f} looks like raw data")
    added = "\n".join(l[1:] for l in git("diff", "-U0", f"{base}..HEAD", cwd=wt).splitlines()
                      if l.startswith("+") and not l.startswith("+++"))
    m = SECRET_RX.search(added)
    if m:
        bad.append(f"possible credential: {m.group(0)[:12]}...")
    return bad, files

def _tests(wt):
    p = subprocess.run(["python3", "-m", "unittest", "discover", "-s", "core/tests"], cwd=wt,
                       capture_output=True, text=True, timeout=600)
    return p.returncode == 0, (p.stdout + p.stderr)[-1500:]

def _cleanup(task, wt, keep_branch):
    git("worktree", "remove", "--force", str(wt), check=False)
    if not keep_branch:
        git("branch", "-D", branch(task), check=False)

def integrate(c, task, workdir, role_name):
    """Merge the task's commits into origin/main. Returns a short status string."""
    wt = Path(workdir) / "repo"
    if not wt.is_dir():
        return "no worktree"
    try:
        if git("status", "--porcelain", cwd=wt):
            git("add", "-A", cwd=wt)
            git("commit", "-q", "-m", f"{role_name}: work left uncommitted at the end of task #{task['id']}", cwd=wt, check=False)
        base = git("merge-base", "HEAD", "origin/main", cwd=wt)
        n = int(git("rev-list", "--count", f"{base}..HEAD", cwd=wt) or 0)
        if n == 0:
            _cleanup(task, wt, keep_branch=False); return "no commits"
        bad, files = check_changes(wt, base)
        if bad:
            event(c, "git", "git.refused", task["id"], role=role_name, reasons=bad[:8], branch=branch(task))
            _cleanup(task, wt, keep_branch=True); return "refused: " + "; ".join(bad[:3])
        with _Lock():
            for attempt in range(4):
                git("fetch", "-q", "origin", "main", cwd=wt, timeout=90)
                r = subprocess.run(["git", "rebase", "-q", "origin/main"], cwd=wt, capture_output=True, text=True)
                if r.returncode:
                    git("rebase", "--abort", cwd=wt, check=False)
                    event(c, "git", "git.conflict", task["id"], role=role_name, branch=branch(task), files=files[:20])
                    _cleanup(task, wt, keep_branch=True); return "conflict with main (branch kept)"
                ok, out = _tests(wt)
                if not ok:
                    event(c, "git", "git.tests_failed", task["id"], role=role_name, branch=branch(task), out=out)
                    _cleanup(task, wt, keep_branch=True); return "tests failed (branch kept)"
                push = subprocess.run(["git", "push", "-q", "origin", "HEAD:main"], cwd=wt, capture_output=True, text=True, timeout=120)
                if push.returncode == 0:
                    sha = git("rev-parse", "--short", "HEAD", cwd=wt)
                    event(c, "git", "git.merged", task["id"], role=role_name, sha=sha, commits=n, files=files[:30])
                    _cleanup(task, wt, keep_branch=False); return f"merged {n} commit(s) as {sha}"
                time.sleep(2 + attempt * 3)              # someone pushed first: fetch, rebase, retry
            event(c, "git", "git.push_failed", task["id"], role=role_name, branch=branch(task), err=push.stderr[-500:])
            _cleanup(task, wt, keep_branch=True); return "push failed (branch kept)"
    except Exception as e:                               # never let git trouble kill the runner
        event(c, "git", "git.error", task["id"], role=role_name, error=str(e)[-800:])
        _cleanup(task, wt, keep_branch=True); return f"git error: {e}"[:200]

def board(wt, n_commits=40):
    """Shared coordination view: every desk's outbox and notebook head, plus recent commits on main."""
    wt = Path(wt)
    L = ["# Board (built by the harness at the start of your shift)", "",
         "## Recent commits on main (newest first)", "```", git("log", f"-{n_commits}", "--format=%h %ar %s", cwd=wt, check=False), "```", ""]
    desks = sorted(p for p in (wt / "desks").glob("*") if p.is_dir()) if (wt / "desks").is_dir() else []
    for d in desks:
        L.append(f"## desk: {d.name}")
        nb, ob = d / "NOTEBOOK.md", d / "OUTBOX.md"
        if nb.is_file():
            L += ["notebook (top):", *nb.read_text(errors="replace").splitlines()[:25]]
        if ob.is_file():
            L += ["outbox (latest requests):", *ob.read_text(errors="replace").splitlines()[-20:]]
        L.append("")
    if not desks:
        L.append("(no desk has written yet: you may be first)")
    return "\n".join(L)
