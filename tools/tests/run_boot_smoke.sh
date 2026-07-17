#!/bin/sh
# Boot smoke: cold boot -> A-mash -> SaveBlock trio live in EWRAM + spawn
# map 0.57 reached (tools/mgba_scripts/boot_smoke.lua). Runs the patched
# build by default; pass a ROM path to test another (e.g. the original for
# a baseline). The RR-inherited GDB variant was dropped: its gMain
# addresses are FRLG-only and the Lua assertions are strictly stronger.
#   usage: run_boot_smoke.sh [rom.gba]
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
ROM="${1:-$ROOT/build/lazarus_cm.gba}"
MGBA="$ROOT/../Seaglass-Character-Mode/tools/mgba_src/build/mgba-headless"
LOG="$ROOT/build/boot_smoke.$(basename "$ROM" .gba | tr -c 'A-Za-z0-9._-' '_').log"

[ -f "$ROM" ] || { echo "ROM missing: $ROM"; exit 1; }

cd "$ROOT"
timeout 110 "$MGBA" --script tools/mgba_scripts/boot_smoke.lua "$ROM" > "$LOG" 2>&1 || true

grep -a "HARNESS" "$LOG" | tail -8
if grep -aq "HARNESS RESULT: PASS" "$LOG"; then
    echo "[PASS] boot smoke: $ROM"
    exit 0
else
    echo "[FAIL] boot smoke: $ROM (see $LOG)"
    exit 1
fi
