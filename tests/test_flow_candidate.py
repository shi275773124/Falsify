from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "design" / "falsify-flow-candidate"


def source(name):
    return (CANDIDATE / name).read_text(encoding="utf-8-sig")


def test_homepage_keeps_boundaries_and_brand_assets():
    html, js = source("index.html"), source("candidate.js")
    for marker in ('id="top"', 'id="proof"', 'id="difference"', 'id="how"', 'id="try"', 'id="review-claim"', 'id="partner"'):
        assert marker in html
    assert "PASS, PASS_WITH_DEBT, or BLOCK" in html
    assert 'class="brand-mark"' in html
    assert 'class="brand-wordmark"' in html
    assert "Falsify" in html
    assert 'fetch("/review"' in js
    assert 'href="#partner"' in html
    assert "navPartner" in js
    assert "合作" in js
    assert "Partner" in js


def test_light_theme_tokens_are_active():
    html, css = source("index.html"), source("candidate.css")
    assert 'content="light"' in html or 'color-scheme" content="light"' in html
    assert 'content="#fafafa"' in html
    assert "--ink:#fafafa" in css.replace(" ", "")
    assert "--cyan:#4f46e5" in css.replace(" ", "")
    assert "light SaaS" in css
    # No dark-theme color leaks on light production surface
    for leak in ("#06101d", "#0c1c30", "#b8ebe0", "#e8c4c9", "#6d8fa5"):
        assert leak not in css


def test_review_remains_user_triggered_and_fail_closed():
    html, js = source("index.html"), source("candidate.js")
    assert 'type="button"' in html
    for marker in ('response.status === 503', 'providerSetup', 'Content-Type', 'response.json()', 'renderReviewError'):
        assert marker in js
    assert "innerHTML" not in js


def test_chinese_font_stack_and_utf8_document():
    html, js, css = source("index.html"), source("candidate.js"), source("candidate.css")
    assert '<meta charset="utf-8">' in html
    # Narrative pins (zh): 看起来绿了 / 痛点
    for codepoints in (
        (0x770B, 0x8D77, 0x6765, 0x7EFF, 0x4E86),  # 看起来绿了
        (0x75DB, 0x70B9),  # 痛点
    ):
        assert ''.join(map(chr, codepoints)) in js
    for font in ('-apple-system', 'BlinkMacSystemFont', '"SF Pro SC"', '"PingFang SC"', '"Microsoft YaHei UI"', '"Noto Sans SC"'):
        assert font in css
    assert 'html[lang="zh-CN"]' in css


def test_mobile_menu_and_delivery_section_are_preserved():
    html, js, css = source("index.html"), source("candidate.js"), source("candidate.css")
    assert 'aria-expanded="false"' in html and 'nav.open' in css
    # Menu opens via setMenuOpen helper; outside click + Escape close it.
    assert "setMenuOpen" in js and 'classList.toggle("open"' in js
    assert 'event.key === "Escape"' in js or 'event.key==="Escape"' in js
    assert "menuCloseLabel" in js and "syncMenuLabel" in js
    assert 'id="delivery"' in html and "delivery-list" in html and ".status-badge" in css
    assert "overflow-x:clip" in css.replace(" ", "")
    assert "minmax(0,1fr)" in css.replace(" ", "")
    assert "footer a{" in css or "footer a{" in css.replace("\n", "")
    assert "min-height:44px" in css
