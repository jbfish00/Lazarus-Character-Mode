#!/usr/bin/env python3
"""GDB-driven unit test for the Lazarus Character Mode acquisition gate.

Also covers the wild-encounter roster override (new, 2026-07-17):
CM_CreateWildMonGated(species, level), decoded from the wild trampoline
literal. Observation point is CreateWildMon's own real entry 0x0824AA54 —
the gate always tail-calls it, so whatever (species, level) it's entered
with IS the gate's decision (unchanged input = no override; anything else =
override fired). Runs many trials to check the ~10% rate and confirms every
overridden species is a member of Red's own wildmons.bin table (which is
built exclusively from non-legendary roster bases — see
tools/character_mode/emit_wildmons.py — so this also proves legendary
exclusion without re-deriving LEGENDARY_BASES here).

Runs the REAL CM_GiveMonToPlayerGated code in the REAL emulator (mGBA's GDB
stub), with a synthetic Pokemon struct and a synthetic SaveBlock1, and checks
which branch the shim takes for every case in the decision table.

Lazarus differences from the Radical Red original of this test:
  - Flag 0x2B0 / var 0x40E0 live inside SaveBlock1 (flags +0x12E8, vars
    +0x1414), reached through gSaveBlock1Ptr @ 0x03003664. The test builds a
    zeroed fake SaveBlock1 in scratch EWRAM and points the pointer at it, so
    FlagGet/GetVarPointer read controlled state without booting the game.
  - Branch observation points are the real function entries (stable, pinned
    in docs/ROUTINE_MAP.md), not shim-internal offsets:
        0x081C40BC GiveMonToPlayer  = pass-through path
        0x081C4130 CopyMonToPC      = enforcement path
    Execution stops AT these entries; the deep calls never run.
  - The shim entry address is NOT hardcoded: it is decoded from the shipped
    ROM itself (the trampoline literal at 0x08470A68), so the test exercises
    exactly what the BL patches reach.
  - Species/character ids for the cases are resolved dynamically from
    characters_manifest.json + rosters_expanded.bin + rom_species_table.json.

Mon struct: personality=otId=0 -> xor key 0, substruct order 0
(Growth,Attacks,EVs,Misc) — pokeemerald-expansion keeps the vanilla Emerald
BoxPokemon framing (checksum @28, substructs @32, species Growth+0, isEgg =
IV word bit 30 at Misc+4). MON_DATA_SPECIES=18 was ROM-confirmed against
GiveMonToPlayer's own slot probe. If the layout ever drifts, case 'Red +
off-roster -> PC' fails loudly (a garbage species read parses as bad-egg ->
egg-exempt -> pass-through).

Usage: shim_unit_test.py [rom.gba]   (default build/lazarus_cm.gba)
Starts mgba-qt -g under xvfb-run if there is no DISPLAY. Exit 0 = all pass.
"""
import json
import os
import re

# How many checks this layer must run. A deliberate LITERAL, never a total
# recomputed from the data the checks iterate: such a total drifts in lockstep
# with what it is meant to pin and therefore cannot fail. Bump it in the same
# commit that adds or removes a check. See tools/tests/cm_tally.py.
EXPECT_CHECKS = 34
import struct
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cm_tally import assert_tally  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parent.parent

GIVEMON = 0x081C40BC     # pass-through branch point (function entry)
COPYPC = 0x081C4130      # enforcement branch point (function entry)
TRAMP_LIT_OFF = 0x470A68  # trampoline literal in ROM = gate entry | 1

CREATEWILDMON = 0x0824AA54       # observation point: gate always tail-calls here
WILD_TRAMP_LIT_OFF = 0x470A70    # wild trampoline literal in ROM = wild gate entry | 1
WILDMONS_OFF = 0x15FC000         # WILDMONS_ADDR - 0x08000000

# trade-gate observation: CM_TradeCheck is void and returns; entry decoded
# from the first trade wrapper script's callnative ptr, verdict read from
# gSpecialVar_Result after returning onto the GIVEMON breakpoint
TRADE_WRAPPER_OFF = 0x15FB000   # TRADE_SCRIPT_ADDR - 0x08000000
TRADE_TABLE_OFF = 0xE4D578
TRADE_STRIDE = 60
SPECIAL_VARS_TABLE_OFF = 0x28CB9C  # ROM table of ptrs for vars 0x8000+
SPECIAL_RESULT = 0x0200560C

SB1_PTR = 0x03003664     # gSaveBlock1Ptr
SB1_FAKE = 0x02030000    # scratch EWRAM fake SaveBlock1 (zeroed)
SB1_SIZE = 0x1800
FLAGS_OFF = 0x12E8
VARS_OFF = 0x1414
FLAG_CM = 0x2B0
VAR_CM_CHAR = 0x40E0

