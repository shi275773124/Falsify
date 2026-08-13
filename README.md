# Falsify

English | [中文](README.zh-CN.md)

**Looks green isn't proof.**

Official site: [https://falsify.site/](https://falsify.site/)

Review first. Trust after. Evidence first. Ship after.

Two pains. Three layers.

| Pain | What Falsify does |
|------|-------------------|
| **AI hallucination & false-green** — logs green, another model agrees, still unsafe | **Adversarial review** — red-teams "looks fine" |
| **Long-term rot / over-engineering** — hidden state, brittle rollback, process theater | **Framework review + Cutline** — catch what will rot later; Must Fix / Debt / Delete |

```text
Adversarial  →  red-teams "looks fine"
Framework    →  catches what will rot later
Cutline      →  Must Fix / Known Debt / Delete
Receipt      →  PASS / PASS_WITH_DEBT / BLOCK
```

> Sign-off only. Does not deploy or trade for you.

**Evidence-driven decision gate** — Falsify is a decision gate for high-risk claims: adversarial review + framework + Cutline, then a signed receipt. Not a chatbot second opinion.


[![falsify](https://github.com/shi275773124/Falsify/actions/workflows/falsify.yml/badge.svg)](https://github.com/shi275773124/Falsify/actions/workflows/falsify.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[Live site](https://falsify.site/) · [Getting started](./docs/00-getting-started.md) · [Skills install](./docs/17-skills.md) · [Adversarial Review](./docs/05-adversarial-review.md) · [Cutline / 风险裁刀](./docs/06-risk-scalpel.md)

## Quick start

```bash
git clone https://github.com/shi275773124/Falsify.git
cd Falsify
pip install -e ".[dev]"
python -m falsify demo
```

1. **Install a skill** in [Claude Code or Cursor](./docs/17-skills.md) — copy a folder from [`skills/`](./skills/) (BYOK; no Falsify API key).
2. Install the [GitHub Action](./docs/14-github-action-install.md) — [one-screen share pack](./docs/github-action-share-pack.md) · [false-green share cards](./examples/real-cases/SHARE-CARDS.md).
3. Optionally open the [homepage format demo](https://falsify.site/#try) — receipt **shape only**, not full gate capability.
4. Use Falsify on one high-risk claim before the decision ships.

## Skills (4 workflows)

The v0 skills pack packages evidence discipline into reusable sign-off workflows — not prompts. Each skill includes an input contract, raw artifact requirements, verdict schema, BLOCK sample, PASS_WITH_DEBT sample, pitfalls, and minimal action examples.

Packs define **what to attack**. Enforcement is still the **CLI / CI / Pro gate** ([skills/README.md](./skills/README.md)).

| Workflow | Path | Purpose |
|---|---|---|
| Deployment Claim Review | [`skills/falsify-deployment-claim/`](./skills/falsify-deployment-claim/) | Block "logs green" false confidence. |
| AI PR Review | [`skills/falsify-ai-pr-review/`](./skills/falsify-ai-pr-review/) | Review agent-written or human-written PR claims against raw evidence. |
| Research Report Audit | [`skills/falsify-research-report/`](./skills/falsify-research-report/) | Catch stale data, cherry-picking, and conclusion overreach. |
| Agent Safety Check | [`skills/falsify-agent-safety-check/`](./skills/falsify-agent-safety-check/) | Verify agent completion claims before trust. |

**Install:** [Skills guide (Claude Code / Cursor / BYOK)](./docs/17-skills.md) · [Browse `skills/` on GitHub](https://github.com/shi275773124/Falsify/tree/main/skills)

## Open core & Claiming

| Surface | Repo / path | Open? | Role |
|---------|-------------|-------|------|
| **This repo** | [shi275773124/Falsify](https://github.com/shi275773124/Falsify) | **MIT subset** | Protocol, starter CLI, sign-off packs, docs, site, optional quant extra |
| **Agent skill shell** | [shi275773124/falsify-skill](https://github.com/shi275773124/falsify-skill) | MIT shell | Install entry — **no** Pro production scripts |
| **Pro runtime** | Private (operator skill tree) | **Closed** | Production & quant enforcement gates, fixture antibodies, live wiring |
| **Public version** | `falsify/__init__.py` → `VERSION` | public | OSS product version only — not Pro skill version |

> **Open core (not full open source):** Protocol, starter CLI, templates, and JSON schema are [MIT](./LICENSE). **Production enforcement, live fixture libraries, and private runtime skills stay closed** (Pro). See [Open Core boundary](./docs/12-open-core-boundary.md), [Pro vs OSS](./docs/18-pro-vs-oss.md), [ROOTFIX](./docs/ROOTFIX-architecture.md).

**Claiming Falsify** = running an authority exit and keeping the command + artifact — not only installing a skill. Full live-money discipline lives in **Pro**, not in this MIT tree. See [skills/README.md](./skills/README.md).

## Delivery status (what you can get today)

The LLM attacks the claim and signs a bounded verdict; an **authority adapter** checks physical facts; the **unified kernel** decides what that verdict may authorize. Every offer below states its status — nothing here turns a review into a production or payment gate.

| Offer | Status | What it is |
|---|---|---|
| **Falsify Review** | **AVAILABLE · OSS** | Adversarial LLM review with a bounded epistemic verdict: CLI, local demo, JSON verdict format, GitHub Action template, docs, examples, starter skills. |
| **Falsify Authority Gate** | **ADAPTER REQUIRED** | Runs executable evidence checks against a real authority path; only then can a `PASS` bear action. No public adapter ships today — without one, every verdict stays epistemic. |
| **Audit Sprint** | **AVAILABLE · SERVICE** | Claim manifest, kill-shots, evidence pack, and a signed verdict receipt for one high-risk artifact ([deliverables template](./templates/audit-sprint.md)). |
| **Production / Quant Pro** | **DESIGN PARTNER · PRIVATE** | Integrated per concrete authority path (deploy, data, execution). Scoped pilots, not self-serve. |
| **Team / Enterprise** | **TARGET · NOT SHIPPED** | Dashboard, SSO, RBAC, retention, managed integrations. Roadmap targets — not delivered features. |

License/commercial boundary: this repo contains an MIT `LICENSE`. Commercial workflow packaging, managed integrations, support, private deployment path, and controlled Falsify brand/certification marks remain commercial boundary items.

## What problem it solves

AI made teams faster. It also made false confidence cheaper.

Bad decisions now arrive wrapped in polished summaries, green logs, passing tests that checked the wrong thing, second-model agreement, and confident reports with weak evidence.

Falsify forces the review to bottom out in raw artifacts: code, diffs, command output, source links, parse status, HTTP status, raw verdicts, finish reasons, and usage/token counts when available.

## The framework

```text
Falsify = Adversarial Review + Framework review + Cutline
```

| Layer | Plain language | What it catches | Output |
|---|---|---|---|
| Adversarial Review | red-teams "looks fine" | false truth, false risk, silent failure, stale data, fake acceptance, second-model agreement theater | tagged findings |
| Framework (Brooks-Lint) | catches what will rot later | hidden state, implicit authority, duplicated control paths, brittle rollback, over-engineering | concrete review targets |
| Cutline / 风险裁刀 | Must Fix / Debt / Delete | every risk treated as P0, or real risk deleted as "simplicity" | Must Fix / Known Debt / Delete |

Final decision (every receipt carries `claim_scope` and `authority_ceiling`; OSS receipts are `EPISTEMIC_ONLY` with `capital_authority: NONE`):

- `PASS`: evidence holds and no current blocker remains.
- `PASS_WITH_DEBT`: no current blocker remains, and every Known Debt item has an upgrade trigger.
- `BLOCK`: at least one Must Fix remains, evidence is missing for the current decision, or the audit cannot be parsed.

## Quant Gate — backtest audit

Falsify's quant layer catches what backtests hide: overfitting, lookahead bias, and cost optimism.

```bash
pip install -e ".[quant]"  # from the repo root: numpy, scipy, pandas
python -m falsify.quant_gate --script strategy.py --contract contract.yaml --results-dir results/
```

**Gates 0–5:** contract validation → PIT/survivorship → static code scan (gate4 lookahead) → numeric recompute (PSR/DSR) → robustness (PBO/walk-forward/regime/multi-objective Calmar/per-trade edge-vs-cost) → live reconciliation.

### The PBO=0.99 story

A strategy family showed PBO=0.9991 — "certain overfitting, reject." But 0.9991 is suspiciously high. Investigation found the PBO function subtracted the mean before computing Sharpe, zeroing all Sharpes and making "IS-best" pure noise. PBO was measuring noise mean-reversion, not overfitting. After fixing: **PBO=0.09**. The strategy was actually robust.

**Lesson:** PBO ≈ 1.0 is a red flag for the *implementation*, not just the strategy. Always verify with synthetic data.

### What gate4 catches (lookahead bias)

| Pattern | Severity | Example |
|---|---|---|
| `shift(-N)` | CRITICAL | `df["close"].shift(-5)` — brings future into present |
| `rolling(VAR).std()` without `shift(1)` | WARN | vol includes current bar's return |
| `rolling(20).std()` without `shift(1)` | WARN | same, with literal window |
| Hand-written for-loop with `iloc[i+N]` | WARN | gate4 cannot statically verify — manual review required |

### Credibility assets

- **85 green-light fixtures** — known-answer tests for every statistical function (PBO, DSR, PSR, walk-forward, regime, cost realism, execution realism). Run nightly.
- **6 red-light poisons** — deliberate bugs injected into formulas (PSR kurtosis, PBO rank, DSR formula, gate4 shift/rolling/for-loop). If a poison passes, the check is dead — alert immediately.

```bash
# Run the credibility suite
python -m pytest tests/quant/ -v
```

### Hermes gate6 divergence

The hermes deployment of Falsify runs an additional `gate6_harness_boundary.deployment_parity` gate (research/live contract hash + Jaccard selection similarity + universe/weights/normalization consistency; default `min_selected_jaccard=0.8`). This gate is **not** in the OSS repo: it depends on a live execution context and a production-guard concept that OSS does not ship. OSS users who need research/live parity checking should design a separate OSS-appropriate reproducibility gate rather than port hermes gate6.

## Quick start

```bash
git clone https://github.com/shi275773124/Falsify.git
cd Falsify
python -m pip install -e .[dev]

# For quant backtest auditing (PBO/DSR/gate4):
python -m pip install -e .[quant]  # adds numpy, scipy, pandas

# No API key: deterministic local fixture demo.
python -m falsify demo

# No Falsify API key. Live review uses your provider key (BYOK) or a logged-in agent CLI.

# No API key: local tag/blocker lint.
python -m falsify lint examples/comparison-case-study/05-final-excerpt.md

# Real model-backed review through an OpenAI-compatible provider.
export DEEPSEEK_API_KEY=sk-...
python -m falsify review report.md --provider deepseek

# Full loop: one model drafts, another reviews.
python -m falsify run brief.md --drafter claude --reviewer deepseek
```

You can also route review through a local agent CLI you are already logged into:

```bash
python -m falsify review report.md --provider claude
python -m falsify review report.md --provider codex
FALSIFY_AGENT_CMD="myagent --headless" python -m falsify review report.md -p myagent
```

Start the local product site and paste-and-go reviewer:

```bash
python web/serve.py
# open http://127.0.0.1:8000
```

The homepage demo panel calls the configured backend. It is not a fake live analysis; without a provider key/config it returns a setup error.

## Realistic example

Normal review:

> Deployment succeeded because the logs completed successfully.

Falsify:

```text
[AGENT-B audit] logs are treated as state verification
Failure mode: logs prove something ran; they do not prove the intended system state changed
Cutline: Must Fix
Evidence needed: raw artifact or command output that proves the claim
Minimal action: verify the actual state with a read-after-write check, deployment query, or invariant test
VERDICT: BLOCK
```

Another example:

> A second AI reviewed the prompt-injection risk and found no issue.

Falsify requires the raw output, parse status, HTTP status, `finish_reason`, usage/token counts when available, and known-pattern or reproducer evidence. Agreement alone is not proof.

## Where to use it

- AI-generated pull requests and migration plans
- deployment or incident claims
- research conclusions and market reports
- architecture or vendor-selection decisions
- LLM probes, monitors, and safety checks
- any workflow where a confident summary could hide weak evidence

## What Falsify refuses to accept as evidence

- "The model said it is fine."
- "Another AI reviewed it."
- "The logs look successful."
- "The output is empty, so there is no issue."
- "This is only theoretical."
- "The checklist says to be careful."
- "Known Debt" without an upgrade trigger.
- `PASS` or `PASS_WITH_DEBT` language that bypasses the evidence gate.

## Docs

- [Getting Started](./docs/00-getting-started.md)
- [Skills install (Claude Code / Cursor)](./docs/17-skills.md)
- [ROOTFIX architecture](./docs/ROOTFIX-architecture.md) — structural cure for version / dual-repo / claiming drift
- [Versioning](./docs/VERSIONING.md) — one public product version
- [Verdict vocabulary](./docs/verdict-vocabulary.md) — Core + extensions
- [Brooks-Lint](./docs/09-brooks-lint.md)
- [Adversarial Review](./docs/05-adversarial-review.md)
- [Cutline / 风险裁刀](./docs/06-risk-scalpel.md)
- [Examples](./docs/08-examples.md)
- [Audit-channel risks](./docs/07-audit-channel-risks.md)
- [Team delivery & business model blueprint](./docs/10-team-delivery-and-business-model.md)
- [BYOK + Policy (Team MVP)](./docs/11-byok-and-policy.md)
- [Install GitHub Action (5 min)](./docs/14-github-action-install.md)
- [CI and release gate](./docs/15-ci-and-release-gate.md)
- [Open Core boundary](./docs/12-open-core-boundary.md)
- [Team edition spec (reserved)](./docs/13-team-edition-spec.md)
- [Pro vs OSS](./docs/18-pro-vs-oss.md)

## OSS PR gate (self-hosted)

**Fast path:** [Install GitHub Action in 5 minutes](./docs/14-github-action-install.md)

Self-hosted PR gate — copy the MIT workflow template into your repo:

- Copy `templates/github-action-pr-review-prototype.yml`
- Paste as `.github/workflows/falsify-pr-review.yml` in your target repo
- (Optional) add `.falsify/policy.yml` starting from `templates/falsify-policy.yml`
- Set optional secrets for live model-backed review:
  - `FALSIFY_API_BASE`
  - `FALSIFY_API_KEY`
  - `FALSIFY_MODEL`

Without secrets, lint still runs and comments are posted (advisory mode; live review is explicitly skipped, not faked as PASS_WITH_DEBT).
The workflow defaults to strict debt hygiene in JSON mode:
`FALSIFY_STRICT_KNOWN_DEBT_TRIGGER=1` (Known Debt without trigger becomes BLOCK).

**Boundary:** Hosted Team features (org policy UI, retention store, managed GitHub App) are separate from this OSS template. See [Open Core boundary](./docs/12-open-core-boundary.md).

## Eating our own dog food — `falsify-review.yml`

This repo runs Falsify on itself. Every PR triggers [`.github/workflows/falsify-review.yml`](./.github/workflows/falsify-review.yml), which calls the `falsify gate` subcommand:

```bash
python -m falsify gate \
  --base "origin/${{ github.base_ref }}" \
  --tier "${FALSIFY_TIER:-auto}" \
  --glob 'demo-vault/research/**/*.md' \
  --json falsify-out.json
```

The workflow then posts an idempotent PR comment (`<!-- falsify-pr-review -->` marker — re-pushes update the same comment, no spam) with the verdict, and fails the CI check on `BLOCK` / `KILL`. Output JSON is uploaded as the `falsify-gate-out` artifact for audit.

`falsify gate` is an **honest L2 stub**: it aggregates `falsify lint` over the changed decision-doc files in the PR diff. It never fake-reports `BLOCK` on clean input and never fake-reports `PASS` on dirty input. The stub scope is documented in its JSON output (`schema_version: falsify.gate.v0.1`, `stub: true`). v1.1 will route `--tier quant` through `quant_falsify_gate` (gate0–gate6) per the [risk-contract schema](https://github.com/shi275773124/Falsify/blob/main/docs/06-risk-scalpel.md). For model-backed adversarial review of a single draft, use `falsify review <file> --json`.

To tune the gate for a PR:
- `FALSIFY_TIER` repo variable: `auto` (default) / `normal` / `production` / `quant`
- `FALSIFY_GLOBS` in the workflow `env`: which changed `.md` paths to lint

## Follow the work

Falsify is evolving with real AI-agent, code review, and production-risk workflows. If you are working on similar problems, feel free to follow along or reach out.

- Official site: https://falsify.site/
- GitHub: https://github.com/shi275773124/Falsify
- X / Twitter: https://x.com/aishikejian
- Email: chrisshi168@icloud.com

## License

MIT. See [LICENSE](./LICENSE).
