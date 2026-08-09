const SAMPLES = {
  general: {
    verdict: "BLOCK",
    risks: [
      {
        cutline: "Must Fix",
        issue: "Claim reads confident but cites no raw artifact.",
        minimal_action: "Attach source output, command log, or reproducible check.",
      },
      {
        cutline: "Known Debt",
        issue: "Secondary review mentioned but not independently verified.",
        minimal_action: "Re-run with explicit failure-mode checklist.",
        upgrade_trigger: "Before any customer-facing decision.",
      },
    ],
  },
  code: {
    verdict: "PASS_WITH_DEBT",
    risks: [
      {
        cutline: "Known Debt",
        issue: "Tests pass but do not assert the risky default path.",
        minimal_action: "Add one negative test for the default branch.",
        upgrade_trigger: "Before merge to main.",
      },
    ],
  },
  research: {
    verdict: "BLOCK",
    risks: [
      {
        cutline: "Must Fix",
        issue: "Conclusion cites summary tables without primary source excerpt.",
        minimal_action: "Attach table screenshot or raw CSV hash.",
      },
    ],
  },
  production: {
    verdict: "BLOCK",
    risks: [
      {
        cutline: "Must Fix",
        issue: "Logs completed, but no read-after-write or invariant check proves intended state.",
        minimal_action: "Attach post-deploy probe output and rollback command.",
      },
      {
        cutline: "Delete",
        issue: "Another AI reviewed it is not evidence.",
        minimal_action: "Remove from acceptance chain.",
      },
    ],
  },
};

