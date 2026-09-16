# DEX microcap strategy validation

Use this recipe when validating newly launched or thinly traded tokens on an
AMM/DEX. The goal is to measure the executable return distribution without
turning a marketing feed, display price, or pool count into fake evidence.

## Procedure

### 1. Freeze one chain and one accounting numeraire

Choose the chain before collection and keep the first experiment on that chain.
Record every position as `numeraire -> token -> numeraire` so token P&L is not
mixed with a simultaneous bet on the gas asset. Keep the gas asset as a separate
operating reserve and charge every unit spent to the experiment.

Do not pool chains into one base rate: launch mechanisms, token controls, fee
models, router coverage, and trader populations differ.

### 1b. Separate chain, router, pool, wallet, and funding rail

Name every layer before implementing execution:

```text
chain -> wallet/signer -> router -> underlying pool(s) -> accounting numeraire
```

A router is not a custodial account; fund the wallet, then let the router propose
a path across pools. A wallet advertising support for a chain does **not** prove
a particular dapp exposes that wallet as a connector. Verify the live connection
modal or integration API before telling the user that a wallet can sign through
a router, and test the exact public address as the proposed taker before funding.
For first live microprobes, prefer an explicitly supported wallet with manual
approval over auto-approval convenience.

Fund micro-wallets directly on the destination chain whenever possible. Compare
`source amount -> destination amount received`, including source-chain gas,
bridge fee, price impact, slippage, and wallet/aggregator fee; fixed bridge costs
can consume a micro-budget even when the destination chain is cheap. A good
sequence is to send the native gas asset first as both fee reserve and address
test, then send the accounting numeraire over the same chain. Never act on a
truncated address: copy the complete public key, validate its chain format, and
confirm it matches the configured destination exactly.

Distinguish exchange balance, available-to-trade balance, and available-to-send
balance before planning a withdrawal. Do not try to evade a settlement or
withdrawal hold by converting assets or bridging; the restriction commonly
follows the funded value rather than its ticker. Keep paper collection running
and wait for the source to authorize sending, or compare a genuinely independent
on-ramp by destination amount after all fees. For a one-time micro-wallet funding,
prefer a manual withdrawal over creating a broadly transfer-enabled API key.

### 2. Treat discovery as a candidate feed, never a quality signal

Label how names enter the universe. Paid profiles, boosts, trending lists, and
social activity carry selection effects; promotion spend is equally consistent
with organic demand and a funded rug.

Store the full discovery denominator, including rejected names. A report over
passers only cannot distinguish a good strategy from an increasingly permissive
screen.

### 3. Make the token mint the independent entity

Deduplicate all passing pools by token mint before counting candidates. Select a
pool by a frozen rule such as highest executable liquidity, but count the mint
once. Repeated polls, multiple pools, and multiple routes are observations of one
candidate, not independent bets.

For base-rate estimation, use the token's first qualifying observation as its
entry. Later polls belong to its price path. Otherwise long-lived tokens receive
more weight and future persistence leaks into the estimator.

Do not call repeated fresh round trips a position-return series. Freeze the
entry cost and the **exact raw token output** of the first successful audited buy
quote; on later polls quote only `that fixed token quantity -> numeraire`. Store
these liquidation marks separately from contemporaneous hypothetical round
trips. This preserves the position identity needed to measure intrawindow highs,
24-hour returns, and principal-withdrawal rules.

### 4. Apply a fail-closed market screen

Reject missing liquidity, volume, pair age, activity, or price data instead of
filling absent fields with zero or a permissive default. Use named rejection
reasons and retain all reasons, not only the first, so filter behavior is
auditable.

Useful exclusion dimensions are liquidity floor/ceiling, pair age, transactions
per interval, volume-to-liquidity churn, FDV-to-liquidity, and vertical price
spikes. These disqualify obvious bad pools; they do not predict returns.

### 5. Cross-check token controls against current chain state

Combine an indexed token provider with direct RPC state. Reject disagreement
rather than selecting the friendlier source; indexers can be stale and RPC
parsers can be incomplete.

On Solana, verify at minimum:

- mint and freeze authorities are disabled in both views;
- the mint owner is the expected classic Token or Token-2022 program;
- holder concentration clears a frozen threshold;
- Token-2022 transfer-fee, transfer-hook, permanent-delegate, and unknown
  extensions are rejected;
