"""Validate and copy Nery's 16 px icon into an existing YuTheme installation."""

import argparse
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import re
import stat
from tempfile import NamedTemporaryFile
import xml.etree.ElementTree as ET


SOURCE = Path(__file__).resolve().parents[1] / "assets/icons/micro/nery-16.svg"
SVG = "{http://www.w3.org/2000/svg}"
NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
PATH_TOKEN = re.compile(rf"({NUMBER})|([MmLlHhVvCcSsQqTtAaZz])|[\s,]+", re.ASCII)
PATH_ARITY = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}
ARTWORK = Path("assets/theme-art/nery.svg")
BACKUP = Path("backups/nery-before-kit.svg")


def count_commands(data: str) -> int:
    matches = list(PATH_TOKEN.finditer(data))
    if "".join(match[0] for match in matches) != data:
        raise ValueError("SVG path contains unsupported syntax")
    tokens = [match[0] for match in matches if match.lastindex]
    if not tokens or tokens[0] not in ("M", "m"):
        raise ValueError("SVG path must start with a move")
    count = 0
    i = 0
    while i < len(tokens):
        command = tokens[i].upper()
        if command not in PATH_ARITY:
            raise ValueError("SVG path is missing a command")
        start = i + 1
        i = start
        while i < len(tokens) and tokens[i].upper() not in PATH_ARITY:
            if not math.isfinite(float(tokens[i])):
                raise ValueError("Non-finite SVG path coordinate")
            i += 1
        arity = PATH_ARITY[command]
        length = i - start
        if arity and (length < arity or length % arity) or not arity and length:
            raise ValueError(f"Wrong number of parameters for SVG path command {command}")
        if command == "A":
            for arc in range(start, i, 7):
                if float(tokens[arc]) < 0 or float(tokens[arc + 1]) < 0:
                    raise ValueError("Negative SVG arc radius")
                if set(tokens[arc + 3:arc + 5]) - {"0", "1"}:
                    raise ValueError("Invalid SVG arc flag")
        count += length // arity if arity else 1
    return count


def validate_svg(content: bytes) -> tuple[int, int, int]:
    """Enforce the OpenClaw contract using the kit's narrower path-only profile."""
    if len(content) > 32 * 1024:
        raise ValueError("SVG exceeds 32 KiB")
    markup = content.decode("utf-8")
    if "<!" in markup or "<?" in markup:
        raise ValueError("SVG declarations, entities and comments are disallowed")
    root = ET.fromstring(markup)
    if root.tag != SVG + "svg" or set(root.attrib) - {"viewBox", "width", "height"}:
        raise ValueError("Expected a standalone SVG root with numeric dimensions")
    viewbox = re.split(r"[\s,]+", root.get("viewBox", "").strip())
    if len(viewbox) != 4 or any(not re.fullmatch(NUMBER, item) for item in viewbox):
        raise ValueError("Expected a numeric SVG viewBox")
    coordinates = list(map(float, viewbox))
    dimensions = [root.get(side, viewbox[i]) for side, i in (("width", 2), ("height", 3))]
    if (
        any(not math.isfinite(value) for value in coordinates)
        or any(not 0 < value <= 4096 for value in coordinates[2:])
        or any(not re.fullmatch(NUMBER, item) or not 0 < float(item) <= 4096 for item in dimensions)
    ):
        raise ValueError("SVG dimensions must be positive and at most 4096")
    if not 1 <= len(root) <= 3 or (root.text or "").strip():
        raise ValueError("Expected 1–3 direct path elements")
    path_bytes = commands = 0
    for path in root:
        if (
            path.tag != SVG + "path"
            or set(path.attrib) - {"d", "fill", "fill-rule"}
            or not re.fullmatch(r"#[a-fA-F0-9]{6}", path.get("fill", ""))
            or path.get("fill-rule", "nonzero") not in ("evenodd", "nonzero")
            or len(path)
            or (path.text or "").strip()
            or (path.tail or "").strip()
        ):
            raise ValueError("SVG paths may only contain geometry and literal RGB paint")
        data = path.get("d", "")
        path_bytes += len(data.encode("utf-8"))
        commands += count_commands(data)
    if path_bytes > 8 * 1024 or commands > 1024:
        raise ValueError("SVG exceeds OpenClaw's path complexity limits")
    return len(root) + 1, path_bytes, commands


def atomic_write(path: Path, content: bytes, mode: int) -> None:
    temporary = None
    try:
        with NamedTemporaryFile(dir=path.parent, prefix=".nery-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(mode)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def consumer_paths(root: Path) -> tuple[Path, Path]:
    plugin = root / "plugin"
    destination = plugin / ARTWORK
    backup = root / BACKUP
    for path in (plugin, destination, backup):
        if path.resolve() != path:
            raise ValueError(f"Expected a local path inside YuTheme: {path}")
    manifest = json.loads((plugin / "openclaw.plugin.json").read_text(encoding="utf-8"))
    themes = manifest.get("themes", [])
    if manifest.get("id") != "yutheme" or not any(
        theme.get("id") == "dark" and theme.get("icons", {}).get("nery") == ARTWORK.as_posix()
        for theme in themes
    ):
        raise ValueError("YuTheme manifest does not declare the expected Nery icon")
    return destination, backup


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("yutheme", type=Path, help="YuTheme directory containing plugin/")
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument("--check", action="store_true", help="Check the installed copy without writes")
    operation.add_argument("--rollback", action="store_true", help="Restore the previous validated SVG")
    args = parser.parse_args()

    try:
        destination, backup = consumer_paths(args.yutheme.resolve(strict=True))
        content = (backup if args.rollback else SOURCE).read_bytes()
        elements, path_bytes, commands = validate_svg(content)
        print(f"SHA-256 {sha256(content).hexdigest()} ({len(content)} B, {elements} elements, "
              f"{path_bytes} path bytes, {commands} path commands)")
        previous = destination.read_bytes()
        if previous == content:
            print("YuTheme already has this icon.")
            return
        if args.check:
            raise ValueError("YuTheme differs from the canonical Nery icon")

        mode = stat.S_IMODE(destination.stat().st_mode)
        if not args.rollback:
            backup.parent.mkdir(exist_ok=True)
            atomic_write(backup, previous, mode)
        atomic_write(destination, content, mode)
        print(f"{'Restored' if args.rollback else 'Synced'} {destination}")
    except (OSError, ValueError, ET.ParseError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
