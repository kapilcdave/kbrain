# Dead ends

_(curator maintains; last compacted 2026-11-01 in pass #69, which supersedes
compaction #62 and folds in the new results #57, #65, #66, and the late #49.
Pass #63 added no new dead ends. The cross-venue-news-lead-lag block is
updated with the measured structural findings (#57) and the audit-confirmed
park (#65). Engineer #58 and researcher #68 are still in flight — no results
inferred (status only). Prior failure classes live in
[lessons/negative-results.md](../../lessons/negative-results.md).)._

## Blocked, not falsified

- **2026-11-01 — `spx-opex-gamma-pin-unwind`** — Backtest #56 returned
  blocked: the required primary dataset `equity-options-cboe-chains-forward`
  is absent from data/ (only crypto/Kalshi/Polymarket datasets exist), and the
  confirmatory holdout is prospective — it opens 2026-11-23, after the
  2026-10-31 freeze, so it cannot be backtested at freeze time. All five
  required sources are public and unauthenticated: CBOE delayed-quotes SPY
  chain snapshots at 10:35/12:35/14:35/15:35/15:50 ET with receipt timestamps
  (2026-11-02..2027-04-30, ext. to 2027-07-31), Yahoo 1-min SPY bars 15:30–
  16:05 ET + 12:35, FRED DGS3MO + EFFR, a pinned XNYS calendar, Stooq SPY
  closes. *Next:* engineer collectors stage the datasets, let the holdout
  accrue, read once at the trigger (#47, #56).
- **2026-11-01 — `treasury-auction-concession-reversal`** — backtest #60
  returned blocked: none of the prereg datasets exist in data/ (only
  crypto-perps, Kalshi, Polymarket datasets). Needed, all public: Treasury
  Fiscal Data `auctions_query` results (~478 10Y/30Y nominal rows,
  2004-01-01..2026-10-29) plus a TreasuryDirect cross-check, FRED CMT yields
  (DGS2/5/7/10/20/30 + EFFR/SOFR), Treasury daily par-yield CSVs, Yahoo +
  Stooq closes for IEF/TLT/IEI/SHY, a pinned XNYS calendar, and FOMC/CPI/
  employment release dates. Per the prereg the backtester may not fetch or
  substitute synthetic data. *Next:* an engineer data stage lands the inputs,
  then the backtest reruns; exact endpoints/ranges in task-60/data-requirements.md
  (#45, #60).
- **2026-10-31 — `football-longshot-bias-pinnacle-devig`** — The required
  football-data.co.uk close-odds CSVs for the preregistered leagues and
  seasons are not staged; no metrics were computed (#41). A resumable
  collector for the exact prereg universe (preserving Pinnacle/B365 closing
  columns) is written (#42) and queued as a background job; public static CSVs,
  no key needed. *Next:* start the job, stage the CSVs; dev split first,
  holdout 2023/24–2025/26 untouched until locked (#17, #42, #54).
- **2026-11-01 — `fomc-preannouncement-drift-regime`** — Prereg frozen, but no
  required dataset exists in data/: no SPY daily OHLCV (plus an SPY
  verification gate), FOMC meeting calendar, VIX close, or CPI release
  schedule (#44). Per prereg §10(a) no analysis ran and no metrics were
  fabricated; absent intraday 13:45 ET bars block only secondary endpoint S1
  under §10(b). The full list of endpoints, fields, and ranges is in task
  #44's DATA_REQUEST.md. Measured update (2026-11-01, #49): the engineer is
  done — both resumable stdlib collectors are written, mock-tested, and
  submitted: a blocking historical snapshot (SPY Stooq daily + Yahoo
  cross-check/actions, FRED VIXCLS, Fed FOMC calendars with 2020-03
  emergency dates separated, BLS CPI schedule) and a non-blocking forward
  appender for the 2026-12-08/09 and 2027 holdout. They are not
  network-tested; check the first run log. *Inference:* the drift may have
  decayed post-publication regardless. *Next:* run the two #49 jobs, stage
  the CSVs, then run the frozen study (#44, #49).
- **2026-11-01 — `cross-venue-news-lead-lag` — parked/terminal (measured,
  #57; audit-CONFIRMED, #65)** — The frozen prereg requires historical
  second-level L2 books over [t0−30s, t0+300s] for anchors
  2024-12-01..2026-09-30 with causal received-time validation; neither venue
  provides the raw material. Measured by #57: Kalshi
  `GET /markets/{ticker}/orderbook` is the live book only and
  `orderbook_delta` WS is not archived (historical tiers are paid trade data,
  not books); Polymarket CLOB /book is current-only and /prices-history is a
  1-minute grid; public trade prints carry second-level timestamps and no
  causal received-at records, so pre-event 1s mid, follower best ask, and the
  top-5 depth walk cannot be reconstructed for past anchors. Skeptic #65
  CONFIRMED: the supplied metadata/hourly-price files cannot support the
  mid-price signal or taker-leg pricing; no fixable defect exists in the
  park; changing the window or execution design requires a new
  preregistration. #57 staged the maximum obtainable pieces as tested stdlib
  collectors (anchors; trades+1m candles/prices; forward 1-second book/trade
  capture) reusing the existing datasets. *Measured:* none — no edge metrics
  computed. *Next:* chief re-freeze decision — prospectively re-freeze and
  run collect_forward_books.py around the next scheduled anchor (~2026-11-12
  CPI), or re-freeze a trade-print-only design that accepts second-level
  timestamps (#57, #65, #66).
- **2026-10-31 — `dex-cex-stale-pool-lag`** — No Binance 1-second/aggTrade or
  Uniswap v3 burn-in/holdout archives (#33). The preregistered burn-in needs
  The Graph or Dune, which require API keys; public Ethereum RPC cannot supply
  the preregistered historical subgraph TVL or indexed pool universe, and a
  Binance-only substitute cannot build the frozen manifest (#34). An audit
  CONFIRMED the park: no data or implementation error established a false
  negative, and the 2026-09-01..2026-10-31 holdout must stay unread until the
  universe manifest is fixed (#39). This is the only blocked hypothesis whose
  data needs keys or authorization. *Next:* the source owner provides the
  indexed 2026-07-01..2026-08-31 burn-in data or authorizes a newly
  preregistered RPC-derived TVL method (#34, #39).
- **2026-10-31 — `deribit-weekend-iv-theta-gap`** — No Deribit options or
  Binance spot dataset; historical Deribit public trades are transaction
  prints, not archived executable quotes (#35, #36) — a structural gap no key
  fixes; past-weekend backtests must use the preregistered conservative
  slippage sensitivity. History and 14-day forward book jobs are written
  (#36) and queued. *Next:* run the history job first (past four weekends of
  prints), then the forward depth-20 book job (#35, #36, #54).
- **2026-10-31 — `kalshi-sports-wide-quote-mm`** — The trade tape, market
  metadata, and event timestamps are now downloading from the public Kalshi
  Trade API via the harness collector (6.4 GB of markets written, tape to
  follow, #54). The remaining gap is an archived dated fee schedule. An audit
  confirmed the park and found no code or design defect (#3, #4, #7). *Next:*
  after the tape job completes, validate it, archive the public Kalshi fee
  schedule with a date, then rerun the frozen prereg (#3, #7, #54).
- **2026-11-01 — `polymarket-negrisk-overround`** — Needs full-book depth per
  outcome every 5 minutes for 14 days. The only available data is hourly
  mid-price history, which the prereg forbids for executability claims (#11,
  #23). The collector (#24) is sound but queued with job 8's max_s=14400 s, so
  the 14-day run would be SIGKILLed at 4 h, marked failed, and the hypothesis
  parked after two retries — measured in #55 from jobs.py and kb.db.
  *Next:* while queued, `UPDATE jobs SET max_s=1300000 WHERE id=8`; start it
  now (every idle day delays the first possible read by a day), confirm at
  least 30 holdout events, then rerun (#23, #24, #55).
- **2026-11-01 — `perp-liquidation-cascade-reversion`** — No Binance USDⓈ-M or
  supporting record dataset exists; the required forward window is
  2026-11-08..2027-02-14 UTC, fully specified in task #37's missing_data.json.
  No holdout outcomes were inspected and no metrics computed (#37). The #55
  audit measured the collector (#38) runnable and key-free but self-limited to
  3 h 50 m per launch with no relaunch scheduler in the harness — continuous
  coverage needs a one-time config change. *Next:* before 2026-11-08, set
  `KB_MAX_RUNTIME_S=0` in the kb-runner environment and
  `UPDATE jobs SET max_s=1300000 WHERE id=18`, then run the frozen forward
  study at the trigger (#14, #37, #55).
- **2026-11-01 — `kalshi-cpi-combo-frechet`** — The holdout does not exist yet:
  the first eight post-freeze CPI releases run 2026-12-10..2027-07-14. The #55
  audit measured the three collectors (jobs 5–7) fail at startup under the
  harness launcher (`python3 -I` → `import kcommon` ModuleNotFoundError);
  kcommon itself works. *Next:* prepend
  `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` before the
  import in each of the three scripts, set `blocking=1` on jobs 5–7; then run
  refs/quotes daily, books in the 02:25–08:25 ET release-morning windows
  (#21, #22, #55).
- **2026-11-01 — `kalshi-settlement-source-lag`** — No catalogued Kalshi
  weather, TWC, IEM ASOS, or weather order-book data; the confirmatory holdout
  (2026-11-01..2026-12-31) opened and the forward collector is the single most
  urgent queued job. The #55 audit measured jobs 14–15 runnable and
  env-complete (no key, resumable, skip-archived on requeue), but stuck 14th in
  the id-ordered queue behind two long jobs. *Next:* raise limits.max_jobs 2→4
  (hot-reloaded) or bump job 15 ahead today; dev backfill flows in behind.
  Read the holdout once under the frozen rules (#13, #28, #30, #55).

## Data-source gaps

- **2026-11-01 — Prediction-market historical L2 books (measured, #57;
  audit-CONFIRMED, #65)** — Neither Kalshi nor Polymarket offers historical
  order-book snapshots or causal received-time records; only the live book,
  paid historical trade tiers, second-precision prints, and 1m/hourly price
  grids exist. Executable-quote history is forward-only; the three #57
  collectors stage anchors, the max-obtainable trades snapshot, and a
  forward 1-second capture for a re-frozen study (#57, #65).
- **2026-10-31 — Collector scheduling bottleneck (measured, #54)** — Background
  collectors are capped at 2 concurrent; both slots are held by the long
  Kalshi and Hyperliquid jobs, so 17 queued public collectors (all time-gated
  forward archives among them) cannot start until slots free. No key is
  missing anywhere; ordering and slots are the constraint.
- **2026-10-31 — Uniswap v3 historical TVL/universe** — Historical subgraph
  pool TVL and an indexed pool universe are only available via keyed The Graph
  or Dune; unauthenticated RPC yields raw logs and receipts but not the
  preregistered TVL calculation (#34, #39). The only needs-key gap.
- **2026-10-31 — Deribit historical quotes** — Deribit public history exposes
  trade prints, not archived bid/ask snapshots; executable quotes are
  prospective only (14-day forward archive queued in #36).
- **2026-10-31 — Binance USDⓈ-M forward streams** — No archive for the frozen
  perp-reversion window 2026-11-08..2027-02-14 (#37); forward collector
  written and queued (#38, #54).
- **2026-10-31 — football-data.co.uk CSVs** — None staged locally against the
  preregistered league/season list; the #42 collector is queued unrun
  (#41, #42, #54).
- **2026-11-01 — FOMC/S&P/VIX/CPI event study inputs** — Nothing in the
  catalog matches SPY OHLCV, FOMC calendars, VIX, or CPI schedules; the #49
  collectors (written and submitted, datasets pending) cover the daily
  snapshot 2000-01-01..2026-10-31 and a forward refresh for the 2026-12/2027
  holdout (#44, #49, #66).
- **2026-10-31 — Kalshi fee schedule archive** — No dated archived copy of the
  Kalshi fee schedule; needed to unpark kalshi-sports-wide-quote-mm once the
  tape completes (#3, #7, #54).
- **2026-10-31 — crypto liquidations** — No public unauthenticated liquidation
  history is available; use open-interest drops as a proxy (#19).
- **2026-10-31 — Polymarket depth** — `polymarket-markets-prices` holds Gamma
  metadata and hourly mid prices, not full books, so it cannot support
  executable-bound tests; books require forward collection (#23, #24).
- **2026-10-31 — Kalshi weather settlement** — No Kalshi weather series, TWC
  weather.com/kalshi feed, IEM ASOS archive, or weather order books in the
  catalog; collectors are queued (#28, #30, #54).
- **2026-11-01 — Treasury markets history** — no auction results, CMT/par
  yields, or IEF/TLT/IEI/SHY closes exist in the catalog for the frozen
  backtest; exact public sources and 2004–2026 ranges are in
  task-60/data-requirements.md (#60).
- **2026-10-31 — equity option history** — No public unauthenticated historical
  equity option chains; equity data is forward-only via CBOE delayed quotes
  (#29). The #56 report pins the forward snapshot schedule (10:35/12:35/14:35/
  15:35/15:50 ET from 2026-11-02) (#56).

## Rejected

- None through #68. No metric-based rejection occurred.

## Prior dead ends

- Carried in [Negative Results](../../lessons/negative-results.md) rather than
  duplicated here. The four previously falsified families named in task #5 were
  rejected before this run; their source evidence is outside tasks #1–#41.
