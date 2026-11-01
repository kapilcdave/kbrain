# Gemini desk notebook

## 2026-11-01 — post-reboot tape-health boundary; no score

**Measured, 07:37 UTC (read-only):** all five Gemini units were active with
the same `06:05:16 UTC` start: `gb-depthtape` (PID 1875), `gb-leadfeed`
(1876), `gb-quoter` dry-run (1878), `gb-record` (1879), and `gb-strikepoll`
(1880). The box had 529 MB available RAM and 28 GB free disk.

The depthtape's 06Z file contains 17,832 rows, but just 201 Gemini rows and
32 `depthUpdate`s (only `gemi-btc05m2611010705-up`); the other 17,631 records
are Coinbase. Its journal records rejected subscriptions for expired/invalid
derived 05M symbols after restart. This is an incomplete post-reboot interval,
not a valid all-family basis-taker sample. Do not use it for the frozen score.

By the 07:37 check, the new 07Z file had 53,754 rows: 41,201 Gemini rows,
5,300 depth updates, all four 15M families plus BTC 05M, and 12,553 Coinbase
rows. `gb-record` independently logged 44 newly observed strike records by
07:37. The collection therefore recovered, but the 06Z recovery interval
must remain excluded or explicitly reported as incomplete when scoring.

**Inference:** the current collecting bet remains underpowered, rather than
failed or passed. The frozen BTC clip-10 threshold requires 222 independent
BTC windows; no P&L was inspected or calculated this shift. The dry quoter
was observed emitting only `mode: DRY` orders/cancels; that is plumbing, not a
fill or maker-edge result.

**Operational note:** `./kbssh geminibot` currently fails locally before
connection with an OpenSSH system-config permission error. A read-only direct
SSH invocation with the existing Gemini identity succeeded; no remote state
was changed. This must not be confused with a tape failure.

### Queue

1. At the frozen-read threshold, score only post-recovery complete windows per
   `PREREG_gemflow_basis_taker_20261031`; report independent windows, not tape
   rows, and preserve the 06Z exclusion.
2. Before any read, establish the operator's requested timezone convention
   for the 12am session boundary.
3. Investigate stale-symbol unsubscribe/lifecycle handling only if the
   multi-family depth stream again fails after the recovered 07Z interval.
