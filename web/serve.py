#!/usr/bin/env python3
"""Falsify local website and paste-and-go reviewer.

The homepage is static product/docs copy. The /review endpoint is real: it
reuses falsify.py and the configured provider or agent CLI.
"""
import json
import os
import posixpath
import re
import sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import falsify  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = Path(__file__).resolve().parent
ALLOWED_STATIC_EXTS = {".md", ".svg", ".png", ".gif", ".css", ".js", ".json", ".ico", ".webp"}
STATIC_CTYPE = {
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".gif": "image/gif",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
    ".ico": "image/x-icon",
    ".webp": "image/webp",
    ".html": "text/html; charset=utf-8",
    ".md": "text/plain; charset=utf-8",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
}
PROVIDER = os.environ.get("FALSIFY_PROVIDER")
_RELEASE_VERSION_RAW = os.environ.get("FALSIFY_RELEASE_SHA", "dev")
RELEASE_ASSET_VERSION = re.sub(r"[^A-Za-z0-9._-]", "-", _RELEASE_VERSION_RAW).strip("-.") or "dev"

SCENARIOS = {
    "general": "General AI-generated work. Attack false confidence and missing evidence.",
    "code": "AI-generated code or pull request. Watch for broken commands, risky defaults, and tests that checked the wrong thing.",
    "research": "Research or decision memo. Watch for stale data, misread tables, weak sources, and confident conclusions.",
    "production": "Deployment or production claim. Watch for logs-as-state, silent failure, monitor laundering, and missing rollback evidence.",
}

RISK_SYSTEM = """You are the Falsify Skeptic. Attack false confidence, force raw
evidence, and cut each finding into Must Fix, Known Debt, or Delete.
Scenario: {scenario}

Look specifically for:
- AI summary without raw evidence
- fake acceptance evidence
- logs treated as state verification
- second-model agreement treated as proof
- prompt-only audit theater
- semantic nudges toward PASS or PASS_WITH_DEBT
- monitor failure laundering
- missing raw verdict, parse status, HTTP status, finish_reason, or usage/token counts when available
- findings without Cutline classification

Return ONLY valid JSON, no prose around it:
{{"verdict":"PASS|PASS_WITH_DEBT|BLOCK",
  "risks":[{{"severity":"high|med|low",
             "cutline":"Must Fix|Known Debt|Delete",
             "issue":"one sentence: the problem + evidence needed",
             "minimal_action":"minimal current action",
             "upgrade_trigger":"required only for Known Debt"}}]}}

PASS only if no blocker and no debt remains. PASS_WITH_DEBT only if every debt
item has a concrete trigger. BLOCK if any Must Fix remains, if the current
decision relies on missing evidence, or if the output cannot be audited.
At most 6 risks, worst first.
"""


