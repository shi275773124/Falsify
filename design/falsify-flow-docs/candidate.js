(() => {
  const menu = document.getElementById("docs-menu");
  const sidebar = document.getElementById("flow-sidebar");
  const languageButton = document.getElementById("flow-lang");
  const isChinese = new URL(window.location.href).searchParams.get("lang") === "zh";

  // Chinese is a page-level preference: keep it on every same-origin navigation,
  // including the brand/home link and all documentation links.
  if (isChinese) {
    document.querySelectorAll("a[href]").forEach((anchor) => {
      const rawHref = anchor.getAttribute("href");
      if (!rawHref || rawHref.startsWith("#")) return;

      const target = new URL(rawHref, window.location.href);
      if (target.origin !== window.location.origin) return;

      target.searchParams.set("lang", "zh");
      anchor.href = `${target.pathname}${target.search}${target.hash}`;
    });
  }

  const closeMenu = () => {
    if (!menu || !sidebar) return;
    sidebar.classList.remove("open");
    menu.setAttribute("aria-expanded", "false");
    menu.textContent = menu.dataset.openLabel;
  };

  if (menu && sidebar) {
    menu.addEventListener("click", () => {
      const open = sidebar.classList.toggle("open");
      menu.setAttribute("aria-expanded", String(open));
      menu.textContent = open ? menu.dataset.closeLabel : menu.dataset.openLabel;
    });
  }

  if (languageButton) {
    languageButton.addEventListener("click", () => {
      const url = new URL(window.location.href);
      if (url.searchParams.get("lang") === "zh") {
        url.searchParams.delete("lang");
      } else {
        url.searchParams.set("lang", "zh");
      }
      window.location.assign(url.toString());
    });
  }

  document.querySelectorAll(".flow-docs-sidebar a").forEach((anchor) => {
    anchor.addEventListener("click", closeMenu);
  });
})();
