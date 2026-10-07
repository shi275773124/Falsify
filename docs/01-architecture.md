# 01. Architecture

[中文](./01-architecture.zh-CN.md) · [Back to README](../README.md)

## Product definition (single source of truth)

**Falsify is an evidence-driven decision gate.**

It tries to **disprove** high-risk claims made by AI or humans, then emits a **scoped** verdict (`PASS`, `PASS_WITH_DEBT`, or `BLOCK`) from:

- an explicit **authority path** (what system/state is final),
- **raw artifacts** (not summaries alone),
- and an explicit **policy version**.

Multi-model / multi-agent review is an **optional attacker**, never the trust root.

> Models may propose charges. They may not manufacture facts. Hard `BLOCK` should prefer deterministic policy, missing evidence, or verifiable state conflict.

**Current public MVP surface:** GitHub workflows that gate **claims surrounding a change** (PR narrative, deploy plan, decision docs)—not “full automatic verification of every cloud deployment.”

## The problem

AI systems report completion with confident prose:

- CI green, logs complete, “another AI reviewed it”
- yet the target state never changed
- or the evidence surface was already biased before the metric gates ran

Code review and lint ask: *does the diff look right?*  
Falsify asks: *is this claim defensible against the authority path?*

## The gate pattern (public core)

One inspectable loop:

1. **Frame** — name the claim, owner, authority path, and claim ceiling  
2. **L0 Brooks-Lint (Framework)** — structural decay / auditability surface before adversarial attack (marketing alias:「框架审计」; protocol name is Brooks-Lint)  
3. **Attack** — seek the cheapest counterproof (deterministic checks first)  
4. **Recompute / re-read** — hit the real state, calculation, command, or raw source  
5. **Cutline** — Must Fix / Known Debt / Delete (includes L0 structural Must Fix)  
6. **Receipt** — preserve verdict, evidence path, policy/tool versions, freshness limits, and a **`brooks_lint` block** proving L0 ran (or was explicitly scope-refused / skipped with hard cap)

`PASS` is not permanent. Receipts expire when environment, artifacts, policy, freshness, or authority path change. Claim-bearing `review` / `run` without L0 proof cannot yield `PASS` / `PASS_WITH_DEBT`.

**Not the same tool:** `falsify lint` is a **markdown tag/blocker static check** (L2 gate path). It is **not** Brooks-Lint. See [Brooks-Lint](./09-brooks-lint.md).

## What multi-agent review is (and is not)

Historically this repo also documented a **two-agent drafting pattern** (Agent A writes, Agent B audits into a shared Obsidian vault over git). That pattern remains a **useful collaboration adapter** for research write-ups.

It is **not** the product’s root of trust:

| Role | Trust? |
|------|--------|
| Deterministic probes + policy | Yes — primary |
| Raw artifact hashes / authority reads | Yes — primary |
| Second model / second agent | Optional attacker only |
| “Two models rarely share the same error” | **Not claimed** — unmeasured slogans were removed |

If both agents agree on a false assumption, the gate still fails unless the authority path is checked.

## Optional topology: shared vault collaboration

```
            ┌──────────────────────────────────┐
            │   GitHub repo (private)           │
            │   = single source of truth        │
            └──────────────────────────────────┘
              ▲          ▲           ▲
       git push│   git push│   Obsidian Git
              │          │           │
       ┌──────┴──┐  ┌────┴────┐  ┌───┴────────┐
       │ Agent A │  │ Agent B │  │ Your laptop │
       │ (draft) │  │ (attack)│  │ human read  │
       └─────────┘  └─────────┘  └─────────────┘
```

Three writers can share one truth for research. The **gate** still bottoms out in authority path + artifacts + policy—not in agent consensus.

## Why git + plain markdown still matter

| Concern | Why it helps the gate |
|---------|------------------------|
| Diffable history | Receipts and claims are reviewable |
| Author identity | Provenance for who asserted what |
| Local-first vault | Human can open the same files agents attacked |
| GitHub Action surface | Where the MVP ships first |

## Failure modes the gate targets

- **Logs ≠ state** — “deploy succeeded” with unchanged target  
- **Derived freshness** — today’s signal timestamp over stale inputs  
- **Mirror drift** — docs/runtime disagree  
- **Metric theater** — gates run after an already-shaped evidence surface  
- **Opinion stacking** — second AI agreement treated as evidence  

## Related docs

- [Getting Started](./00-getting-started.md)
- [Brooks-Lint (L0 Framework)](./09-brooks-lint.md)
- [GitHub Action install](./14-github-action-install.md)
- [Adversarial Review](./05-adversarial-review.md) (L1 attacker layer)
- [Cutline / 风险裁刀](./06-risk-scalpel.md)
- [Skills packs](./17-skills.md)
- [Open Core boundary](./12-open-core-boundary.md)
