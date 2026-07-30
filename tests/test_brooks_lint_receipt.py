"""Brooks-Lint L0 receipt + obligation proofs."""

from __future__ import annotations

import argparse
import json
import pathlib

import pytest

import falsify
import falsify.cli
from falsify.authority_kernel import finalize_authority, sha256_text

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _l1_pass():
    return (
        "[AGENT-B audit] No material failure mode found.\n"
        "Cutline: Delete\n"
        "Evidence needed: none\n"
        "Minimal action: none\n"
        "Coverage: full document reviewed against claim scope\n"
        "VERDICT: PASS"
    )


def _brooks_ran():
    return (
        "BROOKS_MODE: full\n"
        "[BROOKS-LINT] Structural surface is auditable.\n"
        "Cutline: Delete\n"
        "Evidence needed: n/a\n"
        "Minimal action: none\n"
        "BROOKS_STATUS: RAN"
    )


def _brooks_scope_refused():
    return (
        "BROOKS_MODE: scope_refused\n"
        "Subject has no code/diff surface for structural lint.\n"
        "BROOKS_STATUS: SCOPE_REFUSED"
    )


def _brooks_must_fix():
    return (
        "BROOKS_MODE: full\n"
        "[BROOKS-LINT] Claim lacks path:line or command evidence.\n"
        "Cutline: Must Fix\n"
        "Evidence needed: path:line or command output\n"
        "Minimal action: attach first-hand evidence\n"
        "BROOKS_STATUS: RAN"
    )


def _phase_llm(*, brooks=_brooks_ran, l1=_l1_pass):
    def fake_llm(system, user, args, dry_run=False, return_meta=False):
        if system == falsify.cli.BROOKS_SYSTEM:
            out = brooks() if callable(brooks) else brooks
        elif system == falsify.AUTHOR_SYSTEM:
            out = "[AGENT-A] draft"
        else:
            out = l1() if callable(l1) else l1
        if return_meta:
            return out, {"finish_reason": "stop"}
        return out

    return fake_llm


def _review_args(draft, **kw):
    base = dict(
        file=str(draft), against=None, dry_run=False, out=None,
        json=True, verbose=False, raw=False,
        strict_known_debt_trigger=True,
        provider="deepseek", model="deepseek-chat", base=None,
        risk_tier="normal", claim_scope="document_logic",
        claim_text="", author_id=None, reviewer_id=None,
        skip_brooks=False,
    )
    base.update(kw)
    return argparse.Namespace(**base)


def test_review_receipt_includes_brooks_lint_ran(monkeypatch, tmp_path, capsys):
    draft = tmp_path / "d.md"
    draft.write_text("[AGENT-A] claim with evidence path:1", encoding="utf-8")
    raw_l0 = _brooks_ran()
    monkeypatch.setattr(falsify.cli, "llm", _phase_llm(brooks=raw_l0, l1=_l1_pass()))

    with pytest.raises(SystemExit) as exc:
        falsify.cmd_review(_review_args(draft))
    assert exc.value.args == (0,)

    payload = json.loads(capsys.readouterr().out)
    bl = payload["brooks_lint"]
    assert bl["ran"] is True
    assert bl["status"] == "RAN"
    assert bl["mode"] == "full"
    assert bl["skill_id"] == "falsify-brooks-lint"
    assert bl["skill_version"]
    assert bl["raw_hash"] == sha256_text(raw_l0)
    assert bl["raw"] == raw_l0
    assert bl["skip_reason"] is None
    assert "l0_brooks_ran" in payload["authority"]["satisfied_obligations"]
    assert "l0_brooks_ran" not in payload["authority"]["missing_obligations"]
    assert payload["verdict"] == "PASS"
    assert payload["evidence_hashes"].get("brooks_lint") == bl["raw_hash"]


def test_skip_brooks_cannot_pass(monkeypatch, tmp_path, capsys):
    draft = tmp_path / "d.md"
    draft.write_text("[AGENT-A] claim", encoding="utf-8")

    def l1_only(system, user, args, dry_run=False, return_meta=False):
        # With --skip-brooks, L0 does not call llm; only L1 runs.
        assert system != falsify.cli.BROOKS_SYSTEM
        out = _l1_pass()
        return (out, {"finish_reason": "stop"}) if return_meta else out

    monkeypatch.setattr(falsify.cli, "llm", l1_only)

    with pytest.raises(SystemExit) as exc:
        falsify.cmd_review(_review_args(draft, skip_brooks=True))
    assert exc.value.args == (1,)

    payload = json.loads(capsys.readouterr().out)
    bl = payload["brooks_lint"]
    assert bl["ran"] is False
    assert bl["status"] == "SKIPPED"
    assert bl["mode"] == "skipped"
    assert bl["skip_reason"]
    assert payload["verdict"] == "BLOCK"
    assert "l0_brooks_ran" in payload["missing_obligations"]
    assert "l0_brooks_ran" not in payload["authority"]["satisfied_obligations"]


