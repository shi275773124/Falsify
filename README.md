# Falsify

> **Review first. Trust after.**

> **Open core:** Protocol, CLI, templates, and JSON schema are [MIT](./LICENSE). Team edition covers hosted governance, report retention, and enterprise integrations — not the protocol itself. See [Open Core boundary](./docs/12-open-core-boundary.md).

Falsify is the **decision gate for AI-era work**: adversarial review for code, research, and production decisions.

It forces decisions to bottom out in evidence and cuts risk into **Must Fix**, **Known Debt**, or **Delete**.

Falsify is not another model saying "looks good." It is a protocol for separating defensible decisions from confident noise.

Code review asks: **"Does the diff look right?"**  
Falsify asks: **"Is this decision defensible?"**

[![falsify](https://github.com/shi275773124/Falsify/actions/workflows/falsify.yml/badge.svg)](https://github.com/shi275773124/Falsify/actions/workflows/falsify.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[Chinese](./README.zh-CN.md) · [Getting started](./docs/00-getting-started.md) · [Brooks-Lint](./docs/09-brooks-lint.md) · [Adversarial Review](./docs/05-adversarial-review.md) · [Cutline / 风险裁刀](./docs/06-risk-scalpel.md)

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

## Quick start

```bash
git clone https://github.com/shi275773124/Falsify.git
cd Falsify
python -m pip install -e .[dev]

# No API key: deterministic local fixture demo.
python falsify.py demo

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
