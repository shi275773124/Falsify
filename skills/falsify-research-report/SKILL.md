# falsify-research-report

## When To Use

Use this workflow when a research, market, investment, vendor, or strategy memo claims evidence supports a decision.

## Inputs Required

- Claim, decision, and recommendation.
- Source list with dates and access dates.
- Raw excerpts, tables, data files, screenshots, or hashes.
- Method, sample, filters, and exclusions.
- Counter-evidence and falsifier.

## Evidence Requirements

Require dated primary or traceable sources. Summaries, uncited tables, and model-written conclusions are not enough.

## Review Procedure

1. Frame the claim, decision boundary, mechanism, and time sensitivity.
2. Check source dates, raw artifacts, method, and conclusion scope.
3. Attack cherry-picking, stale data, mechanism mismatch, missing falsifier, and conclusion overreach.
4. Classify findings into Must Fix, Known Debt, or Delete.
5. Return only the verdict schema.

## Verdict Rules

- `PASS`: sources are current enough, raw artifacts exist, and conclusion matches evidence.
- `PASS_WITH_DEBT`: evidence supports a narrower decision and all debt has triggers.
- `BLOCK`: source dates are missing, evidence is stale, claim overreaches, or falsifier is absent for a high-risk decision.

## BLOCK Conditions

- Stale source or missing source date.
- Cherry-picked evidence.
- Conclusion overreach.
- Missing falsifier.
- Mechanism mismatch between data and claim.
- Raw artifact missing.

## PASS_WITH_DEBT Conditions

- Source is acceptable for a bounded decision but requires refresh trigger.
- Conclusion is narrowed to match available evidence.
- Secondary source is used with explicit primary-source follow-up.

## Output Format

Return JSON matching `templates/verdict.schema.json`.

## Pitfalls

- Do not treat a polished memo as evidence.
- Do not hide uncertainty in executive-summary language.
- Do not accept market-size claims without source date and method.

## Minimal Action Examples

- Add source dates and raw excerpts.
- Narrow conclusion to what data proves.
- Attach a falsifier that would change the decision.

## Commercial Upgrade Path

- Move from starter skill to Audit Sprint when one report drives an investment, market, vendor, or strategic decision.
- Move from repeated report audits to a Design Partner pilot when the team wants evidence standards embedded in research workflow.
- Require enterprise controls when teams need shared policy, review history, report retention, managed integrations, private deployment, RBAC, SSO, audit logs, or support/SLA.
