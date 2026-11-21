#!/usr/bin/env python3
"""Deliver the Twenty-One front page.

build_art.py paints entry.png; this script is the handoff. It drops the
painted page into the directory the harness reads, and refuses to hand
over anything unless the bytes are exactly the page the builder made:
right format, right size, right fingerprint.
"""
import os as _os
import pathlib
import sys as _sys
from hashlib import sha256
from shutil import copyfile

# fingerprint of entry.png exactly as build_art.py paints it — repaint and
# this value changes, so the handoff refuses the new bytes until it is set.
WANT = "2f928644c427344fceb1dd1d0af13a8d6a034d4d761545be7e2dfae393f0fa74"
CEILING = 1048576
MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print("twenty-one: " + message, file=_sys.stderr)
    return 1


def run():
    root = pathlib.Path(__file__).resolve().parent
    src = root / "entry.png"
    if not src.exists():
        return fail("entry.png is missing — run build_art.py first")
    target_dir = pathlib.Path(_os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    target_dir.mkdir(parents=True, exist_ok=True)
    dst = target_dir / "entry.png"
    copyfile(src, dst)
    blob = dst.read_bytes()
    if len(blob) > CEILING:
        return fail(f"entry.png is {len(blob)} bytes, over the 1 MiB ceiling")
    if blob[:8] != MAGIC:
        return fail("entry.png is not a PNG file")
    got = sha256(blob).hexdigest()
    if got != WANT:
        return fail(f"fingerprint mismatch: got {got}")
    print(f"twenty-one: wrote {dst} ({len(blob)} bytes, sha256 {got})")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