- metadata extensions are allowed only after checking their state, e.g. an
  immutable self-pointing metadata pointer and null metadata update authority.

An immutable mint is not proof against a dump: cluster top wallets by funding
source before treating apparent holder dispersion as independent ownership.

### 5b. Split the audit into SAFETY vs QUALITY gates so guesses do not starve the sample

An audit conflates two jobs. **Safety** rejections make a token uninvestable —
active mint/freeze authority, transfer HOOK (can block your sell), permanent
delegate, source disagreement, missing data (fail closed). **Quality**
rejections are unproven alpha guesses or measurable costs — holder-concentration
above a frozen threshold, transfer FEE (a cost, not a trap), holder count below
a floor. Hard-rejecting on the quality guesses **starves the base-rate study
before it can test whether those thresholds even matter**, which contradicts the
measure-before-you-filter discipline (see 2 and 10): you never observe what the
rejected population does, so you can never learn whether the guess was right.

Gate execution on **safety only**: quote and journal a safety-clean mint even
when it fails a quality guess, tagging it (e.g. `STUDY`) and keeping `passed`
false so it is never treated as vetted-safe. Safety failures still hard-reject
and never reach the quote stage. In one session this split lifted eligible
base-rate entries from 19 to 33 in a single collector run — the funnel had been
rejecting ~82% of candidates on thresholds that had never been validated. A
transfer FEE is quality (charge it as a cost per 6); a transfer HOOK is safety
(it can make the sell fail). Classify by whether the flag makes the token
uninvestable or merely worse, not by whether it is a Token-2022 extension.

When adding a `safety_rejections`/`safety_passed` field to the audit result,
grep the test tree for every hand-rolled construction of that result type before
running only one shard — mocks that build the dataclass positionally or omit the
new field fail on shards you did not run.

### 6. Measure the exact executable round trip

Never mark a thin token from a display price. Quote the intended buy size, feed
the **exact raw output amount** of that quote into the sell quote, and compute:

```text
instant_return = sell_output_numeraire / buy_input_numeraire - 1
hurdle_bps     = (1 - sell_output_numeraire / buy_input_numeraire) * 10_000
```

Keep amounts as integer base units through the calculation. This captures route,
pool fee, price impact, and router fee at the tested size. Do not subtract a
router fee again when the quoted output is already net of it.

Record both routes and every quoted fee field. A router may choose different
pools on the buy and sell, and the round-trip hurdle can move between successive
requests.

### 7. Distinguish a quote from a simulated or landed trade

A bidirectional quote proves route availability, not that the wallet can sell.
Before live promotion, build and decode both transactions, inspect every program,
account, signer, destination, setup/cleanup instruction, and minimum output, then
simulate from the intended wallet state.

Charge costs omitted by route output: signature and priority fees, account
creation/rent, tips, failed transactions, and gas-asset conversion. If the route
API offers both managed execution and raw instructions, compare **total
executable output** after platform fees; do not choose from the label “zero fee.”
Prefer raw instructions during safety development because they can be decoded
before signing.

Treat transaction construction and wallet-state simulation as separate gates.
An assembled-transaction endpoint may return a valid route but refuse to build
when the intended taker lacks input funds; record that as `blocked_by_wallet_state`,
not as “no route” or a simulated pass. Do not fund a wallet merely to unlock
simulation before the paper base rate clears its gate. Use the raw-instruction
path for structural inspection first, then perform wallet-specific simulation
only inside the explicitly funded microprobe phase.

### 8. Journal evidence append-only

One record per vetted mint observation should contain:

- timestamp and first-qualification timestamp;
- mint and selected pool;
- full market-screen result;
- indexed and RPC audit result;
- buy and sell raw amounts, minimum outputs, routes, fee fields, and hurdle;
- whether transaction build, decode, simulation, and landing were attempted;
- explicit nulls for unmeasured costs rather than assumed zeros.

Keep display-price discovery journals separate from executable-quote journals.
Never promote a display-price base rate as an executable strategy result.

Make broad collectors rate-limit-safe before scheduling them. Compute request
amplification explicitly: fixed discovery calls + batched audit calls + two
quotes per audit passer. Pace at the client boundary, honor `Retry-After` on
HTTP 429, use bounded backoff for transient errors, and never retry semantic
4xx failures. Isolate failures per mint so one bad quote cannot discard the
batch; checkpoint each completed mint before starting the next so a timeout
does not erase earlier work.

