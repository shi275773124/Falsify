from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from falsify.audit_backtest import (
    ACCEPTANCE_PROFILES,
    DIAG,
    PASS,
    AuditConfig,
    _fixture_root,
    _run_attack_suite,
    audit_backtest,
)


FIXTURES = _fixture_root()
VALID = FIXTURES / "VALID_minimal_registered_pack"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def live_pins(vault: Path = FIXTURES) -> tuple[str, str]:
    return sha(vault / "数据资产目录" / "assets.tsv"), sha(vault / "数据资产目录" / "sources.tsv")


def config(root: Path, profile: str = "strict", *, suite: bool = False) -> AuditConfig:
    ap, sp = live_pins()
    return AuditConfig(
        root=root,
        profile=profile,
        strict=profile == "strict",
        vault_root=FIXTURES,
        catalog_pin_assets_sha256=ap,
        catalog_pin_sources_sha256=sp,
        run_attack_suite=suite,
    )


def refresh_inventory(root: Path) -> None:
    entries = []
    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix()):
        if path.is_file() and path.name != "INVENTORY.json":
            entries.append({"path": path.relative_to(root).as_posix(), "sha256": sha(path)})
    h = hashlib.sha256()
    for entry in entries:
        h.update(entry["path"].encode() + b"\0" + entry["sha256"].encode() + b"\n")
    (root / "INVENTORY.json").write_text(
        json.dumps({"files": entries, "inventory_sha256": h.hexdigest()}, indent=2) + "\n",
        encoding="utf-8",
    )


def tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix()):
        if path.is_file() and not path.is_symlink():
            h.update(path.relative_to(root).as_posix().encode() + b"\0" + sha(path).encode() + b"\n")
    return h.hexdigest()


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    return subprocess.run(
        [sys.executable, "-m", "falsify", "audit-backtest", *args],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )


def test_catalog_materialized_29_attacks_plus_one_valid() -> None:
    catalog = json.loads((FIXTURES / "ATTACK_CATALOG.json").read_text(encoding="utf-8"))
    assert len(catalog["attack_fixtures"]) == 29
    assert len(catalog["valid_fixtures"]) == 1
    ids = [x["id"] for x in catalog["attack_fixtures"] + catalog["valid_fixtures"]]
    assert len(set(ids)) == 30
    for fixture_id in ids:
        case = FIXTURES / fixture_id / "FIXTURE_CASE.json"
        assert case.is_file(), fixture_id
        obj = json.loads(case.read_text(encoding="utf-8"))
        pack_root = case.parent / obj.get("pack_root", ".")
        assert (pack_root / "PACK_MANIFEST.json").is_file(), fixture_id
        assert (pack_root / "INVENTORY.json").is_file(), fixture_id


@pytest.mark.parametrize("profile", sorted(ACCEPTANCE_PROFILES))
def test_acceptance_profiles_run_d0_d12_and_full_suite(profile: str) -> None:
    report, code = audit_backtest(config(VALID, profile, suite=True))
    assert code == 0
    assert report["verdict"] == PASS
    assert report["acceptance_eligible"] is True
    assert {c["id"] for c in report["checks"]} == {f"D{i}" for i in range(13)}
    assert all(c["result"] == "PASS" for c in report["checks"])
    assert report["attacks"]["pass"] is True
    assert report["attacks"]["attack_count"] == 29
    assert report["attacks"]["valid_count"] == 1


def test_all_materialized_attacks_reject_and_valid_accepts() -> None:
    result = _run_attack_suite("strict")
    assert result["pass"] is True
    assert len(result["cases"]) == 30
    assert all(item["pass"] for item in result["cases"].values())
    assert result["cases"]["VALID_minimal_registered_pack"]["actual"] == "ACCEPT"
    for fid, item in result["cases"].items():
        if fid.startswith("ATTACK_"):
            assert item["actual"] == "REJECT", fid
            assert item["exit_code"] != 0, fid


def test_cheap_valid_scope_never_passes_or_exits_zero() -> None:
    report, code = audit_backtest(config(VALID, "cheap", suite=True))
    assert code == 1
    assert report["verdict"] == DIAG
    assert report["verdict"] not in {PASS, "ENGINE_CHECK_PASS"}
    assert report["acceptance_eligible"] is False
    assert report["catalog_refs"]["acceptance_eligible"] is False


