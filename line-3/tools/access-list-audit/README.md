# Access-list audit

Locate repeated addresses and storage keys in an **original unsigned EIP-1559
transaction**. The report preserves the full decoded transaction, gives every
repeated occurrence's zero-based position and its first occurrence, and separates
unique-set charges from repeated charges under the fixed EIP-2930 schedule.
Identical storage keys at different addresses are distinct. Duplicates are legal;
this tool reports them without rewriting or rejecting the transaction.

From the repository root, with Python 3.10 or newer:

```sh
python3 -B line-3/tools/access-list-audit/access_audit.py --demo
```

Tried locally: exit 0, destination `ZTO`, two occurrences of the real ZTO address,
4800 gas of access-list charges, 2400 gas of repeated charges. Entry 1 points to
entry 0. The demo extends the inherited **synthetic**, unsigned ZTO `totalSupply()`
example with duplicate address-only entries. Fees, nonce and access list are
examples, not a live transaction or claims about ZTO storage. Nothing is sent.
The JSON demo (`--demo --format json`) gives the same inspection and arithmetic.

For your own complete unsigned input, use `--stdin` (RLP hex by default),
`--format json --stdin`, or `--transaction TEXT`. JSON requires every field;
there is no sender, state lookup, defaulting or signature support. A precomputed
summary is not accepted as input. Exit 0 means inspection completed, including
when duplicates exist; exit 2 means malformed/unsupported input, with no partial
JSON on stdout. Input is bounded to 512 Ki characters and inherits the decoder's
128 KiB envelope, depth and item limits. Gas values are exact decimal strings;
bounded counts and indices are JSON integers.

`inspect(text, input_format='rlp')` exposes the same report as a Python API.
`inspection.transaction.accessList` retains order and duplicates, normalized to
lowercase byte identities. In `duplicates.storageKeys`, `firstEntryIndex` and
`firstKeyIndex` locate the first identical **address/key pair**, even across
repeated address entries. `gas.totalAccessListCharges` equals
`gas.uniqueSetCharges + gas.totalRepeatedCharges`.

## Checks and dependencies

```sh
python3 -B -m unittest discover -s line-3/tools/access-list-audit -v
```

All 14 tests passed, including 100 seeded cost partitions, cross-entry and
within-entry duplicates, byte-case equivalence, distinct-address key scope,
JSON/RLP agreement, preserved order, creation, malformed and signed input,
integer bounds and CLI exit codes. The tool uses only the Python standard
library plus three unchanged committed sibling modules: `rpc-unsigned-reader`,
`erc20-intent` and `zto-eip1559-decoder`. Keep those directories beside this one.
No package installation, environment variables, keys, wallets or network needed.

## Interpretation limits

The fixed schedule is 2400 gas per address occurrence and 1900 per storage-key
occurrence, including duplicates: [EIP-2930 specification](https://eips.ethereum.org/EIPS/eip-2930).
The tool does not detect which chain fork applies. These are access-list charges
only, not total intrinsic gas, gas used, ETH fees or token prices. The existing
`gas-budget` companion supplies explicit historical whole-transaction lower bounds.

Unique-set comparison is not a proposed replacement transaction or a promise of
fee savings. This audit does not establish actual accesses, already-warm addresses,
execution, refund or calldata-floor effects, balance, nonce, inclusion or safety
to sign. Changing intrinsic gas can change gas available during execution.
No deduplicated envelope, signatures or transactions are produced or sent.
