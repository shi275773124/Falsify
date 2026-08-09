import pytest

from falsify.discovery import DiscoveryError, SCHEMA_VERSION, activate_next, strict_summary, transition, validate_queue


def registration(candidate_id="LF-001"):
    return {"id": candidate_id, "payer": "leveraged futures participants", "leading_factor_class": "open_interest", "primary_signal_description": "OI crowding change is the sole alpha driver.", "data_source": "CFTC Traders in Financial Futures", "data_source_url": "https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm", "leading_justification": "Positioning is capital committed before the modeled return.", "lagging_component_check": "Price is used only for return measurement and costs, not the signal.", "venue": "CME Bitcoin futures", "signal_semantics": "weekly leveraged-funds net-position change", "horizon": "Friday release through next Friday", "frozen_next_gate": "official coverage and availability-time audit", "kill_condition": "coverage or PIT contract failure"}


def candidate(candidate_id="LF-001", state="QUEUED", active=False, strict=True):
    return {"id": candidate_id, "state": state, "active": active, "registration": registration(candidate_id), "strict_leading_compliant": strict}


def queue(*items):
    value = {"schema_version": SCHEMA_VERSION, "items": list(items)}
    validate_queue(value)
    return value


def test_registration_rejects_missing_leading_declaration():
    item = candidate()
    item["registration"].pop("data_source_url")
    value = queue(item)
    activate_next(value)
    with pytest.raises(DiscoveryError, match="data_source_url"):
        transition(value, "LF-001", "REGISTERED", {})


def test_terminal_kill_activates_next_independent_candidate():
    first, second = candidate("LF-001"), candidate("LF-002")
    second["registration"]["leading_factor_class"] = "implied_vol"
    second["registration"]["signal_semantics"] = "monthly IV term structure"
    value = queue(first, second)
    assert activate_next(value) == "LF-001"
    transition(value, "LF-001", "REGISTERED", {})
    transition(value, "LF-001", "DATA_CLOSURE", {})
    transition(value, "LF-001", "KILL", {"artifact_path": "artifacts/LF-001.json"})
    assert first["state"] == "KILL"
    assert second["active"] is True


def test_terminal_candidate_cannot_be_resurrected():
    item = candidate()
    value = queue(item)
    activate_next(value)
    transition(value, "LF-001", "REGISTERED", {})
    transition(value, "LF-001", "DATA_CLOSURE", {})
    transition(value, "LF-001", "NO_DECISION_PIT_UNCLOSED", {"artifact_path": "artifacts/pit.json"})
    with pytest.raises(DiscoveryError, match="illegal transition"):
        transition(value, "LF-001", "FALSIFIER_FROZEN", {})


def test_duplicate_fingerprint_is_rejected_without_mechanism_change():
    first, second = candidate("LF-001", "REGISTERED"), candidate("LF-002", "REGISTERED")
    first["family_fingerprint"] = second["family_fingerprint"] = "same"
    with pytest.raises(DiscoveryError, match="duplicate family fingerprint"):
        queue(first, second)


def test_promotion_requires_metrics_and_all_hashes():
    item = candidate()
    value = queue(item)
    activate_next(value)
    for target in ("REGISTERED", "DATA_CLOSURE", "FALSIFIER_FROZEN", "CHEAP_FALSIFIER", "MECHANISM_SEED_SURVIVES", "PROMOTION_GATE"):
        evidence = {"artifact_path": "artifacts/cheap.json"} if target == "MECHANISM_SEED_SURVIVES" else {}
        transition(value, "LF-001", target, evidence)
    with pytest.raises(DiscoveryError, match="Sharpe"):
        transition(value, "LF-001", "PROMOTION_ELIGIBLE", {"artifact_path": "artifacts/gate.json", "metrics": {"sharpe": 1.5, "calmar": 10}})
    evidence = {"artifact_path": "artifacts/gate.json", "metrics": {"sharpe": 1.51, "calmar": 10}, "source_manifest_hash": "source", "return_basis_hash": "returns", "intake_hash": "intake"}
    transition(value, "LF-001", "PROMOTION_ELIGIBLE", evidence)
    assert item["state"] == "PROMOTION_ELIGIBLE"


def test_strict_summary_excludes_legacy_price_led_lines():
    strict, legacy = candidate("LF-001"), candidate("ADF-LF-001", strict=False)
    summary = strict_summary(queue(strict, legacy))
    assert summary["strict_campaign_count"] == 1
    assert summary["excluded_historical_ids"] == ["ADF-LF-001"]
import pytest
