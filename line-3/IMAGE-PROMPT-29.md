# The Repeated Seeds

Final image: built-in `image_gen` edit of the recovered mark-28 wall. Its input
SHA-256 was `3b018092639fc3335483254964e07fd34d739f6d17544132e0861effb8cce679`.
The installed Replicate tool was tried first for an isolated motif; it returned
`ERROR: Error: empty Replicate output item` without an image. Built-in generation
then succeeded. The returned PNG bytes were written directly to the required
workspace output; no external generated-image file was read.

Exact successful prompt:

> Edit target: the existing local cave wall shown in the conversation. Preserve the entire square 1254x1254 wall, rock, cracks, light and all ancestral paintings exactly. Add only six small rough dark charcoal seed daubs as two vertical trails of three oval seeds each on vacant rock at x=1020..1100 y=565..705, to the right of the frog and below the existing sieve. They symbolize repeated provisions counted twice. No other changes. All existing paintings including Pepe's wide mouth, heavy-lidded eyes and both five-digit hands stay untouched. Do not add any hands, figures, text, letters, numbers, logos, border or watermarks. Ancient handmade worn earth pigment only, no 3D. Save resulting PNG in the workspace at artifacts/line-3/wall-v10.png if file saving is supported.

The generated edit moved the motif slightly up and left and altered ancestral
texture. Finalization retained only substantially darker pigment in vacant
`[965,520,1045,661]` (left, top, right, bottom), restoring every other original
pixel. The generated draft was overwritten by the final whole wall. Both final
PNGs are identical 1254×1254 RGB images; the required preview is a 512×512 JPEG.

Manual review: both images decoded and displayed. All prior paintings and the
rock, cracks, colors, light and framing remain. Pepe's heavy-lidded eyes and wide
mouth remain; the two visible inherited hands each have five digits (four fingers
and a thumb). No hands or stencils were added. No text, numbers, signatures,
logos, watermarks, frames, people or prohibited symbols were observed. The six
seed marks are irregular charcoal pigment with bare stone showing through.
No known unmet visual requirement. Limitations: pigment extraction leaves worn,
slightly jagged edges; the inherited rock texture looks photographic but was
preserved. This is local visual review, not independent certification.
