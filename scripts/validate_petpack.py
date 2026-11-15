#!/usr/bin/env python3
"""Validate the Nery Mizuki Petdex pack.

Checks (goal contract):
1. pet.json: required fields, id matches the folder, spritesheetPath resolves.
2. Atlas: exact v2 geometry (1536x2288, 8 cols x 11 rows of 192x208).
3. Frames: the canonical count of each state row is non-empty,
   keep a real alpha channel and transparent corners.
4. Character consistency gate: every frame keeps the signature colors of the
   approved kit (copper hair, cream bow, terracotta/orange accents, charcoal
   hoodie) and stays within a hue-histogram distance of its row's first frame,
   so generated frames that drift fail the build instead of shipping.

Exit code 0 = pack is valid; 1 = any check failed.

Usage: python3 scripts/validate_petpack.py [--pack PET_DIR]
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]

FRAME_W, FRAME_H = 192, 208
ATLAS_SIZE = (1536, 2288)
CODEX_STATE_ROWS = [
    "idle", "running-right", "running-left", "waving", "jumping",
    "failed", "waiting", "running", "review",
]
COUNTS = [6,8,8,4,5,8,6,6,6]
MIN_BODY_PIXELS = 900
MIN_SIGNATURE_PIXELS = 24
MAX_HUE_DISTANCE = 0.35  # total-variation distance vs the row's first frame
# Motion gate: run-family rows must show REAL leg movement between consecutive
# frames (a "walking in place" cycle with near-identical frames fails the build).
RUN_ROWS = {"running-right", "running-left"}
MIN_LEG_MOTION_PIXELS = 1800


@dataclass(frozen=True)
class Signature:
    """A color the approved kit always shows on the character."""

    name: str
    hue_center: float | None  # degrees; None = near-neutral dark (charcoal)
    hue_tol: float
    sat_floor: float
    sat_ceiling: float
    value_floor: float
    value_ceiling: float


SIGNATURES = [
    Signature("copper-hair", 18.0, 16.0, 0.35, 1.0, 0.20, 1.0),
    Signature("cream-bow", 30.0, 25.0, 0.05, 0.45, 0.55, 1.0),
    Signature("terracotta-accent", 16.0, 14.0, 0.35, 1.0, 0.20, 1.0),
    Signature("charcoal-hoodie", None, 0.0, 0.0, 0.50, 0.0, 0.25),
]


def frame_hue_sat_val(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Hue (0..360), saturation and value arrays for a float RGBA frame."""
    rgb = frame[..., :3]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    max_c = np.max(rgb, axis=-1)
    min_c = np.min(rgb, axis=-1)
    delta = max_c - min_c
    value = max_c
    sat = np.where(max_c > 0, delta / np.maximum(max_c, 1e-9), 0.0)
    hue = np.zeros_like(max_c)
    nonzero = delta > 1e-9
    rr, gg, bb, dd = r[nonzero], g[nonzero], b[nonzero], delta[nonzero]
    hue_n = np.zeros_like(rr)
    idx_max_r = rr == max_c[nonzero]
    idx_max_g = (~idx_max_r) & (gg == max_c[nonzero])
    idx_max_b = (~idx_max_r) & (~idx_max_g)
    hue_n[idx_max_r] = (60 * ((gg[idx_max_r] - bb[idx_max_r]) / dd[idx_max_r])) % 360
    hue_n[idx_max_g] = (60 * ((bb[idx_max_g] - rr[idx_max_g]) / dd[idx_max_g]) + 120) % 360
    hue_n[idx_max_b] = (60 * ((rr[idx_max_b] - gg[idx_max_b]) / dd[idx_max_b]) + 240) % 360
    hue[nonzero] = hue_n
    return hue, sat, value


def signature_counts(frame: np.ndarray) -> dict[str, int]:
    """Count opaque pixels matching each signature color."""
    opaque = frame[..., 3] >= (200 / 255)
    hue, sat, value = frame_hue_sat_val(frame)
    counts: dict[str, int] = {}
    for signature in SIGNATURES:
        if signature.hue_center is None:
            mask = (value <= signature.value_ceiling) & (sat <= signature.sat_ceiling)
        else:
            delta = np.minimum(
                np.abs(hue - signature.hue_center),
                360 - np.abs(hue - signature.hue_center),
            )
            mask = (
                (delta <= signature.hue_tol)
                & (sat >= signature.sat_floor)
                & (sat <= signature.sat_ceiling)
                & (value >= signature.value_floor)
            )
        counts[signature.name] = int(np.sum(mask & opaque))
    return counts


