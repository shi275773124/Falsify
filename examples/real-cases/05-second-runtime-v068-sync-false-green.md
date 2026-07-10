# Real case: a fixed mirror produced a runtime sync false-green

> Public-safe reconstruction of a 2026-07 audit. Host and private filesystem prefixes are omitted. Version facts, tests, and acceptance outputs come from the canonical records listed below.

## Apparent green

The versioned vault mirror contained the v0.6.8 log-return basis fix. Inspecting that mirror could therefore suggest the second profile was ready to use the corrected quant path.

That was not deployment evidence. The executable second-profile runtime was a separate tree.

## Actual failure

Direct inspection found split state:

```text
vault mirror: v0.6.8 basis logic present
actual runtime: old implementation
runtime skill metadata: version 0.6.7
```

The real runtime lacked `ret_log` preference, `_ReturnsArray` metadata propagation, and `return_basis` output. The v0.6.8 mirror was an orphan artifact: correct code existed, but not where execution loaded it.

Under the current verdict vocabulary, pre-fix status normalizes to `BLOCK` because runtime provenance and deployment parity were not proven. A clean mirror is not `PASS` for a runtime claim.

## Falsify requirement

For every runtime/mirror sync claim:

1. Resolve and inspect the actual executable runtime path.
2. Compare runtime and mirror content and declared version.
3. Run the same focused fixtures in both trees.
4. Require the fixture to exercise the corrected semantic contract, not only syntax.
5. Bound PASS to the tested runtime behavior; do not inherit strategy or live authority.

The focused regression used a dual-column CSV containing both `ret_log` and `ret_simple`. It required:

- `ret_log` to be selected;
- `return_basis='log'` to be attached;
- copy/slice operations to preserve that metadata; and
- computed statistics to report `return_basis='log'`.

## Closure evidence

After synchronizing the actual runtime and setting its metadata to v0.6.8:

```text
runtime direct fixtures: 78 passed, 0 failed
runtime pytest wrapper:   2 passed, 3 warnings
mirror pytest wrapper:    2 passed, 3 warnings
```

The warnings were recorded as pre-existing numerical-library warnings and were not blockers for this scoped fix.

## Verdict and claim ceiling

- Pre-fix normalized verdict: `BLOCK`
- Post-fix scoped verdict: `PASS` for v0.6.8 `ret_log`/`ret_simple` basis handling in the second runtime
- Supported claim: mirror/runtime parity must be verified at the executable path, with semantic fixtures in both trees.
- Claim ceiling: runtime basis handling only; no strategy verdict, live action, order, schedule, or scaling authority.

## Machine-checkable provenance

```yaml
provenance_schema: falsify.real_case.sources.v1
case_id: second-runtime-v068-sync-false-green-20260701
source_snapshot_date: 2026-07-10
sources:
  - id: canonical_change_record
    public_locator: "private-vault:change-record/2026-07-01-second-runtime-falsify-v068-sync"
    source_title: "2026-07-01 second runtime Falsify v0.6.8 sync"
    sha256: "ca3b194f4c0ba2597a492d179ad3dda95aea3299844e87709e357fd537ab60c0"
    anchors: ["sync false green / orphan artifact", "78 passed, 0 failed", "version: 0.6.8"]
  - id: current_falsify_truth
    public_locator: "private-vault:current-truth/falsify"
    source_title: "Falsify current truth"
    sha256: "2a677fa5123e681713a8d2589d78ec332e29430b0ae4019ea48cf7d09a6665f4"
    anchors: ["Second runtime quant Falsify sync false-green CLOSED", "dual-column CSV fixture"]
runtime_surfaces:
  - "second-profile executable Falsify runtime"
  - "vault runtime mirror for second profile"
focused_acceptance:
  direct_fixture: "78 passed, 0 failed"
  runtime_pytest: "2 passed, 3 warnings"
  mirror_pytest: "2 passed, 3 warnings"
```
