# Gemini prediction markets dossier

_Seeded 2026-11-01. Scope: recurring BTC/ETH/SOL/XRP 05M and 15M crypto
contracts. Measured facts are labelled; an inference is not an executable edge._

## Venue facts

- **Surface and instruments.** Public REST root is
  `https://api.gemini.com/v1/prediction-markets`; the sandbox root is
  `https://api.sandbox.gemini.com`. Crypto up/down is one `-UP` binary per
  event: ticker `{ASSET}{DURATION}{YYMMDDHHmm}`, UTC expiry, instrument symbol
  `GEMI-{event}-{contract}`. 15M windows are `:00/:15/:30/:45`; the strike is
  the opening reference price. 05M and 15M BTC/ETH/SOL/XRP families are the
  recurring universe. [measured: `FINDINGS_venue_discovery_20261028.md`]
- **Grid and settlement.** Price fields are decimal strings on 0--1 with a
  $0.01/one-cent tick; minimum quantity and increment are 0.01 contract.
  `strike` is absent until the window opens, then is rounded to two decimals;
  do not treat a missing future strike as a missing market or use exact float
  equality. The apparent settlement index is Lukka LS-LRRR
  (`XBT`, `ETH`, `SOLN`, `XRP`); it is an averaged, not tick-for-tick, index.
  Its averaging horizon remains unpinned. [measured/open:
  `FINDINGS_venue_discovery_20261028.md`]
- **Fees and clips.** Discovery recorded taker fee
  `0.07*C*P*(1-P)` and maker fee `0.0175*C*P*(1-P)`, each rounded **up** to a
  cent, with no settlement/cancel fee. Thus small clips are invalid economics:
  0.01 contract pays 100 c/ct at the floor and a clip of 10 pays 1.75 c/ct
  taker at P=.50 before spread. Maker rebates apply only in the $0.20--$0.80
  band and round down, so a maker must be costed per order and clip, not by a
  continuous fee rate. [measured: `fee_math.py`,
  `FINDINGS_venue_discovery_20261028.md`]
- **Maker-fee caveat.** The public rate data showed a 0.30 multiplier (the
  former 0.70 promo had expired), but the human schedule and machine-readable
  spec disagree whether the rebate is based on the taker or maker fee. At
  P=.50 that is a roughly 0.39 c/ct sign difference (apparent -0.0875 c/ct
  credit versus +0.306 c/ct cost, before rounding). Do not arm any rebate-led
  maker case until an actual eligible fill and its 5pm ET rebate settle this.
  [unresolved: `FINDINGS_venue_discovery_20261028.md`]
- **Liquidity/capacity.** The liquidity-rewards configuration observed on
  2026-10-28 required at least 10 contracts, up to 10c spread and 50% snapshot
  uptime, but stated an end date of 2026-11-06; it is a temporary subsidy, not
  base economics. In a 90-second 15M tape, BTC touch width p50 was 9c and
  ETH/SOL/XRP 13c; touch capacity was only about $3/$27 BTC and $150--255 on
  the other assets. Treat this as a wide-maker venue, not a tight-scalar; the
  crypto category then turned about $223--437k/day. [measured, short tape:
  `FINDINGS_venue_discovery_20261028.md`]
- **REST vs WebSocket.** All market data is public; metadata/settled history
  are REST, but there is no REST orderbook. Use `wss://ws.gemini.com` with
  `?snapshot=-1` for an initial absolute book; otherwise `@depth` is delta-only
  and cannot recover absolute depth. Useful public streams: `@bookTicker`,
  `@depth{5,10,20}[@100ms]`, `@trade`, Lukka `@indexPrice`, and
  `contractStatus`. `recently-settled` is only about 24 hours / 200 rows, so
  history is forward-tape only. [measured: `FINDINGS_venue_discovery_20261028.md`]
