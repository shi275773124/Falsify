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
ALLOWED_STATIC_EXTS = {".md", ".svg", ".png", ".gif", ".css", ".json"}
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
            active_attr = ' class="active"' if cls else ""
            items.append(
                f'<li><a{active_attr} href="/docs/{stem}.md">{html_escape(doc_title(stem))}</a></li>'
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
            list_text = re.sub(r"^\d+\.\s*", "", stripped)
            body.append(f"<li>{inline_md(list_text)}</li>")
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
:root{color-scheme:dark;--bg:#090909;--bg-elevated:#111;--bg-panel:#161616;--fg:#f4f4f4;--body:#d6d6d6;--muted:#8c8c8c;--border:#2a2a2a;--accent:#b8ff3c;--accent-fg:#0a0a0a;--pass:#3dd68c;--debt:#f0b429;--block:#ff5c5c;--radius:10px;--font:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Arial,sans-serif;--mono:"IBM Plex Mono","SFMono-Regular",Consolas,monospace;--max:1120px;--pad:clamp(20px,4vw,40px)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--body);font:16px/1.6 var(--font)}a{color:inherit;text-decoration:none}img{max-width:100%}.wrap{width:min(var(--max),calc(100% - var(--pad)*2));margin:0 auto}
.nav{position:sticky;top:0;z-index:30;background:rgba(9,9,9,.88);backdrop-filter:blur(14px);border-bottom:1px solid var(--border)}.nav .wrap{display:flex;align-items:center;justify-content:space-between;height:64px;gap:16px}.brand{font:800 18px/1 var(--font);letter-spacing:-.02em;color:var(--fg)}.links{display:flex;align-items:center;gap:20px;color:var(--muted);font-size:14px;font-weight:500}.links a:hover{color:var(--fg)}.links a.nav-mobile{display:none}.lang-btn{background:transparent;border:1px solid var(--border);border-radius:999px;color:var(--muted);cursor:pointer;font:600 12px var(--mono);padding:6px 12px}.lang-btn:hover{border-color:var(--fg);color:var(--fg)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 20px;border-radius:999px;font:700 14px var(--font);cursor:pointer;border:1px solid transparent;transition:transform .15s,opacity .15s,border-color .15s,color .15s}.btn:hover{transform:translateY(-1px)}.btn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}.btn.primary{background:var(--accent);color:var(--accent-fg)}.btn.ghost{background:transparent;border-color:var(--border);color:var(--muted)}.btn.ghost:hover{border-color:#3a3a3a;color:var(--body)}
.hero{position:relative;overflow:hidden;border-bottom:1px solid var(--border)}.hero-inner{display:grid;grid-template-columns:1.1fr .9fr;min-height:min(88vh,760px)}.hero-copy{padding:clamp(88px,12vw,140px) var(--pad) 64px;max-width:640px;margin-left:max(0px,calc((100vw - var(--max))/2))}.hero-visual{position:relative;background:var(--bg-panel);border-left:1px solid var(--border);clip-path:polygon(18% 0,100% 0,100% 100%,0 100%)}.hero-visual-inner{position:absolute;inset:32px 32px 32px 14%;display:flex;flex-direction:column;justify-content:center;align-items:center}.pipeline{display:flex;flex-direction:column;gap:0;width:100%;max-width:260px}.pipeline-step{padding:12px 16px;border:1px solid var(--border);border-radius:10px;background:var(--bg-elevated);font:600 12px var(--mono);letter-spacing:.04em;color:var(--fg);text-align:center}.pipeline-arrow{text-align:center;color:var(--muted);font:500 11px var(--mono);padding:3px 0;line-height:1}.pipeline-end{display:flex;align-items:center;justify-content:center;gap:10px;padding:8px 0 0}.pipeline-end .pipeline-step{flex:1;border-color:rgba(255,92,92,.3);background:rgba(255,92,92,.06)}.hero-chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px}.hero-chip{display:inline-flex;align-items:center;padding:5px 11px;border:1px solid rgba(184,255,60,.2);border-radius:999px;color:var(--muted);font:600 11px var(--mono);letter-spacing:.04em;background:rgba(184,255,60,.04)}.hero-chip::before{content:"";width:4px;height:4px;border-radius:50%;background:var(--accent);margin-right:7px;opacity:.75;flex-shrink:0}.eyebrow{font:600 12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin-bottom:16px}h1{margin:0 0 16px;font-size:clamp(40px,6vw,68px);line-height:.95;letter-spacing:-.03em;font-weight:800;color:var(--fg)}.sub{margin:0 0 28px;color:var(--body);font-size:clamp(17px,2.2vw,20px);line-height:1.5;max-width:52ch}.hero-sub-note{font-size:13px;color:var(--muted);margin:-12px 0 28px;max-width:52ch}.actions{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:28px}.hero-meta{display:flex;flex-wrap:wrap;gap:10px}.pill{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border:1px solid var(--border);border-radius:999px;color:var(--muted);font:600 13px var(--mono)}
.badge{display:inline-block;border-radius:999px;padding:6px 10px;font:700 11px var(--mono);letter-spacing:.04em;text-transform:uppercase}.badge.PASS{background:rgba(61,214,140,.14);color:var(--pass)}.badge.PASS_WITH_DEBT{background:rgba(240,180,41,.14);color:var(--debt)}.badge.BLOCK{background:rgba(255,92,92,.14);color:var(--block)}
.quote{padding:72px 0;border-bottom:1px solid var(--border);background:var(--bg-elevated)}.quote-card{display:grid;grid-template-columns:auto 1fr;gap:20px;align-items:center;padding:24px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-panel)}.avatar{width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#333,#666);object-fit:cover;flex-shrink:0;align-self:center}.quote p{margin:0;color:var(--body);font-size:18px;line-height:1.55}.quote cite{display:block;margin-top:12px;color:var(--muted);font:600 13px var(--mono);font-style:normal}
.hero-layers{padding:56px 0;border-bottom:1px solid var(--border);background:var(--bg)}.hero-layers-hook{margin:0 0 10px;font-size:clamp(22px,3vw,28px);line-height:1.25;color:var(--fg);font-weight:700;letter-spacing:-.02em}.hero-layers-intro{margin:0 0 28px;color:var(--muted);font-size:18px;line-height:1.55;max-width:52ch}.hero-layers-grid{display:grid;gap:14px;margin-bottom:28px;max-width:720px}.hero-layer{display:grid;grid-template-columns:auto 1fr;gap:12px 16px;align-items:baseline;padding:14px 16px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-panel)}.hero-layer-tag{font:600 11px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--accent);white-space:nowrap}.hero-layer-map{display:block;margin-top:2px;font:500 10px var(--mono);letter-spacing:.04em;color:var(--muted);opacity:.75;text-transform:none}.hero-layer-body{margin:0;color:var(--body);font-size:15px;line-height:1.55}.hero-layers-close{margin:0 0 12px;color:var(--muted);font-size:16px;line-height:1.5}.hero-layers-verdicts{margin:0;font:700 14px var(--mono);color:var(--fg);letter-spacing:.02em}
.evidence{display:none}.sample-artifact{max-width:640px}.sample-artifact .artifact{margin-bottom:16px}.sample-actions{display:flex;flex-wrap:wrap;gap:12px;align-items:center}.artifact{border:1px solid var(--border);border-radius:14px;background:#0d0d0d;overflow:hidden}.artifact-head{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid var(--border);font:600 13px var(--mono);color:var(--muted)}.artifact-body{padding:16px;font:13px/1.65 var(--mono);color:#c9d2de;white-space:pre-wrap}
.open-core-block{padding:24px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-panel);max-width:640px}.open-core-block p{margin:0 0 10px;color:var(--body);font-size:15px;line-height:1.55}.open-core-block p:last-of-type{margin-bottom:14px}.footer-oc{margin:0 0 6px;color:var(--muted);font-size:13px;line-height:1.5}.footer-trust{margin:0;color:var(--muted);font:600 11px var(--mono);opacity:.75}
.s{padding:72px 0;border-bottom:1px solid var(--border)}.s.alt{background:var(--bg-elevated)}.section-head{margin-bottom:40px;max-width:720px}.section-head .tag{margin-bottom:10px}.section-head h2{margin:0 0 14px}.tag{font:600 12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin-bottom:12px}h2{margin:0 0 12px;font-size:clamp(28px,4vw,40px);line-height:1.08;letter-spacing:-.02em;color:var(--fg)}.lead{margin:0;color:var(--muted);font-size:18px;line-height:1.6}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.card{border:1px solid var(--border);background:var(--bg-panel);border-radius:var(--radius);padding:22px}.card h3{margin:8px 0 10px;font-size:18px;color:var(--fg)}.card p,.card li{color:var(--muted);margin:0}.card ul{padding-left:18px;margin:8px 0 0}.card li+li{margin-top:8px}.layer-num{font:600 12px var(--mono);color:var(--accent);letter-spacing:.08em;text-transform:uppercase}
.problems{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.problem{padding:18px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--body);font-weight:600;font-size:14px}
.compare{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--border);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden}.compare div{padding:18px;background:var(--bg-panel)}.compare b{color:var(--block)}.compare strong{color:var(--accent)}
.workbench{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:stretch}.panel{border:1px solid var(--border);border-radius:14px;background:var(--bg-panel);padding:18px}.panel h3{margin:0 0 8px;font-size:16px}.panel p{margin:0 0 14px;color:var(--muted);font-size:14px}textarea{width:100%;min-height:240px;background:#0d0d0d;color:#ececec;border:1px solid var(--border);border-radius:10px;padding:14px;font:13px/1.55 var(--mono);resize:vertical}select, .row select{background:#0d0d0d;color:#ececec;border:1px solid var(--border);border-radius:10px;padding:10px 12px;font:13px var(--mono)}.row{display:flex;gap:10px;align-items:center;margin-top:12px;flex-wrap:wrap}.row .btn{margin-left:auto}.result{min-height:240px}.risk{margin-top:14px;padding:12px 0 0;border-top:1px solid var(--border)}.risk small{display:block;color:var(--muted);font:700 11px var(--mono);text-transform:uppercase;margin-bottom:6px}.risk em{display:block;margin-top:8px;color:var(--muted);font-style:normal;font-size:13px}.demo-note{margin-top:12px;padding:12px;border-radius:10px;background:rgba(184,255,60,.08);border:1px solid rgba(184,255,60,.18);color:#d7f2a2;font-size:13px}
.pricing{display:none}
.terminal{background:#0d0d0d;border:1px solid var(--border);border-radius:14px;padding:18px;font:13px/1.7 var(--mono);color:#d7dde7;overflow:auto}.terminal a{color:var(--accent)}
footer{padding:40px 0;color:var(--muted);font-size:14px;border-top:1px solid var(--border)}footer .wrap{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;align-items:flex-end}footer a:hover{color:var(--fg)}
@media(max-width:960px){.hero-inner{grid-template-columns:1fr}.hero-visual{min-height:240px;clip-path:none}.hero-copy{margin:0 auto;max-width:none;padding-top:96px}.links a:not(.nav-mobile):not(.lang-btn){display:none}.links a.nav-mobile{display:inline}.grid3,.problems,.workbench,.compare{grid-template-columns:1fr}.row .btn{margin-left:0;width:100%}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
</style>
</head>
<body>
<nav class="nav"><div class="wrap"><a class="brand" href="#">Falsify</a><div class="links"><a href="#system" data-i18n="nav_system">System</a><a href="#demo" data-i18n="nav_demo">Demo</a><a href="/docs/" data-i18n="nav_docs">Docs</a><a class="nav-mobile" href="/docs/" data-i18n="nav_docs">Docs</a><a class="nav-mobile" href="/docs/14-github-action-install.md" data-i18n="btn_install">Install GitHub Action</a><a href="https://github.com/shi275773124/Falsify">GitHub</a><button class="lang-btn" id="lang-btn" onclick="toggleLang()">中文</button></div></div></nav>
<div style="display:none" aria-hidden="true">
  <canvas id="cvs" role="img" aria-label="Falsify scan canvas"></canvas>
</div>
<header class="hero"><div class="hero-inner"><div class="hero-copy"><h1 data-i18n="h1">Looks right is not enough.</h1><div class="hero-chips" role="list" aria-label="Product scope"><span class="hero-chip" role="listitem" data-i18n="hero_chip_unified">Three layers</span></div><p class="sub" data-i18n="hero_sub">Falsify turns confident AI output into a shipping decision:<br>PASS, PASS_WITH_DEBT, or BLOCK — backed by raw evidence.</p><p class="hero-sub-note" data-i18n="hero_definition">Full Falsify = Frame Audit + Adversarial Review + Cutline. Miss a layer, you only have a partial review.</p><div class="actions"><a class="btn primary" href="/docs/14-github-action-install.md" data-i18n="btn_install">Install GitHub Action</a><a class="btn ghost" href="#sample-report" data-i18n="btn_sample_report_hero">View sample report</a></div><div class="hero-meta"><span class="pill" data-i18n="pill_verdicts">PASS / PASS_WITH_DEBT / BLOCK</span></div></div><div class="hero-visual" aria-hidden="true"><div class="hero-visual-inner"><div class="pipeline"><div class="pipeline-step" data-i18n="pipe_claim">Claim</div><div class="pipeline-arrow">↓</div><div class="pipeline-step" data-i18n="pipe_frame">Frame</div><div class="pipeline-arrow">↓</div><div class="pipeline-step" data-i18n="pipe_adversarial">Adversarial</div><div class="pipeline-arrow">↓</div><div class="pipeline-step" data-i18n="pipe_cutline">Cutline</div><div class="pipeline-end"><div class="pipeline-arrow">→</div><div class="pipeline-step"><span class="badge BLOCK">BLOCK</span></div></div></div></div></div></div></header>
<section class="quote"><div class="wrap"><div class="quote-card"><img class="avatar" src="/assets/chris-shi-founder.png" alt="史可鉴 / Chris Shi" width="48" height="48"><div><p data-i18n="quote_p">"Green logs aren't proof. We stopped pretending they were."</p><cite data-i18n="quote_cite">Chris Shi</cite></div></div></div></section>
<section class="hero-layers" id="layers"><div class="wrap"><p class="hero-layers-hook" data-i18n="hero_layers_hook">AI made fake proof cheap.</p><p class="hero-layers-intro" data-i18n="hero_layers_intro">Falsify runs three layers.</p><div class="hero-layers-grid"><div class="hero-layer"><div><span class="hero-layer-tag" data-i18n="hero_layers_l1_tag">Frame</span><span class="hero-layer-map" data-i18n="hero_layers_l1_map">Frame Audit</span></div><p class="hero-layer-body" data-i18n="hero_layers_l1_body">hidden state, authority drift, missing rollback.</p></div><div class="hero-layer"><div><span class="hero-layer-tag" data-i18n="hero_layers_l2_tag">Evidence</span><span class="hero-layer-map" data-i18n="hero_layers_l2_map">Adversarial Review</span></div><p class="hero-layer-body" data-i18n="hero_layers_l2_body">false facts, fake acceptance, audit theater.</p></div><div class="hero-layer"><div><span class="hero-layer-tag" data-i18n="hero_layers_l3_tag">Cutline</span><span class="hero-layer-map" data-i18n="hero_layers_l3_map">Cutline</span></div><p class="hero-layer-body" data-i18n="hero_layers_l3_body">must fix, known debt, delete.</p></div></div><p class="hero-layers-close" data-i18n="hero_layers_close">Three verdicts only.</p><p class="hero-layers-verdicts" data-i18n="hero_layers_verdicts">PASS / PASS_WITH_DEBT / BLOCK</p></div></section>
<section class="s alt" id="sample-report"><div class="wrap"><div class="section-head"><div class="tag" data-i18n="sample_tag">Artifact</div><h2 data-i18n="sample_h2">Real output, not a mockup.</h2><p class="lead" data-i18n="sample_lead">A BLOCK report from the protocol — schema, findings, verdict. No GitHub UI theater.</p></div><div class="sample-artifact"><div class="artifact"><div class="artifact-head"><span>sample-block-report.json</span><span class="badge BLOCK">BLOCK</span></div><div class="artifact-body">{
  "schema_version": "falsify.review.v1",
  "verdict": "BLOCK",
  "findings": [{
    "cutline": "Must Fix",
    "issue": "Logs are treated as state verification",
    "minimal_action": "Add read-after-write probe"
  }]
}</div></div><div class="sample-actions"><a class="btn ghost" href="/examples/sample-block-report.json" data-i18n="sample_download">Download sample JSON</a><a class="btn ghost" href="/docs/14-github-action-install.md" data-i18n="docs_install">Install GitHub Action (5 min) →</a></div></div></div></section>
<section class="s alt" id="system"><div class="wrap"><div class="section-head"><div class="tag" data-i18n="system_tag">System</div><h2 data-i18n="system_h2">Three layers. One decision.</h2><p class="lead" data-i18n="system_lead">Frame Audit, Adversarial Review, and Cutline — built for teams that cannot afford fake PASS.</p></div><div class="grid3"><div class="card"><div class="layer-num" data-i18n="bl_label">Layer 01</div><h3 data-i18n="bl_h3">Frame Audit</h3><ul><li data-i18n="bl_1">hidden state / implicit authority</li><li data-i18n="bl_2">owner / lock / lifecycle</li><li data-i18n="bl_4">rollback / verification path</li></ul></div><div class="card"><div class="layer-num" data-i18n="ar_label">Layer 02</div><h3 data-i18n="ar_h3">Adversarial Review</h3><ul><li data-i18n="ar_1">false truth / false risk</li><li data-i18n="ar_5">prompt-only audit theater</li><li data-i18n="ar_6">monitor-failure laundering</li></ul></div><div class="card"><div class="layer-num" data-i18n="rs_label">Layer 03</div><h3 data-i18n="rs_h3">Cutline</h3><p data-i18n="rs_lead">Decides what blocks now — not a laundry list of every risk.</p><ul><li data-i18n="rs_1">Must Fix</li><li data-i18n="rs_2">Known Debt</li><li data-i18n="rs_3">Delete</li></ul></div></div></div></section>
<section class="s alt" id="not-falsify"><div class="wrap"><div class="section-head"><div class="tag" data-i18n="antipattern_tag">Not Falsify</div><h2 data-i18n="antipattern_h2">Looks like review. Is not full Falsify.</h2><p class="lead" data-i18n="antipattern_lead">Partial checks masquerade as complete review.</p></div><div class="problems"><div class="problem" data-i18n="ap_1">"A second glance" ≠ full Falsify</div><div class="problem" data-i18n="ap_2">Cutline-only ≠ full Falsify</div><div class="problem" data-i18n="ap_3">Every smell as Must Fix ≠ Cutline</div></div></div></section>
<section class="s" id="demo"><div class="wrap"><div class="section-head"><div class="tag" data-i18n="try_tag">Workbench</div><h2 data-i18n="try_h2">See a verdict in seconds.</h2><p class="lead" data-i18n="try_lead">Preview verdict format here. Samples are fixed adversarial demos; live review is one LLM call with your local key — not full Falsify.</p></div><div class="workbench"><div class="panel"><h3 data-i18n="input_h3">Claim</h3><p data-i18n="input_p">Paste a deployment claim, PR summary, or AI-generated report.</p><textarea id="t">Deployment succeeded because the logs completed. Another AI reviewed it and found no issue. No raw verdict, parse status, finish_reason, or usage counts were kept.</textarea><div class="row"><select id="s"><option value="general" data-i18n="scenario_general">General</option><option value="code" data-i18n="scenario_code">Code / PR</option><option value="research" data-i18n="scenario_research">Research</option><option value="production" selected data-i18n="scenario_production">Production</option></select><button class="btn ghost" onclick="runSample()" data-i18n="btn_sample">Run sample</button><button class="btn primary" id="b" onclick="go()" data-i18n="btn_review">Live review</button></div><div class="demo-note" data-i18n="demo_note">Partial layer only. Canned samples are adversarial demos — not full Falsify. Live /review is a single LLM pass with your local key; no Frame Audit gate, no machine Cutline.</div><p class="demo-note" data-i18n="workbench_scope">Full stack: CLI + GitHub Action. This page demonstrates output shape, not enforcement.</p><p class="demo-note" data-i18n="hero_workbench_note">Protocol is three-layer. The public workbench below shows verdict format and adversarial samples — not machine-enforced Frame Audit or Cutline.</p></div><div class="panel result" id="out"><h3 data-i18n="output_h3">Verdict</h3><p data-i18n="output_p">Hit Run sample to preview the decision artifact.</p></div></div></div></section>
<section class="s alt"><div class="wrap"><div class="section-head"><div class="tag" data-i18n="boundary_tag">Boundary</div><h2 data-i18n="boundary_h2">Falsify classifies risk. It does not authorize action.</h2><p class="lead" data-i18n="boundary_p">Live money, production config, cron, gateway, and external send still require independent final judgment. Self-review is not independent review.</p></div></div></section>
<section class="s" id="start"><div class="wrap"><div class="section-head"><div class="tag" data-i18n="start_tag">Start</div><h2 data-i18n="start_h2">Run it locally in 60 seconds.</h2></div><div class="terminal">git clone https://github.com/shi275773124/Falsify.git
cd Falsify
python falsify.py demo
export FALSIFY_PROVIDER=deepseek
export DEEPSEEK_API_KEY=sk-...
python falsify.py review report.md
python web/serve.py
<a href="/docs/14-github-action-install.md" data-i18n="docs_install">Install GitHub Action (5 min) →</a></div><div class="open-core-block" style="margin-top:24px"><p data-i18n="pricing_honest_oss">OSS: MIT core, self-hosted unlimited repos.</p><p data-i18n="pricing_honest_team">Team: waitlist — hosted governance, not the protocol.</p><a href="/docs/12-open-core-boundary.md" data-i18n="licensing_link">Read the full open core boundary →</a></div></div></section>
<footer><div class="wrap"><div><p class="footer-oc" data-i18n="footer_open_core">MIT core · self-hosted unlimited · Team is hosted governance, not the protocol.</p><p class="footer-trust" data-i18n="footer_trust">GitHub Actions · BYOK · falsify.review.v1</p></div><div><a href="https://github.com/shi275773124/Falsify">GitHub</a> · <a href="https://x.com/aishikejian">X</a> · <a href="mailto:chrisshi168@icloud.com">Email</a> · <a href="https://github.com/shi275773124/Falsify/blob/main/LICENSE">License</a> · <a href="/docs/12-open-core-boundary.md" data-i18n="licensing_link">Open core</a></div></div></footer>
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
];
const SAMPLES={general:{verdict:"BLOCK",risks:[{cutline:"Must Fix",issue:"Claim reads confident but cites no raw artifact.",minimal_action:"Attach source output, command log, or reproducible check."},{cutline:"Known Debt",issue:"Secondary review mentioned but not independently verified.",minimal_action:"Re-run with explicit failure-mode checklist.",upgrade_trigger:"Before any customer-facing decision."}]},code:{verdict:"PASS_WITH_DEBT",risks:[{cutline:"Known Debt",issue:"Tests pass but do not assert the risky default path.",minimal_action:"Add one negative test for the default branch.",upgrade_trigger:"Before merge to main."}]},research:{verdict:"BLOCK",risks:[{cutline:"Must Fix",issue:"Conclusion cites summary tables without primary source excerpt.",minimal_action:"Attach table screenshot or raw CSV hash."}]},production:{verdict:"BLOCK",risks:[{cutline:"Must Fix",issue:"Logs completed, but no read-after-write or invariant check proves intended state.",minimal_action:"Attach post-deploy probe output and rollback command."},{cutline:"Delete",issue:"Another AI reviewed it — not evidence.",minimal_action:"Remove from acceptance chain."}]}};
const T={en:{"nav_system":"System","nav_demo":"Demo","nav_docs":"Docs","h1":"Looks right is not enough.","hero_chip_unified":"Three layers","hero_sub":"Falsify turns confident AI output into a shipping decision:\nPASS, PASS_WITH_DEBT, or BLOCK — backed by raw evidence.","hero_definition":"Full Falsify = Frame Audit + Adversarial Review + Cutline. Miss a layer, you only have a partial review.","hero_workbench_note":"Protocol is three-layer. The public workbench below shows verdict format and adversarial samples — not machine-enforced Frame Audit or Cutline.","btn_install":"Install GitHub Action","btn_sample_report_hero":"View sample report","pill_verdicts":"PASS / PASS_WITH_DEBT / BLOCK","pipe_claim":"Claim","pipe_frame":"Frame","pipe_adversarial":"Adversarial","pipe_cutline":"Cutline","quote_p":"\"Green logs aren't proof. We stopped pretending they were.\"","quote_cite":"Chris Shi","hero_layers_hook":"AI made fake proof cheap.","hero_layers_intro":"Falsify runs three layers.","hero_layers_l1_tag":"Frame","hero_layers_l1_map":"Frame Audit","hero_layers_l1_body":"hidden state, authority drift, missing rollback.","hero_layers_l2_tag":"Evidence","hero_layers_l2_map":"Adversarial Review","hero_layers_l2_body":"false facts, fake acceptance, audit theater.","hero_layers_l3_tag":"Cutline","hero_layers_l3_map":"Cutline","hero_layers_l3_body":"must fix, known debt, delete.","hero_layers_close":"Three verdicts only.","hero_layers_verdicts":"PASS / PASS_WITH_DEBT / BLOCK","sample_tag":"Artifact","sample_h2":"Real output, not a mockup.","sample_lead":"A BLOCK report from the protocol — schema, findings, verdict. No GitHub UI theater.","sample_download":"Download sample JSON","system_tag":"System","system_h2":"Three layers. One decision.","system_lead":"Frame Audit, Adversarial Review, and Cutline — built for teams that cannot afford fake PASS.","bl_label":"Layer 01","ar_label":"Layer 02","rs_label":"Layer 03","bl_h3":"Frame Audit","ar_h3":"Adversarial Review","rs_h3":"Cutline","bl_1":"hidden state / implicit authority","bl_2":"owner / lock / lifecycle","bl_4":"rollback / verification path","ar_1":"false truth / false risk","ar_5":"prompt-only audit theater","ar_6":"monitor-failure laundering","rs_1":"Must Fix","rs_2":"Known Debt","rs_3":"Delete","rs_lead":"Decides what blocks now — not a laundry list of every risk.","antipattern_tag":"Not Falsify","antipattern_h2":"Looks like review. Is not full Falsify.","antipattern_lead":"Partial checks masquerade as complete review.","ap_1":"\"A second glance\" ≠ full Falsify","ap_2":"Cutline-only ≠ full Falsify","ap_3":"Every smell as Must Fix ≠ Cutline","try_tag":"Workbench","try_h2":"See a verdict in seconds.","try_lead":"Preview verdict format here. Samples are fixed adversarial demos; live review is one LLM call with your local key — not full Falsify.","input_h3":"Claim","input_p":"Paste a deployment claim, PR summary, or AI-generated report.","output_h3":"Verdict","output_p":"Hit Run sample to preview the decision artifact.","demo_note":"Partial layer only. Canned samples are adversarial demos — not full Falsify. Live /review is a single LLM pass with your local key; no Frame Audit gate, no machine Cutline.","workbench_scope":"Full stack: CLI + GitHub Action. This page demonstrates output shape, not enforcement.","scenario_general":"General","scenario_code":"Code / PR","scenario_research":"Research","scenario_production":"Production","btn_sample":"Run sample","btn_review":"Live review","start_tag":"Start","start_h2":"Run it locally in 60 seconds.","docs_install":"Install GitHub Action (5 min) →","boundary_tag":"Boundary","boundary_h2":"Falsify classifies risk. It does not authorize action.","boundary_p":"Live money, production config, cron, gateway, and external send still require independent final judgment. Self-review is not independent review.","pricing_honest_oss":"OSS: MIT core, self-hosted unlimited repos.","pricing_honest_team":"Team: waitlist — hosted governance, not the protocol.","licensing_link":"Read the full open core boundary →","footer_open_core":"MIT core · self-hosted unlimited · Team is hosted governance, not the protocol.","footer_trust":"GitHub Actions · BYOK · falsify.review.v1"},
zh:{"nav_system":"系统","nav_demo":"演示","nav_docs":"文档","h1":"看起来对，不够。","hero_chip_unified":"三层合一","hero_sub":"Falsify 把 AI 的自信输出变成上线决策：\nPASS、PASS_WITH_DEBT、BLOCK — 以原始证据为准。","hero_definition":"完整 Falsify = 框架审 + 对抗审 + Cutline；缺任一层，只是局部审查。","hero_workbench_note":"协议是三层。下方公网工作台只演示裁决格式与对抗审样例 — 非机审框架审，非机审 Cutline。","btn_install":"安装 GitHub Action","btn_sample_report_hero":"查看样例报告","pill_verdicts":"PASS / PASS_WITH_DEBT / BLOCK","pipe_claim":"Claim","pipe_frame":"框架审","pipe_adversarial":"对抗审","pipe_cutline":"Cutline","quote_p":"「日志绿了，不等于证据成立。我们不再假装它算数。」","quote_cite":"史可鉴","hero_layers_hook":"AI 让假证明变便宜了。","hero_layers_intro":"Falsify 走三层。","hero_layers_l1_tag":"审结构","hero_layers_l1_map":"框架审","hero_layers_l1_body":"隐式状态、越权路径、回滚缺失。","hero_layers_l2_tag":"审证据","hero_layers_l2_map":"对抗审","hero_layers_l2_body":"假事实、假验收、审计作秀。","hero_layers_l3_tag":"裁边界","hero_layers_l3_map":"Cutline","hero_layers_l3_body":"必须修、可以欠、该删。","hero_layers_close":"走完，只落三档裁决。","hero_layers_verdicts":"PASS / PASS_WITH_DEBT / BLOCK","sample_tag":"产物","sample_h2":"真输出，不是 mock。","sample_lead":"协议产出的 BLOCK 报告 — schema、findings、verdict。没有 GitHub UI 作秀。","sample_download":"下载样例 JSON","system_tag":"系统","system_h2":"三层结构，一个决策。","system_lead":"框架审、对抗审、Cutline — 给承受不起假 PASS 的团队。","bl_label":"第一层","ar_label":"第二层","rs_label":"第三层","bl_h3":"框架审","ar_h3":"对抗审","rs_h3":"Cutline","bl_1":"隐藏状态与隐式授权","bl_2":"归属、锁与生命周期","bl_4":"回滚与验证路径","ar_1":"虚假事实与虚假风险","ar_5":"提示词作秀","ar_6":"监控洗白","rs_1":"Must Fix","rs_2":"Known Debt","rs_3":"Delete","rs_lead":"决定当下什么阻塞，不是罗列全部风险。","antipattern_tag":"不是 Falsify","antipattern_h2":"像审查，不是完整 Falsify。","antipattern_lead":"局部检查冒充完整审查。","ap_1":"「再看一眼」≠ 完整 Falsify","ap_2":"只有 Cutline ≠ 完整 Falsify","ap_3":"每个 smell 都是 Must Fix ≠ Cutline","try_tag":"工作台","try_h2":"几秒内看到裁决。","try_lead":"在此预览裁决格式。样例为固定对抗审样例；真审查为单次模型调用、本地 key — 不是完整 Falsify。","input_h3":"声明","input_p":"粘贴部署声明、PR 摘要或 AI 生成报告。","output_h3":"裁决","output_p":"点「运行样例」预览裁决。","demo_note":"局部层演示。样例为固定对抗审样例，不是完整 Falsify。真 /review 为单次模型调用、本地 key；无框架审闸门，无机审 Cutline。","workbench_scope":"完整协议：CLI + GitHub Action。本页只演示输出形态，不做强制。","scenario_general":"通用","scenario_code":"代码 / PR","scenario_research":"研究","scenario_production":"生产","btn_sample":"运行样例","btn_review":"真审查","start_tag":"开始","start_h2":"60 秒本地跑起来。","docs_install":"5 分钟安装 GitHub Action →","boundary_tag":"边界","boundary_h2":"Falsify 只做风险分类，不做执行授权。","boundary_p":"真实资金、生产配置、cron、网关与外部发送仍需独立终审。自己审自己不算独立判断。","pricing_honest_oss":"开源：MIT 核心，自托管仓库不限。","pricing_honest_team":"Team：候补名单 — 托管治理，不是协议本身。","licensing_link":"阅读完整 Open Core 边界 →","footer_open_core":"MIT 核心 · 自托管不限 · Team 是托管治理，不是协议。","footer_trust":"GitHub Actions · BYOK · falsify.review.v1"}};
let lang='en';
function applyLang(){document.documentElement.lang=lang==='zh'?'zh-CN':'en';document.getElementById('lang-btn').textContent=lang==='en'?'中文':'EN';document.querySelectorAll('[data-i18n]').forEach(el=>{const k=el.getAttribute('data-i18n');if(T[lang][k]===undefined)return;const v=T[lang][k];if(k==='hero_sub')el.innerHTML=v.replace(/\n/g,'<br>');else el.textContent=v;});}
function toggleLang(){lang=lang==='en'?'zh':'en';applyLang();}
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
function renderVerdict(d){let h='<span class="badge '+d.verdict+'">'+d.verdict+'</span>';for(const x of d.risks||[]){h+='<div class="risk"><small>'+esc(x.cutline||x.severity||'Finding')+'</small>'+esc(x.issue||'')+'<br><em>'+esc(x.minimal_action||'')+'</em>';if(x.upgrade_trigger){h+='<br><em>'+(lang==='zh'?'升级触发：':'Upgrade trigger: ')+esc(x.upgrade_trigger)+'</em>'}h+='</div>'}return h}
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
        ctype = {".svg": "image/svg+xml", ".png": "image/png", ".gif": "image/gif", ".css": "text/css", ".json": "application/json"}[suffix]
        return self._send(200, target.read_bytes(), ctype)

    def do_HEAD(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return
        if parsed.path.startswith("/docs/") or parsed.path.startswith("/assets/") or parsed.path.startswith("/examples/"):
            target = safe_repo_path(self.path)
            if not target or not target.is_file():
                self.send_response(404)
                self.end_headers()
                return
            if target.suffix.lower() == ".md":
                html = render_markdown(
                    target.read_text(encoding="utf-8"),
                    doc_title(target.stem),
                    current_path=parsed.path,
                )
                body = html.encode("utf-8")
                ctype = "text/html; charset=utf-8"
            else:
                body = target.read_bytes()
                ctype = {
                    ".svg": "image/svg+xml",
                    ".png": "image/png",
                    ".gif": "image/gif",
                    ".css": "text/css",
                    ".json": "application/json",
                }[target.suffix.lower()]
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._send(200, PAGE, "text/html")
        elif parsed.path.startswith("/docs/") or parsed.path.startswith("/assets/") or parsed.path.startswith("/examples/"):
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
