# 18. Immutable Anchor Redesign — 拨乱反正

**Date:** 2026-07-28
**Trigger:** R3 + D 双策略同日因 immutable manifest hash mismatch 被 cron BLOCK。R3 经人工 rebind 后 04:19 UTC 恢复；D 仍 BLOCK。
**Method:** Self-Falsify (Brooks-Lint → Adversarial Review → Cutline) applied to the production gate implementation, not just the protocol docs.

---

## 1. What broke, and what didn't

### The design philosophy is sound

Brooks-Lint, Adversarial Review, and Cutline / 风险裁刀 — the three layers described in `docs/09`, `docs/05`, `docs/06` — are **not the problem**. The problem is how they were **implemented in the live trading gate**, not how they were **designed in the docs**.

### What actually broke (three independent failures)

| # | Failure | Evidence | Layer it violates |
|---|---|---|---|
| **F1** | **Byte-hash as immutability anchor** — `IMMUTABLE_MANIFEST.json` pins SHA256 of file bytes. A comment or whitespace change breaks the manifest. | D today: 5 files SHA256_MISMATCH, none of them logic changes. `py_compile: PASS` on all 5 — the code is valid, only bytes drifted. | Brooks-Lint: "passing tests that do not cover the decision" + G4 ruler/object match |
| **F2** | **Self-referential verifier bootstrapping** — `verify_immutable_manifest.py` is itself a file in the manifest's `files[]`. When it changes, it hash-mismatches itself. The code has a `--bootstrap-verifier-selfhash` escape hatch, but the bootstrap receipt is signed by `verifier_selfhash_rebind_bootstrap.py`, which is **not** in the manifest — so the trust chain root floats. | `verify_immutable_manifest.py:400-438` — `_SELFHASH_BOOTSTRAP_BASENAMES` + `_gate_report_is_bootstrap`. The verifier's own hash is verified by... a script that isn't verified. | Adversarial Review: GLOSSOPETRAE "prompt-only audit theater" — the immutability proof bottoms out at an unverified file |
| **F3** | **Quant gate made advisory (audit theater)** — `r3_falsify_production_change_gate.py` runs `quant_falsify_gate.py` (PBO, deflated Sharpe, walk-forward) but its result does **not** participate in the PASS/FAIL verdict. | `r3_falsify_production_change_gate.py:344-347`: `quant_advisory = quant['ok']` then `verdict = 'PASS'` only checks `rc, lot, shell` — **quant is never in the condition**. Comment admits: "S1 hard-wiring caused rebind deadlock." | Adversarial Review: the adversarial layer was neutered to make the system operational. This is "monitor failure laundering" — the gate runs, produces a verdict, but the verdict is cosmetic. |

### What did NOT break

- **R3 rebalance logic** — once the manifest was re-pinned, all 12 legs submitted, `POST_LIVE_POSITION_CHECK=PASS`, `RESIDUAL_USD=0.00`. The strategy itself is healthy.
- **D preflight** — `preflight_verify_20260728T040135Z.log` shows `PASS_DRYRUN`, all guards green. The strategy is healthy; only the release gate is broken.
- **The release runner** — `run_from_current.sh` correctly refused to exec a release-tree file whose SHA256SUMS entry didn't match (exit 15). The integrity gate **worked as designed** — it caught the corruption. The problem is upstream: the corruption should never have reached the release tree.

---

## 2. Root cause: the immutability anchor is wrong

### Current design (broken)

```
worktree files ──sha256──> IMMUTABLE_MANIFEST.json
                              │
                              ▼
                     verify_immutable_manifest.py
                              │
                              ▼
                     cron ──> run_from_current.sh
                              │
                              ▼
                     out/releases/current/tree/<file>
                              │
                              ▼
                     SHA256SUMS cross-check
```

**Why it breaks:**

1. **Byte-hash ≠ logic-hash.** SHA256 of file bytes catches any change — including comments, whitespace, formatting. The business question is "did the strategy logic change?" not "did any byte change?" This is the G4 failure (ruler/object match): the tool's assumption (byte-identity = logic-identity) does not fit the data (code where comments are not logic).

2. **The verifier is self-referential.** `verify_immutable_manifest.py` pins its own hash. When it changes, it cannot verify itself. The `--bootstrap-verifier-selfhash` workaround moves the trust to an external script that is itself unverified — the chain root floats.

3. **The release tree is not actually immutable.** `materialize_release.py` copies files into `out/releases/<id>/tree/` but does not make them read-only. Today's D incident: someone edited `tree/xsmomo_d_daily_auto.sh` in place (mtime 07-27 15:51, after the 07-26 17:14 release). The SHA256SUMS caught it at cron time (exit 15), but the corruption was silent for ~12 hours.

