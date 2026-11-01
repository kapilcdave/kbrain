# Data desk notebook

## 2026-11-01 — KAP frozen sample preserved at 07:28Z

Measured at 07:28:28Z: the authoritative `kap-poly15-ws.service` remained
`active/running`, and its output was still changing. The file was 1,270,817,815
bytes with an mtime of 07:28:28Z. The host had 629 MB available memory, 2,013 MB
free swap, and 13 GB free disk. This was a read-only health check; no process or
remote file was changed.

Conclusion: the preregistered three-hour sample was not complete, so copying or
scoring it in this shift would have frozen a different window. Preserve the run
through its approximately 08:03Z exit, then pull, integrity-check, audit and score
the completed artifact off-box. This check makes no tape-quality or edge claim.

## 2026-11-01 — KAP post-cutoff pull/scoring preflight complete

Measured at 07:24Z: the authoritative host unit `kap-poly15-ws.service` was still
active with PID 79035 and the unchanged command
`polyus_pair_ws.py --out .../pair_ws_20261101.jsonl --hours 3`; its start time was
05:03:28Z, so the artifact was not yet complete and was not copied or scored. The
host exposes the frozen WS scorer and its fee module. Their SHA-256 hashes are
`cbf5529844ee001a09ee18a7f373d2e8651ac643e22a905068bece90c26337ae` and
`72f778164780081b712843f06d81ae0eb40145393bf19889ca7359f4af98e353`,
respectively. The scorer streams rows rather than accumulating the tape. Local disk
has 163 GB free, and all six schema-aware auditor tests pass.

Inference: the completed tape can be copied and scored locally without touching a
live runner or risking the t3.micro, but doing so before the host unit exits would
change the frozen sample. A read-only local watcher was stopped; no remote process
or file was changed. This shift makes no gap/edge claim.

## 2026-11-01 — KAP tape access recovered; recorder healthy before cutoff

Measured at 07:21Z: `./kbssh` remains broken by its missing `kbro_ed25519` and the
system SSH-config permissions error, but the staged rustmaker identity works with an
explicit empty SSH config. Read-only inspection found `kap-poly15-ws.service` active
since 05:03:28Z. Its frozen output was still growing: 1,186,407,054 bytes and
2,197,162 rows after about 2h17m. Recent rows contained both Kalshi and Polymarket
messages; Kalshi exposed `msg.ts`/`sending_ts_ms`, PM exposed
`marketData.transactTime`, and both retained legacy floating-point-seconds `rx`.
The process was about 35 MB RSS on recheck; the host had 635 MB available memory,
2 GB swap, and 13 GB disk free. No diagnostic process remained.

Inference: the previous access blocker is retracted. This is only a live health
check, not a completed-tape audit or executable-gap result. Do not scan the 1.2 GB
tape on the t3.micro. After the fixed three-hour cutoff (~08:03Z), stream/copy it
off-box, preserve it unchanged, audit its known timestamp-contract limitations, and
score it locally with the frozen KAP scorer.

## 2026-11-01 — KAP tape still blocked; no local recovery artifact

Measured: a fresh read-only `./kbssh rustmaker` attempt again failed before any
connection because `/home/kapil/.ssh/kbro_ed25519` is absent and the system SSH
configuration reports a permissions error. The workspace's `data/` tree contains no
files, including no failed-job log or partial KAP payload that could be audited as a
fallback. Review has independently accepted the six-test gap-clock auditor repair.

Inference: this shift adds no tape-health or edge evidence. Recollecting would replace
the frozen three-hour decision sample and is therefore not an admissible workaround.
The existing operator request to restore read-only box access remains the only causal
next step; the finished tape should then be streamed through the schema-aware auditor
and its frozen scorer off-box.

## 2026-11-01 — KAP scoring blocked; altspot live runner down

Measured: a post-08:02Z read-only rustmaker check still fails locally before
connection because `/home/kapil/.ssh/kbro_ed25519` is absent and the system SSH
configuration reports a permissions error. The completed KAP tape therefore remains
unseen and cannot be audited or scored. The staged fleet snapshot also marks the
`altspot` live runner **DOWN**, with its last line only reporting consumed CPU time.

Control check: the current auditor does update `previous_recv` for a valid timestamped
gap, and its exact `N+10, N+20 gap, N+15` regression fixture is present. This says
nothing about the inaccessible tape.

Conclusion: KAP remains access-blocked rather than evidence-negative. Operator action
is also required to diagnose `altspot`; data did not start, stop, restart, or arm it.

## 2026-11-01 — KAP decision tape remains access-blocked

Measured: the current generic tape auditor passes all six focused regression tests,
including the timestamped-gap causal-clock fixture. A fresh read-only rustmaker
attempt still exits 255 before connecting: the workspace has no
`/home/kapil/.ssh/kbro_ed25519` identity (and the system SSH config also reports a
permissions error). The completed KAP tape therefore remains unseen.

Inference: no tape-health or executable-gap verdict is possible from this workspace.
The access failure is independent of the repaired audit control. The existing operator
request remains the shortest path to the 2026-11-02 decision; do not rerun or replace
the completed tape.

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

1. After the host unit exits around 08:03Z, gzip-stream the completed
   `/home/ec2-user/poly15/data/pair_ws_20261101.jsonl` through the explicit rustmaker SSH identity.
   Verify gzip integrity, preserve the compressed original, run the schema-aware auditor, then
   decompress locally and run the exact frozen scorer whose hashes are recorded above. Report its
   seconds-valued receive-time and missing Kalshi venue-time violations as limitations, and require
   `time.time_ns()` plus exchange timestamps in the next recorder run.
2. Check the failed collector directories named in the next board request; do not retry all failed
   historical jobs speculatively.
3. Support the altlive lead-venue dry rerun after operator go-ahead (Hyperliquid for HYPE;
   Binance for NEAR/ZEC), preserving venue and local receive timestamps.
