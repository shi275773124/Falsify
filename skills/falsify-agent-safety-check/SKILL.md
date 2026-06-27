# falsify-agent-safety-check

## When To Use

Use this workflow when an autonomous or semi-autonomous agent claims task completion, especially before trusting external side effects or irreversible actions.

## Inputs Required

- Agent completion claim and requested trust decision.
- Task objective, allowed tools, and permission boundary.
- Raw tool outputs and artifact paths.
- Read-back verification of files, services, tickets, messages, or external state.
- List of irreversible actions and approval gates.

## Evidence Requirements

Agent self-report is not proof. Require raw artifact trail and read-back verification from the external system or file state that matters.

## Review Procedure

1. Frame task objective, side effects, permissions, and irreversible actions.
2. Compare self-report with raw tool outputs and read-back evidence.
3. Attack missing artifact trail, unverified side effects, permission drift, and skipped approval gates.
4. Classify findings into Must Fix, Known Debt, or Delete.
5. Return only the verdict schema.

## Verdict Rules

- `PASS`: artifacts and external side effects are independently verified.
- `PASS_WITH_DEBT`: current completion is verified and every residual risk has a trigger.
- `BLOCK`: self-report is treated as proof, side effects are not read back, irreversible actions lack a gate, or permissions drifted.

## BLOCK Conditions

- Self-report treated as proof.
- External side effects not verified.
- Irreversible actions without gate.
- Missing artifact trail.
- Tool output not read back.
- Permission boundary drift.

## PASS_WITH_DEBT Conditions

- Artifact exists but retention needs improvement with trigger.
- Non-critical side effect is queued and bounded.
- Permission expansion is documented and time-limited.

## Output Format

Return JSON matching `templates/verdict.schema.json`.

## Pitfalls

- Do not accept "done" without artifact paths.
- Do not trust a tool call unless its output was read and mapped to the objective.
- Do not ignore side effects outside the workspace.

## Minimal Action Examples

- Read back the created artifact from disk or external system.
- Attach tool output and final state evidence.
- Add an approval gate before irreversible actions.

## Commercial Upgrade Path

- Move from starter skill to Audit Sprint when one agent completion claim affects production, customers, money, permissions, or irreversible actions.
- Move from repeated agent checks to a Design Partner pilot when agent sign-off should become a standard workflow gate.
- Require enterprise controls when teams need shared policy, review history, report retention, managed integrations, private deployment, RBAC, SSO, audit logs, or support/SLA.
