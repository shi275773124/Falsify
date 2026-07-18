from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "design" / "falsify-flow-candidate"


def source(name):
    return (CANDIDATE / name).read_text(encoding="utf-8-sig")


def test_homepage_keeps_boundaries_and_brand_assets():
    html, js = source("index.html"), source("candidate.js")
    for marker in ('id="top"', 'id="proof"', 'id="difference"', 'id="how"', 'id="try"', 'id="review-claim"'):
        assert marker in html
    assert "PASS, PASS_WITH_DEBT, or BLOCK" in html
    assert 'class="brand-mark"' in html
    assert 'class="brand-wordmark"' in html
    assert "Falsify" in html
    assert 'fetch("/review"' in js


def test_review_remains_user_triggered_and_fail_closed():
    html, js = source("index.html"), source("candidate.js")
    assert 'type="button"' in html
    for marker in ('response.status === 503', 'providerSetup', 'Content-Type', 'response.json()', 'renderReviewError'):
        assert marker in js
    assert "innerHTML" not in js


def test_chinese_font_stack_and_utf8_document():
    html, js, css = source("index.html"), source("candidate.js"), source("candidate.css")
    assert '<meta charset="utf-8">' in html
    for codepoints in ((0x5148, 0x6838, 0x5bf9, 0x6743, 0x5a01, 0x6765, 0x6e90), (0x518d, 0x8ba9, 0x9ad8, 0x540e, 0x679c, 0x20, 0x41, 0x49, 0x20, 0x8f93, 0x51fa)):
        assert ''.join(map(chr, codepoints)) in js
    for font in ('-apple-system', 'BlinkMacSystemFont', '"SF Pro SC"', '"PingFang SC"', '"Microsoft YaHei UI"', '"Noto Sans SC"'):
        assert font in css
    assert 'html[lang="zh-CN"]' in css


def test_mobile_menu_and_tier_controls_are_preserved():
    html, js, css = source("index.html"), source("candidate.js"), source("candidate.css")
    assert 'aria-expanded="false"' in html and 'nav.classList.toggle("open")' in js and 'nav.open' in css and 'document.querySelectorAll(".tier")' in js
