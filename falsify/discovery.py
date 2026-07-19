"""Fail-closed, resumable state machine for Alpha Discovery Factory."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "falsify.discovery.v1"
ALLOWED_LEADING_CLASSES = {"orderbook", "funding_rate", "open_interest", "implied_vol", "capital_flow", "liquidation", "leverage_ratio", "basis_spread", "options_flow", "other_leading"}
TERMINAL = {"KILL", "NO_DECISION_DATA_NOT_AVAILABLE", "NO_DECISION_PIT_UNCLOSED", "NO_DECISION_SCHEMA_MISMATCH", "NO_DECISION_N_TOO_LOW", "PROMOTION_ELIGIBLE"}
TRANSITIONS = {
    "QUEUED": {"REGISTERED"},
    "REGISTERED": {"DATA_CLOSURE"},
    "DATA_CLOSURE": {"FALSIFIER_FROZEN", *TERMINAL},
    "FALSIFIER_FROZEN": {"CHEAP_FALSIFIER"},
    "CHEAP_FALSIFIER": {"MECHANISM_SEED_SURVIVES", *TERMINAL},
    "MECHANISM_SEED_SURVIVES": {"PROMOTION_GATE", *TERMINAL},
    "PROMOTION_GATE": {"PROMOTION_ELIGIBLE", "KILL"},
}


class DiscoveryError(ValueError):
    """A queue or intake violates a discovery-factory invariant."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_registration(registration: dict[str, Any]) -> list[str]:
    required = ("id", "payer", "leading_factor_class", "primary_signal_description", "data_source", "data_source_url", "leading_justification", "lagging_component_check", "venue", "signal_semantics", "horizon", "frozen_next_gate", "kill_condition")
    errors = [f"missing {field}" for field in required if not registration.get(field)]
    if registration.get("leading_factor_class") not in ALLOWED_LEADING_CLASSES:
        errors.append("leading_factor_class is not allowed")
    if registration.get("data_source_url") and not registration["data_source_url"].startswith(("https://", "http://")):
        errors.append("data_source_url must be http(s)")
    check = registration.get("lagging_component_check", "").lower()
    if check and "not" not in check and "only" not in check:
        errors.append("lagging_component_check must restrict lagging inputs")
    if registration.get("parent_id") and not registration.get("mechanism_change"):
        errors.append("parent_id requires mechanism_change")
    return errors


def fingerprint(registration: dict[str, Any]) -> str:
    keys = ("payer", "leading_factor_class", "venue", "signal_semantics", "horizon")
    return _hash({key: registration.get(key) for key in keys})


def validate_queue(queue: dict[str, Any]) -> None:
    if queue.get("schema_version") != SCHEMA_VERSION or not isinstance(queue.get("items"), list):
        raise DiscoveryError("unsupported queue schema")
    if sum(bool(item.get("active")) for item in queue["items"]) > 1:
        raise DiscoveryError("only one active work item is allowed")
    seen_ids, seen_fingerprints = set(), {}
    for item in queue["items"]:
        if not item.get("id") or item["id"] in seen_ids:
            raise DiscoveryError("item ids must be unique and non-empty")
        seen_ids.add(item["id"])
        if item.get("state") != "QUEUED":
            errors = validate_registration(item.get("registration", {}))
            if errors:
                raise DiscoveryError("invalid registration: " + "; ".join(errors))
        value = item.get("family_fingerprint")
        if value in seen_fingerprints and not item.get("registration", {}).get("mechanism_change"):
            raise DiscoveryError("duplicate family fingerprint")
        if value:
            seen_fingerprints[value] = item["id"]


def activate_next(queue: dict[str, Any]) -> str | None:
    if any(item.get("active") for item in queue["items"]):
        return None
    for item in queue["items"]:
        if item.get("state") == "QUEUED":
            item["active"] = True
            item["activated_at_utc"] = _now()
            return item["id"]
    return None


def transition(queue: dict[str, Any], candidate_id: str, target: str, evidence: dict[str, Any]) -> dict[str, Any]:
    validate_queue(queue)
    item = next((candidate for candidate in queue["items"] if candidate["id"] == candidate_id), None)
    if not item:
        raise DiscoveryError("unknown candidate")
    current = item.get("state", "QUEUED")
    if target not in TRANSITIONS.get(current, set()):
        raise DiscoveryError(f"illegal transition {current} -> {target}")
    if not item.get("active"):
        raise DiscoveryError("only active candidate may transition")
    if target == "REGISTERED":
        errors = validate_registration(item["registration"])
        if errors:
            raise DiscoveryError("registration rejected: " + "; ".join(errors))
        item["family_fingerprint"] = fingerprint(item["registration"])
    if target in TERMINAL and not evidence.get("artifact_path"):
        raise DiscoveryError("terminal verdict requires artifact_path")
    if target == "PROMOTION_ELIGIBLE":
        metrics = evidence.get("metrics", {})
        if metrics.get("sharpe", 0) <= 1.5 or metrics.get("calmar", 0) < 10:
            raise DiscoveryError("promotion requires Sharpe > 1.5 and Calmar >= 10")
        hash_keys = ("source_manifest_hash", "return_basis_hash", "intake_hash")
        if any(not evidence.get(key) for key in hash_keys):
            raise DiscoveryError("promotion requires source, return basis, and intake hashes")
    event = {"at_utc": _now(), "from": current, "to": target, "evidence": evidence, "evidence_hash": _hash(evidence)}
    item.setdefault("history", []).append(event)
    item["state"] = target
    if target in TERMINAL:
        item["active"] = False
        item["terminal_at_utc"] = event["at_utc"]
        activate_next(queue)
    queue["updated_at_utc"] = event["at_utc"]
    validate_queue(queue)
    return event


def strict_summary(queue: dict[str, Any]) -> dict[str, Any]:
    valid, excluded = [], []
    for item in queue["items"]:
        if item.get("strict_leading_compliant", True) and not validate_registration(item.get("registration", {})):
            valid.append(item)
        else:
            excluded.append(item)
    return {"schema_version": SCHEMA_VERSION, "strict_campaign_count": len(valid), "strict_terminal_count": sum(item.get("state") in TERMINAL for item in valid), "promotion_eligible_count": sum(item.get("state") == "PROMOTION_ELIGIBLE" for item in valid), "excluded_historical_ids": [item["id"] for item in excluded], "queue_hash": _hash(queue)}
"""Fail-closed, resumable state machine for Alpha Discovery Factory."""