Run scheduled read-only collectors as deterministic scripts rather than agent
prompts. Use a nonblocking file lock to prevent overlap, a runtime bound shorter
than the scheduler's hard limit, local delivery for routine output, and an alert
channel only for failures. Verify the scheduler path with one manually triggered
run and read back both job state and journal growth before trusting the schedule.

### 9. Validate attention as a lead-lag mechanism, not a story

For assets whose price is driven by attention rather than fundamental value,
do not conclude that they are “not quantifiable.” Quantify the conversion path:

```text
attention arrives -> independent participants act -> liquidity/holders grow -> price absorbs it
```

When external social data is unavailable or too noisy, use **revealed on-chain
attention**: growth and acceleration in unique organic buyers, independent
traders, holder count, organic versus total volume, buy/sell imbalance, and
liquidity retention. Prefer rates and acceleration over levels; a high level may
mark saturation, while acceleration can identify an expanding cohort.

Fetch token information in one batch for all open paper positions at each
fixed-quantity mark timestamp. Normalize and journal top-level holder count,
organic score, liquidity, and price plus 5m/1h/6h/24h organic buy/sell volume,
organic/net buyer counts, trader counts, holder change, liquidity change, price
change, and volume change. Keep the executable liquidation mark when this
auxiliary endpoint fails: write an explicit null/error for the attention snapshot
rather than losing primary P&L evidence or silently filling missing fields with
zero.

Preregister the edge as a lead-lag claim: attention/conversion features must
predict later executable return after controlling for price already moved. A
feature that rises only after price is not an entry signal. Treat high mentions
or transaction counts without independent buyer conversion as manipulation-shaped,
not demand.

Separate collection cadences. Broad discovery and full audits may run slowly;
mark existing first-seen positions often enough to observe the proposed exit
path. Use a shared nonblocking lock so audit and mark jobs cannot contend for API
limits or append partial concurrent records. Repeated marks buy path resolution,
not sample size.

Make the counterparty explicit. In an attention-continuation trade, intended
profits come from later participants entering after broader adoption; intended
edge is earlier measurement of genuine conversion. Insiders distributing supply,
earlier bots, AMM fees, slippage, and vanishing liquidity are the opposing flow.
If no measured conversion process separates later buyers from distribution, stop.

### 10. Score independence and tail behavior before funding

Count unique token mints, not rows. Use chronological holdout and report median,
mean, worst outcomes, vanished/unsellable share, and concentration of profit in
the best token and day. Score vanished or unquotable tokens conservatively.

For “withdraw principal at 2x,” collect intrawindow executable sell quotes. A
24-hour endpoint cannot prove that a 2x exit was reachable, and applying the rule
to the terminal return is an upper bound rather than a backtest.

Optimise the whole payoff distribution, not win rate. State the break-even winner
magnitude implied by the loss rate and include complete-loss probability, right-
tail concentration, drawdown before peak, and ruin probability at the proposed
bankroll. A positive mean carried by one token is distribution evidence, not a
fundable edge.

A micro-budget with only a few positions cannot estimate a fat-tailed strategy.
Estimate the number of independent attempts required from the measured hit rate
and winner distribution before deciding whether the available bankroll can
express the strategy. Keep fee/gas reserve separate from risk capital; sending
funds to a wallet proves transfer plumbing, not strategy calibration.

### 10b. Run the leave-one-out flip test; it names where the leverage is

