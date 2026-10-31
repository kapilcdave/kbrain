"""Shared, tested statistics for backtests. Agents import this instead of reinventing it.

    from kbstats import evaluate          # copied into backtester/skeptic working dirs
    metrics = evaluate({"2026-10-01": 1.2, "2026-10-02": -0.4, ...})   # unit -> net PnL after ALL costs
"""
import random, statistics

def cluster_bootstrap(values, n_boot=2000, alpha=0.05, seed=7):
    """Bootstrap the mean over independent units (days/events/settlement windows), not raw trades."""
    vals = list(values.values()) if isinstance(values, dict) else list(values)
    if len(vals) < 2:
        raise ValueError("need at least 2 independent units")
    rng = random.Random(seed)
    means = sorted(statistics.fmean(rng.choices(vals, k=len(vals))) for _ in range(n_boot))
    return statistics.fmean(vals), means[int(alpha / 2 * n_boot)], means[int((1 - alpha / 2) * n_boot) - 1]

def evaluate(unit_pnl, top_frac=0.05, **kw):
    """Returns exactly the metrics dict the harness grades deterministically."""
    vals = list(unit_pnl.values()) if isinstance(unit_pnl, dict) else list(unit_pnl)
    mean, lo, hi = cluster_bootstrap(vals, **kw)
    k = max(1, int(len(vals) * top_frac))
    trimmed = sorted(vals)[:-k]
    return {"net_mean": mean, "ci_low": lo, "ci_high": hi, "n_units": len(vals),
            "net_mean_ex_top": statistics.fmean(trimmed) if trimmed else 0.0}
