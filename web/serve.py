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
from urllib.parse import unquote, urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import falsify  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_STATIC_EXTS = {".md", ".svg", ".png", ".gif", ".css"}
PROVIDER = os.environ.get("FALSIFY_PROVIDER")

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


def safe_repo_path(url_path):
    raw = unquote(urlparse(url_path).path)
    normalized = posixpath.normpath(raw).lstrip("/")
    if normalized in {"", "."} or normalized.startswith("../") or "/../" in raw:
        return None
    target = (ROOT / normalized).resolve()
    try:
        target.relative_to(ROOT)
    except ValueError:
        return None
    if target.suffix.lower() not in ALLOWED_STATIC_EXTS:
        return None
    return target


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
:root{color-scheme:dark;--bg:#090909;--bg-elevated:#111;--bg-panel:#161616;--fg:#f4f4f4;--muted:#8c8c8c;--border:#2a2a2a;--accent:#b8ff3c;--radius:10px;--font:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Arial,sans-serif;--mono:"IBM Plex Mono","SFMono-Regular",Consolas,monospace;--max:1120px;--pad:clamp(20px,4vw,40px)}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.65 var(--font)}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.docs-nav{position:sticky;top:0;z-index:20;background:rgba(9,9,9,.92);backdrop-filter:blur(14px);border-bottom:1px solid var(--border)}.docs-nav .wrap{display:flex;align-items:center;justify-content:space-between;height:64px;gap:16px}.brand{font:800 18px/1 var(--font);color:var(--fg)}.brand:hover{text-decoration:none}.nav-links{display:flex;gap:18px;font-size:14px;color:var(--muted)}.nav-links a{color:var(--muted)}.nav-links a:hover{color:var(--fg);text-decoration:none}
.docs-layout{display:grid;grid-template-columns:280px 1fr;gap:32px;padding:40px 0 80px}.docs-sidebar{position:sticky;top:88px;align-self:start;max-height:calc(100vh - 104px);overflow:auto;padding-right:8px}.docs-sidebar h2{font:600 11px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin:0 0 10px}.docs-sidebar section+section{margin-top:24px}.docs-sidebar ul{list-style:none;margin:0;padding:0}.docs-sidebar li+li{margin-top:4px}.docs-sidebar a{display:block;padding:8px 10px;border-radius:8px;color:var(--muted);font-size:14px;line-height:1.35}.docs-sidebar a:hover,.docs-sidebar a.active{background:var(--bg-panel);color:var(--fg);text-decoration:none}
.docs-main{min-width:0}.docs-main>section{margin-top:32px}.docs-main>section>h2{font-size:13px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin:0 0 14px}
.docs-hero{margin-bottom:32px;padding-bottom:24px;border-bottom:1px solid var(--border)}.docs-hero h1{margin:0 0 8px;font-size:clamp(32px,4vw,44px);line-height:1.05;letter-spacing:-.02em}.docs-hero p{margin:0;color:var(--muted);max-width:60ch}
.docs-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}.doc-card{display:block;padding:18px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-panel);color:inherit;text-decoration:none;transition:border-color .15s,transform .15s}.doc-card:hover{border-color:rgba(184,255,60,.35);transform:translateY(-1px);text-decoration:none}.doc-card .num{font:600 11px var(--mono);color:var(--accent);letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}.doc-card h3{margin:0 0 6px;font-size:17px;color:var(--fg)}.doc-card p{margin:0;color:var(--muted);font-size:14px;line-height:1.45}
.doc-body h1,.doc-body h2,.doc-body h3,.doc-body h4{line-height:1.2;letter-spacing:-.02em}.doc-body h1{font-size:36px;margin:0 0 16px}.doc-body h2{font-size:24px;margin:32px 0 12px;padding-top:8px;border-top:1px solid var(--border)}.doc-body h3{font-size:18px;margin:24px 0 8px}.doc-body p,.doc-body li{color:#d6d6d6}.doc-body p{margin:0 0 14px}.doc-body ul,.doc-body ol{margin:0 0 16px;padding-left:22px}.doc-body li+li{margin-top:6px}.doc-body code{font:13px/1.4 var(--mono);background:#0d0d0d;border:1px solid var(--border);border-radius:6px;padding:2px 6px}.doc-body pre{margin:0 0 18px;padding:16px;border:1px solid var(--border);border-radius:12px;background:#0d0d0d;overflow:auto}.doc-body pre code{display:block;padding:0;border:none;background:transparent;font:13px/1.6 var(--mono);color:#d7dde7;white-space:pre-wrap}.doc-body table{width:100%;border-collapse:collapse;margin:0 0 18px;font-size:14px}.doc-body th,.doc-body td{border:1px solid var(--border);padding:10px 12px;text-align:left}.doc-body th{background:var(--bg-panel);color:var(--fg)}.doc-body td{color:#d6d6d6}
.wrap{width:min(var(--max),calc(100% - var(--pad)*2));margin:0 auto}
@media(max-width:900px){.docs-layout{grid-template-columns:1fr}.docs-sidebar{position:static;max-height:none}.docs-grid{grid-template-columns:1fr}}
"""


DOC_SECTIONS = [
    ("Start", ["00-getting-started", "14-github-action-install", "02-setup", "04-troubleshooting"]),
    ("Framework", ["01-architecture", "05-adversarial-review", "06-risk-scalpel", "07-audit-channel-risks", "08-examples", "09-brooks-lint"]),
    ("Product", ["10-team-delivery-and-business-model", "11-byok-and-policy", "12-open-core-boundary", "13-team-edition-spec"]),
    ("Ops", ["15-ci-and-release-gate", "03-collaboration"]),
]

DOC_FEATURED = ["14-github-action-install", "00-getting-started", "12-open-core-boundary"]


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


def doc_title(stem):
    path = ROOT / "docs" / f"{stem}.md"
    if not path.is_file():
        return stem.replace("-", " ").title()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("# "):
            title = line[2:].strip()
            return re.sub(r"^\d+\.\s*", "", title)
    return stem.replace("-", " ").title()


def docs_nav_html(current=None):
    files = doc_files()
    blocks = []
    for section, stems in DOC_SECTIONS:
        items = []
        for stem in stems:
            if stem not in files:
                continue
            cls = "active" if current == f"{stem}.md" else ""
            items.append(
                f'<li><a{" class=\"active\"" if cls else ""} href="/docs/{stem}.md">{html_escape(doc_title(stem))}</a></li>'
            )
        if items:
            blocks.append(f"<section><h2>{html_escape(section)}</h2><ul>{''.join(items)}</ul></section>")
    return "".join(blocks)


def docs_shell(title, body_html, current_path=None):
    current = current_path.split("/")[-1] if current_path else None
    nav = docs_nav_html(current)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html_escape(title)} — Falsify docs</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>{DOCS_CSS}</style>
</head>
<body>
<nav class="docs-nav"><div class="wrap"><a class="brand" href="/">Falsify</a><div class="nav-links"><a href="/docs/">Docs</a><a href="/">Home</a><a href="https://github.com/shi275773124/Falsify">GitHub</a></div></div></nav>
<div class="wrap docs-layout">
<aside class="docs-sidebar">{nav}</aside>
<main class="docs-main">{body_html}</main>
</div>
</body>
</html>"""


def render_markdown(text, title="Falsify docs", current_path=None):
    body = ['<article class="doc-body">']
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
            body.append(f"<li>{inline_md(re.sub(r'^\\d+\\.\\s*', '', stripped))}</li>")
        else:
            close_list()
            body.append(f"<p>{inline_md(stripped)}</p>")

    close_list()
    if in_code and code_lines:
        body.append(f"<pre><code>{html_escape(chr(10).join(code_lines))}</code></pre>")
    body.append("</article>")
    return docs_shell(title, "".join(body), current_path)


def docs_index():
    files = doc_files()
    featured_cards = []
    for stem in DOC_FEATURED:
        if stem not in files:
            continue
        title = doc_title(stem)
        featured_cards.append(
            f'<a class="doc-card" href="/docs/{stem}.md">'
            f'<div class="num">Featured</div><h3>{html_escape(title)}</h3>'
            f'<p>Open guide</p></a>'
        )

    sections = []
    for section, stems in DOC_SECTIONS:
        cards = []
        for stem in stems:
            if stem in DOC_FEATURED or stem not in files:
                continue
            title = doc_title(stem)
            num = stem.split("-", 1)[0] if stem[:2].isdigit() else section
            cards.append(
                f'<a class="doc-card" href="/docs/{stem}.md">'
                f'<div class="num">{html_escape(num)}</div>'
                f'<h3>{html_escape(title)}</h3>'
                f'<p>{html_escape(stem.replace("-", " "))}</p></a>'
            )
        if cards:
            sections.append(
                f'<section><h2>{html_escape(section)}</h2>'
                f'<div class="docs-grid">{"".join(cards)}</div></section>'
            )

    body = f"""
<div class="docs-hero">
  <h1>Documentation</h1>
  <p>Install the PR gate, learn the framework, and ship decision artifacts your team can defend.</p>
</div>
<section><h2>Featured</h2><div class="docs-grid">{"".join(featured_cards)}</div></section>
{"".join(sections)}
"""
    return docs_shell("Documentation", body)


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Falsify — adversarial review for AI-era work</title>
<meta name="description" content="Falsify attacks false confidence, forces evidence, and cuts every risk into Must Fix, Known Debt, or Delete.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{color-scheme:dark;--bg:#090909;--bg-elevated:#111;--bg-panel:#161616;--fg:#f4f4f4;--muted:#8c8c8c;--border:#2a2a2a;--accent:#b8ff3c;--accent-fg:#0a0a0a;--pass:#3dd68c;--debt:#f0b429;--block:#ff5c5c;--radius:10px;--font:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Arial,sans-serif;--mono:"IBM Plex Mono","SFMono-Regular",Consolas,monospace;--max:1120px;--pad:clamp(20px,4vw,40px)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 var(--font)}a{color:inherit;text-decoration:none}img{max-width:100%}.wrap{width:min(var(--max),calc(100% - var(--pad)*2));margin:0 auto}
.nav{position:sticky;top:0;z-index:30;background:rgba(9,9,9,.88);backdrop-filter:blur(14px);border-bottom:1px solid var(--border)}.nav .wrap{display:flex;align-items:center;justify-content:space-between;height:64px;gap:16px}.brand{font:800 18px/1 var(--font);letter-spacing:-.02em}.links{display:flex;align-items:center;gap:20px;color:var(--muted);font-size:14px;font-weight:500}.links a:hover{color:var(--fg)}.lang-btn{background:transparent;border:1px solid var(--border);border-radius:999px;color:var(--muted);cursor:pointer;font:600 12px var(--mono);padding:6px 12px}.lang-btn:hover{border-color:var(--fg);color:var(--fg)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 18px;border-radius:999px;font:700 14px var(--font);cursor:pointer;border:1px solid transparent;transition:transform .15s,opacity .15s}.btn:hover{transform:translateY(-1px)}.btn.primary{background:var(--accent);color:var(--accent-fg)}.btn.ghost{background:transparent;border-color:var(--border);color:var(--fg)}.btn.ghost:hover{border-color:var(--fg)}
.hero{position:relative;overflow:hidden;border-bottom:1px solid var(--border)}.hero-inner{display:grid;grid-template-columns:1.1fr .9fr;min-height:min(88vh,760px)}.hero-copy{padding:clamp(88px,12vw,140px) var(--pad) 64px;max-width:640px;margin-left:max(0px,calc((100vw - var(--max))/2))}.hero-visual{position:relative;background:linear-gradient(135deg,#f4f4f4 0%,#d8d8d8 55%,#bdbdbd 100%);clip-path:polygon(18% 0,100% 0,100% 100%,0 100%)}.hero-visual-inner{position:absolute;inset:24px 24px 24px 12%;display:flex;flex-direction:column;justify-content:flex-end;gap:12px;color:#111}.preview-card{background:#fff;border:1px solid rgba(0,0,0,.08);border-radius:14px;padding:16px;box-shadow:0 24px 60px rgba(0,0,0,.12)}.preview-top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px}.preview-label{font:600 11px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:#666}.eyebrow{font:600 12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin-bottom:16px}h1{margin:0 0 20px;font-size:clamp(40px,6vw,68px);line-height:.95;letter-spacing:-.03em;font-weight:800}.sub{margin:0 0 28px;color:#c8c8c8;font-size:clamp(17px,2.2vw,20px);line-height:1.5;max-width:52ch}.hero-sub-note{font-size:14px;color:var(--muted);margin:-12px 0 28px;max-width:52ch}.actions{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:28px}.hero-meta{display:flex;flex-wrap:wrap;gap:10px}.pill{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border:1px solid var(--border);border-radius:999px;color:var(--muted);font:600 12px var(--mono)}
.badge{display:inline-block;border-radius:999px;padding:6px 10px;font:700 11px var(--mono);letter-spacing:.04em;text-transform:uppercase}.badge.PASS{background:rgba(61,214,140,.14);color:var(--pass)}.badge.PASS_WITH_DEBT{background:rgba(240,180,41,.14);color:var(--debt)}.badge.BLOCK{background:rgba(255,92,92,.14);color:var(--block)}
.quote{padding:56px 0;border-bottom:1px solid var(--border);background:var(--bg-elevated)}.quote-card{display:grid;grid-template-columns:auto 1fr;gap:20px;align-items:center;padding:24px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-panel)}.avatar{width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#333,#666);object-fit:cover;flex-shrink:0}.quote p{margin:0;color:#ddd;font-size:18px;line-height:1.55}.quote cite{display:block;margin-top:12px;color:var(--muted);font:600 13px var(--mono);font-style:normal}
.evidence{padding:40px 0;border-bottom:1px solid var(--border);background:var(--bg)}.evidence-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.evidence-card{padding:20px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-panel)}.evidence-val{font:800 28px/1 var(--font);letter-spacing:-.02em;margin-bottom:6px}.evidence-lbl{color:var(--muted);font-size:14px;line-height:1.45}
.deliverables{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:24px}.artifact{border:1px solid var(--border);border-radius:14px;background:#0d0d0d;overflow:hidden}.artifact-head{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid var(--border);font:600 12px var(--mono);color:var(--muted)}.artifact-body{padding:16px;font:12px/1.65 var(--mono);color:#c9d2de;white-space:pre-wrap}.gh-check{background:#0d1117;border-color:#30363d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji"}.gh-check-run{display:flex;gap:12px;padding:14px 16px;border-bottom:1px solid #21262d;background:#161b22}.gh-check-icon{flex:0 0 20px;width:20px;height:20px;margin-top:1px;border-radius:50%;background:#da3633;display:flex;align-items:center;justify-content:center}.gh-check-icon svg{width:12px;height:12px;fill:#fff}.gh-check-meta{min-width:0;flex:1}.gh-check-title{font:600 14px/1.3 var(--font);color:#f0f6fc}.gh-check-sub{font:12px/1.4 var(--font);color:#8b949e;margin-top:2px}.gh-check-badge{display:inline-block;margin-left:6px;padding:0 7px;border-radius:2em;font:500 12px/20px var(--font);background:rgba(248,81,73,.15);color:#ff7b72;vertical-align:baseline}.gh-comment{padding:14px 16px 16px}.gh-comment-hdr{display:flex;align-items:center;gap:8px;margin-bottom:10px;font-size:12px;color:#8b949e}.gh-bot-avatar{width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#238636,#1f6feb);flex:0 0 28px}.gh-comment-hdr strong{color:#c9d1d9;font-weight:600}.gh-md{font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;color:#c9d1d9}.gh-md h2{font-size:1.25em;font-weight:600;margin:0 0 12px;padding-bottom:.3em;border-bottom:1px solid #21262d;color:#f0f6fc}.gh-md h3{font-size:1em;font-weight:600;margin:16px 0 8px;color:#f0f6fc}.gh-md h4{font-size:.875em;font-weight:600;margin:12px 0 6px;color:#f0f6fc}.gh-md ul{margin:0;padding-left:1.5em}.gh-md li{margin:4px 0}.gh-md li ul{margin:4px 0 0;padding-left:1.25em;list-style:none}.gh-md li ul li{color:#8b949e;font-size:13px}.gh-md code{padding:.2em .4em;border-radius:6px;background:#161b22;border:1px solid #30363d;font:85% var(--mono);color:#ff7b72}
.price-limit{margin:0;padding:10px 12px;border-radius:8px;background:rgba(184,255,60,.06);border:1px solid rgba(184,255,60,.14);color:#d7f2a2;font:600 13px var(--mono)}
.s{padding:80px 0;border-bottom:1px solid var(--border)}.s.alt{background:var(--bg-elevated)}.section-head{margin-bottom:36px;max-width:720px}.tag{font:600 12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin-bottom:12px}h2{margin:0 0 12px;font-size:clamp(28px,4vw,40px);line-height:1.08;letter-spacing:-.02em}.lead{margin:0;color:var(--muted);font-size:18px;line-height:1.6}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.card{border:1px solid var(--border);background:var(--bg-panel);border-radius:var(--radius);padding:22px}.card h3{margin:8px 0 10px;font-size:18px}.card p,.card li{color:var(--muted);margin:0}.card ul{padding-left:18px;margin:8px 0 0}.card li+li{margin-top:8px}.layer-num{font:600 11px var(--mono);color:var(--accent);letter-spacing:.08em;text-transform:uppercase}
.problems{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.problem{padding:18px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:#ddd;font-weight:600}
.compare{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--border);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden}.compare div{padding:18px;background:var(--bg-panel)}.compare b{color:var(--block)}.compare strong{color:var(--accent)}
.workbench{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:stretch}.panel{border:1px solid var(--border);border-radius:14px;background:var(--bg-panel);padding:18px}.panel h3{margin:0 0 8px;font-size:16px}.panel p{margin:0 0 14px;color:var(--muted);font-size:14px}textarea{width:100%;min-height:240px;background:#0d0d0d;color:#ececec;border:1px solid var(--border);border-radius:10px;padding:14px;font:13px/1.55 var(--mono);resize:vertical}select, .row select{background:#0d0d0d;color:#ececec;border:1px solid var(--border);border-radius:10px;padding:10px 12px;font:13px var(--mono)}.row{display:flex;gap:10px;align-items:center;margin-top:12px;flex-wrap:wrap}.row .btn{margin-left:auto}.result{min-height:240px}.risk{margin-top:14px;padding:12px 0 0;border-top:1px solid var(--border)}.risk small{display:block;color:var(--muted);font:700 11px var(--mono);text-transform:uppercase;margin-bottom:6px}.risk em{display:block;margin-top:8px;color:var(--muted);font-style:normal;font-size:13px}.demo-note{margin-top:12px;padding:12px;border-radius:10px;background:rgba(184,255,60,.08);border:1px solid rgba(184,255,60,.18);color:#d7f2a2;font-size:13px}
.pricing{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.price-card{padding:24px;border:1px solid var(--border);border-radius:14px;background:var(--bg-panel);display:flex;flex-direction:column;gap:14px}.price-card.featured{border-color:rgba(184,255,60,.45);box-shadow:0 0 0 1px rgba(184,255,60,.12) inset}.price{font:800 32px/1 var(--font);letter-spacing:-.03em}.price span{font-size:14px;color:var(--muted);font-weight:600}.price-card ul{margin:0;padding-left:18px;color:var(--muted)}.price-card li+li{margin-top:8px}
.terminal{background:#0d0d0d;border:1px solid var(--border);border-radius:14px;padding:18px;font:13px/1.7 var(--mono);color:#d7dde7;overflow:auto}.terminal a{color:var(--accent)}
footer{padding:40px 0;color:var(--muted);font-size:14px}footer .wrap{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}footer a:hover{color:var(--fg)}
@media(max-width:960px){.hero-inner{grid-template-columns:1fr}.hero-visual{min-height:280px;clip-path:none}.hero-copy{margin:0 auto;max-width:none;padding-top:96px}.links a{display:none}.grid3,.problems,.pricing,.workbench,.compare,.evidence-grid,.deliverables{grid-template-columns:1fr}.row .btn{margin-left:0;width:100%}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
</style>
</head>
<body>
<nav class="nav"><div class="wrap"><a class="brand" href="#">Falsify</a><div class="links"><a href="#system" data-i18n="nav_system">System</a><a href="#demo" data-i18n="nav_demo">Demo</a><a href="#pricing" data-i18n="nav_pricing">Pricing</a><a href="/docs/" data-i18n="nav_docs">Docs</a><a href="https://github.com/shi275773124/Falsify">GitHub</a><button class="lang-btn" id="lang-btn" onclick="toggleLang()">中文</button></div></div></nav>
<div style="display:none" aria-hidden="true">
  <canvas id="cvs" role="img" aria-label="Falsify scan canvas"></canvas>
</div>
<header class="hero"><div class="hero-inner"><div class="hero-copy"><h1 data-i18n="h1">Looks right is not enough.</h1><p class="sub" data-i18n="hero_sub">Falsify turns confident AI output into a shipping decision:<br>PASS, PASS_WITH_DEBT, or BLOCK — backed by raw evidence.</p><p class="hero-sub-note" data-i18n="hero_sub_note">For PRs, deployment claims, research memos, and AI-generated decisions.</p><div class="actions"><a class="btn primary" href="/docs/14-github-action-install.md" data-i18n="btn_install">Install GitHub Action</a><a class="btn ghost" href="#deliverables" data-i18n="btn_sample_report">View real cases</a></div><div class="hero-meta"><span class="pill" data-i18n="pill_verdicts">PASS / PASS_WITH_DEBT / BLOCK</span><span class="pill" data-i18n="pill_stack">backed by raw evidence</span><span class="pill">MIT</span></div></div><div class="hero-visual" aria-hidden="true"><div class="hero-visual-inner"><div class="preview-card"><div class="preview-top"><span class="preview-label">Review output</span><span class="badge BLOCK">BLOCK</span></div><div style="font:600 14px/1.4 var(--font);margin-bottom:10px">Deployment succeeded because logs completed.</div><div style="font:12px/1.5 var(--mono);color:#555"><div><strong style="color:#c0392b">Must Fix</strong> — Logs are not state verification.</div><div style="margin-top:8px"><strong style="color:#b07d00">Known Debt</strong> — No rollback artifact attached.</div></div></div></div></div></div></header>
<section class="quote"><div class="wrap"><div class="quote-card"><img class="avatar" src="/assets/chris-shi-founder.png" alt="史可鉴 / Chris Shi" width="48" height="48"><div><p data-i18n="quote_p">"We stopped shipping 'green logs' as proof. Falsify turned review from vibes into a decision artifact the team can actually defend."</p><cite data-i18n="quote_cite">Chris Shi</cite></div></div></div></section>
<section class="evidence"><div class="wrap"><div class="evidence-grid"><div class="evidence-card"><div class="evidence-val" data-i18n="ev1_val">&lt; 1 day</div><div class="evidence-lbl" data-i18n="ev1_lbl">Time to first useful BLOCK</div></div><div class="evidence-card"><div class="evidence-val" data-i18n="ev2_val">3 verdicts</div><div class="evidence-lbl" data-i18n="ev2_lbl">PASS / PASS_WITH_DEBT / BLOCK only</div></div><div class="evidence-card"><div class="evidence-val" data-i18n="ev3_val">100%</div><div class="evidence-lbl" data-i18n="ev3_lbl">Known Debt requires upgrade trigger (strict mode)</div></div></div></div></section>
<section class="s"><div class="wrap"><div class="section-head"><div class="tag" data-i18n="problem_tag">Problem</div><h2 data-i18n="problem_h2">Confidence got cheap.</h2><p class="lead" data-i18n="problem_lead">AI made teams faster. It also made polished wrongness easier to ship.</p></div><div class="problems"><div class="problem" data-i18n="p1">Green logs that do not prove state</div><div class="problem" data-i18n="p2">Second-model agreement treated as proof</div><div class="problem" data-i18n="p3">Safety checks that live only in prompts</div></div></div></section>
<section class="s alt" id="system"><div class="wrap"><div class="section-head"><div class="tag" data-i18n="system_tag">System</div><h2 data-i18n="system_h2">Three layers. One decision.</h2><p class="lead" data-i18n="system_lead">Frame Audit, Adversarial Review, and Cutline — built for teams that cannot afford fake PASS.</p></div><div class="grid3"><div class="card"><div class="layer-num" data-i18n="bl_label">Layer 01</div><h3 data-i18n="bl_h3">Frame Audit</h3><ul><li data-i18n="bl_1">hidden state / implicit authority</li><li data-i18n="bl_2">owner / lock / lifecycle</li><li data-i18n="bl_4">rollback / verification path</li></ul></div><div class="card"><div class="layer-num" data-i18n="ar_label">Layer 02</div><h3 data-i18n="ar_h3">Adversarial Review</h3><ul><li data-i18n="ar_1">false truth / false risk</li><li data-i18n="ar_5">prompt-only audit theater</li><li data-i18n="ar_6">monitor-failure laundering</li></ul></div><div class="card"><div class="layer-num" data-i18n="rs_label">Layer 03</div><h3 data-i18n="rs_h3">Cutline</h3><ul><li data-i18n="rs_1">Must Fix</li><li data-i18n="rs_2">Known Debt</li><li data-i18n="rs_3">Delete</li></ul></div></div></div></section>
<section class="s"><div class="wrap"><div class="section-head"><div class="tag" data-i18n="compare_tag">Fake proof</div><h2 data-i18n="compare_h2">Fake proof is not proof.</h2></div><div class="compare"><div><b data-i18n="cmp_l1">"The model said it is fine."</b></div><div><strong data-i18n="cmp_r1">Where is the raw artifact.</strong></div><div><b data-i18n="cmp_l2">"Another AI reviewed it."</b></div><div><strong data-i18n="cmp_r2">Did it check the failure mode, or just agree.</strong></div><div><b data-i18n="cmp_l3">"The logs look successful."</b></div><div><strong data-i18n="cmp_r3">Did the actual state change.</strong></div></div></div></section>
<section class="s alt" id="deliverables"><div class="wrap"><div class="section-head"><div class="tag" data-i18n="deliver_tag">Deliverables</div><h2 data-i18n="deliver_h2">What you actually ship.</h2><p class="lead" data-i18n="deliver_lead">Not another chat reply — a PR check, a JSON report, and a markdown summary your team can defend.</p></div><div class="deliverables"><div class="artifact"><div class="artifact-head"><span>falsify-report.json</span><span class="badge BLOCK">BLOCK</span></div><div class="artifact-body">{
  "schema_version": "falsify.review.v1",
  "verdict": "BLOCK",
  "findings": [{
    "cutline": "Must Fix",
    "issue": "Logs are treated as state verification",
    "minimal_action": "Add read-after-write probe"
  }]
}</div></div><div class="artifact gh-check"><div class="artifact-head"><span data-i18n="deliver_pr_label">Pull request check</span><span class="gh-check-badge" data-i18n="deliver_pr_check_failed">Failed</span></div><div class="gh-check-run"><div class="gh-check-icon" aria-hidden="true"><svg viewBox="0 0 16 16"><path d="M3.72 3.72a.75.75 0 0 1 1.06 0L8 6.94l3.22-3.22a.749.749 0 0 1 1.275.326.749.749 0 0 1-.215.734L9.06 8l3.22 3.22a.749.749 0 0 1-.326 1.275.749.749 0 0 1-.734-.215L8 9.06l-3.22 3.22a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042L6.94 8 3.72 4.78a.75.75 0 0 1 0-1.06Z"/></svg></div><div class="gh-check-meta"><div class="gh-check-title"><span data-i18n="deliver_pr_check_name">falsify-pr-review</span></div><div class="gh-check-sub"><span data-i18n="deliver_pr_check_sub">falsify / test-suite</span> · pull_request</div></div></div><div class="gh-comment"><div class="gh-comment-hdr"><span class="gh-bot-avatar" aria-hidden="true"></span><strong data-i18n="deliver_pr_bot">github-actions[bot]</strong><span data-i18n="deliver_pr_commented">commented</span></div><div class="gh-md"><h2 data-i18n="deliver_pr_verdict">Falsify Verdict: BLOCK</h2><h3><code data-i18n="deliver_pr_filepath">reports/deploy.md</code></h3><ul><li data-i18n="deliver_pr_lint">lint: ✅</li><li><span data-i18n="deliver_pr_review">review:</span> <code>BLOCK</code></li></ul><h4 data-i18n="deliver_pr_must_fix">Must Fix</h4><ul><li><span data-i18n="deliver_pr_issue">Logs are treated as state verification</span><ul><li data-i18n="deliver_pr_action">Minimal action: Add read-after-write probe</li></ul></li></ul><h4 data-i18n="deliver_pr_final_h">Final</h4><p data-i18n="deliver_pr_final">Merge blocked until Must Fix items are resolved.</p></div></div></div></div></div></section>
<section class="s" id="demo"><div class="wrap"><div class="section-head"><div class="tag" data-i18n="try_tag">Workbench</div><h2 data-i18n="try_h2">See a verdict in seconds.</h2><p class="lead" data-i18n="try_lead">Run a free sample instantly. Live review uses your configured API key — not billed through this public demo.</p></div><div class="workbench"><div class="panel"><h3 data-i18n="input_h3">Claim</h3><p data-i18n="input_p">Paste a deployment claim, PR summary, or AI-generated report.</p><textarea id="t">Deployment succeeded because the logs completed. Another AI reviewed it and found no issue. No raw verdict, parse status, finish_reason, or usage counts were kept.</textarea><div class="row"><select id="s"><option value="general" data-i18n="scenario_general">General</option><option value="code" data-i18n="scenario_code">Code / PR</option><option value="research" data-i18n="scenario_research">Research</option><option value="production" selected data-i18n="scenario_production">Production</option></select><button class="btn ghost" onclick="runSample()" data-i18n="btn_sample">Run sample</button><button class="btn primary" id="b" onclick="go()" data-i18n="btn_review">Live review</button></div><div class="demo-note" data-i18n="demo_note">Samples are canned and cost zero tokens. Live review only works when you configure a provider key locally.</div></div><div class="panel result" id="out"><h3 data-i18n="output_h3">Verdict</h3><p data-i18n="output_p">Hit Run sample to preview the decision artifact.</p></div></div></div></section>
<section class="s" id="pricing"><div class="wrap"><div class="section-head"><div class="tag" data-i18n="pricing_tag">Pricing</div><h2 data-i18n="pricing_h2">Start free. Scale with your team.</h2><p class="lead" data-i18n="pricing_lead">Tool-first delivery: local CLI for builders, team workflows for leads, audit coaching for high-stakes launches.</p></div><div class="pricing"><div class="price-card"><div class="tag">Free</div><div class="price">$0</div><p class="price-limit" data-i18n="price_free_limit">1 repo · BYOK · OSS CLI + Action template</p><ul><li data-i18n="price_free_1">CLI + MIT core</li><li data-i18n="price_free_2">Local review with your API key</li><li data-i18n="price_free_3">Sample templates</li></ul><a class="btn ghost" href="/docs/14-github-action-install.md" data-i18n="btn_install">Install in 5 min</a></div><div class="price-card featured"><div class="tag">Team</div><div class="price">$99<span>/mo</span></div><p class="price-limit" data-i18n="price_team_limit">Up to 10 repos · shared policy · 90-day report retention</p><ul><li data-i18n="price_team_1">Shared review templates</li><li data-i18n="price_team_2">Exportable decision reports</li><li data-i18n="price_team_3">Team rule packs</li></ul><a class="btn primary" href="mailto:chrisshi168@icloud.com" data-i18n="btn_waitlist">Join waitlist</a></div><div class="price-card"><div class="tag">Enterprise</div><div class="price" data-i18n="price_ent_label">Custom</div><p class="price-limit" data-i18n="price_ent_limit">SSO/RBAC · private deploy · SLA + audit coaching</p><ul><li data-i18n="price_ent_1">Private deploy</li><li data-i18n="price_ent_2">Workflow integration</li><li data-i18n="price_ent_3">Audit coaching</li></ul><a class="btn ghost" href="mailto:chrisshi168@icloud.com" data-i18n="btn_audit">Book audit</a></div></div></div></section>
<section class="s alt" id="start"><div class="wrap"><div class="section-head"><div class="tag" data-i18n="start_tag">Start</div><h2 data-i18n="start_h2">Run it locally in 60 seconds.</h2></div><div class="terminal">git clone https://github.com/shi275773124/Falsify.git
cd Falsify
python falsify.py demo
export FALSIFY_PROVIDER=deepseek
export DEEPSEEK_API_KEY=sk-...
python falsify.py review report.md
python web/serve.py
<a href="/docs/14-github-action-install.md" data-i18n="docs_install">Install GitHub Action (5 min) →</a></div></div></section>
<section class="s"><div class="wrap"><div class="section-head"><div class="tag" data-i18n="boundary_tag">Boundary</div><h2 data-i18n="boundary_h2">Falsify classifies risk. It does not authorize action.</h2><p class="lead" data-i18n="boundary_p">Live money, production config, cron, gateway, and external send still require independent final judgment. Self-review is not independent review.</p></div></div></section>
<footer><div class="wrap"><div>Falsify</div><div><a href="https://github.com/shi275773124/Falsify">GitHub</a> · <a href="https://x.com/aishikejian">X</a> · <a href="mailto:chrisshi168@icloud.com">Email</a> · <a href="https://github.com/shi275773124/Falsify/blob/main/LICENSE">License</a></div></div></footer>
<script>
const PUBLIC_COPY=[
  "Review first. Trust after.",
  "Falsify does not argue. It asks one question: where is the evidence.",
  "先审，再信。",
  "Falsify 不争。只问一件事：证据在哪。",
  "Frame Audit + Adversarial Review + Cutline.",
  "框架审 + 对抗审 + Cutline。",
  "audit the audit channel itself",
  "审计通道本身也要被审计",
  "human-auditability break",
  "duplicated authority sources",
  "naming / status semantics that mislead",
  "命名与状态语义误导",
  "Semantic verdict nudge",
  "Prompt-only audit theater",
  "Monitor-failure laundering",
  "Final",
  "Real backend, not fake analysis."
  ,"NODE_DESKTOP=168",
  "SCAN_PERIOD=7200"
];
const SAMPLES={general:{verdict:"BLOCK",risks:[{cutline:"Must Fix",issue:"Claim reads confident but cites no raw artifact.",minimal_action:"Attach source output, command log, or reproducible check."},{cutline:"Known Debt",issue:"Secondary review mentioned but not independently verified.",minimal_action:"Re-run with explicit failure-mode checklist.",upgrade_trigger:"Before any customer-facing decision."}]},code:{verdict:"PASS_WITH_DEBT",risks:[{cutline:"Known Debt",issue:"Tests pass but do not assert the risky default path.",minimal_action:"Add one negative test for the default branch.",upgrade_trigger:"Before merge to main."}]},research:{verdict:"BLOCK",risks:[{cutline:"Must Fix",issue:"Conclusion cites summary tables without primary source excerpt.",minimal_action:"Attach table screenshot or raw CSV hash."}]},production:{verdict:"BLOCK",risks:[{cutline:"Must Fix",issue:"Logs completed, but no read-after-write or invariant check proves intended state.",minimal_action:"Attach post-deploy probe output and rollback command."},{cutline:"Delete",issue:"Another AI reviewed it — not evidence.",minimal_action:"Remove from acceptance chain."}]}};
const T={en:{"nav_system":"System","nav_demo":"Demo","nav_pricing":"Pricing","nav_docs":"Docs","h1":"Looks right is not enough.","hero_sub":"Falsify turns confident AI output into a shipping decision:\nPASS, PASS_WITH_DEBT, or BLOCK — backed by raw evidence.","hero_sub_note":"For PRs, deployment claims, research memos, and AI-generated decisions.","btn_install":"Install GitHub Action","btn_sample_report":"View real cases","btn_demo":"Try demo","btn_audit":"Book audit","pill_verdicts":"PASS / PASS_WITH_DEBT / BLOCK","pill_stack":"backed by raw evidence","quote_p":"\"We stopped shipping 'green logs' as proof. Falsify turned review from vibes into a decision artifact the team can actually defend.\"","quote_cite":"Chris Shi","ev1_val":"< 1 day","ev1_lbl":"Time to first useful BLOCK","ev2_val":"3 verdicts","ev2_lbl":"PASS / PASS_WITH_DEBT / BLOCK only","ev3_val":"100%","ev3_lbl":"Known Debt requires upgrade trigger (strict mode)","deliver_tag":"Deliverables","deliver_h2":"What you actually ship.","deliver_lead":"Not another chat reply — a PR check, a JSON report, and a markdown summary your team can defend.","deliver_pr_label":"Pull request check","deliver_pr_check_failed":"Failed","deliver_pr_check_name":"falsify-pr-review","deliver_pr_check_sub":"falsify / test-suite","deliver_pr_bot":"github-actions[bot]","deliver_pr_commented":"commented","deliver_pr_verdict":"Falsify Verdict: BLOCK","deliver_pr_filepath":"reports/deploy.md","deliver_pr_lint":"lint: ✅","deliver_pr_review":"review:","deliver_pr_must_fix":"Must Fix","deliver_pr_issue":"Logs are treated as state verification","deliver_pr_action":"Minimal action: Add read-after-write probe","deliver_pr_final_h":"Final","deliver_pr_final":"Merge blocked until Must Fix items are resolved.","problem_tag":"Problem","problem_h2":"Confidence got cheap.","problem_lead":"AI made teams faster. It also made polished wrongness easier to ship.","p1":"Green logs that do not prove state","p2":"Second-model agreement treated as proof","p3":"Safety checks that live only in prompts","system_tag":"System","system_h2":"Three layers. One decision.","system_lead":"Frame Audit, Adversarial Review, and Cutline — built for teams that cannot afford fake PASS.","bl_label":"Layer 01","ar_label":"Layer 02","rs_label":"Layer 03","bl_h3":"Frame Audit","ar_h3":"Adversarial Review","rs_h3":"Cutline","bl_1":"hidden state / implicit authority","bl_2":"owner / lock / lifecycle","bl_4":"rollback / verification path","ar_1":"false truth / false risk","ar_5":"prompt-only audit theater","ar_6":"monitor-failure laundering","rs_1":"Must Fix","rs_2":"Known Debt","rs_3":"Delete","compare_tag":"Fake proof","compare_h2":"Fake proof is not proof.","cmp_l1":"\"The model said it is fine.\"","cmp_r1":"Where is the raw artifact.","cmp_l2":"\"Another AI reviewed it.\"","cmp_r2":"Did it check the failure mode, or just agree.","cmp_l3":"\"The logs look successful.\"","cmp_r3":"Did the actual state change.","try_tag":"Workbench","try_h2":"See a verdict in seconds.","try_lead":"Run a free sample instantly. Live review uses your configured API key — not billed through this public demo.","input_h3":"Claim","input_p":"Paste a deployment claim, PR summary, or AI-generated report.","output_h3":"Verdict","output_p":"Hit Run sample to preview the decision artifact.","demo_note":"Samples are canned and cost zero tokens. Live review only works when you configure a provider key locally.","scenario_general":"General","scenario_code":"Code / PR","scenario_research":"Research","scenario_production":"Production","btn_sample":"Run sample","btn_review":"Live review","pricing_tag":"Pricing","pricing_h2":"Start free. Scale with your team.","pricing_lead":"Tool-first delivery: local CLI for builders, team workflows for leads, audit coaching for high-stakes launches.","price_free_limit":"1 repo · BYOK · OSS CLI + Action template","price_free_1":"CLI + MIT core","price_free_2":"Local review with your API key","price_free_3":"Sample templates","price_team_limit":"Up to 10 repos · shared policy · 90-day report retention","price_team_1":"Shared review templates","price_team_2":"Exportable decision reports","price_team_3":"Team rule packs","btn_waitlist":"Join waitlist","price_ent_label":"Custom","price_ent_limit":"SSO/RBAC · private deploy · SLA + audit coaching","price_ent_1":"Private deploy","price_ent_2":"Workflow integration","price_ent_3":"Audit coaching","start_tag":"Start","start_h2":"Run it locally in 60 seconds.","docs_install":"Install GitHub Action (5 min) →","boundary_tag":"Boundary","boundary_h2":"Falsify classifies risk. It does not authorize action.","boundary_p":"Live money, production config, cron, gateway, and external send still require independent final judgment. Self-review is not independent review.","btn_github":"GitHub"},
zh:{"nav_system":"系统","nav_demo":"演示","nav_pricing":"定价","nav_docs":"文档","h1":"看起来对，不够。","hero_sub":"Falsify 把自信的 AI 输出变成上线决策：\nPASS、PASS_WITH_DEBT、BLOCK — 以原始证据为底。","hero_sub_note":"覆盖 PR、部署声明、研究备忘录、AI 生成决策。","btn_install":"安装 GitHub Action","btn_sample_report":"查看真实案例","btn_demo":"试用演示","btn_audit":"预约审计","pill_verdicts":"PASS / PASS_WITH_DEBT / BLOCK","pill_stack":"以原始证据为底","quote_p":"「我们不再把『日志绿了』当证明。Falsify 把审查从『感觉』变成了团队能站得住的决策产物。」","quote_cite":"史可鉴","ev1_val":"< 1 天","ev1_lbl":"首次有效 BLOCK 耗时","ev2_val":"3 种裁决","ev2_lbl":"仅 PASS / PASS_WITH_DEBT / BLOCK","ev3_val":"100%","ev3_lbl":"Known Debt 必须带升级触发（严格模式）","deliver_tag":"交付物","deliver_h2":"你真正交付的是什么","deliver_lead":"不是又一条聊天回复 — 而是 PR Check、JSON 报告、可辩护的 Markdown 摘要。","deliver_pr_label":"PR 检查","deliver_pr_check_failed":"失败","deliver_pr_check_name":"falsify-pr-review","deliver_pr_check_sub":"falsify / test-suite","deliver_pr_bot":"github-actions[bot]","deliver_pr_commented":"评论于","deliver_pr_verdict":"Falsify Verdict: BLOCK","deliver_pr_filepath":"reports/deploy.md","deliver_pr_lint":"lint: ✅","deliver_pr_review":"review:","deliver_pr_must_fix":"Must Fix","deliver_pr_issue":"日志被当作状态验证","deliver_pr_action":"Minimal action: 添加 read-after-write 探针","deliver_pr_final_h":"Final","deliver_pr_final":"存在 Must Fix 项，合并已阻断。","problem_tag":"问题","problem_h2":"自信变便宜了。","problem_lead":"AI 让交付变快，也让漂亮的错误更容易上线。","p1":"日志绿了，不代表状态对了","p2":"第二个模型点头，不代表证据成立","p3":"安全检查只写在提示词里","system_tag":"系统","system_h2":"三层结构，一个决策。","system_lead":"框架审、对抗审、Cutline — 给不能承受假 PASS 的团队。","bl_label":"第一层","ar_label":"第二层","rs_label":"第三层","bl_h3":"框架审","ar_h3":"对抗审","rs_h3":"Cutline","bl_1":"隐藏状态与隐式权威","bl_2":"归属、锁与生命周期","bl_4":"回滚与验证路径","ar_1":"虚假事实与虚假风险","ar_5":"提示词作秀","ar_6":"监控洗白","rs_1":"Must Fix","rs_2":"Known Debt","rs_3":"Delete","compare_tag":"假证明","compare_h2":"假证明不是证明。","cmp_l1":"\"模型说没问题。\"","cmp_r1":"原始输出在哪。","cmp_l2":"\"另一个 AI 审过了。\"","cmp_r2":"它查了失败模式，还是只是附和。","cmp_l3":"\"日志看起来成功。\"","cmp_r3":"实际状态变了吗。","try_tag":"工作台","try_h2":"几秒内看到裁决。","try_lead":"样例即时免费。真审查走你本地配置的 API key — 公网 demo 不替你付 token。","input_h3":"断言","input_p":"粘贴部署声明、PR 摘要或 AI 生成报告。","output_h3":"裁决","output_p":"点「运行样例」预览决策产物。","demo_note":"样例是固定的，零 token。真审查需本地配置 provider key。","scenario_general":"通用","scenario_code":"代码 / PR","scenario_research":"研究","scenario_production":"生产","btn_sample":"运行样例","btn_review":"真审查","pricing_tag":"定价","pricing_h2":"免费起步，随团队扩展。","pricing_lead":"工具先行：开发者用 CLI，负责人用团队流，关键上线用审计陪跑。","price_free_limit":"1 仓库 · BYOK · OSS CLI + Action 模板","price_free_1":"CLI + MIT 核心","price_free_2":"本地审查，自带 API key","price_free_3":"样例模板","price_team_limit":"最多 10 仓库 · 共享 policy · 90 天报告留存","price_team_1":"共享审查模板","price_team_2":"可导出决策报告","price_team_3":"团队规则包","btn_waitlist":"加入候补","price_ent_label":"定制","price_ent_limit":"SSO/RBAC · 私有化部署 · SLA + 审计陪跑","price_ent_1":"私有化部署","price_ent_2":"流程集成","price_ent_3":"审计陪跑","start_tag":"开始","start_h2":"60 秒本地跑起来。","docs_install":"5 分钟安装 GitHub Action →","boundary_tag":"边界","boundary_h2":"Falsify 只做风险分类，不做执行授权。","boundary_p":"真实资金、生产配置、cron、网关与外部发送仍需独立终审。自己审自己不算独立判断。","btn_github":"GitHub"}};
let lang='en';
function applyLang(){document.documentElement.lang=lang==='zh'?'zh-CN':'en';document.getElementById('lang-btn').textContent=lang==='en'?'中文':'EN';document.querySelectorAll('[data-i18n]').forEach(el=>{const k=el.getAttribute('data-i18n');if(T[lang][k]===undefined)return;const v=T[lang][k];if(k==='hero_sub')el.innerHTML=v.replace(/\n/g,'<br>');else el.textContent=v;});}
function toggleLang(){lang=lang==='en'?'zh':'en';applyLang();}
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
function renderVerdict(d){let h='<span class="badge '+d.verdict+'">'+d.verdict+'</span>';for(const x of d.risks||[]){h+='<div class="risk"><small>'+esc(x.cutline||x.severity||'Finding')+'</small>'+esc(x.issue||'')+'<br><em>'+esc(x.minimal_action||'')+'</em></div>'}return h}
function runSample(){const sc=document.getElementById('s').value;document.getElementById('out').innerHTML='<h3>'+(lang==='zh'?'裁决':'Verdict')+'</h3>'+renderVerdict(SAMPLES[sc]||SAMPLES.production)}
async function go(){const t=document.getElementById('t').value.trim(),out=document.getElementById('out'),b=document.getElementById('b');if(!t){out.innerHTML='<p>Paste something first.</p>';return}b.disabled=true;out.innerHTML='<p>Reviewing...</p>';try{const r=await fetch('/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:t,scenario:document.getElementById('s').value})});const d=await r.json();if(d.error){out.innerHTML='<h3>'+(lang==='zh'?'裁决':'Verdict')+'</h3><p>'+esc(d.error)+'</p><p><button class="btn ghost" onclick="runSample()">'+(lang==='zh'?'改用样例':'Use sample instead')+'</button></p>';b.disabled=false;return}if(d.raw){out.innerHTML='<span class="badge '+d.verdict+'">'+d.verdict+'</span><pre>'+esc(d.raw)+'</pre>';b.disabled=false;return}out.innerHTML='<h3>'+(lang==='zh'?'裁决':'Verdict')+'</h3>'+renderVerdict(d)}catch(e){out.innerHTML='<p>'+esc(String(e))+'</p>'}b.disabled=false}
applyLang();
</script>
</body>
</html>"""

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def serve_static(self):
        parsed = urlparse(self.path)
        if parsed.path == "/docs/":
            return self._send(200, docs_index(), "text/html")
        target = safe_repo_path(self.path)
        if not target or not target.is_file():
            return self._send(404, json.dumps({"error": "not found"}))
        suffix = target.suffix.lower()
        if suffix == ".md":
            title = doc_title(target.stem)
            html = render_markdown(
                target.read_text(encoding="utf-8"),
                title,
                current_path=parsed.path,
            )
            return self._send(200, html, "text/html")
        ctype = {".svg": "image/svg+xml", ".png": "image/png", ".gif": "image/gif", ".css": "text/css"}[suffix]
        return self._send(200, target.read_bytes(), ctype)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._send(200, PAGE, "text/html")
        elif parsed.path.startswith("/docs/") or parsed.path.startswith("/assets/"):
            self.serve_static()
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        if urlparse(self.path).path != "/review":
            return self._send(404, json.dumps({"error": "not found"}))
        try:
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(n) or b"{}")
            text = (req.get("text") or "").strip()
            if not text:
                return self._send(400, json.dumps({"error": "empty text"}))
            result = review(text, req.get("scenario", "general"))
            self._send(200, json.dumps(result))
        except falsify.FalsifyError as e:
            self._send(200, json.dumps({"error": str(e)}))
        except Exception as e:  # noqa: BLE001
            self._send(200, json.dumps({"error": f"server error: {e}"}))

    def log_message(self, *a):
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
