# Team Delivery & Business Model Blueprint

This page turns Falsify from a framework into a sellable product.

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

### L0 - Public website demo (free)

- Goal: explain the method and capture demand
- Deliverable: static sample verdicts (no live token burn)
- CTA: "Run locally", "Join waitlist", "Book audit"

### L1 - Builder (free / OSS)

- Goal: individual adoption
- Deliverable: local CLI + templates + docs
- Billing: user brings own model key (BYOK)

### L2 - Team (paid, default motion)

- Goal: team workflow integration and governance
- Deliverable:
  - shared rule packs
  - PR gate policy (advisory/required)
  - decision artifact export (markdown + machine-readable summary)
  - trend dashboard (BLOCK rate, debt carry-over)
- Billing: seat + usage cap, or team credits

### L3 - Enterprise (high ACV)

- Goal: security/compliance and rollout support
- Deliverable:
  - SSO, RBAC, audit log
  - private deployment / VPC
  - custom policy packs by repo/risk tier
  - enablement + periodic review cadence
- Billing: annual contract + onboarding

## Delivery workflow that buyers understand

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

## Pricing shapes used by peers

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

Recommended for Falsify now: BYOK hybrid for Team, annual contract for Enterprise.

## Example offer design

- Free: OSS CLI + docs + demo
- Team: $49-99 per active committer/month
  - includes shared templates, PR gate, exports
  - BYOK default, optional managed credits add-on
- Enterprise: custom annual
  - SSO, audit logs, private deployment, support SLA

## Commercial KPIs to track

- Activation: first successful PR review in < 1 day
- Value: % of BLOCK findings fixed within 7 days
- Cost discipline: median token cost per useful finding
- Expansion: repos/workspaces per paying org
- Reliability: false positive dispute rate

## Positioning line

Many automated checks focus on diffs and green CI. Falsify reviews whether a decision is defensible.

