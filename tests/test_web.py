import json
from io import BytesIO
from pathlib import Path
from web import serve

def handler(path, method="GET"):
    h=serve.H.__new__(serve.H); h.path=path; h.headers={}; h.wfile=BytesIO(); h._headers_buffer=[]; h.request_version="HTTP/1.1"; h.command=method
    h.send_response=lambda code,message=None:setattr(h,"status_code",code); h.send_header=lambda *args:None; h.end_headers=lambda:None
    return h

def test_production_root_is_formal_console():
    assert "Looks green isn't proof" in serve.PAGE
    assert "/docs/" in serve.PAGE
    assert "/review" in Path(serve.FLOW_HOME_DIR / "candidate.js").read_text(encoding="utf-8")
    assert "<form" not in serve.PAGE

def test_root_assets_are_versioned_and_brand_assets_are_served():
    assert "/assets/flow/home.css?v=" in serve.PAGE and "/assets/flow/home.js?v=" in serve.PAGE
    for page_path in ("/", "/?lang=zh", "/docs/", "/docs/00-getting-started.html"):
        page=handler(page_path); page.do_GET(); assert page.status_code==200
        body=page.wfile.getvalue().decode()
        assert "/static/favicon.svg" in body
        assert 'class="brand-mark"' in body
        assert 'class="brand-wordmark"' in body or "Falsify" in body
    # Public brand surface is brand-mark/wordmark + favicon (not legacy logo-dark).
    for asset_path in ("/static/favicon.svg", "/static/favicon.png"):
        asset=handler(asset_path); asset.do_GET(); assert asset.status_code==200 and asset.wfile.getvalue()

def test_docs_routes_use_current_flow_shell():
    for path in ("/docs/","/docs/?lang=zh","/docs/00-getting-started.html"):
        h=handler(path); h.do_GET(); assert h.status_code==200
        assert b"flow-docs" in h.wfile.getvalue()

def test_real_case_reader_routes_render_html_and_keep_raw_markdown():
    cases = (
        "02-derived-freshness-stale-panel",
        "04-round3b-evidence-integrity-reversal",
        "05-second-runtime-v068-sync-false-green",
    )
    for stem in cases:
        reader = handler(f"/examples/real-cases/{stem}")
        reader.do_GET()
        page = reader.wfile.getvalue().decode("utf-8")
        assert reader.status_code == 200
        assert "flow-docs" in page
        assert 'class="case-reader-nav"' in page
        assert f'/examples/real-cases/{stem}.md' in page

        raw = handler(f"/examples/real-cases/{stem}.md")
        raw.do_GET()
        assert raw.status_code == 200
        assert raw.wfile.getvalue().decode("utf-8-sig").startswith("# ")


def test_chinese_case_reader_uses_utf8_shell_and_localized_navigation():
    h = handler("/examples/real-cases/04-round3b-evidence-integrity-reversal?lang=zh")
    h.do_GET()
    page = h.wfile.getvalue().decode("utf-8")
    assert h.status_code == 200
    assert 'lang="zh-CN"' in page
    assert "返回案例" in page
    assert "查看 Markdown 原文 / 下载" in page


def test_review_request_validation_and_fail_closed(monkeypatch):
    h=handler("/review","POST"); h.headers={"Content-Length":"2"}; h.rfile=BytesIO(b"{}"); h.do_POST(); assert h.status_code==400
    monkeypatch.setattr(serve,"review",lambda text,scenario: (_ for _ in ()).throw(serve.falsify.FalsifyError("no api key")))
    payload=json.dumps({"text":"logs green","scenario":"production"}).encode(); h=handler("/review","POST"); h.headers={"Content-Length":str(len(payload))}; h.rfile=BytesIO(payload); h.do_POST()
    assert h.status_code==503 and json.loads(h.wfile.getvalue())["error"]["code"]=="provider_unavailable"

