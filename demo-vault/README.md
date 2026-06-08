# Demo Vault — Agent Review Kit

A ready-to-run dual-agent research workspace. Fork it, edit one file, point two
agents at it, and go.

This is the [Agent Review Kit](https://github.com/shi275773124/Falsify)
protocol, pre-wired into an empty vault so you don't start from a blank page.

## Start in 4 steps

1. **Fork / copy** this `demo-vault/` into a private repo of your own.
2. **Edit [`research/00-brief.md`](./research/00-brief.md)** — the only file you
   must touch first. Set the topic, the 1–3 questions, scope, and division of labor.
3. **Point two agents at it**, one as `AGENT-A`, one as `AGENT-B`. Both read
   [`AGENTS.md`](./AGENTS.md) at startup. (Optional: also open the folder in
   Obsidian for human reading.)
4. **Stay hands-off** while they draft + audit. Then arbitrate the
   `[CONFLICT]` items and ship.

## What's here

```
demo-vault/
├── AGENTS.md                 the rules both agents read first
├── .gitignore                Obsidian-friendly ignores
├── inbox/
│   └── raw-links.md          drop unsorted links/leads here
├── research/
│   ├── 00-brief.md           ← edit this first (the task)
│   ├── 01-sources.md         graded source list (A/B/C/D)
│   ├── 02-agent-a-draft.md   Agent A writes here
│   ├── 03-agent-b-audit.md   Agent B audits here
│   ├── 04-conflicts.md       open disagreements
│   └── 05-resolutions.md     conflicts closed by first-hand sources
├── reports/
│   └── final-report.md       the shippable output (all [BOTH])
└── logs/
    ├── decisions.md          operator decisions
    └── changelog.md          what changed, when, by whom
```

## The whole loop in one line

> Agent A drafts → Agent B audits → disagreements become `[CONFLICT]` →
> first-hand sources arbitrate → `[BOTH]` → ship, with Git keeping the trail.

Full protocol, prompts, and templates:
[Agent Review Kit](https://github.com/shi275773124/Falsify).
