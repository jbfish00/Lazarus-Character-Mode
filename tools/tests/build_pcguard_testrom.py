#!/usr/bin/env python3
"""The PC second guard's NEGATIVE-CONTROL ROM (test-only, never shipped).

The guard's live layer (tools/mgba_scripts/cm_pc_guard_test.lua) reuses the
PC-exit test ROM unchanged: build_pc_testrom.py's desk script already builds
the fixture the guard needs -- giveegg + an INLINE hatch, so the party is
[savestate mon, an alive hatchling] -- and then opens the SHIPPED storage
system. This writes the same ROM with the guard removed: the six retargeted
BLs and CanShiftMon's tail restored to the BASE ROM's bytes. The layer must
FAIL on it (the deposit goes through).

Usage: python3 tools/tests/build_pcguard_testrom.py
Reads build/lazarus_cm_pctest.gba (run build_pc_testrom.py first).
Writes build/lazarus_cm_pctest_noguard.gba.
"""
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PCTEST = ROOT / "build" / "lazarus_cm_pctest.gba"
BASE = ROOT / "rom" / "lazarus-v2.gba"
OUT = ROOT / "build" / "lazarus_cm_pctest_noguard.gba"

_INJ = (ROOT / "tools" / "inject_character_mode.py").read_text()


def _inj(name):
    return int(re.search(rf"^{name}\s*=\s*(0x[0-9A-Fa-f]+)", _INJ, re.M).group(1), 16)


def main():
    body = re.search(r"^PSS_GUARD_BL_SITES\s*=\s*\(([^)]*)\)", _INJ, re.M).group(1)
    sites = tuple(int(x, 16) for x in re.findall(r"0x[0-9A-Fa-f]+", body))
    sites += (_inj("PSS_CANSHIFT_BL"), _inj("PSS_CANSHIFT_TAIL"))
    d = bytearray(PCTEST.read_bytes())
    base = BASE.read_bytes()
    changed = 0
    for s in sites:
        if d[s:s + 4] != base[s:s + 4]:
            changed += 1
        d[s:s + 4] = base[s:s + 4]
    assert changed == len(sites), (
        f"only {changed}/{len(sites)} guard sites differed from the base -- "
        "is the guard in build/lazarus_cm_pctest.gba at all?")
    OUT.write_bytes(bytes(d))
    print(f"NEGATIVE CONTROL: {OUT.name}: {changed} guard sites restored to the "
          "base ROM -- the guard is absent here. Never distributed.")


if __name__ == "__main__":
    main()
