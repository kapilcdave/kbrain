# P&L reconstruction bugs that produce confident, wrong, POSITIVE numbers

These bugs share a signature: they inflate profit, they do not crash, and the
resulting number looks plausible enough to act on.

## 1. Multi-leg cost: the first-non-empty accessor (flipped +$833 → -$2.55)

A settlement record carries a cost field **per leg**. The unused leg is present
and set to `"0.000000"` — not absent, not null:

```json
{"yes_total_cost_dollars": "2.895000", "no_total_cost_dollars": "0.000000",
 "revenue": 300, "value": 100}
```

A convenience accessor that returns the first non-empty field:

```python
def f(x, *names):            # WRONG
    for n in names:
        if x.get(n) not in (None, ""):
            return float(x[n])
cost = f(rec, "cost_dollars", "yes_total_cost_dollars", "no_total_cost_dollars")
```

returns **0.0** for every NO-side settlement, because `"0.000000"` is non-empty.
Every NO trade reads as pure revenue.

**Fix — cost is the SUM of legs, always:**

```python
cost = num(rec, "yes_total_cost_dollars") + num(rec, "no_total_cost_dollars")
```

Reported +$833.68 net. Corrected: **-$2.55**. Sign flip on the headline.

## 2. Mixed units in one payload

The same object can carry integer **cents** and decimal-string **dollars**:
`revenue: 300` (cents) beside `yes_total_cost_dollars: "2.895000"` (dollars).
Subtracting them directly is a 100x error. Normalise at read time and assert the
result is in a sane range.

## 3. Fixed-point string migration → silent zeros

An API that moves `volume` → `volume_fp` (decimal strings) makes the bare key
return `None`. Downstream `or 0` turns every volume into zero. Symptom: "median
volume 0.0" on instruments you demonstrably traded.

**Generalisation:** any helper that maps a missing key to a falsy default hides a
schema migration. Prefer an accessor that tries `f"{key}_dollars"` then `key`,
and **fails loudly** if neither parses.

## 4. Never trust a settlement `revenue` field before proving its semantics

A portfolio can hold both legs of one binary market. Reconstruct gross payout
from the resolved outcome and leg counts:

```python
gross = yes_count if outcome == "yes" else no_count
pnl = gross - yes_cost - no_cost - fees
```

A perfectly matched position with `yes_count == no_count == n` pays `n` under
either outcome. Use that as an invariant test. A provider field named `revenue`
may represent only one accounting path and may be zero even when the matched
position has a guaranteed payout; treating it as total settlement proceeds can
turn profitable hedges into large fictitious losses.

Reconcile reconstructed cashflow with current venue balance plus known deposits,
withdrawals, and open exposure. If the claimed drawdown is impossible relative
to the account's actual capital, stop and audit the formula before producing
series rankings, risk advice, or a trading halt.

## 5. Win rate is not P&L, and can move the opposite way

```
KXSILVER15M  59 settlements  98.3% win rate  net +$1.27
KXWTI15M     53 settlements  98.1% win rate  net -$0.14
```

Buying a favourite at price `p`, break-even is `1-p`. A 98.1% win rate against a
97c basis loses money. **Never report a win rate as evidence of profitability**
without the cost basis beside it.

## 6. Small-sample positives that do not survive extension

```
README:   +$21.83 over 150 settlements, day-clustered CI excludes zero
Full pull: -$0.06 over 482 settlements  =  -$0.0001/settlement
```

Always recompute over the **full** ledger and report the count next to the
number. A CI excluding zero on 150 observations is not a licence to stop looking.

## Standing checklist

- [ ] Cost sums **all** legs
- [ ] Gross payout reconstructed from outcome and leg counts
- [ ] Equal-count opposite legs pass the guaranteed-payout invariant
- [ ] Units normalised (cents vs dollars) and asserted
- [ ] Fees included and their rounding rule verified
- [ ] Computed over the FULL record, count reported
- [ ] Reconciled against balance, transfers, and open exposure
- [ ] Per-instrument breakdown (hides offsetting winners/losers)
- [ ] Cross-check: does a strategy you believe is marginal show a big profit,
      or a loss impossible for the funded balance? Either is a bug signal.
