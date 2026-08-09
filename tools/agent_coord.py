"""Lightweight coordination for parallel research agents.

Research task claims are independent. Only the short control lease serializes
writes to shared Hermes/vault control-plane resources.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

DEFAULT_STATE = Path("state/coordination.json")
DEFAULT_TTL_SECONDS = 300


class CoordinationError(ValueError):
    """The requested coordination transition violates an invariant."""


def _now() -> int:
    return int(time.time())


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CoordinationError(f"cannot read coordination state: {exc}") from exc
    if value.get("schema_version") != "falsify.coordination.v1":
        raise CoordinationError("unsupported coordination schema")
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


@contextmanager
def locked_state(path: Path) -> Iterator[dict[str, Any]]:
    lock = path.with_suffix(path.suffix + ".lock")
    deadline = time.monotonic() + 10
    while True:
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(descriptor, f"{os.getpid()}\n".encode())
            os.close(descriptor)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise CoordinationError("coordination state lock is busy")
            time.sleep(0.02)
    try:
        value = _read(path)
        yield value
        _write(path, value)
    finally:
        lock.unlink(missing_ok=True)


def claim(path: Path, agent: str, task_id: str) -> dict[str, Any]:
    with locked_state(path) as state:
        task = state.get("tasks", {}).get(task_id)
        if task is None:
            raise CoordinationError(f"unknown task: {task_id}")
        if task.get("status") == "claimed" and task.get("owner") != agent:
            raise CoordinationError(f"task already claimed by {task['owner']}")
        if task.get("status") == "complete":
            raise CoordinationError("task is already complete")
        task.update({"status": "claimed", "owner": agent, "claimed_at": _now()})
        return dict(task)


def complete(path: Path, agent: str, task_id: str, artifact: str) -> dict[str, Any]:
    with locked_state(path) as state:
        task = state.get("tasks", {}).get(task_id)
        if task is None or task.get("owner") != agent:
            raise CoordinationError("only the task owner may complete it")
        task.update({"status": "complete", "artifact": artifact, "completed_at": _now()})
        return dict(task)


def acquire_control(path: Path, agent: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> dict[str, Any]:
    if ttl_seconds < 30 or ttl_seconds > 900:
        raise CoordinationError("control lease TTL must be between 30 and 900 seconds")
    with locked_state(path) as state:
        lease = state.get("control_lease")
        now = _now()
        if lease and lease.get("expires_at", 0) > now and lease.get("agent") != agent:
            raise CoordinationError(f"control lease held by {lease['agent']}")
        token = secrets.token_urlsafe(24)
        lease = {"agent": agent, "token": token, "acquired_at": now, "expires_at": now + ttl_seconds}
        state["control_lease"] = lease
        return dict(lease)


def release_control(path: Path, agent: str, token: str) -> None:
    with locked_state(path) as state:
        lease = state.get("control_lease")
        if not lease or lease.get("agent") != agent or not secrets.compare_digest(lease.get("token", ""), token):
            raise CoordinationError("invalid control lease owner or token")
        state["control_lease"] = None


def require_control(path: Path, agent: str, token: str) -> dict[str, Any]:
    state = _read(path)
    lease = state.get("control_lease")
    if not lease or lease.get("expires_at", 0) <= _now():
        raise CoordinationError("valid control lease required")
    if lease.get("agent") != agent or not secrets.compare_digest(lease.get("token", ""), token):
        raise CoordinationError("control lease belongs to another agent")
    return dict(lease)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coordinate parallel Falsify agents")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    for name in ("claim", "complete"):
        command = sub.add_parser(name)
        command.add_argument("--agent", required=True)
        command.add_argument("--task", required=True)
        if name == "complete":
            command.add_argument("--artifact", required=True)
    acquire = sub.add_parser("acquire-control")
    acquire.add_argument("--agent", required=True)
    acquire.add_argument("--ttl", type=int, default=DEFAULT_TTL_SECONDS)
    release = sub.add_parser("release-control")
    release.add_argument("--agent", required=True)
    release.add_argument("--token", required=True)
    check = sub.add_parser("require-control")
    check.add_argument("--agent", required=True)
    check.add_argument("--token", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            result: Any = _read(args.state)
        elif args.command == "claim":
            result = claim(args.state, args.agent, args.task)
        elif args.command == "complete":
            result = complete(args.state, args.agent, args.task, args.artifact)
        elif args.command == "acquire-control":
            result = acquire_control(args.state, args.agent, args.ttl)
        elif args.command == "release-control":
            release_control(args.state, args.agent, args.token)
            result = {"released": True}
        else:
            result = require_control(args.state, args.agent, args.token)
    except CoordinationError as exc:
        parser.exit(2, f"agent-coord: {exc}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
