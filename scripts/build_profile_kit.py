"""Build profile crops from canonical Nery artwork and check platform limits."""

import argparse
from io import BytesIO
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps


KIT = Path(__file__).resolve().parents[1] / "assets/profile"
LANCZOS = Image.Resampling.LANCZOS


def export(image: Image.Image, name: str, check: bool, max_bytes: int | None = None) -> None:
    path = KIT / name
    options = {
        ".png": {"optimize": True},
        ".webp": {"lossless": image.mode == "RGBA", "quality": 90, "method": 6},
        ".jpg": {"quality": 91, "optimize": True, "subsampling": 0},
    }
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, **options[path.suffix])
    with Image.open(path) as actual:
        if actual.size != image.size or actual.mode != image.mode:
            raise ValueError(f"Wrong export size or mode: {name}")
        if check:
            output = BytesIO()
            image.save(output, format=actual.format, **options[path.suffix])
            with Image.open(output) as expected:
                mode = "RGBa" if image.mode == "RGBA" else "RGB"
                if actual.convert(mode).tobytes() != expected.convert(mode).tobytes():
                    raise ValueError(f"Export differs from its source: {name}")
    if max_bytes and not path.stat().st_size < max_bytes:
        raise ValueError(f"Export exceeds {max_bytes} bytes: {name}")


def avatar(source: Image.Image, size: int) -> Image.Image:
    edge = round(size * 0.92)
    canvas = Image.new("RGBA", (size, size))
    canvas.alpha_composite(source.resize((edge, edge), LANCZOS), ((size - edge) // 2,) * 2)
    return canvas


def circle_crop(image: Image.Image) -> Image.Image:
    resolution = image.width * 4
    mask = Image.new("L", (resolution, resolution))
    ImageDraw.Draw(mask).ellipse((0, 0, resolution - 1, resolution - 1), fill=255)
    result = image.copy()
    result.putalpha(ImageChops.multiply(image.getchannel("A"), mask.resize(image.size, LANCZOS)))
    return result


def review(avatars: dict[str, Image.Image], covers: dict[str, Image.Image]) -> Image.Image:
    canvas = Image.new("RGB", (1080, 860), "#211915")
    draw = ImageDraw.Draw(canvas)
    heading = ImageFont.load_default(size=24)
    caption = ImageFont.load_default(size=14)
    draw.text((24, 14), "Nery Mizuki / Profile kit", "#f0e9e3", font=heading)
    for row, (background, ink) in enumerate((("#100e0d", "#f0e9e3"), ("#f0e9e3", "#211915"))):
        y = 62 + row * 170
        draw.rectangle((24, y, 1056, y + 152), fill=background)
        for col, (name, source) in enumerate(avatars.items()):
            x = 46 + col * 515
            draw.text((x, y + 10), name, ink, font=caption)
            for index, size in enumerate((32, 48, 64)):
                square = avatar(source, size)
                left = x + 50 + index * 143
                circle = circle_crop(square)
                canvas.paste(square, (left, y + 82 - size // 2), square)
                canvas.paste(circle, (left + 68, y + 82 - size // 2), circle)
                draw.text((left + 13, y + 124), f"{size} px", ink, font=caption)
    for name, x, y, size, label in (
        ("banners/profile.webp", 24, 430, (696, 232), "Wide profile header"),
        ("backgrounds/desktop.webp", 24, 682, (280, 158), "Desktop background"),
        ("banners/discord.png", 322, 682, (395, 158), "Compact profile header"),
        ("backgrounds/mobile.webp", 754, 430, (273, 410), "Mobile background"),
    ):
        image = covers[name].resize(size, LANCZOS)
        canvas.paste(image, (x, y))
        draw.text((x + 10, y + 8), label, "#f0e9e3", font=caption, stroke_width=1, stroke_fill="#211915")
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify exports without writing files")
    args = parser.parse_args()
    manifest = json.loads((KIT / "manifest.json").read_text(encoding="utf-8"))
    sources = {name: Image.open(KIT / spec["file"]) for name, spec in manifest["sources"].items()}
    avatars = {name: sources[name] for name in ("profile", "friendly")}
    for name, source in avatars.items():
        if source.mode != "RGBA" or source.width != source.height or source.getchannel("A").getextrema()[0] != 0:
            raise ValueError(f"Expected a square transparent source for {name}")
        for size in manifest["avatarSizes"]:
            export(avatar(source, size), f"avatars/{name}-{size}.png", args.check, max_bytes=1_000_000)
        export(avatar(source, 512), f"avatars/{name}-512.webp", args.check)

    covers = {}
    for spec in manifest["covers"]:
        source = sources[spec["source"]].convert("RGB")
        image = ImageOps.fit(source, tuple(spec["size"]), LANCZOS, centering=tuple(spec["position"]))
        export(image, spec["file"], args.check, spec.get("maxBytes"))
        covers[spec["file"]] = image
    export(review(avatars, covers), "preview/profile-kit.png", args.check)
    print(f"Verified {2 * len(manifest['avatarSizes']) + 2} avatars and {len(covers)} covers/backgrounds.")


if __name__ == "__main__":
    main()
