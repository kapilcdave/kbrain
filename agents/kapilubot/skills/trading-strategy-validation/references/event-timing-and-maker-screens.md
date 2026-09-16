# Scheduled-Event Timing Tests and Maker-Side Screens

Method for two related questions that recur whenever a market has a **scheduled
data release** (model runs, economic prints, index rebalances, settlement feeds):

1. Do quotes actually reprice around the release?
2. If so, can either side of the book harvest it?

Both were run end-to-end on a real case. The effect was overwhelming (z=+7.56,
p~2e-14) and **both sides still lost money**. The screens below are what turned a
reported "+0.735c/fill PROFITABLE" into a measured -1.347c/fill.

## Part 1 — Testing the timing claim retrospectively

### Use minute-bar history, not a live feed

Waiting live buys a handful of release events per day. If the venue exposes
minute-level quote history on settled markets, the same hypothesis is testable
over months in minutes of wall time — one run yielded **82,933 consecutive-minute
pairs across 112 markets**. Always check for a candlestick/OHLC endpoint before
building a live collector.

Live collection is still required for anything about **queue position or fill
sequencing**; history cannot price those. Split the question and run the archival
work first.

### Quote hygiene (both of these manufacture fake effects)

- **Two-sided sane quotes only**: `ask > bid`, `0 < bid`, `ask < 1`. A 0/1 quote
  is an empty book, not a price; counting it produces a huge fake "move" the
  moment a market wakes up.
- **Strictly consecutive periods only** (`ts diff == period`). A gap means the
  book was empty in between, so the change is not attributable to one period.

### Build the null from the data's own structure

The naive null — "movement is uniform across the hour" — is wrong, because each
market has its own activity profile by hour-of-day that will either fake or mask
the effect.

Use **within-block exchangeability**: inside one market-hour, which minute a
given `|d mid|` landed on is uninformative under the null. Shuffling within the
block preserves that block's total activity and its minute set while destroying
position-in-hour structure.

### Closed-form permutation moments

Brute-force shuffling over thousands of blocks does not finish in pure Python.
The moments are exact — each block is a sum over a simple random sample without
replacement from its own values:

```
per block:  E[T_i]   = k * mean_i
            Var[T_i] = k * (n - k) / (n - 1) * popvar_i
blocks independent -> moments add; CLT gives the p-value
```

Blocks where `k == 0` or `k == n` carry no within-block contrast and contribute
zero variance — skip them rather than letting them inflate the block count.

**Validate the closed form against ~1500 real shuffles before trusting it.**
Agreement in one run was 0.03% on the mean and 1% on the sd. An unvalidated
analytic shortcut is exactly the kind of thing that silently produces a wrong z.

### Report every window you tried

Window edges are rarely preregistered. The same effect read **1.012 (n.s.)** or
**1.177 (p=9e-10)** depending on the window. Report all candidates with a
Bonferroni-adjusted threshold; the *pattern across windows* is what localises the
effect, and a result appearing at only one hand-picked window is not a finding.

A window that FAILS can be the most informative: one covering the release but
missing the following minutes was non-significant, which is what showed the
reprice was **late** rather than anticipatory.

### Rate limits

Sustained history polling gets 429s. Sleep ~1.2s between calls with backoff, and
**cache the fetch separately from the inference** so the statistics can be re-run
without re-hammering the venue. Cache *every field you might need* — a mid-only
cache had to be refetched in full to test spread and volume.

## Part 2 — The three screens that kill a false maker edge

A release window that widens spreads looks like a maker opportunity. Each screen
below independently flipped or erased the result.

### Screen 1: unsigned movement is not edge

`|d mid|` says the quote *moves*, not that the direction is predictable. Test
signed continuation: for each move, the signed forward return at t+1/3/5/10,
against non-window periods as a **control**.

In the real case, continuation was **negative at 4/4 horizons and statistically
indistinguishable from control** (p=0.30-0.87) — quote flicker around the
release, not sustained repricing. A taker paying a 6c hurdle to chase a reverting
0.2c move loses ~6c/contract.

### Screen 2: unconditional drift flatters a maker

A maker does not experience the average period. A maker experiences **the periods
in which someone chose to cross**, and that flow is informed.

Split exposure by whether a trade actually occurred:

| horizon | drift after trade | after no trade | ratio |
|---|---|---|---|
| t+1 | 1.373c | 0.679c | 2.02x |
| t+3 | 2.552c | 1.196c | 2.13x |
| t+5 | 3.291c | 1.536c | 2.14x |

All p~0. And signed continuation after traded periods was positive and **growing
with horizon** (+0.007c → +0.079c → +0.172c, p<1e-8) — the signature of
progressive pick-off, not mean reversion back to the maker.

Using unconditional drift understates exposure by ~2x, which is exactly the
quantity that kills market makers.

### Screen 3: a markout is not realised P&L

`half_spread - drift` is the standard markout convention: it **values the
position** at t+h. It does not include getting out. To realise it the maker must
cross back and pay the other half-spread, or rest the exit with no guaranteed
fill (and the unfilled case is exactly the adverse one).

Charging the exit column:

| horizon | earn | drift | exit | realised |
|---|---|---|---|---|
| t+1 | 2.166c | 1.503c | 2.010c | **-1.347c** |
| t+3 | 2.103c | 2.746c | 1.868c | -2.511c |

**The sign flip comes entirely from the column the markout omits.** Always price
the round trip.

The apparent escape — hold to settlement, pay no exit spread — is worse, not
better: that means holding an informed counterparty's wrong side to resolution,
and it requires being right about the OUTCOME rather than about the next 60
seconds.

### Also: decompose baseline vs event-specific

Even a surviving edge must be split into "what exists in ordinary periods" vs
"what the event adds". In the real case **88% of the gross maker edge existed in
ordinary minutes**; the event-specific increment was 12%. An effect can be
statistically overwhelming and still contribute almost nothing over the generic
strategy — in which case the event thesis is not the thing to build on.

### And: confirm the mechanism before building on it

"Makers widen around the release" was asserted one stage before it was measured
(it turned out true: +13.1%, t=+9.20, p=3e-20). That was luck, not method. An
unverified mechanism is a guess, and the next stage's design depends on it.

## What a positive result would have licensed

If the round trip had cleared costs, the next instrument is a **live markout
probe on real fills** — minute bars cannot see queue position and will flatter
any resting strategy. Never go from a bar-level screen straight to size.
