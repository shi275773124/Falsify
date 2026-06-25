# Falsify Homepage Redesign — Competitor Teardown & Rebuild Spec

> **Date**: 2026-06-24  
> **Purpose**: Phase 2 teardown before any homepage rebuild. Phase 3 rebuild spec for Chris review.  
> **Constraint**: 框架审计 on marketing (not Brooks-Lint). Keep quote A + hero_layers content; redesign presentation only.

---

## Part 1 — Competitor Teardown

### 1. Detail (detail.dev)

**Above-fold (5 sec layout grid)**  
- Full-viewport **black** canvas; content is **left-weighted** (~55% copy / ~45% negative space).  
- Giant **H1** stacked 2–3 lines; no product screenshot in hero — instead a **neon-green diagonal slash** (brand mark) cuts across the right half.  
- **Dual CTA row** directly under subhead: primary filled green `Try For Free` + secondary outline `Talk to an Engineer`.  
- Nav is minimal: OSS · About · Pricing · Experiments · login — no mega-menu.  
- First scroll is **not** features — it's a **testimonial wall** (CTO quotes with company names).

**Typography scale**  
- H1: ~56–72px, tight line-height (~1.0), sans-serif (Framer default / similar to Inter).  
- Body: 16–18px, muted gray on black.  
- CTAs: **monospace** labels — signals devtool, not SaaS brochure.  
- Section H2: ~32–40px; step labels use small caps / numbered `#####` style.

