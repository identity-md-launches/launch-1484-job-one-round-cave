#!/usr/bin/env python3
"""Offline checks for block-audit response handling."""
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('block_audit', HERE / 'block_audit.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
BUNDLE = json.loads((HERE.parent / 'direct-capture' / 'example-pinned-zto.json').read_text())


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.block = dict(BUNDLE['block'])

    def reader(self, method, params):
        self.calls.append((method, params))
        if method == 'eth_chainId':
            return '0x1'
        return self.block

    def test_matching_anchor(self):
        result = tool.audit(BUNDLE, read=self.reader)
        self.assertEqual(result['status'], 'matches')
        self.assertEqual(result['snapshot_block_hash'], self.block['hash'])
        self.assertEqual(len(self.calls), 2)

    def test_different_hash_is_reported_without_claiming_reorg(self):
        self.block['hash'] = '0x' + 'ab' * 32
        result = tool.audit(BUNDLE, read=self.reader)
        self.assertEqual(result['status'], 'different')

    def test_missing_height_is_unavailable(self):
        def unavailable(method, _params):
            return '0x1' if method == 'eth_chainId' else None
        result = tool.audit(BUNDLE, read=unavailable)
        self.assertEqual(result['status'], 'unavailable')
        self.assertIsNone(result['provider_block_hash'])

    def test_changed_height_is_rejected(self):
        self.block['number'] = hex(int(self.block['number'], 16) + 1)
        with self.assertRaises(ValueError):
            tool.audit(BUNDLE, read=self.reader)

    def test_wrong_chain_is_rejected_before_block_lookup(self):
        calls = []
        def wrong_chain(method, params):
            calls.append(method)
            return '0x5'
        with self.assertRaises(ValueError):
            tool.audit(BUNDLE, read=wrong_chain)
        self.assertEqual(calls, ['eth_chainId'])

    def test_invalid_snapshot_is_rejected_before_provider_read(self):
        invalid = dict(BUNDLE)
        invalid['result'] = '0x00'
        with self.assertRaises(ValueError):
            tool.audit(invalid, read=self.reader)
        self.assertEqual(self.calls, [])

    def test_duplicate_keys_rejected(self):
        with self.assertRaises(ValueError):
            tool.strict_json(b'{"block": {}, "block": {}}')


if __name__ == '__main__':
    unittest.main()
