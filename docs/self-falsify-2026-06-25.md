# Self-Falsify audit — 2026-06-25

**Scope:** self-Falsify (same agent/repo author; not independent final judgment)  
**Targets:** public marketing site `https://falsify.zjdeng.xyz` + GitHub repo `shi275773124/Falsify` branch `fix/falsify-self-audit-copy` @ `c45d29c` (+ docstring/teardown follow-up in this commit)  
**Method:** Brooks-Lint → Adversarial Review → Cutline; evidence from raw commands, file paths, and quoted copy.

---

## Verification table

| Gate | Command / check | Branch (built `serve.PAGE`) | Live site (pre-merge) |
|---|---|---|---|
| Tests | `py -3.11 -m pytest tests/ -q` | **PASS** (50 passed) | n/a |
| Demo fixture | `py -3.12 falsify.py demo` | **PASS** (exit 1, `VERDICT: BLOCK`) | n/a |
| No 史可鉴 in HTML | `史可鉴 not in serve.PAGE` | **PASS** | **FAIL** (avatar `aria-label` / zh `quote_cite` still 史可鉴 on main@VPS) |
| Quote cite | `Chris Shi` in PAGE, no `avatar-initial` | **PASS** | **PARTIAL** (en cite OK; zh JS still 史可鉴) |
| BYOK chip | `No Falsify key` in PAGE | **PASS** | **FAIL** (`trust_byok: "BYOK"`) |
| Sharpe case labeled | `Illustrative` + `examples/real-cases/…` link | **PASS** | **FAIL** (no Illustrative prefix) |
| Workbench boundary | `not full Falsify` in PAGE | **PASS** | **PASS** |
| Self-review boundary | `Self-review is not independent` | **PASS** | **PASS** |
| HTTPS | `curl -w "%{http_code}" https://falsify.zjdeng.xyz/` | n/a | **PASS** (200) |
| No 20.5k★ / neutral-referee overclaim in repo | `rg '20\.5\|neutral referee' .` | **PASS** (0 marketing hits) | n/a |
| Open-core honesty | `docs/12-open-core-boundary.md` Known Debt | **PASS** | n/a (docs not on homepage) |

---

## Website verdict

### Verdict

**PASS_WITH_DEBT** (branch fixes address Must Fix copy; live remains stale until merge + VPS deploy)

### Brooks-Lint

| Finding | Evidence |
|---|---|
| Deploy authority split | GitHub `main` @ `44c30a4`; VPS `falsify-web` serves same; PR #20 not merged → **live ≠ branch**. Rollback: `git revert` + `systemctl restart falsify-web`. |
| Human-auditability | Cases link to `/examples/sample-block-report.json`, `/examples/real-cases/01-fictional-horizon-quant-audit.md`, `/examples/comparison-case-study/README.md` — **auditable**. Hero image `hero-block-check.png` is **Pillow-rendered mock**, not a real GitHub Checks screenshot (`当前真相/Falsify 当前真相.md`). |
| Workbench scope | `home.html` workbench: *"Verdict format demo — not full Falsify enforcement."* — **labeled partial**. |
| Quote block | Pre-fix: `aria-label="史可鉴 / Chris Shi"` + `avatar-initial` looked like **fake third-party testimonial** on mobile. Branch: product voice, `Chris Shi` only, no initial overlay. |

### Adversarial Review

| Claim attacked | Result |
|---|---|
| "Green logs aren't proof" quote | **Defensible** — founder product voice after fix; not fabricated customer. |
| "Real BLOCK · reports/deploy.md" | **Defensible** — points to `examples/sample-block-report.json` in repo. |
| Sharpe 4.06 case | Pre-fix: read like live production proof. Branch: **"Illustrative · …"** + explicit artifact path. |
| Trust band "BYOK" alone | Pre-fix: implies Falsify-hosted key. Branch: **"No Falsify key · BYOK"**. |
| Hero gate panel (Frame/Evidence/Cutline all PASS → BLOCK) | **Misleading UI** — decorative fallback; hero PNG carries real BLOCK story. Not a fabricated GH check (artifact section says so). |
| Live review button | **Honest** — `/review` calls real backend; returns setup error without key (`web/README.md`). |

### Cutline — Website

