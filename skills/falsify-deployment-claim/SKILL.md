# falsify-deployment-claim

## When To Use

Use this workflow when a team claims a deployment, rollback, incident fix, migration, or production change succeeded because CI passed, logs completed, or an agent reported success.

## Inputs Required

- Claim text and decision being requested.
- Deployment target, environment, service, commit, build, or release id.
- Raw CI output or deploy logs.
- Post-deploy state query, read-after-write probe, or invariant check.
- Rollback command or rollback point.
- Account, region, tenant, or permission context.

## Evidence Requirements

Logs are not state proof. Require at least one raw artifact proving the intended state changed in the target environment. Evidence should include timestamp, command, target, status, and owner.

## Review Procedure

1. Frame the claim, target, scope, invariants, and irreversible risk.
2. Separate execution evidence from state evidence.
3. Attack silent failure, wrong target, wrong account, permission drift, stale monitor, and missing rollback.
4. Assign each finding to Must Fix, Known Debt, or Delete.
5. Return only the verdict schema.

## Verdict Rules

- `PASS`: state proof exists, target is correct, rollback point exists, and no blocker remains.
- `PASS_WITH_DEBT`: no blocker remains and every debt has an upgrade trigger.
- `BLOCK`: any Must Fix remains, state proof is missing, rollback is unknown, or output cannot be audited.

## BLOCK Conditions

- Logs green are treated as state proof.
- Missing read-after-write probe or post-deploy query.
- Missing rollback point.
- No state, account, tenant, region, or permission verification.
- Silent failure is plausible.
- Raw artifacts are absent or stale.

## PASS_WITH_DEBT Conditions

- Verification exists but monitoring is partial.
- Rollback exists but rehearsal evidence is old.
- Non-critical permission drift is documented with trigger.

## Output Format

Return JSON matching `templates/verdict.schema.json`.

## Pitfalls

- Do not accept screenshots without command/source context.
- Do not accept "another AI reviewed it" as evidence.
- Do not call advisory logs a PASS.
- Do not invent probes that were not run.

## Minimal Action Examples

- Add a read-after-write probe against the deployed system.
- Attach a post-deploy query result and rollback command.
- Re-run verification with explicit account, region, and service target.

## Commercial Upgrade Path

- Move from starter skill to Audit Sprint when one deployment claim controls a production, customer, money, or incident decision.
- Move from repeated deployment reviews to a Design Partner pilot when the same evidence gate should become part of release workflow.
- Require enterprise controls when teams need shared policy, review history, report retention, managed integrations, private deployment, RBAC, SSO, audit logs, or support/SLA.
