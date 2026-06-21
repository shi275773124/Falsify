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
.lang-btn{background:transparent;border:1px solid var(--border);border-radius:var(--radius);color:var(--muted);cursor:pointer;font:700 12px var(--mono);padding:6px 12px;transition:border-color .15s,color .15s}
.lang-btn:hover{border-color:var(--accent);color:var(--accent)}
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
.step .lbl{display:block;color:var(--accent);font:700 12px var(--mono);margin-bottom:8px}
.step .body{display:block;color:var(--muted);font:400 14px/1.5 var(--font)}
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
<nav class="nav"><div class="wrap"><a class="brand" href="#">Falsify</a><div class="links"><a href="#system" data-i18n="nav_system">System</a><a href="#examples" data-i18n="nav_examples">Examples</a><a href="#start" data-i18n="nav_start">Get started</a><a href="https://github.com/shi275773124/Falsify">GitHub</a><button class="lang-btn" id="lang-btn" onclick="toggleLang()">中文</button></div></div></nav>
<main>
<header class="wrap hero">
  <div>
    <div class="eyebrow" data-i18n="eyebrow">Adversarial review framework</div>
    <h1 data-i18n="h1">Stop trusting confident AI.</h1>
    <p class="sub" data-i18n="hero_sub">Falsify is an adversarial review framework for AI-generated code, research, and production decisions.</p>
    <div class="actions"><a class="btn primary" href="#start" data-i18n="btn_start">Get started</a><a class="btn ghost" href="https://github.com/shi275773124/Falsify" data-i18n="btn_github">View on GitHub</a></div>
    <div class="markers"><span class="marker">PASS / PASS_WITH_DEBT / BLOCK</span><span class="marker" data-i18n="m1">3-layer review stack</span><span class="marker" data-i18n="m2">Evidence-first decisions</span></div>
  </div>
  <div class="field" role="img" aria-label="Falsify audit field">
    <div class="claim"><b data-i18n="field_claim_title">Confident claim</b><p data-i18n="field_claim_body">"Deployment succeeded. Logs completed. Another AI reviewed it."</p></div>
    <div class="strip"><span class="ok">$ job completed</span><span class="bad" data-i18n="strip_state">state: not verified</span><span>finish_reason: missing</span><span>parse_status: missing</span></div>
    <div class="lane evidence"><b data-i18n="field_evidence">Evidence</b><p data-i18n="field_evidence_sub">Raw artifacts, readable diffs, command output, source links.</p></div>
    <div class="lane assumptions"><b data-i18n="field_assumptions">Assumptions</b><p data-i18n="field_assumptions_sub">What must be true for the decision to hold.</p></div>
    <div class="lane failures"><b data-i18n="field_failures">Failure modes</b><p data-i18n="field_failures_sub">False truth, false risk, silent failure, permission drift.</p></div>
    <div class="verdicts"><div class="v pass">PASS</div><div class="v debt">PASS_WITH_DEBT</div><div class="v block">BLOCK</div></div>
  </div>
</header>

<section><div class="wrap section-head"><h2 data-i18n="s1_h2">False confidence got cheaper.</h2><p class="lead" data-i18n="s1_lead">AI made teams faster. It also made polished wrongness easier to ship: green logs, second-model agreement, passing tests that checked the wrong thing, and summaries that replaced raw evidence.</p></div></section>

