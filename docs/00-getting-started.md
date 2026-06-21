# Getting Started

Falsify is an adversarial review framework for AI-generated code, research, and production decisions.

It produces one of three decisions:

- `PASS`
- `PASS_WITH_DEBT`
- `BLOCK`

## Install

```bash
git clone https://github.com/shi275773124/Falsify.git
cd Falsify
python -m pip install -e .[dev]
```

## Run the local demo

The demo does not call a model. It runs deterministic local rules against a fixture and returns a real Falsify-style verdict.

```bash
python falsify.py demo
```

Expected shape:

```text
[AGENT-B audit] logs are treated as state verification
Cutline: Must Fix
VERDICT: BLOCK
```

## Review a file with a model

```bash
export DEEPSEEK_API_KEY=sk-...
python falsify.py review report.md --provider deepseek
```

You can also use a local agent CLI:

```bash
python falsify.py review report.md --provider claude
python falsify.py review report.md --provider codex
```

## Run the full loop

```bash
python falsify.py run brief.md --drafter claude --reviewer deepseek
```

Use independent author and reviewer contexts when possible. If both roles resolve to the same model or agent command, Falsify warns that independence is weakened.

## Start the local website

```bash
python web/serve.py
```

Open `http://127.0.0.1:8000`.

The homepage explains the framework. The reviewer panel calls the real configured backend and returns a setup error if no provider/key is available.

## Decision semantics

`PASS` means the current decision has enough evidence.

`PASS_WITH_DEBT` means no current blocker remains, but real Known Debt is recorded with a concrete upgrade trigger.

`BLOCK` means at least one Must Fix remains, current evidence is missing, or the audit result cannot be parsed.
