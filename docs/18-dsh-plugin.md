# 18. Install Falsify DeepSeek plugin (3 steps)

[Back to README](../README.md) · [BYOK + Policy](./11-byok-and-policy.md) · [Skills](./17-skills.md) · [GitHub Action](./14-github-action-install.md)

DeepSeek writes. Falsify asks: **where is the evidence?**

After install, tell the agent “falsify this file” or “gate this PR.”
You get a receipt: `PASS` / `PASS_WITH_DEBT` / `BLOCK`.
Agent “looks fine” is not a receipt. Green lint is not a ship.

This guide installs the [falsify-dsh](https://github.com/shi275773124/falsify-dsh) plugin in **DeepSeek Harness**. It is a parallel local path — not a replacement for the [GitHub Action](./14-github-action-install.md).

## What you get

After install, the agent can call three tools that wrap the public Falsify CLI:

- `falsify_lint` — static check; `L2_CLEAN` / `L2_DIRTY`; not ship authority
- `falsify_review` — review a claim or file; `PASS` / `PASS_WITH_DEBT` / `BLOCK`; BYOK; document-logic only
- `falsify_gate` — gate a PR vs `origin/main`; public CLI; `production` / `quant` fail closed

The plugin does not choose the verdict. It supplies paths, runs `python -m falsify`, and returns the receipt.

The OSS plugin is an **adversarial-review layer**, not production or deployment authority. It cannot grant a claim-bearing production PASS; that requires a separately deployed authority adapter, signer, and sandbox. `claim_bearing` stays false.

## Prerequisites

- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) (developer preview; expect breaking changes)
- Python 3.12+ with the public Falsify CLI
- A DSH profile you can restart (this guide uses `--profile web`)
- (Optional) a provider key for live model-backed review (BYOK)

## Step 1 — Install the public CLI (1 min)

```sh
pip install "falsify @ git+https://github.com/shi275773124/Falsify.git"
python -m falsify --help
```

Set `FALSIFY_PYTHON` if `python` is not the interpreter that has Falsify installed.

## Step 2 — Add the plugin (30 seconds)

```sh
dsh plugin --profile web add "github:shi275773124/falsify-dsh#v0.1.1"
```

Only packages that declare `dsh.bundle.patch` become active profile layers. This package does.

## Step 3 — Restart and ask (30 seconds)

```sh
dsh --profile web
```

Then say one of these to the agent:

| Say this | What should happen |
|---|---|
| `falsify this file` | `falsify_review` on the open file; receipt is `PASS` / `PASS_WITH_DEBT` / `BLOCK` |
| `gate this PR` | `falsify_gate` vs `origin/main`; `production` / `quant` fail closed on the public CLI |
| `lint this file` | `falsify_lint` only; `L2_CLEAN` is not a ship signal |

Without a provider key, live review is unavailable. Missing evidence is `BLOCK` or `CLI_ERROR`, never a silent green.

## Ceiling

| Tool | Allowed meaning | Not allowed |
|---|---|---|
| `falsify_lint` | Static tags + blocker markers. Ceiling = `NONE`. | Treating `L2_CLEAN` as PASS or ship authority |
| `falsify_review` | Epistemic document review. BYOK. `claim_bearing=false`. | Live / production / capital authority |
| `falsify_gate` | Public gate receipt. `production` / `quant` fail closed. | A Pro adapter, HMAC signer, or action-bearing PASS |

Looks green is not proof. A plugin receipt is still OSS review.

## Verification checklist

- [ ] `python -m falsify --help` works in the same interpreter the plugin will spawn
- [ ] After restart, the agent exposes `falsify_lint`, `falsify_review`, and `falsify_gate`
- [ ] “lint this file” returns `L2_CLEAN` or `L2_DIRTY`, never a ship PASS
- [ ] “falsify this file” without a key does not invent `PASS`
- [ ] “gate this PR” on `production` / `quant` fail-closes on the public CLI

## Modes

| Mode | Secrets | Behavior |
|---|---|---|
| Lint only | none | `falsify_lint` runs; not a review receipt |
| Review, no key | none | live review cannot run; no invented PASS |
| Live BYOK | `DEEPSEEK_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | model-backed OSS review; still non-authoritative |
| Public gate | none | `production` / `quant` fail closed without a Pro adapter |

## Troubleshooting

**`verdict=CLI_ERROR`**

- `python -m falsify` is missing or the spawn failed
- Install the public CLI, or set `FALSIFY_PYTHON`

**Plugin listed but tools missing**

- Profile did not load `dsh.bundle.patch`
- Reinstall the plugin and restart the profile

**`L2_CLEAN` looks like a pass**

- It is not. Lint is static only. Do not ship on it.

**`production` / `quant` gate BLOCKs**

- Expected on the public CLI. Pro adapters are closed.

Uninstall:

```sh
dsh plugin --profile web remove falsify-dsh
```

## Next docs

- [BYOK + Policy](./11-byok-and-policy.md)
- [Use Falsify workflow packs](./17-skills.md)
- [Install GitHub Action](./14-github-action-install.md)
- [Open Core boundary](./12-open-core-boundary.md)