FLAG_BYTE = SB1_FAKE + FLAGS_OFF + (FLAG_CM >> 3)
FLAG_MASK = 1 << (FLAG_CM & 7)
VAR_ADDR = SB1_FAKE + VARS_OFF + 2 * (VAR_CM_CHAR - 0x4000)

VAR_CM_STARTER = 0x40E4
STARTER_VAR_ADDR = SB1_FAKE + VARS_OFF + 2 * (VAR_CM_STARTER - 0x4000)
CODE_BUFFER = 0x0203CCE0     # the naming screen's 10-char buffer (sCodeBuffer)
SPECIALS_SLOT_222 = 0x28D47C  # specials-table entry the naming screen calls

PARTY_COUNT = 0x0201B95D
MON_ADDR = 0x02033000    # scratch EWRAM for the synthetic mon
TRAMP_ADDR = 0x02032F00  # scratch EWRAM for the ARM->Thumb entry trampoline

# --- encounter marker (../../game_plans/rowe_parity.md §3) ---
# Observation point is the REAL entry of BattleStringExpandPlaceholders, which
# CM_BattleStringGated always tail-calls -- so whatever r0 it is entered with IS
# the shim's decision, exactly the same trick the wild cases use on
# CreateWildMon. The expander itself never runs.
EXPAND_STRING = 0x08088928
MARKER_TRAMP_LIT_OFF = 0x471268     # marker trampoline literal = entry | 1
MARKER_ADDR = 0x09650000
MARKER_STRIDE = 64
# The two byte-identical "Wild {FD}{06} appeared!{FB}" copies the shim matches.
TEXT_WILD_A = 0x08575304
TEXT_WILD_B = 0x08575318
# Something that is NOT a wild intro, to prove other battle messages are not
# clobbered. Any ROM address the shim must pass through untouched will do.
TEXT_NOT_WILD = 0x08575400
ENEMY_PARTY = 0x0201BBB8            # gEnemyParty, docs/ROUTINE_MAP.md
DST_SCRATCH = 0x02033400            # scratch dst for the expander (never written)

# DERIVED, never a literal. A stale count here does not fail as a count error:
# the "out of range -> give" case below picks NUM_CHARACTERS + 1, and once the
# roster grows past the literal that index is a REAL character, so the test
# fails as an apparent shim bug. That exact confusion cost real time on the
# 2026-07-26 Radical Red pass.
NUM_CHARACTERS = len(json.loads(
    (ROOT / "tools" / "character_mode" / "characters_manifest.json").read_text()
)["characters"])
NUM_SPECIES = 1561
STRIDE = 196
CODE_LEN = 11


def build_mon(species, is_egg=False):
    """Minimal valid party mon (plaintext: personality=otId=0 -> xor key 0,
    substruct order index 0 = Growth,Attacks,EVs,Misc)."""
    mon = bytearray(100)
    mon[19] = 0x02  # bit1 hasSpecies
    struct.pack_into("<H", mon, 32, species)          # Growth+0: species
    ivword = 0x40000000 if is_egg else 0              # Misc+4: bit30 isEgg
    struct.pack_into("<I", mon, 72, ivword)
    csum = sum(struct.unpack_from("<24H", mon, 32)) & 0xFFFF
    struct.pack_into("<H", mon, 28, csum)             # checksum @28
    return bytes(mon)


