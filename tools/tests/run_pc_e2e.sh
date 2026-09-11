#!/bin/sh
# LIVE PC-exit e2e (../game_plans/rowe_parity.md §13.33 item 1).
#
# The PC-exit hook shipped in all four GBA games on STATIC evidence alone.
# Seaglass got the first live layer on 2026-09-10; this is the port. §13.20 is
# why it matters: four live layers in three repos were once found dead behind a
# fully green static suite, and a hook with no live layer is the same claim.
#
# tools/tests/build_pc_testrom.py repoints the University desk (8,8) at
#   giveegg 60 ; setvar 0x8004,1 ; <inline hatch> ; goto 0x08326A28
# and everything after that goto is SHIPPED. Poliwag 60 is the egg layer's own
# discriminator -- ON Misty's roster, OFF Red's -- so one species covers all
# three positive cases. The hatch is FIXTURE: it is the only way to get an
# off-roster mon INTO the party, since the gift gate boxes an off-roster gift on
# the way in and eggs are exempt everywhere. The savestate's own party mon is
# the never-empty anchor.
#
# ⚠️ Only SITE 0 (EventScript_AccessPokemonStorage) is walked. Both sites are
# pinned statically in both directions, and the negative test's CROSS-WIRE case
# covers their rejoins.
#
# Four runs, and the fourth is the point: with both PC splices reverted the same
# run must FAIL. Exit 0 = all four behaved.
set -e
cd "$(dirname "$0")/../.."

MGBA=../Seaglass-Character-Mode/tools/mgba_src/build/mgba-headless
STATE=tools/savestates/cm_red_active.ss
SCRIPT=tools/mgba_scripts/cm_pc_exit_test.lua

[ -f "$MGBA" ] || { echo "SKIP: mgba-headless not found at $MGBA"; exit 0; }

python3 tools/tests/build_pc_testrom.py 60 1
python3 tools/tests/build_pc_testrom.py 60 1 --no-hook

# CM_SweepPartyToPCNative moves on every shim rebuild; a stale literal here
# would report "the PC exit never reached the sweep" on a ROM where it did.
CM_SWEEP_ADDR=$(arm-none-eabi-nm build/character_mode.elf \
    | awk '/ T CM_SweepPartyToPCNative$/{printf "0x%s\n", toupper($1)}')
[ -n "$CM_SWEEP_ADDR" ] || { echo "[FAIL] locating CM_SweepPartyToPCNative"; exit 1; }

# ⭐ The storage system's own handler, read out of the BUILT ROM's gSpecials
# table. Breakpointing it is what turns "the script ran" into "the PC opened":
# a no-op special would release its waitstate at once and the sweep would still
# fire, green, with no PC ever involved. Derived, never hardcoded.
CM_PSS_ADDR=$(python3 -c "
import sys, struct
sys.path.insert(0, 'tools/character_mode')
import pc_hook
d = open('build/lazarus_cm.gba','rb').read()
off = pc_hook.SPECIALS_TABLE_ADDR - 0x08000000 + pc_hook.SPECIAL_PC * 4
print('0x%08X' % (struct.unpack_from('<I', d, off)[0] & ~1))")
[ -n "$CM_PSS_ADDR" ] || { echo "[FAIL] deriving the storage special handler"; exit 1; }
export CM_SWEEP_ADDR CM_PSS_ADDR MGBA_HEADLESS_DEBUGGER=1
echo "  (sweep @ $CM_SWEEP_ADDR, storage special @ $CM_PSS_ADDR)"

fail=0
pc_case() {  # name  cfg  rom
    echo "$2" > build/cm_pc_mode.lua
    log=build/pc_e2e_$1.log
    CM_EXPECT_CHECKS=7 timeout 300 "$MGBA" -t "$STATE" --script "$SCRIPT" "$3" \
        > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: PASS" "$log"; then
        echo "[PASS] PC exit $1 (7 checks)"
    else
        echo "[FAIL] PC exit $1 (see $log)"; grep -a "HARNESS" "$log" | tail -8
        fail=1
    fi
}
PCROM=build/lazarus_cm_pctest.gba
pc_case red   'return {cm_on=true, char=1, expect="box", name="red"}'      "$PCROM"
pc_case misty 'return {cm_on=true, char=10, expect="party", name="misty"}' "$PCROM"
pc_case off   'return {cm_on=false, expect="party", name="off"}'           "$PCROM"

# ⭐ The negative control. No CM_EXPECT_CHECKS: the run must die on the missing
# sweep, not on a tally mismatch, or a future harness change could keep this
# "failing" for the wrong reason and the layer would stop discriminating.
echo 'return {cm_on=true, char=1, expect="box", name="nohook"}' > build/cm_pc_mode.lua
log=build/pc_e2e_nohook.log
timeout 300 "$MGBA" -t "$STATE" --script "$SCRIPT" \
    build/lazarus_cm_pctest_nohook.gba > "$log" 2>&1 || true
if grep -aq "HARNESS RESULT: FAIL" "$log" \
   && grep -aq "reached the shipped sweep (timeout)" "$log"; then
    echo "[PASS] PC exit NEGATIVE CONTROL (hook absent -> layer fails)"
else
    echo "[FAIL] negative control did not fail, or failed for another reason (see $log)"
    fail=1
fi
exit $fail
