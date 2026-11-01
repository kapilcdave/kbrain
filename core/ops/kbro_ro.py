#!/usr/bin/env python3
"""Read-only gate for kbrain agents on a trading box (python3.9-compatible, stdlib only).

Installed on each box as a FORCED command in ~/.ssh/authorized_keys for the agents' key only:
    restrict,command="/usr/bin/python3 ~/.kbro/kbro_ro.py" ssh-ed25519 AAAA... kbro-readonly
so whatever the agent asks for arrives in $SSH_ORIGINAL_COMMAND and runs only if it is on the allowlist.
No shell: no pipes, redirects, globs or `;`. Agents look and pull data; they never start, stop, arm,
kill, write, or read credentials. The operator's own key is untouched and unrestricted.
"""
import os, shlex, subprocess, sys

HOME = os.path.expanduser("~")
SECRET = (".kalshi", ".ssh", ".config", ".aws", ".gnupg", ".bash", ".profile", ".env", "/env", "environ",
          "creds", "credential", "secret", "token", ".pem", ".key", "_key", "id_ed25519", "id_rsa", "wallet",
          "mnemonic", "seed", ".kbro", ".netrc", ".git-credentials", "/etc/shadow", ".python_history")
TAR_EXCLUDES = ["--exclude=.*", "--exclude=*env*", "--exclude=*cred*", "--exclude=*secret*", "--exclude=*key*",
                "--exclude=*.pem", "--exclude=*token*"]
SIMPLE = {"uptime", "df", "free", "date", "hostname", "whoami", "nproc", "ls", "du", "wc", "head", "tail", "cat",
          "zcat", "stat", "md5sum", "sha256sum", "file", "pgrep", "grep", "zgrep", "journalctl", "systemctl", "ps", "tar"}
SYSTEMCTL_OK = {"status", "is-active", "is-failed", "is-enabled", "list-units", "list-timers"}
JOURNAL_BAD = ("--vacuum", "--rotate", "--flush", "--relinquish", "--sync", "--setup-keys", "--update-catalog", "-f", "--follow")

def die(msg):
    sys.stderr.write("kbro-readonly: refused: " + msg + "\n")
    sys.exit(126)

def secretish(arg):
    a = arg.lower()
    if any(s in a for s in SECRET):
        return True
    if not arg.startswith("-") and os.path.lexists(os.path.expanduser(arg)):
        real = os.path.realpath(os.path.expanduser(arg)).lower()
        return any(s in real for s in SECRET)
    return False

def check(argv):
    cmd, args = argv[0], argv[1:]
    if cmd not in SIMPLE:
        die("command not allowed: " + cmd + " (allowed: " + ", ".join(sorted(SIMPLE)) + ")")
    for a in args:
        if secretish(a):
            die("argument touches a credential path: " + a)
    if cmd == "systemctl":
        if not args or args[0] not in SYSTEMCTL_OK:
            die("systemctl only allows: " + ", ".join(sorted(SYSTEMCTL_OK)))
    if cmd == "journalctl" and any(a.startswith(b) for a in args for b in JOURNAL_BAD):
        die("journalctl maintenance/follow flags are not allowed")
    if cmd == "tail" and any(a in ("-f", "-F", "--follow") or a.startswith("--follow") for a in args):
        die("tail -f is not allowed (use -n)")
    if cmd in ("grep", "zgrep") and any(a in ("-r", "-R", "--recursive", "-d") or (a.startswith("-") and not a.startswith("--") and ("r" in a or "R" in a)) for a in args):
        die("recursive grep is not allowed; name the files")
    if cmd == "ps":
        prev = ""
        for a in args:
            if prev in ("-o", "-p", "-u", "-C", "--sort", "-eo"):
                prev = ""; continue
            if not a.startswith("-") and a not in ("aux", "ax", "axo", "auxww", "axww"):
                die("ps BSD flags beyond aux/ax are not allowed (no environment dumps)")
            if a.startswith("-") and "E" in a.lstrip("-"):
                die("ps environment flags are not allowed")
            prev = a
    if cmd == "tar":
        if len(args) < 3 or args[0].lstrip("-") not in ("czf", "cf", "cJf") or args[1] != "-":
            die("tar only as: tar czf - <path under ~> ...")
        for p in args[2:]:
            if p.startswith("-"):
                die("tar options beyond czf - are not allowed")
            real = os.path.realpath(os.path.join(HOME, os.path.expanduser(p)))
            if not real.startswith(HOME + "/") or real == HOME:
                die("tar paths must be subdirectories of ~ (not ~ itself): " + p)
        mode = args[0].lstrip("-")
        return (["tar", "-c"] + (["-z"] if "z" in mode else ["-J"] if "J" in mode else [])
                + ["-f", "-", "-C", HOME] + TAR_EXCLUDES + args[2:])
    return [cmd] + args

def main():
    raw = os.environ.get("SSH_ORIGINAL_COMMAND", "").strip()
    if not raw:
        die("no command given (interactive shells are disabled for this key)")
    if any(ch in raw for ch in ";&|`$<>\n"):
        die("shell syntax is not allowed: run one plain command")
    try:
        argv = shlex.split(raw)
    except ValueError as e:
        die("could not parse: %s" % e)
    os.chdir(HOME)                         # before checks, so relative paths and symlinks resolve from ~
    argv = check(argv)
    try:
        sys.exit(subprocess.run(argv, timeout=300).returncode)
    except subprocess.TimeoutExpired:
        die("timed out after 300 s")

if __name__ == "__main__":
    main()
