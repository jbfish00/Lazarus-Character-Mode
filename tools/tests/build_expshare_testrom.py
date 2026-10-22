#!/usr/bin/env python3
"""Build TEST-ONLY ROMs for the live Exp. Share give layer (user, 2026-10-21: early
party-wide Exp. Share with Character Mode OFF too).

Lazarus gives the Exp. Share natively in the pre-gym-1 Rotom Phone scene, for every
player: the scene's script, at 0x08382D5F,

    delay 5 ; additem 461, 1 ; setflag 0x495 ; additem 0x33C, 1 ; ...

(461 = the Exp. Share, flag 0x495 = the switch IsExpShareEnabled 0x080D1270 reads)
checks nothing about Character Mode. Our savestates are all before that scene, so,
as build_relearn_testrom.py does, the University desk (8,8) is repointed at a test
entry that is just `goto 0x08382D5F`: everything that runs is the base game's own
bytes, which this script first asserts are unchanged in build/lazarus_cm.gba.

--control enters the same script just AFTER the setflag (0x08382D6A): the live layer
must FAIL on it (no flag, no item), proving the layer sees the give itself.
Never distributed.
"""
import struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESK_BG_PTR_OFF = 0xEA28AC
TEST_SCRIPT_ADDR = 0x09700200        # beside build_relearn_testrom.py's 0x09700100
GIVE = 0x08382D5F
GIVE_BYTES = bytes.fromhex("280500" "44cd010100" "299504" "443c030100")
AFTER_SETFLAG = GIVE + 11


def goto(a):
    return bytes([0x05]) + struct.pack("<I", a)


def main():
    control = "--control" in sys.argv
    d = bytearray((ROOT / "build" / "lazarus_cm.gba").read_bytes())
    base = (ROOT / "rom" / "lazarus-v2.gba").read_bytes()
    g = GIVE - 0x08000000
    assert base[g:g + len(GIVE_BYTES)] == GIVE_BYTES, "base ROM: the Rotom Phone give moved"
    assert d[g:g + len(GIVE_BYTES)] == GIVE_BYTES, "the CM build changed the Exp. Share give"
    script = goto(AFTER_SETFLAG if control else GIVE)
    off = TEST_SCRIPT_ADDR - 0x08000000
    assert all(b == 0xFF for b in d[off:off + len(script) + 8]), "test-script space not clear"
    d[off:off + len(script)] = script
    struct.pack_into("<I", d, DESK_BG_PTR_OFF, TEST_SCRIPT_ADDR)
    out = ROOT / "build" / ("lazarus_cm_expgive_ctl.gba" if control else "lazarus_cm_expgive.gba")
    out.write_bytes(bytes(d))
    print("test ROM:", out.name, "(control: enters after the setflag)" if control else "")


if __name__ == "__main__":
    main()
