# Three ways a surviving edge is still wrong: incoherent intervals, composition drift, shrinkage

All three surfaced in one session **after** the finding had already passed a
preregistered time+factor holdout and a clustering correction. Passing the bar is
not the end of the audit.

---

## 1. The incoherent estimator: an interval that does not contain its own point estimate

Standard advice — *"point estimate over legs, interval over clusters"* — is right
about **what to report** but silently produces a broken interval if you compute
the two from different units. Watch what it printed:

```
time: early half   EV = +0.59c   interval [-1.62, +0.62]   <- estimate at the TOP
time: late half    EV = +1.62c   interval [+1.42, +3.31]   <- estimate at the BOTTOM
```

The point estimate is a leg-average; the interval is a Wilson band on a
*window-majority win rate*. Two different estimators. An interval that does not
bracket its own estimator's sampling distribution **is not a confidence
statement** and cannot be reported as one.

**Detection — free, do it every time:**

```python
assert lo <= point <= hi, "estimator incoherence: interval is on a different quantity"
```

If the point estimate sits at or outside an edge of its own interval in more than
one cell, the two are not measuring the same thing.

**Fix — one coherent estimator, via cluster bootstrap.** Make the *cluster* the
unit of observation, reduce within it, then resample clusters:

```python
# 1. reduce each cluster to one number: what trading every qualifying leg
#    in that window would have earned per contract
per_window = [mean(ev_of_leg for leg in window) for window in windows]

# 2. resample WINDOWS with replacement
means = []
for _ in range(4000):
    means.append(mean(random.choice(per_window) for _ in per_window))
means.sort()
lo, hi = means[int(.025*len(means))], means[int(.975*len(means))]
point  = mean(per_window)          # same units as lo/hi, by construction
```

Cluster-robust with no independence assumption about legs inside a window, and
the interval is guaranteed to be on the same quantity as the estimate. Also
report `P(EV>0)` — the share of bootstrap means above zero — which is more
legible than a bound for a marginal edge.

The corrected pooled figure came out **+0.87c [+0.28, +1.44], P(EV>0)=0.998**,
versus the incoherent `+1.18c [+0.22, +1.69]`.

---

## 2. Composition drift: when a backfill turns a time split into an instrument split

**The trap.** A panel is backfilled from 3 instruments to 15. The 12 new ones
only exist for the period the backfill covered, so they land almost entirely in
one chronological half. Split that panel on time and "early vs late" is really
"old instruments vs everything" wearing a clock's costume.

Observed share of legs, early half → late half:

```
KXCRYPTOLEAD15M    0.0%  ->  15.3%    (+15.3)
KXGOLD15M          0.1%  ->   5.3%    ( +5.2)
KXSILVER15M        0.2%  ->   5.1%    ( +4.9)
KXWTI15M           0.1%  ->   4.6%    ( +4.5)
KXBTC15M          11.6%  ->   6.6%    ( -5.0)
```

The uncorrected split read early **+0.31c** / late **+1.43c** and looked like a
regime story. It was a roster change.

**Always print composition per half before interpreting a time split:**

```python
ce, cl = Counter(s for e in early), Counter(s for s in late)
shift = {s: 100*cl[s]/len(late) - 100*ce[s]/len(early) for s in all_series}
# any |shift| > ~5pp  ->  the time split is confounded
```

**Fix — balance the panel, then split.** Keep only entities with real coverage on
both sides of the cut (e.g. >=40 legs each side), and split *those*:

```
balanced subset   12,874 of 15,837 legs, 9 of 15 series
pooled            +0.97c [+0.33, +1.61]
early half        +0.32c [-0.61, +1.24]    <- does NOT clear zero alone
late half         +1.72c [+0.81, +2.59]
```

Positive in both halves once composition is fixed — but weaker than the raw
split suggested, and the early half no longer clears on its own.

**Then go one level stricter: split each instrument on time individually.**
Pooling can hide that the effect only lives in a subset.

```
per-series, each split on time:  6 of 9 positive in BOTH halves
  (3 of 9 flipped sign across the cut)
```

"6/9 hold" is a materially different claim from "positive in both halves", and
it is the honest one. Report the count.

---

## 3. Effect-size shrinkage as a selection diagnostic

Track the point estimate **as a function of sample size**. A cell found by
scanning many cells regresses toward zero as data is added; a mechanism-driven
edge is roughly stable.

```
 1,162 legs (3-series panel)    EV +2.46c
15,837 legs (15-series panel)   EV +0.87c      <- halved on 13.6x the data
```

This cell was selected by scanning ~32 cells, so the shrinkage is exactly what
multiplicity predicts. **Halving is consistent with two readings at once** — a
real-but-smaller edge, and a mostly-selected one — and the data cannot separate
them. Say that rather than picking the flattering branch.

The tie-breaker is not more of the same panel. It is whether the effect holds on
data that was **not part of the original scan**, or a stated mechanism that
predicts it independently.

**Report the trajectory, not just the latest number.** "+2.46c → +0.87c as n grew
13.6x" tells the reader more about reliability than either figure alone, and it
pre-empts the reader who remembers the older, larger number.

---

## Composite checklist for a "surviving" edge

Before reporting survival, confirm all of:

- [ ] interval brackets its own point estimate (same estimator, both quantities)
- [ ] cluster bootstrap agrees with the analytic bound
- [ ] composition per split-half printed; no group shifted >5pp
- [ ] split holds per-instrument, not only pooled — report the `k/n` count
- [ ] effect-size trajectory vs sample size reported
- [ ] fees applied at the actual entry price, taker and maker priced separately
- [ ] the gross edge still exceeds the fee (see below)

**The last one ends more strategies than any statistic.** A `ceil`-to-the-cent
fee is flat across a wide price range, so a shrinking edge can pass under it:

```
gross edge at the mid   +0.87c
taker fee at P=0.90      1.00c
taker net               -0.13c    DEAD, at any bankroll
```

When the fee exceeds the gross edge, the taker path is arithmetically dead and
**the entire strategy reduces to a bet on benign maker fills** — a term no
archive can price at any sample size. State that reduction explicitly; it is the
result, not a footnote.
