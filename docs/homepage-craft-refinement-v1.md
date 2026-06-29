# Falsify Homepage — Craft Refinement v1

> **Status**: Analysis only (no `home.html` edits in this pass)  
> **Date**: 2026-06-28  
> **Context**: Chris v12 review — **structure OK, craft NOT OK**. Five-screen IA locked; this doc captures transferable craft patterns from live benchmarks.  
> **Related**: `docs/homepage-design-brief-v1.md` (v1.1 hero-surface spec), `docs/design/benchmark-notes.md`

---

## Chris complaints → craft target

| Complaint | Craft symptom | Target state |
|-----------|---------------|--------------|
| Fragmented hero | GitHub row + loop + gate-panel as three bordered boxes | One fused product surface, internal hairlines only |
| All-text / no premium | Copy column + small UI widgets; no atmospheric anchor | Product chrome carries meaning; copy stays ≤40 words; section feels “designed” not “documented” |
| Lack of premium feel | Nested cards, heavy borders, Inter+serif mismatch, tight padding | Calm viewport rhythm, one shadow, restrained type scale, warm paper/ink planes |

---

## Jigsaw.google — observed patterns

**Source**: [实测] HTML + CSS fetch (`jigsaw.google/`, `app-hocikOih.css`, 2026-06-28). Visual motion/scroll behavior inferred from DOM + Upperquad case study where not directly captured.

### Layout & IA

- **Full-viewport sticky “moments”** — `#hero` and `#logline` are both `hero is-sticky` at `100vh`; logo/wordmark or one-sentence tagline sits centered on a single color field. Content scrolls *over* the hero rather than beside it. [实测]
- **One job per screen** — Homepage is ~4 beats: brand moment → editorial letter (thesis) → logline restatement → work carousel → footer bookend. No stacked pitch sections. [实测]
- **Centered narrow column for prose** — `#letter` uses 6-col grid, offset 3 (half width), `min-height: calc(100vh - header)`, padding `190px 0 260px` desktop. Prose never spans full width. [实测]
- **Work section = horizontal carousel, not grid** — `carousel peek-out` bleeds cards past viewport edge; cards are image-dominant with title + one line + “Read more”. [实测]

### Typography

- **Google Sans** at weight **500** for almost everything — no ultra-bold headline stack. Body/letter at `1.25rem → 1.5rem`, logline at `1.5rem → 2.25rem`, headings `heading-3` at `1.5rem`. [实测]
- **Muted default text** — `#6e6e6e` on `#f2f2ed` paper; high contrast reserved for blue hero/footer fields (`#0084f5` bg, `#f2f2ed` type). [实测]
- **Italic for one coined term** — “structural agency” in `<em>`; editorial voice without extra UI. [实测]

### Color & surfaces

- **Two-plane system** — saturated blue immersive fields (hero, footer) vs warm paper content (`#f2f2ed`). Sharp section transitions, not gradient soup. [实测]
- **Cards have no outer chrome** — `.card` is flex column: media → text → CTA string. No card border, no card shadow. Image carries weight. [实测]
- **Hero foreground blur** — `backdrop-filter: blur(2px)` over full-bleed photo/video; text stays legible without boxing it. [实测]

### Motion & geometric language

- **Background video** on first hero (loop, muted); static image fallback. [实测]
- **Sticky scroll choreography** — multiple `is-sticky` sections create depth as user scrolls. [实测]
- **Footer Lottie** — brand mark animation on same blue field as hero (bookend symmetry). [实测]
- **Upperquad brand themes** — fragmentation, dimension, connection, illumination; custom Jigsaw Sans to *reduce reliance on photography* for sensitive topics. [推断 — Upperquad case study]

### Content density

- Hero: **logo only** (no H1 sentence in first viewport).
- Letter: **3 short paragraphs** + 2 links.
- Logline: **1 sentence**.
- Work: **6 case cards**, each image-first.
- Total homepage copy ≈ **150 words** visible before carousel interaction. [实测]

---

## Consensys `/products` — brief contrast

**Source**: [实测] WebFetch + existing `.verification-shots/competitor-study/consensys-hero.png`.

