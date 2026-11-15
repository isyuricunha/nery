#!/usr/bin/env python3
"""Negative regression tests for the pet pack's motion quality gate.

Never touches the live atlas. Each intentionally broken copy is validated
in an isolated temporary directory, and must be rejected for the right reason.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "pet/nery/spritesheet.webp"
VALIDATOR = ROOT / "scripts/validate_petpack.py"
CELL_W, CELL_H = 192, 208


def replace_cell(atlas: Image.Image, row: int, source_col: int, dest_col: int) -> None:
    source = atlas.crop((
        source_col * CELL_W, row * CELL_H,
        (source_col + 1) * CELL_W, (row + 1) * CELL_H,
    ))
    atlas.paste(source, (dest_col * CELL_W, row * CELL_H))


def expect_rejected(atlas: Image.Image, reason: str) -> None:
    with TemporaryDirectory(prefix="nery-pet-test-") as temp:
        pack = Path(temp) / "nery"
        pack.mkdir()
        data = json.loads((ROOT / "pet/nery/pet.json").read_text(encoding="utf-8"))
        (pack / "pet.json").write_text(json.dumps(data), encoding="utf-8")
        atlas.save(pack / "spritesheet.webp", "WEBP", quality=90, method=6)
        run = subprocess.run(
            [sys.executable, str(VALIDATOR), "--pack", str(pack)],
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
        if run.returncode == 0 or reason not in run.stdout:
            raise AssertionError(
                f"Expected validator failure '{reason}', got exit={run.returncode}\n"
                f"{run.stdout}\n{run.stderr}"
            )


def main() -> None:
    original = Image.open(ATLAS).convert("RGBA")

    repeated = original.copy()
    for row in (1, 2):
        for col in range(2, 8):
            replace_cell(repeated, row, col % 2, col)
    expect_rejected(repeated, "only 2 distinct leg silhouettes")
    print("PASS: rejects an A/B/A/B repeated fake gait")

    impossible_descent = original.copy()
    replace_cell(impossible_descent, 4, 0, 3)
    expect_rejected(impossible_descent, "discontinuous airborne descent")
    print("PASS: rejects a teleporting jump/descent")

    reused_working = original.copy()
    for col in range(6):
        replace_cell(reused_working, 2, col, col)  # left row source unchanged
        source = original.crop((col * CELL_W, 2 * CELL_H,
                                (col + 1) * CELL_W, 3 * CELL_H))
        reused_working.paste(source, (col * CELL_W, 7 * CELL_H))
    expect_rejected(reused_working, "work state incorrectly reuses walking animation")
    print("PASS: detects a working state that just repeats walking")

    old_idle = original.copy()
    # Construct an intentionally oversized portrait from the real idle
    # frame. The test does not depend on personal backups or outside paths.
    for col in range(6):
        raw=original.crop((col*CELL_W,0,(col+1)*CELL_W,CELL_H))
        alpha_box=raw.getchannel("A").getbbox()
        body=raw.crop(alpha_box)
        oversized=body.resize((168,body.height),Image.Resampling.LANCZOS)
        giant=Image.new("RGBA",(CELL_W,CELL_H))
        giant.alpha_composite(oversized,((CELL_W-168)//2,CELL_H-body.height-12))
        old_idle.paste(giant,(col*CELL_W,0))
    expect_rejected(old_idle, "character too wide")
    print("PASS: rejects a giant portrait as the idle animation")

    # The entire character (head, shoes, arms, skirt) must be mirrored
    # together to face right. A partial-leg mirror was the prior root cause.
    from PIL import ImageOps, ImageChops
    lossless=Image.open(ROOT / "pet/nery/spritesheet.png").convert("RGBA")
    for col in range(8):
        right=lossless.crop((col*CELL_W,CELL_H,(col+1)*CELL_W,2*CELL_H))
        left=lossless.crop((col*CELL_W,2*CELL_H,(col+1)*CELL_W,3*CELL_H))
        if ImageChops.difference(right,ImageOps.mirror(left)).getbbox():
            raise AssertionError(f"walking pose {col} is NOT a complete-body horizontal mirror")
    print("PASS: all eight directional frames mirror the WHOLE character")

    code=(ROOT/"scripts/build_petpack.py").read_text(encoding="utf-8")
    if "def opposite_stride" in code:
        raise AssertionError("partial leg mirroring must never be reintroduced")
    print("PASS: no partial-leg reflection assembly function")
    # Previously an AI passing key generated on WHITE had a bright matte
    # outline, visible as white flashes on dark backgrounds.
    from PIL import ImageFilter, ImageChops
    white_halo=original.copy()
    base=original.crop((0,2*CELL_H,CELL_W,3*CELL_H))
    opaque=base.getchannel("A").point(lambda alpha:255 if alpha>30 else 0)
    rim=ImageChops.subtract(opaque.filter(ImageFilter.MaxFilter(7)),opaque)
    rim=rim.point(lambda a:190 if a else 0)
    fringe=Image.new("RGBA",base.size,(255,255,255,0))
    fringe.putalpha(rim)
    base.alpha_composite(fringe)
    white_halo.paste(base,(0,2*CELL_H))
    expect_rejected(white_halo,"white matte fringe")
    print("PASS: rejects a white alpha-matte border on the walk")

    floating=original.copy()
    # Simulate the actual defect: shoes float 13 pixels above the floor.
    for row in (1,2):
        for col in (0,5):
            source=original.crop((col*CELL_W,row*CELL_H,
                                  (col+1)*CELL_W,(row+1)*CELL_H))
            lifted=Image.new("RGBA",(CELL_W,CELL_H))
            lifted.alpha_composite(source,(0,-13))
            floating.paste(lifted,(col*CELL_W,row*CELL_H))
    expect_rejected(floating,"missing grounded supporting sole")
    print("PASS: rejects a floating pose without a planted support shoe")

    print("Motion regressions: 8 passed")


if __name__ == "__main__":
    main()
