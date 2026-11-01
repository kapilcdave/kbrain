#!/usr/bin/env python3
"""Box-side gate for kbrain agents (python3.9-compatible, stdlib only).

Installed as the FORCED command for the agents' key in ~/.ssh/authorized_keys:
    restrict,command="/usr/bin/python3 -I /home/ec2-user/.kbro/kbro_gate.py" ssh-ed25519 AAAA... kbro-agent
Agents get a full shell (sudo, deploys, collectors, dry runs). The gate adds two things:
  1. an audit log of every command (~/.kbro/audit.log);
  2. a tripwire on the obvious ways to place REAL orders or leak keys. Operator policy (2026-11-01):
     agents do everything except arming live trading; they ask on the board ([to:operator]).
The tripwire catches mistakes, not intent: a determined agent could still arm through a script.
The operator's own key is not affected.
"""
import os, re, subprocess, sys, time

HOME = os.path.expanduser("~")
AUDIT = os.path.join(HOME, ".kbro", "audit.log")
TRIPWIRE = [
    (r"--armed\b", "arming live trading is operator-only: ask on the board with [to:operator]"),
    (r"systemctl\s+(?:--\S+\s+)*(?:start|restart|enable|reenable)\s+(?:\S+\s+)*altspot", "altspot trades real money: the operator starts it"),
    (r"\bmmlive(?:\.py)?\b(?![^\n]*--dry)", "mmlive places real Hyperliquid orders: dry runs need --dry, live runs are operator-only"),
    (r"\bkalshi-mm15\s+live\b(?![^\n]*--dry)", "kalshi-mm15 live is operator-only (use --dry-run)"),
    (r"(?:cat|less|more|head|tail|cp|scp|base64|xxd|od|strings|grep|curl|nc)\b[^\n]*(?:\.kalshi/|\.config/hyperliquid|\.config/geminipred|creds\.env|\.pem\b|_key\b|/env\b)",
     "reading or copying key files is not allowed (programs may use them; agents never print them)"),
    (r"\bprintenv\b|\benv\s*$|/proc/\S*/environ", "dumping the environment can leak keys"),
    (r"authorized_keys", "ssh access is managed by the operator"),
]

def log(status, cmd):
    try:
        os.makedirs(os.path.dirname(AUDIT), exist_ok=True)
        with open(AUDIT, "a") as f:
            f.write("%s\t%s\t%s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), status, cmd.replace("\n", "\\n")[:2000]))
    except OSError:
        pass

def main():
    cmd = os.environ.get("SSH_ORIGINAL_COMMAND", "").strip()
    if not cmd:
        log("refused", "<interactive>")
        sys.stderr.write("kbro: give a command (interactive shells are not available on this key)\n")
        sys.exit(126)
    for rx, why in TRIPWIRE:
        if re.search(rx, cmd):
            log("refused", cmd)
            sys.stderr.write("kbro: refused: %s\n" % why)
            sys.exit(126)
    log("ran", cmd)
    os.chdir(HOME)
    os.execv("/bin/bash", ["bash", "-lc", cmd])

if __name__ == "__main__":
    main()