4. **Three duplicated pipelines.** `momo-d/`, `momo-r3/`, `b-stab-gate/` each carry their own copy of `verify_immutable_manifest.py`, `materialize_release.py`, `release_rebind_authority.py`, `*_production_change_gate.py`. Logic drifts. A fix in one is not automatically a fix in the others. Today: R3 was fixed by rebind; D was not, because the operator worked on R3's copy.

### Correct design (proposed)

```
git commit SHA ──> RELEASE_ANCHOR.json (just the commit SHA + strategy_id)
                       │
                       ▼
              verify_release_anchor.py
              (git ls-tree <sha> vs release tree)
                       │
                       ▼
              cron ──> run_from_current.sh
                       │
                       ▼
              out/releases/<commit-sha>/
                = git archive <commit-sha> (read-only tar or checkout)
```

**Why this is correct:**

1. **Git commit SHA is the natural immutability unit.** A commit captures the exact tree state. Comments/whitespace changes produce a new commit = new release. Logic changes also produce a new commit = new release. No false positives, no false negatives. The ruler matches the object.

2. **No self-referential paradox.** `verify_release_anchor.py` is part of the commit. Its hash is implicitly the commit hash. No need for a `--bootstrap-verifier-selfhash` escape hatch — the verifier is verified by being in the commit, not by being in a manifest that it itself verifies.

3. **Release tree = `git archive` output.** A tarball or a `git checkout --detach <sha>` into a read-only directory. Editing a file in a git-detached-HEAD checkout is possible but detectable via `git status`. Better: ship a `.tar.gz` and verify its hash, never extract into a mutable tree.

4. **One shared library.** `release_lib.py` in a shared location (e.g. `/home/ubuntu/.hermes/skills/automation/falsify/scripts/release_lib.py`), versioned by the commit. Each strategy's manifest shrinks to: strategy_id + commit SHA + cron bindings + strategy-specific files list.

---

## 3. The authority chain is self-signed (and that's a Known Debt, not a Must Fix)

### Current authority chain

```
FALSIFY_SIGNING_KEY_PATH (local file on the VPS)
    │
    ▼
release_rebind_authority.py (HMAC-SHA256 over token fields)
    │
    ▼
RELEASE_REBIND_AUTHORITY.json (token)
    │
    ▼
verify_immutable_manifest.py --write-current (consumes token, re-pins manifest)
```

**Observation:** The signing key is a local file on the same VPS that runs the gate. Anyone with shell access can sign a token. The HMAC proves "someone with the key ran the gate," but since the key is co-located, it does not prove **independent** authority.

