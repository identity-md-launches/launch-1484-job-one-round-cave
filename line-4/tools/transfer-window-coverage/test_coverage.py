"""Offline tests for validated bounded-window coverage reports."""

import copy
import importlib.util
import io
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("coverage", HERE / "coverage.py")
coverage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coverage)


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.capture = json.loads(
            (HERE.parent / "transfer-crosscheck" / "publicnode.json").read_text()
        )

    def test_demo_has_real_events_and_empty_blocks(self):
        result = coverage.coverage(self.capture)
        self.assertEqual(result["token"], "ZTO")
        self.assertEqual(result["transfer_count"], 3)
        self.assertEqual(result["populated_block_count"], 1)
        self.assertEqual(result["empty_block_count"], 11)
        self.assertEqual(sum(item["transfer_count"] for item in result["populated_blocks"]), 3)

    def test_empty_window_reports_all_blocks_empty(self):
        empty = copy.deepcopy(self.capture)
        empty["raw_logs"] = []
        empty["transfers"] = []
        empty["transfer_count"] = 0
        empty["duplicate_count"] = 0
        result = coverage.coverage(empty)
        self.assertEqual(result["populated_blocks"], [])
        self.assertEqual(result["empty_block_count"], result["block_count"])

    def test_log_order_does_not_change_block_report(self):
        altered = copy.deepcopy(self.capture)
        altered["raw_logs"] = list(reversed(altered["raw_logs"]))
        events, duplicates = coverage.crosscheck.window.validate_logs(
            altered["raw_logs"], altered["decimals"], altered["token_address"],
            altered["from_block"], altered["to_block"])
        altered["transfers"] = events
        altered["transfer_count"] = len(events)
        altered["duplicate_count"] = duplicates
        self.assertEqual(coverage.coverage(self.capture), coverage.coverage(altered))

    def test_tampered_evidence_is_rejected(self):
        bad = copy.deepcopy(self.capture)
        bad["raw_logs"][0]["removed"] = True
        with self.assertRaises(coverage.crosscheck.window.RpcError):
            coverage.coverage(bad)

    def test_duplicate_json_keys_are_rejected(self):
        duplicate = HERE / "duplicate.json"
        duplicate.write_text('{"token":"ZTO","token":"IMD"}')
        self.addCleanup(duplicate.unlink)
        with self.assertRaises(ValueError):
            coverage.read_capture(duplicate)

    def test_demo_command_emits_json(self):
        output = io.StringIO()
        from contextlib import redirect_stdout
        with redirect_stdout(output):
            coverage.main(["--demo"])
        self.assertEqual(json.loads(output.getvalue())["kind"], "erc20-transfer-window-coverage")


if __name__ == "__main__":
    unittest.main()
