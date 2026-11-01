# Data desk notebook

## 2026-11-01 — gap-clock audit repair

Measured: review's exact three-row reproducer (`book recv_ns=N+10`, timestamped `gap N+20`,
then `trade N+15`) now fails with `recv_regressions=1` and nonzero status. Timestamped gap
markers participate in the same file-local monotonic receive clock and min/max range as ordinary
rows. All six focused regression tests pass, including the new causal-clock fixture.

Conclusion: the generic auditor no longer silently admits receive-time reversal across a recorded
disconnect. This repairs the audit control only; the KAP tape is still unseen and establishes no
edge or tape-health result.

## 2026-11-01 — KAP legacy-envelope audit support

Measured: `./kbssh rustmaker ...` still exits 255 before connection because the workspace lacks
`/home/kapil/.ssh/kbro_ed25519`; the completed paired-book tape remains unseen. Source inspection
of the frozen KAP recorder confirms local receive time is `rx` in floating-point seconds and the
Polymarket exchange timestamp is nested at `m.marketData.transactTime`. Kalshi book messages do
not consistently expose a venue timestamp. These are schema limitations, not tape-health or edge
results.

Updated the constant-memory auditor to recognize the legacy `rx` envelope and nested Polymarket
timestamp. It deliberately still fails `rx` as non-nanosecond and reports Kalshi rows lacking a
venue timestamp, but now separates those known violations from genuinely absent fields. Added a
regression test; all five tests pass.

## 2026-11-01 — KAP tape audit preflight, access still blocked

Measured: a second `./kbssh rustmaker ...` attempt still failed locally before connection because
`/home/kapil/.ssh/kbro_ed25519` is absent. The KAP recorder source in `~/proj/kap` writes local
receive time as floating-point seconds under `rx`; Polymarket's venue time is nested in raw
messages, while not every Kalshi row exposes a venue timestamp. Therefore the generic collector-
contract audit will reject this recorder as written. This is a timestamp-contract finding, not a
tape-health or edge verdict; the remote tape itself remains unseen.

Fixed the auditor so a gap marker must carry a nanosecond local receive timestamp, and receive-time
monotonicity resets at file boundaries (explicit input order is not chronology). Added four
regression tests covering a valid timestamped gap, a seconds-valued gap, cross-file ordering, and
an actual within-file regression. All four pass.

## 2026-11-01 — paired-book tape handoff

Measured: the board had no request addressed to data. Fleet's nearest decision is KAP's
Polymarket US/Kalshi BTC 15M paired-book tape, scheduled to finish around 08:02Z on rustmaker.
The workspace could not inspect it: `./kbssh` failed locally before connecting because
`/home/kapil/.ssh/kbro_ed25519` is absent (and emitted an SSH config permissions warning).
This is an access failure, not evidence about tape health.

Shipped `audit_jsonl_tape.py`, a constant-memory auditor for plain/gzipped hourly JSONL. It counts
gap markers and row kinds and fails on malformed rows, absent venue/local timestamps, local receive
timestamps not in ns, or receive-time regressions. This specifically guards the timestamp and
flat-memory requirements before the tape is scored; it does not estimate an edge.

## Queue

1. Ask review to recheck the gap-clock repair; once read-only box access is restored, inspect and
   pull the completed KAP tape. Preserve and
   score the existing tape with its frozen scorer. Run the schema-aware auditor first; report its
   seconds-valued receive-time and missing Kalshi venue-time violations as limitations, and require
   `time.time_ns()` plus exchange timestamps in the next recorder run.
2. Check the failed collector directories named in the next board request; do not retry all failed
   historical jobs speculatively.
3. Support the altlive lead-venue dry rerun after operator go-ahead (Hyperliquid for HYPE;
   Binance for NEAR/ZEC), preserving venue and local receive timestamps.
