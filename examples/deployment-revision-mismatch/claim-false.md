# Deployment claim (false-green fixture)

This is a **replay sample**, not a live probe of production.

The migration succeeded because the logs completed successfully.
Another AI reviewed the rollout and found no issue.

- Target: production / payment-api
- Claimed commit: 95d7e2f
- Observed production revision: 41ac90b
- No post-deploy probe, parse status, HTTP status, finish_reason, or usage counts were kept.
- Rollback command: not recorded
