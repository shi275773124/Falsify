import json
from io import BytesIO

import pytest

from web import serve


REQUIRED_PUBLIC_COPY = [
    'Review first. Trust after.',
    'Falsify does not argue. It asks one question: where is the evidence.',
    '先审，再信。',
    'Falsify 不争。只问一件事：证据在哪。',
    'Frame Audit + Adversarial Review + Cutline.',
    '框架审 + 对抗审 + Cutline。',
    'audit the audit channel itself',
    '审计通道本身也要被审计',
    'human-auditability break',
    'owner / lock / lifecycle',
    'duplicated authority sources',
    'rollback / verification path',
    'naming / status semantics that mislead',
    '命名与状态语义误导',
    'Semantic verdict nudge',
    'Prompt-only audit theater',
    'Monitor-failure laundering',
    'Must Fix',
    'Known Debt',
    'Delete',
    'Verdict',
    'Final',
    'Falsify classifies risk. It does not authorize action.',
    'Falsify 只做风险分类，不做执行授权。',
    'independent final judgment',
    'Self-review is not independent review.',
]
def test_extract_json_accepts_fenced_json():
    assert serve.extract_json('```json\n{"verdict":"PASS","risks":[]}\n```') == {
        "verdict": "PASS",
        "risks": [],
    }


def test_extract_json_rejects_missing_object():
    with pytest.raises(ValueError):
        serve.extract_json("no json here")


def test_web_prompt_contains_audit_channel_checks():
    assert "AI summary without raw evidence" in serve.RISK_SYSTEM
    assert "fake acceptance evidence" in serve.RISK_SYSTEM
    assert "logs treated as state verification" in serve.RISK_SYSTEM
    assert "second-model agreement treated as proof" in serve.RISK_SYSTEM
    assert "prompt-only audit theater" in serve.RISK_SYSTEM
    assert "semantic nudges toward PASS" in serve.RISK_SYSTEM
    assert "monitor failure laundering" in serve.RISK_SYSTEM
    assert "finish_reason" in serve.RISK_SYSTEM
    assert "usage/token counts" in serve.RISK_SYSTEM
    assert "Cutline" in serve.RISK_SYSTEM


def test_web_template_contains_public_product_markers():
    assert "Review first. Trust after." in serve.PAGE
    assert "Frame Audit + Adversarial Review + Cutline." in serve.PAGE
    for phrase in REQUIRED_PUBLIC_COPY:
        assert phrase in serve.PAGE
    assert "PASS / PASS_WITH_DEBT / BLOCK" in serve.PAGE
    assert "Real backend, not fake analysis." in serve.PAGE
    assert '<canvas id="cvs" role="img"' in serve.PAGE
    assert "NODE_DESKTOP=168" in serve.PAGE
    assert "SCAN_PERIOD=7200" in serve.PAGE
    assert "prefers-reduced-motion:reduce" in serve.PAGE
    assert "/docs/" in serve.PAGE
    assert "https://github.com/shi275773124/Falsify/blob/main/LICENSE" in serve.PAGE

def test_normalize_verdict_maps_legacy_and_unknown_to_public_values():
    assert serve.normalize_verdict("PROCEED") == "PASS"
    assert serve.normalize_verdict("PASS_WITH_DEBT") == "PASS_WITH_DEBT"
    assert serve.normalize_verdict("nope") == "BLOCK"


def test_i18n_keys_exist_in_english_and_chinese():
    keys = set()
    for match in serve.re.finditer(r'data-i18n="([^"]+)"', serve.PAGE):
        keys.add(match.group(1))

    assert keys
    for key in keys:
        assert f"{key}:" in serve.PAGE or f'"{key}":' in serve.PAGE

    en_block = serve.PAGE.split("const T={en:", 1)[1].split("},\nzh:", 1)[0]
    zh_block = serve.PAGE.split("},\nzh:", 1)[1].split("};", 1)[0]
    missing_en = [key for key in keys if f"{key}:" not in en_block and f'"{key}":' not in en_block]
    missing_zh = [key for key in keys if f"{key}:" not in zh_block and f'"{key}":' not in zh_block]

    assert missing_en == []
    assert missing_zh == []


def make_handler(path):
    handler = serve.H.__new__(serve.H)
    handler.path = path
    handler.headers = {}
    handler.wfile = BytesIO()
    handler._headers_buffer = []
    handler.request_version = "HTTP/1.1"
    handler.command = "GET"
    handler.send_response = lambda code, message=None: setattr(handler, "status_code", code)
    handler.send_header = lambda *args: None
    handler.end_headers = lambda: None
    return handler


def test_docs_index_route_returns_200():
    handler = make_handler("/docs/")
    handler.do_GET()

    assert handler.status_code == 200
    assert b"Docs" in handler.wfile.getvalue()


def test_docs_markdown_route_returns_200():
    handler = make_handler("/docs/00-getting-started.md")
    handler.do_GET()

    assert handler.status_code == 200
    assert b"Getting Started" in handler.wfile.getvalue()


def test_static_traversal_is_rejected():
    assert serve.safe_repo_path("/docs/../LICENSE") is None
    assert serve.safe_repo_path("/docs/%2e%2e/LICENSE") is None

    handler = make_handler("/docs/../LICENSE")
    handler.do_GET()
    assert handler.status_code == 404
