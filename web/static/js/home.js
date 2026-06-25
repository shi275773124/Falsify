const PUBLIC_COPY = [
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
  "Real backend, not fake analysis.",
  "Frame Audit",
  "框架审",
  "hidden state / implicit authority",
  "false truth / false risk",
  "prompt-only audit theater",
  "monitor-failure laundering",
  "Hosted org policy",
  "托管组织 policy",
  "Self-hosted · unlimited repos",
  "自托管 · 仓库不限",
];

const SAMPLES = {
  general: {
    verdict: "BLOCK",
    risks: [
      { cutline: "Must Fix", issue: "Claim reads confident but cites no raw artifact.", minimal_action: "Attach source output, command log, or reproducible check." },
      { cutline: "Known Debt", issue: "Secondary review mentioned but not independently verified.", minimal_action: "Re-run with explicit failure-mode checklist.", upgrade_trigger: "Before any customer-facing decision." },
    ],
  },
  code: {
    verdict: "PASS_WITH_DEBT",
    risks: [
      { cutline: "Known Debt", issue: "Tests pass but do not assert the risky default path.", minimal_action: "Add one negative test for the default branch.", upgrade_trigger: "Before merge to main." },
    ],
  },
  research: {
    verdict: "BLOCK",
    risks: [
      { cutline: "Must Fix", issue: "Conclusion cites summary tables without primary source excerpt.", minimal_action: "Attach table screenshot or raw CSV hash." },
    ],
  },
  production: {
    verdict: "BLOCK",
    risks: [
      { cutline: "Must Fix", issue: "Logs completed, but no read-after-write or invariant check proves intended state.", minimal_action: "Attach post-deploy probe output and rollback command." },
      { cutline: "Delete", issue: "Another AI reviewed it — not evidence.", minimal_action: "Remove from acceptance chain." },
    ],
  },
};