- **Schema traps.** Returned symbols are lowercase. Socket event time units
  differ: book ticker `E` ns, `thirdPartyPrice.E` seconds, and
  `contractStatus.E` ms. Lukka subscription names, frame index IDs, and
  returned symbols differ (`LS-LRRR-XBTUSD`, `LRRR_XBT`, `btcusd`).
  `contractStatus.p` carries the live activation strike. [measured:
  `FINDINGS_venue_discovery_20261028.md`]
- **Private access.** Signed REST worked in prior discovery, but the existing
  master/group credential could not authenticate private WS streams (401); an
  account-scoped key is required for orders/positions/balances streams. This
  does not block public tapes. Never record credentials here. [measured:
  `FINDINGS_venue_discovery_20261028.md`]

## Our setup

- **Box/code.** `geminibot`, AWS us-east-1b t3.micro, Python 3.9; code lives
  at `~/proj/geminibot`. No live orders have been placed from this box.
  Laptop latency was not relevant to execution; the Gemini project identifies
  the us-east-1 measurement as the decision-relevant one. [staged
  `fleet.md`; `FINDINGS_venue_discovery_20261028.md`]
- **Research/tape path.** `depthtape.py` records Gemini absolute depth plus
  lead spot feeds; `record.py` records book/trade/oracle provenance;
  `strikepoll.py` saves contiguous opening strikes; `leadfeed.py` compares
  lead venues; `gemflow.py` and `capcurve.py` score the frozen taker
  preregistration. All current score inputs are public/read-only.
- **Dry maker.** `quoter.py` is dry by default and logs intended actions with
  ns timestamps. Its proposed range is 25--250 contracts, only in the
  $0.20--$0.80 rebate band, with maker-or-cancel and index-move cancellation.
  A dry order/cancel is plumbing only, not a fill result or maker edge.
- **Latency/seat.** The frozen basis premise is slow (Lukka about a 48-second
  time constant and book absorption inferred at 5--8 minutes), so it is not a
  sub-10ms feed race. That mechanism still requires scoring executable VWAP
  from our fill set. [inference, not a live claim:
  `PREREG_gemflow_basis_taker_20261031.md`]

## Closed branches

- **Gemini--Kalshi settlement lock / taker cross: closed.** 47/48 one-day
  15M outcomes agreed, but the one full-loss disagreement implies roughly 2
  c/ct oracle-risk allowance before fees and the 9--13c Gemini spread; it is
  not a settle-for-settle lock. A new instrument or settlement mechanism is
  required to reopen. [small sample, `FINDINGS_venue_discovery_20261028.md`]
- **Unconditional basis taker: closed for the tested shape.** The first
  clip-10 BTC reading was -0.574 c/ct at 0.95 opportunity rate: average
  predictable move (~2.3c) did not clear the measured 4.40c clip-10 toll.
  Only the separately frozen noise-derived tail threshold remains open.
  [exploratory diagnostic, `PREREG_gemflow_basis_taker_20261031.md`]
- **Rebate-led maker arm: blocked, not validated.** The rebate-base ambiguity
  can flip its sign; no actual eligible fill/rebate has resolved it. Do not
  treat broad-spread simulation or liquidity rewards as a deployable maker
  edge. [source above]
- **All row-level/venue-average claims: closed as evidence.** A prior apparent
  +2.15 c/ct Gemini pass used 7,997 samples from only 60 settlement draws.
  Count one first fillable signal per window/clip; paper fills cannot replace
  our own fills. [estimator correction:
  `PREREG_gemflow_basis_taker_20261031.md`; `priors.md`]

## Live / open bets

- **Basis taker, collecting; decision target 2026-11-03.** The frozen
  confirmatory cell is BTC, clip 10, 1.9c noise-derived threshold, one first
  fillable signal per independent window. It needs n >= 222 BTC windows;
  pass requires net c/ct > 0 with 95% lower CI > 0 and opportunity rate >=.10.
  `gb-depthtape`, `gb-record`, `gb-strikepoll`, and `gb-leadfeed` are declared
  tape runners through 2026-11-08. [staged `runners.toml`, `fleet.md`,
  `PREREG_gemflow_basis_taker_20261031.md`]
