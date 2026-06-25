# 12. Open Core Boundary

[Back to README](../README.md)

This document defines what stays open, what is paid, and what is intentionally deferred.

Core principle:

**Protocol open, workflow system paid.**

## Positioning

Falsify is not an "AI code reviewer".  
Falsify is a **decision gate for AI-era work**.

Code review and lint gates catch many issues. They still ask: "Does the diff look right?"  
Falsify asks: "Is this decision defensible?"

## Open vs Paid boundary (current)

### Protocol

- **Open**
  - Verdict semantics: `PASS / PASS_WITH_DEBT / BLOCK`
  - Cutline semantics: `Must Fix / Known Debt / Delete`
  - JSON schema for `falsify review --json`
- **Paid (reserved)**
  - Custom enterprise taxonomy beyond core cutline

### CLI

- **Open**
  - `falsify lint`
  - `falsify review --json`
  - `falsify demo`
- **Paid (reserved)**
  - team runner orchestration
  - queueing / concurrency controls

### GitHub / CI gate

- **Open**
  - basic workflow template
  - BYOK execution
  - JSON + Markdown artifacts
- **Paid (reserved)**
  - managed GitHub App
  - org-wide rollout controls and governance

### Policy

- **Open**
  - `.falsify/policy.yml` base fields
- **Paid (reserved)**
  - policy UI
  - approval workflow
  - policy version history and governance

### Reporting

- **Open**
  - local/CI artifacts (`falsify-report.json`, `falsify-report.md`)
- **Paid (reserved)**
  - historical store
  - cross-repo aggregation
  - trend and governance reporting

### Integrations

- **Open**
  - examples and webhook patterns
- **Paid (reserved)**
  - production-grade integrations (Linear/Jira/Slack/SIEM)

### Deployment

- **Open**
  - local + CI usage
- **Paid (reserved)**
  - private deployment, SSO, RBAC, audit logs

## What we deliberately avoid now

- Splitting repos early
- Full SaaS dashboard
- Hosted billing complexity
- Multi-model voting systems

## Trigger to revisit physical repo split

We split into `falsify` + `falsify-team` only when all are true:

1. Team features are stable for at least one paying design partner
2. API/schema boundaries are versioned
3. Multi-repo development overhead is lower than single-repo confusion

## Known Debt — open-core business model

**Why not blocking:** OSS protocol + MIT templates are shipped and self-hostable today. Patterns like dbt/Vault-style open core are analogies for how teams sell workflow around an open spec — not proof that Falsify Team will convert.

**Upgrade trigger:** Becomes Must Fix when we claim "open core is proven" in marketing, publish funnel/conversion data, or sign the first paying Team customer without updating this section.
