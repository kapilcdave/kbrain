---
name: trading-strategy-validation
description: "Validate a trading strategy/backtest; kill false edges."
tags: [quant, backtest, falsification, prediction-markets, kalshi, statistics, edge-validation]
---

# Trading Strategy Validation

For any task shaped like "is this edge real", "why isn't the strategy making
money", "tune the entry band", or "backtest this idea". The job is almost never
to find an edge. It is to **kill the false ones fast** so the real one, if any,
is still standing.

**Default posture: assume the reported edge is an artifact until three
independent cuts agree it is not.** Most claimed edges in this domain die to
accounting bugs, weighting artifacts, or self-credited spread — not to bad luck.

## The order of operations (do not reorder)

Each step is cheap and can kill the thesis outright. Running them out of order
wastes work on a hypothesis that a later step would have refused.

### 1. Reconcile against the ground-truth ledger FIRST

Before touching a backtest, pull the **venue's own settlement/fill record** and
compute realised P&L. Not the bot's journal — the exchange's numbers.

A backtest is a model of the past; the ledger *is* the past. If the ledger says
zero, no amount of panel analysis matters. This single step has repeatedly ended
sessions in ten minutes that would otherwise have been days of band-tuning.

Watch for the README/FINDINGS drift pattern: an early positive over a small
sample ("+$21.83 over 150 settlements, CI excludes zero") that **does not survive
extension** (net $-0.06 over 482). Always recompute over the FULL record, and
report the settlement count alongside the number.

### 2. Audit the P&L accounting before believing any P&L

See `references/ledger-accounting-pitfalls.md`. The multi-leg cost bug there
flipped a headline from **+$833 to -$2.55**. Read it before writing a P&L
reconstruction — these bugs produce large, confident, wrong, *positive* numbers.

Sanity gate: if a reconstruction shows a strategy you know to be marginal
returning a big profit, that is a bug signal, not a discovery.

### 3. Pick the metric the actual constraint implies

Optimising the wrong objective invents edges that cannot be spent.

| binding constraint | correct objective | wrong objective |
|---|---|---|
| capital / small bankroll | return **on capital** per unit time: `(EV/price) x (3600/hold_s)` | EV per contract |
| opportunity / few signals | EV per contract | ROC |
| throughput / rate limits | EV per requote | EV per contract |

Buying at 0.97 and 0.60 for the same 2.5c EV are identical per contract and
**1.6x apart per dollar**. State which constraint binds before choosing.

### 3b. Check the position identity before claiming a "new family"

In a binary market, **buying YES at `p` and selling NO at `1-p` are the same
position** — same collateral, same payoff, same risk. At the mid the identity is
exact:

```
EV_no(mid) = (1-q) - (1-mid) = -(q - mid) = -EV_yes(mid)
```

So "tails are overpriced" and "favourites are underpriced" are **one measurement
with the sign flipped**, not two strategies. There is one calibration curve; the
only question is which side of it to stand on, and in which regime.

Before proposing any alternative as a *different* family, write down its payoff
and collateral and check it is not the existing trade in different words. Do this
for spreads and hedges too. Cheap to check, embarrassing to skip.

### 3c. Name who pays the edge and why they are late

Before collecting signals, state the wealth-transfer mechanism in one sentence:
**who takes the other side, what information or constraint makes them trade, and
why your signal arrives before their price impact**. An effect with no plausible
payer is pattern description, not a strategy.

For AMM assets there is no house: entry takes inventory from pools and profitable
exit requires later buyers or LP inventory to absorb the sale. List the agents
likely taking money from you too—insiders distributing supply, earlier bots,
arbitrageurs, LP fees, route fees, and failed exits. If the only thesis is “more
people will buy later,” identify the observable process that predicts those later
buyers and test whether it leads price rather than follows it.

### 3d. Classify the edge as predictive vs structural before collecting anything

An LLM asked to "build a mean-reversion bot for the Nasdaq" will cheerfully
manufacture an edge: enough knobs (lookback, band, stop, hold) and a backtest
always finds a profitable cell on the sample. That is overfitting wearing an
equity curve, and it looks identical to a real edge until it trades and reverts
to minus-costs. The defense is to name the edge's SOURCE before touching data:

