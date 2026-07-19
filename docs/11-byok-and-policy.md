# Use Locally & BYOK

Falsify is a local toolchain. It does not provide a hosted model gateway or hold your provider keys. You choose the provider, credentials, and machine that runs a review.

## What works without a key

These commands make no model call:

```bash
falsify demo
falsify lint report.md
```

Use them to verify installation and local structural checks. The demo is not a substitute for a model review; it proves only that the local check path works.

## What needs your credentials

A live `falsify review` needs one of:

- a provider key you configure for an OpenAI-compatible endpoint; or
- a compatible agent CLI already authenticated on your machine.

DeepSeek example:

```bash
export DEEPSEEK_API_KEY=sk-...
falsify review report.md --provider deepseek --json
```

For GitHub Actions, add these as repository secrets:

- `FALSIFY_API_BASE`
- `FALSIFY_API_KEY`
- `FALSIFY_MODEL`

When `FALSIFY_API_KEY` is absent, the supplied workflow stays in lint-only advisory mode and does not spend model tokens.

## Local configuration and data boundary

Use environment variables or the local template from `falsify init` to avoid repeating configuration. Do not commit configuration files or environment variables that contain secrets.

Falsify does not:

- host your organization, project, or review history;
- share receipts or reports between users;
- automatically connect to or read an authority system you have not explicitly supplied;
- deploy, merge, or perform production actions on your behalf.

If a claim depends on external state, include inspectable output, a link, command result, or a clear verification path in the review input and artifact.

## What the policy file does today

The template supports `.falsify/policy.yml` as a repository-owned description of:

- which paths contain decision artifacts;
- file-count and size limits;
- intended lint, live-review, and artifact behavior.

The current GitHub Action template reads `TARGET_GLOBS` from workflow configuration. Keep it aligned with the policy targets; do not treat the file as an implemented general policy engine.

## Next

- [Getting Started](./00-getting-started.md)
- [GitHub Action template](./14-github-action-install.md)
- [CLI & Artifact Reference](./20-cli-and-artifacts.md)
