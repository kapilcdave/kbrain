# Forward paper validation: buying the term history cannot price

When a backtested edge survives every historical control, exactly one class of
question remains: **would we actually have got the fill, and would it have been
benign?** No amount of history answers it — 1-minute bars cannot see queue
position or intra-bar sequencing. Only forward observation does.

Build a **paper runner**: record the full decision state at signal time and the
realised outcome, place nothing.

## Log the decision, not just the signal

One `quote` record per entity that enters the cell, one `settle` record when it
resolves, and a `skip` record with a reason whenever a filter rejects something.
Skips are data: they measure the filter's own cost, and a filter that never fires
should be deleted.

Capture at minimum: timestamp, entity, time-to-event, both sides of the touch,
spread, **queue depth ahead at our price**, and every filter input. Depth is the
whole point — a 2.5c edge behind a 4,000-contract queue is inaccessible at any
bankroll, and depth varied 20 vs 590 contracts between two instruments in a
single 15-minute sample.

## Score three things separately — never one blended number

1. **Calibration** — priced at the **mid**. Makes no fill assumption. This is the
   historical finding, retested out of sample.
2. **Fill economics** — priced at the **bid**, minus fees on the taker path.
   Reported beside calibration, never added to it. The gap between the two *is*
   the fill assumption, stated numerically.
3. **Adverse selection** — win rate of fillable signals vs unfillable ones. If
   fillable ones win less, the maker path is worse than the mid path.

## Prove the thing cannot trade — audit, don't assert

A comment saying "read-only" is not evidence. Verify mechanically:

```bash
grep -oE "requests\.[a-z]+" runner.py | sort -u        # expect: requests.get only
grep -nE "POST|DELETE|PUT|KALSHI-ACCESS|Broker|/portfolio" runner.py
python -c "import ast;
t=ast.parse(open('runner.py').read())
imps=[n.module or '' for n in ast.walk(t) if isinstance(n,ast.ImportFrom)]
assert not any('broker' in i for i in imps), 'IMPORTS A TRADING MODULE'"
```

The strongest guarantee is structural: no auth, no write verbs, no import of any
module that owns an order path. Then the worst failure mode is a wrong number in
a log.

## Validate every parser against the venue BEFORE the long run

A silent parse bug produces a full journal of confident nonsense, and you only
find out after burning the collection window. Cross-check each parsed field
against an independent endpoint first.

**Latency vs parse bug — the bracket test.** When two sources disagree, you
cannot tell a stale snapshot from a misread. Bracket the suspect call between two
calls of the reference:

```
read A  ->  read B (suspect)  ->  read A again
```

If B lies **between** the two A readings, the parser is right and the sources are
simply snapshots at different instants. If B falls **outside** the bracket, and
does so one-sidedly, it is a real defect. Slow instruments agreeing while fast
ones disagree is the signature of latency, not of a bug — but confirm it, don't
assume it.

**Resolution: prefer one payload over a join of two.** When the bracket test
rejects a source, look for a single endpoint carrying every correlated field at
once. One session found the orderbook ladder disagreed with the venue's own
quote (best bid 0.65 against a reported 0.59 ask — a crossed, stale book), and
dropped it entirely because the markets payload already carried the touch price
**and** its size (`yes_bid_dollars` beside `yes_bid_size_fp`). Two endpoints
joined on a fast-moving entity are two different instants; one payload is
self-consistent by construction, and it halves the request count.

Related: `?depth=N` style parameters may truncate the end of a ladder you care
about. Verify which end by sweeping the parameter and watching whether the touch
moves.

## Calibrate expectations before starting

Measure the signal's real-time arrival rate first (log the unfiltered
time/price distribution for a few minutes). A cell firing on 4.4% of
observations produces ~2 signals per 15 minutes — so ~100 settlements is days,
not an overnight run. Say this to the user up front; it prevents a premature
"it's not working" read on a sample too small to say anything.

## Test forward vs history for CONSISTENCY, not for confirmation

A small forward sample cannot confirm an edge, and reading it as if it could
cuts both ways — a mildly negative forward result is not a refutation either.
Ask the answerable question instead: **is the forward result consistent with the
historical estimate?**

Bootstrap the historical population at the forward sample size and locate the
forward mean as a percentile:

```python
sims = [mean(sample(hist_window_evs, k=len(fwd_windows))) for _ in range(20000)]
pct  = sum(x < mean(fwd_windows) for x in sims) / len(sims)
# 0.025 < pct < 0.975  ->  consistent; history has not been contradicted
```

Worked example: history `+0.87c` over 5,369 windows; forward `−0.65c` over 52.
A 52-window draw from the historical population lands in `[−5.65c, +6.22c]` 95%
of the time, and the forward result sits at the **29.4th percentile** — fully
consistent. Reporting that as "the forward run is negative, the edge is dead"
would have been as wrong as reporting an early positive as confirmation.

State the width explicitly so the user reads it correctly: *"neither confirms
nor refutes"* is the honest verdict for most forward samples, and saying it early
prevents both premature celebration and premature abandonment.

## Beware inclusion criteria that change the population

If a panel only records rows meeting a price condition, cells at different times
contain **different populations**. Same price, different histories:

```
favourite at 0.90, 420-600s left  ->  +2.46c
favourite at 0.90, 180-300s left  ->  -1.94c

of markets in-band late: 143 FELL into the band, 109 rose into it
```

Late-window rows are dominated by favourites *decaying* into the band; early ones
by markets simply *priced* there. A sign flip across adjacent time cells is a
prompt to check the conditioning, not to declare a regime. Narrow the claim to
the population you actually measured, and enforce it forward with an explicit
filter — recording "history unknown" when the entity was first seen already
inside the region.
