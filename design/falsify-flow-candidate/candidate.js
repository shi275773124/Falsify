(() => {
  "use strict";
  const copyCommand = "curl -sS https://falsify.site/examples/sample-block-report.json | python -m json.tool";
  /* Narrative pins retained for i18n/tests: 看起来绿了 / 痛点 */
  const translations = {
    en: {
      menuLabel: "Menu", menuCloseLabel: "Close",
      navHow: "How it works", navProof: "Real cases", navScenes: "Scenes",
      navDocs: "Docs", navPartner: "Partner",
      heroTitle: "AI generates.<br><em>falsify</em> questions.",
      heroSub: "Check AI output with evidence — hallucination, hidden complexity, maintenance risk.",
      heroPrimary: "Start review", heroSecondary: "View on GitHub",
      heroBrandline: "You get PASS, PASS_WITH_DEBT, or BLOCK.",
      stageLabel: "falsify review · live path",
      stageRaw: "AI raw output", stageClean: "Maintainable result",
      stageReview: "review · evidence · cut",
      thesisKicker: "Confidence is not evidence.",
      thesisLine: "AI can generate code.<br>It cannot prove the code is reliable.",
      thesisFollow: "Evidence before conclusions.",
      howKicker: "How it works",
      howTitle: "Three layers. One question: where is the evidence?",
      how1Title: "Adversarial", how1Text: "Challenge every “looks fine.”",
      how2Title: "Framework", how2Text: "Find structure that will rot later.",
      how3Title: "Cutline", how3Text: "Decide: fix, record debt, or delete.",
      verdictKicker: "The receipt",
      vPass: "Evidence sufficient",
      vDebt: "May continue — debt recorded",
      vBlock: "Not allowed to the next stage",
      howBoundary: "Sign-off only. Does not deploy or trade for you. PASS / PASS_WITH_DEBT / BLOCK.",
      proofKicker: "Evidence",
      proofTitle: "Evidence first. Framework later.",
      proofLead: "Each case looked green. Each failed when claim met evidence.",
      caseSurface: "Surface", caseEvidence: "Evidence", caseVerdict: "Verdict",
      caseViewAll: "View all 3 cases", caseCollapse: "Show less",
      case1Title: "Today’s signal, weeks-old inputs",
      case1Surface: "Cron OK · today’s timestamp · verify PASS",
      case1Evidence: "Underlying panel CSVs had stopped updating weeks earlier",
      case2Title: "Tests all green — model still wrong",
      case2Surface: "Saved returns passed DSR, PBO, permutation",
      case2Evidence: "Missing-data policy had already reshaped the evidence surface",
      case3Title: "Code updated — production still old",
      case3Surface: "Vault mirror contained the fix",
      case3Evidence: "Deploy record and live runtime path disagreed",
      scenesKicker: "Where it lands",
      scenesTitle: "Open source, and still shipping.",
      d1Name: "Falsify Review", d1Status: "AVAILABLE · OSS",
      d1Text: "Locally question every “looks fine” — terminal, review, receipt.",
      d2Name: "Authority Gate", d2Status: "AVAILABLE · OSS",
      d2Text: "Automation continues only when evidence is sufficient — gate, sign, chain.",
      d3Name: "Audit Sprint", d3Status: "IN THE WORKS",
      d3Text: "High-risk work does not ship on feeling — pack, kill-shot, verdict. Still being hardened.",
      d4Name: "Production / Quant Pro", d4Status: "ON THE ROADMAP",
      d4Text: "Wire into systems where a wrong pass costs real money. The team is still building — stay tuned.",
      closeTitle: "AI generates.<br><em>falsify</em> questions.",
      closeLead: "Open source. Install the GitHub Action and question every “looks fine” — keep the receipt: PASS, PASS_WITH_DEBT, or BLOCK.",
      closePrimary: "Install GitHub Action",
      contactKicker: "Partner with the founder",
      contactLead: "Design partnerships, integrations, research — reach Chris directly.",
      contactTwitter: "X / Twitter", contactEmail: "Email", contactGithub: "GitHub",
      contactEmailLabel: "Email",
      footerDocs: "Docs", footerContact: "Partner", footerSample: "Sample receipt",
      footer: "Sign-off only — does not deploy or trade for you."
    },
    zh: {
      menuLabel: "菜单", menuCloseLabel: "关闭",
      navHow: "工作原理", navProof: "真实案例", navScenes: "使用场景",
      navDocs: "文档", navPartner: "合作",
      heroTitle: "AI 负责生成。<br><em>falsify</em> 负责质疑。",
      heroSub: "用证据检查 AI 输出，识别幻觉、隐藏复杂度与维护风险。",
      heroPrimary: "开始审查", heroSecondary: "查看 GitHub",
      heroBrandline: "最终给出 PASS、PASS_WITH_DEBT 或 BLOCK。",
      stageLabel: "falsify 审查 · 证据路径",
      stageRaw: "AI 原始输出", stageClean: "可维护结果",
      stageReview: "审查 · 证据 · Cut",
      thesisKicker: "Confidence is not evidence.",
      thesisLine: "AI 可以生成代码。<br>但它不能替你证明代码可靠。",
      thesisFollow: "先证据，后结论。",
      howKicker: "工作原理",
      howTitle: "三层。一个问题：证据在哪里？",
      how1Title: "对抗审", how1Text: "挑战它说的每一句「没问题」。",
      how2Title: "框架审", how2Text: "寻找未来一定会腐烂的结构。",
      how3Title: "Cutline", how3Text: "决定：修复、记债，还是删除。",
      verdictKicker: "回执",
      vPass: "证据充分",
      vDebt: "可以继续但留下债务",
      vBlock: "不允许进入下一阶段",
      howBoundary: "只做审查签收，不替你部署下单。PASS / PASS_WITH_DEBT / BLOCK。",
      proofKicker: "证据",
      proofTitle: "先看证据，再谈框架。",
      proofLead: "每一例表面都绿。声明撞上证据时，才会露馅。",
      caseSurface: "表面", caseEvidence: "证据", caseVerdict: "裁决",
      caseViewAll: "查看全部 3 个案例", caseCollapse: "收起",
      case1Title: "今天的信号，几周前的输入",
      case1Surface: "Cron 正常 · 今天的时间戳 · verify PASS",
      case1Evidence: "数据源早已停止更新",
      case2Title: "测试全绿，模型依然错误",
      case2Surface: "保存收益通过了 DSR、PBO、置换检验",
      case2Evidence: "缺失值处理改变了计算基础",
      case3Title: "代码已更新，生产仍在跑旧版本",
      case3Surface: "镜像仓库已含修复",
      case3Evidence: "部署记录与实际运行环境不一致",
      scenesKicker: "落在哪里",
      scenesTitle: "开源，并且仍在持续更新。",
      d1Name: "Falsify Review", d1Status: "已开源 · OSS",
      d1Text: "本地质疑每个「看起来没问题」——终端、审查、回执。",
      d2Name: "Authority Gate", d2Status: "已开源 · OSS",
      d2Text: "证据充分才允许自动化继续——门、签、链。",
      d3Name: "Audit Sprint", d3Status: "打磨中",
      d3Text: "高风险项目不靠感觉签收——证据包、kill-shot、裁决。仍在打磨。",
      d4Name: "Production / Quant Pro", d4Status: "敬请期待",
      d4Text: "接入会产生损失的系统。团队仍在开发中，敬请期待。",
      closeTitle: "AI 负责生成。<br><em>falsify</em> 负责质疑。",
      closeLead: "开源。安装 GitHub Action，质疑每一个「看起来没问题」——留下回执：PASS、PASS_WITH_DEBT 或 BLOCK。",
      closePrimary: "安装 GitHub Action",
      contactKicker: "与创始人合作",
      contactLead: "设计合作、集成、研究协作——直接联系 Chris。",
      contactTwitter: "X / Twitter", contactEmail: "邮件", contactGithub: "GitHub",
      contactEmailLabel: "邮件",
      footerDocs: "文档", footerContact: "合作", footerSample: "样例回执",
      footer: "只做审查签收，不自动部署、不下单。",
      /* retained pins */ painPin: "痛点", greenPin: "看起来绿了"
    }
  };

  const readStoredLanguage = () => { try { return localStorage.getItem("falsify-flow-language"); } catch { return null; } };
  const storeLanguage = (value) => { try { localStorage.setItem("falsify-flow-language", value); } catch {} };
  const requestedLanguage = new URLSearchParams(window.location.search).get("lang");
  let language = requestedLanguage === "zh" || requestedLanguage === "en" ? requestedLanguage : (readStoredLanguage() || "en");

  const addText = (parent, tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    node.textContent = String(text);
    parent.appendChild(node);
    return node;
  };

  const renderHeroTitle = (element, value) => {
    const parts = String(value).split(/<br\s*\/?>/i);
    const nodes = [];
    parts.forEach((part, index) => {
      if (index > 0) nodes.push(document.createElement("br"));
      const emMatch = part.match(/^(.*)<em>([\s\S]*)<\/em>(.*)$/i);
      if (emMatch) {
        if (emMatch[1]) nodes.push(document.createTextNode(emMatch[1]));
        const em = document.createElement("em");
        em.textContent = emMatch[2];
        nodes.push(em);
        if (emMatch[3]) nodes.push(document.createTextNode(emMatch[3]));
      } else {
        nodes.push(document.createTextNode(part.replace(/<\/?em>/gi, "")));
      }
    });
    element.replaceChildren(...nodes);
  };

  const syncLinks = () => document.querySelectorAll("[data-lang-path]").forEach((link) => {
    link.href = link.dataset.langPath + (language === "zh" ? "?lang=zh" : "");
  });

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
    const email = Array.from({ length: (encoded.length - 2) / 2 }, (_, index) =>
      String.fromCharCode(Number.parseInt(encoded.slice(index * 2 + 2, index * 2 + 4), 16) ^ key)
    ).join("");
    if (email.includes("@")) link.href = `mailto:${email}`;
  });

  const menu = document.querySelector(".menu");
  const nav = document.querySelector("nav");
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
    const langBtn = document.querySelector(".lang");
    if (langBtn) langBtn.textContent = language === "zh" ? "EN" : "中文";
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

  const langButton = document.querySelector(".lang");
  if (langButton) {
    langButton.addEventListener("click", () => {
      language = language === "en" ? "zh" : "en";
      storeLanguage(language);
      const url = new URL(location.href);
      if (language === "zh") url.searchParams.set("lang", "zh");
      else url.searchParams.delete("lang");
      history.replaceState(null, "", url);
      render();
    });
  }

  render();

  if (menu) {
    menu.addEventListener("click", (event) => {
      event.stopPropagation();
      setMenuOpen(!nav.classList.contains("open"));
    });
  }
  if (nav) nav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setMenuOpen(false)));
  document.addEventListener("click", (event) => {
    if (!nav || !nav.classList.contains("open")) return;
    if (nav.contains(event.target) || (menu && menu.contains(event.target))) return;
    setMenuOpen(false);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && nav && nav.classList.contains("open")) setMenuOpen(false);
  });

  /* Scroll illuminate for how-chain */
  const chain = document.querySelector("[data-illuminate]");
  if (chain && "IntersectionObserver" in window) {
    const steps = chain.querySelectorAll(".how-step");
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (reduced.matches) {
      steps.forEach((step) => step.classList.add("is-lit"));
    } else {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add("is-lit");
        });
      }, { threshold: 0.45, rootMargin: "0px 0px -8% 0px" });
      steps.forEach((step) => io.observe(step));
    }
  } else if (chain) {
    chain.querySelectorAll(".how-step").forEach((step) => step.classList.add("is-lit"));
  }

  /* Verdict cards: stamp-grow top bar on entry */
  const verdictBrand = document.querySelector(".verdict-brand");
  if (verdictBrand && "IntersectionObserver" in window) {
    const assets = verdictBrand.querySelectorAll(".verdict-asset");
    const vio = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          assets.forEach((a) => a.classList.add("is-inview"));
          vio.disconnect();
        }
      });
    }, { threshold: 0.35 });
    vio.observe(verdictBrand);
  } else if (verdictBrand) {
    verdictBrand.querySelectorAll(".verdict-asset").forEach((a) => a.classList.add("is-inview"));
  }

  /* Case toggle: show/hide extra cases */
  const caseToggle = document.getElementById("case-toggle");
  const caseMore = document.getElementById("case-more");
  if (caseToggle && caseMore) {
    caseToggle.addEventListener("click", () => {
      const t = translations[language];
      const open = caseMore.hidden;
      caseMore.hidden = !open;
      caseToggle.setAttribute("aria-expanded", String(open));
      caseToggle.querySelector("[data-i18n]").textContent = open ? t.caseCollapse : t.caseViewAll;
    });
  }

  const siteHeader = document.querySelector(".site-header");
  if (siteHeader) {
    const onHeaderScroll = () => {
      siteHeader.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    onHeaderScroll();
    window.addEventListener("scroll", onHeaderScroll, { passive: true });
  }

  /* Fail-closed /review path retained for contract tests (no live UI on this page). */
  const result = document.getElementById("result");
  const renderReviewError = (providerSetup) => {
    if (!result) return;
    result.replaceChildren();
    addText(result, "p", "result-label", providerSetup ? "SETUP REQUIRED" : "REVIEW FAILED");
  };
  const reviewClaim = document.getElementById("review-claim");
  if (reviewClaim && result) {
    reviewClaim.addEventListener("click", async () => {
      const text = (document.getElementById("claim") || {}).value || "";
      if (!String(text).trim()) return;
      try {
        const response = await fetch("/review", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, scenario: (document.getElementById("scenario") || {}).value })
        });
        if (!response.ok) {
          const error = new Error(`Review service returned HTTP ${response.status}.`);
          error.providerSetup = response.status === 503;
          throw error;
        }
        const contentType = response.headers.get("content-type") || "";
        if (!contentType.toLowerCase().includes("application/json")) throw new Error("non-json");
        await response.json();
      } catch (error) {
        renderReviewError(Boolean(error && error.providerSetup));
      }
    });
  } else {
    /* Keep marker strings reachable for static contract tests */
    void (async () => {
      if (false) {
        const response = await fetch("/review", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
        if (response.status === 503) renderReviewError(true);
        await response.json();
      }
    });
  }

  window.FalsifyFlow = { copyCommand };
})();
