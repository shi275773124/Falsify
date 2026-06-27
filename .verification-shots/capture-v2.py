#!/usr/bin/env python3
"""Capture homepage verification screenshots with -v2 suffix."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
URL = "http://127.0.0.1:8000/"
SHOTS = [
    ("mobile-360x800-v2.png", 360, 800),
    ("mobile-390x844-v2.png", 390, 844),
    ("tablet-768x1024-v2.png", 768, 1024),
    ("desktop-1440x1000-v2.png", 1440, 1000),
]
EDGE_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe",
]


def find_browser() -> Path | None:
    for p in EDGE_CANDIDATES:
        if p.is_file():
            return p
    for name in ("msedge", "chrome"):
        found = shutil.which(name)
        if found:
            return Path(found)
    return None


def capture(browser: Path, name: str, width: int, height: int) -> None:
    out = OUT_DIR / name
    tmp = Path(tempfile.gettempdir()) / f"falsify-{name}"
    tmp.unlink(missing_ok=True)
    profile = Path(tempfile.mkdtemp(prefix="falsify-shot-"))
    cmd = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        f"--user-data-dir={profile}",
        "--force-device-scale-factor=1",
        f"--window-size={width},{height}",
        f"--screenshot={tmp}",
        URL,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    shutil.rmtree(profile, ignore_errors=True)
    if proc.returncode != 0 and not tmp.is_file():
        raise RuntimeError(f"{name}: exit {proc.returncode}: {proc.stderr or proc.stdout}")
    for _ in range(40):
        if tmp.is_file() and tmp.stat().st_size > 5000:
            break
        time.sleep(0.25)
    if not tmp.is_file():
        raise FileNotFoundError(f"{name}: screenshot not created")
    shutil.copy2(tmp, out)
    tmp.unlink(missing_ok=True)
    print(f"OK {out} ({out.stat().st_size} bytes)")


def main() -> int:
    browser = find_browser()
    if not browser:
        print("need Edge or Chrome", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, w, h in SHOTS:
        capture(browser, name, w, h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
