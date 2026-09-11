# Deployment claim (matching-evidence fixture)

This is a **replay sample**, not a live probe of production.

Deployment claim: payment-api should be at 95d7e2f in production.

Probe (attached artifact, not a live call):

```text
GET /v2/projects/demo/services/payment-api/revision
HTTP 200
observed_revision=95d7e2f
claimed_revision=95d7e2f
match=true
finish_reason=stop
```

Rollback command: `helm rollback payment-api 12`
Account / region: demo-prod / us-east-1
