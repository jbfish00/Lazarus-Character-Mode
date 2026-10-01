#!/bin/sh
# LIVE e2e for the link-trade sweep (src/character_mode.c
# CM_LinkTradeSweepThenExpand; verify_artifacts section 18; rowe_parity.md
# §13.53). Reuses the PC-guard fixture (party [Pikachu, alive Poliwag]) and runs
# the REAL trade enders from state 0 up to their hooked BL -- the wired
# CB2_SaveAndEndTrade and the wireless CB2_SaveAndEndWirelessTrade. A real link
# trade needs two consoles; this is the closest single-console run of the hook.
# ⭐ Asserts WHICH mon moved: Red boxes Poliwag, Misty boxes Pikachu, CM off
# moves nothing, and the --no-link-sweep ROM must fail on both enders.
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
STATE=tools/savestates/cm_red_active.ss
SCRIPT=tools/mgba_scripts/cm_link_trade_sweep_test.lua

python3 tools/tests/build_pc_testrom.py 60 1 >/dev/null
python3 tools/tests/build_pcguard_testrom.py --no-link-sweep >/dev/null

CM_SHIM_ADDR=$(arm-none-eabi-nm build/character_mode.elf \
    | awk '/ T CM_LinkTradeSweepThenExpand$/{printf "0x%s\n", toupper($1)}')
[ -n "$CM_SHIM_ADDR" ] || { echo "[FAIL] locating CM_LinkTradeSweepThenExpand"; exit 1; }
CM_PSS_ADDR=$(python3 -c "
import sys, struct
sys.path.insert(0, 'tools/character_mode')
import pc_hook
d = open('build/lazarus_cm.gba','rb').read()
off = pc_hook.SPECIALS_TABLE_ADDR - 0x08000000 + pc_hook.SPECIAL_PC * 4
print('0x%08X' % (struct.unpack_from('<I', d, off)[0] & ~1))")
export CM_PSS_ADDR MGBA_HEADLESS_DEBUGGER=1
echo "  (sweep shim @ $CM_SHIM_ADDR, storage special @ $CM_PSS_ADDR)"

fail=0
run_case() {  # name  CM_ON  CM_CHAR  EXPECT  ENDER  ROM  SHIM
    CM_EXPECT_CHECKS=6 CM_ON=$2 CM_CHAR=$3 EXPECT=$4 ENDER=$5 CM_SHIM_ADDR=$7 \
        CM_SHOT_PREFIX=build/linksweep_$1 \
        timeout 300 "$MGBA" -t "$STATE" --script "$SCRIPT" "$6" \
        > "build/linksweep_$1.log" 2>&1 || true
}
ROM=build/lazarus_cm_pctest.gba
for c in "red 1 1 box1 wired" "misty 1 10 box0 wired" "off 0 1 none wired" \
         "red_wireless 1 1 box1 wireless" "misty_wireless 1 10 box0 wireless"; do
    set -- $c
    run_case "$1" "$2" "$3" "$4" "$5" "$ROM" "$CM_SHIM_ADDR"
    if grep -aq "HARNESS RESULT: PASS" "build/linksweep_$1.log"; then
        echo "[PASS] link-trade sweep $1 (6 checks)"
    else
        echo "[FAIL] link-trade sweep $1 (see build/linksweep_$1.log)"
        grep -a "HARNESS" "build/linksweep_$1.log" | tail -8; fail=1
    fi
done
for e in wired wireless; do
    run_case "nosweep_$e" 1 1 box1 "$e" build/lazarus_cm_pctest_nolinksweep.gba 0
    if grep -aq "HARNESS RESULT: FAIL" "build/linksweep_nosweep_$e.log" \
       && grep -aq "FAIL Poliwag (off the roster) left the party" "build/linksweep_nosweep_$e.log"; then
        echo "[PASS] link-trade sweep NEGATIVE CONTROL $e (hook absent -> Poliwag stays)"
    else
        echo "[FAIL] negative control $e did not fail, or failed for another reason (see build/linksweep_nosweep_$e.log)"
        fail=1
    fi
done
exit $fail
