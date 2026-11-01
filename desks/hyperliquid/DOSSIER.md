# Hyperliquid dossier

Last reconciled: 2026-11-01. Scope: Hyperliquid perps and HIP-4 outcome
markets. Measured statements below are from the cited corpus artifacts; an
open tape is not a result or an arm.

## Venue facts

### Perps

- Public REST/info base is `https://api.hyperliquid.xyz`; public WebSocket is
  `wss://api.hyperliquid.xyz/ws`. Perp coins use plain names (for example
  `ETH`, `PUMP`, `ZEC`); ccxt names the same contract `ETH/USDC:USDC`.
  `l2Book` requires a `dex` in the body for HIP-3 builder books. See
  `corpus/hyperliquid-l2book-is-slow-bbo-is-the-fast-channel.md` and
  `corpus/hl-perp-maker-fee-is-not-binding-adverse-selection-is.md`.
- The public perp WebSocket has no incremental-depth feed: full `l2Book`
  snapshots arrived every 5,382 ms median, while `bbo` arrived every 74 ms
  median (p10 29 ms). Use `bbo` for a markout clock and treat depth/OBI as
  roughly 5.4 s stale. `trades.side` is the aggressive/taker side (sweep-walk
  validation 0.996); passive side is its complement. Do not infer side from
  the post-print touch. Source: `corpus/hyperliquid-l2book-is-slow-bbo-is-the-fast-channel.md`.
- Base-tier fee assumptions used in the perp work are maker 1.5 bp and taker
  4.5 bp; verify the account's live schedule before any execution. Default
  public ccxt fees are not account-specific. Main-dex BTC is not a proxy for
  the venue: its 0.06 bp half-spread was 25x its maker fee, while the
  cross-venue median across 206 perps was 1.84 bp and 116/206 exceeded the
  1.5 bp maker fee. Sources: `corpus/hyperliquid-l2book-is-slow-bbo-is-the-fast-channel.md`,
  `corpus/hl-perp-maker-fee-is-not-binding-adverse-selection-is.md`.
- HIP-3 builder dexes (`xyz`, `flx`, `vntl`, `hyna`, `km`, `abcd`, `cash`,
  `para`, `mkts`, `io`) are a distinct instrument surface. Wide quoted spreads
  do not imply scale: observed touch depth was only $12--$1,253. Liquidity and
  observed edge must be evaluated by time of day and by notional as well as
  per-fill weighting. Source: `corpus/hl-perp-maker-fee-is-not-binding-adverse-selection-is.md`.

### HIP-4 outcome markets

- Mainnet outcome-market info is public. At the last verified read,
  `feeScale` was `1.0` and the implementation treated fees as zero, but a
  later audit notes that this may be a multiplier, not a waiver; re-verify
  rather than assert zero. Contracts are USDC-collateralized with no leverage
  or liquidation. Sources: `projects/hl-outcomes/README.md`,
  `corpus/hl-15m-implied-vol-is-rich-favourite-is-the-port.md`.
- Asset encoding is `enc = 10*outcome + side`, coin `#enc`, token `+enc`, and
  order asset id `100000000 + enc`. It is one merged dual book: buy Yes at `p`
  is sell No at `1-p`, with price-side-time priority. A mirrored ladder level
  is not separate executable depth. Source:
  `corpus/hyperliquid-hip4-has-a-15m-crypto-twin.md`.
- BTC/ETH/HYPE perp-mark binaries run on the 15-minute :00/:15/:30/:45 grid;
  they settle **strictly above** threshold using a 60-second TWAP of the named
  feed, normally the HL perp `markPx`. Threshold is the rounded window open,
  not deploy-time ATM. `markPx` and `oraclePx` differ, so record the named
  `priceDescription` feed, not an assumed oracle. Sources:
  `corpus/hyperliquid-hip4-has-a-15m-crypto-twin.md`,
  `corpus/pm-intl-vs-hl-15m-cross-is-closed.md`.
- Outcome coins have no `bbo`; outcome `l2Book` is sparse and change-driven.
  `activeAssetCtx` provides the settlement `markPx` around once a second and
  is WebSocket-only; REST `metaAndAssetCtxs` is the fallback for that data.
  Settled outcome coins disappear: historical labels are enumerable via
  `settledOutcome`, but their books, trades and candles cannot be fetched.
  Any price/book result therefore needs an intact live tape. Source:
  `corpus/hyperliquid-hip4-has-a-15m-crypto-twin.md`.
