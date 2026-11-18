"""Render the Nery micro icon kit and its pixel-size review sheet."""

import argparse
from io import BytesIO
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont
import resvg_py


ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "assets/icons/micro"
AVATAR = ROOT / "assets/mascot/kit-v1/avatars/nery-avatar-512.png"
SIZES = (16, 24, 32, 48)
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def render_svg(svg: str, size: int) -> Image.Image:
    png = resvg_py.svg_to_bytes(svg_string=svg, width=size, height=size)
    return Image.open(BytesIO(png)).convert("RGBA")


def derive_svg(size: int) -> str:
    master = KIT / ("nery-16.svg" if size == 16 else "nery-32.svg")
    if size in (16, 32):
        return master.read_text(encoding="utf-8")
    svg = ET.parse(master).getroot()
    svg.attrib.update(width=str(size), height=str(size))
    if size == 24:
        svg.remove(svg.find(f"{{{SVG_NS}}}g[@id='compact-details']"))
    return ET.tostring(svg, encoding="unicode") + "\n"


def save_or_check(path: Path, content: bytes, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_bytes() != content:
            raise SystemExit(f"Stale or missing export: {path.relative_to(ROOT)}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def save_png(path: Path, image: Image.Image, check: bool) -> None:
    if check:
        if path.is_file():
            with Image.open(path) as current:
                if (
                    current.format == "PNG"
                    and current.size == image.size
                    and current.mode == image.mode
                    and current.tobytes() == image.tobytes()
                ):
                    return
        raise SystemExit(f"Stale or missing PNG: {path.relative_to(ROOT)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")


def comparison(icons: dict[int, Image.Image], previous: Path) -> Image.Image:
    sheet = Image.new("RGB", (920, 630), "#22272b")
    draw = ImageDraw.Draw(sheet)
    title = ImageFont.load_default(size=24)
    label = ImageFont.load_default(size=15)
    small = ImageFont.load_default(size=12)
    draw.text((22, 15), "Nery Mizuki / Micro Icon Kit", "#e8e4dc", font=title)
    draw.text((23, 49), "Native size on the left of each sample. Enlargements use nearest-neighbor.", "#bcb6ae", font=small)

    original = Image.open(AVATAR).convert("RGBA")
    original.thumbnail((103, 103), Image.Resampling.LANCZOS)
    old = render_svg(previous.read_text(encoding="utf-8"), 16)
    columns = [(28, "Approved avatar"), (161, "Previous / 16 px")]
    columns += [(294 + i * 146, f"{size} px / {('Micro' if size < 32 else 'Compact')}") for i, size in enumerate(SIZES)]
    for y, background in [(77, "#17191c"), (353, "#0f1113")]:
        draw.rounded_rectangle((12, y, 908, y + 264), 10, fill=background)
        draw.text((24, y + 11), background.upper(), "#e8e4dc", font=label)
        for x, name in columns:
            draw.text((x, y + 41), name, "#e8e4dc", font=small)
        sheet.paste(original, (columns[0][0], y + 67), original)

        for (x, _), icon in zip(columns[1:], [old, *icons.values()], strict=True):
            sheet.paste(icon, (x, y + 67), icon)
            scale = 96 // icon.width
            enlarged = icon.resize((icon.width * scale, icon.height * scale), Image.Resampling.NEAREST)
            sheet.paste(enlarged, (x + 26, y + 121), enlarged)

        for x, caption, icon in [(28, "Previous", old), (439, "Nery", icons[16])]:
            row = y + 233
            draw.text((x, row), caption, "#bcb6ae", font=small)
            sheet.paste(icon, (x + 62, row - 2), icon)
            draw.text((x + 86, row), "1.2k tokens  ·  3.4s", "#e8e4dc", font=small)
    return sheet


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check committed exports are up to date")
    parser.add_argument("--previous", type=Path, help="Old YuTheme SVG for the comparison sheet")
    args = parser.parse_args()

    icons = {}
    for size in SIZES:
        svg = derive_svg(size)
        if size not in (16, 32):
            save_or_check(KIT / f"nery-{size}.svg", svg.encode("utf-8"), args.check)
        icon = render_svg(svg, size)
        left, top, right, bottom = icon.getbbox()
        if icon.size != (size, size) or min(right - left, bottom - top) < size - 3:
            raise SystemExit(f"Unexpected artwork bounds at {size} px")
        if icon.getpixel((0, 0))[3] != 0 or icon.getpixel((size - 1, size - 1))[3] != 0:
            raise SystemExit(f"Expected transparent corners at {size} px")
        save_png(KIT / "png" / f"nery-{size}.png", icon, args.check)
        icons[size] = icon

    if args.previous:
        save_png(KIT / "previews/comparison.png", comparison(icons, args.previous), args.check)
    print("Rendered and verified Nery icons at 16, 24, 32 and 48 px.")


if __name__ == "__main__":
    main()
