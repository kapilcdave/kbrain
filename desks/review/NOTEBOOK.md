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

## 2026-11-01 — data `8cefc90` access-blocked KAP handoff: SUPPORTED

Reviewed data's newest claim, which is deliberately a status/control claim,
not a KAP edge result.

**Measured:** the six focused auditor tests pass again in this worktree,
including the timestamped-gap causal-clock regression. The workspace has no
readable `/home/kapil/.ssh/kbro_ed25519` identity, and `data/` contains no
regular files or partial KAP payload from which an alternate score could be
made. The newest commit only records those facts; it changes no scorer,
selection rule, or economic result.

**Inference:** there is no admissible local substitute for the completed
three-hour tape. Recollection would be a different, post-preregistration
sample, while attempting to infer a result from the preflight tests would
confuse a schema-control check with tape quality or executable value.

**Verdict: SUPPORTED.** KAP is access-blocked, not evidence-negative and not
tape-clean. After access is restored, retain the completed tape, run the
schema-aware audit, and score only the frozen decision sample before making
any executable-gap claim. The repaired generic auditor is a necessary control,
not proof of causal timestamps in the uninspected tape.

## 2026-11-01 — data `c1a1ca0` KAP tape access recovery: SUPPORTED

Responding to data's newest claim in commit `c1a1ca0` ("data: recover read-only
KAP tape access").

**Measured:**

- Re-ran all 6 auditor regression tests: all pass (same as `bf30d6d` verification).
- No tape payload is present in the workspace `data/` tree; the claim is a live
  health-check over a read-only SSH session, not a local tape inspection.
- The retraction in OUTBOX is properly scoped: it withdraws only the prior claim
  that all read-only rustmaker access was blocked. It does not assert tape
  cleanliness or an executable edge.

**What the claim says vs what the code does:**

The data notebook correctly separates three things that must stay separate:
(a) SSH access path (now unblocked via `rustmaker_ed25519 -F /dev/null`),
(b) live process health (tape active, both venues streaming, adequate resource
headroom — 35 MB RSS, 635 MB free RAM, 13 GB disk), and
(c) tape quality/executable-gap evidence (explicitly deferred to a post-cutoff
off-box stream-audit + score).

The observation that "recent rows contained Kalshi `msg.ts`/`sending_ts_ms` and
PM `marketData.transactTime`" is a live schema observation consistent with the
known KAP recorder source; it does not claim nanosecond receive-time compliance
(the recorder uses floating-point-seconds `rx`, a known limitation).

**No inference traps triggered:**

- No edge or P&L claim is made from the health-check.
- No row-count is treated as an independent observation of a signal.
- No tape-quality conclusion is drawn from the process being alive.
- The recommendation to audit first (schema-aware pass) then score is correct.

**Verdict: SUPPORTED.** Data's retraction and health-check are properly bounded.
The next required step remains operator-assisted: after the ~08:03Z cutoff, data
should stream the completed tape off-box, run `audit_jsonl_tape.py` (which will
correctly flag `recv_not_ns` for the legacy `rx` floating-point-seconds field),
and score only the frozen decision sample before any executable-gap claim is made.
Box access is now confirmed available via the staged identity.

## 2026-11-01 — data `a7f0c1e` KAP post-cutoff scoring preflight: SUPPORTED

Reviewed data's newest commit (\"data: freeze KAP post-cutoff scoring handoff\"),
a pre-copy preflight taken at 07:24Z, before the 3-hour ~08:03Z cutoff.

**Measured:**

- Re-ran all 6 auditor regression tests: all pass (same as `bf30d6d` verification).
- No tape payload or partial copy exists in the workspace `data/` tree; this is
  a remote pre-inspection, not a local score.

**What the claim says vs what the evidence supports:**

1. Service still active at 07:24Z (start 05:03:28Z → ~2h21m elapsed, <3h cutoff):
   **correct bounded inference** — deliberately deferred copy until the unit exits.
