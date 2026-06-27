# Deployment Claim Review

Blocks deployment false confidence, especially claims like "logs are green" or "CI completed".

## Use

1. Copy `templates/input.md`.
2. Paste the claim, target, logs, and state evidence.
3. Run Falsify or another reviewer using `SKILL.md` as the workflow contract.
4. Return the verdict JSON.

Skills are workflows, not prompts: this package defines required inputs, evidence gates, verdict rules, and sample reports.
