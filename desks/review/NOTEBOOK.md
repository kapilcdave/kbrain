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

## Queue

1. Re-review the data auditor after the gap-clock previous_recv fix (one-line
   fix identified above). The gap-clock bug is the sole remaining blocker.
2. Audit the Hyperliquid wide-maker scoring at its scheduled tape completion;
   enforce independent settlement/time windows and both preregistered
   weightings/horizons.
