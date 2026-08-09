# 14. Install Falsify GitHub Action (5 minutes)

[Back to README](../README.md) · [BYOK + Policy](./11-byok-and-policy.md) · **[Share pack (one screen)](./github-action-share-pack.md)** · [False-green cards](../examples/real-cases/SHARE-CARDS.md)

This guide installs the PR gate in a **target repo** (the repo you want to protect), not necessarily the Falsify repo itself.

## What you get

After install, every PR that changes decision docs will produce:

- a PR comment with `PASS / PASS_WITH_DEBT / BLOCK`
- `falsify-report.json` (machine-readable)
- `falsify-report.md` (human-readable)
- a failing GitHub Check when verdict is `BLOCK`

The OSS template is an **adversarial-review layer**, not production or deployment authority. It cannot grant a claim-bearing production PASS; that requires a separately deployed authority adapter, signer, and sandbox.

## Prerequisites

- GitHub repo with Actions enabled
- Decision docs live in markdown (for example `reports/`, `research/`, migration plans)
- (Optional) OpenAI-compatible API key for live model-backed review (BYOK)

## Step 1 — Add the workflow (2 min)

1. In your target repo, create:

```text
.github/workflows/falsify-pr-review.yml
```

2. Copy contents from:

```text
https://github.com/shi275773124/Falsify/blob/main/templates/github-action-pr-review-prototype.yml
```

3. Edit `TARGET_GLOBS` near the top of the job `env` block:

```yaml
env:
  TARGET_GLOBS: "reports/**/*.md research/**/*.md"
```

Keep this tight. Do not scan your whole repo.

4. Commit and push to `main`.

## Step 2 — Open a test PR (1 min)

Change one markdown file under your target globs, for example:

```text
reports/deployment-claim.md
```

Open a PR. You should see:

- workflow `falsify-pr-review` runs
- PR comment `<!-- falsify-pr-summary -->` appears or updates
- artifacts `falsify-report` uploaded

Without API secrets, live review is unavailable. The template records `BLOCK` rather than laundering lint-only output into `PASS`; add BYOK credentials to run the model-backed review.

## Step 3 — (Optional) Enable BYOK live review (1 min)

Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add:

| Secret | Example |
|---|---|
| `FALSIFY_API_BASE` | `https://api.deepseek.com/v1` |
| `FALSIFY_API_KEY` | `sk-...` |
| `FALSIFY_MODEL` | `deepseek-chat` |

Re-run the PR workflow. Live `falsify review --json` will run when the key exists.

## Step 4 — (Optional) Add policy file (1 min)

Add repo policy file (OSS):

```text
.falsify/policy.yml
```

Start from:

```text
templates/falsify-policy.yml
```

Policy documents globs, limits, and enforcement intent for your team.

Note: the current workflow prototype reads `TARGET_GLOBS` from workflow `env`. Keep `TARGET_GLOBS` aligned with `.falsify/policy.yml` `targets.globs` until native policy loading ships.

## Step 5 — Turn on required check (when ready)

After observing the reports on non-consequential documents:

1. Repo → **Settings** → **Branches** → branch protection rule
2. Require status check: `falsify-pr-review` (or your workflow job name)
3. Do not make this OSS template a production/deployment authorization check. It is a review signal; use a separately implemented authority gate for claim-bearing PASS.

## Verification checklist

Run these checks on your first PR:

- [ ] Missing `FALSIFY_API_KEY` yields `BLOCK`, never a lint-only `PASS`
- [ ] PR comment includes verdict + findings grouped by cutline
- [ ] Artifact contains `falsify-report.json` with `schema_version: falsify.report.v0.1`
- [ ] A deliberate weak claim returns `BLOCK` when live review is enabled
- [ ] Known Debt without `upgrade_trigger` returns `BLOCK` when `FALSIFY_STRICT_KNOWN_DEBT_TRIGGER=1`

## Modes

| Mode | Secrets | Behavior |
|---|---|---|
| No evidence | none | lint runs, live review is skipped, verdict is `BLOCK` |
| Live BYOK | `FALSIFY_*` set | model-backed review runs; this remains non-authoritative OSS review |
| Strict debt | default on | missing Known Debt trigger becomes `BLOCK` |

## Troubleshooting

**No files scanned**

- Your changed files do not match `TARGET_GLOBS`
- Fix globs or move decision docs into covered paths

**Workflow BLOCKs because live review was skipped**

- Expected without `FALSIFY_API_KEY`: no evidence, no PASS
- Add BYOK secrets to enable the model-backed OSS review

**Check fails with BLOCK unexpectedly**

- Open `falsify-report.md` artifact
- Fix `Must Fix` items or add missing `upgrade_trigger` for Known Debt

**Token cost too high**

- Tighten `TARGET_GLOBS`
- Reduce changed file size
- Use advisory mode on low-risk repos

## Next docs

- [BYOK + Policy](./11-byok-and-policy.md)
- [Team delivery blueprint](./10-team-delivery-and-business-model.md)
- [Open Core boundary](./12-open-core-boundary.md)
