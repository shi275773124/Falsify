#!/usr/bin/env python3
"""Export assets/moments-wechat-v1.html → moments-wechat-v1.png (1080×1350)."""

from __future__ import annotations

import http.server
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "moments-wechat-v1.html"
OUT = ROOT / "moments-wechat-v1.png"
WIDTH, HEIGHT = 1080, 1350

EDGE_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe",
]


def find_browser() -> Path | None:
    for p in EDGE_CANDIDATES:
        if p.is_file():
            return p
    return shutil.which("msedge") or shutil.which("chrome")


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def serve(directory: Path, port: int) -> http.server.ThreadingHTTPServer:
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def export_png(url: str, out: Path, browser: Path) -> None:
    import tempfile

    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.gettempdir()) / "falsify-moments-wechat-v1.png"
    if tmp.exists():
        tmp.unlink()
    profile = Path(tempfile.mkdtemp(prefix="falsify-edge-"))
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
        f"--window-size={WIDTH},{HEIGHT}",
        f"--screenshot={tmp}",
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    try:
        shutil.rmtree(profile, ignore_errors=True)
    except OSError:
        pass
    if proc.returncode != 0 and not tmp.is_file():
        raise RuntimeError(f"browser exit {proc.returncode}: {proc.stderr or proc.stdout}")
    for _ in range(40):
        if tmp.is_file() and tmp.stat().st_size > 10_000:
            break
        time.sleep(0.25)
    if not tmp.is_file():
        raise FileNotFoundError(f"screenshot not created (stderr: {proc.stderr})")
    shutil.copy2(tmp, out)
    tmp.unlink(missing_ok=True)


def validate_png(path: Path) -> None:
    from PIL import Image

    im = Image.open(path)
    if im.size != (WIDTH, HEIGHT):
        im = im.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        im.save(path, optimize=True)
    # Sanity: not a blank/near-black frame (bottom band should have accent pixels)
    px = im.load()
    accent_hits = 0
    for x in range(0, WIDTH, 40):
        r, g, b = px[x, HEIGHT - 80]
        if g > 180 and r > 140:
            accent_hits += 1
    if accent_hits < 2:
        raise RuntimeError("export may be clipped or blank — check layout")


def main() -> int:
    if not HTML.is_file():
        print(f"missing {HTML}", file=sys.stderr)
        return 1
    browser = find_browser()
    if not browser:
        print("need Edge or Chrome for headless screenshot", file=sys.stderr)
        return 1

    port = free_port()
    server = serve(ROOT, port)
    url = f"http://127.0.0.1:{port}/{HTML.name}"
    try:
        export_png(url, OUT, Path(browser))
        validate_png(OUT)
        print(f"ok {OUT} ({OUT.stat().st_size} bytes)")
        return 0
    finally:
        server.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
