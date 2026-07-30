"""Unified claim-bearing authority kernel for Falsify.

Pure composition only — no network, no filesystem, no subprocess, no LLM I/O.

Every claim-bearing entry (review / run / gate / quant adapter / production
adapter) must call ``finalize_authority`` and take exit codes from its output.
LLM semantic PASS remains a real PASS inside its claim scope; it never alone
upgrades capital or live authority.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, Mapping, Optional, Sequence

# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------

PUBLIC_VERDICTS = ("PASS", "PASS_WITH_DEBT", "BLOCK")
LEGACY_VERDICTS = {"PROCEED": "PASS", "HOLD": "BLOCK", "ARCHIVE": "BLOCK"}

# Lower rank = worse. min() across legs is fail-closed.
VERDICT_RANK = {
    "PASS": 40,
    "PASS_WITH_DEBT": 30,
    "UNSUPPORTED": 15,
    "BLOCK": 10,
    "UNKNOWN": 5,
    "SKIP": 5,
    "N/A": 5,
    "ERROR": 5,
    "INCOMPLETE": 5,
    "TRUNCATED": 5,
    "UNPARSEABLE": 5,
}

FAIL_CLOSED_TOKENS = frozenset({
    "UNKNOWN", "SKIP", "N/A", "UNSUPPORTED", "TRUNCATED", "ERROR",
    "INCOMPLETE", "UNPARSEABLE", "MISSING",
})

RISK_TIERS = frozenset({
    "normal", "epistemic", "high", "production", "quant", "auto",
})

HIGH_RISK_TIERS = frozenset({"high", "production", "quant"})

AUTHORITY_CEILINGS = (
    "NONE",
    "L2_LINT",
    "EPISTEMIC_CLAIM",
    "QUANT_PROMOTION",
    "PRODUCTION_LIVE",
)

CAPITAL_AUTHORITIES = ("NONE", "PAPER", "LIVE")

CEILING_CAPITAL_ELIGIBILITY = {
    "NONE": "NONE",
    "L2_LINT": "NONE",
    "EPISTEMIC_CLAIM": "NONE",
    "QUANT_PROMOTION": "PAPER",
    "PRODUCTION_LIVE": "LIVE",
}

_VERDICT_LINE_RE = re.compile(
    r"^VERDICT:\s*(PASS_WITH_DEBT|PASS|BLOCK|PROCEED|HOLD(?:-\d+)?|ARCHIVE)\s*$",
    re.IGNORECASE,
)
_ANY_VERDICT_RE = re.compile(
    r"VERDICT:\s*(PASS_WITH_DEBT|PASS|BLOCK|PROCEED|HOLD(?:-\d+)?|ARCHIVE)\b",
    re.IGNORECASE,
)
_COVERAGE_RE = re.compile(
    r"(?im)^(?:Coverage|Evidence summary|Audit coverage|Coverage summary)\s*:\s*\S+"
)


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def normalize_verdict_token(raw: Optional[str]) -> Optional[str]:
    if raw is None:
        return None
    v = str(raw).strip().upper()
    if not v:
        return None
    if v.startswith("HOLD"):
        return "BLOCK"
    return LEGACY_VERDICTS.get(v, v)


def min_verdict(*verdicts: Optional[str]) -> str:
    """Fail-closed min. Non-public / fail-closed tokens collapse to BLOCK."""
    best = "PASS"
    best_rank = VERDICT_RANK["PASS"]
    for v in verdicts:
        token = normalize_verdict_token(v)
        if token is None or token in FAIL_CLOSED_TOKENS or token not in PUBLIC_VERDICTS:
            token = "BLOCK"
        rank = VERDICT_RANK.get(token, VERDICT_RANK["BLOCK"])
        if rank < best_rank:
            best_rank = rank
            best = token
    return best


def parse_model_completion(text: str) -> dict:
    """Strict completion parse for LLM audit text.

    - Exactly one VERDICT line in the whole text.
    - That line must be the last non-empty line.
    - Unknown VERDICT tokens are parse failure.
    """
    text = text or ""
    lines = text.splitlines()
    non_empty_idx = [i for i, ln in enumerate(lines) if ln.strip()]
    verdict_hits = []
    for i, ln in enumerate(lines):
        stripped = ln.strip()
        m = _VERDICT_LINE_RE.match(stripped)
        if m:
            verdict_hits.append((i, normalize_verdict_token(m.group(1))))
        elif re.match(r"(?i)^VERDICT:\s*\S+", stripped):
            verdict_hits.append((i, None))

    any_matches = list(_ANY_VERDICT_RE.finditer(text))
    reasons: list[str] = []
    completion_status = "COMPLETE"
    model_verdict = None

    if not verdict_hits:
        completion_status = "INCOMPLETE"
        reasons.append("missing_verdict_line")
    elif any(v is None for _, v in verdict_hits):
        completion_status = "UNPARSEABLE"
        reasons.append("unknown_verdict_token")
    elif len(verdict_hits) != 1:
        completion_status = "UNPARSEABLE"
        reasons.append("multiple_verdict_lines")
    else:
        idx, model_verdict = verdict_hits[0]
        if not non_empty_idx or idx != non_empty_idx[-1]:
            completion_status = "UNPARSEABLE"
            reasons.append("verdict_not_last_nonempty_line")
            model_verdict = None
        if len(any_matches) > 1:
            completion_status = "UNPARSEABLE"
            reasons.append("multiple_verdict_tokens_in_body")
            model_verdict = None

    if completion_status != "COMPLETE":
        model_verdict = None

    return {
        "completion_status": completion_status,
        "model_verdict": model_verdict,
        "parse_reasons": reasons,
        "verdict_line_count": len(verdict_hits),
        "raw_sha256": sha256_text(text),
    }


def validate_structured_findings(findings: Sequence[Mapping[str, Any]]) -> dict:
    """Validate parsed findings; malformed critical fields are not silent drops."""
    errors: list[dict] = []
    must_fix = 0
    known_debt = 0
    for i, f in enumerate(findings or []):
        cutline = (f.get("cutline") or "").strip()
        issue = (f.get("issue") or "").strip()
        evidence = (f.get("evidence_gap") or f.get("evidence_needed") or "").strip()
        action = (f.get("minimal_action") or "").strip()
        trigger = (f.get("upgrade_trigger") or "").strip()
        if cutline == "Must Fix":
            must_fix += 1
        if cutline == "Known Debt":
            known_debt += 1
        missing_fields = []
        if not cutline:
            missing_fields.append("Cutline")
        if not evidence:
            missing_fields.append("Evidence needed")
        if not action:
            missing_fields.append("Minimal action")
        if missing_fields:
            errors.append({
                "type": "malformed_finding",
                "finding_index": i,
                "issue": issue,
                "missing_fields": missing_fields,
            })
        if cutline == "Known Debt" and not trigger:
            errors.append({
                "type": "known_debt_missing_upgrade_trigger",
                "finding_index": i,
                "issue": issue,
            })
    return {
        "ok": not errors,
        "errors": errors,
        "must_fix_count": must_fix,
        "known_debt_count": known_debt,
    }


def has_audit_coverage_proof(text: str, findings: Sequence[Mapping[str, Any]]) -> bool:
    """PASS requires proven audit completeness, not empty silence."""
    if _COVERAGE_RE.search(text or ""):
        return True
    for f in findings or []:
        cutline = (f.get("cutline") or "").strip()
        evidence = (f.get("evidence_gap") or f.get("evidence_needed") or "").strip()
        action = (f.get("minimal_action") or "").strip()
        if cutline and evidence and action:
            return True
    return False


def semantic_leg_from_llm(
    *,
    audit_text: str,
    findings: Sequence[Mapping[str, Any]],
    completion_meta: Optional[Mapping[str, Any]] = None,
    strict_known_debt_trigger: bool = True,
) -> dict:
    """Derive the LLM semantic leg (real PASS/BLOCK inside claim scope)."""
    parsed = parse_model_completion(audit_text)
    completion_meta = dict(completion_meta or {})
    finish_reason = completion_meta.get("finish_reason")
    http_status = completion_meta.get("http_status")

    reasons: list[str] = list(parsed["parse_reasons"])
    completion_status = parsed["completion_status"]
    model_verdict = parsed["model_verdict"]

    if "finish_reason" in completion_meta:
        fr = completion_meta.get("finish_reason")
        if fr is None or fr == "":
            completion_status = "INCOMPLETE"
            model_verdict = None
            reasons.append("finish_reason_missing")
        elif str(fr).lower() != "stop":
            completion_status = (
                "TRUNCATED" if str(fr).lower() == "length" else "INCOMPLETE"
            )
            model_verdict = None
            reasons.append(f"finish_reason={fr}")

    if http_status is not None and int(http_status) != 200:
        completion_status = "ERROR"
        model_verdict = None
        reasons.append(f"http_status={http_status}")

    finding_val = validate_structured_findings(findings)
    raw_must_fix = bool(re.search(r"must fix", audit_text or "", re.IGNORECASE))
    has_must = finding_val["must_fix_count"] > 0 or raw_must_fix

    semantic = model_verdict
    override = None

    if completion_status != "COMPLETE" or semantic is None:
        semantic = "BLOCK"
        override = "incomplete_or_unparseable_model_output: " + ",".join(
            reasons or ["unknown"]
        )
    elif has_must and semantic != "BLOCK":
        override = f"model said {semantic} but output contains Must Fix findings"
        semantic = "BLOCK"
    elif finding_val["errors"] and strict_known_debt_trigger:
        if semantic in ("PASS", "PASS_WITH_DEBT"):
            override = "structured_finding_validation_failed"
            semantic = "BLOCK"
    elif semantic in ("PASS", "PASS_WITH_DEBT") and not has_audit_coverage_proof(
        audit_text, findings
    ):
        override = "hollow_pass_without_coverage_or_evidence_summary"
        semantic = "BLOCK"
    elif semantic == "PASS" and finding_val["known_debt_count"] > 0:
        override = "model said PASS but Known Debt findings present"
        semantic = "BLOCK"

    return {
        "llm_semantic_verdict": semantic,
        "model_verdict": model_verdict,
        "completion_status": completion_status,
        "verdict_override": override,
        "parse_reasons": reasons,
        "finding_validation": finding_val,
        "raw_sha256": parsed["raw_sha256"],
        "has_must_fix": has_must,
        "has_coverage_proof": has_audit_coverage_proof(audit_text, findings),
    }


def default_ceiling_for_tier(risk_tier: str, entry: str = "review") -> str:
    tier = (risk_tier or "normal").lower()
    if tier == "production":
        return "PRODUCTION_LIVE"
    if tier == "quant":
        return "QUANT_PROMOTION"
    if entry == "gate" and tier in ("normal", "auto"):
        return "L2_LINT"
    return "EPISTEMIC_CLAIM"


def required_obligations_for(
    *,
    risk_tier: str,
    claim_scope: str,
    authority_ceiling: str,
    entry: str,
) -> list[str]:
    tier = (risk_tier or "normal").lower()
    if entry == "gate" and tier in ("normal", "auto"):
        # Pure L2 markdown lint path — no Brooks-Lint (L0) obligation.
        return ["l2_lint_clean", "authority_ceiling_declared"]

    obs = [
        "llm_completion_complete",
        "single_terminal_verdict",
        "no_must_fix",
        "audit_coverage_proof",
    ]
    # Claim-bearing review/run must prove Brooks-Lint (L0) ran (or scope-refused).
    if entry in ("review", "run"):
        obs.insert(0, "l0_brooks_ran")
    if tier in HIGH_RISK_TIERS or authority_ceiling in (
        "QUANT_PROMOTION",
        "PRODUCTION_LIVE",
    ):
        obs.extend([
            "independent_reviewer",
            "executable_evidence",
            "subject_binding",
        ])
    if authority_ceiling == "PRODUCTION_LIVE" or tier == "production":
        obs.extend([
            "production_path_proof",
            "order_boundary_trap",
            "account_invariants",
        ])
    if authority_ceiling == "QUANT_PROMOTION" or tier == "quant":
        obs.extend([
            "quant_gate_tools_present",
            "quant_gate_no_skip",
        ])
    return obs


def _public_leg(value: str, required: bool) -> str:
    """Map a leg to public PASS/PASS_WITH_DEBT/BLOCK; non-required → PASS."""
    if not required:
        return "PASS"
    v = normalize_verdict_token(value) or "UNKNOWN"
    if v in FAIL_CLOSED_TOKENS or v not in PUBLIC_VERDICTS:
        return "BLOCK"
    return v


def finalize_authority(
    *,
    claim_text: str = "",
    claim_scope: str = "document_logic",
    risk_tier: str = "normal",
    entry: str = "review",
    model_verdict: Optional[str] = None,
    llm_semantic_verdict: Optional[str] = None,
    executable_evidence_verdict: str = "UNKNOWN",
    production_path_verdict: str = "UNKNOWN",
    subject_binding_verdict: str = "UNKNOWN",
    independence_verdict: str = "PASS",
    completion_status: str = "COMPLETE",
    required_obligations: Optional[Sequence[str]] = None,
    satisfied_obligations: Optional[Sequence[str]] = None,
    subject_manifest: Optional[Mapping[str, Any]] = None,
    subject_hashes: Optional[Mapping[str, str]] = None,
    evidence_hashes: Optional[Mapping[str, str]] = None,
    verdict_override: Optional[str] = None,
    requested_ceiling: Optional[str] = None,
) -> dict:
    """Compose final authority. Pure function.

    final_verdict = min(
        llm_semantic_verdict,
        executable_evidence_verdict,   # high-risk only
        production_path_verdict,       # production only
        subject_binding_verdict,       # high-risk only
        independence_verdict,          # high-risk only
    )

    Any UNKNOWN / SKIP / UNSUPPORTED / TRUNCATED / ERROR / missing obligation
    on a high-risk path → BLOCK + nonzero exit.
    """
    tier = (risk_tier or "normal").lower()
    if tier not in RISK_TIERS:
        tier = "normal"
    high = tier in HIGH_RISK_TIERS

    ceiling = requested_ceiling or default_ceiling_for_tier(tier, entry=entry)
    if ceiling not in AUTHORITY_CEILINGS:
        ceiling = "NONE"

    llm_v = normalize_verdict_token(llm_semantic_verdict or model_verdict) or "BLOCK"
    model_v = normalize_verdict_token(model_verdict)

    need_exec = high or ceiling in ("QUANT_PROMOTION", "PRODUCTION_LIVE")
    need_prod = tier == "production" or ceiling == "PRODUCTION_LIVE"
    need_bind = high or ceiling in ("QUANT_PROMOTION", "PRODUCTION_LIVE")
    need_indep = high or ceiling in ("QUANT_PROMOTION", "PRODUCTION_LIVE")

    exec_v = _public_leg(executable_evidence_verdict, need_exec)
    prod_v = _public_leg(production_path_verdict, need_prod)
    bind_v = _public_leg(subject_binding_verdict, need_bind)
    indep_raw = normalize_verdict_token(independence_verdict) or "UNKNOWN"
    if need_indep:
        indep_v = "PASS" if indep_raw == "PASS" else "BLOCK"
    else:
        indep_v = "PASS"

    if completion_status not in (None, "COMPLETE", "complete"):
        llm_v = "BLOCK"
        if not verdict_override:
            verdict_override = f"completion_status={completion_status}"

    effective = min_verdict(llm_v, exec_v, prod_v, bind_v, indep_v)

    req = list(required_obligations or required_obligations_for(
        risk_tier=tier,
        claim_scope=claim_scope,
        authority_ceiling=ceiling,
        entry=entry,
    ))
    sat = set(satisfied_obligations or [])

    if (
        llm_v in ("PASS", "PASS_WITH_DEBT")
        and completion_status in (None, "COMPLETE", "complete")
    ):
        sat.update({
            "llm_completion_complete",
            "single_terminal_verdict",
            "audit_coverage_proof",
        })
    if llm_v in ("PASS", "PASS_WITH_DEBT") and not (
        verdict_override and "Must Fix" in (verdict_override or "")
    ):
        sat.add("no_must_fix")
    if indep_raw == "PASS":
        sat.add("independent_reviewer")
    if exec_v == "PASS" and need_exec:
        sat.add("executable_evidence")
    if prod_v == "PASS" and need_prod:
        sat.update({
            "production_path_proof",
            "order_boundary_trap",
            "account_invariants",
        })
    if bind_v == "PASS" and need_bind:
        sat.add("subject_binding")
    if entry == "gate" and tier in ("normal", "auto") and llm_v in (
        "PASS", "PASS_WITH_DEBT",
    ):
        sat.update({"l2_lint_clean", "authority_ceiling_declared"})

    missing = [o for o in req if o not in sat]

    if missing and (high or ceiling in ("QUANT_PROMOTION", "PRODUCTION_LIVE")):
        effective = "BLOCK"
        if not verdict_override:
            verdict_override = "missing_obligations: " + ",".join(missing)
    elif missing and entry in ("review", "run") and "l0_brooks_ran" in missing:
        # Without L0 proof, claim-bearing review/run cannot PASS / PASS_WITH_DEBT.
        effective = "BLOCK"
        if not verdict_override:
            verdict_override = "missing_obligations: " + ",".join(missing)
    elif missing and entry == "gate" and "l2_lint_clean" in missing:
        effective = "BLOCK"

    # Capital: only full PASS, no missing obs, eligible ceiling, independent.
    capital = "NONE"
    eligible = CEILING_CAPITAL_ELIGIBILITY.get(ceiling, "NONE")
    if (
        effective == "PASS"
        and not missing
        and eligible != "NONE"
        and indep_raw == "PASS"
        and completion_status in (None, "COMPLETE", "complete")
    ):
        capital = eligible
    if effective == "PASS_WITH_DEBT":
        capital = "NONE"

    # Epistemic review/run: always declare EPISTEMIC ceiling + no capital.
    effective_ceiling = ceiling
    if entry in ("review", "run") and not high:
        effective_ceiling = "EPISTEMIC_CLAIM"
        capital = "NONE"
    if entry == "gate" and tier in ("normal", "auto"):
        effective_ceiling = "L2_LINT"
        capital = "NONE"

    # Exit codes
    if high or ceiling in ("PRODUCTION_LIVE", "QUANT_PROMOTION"):
        # High-risk: only PASS with zero missing obligations → 0
        exit_code = 0 if (effective == "PASS" and not missing) else 1
        if effective == "PASS_WITH_DEBT":
            capital = "NONE"
            exit_code = 1
    else:
        exit_code = 0 if effective in ("PASS", "PASS_WITH_DEBT") else 1
        capital = "NONE"

    exit_reason_parts = []
    if verdict_override:
        exit_reason_parts.append(verdict_override)
    if missing and (high or ceiling in ("PRODUCTION_LIVE", "QUANT_PROMOTION")):
        exit_reason_parts.append("missing:" + ",".join(missing))
    if model_v and effective != model_v:
        exit_reason_parts.append(f"composed:{model_v}->{effective}")
    exit_code_reason = "; ".join(exit_reason_parts) if exit_reason_parts else (
        "pass" if exit_code == 0 else f"effective={effective}"
    )

    return {
        "schema_version": "falsify.authority.v1",
        "claim_text": claim_text or "",
        "claim_scope": claim_scope,
        "risk_tier": tier,
        "entry": entry,
        "model_verdict": model_v,
        "llm_semantic_verdict": llm_v,
        "executable_evidence_verdict": exec_v if need_exec else "N/A",
        "production_path_verdict": prod_v if need_prod else "N/A",
        "subject_binding_verdict": bind_v if need_bind else "N/A",
        "independence_verdict": indep_raw,
        "effective_verdict": effective,
        "authority_ceiling": effective_ceiling,
        "capital_authority": capital,
        "required_obligations": req,
        "satisfied_obligations": sorted(sat),
        "missing_obligations": missing,
        "subject_manifest": dict(subject_manifest or {}),
        "subject_hashes": dict(subject_hashes or {}),
        "evidence_hashes": dict(evidence_hashes or {}),
        "completion_status": completion_status,
        "verdict_override": verdict_override,
        "exit_code": exit_code,
        "exit_code_reason": exit_code_reason,
        "legs": {
            "llm_semantic": llm_v,
            "executable_evidence": exec_v if need_exec else "N/A",
            "production_path": prod_v if need_prod else "N/A",
            "subject_binding": bind_v if need_bind else "N/A",
            "independence": indep_v if need_indep else (
                "WARN" if indep_raw != "PASS" else "N/A"
            ),
        },
    }


def exit_code_for_decision(decision: Mapping[str, Any]) -> int:
    return int(decision.get("exit_code", 1))


# Marker used by matrix tests to prove shared kernel import.
KERNEL_ID = "falsify.authority_kernel.finalize_authority"
