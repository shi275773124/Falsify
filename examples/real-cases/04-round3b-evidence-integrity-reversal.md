# Real case: a statistical PASS reversed by evidence-integrity checks

> Public-safe reconstruction of a 2026-07 audit. Strategy, venue, host, and account details are omitted. The failure shape, observed outputs, and gate requirements come from the canonical records listed below.

## Share card

| | |
|--|--|
| **Apparent green** | Saved returns passed DSR, PBO, permutation (headline SR ~3.95) |
| **Real failure** | Implicit missing-data policy shaped the matrix; coverage collapsed variants |
| **Authority / Falsify** | Calendar contract, row-loss audit, coverage manifest, missing-policy variants before metrics |
| **Verdict** | Statistical PASS withdrawn → **BLOCK** / no live authority |
| **Public URL** | https://falsify.site/examples/real-cases/04-round3b-evidence-integrity-reversal |

All three cards: [SHARE-CARDS.md](./SHARE-CARDS.md) · Install gate: [GitHub Action share pack](../../docs/github-action-share-pack.md)

## Apparent green

A strict quant run reported `PASS` after testing a saved returns matrix. On the main 264-day window, the `combined_missing_zero` variant reported SR `3.9503`, DSR `0.9017`, PBO `0.1540`, and permutation p-value `0.000`.

The green result answered whether the supplied matrix looked statistically strong. It did not prove that the matrix preserved the full calendar or handled missing upstream features safely.

## Actual failure

A read-only full-calendar attack varied the missing-feature policy:

| Variant | DSR | Permutation p | Historical label |
|---|---:|---:|---|
| `combined_missing_zero` | 0.9017 | 0.000 | `PASS` |
| `combined_missing_neutral` | 0.5208 | 0.009 | `RESEARCH_ONLY` |
| `combined_premium_available_only` | 0.3435 | 0.037 | `RESEARCH_ONLY` |
| `premium_available_only` | 0.1616 | 0.104 | `RESEARCH_ONLY` |

Feature coverage on that window averaged `80.36%` and fell as low as `36.11%`. The headline survived only when missing values were implicitly treated as zero. The audit therefore returned `BLOCK`; the old PASS could no longer support promotion, scaling, scheduling, or order changes.

`RESEARCH_ONLY` above is a historical claim-ceiling label, not a current core verdict. Under the current vocabulary this case is `BLOCK`, with the historical ceiling normalized to `DIAGNOSTIC_ONLY / NO_LIVE_AUTHORITY`.

## Why the old gate missed it

The gate checked DSR, PBO, and permutation evidence after returns had already been produced. It did not require:

- a full-calendar contract;
- a row-loss audit;
- a feature-coverage manifest;
- explicit missing-value policy variants; or
- provenance from feature availability to saved returns.

That allowed `dropna()` alignment and implicit zero-fill policy to alter the evidence surface before statistical checks ran.

## Falsify requirement

Before DSR/PBO/permutation, Quant Falsify must receive machine-inspectable:

```text
calendar_contract
row_loss_audit
coverage_manifest
variant_policy
claim_ceiling
```

A missing item is a blocking evidence-integrity defect. Supplying all items is necessary but not sufficient: after the runner was wired to emit them, evidence-integrity passed while the overall verdict remained `BLOCK` because missing-policy robustness and live-authority evidence were still insufficient.

## Verdict and claim ceiling

- Current normalized verdict: `BLOCK`
- Supported claim: the original statistical PASS depended on an unsafe missing-data policy and was correctly withdrawn as authority evidence.
- Claim ceiling: `DIAGNOSTIC_ONLY / NO_LIVE_AUTHORITY`
- Not supported: that the strategy had no research signal, or that evidence-integrity checks alone authorize live use.

## Machine-checkable provenance

```yaml
provenance_schema: falsify.real_case.sources.v1
case_id: round3b-evidence-integrity-reversal-20260703
source_snapshot_date: 2026-07-10
sources:
  - id: canonical_change_record
    public_locator: "private-vault:change-record/2026-07-03-round3b-evidence-integrity-hotfix"
    source_title: "2026-07-03 XS-Momo Round3b data falsify and Falsify evidence-integrity hotfix"
    sha256: "f265a8e706e340a8c2f173ab6f985f671ae90068e6f49038459b260657e21ea4"
    anchors: ["VERDICT = BLOCK", "combined_missing_zero", "L0.5 Evidence integrity gate"]
  - id: current_falsify_truth
    public_locator: "private-vault:current-truth/falsify"
    source_title: "Falsify current truth"
    sha256: "2a677fa5123e681713a8d2589d78ec332e29430b0ae4019ea48cf7d09a6665f4"
    anchors: ["Falsify evidence-integrity hotfix", "old strict PASS no longer authority evidence"]
  - id: current_backtest_contract_truth
    public_locator: "private-vault:current-truth/backtest-machine-contract"
    source_title: "Backtest machine contract current truth"
    sha256: "4a5d4ebcd8dfbc32cfa44ba2a48b594d50af5f6d0d17b9dd614644c19d38f4c5"
    anchors: ["full-calendar premium coverage attack", "VERDICT = BLOCK"]
artifacts_named_by_sources:
  - "round3b_data_falsify_20260703/REPORT.md"
  - "round3b_data_falsify_20260703/summary.csv"
  - "round3b_data_falsify_20260703/manifest.json"
```