def test_security_headers_and_no_inline_csp_violations():
    headers = serve.H.SECURITY_HEADERS
    assert "script-src 'self'" in headers["Content-Security-Policy"]
    assert headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
    assert headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"
    assert headers["X-Frame-Options"] == "DENY"

def test_options_is_explicitly_rejected_without_cors():
    h = handler("/review", "OPTIONS")
    h.do_OPTIONS()
    assert h.status_code == 405
    assert json.loads(h.wfile.getvalue())["error"]["code"] == "method_not_allowed"

def test_static_traversal_rejected():
    assert serve.safe_repo_path("/docs/../LICENSE") is None
    assert serve.safe_web_static("/static/../serve.py") is None


def test_design_path_rejects_markdown_drafts():
    """Design mirrors serve product assets only — never internal .md drafts."""
    assert serve.safe_design_path("/design/falsify-flow-docs/notes.md") is None
    assert serve.safe_design_path("/design/any/internal-draft.md") is None
    h = handler("/design/falsify-flow-docs/notes.md")
    h.do_GET()
    assert h.status_code == 404


def test_case_reader_allowlist_blocks_non_public_stems():
    # On-disk drafts outside CASE_ALLOWLIST must not get an HTML reader shell.
    h = handler("/examples/real-cases/03-cron-wrapper-refresh-gate-rootfix")
    h.do_GET()
    assert h.status_code == 404


def test_github_action_markdown_renders_semantic_emphasis_and_table():
    h = handler("/docs/14-github-action-install.html")
    h.do_GET()
    body = h.wfile.getvalue().decode("utf-8")
    assert h.status_code == 200
    assert "<strong>target repo</strong>" in body
    assert "<table>" in body and '<th scope="col">Secret</th>' in body
    assert "**target repo**" not in body and "| Secret | Example |" not in body


def test_dsh_plugin_doc_is_public_and_homepage_lists_install_path():
    assert "18-dsh-plugin" in serve.DOCS_ALLOWLIST
    assert "18-dsh-plugin" in serve.DOC_FEATURED
    assert "18-dsh-plugin" in dict(serve.DOC_SECTIONS)["Use locally"]

    h = handler("/docs/18-dsh-plugin.html")
    h.do_GET()
    body = h.wfile.getvalue().decode("utf-8")
    assert h.status_code == 200
    assert "Install Falsify DeepSeek plugin" in body
    assert "dsh plugin --profile web add" in body
    assert "falsify this file" in body
    assert "claim_bearing" in body
    assert "<table>" in body

    zh = handler("/docs/18-dsh-plugin.html?lang=zh")
    zh.do_GET()
    zh_body = zh.wfile.getvalue().decode("utf-8")
    assert zh.status_code == 200
    assert "安装 Falsify DeepSeek 插件" in zh_body

    sitemap = handler("/sitemap.xml")
    sitemap.do_GET()
    sm = sitemap.wfile.getvalue().decode("utf-8")
    assert sitemap.status_code == 200
    assert "<loc>https://falsify.site/docs/18-dsh-plugin.html</loc>" in sm

    home = handler("/")
    home.do_GET()
    homepage = home.wfile.getvalue().decode("utf-8")
    assert home.status_code == 200
    assert 'data-i18n="heroPrimary">Install GitHub Action</a>' in homepage
    assert 'data-i18n="dshLink">Install DeepSeek plugin →</a>' in homepage
    assert 'data-lang-path="/docs/18-dsh-plugin.html"' in homepage
    js = (serve.FLOW_HOME_DIR / "candidate.js").read_text(encoding="utf-8")
    assert 'dshLink:"Install DeepSeek plugin →"' in js
    assert 'dshLink:"安装 DeepSeek 插件 →"' in js
    assert "DeepSeek plugin" in js



