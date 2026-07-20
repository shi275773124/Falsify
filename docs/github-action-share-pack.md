# Falsify GitHub Action — share pack (one screen)

> Forward this page. Full guide: [14-github-action-install.md](./14-github-action-install.md)

## What it is

A **PR claim gate**, not another code-review bot.

When a PR changes decision docs, Falsify posts a **PASS / PASS_WITH_DEBT / BLOCK** receipt.  
**Looks green isn't proof** — a completion message is a claim until an authority path is checked.

OSS Action = adversarial review layer. It does **not** grant production or live trading authority.

## 5 minutes

### 1. Workflow file

In the **target** repo (the one you protect):

```text
.github/workflows/falsify-pr-review.yml
```

Copy from:

https://github.com/shi275773124/Falsify/blob/main/templates/github-action-pr-review-prototype.yml

### 2. Narrow globs (required)

```yaml
env:
  TARGET_GLOBS: "reports/**/*.md research/**/*.md"
```

Do **not** scan the whole repo.

### 3. Test PR

Change one file under those globs (example `reports/deployment-claim.md`), open a PR.

Expect:

- workflow `falsify-pr-review` runs
- PR comment `<!-- falsify-pr-summary -->`
- artifacts `falsify-report.json` / `.md`
- without API secrets → fail-closed **BLOCK** (not fake PASS)

### 4. Optional BYOK

Secrets: `FALSIFY_API_BASE`, `FALSIFY_API_KEY`, `FALSIFY_MODEL`  
Then re-run for model-backed `falsify review --json`.

## One sentence to paste

> We gate AI/agent “done” claims on decision docs: Falsify returns a reproducible PASS / PASS_WITH_DEBT / BLOCK receipt. Install: 5-minute GitHub Action — https://falsify.site/docs/14-github-action-install.html

## Three false-green cases (why this exists)

| Case | Shape | Link |
|------|--------|------|
| 01 | Fresh signal, stale inputs | https://falsify.site/examples/real-cases/02-derived-freshness-stale-panel |
| 02 | Statistical PASS, hidden missing-data policy | https://falsify.site/examples/real-cases/04-round3b-evidence-integrity-reversal |
| 03 | Mirror fixed, runtime not | https://falsify.site/examples/real-cases/05-second-runtime-v068-sync-false-green |

Card index: [examples/real-cases/SHARE-CARDS.md](../examples/real-cases/SHARE-CARDS.md)

## Not this product

| Not | Instead |
|-----|---------|
| Bug scanner on a diff | Bounded **claim** vs authority |
| Eval / second AI opinion | Inspectable **receipt** |
| Live order authorization | Risk classification only |
