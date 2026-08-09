# Shared Agent Contract

This repository is shared by Cursor, Windows Grok, and Windows Codex. Optimize for throughput.

## Parallel by default

Research agents may continue independently with read-only inspection, public-data downloads, scripts, tests, artifacts, and frozen cheap falsifiers. Do not wait for another agent for these tasks. Claim a task only to prevent duplicate work on the same mechanism.

## Only four writes are serialized

Before changing any of these shared resources, read `state/coordination.json` and `docs/agent-control-plane.md`, then use `python tools/agent_coord.py acquire-control --agent <id>`:

- Hermes crontab
- systemd units/timers
- persistent supervisors/watchdogs
- canonical vault files under `当前真相/` or `变更记录/`

Keep the lease short and release it immediately after read-after-write verification. A control lease never blocks research.

## Current owner and legacy boundary

`cursor-main` is the coordination owner. The legacy `adf_lf_continuous_factory.py` is excluded price-led history. Do not remove `/home/ubuntu/funding-research/results/adf_lf_continuous/STOP_MANUAL.stop`, restart that supervisor, or edit its watchdog without a fresh control receipt.

When a shared write is needed but the lease is unavailable, write a proposal/receipt and continue any independent work. Do not overwrite another agent's changes, force-push, or mutate canonical vault files directly.

## Existing work

Do not interrupt already-running research solely to apply this contract. The current `322 FINRA short-sale flow` process remains in progress; register its artifact when it completes.
