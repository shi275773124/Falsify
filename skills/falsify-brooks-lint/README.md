# Brooks-Lint (L0 Framework)

Structural / auditability review pack — Falsify’s **L0 Framework** layer (marketing alias:「框架审计」; protocol name: **Brooks-Lint**).

Surfaces decay that weakens evidence: hidden state, implicit authority, duplicated control paths, brittle rollback, unverifiable acceptance, and catalog risks from the vendored references (including **chris-improvements**: Evidence Gate, Scope Refusal, Light Mode).

## Claiming Falsify requires CLI authority exit

```text
Installing or reading this pack ≠ Claiming Falsify.
```

This pack defines **what to attack at L0**. It does **not** replace the product CLI.

| Exit | Command |
|------|---------|
| Default claim-bearing review (L0 then L1) | `python -m falsify review …` |
| L0-only | `python -m falsify brooks <path>` |
| Local demo | `python -m falsify demo` |
| Quant (optional) | `python -m falsify.quant_gate …` with `pip install falsify[quant]` |

Keep the command line + exit code / JSON artifact. Receipts for claim-bearing review must include a **`brooks_lint`** block proving L0 ran (`RAN` or `SCOPE_REFUSED`). Explicit skip cannot yield claim-bearing `PASS`.

**Not Brooks-Lint:** `python -m falsify lint` — markdown tag/blocker static check only (L2 gate path).

See `docs/09-brooks-lint.md`, `docs/01-architecture.md`, and `docs/ROOTFIX-architecture.md` §6.1.

## Use

1. Read `SKILL.md` as the workflow contract.
2. Load `references/` in the order listed in `SKILL.md` (always include `chris-improvements.md`).
3. Optionally fill a claim/diff into a short brief (same spirit as other packs’ `templates/input.md`).
4. Return JSON matching `templates/verdict.schema.json` (optional `layer: "brooks_lint"`).
5. For product sign-off, run the CLI authority exit above and retain the receipt.

## Provenance

| Field | Value |
|-------|--------|
| upstream | `hyhmrright/brooks-lint` |
| fork_branch | `chris-improvements` |
| source_sha | `6be92af94839175665c35df77390e7baab78a303` |
| local_fork | `/home/ubuntu/brooks-lint-fork` (pin time) |
| references_source | Hermes pack `brooks-lint-review/references/` + fork chris-improvements content |

This directory is the **product source of truth** for Brooks-Lint in Falsify. Agent hosts (Hermes, Cursor, Claude Code) should install/copy from here rather than maintaining a divergent private tree.

## Layout

```text
falsify-brooks-lint/
  SKILL.md
  README.md
  references/          # common, decay-risks, chris-improvements, …
  templates/
    verdict.schema.json
```

## Related

- [Architecture](../../docs/01-architecture.md)
- [Brooks-Lint doc](../../docs/09-brooks-lint.md)
- [Skills index](../README.md)
