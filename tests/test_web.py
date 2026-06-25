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
    "框架审计 + 对抗审查 + Cutline。",
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
    assert 'data-i18n="hero_docs_link"' in serve.PAGE
    assert "gate-map" in serve.PAGE
    assert "Frame Audit" in serve.PAGE
    assert "框架审计" in serve.PAGE
    assert "trust-band" in serve.PAGE
    assert 'data-i18n="trust_band_github"' in serve.PAGE
    assert 'data-i18n="trust_examples"' in serve.PAGE
    assert 'data-i18n="trust_self_audit"' in serve.PAGE
    assert 'data-i18n="trust_schema"' in serve.PAGE
    assert 'data-i18n="trust_byok"' in serve.PAGE
    assert 'href="#demo"' in serve.PAGE
    assert 'data-i18n="btn_run_sample_hero"' in serve.PAGE
    assert "preview-must-fix" in serve.PAGE
    assert "falsify.review.v1" in serve.PAGE
    assert "workbench-panel" in serve.PAGE
    assert "workbench-collapse" not in serve.PAGE
    assert 'class="btn primary" href="#demo"' in serve.PAGE
    assert "NOT_VIABLE" not in serve.PAGE
    assert "CAUGHT" not in serve.PAGE
    assert "id=\"pricing\"" not in serve.PAGE
    assert "deliverables" not in serve.PAGE
    assert "evidence-grid" not in serve.PAGE
    assert "trust-strip" not in serve.PAGE
    assert 'id="not-falsify"' not in serve.PAGE


def test_homepage_limits_section():
    assert 'id="limits"' in serve.PAGE
    assert 'data-i18n="limits_tag"' in serve.PAGE
    assert 'data-i18n="ap_1"' in serve.PAGE
    assert 'data-i18n="ap_2"' in serve.PAGE
    assert 'data-i18n="ap_3"' in serve.PAGE
    assert 'data-i18n="boundary_h2"' in serve.PAGE
    assert 'data-i18n="boundary_p"' in serve.PAGE
    assert "Cutline-only ≠ full Falsify" in serve.PAGE
    assert "只有 Cutline ≠ 完整 Falsify" in serve.PAGE
    assert "limits-grid" in serve.PAGE


def test_homepage_layers_strip():
    assert 'class="layers-strip"' in serve.PAGE
    assert 'data-i18n="hero_layers_l1_tag"' in serve.PAGE
    assert 'data-i18n="hero_layers_l3_tag"' in serve.PAGE
    assert 'data-i18n="hero_layers_verdicts"' in serve.PAGE
    assert 'class="layer-body"' not in serve.PAGE
    assert 'data-i18n="hero_layers_hook"' not in serve.PAGE
    assert 'data-i18n="hero_layers_intro"' not in serve.PAGE


def test_homepage_quote_attribution_and_avatar():
    assert "Chris Shi" in serve.PAGE
    assert "史可鉴" not in serve.PAGE
    assert "Founder, Falsify" not in serve.PAGE
    assert "Falsify 创始人" not in serve.PAGE
    assert 'src="/assets/chris-shi-founder.png"' in serve.PAGE
    assert 'alt="Chris Shi"' in serve.PAGE
    assert 'aria-label="Chris Shi"' in serve.PAGE
    assert 'avatar-initial' not in serve.PAGE
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
    assert serve.PAGE.index('class="trust-band"') < serve.PAGE.index('class="quote"')
    assert serve.PAGE.index('class="quote"') < serve.PAGE.index('class="hero-layers"')
    assert serve.PAGE.index('class="hero-layers"') < serve.PAGE.index('id="demo"')
    assert serve.PAGE.index('id="demo"') < serve.PAGE.index('id="artifact"')
    assert "PASS / PASS_WITH_DEBT / BLOCK" in serve.PAGE
    assert "差一个机制就要上实盘" in serve.PAGE
    assert "one mechanic away from live money" in serve.PAGE


def test_homepage_workbench_partial_scope_copy():
    assert 'data-i18n="workbench_scope"' in serve.PAGE
    assert "not full Falsify" in serve.PAGE
    assert "非完整 Falsify" in serve.PAGE
    assert 'data-i18n="try_lead"' not in serve.PAGE
    assert 'data-i18n="demo_note"' not in serve.PAGE


def test_web_template_contains_public_product_markers():
    assert "Review first. Trust after." in serve.PAGE
    assert "Frame Audit + Adversarial Review + Cutline." in serve.PAGE
    assert "Frame Audit · Adversarial Review · Cutline" in serve.PAGE
    assert "框架审计 · 对抗审查 · Cutline" in serve.PAGE
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
    assert b'id="lang-btn"' in body
    assert b"docs.js" in body or b"falsify-lang" in body


