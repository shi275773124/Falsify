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
    for copy in ("Falsify 文档", "让无法自证的绿灯在变成事故前曝露。", "开始使用", "接入 CI", "理解裁决"):
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
    assert h.status_code==200 and 'lang="zh-CN"' in body and "快速开始" in body
    assert "跳到正文" in body and ">文档<" in body and "打开菜单" in body and "切换至中文" in body
    assert not any(marker in body for marker in MOJIBAKE_MARKERS)


def test_docs_routes_accept_html_and_md_canonical_paths():
    for path in ("/docs/00-getting-started.html", "/docs/00-getting-started.md", "/docs/19-security-and-contact.html"):
        h, body = decoded_body(path)
        assert h.status_code == 200
        assert "flow-docs" in body
