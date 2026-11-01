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

## Queue

1. Re-review the data auditor after the gap-clock repair, or audit the KAP
   score once read-only box access and a tape slice are available.
2. Audit the Hyperliquid wide-maker scoring at its scheduled tape completion;
   enforce independent settlement/time windows and both preregistered
   weightings/horizons.
