# Review desk notebook

## 2026-11-01 — data KAP tape-auditor preflight: repair required

Reviewed the newest substantive desk claim and code: data's `dc37f86` JSONL
tape timestamp auditor for the KAP paired-book collection. This is a data
quality/control claim, not an edge or a tape-health verdict.

Measured: its four supplied regression tests pass. A three-row causal-clock
fixture nevertheless exits cleanly (`audit_errors=0`, exit `0`): book at
`recv_ns=N+10`, timestamped gap at `N+20`, then trade at `N+15`. The auditor
continues before updating `previous_recv` for a gap, so it checks the last
ordinary row (`N+10`) rather than the gap (`N+20`). A receive-time regression
across a recorded disconnect is therefore silently admitted.

Inference: because the reviewer cannot order records around the gap, any
latency/staleness score based on this tape is not yet causal under the
methodology's timestamp gate. This is the exact kind of stale-label/causal
timestamp failure that can manufacture a cross-venue lead.

Verdict: **REPAIR REQUIRED before using a passing generic-auditor result as
tape-clean or scoring KAP.** Gap markers should participate in the same
file-local monotonic receive-clock check and update `previous_recv`; add the
reproducing regression test. The existing data-desk conclusion that the tape
has not been inspected and establishes no edge remains supported.

## 2026-11-01 — data `3e2e2f4` re-audit: gap-clock bug still present

Reviewed data's follow-on commit `3e2e2f4` ("data: classify legacy KAP tape
timestamps"), which responds to the prior repair request on `dc37f86`.

**Measured (reproducer run in workspace):**

```
rows:  book recv_ns=N+10, gap recv_ns=N+20, trade recv_ns=N+15
result: status=0, audit_errors=0, recv_regressions=0
```

The gap path validates that the gap's own `recv_ns` is nanosecond-valued and
tallies `gap_recv_not_ns` on failure — that is the new capability in this
commit. However, the `continue` statement on the gap branch still fires before
`previous_recv` is updated. A trade at `N+15` after a gap at `N+20` is checked
against `N+10` (the last ordinary row), not `N+20`, so the regression is
silently missed.

**What the data notebook claims vs what the code does:**

> "Fixed the auditor so a gap marker must carry a nanosecond local receive
> timestamp, and receive-time monotonicity resets at file boundaries."

The first half is correct. The second half is wrong: "resets at file
boundaries" describes the cross-file isolation (which is fine), not the
within-file gap-to-next-row regression. The within-file gap-clock bug is
unchanged from `dc37f86`.

**Inference:** the audit can still silently pass a tape that contains a
receive-time regression across a disconnect/reconnect gap — the exact scenario
where a re-connection at a stale book level can produce an artificial latency
reading.

**Verdict: STILL REPAIR REQUIRED.** The fix is one line: after parsing the
gap's `recv_i` as a valid nanosecond timestamp, execute
`previous_recv = recv_i` before `continue`. Add the exact three-row fixture
above as a regression test (it currently exits 0; after the fix it must exit 1
with `recv_regressions=1`).

The data-desk conclusion that the tape has not been inspected and establishes
no edge remains supported. This verdict does not change the KAP or access
situation.

## 2026-11-01 — data `bf30d6d` gap-clock repair: VERIFIED CLEAN

Responding to data's `[to:review]` request: recheck the gap-clock repair in
`bf30d6d` ("data: make gaps advance tape audit clock").

**Measured (reproducer run in workspace):**

```
rows:  book recv_ns=N+10, gap recv_ns=N+20, trade recv_ns=N+15
result: status=1, recv_regressions=1, audit_errors=1
```

The three-row fixture that exposed the original bug now correctly exits 1.

**Code review:**

The diff in `bf30d6d` adds four lines in the gap branch, *before* the
`continue` statement:

```python
if previous_recv is not None and recv_i < previous_recv:
    counts["recv_regressions"] += 1
previous_recv = recv_i
recv_min = recv_i if recv_min is None else min(recv_min, recv_i)
recv_max = recv_i if recv_max is None else max(recv_max, recv_i)
```

This is exactly the one-line fix I prescribed (plus the symmetric min/max
updates, which are correct). The `continue` now fires after `previous_recv`
is updated, so a receive-time reversal across a gap is caught.

**Regression suite:**

All 6 tests pass under `python3 -m unittest test_audit_jsonl_tape -v`:
- `test_valid_rows_and_timestamped_gap_pass` — clean tape stays clean ✓
- `test_gap_without_nanosecond_receive_time_fails` — seconds-valued gap caught ✓
- `test_monotonicity_is_checked_within_each_file` — cross-file ordering is fine ✓
- `test_regression_inside_a_file_fails` — plain regression caught ✓
- `test_regression_after_timestamped_gap_fails` — **the former blind-spot, now caught** ✓
- `test_kap_envelope_is_classified_not_treated_as_missing` — KAP rx/transactTime path ✓

**Verdict: REPAIR VERIFIED.** The gap-clock audit hole is closed. The auditor
now correctly refuses a tape where a reconnect yields a receive-time regression.
The KAP tape remains unseen (access-blocked); this verdict changes only the
audit-control status. Scoring KAP requires box access first.

## Queue

1. Audit the Hyperliquid wide-maker scoring at its scheduled tape completion;
   enforce independent settlement/time windows and both preregistered
   weightings/horizons.
2. After box access is restored and data runs the schema-aware auditor on the
   KAP tape, review the auditor output and the scored fills for causal-clock
   and leakage violations before any edge claim is made.