- **Predictive** — "I analyze public data and forecast price better than the
  market." Almost always fake: everyone has the same data, and firms with PhDs
  and colocated servers already ran your idea. If the edge is *cleverness applied
  to public information*, assume it is arbitraged away or never existed. A
  screen-and-swing microcap strategy is this category.
- **Structural** — you get paid for something real and asymmetric: **speed**
  (being first), **private information** (knowing before it is in the price),
  **providing a service** (liquidity, taking inventory/forced-flow risk), or
  **access** (doing what others structurally cannot). Only structural edges are
  durable, because they do not compete on "who is smarter about the same data."

A structural edge that also **compounds** and is **hard to replicate** (an asset
built over time, not a `pip install`) is the one worth building. Prefer edges
that fit the operator's real advantage: a data/graph problem suits a research
harness; a millisecond race does not. Whatever the class, the falsification bar
is unchanged: one-sentence mechanism plus a chronological holdout, or it is
noise.

For this user's attention-led microcap research, start with revealed on-chain
attention and do not add X/social ingestion unless they explicitly opt back in.
Capture attention features at the same timestamps as fixed-quantity executable
marks; a contemporaneous attention/price correlation cannot establish a lead.

Treat wallet funding as **plumbing capital**, never calibration data. Estimate the
return distribution with paper positions first; a tiny funded wallet buys only a
few noisy outcomes and cannot establish a fat-tail base rate. Funding authorizes
wallet-state simulation or a bounded microprobe only after the paper gate, not
strategy deployment.

### 4. Decompose the edge into what you invent vs what the market gives

A maker backtest that rests at the bid **credits itself the half-spread by
construction**. Split it:

```
EV_bid = q - bid      # what the backtest reports (spread + mispricing)
EV_mid = q - mid      # mispricing only, assumption-free
spread_term = mid - bid
```

If `EV_mid <= 0 < EV_bid`, it is a **pure spread-capture bet** and its survival is
an adverse-selection question, not a calibration one. Only `EV_mid` clearing its
bound means the market is genuinely mispriced.

### 5. Preregister the falsification bar, then run it

Write the bar **in the script, before seeing numbers**. State it so it can fail:

- **Time holdout** — chronological split; positive in BOTH halves.
- **Independent factor split** — instruments sharing neither benchmark nor
  settlement boundary (e.g. BTC vs GOLD). Co-expiring legs off one benchmark are
  ~one draw, not N draws, and **cannot buy precision**.
- **Multiplicity** — report cells examined vs expected spurious passes
  (~5% of cells at a 95% bound). 70 cells → ~3.5 free "discoveries".
- **Control region** — a cell that SHOULD be dead. If it also passes, the test
  has no power.

### 6. Run the entity-weighting control — this is the one that gets missed

**Read `references/panel-weighting-bias.md`.** It cost a session's headline
finding that had already passed a preregistered time+factor holdout.

If your panel has **more than one row per tradeable decision**, weighting by rows
weights each entity by how long it lingered in the qualifying region — and
lingering correlates with outcome. That is look-ahead **in the weights**, not in
the features, so no feature audit finds it.

For DEX token studies, define the independent entity as the **token mint**, not
the pool, route, or polling row. Deduplicate multiple pools before counting and
use the first qualifying observation as entry; later polls are one token's path.
Otherwise persistent tokens and multi-pool tokens manufacture sample size.

Run `scripts/entity_weighting_check.py` on any panel-derived edge before
reporting it. A finding can pass every holdout and still die here.

### 6b. Audit a SURVIVING edge before reporting it

Passing the preregistered bar is not the end. Three checks kill findings that
already survived a holdout — see
`references/estimator-coherence-and-composition.md`:

- **Interval coherence.** If the point estimate is over legs and the interval
  over clusters, they are different estimators and the band may not bracket its
  own estimate. Free assertion: `lo <= point <= hi`. Fix with a **cluster
  bootstrap** — reduce each cluster to one number, resample clusters — so both
  quantities share units by construction. Report `P(EV>0)` alongside.
- **Composition drift.** After a backfill, new instruments land mostly in one
  chronological half, so a "time split" is really an instrument split. Print
  share-per-half; any group shifting >5pp confounds it. Re-split on entities
  covered in **both** halves, then split each entity individually and report the
  `k/n` that hold (one session: 9/9 pooled, but only **6/9** per series).
