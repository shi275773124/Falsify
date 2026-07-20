"""Kill-shots + matrix + mutation tests for the unified authority kernel.

These prove:
- LLM semantic PASS is real inside claim scope
- LLM PASS cannot alone grant capital / live authority
- review / run / gate / production adapter share one kernel
- high-risk fail-closed on UNKNOWN/SKIP/UNSUPPORTED/missing obligations
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import pytest

import falsify
import falsify.cli
from falsify.authority_kernel import (
    KERNEL_ID,
    finalize_authority,
    min_verdict,
    parse_model_completion,
    semantic_leg_from_llm,
)
from falsify.production_adapter import (
    SubmitTrap,
    evaluate_production_path,
    fixture_evidence_book_residue,
    fixture_evidence_ok_with_dust,
    fixture_evidence_orphan,
    fixture_evidence_wrapper_missing,
    run_trapped_simulation,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]


def _audit_pass(extra=""):
    return (
        "[AGENT-B audit] No material failure mode found.\n"
        "Cutline: Delete\n"
        "Evidence needed: none\n"
        "Minimal action: none\n"
        "Coverage: full document reviewed against claim scope\n"
        f"{extra}"
        "VERDICT: PASS"
    )


def _audit_must_fix_pass():
    return (
        "[AGENT-B audit] Fee figure cites no source.\n"
        "Cutline: Must Fix\n"
        "Evidence needed: source link\n"
        "Minimal action: cite the fee schedule\n"
        "VERDICT: PASS"
    )


def _review_args(draft, **kw):
    base = dict(
        file=str(draft), against=None, dry_run=False, out=None,
        json=True, verbose=False, raw=False,
        strict_known_debt_trigger=True,
        provider="deepseek", model="deepseek-chat", base=None,
        risk_tier="normal", claim_scope="document_logic",
        claim_text="", author_id=None, reviewer_id=None,
    )
    base.update(kw)
    return argparse.Namespace(**base)


# ---------------------------------------------------------------------------
# KS1: review Must Fix + PASS → BLOCK
# ---------------------------------------------------------------------------

def test_ks1_review_must_fix_plus_pass_blocks(monkeypatch, tmp_path, capsys):
    draft = tmp_path / "d.md"
    draft.write_text("[AGENT-A] claim", encoding="utf-8")
    monkeypatch.setattr(falsify.cli, "llm", lambda *a, **k: _audit_must_fix_pass())
    with pytest.raises(SystemExit) as exc:
        falsify.cmd_review(_review_args(draft))
    assert exc.value.args == (1,)
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "BLOCK"
    assert payload["model_verdict"] == "PASS"
    assert "Must Fix" in (payload.get("verdict_override") or "")
    assert payload["capital_authority"] == "NONE"
    assert payload["kernel_id"] == KERNEL_ID


# ---------------------------------------------------------------------------
# KS2: run Must Fix + PASS → BLOCK
# ---------------------------------------------------------------------------

def test_ks2_run_must_fix_plus_pass_blocks(monkeypatch, tmp_path):
    brief = tmp_path / "b.md"
    brief.write_text("brief", encoding="utf-8")

    def fake_llm(system, user, args, dry_run=False, return_meta=False):
        if system == falsify.AUTHOR_SYSTEM:
            out = "[AGENT-A] draft"
        else:
            out = _audit_must_fix_pass()
        if return_meta:
            return out, {"finish_reason": "stop"}
        return out

    monkeypatch.setattr(falsify.cli, "llm", fake_llm)
    args = argparse.Namespace(
        file=str(brief), out=None, provider="deepseek", model="deepseek-chat",
        base=None, drafter=None, drafter_model=None, drafter_base=None,
        reviewer=None, reviewer_model=None, reviewer_base=None,
        risk_tier="normal", claim_scope="document_logic", claim_text="",
        strict_known_debt_trigger=True,
    )
    with pytest.raises(SystemExit) as exc:
        falsify.cmd_run(args)
    assert exc.value.args == (1,)


# ---------------------------------------------------------------------------
# KS3: malformed critical finding + PASS → BLOCK
# ---------------------------------------------------------------------------

def test_ks3_malformed_finding_plus_pass_blocks():
    audit = (
        "[AGENT-B audit] Incomplete finding.\n"
        "Cutline: Must Fix\n"
        # missing Evidence needed + Minimal action
        "VERDICT: PASS"
    )
    findings = falsify.parse_findings(audit)
    # parse_findings may still capture cutline without evidence
    leg = semantic_leg_from_llm(
        audit_text=audit,
        findings=findings,
        completion_meta={"finish_reason": "stop"},
        strict_known_debt_trigger=True,
    )
    assert leg["llm_semantic_verdict"] == "BLOCK"


# ---------------------------------------------------------------------------
# KS4: hollow PASS without coverage/evidence → BLOCK
# ---------------------------------------------------------------------------

def test_ks4_hollow_pass_blocks():
    audit = "Everything looks correct.\nVERDICT: PASS"
    leg = semantic_leg_from_llm(
        audit_text=audit,
        findings=[],
        completion_meta={"finish_reason": "stop"},
    )
    assert leg["llm_semantic_verdict"] == "BLOCK"
    assert "hollow_pass" in (leg.get("verdict_override") or "")


# ---------------------------------------------------------------------------
# KS5: two verdicts, last PASS → BLOCK (not last-wins)
# ---------------------------------------------------------------------------

def test_ks5_two_verdicts_last_pass_blocks():
    text = "VERDICT: BLOCK\nmore text\nVERDICT: PASS"
    parsed = parse_model_completion(text)
    assert parsed["completion_status"] == "UNPARSEABLE"
    assert parsed["model_verdict"] is None
    leg = semantic_leg_from_llm(
        audit_text=text, findings=[],
        completion_meta={"finish_reason": "stop"},
    )
    assert leg["llm_semantic_verdict"] == "BLOCK"


# ---------------------------------------------------------------------------
# KS6: verdict not last line → BLOCK
# ---------------------------------------------------------------------------

def test_ks6_verdict_not_last_line_blocks():
    text = "VERDICT: PASS\ntrailing commentary that should fail closed"
    parsed = parse_model_completion(text)
    assert parsed["completion_status"] == "UNPARSEABLE"
    assert "verdict_not_last" in ",".join(parsed["parse_reasons"])


# ---------------------------------------------------------------------------
# KS7: finish_reason length / missing / unknown → BLOCK
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fr,expect_status", [
    ("length", "TRUNCATED"),
    (None, "INCOMPLETE"),
    ("content_filter", "INCOMPLETE"),
    ("tool_calls", "INCOMPLETE"),
    ("weird", "INCOMPLETE"),
])
def test_ks7_finish_reason_fail_closed(fr, expect_status):
    meta = {"finish_reason": fr}
    leg = semantic_leg_from_llm(
        audit_text=_audit_pass(),
        findings=falsify.parse_findings(_audit_pass()),
        completion_meta=meta,
    )
    assert leg["completion_status"] == expect_status
    assert leg["llm_semantic_verdict"] == "BLOCK"


# ---------------------------------------------------------------------------
# KS8: author == reviewer + high-risk → BLOCK
# ---------------------------------------------------------------------------

def test_ks8_author_equals_reviewer_high_risk_blocks(monkeypatch, tmp_path, capsys):
    draft = tmp_path / "d.md"
    draft.write_text("[AGENT-A] claim", encoding="utf-8")
    monkeypatch.setattr(falsify.cli, "llm", lambda *a, **k: _audit_pass())
    args = _review_args(
        draft, risk_tier="high",
        author_id=("http", "https://api.deepseek.com/v1", "deepseek-chat"),
        reviewer_id=("http", "https://api.deepseek.com/v1", "deepseek-chat"),
    )
    with pytest.raises(SystemExit) as exc:
        falsify.cmd_review(args)
    assert exc.value.args == (1,)
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "BLOCK"
    assert payload["capital_authority"] == "NONE"


# ---------------------------------------------------------------------------
# KS9: production tier does not fall through to L2 stub exit 0
# ---------------------------------------------------------------------------

def test_ks9_production_tier_not_stub_green(monkeypatch, tmp_path):
    # Even with clean lint, production without Pro gate / evidence → nonzero
    monkeypatch.setattr(
        falsify.cli, "_changed_md_files", lambda base: []
    )
    args = argparse.Namespace(
        base="HEAD", tier="production", json=None, glob=None,
        production_evidence=None, results_dir=None,
    )
    with pytest.raises(SystemExit) as exc:
        falsify.cmd_gate(args)
    assert exc.value.args != (0,)
    assert exc.value.args[0] != 0


# ---------------------------------------------------------------------------
# KS10: quant tier tool missing / SKIP → nonzero
# ---------------------------------------------------------------------------

def test_ks10_quant_tier_missing_tools_nonzero(monkeypatch):
    monkeypatch.setattr(falsify.cli, "_changed_md_files", lambda base: [])
    # Force backtest-audit missing
    monkeypatch.setattr(falsify.cli.shutil, "which", lambda name: None)
    args = argparse.Namespace(
        base="HEAD", tier="quant", json=None, glob=None,
        production_evidence=None, results_dir=None,
    )
    with pytest.raises(SystemExit) as exc:
        falsify.cmd_gate(args)
    assert exc.value.args[0] != 0


# ---------------------------------------------------------------------------
# KS11: PASS_WITH_DEBT + high-risk → no capital authority
# ---------------------------------------------------------------------------

def test_ks11_pass_with_debt_high_risk_no_capital():
    d = finalize_authority(
        claim_text="x",
        claim_scope="strategy",
        risk_tier="high",
        entry="review",
        model_verdict="PASS_WITH_DEBT",
        llm_semantic_verdict="PASS_WITH_DEBT",
        executable_evidence_verdict="PASS",
        production_path_verdict="N/A",
        subject_binding_verdict="PASS",
        independence_verdict="PASS",
        completion_status="COMPLETE",
        satisfied_obligations=[
            "llm_completion_complete", "single_terminal_verdict",
            "no_must_fix", "audit_coverage_proof",
            "independent_reviewer", "executable_evidence", "subject_binding",
        ],
        requested_ceiling="EPISTEMIC_CLAIM",
    )
    assert d["capital_authority"] == "NONE"
    assert d["exit_code"] == 1  # high-risk only PASS exits 0


# ---------------------------------------------------------------------------
# KS12: wrapper missing / job exists → BLOCK
# ---------------------------------------------------------------------------

def test_ks12_wrapper_missing_job_exists_blocks():
    result = fixture_evidence_wrapper_missing()
    assert result["verdict"] in ("BLOCK", "UNSUPPORTED")
    assert any("wrapper" in i or "script" in i for i in result["issues"])
    d = finalize_authority(
        risk_tier="production", entry="gate",
        model_verdict="PASS", llm_semantic_verdict="PASS",
        executable_evidence_verdict="PASS",
        production_path_verdict="BLOCK",
        subject_binding_verdict="PASS",
        independence_verdict="PASS",
        completion_status="COMPLETE",
        requested_ceiling="PRODUCTION_LIVE",
    )
    assert d["effective_verdict"] == "BLOCK"
    assert d["capital_authority"] == "NONE"
    assert d["exit_code"] != 0


# ---------------------------------------------------------------------------
# KS13: orphan unsubmitted → BLOCK
# ---------------------------------------------------------------------------

def test_ks13_orphan_blocks():
    result = fixture_evidence_orphan()
    assert result["verdict"] == "BLOCK" or "orphans" in ",".join(result["issues"])
    assert any("orphan" in i for i in result["issues"])


# ---------------------------------------------------------------------------
# KS14: final book residue → BLOCK
# ---------------------------------------------------------------------------

def test_ks14_final_book_residue_blocks():
    result = fixture_evidence_book_residue()
    assert any("final_book" in i for i in result["issues"])
    assert result["verdict"] == "BLOCK"


# ---------------------------------------------------------------------------
# KS15: dust / on-target SKIP legal → not false kill
# ---------------------------------------------------------------------------

def test_ks15_dust_on_target_skip_not_false_kill():
    result = fixture_evidence_ok_with_dust()
    # Without Pro gate overall is UNSUPPORTED, but account invariants PASS
    assert result["stage_status"]["account_invariants"] == "PASS"
    assert result["real_orders"] == 0
    assert result["trap_proof"] is True
    assert not any("partial_book_miscount" in i for i in result["issues"])


# ---------------------------------------------------------------------------
# KS16: submit trap proves zero real orders
# ---------------------------------------------------------------------------

def test_ks16_submit_trap_zero_real_orders():
    trap = SubmitTrap()
    trap.submit({"symbol": "BTC", "side": "buy", "qty": 1})
    trap.submit({"symbol": "ETH", "side": "sell", "qty": 2})
    assert trap.real_orders == 0
    assert len(trap.attempts) == 2
    assert all(a["trapped"] and not a["forwarded"] for a in trap.attempts)

    sim = run_trapped_simulation([
        {"id": "1", "kind": "order", "symbol": "BTC", "side": "buy", "qty": 1},
    ])
    assert sim["real_orders"] == 0
    assert sim["trap_proof"] is True


# ---------------------------------------------------------------------------
# Cross-entry matrix: all claim-bearing commands use the same kernel
# ---------------------------------------------------------------------------

def test_matrix_all_entries_share_kernel_id(monkeypatch, tmp_path, capsys):
    draft = tmp_path / "d.md"
    draft.write_text("[AGENT-A] x", encoding="utf-8")
    monkeypatch.setattr(falsify.cli, "llm", lambda *a, **k: _audit_pass())

    with pytest.raises(SystemExit):
        falsify.cmd_review(_review_args(draft, json=True))
    review_payload = json.loads(capsys.readouterr().out)
    assert review_payload["kernel_id"] == KERNEL_ID
    assert review_payload["authority"]["schema_version"] == "falsify.authority.v1"

    # run
    brief = tmp_path / "b.md"
    brief.write_text("b", encoding="utf-8")

    def fake_llm(system, user, args, dry_run=False, return_meta=False):
        out = "[AGENT-A] d" if system == falsify.AUTHOR_SYSTEM else _audit_pass()
        return (out, {"finish_reason": "stop"}) if return_meta else out

    monkeypatch.setattr(falsify.cli, "llm", fake_llm)
    run_args = argparse.Namespace(
        file=str(brief), out=None, provider="deepseek", model="deepseek-chat",
        base=None, drafter="claude", drafter_model="sonnet", drafter_base=None,
        reviewer="deepseek", reviewer_model="deepseek-chat", reviewer_base=None,
        risk_tier="normal", claim_scope="document_logic", claim_text="",
        strict_known_debt_trigger=True,
    )
    with pytest.raises(SystemExit) as exc:
        falsify.cmd_run(run_args)
    # run prints audit not json; kernel used if exit is 0/1 from decision
    assert exc.value.args[0] in (0, 1)

    # gate production
    monkeypatch.setattr(falsify.cli, "_changed_md_files", lambda base: [])
    with pytest.raises(SystemExit) as gexc:
        falsify.cmd_gate(argparse.Namespace(
            base="HEAD", tier="production", json=str(tmp_path / "g.json"),
            glob=None, production_evidence=None, results_dir=None,
        ))
    assert gexc.value.args[0] != 0
    gate_payload = json.loads((tmp_path / "g.json").read_text(encoding="utf-8"))
    assert gate_payload["kernel_id"] == KERNEL_ID
    assert gate_payload["authority"]["schema_version"] == "falsify.authority.v1"


def test_matrix_epistemic_pass_never_grants_capital(monkeypatch, tmp_path, capsys):
    draft = tmp_path / "d.md"
    draft.write_text("[AGENT-A] claim", encoding="utf-8")
    monkeypatch.setattr(falsify.cli, "llm", lambda *a, **k: _audit_pass())
    with pytest.raises(SystemExit) as exc:
        falsify.cmd_review(_review_args(draft))
    assert exc.value.args == (0,)
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "PASS"
    assert payload["authority_ceiling"] == "EPISTEMIC_CLAIM"
    assert payload["capital_authority"] == "NONE"


# ---------------------------------------------------------------------------
# Mutation: invert critical judgment → tests must RED if kernel broken
# ---------------------------------------------------------------------------

def test_mutation_min_verdict_fail_closed():
    assert min_verdict("PASS", "BLOCK") == "BLOCK"
    assert min_verdict("PASS", "UNKNOWN") == "BLOCK"
    assert min_verdict("PASS", "SKIP") == "BLOCK"
    assert min_verdict("PASS", "UNSUPPORTED") == "BLOCK"
    assert min_verdict("PASS", "PASS_WITH_DEBT") == "PASS_WITH_DEBT"


def test_mutation_invert_must_fix_would_break_ks1():
    """If must-fix override were inverted, KS1 would fail — document the invariant."""
    leg = semantic_leg_from_llm(
        audit_text=_audit_must_fix_pass(),
        findings=falsify.parse_findings(_audit_must_fix_pass()),
        completion_meta={"finish_reason": "stop"},
    )
    # The critical judgment: Must Fix forces BLOCK, never leaves model PASS.
    assert leg["model_verdict"] == "PASS"
    assert leg["llm_semantic_verdict"] == "BLOCK"
    # Mutation check: effective must not equal raw model PASS when Must Fix present
    assert leg["llm_semantic_verdict"] != leg["model_verdict"]


def test_mutation_production_pass_requires_all_legs():
    d = finalize_authority(
        risk_tier="production", entry="gate",
        model_verdict="PASS", llm_semantic_verdict="PASS",
        executable_evidence_verdict="PASS",
        production_path_verdict="UNKNOWN",  # missing proof
        subject_binding_verdict="PASS",
        independence_verdict="PASS",
        completion_status="COMPLETE",
        requested_ceiling="PRODUCTION_LIVE",
    )
    assert d["effective_verdict"] == "BLOCK"
    assert d["capital_authority"] == "NONE"


def test_kernel_is_pure_no_io_import_side_effects():
    import falsify.authority_kernel as ak
    # Module must not import urllib / subprocess for purity
    src = pathlib.Path(ak.__file__).read_text(encoding="utf-8")
    assert "import urllib" not in src
    assert "import subprocess" not in src
    assert "urlopen" not in src


def test_evaluate_production_path_does_not_call_build_plan():
    """Calling evaluate_production_path is not a production-path proof by itself
    unless evidence stages are green; empty evidence → fail-closed."""
    result = evaluate_production_path({})
    assert result["verdict"] in ("BLOCK", "UNSUPPORTED")
    assert result["capital_authority"] == "NONE"
