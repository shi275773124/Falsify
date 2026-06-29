# Production Falsify Audit Brief — XS-Momo A Incident Closure Loop

> Scope: **Production Falsify** (live money context). Dual-model required.
> Date: 2026-06-29
> incident_id: `xsmomo-a-stale-panel-20260629`

## Claim Under Audit

The XS-Momo A stale-panel incident loop is **institutionally closed**:

1. Canonical incident doc exists and matches vault truth
2. Incident Closure Index row is accurate (fixture paths, rule IDs, oracle JSON, wikilinks)
3. OSS Falsify repo syncs with vault/runtime falsify skill (no fork drift on rule IDs)
4. Must Fix items from 2026-06-29 production Falsify are closed with machine evidence

**NOT claiming**: live restore re-authorization, RISK_FREEZE lift, or strategy promotion.

## Deliverables to Falsify

| # | Artifact | Path |
|---|----------|------|
| D1 | Canonical incident doc | vault `事故记录/2026-06-29 XS-Momo A stale panel fresh-signal-over-stale-data事故.md` |
| D2 | Incident Closure Index | vault `事故记录/00-incident-closure-index.md` |
| D3 | OSS skill pack + example | Falsify repo `skills/falsify-live-production-gate/`, `examples/real-cases/02-derived-freshness-stale-panel.md`, `docs/17-skills.md` |
| D4 | Must Fix closure record | vault `变更记录/2026-06-29-falsify-mustfix-closure.md` |

## Claims to Attack

### C1 — Incident doc completeness
- Root cause class = derived freshness false-green (not executor outage)
- Timeline includes panel stop ≤2026-05-30, incident surface 2026-06-29, rootfix, Chris-authorized restore
- Rollback command present and specific (backup dir + files)
- Must Fix table cites fixture PASS with UTC + exit code
- Oracle DD references real JSON (not bootstrap 0% false green)
- Known debt explicitly separated from Must Fix (RISK_FREEZE, P0a strategy change, structural beta)

### C2 — Closure Index accuracy
- Row `xsmomo-a-stale-panel-20260629` matches D1 incident_id
- Rule IDs: `FALSIFY_INCIDENT_REPLAY_V1`, `FALSIFY_LIVE_NEGATIVE_FIXTURE_V1`, input provenance manifest, replacement semantics
- Fixture path + last PASS: PM `tests/test_stale_panel_fixture.py` 2026-06-29T11:54Z exit 0
- Oracle pointer: `drawdown_report.json` with `FAIL_MATERIAL_DD`, peak 9548.74U, DD ~-9.15%
- All wikilinks resolve to existing vault files

### C3 — OSS / vault skill sync
- OSS `falsify-live-production-gate` encodes same four rule IDs as vault `hermes-skills-runtime/default/falsify/SKILL.md`
- Public example `02-derived-freshness-stale-panel.md` has no venue secrets
- `docs/17-skills.md` lists live production gate pack

### C4 — Evidence not prose
- P0a: `STRATEGY_CHANGE` not equivalence — artifact at vault `当前真相/审计/xsmomo-a/latest/p0a_volume_metric_diff.json`
- Input manifest: vault `当前真相/审计/xsmomo-a/latest/input_provenance_manifest.json` with min_last, coverage
- Panel refresh: vault `当前真相/审计/xsmomo-a/latest/panel_refresh_report.json`
- Oracle: vault `当前真相/审计/live-drawdown-oracle/latest/drawdown_report.json` exit 1, prior_peak seeded

## Required Evidence (machine)

| Gate | Required | BLOCK if missing |
|------|----------|------------------|
| Rollback | Specific backup path + restore command in D1 | Yes |
| Wikilinks | All `[[...]]` in D1/D2 resolve | Yes |
| Rule ID sync | All 4 rule IDs in D1, D2, OSS skill, vault skill | Yes |
| Fixture PASS | UTC timestamp + exit 0 cited; not re-run required in this audit if vault record consistent | Yes if claim contradicts closure record |
| Oracle | `drawdown_pct` non-zero, `peak_equity` seeded, `verdict=FAIL_MATERIAL_DD` | Yes if bootstrap 0% claimed |
| OSS example | File exists, anonymized | Yes |

## Cutline (Production)

**BLOCK** if any:
- Incident doc missing rollback section
- Broken wikilinks in D1 or D2
- OSS/vault rule ID mismatch on the four production gates
- Must Fix claimed closed without artifact pointer
- Closure index row missing or contradicts canonical doc
- Derived freshness fix claimed without incident replay rule ID present

**PASS_WITH_DEBT** if:
- Documentation/index/skill sync complete
- Must Fix evidence pointers valid locally
- Known debt documented with upgrade triggers
- BUT: fixture PASS not re-verified on PM this session, or dual-model audit incomplete, or RISK_FREEZE still active

**PASS** only if:
- All BLOCK conditions cleared
- Independent dual-model review completed
- Evidence artifacts exist and match claims [local verify OK]

## Known Debt (pre-declared, not Must Fix for doc closure)

- RISK_FREEZE still active — restore ≠ freeze lift
- P0a live still on old metric — strategy change registered, not faithful replacement
- D-line dust/ledger semantics open
- fact_sheet.json mtime 2026-05-30 approaching STALE_FACT_SHEET boundary
- Scheduler-context dry-run not re-run in this audit session

## Output Required

Standard Falsify verdict shape:
`Verdict` / `Brooks-Lint` / `Adversarial` / `Cutline` / `Must Fix` / `Known Debt` / `Delete` / `Final`