- **Effect-size trajectory.** Report the estimate as a function of n. `+2.46c →
  +0.87c on 13.6x the data` is the signature of a scanned cell, and is
  consistent with both a real-but-smaller edge and a mostly-selected one. Say
  both; do not pick the flattering branch.

### 7. Apply fees at the actual entry price before believing anything

Fees are frequently a third or more of a small edge, and **rounding rules matter
more than rates**. A `ceil`-to-the-cent fee is flat in absolute terms across a
whole price range: Kalshi's `ceil(0.07*C*P*(1-P))` is **1.00c per contract at
every price from 0.88 to 0.97** — 40% of a 2.46c gross edge.

Price both execution paths separately and never blend them:

```
taker: gross - fee                  # real, no fill assumption, smaller
maker: gross + half-spread - 0      # bigger, and assumes a benign fill
```

The gap between them **is** the unverified assumption, stated as a number.

**When the fee exceeds the gross edge, the taker path is dead at any bankroll**
and the strategy reduces to a pure bet on benign maker fills — a term no archive
can price. That reduction is the headline result, not a footnote.

For AMM/DEX tokens, replace display-price returns with an **exact-size executable
round trip**: quote the buy, feed its raw output amount into the sell quote, and
compute the numeraire returned. Keep integer base units, record both routes, and
do not subtract fees already reflected in quoted output. Treat network fees,
account creation/rent, tips, failed transactions, and unsimulated wallet state as
explicit unmeasured costs—not zero. For forward returns, freeze the first audited
buy's raw token output and re-quote selling that same fixed quantity; repeated
fresh round trips are cost observations, not a position path. See
`references/dex-microcap-validation.md`.

### 8. Only then: capacity and size arithmetic

```
$/window needed / qualification_rate = $ per qualifying window
/ (EV_per_contract)                  = contracts needed
x price                              = premium at risk in ONE window
```

Compare premium-at-risk to the actual balance. Also: **capture-at-size is not
measurable from history.** Every $/day figure scales linearly and is fiction
above some unknown clip until bought with a real experiment.

## Exhaust the archive before spending wall-clock on forward collection

Forward runs buy precision at ~4 independent windows/hour. An existing panel may
already hold thousands, and a backfill is pure API work costing nothing.

**Split the question before choosing an instrument:**

- *Does the edge exist?* → **history**, and it answers ~1000x faster.
- *Would we get the fill, benignly?* → **forward only**; no archive can price
  queue position or intra-bar sequencing.

Run the forward collector in the background for the second question *while* the
archival work proceeds — never instead of it. If a user asks "can't you just use
the historical data", they are almost certainly right; act on it immediately and
say which single term still requires forward observation.

**Backfill breadth, not just depth.** Reuse the existing collector if it is
resumable (most are: they record completed entities and append). Widening from 3
instruments to 15 and 37 days to 68 took one session from 20k to 275k rows —
13.6x — in one unattended run, and *broadening the instrument set* is what buys
independent factors. Back up the panel first, then let it append.

Expect the effect to **shrink** on the larger sample, and treat that as a
diagnostic rather than a disappointment (see §6b).

## Escalating to live micro-orders

When paper has exhausted itself and only fill quality remains, the next
instrument is a **minimum-size real order** — at venue granularity an answer
costs cents (`0.01 contracts x $0.92 = $0.0092`; 25 fills = $0.23 worst case).
See `references/live-microprobe-fill-measurement.md`.

Non-negotiables: get **explicit consent with the worst-case number derived**
before arming; reuse the repository's tested order path rather than hand-rolling
one; verify the risk envelope by *testing* it (oversized clips refused, crossing
refused) rather than trusting a flag; and reconcile fills against the venue —
a queue-position endpoint returning a number does **not** mean unfilled.

**Budget a short armed shakeout before the long run.** A dry run exercises
selection and logging but never post-fill state, and the classic bug lives there:
a filled order left in the in-process resting map trips `max_resting_orders` and
refuses everything afterwards — one fill, then silence. When an armed probe goes
quiet, aggregate the journal's refusal reasons rather than reading the console.
Budget orders **per entity**, not per cycle, or one market absorbs the whole
budget and buys ~one independent draw.

State the limit plainly when reporting: a micro-probe measures whether the queue
clears, **not capture-at-size**. It is the necessary first step, not the answer.

