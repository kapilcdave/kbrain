#!/usr/bin/env python3
"""Stream-audit JSONL or JSONL.gz tapes without loading them into memory."""

from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterator, TextIO


RECV_PATHS = (("recv_ns",), ("local_recv_ns",), ("received_ns",), ("t_ns",), ("rx",))
VENUE_PATHS = (
    ("venue_ts",), ("venue_ts_ms",), ("transactTime",), ("exchange_ts",), ("ts",),
    # Polymarket US market-data messages put the exchange timestamp below the
    # raw message envelope used by the KAP paired-book recorder.
    ("m", "marketData", "transactTime"),
)


def open_text(path: Path) -> TextIO:
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8")
    return path.open("r", encoding="utf-8")


def files(paths: list[Path]) -> Iterator[Path]:
    for path in paths:
        if path.is_dir():
            yield from sorted(
                child
                for child in path.rglob("*")
                if child.is_file() and (child.name.endswith(".jsonl") or child.name.endswith(".jsonl.gz"))
            )
        else:
            yield path


def first_path(row: dict[str, Any], paths: tuple[tuple[str, ...], ...]) -> tuple[str | None, Any]:
    for path in paths:
        value: Any = row
        for key in path:
            if not isinstance(value, dict) or key not in value:
                break
            value = value[key]
        else:
            if value is not None:
                return ".".join(path), value
    return None, None


def audit(paths: list[Path]) -> tuple[dict[str, Any], int]:
    counts: Counter[str] = Counter()
    kinds: Counter[str] = Counter()
    recv_min: int | None = None
    recv_max: int | None = None

    for path in files(paths):
        counts["files"] += 1
        # Each hourly file is independently resumable. Comparing the last row of
        # one explicit input with the first of another makes CLI argument order
        # look like a clock regression, so monotonicity is file-local.
        previous_recv: int | None = None
        try:
            handle = open_text(path)
        except OSError:
            counts["open_errors"] += 1
            continue
        with handle:
            for line in handle:
                counts["lines"] += 1
                try:
                    row = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    counts["invalid_json"] += 1
                    continue
                if not isinstance(row, dict):
                    counts["non_object"] += 1
                    continue
                kind = str(row.get("k", row.get("kind", row.get("type", "unknown"))))
                kinds[kind] += 1
                if kind == "gap":
                    counts["gaps"] += 1
                    recv_key, recv = first_path(row, RECV_PATHS)
                    if recv_key is None:
                        counts["gap_missing_recv_ts"] += 1
                    else:
                        try:
                            recv_i = int(recv)
                        except (TypeError, ValueError):
                            counts["gap_bad_recv_ts"] += 1
                        else:
                            if recv_i < 1_000_000_000_000_000_000:
                                counts["gap_recv_not_ns"] += 1
                    continue

                recv_key, recv = first_path(row, RECV_PATHS)
                venue_key, _venue = first_path(row, VENUE_PATHS)
                if recv_key is None:
                    counts["missing_recv_ts"] += 1
                else:
                    try:
                        recv_i = int(recv)
                    except (TypeError, ValueError):
                        counts["bad_recv_ts"] += 1
                    else:
                        if recv_i < 1_000_000_000_000_000_000:
                            counts["recv_not_ns"] += 1
                        if previous_recv is not None and recv_i < previous_recv:
                            counts["recv_regressions"] += 1
                        previous_recv = recv_i
                        recv_min = recv_i if recv_min is None else min(recv_min, recv_i)
                        recv_max = recv_i if recv_max is None else max(recv_max, recv_i)
                if venue_key is None:
                    counts["missing_venue_ts"] += 1

    errors = sum(counts[key] for key in (
        "open_errors", "invalid_json", "non_object", "missing_recv_ts",
        "bad_recv_ts", "recv_not_ns", "recv_regressions", "missing_venue_ts",
        "gap_missing_recv_ts", "gap_bad_recv_ts", "gap_recv_not_ns",
    ))
    report = {
        "counts": dict(sorted(counts.items())),
        "kinds": dict(sorted(kinds.items())),
        "recv_ns_min": recv_min,
        "recv_ns_max": recv_max,
        "audit_errors": errors,
    }
    return report, 1 if errors or counts["files"] == 0 else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    report, status = audit(args.paths)
    print(json.dumps(report, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
