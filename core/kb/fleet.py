"""Fleet monitor: what runs on which VM, checked by the harness (never by an agent).

The map lives in ~/.config/kbrain/ops.toml (or $KB_OPS): machine config, next to the ssh keys it names.
One read-only ssh per box; the check script is sent on stdin so `pgrep -f` cannot match our own shell.
Output: state/fleet.md (staged into the chief's digest), state/fleet.json (HQ), and alert.fleet events
for runners that are down before their `until`, or boxes that are unreachable.
"""
import json, os, re, shlex, subprocess, time, tomllib
from datetime import datetime, timezone
from pathlib import Path
from .db import STATE, event

OPS = Path(os.environ.get("KB_OPS", Path.home() / ".config" / "kbrain" / "ops.toml"))
FLEET_MD, FLEET_JSON = STATE / "fleet.md", STATE / "fleet.json"

def load(path=OPS):
    return tomllib.loads(Path(path).read_text()) if Path(path).is_file() else {}

UNIT_OK = re.compile(r"[A-Za-z0-9@._-]{1,80}")
PROC_OK = re.compile(r"[A-Za-z0-9 ._/=:,-]{3,120}")

def desk_runners(boxes):
    """Runners the desks declared in desks/<desk>/runners.toml on origin/main, so what agents start gets watched.
    Agent-written input: only a validated unit name or process substring is used (shell-quoted in the check);
    no `probe` (that would run agent text with the operator's key), and never `live` mode."""
    from .gitops import git
    out = []
    try:
        git("fetch", "-q", "origin", "main", check=False, timeout=60)
        files = [f for f in git("ls-tree", "-r", "--name-only", "origin/main", "desks/", check=False).splitlines()
                 if f.endswith("/runners.toml")]
        for f in files:
            desk = f.split("/")[1]
            for r in tomllib.loads(git("show", f"origin/main:{f}", check=False) or "").get("runner", []):
                if not isinstance(r, dict) or r.get("box") not in boxes or not UNIT_OK.fullmatch(str(r.get("name", ""))):
                    continue
                unit, proc = str(r.get("unit", "")), str(r.get("proc", ""))
                if not (UNIT_OK.fullmatch(unit) if unit else PROC_OK.fullmatch(proc)):
                    continue
                safe = {"name": f"{desk}/{r['name']}", "box": r["box"], "mode": r.get("mode") if r.get("mode") in ("dry", "tape") else "tape",
                        "until": str(r.get("until", ""))[:25], "decides": f"[{desk} desk] " + str(r.get("decides", ""))[:200]}
                safe["unit" if unit else "proc"] = unit or proc
                try:
                    _until_ts(safe)
                except ValueError:
                    safe["until"] = ""
                out.append(safe)
    except Exception:
        pass
    return out

def _until_ts(r):
    u = r.get("until") or ""
    return datetime.fromisoformat(u.replace("Z", "+00:00")).timestamp() if u else None

def ssh_cmd(box):
    return ["ssh", "-i", os.path.expanduser(box["key"]), "-o", "BatchMode=yes", "-o", "ConnectTimeout=8",
            "-o", "StrictHostKeyChecking=accept-new", "-o", "LogLevel=ERROR", f"{box['user']}@{box['host']}", "bash -s"]

def check_script(runners):
    """Bash for one box. Prints one tagged line per runner: R<TAB>name<TAB>up|down<TAB>etime<TAB>probe."""
    lines = ["export LC_ALL=C", 'echo "H	$(uptime -p)	$(df -h / | awk \'NR==2{print $5}\')"']
    for r in runners:
        n = shlex.quote(r["name"])
        if r.get("unit"):
            u = shlex.quote(r["unit"])
            lines.append(f'if systemctl is-active --quiet {u}; then s=up; '
                         f'e=$(ps -o etime= -p "$(systemctl show -p MainPID --value {u})" 2>/dev/null | tr -d " "); '
                         f'else s=down; e=; fi')
        else:
            p = shlex.quote(r["proc"])
            lines.append(f'pid=$(pgrep -f -- {p} | head -1); if [ -n "$pid" ]; then s=up; '
                         f'e=$(ps -o etime= -p $pid | tr -d " "); else s=down; e=; fi')
        probe = r.get("probe")
        lines.append(f'pr=$( ( {probe} ) 2>&1 | tail -1 | tr "\\t" " " | cut -c1-200)' if probe else "pr=")
        lines.append(f'printf "R\\t%s\\t%s\\t%s\\t%s\\n" {n} "$s" "$e" "$pr"')
    return "\n".join(lines) + "\n"

def check_box(box, runners, timeout):
    try:
        p = subprocess.run(ssh_cmd(box), input=check_script(runners), capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"reachable": False, "error": "ssh timeout"}, {}
    out = {"reachable": p.returncode == 0 or p.stdout.startswith("H"), "error": p.stderr.strip()[-300:] if p.returncode else ""}
    res = {}
    for line in p.stdout.splitlines():
        f = line.split("\t")
        if f[0] == "H" and len(f) >= 3:
            out["uptime"], out["disk"] = f[1], f[2]
        elif f[0] == "R" and len(f) >= 5:
            res[f[1]] = {"up": f[2] == "up", "etime": f[3], "probe": f[4]}
    return out, res

