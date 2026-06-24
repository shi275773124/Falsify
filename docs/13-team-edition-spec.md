# 13. Team Edition Spec (Reserved)

[Back to README](../README.md)

This page describes Team/Enterprise scope as a product spec, not as immediate implementation.

## Product tiers (spec-level)

### OSS (current)

- CLI + JSON review
- BYOK
- CI/PR gate template
- artifacts (JSON/MD)

### Team (target)

- PR comments and check policies at workspace level
- shared policy packs
- report retention and query
- one integration channel (pick one first)

### Pro Team (target)

- multi-repo governance
- scheduled audits
- expanded integrations (Linear/Jira/Slack)

### Enterprise (target)

- private deployment options
- SSO/RBAC/audit logs
- custom onboarding and workflow design

## Team MVP order (strict)

1. PR comment + check (must already work)
2. JSON/MD artifacts (must be stable schema)
3. policy.yml enforcement
4. artifact history retention
5. single integration (one only)
6. dashboard (last)

## Non-goals right now

- Hosted dashboard first
- complex billing engine
- policy DSL expansion
- marketplace for rules

## Required quality bars before Team launch

- Schema compatibility policy published
- `Known Debt` trigger validation enforced in gate
- deterministic BLOCK behavior from JSON source of truth
- documentation for BYOK, limits, and incident handling

## Metrics for Team design-partner phase

- first-value time (first useful BLOCK) < 1 day
- false positive dispute rate
- remediation completion rate for Must Fix
- debt trigger follow-through rate
- cost per useful finding (BYOK token economics)

