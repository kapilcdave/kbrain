#!/usr/bin/env python3
"""Regression tests for the constant-memory tape auditor."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from audit_jsonl_tape import audit


NS = 1_800_000_000_000_000_000


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


class AuditTests(unittest.TestCase):
    def test_valid_rows_and_timestamped_gap_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "00.jsonl"
            write_rows(path, [
                {"k": "book", "recv_ns": NS, "venue_ts": 1},
                {"k": "gap", "recv_ns": NS + 1, "reason": "disconnect"},
                {"k": "trade", "recv_ns": NS + 2, "venue_ts": 2},
            ])
            report, status = audit([path])
        self.assertEqual(status, 0)
        self.assertEqual(report["audit_errors"], 0)
        self.assertEqual(report["counts"]["gaps"], 1)

    def test_gap_without_nanosecond_receive_time_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "00.jsonl"
            write_rows(path, [{"k": "gap", "recv_ns": 1_800_000_000}])
            report, status = audit([path])
        self.assertEqual(status, 1)
        self.assertEqual(report["counts"]["gap_recv_not_ns"], 1)

    def test_monotonicity_is_checked_within_each_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            late = Path(tmp) / "late.jsonl"
            early = Path(tmp) / "early.jsonl"
            write_rows(late, [{"k": "book", "recv_ns": NS + 10, "venue_ts": 2}])
            write_rows(early, [{"k": "book", "recv_ns": NS, "venue_ts": 1}])
            report, status = audit([late, early])
        self.assertEqual(status, 0)
        self.assertNotIn("recv_regressions", report["counts"])

    def test_regression_inside_a_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "00.jsonl"
            write_rows(path, [
                {"k": "book", "recv_ns": NS + 1, "venue_ts": 1},
                {"k": "book", "recv_ns": NS, "venue_ts": 2},
            ])
            report, status = audit([path])
        self.assertEqual(status, 1)
        self.assertEqual(report["counts"]["recv_regressions"], 1)

    def test_kap_envelope_is_classified_not_treated_as_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "kap.jsonl"
            write_rows(path, [{
                "v": "pm",
                "rx": 1_800_000_000.25,
                "m": {"marketData": {"transactTime": "1800000000123"}},
            }])
            report, status = audit([path])
        self.assertEqual(status, 1)
        self.assertEqual(report["counts"]["recv_not_ns"], 1)
        self.assertNotIn("missing_recv_ts", report["counts"])
        self.assertNotIn("missing_venue_ts", report["counts"])


if __name__ == "__main__":
    unittest.main()
