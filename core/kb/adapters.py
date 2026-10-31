"""Backends. Each runs one agent turn in `workdir`, logs to `log_path`, returns (rc, timed_out)."""
import json, os, re, signal, subprocess, urllib.error, urllib.request
from pathlib import Path

SECRET_ENV = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|COOKIE|PRIVATE|SEED|MNEMONIC)", re.I)

def clean_env():
    """Agents never inherit credentials from the daemon's environment."""
    return {k: v for k, v in os.environ.items() if not SECRET_ENV.search(k)}

def _spawn(argv, cwd, log_path, timeout, stdin_text=None):
    with open(log_path, "ab") as log:
        p = subprocess.Popen(argv, cwd=cwd, env=clean_env(), stdout=log, stderr=subprocess.STDOUT,
                             stdin=subprocess.PIPE if stdin_text else subprocess.DEVNULL,
                             start_new_session=True)
        try:
            p.communicate(stdin_text.encode() if stdin_text else None, timeout=timeout)
            return p.returncode, False
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
            return -9, True

def run_claude(model, prompt, workdir, timeout, log_path, tools):
    argv = ["claude", "-p", "--model", model, "--permission-mode", "acceptEdits",
            "--allowedTools", *tools, "--output-format", "text"]
    return _spawn(argv, workdir, log_path, timeout, stdin_text=prompt)

def run_codex(model, prompt, workdir, timeout, log_path, tools):
    argv = ["codex", "exec", "-s", "workspace-write", "-C", str(workdir), "--skip-git-repo-check"]
    if model:
        argv += ["-m", model]
    argv.append("-")                       # prompt from stdin
    return _spawn(argv, workdir, log_path, timeout, stdin_text=prompt)

def run_shell(model, prompt, workdir, timeout, log_path, tools):
    """Deterministic (T0) backend: `model` is a command; prompt is ignored. Used for gates/backtests/tests."""
    import shlex
    return _spawn(shlex.split(model), workdir, log_path, timeout)

def run_gemini(model, prompt, workdir, timeout, log_path, tools):
    argv = ["gemini", "--approval-mode", "auto_edit", "-p", "Complete the task described above."]
    if model:
        argv += ["-m", model]
    return _spawn(argv, workdir, log_path, timeout, stdin_text=prompt)

def run_opencode(model, prompt, workdir, timeout, log_path, tools):
    """opencode run -m provider/model: free models (big-pickle etc.) with file tools, in `workdir`."""
    argv = ["opencode", "run", "--dir", str(workdir)]
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

BACKENDS = {"claude": run_claude, "codex": run_codex, "gemini": run_gemini, "opencode": run_opencode, "shell": run_shell, "api": run_api}

def run(model, prompt, workdir, timeout, log_path, tools):
    backend, _, name = model.partition(":")
    return BACKENDS[backend](name, prompt, workdir, timeout, log_path, tools)
