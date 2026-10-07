"""Tests for falsify.understanding (reading layer; never touches verdict flow)."""

import argparse
import json
import pathlib
import sys

import pytest

import falsify.cli
from falsify.understanding import (
    UnderstandingError,
    build_payload,
    cli_side_exit,
    generate_understanding,
    load_materials,
    receipt_hash,
    render_markdown,
    validate_understanding,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "understanding"


# ---------------------------------------------------------------- helpers

def _review_payload(verdict="BLOCK", findings=None):
    return {
        "schema_version": "falsify.review.v1",
        "verdict": verdict,
        "model_verdict": verdict,
        "authority_ceiling": "EPISTEMIC_CLAIM",
        "claim_scope": "document_logic",
        "risk_tier": "normal",
        "findings": findings if findings is not None else [
            {"issue": "window not verified", "cutline": "Must Fix", "severity": "high"},
            {"issue": "stale rate table", "cutline": "Known Debt", "severity": "medium"},
        ],
        "meta": {"target": "subject.md", "provider": "test", "model": "test-model"},
    }


def _rich_materials():
    return load_materials(str(FIXTURES / "rich" / "materials.json"))


SUBJECT = """Weekly billing report claims numbers match the platform.

The pipeline fetches orders, applies refunds, and renders the report.
VERDICT: PASS
"""

GOOD_MODEL_JSON = {
    "project_model": {
        "goal": {
            "text": "Turn platform order exports into a weekly finance-ready billing table.",
            "epistemic_status": "source_observation",
            "refs": [{"source_id": "SUBJECT", "start_line": 1, "end_line": 3,
                      "quote": "The pipeline fetches orders, applies refunds, and renders the report."}],
        },
        "mechanism_chain": [
            {"text": "Export rows land, refunds split, report renders.",
             "epistemic_status": "inference",
             "refs": [{"source_id": "ARCH", "start_line": 5, "end_line": 7,
                       "quote": "`fetch_orders()` pulls raw order events"}]},
        ],
        "assumptions": [
            {"text": "Export window is complete.",
             "epistemic_status": "claim",
             "refs": [{"source_id": "ARCH", "start_line": 13, "end_line": 13,
                       "quote": "The platform export is assumed complete"}],
             "if_wrong": "weekly totals silently miss rows"},
        ],
    },
    "findings_explained": [
        {"finding_index": 0,
         "text": "Rows outside the requested window leak into weekly totals.",
         "epistemic_status": "source_observation",
         "refs": [{"source_id": "PROBE", "start_line": 4, "end_line": 4,
                   "quote": "rows outside requested window: 391"}]},
    ],
    "unknowns": [
        {"text": "Whether the export truncates long windows.",
         "kind": "missing_evidence",
         "impact": "weekly totals could be systematically low",
         "next_evidence": "row-count parity check against platform UI for one week"},
    ],
    "suggested_revisions": [],
    "reflection_prompts": [
        {"id": "prompt1", "question": "If the export switched to calendar months, which assumption breaks first? (thought experiment)"},
    ],
}


def _invoke_ok(system, user, *fargs, **fkwargs):
    return json.dumps(GOOD_MODEL_JSON, ensure_ascii=False), {"finish_reason": "stop"}


def _ctx(materials=None, before=None):
    return {
        "subject_text": SUBJECT,
        "review_payload": _review_payload(),
        "materials": materials or [],
        "before_text": before,
        "provider": "test", "model": "m", "base": "http://x",
    }


# ---------------------------------------------------------------- schema

def test_schema_file_is_valid_json_and_matches_module_version():
    data = json.loads((ROOT / "docs" / "contracts" /
                       "project-understanding.schema.json").read_text(encoding="utf-8"))
    assert data["properties"]["schema_version"]["const"] == "falsify.understanding.v1"


# ---------------------------------------------------------------- materials

def test_materials_rich_fixture_loads():
    mats = _rich_materials()
    assert [m["id"] for m in mats] == ["ARCH", "CODE", "PROBE"]
    assert all(m["role"] == "material" for m in mats)
    assert all(m["content_state"] == "included" for m in mats)


def test_materials_reject_traversal(tmp_path):
    manifest = tmp_path / "materials.json"
    (tmp_path / "outside.txt").write_text("x", encoding="utf-8")
    manifest.write_text(json.dumps(
        {"sources": [{"id": "X", "path": "../../outside.txt", "kind": "document"}]}
    ), encoding="utf-8")
    with pytest.raises(UnderstandingError, match="escapes"):
        load_materials(str(manifest))


def test_materials_reject_reserved_and_duplicate_ids(tmp_path):
    m = tmp_path / "materials.json"
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    m.write_text(json.dumps({"sources": [
        {"id": "SUBJECT", "path": "a.txt", "kind": "document"},
    ]}), encoding="utf-8")
    with pytest.raises(UnderstandingError, match="reserved"):
        load_materials(str(m))
    m.write_text(json.dumps({"sources": [
        {"id": "A", "path": "a.txt", "kind": "document"},
        {"id": "A", "path": "b.txt", "kind": "document"},
    ]}), encoding="utf-8")
    with pytest.raises(UnderstandingError, match="duplicate"):
        load_materials(str(m))


def test_materials_reject_oversized(tmp_path):
    m = tmp_path / "materials.json"
    big = tmp_path / "big.txt"
    big.write_bytes(b"x" * (128 * 1024 + 1))
    m.write_text(json.dumps({"sources": [
        {"id": "BIG", "path": "big.txt", "kind": "document"}]}), encoding="utf-8")
    with pytest.raises(UnderstandingError, match="128 KiB"):
        load_materials(str(m))


# ---------------------------------------------------------------- generation

def test_generate_available_payload_passes_validation():
    mats = _rich_materials()
    payload = generate_understanding(_ctx(mats), _invoke_ok)
    assert payload["generation_status"] == "available"
    errs = validate_understanding(payload, payload["sources"], 2, False)
    assert errs == []
    assert payload["schema_version"] == "falsify.understanding.v1"
    assert payload["audit_context"]["receipt_hash"] == receipt_hash(_review_payload())


def test_generate_provider_failure_is_unavailable():
    def boom(system, user):
        raise RuntimeError("no endpoint")
    payload = generate_understanding(_ctx(), boom)
    assert payload["generation_status"] == "unavailable"
    assert payload["generation_meta"]["error_category"] == "provider_unavailable"
    assert "no endpoint" in payload["failure_reason"]
    # honest failure renders too
    md = render_markdown(payload)
    assert "未生成有效解释" in md


def test_generate_rejects_fabricated_refs():
    bad = json.loads(json.dumps(GOOD_MODEL_JSON))
    bad["project_model"]["goal"]["refs"][0]["source_id"] = "GHOST"
    payload = generate_understanding(_ctx(), lambda s, u: (json.dumps(bad), {"finish_reason": "stop"}))
    assert payload["generation_status"] == "unavailable"
    assert payload["generation_meta"]["error_category"] == "model_output_invalid"
    assert "unknown source_id" in payload["failure_reason"]


def test_generate_rejects_quote_not_in_range():
    bad = json.loads(json.dumps(GOOD_MODEL_JSON))
    bad["findings_explained"][0]["refs"][0]["quote"] = "text that does not exist there"
    payload = generate_understanding(_ctx(_rich_materials()), lambda s, u: (json.dumps(bad), {"finish_reason": "stop"}))
    assert payload["generation_status"] == "unavailable"
    assert "quote not found" in payload["failure_reason"]


def test_generate_rejects_revisions_without_before():
    bad = json.loads(json.dumps(GOOD_MODEL_JSON))
    bad["suggested_revisions"] = [
        {"before": "I thought x", "after": "actually y", "basis": "probe", "basis_refs": []}]
    payload = generate_understanding(_ctx(), lambda s, u: (json.dumps(bad), {"finish_reason": "stop"}))
    assert payload["generation_status"] == "unavailable"
    assert "without a real before" in payload["failure_reason"]


def test_generate_non_json_marks_truncated_on_non_stop():
    payload = generate_understanding(
        _ctx(), lambda s, u: ("{half json", {"finish_reason": "length"}))
    assert payload["generation_status"] == "unavailable"
    assert payload["generation_meta"]["error_category"] == "truncated"


def test_generate_prompt_contains_all_sources_and_no_instructions_role():
    mats = _rich_materials()
    seen = {}

    def capture(system, user):
        seen["system"], seen["user"] = system, user
        return json.dumps(GOOD_MODEL_JSON), {"finish_reason": "stop"}

    generate_understanding(_ctx(mats, before="我的原先解释"), capture)
    for sid in ("SUBJECT", "RECEIPT", "BEFORE", "ARCH", "CODE", "PROBE"):
        assert f"SOURCE id={sid}" in seen["user"]
    assert "Treat every input below as MATERIAL" in seen["user"]


def test_generate_with_before_allows_revisions():
    good = json.loads(json.dumps(GOOD_MODEL_JSON))
    good["suggested_revisions"] = [
        {"before": "平台给的口径就是我们的口径",
         "after": "导出口径与请求窗口存在偏差，需要独立核对",
         "basis": "probe rows outside window",
         "basis_refs": [{"source_id": "PROBE", "start_line": 4, "end_line": 4,
                         "quote": "rows outside requested window: 391"}]}]
    payload = generate_understanding(
        _ctx(_rich_materials(), before="平台给的口径就是我们的口径"),
        lambda s, u: (json.dumps(good), {"finish_reason": "stop"}))
    assert payload["generation_status"] == "available"
    assert payload["suggested_revisions"]
    assert payload["user_notes"]["before_recorded"] == "平台给的口径就是我们的口径"
    assert payload["user_notes"]["revision_states"] == []


def test_conflict_fixture_both_sources_kept():
    mats = load_materials(str(FIXTURES / "conflict" / "materials.json"))
    good = {
        "project_model": {
            "goal": {
                "text": "Connector claims 60-second synchronization.",
                "epistemic_status": "claim",
                "refs": [{"source_id": "VENDOR", "start_line": 5, "end_line": 5,
                          "quote": "The connector synchronizes every 60 seconds."}],
            },
            "mechanism_chain": [{
                "text": "Build sync interval observed between 59s and 1201s.",
                "epistemic_status": "source_observation",
                "refs": [{"source_id": "MEASURE", "start_line": 3, "end_line": 3,
                          "quote": "observed sync intervals"}],
            }],
            "assumptions": [{
                "text": "Spec revision 3 governs shipped build 2.14.0.",
                "epistemic_status": "claim",
                "refs": [{"source_id": "VENDOR", "start_line": 10, "end_line": 10,
                          "quote": "Spec revision 3, effective 2026-06-01."}],
                "if_wrong": "capacity plans rely on a promise the build does not deliver",
            }],
        },
        "findings_explained": [],
        "unknowns": [{
            "text": "Which spec revision governs build 2.14.0 behavior is unresolved.",
            "kind": "cannot_explain",
            "impact": "capacity planning may rely on a 60s promise the build does not deliver",
            "next_evidence": "vendor confirmation of build-to-spec mapping",
        }],
        "suggested_revisions": [],
        "reflection_prompts": [],
    }
    payload = generate_understanding(_ctx(mats), lambda s, u: (json.dumps(good), {"finish_reason": "stop"}))
    assert payload["generation_status"] == "available"
    ids = [s["id"] for s in payload["sources"]]
    assert "VENDOR" in ids and "MEASURE" in ids


# ---------------------------------------------------------------- markdown

def test_markdown_renders_sections_and_refs():
    payload = generate_understanding(_ctx(_rich_materials()), _invoke_ok)
    md = render_markdown(payload)
    assert "## 1 · 它怎样运转" in md
    assert "## 5 · 还有什么没弄清" in md
    assert "PROBE:4-4" in md
    assert "推演问题" in md
    assert payload["audit_context"]["receipt_hash"] in md


def test_markdown_matches_json_content():
    payload = generate_understanding(_ctx(_rich_materials()), _invoke_ok)
    md = render_markdown(payload)
    # user confirmation state flows into md
    payload["user_notes"]["revision_states"] = [
        {"revision_id": "rev0", "state": "confirmed", "changed_at": "2026-10-07T00:00:00Z"}]
    md2 = render_markdown(payload)
    assert "rev0：confirmed" in md2


# ---------------------------------------------------------------- CLI side exit

def _args(tmp_path, materials=None, before=None, out=None, subject=None):
    return argparse.Namespace(
        file=str(subject or (tmp_path / "subject.md")),
        out=None, json=True, verbose=False, raw=False,
        provider="test", model="test-model", base=None,
        understanding_out=str(out or (tmp_path / "result")),
        understanding_materials=materials,
        understanding_before=before,
    )


def test_cli_side_exit_writes_json_and_md(tmp_path):
    subject = tmp_path / "subject.md"
    subject.write_text(SUBJECT, encoding="utf-8")
    args = _args(tmp_path, materials=str(FIXTURES / "rich" / "materials.json"),
                 before=str(FIXTURES / "rich" / "before.md"), subject=subject)
    payload = cli_side_exit(args, SUBJECT, _review_payload(), _invoke_ok)
    out = pathlib.Path(args.understanding_out)
    assert payload["generation_status"] == "available"
    assert (out / "understanding.json").is_file()
    assert (out / "understanding.md").is_file()
    saved = json.loads((out / "understanding.json").read_text(encoding="utf-8"))
    assert saved["schema_version"] == "falsify.understanding.v1"
    assert saved["user_notes"]["before_recorded"].startswith("我认为周报数字")


def test_cli_side_exit_refuses_overwrite(tmp_path, capsys):
    subject = tmp_path / "subject.md"
    subject.write_text(SUBJECT, encoding="utf-8")
    out = tmp_path / "result"
    out.mkdir()
    (out / "understanding.json").write_text("{}", encoding="utf-8")
    args = _args(tmp_path, subject=subject, out=out)
    payload = cli_side_exit(args, SUBJECT, _review_payload(), _invoke_ok)
    assert payload["generation_status"] == "unavailable"
    assert payload["generation_meta"]["error_category"] == "write_failed"
    assert (out / "understanding.json").read_text(encoding="utf-8") == "{}"
    err = capsys.readouterr().err
    assert "refusing to overwrite" in err


def test_cli_side_exit_rejects_output_aliasing_input(tmp_path):
    subject = tmp_path / "subject.md"
    subject.write_text(SUBJECT, encoding="utf-8")
    # point output dir at a path whose understanding.json would equal the subject file
    args = _args(tmp_path, subject=subject)
    args.understanding_out = str(subject.parent)
    # pre-create to force alias check path: understanding.json does not exist, but
    # subject.md is protected via same-file compare only for exact names; simulate:
    args.file = str(subject.parent / "understanding.json")
    (subject.parent / "understanding.json").unlink(missing_ok=True)
    payload = cli_side_exit(args, SUBJECT, _review_payload(), _invoke_ok)
    assert payload["generation_status"] == "unavailable"
    assert "aliases a protected input" in payload["failure_reason"]


def test_cli_side_exit_materials_error_writes_unavailable(tmp_path):
    subject = tmp_path / "subject.md"
    subject.write_text(SUBJECT, encoding="utf-8")
    args = _args(tmp_path, materials=str(tmp_path / "nope.json"), subject=subject)
    payload = cli_side_exit(args, SUBJECT, _review_payload(), _invoke_ok)
    assert payload["generation_status"] == "unavailable"
    assert payload["generation_meta"]["error_category"] == "materials_invalid"
    out = pathlib.Path(args.understanding_out)
    assert json.loads((out / "understanding.json").read_text(encoding="utf-8"))["generation_status"] == "unavailable"


# ---------------------------------------------------------------- integration: cmd_review

def _full_args(tmp_path, subject, out_dir, materials=None, before=None):
    return argparse.Namespace(
        file=str(subject), against=None, dry_run=False, out=None, json=True,
        verbose=False, raw=False, strict_known_debt_trigger=True,
        provider="deepseek", model="deepseek-chat", base=None,
        risk_tier="normal", claim_scope="document_logic", claim_text="",
        author_id=None, reviewer_id=None, skip_brooks=False,
        understanding_out=str(out_dir),
        understanding_materials=materials,
        understanding_before=before,
    )


def _route_llm_with_understanding(l1_text, model_json):
    calls = {"n": 0}

    def fake_llm(system, user, args, dry_run=False, return_meta=False):
        calls["n"] += 1
        if system == falsify.cli.BROOKS_SYSTEM:
            out = ("BROOKS_MODE: light\n[BROOKS-LINT] ok.\nCutline: Delete\n"
                   "Evidence needed: n/a\nMinimal action: none\nBROOKS_STATUS: RAN")
        elif calls["n"] <= 2:  # L1 skeptic
            out = l1_text
        else:  # understanding call
            out = json.dumps(model_json, ensure_ascii=False)
        if return_meta:
            return out, {"finish_reason": "stop"}
        return out

    return fake_llm, calls


def test_cmd_review_with_understanding_keeps_stdout_single_json(
        monkeypatch, tmp_path, capsys):
    subject = tmp_path / "draft.md"
    subject.write_text(SUBJECT, encoding="utf-8")
    l1 = ("[AGENT-B audit] window not verified.\nCutline: Must Fix\n"
          "Evidence needed: parity check\nMinimal action: add check\nVERDICT: BLOCK")
    fake, calls = _route_llm_with_understanding(l1, GOOD_MODEL_JSON)
    monkeypatch.setattr(falsify.cli, "llm", fake)
    out_dir = tmp_path / "result"
    args = _full_args(tmp_path, subject, out_dir)

    with pytest.raises(SystemExit) as exc:
        falsify.cmd_review(args)
    assert exc.value.args == (1,)

    captured = capsys.readouterr()
    payload = json.loads(captured.out)  # exactly one parseable JSON on stdout
    assert payload["schema_version"] == "falsify.review.v1"
    assert calls["n"] == 3  # brooks + L1 + one understanding call
    assert (out_dir / "understanding.json").is_file()
    assert (out_dir / "understanding.md").is_file()
    u = json.loads((out_dir / "understanding.json").read_text(encoding="utf-8"))
    assert u["audit_context"]["verdict"] == "BLOCK"
    assert u["audit_context"]["receipt_hash"] == receipt_hash(payload)


def test_cmd_review_default_no_understanding_calls(monkeypatch, tmp_path, capsys):
    subject = tmp_path / "draft.md"
    subject.write_text(SUBJECT, encoding="utf-8")
    l1 = ("[AGENT-B audit] window not verified.\nCutline: Must Fix\n"
          "Evidence needed: parity check\nMinimal action: add check\nVERDICT: BLOCK")
    fake, calls = _route_llm_with_understanding(l1, GOOD_MODEL_JSON)
    monkeypatch.setattr(falsify.cli, "llm", fake)
    args = _full_args(tmp_path, subject, tmp_path / "unused")
    args.understanding_out = None
    args.understanding_materials = None
    args.understanding_before = None

    with pytest.raises(SystemExit):
        falsify.cmd_review(args)
    assert calls["n"] == 2  # brooks + L1 only
    assert not (tmp_path / "unused").exists()


def test_cmd_review_dry_run_skips_understanding(monkeypatch, tmp_path, capsys):
    subject = tmp_path / "draft.md"
    subject.write_text(SUBJECT, encoding="utf-8")
    out_dir = tmp_path / "result"
    args = _full_args(tmp_path, subject, out_dir)
    args.dry_run = True
    # Dry-run: brooks dry-runs -> cmd_review returns early; no understanding,
    # no SystemExit, no artifact directory created.
    falsify.cmd_review(args)
    assert not out_dir.exists()


def test_usage_guard_rejects_materials_without_out(tmp_path):
    proc = _run_cli(["review", str(tmp_path / "x.md"), "--json",
                     "--understanding-materials", "m.json"])
    assert proc.returncode != 0
    assert "require" in proc.stderr


def _run_cli(argv):
    import subprocess
    return subprocess.run(
        [sys.executable, "-m", "falsify", *argv],
        capture_output=True, text=True, encoding="utf-8",
        cwd=str(ROOT), timeout=120,
    )


def test_receipt_only_scenario_stays_available_with_unknowns():
    """Only SUBJECT+RECEIPT: model must keep mechanism gaps as unknowns."""
    good = {
        "project_model": {
            "goal": {
                "text": "Subject claims the weekly numbers match the platform.",
                "epistemic_status": "claim",
                "refs": [{"source_id": "SUBJECT", "start_line": 1, "end_line": 1,
                          "quote": "Weekly billing report claims numbers match the platform."}],
            },
            "mechanism_chain": [{
                "text": "Mechanism cannot be reconstructed from the review record alone.",
                "epistemic_status": "unknown", "refs": [],
            }],
            "assumptions": [{
                "text": "Review's Must Fix on window verification is warranted.",
                "epistemic_status": "claim",
                "refs": [{"source_id": "RECEIPT", "start_line": 6, "end_line": 6,
                          "quote": "finding[0] cutline=Must Fix"}],
                "if_wrong": "subject may be fine without parity checks",
            }],
        },
        "findings_explained": [{
            "finding_index": 0,
            "text": "Window verification gap means totals cannot be trusted yet.",
            "epistemic_status": "inference",
            "refs": [{"source_id": "RECEIPT", "start_line": 6, "end_line": 6,
                      "quote": "finding[0] cutline=Must Fix"}],
        }],
        "unknowns": [{
            "text": "How the pipeline actually fetches and transforms rows.",
            "kind": "not_reviewed",
            "impact": "any mechanism claim beyond the document",
            "next_evidence": "architecture or code material",
        }],
        "suggested_revisions": [],
        "reflection_prompts": [],
    }
    payload = generate_understanding(_ctx(), lambda s, u: (json.dumps(good), {"finish_reason": "stop"}))
    assert payload["generation_status"] == "available"
    assert payload["project_model"]["mechanism_chain"][0]["epistemic_status"] == "unknown"


def test_withheld_roundtrip(tmp_path):
    """Export-style withheld source: refs lose quotes but keep ids; validation tolerates."""
    payload = generate_understanding(_ctx(_rich_materials()), _invoke_ok)
    # simulate reader-side withholding of PROBE
    for s in payload["sources"]:
        if s["id"] == "PROBE":
            s["content_state"] = "withheld"
            s["text"] = ""
            s["text_sha256"] = ""
    for f in payload["findings_explained"]:
        for r in f.get("refs", []):
            if r["source_id"] == "PROBE":
                r["quote"] = ""
    errs = validate_understanding(payload, payload["sources"], 2, False)
    assert errs == []
    md = render_markdown(payload)
    assert "省略原文，无法核对" in md
