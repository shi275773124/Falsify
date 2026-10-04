# Audit Power: How We Measure the Auditor

> An auditor that cannot be attacked cannot be trusted. This page documents how the private Falsify engine measures its own audit capability — with reproducible harnesses, not adjectives.

## Why "audit power"

Most audit tools make a claim: *"it catches problems."* The claim is rarely measured. A gate that has never been attacked is indistinguishable from a dead gate — it may be green simply because nothing ever tried to get past it.

Falsify's private engine treats the auditor itself as a system under test. Capability is expressed as three measurable agents, each with a named harness and reproducible receipts:

| Agent | Measures | Harness |
|---|---|---|
| **MKR** — Mutation Kill Rate | Whether injected evidence tampering gets caught | `audit_power_probe.py` (R/D/E layers, 16 mutation operators) |
| **CHR** — Canary Hit Rate | Whether the auditor detects miscalibration, not just bad data | `canary_harness.py` (5 rounds, 15 injections) |
| **ACR** — Adversarial Capture Rate | Whether LLM red-team artifacts get blocked | `redteam_corpus_builder.py` (52-artifact corpus, 32 attack classes) |

## Current measured numbers (2026-10-02)

These figures come from the private engine's harness-generated receipts. They are observations, not guarantees; the harnesses evolve weekly and every engine change re-runs them.

- **MKR 16/16 = 100%** — 16 classes of injected evidence tampering (wrong numbers, truncated data, stale panels, forged summaries, date shifts, coverage gaps) all caught, zero survivors. Each mutation class is a real attack shape recovered from production incidents or red-team rounds.
- **CHR 15/15 = 100%** — 5 calibration rounds, 15 canary injections, all flagged. The canary layer specifically tests whether the auditor notices when *calibration itself* is faked — "headline without recomputation" is treated as structurally unauditable.
- **Red-team corpus: 52 artifacts, 0 penetrations** — an adversarial LLM generated attack artifacts across 32 classes (including provenance rewrites, latency-audit replay overwrites, filename escapes, claim/data decoupling). Every one was caught; weekly cron keeps evolving new attack classes.
- **Independent audit rounds: 6 consecutive BLOCK→fix→PASS before v0.9.40** — engine changes do not ship on author self-test. A non-author auditor attacks each change; v0.9.37 alone took five BLOCK rounds (anchored-registry poisoning, TOCTOU write races, relative-namespace splits) before passing.

## The discipline behind the numbers

Four principles were burned in during those six audit rounds:

1. **Exemption ≠ verification.** A skipped check proves nothing. Missing evidence fails closed.
2. **Collection surface must close.** A check that can be silently skipped is worse than no check.
3. **Undeclared is fraud.** If a capability is not declared, claiming it is a finding — not marketing.
4. **Fail-closed must not misfire.** 107 real directories run clean through the same guards that kill the 52 attack artifacts.

## Where this runs

The full engine — mutation probes, canary calibration, red-team corpus, sealed-candidate admission, HMAC-signed authority — runs in production on a live quant desk where a wrong PASS costs real money. The public repository ships the review layer (CLI, GitHub Action, DeepSeek plugin) with bounded epistemic verdicts; the measured audit-power stack above is available through Audit Sprint and design-partner engagements.

## Reproduce the shape

The public sample receipt shows the verdict format these gates emit:

```bash
curl -sS https://falsify.site/examples/sample-block-report.json | python -m json.tool
```

## Boundary

Figures on this page describe the private engine's measured audit power. They are not a claim that any public artifact passes those gates, and no PASS here authorizes deployment, trading, or capital movement. Sign-off only.
