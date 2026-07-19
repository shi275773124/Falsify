# Real case: derived freshness false-green on a scheduled live executor

> Anonymized from a 2026-06 production incident. Venue, account, host, and
> strategy names are sanitized; failure shape and Falsify gates are real.

## Share card

| | |
|--|--|
| **Apparent green** | Cron OK, today's signal timestamp, executor `--verify` PASS |
| **Real failure** | Underlying panel CSVs stopped updating weeks earlier |
| **Authority / Falsify** | Refresh + coverage before signal; incident replay via real production wrapper; provenance manifest |
| **Verdict** | Derived freshness false-green → **BLOCK** until gates close |
| **Public URL** | https://falsify.site/examples/real-cases/02-derived-freshness-stale-panel |

All three cards: [SHARE-CARDS.md](./SHARE-CARDS.md) · Install gate: [GitHub Action share pack](../../docs/github-action-share-pack.md)

## TL;DR

A daily scheduled momentum bot looked healthy:

```text
cron last_status = ok
signal_state.ts = today
executor --verify = PASS
```

Underlying daily panel CSVs had **stopped updating weeks earlier**. The signal
layer appended today's prices on stale history, producing a **fresh derived
artifact over stale upstream data** — classic **derived freshness false-green**.

Live orders continued until manual intervention. Post-incident Falsify closed
only after:

1. Panel refresh + coverage gate before signal generation
2. **FALSIFY_INCIDENT_REPLAY_V1** permanent red sample through the production wrapper
3. **Input provenance manifest** listing upstream min dates and coverage
4. Drawdown oracle seeded from historical equity (eliminating bootstrap 0% DD false green)

## Failure shape

```text
fresh/new derived signal artifact
+ stale underlying panel/CSV
+ live wrapper or scheduler-context dry-run
= must fail-close before signer/order construction
```

## What partial Falsify looked like

- Audit prose: "watch for stale data"
- Verify PASS on current account snapshot
- No stale CSV routed through the same cron wrapper entrypoint

That is **partial Falsify**, not Production PASS.

## Negative fixture contract

The permanent regression sample must enter via the **real production runner**
(cron shell wrapper), with only fixture input/env swapped:

| Field | Example (sanitized) |
|-------|------------------------|
| `fixture_id` | `stale_panel_incident_replay_v1` |
| `authority_path` | daily auto rebalance wrapper |
| `production_entrypoint` | `wrapper.sh → refresh → signal → executor --verify` |
| `mode` | dry-run / no-submit |
| `expected failure gate` | `STALE_PANEL_COVERAGE` or refresh fail-close |
| `assertion` | exit != 0 before fix; exit 0 after guard |

A unit test that mocks the executor and fails by construction is useful but
**not** full Falsify evidence.

## Input provenance manifest (minimal)

Machine-readable JSON alongside derived artifacts:

```json
{
  "sources": [
    {
      "name": "daily_panel_csvs",
      "expected_freshness": "min_last>=yesterday_utc",
      "min_last": "2026-06-28",
      "coverage_count": 66,
      "stale_symbols": []
    }
  ],
  "generated_at_utc": "2026-06-29T11:53:29Z"
}
```

Derived freshness alone is not evidence. A new `signal_state` timestamp
does not prove panel CSVs refreshed.

## Skill pack

Open-core workflow: [`skills/falsify-live-production-gate/`](../../skills/falsify-live-production-gate/SKILL.md)

Rule IDs: `FALSIFY_LIVE_NEGATIVE_FIXTURE_V1`, `FALSIFY_INCIDENT_REPLAY_V1`,
input provenance manifest gate, replacement semantics gate.

## Outcome

- Rootfix: refresh-before-signal + fail-close on stale coverage
- Incident replay: fixture PASS archived with UTC timestamp and exit code
- Live restore: separate gate from data rootfix; requires explicit authorization
- Remaining debt: structural book beta, metric replacement registered as strategy change

See also: [fictional-horizon quant audit](./01-fictional-horizon-quant-audit.md) for research-side Falsify.
