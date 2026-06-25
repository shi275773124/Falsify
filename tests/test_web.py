import json
from io import BytesIO
from pathlib import Path

import pytest

from web import serve


REQUIRED_PUBLIC_COPY = [
    "Review first. Trust after.",
    "Falsify does not argue. It asks one question: where is the evidence.",
    "先审，再信。",
    "Falsify 不争。只问一件事：证据在哪。",
    "Frame Audit + Adversarial Review + Cutline.",
    "框架审 + 对抗审 + Cutline。",
    "audit the audit channel itself",
    "审计通道本身也要被审计",
    "human-auditability break",
    "owner / lock / lifecycle",
    "duplicated authority sources",
    "rollback / verification path",
    "naming / status semantics that mislead",
    "命名与状态语义误导",
    "Semantic verdict nudge",
    "Prompt-only audit theater",
    "Monitor-failure laundering",
    "Must Fix",
    "Known Debt",
    "Delete",
    "Verdict",
    "Final",
    "Falsify classifies risk. It does not authorize action.",
    "Falsify 只做风险分类，不做执行授权。",
    "independent final judgment",
    "Self-review is not independent review.",
]


def test_extract_json_accepts_fenced_json():
    assert serve.extract_json('```json\n{"verdict":"PASS","risks":[]}\n```') == {
        "verdict": "PASS",
        "risks": [],
    }


def test_extract_json_rejects_missing_object():
    with pytest.raises(ValueError):
        serve.extract_json("no json here")


def test_web_prompt_contains_audit_channel_checks():
    assert "AI summary without raw evidence" in serve.RISK_SYSTEM
    assert "fake acceptance evidence" in serve.RISK_SYSTEM
    assert "logs treated as state verification" in serve.RISK_SYSTEM
    assert "second-model agreement treated as proof" in serve.RISK_SYSTEM
    assert "prompt-only audit theater" in serve.RISK_SYSTEM
    assert "semantic nudges toward PASS" in serve.RISK_SYSTEM
    assert "monitor failure laundering" in serve.RISK_SYSTEM
    assert "finish_reason" in serve.RISK_SYSTEM
    assert "usage/token counts" in serve.RISK_SYSTEM
    assert "Cutline" in serve.RISK_SYSTEM


def test_homepage_hero_redesign():
    assert "gate-panel" in serve.PAGE
    assert "hero-check-img" in serve.PAGE
    assert "/static/img/hero-block-check.png" in serve.PAGE
    assert 'data-i18n-alt="hero_img_alt"' in serve.PAGE
    assert "proof-strip" in serve.PAGE
    assert 'data-i18n="hero_definition"' in serve.PAGE
    assert 'data-i18n="hero_workbench_note"' in serve.PAGE
    assert "Frame Audit" in serve.PAGE
    assert "框架审" in serve.PAGE
    assert "trust-strip" in serve.PAGE
    assert 'data-i18n="trust_github"' in serve.PAGE
    assert 'data-i18n="trust_schema"' in serve.PAGE
    assert 'data-i18n="trust_byok"' in serve.PAGE
    assert 'href="#demo"' in serve.PAGE
    assert 'data-i18n="btn_run_sample_hero"' in serve.PAGE
    assert "preview-must-fix" in serve.PAGE
    assert "falsify.review.v1" in serve.PAGE
    assert "id=\"pricing\"" not in serve.PAGE
    assert "deliverables" not in serve.PAGE
    assert "evidence-grid" not in serve.PAGE


def test_homepage_antipattern_section():
    assert 'id="not-falsify"' in serve.PAGE
    assert 'data-i18n="antipattern_h2"' in serve.PAGE
    assert 'data-i18n="ap_1"' in serve.PAGE
    assert 'data-i18n="ap_2"' in serve.PAGE
    assert 'data-i18n="ap_3"' in serve.PAGE
    assert "Cutline-only ≠ full Falsify" in serve.PAGE
    assert "只有 Cutline ≠ 完整 Falsify" in serve.PAGE


def test_homepage_cutline_philosophy():
    assert 'data-i18n="rs_lead"' in serve.PAGE
    assert "Decides what blocks now" in serve.PAGE
    assert "决定当下什么阻塞" in serve.PAGE


def test_homepage_quote_attribution_and_avatar():
    assert "Chris Shi" in serve.PAGE
    assert "史可鉴" in serve.PAGE
    assert "Founder, Falsify" not in serve.PAGE
    assert "Falsify 创始人" not in serve.PAGE
    assert 'src="/assets/chris-shi-founder.png"' in serve.PAGE
    assert 'alt="史可鉴 / Chris Shi"' in serve.PAGE
    assert 'data-i18n="quote_cite">Chris Shi</cite>' in serve.PAGE
    css = Path(serve.WEB_DIR / "static/css/home.css").read_text(encoding="utf-8")
    assert "align-items: center" in css
    assert "flex-shrink: 0" in css
    assert "CTO · AI-native product team" not in serve.PAGE
    assert "CTO · AI 原生产品团队" not in serve.PAGE
    assert "applyLang();" in serve.PAGE


