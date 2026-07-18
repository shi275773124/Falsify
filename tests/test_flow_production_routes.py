import io
from pathlib import Path
from unittest.mock import patch

from web import serve


def request(path: str):
    handler = serve.H.__new__(serve.H)
    handler.path = path
    handler.command = "GET"
    handler.request_version = "HTTP/1.1"
    handler.wfile = io.BytesIO()
    handler.send_response = lambda code: setattr(handler, "status_code", code)
    handler.send_header = lambda *args: None
    handler.end_headers = lambda: None
    handler._route()
    return handler


def body_text(handler):
    return handler.wfile.getvalue().decode("utf-8")


def test_root_serves_v2_flow_candidate_and_versioned_assets():
    root = request("/")
    body = body_text(root)
    assert root.status_code == 200
    assert "Falsify | Evidence gate for AI claims on GitHub" in body
    assert "/assets/flow/home.css?v=" in body
    assert "/assets/flow/home.js?v=" in body
    assert "/assets/flow/flow-canvas.js?v=" in body
    assert "/assets/flow/flow-motion.js?v=" in body or "flow-motion" in body
    assert ("Check the authority" in body) or ("95d7e2f" in body and "41ac90b" in body)


def test_same_origin_flow_assets_are_served():
    for path, marker in (("/assets/flow/home.css", b".hero"), ("/assets/flow/home.js", b"FalsifyFlow"), ("/assets/flow/flow-motion.js", b"FalsifyFlowMotion"), ("/assets/flow/flow-canvas.js", b"IntersectionObserver")):
        response = request(path)
        assert response.status_code == 200
        assert marker in response.wfile.getvalue()


def test_candidate_and_case_routes_are_inspectable():
    candidate = request("/design/falsify-flow-candidate/")
    case = request("/examples/real-cases/02-derived-freshness-stale-panel.md")
    assert candidate.status_code == 200
    assert case.status_code == 200
    assert "derived freshness false-green" in body_text(case)


def test_unknown_flow_asset_fails_closed():
    response = request("/assets/flow/not-real.js")
    assert response.status_code == 404

def test_legacy_home_is_retired_and_not_root():
    root = body_text(request("/"))
    for path in ("/legacy/home", "/legacy/home.html"):
        legacy = request(path)
        assert legacy.status_code == 410
        assert "falsify.zjdeng.xyz" not in body_text(legacy)
        assert "fonts.googleapis.com" not in body_text(legacy)
    assert "flow-canvas" in root or "flow-orbs" in root or "/assets/flow/" in root
