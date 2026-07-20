# Team Delivery & Business Model Blueprint

This page turns Falsify from a framework into a sellable product.

> **Status legend (mandatory on every offer):** `AVAILABLE` = shipped or bookable today · `DESIGN_PARTNER` = scoped private pilot, integrated per concrete authority path · `TARGET_NOT_SHIPPED` = roadmap target — not a delivered feature, never sell it as one.

## Who we sell to first

Primary customer: AI-native software teams (5-80 engineers), with a technical decision owner:

- CTO / VP Engineering
- Eng manager running release quality
- Staff engineer owning platform reliability

Why them:

- They feel the pain of false PASS immediately (incident, rollback, lost trust).
- They can pay for workflow tooling and compliance guardrails.
- They already use GitHub, Jira, and CI gates.

## Product packaging (what gets delivered)

### L0 - Public website demo (free) — `AVAILABLE`

- Goal: explain the method and capture demand
- Deliverable: static sample verdicts (no live token burn)
- CTA: "Run locally", "Join waitlist", "Book audit"

### L1 - Falsify Review / Builder (free / OSS) — `AVAILABLE`

- Goal: individual adoption
- Deliverable: local CLI + templates + docs; adversarial LLM review with a bounded **epistemic** verdict (`PASS` / `PASS_WITH_DEBT` / `BLOCK` with `claim_scope` and `authority_ceiling`)
- Billing: user brings own model key (BYOK)

### L1.5 - Audit Sprint (service) — `AVAILABLE`

- Goal: prove value on one artifact before any platform commitment
- Deliverable: claim manifest, kill-shots, evidence pack, and a signed verdict receipt for one high-risk artifact — fixed format in [templates/audit-sprint.md](../templates/audit-sprint.md)
- Billing: fixed-fee sprint

### L2 - Falsify Authority Gate — `DESIGN_PARTNER` (adapter required)

- Goal: let a verdict bear action on a real system
- Deliverable: executable evidence checks against a concrete authority path (deploy, data, execution); only with an adapter can a `PASS` bear action. No public adapter ships today — without one, every verdict stays epistemic.
- Billing: scoped pilot integration, not self-serve

### L3 - Team (paid, default motion) — `TARGET_NOT_SHIPPED`

- Goal: team workflow integration and governance
- Deliverable (target, not shipped):
  - shared rule packs
  - PR gate policy (advisory/required)
  - decision artifact export (markdown + machine-readable summary)
  - trend dashboard (BLOCK rate, debt carry-over)
- Billing (target): seat + usage cap, or team credits

### L4 - Enterprise (high ACV) — `TARGET_NOT_SHIPPED`

- Goal: security/compliance and rollout support
- Deliverable (target, not shipped):
  - SSO, RBAC, audit log
  - private deployment / VPC
  - custom policy packs by repo/risk tier
  - enablement + periodic review cadence
- Billing (target): annual contract + onboarding

## Delivery workflow that buyers understand — `TARGET_NOT_SHIPPED`

1. Connect repo(s)
2. Pick policy mode per branch:
   - advisory (comment only)
   - required (BLOCK fails check)
3. Falsify runs on PR / release claims
4. Findings are pushed to existing tools (GitHub/Jira/Linear)
5. Team reviews one decision artifact:
   - verdict
   - must-fix list
   - known debt with upgrade trigger
6. Weekly summary for engineering lead

## Pricing shapes used by peers — `TARGET_NOT_SHIPPED`

Choose one primary shape and one fallback:

- Seat-first (predictable budget):
  - Team: fixed per committer/month
  - Include a fair-use review quota
- Credits/usage (cost-aligned):
  - budget pool shared by workspace
  - burn rate by review depth and changed scope
- BYOK hybrid (best token control):
  - platform fee for orchestration/governance
  - model tokens billed to customer key

Recommended for Falsify now: BYOK hybrid for Team, annual contract for Enterprise. (Target pricing — nothing on this line is a shipped, bookable SKU yet.)

## Example offer design

- Free — `AVAILABLE`: OSS CLI + docs + demo
- Audit Sprint — `AVAILABLE` (service): fixed-fee review of one high-risk artifact; claim manifest, kill-shots, evidence pack, signed verdict receipt
- Team: $49-99 per active committer/month — `TARGET_NOT_SHIPPED`
  - includes shared templates, PR gate, exports
  - BYOK default, optional managed credits add-on
- Enterprise path: custom annual — `TARGET_NOT_SHIPPED`
  - SSO, audit logs, private deployment, and support path only where explicitly supported or contracted

## Commercial KPIs to track

- Activation: first successful PR review in < 1 day
- Value: % of BLOCK findings fixed within 7 days
- Cost discipline: median token cost per useful finding
- Expansion: repos/workspaces per paying org
- Reliability: false positive dispute rate

## Positioning line

Many automated checks focus on diffs and green CI. Falsify reviews whether a decision is defensible.
