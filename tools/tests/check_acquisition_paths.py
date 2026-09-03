#!/usr/bin/env python3
"""INVENTORY every routine in this ROM that writes gPlayerPartyCount.

⭐ WHY THIS EXISTS, and why it is an inventory rather than a grep.

The workspace's lesson #1 (CLAUDE.md, from Platinum): *a checker that greps the
files which ALREADY contain a hook cannot see a bypass in a file with no hook.*
Platinum's acquisition inventory enumerated `Party_AddPokemon*` repo-wide and
still could not see the link trade or the GTS, because a trade fills the slot
its partner vacated and adds nothing. The fix there was not "search more files"
but "choose a different PRIMITIVE to count".

For a GBA binary hack the primitive that cannot be dodged is the one every
acquisition must eventually touch: **the party count byte itself**. A routine
that hands the player a Pokemon has to increment gPlayerPartyCount, whatever
route it took to get there. So this enumerates every instruction in the ROM
that STORES through a pointer to that byte, and requires each one to carry a
verdict below. A new acquisition path is then a failing check rather than a
silent arrival.

✅ THE METHOD IS VALIDATED ON A KNOWN POSITIVE. Run against Seaglass, it
rediscovers both that game's enforcement choke point AND the give-core bypass
its own ROUTINE_MAP documents as "never BLs GiveMonToPlayer -> bypasses the
injected CM gate" -- a path a caller-of-GiveMonToPlayer scan cannot see, and
the exact shape of the Platinum miss.

⚠️ WHAT THIS DOES AND DOES NOT PROVE. It proves the SET of party-count writers
has not changed. It does NOT prove each one is correctly gated -- that is what
the verdicts record, and several are still UNVERIFIED (they are writers whose
containing routine has not been reverse-engineered here). An UNVERIFIED entry
is a "go look", not a clean bill of health. Recording an absence of
investigation as a negative result is a mistake this workspace has made at
least four times.

Detection: Thumb `ldr rX,[pc,#imm]` puts its literal at ((pc+4) & ~3) + imm*4,
so the loads of a given pool word are found exactly rather than by proximity;
then a store THROUGH that register within the following instructions is a
write. Conservative: it reports WRITE only when it can see the store.

Run:  python3 tools/tests/check_acquisition_paths.py   (0 = ok, 1 = changed)
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from cm_tally import assert_tally          # noqa: E402

GAME = "Pokémon Lazarus v2.0"
ROM = os.path.join(ROOT, 'rom/lazarus-v2.gba')
PARTY_COUNT = 0x0201b95d

# How many checks this layer must run. A deliberate LITERAL -- see cm_tally.py.
EXPECT_CHECKS = 4

# Measured, reachable, and covered by NO gate. A second one must fail check 4.
EXPECT_UNGATED = frozenset({0x0020ddb8})

# ldr site -> (verdict, why). Every writer the scan finds must be listed here.
#   GATED      the project's enforcement covers this path
#   EXEMPT     deliberately not gated, with a reason
#   UNVERIFIED found by the scan, containing routine not yet identified
INVENTORY = {
    0x001542ca: ("EXEMPT",
                 "SAVE/RESTORE, not a write: `ldrb r7,[r4]` snapshots "
                 "gPlayerPartyCount at 0x081542CC and `strb r7,[r4]` writes "
                 "the SAME value back at 0x081542E0, across four subsystem "
                 "calls. Value-preserving by construction"),
    0x0016ebec: ("EXEMPT",
                 "LoadPlayerParty-equivalent: gPlayerPartyCount = "
                 "gSaveBlock1Ptr->[0x238], then a 100-byte-stride copy loop "
                 "restores the party. Restores the player's OWN saved "
                 "party; everything in it was gated when first acquired"),
    0x0018977e: ("EXEMPT",
                 "new-game reset: `strb r6,[r3]` with r6 = 0, amid the init "
                 "BL run (0x081D4ACC / 0x081D4B20 / 0x081C0A38 ...). "
                 "Zeroing removes, never adds"),
    0x001c4118: ("GATED",
                 "inside GiveMonToPlayer 0x081C40BC -- the injected enforcement point (docs/ROUTINE_MAP.md:158)"),
    0x001c422a: ("EXEMPT",
                 "CalculatePlayerPartyCount (40 BL callers -- the engine's "
                 "recount primitive): count = 6 if all six slots are "
                 "filled, else the index of the first empty one. A RECOUNT. "
                 "See the LAUNDERING note in docs/PARTY_COUNT_WRITERS.md"),
    0x001c429e: ("EXEMPT",
                 "second recount arm in the same region: `strb r4,[r7]` "
                 "where r4 is the first-empty-slot index from the loop "
                 "immediately above"),
    0x001c430a: ("EXEMPT",
                 "third recount arm, the early-exit branch of the loop at "
                 "0x001C429E (`strb r4,[r7]`, r4 = the index the loop broke "
                 "at)"),
    0x001d830a: ("EXEMPT",
                 "gPlayerPartyCount = CalculatePlayerPartyCount() -- `bl "
                 "0x081C420C; ldr r3,=count; strb r0,[r3]`. A recount"),
    0x001d84ba: ("EXEMPT",
                 "the same recount as 0x001D830A in the sibling routine; "
                 "these two are the +0x1B0 pair the plan predicted, "
                 "confirmed here by opcode stream"),
    0x0020db60: ("GATED",
                 "in the ScriptGiveMon 0x0820D3F4 give region; the 112 callnative give sites are retargeted to the wrapper and verify_artifacts.py check [8] pins them"),
    0x0020ddb8: ("UNGATED",
                 "UNGATED, CONFIRMED REACHABLE, NOW MITIGATED. Lazarus's "
                 "own 9-starter picker: thumb ptr 0x08239DB8 installs task "
                 "fn 0x08239C08, which BLs 0x08239348 (its entry -- the "
                 "`movs r0,#134` is hoisted above the push, so a "
                 "nearest-push scan lands 2 bytes late), which reads a "
                 "36-byte record from the table at 0x08E55FE8 and BLs the "
                 "parameterised give 0x0820DBB4 at 0x082393BA. The 9 clean "
                 "records are Chespin, Fennekin, Froakie, Rowlet, Litten, "
                 "Popplio, Sprigatito, Fuecoco and Quaxly, all level 5, and "
                 "docs/INTRO_NAVIGATION.md's have_starter.ss fixture is a "
                 "level-5 Popplio, entry [0]. THE VERDICT STAYS UNGATED "
                 "because the give itself still is: no gate covers this "
                 "call. What changed on 2026-09-02 is the CONSEQUENCE. The "
                 "picker can only run BEFORE Character Mode is activated at "
                 "the code-entry NPC, and the confirm script now calls "
                 "CM_SweepPartyToPCNative immediately after granting the "
                 "character's own starter, which boxes the picker's mon. "
                 "Ordering is load-bearing and is asserted positionally by "
                 "verify_artifacts.py; shim_unit_test.py drives the sweep "
                 "in the emulator with a synthetic party, including the "
                 "case that shows a sweep BEFORE the give would box "
                 "nothing. If a future edit ever made this picker reachable "
                 "while the mode is already on, the hole would be live "
                 "again"),
    0x0023a698: ("NOT-A-WRITER",
                 "FALSE POSITIVE -- not a writer. `ldr r3,=count; ldrb "
                 "r3,[r3]; cmp r3,#0` is an is-the-party-empty READ that "
                 "immediately clobbers r3. The detector matched `strb "
                 "r1,[r3,#5]` at 0x0823A6F0, which stores through the "
                 "reloaded r3 at a +5 offset. Same detector defect as "
                 "Radical Red's 0x0012092A"),
}

WINDOW = 60          # instructions to follow after the ldr


def thumb(b, i):
    return struct.unpack_from("<H", b, i)[0]


def writers(b):
    """{ldr file offset: pool offset} for every store through gPlayerPartyCount."""
    pools = []
    p = struct.pack("<I", PARTY_COUNT)
    i = b.find(p)
    while i >= 0:
        if i % 4 == 0:
            pools.append(i)
        i = b.find(p, i + 1)

    found = {}
    for pool in pools:
        for i in range(max(0, pool - 1024), pool, 2):
            w = thumb(b, i)
            if (w & 0xF800) != 0x4800:            # ldr rX,[pc,#imm8]
                continue
            rX, imm = (w >> 8) & 7, w & 0xFF
            if (((i + 4) & ~3) + imm * 4) != pool:
                continue
            for k in range(i + 2, min(i + 2 + WINDOW * 2, len(b) - 1), 2):
                v = thumb(b, k)
                if (v & 0xF800) == 0x7000 and ((v >> 3) & 7) == rX:
                    found[i] = pool; break        # strb rY,[rX,#imm]
                if (v & 0xFE00) == 0x5400 and ((v >> 3) & 7) == rX:
                    found[i] = pool; break        # strb rY,[rX,rZ]
                if (v & 0xF800) == 0x6000 and ((v >> 3) & 7) == rX:
                    found[i] = pool; break        # str  rY,[rX,#imm]
                if (v & 0xF800) == 0x4800 and ((v >> 8) & 7) == rX:
                    break                         # rX reloaded: not ours
                if (v & 0xFF00) in (0x4700, 0xBD00):
                    break                         # bx / pop {..,pc}
    return found


failures = []
checks_run = 0


def check(name, ok, detail=""):
    global checks_run
    checks_run += 1
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                           (" -- " + detail) if detail and not ok else ""))
    if not ok:
        failures.append(name)


def main():
    if not os.path.isfile(ROM):
        print("base ROM not found: %s" % os.path.relpath(ROM, ROOT))
        return 1
    with open(ROM, "rb") as f:
        b = f.read()

    found = writers(b)
    rom_addr = {off: 0x08000000 + off for off in found}

    print("%s -- gPlayerPartyCount %#010x" % (GAME, PARTY_COUNT))
    print("  %d writer site(s) found, %d inventoried\n"
          % (len(found), len(INVENTORY)))

    # 1. nothing new arrived
    new = sorted(set(found) - set(INVENTORY))
    check("every party-count writer in the ROM is inventoried",
          not new,
          ", ".join("%#010x" % rom_addr[o] for o in new)
          + " -- a routine that writes the party count and is not on the list "
            "is a possible ungated acquisition path; identify it, then add it "
            "with a verdict")

    # 2. nothing inventoried vanished (the inventory is not describing a
    #    ROM that no longer exists)
    gone = sorted(set(INVENTORY) - set(found))
    check("every inventoried writer is still present in the ROM",
          not gone,
          ", ".join("%#010x" % (0x08000000 + o) for o in gone))

    # 3. the enforcement choke point is actually among the writers -- an
    #    inventory that lists no GATED path would be describing a ROM with no
    #    enforcement at all, and would still pass checks 1 and 2.
    gated = [o for o in INVENTORY if INVENTORY[o][0] == "GATED" and o in found]
    check("at least one GATED writer is present (the enforcement point)",
          bool(gated), "no GATED writer found among %d" % len(found))

    # 4. no NEW ungated acquisition path. UNGATED means measured, reachable and
    #    NOT covered by any gate -- a known hole, pinned here so that finding a
    #    SECOND one fails the suite instead of arriving silently. Pinning it
    #    rather than failing on its existence is deliberate: the suite must stay
    #    green while a recorded, understood hole waits on a design decision,
    #    or it becomes a red checker nobody runs.
    ungated = frozenset(o for o in INVENTORY if INVENTORY[o][0] == "UNGATED")
    check("the set of UNGATED acquisition paths is exactly the known one",
          ungated == EXPECT_UNGATED,
          "new: %s | disappeared: %s"
          % (", ".join("%#010x" % (0x08000000 + o)
                       for o in sorted(ungated - EXPECT_UNGATED)) or "none",
             ", ".join("%#010x" % (0x08000000 + o)
                       for o in sorted(EXPECT_UNGATED - ungated)) or "none"))
    if ungated:
        print("  🔴 %d UNGATED path(s) -- reachable and covered by no gate:"
              % len(ungated))
        for o in sorted(ungated):
            print("       %#010x" % (0x08000000 + o))

    unver = sorted(o for o in INVENTORY if INVENTORY[o][0] == "UNVERIFIED")
    print("\n  verdicts: %d GATED, %d EXEMPT, %d NOT-A-WRITER, %d UNGATED, "
          "%d UNVERIFIED"
          % (sum(1 for v in INVENTORY.values() if v[0] == "GATED"),
             sum(1 for v in INVENTORY.values() if v[0] == "EXEMPT"),
             sum(1 for v in INVENTORY.values() if v[0] == "NOT-A-WRITER"),
             len(ungated), len(unver)))
    print("  NOT-A-WRITER: the scan reports these, and reverse engineering "
          "showed they are\n    reads, not stores. They stay listed on "
          "purpose -- the detector is deliberately\n    conservative, so "
          "dropping them would make check 2 fail. See\n    "
          "docs/PARTY_COUNT_WRITERS.md for the detector defect that "
          "produces them.")
    if unver:
        print("  ⚠️ UNVERIFIED means the containing routine has not been "
              "identified here. It is a 'go look', not a clean bill of health:")
        for o in unver:
            print("       %#010x" % (0x08000000 + o))

    if assert_tally(checks_run, EXPECT_CHECKS, "check_acquisition_paths"):
        return 1
    print("\n%s" % ("ALL PASS" if not failures
                     else "FAILURES: " + ", ".join(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
