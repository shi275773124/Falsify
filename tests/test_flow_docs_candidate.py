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
    assert h.status_code==200 and "flow-docs-sidebar" in body and "Documentation" in body
    assert "00-getting-started.html" in body and "candidate.css" in body


def test_flow_docs_english_copy_is_unchanged():
    _, body=decoded_body("/design/falsify-flow-docs/")
    assert "FLOW / KNOWLEDGE BASE" in body
    assert "Install the PR gate, learn the framework, and ship decision artifacts your team can defend." in body
    assert ">Docs<" in body and ">Menu<" in body
    assert 'href="/design/falsify-flow-docs/" aria-current="page"' in body
    assert 'href="/docs/"' not in body


def test_flow_docs_chinese_index_uses_native_ui_copy_without_mojibake():
    h, body=decoded_body("/design/falsify-flow-docs/?lang=zh")
    assert h.status_code==200 and 'lang="zh-CN"' in body
    for copy in ("Falsify \u6587\u6863", "\u5ba1\u67e5\u4e0d\u662f\u66ff\u4f60\u505a\u51b3\u5b9a\u3002\u5b83\u5148\u628a\u4f9d\u636e\u6446\u51fa\u6765\u3002", "\u4ece\u672c\u5730 CLI \u5f00\u59cb\uff0c\u4e86\u89e3\u56de\u6267\u7ed3\u6784\u3001\u5ba1\u67e5\u6df1\u5ea6\u548c\u5404\u9886\u57df\u7684\u6269\u5c55\u8fb9\u754c\u3002", "\u5f00\u59cb\u4f7f\u7528", "\u6838\u5fc3\u6982\u5ff5", "\u9886\u57df\u6307\u5357", "\u67e5\u770b\u6307\u5357", "\u6253\u5f00\u83dc\u5355", "\u5173\u95ed\u83dc\u5355"):
        assert copy in body
    assert "\u5b89\u88c5 PR \u95f8\u95e8\u3001\u7406\u89e3\u6846\u67b6\uff0c\u4ea7\u51fa\u56e2\u961f\u80fd\u8fa9\u62a4\u7684\u51b3\u7b56\u4ea7\u7269\u3002" not in body
    assert not any(marker in body for marker in MOJIBAKE_MARKERS)
    assert 'href="/design/falsify-flow-docs/?lang=zh" aria-current="page"' in body
    assert 'href="/docs/?lang=zh"' not in body
    assert 'href="/design/falsify-flow-candidate/?lang=zh"' in body


def test_flow_doc_renders_markdown_with_active_sidebar_and_code():
    h, body=decoded_body("/design/falsify-flow-docs/00-getting-started.html")
    assert h.status_code==200 and "Getting Started" in body and 'aria-current="page"' in body
    assert "doc-body" in body and "<pre><code" in body


def test_flow_doc_chinese_uses_actual_translation_and_native_chrome():
    h, body=decoded_body("/design/falsify-flow-docs/00-getting-started.html?lang=zh")
    assert h.status_code==200 and 'lang="zh-CN"' in body and "\u5feb\u901f\u5f00\u59cb" in body
    assert ">\u6587\u6863<" in body and "\u6253\u5f00\u83dc\u5355" in body and "\u5207\u6362\u5230\u82f1\u6587" in body
    assert not any(marker in body for marker in MOJIBAKE_MARKERS)
