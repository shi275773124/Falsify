"""Anti-rot tests: wiring scanner must RED when claim-bearing paths bypass kernel.

These tests are the decay detector. If someone reintroduces:
  parse_verdict(...) -> sys.exit(EXIT[v])
  or a new cmd_* with bare sys.exit(0)
the scanner and/or these mutations must fail CI.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import textwrap

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_authority_wiring import (  # noqa: E402
    check_cli_wiring,
    check_kernel_purity,
    check_production_adapter,
    run_all_checks,
)


def test_live_tree_authority_wiring_ok():
    failures = run_all_checks()
    assert failures == [], failures


def test_cli_wiring_scanner_clean_on_current_cli():
    assert check_cli_wiring() == []


def test_kernel_purity_holds():
    assert check_kernel_purity() == []


def test_production_adapter_honest_defaults():
    assert check_production_adapter() == []


def test_scanner_detects_bare_sys_exit_in_cmd_review():
    """Mutation: cmd_review exits without kernel → must RED."""
    poisoned = textwrap.dedent(
        '''
        from falsify.authority_kernel import (
            KERNEL_ID, exit_code_for_decision, finalize_authority,
        )
        def adjudicate_llm_audit(*a, **k):
            pass
        def cmd_review(args):
            import sys
            sys.exit(0)
        def cmd_run(args):
            decision = adjudicate_llm_audit()
            import sys
            sys.exit(exit_code_for_decision(decision))
        def cmd_gate(args):
            decision = finalize_authority()
            import sys
            sys.exit(exit_code_for_decision(decision))
        def finish(audit):
            decision = adjudicate_llm_audit()
            import sys
            sys.exit(exit_code_for_decision(decision))
        def die(msg, code=3):
            import sys
            sys.exit(code)
        def cmd_lint(args):
            import sys
            sys.exit(0)
        '''
    )
    # Need markers present
    poisoned = (
        "from falsify.authority_kernel import KERNEL_ID, exit_code_for_decision, finalize_authority\n"
        "adjudicate_llm_audit = None\n"
        + poisoned
    )
    fails = check_cli_wiring(poisoned)
    assert any("bare sys.exit" in f and "cmd_review" in f for f in fails), fails


def test_scanner_detects_exit_parse_verdict_bypass():
    poisoned = textwrap.dedent(
        '''
        from falsify.authority_kernel import KERNEL_ID, exit_code_for_decision, finalize_authority
        adjudicate_llm_audit = None
        EXIT = {"PASS": 0, "BLOCK": 1}
        def parse_verdict(t):
            return "PASS"
        def cmd_review(args):
            import sys
            v = parse_verdict("x")
            sys.exit(EXIT[parse_verdict("x")])
        def cmd_run(args):
            decision = adjudicate_llm_audit()
            import sys
            sys.exit(exit_code_for_decision(decision))
        def cmd_gate(args):
            decision = finalize_authority()
            import sys
            sys.exit(exit_code_for_decision(decision))
        def finish(audit):
            decision = adjudicate_llm_audit()
            import sys
            sys.exit(exit_code_for_decision(decision))
        '''
    )
    fails = check_cli_wiring(poisoned)
    assert any("parse_verdict" in f or "bare sys.exit" in f for f in fails), fails


def test_scanner_detects_missing_kernel_call_on_cmd_gate():
    poisoned = textwrap.dedent(
        '''
        from falsify.authority_kernel import KERNEL_ID, exit_code_for_decision, finalize_authority
        adjudicate_llm_audit = None
        def cmd_review(args):
            decision = adjudicate_llm_audit()
            import sys
            sys.exit(exit_code_for_decision(decision))
        def cmd_run(args):
            decision = adjudicate_llm_audit()
            import sys
            sys.exit(exit_code_for_decision(decision))
        def cmd_gate(args):
            import sys
            sys.exit(0)  # stub green — the original rot
        def finish(audit):
            decision = adjudicate_llm_audit()
            import sys
            sys.exit(exit_code_for_decision(decision))
        '''
    )
    fails = check_cli_wiring(poisoned)
    assert any("cmd_gate" in f for f in fails), fails


def test_scanner_detects_shippable_user_string():
    poisoned = textwrap.dedent(
        '''
        from falsify.authority_kernel import KERNEL_ID, exit_code_for_decision, finalize_authority
        adjudicate_llm_audit = None
        def cmd_review(args):
            decision = adjudicate_llm_audit()
            import sys
            sys.exit(exit_code_for_decision(decision))
        def cmd_run(args):
            decision = adjudicate_llm_audit()
            import sys
            sys.exit(exit_code_for_decision(decision))
        def cmd_gate(args):
            decision = finalize_authority()
            import sys
            sys.exit(exit_code_for_decision(decision))
        def finish(audit):
            decision = adjudicate_llm_audit()
            import sys
            sys.exit(exit_code_for_decision(decision))
        def cmd_lint(args):
            print("SHIPPABLE")
            import sys
            sys.exit(0)
        '''
    )
    fails = check_cli_wiring(poisoned)
    assert any("SHIPPABLE" in f for f in fails), fails


def test_scanner_detects_kernel_import_urllib():
    fails = check_kernel_purity("import urllib\ndef finalize_authority():\n    pass\nKERNEL_ID='x'\n")
    assert any("urllib" in f for f in fails), fails


def test_tools_script_exit_zero_on_live_tree():
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_authority_wiring.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "AUTHORITY_WIRING_OK" in r.stdout


def test_claim_bearing_cmds_still_export_kernel_id_in_payloads():
    """Live import smoke: KERNEL_ID stable marker used by matrix tests."""
    from falsify.authority_kernel import KERNEL_ID
    from falsify.cli import adjudicate_llm_audit, cmd_gate, cmd_review, cmd_run

    assert KERNEL_ID == "falsify.authority_kernel.finalize_authority"
    assert callable(adjudicate_llm_audit)
    assert callable(cmd_review) and callable(cmd_run) and callable(cmd_gate)
