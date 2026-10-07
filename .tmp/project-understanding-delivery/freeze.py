"""Freeze the project-understanding delivery: hash all touched files.

Writes .tmp/project-understanding-delivery/freeze-manifest.json
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

FILES = [
    "falsify/understanding.py",
    "falsify/cli.py",
    "web/serve.py",
    "web/understanding/index.html",
    "web/understanding/understanding.js",
    "web/understanding/understanding.css",
    "tests/test_understanding.py",
    "tests/test_web.py",
    "tests/fixtures/understanding/rich/materials.json",
    "tests/fixtures/understanding/rich/architecture.md",
    "tests/fixtures/understanding/rich/billing.py",
    "tests/fixtures/understanding/rich/probe-output.txt",
    "tests/fixtures/understanding/rich/before.md",
    "tests/fixtures/understanding/receipt-only/materials.json",
    "tests/fixtures/understanding/conflict/materials.json",
    "tests/fixtures/understanding/conflict/vendor-spec.md",
    "tests/fixtures/understanding/conflict/measurement.md",
    "docs/contracts/project-understanding.schema.json",
    "docs/project-understanding-guide.zh-CN.md",
    "docs/project-understanding-implementation-plan.zh-CN.md",
    "docs/project-understanding-proposal.zh-CN.md",
]


def main():
    manifest = {"purpose": "freeze for non-author independent audit",
                "generated_at": subprocess.run(
                    ["git", "log", "-1", "--format=%H %cI"],
                    capture_output=True, text=True, cwd=ROOT).stdout.strip(),
                "files": {}}
    missing = []
    for rel in FILES:
        p = ROOT / rel
        if not p.is_file():
            missing.append(rel)
            continue
        blob = p.read_bytes()
        manifest["files"][rel] = {
            "sha256": hashlib.sha256(blob).hexdigest(),
            "bytes": len(blob),
        }
    if missing:
        print("MISSING:", missing)
        sys.exit(1)
    (OUT / "freeze-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"froze {len(manifest['files'])} files -> {OUT / 'freeze-manifest.json'}")


if __name__ == "__main__":
    main()
