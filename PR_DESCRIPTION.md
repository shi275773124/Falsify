# PR Description

## Summary

Repositioned Falsify as a commercializable B2B-first adversarial sign-off layer for high-risk AI work. The homepage now leads with a forensic Verdict Cockpit, explains PR/deployment/research/agent use cases, differentiates Falsify from eval/observability/red-team categories, keeps verdict language to `PASS`, `PASS_WITH_DEBT`, and `BLOCK`, and presents the open protocol -> skills -> Audit Sprint -> Design Partner -> Team path conservatively.

Created a v0 skills pack with four repeatable sign-off workflows:

- `skills/falsify-deployment-claim/`
- `skills/falsify-ai-pr-review/`
- `skills/falsify-research-report/`
- `skills/falsify-agent-safety-check/`

## Files Changed

- `web/templates/home.html`
- `web/static/css/tokens.css`
- `web/static/css/home.css`
- `web/static/js/home.js`
- `README.md`
- `docs/10-team-delivery-and-business-model.md`
- `docs/self-falsify-2026-06-25.md`
- `skills/falsify-deployment-claim/**`
- `skills/falsify-ai-pr-review/**`
- `skills/falsify-research-report/**`
- `skills/falsify-agent-safety-check/**`
- `GOAL_PROGRESS.md`
- `PR_DESCRIPTION.md`

## Verification Commands And Outputs

- `py -3.12 -m py_compile falsify.py web\serve.py` -> exit 0.
- `python -m json.tool` on all four skill `templates/verdict.schema.json` and sample `block-output.json` files -> exit 0.
- `py -3.12 -m pytest` -> `51 passed in 1.56s`.
- `GET http://127.0.0.1:8000/` -> `200`.
- `GET http://127.0.0.1:8000/docs/` -> `200`.
- `GET http://127.0.0.1:8000/examples/sample-block-report.json` -> `200`.
- `POST http://127.0.0.1:8000/review` with production claim -> setup error when no provider is configured, preserving real backend behavior instead of fake analysis.
- Browser metrics at 360x800, 390x844, 768x1024, 1440x1000 -> no horizontal scroll; cockpit, wedge, bento, workbench, skills, commercial path, business loop, and artifact sections visible.
- Browser interactions -> Run sample rendered a `BLOCK` verdict artifact; language switch changed page to `zh-CN`; mobile menu opened.
- Unsupported claim scan -> no matches for `NOT_VIABLE`, `CAUGHT`, guarantee-truth, prevent-hallucination, SOC2, ARR, customer logos, 99%, hosted dashboard, or full enterprise SaaS.

## Screenshot Paths

- `.verification-shots/mobile-360x800-v5.png`
- `.verification-shots/mobile-390x844-v5.png`
- `.verification-shots/tablet-768x1024-v5.png`
- `.verification-shots/desktop-1440x1000-v5.png`

## Commercial Boundary Implemented

- Open core today: CLI, JSON schema, GitHub Action path, local artifacts, workflow templates, downloadable skills, public examples.
- Audit Sprint / Design Partner: positioned as service/pilot path for one high-risk artifact or one team workflow.
- Team / Enterprise: positioned as path only; hosted/team controls are not claimed as live repo features.
- Skills: positioned as public distribution and proof layer, not primary company identity.
- License: repo has MIT `LICENSE`; brand/certification marks, managed integrations, support, private deployment path, and commercial workflow packaging remain commercial boundary items.

## Known Risks

- Hosted/team capabilities are described as a commercial path, not as live product features.
- The homepage live review still depends on the existing local `/review` backend configuration and provider keys.
- Final human review should confirm commercial copy, visual taste, and contact route before deployment.
