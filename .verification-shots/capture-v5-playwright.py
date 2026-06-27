#!/usr/bin/env python3
"""Capture homepage verification screenshots with -v5 suffix."""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).resolve().parent
URL = "http://127.0.0.1:8000/?lang=zh"
SHOTS = [
    ("mobile-360x800-v5.png", 360, 800),
    ("mobile-390x844-v5.png", 390, 844),
    ("tablet-768x1024-v5.png", 768, 1024),
    ("desktop-1440x1000-v5.png", 1440, 1000),
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, width, height in SHOTS:
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(URL, wait_until="networkidle")
            page.wait_for_timeout(600)
            out = OUT_DIR / name
            page.screenshot(path=str(out), full_page=True)
            page.close()
            print(f"OK {out} ({out.stat().st_size} bytes)")
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