def test_homepage_hero_layers_section():
    assert 'class="hero-layers"' in serve.PAGE
    assert 'id="layers"' in serve.PAGE
    assert serve.PAGE.index('class="quote"') < serve.PAGE.index('class="hero-layers"')
    assert serve.PAGE.index('class="hero-layers"') < serve.PAGE.index('id="artifact"')
    assert 'data-i18n="hero_layers_hook"' in serve.PAGE
    assert 'data-i18n="hero_layers_l1_tag"' in serve.PAGE
    assert 'data-i18n="hero_layers_l3_body"' in serve.PAGE
    assert "AI made fake proof cheap." in serve.PAGE
    assert "AI 让假证明变便宜了。" in serve.PAGE
    assert "hidden state, authority drift, missing rollback." in serve.PAGE
    assert "隐式状态、越权路径、回滚缺失。" in serve.PAGE
    assert "false facts, fake acceptance, audit theater." in serve.PAGE
    assert "假事实、假验收、审计作秀。" in serve.PAGE
    assert "Three verdicts only." in serve.PAGE
    assert "走完，只落三档裁决。" in serve.PAGE
    assert "「日志绿了，不等于证据成立。我们不再假装它算数。」" in serve.PAGE
    assert '"Green logs aren\'t proof. We stopped pretending they were."' in serve.PAGE


def test_homepage_workbench_partial_scope_copy():
    assert 'data-i18n="workbench_scope"' in serve.PAGE
    assert "not machine-enforced Frame Audit" in serve.PAGE
    assert "非机审框架审" in serve.PAGE
    assert "adversarial demos" in serve.PAGE
    assert "对抗审样例" in serve.PAGE
    assert "not full Falsify" in serve.PAGE


def test_web_template_contains_public_product_markers():
    assert "Review first. Trust after." in serve.PAGE
    assert "Frame Audit + Adversarial Review + Cutline." in serve.PAGE
    assert "Full Falsify = Frame Audit + Adversarial Review + Cutline." in serve.PAGE
    assert "完整 Falsify = 框架审 + 对抗审 + Cutline" in serve.PAGE
    for phrase in REQUIRED_PUBLIC_COPY:
        assert phrase in serve.PAGE
    assert "PASS / PASS_WITH_DEBT / BLOCK" in serve.PAGE
    assert "Real backend, not fake analysis." in serve.PAGE
    assert '<canvas id="cvs" role="img"' in serve.PAGE
    css = Path(serve.WEB_DIR / "static/css/home.css").read_text(encoding="utf-8")
    assert "prefers-reduced-motion: reduce" in css
    assert "/docs/" in serve.PAGE
    assert "https://github.com/shi275773124/Falsify/blob/main/LICENSE" in serve.PAGE


def test_normalize_verdict_maps_legacy_and_unknown_to_public_values():
    assert serve.normalize_verdict("PROCEED") == "PASS"
    assert serve.normalize_verdict("PASS_WITH_DEBT") == "PASS_WITH_DEBT"
    assert serve.normalize_verdict("nope") == "BLOCK"


def test_i18n_keys_exist_in_english_and_chinese():
    keys = set()
    for match in serve.re.finditer(r'data-i18n="([^"]+)"', serve.PAGE):
        keys.add(match.group(1))

    assert keys
    js = Path(serve.WEB_DIR / "static/js/home.js").read_text(encoding="utf-8")
    for key in keys:
        assert f"{key}:" in js or f'"{key}"' in js

    en_block = js.split("en:", 1)[1].split("zh:", 1)[0]
    zh_block = js.split("zh:", 1)[1].split("};", 1)[0]
    missing_en = [key for key in keys if f"{key}:" not in en_block and f'"{key}"' not in en_block]
    missing_zh = [key for key in keys if f"{key}:" not in zh_block and f'"{key}"' not in zh_block]

    assert missing_en == []
    assert missing_zh == []


def make_handler(path):
    handler = serve.H.__new__(serve.H)
    handler.path = path
    handler.headers = {}
    handler.wfile = BytesIO()
    handler._headers_buffer = []
    handler.request_version = "HTTP/1.1"
    handler.command = "GET"
    handler.send_response = lambda code, message=None: setattr(handler, "status_code", code)
    handler.send_header = lambda *args: None
    handler.end_headers = lambda: None
    return handler


def test_docs_index_route_returns_200():
    handler = make_handler("/docs/")
    handler.do_GET()

    assert handler.status_code == 200
    body = handler.wfile.getvalue()
    assert b"Docs" in body
    assert b"Documentation" in body
    assert b"docs-sidebar" in body
    assert b"doc-card" in body


