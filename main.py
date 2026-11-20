#!/usr/bin/env python3
"""Entrypoint for the news-image-20261120 make.fun entry.

Copies the built entry.png into $MAKEFUN_OUTPUT_DIR (default /output),
verifies it is a PNG of at most 1 MiB whose SHA-256 matches the expected
value, and prints what it wrote. Exits non-zero on any mismatch.
"""
import hashlib
import os
import shutil
import sys
from pathlib import Path

EXPECTED_SHA256 = "9d5177974de3462a9238cde0812a0052c63c68ca95b3af83cb7c9f2edb33b11a"
MAX_BYTES = 1_048_576


def main():
    here = Path(__file__).resolve().parent
    src = here / "entry.png"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "entry.png"

    if not src.is_file():
        print(f"error: {src} not found; run build_art.py first", file=sys.stderr)
        return 1

    shutil.copyfile(src, dst)
    data = dst.read_bytes()
    if len(data) > MAX_BYTES:
        print(f"error: entry.png is {len(data)} bytes, over the 1 MiB limit",
              file=sys.stderr)
        return 1
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        print("error: entry.png is not a PNG", file=sys.stderr)
        return 1
    sha = hashlib.sha256(data).hexdigest()
    if sha != EXPECTED_SHA256:
        print(f"error: SHA-256 mismatch: got {sha}, expected {EXPECTED_SHA256}",
              file=sys.stderr)
        return 1
    print(f"Wrote {dst} ({len(data)} bytes, sha256 {sha})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
