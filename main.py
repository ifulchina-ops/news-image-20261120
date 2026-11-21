#!/usr/bin/env python3
"""Hand the painted Twenty-One page to the harness.

The page itself is painted by build_art.py; this entrypoint only moves
entry.png into the output directory and checks the bytes before it
reports success: PNG signature, size under the 1 MiB ceiling, and the
SHA-256 fingerprint of the exact bytes the painter produced. If the
painter ever changes, the fingerprint below must be updated to match
the new bytes, or the handoff refuses them.
"""
import hashlib
import os
import shutil
import sys
from pathlib import Path

EXPECTED_SHA256 = "2f928644c427344fceb1dd1d0af13a8d6a034d4d761545be7e2dfae393f0fa74"
MAX_BYTES = 1_048_576
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def die(reason):
    print(f"twenty-one: {reason}", file=sys.stderr)
    return 1


def deliver():
    here = Path(__file__).resolve().parent
    page = here / "entry.png"
    if not page.is_file():
        return die("entry.png is missing — run build_art.py first")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(page, target)
    data = target.read_bytes()
    if len(data) > MAX_BYTES:
        return die(f"entry.png is {len(data)} bytes, over the 1 MiB ceiling")
    if data[:8] != PNG_SIGNATURE:
        return die("entry.png is not a PNG file")
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if width > 1024 or height > 1024:
        return die(f"entry.png is {width}x{height}, over the 1024x1024 limit")
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        return die(f"fingerprint mismatch: got {digest}")
    print(f"twenty-one: wrote {target} ({len(data)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(deliver())
