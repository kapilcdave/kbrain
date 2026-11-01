# Polymarket (US) dossier

Scope: PM-US recurring crypto, especially BTC/ETH 5M and 15M, and the
PM-US/Kalshi pair.  This is a venue page, not an execution authorization.
All conclusions below are post-cost and distinguish venue-print results from our
fills.  Source files are in `corpus/`; raw tapes are not committed.

## Venue facts

- **Contracts and settlement.** PM-US up/down crypto is a binary on the simple
  mean of the 60 CF Benchmarks BRTI index observations immediately preceding
  window open versus the corresponding mean before close; equality resolves
  Up.  5M (launched 2026-10-23) and 15M BTC/ETH/SOL/XRP have deterministic but
  irregular-prefix slugs.  Only the current 5M window is tradeable; `endDate`
  is close +30 minutes, not the decision time.  Generate slugs; do not census
  `/v1/markets`.  `priceToBeat` precision varies by asset and should be compared
  with a tolerance.  [pmus-5m-updown-venue-facts.md]
- **Kalshi identity.** BTC/ETH/SOL PM-US 15M and Kalshi KX*15M strikes matched
  exactly in 180/180 checked windows and use the same BRTI window; XRP differs
  in both directions in most windows and must be refused unless the individual
  window strike matches.  PM 5M's final five minutes and Kalshi 15M have the
  same terminal BRTI average but different already-published strikes, creating
  a model-free ordering constraint—not a generic 15M taker cross.
  [pmus-btc-15m-is-kalshi-kxbtc15m-twin.md;
  the-15m-twin-strike-gap-is-an-xrp-only-defect.md;
  pm-5m-and-kalshi-15m-are-two-strikes-on-one-terminal-value.md]
- **Fees, tick and book.** Crypto taker fee is
  `0.0695 * p * (1-p)` per leg (about 1.74c at p=0.50); tick is 1c and minimum
  quantity is 0.01.  The market payload's `feeCoefficient` is taker-only.  Our
  Tier-1 maker fee is zero, but do not infer maker economics from that payload.
  PM uses one Yes-token CLOB: `/v1/markets/{slug}/book` exposes
  `marketData.bids` and **`offers`** (not `asks`); buying No is selling Yes at
  `1 - bid`.  [topics-venue-facts.md; pmus-5m-updown-venue-facts.md]
- **Data path.** Use the authenticated market WebSocket, preserving
  `transactTime` and a local receive time.  MARKET_DATA is a roughly 100ms,
  change-suppressed per-market publication grid; TRADE is event-driven and is
  the correct persistence/fill-confirmation channel.  REST `/book` can be
  cached for 30s and is not an execution feed.  PM reconnects with 1001 and
  requires resubscription.  One socket can carry thousands of slugs.
  [pmus-runs-in-us-east-1-and-colocation-pays.md;
  one-pm-us-socket-carries-five-thousand-slugs.md]
- **History/schema traps.** `/v2/live-trade-history` ignores `startTimestamp`,
  serves a trailing-now sample, and its `longPrice`/`shortPrice` are stale asks;
  it cannot price historical taker entries.  Gamma pages cap at 100 and
  `interval=max` can be empty.  PM data-api trades are taker-perspective only;
  a wrong `condition_id` spelling can silently return global trades.  Public WS
  tapes can drop/coalesce frames: run coverage checks before scoring.  Historical
  1m marks are mids because tokens are complements, not executable quotes.
  [pmus-5m-updown-venue-facts.md; polymarket-price-history-traps.md;
  public-ws-tape-drops-and-slots-are-212ms.md; topics-venue-facts.md]
- **Liquidity reality.** In 5M, the book is two-sided through 60–120s but is
  one-sided below 60s; the apparent forecast becomes sharp exactly when an exit
  is unavailable.  BTC is the deepest; other assets are materially thinner.
  Any calculation must use causal displayed size and our fill set, collapse
  repeated observations into episodes, and cluster by independent window.
  [pmus-5m-updown-venue-facts.md; gemini-pmus-5m-taker-cross-closed.md]

## Our setup