def extract_json(text):
    """Models sometimes wrap JSON in prose or code fences; pull out the object."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    a, b = text.find("{"), text.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no JSON object in response")
    return json.loads(text[a:b + 1])


def normalize_verdict(value):
    value = str(value or "BLOCK").upper()
    if value in {"PASS", "PASS_WITH_DEBT", "BLOCK"}:
        return value
    if value == "PROCEED":
        return "PASS"
    return "BLOCK"


def review(text, scenario):
    base, key, model = falsify.resolve_endpoint(provider=PROVIDER)
    system = RISK_SYSTEM.format(scenario=SCENARIOS.get(scenario, SCENARIOS["general"]))
    raw = falsify.chat(system, text, base, key, model)
    try:
        data = extract_json(raw)
    except (ValueError, json.JSONDecodeError):
        return {"verdict": "BLOCK", "risks": [], "raw": raw,
                "note": "model did not return clean JSON; showing raw output"}
    data["verdict"] = normalize_verdict(data.get("verdict"))
    data["risks"] = (data.get("risks") or [])[:6]
    return data


def _safe_under(base: Path, rel: str):
    if rel in {"", "."} or rel.startswith("../") or "/../" in f"/{rel}":
        return None
    target = (base / rel).resolve()
    try:
        target.relative_to(base.resolve())
    except ValueError:
        return None
    if target.suffix.lower() not in ALLOWED_STATIC_EXTS:
        return None
    return target


def safe_repo_path(url_path):
    raw = unquote(urlparse(url_path).path)
    normalized = posixpath.normpath(raw).lstrip("/")
    return _safe_under(ROOT, normalized)


def safe_web_static(url_path):
    raw = unquote(urlparse(url_path).path)
    if not raw.startswith("/static/"):
        return None
    rel = posixpath.normpath(raw[len("/static/"):]).lstrip("/")
    return _safe_under(WEB_DIR / "static", rel)


def safe_examples_path(url_path):
    raw = unquote(urlparse(url_path).path)
    if not raw.startswith("/examples/"):
        return None
    rel = posixpath.normpath(raw[len("/examples/"):]).lstrip("/")
    return _safe_under(ROOT / "examples", rel)


def safe_design_path(url_path):
    raw = unquote(urlparse(url_path).path)
    if not raw.startswith("/design/"):
        return None
    rel = posixpath.normpath(raw[len("/design/"):]).lstrip("/")
    if rel in {"", "."} or rel.startswith("../") or "/../" in f"/{rel}":
        return None
    target = (ROOT / "design" / rel).resolve()
    try:
        target.relative_to((ROOT / "design").resolve())
    except ValueError:
        return None
    if target.is_dir():
        return target
    allowed = {".html", ".png", ".css", ".js", ".svg", ".webp", ".ico", ".mp4", ".webm", ".md"}
    if target.suffix.lower() not in allowed:
        return None
    return target


def load_homepage():
    template = (WEB_DIR / "templates" / "home.html").read_text(encoding="utf-8")
    js = (WEB_DIR / "static" / "js" / "home.js").read_text(encoding="utf-8")
    sample_path = ROOT / "examples" / "sample-block-report.json"
    sample_json = sample_path.read_text(encoding="utf-8") if sample_path.is_file() else "{}"
    html = template.replace("__SAMPLE_JSON__", html_escape(sample_json))
    return html.replace("__HOME_JS__", js)


def html_escape(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def inline_md(text):
    out = html_escape(text)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', out)
    return out


DOCS_CSS = """
:root{color-scheme:dark;--bg:#090909;--bg-elevated:#111;--bg-panel:#161616;--fg:#f4f4f4;--muted:#8c8c8c;--border:#2a2a2a;--accent:#b8ff3c;--radius:10px;--font:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Arial,sans-serif;--font-zh:"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC",sans-serif;--mono:"IBM Plex Mono","SFMono-Regular",Consolas,monospace;--max:1120px;--pad:clamp(20px,4vw,40px)}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.65 var(--font)}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
html[lang="zh-CN"],html.lang-zh{font-family:var(--font-zh)}html[lang="zh-CN"] body,html.lang-zh body{font-family:var(--font-zh);line-height:1.82;word-break:keep-all}html[lang="zh-CN"] .doc-body h1,html.lang-zh .doc-body h1{letter-spacing:.02em;line-height:1.25}html[lang="zh-CN"] .doc-body h2,html.lang-zh .doc-body h2{letter-spacing:.04em}html[lang="zh-CN"] .docs-sidebar a,html.lang-zh .docs-sidebar a{font-family:var(--font-zh)}
.docs-nav{position:sticky;top:0;z-index:20;background:rgba(9,9,9,.92);backdrop-filter:blur(14px);border-bottom:1px solid var(--border)}.docs-nav .wrap{display:flex;align-items:center;justify-content:space-between;height:64px;gap:16px}.brand{font:800 18px/1 var(--font);color:var(--fg)}.brand:hover{text-decoration:none}.nav-links{display:flex;align-items:center;gap:18px;font-size:14px;color:var(--muted)}.nav-links a{color:var(--muted)}.nav-links a:hover{color:var(--fg);text-decoration:none}.lang-btn{background:transparent;border:1px solid var(--border);border-radius:8px;color:var(--muted);cursor:pointer;font:inherit;font-size:13px;padding:6px 12px}.lang-btn:hover{border-color:var(--fg);color:var(--fg)}
.doc-untranslated{margin:0 0 24px;padding:14px 16px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-panel);color:var(--muted);font-size:14px}
.docs-layout{display:grid;grid-template-columns:280px 1fr;gap:32px;padding:40px 0 80px}.docs-sidebar{position:sticky;top:88px;align-self:start;max-height:calc(100vh - 104px);overflow:auto;padding-right:8px}.docs-sidebar h2{font:600 11px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin:0 0 10px}.docs-sidebar section+section{margin-top:24px}.docs-sidebar ul{list-style:none;margin:0;padding:0}.docs-sidebar li+li{margin-top:4px}.docs-sidebar a{display:block;padding:8px 10px;border-radius:8px;color:var(--muted);font-size:14px;line-height:1.35}.docs-sidebar a:hover,.docs-sidebar a.active{background:var(--bg-panel);color:var(--fg);text-decoration:none}
.docs-main{min-width:0}.docs-main>section{margin-top:32px}.docs-main>section>h2{font-size:13px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin:0 0 14px}
.docs-hero{margin-bottom:32px;padding-bottom:24px;border-bottom:1px solid var(--border)}.docs-hero h1{margin:0 0 8px;font-size:clamp(32px,4vw,44px);line-height:1.05;letter-spacing:-.02em}.docs-hero p{margin:0;color:var(--muted);max-width:60ch}
.docs-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}.doc-card{display:block;padding:18px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-panel);color:inherit;text-decoration:none;transition:border-color .15s,transform .15s}.doc-card:hover{border-color:rgba(184,255,60,.35);transform:translateY(-1px);text-decoration:none}.doc-card .num{font:600 11px var(--mono);color:var(--accent);letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}.doc-card h3{margin:0 0 6px;font-size:17px;color:var(--fg)}.doc-card p{margin:0;color:var(--muted);font-size:14px;line-height:1.45}
.doc-body h1,.doc-body h2,.doc-body h3,.doc-body h4{line-height:1.2;letter-spacing:-.02em}.doc-body h1{font-size:36px;margin:0 0 16px}.doc-body h2{font-size:24px;margin:32px 0 12px;padding-top:8px;border-top:1px solid var(--border)}.doc-body h3{font-size:18px;margin:24px 0 8px}.doc-body p,.doc-body li{color:#d6d6d6}.doc-body p{margin:0 0 14px}.doc-body ul,.doc-body ol{margin:0 0 16px;padding-left:22px}.doc-body li+li{margin-top:6px}.doc-body code{font:13px/1.4 var(--mono);background:#0d0d0d;border:1px solid var(--border);border-radius:6px;padding:2px 6px}.doc-body pre{margin:0 0 18px;padding:16px;border:1px solid var(--border);border-radius:12px;background:#0d0d0d;overflow:auto}.doc-body pre code{display:block;padding:0;border:none;background:transparent;font:13px/1.6 var(--mono);color:#d7dde7;white-space:pre-wrap}.doc-body table{width:100%;border-collapse:collapse;margin:0 0 18px;font-size:14px}.doc-body th,.doc-body td{border:1px solid var(--border);padding:10px 12px;text-align:left}.doc-body th{background:var(--bg-panel);color:var(--fg)}.doc-body td{color:#d6d6d6}
.wrap{width:min(var(--max),calc(100% - var(--pad)*2));margin:0 auto}
@media(max-width:900px){.docs-layout{grid-template-columns:1fr}.docs-sidebar{position:static;max-height:none}.docs-grid{grid-template-columns:1fr}}
"""


DOC_SECTIONS = [
    ("Start", ["00-getting-started", "17-skills", "14-github-action-install", "02-setup", "04-troubleshooting"]),
    ("Framework", ["01-architecture", "05-adversarial-review", "06-risk-scalpel", "07-audit-channel-risks", "08-examples", "09-brooks-lint"]),
    ("Product", ["10-team-delivery-and-business-model", "11-byok-and-policy", "12-open-core-boundary", "13-team-edition-spec"]),
    ("Ops", ["15-ci-and-release-gate", "03-collaboration"]),
]

DOC_FEATURED = ["17-skills", "14-github-action-install", "00-getting-started", "12-open-core-boundary"]

DOC_SECTION_LABELS = {
    "en": {"Start": "Start", "Framework": "Framework", "Product": "Product", "Ops": "Ops", "Featured": "Featured"},
    "zh": {"Start": "入门", "Framework": "框架", "Product": "产品", "Ops": "运维", "Featured": "精选"},
}

DOCS_CHROME = {
    "en": {
        "nav_docs": "Docs",
        "nav_home": "Home",
        "suffix": "Falsify docs",
        "index_title": "Documentation",
        "index_h1": "Documentation",
        "index_lead": "Install the PR gate, learn the framework, and ship decision artifacts your team can defend.",
        "card_open": "Open guide",
        "untranslated": "This page is not yet available in Chinese. Showing the English version.",
    },
    "zh": {
        "nav_docs": "文档",
        "nav_home": "首页",
        "suffix": "Falsify 文档",
        "index_title": "文档",
        "index_h1": "文档",
        "index_lead": "安装 PR 闸门、理解框架，产出团队能辩护的决策产物。",
        "card_open": "打开指南",
        "untranslated": "此页暂无中文版，以下为英文原文。",
    },
}


def parse_lang(query_string):
    params = parse_qs(query_string or "")
    values = params.get("lang") or []
    return "zh" if values and values[0] == "zh" else "en"


def doc_zh_path(stem):
    return ROOT / "docs" / f"{stem}.zh-CN.md"


def doc_has_zh(stem):
    return doc_zh_path(stem).is_file()


def doc_files():
    paths = sorted((ROOT / "docs").glob("*.md"))
    stems = {}
    for p in paths:
        if p.stem.endswith(".zh-CN"):
            continue
        if p.stem == "15-ci-and-release-gates" and (ROOT / "docs" / "15-ci-and-release-gate.md").is_file():
            continue
        stems[p.stem] = p
    return stems


def doc_title(stem, lang="en"):
    path = doc_zh_path(stem) if lang == "zh" and doc_has_zh(stem) else ROOT / "docs" / f"{stem}.md"
    if not path.is_file():
        return stem.replace("-", " ").title()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("# "):
            title = line[2:].strip()
            return re.sub(r"^\d+\.\s*", "", title)
    return stem.replace("-", " ").title()


def docs_href(stem, lang):
    href = f"/docs/{stem}.md"
    return f"{href}?lang=zh" if lang == "zh" else href


def docs_nav_html(current=None, lang="en"):
    files = doc_files()
    labels = DOC_SECTION_LABELS.get(lang, DOC_SECTION_LABELS["en"])
    blocks = []
    for section, stems in DOC_SECTIONS:
        items = []
        for stem in stems:
            if stem not in files:
                continue
            cls = "active" if current == f"{stem}.md" else ""
            active_attr = ' class="active"' if cls else ""
            items.append(
                f'<li><a{active_attr} href="{docs_href(stem, lang)}">{html_escape(doc_title(stem, lang))}</a></li>'
            )
        if items:
            section_label = labels.get(section, section)
            blocks.append(
                f'<section><h2 data-i18n-section="{html_escape(section)}">{html_escape(section_label)}</h2>'
                f"<ul>{''.join(items)}</ul></section>"
            )
    return "".join(blocks)


FLOW_HOME_DIR = ROOT / "design" / "falsify-flow-candidate"
FLOW_DOCS_DIR = ROOT / "design" / "falsify-flow-docs"

FLOW_DOCS_ZH = {
    "skip": "\u8df3\u5230\u6b63\u6587",
    "nav_docs": "\u6587\u6863",
    "menu_open": "\u6253\u5f00\u83dc\u5355",
    "menu_close": "\u5173\u95ed\u83dc\u5355",
    "language": "\u5207\u6362\u5230\u82f1\u6587",
    "eyebrow": "Falsify \u6587\u6863",
    "index_title": "Falsify \u6587\u6863",
    "index_h1": "\u5ba1\u67e5\u4e0d\u662f\u66ff\u4f60\u505a\u51b3\u5b9a\u3002\u5b83\u5148\u628a\u4f9d\u636e\u6446\u51fa\u6765\u3002",
    "index_lead": "\u4ece\u672c\u5730 CLI \u5f00\u59cb\uff0c\u4e86\u89e3\u56de\u6267\u7ed3\u6784\u3001\u5ba1\u67e5\u6df1\u5ea6\u548c\u5404\u9886\u57df\u7684\u6269\u5c55\u8fb9\u754c\u3002",
    "card_open": "\u67e5\u770b\u6307\u5357",
    "untranslated": "\u9875\u9762\u6682\u65f6\u6ca1\u6709\u4e2d\u6587\u7248\uff0c\u4ee5\u4e0b\u663e\u793a\u82f1\u6587\u539f\u6587\u3002",
}

FLOW_DOCS_ZH_SECTION_LABELS = {
    "Start": "\u5f00\u59cb\u4f7f\u7528",
    "Framework": "\u6838\u5fc3\u6982\u5ff5",
    "Product": "\u9886\u57df\u6307\u5357",
    "Ops": "\u53c2\u8003",
}


def flow_docs_href(stem, lang, canonical=False):
    prefix = "/docs" if canonical else "/design/falsify-flow-docs"
    href = f"{prefix}/{stem}.html"
    return f"{href}?lang=zh" if lang == "zh" else href

def flow_docs_nav_html(current=None, lang="en", canonical=False):
    labels = FLOW_DOCS_ZH_SECTION_LABELS if lang == "zh" else DOC_SECTION_LABELS["en"]
    blocks = []
    for section, stems in DOC_SECTIONS:
        links = []
        for stem in stems:
            if stem in doc_files():
                active = ' class="active" aria-current="page"' if stem == current else ""
                links.append(f'<li><a{active} href="{flow_docs_href(stem, lang, canonical)}">{html_escape(doc_title(stem, lang))}</a></li>')
        if links:
            blocks.append(f'<section><h2>{html_escape(labels.get(section, section))}</h2><ul>{"".join(links)}</ul></section>')
    return "".join(blocks)

def flow_docs_shell(title, body, current=None, lang="en", canonical=False):
    is_zh = lang == "zh"
    lang_query = "?lang=zh" if is_zh else ""
    button = "EN" if is_zh else "\u4e2d\u6587"
    skip = FLOW_DOCS_ZH["skip"] if is_zh else "Skip to content"
    docs_label = FLOW_DOCS_ZH["nav_docs"] if is_zh else "Docs"
    docs_prefix = "/docs/" if canonical else "/design/falsify-flow-docs/"
    flow_prefix = "/" if canonical else "/design/falsify-flow-candidate/"
    docs_href = f"{docs_prefix}{lang_query}"
    flow_href = f"{flow_prefix}{lang_query}"
    menu_label = FLOW_DOCS_ZH["menu_open"] if is_zh else "Menu"
    language_label = FLOW_DOCS_ZH["language"] if is_zh else "Switch to Chinese"
    menu_close = FLOW_DOCS_ZH["menu_close"] if is_zh else "Menu"
    return f"""<!doctype html><html lang="{'zh-CN' if is_zh else 'en'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#020914"><title>{html_escape(title)} \u2014 Falsify Flow Docs</title><link rel="stylesheet" href="/design/falsify-flow-docs/candidate.css"></head><body><a class="skip" href="#main">{html_escape(skip)}</a><header class="flow-docs-header"><a class="flow-brand" href="{docs_prefix}{lang_query}">Falsify<span></span></a><div class="flow-header-actions"><a href="{flow_href}">Flow</a><a href="{docs_href}" aria-current="page">{html_escape(docs_label)}</a><button id="flow-lang" type="button" aria-label="{html_escape(language_label)}">{button}</button><button id="docs-menu" type="button" aria-expanded="false" aria-controls="flow-sidebar" data-open-label="{html_escape(menu_label)}" data-close-label="{html_escape(menu_close)}">{html_escape(menu_label)}</button></div></header><div class="flow-docs-layout"><aside id="flow-sidebar" class="flow-docs-sidebar"><p class="sidebar-kicker">FLOW / DOCS</p>{flow_docs_nav_html(current, lang, canonical)}</aside><main id="main" class="flow-docs-main">{body}</main></div><script src="/design/falsify-flow-docs/candidate.js"></script></body></html>"""


def flow_docs_index(lang="en", canonical=False):
    is_zh = lang == "zh"
    chrome = FLOW_DOCS_ZH if is_zh else DOCS_CHROME["en"]
    labels = FLOW_DOCS_ZH_SECTION_LABELS if is_zh else DOC_SECTION_LABELS["en"]
    cards=[]
    for section, stems in DOC_SECTIONS:
        for stem in stems:
            if stem in doc_files():
                card_meta = chrome["card_open"] if is_zh else stem.replace("-", " ")
                cards.append(f'<a class="flow-doc-card" href="{flow_docs_href(stem, lang, canonical)}"><span>{html_escape(labels.get(section, section))}</span><h2>{html_escape(doc_title(stem, lang))}</h2><p>{html_escape(card_meta)} <b>\u2192</b></p></a>')
    eyebrow = chrome["eyebrow"] if is_zh else "FLOW / KNOWLEDGE BASE"
    body=f'<section class="flow-doc-hero"><p class="eyebrow">{html_escape(eyebrow)}</p><h1>{html_escape(chrome["index_h1"])}</h1><p>{html_escape(chrome["index_lead"])}</p></section><section class="flow-doc-grid">{"".join(cards)}</section>'
    return flow_docs_shell(chrome["index_title"], body, lang=lang, canonical=canonical)

def flow_docs_page(stem, lang="en", canonical=False):
    text, untranslated=resolve_doc_markdown(stem, lang)
    if not text: return None
    rendered=render_markdown(text, doc_title(stem, lang), lang=lang, untranslated=False)
    article=rendered.split('<main class="docs-main">',1)[1].split('</main>',1)[0]
    if untranslated:
        notice = FLOW_DOCS_ZH["untranslated"]
        article = f'<p class="doc-untranslated"><strong>\u63d0\u793a</strong>{html_escape(notice)}</p>{article}'
    return flow_docs_shell(doc_title(stem, lang), article, current=stem, lang=lang, canonical=canonical)


def load_docs_js():
    return (WEB_DIR / "static" / "js" / "docs.js").read_text(encoding="utf-8")


def docs_shell(title, body_html, current_path=None, lang="en"):
    current = current_path.split("/")[-1] if current_path else None
    nav = docs_nav_html(current, lang)
    chrome = DOCS_CHROME.get(lang, DOCS_CHROME["en"])
    html_lang = "zh-CN" if lang == "zh" else "en"
    lang_class = ' class="lang-zh"' if lang == "zh" else ""
    home_href = "/?lang=zh" if lang == "zh" else "/"
    docs_index_href = "/docs/?lang=zh" if lang == "zh" else "/docs/"
    lang_btn = "EN" if lang == "zh" else "中文"
    docs_js = load_docs_js()
    return f"""<!doctype html>
<html lang="{html_lang}"{lang_class}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html_escape(title)} — {html_escape(chrome["suffix"])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>{DOCS_CSS}</style>
</head>
<body{lang_class}>
<nav class="docs-nav"><div class="wrap"><a class="brand" href="{home_href}">Falsify</a><div class="nav-links"><a href="{docs_index_href}" data-i18n="nav_docs">{html_escape(chrome["nav_docs"])}</a><a href="{home_href}" data-i18n="nav_home">{html_escape(chrome["nav_home"])}</a><a href="https://github.com/shi275773124/Falsify" data-i18n="nav_github">GitHub</a><button class="lang-btn" id="lang-btn" type="button">{lang_btn}</button></div></div></nav>
<div class="wrap docs-layout">
<aside class="docs-sidebar">{nav}</aside>
<main class="docs-main">{body_html}</main>
</div>
<script>{docs_js}</script>
</body>
</html>"""


def resolve_doc_markdown(stem, lang="en"):
    en_path = ROOT / "docs" / f"{stem}.md"
    zh_path = doc_zh_path(stem)
    if lang == "zh" and zh_path.is_file():
        return zh_path.read_text(encoding="utf-8"), False
    if lang == "zh" and en_path.is_file():
        return en_path.read_text(encoding="utf-8"), True
    if en_path.is_file():
        return en_path.read_text(encoding="utf-8"), False
    return "", False


def render_markdown(text, title="Falsify docs", current_path=None, lang="en", untranslated=False):
    body = ['<article class="doc-body">']
    if untranslated:
        notice = DOCS_CHROME.get(lang, DOCS_CHROME["en"])["untranslated"]
        body.append(f'<p class="doc-untranslated" data-i18n="untranslated">{html_escape(notice)}</p>')
    in_code = False
    code_lang = ""
    code_lines = []
    list_open = None

    def close_list():
        nonlocal list_open
        if list_open:
            body.append(f"</{list_open}>")
            list_open = None

    for raw in text.splitlines():
        line = raw.rstrip()
        if line.strip().startswith("```"):
            if not in_code:
                close_list()
                in_code = True
                code_lang = line.strip()[3:].strip()
                code_lines = []
            else:
                lang_cls = f' class="language-{html_escape(code_lang)}"' if code_lang else ""
                body.append(f"<pre><code{lang_cls}>{html_escape(chr(10).join(code_lines))}</code></pre>")
                in_code = False
                code_lang = ""
                code_lines = []
            continue
        if in_code:
            code_lines.append(line)
            continue

        stripped = line.strip()
        if not stripped:
            close_list()
            continue
        if stripped.startswith("# "):
            close_list()
            body.append(f"<h1>{inline_md(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            close_list()
            body.append(f"<h2>{inline_md(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            close_list()
            body.append(f"<h3>{inline_md(stripped[4:])}</h3>")
        elif stripped.startswith("#### "):
            close_list()
            body.append(f"<h4>{inline_md(stripped[5:])}</h4>")
        elif stripped.startswith("- "):
            if list_open != "ul":
                close_list()
                body.append("<ul>")
                list_open = "ul"
            body.append(f"<li>{inline_md(stripped[2:])}</li>")
        elif re.match(r"^\d+\.\s", stripped):
            if list_open != "ol":
                close_list()
                body.append("<ol>")
                list_open = "ol"
            list_text = re.sub(r"^\d+\.\s*", "", stripped)
            body.append(f"<li>{inline_md(list_text)}</li>")
        else:
            close_list()
            body.append(f"<p>{inline_md(stripped)}</p>")

    close_list()
    if in_code and code_lines:
        body.append(f"<pre><code>{html_escape(chr(10).join(code_lines))}</code></pre>")
    body.append("</article>")
    return docs_shell(title, "".join(body), current_path, lang)


def docs_index(lang="en"):
    files = doc_files()
    chrome = DOCS_CHROME.get(lang, DOCS_CHROME["en"])
    labels = DOC_SECTION_LABELS.get(lang, DOC_SECTION_LABELS["en"])
    featured_label = labels.get("Featured", "Featured")
    featured_cards = []
    for stem in DOC_FEATURED:
        if stem not in files:
            continue
        title = doc_title(stem, lang)
        featured_cards.append(
            f'<a class="doc-card" href="{docs_href(stem, lang)}">'
            f'<div class="num" data-i18n-section="Featured">{html_escape(featured_label)}</div>'
            f'<h3>{html_escape(title)}</h3>'
            f'<p data-i18n="card_open">{html_escape(chrome["card_open"])}</p></a>'
        )

    sections = []
    for section, stems in DOC_SECTIONS:
        cards = []
        for stem in stems:
            if stem in DOC_FEATURED or stem not in files:
                continue
            title = doc_title(stem, lang)
            num = stem.split("-", 1)[0] if stem[:2].isdigit() else section
            cards.append(
                f'<a class="doc-card" href="{docs_href(stem, lang)}">'
                f'<div class="num">{html_escape(num)}</div>'
                f'<h3>{html_escape(title)}</h3>'
                f'<p>{html_escape(stem.replace("-", " "))}</p></a>'
            )
        if cards:
            section_label = labels.get(section, section)
            sections.append(
                f'<section><h2 data-i18n-section="{html_escape(section)}">{html_escape(section_label)}</h2>'
                f'<div class="docs-grid">{"".join(cards)}</div></section>'
            )

    body = f"""
<div class="docs-hero">
  <h1 data-i18n="index_h1">{html_escape(chrome["index_h1"])}</h1>
  <p data-i18n="index_lead">{html_escape(chrome["index_lead"])}</p>
</div>
<section><h2 data-i18n-section="Featured">{html_escape(featured_label)}</h2><div class="docs-grid">{"".join(featured_cards)}</div></section>
{"".join(sections)}
"""
    return docs_shell(chrome["index_title"], body, lang=lang)


def load_flow_homepage():
    """Mount the immutable candidate at root with explicit asset URLs."""
    html = (FLOW_HOME_DIR / "index.html").read_text(encoding="utf-8-sig")
    asset_urls = {
        'href="candidate.css"': f'href="/assets/flow/home.css?v={RELEASE_ASSET_VERSION}"',
        'href="./candidate.css"': f'href="/assets/flow/home.css?v={RELEASE_ASSET_VERSION}"',
        'src="candidate.js"': f'src="/assets/flow/home.js?v={RELEASE_ASSET_VERSION}"',
        'src="./candidate.js"': f'src="/assets/flow/home.js?v={RELEASE_ASSET_VERSION}"',
        'src="flow-canvas.js"': f'src="/assets/flow/flow-canvas.js?v={RELEASE_ASSET_VERSION}"',
        'src="./flow-canvas.js"': f'src="/assets/flow/flow-canvas.js?v={RELEASE_ASSET_VERSION}"',
    }
    for source, mounted in asset_urls.items():
        html = html.replace(source, mounted)
    return html


PAGE = load_flow_homepage()

class H(BaseHTTPRequestHandler):
    SECURITY_HEADERS = {
        "Content-Security-Policy": (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; font-src 'self'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; "
            "form-action 'self'"
        ),
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    def _send(self, code, body=b"", ctype="application/json", head=False):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        if ctype.startswith("text/") or ctype in {"application/json", "application/javascript"}:
            if "charset=" not in ctype:
                ctype += "; charset=utf-8"
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        for name, value in self.SECURITY_HEADERS.items():
            self.send_header(name, value)
        self.end_headers()
        if not head:
            self.wfile.write(b)

    def _json_error(self, code, error_code, message, head=False):
        payload = {"error": {"code": error_code, "message": message}}
        return self._send(code, json.dumps(payload), head=head)

    def _flow_asset(self, parsed):
        prefix = "/assets/flow/"
        if not parsed.path.startswith(prefix):
            return None
        rel = posixpath.normpath(unquote(parsed.path[len(prefix):])).lstrip("/")
        aliases = {
            "home.css": "candidate.css",
            "home.js": "candidate.js",
            "flow-canvas.js": "flow-canvas.js",
        }
        filename = aliases.get(rel)
        return _safe_under(FLOW_HOME_DIR, filename) if filename else None

    def _route(self, head=False):
        parsed = urlparse(self.path)
        lang = parse_lang(parsed.query)
        path = parsed.path

        if path in {"/", "/index.html"}:
            return self._send(200, PAGE, "text/html", head=head)

        if path in {"/docs", "/docs/", "/docs/index.html"}:
            return self._send(200, flow_docs_index(lang, canonical=True), "text/html", head=head)

        if path.startswith("/docs/"):
            name = Path(path).name
            stem = name
            if name.endswith(".zh-CN.md"):
                lang = "zh"
            for suffix in (".zh-CN.md", ".html", ".md"):
                if stem.endswith(suffix):
                    stem = stem[:-len(suffix)]
                    break
            page = flow_docs_page(stem, lang, canonical=True)
            if page:
                return self._send(200, page, "text/html", head=head)
            return self._json_error(404, "not_found", "Resource not found.", head=head)

        if path in {"/design/falsify-flow-docs/", "/design/falsify-flow-docs/index.html"}:
            return self._send(200, flow_docs_index(lang), "text/html", head=head)
        if path.startswith("/design/falsify-flow-docs/") and path.endswith(".html"):
            page = flow_docs_page(Path(path).stem, lang)
            if page:
                return self._send(200, page, "text/html", head=head)
            return self._json_error(404, "not_found", "Resource not found.", head=head)

        target = self._flow_asset(parsed)
        if not target:
            target = safe_web_static(self.path) or safe_examples_path(self.path) or safe_design_path(self.path)
        if not target and path.startswith("/assets/"):
            target = safe_repo_path(self.path)
        if target and target.is_dir() and path.startswith("/design/"):
            target = target / "index.html"
        if target and target.is_file():
            suffix = target.suffix.lower()
            ctype = STATIC_CTYPE.get(suffix)
            if ctype:
                return self._send(200, target.read_bytes(), ctype, head=head)
        return self._json_error(404, "not_found", "Resource not found.", head=head)

    def do_HEAD(self):
        self._route(head=True)

    def do_GET(self):
        self._route()

    def do_POST(self):
        if urlparse(self.path).path != "/review":
            return self._json_error(404, "not_found", "Resource not found.")
        try:
            try:
                n = int(self.headers.get("Content-Length", 0))
                req = json.loads(self.rfile.read(n) or b"{}")
            except (TypeError, ValueError, json.JSONDecodeError):
                return self._json_error(400, "invalid_json", "Request body must be valid JSON.")
            if not isinstance(req, dict):
                return self._json_error(400, "invalid_request", "Request body must be a JSON object.")
            text = req.get("text")
            if not isinstance(text, str) or not text.strip():
                return self._json_error(400, "empty_text", "Text is required.")
            scenario = req.get("scenario", "general")
            if scenario not in SCENARIOS:
                return self._json_error(400, "invalid_scenario", "Scenario is not supported.")
            result = review(text.strip(), scenario)
            return self._send(200, json.dumps(result))
        except falsify.FalsifyError as exc:
            detail = str(exc).lower()
            if detail.startswith(("no endpoint", "no api key", "no model", "unknown provider")):
                return self._json_error(503, "provider_unavailable", "Review provider is not configured.")
            return self._json_error(502, "upstream_failure", "Review provider request failed.")
        except Exception:  # noqa: BLE001
            return self._json_error(500, "internal_error", "Review failed unexpectedly.")

    def log_message(self, *args):
        pass

def main():
    port = int(os.environ.get("PORT", "8000"))
    print(f"falsify web -> http://127.0.0.1:{port}  (Ctrl+C to stop)")
    try:
        ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
