# falsify-brooks-lint

## Provenance

| Field | Value |
|-------|--------|
| skill_id | `falsify-brooks-lint` |
| layer | L0 Framework (Brooks-Lint) |
| upstream | `hyhmrright/brooks-lint` |
| fork_branch | `chris-improvements` |
| source_sha | `6be92af94839175665c35df77390e7baab78a303` |
| vendor_note | References copied from Hermes pack + local fork at pin time; Falsify pack is now the product source of truth |

Marketing alias:「框架审计」。Protocol name: **Brooks-Lint (L0)**.

## When To Use

Use this workflow when you need the **structural / auditability** layer before (or without) a full adversarial attack:

- PR, migration, refactor, or agent-generated code that will be maintained, re-run, or cited as evidence
- Claims that “the design is clean” / “ready to merge” / “no structural risk”
- Any claim-bearing Falsify `review` / `run` path (product default: L0 runs first)

Do **not** use this pack as a substitute for `falsify lint` (markdown tag/blocker only) or as Claiming Falsify without a CLI authority exit.

## Inputs Required

- Review scope: paths, diff, or pasted code (if none, apply Auto Scope Detection from `references/common.md`)
- Claim / decision under review and owner
- Authority path and claim ceiling when available
- Test commands and raw output when acceptance is claimed
- Config / permission / rollback surface when relevant

## Evidence Requirements

**Evidence Gate** (from `references/chris-improvements.md`): every Critical / Warning finding **must** carry at least one of:

- File path + line range (`path/to/file.py:127-145`)
- Inline diff snippet (≥ 3 lines)
- Command + observable output

If the assistant cannot point to a concrete artifact, the finding does not exist (downgrade to suggestion or drop). Model agreement is not evidence.

## Review Procedure

1. Load references in order:
   1. `references/common.md` — Iron Law, project config, report template, health score
   2. `references/chris-improvements.md` — Evidence Gate, Scope Refusal, Light Mode
   3. `references/source-coverage.md` — book-level coverage and tradeoffs
   4. `references/decay-risks.md` — symptom definitions
   5. `references/pr-review-guide.md` — analysis steps
2. **Scope gate:** if Q1–Q3 in chris-improvements are all no → emit **SCOPE_REFUSED** (counts as L0 ran; do not template-fill).
3. Choose mode: **Full** (default) or **Light** (small, medium-risk change per chris-improvements).
4. Scan decay risks (Full) or answer Light Mode’s three questions.
5. Apply Iron Law to every finding; attach Artifact for Critical/Warning.
6. Map findings into Cutline: Must Fix / Known Debt / Delete.
7. Return JSON matching `templates/verdict.schema.json` (optional `layer: "brooks_lint"`).

**Mode line:** `PR Review` (or `Light` / `SCOPE_REFUSED` as applicable).

Terminal status for product receipts:

```text
BROOKS_STATUS: RAN | SCOPE_REFUSED | SKIPPED
```

(`SKIPPED` is for explicit diagnostic skip only — not a successful L0.)

## Verdict Rules

- `PASS`: no Must Fix; structural surface is auditable for the current claim; Known Debt (if any) has upgrade triggers.
- `PASS_WITH_DEBT`: no Must Fix; Known Debt items have explicit upgrade triggers.
- `BLOCK`: at least one Must Fix (structural gap blocks the current decision), missing required evidence, or unparsable review.
- `SCOPE_REFUSED` (mode/status, not a product PASS): no decay surface; do not invent findings.

L0 Must Fix has the same weight as adversarial Must Fix for product adjudication.

## BLOCK Conditions

- Hidden state / implicit authority / duplicated control path blocks verification of the claim
- Brittle rollback or unverifiable acceptance for the decision being claimed
- Critical finding without Evidence Gate artifact (treat as invalid or escalate to BLOCK for missing evidence)
- Tests pass but do not cover the structural invariant claimed
- AI summary replaces raw artifacts required for audit

## PASS_WITH_DEBT Conditions

- Real structural debt not blocking this phase, with upgrade trigger
- Light Mode completed with known follow-ups that do not break the current invariant

## Output Format

Return JSON matching `templates/verdict.schema.json`. Prefer `layer: "brooks_lint"` when embedding in multi-layer receipts.

Finding shape (narrative fields also fine inside `issue` / `evidence`):

```text
Structural issue:
Why it weakens auditability:
Evidence needed:
Current decision affected:
Artifact:
```

## Pitfalls

- Do not treat `falsify lint` green as Brooks-Lint complete.
- Do not invent catalog findings on SCOPE_REFUSED surfaces.
- Do not skip Evidence Gate for “obvious” Critical items.
- Do not claim Falsify PASS from this pack alone without CLI authority exit.

## Minimal Action Examples

- Point the claim at a single authority path and attach raw state evidence
- Add a test for the structural invariant (not only happy-path coverage)
- Collapse duplicated control paths or document the one true writer
- Attach path:line or command output for each Must Fix

## Authority exit (Claiming Falsify)

This pack defines **what to attack at L0**. It does **not** replace the product CLI.

Claiming Falsify requires running an authority exit and keeping the artifact:

- `python -m falsify review …` (default runs L0 Brooks-Lint before L1)
- `python -m falsify brooks <path>` (L0-only; JSON includes `brooks_lint` block)
- `python -m falsify demo`
- Quant (optional): `python -m falsify.quant_gate …` after `pip install falsify[quant]`
- CI: templates under repo `templates/`

**Not authority for Brooks-Lint:** `python -m falsify lint` (markdown tag/blocker only).

See `skills/README.md`, `docs/09-brooks-lint.md`, and `docs/ROOTFIX-architecture.md`.

## Commercial Upgrade Path

- Move from starter L0 pack to Audit Sprint when structural debt blocks a launch or customer commitment.
- Move to Design Partner when the team wants Brooks-Lint wired into CI/release policy with shared history.
- Require enterprise controls for shared policy, retention, private deployment, RBAC, SSO, or SLA.
