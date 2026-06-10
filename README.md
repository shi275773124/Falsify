# Falsify

> **Your unfair advantage: two top AIs from different vendors cross-examine your work — you keep only what survives.**
> **No API key.** Point the AI subscriptions you already pay for (Claude, ChatGPT/Codex, Gemini) at one shared folder and let them audit each other. Falsify is the neutral referee — it reviews the *judgment*, not just the diff, and the referee isn't owned by either contestant.

[![falsify](https://github.com/shi275773124/Falsify/actions/workflows/falsify.yml/badge.svg)](https://github.com/shi275773124/Falsify/actions/workflows/falsify.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![中文](https://img.shields.io/badge/lang-中文-red.svg)](./README.zh-CN.md)

[中文版](./README.zh-CN.md) · [Setup](./docs/02-setup.md) · [Layer 1 · Peer Review](./docs/03-collaboration.md) · [Layer 2 · Adversarial Review](./docs/05-adversarial-review.md)

<p align="center">
  <img src="./assets/flow-card.png" alt="Falsify: Agent A drafts → Agent B audits → conflict → first-hand sources arbitrate → Git evidence trail → ship" width="820">
</p>

> 🙏 Thanks to **Hermes Agent**, **Claude Code**, and **Codex** — the tooling this workflow was built and tested on.

---

A single AI writes it; you have to verify it. **Falsify makes a second, different top model take its work apart** — wrong numbers and unsupported conclusions get caught before they reach your eyes. One drafts, one audits, Git keeps the evidence trail.

<p align="center">
  <img src="./assets/demo.gif" alt="falsify review run: the Skeptic catches 4+ issues, returns Verdict: HOLD" width="760">
</p>

> A real run: a DeepSeek model as the Skeptic audits a draft, catches every seeded error, returns `Verdict: HOLD`. Verbatim transcript: [examples/.../06](./examples/comparison-case-study/06-real-review-deepseek.md).

---

## Why it's worth it

- **Less effort** — one round of work, a report two top minds already vetted.
- **1 + 1 > 2** — two different models check each other; one's blind spot is the other's catch.
- **Provable trust** — it really catches errors a single model would have shipped (below).

---

## Real case: a Sharpe 4.06 strategy, killed before it reached real money

A single AI produced a quant strategy that passed everything — `Sharpe 4.06–4.31`, `PBO 0.000`, `DSR p < 1e-7`, 6 of 7 audit gates. The next step in the workflow was a small **live test with real money**.

Falsify forced a second model (a different vendor) to re-audit it adversarially. Five rounds later it was reclassified `NOT_VIABLE`: the Sharpe wasn't alpha — it was trading cost amortized over a holding period the strategy's own design never actually held (assumed ~14 days, real ~1.5 days → **cost understated ~9×**). Spread the cost correctly and the edge vanishes.

Along the way the reviewer caught **itself** three times — asserting a cause, re-running the numbers, then retracting when the data disagreed. A model auditing its own work defends what it wrote; an independent one re-derives and walks itself back.

> Why it takes two vendors: when the author and reviewer are the same model, `PBO=0` and `DSR p<1e-7` only prove the result is consistent *with its own assumption* — not that the assumption is real. A reviewer with different blind spots is the only thing that questions the assumption itself.

**→ Full sanitized audit log, numbers verbatim:** [examples/real-cases/01](./examples/real-cases/01-fictional-horizon-quant-audit.md)

<details>
<summary>Also — 4 pricing errors caught in a ~12-venue comparison (reproducible transcript)</summary>

Two independent agents (different models) ran a horizontal comparison of ~12 competing venues, 80+ cited URLs, in under 30 minutes. Agent B caught 4 critical pricing errors that would have shipped:

| Caught | Single agent | After dual-agent review |
|---|---|---|
| Venue A fee copied from a peer | Wrong by 2×, looks complete | B flags, resolves against docs |
| Venue B VIP0 maker sign flipped | Rebate written as a charge | B re-checks fee schedule |
| Venue C premium tier "not public" | Actually in the docs | B verifies, marks conflict |
| Venue D base fee wrong row | Wrong row in the table | B audits, requires source |

Verbatim transcript: [examples/.../06](./examples/comparison-case-study/06-real-review-deepseek.md)

</details>

---

## Two ways to run it

**① Vault mode — zero API key.** Point two agent apps you're already logged into (Claude Code, Codex, Gemini CLI…) at one Git-synced folder. They draft and audit each other through it; you arbitrate the conflicts. No key, no per-token cost — it rides the subscriptions you already pay for.

1. **Fork [`demo-vault/`](./demo-vault/)** — a Git-synced folder pre-wired with the rules. (Open it in Obsidian for a nicer reader — not required.)
2. **Edit `research/00-brief.md`** (topic + 1–3 questions), then point two agents at the folder, one as `AGENT-A`, one as `AGENT-B`. Both read [`AGENTS.md`](./demo-vault/AGENTS.md) on startup — that's what makes them tag, not overwrite, and send conflicts to first-hand sources.
3. **Stay hands-off** while they draft → audit → flag `[CONFLICT]`s. Arbitrate against first-hand sources, ship the `[BOTH]` report. Git keeps the evidence trail.

> Different vendors on purpose: one model's blind spot is the other's catch — and neither one owns the referee.

**② CLI mode — one command.** Automated and scriptable, exit code straight into CI. Key-free if you want it: `-p claude` (also `codex` / `gemini` / `hermes`, or any agent via `FALSIFY_<NAME>_CMD`) routes through an agent CLI you're already logged into — no key, rides your subscription. Or bring a provider API key:

```bash
pip install -e .                       # or just python falsify.py
export DEEPSEEK_API_KEY=sk-...         # or OPENAI_API_KEY / OPENROUTER_API_KEY…
falsify review report.md -p deepseek   # a second model audits it -> Verdict (PROCEED/HOLD/ARCHIVE)
falsify run brief.md --drafter claude --reviewer deepseek   # draft with one model, audit with another
```

`run` is the full loop. Use `--drafter/--reviewer` (plus optional `--drafter-model/--reviewer-model`) to preserve the core Falsify rule: author and reviewer should be independent. If both roles resolve to the same effective endpoint + model (or the same agent CLI command), the CLI warns that independence is weakened.

`-p` is a provider preset (deepseek / openai / openrouter / moonshot / siliconflow / local) that fills in the endpoint and model — **you only supply the key**. Tired of typing it? `falsify init` saves it once, then just `falsify review report.md`; or `cat report.md | falsify review -` to paste-and-go.

`review`'s **exit code is the Verdict** (`PROCEED=0 / HOLD=1 / ARCHIVE=2`) — drop it straight into CI. Falsify treats the reviewed draft as untrusted evidence: draft text is delimited in the review prompt, and the CLI parses the **last** `VERDICT:` line from the reviewer output so a `VERDICT:` embedded in the draft cannot silently pass the gate.

No key handy? `falsify lint <file>` runs a pure-local ship-blocker check (no API):

```bash
falsify lint examples/comparison-case-study/05-final-excerpt.md   # → SHIPPABLE
```

---

## Two layers

- **[Layer 1 · Peer Review](./docs/03-collaboration.md)** — catches **wrong numbers** (cheap, default): tag every paragraph, don't overwrite the other agent, conflicts go to first-hand sources.
- **[Layer 2 · Adversarial Review](./docs/05-adversarial-review.md)** — catches **wrong conclusions** (high-stakes): verdict ladder (`PROCEED/HOLD-N/ARCHIVE`) + multi-round + G1–G4 gates + cross-model independence.

| | Layer 1 | Layer 2 |
|---|---|---|
| Catches | wrong facts | right facts + wrong conclusion |
| In one line | "is this number right?" | "what makes this conclusion hold?" |

---

## What else is in here

- [`web/`](./web/) — browser paste-and-go POC: one box, one button → Verdict + top risks (`python web/serve.py`)
- [`templates/`](./templates/) — ready to use: `AGENTS.md`, three prompts, kickoff/retro, conflict/resolution logs, CI template
- [`demo-vault/`](./demo-vault/) — forkable empty workspace; edit `00-brief.md` and go
- [`examples/comparison-case-study/`](./examples/comparison-case-study/) — sanitized end-to-end sample + one real run
- [`examples/cases/`](./examples/cases/) — cross-industry case library (tech selection / market research / …), each proving "without Falsify, this error ships"
- [`docs/`](./docs/) — [architecture](./docs/01-architecture.md) · [setup](./docs/02-setup.md) · [Layer 1](./docs/03-collaboration.md) · [Layer 2](./docs/05-adversarial-review.md) · [troubleshooting](./docs/04-troubleshooting.md)

---

## Roadmap

- [x] CLI engine `falsify` (lint / review / verdict gate)
- [x] One-click: provider presets (`-p deepseek`) / `.falsify` config / paste-and-go
- [x] Web paste-and-go POC ([`web/`](./web/))
- [x] GitHub Action: block a PR that doesn't pass the verdict ([template](./templates/github-action-falsify.yml))
- [x] Forkable demo vault · sanitized case · flow card · real-run GIF
- [x] Cross-industry case library, started ([`examples/cases/`](./examples/cases/)): tech selection / market research
- [ ] Hosted web: 3 free runs, no key (paste-and-go, zero install)
- [ ] Chrome extension: one-click Falsify on ChatGPT / Claude / Gemini
- [ ] More industry cases: legal / medical / product / academic

## Contributing

Welcome: new scenario templates, sanitized case studies, sharper prompts, more agent-runner examples, translations. Fork → small focused change → PR (name the pain you're solving). Open an Issue to discuss first.

---

## License

MIT — fork it, ship it, write a blog post about it.

<details>
<summary>Support</summary>

- 🐦 [@aishikejian](https://x.com/aishikejian) · ☕ [Buy me a coffee](https://buymeacoffee.com/chris168) · ⭐ Star it

</details>
