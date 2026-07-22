# Design comps — local preview

Start the server from repo root:

```bash
py -3.12 web/serve.py
```

## Light SaaS system → production (2026-07-22)

Light visual language is now the **production** homepage + docs chrome:

| Surface | Source | Local URL (via `web/serve.py`) |
|---------|--------|--------------------------------|
| **Homepage** | `design/falsify-flow-candidate/` | http://127.0.0.1:8000/ |
| **Docs** | `design/falsify-flow-docs/candidate.css` + `flow_docs_shell` | http://127.0.0.1:8000/docs/ |
| Static mock (archive) | `design/falsify-site-light/` | http://127.0.0.1:8770/ |

Nav: **合作 / Partner** → `#partner` (Chris Shi contact: X / Email / GitHub).

```bash
py -3.12 web/serve.py
# → http://127.0.0.1:8000/
```

## Cursor get-started replica (2026-07-21)

Static visual replica of [cursor.com/get-started](https://cursor.com/get-started), motion tuned with [emil-design-eng](https://github.com/emilkowalski/skills).

| Comp | URL |
|------|-----|
| **Cursor get-started replica** | http://127.0.0.1:8000/design/cursor-get-started/ |

Quick preview (no `web/serve.py` deps):

```bash
py -3 -m http.server 8765 --bind 127.0.0.1 --directory design/cursor-get-started
# → http://127.0.0.1:8765/
```

Stack: static HTML/CSS/JS · tokens sampled from live page · motion from `emil-design-eng` (ease-out, press scale 0.97, stagger enter, `prefers-reduced-motion`).

## Hero right column — Chris pick B / C / D (2026-06-28)

Left column **locked**. Screenshot path **deprecated**.

| Comp | URL |
|------|-----|
| **Hub (tabs B/C/D)** | http://127.0.0.1:8000/design/hero-v1-variants-bcd.html |
| Variant B · geometry | http://127.0.0.1:8000/design/hero-v1-variants-bcd.html#b |
| Variant C · pool + skill card | http://127.0.0.1:8000/design/hero-v1-variants-bcd.html#c |
| Variant D · media slot | http://127.0.0.1:8000/design/hero-v1-variants-bcd.html#d |
| Diagnosis (why screenshot fails) | http://127.0.0.1:8000/design/hero-right-column-diagnosis.md |
| Deprecated A+B (screenshot) | http://127.0.0.1:8000/design/hero-v1-ab-comp.html |

Use `http://127.0.0.1:8000/design/…` — not `file://` (breaks asset paths in some previews).

**Variant D video drop:** add `design/hero-demo.mp4`, set `<video src="hero-demo.mp4">` in the comp, reload.
