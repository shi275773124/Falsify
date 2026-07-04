# 18. Pro vs OSS

[Back to README](../README.md) · [Open Core boundary](./12-open-core-boundary.md) · [Skills](./17-skills.md)

One-page map of what ships on GitHub (MIT), what stays in the closed Pro skill/runtime, and what Team sells as a workspace product. Use this when linking from the README, footer, or onboarding — not as a pitch deck.

## Three layers

| Layer | What it is | Source / delivery | You pay for |
|---|---|---|---|
| **OSS (MIT)** | Protocol, CLI, five workflow packs, templates, examples | [GitHub](https://github.com/shi275773124/Falsify) — self-host, BYOK | Nothing (your model keys) |
| **Pro (closed source)** | Umbrella Falsify skill + Production enforcement + fixture library updates | Private canonical (your private skill directory) — not a full public copy | Skill/runtime updates, incident antibody library, Production cutline enforcement |
| **Team (paid product)** | Org governance, retention, integrations, rollout | Hosted or contracted workspace path — spec in [Team edition](./13-team-edition-spec.md) | Seats / workspace fee (BYOK hybrid per [business model](./10-team-delivery-and-business-model.md)) |

**Naming:** Pro ≠ Team. Pro is the umbrella skill stack and Production gate discipline. Team is the paid workspace product (policy at org scale, artifact history, integrations) — see [docs/13](./13-team-edition-spec.md).

## OSS inventory (GitHub, MIT)

Matches [Open Core boundary](./12-open-core-boundary.md):

- **Protocol** — `PASS / PASS_WITH_DEBT / BLOCK`, Cutline (`Must Fix / Known Debt / Delete`), `falsify.review.v1` JSON schema
- **CLI** — `falsify lint`, `falsify review --json`, `falsify demo`
- **GitHub / CI** — workflow template, BYOK execution, JSON + Markdown artifacts
- **Policy** — `.falsify/policy.yml` base fields
- **Reporting** — local/CI artifacts only
- **Integrations** — examples and webhook patterns (not production-grade connectors)
- **Five workflow packs (v0)** — deployment-claim, live-production-gate, ai-pr-review, research-report, agent-safety-check ([skills index](./17-skills.md))
- **Templates + examples** — including anonymized incident pattern [`examples/real-cases/02-derived-freshness-stale-panel.md`](../examples/real-cases/02-derived-freshness-stale-panel.md)

## Pro inventory (closed source)

Not published as a full copy on GitHub. Canonical lives in the private umbrella skill and vault Hermes runtime; only a **subset** is exported to OSS (see below).

Pro adds what OSS templates describe but do not fully enforce on their own:

| Capability | What Pro owns |
|---|---|
| **Daily vs Production hard boundary** | Daily health / ops checks are not Production sign-off. Production Falsify requires dual-model or delegated audit for live-money claims — not self-Falsify by the same agent that authored the fix |
| **Incident → fixture → gate** | Real incident failure shape becomes a permanent red sample; future closure must show RED→GREEN through the **production runner** entrypoint (not a test stub that never reaches the order path) |
| **Negative fixtures** | Minimum coverage set (derived freshness false-green, missing coverage, fail-close markers, signer/account mismatch, synthetic non-NOOP branch) maintained as a living library |
| **Input provenance manifest** | Independent manifest gate: source names, freshness boundary, min/max timestamps, coverage, missing/stale list |
| **Replacement semantics** | Data-source / field / window / metric swaps require old-vs-new diff or explicit strategy-change registration |
| **Hermes integration** | Skill manifest + runtime hooks so scheduled/live executors run the same Production rules the human audit used |
| **Delegated / self-Falsify discipline** | Explicit cutline: same-agent sign-off on high-stakes claims is `PASS_WITH_DEBT` at best unless a second authority path is recorded |

Rule IDs visible in the exported OSS pack (e.g. `FALSIFY_INCIDENT_REPLAY_V1`, `FALSIFY_LIVE_NEGATIVE_FIXTURE_V1`) name the gates; Pro owns **enforcement depth**, fixture corpus, and update cadence.

## Export policy (one-way sync)

```text
canonical (private umbrella + vault runtime)
        │
        │  one-way export — reviewed subset only
        ▼
OSS  skills/falsify-live-production-gate/
```

- **Canonical** = private umbrella skill + private runtime
- **Export target** = [`skills/falsify-live-production-gate/`](../skills/falsify-live-production-gate/) only (not the other four packs from Pro internals)
- **Direction** = Pro → OSS only; OSS PRs do not become the source of truth for Production enforcement

**Export denylist** — never ship to OSS GitHub:

| Deny | Why |
|---|---|
| Full umbrella `SKILL.md` workflow graph | Pro orchestration across Daily + Production + domain packs |
| Complete negative-fixture corpus + PM/vault fixture paths | Incident antibody library is the paid update surface |
| Hermes runtime manifest, scheduler hooks, executor wiring | Live loop integration |
| Production-only cutline tables and dual-model audit contracts | Enforcement updates, not protocol |
| Customer/vault-specific incident docs, host paths, account boundaries | Privacy + non-anonymized operational truth |
| Delegated-audit runtime enforcement (who may sign Production PASS) | Trust model, not schema |

OSS may keep **anonymized pattern docs** and **rule ID names** so builders understand the gates; denylist items stay out of the public repo even when rule names appear in exported skill text.

## Moat (honest)

What Pro is **not** claiming:

- Exclusive cross-vendor lock-in — Falsify territory is **decision gates for defensible sign-off**, not owning your broker, CI, or model provider (whitepaper §9)

What Pro **does** sell:

- **Territory** — Production Falsify as a distinct hard boundary from Daily ops (whitepaper §10)
- **Incident antibody library** — each real incident becomes a permanent fixture that must replay through the production path (whitepaper §13: incident → fixture → gate)
- **Enforcement updates** — cutline tightening and fixture coverage as new failure classes appear, synced from canonical to the OSS export subset

Moat = updates + library + live loop discipline — not merely hiding files that are already fully described in public markdown.

## Team path (separate from Pro)

Pro is skill/runtime depth for operators who run Production Falsify locally or in vault.

Team is the **workspace product** for engineering orgs:

- **Now:** Audit Sprint on one high-risk artifact, or 4–8 week Design Partner pilot ([business model](./10-team-delivery-and-business-model.md))
- **Team MVP order (strict):** PR comment + check → stable JSON/MD artifacts → `policy.yml` enforcement → artifact history → single integration → dashboard last ([Team spec](./13-team-edition-spec.md))

Team does not replace Pro; it adds org rollout, retention, and integrations Pro does not host in the OSS repo.

## Known debt

| Item | Status |
|---|---|
| Open-core business model conversion | **Unverified** — OSS ships today; dbt/Vault-style analogies are not proof Team will convert ([docs/12 Known Debt](./12-open-core-boundary.md#known-debt--open-core-business-model)) |
| OSS `falsify-live-production-gate` scope | **Planned P1** — second-bot review: public pack may narrow to Daily/partial Production pattern docs; full four-gate enforcement stays Pro-only until export policy is re-cut |
| Physical repo split (`falsify` + `falsify-team`) | Deferred until design-partner stability + versioned API boundaries ([docs/12](./12-open-core-boundary.md#trigger-to-revisit-physical-repo-split)) |

## Related links

- [12. Open Core boundary](./12-open-core-boundary.md) — field-by-field OSS vs paid (Team) reservation
- [17. Skills](./17-skills.md) — five MIT workflow packs
- [10. Team delivery & business model](./10-team-delivery-and-business-model.md) — Audit Sprint / Design Partner / pricing shapes
- [13. Team edition spec](./13-team-edition-spec.md) — Team MVP order and quality bars
- [Real case: derived freshness stale panel](../examples/real-cases/02-derived-freshness-stale-panel.md) — anonymized Production Falsify pattern