| Dimension | Consensys | Jigsaw | Falsify implication |
|-----------|-----------|--------|---------------------|
| Hero anchor | Massive display type + lime accent on black | Logo/wordmark on blue field + video | Falsify already aligns with Consensys for **headline weight**; borrow Jigsaw for **surface unity** and **paper sections** |
| Product proof | Metrics (M users, T requests) + product cards | Case images + editorial titles | Falsify Proof screen = one Sharpe case (Consensys depth) inside Jigsaw-style **single card, no nested chrome** |
| Stack story | Explicit platform layers, jump links | None on homepage — work carousel only | Falsify Screen 2 (How) stays Consensys-like **loop → stack**; Jigsaw does not replace IA |
| Palette | Black + neon green | Blue + warm gray paper | Keep Falsify **warm ink + paper** — do not import either palette |
| Premium lever | Type scale + dark void | Viewport rhythm + editorial restraint | **Combine**: Consensys-bold H1 + Jigsaw-calm section padding and unified product frame |

Consensys answers *“what world is this?”* Jigsaw answers *“how does each screen feel designed?”* Falsify needs both.

---

## Pool Money learnings

**Source**: [实测] HTML + CSS fetch (`poolmoney.com/`, `/_astro/main.C_-OZhCg.css`, 2026-06-28); screenshots `.verification-shots/competitor-study/poolmoney-{hero,sections,full,mobile}.png`. Craftwork curated page (`poolmoney-craftwork.png`) is a prior 3D concept — live site is canonical.

### Typography

- **Three-font system** — `Söhne` (UI/body), `Söhne Breit` (wide display, loaded but hero H1 uses standard sans), `Söhne Mono` (CTAs, tabs, metadata). [实测] CSS
- **Display scale** — H1 `text-display-2`: `clamp(44px, 5.5vw, 62px)`; section H2s `text-heading-1`: `clamp(32px, 4.5vw, 44px)`; body `text-body-lg`: `clamp(16px, 1.7vw, 18px)`. Weights 500–600, not ultra-black. [实测] CSS
- **Mono for actions** — Primary CTA + product tabs: `font-mono uppercase text-mono` (12px caps pill — “Create My Pool”, “COLLABORATE”, …). [实测] HTML
- **Falsify adjacency** — Plus Jakarta Sans 800/400–500 (v1.1) is the correct free stand-in; IBM Plex Mono covers action/evidence labels. No new font work.

### Hero

- **Copy-first, product-second stack** — Hero section = H1 + ≤2-line sub + pill CTA; **product demo is the next block**, full-width below copy (not a 50/50 split at xl). H1: “One account isn't enough.” `max-w-3xl`, left-aligned on sand. [实测]
- **Sparse above-fold copy** — ≈35 words before product frame; blunt category claim, not feature list. [实测]
- **CTA as tactile object** — `rounded-full h-12` pill on brand fill `#003439` — chip, not text link. [实测]

### Product objects

- **Auto-advancing demo** — `#product-demo` cycles tabs every 5s: COLLABORATE · COLLECT · SPEND · MANAGE. Each state shows full app chrome — sidebar pools, balance, collaborators (+N), debit card, deposit/send. [实测]
- **Named instances with state** — “44 Mont Apartment”, dollar amounts, role counts (+8) — not abstract icons. [实测]
- **Use-case rail** — Horizontal marquee of 264px `rounded-3xl` cards: lifestyle photo + pool name + balance. Objects carry “world” without paragraphs. [实测]
- **Diagram objects** — Avatar network on dark “Safety first” band; physical debit card render — product metaphors as designed objects. [实测]

### Scene

- **Atmospheric backdrop inside product frame** — Demo in `xl:rounded-4xl` (~40px) container; UI floats over **painterly green/teal texture** (mobile) or white padded frame with texture bleed (desktop). Depth is **inside** the outer frame. [实测] screenshots
- **Two-plane palette** — Sand paper `#f9f6f1` / `#f4eee5`; brand teal `#003439`; ink footer `#001F22`. Sharp sand ↔ dark breaks. [实测] CSS tokens
- **One outer demo frame** — Internal UI uses sidebar + main pane spacing only; mirrors Jigsaw one-frame logic with Pool’s atmospheric fill.

### Whitespace

- **Section rhythm** — `py-20` (80px) default; xl closers `py-[120px]`; footer `xl:pt-[140px]`. [实测]
- **Container** — `max-w-7xl` with xl padding `104px`; demo capped `xl:max-h-[max(420px,calc(100svh-200px))]`. [实测]
- **Dashed hairline dividers** — Repeating 3px sand dashes between major beats — separation without heavy borders. [实测]

