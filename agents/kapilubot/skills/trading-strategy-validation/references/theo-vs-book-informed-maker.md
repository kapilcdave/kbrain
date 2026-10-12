# Theo-vs-book: becoming the informed maker on digital markets

Context where this applies: a passive maker on Kalshi's 15-minute crypto strike
markets (KXBTC15M, KXETH15M, KXSOL15M, KXXRP15M, KXDOGE15M, KXHYPE15M) was
measured **adversely selected** — a live armed micro-probe filled 94% in empty
books yet won 6.2pp LESS than the unfilled counterfactual. Fills land precisely
when the contract is about to go the other way. The maker premium is not free;
it is compensation paid to whoever knows more. The obvious next question the
user asks is "how do we become the one collecting it?" This file records the
answer and, more importantly, the trap in the answer.

## The mechanism: these contracts have a computable fair value

Each market is a **digital option on a crypto spot price**. "BTC price up in
next 15 mins?" pays YES iff spot >= `floor_strike` at `close_time`
(`strike_type == "greater_or_equal"`, `cap_strike` null). The market object
carries `floor_strike` and `close_time` directly. Risk-neutral fair value:

```
theo = P(S_T >= K) = Phi( (ln(S0/K) - 0.5*sigma_h^2) / sigma_h )
sigma_h = sigma_per_minute * sqrt(minutes_to_close)
```

You get S0 (live spot) and sigma from an **external** source the Kalshi book
cannot see — that is the entire point. Kalshi's book prices the same contract
off order flow; where the two disagree you would be the informed maker. Edge
sign convention as a maker (maker fee is zero on these series — see
kalshi-api-notes):

```
edge_buy  = theo - yes_bid    # rest a YES bid; if filled you own YES at bid
edge_sell = yes_ask - theo    # rest a YES ask (== NO bid); short YES at ask
```

