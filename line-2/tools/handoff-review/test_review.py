#!/usr/bin/env python3
"""Offline behavioral checks; disposable public fixtures stay in test/scratch."""
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import review as R


def altered(data, comment=b"", corrupt=False):
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as source, zipfile.ZipFile(out, "w") as target:
        for item in source.infolist():
            payload = source.read(item.filename)
            if corrupt and item.filename != "HANDOFF.json":
                payload = b"x" * len(payload)
            target.writestr(item, payload)
        target.comment = comment
    return out.getvalue()


class ReviewTests(unittest.TestCase):
    def setUp(self):
        root = Path("test/scratch")
        root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve().relative_to(Path.cwd())
        self.source = self.root / "source"
        self.source.mkdir()
        self.files = {"README.md": b"public fixture\n", "nested/empty": b""}
        for name, data in self.files.items():
            dest = self.source / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        self.data = R.WRITER.build(self.files)
        self.archive = self.root / "bundle.zip"
        self.archive.write_bytes(self.data)

    def test_real_archive_and_source(self):
        result = R.demo()
        self.assertTrue(result["selected_checks_passed"])
        self.assertEqual(result["file_count"], 2)
        self.assertEqual(result["payload_bytes"], 12603)
        self.assertEqual(result["checks"]["source"]["status"], "pass")

    def test_without_source_is_explicitly_skipped(self):
        result = R.review_bytes(self.data)
        self.assertTrue(result["selected_checks_passed"])
        self.assertEqual(result["checks"]["source"]["status"], "not-requested")
        self.assertIsNone(result["checks"]["source"]["receipt"])
        self.assertFalse(result["trusted_digest_matched"])

    def test_deterministic_report_and_trusted_digest(self):
        a = R.review_bytes(self.data, str(self.source), R.WRITER.digest(self.data))
        b = R.review_bytes(self.data, str(self.source), R.WRITER.digest(self.data))
        self.assertEqual(a, b)
        self.assertTrue(a["trusted_digest_matched"])
        self.assertEqual(a["archive_sha256"], a["checks"]["source"]["receipt"]["archive_sha256"])
        self.assertEqual(a["archive_sha256"], a["checks"]["reproduction"]["receipt"]["archive_sha256"])

    def test_valid_alternate_serialization_is_difference(self):
        result = R.review_bytes(altered(self.data, comment=b"public comment"), str(self.source))
        self.assertEqual(result["failed_checks"], ["reproduction"])
        self.assertEqual(result["checks"]["integrity"]["status"], "pass")
        self.assertEqual(result["checks"]["source"]["status"], "pass")

    def test_portability_hazard_is_difference(self):
        result = R.review_bytes(R.WRITER.build({"CON.txt": b"public"}))
        self.assertEqual(result["failed_checks"], ["portability"])
        self.assertIn("windows-device-name", [i["code"] for i in result["checks"]["portability"]["issues"]])

    def test_source_diagnostics_retained(self):
        (self.source / "README.md").write_bytes(b"changed")
        (self.source / "nested/empty").unlink()
        (self.source / "added.txt").write_bytes(b"new")
        result = R.review_bytes(self.data, str(self.source))
        self.assertEqual(result["failed_checks"], ["source"])
        counts = result["checks"]["source"]["receipt"]["counts"]
        self.assertEqual(counts, {"changed": 1, "missing_from_source": 1,
                                  "omitted_from_archive": 1, "unchanged": 0})

    def test_all_differences_reported_together(self):
        data = altered(R.WRITER.build({"CON.txt": b"public"}), comment=b"different")
        result = R.review_bytes(data, str(self.source))
        self.assertFalse(result["selected_checks_passed"])
        self.assertEqual(result["failed_checks"], ["reproduction", "portability", "source"])

    def test_corruption_prevents_source_scan(self):
        with patch.object(R.SOURCE, "source_receipt") as scanner:
            with self.assertRaisesRegex(ValueError, "integrity mismatch"):
                R.review_bytes(altered(self.data, corrupt=True), str(self.source))
            scanner.assert_not_called()

    def test_trusted_digest_refusals(self):
        for digest in ("f" * 64, "invalid"):
            with self.assertRaises(ValueError):
                R.review_bytes(self.data, expected=digest)

    def test_budgets_and_invalid_archive(self):
        for limits in (R.INSPECT.Limits(archive_bytes=1), R.INSPECT.Limits(payload_bytes=1),
                       R.INSPECT.Limits(files=1)):
            with self.assertRaises(ValueError):
                R.review_path(str(self.archive), limits=limits)
        for data in (b"not a ZIP", self.data[:-1], self.data + b"trailing"):
            with self.assertRaises(ValueError):
                R.review_bytes(data)

    def test_archive_is_read_once(self):
        original = R.WRITER.regular_bytes
        with patch.object(R.WRITER, "regular_bytes", wraps=original) as reader:
            result = R.review_path(str(self.archive), str(self.source))
            self.assertTrue(result["selected_checks_passed"])
            self.assertEqual(reader.call_count, 1)

    def test_archive_replacement_after_snapshot(self):
        original = R.WRITER.regular_bytes
        def read_then_replace(path, limit):
            data = original(path, limit)
            self.archive.write_bytes(b"invalid replacement")
            return data
        with patch.object(R.WRITER, "regular_bytes", side_effect=read_then_replace):
            result = R.review_path(str(self.archive), str(self.source))
        self.assertTrue(result["selected_checks_passed"])
        self.assertEqual(result["archive_sha256"], R.WRITER.digest(self.data))

    def test_workspace_paths_and_symlinks_refused(self):
        link = self.root / "link.zip"
        link.symlink_to("bundle.zip")
        for name in (str(link), str(self.archive.absolute()), "../outside.zip"):
            with self.assertRaises(ValueError):
                R.review_path(name)
        directory_link = self.root / "source-link"
        directory_link.symlink_to("source", target_is_directory=True)
        for source in (str(directory_link), str(self.source.absolute()), "../outside"):
            with self.assertRaises(ValueError):
                R.review_bytes(self.data, source)

    def test_nonregular_source_is_refused(self):
        (self.source / "link").symlink_to("README.md")
        with self.assertRaises(ValueError):
            R.review_bytes(self.data, str(self.source))

    def test_cli_statuses_and_no_partial_json(self):
        command = [sys.executable, "-B", "line-2/tools/handoff-review/review.py", "check", str(self.archive)]
        for data, status in ((self.data, 0), (altered(self.data, comment=b"x"), 2),
                             (R.WRITER.build({"NUL": b"hazard"}), 2), (b"bad", 1)):
            self.archive.write_bytes(data)
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, status, result.stderr)
            if status == 1:
                self.assertEqual(result.stdout, "")
                self.assertIn("handoff-review:", result.stderr)
            else:
                self.assertEqual(json.loads(result.stdout)["selected_checks_passed"], status == 0)
        self.archive.write_bytes(self.data)
        (self.source / "extra").write_bytes(b"new")
        result = subprocess.run(command + ["--source", str(self.source)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)["failed_checks"], ["source"])
        result = subprocess.run(command + ["--sha256", "bad"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