def test_assets_path_traversal_does_not_leak_repo():
    """MF-1: /assets/../ must not fall through to safe_repo_path(ROOT)."""
    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8", errors="replace")
    marker = "Falsify" if "Falsify" in readme else readme[:40]
    for path in (
        "/assets/../README.md",
        "/assets/..%2fREADME.md",
        "/assets/flow/../../README.md",
        "/assets/not-a-real-file.js",
    ):
        h = handler(path)
        h.do_GET()
        body = h.wfile.getvalue()
        assert h.status_code == 404, (path, h.status_code)
        assert marker.encode("utf-8") not in body or b"not_found" in body
        # JSON error body must not embed full README
        assert b"# Falsify" not in body and b"#!/usr/bin" not in body

def test_inline_md_blocks_dangerous_hrefs():
    assert "javascript:" not in serve.inline_md("[x](javascript:alert(1))")
    assert "data:" not in serve.inline_md("[x](data:text/html,hi)")
    assert 'href="https://example.com"' in serve.inline_md("[x](https://example.com)")
    assert 'href="/docs/"' in serve.inline_md("[x](/docs/)")

def test_hygiene_seo_and_selective_geo_routes():
    root = handler("/")
    root.do_GET()
    home = root.wfile.getvalue().decode("utf-8")
    assert root.status_code == 200
    assert 'rel="canonical" href="https://falsify.site/"' in home
    assert 'property="og:image" content="https://falsify.site/static/img/og-share.png"' in home
    assert 'name="twitter:card" content="summary_large_image"' in home

    og = handler("/static/img/og-share.png")
    og.do_GET()
    assert og.status_code == 200 and og.wfile.getvalue()[:8] == b"\x89PNG\r\n\x1a\n"

    robots = handler("/robots.txt")
    robots.do_GET()
    robots_body = robots.wfile.getvalue().decode("utf-8")
    assert robots.status_code == 200
    assert "Sitemap: https://falsify.site/sitemap.xml" in robots_body
    assert "ai-train=no" in robots_body
    assert "ai-input=yes" in robots_body
    assert "User-agent: GPTBot" in robots_body and "Allow: /" in robots_body
    assert "User-agent: CCBot" in robots_body and "Disallow: /" in robots_body
    assert "Disallow: /design/" in robots_body
    assert "Disallow: /review" in robots_body

    sitemap = handler("/sitemap.xml")
    sitemap.do_GET()
    sm = sitemap.wfile.getvalue().decode("utf-8")
    assert sitemap.status_code == 200
    assert "<loc>https://falsify.site/</loc>" in sm
    assert "<loc>https://falsify.site/docs/</loc>" in sm
    assert "<loc>https://falsify.site/docs/14-github-action-install.html</loc>" in sm
    assert "<loc>https://falsify.site/docs/verdict-vocabulary.html</loc>" in sm
    for stem in (
        "02-derived-freshness-stale-panel",
        "04-round3b-evidence-integrity-reversal",
        "05-second-runtime-v068-sync-false-green",
    ):
        assert f"<loc>https://falsify.site/examples/real-cases/{stem}</loc>" in sm

    llms = handler("/llms.txt")
    llms.do_GET()
    llms_body = llms.wfile.getvalue().decode("utf-8")
    assert llms.status_code == 200
    assert "Evidence gate" in llms_body
    assert "https://falsify.site/docs/14-github-action-install.html" in llms_body

    well_known = handler("/.well-known/llms.txt")
    well_known.do_GET()
    assert well_known.status_code == 200
    assert well_known.wfile.getvalue().decode("utf-8") == llms_body

    docs = handler("/docs/")
    docs.do_GET()
    docs_body = docs.wfile.getvalue().decode("utf-8")
    assert docs.status_code == 200
    assert 'rel="canonical" href="https://falsify.site/docs/"' in docs_body
    assert 'name="robots" content="index,follow"' in docs_body
    assert "verdict-vocabulary" in docs_body

    design = handler("/design/falsify-flow-docs/")
    design.do_GET()
    design_body = design.wfile.getvalue().decode("utf-8")
    assert design.status_code == 200
    assert 'name="robots" content="noindex,follow"' in design_body
