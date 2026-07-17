#!/usr/bin/env python3
"""GDB-driven unit test for the Lazarus Character Mode acquisition gate.

Runs the REAL CM_GiveMonToPlayerGated code in the REAL emulator (mGBA's GDB
stub), with a synthetic Pokemon struct and a synthetic SaveBlock1, and checks
which branch the shim takes for every case in the decision table.

Lazarus differences from the Radical Red original of this test:
  - Flag 0x945 / var 0x40E0 live inside SaveBlock1 (flags +0x12E8, vars
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
import struct
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent

GIVEMON = 0x081C40BC     # pass-through branch point (function entry)
COPYPC = 0x081C4130      # enforcement branch point (function entry)
TRAMP_LIT_OFF = 0x470A68  # trampoline literal in ROM = gate entry | 1

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
FLAG_CM = 0x945
VAR_CM_CHAR = 0x40E0

FLAG_BYTE = SB1_FAKE + FLAGS_OFF + (FLAG_CM >> 3)
FLAG_MASK = 1 << (FLAG_CM & 7)
VAR_ADDR = SB1_FAKE + VARS_OFF + 2 * (VAR_CM_CHAR - 0x4000)

PARTY_COUNT = 0x0201B95D
MON_ADDR = 0x02033000    # scratch EWRAM for the synthetic mon
TRAMP_ADDR = 0x02032F00  # scratch EWRAM for the ARM->Thumb entry trampoline

NUM_CHARACTERS = 179
NUM_SPECIES = 1561
STRIDE = 196


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
               var8004_addr):
    # ARM->Thumb entry trampoline in scratch EWRAM: the stub ignores manual
    # CPSR T-bit writes, so the first entry goes through a real BX. Later
    # cases re-enter from Thumb context and can set $pc directly.
    tramp = struct.pack("<III", 0xE59FC000, 0xE12FFF1C, gate_entry_thumb)
    tramphex = tramp.hex()
    lines = [
        "set pagination off",
        "set confirm off",
        "target remote :2345",
        f'python gdb.selected_inferior().write_memory({TRAMP_ADDR:#x}, bytes.fromhex("{tramphex}"))',
        # zeroed fake SaveBlock1 + repoint gSaveBlock1Ptr at it
        f'python gdb.selected_inferior().write_memory({SB1_FAKE:#x}, bytes({SB1_SIZE}))',
        f'set *(unsigned int*){SB1_PTR:#x} = {SB1_FAKE:#x}',
        f"break *{GIVEMON:#x}",
        f"break *{COPYPC:#x}",
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

    script = HERE / "shim_test.gdb"
    script.write_text(gdb_script(cases, gate, trade_cases, trade_entry, var8004))

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
    print(out[-3000:] if len(out) > 3000 else out)
    if len(stops) != len(cases) or len(tresults) != len(trade_cases):
        print(f"FATAL: expected {len(cases)} stops + {len(trade_cases)} trade "
              f"results, got {len(stops)} + {len(tresults)}")
        print(r.stderr[-2000:])
        return 1

    failures = 0
    print("\n=== RESULTS ===")
    for c, got in zip(cases, stops):
        ok = got == c["expect"]
        failures += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {c['name']}: stopped at {got:#x} "
              f"(expected {c['expect']:#x})")
    for c, got in zip(trade_cases, tresults):
        ok = got == c["expect"]
        failures += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] trade: {c['name']}: result {got} "
              f"(expected {c['expect']})")
    total = len(cases) + len(trade_cases)
    print(f"\n{total - failures}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
