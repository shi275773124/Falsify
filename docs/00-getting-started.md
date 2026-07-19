# Getting Started

Falsify is a local, BYOK review toolchain for stopping **false green**: a change, report, or deployment that looks complete but cannot show the evidence needed to trust it.

Start with one decision that matters. Falsify does not host your review data, guess your source of truth, or make a decision for you. It helps you challenge the claim, record what was checked, and keep the resulting artifact beside your work.

## The false-green problem

A PR says: "The migration is deployed, CI is green, and the reviewer agrees." That can still be unsafe:

- CI may have tested the wrong environment.
- A successful log is not proof that the target state changed.
- A model agreeing with another model is not evidence.

Give Falsify the claim and the evidence you have. A `BLOCK` is useful output: it tells you which proof is missing before the claim ships.

## What you can do today

- run a deterministic local demo without any key;
- review a file through your own model provider or a locally logged-in agent CLI;
- use the local Web Console to submit a review;
- add the GitHub Action template to a repository and retain JSON/Markdown report artifacts.

There is no hosted Falsify organization console, shared receipt store, or managed gateway in this repository. Your files, provider configuration, and artifacts remain under your control.

## 1. Install

```bash
git clone https://github.com/shi275773124/Falsify.git
cd Falsify
python -m pip install -e ".[dev]"
```

The package installs the `falsify` command. If your shell does not find it, use `python -m falsify` in the commands below.

## 2. See a real false green — no key required

```bash
falsify demo
```

The demo uses a bundled fixture and deterministic local checks. It makes no network or model call. Its expected result is a `BLOCK`, because the fixture treats logs as proof of state:

```text
[AGENT-B audit] logs are treated as state verification
Cutline: Must Fix
VERDICT: BLOCK
```

This is a safe first success: the tool caught a claim that sounded finished but lacked state evidence.

## 3. Configure a provider for a live review — your key required

A live review needs either a provider key that you control or a compatible agent CLI that is already authenticated on your machine. Falsify does not issue an API key.

For a DeepSeek-compatible setup:

```bash
export DEEPSEEK_API_KEY=sk-...
falsify review report.md --provider deepseek --json
```

The `--json` result is designed for automation and artifact retention. You can also use a locally authenticated CLI provider:

```bash
falsify review report.md --provider claude --json
# or: codex, gemini, hermes
```

Do not put provider keys in a document, commit, or shell history you intend to share. See [Local use and BYOK](./11-byok-and-policy.md) for configuration boundaries.

## 4. Read the verdict in plain language

| Verdict | What it means now | What to do |
|---|---|---|
| `PASS` | The supplied evidence supports this scoped claim; no current blocker was found. | Keep the artifact and state the scope. It is not a permanent guarantee. |
| `PASS_WITH_DEBT` | The claim can proceed, but a real limitation is recorded with a concrete condition for revisiting it. | Track that condition; do not treat debt as an ignored warning. |
| `BLOCK` | Evidence is missing, a blocking finding remains, or the result cannot be audited. | Add the missing evidence or narrow the claim, then review again. |

Terms such as "Must Fix," "Known Debt," and "Cutline" are the finding labels behind those outcomes. You do not need to learn the protocol before your first review; use [Understand verdicts](./01-architecture.md) when you need the deeper model.

Every receipt also carries `claim_scope` and `authority_ceiling`. An OSS receipt is `EPISTEMIC_ONLY` with `capital_authority: NONE`: it records what was proven for the scoped claim and never authorizes a payment, deploy, or other live action. An action-bearing `PASS` additionally requires an authority adapter and the unified kernel.

## 5. Keep the artifact with the decision

For a file review, save the machine-readable result in the repository or your decision folder:

```bash
mkdir -p artifacts
falsify review report.md --provider deepseek --json > artifacts/falsify-review.json
```

Keep the reviewed input, command context, and JSON result together. The artifact records what this one review saw; it does not automatically watch future changes or read any external authority system for you.

For pull requests, the included template generates both `falsify-report.json` and `falsify-report.md` and uploads them as GitHub Actions artifacts.

## 6. Open the local Web Console

```bash
python web/serve.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The console is served from your machine. Its review panel uses the provider configuration available to that local process; without a provider/key it returns a setup error instead of pretending that a review ran.

## 7. Add a PR gate when ready

Copy the [GitHub Action template](./14-github-action-install.md) into the repository you want to protect. Start in advisory mode with narrow Markdown globs. Add your BYOK secret only when you want model-backed review, then make the check required after you have verified its behavior on real PRs.

## Next

- [Use Falsify locally](./11-byok-and-policy.md)
- [Add Falsify to CI](./14-github-action-install.md)
- [Understand verdicts](./01-architecture.md)
- [CLI and artifact reference](./20-cli-and-artifacts.md)