- **Code.** `~/proj/kap` contains the read-only PM-US 5M→15M forecast work and
  paired PM-US/Kalshi WebSocket recorder/scorer (`fwd/polyus_pair_ws.py`,
  `fwd/score_polyus_pair_ws.py`).  The code has no live-trading mandate; secrets
  remain on the box.  The former `polymarket-us-mm` and `pmus-5m` projects are
  archived under the private `~/proj` monorepo.  [projects/INDEX.md;
  projects/HANDOFF-ASTRA.md; `~/proj/kap/README.md`]
- **Boxes/latency.** PM-US infrastructure is in AWS us-east-1.  An us-east-1d
  probe cut PM order-path RTT from 13.3ms to 4.5ms and receives book changes
  about 6.7ms earlier than us-east-2, but PM's own publish delay is about 48ms;
  REST remains unusable for fast decisions.  Current paired PM/Kalshi tape runs
  on `rustmaker` (us-east-2) because its Kalshi leg matters; do not infer a fill
  advantage from tape timing.  [pmus-runs-in-us-east-1-and-colocation-pays.md;
  fleet.md]
- **Operational constraints.** Never use stale REST for a signal, trust a
  cancel acknowledgement without re-reading open orders, or assume a private
  position/balance stream is authoritative.  PM cancel requests require
  `marketSlug`; there is no POST_ONLY TIF, so post price must be revalidated
  immediately before sending or a quote can become a costly taker.  No real
  PM-US order is authorized by this dossier.  [pmus-5m-updown-venue-facts.md]

## Closed branches

- **Unconditional PM-US 5M/15M crypto taker:** closed.  No price/tau band was
  net-positive with CI above zero after executable 5-share VWAP and taker fees;
  underdogs are rich and favourites are approximately fair.
  [pm-5m-15m-unconditional-taker-calibration-no-edge.md]
- **PM-US 5M maker (our fills):** closed.  Venue prints were positive
  (+1.83c/ct), but our third arm lost $1.37: late one-sided books made flatten
  roughly 48c, not a spread-plus-fee exit.  This is an own-fill closure, not a
  claim that venue-average maker prints are negative.
  [pmus-5m-updown-venue-facts.md]
- **Kap5 as PM-US 5M taker or maker gate:** closed.  The forecast loses to the
  market after toll; maker-gate pickoff lift was 0.022c (95% CI
  [-0.267,+0.315]) against a +1.45c promotion bar.  Do not reopen by asset or
  tau slicing.
  [kap5-pmus-5m-forecaster.md]
- **PM-US/Kalshi 15M taker-taker:** closed across BTC/ETH/SOL/XRP.  The
  apparent positives are short stale-leg spells and cannot clear the two-leg
  toll with our reaction path; XRP also has unsafe strike disagreements.
  [pmus-btc-15m-is-kalshi-kxbtc15m-twin.md;
  the-15m-twin-strike-gap-is-an-xrp-only-defect.md]
- **PM wallet copy to Kalshi / on-venue crypto wallet tails:** closed.  Leader
  price, not portable direction, explains the 15M result; the 5M forward tail
  test was +0.047c, CI [-1.378,+1.392].  [polymarket-15m-copy-to-kalshi-closed.md;
  pm-5m-tail-forward-fail-20261023.md]
- **PM-US/PM-intl 5M and Gemini/PM-US 5M taker crosses:** closed on fee,
  persistence, and especially min-leg capacity.  PM-intl may remain a
  fair-value *feed*, never a licensed PM-US trade leg for this operator.
  [pm-intl-vs-pmus-5m-cross-is-closed.md;
  gemini-pmus-5m-taker-cross-closed.md]
- **Tennis score reaction/score-state takers:** closed; observed score
  information recovers only about 60% of friction and the score-state family is
  negative net.  [pmus-tennis-score-branches-closed.md]
- **Generic PM-US non-sports/wide-book maker or internal-consistency arb:** not
  a live route.  Wide books are commonly unquoted/empty; PM-US enforces tested
  partition and ladder constraints.  [pmus-nonsports-wide-books-are-unquoted-books.md;
  pmus-venue-dossier.md]