Data plumbing that worked, read-only: Coinbase public endpoints, no auth,
`api.exchange.coinbase.com/products/{P}-USD/ticker` for spot mid (bid/ask),
`.../candles?granularity=60` for a realized-vol estimate
(row = `[time, low, high, open, close, volume]`, newest first). Series->product
map is 1:1 by the crypto symbol. Reuse `Broker(env=..., armed=False)` for the
Kalshi GETs and read the book from `/markets` (the consistent snapshot), NOT
`/orderbook` (measured disagreeing with the venue's own touch).

## THE TRAP: a "theo-vs-book edge" is usually a VOL disagreement, not staleness

The first live run flagged +15c edges on ETH and DOGE. **A 15c disagreement on
a liquid book is a bug signal, not a discovery** (the same sanity gate as a
backtest printing a big profit on a marginal strategy). The cause was the
volatility input, not the book being slow:

- A trailing 30x1-minute realized-vol estimate collapses when the last half
  hour is quiet. Low sigma shoves every theo toward 0 or 1, manufacturing edge.
- Back out the vol the BOOK implies instead (solve for sigma that makes
  theo == book mid). In that session the book priced **~1.5-1.7x more vol**
  than the backward window saw (ETH book implied ~0.087%/15min vs 0.05%
  realized; BTC ~0.070% vs 0.05%).
- So the "edge" was not "we are faster than the book relative to spot." It was
  "our realized-vol number disagrees with the book's implied-vol number."
  Betting it is a **volatility bet** — you are short vol when theo is more
  confident than the book, long vol when less — a far humbler and riskier claim
  than a latency edge, and one the user did not know they were taking.

### Rule: never report a theo-vs-book edge as a cent number alone

Always show it as **realized sigma vs book-implied sigma** on the same row. An
edge inside ~2c is vol-estimate noise and must not be flagged (set the flag
margin accordingly). The only question worth answering is: **is there any
horizon or regime where your realized vol repeatably beats the book's implied
vol?** If yes, that is a real edge. If no, there is nothing here and the tool
just saved the user from arming into an unhedged vol short. Treat this exactly
like step 4's spread-decomposition: name the unverified assumption as a number
before believing the headline.

## Other caveats to carry in the tool's own output

- Coinbase spot != Kalshi's settlement source. A persistent per-series offset
  is a data problem (basis / settlement-feed difference), not an edge.
- sigma is realized, backward-looking, 1-minute-sampled; a 15-min horizon has
  only ~15 candles of signal and vol clusters, so it is biased low right before
  a jump — exactly when you would most want it high.
- Clock skew (~150ms local-vs-venue, documented in market_feed) is negligible
  at a 15-min horizon but not in the final seconds; guard with a --min-seconds
  floor so the pricer never trusts the tail.

## Implementing the implied-vol backout (the reframe that matters)

Invert `theo_yes` numerically — **bisection, not a closed form** — because the
0.5*sigma_h^2 Ito term makes theo non-monotone in sigma near ATM, so a naive
solver returns fake roots. What worked:

- Bracket per-minute sigma in `[1e-6, 0.05]` (~0.06% .. ~300% annualized).
- Before iterating, check the target price is actually bracketed:
  `(f_lo - price)*(f_hi - price) <= 0`; if not, **return None** rather than a
  root. This correctly rejects two corner cases that would otherwise fabricate a
  number: a locked `price in {0,1}` book (no vol information) and an exactly-ATM
  `price == 0.5` (only reachable as sigma->0, so no positive-vol root exists).
- Verify by round-trip: pick sigma, price it with `theo_yes`, back it out —
  recovered sigma matched to ~1e-18 in this session.

Then report every row as `volR` (realized) vs `volI` (implied) with their ratio,
and label the flagged signal's mechanism: recompute theo **at the book's own
implied vol** and see if the edge survives. If it evaporates (it will, because
theo-at-implied == book mid by construction), the edge was *entirely* the vol
gap = `VOL`; only genuine spot/moneyness mispricing survives = `SPOT`. In this
session's live tape the ratio scattered **both above and below 1.0 across the six
names in one snapshot** (BTC x0.48, XRP x0.68, ETH x0.75 vs DOGE x2.39, HYPE
x1.17) — the signature of estimator noise, not a directional edge.

## Scoring it: the calibration acid test kills the idea first

Build the scorer (`research_adhoc/score_theo_edge.py`) to run three tests in
kill-order, and encode the arm/don't-arm verdict in the output:

1. **CALIBRATION ACID TEST (runs first, can end it).** Pull each market's settled
   `result` from the venue (`/markets/{ticker}` -> `market.result` in
   {yes,no}), take **one representative row per market** (the flagged snapshot
   nearest a fixed decision horizon — NOT the last row, which leans on near-close
   snapshots where theo trivially -> 0/1, and NOT the max-edge row, which
   cherry-picks the estimator's luckiest moment), and compare `Brier(theo)` vs
   `Brier(book_mid)` against the binary outcome. **If theo's Brier is not lower
   than the book's, the spot model carries no information the book lacks — every
   flagged edge is noise or a vol short, do not arm.** This is the direct test of
   "is our number better than the book's", and it is cheaper and more decisive
   than any PnL reconstruction.
2. **Vol gap directional or noise?** Per-series distribution of realized/implied;
   `frac>1` near 0% or 100% is directional (real), near 50% is random
   disagreement (the null).
3. **Flagged-trade maker PnL at settlement**, market-blocked bootstrap (one PnL
   per market, resample whole markets — the standing anti-pooling rule), split by
   the SPOT/VOL `vol_kind` label.

Verdict rule wired into the script: **arm nothing unless BOTH** theo beats the
book on Brier AND flagged PnL's blocked CI excludes zero above it. Test 2 only
explains *why*; it never on its own justifies a trade. A "no edge" verdict here
is a real, cheap result — it kills a plausible idea before it costs anything.

## Backtesting theo at scale on settled history — and its fill-model trap

Once the forward tool exists, the user is right to say "stop wasting time, use
the historical API." Both venues cooperate: the **Kalshi candlestick endpoint**
(`/series/{s}/markets/{ticker}/candlesticks?start_ts&end_ts&period_interval=1`)
carries per-minute `yes_bid.close`, `yes_ask.close`, and the minute's TRADED
range `price.low`/`price.high`, plus the market object's settled `result`;
**Coinbase historical candles** reconstruct spot at the same minutes. Page
Coinbase in **<=300-candle spans** (`?granularity=60&start=&end=`, the response
caps at 300 rows) and cache per (product, minute); one 14-day pass over six
series rebuilt **92,782 minutes across 7,959 markets** unattended. Reuse the
repo's proven `measure_wing_capacity` helpers (`get`, `fdollar`, `fp`,
`settled_markets`) and the same `theo_yes`/`implied_sigma_min` so history and
forward share identical math. This answers "does the edge exist" ~1000x faster
than forward logging (see the archive-before-forward rule in the main skill).

**The calibration result held up at scale and is the durable finding:** theo
BEAT the book on Brier (0.107 vs 0.118 over 7,959 markets, base rate ~0.50). The
spot model genuinely carries information the Kalshi book prices slowly. Test 2
also resolved: vol ratios sat dead on 1.0 (44-52% frac>1) across all six series,
confirming the one-quiet-hour "vol edge" was pure small-sample noise.

### THE TRAP: a candle-range fill gate manufactures universal positive PnL

The backtest's fill model gates a resting order as filled when the minute's
traded range reached your price (`price.low <= your bid` for a rested YES bid;
`price.high >= your ask` for a rested YES ask). This looks like realism — it
requires an actual trade at your price rather than assuming a fill — but at
**1-minute resolution the traded range almost always straddles the inside**, so
it credits ~95-100% fills and, fatally, it credits them without adverse
selection. The tell is unmistakable and worth burning into memory:

> **Positive mean PnL at EVERY price-basis bucket from 0.0 to 1.0 is the
> signature of a fill-model artifact, not an edge.** No passive maker makes
> money at every moneyness simultaneously; if it did the market would not exist.

One session's diagnostic (bucket the filled trades by cost basis, print mean
PnL + win rate per bucket) showed +1.47c at 0.0 rising to +16.45c mid-book and
tapering to +2.80c at 1.0 — smoothly positive across the whole range. That is
the backtest crediting itself the fills that worked out, exactly the
self-credited-spread failure (step 4) one level deeper: the coarse candle cannot
see **queue position or intra-bar sequencing**, so it cannot reproduce the
-6.2pp adverse selection the live probe measured. Whenever a fill-gated backtest
prints edge everywhere, run the per-bucket cut before believing any aggregate
CI — the aggregate will look great (one run: +8.78c, CI [+8.44, +9.14]) and be
an artifact.