def gdb_script(cases, gate_entry_thumb, trade_cases, trade_entry_thumb,
               var8004_addr, wild_cases, wild_entry_thumb,
               select_cases, select_entry_thumb,
               marker_cases, marker_entry_thumb):
    # ARM->Thumb entry trampoline in scratch EWRAM: the stub ignores manual
    # CPSR T-bit writes, so the first entry goes through a real BX. Later
    # cases re-enter from Thumb context and can set $pc directly.
    tramp = struct.pack("<III", 0xE59FC000, 0xE12FFF1C, gate_entry_thumb)
    tramphex = tramp.hex()
    lines = [
        "set pagination off",
        "set confirm off",
        # mGBA's GDB stub answers the qXfer:memory-map probe one packet out of
        # step, which desyncs the whole session on modern GDB (15.x here) --
        # "Remote replied unexpectedly to 'vMustReplyEmpty'", with 0 stops
        # collected. Skipping that one probe keeps the handshake in sync.
        # Do NOT also disable target-features: the stub's register layout comes
        # from it, and without it the 'g' packet parses as "Truncated register
        # 16". (2026-07-24: this is why layer 1 could not run.)
        "set remote memory-map-packet off",
        "target remote :2345",
        f'python gdb.selected_inferior().write_memory({TRAMP_ADDR:#x}, bytes.fromhex("{tramphex}"))',
        # zeroed fake SaveBlock1 + repoint gSaveBlock1Ptr at it
        f'python gdb.selected_inferior().write_memory({SB1_FAKE:#x}, bytes({SB1_SIZE}))',
        f'set *(unsigned int*){SB1_PTR:#x} = {SB1_FAKE:#x}',
        f"break *{GIVEMON:#x}",
        f"break *{COPYPC:#x}",
        f"break *{CREATEWILDMON:#x}",
        f"break *{EXPAND_STRING:#x}",
    ]
    for i, c in enumerate(cases):
        mon = build_mon(c["species"], c.get("egg", False))
        lines += [
            f'echo \\n=== CASE {i}: {c["name"]} ===\\n',
            f'python gdb.selected_inferior().write_memory({MON_ADDR:#x}, bytes.fromhex("{mon.hex()}"))',
            f'set *(unsigned char*){FLAG_BYTE:#x} = {FLAG_MASK if c["flag"] else 0:#x}',
            f'set *(unsigned short*){VAR_ADDR:#x} = {c["char_id"]}',
            f'set *(unsigned char*){PARTY_COUNT:#x} = {c["party"]}',
            f'set $r0 = {MON_ADDR:#x}',
            'set $sp = 0x03007F00',
            f'set $lr = {gate_entry_thumb:#x}',  # never returned to; a BP hits first
            (f'set $pc = {TRAMP_ADDR:#x}' if i == 0
             else f'set $pc = {gate_entry_thumb & ~1:#x}'),
            "continue",
            'printf "STOPPED_AT=%08x\\n", $pc',
        ]
    # trade-gate cases: CM_TradeCheck is void; run it with lr parked on the
    # GIVEMON breakpoint, then read gSpecialVar_Result. All runs after the
    # give cases start from Thumb context, so $pc can be set directly.
    for i, c in enumerate(trade_cases):
        lines += [
            f'echo \\n=== TRADE {i}: {c["name"]} ===\\n',
            f'set *(unsigned char*){FLAG_BYTE:#x} = {FLAG_MASK if c["flag"] else 0:#x}',
            f'set *(unsigned short*){VAR_ADDR:#x} = {c["char_id"]}',
            f'set *(unsigned short*){var8004_addr:#x} = {c["idx"]}',
            f'set *(unsigned short*){SPECIAL_RESULT:#x} = 0xDEAD',
            'set $r0 = 0',
            'set $sp = 0x03007F00',
            f'set $lr = {GIVEMON | 1:#x}',
            f'set $pc = {trade_entry_thumb & ~1:#x}',
            "continue",
            f'printf "TRADE_RESULT=%04x\\n", *(unsigned short*){SPECIAL_RESULT:#x}',
        ]
    # wild-encounter override trials: observation point is CreateWildMon's
    # own entry, which the gate always tail-calls (overridden or not) — so
    # whatever (r0,r1) it's entered with is exactly the gate's decision.
    # Every run after the give cases is already in Thumb context.
    for i, c in enumerate(wild_cases):
        lines += [
            f'set *(unsigned char*){FLAG_BYTE:#x} = {FLAG_MASK if c["flag"] else 0:#x}',
            f'set *(unsigned short*){VAR_ADDR:#x} = {c["char_id"]}',
            f'set $r0 = {c["species"]}',
            f'set $r1 = {c["level"]}',
            'set $sp = 0x03007F00',
            f'set $lr = {GIVEMON | 1:#x}',
            f'set $pc = {wild_entry_thumb & ~1:#x}',
            "continue",
            'printf "WILD_RESULT=%d,%d\\n", $r0, $r1',
        ]
    # encounter marker: which string does the shim hand the expander?
    for i, c in enumerate(marker_cases):
        mon = build_mon(c["species"])
        lines += [
            f'echo \\n=== MARKER {i}: {c["name"]} ===\\n',
            f'python gdb.selected_inferior().write_memory({ENEMY_PARTY:#x}, bytes.fromhex("{mon.hex()}"))',
            f'set *(unsigned char*){FLAG_BYTE:#x} = {FLAG_MASK if c["flag"] else 0:#x}',
            f'set *(unsigned short*){VAR_ADDR:#x} = {c["char_id"]}',
            f'set $r0 = {c["src"]:#x}',
            f'set $r1 = {DST_SCRATCH:#x}',
            'set $sp = 0x03007F00',
            f'set $lr = {GIVEMON | 1:#x}',
            f'set $pc = {marker_entry_thumb & ~1:#x}',
            "continue",
            'printf "MARKER_R0=%08x\\n", $r0',
        ]

    # selection gate: drive the REAL shipped entry (the specials-table slot the
    # naming screen calls) with the REAL shipped code bytes, and read back what
    # it decided. The naming screen itself cannot be typed to an arbitrary
    # character from a test -- Unbound proved that the hard way -- but the code
    # buffer is exactly what it hands the matcher, so filling it in is driving
    # the same gate with the same input.
    for i, c in enumerate(select_cases):
        lines += [
            f'echo \\n=== SELECT {i}: {c["name"]} ===\\n',
            f'python gdb.selected_inferior().write_memory({CODE_BUFFER:#x}, bytes.fromhex("{c["code"]}"))',
            f'set *(unsigned char*){FLAG_BYTE:#x} = 0',
            f'set *(unsigned short*){VAR_ADDR:#x} = 0',
            f'set *(unsigned short*){STARTER_VAR_ADDR:#x} = 0xBEEF',
            f'set *(unsigned short*){SPECIAL_RESULT:#x} = 0',
            'set $r0 = 0',
            'set $sp = 0x03007F00',
            f'set $lr = {GIVEMON | 1:#x}',
            f'set $pc = {select_entry_thumb & ~1:#x}',
            "continue",
            f'printf "SELECT_RESULT=%d,%d\\n", *(unsigned short*){VAR_ADDR:#x},'
            f' (*(unsigned char*){FLAG_BYTE:#x} & {FLAG_MASK:#x}) != 0',
        ]
    lines += ["disconnect", "quit"]
    return "\n".join(lines) + "\n"


