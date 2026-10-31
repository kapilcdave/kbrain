import argparse, json, sys, time
from datetime import datetime
from .db import STATE, connect, add_task
from . import runner

def main(argv=None):
    ap = argparse.ArgumentParser(prog="kb")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("role"); a.add_argument("title")
    a.add_argument("--spec", default="{}"); a.add_argument("--hypothesis")
    sub.add_parser("status"); sub.add_parser("stats"); t = sub.add_parser("tail"); t.add_argument("-n", type=int, default=30)
    t.add_argument("-f", action="store_true")
    sub.add_parser("serve"); sub.add_parser("once")
    sub.add_parser("stop"); sub.add_parser("resume")
    g = sub.add_parser("gate"); g.add_argument("prereg")
    args = ap.parse_args(argv)

    if args.cmd == "stop":
        STATE.mkdir(parents=True, exist_ok=True); runner.STOP.touch(); print("STOP set"); return
    if args.cmd == "resume":
        runner.STOP.unlink(missing_ok=True); print("STOP cleared"); return
    if args.cmd == "gate":
        from .gates import prereg_missing
        m = prereg_missing(args.prereg); print("OK" if not m else f"missing: {', '.join(m)}"); sys.exit(bool(m))
    if args.cmd == "serve": return runner.serve()
    c = connect()
    if args.cmd == "add":
        spec = json.load(open(args.spec[1:])) if args.spec.startswith("@") else json.loads(args.spec)
        print(add_task(c, args.role, args.title, spec, hypothesis=args.hypothesis))
    elif args.cmd == "once":
        print(runner.tick(c, runner.load_config()))
    elif args.cmd == "status":
        for r in c.execute("SELECT status, COUNT(*) n FROM tasks GROUP BY status"): print(f"{r['status']:8} {r['n']}")
        print("STOP flag:", runner.STOP.exists(), "| mem avail MB:", runner.mem_available_mb())
        for r in c.execute("SELECT id,role,status,attempts,title FROM tasks WHERE status IN ('running','queued','blocked','failed') ORDER BY id LIMIT 15"):
            print(f"#{r['id']:<4}{r['role']:<11}{r['status']:<8}try={r['attempts']} {r['title'][:60]}")
    elif args.cmd == "stats":
        print(f"{'model':42}{'runs':>5}{'ok%':>6}{'avg_s':>7}")
        for r in c.execute("SELECT model, COUNT(*) n, 100.0*SUM(outcome='ok')/COUNT(*) ok, AVG(ended-started) s FROM runs WHERE ended IS NOT NULL GROUP BY model ORDER BY n DESC"):
            print(f"{r['model'][:41]:42}{r['n']:>5}{r['ok']:>6.0f}{r['s'] or 0:>7.0f}")
    elif args.cmd == "tail":
        last = 0
        while True:
            rows = c.execute("SELECT * FROM (SELECT * FROM events WHERE id>? ORDER BY id DESC LIMIT ?) ORDER BY id", (last, args.n)).fetchall()
            for r in rows:
                last = r["id"]
                print(datetime.fromtimestamp(r["ts"]).strftime("%H:%M:%S"), r["actor"], r["kind"], r["task_id"] or "", r["data"][:140])
            if not args.f: break
            args.n = 1000; time.sleep(2)

if __name__ == "__main__":
    main()
