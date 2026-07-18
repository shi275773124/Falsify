(() => {
  "use strict";
  const copyCommand = "curl -sS https://falsify.site/examples/sample-block-report.json | python -m json.tool";
  const translations = {
    en: {
      menuLabel:"Menu",navProof:"Real cases",navDifference:"What it is",navHow:"How it works",navTry:"Try",navDocs:"Docs",
      heroTitle:"Check the authority.<br><em>Before consequential AI output passes.</em>",
      heroEyebrow:"EVIDENCE GATE · GITHUB FIRST",
      heroPrimary:"Install GitHub Action",heroSecondary:"Run the authority check",
      heroNote:"Format demo only — not live data, not a full gate, not permission to ship.",
      brandThesis:"Agents say \"trust me.\" Falsify turns that into a reproducible verdict.",
      heroLead:"A completion message is a claim, not a fact. Falsify frames the claim, reads the system that holds the truth, and returns a scoped PASS, PASS_WITH_DEBT, or BLOCK receipt.",
      receiptExample:"FALSIFY RECEIPT #0482",receiptPhase:"01 CLAIM",
      proofHeadline:"Agents say \"trust me.\"",
      demoPause:"Reset",demoPlay:"Run example",
      deployBot:"DEPLOY BOT",successPill:"SUCCESS",
      demoClaim:"Deployment completed successfully.",
      envLabel:"ENVIRONMENT",envValue:"production",commitLabel:"COMMIT",
      authorityLine:"AUTHORITY CHECK · GET /v2/projects/.../services/payment-api",
      claimedCommit:"CLAIMED COMMIT",prodCommit:"PRODUCTION COMMIT",
      conflictLabel:"EVIDENCE CONFLICT",
      conflictText:"Live revision does not match the claimed commit.",
      findingLabel:"FINDING",findingText:"Deployed revision does not match claimed commit.",
      authorityLabel:"AUTHORITY",authorityText:"Cloud Run API / payment-api",
      reproduceLabel:"REPRODUCE",
      demoCaption:"Format demo only. Same false-green shape as the product film: claim → frame → authority read → cutline → receipt. Not live data.",
      cutlineKicker:"04 CUTLINE",
      cutlineTitle:"NO EVIDENCE.<br><em>NO PASS.</em>",
      cutlineLead:"A deployment claim is not a production fact. Falsify compares the claim with the authoritative system.",
      stripClaim:"CLAIM",stripAuth:"AUTHORITY",
      clarityUser:"USER",clarityUserText:"Teams shipping AI-written PRs, deploys, and decision docs",
      clarityTrigger:"TRIGGER",clarityTriggerText:"Before you merge, pay, or ship on an AI claim of \"done\"",
      clarityAction:"ACTION",clarityActionText:"Challenge the claim against real state and artifacts",
      clarityArtifact:"ARTIFACT",clarityArtifactText:"Reproducible PASS / BLOCK receipt",
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
      differenceLabel:"THE CATEGORY LINE",differenceTitle:"A gate for high-stakes claims - not another model.",
      bugScanner:"Bug scanner",bugScannerText:"Checks a diff for defects",eval:"Eval",evalText:"Measures model behavior on a test set",
      secondAi:"Second model",secondAiText:"Optional help attacking a claim-never the source of truth",
      falsifyText:"A bounded claim checked against real state, raw artifacts, and explicit policy",
      stepFrameTitle:"Claim",stepAttackTitle:"Frame",stepRecomputeTitle:"Verify",stepCutlineTitle:"Cutline",stepReceiptTitle:"Receipt",
      tierNormal:"Normal",tierProduction:"Production",tierQuant:"Quant",
      howLabel:"HOW THE GATE WORKS",howTitle:"Claim. Frame. Verify. Cutline. Receipt.",
      howLead:"One inspectable decision contract: PASS, PASS_WITH_DEBT, or BLOCK — with an authority path you can re-read.",
      stepFrame:"Surface the AI or bot statement as a claim, not a fact.",
      stepAttack:"Capture scope, assumptions, and the authority that can prove it.",
      stepRecompute:"Read the system that actually holds the truth.",
      stepCutline:"No evidence, no pass — separate Must Fix from Known Debt.",
      stepReceipt:"Leave finding, authority, evidence, and a reproduce command.",
      resultLabel:"FORMAT DEMO ONLY",footerDocs:"Docs",footerContact:"Contact",footerSample:"Sample receipt",contactKicker:"CONTACT THE FOUNDER",contactLead:"Design partnerships, integrations, research collaboration, or product questions — reach Chris Shi directly.",contactTwitter:"X / Twitter",contactEmail:"Email",contactGithub:"GitHub",contactEmailLabel:"Email",contactSecurity:"Security reporting",
      tryLabel:"FORMAT DEMO ONLY",tryTitle:"Preview the receipt shape - not full verification",
      tryLead:"This is a format demo only. It does not run a full Falsify gate, a cloud review, or a live state probe. Do not treat it as proof of product capability.",
      runExample:"Run example",copyArtifact:"Copy reproduction command",
      resultTitle:"Ready to preview a format sample.",
      resultLead:"Run the example to see the verdict shape only - not evidence-backed verification.",
      installLabel:"START HERE",installTitle:"Start by gating claims on GitHub.",
      installLead:"Best first step: a GitHub Action on PR claims and decision docs. CLI and skills stay open-core. Production and quant enforcement stay in Pro.",
      actionLink:"Install GitHub Action →",skillsLink:"Install a skill →",verdictLink:"Verdict contract →",
      ctaTitle:"Turn \"trust me\" into a reproducible verdict.",
      ctaLead:"Before consequential AI output passes — check the authority and keep the receipt.",
      ctaPrimary:"Install GitHub Action",ctaSecondary:"Format demo",
      footer:"Evidence-driven decision gate. Multi-model review is optional. We classify risk-we do not authorize action."
    },
    zh: {
      menuLabel:"菜单",navProof:"真实案例",navDifference:"它是什么",navHow:"如何把关",navTry:"试一试",navDocs:"文档",
      heroTitle:"先核对权威来源。<br><em>再让高后果 AI 输出过关。</em>",
      heroEyebrow:"证据闸门 · 从 GitHub 起步",
      heroPrimary:"安装 GitHub Action",heroSecondary:"跑一遍权威核对",
      heroNote:"仅格式演示 — 不是实时数据，不是完整门禁，也不是上线许可。",
      brandThesis:"Agent 说「信我」。Falsify 把它变成可复现的判定。",
      heroLead:"完成提示只是声明，不是事实。Falsify 界定声明、回读真正持有真相的系统，并返回有范围的 PASS、PASS_WITH_DEBT 或 BLOCK 回执。",
      receiptExample:"FALSIFY 回执 #0482",receiptPhase:"01 声明",
      proofHeadline:"Agent 说「信我」。",
      demoPause:"重置",demoPlay:"运行示例",
      deployBot:"部署机器人",successPill:"SUCCESS",
      demoClaim:"部署已成功完成。",
      envLabel:"环境",envValue:"production",commitLabel:"提交",
      authorityLine:"权威核对 · GET /v2/projects/.../services/payment-api",
      claimedCommit:"声称提交",prodCommit:"生产提交",
      conflictLabel:"证据冲突",
      conflictText:"线上版本与声称的提交不一致。",
      findingLabel:"发现",findingText:"已部署版本与声称提交不一致。",
      authorityLabel:"权威来源",authorityText:"Cloud Run API / payment-api",
      reproduceLabel:"复现",
      demoCaption:"仅格式演示。与产品片同构：声明 → 界定 → 权威回读 → 分级 → 回执。不是实时数据。",
      cutlineKicker:"04 分级",
      cutlineTitle:"没有证据。<br><em>就不能 PASS。</em>",
      cutlineLead:"部署声明不等于生产事实。Falsify 把声明与权威系统对照。",
      stripClaim:"声明",stripAuth:"权威",
      clarityUser:"谁会用",clarityUserText:"用 AI 写 PR、部署与决策文档的团队",
      clarityTrigger:"什么时候",clarityTriggerText:"在合并、付款或上线前，面对 AI 的「已完成」",
      clarityAction:"它做什么",clarityActionText:"对照真实状态与原始材料反查声明",
      clarityArtifact:"留下什么",clarityArtifactText:"一份能复查的 PASS / BLOCK 回执",
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
      differenceLabel:"它到底是什么",differenceTitle:"决策闸门，不是又一个模型。",
      bugScanner:"缺陷扫描器",bugScannerText:"看代码改动里有没有 bug",eval:"模型评测",evalText:"看模型在测试题里表现怎样",
      secondAi:"第二个模型",secondAiText:"可选的挑刺手段--不是真相来源",
      falsifyText:"把有限声明放到真实状态、原始材料和明确策略上核对",
      stepFrameTitle:"声明",stepAttackTitle:"界定",stepRecomputeTitle:"核对",stepCutlineTitle:"分级",stepReceiptTitle:"回执",
      tierNormal:"常规",tierProduction:"生产",tierQuant:"量化",
      howLabel:"Falsify 怎么做",howTitle:"声明 · 界定 · 核对 · 分级 · 回执",
      howLead:"公开核心只有三种可检查的判定：PASS、PASS_WITH_DEBT、BLOCK——并且能回读权威路径。",
      stepFrame:"把 AI 或机器人的表述先当成声明，而不是事实。",
      stepAttack:"写清范围、假设，以及能证明它的权威来源。",
      stepRecompute:"回读真正持有真相的系统。",
      stepCutline:"没有证据就不能 PASS——把必须修复与已知欠账分开。",
      stepReceipt:"留下发现、权威、证据与复现命令。",
      resultLabel:"仅格式演示",footerDocs:"文档",footerContact:"联系",footerSample:"示例回执",contactKicker:"联系创始人",contactLead:"设计合作、集成、研究协作或产品问题 — 直接联系 Chris Shi。",contactTwitter:"X / Twitter",contactEmail:"邮箱",contactGithub:"GitHub",contactEmailLabel:"邮箱",contactSecurity:"安全报告",
      tryLabel:"仅格式演示",tryTitle:"预览回执长什么样--不是完整核验",
      tryLead:"这只是格式演示，不会跑完整 Falsify 门禁、云端审查或实时状态探测。请别把它当成产品能力证明。",
      runExample:"运行示例",copyArtifact:"复制复现命令",
      resultTitle:"可以预览格式样例",
      resultLead:"运行示例只看判定长什么样--不是有证据背书的核验。",
      installLabel:"从这里开始",installTitle:"先从 GitHub 拦住声明",
      installLead:"最稳的第一步：用 GitHub Action 卡住 PR 声明与决策文档。CLI 与 skill 仍属公开版；生产与量化强制仍在 Pro。",
      actionLink:"安装 GitHub Action →",skillsLink:"安装 Skill →",verdictLink:"查看判定约定 →",
      ctaTitle:"把「信我」变成可复现的判定。",
      ctaLead:"高后果 AI 输出过关前——先核对权威来源，并留下回执。",
      ctaPrimary:"安装 GitHub Action",ctaSecondary:"格式演示",
      footer:"证据驱动的决策闸门。多模型审查可选。我们只给风险分类--不替你批准行动。"
    }
  };
  const phaseLabels = {
    en: ["01 CLAIM", "02 FRAME", "03 VERIFY", "03 VERIFY", "04 CUTLINE", "05 RECEIPT"],
    zh: ["01 声明", "02 界定", "03 核对", "03 核对", "04 分级", "05 回执"]
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
    syncTierCopy();
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
  const tierCopy = {
    en: {
      normal: "Core receipt and reproducible evidence for a bounded claim.",
      production: "Add state verification, rollback, and accountable operational evidence.",
      quant: "Add data semantics, execution mechanics, and an explicit claim ceiling."
    },
    zh: {
      normal: "针对范围明确的判断，保留回执和可复现记录。",
      production: "增加状态核验、回滚方案和责任明确的运行记录。",
      quant: "增加数据定义、执行方式和明确的适用范围。"
    }
  };
  const syncTierCopy = () => {
    const active = document.querySelector(".tier.active");
    document.getElementById("tier-copy").textContent = tierCopy[language][active.dataset.tier];
  };
  document.querySelectorAll(".tier").forEach((button) => button.addEventListener("click", () => {
    document.querySelectorAll(".tier").forEach((item) => { item.classList.remove("active"); item.setAttribute("aria-pressed", "false"); });
    button.classList.add("active");
    button.setAttribute("aria-pressed", "true");
    syncTierCopy();
  }));
  syncTierCopy();

  const receipt = document.querySelector(".demo-receipt");
  const toggle = document.querySelector(".demo-toggle");
  const phaseEl = document.querySelector(".receipt-phase");
  // claim → success card → frame/compare intro → commits lit → conflict → block+receipt
  const stages = ["claim", "success", "compare", "mismatch", "conflict", "block"];
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let demoTimer = 0, stageIndex = 0;
  const stopDemo = () => { if (demoTimer) window.clearInterval(demoTimer); demoTimer = 0; };
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
    demoTimer = window.setInterval(() => {
      if (stageIndex >= stages.length - 1) { stopDemo(); return; }
      setStage(stageIndex + 1);
    }, 480);
  };
  toggle.addEventListener("click", () => {
    if (stageIndex > 0 || demoTimer) resetDemo(); else startDemo();
  });
  if (typeof reducedMotion.addEventListener === "function") reducedMotion.addEventListener("change", resetDemo);
  resetDemo();

  document.getElementById("copy-artifact").addEventListener("click", async () => {
    const status = document.getElementById("copy-status");
    try {
      if (typeof navigator === "undefined" || !navigator.clipboard || typeof navigator.clipboard.writeText !== "function") throw new Error("clipboard unavailable");
      await navigator.clipboard.writeText(copyCommand);
      status.textContent = language === "zh" ? "复现命令已复制。" : "Reproduce command copied.";
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
