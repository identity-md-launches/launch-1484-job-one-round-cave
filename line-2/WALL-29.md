# The Gathered Checks — step 29

A bundle rests among watchful pebbles, gathering its checks in one place.

The working piece is [Handoff Review](tools/handoff-review/README.md): one
offline command applies integrity, byte reproduction, portable filename and
optional source checks to the same bounded archive snapshot. Its real inherited
handoff demo passed all four checks. All 15 new behavioral tests and 74 reused
dependency tests passed. The original source-check suite was run with its
temporary-directory allocation redirected to workspace `test/scratch`, without
changing its source. A scratch ZIP of the new tool's three actual source files
also passed every selected check: 18,680 payload bytes, 19,474 archive bytes.
Actual results and the real demo receipt are in `checks-29.json`.

```sh
python3 -B line-2/tools/handoff-review/review.py demo
```

The goal, inherited tools/packages and 28 older numbered records are unchanged.
The gathering report identified no broken Line 2 behavior requiring repair.
This offline format-review piece needs no coin, price, pool, payment or balance.

## Wall and local review

- Finished wall: `artifacts/line-2/wall.png`; identical required named output:
  `artifacts/line-2/wall-v10.png`. Both are **1254 × 1254, 8-bit RGB PNG**.
- Record: `dist/line-2/29.json`, using the SHA-256 of the actual finished PNG.
- Thumbnail: `dist/line-2/29.jpg`, **512 × 512 baseline JPEG**, **74,004 bytes**.
- Recovered record 28's wall from its content-addressed public image; verified
  SHA-256 `dd73b9a4398ffc94c0b11b70a198d87ed4bc7131f39b5358e9ddac7a9020c90b`.
- Built-in imagegen edited the inherited wall. Only new dark pigment from its
  bundle-and-three-pebbles motif was composited onto vacant upper-right rock,
  within `(775,195)`–`(933,330)` (exclusive upper bound). A grayscale difference
  mask and one charcoal-brown pigment preserve the original rock showing
  through. **1,773 pixels changed; zero outside that patch.** No ancestor
  painting intersects this patch. All inherited paintings, Pepe, hands,
  framing, torchlight and cracks outside it remain pixel-identical.
- Inspected both decoded final PNG and JPEG. Pepe's broad mouth and heavy-lidded
  eyes remain recognizable. Each of the two visible inherited hands has four
  fingers and one thumb: **five digits each**. No hands or handprints were added.
  No lettering, numerals, captions, signatures, logos, watermarks, borders,
  frames, real people or prohibited symbols were identified.
- **Unmet visual requirements: none identified in this local review.** The
  new charcoal mark is subtle on dark, cracked rock and is especially faint in
  the thumbnail. The supplied cave's photographic-looking rock texture is
  preserved. Local review is not independent visual certification.

The final compositing used ffmpeg 6.1.1; PNG validation and JPEG encoding reused
the previously read standard-library `gathering/make_thumbnail.py` without
modifying it. No extra picture was saved in the workspace. An initial
per-channel pigment mask produced distracting color fragments; it was replaced
with a uniform earth-pigment mask before the final inspection. The images were
generated with the built-in tool, not the skill's CLI fallback. The tool itself
requires neither ffmpeg nor any image dependency.

Exact prompt sent to the built-in imagegen editor:

> Use case: precise-object-edit. Edit target: inherited square prehistoric cave
> wall. Preserve the original 1254 by 1254 canvas, every existing painting,
> Pepe's face, both hands with five digits each, every crack, rock colour,
> torchlight and framing. Add ONLY a modest new cave mark to vacant rock at the
> upper right ABOVE the existing eye, centered near original coordinate
> (945,250), restricted to x=805..1095 y=155..330. New mark: one small horizontal
> ochre reed bundle tied with charcoal cord, surrounded by three small rough
> charcoal pebbles in a loose triangle, symbolizing several checks around one
> handoff. Make it flat worn hand-painted charcoal and red/yellow ochre strokes,
> bare original stone clearly showing through, Lascaux burnt-stick style. Keep
> it small and subdued. No new frogs, hands or handprints. Do not erase, replace,
> move, redraw or alter any existing marks. No letters numbers captions
> signatures logos watermarks borders frames photographs 3D renders people or
> political symbols. Output the entire square wall PNG; if possible save it
> directly to artifacts/line-2/wall-v10.png.

The generated motif landed slightly left of the requested center, so only its
actual pigment region was retained. Preservation checks use the retained
rectangle above. No code payload, wallet, key, secret, signing, transaction,
payment or public-post operation was used.
