# Live micro-probes: measuring fills for cents, safely

When paper validation has exhausted itself, exactly one term remains: **would a
resting order have filled, and would the fill have been benign?** A paper runner
records the book but never joins a queue, so it cannot answer this at any sample
size. Neither can any archive.

The instrument is a **minimum-size real order**. At the venue's smallest
granularity the cost of an answer is cents, and it is the only honest measurement
of queue position and adverse selection.

```
0.01 contracts at ~$0.92 = $0.0092 of premium per order
max_fills_total = 25     -> $0.23 absolute worst case
```

Worst case means *every order fills and every filled contract settles worthless*.
Quote that number to the user before arming; it is usually so small that the
decision becomes obvious.

## Get explicit consent, with the numbers, before arming

A live order is a different category of act from analysis, however small. Even
when the user has said "let's do it", present before sending:

1. the exact experiment (what rests where, and for how long);
2. the worst-case dollar figure, derived not asserted;
3. the enforced limits, and that they were **tested**;
4. what the result can and cannot establish.

Then stop and wait. "Reply `arm it`" is a good pattern: unambiguous, and it
leaves a clear consent record in the transcript.

## Verify the safety envelope — do not trust the flag

Prove the rails hold rather than asserting them. Constructor arguments are not
evidence:

```python
for n in (1.0, 0.5, 0.01):                 # oversized clips must be REFUSED
    try: broker._check_envelope(n, 0.90, ticker="TEST")
    except RiskViolation as e: print("refused", e)

Broker.would_cross("bid", 0.92, 0.90, 0.91)   # True  -> crossing blocked
Broker.would_cross("bid", 0.90, 0.90, 0.91)   # False -> resting allowed
```

For the unarmed path, **read the source** rather than executing a placement to
see what happens — an unarmed dry-run call can still be flagged as a write
attempt by a supervising safety layer, and retrying it is the wrong instinct.
Confirm the branch exists and returns before any HTTP write:

```python
if not self.armed:
    order = RestingOrder(order_id=f"dry-{...}", dry_run=True)
    return order          # returns BEFORE self._request("POST", ...)
```

If a safety layer blocks a command, that is the system working. Do not rephrase
it or route around it; verify the property another way and say so.

Required properties for a micro-probe:

- `post_only` on every order — cannot cross, cannot become a taker. A fill on
  placement should **halt** the run: it means the model is wrong.
- clip capped at venue minimum, enforced *inside* the broker so callers cannot
  widen it at runtime.
- a minimum time-to-close, since settlement is the one exposure a cancel cannot
  undo.
- a cumulative realised-loss halt.
- unarmed by default; nothing sends without an explicit flag.

## Reuse the tested order path; never hand-roll one

If the repository already owns an order path with tests behind it, use it. Invent
nothing on the write side.

A concrete failure to avoid: assuming a convenient method name (`order_status`)
that does not exist, when the real one (`reconcile_order`) exists precisely
because of a past incident. Grep the class for its actual method list before
writing against it.

## Ask the venue what happened — inference is not enough

The canonical bug, worth quoting because it recurs:

> A live probe run reported `fills: 0` while the venue showed a small open
> position: a resting post-only ask was hit when the market moved to it,
> which is ordinary maker behaviour and precisely what the experiment rests on,
> but nothing in the loop looked for it.

Two rules follow:

- **A queue-position endpoint returning a number does NOT imply unfilled.**
  Reconcile against the venue's own fill record.
- **Re-check after cancelling.** An order can fill in the gap between the last
  poll and the cancel landing. Log that as its own event type rather than
  discarding it as a no-fill.

## Budget the orders across ENTITIES, not cycles

A market sits inside the qualifying region for minutes, so a naive loop re-picks
the **same ticker every cycle** and spends the whole order budget on one
instrument. Since the interval clusters by market, five fills in one ticker are
~one draw: the run burns real money buying almost no independent evidence.

Cap orders per entity per run (`--max-per-market`, default 1) and pick the
least-visited qualifying candidate first. The binding constraint on sample size
is the **arrival rate of new markets**, not the fill rate — so the budget should
be spent on breadth.

## The armed run surfaces bugs dry-run and paper cannot

A dry run exercises selection and logging; it does not exercise **post-fill
state**. Budget for a short armed shakeout, read the journal, and expect to find
something before committing to a long run.

The canonical instance: a **filled order stays in the in-process resting map**.
If `place_maker` only removes an order on *cancel*, then after a fill the map
still holds it, and `max_resting_orders=1` refuses every subsequent placement.
The symptom is a probe that produces exactly one fill and then goes silent —
one session logged 1 fill followed by 32 consecutive
`"already 1 resting; max is 1"` refusals. Pop the order from the map on **both**
the fill path and the fill-in-cancel-gap path:

```python
if filled:
    broker.resting.pop(resting.order_id, None)   # venue no longer holds it
```

Generalise the lesson: **in-process order bookkeeping diverges from venue state
the moment a fill happens**, because fills arrive asynchronously and the local
map is usually only maintained on the paths the author was thinking about. Check
whether the repo's own tested probe already handles this — one grep for
`resting.pop` found the exact fix, with a comment explaining why.

### Diagnose a quiet probe from the journal, not the console

When an armed run stops producing orders, the reason is almost always being
logged and discarded. Count the refusal reasons first:

```bash
grep -o '"reason":"[^"]*"' logs/probe.jsonl | sort | uniq -c | sort -rn
```

This turns "it seems stuck" into a named cause in one command. Log every refusal
with a machine-readable `reason` field for exactly this purpose — a refusal that
is only printed is a refusal you cannot aggregate.

## What to record per order

- queue depth ahead **at placement** (from the same payload as the price), and
  the venue's reported `queue_position` sampled while resting — they are
  different measurements and both matter;
- filled or not, and time-to-fill;
- mid at placement and at horizons afterwards, giving
  `capture = |mid(fill) − price|` and `adverse = markout − capture`;
- the settled outcome.

Two results fall out that nothing else provides:

1. **Fill rate as a function of queue depth.** If orders only fill when the queue
   is trivially thin, the strategy has no capacity regardless of its edge.
2. **Adverse selection.** If filled orders win *less* than unfilled ones, the
   maker premium is imaginary.

## State the limit of what a micro-probe proves

At minimum size you measure **whether the queue clears**, not capture-at-size. A
0.01-contract fill does not prove a 30-contract order fills — that order joins a
different position in the queue and moves the book. Say this explicitly when
reporting, or the result will be over-read as a capacity answer.

It is the necessary first step, not the whole answer.
