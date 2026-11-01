import argparse, json, os, sys, time
from datetime import datetime
from .db import STATE, connect, add_task, event
from . import runner, lifecycle

# Mark: a brush-stroke pixel K. Every stroke tapers: thin at its ends, thick toward the joint.
# Half-block pixels, money green -> blue (in the style of agy's banner).
MARK = [".#.....#", ".#....#.", "##...##.", "##..##..", "####....",
        "####....", "##..##..", "##...##.", ".#....#.", ".#.....#"]   # mirror-symmetric top/bottom
STOPS = [(10, 92, 54), (20, 128, 72), (16, 122, 120), (28, 92, 190), (47, 111, 235)]
COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
TRUECOLOR = os.environ.get("COLORTERM", "") in ("truecolor", "24bit")

def grad(t):
    t = max(0.0, min(1.0, t)) * (len(STOPS) - 1); i = min(int(t), len(STOPS) - 2); f = t - i
    return tuple(round(a + (b - a) * f) for a, b in zip(STOPS[i], STOPS[i + 1]))

def sgr(rgb, bg=False):
    if TRUECOLOR:
        return f"{48 if bg else 38};2;{rgb[0]};{rgb[1]};{rgb[2]}"
    q = lambda v: 0 if v < 48 else 1 if v < 115 else (v - 35) // 40      # nearest xterm-256 cube cell
    return f"{48 if bg else 38};5;{16 + 36 * q(rgb[0]) + 6 * q(rgb[1]) + q(rgb[2])}"

def c(code, s):
    return f"\033[{code}m{s}\033[0m" if COLOR else s

def mark_lines():
    h, w, out = len(MARK), len(MARK[0]), []
    for r in range(0, h, 2):
        line = ""
        for x in range(w):
            top, bot = MARK[r][x] == "#", r + 1 < h and MARK[r + 1][x] == "#"
            ct, cb = grad(x / w * .7 + r / h * .3), grad(x / w * .7 + (r + 1) / h * .3)
            if not COLOR:
                line += "█" if top and bot else "▀" if top else "▄" if bot else " "
            elif top and bot: line += c(f"{sgr(ct)};{sgr(cb, True)}", "▀")
            elif top: line += c(sgr(ct), "▀")
            elif bot: line += c(sgr(cb), "▄")
            else: line += " "
        out.append(line)
    return out

def banner():
    word = "kbrain"
    wm = "".join(c(f"1;{sgr(grad(i / (len(word) - 1)))}", ch) for i, ch in enumerate(word))
    side = ["", wm + c("2", "  research engine"), c("2", "kapil's agents"), "", ""]
    print()
    for m, t in zip(mark_lines(), side):
        print("  " + m + "   " + t)
    print()

GREEN, TEAL, BLUE = sgr((40, 160, 90)), sgr((22, 150, 150)), sgr((70, 130, 240))
STATUS_COLOR = {"queued": "33", "running": f"1;{BLUE}", "done": GREEN, "failed": "31", "blocked": "35",
                "idea": "37", "prereg": TEAL, "backtest": BLUE, "review": "33", "validated": f"1;{GREEN}",
                "rejected": "31", "parked": "2"}

def status(conn, cfg):
    alive = runner.ALIVE.stat().st_mtime if runner.ALIVE.exists() else 0
    age = time.time() - alive if alive else None
    light = (c(GREEN, "● " + runner.ALIVE.read_text()[:60]) if age is not None and age < 45
             else c("31", "○ not running (start: kb serve, or systemctl --user start kb-runner)"))
    stalled, _ = lifecycle.stalled(conn, cfg)
    print(f" runner {light}   STOP {c('31;1','ON') if runner.STOP.exists() else 'off'}   "
          f"mem {runner.mem_available_mb()}MB   runs/24h {runner.runs_last_day(conn)}/{cfg['limits'].get('max_runs_per_day')}"
          + (c("31;1", "   ⚠ STALLED: run `kb ack` after reviewing") if stalled else ""))
    counts = {r["status"]: r["n"] for r in conn.execute("SELECT status, COUNT(*) n FROM tasks GROUP BY status")}
    print(" tasks  " + "  ".join(c(STATUS_COLOR.get(k, "0"), f"{k} {v}") for k, v in counts.items()) or " tasks  none")
    print(c("1", "\n hypotheses"))
    for r in conn.execute("SELECT * FROM hypotheses ORDER BY updated DESC LIMIT 12"):
        print(f"  {c(STATUS_COLOR.get(r['status'],'0'), f'{r['status']:<10}')} {r['slug']:<34} {(r['reason'] or '')[:70]}")
    print(c("1", "\n active"))
    for r in conn.execute("SELECT id,role,status,attempts,title FROM tasks WHERE status IN ('running','queued') ORDER BY status DESC, id LIMIT 10"):
        print(f"  #{r['id']:<5}{c(STATUS_COLOR[r['status']], f'{r['status']:<8}')}{r['role']:<11}{r['title'][:64]}")

