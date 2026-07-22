(() => {
  "use strict";
  const copyCommand = "curl -sS https://falsify.site/examples/sample-block-report.json | python -m json.tool";
  const translations = {
    en: {
      menuLabel:"Menu",menuCloseLabel:"Close",navProof:"Real cases",navHow:"How it works",navDocs:"Docs",navGetStarted:"Get started",navPartner:"Partner",
      heroTitle:"Looks green isn't proof.",
      heroEyebrow:"TWO PAINS · THREE LAYERS",
      heroPrimary:"Install GitHub Action",heroSecondary:"Watch a claim get blocked",
      heroNote:"Sign-off only. Does not deploy or trade for you.",
      brandThesis:"Review first. Trust after. Evidence first. Ship after.",
      evidenceChrome:"EVIDENCE",
      heroPainLabel:"THE PAIN",
      heroPain1:"AI hallucination and false-green still ship",
      heroPain2:"Code rots — or dies of over-engineering",
      heroSolveLabel:"THE FIX",
      heroSolve1:"Adversarial review — red-teams \"looks fine\"",
      heroSolve2:"Framework + Cutline — stay maintainable, no bloat",
      heroLead:"",
      receiptExample:"FALSIFY RECEIPT #0482",receiptPhase:"01 CLAIM",
      proofHeadline:"Agents say \"trust me.\"",
      demoPause:"Reset",demoPlay:"Run example",
      deployBot:"DEPLOY BOT",successPill:"SUCCESS",
      demoClaim:"Deployment completed successfully.",
      envLabel:"ENVIRONMENT",envValue:"production",commitLabel:"COMMIT",
      authorityLine:"EVIDENCE CHECK · ADAPTER PROBE · GET /v2/projects/.../services/payment-api",
      claimedCommit:"CLAIMED COMMIT",prodCommit:"PRODUCTION COMMIT",
      conflictLabel:"EVIDENCE CONFLICT",
      conflictText:"Live revision does not match the claimed commit.",
      findingLabel:"FINDING",findingText:"Deployed revision does not match claimed commit.",
      scopeLabel:"CLAIM SCOPE",scopeValue:"deployment_revision",
      ceilingLabel:"AUTHORITY CEILING",ceilingValue:"EPISTEMIC_ONLY — no action authorized",
      capitalLabel:"CAPITAL AUTHORITY",capitalValue:"NONE",
      reproduceLabel:"REPRODUCE LOCALLY",
      demoCaption:"Format demo: claim → attack → evidence check → verdict. Not live data — local fixture reproduces this false green.",
      cutlineKicker:"CUTLINE",
      cutlineTitle:"NO EVIDENCE.<br><em>NO PASS.</em>",
      cutlineLead:"A deployment claim is not a production fact. Falsify checks the claim against executable evidence — not against another summary.",
      stripClaim:"CLAIM",stripAuth:"EVIDENCE",
      clarityUser:"WHO",clarityUserText:"Teams shipping AI-written PRs, deploys, and decision docs",
      clarityTrigger:"WHEN",clarityTriggerText:"Before you merge or ship on an AI claim of \"done\"",
      clarityAction:"WHAT",clarityActionText:"Adversarial · Framework · Cutline — then a PASS / PASS_WITH_DEBT / BLOCK receipt",
      clarityArtifact:"OUTPUT",clarityArtifactText:"A review sign-off you can keep, not an auto-deploy",
      proofLabel:"THREE DOCUMENTED FALSE-GREENS",proofTitle:"Start with proof, not process.",
      proofLead:"Each case looked green at the surface. Looks green isn't proof — each failed when the claim met real evidence.",
      apparentGreen:"APPARENT GREEN",realFailure:"REAL FAILURE",falsifyRequired:"FALSIFY REQUIRED",
      caseOneDomain:"LIVE EXECUTOR · DERIVED FRESHNESS",caseOneTitle:"Today's signal, weeks-old inputs",
      caseOneGreen:"Cron OK, today's signal timestamp, executor verify PASS.",
      caseOneFail:"Underlying panel CSVs had stopped updating weeks earlier.",
      caseOneReq:"Refresh and coverage gates, provenance manifest, and a permanent incident replay through the production wrapper.",
      caseTwoDomain:"QUANT RESEARCH · EVIDENCE INTEGRITY",caseTwoTitle:"A strict PASS overturned by hidden input assumptions",
      caseTwoGreen:"Saved returns passed DSR, PBO, and permutation checks.",
      caseTwoFail:"Coverage, row loss, and an implicit missing-data policy had already shaped the evidence surface.",
      caseTwoReq:"Calendar contract, row-loss audit, coverage manifest, and missing-policy variants before metric gates.",
      caseThreeDomain:"RUNTIME · MIRROR DRIFT",caseThreeTitle:"The mirror was fixed. The runtime was not.",
      caseThreeGreen:"The vault mirror contained the v0.6.8 return-basis fix.",
      caseThreeFail:"The actual second-profile runtime still executed the old version.",
      caseThreeReq:"Read and test the real runtime path, then verify runtime and mirror together.",
      inspectSource:"Inspect source ↗",inspectRepoContext:"Inspect repository context ↗",inspectArchitecture:"Inspect the runtime evidence ↗",
      differenceLabel:"THE CATEGORY LINE",differenceTitle:"Not another model opinion — a review with a receipt.",
      differenceLead:"Falsify red-teams claims that look fine, catches structure that will rot later, and forces Must Fix / Debt / Delete — then returns PASS, PASS_WITH_DEBT, or BLOCK.",
      bugScanner:"Bug scanner",bugScannerText:"checks a diff for defects",eval:"Eval",evalText:"measures model behavior on a test set",
      secondAi:"Second model",secondAiText:"another opinion — not proof",
      falsifyText:"adversarial + framework + Cutline → a sign-off receipt, not auto-ship",
      stepClaimTitle:"Claim",stepAttackTitle:"Adversarial",stepFrameTitle:"Framework",stepCheckTitle:"Cutline",stepVerdictTitle:"Verdict",stepGateTitle:"Boundary",
      howLabel:"HOW IT WORKS",howTitle:"Three layers. One plain question: where is the evidence?",
      howLead:"Adversarial red-teams \"looks fine.\" Framework catches what will rot later. Cutline says Must Fix / Debt / Delete. Then PASS, PASS_WITH_DEBT, or BLOCK.",
      stepClaim:"Something asserts success — a deploy, a metric, a \"done\" without proof.",
      stepAttack:"Red-teams what looks fine — AI hallucination, false-green, and confident claims without evidence.",
      stepFrame:"Catches what will rot later — hidden state, duplicated authority, brittle rollback, over-engineering.",
      stepCheck:"Must Fix / Known Debt / Delete — what to change, what to record, what to remove.",
      stepVerdict:"Receipt: PASS, PASS_WITH_DEBT, or BLOCK — keep it, diff it, re-run it.",
      stepGate:"Sign-off only. Does not deploy or trade for you.",
      deliveryLabel:"WHAT YOU CAN GET TODAY",deliveryTitle:"Same kernel. Different authority levels.",
      deliveryLead:"Every offer states its status. Sign-off only — nothing here deploys or trades for you.",
      d1Name:"Falsify Review",d1Status:"AVAILABLE · OSS",d1Text:"Adversarial LLM review with a bounded epistemic verdict. CLI, local demo, skills, and the GitHub Action template.",
      d2Name:"Falsify Authority Gate",d2Status:"ADAPTER REQUIRED",d2Text:"Runs executable evidence checks against a real authority path. Only then can a PASS bear action. No public adapter ships today.",
      d3Name:"Audit Sprint",d3Status:"AVAILABLE · SERVICE",d3Text:"Claim manifest, kill-shots, evidence pack, and a signed verdict receipt for one high-risk artifact.",
      d4Name:"Production / Quant Pro",d4Status:"DESIGN PARTNER · PRIVATE",d4Text:"Integrated per concrete authority path — deploy, data, or execution. Scoped pilots, not self-serve.",
      d5Name:"Team / Enterprise",d5Status:"TARGET · NOT SHIPPED",d5Text:"Dashboard, SSO, RBAC, retention. Roadmap targets — not delivered features.",
      resultLabel:"FORMAT PREVIEW",footerDocs:"Docs",footerContact:"Partner",footerSample:"Sample receipt",contactKicker:"PARTNER WITH THE FOUNDER",contactLead:"Design partnerships, integrations, research collaboration, or product questions — reach Chris Shi directly.",contactTwitter:"X / Twitter",contactEmail:"Email",contactGithub:"GitHub",contactEmailLabel:"Email",contactSecurity:"Security reporting",
      tryLabel:"FORMAT PREVIEW",tryTitle:"Preview the receipt shape",
      tryLead:"Same format as the hero demo — shape only, not a full gate or live probe.",
      runExample:"Run example",copyArtifact:"Copy reproduction command",
      resultTitle:"Ready to preview a format sample.",
      resultLead:"Run the example to see the verdict shape only — not evidence-backed verification.",
      installLabel:"START HERE",installTitle:"Start by gating claims on GitHub.",
      installLead:"Best first step: the GitHub Action reviews PR claims and decision docs and posts a PASS / PASS_WITH_DEBT / BLOCK receipt. Sign-off only — does not deploy or trade for you.",
      actionLink:"Install GitHub Action →",skillsLink:"Install a skill →",verdictLink:"Verdict contract →",
      ctaTitle:"Review first. Trust after.",
      ctaLead:"Keep the receipt — PASS, PASS_WITH_DEBT, or BLOCK. Sign-off only.",
      ctaPrimary:"Install GitHub Action",ctaSecondary:"See what you can get",
      footer:"Sign-off only — does not deploy or trade for you."
    },
    zh: {
      menuLabel:"菜单",menuCloseLabel:"关闭",navProof:"真实案例",navHow:"工作原理",navDocs:"文档",navGetStarted:"开始使用",navPartner:"合作",
      heroTitle:"看起来绿了，还不够。",
      heroEyebrow:"两个痛点 · 三层白话",
      heroPrimary:"安装 GitHub Action",heroSecondary:"看一条声明被拦下",
      heroNote:"只做审查签收，不自动部署、不下单。",
      brandThesis:"先审，再信；先证据，再放行。",
      evidenceChrome:"证据",
      heroPainLabel:"痛点",
      heroPain1:"AI 幻觉和假绿照样进生产",
      heroPain2:"代码长期腐烂，或过度工程",
      heroSolveLabel:"解法",
      heroSolve1:"对抗审 — 专打「看起来没问题」",
      heroSolve2:"框架审 + Cutline — 好维护、不过度工程",
      heroLead:"",
      receiptExample:"FALSIFY 回执 #0482",receiptPhase:"01 声明",
      proofHeadline:"Agent 说「信我」。",
      demoPause:"重置",demoPlay:"运行示例",
      deployBot:"部署机器人",successPill:"SUCCESS",
      demoClaim:"部署已成功完成。",
      envLabel:"环境",envValue:"production",commitLabel:"提交",
      authorityLine:"证据检查 · ADAPTER 探针 · GET /v2/projects/.../services/payment-api",
      claimedCommit:"声称提交",prodCommit:"生产提交",
      conflictLabel:"证据冲突",
      conflictText:"线上版本与声称的提交不一致。",
      findingLabel:"发现",findingText:"已部署版本与声称提交不一致。",
      scopeLabel:"声明范围",scopeValue:"deployment_revision",
      ceilingLabel:"权威上限",ceilingValue:"EPISTEMIC_ONLY — 不授权任何动作",
      capitalLabel:"资金权限",capitalValue:"NONE",
      reproduceLabel:"本地复现",
      demoCaption:"格式演示：声明 → 攻击 → 证据检查 → 裁决。不是实时数据——本地 fixture 可复现这个假绿。",
      cutlineKicker:"CUTLINE",
      cutlineTitle:"没有证据。<br><em>就不能 PASS。</em>",
      cutlineLead:"部署声明不等于生产事实。Falsify 用可执行的证据检查核对声明，而不是再看一份摘要。",
      stripClaim:"声明",stripAuth:"证据",
      clarityUser:"谁在用",clarityUserText:"用 AI 写 PR、部署与决策文档的团队",
      clarityTrigger:"什么时候用",clarityTriggerText:"在合并或上线前，面对 AI 的「已完成」",
      clarityAction:"它做什么",clarityActionText:"对抗审 · 框架审 · Cutline — 再给 PASS / PASS_WITH_DEBT / BLOCK 回执",
      clarityArtifact:"留下什么",clarityArtifactText:"审查签收，不是自动部署",
      proofLabel:"三个有据可查的假绿",proofTitle:"先看证据，再谈框架。",
      proofLead:"表面全绿不等于证明。每个案例都在碰到真实证据时露馅。",
      apparentGreen:"表面全绿",realFailure:"真实失败",falsifyRequired:"核验要求",
      caseOneDomain:"生产执行 · 数据时效",caseOneTitle:"今天的信号，几周前的输入",
      caseOneGreen:"cron 状态正常、信号时间戳是今天、executor verify 为 PASS。",
      caseOneFail:"底层 panel CSV 早在几周前就停止更新。",
      caseOneReq:"出信号前检查数据是否刷新、覆盖是否够；保留输入来源清单；并经生产入口永久回放该事故。",
      caseTwoDomain:"量化研究 · 证据完整性",caseTwoTitle:"输入口径有误，严格 PASS 也会失效",
      caseTwoGreen:"保存的收益序列通过了 DSR、PBO 和置换检验。",
      caseTwoFail:"覆盖率不足、数据丢行和未声明的缺失值处理，早已改变了计算基础。",
      caseTwoReq:"计算指标前，必须明确交易日历，检查数据丢行，记录覆盖率，并比较不同缺失值处理方案。",
      caseThreeDomain:"版本同步 · 生效偏差",caseThreeTitle:"代码已更新，生效环境还在跑旧版",
      caseThreeGreen:"留存副本已包含 v0.6.8 的收益基准修复。",
      caseThreeFail:"真正生效的环境仍在运行旧版本。",
      caseThreeReq:"直接读取并测试实际生效路径，再核对部署版本与留存副本是否一致。",
      inspectSource:"查看案例原文 ↗",inspectRepoContext:"查看案例原文 ↗",inspectArchitecture:"查看案例原文 ↗",
      differenceLabel:"它到底是什么",differenceTitle:"不是又一个模型意见，而是带回执的审查。",
      differenceLead:"Falsify 专打「看起来没问题」，专抓「以后会烂掉」，再强制 Must Fix / 记债 / 删除——然后给出 PASS、PASS_WITH_DEBT 或 BLOCK。",
      bugScanner:"缺陷扫描器",bugScannerText:"检查 diff 里有没有缺陷",eval:"模型评测",evalText:"衡量模型在测试集上的表现",
      secondAi:"第二个模型",secondAiText:"又一个意见——不是证明",
      falsifyText:"对抗审 + 框架审 + Cutline → 签收回执，不是自动上线",
      stepClaimTitle:"声明",stepAttackTitle:"对抗审",stepFrameTitle:"框架审",stepCheckTitle:"Cutline",stepVerdictTitle:"裁决",stepGateTitle:"边界",
      howLabel:"工作原理",howTitle:"三层白话。只问一件事：证据在哪里？",
      howLead:"对抗审专打「看起来没问题」。框架审专抓「以后会烂掉」。Cutline：该改改，该记记，该删删。然后 PASS、PASS_WITH_DEBT 或 BLOCK。",
      stepClaim:"有人声称成功——一次部署、一个指标、一句没有证据的「做完了」。",
      stepAttack:"专打「看起来没问题」——AI 幻觉、假绿、没证据却很自信的声明。",
      stepFrame:"专抓「以后会烂掉」——隐状态、重复权威、脆弱回滚、过度工程。",
      stepCheck:"该改改，该记记，该删删——Must Fix / Known Debt / Delete。",
      stepVerdict:"回执：PASS、PASS_WITH_DEBT 或 BLOCK——可保留、可 diff、可重跑。",
      stepGate:"只做审查签收，不自动部署、不下单。",
      deliveryLabel:"今天能拿到什么",deliveryTitle:"同一内核，不同权威级别。",
      deliveryLead:"每个交付物都标明状态。只做审查签收——这里不会替你部署或下单。",
      d1Name:"Falsify Review",d1Status:"AVAILABLE · 开源",d1Text:"对抗式 LLM 审查，签发边界内的认知层裁决。含 CLI、本地 demo、skills 与 GitHub Action 模板。",
      d2Name:"Falsify Authority Gate",d2Status:"需要 ADAPTER",d2Text:"对真实权威路径执行可执行的证据检查；只有这样 PASS 才能承载动作。目前没有公开的 adapter。",
      d3Name:"Audit Sprint",d3Status:"AVAILABLE · 服务",d3Text:"针对一个高风险产物：声明清单、kill-shots、证据包，以及签署的裁决回执。",
      d4Name:"Production / Quant Pro",d4Status:"DESIGN PARTNER · 私有",d4Text:"按具体权威路径集成——部署、数据或执行。小规模试点，不自助开放。",
      d5Name:"Team / Enterprise",d5Status:"TARGET · 未交付",d5Text:"Dashboard、SSO、RBAC、留存。路线图目标，不是已交付功能。",
      resultLabel:"格式预览",footerDocs:"文档",footerContact:"合作",footerSample:"示例回执",contactKicker:"与创始人合作",contactLead:"设计合作、集成、研究协作或产品问题——直接联系 Chris Shi。",contactTwitter:"X / Twitter",contactEmail:"邮箱",contactGithub:"GitHub",contactEmailLabel:"邮箱",contactSecurity:"安全报告",
      tryLabel:"格式预览",tryTitle:"预览回执长什么样",
      tryLead:"与 Hero 演示同一格式——只看形状，不是完整门禁或实时探测。",
      runExample:"运行示例",copyArtifact:"复制复现命令",
      resultTitle:"可以预览格式样例",
      resultLead:"运行示例只看判定长什么样——不是有证据背书的核验。",
      installLabel:"从这里开始",installTitle:"先从 GitHub 拦住声明。",
      installLead:"最稳的第一步：GitHub Action 审查 PR 声明与决策文档，给出 PASS / PASS_WITH_DEBT / BLOCK 回执。只做审查签收，不自动部署、不下单。",
      actionLink:"安装 GitHub Action →",skillsLink:"安装 Skill →",verdictLink:"查看判定约定 →",
      ctaTitle:"先审，再信。",
      ctaLead:"留下回执——PASS、PASS_WITH_DEBT 或 BLOCK。只做审查签收。",
      ctaPrimary:"安装 GitHub Action",ctaSecondary:"看看能拿到什么",
      footer:"只做审查签收，不自动部署、不下单。"
    }
  };
  const phaseLabels = {
    en: ["01 CLAIM", "02 FRAME", "03 CHECK", "03 CHECK", "04 VERDICT", "05 RECEIPT"],
    zh: ["01 声明", "02 界定", "03 核对", "03 核对", "04 裁决", "05 回执"]
  };
  const readStoredLanguage = () => { try { return localStorage.getItem("falsify-flow-language"); } catch { return null; } };
  const storeLanguage = (value) => { try { localStorage.setItem("falsify-flow-language", value); } catch {} };
  const requestedLanguage = new URLSearchParams(window.location.search).get("lang");
  let language = requestedLanguage === "zh" || requestedLanguage === "en" ? requestedLanguage : (readStoredLanguage() || "en");
  const addText = (parent, tag, className, text) => { const node = document.createElement(tag); if (className) node.className = className; node.textContent = String(text); parent.appendChild(node); return node; };
  const renderHeroTitle = (element, value) => {
    const marker = "<br><em>", markerIndex = value.indexOf(marker);
    if (markerIndex < 0) { element.textContent = value; return; }
    const plain = value.slice(0, markerIndex);
    const emphasized = value.slice(markerIndex + marker.length).replace(/<\/em>$/, "");
    const br = document.createElement("br"), em = document.createElement("em");
    em.textContent = emphasized;
    element.replaceChildren(document.createTextNode(plain), br, em);
  };
  const syncLinks = () => document.querySelectorAll("[data-lang-path]").forEach((link) => {
    link.href = link.dataset.langPath + (language === "zh" ? "?lang=zh" : "");
  });
  // Never put bare mailto: or raw email text in static HTML — Cloudflare email
  // obfuscation rewrites both. Wire href (+ optional visible text) from data-email.
  const wireContactEmails = () => document.querySelectorAll("a[data-email]").forEach((link) => {
    const email = (link.dataset.email || "").trim();
    if (!email.includes("@")) return;
    const subject = (link.dataset.emailSubject || "").trim();
    link.href = subject
      ? `mailto:${email}?subject=${encodeURIComponent(subject)}`
      : `mailto:${email}`;
    if (link.dataset.emailText === "1") link.textContent = email;
  });
  const restoreCloudflareEmailLinks = () => document.querySelectorAll("a[data-cfemail]").forEach((link) => {
    const encoded = link.dataset.cfemail || "";
    if (encoded.length < 4) return;
    const key = Number.parseInt(encoded.slice(0, 2), 16);
    const email = Array.from({ length: (encoded.length - 2) / 2 }, (_, index) => String.fromCharCode(Number.parseInt(encoded.slice(index * 2 + 2, index * 2 + 4), 16) ^ key)).join("");
    if (email.includes("@")) link.href = `mailto:${email}`;
  });
  const menu = document.querySelector(".menu"), nav = document.querySelector("nav");
  const syncMenuLabel = () => {
    if (!menu) return;
    const t = translations[language];
    const open = Boolean(nav && nav.classList.contains("open"));
    menu.textContent = open ? t.menuCloseLabel : t.menuLabel;
  };
  const setMenuOpen = (open) => {
    if (!nav || !menu) return;
    nav.classList.toggle("open", open);
    menu.setAttribute("aria-expanded", String(open));
    syncMenuLabel();
  };
  const render = () => {
    const t = translations[language];
    document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
    document.documentElement.setAttribute("data-flow-lang", language);
    document.querySelector(".lang").textContent = language === "zh" ? "EN" : "中文";
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      if (el === menu) return;
      const value = t[el.dataset.i18n];
      if (value) el.textContent = value;
    });
    document.querySelectorAll("[data-i18n-html]").forEach((el) => {
      const value = t[el.dataset.i18nHtml];
      if (value) renderHeroTitle(el, value);
    });
    syncMenuLabel();
    syncLinks();
    wireContactEmails();
    restoreCloudflareEmailLinks();
    document.documentElement.removeAttribute("data-i18n-pending");
  };
  document.querySelector(".lang").addEventListener("click", () => {
    language = language === "en" ? "zh" : "en";
    storeLanguage(language);
    const url = new URL(location.href);
    if (language === "zh") url.searchParams.set("lang", "zh"); else url.searchParams.delete("lang");
    history.replaceState(null, "", url);
    render();
    setStage(stageIndex);
    const playing = demoActive || Boolean(demoTimer);
    toggle.setAttribute("aria-pressed", playing ? "true" : "false");
    toggle.textContent = playing ? translations[language].demoPause : translations[language].demoPlay;
    if(window.ScrollTrigger)ScrollTrigger.refresh();
  });
  window.addEventListener("load",function(){if(window.ScrollTrigger)ScrollTrigger.refresh()});
  render();
  menu.addEventListener("click", (event) => {
    event.stopPropagation();
    setMenuOpen(!nav.classList.contains("open"));
  });
  nav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setMenuOpen(false)));
  document.addEventListener("click", (event) => {
    if (!nav.classList.contains("open")) return;
    if (nav.contains(event.target) || menu.contains(event.target)) return;
    setMenuOpen(false);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && nav.classList.contains("open")) setMenuOpen(false);
  });

  const receipt = document.querySelector(".demo-receipt");
  const toggle = document.querySelector(".demo-toggle");
  const phaseEl = document.querySelector(".receipt-phase");
  // claim → success card → frame/compare intro → commits lit → conflict → block+receipt
  const stages = ["claim", "success", "compare", "mismatch", "conflict", "block"];
  // Idle default = claim (start empty). Run example advances to full BLOCK.
  const stageDelays = [0, 170, 180, 190, 200, 0];
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let demoTimer = 0, stageIndex = 0, demoActive = false;
  const stopDemo = () => { if (demoTimer) window.clearTimeout(demoTimer); demoTimer = 0; };
  const setStage = (index) => {
    stageIndex = Math.min(index, stages.length - 1);
    receipt.dataset.demoState = stages[stageIndex];
    if (phaseEl) phaseEl.textContent = phaseLabels[language][stageIndex];
  };
  const resetDemo = () => {
    stopDemo();
    demoActive = false;
    setStage(0);
    toggle.setAttribute("aria-pressed", "false");
    toggle.textContent = translations[language].demoPlay;
  };
  const advanceDemo = () => {
    if (stageIndex >= stages.length - 1) {
      stopDemo();
      demoActive = false;
      toggle.setAttribute("aria-pressed", "false");
      toggle.textContent = translations[language].demoPlay;
      return;
    }
    setStage(stageIndex + 1);
    if (stageIndex >= stages.length - 1) {
      stopDemo();
      demoActive = false;
      toggle.setAttribute("aria-pressed", "false");
      toggle.textContent = translations[language].demoPlay;
      return;
    }
    demoTimer = window.setTimeout(advanceDemo, stageDelays[stageIndex] || 180);
  };
  const startDemo = () => {
    stopDemo();
    demoActive = true;
    if (reducedMotion.matches) {
      setStage(stages.length - 1);
      toggle.setAttribute("aria-pressed", "false");
      toggle.textContent = translations[language].demoPlay;
      demoActive = false;
      return;
    }
    setStage(0);
    toggle.setAttribute("aria-pressed", "true");
    toggle.textContent = translations[language].demoPause;
    demoTimer = window.setTimeout(advanceDemo, stageDelays[1] || 170);
  };
  toggle.addEventListener("click", () => {
    if (demoActive || demoTimer) resetDemo(); else startDemo();
  });
  if (typeof reducedMotion.addEventListener === "function") reducedMotion.addEventListener("change", resetDemo);
  resetDemo();

  document.getElementById("copy-artifact").addEventListener("click", async () => {
    const status = document.getElementById("copy-status");
    const flash = () => {
      status.classList.remove("is-flash");
      void status.offsetWidth;
      status.classList.add("is-flash");
      window.setTimeout(() => status.classList.remove("is-flash"), 900);
    };
    try {
      if (typeof navigator === "undefined" || !navigator.clipboard || typeof navigator.clipboard.writeText !== "function") throw new Error("clipboard unavailable");
      await navigator.clipboard.writeText(copyCommand);
      status.textContent = language === "zh" ? "复现命令已复制。" : "Reproduce command copied.";
      flash();
    } catch {
      status.textContent = (language === "zh" ? "剪贴板不可用，请手动复制：" : "Clipboard unavailable. Copy manually: ") + copyCommand;
    }
  });
  const result = document.getElementById("result");
  const localizedCutline = (cutline) => {
    if (language !== "zh") return cutline || "FINDING";
    return { "MUST FIX": "必须修复", DELETE: "应当删除", "KNOWN DEBT": "已知欠账", FINDING: "发现" }[cutline] || cutline || "发现";
  };
  const verdictClass = (verdict) => {
    const v = String(verdict || "BLOCK").toUpperCase();
    if (v === "PASS") return "is-pass";
    if (v === "PASS_WITH_DEBT" || v.includes("DEBT")) return "is-debt";
    return "is-block";
  };
  const renderReceipt = (label, verdict, risks) => {
    result.replaceChildren();
    result.classList.remove("is-pass", "is-debt", "is-block");
    result.classList.add(verdictClass(verdict));
    addText(result, "p", "result-label", label);
    addText(result, "p", "verdict", verdict || "BLOCK");
    risks.forEach((risk) => {
      const finding = document.createElement("div");
      finding.className = "finding";
      addText(finding, "b", "", localizedCutline(risk.cutline));
      finding.appendChild(document.createTextNode(risk.issue || (language === "zh" ? "未返回可核查的问题。" : "No inspectable finding returned.")));
      result.appendChild(finding);
    });
  };
  const sample = () => renderReceipt(translations[language].resultLabel, "BLOCK", [
    { cutline: "MUST FIX", issue: language === "zh" ? "线上版本与声称提交不一致。回读权威 API 并补上复现命令。" : "Live revision does not match claimed commit. Re-read the authority API and attach a reproduce command." },
    { cutline: "DELETE", issue: language === "zh" ? "「部署成功」提示不能当作生产事实。" : "A \"deployment completed\" message is not a production fact." }
  ]);
  document.getElementById("run-example").addEventListener("click", sample);
  const renderReviewError = (providerSetup) => {
    result.replaceChildren();
    addText(result, "p", "result-label", language === "zh" ? (providerSetup ? "需要配置" : "审查失败") : (providerSetup ? "SETUP REQUIRED" : "REVIEW FAILED"));
    addText(result, "h3", "", language === "zh" ? (providerSetup ? "实时审查需要配置 provider。" : "暂时无法完成审查。") : (providerSetup ? "Live review needs provider setup." : "The review could not be completed."));
    addText(result, "p", "", language === "zh" ? (providerSetup ? "此页面不声称提供云端审查。请运行本地示例，或配置服务器的 /review 路由。" : "请稍后重试，或先运行本地示例。") : (providerSetup ? "This page does not claim cloud review. Use the local example or configure this server's /review route." : "Try again later, or run the local example first."));
    const fallback = addText(result, "button", "button ghost", language === "zh" ? "运行示例并重置" : "Run example and reset");
    fallback.type = "button";
    fallback.addEventListener("click", sample);
  };
  document.getElementById("review-claim").addEventListener("click", async () => {
    const button = document.getElementById("review-claim"), text = document.getElementById("claim").value.trim();
    if (!text) return;
    button.disabled = true;
    result.textContent = language === "zh" ? "正在审查…" : "Reviewing…";
    try {
      const response = await fetch("/review", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, scenario: document.getElementById("scenario").value }) });
      if (!response.ok) {
        const error = new Error(`Review service returned HTTP ${response.status}.`);
        error.providerSetup = response.status === 503;
        throw error;
      }
      const contentType = response.headers.get("content-type") || "";
      if (!contentType.toLowerCase().includes("application/json")) throw new Error("Review service returned a non-JSON response.");
      const data = await response.json();
      renderReceipt(language === "zh" ? "当前审查结果" : "CURRENT /REVIEW ROUTE", data.verdict, Array.isArray(data.risks) ? data.risks : []);
    } catch (error) {
      renderReviewError(Boolean(error && error.providerSetup));
    } finally {
      button.disabled = false;
    }
  });
  /* Sticky nav border on scroll — craft polish (border/bg only; no height animation) */
  const siteHeader = document.querySelector(".site-header");
  if (siteHeader) {
    const onHeaderScroll = () => {
      siteHeader.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    onHeaderScroll();
    window.addEventListener("scroll", onHeaderScroll, { passive: true });
  }

  window.FalsifyFlow = { copyCommand, renderReceipt };
})();