Regroup the interleaved marks journal into **per-mint chronological paths**
(each mint's fixed-quantity liquidation marks, sorted by observed-at) before any
distribution analysis. The journal is appended one row per live mint per run, so
raw rows are shuffled across mints and time; per-mint paths are the shape every
downside/exit question needs.

Then apply an exit rule to each path (see 10c) and run the **leave-one-out
sensitivity**: recompute the mean after dropping the single worst-outcome mint.
If dropping one rug flips the mean from negative to positive, the sample's sign
is set by one tail event, not by the median position — the honest read is "not
enough independent draws yet," and the median is the number to trust meanwhile.
This is the mirror of §10's "profit carried by one token" and is often the
sharper diagnostic, because the downside tail on these assets is a total loss.

The flip test also **names where the leverage is**. When entry features do not
separate winners from losers (the Cohen's d ~ 0 result these universes keep
producing) yet one catastrophic loss dominates the mean, the edge cannot come
from picking winners — it can only come from **not holding the token that goes to
zero**. Redirect effort accordingly: away from entry-timing/screen signals
(measured worthless) and onto the rug-prevention gates in §5 and §7 — holder
clustering by funding source, real LP/pool-authority inspection, and simulated
(not merely quoted) sells. The alpha in a lottery-shaped universe is a downside
filter, not a stock picker.

### 10c. Measure time-to-peak before trusting any principal-withdrawal rule

A "withdraw principal at 2x" (or any fixed-multiple) exit is dead on arrival for
a universe whose paths never reach that multiple — applying it then just holds to
the horizon. Before assuming the rule works, from the per-mint paths report:

- **fraction of mints that ever reached the exit multiple** — if it is zero, the
  rule is structurally inert here, not merely underperforming;
- **time-to-peak distribution** — if peaks arrive early (first hours) and paths
  bleed afterward, the only exit that helps is a fast, tight take-profit inside
  that window, not a patient multiple;
- a **take-profit threshold sweep** (exit at first mark >= T for T in e.g.
  10/20/30/50/100%, else hold to last) reporting mean AND median per T. The best
  T by median can still show a losing mean — that gap is the rug tax from §10b,
  and it is the finding, not a footnote.

### 10d. Pair the take-profit with a path-based stop-loss — this is the rug filter

The downside filter §10b points to is not only an entry gate. The defense that
works on **every** mint, including ones with no entry-time features recorded, is
a **chronological stop-loss** on the executable liquidation path. Walk each
per-mint path in observed-at order and exit at whichever trips first: return
>= take-profit (sell at T) or return <= stop-loss (liquidate at the stop); else
hold to the last mark. Sweep a TP x SL grid over the paths and report mean,
median, and worst per cell **before** building the executor — capping the tail is
usually what flips a negative mean positive, because the tail on these assets is
a total loss, and the grid tells you it does so on your own data rather than on
faith.

Realise a stop exit at the **stop threshold, not the deeper observed return** —
and say it is an optimistic bound. Marks are periodic snapshots (tens of
minutes apart); between two marks a draining pool can gap well below the stop, so
a real liquidation could fill worse. Crediting the exact deeper number would
understate losses; crediting the stop overstates the rescue — so report the stop
fill as a bound and name the gap risk, never as a clean backtested exit.

Do not conflate this path stop with an **entry** rug-classifier. Before claiming
an entry screen can be validated, confirm the known losers actually carry the
entry-time features you would screen on. If most rugs predate the feature (a
feature added mid-collection leaves earlier tokens with null snapshots), the
validatable sample is ~1 and any entry classifier fits noise — build the path
stop, which needs no entry data, and defer the entry screen until enough rugs
carry contemporaneous features to measure separation (Cohen's d) honestly.

### 10e. Backtest any signal exit against the trivial baseline; price IS the flow

Before building a signal-driven exit (toxic-flow stop, sell-pressure trigger,
holder-drain alarm), backtest it **head-to-head against the trivial price-only
baseline** (the TP x SL grid from 10d) on the same paths and take-profit. A
signal that cannot beat a dumb fixed number on your own history is dead cheap to
kill — do this before writing any executor or streaming feed. In one session a
2-of-3 toxic-flow exit lost to a fixed -25% stop by ~11.6 pts of mean return and
rode a rug to -99.7% because the signal never fired in time.

The mechanism generalizes: **price is the aggregated output of the very flow you
would read** — liquidity draining, sells dominating, holders leaving all show up
in price. A price stop is therefore a faster, zero-lag, zero-false-positive flow
detector, and a hand-built flow signal must beat that, not merely correlate with
crashes. Reach for the composite signal only where the simple aggregate provably
misses.

Separate "the signal leads price" from "the signal is tradeable at our
resolution." A tell can genuinely lead price (measure the marks between first
toxic mark and first crash mark per rug) yet still lose to the baseline because
the sampling cadence is too coarse to act on the lead — a rug clears in one block
while marks are tens of minutes apart. When that is the diagnosis, the edge (if
any) lives at the **data-resolution/infrastructure layer** (per-block/mempool
streaming), not the analysis layer. Do not fund streaming infra until (a) the
signal beats the baseline on the subset of events where it fired early, and
(b) you have confirmed the failure is resolution, not absence.

Enforce the small-sample refusal **in the tool**: a separation statistic
(Cohen's d, hit rate) should return `reportable=False` and emit nothing when
either group is below a minimum n, so a future run cannot accidentally act on a
d computed from one or two events. Discipline in prose is bypassable; a gate in
the function is not.

### 10f. Decompose latency into detection vs submission before betting on speed

Before claiming a speed edge (sniping, first-block buys), measure both halves
separately — they have different bottlenecks and different fixes:

- **Submission** — time to land the order (e.g. RTT to a Jito block-engine
  relayer). Cheap to measure with `curl -w %{time_total}` against regional
  relayer hosts; a good cloud datacenter gets tens of ms.
- **Detection** — time from an on-chain event to your process SEEING it. This is
  the usual killer and the one that goes unmeasured. A shared/public RPC or
  websocket fans out to thousands and trails the leading edge; measure it by
  subscribing to program logs and comparing your local receive time to the
  feed's own slot-notification time for that slot.

Sort the result into tiers against the chain's slot time (~400ms on Solana):
colocated pros (<10ms, custom Rust, staked connections) you cannot beat; regional
players (tens of ms to relayers, ~150ms detection on a commodity feed) — likely
where a cloud box lands; and everyone else (home internet, public RPC, humans)
whom you beat trivially. A median detection lag near half a slot means you
consistently land a block or two late — dead for block-0 sniping, fine for
follow-the-wallet trades that have seconds of runway. The lag ceiling on a
commodity feed is usually **money** (dedicated Geyser/gRPC, self-hosted RPC), not
geography; say so rather than concluding "we are too slow."

Modern Solana sniping is a **Jito tip auction inside the slot**, not a pure race:
once within a slot you bid for inclusion, and competitive tips (0.001–0.01 SOL,
~$0.15–1.50 per attempt win or lose) can exceed a micro-position — so sniping is
a capital game before it is a latency game. MEV sandwiching is closed to
non-validators since the public mempool was shut off; do not propose it. When the
latency numbers rule out sniping, redirect to **copy-trading** (mirror proven
wallets; the edge is wallet SELECTION, a graph/data problem, not raw speed), which
tolerates ~150ms detection and fits a small bankroll far better.

### 10g. Find smart-money wallets by out-of-sample persistence, not sample rank

Ranking wallets by early-buy hit rate always surfaces prescient-looking names;
that is manufactured, the wallet-graph version of overfitting. The only test that
separates a structural edge (private information / genuine skill) from luck is
**chronological persistence**:

1. Collect `(wallet, mint, bought_at)` edges: stream new-token creates, then the
   first K distinct buyers of each tracked mint (bound RPC cost by tracking only
   mints created during the run and capping buyers per mint). Read the buyer as
   the fee payer whose token balance increased in `postTokenBalances` — no
   instruction decoding needed. Label `is_winner` in a SEPARATE resolve step that
   re-prices each mint after a horizon; the collector must never guess outcomes.
2. Split edges by `bought_at` into train (before a cutoff) and holdout (at/after).
3. In TRAIN ONLY, pick wallets clearing a hit-rate bar with a minimum coin count.
4. Score those same wallets in the HOLDOUT and compute **lift** = their holdout
   hit rate minus the holdout base rate (everyone's average).

Positive lift out of sample is the falsifiable win condition; lift at or below
zero means the "smart" wallets were lucky and reverted to average — walk away.
The boundary edge belongs to the holdout, so a wallet cannot both earn its label
and be scored on the same buy. This is a structural edge (§3d): free-riding other
actors' revealed private information, and it compounds because the graph gets more
valuable the longer it runs. Async-offload the blocking RPC fetches
(`asyncio.to_thread`) and set generous websocket `ping_interval`/`ping_timeout`,
or synchronous `getTransaction` calls starve the keepalive and drop the socket
mid-collection.

### 11. Preserve the no-order boundary until one uncertainty remains

Research clients should contain no private-key loading, signing, transaction
submission, or authenticated order path. Add a dedicated wallet only after the
base rate survives costs and holdout. Fund it with the explicit experiment cap
plus a separate fee reserve, then begin with a consented minimum-size microprobe
and reconcile balances from chain state.
