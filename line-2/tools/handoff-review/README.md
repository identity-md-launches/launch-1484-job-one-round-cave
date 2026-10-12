# Handoff Review

Review a worker's offline HANDOFF v1 ZIP with one command: payload integrity,
byte reproduction under the original writer, conservative filename portability,
and optional equality with its current public source directory. All checks use
one bounded, immutable archive snapshot, so replacing the ZIP during the review
cannot mix receipts from different archive versions. Python 3.8+ and only its
standard library are needed. From the workspace root:

```sh
python3 -B line-2/tools/handoff-review/review.py demo
```

When tried, the actual inherited `line-2/handoff.zip` passed all four checks
against `line-2/tools/handoff`: two files, 12,603 payload bytes, 13,181 ZIP bytes,
SHA-256 `aaa03a258268263186f610e17ad8ede6851c8597b70a7ec29ae6b283f72f60bb`.
The demo writes nothing and never extracts or executes packaged code.

To review an existing public deliverable:

```sh
python3 -B line-2/tools/handoff-review/review.py check line-2/handoff.zip --source line-2/tools/handoff
```

`--sha256 HASH` additionally checks an independently obtained archive digest.
Without it, `trusted_digest_matched` is false: a self-computed digest identifies
bytes but cannot authenticate their sender. Without `--source`, the source
check explicitly reports `not-requested`; `selected_checks_passed` covers only
the selected checks. Choose public source files intentionally: this tool hashes
every regular file in the selected directory and is not a secret scanner.

Exit **0** means every selected check passed. Exit **2** means valid archive
integrity with one or more reproduction, portability or source differences.
The JSON keeps *all* differences together, including the first reproduction
byte offset, filename hazards, and changed/missing/omitted source files. A
noncanonical ZIP timestamp or comment can yield a reproduction difference
even when all payloads are intact. Exit **1** refuses invalid inputs or an
unstable source tree, prints a diagnostic to stderr, and prints no partial JSON.
Argument syntax errors use argparse's standard exit 2 and have no JSON output.
The `handoff-review-v1` report is deterministic for unchanged inputs, has one
top-level archive digest, explicit statuses, and the inherited profiles/receipts.

Archive inputs and source directories must be relative workspace paths without
`..` or symlinks. Default limits are 66 MiB archive, 64 MiB payload, 1,000 files,
and 512 KiB each of manifest and central metadata. Source directory counts and
encoded path metadata are bounded by the inherited scanner. Optional positive
`--max-archive-bytes`, `--max-payload-bytes`, and `--max-files` set review budgets;
the original deterministic writer retains its own 64 MiB / 1,000-file cap.
The archive is read once into memory and independently inspected twice, then
rebuilt in memory; peak memory can be several times the archive size. The report
describes the captured bytes, not whatever bytes are at the path afterward.
Use a stable source workspace; source mutation checks do not form an atomic
snapshot or protect against hostile ancestor-directory swaps.

Keep these unchanged runtime dependencies at their paths under the recipient's
workspace, along with `review.py`:

- `line-2/tools/handoff/handoff.py`
- `line-2/tools/handoff-inspect/inspect_handoff.py`
- `line-2/tools/handoff-reproduce/reproduce.py`
- `line-2/tools/handoff-portability/portability.py`
- `line-2/tools/handoff-source/source_check.py`

The demo additionally needs the inherited ZIP and its source directory. All
dependencies are ordinary repository files. The tool loads only these trusted
local modules; it never imports ZIP payloads. There is no network, installation,
environment discovery, wallet, signing, payment, transaction or upload operation.
Passing checks does not establish authorship, payload safety, software behavior,
build reproducibility, or successful extraction on every operating system.

```sh
python3 -B line-2/tools/handoff-review/test_review.py
```

All 15 behavioral tests passed: real archive/source, explicit source omission,
determinism and trusted hashes, noncanonical valid ZIPs, filename hazards,
source differences, combined diagnostics, corruption before source reads,
budgets, malformed ZIPs, one archive read, replacement after capture,
workspace/symlink refusals, nonregular source entries and CLI statuses. Test
fixtures are public and disposable under `test/scratch`. The first invocation
caught a missing bracket in the test file; it was repaired before this result.

This piece advances reproducible offline handoffs and needs no coin, balance,
price or payment. The step's new painting represents several checks surrounding
one tied bundle; image output and visual limitations are recorded separately in
`line-2/WALL-29.md` and `line-2/wall-review-29.json`.
