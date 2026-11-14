# Nery Mizuki final frame provenance

Pack: `nery/pet.json` and `nery/spritesheet.webp`; diagnostic PNG also included.
Atlas: 1536×2288 RGBA, 8×11 cells of 192×208. Nine states use six frames each;
columns 6–7 and rows 9–10 are transparent. Playback uses the requested approximately
183 ms per frame in the Petdex player; the specified pet.json schema has no timing field.
Frame numbering below is zero-based. “Position 3” means column 3 (the fourth frame).

| Row/state | Shipped art |
| --- | --- |
| 0 idle | Six approved nery-sleeping bob frames; eyes already closed, so no extra blink. |
| 1 running-right | Stride/passing walk cycle: frames from `stride-a.png` (wide stride) and `stride-b.png` (passing), with the mirrored stride providing leg alternation; horizontal flip preserved for the right-facing row. |
| 2 running-left | Same stride/passing cycle, unflipped (strict left profile, one eye visible in every frame). |
| 3 waving | Six newly generated full-body right-arm wave drawings from wave/01–06.png; no flipped art. |
| 4 jumping | Six newly generated crouch, launch, apex, descent/landing approach, landing crouch, settle drawings from jump/01–06.png; no flipped art. |
| 5 failed | Approved thinking bob; frame 3 uses generated half-closed eyelids composited into the approved pose. |
| 6 waiting | Approved coffee bob; frame 3 uses generated gentle eye-squeeze patches in the approved pose. |
| 7 running | Same stride/passing walk cycle as the running-left row (unflipped). |
| 8 review | Approved cat bob; frame 3 uses generated closed-eyelid patches in the approved pose. |

No signature-gate fallback frames were necessary. Approved bob frames above are
intentional requested sources, not failed-generation replacements. Four additional
fullbody/happy blink drawings are retained in frames-generated/blink/01,02,04,05.png;
they are not substituted into unrelated portrait poses. Pose-matched composite
variants live in blink/variants/. All non-eye pixels in these variants stay approved.

## Generation and extraction

Used the user-specified Agnes img2img CLI, eight API calls total (below ten).
Exact prompts are preserved in frames-generated/prompts.json. References were the
approved happy/fullbody poses and character sheet; each portrait edit additionally
used its own approved thinking/coffee/cat reference. Raw outputs remain in strips/.
No credentials were printed or copied.

The first wave sheet returned 4×2 rather than the requested 3×2. It contained eight
complete right-arm poses; six real drawings were curated in order: top columns
0,1,2, then bottom columns 2,1,0. The retry was rejected for switching arms and
including non-wave poses. The first jump sheet lacked a center-bottom character;
the complete 3×2 retry supplies all six final jump drawings. No empty cell ships.

scripts/split_cells.py supplies edge-connected flood-fill extraction, not global
chroma keying. scripts/prepare_pet_frames.py records the curated cell selection,
uses a conservative six-level background tolerance to preserve dark hoodies,
and applies generated eyelids through feathered local masks on approved poses.
One constant scale per cycle preserves relative sizes; jump adds a vertical arc.
The running-row build path is unchanged.

## Visual qualifications

- All six wave frames are real separate generated drawings, but the wrist/arm
  differences are subtle; the movement reads as a gentle wave rather than broad swings.
- Jump frame 3 (fourth frame) reads more like a low landing approach/lunge than
  an unmistakably airborne fall. This is the main pose uncertainty.
- Coffee and cat already have closed eyes; their inserted eye-squeeze changes
  are intentionally subtle. The thinking blink is more visible.
- The new wave proportions are slightly taller than the jump drawings; within
  each sequence a constant scale is used. The signature gate passes every frame,
  but it does not prove perfect anatomical or stylistic identity.

## Validation

python3 scripts/build_petpack.py && python3 scripts/validate_petpack.py exited 0.

    PET PACK VALID: /home/ubuntu/ella-repos/nery/pet/nery
      atlas 1536x2288 | 9 states x 6 frames | pet.json ok

Additional decoded-WebP checks confirmed transparent unused columns and rows 9–10.
Visual contact sheet: pet/preview/final-contact-sheet.jpg.
