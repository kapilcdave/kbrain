# Clustering: find the real unit of independence, then re-apply it everywhere

Getting the interval right is not one decision. It is a **hierarchy**, and each
level up shrinks the effective sample. Most sessions fix one level, declare
victory, and leave a wrong number standing somewhere else.

```
rows / entity-minutes        <- almost always wrong
  entity (market, side)      <- the usual "fixed" answer; often still wrong
    settlement boundary      <- the real unit when instruments co-expire
      day / regime           <- when boundaries share a driver
```

## The level that gets missed: co-expiring settlement boundaries

One session clustered correctly by `(ticker, side)` — one entry per market, one
outcome per market — and the finding passed a preregistered time+factor holdout
at **+2.46c [+0.81, +3.82]**.

Then a live check showed **every instrument closed on the same boundary**: all 9
series simultaneously reported `t_remaining = 43s`. They settle off correlated
underlyings at one instant. Legs taken in one window are therefore not
independent draws, no matter how distinct their tickers are.

Measured in the forward sample: **6 of 7 windows had every leg resolve
identically.**

**Detection is cheap — measure agreement, do not assume it:**

```python
by_window = defaultdict(list)
for entity in entities:
    by_window[entity.close_ts].append(entity.won)

multi  = {c: L for c, L in by_window.items() if len(L) > 1}
agree  = sum(1 for L in multi.values() if len(set(L)) == 1)
baseline = max(q, 1 - q)      # agreement expected if independent
# agree/len(multi) >> baseline  ->  correlated, cluster on the window
```

Compare the observed agreement rate against `max(q, 1-q)`. At a 92% win rate,
two independent legs already agree ~92% of the time — so a raw agreement rate
near that is *not* evidence of correlation. Only the excess is.

## The design effect depends on legs-per-window — measure it, both ways

The severity is not a constant, and intuition gets it wrong in both directions:

| sample | legs/window | agreement | interval widening |
|---|---|---|---|
| live, 9 series polled | 3.57 | 6/7 windows | severe |
| historical panel, 3 series | 1.11 | 87.3% vs 92.6% baseline | **1.09x only** |

The historical panel had *fewer* instruments, so it accidentally avoided most of
the correlation — legs/window was barely above 1. The widening was only 1.09x
(3.02pp → 3.30pp).

**But 1.09x was still enough to change the verdict:**

```
legs (as published)   n=1162   EV +2.46c   95% lower  +0.81c   SURVIVES
windows (corrected)   n=1051   EV +2.46c   95% lower  -0.04c   DOES NOT CLEAR
```

A mild design effect is not a safe one. Compute it; never eyeball it.

Note the point estimate is **unchanged** — only the interval moves. Cluster the
interval, keep the point estimate over legs (legs are what actually get traded).

## EXCEPTION: when cluster SIZE correlates with cluster OUTCOME

"Keep the point estimate over legs" holds only while the number of legs in a
cluster is independent of that cluster's outcome. When it is not, the leg-weighted
point estimate is **biased**, and it can flip sign.

A later session hit exactly this on the same data:

```
same 132 legs / 52 windows
  leg-weighted mean EV    +0.98c
  window-weighted mean EV -0.65c      <- opposite sign
```

Mechanism, measured directly:

```
windows where all legs won :  41 windows,  98 legs -> 2.39 legs/window
mixed                      :   8 windows,  31 legs -> 3.88 legs/window
windows where all legs lost:   3 windows,   3 legs -> 1.00 legs/window
```

**Losing windows were thinner.** A window that gaps away offers only one
qualifying leg before the price leaves the region; a calm window offers several.
So leg-weighting silently over-samples the winners — the same class of
look-ahead-in-the-weights as the loiter bias, one level up the hierarchy.

Diagnostic (run it whenever legs/window > 1):

```python
clean  = [w for w in windows if all(w.outcomes)]
allbad = [w for w in windows if not any(w.outcomes)]
n_win  = mean(len(w.legs) for w in clean)
n_lose = mean(len(w.legs) for w in allbad)
# n_lose < n_win  ->  leg-weighting reads HIGH; report the window number
```

Rule: **if leg- and window-weighting disagree in sign or materially in size, the
window number is the honest one** and the leg number must not be reported alone.
When they agree, keep the leg estimate as before.

## Report the distribution, not just the estimate

The same sample showed why a point estimate is a poor summary of this payoff:

```
median window EV  +9.85c
mean   window EV  -0.65c
worst three       -90.85c, -88.50c, -88.50c
```

Most windows win a little; a few lose nearly the whole basis. **The mean is
carried entirely by a tail the sample cannot price.** This is the mechanical
explanation for the recurring puzzle where a 90%+ win rate settles at ~$0 of
realised P&L: the wins are capped at `1-p` and the losses are ~`p`.

Always report median alongside mean, plus the worst few clusters. A median
comfortably positive against a negative mean is not a contradiction — it is the
shape of the trade, and it says the tail, not the win rate, is the strategy.


## Retro-apply every estimator fix to ALL prior claims

This is the process rule, and it is the one worth internalising.

When a clustering/weighting/accounting bug is found in *one* artifact, it is
almost never confined to it. The same session:

1. found the boundary-clustering bug in the **forward scorer**, fixed it there,
   and moved the forward lower bound from −9.29c to −25.18c;
2. **left the historical claim uncorrected**, because that is where the bug was
   noticed, not where it was born;
3. only revisited it when the user pushed — and the historical headline finding
   then failed to clear zero.

Inconsistent application is worse than not finding the bug at all: it produces a
report where one number is honest and another is not, with no marker saying
which. On finding any estimator defect, **grep the session for every claim built
on the same estimator and re-run them all** before reporting.

## Prefer archival evidence for "does the edge exist"

Forward collection is expensive in wall-clock time and buys precision slowly.
Before starting one, price both options:

```
forward runner:  ~4 independent windows/hour  -> ~50 overnight
existing panel:  3,276 windows already on disk
full backfill:   96 boundaries/day x 180 days = ~17,000 windows
```

History answers **"is the edge real"** thousands of times faster. Reserve forward
runs for the terms history genuinely cannot price — queue position, fill
benignity, adverse selection — and run them in the background *while* the
archival work proceeds, not instead of it.

When a user asks "can't you just use the historical data", that is usually
correct and worth acting on immediately. Answer with the two questions split:
which term history can settle, and which single term it cannot.

## Sample-size sanity, stated up front

Report effective sample size, not raw count, and say what it cannot resolve:

> 25 legs is really 7 windows. The interval is 35pp wide. A 96% win rate on 7
> correlated draws is what you would see whether the edge is real or zero.

A high win rate on a handful of correlated draws is the single most common way a
zero-edge strategy looks validated.
