/**
 * Flow motion: Lenis + GSAP ScrollTrigger section reveals + hero spotlight.
 * DNA from FALSIFY_FLOW_PACK / sui technique notes — no Sui brand assets.
 */
(() => {
  "use strict";

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");

  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn, { once: true });
    else fn();
  }

  ready(() => {
    document.documentElement.classList.add("js-motion");
    initSpotlight();
    if (reduce.matches) {
      document.documentElement.classList.add("reduce-motion");
      revealInstant();
      return;
    }
    const lenis = initLenis();
    initReveals(lenis);
  });

  function initLenis() {
    if (typeof Lenis === "undefined") return null;
    // Snappier than default marketing Lenis — still smooth, not floaty (Emil: perceived speed).
    const lenis = new Lenis({
      duration: 0.85,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      touchMultiplier: 1.6,
    });
    document.documentElement.classList.add("lenis", "lenis-smooth");

    if (typeof gsap !== "undefined" && typeof ScrollTrigger !== "undefined") {
      gsap.registerPlugin(ScrollTrigger);
      lenis.on("scroll", ScrollTrigger.update);
      gsap.ticker.add((time) => lenis.raf(time * 1000));
      gsap.ticker.lagSmoothing(0);
    } else {
      const loop = (t) => {
        lenis.raf(t);
        requestAnimationFrame(loop);
      };
      requestAnimationFrame(loop);
    }

    // Anchor links through Lenis
    document.querySelectorAll('a[href^="#"]').forEach((a) => {
      a.addEventListener("click", (e) => {
        const id = a.getAttribute("href");
        if (!id || id === "#") return;
        const el = document.querySelector(id);
        if (!el) return;
        e.preventDefault();
        lenis.scrollTo(el, { offset: -72, duration: 0.45 });
      });
    });

    return lenis;
  }

  function revealInstant() {
    document.querySelectorAll("[data-reveal]").forEach((el) => el.classList.add("is-in"));
  }

  function initReveals(lenis) {
    const targets = document.querySelectorAll("[data-reveal]");
    if (!targets.length) return;

    const useGsap = typeof gsap !== "undefined" && typeof ScrollTrigger !== "undefined";
    if (useGsap) {
      try {
        gsap.registerPlugin(ScrollTrigger);
        targets.forEach((el) => {
          const kids = el.matches("[data-reveal-stagger]")
            ? el.querySelectorAll(":scope > *")
            : null;
          if (kids && kids.length > 1) {
            el.classList.add("is-in");
            gsap.set(kids, { opacity: 0, y: 10 });
            gsap.to(kids, {
              opacity: 1,
              y: 0,
              duration: 0.32,
              ease: "power2.out",
              stagger: 0.045,
              scrollTrigger: { trigger: el, start: "top 88%", once: true },
            });
          } else {
            gsap.fromTo(
              el,
              { opacity: 0, y: 10 },
              {
                opacity: 1,
                y: 0,
                duration: 0.32,
                ease: "power2.out",
                scrollTrigger: { trigger: el, start: "top 90%", once: true },
              }
            );
          }
        });
        if (lenis) ScrollTrigger.refresh();
        return;
      } catch (err) {
        if (typeof gsap !== "undefined") gsap.set(targets, { clearProps: "all" });
        console.warn("[flow-motion] ScrollTrigger path failed; IO fallback", err);
      }
    }

    // IntersectionObserver fallback (also when gsap-only / ST missing / ST throws)
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );
    targets.forEach((el) => io.observe(el));
  }

  function initSpotlight() {
    const hero = document.querySelector(".hero");
    if (!hero) return;

    let mx = 0.72;
    let my = 0.32;
    let tx = mx;
    let ty = my;
    let raf = 0;

    // Scope CSS vars to .hero (candidate.css already defines defaults + consumers there).
    const set = () => {
      hero.style.setProperty("--spot-x", `${(mx * 100).toFixed(2)}%`);
      hero.style.setProperty("--spot-y", `${(my * 100).toFixed(2)}%`);
      hero.style.setProperty("--text-x", `${(mx * 100).toFixed(2)}%`);
      hero.style.setProperty("--text-y", `${(my * 100).toFixed(2)}%`);
    };
    set();

    if (reduce.matches || !finePointer.matches) return;

    const tick = () => {
      // Slightly snappier spring-ish follow (decorative only).
      mx += (tx - mx) * 0.12;
      my += (ty - my) * 0.12;
      set();
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);

    hero.addEventListener(
      "pointermove",
      (e) => {
        const r = hero.getBoundingClientRect();
        tx = (e.clientX - r.left) / Math.max(1, r.width);
        ty = (e.clientY - r.top) / Math.max(1, r.height);
      },
      { passive: true }
    );
    hero.addEventListener(
      "pointerleave",
      () => {
        tx = 0.72;
        ty = 0.32;
      },
      { passive: true }
    );

    // Clean up not required for SPA-less page; keep raf for life of page
    void raf;
  }

  window.FalsifyFlowMotion = { version: "emil-1" };
})();
