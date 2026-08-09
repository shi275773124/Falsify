"""Local smoke tests for falsify.site mobile fixes."""
import re
import subprocess
import sys
import time
from pathlib import Path
import urllib.request
import urllib.error

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PORT = 8001


def wait_for_server(url, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2):
                return True
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"server did not start at {url}")


def fetch_html(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "falsify-smoke-test/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")


def main():
    proc = subprocess.Popen(
        [sys.executable, "-m", "web.serve"],
        cwd=ROOT,
        env={**dict(__import__("os").environ), "PORT": str(PORT)},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        base = f"http://127.0.0.1:{PORT}"
        wait_for_server(base)

        fails = []

        # P1/P2: case pages via HTTP (fast, no browser)
        for stem in (
            "01-fictional-horizon-quant-audit",
            "02-derived-freshness-stale-panel",
            "04-round3b-evidence-integrity-reversal",
            "05-second-runtime-v068-sync-false-green",
        ):
            url = f"{base}/examples/real-cases/{stem}"
            try:
                status, html = fetch_html(url, timeout=15)
            except urllib.error.HTTPError as e:
                fails.append(f"case page {stem} HTTP {e.code}")
                continue
            except Exception as e:
                fails.append(f"case page {stem} fetch failed: {e}")
                continue
            if status != 200:
                fails.append(f"case page {stem} status {status}")
                continue
            text = re.sub(r"<[^>]+>", "", html)
            raw_in_text = re.findall(r"\*\*[^*]+\*\*", text)
            print(f"Case {stem}: raw '**' in text = {len(raw_in_text)}")
            if raw_in_text:
                fails.append(f"P1 markdown bold broken in {stem}: {raw_in_text[:3]}")
            if "<blockquote>" not in html:
                fails.append(f"P1 markdown blockquote missing in {stem}")
            if "<table>" not in html:
                fails.append(f"P1 markdown table missing in {stem}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            def viewport(w, h):
                ctx = browser.new_context(viewport={"width": w, "height": h})
                page = ctx.new_page()
                return page, ctx

            # P0: Chinese homepage at 390px should not overflow horizontally
            page, ctx = viewport(390, 844)
            page.goto(f"{base}/?lang=zh", timeout=10000)
            page.wait_for_load_state("networkidle", timeout=5000)
            body_width = page.evaluate("document.body.scrollWidth")
            client_width = page.evaluate("document.documentElement.clientWidth")
            hero_copy = page.locator(".hero-copy")
            hero_copy_width = hero_copy.evaluate("el => el.scrollWidth") if hero_copy.count() else 0
            print(f"P0 zh homepage 390px: body scrollWidth={body_width}, clientWidth={client_width}, .hero-copy scrollWidth={hero_copy_width}")
            if body_width > client_width + 1:
                fails.append(f"P0 overflow: body scrollWidth {body_width} > clientWidth {client_width}")
            if hero_copy_width > client_width + 1:
                fails.append(f"P0 overflow: .hero-copy scrollWidth {hero_copy_width} > clientWidth {client_width}")
            ctx.close()

            # P0: English homepage at 390px should also not overflow
            page, ctx = viewport(390, 844)
            page.goto(f"{base}/", timeout=10000)
            page.wait_for_load_state("networkidle", timeout=5000)
            body_width_en = page.evaluate("document.body.scrollWidth")
            client_width_en = page.evaluate("document.documentElement.clientWidth")
            print(f"P0 en homepage 390px: body scrollWidth={body_width_en}, clientWidth={client_width_en}")
            if body_width_en > client_width_en + 1:
                fails.append(f"P0 EN overflow: body scrollWidth {body_width_en} > clientWidth {client_width_en}")
            ctx.close()

            # P1: receipt demo initial state should not be a tall blank card
            page, ctx = viewport(390, 844)
            page.goto(base, timeout=10000)
            page.wait_for_load_state("networkidle", timeout=5000)
            receipt = page.locator(".demo-receipt")
            receipt_count = receipt.count()
            receipt_height = receipt.evaluate("el => el.getBoundingClientRect().height") if receipt_count else 0
            print(f"P1 receipt initial height at 390px: {receipt_height}")
            if receipt_height > 430:
                fails.append(f"P1 blank receipt: initial height {receipt_height} > 430px")
            ctx.close()

            page, ctx = viewport(1280, 800)
            page.goto(base, timeout=10000)
            page.wait_for_load_state("networkidle", timeout=5000)
            receipt = page.locator(".demo-receipt")
            receipt_count = receipt.count()
            receipt_height = receipt.evaluate("el => el.getBoundingClientRect().height") if receipt_count else 0
            print(f"P1 receipt initial height at 1280px: {receipt_height}")
            if receipt_height > 380:
                fails.append(f"P1 blank receipt desktop: initial height {receipt_height} > 380px")
            ctx.close()

            browser.close()

        if fails:
            print("\nFAILED:")
            for f in fails:
                print(f"  - {f}")
            sys.exit(1)
        print("\nALL CHECKS PASSED")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
