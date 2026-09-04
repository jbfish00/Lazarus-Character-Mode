#!/bin/sh
# LIVE egg-hatch e2e (../game_plans/rowe_parity.md §13.21 item 1).
#
# The hatch hook shipped 2026-09-04 verified statically (five checks in
# verify_artifacts.py, negative-tested 6/6) and by every pre-existing live
# layer -- but until this suite no hatch had ever been WALKED in an emulator
# here, so "the hatch calls the sweep" rested entirely on reading bytes.
#
# tools/tests/build_egg_testrom.py repoints the University desk (8,8) at
#   giveegg 60 ; setvar 0x8004,1 ; goto EventScript_EggHatch
# and everything after the goto is SHIPPED. Poliwag 60 is deliberate: it is ON
# Misty's roster and OFF Red's, so one species discriminates all three cases.
#
# Four runs, and the fourth is the point: with the splice reverted the same run
# must FAIL, or the layer is only ever testing that the sweep works when
# something calls it. Exit 0 = all four behaved.
set -e
cd "$(dirname "$0")/../.."

MGBA=../Seaglass-Character-Mode/tools/mgba_src/build/mgba-headless
STATE=tools/savestates/cm_red_active.ss
SCRIPT=tools/mgba_scripts/cm_egg_hatch_test.lua

python3 tools/tests/build_egg_testrom.py 60 1
python3 tools/tests/build_egg_testrom.py 60 1 --no-hook

# CM_SweepPartyToPCNative moves on every shim rebuild; a stale literal here
# would report "the tail never reached the sweep" on a ROM where it plainly did.
CM_SWEEP_ADDR=$(arm-none-eabi-nm build/character_mode.elf \
    | awk '/ T CM_SweepPartyToPCNative$/{printf "0x%s\n", toupper($1)}')
[ -n "$CM_SWEEP_ADDR" ] || { echo "[FAIL] locating CM_SweepPartyToPCNative"; exit 1; }
export CM_SWEEP_ADDR MGBA_HEADLESS_DEBUGGER=1
echo "  (sweep @ $CM_SWEEP_ADDR)"

fail=0
egg_case() {  # name  cfg  rom
    echo "$2" > build/cm_egg_mode.lua
    log=build/egg_e2e_$1.log
    CM_EXPECT_CHECKS=5 timeout 200 "$MGBA" -t "$STATE" --script "$SCRIPT" "$3" \
        > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: PASS" "$log"; then
        echo "[PASS] egg hatch $1 (5 checks)"
    else
        echo "[FAIL] egg hatch $1 (see $log)"; grep -a "HARNESS" "$log" | tail -8
        fail=1
    fi
}
EGGROM=build/lazarus_cm_eggtest.gba
egg_case red   'return {cm_on=true, char=1, expect="box", name="red"}'      "$EGGROM"
egg_case misty 'return {cm_on=true, char=10, expect="party", name="misty"}' "$EGGROM"
egg_case off   'return {cm_on=false, expect="party", name="off"}'           "$EGGROM"

# ⭐ The negative control. No CM_EXPECT_CHECKS: the run must die on the missing
# sweep, not on a tally mismatch, or a future harness change could keep this
# "failing" for the wrong reason and the layer would stop discriminating.
echo 'return {cm_on=true, char=1, expect="box", name="nohook"}' > build/cm_egg_mode.lua
log=build/egg_e2e_nohook.log
timeout 200 "$MGBA" -t "$STATE" --script "$SCRIPT" \
    build/lazarus_cm_eggtest_nohook.gba > "$log" 2>&1 || true
if grep -aq "HARNESS RESULT: FAIL" "$log" \
   && grep -aq "reached the sweep (timeout)" "$log"; then
    echo "[PASS] egg hatch NEGATIVE CONTROL (hook absent -> layer fails)"
else
    echo "[FAIL] negative control did not fail, or failed for another reason (see $log)"
    fail=1
fi
exit $fail