This is **not a Must Fix** for the current phase. The threat model is: an operator accidentally editing files out-of-band (today's incident), not a malicious insider forging tokens. The authority chain as built is sufficient for accidental-corruption prevention.

**Cutline classification: Known Debt.**
- Why not blocking now: the system runs on a single VPS with a small operator set; the threat is drift, not malice.
- Upgrade trigger: becomes Must Fix when a second operator or automated CI can trigger rebinds, or when the VPS is shared with non-trading workloads.

---

## 4. Cutline table

| # | Finding | Failure mode if unfixed | Class | Minimal action | Upgrade trigger |
|---|---|---|---|---|---|
| F1 | Byte-hash anchor | False-positive BLOCK on non-logic changes; today's incident | **Must Fix** | Replace with git-commit-SHA anchor | — |
| F2 | Self-referential verifier | Trust chain root floats; bootstrap is audit theater | **Must Fix** | Verifier anchored by commit, removed from manifest files[] | — |
| F3 | Quant gate advisory | Adversarial layer runs but cannot block; audit theater | **Must Fix** | Either make it hard-FAIL (fix backtest to PASS) or remove it and record as Known Debt. Do not leave a gate that looks binding but isn't. | Hard-FAIL when backtest reaches PASS_TO_PAPER/PASS |
| F4 | Release tree mutable | Files editable in place; corruption silent until cron | **Must Fix** | `git archive` to `.tar.gz`; verify tar hash at cron, never extract to mutable tree | — |
| F5 | Three duplicated pipelines | Fix drift; one strategy fixed, others not | **Must Fix** | Shared `release_lib.py`; strategy manifests reference it by commit | — |
| F6 | Authority chain self-signed | No independent authority for rebind | **Known Debt** | Document; keep HMAC for tamper-evidence | Must Fix when multi-operator or CI-driven rebind |
| F7 | Watchdog JSON summaries replace raw evidence | Raw tx_hash/position readback buried under layers | **Known Debt** | Preserve raw evidence path in every gate report | Must Fix when a leg fails POST_LIVE_POSITION_CHECK |
| F8 | `py_compile` in manifest checks | Zero防护 for today's failure class; false sense of safety | **Delete** | Remove from manifest files[]; keep in CI only | — |
| F9 | `IMMUTABLE_MANIFEST.json` notes[] accumulation | 60/207 lines are history; git diff unreadable | **Delete** | Move notes to `RELEASE_HISTORY.jsonl`; manifest = current state only | — |

---

## 5. Migration plan (non-breaking, phased)

### Phase 1 — Anchor migration (this week)

**Goal:** Replace byte-hash anchor with git-commit anchor for one strategy (R3) as a pilot.

1. **Add `RELEASE_ANCHOR.json`** to `momo-r3/`:
   ```json
   {
     "schema": "release_anchor_v1",
     "strategy_id": "XS-Momo-R3-PIT-OHLCV-Only",
     "commit_sha": "<40-char git SHA>",
     "commit_sha_short": "<12-char>",
     "created_at_utc": "...",
     "cron_bindings": [ ... same as current manifest ... ],
     "continuity_dependencies": { ... same ... }
   }
   ```
   This file is **not** self-referential: `verify_release_anchor.py` is **not** listed in it.

2. **Write `verify_release_anchor.py`** (shared, in falsify skill scripts dir):
   - Read `RELEASE_ANCHOR.json`
   - `git ls-tree <commit_sha>` → expected tree
   - Compare against `out/releases/<commit_sha>/` contents
   - Verify cron bindings (same logic as current)
   - No self-hash. No bootstrap. The verifier is in the commit; the commit IS the anchor.

3. **Update `materialize_release.py`:**
   - `git archive <commit_sha> --prefix=momo-r3/ | gzip > out/releases/<commit_sha>.tar.gz`
   - Record tar.gz SHA256 in `RELEASE_ANCHOR.json`
   - `out/releases/current` → symlink to the **tarball**, not a mutable tree

4. **Update `run_from_current.sh`:**
   - Extract tarball to a tmp dir at run time (or verify in-place if read-only fs)
   - Verify tarball SHA256 against `RELEASE_ANCHOR.json` before exec
   - Exec from extracted dir

5. **Delete from manifest files[]:** `verify_immutable_manifest.py`, `pre_live_ci.py`, `make_release_artifact.py`, `materialize_release.py`, `promote_release.sh`, `verify_all.py` — these are **infrastructure**, not strategy. They belong to the commit, not to the strategy manifest.

### Phase 2 — Quant gate honesty (this week)

**Either:**
- **(a)** Make `quant_falsify_gate` result hard-FAIL the production gate (remove `quant_advisory` bypass). Requires the R3 backtest to reach `PASS_TO_PAPER` or `PASS`. If it can't, the gate stays BLOCK and the strategy does not rebind — which is the correct Falsify behavior.
- **(b)** If the backtest is known-not-passing and the strategy is still live by operator decision, **remove** `quant_falsify_gate()` from the production gate entirely and record as Known Debt: "Quant gate removed; strategy live by operator override. Upgrade trigger: re-add when backtest reaches PASS_TO_PAPER."

**Forbidden:** leaving the gate running but advisory. That is the audit theater the protocol was designed to prevent.

### Phase 3 — Dedup (next week)

1. Extract shared `release_lib.py` from the three copies of `verify_*`, `materialize_*`, `release_rebind_authority.py`.
2. Each strategy repo imports it; the strategy manifest pins only strategy-specific entry scripts.
3. A fix to the release library = one commit in one place = all three strategies pick it up on next release.

### Phase 4 — Release tree immutability (this week)

After `materialize_release.py` writes the tarball:
```bash
chmod 0444 out/releases/<commit_sha>.tar.gz
# Optional, if filesystem supports: chattr +i out/releases/<commit_sha>.tar.gz
```
The tarball is the artifact; the extracted tree is ephemeral. Never exec from a mutable extracted tree.

---

## 6. What this does NOT change

- **Cron schedule.** Unchanged. Hermes jobs.json stays the source of truth for cron.
- **Order logic.** The executor, the signal generator, the wrapper scripts — unchanged. Only the release/integrity layer changes.
- **Operator authority.** `release_rebind_authority.py` + `FALSIFY_SIGNING_KEY_PATH` stays as-is (Known Debt F6). The token format is unchanged; only the thing it authorizes changes (re-pinning `RELEASE_ANCHOR.json` instead of `IMMUTABLE_MANIFEST.json`).
- **Incident replay requirement.** `FALSIFY_INCIDENT_REPLAY_V1` stays. Today's incident becomes a permanent red sample: "release tree file edited in place → SHA256SUMS mismatch → cron BLOCK (exit 15)."

---

## 7. Self-Falsify boundary

This document is a **design proposal**, not an independent audit. The author (same agent/repo) cannot independently certify the fix. After implementation:

1. Run the new `verify_release_anchor.py` against a known-good commit → must PASS.
2. Tamper one file in the release tarball → must FAIL.
3. Tamper the `RELEASE_ANCHOR.json` commit SHA → must FAIL.
4. Run the production gate with the quant gate **hard-FAIL** (Phase 2a) → if the backtest is not PASS, the gate must BLOCK and no token is emitted.

Only after these four checks pass is the redesign ready for a live rebind.