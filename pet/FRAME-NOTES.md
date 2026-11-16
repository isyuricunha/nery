# Nery Mizuki — locomotion v5

This follow-up changes **only left/right walking**. Idle, greeting, jumping,
failure, waiting, working and review retain every drawing and exposure from
milestone `2c0aeff`. The original approved static kit is also unchanged.

## Appearance and sources

The existing Idle sprite is the master for body proportions, clothing and
illustration style. The selected rounded A candidate is a secondary reference.
The earlier skinny articulated candidate was rejected; it is not a runtime
input. Locomotion uses the same copper hair, amber eyes, cream bows, short
torso, charcoal hoodie, shorts, fuller chibi legs and tall dark socks.

- Other action sources: `pet/frames-generated/motion-v4/source/`.
- Walking source artwork and registered parts:
  `pet/frames-generated/motion-v5/rig/`.
- Retained Idle/rounded references and original six-part sheet are in that
  directory. `shin-source.png` corrects the sock height against Idle.
- Generation briefs and provenance: `motion-v5/provenance.json`.
- Reproducible extraction: `scripts/prepare_walk_parts.py`.
- Animation and joint registration: `scripts/walk_motion.py`.

The walking artwork is rendered from registered illustrated parts. Two-bone
leg motion preserves segment length and forward knee bending. Rigid piece
rotations, small torso weight shifts, arm counter-swing and a fixed body scale
avoid the old unrelated-pose jumps. Overlapping knee interiors use the same
illustrated skin texture, retaining the outer silhouette without cap rings.
Premultiplied alpha and supersampling prevent pale edge halos.

## Passada and timing

Each direction has **32 frames at 30 ms**, a 960 ms cycle. The two legs
alternate support. A planted foot moves linearly against page travel;
the companion covers 30 screen pixels per cycle at its half-size display.
Swing motion matches horizontal stance velocity at takeoff and landing.
Foot lift and angle start/end with zero vertical/angular velocity.

The complete figure is mirrored for the opposite direction. There is no
leg-only reflection, optical-flow reconstruction or opacity crossfade
between poses. The native eight-frame walking preview now uses uniform
120 ms exposures, without an extra hold on its final frame.

## Formats

All cells are 192 × 208.

| Asset | Geometry | Use |
| --- | --- | --- |
| `pet/nery/spritesheet.webp` / `.png` | 1536 × 2288; 8 × 11 cells | Petdex v2 |
| `pet/nery/motion.webp` | 6144 × 1872; 32 × 9 cells | Full web sequences |
| `pet/nery/motion.json` | Exposure, loops, static poses and native sampling | Shared playback contract |
| `pet/nery/walk-32.webp` | 1536 × 1664; 8 × 8 cells | Full walking atlas |
| `pet/nery/walk-16.webp` | 1536 × 832; 8 × 4 cells | Compatibility sample |

Native frame counts remain **6 / 8 / 8 / 4 / 5 / 8 / 6 / 6 / 6**.
The website has 12 frames per non-walking action and 32 per walking direction,
148 frames total. Native walking takes every fourth full walking frame;
the compatibility atlas takes every second. Native client timing is owned
by that client, so browser enhancements are not automatically transferred.
Optional native cursor-look cells in rows 9–10 remain transparent.

## Preserved Failed correction

Failure cel 6 (index 5) contained a disconnected neighboring fragment. It
biased the old alignment by approximately 33 pixels. Extraction isolates the
character and anchors its planted feet. The failure alignment tests reject
that exact sideways-teleport regression. Locomotion v5 preserves the corrected
failure drawings and timing.

## Build and validation

Install `scripts/requirements.txt`, then run from repository root:

```bash
python scripts/prepare_walk_parts.py
python scripts/build_petpack.py
python scripts/validate_petpack.py
python scripts/validate_walk_animation.py
python scripts/validate_motion.py
python scripts/test_petpack_regressions.py
python scripts/test_motion_alignment.py
python scripts/test_walk_motion.py
python scripts/test_walk_scope.py
python scripts/render_pet_previews.py
cd website
pnpm test
pnpm lint
pnpm check
pnpm build
```

The checks cover geometry, alpha, palette, grounded support, whole-body
mirroring, native/web sampling, bone lengths, alternating steps and continuous
takeoff/landing velocity. The world-space stance check rejects foot skating;
silhouette similarity alone cannot establish correct walking.

`preserved-states.json` stores hashes of every non-walking drawing plus its
exposures, loops and native sampling from `2c0aeff`. `test_walk_scope.py`
requires all seven other actions to match that saved state exactly.

## Visual review

`pet/preview/walk-review.html` embeds **actual GIF playback at normal speed**
beside unchanged Idle, Waving and Waiting references, plus the prior walk
and both new walking directions. The website serves it at `/walk-review.html`.

`pet/preview/motion-review.html` provides all nine states, slower playback,
pause, restart and frame stepping. It embeds the shipped atlas and manifest
and works offline. `web-*.gif` files show full web sequences; the original
per-state GIF filenames show native samples. `walk-32.gif` is the full cycle.

The gait was reviewed through browser GIF playback and sampled compositor
frames over multiple cycles, then checked in the live canvas renderer.
Automated checks do not certify subjective artistic perfection. No native
third-party client installation or production publication is implied.
