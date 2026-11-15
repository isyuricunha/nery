#!/usr/bin/env python3
"""Regenerate frame-accurate previews from the SHIPPED Petdex WebP atlas.

Keep contact sheets and GIFs synchronized with the actual current build.
No generated artwork or approved source poses are changed by this script.
Usage: python3 scripts/render_pet_previews.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from build_walk_animation import load_motion_frames

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "pet/nery/spritesheet.webp"
OUT = ROOT / "pet/preview"
STATES = (
    "idle", "running-right", "running-left", "waving", "jumping",
    "failed", "waiting", "running", "review",
)
W, H = 192, 208
BACKGROUND = (33, 25, 21)
COUNTS = (6,8,8,4,5,8,6,6,6)
DURATIONS = (
    (280,110,110,140,140,320),
    (120,120,120,120,120,120,120,220),
    (120,120,120,120,120,120,120,220),
    (140,140,140,280),
    (140,140,140,140,280),
    (140,140,140,140,140,140,140,240),
    (150,150,150,150,150,260),
    (120,120,120,120,120,220),
    (150,150,150,150,150,280),
)


def show_frame(atlas: Image.Image, row: int, col: int) -> Image.Image:
    source = atlas.crop((col * W, row * H, (col + 1) * W, (row + 1) * H))
    result = Image.new("RGBA", (W, H), BACKGROUND + (255,))
    result.alpha_composite(source)
    return result.convert("RGB")


def main() -> None:
    if not ATLAS.is_file():
        raise SystemExit(f"Atlas missing: {ATLAS}")
    atlas = Image.open(ATLAS).convert("RGBA")
    if atlas.size != (1536, 2288):
        raise SystemExit(f"Unexpected v2 atlas dimensions: {atlas.size}")
    OUT.mkdir(parents=True, exist_ok=True)
    frames: dict[str, list[Image.Image]] = {}
    for row, state in enumerate(STATES):
        seq = [show_frame(atlas, row, col) for col in range(COUNTS[row])]
        frames[state] = seq
        seq[0].save(
            OUT / f"{state}.gif",
            save_all=True,
            append_images=seq[1:],
            duration=DURATIONS[row],
            loop=0,
            optimize=False,
            disposal=2,
        )

    label_width = 165
    sheet = Image.new("RGB", (label_width + W * 8, H * len(STATES)), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for row, name in enumerate(STATES):
        y = row * H
        draw.text((12, y + 88), name, font=font, fill=(234, 208, 180))
        for col, frame in enumerate(frames[name]):
            sheet.paste(frame, (label_width + col * W, y))
    sheet.save(OUT / "final-contact-sheet.jpg", quality=93, subsampling=0)

    strip = Image.new("RGB", (W * 8, H + 25), BACKGROUND)
    for col, frame in enumerate(frames["running-left"]):
        strip.paste(frame, (col * W, 25))
        ImageDraw.Draw(strip).text((col * W + 12, 7), str(col + 1), fill=(234, 208, 180))
    strip.save(OUT / "walking-filmstrip.png", optimize=True)

    # A one-pass state reel helps spot jarring pose changes and broken cycles.
    reel = [frame for name in STATES for frame in frames[name]]
    reel[0].save(
        OUT / "state-reel.gif",
        save_all=True,
        append_images=reel[1:],
        duration=[d for row in DURATIONS for d in row],
        loop=0,
        optimize=False,
        disposal=2,
    )
    # Website-only 16-frame walk. Keep native Petdex previews separate:
    # this animation uses the additional web sprite asset, not fake alpha fades.
    web_walk = []
    for key in load_motion_frames():
        bg = Image.new("RGBA", (W, H), BACKGROUND + (255,))
        bg.alpha_composite(key)
        web_walk.append(bg.convert("RGB"))
    web_walk[0].save(
        OUT / "walk-16.gif",
        save_all=True,
        append_images=web_walk[1:],
        duration=[60] * len(web_walk),
        loop=0,
        optimize=False,
        disposal=2,
    )
    print(f"Rendered {len(STATES)} state GIFs, the 16-frame web walk, state reel and contact sheets into {OUT}")


if __name__ == "__main__":
    main()
