"""Regression checks for the OpenClaw icon contract and safe sync."""

import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import sync_openclaw_icon as sync


def icon(paths: str) -> bytes:
    return f'<svg xmlns="{sync.SVG[1:-1]}" viewBox="0 0 16 16">{paths}</svg>'.encode()


def path(data: str = "M0 0L1 1Z") -> str:
    return f'<path fill="#ba593a" d="{data}"/>'


class SvgTest(unittest.TestCase):
    def test_canonical_icon_and_command_count(self):
        self.assertEqual(sync.validate_svg(sync.SOURCE.read_bytes())[0], 4)
        self.assertEqual(sync.count_commands("M0 1 2 3L4 5 6 7Z"), 5)

    def test_rejects_disallowed_artwork(self):
        for bad in (
            icon(path() * 4),
            icon(path() + '<image href="https://example.com/icon.png"/>'),
            icon(path().replace("#ba593a", "url(#paint)")),
            icon(path()).replace(b"<svg", b'<svg onload="x"'),
            icon(path()).replace(b"16 16", b"0 16"),
            icon(path("M0 0Q5 5Z")),
            icon(path("M0 0 A1 1 0 2 0 4 4Z")),
            icon(path("M0 0" + " 1 1" * 1024)),
            icon(path("M0 0 " + " " * 8192)),
            icon(path()) + b" " * (32 * 1024),
        ):
            with self.subTest(svg=bad[:180]):
                with self.assertRaises((ValueError, ET.ParseError)):
                    sync.validate_svg(bad)


class SyncTest(unittest.TestCase):
    def test_sync_check_and_rollback(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            destination = root / "plugin" / sync.ARTWORK
            destination.parent.mkdir(parents=True)
            manifest = {"id": "yutheme", "themes": [
                {"id": "dark", "icons": {"nery": sync.ARTWORK.as_posix()}},
            ]}
            (root / "plugin/openclaw.plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
            previous = icon(path())
            destination.write_bytes(previous)
            backup = root / sync.BACKUP
            invalid = root / "invalid.svg"
            invalid.write_bytes(icon("<script/>"))

            with patch.object(sync, "SOURCE", invalid):
                with self.assertRaises(SystemExit):
                    self.run_sync(root)
            self.assertEqual(destination.read_bytes(), previous)
            self.assertFalse(backup.exists())

            with self.assertRaises(SystemExit):
                self.run_sync(root, "--check")
            self.assertFalse(backup.exists())
            self.run_sync(root)
            self.assertEqual(destination.read_bytes(), sync.SOURCE.read_bytes())
            self.assertEqual(backup.read_bytes(), previous)
            timestamp = destination.stat().st_mtime_ns
            self.run_sync(root, "--check")
            self.run_sync(root)
            self.assertEqual(destination.stat().st_mtime_ns, timestamp)
            self.assertEqual(backup.read_bytes(), previous)
            self.run_sync(root, "--rollback")
            self.assertEqual(destination.read_bytes(), previous)

    def run_sync(self, root, *args):
        with (
            patch("sys.argv", ["sync_openclaw_icon.py", str(root), *args]),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            sync.main()


if __name__ == "__main__":
    unittest.main()
