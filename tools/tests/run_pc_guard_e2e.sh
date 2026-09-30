#!/bin/sh
# LIVE e2e for the PC second guard (ROWE's IsRemovingLastAllowedPartyMon;
# src/character_mode.c CM_PSSLastMonGuard; verify_artifacts section 17).
#
# Reuses the PC-exit test ROM: its desk script gives an egg, hatches it INLINE
# and opens the SHIPPED storage system, so the party is [Pikachu (savestate),
# alive Poliwag]. The layer deposits slot 0. ⭐ With an alive Poliwag beside it
# VANILLA ALLOWS that deposit, so only the guard can refuse -- and only for a
# character who has Pikachu but not Poliwag (Red). The swap is asserted
# (slot 0's personality), while the PC is still open.
#   red   char 1  -> refused  ("That's your last Pokemon!")
#   misty char 10 -> deposited (Pikachu is off her roster: discrimination)
#   off           -> deposited (control)
#   noguard ROM   -> the layer must FAIL on the deposit (negative control)
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
STATE=tools/savestates/cm_red_active.ss
SCRIPT=tools/mgba_scripts/cm_pc_guard_test.lua

python3 tools/tests/build_pc_testrom.py 60 1 >/dev/null
python3 tools/tests/build_pcguard_testrom.py >/dev/null

CM_GUARD_ADDR=$(arm-none-eabi-nm build/character_mode.elf \
    | awk '/ T CM_PSSLastMonGuard$/{printf "0x%s\n", toupper($1)}')
[ -n "$CM_GUARD_ADDR" ] || { echo "[FAIL] locating CM_PSSLastMonGuard"; exit 1; }
CM_PSS_ADDR=$(python3 -c "
import sys, struct
sys.path.insert(0, 'tools/character_mode')
import pc_hook
d = open('build/lazarus_cm.gba','rb').read()
off = pc_hook.SPECIALS_TABLE_ADDR - 0x08000000 + pc_hook.SPECIAL_PC * 4
print('0x%08X' % (struct.unpack_from('<I', d, off)[0] & ~1))")
export CM_GUARD_ADDR CM_PSS_ADDR MGBA_HEADLESS_DEBUGGER=1
echo "  (guard @ $CM_GUARD_ADDR, storage special @ $CM_PSS_ADDR)"

fail=0
guard_case() {  # name  cfg  checks  rom
    echo "$2" > build/cm_pc_mode.lua
    log=build/pcguard_$1.log
    CM_EXPECT_CHECKS=$3 timeout 300 "$MGBA" -t "$STATE" --script "$SCRIPT" "$4" \
        > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: PASS" "$log"; then
        echo "[PASS] PC guard $1 ($3 checks)"
    else
        echo "[FAIL] PC guard $1 (see $log)"; grep -a "HARNESS" "$log" | tail -8
        fail=1
    fi
}
ROM=build/lazarus_cm_pctest.gba
guard_case red   'return {cm_on=true, char=1, expect="refused", name="red"}'       4 "$ROM"
guard_case misty 'return {cm_on=true, char=10, expect="deposited", name="misty"}'  3 "$ROM"
guard_case off   'return {cm_on=false, expect="deposited", name="off"}'            3 "$ROM"

echo 'return {cm_on=true, char=1, expect="refused", name="noguard"}' > build/cm_pc_mode.lua
log=build/pcguard_noguard.log
timeout 300 "$MGBA" -t "$STATE" --script "$SCRIPT" \
    build/lazarus_cm_pctest_noguard.gba > "$log" 2>&1 || true
if grep -aq "HARNESS RESULT: FAIL" "$log" \
   && grep -aq "FAIL slot 0 (the last on-roster mon) is still in the party" "$log"; then
    echo "[PASS] PC guard NEGATIVE CONTROL (guard absent -> the deposit goes through)"
else
    echo "[FAIL] negative control did not fail, or failed for another reason (see $log)"
    fail=1
fi
exit $fail