def main(argv=None):
    ap = argparse.ArgumentParser(prog="kb", description="kbrain research engine")
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("add", help="queue a task"); a.add_argument("role"); a.add_argument("title")
    a.add_argument("--spec", default="{}"); a.add_argument("--hypothesis")
    sub.add_parser("status"); sub.add_parser("stats"); sub.add_parser("top", help="live status")
    t = sub.add_parser("tail"); t.add_argument("-n", type=int, default=30); t.add_argument("-f", action="store_true")
    w = sub.add_parser("web", help="LARP HQ at http://127.0.0.1:7777"); w.add_argument("--port", type=int, default=7777)
    sub.add_parser("serve"); sub.add_parser("once")
    sub.add_parser("stop"); sub.add_parser("resume"); sub.add_parser("ack", help="acknowledge a stall alert")
    g = sub.add_parser("gate"); g.add_argument("prereg")
    args = ap.parse_args(argv)
    from .router import load_config

    if args.cmd == "stop":
        STATE.mkdir(parents=True, exist_ok=True); runner.STOP.touch(); print("STOP set"); return
    if args.cmd == "resume":
        runner.STOP.unlink(missing_ok=True); print("STOP cleared"); return
    if args.cmd == "gate":
        from .gates import prereg_missing
        m = prereg_missing(args.prereg); print("OK" if not m else f"missing: {', '.join(m)}"); sys.exit(bool(m))
    if args.cmd == "serve": return runner.serve()
    if args.cmd == "web":
        from .web import serve
        banner(); return serve(args.port)
    conn = connect()
    if args.cmd in (None, "status"):
        banner(); status(conn, load_config())
    elif args.cmd == "top":
        try:
            while True:
                print("\033[2J\033[H", end=""); banner(); status(conn, load_config()); time.sleep(2)
        except KeyboardInterrupt:
            pass
    elif args.cmd == "add":
        spec = json.load(open(args.spec[1:])) if args.spec.startswith("@") else json.loads(args.spec)
        print(add_task(conn, args.role, args.title, spec, hypothesis=args.hypothesis))
    elif args.cmd == "ack":
        event(conn, "user:cli", "user.ack"); print("stall acknowledged; chief heartbeats resume")
    elif args.cmd == "once":
        print(runner.tick(conn, load_config()))
    elif args.cmd == "stats":
        print(f"{'model':42}{'runs':>5}{'ok':>5}{'blocked':>8}{'invalid':>8}{'limited':>8}{'avg_s':>7}")
        for r in conn.execute("SELECT model, COUNT(*) n, SUM(outcome='ok') ok, SUM(outcome='blocked') blocked, "
                              "SUM(outcome IN ('invalid','timeout')) invalid, SUM(outcome='rate_limited') limited, "
                              "AVG(ended-started) s FROM runs WHERE ended IS NOT NULL GROUP BY model ORDER BY n DESC"):
            print(f"{r['model'][:41]:42}{r['n']:>5}{r['ok']:>5}{r['blocked']:>8}{r['invalid']:>8}{r['limited']:>8}{r['s'] or 0:>7.0f}")
    elif args.cmd == "tail":
        last = 0
        while True:
            rows = conn.execute("SELECT * FROM (SELECT * FROM events WHERE id>? ORDER BY id DESC LIMIT ?) ORDER BY id", (last, args.n)).fetchall()
            for r in rows:
                last = r["id"]
                print(c("2", datetime.fromtimestamp(r["ts"]).strftime("%H:%M:%S")), c(BLUE, r["actor"]), r["kind"], r["task_id"] or "", r["data"][:140])
            if not args.f: break
            args.n = 1000; time.sleep(2)

if __name__ == "__main__":
    main()
