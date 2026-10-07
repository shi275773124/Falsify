#!/usr/bin/env python3
"""Capture competitor study screenshots (Pool Money + Consensys)."""
from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".verification-shots" / "competitor-study"
OUT.mkdir(parents=True, exist_ok=True)

SHOTS = [
    ("poolmoney-hero", "https://poolmoney.com/", False, 1440, 1000),
    ("poolmoney-sections", "https://poolmoney.com/", True, 1440, 1000),
    ("poolmoney-craftwork", "https://craftwork.design/curated/website/pool-money", True, 1440, 1000),
    ("consensys-hero", "https://consensys.io/", False, 1440, 1000),
    ("consensys-craftwork", "https://craftwork.design/curated/website/consensys", True, 1440, 1000),
    ("consensys-section-ecosystem", "https://consensys.io/", True, 1440, 1000),
    ("consensys-section-products", "https://consensys.io/", True, 1440, 1000),
    ("consensys-mobile", "https://consensys.io/", True, 390, 844),
]


def page_info(page):
    return page.evaluate(
        """() => {
          const pick = (sel) => {
            const el = document.querySelector(sel);
            if (!el) return null;
            const s = getComputedStyle(el);
            return {
              text: el.innerText?.slice(0, 120),
              size: s.fontSize,
              weight: s.fontWeight,
              lh: s.lineHeight,
              ls: s.letterSpacing,
              color: s.color,
            };
          };
          const headings = [...document.querySelectorAll('h1,h2,h3')].slice(0, 10).map(el => {
            const s = getComputedStyle(el);
            return { tag: el.tagName, text: el.innerText.slice(0, 70), size: s.fontSize, weight: s.fontWeight };
          });
          const sections = [...document.querySelectorAll('section')].slice(0, 8).map((el, i) => ({
            i,
            cls: (el.className || '').toString().slice(0, 60),
            h: el.querySelector('h1,h2,h3')?.innerText?.slice(0, 60) || '',
          }));
          return {
            title: document.title,
            h1: pick('h1'),
            bodyBg: getComputedStyle(document.body).backgroundColor,
            bodyFont: getComputedStyle(document.body).fontFamily,
            sectionCount: document.querySelectorAll('section').length,
            headings,
            sections,
          };
        }"""
    )


def main() -> int:
    report = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, url, full, w, h in SHOTS:
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(url, wait_until="domcontentloaded", timeout=120000)
            page.wait_for_timeout(3500)
            path = OUT / f"{name}.png"
            page.screenshot(path=str(path), full_page=full)
            info = page_info(page)
            report[name] = {"url": url, "bytes": path.stat().st_size, **info}
            print(f"OK {path} ({path.stat().st_size})")
            page.close()
        browser.close()

    meta = OUT / "competitor-study-report.json"
    meta.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"report {meta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
