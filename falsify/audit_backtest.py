"""Pure-read verifier for frozen backtest packs.

This module deliberately uses only the Python standard library and never imports
research runners, executors, order, broker, wallet, or live-trading modules.  It
implements the Design Gate A rem3 contract as a mechanical data/claim sieve.
Its PASS token is not a strategy, deployment, paper, live, or capital authority.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


PASS = "BACKTEST_PACK_CHECK_PASS"
FAIL = "BACKTEST_PACK_CHECK_FAIL"
BLOCK = "BACKTEST_PACK_CHECK_BLOCK"
DIAG = "ENGINE_CHECK_DIAG"
ACCEPTANCE_PROFILES = frozenset({"strict", "data-only"})
NON_ACCEPTANCE_PROFILES = frozenset({"cheap", "catalog-diag"})
ALL_PROFILES = ACCEPTANCE_PROFILES | NON_ACCEPTANCE_PROFILES
CATALOG_DIR = "数据资产目录"
ASSETS_NAME = "assets.tsv"
SOURCES_NAME = "sources.tsv"
REQUIRED_ROLES = (
    "manifest", "data_bindings", "universe", "calendar", "bar_index",
    "claim", "inventory", "provenance", "cli_contract", "attack_catalog",
)
DEFAULT_ROLE_PATHS = {
    "manifest": "PACK_MANIFEST.json",
    "data_bindings": "DATA_BINDINGS.json",
    "universe": "UNIVERSE.json",
    "calendar": "SESSION_CALENDAR.json",
    "bar_index": "BAR_INDEX.json",
    "claim": "CLAIM.json",
    "inventory": "INVENTORY.json",
    "provenance": "PROVENANCE.json",
    "cli_contract": "CLI_CONTRACT.md",
    "attack_catalog": "ATTACK_CATALOG.json",
    "fee_model": "FEE_MODEL.json",
    "slippage_model": "SLIPPAGE_MODEL.json",
    "pit_markers": "PIT_MARKERS.json",
    "trial_ledger": "TRIAL_LEDGER.json",
    "metrics": "METRICS.json",
    "gap_report": "GAP_REPORT.json",
}
CHECK_META = {
    "D0": ("pack_layout_snapshot", "CRITICAL"),
    "D1": ("asset_registration", "CRITICAL"),
    "D2": ("physical_path_hash_venue", "CRITICAL"),
    "D3": ("coverage_window", "CRITICAL"),
    "D4": ("universe_symbol_survivorship", "CRITICAL"),
    "D5": ("bar_timezone_session_alignment", "CRITICAL"),
    "D6": ("gaps_forward_fill", "CRITICAL"),
    "D7": ("lookahead_future_join", "CRITICAL"),
    "D8": ("fees_slippage_gross_net", "CRITICAL"),
    "D9": ("point_in_time_restatement", "CRITICAL"),
    "D10": ("source_provenance", "CRITICAL"),
    "D11": ("trial_count", "HIGH"),
    "D12": ("authority_ceiling_inventory_receipt", "CRITICAL"),
}
FORBIDDEN_VERDICTS = frozenset({
    "FOUNDATION_DESIGN_ACCEPTANCE", "GATE_A_PASS", "GATE_B_PASS",
    "PRODUCTION_AUDIT_PASS", "DEPLOY_AUTHORIZED", "CAPITAL_PASS", "LIVE_OK",
    "STRATEGY_PASS", "EDGE_CONFIRMED", "ACTIVATION_PACKAGE_PASS",
    "AUDIT_BACKTEST_IMPLEMENTATION_GATE_B_PASS",
})
NON_CLAIMS = [
    "not_strategy_is_good", "not_live_or_paper_auth", "not_capital_pass",
    "not_gate_a_b_inheritance", "not_production_audit_pass_authority",
    "not_deploy_authorization", "not_independent_falsify_audit",
    "not_runtime_activation", "not_falsify_backtest_run",
]
EXPECTED_ATTACK_CATALOG_ID = "falsify.audit_backtest.attack_catalog.v0.5-design-rem3-cheap-non-acceptance"


class AuditInputError(Exception):
    """A fail-closed input/layout error that maps to exit 2."""


@dataclass
class AuditConfig:
    root: Path
    profile: str = "strict"
    strict: bool = False
    vault_root: Path | None = None
    catalog_pin_assets_sha256: str | None = None
    catalog_pin_sources_sha256: str | None = None
    catalog_manifest: Path | None = None
    data_truth: Path | None = None
    vault_root_allowlist: list[Path] = field(default_factory=list)
    expect_pack_id: str | None = None
    out_json: Path | None = None
    out_md: Path | None = None
    run_attack_suite: bool = True
    preflight_errors: list[str] = field(default_factory=list)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8-sig") as f:
            return json.load(f)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuditInputError(f"unreadable or invalid JSON {path}: {exc}") from exc


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _inside(root: Path, rel: str) -> Path:
    rel_path = Path(rel)
    if rel_path.is_absolute() or ".." in rel_path.parts:
        raise AuditInputError(f"path escape outside pack root: {rel}")
    raw = root / rel_path
    cursor = raw
    while cursor != root:
        if cursor.is_symlink():
            raise AuditInputError(f"symlink input forbidden: {rel}")
        if cursor.parent == cursor:
            break
        cursor = cursor.parent
    candidate = raw.resolve(strict=False)
    if not _is_relative_to(candidate, root):
        raise AuditInputError(f"path escape outside pack root: {rel}")
    return candidate


def _tree_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix()):
        if path.is_symlink():
            raise AuditInputError(f"symlink input forbidden: {path.relative_to(root)}")
        if path.is_file():
            files.append(path)
    return files


def _tree_snapshot(root: Path) -> tuple[str, dict[str, str]]:
    hashes: dict[str, str] = {}
    h = hashlib.sha256()
    for path in _tree_files(root):
        rel = path.relative_to(root).as_posix()
        digest = _sha256(path)
        hashes[rel] = digest
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(digest.encode("ascii"))
        h.update(b"\n")
    return h.hexdigest(), hashes


def _check_records() -> dict[str, dict[str, Any]]:
    return {
        cid: {"id": cid, "name": name, "result": "PASS", "severity": sev, "errors": []}
        for cid, (name, sev) in CHECK_META.items()
    }


def _fail(checks: dict[str, dict[str, Any]], cid: str, message: str) -> None:
    checks[cid]["result"] = "FAIL"
    checks[cid]["errors"].append(message)


def _block_all(checks: dict[str, dict[str, Any]], message: str) -> None:
    checks["D0"]["result"] = "BLOCK"
    checks["D0"]["errors"].append(message)
    for cid in checks:
        if cid != "D0" and checks[cid]["result"] == "PASS":
            checks[cid]["result"] = "NOT_RUN"


def _read_tsv(path: Path, required: Iterable[str]) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise AuditInputError(f"unreadable or invalid TSV {path}: {exc}") from exc
    fields = set(rows[0].keys()) if rows else set()
    missing = set(required) - fields
    if missing:
        raise AuditInputError(f"TSV {path} missing columns: {sorted(missing)}")
    return rows


def _hex64(value: str | None) -> bool:
    return bool(value and re.fullmatch(r"[0-9a-fA-F]{64}", value))


def _norm_paths(values: Iterable[Path | str]) -> list[Path]:
    out: list[Path] = []
    for value in values:
        try:
            out.append(Path(value).expanduser().resolve())
        except OSError:
            continue
    return out


def _manifest_entities(manifest: dict[str, Any]) -> dict[str, str]:
    entities = dict(DEFAULT_ROLE_PATHS)
    raw = manifest.get("entities", {})
    if isinstance(raw, dict):
        for role, value in raw.items():
            if isinstance(value, str) and value.strip():
                entities[role] = value
    return entities


def _operator_identity(config: AuditConfig, root: Path) -> tuple[str | None, str | None, str | None]:
    assets_pin = config.catalog_pin_assets_sha256
    sources_pin = config.catalog_pin_sources_sha256
    source: str | None = None
    if assets_pin or sources_pin:
        if not (_hex64(assets_pin) and _hex64(sources_pin)):
            raise AuditInputError("operator catalog pins must be a complete pair of hex64 SHA-256 values")
        source = "cli"
    if config.catalog_manifest:
        mp = config.catalog_manifest.expanduser().resolve()
        if _is_relative_to(mp, root):
            raise AuditInputError("operator catalog manifest cannot be pack-local")
        obj = _json(mp)
        ma = obj.get("assets_sha256")
        ms = obj.get("sources_sha256")
        if not (_hex64(ma) and _hex64(ms)):
            raise AuditInputError("operator catalog manifest missing complete hex64 pins")
        if assets_pin and (assets_pin.lower() != ma.lower() or sources_pin.lower() != ms.lower()):
            raise AuditInputError("CLI and operator manifest catalog identity pins disagree")
        assets_pin, sources_pin, source = ma, ms, "operator_manifest"
    return assets_pin.lower() if assets_pin else None, sources_pin.lower() if sources_pin else None, source


def _catalog_paths(vault_root: Path) -> tuple[Path, Path]:
    return vault_root / CATALOG_DIR / ASSETS_NAME, vault_root / CATALOG_DIR / SOURCES_NAME


def _bind_catalog(
    config: AuditConfig,
    root: Path,
    manifest: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, str]], list[dict[str, str]]]:
    op_assets, op_sources, op_source = _operator_identity(config, root)
    allowlist = list(config.vault_root_allowlist)
    env_allow = os.environ.get("FALSIFY_VAULT_ROOT_ALLOWLIST", "")
    if env_allow:
        allowlist.extend(Path(x) for x in env_allow.split(os.pathsep) if x.strip())
    allowed = _norm_paths(allowlist)
    pack_assets = manifest.get("catalog_assets_sha256")
    pack_sources = manifest.get("catalog_sources_sha256")
    pack_pin_present = bool(pack_assets or pack_sources)
    if pack_pin_present and not (_hex64(pack_assets) and _hex64(pack_sources)):
        raise AuditInputError("pack catalog pin must be a complete assets/sources hex64 pair")

    candidates: list[Path] = []
    explicit = config.vault_root.expanduser().resolve() if config.vault_root else None
    if explicit:
        candidates = [explicit]
    else:
        seen: set[Path] = set()
        for start in (root, Path.cwd().resolve()):
            for candidate in (start, *start.parents):
                if candidate not in seen:
                    candidates.append(candidate)
                    seen.add(candidate)

    fake_parent_seen = False
    chosen: tuple[Path, Path, Path, str, str, str] | None = None
    for candidate in candidates:
        assets_path, sources_path = _catalog_paths(candidate)
        if not (assets_path.is_file() and sources_path.is_file()):
            continue
        if ((candidate / CATALOG_DIR).is_symlink() or assets_path.is_symlink()
                or sources_path.is_symlink()):
            fake_parent_seen = True
            continue
        ah, sh = _sha256(assets_path), _sha256(sources_path)
        is_allowed = candidate in allowed
        pins_match = bool(op_assets and op_sources and ah == op_assets and sh == op_sources)
        if is_allowed:
            chosen = (candidate, assets_path, sources_path, ah, sh, "allowlist")
            break
        if pins_match:
            chosen = (candidate, assets_path, sources_path, ah, sh, op_source or "cli")
            break
        fake_parent_seen = True
        if explicit:
            break

    if chosen is None:
        detail = "forged/free vault-root failed vault identity bind"
        if fake_parent_seen and not explicit:
            detail = "discovery found fake parent catalog without non-pack identity bind"
        if pack_pin_present and not (op_assets and op_sources) and not any(c in allowed for c in candidates):
            detail += "; pack-only catalog pin is insufficient without operator/vault-freeze pin or allowlist"
        raise AuditInputError(detail)

    vault_root, assets_path, sources_path, ah, sh, identity_source = chosen
    if op_assets and (ah != op_assets or sh != op_sources):
        raise AuditInputError("catalog live SHA-256 mismatch against non-pack operator identity pins")
    if pack_pin_present and (ah != str(pack_assets).lower() or sh != str(pack_sources).lower()):
        raise AuditInputError("catalog SHA-256 pin mismatch: pack pin diverges from canonical loaded files")
    data_truth_sha = None
    if config.data_truth:
        expected_truth = (vault_root / "当前真相" / "数据资产目录 当前真相.md").resolve(strict=False)
        supplied_truth = config.data_truth.expanduser().resolve(strict=False)
        if supplied_truth != expected_truth or not expected_truth.is_file() or expected_truth.is_symlink():
            raise AuditInputError("data-truth pointer must equal canonical 当前真相/数据资产目录 当前真相.md under bound vault")
        data_truth_sha = _sha256(expected_truth)
    refs = {
        "vault_root": str(vault_root),
        "assets_tsv": f"{CATALOG_DIR}/{ASSETS_NAME}",
        "sources_tsv": f"{CATALOG_DIR}/{SOURCES_NAME}",
        "assets_tsv_sha256": ah,
        "sources_tsv_sha256": sh,
        "identity_pin_source": identity_source,
        "pack_pin_present": pack_pin_present,
        "pin_source": "identity+pack" if pack_pin_present else "identity_only",
        "pin_match": True,
        "vault_identity_bound": True,
        "acceptance_eligible": config.profile in ACCEPTANCE_PROFILES,
        "data_truth_sha256": data_truth_sha,
    }
    assets = _read_tsv(assets_path, ("asset_id", "status", "class", "venue", "data_types", "symbols", "coverage", "physical_path", "source"))
    sources = _read_tsv(sources_path, ("source_id", "platform", "local_state"))
    return refs, assets, sources


def _as_list(value: Any, key: str | None = None) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict) and key and isinstance(value.get(key), list):
        return value[key]
    if isinstance(value, dict):
        return [value]
    return []


def _date(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def _coverage_bounds(row: dict[str, Any]) -> tuple[datetime | None, datetime | None]:
    start = _date(row.get("coverage_start"))
    end = _date(row.get("coverage_end"))
    if start and end:
        return start, end
    dates = re.findall(r"20\d\d-\d\d-\d\d(?:T\d\d:\d\d(?::\d\d)?Z?)?", str(row.get("coverage", "")))
    parsed = [d for d in (_date(x) for x in dates) if d]
    return (min(parsed), max(parsed)) if len(parsed) >= 2 else (None, None)


def _csv_header(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return next(csv.reader(f))
    except (OSError, UnicodeError, csv.Error, StopIteration) as exc:
        raise AuditInputError(f"cannot read data panel header {path}: {exc}") from exc


def _resolve_physical(root: Path, value: str) -> Path | None:
    if value.startswith("PACK_LOCAL:"):
        return _inside(root, value.split(":", 1)[1].lstrip("/\\"))
    path = Path(value)
    if not path.is_absolute():
        return _inside(root, value)
    try:
        return path.resolve()
    except OSError:
        return None


def _contains_any(text: str, words: Iterable[str]) -> bool:
    low = text.lower()
    return any(word.lower() in low for word in words)


def _authority_token_hits(obj: Any, prefix: str = "") -> list[str]:
    """Find forbidden exact tokens only in authority-bearing JSON fields."""
    hits: list[str] = []
    authority_keys = {"verdict", "authority_verdict", "cli_verdict", "authority_token", "gate_verdict"}
    if isinstance(obj, dict):
        for key, value in obj.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            if str(key).lower() in authority_keys and isinstance(value, str) and value.upper() in FORBIDDEN_VERDICTS:
                hits.append(f"{child}={value}")
            hits.extend(_authority_token_hits(value, child))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            hits.extend(_authority_token_hits(value, f"{prefix}[{i}]"))
    return hits


def _load_entities(root: Path, manifest: dict[str, Any]) -> tuple[dict[str, Path], dict[str, Any]]:
    role_paths: dict[str, Path] = {}
    objects: dict[str, Any] = {"manifest": manifest}
    for role, rel in _manifest_entities(manifest).items():
        path = _inside(root, rel)
        role_paths[role] = path
        if role in REQUIRED_ROLES and not path.is_file():
            raise AuditInputError(f"required entity missing: {role} at {rel}")
        if path.is_file() and path.suffix.lower() == ".json" and role != "manifest":
            objects[role] = _json(path)
    return role_paths, objects


def _d0(root: Path, role_paths: dict[str, Path], objects: dict[str, Any], hashes: dict[str, str], checks: dict[str, dict[str, Any]]) -> str:
    manifest = objects.get("manifest", {})
    attack_catalog = objects.get("attack_catalog")
    if not isinstance(attack_catalog, dict) or attack_catalog.get("catalog_id") != EXPECTED_ATTACK_CATALOG_ID:
        _fail(checks, "D0", "pack attack_catalog does not bind frozen rem3 catalog_id")
    if manifest.get("attack_catalog_id") != EXPECTED_ATTACK_CATALOG_ID:
        _fail(checks, "D0", "PACK_MANIFEST attack_catalog_id missing or not frozen rem3 id")
    inventory = objects.get("inventory")
    if not isinstance(inventory, dict):
        _fail(checks, "D0", "INVENTORY.json must be an object")
        return ""
    entries = _as_list(inventory, "files")
    declared: set[str] = set()
    inv_digest = hashlib.sha256()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not _hex64(entry.get("sha256")):
            _fail(checks, "D0", "inventory entry requires path + hex64 sha256")
            continue
        rel = entry["path"].replace("\\", "/")
        declared.add(rel)
        actual = hashes.get(rel)
        if actual != entry["sha256"].lower():
            _fail(checks, "D0", f"inventory drift sha256 mismatch for {rel}: declared={entry['sha256']} actual={actual}")
        inv_digest.update(rel.encode("utf-8") + b"\0" + entry["sha256"].lower().encode("ascii") + b"\n")
    inventory_rel = role_paths["inventory"].relative_to(root).as_posix()
    live = set(hashes) - {inventory_rel}
    missing_inventory = sorted(live - declared)
    extra_inventory = sorted(declared - live)
    if missing_inventory:
        _fail(checks, "D0", f"inventory omits live files: {missing_inventory}")
    if extra_inventory:
        _fail(checks, "D0", f"inventory declares missing files: {extra_inventory}")
    computed = inv_digest.hexdigest()
    stored = inventory.get("inventory_sha256")
    if stored and stored != computed:
        _fail(checks, "D0", f"inventory aggregate sha256 drift: stored={stored} actual={computed}")
    return computed


def _audit_checks(
    config: AuditConfig,
    root: Path,
    manifest: dict[str, Any],
    role_paths: dict[str, Path],
    objects: dict[str, Any],
    assets_rows: list[dict[str, str]],
    sources_rows: list[dict[str, str]],
    hashes: dict[str, str],
    checks: dict[str, dict[str, Any]],
    inventory_sha: str,
) -> None:
    bindings = _as_list(objects.get("data_bindings", {}), "bindings")
    claim = objects.get("claim", {})
    universe_obj = objects.get("universe", {})
    provenance_obj = objects.get("provenance", {})
    assets_by_id = {r.get("asset_id", ""): r for r in assets_rows}
    sources_by_id = {r.get("source_id", ""): r for r in sources_rows}
    claim_asset_ids = set(claim.get("asset_ids", [])) if isinstance(claim.get("asset_ids"), list) else set()
    binding_asset_ids = {b.get("asset_id") for b in bindings if isinstance(b, dict)}
    all_asset_ids = {x for x in claim_asset_ids | binding_asset_ids if isinstance(x, str) and x}
    if not all_asset_ids:
        _fail(checks, "D1", "no asset_id declared in DATA_BINDINGS/CLAIM")
    if claim_asset_ids != binding_asset_ids:
        _fail(checks, "D1", f"asset_id mismatch between claim and bindings: claim={sorted(claim_asset_ids)} bindings={sorted(binding_asset_ids)}")
    if (root / ASSETS_NAME).exists() or (root / SOURCES_NAME).exists():
        _fail(checks, "D1", "pack-local catalog assets.tsv/sources.tsv is advisory only and cannot establish authority")

    continuous = bool(claim.get("continuous_history"))
    derived_only = bool(claim.get("derived_only"))
    claim_start = _date(claim.get("window_start"))
    claim_end = _date(claim.get("window_end"))
    claim_venue = str(claim.get("venue", ""))
    claim_class = str(claim.get("class", ""))
    claim_types = {str(x) for x in claim.get("data_types", [])} if isinstance(claim.get("data_types"), list) else set()
    panel_headers: set[str] = set()

    for binding in bindings:
        if not isinstance(binding, dict):
            _fail(checks, "D1", "binding must be an object")
            continue
        aid = str(binding.get("asset_id", ""))
        row = assets_by_id.get(aid)
        if not row:
            _fail(checks, "D1", f"UNREGISTERED_UNKNOWN asset_id={aid}: absent from canonical assets.tsv")
            continue
        status = row.get("status", "")
        if status in {"UNREGISTERED_UNKNOWN", "LOCATOR_ONLY_NO_DATA", "DELETED_SUPERSEDED", "SOURCE_AVAILABLE_NOT_DOWNLOADED"}:
            _fail(checks, "D1", f"asset_id={aid} status={status} cannot support HAVE/raw backtest claim")
        if status in {"DERIVED_CACHE", "DERIVED_ARTIFACTS"} and not derived_only:
            _fail(checks, "D1", f"asset_id={aid} DERIVED status sold as raw HAVE authority")
        if status == "HAVE_VERIFIED_SPARSE" and continuous:
            _fail(checks, "D1", f"asset_id={aid} SPARSE sample cannot support continuous full-window claim")
        if status.startswith("HAVE_PARTIAL") or status == "FORWARD_ACTIVE_PARTIAL":
            if continuous and not binding.get("gap_ledger"):
                _fail(checks, "D3", f"asset_id={aid} partial status cannot support continuous claim without gap ledger")

        binding_venue = str(binding.get("venue", ""))
        catalog_venue = str(row.get("venue", ""))
        if claim_venue and catalog_venue and claim_venue.lower() != catalog_venue.lower():
            _fail(checks, "D2", f"venue mismatch/proxy: claim={claim_venue} catalog={catalog_venue} asset_id={aid}")
        if binding_venue and catalog_venue and binding_venue.lower() != catalog_venue.lower():
            _fail(checks, "D2", f"venue mismatch/proxy: binding={binding_venue} catalog={catalog_venue} asset_id={aid}")
        if claim_class and row.get("class") and claim_class.lower() != row["class"].lower():
            _fail(checks, "D2", f"class mismatch: claim={claim_class} catalog={row['class']}")
        catalog_types = {x.strip() for x in row.get("data_types", "").split(",") if x.strip()}
        if claim_types and not claim_types.issubset(catalog_types):
            _fail(checks, "D2", f"data_types mismatch: claim={sorted(claim_types)} catalog={sorted(catalog_types)}")

        physical = str(binding.get("physical_path", ""))
        catalog_physical = str(row.get("physical_path", ""))
        if not physical:
            _fail(checks, "D2", f"asset_id={aid} binding physical_path missing")
            continue
        if catalog_physical and physical != catalog_physical:
            _fail(checks, "D2", f"physical path mismatch between DATA_BINDINGS and canonical assets.tsv for {aid}")
        resolved = _resolve_physical(root, physical)
        if resolved and (physical.startswith("PACK_LOCAL:") or not Path(physical).is_absolute()):
            if not resolved.is_file():
                _fail(checks, "D2", f"physical data file missing: {physical}")
            else:
                data_pin = binding.get("data_sha256")
                if not _hex64(data_pin) or _sha256(resolved) != str(data_pin).lower():
                    _fail(checks, "D2", f"physical data sha256/manifest pin mismatch: {physical}")
                if resolved.suffix.lower() == ".csv":
                    panel_headers.update(_csv_header(resolved))
        elif not binding.get("data_manifest_sha256"):
            _fail(checks, "D2", f"remote/non-local physical path lacks data_manifest_sha256: {physical}")

        bstart = _date(binding.get("coverage_start"))
        bend = _date(binding.get("coverage_end"))
        cstart, cend = _coverage_bounds(row)
        if not (claim_start and claim_end and bstart and bend):
            _fail(checks, "D3", f"coverage bounds missing or invalid for asset_id={aid}")
        else:
            if claim_start < bstart or claim_end > bend:
                _fail(checks, "D3", f"claimed coverage outside binding window for {aid}")
            if cstart and cend and (claim_start < cstart or claim_end > cend):
                _fail(checks, "D3", f"claimed coverage outside canonical registered window for {aid}")
        if bool(binding.get("freeze_qa_only")) and continuous:
            _fail(checks, "D3", "freeze QA slice promoted to full HAVE_VERIFIED_COMPLETE archive claim")

    symbols = claim.get("symbols", []) if isinstance(claim.get("symbols"), list) else []
    universe = _as_list(universe_obj, "symbols")
    universe_symbols = {str(x.get("symbol")) for x in universe if isinstance(x, dict)}
    for symbol in symbols:
        if symbol not in universe_symbols:
            _fail(checks, "D4", f"traded symbol {symbol} missing from universe")
        if panel_headers and symbol not in panel_headers:
            _fail(checks, "D4", f"universe symbol {symbol} absent from data panel columns")
    for item in universe:
        if not isinstance(item, dict):
            continue
        listing = _date(item.get("listing_date"))
        delist = _date(item.get("delist_date"))
        if claim_start and listing and claim_start < listing and not universe_obj.get("pit_membership"):
            _fail(checks, "D4", f"survivorship/PIT universe failure: claim begins before listing for {item.get('symbol')}")
        if claim_end and delist and claim_end > delist and not universe_obj.get("pit_membership"):
            _fail(checks, "D4", f"survivorship/PIT universe failure: claim continues after delist for {item.get('symbol')}")
        if item.get("venue") and claim_venue and str(item["venue"]).lower() != claim_venue.lower():
            _fail(checks, "D4", f"cross-venue symbol collision/mismatch for {item.get('symbol')}")

    calendar = objects.get("calendar", {})
    bar = objects.get("bar_index", {})
    if str(bar.get("timezone", "")).upper() != "UTC":
        _fail(checks, "D5", f"timezone mismatch/undeclared conversion: {bar.get('timezone')}")
    if bar.get("label") not in {"open", "close"}:
        _fail(checks, "D5", "bar label semantics must declare open or close")
    if str(calendar.get("timezone", "")).upper() != "UTC" or calendar.get("session") != "24/7":
        _fail(checks, "D5", "crypto session calendar must explicitly declare UTC 24/7")
    if int(bar.get("alignment_shift_bars", 0) or 0) != 0:
        _fail(checks, "D5", "bar +1 shift / timezone alignment creates look-ahead")

    gap = objects.get("gap_report", {})
    if continuous and not isinstance(gap, dict):
        _fail(checks, "D6", "continuous claim requires GAP_REPORT")
    if continuous:
        missing = int(gap.get("missing_bars", 0) or 0)
        policy = str(claim.get("missing_policy", gap.get("policy", ""))).lower()
        max_hole = int(gap.get("max_hole_bars", 0) or 0)
        max_ffill = int(claim.get("max_ffill_bars", 0) or 0)
        if missing and (policy == "dropna" or not claim.get("gap_ledger")):
            _fail(checks, "D6", f"gap/missing continuous series uses silent dropna or lacks gap ledger: missing={missing}")
        if policy in {"ffill", "forward-fill", "forward_fill"} and max_hole > max_ffill:
            _fail(checks, "D6", f"ffill/forward-fill across hole exceeds max_ffill; synthetic marker required")

    if str(bar.get("join_direction", "")).lower() == "forward":
        _fail(checks, "D7", "look-ahead future join: merge_asof direction=forward")
    if bar.get("feature_timestamp_relation") not in {"lte_decision", "<="}:
        _fail(checks, "D7", "feature timestamp must be <= decision timestamp")
    if bar.get("signal_return_alignment") in {"same_bar_close_to_open", "close_to_same_open"}:
        _fail(checks, "D7", "same-bar close-to-open leakage/look-ahead")

    metrics = objects.get("metrics", {})
    net_claim = bool(claim.get("net_metrics")) or any(str(k).lower().startswith("net_") for k in metrics)
    if net_claim:
        fee = objects.get("fee_model")
        slip = objects.get("slippage_model")
        if not isinstance(fee, dict):
            _fail(checks, "D8", "net claim missing fee_model; gross cannot be labeled net")
        else:
            rate = float(fee.get("fee_rate", 0) or 0)
            if rate == 0 and not fee.get("venue_fee_free"):
                _fail(checks, "D8", "fee=0 theater on net claim without venue fee-free declaration")
        if not isinstance(slip, dict) and not claim.get("slippage_zero_justification"):
            _fail(checks, "D8", "net claim missing slippage model/zero justification")
        if metrics.get("net_pnl") == metrics.get("gross_pnl") and not claim.get("costs_can_be_zero"):
            _fail(checks, "D8", "gross labeled as net: net_pnl identical to gross_pnl")
    elif not claim.get("gross_only"):
        _fail(checks, "D8", "gross-only claim must explicitly set gross_only=true")

    claim_text = json.dumps(claim, ensure_ascii=False).lower()
    pit_claim = bool(claim.get("point_in_time") or claim.get("non_restated") or _contains_any(claim_text, ("point-in-time", "no lookahead data")))
    pit = objects.get("pit_markers")
    if pit_claim:
        if not isinstance(pit, dict):
            _fail(checks, "D9", "point-in-time/non-restated claim missing PIT markers")
        elif not (pit.get("asof_column") or pit.get("revision_id_column")):
            _fail(checks, "D9", "restated source sold as point-in-time without asof/revision marker")
        elif panel_headers and not ({str(pit.get("asof_column")), str(pit.get("revision_id_column"))} & panel_headers):
            _fail(checks, "D9", "PIT asof/revision marker declared but absent from panel schema")

    chains = _as_list(provenance_obj, "chains")
    chain_by_asset = {str(x.get("asset_id")): x for x in chains if isinstance(x, dict)}
    for binding in bindings:
        if not isinstance(binding, dict):
            continue
        aid = str(binding.get("asset_id", ""))
        source_id = str(binding.get("source_id", ""))
        if source_id not in sources_by_id:
            _fail(checks, "D10", f"broken provenance chain: source_id={source_id} absent from canonical sources.tsv")
        chain = chain_by_asset.get(aid)
        if not chain:
            _fail(checks, "D10", f"broken provenance chain: no chain for asset_id={aid}")
            continue
        for key in ("source_id", "archive_physical_path", "binding_data_sha256", "coverage_start", "coverage_end"):
            if not chain.get(key):
                _fail(checks, "D10", f"broken provenance chain missing {key} for asset_id={aid}")
        if chain.get("source_id") != source_id or chain.get("archive_physical_path") != binding.get("physical_path") or chain.get("binding_data_sha256") != binding.get("data_sha256"):
            _fail(checks, "D10", f"provenance source/archive/pack pin chain mismatch for asset_id={aid}")

    trial_files = sorted(root.glob("trials/*.json"))
    trial_ledger = objects.get("trial_ledger")
    language = str(claim.get("claim_language", "")).lower()
    multiplicity = _contains_any(language, ("robust", "significant", "multiplicity", "multiple-testing")) or bool(claim.get("n_trials"))
    if multiplicity:
        if not isinstance(trial_ledger, dict):
            _fail(checks, "D11", "multiple-testing/significance claim missing trial ledger")
        declared = int(claim.get("n_trials", 0) or 0)
        ledger_n = int(trial_ledger.get("n_trials", 0) or 0) if isinstance(trial_ledger, dict) else 0
        observed = len(trial_files)
        if declared < observed or ledger_n < observed or declared != ledger_n:
            _fail(checks, "D11", f"n_trials undercount/mismatch: claim={declared} ledger={ledger_n} observed={observed}")
        if "multiplicity-adjusted" in language and declared <= 1:
            checks["D11"]["severity"] = "CRITICAL"
            _fail(checks, "D11", "multiplicity-adjusted PASS with n_trials<=1")

    authority_objects: list[tuple[str, Any]] = [("CLAIM.json", claim), ("METRICS.json", metrics)]
    for pattern in ("*RESULT*.json", "*REPORT*.json", "*RECEIPT*.json"):
        for path in root.rglob(pattern):
            if path.is_file() and path not in {role_paths.get("claim"), role_paths.get("metrics")}:
                authority_objects.append((path.relative_to(root).as_posix(), _json(path)))
    for source_name, obj in authority_objects:
        for hit in _authority_token_hits(obj):
            _fail(checks, "D12", f"authority ceiling forbidden verdict token in {source_name}: {hit}")
    evidence = claim.get("acceptance_evidence", [])
    if isinstance(evidence, list) and evidence and all("SELFTEST" in str(x).upper() for x in evidence):
        _fail(checks, "D12", "AUTHOR SELFTEST used as sole independent acceptance authority")
    receipt_rel = manifest.get("stored_receipt")
    if receipt_rel:
        receipt_path = _inside(root, str(receipt_rel))
        receipt = _json(receipt_path) if receipt_path.is_file() else {}
        if receipt.get("inventory_sha256") != inventory_sha:
            _fail(checks, "D12", "inventory/snapshot drift after stored author PASS receipt")


def _fixture_root() -> Path:
    return Path(__file__).with_name("audit_backtest_fixtures")


def _run_attack_suite(profile: str) -> dict[str, Any]:
    base = _fixture_root()
    catalog_path = base / "ATTACK_CATALOG.json"
    if not catalog_path.is_file():
        raise AuditInputError(f"materialized attack suite missing: {catalog_path}")
    catalog = _json(catalog_path)
    cases = list(catalog.get("attack_fixtures", [])) + list(catalog.get("valid_fixtures", []))
    if not catalog.get("attack_fixtures") or not catalog.get("valid_fixtures"):
        raise AuditInputError("attack suite invalid: zero attacks or missing valid fixture")
    results: dict[str, Any] = {}
    for entry in cases:
        fid = entry["id"]
        case_dir = base / fid
        case = _json(case_dir / "FIXTURE_CASE.json")
        pack_root = (case_dir / case.get("pack_root", ".")).resolve()
        vault_root = (case_dir / case["vault_root"]).resolve() if case.get("vault_root") else base.resolve()
        allowlist = [vault_root] if case.get("allowlist", True) else []
        pins_mode = case.get("operator_pins", "live")
        ap = sp = None
        if pins_mode == "live":
            apath, spath = _catalog_paths(vault_root)
            if apath.is_file() and spath.is_file():
                ap, sp = _sha256(apath), _sha256(spath)
        elif pins_mode == "wrong":
            ap, sp = "0" * 64, "1" * 64
        case_profile = case.get("profile", profile if profile in ACCEPTANCE_PROFILES else "strict")
        preflight_errors = list(case.get("preflight_errors", []))
        if case.get("forbidden_output_path"):
            try:
                _safe_output(pack_root / case["forbidden_output_path"], pack_root, vault_root)
            except AuditInputError as exc:
                preflight_errors.append(str(exc))
        cfg = AuditConfig(
            root=pack_root,
            profile=case_profile,
            strict=case_profile == "strict",
            vault_root=vault_root if case.get("explicit_vault_root", True) else None,
            catalog_pin_assets_sha256=ap,
            catalog_pin_sources_sha256=sp,
            vault_root_allowlist=allowlist,
            run_attack_suite=False,
            preflight_errors=preflight_errors,
        )
        report, code = audit_backtest(cfg)
        actual = "ACCEPT" if code == 0 and report.get("verdict") == PASS else "REJECT"
        expected = entry.get("expected")
        errors_text = " ".join(report.get("errors", []) + [e for c in report.get("checks", []) for e in c.get("errors", [])])
        terms = entry.get("must_surface_errors_matching", [])
        term_match = True if not terms else any(str(term).lower() in errors_text.lower() for term in terms)
        results[fid] = {
            "expected": expected,
            "actual": actual,
            "pass": actual == expected and term_match,
            "exit_code": code,
            "error_term_match": term_match,
        }
    return {
        "catalog_id": catalog.get("catalog_id"),
        "attack_count": len(catalog.get("attack_fixtures", [])),
        "valid_count": len(catalog.get("valid_fixtures", [])),
        "cases": results,
        "pass": all(x["pass"] for x in results.values()),
    }


def audit_backtest(config: AuditConfig) -> tuple[dict[str, Any], int]:
    checks = _check_records()
    profile = config.profile
    report: dict[str, Any] = {
        "schema_version": "falsify.audit_backtest.v1",
        "command": "falsify audit-backtest",
        "profile": profile,
        "strict": bool(config.strict or profile == "strict"),
        "generated_at_utc": _utc_now(),
        "root": str(config.root.expanduser().resolve(strict=False)),
        "input_snapshot_sha256": None,
        "pack_id": None,
        "verdict": BLOCK,
        "exit_code": 2,
        "authority": False,
        "data_authority_first": True,
        "acceptance_eligible": profile in ACCEPTANCE_PROFILES,
        "non_claims": list(NON_CLAIMS),
        "catalog_refs": {
            "vault_root": None, "assets_tsv": f"{CATALOG_DIR}/{ASSETS_NAME}",
            "sources_tsv": f"{CATALOG_DIR}/{SOURCES_NAME}",
            "assets_tsv_sha256": None, "sources_tsv_sha256": None,
            "identity_pin_source": None, "pack_pin_present": False,
            "pin_source": None, "pin_match": False, "vault_identity_bound": False,
            "acceptance_eligible": profile in ACCEPTANCE_PROFILES,
        },
        "checks": list(checks.values()),
        "attacks": {"pass": False, "cases": {}},
        "recomputed_hashes": {},
        "errors": [],
    }
    try:
        if profile not in ALL_PROFILES:
            raise AuditInputError(f"unknown profile {profile}; only {sorted(ALL_PROFILES)}")
        raw_root = config.root.expanduser()
        if raw_root.is_symlink():
            raise AuditInputError(f"pack root symlink forbidden: {raw_root}")
        root = raw_root.resolve()
        if not root.is_dir():
            raise AuditInputError(f"pack root missing/not directory/symlink: {root}")
        if config.preflight_errors:
            for error in config.preflight_errors:
                _fail(checks, "D1", error)
        snapshot, hashes = _tree_snapshot(root)
        report["input_snapshot_sha256"] = snapshot
        report["recomputed_hashes"] = hashes
        manifest_path = _inside(root, DEFAULT_ROLE_PATHS["manifest"])
        if not manifest_path.is_file():
            raise AuditInputError("required entity missing: PACK_MANIFEST.json")
        manifest = _json(manifest_path)
        if not isinstance(manifest, dict):
            raise AuditInputError("PACK_MANIFEST.json must be an object")
        report["pack_id"] = manifest.get("pack_id")
        if config.expect_pack_id and manifest.get("pack_id") != config.expect_pack_id:
            _fail(checks, "D0", f"pack_id mismatch expected={config.expect_pack_id} actual={manifest.get('pack_id')}")
        role_paths, objects = _load_entities(root, manifest)
        inventory_sha = _d0(root, role_paths, objects, hashes, checks)
        refs, assets, sources = _bind_catalog(config, root, manifest)
        report["catalog_refs"] = refs
        _audit_checks(config, root, manifest, role_paths, objects, assets, sources, hashes, checks, inventory_sha)
        if config.run_attack_suite:
            report["attacks"] = _run_attack_suite(profile)
        else:
            report["attacks"] = {"pass": True, "skipped_internal": True, "cases": {}}
        if not report["attacks"].get("pass"):
            _fail(checks, "D12", "full materialized attack suite did not reject all attacks and accept valid fixture")
    except AuditInputError as exc:
        report["errors"].append(str(exc))
        _block_all(checks, str(exc))
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        message = f"internal fail-closed input error: {type(exc).__name__}: {exc}"
        report["errors"].append(message)
        _block_all(checks, message)

    hard_block = any(c["result"] == "BLOCK" for c in checks.values())
    failed = any(c["result"] == "FAIL" for c in checks.values())
    if hard_block:
        verdict, code = BLOCK, 2
    elif failed:
        verdict, code = FAIL, 1
    elif profile in NON_ACCEPTANCE_PROFILES:
        verdict, code = DIAG, 1
        report["acceptance_eligible"] = False
        report["catalog_refs"]["acceptance_eligible"] = False
    else:
        verdict, code = PASS, 0
    report["verdict"] = verdict
    report["exit_code"] = code
    return report, code


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Falsify audit-backtest report", "",
        f"- Verdict: `{report['verdict']}`", f"- Exit code: `{report['exit_code']}`",
        "- Authority: `false`", f"- Profile: `{report['profile']}`",
        f"- Acceptance eligible: `{str(report['acceptance_eligible']).lower()}`", "",
        "## Input snapshot", "", f"`{report.get('input_snapshot_sha256')}`", "",
        "## Data checks first", "", "| Check | Result | Severity | Errors |", "|---|---|---|---|",
    ]
    for check in report.get("checks", []):
        errors = "<br>".join(str(x).replace("|", "\\|") for x in check.get("errors", []))
        lines.append(f"| {check['id']} {check['name']} | {check['result']} | {check['severity']} | {errors} |")
    lines += ["", "## Attack suite", ""]
    attacks = report.get("attacks", {})
    lines.append(f"Suite pass: `{str(attacks.get('pass', False)).lower()}`")
    lines += ["", "| Fixture | Expected | Actual | Pass |", "|---|---|---|---|"]
    for fid, item in sorted(attacks.get("cases", {}).items()):
        lines.append(f"| {fid} | {item.get('expected')} | {item.get('actual')} | {item.get('pass')} |")
    lines += ["", "## Explicit non-claims", ""]
    lines.extend(f"- `{x}`" for x in report.get("non_claims", []))
    lines += ["", "## Next authority", "", "Independent Falsify Audit/chief auditor still owns novel attacks, identity, and every claim-bearing upgrade.", ""]
    return "\n".join(lines)


def _safe_output(
    path: Path | None,
    root: Path,
    vault_root: Path | None,
    protected_inputs: Iterable[Path] = (),
) -> Path | None:
    if path is None:
        return None
    expanded = path.expanduser()
    raw_absolute = Path(os.path.abspath(str(expanded)))
    resolved = expanded.resolve(strict=False)
    resolved_root = root.resolve(strict=False)
    if _is_relative_to(raw_absolute, resolved_root) or _is_relative_to(resolved, resolved_root):
        raise AuditInputError(f"output path must not mutate pack root: {resolved}")
    if vault_root:
        catalog_dir = (vault_root.resolve(strict=False) / CATALOG_DIR)
        if _is_relative_to(raw_absolute, catalog_dir) or _is_relative_to(resolved, catalog_dir):
            raise AuditInputError(f"output path must not mutate vault catalog: {resolved}")
    for protected in protected_inputs:
        protected_resolved = protected.expanduser().resolve(strict=False)
        if resolved == protected_resolved:
            raise AuditInputError(f"output path must not overwrite verifier input: {resolved}")
    return resolved


def run_cli(args: Any) -> int:
    profile = args.profile or ("strict" if args.strict else "strict")
    config = AuditConfig(
        root=Path(args.root), profile=profile, strict=bool(args.strict or profile == "strict"),
        vault_root=Path(args.vault_root) if args.vault_root else None,
        catalog_pin_assets_sha256=args.catalog_pin_assets_sha256,
        catalog_pin_sources_sha256=args.catalog_pin_sources_sha256,
        catalog_manifest=Path(args.catalog_manifest) if args.catalog_manifest else None,
        data_truth=Path(args.data_truth) if args.data_truth else None,
        vault_root_allowlist=[Path(x) for x in (args.vault_root_allowlist or [])],
        expect_pack_id=args.expect_pack_id,
        out_json=Path(args.out_json) if args.out_json else None,
        out_md=Path(args.out_md) if args.out_md else None,
        # There is intentionally no CLI/env bypass: acceptance profiles must
        # execute the complete materialized attack suite on every invocation.
        run_attack_suite=True,
    )
    root = config.root.expanduser().resolve(strict=False)
    report, code = audit_backtest(config)
    bound_vault_text = report.get("catalog_refs", {}).get("vault_root")
    bound_vault = Path(bound_vault_text) if bound_vault_text else config.vault_root
    try:
        protected_inputs = [p for p in (config.catalog_manifest, config.data_truth) if p is not None]
        out_json = _safe_output(config.out_json, root, bound_vault, protected_inputs)
        out_md = _safe_output(config.out_md, root, bound_vault, protected_inputs)
        if out_json and out_md and out_json == out_md:
            raise AuditInputError("out-json and out-md must not resolve to the same file")
    except AuditInputError as exc:
        report["verdict"], report["exit_code"] = BLOCK, 2
        report["errors"].append(str(exc))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    markdown = render_markdown(report)
    try:
        if out_json:
            out_json.parent.mkdir(parents=True, exist_ok=True)
            out_json.write_text(payload, encoding="utf-8")
        if out_md:
            out_md.parent.mkdir(parents=True, exist_ok=True)
            out_md.write_text(markdown, encoding="utf-8")
    except OSError as exc:
        report["verdict"], report["exit_code"] = BLOCK, 2
        report["errors"].append(f"cannot write explicit output: {exc}")
        payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        code = 2
    print(payload, end="")
    return code


def add_parser(subparsers: Any) -> None:
    parser = subparsers.add_parser(
        "audit-backtest",
        help="pure-read frozen backtest data/claim verifier (not strategy/live authority)",
    )
    parser.add_argument("--root", required=True, help="frozen backtest pack root")
    parser.add_argument("--strict", action="store_true", help="strict acceptance profile")
    parser.add_argument("--profile", choices=sorted(ALL_PROFILES))
    parser.add_argument("--vault-root", help="candidate canonical vault root; identity bind still required")
    parser.add_argument("--vault-root-allowlist", action="append", default=[], help="operator-approved absolute vault root (repeatable)")
    parser.add_argument("--catalog-pin-assets-sha256")
    parser.add_argument("--catalog-pin-sources-sha256")
    parser.add_argument("--catalog-manifest", help="non-pack operator pin manifest")
    parser.add_argument("--data-truth", help="optional human truth pointer; not TSV authority")
    parser.add_argument("--out-json")
    parser.add_argument("--out-md")
    parser.add_argument("--expect-pack-id")
    parser.set_defaults(func=lambda args: sys.exit(run_cli(args)))
