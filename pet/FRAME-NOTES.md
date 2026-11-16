# Nery Mizuki — motion v4

Local artwork revision of 2026-11-16, prepared at the rights holder's request.
The original approved static kit remains unchanged. This animation revision
is available for visual review; it has not been published or installed in a
third-party Petdex client.

## What changed

All nine action rows now use a new, consistently dressed set of cels. The
open charcoal hoodie, cream undershirt, shorts, socks and sneakers stay
consistent through idle, walking, greeting, jumping, failure, waiting,
typing and review. The working state is a standing laptop pose, at the
same body scale as the other front-facing actions.

The walk was redrawn against a sixteen-pose guide, with alternating support,
passing and contact positions. Both directions mirror the entire figure.
There is no leg-only reflection, optical-flow interpolation, opacity blend
between cels, or frozen upper-body patch. Small drawn hair and head movements
are retained, with a stable head anchor and grounded soles.

The greeting includes raising the hand, waving and lowering it. The jump
includes anticipation, takeoff, ascent, apex, descent, landing and recovery.
Failure gradually lowers the expression and holds the final pose. Waiting
opens and lowers both palms in a loop. Typing and clipboard checking use
small hand motions and blinks.

## Formats

| Asset | Geometry | Use |
| --- | --- | --- |
| `pet/nery/spritesheet.webp` / `.png` | 1536 × 2288, 8 × 11 cells | Petdex v2 compatibility |
| `pet/nery/motion.webp` | 3072 × 1872, 16 × 9 cells | Full website action sequences |
| `pet/nery/motion.json` | Shared exposures, loops, static poses and native sample indices | Website and preview timing |
| `pet/nery/walk-16.webp` | 1536 × 832, 8 × 4 cells | Standalone walking atlas |

Every cell is 192 × 208. Native frame counts remain
**6 / 8 / 8 / 4 / 5 / 8 / 6 / 6 / 6**. The website has **12 cels per
non-walking action and 16 per walking direction**, 116 cells in total.
Native clients cannot display the additional web cels without supporting
the separate format. Their playback timing is controlled by the client.
The native four-frame wave uses raised-hand wave keys; the web twelve-frame
wave additionally includes the arm raising and lowering.

The optional cursor-look cells in native rows 9–10 remain transparent;
cursor-look tracking is outside this action-animation revision.

## Reproducible sources

- Final cel sheets: `pet/frames-generated/motion-v4/source/`.
- Walking guide: `source/walk-pose-guide.png` in that directory.
- Generation briefs: `pet/frames-generated/motion-v4/prompts.json` and
  `revision-prompts.json`.
- Slicing, common per-action scale, head anchoring, floor alignment and
  atlas packing: `scripts/motion_assets.py`.
- Previous source drawings remain in the earlier `frames-generated/`
  directories. They are not inputs to the v4 build.

The build only slices, uniformly scales and translates complete cels,
removes almost invisible alpha noise, and mirrors complete figures. Jump
height offsets are explicit and reproducible. No original static kit
artwork is overwritten or upscaled for the website's kit gallery.

## Website behavior

The canvas renderer reads a single atlas and the shared exposure manifest.
It selects a drawn cel, without crossfades or ghost limbs. Page travel and
walking phase share the same distance counter, including acceleration and
deceleration. At page edges the walker stops before changing direction.

Wave and jump play once and return to idle after the final recovery frame.
Failure holds its final expression; the other selected states loop. Clicking
Nery restarts the full greeting, including on repeated clicks. A greeting
stops the page walker so a waving pose cannot slide across the floor.

Reduced motion uses representative static poses and stops page travel.
Hidden tabs stop the animation clock. Asset URLs hash both the cel atlas
and timing manifest, preventing stale drawing/timing combinations.

## Build and checks

Install the Python dependencies from `scripts/requirements.txt`, then run:

```bash
python scripts/build_petpack.py
python scripts/validate_petpack.py
python scripts/validate_walk_animation.py
python scripts/validate_motion.py
python scripts/test_petpack_regressions.py
python scripts/render_pet_previews.py
cd website
pnpm install --frozen-lockfile
pnpm test
pnpm lint
pnpm check
pnpm build
```

The validators cover geometry, transparent padding, native/web sample
agreement, whole-body mirroring, planted sole support, head continuity,
visible palette, unique drawings and ascending/descending jump order.
The original eight negative regressions are retained.

The walk's adjacent lower-body silhouette IoU is approximately **0.372
minimum / 0.584 average**, versus 0.161 / 0.453 in the previous atlas.
The loop seam is 0.481, with real contact motion rather than a repeated
endpoint. These are continuity diagnostics, not proof of correct anatomy.
Head silhouette overlap between adjacent walking cels stays above 0.94.

## Visual review

Open `pet/preview/motion-review.html` in a browser. This standalone review
embeds the shipped web atlas and manifest, works offline, and provides all
nine states, slow playback, pause, restart and individual frame stepping.
The website also serves it at `/motion-review.html` after preparing assets.

- `pet/preview/web-states.gif`: simultaneous overview of all web actions.
- `pet/preview/web-*.gif`: full web sequences with matching timing.
- `pet/preview/web-contact-sheet.jpg`: every shipped web cel.
- Existing per-state filenames and `final-contact-sheet.jpg`: native Petdex
  sampling, kept distinct from the fuller web animations.

Visual and automated checks do not guarantee subjective perfection. The
drawings retain small hand-drawn differences; the final visual acceptance
belongs to the rights holder. No commit, push or production deploy is
performed by these scripts.