**Must Fix** (addressed in PR #20 branch)

- Remove 史可鉴 / fake-testimonial avatar pattern → `web/templates/home.html`, `web/static/js/home.js`
- Soften BYOK chip → `No Falsify key · BYOK` / `无 Falsify key · BYOK`
- Label Sharpe case illustrative + artifact link

**Known Debt**

- Live site stale until merge + `git pull` on VPS + `systemctl restart falsify-web` → upgrade when PR #20 merges.
- Hero PNG mock → replace with real Action/CLI BLOCK screenshot when available.
- Cloudflare CSS cache (~4h) → purge or cache-bust query after deploy.

**Delete**

- `avatar-initial` 史 overlay (removed on branch).
- Implicit 史可鉴 zh cite in `home.js` (removed on branch).

**Final (Website):** Merge PR #20 and deploy before calling live site clean; branch copy passes self-Falsify Must Fix bar.

---

## Repo verdict

### Verdict

**PASS_WITH_DEBT**

### Brooks-Lint

| Finding | Evidence |
|---|---|
| Marketing vs implementation | Full Falsify = Brooks-Lint + Adversarial + Cutline (`README.md`, `home.js` PUBLIC_COPY). **CLI `falsify.py review`** implements adversarial + cutline via LLM; **`lint`/`demo`** are deterministic partial paths. **Web workbench** = verdict-format demo only. |
| Authority paths | `.github/workflows/falsify.yml`, `release-gate.yml`; VPS `falsify-web.service`; docs `14-github-action-install.md`. |
| Rollback documented | `docs/15-ci-and-release-gate.md`, vault `当前真相/Falsify 当前真相.md`. |
| Distribution | OSS = copy MIT workflow template into target repo (`README.md` § OSS PR gate). No false "one-click marketplace" claim in repo. |

### Adversarial Review

| Claim attacked | Result |
|---|---|
| "Code review asks diff; Falsify asks defensible" | **Softened** in PR — *"lint gates catch many issues; they still ask…"* (`README.md`, `docs/12-open-core-boundary.md`). Vault `创作/Falsify 发布物料.md` pillar ③ *审判断不审 diff* is **absolute** — kept out of public repo. |
| "No API key" / zero key | **Partially overclaimed** in `falsify.py` module docstring (`No API key?`). PR README adds BYOK note; follow-up commit softens docstring to *"No Falsify API key… BYOK or agent CLI"*. Live review still needs provider key or logged-in CLI subscription. |
| "Neutral referee" / 消除偏差 | **Not in public repo marketing** (vault-only in `创作/Falsify 发布物料.md`). No 20.5k★ star count in repo. |
| Open-core feasible | **Honest** — Known Debt in `docs/12-open-core-boundary.md`: analogy only; upgrade trigger on first paying customer. |
| CLI edits drafts | `falsify run` drafts then reviews — **not** "CLI无改稿"; repo does not claim CLI is read-only. |
| Sharpe evidence | `examples/real-cases/01-fictional-horizon-quant-audit.md` exists; homepage now links explicitly. |

### Cutline — Repo

**Must Fix** (addressed in PR #20)

- Diff-review absolute contrast → softened (`README.md`, `README.zh-CN.md`, `docs/10`, `docs/12`)
- BYOK / no Falsify key clarity (`docs/11-byok-and-policy.md`, homepage chip, README comment)
- Fake testimonial attribution (史可鉴) → Chris Shi product voice
- Sharpe case without artifact label → Illustrative + path

**Known Debt**

- `falsify.py` agent-CLI path still requires user subscription/login — document in getting-started if marketing expands.
- Team edition / open-core conversion unproven — documented with upgrade trigger.
- Hero redesign teardown doc updated to drop 史可鉴 (`docs/16-homepage-redesign-teardown.md`).

**Delete**

- Vault-only moat copy (20.5k★, absolute "no API key", "neutral referee") — **not shipped** in repo.

**Final (Repo):** PR #20 brings repo marketing/docs to PASS_WITH_DEBT; no BLOCK for merge once tests pass.

---

## Combined verdict

| Target | Verdict | Merge? |
|---|---|---|
| **Repo** (branch) | PASS_WITH_DEBT | **Yes** — Must Fix copy addressed; tests green |
| **Website** (live) | BLOCK → PASS_WITH_DEBT after deploy | **Merge then deploy** — live still FAIL on 史可鉴/BYOK/Illustrative until VPS pull |

**Merge recommendation:** **Merge PR #20** (do not deploy until merged). Post-merge: VPS `git pull --ff-only origin main && sudo systemctl restart falsify-web`, then re-run live curl gates. Do **not** treat live as authoritative until deploy completes.

---

## Raw evidence (commands)

```powershell
# Branch tests
cd /path/to/Falsify
py -3.11 -m pytest tests/ -q
# → 50 passed in 0.96s

# Branch built homepage
py -3.12 -c "from web import serve; p=serve.PAGE; assert '史可鉴' not in p; assert 'No Falsify key' in p; assert 'Illustrative' in p; print('branch homepage OK')"

# CLI demo
py -3.12 falsify.py demo
# → VERDICT: BLOCK (exit 1)

# Live (pre-merge, 2026-06-25)
curl.exe -sS -o NUL -w "%{http_code}" https://falsify.zjdeng.xyz/
# → 200
curl.exe -sS https://falsify.zjdeng.xyz/ | findstr "trust_byok"
# → trust_byok: "BYOK"   (stale; branch has "No Falsify key · BYOK")
```

**Key quotes (branch `web/templates/home.html`):**

```html
<span class="trust-chip trust-item" data-i18n="trust_byok">No Falsify key · BYOK</span>
<cite data-i18n="quote_cite">Chris Shi</cite>
<h3 class="case-title" data-i18n="case2_title">Illustrative · Sharpe 4.06 · 6/7 PASS → BLOCK</h3>
<p class="lead" data-i18n="boundary_p">Self-review is not independent review.</p>
```

> **Note (2026-06-27):** The quoted case title uses current protocol verdict vocabulary (`BLOCK`). Older drafts used legacy `NOT_VIABLE`; this edit syncs the homepage quote only — it does not change the audit verdicts recorded above.

**Vault cross-check (`创作/Falsify 发布物料.md`):** pillars ①零 API key ②中立裁判 ③审判断不审 diff — items ②③ and 20.5k★ are **vault-only**; public repo uses softened README/docs copy. No repo change required for vault draft posts.

---

## PR

https://github.com/shi275773124/Falsify/pull/20
