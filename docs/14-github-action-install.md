# 14. Install Falsify GitHub Action (5 minutes)

[Back to README](../README.md) · [BYOK + Policy](./11-byok-and-policy.md)

This guide installs the PR gate in a **target repo** (the repo you want to protect), not necessarily the Falsify repo itself.

## What you get

After install, every PR that changes decision docs will produce:

- a PR comment with `PASS / PASS_WITH_DEBT / BLOCK`
- `falsify-report.json` (machine-readable)
- `falsify-report.md` (human-readable)
- a failing GitHub Check when verdict is `BLOCK`

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

Without API secrets, live review is skipped and lint still runs (advisory mode).

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

Add team policy contract:

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

After 3–7 days of advisory comments:

1. Repo → **Settings** → **Branches** → branch protection rule
2. Require status check: `falsify-pr-review` (or your workflow job name)
3. Keep advisory mode first if your team is still tuning globs

## Verification checklist

Run these checks on your first PR:

- [ ] Workflow exits green on a clean decision doc
- [ ] PR comment includes verdict + findings grouped by cutline
- [ ] Artifact contains `falsify-report.json` with `schema_version: falsify.report.v0.1`
- [ ] A deliberate weak claim returns `BLOCK` when live review is enabled
- [ ] Known Debt without `upgrade_trigger` returns `BLOCK` when `FALSIFY_STRICT_KNOWN_DEBT_TRIGGER=1`

## Modes

| Mode | Secrets | Behavior |
|---|---|---|
| Advisory | none | lint runs, live review skipped, comment posted |
| Live BYOK | `FALSIFY_*` set | review runs, `BLOCK` can fail check |
| Strict debt | default on | missing Known Debt trigger becomes `BLOCK` |

## Troubleshooting

**No files scanned**

- Your changed files do not match `TARGET_GLOBS`
- Fix globs or move decision docs into covered paths

**Workflow passes but comment says skipped live review**

- Expected without `FALSIFY_API_KEY`
- Add BYOK secrets to enable live review

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