// Product homepage copy — general false-green first; open core; no portfolio.
const T = {
  en: {
    nav_menu: "Menu",
    nav_how: "How",
    nav_proof: "Proof",
    nav_try: "Try",
    nav_docs: "Docs",
    nav_skills: "Skills",
    nav_rootfix: "ROOTFIX",
    hero_eyebrow: "Two pains · three layers",
    h1: "Looks green isn't proof.",
    hero_sub:
      "AI hallucination and false-green need adversarial review. Long-term rot and over-engineering need framework review plus Cutline. Then a sign-off: PASS, PASS_WITH_DEBT, or BLOCK.",
    hero_io:
      "In: claim + evidence pack · Out: falsify.review.v1 JSON you can keep, diff, and re-run.",
    hero_step_1_k: "Adversarial",
    hero_step_1: " — red-teams \"looks fine\" (false-green, AI hallucination)",
    hero_step_2_k: "Framework",
    hero_step_2: " — catches what will rot later (structure, over-engineering)",
    hero_step_3_k: "Cutline",
    hero_step_3: " — Must Fix / Debt / Delete, then PASS / PASS_WITH_DEBT / BLOCK",
    hero_claiming:
      "Sign-off only. Does not deploy or trade for you. Installing a skill is not Claiming Falsify — keep the artifact.",
    btn_see_proof: "See proof",
    btn_run_sample_hero: "See a real BLOCK artifact",
    btn_try_demo: "Run 60s demo",
    btn_install_skill: "Install locally",
    btn_install: "GitHub Action",
    btn_sample: "Run example",
    btn_review: "Review my claim",
    trust_band_github: "GitHub",
    trust_mit: "MIT (open core)",
    trust_byok: "No Falsify key · BYOK",
    trust_pro: "Pro enforcement closed",
    trust_schema: "falsify.review.v1",
    hero_skill_install: "Deploy claim",
    hero_skill_claude: "logs green",
    hero_skill_cursor: "AI agreed",
    hero_skill_byok: "still BLOCK",
    hero_skill_strip_label: "Deploy claim — logs green, AI agreed, still BLOCK",
    hero_scene_kicker: "Under review",
    hero_scene_meta: "falsify.review.v1",
    receipt_claim_label: "claim",
    receipt_evidence_label: "evidence",
    receipt_verdict_label: "verdict",
    radar_kicker: "Verdict",
    radar_status: "Verdict: BLOCK",
    radar_evidence_label: "Blocking evidence",
    radar_repro: "Reproduce: open examples/sample-block-report.json",
    radar_n1_t: "Claim parse",
    radar_n1_s: "Deconstruct claim",
    radar_n2_t: "Evidence",
    radar_n2_s: "Collect artifacts",
    radar_n3_t: "Verifiability",
    radar_n3_s: "Reproduce checks",
    radar_n4_t: "Risk scope",
    radar_n4_s: "Impact & range",
    radar_n5_t: "Adversarial",
    radar_n5_s: "Hunt counterproof",
    radar_n6_t: "Decision",
    radar_n6_s: "Core receipt + claim ceiling",
    receipt_e1: "× log is not state",
    receipt_e2: "× missing rollback proof",
    receipt_e3: "× incomplete risk assessment",
    hero_claim: "“Logs green. Another AI agreed. Ship it.”",
    preview_must_fix: "Must Fix",
    preview_issue: "Logs ≠ state. Need probe + rollback evidence.",
    preview_title: "Logs green. Second model agreed. Ready to ship?",
    preview_action: "Minimal action: attach post-deploy probe + rollback command",
    gate_live: "LIVE EVIDENCE GATE",
    gate_frame: "Frame",
    gate_adv: "Adversarial",
    gate_cut: "Cutline",
    gate_verdict: "Verdict",
    gate_pass: "PASS",
    loop_submit: "Submit",
    loop_attack: "Attack",
    loop_cutline: "Cutline",
    loop_verdict: "Verdict",
    loop_artifact: "Artifact",
    hero_img_alt: "Falsify BLOCK review: deploy claim blocked without state proof",
    sig1_n: "Stable public core",
    sig1_l: "PASS · PASS_WITH_DEBT · BLOCK",
    sig2_n: "Evidence or BLOCK",
    sig2_l: "green logs / AI agreement are not proof",
    sig3_n: "3 cost tiers",
    sig3_l: "Normal ? Production ? Quant",
    sig4_n: "Open core",
    sig4_l: "MIT protocol · Pro enforcement stays closed",
    how_label: "How it decides",
    how_summary_hint: "Adversarial → Framework → Cutline → PASS / PASS_WITH_DEBT / BLOCK",
    how_analogy:
      "Review first. Trust after. Evidence first. Ship after.",
    hero_layers_l1_tag: "Adversarial",
    hero_layers_l1_map: "Red-teams \"looks fine\"",
    hero_layers_l2_tag: "Framework",
    hero_layers_l2_map: "Catches what will rot later",
    hero_layers_l3_tag: "Cutline",
    hero_layers_l3_map: "Must Fix / Debt / Delete",
    hero_layers_verdicts: "Core receipt: PASS / PASS_WITH_DEBT / BLOCK",
    verdict_lanes:
      "Public core stays parseable: PASS / PASS_WITH_DEBT / BLOCK. CLI-first Production and Quant gates may add KILL, CANDIDATE_NEEDS_NEXT_GATE, NO_DECISION_INSUFFICIENT_EVIDENCE, and an explicit claim ceiling.",
    hero_docs_link: "How adversarial review works →",
    proof_label: "Proof",
    proof_h2: "What actually gets stopped.",
    proof_lead:
      "Open the real JSON. Public artifacts use the stable core receipt; stricter domain verdicts safely degrade to BLOCK for core consumers.",
    case_claim_label: "Original claim",
    case_found_label: "What Falsify found",
    case_verdict_label: "Verdict",
    case_verdict_note: "Not FAIL. Not KILL. Engineering protocol uses BLOCK.",
    case_artifact_label: "Raw artifact",
    case_repro_label: "Reproduce",
    case1_domain: "Production · deploy",
    case1_title: "Logs green ≠ state proven",
    case1_claim:
      "“Deployment succeeded — logs completed and another AI found no issue.”",
    case1_finding:
      "Logs treated as state verification; “another AI reviewed it” is not evidence. No read-after-write probe, no rollback in the pack.",
    case1_link: "sample-block-report.json →",
    case1_repro:
      "curl -sL https://falsify.zjdeng.xyz/examples/sample-block-report.json | python -m json.tool",
    case1_repro_local:
      "Local: open examples/sample-block-report.json · or python -m json.tool examples/sample-block-report.json",
    case2_domain: "Research ops · tables",
    case2_title: "4 pricing errors in one table",
    case2_finding:
      "Dual agents, different model families: wrong base, flipped sign, abandoned tier, wrong row. Conflicts logged with verification paths — never silently overwritten.",
    case2_link: "comparison case study →",
    case3_domain: "Optional depth",
    case3_title: "Pretty metrics, wrong mechanic",
    case3_finding:
      "A report looked ready after formal gates. An independent second model forced a different execution assumption — the claim died before live. Same protocol; domain is optional.",
    case3_link: "deep case (optional) →",
    quote_p:
      '"Gate pass is not evidence. If the assumption is wrong, pretty numbers just make the failure faster."',
    quote_cite: "Chris Shi",
    compat_mechanic: "one mechanic away from live money",
    compat_selfhost: "Self-hosted · unlimited repos",
    workbench_h2: "Generate a BLOCK receipt in under a minute",
    workbench_scope:
      "Local demo of the verdict format — not full Falsify enforcement. Keep this output or a CLI artifact if you claim Falsify was run.",
    workbench_privacy:
      "Run example stays local in the browser. Review my claim only hits /review if you configure a provider key — nothing is uploaded to Falsify cloud.",
    input_h3: "Claim",
    input_p: "Paste a deployment claim, PR summary, or AI-generated report.",
    output_h3: "Verdict",
    output_p: "Hit Run example to preview a BLOCK artifact.",
    scenario_general: "General",
    scenario_code: "Code / PR",
    scenario_research: "Research",
    scenario_production: "Production",
    start_h2: "Install locally",
    try_skills_note:
      "MIT: protocol, CLI, packs, templates. Pro: production enforcement, private runtime skills, full fixture libraries.",
    try_skills_link: "Install a Falsify skill (Claude Code or Cursor) →",
    docs_install: "Install GitHub Action (5 min) →",
    cta_h2: "Review first. Trust after.",
    cta_boundary: "Sign-off only. Does not deploy or trade for you. Know what ships today vs what stays Pro.",
    oss_h: "OSS (MIT)",
    oss_1: "Protocol + schema (falsify.review.v1)",
    oss_2: "CLI + local demo",
    oss_3: "Local receipts / public example artifacts",
    oss_4: "Starter skill packs + Action templates",
    pro_h: "Pro",
    pro_1: "CI enforcement hooks",
    pro_2: "Policy management",
    pro_3: "Private antibodies / fixture libraries",
    pro_4: "Audit retention + contracted governance",
    licensing_p: "This site is not hosted SaaS. Self-host the MIT tree; Pro is separate closed surface.",
    licensing_link: "Open-core boundary →",
    licensing_pro: "Pro vs OSS →",
    use_sample: "Use sample instead",
    live_setup_h3: "Live review needs setup",
    live_setup_p:
      "Bring your own provider key (BYOK) or run falsify init on the server. Use the sample to preview the verdict format without a key.",
    live_setup_docs: "Getting started →",
  },
  zh: {
    nav_menu: "菜单",
    nav_how: "如何裁决",
    nav_proof: "证据",
    nav_try: "试用",
    nav_docs: "文档",
    nav_skills: "技能",
    nav_rootfix: "ROOTFIX",
    hero_eyebrow: "两个痛点 · 三层白话",
    h1: "看起来绿了，还不够。",
    hero_sub:
      "AI 幻觉与假绿，靠对抗审。长期腐烂与过度工程，靠框架审 + Cutline。然后签收：PASS、PASS_WITH_DEBT 或 BLOCK。",
    hero_io: "输入：声明 + 证据包 · 输出：可保留、可 diff、可重跑的 falsify.review.v1 JSON。",
    hero_step_1_k: "对抗审",
    hero_step_1: " — 专打「看起来没问题」（假绿、AI 幻觉）",
    hero_step_2_k: "框架审",
    hero_step_2: " — 专抓「以后会烂掉」（结构、过度工程）",
    hero_step_3_k: "Cutline",
    hero_step_3: " — 该改改、该记记、该删删，再给 PASS / PASS_WITH_DEBT / BLOCK",
    hero_claiming: "只做审查签收，不自动部署、不下单。安装 skill 不等于做过 Falsify——请保留产物。",
    btn_see_proof: "看证据",
    btn_run_sample_hero: "看真实 BLOCK 产物",
    btn_try_demo: "60 秒演示",
    btn_install_skill: "本地安装",
    btn_install: "GitHub Action",
    btn_sample: "运行示例",
    btn_review: "审查我的声明",
    trust_band_github: "GitHub",
    trust_mit: "MIT（open core）",
    trust_byok: "无 Falsify key · BYOK",
    trust_pro: "生产强制闭源（Pro）",
    trust_schema: "falsify.review.v1",
    hero_skill_install: "部署声明",
    hero_skill_claude: "日志绿了",
    hero_skill_cursor: "AI 同意",
    hero_skill_byok: "仍是 BLOCK",
    hero_skill_strip_label: "部署声明 — 日志绿了、AI 同意、仍是 BLOCK",
    hero_scene_kicker: "审查中",
    hero_scene_meta: "falsify.review.v1",
    receipt_claim_label: "claim",
    receipt_evidence_label: "evidence",
    receipt_verdict_label: "verdict",
    radar_kicker: "裁决",
    radar_status: "裁决：BLOCK",
    radar_evidence_label: "阻断证据",
    radar_repro: "复现：打开 examples/sample-block-report.json",
    radar_n1_t: "声明解构",
    radar_n1_s: "拆解 claim",
    radar_n2_t: "证据收集",
    radar_n2_s: "收集 artifacts",
    radar_n3_t: "可验证性",
    radar_n3_s: "验证可复现",
    radar_n4_t: "风险评估",
    radar_n4_s: "影响与范围",
    radar_n5_t: "对抗检验",
    radar_n5_s: "寻找反证",
    radar_n6_t: "决策输出",
    radar_n6_s: "\u6838\u5fc3\u56de\u6267 + claim ceiling",
    receipt_e1: "× 缺少 rollback 证据",
    receipt_e2: "× 无 deploy trace",
    receipt_e3: "× 无完整风险评估",
    hero_claim: "“日志绿了，另一个 AI 也同意。能上。”",
    preview_must_fix: "Must Fix",
    preview_issue: "日志 ≠ 状态。缺探针与回滚证据。",
    preview_title: "日志绿了。第二个模型也同意。能上线吗？",
    preview_action: "最小动作：附 post-deploy 探针 + 回滚命令",
    gate_live: "实时证据门",
    gate_frame: "框架",
    gate_adv: "对抗",
    gate_cut: "Cutline",
    gate_verdict: "裁决",
    gate_pass: "PASS",
    loop_submit: "提交",
    loop_attack: "攻击",
    loop_cutline: "分界线",
    loop_verdict: "裁决",
    loop_artifact: "证据",
    hero_img_alt: "Falsify BLOCK 审查：缺状态证明的部署声明被拦截",
    sig1_n: "\u7a33\u5b9a\u7684\u516c\u5f00\u6838\u5fc3",
    sig1_l: "PASS · PASS_WITH_DEBT · BLOCK",
    sig2_n: "没证据就 BLOCK",
    sig2_l: "绿日志 / AI 同意不算证明",
    sig3_n: "\u4e09\u6863\u6210\u672c\u5c42\u7ea7",
    sig3_l: "Normal \u00b7 Production \u00b7 Quant",
    sig4_n: "Open core",
    sig4_l: "MIT 协议 · 生产强制仍闭源",
    how_label: "如何裁决",
    how_summary_hint: "对抗审 → 框架审 → Cutline → PASS / PASS_WITH_DEBT / BLOCK",
    how_analogy: "先审，再信；先证据，再放行。",
    hero_layers_l1_tag: "对抗审",
    hero_layers_l1_map: "专打「看起来没问题」",
    hero_layers_l2_tag: "框架审",
    hero_layers_l2_map: "专抓「以后会烂掉」",
    hero_layers_l3_tag: "Cutline",
    hero_layers_l3_map: "该改改，该记记，该删删",
    hero_layers_verdicts: "核心回执：PASS / PASS_WITH_DEBT / BLOCK",
    verdict_lanes:
      "公开核心保持可解析：PASS / PASS_WITH_DEBT / BLOCK。CLI-first 的 Production / Quant 闸门可追加 KILL、CANDIDATE_NEEDS_NEXT_GATE、NO_DECISION_INSUFFICIENT_EVIDENCE，并明确 claim ceiling。",
    hero_docs_link: "对抗审查如何工作 →",
    proof_label: "证据",
    proof_h2: "真正拦住了什么。",
    proof_lead: "\u76f4\u63a5\u6253\u5f00\u771f\u5b9e JSON\u3002\u516c\u5f00\u4ea7\u7269\u4f7f\u7528\u7a33\u5b9a\u6838\u5fc3\u56de\u6267\uff1b\u66f4\u4e25\u683c\u7684\u9886\u57df\u88c1\u51b3\u53ef\u5b89\u5168\u964d\u7ea7\u4e3a BLOCK\u3002",
    case_claim_label: "原始声明",
    case_found_label: "Falsify 发现",
    case_verdict_label: "裁决",
    case_verdict_note: "不是 FAIL。不是 KILL。工程协议用 BLOCK。",
    case_artifact_label: "原始产物",
    case_repro_label: "复现",
    case1_domain: "生产 · 部署",
    case1_title: "日志绿了 ≠ 状态成立",
    case1_claim: "「部署成功——日志跑完，另一个 AI 也没发现问题。」",
    case1_finding:
      "把日志当状态验证；「另一个 AI 审过」不是证据。没有 read-after-write 探针，包里也没有回滚。",
    case1_link: "sample-block-report.json →",
    case1_repro:
      "curl -sL https://falsify.zjdeng.xyz/examples/sample-block-report.json | python -m json.tool",
    case1_repro_local:
      "本地：打开 examples/sample-block-report.json · 或 python -m json.tool examples/sample-block-report.json",
    case2_domain: "研究运维 · 表格",
    case2_title: "一张表 4 处定价错误",
    case2_finding:
      "双 Agent、不同模型族：基数错、符号反、档位放弃、行选错。冲突带验证路径写进 log，从不静默覆盖。",
    case2_link: "横向对比案例 →",
    case3_domain: "可选深度",
    case3_title: "漂亮指标，错误机制",
    case3_finding:
      "正式关卡后看起来可以上线。独立第二模型强制换执行假设 — 结论在 live 前死亡。协议通用；领域可选。",
    case3_link: "深案例（可选）→",
    quote_p: "「过关不是证据。假设错了，漂亮数字只会让失败更快。」",
    quote_cite: "Chris Shi",
    compat_mechanic: "差一个机制就要上实盘",
    compat_selfhost: "自托管 · 仓库不限",
    workbench_h2: "一分钟内生成 BLOCK 回执",
    workbench_scope:
      "裁决格式本地演示 — 非完整 Falsify 强制。若声称跑过 Falsify，请保留本输出或 CLI 产物。",
    workbench_privacy:
      "「运行示例」只在浏览器本地。「审查我的声明」仅在配置 provider key 后访问 /review — 不会上传到 Falsify 云。",
    input_h3: "声明",
    input_p: "粘贴部署声明、PR 摘要或 AI 生成报告。",
    output_h3: "裁决",
    output_p: "点「运行示例」预览 BLOCK 产物。",
    scenario_general: "通用",
    scenario_code: "代码 / PR",
    scenario_research: "研究",
    scenario_production: "生产",
    start_h2: "本地安装",
    try_skills_note: "MIT：协议、CLI、packs、模板。Pro：生产强制、私有 runtime skill、完整 fixture 库。",
    try_skills_link: "安装 Falsify skill（Claude Code 或 Cursor）→",
    docs_install: "5 分钟安装 GitHub Action →",
    cta_h2: "先审，再信。",
    cta_boundary: "只做审查签收，不自动部署、不下单。先看清今天能拿到什么，Pro 多什么。",
    oss_h: "OSS（MIT）",
    oss_1: "协议 + schema（falsify.review.v1）",
    oss_2: "CLI + 本地 demo",
    oss_3: "本地回执 / 公开示例产物",
    oss_4: "Starter skill packs + Action 模板",
    pro_h: "Pro",
    pro_1: "CI 强制钩子",
    pro_2: "策略 / policy 管理",
    pro_3: "私有 antibody / fixture 库",
    pro_4: "审计留存 + 签约治理",
    licensing_p: "本站不是托管 SaaS。MIT 树自托管；Pro 是独立闭源面。",
    licensing_link: "Open-core 边界 →",
    licensing_pro: "Pro vs OSS →",
    use_sample: "改用样例",
    live_setup_h3: "实时审查需要先配置",
    live_setup_p:
      "请自带 provider key（BYOK），或在服务端运行 falsify init。没有 key 时，先用样例预览裁决格式。",
    live_setup_docs: "入门指南 →",
  },
};

