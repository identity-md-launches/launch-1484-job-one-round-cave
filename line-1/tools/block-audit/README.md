# Block audit

Recheck the block identity carried by a saved `pinned-zto-snapshot/1` against one live Ethereum JSON-RPC provider. This helps a recipient notice when a provider now returns a different hash at the snapshot's block height, or no block there. It checks mainnet chain ID before checking the block. It reuses the line's strict ZTO snapshot inspector and uses only Python's standard library; sibling `rpc-snapshot` and `pinned-snapshot` folders must remain present.

One command uses the retained real ZTO snapshot and performs two read-only public RPC requests:

```sh
python3 -B line-1/tools/block-audit/block_audit.py demo
```

For a received snapshot, pipe JSON or give a local path:

```sh
python3 -B line-1/tools/block-audit/block_audit.py check snapshot.json
cat snapshot.json | python3 -B line-1/tools/block-audit/block_audit.py check -
```

Use `--rpc https://eth.drpc.org` to select another public endpoint. The default is `https://ethereum-rpc.publicnode.com`. Both requests send this tool's own User-Agent, explicitly disable proxy discovery and redirects, bound the response, and never read environment settings. Exit 0 means the reported hashes match, 3 means they differ or the height is unavailable, and 1 means the snapshot, chain ID, or request failed. Output includes the snapshot's ZTO supply so the audited evidence remains connected to the saved observation.

## What happened when tried

The retained example snapshot validates offline, and the seven tests exercise matching, differing, unavailable, wrong-chain, malformed and changed-height responses without opening a network connection:

```sh
python3 -B line-1/tools/block-audit/test_block_audit.py
```

At `2026-10-12T23:17:49Z`, the live demo checked the retained ZTO observation at block **26179157** against PublicNode, after confirming chain ID `0x1`. Both the snapshot and provider returned `0x3d555940233dd8faf3cc6d8225a3563c32a9bd696182d30c6875ed8e5ad2ed19`; status was `matches`. The ZTO supply in the saved snapshot is **1000000000000000000000000000** base units. This observation is dated and should be rerun when a recipient needs a current check.

The result is one provider's observation at check time. A matching hash does not establish provider honesty, independent corroboration, finality, or what the chain will contain later. This is a recheck of the exact saved block height, not a new token-state read.

## Round 29 painting

**The Shared Moment:** “Two stones return to one remembered height.” The added motif joins two unequal stones to one anchored point and short arcs. It is confined to vacant lower-center rock `(515,915)–(765,1035)`; zero pixels changed outside that patch. The final wall is an **8-bit RGB PNG, 1254×1254, 3,833,464 bytes**, SHA-256 `1476d8d9e63de6ceb4ec2a01a9923b14c460a4c9a4cfa9a98f1ba7317e1fcca5`. Its matching thumbnail is a **512×512 baseline JPEG, 71,585 bytes**. Visual review found no added text, digits, signature, logo, watermark, border, frame, person or prohibited symbol. The inherited Pepe still has heavy-lidded eyes, a wide mouth, and four finger strokes plus an opposing thumb on each hand. The inherited cave background remains photographic-looking, the visual limitation retained with the ancestral wall; the new mark may be subdued at thumbnail size. Local visual review is not independent certification; details are in `line-1/wall-review-29.json`.