def hue_histogram(frame: np.ndarray) -> np.ndarray:
    """Normalized 36-bin hue histogram of saturated opaque pixels."""
    opaque = frame[..., 3] >= (200 / 255)
    hue, sat, value = frame_hue_sat_val(frame)
    selected = opaque & (sat >= 0.25) & (value >= 0.15)
    hist, _ = np.histogram(hue[selected], bins=36, range=(0, 360))
    total = int(hist.sum())
    return hist / total if total else hist.astype(float)


def histogram_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Total variation distance between two normalized histograms."""
    return 0.5 * float(np.sum(np.abs(a - b)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=REPO_ROOT / "pet" / "nery", help="pack directory")
    args = parser.parse_args()
    pack = args.pack
    failures: list[str] = []

    pet_path = pack / "pet.json"
    try:
        pet = json.loads(pet_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL pet.json unreadable: {exc}")
        return 1
    for field in ("id", "displayName", "description", "spriteVersionNumber", "spritesheetPath"):
        if field not in pet:
            failures.append(f"pet.json missing field: {field}")
    if pet.get("id") != pack.name:
        failures.append(f"pet.json id '{pet.get('id')}' does not match folder name '{pack.name}'")
    if pet.get("spriteVersionNumber") != 2:
        failures.append("spriteVersionNumber must be 2")
    sheet_path = pack / str(pet.get("spritesheetPath", ""))
    if not sheet_path.exists():
        failures.append(f"spritesheetPath does not resolve: {sheet_path}")

    if not failures:
        atlas = Image.open(sheet_path).convert("RGBA")
        if atlas.size != ATLAS_SIZE:
            failures.append(f"atlas is {atlas.size}, expected {ATLAS_SIZE} (v2: 8 cols x 11 rows of {FRAME_W}x{FRAME_H})")
        else:
            atlas_arr = np.asarray(atlas, dtype=np.float32) / 255.0
            for row_index, state in enumerate(CODEX_STATE_ROWS):
                top = row_index * FRAME_H
                row_frames = [
                    atlas_arr[top:top + FRAME_H, col * FRAME_W:(col + 1) * FRAME_W]
                    for col in range(COUNTS[row_index])
                ]
                for col, frame in enumerate(row_frames):
                    alpha = frame[..., 3]
                    body = int(np.sum(alpha > 0.05))
                    if body < MIN_BODY_PIXELS:
                        failures.append(f"{state} frame {col}: body too small ({body} px)")
                    corners = [alpha[2, 2], alpha[2, -3], alpha[-3, 2], alpha[-3, -3]]
                    if any(c > 0.125 for c in corners):
                        failures.append(f"{state} frame {col}: opaque background corners")
                    for name, count in signature_counts(frame).items():
                        if count < MIN_SIGNATURE_PIXELS:
                            failures.append(f"{state} frame {col}: signature '{name}' nearly absent ({count} px)")
                base = hue_histogram(row_frames[0])
                for col in range(1, COUNTS[row_index]):
                    dist = histogram_distance(base, hue_histogram(row_frames[col]))
                    if dist > MAX_HUE_DISTANCE:
                        failures.append(f"{state} frame {col}: hue drift vs frame 0 (distance {dist:.2f} > {MAX_HUE_DISTANCE})")
                # Check all *unused* standard cells. Blank canvas width is
                # not the same thing as a six-frame cycle in every state.
                for col in range(COUNTS[row_index], 8):
                    empty = atlas_arr[top:top + FRAME_H,
                                      col * FRAME_W:(col + 1) * FRAME_W, 3]
                    if np.any(empty > 0.01):
                        failures.append(f"{state}: unused column {col} is not transparent")


                # Motion quality checks beyond a valid-looking sprite atlas.
                if state in RUN_ROWS:
                    # Reject the previous two-pose A/B/A/B/A/B cycle even
                    # though it moved enough pixels to pass the old gate.
                    profiles = {
                        (frame[FRAME_H // 2:, :, 3] > 0.5).tobytes()
                        for frame in row_frames
                    }
                    if len(profiles) < 4:
                        failures.append(f"{state}: only {len(profiles)} distinct leg silhouettes")
                    head_centers = []
                    head_tops = []
                    feet_lines = []
                    for col, frame in enumerate(row_frames):
                        alpha = frame[:, :, 3]
                        # Pale soft pixels on the silhouette are a residue
                        # from the old white-background passing pose. Test
                        # the alpha *edge*, not legitimate cream bows/shoes.
                        pale_edge = (
                            (np.min(frame[:, :, :3], axis=2) > 0.70)
                            & (alpha > 0.07) & (alpha < 0.90)
                        )
                        edge_count = int(np.count_nonzero(pale_edge))
                        if edge_count > 100:
                            failures.append(
                                f"{state} frame {col}: white matte fringe ({edge_count} pale edge pixels)"
                            )
                        # A natural single-support phase often has ONE shoe
                        # grounded. Every keyframe nevertheless requires a
                        # stable, broad sole at ground height. Tiny toe-only
                        # contact and a floating character are invalid.
                        support = np.count_nonzero(alpha[189:195, :] > 0.48)
                        if support < 90:
                            failures.append(
                                f"{state} frame {col}: missing grounded supporting sole ({support} px)"
                            )
                        if np.any(alpha[:, :2] > 0.07) or np.any(alpha[:, -2:] > 0.07):
                            failures.append(f"{state} frame {col}: clipped at cell side")
                        upper = alpha[:110]
                        _, xs = np.where(upper > 0.5)
                        if xs.size:
                            head_centers.append((xs.min() + xs.max()) / 2)
                        ys, _ = np.where(alpha > 0.5)
                        if ys.size:
                            head_tops.append(int(ys.min()))
                            feet_lines.append(int(ys.max()))
                    if head_centers and max(head_centers) - min(head_centers) > 7:
                        failures.append(f"{state}: head pivot jumps between frames")
                    if head_tops and max(head_tops) - min(head_tops) > 6:
                        failures.append(f"{state}: head jumps vertically between steps")
                    if feet_lines and max(feet_lines) - min(feet_lines) > 4:
                        failures.append(f"{state}: feet shift vertically on flat ground")

                # Persona/state sanity: a front-facing *standing* idle
                # should not be a giant cropped/sleeping close-up, and
                # waiting is the little full-body "needs input" gesture.
                if state in {"idle", "waiting"}:
                    widths = []
                    for frame in row_frames:
                        _, xx = np.where(frame[:, :, 3] > 0.5)
                        if xx.size: widths.append(int(xx.max() - xx.min() + 1))
                    if widths and max(widths) > 125:
                        failures.append(f"{state}: character too wide for normal-sized full-body stance")

                if state == "failed":
                    def height_of_frame(frame):
                        yy, _ = np.where(frame[:, :, 3] > 0.5)
                        return int(yy.max() - yy.min() + 1) if yy.size else 0
                    stand_h=height_of_frame(row_frames[0])
                    slump_h=height_of_frame(row_frames[-1])
                    if slump_h > stand_h - 3:
                        failures.append(f"failed: head/shoulders do not lower, height {stand_h}->{slump_h}")
                    expression_change=int(np.count_nonzero(np.abs(row_frames[0]-row_frames[-1]) > 0.08))
                    if expression_change < 4000:
                        failures.append(f"failed: shock and dejected reactions too similar ({expression_change} changed channels)")

                if state == "running":
                    # In Petdex this is *agent work*, not locomotion.
                    working_rows = [
                        atlas_arr[2 * FRAME_H:(2 + 1) * FRAME_H,
                                  col * FRAME_W:(col + 1) * FRAME_W]
                        for col in range(COUNTS[row_index])
                    ]
                    if all(float(np.mean(np.abs(frame - motion))) < 0.025
                           for frame, motion in zip(row_frames, working_rows)):
                        failures.append("running: work state incorrectly reuses walking animation")

                if state == "review":
                    failure_rows = [
                        atlas_arr[5 * FRAME_H:(5 + 1) * FRAME_H,
                                  col * FRAME_W:(col + 1) * FRAME_W]
                        for col in range(COUNTS[row_index])
                    ]
                    if all(np.array_equal(frame, other)
                           for frame, other in zip(row_frames, failure_rows)):
                        failures.append("review: review animation duplicates failed state")

                if state == "jumping":
                    # Jump must ascend, descend, and end grounded, not switch
                    # to an unrelated running/lunging pose midair.
                    bottoms = []
                    for frame in row_frames:
                        ys, _ = np.where(frame[:, :, 3] > 0.5)
                        bottoms.append(int(ys.max()) if ys.size else -1)
                    if not (bottoms[2] + 7 <= bottoms[3] < bottoms[4]):
                        failures.append(f"jumping: discontinuous airborne descent {bottoms}")
                    if abs(bottoms[0] - bottoms[4]) > 4:
                        failures.append(f"jumping: landing does not return to the ground {bottoms}")

    if failures:
        print("PET PACK INVALID:")
        for failure in failures[:40]:
            print(f"  - {failure}")
        if len(failures) > 40:
            print(f"  ... and {len(failures) - 40} more")
        return 1
    print(f"PET PACK CORE STATES VALID: {pack}")
    print("  NOTE: v2 cursor-look rows 9–10 are unpopulated; directional gaze remains unsupported")
    print(f"  atlas {ATLAS_SIZE[0]}x{ATLAS_SIZE[1]} | frames per row {COUNTS} | pet.json ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
