"""Production-path adapter contract for Falsify.

Proves (or honestly fails to prove) the control flow:

    scheduler/job
      → Hermes resolver
      → wrapper
      → production entrypoint
      → main --live same control flow
      → unique order-boundary submit trap
      → projected/final account invariants

This module is pure evaluation + in-process trap fixtures. It never places
real orders. When the Pro production gate is not installed in this repo, the
adapter returns UNSUPPORTED / BLOCK — it does not fake a green production PASS.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Callable, Mapping, Optional, Sequence

SCHEMA_VERSION = "falsify.production_adapter.v1"

PATH_STAGES = (
    "scheduler_job",
    "hermes_resolver",
    "wrapper",
    "production_entrypoint",
    "main_live_control_flow",
    "order_boundary_submit_trap",
    "account_invariants",
)

# Pro gate is intentionally not bundled in OSS. Adapter stays honest.
PRO_PRODUCTION_GATE_AVAILABLE = False
PRO_PRODUCTION_GATE_REASON = (
    "Pro production gate not installed in this repository; "
    "adapter evaluates fixtures/contracts only and cannot grant live authority"
)


def _sha(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class SubmitTrap:
    """Records submit attempts; never forwards to a real venue."""

    def __init__(self) -> None:
        self.attempts: list[dict] = []
        self.forwarded_to_venue = 0

    def submit(self, order: Mapping[str, Any]) -> dict:
        rec = {"order": dict(order), "trapped": True, "forwarded": False}
        self.attempts.append(rec)
        return {"status": "TRAPPED", "order_id": None, "forwarded": False}

    @property
    def real_orders(self) -> int:
        return self.forwarded_to_venue


def evaluate_production_path(evidence: Mapping[str, Any]) -> dict:
    """Pure evaluation of a production-path evidence document.

    Expected evidence keys (all optional; missing → fail-closed on high path):

    - job: {exists, id, script_path, script_resolvable}
    - resolver: {ok, target}
    - wrapper: {path, resolvable}
    - entrypoint: {path, reachable, live_flag}
    - control_flow: {same_as_main_live}
    - order_boundary: {reachable, trapped, real_orders, trap_proof}
    - legs: [{id, disposition}]
    - account: orphans / unexpected_positions / open_orders /
      final_book_within_tolerance / partial_book_miscount
    - pro_gate: {available, verdict}
    """
    evidence = dict(evidence or {})
    issues: list[str] = []
    stage_status: dict[str, str] = {}

    job = dict(evidence.get("job") or {})
    if not job.get("exists"):
        issues.append("scheduler_job_missing")
        stage_status["scheduler_job"] = "BLOCK"
    elif job.get("exists") and not job.get("script_resolvable"):
        issues.append("job_exists_but_script_unresolvable")
        stage_status["scheduler_job"] = "BLOCK"
    else:
        stage_status["scheduler_job"] = "PASS"

    resolver = dict(evidence.get("resolver") or {})
    stage_status["hermes_resolver"] = "PASS" if resolver.get("ok") else "BLOCK"
    if stage_status["hermes_resolver"] != "PASS":
        issues.append("hermes_resolver_failed")

    wrapper = dict(evidence.get("wrapper") or {})
    if not wrapper.get("resolvable"):
        issues.append("wrapper_missing_or_unresolvable")
        stage_status["wrapper"] = "BLOCK"
    else:
        stage_status["wrapper"] = "PASS"

    entry = dict(evidence.get("entrypoint") or {})
    if not (entry.get("reachable") and entry.get("live_flag")):
        issues.append("production_entrypoint_not_reachable_with_live")
        stage_status["production_entrypoint"] = "BLOCK"
    else:
        stage_status["production_entrypoint"] = "PASS"

    flow = dict(evidence.get("control_flow") or {})
    if not flow.get("same_as_main_live"):
        issues.append("control_flow_not_same_as_main_live")
        stage_status["main_live_control_flow"] = "BLOCK"
    else:
        stage_status["main_live_control_flow"] = "PASS"

    boundary = dict(evidence.get("order_boundary") or {})
    real_orders = int(boundary.get("real_orders") or 0)
    if not boundary.get("reachable"):
        issues.append("order_boundary_not_reachable")
        stage_status["order_boundary_submit_trap"] = "BLOCK"
    elif not boundary.get("trapped") or not boundary.get("trap_proof"):
        issues.append("order_boundary_not_trapped")
        stage_status["order_boundary_submit_trap"] = "BLOCK"
    elif real_orders != 0:
        issues.append(f"real_orders_nonzero={real_orders}")
        stage_status["order_boundary_submit_trap"] = "BLOCK"
    else:
        stage_status["order_boundary_submit_trap"] = "PASS"

    legs = list(evidence.get("legs") or [])
    for leg in legs:
        disp = (leg.get("disposition") or "").lower()
        if not disp:
            issues.append(f"leg_missing_disposition:{leg.get('id')}")

    account = dict(evidence.get("account") or {})
    orphans = int(account.get("orphans") or 0)
    unexpected = int(account.get("unexpected_positions") or 0)
    open_orders = int(account.get("open_orders") or 0)
    book_ok = bool(account.get("final_book_within_tolerance"))
    miscount = bool(account.get("partial_book_miscount"))

    if orphans != 0:
        issues.append(f"orphans={orphans}")
    if unexpected != 0:
        issues.append(f"unexpected_positions={unexpected}")
    if open_orders != 0:
        issues.append(f"open_orders={open_orders}")
    if not book_ok:
        issues.append("final_book_out_of_tolerance")
    if miscount:
        issues.append("dust_or_on_target_skip_miscounted_as_partial_book")

    if any(not (leg.get("disposition") or "").strip() for leg in legs):
        stage_status["account_invariants"] = "BLOCK"
    elif orphans or unexpected or open_orders or not book_ok or miscount:
        stage_status["account_invariants"] = "BLOCK"
    else:
        stage_status["account_invariants"] = "PASS"

    pro = dict(evidence.get("pro_gate") or {})
    pro_available = bool(pro.get("available", PRO_PRODUCTION_GATE_AVAILABLE))
    if not pro_available:
        # Honest: fixture path can validate stages, but live authority is unsupported.
        overall = "BLOCK" if issues else "UNSUPPORTED"
    else:
        overall = (
            "PASS"
            if not issues and all(stage_status.get(s) == "PASS" for s in PATH_STAGES)
            else "BLOCK"
        )

    capital_authority = "NONE"
    if overall == "PASS" and pro_available:
        capital_authority = "LIVE"

    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": overall,
        "stage_status": stage_status,
        "issues": issues,
        "real_orders": real_orders,
        "trap_proof": bool(boundary.get("trap_proof")) and real_orders == 0,
        "pro_gate_available": pro_available,
        "pro_gate_reason": None if pro_available else PRO_PRODUCTION_GATE_REASON,
        "capital_authority": capital_authority,
        "evidence_sha256": _sha(evidence),
        "path_stages": list(PATH_STAGES),
    }


def run_trapped_simulation(
    plan_legs: Optional[Sequence[Mapping[str, Any]]] = None,
    *,
    account_seed: Optional[Mapping[str, Any]] = None,
    submit_hook: Optional[Callable[[SubmitTrap, Mapping[str, Any]], None]] = None,
) -> dict:
    """In-process simulation: every submit goes through SubmitTrap."""
    trap = SubmitTrap()
    legs_in = list(plan_legs or [])
    dispositions = []
    for leg in legs_in:
        leg = dict(leg)
        kind = (leg.get("kind") or "order").lower()
        if kind == "dust":
            dispositions.append({"id": leg.get("id"), "disposition": "skipped_dust"})
            continue
        if kind == "on_target":
            dispositions.append({"id": leg.get("id"), "disposition": "skipped_on_target"})
            continue
        order = {
            "id": leg.get("id"),
            "symbol": leg.get("symbol"),
            "side": leg.get("side"),
            "qty": leg.get("qty"),
        }
        if submit_hook:
            submit_hook(trap, order)
        else:
            trap.submit(order)
        dispositions.append({"id": leg.get("id"), "disposition": "filled_trapped"})

    seed = dict(account_seed or {})
    account = {
        "orphans": int(seed.get("orphans", 0)),
        "unexpected_positions": int(seed.get("unexpected_positions", 0)),
        "open_orders": int(seed.get("open_orders", 0)),
        "final_book_within_tolerance": bool(seed.get("final_book_within_tolerance", True)),
        "dust_skips": sum(1 for d in dispositions if d["disposition"] == "skipped_dust"),
        "on_target_skips": sum(
            1 for d in dispositions if d["disposition"] == "skipped_on_target"
        ),
        "partial_book_miscount": bool(seed.get("partial_book_miscount", False)),
    }
    evidence = {
        "job": {
            "exists": True,
            "id": "fixture-job",
            "script_path": "/fixture/wrapper.sh",
            "script_resolvable": True,
        },
        "resolver": {"ok": True, "target": "fixture-target"},
        "wrapper": {"path": "/fixture/wrapper.sh", "resolvable": True},
        "entrypoint": {
            "path": "python -m fixture_bot",
            "reachable": True,
            "live_flag": True,
        },
        "control_flow": {"same_as_main_live": True},
        "order_boundary": {
            "reachable": True,
            "trapped": True,
            "trap_proof": True,
            "real_orders": trap.real_orders,
            "trapped_attempts": len(trap.attempts),
        },
        "legs": dispositions,
        "account": account,
        "pro_gate": {"available": False, "verdict": None},
    }
    result = evaluate_production_path(evidence)
    result["trap_attempts"] = deepcopy(trap.attempts)
    result["evidence"] = evidence
    return result


def fixture_evidence_ok_with_dust() -> dict:
    """Legal dust/on-target SKIP must not be miscounted as partial-book."""
    return run_trapped_simulation(
        [
            {"id": "L1", "kind": "order", "symbol": "BTC", "side": "buy", "qty": 1},
            {"id": "L2", "kind": "dust", "symbol": "ETH", "side": "sell", "qty": 0.0001},
            {"id": "L3", "kind": "on_target", "symbol": "SOL", "side": "buy", "qty": 0},
        ],
        account_seed={
            "orphans": 0,
            "unexpected_positions": 0,
            "open_orders": 0,
            "final_book_within_tolerance": True,
            "partial_book_miscount": False,
        },
    )


def fixture_evidence_wrapper_missing() -> dict:
    ev = deepcopy(fixture_evidence_ok_with_dust()["evidence"])
    ev["wrapper"] = {"path": None, "resolvable": False}
    ev["job"] = {
        "exists": True,
        "id": "job-1",
        "script_path": "/missing/wrapper.sh",
        "script_resolvable": False,
    }
    return evaluate_production_path(ev)


def fixture_evidence_orphan() -> dict:
    ev = deepcopy(fixture_evidence_ok_with_dust()["evidence"])
    ev["account"]["orphans"] = 1
    return evaluate_production_path(ev)


def fixture_evidence_book_residue() -> dict:
    ev = deepcopy(fixture_evidence_ok_with_dust()["evidence"])
    ev["account"]["final_book_within_tolerance"] = False
    return evaluate_production_path(ev)