const T = {
  en: {
    nav_layers: "Layers",
    nav_artifact: "Sample",
    nav_demo: "Demo",
    nav_docs: "Docs",
    h1: "Looks right is not enough.",
    hero_sub: "Falsify turns confident AI output into a shipping decision:\nPASS, PASS_WITH_DEBT, or BLOCK — backed by raw evidence.",
    hero_definition: "Full Falsify = Frame Audit + Adversarial Review + Cutline. Miss a layer, you only have a partial review.",
    hero_workbench_note: "Protocol is three-layer. The public workbench below shows verdict format and adversarial samples — not machine-enforced Frame Audit or Cutline.",
    btn_install: "Install GitHub Action",
    btn_run_sample_hero: "Run sample",
    trust_github: "GitHub Actions",
    trust_mit: "MIT (core)",
    trust_byok: "BYOK",
    trust_schema: "falsify.review.v1",
    preview_label: "Review output",
    preview_title: "Deployment succeeded because logs completed.",
    preview_must_fix: "Must Fix",
    preview_issue: "Logs are treated as state verification",
    preview_action: "Minimal action: Add read-after-write probe",
    gate_frame: "Frame",
    gate_adv: "Evidence",
    gate_cut: "Cutline",
    gate_verdict: "Verdict",
    gate_pass: "PASS",
    ev1_val: "< 1 day",
    ev1_lbl: "Time to first useful BLOCK",
    ev2_val: "3 verdicts",
    ev2_lbl: "PASS / PASS_WITH_DEBT / BLOCK only",
    ev3_val: "MIT",
    proof_action: "GitHub Action · open core",
    proof_github: "GitHub",
    proof_case_val: "Logs ≠ state proof",
    proof_case_lbl: "Real BLOCK · reports/deploy.md",
    hero_img_alt: "Falsify BLOCK review: logs treated as state verification on reports/deploy.md",
    quote_p: "\"Green logs aren't proof. We stopped pretending they were.\"",
    quote_cite: "Chris Shi",
    hero_layers_hook: "AI made fake proof cheap.",
    hero_layers_intro: "Falsify runs three layers.",
    hero_layers_l1_tag: "Frame",
    hero_layers_l1_map: "Frame Audit",
    hero_layers_l1_body: "hidden state, authority drift, missing rollback.",
    hero_layers_l2_tag: "Evidence",
    hero_layers_l2_map: "Adversarial Review",
    hero_layers_l2_body: "false facts, fake acceptance, audit theater.",
    hero_layers_l3_tag: "Cutline",
    hero_layers_l3_body: "must fix, known debt, delete.",
    hero_layers_close: "Three verdicts only.",
    hero_layers_verdicts: "PASS / PASS_WITH_DEBT / BLOCK",
    bl_label: "Layer 01",
    ar_label: "Layer 02",
    rs_label: "Layer 03",
    rs_lead: "Decides what blocks now — not a laundry list of every risk.",
    artifact_tag: "Artifact",
    artifact_h2: "Real BLOCK report.",
    artifact_lead: "Sample JSON from the protocol — not a fabricated GitHub check mock.",
    artifact_download: "Download JSON",
    antipattern_tag: "Not Falsify",
    antipattern_h2: "Looks like review. Is not full Falsify.",
    antipattern_lead: "Partial checks masquerade as complete review.",
    ap_1: "\"A second glance\" ≠ full Falsify",
    ap_2: "Cutline-only ≠ full Falsify",
    ap_3: "Every smell as Must Fix ≠ Cutline",
    workbench_summary: "Open workbench",
    try_lead: "Preview verdict format here. Samples are fixed adversarial demos; live review is one LLM call with your local key — not full Falsify.",
    input_h3: "Claim",
    input_p: "Paste a deployment claim, PR summary, or AI-generated report.",
    output_h3: "Verdict",
    output_p: "Hit Run sample to preview the decision artifact.",
    demo_note: "Partial layer only. Canned samples are adversarial demos — not full Falsify. Live /review is a single LLM pass with your local key; no Frame Audit gate, no machine Cutline.",
    workbench_scope: "Full stack: CLI + GitHub Action. This page demonstrates output shape, not enforcement.",
    scenario_general: "General",
    scenario_code: "Code / PR",
    scenario_research: "Research",
    scenario_production: "Production",
    btn_sample: "Run sample",
    btn_review: "Live review",
    start_tag: "Start",
    start_h2: "Run it locally in 60 seconds.",
    docs_install: "Install GitHub Action (5 min) →",
    boundary_tag: "Boundary",
    boundary_h2: "Falsify classifies risk. It does not authorize action.",
    boundary_p: "Live money, production config, cron, gateway, and external send still require independent final judgment. Self-review is not independent review.",
    licensing_p: "MIT covers the protocol, CLI, JSON schema, workflow templates, and local artifacts. Team covers hosted policy enforcement, report retention, org rollout, and managed integrations — not a second copy of the OSS templates.",
    licensing_link: "Read the full open core boundary →",
    licensing_tag: "Open core",
    bl_h3: "Frame Audit",
    ar_h3: "Adversarial Review",
    rs_h3: "Cutline",
    bl_1: "hidden state / implicit authority",
    bl_2: "owner / lock / lifecycle",
    bl_4: "rollback / verification path",
    ar_1: "false truth / false risk",
    ar_5: "prompt-only audit theater",
    ar_6: "monitor-failure laundering",
    rs_1: "Must Fix",
    rs_2: "Known Debt",
    rs_3: "Delete",
    hero_chip_1: "Frame Audit",
    hero_chip_2: "Adversarial Review",
    hero_chip_3: "Cutline",
    lic_open_2: "MIT — self-hosted, unlimited repos",
    lic_team_2: "Team — org workspace, not OSS overlap",
  },
  zh: {
    nav_layers: "三层",
    nav_artifact: "样例",
    nav_demo: "演示",
    nav_docs: "文档",
    h1: "看起来对，不够。",
    hero_sub: "Falsify 把 AI 的自信输出变成上线决策：\nPASS、PASS_WITH_DEBT、BLOCK — 以原始证据为准。",
    hero_definition: "完整 Falsify = 框架审 + 对抗审 + Cutline；缺任一层，只是局部审查。",
    hero_workbench_note: "协议是三层。下方公网工作台只演示裁决格式与对抗审样例 — 非机审框架审，非机审 Cutline。",
    btn_install: "安装 GitHub Action",
    btn_run_sample_hero: "运行样例",
    trust_github: "GitHub Actions",
    trust_mit: "MIT（核心）",
    trust_byok: "BYOK",
    trust_schema: "falsify.review.v1",
    preview_label: "审查输出",
    preview_title: "部署成功，因为日志跑完了。",
    preview_must_fix: "Must Fix",
    preview_issue: "日志被当作状态验证",
    preview_action: "最小动作：添加 read-after-write 探针",
    gate_frame: "结构",
    gate_adv: "证据",
    gate_cut: "边界",
    gate_verdict: "裁决",
    gate_pass: "PASS",
    ev1_val: "< 1 天",
    ev1_lbl: "首次有效 BLOCK",
    ev2_val: "3 种裁决",
    ev2_lbl: "仅 PASS / PASS_WITH_DEBT / BLOCK",
    ev3_val: "MIT",
    proof_action: "GitHub Action · 开源核心",
    proof_github: "GitHub",
    proof_case_val: "日志 ≠ 状态证明",
    proof_case_lbl: "真实 BLOCK · reports/deploy.md",
    hero_img_alt: "Falsify BLOCK 审查：reports/deploy.md 上日志被当作状态验证",
    quote_p: "「日志绿了，不等于证据成立。我们不再假装它算数。」",
    quote_cite: "史可鉴",
    hero_layers_hook: "AI 让假证明变便宜了。",
    hero_layers_intro: "Falsify 走三层。",
    hero_layers_l1_tag: "审结构",
    hero_layers_l1_map: "框架审",
    hero_layers_l1_body: "隐式状态、越权路径、回滚缺失。",
    hero_layers_l2_tag: "审证据",
    hero_layers_l2_map: "对抗审",
    hero_layers_l2_body: "假事实、假验收、审计作秀。",
    hero_layers_l3_tag: "裁边界",
    hero_layers_l3_body: "必须修、可以欠、该删。",
    hero_layers_close: "走完，只落三档裁决。",
    hero_layers_verdicts: "PASS / PASS_WITH_DEBT / BLOCK",
    bl_label: "第一层",
    ar_label: "第二层",
    rs_label: "第三层",
    rs_lead: "决定当下什么阻塞，不是罗列全部风险。",
    artifact_tag: "产物",
    artifact_h2: "真实 BLOCK 报告。",
    artifact_lead: "协议样例 JSON — 不是捏造的 GitHub Check 界面。",
    artifact_download: "下载 JSON",
    antipattern_tag: "不是 Falsify",
    antipattern_h2: "像审查，不是完整 Falsify。",
    antipattern_lead: "局部检查冒充完整审查。",
    ap_1: "「再看一眼」≠ 完整 Falsify",
    ap_2: "只有 Cutline ≠ 完整 Falsify",
    ap_3: "每个 smell 都是 Must Fix ≠ Cutline",
    workbench_summary: "打开工作台",
    try_lead: "在此预览裁决格式。样例为固定对抗审样例；真审查为单次模型调用、本地 key — 不是完整 Falsify。",
    input_h3: "声明",
    input_p: "粘贴部署声明、PR 摘要或 AI 生成报告。",
    output_h3: "裁决",
    output_p: "点「运行样例」预览裁决。",
    demo_note: "局部层演示。样例为固定对抗审样例，不是完整 Falsify。真 /review 为单次模型调用、本地 key；无框架审闸门，无机审 Cutline。",
    workbench_scope: "完整协议：CLI + GitHub Action。本页只演示输出形态，不做强制。",
    scenario_general: "通用",
    scenario_code: "代码 / PR",
    scenario_research: "研究",
    scenario_production: "生产",
    btn_sample: "运行样例",
    btn_review: "真审查",
    start_tag: "开始",
    start_h2: "60 秒本地跑起来。",
    docs_install: "5 分钟安装 GitHub Action →",
    boundary_tag: "边界",
    boundary_h2: "Falsify 只做风险分类，不做执行授权。",
    boundary_p: "真实资金、生产配置、cron、网关与外部发送仍需独立终审。自己审自己不算独立判断。",
    licensing_p: "MIT 覆盖协议、CLI、JSON schema、工作流模板与本地产物。Team 覆盖托管 policy 执行、报告留存、组织落地与托管集成 — 不是 OSS 模板的第二份拷贝。",
    licensing_link: "阅读完整 Open Core 边界 →",
    licensing_tag: "开源核心",
    bl_h3: "框架审",
    ar_h3: "对抗审",
    rs_h3: "Cutline",
    bl_1: "隐藏状态与隐式授权",
    bl_2: "归属、锁与生命周期",
    bl_4: "回滚与验证路径",
    ar_1: "虚假事实与虚假风险",
    ar_5: "提示词作秀",
    ar_6: "监控洗白",
    rs_1: "Must Fix",
    rs_2: "Known Debt",
    rs_3: "Delete",
    hero_chip_1: "框架审",
    hero_chip_2: "对抗审",
    hero_chip_3: "Cutline",
    lic_open_2: "MIT — 自托管，仓库不限",
    lic_team_2: "Team — 组织工作区，不与 OSS 重叠",
  },
};