## Live / open bets

- **KAP PM-US/Kalshi paired-book frozen preflight — collecting, decision
  2026-11-02.** `kap-poly15-ws` is declared in `runners.toml` on `rustmaker` as
  tape only.  It records paired BTC 15M WS books.  After the scheduled cutoff,
  pull and stream-score off-box; audit gzip, contract identity, receive-time
  limits, WS reconnects, and Kalshi sequence gaps.  Report episodes and unique
  15M windows separately.  It closes if no post-fee executable gap survives our
  reaction/staleness controls.  A positive top-of-book replay is not a fill or
  deployment result.  [NOTEBOOK.md; runners.toml; fleet.md]
- **PM 5M/Kalshi 15M strike-ordering screen:** structural mechanism verified,
  but not yet screened with causal live books.  It is distinct from the closed
  identical-15M taker cross; first test is a read-only, post-fee ordering
  violation screen using WS books and actual displayed size.  No order path is
  approved.  [pm-5m-and-kalshi-15m-are-two-strikes-on-one-terminal-value.md]

## Verdicts

### 2026-11-01 — KAP 5M→15M transfer: no promotion; paired-book audit remains open

Measured: the 12-hour read-only forward tape had 50 distinct 15M windows.
At 60s, the 5M-transfer vs index-only Brier difference was -0.0057 with 95%
window-bootstrap CI [-0.0171,+0.0049] on 32 windows; at 300/600s transfer
coverage was only three windows.  Frozen promotion criteria failed.  A BBO
report's apparent 62.7c gaps were invalid: full depth showed missing PM bids,
different offers, and some post-close rows.  Conclusion: no KAP feature or
order-rule promotion; retain only the separately declared L2/WS paper audit.
[~/proj/kap/FINDINGS_polyus_5m_transfer_20261101.md; NOTEBOOK.md]

### 2026-10-29 — PM-US 5M maker: failed on our fills

Measured: 136 fills produced 67 matched round trips and two unpaired legs;
two costly flattens/unpaired outcomes yielded -$1.37 attributed P&L.  The
failure rate exceeded the approximately 1.7% break-even rate once actual
failure cost (~56.5c) replaced the false 4c flatten assumption.  Conclusion:
do not arm this maker family on venue-average markout.
[pmus-5m-updown-venue-facts.md]

### 2026-10-23 — PM 5M wallet-tail forward test: failed

Measured: +0.047c, 95% CI [-1.378,+1.392], across 2,043 wallet-windows;
the all-taker control was -1.99c.  Conclusion: a possible relative wallet
effect is not a post-fee absolute edge; close crypto wallet-copy variants
without a new mechanism.  [pm-5m-tail-forward-fail-20261023.md]

## Corpus pointers

- **Start for mechanics and schema:** `pmus-5m-updown-venue-facts.md`,
  `pmus-venue-dossier.md`, `topics-venue-facts.md`,
  `polymarket-price-history-traps.md`.
- **Before PM/Kalshi work:** `pmus-btc-15m-is-kalshi-kxbtc15m-twin.md`,
  `the-15m-twin-strike-gap-is-an-xrp-only-defect.md`,
  `pm-5m-and-kalshi-15m-are-two-strikes-on-one-terminal-value.md`,
  `the-pm-first-15m-seat-is-a-race-not-a-latency-problem.md`.
- **Before a maker/fill claim:** `pmus-5m-updown-venue-facts.md`,
  `topics-maker-seat-mechanics.md`, `topics-estimator-and-inference-traps.md`,
  `public-ws-tape-drops-and-slots-are-212ms.md`.
- **Before reopening a branch:** `priors.md`, `topics-closed-branches.md`,
  `pm-5m-15m-unconditional-taker-calibration-no-edge.md`,
  `kap5-pmus-5m-forecaster.md`, and the branch-specific closure above.
- **Operational/research provenance:** `projects/INDEX.md`,
  `projects/HANDOFF-ASTRA.md`, `NOTEBOOK.md`, `runners.toml`, and `fleet.md`.
