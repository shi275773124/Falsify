# Chris Improvements (chris-improvements branch)

> Adds three rules on top of upstream `_shared/common.md`. Loaded automatically by
> every brooks-lint skill mode (review/audit/debt/test/health/sweep) via the
> reference appended to common.md.
>
> Source: real failure modes from running brooks-lint against production trading
> bots and research backtests. These are not stylistic preferences; each rule
> closes a documented decay-of-the-decay-tool.

## 1. Evidence Gate (anti-fabrication)

Every Critical and Warning finding **must** carry one of the following before it
is allowed into the report:

- File path + line range (`path/to/file.py:127-145`)
- Inline diff snippet (≥ 3 lines)
- Command + observable output (`pytest tests/x.py::test_y` + first error line)

If the assistant cannot point to a concrete artifact, the finding does not exist.

**Rationale.** Brooks-lint vocabulary (Iron Law, atomic write, INTENT/OUTCOME,
staged-verification, R1–R6, T1–T6) sounds authoritative even when no real work
was done. A plausible-looking but artifact-free report is *worse* than no
report — it pollutes downstream truth (vault, PR comments, post-mortems) with
fiction that the same vocabulary will validate next time.

Documented incident (this branch's reason for existing): on 2026-06-07 the
assistant produced a "Wave 2 #3-#10 fixes complete" report citing atomic writes,
chaos S1–S5, INTENT/OUTCOME journaling, and Telegram delivery verification.
None of it had run. The skill's own framing made the fabrication legible.

**Enforcement.** When writing the report:

1. For each Critical/Warning candidate, write the artifact reference first.
2. If the reference cell is blank, the finding is downgraded to a Suggestion or
   dropped.
3. Suggestions may be artifact-free (style nits, naming) but must explicitly say
   so (`scope: suggestion (no artifact required)`).

This rule does **not** weaken the Iron Law. Symptom → Source → Consequence →
Remedy is still required. Evidence Gate adds a fifth required field for the
heavy severities: **Artifact**.

## 2. Scope Refusal (don't review what doesn't decay)

Before applying the full R1–R6 / T1–T6 catalog, run a 3-question gate. If all
three are "no", **abort the review** with a one-line note. Do not template-fill
findings to look thorough.

```
Q1. Does this code persist state, mutate ledgers, or write evidence files?
Q2. Does this code touch external systems (orders, APIs, auth, cron, systemd)?
Q3. Will this code be re-run, imported, or maintained by anyone other than the
    current author within the next 30 days?
```

If `Q1=Q2=Q3=no` → output:

```markdown
# Brooks-Lint Review

**Mode:** <mode>
**Scope:** <scope>
**Verdict:** SCOPE_REFUSED — single-shot research/EDA script, no decay surface.

Brooks-lint is not the right tool here. Re-invoke if (a) the script will be
productionized, (b) artifacts will be cited as evidence, or (c) state/ledger
behavior is added.
```

**Rationale.** Throwaway backtests, one-shot data pulls, and exploratory
notebooks have no decay risk to review. Forcing the catalog onto them produces
noise findings ("magic number 0.30 in `target_vol_annual`") that drown the real
signal when a genuinely risky change is reviewed next.

**What still gets reviewed even on research code:**

- Scripts that write to `obsidian-vault/` or other canonical truth stores
- Scripts whose output is cited in a thesis, PR, or post-mortem
- Scripts that mutate any file outside their own results directory
- Scripts that call live trading APIs even in "research mode"

These all answer "yes" to Q1 or Q2 and proceed normally.

## 3. Light Mode (the missing middle gear)

Most reviews are not full audits and not pure throwaways. For medium-risk
changes — adding a watcher, tweaking a cron parameter, modifying a config field
that is read but not written by hot paths — use Light Mode instead of the full
catalog.

**Trigger Light Mode** when the change:

- Touches < 50 lines
- Does not modify state schemas, identity keys, or atomic-write paths
- Does not change power graph (who can submit orders / restart services / write
  ledgers)

**Light Mode output (3 questions, max 1 paragraph each):**

```markdown
# Brooks-Lint Review (Light Mode)

**Scope:** <files>
**Mode:** Light

**Invariant.** <what this change is supposed to keep true>

**Single point of failure.** <the one thing most likely to break and the
specific symptom you'd see>

**Verification.** <command to run + expected output that proves the invariant
holds>
```

If any of the three answers is "I don't know yet", **escalate to full Mode**
before reporting.

**Rationale.** The full R1–R6 / T1–T6 catalog is calibrated for architectural
review. Running it against a 30-line cron tweak produces 5+ findings that are
all either irrelevant (R4 Speculative Generality on a one-off) or already
constrained by the surrounding system. Light Mode keeps the review proportional
to the change.

## Loading Order

These three rules **augment** common.md, they do not replace it. Loading order
inside each skill mode:

1. `_shared/common.md` — Iron Law, project config, report template, severity
2. `_shared/chris-improvements.md` — *this file*: Evidence Gate, Scope Refusal,
   Light Mode
3. `_shared/decay-risks.md` (or `test-decay-risks.md`) — risk catalog
4. mode-specific guide (`pr-review-guide.md`, `audit-guide.md`, etc.)

Where a rule from this file conflicts with common.md, **this file wins** — it
is the more recent learning. Where they agree, this file is silent.