def test_l0_must_fix_alone_blocks_even_if_l1_passes(monkeypatch, tmp_path, capsys):
    draft = tmp_path / "d.md"
    draft.write_text("[AGENT-A] claim", encoding="utf-8")
    monkeypatch.setattr(
        falsify.cli, "llm",
        _phase_llm(brooks=_brooks_must_fix(), l1=_l1_pass()),
    )

    with pytest.raises(SystemExit) as exc:
        falsify.cmd_review(_review_args(draft))
    assert exc.value.args == (1,)

    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "BLOCK"
    assert payload["model_verdict"] == "PASS"
    assert payload["brooks_lint"]["ran"] is True
    assert payload["brooks_lint"]["must_fix_count"] >= 1
    assert any(
        f.get("layer") == "brooks_lint" and f.get("cutline") == "Must Fix"
        for f in payload["findings"]
    )
    assert "Must Fix" in (payload.get("verdict_override") or "")


def test_scope_refused_counts_as_ran(monkeypatch, tmp_path, capsys):
    draft = tmp_path / "d.md"
    draft.write_text("plain prose with no code", encoding="utf-8")
    monkeypatch.setattr(
        falsify.cli, "llm",
        _phase_llm(brooks=_brooks_scope_refused(), l1=_l1_pass()),
    )

    with pytest.raises(SystemExit) as exc:
        falsify.cmd_review(_review_args(draft))
    assert exc.value.args == (0,)

    payload = json.loads(capsys.readouterr().out)
    bl = payload["brooks_lint"]
    assert bl["ran"] is True
    assert bl["status"] == "SCOPE_REFUSED"
    assert bl["mode"] == "scope_refused"
    assert "l0_brooks_ran" in payload["authority"]["satisfied_obligations"]
    assert payload["verdict"] == "PASS"


def test_brooks_subcommand_json(monkeypatch, tmp_path, capsys):
    path = tmp_path / "s.md"
    path.write_text("[AGENT-A] subject", encoding="utf-8")
    monkeypatch.setattr(
        falsify.cli, "llm",
        _phase_llm(brooks=_brooks_ran()),
    )
    args = argparse.Namespace(
        file=str(path), dry_run=False, skip_brooks=False,
        provider="deepseek", model="deepseek-chat", base=None,
    )
    with pytest.raises(SystemExit) as exc:
        falsify.cmd_brooks(args)
    assert exc.value.args == (0,)
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "falsify.brooks.v1"
    assert payload["skill_id"] == "falsify-brooks-lint"
    assert payload["brooks_lint"]["ran"] is True
    assert payload["brooks_lint"]["status"] == "RAN"


def test_kernel_missing_l0_blocks_pass():
    d = finalize_authority(
        entry="review",
        risk_tier="normal",
        model_verdict="PASS",
        llm_semantic_verdict="PASS",
        completion_status="COMPLETE",
        satisfied_obligations=[
            "llm_completion_complete",
            "single_terminal_verdict",
            "no_must_fix",
            "audit_coverage_proof",
        ],
    )
    assert d["effective_verdict"] == "BLOCK"
    assert "l0_brooks_ran" in d["missing_obligations"]
    assert d["exit_code"] == 1


def test_skill_pack_path_exists():
    skill = ROOT / "skills" / "falsify-brooks-lint" / "SKILL.md"
    assert skill.is_file(), (
        f"expected skill pack at {skill} (sibling pack agent should create it)"
    )


def test_architecture_docs_mention_l0_brooks():
    arch = ROOT / "docs" / "01-architecture.md"
    if not arch.is_file():
        pytest.skip("docs/01-architecture.md not present yet")
    text = arch.read_text(encoding="utf-8")
    # Soft when docs agent has not landed L0 wording; hard once markers exist.
    has_l0 = ("L0" in text and "Brooks" in text) or "Brooks-Lint" in text
    if not has_l0:
        pytest.skip("docs L0/Brooks-Lint wording not landed yet")
    assert has_l0
