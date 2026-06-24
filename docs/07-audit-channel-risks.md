# Audit-Channel Risks

Audit-channel risks are failures in the review path itself. Falsify treats them as normal findings and cuts them through Cutline / 风险裁刀. They do not create a fourth layer.

## Human-auditability breaks

A review fails when the verdict depends on an opaque AI summary, unreadable generated text, hidden prompt state, or missing raw artifacts.

Evidence should bottom out in raw artifacts a human can inspect: code, diffs, logs, source links, command output, fixtures, raw model responses, or provider metadata.

## Semantic verdict nudge

Ordinary language can push a reviewer toward `PASS` or `PASS_WITH_DEBT` without satisfying the gate.

Examples:

- "not blocking"
- "enough evidence"
- "another model agrees"
- "just theoretical"
- blocker relabeled as Known Debt without an upgrade trigger

Falsify asks whether the evidence changed. If the evidence did not change, the verdict should not soften.

## Prompt-only audit theater

A prompt or checklist line saying "watch for prompt injection" is not a defense.

Prefer:

- a known-pattern check for known failure modes
- a fixture
- a reproducer
- raw model output
- parse status and failure handling

A known-pattern library does not prove unknown channels are absent.

## Monitor-failure laundering

Empty, truncated, filtered, unparseable, or confident "no issue" outputs are not clean by default.

When an LLM/API probe is used as evidence, keep:

- raw verdict
- parse status
- HTTP status
- `finish_reason`
- usage/token counts when available
- raw response or a durable pointer to it

If those fields are missing and the current decision relies on the probe, classify the finding as `Must Fix`.

## Cutline

Use `Must Fix` when the current decision depends on missing audit-channel evidence.

Use `Known Debt` when the risk is real but the current phase is read-only, does not authorize action, and includes a trigger such as "becomes Must Fix when this gates CI, production, money, account authority, or public release."

Use `Delete` when the concern has no concrete current failure mode.
