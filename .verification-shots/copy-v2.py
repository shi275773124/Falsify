#!/usr/bin/env python3
"""Copy browser MCP screenshots into .verification-shots with -v2 suffix."""

from __future__ import annotations

import shutil
from pathlib import Path

SRC = Path.home() / "AppData/Local/Temp/cursor/screenshots"
DST = Path(__file__).resolve().parent
FILES = [
    "mobile-360x800-v2.png",
    "mobile-390x844-v2.png",
    "tablet-768x1024-v2.png",
    "desktop-1440x1000-v2.png",
]

def main() -> int:
    DST.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        src = SRC / name
        dst = DST / name
        if not src.is_file():
            print(f"missing {src}")
            return 1
        shutil.copy2(src, dst)
        print(f"copied {dst} ({dst.stat().st_size} bytes)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
