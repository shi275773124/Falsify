# Audit Sprint — Deliverables Pack

> Fixed-fee service for **one high-risk artifact** (a deploy plan, PR, research
> report, or decision doc). Four deliverables, one signed verdict:
> **claim manifest → kill-shots → evidence pack → verdict receipt.**
>
> The verdict is bounded: it signs only what was actually proven, for the scoped
> claims below. Unless an authority adapter and the unified kernel are involved,
> the receipt is `EPISTEMIC_ONLY` with `capital_authority: NONE` — it does not
> authorize a merge, payment, deploy, or any other live action.

## 0. Sprint header

| Field | Value |
|---|---|
| Artifact under review | <!-- link / commit / version --> |
| Decision owner | <!-- who acts on this verdict --> |
| Sprint window | <!-- start → end --> |
| Scope statement | <!-- what this sprint covers — and what it does not --> |

## 1. Claim manifest

Every consequential statement in the artifact, framed as a claim with its scope
and the authority that could prove it.

| Claim ID | Claim (verbatim or close paraphrase) | `claim_scope` | Authority path that could prove it |
|---|---|---|---|
| C1 |  |  |  |
| C2 |  |  |  |

## 2. Kill-shots

The adversarial attacks against each claim — the failures existing checks missed —
and the executable evidence check that settles each one.

| Claim ID | Kill-shot (how this claim fails) | Executable evidence check (command / probe / artifact) |
|---|---|---|
| C1 |  |  |
| C2 |  |  |

## 3. Evidence pack

Raw artifacts only: command output, API reads, diffs, logs with parse status.
No summaries as evidence; no second-model agreement as proof.

| Check | Artifact (raw output / link) | Result | Parse status |
|---|---|---|---|
| C1-K1 |  | supports / contradicts / missing |  |
| C2-K1 |  | supports / contradicts / missing |  |

## 4. Verdict receipt

One receipt per scoped claim, then one final verdict for the sprint. Every
receipt carries all six authority fields — a bare `PASS` / `BLOCK` is not a
valid receipt.

```json
{
  "claim_scope": "<scope from the manifest>",
  "llm_semantic_verdict": "PASS | PASS_WITH_DEBT | BLOCK",
  "evidence_verdict": "PASS | PASS_WITH_DEBT | BLOCK",
  "final_verdict": "PASS | PASS_WITH_DEBT | BLOCK",
  "authority_ceiling": "EPISTEMIC_ONLY",
  "capital_authority": "NONE"
}
```

| Claim ID | Receipt verdict | Must Fix | Known Debt (with upgrade trigger) | Delete |
|---|---|---|---|---|
| C1 |  |  |  |  |
| C2 |  |  |  |  |

**Final sprint verdict:** `PASS | PASS_WITH_DEBT | BLOCK` — the most conservative
receipt wins.

## 5. Sign-off and boundary

- [ ] Every claim in the manifest has a receipt with all six authority fields.
- [ ] Every `PASS` names its `claim_scope` and `authority_ceiling`.
- [ ] Any action-bearing claim has an authority adapter + executable evidence +
      unified kernel sign-off; otherwise the ceiling stays `EPISTEMIC_ONLY`.
- [ ] The artifact, this pack, and the raw evidence are stored together.

| Role | Name | Date | Signature |
|---|---|---|---|
| Reviewer |  |  |  |
| Decision owner |  |  |  |