def main():
    rom = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "build" / "lazarus_cm.gba"

    # gate entry straight from the shipped artifact (trampoline literal)
    romdata = rom.read_bytes()
    gate = struct.unpack_from("<I", romdata, TRAMP_LIT_OFF)[0]
    assert gate & 1 and 0x08000000 < (gate & ~1) < 0x0A000000, hex(gate)
    print(f"gate entry (from ROM trampoline literal): {gate:#x}")

    # CM_TradeCheck entry from the first trade wrapper's callnative ptr;
    # VAR_0x8004 storage from the ROM's special-vars pointer table
    wa = struct.unpack_from("<I", romdata, 0x2B61E5 + 1)[0] - 0x08000000
    trade_entry = struct.unpack_from("<I", romdata, wa + 11)[0]
    assert trade_entry & 1 and 0x08000000 < (trade_entry & ~1) < 0x0A000000
    var8004 = struct.unpack_from("<I", romdata, SPECIAL_VARS_TABLE_OFF + 4 * 4)[0]
    assert 0x02000000 <= var8004 < 0x02040000, hex(var8004)
    print(f"trade-check entry: {trade_entry:#x}; VAR_0x8004 @ {var8004:#x}")

    with open(ROOT / "tools" / "character_mode" / "characters_manifest.json") as f:
        chars = json.load(f)["characters"]
    assert len(chars) == NUM_CHARACTERS
    bitmaps = (ROOT / "tools" / "character_mode" / "rosters_expanded.bin").read_bytes()
    sp_table = json.loads(
        (ROOT / "tools" / "character_mode" / "rom_species_table.json").read_text())
    # duplicate names exist (forms) -> keep the lowest id (base form)
    name_to_id = {}
    for k, v in sorted(sp_table["species"].items(), key=lambda kv: int(kv[0])):
        name_to_id.setdefault(v, int(k))

    def allows(ci0, sp):  # ci0 = 0-based character index
        return bool(bitmaps[ci0 * STRIDE + (sp >> 3)] & (1 << (sp & 7)))

    red0 = next(i for i, c in enumerate(chars) if c["character"] == "Red")
    red_id = red0 + 1
    pikachu = name_to_id["Pikachu"]
    assert allows(red0, pikachu), "Red's bitmap must allow Pikachu"

    # off-roster species for Red that some OTHER character's roster leads with
    # (proves per-character bitmaps differ, not just presence/absence)
    other0 = other_sp = None
    for i, c in enumerate(chars):
        sp = c["roster_species_ids"][0]
        if not allows(red0, sp) and allows(i, sp):
            other0, other_sp = i, sp
            break
    assert other0 is not None, "no differential species found?!"
    other_name = chars[other0]["character"]
    sp_name = sp_table["species"][str(other_sp)]
    print(f"differential: {sp_name} ({other_sp}) — off Red's roster, "
          f"on {other_name}'s (char {other0 + 1})")

    cases = [
        {"name": "flag off -> give", "flag": 0,
         "char_id": red_id, "party": 1, "species": other_sp, "expect": GIVEMON},
        {"name": "party empty -> give (soft-lock guard)", "flag": 1,
         "char_id": red_id, "party": 0, "species": other_sp, "expect": GIVEMON},
        {"name": f"Red + Pikachu({pikachu}) -> give (on roster)", "flag": 1,
         "char_id": red_id, "party": 1, "species": pikachu, "expect": GIVEMON},
        {"name": f"Red + {sp_name}({other_sp}) -> PC (off roster)", "flag": 1,
         "char_id": red_id, "party": 1, "species": other_sp, "expect": COPYPC},
        {"name": "char 0 (unset) -> give", "flag": 1,
         "char_id": 0, "party": 1, "species": other_sp, "expect": GIVEMON},
        {"name": f"Red + {sp_name} EGG -> give (eggs exempt)", "flag": 1,
         "char_id": red_id, "party": 1, "species": other_sp, "egg": True,
         "expect": GIVEMON},
        {"name": f"char {NUM_CHARACTERS + 1} out of range -> give", "flag": 1,
         "char_id": NUM_CHARACTERS + 1, "party": 1, "species": other_sp,
         "expect": GIVEMON},
        {"name": f"{other_name} + {sp_name} -> give (their roster differs)",
         "flag": 1, "char_id": other0 + 1, "party": 1, "species": other_sp,
         "expect": GIVEMON},
        {"name": f"out-of-model species {NUM_SPECIES + 39} -> give (never block)",
         "flag": 1, "char_id": red_id, "party": 1, "species": NUM_SPECIES + 39,
         "expect": GIVEMON},
    ]
    # borderline in-model species: highest id, only if Red's bitmap rejects it
    if not allows(red0, NUM_SPECIES - 1):
        cases.append({"name": f"Red + species {NUM_SPECIES - 1} (max in-model, "
                              "off roster) -> PC", "flag": 1, "char_id": red_id,
                      "party": 1, "species": NUM_SPECIES - 1, "expect": COPYPC})

    # trade-gate decision table (verdict written to gSpecialVar_Result)
    trade_sp = [struct.unpack_from("<H", romdata,
                                   TRADE_TABLE_OFF + k * TRADE_STRIDE + 14)[0]
                for k in range(4)]
    trade_cases = [{"name": "CM off, trade 0 -> allow",
                    "flag": 0, "char_id": 0, "idx": 0, "expect": 1}]
    for k, sp in enumerate(trade_sp):
        exp = 1 if allows(red0, sp) else 0
        nm = sp_table["species"].get(str(sp), f"#{sp}")
        trade_cases.append({"name": f"Red, trade {k} ({nm}) -> "
                                    f"{'allow' if exp else 'refuse'}",
                            "flag": 1, "char_id": red_id, "idx": k, "expect": exp})
    allow0 = next((i for i in range(NUM_CHARACTERS) if allows(i, trade_sp[0])), None)
    if allow0 is not None:
        trade_cases.append({"name": f"{chars[allow0]['character']}, trade 0 -> "
                                    "allow (their roster has it)",
                            "flag": 1, "char_id": allow0 + 1, "idx": 0, "expect": 1})
    trade_cases.append({"name": "Red, trade idx 7 out of range -> allow",
                        "flag": 1, "char_id": red_id, "idx": 7, "expect": 1})

    # wild-encounter override trials (new, 2026-07-17): decode the wild gate
    # entry from the shipped wild trampoline literal, and independently
    # derive Red's own wildmons.bin table (never-legendary by construction —
    # see emit_wildmons.py) to check every override lands on a real member.
    wild_gate = struct.unpack_from("<I", romdata, WILD_TRAMP_LIT_OFF)[0]
    assert wild_gate & 1 and 0x08000000 < (wild_gate & ~1) < 0x0A000000, hex(wild_gate)
    print(f"wild gate entry (from ROM wild trampoline literal): {wild_gate:#x}")

    wildmons = (ROOT / "tools" / "character_mode" / "wildmons.bin").read_bytes()
    assert len(wildmons) % NUM_CHARACTERS == 0
    wildmon_stride = len(wildmons) // NUM_CHARACTERS
    red_wild_species = set()
    base = red0 * wildmon_stride
    i = 0
    while i + 4 <= wildmon_stride:
        raw, lo, hi = struct.unpack_from("<HBB", wildmons, base + i)
        if raw == 0:
            break
        red_wild_species.add(raw & 0x7FFF)
        i += 4
    assert red_wild_species, "Red's wildmons table must not be empty"

    # Red's 1% legendary pool (game_plans/legendary_encounters.md). Same entry
    # format, separate blob -- an override may legitimately come from either.
    legendaries = (ROOT / "tools" / "character_mode" / "legendaries.bin").read_bytes()
    legendary_stride = len(legendaries) // len(chars)
    red_legendary_species = set()
    _b = red0 * legendary_stride
    _i = 0
    while _i + 4 <= legendary_stride:
        _raw, _lo, _hi = struct.unpack_from("<HBB", legendaries, _b + _i)
        if _raw == 0:
            break
        red_legendary_species.add(_raw & 0x7FFF)
        _i += 4
    assert red_legendary_species, \
        "Red must have a legendary pool, or the positive assertion below is vacuous"
    assert not (red_wild_species & set(chars[red0]["roster_species_ids"][chars[red0]["starter_count"]:])), \
        "Red's wildmons table must never contain a legendary roster id"
    print(f"Red's wild-override pool: {len(red_wild_species)} species")

    WILD_TRIALS_OFF = 20    # CM off: deterministic, a handful of trials suffices
    WILD_TRIALS_ON = 200    # CM on: enough for a ~10% rate estimate with a loose band
    wild_input_species = other_sp  # off-Red's-catch-roster, so an override is unambiguous
    wild_input_level = 30
    wild_cases = (
        [{"flag": 0, "char_id": red_id, "species": wild_input_species,
          "level": wild_input_level} for _ in range(WILD_TRIALS_OFF)]
        + [{"flag": 1, "char_id": red_id, "species": wild_input_species,
            "level": wild_input_level} for _ in range(WILD_TRIALS_ON)]
    )

    # --- selection gate (the playability threshold, 2026-07-26) -------------
    # Entry and code bytes both come out of the SHIPPED ROM: the entry from the
    # specials slot the naming screen dispatches through, the codes from the
    # injected code table. Nothing here re-encodes a name, so the test cannot
    # pass against a build whose table says something else.
    select_entry = struct.unpack_from("<I", romdata, SPECIALS_SLOT_222)[0]
    assert select_entry & 1 and 0x08000000 < (select_entry & ~1) < 0x0A000000
    codes_off = int(re.search(r"^CODES_ADDR\s*=\s*(0x[0-9A-Fa-f]+)",
                              (ROOT / "tools" / "inject_character_mode.py").read_text(),
                              re.M).group(1), 16) - 0x08000000

    def code_bytes(i):
        return romdata[codes_off + i * CODE_LEN:codes_off + (i + 1) * CODE_LEN]

    hidden0 = next((i for i, c in enumerate(chars) if c.get("hidden")), None)
    assert hidden0 is not None, "no hidden characters -- did derive_drops.py run?"
    select_cases = [
        {"name": f"{chars[red0]['character']} (offered) -> selected",
         "code": code_bytes(red0).hex(), "expect": (red_id, 1)},
        {"name": f"{chars[hidden0]['character']} (under threshold) -> refused",
         "code": code_bytes(hidden0).hex(), "expect": (0, 0)},
        {"name": "unknown code -> refused",
         "code": (b"\xBB" * 4 + b"\xFF" * (CODE_LEN - 4)).hex(), "expect": (0, 0)},
    ]
    # A second hidden character, chosen as the LAST one in the table: an
    # off-by-one in the hidden bitmap's indexing shows up at the ends first.
    hiddenN = next((i for i in range(len(chars) - 1, -1, -1)
                    if chars[i].get("hidden")), None)
    if hiddenN is not None and hiddenN != hidden0:
        select_cases.append(
            {"name": f"{chars[hiddenN]['character']} (last hidden) -> refused",
             "code": code_bytes(hiddenN).hex(), "expect": (0, 0)})
    # ...and the last OFFERED character, for the same reason in the other
    # direction: a bitmap read that drifts high would refuse a real character.
    lastok = next((i for i in range(len(chars) - 1, -1, -1)
                   if not chars[i].get("hidden")), None)
    if lastok is not None and lastok != red0:
        select_cases.append(
            {"name": f"{chars[lastok]['character']} (last offered) -> selected",
             "code": code_bytes(lastok).hex(), "expect": (lastok + 1, 1)})

    # --- encounter marker (2026-08-21) ---------------------------------------
    # Entry from the SHIPPED marker trampoline's literal, like every other entry
    # here, so the test exercises exactly what the retargeted BL reaches.
    marker_entry = struct.unpack_from("<I", romdata, MARKER_TRAMP_LIT_OFF)[0]
    assert marker_entry & 1 and 0x08000000 < (marker_entry & ~1) < 0x0A000000, \
        hex(marker_entry)
    print(f"marker entry (from ROM trampoline literal): {marker_entry:#x}")

    def marker_for(ci0):
        return MARKER_ADDR + ci0 * MARKER_STRIDE

    # A species on Red's roster, and one that is not, resolved from the shipped
    # bitmaps rather than hardcoded.
    red_on = next(sp for sp in range(1, 500) if allows(red0, sp))
    # A REAL species id that Red's bitmap does not allow -- validity matters,
    # because a nonexistent id would make GetMonData's read meaningless and the
    # case would pass for the wrong reason.
    red_off = next(sp for sp in range(1, 500)
                   if not allows(red0, sp) and str(sp) in sp_table["species"])
    other0 = next(i for i in range(len(chars))
                  if i != red0 and not chars[i].get("hidden")
                  and any(allows(i, sp) for sp in range(1, 500)))
    other_on = next(sp for sp in range(1, 500) if allows(other0, sp))

    marker_cases = [
        # The positive claim. Everything else here is an absence.
        {"name": f"CM on, {chars[red0]['character']}, on-roster -> marker",
         "flag": 1, "char_id": red0 + 1, "species": red_on, "src": TEXT_WILD_A,
         "expect": marker_for(red0)},
        # THE control that matters: a different character must get a DIFFERENT
        # string. A shim that ignored charId and always returned the first
        # character's marker would pass every other case here.
        {"name": f"CM on, {chars[other0]['character']} (char {other0 + 1}) -> its OWN marker",
         "flag": 1, "char_id": other0 + 1, "species": other_on, "src": TEXT_WILD_A,
         "expect": marker_for(other0)},
        # The second copy of the string must be matched too -- the whole reason
        # the shim tests both is that we could not tell them apart statically.
        {"name": "CM on, on-roster, SECOND string copy -> marker",
         "flag": 1, "char_id": red0 + 1, "species": red_on, "src": TEXT_WILD_B,
         "expect": marker_for(red0)},
        # Off-roster: unmarked. This is the case the live e2e cannot make
        # deterministic (a 10% override could turn it on-roster), which is
        # exactly why it belongs here.
        {"name": "CM on, OFF-roster mon -> vanilla string",
         "flag": 1, "char_id": red0 + 1, "species": red_off, "src": TEXT_WILD_A,
         "expect": TEXT_WILD_A},
        {"name": "CM off -> vanilla string",
         "flag": 0, "char_id": red0 + 1, "species": red_on, "src": TEXT_WILD_A,
         "expect": TEXT_WILD_A},
        # Any other battle message must pass through untouched, or the marker
        # would be rewriting unrelated text.
        {"name": "a non-wild-intro string is never substituted",
         "flag": 1, "char_id": red0 + 1, "species": red_on, "src": TEXT_NOT_WILD,
         "expect": TEXT_NOT_WILD},
    ]

    script = HERE / "shim_test.gdb"
    script.write_text(gdb_script(cases, gate, trade_cases, trade_entry, var8004,
                                  wild_cases, wild_gate,
                                  select_cases, select_entry,
                                  marker_cases, marker_entry))

    launcher = ["mgba-qt", "-g", str(rom)]
    if not os.environ.get("DISPLAY"):
        launcher = ["xvfb-run", "-a"] + launcher
    subprocess.run(["pkill", "-f", "mgba-qt -g"], capture_output=True)
    time.sleep(1)
    emu = subprocess.Popen(launcher, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
    try:
        time.sleep(4)  # let xvfb + the stub come up
        r = subprocess.run(["gdb-multiarch", "-nx", "-batch", "-x", str(script)],
                           capture_output=True, text=True, timeout=120)
        out = r.stdout
    finally:
        emu.terminate()
        try:
            emu.wait(timeout=5)
        except subprocess.TimeoutExpired:
            emu.kill()

    stops = [int(m, 16) for m in re.findall(r"STOPPED_AT=([0-9a-f]+)", out)]
    tresults = [int(m, 16) for m in re.findall(r"TRADE_RESULT=([0-9a-f]+)", out)]
    wresults = [(int(a), int(b) & 0xFF) for a, b in
                (m.split(",") for m in re.findall(r"WILD_RESULT=(-?\d+,-?\d+)", out))]
    wresults = [(a & 0xFFFF, b) for a, b in wresults]
    sresults = [(int(a) & 0xFFFF, int(b)) for a, b in
                (m.split(",") for m in
                 re.findall(r"SELECT_RESULT=(-?\d+,-?\d+)", out))]
    mresults = [int(m, 16) for m in re.findall(r"MARKER_R0=([0-9a-f]+)", out)]
    print(out[-3000:] if len(out) > 3000 else out)
    if (len(stops) != len(cases) or len(tresults) != len(trade_cases)
            or len(wresults) != len(wild_cases)
            or len(sresults) != len(select_cases)
            or len(mresults) != len(marker_cases)):
        print(f"FATAL: expected {len(cases)} stops + {len(trade_cases)} trade "
              f"+ {len(wild_cases)} wild + {len(select_cases)} select results, "
              f"got {len(stops)} + {len(tresults)} + {len(wresults)} + "
              f"{len(sresults)}")
        print(r.stderr[-2000:])
        return 1

    failures = 0
    checks_run = 0
    print("\n=== RESULTS ===")
    for c, got in zip(cases, stops):
        ok = got == c["expect"]
        checks_run += 1
        failures += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {c['name']}: stopped at {got:#x} "
              f"(expected {c['expect']:#x})")
    for c, got in zip(trade_cases, tresults):
        ok = got == c["expect"]
        checks_run += 1
        failures += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] trade: {c['name']}: result {got} "
              f"(expected {c['expect']})")

    # wild-encounter override trials
    wild_off = wresults[:WILD_TRIALS_OFF]
    wild_on = wresults[WILD_TRIALS_OFF:WILD_TRIALS_OFF + WILD_TRIALS_ON]

    off_unchanged = sum(1 for sp, lvl in wild_off
                        if sp == wild_input_species and lvl == wild_input_level)
    ok = off_unchanged == len(wild_off)
    checks_run += 1
    failures += not ok
    print(f"  [{'PASS' if ok else 'FAIL'}] wild: CM off, {len(wild_off)} trials -> "
          f"never overridden ({off_unchanged}/{len(wild_off)} unchanged)")

    on_overridden = [(sp, lvl) for sp, lvl in wild_on
                     if not (sp == wild_input_species and lvl == wild_input_level)]
    rate = len(on_overridden) / len(wild_on) if wild_on else 0
    rate_ok = 0.04 <= rate <= 0.20   # target 10%, generous band for 300 Bernoulli trials
    checks_run += 1
    failures += not rate_ok
    print(f"  [{'PASS' if rate_ok else 'FAIL'}] wild: CM on, {len(wild_on)} trials -> "
          f"{len(on_overridden)} overridden ({rate:.1%}, expected ~10%)")

    # An override may come from EITHER pool now. Checking only wildmons.bin was
    # correct until the 1% legendary roll existed; left as-is it rejects exactly
    # the species the new feature is supposed to produce.
    exclusion_bad = [sp for sp, lvl in on_overridden
                     if sp not in red_wild_species and sp not in red_legendary_species]
    excl_ok = not exclusion_bad
    checks_run += 1
    failures += not excl_ok
    print(f"  [{'PASS' if excl_ok else 'FAIL'}] wild: every overridden species is on "
          f"Red's roster, from either pool ({len(exclusion_bad)} bad, "
          f"e.g. {exclusion_bad[:5]})")

    # ---- THE POSITIVE ASSERTION (the spec's biggest risk) -------------------
    #
    # Every other wild assertion here is of the form "an override never produced
    # a legendary". Once the dex filter exists that is satisfied BOTH by correct
    # suppression AND by the legendary path being completely dead, so on its own
    # it can never show the feature works. These trials run with no legendary
    # caught, so the pool is full and the roll must fire. ~1% of 200 is ~2.
    legendary_hits = [sp for sp, lvl in on_overridden if sp in red_legendary_species]
    pos_ok = len(legendary_hits) > 0
    checks_run += 1
    failures += not pos_ok
    print(f"  [{'PASS' if pos_ok else 'FAIL'}] wild: the 1% legendary roll ACTUALLY "
          f"FIRED ({len(legendary_hits)} of {len(wild_on)} trials, "
          f"e.g. {sorted(set(legendary_hits))[:3]})")

    # ...and stays rare. 12+ would mean it is leaking into the 10% path.
    rare_ok = len(legendary_hits) < 12
    checks_run += 1
    failures += not rare_ok
    print(f"  [{'PASS' if rare_ok else 'FAIL'}] wild: legendaries stay rare "
          f"({len(legendary_hits)} < 12 in {len(wild_on)} trials)")

    # The ordinary override must still dominate; if the legendary roll had
    # swallowed the 10% path, this collapses.
    ordinary = len(on_overridden) - len(legendary_hits)
    dom_ok = ordinary > len(legendary_hits)
    checks_run += 1
    failures += not dom_ok
    print(f"  [{'PASS' if dom_ok else 'FAIL'}] wild: the 10% roster override still "
          f"dominates ({ordinary} ordinary vs {len(legendary_hits)} legendary)")

    level_bad = [lvl for _, lvl in on_overridden if not (1 <= lvl <= 100)]
    lvl_ok = not level_bad
    checks_run += 1
    failures += not lvl_ok
    print(f"  [{'PASS' if lvl_ok else 'FAIL'}] wild: every overridden level stays in "
          f"[1,100] ({len(level_bad)} bad)")

    for c, got in zip(select_cases, sresults):
        ok = got == tuple(c["expect"])
        checks_run += 1
        failures += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] select: {c['name']}: "
              f"(char={got[0]}, flag={got[1]}) (expected char={c['expect'][0]}, "
              f"flag={c['expect'][1]})")

    for c, got in zip(marker_cases, mresults):
        ok = got == c["expect"]
        checks_run += 1
        failures += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] marker: {c['name']}: "
              f"r0={got:#010x} (expected {c['expect']:#010x})")

    # This total used to be hand-summed from the case lists by name. That is
    # a CLAIM, not a count of what ran: its sibling wild_encounter_shim_test.py
    # printed "21/21 checks passed" while running 20, in both modes, for as
    # long as its version of this expression existed. Count the real results,
    # and pin the count to a literal (rowe_parity.md §9 Finding 2).
    total = checks_run
    print(f"\n{total - failures}/{total} passed")
    if assert_tally(total, EXPECT_CHECKS, "shim_unit_test"):
        return 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