<section id="system"><div class="wrap">
  <div class="section-head"><h2 data-i18n="s2_h2">The system</h2><p class="lead" data-i18n="s2_lead">Falsify = Brooks-Lint + Adversarial Review + Risk Scalpel.</p></div>
  <div class="grid">
    <div class="card"><h3 data-i18n="card_bl_h3">Brooks-Lint</h3><ul><li data-i18n="bl_1">hidden state</li><li data-i18n="bl_2">implicit authority</li><li data-i18n="bl_3">duplicated control paths</li><li data-i18n="bl_4">brittle rollback</li><li data-i18n="bl_5">unverifiable acceptance</li><li data-i18n="bl_6">AI summaries replacing raw evidence</li></ul></div>
    <div class="card"><h3 data-i18n="card_ar_h3">Adversarial Review</h3><ul><li data-i18n="ar_1">false truth</li><li data-i18n="ar_2">false risk</li><li data-i18n="ar_3">silent failure</li><li data-i18n="ar_4">stale data</li><li data-i18n="ar_5">permission drift</li><li data-i18n="ar_6">semantic nudges toward PASS</li><li data-i18n="ar_7">monitor failure laundering</li></ul></div>
    <div class="card"><h3 data-i18n="card_rs_h3">Risk Scalpel</h3><ul><li data-i18n="rs_1">Must Fix: blocks the current decision</li><li data-i18n="rs_2">Known Debt: real risk with a trigger</li><li data-i18n="rs_3">Delete: no concrete current failure mode</li></ul></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="section-head"><h2 data-i18n="s3_h2">Fake proof is not proof.</h2><p class="lead" data-i18n="s3_lead">Falsify does not ask whether another model sounded confident. It asks what evidence survives attack.</p></div>
  <div class="compare">
    <div><b data-i18n="cmp_l1">"The model said it is fine."</b></div><div><strong data-i18n="cmp_r1">Where is the raw artifact?</strong></div>
    <div><b data-i18n="cmp_l2">"Another AI reviewed it."</b></div><div><strong data-i18n="cmp_r2">Did it check the failure mode or just agree?</strong></div>
    <div><b data-i18n="cmp_l3">"The logs look successful."</b></div><div><strong data-i18n="cmp_r3">Did the actual state change?</strong></div>
    <div><b data-i18n="cmp_l4">"The output is empty, so no issue."</b></div><div><strong data-i18n="cmp_r4">Was it truncated, filtered, or unparsable?</strong></div>
    <div><b data-i18n="cmp_l5">"This is only theoretical."</b></div><div><strong data-i18n="cmp_r5">Can it affect the current decision?</strong></div>
    <div><b data-i18n="cmp_l6">"We should add a big safety checklist."</b></div><div><strong data-i18n="cmp_r6">What is the minimal blocking fix?</strong></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="section-head"><h2 data-i18n="s4_h2">Workflow</h2><p class="lead" data-i18n="s4_lead">Input a claim. Attack assumptions, evidence, failure modes, and acceptance criteria. Cut findings. Return a decision.</p></div>
  <div class="flow">
    <div class="step"><span class="lbl" data-i18n="step1_label">INPUT</span><span class="body" data-i18n="step1_body">code, report, deployment claim, AI output, research conclusion</span></div>
    <div class="step"><span class="lbl" data-i18n="step2_label">ATTACK</span><span class="body" data-i18n="step2_body">assumptions, evidence, failure modes, acceptance criteria</span></div>
    <div class="step"><span class="lbl" data-i18n="step3_label">CUT</span><span class="body" data-i18n="step3_body">Must Fix, Known Debt, Delete</span></div>
    <div class="step"><span class="lbl" data-i18n="step4_label">OUTPUT</span><span class="body" data-i18n="step4_body">PASS, PASS_WITH_DEBT, BLOCK</span></div>
  </div>
</div></section>

<section id="examples"><div class="wrap">
  <div class="section-head"><h2 data-i18n="s5_h2">Examples</h2><p class="lead" data-i18n="s5_lead">Synthetic examples, not customer cases.</p></div>
  <div class="grid">
    <div class="card"><h3 data-i18n="ex1_h3">Deployment logs</h3><p data-i18n="ex1_p">Normal review says deployment succeeded because logs completed. Falsify blocks because logs prove something ran; they do not prove the system is in the intended state.</p></div>
    <div class="card"><h3 data-i18n="ex2_h3">Prompt injection</h3><p data-i18n="ex2_p">Normal AI review says no issue found. Falsify requires raw output, parse status, finish_reason, usage/token counts when available, and known-pattern or reproducer evidence.</p></div>
    <div class="card"><h3 data-i18n="ex3_h3">Twenty risks</h3><p data-i18n="ex3_p">Normal audit lists everything. Falsify cuts each finding into Must Fix, Known Debt, or Delete so the decision is not buried in generic TODOs.</p></div>
  </div>
</div></section>

