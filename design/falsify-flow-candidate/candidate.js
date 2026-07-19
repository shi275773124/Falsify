(() => {
  "use strict";
  const copyCommand = "curl -sS https://falsify.site/examples/sample-block-report.json | python -m json.tool";
  const translations = {
    en: {
      menuLabel:"Menu",navProof:"Real cases",navDifference:"What it is",navHow:"How it works",navDelivery:"Get it",navTry:"Try",navDocs:"Docs",
      heroTitle:"Challenge the claim. Verify the authority.<br><em>Gate the action.</em>",
      heroEyebrow:"ADVERSARIAL REVIEW · BOUNDED VERDICTS",
      heroPrimary:"Install GitHub Action",heroSecondary:"Watch a claim get blocked",
      heroNote:"Format demo only — not live data. An OSS verdict is epistemic: it bounds what was proven and does not authorize an action.",
      brandThesis:"Agents say \"trust me.\" Falsify signs only what was actually proven.",
      heroLead:"Falsify uses adversarial AI to uncover what existing checks missed, turns findings into executable evidence checks, and issues a verdict bounded to what was actually proven.",
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
      demoCaption:"Format demo only: claim → attack → evidence check → verdict with scope and ceiling. Not live data — the local fixture demo reproduces this false green deterministically.",
      cutlineKicker:"04 CUTLINE",
      cutlineTitle:"NO EVIDENCE.<br><em>NO PASS.</em>",
      cutlineLead:"A deployment claim is not a production fact. Falsify checks the claim against executable evidence — not against another summary.",
      stripClaim:"CLAIM",stripAuth:"EVIDENCE",
      clarityUser:"WHO",clarityUserText:"Teams shipping AI-written PRs, deploys, and decision docs",
      clarityTrigger:"WHEN",clarityTriggerText:"Before you merge or ship on an AI claim of \"done\"",
      clarityAction:"WHAT",clarityActionText:"Attack the claim, then verify it against executable evidence",
      clarityArtifact:"OUTPUT",clarityArtifactText:"A verdict receipt with claim scope and authority ceiling",
      proofLabel:"THREE DOCUMENTED FALSE-GREENS",proofTitle:"Start with proof, not process.",
      proofLead:"Each case looked green at the surface. Each failed when the claim met its real evidence or authority path.",
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
      differenceLabel:"THE CATEGORY LINE",differenceTitle:"Not another model opinion — a verdict with a boundary.",
      differenceLead:"The LLM attacks the claim and signs a bounded verdict. An authority adapter checks physical facts. The unified kernel decides what that verdict may authorize.",
      bugScanner:"Bug scanner",bugScannerText:"checks a diff for defects",eval:"Eval",evalText:"measures model behavior on a test set",
      secondAi:"Second model",secondAiText:"attacks the claim — never the source of truth",
      falsifyText:"turns attacks into executable evidence checks and signs a verdict bounded to what was proven",
      stepAttackTitle:"Attack",stepFrameTitle:"Frame",stepCheckTitle:"Check",stepVerdictTitle:"Verdict",stepGateTitle:"Gate",
      howLabel:"HOW IT WORKS",howTitle:"Three jobs. One decision contract.",
      howLead:"Adversarial AI attacks the claim, an authority adapter checks the facts, and the kernel bounds what the verdict can do — PASS, PASS_WITH_DEBT, or BLOCK, always with its scope on the receipt.",
      stepAttack:"Adversarial AI attacks the claim and surfaces the failures existing checks missed.",
      stepFrame:"Bind the claim's scope, assumptions, and the authority that could prove it.",
      stepCheck:"Turn findings into executable evidence checks — an adapter can run them against the real system.",
      stepVerdict:"The kernel signs PASS, PASS_WITH_DEBT, or BLOCK, bounded to what was actually proven.",
      stepGate:"No adapter, no action: without an authority adapter the verdict stays epistemic.",
      deliveryLabel:"WHAT YOU CAN GET TODAY",deliveryTitle:"Same kernel. Different authority levels.",
      deliveryLead:"Every offer states its status. Nothing here turns a review into a production or payment gate.",
      d1Name:"Falsify Review",d1Status:"AVAILABLE · OSS",d1Text:"Adversarial LLM review with a bounded epistemic verdict. CLI, local demo, skills, and the GitHub Action template.",
      d2Name:"Falsify Authority Gate",d2Status:"ADAPTER REQUIRED",d2Text:"Runs executable evidence checks against a real authority path. Only then can a PASS bear action. No public adapter ships today.",
      d3Name:"Audit Sprint",d3Status:"AVAILABLE · SERVICE",d3Text:"Claim manifest, kill-shots, evidence pack, and a signed verdict receipt for one high-risk artifact.",
      d4Name:"Production / Quant Pro",d4Status:"DESIGN PARTNER · PRIVATE",d4Text:"Integrated per concrete authority path — deploy, data, or execution. Scoped pilots, not self-serve.",
      d5Name:"Team / Enterprise",d5Status:"TARGET · NOT SHIPPED",d5Text:"Dashboard, SSO, RBAC, retention. Roadmap targets — not delivered features.",
      resultLabel:"FORMAT DEMO ONLY",footerDocs:"Docs",footerContact:"Contact",footerSample:"Sample receipt",contactKicker:"CONTACT THE FOUNDER",contactLead:"Design partnerships, integrations, research collaboration, or product questions — reach Chris Shi directly.",contactTwitter:"X / Twitter",contactEmail:"Email",contactGithub:"GitHub",contactEmailLabel:"Email",contactSecurity:"Security reporting",
      tryLabel:"FORMAT DEMO ONLY",tryTitle:"Preview the receipt shape — not full verification",
      tryLead:"This is a format demo only. It does not run a full Falsify gate, a cloud review, or a live state probe. Do not treat it as proof of product capability.",
      runExample:"Run example",copyArtifact:"Copy reproduction command",
      resultTitle:"Ready to preview a format sample.",
      resultLead:"Run the example to see the verdict shape only — not evidence-backed verification.",
      installLabel:"START HERE",installTitle:"Start by gating claims on GitHub.",
      installLead:"Best first step: the GitHub Action reviews PR claims and decision docs and posts a bounded verdict. It gates review — never payments, deploys, or other live actions.",
      actionLink:"Install GitHub Action →",skillsLink:"Install a skill →",verdictLink:"Verdict contract →",
      ctaTitle:"Turn \"trust me\" into a bounded verdict.",
      ctaLead:"Challenge the claim. Verify the authority. Keep the receipt — scope and ceiling included.",
      ctaPrimary:"Install GitHub Action",ctaSecondary:"Format demo only",
      footer:"Adversarial review with a bounded verdict. OSS receipts are epistemic: an action-bearing PASS requires an authority adapter and the unified kernel."
    },
    zh: {
      menuLabel:"菜单",navProof:"真实案例",navDifference:"它是什么",navHow:"工作原理",navDelivery:"如何获取",navTry:"试一试",navDocs:"文档",
      heroTitle:"先攻击声明，再核对权威，<br><em>最后决定能不能放行。</em>",
      heroEyebrow:"对抗式审查 · 有边界的裁决",
      heroPrimary:"安装 GitHub Action",heroSecondary:"看一条声明被拦下",
      heroNote:"仅为格式演示，不是实时数据。开源版裁决只界定已证明的范围，不授权任何动作。",
      brandThesis:"Agent 说「信我」。Falsify 只对真正证明过的范围签发裁决。",
      heroLead:"Falsify 用对抗式 AI 找出既有测试没覆盖到的失败方式，把质疑变成可执行的证据检查，并只对真正证明过的范围签发裁决。",
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
      demoCaption:"仅为格式演示：声明 → 攻击 → 证据检查 → 带范围与上限的裁决。不是实时数据——本地 fixture demo 可确定性复现这个假绿。",
      cutlineKicker:"04 分级",
      cutlineTitle:"没有证据。<br><em>就不能 PASS。</em>",
      cutlineLead:"部署声明不等于生产事实。Falsify 用可执行的证据检查核对声明，而不是再看一份摘要。",
      stripClaim:"声明",stripAuth:"证据",
      clarityUser:"谁在用",clarityUserText:"用 AI 写 PR、部署与决策文档的团队",
      clarityTrigger:"什么时候用",clarityTriggerText:"在合并或上线前，面对 AI 的「已完成」",
      clarityAction:"它做什么",clarityActionText:"先攻击声明，再用可执行的证据核对它",
      clarityArtifact:"留下什么",clarityArtifactText:"一份带声明范围与权威上限的裁决回执",
      proofLabel:"三个有据可查的假绿",proofTitle:"先看证据，再谈框架。",
      proofLead:"表面检查全部通过；一旦沿实际生效路径核对原始记录，假绿就暴露了。",
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
      differenceLabel:"它到底是什么",differenceTitle:"不是又一个模型意见，而是有边界的裁决。",
      differenceLead:"LLM 负责攻击声明并签署边界内裁决；authority adapter 负责核对物理事实；统一 kernel 决定该裁决能否授权动作。",
      bugScanner:"缺陷扫描器",bugScannerText:"检查 diff 里有没有缺陷",eval:"模型评测",evalText:"衡量模型在测试集上的表现",
      secondAi:"第二个模型",secondAiText:"负责攻击声明，永远不是真相来源",
      falsifyText:"把攻击变成可执行的证据检查，并只对真正证明过的范围签发裁决",
      stepAttackTitle:"攻击",stepFrameTitle:"界定",stepCheckTitle:"核对",stepVerdictTitle:"裁决",stepGateTitle:"放行",
      howLabel:"工作原理",howTitle:"三方分工，一份决策契约。",
      howLead:"对抗式 AI 攻击声明，authority adapter 核对事实，kernel 界定裁决能做什么——PASS、PASS_WITH_DEBT 或 BLOCK，回执上永远写明范围。",
      stepAttack:"对抗式 AI 攻击声明，找出既有检查没覆盖到的失败方式。",
      stepFrame:"锁定声明的范围、假设，以及能证明它的权威来源。",
      stepCheck:"把质疑变成可执行的证据检查——adapter 可以对真实系统跑这些检查。",
      stepVerdict:"kernel 签发 PASS、PASS_WITH_DEBT 或 BLOCK，且只对真正证明过的范围生效。",
      stepGate:"没有 adapter 就没有动作：缺少 authority adapter 时，裁决只停留在认知层。",
      deliveryLabel:"今天能拿到什么",deliveryTitle:"同一个 kernel，不同的权威级别。",
      deliveryLead:"每个交付物都标明状态。这里没有任何东西会把一次审查悄悄变成生产或付款闸门。",
      d1Name:"Falsify Review",d1Status:"AVAILABLE · 开源",d1Text:"对抗式 LLM 审查，签发边界内的认知层裁决。含 CLI、本地 demo、skills 与 GitHub Action 模板。",
      d2Name:"Falsify Authority Gate",d2Status:"需要 ADAPTER",d2Text:"对真实权威路径执行可执行的证据检查；只有这样 PASS 才能承载动作。目前没有公开的 adapter。",
      d3Name:"Audit Sprint",d3Status:"AVAILABLE · 服务",d3Text:"针对一个高风险产物：声明清单、kill-shots、证据包，以及签署的裁决回执。",
      d4Name:"Production / Quant Pro",d4Status:"DESIGN PARTNER · 私有",d4Text:"按具体权威路径集成——部署、数据或执行。小规模试点，不自助开放。",
      d5Name:"Team / Enterprise",d5Status:"TARGET · 未交付",d5Text:"Dashboard、SSO、RBAC、留存。路线图目标，不是已交付功能。",
      resultLabel:"仅格式演示",footerDocs:"文档",footerContact:"联系",footerSample:"示例回执",contactKicker:"联系创始人",contactLead:"设计合作、集成、研究协作或产品问题——直接联系 Chris Shi。",contactTwitter:"X / Twitter",contactEmail:"邮箱",contactGithub:"GitHub",contactEmailLabel:"邮箱",contactSecurity:"安全报告",
      tryLabel:"仅格式演示",tryTitle:"预览回执长什么样——不是完整核验",
      tryLead:"这只是格式演示，不会跑完整 Falsify 门禁、云端审查或实时状态探测。请别把它当成产品能力证明。",
      runExample:"运行示例",copyArtifact:"复制复现命令",
      resultTitle:"可以预览格式样例",
      resultLead:"运行示例只看判定长什么样——不是有证据背书的核验。",
      installLabel:"从这里开始",installTitle:"先从 GitHub 拦住声明。",
      installLead:"最稳的第一步：GitHub Action 审查 PR 声明与决策文档并给出有边界的裁决。它管的是审查——永远不管付款、部署或其他实时动作。",
      actionLink:"安装 GitHub Action →",skillsLink:"安装 Skill →",verdictLink:"查看判定约定 →",
      ctaTitle:"把「信我」变成有边界的裁决。",
      ctaLead:"先攻击声明，再核对权威，最后留下带范围与上限的回执。",
      ctaPrimary:"安装 GitHub Action",ctaSecondary:"格式演示",
      footer:"对抗式审查，签发有边界的裁决。开源回执只到认知层：能授权动作的 PASS 需要 authority adapter 与统一 kernel。"
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
  const render = () => {
    const t = translations[language];
    document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
    document.documentElement.setAttribute("data-flow-lang", language);
    document.querySelector(".lang").textContent = language === "zh" ? "EN" : "中文";
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const value = t[el.dataset.i18n];
      if (value) el.textContent = value;
    });
    document.querySelectorAll("[data-i18n-html]").forEach((el) => {
      const value = t[el.dataset.i18nHtml];
      if (value) renderHeroTitle(el, value);
    });
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
    const demoActive = stageIndex > 0 || demoTimer;
    toggle.setAttribute("aria-pressed", demoActive ? "true" : "false");
    toggle.textContent = demoActive ? translations[language].demoPause : translations[language].demoPlay;
    if(window.ScrollTrigger)ScrollTrigger.refresh();
  });
  window.addEventListener("load",function(){if(window.ScrollTrigger)ScrollTrigger.refresh()});
  render();
  const menu = document.querySelector(".menu"), nav = document.querySelector("nav");
  menu.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    menu.setAttribute("aria-expanded", String(open));
  });
  nav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
    nav.classList.remove("open");
    menu.setAttribute("aria-expanded", "false");
  }));

  const receipt = document.querySelector(".demo-receipt");
  const toggle = document.querySelector(".demo-toggle");
  const phaseEl = document.querySelector(".receipt-phase");
  // claim → success card → frame/compare intro → commits lit → conflict → block+receipt
  const stages = ["claim", "success", "compare", "mismatch", "conflict", "block"];
  // Per-stage dwell (ms): open fast, hold conflict slightly longer, then stamp BLOCK.
  const stageDelays = [0, 260, 280, 300, 340, 0];
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let demoTimer = 0, stageIndex = 0;
  const stopDemo = () => { if (demoTimer) window.clearTimeout(demoTimer); demoTimer = 0; };
  const setStage = (index) => {
    stageIndex = Math.min(index, stages.length - 1);
    receipt.dataset.demoState = stages[stageIndex];
    if (phaseEl) phaseEl.textContent = phaseLabels[language][stageIndex];
  };
  const resetDemo = () => {
    stopDemo();
    setStage(0);
    toggle.setAttribute("aria-pressed", "false");
    toggle.textContent = translations[language].demoPlay;
  };
  const advanceDemo = () => {
    if (stageIndex >= stages.length - 1) {
      stopDemo();
      return;
    }
    setStage(stageIndex + 1);
    if (stageIndex >= stages.length - 1) {
      stopDemo();
      return;
    }
    demoTimer = window.setTimeout(advanceDemo, stageDelays[stageIndex] || 280);
  };
  const startDemo = () => {
    stopDemo();
    if (reducedMotion.matches) {
      setStage(stages.length - 1);
      toggle.setAttribute("aria-pressed", "true");
      toggle.textContent = translations[language].demoPause;
      return;
    }
    setStage(1);
    toggle.setAttribute("aria-pressed", "true");
    toggle.textContent = translations[language].demoPause;
    demoTimer = window.setTimeout(advanceDemo, stageDelays[1] || 260);
  };
  toggle.addEventListener("click", () => {
    if (stageIndex > 0 || demoTimer) resetDemo(); else startDemo();
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
  const renderReceipt = (label, verdict, risks) => {
    result.replaceChildren();
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
  window.FalsifyFlow = { copyCommand, renderReceipt };
})();
