import json

import pytest

from web import serve


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
    assert "Stop trusting confident AI." in serve.PAGE
    assert "Falsify = Brooks-Lint + Adversarial Review + Risk Scalpel" in serve.PAGE
    assert "PASS / PASS_WITH_DEBT / BLOCK" in serve.PAGE
    assert "This calls the configured backend. It is not a fake analysis." in serve.PAGE


def test_normalize_verdict_maps_legacy_and_unknown_to_public_values():
    assert serve.normalize_verdict("PROCEED") == "PASS"
    assert serve.normalize_verdict("PASS_WITH_DEBT") == "PASS_WITH_DEBT"
    assert serve.normalize_verdict("nope") == "BLOCK"
