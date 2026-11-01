# Kalshi dossier

_Seeded 2026-11-01.  This is the venue page for recurring short-horizon work;
it records measured venue facts separately from inference and trading verdicts.
It does not authorize an armed runner._

## Venue facts

- **Contract and price schema.** REST `*_dollars` fields are decimal strings on
  a 0--1 dollar scale; do not use the nullable integer-cent fields.  `volume_fp`
  and trade `count_fp` are fractional contracts.  For 15-minute crypto the
  minimum tick is **0.1 cent**, not one cent.  `taker_side` is the operative
  direction field in public trade history.  _Sources:
  `corpus/kalshi-venue-mechanics.md`, `corpus/kalshi-prices-are-dollar-strings.md`,
  `corpus/kalshi-15m-tick-is-a-decicent.md`._
- **Public history versus depth.** Public one-minute candles contain top-of-book
  yes bid/ask OHLC, and public settled markets/trades can support a taker replay.
  They do **not** contain historical resting depth, queue position, or causal
  receipt time; any claim requiring those must forward-collect an L2 tape.
  Candle `ts` is the **bar close**, so a one-minute bar ending at `E` covers
  `[E-60s,E)`.  _Sources: `corpus/kalshi-candlesticks-are-unauthenticated.md`,
  `corpus/kalshi-retains-no-historical-resting-depth.md`,
  `corpus/candle-bar-ts-is-the-bar-close.md`._
- **History routing correction.** The former “67-day floor” is an archive
  cutoff, not deletion: use `/trade-api/v2/historical/{markets,trades,...}` for
  pre-cutoff data and cursor-page it (the archive ignores `max_close_ts`).  The
  ordinary pre-cutoff `/trades` route can return a silent empty list.  Historical
  depth remains unavailable.  _Source and retraction:
  `corpus/kalshi-market-history-has-a-67-day-floor.md`._
- **15M crypto mechanics.** KX*15M is “up versus the window-open strike”; it
  settles on the CF RTI/BRTI trailing 60-second average, republished at 1 Hz.
  `live_data.details.timeseries[].v` is already that rolling value, so do not
  average it a second time.  The 15M ticker clock is US/Eastern.  Resolve the
  active window with `min_close_ts`/`max_close_ts`, never a `status` filter:
  rollover can yield either no current market or future unstruck markets.
  _Sources: `corpus/kalshi-15m-settles-on-cf-rti-republished-at-one-hertz.md`,
  `corpus/kalshi-live-data-v-is-the-brti-settlement-value.md`,
  `corpus/kalshi-15m-ticker-timestamp-is-eastern.md`,
  `corpus/topics-venue-facts.md`._
- **Interfaces and limits.** Candles and `GET /markets/{ticker}/orderbook` are
  public; REST candle reads tolerate roughly 2--3 requests/s, and rate limits
  are per route.  Use WebSocket for live book/tape work, not the cached
  `/markets?series_ticker=` list (quotes can lag about 30s).  For live cancels,
  V2 needs the `market_ticker` shard hint; treat a 404 as an error to investigate,
  not proof an order is gone.  _Sources: `corpus/topics-venue-facts.md`,
  `corpus/kalshi-venue-mechanics.md`, `corpus/kalshi-rate-limits-per-route-not-per-host.md`._
- **Fees and settlement implementation.** Fee type is market/series-specific;
  read and archive the applicable schedule before scoring.  Crypto KX*15M is
  quadratic/taker-billed in the tested family.  Binary yes/no is one signed
  position, not a hedge.  Balance and order routing are shard-specific; price
  units, balance fields, and intra-shard transfer units differ, so obtain these
  facts from the current client/API rather than hard-coding them.  _Sources:
  `corpus/topics-15m-crypto-seat.md`, `corpus/kalshi-venue-mechanics.md`,
  `corpus/buying-no-is-the-exit-not-a-hedge.md`._

## Our setup

- **Box:** `rustmaker`, AWS us-east-2b t3.micro, Kalshi execution/tape box.
  Check `fleet.md`, `free -m`, and `df -h` before starting anything; do not
  analyse large tapes there or touch another runner.  Only the operator may arm
  a real-order process.  _Sources: `fleet.md`,
  `corpus/dont-run-tape-analysis-on-the-1gb-box.md`._
- **Execution code:** `~/proj/rustmaker` (Rust package `kalshi-mm15`, branch
  `altspot` at seed time) has separate probe, shadow, 15M live/dry, sports,
  `altspot`, and `altlive` paths.  `--dry-run` sends no order/amend/cancel;
  non-dry order paths require `--armed`.  KAP (`~/proj/kap`) is a separate
  probability/replay and forward-L2 research codebase; it does not itself
  authorize trading.  _Sources: `~/proj/rustmaker/Cargo.toml`,
  `~/proj/rustmaker/src/main.rs`, `~/proj/kap/README.md`._
- **Latency posture (measured, not a target):** current public-WS reaction is
  about 9.5ms (roughly 6.6ms feed age, ~0.01ms local decision, ~2.85ms
  order-to-book).  FIX is entitlement-blocked.  Faster local code will not
  turn a cancel race into our edge; competitors are materially faster and the
  feed itself is the dominant delay.  _Sources:
  `corpus/kalshi-order-latency-is-venue-side-and-fix-is-tier-blocked.md`,
  `corpus/kalshi-15m-crypto-competitors-react-twice-as-fast-as-the-ohio-box.md`._
