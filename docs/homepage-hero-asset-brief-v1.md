# Falsify Homepage — Hero Asset Brief v1

> **Status**: **Approved — Phase A implementation authorized** (Chris 全过, 2026-06-28)  
> **Date**: 2026-06-28  
> **Supersedes for hero visual only**: `docs/homepage-design-brief-v1.md` § Hero visual (GitHub Check + product loop composite) and v1.1/v1.2 `.hero-surface` dashboard-merge direction  
> **Does not change**: 5-screen IA, headline A, copy budget, anti-AI rules, pytest compat strategy  
> **Related**: `docs/homepage-design-brief-v1.md`, `docs/homepage-craft-refinement-v1.md`, `docs/design/design-system.md`, `docs/design/benchmark-notes.md`

---

## Right column pivot (2026-06-28)

Chris feedback on A+B comp: **left column locked and approved**; **right column still wrong** — `hero-block-check.png` (fake GitHub Check UI) reads as PPT / fake dashboard, not beauty / animation / ToC skills feel.

**Screenshot path deprecated for hero.** CSS polish around a PNG cannot fix a focal object that parses as CI chrome. Pick one of:

| Variant | Direction | Comp |
|---------|-----------|------|
| **B — Geometry-only** | Large abstract SVG/CSS composition, warm ink void, subtle drift; BLOCK as typographic accent only — no product UI | [B](http://127.0.0.1:8000/design/hero-v1-variants-bcd.html#b) |
| **C — Pool scene** | Soft gradient scene + single floating **skill install card** (Claude Code) — consumer fintech object, not gate dashboard | [C](http://127.0.0.1:8000/design/hero-v1-variants-bcd.html#c) |
| **D — Real media slot** | Full-bleed animated gradient poster + overlay “Watch it BLOCK”; Chris drops 15s screen recording into `design/hero-demo.mp4` when ready | [D](http://127.0.0.1:8000/design/hero-v1-variants-bcd.html#d) |

**Hub (tab switcher):** `design/hero-v1-variants-bcd.html` → http://127.0.0.1:8000/design/hero-v1-variants-bcd.html

**Diagnosis (1 paragraph):** `design/hero-right-column-diagnosis.md`

**Deprecated:** Variant A / `hero-v1-ab-comp.html` right column (screenshot-in-card) — keep for history only.

---

## A+B approved (2026-06-28)

Chris chose **A+B hero strategy** (same day as Phase A brief approval):

| Layer | Decision |
|-------|----------|
| **A — core** | **Real product media** — GitHub Check screenshot / repo asset (`web/static/img/hero-block-check.png`). **Not** a fake HTML dashboard mock, gate-panel collage, or MUST FIX red widget boxes in the hero visual. |
| **B — shell** | Figma-designed **geometry, whitespace, typography, skill strip** — Pool × Jigsaw × Consensys craft without fake UI chrome. |
| **Headline A (locked)** | EN: *Looks right isn't enough.* · ZH: *看起来对，还不够。* |
| **CTA default** | **Install skill** primary (Claude Code · BYOK); **Run sample** secondary — unless a future brief overrides. |

### Deliverables

| Artifact | Status | URL / path |
|----------|--------|------------|
| **Figma file** | **Partial** — file + tokens + desktop left column built; visual column blocked by MCP rate limit | [Falsify Homepage Hero v1](https://www.figma.com/design/fE7xMbUI7HxPJDjNd6UGEc) |
| **Fallback comp** | **Complete** — static HTML for Chris sign-off | `design/hero-v1-ab-comp.html` |

**Blocker (Figma MCP):** Authenticated account is Figma **Starter / View** seat — MCP tool call limit hit after ~5 calls. Right-column asset placeholder + geometric accents + mobile frame remain in fallback comp until plan upgrade or manual Figma completion.

**Chris review gate:** Open fallback comp locally (or finish Figma file) → approve A+B layout → then authorize `home.html` implementation. **Do not edit production homepage until sign-off.**

---

## Positioning shift

### What we are

Falsify’s homepage is a **ToC skills product** landing page — the same delivery surface as `skills/` in the repo. A person installs a skill into **Claude Code** (or another agent host), brings their own keys (**BYOK**), and gets **adversarial sign-off on their conclusions** before they ship money, memos, or agent actions.

The hero’s job is **desire + clarity in 3 seconds**:

- *What is this?* A skill that attacks your AI conclusions and cuts a verdict.
- *How do I enter?* Install skill → run in your editor → see PASS / debt / BLOCK.
- *Why care?* “Looks right” failed; the attack found what self-review missed.

### What we are not

- An **enterprise compliance dashboard** (gate stages grid, LIVE pills, schema chrome, six-column PASS matrix).
- A **protocol education page** (Frame Audit → Adversarial → Cutline essay above the fold).
- A **Semgrep-style finding snippet** (HTML widgets pretending to be “evidence”).
- A **GitHub Action sales page** as the primary hero story (Action is one install path; skill-in-editor is the ToC front door).

### Hero job vs. rest of page

| Hero (3s) | Screens 2–5 + `/docs` |
|-----------|------------------------|
| One memorable product moment | How the protocol works |
| Install skill / Claude Code / BYOK | GitHub Action install guide |
| Emotional hook: attack → BLOCK | Sharpe case depth, artifact JSON |
| Geometric beauty + motion | Gate stages grid, schema labels, protocol jargon |

---

## Visual direction — Pool × Jigsaw × Consensys (NOT Semgrep)

### North star frame

**One designed scene** — not a collage of HTML dashboard panels. The visitor should remember a **single image in motion**, like Jigsaw’s blue field or Pool Money’s product window over atmospheric depth, not “three divs with borders.”

| Reference | Borrow | Do not borrow |
|-----------|--------|---------------|
| **Pool Money** | Product-as-object; warm paper field; one outer frame; named state (balance, pool name) | Fintech tone, lifestyle photos, 40px radius cosplay |
| **Jigsaw** | Viewport rhythm; generous whitespace inside the frame; one focal composition; editorial restraint | Logo-only hero, Google blue, sticky parallax stack |
| **Consensys** | Bold geometric motifs (arcs, dots, lines); display-weight thesis beside object | Black + neon lime palette, chain imagery, full dark dashboard page |
| **Semgrep** | — | Finding snippet as hero, orange accent, PR-diff positioning |

### Geometric beauty

- **Consensys-style shapes**: 2–4 large, low-opacity geometric accents (arc segment, diagonal line, dot cluster) **outside** the focal scene — parallax at ≤4px on scroll or idle drift, opacity ≤0.12.
- **Jigsaw whitespace**: Hero visual column breathes; focal scene occupies ~55–65% of hero height; no nested bordered boxes inside the scene.
- **Pool product-as-object**: One inspectable **conclusion card** (claim line + verdict + Must Fix) reads as a designed object on warm ink, not a devtools panel.

### Color and motion discipline

- **Warm ink + paper** from `tokens.css` — scene lives on `--ink-950` / `--graphite-900` with paper text.
- **One accent** (muted pass green or warm amber for “attack in progress”) — not neon lime, not Semgrep orange.
- **BLOCK red (`--critical-red`)** appears only at the **verdict landing beat** — never on eyebrows, chips, or decorative badges.
- **Motion**: purposeful, ≤8s loop or scroll-triggered once; full **`prefers-reduced-motion: reduce`** fallback (static final frame: BLOCK landed).

---

## Recommended asset type

### Recommendation: **Designed SVG scene + CSS motion accents** (Phase A)

| Option | Verdict |
|--------|---------|
| **SVG scene + CSS** ✅ | Scalable, lightweight, designer-owned composition; dev animates accents and verdict without video weight; respects reduced motion; matches Consensys geometry + Jigsaw calm; no autoplay policy fights. |
| Short loop video | High craft potential (Jigsaw hero) but heavy assets, encoding variants, autoplay muted loops feel “crypto landing”; harder to i18n swap text inside scene. **Defer to Phase B** only if SVG motion fails screenshot review. |
| Lottie | Good for brand mark loops (Jigsaw footer) but poor fit for **data-bearing** hero (claim text, Must Fix line must stay editable/i18n); designer toolchain + file weight; **not primary**. |

**Rationale**: Falsify’s hero must show **instantiated conclusion text** (Sharpe claim, mechanic flaw) in EN/ZH without re-exporting motion files. A layered SVG (background geometry + conclusion card group) lets copy stay in HTML/DOM or SVG `<text>` with i18n, while CSS/`@keyframes` handles attack pulse and BLOCK stamp. Pool Money’s premium feel comes from **one designed window**, not from more dashboard rows — SVG scene is that window.

---

## Hero composition — single frame (static keyframe)

One **dramatic moment** frozen at loop end (or scroll-reveal climax):

```
[ geometric accents — background, subtle parallax ]

        ┌─────────────────────────────────────┐
        │  SKILL · Claude Code          BYOK   │  ← ToC entry hook (mono strip)
        ├─────────────────────────────────────┤
        │                                     │
        │   "Sharpe 4.06 — strategy looks     │  ← conclusion enters (claim)
        │    ready for shadow live"             │
        │              ↓ attack pulse           │
        │   Must Fix: different rebalance       │  ← attack surfaces flaw
        │   mechanic; SR ≈ 0.77                 │
        │                                     │
        │            BLOCK                      │  ← verdict lands (red, once)
        │                                     │
        │   ● ● ● ○ ○   Submit→…→Verdict      │  ← loop progress (dots, not tabs)
        └─────────────────────────────────────┘
```

### Required in frame

1. **Skills hook** — at least one of: “Install skill”, “Works in Claude Code”, “BYOK / no Falsify key” (visible in hero visual, not only trust chips).
2. **One claim line** — the conclusion under attack (Sharpe-class; no “6/7 PASS — ready for shadow live” as hero headline — that contradiction moves to Proof screen / `/docs`).
3. **Attack → BLOCK** — visitor sees the flaw surface, then BLOCK lands; no simultaneous “mostly PASS” dashboard grid in hero.
4. **Loop progress** — dot rail or thin progress (Submit → Attack → Cutline → Verdict → Artifact); tertiary, not a second dashboard row.

### Explicitly out of hero frame

| Element | Destination |
|---------|-------------|
| 4-column gate-stages grid (`gate-map`, Frame/Adv/Cutline PASS columns) | Hidden compat DOM or Screen 2 How |
| `LIVE EVIDENCE GATE` pill + schema header band | `/docs` protocol pages |
| Bordered “Review output” nested verdict box | Retire — BLOCK is typography, not a widget |
| GitHub Check row as separate top band | Optional tiny mono link “View on GitHub →”; not a second dashboard surface |
| `preview-title` “6/7 gates PASS — ready for shadow live” | **Proof** section H2 territory only |

---

## Motion spec

### What animates

| Layer | Motion | Duration | Reduced motion |
|-------|--------|----------|----------------|
| Background geometry | Slow parallax drift (transform translate) or scroll-linked shift | continuous, ≤4px amplitude | Static positions |
| Conclusion card | Fade + slight rise on enter | 400ms ease-out | Visible immediately |
| Attack pulse | Amber/green edge glow or scan line crossing claim text once | 600ms | Skip — show Must Fix visible |
| Must Fix block | Slide up + opacity after attack pulse | 350ms, 200ms delay | Visible immediately |
| BLOCK verdict | `block-stamp` scale + opacity (existing keyframes) | 450ms, 500ms delay | Static BLOCK, no scale |
| Loop dots | Active dot advances one step per loop cycle | 1200ms per step | All past dots filled to Verdict |
| Skill strip | None or subtle opacity on load | 300ms | Static |

### What does not animate

- Red pulse on load, scrolling BLOCK badges, autoplay sound, scroll-jacking, sticky multi-hero parallax.
- Semgrep-style line-by-line diff highlight.

### Loop vs scroll

- **Default**: ≤8s seamless loop (attack → BLOCK → hold 2s → soft reset to claim enter).
- **Alternative**: Scroll-triggered once on first hero visibility (`IntersectionObserver`); loop disabled after first play.
- Chris approval gate: pick one in implementation; brief allows either.

---

## Animation storyboard (7 beats · ~6.5s loop)

| Beat | Time | Frame description | Implementer notes |
|------|------|-------------------|-------------------|
| **1 — Arrive** | 0.0s | Warm ink field; geometric accents at rest; skill strip readable: “Install skill · Claude Code · BYOK” | SVG background layer + HTML mono strip |
| **2 — Claim enters** | 0.4s | Conclusion card fades in: optimistic claim (“Sharpe 4.06 — looks ready…”) in paper card on ink | EN/ZH strings from `bilingual-copy.md` |
| **3 — Attack pulse** | 1.2s | Single scan line or soft amber pulse crosses claim; no red yet | CSS `::after` or SVG animate |
| **4 — Flaw surfaces** | 1.8s | Must Fix block rises: “Second AI reran different mechanic; SR ≈ 0.77” | `preview-must-fix` content, redesigned layout |
| **5 — BLOCK lands** | 2.6s | Large BLOCK typographic stamp scales in; **first and only red moment** | Reuse `.block-stamp` animation |
| **6 — Loop ticks** | 3.2s | Dot rail advances: Verdict dot active; prior steps filled | CSS class toggle on loop |
| **7 — Hold & reset** | 4.0–6.5s | Hold BLOCK + Must Fix 2s; soft fade claim to beat 2 state OR loop restart | `@media (prefers-reduced-motion: reduce)` skips reset |

---

## What moves to `/docs`

| Homepage burden | Route |
|-----------------|-------|
| Gate stages grid (Frame / Adv / Cutline / Verdict columns) | `/docs/05-adversarial-review.md` |
| `falsify.review.v1` schema education | `/docs` verdict schema |
| LIVE gate / evidence gate protocol chrome | `/docs/07-audit-channel-risks.md` |
| “6/7 gates PASS” full case narrative | Screen 3 Proof + `/docs/08-examples.md` |
| GitHub Action install steps | `/docs/14-github-action-install.md` |
| Skills catalog detail | `skills/` + future `/docs/skills` |

---

## Implementation path

### Phase A — Static designed hero + CSS motion (ship first)

**Phase A implemented** — 2026-06-28. Visible `.hero-scene` ships with SVG geometry, skill strip, claim → attack → Must Fix → BLOCK loop (~6.5s), dot rail; hidden `.hero-compat` preserves pytest anchors. Screenshots: `.verification-shots/*-v15.png`.

1. **Design deliverable**: Layered SVG scene (`web/static/img/hero-scene.svg` or inline SVG) — background geometry + card silhouette; text may be HTML overlay for i18n.
2. **Visible layer**: `.hero-scene` — designed composition; no `.hero-surface` dashboard chrome visible.
3. **CSS**: Accent parallax, attack pulse, BLOCK stamp, dot rail — all in `home.css` with `prefers-reduced-motion` overrides.
4. **Copy column unchanged**: Headline A, sub, dual CTA, trust chips.
5. **Screenshot gate**: Desktop 1440 + mobile 390 — squint test = **one object**, not dashboard.

### Phase B — Optional enhancement (only after Phase A approved)

- Short WebM/MP4 loop for background atmosphere (muted, `playsinline`, poster = static SVG).
- Or Lottie **only** for geometric accents — not for verdict text.
- Do not replace Phase A text layer with baked-in video typography.

### Explicitly forbidden — v15 “merge more divs”

- ❌ Adding another hairline band between GitHub row + loop + cockpit.
- ❌ Hiding dashboard chrome with `display:none` while keeping the same collage structure.
- ❌ More `gate-stage` columns, LIVE pills, or nested bordered verdict boxes.
- ❌ Treating Semgrep-style HTML snippet as the hero asset.
- ❌ Hero primary CTA pivot to “Install GitHub Action” over “Run sample” / skill install without Chris sign-off.

**The hero visual is an asset decision, not a CSS merge pass.**

---

## Test DOM compatibility

Pytest (`tests/test_web.py`) requires these strings/classes in `serve.PAGE` and inside `hero-visual` before `</header>`:

| Requirement | Source test |
|-------------|-------------|
| `gate-panel`, `hero-cockpit` in PAGE and hero_visual | `test_homepage_hero_redesign`, `test_homepage_hero_image_first` |
| `preview-must-fix` in PAGE | `test_homepage_hero_redesign` |
| `gate-map`, `Frame Audit`, `框架审计` | `test_homepage_hero_redesign` |
| `hero-cockpit { display: none` **not** in CSS | `test_homepage_hero_image_first` |
| `hero-check-img` **not** in hero_visual (hidden compat OK) | `test_homepage_hero_image_first` |
| `/static/img/hero-block-check.png` in PAGE | `test_homepage_hero_redesign` |
| `block-stamp` in PAGE + CSS `@keyframes block-stamp` | `test_homepage_block_stamp_animation` |

### Strategy: hidden compat layer vs redesigned visible layer

**Recommended (Phase 1 — no pytest edits):**

```html
<div class="hero-visual">
  <!-- VISIBLE: designed scene -->
  <div class="hero-scene" aria-label="…">
    <!-- SVG + animated conclusion card + skill strip + dot rail -->
    <!-- preview-must-fix content lives HERE visually -->
  </div>

  <!-- HIDDEN COMPAT: pytest anchors, not shown -->
  <div class="hero-compat" hidden aria-hidden="true">
    <div class="gate-panel hero-cockpit">
      <span class="gate-map">Frame Audit</span>
      … gate-stage grid, schema strings …
      <div class="preview-must-fix">…</div>
    </div>
  </div>
</div>
```

- **Visible layer** carries beauty, motion, ToC skills hook.
- **Compat layer** preserves class names and protocol strings for Tier 1 tests.
- CSS: `.hero-compat { display: none !important; }` or `hidden` attribute — **not** `.hero-cockpit { display: none }` globally (test forbids that rule on `hero-cockpit` selector).

**Phase 2 (optional):** Update pytest Tier 2 to assert on `.hero-scene` + skill strip instead of dashboard classes; shrink compat block.

### i18n

- Visible claim, Must Fix, skill strip: `data-i18n` on visible layer.
- Compat block: duplicate strings or `aria-hidden` static EN — `applyLang()` must not break hidden compat assertions for ZH keys already in PAGE.

---

## Chris approval checklist

Approved **2026-06-28** — Chris 全过:

- [x] **Positioning** — Hero sells **ToC skill install** (Claude Code / BYOK), not enterprise gate dashboard.
- [x] **Asset type** — Designed **SVG scene + CSS motion** (Phase A); video/Lottie deferred to Phase B.
- [x] **Single moment** — No “6/7 PASS shadow live” contradiction in hero; BLOCK + Must Fix is the climax.
- [x] **Visual reference** — Pool × Jigsaw × Consensys geometry; explicitly **not** Semgrep snippet / merged CI boxes.
- [x] **Compat plan** — Hidden `.hero-compat` layer OK for pytest; visible `.hero-scene` is what ships.

---

## Document map

| Doc | Role after this brief approved |
|-----|--------------------------------|
| **This file** | Hero asset + motion spec + implementation gate |
| `docs/homepage-design-brief-v1.md` | 5-screen IA + copy; hero visual section superseded by this doc |
| `docs/homepage-craft-refinement-v1.md` | Craft analysis; v1.2 dashboard-collapse notes historical |
| `docs/design/design-system.md` | Tokens, typography, motion tokens |
| `docs/design/bilingual-copy.md` | Hero claim / Must Fix / skill strip strings |

---

## References

- Strategic correction: Chris 2026-06-28 — “动画和美的东西”; ToC skills delivery; stop dashboard collage.
- Product skills: `skills/falsify-*/SKILL.md`
- Whitepaper: `.vault/创作/Falsify 白皮书 v0.1.md` (v0.2) — protocol truth lives in docs, not hero.
- Benchmark shots: `.verification-shots/competitor-study/poolmoney-*.png`, `consensys-*.png`
