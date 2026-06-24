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
WEB_DIR = Path(__file__).resolve().parent
ALLOWED_STATIC_EXTS = {".md", ".svg", ".png", ".gif", ".css", ".js", ".json"}
STATIC_CTYPE = {
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".gif": "image/gif",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
}
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


PAGE = load_homepage()

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _file_response_body(self, parsed_path, target):
        if target.suffix.lower() == ".md":
            html = render_markdown(
                target.read_text(encoding="utf-8"),
                doc_title(target.stem),
                current_path=parsed_path,
            )
            return html.encode("utf-8"), "text/html; charset=utf-8"
        suffix = target.suffix.lower()
        return target.read_bytes(), STATIC_CTYPE[suffix]

    def serve_static(self):
        parsed = urlparse(self.path)
        if parsed.path == "/docs/":
            return self._send(200, docs_index(), "text/html")
        target = safe_web_static(self.path) or safe_examples_path(self.path) or safe_repo_path(self.path)
        if not target or not target.is_file():
            return self._send(404, json.dumps({"error": "not found"}))
        if target.suffix.lower() == ".md":
            title = doc_title(target.stem)
            html = render_markdown(
                target.read_text(encoding="utf-8"),
                title,
                current_path=parsed.path,
            )
            return self._send(200, html, "text/html")
        return self._send(200, target.read_bytes(), STATIC_CTYPE[target.suffix.lower()])

    def do_HEAD(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return
        target = None
        if parsed.path.startswith("/docs/") or parsed.path.startswith("/assets/"):
            target = safe_repo_path(self.path)
        elif parsed.path.startswith("/static/"):
            target = safe_web_static(self.path)
        elif parsed.path.startswith("/examples/"):
            target = safe_examples_path(self.path)
        if target and target.is_file():
            body, ctype = self._file_response_body(parsed.path, target)
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
        elif (
            parsed.path.startswith("/docs/")
            or parsed.path.startswith("/assets/")
            or parsed.path.startswith("/static/")
            or parsed.path.startswith("/examples/")
        ):
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
