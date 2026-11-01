# Data desk notebook

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

1. Once read-only box access is restored, inspect and pull the completed KAP tape, run the auditor,
   and hand the audit plus artifact path to predx for the frozen scorer.
2. Check the failed collector directories named in the next board request; do not retry all failed
   historical jobs speculatively.
3. Support the altlive lead-venue dry rerun after operator go-ahead (Hyperliquid for HYPE;
   Binance for NEAR/ZEC), preserving venue and local receive timestamps.
