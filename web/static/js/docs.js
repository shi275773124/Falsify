(function () {
  const STORAGE_KEY = "falsify-lang";

  function readStoredLang() {
    try {
      return localStorage.getItem(STORAGE_KEY) === "zh" ? "zh" : "en";
    } catch (_e) {
      return "en";
    }
  }

  function writeStoredLang(lang) {
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (_e) {
      /* ignore */
    }
  }

  function urlLang() {
    return new URLSearchParams(window.location.search).get("lang") === "zh" ? "zh" : null;
  }

  function syncUrlWithStorage() {
    const stored = readStoredLang();
    const fromUrl = urlLang();
    if (fromUrl) {
      writeStoredLang(fromUrl);
      return fromUrl;
    }
    if (stored === "zh") {
      const u = new URL(window.location.href);
      u.searchParams.set("lang", "zh");
      window.location.replace(u.toString());
      return stored;
    }
    return "en";
  }

  const T = {
    en: {
      nav_docs: "Docs",
      nav_home: "Home",
      nav_github: "GitHub",
      docs_title_suffix: "Falsify docs",
      index_h1: "Documentation",
      index_lead:
        "Install the PR gate, learn the framework, and ship decision artifacts your team can defend.",
      section_featured: "Featured",
      card_open: "Open guide",
      untranslated:
        "This page is not yet available in Chinese. Showing the English version.",
    },
    zh: {
      nav_docs: "文档",
      nav_home: "首页",
      nav_github: "GitHub",
      docs_title_suffix: "Falsify 文档",
      index_h1: "文档",
      index_lead: "安装 PR 闸门、理解框架，产出团队能辩护的决策产物。",
      section_featured: "精选",
      card_open: "打开指南",
      untranslated: "此页暂无中文版，以下为英文原文。",
    },
  };

  const SECTIONS = {
    en: {
      Start: "Start",
      Framework: "Framework",
      Product: "Product",
      Ops: "Ops",
      Featured: "Featured",
    },
    zh: {
      Start: "入门",
      Framework: "框架",
      Product: "产品",
      Ops: "运维",
      Featured: "精选",
    },
  };

  let lang = syncUrlWithStorage();

  function applyLang() {
    const isZh = lang === "zh";
    document.documentElement.lang = isZh ? "zh-CN" : "en";
    document.documentElement.classList.toggle("lang-zh", isZh);
    document.body.classList.toggle("lang-zh", isZh);
    const btn = document.getElementById("lang-btn");
    if (btn) btn.textContent = lang === "en" ? "中文" : "EN";
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const k = el.getAttribute("data-i18n");
      if (T[lang][k] !== undefined) el.textContent = T[lang][k];
    });
    document.querySelectorAll("[data-i18n-section]").forEach((el) => {
      const k = el.getAttribute("data-i18n-section");
      if (SECTIONS[lang][k] !== undefined) el.textContent = SECTIONS[lang][k];
    });
  }

  function toggleLang() {
    lang = lang === "en" ? "zh" : "en";
    writeStoredLang(lang);
    const u = new URL(window.location.href);
    if (lang === "zh") u.searchParams.set("lang", "zh");
    else u.searchParams.delete("lang");
    window.location.href = u.toString();
  }

  const btn = document.getElementById("lang-btn");
  if (btn) btn.addEventListener("click", toggleLang);
  applyLang();
})();