### v1.1 already landed vs v1.2 gaps

**v1.1 shipped** (commit `ce39d2b6` — `.hero-surface`, hairline internals, Plus Jakarta in `tokens.css` / `home.css`). Pool Money informs **v1.2 polish only**:

| v1.1 done | v1.2 gap (Pool Money lever) |
|-----------|----------------------------|
| Three boxes → one `.hero-surface` | **Scene depth** inside frame — flat rgba bands still read “mockup”, not “workspace” |
| Plus Jakarta 800/400–500 | **Widen** `.hero-composite` toward ≥50% viewport (Pool demo spans full container; Falsify still `max-width: 480px`) |
| Hairline loop strip | **Active loop beat** highlight (Pool auto-tabs → one step reads “live”) |
| Hero visual padding 48–72px | Section py toward **96–120px** on paper screens (Pool `py-20` → `py-[120px]`) |

---

## What Pool Money fixes for Chris’s complaints

### Fragmented hero

Pool never renders GitHub-row / loop / cockpit as three siblings with gaps. It presents **one outer rounded frame** with a **mode strip** on top and **one continuous product canvas** inside. Internal UI regions (sidebar, balance, card) share the same white surface — separation is spacing and typographic hierarchy, not second borders.

**Transferable rule**: Loop strip maps to Pool’s mode pills — sits **inside** `.hero-surface` top edge, not as a detached chip row between two other boxes.

### All-text / weak product feel

~60% of hero viewport height is **product chrome**; copy is a short left column. Meaning comes from **named objects with state** (pool + balance) before the visitor reads feature prose. Falsify equivalent: **claim title + verdict row + artifact ID** visible in hero frame before subhead finishes.

**Transferable rule**: Every hero zone must show at least one **instantiated** object (real check name, live verdict state, sample claim string) — not labels alone.

### Premium feel

Premium is **cream field + one dark accent + mega whitespace + single focal product window**, not gradient meshes or neon. Pool feels expensive because it **under-fills** the viewport and **over-scales** the product frame.

**Transferable rule**: Increase hero visual min-height and outer padding before adding decoration; one shadow on `.hero-surface` only (aligns with Jigsaw Rule 1).

---

## 8 concrete rules — Pool Money → Falsify

### PM Rule 1 — One product window (Screen 1 hero)

Treat hero visual as **one rounded inspectable window** (~min-height 420px desktop). GitHub band, loop/mode strip, and gate cockpit are **layers inside**, not siblings outside.

**Acceptance**: screenshot crop of visual column — single outer radius visible.

### PM Rule 2 — Mode strip, not chip boxes (Screen 1)

Product loop renders as **horizontal text tabs** with hairline separators (Pool: COLLABORATE…; Falsify: Submit → Attack → Cutline → Verdict → Artifact). Active step gets underline or weight shift — not five bordered pills.

### PM Rule 3 — Instantiated objects with state (Screens 1, 3, 4)

Show **named instances**: `Sharpe 4.06 / mechanic flaw` + `BLOCK` + artifact path — analogous to `Mrs. K's Class $1,210`. Numbers and verdicts are data, not adjectives.

### PM Rule 4 — Atmospheric depth behind chrome (Screen 1)

Optional **low-contrast warm gradient or paper texture** behind `.hero-surface` (Pool’s blurred foliage; Falsify: subtle ink-to-paper radial at ≤8% opacity). UI stays flat and legible; scene never competes with cockpit.

### PM Rule 5 — Headline island sections (Screens 2–3)

Each paper section: **H2 left (≤8 words) + ≤2 sentence explainer right** with ≥40% row empty. No centered manifesto blocks.

### PM Rule 6 — One contrast band (Screen 3 or footer)

Pool uses dark green “Safety first” to break rhythm. Falsify: one **ink-dense band** (Proof BLOCK case or footer CTA) per scroll — not red wallpaper on every section.

### PM Rule 7 — Warm paper field default (Screens 2–3)

Page background stays cream/paper (`--paper-50`); product objects sit on white inner cards. Matches Pool’s cream + white UI pairing — already in Falsify tokens; enforce vs. full-bleed dark How/Proof.

