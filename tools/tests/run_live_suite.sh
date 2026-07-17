#!/bin/sh
# Full live regression suite for Lazarus Character Mode (headless mGBA).
# Runs every savestate-driven e2e against build/lazarus_cm.gba and prints a
# PASS/FAIL summary. ~2 min wall (harness os.exit-s at finish). Exit 0 = everything green.
#
# Layers not covered here (run separately):
#   python3 tools/tests/shim_unit_test.py      # GDB decision-table unit tests
#   python3 tools/tests/verify_artifacts.py    # static artifact verification
cd "$(dirname "$0")/../.."

MGBA=../Seaglass-Character-Mode/tools/mgba_src/build/mgba-headless
ROM=build/lazarus_cm.gba
fail=0

run() { # name savestate script [pre-command]
    name=$1; state=$2; script=$3
    log=build/live_$name.log
    if [ -n "$state" ]; then
        timeout 110 "$MGBA" -t "$state" --script "$script" "$ROM" > "$log" 2>&1 || true
    else
        timeout 110 "$MGBA" --script "$script" "$ROM" > "$log" 2>&1 || true
    fi
    if grep -aq "HARNESS RESULT: PASS" "$log"; then
        echo "[PASS] $name"
    else
        echo "[FAIL] $name (see $log)"
        grep -a "HARNESS" "$log" | tail -6
        fail=1
    fi
}

run boot_smoke "" tools/mgba_scripts/boot_smoke.lua

echo 'return {cm_on=true}'  > build/cm_test_mode.lua
run catch_gate_on  tools/savestates/battle_bag.ss tools/mgba_scripts/cm_gate_test.lua
run starter_on     tools/savestates/spawn.ss      tools/mgba_scripts/cm_starter_test.lua
echo 'return {cm_on=false}' > build/cm_test_mode.lua
run catch_gate_off tools/savestates/battle_bag.ss tools/mgba_scripts/cm_gate_test.lua
run starter_off    tools/savestates/spawn.ss      tools/mgba_scripts/cm_starter_test.lua

# cheat-UI activation (also regenerates cm_red_active.ss for the tests below)
echo 'return {code="red", expect="activate_red"}' > build/cm_ui_code.lua
run ui_activate_red tools/savestates/naming.ss tools/mgba_scripts/cm_cheat_ui_test.lua

echo 'return {code="cmdbggive2", expect="give2", open_desk=true}' > build/cm_ui_code.lua
run ui_give2_boxing tools/savestates/cm_red_active.ss tools/mgba_scripts/cm_cheat_ui_test.lua

run save_load tools/savestates/cm_red_active.ss tools/mgba_scripts/cm_saveload_test.lua

sh tools/tests/run_trade_e2e.sh || fail=1

echo
[ $fail -eq 0 ] && echo "LIVE SUITE: ALL PASS" || echo "LIVE SUITE: FAILURES"
exit $fail
