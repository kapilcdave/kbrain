# Polymarket desk notebook

## 2026-11-01 — KAP paired-book frozen sample still collecting; no score yet

**Measured at 07:37:31 UTC (read-only SSH to rustmaker):**

- `kap-poly15-ws.service` was `active`, PID 79035, continuously active since
  05:03:28 UTC, running the declared three-hour paired-book recorder through
  the scheduled ~08:03 UTC cutoff.
- The host had 623 MB available memory and 13 GB disk free.  The recorder used
  235.4 MB resident memory.  No process, service, file, or configuration was
  changed.

**Interpretation:** the authoritative three-hour sample remains incomplete.
No tape-quality, lead/lag, executable-gap, fill, or edge claim is made from a
running artifact.  The closed PM-US/Kalshi taker-taker route remains excluded:
the frozen evaluation is only the preregistered paired-book paper preflight,
and it must use file-order local receive time, report independent 15-minute
windows separately from episodes, and remain non-causal for fill claims.

**Next, in order:**

1. After the unit exits, pull the completed artifact off-box by streaming; do
   not score it on rustmaker.
2. Verify gzip integrity and the frozen scorer hashes from `a7f0c1e`; then run
   the repaired schema/timestamp auditor.  Treat `recv_not_ns` and Kalshi
   `missing_venue_ts` as disclosed limitations, rather than silently omitting
   them or calling them a clean audit.
3. Score the frozen rule with the declared fee, reaction, and stale-quote
   controls; report episodes and unique 15-minute windows separately.  Close
   this KAP decision path if it has no executable post-fee gap at our reaction
   budget.  A positive top-of-book replay alone cannot promote a maker or
   taker order path.

## Queue

1. Completed KAP paired-book frozen scorer and audit after the scheduled
   recorder exit (decision 2026-11-02).
2. If closed, retain the null and do not reopen generic PM-US/Kalshi 15M
   taker-taker: four-asset shared-index width-and-toll closure already covers
   it.
