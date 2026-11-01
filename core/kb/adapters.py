"""Backends. Each runs one agent turn in `workdir`, logs to `log_path`, returns (rc, timed_out)."""
import json, os, re, shutil, signal, subprocess, urllib.error, urllib.request
from pathlib import Path

SECRET_ENV = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|COOKIE|PRIVATE|SEED|MNEMONIC)", re.I)

SCI_BIN = Path.home() / ".local/share/kbrain/sci/bin"   # numpy/pandas/scipy/sklearn/biopython/torch-cpu

def clean_env():
    """Agents never inherit credentials from the daemon's environment. Their `python3` is the science venv."""
    env = {k: v for k, v in os.environ.items() if not SECRET_ENV.search(k)}
    if SCI_BIN.is_dir():
        env["PATH"] = f"{SCI_BIN}:{env.get('PATH', '')}"
    return env

# Quota/rate-limit text some CLIs print and then silently retry on forever (opencode free tier does).
# Only the CLIs' OWN quota errors. Never generic words like "rate limit" or "429": agents read trading notes
# full of those, and a broad pattern killed healthy runs (2026-11-01).
LIMIT_TEXT = re.compile(r"(Free usage limit reached|(?:You['’]ve|You have) hit your [\w -]{0,24}limit|usage limit reached for|"
                        r"Rate limit reached for|AI_RetryError|RESOURCE_EXHAUSTED|exceeded your current quota|"
                        r"Claude AI usage limit reached|429 Too Many Requests)")
RATE_LIMITED_RC = -29

def _spawn(argv, cwd, log_path, timeout, stdin_text=None):
    """Run one agent. A watchdog tails the log and kills the agent as soon as it reports a quota/rate
    limit, so a rate-limited model costs seconds, not the whole timeout (returns RATE_LIMITED_RC)."""
    import time
    with open(log_path, "ab") as log:
        p = subprocess.Popen(argv, cwd=cwd, env=clean_env(), stdout=log, stderr=subprocess.STDOUT,
                             stdin=subprocess.PIPE if stdin_text else subprocess.DEVNULL,
                             start_new_session=True)
        if stdin_text:
            try:
                p.stdin.write(stdin_text.encode()); p.stdin.close()
            except BrokenPipeError:
                pass
        deadline, seen = time.time() + timeout, 0
        while True:
            try:
                p.wait(timeout=5)
                return p.returncode, False
            except subprocess.TimeoutExpired:
                pass
            try:
                with open(log_path, "rb") as f:
                    f.seek(seen); chunk = f.read().decode(errors="replace"); seen = f.tell()
            except OSError:
                chunk = ""
            if LIMIT_TEXT.search(chunk):
                os.killpg(p.pid, signal.SIGKILL); p.wait()
                with open(log_path, "a") as f:
                    f.write("\n[harness] killed: model reported a usage/rate limit\n")
                return RATE_LIMITED_RC, False
            if time.time() >= deadline:
                os.killpg(p.pid, signal.SIGKILL); p.wait()
                return -9, True

def run_claude(model, prompt, workdir, timeout, log_path, tools):
    """`claude-sonnet-5-5@low` -> --model claude-sonnet-5-5 --effort low. --strict-mcp-config: agents get
    NO MCP servers (no AWS API); box access is only through ./kbssh (gated, logged)."""
    name, _, effort = model.partition("@")
    argv = ["claude", "-p", "--model", name, *(["--effort", effort] if effort else []), "--strict-mcp-config",
            "--permission-mode", "acceptEdits", "--allowedTools", *tools, "--output-format", "text"]
    return _spawn(argv, workdir, log_path, timeout, stdin_text=prompt)

def available(model):
    """False for backends that are not set up yet, so the router skips them instead of burning attempts."""
    backend = model.partition(":")[0]
    if backend in ("claude", "codex", "opencode", "agy"):
        return shutil.which(backend) is not None
    return True

KB_GIT_DIR = Path(__file__).resolve().parents[2] / ".git"

def run_codex(model, prompt, workdir, timeout, log_path, tools):
    """`gpt-5.6-sol@low` -> -m gpt-5.6-sol, reasoning effort low. --ignore-user-config: agents never inherit
    the operator's MCP servers (AWS). Network only for roles that use ./kbssh; the kbrain .git dir is
    writable so commits in the task's repo/ worktree work inside the sandbox."""
    name, _, effort = model.partition("@")
    argv = ["codex", "exec", "-s", "workspace-write", "-C", str(workdir), "--skip-git-repo-check",
            "--ignore-user-config"]
    if name:
        argv += ["-m", name]
    if effort:
        argv += ["-c", f'model_reasoning_effort="{effort}"']
    if any(k in t for t in tools for k in ("kbssh", "WebFetch", "WebSearch")):
        argv += ["-c", "sandbox_workspace_write.network_access=true"]
    if (Path(workdir) / "repo").exists():
        argv += ["--add-dir", str(KB_GIT_DIR)]
    argv.append("-")                       # prompt from stdin
    return _spawn(argv, workdir, log_path, timeout, stdin_text=prompt)