- **Measurement rule:** score our matched fills/round trips with costs, causal
  timestamps and independent close-window/event clusters--never venue-average
  prints or panel rows.  A candle quote can validate a decision price but not a
  fill set.  _Sources: `corpus/score-a-binary-maker-on-matched-round-trips.md`,
  `corpus/a-verified-decision-price-is-not-a-verified-fill-set.md`,
  `corpus/topics-estimator-and-inference-traps.md`._

## Closed branches

- **15M crypto/commodity generic market making:** closed end-to-end (A--S,
  GLFT, microprice, Cartea--Jaimungal, RL/C51, two-sided/one-sided and
  hold/flatten variants).  Real-print corrections reduced simulated adverse
  selection, but did not make the venue-normal fill economics deployable for
  us.  Do not reopen by adding features, tuning delay, width, or model class.
  _Sources: `corpus/topics-closed-branches.md`,
  `corpus/real-print-maker-ledger-15m-venue-normal.md`._
- **15M penny/improve-one-tick seat:** an early offline/live positive shape was
  superseded by a negative lifetime result across the tested configuration;
  do not re-arm that configuration.  _Source:
  `corpus/the-15m-penny-seat-is-cap-limited-not-edge-limited.md`._
- **15M taker/forecast families:** unfolded continuation, sub-50/settlement
  takers, external-spot latency takers, and the Jev/LLM directional forecaster
  are closed on post-toll economics or information, not on a missing feature.
  _Sources: `corpus/topics-closed-branches.md`,
  `corpus/thin-altcoin-spot-gap-is-a-one-minute-snapshot-edge.md`._
- **Wings, hourly ladder, perps and token-price markets:** crypto/altcoin/FX/
  commodity wings have no deployable cell; hourly-ladder variance was not
  identified; all tested perps failed toll × notional-cap arithmetic; token-price
  products were delisted.  _Source: `corpus/topics-closed-branches.md`._
- **Listing-minute and cross-venue copy:** the listing book is empty for too
  long absent external fair value; copying PM wallet direction into Kalshi
  failed because the leader's price, not direction, supplied the edge.  _Sources:
  `corpus/be-first-at-listing-has-nothing-to-be-first-to.md`,
  `corpus/polymarket-15m-copy-to-kalshi-closed.md`._
- **Sports directional taker and broad in-play MM:** parent-lead directional
  taker did not clear fees on our executable design; prior in-play MM arms are
  closed.  Do not turn the surviving parent-level forecast result into an
  offline execution claim without forward depth.  _Source:
  `corpus/sports-parent-lead-taker-closed-level-not-move.md`._
- **Weather/yield/vol/LIP:** weather scalps, station-siting, DeFi carry,
  IBIT/crypto-vol and liquidity-incentive trading are closed.  _Source:
  `corpus/topics-closed-branches.md`._

## Live / open bets

- **Thin-alt spot gap:** the operator-owned Kalshi `altspot` live runner is
  down; its successor `altlive-dry` is running on `rustmaker` in DRY mode
  through 2026-11-01T08:30Z.  The frozen question is whether a correctly chosen
  lead-venue fair value predicts the Kalshi book; Coinbase was rejected as the
  fair for the currently tested alts.  Decision date: 2026-11-08.  _Source:
  `fleet.md`._
- **PM US/Kalshi paired-book preflight:** `kap-poly15-ws` is a tape-only
  recorder on `rustmaker` through 2026-11-01T08:02Z.  It is a shared-index,
  post-fee executable-gap check, not a license for the already-closed generic
  15M taker-taker route.  Score locally after completion.  _Sources:
  `fleet.md`, `repo/desks/polymarket/NOTEBOOK.md`._
- **Forward-only candidates:** book-imbalance cancellation remains unadjudicable
  until a causal depth tape exists; sports parent-level versus child-mid is
  likewise forward-only.  Neither is an armed Kalshi strategy.  _Sources:
  `corpus/kalshi-commodity-latency-branch-closed.md`,
  `corpus/sports-parent-lead-taker-closed-level-not-move.md`._

## Verdicts

### 2026-11-01 — Seed verdict: no new Kalshi arm

**Measured record:** the active Kalshi state is one DRY thin-alt experiment and
one tape-only paired-book preflight; the broader 15M crypto maker/taker families
are already closed in the corpus.  **Inference:** neither active process
overrides those closures because neither has yet scored our completed fill set.
**Conclusion:** keep the runners non-armed, preserve forward data, and require a
new preregistration with a genuinely new instrument/mechanism before reopening a
closed family.  _Sources: `fleet.md`, `corpus/topics-closed-branches.md`,
`priors.md`._

## Corpus pointers

- **Start before any 15M proposal:** `corpus/MEMORY.md`,
  `corpus/topics-15m-crypto-seat.md`, `corpus/topics-closed-branches.md`.
- **Before a maker/quoter change:** `corpus/topics-maker-seat-mechanics.md`,
  `corpus/topics-latency-and-feed-races.md`,
  `corpus/topics-live-arming-and-plumbing.md`.
- **Before parsing, collecting, or backtesting:** `corpus/topics-venue-facts.md`,
  `corpus/kalshi-venue-mechanics.md`,
  `corpus/topics-estimator-and-inference-traps.md`.
- **Current code/operations:** `~/proj/rustmaker/FINDINGS.md`,
  `~/proj/rustmaker/PREREG_altspot_tilt_live_20261006.md`,
  `~/proj/kap/FINDINGS_forward_l2_tape_20261023.md`, and staged `fleet.md`.