def status_of(r, res, now):
    """running | finished | DOWN | unknown"""
    if res is None:
        return "unknown"
    if res["up"]:
        return "running"
    u = _until_ts(r)
    return "finished" if u is not None and now >= u else "DOWN"

def refresh(c=None, ops=None, now=None):
    """Check every box, write fleet.md/json, emit alert.fleet on problems. Returns the snapshot dict."""
    if ops is None:
        ops = load()
        ops["runner"] = ops.get("runner", []) + desk_runners({b["name"] for b in ops.get("box", [])})
    now = now or time.time()
    timeout = ops.get("fleet", {}).get("ssh_timeout_s", 20)
    boxes, snap = ops.get("box", []), {"ts": now, "boxes": [], "runners": [], "bets": ops.get("bet", [])}
    for b in boxes:
        rs = [r for r in ops.get("runner", []) if r.get("box") == b["name"]]
        info, res = check_box(b, rs, timeout)
        snap["boxes"].append({**{k: b.get(k) for k in ("name", "host", "where", "role")}, **info})
        for r in rs:
            got = res.get(r["name"]) if info["reachable"] else None
            snap["runners"].append({**r, "status": status_of(r, got, now), **(got or {})})
    STATE.mkdir(parents=True, exist_ok=True)
    FLEET_JSON.write_text(json.dumps(snap, indent=1))
    FLEET_MD.write_text(render(snap, ops))
    if c is not None:
        problems = [f"box {b['name']} unreachable" for b in snap["boxes"] if not b["reachable"]]
        problems += [f"{r['name']} on {r['box']} is DOWN ({r['mode']})" for r in snap["runners"] if r["status"] == "DOWN"]
        prev = c.execute("SELECT data FROM events WHERE kind IN ('alert.fleet','fleet.ok') ORDER BY id DESC LIMIT 1").fetchone()
        prev = json.loads(prev["data"]).get("problems") if prev else None
        if problems and problems != prev:
            event(c, "fleet", "alert.fleet", None, problems=problems, msg="; ".join(problems))
        elif not problems and prev:
            event(c, "fleet", "fleet.ok", None, problems=[], msg="all runners healthy")
    return snap

def render(snap, ops):
    stamp = datetime.fromtimestamp(snap["ts"], timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L = [f"# Fleet (checked {stamp})", "",
         "The harness checks this every 15 min. Desks run the boxes with ./kbssh (deploy, tapes, dry runs);",
         "only the operator arms real money or touches a live runner. Declare runners in desks/<desk>/runners.toml.", ""]
    if snap["bets"]:
        L += ["## Bets (the money path: these come before any new research idea)"]
        for b in snap["bets"]:
            overdue = b.get("decide_by") and b["decide_by"] < datetime.now(timezone.utc).strftime("%Y-%m-%d")
            L.append(f"- **{b['name']}** [{b.get('status')}] decide by {b.get('decide_by') or 'UNSET'}"
                     + (" **OVERDUE: decide now**" if overdue else "")
                     + f"\n  evidence: {b.get('evidence', '')}\n  kill rule: {b.get('kill_rule') or 'UNSET'}"
                     + (f"\n  next: {b['next']}" if b.get("next") else ""))
        L.append("")
    L += ["## Runners", "| runner | box | mode | status | up for | until | answers | last line |", "|---|---|---|---|---|---|---|---|"]
    for r in snap["runners"]:
        st = r["status"] if r["status"] != "DOWN" else "**DOWN**"
        L.append(f"| {r['name']} | {r['box']} | {r['mode']} | {st} | {r.get('etime') or ''} | {r.get('until') or 'always'} "
                 f"| {r.get('decides', '')} | {(r.get('probe') or '').replace('|', '/')} |")
    L += ["", "## Boxes"]
    by = {b["name"]: b for b in ops.get("box", [])}
    for b in snap["boxes"]:
        cfg = by.get(b["name"], {})
        health = f"{b.get('uptime', '?')}, disk {b.get('disk', '?')}" if b["reachable"] else f"UNREACHABLE: {b.get('error')}"
        L += [f"### {b['name']} ({health})", f"- where: {cfg.get('where', '')}", f"- role: {cfg.get('role', '')}",
              f"- ssh: `ssh -i {cfg.get('key')} {cfg.get('user')}@{cfg.get('host')}`",
              f"- repo: {cfg.get('repo', '')}", f"- notes: {cfg.get('notes', '')}", ""]
    return "\n".join(L)

def cached_md():
    return FLEET_MD.read_text() if FLEET_MD.is_file() else ""

def maybe_refresh(c, ops_interval=None):
    """Called from the runner loop thread; cheap no-op until the interval elapses."""
    ops = load()
    if not ops:
        return None
    iv = ops_interval or ops.get("fleet", {}).get("interval_s", 900)
    if FLEET_JSON.is_file() and time.time() - FLEET_JSON.stat().st_mtime < iv:
        return None
    return refresh(c, ops)
