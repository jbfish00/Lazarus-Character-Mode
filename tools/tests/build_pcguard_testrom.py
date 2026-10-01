#!/usr/bin/env python3
"""The PC second guard's NEGATIVE-CONTROL ROM (test-only, never shipped).

The guard's live layer (tools/mgba_scripts/cm_pc_guard_test.lua) reuses the
PC-exit test ROM unchanged: build_pc_testrom.py's desk script already builds
the fixture the guard needs -- giveegg + an INLINE hatch, so the party is
[savestate mon, an alive hatchling] -- and then opens the SHIPPED storage
system. This writes the same ROM with the guard removed: the six retargeted
BLs and CanShiftMon's tail restored to the BASE ROM's bytes. The layer must
FAIL on it (the deposit goes through).

`--no-link-sweep` instead restores only the two link-trade BLs
(LINK_TRADE_BL_SITES): the negative control for the link-trade sweep layer
(tools/mgba_scripts/cm_link_trade_sweep_test.lua), which reuses this fixture.

Usage: python3 tools/tests/build_pcguard_testrom.py [--no-link-sweep]
Reads build/lazarus_cm_pctest.gba (run build_pc_testrom.py first).
Writes build/lazarus_cm_pctest_noguard.gba (or ..._nolinksweep.gba).
"""
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PCTEST = ROOT / "build" / "lazarus_cm_pctest.gba"
BASE = ROOT / "rom" / "lazarus-v2.gba"
OUT = ROOT / "build" / "lazarus_cm_pctest_noguard.gba"

_INJ = (ROOT / "tools" / "inject_character_mode.py").read_text()


def _inj(name):
    return int(re.search(rf"^{name}\s*=\s*(0x[0-9A-Fa-f]+)", _INJ, re.M).group(1), 16)


def main():
    link = "--no-link-sweep" in sys.argv
    key = "LINK_TRADE_BL_SITES" if link else "PSS_GUARD_BL_SITES"
    body = re.search(rf"^{key}\s*=\s*\(([^)]*)\)", _INJ, re.M).group(1)
    sites = tuple(int(x, 16) for x in re.findall(r"0x[0-9A-Fa-f]+", body))
    if not link:
        sites += (_inj("PSS_CANSHIFT_BL"), _inj("PSS_CANSHIFT_TAIL"))
    out = OUT.with_name("lazarus_cm_pctest_nolinksweep.gba") if link else OUT
    d = bytearray(PCTEST.read_bytes())
    base = BASE.read_bytes()
    changed = 0
    for s in sites:
        if d[s:s + 4] != base[s:s + 4]:
            changed += 1
        d[s:s + 4] = base[s:s + 4]
    what = "link-trade sweep" if link else "guard"
    assert changed == len(sites), (
        f"only {changed}/{len(sites)} {what} sites differed from the base -- "
        f"is the {what} in build/lazarus_cm_pctest.gba at all?")
    out.write_bytes(bytes(d))
    print(f"NEGATIVE CONTROL: {out.name}: {changed} {what} sites restored to the "
          f"base ROM -- the {what} is absent here. Never distributed.")


if __name__ == "__main__":
    main()