- Outcome schema traps: parse `time:YYYYMMDD-HHMM` with a strict fixed-width
  matcher (permissive `strptime` misread `0615` as `06:01:05`); do not use a
  candle keyed at `T` as the price at `T`--it is the bar close. Per-IP limits
  observed: 1,200 weight/min; info 20, `l2Book`/`allMids` 2, and
  `candleSnapshot` 20 plus 20 per 60 candles. Source:
  `corpus/hyperliquid-hip4-has-a-15m-crypto-twin.md`.

## Our setup

- Research box: `hypephil`, AWS Tokyo (`ap-northeast-1a`), t3.micro. It is the
  Hyperliquid research box, with code in `~/proj/hypephil`/the preserved
  `~/proj/hl-outcomes` tree, data in `~/data`, and logs in `~/logs`. It has an
  8 GB disk; raw tape is about 150 MB/hour for the current wide sweep. Check
  RAM and disk before any collector action and score tapes off-box. Source:
  `fleet.md`.
- Repository history: the former `hypephil` repository was deduplicated on
  2026-10-31 after its history was preserved as `hypephil-main`; the canonical
  code is `projects/hl-outcomes`. It is read-only research code: `mmtape.py`,
  `mmscore.py`, `mmscreen.py`, and `cover.py` support perp work; HIP-4 tools
  include `record.py`, `roundtrip.py`, `pickoff.py`, `evtaker.py`, and
  `deltahedge.py`. Sources: `projects/INDEX.md`, `projects/hl-outcomes/README.md`.
- Feed position: our observed feed lag is about 8.5 ms and there is no FIX;
  do not frame an HL proposal as a race we need to win. That latency was not
  binding in the initial main-dex maker closure, but it makes a positive
  venue-average fill result insufficient for arming. Sources:
  `priors.md`, `corpus/hyperliquid-l2book-is-slow-bbo-is-the-fast-channel.md`.
- Tape hygiene: run `cover.py` before scoring. A WebSocket gap is not quiet
  market data; require a post-horizon fresh `bbo` markout when testing for
  change-driven-feed artifacts. Keep raw tapes out of git. Sources:
  `projects/hl-outcomes/PREREG_hl_builder_maker_20261030.md`,
  `corpus/topics-estimator-and-inference-traps.md`.

## Closed branches

- **Main-dex perp touch maker — CLOSED.** 12 h/428,544 passive fills: captured
  +0.385 bp versus adverse +0.582 bp, net -1.697 bp; all eight coins negative,
  and still -0.263 bp at zero fee. The six-hour replication found pooled
  notional net0 -0.386 bp [ -0.494, -0.288 ]. Do not reopen on fee tier, rebate,
  wider coin, quote-rate tuning, faster box, or a generic forecasting gate;
  captured spread approximately equals adverse selection. Sources:
  `corpus/hyperliquid-l2book-is-slow-bbo-is-the-fast-channel.md`,
  `corpus/hl-perp-market-making-is-a-rebate-business-not-an-alpha-one.md`.
- **Generic HL perp MM is a rebate/capacity business, not an alpha seat.** Main
  dex has gross near zero and base fees turn it negative. Builder-cell positives
  require disjoint-window replication and then own-fill, impact, and capacity
  evidence; they do not license live trading. Source:
  `corpus/hl-perp-market-making-is-a-rebate-business-not-an-alpha-one.md`.
- **HIP-4 15M maker, taker, forecast maker, delta hedge, and cross-strike/cross-
  venue arms — CLOSED.** The full 20 h tape (187 markets, 10,238 round trips)
  made pooled maker -$17.41 / -0.04c per leg; the tight-book lead fell from
  +7.37c to +2.36c with CI spanning zero. Taker cannot clear its ~9.13c toll
  even under the perfect-forecaster bound; delta hedging costs 5--12x the pool.
  Reopen only on a genuinely different instrument. Sources:
  `projects/hl-outcomes/README.md`,
  `corpus/hl-15m-implied-vol-is-rich-favourite-is-the-port.md`.
- **PM international x HIP-4 15M cross — CLOSED.** 869 windows: strike buffer
  maxed at 10.2/13.0/18.5 bp (BTC/ETH/HYPE), never clearing the p90 24.8 bp
  mark-vs-spot oracle divergence. It is a naked basis bet, not a lock. Source:
  `corpus/pm-intl-vs-hl-15m-cross-is-closed.md`.
- **Porting a fixed-strike 15M forecast to an HL perp taker — CLOSED as stated.**
  The fixed-strike label includes already-realized movement; a perp needs the
  forward increment. Rescore any genuinely new signal on signed incremental
  return and executable taker toll, not binary Brier/AUC. Source:
  `corpus/a-fixed-strike-forecast-does-not-transfer-to-a-perp-taker.md`.

