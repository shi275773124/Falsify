# 06. Risk Scalpel (Layer 3)

[中文](./06-risk-scalpel.zh-CN.md) · [Back to README](../README.md)

**This is Layer 3.** [Layer 1 — peer review](./03-collaboration.md) catches wrong facts. [Layer 2 — adversarial review](./05-adversarial-review.md) catches wrong conclusions. **Risk Scalpel catches the failure after a good review: turning every finding into a P0, or deleting real risks in the name of simplicity.**

Falsify finds what can go wrong. Risk Scalpel decides what must change now.

---

## The problem

A strong adversarial review can produce ten good findings. Two bad things then happen:

1. **Patch bloat** — every finding becomes urgent, the first version never ships.
2. **False simplicity** — the team says “cut scope” and quietly deletes real risks.

Risk Scalpel is the decision layer between review findings and implementation work.

It does not erase risk facts. It only decides whether a risk blocks the current deliverable.

---

## One-line rule

```text
Adversarial review produces failure modes.
Risk Scalpel cuts scope, not risk facts.
```

Every finding is rewritten as:

```text
Finding:
Failure mode if unfixed:
Current phase/objective:
```

Then classified into exactly one bucket.

---

## The three buckets

| Class | Use when leaving it unfixed can cause... | Required output | Forbidden |
|---|---|---|---|
| **Must Fix** | false truth, false risk, silent failure, unauthorized action, non-reproducibility, or a current-phase verification break | minimal fix + verification evidence | “later optimization” |
| **Known Debt** | real risk, but not blocking the current phase | debt note + upgrade trigger | vague TODO |
| **Delete** | no concrete current failure mode; only completeness, generic abstraction, prettier reporting, dashboard desire, or platformization | deletion reason | renaming it back into the backlog |

---

## Must-Fix gates

A finding is **Must Fix** if leaving it unfixed can make any of these false or unsafe in the current deliverable:

1. **Truth** — the report can publish false numbers, facts, or conclusions.
2. **Risk** — the system can understate exposure, permissions, blast radius, or safety state.
3. **Silence** — missing, stale, or broken data can look like success.
4. **Action boundary** — wording or code can imply or trigger action without authorization.
5. **Reproducibility** — later readers cannot reconstruct the number, source, unit, sign, or decision path.
6. **Verification** — the current phase cannot be tested or reviewed without fixing it.

If none of these apply, it is not automatically urgent.

---

## Known Debt must have a trigger

Known Debt is not a dumping ground. It must say when it becomes urgent.

```text
Known Debt: <issue>
Why not blocking now: <current phase does not depend on it>
Upgrade trigger: becomes Must Fix when <specific event/scale/use-case happens>
```

Examples:

- **Full machine-readable schema** → debt now; Must Fix when reports are consumed by CI, dashboards, or other programs.
- **Advanced attribution** → debt now; Must Fix when attribution is used to stop, resize, approve, or expand a decision.
- **Generic adapter/framework** → debt now; Must Fix when two real implementations need the same normalized interface.

No upgrade trigger means it is not valid debt. Make it Must Fix or Delete.

---

## Output template

```markdown
## Verdict
PASS / PASS_WITH_CONDITIONS / BLOCK

## Cut-line table
| Finding | Failure mode if unfixed | Class | Minimal action | Upgrade trigger |
|---|---|---|---|---|

## Must Fix now
- ...

## Known Debt
- ... — Upgrade when ...

## Delete
- ... — reason

## One-line rule
...
```

---

## Worked micro-example

Adversarial review finds:

```text
The proposed system has no full JSON schema.
```

Risk Scalpel rewrites it:

```text
Finding: no full JSON schema.
Failure mode if unfixed: downstream tools may misread fields once reports are machine-consumed.
Current phase/objective: human-reviewed v0 report.
```

Classification:

```text
Known Debt: full JSON schema.
Why not blocking now: v0 is human-read only.
Upgrade trigger: Must Fix when the report is consumed by CI, dashboards, aggregation, or another program.
```

Same finding, later phase:

```text
Current phase/objective: CI blocks deploys based on this report.
Class: Must Fix.
Minimal action: define field names, units, signs, missing-data policy, and schema validation.
```

---

## Anti-patterns

- **Reviewer owns the roadmap** — adversarial findings are attack surface, not automatic requirements.
- **“Minimal” deletes risk facts** — cut implementation scope, not the record of what can go wrong.
- **Debt without trigger** — this is just a hidden backlog.
- **Project-management creep** — Risk Scalpel is one table and one verdict, not a planning system.
- **Action leakage** — an evidence layer should not quietly become an action recommendation layer.

---

## Where it fits

```text
Layer 1 · Peer Review        → wrong facts / wrong numbers
Layer 2 · Adversarial Review → right facts, wrong conclusion
Layer 3 · Risk Scalpel       → review aftermath: Must Fix / Known Debt / Delete
```

Use Layer 3 after Layer 2, after a code-decay review, or after any serious audit that returns more findings than can safely become immediate work.
