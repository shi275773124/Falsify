# falsify-ai-pr-review

## When To Use

Use this workflow when an AI agent or human claims a PR, migration, refactor, policy change, or generated code is safe.

## Inputs Required

- PR claim and requested decision.
- Diff, affected files, public API surface, and migration scope.
- Test commands and raw output.
- CI result and logs.
- Runtime verification output when behavior changes.
- Permission, secret, config, or environment changes.

## Evidence Requirements

Require raw diff, command output, and evidence that tests cover the risky invariant. Model agreement and green CI are supporting context, not proof.

## Review Procedure

1. Frame the risky invariant, runtime path, public contract, and permission boundary.
2. Compare the claim with the diff and tests.
3. Attack CI theater, wrong tests, permission drift, public API drift, and missing runtime verification.
4. Classify findings into Must Fix, Known Debt, or Delete.
5. Return only the verdict schema.

## Verdict Rules

- `PASS`: evidence covers the risky invariant and runtime path.
- `PASS_WITH_DEBT`: non-blocking debt has explicit upgrade trigger.
- `BLOCK`: tests checked the wrong thing, raw evidence is missing, public contract drift is unresolved, or permission drift is unverified.

## BLOCK Conditions

- Tests pass but do not cover the migration invariant.
- Another AI agreed but provided no raw evidence.
- Permission, API, config, or runtime contract drift is unresolved.
- CI is advisory theater and no real check ran.
- No runtime verification for behavior-changing PR.

## PASS_WITH_DEBT Conditions

- Low-risk code path has partial coverage with trigger.
- Follow-up refactor is documented and not needed for current safety.
- Runtime verification is limited but current invariant is covered.

## Output Format

Return JSON matching `templates/verdict.schema.json`.

## Pitfalls

- Do not treat "no diff risk found" as evidence.
- Do not accept screenshots of green CI without command context.
- Do not let PASS_WITH_DEBT hide a missing invariant test.

## Minimal Action Examples

- Add a failing test for the migration invariant.
- Attach runtime verification from the changed path.
- Compare public API before and after the PR.

## Authority exit (Claiming Falsify)

This pack defines **what to attack**. It does **not** replace the product CLI.

Claiming Falsify requires running an authority exit and keeping the artifact:

- `python -m falsify review …` / `python -m falsify demo`
- Quant (optional): `python -m falsify.quant_gate …` after `pip install falsify[quant]`
- CI: templates under repo `templates/`

See `skills/README.md` and `docs/ROOTFIX-architecture.md`.

## Commercial Upgrade Path

- Move from starter skill to Audit Sprint when one PR or migration is high-risk enough to block a launch, deployment, or customer commitment.
- Move from repeated PR reviews to a Design Partner pilot when the team wants Falsify mapped into code review, CI, and release policy.
- Require enterprise controls when teams need shared policy, review history, report retention, managed integrations, private deployment, RBAC, SSO, audit logs, or support/SLA.