<section id="start"><div class="wrap">
  <div class="section-head"><h2 data-i18n="s6_h2">Get started</h2><p class="lead" data-i18n="s6_lead">Use the CLI locally, run the deterministic fixture demo, or start the real paste-and-go web reviewer with your configured provider key.</p></div>
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
  <div class="section-head"><h2 data-i18n="s7_h2">Try the local reviewer</h2><p class="lead" data-i18n="s7_lead">This calls the configured backend. It is not a fake analysis. Without an API key or provider config, it will return a setup error.</p></div>
  <div class="demo">
    <div><textarea id="t">Deployment succeeded because the logs completed. Another AI reviewed it and found no issue. The prompt-injection audit is covered by a checklist. No raw verdict, parse status, finish_reason, or usage counts were kept.</textarea><div class="row"><select id="s"><option value="general" data-i18n="scenario_general">General</option><option value="code" data-i18n="scenario_code">Code / PR</option><option value="research" data-i18n="scenario_research">Research</option><option value="production" data-i18n="scenario_production">Production</option></select><button class="btn primary" id="b" onclick="go()" data-i18n="btn_review">Run review</button></div></div>
    <div class="result" id="out"><span class="badge BLOCK">Example shape: BLOCK</span><div class="risk"><small>Must Fix</small>Logs are not state verification. Attach a read-after-write or invariant check.</div></div>
  </div>
</div></section>

