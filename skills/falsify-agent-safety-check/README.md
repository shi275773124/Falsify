# Agent Safety Check

Verifies agent completion claims before trust. It focuses on raw artifact trails, external side-effect verification, and irreversible-action boundaries.

## Use

1. Copy `templates/input.md`.
2. Paste the agent claim, tool outputs, artifact paths, side effects, and permission boundary.
3. Apply `SKILL.md` as the workflow contract.
4. Return JSON matching the verdict schema.

This workflow is a sign-off gate for agent completion, not a generic agent prompt.
