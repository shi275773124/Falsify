# Examples

These are synthetic examples, not customer cases.

## Example 1: logs are not state

Claim:

```text
Deployment succeeded because the logs completed successfully.
```

Falsify finding:

```text
[AGENT-B audit] logs are treated as state verification
Failure mode: logs prove something ran; they do not prove the intended system state changed
Cutline: Must Fix
Evidence needed: raw artifact or command output that proves the claim
Minimal action: verify the actual state with a read-after-write check, deployment query, or invariant test
VERDICT: BLOCK
```

## Example 2: second model agreement is not proof

Claim:

```text
Another AI reviewed the prompt-injection risk and found no issue.
```

Falsify asks:

- Where is the raw output?
- Was the response parsed successfully?
- What was the HTTP status?
- What was the `finish_reason`?
- Were usage/token counts available?
- Which known-pattern check, fixture, or reproducer was run?

If those are missing and the current decision relies on the claim, the cutline is `Must Fix`.

## Example 3: twenty risks are not a decision

Normal audit:

```text
Here are 20 possible risks.
```

Falsify output:

```text
Must Fix:
- current decision relies on missing raw evidence
- deployment success is inferred from logs only

Known Debt:
- full machine-readable schema
  Upgrade trigger: becomes Must Fix when reports gate CI or dashboards

Delete:
- generic dashboard request with no current failure mode

VERDICT: BLOCK
```

The goal is not to shrink risk language until it feels simple. The goal is to keep real risks visible while blocking only what can break the current decision.
