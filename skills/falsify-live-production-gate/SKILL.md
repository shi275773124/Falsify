# falsify-live-production-gate

Production Falsify adapter for **live trading executors**, **scheduled order-capable jobs**, and **post-incident restore** claims.

Distilled from the 2026-06 derived-freshness / stale-panel incident class. Use anonymized patterns only in public artifacts — no venue accounts, private keys, or host paths in outputs.

## When To Use

Load when a claim involves:

- live money, cron/systemd, or order-capable automation;
- post-incident **rootfix** or **live restore**;
- stale data, derived freshness, or "monitor is green";
- input provenance for derived artifacts (`signal_state`, targets, dashboards, verify PASS).

## Core failure class: derived freshness false-green

```text
downstream artifact timestamp fresh
≠
upstream input data fresh
```

Example pattern (anonymized): new daily signal file + stale underlying panel/CSV → cron OK + verify PASS while live path should fail-close before signer/order construction.

## Required rule IDs (Production Falsify)

| Rule ID | Gate |
|---------|------|
| **FALSIFY_LIVE_NEGATIVE_FIXTURE_V1** | Negative fixtures through the **same production runner** cron/live uses — not a dedicated test stub that cannot reach the order path |
| **FALSIFY_INCIDENT_REPLAY_V1** | Real incident failure shape → permanent red sample → future Falsify shows RED→GREEN |
| **input provenance manifest** | Independent manifest: source names, freshness boundary, min/max timestamps, coverage count, missing/stale list, artifact mtime |
| **replacement semantics** | Data-source/field/window/metric swap needs old-vs-new diff or explicit strategy-change registration |

## Negative fixture minimum coverage

After stale-data or derived-freshness incidents, require replay evidence for:

1. **Derived freshness false-green** — fresh derived artifact + stale upstream panel/CSV → fail before signer/order.
2. **Missing source coverage** — truncated API, omitted symbol, empty response hidden by wrapper success.
3. **Paused / fail-close marker** — incident marker stops scheduled wrapper with readable reason.
4. **Signer / account mismatch** — wrong key, missing key, account id drift.
5. **Account-state mismatch** — orphan leg, open orders, missing target leg.
6. **Synthetic non-NOOP order branch** — force order-wire construction in no-submit mode when live state is naturally NOOP.

## Evidence artifact contract (replay fixture)

Each replay should leave machine-readable output containing:

- `fixture_id`, `incident_id` (or anonymized case ref)
- `authority_path`: cron/job/service/wrapper/executor
- `production_entrypoint`, `mode` (no-submit / dry-run / scheduler-context)
- input fixture paths and checksums
- expected failure gate, actual exit code
- stdout/stderr excerpt, report paths
- timestamp

## Inputs Required

- Claim text (rootfixed / live restore / scheduler enablement).
- Authority path: service, cron id, wrapper script, account boundary (sanitized in public reports).
- Raw artifacts: panel/signal timestamps, manifest, refresh report, account-state readback.
- Negative fixture command + last PASS/FAIL output with exit code and UTC time.
- Rollback command or backup path.
- For metric replacement: old-vs-new definition table + universe/target diff.

## Review Procedure

1. Frame claim, authority path, irreversible risk (orders, config, external send).
2. Attack **derived freshness**: do downstream greens prove upstream freshness?
3. Attack **replacement semantics**: is fresh data equivalent to correct data?
4. Require **incident replay** if this path had a real incident — no fixture → BLOCK rootfixed claims.
5. Require **input provenance manifest** for any derived live artifact.
6. Separate data/signal rootfix from live authority restore.
7. Assign Must Fix / Known Debt / Delete; return verdict schema only.

## Verdict Rules

- `PASS`: production runner negative fixtures fail on bad samples; manifest present; rollback exists; no blocker for the **specific claim scope**.
- `PASS_WITH_DEBT`: claim scope survives but debt has upgrade trigger (e.g. oracle bootstrap, attribution lag).
- `BLOCK`: missing negative fixture, missing manifest, fixture bypasses production runner, scheduler-context not proven, or unfixed derived-freshness path.

## BLOCK Conditions

- "Stale data is a risk" prose without stale sample failing through production runner.
- Incident class claimed fixed with no permanent red sample (`FALSIFY_INCIDENT_REPLAY_V1`).
- Derived artifact freshness treated as upstream freshness proof.
- Metric/source replacement without old-vs-new diff or strategy-change registration.
- Direct wrapper PASS but no scheduler-context dry-run for scheduled authority.
- Logs / verify PASS / cron OK treated as account-state or input-data proof.

## Output Format

Return JSON matching `templates/verdict.schema.json`.

## Public example

Anonymized case study: [`examples/real-cases/02-derived-freshness-stale-panel.md`](../../examples/real-cases/02-derived-freshness-stale-panel.md)

## Pitfalls

- Unit test that mocks the runner is not full Falsify evidence.
- Chris override of BLOCK does not erase the skipped gate — record override scope in debt.
- Bootstrap oracle with null peak → 0% drawdown is false green, not PASS.

## Minimal Action Examples

- Add stale-panel negative fixture routed through production wrapper; archive last PASS with exit code.
- Publish input provenance manifest next to signal/target artifacts.
- Register metric replacement as strategy change with diff artifact before faithful-restore claims.

## Commercial Upgrade Path

Move to Audit Sprint when one live executor controls material capital or customer-facing automation SLA.
