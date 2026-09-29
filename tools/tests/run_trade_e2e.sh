#!/bin/sh
# Live trade-gate e2e: builds a TEST-ONLY ROM variant (desk (8,8) BG event
# repointed to the in-game-trade script 0x082B6182 = sIngameTrades index 2)
# and runs tools/mgba_scripts/cm_trade_test.lua both ways. The shipped
# artifacts are never modified. Exit 0 = both runs PASS.
set -e
cd "$(dirname "$0")/../.."

MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
TESTROM=build/lazarus_cm_tradetest.gba

python3 - <<'EOF'
import struct, shutil
shutil.copy("build/lazarus_cm.gba", "build/lazarus_cm_tradetest.gba")
d = bytearray(open("build/lazarus_cm_tradetest.gba", "rb").read())
old = struct.unpack_from("<I", d, 0xEA28AC)[0]
# Since 2026-09-27 the desk lands on the roster display's pre-entry, whose
# first op is `checkflag 0x2B0; goto_if unset, 0x083287A7` (the stock script).
o = old - 0x08000000
assert (d[o:o + 5] == bytes([0x2B, 0xB0, 0x02, 0x06, 0x00])
        and struct.unpack_from("<I", d, o + 5)[0] == 0x083287A7), \
    f"desk (8,8) BG ptr {old:#x} is not the roster pre-entry for 0x083287A7"
struct.pack_into("<I", d, 0xEA28AC, 0x082B6182)
open("build/lazarus_cm_tradetest.gba", "wb").write(bytes(d))
print("test ROM: desk (8,8) -> trade script (never shipped)")
EOF

fail=0
for mode in true false; do
    echo "return {cm_on=$mode}" > build/cm_trade_mode.lua
    log=build/trade_e2e_$mode.log
    timeout 110 "$MGBA" -t tools/savestates/cm_red_active.ss \
        --script tools/mgba_scripts/cm_trade_test.lua "$TESTROM" > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: PASS" "$log"; then
        echo "[PASS] trade e2e cm_on=$mode"
    else
        echo "[FAIL] trade e2e cm_on=$mode (see $log)"
        grep -a "HARNESS" "$log" | tail -8
        fail=1
    fi
done
exit $fail