## Live / open bets

- **HL wide maker replication, collecting on `hypephil`; decision 2026-11-02.**
  The active frozen decision is `PREREG_hl_wide_maker_20261101`: growth-mode
  HIP-3 tape plus a 162-coin three-shard sweep. Pass requires 1 s CI excluding
  zero on both per-fill and per-notional weightings and positive 30 s result,
  each in disjoint D and R partitions. The earlier 29-altcoin arm is closed;
  its finishing tape is not an open result. Source: `fleet.md`.
- The only historical builders to merit this replication were `xyz:PURRDAT`
  and `xyz:KIOXIA`: one 6 h venue-average window was positive after the base
  fee on both weightings. Two laptop replications were VOID for 54%/62%
  coverage loss, not pass or fail. This remains a venue-average screen, not
  our fill set. Source: `projects/hl-outcomes/PREREG_hl_builder_maker_20261030.md`.
- No Hyperliquid strategy is armed. `mmlive.py` requires fresh operator
  approval; any validated tape result still needs an order path, preflight,
  impact/own-fill validation, resources and a DRY run first. Source: `fleet.md`.

## Verdicts

### 2026-11-01 — seed reconciliation: wide maker is the sole active HL decision

**Measured:** `fleet.md` lists `mmtape_growth` and `mmtape_w1`/`w2`/`w3` running
through 2026-11-02, plus `compress_closed`; the 29-alt tape is explicitly
closed. **Inference:** the active work is a replication/screen, not a reversal
of the main-dex or HIP-4 closures. **Conclusion:** do not arm or score before
the frozen tape endpoints; evaluate independent partitions/windows, both
weightings, coverage, fresh markouts, fees, and our attainable fills.

### 2026-10-30 — builder-dex positive cells require replication, not deployment

**Measured:** on one 6 h tape, `xyz:PURRDAT` and `xyz:KIOXIA` cleared the
base-fee result on both published weightings, while main-dex net0 remained
negative. **Inference:** a distinct HIP-3 surface could differ from main dex,
but the observed touch flow is venue-average with shallow depth. **Conclusion:**
replication only; prior attempts were void for laptop sleep/coverage failure.
Source: `corpus/hl-perp-market-making-is-a-rebate-business-not-an-alpha-one.md`.

### 2026-10-29/30 — HIP-4 15M family closed

**Measured:** full-day outcome tape erased the tight-book maker lead; taker
and delta-hedge bounds independently fail. **Conclusion:** all model, width,
and box variants of that instrument family are closed; retain the conclusion
and the correction that its strike is window-open. Sources:
`corpus/hl-15m-implied-vol-is-rich-favourite-is-the-port.md`,
`corpus/pm-intl-vs-hl-15m-cross-is-closed.md`.

### 2026-10-13 and 2026-10-30 — main-dex perp maker family closed

**Measured:** captured spread was not enough to offset adverse selection before
fees in the original 12 h study and was reproduced on subsequent tape.
**Conclusion:** a speed, fee, or generic spread gate is not a reopening
condition. Sources: `corpus/hyperliquid-l2book-is-slow-bbo-is-the-fast-channel.md`,
`corpus/hl-perp-market-making-is-a-rebate-business-not-an-alpha-one.md`.

## Corpus pointers

- Start with `priors.md`, then `corpus/MEMORY.md`,
  `corpus/topics-closed-branches.md`, and
  `corpus/topics-estimator-and-inference-traps.md` before proposing or scoring.
- Perp market mechanics and current builder context:
  `corpus/hyperliquid-l2book-is-slow-bbo-is-the-fast-channel.md`,
  `corpus/hl-perp-maker-fee-is-not-binding-adverse-selection-is.md`,
  `corpus/hl-perp-market-making-is-a-rebate-business-not-an-alpha-one.md`, and
  `projects/hl-outcomes/PREREG_hl_builder_maker_20261030.md`.
- HIP-4 facts and permanent 15M exclusions:
  `corpus/hyperliquid-hip4-has-a-15m-crypto-twin.md`,
  `corpus/hl-15m-implied-vol-is-rich-favourite-is-the-port.md`, and
  `corpus/pm-intl-vs-hl-15m-cross-is-closed.md`.
- Taker signal framing: `corpus/a-fixed-strike-forecast-does-not-transfer-to-a-perp-taker.md`.
- Operational and measurement controls: `corpus/topics-live-arming-and-plumbing.md`,
  `corpus/topics-machine-and-repo-facts.md`, and
  `corpus/topics-latency-and-feed-races.md`.