**Conclusion the scale-up forces:** the two questions separate cleanly. theo
predicting settlement better than the book is REAL (robust over ~8k markets).
Capturing it as a passive maker is NOT demonstrated — the only backtest cheap
enough to run at scale has a fill model too coarse to charge the adverse tax, so
it overstates capture. History settles "does the signal exist"; it cannot settle
"do we get the fill benignly." That term still needs live fills.

## The theo-conditioned live micro-probe — the only instrument that pays the tax

The honest resolution is not more backtesting (coarse candles keep overstating
fills) but pointing the **real-money** micro-probe framework at theo signals.
Extend the existing armed queue probe rather than fork it:

- Add a `--theo-trigger` / `--theo-margin` gate that prices every scan candidate
  off spot (`annotate_theo`) and arms **only** when the favourite-side
  `theo_edge` clears the margin — `theo - price` for a YES favourite,
  `price - theo` for a NO favourite (unit-test both signs; exclude commodity
  series that have no Coinbase underlying).
- **Always annotate `theo_edge` on every order — filled AND unfilled — even when
  not filtering.** The whole experiment lives in the scorer's ability to split
  the filled-vs-unfilled adverse-selection gap BY theo agreement: if theo is
  tradeable, the -6.2pp gap shrinks or reverses on the theo-agree subset versus
  the theo-disagree subset. If both subsets stay equally negative, the signal is
  real but **uncapturable as a passive maker**, and it is shelved with proof.
  This is the comparison neither the forward counterfactual nor the historical
  backtest could make honestly, because only real orders see the adverse fills.
- Cache spot+sigma once per product per cycle (shared across that product's
  strikes) to keep the read budget flat.

This is a strict extension of the live-microprobe discipline
(`live-microprobe-fill-measurement.md`): explicit consent with worst-case number,
reuse the tested order path, test the risk envelope, reconcile against the venue.
State the standing limit when reporting: it measures whether theo buys **better
fills**, not capture-at-size.

## Build posture

This is a **measurement instrument first**: price theo vs book, journal every
row, eyeball whether realized-vs-implied ever crosses in your favor across quiet
AND moving tape — BEFORE anything is armed. Same house rule the queue probe
taught: observe the counterfactual first, arm second. Implement it as a
standalone research script that imports the broker for read-only GETs only and
never reaches the order-placement method. Log an hour at 30s cycles to catch
both quiet and moving tape, then run the scorer once the covered markets settle.
