#!/usr/bin/env python3
"""Capture Pool Money competitor study screenshots."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".verification-shots" / "competitor-study"
OUT.mkdir(parents=True, exist_ok=True)

SHOTS = [
    ("poolmoney-hero", "https://poolmoney.com/", False, 1440, 1000),
    ("poolmoney-full", "https://poolmoney.com/", True, 1440, 9000),
    ("poolmoney-craftwork", "https://craftwork.design/curated/website/pool-money", True, 1440, 4000),
    ("poolmoney-mobile", "https://poolmoney.com/", True, 390, 844),
]


def page_info(page):
    return page.evaluate(
        """() => {
          const h1 = document.querySelector('h1');
          const h1s = [...document.querySelectorAll('h1,h2')].slice(0, 8).map(el => {
            const s = getComputedStyle(el);
            return {text: el.innerText.slice(0,80), size: s.fontSize, weight: s.fontWeight};
          });
          return {
            title: document.title,
            h1: h1?.innerText,
            headings: h1s,
            sectionCount: document.querySelectorAll('section').length,
            bodyBg: getComputedStyle(document.body).backgroundColor,
            bodyFont: getComputedStyle(document.body).fontFamily,
          };
        }"""
    )


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, url, full, w, h in SHOTS:
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(url, wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(2500)
            path = OUT / f"{name}.png"
            page.screenshot(path=str(path), full_page=full)
            print(f"OK {path} ({path.stat().st_size} bytes)")
            if name.startswith("poolmoney-hero"):
                import json

                print(json.dumps(page_info(page), indent=2))
            page.close()
        browser.close()


if __name__ == "__main__":
    main()