**Color**  
- Background: `#000` / near-black.  
- Accent: **neon green** (~#B8FF3C family) — used on slash, primary CTA, links; **~8–12%** of visible pixels.  
- Red: absent in hero; severity implied by copy, not UI chrome.  
- White/gray text hierarchy: H1 white, body #aaa, meta #666.

**Imagery**  
- **No fake product UI** in hero.  
- Proof = **real OSS scan cards** (Tailscale, Next.js, Kubernetes) with bug counts + language tags.  
- Testimonials = real names + titles + companies (Sourcegraph, Notion, Vanta, OpenRouter).

**Section count (homepage)**  
~6 scrolls: Hero → Testimonials → OSS proof grid → How it works (3 steps) → Enterprise trust (2 cards) → Footer. **No pricing grid on homepage** (links to /pricing).

**CTA pattern**  
- Primary: `Try For Free` (app) — appears **3×** (nav, hero, footer).  
- Secondary: `Talk to an Engineer` (Calendly) — **2×** (hero, nav area).  
- No third "Book demo" variant.

**What they deliberately DON'T show**  
- No 3-column pricing on homepage.  
- No animated pipeline diagram.  
- No workbench / paste-and-go demo on marketing site.  
- No feature grid with 9 cards.  
- No GitHub Action YAML mock.

**3 screenshots worth stealing (describe precisely)**  
1. **Hero slash + monospace dual CTA** — black field, green diagonal, blunt H1 ("Your codebase is full of bugs"), two buttons with different visual weight.  
2. **OSS proof card** — repo name, language pill, "7 bugs flagged / 5 fixed", star count; feels like **evidence not marketing**.  
3. **3-step How it works** — numbered steps with one sentence each, no icons, no cards-with-shadows; editorial not PPT.

---

### 2. Factory.ai

**Above-fold (5 sec layout grid)**  
- **Full-bleed dark dashboard** as hero visual — not a static mock; reads as **live ops console** (SIGNALS / 7DAY, throughput, cycle times).  
- Headline area is **compact** above or beside the dashboard; brand = **industrial telemetry**, not copy-heavy.  
- Logo row: "Trusted by leading engineering teams" with grayscale logos.  
- Single CTA: `start building` — low friction, not enterprise sales.

**Typography scale**  
- Dashboard labels: **10–11px mono**, uppercase, letter-spaced (`SIGNALS`, `THROUGHPUT`).  
- Metric values: **24–32px bold** tabular nums.  
- Marketing H2: moderate (~28px); body sparse — **UI carries the story**.

**Color**  
- Background: charcoal / blue-black (`#0a0a0f` family).  
- Accent: **cyan/teal** on active metrics + sparklines; green only on "pass" states.  
- Red/amber: incident + validation failure states **inside the dashboard** — narrative color.  
- Accent **~15%** — higher than Detail because the hero *is* the accent (charts, lines).

**Imagery**  
- **Real UI screenshot aesthetic** — multi-panel grid, mini charts, KPI strips.  
- Not illustration; not CSS wireframe boxes.  
- Pipeline story = **6 stages** (Input → Triage → Code Gen → Validate → Release → Document → Monitor) shown as **tabs/stages with live numbers**.

**Section count**  
~4–5 scrolls on homepage: Dashboard hero → logo strip → stage explainer → CTA → footer. **Very few prose sections**.

**CTA pattern**  
- One primary throughout; no pricing grid.  
- Conversion = **start building** (product-led), not "talk to sales".

**What they deliberately DON'T show**  
- No testimonial carousel.  
- No 3-column feature cards.  
- No "$99/mo" pricing.  
- No long philosophy essay above fold.

**3 screenshots worth stealing**  
1. **Pipeline KPI header** — horizontal stage strip with real metrics per gate (throughput, cycle time, pass rate).  
2. **Sparkline + delta %** — "PRS -43% This week" with mini chart; makes abstract process **measurable**.  
3. **Dark grid panel** — rounded rect modules, 1px borders, mono labels; **designed density** not wireframe boxes.

---

### 3. Rig AI (rig.ai)

**Above-fold (5 sec layout grid)**  
- **Centered stack**: eyebrow → H1 (2 lines) → sub → dual CTA (`Join Waitlist` + `Our Approach`).  
- Below fold: **marquee ticker** of value props (Zero telemetry · Native inference · …).  
- Hero has **no product screenshot** — terminal aesthetic comes later.

**Typography scale**  
- H1: ~48–64px, heavy weight, tight tracking.  
- Section labels: `Step 01` mono prefixes.  
- Body: 16px; **high contrast** white on near-black.  
- Terminal block: 13px mono with ASCII art logo.

**Color**  
- Background: **pure dark** (#050505).  
- Accent: **white** primarily; red used for "MONITORING ACTIVE / TELEMETRY" alarm UI.  
- Green: only in terminal `OK` states.  
- Accent discipline: **alarm red** for enemy (cloud); **neutral** for product — adversarial through **copy + diagram**, not lime green everywhere.

**Imagery**  
- **Concept diagrams**: cloud severed from laptop, firewall blocks, latency bar comparisons.  
- **Terminal mock** with real commands (`rig init`, hardware scan).  
- Comparison tables (Rig vs Cloud models) — **spec sheet**, not cards.

**Section count**  
~8–9 scrolls — longer page, but each section is **one idea**: Problem (4 cards) → Solution diagram → Offline/Unlimited/Privacy/Latency → 3-step approach → Capabilities grid → Terminal → FAQ → CTA.

**CTA pattern**  
- `Join Waitlist` repeated 3×; secondary `Our Approach` anchor scroll.  
- No free trial — waitlist = scarcity.

**What they deliberately DON'T show**  
- No pricing table.  
- No customer logo wall (pre-launch).  
- No fake GitHub PR UI.  
- No "3 verdicts" style protocol jargon above fold.

**3 screenshots worth stealing**  
1. **Cloud severed diagram** — laptop vs cloud with literal "Severed" label; one visual = entire thesis.  
2. **Comparison bar chart** (model size / latency / cost) — Rig bar tiny green vs cloud bars huge.  
3. **Terminal hero block** — dark panel, green `OK`, monospace boot sequence; **authentic dev surface**.

---

### 4. CodeRabbit (coderabbit.ai) — Craftwork-adjacent devtool B2B

**Above-fold (5 sec layout grid)**  
- **Centered hero**: H1 with **metric hook** ("Cut code review time & bugs in half").  
- Sub + **two CTAs**: `Try it for free` + `2-click install` badge.  
- Below: **stat strip** (6M repos · 75M defects · Most installed AI App).  
- Then **logo carousel** + Jensen Huang quote **before** feature explanation.

**Typography scale**  
- H1: ~48–56px, bold sans.  
- Stat numbers: **40–48px** bold.  
- Feature section labels: `CR_Flexibility` mono anchors.  
- Body: 16px; feature cards ~14px.

**Color**  
- Background: dark navy-black.  
- Accent: **orange** (~#FF570A) on CTAs, highlights, code comments in mocks.  
- Green: minimal; red for defect severity in PR mocks.  
- Orange **~10%** — disciplined to CTA + section tags.

**Imagery**  
- **Real PR review screenshots** + embedded video.  
- `See a sample review` links to **live GitHub PR** — not fabricated JSON.  
- IDE/CLI/GIT triptych icons for "reviews everywhere".

**Section count**  
~7–8 scrolls: Hero → stats → logos → quote → problem statement → 6 feature tiles → CR_Flexibility/Quality/Intelligence (3 mega-sections) → Security → video CTA → testimonial carousel.

**CTA pattern**  
- `Try it for free` / `Start reviewing` — **4+** placements.  
- `See a sample review` — proof CTA, not sales.  
- `See pricing` secondary only at bottom.

**What they deliberately DON'T show**  
- No 3-tier pricing grid above fold.  
- No protocol/layer essay.  
- No paste-and-go text box on homepage.

**3 screenshots worth stealing**  
1. **Stat strip under hero** — 3 numbers, one row, no card chrome.  
2. **Live sample PR link** — "judge output yourself" CTA with external proof.  
3. **CR_* section anchor** — one mega-topic per scroll with **real UI fragment** (not 9 equal cards).

---

### 5. Semgrep Code (semgrep.dev/products/semgrep-code) — enterprise SAST reference

**Above-fold (5 sec layout grid)**  
- Split hero: **left copy** ("Your AI AppSec Engineer") + **right product visual** (scan results UI).  
- Dual CTA: `Book a demo` + `Try for free`.  
- Logo strip immediately below.

**Typography scale**  
- H1: ~40–48px professional sans (not oversized).  
- Body: 16–18px, enterprise tone.  
- Feature H3: 20–24px.

**Color**  
- Background: white/light gray **or** dark mode variant — Semgrep uses **brand green** (#0FCCBB / teal-green) sparingly on CTAs.  
- High **trust/compliance** palette — less neon than Detail.

**Imagery**  
- **Actual product screenshots** of findings + fix snippets.  
- Charts for "3.5x more true positives" — data viz as proof.

**Section count**  
~5 scrolls: Hero → multimodal explainer → 4 benefit blocks → demo form → footer.

**CTA pattern**  
- Enterprise `Book a demo` + PLG `Try for free` — dual funnel.

**What they DON'T show**  
- No fake GitHub check runs.  
- No founder quote hero.  
- No $99 grid.

**3 screenshots worth stealing**  
1. **Finding + fix snippet** side-by-side in product chrome.  
2. **ROI / comparison stat** with sourced claim (3.5x, 19% lower cost).  
3. **Logo strip** directly under hero — instant B2B credibility.

---

## Cross-peer patterns (why Falsify feels like PPT)

| Pattern | Detail / Factory / CodeRabbit | Current Falsify (serve.py) |
|--------|------------------------------|----------------------------|
| Hero visual | Real UI, OSS proof, or ops dashboard | CSS `pipeline-step` wireframe boxes |
| Proof | Live PR link, scan results, KPIs | Fake `gh-check` HTML + inline JSON |
| Section rhythm | 4–6 sections, one thesis each | 12+ sections, equal-weight cards |
| Accent | 8–15% of pixels, CTA + proof only | Green on chips, tags, bars, pills everywhere |
| Typography | 1 display size + mono for labels | Everything same weight; mono overused |
| Pricing | Hidden or /pricing route | 3-column $99 grid on homepage |
| Density | Designed panels OR editorial whitespace | Grid-of-cards template stacking |

**Root cause**: `web/serve.py` is a single `PAGE` string grown by incremental patches — no design tokens file, no component library, no reference layout fidelity. Each "polish pass" adds another `.s.alt` section instead of restructuring information hierarchy.

---

## Part 2 — Rebuild Spec

### Primary reference recommendation: **Detail** (with Factory hero visual language)

**Justification**  
- Falsify's thesis is **adversarial proof**, not factory throughput — Detail's blunt honesty ("your codebase is full of bugs") maps to Falsify's "looks right is not enough."  
- Factory's **stage-gate KPI strip** is the right visual for **Frame → Adversarial → Cutline → BLOCK** — but as **one designed panel**, not CSS boxes.  
- CodeRabbit's stat strip + live sample link informs **evidence row** and **real artifact CTA**.  
- Rig's adversarial tone informs copy presentation, not layout.

**Hybrid**: Detail's editorial structure + Factory's pipeline panel + CodeRabbit's proof link.

---

### Wireframe — max 6 sections

| # | Section | Content (survives from current) | Presentation |
|---|---------|--------------------------------|--------------|
| 1 | **Hero** | H1, quote A one-liner (optional sub), Install CTA + View sample CTA | Left copy / right **real screenshot** of BLOCK report or Factory-style gate panel. Trust strip: GitHub Actions · MIT · BYOK. |
| 2 | **Proof strip** | 3 metrics: `<1 day to first BLOCK` · `3 verdicts only` · `strict debt trigger` | CodeRabbit-style **one row**, no card grid. |
| 3 | **Three layers** | hero_layers copy (框架审计 / 对抗审查 / Cutline) | Detail-style **3 steps** or Factory **stage strip** — not 3 equal cards. |
| 4 | **Sample artifact** | `/examples/` real JSON + link to GitHub Action install | **One** artifact panel (JSON syntax highlighted) — kill dual deliverables + gh-check mock. |
| 5 | **Workbench** | Partial scope disclaimer, Run sample | Keep functional `/review` but **collapse** on homepage — link "Open workbench" vs full section. |
| 6 | **Start + boundary** | 60s install, open-core one-liner (no $99 grid) | Detail-style dual CTA; footer MIT/Team honesty. |

**Moves to `/docs` (off homepage)**  
- Full 3-column pricing → `docs/10-team-delivery-and-business-model.md` + `/pricing` route later.  
- `#licensing` duplicate → footer one-liner only (already post-PR#7).  
- Antipattern 3-card section → fold into hero_layers or docs `05-adversarial-review.md`.  
- Compare / problem sections → cut (redundant with layers).  
- Full GitHub PR mock → replace with link to real Action run or sample JSON.

---

### Implementation approach

**Recommendation: split static assets, thin Python shell**

| Option | Pros | Cons |
|--------|------|------|
| Keep patching `serve.py` | No deploy change | Already failed — PPT accumulation |
| **`web/static/` + template fragments** | Design system in CSS files; HTML partials; `serve.py` only routes | One-time refactor; fits current Caddy/systemd |
| Full static site (Astro/11ty) | Best DX | New build step on VPS |

**Pick**: `web/static/` + Jinja2 or string templates loaded by `serve.py`.  
- `tokens.css` — colors, type scale from Detail teardown.  
- `components/` — hero, proof-strip, layer-steps, artifact, workbench-embed.  
- `serve.py` — load templates, keep `/review` POST logic.  
- **Reason**: VPS already runs `python3 web/serve.py`; no Node build chain on hel1; Chris can iterate CSS in repo without 3000-line string.

---

### Green accent discipline (rebuild rules)

1. Primary CTA fill only.  
2. BLOCK badge + Must Fix severity only for red.  
3. Pipeline **Cutline → BLOCK** step gets green accent — nowhere else in hero.  
4. Kill `.hero-chip` green borders — use neutral pills.

---

### i18n / content constraints

- Keep **quote A** (Chris Shi) — avatar + cite, product voice only; no "Founder" title or fabricated third-party testimonial.  
- Keep **hero_layers** i18n keys — rewrite layout only.  
- Marketing says **框架审计** not Brooks-Lint.  
- Tests: `tests/test_web.py` updated for new section IDs; key copy phrases preserved.

---

## Deferred to next PR (after Chris picks direction)

- [x] Implement `web/static/` split + 6-section layout — see PR (homepage redesign v2)
- [ ] Capture **real** BLOCK screenshot from CLI/Action for hero  
- [ ] VPS deploy of `16fd3a3` (PR #10 revert) — pending SSH access  
- [ ] Optional `/pricing` standalone page  
- [ ] Mobile nav fix  
- [ ] Remove `$99` grid permanently (user preference from subtraction era — confirm in rebuild)

---

## Appendix — Phase 1 status (2026-06-24)

See vault `变更记录/2026-06-24 Falsify 站点可用性与PR9回滚.md`.
