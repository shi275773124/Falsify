# 11. BYOK + Policy (Team MVP)

[Back to README](../README.md)

This doc explains how to deploy Falsify as a PR gate without the vendor paying model tokens.

## BYOK (Bring Your Own Key)

Falsify is designed to run in two modes:

- **Advisory mode (default)**: no model call. Lint runs, sample/demo runs, PR comment still posts.
- **Live review mode (BYOK)**: the PR gate calls an OpenAI-compatible endpoint using your secret.

In GitHub:

1. Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
2. Add:
   - `FALSIFY_API_BASE` (example: `https://api.deepseek.com/v1`)
   - `FALSIFY_API_KEY`
   - `FALSIFY_MODEL` (example: `deepseek-chat`)

If `FALSIFY_API_KEY` is missing, the workflow must **skip** live review and never burn tokens.

## Policy file

Put a policy file in the target repo:

```text
.falsify/policy.yml
```

Start from:

```text
templates/falsify-policy.yml
```

### What policy controls

- **targets.globs**: what files are considered “decision artifacts”
- **limits**: caps to prevent token blowups (bytes per file, number of files)
- **gates.lint**: always-on tag / ship-blocker conventions
- **gates.live_review**: whether the BYOK review is enforced when a key exists
- **output**: whether to upload JSON/Markdown artifacts and comment on PR

## What “sellable” means in Team MVP

The sellable unit is not the website. It’s the workflow output:

- a PR comment that surfaces the verdict
- machine-readable JSON artifact for downstream integrations
- a consistent policy file that an org can standardize
- a report that is auditable (who/when/what changed/what evidence is missing)

## Recommended rollout path

1. Advisory mode for 1 week (comment only)
2. Tighten `targets.globs` (only real decision docs)
3. Turn on required check in branch protection
4. Expand to more repos / add integrations

