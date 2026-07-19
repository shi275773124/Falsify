"""Command line adapter for the fail-closed Alpha Discovery Factory queue."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from falsify.discovery import strict_summary, transition, validate_queue


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def save_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_receipt(summary: dict) -> str:
    return "\n".join((
        "# Alpha Discovery Factory Receipt",
        "",
        f"- Schema: `{summary['schema_version']}`",
        f"- Strict campaign candidates: `{summary['strict_campaign_count']}`",
        f"- Strict terminal candidates: `{summary['strict_terminal_count']}`",
        f"- Promotion-eligible seeds: `{summary['promotion_eligible_count']}`",
        f"- Historical excluded IDs: `{', '.join(summary['excluded_historical_ids']) or 'none'}`",
        f"- Queue hash: `{summary['queue_hash']}`",
        "",
        "Canonical vault write is intentionally external: only apply this receipt after `git pull --rebase` succeeds in the vault.",
        "",
    ))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Alpha Discovery Factory queue")
    sub = parser.add_subparsers(dest="command", required=True)
    status = sub.add_parser("status", help="validate queue and print strict summary")
    status.add_argument("queue", type=Path)
    status.add_argument("--receipt", type=Path)
    move = sub.add_parser("transition", help="apply one legal transition")
    move.add_argument("queue", type=Path)
    move.add_argument("candidate_id")
    move.add_argument("target")
    move.add_argument("evidence", type=Path)
    move.add_argument("--receipt", type=Path)
    args = parser.parse_args(argv)
    queue = load_json(args.queue)
    validate_queue(queue)
    if args.command == "transition":
        event = transition(queue, args.candidate_id, args.target, load_json(args.evidence))
        save_json(args.queue, queue)
        print(json.dumps(event, ensure_ascii=False, indent=2))
    summary = strict_summary(queue)
    if args.receipt:
        args.receipt.write_text(render_receipt(summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""Command line adapter for the fail-closed Alpha Discovery Factory queue."""
