#!/usr/bin/env python3
"""Capture homepage verification screenshots at standard breakpoints.

Usage:
  py -3.12 scripts/capture-verification-shots.py
  py -3.12 scripts/capture-verification-shots.py --suffix v5 --lang zh
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / ".verification-shots"
DEFAULT_SHOTS = [
    ("mobile-360x800", 360, 800),
    ("mobile-390x844", 390, 844),
    ("tablet-768x1024", 768, 1024),
    ("desktop-1440x1000", 1440, 1000),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture Falsify homepage screenshots")
    parser.add_argument("--suffix", default="v5", help="filename suffix, e.g. v5")
    parser.add_argument("--lang", default="zh", choices=("en", "zh"))
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/")
    args = parser.parse_args()

    url = args.base_url.rstrip("/") + "/"
    if args.lang == "zh":
        url += "?lang=zh"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shots_report: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for stem, width, height in DEFAULT_SHOTS:
            name = f"{stem}-{args.suffix}.png"
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(600)
            out = OUT_DIR / name
            page.screenshot(path=str(out), full_page=True)
            doc_width = page.evaluate("document.documentElement.scrollWidth")
            cockpit = page.locator(".gate-panel, .hero-cockpit").first
            block = page.locator(".block-stamp, .verdict-block").first
            shots_report.append(
                {
                    "file": name,
                    "viewport": [width, height],
                    "bytes": out.stat().st_size,
                    "horizontal_scroll": doc_width > width + 1,
                    "cockpit_visible": cockpit.count() > 0 and cockpit.is_visible(),
                    "block_badge_visible": block.count() > 0 and block.is_visible(),
                }
            )
            page.close()
            print(f"OK {out} ({out.stat().st_size} bytes)")
        browser.close()

    report_path = OUT_DIR / "capture-report.json"
    report_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "url": url,
                "suffix": args.suffix,
                "shots": shots_report,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"report {report_path}")
    if any(s["horizontal_scroll"] for s in shots_report):
        print("warning: horizontal scroll detected")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