<section><div class="wrap section-head"><h2 data-i18n="s8_h2">Follow the work</h2><p class="lead" data-i18n="s8_lead">Falsify is evolving with real AI-agent, code review, and production-risk workflows. If you are working on similar problems, feel free to follow along or reach out.<br><br><a href="https://github.com/shi275773124/Falsify">GitHub</a> · <a href="https://x.com/aishikejian">X / Twitter</a> · <a href="mailto:chrisshi168@icloud.com">Email</a></p></div></section>
</main>
<footer><div class="wrap"><div>Falsify</div><div><a href="https://github.com/shi275773124/Falsify">GitHub</a> · <a href="https://x.com/aishikejian">X / Twitter</a> · <a href="mailto:chrisshi168@icloud.com">Email</a> · <a href="../LICENSE">License</a></div></div></footer>
<script>
const T={
en:{
nav_system:"System",nav_examples:"Examples",nav_start:"Get started",
eyebrow:"Adversarial review framework",
h1:"Stop trusting confident AI.",
hero_sub:"Falsify is an adversarial review framework for AI-generated code, research, and production decisions.",
btn_start:"Get started",btn_github:"View on GitHub",
m1:"3-layer review stack",m2:"Evidence-first decisions",
field_claim_title:"Confident claim",
field_claim_body:"\"Deployment succeeded. Logs completed. Another AI reviewed it.\"",
strip_state:"state: not verified",
field_evidence:"Evidence",field_evidence_sub:"Raw artifacts, readable diffs, command output, source links.",
field_assumptions:"Assumptions",field_assumptions_sub:"What must be true for the decision to hold.",
field_failures:"Failure modes",field_failures_sub:"False truth, false risk, silent failure, permission drift.",
s1_h2:"False confidence got cheaper.",
s1_lead:"AI made teams faster. It also made polished wrongness easier to ship: green logs, second-model agreement, passing tests that checked the wrong thing, and summaries that replaced raw evidence.",
s2_h2:"The system",s2_lead:"Falsify = Brooks-Lint + Adversarial Review + Risk Scalpel.",
card_bl_h3:"Brooks-Lint",card_ar_h3:"Adversarial Review",card_rs_h3:"Risk Scalpel",
bl_1:"hidden state",bl_2:"implicit authority",bl_3:"duplicated control paths",bl_4:"brittle rollback",bl_5:"unverifiable acceptance",bl_6:"AI summaries replacing raw evidence",
ar_1:"false truth",ar_2:"false risk",ar_3:"silent failure",ar_4:"stale data",ar_5:"permission drift",ar_6:"semantic nudges toward PASS",ar_7:"monitor failure laundering",
rs_1:"Must Fix: blocks the current decision",rs_2:"Known Debt: real risk with a trigger",rs_3:"Delete: no concrete current failure mode",
s3_h2:"Fake proof is not proof.",s3_lead:"Falsify does not ask whether another model sounded confident. It asks what evidence survives attack.",
cmp_l1:"\"The model said it is fine.\"",cmp_r1:"Where is the raw artifact?",
cmp_l2:"\"Another AI reviewed it.\"",cmp_r2:"Did it check the failure mode or just agree?",
cmp_l3:"\"The logs look successful.\"",cmp_r3:"Did the actual state change?",
cmp_l4:"\"The output is empty, so no issue.\"",cmp_r4:"Was it truncated, filtered, or unparsable?",
cmp_l5:"\"This is only theoretical.\"",cmp_r5:"Can it affect the current decision?",
cmp_l6:"\"We should add a big safety checklist.\"",cmp_r6:"What is the minimal blocking fix?",
s4_h2:"Workflow",s4_lead:"Input a claim. Attack assumptions, evidence, failure modes, and acceptance criteria. Cut findings. Return a decision.",
step1_label:"INPUT",step1_body:"code, report, deployment claim, AI output, research conclusion",
step2_label:"ATTACK",step2_body:"assumptions, evidence, failure modes, acceptance criteria",
step3_label:"CUT",step3_body:"Must Fix, Known Debt, Delete",
step4_label:"OUTPUT",step4_body:"PASS, PASS_WITH_DEBT, BLOCK",
s5_h2:"Examples",s5_lead:"Synthetic examples, not customer cases.",
ex1_h3:"Deployment logs",ex1_p:"Normal review says deployment succeeded because logs completed. Falsify blocks because logs prove something ran; they do not prove the system is in the intended state.",
ex2_h3:"Prompt injection",ex2_p:"Normal AI review says no issue found. Falsify requires raw output, parse status, finish_reason, usage/token counts when available, and known-pattern or reproducer evidence.",
ex3_h3:"Twenty risks",ex3_p:"Normal audit lists everything. Falsify cuts each finding into Must Fix, Known Debt, or Delete so the decision is not buried in generic TODOs.",
s6_h2:"Get started",s6_lead:"Use the CLI locally, run the deterministic fixture demo, or start the real paste-and-go web reviewer with your configured provider key.",
s7_h2:"Try the local reviewer",s7_lead:"This calls the configured backend. It is not a fake analysis. Without an API key or provider config, it will return a setup error.",
scenario_general:"General",scenario_code:"Code / PR",scenario_research:"Research",scenario_production:"Production",
btn_review:"Run review",
s8_h2:"Follow the work",s8_lead:"Falsify is evolving with real AI-agent, code review, and production-risk workflows. If you are working on similar problems, feel free to follow along or reach out.<br><br><a href=\"https://github.com/shi275773124/Falsify\">GitHub</a> \xb7 <a href=\"https://x.com/aishikejian\">X / Twitter</a> \xb7 <a href=\"mailto:chrisshi168@icloud.com\">Email</a>",
},
zh:{
nav_system:"系统",nav_examples:"示例",nav_start:"快速开始",
eyebrow:"对抗性审查框架",
h1:"别再信任自信满满的 AI。",
hero_sub:"Falsify 是一个针对 AI 生成代码、研究报告和生产决策的对抗性审查框架。",
btn_start:"快速开始",btn_github:"查看 GitHub",
m1:"三层审查栈",m2:"证据优先决策",
field_claim_title:"自信断言",
field_claim_body:"\"部署成功。日志已完成。另一个 AI 审核过了。\"",
strip_state:"状态：未验证",
field_evidence:"证据",field_evidence_sub:"原始产物、可读差异、命令输出、来源链接。",
field_assumptions:"假设",field_assumptions_sub:"决策成立所需满足的前提条件。",
field_failures:"失效模式",field_failures_sub:"虚假事实、虚假风险、静默失败、权限漂移。",
s1_h2:"虚假自信变得越来越廉价。",
s1_lead:"AI 让团队更快，也让精心包装的错误更容易被交付：绳色日志、第二个模型的附议、检查了错误东西的通过测试，以及替代原始证据的摘要。",
s2_h2:"系统",s2_lead:"Falsify = Brooks-Lint + 对抗性审查 + 风险手术刀。",
card_bl_h3:"Brooks-Lint",card_ar_h3:"对抗性审查",card_rs_h3:"风险手术刀",
bl_1:"隐藏状态",bl_2:"隐性权威",bl_3:"重复控制路径",bl_4:"脂性回滚",bl_5:"不可验证的验收",bl_6:"AI 摘要替代原始证据",
ar_1:"虚假事实",ar_2:"虚假风险",ar_3:"静默失败",ar_4:"过期数据",ar_5:"权限漂移",ar_6:"向 PASS 倾斜的语义暗示",ar_7:"监控失败洗白",
rs_1:"必须修复：阻断当前决策",rs_2:"已知债务：有触发条件的真实风险",rs_3:"删除：没有具体的当前失效场景",
s3_h2:"假证明不是证明。",s3_lead:"Falsify 不问另一个模型听起来是否自信，它问的是什么证据能经受攻击。",
cmp_l1:"\"模型说没问题。\"",cmp_r1:"原始产物在哪里？",
cmp_l2:"\"另一个 AI 审核过了。\"",cmp_r2:"它检查了具体失效模式，还是只是表示认同？",
cmp_l3:"\"日志看起来成功了。\"",cmp_r3:"实际状态改变了吗？",
cmp_l4:"\"输出为空，说明没问题。\"",cmp_r4:"是被截断、过滤，还是无法解析？",
cmp_l5:"\"这只是理论上的风险。\"",cmp_r5:"它会影响当前决策吗？",
cmp_l6:"\"我们应该加一个大的安全检查清单。\"",cmp_r6:"最小阻断性修复是什么？",
s4_h2:"工作流",s4_lead:"输入一个断言。攻击假设、证据、失效模式和验收标准。裁剪发现。返回决策。",
step1_label:"输入",step1_body:"代码、报告、部署声明、AI 输出、研究结论",
step2_label:"攻击",step2_body:"假设、证据、失效模式、验收标准",
step3_label:"裁剪",step3_body:"必须修复、已知债务、删除",
step4_label:"输出",step4_body:"PASS、PASS_WITH_DEBT、BLOCK",
s5_h2:"示例",s5_lead:"合成示例，非真实客户案例。",
ex1_h3:"部署日志",ex1_p:"普通审查说部署成功因为日志完成了。Falsify 阻断，因为日志只证明某个东西运行了，并不证明系统处于预期状态。",
ex2_h3:"提示词注入",ex2_p:"普通 AI 审查说未发现问题。Falsify 要求原始输出、解析状态、finish_reason、usage/token 数（如有），以及已知模式或复现证据。",
ex3_h3:"二十个风险",ex3_p:"普通审计列出所有内容。Falsify 将每个发现裁剪为必须修复、已知债务或删除，让决策不被淩浸在通用 TODO 里。",
s6_h2:"快速开始",s6_lead:"在本地使用 CLI，运行确定性 fixture 演示，或使用你配置的 provider key 启动真实的粘贴即用 Web 审查器。",
s7_h2:"试用本地审查器",s7_lead:"这里调用的是已配置的后端，不是假分析。没有 API key 或 provider 配置时，会返回设置错误。",
scenario_general:"通用",scenario_code:"代码 / PR",scenario_research:"研究",scenario_production:"生产环境",
btn_review:"运行审查",
s8_h2:"关注进展",s8_lead:"Falsify 正在随真实的 AI-agent、代码审查和生产风险工作流持续演进。如果你在做类似的事，欢迎关注或联系。<br><br><a href=\"https://github.com/shi275773124/Falsify\">GitHub</a> \xb7 <a href=\"https://x.com/aishikejian\">X / Twitter</a> \xb7 <a href=\"mailto:chrisshi168@icloud.com\">Email</a>",
}};
let lang='en';
function toggleLang(){
  lang=lang==='en'?'zh':'en';
  document.getElementById('lang-btn').textContent=lang==='en'?'中文':'EN';
  document.querySelectorAll('[data-i18n]').forEach(el=>{
    const k=el.getAttribute('data-i18n');
    if(T[lang][k]!==undefined)el.innerHTML=T[lang][k];
  });
}
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
