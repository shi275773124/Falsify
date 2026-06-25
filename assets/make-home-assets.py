#!/usr/bin/env python3
"""Generate homepage hero screenshot mock + OG share card + favicon PNG."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "web" / "static"
IMG_DIR = OUT_DIR / "img"

BG = (9, 9, 9)
PANEL = (22, 22, 22)
ELEVATED = (17, 17, 17)
BORDER = (42, 42, 42)
FG = (244, 244, 244)
BODY = (214, 214, 214)
MUTED = (140, 140, 140)
BLOCK = (255, 92, 92)
PASS = (61, 214, 140)
ACCENT = (184, 255, 60)


def _font(size: int, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    path = candidates[0 if mono else 1]
    for p in candidates if mono else [candidates[1], candidates[0], *candidates[2:]]:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _rounded_rect(draw: ImageDraw.ImageDraw, xy, radius: int, fill, outline=None, width: int = 1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_hero_check() -> Image.Image:
    w, h = 840, 520
    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)

    pad = 24
    panel = (pad, pad, w - pad, h - pad)
    _rounded_rect(draw, panel, 14, ELEVATED, outline=BORDER, width=1)

    mono_sm = _font(11, mono=True)
    mono_md = _font(13, mono=True)
    sans_md = _font(15)
    sans_sm = _font(12)

    head_y = pad + 14
    draw.text((pad + 16, head_y), "FALSIFY REVIEW", fill=MUTED, font=mono_sm)
    badge_x = w - pad - 16 - 72
    _rounded_rect(draw, (badge_x, head_y - 4, badge_x + 72, head_y + 22), 999, (40, 18, 18), outline=(120, 40, 40))
    draw.text((badge_x + 12, head_y), "BLOCK", fill=BLOCK, font=mono_md)

    stage_top = pad + 52
    stage_h = 58
    stages = [("Frame", "PASS", PASS), ("Evidence", "PASS", PASS), ("Cutline", "PASS", PASS), ("Verdict", "BLOCK", BLOCK)]
    col_w = (w - pad * 2) // 4
    for i, (label, val, color) in enumerate(stages):
        x0 = pad + i * col_w
        x1 = x0 + col_w
        fill = (28, 14, 14) if val == "BLOCK" else PANEL
        draw.rectangle((x0, stage_top, x1, stage_top + stage_h), fill=fill, outline=BORDER)
        draw.text((x0 + 12, stage_top + 10), label.upper(), fill=MUTED, font=_font(9, mono=True))
        draw.text((x0 + 12, stage_top + 28), val, fill=color, font=mono_md)

    body_y = stage_top + stage_h + 18
    draw.text((pad + 16, body_y), "falsify.review.v1 · reports/deploy.md", fill=MUTED, font=_font(10, mono=True))
    draw.text((pad + 16, body_y + 22), "Deployment succeeded because logs completed.", fill=FG, font=sans_md)

    mf_y = body_y + 58
    _rounded_rect(draw, (pad + 16, mf_y, w - pad - 16, mf_y + 92), 8, (28, 14, 14), outline=(120, 40, 40))
    draw.text((pad + 28, mf_y + 10), "MUST FIX", fill=BLOCK, font=_font(10, mono=True))
    draw.text((pad + 28, mf_y + 28), "Logs are treated as state verification", fill=BODY, font=sans_sm)
    draw.text((pad + 28, mf_y + 50), "Minimal action: Add read-after-write probe", fill=MUTED, font=_font(11, mono=True))

    gh_y = h - pad - 36
    draw.line((pad + 16, gh_y - 10, w - pad - 16, gh_y - 10), fill=BORDER, width=1)
    draw.text((pad + 16, gh_y), "shi275773124/Falsify · pull request #42 · GitHub Checks", fill=MUTED, font=_font(11, mono=True))

    return img


def draw_og_card() -> Image.Image:
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, w, 6), fill=ACCENT)
    title = _font(72)
    sub = _font(28)
    tag = _font(22, mono=True)

    draw.text((80, 120), "Falsify", fill=FG, font=title)
    draw.text((80, 210), "Looks right is not enough.", fill=BODY, font=sub)
    draw.text((80, 270), "PASS · PASS_WITH_DEBT · BLOCK — backed by raw evidence.", fill=MUTED, font=tag)

    badge_x, badge_y = 80, 360
    _rounded_rect(draw, (badge_x, badge_y, badge_x + 120, badge_y + 44), 999, (40, 18, 18), outline=(120, 40, 40))
    draw.text((badge_x + 22, badge_y + 10), "BLOCK", fill=BLOCK, font=_font(20, mono=True))

    draw.text((80, h - 80), "falsify.zjdeng.xyz", fill=MUTED, font=tag)
    return img


def draw_favicon() -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    _rounded_rect(draw, (4, 4, size - 4, size - 4), 12, BG, outline=ACCENT, width=3)
    draw.text((18, 16), "F", fill=ACCENT, font=_font(32, mono=True))
    return img


def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    hero = draw_hero_check()
    hero.save(IMG_DIR / "hero-block-check.png", optimize=True)
    draw_og_card().save(IMG_DIR / "og-share.png", optimize=True)
    fav = draw_favicon()
    fav.save(OUT_DIR / "favicon.png")
    fav.resize((32, 32), Image.Resampling.LANCZOS).save(OUT_DIR / "favicon.ico", format="ICO")
    print(f"Wrote assets under {OUT_DIR}")


if __name__ == "__main__":
    main()
