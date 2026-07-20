# Use Falsify Workflow Packs

[Getting Started](./00-getting-started.md) ? [Use locally & BYOK](./11-byok-and-policy.md)

Workflow packs are local, repeatable review instructions?not hosted services and not proof by themselves. Each pack tells an agent what evidence to request, how to challenge a claim, and how to format a verdict. Keep the resulting evidence and verdict artifact with your work.

## Available packs

| Pack | Use it when |
|---|---|
| [Deployment Claim Review](../skills/falsify-deployment-claim/) | A deploy sounds successful but you need evidence of the target state. |
| [AI PR Review](../skills/falsify-ai-pr-review/) | A human or agent PR claims work is complete. |
| [Research Report Audit](../skills/falsify-research-report/) | A memo may rely on stale, cherry-picked, or unsupported evidence. |
| [Agent Safety Check](../skills/falsify-agent-safety-check/) | An agent says it finished a consequential task. |

## Install in Claude Code

1. Copy one folder from [`skills/`](../skills/) into a project or user skills location, for example `.claude/skills/falsify-deployment-claim/`.
2. Confirm the folder contains `SKILL.md`.
3. Reload or restart your host if it requires it.
4. Invoke the pack with the claim and the raw artifacts requested by its input template.

## Install in Cursor

1. Copy a folder from [`skills/`](../skills/) into `.cursor/skills/<skill-name>/` or your Cursor user skills location.
2. Confirm the folder contains `SKILL.md`.
3. Let the host load it when the task matches, then provide the requested evidence.

No Falsify API key is required to install a pack. A live model-backed review still uses your provider key or a locally authenticated agent CLI.

## What a pack does not do

A pack does not automatically inspect your cloud account, run a production gate, or turn an agent's answer into evidence. Use it to structure the review; use the CLI or your own verification commands to generate and retain artifacts.

## Next

- [Run a local review](./00-getting-started.md)
- [CLI & Artifact Reference](./20-cli-and-artifacts.md)
- [Add a GitHub PR gate](./14-github-action-install.md)
