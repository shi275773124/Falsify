from io import BytesIO
from web import serve

MOJIBAKE_MARKERS = ("\ufffd", "\u00c3", "\u00c2", "\u00e6\u2013\u2021", "\u00e4\u00b8")


def handler(path):
    h=serve.H.__new__(serve.H); h.path=path; h.headers={}; h.wfile=BytesIO(); h._headers_buffer=[]; h.request_version="HTTP/1.1"; h.command="GET"
    h.send_response=lambda code, message=None:setattr(h,"status_code",code); h.send_header=lambda *args:None; h.end_headers=lambda:None
    return h


def decoded_body(path):
    h=handler(path); h.do_GET(); return h, h.wfile.getvalue().decode("utf-8")


def test_flow_docs_index_isolated_and_real():
    h, body=decoded_body("/design/falsify-flow-docs/")
    assert h.status_code==200 and "flow-docs-sidebar" in body and "Catch the green light" in body
    assert "00-getting-started.html" in body and "candidate.css" in body


def test_docs_index_uses_task_first_information_architecture():
    _, body=decoded_body("/docs/")
    for label in ("Start here", "Use locally", "Add to CI", "Understand verdicts", "Reference", "Security &amp; Contact"):
        assert label in body
    assert "Open Core" not in body and "Team Edition" not in body


def test_flow_docs_chinese_index_uses_native_ui_copy_without_mojibake():
    h, body=decoded_body("/design/falsify-flow-docs/?lang=zh")
    assert h.status_code==200 and 'lang="zh-CN"' in body
    for copy in ("Falsify 鏂囨。", "璁╂棤娉曡嚜璇佺殑缁跨伅鍦ㄥ彉鎴愪簨鏁呭墠鏇濋湶銆?, "寮€濮嬩娇鐢?, "鎺ュ叆 CI", "鐞嗚В瑁佸喅"):
        assert copy in body
    assert not any(marker in body for marker in MOJIBAKE_MARKERS)
    assert 'href="/design/falsify-flow-docs/?lang=zh" aria-current="page"' in body
    assert 'href="/design/falsify-flow-candidate/?lang=zh"' in body


def test_flow_doc_renders_markdown_with_active_sidebar_and_code():
    h, body=decoded_body("/design/falsify-flow-docs/00-getting-started.html")
    assert h.status_code==200 and "Getting Started" in body and 'aria-current="page"' in body
    assert "false green" in body and "doc-body" in body and "<pre><code" in body


def test_flow_doc_chinese_uses_actual_translation_and_native_chrome():
    h, body=decoded_body("/design/falsify-flow-docs/00-getting-started.html?lang=zh")
    assert h.status_code==200 and 'lang="zh-CN"' in body and "蹇€熷紑濮? in body
    assert "璺冲埌姝ｆ枃" in body and ">鏂囨。<" in body and "鎵撳紑鑿滃崟" in body and "鍒囨崲鑷充腑鏂? in body
    assert not any(marker in body for marker in MOJIBAKE_MARKERS)


def test_flow_docs_never_render_question_mark_corrupted_chinese_sources():
    expected_titles = {
        "11-byok-and-policy": "鏈湴浣跨敤涓?BYOK",
        "17-skills": "浣跨敤 Falsify 宸ヤ綔娴佸寘",
        "20-cli-and-artifacts": "CLI 涓庝骇鐗╁弬鑰?,
    }
    for stem, title in expected_titles.items():
        h, body = decoded_body(f"/docs/{stem}.html?lang=zh")
        assert h.status_code == 200
        assert title in body
        assert "????" not in body


def test_docs_routes_accept_html_and_md_canonical_paths():
    for path in ("/docs/00-getting-started.html", "/docs/00-getting-started.md", "/docs/19-security-and-contact.html"):
        h, body = decoded_body(path)
        assert h.status_code == 200
        assert "flow-docs" in body
