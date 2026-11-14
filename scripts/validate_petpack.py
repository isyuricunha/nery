#!/usr/bin/env python3
"""Validate the Nery Mizuki Petdex pack.

Checks (goal contract):
1. pet.json: required fields, id matches the folder, spritesheetPath resolves.
2. Atlas: exact v2 geometry (1536x2288, 8 cols x 11 rows of 192x208).
3. Frames: the first 6 columns of every canonical state row are non-empty,
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
FRAMES_PER_STATE = 6
MIN_BODY_PIXELS = 900
MIN_SIGNATURE_PIXELS = 24
MAX_HUE_DISTANCE = 0.35  # total-variation distance vs the row's first frame
# Motion gate: run-family rows must show REAL leg movement between consecutive
# frames (a "walking in place" cycle with near-identical frames fails the build).
RUN_ROWS = {"running-right", "running-left", "running"}
MIN_LEG_MOTION_PIXELS = 2000


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
                    for col in range(FRAMES_PER_STATE)
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
                for col in range(1, FRAMES_PER_STATE):
                    dist = histogram_distance(base, hue_histogram(row_frames[col]))
                    if dist > MAX_HUE_DISTANCE:
                        failures.append(f"{state} frame {col}: hue drift vs frame 0 (distance {dist:.2f} > {MAX_HUE_DISTANCE})")
                if state in RUN_ROWS:
                    for col in range(1, FRAMES_PER_STATE):
                        lower = slice(FRAME_H // 2, FRAME_H)
                        diff = np.abs(row_frames[col][lower] - row_frames[col - 1][lower]).sum(axis=-1) > 0.16
                        motion = int(diff.sum())
                        if motion < MIN_LEG_MOTION_PIXELS:
                            failures.append(
                                f"{state} frame {col}: walking in place (leg motion {motion} px < {MIN_LEG_MOTION_PIXELS})"
                            )

    if failures:
        print("PET PACK INVALID:")
        for failure in failures[:40]:
            print(f"  - {failure}")
        if len(failures) > 40:
            print(f"  ... and {len(failures) - 40} more")
        return 1
    print(f"PET PACK VALID: {pack}")
    print(f"  atlas {ATLAS_SIZE[0]}x{ATLAS_SIZE[1]} | {len(CODEX_STATE_ROWS)} states x {FRAMES_PER_STATE} frames | pet.json ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
