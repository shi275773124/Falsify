import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "design" / "falsify-flow-candidate"

def _source(name: str) -> str:
    return (CANDIDATE / name).read_text(encoding="utf-8-sig")

def test_provider_output_has_no_innerhtml_sink():
    js = _source("candidate.js")
    assert "innerHTML" not in js
    assert "renderReceipt" in js and "replaceChildren" in js
    assert "textContent = String(text)" in js

def test_copy_command_is_stable_and_clipboard_fails_closed():
    js = _source("candidate.js")
    for marker in ("sample-block-report.json", "copyCommand", "python -m json.tool", 'typeof navigator === "undefined"', 'typeof navigator.clipboard.writeText !== "function"', "await navigator.clipboard.writeText(copyCommand)", "window.FalsifyFlow = { copyCommand, renderReceipt }"):
        assert marker in js

def test_review_response_is_validated_before_json_use():
    js = _source("candidate.js")
    assert js.index("if (!response.ok)") < js.index('response.headers.get("content-type")') < js.index("response.json()") < js.index('renderReceipt(language === "zh"')
    assert 'includes("application/json")' in js

def test_language_aware_docs_links():
    html, js = _source("index.html"), _source("candidate.js")
    assert 'data-lang-path="/docs/"' in html and 'data-lang-path="/docs/17-skills"' in html
    assert 'language === "zh" ? "?lang=zh" : ""' in js

def test_public_copy_is_native_bounded_and_avoids_old_slogan():
    html, js = _source("index.html"), _source("candidate.js")
    for forbidden in ("Candidate only", "\u8fd9\u662f\u5019\u9009\u9875\u9762", "\u5148\u628a\u8bc1\u636e\u6446\u51fa\u6765\u3002", "\u518d\u8c08\u7ed3\u8bba\u3002"):
        assert forbidden not in html + js
    for copy in ("\u5148\u653b\u51fb\u58f0\u660e", "\u5bf9\u6297\u5f0f\u5ba1\u67e5", "\u5b89\u88c5 GitHub Action"):
        assert copy in js

def test_chinese_interactive_states_are_native_and_complete():
    js = _source("candidate.js")
    for state in ("\u590d\u73b0\u547d\u4ee4\u5df2\u590d\u5236\u3002", "\u526a\u8d34\u677f\u4e0d\u53ef\u7528\uff0c\u8bf7\u624b\u52a8\u590d\u5236\uff1a", "\u7ebf\u4e0a\u7248\u672c\u4e0e\u58f0\u79f0\u63d0\u4ea4\u4e0d\u4e00\u81f4", "\u90e8\u7f72\u6210\u529f", "\u6b63\u5728\u5ba1\u67e5\u2026", "\u5ba1\u67e5\u5931\u8d25", "\u9700\u8981\u914d\u7f6e"):
        assert state in js

def test_frontend_has_no_mojibake():
    production = _source("candidate.js") + "\n" + _source("index.html")
    assert re.search(r"\?{3,}", production) is None
    for glyph in ("\ufffd", "\u951f", "\u70eb", "\u5c6f", "\u00ef\u00bf\u00bd", "\u00c3", "\u00c2"):
        assert glyph not in production