## Retro-apply every estimator fix to all prior claims

When you find a clustering, weighting, or accounting defect, it is almost never
confined to the artifact where you noticed it. **Immediately re-run every earlier
claim built on the same estimator**, including ones already reported as passing.

One session fixed boundary-clustering in a forward scorer, left the historical
headline uncorrected because that is not where the bug surfaced, and only
revisited it when the user pushed — at which point the headline finding no longer
cleared zero. A report where one number is honest and another is not, with no
marker saying which, is worse than not having found the bug.

## Statistical rules that are not optional

- **Interval over clusters, never over rows — and find the RIGHT cluster.**
  Clustering is a hierarchy: `rows -> entity -> settlement boundary -> day`.
  Fixing rows->entity is the usual stopping point and is often still wrong.
  **When instruments co-expire on a shared boundary, distinct tickers are not
  independent draws.** Measure the agreement rate against a `max(q, 1-q)`
  independence baseline rather than assuming. See
  `references/clustering-and-effective-sample-size.md` — a design effect of only
  1.09x still moved a published finding from `+0.81c` (survives) to `-0.04c`
  (does not clear zero). Cluster the *interval*; keep the point estimate over
  legs, since legs are what get traded — **unless cluster size correlates with
  cluster outcome** (next rule).
- **Check whether cluster SIZE predicts cluster OUTCOME.** If losing clusters
  carry fewer legs than winning ones, leg-weighting over-samples winners and the
  point estimate is biased — one session saw `+0.98c` leg-weighted against
  `-0.65c` window-weighted on the same 132 legs, because losing windows offered
  1.00 legs and winning ones 2.39. When the two weightings disagree in sign, the
  **cluster-weighted number is the honest one.** This is the loiter bias one
  level up the hierarchy.
- **Report median and the worst few clusters, not just the mean.** For
  favourite-buying the payoff is capped at `1-p` and the downside is ~`p`, so a
  median of `+9.85c` against a mean of `-0.65c` is normal and the mean is carried
  entirely by a tail the sample cannot price. This is the mechanical reason a
  90%+ win rate settles at ~$0.
- **Wilson, not normal approximation**, at extreme `p`. At `p=0.98` the normal
  interval is nonsense.
- **Kelly is undefined at the wings.** At `p=0.98`, `p/(1-p)=49`: one percentage
  point of error in `q` moves `f*` by 49 points. Size on the Wilson **lower
  bound** or do not size at all. Where the edge does not survive its own
  interval there is no clip, there is a skip.
- **Break-even for buying a favourite at price `p` is `1-p`.** Not some derived
  win/loss ratio. A 98.1% win rate at a 97c basis still loses money — the win
  rate is not the question, the price is.
- **Never quote mean-edge x aggregate-volume as capacity.** Edge and attainable
  size are typically negatively related.

## Reporting

Write findings as a dated `FINDINGS_*.md` next to the code, and **lead with the
result that is largest, even when it is negative**. Structure:

1. Headline claim, stated so it could have failed.
2. Evidence table with n, and n as *clusters*.
3. **"What this cannot tell you, stated plainly"** — always present. Name the
   unmeasured terms explicitly rather than letting them pass silently.
4. Bugs found on the way, and which number each one flipped.
5. What follows, in order.

Classify every negative into a failure class — no edge / overfit / cost barrier /
adverse selection / capacity / data defect / underpowered. **The class licenses
different next steps: "underpowered" permits more data collection on the same
hypothesis, "no edge" explicitly does not.**

## Safety

- Research is **read-only by default**. Say so explicitly in the writeup: "no
  orders placed, no config changed, running bot untouched."
- Never change live trading config as part of an analysis task. Recommend, and
  let the user decide.
- Long-running collectors and sweeps **contend for rate limits**. Do not run two
  at once; one session took a sweep from 350s to 5,651s that way.

## Separate "is there an edge" from "what would it pay"

When the user names an income target, answer it as **two questions with different
answers**, or the analysis silently becomes target-driven:

1. *Is the edge real?* — the falsification work above.
2. *If real, what does it pay?* — bounded by `bankroll x edge x capture`.

Then sanity-check the target against the bankroll before optimising anything:

```
$3/15min = $288/day
  on $35     ->   832%/day
  on $1,000  ->  28.8%/day
  on $10,000 ->   2.9%/day
  on $250k   ->   0.1%/day
Best sustained track record in finance ~0.15%/day.
```

A target needing many multiples of Medallion is a **bankroll problem wearing a
strategy costume**, and no amount of tuning touches it. Say so plainly and early.

Corollary — the absurdity check: take the best measured per-deployment edge, apply
it at full size every window, and look at the implied daily. If it prints
$13,727/day on $10k, the per-deployment edge **cannot survive contact with size**,
and capture-at-size is the whole strategy rather than a detail to measure later.

## When the answer is "stop"

If the ledger, the corrected panel, and the capacity arithmetic all agree the
family returns ~zero, **say so and recommend switching families** — even when
asked to "keep going until we win". Grinding parameters on a first-order zero is
the expensive failure mode. Deliver it as: the three cuts, the failure class, and
one concrete alternative direction with a stated mechanism.

Users say things like "don't stop until we win" and "my desire to make money is
strong". That is a reason to be **more** rigorous, not less: the fastest path to
money is refusing to fund a zero. Give the honest verdict, then a concrete next
experiment that risks nothing — never a hedge or a softened number.

## Correct yourself in-line, prominently

If you proposed something that a later step proves wrong, **lead the next message
with the correction** rather than quietly dropping it. A retracted suggestion the
user might still act on is worse than no suggestion. State what was wrong, why,
and what replaces it — then continue.

When a prior session's summary is the thing that is wrong, retract it **before**
building on it, even if the user asks you to continue from it. Continuing on a
known-bad premise compounds the error into every downstream result.

## Quarantine broken code; never leave it runnable

A script that once printed a confident wrong number will print it again. When an
analysis is retracted:

- Move the defective scripts to a `retracted/` subdirectory with a README naming
  **each file's specific defect** — not a generic warning.
- Put a `RETRACTED — DO NOT USE` header at the top of the file's docstring,
  stating which output was wrong and which corrected script replaces it.
- Keep them only as the reproduction case, and say so. Deleting them loses the
  ability to demonstrate the bug; leaving them in place invites a rerun.
- Write the retraction findings file so it **links forward** to the corrected
  result, and the corrected one back, so the two read as one arc rather than as
  contradictory claims.

The same applies to derived artifacts: a discovery JSON built by a broken filter
(e.g. a "weather markets" list that is mostly sports contracts matched on city
names) is actively misleading and belongs in quarantine with the code.

## "Never run" is a claim that must itself be tested

Asserting an experiment is untestable is a hypothesis, not a conclusion. If you
find yourself repeatedly telling a user a test "would require infrastructure we
don't have", stop and look for the archival route — scheduled events, settled
history, and OHLC/candlestick endpoints frequently make a "live-only" question
answerable retrospectively with far more statistical power.

When a user pushes back on a negative claim with conviction, treat it as a
prompt to re-examine the claim's *premise* rather than to restate it. In one
session the user was right that a latency effect existed; the correct move was
to find the retrospective test, which then confirmed the effect was real (and
separately showed it was not harvestable). Both halves needed measuring.

## Killing a live strategy

"Kill it" means **no exposure**, not "no process". Check, in order: systemd/user
units, running processes, cron — and then **the venue itself** for resting orders
and open positions. Resting orders survive the death of the process that placed
them. Report the flat state with the actual numbers (0 resting, 0 positions,
balance) rather than asserting it.

## Model the SETTLEMENT quantity, not a proxy for it

Every "market is mispriced" claim compares your number to the venue's number. If
your number measures a *different quantity*, the comparison is meaningless and
the error is systematic — you will get confident, repeatable, **sign-flipped**
edges rather than noise.