def run_shell(model, prompt, workdir, timeout, log_path, tools):
    """Deterministic (T0) backend: `model` is a command; prompt is ignored. Used for gates/backtests/tests."""
    import shlex
    return _spawn(shlex.split(model), workdir, log_path, timeout)

def run_agy(model, prompt, workdir, timeout, log_path, tools):
    """Antigravity CLI (Google AI Pro login). `agy models` lists them: gemini-3.8-flash-{low,medium,high},
    claude-sonnet-4-6, claude-opus-4-6-thinking, gpt-oss-120b-medium. Shell access follows the role's tools:
    Rules are command prefixes (agy syntax: `command(gh pr list)`), so Bash(python3:*) -> command(python3)."""
    allow = ["command(cat)", "command(ls)", "command(echo)"]
    if any(t.startswith("Bash(") for t in tools):          # roles with a shell get the ordinary dev toolbox
        allow += [f"command({c})" for c in ("git", "grep", "rg", "find", "head", "tail", "wc", "sort", "uniq", "sed",
                  "awk", "cut", "diff", "jq", "mkdir", "cp", "mv", "touch", "date", "pwd", "tar", "gzip", "zcat", "file", "stat",
                  "python", "curl", "wget", "unzip", "gunzip", "tee", "xargs", "tr", "printf", "basename", "dirname",
                  "realpath", "which", "test", "du", "df", "nproc", "free")]
    if any(t in ("WebFetch", "WebSearch") for t in tools):                 # web roles fetch papers and APIs
        allow += ["read_url(api.biorxiv.org)", "read_url(export.arxiv.org)", "read_url(arxiv.org)",
                  "read_url(eutils.ncbi.nlm.nih.gov)", "read_url(www.ncbi.nlm.nih.gov)", "read_url(huggingface.co)",
                  "read_url(proteingym.org)", "read_url(github.com)", "read_url(raw.githubusercontent.com)",
                  "read_url(www.biorxiv.org)", "read_url(rest.uniprot.org)", "read_url(www.ebi.ac.uk)",
                  "read_url(alphafold.ebi.ac.uk)", "read_url(www.rcsb.org)", "read_url(pubmed.ncbi.nlm.nih.gov)"]
    for t in tools:
        if t.startswith("Bash(") and t.endswith(":*)"):
            allow.append(f"command({t[5:-3]})")
    settings = json.dumps({"permissions": {"allow": allow}})      # session-only, never saved
    argv = ["agy", "--sandbox", "--mode", "accept-edits", "--settings", settings, "--add-dir", str(workdir)]
    if model:
        argv += ["--model", model]
    argv.append("--print=" + prompt)       # --print consumes the next token as the prompt
    return _spawn(argv, workdir, log_path, timeout)

def run_opencode(model, prompt, workdir, timeout, log_path, tools):
    """opencode run -m provider/model: free models (big-pickle etc.) with file tools, in `workdir`."""
    argv = ["opencode", "run", "--dir", str(workdir), "--auto", "--print-logs", "--log-level", "WARN"]
    if model:
        argv += ["-m", model]
    argv.append(prompt)
    return _spawn(argv, workdir, log_path, timeout)

def load_env():
    """Provider keys live in ~/.config/kbrain/env (chmod 600), loaded into the daemon only.
    clean_env() strips them from every agent subprocess; API calls happen in-process."""
    f = Path.home() / ".config" / "kbrain" / "env"
    if f.is_file():
        for line in f.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))

def run_api(model, prompt, workdir, timeout, log_path, tools):
    """Tool-less single-shot call to any OpenAI-compatible endpoint (free tiers: OpenRouter, Groq, ...).
    `model` is "provider/model-id"; provider is defined in routing.toml [providers.*].
    The reply must contain the result.json object; we extract and write it."""
    from .router import load_config
    prov, _, mid = model.partition("/")
    cfg = load_config()["providers"][prov]
    body = json.dumps({"model": mid, "messages": [
        {"role": "system", "content": "You have no tools or file access. Reply with ONLY the result.json object as JSON."},
        {"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(cfg["base_url"].rstrip("/") + "/chat/completions", data=body, headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + os.environ.get(cfg["key_env"], "")})
    def log(msg):
        with open(log_path, "a") as f:
            f.write(msg + "\n")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            text = json.load(r)["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        log(f"HTTP {e.code} {'rate limit' if e.code == 429 else ''}")
        return e.code, False
    except TimeoutError:
        log("timeout"); return -9, True
    except Exception as e:                       # network, bad JSON shape, ...
        log(f"error: {type(e).__name__}"); return -1, False
    log(text[-4000:])
    i = text.find("{")
    while i != -1:
        try:
            obj, _ = json.JSONDecoder().raw_decode(text[i:])
            if isinstance(obj, dict) and "status" in obj:
                (Path(workdir) / "result.json").write_text(json.dumps(obj))
                break
        except json.JSONDecodeError:
            pass
        i = text.find("{", i + 1)
    return 0, False

BACKENDS = {"claude": run_claude, "codex": run_codex, "agy": run_agy, "opencode": run_opencode, "shell": run_shell, "api": run_api}

def run(model, prompt, workdir, timeout, log_path, tools):
    backend, _, name = model.partition(":")
    return BACKENDS[backend](name, prompt, workdir, timeout, log_path, tools)
