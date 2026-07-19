#!/usr/bin/env python3
"""Quant Falsify Gate — automated backtest methodology checker.

Implements L0-L5 of the Falsify v2 pipeline (L6 execution sim + L7 live are separate):
  L0  gate0_contract       — research contract presence + schema validation
  L2  gate1_backtest_audit — AST static analysis (backtest-audit)
  L1  gate2_survivorship   — universe PIT / survivorship bias detection
  L3  gate3_numeric_recompute — independent SR re-computation + formula audit
  L2  gate4_inherited_code — known bug pattern detection (expm1, lookahead, etc.)

Verdict uses a terminal-path claim-ceiling system, not binary PASS/FAIL:
  BLOCK                    — formula/timing/data invalid; results cannot be cited
  CANDIDATE_NEEDS_NEXT_GATE — alpha direction may exist; one decisive next gate required
  PASS_TO_PAPER            — all automated gates pass; eligible for paper/pilot path

Usage:
  python -m falsify.quant_gate --script strategy.py --contract contract.yaml --results-dir results/

Output: JSON with gate-by-gate verdict + claim_ceiling.
"""
from __future__ import annotations
import argparse
import ast
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

# ─── Gate 0: Research Contract (L0) ────────────────────────────────────────────

REQUIRED_CONTRACT_FIELDS = {
    "strategy_id": str,
    "hypothesis": str,
    "universe_rule": dict,
    "signal_time": str,
    "execution_time": str,
    "cost_model": dict,
    "parameter_family": dict,
    "claim_ceiling": dict,
    "terminal_path": dict,
    "strategy_object": dict,
}

REQUIRED_TERMINAL_PATH_FIELDS = (
    "next_gate",
    "deadline_or_sample_target",
    "pass_path",
    "fail_action",
)

REQUIRED_STRATEGY_OBJECT_FIELDS = (
    "signal_core_path",
    "production_binding",
    "execution_replay",
    "reconciliation_evidence",
)

CANONICAL_FORBIDDEN_SOURCES = (
    "current_fact_sheet",
    "current_listing",
    "current_asset_class",
    "current_volume",
    "future_missingness",
    "same_window_best_pick",
)

CLAIM_CEILING_ORDER = {
    "BLOCK": 0,
    "DIAGNOSTIC_ONLY": 1,
    "STATISTICAL_SCREEN_ONLY": 2,
    "CANDIDATE_NEEDS_NEXT_GATE": 3,
    "CLEAN_RESEARCH_CANDIDATE": 4,
    "PASS_TO_PAPER": 5,
}