**Read `rules_primary` (or the venue's equivalent) before modelling.** It names
the data vendor, the exact site/index, and the measurement window. Ticker strings
encode none of those. Assuming a plausible public data source instead cost one
session its entire thesis: the venue settled on a commercial vendor's value,
while the model used the free government feed for the "same" site — a systematic
**+3.20 ± 1.33 °F** offset, 3.2x the strike spacing, which flipped a
+0.503/contract trade to -0.144.

**Fit the gauge on settled history.** Settled markets publish what actually
settled (`expiration_value` on Kalshi). That turns "which source and window?"
from a guess into a scoring problem with a checkable answer. Score candidate
(source, window, rounding) combinations against it before trusting any model.
If nothing reproduces it, that is a **stop**, not a smaller edge.

**A market on a daily extremum is a question about a WINDOW, not an instant.** A
daily minimum is a running floor and can only ratchet down. Comparing the current
observation to an extremum strike is sign-flipped whenever the extreme part of
the window has not happened yet.

**Price a rung against its whole ladder.** Where strikes form mutually exclusive
buckets (`floor_strike` + "X or above"), normalise the ladder for overround and
compare the full distribution. A bucket the market prices at 30% that your model
calls impossible is not an edge — it is your gauge assumption failing, and that
normalisation is what surfaces it.

## Timing claims need timestamps; movement is not direction

A latency claim is a **timing** claim: quotes lag a release by seconds. Testing
it requires release timestamps matched against quote-change timestamps. An HTTP
round-trip figure ("~500 ms to fetch the data API") is a property of the network
path and is **not evidence of any market lag** — never report one as the other.

Scheduled releases make this testable **retrospectively**, with far more power
than waiting live: minute-bar quote history over settled markets yielded ~83k
minute-pairs in minutes of wall time. See
`references/event-timing-and-maker-screens.md` for the method and the three
screens that kill a false positive.

**Unsigned movement is not edge.** `|d mid|` clustering can be overwhelming
(z=+7.56, p~2e-14) while the trade is worthless. It says the quote *moves*, not
that the direction is predictable or that anyone could be filled on the right
side. Always follow it with a signed-continuation test against a control, and a
comparison against the real cost hurdle.

## Check the venue's cost structure before investing in any signal

On a [0,1] contract, costs are a percentage of the **whole instrument**: ~4c
spread + up to 1.75c fee is ~6% of notional round trip, against ~0.01% for a
liquid equity. That is a ~600x difference in the edge required to break even, and
it is the single best predictor of whether work in a venue can pay.

Before spending a session on a signal, ask whether its *plausible* size can clear
the hurdle. One real, statistically overwhelming effect measured ~0.2c against a
6c hurdle — a good signal in the wrong venue. When several unrelated strategies
in one venue all die at the cost line, that is structural, and the correct move
is to change venue rather than to keep hunting signals.

## Files

- `references/panel-weighting-bias.md` — the row-vs-entity artifact, worked.
- `references/clustering-and-effective-sample-size.md` — the clustering
  hierarchy, co-expiring settlement boundaries, design effects, retro-apply rule.
- `references/ledger-accounting-pitfalls.md` — P&L reconstruction bugs.
- `references/kalshi-api-notes.md` — Kalshi venue specifics, fees, auth, quirks.
- `references/forward-paper-validation.md` — paper runners, no-order-path audit,
  the bracket test for source disagreement, inclusion-criterion artifacts.
- `references/estimator-coherence-and-composition.md` — auditing an edge that
  already survived: incoherent intervals, cluster bootstrap, composition drift
  after a backfill, effect-size shrinkage as a selection diagnostic.
- `references/live-microprobe-fill-measurement.md` — escalating from paper to
  minimum-size real orders: consent, testing the risk envelope, reconciling
  fills against the venue, and what a micro-probe cannot prove.
- `references/theo-vs-book-informed-maker.md` — pricing digital markets off
  external spot to become the informed maker, and the vol-disagreement trap that
  makes a naive realized-vol estimate manufacture huge fake theo-vs-book edges.
- `references/weather-model-latency.md` — Kalshi weather markets: the settlement
  gauge (fit on `expiration_value`; METAR runs +3.2 °F warm), market/ladder
  structure, and why both the taker and maker sides of the release-timing trade
  are measured dead.
- `references/event-timing-and-maker-screens.md` — testing a scheduled-release
  timing hypothesis from minute-bar history (quote hygiene, within-block
  permutation nulls, closed-form moments), plus the three screens that kill a
  false maker edge: unsigned movement, unconditional drift, markout-vs-round-trip.
- `references/dex-microcap-validation.md` — one-chain venue selection, mint-level
  independence, cross-source token controls, exact-size round-trip quotes,
  transaction simulation, and append-only evidence for thin AMM tokens.
- `scripts/entity_weighting_check.py` — generic row-vs-entity weighting control.
