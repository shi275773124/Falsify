#!/usr/bin/env python3
"""Falsify local website and paste-and-go reviewer.

The homepage is static product/docs copy. The /review endpoint is real: it
reuses falsify.py and the configured provider or agent CLI.
"""
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import falsify  # noqa: E402

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


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Falsify - adversarial review for AI-era work</title>
<meta name="description" content="Falsify attacks false confidence, forces evidence, and cuts every risk into Must Fix, Known Debt, or Delete.">
<style>
:root{
  color-scheme:dark;
  --background:#090b0f;
  --foreground:#f5f7fb;
  --muted:#9aa4b2;
  --border:#252c38;
  --panel:#10141c;
  --panel-2:#151b25;
  --accent:#76e0c6;
  --danger:#ff6b6b;
  --warning:#f3b95f;
  --success:#73d18b;
  --neutral:#94a3b8;
  --radius:8px;
  --s1:6px;--s2:10px;--s3:16px;--s4:24px;--s5:40px;--s6:64px;--s7:96px;
  --font:Inter,Geist,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Arial,sans-serif;
  --mono:"SFMono-Regular",Consolas,"Liberation Mono",monospace;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--background);color:var(--foreground);font:16px/1.55 var(--font);letter-spacing:0}
a{color:inherit}
.wrap{width:min(1160px,calc(100% - 40px));margin:0 auto}
.nav{position:sticky;top:0;z-index:20;background:rgba(9,11,15,.82);backdrop-filter:blur(18px);border-bottom:1px solid var(--border)}
.nav .wrap{display:flex;align-items:center;justify-content:space-between;height:64px}
.brand{font-weight:760}.links{display:flex;gap:18px;align-items:center;color:var(--muted);font-size:14px}.links a{text-decoration:none}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:42px;padding:0 16px;border:1px solid var(--border);border-radius:var(--radius);background:#121822;color:var(--foreground);text-decoration:none;font-weight:700;cursor:pointer}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#05100d}.btn.ghost{background:transparent}
.hero{display:grid;grid-template-columns:minmax(0,.9fr) minmax(420px,1.1fr);gap:48px;align-items:center;padding:42px 0 52px;overflow:hidden}
.eyebrow{color:var(--accent);font:700 13px/1 var(--mono);text-transform:uppercase}
h1{margin:16px 0 16px;font-size:clamp(46px,7vw,88px);line-height:.94;letter-spacing:0;max-width:780px}
.sub{font-size:21px;line-height:1.45;color:#c7d0dc;max-width:680px;margin:0 0 28px}
.actions{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:24px}
.markers{display:flex;gap:10px;flex-wrap:wrap;color:var(--muted);font:700 12px/1 var(--mono)}
.marker{border:1px solid var(--border);border-radius:999px;padding:9px 11px;background:#0c1118}
.field{position:relative;min-width:0;min-height:500px;border:1px solid #26313e;background:linear-gradient(180deg,#111720,#090c12);overflow:hidden;border-radius:0}
.field:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:40px 40px;mask-image:linear-gradient(180deg,#000,rgba(0,0,0,.62))}
.claim,.strip,.lane,.verdicts{position:absolute;border:1px solid var(--border);background:rgba(16,20,28,.86);backdrop-filter:blur(10px)}
.claim{left:36px;top:42px;width:48%;padding:18px;border-left:3px solid var(--warning)}
.claim b,.lane b{display:block;color:#fff;margin-bottom:8px}.claim p,.lane p{margin:0;color:var(--muted);font:13px/1.45 var(--mono)}
.strip{right:30px;top:46px;width:38%;padding:12px;font:12px/1.7 var(--mono);color:#a9b4c2}
.strip span{display:block}.ok{color:var(--success)}.bad{color:var(--danger)}
.lane{left:38px;right:38px;padding:14px}
.lane.evidence{top:155px}.lane.assumptions{top:245px}.lane.failures{top:335px}
.lane:after{content:"";position:absolute;height:1px;background:linear-gradient(90deg,var(--accent),transparent);left:18px;right:18px;bottom:-22px}
.verdicts{left:38px;right:38px;bottom:28px;display:grid;grid-template-columns:repeat(3,1fr);gap:10px;padding:14px}
.v{border:1px solid var(--border);padding:15px 12px;text-align:center;font:800 13px/1 var(--mono)}
.v.pass{color:var(--success)}.v.debt{color:var(--warning)}.v.block{color:var(--danger)}
section{padding:84px 0;border-top:1px solid var(--border)}
.section-head{display:grid;grid-template-columns:.38fr 1fr;gap:40px;margin-bottom:36px}
h2{font-size:36px;line-height:1.08;margin:0}.lead{color:#c7d0dc;font-size:19px;margin:0;max-width:760px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.card{border:1px solid var(--border);background:var(--panel);border-radius:var(--radius);padding:20px}
.card h3{margin:0 0 10px;font-size:18px}.card p,.card li{color:var(--muted)}
.card ul{padding-left:18px;margin:0}.card li+li{margin-top:8px}
.compare{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--border);border:1px solid var(--border)}
.compare div{background:var(--panel);padding:18px}.compare b{color:var(--danger)}.compare strong{color:var(--accent)}
.flow{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.step{background:var(--panel);border:1px solid var(--border);padding:18px;border-radius:var(--radius)}
.step span{display:block;color:var(--accent);font:700 12px var(--mono);margin-bottom:8px}
.terminal{background:#05070a;border:1px solid #27313c;border-radius:var(--radius);padding:18px;font:13px/1.65 var(--mono);color:#c9d2de;overflow:auto}
.demo{display:grid;grid-template-columns:1fr 1fr;gap:16px}
textarea{width:100%;min-height:260px;background:#080b10;color:#e7eef8;border:1px solid var(--border);border-radius:var(--radius);padding:14px;font:13px/1.55 var(--mono);resize:vertical}
select{background:#080b10;color:#e7eef8;border:1px solid var(--border);border-radius:var(--radius);padding:10px}
.row{display:flex;gap:10px;align-items:center;margin-top:10px}.row button{margin-left:auto}
.result{min-height:260px;background:#080b10;border:1px solid var(--border);border-radius:var(--radius);padding:14px}
.badge{display:inline-block;border:1px solid var(--border);border-radius:999px;padding:7px 10px;font:800 12px var(--mono)}
.PASS{color:var(--success)}.PASS_WITH_DEBT{color:var(--warning)}.BLOCK{color:var(--danger)}
.risk{margin-top:12px;border-left:3px solid var(--warning);padding-left:12px;color:#c9d2de}.risk small{display:block;color:var(--muted);font:700 11px var(--mono);text-transform:uppercase}
footer{padding:42px 0;color:var(--muted);border-top:1px solid var(--border)}footer .wrap{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}
@media (max-width:900px){
  .hero{grid-template-columns:1fr;padding:34px 0 42px}.field{min-height:680px}.links{display:none}
  .hero>*{min-width:0}.sub{max-width:100%}.field{width:100%}
  .markers{display:grid;grid-template-columns:1fr;gap:8px}
  .marker{width:100%;text-align:center;white-space:normal;line-height:1.35}
  .claim{left:18px;right:18px;top:42px;width:auto;padding:14px}
  .strip{left:18px;right:18px;top:178px;width:auto;padding:10px;font-size:11px}
  .lane{left:18px;right:18px;padding:13px}
  .lane.evidence{top:300px}.lane.assumptions{top:405px}.lane.failures{top:510px}
  .verdicts{left:18px;right:18px;bottom:18px}
  .section-head,.grid,.flow,.demo{grid-template-columns:1fr}.compare{grid-template-columns:1fr}
  h1{font-size:44px}.sub{font-size:18px}.wrap{width:min(100% - 28px,362px);margin-left:14px;margin-right:auto}
}
</style>
</head>
<body>
<nav class="nav"><div class="wrap"><a class="brand" href="#">Falsify</a><div class="links"><a href="#system">System</a><a href="#examples">Examples</a><a href="#start">Get started</a><a href="https://github.com/shi275773124/Falsify">GitHub</a></div></div></nav>
<main>
<header class="wrap hero">
  <div>
    <div class="eyebrow">Adversarial review framework</div>
    <h1>Stop trusting confident AI.</h1>
    <p class="sub">Falsify is an adversarial review framework for AI-generated code, research, and production decisions.</p>
    <div class="actions"><a class="btn primary" href="#start">Get started</a><a class="btn ghost" href="https://github.com/shi275773124/Falsify">View on GitHub</a></div>
    <div class="markers"><span class="marker">PASS / PASS_WITH_DEBT / BLOCK</span><span class="marker">3-layer review stack</span><span class="marker">Evidence-first decisions</span></div>
  </div>
  <div class="field" role="img" aria-label="Original Falsify audit field showing a claim cut into evidence, assumptions, failure modes, and verdict lanes.">
    <div class="claim"><b>Confident claim</b><p>"Deployment succeeded. Logs completed. Another AI reviewed it."</p></div>
    <div class="strip"><span class="ok">$ job completed</span><span class="bad">state: not verified</span><span>finish_reason: missing</span><span>parse_status: missing</span></div>
    <div class="lane evidence"><b>Evidence</b><p>Raw artifacts, readable diffs, command output, source links.</p></div>
    <div class="lane assumptions"><b>Assumptions</b><p>What must be true for the decision to hold.</p></div>
    <div class="lane failures"><b>Failure modes</b><p>False truth, false risk, silent failure, permission drift.</p></div>
    <div class="verdicts"><div class="v pass">PASS</div><div class="v debt">PASS_WITH_DEBT</div><div class="v block">BLOCK</div></div>
  </div>
</header>

<section><div class="wrap section-head"><h2>False confidence got cheaper.</h2><p class="lead">AI made teams faster. It also made polished wrongness easier to ship: green logs, second-model agreement, passing tests that checked the wrong thing, and summaries that replaced raw evidence.</p></div></section>

<section id="system"><div class="wrap">
  <div class="section-head"><h2>The system</h2><p class="lead">Falsify = Brooks-Lint + Adversarial Review + Risk Scalpel.</p></div>
  <div class="grid">
    <div class="card"><h3>Brooks-Lint</h3><ul><li>hidden state</li><li>implicit authority</li><li>duplicated control paths</li><li>brittle rollback</li><li>unverifiable acceptance</li><li>AI summaries replacing raw evidence</li></ul></div>
    <div class="card"><h3>Adversarial Review</h3><ul><li>false truth</li><li>false risk</li><li>silent failure</li><li>stale data</li><li>permission drift</li><li>semantic nudges toward PASS</li><li>monitor failure laundering</li></ul></div>
    <div class="card"><h3>Risk Scalpel</h3><ul><li>Must Fix: blocks the current decision</li><li>Known Debt: real risk with a trigger</li><li>Delete: no concrete current failure mode</li></ul></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="section-head"><h2>Fake proof is not proof.</h2><p class="lead">Falsify does not ask whether another model sounded confident. It asks what evidence survives attack.</p></div>
  <div class="compare">
    <div><b>"The model said it is fine."</b></div><div><strong>Where is the raw artifact?</strong></div>
    <div><b>"Another AI reviewed it."</b></div><div><strong>Did it check the failure mode or just agree?</strong></div>
    <div><b>"The logs look successful."</b></div><div><strong>Did the actual state change?</strong></div>
    <div><b>"The output is empty, so no issue."</b></div><div><strong>Was it truncated, filtered, or unparsable?</strong></div>
    <div><b>"This is only theoretical."</b></div><div><strong>Can it affect the current decision?</strong></div>
    <div><b>"We should add a big safety checklist."</b></div><div><strong>What is the minimal blocking fix?</strong></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="section-head"><h2>Workflow</h2><p class="lead">Input a claim. Attack assumptions, evidence, failure modes, and acceptance criteria. Cut findings. Return a decision.</p></div>
  <div class="flow">
    <div class="step"><span>INPUT</span>code, report, deployment claim, AI output, research conclusion</div>
    <div class="step"><span>ATTACK</span>assumptions, evidence, failure modes, acceptance criteria</div>
    <div class="step"><span>CUT</span>Must Fix, Known Debt, Delete</div>
    <div class="step"><span>OUTPUT</span>PASS, PASS_WITH_DEBT, BLOCK</div>
  </div>
</div></section>

<section id="examples"><div class="wrap">
  <div class="section-head"><h2>Examples</h2><p class="lead">Synthetic examples, not customer cases.</p></div>
  <div class="grid">
    <div class="card"><h3>Deployment logs</h3><p>Normal review says deployment succeeded because logs completed. Falsify blocks because logs prove something ran; they do not prove the system is in the intended state.</p></div>
    <div class="card"><h3>Prompt injection</h3><p>Normal AI review says no issue found. Falsify requires raw output, parse status, finish_reason, usage/token counts when available, and known-pattern or reproducer evidence.</p></div>
    <div class="card"><h3>Twenty risks</h3><p>Normal audit lists everything. Falsify cuts each finding into Must Fix, Known Debt, or Delete so the decision is not buried in generic TODOs.</p></div>
  </div>
</div></section>

<section id="start"><div class="wrap">
  <div class="section-head"><h2>Get started</h2><p class="lead">Use the CLI locally, run the deterministic fixture demo, or start the real paste-and-go web reviewer with your configured provider key.</p></div>
  <div class="terminal">git clone https://github.com/shi275773124/Falsify.git
cd Falsify
python -m pip install -e .[dev]
python falsify.py demo
python falsify.py lint examples/comparison-case-study/05-final-excerpt.md
export DEEPSEEK_API_KEY=sk-...
python falsify.py review report.md --provider deepseek
python web/serve.py</div>
</div></section>

<section><div class="wrap">
  <div class="section-head"><h2>Try the local reviewer</h2><p class="lead">This calls the configured backend. It is not a fake analysis. Without an API key or provider config, it will return a setup error.</p></div>
  <div class="demo">
    <div><textarea id="t">Deployment succeeded because the logs completed. Another AI reviewed it and found no issue. The prompt-injection audit is covered by a checklist. No raw verdict, parse status, finish_reason, or usage counts were kept.</textarea><div class="row"><select id="s"><option value="general">General</option><option value="code">Code / PR</option><option value="research">Research</option><option value="production">Production</option></select><button class="btn primary" id="b" onclick="go()">Run review</button></div></div>
    <div class="result" id="out"><span class="badge BLOCK">Example shape: BLOCK</span><div class="risk"><small>Must Fix</small>Logs are not state verification. Attach a read-after-write or invariant check.</div></div>
  </div>
</div></section>

<section><div class="wrap section-head"><h2>Follow the work</h2><p class="lead">Falsify is evolving with real AI-agent, code review, and production-risk workflows. If you are working on similar problems, feel free to follow along or reach out.<br><br><a href="https://github.com/shi275773124/Falsify">GitHub</a> · <a href="https://x.com/aishikejian">X / Twitter</a> · <a href="mailto:chrisshi168@icloud.com">Email</a></p></div></section>
</main>
<footer><div class="wrap"><div>Falsify</div><div><a href="https://github.com/shi275773124/Falsify">GitHub</a> · <a href="https://x.com/aishikejian">X / Twitter</a> · <a href="mailto:chrisshi168@icloud.com">Email</a> · <a href="../LICENSE">License</a></div></div></footer>
<script>
async function go(){
  const t=document.getElementById('t').value.trim();
  const out=document.getElementById('out'), b=document.getElementById('b');
  if(!t){out.innerHTML='<p>Paste something first.</p>';return}
  b.disabled=true;out.innerHTML='<p>Reviewing...</p>';
  try{
    const r=await fetch('/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:t,scenario:document.getElementById('s').value})});
    const d=await r.json();
    if(d.error){out.innerHTML='<p>'+esc(d.error)+'</p>';b.disabled=false;return}
    if(d.raw){out.innerHTML='<span class="badge '+d.verdict+'">'+d.verdict+'</span><pre>'+esc(d.raw)+'</pre>';b.disabled=false;return}
    let h='<span class="badge '+d.verdict+'">'+d.verdict+'</span>';
    for(const x of d.risks||[]){
      h+='<div class="risk"><small>'+esc(x.cutline||x.severity||'Finding')+'</small>'+esc(x.issue||'')+'<br><em>'+esc(x.minimal_action||'')+'</em></div>';
    }
    out.innerHTML=h;
  }catch(e){out.innerHTML='<p>'+esc(String(e))+'</p>'}
  b.disabled=false;
}
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
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
