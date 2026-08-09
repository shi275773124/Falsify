from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLOW_DOCS = ROOT / "design" / "falsify-flow-docs"
INDEX = (FLOW_DOCS / "index.html").read_text(encoding="utf-8-sig")
SCRIPT = (FLOW_DOCS / "candidate.js").read_text(encoding="utf-8-sig")
PRODUCTION_SOURCES = (INDEX, SCRIPT)


def test_flow_docs_entry_uses_canonical_docs_index():
    assert 'href="/docs/"' in INDEX
    assert "/design/falsify-flow-docs" not in INDEX


def test_production_navigation_sources_have_no_stale_design_docs_links():
    for source in PRODUCTION_SOURCES:
        assert "/design/falsify-flow-docs" not in source
        assert "/design/falsify-flow-docs/" not in source


def test_chinese_preference_is_retained_for_same_origin_navigation():
    assert 'document.querySelectorAll("a[href]")' in SCRIPT
    assert 'target.origin !== window.location.origin' in SCRIPT
    assert 'target.searchParams.set("lang", "zh")' in SCRIPT
    assert "target.pathname" in SCRIPT


def test_language_switch_preserves_the_current_canonical_page():
    assert "new URL(window.location.href)" in SCRIPT
    assert 'url.searchParams.delete("lang")' in SCRIPT
    assert 'url.searchParams.set("lang", "zh")' in SCRIPT
    assert "window.location.assign(url.toString())" in SCRIPT
    assert "window.location.pathname =" not in SCRIPT


def test_mobile_sidebar_closes_after_internal_navigation():
    assert 'document.querySelectorAll(".flow-docs-sidebar a")' in SCRIPT
    assert 'anchor.addEventListener("click", closeMenu)' in SCRIPT
    assert 'sidebar.classList.remove("open")' in SCRIPT
    assert 'menu.setAttribute("aria-expanded", "false")' in SCRIPT
