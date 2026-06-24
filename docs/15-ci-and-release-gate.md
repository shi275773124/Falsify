# 15. CI and Release Gate

[Back to README](../README.md)

This repo treats **green tests** as a hard gate for merge and release.

## Required checks (main)

Enable branch protection on `main` and require:

> **Status (2026-06-24):** `main` branch protection is live via GitHub API — merges require green **`falsify / test-suite`**.

| Check name | Workflow | Job |
|---|---|---|
| `falsify / test-suite` | `.github/workflows/falsify.yml` | `test-suite` |
| `release-gate / test-suite` (on tags) | `.github/workflows/release-gate.yml` | `test-suite` |

## Local verification (before push/tag)

```bash
python -m pip install -e '.[dev]'
python -m pytest tests -q
```

Expected: all tests pass (currently 27).

## Release procedure

1. Ensure `main` is green on `falsify / test-suite`
2. Merge all intended changes
3. Create tag only after local + CI tests pass:

```bash
git tag v0.1.1
git push origin v0.1.1
```

4. `release-gate` runs on `v*` tags and must pass
5. Publish GitHub Release notes after tag gate is green

## What failed in v0.1.0 postmortem

- README slogan changed to `Review first. Trust after.`
- `tests/test_falsify_core.py` still asserted `Stop trusting confident AI.`
- Release was published while core tests were red

Fix: commit `2cb484f` aligned test markers with README positioning.

## Upgrade trigger

Any of the following must block release:

- `python -m pytest tests -q` returns non-zero locally
- `falsify / test-suite` fails on `main`
- `release-gate / test-suite` fails on `v*` tag push

## Related

- [Install GitHub Action](./14-github-action-install.md)
- [Open Core boundary](./12-open-core-boundary.md)
