#!/usr/bin/env python3
"""Locate repeated access-list charges in original unsigned type-2 input."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'rpc-unsigned-reader'))
import rpc_reader as reader

MAX_INPUT_CHARS = reader.MAX_JSON_CHARS


def inspect(text, input_format='rlp'):
    """Preserve the original list and report occurrences; never rewrite input.

    Costs are explicitly the historical EIP-2930 schedule, not fork detection.
    Entry and key indices are zero-based positions in the original accessList.
    """
    if input_format not in ('rlp', 'json'):
        raise ValueError('input format must be rlp or json')
    if not isinstance(text, str) or len(text) > MAX_INPUT_CHARS:
        raise ValueError('input must be text within 512 Ki characters')
    evidence = (reader.inspect_json(text)['inspection'] if input_format == 'json'
                else reader.intent.interpret(text))
    tx = evidence['transaction']
    for name in reader.QUANTITIES:
        field = 'gasLimit' if name == 'gas' else name
        if int(tx[field]) >= 2**256:
            raise ValueError(field + ' exceeds uint256')
    addresses, pairs = {}, {}
    duplicate_addresses, duplicate_keys = [], []
    key_count = 0
    for index, entry in enumerate(tx['accessList']):
        address = entry['address']
        if address in addresses:
            duplicate_addresses.append({'entryIndex': index, 'address': address,
                                        'firstEntryIndex': addresses[address]})
        else:
            addresses[address] = index
        for key_index, key in enumerate(entry['storageKeys']):
            key_count += 1
            pair = (address, key)
            if pair in pairs:
                first_entry, first_key = pairs[pair]
                duplicate_keys.append({'entryIndex': index, 'keyIndex': key_index,
                                       'address': address, 'storageKey': key,
                                       'firstEntryIndex': first_entry,
                                       'firstKeyIndex': first_key})
            else:
                pairs[pair] = (index, key_index)
    entry_count = len(tx['accessList'])
    address_gas = 2400 * entry_count
    key_gas = 1900 * key_count
    repeated_address_gas = 2400 * len(duplicate_addresses)
    repeated_key_gas = 1900 * len(duplicate_keys)
    unique_gas = 2400 * len(addresses) + 1900 * len(pairs)
    return {
        'schema': 'access-list-audit/v1', 'inputFormat': input_format,
        'inspection': evidence, 'indexBase': 0,
        'schedule': {'name': 'EIP-2930', 'addressOccurrenceGas': '2400',
                     'storageKeyOccurrenceGas': '1900',
                     'source': 'https://eips.ethereum.org/EIPS/eip-2930'},
        'counts': {'addressOccurrences': entry_count, 'storageKeyOccurrences': key_count,
                   'uniqueAddresses': len(addresses), 'uniqueAddressStorageKeyPairs': len(pairs)},
        'duplicates': {'addresses': duplicate_addresses, 'storageKeys': duplicate_keys},
        'hasRepeatedCharges': bool(duplicate_addresses or duplicate_keys),
        'gas': {'addressCharges': str(address_gas), 'storageKeyCharges': str(key_gas),
                'totalAccessListCharges': str(address_gas + key_gas),
                'repeatedAddressCharges': str(repeated_address_gas),
                'repeatedStorageKeyCharges': str(repeated_key_gas),
                'totalRepeatedCharges': str(repeated_address_gas + repeated_key_gas),
                'uniqueSetCharges': str(unique_gas)},
        'warnings': list(evidence['warnings']) + [
            'Duplicates are permitted, not malformed. Indices refer to the unchanged original list.',
            'Fixed EIP-2930 schedule only; chain activation and current fork rules are unverified.',
            'Storage keys are scoped to their address; identical keys at different addresses are distinct.',
            'Unique-set charges are comparison arithmetic, not an edited transaction or guaranteed fee savings.',
            'No execution, actual accesses, already-warm addresses, gas used, refunds or calldata floor assessed. '
            'Removing entries can affect gas available to execution; no safety or equivalent outcome is claimed.',
        ],
    }


def demo_text(input_format):
    """Synthetic duplicate-address example; no invented storage layout or owner."""
    obj = reader.demo_object()
    obj['accessList'] = [{'address': reader.D.ZTO, 'storageKeys': []},
                         {'address': reader.D.ZTO, 'storageKeys': []}]
    if input_format == 'json':
        return json.dumps(obj)
    fields = [int(obj[name], 16) for name in reader.QUANTITIES[:5]]
    fields += [bytes.fromhex(obj['to'][2:]), int(obj['value'], 16),
               bytes.fromhex(obj['data'][2:]),
               [[bytes.fromhex(e['address'][2:]), []] for e in obj['accessList']]]
    return '0x02' + reader.D.rlp_encode(fields).hex()


def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--format', choices=('rlp', 'json'), default='rlp')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--demo', action='store_true')
    source.add_argument('--stdin', action='store_true')
    source.add_argument('--transaction')
    args = parser.parse_args(arguments)
    try:
        if args.demo:
            text = demo_text(args.format)
        elif args.stdin:
            text = sys.stdin.read(MAX_INPUT_CHARS + 1)
            if len(text) > MAX_INPUT_CHARS:
                raise ValueError('input exceeds 512 Ki characters')
            if args.format == 'rlp':
                text = text.removesuffix('\n').removesuffix('\r')
        else:
            text = args.transaction
        result = inspect(text, args.format)
    except (ValueError, UnicodeError) as error:
        print('error: ' + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
