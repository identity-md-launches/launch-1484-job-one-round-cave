#!/usr/bin/env python3
"""Compare a saved ZTO snapshot's block hash with a live Ethereum provider."""
import argparse
import datetime as dt
import importlib.util
import json
from pathlib import Path
import sys
import urllib.request

HERE = Path(__file__).resolve().parent
LIMIT = 4 * 1024 * 1024
DEFAULT_RPC = 'https://ethereum-rpc.publicnode.com'
USER_AGENT = 'Pepeolithic-Block-Audit/1.0 (read-only Ethereum block check)'


def sibling(name, filename):
    path = HERE.parent / name / filename
    spec = importlib.util.spec_from_file_location('block_audit_' + name.replace('-', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rpc = sibling('rpc-snapshot', 'rpc_snapshot.py')
pinned = sibling('pinned-snapshot', 'pinned_snapshot.py')


def strict_json(raw):
    if len(raw) > LIMIT:
        raise ValueError('snapshot or RPC response exceeds 4 MiB')

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result

    def constant(_value):
        raise ValueError('non-finite JSON number')

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('RPC redirects are refused')


def public_read(endpoint, method, params):
    rpc.validate_endpoint(endpoint)
    rpc.validate_request(method, params)
    payload = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method,
                          'params': params}, allow_nan=False).encode('utf-8')
    request = urllib.request.Request(endpoint, data=payload, headers={
        'Content-Type': 'application/json', 'Accept': 'application/json',
        'Accept-Encoding': 'identity', 'User-Agent': USER_AGENT})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(request, timeout=20) as response:
        if response.status != 200:
            raise ValueError('RPC requires HTTP 200')
        if response.headers.get('Content-Encoding', 'identity').lower() != 'identity':
            raise ValueError('compressed RPC response is unsupported')
        raw = response.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError('RPC response exceeds 4 MiB')
    envelope = strict_json(raw)
    if not isinstance(envelope, dict) or set(envelope) != {'jsonrpc', 'id', 'result'}:
        raise ValueError('expected a successful JSON-RPC response')
    return rpc.validate_response(envelope)


def audit(bundle, endpoint=DEFAULT_RPC, read=None):
    evidence = pinned.inspect(bundle)
    rpc.validate_endpoint(endpoint)
    read = read or (lambda method, params: public_read(endpoint, method, params))
    chain_id = read('eth_chainId', [])
    if chain_id != '0x1':
        raise ValueError('provider is not Ethereum mainnet')
    current = read('eth_getBlockByNumber', [bundle['block']['number'], False])
    checked_at = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    claimed = evidence['block_hash']
    if current is None:
        observed_hash = None
        status = 'unavailable'
    else:
        pinned.check_block(current, bundle['block']['number'])
        observed_hash = current['hash']
        status = 'matches' if observed_hash == claimed else 'different'
    return {
        'schema': 'zto-block-audit/1',
        'checked_at': checked_at,
        'endpoint': endpoint,
        'chain_id': chain_id,
        'block_number': evidence['block_number'],
        'snapshot_block_hash': claimed,
        'provider_block_hash': observed_hash,
        'status': status,
        'token': evidence['token'],
        'total_supply_base_units': evidence['total_supply_base_units'],
        'evidence_limits': ('One provider observation at check time. A match does not prove '
                            'provider honesty, independent corroboration, finality, or future canonicality.')
    }


def load_snapshot(path):
    if path == '-':
        raw = sys.stdin.buffer.read(LIMIT + 1)
    else:
        with open(path, 'rb') as source:
            raw = source.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError('snapshot exceeds 4 MiB')
    return strict_json(raw)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    demo = subs.add_parser('demo', help='recheck the retained real ZTO snapshot')
    demo.add_argument('--rpc', default=DEFAULT_RPC)
    check = subs.add_parser('check', help='recheck a pinned ZTO snapshot from a file or stdin')
    check.add_argument('snapshot', help='JSON path, or - for stdin')
    check.add_argument('--rpc', default=DEFAULT_RPC)
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            path = HERE.parent / 'direct-capture' / 'example-pinned-zto.json'
            bundle = load_snapshot(str(path))
            endpoint = args.rpc
        else:
            bundle = load_snapshot(args.snapshot)
            endpoint = args.rpc
        result = audit(bundle, endpoint)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result['status'] == 'matches' else 3
    except (ValueError, TypeError, KeyError, OSError, TimeoutError,
            urllib.error.URLError, RecursionError) as exc:
        # Avoid exposing URLs, response bodies, or provider diagnostics.
        print('block-audit: invalid snapshot, inconsistent response, or RPC failure',
              file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
