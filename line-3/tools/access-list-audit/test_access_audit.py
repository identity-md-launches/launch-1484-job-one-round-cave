"""Offline behavioral checks; synthetic slots are test data, never chain claims."""
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

import access_audit as a

ZTO = a.reader.D.ZTO
IMD = a.reader.intent.IMD
K1, K2 = '0x' + '11' * 32, '0x' + '22' * 32


def entry(address, *keys):
    return {'address': address, 'storageKeys': list(keys)}


def text(entries):
    obj = a.reader.demo_object()
    obj['accessList'] = entries
    return json.dumps(obj)


def rlp(json_text):
    obj = json.loads(json_text)
    fields = [int(obj[name], 16) for name in a.reader.QUANTITIES[:5]]
    fields += [bytes.fromhex(obj['to'][2:]), int(obj['value'], 16), bytes.fromhex(obj['data'][2:]),
               [[bytes.fromhex(e['address'][2:]), [bytes.fromhex(k[2:]) for k in e['storageKeys']]]
                for e in obj['accessList']]]
    return '0x02' + a.reader.D.rlp_encode(fields).hex()


class AuditTests(unittest.TestCase):
    def audit(self, entries):
        return a.inspect(text(entries), 'json')

    def test_empty(self):
        r = self.audit([])
        self.assertFalse(r['hasRepeatedCharges'])
        self.assertEqual(set(r['gas'].values()), {'0'})

    def test_demo_matches_formats_and_has_real_destination(self):
        x, y = (a.inspect(a.demo_text(fmt), fmt) for fmt in ('rlp', 'json'))
        self.assertEqual(x['inspection'], y['inspection'])
        self.assertEqual(x['gas'], y['gas'])
        self.assertEqual(x['inspection']['destinationLabel'], 'ZTO')
        self.assertEqual(x['gas']['totalAccessListCharges'], '4800')
        self.assertEqual(x['gas']['totalRepeatedCharges'], '2400')

    def test_within_entry_repetition(self):
        r = self.audit([entry(ZTO, K1, K1, K1)])
        self.assertEqual(r['gas']['totalAccessListCharges'], '8100')
        self.assertEqual(r['gas']['totalRepeatedCharges'], '3800')
        self.assertEqual([x['keyIndex'] for x in r['duplicates']['storageKeys']], [1, 2])
        self.assertTrue(all(x['firstKeyIndex'] == 0 for x in r['duplicates']['storageKeys']))

    def test_across_entries_and_first_occurrence(self):
        r = self.audit([entry(ZTO), entry(ZTO, K1), entry(ZTO, K2, K1), entry(ZTO, K1)])
        self.assertEqual([x['entryIndex'] for x in r['duplicates']['addresses']], [1, 2, 3])
        self.assertEqual([x['firstEntryIndex'] for x in r['duplicates']['addresses']], [0, 0, 0])
        self.assertEqual([(x['entryIndex'], x['keyIndex'], x['firstEntryIndex'], x['firstKeyIndex'])
                          for x in r['duplicates']['storageKeys']], [(2, 1, 1, 0), (3, 0, 1, 0)])
        self.assertEqual(r['gas']['totalRepeatedCharges'], '11000')

    def test_key_is_scoped_to_address(self):
        r = self.audit([entry(ZTO, K1), entry(IMD, K1)])
        self.assertFalse(r['hasRepeatedCharges'])
        self.assertEqual(r['counts']['uniqueAddressStorageKeyPairs'], 2)
        self.assertEqual(r['gas']['totalAccessListCharges'], '8600')

    def test_byte_identity_case_not_text_identity(self):
        r = self.audit([entry(ZTO, K1), entry('0x' + ZTO[2:].upper(), K1)])
        self.assertEqual(len(r['duplicates']['addresses']), 1)
        self.assertEqual(len(r['duplicates']['storageKeys']), 1)

    def test_original_order_retained_and_json_rlp_equivalent(self):
        entries = [entry(IMD, K2, K1, K2), entry(ZTO, K1), entry(IMD, K1)]
        original = text(entries)
        x = a.inspect(original, 'json')
        y = a.inspect(rlp(original))
        self.assertEqual(x['inspection']['transaction']['accessList'], entries)
        for field in ('inspection', 'gas', 'duplicates', 'counts'):
            self.assertEqual(x[field], y[field])

    def test_duplicate_addresses_with_distinct_keys(self):
        r = self.audit([entry(ZTO, K1), entry(ZTO, K2)])
        self.assertEqual(r['duplicates']['storageKeys'], [])
        self.assertEqual(r['gas']['totalRepeatedCharges'], '2400')

    def test_seeded_cost_partition(self):
        rng = random.Random(29)
        for _ in range(100):
            entries = [entry(rng.choice([ZTO, IMD]),
                             *[rng.choice([K1, K2]) for _ in range(rng.randrange(6))])
                       for _ in range(rng.randrange(10))]
            r = self.audit(entries)
            unique_addresses = set(e['address'] for e in entries)
            unique_pairs = {(e['address'], k) for e in entries for k in e['storageKeys']}
            total = len(entries)*2400 + sum(len(e['storageKeys']) for e in entries)*1900
            unique = len(unique_addresses)*2400 + len(unique_pairs)*1900
            self.assertEqual(int(r['gas']['totalAccessListCharges']), total)
            self.assertEqual(int(r['gas']['uniqueSetCharges']), unique)
            self.assertEqual(int(r['gas']['totalRepeatedCharges']), total-unique)

    def test_refuses_signed_json_and_rlp(self):
        obj = a.reader.demo_object()
        for key in ('r', 's', 'yParity', 'from'):
            with self.assertRaises(ValueError):
                a.inspect(json.dumps(dict(obj, **{key: '0x1'})), 'json')
        raw = bytes.fromhex(a.reader.D.demo_transaction()[2:])
        fields, _ = a.reader.D.rlp_item(raw, 1)
        with self.assertRaises(ValueError):
            a.inspect('0x02' + a.reader.D.rlp_encode(fields + [b'', b'\x01', b'\x01']).hex())

    def test_refuses_ambiguous_malformed_and_oversize(self):
        for data in ('{"type":"0x2","type":"0x2"}', '{"inspection":{}}', '['*2000,
                     'x'*(a.MAX_INPUT_CHARS+1)):
            with self.assertRaises(ValueError):
                a.inspect(data, 'json')
        for entries in ([entry(ZTO, '0x11')], [entry('0x12')], [{'address': ZTO}]):
            with self.assertRaises(ValueError):
                self.audit(entries)
        for data in ('0x02c0', '0x02', '0x00', '', '0x02 ff'):
            with self.assertRaises(ValueError):
                a.inspect(data)
        with self.assertRaises(ValueError):
            a.inspect(text([]), 'summary')

    def test_oversize_rlp_integer(self):
        raw = bytes.fromhex(a.reader.D.demo_transaction()[2:])
        fields, _ = a.reader.D.rlp_item(raw, 1)
        fields[0] = 2**256
        with self.assertRaisesRegex(ValueError, 'uint256'):
            a.inspect('0x02' + a.reader.D.rlp_encode(fields).hex())

    def test_creation_does_not_change_list_charges(self):
        obj = json.loads(text([entry(ZTO, K1, K1)]))
        obj['to'] = None
        r = a.inspect(json.dumps(obj), 'json')
        self.assertEqual(r['inspection']['calldata']['status'], 'contract-creation')
        self.assertEqual(r['gas']['totalRepeatedCharges'], '1900')

    def test_cli_status_stdin_and_no_partial_output(self):
        script = str(Path(a.__file__).resolve())
        prefix = [sys.executable, '-B', script]
        for fmt in ('rlp', 'json'):
            demo = subprocess.run(prefix+['--demo', '--format', fmt], capture_output=True, text=True)
            self.assertEqual(demo.returncode, 0, demo.stderr)
            self.assertTrue(json.loads(demo.stdout)['hasRepeatedCharges'])
            piped = subprocess.run(prefix+['--stdin', '--format', fmt],
                                   input=a.demo_text(fmt)+'\r\n', capture_output=True, text=True)
            self.assertEqual(piped.returncode, 0, piped.stderr)
        bad = subprocess.run(prefix+['--stdin'], input='0x02c0', capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, '')


if __name__ == '__main__':
    unittest.main()
