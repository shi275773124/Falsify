const PUBLIC_COPY = [
  "Review first. Trust after.",
  "Falsify does not argue. It asks one question: where is the evidence.",
  "先审，再信。",
  "Falsify 不争辩，只问一件事：证据在哪里。",
  "Frame Audit + Adversarial Review + Cutline.",
  "框架审计 + 对抗审查 + Cutline。",
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
  "框架审计",
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

const T = {
  en: {
    nav_menu: "Menu",
    nav_layers: "Layers",
    nav_cases: "Cases",
    nav_artifact: "Sample",
    nav_demo: "Demo",
    nav_skills: "Skills",
    nav_docs: "Docs",
    h1: "Looks right is not enough.",
    hero_sub: "A conclusion is not trusted — unless it survives an independent adversarial attack.",
    hero_definition: "Frame Audit · Adversarial Review · Cutline → one protocol verdict.",
    hero_docs_link: "Full layers in docs →",
    btn_install: "Install GitHub Action",
    btn_run_sample: "Run sample review",
    btn_run_sample_hero: "Run sample",
    btn_download_skills: "Download skills",
    btn_audit: "Discuss an audit sprint",
    btn_docs: "Read docs",
    trust_band_github: "GitHub",
    trust_examples: "Examples",
    trust_self_audit: "Self-Falsify audit",
    trust_mit: "MIT (core)",
    trust_byok: "No Falsify key · BYOK",
    trust_schema: "falsify.review.v1",
    preview_label: "Review output",
    gate_live: "LIVE EVIDENCE GATE",
    preview_title: "6/7 gates PASS — ready for shadow live.",
    preview_must_fix: "Must Fix",
    preview_issue: "Second AI reran a different rebalance mechanic; SR collapsed to ≈0.77",
    preview_action: "Minimal action: Mechanic ground-truth vs live journal",
    gate_frame: "Frame",
    gate_adv: "Adversarial",
    gate_cut: "Cutline",
    gate_verdict: "Verdict",
    gate_pass: "PASS",
    ev1_val: "Try in minutes",
    ev1_lbl: "Workbench sample — not a benchmark",
    ev2_val: "3 protocol verdicts",
    ev2_lbl: "PASS / PASS_WITH_DEBT / BLOCK",
    ev3_val: "MIT",
    proof_action: "GitHub Action · open core",
    proof_github: "GitHub",
    hero_img_alt: "Falsify BLOCK review: Sharpe 4.06 strategy blocked after mechanic cross-check",
    quote_p: "\"Six gates passed. We were one mechanic away from live money — until the second run collapsed the Sharpe.\"",
    quote_cite: "Chris Shi",
    hero_layers_l1_tag: "Frame",
    hero_layers_l1_map: "Find rot in the frame",
    hero_layers_l2_tag: "Adversarial",
    hero_layers_l2_map: "Find assumptions that die",
    hero_layers_l3_tag: "Cutline",
    hero_layers_l3_map: "What must change now",
    hero_layers_verdicts: "PASS / PASS_WITH_DEBT / BLOCK",
    layers_manifesto_1: "Frame Audit detects structural rot. Adversarial Review attacks fatal assumptions. Cutline cuts discrete verdicts. The meta-layer audits the audit channel itself. Reviewer and author are cross-vendor independent. Verdict and authorization are deliberately separated.",
    layers_manifesto_2: "Falsify does not answer \"who should criticize.\" It defines what a trustworthy conclusion means.",
    cases_tag: "Cases",
    cases_h2: "Blind spots caught",
    case_illus: "Internal case",
    case1_domain: "Strategy research",
    case1_title: "Sharpe 4.06 · 6/7 PASS → mechanic flaw",
    case1_finding: "Second AI reran a different rebalance mechanic; SR collapsed to ≤.77. Gate pass is not evidence.",
    case1_link: "01-fictional-horizon-quant-audit.md →",
    case2_domain: "Research ops · fee table",
    case2_findings: "4 findings",
    case2_title: "4 pricing errors in one table",
    case2_finding: "No cite per cell — wrong base, flipped sign, wrong row. Conflicts logged, not silently overwritten.",
    case2_link: "comparison case study →",
    case3_domain: "DevOps · deploy",
    case3_title: "Logs green ≠ state proof",
    case3_finding: "Acceptance chain treats deploy logs as verification — no read-after-write probe.",
    case3_link: "sample-block-report.json →",
    bl_label: "Layer 01",
    ar_label: "Layer 02",
    rs_label: "Layer 03",
    rs_lead: "Decides what blocks now — not a laundry list of every risk.",
    artifact_tag: "Artifact",
    artifact_h2: "Real BLOCK report.",
    artifact_lead: "Sample JSON from the protocol — deploy logs ≠ state proof. Not a fabricated GitHub check mock.",
    artifact_download: "Download JSON",
    limits_tag: "Not Falsify",
    ap_1: "\"A second glance\" ≠ full Falsify",
    ap_2: "Cutline-only ≠ full Falsify",
    ap_3: "Every smell as Must Fix ≠ Cutline",
    workbench_h2: "Try a verdict in minutes",
    input_h3: "Claim",
    input_p: "Paste a deployment claim, PR summary, or AI-generated report.",
    output_h3: "Verdict",
    output_p: "Hit Run sample to preview the decision artifact.",
    workbench_scope: "Verdict format demo — not full Falsify enforcement.",
    scenario_general: "General",
    scenario_code: "Code / PR",
    scenario_research: "Research",
    scenario_production: "Production",
    btn_sample: "Run sample",
    btn_review: "Quick review (single-step)",
    start_tag: "Start",
    start_h2: "Run it locally in 60 seconds.",
    docs_install: "Install GitHub Action (5 min) →",
    boundary_tag: "Boundary",
    boundary_h2: "Falsify classifies risk. It does not authorize action.",
    boundary_p: "Self-review is not independent review.",
    licensing_p: "MIT covers the protocol, CLI, JSON schema, workflow templates, and local artifacts. Team covers hosted policy enforcement, report retention, org rollout, and managed integrations — not a second copy of the OSS templates.",
    licensing_link: "View on GitHub →",
    licensing_tag: "License",
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
    catches_tag: "What Falsify catches",
    catches_h2: "Weak evidence patterns become explicit verdicts.",
    catch_1_title: "Raw evidence missing",
    catch_1_body: "No source artifact, command output, raw verdict, parse status, or state proof.",
    catch_2_title: "Fake acceptance evidence",
    catch_2_body: "Logs, summaries, or agreement are treated as verification.",
    catch_3_title: "Stale source / stale data",
    catch_3_body: "Evidence may support a past state, not the current decision.",
    catch_4_title: "Permission drift",
    catch_4_body: "Policy, token, account, or role assumptions changed outside the reviewed artifact.",
    catch_5_title: "Known Debt without trigger",
    catch_5_body: "Debt that cannot say when it becomes a blocker is not controlled debt.",
    catch_6_title: "Prompt-only audit theater",
    catch_6_body: "Delete claims that add ceremony but no independent evidence.",
    delete_chip: "DELETE",
    skills_tag: "Skills Pack v0",
    skills_h2: "Run Falsify as workflows, not prompts.",
    skills_lead: "Falsify skills package evidence discipline into repeatable sign-off workflows: input contracts, verdict schema, raw artifact requirements, and sample BLOCK reports.",
    skills_commercial: "Skills are the public distribution layer: they help developers and teams try the protocol before a paid Audit Sprint or Design Partner pilot.",
    skill_1_title: "Deployment Claim Review",
    skill_1_body: "Purpose: Block \"logs green\" false confidence.",
    skill_1_cta: "Download skill / View workflow",
    skill_2_title: "AI PR Review",
    skill_2_body: "Purpose: Review agent-written code against raw evidence.",
    skill_2_cta: "Install GitHub Action / View workflow",
    skill_3_title: "Research Report Audit",
    skill_3_body: "Purpose: Catch stale data and conclusion overreach.",
    skill_3_cta: "Run sample / View workflow",
    skill_4_title: "Agent Safety Check",
    skill_4_body: "Purpose: Verify agent completion claims before trust.",
    skill_4_cta: "View template",
    commercial_tag: "Commercial path",
    commercial_h2: "From open protocol to team sign-off.",
    open_title: "Open core today",
    audit_title: "Audit Sprint / Design Partner",
    audit_1: "one high-risk artifact reviewed",
    audit_2: "adversarial verdict",
    audit_3: "Must Fix / Known Debt / Delete",
    audit_4: "implementation-ready minimal actions",
    audit_5: "team workflow mapping",
    audit_6: "4-8 week pilot path",
    team_title: "Team / Enterprise path",
    team_1: "shared review history",
    team_2: "policy enforcement",
    team_3: "report retention",
    team_5: "managed integrations",
    team_6: "RBAC, SSO, audit logs, and SLA as team/commercial path items",
    team_7: "private deployment / self-host path where supported",
    trust_boundary_tag: "Trust boundary",
    trust_boundary_h2: "Open where trust compounds. Commercial where teams need control.",
    boundary_public: "Public-facing",
    boundary_open: "Open-core entry",
    boundary_commercial: "Commercial path",
    cta_h2: "Block weak evidence before it ships.",
    cta_p: "Start open-core. Run it locally. Bring Falsify into your team when decisions need a sign-off trail.",
    must_fix: "Must Fix",
    minimal_action: "Minimal action",
    next_evidence: "Next evidence",
    verdict_label: "Verdict",
    confidence_label: "Confidence",
    findings_label: "Findings",
    provider_label: "Provider",
    finish_reason_label: "finish_reason",
    raw_status_label: "Raw evidence status",
    upgrade_trigger_label: "Upgrade trigger",
    reviewing: "Reviewing...",
    paste_first: "Paste something first.",
    use_sample: "Use sample instead",
    live_setup_h3: "Live review needs setup",
    live_setup_p: "Bring your own provider key (BYOK) or run falsify init on the server. Use the sample to preview the verdict format without a key.",
    live_setup_docs: "Getting started →",
  },
  zh: {
    nav_menu: "菜单",
    nav_layers: "三层",
    nav_cases: "案例",
    nav_artifact: "样例",
    nav_demo: "演示",
    nav_skills: "技能",
    nav_docs: "文档",
    h1: "看起来对，不够。",
    hero_sub: "结论不可信——除非它扛过独立对抗攻击。\nFalsify 把自信输出变成上线决策：PASS、PASS_WITH_DEBT 或 BLOCK，以原始证据为准。",
    hero_definition: "框架审计 · 对抗审查 · Cutline → 一个协议裁决。",
    hero_docs_link: "完整三层见文档 →",
    btn_install: "安装 GitHub Action",
    btn_run_sample: "运行样例审查",
    btn_run_sample_hero: "运行样例",
    btn_download_skills: "下载 skills",
    btn_audit: "讨论 Audit Sprint",
    btn_docs: "阅读文档",
    trust_band_github: "GitHub",
    trust_examples: "案例库",
    trust_self_audit: "Self-Falsify 审计",
    trust_mit: "MIT（核心）",
    trust_byok: "无 Falsify key · BYOK",
    trust_schema: "falsify.review.v1",
    preview_label: "审查输出",
    gate_live: "实时证据门",
    preview_title: "6/7 关 PASS — 准备 shadow live。",
    preview_must_fix: "Must Fix",
    preview_issue: "第二个 AI 用不同再平衡机制重跑，SR 跌到 ≈0.77",
    preview_action: "最小动作：机制实证对照 live 流水",
    gate_frame: "框架",
    gate_adv: "对抗",
    gate_cut: "Cutline",
    gate_verdict: "裁决",
    gate_pass: "PASS",
    ev1_val: "几分钟可试",
    ev1_lbl: "工作台样例 — 非基准测试",
    ev2_val: "3 种协议裁决",
    ev2_lbl: "PASS / PASS_WITH_DEBT / BLOCK",
    ev3_val: "MIT",
    proof_action: "GitHub Action · 开源核心",
    proof_github: "GitHub",
    hero_img_alt: "Falsify BLOCK 审查：Sharpe 4.06 策略在机制交叉验证后被拦截",
    quote_p: "「六道关全过了。距离上实盘只差一个机制——直到第二轮重跑，Sharpe 直接崩了。」",
    quote_cite: "Chris Shi",
    hero_layers_l1_tag: "框架",
    hero_layers_l1_map: "找出框架腐点",
    hero_layers_l2_tag: "对抗",
    hero_layers_l2_map: "找出会死的假设",
    hero_layers_l3_tag: "Cutline",
    hero_layers_l3_map: "决定现在必须改什么",
    hero_layers_verdicts: "PASS / PASS_WITH_DEBT / BLOCK",
    layers_manifesto_1: "框架审计找结构性腐点。对抗审查攻击致命假设。Cutline 切出离散裁决。元层还要审计审计通道本身。审查者与作者跨厂商独立。裁决与授权刻意分离。",
    layers_manifesto_2: "Falsify 不回答「该由谁来批评」，它定义什么叫可信赖的结论。",
    cases_tag: "案例",
    cases_h2: "拦住的盲区",
    case_illus: "内部案例",
    case1_domain: "策略研究",
    case1_title: "Sharpe 4.06 · 6/7 PASS → 机制缺陷",
    case1_finding: "第二个 AI 用不同再平衡机制重跑，SR 跌到 ≤.77。PASS 本身不是证据。",
    case1_link: "01-fictional-horizon-quant-audit.md →",
    case2_domain: "研究运维 · 费率表",
    case2_findings: "4 处发现",
    case2_title: "一张费率表 4 处定价错误",
    case2_finding: "每格缺出处 — 基数抄错、符号反了、选错行。冲突写进 log，不静默覆盖。",
    case2_link: "横向对比案例 →",
    case3_domain: "DevOps · 部署",
    case3_title: "日志绿了 ≠ 状态成立",
    case3_finding: "验收链把部署日志当状态证明 — 缺 read-after-write 探针。",
    case3_link: "sample-block-report.json →",
    bl_label: "第一层",
    ar_label: "第二层",
    rs_label: "第三层",
    rs_lead: "决定当下什么阻塞，不是罗列全部风险。",
    artifact_tag: "产物",
    artifact_h2: "真实 BLOCK 报告。",
    artifact_lead: "协议样例 JSON — 部署日志 ≠ 状态证明。不是伪造的 GitHub Check 截图。",
    artifact_download: "下载 JSON",
    limits_tag: "不是 Falsify",
    ap_1: "“再看一眼” ≠ 完整 Falsify",
    ap_2: "只有 Cutline ≠ 完整 Falsify",
    ap_3: "每个坏味道都标 Must Fix ≠ Cutline",
    workbench_h2: "几分钟跑一次裁决",
    input_h3: "声明",
    input_p: "粘贴部署声明、PR 摘要或 AI 生成报告。",
    output_h3: "裁决",
    output_p: "点“运行样例”预览裁决产物。",
    workbench_scope: "裁决格式演示 — 非完整 Falsify 强制。",
    scenario_general: "通用",
    scenario_code: "代码 / PR",
    scenario_research: "研究",
    scenario_production: "生产",
    btn_sample: "运行样例",
    btn_review: "快速审查（单步）",
    start_tag: "开始",
    start_h2: "60 秒本地跑起来。",
    docs_install: "5 分钟安装 GitHub Action →",
    boundary_tag: "边界",
    boundary_h2: "Falsify 只做风险分类，不做执行授权。",
    boundary_p: "自己审自己不算独立判断。",
    licensing_p: "MIT 覆盖协议、CLI、JSON schema、工作流模板与本地产物。Team 覆盖托管策略执行、报告留存、组织 rollout 与托管集成 — 不是 OSS 模板的第二份拷贝。",
    licensing_link: "在 GitHub 查看 →",
    licensing_tag: "许可证",
    bl_h3: "框架审计",
    ar_h3: "对抗审查",
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
    hero_chip_1: "框架审计",
    hero_chip_2: "对抗审查",
    hero_chip_3: "Cutline",
    lic_open_2: "MIT — 自托管，仓库不限",
    lic_team_2: "Team — 组织工作区，不与 OSS 重复",
    catches_tag: "Falsify 拦截什么",
    catches_h2: "弱证据模式会变成明确裁决。",
    catch_1_title: "缺少原始证据",
    catch_1_body: "没有来源产物、命令输出、原始裁决、解析状态或状态证明。",
    catch_2_title: "伪验收证据",
    catch_2_body: "把日志、摘要或模型同意当作验证。",
    catch_3_title: "过期来源 / 过期数据",
    catch_3_body: "证据可能只支持过去的状态，不支持当前决策。",
    catch_4_title: "权限漂移",
    catch_4_body: "策略、token、账号或角色假设在审查产物之外发生变化。",
    catch_5_title: "Known Debt 没有触发器",
    catch_5_body: "不能说明何时升级为 blocker 的债务，不是受控债务。",
    catch_6_title: "只有提示词的审计表演",
    catch_6_body: "删除那些增加仪式但没有独立证据的声明。",
    delete_chip: "DELETE",
    skills_tag: "Skills Pack v0",
    skills_h2: "把 Falsify 当工作流运行，不是提示词。",
    skills_lead: "Falsify skills 把证据纪律封装为可重复签收工作流：输入契约、裁决 schema、原始产物要求和样例 BLOCK 报告。",
    skills_commercial: "Skills 是公开分发层：帮助开发者和团队先试用协议，再进入付费 Audit Sprint 或 Design Partner pilot。",
    skill_1_title: "部署声明审查",
    skill_1_body: "用途：拦截“日志绿了”的虚假自信。",
    skill_1_cta: "下载 skill / 查看工作流",
    skill_2_title: "AI PR 审查",
    skill_2_body: "用途：用原始证据审查 agent 写的代码。",
    skill_2_cta: "安装 GitHub Action / 查看工作流",
    skill_3_title: "研究报告审计",
    skill_3_body: "用途：抓出过期数据和结论越界。",
    skill_3_cta: "运行样例 / 查看工作流",
    skill_4_title: "Agent 安全检查",
    skill_4_body: "用途：信任前验证 agent 完成声明。",
    skill_4_cta: "查看模板",
    commercial_tag: "商业路径",
    commercial_h2: "从开放协议到团队签收。",
    open_title: "今天可用的开放核心",
    audit_title: "Audit Sprint / Design Partner",
    audit_1: "审查一个高风险产物",
    audit_2: "对抗式裁决",
    audit_3: "Must Fix / Known Debt / Delete",
    audit_4: "可执行的最小动作",
    audit_5: "可重复的团队工作流",
    audit_6: "4-8 周 pilot 路径",
    team_title: "Team / Enterprise 路径",
    team_1: "共享审查历史",
    team_2: "策略执行",
    team_3: "报告留存",
    team_5: "托管集成",
    team_6: "RBAC、SSO、审计日志属于商业路径项",
    team_7: "在支持时提供 private deployment / self-host 路径",
    trust_boundary_tag: "信任边界",
    trust_boundary_h2: "信任会复利的部分开放，团队需要控制的部分商业化。",
    boundary_public: "公开侧",
    boundary_open: "开放核心入口",
    boundary_commercial: "商业路径",
    cta_h2: "在弱证据上线前拦住它。",
    cta_p: "先用开放核心本地运行。当决策需要签收轨迹时，把 Falsify 带进团队流程。",
    must_fix: "Must Fix",
    minimal_action: "最小动作",
    next_evidence: "下一份证据",
    verdict_label: "裁决",
    confidence_label: "置信度",
    findings_label: "发现",
    provider_label: "Provider",
    finish_reason_label: "finish_reason",
    raw_status_label: "原始证据状态",
    upgrade_trigger_label: "升级触发器",
    reviewing: "审查中...",
    paste_first: "请先粘贴内容。",
    use_sample: "改用样例",
    live_setup_h3: "实时审查需要先配置",
    live_setup_p: "请自带 provider key（BYOK），或在服务端运行 falsify init。没有 key 时，先用样例预览裁决格式。",
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
  document.getElementById("lang-btn").textContent = isZh ? "EN" : "中文";
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

document.getElementById("lang-btn").addEventListener("click", toggleLang);
document.getElementById("btn-sample").addEventListener("click", runSample);
document.getElementById("b").addEventListener("click", go);
initNav();
applyLang();