### PM Rule 8 — Defer prose to docs / FAQ pattern (Screen 5)

Footer + FAQ energy: one closing thesis line, links, single open-core honesty line. Long policy and protocol vocabulary → `/docs`, not homepage sections.

---

## Apply / don’t apply — Pool Money

| ✅ Apply to Falsify (evidence gate) | ❌ Don’t apply (consumer fintech) |
|-----------------------------------|----------------------------------|
| Single mega-frame hero product window | “Bank alone, Pool together” casual voice |
| Mode/loop strip integrated in frame top | Emoji use-case titles (⚽️ 🌟 🏔️) |
| Named objects + state (claim, verdict, severity) | Lifestyle photography in product sections |
| Warm cream/paper page + white inner UI | Forest green `#003439` / ink `#001F22` palette |
| Extreme section whitespace; H2 + 2-line explainer | `rounded-4xl` (40px) radius cosplay — brief caps **≤8px** |
| One dark structural accent band per page | Physical debit card mock |
| Atmospheric depth **inside** `.hero-surface` | Horizontal use-case carousel as Screen 2 IA |
| Mono-caps pills for CTAs / active loop beat | “CREATE MY POOL” consumer CTA tone |
| FAQ/defer pattern for long copy | Shared-money / roommate positioning |
| Auto-highlight one loop beat (motion restraint) | Craftwork 3D stack hero asset |

---

## What Jigsaw fixes for Chris’s complaints

### Fragmented hero

Jigsaw never places three competing bordered widgets in one viewport. It uses **one frame** (full bleed OR single centered block). The v1.1 `.hero-surface` direction matches this: GitHub band + loop + cockpit share **one outer border and one shadow**; separation is `border-top` hairlines only (`docs/homepage-design-brief-v1.md` v1.1).

**Transferable rule**: If a child element has its own outer border + shadow, merge or demote to hairline.

### All-text / weak product feel

Jigsaw’s first viewport is **almost non-verbal** (logo on atmospheric field). Falsify cannot copy that literally — brief requires GitHub Check + product loop + verdict cockpit. Jigsaw’s transferable lesson: **make the visual column ≥50% width and let product objects dominate scan path**; copy stays left and short.

The product surface should read like **one inspectable artifact**, not three pasted components.

### Premium feel

Comes from:

1. **Viewport-height sections** with generous vertical padding (Jigsaw letter: 190–260px desktop).
2. **Restrained type** — medium weights, large sizes, few styles.
3. **Limited chrome** — one shadow, no nested cards.
4. **Color plane shifts** — immersive field → calm paper → immersive footer.

Falsify’s warm paper `#f4f1ea` maps to Jigsaw `#f2f2ed`; `--text-muted-paper: #6e665b` maps to Jigsaw `#6e6e6e`.

---

## What NOT to copy

| Jigsaw pattern | Why skip for Falsify |
|----------------|----------------------|
| Logo-only first viewport | Must show adversarial sign-off product moment in hero |
| Google Sans / Jigsaw Sans | Use Plus Jakarta Sans (already v1.1) — no custom font budget |
| Full-viewport background video | Heavy asset + motion cost; static product chrome is on-brand |
| Google blue `#0084f5` hero field | Wrong brand; keep warm ink hero + paper How/Proof |
| Sticky parallax stack (multiple `is-sticky` heroes) | High engineering cost; static hierarchy first per brief |
| Upperquad illustration / 3D art system | Budget + maintenance; use inline SVG accents + real product UI |
| 2-link minimal nav | Falsify needs How · Proof · Try · Docs · GitHub · 中文 |
| Image-only case cards without product UI | Falsify proof must link to real artifact JSON, not stock photography |
| Carousel as Screen 2 | Five-screen IA uses fixed How strip, not horizontal case carousel |

---

## 8 concrete rules — hero + 5-screen structure

### Rule 1 — One surface, hairline internals (Screen 1 hero)

Wrap GitHub check + product loop + gate cockpit in **one** `.hero-surface`. Only this element gets `box-shadow: var(--shadow-lg)`. Internal zones use `border-top: 1px solid var(--border-subtle)` — never second outer frames.

**Acceptance**: squint test — hero visual reads as one card, not three.

### Rule 2 — Copy/visual weight split (Screen 1)

