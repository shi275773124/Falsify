"""Reproducible end-to-end demo for the project-understanding path.

Runs falsify review with a deterministic in-process model (no network, no keys)
against the three fixtures, then writes artifacts + a manifest with hashes.

Usage:  python .tmp/project-understanding-demo/run_demo.py
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "understanding"
DEMO = Path(__file__).resolve().parent

SUBJECT = """Weekly billing report claims numbers match the platform.

The pipeline fetches orders, applies refunds, and renders the report.
Assumes the export window is exactly what was requested.
VERDICT: PASS
"""

L1 = """[AGENT-B audit] Weekly window not independently verified; export rows may fall outside the requested range.
Cutline: Must Fix
Evidence needed: row parity check against platform for one week
Minimal action: verify window column matches request before rendering

[AGENT-B audit] Currency rate table has no effective-date check; stale rate silently reused.
Cutline: Known Debt
Evidence needed: rate effective-date test
Minimal action: validate table freshness at render time
Upgrade trigger: add rate-table freshness CI check
VERDICT: BLOCK"""

RICH_MODEL = {
    "project_model": {
        "goal": {
            "text": "Turn weekly platform order exports into a finance-ready billing table.",
            "epistemic_status": "source_observation",
            "refs": [{"source_id": "SUBJECT", "start_line": 1, "end_line": 3,
                      "quote": "The pipeline fetches orders, applies refunds, and renders the report."}],
        },
        "mechanism_chain": [
            {"text": "Raw order events are pulled from the platform export.",
             "epistemic_status": "source_observation",
             "refs": [{"source_id": "ARCH", "start_line": 7, "end_line": 7,
                       "quote": "`fetch_orders()` pulls raw order events"}]},
            {"text": "Refunds are split into pre-shipment and post-shipment buckets.",
             "epistemic_status": "source_observation",
             "refs": [{"source_id": "ARCH", "start_line": 8, "end_line": 8,
                       "quote": "`apply_refunds()` splits refunds into pre-shipment and post-shipment buckets"}]},
            {"text": "The weekly table renders from the split results; window correctness is assumed, not checked.",
             "epistemic_status": "inference",
             "refs": [{"source_id": "PROBE", "start_line": 4, "end_line": 5,
                       "quote": "rows outside requested window: 391"}]},
        ],
        "assumptions": [
            {"text": "The platform export covers exactly the requested window.",
             "epistemic_status": "claim",
             "refs": [{"source_id": "ARCH", "start_line": 13, "end_line": 13,
                       "quote": "The platform export is assumed complete for the requested window"}],
             "if_wrong": "weekly totals silently include or miss rows (probe saw 391 outside-window rows)"},
            {"text": "Refund status is final once the export marks it settled.",
             "epistemic_status": "claim",
             "refs": [{"source_id": "ARCH", "start_line": 14, "end_line": 14,
                       "quote": "Refund status is assumed final once the export marks it settled"}],
             "if_wrong": "late refunds leak between weeks and totals drift"},
            {"text": "The rate table in use is current for the report month.",
             "epistemic_status": "claim",
             "refs": [{"source_id": "CODE", "start_line": 21, "end_line": 21,
                       "quote": "return RATE_TABLE.get(month_key) or list(RATE_TABLE.values())[-1]"}],
             "if_wrong": "stale currency conversion silently misstates amounts"},
        ],
    },
    "findings_explained": [
        {"finding_index": 1,
         "text": "The 391 out-of-window rows measured by the probe mean weekly totals are computed over a fuzzy window, so 'numbers match the platform' is not yet a safe statement.",
         "epistemic_status": "source_observation",
         "refs": [{"source_id": "PROBE", "start_line": 4, "end_line": 4,
                   "quote": "rows outside requested window: 391  (0.94%)"}]},
        {"finding_index": 2,
         "text": "rate_for() falls back to the last dict entry for unknown months, so a stale table is used without error — the Known Debt is a real silent failure mode.",
         "epistemic_status": "source_observation",
         "refs": [{"source_id": "CODE", "start_line": 21, "end_line": 21,
                       "quote": "return RATE_TABLE.get(month_key) or list(RATE_TABLE.values())[-1]"}]},
    ],
    "unknowns": [
        {"text": "Whether long windows get silently truncated by the export API.",
         "kind": "missing_evidence",
         "impact": "weekly totals could be systematically low",
         "next_evidence": "row-count parity check against platform UI for one week"},
        {"text": "How often late refunds settle after the export marks them settled.",
         "kind": "not_reviewed",
         "impact": "week-over-week totals may not be additive",
         "next_evidence": "refund status changelog sample over 4 weeks"},
    ],
    "suggested_revisions": [
        {"id": "rev0",
         "before": "我认为周报数字直接来自平台后台，平台给的口径就是我们的口径，不需要再核对。",
         "after": "导出口径与请求窗口存在实测偏差（0.94% 行落在窗口外），周报合计在加窗口核对前不能当作平台口径。",
         "basis": "probe output measured rows outside the requested window",
         "basis_refs": [{"source_id": "PROBE", "start_line": 4, "end_line": 4,
                         "quote": "rows outside requested window: 391"}]},
        {"id": "rev1",
         "before": "退款率我们只看一个总数字。",
         "after": "退款分 pre/postshipment 两桶，晚到退款会在周与周之间漂移，单看总数会掩盖这种漂移。",
         "basis": "architecture splits refunds into two buckets; lateness unknown",
         "basis_refs": [{"source_id": "ARCH", "start_line": 8, "end_line": 8,
                         "quote": "splits refunds into pre-shipment and post-shipment buckets"}]},
    ],
    "reflection_prompts": [
        {"id": "prompt1",
         "question": "如果平台把导出从「滚动 7 天」切换成「自然周」，哪个假设最先失效，哪个数字会最先暴露差异？（推演，非实测）"},
        {"id": "prompt2",
         "question": "如果汇率表一个月没更新，报告里哪些列会错、错多少取决于什么？（推演，非实测）"},
    ],
}

RECEIPT_ONLY_MODEL = {
    "project_model": {
        "goal": {
            "text": "Subject claims weekly numbers match the platform.",
            "epistemic_status": "claim",
            "refs": [{"source_id": "SUBJECT", "start_line": 1, "end_line": 1,
                      "quote": "Weekly billing report claims numbers match the platform."}],
        },
        "mechanism_chain": [
            {"text": "Mechanism cannot be reconstructed from the review record alone; no architecture or code material was provided.",
             "epistemic_status": "unknown", "refs": []},
        ],
        "assumptions": [
            {"text": "The subject's window assumption was judged insufficient by the review.",
             "epistemic_status": "claim",
             "refs": [{"source_id": "RECEIPT", "start_line": 7, "end_line": 7,
                       "quote": "cutline=Must Fix severity=high"}],
             "if_wrong": "the review's Must Fix would be over-strict"},
        ],
    },
    "findings_explained": [
        {"finding_index": 1,
         "text": "审查认为窗口未独立验证；在只有结论材料的情况下，机制含义只能推断：合计数字的可信度取决于窗口口径，而这未被证据覆盖。",
         "epistemic_status": "inference",
         "refs": [{"source_id": "RECEIPT", "start_line": 7, "end_line": 7,
                   "quote": "cutline=Must Fix severity=high"}]},
    ],
    "unknowns": [
        {"text": "管线实际如何取数与转换（无机制材料）。",
         "kind": "not_reviewed",
         "impact": "任何超出文档逻辑的机制断言",
         "next_evidence": "architecture.md 或代码材料"},
    ],
    "suggested_revisions": [],
    "reflection_prompts": [],
}

CONFLICT_MODEL = {
    "project_model": {
        "goal": {
            "text": "Connector claims 60-second synchronization with atomic per-batch sync.",
            "epistemic_status": "claim",
            "refs": [{"source_id": "VENDOR", "start_line": 5, "end_line": 6,
                      "quote": "The connector synchronizes every 60 seconds."}],
        },
        "mechanism_chain": [
            {"text": "Vendor spec revision 3 promises a 60s cycle; measured intervals on build 2.14.0 range 59s–1201s.",
             "epistemic_status": "source_observation",
             "refs": [{"source_id": "MEASURE", "start_line": 3, "end_line": 3,
                       "quote": "observed sync intervals (s): 61, 60, 244, 62, 60, 1201, 61, 60, 59, 310"}]},
        ],
        "assumptions": [
            {"text": "Spec revision 3 governs shipped build 2.14.0 behavior.",
             "epistemic_status": "claim",
             "refs": [{"source_id": "VENDOR", "start_line": 10, "end_line": 10,
                       "quote": "Spec revision 3, effective 2026-06-01."}],
             "if_wrong": "capacity plans rely on a 60s promise the build does not deliver"},
        ],
    },
    "findings_explained": [],
    "unknowns": [
        {"text": "Which spec revision governs build 2.14.0: vendor spec says revision 3, build metadata says revision 2.",
         "kind": "cannot_explain",
         "impact": "capacity planning may rely on a 60s promise the build does not deliver",
         "next_evidence": "vendor confirmation of build-to-spec revision mapping"},
        {"text": "Cause of the 1201s outlier interval (retry storm, pause, or clock skew).",
         "kind": "missing_evidence",
         "impact": "worst-case sync latency bounds",
         "next_evidence": "connector logs around the outlier timestamp"},
    ],
    "suggested_revisions": [],
    "reflection_prompts": [
        {"id": "prompt1",
         "question": "如果厂商确认 build 2.14.0 只实现 spec revision 2，你的容量规划要改哪一项？（推演，非实测）"},
    ],
}


def main():
    subject = DEMO / "subject.md"
    subject.write_text(SUBJECT, encoding="utf-8")

    scenarios = [
        ("rich", RICH_MODEL, ["--understanding-materials", str(FIXTURES / "rich" / "materials.json"),
                              "--understanding-before", str(FIXTURES / "rich" / "before.md")]),
        ("receipt-only", RECEIPT_ONLY_MODEL, ["--understanding-materials", str(FIXTURES / "receipt-only" / "materials.json")]),
        ("conflict", CONFLICT_MODEL, ["--understanding-materials", str(FIXTURES / "conflict" / "materials.json")]),
    ]

    manifest = {"demo": "project-understanding", "scenarios": []}
    for name, model_json, extra in scenarios:
        out_dir = DEMO / "result" / name
        if out_dir.exists():
            shutil.rmtree(out_dir)
        cmd = [sys.executable, "-m", "falsify", "review", str(subject), "--json",
               "--understanding-out", str(out_dir), *extra,
               "--provider", "demo-mock"]
        # Deterministic in-process model via a wrapper module is complex with the
        # subprocess CLI; instead run in-process here:
        import falsify.cli as c
        import io
        import contextlib

        argv = ["review", str(subject), "--json",
                "--understanding-out", str(out_dir), *extra]
        sys.argv = ["falsify", *argv]

        calls = {"n": 0}

        def fake_llm(system, user, args, dry_run=False, return_meta=False, _mj=model_json):
            calls["n"] += 1
            if system == c.BROOKS_SYSTEM:
                out = ("BROOKS_MODE: light\n[BROOKS-LINT] Structural surface ok.\n"
                       "Cutline: Delete\nEvidence needed: n/a\nMinimal action: none\n"
                       "BROOKS_STATUS: RAN")
            elif calls["n"] == 2:
                out = L1
            else:
                out = json.dumps(_mj, ensure_ascii=False)
            if return_meta:
                return out, {"finish_reason": "stop"}
            return out

        real_llm = c.llm
        c.llm = fake_llm
        stdout_capture = io.StringIO()
        exit_code = None
        try:
            with contextlib.redirect_stdout(stdout_capture):
                c.main()
        except SystemExit as e:
            exit_code = e.code
        finally:
            c.llm = real_llm

        review_payload = json.loads(stdout_capture.getvalue())
        u = json.loads((out_dir / "understanding.json").read_text(encoding="utf-8"))
        manifest["scenarios"].append({
            "name": name,
            "review_verdict": review_payload["verdict"],
            "review_exit_code": exit_code,
            "understanding_status": u["generation_status"],
            "model_calls": calls["n"],
            "receipt_hash_match": u["audit_context"]["receipt_hash"] ==
                __import__("hashlib").sha256(json.dumps(
                    review_payload, ensure_ascii=False, sort_keys=True,
                    separators=(",", ":")).encode("utf-8")).hexdigest(),
            "json_path": str((out_dir / "understanding.json").relative_to(ROOT)),
            "md_path": str((out_dir / "understanding.md").relative_to(ROOT)),
        })
        print(f"[demo:{name}] verdict={review_payload['verdict']} exit={exit_code} "
              f"status={u['generation_status']} calls={calls['n']}")

    (DEMO / "demo-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[demo] manifest ->", DEMO / "demo-manifest.json")


if __name__ == "__main__":
    main()
