# Nery Mizuki — Petdex motion audit and sources

This document records the frame-by-frame motion review, source selection,
technical validation and **known remaining visual limitations**. New motion
assets are a local working candidate until the rights holder reviews them.
Original mascot drawings are preserved in `assets/mascot/kit-v1/`.

## Native format and website animation

- **Petdex v2 atlas:** `pet/nery/spritesheet.webp`; 1536×2288,
  eight columns and eleven rows, 192×208 cells. States have frame counts
  **6 / 8 / 8 / 4 / 5 / 8 / 6 / 6 / 6** in rows 0–8.
- **Website-exclusive walking atlas:** `pet/nery/walk-16.webp`; 1536×832,
  eight columns and four rows. Rows 0–1 contain 16 walking-right drawings;
  rows 2–3 contain 16 walking-left drawings. The asset uses lossless WebP
  transparency to avoid compression color fringes.
- The Petdex atlas receives **every second** web walk drawing (8 per
  direction). The native consumer cannot access the website's 16
  frames without its own extension. Frame index 0 in the site is the same
  pose as frame 0 in native; the relative order and scale are reproducible.
- The website displays 16 drawn poses per gait cycle (60 ms per drawing),
  matched to 64 px per cycle and 66.7 px/s page movement. There is **no
  frame-to-frame opacity crossfade** of legs, motion-flow reconstruction,
  partial-leg horizontal reflection, or random face replacement.
- `prefers-reduced-motion` displays still poses. State-to-state fades
  are restricted to non-walking states and do not blend right and left
  walking directions. Cache-busting hashes are generated for both
  WebP atlases during the site build.

Petdex v2's optional cursor-look grid in rows 9–10 (16 cells) **remains
transparent**. Full head-look tracking is not implemented.

## Audit by action row

| Row | State | Source and actual motion | Remaining concern |
| --- | --- | --- | --- |
| 0 | `idle` (6) | Approved full-body upright stance; tiny upper-body breathing | Almost static by design, not a sleeping/giant close-up |
| 1 | `running-right` (8) | **Whole-frame mirror** of left gait keys | Native 8-key stepping is less smooth than the website |
| 2 | `running-left` (8) | Eight separately drawn keys selected from a 16-pose website cycle | A few lower-body transitions are still abrupt |
| 3 | `waving` (4) | Four raised-hand and arm poses | Motion relatively subtle; existing wave source preserved |
| 4 | `jumping` (5) | Crouch, launch, apex, descent, stand | Silhouette changes quickly between some keys |
| 5 | `failed` (8) | Surprise → *new in-between pose with lowered hands* → sad posture | Two main expressions remain visibly distinct |
| 6 | `waiting` (6) | Hands clasped → *new fists-apart in-between* → palms open → return | Hand/head movement is intentionally distinct from waving |
| 7 | `running` (6) | Agent **working** at laptop (typing), **not walking** | Subtle finger movements |
| 8 | `review` (6) | Clipboard review and pencil movement | Subtle facial/hand movement |

## Walk source audit: all 16 frames

The prior sprite cycle repeated 4–5 unrelated generated drawings. Specifically,
the return from frame 7 to frame 0 and intermediate poses jumped abruptly,
feet lifted without apparent support, and generated face/hair edges changed
between poses. A white-background input also caused visible white hair/shoe
fringes. The old `opposite_stride()` had *flipped only the legs*, reversing
shoe anatomy; the new builder does not use it.

The proposed 16-pose sequence was created by **redrawing every pose**
based on a walking guide, extracting alpha once, applying a shared scale and
ground baseline, and compositing the **same exact approved upper-body
pixels** onto every frame, leaving the individually drawn legs intact.

Frame numbers below refer to
`pet/frames-generated/semantic-v3/walk/00.png` – `15.png`.

| Frame | Visual movement | Frame | Visual movement |
| --- | --- | --- | --- |
| 00 | Wide contact / transfer | 08 | Other-leg forward contact |
| 01 | Contact deceleration | 09 | Push-off begins |
| 02 | Knee load with rear heel rising | 10 | Heel lift and leg transfer |
| 03 | Feet pass near each other | 11 | Trailing leg swinging |
| 04 | Swinging knee lifted | 12 | Free leg extends forward |
| 05 | Leg swing continuing | 13 | Next foot advances |
| 06 | Supporting foot while lifted knee passes | 14 | Forward knee raised |
| 07 | Forward foot steps into contact | 15 | Return toward start contact |

**Quality metrics on the website's 16-key lower-body silhouettes**
(`scripts/validate_walk_animation.py`): adjacent silhouette IoU averages
~0.45; the wrap from frame 15 → 0 is ~0.83. Some transitions still have
low overlap (~0.16, notably keys 11–12 and 12–13), so these must be
**visually inspected**, not called perfect. Gait art from individual model
redraws is not the same as a studio-authored 2D rig.

I evaluated two other candidate methods, **optical-flow interpolation** and
an ad hoc joint-warp leg rig, but rejected them after visual inspection:
they caused double shoes, anatomy breaks or ugly knees. The resulting
experimental artifacts live only in `~/chatgpt/nery/probes/` and are **not
integrated into the project**. A sequence reordered for numerical similarity
was rejected because silhouette similarity is not proof of correct step
order.

## Sources

- Approved source kit: `assets/mascot/kit-v1/transparent/`.
- Original generated motion sources and prompts: `pet/frames-generated/`
  (not modified or deleted).
- Prior curated semantic poses:
  `pet/frames-generated/semantic-v2/` (preserved for comparison).
- New **16×192×208 RGBA walking keys**:
  `pet/frames-generated/semantic-v3/walk/`.
- New intermediate `failed`/`waiting` keys:
  `pet/frames-generated/semantic-v3/failed/transition.png`,
  `pet/frames-generated/semantic-v3/waiting/transition.png`.
- Full raw resolution generation outputs, contact sheets, timeline tests,
  visual screenshots and exploratory rejects are in server work directory
  `~/chatgpt/nery/images/`, `~/chatgpt/nery/probes/` and
  `~/chatgpt/nery/tests/`, separately from production files.
- A pre-change backup of build logic and original WebP is under
  `~/chatgpt/nery/backups/pre-walk-v3/`.

## Deterministic build and QA

Run from repo root:

```bash
python3 scripts/build_petpack.py
python3 scripts/validate_petpack.py
python3 scripts/validate_walk_animation.py
python3 scripts/test_petpack_regressions.py
python3 scripts/render_pet_previews.py
cd website && pnpm lint && pnpm check && pnpm build
```

`scripts/build_walk_animation.py` can also regenerate
`pet/nery/walk-16.webp` alone.

The validators check: atlas dimensions and alpha, color identity, grounded
shoe support in every walk key, untouched canonical face pixels,
full-body left/right mirroring, alpha edge fringes, 16-key source ↔
native ↔ web consistency, loop closure and semantic states. Negative
regressions introduce known defects and require rejection.

**Visual QA in a real browser** uses
`~/chatgpt/nery/tests/browser-qa.mjs` with local headless Chromium,
including page JavaScript errors, actual canvas samples for walking
and screenshots of the other action states. Review actual animations
in `pet/preview/walk-16.gif` and per-state GIFs. These static and
automated checks do not certify subjective naturalness; the final
quality decision belongs to the rights holder.

No commit, push or production deploy is performed by these scripts.
