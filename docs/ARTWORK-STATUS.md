# Nery Mizuki — artwork status and limitations

## Provenance

The approved character sheet (1536x1024) is the original approved artwork. The eight pose crops are cut from that sheet at their native resolution; alpha channels were extracted from the approved pixels (OpenCV-assisted with manual cleanup) and composited. **Nothing was redrawn, regenerated or upscaled.**

Avatars (128/256/512) are reductions of the original portrait crop (745x905), not new paintings.

## Native sizes

The sheet is larger than its individual figures. Native pose sizes (from the kit manifest):

| Pose | Native size (px) |
| --- | --- |
| Portrait | 745x905 |
| Full body | 195x403 |
| Happy | 222x198 |
| Thinking | 214x197 |
| Sleeping | 312x228 |
| Coding | 225x218 |
| Coffee | 225x222 |
| With cat | 294x198 |

**Do not upscale poses for large banners or print**: the full-body pose at 195 px wide degrades past its native size. Large-format or high-resolution poses require new original artwork, produced and approved through this repository.

## Known imperfections

- Background removal was semi-automatic: fine edges (hair tips, dark clothing) can carry small artifacts.
- The opaque original crops are included in `source/original-crops/` for reference and edge refinement.
- No EXIF metadata was found in the inspected files.
- The preview composition is illustrative artwork, not an application screenshot.

## Import integrity

The original delivery ZIP (`nery-mizuki-kit-v1.zip`, 35 entries) is recorded with SHA-256 `ec4ee4a77f1253d9b074e55ea8d2f0c138ca58fad34f6fa75f0fd35a846cb657` and kept outside the repository. The Mnerys import script (`scripts/import_nery_kit.py` in the Mnerys repo) verifies a local copy against that hash.
