#!/bin/bash
# LIVE overworld-sprite layer (2026-10-22, ../game_plans/overworld_sprites.md).
#
# From naming.ss (the code screen open at the Acrisia University desk), each run
# types a real code; the shipped activation script runs and the player's sprite
# follows the character (src/ow_sprite.c). tools/mgba_scripts/cm_ow_sprite_test.lua
# reads the player out of OBJ VRAM and palette RAM against the SOURCE art
# (tools/tests/ow_sprite_env.py) and walks in all four directions.
#
#   MISTY  16x32 sheet
#   LUCAS  32x32 sheet
#   PAUL   GENERATED 16x32 sheet (../game_plans/ow_generated)
#   ETHAN  Lazarus's own Johto Fashion costume (its images table is asserted)
#   ZZZ    refused code: the player stays stock
# and a NEGATIVE CONTROL: a copy with GetObjectEventGraphicsInfo's entry put
# back, typing MISTY, which must FAIL.
set -u
[ -z "${BASH_VERSION:-}" ] && exec bash "$0" "$@"
cd "$(dirname "$0")/../.." || exit 1
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
ROM=build/lazarus_cm.gba
NEG=build/lazarus_cm_ow_neg.gba
SS=tools/savestates/naming.ss
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA (sh tools/build_mgba.sh)"; exit 2; }
[ -f "$ROM" ] && [ -f "$SS" ] || { echo "build first (and have $SS)"; exit 1; }

python3 - <<'PY' || exit 1
import sys
sys.path.insert(0, "tools/character_mode")
import lazarus_ow_player as owp
d = bytearray(open("build/lazarus_cm.gba", "rb").read())
o = owp.R(owp.GET_INFO)
assert d[o:o + 8] != owp.GET_INFO_ORIG, "shipped build has no trampoline"
d[o:o + 8] = owp.GET_INFO_ORIG
open("build/lazarus_cm_ow_neg.gba", "wb").write(bytes(d))
PY

fail=0
run() {  # label name code expect checks rom want
    eval "$(python3 tools/tests/ow_sprite_env.py "$2")" || { echo "  FAIL env $2"; fail=1; return; }
    local log=/tmp/lz_ow_$1.log
    CM_CODE=$3 CM_EXPECT=$4 CM_SHOTS=/tmp/lz_ow_$1 timeout 240 "$MGBA" \
        --script tools/mgba_scripts/cm_ow_sprite_test.lua -t "$SS" "$6" > "$log" 2>&1
    if [ "$7" = PASS ]; then
        if grep -aq "HARNESS PASSED $5, FAILED 0" "$log" && grep -aq "HARNESS RESULT: PASS" "$log"; then
            echo "  PASS overworld sprite $1 ($5 checks, want PASS)"
        else echo "  FAIL overworld sprite $1 (want PASS with $5 checks, see $log)"; grep -a "HARNESS FAIL" "$log" | head -4; fail=1; fi
    else
        if grep -aq "HARNESS RESULT: FAIL" "$log"; then echo "  PASS overworld sprite $1 (want FAIL)"
        else echo "  FAIL overworld sprite $1 (want FAIL, see $log)"; fail=1; fi
    fi
}
run misty Misty misty on 9 "$ROM" PASS
run lucas Lucas lucas on 9 "$ROM" PASS
run paul  Paul  paul  on 9 "$ROM" PASS
run ethan Ethan ethan on 3 "$ROM" PASS
run off   Misty zzz   off 3 "$ROM" PASS
run NEGATIVE_CONTROL_no_hook Misty misty on 9 "$NEG" FAIL
exit $fail
