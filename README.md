# Falsify

> **Review first. Trust after.**

> **Open core:** Protocol, CLI, templates, and JSON schema are [MIT](./LICENSE). Team edition covers hosted governance, report retention, and enterprise integrations — not the protocol itself. See [Open Core boundary](./docs/12-open-core-boundary.md) and [Pro vs OSS](./docs/18-pro-vs-oss.md).

Falsify is an **adversarial sign-off layer for high-risk AI work**: PRs, deployments, research reports, agent outputs, and **quant backtests** are reviewed against raw evidence before a team ships the decision.

It is still a decision gate: it turns raw evidence into `PASS`, `PASS_WITH_DEBT`, or `BLOCK` before a high-risk decision ships.

It forces decisions to bottom out in evidence and cuts risk into **Must Fix**, **Known Debt**, or **Delete**.

Falsify is not another model saying "looks good." It is a protocol for separating defensible decisions from confident noise and returning exactly one of `PASS`, `PASS_WITH_DEBT`, or `BLOCK`.

Code review and lint gates catch many issues. They still ask: **"Does the diff look right?"**  
Falsify asks: **"Is this decision defensible?"**

[![falsify](https://github.com/shi275773124/Falsify/actions/workflows/falsify.yml/badge.svg)](https://github.com/shi275773124/Falsify/actions/workflows/falsify.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[Chinese](./README.zh-CN.md) · [Live site](https://falsify.zjdeng.xyz/) · [Getting started](./docs/00-getting-started.md) · [Skills install](./docs/17-skills.md) · [Brooks-Lint](./docs/09-brooks-lint.md) · [Adversarial Review](./docs/05-adversarial-review.md) · [Cutline / 风险裁刀](./docs/06-risk-scalpel.md)

## Table of contents

- [Entry path](#entry-path)
- [Skills (4 workflows)](#skills-4-workflows)
- [Audit Sprint / Design Partner / Team path](#audit-sprint--design-partner--team-path)
- [What problem it solves](#what-problem-it-solves)
- [The framework](#the-framework)
- [Quick start](#quick-start)
- [Docs](#docs)
- [OSS PR gate (self-hosted)](#oss-pr-gate-self-hosted)

## Entry path

1. **Install a skill** in [Claude Code or Cursor](./docs/17-skills.md) — copy a folder from [`skills/`](./skills/) (BYOK; no Falsify API key).
2. Run a sample review with `python falsify.py demo` or the [homepage workbench](https://falsify.zjdeng.xyz/#try).
3. Install the [GitHub Action](./docs/14-github-action-install.md) when PR docs need a gate.
4. Use Falsify on one high-risk artifact before the decision ships.
5. If the workflow repeats or becomes high-stakes, discuss an Audit Sprint or Design Partner pilot.

## Skills (4 workflows)

The v0 skills pack packages evidence discipline into reusable sign-off workflows — not prompts. Each skill includes an input contract, raw artifact requirements, verdict schema, BLOCK sample, PASS_WITH_DEBT sample, pitfalls, and minimal action examples.

| Workflow | Path | Purpose |
|---|---|---|
| Deployment Claim Review | [`skills/falsify-deployment-claim/`](./skills/falsify-deployment-claim/) | Block "logs green" false confidence. |
| AI PR Review | [`skills/falsify-ai-pr-review/`](./skills/falsify-ai-pr-review/) | Review agent-written or human-written PR claims against raw evidence. |
| Research Report Audit | [`skills/falsify-research-report/`](./skills/falsify-research-report/) | Catch stale data, cherry-picking, and conclusion overreach. |
| Agent Safety Check | [`skills/falsify-agent-safety-check/`](./skills/falsify-agent-safety-check/) | Verify agent completion claims before trust. |

**Install:** [Skills guide (Claude Code / Cursor / BYOK)](./docs/17-skills.md) · [Browse `skills/` on GitHub](https://github.com/shi275773124/Falsify/tree/main/skills)

## Audit Sprint / Design Partner / Team path

Open core is the CLI, JSON schema, GitHub Action template, local artifacts, workflow templates, public examples, and downloadable skills. The commercial path is for teams that need an Audit Sprint on one high-risk artifact, a 4-8 week Design Partner pilot, shared policy, review history, report retention, org rollout, managed integrations, or private deployment/support paths. Those team capabilities are described as a path, not claimed as hosted features in this repo.

Implemented today versus path:

- Implemented today: CLI, local demo, JSON verdict format, GitHub Action template, docs, examples, and starter skills.
- Available as service: Audit Sprint review of one high-risk artifact.
- Design Partner path: workflow mapping and pilot integration for one team.
- Team / Enterprise path: shared history, retention, managed integrations, private deployment, RBAC, SSO, audit logs, and SLA only where explicitly supported or contracted.

License/commercial boundary: this repo contains an MIT `LICENSE`. Commercial workflow packaging, managed integrations, support, private deployment path, and controlled Falsify brand/certification marks remain commercial boundary items.

## What problem it solves

AI made teams faster. It also made false confidence cheaper.

Bad decisions now arrive wrapped in polished summaries, green logs, passing tests that checked the wrong thing, second-model agreement, and confident reports with weak evidence.

Falsify forces the review to bottom out in raw artifacts: code, diffs, command output, source links, parse status, HTTP status, raw verdicts, finish reasons, and usage/token counts when available.

## The framework

```text
Falsify = Brooks-Lint + Adversarial Review + Cutline / 风险裁刀
```

| Layer | What it catches | Output |
|---|---|---|
| Brooks-Lint | structural decay: hidden state, implicit authority, duplicated control paths, brittle rollback, unverifiable acceptance, AI summaries replacing raw evidence | concrete review targets |
| Adversarial Review | false truth, false risk, silent failure, stale data, permission drift, fake acceptance evidence, semantic nudges, prompt-only audit theater, monitor failure laundering | tagged findings |
| Cutline / 风险裁刀 | review aftermath failure: every risk becomes urgent, or real risk gets deleted as "simplicity" | Must Fix / Known Debt / Delete |

Final decision:

- `PASS`: evidence holds and no current blocker remains.
- `PASS_WITH_DEBT`: no current blocker remains, and every Known Debt item has an upgrade trigger.
- `BLOCK`: at least one Must Fix remains, evidence is missing for the current decision, or the audit cannot be parsed.

## Quant Gate — backtest audit

Falsify's quant layer catches what backtests hide: overfitting, lookahead bias, and cost optimism.

```bash
pip install falsify[quant]  # numpy, scipy, pandas
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
python falsify.py demo

# No Falsify API key. Live review uses your provider key (BYOK) or a logged-in agent CLI.

# No API key: local tag/blocker lint.
python falsify.py lint examples/comparison-case-study/05-final-excerpt.md

# Real model-backed review through an OpenAI-compatible provider.
export DEEPSEEK_API_KEY=sk-...
python falsify.py review report.md --provider deepseek

# Full loop: one model drafts, another reviews.
python falsify.py run brief.md --drafter claude --reviewer deepseek
```

You can also route review through a local agent CLI you are already logged into:

```bash
python falsify.py review report.md --provider claude
python falsify.py review report.md --provider codex
FALSIFY_AGENT_CMD="myagent --headless" python falsify.py review report.md -p myagent
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
- [Brooks-Lint](./docs/09-brooks-lint.md)
- [Adversarial Review](./docs/05-adversarial-review.md)
- [Cutline / 风险裁刀 / Cutline](./docs/06-risk-scalpel.md)
- [Examples](./docs/08-examples.md)
- [Audit-channel risks](./docs/07-audit-channel-risks.md)
- [Team delivery & business model blueprint](./docs/10-team-delivery-and-business-model.md)
- [BYOK + Policy (Team MVP)](./docs/11-byok-and-policy.md)
- [Install GitHub Action (5 min)](./docs/14-github-action-install.md)
- [CI and release gate](./docs/15-ci-and-release-gate.md)
- [Open Core boundary](./docs/12-open-core-boundary.md)
- [Team edition spec (reserved)](./docs/13-team-edition-spec.md)

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

## Follow the work

Falsify is evolving with real AI-agent, code review, and production-risk workflows. If you are working on similar problems, feel free to follow along or reach out.

- GitHub: https://github.com/shi275773124/Falsify
- X / Twitter: https://x.com/aishikejian
- Email: chrisshi168@icloud.com

## License

MIT. See [LICENSE](./LICENSE).
