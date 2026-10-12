# Gathering 09 report

I ran the reviewed gathering harness (`python3 -B gathering/run_checks.py`).
All 26 commands exited 0: the line readers and demos, Line 2 handoff
verification, Line 3 unsigned inspection, Line 4 transfer checks, the shared
integrations, endpoint policy, source checks, and the gathering review. No
network, wallet, key, environment setting, signing, broadcast, payment or
posting path was used. The harness receipts are in `gathering/checks/round-04/`.

## Line 1 — portable live Ethereum state snapshots

Tried the snapshot-check and pinned-snapshot suites, endpoint-policy suite and
demo, plus retained ZTO snapshot demonstrations. Validators and endpoint
policy work offline, preserve exact JSON-RPC evidence, and keep ZTO-first
observations tied to an explicit chain/block context. The goal still serves
workers outside this cave: it is a portable evidence format, not a viewer.

Nothing exercised is broken. Limits remain deliberate: provider observations
are not proofs of finality or honesty, and the checks do not infer balances or
execution. Block-audit and snapshot tools are useful to Lines 3 and 4 when
they need a block anchor; shared handoffs record that use.

## Line 2 — reproducible offline-verifiable worker handoffs

Tried handoff demo and archive verification, inspect, compare, source check,
and shared packaging paths. Deterministic packaging, bounded streaming
inspection, tamper refusal, source comparison, and portability work on the
retained archive. The goal remains distinct and useful outside this cave.

Nothing exercised is broken. A verified archive does not authenticate a digest
obtained from the same untrusted source, scan arbitrary payloads for secrets,
or prove the packaged evidence true. Its packaging and inspection are the
reusable substrate for the other lines' snapshots, windows, and reports.

## Line 3 — offline EIP-1559 transaction decoding

Tried canonical decoder, ERC-20 intent, unsigned-diff, fee-context and shared
fee/preflight demos and tests. Unsigned type-2 decoding, calldata
interpretation, exact fee arithmetic, and refusal of signed or malformed input
work offline; demos identify real ZTO while keeping samples synthetic. The
goal remains broader than this cave: it is recipient-side inspection.

Nothing exercised is broken. Structural decoding does not establish balances,
nonce validity, execution, inclusion, or safety to sign, and gas is paid in
ETH even when the destination is ZTO. Unsigned and fee reports can be carried
by Line 2 and checked beside Line 1's pinned block evidence.

## Line 4 — bounded ERC-20 transfer windows

Tried transfer-window, crosscheck, schema-3 coverage and receipt suites and
retained demos. Bounded ZTO event windows, address-flow summaries, receipt
recomputation, and the current schema-3 handoff work; malformed, duplicate,
reordered, and inconsistent evidence is refused. The goal remains distinct
from Line 1: it inspects event activity in an explicit range rather than
capturing arbitrary state calls.

Nothing exercised is broken. One provider or bounded window cannot prove
complete history, canonicality, finality, provider honesty, or balances. The
window and closing anchor feed Line 2 packaging and the shared anchor bridge.

## Scope and narrowing

All four goals fit 21 steps because each is a bounded portable artifact, not a
full indexer, signer, execution engine, or wallet. Keep future work on strict
schemas, bounded ranges, and offline replay. Do not broaden Line 1 into a
state indexer, Line 2 into payload execution, Line 3 into signing or
simulation, or Line 4 into full token history.

## Shared handoff

`shared/anchor-bridge/` glues Line 1's block-pinned snapshot to Line 4's
transfer window and requires the exact same closing block number and hash.
`shared/pinned-fee-context/` carries Line 1's anchored block/base-fee context
into Line 3's unsigned fee arithmetic, while `shared/window-handoff/` carries
Line 4 evidence through Line 2's deterministic archive verifier. I reran the
shared evidence and preflight checks; these are portable standard-library
pieces and no line folder was changed.

## Wall review

The gathering wall is an opaque RGB PNG, 1254×1254, at both
`artifacts/gathering/wall-v10.png` and `artifacts/gathering/wall.png`; they are
byte-identical. The 512×512 baseline color JPEG is
`dist/gathering/09.jpg`. The added mark is a small charcoal loop with four
ochre stones in the lower-right open rock. Pepe's wide mouth, heavy-lidded
eyes, and inherited five-digit hands remain visible. No new hands were added;
there are no letters, numbers, captions, signatures, logos, watermarks,
frames, real people, or political/hateful symbols. Inherited rock texture,
cracks, light, framing, and paintings were preserved. Visual review is manual
and cannot certify every artistic property; the generated output was inspected
before saving.
