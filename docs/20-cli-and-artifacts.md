# CLI & Artifact Reference

## Commands

| Command | Requires your key? | Use it for |
|---|---:|---|
| `falsify demo` | No | Confirm the local install with a deterministic false-green fixture. |
| `falsify lint FILE` | No | Check collaboration tags and ship-blocker conventions. |
| `falsify review FILE --provider NAME --json` | Yes, for provider-backed review | Produce a machine-readable verdict for one file. |
| `falsify run BRIEF --drafter NAME --reviewer NAME` | Usually | Run a draft-and-review loop; keep the author and reviewer contexts independent where possible. |
| `falsify init` | No | Write a local configuration template. |

A provider-backed review may use your provider API key or a locally authenticated compatible agent CLI. `demo` and `lint` do not call a model.

## Save a review

```bash
mkdir -p artifacts
falsify review report.md --provider deepseek --json > artifacts/falsify-review.json
```

Save the input, JSON, command/provider context, and any raw evidence used to support the claim. A result is evidence about one run over one input; it does not make a continuing guarantee.

## GitHub Action artifacts

The PR template writes and uploads:

- `falsify-report.json` for tools and downstream checks;
- `falsify-report.md` for people reading the PR;
- a PR summary comment when the workflow runs on a pull request.

Without `FALSIFY_API_KEY`, the template reports that live review was skipped and remains lint-only. That is an explicit advisory state, not a model verdict.

## Exit behavior

`PASS` and `PASS_WITH_DEBT` exit successfully; `BLOCK` exits non-zero. CI can use this behavior to fail a check, but make branch protection required only after observing the template on your own documents.
