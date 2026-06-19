# Risk Scalpel Decision

> The post-review **decision** step. It does not generate more findings — it takes
> the findings you already have and cuts each one into **Must Fix / Known Debt /
> Delete**, then issues a Final Cut on the current phase.
>
> **Risk facts stay; current scope gets cut.**

## Object

<!-- What was reviewed (the report / PR / strategy / design under decision). -->

## Findings Source

<!-- Where the findings came from. Risk Scalpel is source-agnostic. -->

- [ ] Peer Review (Layer 1)
- [ ] Adversarial Review (Layer 2)
- [ ] Brooks-Lint / code-decay
- [ ] Incident review
- [ ] Research robustness
- [ ] Live-truth / permission-boundary
- [ ] Other:

## Must Fix

<!-- Change it now, or it creates false truth, false risk, silent failure, a
     permission breach, non-reproducibility, or broken current-phase verification. -->

| Finding | Failure mode | Why now | Acceptance (how we know it's fixed) |
|---|---|---|---|
|  |  |  |  |

## Known Debt

<!-- Real risk, but it does not block this phase. MUST carry an upgrade trigger —
     the concrete condition that promotes it to Must Fix. -->

| Finding | Real risk | Why not now | Upgrade trigger |
|---|---|---|---|
|  |  |  |  |

## Delete

<!-- No current failure mode. Only completeness, aesthetics, platformization,
     premature abstraction, or engineering noise. Cut it from the current scope. -->

| Finding | Why delete |
|---|---|
|  |  |

## Final Cut

<!-- Can the current phase proceed? -->

**Verdict:** <!-- PASS | PASS_WITH_CONDITIONS | BLOCK -->

- **PASS** — no Must Fix open.
- **PASS_WITH_CONDITIONS** — proceeds only with the listed Must Fix done / Known Debt accepted.
- **BLOCK** — at least one Must Fix is open and unmitigated.

Conditions / notes:
