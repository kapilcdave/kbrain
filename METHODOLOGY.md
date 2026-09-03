# Methodology

This work treats a promising backtest as the beginning of an investigation,
not as evidence of a trade. A result advances only when its data, execution
assumptions, uncertainty, robustness, and operational risks survive separate
gates.

## Causal Timestamps

Every input needs an availability time. Event time, publication time, local
receipt time, and decision time are different quantities.

At decision time `t`:

- use only records available before `t`;
- exclude incomplete bars and later revisions;
- build rolling features from prior observations only;
- preserve receipt timestamps for latency-sensitive studies;
- verify venue fields against observed behavior instead of trusting names.

A timestamped value is not necessarily causal. Settlement prints, revised
observations, and candles closing after a decision can reveal the answer while
still looking historical.

## Executable Prices

Mids and candle closes help discovery, but they do not prove executable profit.
Economic tests use the price available to the proposed side, synchronize all
required legs, and reject comparisons without equivalent settlement rules.

A quote is not a fill. Historical candles without depth cannot establish queue
position, fill probability, or size. Those terms remain unmeasured until
forward order-book observations or controlled canaries exist.

## Costs

Every result includes the venue's actual fees, spread, slippage, and rounding.
For multi-leg or round-trip trades, each paid leg is charged separately.

```text
net value = forecast value - executable price - fees - slippage
```

Sensitivity checks vary adverse fill, latency, depth, and size. If a small
haircut changes the sign, the result is execution-dependent rather than robust.

## Preregistration and Holdouts

Confirmatory tests are frozen before evaluation data is inspected. A useful
preregistration states the hypothesis, universe, dates, entry and exit rules,
costs, independent sampling unit, endpoints, controls, concentration checks,
and response to pass, fail, underpowered, or blocked outcomes.

Time-dependent data is split chronologically. Once a holdout has been viewed,
it is burned. Any parameter change based on its result creates a new exploratory
hypothesis that needs a new future window.

## Clustering and Concentration

Confidence intervals resample the unit receiving a common shock, such as a
day, event, game, or settlement window. Multiple contracts sharing one outcome
are not independent observations.

Positive means are also tested after removing the best observations. I compare
equal-weighted and capacity-weighted estimates, report breadth across periods,
and treat rare-loss strategies as unresolved until enough independent tail
exposure exists.

## Controls

A candidate must beat the appropriate baseline, usually the market price rather
than a constant forecast. Useful controls include inverted signals, mismatched
times, shuffled labels within valid strata, trivial strategies, and independent
data sources.

The mechanism should leave internal structure such as a dose-response,
monotone decay, or replication across independent dimensions. Statistical
predictability is insufficient when conditional value is below costs.

## Forward Testing

Historical success authorizes forward measurement, not deployment. Forward
tests preserve the frozen rule and collect terms history cannot supply:
executable depth, queue position, fill rate, markout, competition, and
persistence.

Paper fills stay labeled as proxies. Claims about real resting-order behavior
remain unresolved until separately authorized canary evidence exists.

## Safe Deployment

Research and order-entry code are separated. The default is read-only or paper.
A mutating path requires explicit arming and a passed verification gate.

Live-capable systems should include kill switches, aggregate exposure limits,
venue reconciliation, idempotent identifiers, append-only decisions, bounded
order types, graceful shutdown, and fail-closed handling of ambiguous state.

Promotion proceeds from collection to replay, frozen paper testing, dry-run
integration, a small supervised canary, reconciliation, and only then gradual
size changes.

## Retractions

When a defect changes a result:

1. Mark the original claim retracted or superseded.
2. Explain the defect and its direction of bias.
3. Publish the corrected result beside the old one.
4. Identify which conclusions changed.
5. Add a test or invariant for the failure.
6. Prevent retracted figures from supporting promotion or sizing.

Negative results and corrections remain searchable so the same hypothesis or
bug is not unknowingly repeated.
