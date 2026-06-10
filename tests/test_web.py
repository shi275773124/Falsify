import json

import pytest

from web import serve


def test_extract_json_accepts_fenced_json():
    assert serve.extract_json('```json\n{"verdict":"PROCEED","risks":[]}\n```') == {
        "verdict": "PROCEED",
        "risks": [],
    }


def test_extract_json_rejects_missing_object():
    with pytest.raises(ValueError):
        serve.extract_json("no json here")


def test_web_template_escapes_error_text_before_innerhtml():
    assert "if(d.error){out.innerHTML='<p class=\"err\">'+esc(d.error)+'</p>'" in serve.PAGE


def test_web_template_normalizes_risk_severity_class():
    assert "sev=normSeverity(x.severity)" in serve.PAGE
    assert "class=\"risk '+sev+'\"" in serve.PAGE
