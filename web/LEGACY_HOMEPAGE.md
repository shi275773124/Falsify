# LEGACY homepage stack (do not use for production)

**Production homepage:** `design/falsify-flow-candidate/` served at `/`.

This directory's `templates/home.html` + `static/js/sui-motion.js` + related CSS was the
2026-07-01 sui.io visual-grammar transplant. It remains available for inspection only:

- Local / hermes: `/legacy/home`
- Do **not** re-point root `PAGE` to `load_homepage()`.

When editing marketing UI, change **only** `design/falsify-flow-candidate/`.
