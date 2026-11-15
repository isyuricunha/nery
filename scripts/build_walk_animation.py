#!/usr/bin/env python3
"""Deterministic Nery walk animation source.

Petdex v2 is limited to 8 native frames per walking direction. The Astro
preview uses a separate 16-frame atlas to reduce temporal stutter without
cross-fading feet or generating motion-estimation ghost limbs.

All 16 frames are separately drawn and curated, with the same head/upper
body overlaid for exact facial continuity, at 192x208 RGBA. The two
directions mirror the ENTIRE sprite frame. No anatomical partial mirroring.

Source: pet/frames-generated/semantic-v3/walk/00.png through 15.png
Output: pet/nery/walk-16.webp (1536x832, 8 columns by 4 rows).
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"pet/frames-generated/semantic-v3/walk"
W,H=192,208
COUNT=16

def load_motion_frames() -> list[Image.Image]:
    frames=[]
    for i in range(COUNT):
        path=SOURCE/f"{i:02}.png"
        if not path.is_file():
            raise FileNotFoundError(f"Walk inbetween frame missing: {path}")
        frame=Image.open(path).convert("RGBA")
        if frame.size != (W,H):
            raise ValueError(f"Invalid walk source {path}: {frame.size}; expected {(W,H)}")
        alpha=frame.getchannel("A")
        if not alpha.getbbox():
            raise ValueError(f"Empty walk frame: {path}")
        frames.append(frame)
    return frames

def native_frames(right: bool) -> list[Image.Image]:
    # Native state has precisely 8 frames; sample every other high-quality
    # key in the website's 16-frame timeline.
    frames=load_motion_frames()[::2]
    if right:
        frames=[ImageOps.mirror(f) for f in frames]
    return frames

def build_smooth_walk_atlas(out_dir: Path) -> Path:
    source=load_motion_frames()
    atlas=Image.new("RGBA",(W*8,H*4))
    for base_row,frames in (
        (0,[ImageOps.mirror(frame) for frame in source]),
        (2,source),
    ):
        for col,frame in enumerate(frames):
            cell_row=base_row+col//8
            cell_col=col%8
            atlas.alpha_composite(frame,(cell_col*W,cell_row*H))
    out_dir.mkdir(parents=True,exist_ok=True)
    target=out_dir/"walk-16.webp"
    # Use lossless to preserve alpha and avoid bright fringe compression.
    atlas.save(target,"WEBP",lossless=True,method=6)
    print(f"Built smooth web walking atlas: {target}, {atlas.size}, 16 frames/direction")
    return target

if __name__=="__main__":
    build_smooth_walk_atlas(ROOT/"pet/nery")
