import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "design" / "falsify-flow-candidate"


def _source(name: str) -> str:
    return (CANDIDATE / name).read_text(encoding="utf-8-sig")


def test_provider_output_has_no_innerhtml_sink():
    js = _source("candidate.js")
    assert "innerHTML" not in js
    assert "renderReceipt" in js
    assert "replaceChildren" in js
    assert "textContent = String(text)" in js


def test_copy_command_is_stable_and_clipboard_fails_closed():
    js = _source("candidate.js")
    assert 'const copyCommand = "curl -sS http://127.0.0.1:8000/examples/sample-block-report.json | python -m json.tool";' in js
    assert 'typeof navigator === "undefined"' in js
    assert 'typeof navigator.clipboard.writeText !== "function"' in js
    assert "await navigator.clipboard.writeText(copyCommand)" in js
    assert "window.FalsifyFlow = { copyCommand, renderReceipt }" in js


def test_review_response_is_validated_before_json_use():
    js = _source("candidate.js")
    assert js.index("if (!response.ok)") < js.index('response.headers.get("content-type")') < js.index("response.json()") < js.index('renderReceipt(language === "zh"')
    assert 'includes("application/json")' in js


def test_language_aware_docs_links():
    html, js = _source("index.html"), _source("candidate.js")
    assert 'data-lang-path="/docs/"' in html
    assert 'data-lang-path="/docs/17-skills"' in html
    assert 'language === "zh" ? "?lang=zh" : ""' in js


def test_public_copy_is_native_bounded_and_avoids_old_slogan():
    html, js = _source("index.html"), _source("candidate.js")
    for forbidden in ("Candidate only", "这是候选页面", "先把证据摆出来。", "再谈结论。", "高后果 AI 输出", "真实权威路径", "可复现判决工件", "行动前声明闸门", "屎山", "电子捧哏", "胡说八道"):
        assert forbidden not in html + js
    for copy in ("\u522b\u8ba9\u201c\u5df2\u5b8c\u6210\u201d", "\u53ea\u5b58\u5728\u4e8e AI \u7684\u56de\u7b54\u91cc\u3002", "\u5728\u4f60\u5408\u5e76\u3001\u4ed8\u6b3e\u6216\u4e0a\u7ebf\u524d"):
        assert copy in js


def test_chinese_interactive_states_are_native_and_complete():
    js = _source("candidate.js")
    for state in ("复现命令已复制。", "剪贴板不可用，请手动复制：", "日志不等于状态证据。请补上部署后探针和回滚命令。", "“另一个 AI 已审查”不能作为验收证据。", "正在审查…", "审查失败", "需要配置"):
        assert state in js


def test_frontend_has_no_mojibake():
    production = _source("candidate.js") + "\n" + _source("index.html")
    assert re.search(r"\?{3,}", production) is None
    for glyph in ("�", "锟", "烫", "屯", "ï¿½", "Ã", "Â"):
        assert glyph not in production
