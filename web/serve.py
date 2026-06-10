#!/usr/bin/env python3
"""falsify web — paste-and-go. One box, one button: find what's wrong before you ship.

Zero dependencies (stdlib only). Reuses falsify.py for the model call + config.

    pip install -e .          # or just have falsify.py on the path
    export DEEPSEEK_API_KEY=sk-...        # or set a .falsify with FALSIFY_PROVIDER
    python web/serve.py                   # then open http://127.0.0.1:8000

NOTE: this local POC uses YOUR key (from env / .falsify / --provider). The hosted
"try 3× free, no key" experience is a separate deployment — this is its seed.
"""
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import falsify  # noqa: E402

PROVIDER = os.environ.get("FALSIFY_PROVIDER")  # optional; else env/.falsify decide

SCENARIOS = {
    "general":    "General fact-dense output.",
    "tech":       "A technical-selection / architecture decision. Watch for unsupported benchmarks, version/compat claims, hand-waved trade-offs.",
    "competitor": "A competitor / market comparison. Watch for wrong figures, stale data, apples-to-oranges rows, cherry-picked sources.",
    "pr":         "A pull request / migration plan / README. Watch for broken commands, wrong flags, risky defaults, missing rollback.",
    "research":   "An investment / research report. Watch for flipped signs, wrong units, misread tables, conclusions the data doesn't support.",
}

RISK_SYSTEM = """You are the Skeptic — an adversarial reviewer. Find what would ship
wrong in the text below. Scenario: {scenario}

You only see this text. Do NOT claim a file/tool/source is fake just because you
can't see it — if unverifiable, say so, don't assert it's false.

Return ONLY valid JSON, no prose around it:
{{"verdict":"PROCEED|HOLD|ARCHIVE",
  "risks":[{{"severity":"high|med|low",
             "type":"number|logic|source|stale|scope|other",
             "issue":"one sentence: the problem + how to verify it"}}]}}

At most 5 risks, worst first. PROCEED only if nothing material is wrong.
"""


