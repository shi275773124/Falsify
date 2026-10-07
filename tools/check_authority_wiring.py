#!/usr/bin/env python3
"""Anti-rot gate: claim-bearing CLI exits must go through the authority kernel.

Run:
  python tools/check_authority_wiring.py
  python -m pytest tests/test_authority_antirot.py -q

Exit 0 = wiring intact. Exit 1 = decay / bypass detected.

This is a structural check, not a product PASS. It does not grant capital.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "falsify" / "cli.py"
KERNEL_PATH = ROOT / "falsify" / "authority_kernel.py"
ADAPTER_PATH = ROOT / "falsify" / "production_adapter.py"

# Functions that adjudicate claims / emit authority-shaped verdicts.
CLAIM_BEARING_FUNCS = frozenset({
    "cmd_review",
    "cmd_run",
    "cmd_gate",
    "finish",
    "adjudicate_llm_audit",
})

# Static / fatal helpers may exit without kernel.
ALLOWED_BARE_EXIT_FUNCS = frozenset({
    "die",
    "cmd_lint",  # L2 only; must not print PASS/SHIPPABLE
    "cmd_brooks",  # L0-only structural JSON; not claim-bearing authority
    "cmd_draft",
    "cmd_init",
    "main",
})

FORBIDDEN_USER_STRINGS = (
    "SHIPPABLE",
    "NOT shippable",
)

REQUIRED_KERNEL_MARKERS = (
    "from falsify.authority_kernel import",
    "exit_code_for_decision",
    "finalize_authority",
    "KERNEL_ID",
    "adjudicate_llm_audit",
)


class _ExitVisitor(ast.NodeVisitor):
    """Collect sys.exit call sites and whether they use exit_code_for_decision."""

    def __init__(self) -> None:
        self.func_stack: list[str] = []
        self.exits: list[dict] = []
        self.calls_by_func: dict[str, set[str]] = {}
        self.parse_verdict_exit: list[dict] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.func_stack.append(node.name)
        self.calls_by_func.setdefault(node.name, set())
        self.generic_visit(node)
        self.func_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node: ast.Call) -> None:
        fname = self.func_stack[-1] if self.func_stack else "<module>"
        callees = self.calls_by_func.setdefault(fname, set())

        name = _call_name(node.func)
        if name:
            callees.add(name.split(".")[-1])
            callees.add(name)

        if name in ("sys.exit", "exit") or (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "exit"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "sys"
        ):
            via_kernel = False
            if node.args:
                arg0 = node.args[0]
                if isinstance(arg0, ast.Call):
                    inner = _call_name(arg0.func) or ""
                    if inner.endswith("exit_code_for_decision") or inner == "exit_code_for_decision":
                        via_kernel = True
                # die(msg, code=3) style is not claim-bearing when inside die()
            self.exits.append({
                "func": fname,
                "lineno": node.lineno,
                "via_kernel": via_kernel,
                "src": ast.dump(node)[:200],
            })

        # Forbidden: EXIT[parse_verdict(...)]
        if isinstance(node.func, ast.Subscript):
            pass
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        # EXIT[parse_verdict(...)] or EXIT[payload["verdict"]]
        if isinstance(node.value, ast.Name) and node.value.id == "EXIT":
            fname = self.func_stack[-1] if self.func_stack else "<module>"
            # walk for parse_verdict inside slice
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    cn = _call_name(child.func) or ""
                    if cn.endswith("parse_verdict") or cn == "parse_verdict":
                        self.parse_verdict_exit.append({
                            "func": fname,
                            "lineno": node.lineno,
                        })
        self.generic_visit(node)


def _call_name(func: ast.AST) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        base = _call_name(func.value)
        if base:
            return f"{base}.{func.attr}"
        return func.attr
    return None


def check_cli_wiring(cli_src: str | None = None) -> list[str]:
    """Return list of failure messages (empty = OK)."""
    failures: list[str] = []
    src = cli_src if cli_src is not None else CLI_PATH.read_text(encoding="utf-8")

    for marker in REQUIRED_KERNEL_MARKERS:
        if marker not in src:
            failures.append(f"cli.py missing required marker: {marker!r}")

    # Forbidden authority-shaped user strings (allow only in anti-SHIPPABLE comments)
    for bad in FORBIDDEN_USER_STRINGS:
        for i, line in enumerate(src.splitlines(), 1):
            if bad not in line:
                continue
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if "avoids" in line or "avoid" in line.lower() and "SHIPPABLE" in line:
                continue
            if "not" in line.lower() and "SHIPPABLE" in line:
                continue
            # print / f-string emitting SHIPPABLE is forbidden
            if "print" in line or "SHIPPABLE" in line and "f\"" in line or "f'" in line:
                if "SHIPPABLE" in line and ("avoids" in line or "avoid" in line.lower()):
                    continue
                if re.search(r"""['\"]SHIPPABLE['\"]""", line) or "SHIPPABLE if" in line:
                    failures.append(
                        f"cli.py:{i}: forbidden user-facing authority word {bad!r}"
                    )

    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [f"cli.py parse error: {e}"]

    v = _ExitVisitor()
    v.visit(tree)

    for hit in v.parse_verdict_exit:
        failures.append(
            f"cli.py:{hit['lineno']}: EXIT[parse_verdict(...)] bypass in {hit['func']}"
        )

    for ex in v.exits:
        func = ex["func"]
        if func in ALLOWED_BARE_EXIT_FUNCS:
            continue
        if func in CLAIM_BEARING_FUNCS or func.startswith("cmd_"):
            # New cmd_* are claim-bearing by default unless allowlisted
            if func in ALLOWED_BARE_EXIT_FUNCS:
                continue
            if not ex["via_kernel"]:
                # cmd_lint is allowlisted; other cmd_* must use kernel
                if func == "cmd_lint":
                    continue
                failures.append(
                    f"cli.py:{ex['lineno']}: bare sys.exit in claim-bearing "
                    f"{func!r} (must use exit_code_for_decision)"
                )

    # Required callees inside claim-bearing entries
    required = {
        "cmd_review": {"adjudicate_llm_audit", "exit_code_for_decision"},
        "cmd_run": {"adjudicate_llm_audit", "exit_code_for_decision"},
        "cmd_gate": {"finalize_authority", "exit_code_for_decision"},
        "finish": {"adjudicate_llm_audit", "exit_code_for_decision"},
    }
    for func, need in required.items():
        have = v.calls_by_func.get(func, set())
        missing = need - have
        if missing:
            failures.append(
                f"cli.py: {func} missing calls to {sorted(missing)} "
                f"(anti-rot: entry must use authority kernel)"
            )

    # lint must not claim ship authority in output path
    lint_body_calls = v.calls_by_func.get("cmd_lint", set())
    if "finalize_authority" in lint_body_calls or "adjudicate_llm_audit" in lint_body_calls:
        # lint *may* call kernel in future; if it does, capital must stay NONE —
        # for now we only require no SHIPPABLE (checked above).
        pass

    return failures


