#!/usr/bin/env python3
"""Build a TEST-ONLY ROM variant for the LIVE PC-exit e2e (never shipped).

WHY THIS EXISTS. ../game_plans/rowe_parity.md §13.33 item 1: the PC-exit hook
shipped in all four GBA games on STATIC evidence alone. Seaglass got the first
live layer on 2026-09-10; this is the port. §13.20 is why it matters -- four
live layers in three repos were once found dead behind a fully green static
suite, and a hook with no live layer is the same class of claim.

Reach is the obstacle, and the answer is the one run_trade_e2e.sh and
build_egg_testrom.py already use: repoint the one interaction point we hold a
savestate for (the University desk at (8,8)) at a tiny test entry script:

    giveegg <species>          ; becomes the MON UNDER TEST when it hatches
    setvar  0x8004, <slot>     ; the party index EggHatch reads
    <the hatch script's own prefix, copied out of this ROM>
    special <EggHatch> ; waitstate
    goto    0x08326A28         ; == EventScript_AccessPokemonStorage's spliced tail

⭐ Everything after that `goto` is shipped, unmodified bytes: the overlay, the
replayed `special 0x3F` + `waitstate` that opens the storage system and waits
for the player to close it, and the `callnative CM_SweepPartyToPCNative` that
runs when it does. build/lazarus_cm.gba is never touched.

⚠️ WHY THE HATCH IS INLINE RATHER THAN A `goto` INTO THE HATCH SCRIPT. That
script ends in `releaseall; end`, so there is no way to reach the PC after it --
and going through it would ALSO fire the EGG hook's sweep, which would box the
mon before the PC ever opened and leave this layer testing the wrong hook. The
hatch is FIXTURE here: its prefix is copied verbatim out of this ROM at build
time rather than hardcoded, so the fixture cannot drift from the script it
imitates, and the `special`/`waitstate` pair is rebuilt from egg_hook's own
constant. The egg hook's splice is left completely alone.

⚠️ WHY AN EGG AT ALL. It is the only way to get an OFF-ROSTER mon into the party:
an off-roster gift is routed to the PC on the way in by the gift gate, while
eggs are exempt everywhere by design and what hatches out of one was never
checked on the way in. ⭐ The savestate's own party mon then serves as the
never-empty anchor -- without SOME keeper the sweep would keep the hatchling for
every character and the layer would discriminate nothing. (Radical Red has to
supply that anchor itself with a second egg; its checkpoint predates the
starter.)

⚠️ ONLY SITE 0 IS EXERCISED. This ROM has two PC access scripts
(EventScript_AccessPokemonStorage and EventScript_AccessPokemonBoxLink); the
static checks cover both in both directions, and the negative test's CROSS-WIRE
case covers their rejoins. This layer walks the first.

Usage: python3 tools/tests/build_pc_testrom.py <species> [slot] [--no-hook]
Writes build/lazarus_cm_pctest.gba (or ..._pctest_nohook.gba).

`--no-hook` reverts BOTH PC splices to their stock tails in the test ROM only.
That is the live layer's NEGATIVE CONTROL: cm_pc_exit_test.lua must FAIL on it.
Without it the layer proves the sweep works when it is called and says nothing
about whether CLOSING THE PC calls it -- which is the entire claim.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHIPPED = ROOT / "build" / "lazarus_cm.gba"
TESTROM = ROOT / "build" / "lazarus_cm_pctest.gba"

DESK_BG_PTR_OFF  = 0xEA28AC          # University desk (8,8) BG event script ptr
DESK_ORIG_SCRIPT = 0x083287A7        # its shipped target (run_trade_e2e.sh)
# Free space past every injected region, and one page clear of the egg e2e's
# 0x09700000 so both test ROMs can be built from one tree without one silently
# overwriting the other's entry.
TEST_SCRIPT_ADDR = 0x09701000

OP_GIVEEGG   = 0x7A
OP_SETVAR    = 0x16
OP_GOTO      = 0x05
OP_SPECIAL   = 0x25
OP_WAITSTATE = 0x27
VAR_0x8004   = 0x8004


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_hook = "--no-hook" in sys.argv
    if not argv:
        sys.exit("usage: build_pc_testrom.py <species> [slot] [--no-hook]")
    species = int(argv[0], 0)
    slot = int(argv[1], 0) if len(argv) > 1 else 1
    assert 0 < species < 0x4000, "species must be a literal id, not a var ref"
    assert 0 <= slot < 6, "slot must be a party index"

    sys.path.insert(0, str(ROOT / "tools" / "character_mode"))
    import egg_hook
    import pc_hook

    d = bytearray(SHIPPED.read_bytes())

    cur = struct.unpack_from("<I", d, DESK_BG_PTR_OFF)[0]
    assert cur == DESK_ORIG_SCRIPT, \
        f"desk BG ptr drifted: {cur:#x} != {DESK_ORIG_SCRIPT:#x}"

    # The whole point of this ROM is to run the SHIPPED PC hook. If the splice
    # is not in place the run would exercise the stock tail and report a green
    # "the mon stayed in the party" for the control cases while proving nothing.
    site_rom, site_off, site_orig = (pc_hook.SITES[0][0], pc_hook.SITES[0][1],
                                     pc_hook.SITES[0][2])
    spliced = bytes(d[site_off:site_off + len(site_orig)])
    assert spliced[0] == OP_GOTO, (
        "the PC splice is NOT in this build (%s) -- run the injector first"
        % spliced.hex(" "))
    tail = struct.unpack_from("<I", spliced, 1)[0]
    assert 0x08000000 <= tail < 0x0A000000, f"splice goto operand looks wrong: {tail:#x}"

    # The hatch script's prefix -- from its entry up to (not including) the
    # bytes the EGG hook overlays, so these are stock bytes even in a hooked
    # build.
    pre_lo = egg_hook.SCRIPT_ENTRY - 0x08000000
    pre_hi = egg_hook.SPLICE_FILE_OFF
    assert pre_lo < pre_hi, "hatch script entry is not before its splice site"
    hatch_prefix = bytes(d[pre_lo:pre_hi])
    assert hatch_prefix[0] == 0x69, (
        "hatch script does not start with lockall (%s)" % hatch_prefix[:1].hex())

    off = TEST_SCRIPT_ADDR - 0x08000000
    script = (bytes([OP_GIVEEGG]) + struct.pack("<H", species)
              + bytes([OP_SETVAR]) + struct.pack("<HH", VAR_0x8004, slot)
              + hatch_prefix
              + bytes([OP_SPECIAL]) + struct.pack("<H", egg_hook.SPECIAL_HATCH)
              + bytes([OP_WAITSTATE])
              + bytes([OP_GOTO]) + struct.pack("<I", site_rom))
    assert all(b == 0xFF for b in d[off:off + len(script) + 8]), \
        "test-script free space not clear"
    d[off:off + len(script)] = script

    struct.pack_into("<I", d, DESK_BG_PTR_OFF, TEST_SCRIPT_ADDR)

    out = TESTROM
    if no_hook:
        # BOTH sites, not just the one this layer walks: reverting only site 0
        # would leave a build that still differs from "the hook is absent" in a
        # way nothing here would notice.
        for _r, _o, _orig, _txt in pc_hook.SITES:
            d[_o:_o + len(_orig)] = _orig
        out = TESTROM.with_name(TESTROM.stem + "_nohook" + TESTROM.suffix)
        print("NEGATIVE CONTROL: both PC splices reverted to their stock tails "
              "-- the hook is absent here.")

    out.write_bytes(bytes(d))
    print(f"test ROM: {out.name}: desk -> giveegg {species} (slot {slot}), "
          f"inline hatch, goto PC script {site_rom:#x} "
          + ("(STOCK tail -- no sweep)" if no_hook else f"(spliced -> tail {tail:#x})")
          + f"; script {len(script)} B @ {TEST_SCRIPT_ADDR:#x}. Never distributed.")


if __name__ == "__main__":
    main()
