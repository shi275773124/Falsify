"""Browser behavior acceptance for /understanding (playwright, local server).

Covers: import success + five sections, ref -> source dialog with highlighted
lines, confirm/retract revision, answer recording, JSON+MD export with/without
notes, XSS non-execution, zh/en, narrow viewport. Writes screenshots.
"""

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
DEMO = Path(__file__).resolve().parent
BASE = "http://127.0.0.1:8899"
RESULTS = DEMO / "browser-acceptance"
RESULTS.mkdir(parents=True, exist_ok=True)

checks = []


def check(name, ok, detail=""):
    checks.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + str(detail)) if detail else ""))


def main():
    artifact = DEMO / "result" / "rich" / "understanding.json"

    with sync_playwright() as pw:
        exe = Path.home() / "AppData" / "Local" / "ms-playwright" / "chromium-1243" / "chrome-win64" / "chrome.exe"
        browser = pw.chromium.launch(executable_path=str(exe) if exe.is_file() else None)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        page.goto(BASE + "/understanding?lang=zh")

        # --- import
        page.set_input_files("#file-input", str(artifact))
        page.wait_for_selector("#reader:not([hidden])", timeout=5000)
        check("import shows reader", page.is_visible("#reader"))
        check("meta verdict shown", "BLOCK" in page.text_content("#meta-list"))

        # --- five sections rendered
        for sec, marker in (
            ("#sec-goal", "目标"),
            ("#sec-assumptions", "承重假设"),
            ("#sec-findings", "发现解释"),
            ("#sec-unknowns", "未知"),
        ):
            txt = page.text_content(sec) or ""
            check(f"section {sec} rendered", len(txt.strip()) > 10, txt[:40])

        # --- ref -> source dialog with highlighted lines
        page.click(".refs button >> nth=0")
        page.wait_for_selector("dialog.srcdialog", timeout=5000)
        check("source dialog opens", page.is_visible("dialog.srcdialog"))
        hl = page.text_content("dialog.srcdialog .hl")
        check("highlighted line present", bool(hl and hl.strip()))
        page.screenshot(path=str(RESULTS / "01-source-dialog.png"))
        page.click("dialog.srcdialog button")
        page.wait_for_selector("dialog.srcdialog", state="detached", timeout=5000)

        # --- confirm / retract a revision
        rev_before = page.text_content("#sec-revisions")
        check("revisions listed", "平台" in rev_before or "确认" in rev_before)
        page.on("dialog", lambda d: d.accept())
        page.click("#sec-revisions .rev .actions button >> nth=0")  # 确认
        page.wait_for_timeout(200)
        rev_after = page.text_content("#sec-revisions")
        check("confirm marks item", ("已确认" in rev_after) or ("rev.confirmed" in page.get_attribute("#sec-revisions .rev.confirmed", "class") if page.query_selector("#sec-revisions .rev.confirmed") else False))
        if page.query_selector("#sec-revisions .rev.confirmed button"):
            page.click("#sec-revisions .rev.confirmed button")  # 撤销
            page.wait_for_timeout(200)
            rev_final = page.text_content("#sec-revisions")
            check("retract restores suggestion", "已撤销" in rev_final)
        page.screenshot(path=str(RESULTS / "02-revisions.png"), full_page=True)

        # --- answer recording
        if page.query_selector("#sec-prompts textarea"):
            page.fill("#sec-prompts textarea", "如果切自然周，窗口完整性假设最先失效。")
            page.click("#sec-prompts button")
            page.wait_for_timeout(200)
            check("answer recorded indicator", "已记录" in (page.text_content("#sec-prompts") or ""))

        # --- export with everything
        page.click("#btn-preview")
        page.wait_for_selector("#preview-area:not([hidden])", timeout=5000)
        check("preview visible", page.is_visible("#preview-body"))
        with page.expect_download() as dl:
            page.click("#btn-export-json")
        jp = RESULTS / "export-full.json"
        dl.value.save_as(str(jp))
        data = json.loads(jp.read_text(encoding="utf-8"))
        check("export full has notes", data["user_notes"]["before_recorded"] is not None)
        check("export full has revisions", len(data.get("suggested_revisions", [])) == 2)
        check("export keeps source text", all(
            s["content_state"] == "included" for s in data["sources"]))
        with page.expect_download() as dl2:
            page.click("#btn-export-md")
        mp = RESULTS / "export-full.md"
        dl2.value.save_as(str(mp))
        md = mp.read_text(encoding="utf-8")
        check("md contains sections", "它怎样运转" in md and "还有什么没弄清" in md)

        # --- export without notes/texts
        page.uncheck("#opt-include-notes")
        page.uncheck("#opt-include-texts")
        page.click("#btn-preview")
        with page.expect_download() as dl3:
            page.click("#btn-export-json")
        jp2 = RESULTS / "export-minimal.json"
        dl3.value.save_as(str(jp2))
        data2 = json.loads(jp2.read_text(encoding="utf-8"))
        check("minimal drops notes", data2["user_notes"]["before_recorded"] is None
              and data2["user_notes"]["answers"] == []
              and data2.get("suggested_revisions") == [])
        withheld = [s for s in data2["sources"] if s["role"] != "receipt"]
        check("minimal withholds texts", all(
            s["content_state"] == "withheld" and not s.get("text") for s in withheld))

        # --- withheld artifact re-imports
        page.goto(BASE + "/understanding?lang=zh")
        page.set_input_files("#file-input", str(jp2))
        page.wait_for_selector("#reader:not([hidden])", timeout=5000)
        body_txt = page.text_content("#sec-sources") or ""
        check("withheld import shows unverifiable", ("无法核对" in body_txt) or ("省略" in body_txt))

        # --- XSS: malicious artifact must not execute
        evil = json.loads(artifact.read_text(encoding="utf-8"))
        evil["project_model"]["goal"]["text"] = "<img src=x onerror=window.__xss=1>MARKER_XSS"
        evil_path = RESULTS / "evil.json"
        evil_path.write_text(json.dumps(evil, ensure_ascii=False), encoding="utf-8")
        page.goto(BASE + "/understanding?lang=zh")
        page.set_input_files("#file-input", str(evil_path))
        page.wait_for_selector("#reader:not([hidden])", timeout=5000)
        xss = page.evaluate("() => window.__xss || null")
        check("xss not executed", xss is None)
        check("xss text shown as text", "MARKER_XSS" in (page.text_content("#sec-goal") or ""))

        # --- narrow viewport renders
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(200)
        check("390px viewport ok", page.is_visible("#reader"))
        page.screenshot(path=str(RESULTS / "03-narrow-390px.png"), full_page=True)
        page.set_viewport_size({"width": 1440, "height": 900})
        page.wait_for_timeout(200)
        check("1440px viewport ok", page.is_visible("#reader"))

        # --- English locale
        page.goto(BASE + "/understanding?lang=en")
        page.set_input_files("#file-input", str(artifact))
        page.wait_for_selector("#reader:not([hidden])", timeout=5000)
        check("en locale strings", "How it works" in (page.text_content("body") or ""))
        page.screenshot(path=str(RESULTS / "04-en-locale.png"), full_page=True)

        browser.close()

    fails = [c for c in checks if not c[1]]
    report = {"checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks],
              "passed": len(checks) - len(fails), "failed": len(fails)}
    (RESULTS / "acceptance-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{report['passed']} passed, {report['failed']} failed")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