def check_kernel_purity(kernel_src: str | None = None) -> list[str]:
    failures: list[str] = []
    src = kernel_src if kernel_src is not None else KERNEL_PATH.read_text(encoding="utf-8")
    for bad in ("import urllib", "import subprocess", "urlopen", "requests."):
        if bad in src:
            failures.append(f"authority_kernel.py not pure: contains {bad!r}")
    if "def finalize_authority" not in src:
        failures.append("authority_kernel.py missing finalize_authority")
    if "KERNEL_ID" not in src:
        failures.append("authority_kernel.py missing KERNEL_ID")
    return failures


def check_production_adapter(adapter_src: str | None = None) -> list[str]:
    failures: list[str] = []
    src = (
        adapter_src
        if adapter_src is not None
        else ADAPTER_PATH.read_text(encoding="utf-8")
    )
    if "class SubmitTrap" not in src:
        failures.append("production_adapter.py missing SubmitTrap")
    if "PRO_PRODUCTION_GATE_AVAILABLE" not in src:
        failures.append("production_adapter.py missing PRO_PRODUCTION_GATE_AVAILABLE")
    # Must default to not available (honest OSS)
    if re.search(r"PRO_PRODUCTION_GATE_AVAILABLE\s*=\s*True", src):
        failures.append(
            "production_adapter.py: PRO_PRODUCTION_GATE_AVAILABLE must not be hardcoded True"
        )
    return failures


def run_all_checks() -> list[str]:
    failures: list[str] = []
    if not CLI_PATH.is_file():
        return [f"missing {CLI_PATH}"]
    failures.extend(check_cli_wiring())
    if KERNEL_PATH.is_file():
        failures.extend(check_kernel_purity())
    else:
        failures.append(f"missing {KERNEL_PATH}")
    if ADAPTER_PATH.is_file():
        failures.extend(check_production_adapter())
    else:
        failures.append(f"missing {ADAPTER_PATH}")
    return failures


def main(argv: list[str] | None = None) -> int:
    failures = run_all_checks()
    if failures:
        print("AUTHORITY_WIRING_FAIL")
        for f in failures:
            print(f"  - {f}")
        print(
            "\nAnti-rot: claim-bearing exits must use "
            "exit_code_for_decision(finalize_authority(...))."
        )
        return 1
    print("AUTHORITY_WIRING_OK")
    print(f"  kernel markers present in {CLI_PATH.relative_to(ROOT)}")
    print(f"  claim-bearing: {', '.join(sorted(CLAIM_BEARING_FUNCS))}")
    print("  capital_authority still requires independent formal audit (not this gate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
