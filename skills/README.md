# OSS Skills packs

Sign-off **workflows** for high-risk claims. Not a second Falsify product.

## Claiming Falsify（根治定义）

```text
Installing or reading a pack ≠ Claiming Falsify.

Claiming Falsify requires:
  1. Running an authority exit (see below), and
  2. Keeping command + exit code / JSON artifact, and
  3. Using the unified verdict vocabulary (docs/verdict-vocabulary.md).
```

### Authority exits (OSS)

| Exit | Command / path |
|------|----------------|
| Local demo / review | `python -m falsify demo` · `python -m falsify review …` |
| Quant (optional extra) | `python -m falsify.quant_gate …` with `pip install falsify[quant]` |
| CI | GitHub Action templates under `templates/` |

### What packs are

| Pack | Directory | Claim class |
|------|-----------|-------------|
| Brooks-Lint (L0) | `falsify-brooks-lint/` | structural decay / auditability (Framework layer) |
| Deployment | `falsify-deployment-claim/` | logs green ≠ state |
| AI PR | `falsify-ai-pr-review/` | PR / agent code claims |
| Research | `falsify-research-report/` | memo / report claims |
| Agent safety | `falsify-agent-safety-check/` | agent “done” claims |
| Live production | `falsify-live-production-gate/` | live/cron restore claims (pattern export) |

Each pack: input contract → evidence rules → cutline → `falsify.review.v1` JSON.

## Related public surface

| Surface | Role |
|---------|------|
| [shi275773124/Falsify](https://github.com/shi275773124/Falsify) | **Product** (this repo) |
| [shi275773124/falsify-skill](https://github.com/shi275773124/falsify-skill) | **Distribution shell** for agent install / ASP narrative — not a second protocol |

## Docs

- [Skills install](../docs/17-skills.md)  
- [ROOTFIX](../docs/ROOTFIX-architecture.md)  
- [Versioning](../docs/VERSIONING.md)  
- [Verdict vocabulary](../docs/verdict-vocabulary.md)  