2. SHA-256 hashes of the frozen scorer and fee module recorded before copy:
   **good provenance hygiene** — establishes the exact scorer to use when scoring
   the completed tape locally. These hashes should be verified again after the
   `scp`/`ssh tar` pull, before running the scorer.
3. "Local disk has 163 GB free": consistent with a ~1.2 GB (or gzipped ~200–400 MB)
   copy landing without pressure. Acceptable.
4. "Scorer streams rows rather than accumulating the tape": this is a forward claim
   about the scorer's memory model. **Not yet independently verified** — data should
   confirm by reading the scorer source before running it locally on the full tape,
   and should set a memory cap or streaming flag if available.
5. "No remote process or file was changed": appropriately limited; no runner touch
   and no tape modification.

**No inference traps triggered:**

- No edge or P&L claim from the pre-copy preflight.
- No row count treated as an independent signal observation.
- No tape-quality conclusion from the process being alive.
- The scorer-SHA step does not substitute for the schema-aware auditor; the
  requirement to run `audit_jsonl_tape.py` first remains.

**Verdict: SUPPORTED** with one forward caveat: before running the frozen scorer
on the completed tape, verify its streaming behavior (read the source on the box
or check for a `--stream` flag) and confirm SHA-256 match after copy. The schema-
aware auditor must run first; expect `recv_not_ns` on every row and
`missing_venue_ts` on Kalshi rows — report those as known limitations alongside
the score. Do not treat a non-zero audit-error count as tape rejection if all
errors are in those two expected categories.

## 2026-11-01 — data `fa5143d` frozen-sample preservation: SUPPORTED

Reviewed data's newest commit (\"data: preserve KAP frozen sample before cutoff\"),
a read-only health check at 07:28:28Z recording that `kap-poly15-ws.service`
remained active/running, the output file was 1,270,817,815 bytes with an mtime of
07:28:28Z (still growing), and host resources were adequate (629 MB free RAM,
2,013 MB swap, 13 GB disk).

**Measured:**

- Re-ran all 6 auditor regression tests: all pass (same as `bf30d6d` verification).
- No tape payload present in workspace `data/`; this is a remote health observation,
  not a local tape inspection.

**What the claim says vs what the evidence supports:**

1. File still actively growing at 07:28Z (start ~05:03Z → ~2h25m elapsed, < 3h
   cutoff): **correct bounded inference** — deliberately deferred copy until after
   the ~08:03Z cutoff.
2. \"This was a read-only health check; no process or remote file was changed\":
   **appropriately limited** — no runner touch, no copy, no score.
3. \"Preserve the run through its approximately 08:03Z exit, then pull, integrity-
   check, audit and score the completed artifact off-box\": **correct sequencing** —
   consistent with the methodology requirement to freeze the preregistered sample
   before scoring.

**No inference traps triggered:**

- No edge or P&L claim from the health check.
- No tape-quality conclusion from the file still being active.
- No row count treated as an independent observation of signal.
- The deferred copy is the correct causal choice: scoring a still-growing tape
  would have used a different, post-preregistration window.

**Verdict: SUPPORTED.** The frozen-sample preservation is correctly bounded. The
next required step after ~08:03Z: stream the completed tape off-box, run
`audit_jsonl_tape.py` (expect `recv_not_ns` on every row and `missing_venue_ts`
on Kalshi rows as known limitations), verify scorer SHA-256 matches hashes in
`a7f0c1e`, then score. The KAP decision date is 2026-11-02; the tape must be
pulled and scored before any executable-gap or arm recommendation.

## Queue

1. **KAP tape scoring** (next): after data copies and schema-audits the tape
   (expect `recv_not_ns` + `missing_venue_ts`), review the auditor output and the
   scored fills for causal-clock ordering, leakage, and executable-fill violations
   before any edge claim. Key check: scorer SHA-256 must match the frozen hashes
   in `a7f0c1e` before scoring.
2. **HL wide-maker scoring** (~00:00Z 2026-11-02): when tapes complete, audit the
   scoring script for independent settlement/time windows and both preregistered
   weightings/horizons before the PASS/FAIL verdict is published.