def test_docs_markdown_route_returns_200():
    handler = make_handler("/docs/00-getting-started.md")
    handler.do_GET()

    assert handler.status_code == 200
    body = handler.wfile.getvalue()
    assert b"Getting Started" in body
    assert b"docs-sidebar" in body
    assert b'class="active"' in body
    assert b"doc-body" in body


def test_static_traversal_is_rejected():
    assert serve.safe_repo_path("/docs/../LICENSE") is None
    assert serve.safe_repo_path("/docs/%2e%2e/LICENSE") is None
    assert serve.safe_web_static("/static/../serve.py") is None

    handler = make_handler("/docs/../LICENSE")
    handler.do_GET()
    assert handler.status_code == 404


def test_static_css_route_returns_200():
    handler = make_handler("/static/css/home.css")
    handler.do_GET()
    assert handler.status_code == 200
    body = handler.wfile.getvalue()
    assert b"gate-panel" in body


def test_examples_json_route_returns_200():
    handler = make_handler("/examples/sample-block-report.json")
    handler.do_GET()
    assert handler.status_code == 200
    data = json.loads(handler.wfile.getvalue())
    assert data["schema_version"] == "falsify.review.v1"


def test_head_root_returns_200():
    handler = make_handler("/")
    handler.command = "HEAD"
    handler.do_HEAD()
    assert handler.status_code == 200


def test_head_docs_markdown_returns_200():
    handler = make_handler("/docs/00-getting-started.md")
    handler.command = "HEAD"
    handler.do_HEAD()
    assert handler.status_code == 200


def test_homepage_open_core_licensing_footer():
    assert 'id="licensing"' in serve.PAGE
    assert 'data-i18n="licensing_p"' in serve.PAGE
    assert "/docs/12-open-core-boundary.md" in serve.PAGE
    assert "MIT (core)" in serve.PAGE
    assert "MIT（核心）" in serve.PAGE
    assert "Self-hosted · unlimited repos" in serve.PAGE
    assert "自托管，仓库不限" in serve.PAGE or "自托管 · 仓库不限" in serve.PAGE
    assert "hosted policy enforcement" in serve.PAGE
    assert "托管 policy" in serve.PAGE
    assert "Shared review templates" not in serve.PAGE


def test_homepage_social_and_favicon_meta():
    assert 'property="og:title"' in serve.PAGE
    assert 'property="og:image"' in serve.PAGE
    assert 'name="twitter:card"' in serve.PAGE
    assert "summary_large_image" in serve.PAGE
    assert "/static/favicon.svg" in serve.PAGE
    assert "/static/favicon.ico" in serve.PAGE
    assert "og-share.png" in serve.PAGE


def test_homepage_proof_strip_github_and_case():
    assert 'data-i18n="proof_github"' in serve.PAGE
    assert 'data-i18n="proof_case_val"' in serve.PAGE
    assert "github.com/shi275773124/Falsify" in serve.PAGE
    assert "Logs ≠ state proof" in serve.PAGE
    assert "日志 ≠ 状态证明" in serve.PAGE
    css = Path(serve.WEB_DIR / "static/css/home.css").read_text(encoding="utf-8")
    assert "grid-template-columns: repeat(4, 1fr)" in css


def test_homepage_block_stamp_animation():
    css = Path(serve.WEB_DIR / "static/css/home.css").read_text(encoding="utf-8")
    assert "block-stamp" in css
    assert "@keyframes block-stamp" in css
    assert "block-stamp" in serve.PAGE


def test_static_home_assets_route_returns_200():
    for path in (
        "/static/img/hero-block-check.png",
        "/static/img/og-share.png",
        "/static/favicon.svg",
        "/static/favicon.ico",
    ):
        handler = make_handler(path)
        handler.do_GET()
        assert handler.status_code == 200, path


def test_render_verdict_shows_upgrade_trigger():
    assert "upgrade_trigger" in serve.PAGE
    assert "Upgrade trigger:" in serve.PAGE
    assert "升级触发：" in serve.PAGE


def test_homepage_zh_cn_typography():
    css = Path(serve.WEB_DIR / "static/css/home.css").read_text(encoding="utf-8")
    tokens = Path(serve.WEB_DIR / "static/css/tokens.css").read_text(encoding="utf-8")
    js = Path(serve.WEB_DIR / "static/js/home.js").read_text(encoding="utf-8")

    assert "--font-zh:" in tokens
    assert "PingFang SC" in tokens
    assert 'html[lang="zh-CN"]' in css
    assert "word-break: keep-all" in css
    assert "line-height: 1.8" in css or "line-height: 1.82" in css
    assert 'classList.toggle("lang-zh"' in js
    assert 'document.documentElement.lang = isZh ? "zh-CN" : "en"' in js