Desktop: copy column `max-width: 620px`; visual column ≥50% of `hero-inner`. Hero visible copy ≤40 words. Product loop is **horizontal strip with dividers**, not five boxed chips.

**Acceptance**: screenshot at 1440px — eye hits BLOCK/verdict row before reading subhead.

### Rule 3 — Viewport rhythm per screen (Screens 1–5)

Each screen `min-height: min(85vh, …)` with vertical breathing room matching Jigsaw letter padding scaled to Falsify tokens: desktop section padding **92–150px** (`design-system.md`), hero visual padding **48–72px**.

**Acceptance**: each nav anchor lands with one thesis visible without mid-section cut-off.

### Rule 4 — Two-plane color story (Screens 1–5)

- **Screens 1, 4, 5**: warm ink (`--ink-950` / `--graphite-950`) — product chrome lives here.
- **Screens 2–3**: paper surface (`.section-flow`, `--paper-50`) — How + Proof read as “report room”, not another dark dashboard.

Mirrors Jigsaw blue ↔ paper alternation without copying blue.

### Rule 5 — Typography discipline (all screens)

One sans family for H1 + body (Plus Jakarta 800 / 400–500). Mono only for evidence labels. No serif in hero after v1.1. Scale steps: H1 clamp ~2.5–3.5rem, section titles ~1.25–1.5rem, body 1rem, metadata mono 10–12px.

**Acceptance**: no third display family on homepage.

### Rule 6 — Object carries meaning; text confirms (Screens 2–4)

Screen 2: three step labels ≤8 words each + verdict row — **no manifesto**.  
Screen 3: one case card — finding ≤25 words + artifact link.  
Screen 4: workbench panels + terminal — interactive objects, not feature bullets.

Jigsaw card pattern: image/object first, one title, one subline.

### Rule 7 — Geometric accent budget (Screen 1 visual column)

Max **3** low-opacity SVG accents (arc, line, dot) in `.hero-visual` background — Jigsaw/Consensys geometric motif without illustration budget. Accents must not compete with cockpit legibility (opacity ≤0.14).

### Rule 8 — Motion restraint (all screens)

No stagger on every loop chip. Optional: single `hero-rise` on copy column; status pulse only on BLOCK stamp. Avoid sticky parallax until craft baseline passes screenshot review.

---

## Screen-by-screen checklist (Jigsaw × Pool Money × Consensys × Falsify brief)

| Screen | Jigsaw | Pool Money | Consensys | Do not |
|--------|--------|------------|-----------|--------|
| **1 Hero** | Unified surface, hairline zones | One product window + mode strip; scene depth | Bold H1 thesis, dual CTA | Three boxed widgets; PNG-only hero |
| **2 How** | Paper plane, calm layout | H2 island + 2-line explainer | Loop vocabulary, stack as layers | 3 equal manifesto cards |
| **3 Proof** | Single card, no nested chrome | Named instance + state number | One undeniable BLOCK case | 6-card bento; emoji tiles |
| **4 Try** | Object-first workbench | White UI on paper field | Conversion focus | Separate skills/catches grids |
| **5 Footer CTA** | One closing line + links | Dark contrast band bookend | Commercial honesty one-liner | Duplicate CTA blocks |

---

## Apply / don’t apply (quick reference)

| Apply to Falsify | Don’t apply |
|------------------|-------------|
| One outer frame + internal hairlines in hero (Jigsaw) | Logo-only hero |
| One product window + integrated loop/mode strip (Pool Money) | Three detached hero boxes |
| Named objects with verdict/state, not feature bullets (Pool Money) | Emoji use-case carousel |
| Visual column ≥50%; hero ≤40 words (Jigsaw + Pool Money) | Lifestyle photo scenes |
| 100vh-ish section rhythm / large vertical padding (Jigsaw + Pool Money) | Multi-layer sticky parallax |
| Warm cream paper + white inner product UI (Pool Money → Falsify tokens) | Forest green / Google blue palettes |
| Paper sections for How/Proof; ink for Hero/Try (Jigsaw two-plane) | Full-bleed dark dashboard entire page |
| Bold H1 + geometric sans (Consensys + Pool Money) | Consensys neon lime accent |
| Single dark contrast band (Pool Money Safety / Falsify Proof) | Red BLOCK wallpaper |
| ≤3 low-opacity SVG accents (Jigsaw + Consensys) | 3D craftwork stack / Upperquad illustration |
| Defer long copy to docs/FAQ (Pool Money) | Consumer “Pool together” tone |