const STORAGE_KEY = "falsify-lang";

function readStoredLang() {
  try {
    return localStorage.getItem(STORAGE_KEY) === "zh" ? "zh" : "en";
  } catch (_e) {
    return "en";
  }
}

function writeStoredLang(next) {
  try {
    localStorage.setItem(STORAGE_KEY, next);
  } catch (_e) {
    /* ignore */
  }
}

let lang = readStoredLang();

function applyLang() {
  const isZh = lang === "zh";
  document.documentElement.lang = isZh ? "zh-CN" : "en";
  document.documentElement.classList.toggle("lang-zh", isZh);
  document.body.classList.toggle("lang-zh", isZh);
  document.getElementById("lang-btn").textContent = lang === "en" ? "中文" : "EN";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const k = el.getAttribute("data-i18n");
    if (T[lang][k] === undefined) return;
    const v = T[lang][k];
    if (k === "hero_sub") el.innerHTML = v.replace(/\n/g, "<br>");
    else el.textContent = v;
  });
  document.querySelectorAll("[data-i18n-alt]").forEach((el) => {
    const k = el.getAttribute("data-i18n-alt");
    if (T[lang][k] !== undefined) el.alt = T[lang][k];
  });
}

function toggleLang() {
  lang = lang === "en" ? "zh" : "en";
  writeStoredLang(lang);
  applyLang();
}