const STORAGE_KEY = "falsify-lang";

function readRequestedLang() {
  const params = new URLSearchParams(window.location.search);
  const fromQuery = params.get("lang");
  if (fromQuery === "zh" || fromQuery === "zh-CN") return "zh";
  if (fromQuery === "en") return "en";
  return null;
}

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

let lang = readRequestedLang() || readStoredLang();
if (readRequestedLang()) writeStoredLang(lang);

function applyLang() {
  const isZh = lang === "zh";
  document.documentElement.lang = isZh ? "zh-CN" : "en";
  document.documentElement.classList.toggle("lang-zh", isZh);
  document.body.classList.toggle("lang-zh", isZh);
  const langBtn = document.getElementById("lang-btn");
  if (langBtn) langBtn.textContent = isZh ? "EN" : "中文";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const k = el.getAttribute("data-i18n");
    if (T[lang][k] === undefined) return;
    el.textContent = T[lang][k];
  });
  document.querySelectorAll("[data-i18n-alt]").forEach((el) => {
    const k = el.getAttribute("data-i18n-alt");
    if (T[lang][k] !== undefined) el.alt = T[lang][k];
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
    const k = el.getAttribute("data-i18n-aria");
    if (T[lang][k] !== undefined) el.setAttribute("aria-label", T[lang][k]);
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

function tr(key) {
  return T[lang][key] ?? T.en[key] ?? key;
}

function isSetupError(message) {
  const m = String(message || "").toLowerCase();
  return (
    m.includes("no endpoint") ||
    m.includes("no api key") ||
    m.includes("no model") ||
    m.includes("falsify init")
  );
}

function renderReviewError(error) {
  const fallback =
    '<p><button class="btn ghost" type="button" id="fallback-sample">' +
    esc(tr("use_sample")) +
    "</button></p>";
  if (isSetupError(error)) {
    return (
      "<h3>" +
      esc(tr("live_setup_h3")) +
      "</h3><p>" +
      esc(tr("live_setup_p")) +
      '</p><p><a class="hero-docs-link" href="/docs/00-getting-started.md">' +
      esc(tr("live_setup_docs")) +
      "</a></p>" +
      fallback
    );
  }
  return "<h3>" + esc(tr("output_h3")) + "</h3><p>" + esc(error) + "</p>" + fallback;
}

function renderVerdict(d) {
  let h = '<span class="badge ' + d.verdict + '">' + d.verdict + "</span>";
  for (const x of d.risks || []) {
    h +=
      '<div class="risk"><small>' +
      esc(x.cutline || x.severity || "Finding") +
      "</small>" +
      esc(x.issue || "") +
      "<br><em>" +
      esc(x.minimal_action || "") +
      "</em>";
    if (x.upgrade_trigger) {
      h +=
        "<br><em>" +
        (lang === "zh" ? "升级触发：" : "Upgrade trigger: ") +
        esc(x.upgrade_trigger) +
        "</em>";
    }
    h += "</div>";
  }
  return h;
}

function runSample() {
  const sc = document.getElementById("s").value;
  document.getElementById("out").innerHTML =
    "<h3>" + (lang === "zh" ? "裁决" : "Verdict") + "</h3>" + renderVerdict(SAMPLES[sc] || SAMPLES.production);
}

async function go() {
  const t = document.getElementById("t").value.trim();
  const out = document.getElementById("out");
  const b = document.getElementById("b");
  if (!t) {
    out.innerHTML = "<p>" + (lang === "zh" ? "请先粘贴内容。" : "Paste something first.") + "</p>";
    return;
  }
  b.disabled = true;
  out.innerHTML = "<p>" + (lang === "zh" ? "审查中..." : "Reviewing...") + "</p>";
  try {
    const r = await fetch("/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: t, scenario: document.getElementById("s").value }),
    });
    const d = await r.json();
    if (d.error) {
      out.innerHTML = renderReviewError(d.error);
      const fb = document.getElementById("fallback-sample");
      if (fb) fb.onclick = runSample;
      b.disabled = false;
      return;
    }
    if (d.raw) {
      out.innerHTML =
        '<span class="badge ' + d.verdict + '">' + d.verdict + "</span><pre>" + esc(d.raw) + "</pre>";
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

  const closeNav = () => {
    links.classList.remove("open");
    toggle.setAttribute("aria-expanded", "false");
  };

  toggle.addEventListener("click", () => {
    const open = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });

  links.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeNav);
  });
}

function initHeroScene() {
  const scene = document.querySelector(".hero-scene");
  if (!scene) return;
  // Static verdict terminal — no step theater.
  scene.classList.add("hero-scene--static");
}

document.getElementById("lang-btn").addEventListener("click", toggleLang);
document.getElementById("btn-sample").addEventListener("click", runSample);
document.getElementById("b").addEventListener("click", go);
initNav();
initHeroScene();
applyLang();
