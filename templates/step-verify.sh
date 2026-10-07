#!/usr/bin/env bash
# step-verify.sh — sentinel guard for multi-step pipelines.
#
# Why this exists: a step can "fail closed" by writing an ABORT file and exiting 0.
# The scheduler sees exit 0 and is happy. Downstream steps run on missing/aborted
# input, stay internally consistent, and nobody notices until a human asks hours
# later. fail-close-by-writing-ABORT is NOT fail-loud.
#
# This script verifies a step's OUTPUT actually exists and is real:
#   1. the output file exists
#   2. it is at least MIN_BYTES big
#   3. it does NOT start with an ABORT/ERROR marker
# Any failure -> non-zero exit (and an optional notification) so the chain stops loud.
#
# Usage:
#   ./step-verify.sh <output-file> [min-bytes]
# Example (in a pipeline):
#   run_step_4 || exit 2
#   ./step-verify.sh out/step-4-result.md 200 || exit 2
#   run_step_5 ...

set -euo pipefail

OUT_FILE="${1:?usage: step-verify.sh <output-file> [min-bytes]}"
MIN_BYTES="${2:-100}"

# --- optional: wire your own alerting here (Telegram, Slack, email, ...) ---
notify() {
  # echo to stderr always; replace the body with a real webhook if you want
  echo "ALERT: $*" >&2
  # curl -s -X POST "$ALERT_WEBHOOK" -d "text=$*" >/dev/null 2>&1 || true
}

fail() { notify "step-verify FAILED: $1"; exit 2; }

# 1. exists
[ -f "$OUT_FILE" ] || fail "missing output: $OUT_FILE"

# 2. size floor
size=$(wc -c < "$OUT_FILE" | tr -d ' ')
[ "$size" -ge "$MIN_BYTES" ] || fail "output too small ($size < $MIN_BYTES bytes): $OUT_FILE"

# 3. not an abort/error sentinel at the top
first_line=$(head -n 1 "$OUT_FILE" | tr '[:lower:]' '[:upper:]')
case "$first_line" in
  ABORT*|ERROR*|FAILED*|BLOCKED*) fail "output is an abort/error sentinel: $OUT_FILE ($first_line)";;
esac

echo "step-verify OK: $OUT_FILE ($size bytes)"
