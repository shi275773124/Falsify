# Design comps — local preview

Start the server from repo root:

```bash
py -3.12 web/serve.py
```

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
