# Case: logs green, live revision is not the claimed commit

**Replay fixtures. This path does not call production.**
`falsify demo` only inspects the text you pass it. A `PASS` here means the local rules did not find a known false-green pattern in that file — not that any server was checked.

## What to give Falsify

| Input | File |
|---|---|
| Claim that treats logs as proof, and claimed ≠ observed revision | [`claim-false.md`](./claim-false.md) |
| Same kind of claim, with matching probe evidence | [`claim-true.md`](./claim-true.md) |

## Preconditions

- Python 3.12+
- From the repository root: `python -m pip install -e ".[dev]"`
- No API key. `demo` is local and deterministic.

## Commands

False sample — expected `BLOCK` (exit 1):

```bash
python -m falsify demo examples/deployment-revision-mismatch/claim-false.md
```

True sample — expected `PASS` (exit 0):

```bash
python -m falsify demo examples/deployment-revision-mismatch/claim-true.md
```

Bundled default (same failure class as the false sample):

```bash
python -m falsify demo
```

## Expected findings (false sample)

At least:

- logs treated as state verification
- claimed commit ≠ observed production revision
- second-model agreement treated as proof
- missing probe metadata

Cutline: Must Fix. Verdict: `BLOCK`.
Authority ceiling stays `EPISTEMIC_ONLY` / capital `NONE`.

## Expected findings (true sample)

No Must Fix from the local demo rules. Verdict: `PASS`.
That PASS is still epistemic: it does not authorize a deploy.

## Swap in your own input

1. Write a short claim file (markdown or plain text).
2. Attach the raw evidence you actually have: probe output, HTTP status, observed revision, rollback command.
3. Run `python -m falsify demo path/to/your-claim.md`.
4. If you need a model to attack the prose, that is a different command: `python -m falsify review path/to/your-claim.md --provider <name>` (BYOK). Missing provider configuration fails closed; it does not print PASS.

## What this does not do

- It does not GET your production API.
- GitHub Action in this repo lints **changed Markdown decision docs**, not application code.
- Quant / live enforcement stays in the private Pro runtime.
