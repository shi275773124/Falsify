# Brooks-Lint (L0 Framework)

[中文 README 入口](../README.zh-CN.md) · [Architecture](./01-architecture.md) · [Back to README](../README.md)

Brooks-Lint is **L0** in the Falsify gate loop — the **Framework** layer that looks for structural decay that makes AI-generated (or human-generated) work hard to audit.

Marketing may say「框架审计」. The **protocol name** is **Brooks-Lint (L0)**.

It is named for the failure pattern where complexity hides inside coordination, ownership, and verification paths. The output is not a style score. The output is a list of review targets that weaken evidence — classified into Cutline buckets before (or alongside) adversarial attack.

## Position in the gate loop

See [Architecture — gate pattern](./01-architecture.md#the-gate-pattern-public-core):

1. Frame  
2. **L0 Brooks-Lint (Framework)** ← this doc  
3. Attack (L1 adversarial)  
4. Recompute / re-read  
5. Cutline  
6. Receipt (must include `brooks_lint` block)

Claim-bearing `python -m falsify review` / `run` **default-runs L0** before L1. Without L0 proof on the receipt (`brooks_lint.ran == true` with status `RAN` or `SCOPE_REFUSED`), the product must not emit claim-bearing `PASS` / `PASS_WITH_DEBT`.

## Brooks-Lint vs `falsify lint`

| Tool | What it is | What it is not |
|------|------------|----------------|
| **Brooks-Lint (L0)** | Structural / auditability review of code, diffs, and claim surfaces | A markdown tag scanner |
| **`falsify lint`** | Local **markdown tag/blocker static check** (L2 gate path for decision docs) | Brooks-Lint |

`falsify gate` aggregates `falsify lint` over changed decision-doc files. That path does **not** satisfy the L0 Brooks obligation. Do not rename or describe `falsify lint` as Brooks-Lint.

## What it looks for

- hidden state  
- implicit authority  
- duplicated control paths  
- brittle rollback  
- unverifiable acceptance  
- unreadable diffs  
- AI summaries replacing raw evidence  
- passing tests that do not cover the decision being claimed  
- decay risks catalogued in the skill pack (`skills/falsify-brooks-lint/references/`)

## Modes (Full / Light / SCOPE_REFUSED)

From the vendored **chris-improvements** rules (`references/chris-improvements.md`):

| Mode | When | Behavior |
|------|------|----------|
| **Full** | Default for claim-bearing code/diff with real decay surface | Full decay catalog + Iron Law findings |
| **Light** | Small, medium-risk changes (e.g. &lt; 50 lines; no state schema / power-graph change) | Three short answers: invariant, single point of failure, verification command |
| **SCOPE_REFUSED** | Scope has no decay surface (throwaway research, no state/external/maintain surface) | Abort full catalog; emit one-line refusal; still counts as L0 **ran** for receipt proof |

`SCOPE_REFUSED` is **not** a skip. Skip (`--skip-brooks` / diagnostic only) sets `ran=false` and **cannot** satisfy L0 for PASS.

## Evidence Gate

Every Critical / Warning (Must Fix–grade) finding **must** carry at least one:

- path + line range (`path/to/file.py:127-145`)  
- inline diff snippet (≥ 3 lines)  
- command + observable output  

If there is no concrete artifact, the finding does not exist (downgrade to suggestion or drop). See `skills/falsify-brooks-lint/references/chris-improvements.md`.

## How findings feed Cutline

Each structural item should answer:

```text
Structural issue:
Why it weakens auditability:
Evidence needed:
Current decision affected:
Artifact:   # Evidence Gate
```

| Cutline | Rule |
|---------|------|
| **Must Fix** | Current decision relies on the missing evidence / structural gap → same weight as adversarial Must Fix; alone can force `BLOCK` |
| **Known Debt** | Real issue, not blocking this phase → requires an **upgrade trigger** |
| **Delete** | No concrete current failure mode → drop from the decision surface |

L0 Must Fix merges into the same cutline adjudication as L1 findings before the final verdict.

## Skill pack

| Path | Role |
|------|------|
| [`skills/falsify-brooks-lint/`](../skills/falsify-brooks-lint/) | OSS workflow pack (PR/review mode) |
| `SKILL.md` | When / Evidence / Procedure / Verdict / Authority exit |
| `references/*` | common, decay-risks, pr-review-guide, **chris-improvements**, source-coverage, … |
| `templates/verdict.schema.json` | `falsify.review.v1` + optional `layer: "brooks_lint"` |

**Provenance (pinned at vendor time):**

- upstream: `hyhmrright/brooks-lint`  
- fork_branch: `chris-improvements`  
- source_sha: see pack `README.md` / `SKILL.md` metadata  

Hermes or other agent hosts should treat **this pack** as the source of truth for Brooks-Lint in Falsify (copy/symlink from here), not a private Hermes-only tree.

## CLI surface

| Entry | L0 behavior |
|-------|-------------|
| `python -m falsify review …` / `run` | **Default:** run L0, then L1; receipt includes `brooks_lint` |
| `--skip-brooks` | Diagnostic only; `ran=false`; **cannot** claim PASS |
| `python -m falsify brooks <path>` | Optional L0-only path for agents/CI (JSON includes full `brooks_lint` block) |
| `python -m falsify lint …` | **Not** Brooks — markdown tag/blocker only |
| `python -m falsify gate` | L2 markdown aggregation stub — not L0 |

Receipt shape (illustrative; enforced by product CLI / authority kernel):

```json
"brooks_lint": {
  "ran": true,
  "mode": "full|light|scope_refused|skipped",
  "status": "RAN|SCOPE_REFUSED|SKIPPED|ERROR",
  "skill_id": "falsify-brooks-lint",
  "skill_version": "<pin or package version>",
  "findings_count": 0,
  "must_fix_count": 0,
  "raw_hash": "<sha256 of L0 raw text>",
  "skip_reason": null
}
```

## Why it matters

An AI summary can sound precise while hiding the artifact a human needs to inspect. A green log can say a job completed without proving the intended system state changed. A test can pass while checking the wrong invariant.

Brooks-Lint catches those structural gaps **before** the adversarial reviewer decides whether the claim should pass — and leaves a **receipt proof** that the framework layer actually ran.

## Related docs

- [Architecture](./01-architecture.md)  
- [Adversarial Review](./05-adversarial-review.md)  
- [Cutline / 风险裁刀](./06-risk-scalpel.md)  
- [Skills packs](./17-skills.md)  
- [CLI & artifacts](./20-cli-and-artifacts.md)  
- [ROOTFIX](./ROOTFIX-architecture.md)  
