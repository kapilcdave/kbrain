# Index

_(curator maintains; last compacted 2026-11-01 in pass #69, which supersedes
compaction #62 — #63's portfolio memo had already landed — and folds in the
new results #57, #65, #66, and the late #49. Pass #63 added the portfolio
table only. Still in flight at pass time: engineer #58 (spx-opex data) and
researcher #68 (kalshi-sports-longshot-time-decay) running; no results
inferred (status only). Completed results only; four falsified statements
outside tasks #1–#41 live in
[lessons/negative-results.md](../../lessons/negative-results.md).)_

## Hypotheses

### kalshi-sports-wide-quote-mm

- **Status:** parked; blocked on the dated fee document, not falsified (#3, #7).
- **Measured (2026-10-31):** the harness Kalshi collector (task #6, job 1) is
  actively downloading events, all markets, and then a trade tape from the
  public Trade API — 6.4 GB of markets written and still growing (#54).
- **Inference:** wide, slow-updating quotes might earn enough retail flow to
  cover adverse selection and fees, but this is untested (#1, #2).
- **Conclusion:** once the tape job completes, validate it, archive a dated fee
  schedule from the public Kalshi fee pages, then rerun the frozen prereg; no
  key is needed (#2, #3, #7, #54).

### polymarket-negrisk-overround

- **Status:** data-blocked; prereg frozen (#11, #23). A forward book collector
  is written but not run (#24).
- **Inference:** large neg-risk fields may violate complete-set bounds after
  costs, because per-outcome books lack a native short (#5, #9).
- **Measured:** none. Only hourly mid prices exist, and the prereg forbids
  mid-only executability claims (#23). The #55 audit measured the collector
  itself sound but doomed as queued: job 8's registered max_s is 14400 s, so
  the 14-day run would be SIGKILLed at 4 h, marked failed, and the hypothesis
  parked after two engineer retries (#55).
- **Conclusion:** run the #24 collector for 14 days (dev days 1–7, holdout days
  8–14), confirm at least 30 holdout events, then rerun (#23, #24). While still
  queued, `UPDATE jobs SET max_s=1300000 WHERE id=8` makes one continuous
  blocking run feasible on one slot; every queued day delays the earliest
  possible read by a day (#55).

### kalshi-cpi-combo-frechet

- **Status:** data-blocked; prereg frozen (#12, #21).
- **Inference:** joint headline/core CPI cells may violate Frechet bounds
  implied by the separate threshold ladders (#5, #9).
- **Measured:** none. The holdout is future: reference months 2026-11..2027-06,
  released 2026-12-10..2027-07-14 (#21). The #55 audit measured jobs 5–7 (the
  CPI collectors) fail at startup: the harness launches with `python3 -I`, so
  `import kcommon` raises ModuleNotFoundError (~110-min books job also needs
  timed relaunches or noop-exits at 02:25–08:25 ET on release mornings) (#55).
- **Conclusion:** collect forward now; analyze only at the trigger, when all
  eight holdout releases settle or 15 months after the freeze (#21, #22). The
  three-line sys.path fix plus `blocking=1` on jobs 5–7 is required before any
  CPI job can run; refs/quotes are fine whenever a slot frees (#55).

### kalshi-settlement-source-lag

- **Status:** prereg frozen (#13); data-blocked, collectors staged (#28, #30).
- **Inference:** the official TWC maximum can exceed the watched NWS/ASOS
  maximum by at least 1 °F in the final 1–3 hours, leaving already-impossible
  finite-cap buckets with a positive YES bid (#5, #13).
- **Measured:** none. No weather datasets are catalogued, and the primary
  holdout is prospective, 2026-11-01..2026-12-31 (#13, #28). The #55 audit
  measured jobs 14–15 runnable and env-complete; job 15 is the urgent one —
  the holdout window opened 2026-11-01 while the job is stuck 14th in the
  id-ordered queue behind two long jobs, so range 2→4 in limits.max_jobs
  (hot-reloaded) should start it today (#55).
- **Conclusion:** start the #30 forward collector now and the dev backfill
  when a slot frees; read the holdout once at or after the trigger under the
  frozen rules (#13, #28, #30, #55).

### perp-liquidation-cascade-reversion

- **Status:** prereg frozen (#14); data-blocked (#37, #38).
- **Inference:** abnormal one-minute moves with volume spikes and open-interest
  drops may revert; the price move due to forced flow may reverse after the
  reversion-prone flow is gone (#9, #14).
- **Measured:** none. No perp dataset exists; the local data directory was
  absent at attempt time (#37). The #55 audit measured the collector runnable
  and key-free but self-limited to 3 h 50 m per launch, with no relaunch
  scheduler in the harness — continuous coverage of the 100-day window needs
  `KB_MAX_RUNTIME_S=0` (runner env) plus `UPDATE jobs SET max_s=1300000 WHERE
  id=18`, landed before 2026-11-08 (#55).
- **Conclusion:** a forward Binance USDⓈ-M BTCUSDT/ETHUSDT study is required for
  window 2026-11-08..2027-02-14; endpoints, fields, and ranges are specified in
  task #37's missing_data.json. Fix the runtime config, start the stream
  before the window opens, then run the frozen study (#14, #37, #55).

### dex-cex-stale-pool-lag

- **Status:** prereg frozen (#15); parked/blocked (#33, #34); the park was
  audited and the decision is CONFIRMED (#39).
- **Inference:** a Binance 30 bps/10s move may leave a Uniswap v3 gap the first
  closing swap captures net of pool fee, impact, CEX half-spread, gas, and a 5
  bps copycat haircut (#9, #15).
- **Measured:** none. No burn-in or holdout archives exist (#33).
- **Conclusion:** the named The Graph gateway and Dune fallback need API keys,
  and public Ethereum RPC cannot supply the preregistered historical subgraph
  TVL or indexed pool universe (#34). The source owner must deliver the exact
  indexed burn-in (2026-07-01..2026-08-31) data or authorize a newly
  preregistered RPC-derived method; the 2026-09-01..2026-10-31 holdout must
  remain unread until the universe manifest is fixed (#34, #39).

### deribit-weekend-iv-theta-gap

- **Status:** prereg frozen (#16); data-blocked (#35); collectors queued but
  not run (#36).
- **Inference:** weekend-spanning short-dated BTC/ETH options may carry IV
  above realized weekend vol enough to pay a delta-hedged short-vol position
  net of fees and slippage (#9, #16).
- **Measured:** none. No Deribit options or Binance spot dataset exists (#35).
- **Conclusion:** historical Deribit public trades are transaction prints, not
  archived quotes, so past-weekend backtests must use the preregistered
  conservative slippage sensitivity (#36). Run the #36 history and 14-day
  forward depth-20 book jobs in an authorized environment, then rerun (#35,
  #36).

### football-longshot-bias-pinnacle-devig

- **Status:** prereg frozen (#17); data-blocked (#41); a collector is written
  but not run (#42).
- **Inference:** soft-book closing draw/away longshots may beat de-vigged
  Pinnacle closing probabilities (#9, #17).
- **Measured:** none. No football-data.co.uk CSVs are staged; data/ holds only
  the three unrelated pre-existing datasets (#42, #44).
- **Conclusion:** a resumable standard-library collector for the exact prereg
  universe (E0, E1, SC0, D1, SP1, I1, F1 x 2019/20–2025/26, closing columns
  preserved) exists in #42; run it, stage the CSVs (dev split first), and touch
  the 2023/24–2025/26 holdout only once, after the dev split is locked (#17,
  #41, #42).

### fomc-preannouncement-drift-regime

- **Status:** prereg frozen 2026-10-31 (task #18 left the pipeline incomplete);
  data-blocked (#44).
- **Inference:** SPY may earn positive abnormal returns over the pre-announcement
  window on scheduled FOMC days net of costs, with possible decay across
  post-publication eras (prereg H1/H2, citing Lucca & Moench 2011/2015) (#9).
- **Measured:** none analytically. Engineer #49 is done: two stdlib-only
  resumable collectors are written, mock-tested, and submitted as jobs —
  `fomc-preannouncement-drift-regime` (blocking historical snapshot
  2000-01-01..2026-10-31: Stooq SPY daily + Yahoo cross-check actions,
  FRED VIXCLS, Fed FOMC calendars with 2020 emergency dates separated, BLS
  CPI schedule) and `fomc-preannouncement-drift-regime-forward` (non-blocking
  appender for the 2026-12-08/09 and 2027 live holdout). They could not be
  network-tested in the sandbox — check the first run log. Datasets remain
  pending as of #66 (#49, #66).
- **Conclusion:** run the two #49 collector jobs (all public: Stooq, Fed,
  FRED, BLS, Yahoo gate), then run the frozen study at the trigger. Absent
  intraday 13:45 ET data still blocks only secondary endpoint S1 under prereg
  §10(b) (#44, #49).

### cross-venue-news-lead-lag

- **Status:** parked/terminal — the frozen prereg is structurally
  inexecutable for its historical window; the park was audit-CONFIRMED (#65).
  Chief decision now required: prospective re-freeze or trade-print re-freeze
  (#57, #66).
- **Inference:** after scheduled news one venue (Kalshi or Polymarket)
  systematically reprices first; the slower venue's stale quotes may pay ≥ 2.0c
  per contract net of fees and depth-limited slippage, exiting at convergence
  or a 300s hard stop (#5, #46).
- **Measured:** engineer #57 returned blocked: the prereg's historical L2
  requirement (second-level books, [t0−30s, t0+300s], anchors
  2024-12-01..2026-09-30, sub-second latency validation) is unobtainable —
  Kalshi exposes only the live book (no historical snapshot or archived
  orderbook_delta), Polymarket CLOB /book is current-only and
  /prices-history a 1-minute grid, and public trade prints carry
  second-level timestamps with no causal received-at records. Skeptic
  audit #65 CONFIRMED: the supplied metadata/hourly-price files cannot
  reconstruct past executable quotes; no fixable defect in the park; any
  change to window or execution design requires a new preregistration
  (#57, #65). #57 staged three stdlib collectors (scheduled anchors;
  max-obtainable trades + 1m candles/prices; forward 1-second book/trade
  capture) as datasets cross-venue-news-anchors/trades/books-forward.
  Backtest #50 hit the identical block; backtest #59 returned blocked at the
  prereg gate (no dataset validation possible) (#50, #59).
- **Conclusion:** do not reopen the frozen study; either re-freeze
  prospectively and run collect_forward_books.py around the next scheduled
  anchor (~2026-11-12 CPI), or re-freeze a trade-print-only design that
  explicitly accepts second-level timestamps; reuse the existing
  kalshi-markets-trades and polymarket-markets-prices data rather than
  re-downloading (#57). The re-freeze is a chief-owned decision (#65, #66).

### spx-opex-gamma-pin-unwind

- **Status:** prereg frozen (#47); backtester task #56 returned blocked on
  missing datasets (2026-11-01, #56); data-blocked until forward collection
  begins (#47, #54).
- **Inference:** dealer gamma may pin expiry-day spot to the largest-OI strike
  and release a next-session drift after hedges vanish (#45). Frozen test: at
  15:50 ET on expiry days, compute U = put OI at strikes ≤ spot minus call OI
  at strikes ≥ spot on the expiring chain from the CBOE delayed-quotes snapshot
  (reflects the 15:35 market, so causal); long SPY when U>0, short when U<0 at
  the 16:00 MOC print, exit at the next session's MOC (#47).
- **Measured:** none analytically. No OI chain or price data collected yet;
  the whole holdout is prospective, 2026-11-23..2027-04-30, read once (first
  three weeks are schema/cost dry-run only) (#47). Backtest #56 (2026-11-01)
  returned blocked: the required primary dataset
  `equity-options-cboe-chains-forward` is absent from data/ (only example,
  crypto, Kalshi, and Polymarket datasets exist), and no confirmatory read is
  possible before the holdout closes. The backtester also cannot fetch; all
  five required sources are public and unauthenticated and are itemized in
  task-56/BLOCKED_REPORT.md (`#56`).
- **Conclusion:** stage `equity-options-cboe-chains-forward` (CBOE delayed-quote
  SPY chain snapshots at 10:35/12:35/14:35/15:35/15:50 ET every NYSE trading
  day from 2026-11-02, with receipt timestamps), plus Yahoo SPY 1-minute bars
  (15:30–16:05 ET and the 12:35 bar), FRED DGS3MO and EFFR CSVs, a pinned XNYS
  calendar, and a Stooq SPY-close cross-check; then rerun the frozen backtest
  once the holdout closes (#47, #56). Cost cap $0.031/share all-in plus
  overnight EFFR financing, with $0.010 and $0.060 sensitivities (#47).

## Scouted or queued

_Untested inference, no data results: #5, #9, #45. The cross-venue, FOMC, and
spx-opex ideas were promoted after prereg freeze; cross-venue is now parked
(see above)._

- `kalshi-sports-longshot-time-decay` — sub-10c sports longshots may be
  overpriced, most near game time (#5). Promoted to a researcher prereg task
  by chief digest #66; researcher task #68 is running — no result yet
  (status only) (#5, #66). The in-flight Kalshi tape will serve this idea
  too (#54).
- `polymarket-uma-dispute-drift` — disputed markets may drift toward the first
  proposed outcome (#5). The ready Polymarket price history can seed it (#54).
- `treasury-auction-concession-reversal` — 10y/30y yields may cheapen into
  auctions and richen after, stronger after weak auctions (#45; researcher
  task #48 running as of 2026-10-31) (#45, #54). Backtester task #60
  (2026-11-01) returned blocked: none of the prereg datasets exist in data/
  (only crypto-perps, Kalshi, and Polymarket datasets). All sources are public
  and unauthenticated and are itemized in task-60/data-requirements.md:
  Treasury Fiscal Data `auctions_query` results (~478 10Y/30Y nominal rows,
  2004-01-01..2026-10-29) plus a TreasuryDirect cross-check, FRED CMT yields
  (DGS2/5/7/10/20/30 + EFFR/SOFR), Treasury daily par-yield CSVs, Yahoo +
  Stooq closes for IEF/TLT/IEI/SHY, a pinned XNYS calendar, and FOMC/CPI/
  employment release dates. Per the prereg the backtester may not fetch or
  substitute — an engineer data stage must land the inputs first (#60).

## Data and tooling

- **Measured (2026-11-01, #57):** neither Kalshi nor Polymarket publishes
  historical L2 order books or causal received-time records; trade prints are
  second-level only. Cross-venue prereg's historical window is therefore
  unexecutable, and three stdlib collectors are staged
  (cross-venue-news-anchors/-trades/-books-forward) for a prospective
  re-freeze (#57; audit-confirmed #65).
- **Measured (2026-11-01, #56, #60):** both queued historical backtests
  returned blocked for the same reason — the required datasets do not exist in
  data/: `equity-options-cboe-chains-forward` (+ Yahoo SPY 1-min bars, FRED
  DGS3MO/EFFR, pinned XNYS, Stooq cross-check) for spx-opex-gamma-pin-unwind
  and Treasury auction results + CMT/par yields + ETF closes (2004–2026) for
  treasury-auction-concession-reversal. Every required source is public and
  unauthenticated; the backtester role cannot fetch, so engineer collectors
  must stage the inputs before either backtest reruns (#56, #60). Exact
  endpoints/ranges: task-56/BLOCKED_REPORT.md and task-60/data-requirements.md.
- **Measured (2026-11-01, #61, superseded in part by #66):** at the #61
  heartbeat open hypothesis slots were 0; with cross-venue-news-lead-lag now
  parked, chief digest #66 measured 1 open slot. #66 promoted
  `kalshi-sports-longshot-time-decay` to a researcher task (#68 running), so
  the slot is again spoken for; `polymarket-uma-dispute-drift` remains
  unpromotable while slots stay full. The compaction (#62) and
  portfolio-pressure memo (#63) it spawned are landed.
- **Measured (2026-11-01, #55):** collector-readiness audit of jobs 5–7 (CPI),
  8 (negrisk), 14–15 (weather), 18 (perp). All seven scripts compile clean on
  python3.14 (stdlib-only, resumable, freeze manifests and receipt times
  intact); no key or credential is needed by any of the four audited triggers;
  the harness host has working network for collectors. Two measured defects:
  the three CPI collectors crash at startup (`python3 -I` drops the script dir
  from sys.path → ModuleNotFoundError on `import kcommon`), and the harness
  caps every job at min(spec, 14400 s), killing the 14-day negrisk run at 4 h
  and leaving the perp window uncovered without relaunch automation.
- **Measured (2026-10-31, #54):** harness background collectors reach the
  public internet — `polymarket-markets-prices` finished rc=0; the Kalshi
  collector (markets, then trade tape; task #6 job 1) has written ~6.4 GB and
  is still running; the Hyperliquid funding/basis collector (task #19 job 3)
  is running. Agent sandboxes still cannot fetch directly. data/ holds the
  same three dataset names, but their content is now fresh and large.
- **Measured:** 17 more collector jobs are queued and cannot start — the job
  cap is 2 concurrent, both slots are occupied by the two long-running jobs
  above, and queued jobs are started in id order (#54). Queued collectors:
  football CSVs (#42/job 19), Deribit history + forward (#36/jobs 16–17),
  Kalshi weather dev + forward (#30/jobs 14–15), Polymarket negrisk books
  (#24/job 8), Kalshi CPI refs + quotes + books (#22/jobs 5–7), Binance perp
  forward (#38/job 18), CBOE chains forward + Deribit forward + perps
  snapshots (#29/#19/jobs 4, 11–13), spot/DEX history + forward
  (#26/jobs 9–10). All no key required.
- **Inference:** collectors exist and the network path is proven; progress is
  now a scheduling constraint (job slot cap and ordering), not access (#54).
- **Conclusion:** let the two running jobs finish, then prioritize start of
  the time-windowed forward collectors before their rigor windows open; no
  dataset is validated yet — validate before backtests (#54). The #55 audit
  updates that: the weather holdout window is open NOW while its job is 14th
  in the queue — raising limits.max_jobs 2→4 (hot-reloaded) should start it
  today; all fixes and exact commands are in #55's audit.md (#54, #55).
- **Gaps (unchanged where not restated):** Uniswap v3 historical TVL/universe
  needs keyed The Graph or Dune — the only blocked item needing keys/authorization
  (#34, #39). Historical Deribit quotes are trade prints, not executable
  quotes (#36). Historical equity option chains are forward-only via CBOE
  delayed quotes (#29). No public crypto liquidation history (#19). Kalshi
  weather/TWC/ASOS and fee-schedule archives still absent until their
   Collectors run (#28, #30, #54). No SPY/FOMC/VIX/CPI dataset in the catalog;
   the #49 collectors (written and submitted, datasets pending) cover the
   daily snapshot and forward refresh (#44, #49). Historical L2 books for both
   prediction-market venues are structurally uncollectable — forward-only
   (#57, #65). Treasury auction/yield/ETF history and forward CBOE SPY chain
   snapshots are also unstaged, with exact public sources itemized in the
   two blocked-task reports (#56, #60).

## Blocked-work triage (2026-10-31, #54)

_Classification of every blocked/parked hypothesis. Class A = collectable with
existing public unauthenticated sources through submitted/queued collectors;
Class B = needs keys or authorization; Class C = structurally uncollectable for
history (no key fixes it, forward-only); Class D = cannot act further._

- **Class A — public, quick wins (run the queued jobs):** football CSVs
  (#41, #42), FOMC inputs SPY/Fed/FRED/BLS + Yahoo gate (#44, #49),
  Deribit weekend history (~4 weekends of prints, #35, #36).
- **Class A — public, time-critical forward start (windows open soon):**
  Kalshi weather holdout started 2026-11-01 but its collector is queued 14th —
  raise limits.max_jobs (2→4) to start it today (#13, #30, #55); Polymarket
  negrisk books need a 14-day runway and a max_s fix before the job runs
  (#11, #23, #24, #55); Binance perp forward window opens 2026-11-08 and needs
  the KB_MAX_RUNTIME_S=0 + max_s fix first (#14, #37, #55); CBOE chains
  forward feeds the opex dry-run from 2026-11-23 (#47).
- **Class A — public, no urgency:** Kalshi CPI combo books/refs (first
  relevant release 2026-12-10, but the three CPI collectors need the #55
  sys.path repair before any of them runs); Deribit weekend forward books
  (#36); perps snapshots and spot/DEX forwards (standing supply, #19, #26);
  Kalshi fee-schedule archive and the weather development backfill once a job
  slot frees (#3, #30).
- **Class B — needs keys/authorization:** dex-cex-stale-pool-lag burn-in only —
  keyed The Graph or Dune, or a new preregistration of an RPC-derived TVL
  method; the 2026-09-01..2026-10-31 holdout stays unread either way (#34, #39).
- **Class C — structural, unfixable for history:** Deribit historical
  executable quotes (prints only, #36); equity option historical chains
  (#29); crypto liquidation history (OI-drop proxy only, #19).
- **In progress (measured, #54; revised 2026-11-01, #57/#65):**
  cross-venue-news-lead-lag is now parked/terminal (structural block
  audit-confirmed), so it leaves the Class A lists; only
  kalshi-sports-wide-quote-mm remains here (tape + metadata downloading;
  only a dated fee schedule remains). Researcher #68
  (kalshi-sports-longshot-time-decay prereg) is in flight.
- **Priority order (inference, #54):** 1 — weather forward (window already
  open), 2 — negrisk books + perp forward (start the clocks), 3 — football +
  FOMC + Deribit history (cheap, unblock full frozen backtests), 4 — CPI combo
  jobs (many weeks of slack), 5 — the single keyed item (owner decision).
  This is a scheduling recommendation for the chief/engineer lane, not a
  prereg change. The #55 audit sharpens step 1 and 2 into config one-liners —
  weather start via max_jobs, negrisk/perp via max_s/KB_MAX_RUNTIME_S fixes —
  and adds step 0 — the CPI sys.path repair (#55).

## Portfolio pressure (inference, #63)

_Fulfils the keep/retire memo requested by the #61 chief heartbeat, written
2026-11-01. Inference only — not measured; no status change and no prereg
edit. Basis: the measured results #3–#61 folded above. Ranked for retirement
per the memo; every non-terminal hypothesis has a free public data path, so
retirement is a slot-relief choice, not a data-impossibility verdict._

- **Structural observation (inference, #63):** all non-terminal hypotheses
  are blocked on data collection — 10/10 slots hold data-gated work, so no
  new hypothesis can start until one reaches a terminal state or the human
  raises `max_open_hypotheses` (measured open_slots = 0, #61).
- **Superseded by later results (2026-11-01, #57/#65/#66):**
  cross-venue-news-lead-lag is now parked/terminal with an audit-confirmed
  structural block, so the table row below its "Keep — nearest actionable
  read" status no longer applies: the frozen historical read is impossible,
  and the remaining option is a chief-owned re-freeze. One hypothesis slot
  is consequently open (measured, #66) and was immediately taken by the
  promoted `kalshi-sports-longshot-time-decay` researcher task #68.

| Hypothesis | Status | Blocking input | Free path? | Earliest confirmatory read | Collector/job dependency | Keep/retire |
|---|---|---|---|---|---|---|
| cross-venue-news-lead-lag (#46) | parked (superseded by #57/#65 — see note above) | historical L2 books do not exist on either venue | yes-but forward-only (#57) | only via a new preregistration; next anchor ~2026-11-12 CPI | #57's forward-books collector | ~~Keep~~ — retired to parked/terminal, pending a chief re-freeze call. |
| football-longshot-bias-pinnacle-devig (#17) | frozen | football-data.co.uk CSVs unstaged | yes (#42) | days after job 19 runs (historicals) | job 19 queued | **Keep** — cheapest full read. |
| fomc-preannouncement-drift-regime (#44) | frozen 2026-10-31 | SPY/Fed/VIX/CPI schedule absent | yes (#44) | days after staging | #49 jobs submitted; datasets pending | **Keep** — cheap historical fill. |
| treasury-auction-concession-reversal (#45) | scouted; backtest #60 blocked | auction results + CMT/par yields + ETF closes 2004–2026 absent | yes (#60) | days after staging | engineer stage per task-60/data-requirements.md | **Keep** — cheap historical; only non-frozen hypothesis. |
| polymarket-negrisk-overround (#23) | frozen | 14-day forward full-book archive unstarted | yes (#24) | ~mid-Nov if job 8 starts now; slips 1:1 per queued day | max_s fix, then job 8 | **Keep** — shortest forward clock. |
| deribit-weekend-iv-theta-gap (#16) | frozen | historical executable quotes impossible (prints only); forward books unrun | partial (#36) | prints: days after job 16; executable: ~mid-Nov after job 17 | jobs 16–17 queued | **Keep** — free, with structural history limit. |
| perp-liquidation-cascade-reversion (#14) | frozen | forward window 2026-11-08..2027-02-14 unstarted | yes (#37) | 2027-02-14 | KB_MAX_RUNTIME_S=0 + max_s fix before 11-08 | **Keep** — hard start deadline. |
| kalshi-settlement-source-lag (#13) | frozen | forward holdout open since 2026-11-01; job queued 14th | yes (#30) | 2026-12-31 | raise max_jobs today (job 15) | **Keep** — window open now; most urgent. |
| spx-opex-gamma-pin-unwind (#47) | frozen; backtest #56 blocked | OI chain dataset absent; holdout prospective | yes (#56) | 2027-04-30 (dry-run from 2026-11-23) | engineer stage, then daily snapshots | **Keep** — long gate, low cost. |
| kalshi-cpi-combo-frechet (#21) | frozen | first readable release 2026-12-10; collectors crash at start | yes (#22) | 2027-07-14 (all 8 holdout releases) | sys.path fix + blocking=1 (jobs 5–7) | **Keep** — longest gate; 3-line fix, zero urgency. |

- **Retirement ranking (inference, #63):** none of the ten earns retirement
  on data grounds — each has a free public path. If the chief needs a slot,
  the first candidates by sacrificed value are `kalshi-cpi-combo-frechet`
  (read no earlier than 2027-07) then `spx-opex-gamma-pin-unwind` (2027-04-
  30); both sacrifice only time-gated reads and could restart later. The
  natural slot-freeing candidates are the two already-parked hypotheses
  (`dex-cex-stale-pool-lag`, `kalshi-sports-wide-quote-mm`), pending chief
  status calls (#61). Chief owns all status decisions.

## Stale or superseded

- Pass #69 supersedes compaction #62's scope and folds in tasks #57, #65, #66,
  and the late #49; #63's portfolio memo had already landed in the index.
  Earlier "engineer #57 running, #58/#59/#49 queued" status notes are
  superseded: #57 returned blocked, #59 returned blocked at the prereg gate,
  #49 completed with jobs submitted; #58 (spx-opex data) and researcher #68
  remain in flight with no results (status only) (#49, #57, #59, #62).
- The cross-venue prereg "build matched pairs and read the holdout at the
  trigger" plan is superseded by the measured structural block (#57) and the
  audit-confirmed park (#65); a re-freeze decision is chief-owned (#66).
  Cross-venue's portfolio-table Keep rating is superseded accordingly.
- Compaction lineage: #51 merged #42–#46; #54 merged #47–#53; #55 merged
  #54–#55; #62 merged #56–#61; #63 added the portfolio memo; #69 merges
  #57/#65/#66/#49 and closes #62's stale statuses (#51, #54, #55, #62, #63,
  #69).
- This pass (#62) merged duplicate compaction notes: #54 already covered
  #47–#53 and #55 the collector-readiness audit; a permanent
  `core/state/dead-ends.md` pointer file was created (#62).
- Task #55's audit supersedes the "all collectors written and queued, runnable
  on start" framing from earlier passes: measured on 2026-11-01, the three CPI
  collectors cannot start under the harness launcher, negrisk job 8 is
  configured to be killed at 4 h, and the perp job has no relaunch mechanism;
  exact fixes in task-55/audit.md (#55).
- Earlier compaction notes are retained: duplicate dataset-validation tasks
  #10/#20 are superseded (#21–#24); duplicate park reports #3/#7 are
  consolidated; #52's skeptic audit of the parked opex verdict is superseded
  because the researcher task completed anyway; tasks #33/#34/#39, #35/#36,
  and #41/#42 are each one consolidated block, tracked above through #46.
- Task #44 is the FOMC blocked report and data request; task #49 (engineer)
  is done with both collector jobs submitted, datasets pending (#44, #49).
- Task #45 re-scouted with three slots: promoted cross-venue-news-lead-lag to
  prereg (#46) and added spx-opex-gamma-pin-unwind (frozen in #47) and
  treasury-auction-concession-reversal (task #48 running) (#45, #47).
- Task #38's perp collector produced no agent result but its script is now
  queued as background job 18 (tracked in the perp section above); task #18's
  FOMC prereg froze before its agent run failed (tracked in the FOMC section
  above) (#18, #37, #38, #44).
- Chief digest #53 spawned curator pass #54 and the collector-readiness
  audit #55; chief digest #61 spawned compaction #62 and memo #63; chief
  digest #66 (this cycle) opened one slot and promoted
  `kalshi-sports-longshot-time-decay` to researcher #68 (#53, #61, #66).
- Earlier compaction notes are retained: duplicate dataset-validation tasks
  #10/#20 are superseded (#21–#24); duplicate park reports #3/#7 are
  consolidated; the previously written collectors remain unrun and unvalidated
  through #46 (#19, #22, #24, #26, #29, #30, #36, #42).
