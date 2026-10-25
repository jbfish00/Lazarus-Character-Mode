#!/usr/bin/env python3
"""Build TEST-ONLY ROMs for the live relearner layer (QoL 2026-10-17: the relearner also teaches egg moves).

The University desk (8,8) (savestate cm_red_active.ss; build_egg_testrom.py's interaction point) is repointed at
    special ChooseMonForMoveRelearner (0xDE) ; waitstate ; releaseall ; end
so the REAL party-menu path runs: picking the lead sets VAR_0x8005 = GetNumberOfRelearnableMoves(lead), which the
shipped ROM answers through CM_NumRelearnable (level-up list + egg moves). --control builds the same from a
CM_NO_EGGRELEARN injector run (the vanilla count); --anylevel-control (QoL A2, 2026-10-24) from a CM_NO_ANYLEVEL run (the
level cut kept: egg moves only). The shipping ROM and BPS are restored afterwards. Never distributed.
"""
import os, struct, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESK_BG_PTR_OFF = 0xEA28AC
TEST_SCRIPT_ADDR = 0x09700100        # next to build_egg_testrom.py's 0x09700000
SCRIPT = bytes([0x25, 0xDE, 0x00, 0x27, 0x6B, 0x02])


def main():
    control = "--control" in sys.argv
    lvctl = "--anylevel-control" in sys.argv
    noegg = "--noegg" in sys.argv          # QoL A2: the level-up part alone (CM_TEST_NO_EGG), with or without the level cut
    src = ROOT / "build" / "lazarus_cm.gba"
    env = {}
    if control:
        env["CM_NO_EGGRELEARN"] = "1"
    if lvctl:
        env["CM_NO_ANYLEVEL"] = "1"
    if noegg:
        env["CM_TEST_NO_EGG"] = "1"
    if env:
        keep = {f: f.read_bytes() for f in (src, src.with_suffix(".bps")) if f.exists()}
        subprocess.run([sys.executable, str(ROOT / "tools" / "inject_character_mode.py")], check=True, cwd=ROOT,
                       env=dict(os.environ, **env), stdout=subprocess.DEVNULL)
        d = bytearray(src.read_bytes())
        # the control injection also rewrote the ELF/symbols/report in build/: rebuild the shipping set so later checks
        # never read the control's (verify_artifacts did once, 2026-10-24); then the ROM + BPS bytes are restored as before
        subprocess.run([sys.executable, str(ROOT / "tools" / "inject_character_mode.py")], check=True, cwd=ROOT,
                       stdout=subprocess.DEVNULL)
        for f, b in keep.items():
            f.write_bytes(b)
    else:
        d = bytearray(src.read_bytes())
    off = TEST_SCRIPT_ADDR - 0x08000000
    assert all(b == 0xFF for b in d[off:off + len(SCRIPT) + 8]), "test-script space not clear"
    d[off:off + len(SCRIPT)] = SCRIPT
    struct.pack_into("<I", d, DESK_BG_PTR_OFF, TEST_SCRIPT_ADDR)
    tag = "_ctl" if control else ""
    tag += ("_noegg" if noegg else "") + ("_lv" if lvctl else "")
    out = ROOT / "build" / ("lazarus_cm_reltest%s.gba" % tag)
    out.write_bytes(bytes(d))
    print("test ROM:", out.name, env or "")


if __name__ == "__main__":
    main()
