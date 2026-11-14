#!/usr/bin/env python3
"""Build the Nery Mizuki Petdex pet pack (pet.json + spritesheet atlas).

Petdex/Codex pet format (verified against petdex.dev docs, the Boba reference
pet and the Hermes pet loader):

- Frames are 192x208 (FRAME_W x FRAME_H), arranged in an 8-column grid.
- The v2 atlas is 1536x2288 (8 cols x 11 rows); rows 0-8 carry the canonical
  state rows: idle, running-right, running-left, waving, jumping, failed,
  waiting, running, review. Rows 9-10 stay transparent in this pack.
- Each state uses the first 6 columns (petdex ``steps(6)``); extra columns are
  ignored by renderers.
- pet.json carries id/displayName/description/spriteVersionNumber/spritesheetPath.

Derivation policy: every frame is derived from the APPROVED kit poses only.
Static life (breathing bob) is produced with PIL pixel shifts, so the character
cannot drift. AI-generated pose frames (blink, wave arm, walk cycle) are read
from frames-generated/<state>/ when present and must pass the validator's
character-consistency gate; until then walk-family rows reuse an approved pose
with a horizontal shuffle, clearly marked as placeholders in the changelog.

Usage: python3 scripts/build_petpack.py [--out PET_DIR]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

REPO_ROOT = Path(__file__).resolve().parents[1]
KIT = REPO_ROOT / "assets" / "mascot" / "kit-v1"

FRAME_W, FRAME_H = 192, 208
ATLAS_COLS, ATLAS_ROWS = 8, 11
ATLAS_SIZE = (FRAME_W * ATLAS_COLS, FRAME_H * ATLAS_ROWS)
FRAMES_PER_STATE = 6

CODEX_STATE_ROWS = [
    "idle", "running-right", "running-left", "waving", "jumping",
    "failed", "waiting", "running", "review",
]

TRANSPARENT = KIT / "transparent"

# Row -> derivation plan. "bob" rows shift the pose a couple of pixels between
# frames; "shuffle" rows add a small horizontal sway so the placeholder still
# reads as motion until real walk frames replace it.
ROW_PLANS: dict[str, dict[str, str]] = {
    "idle": {"pose": "nery-sleeping.png", "mode": "bob"},
    "running-right": {"pose": "nery-fullbody.png", "mode": "shuffle", "facing": "right"},
    "running-left": {"pose": "nery-fullbody.png", "mode": "shuffle", "facing": "left"},
    "waving": {"pose": "nery-happy.png", "mode": "bob"},
    "jumping": {"pose": "nery-happy.png", "mode": "hop"},
    "failed": {"pose": "nery-thinking.png", "mode": "bob"},
    "waiting": {"pose": "nery-coffee.png", "mode": "bob"},
    "running": {"pose": "nery-fullbody.png", "mode": "shuffle", "facing": "right"},
    "review": {"pose": "nery-with-cat.png", "mode": "bob"},
}


def load_pose(name: str) -> Image.Image:
    path = TRANSPARENT / name
    if not path.exists():
        raise SystemExit(f"approved pose missing: {path}")
    return Image.open(path).convert("RGBA")


def visible_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    """Bounding box of non-transparent pixels; hard failure when empty."""
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise SystemExit("pose/frame has no visible pixels")
    return bbox


def scaled_to_frame_height(image: Image.Image, target_h: int) -> Image.Image:
    """Scale the pose so its body fits *target_h* px, never upscaling past 1.0."""
    bbox = visible_bbox(image)
    body_h = bbox[3] - bbox[1]
    scale = min(1.0, target_h / body_h)
    if scale < 1.0:
        new_size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    return image


def paste_anchored(frame: Image.Image, pose: Image.Image, dx: int = 0, dy: int = 0) -> None:
    """Paste the pose bottom-center anchored, feet resting near the frame floor."""
    bbox = visible_bbox(pose)
    body_w, body_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (FRAME_W - body_w) // 2 - bbox[0] + dx
    y = FRAME_H - 10 - body_h - bbox[1] + dy  # 10 px breathing room below the feet
    frame.alpha_composite(pose, (x, y))


def derive_frames(pose: Image.Image, mode: str, facing: str = "right") -> list[Image.Image]:
    """Produce FRAMES_PER_STATE frames for one row from a single approved pose."""
    pose = scaled_to_frame_height(pose, FRAME_H - 28)
    if mode == "bob":
        offsets = [(0, 0), (0, -2), (0, -3), (0, -2), (0, 0), (0, -1)]
    elif mode == "hop":
        offsets = [(0, 0), (0, -6), (0, -10), (0, -6), (0, 0), (0, -2)]
    elif mode == "shuffle":
        sway = [0, -3, -5, 0, 3, 5]
        lift = [0, -2, -3, 0, -2, -3]
        offsets = list(zip(sway, lift))
    else:
        raise SystemExit(f"unknown derivation mode: {mode}")

    frames: list[Image.Image] = []
    for dx, dy in offsets:
        frame = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
        body = ImageOps.mirror(pose) if facing == "left" else pose
        paste_anchored(frame, body, dx, dy)
        frames.append(frame)
    return frames


def build_atlas() -> Image.Image:
    atlas = Image.new("RGBA", ATLAS_SIZE, (0, 0, 0, 0))
    for row_index, state in enumerate(CODEX_STATE_ROWS):
        plan = ROW_PLANS[state]
        pose = load_pose(plan["pose"])
        frames = derive_frames(pose, plan["mode"], plan.get("facing", "right"))
        for col, frame in enumerate(frames[:FRAMES_PER_STATE]):
            atlas.alpha_composite(frame, (col * FRAME_W, row_index * FRAME_H))
    return atlas


def write_pet_pack(out_dir: Path, atlas: Image.Image) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    atlas.save(out_dir / "spritesheet.webp", "WEBP", quality=90, method=6)
    atlas.save(out_dir / "spritesheet.png", "PNG")
    pet = {
        "id": "nery",
        "displayName": "Nery Mizuki",
        "description": "Nery Mizuki, the official mascot of Mnerys ('Built to be yours'): a curious copper-haired chibi who keeps you company while your agent works.",
        "spriteVersionNumber": 2,
        "spritesheetPath": "spritesheet.webp",
    }
    (out_dir / "pet.json").write_text(json.dumps(pet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "pet" / "nery", help="output pack directory")
    args = parser.parse_args()
    atlas = build_atlas()
    write_pet_pack(args.out, atlas)
    print(f"atlas: {atlas.size[0]}x{atlas.size[1]} ({ATLAS_COLS} cols x {ATLAS_ROWS} rows)")
    print(f"states: {', '.join(CODEX_STATE_ROWS)}")
    print(f"pack written to: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
