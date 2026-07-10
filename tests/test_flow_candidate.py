from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "design" / "falsify-flow-candidate"

def source(name: str) -> str:
    return (CANDIDATE / name).read_text(encoding="utf-8-sig")

def test_flow_candidate_has_v2_narrative_and_boundaries():
    html, js = source("index.html"), source("candidate.js")
    for marker in ('id="top"', 'id="demo"', 'id="proof"', 'id="difference"', 'id="how"', 'id="try"'):
        assert marker in html
    assert "PASS, PASS_WITH_DEBT, or BLOCK" in html
    assert "Don't let ?done?" in js
    assert "ILLUSTRATIVE DEMO" in html
    assert "flow-canvas.js" in html

def test_signature_demo_is_user_triggered_and_reduced_motion_safe():
    html, css, js, flow = source("index.html"), source("candidate.css"), source("candidate.js"), source("flow-canvas.js")
    for text in ("Deployment complete", "CI passed", "Logs complete", "AI review passed", "Target state unchanged", "BLOCK", "Must fix"):
        assert text in html or text in js
    assert 'class="demo-toggle"' in html
    assert "prefers-reduced-motion: reduce" in css
    assert 'matchMedia("(prefers-reduced-motion: reduce)")' in js
    assert 'stages = ["claim", "green-1", "green-2", "green-3", "readback", "block"]' in js
    assert "IntersectionObserver" in flow
    assert "innerHTML" not in js

def test_chinese_hero_is_native_and_utf8_safe():
    html, js, css = source("index.html"), source("candidate.js"), source("candidate.css")
    assert '<meta charset="utf-8">' in html
    for copy in ("\u522b\u8ba9\u201c\u5df2\u5b8c\u6210\u201d", "\u53ea\u5b58\u5728\u4e8e AI \u7684\u56de\u7b54\u91cc\u3002", "\u5728\u4f60\u5408\u5e76\u3001\u4ed8\u6b3e\u6216\u4e0a\u7ebf\u524d", "\u7ed9\u51fa\u4e00\u4efd\u80fd\u590d\u67e5\u7684 PASS / BLOCK \u56de\u6267"):
        assert copy in js
    for forbidden in ("先把证据摆出来。", "高后果工作", "攻击结论", "权威路径", "证据表面", "结论上限", "屎山", "电子捧哏", "胡说八道"):
        assert forbidden not in html + js
    assert 'html[lang="zh-CN"]' in css

def test_language_query_is_deterministic():
    js = source("candidate.js")
    assert 'new URLSearchParams(window.location.search).get("lang")' in js
    assert 'requestedLanguage === "zh" || requestedLanguage === "en"' in js

def test_apple_style_cjk_stack():
    css = source("candidate.css")
    for font in ('-apple-system', 'BlinkMacSystemFont', '"SF Pro SC"', '"PingFang SC"', '"Microsoft YaHei UI"', '"Noto Sans SC"'):
        assert font in css

def test_three_direct_inspectable_case_sources():
    html = source("index.html")
    for link in ("/examples/real-cases/02-derived-freshness-stale-panel.md", "/examples/real-cases/04-round3b-evidence-integrity-reversal.md", "/examples/real-cases/05-second-runtime-v068-sync-false-green.md"):
        assert link in html
