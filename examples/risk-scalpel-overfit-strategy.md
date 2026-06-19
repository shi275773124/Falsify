<!-- Illustrative Risk Scalpel decision. Sanitized, generic — no real entity.
     Shows how Layer 3 cuts existing review findings into Must Fix / Known Debt /
     Delete and issues a Final Cut. The findings are assumed to come from Layer 1 /
     Layer 2 (or any review); Risk Scalpel does not generate them, it decides. -->

# Risk Scalpel example: high Sharpe, low trust

A research write-up claims a trading strategy with a backtested **Sharpe ≈ 4.0** —
on paper, strong enough to promote. Peer Review (Layer 1) and Adversarial Review
(Layer 2) have already run and surfaced a pile of findings. The temptation now is to
treat every finding as a TODO and start "fixing" — building dashboards, wiring up
automation, planning a paper-trading rollout.

That is exactly the scope explosion Risk Scalpel exists to stop. The job here is not
to find more — it is to **decide**: of what was found, what must be fixed now, what is
real-but-not-blocking debt, and what should simply be deleted from the current scope.

> **Risk facts stay. Current scope gets cut.**

---

## What the earlier layers found

- The Sharpe is computed over many overlapping windows; the **effective independent
  sample is small** — far fewer truly independent observations than the headline N.
- **Robustness was never demonstrated**: no parameter-perturbation, no sub-period
  stability check, results may hinge on a handful of windows.
- The reported metrics come from the **same data the strategy was specified on** —
  there is **no post-specification (out-of-sample) validation**.
- A plan already exists to build a monitoring dashboard, automate execution, and
  promote to paper trading — i.e. **engineering that would manufacture false
  confidence** in a number that has not yet earned trust.

---

# Risk Scalpel Decision

## Object

A research note proposing a high-Sharpe strategy as ready to advance.

## Findings Source

- [x] Peer Review (Layer 1)
- [x] Adversarial Review (Layer 2)

## Must Fix

Change it now, or the headline number is a **false truth** that drives a real
decision. Without these, every downstream claim inherits an unvalidated edge.

| Finding | Failure mode | Why now | Acceptance |
|---|---|---|---|
| Effective independent sample unknown | False precision — Sharpe rests on far fewer independent points than claimed | Every further claim multiplies the error | Compute and report N_eff; restate confidence against it |
| Robustness never shown | Edge may be a few lucky windows | Can't tell signal from artifact until tested | Run parameter-perturbation + sub-period stability; result survives or the claim is withdrawn |
| No post-specification validation | In-sample fit dressed up as a result | Promotion on in-sample numbers is the core trap | Freeze the spec, validate on untouched out-of-sample data before any further claim |

## Known Debt

Real, but it does **not** block the current phase — and it is gated behind the Must
Fix work, so it carries an explicit upgrade trigger.

| Finding | Real risk | Why not now | Upgrade trigger |
|---|---|---|---|
| Reporting / monitoring is thin | Hard to track the strategy later | Better reporting on an unvalidated edge just makes a wrong number prettier | Build it **after** statistical validity is established (Must Fix cleared) |

## Delete

No current failure mode. These only add completeness, polish, or premature
engineering — and worse, they manufacture confidence the evidence hasn't earned. Cut
them from this phase.

| Finding | Why delete |
|---|---|
| Automated execution pipeline | Premature automation of an unproven edge |
| Promotion to paper / production trading | No validated edge to deploy; deployment is not a research step |
| Cosmetic charts / dashboard polish | Aesthetics that imply a trust the number does not have |

## Final Cut

Can the current phase proceed?

**Verdict: BLOCK** — for any deployment or promotion.

The strategy is **not deleted as an idea** — the *risk facts* (a high in-sample Sharpe
worth investigating) stay on the books. What gets cut is the *current action*: it is
allowed to continue **only as research-only follow-up**, behind the three Must Fix
gates. If, and only if, N_eff is defined, robustness holds, and an out-of-sample run
survives, this becomes **PASS_WITH_CONDITIONS** for a small, reversible next step —
never a straight PASS off the back of the in-sample number.

> The single-model failure here is not "missing a bug." It is treating a stack of
> findings as a to-do list and engineering around an unvalidated edge. Risk Scalpel's
> only move is the cut: **fix the validity, hold the debt, delete the theater.**
