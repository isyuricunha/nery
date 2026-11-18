"""Export and verify the transparent and layered Nery master artwork."""

import argparse
from io import BytesIO
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZIP_STORED, ZipFile

from PIL import Image, ImageChops, ImageDraw


KIT = Path(__file__).resolve().parents[1] / "assets/mascot/kit-v3"


def png(image: Image.Image) -> bytes:
    stream = BytesIO()
    image.save(stream, format="PNG", optimize=True)
    return stream.getvalue()


def layers_for(image: Image.Image, outlines: dict) -> list:
    alpha = image.getchannel("A")
    remaining = alpha
    layers = []
    for name, key in (("Legs and shoes", "lower"), ("Clothing and hands", "clothing")):
        if key not in outlines:
            continue
        mask = Image.new("L", image.size)
        ImageDraw.Draw(mask).polygon([tuple(point) for point in outlines[key]], fill=255)
        part_alpha = ImageChops.multiply(remaining, mask)
        remaining = ImageChops.subtract(remaining, part_alpha)
        layers.append((name, part_alpha))
    layers.append(("Head, hair and ribbons", remaining))

    output = []
    for name, part_alpha in reversed(layers):
        bbox = part_alpha.getbbox()
        if not bbox:
            raise ValueError(f"Empty drawing layer: {name}")
        artwork = image.crop(bbox)
        artwork.putalpha(part_alpha.crop(bbox))
        artwork = Image.composite(artwork, Image.new("RGBA", artwork.size),
                                  artwork.getchannel("A").point([0] + [255] * 255))
        output.append((name, bbox, artwork))
    return output


def write_master(path: Path, image: Image.Image, title: str, outlines: dict) -> None:
    root = ET.Element("image", w=str(image.width), h=str(image.height), name=title, version="0.0.3")
    stack = ET.SubElement(root, "stack")
    with ZipFile(path, "w") as archive:
        archive.writestr("mimetype", "image/openraster", compress_type=ZIP_STORED)
        for i, (name, (left, top, _, _), layer) in enumerate(layers_for(image, outlines)):
            source = f"data/layer{i}.png"
            ET.SubElement(stack, "layer", {
                "name": name, "src": source, "x": str(left), "y": str(top),
                "opacity": "1.0", "visibility": "visible", "composite-op": "svg:src-over",
            })
            archive.writestr(source, png(layer))
        archive.writestr("stack.xml", ET.tostring(root, encoding="utf-8", xml_declaration=True))
        archive.writestr("mergedimage.png", png(image))
        thumbnail = image.copy()
        thumbnail.thumbnail((256, 256), Image.Resampling.LANCZOS)
        archive.writestr("Thumbnails/thumbnail.png", png(thumbnail))


def same_pixels(first: Image.Image, second: Image.Image, artifact: Path) -> None:
    if first.size != second.size or first.convert("RGBa").tobytes() != second.convert("RGBa").tobytes():
        raise ValueError(f"Rendered pixels differ: {artifact}")


def verify_master(path: Path, image: Image.Image, expected_layers: int) -> None:
    with ZipFile(path) as archive:
        mimetype = archive.infolist()[0]
        if mimetype.filename != "mimetype" or mimetype.compress_type != ZIP_STORED:
            raise ValueError(f"Invalid OpenRaster archive order: {path}")
        if archive.read("mimetype") != b"image/openraster":
            raise ValueError(f"Invalid OpenRaster type: {path}")
        root = ET.fromstring(archive.read("stack.xml"))
        layers = root.findall("stack/layer")
        if len(layers) != expected_layers or len({layer.attrib["name"] for layer in layers}) != len(layers):
            raise ValueError(f"Unexpected drawing layers: {path}")
        canvas = Image.new("RGBA", image.size)
        for layer in reversed(layers):
            data = Image.open(BytesIO(archive.read(layer.attrib["src"]))).convert("RGBA")
            canvas.alpha_composite(data, (int(layer.attrib["x"]), int(layer.attrib["y"])))
        same_pixels(canvas, image, path)
        same_pixels(Image.open(BytesIO(archive.read("mergedimage.png"))), image, path)


def contact_sheet(poses: list) -> Image.Image:
    size = (280, 435)
    canvas = Image.new("RGB", (size[0] * len(poses), size[1] * 2))
    for col, (title, image) in enumerate(poses):
        preview = image.copy()
        preview.thumbnail((size[0] - 28, size[1] - 56), Image.Resampling.LANCZOS)
        for row, (background, text) in enumerate((("#211915", "#f0e9e3"), ("#f0e9e3", "#211915"))):
            tile = Image.new("RGBA", size, background)
            tile.alpha_composite(preview, ((tile.width - preview.width) // 2, 38))
            ImageDraw.Draw(tile).text((14, 12), title, fill=text)
            canvas.paste(tile, (col * size[0], row * size[1]))
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify existing files without rewriting them")
    args = parser.parse_args()
    manifest = json.loads((KIT / "manifest.json").read_text(encoding="utf-8"))
    masks = json.loads((KIT / "layers.json").read_text(encoding="utf-8"))
    poses = []
    for pose in manifest["poses"]:
        source = KIT / "transparent" / pose["png"]
        image = Image.open(source)
        if image.mode != "RGBA" or image.size != (pose["width"], pose["height"]):
            raise ValueError(f"Expected native RGBA artwork: {source}")
        alpha = image.getchannel("A")
        if alpha.getextrema()[0] != 0 or alpha.getextrema()[1] < 250:
            raise ValueError(f"Expected visible artwork and transparent background: {source}")
        webp = source.with_suffix(".webp")
        master = KIT / "masters" / source.with_suffix(".ora").name
        outlines = masks[pose["id"]]
        if not args.check:
            master.parent.mkdir(exist_ok=True)
            image.save(webp, format="WEBP", lossless=True, method=6, exact=True)
            write_master(master, image, pose["title"], outlines)
        same_pixels(Image.open(webp), image, webp)
        verify_master(master, image, 1 + len(outlines))
        poses.append((pose["title"], image))
        print(f"{pose['id']}: {image.width} x {image.height}, {1 + len(outlines)} layers")

    review = KIT / "preview" / "master-kit.png"
    sheet = contact_sheet(poses)
    if not args.check:
        review.parent.mkdir(exist_ok=True)
        review.write_bytes(png(sheet))
    same_pixels(Image.open(review), sheet, review)


if __name__ == "__main__":
    main()
