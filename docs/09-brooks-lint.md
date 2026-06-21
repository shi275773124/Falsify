# Brooks-Lint

Brooks-Lint is the first Falsify layer. It looks for structural decay that makes AI-generated work hard to audit.

It is named for the failure pattern where complexity hides inside coordination, ownership, and verification paths. The output is not a style score. The output is a list of review targets that make evidence weaker.

## What it looks for

- hidden state
- implicit authority
- duplicated control paths
- brittle rollback
- unverifiable acceptance
- unreadable diffs
- AI summaries replacing raw evidence
- passing tests that do not cover the decision being claimed

## Why it matters

An AI summary can sound precise while hiding the artifact a human needs to inspect. A green log can say a job completed without proving the intended system state changed. A test can pass while checking the wrong invariant.

Brooks-Lint catches those structural gaps before the adversarial reviewer decides whether the claim should pass.

## Output

Each item should answer:

```text
Structural issue:
Why it weakens auditability:
Evidence needed:
Current decision affected:
```

If the current decision relies on the missing evidence, pass the item to Risk Scalpel as `Must Fix`.

If the issue is real but not blocking the current phase, classify it as `Known Debt` with an upgrade trigger.

If there is no concrete current failure mode, classify it as `Delete`.
