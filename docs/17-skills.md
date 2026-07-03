# 17. Falsify Skills (install)

[Back to README](../README.md) · [Getting Started](./00-getting-started.md) · [BYOK + Policy](./11-byok-and-policy.md)

Falsify skills are **repeatable sign-off workflows**, not prompt snippets. Each pack includes an input contract, raw artifact requirements, verdict schema (`falsify.review.v1`), sample BLOCK / PASS_WITH_DEBT outputs, pitfalls, and minimal actions.

Live site: [falsify.zjdeng.xyz](https://falsify.zjdeng.xyz/)

## Five workflow packs (v0)

| Skill | Directory | One-line purpose |
|---|---|---|
| **Deployment Claim Review** | [`skills/falsify-deployment-claim/`](../skills/falsify-deployment-claim/) | Block "logs green" false confidence before production sign-off. |
| **Live Production Gate** | [`skills/falsify-live-production-gate/`](../skills/falsify-live-production-gate/) | Production Falsify for live executors: derived freshness, incident replay fixtures, input provenance manifest. |
| **AI PR Review** | [`skills/falsify-ai-pr-review/`](../skills/falsify-ai-pr-review/) | Review agent-written or human-written PR claims against raw diff, tests, and runtime evidence. |
| **Research Report Audit** | [`skills/falsify-research-report/`](../skills/falsify-research-report/) | Catch stale data, cherry-picking, and conclusion overreach in memos. |
| **Agent Safety Check** | [`skills/falsify-agent-safety-check/`](../skills/falsify-agent-safety-check/) | Verify agent completion claims before trust — raw artifacts and side effects, not summaries. |

Anonymized live incident pattern (derived freshness / stale panel): [`examples/real-cases/02-derived-freshness-stale-panel.md`](../examples/real-cases/02-derived-freshness-stale-panel.md).

Browse all packs on GitHub: [`skills/`](https://github.com/shi275773124/Falsify/tree/main/skills)

## Install in Claude Code

1. Clone or download this repo (or copy one skill folder from GitHub).
2. Copy the skill directory into your workspace or user skills path, for example:
   - **Project scope:** `.claude/skills/falsify-deployment-claim/` (folder must contain `SKILL.md`)
   - **User scope:** `~/.claude/skills/falsify-deployment-claim/`
3. Restart Claude Code or reload skills if your host requires it.
4. Invoke the workflow when a claim needs sign-off — paste the claim and required raw artifacts per `templates/input.md`.

No Falsify API key is required. Live model-backed review uses **your provider key (BYOK)** or a logged-in agent CLI. See [BYOK + Policy](./11-byok-and-policy.md).

## Install in Cursor

1. Copy a skill folder from [`skills/`](https://github.com/shi275773124/Falsify/tree/main/skills) into:
   - **Project scope:** `.cursor/skills/<skill-name>/` (contains `SKILL.md`)
   - **User scope:** `~/.cursor/skills-cursor/<skill-name>/`
2. The agent loads `SKILL.md` when the task matches the workflow (deployment claim, PR review, research audit, agent completion check).
3. Bring your own model keys — Falsify does not require a hosted Falsify API key for local or BYOK use.

## What each pack contains

```text
skills/falsify-<name>/
  SKILL.md              # workflow contract (when to use, evidence gates, verdict rules)
  README.md             # quick start
  templates/input.md    # paste template for claims + artifacts
  templates/verdict.schema.json
  examples/             # sample BLOCK inputs and verdict JSON
```

## CLI and GitHub Action (alternative paths)

Skills are the **editor-first** entry. You can also:

- Run the CLI: `python falsify.py review report.md --provider deepseek` ([Getting Started](./00-getting-started.md))
- Install the PR gate: [GitHub Action (5 min)](./14-github-action-install.md)

## Upgrade path

Starter skills are MIT open core. When one artifact controls money, production, or a customer commitment, consider an **Audit Sprint** or **Design Partner** pilot — see [Team delivery blueprint](./10-team-delivery-and-business-model.md).

See also: [Pro vs OSS — three-layer boundary](./18-pro-vs-oss.md).
