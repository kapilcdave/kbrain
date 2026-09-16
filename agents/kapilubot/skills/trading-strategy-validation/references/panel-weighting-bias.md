# The row-vs-entity weighting artifact

The control that killed a finding which had already passed a preregistered
time-holdout AND an independent-factor split. Run it on every panel-derived edge.

## The setup

A panel with one row per **entity-minute** (market-minute, symbol-bar, patient-day).
You compute a win rate over rows and an interval over clusters, which sounds
careful, and is still wrong.

## The mechanism

An entity contributes one row per period it spends inside the qualifying region.
So row weighting weights each entity by **how long it lingered in the region** —
and lingering is not independent of the outcome.

Worked example (Kalshi 15-minute markets, favourite priced 0.88-0.955, 300-600s
to close):

```
5,465 rows / 2,715 markets

weighting              q       mid     EV@mid
row  (minutes)      0.9413   0.9210    +2.02c
market (tradeable)  0.9293   0.9195    +0.98c   95% lower bound: -0.05c

eventual WINNERS  mean 2.04 minutes in band
eventual LOSERS   mean 1.67 minutes in band
                  winners loiter 1.22x longer
```

Corrected, the edge fell **2.07x** and its lower bound crossed zero. The finding
was dead — after passing both holdout splits.

## Why no feature audit catches it

This is look-ahead **in the weights**, not in the features. Every feature is
observed strictly before the outcome. Nothing leaks into a column. The bias is
entirely in how many times each entity is counted, so leakage checks, causal
timing reviews, and feature-timestamp audits all pass clean.

## The rule

**You enter each entity once, so weight each entity once.** If the tradeable act
is one decision per entity, the estimator must be one observation per entity —
usually the entity's mean price/feature across its qualifying rows, paired with
its single outcome.

Row-weighted numbers are not a conservative approximation. They are biased in the
direction that makes you deploy capital.

## Diagnostic

Compare mean rows-in-region for winners vs losers. Ratio > ~1.05 means row
weighting is over-sampling winners and every row-weighted EV in that codebase is
inflated. Report the ratio; it quantifies the damage.

`scripts/entity_weighting_check.py` runs both estimators plus the loiter ratio.

## Direction of the bias is not universal

In the same session, one cell showed the *opposite* sign (losers lingered
longer, so row weighting understated the edge). The point is not "row weighting
inflates" — it is **"row weighting measures something other than the trade."**
Always compute both and report the entity-weighted one.