- **Maker/quoter, DRY only.** `gb-quoter` is declared dry through
  2026-11-02T06:00Z for BTC15M/ETH15M integration; it is not permission to
  arm, nor proof of fills or fees. [staged `runners.toml`]
- **Data integrity boundary.** Exclude the 06Z post-reboot depth slice: it had
  32 depth updates and one BTC05M symbol. The 07Z slice recovered 5,300 depth
  updates across four 15M families plus BTC05M by 07:37Z. This is collection
  health, not score evidence. [measured: `NOTEBOOK.md`, 2026-11-01]

## Verdicts

### 2026-11-01 — underpowered shift diagnostic; no verdict

Measured at 08:08Z: the recovered 08Z file covered 08:00:00.009--08:08:39.877Z
with 14,413 Gemini rows and 1,744 depth updates across 16 symbols. Across the
available 04Z and 08Z files, the frozen scorer found 352 anchors, 336 labelled
windows, 84 BTC clip-10 opportunities, and only 6 first signals (3 buys), for
an opportunity rate of 0.07 and exploratory net **-32.691 c/ct** (sd 6.47;
95% lower bound -37.872). The known incomplete 06Z interval was excluded.
This is below the preregistered 0.10 rate gate and far below n>=222; the clean
08Z slice alone is too short to fit the frozen reconstruction model. Conclusion:
underpowered coverage diagnostic only; keep collecting, no pass/fail and no
arming claim. The DRY quoter logged 8,820 orders and 8,818 cancels, with no
fill events, so it provides no maker evidence. [source: shift `NOTEBOOK.md`,
2026-11-01]

### 2026-11-01 — underpowered / no score

Measured: post-reboot 06Z tape was incomplete and excluded; 07Z recovered.
No P&L was calculated. Conclusion: keep the frozen forward collection open;
do not call pass, fail, or maker readiness. [source: `NOTEBOOK.md`]

### 2026-10-31 — basis mechanism retained; executable edge unresolved

Measured diagnostics support a 36-second reconstructed Lukka time constant
and a tail-shaped basis signal, but the non-threshold first look lost -0.574
c/ct BTC clip-10. The response was a preregistered 1.9c, noise-derived BTC
threshold requiring n >= 222 independent windows, not selection of the
exploratory argmax. Conclusion: collecting only. [source:
`PREREG_gemflow_basis_taker_20261031.md`]

### 2026-10-29 — book absorption mechanism pass, not deployable

Stage 2 reports 138 window clusters and 100k+ observations: only 1.1--1.5%
of spot-vs-Lukka basis was absorbed in 5 seconds, below the predeclared
economically relevant ceilings. It was a mid-change regression, not an
executable fill test; maker held-to-settlement was independently -10.45 c/ct.
Conclusion: it justified the taker VWAP test, not an arm. [source:
`PREREG_stage2_book_absorption_20261029.md`]

## Corpus pointers

- **Venue contract/API/fees/schema:** Gemini project
  `FINDINGS_venue_discovery_20261028.md`, `vendor/prediction-markets.yaml`,
  `fee_math.py`, `ws_probe.py`.
- **Open basis-taker decision and estimator safeguards:**
  `PREREG_gemflow_basis_taker_20261031.md`, `gemflow.py`, `capcurve.py`,
  `reconq.py`, plus corpus `topics-estimator-and-inference-traps.md`.
- **Maker mechanics and latency/race exclusions:** `quoter.py`,
  `PREREG_stage2_book_absorption_20261029.md`, corpus
  `topics-maker-seat-mechanics.md` and `topics-latency-and-feed-races.md`.
- **Recurring-crypto analogues and excluded branches:** corpus
  `topics-15m-crypto-seat.md`, `topics-closed-branches.md`, and `priors.md`.
- **Operational state:** `desks/gemini/NOTEBOOK.md`,
  `desks/gemini/runners.toml`, `fleet.md`; raw tapes stay on the box/state,
  never in git.
