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

# ⭐ Every layer declares the number of assertions it MUST run, as the 4th
# argument. It reaches the script as CM_EXPECT_CHECKS, and H.finish() turns
# both "ran zero assertions" and "ran a different number than declared" into
# RESULT: FAIL -- so the grep below catches them with no extra plumbing
# (../game_plans/rowe_parity.md §1; proved by tools/tests/harness_guard_test.sh).
#
# Why: until 2026-08-20 H.finish() emitted RESULT: PASS whenever nothing had
# FAILED, and the pass count was printed and never read. A layer that
# mis-navigated, lost its savestate, or had its checks edited away was
# indistinguishable here from one that passed, so "LIVE SUITE: ALL PASS" was
# consistent with any number of these layers asserting nothing. Seaglass turned
# out to have exactly that (its boot layer checked nothing at all).
# If you change a layer's assertions, update its number; a changed tally is a
# regression until a human says otherwise.
run() { # name savestate script expected_checks
    name=$1; state=$2; script=$3; expect=$4
    log=build/live_$name.log
    if [ -n "$state" ]; then
        CM_EXPECT_CHECKS="$expect" timeout 110 "$MGBA" -t "$state" --script "$script" "$ROM" > "$log" 2>&1 || true
    else
        CM_EXPECT_CHECKS="$expect" timeout 110 "$MGBA" --script "$script" "$ROM" > "$log" 2>&1 || true
    fi
    if grep -aq "HARNESS RESULT: PASS" "$log"; then
        echo "[PASS] $name ($expect checks)"
    else
        echo "[FAIL] $name (see $log)"
        grep -a "HARNESS" "$log" | tail -6
        fail=1
    fi
}

# Injection addresses the Lua tests need, parsed from the injector rather than
# copied into them. build/ is gitignored, so this must be regenerated per run.
mkdir -p build
python3 - > build/cm_layout.lua <<'PYEOF'
import pathlib, re
src = pathlib.Path("tools/inject_character_mode.py").read_text()
def addr(name):
    m = re.search(r"^%s\s*=\s*(0x[0-9A-Fa-f]+)" % name, src, re.M)
    if not m:
        raise SystemExit("could not parse %s out of the injector" % name)
    return int(m.group(1), 16)
print("return {mugshot_addr=%d, bitmaps_addr=%d, hidden_addr=%d}"
      % (addr("CM_MUGSHOT_ADDR"), addr("BITMAPS_ADDR"), addr("HIDDEN_ADDR")))
PYEOF

run boot_smoke "" tools/mgba_scripts/boot_smoke.lua 4

echo 'return {cm_on=true}'  > build/cm_test_mode.lua
run catch_gate_on  tools/savestates/battle_bag.ss tools/mgba_scripts/cm_gate_test.lua 3
run starter_on     tools/savestates/spawn.ss      tools/mgba_scripts/cm_starter_test.lua 2
echo 'return {cm_on=false}' > build/cm_test_mode.lua
run catch_gate_off tools/savestates/battle_bag.ss tools/mgba_scripts/cm_gate_test.lua 1
run starter_off    tools/savestates/spawn.ss      tools/mgba_scripts/cm_starter_test.lua 1

# cheat-UI activation (also regenerates cm_red_active.ss for the tests below)
echo 'return {code="red", expect="activate_red"}' > build/cm_ui_code.lua
run ui_activate_red tools/savestates/naming.ss tools/mgba_scripts/cm_cheat_ui_test.lua 9

echo 'return {code="cmdbggive2", expect="give2", open_desk=true}' > build/cm_ui_code.lua
run ui_give2_boxing tools/savestates/cm_red_active.ss tools/mgba_scripts/cm_cheat_ui_test.lua 3

run save_load tools/savestates/cm_red_active.ss tools/mgba_scripts/cm_saveload_test.lua 3

sh tools/tests/run_trade_e2e.sh || fail=1

echo
[ $fail -eq 0 ] && echo "LIVE SUITE: ALL PASS" || echo "LIVE SUITE: FAILURES"
exit $fail