function esc(s) {
  return String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

function renderVerdict(d) {
  let h = '<span class="badge ' + d.verdict + '">' + d.verdict + "</span>";
  for (const x of d.risks || []) {
    h += '<div class="risk"><small>' + esc(x.cutline || x.severity || "Finding") + "</small>" + esc(x.issue || "") + "<br><em>" + esc(x.minimal_action || "") + "</em>";
    if (x.upgrade_trigger) {
      h += "<br><em>" + (lang === "zh" ? "升级触发：" : "Upgrade trigger: ") + esc(x.upgrade_trigger) + "</em>";
    }
    h += "</div>";
  }
  return h;
}

function runSample() {
  const sc = document.getElementById("s").value;
  document.getElementById("out").innerHTML = "<h3>" + (lang === "zh" ? "裁决" : "Verdict") + "</h3>" + renderVerdict(SAMPLES[sc] || SAMPLES.production);
}

async function go() {
  const t = document.getElementById("t").value.trim();
  const out = document.getElementById("out");
  const b = document.getElementById("b");
  if (!t) {
    out.innerHTML = "<p>Paste something first.</p>";
    return;
  }
  b.disabled = true;
  out.innerHTML = "<p>Reviewing...</p>";
  try {
    const r = await fetch("/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: t, scenario: document.getElementById("s").value }),
    });
    const d = await r.json();
    if (d.error) {
      out.innerHTML =
        "<h3>" + (lang === "zh" ? "裁决" : "Verdict") + "</h3><p>" + esc(d.error) + "</p><p><button class=\"btn ghost\" type=\"button\" id=\"fallback-sample\">" + (lang === "zh" ? "改用样例" : "Use sample instead") + "</button></p>";
      document.getElementById("fallback-sample").onclick = runSample;
      b.disabled = false;
      return;
    }
    if (d.raw) {
      out.innerHTML = '<span class="badge ' + d.verdict + '">' + d.verdict + "</span><pre>" + esc(d.raw) + "</pre>";
      b.disabled = false;
      return;
    }
    out.innerHTML = "<h3>" + (lang === "zh" ? "裁决" : "Verdict") + "</h3>" + renderVerdict(d);
  } catch (e) {
    out.innerHTML = "<p>" + esc(String(e)) + "</p>";
  }
  b.disabled = false;
}

function initNav() {
  const toggle = document.getElementById("nav-toggle");
  const links = document.getElementById("nav-links");
  if (!toggle || !links) return;
  toggle.addEventListener("click", () => {
    const open = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });
}

document.getElementById("lang-btn").addEventListener("click", toggleLang);
document.getElementById("btn-sample").addEventListener("click", runSample);
document.getElementById("b").addEventListener("click", go);
initNav();
applyLang();
