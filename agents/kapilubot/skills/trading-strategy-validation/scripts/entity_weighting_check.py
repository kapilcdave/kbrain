#!/usr/bin/env python3
"""Row-weighted vs entity-weighted edge, plus the loiter-ratio diagnostic.

Generic control for the artifact in references/panel-weighting-bias.md. Run it on
ANY panel-derived edge before reporting: a finding can pass a time holdout and an
independent-factor split and still die here.

Input: JSONL, one row per entity-period, with (at minimum) an entity id, a price
or prediction, and a binary outcome. Column names are flags.

    python entity_weighting_check.py panel.jsonl \\
        --entity ticker --price mid --outcome won

    # optional region filter, e.g. only rows inside the qualifying band
    python entity_weighting_check.py panel.jsonl \\
        --entity ticker --price mid --outcome won \\
        --filter-col seconds_left --filter-lo 420 --filter-hi 600

Reports both estimators, the Wilson lower bound on the entity-weighted one, and
the winner/loser loiter ratio that explains any gap.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(max(p * (1 - p) / n + z * z / (4 * n * n), 0.0))
    return ((c - h) / d, (c + h) / d)


def truthy(v) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v > 0
    return str(v).strip().lower() in {"true", "yes", "y", "1", "win", "won"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("panel")
    ap.add_argument("--entity", required=True, help="column identifying one tradeable decision")
    ap.add_argument("--price", required=True, help="cost basis / predicted probability column")
    ap.add_argument("--outcome", required=True, help="binary outcome column")
    ap.add_argument("--filter-col")
    ap.add_argument("--filter-lo", type=float)
    ap.add_argument("--filter-hi", type=float)
    ap.add_argument("--price-lo", type=float)
    ap.add_argument("--price-hi", type=float)
    a = ap.parse_args()

    ent: dict[str, dict] = defaultdict(lambda: {"px": [], "won": None})
    n_rows = row_wins = 0
    row_px = 0.0

    with open(a.panel) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if a.entity not in r or a.price not in r or a.outcome not in r:
                continue
            if a.filter_col is not None:
                v = r.get(a.filter_col)
                if v is None:
                    continue
                if a.filter_lo is not None and float(v) < a.filter_lo:
                    continue
                if a.filter_hi is not None and float(v) >= a.filter_hi:
                    continue
            try:
                px = float(r[a.price])
            except (TypeError, ValueError):
                continue
            if a.price_lo is not None and px < a.price_lo:
                continue
            if a.price_hi is not None and px >= a.price_hi:
                continue

            won = truthy(r[a.outcome])
            n_rows += 1
            row_wins += int(won)
            row_px += px
            e = ent[str(r[a.entity])]
            e["px"].append(px)
            e["won"] = won

    n_ent = len(ent)
    if not n_rows or not n_ent:
        print("no rows matched the filters", file=sys.stderr)
        return 1

    q_row = row_wins / n_rows
    px_row = row_px / n_rows

    ent_wins = sum(1 for v in ent.values() if v["won"])
    q_ent = ent_wins / n_ent
    px_ent = statistics.fmean(statistics.fmean(v["px"]) for v in ent.values())
    lo, _hi = wilson(ent_wins, n_ent)

    print(f"rows {n_rows}   entities {n_ent}   "
          f"mean rows/entity {n_rows / n_ent:.2f}\n")
    print(f"{'weighting':<20}{'q':>9}{'price':>9}{'edge':>10}")
    print("-" * 48)
    print(f"{'row (periods)':<20}{q_row:>9.4f}{px_row:>9.4f}{(q_row - px_row) * 100:>9.2f}c")
    print(f"{'entity (tradeable)':<20}{q_ent:>9.4f}{px_ent:>9.4f}{(q_ent - px_ent) * 100:>9.2f}c")
    print(f"\nentity-weighted 95% lower bound: {(lo - px_ent) * 100:+.2f}c")

    ev_row, ev_ent = (q_row - px_row) * 100, (q_ent - px_ent) * 100
    if abs(ev_ent) > 1e-9:
        print(f"row-weighting distortion: {ev_row - ev_ent:+.2f}c "
              f"({ev_row / ev_ent:.2f}x)")

    w = [len(v["px"]) for v in ent.values() if v["won"]]
    l = [len(v["px"]) for v in ent.values() if not v["won"]]
    print("\n=== mechanism: periods-in-region by outcome ===")
    if w and l:
        mw, ml = statistics.fmean(w), statistics.fmean(l)
        print(f"  WINNERS n={len(w):>6} mean={mw:.2f}")
        print(f"  LOSERS  n={len(l):>6} mean={ml:.2f}")
        print(f"  ratio {mw / ml:.2f}x")
        if abs(mw / ml - 1) > 0.05:
            print("  -> row weighting is NOT measuring the trade. Use the")
            print("     entity-weighted figure; treat row-weighted EVs in this")
            print("     codebase as biased.")
        else:
            print("  -> no material loiter asymmetry")
    else:
        print("  need both winners and losers to compute the ratio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
