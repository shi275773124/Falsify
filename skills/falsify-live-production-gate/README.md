# falsify-live-production-gate

Production Falsify workflow for live executors and post-incident restore.

## Quick start

1. Copy this folder to `.cursor/skills/falsify-live-production-gate/` or `~/.cursor/skills-cursor/falsify-live-production-gate/`.
2. Paste claim + artifacts using `templates/input.md`.
3. Agent returns `falsify.review.v1` JSON per `templates/verdict.schema.json`.

## What this adds beyond deployment-claim

- **Derived freshness false-green** gate
- **FALSIFY_INCIDENT_REPLAY_V1** permanent red samples
- **Input provenance manifest** for derived live artifacts
- **Negative fixture** routing through production runners

See anonymized real case: [`examples/real-cases/02-derived-freshness-stale-panel.md`](../../examples/real-cases/02-derived-freshness-stale-panel.md)