---

## Evidence log

| Claim | Tier |
|-------|------|
| Jigsaw colors `#f2f2ed`, `#6e6e6e`, `#0084f5` | [实测] CSS fetch |
| Jigsaw grid, letter padding, sticky hero heights | [实测] CSS fetch |
| Jigsaw homepage section order & copy volume | [实测] HTML fetch |
| Jigsaw Sans / reduced imagery rationale | [推断] Upperquad case study |
| Consensys hero type + dark/lime plane | [实测] prior screenshot + WebFetch |
| Falsify v1.1 `.hero-surface` spec | [实测] `docs/homepage-design-brief-v1.md`, `home.css` |
| Pool Money Söhne scale + sand `#f9f6f1` / brand `#003439` | [实测] CSS fetch 2026-06-28 |
| Pool Money hero copy <35 words; 7 sections | [实测] HTML fetch |
| Pool Money product-demo auto-advance 5s | [实测] HTML fetch |
| Pool Money craftwork 3D concept | [推断] craftwork curated page only — not live site |
| Falsify v1.1 `.hero-surface` + Plus Jakarta | [实测] `home.css`, `tokens.css` (ce39d2b6) |

---

## Synthesis — Falsify hero v1.2 target feel

**Jigsaw + Pool Money + Consensys**: Hero v1.2 should read as a **Consensys-weight thesis** (“Looks right isn’t enough.” in Plus Jakarta 800) beside a **Pool Money product window** — one warm-ink `.hero-surface` (v1.1 merge done) with Submit→Artifact loop on its top edge and **instantiated evidence inside** (GitHub check band, BLOCK verdict row, artifact path), backed by **Pool-caliber scene depth** (subtle ink-to-paper wash inside the frame — not video, not lifestyle photos). How and Proof breathe on **Pool Money cream paper** with Jigsaw hairline discipline; Try and footer return to ink density like Consensys product chrome. Premium comes from **under-filling and over-scaling the product object** — widen the composite, highlight one loop beat, bump section py to 96–120px — not from more copy, nested borders, or neon accents. An evidence gate that feels as calm as Pool Money, as authoritative as Consensys, with Jigsaw’s single-frame restraint holding it together.

---

## Next implementation gate (not in this pass)

1. Screenshot desktop 1440 + mobile 390 after v1.1 CSS lands — compare to Jigsaw section rhythm and Pool Money hero frame ratio (product window ≥60% hero height).
2. Squint test: hero visual = one object (Jigsaw + Pool Money).
3. Verify paper plane on `#how` / `#proof` against ink hero — two-plane story visible in one scroll.
4. v1.2 candidates only: widen `.hero-composite`, scene wash inside `.hero-surface`, active loop beat, section py 96–120px (Pool Money scale).

---

## v1.2 hero focal scene (2026-06-28)

**Chris feedback on v13 (zh UI)**: hero right side still **很割裂** — one `.hero-surface` border did not unify the read.

**Root cause [推断]**: Too many competing UI layers (GitHub row + 5 tab boxes + gate header + Review output box + 4-column PASS grid + Must Fix) = dashboard collage, not one product moment.

**Shipped in v1.2**:

| Removed / collapsed | Why less 割裂 |
|---------------------|---------------|
| 5 equal SUBMIT/ATTACK tab strip → dot progress rail inside cockpit | Loop is tertiary metadata, not a second dashboard row |
| Gate header (schema + LIVE pill) hidden in hero viewport | One less chrome band; schema still in DOM |
| Bordered “Review output” verdict box | BLOCK is the focal type — no nested red frame |
| 4-column gate-stages grid hidden in `.hero-visual` | Stages stay in DOM for tests; detail lives in How/Proof |
| Empty `gate-body` shell | Must Fix moved into unified `.hero-focal` scene |
| 3 floating SVG accents | Replaced by single `.hero-surface-scene` wash inside frame |

**Read hierarchy**: (1) GitHub Check BLOCK row → (2) large BLOCK + claim line + Must Fix → (3) dot rail.

**Preserved**: `gate-panel`, `hero-cockpit`, `preview-must-fix`, `block-stamp`, `gate-map`, compat strings, 5-screen IA, headline A, Plus Jakarta.