def _load_mapping(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError as e:
            raise RuntimeError("PyYAML required for YAML manifest/contract") from e
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a mapping/dict")
    return data

def _restrict_ceiling(current: str, cap: str) -> str:
    if current not in CLAIM_CEILING_ORDER:
        return cap
    if cap not in CLAIM_CEILING_ORDER:
        return current
    return current if CLAIM_CEILING_ORDER[current] <= CLAIM_CEILING_ORDER[cap] else cap

def build_falsify_manifest(*, run_id: str, strategy_family_id: str, rule_hash: str,
                           data_manifest_hash: str, window_id: str,
                           forbidden_sources: list[str] | None = None,
                           allowed_sources: list[str] | None = None,
                           known_contamination: list[str] | None = None,
                           read_path_policy: str = "declared_only",
                           claim_ceiling: str = "STATISTICAL_SCREEN_ONLY",
                           synthetic: dict | None = None,
                           variant_family: dict | None = None) -> dict:
    """Build the minimal Falsify v1.0 MANIFEST.json shape.

    The manifest is intentionally compact: it records the information boundary,
    variant family, synthetic-test status, and claim ceiling in one file instead
    of multiplying artifacts.
    """
    return {
        "manifest_version": "falsify_v1_boundary_alpha",
        "run_id": run_id,
        "strategy_family_id": strategy_family_id,
        "rule_hash": rule_hash,
        "data_manifest_hash": data_manifest_hash,
        "window_id": window_id,
        "variant_family": variant_family or {},
        "information_boundary": {
            "allowed_sources": allowed_sources or [],
            "forbidden_sources": forbidden_sources or list(CANONICAL_FORBIDDEN_SOURCES),
            "known_contamination": known_contamination or [],
            "read_path_policy": read_path_policy,
        },
        "synthetic": synthetic or {"is_synthetic": False, "generator_manifest": None, "artifact_probe": None},
        "claim_ceiling": claim_ceiling,
    }

def validate_falsify_manifest(manifest: dict) -> dict:
    """Validate Falsify v1.0 boundary manifest and return harness verdict.

    This is a harness-boundary check, not a metric check. Metric PASS with
    harness DIRTY becomes DIRTY_PASS_BLOCK_FOR_PROMOTION.
    """
    issues: list[dict] = []
    info = manifest.get("information_boundary")
    if not isinstance(info, dict):
        return {
            "gate": "harness_boundary",
            "status": "WARN",
            "harness_verdict": "NOT_TESTED",
            "claim_ceiling_cap": "STATISTICAL_SCREEN_ONLY",
            "issues": [{"code": "MISSING_INFORMATION_BOUNDARY", "severity": "WARN"}],
        }

    forbidden = info.get("forbidden_sources", [])
    if not isinstance(forbidden, list):
        issues.append({"code": "FORBIDDEN_SOURCES_NOT_LIST", "severity": "FAIL"})
        forbidden_set = set()
    else:
        forbidden_set = {str(x) for x in forbidden}
    missing = [x for x in CANONICAL_FORBIDDEN_SOURCES if x not in forbidden_set]
    if missing:
        issues.append({"code": "MISSING_CANONICAL_FORBIDDEN_SOURCES", "severity": "FAIL", "missing": missing})

    known = info.get("known_contamination", []) or []
    if not isinstance(known, list):
        issues.append({"code": "KNOWN_CONTAMINATION_NOT_LIST", "severity": "FAIL"})
        known = []
    known_set = {str(x) for x in known}
    if known_set:
        severity = "FAIL" if "same_window_best_pick" in known_set else "WARN"
        issues.append({"code": "KNOWN_CONTAMINATION", "severity": severity, "channels": sorted(known_set)})

    read_policy = str(info.get("read_path_policy", "")).strip()
    if read_policy not in {"declared_only", "audit_logged", "sandboxed"}:
        issues.append({"code": "BAD_READ_PATH_POLICY", "severity": "FAIL", "actual": read_policy})

    syn = manifest.get("synthetic", {}) or {}
    if not isinstance(syn, dict):
        issues.append({"code": "SYNTHETIC_NOT_MAPPING", "severity": "FAIL"})
    elif syn.get("is_synthetic") and not syn.get("generator_manifest"):
        issues.append({"code": "SYNTHETIC_GENERATOR_MANIFEST_MISSING", "severity": "WARN"})

    if any(i.get("severity") == "FAIL" for i in issues):
        return {"gate": "harness_boundary", "status": "FAIL", "harness_verdict": "FAIL",
                "claim_ceiling_cap": "BLOCK", "issues": issues}
    if any(i.get("code") == "KNOWN_CONTAMINATION" for i in issues):
        return {"gate": "harness_boundary", "status": "WARN", "harness_verdict": "DIRTY",
                "claim_ceiling_cap": "DIAGNOSTIC_ONLY", "issues": issues}
    if issues:
        return {"gate": "harness_boundary", "status": "WARN", "harness_verdict": "NOT_TESTED",
                "claim_ceiling_cap": "DIAGNOSTIC_ONLY", "issues": issues}
    return {"gate": "harness_boundary", "status": "PASS", "harness_verdict": "PASS",
            "claim_ceiling_cap": "PASS_TO_PAPER", "issues": []}

def gate_harness_boundary(manifest_path: str, results_dir: str = "") -> dict:
    """Load MANIFEST.json and validate harness information boundary.

    If --manifest is omitted, try <results-dir>/MANIFEST.json. Missing manifest
    is NOT_TESTED and caps claims at STATISTICAL_SCREEN_ONLY for L1+/formal use.
    """
    candidate = Path(manifest_path) if manifest_path else (Path(results_dir) / "MANIFEST.json" if results_dir else None)
    if not candidate or not candidate.exists():
        return {
            "gate": "harness_boundary",
            "status": "WARN",
            "harness_verdict": "NOT_TESTED",
            "claim_ceiling_cap": "STATISTICAL_SCREEN_ONLY",
            "issues": [{"code": "MANIFEST_MISSING", "severity": "WARN", "path": str(candidate) if candidate else ""}],
        }
    try:
        manifest = _load_mapping(candidate)
    except Exception as e:
        return {"gate": "harness_boundary", "status": "FAIL", "harness_verdict": "FAIL",
                "claim_ceiling_cap": "BLOCK", "issues": [{"code": "MANIFEST_PARSE_ERROR", "detail": str(e)}]}
    result = validate_falsify_manifest(manifest)
    result["manifest_path"] = str(candidate)
    return result

def _metric_verdict_from_ceiling(claim_ceiling: str) -> str:
    if str(claim_ceiling).startswith("PASS"):
        return "PASS"
    if claim_ceiling == "BLOCK":
        return "BLOCK"
    return "FAIL"

def _final_verdict(metric_verdict: str, harness_verdict: str, claim_ceiling: str) -> str:
    if claim_ceiling == "BLOCK" or harness_verdict == "FAIL":
        return "BLOCK"
    if metric_verdict == "PASS" and harness_verdict == "DIRTY":
        return "DIRTY_PASS_BLOCK_FOR_PROMOTION"
    if metric_verdict == "PASS" and harness_verdict == "NOT_TESTED":
        return "METRIC_PASS_HARNESS_NOT_TESTED"
    if harness_verdict == "DIRTY":
        return "DIRTY_CANDIDATE_BLOCK_FOR_PROMOTION"
    return claim_ceiling

def _self_test_boundary() -> int:
    tests = []
    def add(name, manifest, exp_status, exp_harness):
        res = validate_falsify_manifest(manifest)
        ok = res["status"] == exp_status and res["harness_verdict"] == exp_harness
        tests.append((name, ok, res))
    add("good_clean_l2_manifest", build_falsify_manifest(
        run_id="good", strategy_family_id="fam", rule_hash="r", data_manifest_hash="d", window_id="w"), "PASS", "PASS")
    bad_missing = build_falsify_manifest(run_id="m", strategy_family_id="fam", rule_hash="r", data_manifest_hash="d", window_id="w")
    bad_missing.pop("information_boundary")
    add("missing_information_boundary", bad_missing, "WARN", "NOT_TESTED")
    dirty = build_falsify_manifest(run_id="dirty", strategy_family_id="fam", rule_hash="r", data_manifest_hash="d", window_id="w", known_contamination=["current_fact_sheet"])
    add("dirty_current_fact_sheet_metric_pass", dirty, "WARN", "DIRTY")
    same_window = build_falsify_manifest(run_id="best", strategy_family_id="fam", rule_hash="r", data_manifest_hash="d", window_id="w", known_contamination=["same_window_best_pick"])
    add("same_window_best_pick_dirty", same_window, "FAIL", "FAIL")
    synth = build_falsify_manifest(run_id="syn", strategy_family_id="fam", rule_hash="r", data_manifest_hash="d", window_id="w", synthetic={"is_synthetic": True})
    add("synthetic_no_generator_manifest", synth, "WARN", "NOT_TESTED")

    for name, ok, res in tests:
        print(("PASS" if ok else "FAIL"), name, json.dumps(res, ensure_ascii=False, sort_keys=True))
    return 0 if all(ok for _, ok, _ in tests) else 1

def _filled(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        v = value.strip()
        return bool(v) and not (v.startswith("{") and v.endswith("}")) and v.lower() not in {"todo", "tbd", "none", "n/a"}
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True

def gate0_contract(contract_path: str) -> dict:
    """Validate research contract exists and has required fields.

    The contract freezes the experiment before any code runs:
    - hypothesis (what edge are we testing?)
    - universe_rule (how is the tradable set defined, PIT?)
    - signal/execution timing (t vs t+1)
    - cost_model (fee/slippage assumptions)
    - parameter_family (what params will be searched)
    - claim_ceiling (what verdicts are allowed under what conditions)
    - terminal_path (the decisive next gate; no indefinite candidate parking)
    - strategy_object (canonical signal core + production parity evidence)

    No contract = CONTRACT_REQUIRED, backtest cannot be audited.
    """
    if not contract_path:
        return {"gate": "contract", "status": "FAIL",
                "detail": "No --contract provided. Research must be frozen before backtest.",
                "claim_ceiling": "BLOCK"}

    p = Path(contract_path)
    if not p.exists():
        return {"gate": "contract", "status": "FAIL",
                "detail": f"Contract file not found: {contract_path}",
                "claim_ceiling": "BLOCK"}

    try:
        text = p.read_text(encoding="utf-8")
        # Support YAML and JSON
        if p.suffix in (".yaml", ".yml"):
            try:
                import yaml
                data = yaml.safe_load(text)
            except ImportError:
                return {"gate": "contract", "status": "ERROR",
                        "detail": "PyYAML not installed; use .json contract or pip install pyyaml",
                        "claim_ceiling": "BLOCK"}
        else:
            data = json.loads(text)
    except Exception as e:
        return {"gate": "contract", "status": "FAIL",
                "detail": f"Cannot parse contract: {e}",
                "claim_ceiling": "BLOCK"}

    if not isinstance(data, dict):
        return {"gate": "contract", "status": "FAIL",
                "detail": "Contract must be a mapping/dict",
                "claim_ceiling": "BLOCK"}

    missing = []
    wrong_type = []
    for field, expected_type in REQUIRED_CONTRACT_FIELDS.items():
        if field not in data:
            missing.append(field)
        elif not isinstance(data[field], expected_type):
            wrong_type.append(f"{field} (expected {expected_type.__name__})")

    findings = []
    if missing:
        findings.append({"type": "missing_fields", "fields": missing})
    if wrong_type:
        findings.append({"type": "wrong_type", "fields": wrong_type})

    # Check claim_ceiling has enforceable rules
    cc = data.get("claim_ceiling", {})
    if not isinstance(cc, dict) or not cc:
        findings.append({"type": "empty_claim_ceiling",
                         "detail": "claim_ceiling must define enforceable rules, e.g. {pbo_ge_0_30: candidate_needs_next_gate}"})

    terminal_path = data.get("terminal_path", {})
    if isinstance(terminal_path, dict):
        missing_terminal = [k for k in REQUIRED_TERMINAL_PATH_FIELDS if not _filled(terminal_path.get(k))]
        if missing_terminal:
            findings.append({"type": "incomplete_terminal_path",
                             "fields": missing_terminal,
                             "detail": "CANDIDATE_NEEDS_NEXT_GATE must name one decisive next_gate plus deadline/sample target, pass_path, and fail_action; otherwise it is a parking lot."})
    strategy_object = data.get("strategy_object", {})
    if isinstance(strategy_object, dict):
        missing_strategy_object = [k for k in REQUIRED_STRATEGY_OBJECT_FIELDS if not _filled(strategy_object.get(k))]
        if missing_strategy_object:
            findings.append({"type": "incomplete_strategy_object",
                             "fields": missing_strategy_object,
                             "detail": "Backtest must identify the same strategy object intended for production: signal core, production binding, execution replay, reconciliation evidence."})

    # Check universe_rule has PIT indicator
    # Use explicit whitelist, not substring match — "spinner" contains "pit"
    PIT_SOURCES = {
        "pit", "point_in_time", "venue_markets_pit", "binance_perp_pit",
        "lean", "quantrocket", "portfolio123",
    }
    ur = data.get("universe_rule", {})
    if isinstance(ur, dict):
        source = ur.get("source", "").lower().strip()
        if source not in PIT_SOURCES:
            findings.append({"type": "universe_not_pit",
                             "detail": f"universe_rule.source='{source}' — must be a recognized PIT source: {sorted(PIT_SOURCES)}"})

    if findings:
        return {"gate": "contract", "status": "FAIL", "findings": findings,
                "claim_ceiling": "BLOCK"}
    return {"gate": "contract", "status": "PASS", "findings": [],
            "claim_ceiling": data.get("claim_ceiling", {})}


# ─── Gate 1: backtest-audit (AST static analysis, L2) ─────────────────────────

def gate1_backtest_audit(script_path: str) -> dict:
    """Run backtest-audit on the script. Returns issues list."""
    try:
        result = subprocess.run(
            ["backtest-audit", "check", script_path, "--format", "json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode not in (0, 1):
            return {"gate": "backtest_audit", "status": "ERROR", "detail": result.stderr[:500]}
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"gate": "backtest_audit", "status": "SKIP", "detail": "backtest-audit not installed or no JSON output"}
        issues = []
        for _fname, findings in data.items():
            for f in findings:
                issues.append({
                    "code": f.get("code", ""),
                    "message": f.get("message", ""),
                    "line": f.get("line", 0),
                    "severity": f.get("severity", "warning"),
                })
        # Filter false positives: STAT002 fires even when cost variables exist
        # but use non-standard names. Re-check by looking for cost/bps/commission
        # in the source.
        source = Path(script_path).read_text(encoding="utf-8")
        has_cost = bool(re.search(r'(cost|bps|commission|fee|slippage)\s*=\s*\d', source, re.IGNORECASE))
        if has_cost:
            issues = [i for i in issues if i["code"] != "STAT002"]

        # backtest-audit distinguishes warning vs error. Error-class issues
        # (e.g. LAB002 negative pct_change / lookahead leakage) must block the
        # backtest, not merely cap it at CANDIDATE_NEEDS_NEXT_GATE. Treat unknown severity
        # conservatively as warning, but any explicit error is FAIL.
        if any(str(i.get("severity", "")).lower() == "error" for i in issues):
            status = "FAIL"
        elif issues:
            status = "WARN"
        else:
            status = "PASS"
        return {"gate": "backtest_audit", "status": status, "issues": issues}
    except FileNotFoundError:
        return {"gate": "backtest_audit", "status": "SKIP", "detail": "backtest-audit not installed (pip install backtest-audit)"}
    except Exception as e:
        return {"gate": "backtest_audit", "status": "ERROR", "detail": str(e)[:300]}


# ─── Gate 2: Universe survivorship bias detection ──────────────────────────────

def gate2_survivorship(script_path: str) -> dict:
    """Detect end-of-panel universe selection (survivorship bias).

    Scans the script source for patterns like:
      - qvol.iloc[-N:].mean()  (selects by end-of-period volume)
      - volume.iloc[-N:]       (same)
      - .tail(N)               (same)

    Also checks if universe selection happens BEFORE the backtest loop
    (static universe) vs inside the loop (point-in-time dynamic universe).
    """
    source = Path(script_path).read_text(encoding="utf-8")
    findings = []

    # Pattern 1: end-of-panel volume selection
    end_panel_patterns = [
        (r'(\w+)\.iloc\[-(\d+):\]\.mean\(\)', "end_of_panel_volume_select"),
        (r'(\w+)\.tail\((\d+)\)\.mean\(\)', "tail_volume_select"),
    ]
    for pattern, label in end_panel_patterns:
        for m in re.finditer(pattern, source):
            line_num = source[:m.start()].count('\n') + 1
            findings.append({
                "type": label,
                "line": line_num,
                "match": m.group(0),
                "detail": "Universe selected by end-of-panel data → survivorship + look-ahead listing bias"
            })

    # Pattern 2: static universe (selected once, outside loop)
    # Heuristic: if there's a `top50 = ...` or `selected = ...` before the
    # main backtest loop, and the loop uses that pre-selected list
    # without re-filtering per timestep, that's a static universe.
    has_static_universe = False
    for m in re.finditer(r'(top\d+|selected|universe|eligible_symbols)\s*=\s*.*\.head\(', source):
        # Check if this is inside a function that's called once (not per-timestep)
        line_num = source[:m.start()].count('\n') + 1
        context = source[max(0, m.start()-200):m.start()+200]
        if 'def load' in context or 'return' in context[m.end()-m.start():]:
            has_static_universe = True
            findings.append({
                "type": "static_universe",
                "line": line_num,
                "match": m.group(0),
                "detail": "Universe selected once outside loop → not point-in-time"
            })

    # Pattern 3: check if universe filter inside loop uses iloc[:t+1] (PIT) or full data (lookahead)
    pit_filter = re.search(r'iloc\[:t\s*\+\s*1\]', source)
    full_data_filter = re.search(r'\.iloc\[-1\].*volume', source)  # uses latest volume for all timesteps

    if findings:
        return {"gate": "survivorship", "status": "FAIL", "findings": findings,
                "note": "OOS with this universe construction is UNUSABLE for both promotion AND falsification"}
    elif not pit_filter and has_static_universe:
        return {"gate": "survivorship", "status": "WARN", "findings": [],
                "note": "No point-in-time filter (iloc[:t+1]) detected — verify universe is dynamic"}
    else:
        return {"gate": "survivorship", "status": "PASS", "findings": []}


# ─── Gate 3: Numeric re-computation gate ───────────────────────────────────────

def _gate3_recompute_from_csv(f: Path) -> dict | None:
    """Recompute SR/cum/MaxDD from a daily returns CSV. Returns finding dict or None."""
    import pandas as pd
    df = pd.read_csv(f)
    ret_col = None
    for col in ['ret_simple', 'ret', 'returns', 'daily_ret', 'pnl']:
        if col in df.columns:
            ret_col = col
            break
    if ret_col is None:
        return None
    rets = df[ret_col].dropna().values
    if len(rets) < 10:
        return None
    mean = float(rets.mean()) * 365
    std = float(rets.std(ddof=1)) * math.sqrt(365)
    sr = mean / std if std > 0 else 0
    cum = float((1 + pd.Series(rets)).prod() - 1)
    equity = (1 + pd.Series(rets)).cumprod()
    peak = equity.cummax()
    max_dd_pct = float(((peak - equity) / peak).max() * 100) if len(rets) > 0 else 0.0
    return {
        "file": f.name,
        "n_days": len(rets),
        "recomputed_sr": round(sr, 4),
        "recomputed_cum_pct": round(cum * 100, 2),
        "recomputed_max_dd_pct": round(max_dd_pct, 2),
        "method": "arithmetic (mean*365 / (std*sqrt(365)))"
    }


def _gate3_scan_reported(summary_files: list) -> list:
    """Scan summary.json files for reported SR/cum values."""
    reported = []
    for sf in summary_files:
        try:
            data = json.loads(sf.read_text(encoding="utf-8"))
            for key in ['metrics', 'oos_5y', 'combos_pit']:
                if key in data:
                    metrics = data[key]
                    if isinstance(metrics, list):
                        for m in metrics:
                            if isinstance(m, dict) and 'sharpe' in m:
                                reported.append({
                                    "reported_in": sf.name,
                                    "label": m.get('label', ''),
                                    "reported_sr": m.get('sharpe'),
                                    "reported_cum": m.get('cum_ret_pct'),
                                })
                    elif isinstance(metrics, dict) and 'sharpe' in metrics:
                        reported.append({
                            "reported_in": sf.name,
                            "reported_sr": metrics.get('sharpe'),
                            "reported_cum": metrics.get('cum_ret_pct'),
                        })
        except (json.JSONDecodeError, ValueError) as e:
            reported.append({
                "reported_in": sf.name,
                "summary_parse_error": str(e)[:200],
            })
        except Exception as e:
            reported.append({
                "reported_in": sf.name,
                "summary_parse_error": f"unexpected {type(e).__name__}: {str(e)[:150]}",
            })
    return reported


def _gate3_scan_expm1(results_dir: str) -> list:
    """Scan scripts in results_dir parent for expm1 annualization bug pattern."""
    findings = []
    script_dir = Path(results_dir).parent
    for py in script_dir.glob("*.py"):
        try:
            source = py.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # A sibling script with a non-UTF-8 encoding is not evidence of an
            # expm1 pattern; skip it rather than aborting the entire gate.
            continue
        for line_num, line in enumerate(source.splitlines(), 1):
            if "expm1" in line and ("mean" in line or "sum" in line):
                findings.append({
                    "file": py.name,
                    "line": line_num,
                    "BUG": "expm1 annualization detected — inflates/deflates SR. Replace with arithmetic mean*365"
                })
    return findings


def _gate3_compare_sr(findings: list) -> list:
    """Compare recomputed SR vs reported SR, flag mismatches."""
    recomputed = [f for f in findings if "recomputed_sr" in f]
    reported = [f for f in findings if "reported_sr" in f]
    mismatches = []
    for rep in reported:
        rep_sr = rep.get("reported_sr")
        rep_cum = rep.get("reported_cum")
        rep_label = rep.get("label", "")
        if rep_sr is None:
            continue
        best_match = None
        for rec in recomputed:
            rec_label = rec.get("file", "").replace("_daily.csv", "")
            if rep_label and rep_label in rec_label:
                best_match = rec
                break
            if rep_cum is not None and "recomputed_cum_pct" in rec:
                if abs(rec["recomputed_cum_pct"] - rep_cum) < 5.0:
                    best_match = rec
                    break
        if best_match:
            rec_sr = best_match["recomputed_sr"]
            diff = abs(rec_sr - rep_sr)
            if diff > 0.1:
                mismatches.append({
                    "type": "sr_mismatch",
                    "file": best_match.get("file", ""),
                    "label": rep_label,
                    "recomputed_sr": rec_sr,
                    "reported_sr": rep_sr,
                    "difference": round(diff, 4),
                    "BUG": f"Recomputed SR ({rec_sr}) differs from reported SR ({rep_sr}) by {diff:.4f} — exceeds 0.1 tolerance"
                })
    return mismatches


def gate3_numeric_recompute(results_dir: str) -> dict:
    """Re-compute Sharpe ratio from daily returns CSV.

    Looks for any *_daily.csv or *_daily.json in results_dir,
    extracts daily returns, re-computes SR with arithmetic annualization,
    compares to reported value in summary.json.
    """
    rdir = Path(results_dir)
    if not rdir.exists():
        return {"gate": "numeric_recompute", "status": "SKIP", "detail": f"results dir not found: {results_dir}"}

    daily_files = list(rdir.glob("*daily*.csv")) + list(rdir.glob("*daily*.json"))
    if not daily_files:
        return {"gate": "numeric_recompute", "status": "WARN",
                "detail": "No daily returns CSV found — cannot verify SR"}

    findings = []
    for f in daily_files:
        try:
            if f.suffix == ".csv":
                result = _gate3_recompute_from_csv(f)
                if result:
                    findings.append(result)
        except Exception as e:
            findings.append({"file": f.name, "error": str(e)[:200]})

    # Collect reported values
    summary_files = list(rdir.glob("summary*.json"))
    findings.extend(_gate3_scan_reported(summary_files))

    # expm1 contamination scan
    findings.extend(_gate3_scan_expm1(results_dir))

    # Compare recomputed vs reported
    findings.extend(_gate3_compare_sr(findings))

    status = "PASS"
    if any("BUG" in f for f in findings):
        status = "FAIL"
    elif not findings:
        status = "WARN"

    return {"gate": "numeric_recompute", "status": status, "findings": findings}


# ─── Gate 4: Inherited code contamination ──────────────────────────────────────

def gate4_inherited_code(script_path: str) -> dict:
    """Check for known bug patterns that propagate via copy-paste.

    Patterns checked:
      - expm1(mean*365) or expm1(sum) — wrong annualization
      - rolling(N).std() without shift(1) — vol lookahead (minor but flaggable)
      - score.loc[dt] AND log_ret.loc[dt] in same loop — signal-return same-timestamp lookahead
    """
    source = Path(script_path).read_text(encoding="utf-8")
    findings = []

    # expm1 annualization bug. Broad line-level check catches np.expm1(ret.mean()*365),
    # math.expm1(np.mean(x)*365), expm1(sum(...)), etc. This intentionally favors
    # false positives over missing the historical SR inflation/deflation bug.
    for line_num, line in enumerate(source.splitlines(), 1):
        if "expm1" in line and ("mean" in line or "sum" in line):
            findings.append({
                "type": "expm1_annualization",
                "line": line_num,
                "severity": "CRITICAL",
                "detail": "expm1(mean/sum annualization) inflates/deflates Sharpe ratio. Use arithmetic: mean*365 / (std*sqrt(365))"
            })

    # vol rolling without shift(1) — check context
    # Loosened regex catches ANY rolling() arg (literal, variable name, kwargs) not just literal ints.
    # Balaena gate4 false-negative fix: previously only rolling(20).std() was caught, blind to rolling(VOL_LOOKBACK).
    for m in re.finditer(r'\.rolling\([^)]*\)\.(?:std|mean|var|agg|apply|quantile)\(', source):
        line_num = source[:m.start()].count('\n') + 1
        line_end = source.find('\n', m.end())
        context = source[m.start():line_end+1] if line_end > 0 else source[m.start():]
        if '.shift(1)' not in context and '.shift(1)' not in source[max(0,m.start()-50):m.start()+100]:
            findings.append({
                "type": "vol_lookahead",
                "line": line_num,
                "severity": "WARN",
                "detail": "rolling().agg() without shift(1) — vol includes current bar's return (lookahead risk, esp. with variable-name windows)"
            })

    # shift(-N) — explicit future leak. Almost always lookahead in feature engineering.
    # Balaena gate4 false-negative fix: shift(-5) was silently PASS before.
    for m in re.finditer(r'\.shift\(\s*-\s*\d+\s*\)', source):
        line_num = source[:m.start()].count('\n') + 1
        findings.append({
            "type": "negative_shift_lookahead",
            "line": line_num,
            "severity": "CRITICAL",
            "detail": "shift(-N) brings future data into present — pure lookahead. Use shift(N) for past data."
        })

    # Hand-written for-loop with forward index reference — gate4 cannot statically verify.
    # Balaena gate4 false-negative fix: for-loop with df.iloc[i+5] was silently PASS.
    # If source has for-loop + array slice but no .rolling()/.shift(), emit WARN (manual review required).
    has_for_loop = bool(re.search(r'for\s+\w+\s+in\s+range\s*\(', source))
    has_forward_index = bool(re.search(r'\.iloc\[\w+\s*\+\s*[1-9]\d*\]|\[\w+\s*\+\s*[1-9]\d*\]', source))
    has_rolling_or_shift = bool(re.search(r'\.rolling\(|\.shift\(', source))
    if has_for_loop and has_forward_index and not has_rolling_or_shift:
        findings.append({
            "type": "handwritten_loop_forward_index",
            "line": 0,
            "severity": "WARN",
            "detail": "for-loop with forward index (iloc[i+N]) detected, no rolling/shift API — gate4 cannot statically verify. Manual review required for lookahead."
        })

    # Signal-return same-timestamp lookahead: score.iloc[t] used with log_ret.iloc[t+1] is CORRECT
    # But score.iloc[t] with log_ret.iloc[t] is WRONG. Hard to detect statically,
    # but flag if both are accessed at the same index in the same loop iteration.
    # Simplified check: look for patterns like `score.iloc[t]` and `log_ret.iloc[t]` (not t+1)
    score_at_t = bool(re.search(r'score.*\.iloc\[t\][^+]', source))
    ret_at_t = bool(re.search(r'(log_ret|rets|returns).*\.iloc\[t\][^+]', source))
    if score_at_t and ret_at_t:
        findings.append({
            "type": "signal_return_same_timestamp",
            "severity": "CRITICAL",
            "detail": "score.iloc[t] and returns.iloc[t] in same scope — signal sees the return it predicts. Use returns.iloc[t+1]"
        })

    status = "FAIL" if any(f.get("severity") == "CRITICAL" for f in findings) else \
             "WARN" if findings else "PASS"
    return {"gate": "inherited_code", "status": status, "findings": findings}


# ─── Gate 5: Statistical Validation (L3) ────────────────────────────────────────

def _gate5_boot_check() -> dict | None:
    """Boot-time fixture + complexity guard. Returns ERROR dict or None (proceed)."""
    import os as _os
    import sys as _sys
    import subprocess as _subprocess
    _env = _os.environ.copy()
    _env["PYTHONIOENCODING"] = "utf-8"
    _env["SKIP_GATE_INTEGRATION"] = "1"  # prevent recursive gate calls from fixtures
    _fixture_script = Path(__file__).parent / "test_falsify_quant_fixtures.py"
    if _fixture_script.exists():
        try:
            _check = _subprocess.run(
                [_sys.executable, str(_fixture_script)],
                capture_output=True, text=True, timeout=120, env=_env, encoding="utf-8")
        except _subprocess.TimeoutExpired:
            return {"gate": "statistical", "status": "ERROR",
                    "detail": "Boot-time fixture suite TIMED OUT (>120s) — gate5 cannot run. "
                              "Check for infinite loops or excessive PBO combination counts."}
        except Exception as e:
            return {"gate": "statistical", "status": "ERROR",
                    "detail": f"Boot-time fixture suite crashed: {e}"}
        if _check.returncode != 0:
            _failed = [l for l in _check.stdout.splitlines() if "FAIL " in l]
            _stderr_tail = _check.stderr.strip().splitlines()[-3:] if _check.stderr else []
            return {"gate": "statistical", "status": "ERROR",
                    "detail": f"Boot-time fixture suite FAILED — gate5 cannot run with broken formulas. "
                              f"Failed tests: {'; '.join(_failed[:3]) if _failed else 'CRASH (no FAIL line produced)'}"
                              f"{'; STDERR: ' + ' | '.join(_stderr_tail) if _stderr_tail else ''}"}

    # Complexity guard
    _complexity_guard = Path(__file__).parent / "complexity_guard.py"
    if _complexity_guard.exists():
        try:
            _cc_check = _subprocess.run(
                [_sys.executable, str(_complexity_guard), "--gate"],
                capture_output=True, text=True, timeout=15)
            if _cc_check.returncode != 0:
                _f_funcs = [l.strip() for l in _cc_check.stdout.splitlines()
                            if "F-grade" in l or ": CC=" in l
                            or "radon-unavailable" in l]
                gate5_statistical._complexity_warning = (
                    f"Complexity guard: {len(_f_funcs)} F-grade function(s) detected. "
                    "AI edits to these functions carry high hallucination risk. "
                    f"Details: {'; '.join(_f_funcs[:3])}")
        except _subprocess.TimeoutExpired:
            gate5_statistical._complexity_warning = (
                "Complexity guard TIMED OUT (>15s) — radon may be stuck. "
                "Complexity check did not run.")
        except Exception as e:
            gate5_statistical._complexity_warning = (
                f"Complexity guard CRASHED: {type(e).__name__}: {str(e)[:120]}. "
                "Complexity check did not run.")
    return None


def _gate5_select_csv(results_dir: str, target_csv_override: str) -> tuple:
    """Select the target daily returns CSV. Returns (target_csv_path, error_dict)."""
    if target_csv_override:
        p = Path(target_csv_override)
        if not p.exists():
            return None, {"gate": "statistical", "status": "ERROR",
                    "detail": f"target_csv_override not found: {target_csv_override}"}
        return p, None

    if not results_dir:
        _skip = {"gate": "statistical", "status": "SKIP",
                 "detail": "no results-dir or target-csv provided"}
        _cc_warn = getattr(gate5_statistical, "_complexity_warning", None)
        if _cc_warn:
            _skip["complexity_warning"] = _cc_warn
        return None, _skip

    rdir = Path(results_dir)
    daily_files = list(rdir.glob("*daily*.csv"))
    if not daily_files:
        return None, {"gate": "statistical", "status": "SKIP", "detail": "no daily returns CSV found"}

    # Pick the CSV with the most rows (least likely to be an orphan)
    best_len = 0
    target = None
    for f in daily_files:
        try:
            import pandas as _pd_tmp
            n_rows = len(_pd_tmp.read_csv(f))
            if n_rows > best_len:
                best_len = n_rows
                target = f
        except Exception:
            continue
    if target is None:
        target = daily_files[0]
    return target, None


def _gate5_run_stats(returns, stats, n_param_combos: int,
                     n_trials_effective: int | None = None) -> dict:
    """Run PSR, DSR, permutation test."""
    from falsify.quant import psr, dsr, permutation_test
    findings = {}
    findings["psr"] = psr(
        sharpe=stats["sharpe_annualized"], n=stats["n"],
        skew=stats["skew"], kurt=stats["kurtosis_excess"],
        benchmark_sharpe=0.0)
    findings["dsr"] = dsr(
        observed_sr=stats["sharpe_annualized"], n=stats["n"],
        skew=stats["skew"], kurt=stats["kurtosis_excess"],
        n_trials=max(n_trials_effective or n_param_combos, 1))
    findings["permutation_test"] = permutation_test(returns=returns, n_permutations=500)
    return findings


def _gate5_run_l4(returns, returns_matrix_path: str, target_csv, stats: dict,
                  matrix_columns: str = "",
                  multi_objective: bool = False,
                  calmar_floor: float = 0.3,
                  live_forensics_json: str = "") -> dict:
    """Run L4 robustness checks: PBO, walk-forward, regime, cost realism, execution realism."""
    from falsify.quant import (pbo as pbo_fn, walk_forward_predictive_power,
                                pnl_regime_analysis, cost_realism_check,
                                execution_realism_check, _load_returns_matrix,
                                multi_objective_pbo_calmar, per_trade_edge_vs_cost,
                                cpcv_split)
    import pandas as _pd
    import numpy as _np
    findings = {}

    # PBO + CPCV + walk-forward (+ multi-objective PBO+Calmar if requested)
    # CPCV added 2026-07-07 per Exp3: WF PBO=0.25 vs CPCV PBO=1.0
    # CPCV is now primary OOS validation layer; WF kept as supplementary diagnostic
    if returns_matrix_path and Path(returns_matrix_path).exists():
        try:
            rm, _matrix_cols = _load_returns_matrix(returns_matrix_path, matrix_columns)
            if rm.shape[1] >= 2:
                findings["pbo"] = pbo_fn(rm.values, n_bins=16)
                if multi_objective:
                    findings["multi_objective_pbo_calmar"] = multi_objective_pbo_calmar(
                        rm.values, n_bins=16, calmar_floor=calmar_floor)
                findings["walk_forward"] = walk_forward_predictive_power(rm.values)

                # CPCV: combinatorial purged cross-validation (Exp3: catches overfit WF misses)
                try:
                    T_cpcv = rm.shape[0]
                    n_groups = min(6, T_cpcv // 4) if T_cpcv >= 16 else 0
                    if n_groups >= 4:
                        splits = cpcv_split(T_cpcv, n_groups=n_groups,
                                           n_test_groups=2, purge=5, embargo=5)
                        cpcv_pbo_values = []
                        for train_idx, test_idx in splits[:20]:  # cap at 20 splits for tractability
                            if len(train_idx) < 20 or len(test_idx) < 10:
                                continue
                            oos_returns = rm.values[test_idx, :]
                            is_returns = rm.values[train_idx, :]
                            is_sr = is_returns.mean(axis=0) / (is_returns.std(axis=0, ddof=1) + 1e-10)
                            oos_sr = oos_returns.mean(axis=0) / (oos_returns.std(axis=0, ddof=1) + 1e-10)
                            is_best = int(_np.argmax(is_sr))
                            from scipy.stats import rankdata
                            oos_rank = rankdata(oos_sr)[is_best] - 1
                            median_rank = (rm.shape[1] - 1) / 2.0
                            cpcv_pbo_values.append(1 if oos_rank <= median_rank else 0)
                        if cpcv_pbo_values:
                            cpcv_pbo = float(_np.mean(cpcv_pbo_values))
                            findings["cpcv_pbo"] = {
                                "pbo": round(cpcv_pbo, 4),
                                "n_splits": len(cpcv_pbo_values),
                                "n_groups": n_groups,
                                "verdict": "REJECT" if cpcv_pbo >= 0.50 else
                                          ("WARN" if cpcv_pbo >= 0.30 else "PASS"),
                            }
                except Exception as e:
                    findings["cpcv_pbo"] = {"pbo": None, "error": str(e)[:200]}

                findings["returns_matrix_manifest"] = {
                    "path": returns_matrix_path,
                    "columns": _matrix_cols,
                    "n_rows_after_dropna": int(rm.shape[0]),
                    "n_columns": int(rm.shape[1]),
                }
        except Exception as e:
            findings["pbo"] = {"pbo": None, "error": str(e)[:200]}

    # Per-trade edge vs cost (high-turnover gate, Balaena #7)
    if live_forensics_json and Path(live_forensics_json).exists():
        try:
            _lf = json.loads(Path(live_forensics_json).read_text())
            _agg = None
            for _r in (_lf.get("results") or []):
                if _r.get("check") == "slippage_aggregate":
                    _agg = _r.get("value", {})
                    break
            if _agg:
                _edge = _agg.get("t5_markout_bps", {}).get("median")
                _spread = _agg.get("spread_bps", {}).get("median", 0)
                _impact = _agg.get("impact_bps", {}).get("median", 0)
                _fee = _lf.get("fee_bps", 0)
                _n = _agg.get("t5_markout_bps", {}).get("n", 0)
                if _edge is not None and _n > 0:
                    _edge_arr = _np.array([_edge] * int(_n))
                    _cost_arr = _np.array([_spread + _impact + _fee] * int(_n))
                    findings["per_trade_edge_vs_cost"] = per_trade_edge_vs_cost(
                        _edge_arr, _cost_arr, threshold=1.5, min_trades=30)
        except Exception as e:
            findings["per_trade_edge_vs_cost"] = {"pass": False, "reason": f"error: {str(e)[:120]}"}

    # Regime analysis (auto-detect volume)
    try:
        _volume_data = None
        try:
            _csv_df = _pd.read_csv(str(target_csv))
            for _vcol in ['volume', 'vol', 'quote_volume', 'volume_usd', 'turnover', 'qvol']:
                if _vcol in _csv_df.columns:
                    _volume_data = _csv_df[_vcol].dropna().values
                    break
        except Exception:
            pass
        findings["regime_analysis"] = pnl_regime_analysis(returns, volume=_volume_data)
    except Exception as e:
        findings["regime_analysis"] = {"error": str(e)[:200]}

    # Cost realism
    try:
        _strategy_type = getattr(gate5_statistical, '_strategy_type', '')
        findings["cost_realism"] = cost_realism_check(returns, strategy_type=_strategy_type)
    except Exception as e:
        findings["cost_realism"] = {"error": str(e)[:200]}

    # Execution realism
    try:
        _strategy_type = getattr(gate5_statistical, '_strategy_type', '')
        _base_cost = getattr(gate5_statistical, '_base_cost_bps', 5.0)
        findings["execution_realism"] = execution_realism_check(
            returns, strategy_type=_strategy_type, base_cost_bps=_base_cost)
    except Exception as e:
        findings["execution_realism"] = {"error": str(e)[:200]}

    # CTA/trend regime sub-gate (Exp4: range regime SR=-0.42, skew=-0.80)
    # Linear SR/DSR averages out regime-dependent structure
    _strategy_type = getattr(gate5_statistical, '_strategy_type', '')
    if _strategy_type in ("cta", "trend", "trend_following"):
        try:
            import numpy as _np2
            rets = _np2.asarray(returns, dtype=float)
            rets = rets[_np2.isfinite(rets)]
            if len(rets) > 30:
                from scipy.stats import skew as _skew
                skew_val = float(_skew(rets))
                ann_ret = float(_np2.mean(rets) * 365)
                cum = _np2.cumprod(1 + rets)
                peak = _np2.maximum.accumulate(cum)
                dd = (cum - peak) / peak
                mdd = float(_np2.min(dd))
                calmar = ann_ret / abs(mdd) if mdd < 0 else ann_ret
                crisis_threshold = float(_np2.percentile(rets, 25))
                crisis_rets = rets[rets <= crisis_threshold]
                crisis_alpha = float(_np2.mean(crisis_rets)) if len(crisis_rets) > 0 else 0.0

                cta_pass = (skew_val > 0 and calmar > 0.3 and crisis_alpha > 0)
                cta_warn = (not cta_pass and
                            (skew_val > -0.5 or calmar > 0.1 or crisis_alpha > -0.01))
                findings["cta_regime_subgate"] = {
                    "skew": round(skew_val, 4),
                    "calmar": round(calmar, 4),
                    "crisis_alpha": round(crisis_alpha, 6),
                    "verdict": "PASS" if cta_pass else ("WARN" if cta_warn else "FAIL"),
                    "note": "Exp4: range regime SR=-0.42 skew=-0.80; linear SR averages out regime structure",
                }
        except Exception as e:
            findings["cta_regime_subgate"] = {"error": str(e)[:200]}

    return findings


def _gate5_status(findings: dict, dsr_result: dict, perm_result: dict) -> tuple:
    """Determine gate5 status. Returns (status, blockers).

    L4 sub-checks (regime, cost, execution) that returned {"error": ...}
    must NOT be allowed to pass silently — that's a false green.
    """
    pbo_val = findings.get("pbo", {}).get("pbo")
    dsr_val = dsr_result.get("dsr")
    perm_p = perm_result.get("p_value")
    wf_verdict = findings.get("walk_forward", {}).get("verdict", "")
    regime_verdict = findings.get("regime_analysis", {}).get("verdict", "")
    cost_verdict = findings.get("cost_realism", {}).get("verdict", "")

    blockers = []
    if pbo_val is not None and pbo_val >= 0.50:
        blockers.append(f"PBO={pbo_val} >= 0.50 (reject strategy family)")
    if pbo_val is not None and 0.30 <= pbo_val < 0.50:
        blockers.append(f"PBO={pbo_val} >= 0.30 (high overfitting risk)")
    if dsr_val is not None and dsr_val < 0.90:
        blockers.append(f"DSR={dsr_val} < 0.90 (SR likely inflated by selection bias)")
    if perm_p is not None and perm_p >= 0.05:
        blockers.append(f"Permutation p={perm_p} >= 0.05 (SR not significant vs random)")
    if "WARN" in wf_verdict:
        blockers.append(f"Walk-forward: {wf_verdict}")
    if "WARN" in regime_verdict:
        blockers.append(f"Regime: {findings.get('regime_analysis', {}).get('verdict_detail', regime_verdict)}")
    if cost_verdict == "WARN":
        blockers.append(f"Cost realism: {findings.get('cost_realism', {}).get('recommendation', '')[:150]}")

    exec_verdict = findings.get("execution_realism", {}).get("overall_verdict", "")
    if exec_verdict == "FAIL":
        blockers.append(f"Execution realism FAIL: {findings.get('execution_realism', {}).get('recommendation', '')[:150]}")
    elif exec_verdict == "WARN":
        blockers.append(f"Execution realism WARN: {findings.get('execution_realism', {}).get('recommendation', '')[:150]}")

    # L4 sub-check errors must not pass silently (false-green prevention)
    _L4_KEYS = ["pbo", "cpcv_pbo", "regime_analysis", "cost_realism", "execution_realism",
                "multi_objective_pbo_calmar", "per_trade_edge_vs_cost", "cta_regime_subgate"]
    for _key in _L4_KEYS:
        _sub = findings.get(_key)
        if isinstance(_sub, dict) and "error" in _sub and "verdict" not in _sub:
            blockers.append(f"L4 {_key} check ERROR: {_sub['error'][:120]}")

    # CPCV PBO (Exp3: WF PBO=0.25 vs CPCV PBO=1.0 — WF misses overfit)
    _cpcv = findings.get("cpcv_pbo", {})
    _cpcv_pbo = _cpcv.get("pbo")
    if _cpcv_pbo is not None and _cpcv_pbo >= 0.50:
        blockers.append(f"CPCV PBO={_cpcv_pbo} >= 0.50 (reject strategy family — WF missed this)")
    elif _cpcv_pbo is not None and _cpcv_pbo >= 0.30:
        blockers.append(f"CPCV PBO={_cpcv_pbo} >= 0.30 (high overfitting risk — WF missed this)")

    # CTA regime sub-gate (Exp4: range regime SR=-0.42, skew=-0.80)
    _cta = findings.get("cta_regime_subgate", {})
    _cta_verdict = _cta.get("verdict", "")
    if _cta_verdict == "FAIL":
        blockers.append(f"CTA regime sub-gate FAIL: skew={_cta.get('skew')}, calmar={_cta.get('calmar')}, crisis_alpha={_cta.get('crisis_alpha')}")
    elif _cta_verdict == "WARN":
        blockers.append(f"CTA regime sub-gate WARN: skew={_cta.get('skew')}, calmar={_cta.get('calmar')}")

    # Multi-objective PBO+Calmar (Balaena #1)
    _mo = findings.get("multi_objective_pbo_calmar", {})
    if _mo and _mo.get("verdict") == "BLOCK":
        blockers.append(f"Multi-objective PBO+Calmar BLOCK: {_mo.get('reason', '')[:150]}")

    # Per-trade edge vs cost (Balaena #7) — BLOCK for high-turnover
    _ptec = findings.get("per_trade_edge_vs_cost", {})
    if _ptec and not _ptec.get("pass", True):
        blockers.append(f"Per-trade edge vs cost FAIL: {_ptec.get('reason', '')[:150]}")

    if any("PBO" in b and ">= 0.50" in b for b in blockers):
        status = "FAIL"
    elif blockers:
        status = "WARN"
    else:
        status = "PASS"
    return status, blockers


def gate5_statistical(results_dir: str, n_param_combos: int = 1,
                      returns_matrix_path: str = "",
                      target_csv_override: str = "",
                      matrix_columns: str = "",
                      n_trials_declared: int = 0,
                      trial_ledger: str = "",
                      calendar_contract: str = "",
                      row_loss_audit: str = "",
                      coverage_manifest: str = "",
                      variant_policy: str = "",
                      multi_objective: bool = False,
                      calmar_floor: float = 0.3,
                      live_forensics_json: str = "") -> dict:
    """Run PBO/DSR/PSR/permutation test on backtest results.

    Imports falsify_quant.py (same directory) and runs:
    - PSR: Probabilistic Sharpe Ratio vs 0
    - DSR: Deflated Sharpe Ratio (multiple testing correction)
    - PBO: Probability of Backtest Overfitting (if returns-matrix provided)
    - Permutation test: SR significance vs random ordering

    Returns gate status:
    - PBO >= 0.50 → FAIL (reject strategy family)
    - PBO >= 0.30 → WARN (research only)
    - DSR < 0.90 → WARN
    - Permutation p >= 0.05 → WARN
    """
    # Boot-time checks (fixture suite + complexity guard)
    boot_error = _gate5_boot_check()
    if boot_error:
        return boot_error

    # CSV selection
    target_csv, csv_error = _gate5_select_csv(results_dir, target_csv_override)
    if csv_error:
        return csv_error

    # Import and load data
    import sys as _sys
    try:
        _sys.path.insert(0, str(Path(__file__).parent))
        from falsify.quant import _load_daily_returns, _compute_stats, _count_trial_ledger, _validate_evidence_integrity
    except ImportError as e:
        return {"gate": "statistical", "status": "ERROR", "detail": f"Cannot import falsify_quant: {e}"}

    evidence_integrity = _validate_evidence_integrity(
        calendar_contract=calendar_contract,
        row_loss_audit=row_loss_audit,
        coverage_manifest=coverage_manifest,
        variant_policy=variant_policy,
    )

    try:
        returns = _load_daily_returns(str(target_csv))
        stats = _compute_stats(returns)
    except Exception as e:
        return {"gate": "statistical", "status": "ERROR", "detail": f"Cannot load returns: {e}"}

    try:
        ledger_trials = _count_trial_ledger(trial_ledger) if trial_ledger else None
    except Exception as e:
        return {"gate": "statistical", "status": "ERROR", "detail": f"Cannot load trial ledger: {e}"}

    matrix_col_count = len([c.strip() for c in matrix_columns.split(',') if c.strip()]) if matrix_columns else 0
    n_trials_effective = max(int(n_param_combos), int(n_trials_declared or 0), int(ledger_trials or 0), int(matrix_col_count or 0), 1)

    # Run statistical tests
    stat_findings = _gate5_run_stats(returns, stats, n_param_combos, n_trials_effective)

    # Run L4 robustness checks
    l4_findings = _gate5_run_l4(returns, returns_matrix_path, target_csv, stats, matrix_columns,
                                multi_objective=multi_objective,
                                calmar_floor=calmar_floor,
                                live_forensics_json=live_forensics_json)

    findings = {**stat_findings, **l4_findings}

    # Determine gate status
    status, blockers = _gate5_status(findings, stat_findings["dsr"], stat_findings["permutation_test"])
    if evidence_integrity.get("status") != "PASS":
        if status == "PASS":
            status = "WARN"
        for issue in evidence_integrity.get("issues") or []:
            blockers.append(f"Evidence integrity: {issue}")

    _result = {
        "gate": "statistical",
        "status": status,
        "source_csv": target_csv.name,
        "input_manifest": {
            "returns_matrix_path": returns_matrix_path or None,
            "matrix_columns": [c.strip() for c in matrix_columns.split(',') if c.strip()] if matrix_columns else [],
            "n_param_combos_arg": n_param_combos,
            "n_trials_declared": n_trials_declared or None,
            "trial_ledger_path": trial_ledger or None,
            "trial_ledger_count": ledger_trials,
            "n_trials_effective": n_trials_effective,
        },
        "findings": findings,
        "evidence_integrity": evidence_integrity,
        "blockers": blockers,
    }

    _cc_warn = getattr(gate5_statistical, "_complexity_warning", None)
    if _cc_warn:
        _result["complexity_warning"] = _cc_warn

    return _result


# ─── Production pre-check: quant gate must pass first ──────────────────────────

def check_quant_gate_passed(results_dir: str) -> dict:
    """Pre-check for production Falsify: verify quant gate has been run and passed.

    Production Falsify must NOT run on a strategy whose backtest hasn't passed
    quant Falsify gates (pitfall #21). This function scans results_dir for quant
    gate output JSONs and checks their claim_ceiling.

    A valid quant gate report is a JSON file containing both 'claim_ceiling' and
    'gates' keys. The most recent valid report is used.

    Returns:
        {"status": "PASS", "source": <filename>, "claim_ceiling": <ceiling>}
            if quant gate PASS_TO_* or legacy PASS found
        {"status": "BLOCK", "reason": "...", "source": <filename>?}
            if no quant gate report or claim_ceiling=BLOCK/CANDIDATE_NEEDS_NEXT_GATE
    """
    rdir = Path(results_dir)
    if not rdir.exists():
        return {"status": "BLOCK",
                "reason": f"results dir not found: {results_dir}"}

    # Look for quant gate output JSONs — must have claim_ceiling + gates keys
    candidates = list(rdir.glob("*.json"))
    for jf in sorted(candidates, key=lambda f: f.stat().st_mtime, reverse=True):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            if "claim_ceiling" not in data or "gates" not in data:
                continue
            ceiling = data.get("claim_ceiling", "")
            if str(ceiling).startswith("PASS"):
                return {"status": "PASS", "source": jf.name, "claim_ceiling": ceiling}
            elif ceiling in ("BLOCK", "CANDIDATE_NEEDS_NEXT_GATE"):
                return {"status": "BLOCK",
                        "reason": f"quant gate report {jf.name} has claim_ceiling={ceiling} — only PASS_TO_* / legacy PASS may proceed to production Falsify",
                        "source": jf.name}
        except (json.JSONDecodeError, KeyError):
            continue

    return {"status": "BLOCK",
            "reason": f"No quant gate report found in {results_dir} — pitfall #21: quant Falsify must run BEFORE production Falsify"}


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Quant Falsify Gate (v2)")
    parser.add_argument("--script", required=False, default="", help="Path to backtest script")
    parser.add_argument("--contract", default="", help="Path to research contract YAML/JSON")
    parser.add_argument("--results-dir", default="", help="Path to results directory")
    parser.add_argument("--output", default="", help="Output JSON file (default: stdout)")
    parser.add_argument("--n-param-combos", type=int, default=1,
                        help="Number of parameter combinations tried (for DSR multiple-testing correction)")
    parser.add_argument("--returns-matrix", default="",
                        help="CSV with multiple return columns (each col = one param combo) for PBO")
    parser.add_argument("--matrix-columns", default="",
                        help="Comma-separated explicit return columns in --returns-matrix. Required when --returns-matrix is set; no automatic numeric-column selection.")
    parser.add_argument("--n-trials-declared", type=int, default=0,
                        help="Declared total trials including hidden/failed attempts; used as lower bound for DSR n_trials.")
    parser.add_argument("--trial-ledger", default="",
                        help="Optional JSON/JSONL/CSV/text trial ledger; count is used as lower bound for DSR n_trials.")
    parser.add_argument("--target-csv", default="",
                        help="Explicit daily returns CSV for gate5 (overrides heuristic selection)")
    parser.add_argument("--precheck-production", action="store_true",
                        help="Pre-check mode: verify quant gate has passed before production Falsify. Exits 0 only for PASS_TO_* / legacy PASS, 1 for BLOCK/CANDIDATE_NEEDS_NEXT_GATE.")
    parser.add_argument("--calendar-contract", default="",
                        help="Path to calendar contract JSON (L0.5 evidence integrity). Required for gate5 PASS.")
    parser.add_argument("--row-loss-audit", default="",
                        help="Path to row-loss audit JSON/CSV (L0.5 evidence integrity). Required for gate5 PASS.")
    parser.add_argument("--coverage-manifest", default="",
                        help="Path to coverage manifest JSON/CSV (L0.5 evidence integrity). Required for gate5 PASS.")
    parser.add_argument("--variant-policy", default="",
                        help="Path to variant policy JSON/CSV (L0.5 evidence integrity). Required for gate5 PASS.")
    parser.add_argument("--manifest", default="",
                        help="Falsify v1.0 MANIFEST.json for harness boundary verdict. Defaults to <results-dir>/MANIFEST.json if present.")
    parser.add_argument("--self-test-boundary", action="store_true",
                        help="Run built-in red/green fixtures for harness boundary manifest validator and exit.")
    parser.add_argument("--multi-objective", action="store_true",
                        help="Enable multi-objective PBO+Calmar L4 check (Balaena #1). Pass requires PBO<0.5 AND median OOS Calmar >= --calmar-floor.")
    parser.add_argument("--calmar-floor", type=float, default=0.3,
                        help="Calmar floor for --multi-objective gate (default 0.3 ≈ 30%% annual return / max drawdown).")
    parser.add_argument("--live-forensics-json", default="",
                        help="Path to live_forensics.py output JSON for per-trade edge-vs-cost gate (Balaena #7).")
    args = parser.parse_args()

    if args.self_test_boundary:
        sys.exit(_self_test_boundary())

    # ─── Production pre-check mode ──────────────────────────────────────────
    # Called by production Falsify before proceeding. Does NOT run any gates —
    # only checks for an existing quant gate report in results-dir.
    if args.precheck_production:
        if not args.results_dir:
            print(json.dumps({"status": "BLOCK",
                              "reason": "--results-dir required for --precheck-production"}))
            sys.exit(1)
        result = check_quant_gate_passed(args.results_dir)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result["status"] != "BLOCK" else 1)

    script = os.path.abspath(args.script)
    if not args.script:
        print(json.dumps({"error": "--script is required when not using --precheck-production"}))
        sys.exit(1)
    if not os.path.exists(script):
        print(json.dumps({"error": f"script not found: {script}"}))
        sys.exit(1)

    results_dir = os.path.abspath(args.results_dir) if args.results_dir else ""
    contract_path = args.contract

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "script": script,
        "contract": contract_path or "(none)",
        "results_dir": results_dir,
        "gates": {}
    }

    # L0: Contract gate (must pass before anything else)
    report["gates"]["gate0_contract"] = gate0_contract(contract_path)

    # If contract fails, we still run the other gates for diagnostic value,
    # but claim_ceiling is already BLOCK.
    report["gates"]["gate1_backtest_audit"] = gate1_backtest_audit(script)
    report["gates"]["gate2_survivorship"] = gate2_survivorship(script)
    report["gates"]["gate3_numeric_recompute"] = gate3_numeric_recompute(results_dir) if results_dir else \
        {"gate": "numeric_recompute", "status": "SKIP", "detail": "no results-dir provided"}
    report["gates"]["gate4_inherited_code"] = gate4_inherited_code(script)

    # ─── Infer strategy type for cost_realism_check ─────────────────────
    # Parse contract hypothesis to determine if strategy is momentum or reversion.
    # This lets cost_realism use the correct threshold (3.0 for momentum vs 5.0 for unknown).
    _strategy_type = ""
    _base_cost_bps = 5.0  # default; perp strategies should override via contract
    if contract_path and Path(contract_path).exists():
        try:
            ct = Path(contract_path).read_text(encoding="utf-8").lower()
            if "trend" in ct or "cta" in ct or "breakout" in ct:
                _strategy_type = "cta"
            elif "momentum" in ct or "continuation" in ct:
                _strategy_type = "momentum"
            elif "reversion" in ct or "mean_revert" in ct:
                _strategy_type = "reversion"
            # P1 fix (BUG 7): infer base_cost_bps from contract if present
            import re as _re
            _cost_match = _re.search(r'base_?cost[_\s:=]+(\d+(?:\.\d+)?)\s*bps', ct)
            if _cost_match:
                _base_cost_bps = float(_cost_match.group(1))
            elif 'perp' in ct or 'funding' in ct:
                _base_cost_bps = 15.0  # perp strategies have higher base cost
        except Exception:
            pass
    gate5_statistical._strategy_type = _strategy_type
    gate5_statistical._base_cost_bps = _base_cost_bps

    # L3: Statistical validation gate (PBO/DSR/PSR/permutation)
    report["gates"]["gate5_statistical"] = gate5_statistical(
        results_dir, args.n_param_combos, args.returns_matrix, args.target_csv,
        args.matrix_columns, args.n_trials_declared, args.trial_ledger,
        calendar_contract=args.calendar_contract,
        row_loss_audit=args.row_loss_audit,
        coverage_manifest=args.coverage_manifest,
        variant_policy=args.variant_policy,
        multi_objective=args.multi_objective,
        calmar_floor=args.calmar_floor,
        live_forensics_json=args.live_forensics_json)

    # L1+/L2: Harness boundary verdict (Falsify v1.0 alpha). This separates
    # metric evidence from whether the evaluation environment is clean.
    report["gates"]["gate6_harness_boundary"] = gate_harness_boundary(args.manifest, results_dir)

    # ─── Claim ceiling computation ──────────────────────────────────────────
    # The ceiling is the MOST PERMISSIVE verdict the evidence supports.
    # Any gate FAIL → ceiling drops. Contract claim_ceiling rules are applied last.
    gate_statuses = {name: g["status"] for name, g in report["gates"].items()}

    has_fail = any(s == "FAIL" for s in gate_statuses.values())
    has_error = any(s == "ERROR" for s in gate_statuses.values())
    has_warn = any(s == "WARN" for s in gate_statuses.values())

    if has_fail or has_error:
        claim_ceiling = "BLOCK"
    elif has_warn:
        claim_ceiling = "CANDIDATE_NEEDS_NEXT_GATE"
    else:
        claim_ceiling = "PASS_TO_PAPER"

    # Apply contract-level claim ceilings (if contract parsed). Rules are
    # conditional: their mere presence in the contract must not automatically
    # downgrade PASS. They can only restrict when the corresponding condition
    # is observed in gate outputs.
    contract_result = report["gates"].get("gate0_contract", {})
    contract_cc = contract_result.get("claim_ceiling", {})
    if isinstance(contract_cc, dict) and contract_cc:
        def _restrict_to_candidate(reason: str) -> None:
            nonlocal claim_ceiling
            if str(claim_ceiling).startswith("PASS"):
                claim_ceiling = "CANDIDATE_NEEDS_NEXT_GATE"
                report.setdefault("contract_ceiling_applied", []).append(reason)

        def _restrict_to_block(reason: str) -> None:
            nonlocal claim_ceiling
            claim_ceiling = "BLOCK"
            report.setdefault("contract_ceiling_applied", []).append(reason)

        gate2_status = report["gates"].get("gate2_survivorship", {}).get("status")
        gate5 = report["gates"].get("gate5_statistical", {})
        pbo_val = gate5.get("findings", {}).get("pbo", {}).get("pbo")

        if contract_cc.get("no_pit_universe") == "candidate_needs_next_gate" and gate2_status in ("WARN", "FAIL", "ERROR"):
            _restrict_to_candidate("no_pit_universe")
        if pbo_val is not None:
            if contract_cc.get("pbo_ge_0_50") in ("reject", "block") and pbo_val >= 0.50:
                _restrict_to_block("pbo_ge_0_50")
            elif contract_cc.get("pbo_ge_0_30") == "candidate_needs_next_gate" and pbo_val >= 0.30:
                _restrict_to_candidate("pbo_ge_0_30")
        # no_exec_sim is not auto-applied here: this gate has no execution-sim
        # evidence field yet. Human/production Falsify must apply it when relevant.

    harness_gate = report["gates"].get("gate6_harness_boundary", {})
    claim_ceiling = _restrict_ceiling(claim_ceiling, harness_gate.get("claim_ceiling_cap", "PASS_TO_PAPER"))

    report["metric_verdict"] = _metric_verdict_from_ceiling(claim_ceiling if claim_ceiling == "BLOCK" else ("PASS_TO_PAPER" if not has_fail and not has_error and not has_warn else "CANDIDATE_NEEDS_NEXT_GATE"))
    report["harness_verdict"] = harness_gate.get("harness_verdict", "NOT_TESTED")
    report["claim_ceiling"] = claim_ceiling
    report["final_verdict"] = _final_verdict(report["metric_verdict"], report["harness_verdict"], claim_ceiling)
    report["verdict"] = claim_ceiling  # backwards compat
    report["cannot_claim"] = []
    if report["harness_verdict"] != "PASS":
        report["cannot_claim"].extend(["clean_alpha", "promotion_readiness", "live_authority"])

    # Build human-readable summary
    report["summary"] = _build_summary(report)

    output = json.dumps(report, indent=2, ensure_ascii=False, default=str)
    if args.output:
        Path(args.output).write_text(output + "\n")
        print(f"Report written to {args.output}")
    else:
        print(output)

    # Exit code: 0 only for PASS_TO_* / legacy PASS, 1 for BLOCK/CANDIDATE_NEEDS_NEXT_GATE
    sys.exit(0 if str(claim_ceiling).startswith("PASS") else 1)


def _build_summary(report: dict) -> str:
    """One-line human-readable summary of the verdict."""
    ceiling = report.get("claim_ceiling", "UNKNOWN")
    gates = report.get("gates", {})
    parts = []
    for name, g in gates.items():
        s = g.get("status", "?")
        if s == "PASS":
            parts.append(f"{name}=PASS")
        elif s == "FAIL":
            # Include first finding detail
            detail = g.get("detail", "")
            findings = g.get("findings", [])
            if isinstance(findings, list) and findings and isinstance(findings[0], dict):
                detail = findings[0].get("type", detail)
            elif isinstance(findings, dict):
                # gate5 findings is a dict; use blockers instead
                blockers = g.get("blockers", [])
                if blockers:
                    detail = blockers[0]
            parts.append(f"{name}=FAIL({detail})")
        elif s == "WARN":
            parts.append(f"{name}=WARN")
        elif s == "SKIP":
            parts.append(f"{name}=SKIP")
        elif s == "ERROR":
            parts.append(f"{name}=ERROR")

    return f"FINAL_VERDICT={report.get('final_verdict', ceiling)} | METRIC={report.get('metric_verdict', '?')} | HARNESS={report.get('harness_verdict', '?')} | CLAIM_CEILING={ceiling} | {' | '.join(parts)}"

if __name__ == "__main__":
    main()