def test_docs_index_zh_route_returns_200():
    handler = make_handler("/docs/?lang=zh")
    handler.do_GET()

    assert handler.status_code == 200
    body = handler.wfile.getvalue()
    assert b"lang=zh" in body
    assert b"lang=\"zh-CN\"" in body
    assert "文档".encode() in body
    assert "安装 PR 闸门".encode() in body
    assert "精选".encode() in body


def test_docs_markdown_route_returns_200():
    handler = make_handler("/docs/00-getting-started.md")
    handler.do_GET()

    assert handler.status_code == 200
    body = handler.wfile.getvalue()
    assert b"Getting Started" in body
    assert b"docs-sidebar" in body
    assert b'class="active"' in body
    assert b"doc-body" in body


def test_docs_markdown_zh_route_returns_translated_body():
    handler = make_handler("/docs/00-getting-started.md?lang=zh")
    handler.do_GET()

    assert handler.status_code == 200
    body = handler.wfile.getvalue()
    assert b"lang=\"zh-CN\"" in body
    assert "快速开始".encode() in body
    assert "对抗审查框架".encode() in body
    assert b'<p class="doc-untranslated"' not in body


def test_docs_markdown_zh_install_guide():
    handler = make_handler("/docs/14-github-action-install.md?lang=zh")
    handler.do_GET()

    assert handler.status_code == 200
    body = handler.wfile.getvalue()
    assert "安装 Falsify GitHub Action".encode() in body
    assert "验收清单".encode() in body


def test_docs_markdown_zh_open_core_boundary():
    handler = make_handler("/docs/12-open-core-boundary.md?lang=zh")
    handler.do_GET()

    assert handler.status_code == 200
    body = handler.wfile.getvalue()
    assert "Open Core 边界".encode() in body
    assert "协议开源".encode() in body


def test_docs_untranslated_page_shows_notice():
    handler = make_handler("/docs/16-homepage-redesign-teardown.md?lang=zh")
    handler.do_GET()

    assert handler.status_code == 200
    body = handler.wfile.getvalue()
    assert b"doc-untranslated" in body
    assert b'<p class="doc-untranslated"' in body
    assert "此页暂无中文版".encode() in body


def test_docs_zh_typography_css():
    css = serve.DOCS_CSS
    assert "--font-zh:" in css
    assert "PingFang SC" in css
    assert 'html[lang="zh-CN"]' in css
    assert "word-break:keep-all" in css.replace(" ", "")


def test_doc_has_zh_helpers():
    assert serve.doc_has_zh("00-getting-started")
    assert serve.doc_has_zh("14-github-action-install")
    assert not serve.doc_has_zh("16-homepage-redesign-teardown")


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
    assert "托管策略" in serve.PAGE
    assert "Shared review templates" not in serve.PAGE
    assert 'class="boundary-block"' not in serve.PAGE


def test_homepage_social_and_favicon_meta():
    assert 'property="og:title"' in serve.PAGE
    assert 'property="og:image"' in serve.PAGE
    assert 'name="twitter:card"' in serve.PAGE
    assert "summary_large_image" in serve.PAGE
    assert "/static/favicon.svg" in serve.PAGE
    assert "/static/favicon.ico" in serve.PAGE
    assert "og-share.png" in serve.PAGE


def test_homepage_proof_strip_github():
    assert 'data-i18n="proof_github"' in serve.PAGE
    assert "github.com/shi275773124/Falsify" in serve.PAGE
    assert "proof-case" not in serve.PAGE
    assert "< 1 day" not in serve.PAGE
    assert "Only PASS" not in serve.PAGE
    assert "仅 PASS" not in serve.PAGE
    assert "3 protocol verdicts" in serve.PAGE
    css = Path(serve.WEB_DIR / "static/css/home.css").read_text(encoding="utf-8")
    assert "grid-template-columns: repeat(3, minmax(0, 1fr))" in css


def test_homepage_case_card_links():
    case_urls = [
        "https://github.com/shi275773124/Falsify/blob/main/examples/sample-block-report.json",
        "https://github.com/shi275773124/Falsify/blob/main/examples/real-cases/01-fictional-horizon-quant-audit.md",
        "https://github.com/shi275773124/Falsify/blob/main/examples/comparison-case-study/README.md",
    ]
    for url in case_urls:
        assert url in serve.PAGE
    links = serve.re.findall(r'<a class="case-link"([^>]*)>', serve.PAGE)
    assert len(links) == 3
    for attrs in links:
        assert 'target="_blank"' in attrs
        assert "noopener" in attrs
        assert "noreferrer" in attrs
    assert serve.PAGE.count('<article class="case-card">') == 3


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
    assert "falsify-lang" in js
