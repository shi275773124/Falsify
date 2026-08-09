from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "design" / "falsify-flow-candidate"


def source(name):
    return (CANDIDATE / name).read_text(encoding="utf-8-sig")


def test_every_declared_i18n_key_has_both_languages():
    html, js = source("index.html"), source("candidate.js")
    keys = []
    for token in ('data-i18n="', 'data-i18n-html="'):
        rest = html
        while token in rest:
            rest = rest.split(token, 1)[1]
            keys.append(rest.split('"', 1)[0])
    for key in keys:
        assert f"{key}:" in js, key


def test_visible_chinese_copy_is_native_and_not_mojibake():
    js = source("candidate.js")
    for phrase in ("\u83dc\u5355", "\u5fc5\u987b\u4fee\u590d", "\u4e0d\u662f\u53c8\u4e00\u4e2a\u6a21\u578b\u610f\u89c1", "\u6743\u5a01\u8def\u5f84"):
        assert phrase in js
    assert chr(0xfffd) not in source("index.html") + js


def test_language_toggle_uses_explicit_labels_and_accessible_state():
    html, js = source("index.html"), source("candidate.js")
    label = "\u4e2d\u6587"
    assert f">{label}</button>" in html
    assert 'document.querySelector(".lang").textContent = language === "zh" ? "EN" : "\u4e2d\u6587"' in js
    assert "??</button>" not in html


def test_language_selection_and_safe_render_contract():
    js = source("candidate.js")
    for marker in ('new URLSearchParams(window.location.search).get("lang")', 'requestedLanguage === "zh" || requestedLanguage === "en"', 'history.replaceState', 'document.documentElement.lang', 'renderReceipt'):
        assert marker in js
    assert "innerHTML" not in js


def test_chinese_copy_states_adapter_and_epistemic_boundaries():
    js = source("candidate.js")
    for copy in ("\u7b7e\u53d1\u8fb9\u754c\u5185\u7684\u8ba4\u77e5\u5c42\u88c1\u51b3", "\u6ca1\u6709\u516c\u5f00\u7684 adapter", "\u4e0d\u6388\u6743\u4efb\u4f55\u52a8\u4f5c"):
        assert copy in js


def test_chinese_copy_uses_native_product_language():
    js = source("candidate.js")
    # Product language pins aligned to two-pains narrative
    for copy in ("Agent \u8bf4", "\u6ca1\u6709\u516c\u5f00\u7684 adapter", "\u4e0d\u6388\u6743\u4efb\u4f55\u52a8\u4f5c", "\u8ba4\u77e5\u5c42"):
        assert copy in js
    for stale in ("\u5b9e\u65f6\u8bc1\u636e\u95e8", "\u88c1\u7ebf"):
        assert stale not in js