def extract_json(text):
    """Models sometimes wrap JSON in prose / code fences — pull out the object."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    a, b = text.find("{"), text.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no JSON object in response")
    return json.loads(text[a:b + 1])


def review(text, scenario):
    base, key, model = falsify.resolve_endpoint(provider=PROVIDER)
    system = RISK_SYSTEM.format(scenario=SCENARIOS.get(scenario, SCENARIOS["general"]))
    raw = falsify.chat(system, text, base, key, model)
    try:
        data = extract_json(raw)
    except (ValueError, json.JSONDecodeError):
        return {"verdict": "HOLD", "risks": [], "raw": raw,
                "note": "model didn't return clean JSON; showing raw output"}
    v = str(data.get("verdict", "HOLD")).upper()
    data["verdict"] = "HOLD" if v.startswith("HOLD") else (v if v in ("PROCEED", "ARCHIVE") else "HOLD")
    data["risks"] = (data.get("risks") or [])[:5]
    return data


PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Falsify — find what's wrong before you ship</title>
<style>
:root{color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;font:16px/1.5 -apple-system,"Segoe UI",Roboto,"Microsoft YaHei",sans-serif;
  background:radial-gradient(900px 500px at 20% -10%,#1b2747 0%,rgba(27,39,71,0) 60%),#0b1020;color:#e6edf3}
.wrap{max-width:760px;margin:0 auto;padding:48px 20px 80px}
h1{font-size:34px;margin:0 0 6px}.sub{color:#8b96a8;margin:0 0 28px}
textarea{width:100%;min-height:240px;padding:14px;border-radius:12px;border:1px solid #28324e;
  background:#0f1729;color:#e6edf3;font:14px/1.5 ui-monospace,Consolas,monospace;resize:vertical}
.row{display:flex;gap:12px;align-items:center;margin-top:14px;flex-wrap:wrap}
select{padding:10px 12px;border-radius:10px;border:1px solid #28324e;background:#0f1729;color:#e6edf3}
button{margin-left:auto;padding:12px 22px;border:0;border-radius:10px;font-weight:700;font-size:16px;
  background:#3b82f6;color:#fff;cursor:pointer}button:disabled{opacity:.5;cursor:wait}
#out{margin-top:28px}
.verdict{display:inline-block;padding:8px 16px;border-radius:10px;font-weight:800;font-size:20px;letter-spacing:.5px}
.PROCEED{background:#10331f;color:#3fb950;border:1px solid #1f6f3f}
.HOLD{background:#3a2a10;color:#f0a93e;border:1px solid #8a5a14}
.ARCHIVE{background:#3a1416;color:#f85149;border:1px solid #8a2a2e}
.lead{margin:16px 0 10px;color:#adbac7}
.risk{background:#0f1729;border:1px solid #28324e;border-left:4px solid var(--c);border-radius:10px;padding:12px 14px;margin:10px 0}
.tag{font-size:12px;text-transform:uppercase;letter-spacing:.5px;color:#8b96a8}
.high{--c:#f85149}.med{--c:#f0a93e}.low{--c:#8b96a8}
pre{white-space:pre-wrap;background:#0f1729;border:1px solid #28324e;border-radius:10px;padding:14px}
.err{color:#f85149}
</style></head><body><div class="wrap">
<h1>Falsify</h1>
<p class="sub">Find what's wrong before you ship. Paste your AI output; a skeptic model takes it apart.</p>
<textarea id="t" placeholder="Paste the AI-written report / plan / answer here…"></textarea>
<div class="row">
  <select id="s">
    <option value="general">General</option>
    <option value="tech">Tech selection</option>
    <option value="competitor">Competitor analysis</option>
    <option value="pr">PR / plan / README</option>
    <option value="research">Research report</option>
  </select>
  <button id="b" onclick="go()">Find what's wrong</button>
</div>
<div id="out"></div>
<script>
async function go(){
  const t=document.getElementById('t').value.trim();
  const out=document.getElementById('out'), b=document.getElementById('b');
  if(!t){out.innerHTML='<p class="err">Paste something first.</p>';return}
  b.disabled=true;out.innerHTML='<p class="lead">The Skeptic is reading…</p>';
  try{
    const r=await fetch('/review',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({text:t,scenario:document.getElementById('s').value})});
    const d=await r.json();
    if(d.error){out.innerHTML='<p class="err">'+esc(d.error)+'</p>';b.disabled=false;return}
    if(d.raw){out.innerHTML='<div class="verdict '+d.verdict+'">Verdict: '+d.verdict+'</div><pre>'+esc(d.raw)+'</pre>';b.disabled=false;return}
    const n=d.risks.length;
    let h='<div class="verdict '+d.verdict+'">Verdict: '+d.verdict+'</div>';
    h+='<p class="lead">'+(n?('You almost shipped '+n+' issue'+(n>1?'s':'')+':'):'No material issues found.')+'</p>';
    for(const x of d.risks){
      const sev=normSeverity(x.severity);
      h+='<div class="risk '+sev+'"><span class="tag">'+esc(sev)+' · '+esc(x.type||'')+'</span><div>'+esc(x.issue||'')+'</div></div>';
    }
    out.innerHTML=h;
  }catch(e){out.innerHTML='<p class="err">'+esc(String(e))+'</p>'}
  b.disabled=false;
}
function normSeverity(s){s=String(s||'low').toLowerCase();return ['high','med','low'].includes(s)?s:'low'}
function esc(s){return s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
</script>
</div></body></html>"""


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE, "text/html")
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        if self.path != "/review":
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
        except Exception as e:  # noqa: BLE001 — never crash the server
            self._send(200, json.dumps({"error": f"server error: {e}"}))

    def log_message(self, *a):
        pass


def main():
    port = int(os.environ.get("PORT", "8000"))
    print(f"falsify web → http://127.0.0.1:{port}  (Ctrl+C to stop)")
    try:
        ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