def test_environment_cannot_bypass_full_attack_suite(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FALSIFY_AUDIT_BACKTEST_SKIP_ATTACK_SUITE", "1")
    result = run_cli(
        "--root", str(VALID), "--strict", "--vault-root", str(FIXTURES),
        "--vault-root-allowlist", str(FIXTURES),
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["attacks"]["attack_count"] == 29
    assert payload["attacks"]["valid_count"] == 1
    assert payload["attacks"]["pass"] is True


@pytest.mark.parametrize("flag", ["--assets-tsv", "--sources-tsv", "--allow-catalog-override"])
def test_external_catalog_override_flags_are_not_in_cli(flag: str, tmp_path: Path) -> None:
    fake = tmp_path / "fake.tsv"
    fake.write_text("fake\n", encoding="utf-8")
    result = run_cli(
        "--root", str(VALID), "--strict", "--vault-root", str(FIXTURES),
        "--vault-root-allowlist", str(FIXTURES), flag, str(fake),
    )
    assert result.returncode == 2
    assert "unrecognized arguments" in result.stderr
    assert PASS not in result.stdout


def test_forged_vault_and_pack_only_pin_fail_closed() -> None:
    fid = "ATTACK_forged_vault_root_fake_catalog"
    case_dir = FIXTURES / fid
    case = json.loads((case_dir / "FIXTURE_CASE.json").read_text(encoding="utf-8"))
    fake_vault = case_dir / case["vault_root"]
    report, code = audit_backtest(AuditConfig(
        root=case_dir, profile="strict", strict=True, vault_root=fake_vault,
        run_attack_suite=False,
    ))
    assert code == 2
    text = " ".join(report["errors"])
    assert "pack-only" in text or "identity" in text
    assert report["catalog_refs"]["vault_identity_bound"] is False


def test_inventory_mutation_after_freeze_is_detected(tmp_path: Path) -> None:
    root = tmp_path / "pack"
    shutil.copytree(VALID, root)
    with (root / "data" / "panel.csv").open("a", encoding="utf-8") as f:
        f.write("2026-01-02T01:00:00Z,2026-01-02T01:00:00Z,r2,999\n")
    report, code = audit_backtest(config(root))
    assert code == 1
    d0 = next(c for c in report["checks"] if c["id"] == "D0")
    assert d0["result"] == "FAIL"
    assert "inventory drift" in " ".join(d0["errors"])


def test_mutating_attack_to_good_turns_catalog_expectation_red(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    suite = tmp_path / "suite"
    shutil.copytree(FIXTURES, suite)
    attack = suite / "ATTACK_unregistered_asset_claimed_present"
    good = suite / "VALID_minimal_registered_pack"
    # Replace the attack pack with the honest pack while retaining attack id/case.
    case_text = (attack / "FIXTURE_CASE.json").read_text(encoding="utf-8")
    shutil.rmtree(attack)
    shutil.copytree(good, attack)
    (attack / "FIXTURE_CASE.json").write_text(case_text, encoding="utf-8")
    manifest = json.loads((attack / "PACK_MANIFEST.json").read_text(encoding="utf-8"))
    manifest["pack_id"] = "ATTACK_unregistered_asset_claimed_present"
    (attack / "PACK_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    refresh_inventory(attack)
    monkeypatch.setattr("falsify.audit_backtest._fixture_root", lambda: suite)
    result = _run_attack_suite("strict")
    assert result["pass"] is False
    item = result["cases"]["ATTACK_unregistered_asset_claimed_present"]
    assert item["actual"] == "ACCEPT"
    assert item["expected"] == "REJECT"
    assert item["pass"] is False


def test_cli_outputs_are_outside_pack_and_inputs_remain_read_only(tmp_path: Path) -> None:
    before = {p.relative_to(VALID).as_posix(): sha(p) for p in VALID.rglob("*") if p.is_file()}
    out_json = tmp_path / "report.json"
    out_md = tmp_path / "report.md"
    result = run_cli(
        "--root", str(VALID), "--strict", "--vault-root", str(FIXTURES),
        "--vault-root-allowlist", str(FIXTURES), "--out-json", str(out_json),
        "--out-md", str(out_md), "--expect-pack-id", "VALID_minimal_registered_pack",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["verdict"] == PASS
    assert payload["authority"] is False
    assert payload["catalog_refs"]["vault_identity_bound"] is True
    assert len(payload["catalog_refs"]["assets_tsv_sha256"]) == 64
    assert "Data checks first" in out_md.read_text(encoding="utf-8")
    after = {p.relative_to(VALID).as_posix(): sha(p) for p in VALID.rglob("*") if p.is_file()}
    assert after == before


def test_output_inside_pack_is_blocked() -> None:
    result = run_cli(
        "--root", str(VALID), "--strict", "--vault-root", str(FIXTURES),
        "--vault-root-allowlist", str(FIXTURES),
        "--out-json", str(VALID / "forbidden-report.json"),
    )
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["verdict"] == "BACKTEST_PACK_CHECK_BLOCK"
    assert not (VALID / "forbidden-report.json").exists()


@pytest.mark.parametrize(
    "flag,target_kind",
    [
        ("--out-json", "root"),
        ("--out-md", "claim"),
        ("--out-json", "root_child"),
        ("--out-md", "catalog_dir"),
        ("--out-json", "assets"),
        ("--out-md", "sources"),
    ],
)
def test_output_containment_matrix_is_write_before_safe(flag: str, target_kind: str) -> None:
    targets = {
        "root": VALID,
        "claim": VALID / "CLAIM.json",
        "root_child": VALID / "data" / "forbidden-report.json",
        "catalog_dir": FIXTURES / "数据资产目录",
        "assets": FIXTURES / "数据资产目录" / "assets.tsv",
        "sources": FIXTURES / "数据资产目录" / "sources.tsv",
    }
    target = targets[target_kind]
    root_before, catalog_before = tree_hash(VALID), tree_hash(FIXTURES / "数据资产目录")
    result = run_cli(
        "--root", str(VALID), "--strict", "--vault-root", str(FIXTURES),
        "--vault-root-allowlist", str(FIXTURES), flag, str(target),
    )
    assert result.returncode != 0
    assert PASS not in result.stdout
    assert tree_hash(VALID) == root_before
    assert tree_hash(FIXTURES / "数据资产目录") == catalog_before
    if target_kind == "root_child":
        assert not target.exists()


def test_forbidden_flag_early_error_cannot_write_pack() -> None:
    before = tree_hash(VALID)
    target = VALID / "CLAIM.json"
    result = run_cli(
        "--root", str(VALID), "--strict", "--vault-root", str(FIXTURES),
        "--vault-root-allowlist", str(FIXTURES),
        "--assets-tsv", "external-fake.tsv", "--out-json", str(target),
    )
    assert result.returncode != 0
    assert PASS not in result.stdout
    assert tree_hash(VALID) == before


def test_output_symlink_escape_both_directions_when_supported(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    shutil.copytree(VALID, pack)
    outside = tmp_path / "outside"
    outside.mkdir()
    link_to_pack = outside / "link-to-pack"
    link_out = pack / "link-out"
    try:
        link_to_pack.symlink_to(pack, target_is_directory=True)
        link_out.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlink/reparse creation unavailable on this Windows host")
    before = tree_hash(pack)
    for target in (link_to_pack / "CLAIM.json", link_out / "report.json"):
        result = run_cli(
            "--root", str(pack), "--strict", "--vault-root", str(FIXTURES),
            "--vault-root-allowlist", str(FIXTURES), "--out-json", str(target),
        )
        assert result.returncode != 0
        assert PASS not in result.stdout
    assert tree_hash(pack) == before
    assert not (outside / "report.json").exists()


def test_import_graph_has_no_execution_authority_imports() -> None:
    source = (Path(__file__).resolve().parents[1] / "falsify" / "audit_backtest.py").read_text(encoding="utf-8")
    forbidden = ("executor", "order", "broker", "wallet", "live_deploy", "trading", "quant_gate")
    import_lines = [line.strip().lower() for line in source.splitlines() if line.strip().startswith(("import ", "from "))]
    assert not any(token in line for line in import_lines for token in forbidden)


def test_report_verdict_never_promotes_forbidden_authority() -> None:
    report, code = audit_backtest(config(VALID))
    assert code == 0
    assert report["authority"] is False
    assert report["verdict"] == PASS
    forbidden = {"STRATEGY_PASS", "LIVE_OK", "CAPITAL_PASS", "GATE_A_PASS", "GATE_B_PASS"}
    assert report["verdict"] not in forbidden


def test_bad_json_fails_closed_without_traceback(tmp_path: Path) -> None:
    root = tmp_path / "pack"
    shutil.copytree(VALID, root)
    (root / "CLAIM.json").write_text("{not-json", encoding="utf-8")
    report, code = audit_backtest(config(root))
    assert code == 2
    assert report["verdict"] == "BACKTEST_PACK_CHECK_BLOCK"
    assert "invalid JSON" in " ".join(report["errors"])


def test_bad_canonical_tsv_fails_closed(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    shutil.copytree(FIXTURES / "数据资产目录", vault / "数据资产目录")
    (vault / "数据资产目录" / "assets.tsv").write_text("asset_id\tstatus\nVALID-ASSET\tHAVE_VERIFIED_COMPLETE\n", encoding="utf-8")
    root = tmp_path / "pack"
    shutil.copytree(VALID, root)
    manifest = json.loads((root / "PACK_MANIFEST.json").read_text(encoding="utf-8"))
    manifest["catalog_assets_sha256"] = sha(vault / "数据资产目录" / "assets.tsv")
    manifest["catalog_sources_sha256"] = sha(vault / "数据资产目录" / "sources.tsv")
    (root / "PACK_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    refresh_inventory(root)
    report, code = audit_backtest(AuditConfig(
        root=root, profile="strict", strict=True, vault_root=vault,
        vault_root_allowlist=[vault], run_attack_suite=False,
    ))
    assert code == 2
    assert "missing columns" in " ".join(report["errors"])


def test_manifest_path_escape_fails_closed(tmp_path: Path) -> None:
    root = tmp_path / "pack"
    shutil.copytree(VALID, root)
    manifest = json.loads((root / "PACK_MANIFEST.json").read_text(encoding="utf-8"))
    manifest["entities"]["claim"] = "../outside.json"
    (root / "PACK_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    report, code = audit_backtest(config(root))
    assert code == 2
    assert "path escape" in " ".join(report["errors"])


def test_symlink_pack_input_fails_closed_when_supported(tmp_path: Path) -> None:
    link = tmp_path / "pack-link"
    try:
        link.symlink_to(VALID, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation unavailable on this Windows host")
    report, code = audit_backtest(config(link))
    assert code == 2
    assert "symlink" in " ".join(report["errors"]).lower()
