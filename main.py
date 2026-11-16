#!/usr/bin/env python3
"""Copy the rendered entry.png into the make.fun output directory.

Standard library only. Reads MAKEFUN_OUTPUT_DIR (default /output), creates it,
validates the PNG magic bytes and the 1 MiB size cap, then copies the image.
"""
from __future__ import annotations

import os
import shutil
import sys

MAX_BYTES = 1 * 1024 * 1024  # 1 MiB
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main() -> int:
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    dst = os.path.join(out_dir, "entry.png")

    if not os.path.isfile(src):
        print(f"error: missing source image: {src}", file=sys.stderr)
        return 1

    size = os.path.getsize(src)
    if size > MAX_BYTES:
        print(f"error: entry.png is {size} bytes, exceeding the 1 MiB cap", file=sys.stderr)
        return 1

    with open(src, "rb") as fh:
        header = fh.read(8)
    if header != PNG_MAGIC:
        print("error: entry.png is not a valid PNG (bad magic bytes)", file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    shutil.copy2(src, dst)

    print(f"{dst} ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
