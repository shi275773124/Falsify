import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8899"
ART = Path(__file__).resolve().parent / "result" / "rich" / "understanding.json"

with sync_playwright() as pw:
    exe = Path.home() / "AppData" / "Local" / "ms-playwright" / "chromium-1243" / "chrome-win64" / "chrome.exe"
    browser = pw.chromium.launch(executable_path=str(exe) if exe.is_file() else None)
    page = browser.new_page()
    page.on("console", lambda m: print("CONSOLE", m.type, m.text[:300]))
    page.on("pageerror", lambda e: print("PAGEERROR", str(e)[:300]))
    page.goto(BASE + "/understanding?lang=zh")
    page.set_input_files("#file-input", str(ART))
    page.wait_for_timeout(1500)
    err = page.text_content("#import-error")
    print("import-error:", repr(err))
    print("reader hidden:", page.get_attribute("#reader", "hidden"))
    page.screenshot(path=str(Path(__file__).parent / "debug-import.png"))
    browser.close()
