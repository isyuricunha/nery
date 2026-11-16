#!/usr/bin/env python3
"""Generate web walk atlas from the same cels as the Petdex pack."""
from pathlib import Path
from PIL import Image, ImageOps
from motion_assets import ROOT, normalized

def load_motion_frames() -> list[Image.Image]:
    return normalized('walk')

def native_frames(right: bool) -> list[Image.Image]:
    frames = load_motion_frames()[::2]
    return [ImageOps.mirror(f) for f in frames] if right else frames

def build_smooth_walk_atlas(out_dir: Path) -> Path:
    atlas = Image.new('RGBA',(1536,832))
    source = load_motion_frames()
    for row,seq in ((0,[ImageOps.mirror(f) for f in source]),(2,source)):
        for i,frame in enumerate(seq):
            atlas.alpha_composite(frame,((i%8)*192,(row+i//8)*208))
    out_dir.mkdir(parents=True,exist_ok=True)
    target = out_dir/'walk-16.webp'
    atlas.save(target,'WEBP',lossless=True,method=6)
    return target

if __name__=='__main__':
    print(build_smooth_walk_atlas(ROOT/'pet/nery'))
