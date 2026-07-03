# Pro/OSS Commercial Strategy — Cross-Bot Review Brief

Date: 2026-06-29

## Proposed strategy

**OSS (GitHub, MIT):**
- 5 MIT workflow packs (free hook, v0): deployment-claim, live-production-gate, ai-pr-review, research-report, agent-safety-check
- Protocol open: PASS / PASS_WITH_DEBT / BLOCK, Cutline, falsify.review.v1 JSON schema
- CLI: lint, review --json, demo; GitHub Action template; BYOK

**Pro (closed source):**
- Umbrella skill at `~/.cursor/skills/falsify` v0.1.0
- Daily vs Production boundary enforcement
- Incident replay + negative fixtures + input provenance manifest
- Skill manifest + Hermes runtime integration
- Optional hosted Hermes orchestration (future)

**Sync model:**
- One-way: self canonical (Pro skill + vault hermes-skills-runtime) → export subset to OSS live-gate pack only
- Paid moat = updates + fixture library + live loop + orchestration, NOT merely hiding files

**Gap:** `docs/18-pro-vs-oss.md` proposed but not written.

## Questions for each reviewer

1. Is Pro closed-source + OSS MIT split sound for Falsify?
2. What would you push back on (leak risk, trust, OSS too weak/too strong)?
3. One concrete change to the plan?

Respond as independent reviewer. Be adversarial. No politeness theater.
