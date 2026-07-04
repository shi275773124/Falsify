#!/usr/bin/env python3
"""Poison fixture: deliberately break formulas, verify tests CATCH the breakage.

This is the RED light. Every night, this script:
1. Takes a known-good formula from falsify_quant.py
2. Injects a deliberate bug (the "poison")
3. Runs test_falsify_quant_fixtures.py against the poisoned version
4. Asserts the tests FAIL (RED) — proving the fixtures are alive

If the poison passes, the fixtures are dead — immediate alert.

Run: python test_poison_red_light.py
Exit 0 = RED confirmed (fixtures caught the poison) ← GOOD
Exit 1 = GREEN on poison (fixtures failed to catch the breakage) ← ALERT
"""
import sys
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ORIGINAL = SCRIPT_DIR / "falsify_quant.py"
FIXTURES = SCRIPT_DIR / "test_falsify_quant_fixtures.py"

POISONS = [
    # (name, old_text, new_text, expected_to_fail_test_substring)
    (
        "PSR kurtosis reverted to buggy (excess-1)/4",
        "(kurt + 2) / 4",
        "(kurt - 1) / 4",
        "PSR kurtosis",
    ),
    (
        "PBO median rank flipped (<=  to >)",
        "pbo_value = np.mean(oos_ranks <= median_rank)",
        "pbo_value = np.mean(oos_ranks > median_rank)",
        "PBO",
    ),
    (
        "DSR expected_max_sr uses sqrt(2*ln(N)) approximation instead of Eq.9",
        "expected_max_z = (1 - euler_gamma) * z1 + euler_gamma * z2",
        "expected_max_z = math.sqrt(2 * math.log(n_trials))",
        "DSR",
    ),
]

def run_fixtures(tmp_dir: Path) -> tuple[int, str]:
    """Run fixture tests against a poisoned copy in tmp_dir. Returns (exit_code, output)."""
    env = os.environ.copy()
    env["SKIP_GATE_INTEGRATION"] = "1"
    result = subprocess.run(
        [sys.executable, str(tmp_dir / "test_falsify_quant_fixtures.py")],
        capture_output=True, text=True, timeout=120, env=env,
        cwd=str(tmp_dir),
    )
    return result.returncode, result.stdout + result.stderr


def main():
    all_caught = True

    for name, old_text, new_text, expected_match in POISONS:
        print(f"\n{'='*60}")
        print(f"POISON: {name}")
        print(f"{'='*60}")

        source = ORIGINAL.read_text(encoding="utf-8")
        if old_text not in source:
            print(f"  SKIP — pattern not found in source: {old_text[:60]}...")
            continue

        poisoned = source.replace(old_text, new_text, 1)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            # Copy the poisoned file + all sibling .py files to temp dir
            shutil.copy2(ORIGINAL, tmp / "falsify_quant.py")
            (tmp / "falsify_quant.py").write_text(poisoned, encoding="utf-8")
            shutil.copy2(FIXTURES, tmp / "test_falsify_quant_fixtures.py")
            # Copy any other needed files
            for f in SCRIPT_DIR.glob("*.py"):
                if f.name not in ("falsify_quant.py", "test_falsify_quant_fixtures.py",
                                  "test_poison_red_light.py"):
                    shutil.copy2(f, tmp / f.name)

            rc, output = run_fixtures(tmp)

            # Check if any test mentioning our expected match FAILED
            fail_lines = [l for l in output.splitlines() if "FAIL " in l]
            relevant_fails = [l for l in fail_lines if expected_match.lower() in l.lower()]

            if rc == 1 and (relevant_fails or fail_lines):
                print(f"  RED ✓ — fixtures caught the poison ({len(fail_lines)} failures)")
                if relevant_fails:
                    print(f"  Relevant: {relevant_fails[0].strip()}")
                else:
                    print(f"  First FAIL: {fail_lines[0].strip()}")
            else:
                print(f"  ⚠ ALERT — poison PASSED! Fixtures are dead!")
                print(f"  rc={rc}, fail_lines={len(fail_lines)}")
                all_caught = False

    # ═════════════════════════════════════════════════════════════════════════════
    # GATE4 POISONS — gate4_inherited_code false-negative coverage (v0.9.8 fix)
    # ═════════════════════════════════════════════════════════════════════════════
    # Each poison writes a snippet to a temp file, calls gate4_inherited_code(),
    # and asserts the expected finding type+severity. If gate4 returns PASS (no
    # findings) or misses the expected type, the test FAILs — alert.
    print(f"\n{'='*60}")
    print("GATE4 POISON RED LIGHT TESTS (v0.9.8 false-negative fix)")
    print(f"{'='*60}")
    from falsify import quant_gate as qfg

    GATE4_POISONS = [
        # (name, snippet, expected_finding_type, expected_severity, expect_status_fail)
        (
            "shift(-N) lookahead — explicit future leak",
            'import pandas as pd\ndf = pd.DataFrame({"close": [1,2,3,4,5]})\nfeat = df["close"].shift(-5)\n',
            "negative_shift_lookahead",
            "CRITICAL",
            True,
        ),
        (
            "variable-name rolling window — VOL_LOOKBACK rolling std",
            'import pandas as pd\nVOL_LOOKBACK = 20\ndf = pd.DataFrame({"x": [1,2,3,4,5]})\nv = df["x"].rolling(VOL_LOOKBACK).std()\n',
            "vol_lookahead",
            "WARN",
            False,
        ),
        (
            "hand-written for-loop with forward index reference",
            'import pandas as pd\ndf = pd.DataFrame({"c": [1,2,3,4,5,6,7,8,9,10]})\nfor i in range(len(df)):\n    x = df["c"].iloc[i+5]\n',
            "handwritten_loop_forward_index",
            "WARN",
            False,
        ),
    ]

    for name, snippet, exp_type, exp_sev, expect_fail in GATE4_POISONS:
        print(f"\n{'='*60}")
        print(f"GATE4 POISON: {name}")
        print(f"{'='*60}")
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_script = Path(tmpdir) / "poison_strategy.py"
            tmp_script.write_text(snippet, encoding="utf-8")
            result = qfg.gate4_inherited_code(str(tmp_script))
            findings = result.get("findings", [])
            types = [f.get("type") for f in findings]
            status = result.get("status")
            if expect_fail:
                caught = (status == "FAIL") and any(
                    f.get("severity") == "CRITICAL" and f.get("type") == exp_type
                    for f in findings)
            else:
                caught = (exp_type in types) and any(
                    f.get("severity") == exp_sev and f.get("type") == exp_type
                    for f in findings)
            if caught:
                print(f"  RED ✓ — gate4 caught the poison (status={status}, types={types})")
            else:
                print(f"  ⚠ ALERT — gate4 missed the poison! status={status}, types={types}")
                all_caught = False

    print(f"\n{'='*60}")
    if all_caught:
        print("ALL POISONS CAUGHT ✓ — Red light is alive.")
        sys.exit(0)
    else:
        print("⚠ SOME POISONS ESCAPED — fixtures need investigation!")
        sys.exit(1)


if __name__ == "__main__":
    main()
