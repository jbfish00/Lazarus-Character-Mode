#!/usr/bin/env python3
"""Build the Character Mode patched ROM for Pokemon Lazarus v2.0.

Pipeline (all addresses CONFIRMED — docs/ROUTINE_MAP.md +
docs/SELECTION_MECHANISM.md, pinned to rom.sha1):

  1. Compile src/character_mode.c (three entry points) at SHIM_ADDR inside
     the big free block (ROM 0x095F0EA4+). The block is BL-unreachable from
     low ROM, but every reference to it is a full 32-bit pointer except the
     two BL call-site patches, which go through an 8-byte trampoline at
     0x08470A64 (verified 0xFF padding inside both sites' BL windows).
  2. Splice payloads into a ROM copy (source ROM is never written):
       shim code   @ SHIM_ADDR      confirm script @ SCRIPT_ADDR
       bitmaps     @ BITMAPS_ADDR   codes          @ CODES_ADDR
       starters    @ STARTERS_ADDR  trampoline     @ TRAMPOLINE_ADDR
  3. Patch (verifying original bytes first, refusing otherwise):
       - specials-table slot for special 0x222 (file 0x28D47C):
         0x0813F86D -> CM_CheatDispatchHook   (selection hook)
       - BL @0x0A7BDA (wild catch) and BL @0x20D416 (ScriptGiveMon):
         GiveMonToPlayer -> trampoline -> CM_GiveMonToPlayerGated
       - 112 inline `callnative 0x0820DF41` script pointers ->
         CM_GiveMonNativeGated                (script-gift gate)
       - branch-0 goto_if target of the cheat switch (file 0x3287D7):
         0x08328994 -> confirm script         (confirmation message + give)
       - 9 BL callers of CreateWildMon 0x0824AA54 (grass/cave, surf, rock
         smash, all fishing rods — every random-roll wild table; static/
         scripted gifts never call it) -> wild trampoline ->
         CM_CreateWildMonGated                (wild-encounter roster override)
  4. Write build/lazarus_cm.gba + build/lazarus_cm.bps (BPS against the
     OFFICIAL-PATCH OUTPUT, never clean Emerald — standing rule).

Selection UX: type a character code at the Acrisia University cheat-code
entry (codes = character name, spaces/punctuation stripped, max 10 chars,
case-insensitive). Debug codes: CMDBGOFF, CMDBGGIVE1 (on-roster test give),
CMDBGGIVE2 (off-roster test give).
"""
import hashlib
import json
import re
import struct
import subprocess
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
ROM_IN = ROOT / "rom" / "lazarus-v2.gba"
ROM_SHA1 = "7dcdc7e280bc4631487e13dd37e6e0cea04adea6"
BUILD = ROOT / "build"
CHARMAP = Path("/home/jbfish00/Documents/Pokemon Rowe Alteration/charmap.txt")

BITMAP_STRIDE = 196
CODE_LEN = 11


def _derive_num_characters():
    """DERIVED, never a literal. A stale hardcoded character count is the most
    repeated bug in this workspace and it never presents as a count error -- on
    the 2026-07-26 Radical Red pass it fired six times, twice reading as a bug
    in the test shim itself because a hardcoded out-of-range index had quietly
    become a real character."""
    with open(HERE / "character_mode" / "characters_manifest.json") as f:
        return len(json.load(f)["characters"])


NUM_CHARACTERS = _derive_num_characters()

# --- confirmed layout constants ---
FREE_FILE_BASE = 0x15F0EA4          # big 0xFF block start (file offset)
# Moved down 0x140 on 2026-07-27 to fit the 1% legendary roll. The free block
# starts at FREE_FILE_BASE (0x095F0EA4) and the shim used to start 0x15C into
# it, wasting that head room while the window up to BITMAPS_ADDR was only
# 2048 B -- which the legendary picker overflowed by 43 B. This reclaims it and
# gives the shim 2368 B. splice() asserts the whole target range is still 0xFF,
# so a mistake here fails the build rather than corrupting the ROM.
SHIM_ADDR      = 0x095F0EC0
# Rebased 2026-07-26 for the 238-character roster audit. The 202-char layout
# interleaved blobs (script at 0x95FBC00, wildmons at 0x95FD000, codes way up at
# 0x9610800) and 238-char bitmaps run straight through all three. Everything
# downstream of the bitmaps is now laid out in one ascending, non-interleaved
# order with slack, so the next growth moves one constant instead of three.
# splice() asserts every target is still 0xFF in the working copy, which is what
# actually proves these do not overlap -- keep it that way.
BITMAPS_ADDR   = 0x095F1800  # 238*196=46,648B -> ends 0x095FCE38
CODES_ADDR     = 0x095FD000  # 238*11=2,618B   -> ends 0x095FDA3A
STARTERS_ADDR  = 0x095FDC00  # 238*2=476B      -> ends 0x095FDDDC
HIDDEN_ADDR    = 0x095FDE00  # (238+7)/8=30B   -> ends 0x095FDE1E
SCRIPT_ADDR    = 0x095FE000
WILDMONS_ADDR  = 0x09600000  # 238*stride      -> must end before LEGENDARY_ADDR
# The 1% legendary wild pool (../game_plans/legendary_encounters.md). Sits in
# the same free run, immediately after wildmons: at 238 chars x stride 16 it is
# 3,808 B, and wildmons currently ends at 0x09613FD0, so this has ~49 KB of
# clearance before the sprite table. Both ends are asserted below.
LEGENDARY_ADDR = 0x09614000  # 238*stride      -> must end before 0x09620000
CM_SPRITE_PTRS_ADDR  = 0x09620000   # Phase 3, separate free run; additive table
CM_SPRITE_BLOBS_ADDR = 0x09620800
# Mugshot renderer (src/character_sprite.c). A SEPARATE compile unit from the
# main shim, which is already 1771 B in the 2048 B window before BITMAPS_ADDR
# -- adding to it would overflow into the bitmaps. Placed past the sprite blobs
# (which end ~0x09643384) in the same free run; the 0xFF precondition in
# splice() is what actually proves it clear. No BL-reach constraint: every
# engine call it makes goes through a function pointer, and the script reaches
# it by an absolute `callnative` operand.
# Moved 0x09644000 -> 0x09648000 on 2026-07-26: the 238-character sprite table
# grew the blobs from 142,156 B to 146,896 B and they now end at 0x096445D0,
# past where the renderer used to sit. Keep it clear of the blob end -- the
# assert below says so in words rather than as a bare "target not 0xFF".
CM_MUGSHOT_ADDR = 0x09648000
FREE_END_ROM   = 0x08000000 + 0x2000000  # 32 MiB ROM end

TRAMPOLINE_ADDR      = 0x08470A64   # 8B inside a 22B 0xFF run (word-aligned)
WILD_TRAMPOLINE_ADDR = 0x08470A6C   # next 8B in the same 22B run
# Encounter marker (../game_plans/rowe_parity.md §3). The 22-byte run above is
# full (8B + 8B leaves 4), but the ROM has three more runs of the identical
# shape at 0x800 intervals; this takes the next one. 3.91 MB from the hook at
# 0x080880B6 -- inside the +-4 MB Thumb BL window with little margin, so
# re-check the reach if either address moves.
MARKER_TRAMPOLINE_ADDR = 0x08471264
# The BL inside BufferStringBattle that every intro string funnels through:
#   <many> ldr r0, =<string> ; b 0x080880B4
#   0x080880B4: ldr r1, =gDisplayedStringBattle ; bl BattleStringExpandPlaceholders
MARKER_BL_SITE   = 0x0880B6
EXPAND_STRING    = 0x08088928
# TWO byte-identical copies of "Wild {FD}{06} appeared!{FB}", reached from
# different arms of the compiled switch; the shim matches both (see the note in
# src/character_mode.c for why picking one was not safe).
TEXT_WILD_APPEARED = (0x08575304, 0x08575318)
MARKER_ADDR      = 0x09650000   # 238*64 = 15,232 B; verified 0xFF in the
                                # original and clear of the sprite blob (ends
                                # ~0x09646000) and the mugshot (0x09648000)
MARKER_STRIDE    = 64

BL_SITE_CATCH = 0x0A7BDA            # battle-engine catch caller (live-pinned)
BL_SITE_GIFT  = 0x20D416            # ScriptGiveMon's internal call
GIVEMON_ADDR  = 0x081C40BC

# CreateWildMon(species, level) — live breakpoint-trace-confirmed 2026-07-17
# (docs/ROUTINE_MAP.md): the single choke point every wild table (land/cave,
# surf, rock smash, fishing) funnels species+level through after its roll.
CREATEWILDMON_ADDR = 0x0824AA54
BL_SITES_WILD = (0x1036FE, 0x103876, 0x24AC24, 0x24ACF0, 0x24AD50,
                 0x24ADC8, 0x24ADF6, 0x24B4E2, 0x24B504)

SPECIALS_SLOT_222 = 0x28D47C        # specials table entry for special 0x222
ORIG_DISPATCH = 0x0813F86D

GIVE_NATIVE = 0x0820DF41            # callnative give fn (inline script ptrs)

BRANCH0_PTR_OFF = 0x3287D7          # goto_if target when VAR_RESULT == 0
ORIG_INVALID = 0x08328994           # original "invalid code" branch
RECEIVED_MSG_SUB = 0x083289DB       # fanfare + "received!" script subroutine

FLAG_CHARACTER_MODE = 0x2B0
VAR_CM_CHAR    = 0x40E0
VAR_CM_STARTER = 0x40E4

# In-game trades (docs/ROUTINE_MAP.md): 4 scripts share an identical 17-byte
# "deal confirmed" junction (copyvar 8004,8008; copyvar 8005,800A;
# special 0x100; special 0x101; waitstate). We overlay the first 5 bytes with
# a goto into a per-trade wrapper that asks CM_TradeCheck first.
TRADE_JUNCTIONS = (0x2B61E5, 0x2C8442, 0x2C8E00, 0x319684)
TRADE_JUNCTION_BYTES = bytes([0x19, 0x04, 0x80, 0x08, 0x80,
                              0x19, 0x05, 0x80, 0x0A, 0x80,
                              0x25, 0x00, 0x01, 0x25, 0x01, 0x01, 0x27])
TRADE_SCRIPT_ADDR = 0x095FE800

# --- helpers ---

def load_charmap():
    table = {}
    pat = re.compile(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$")
    with open(CHARMAP, encoding="utf-8") as f:
        for line in f:
            m = pat.match(line.rstrip("\n"))
            if m and m.group(1) not in table:
                table[m.group(1)] = int(m.group(2), 16)
    return table


def enc_text(s, cm):
    out = bytearray()
    for ch in s:
        if ch == "\n":
            out.append(0xFE)
            continue
        if ch not in cm:
            raise ValueError(f"char {ch!r} not in charmap: {s!r}")
        out.append(cm[ch])
    out.append(0xFF)
    return bytes(out)


def thumb_bl(src_rom_addr, dst_rom_addr):
    off = dst_rom_addr - (src_rom_addr + 4)
    assert -0x400000 <= off < 0x400000, f"BL out of range: {off:#x}"
    off = (off >> 1) & 0x3FFFFF
    return struct.pack("<HH", 0xF000 | ((off >> 11) & 0x7FF), 0xF800 | (off & 0x7FF))


def code_for(display):
    """Character name -> typed code: strip accents + non-alnum, cap at 10."""
    n = unicodedata.normalize("NFKD", display)
    n = "".join(ch for ch in n if not unicodedata.combining(ch))
    return "".join(ch for ch in n if ch.isalnum())[:10]


# --- script assembly (opcode lengths verified against this ROM's scripts) ---

def op_compare(var, val):   return bytes([0x21]) + struct.pack("<HH", var, val)
def op_goto_if(cond, addr): return bytes([0x06, cond]) + struct.pack("<I", addr)
def op_goto(addr):          return bytes([0x05]) + struct.pack("<I", addr)
def op_call(addr):          return bytes([0x04]) + struct.pack("<I", addr)
def op_copyvar(dst, src):   return bytes([0x19]) + struct.pack("<HH", dst, src)
def op_setvar(var, val):    return bytes([0x16]) + struct.pack("<HH", var, val)
def op_bufferspecies(buf, sp): return bytes([0x7D, buf]) + struct.pack("<H", sp)
def op_loadword(addr):      return bytes([0x0F, 0x00]) + struct.pack("<I", addr)
def op_callstd(n):          return bytes([0x09, n])
def op_delay(n):            return bytes([0x28]) + struct.pack("<H", n)
def op_callnative(fn_thumb): return bytes([0x23]) + struct.pack("<I", fn_thumb)
def op_releaseall():        return bytes([0x6B])
def op_end():               return bytes([0x02])
def op_callnative_give(fn_thumb, species, level):
    # exact idiom of the ROM's own MONO/starter gives (docs/SELECTION_MECHANISM.md)
    return (bytes([0x23]) + struct.pack("<I", fn_thumb)
            + bytes([0x00, 0x06]) + struct.pack("<HHI", species, level, 0))


CM = HERE / "character_mode"


def main():
    data = bytearray(ROM_IN.read_bytes())
    got = hashlib.sha1(data).hexdigest()
    if got != ROM_SHA1:
        raise SystemExit(f"ROM sha1 mismatch: {got} (expected {ROM_SHA1})")

    cm = load_charmap()
    with open(HERE / "character_mode" / "characters_manifest.json") as f:
        manifest = json.load(f)
    chars = manifest["characters"]
    assert len(chars) == NUM_CHARACTERS, len(chars)  # derived from this file
    bitmaps = (HERE / "character_mode" / "rosters_expanded.bin").read_bytes()
    assert len(bitmaps) == NUM_CHARACTERS * BITMAP_STRIDE, len(bitmaps)
    hidden_bits = (HERE / "character_mode" / "hidden.bin").read_bytes()
    assert len(hidden_bits) == (NUM_CHARACTERS + 7) // 8, len(hidden_bits)
    wildmons = (HERE / "character_mode" / "wildmons.bin").read_bytes()
    assert len(wildmons) % NUM_CHARACTERS == 0, len(wildmons)
    wildmon_stride = len(wildmons) // NUM_CHARACTERS
    assert WILDMONS_ADDR + len(wildmons) <= LEGENDARY_ADDR, \
        f"wildmons run into the legendary pool: {WILDMONS_ADDR + len(wildmons):#x}"
    legendaries = (HERE / "character_mode" / "legendaries.bin").read_bytes()
    assert len(legendaries) % NUM_CHARACTERS == 0, len(legendaries)
    legendary_stride = len(legendaries) // NUM_CHARACTERS
    assert LEGENDARY_ADDR + len(legendaries) <= CM_SPRITE_PTRS_ADDR, \
        f"legendary pool runs into the sprite table: {LEGENDARY_ADDR + len(legendaries):#x}"

    # --- code + starter tables ---
    codes = bytearray()
    seen = {}
    native_codes = {"9RARECANDY", "JUSTCATCH", "WORLDCHAMP", "WATCHPHAUN",
                    "ILOVEALOLA", "ILOVEKALOS", "IWANTMONKE", "ILOVPALDEA",
                    "NEMOSFAVE", "JUSTSHOWME", "WISHINGSTR", "GIMMENUGS",
                    "IMISSJOHTO", "MASKEDOGRE", "LEGENDSZA", "HOUSESTARK",
                    "DRESSUP", "HYLIANFIT", "WILDNATURE", "PORTABLEPC",
                    "MOSEY", "BATTLEPASS"} | {f"MONO{t}" for t in
                    ("BUG","DARK","DRAGN","ELECT","FAIRY","FIGHT","FIRE","FLYIN",
                     "GHOST","GRASS","GROUN","ICE","NORML","POISN","PSYCH","ROCK",
                     "STEEL","WATER")}
    starters = []
    typed_codes = []
    for c in chars:
        code = code_for(c["character"])
        key = code.upper()
        assert 1 <= len(code) <= 10, (c["character"], code)
        assert key not in seen, f"code collision: {code} ({c['character']} vs {seen[key]})"
        assert key not in native_codes, f"clashes with native code: {code}"
        seen[key] = c["character"]
        typed_codes.append(code)
        enc = enc_text(code, cm)
        assert len(enc) <= CODE_LEN
        codes += enc + b"\xFF" * (CODE_LEN - len(enc))
        if c.get("has_signature") and c.get("signature_id"):
            sig = c["signature_id"]
        elif c["roster_species_ids"]:
            sig = c["roster_species_ids"][0]
        else:
            # Empty roster (the 2026-07-25 audit produced 17 of them once this
            # ROM's curated dex was applied). The record exists only to keep
            # every later character's index stable, and the threshold hides it,
            # so no code can select it. SPECIES_NONE also reads as "nothing to
            # give" to the confirm script, which branches on VAR_CM_STARTER == 0.
            assert c["hidden"], f"{c['character']}: empty roster but selectable"
            sig = 0
        starters.append(sig)
    starters_blob = b"".join(struct.pack("<H", s) for s in starters)

    # off-roster debug species for CMDBGGIVE2: wild-obtainable, off char 1's roster
    enc_json = json.loads((HERE / "character_mode" / "encounters.json").read_text())
    sp_table = json.loads((HERE / "character_mode" / "rom_species_table.json").read_text())
    name_to_id = {v: int(k) for k, v in sp_table["species"].items()}
    wild_ids = sorted(name_to_id[n] for n in enc_json["wild"] if n in name_to_id)
    assert wild_ids, "no wild species resolved"
    bm0 = bitmaps[0:BITMAP_STRIDE]
    def on0(sp): return (bm0[sp >> 3] >> (sp & 7)) & 1
    dbg_give2 = next(sp for sp in wild_ids if not on0(sp))
    give2_name = sp_table["species"][str(dbg_give2)]
    print(f"CMDBGGIVE2 species (off-roster for {chars[0]['character']}): "
          f"{dbg_give2} ({give2_name})")

    # --- 1. compile shim ---
    BUILD.mkdir(exist_ok=True)
    obj = BUILD / "character_mode.o"
    elf = BUILD / "character_mode.elf"
    binf = BUILD / "character_mode.bin"
    subprocess.run(["arm-none-eabi-gcc", "-c", "-mthumb", "-mcpu=arm7tdmi",
                    "-O2", "-ffreestanding", "-fno-builtin", "-fno-jump-tables",
                    f"-DCODES_ADDR={CODES_ADDR:#x}",
                    f"-DSTARTERS_ADDR={STARTERS_ADDR:#x}",
                    f"-DBITMAPS_ADDR={BITMAPS_ADDR:#x}",
                    f"-DHIDDEN_ADDR={HIDDEN_ADDR:#x}",
                    f"-DNUM_CHARACTERS={NUM_CHARACTERS}",
                    f"-DDBG_GIVE2_SPECIES={dbg_give2}",
                    f"-DWILDMONS_ADDR={WILDMONS_ADDR:#x}",
                    f"-DMARKER_ADDR={MARKER_ADDR:#x}",
                    f"-DLEGENDARY_ADDR={LEGENDARY_ADDR:#x}",
                    f"-DLEGENDARY_STRIDE={legendary_stride}",
                    f"-DWILDMON_STRIDE={wildmon_stride}",
                    "-o", str(obj), str(ROOT / "src" / "character_mode.c")],
                   check=True)
    libgcc = subprocess.run(["arm-none-eabi-gcc", "-mthumb", "-mcpu=arm7tdmi",
                             "-print-libgcc-file-name"],
                            check=True, capture_output=True, text=True).stdout.strip()
    subprocess.run(["arm-none-eabi-ld", "-Ttext", f"{SHIM_ADDR:#x}",
                    "--entry", "CM_CheatDispatchHook",
                    "-o", str(elf), str(obj), libgcc], check=True)
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", str(elf), str(binf)],
                   check=True)
    shim = binf.read_bytes()
    sym_out = subprocess.run(["arm-none-eabi-nm", str(elf)], check=True,
                             capture_output=True, text=True).stdout
    syms = {m.group(2): int(m.group(1), 16)
            for m in re.finditer(r"^([0-9a-f]+) [Tt] (\w+)$", sym_out, re.M)}
    for need in ("CM_CheatDispatchHook", "CM_GiveMonToPlayerGated",
                 "CM_GiveMonNativeGated", "CM_TradeCheck", "CM_CreateWildMonGated"):
        assert need in syms, f"missing symbol {need}"
    assert len(shim) <= BITMAPS_ADDR - SHIM_ADDR, f"shim too big: {len(shim)}"

    # --- 1b. compile the mugshot renderer (separate unit + link address; see
    # the CM_MUGSHOT_ADDR comment). Both entry points are resolved from the
    # linked ELF rather than assumed to be in source order -- gcc is free to
    # emit them either way and the `callnative` operands must be exact. ---
    mobj = BUILD / "character_sprite.o"
    melf = BUILD / "character_sprite.elf"
    mbin = BUILD / "character_sprite.bin"
    subprocess.run(["arm-none-eabi-gcc", "-c", "-mthumb", "-mcpu=arm7tdmi",
                    "-O2", "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra",
                    f"-DSPRITE_PTRS_ADDR={CM_SPRITE_PTRS_ADDR:#x}",
                    f"-DNUM_CHARACTERS={NUM_CHARACTERS}",
                    "-o", str(mobj), str(ROOT / "src" / "character_sprite.c")],
                   check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext", f"{CM_MUGSHOT_ADDR:#x}",
                    "--entry", "CM_ShowCharacterMugshot",
                    "-o", str(melf), str(mobj)], check=True)
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", str(melf), str(mbin)],
                   check=True)
    mugshot = mbin.read_bytes()
    msym = subprocess.run(["arm-none-eabi-nm", str(melf)], check=True,
                          capture_output=True, text=True).stdout

    def mugshot_sym(name):
        m = re.search(rf"^([0-9a-f]+) [Tt] {name}$", msym, re.M)
        assert m, f"{name} not found in:\n{msym}"
        a = int(m.group(1), 16)
        assert CM_MUGSHOT_ADDR <= a < CM_MUGSHOT_ADDR + len(mugshot), \
            f"{name} at {a:#x} outside the spliced blob"
        return a | 1                    # callnative operands carry the Thumb bit

    SHOW_MUGSHOT = mugshot_sym("CM_ShowCharacterMugshot")
    HIDE_MUGSHOT = mugshot_sym("CM_HideCharacterMugshot")
    print(f"mugshot renderer: {len(mugshot)} bytes @ {CM_MUGSHOT_ADDR:#x} "
          f"(show {SHOW_MUGSHOT:#x}, hide {HIDE_MUGSHOT:#x})")
    print(f"shim: {len(shim)} bytes @ {SHIM_ADDR:#x}; entries: "
          + ", ".join(f"{k}={v:#x}" for k, v in syms.items() if k.startswith("CM_")))

    hook_dispatch = syms["CM_CheatDispatchHook"] | 1
    hook_gate     = syms["CM_GiveMonToPlayerGated"] | 1
    hook_native   = syms["CM_GiveMonNativeGated"] | 1
    hook_trade    = syms["CM_TradeCheck"] | 1
    hook_wild     = syms["CM_CreateWildMonGated"] | 1
    hook_marker   = syms["CM_BattleStringGated"] | 1

    # --- 2. confirm script ---
    txt_on  = enc_text("Character Mode is now active!\nOff-roster catches go to the PC.", cm)
    txt_off = enc_text("Character Mode is now off.", cm)

    # layout: [entry][act][off][txt_on][txt_off] — compute sizes first
    entry_sz = len(op_compare(0, 0) + op_goto_if(5, 0) + op_goto(0))
    # NOTE: RECEIVED_MSG_SUB is a goto-only tail (every path ends in
    # releaseall/end, target 0x083289D9 IS releaseall/end) — it never returns,
    # so everything must happen BEFORE we enter it, and we goto, not call.
    # The mugshot bracket: show before the message, hide after callstd 4
    # returns (it blocks until the player presses A, so the sprite is up for
    # exactly as long as the text). Both are 5 bytes and shift every fixup
    # offset below, so MUG is used there rather than a second literal.
    MUG = len(op_callnative(0))
    act = (op_compare(VAR_CM_STARTER, 0xFFFF) + op_goto_if(1, 0)  # ptr fixed below
           + op_delay(2)
           + op_callnative(SHOW_MUGSHOT)
           + op_loadword(0)  # txt_on ptr fixed below
           + op_callstd(4)
           + op_callnative(HIDE_MUGSHOT)
           + op_copyvar(0x8000, VAR_CM_STARTER)
           + op_bufferspecies(0, 0x8000)
           + op_setvar(0x4001, 0x8000)
           + op_setvar(VAR_CM_STARTER, 0)  # consume the marker before the give
           + op_callnative_give(hook_native, 0x8000, 5)
           + op_goto(RECEIVED_MSG_SUB))  # fanfare + "received!" + nickname/PC, ends script
    off_h = (op_setvar(VAR_CM_STARTER, 0)
             + op_delay(2) + op_loadword(0)  # txt_off ptr fixed below
             + op_callstd(4) + op_releaseall() + op_end())

    act_addr = SCRIPT_ADDR + entry_sz
    off_addr = act_addr + len(act)
    txt_on_addr = off_addr + len(off_h)
    txt_off_addr = txt_on_addr + len(txt_on)

    script = bytearray()
    script += op_compare(VAR_CM_STARTER, 0)
    script += op_goto_if(5, act_addr)          # != 0 -> we matched something
    script += op_goto(ORIG_INVALID)            # else original invalid-code path
    assert len(script) == entry_sz
    script += act
    script += off_h
    script += txt_on
    script += txt_off
    # fix the two placeholder pointers inside act/off_h
    def fixup(needle_off, addr):
        struct.pack_into("<I", script, needle_off, addr)
    # goto_if EQ ptr inside act: entry_sz + 5(compare) + 2 -> u32
    fixup(entry_sz + 5 + 2, off_addr)
    # loadword ptr inside act: after compare(5) + goto_if(6) + delay(3)
    # + callnative show(MUG), skip "0F 00"
    lw_on_off = entry_sz + 5 + 6 + 3 + MUG + 2
    fixup(lw_on_off, txt_on_addr)
    lw_off_off = entry_sz + len(act) + len(off_h) - (len(op_callstd(4)) + 1 + 1) - 4
    fixup(lw_off_off, txt_off_addr)
    print(f"confirm script: {len(script)} bytes @ {SCRIPT_ADDR:#x}")

    # --- 3. splice payloads ---
    def splice(rom_addr, payload, label):
        off = rom_addr - 0x08000000
        assert rom_addr + len(payload) <= FREE_END_ROM, f"{label} overruns ROM"
        seg = data[off:off + len(payload)]
        assert all(b == 0xFF for b in seg), f"{label}: target not 0xFF @ {rom_addr:#x}"
        data[off:off + len(payload)] = payload

    splice(SHIM_ADDR, shim, "shim")
    splice(BITMAPS_ADDR, bitmaps, "bitmaps")
    splice(CODES_ADDR, bytes(codes), "codes")
    splice(STARTERS_ADDR, starters_blob, "starters")
    splice(HIDDEN_ADDR, hidden_bits, "hidden bitmap")
    splice(SCRIPT_ADDR, bytes(script), "script")
    splice(WILDMONS_ADDR, wildmons, "wildmons")
    splice(LEGENDARY_ADDR, legendaries, "legendary pool")
    splice(CM_MUGSHOT_ADDR, mugshot, "mugshot renderer")

    # --- Phase 3 character sprites (2026-07-25) ---
    # Additive: this never touches the engine's own trainer-pic table, so
    # nothing the game already draws changes, and locating that table is not a
    # prerequisite. Blobs first, then a table of absolute ROM pointers.
    _spr_b = CM / "cm_sprite_blobs.bin"
    _spr_o = CM / "cm_sprite_offsets.bin"
    if _spr_b.is_file() and _spr_o.is_file():
        _blobs = _spr_b.read_bytes()
        _offs = _spr_o.read_bytes()
        assert len(_offs) == NUM_CHARACTERS * 8, (len(_offs), NUM_CHARACTERS)
        assert CM_SPRITE_BLOBS_ADDR + len(_blobs) <= CM_MUGSHOT_ADDR, (
            f"sprite blobs end at {CM_SPRITE_BLOBS_ADDR + len(_blobs):#x}, past "
            f"the mugshot renderer at {CM_MUGSHOT_ADDR:#x} -- move it up")
        _ptrs = bytearray()
        _wired = 0
        for _i in range(NUM_CHARACTERS):
            _g, _p = struct.unpack_from("<II", _offs, _i * 8)
            if _g == 0xFFFFFFFF:
                _ptrs += struct.pack("<II", 0, 0)
            else:
                _ptrs += struct.pack("<II", CM_SPRITE_BLOBS_ADDR + _g,
                                            CM_SPRITE_BLOBS_ADDR + _p)
                _wired += 1
        splice(CM_SPRITE_BLOBS_ADDR, _blobs, "character sprite blobs")
        splice(CM_SPRITE_PTRS_ADDR, bytes(_ptrs), "character sprite pointers")
        print(f"character sprites: {_wired}/{NUM_CHARACTERS} wired, "
              f"{len(_blobs):,} B @ {CM_SPRITE_BLOBS_ADDR:#x}, table @ {CM_SPRITE_PTRS_ADDR:#x}")


    # trampoline: ldr r3,[pc,#0]; bx r3; .word gate|1
    tramp = struct.pack("<HH", 0x4B00, 0x4718) + struct.pack("<I", hook_gate)
    assert TRAMPOLINE_ADDR % 4 == 0
    splice(TRAMPOLINE_ADDR, tramp, "trampoline")

    # second trampoline for the wild-encounter gate, same 22B scavenged 0xFF
    # run as the one above (8B used there, this uses the next 8B — verified
    # both fall in the same run and within BL range of all 9 wild call sites).
    wild_tramp = struct.pack("<HH", 0x4B00, 0x4718) + struct.pack("<I", hook_wild)
    assert WILD_TRAMPOLINE_ADDR % 4 == 0
    splice(WILD_TRAMPOLINE_ADDR, wild_tramp, "wild trampoline")

    # --- encounter marker: per-character intro strings + its trampoline ---
    marker_blob = (CM / "marker_strings.bin").read_bytes()
    assert len(marker_blob) == NUM_CHARACTERS * MARKER_STRIDE, (
        f"marker_strings.bin is {len(marker_blob)} B, expected "
        f"{NUM_CHARACTERS * MARKER_STRIDE} -- re-run emit_marker_strings.py")
    splice(MARKER_ADDR, marker_blob, "encounter marker strings")
    assert MARKER_TRAMPOLINE_ADDR % 4 == 0
    splice(MARKER_TRAMPOLINE_ADDR,
           struct.pack("<HH", 0x4B00, 0x4718) + struct.pack("<I", hook_marker),
           "marker trampoline")
    print(f"encounter marker: {len(marker_blob):,} B @ {MARKER_ADDR:#x}, "
          f"stride {MARKER_STRIDE}, trampoline @ {MARKER_TRAMPOLINE_ADDR:#x}")

    # --- 4. patches (verify-then-write) ---
    for site in (BL_SITE_CATCH, BL_SITE_GIFT):
        cur = bytes(data[site:site + 4])
        expect = thumb_bl(0x08000000 + site, GIVEMON_ADDR)
        assert cur == expect, (f"BL site {site:#x}: {cur.hex()} != {expect.hex()} "
                               "(wrong ROM or already patched)")
        data[site:site + 4] = thumb_bl(0x08000000 + site, TRAMPOLINE_ADDR)

    for site in BL_SITES_WILD:
        cur = bytes(data[site:site + 4])
        expect = thumb_bl(0x08000000 + site, CREATEWILDMON_ADDR)
        assert cur == expect, (f"wild BL site {site:#x}: {cur.hex()} != {expect.hex()} "
                               "(wrong ROM or already patched)")
        data[site:site + 4] = thumb_bl(0x08000000 + site, WILD_TRAMPOLINE_ADDR)

    # The shim compares src against these addresses; prove they still hold the
    # exact string before moving the BL, or the marker silently never fires.
    _want = bytes.fromhex("d1dde0d800fd0600d5e4e4d9d5e6d9d8abfbff")
    for _a in TEXT_WILD_APPEARED:
        _got = bytes(data[_a - 0x08000000:_a - 0x08000000 + len(_want)])
        assert _got == _want, (
            f"wild intro string at {_a:#x}: {_got.hex()} != {_want.hex()}")

    cur = bytes(data[MARKER_BL_SITE:MARKER_BL_SITE + 4])
    expect = thumb_bl(0x08000000 + MARKER_BL_SITE, EXPAND_STRING)
    assert cur == expect, (
        f"marker BL site {MARKER_BL_SITE:#x}: {cur.hex()} != {expect.hex()}")
    data[MARKER_BL_SITE:MARKER_BL_SITE + 4] = thumb_bl(
        0x08000000 + MARKER_BL_SITE, MARKER_TRAMPOLINE_ADDR)

    cur = struct.unpack_from("<I", data, SPECIALS_SLOT_222)[0]
    assert cur == ORIG_DISPATCH, f"specials slot: {cur:#x} != {ORIG_DISPATCH:#x}"
    struct.pack_into("<I", data, SPECIALS_SLOT_222, hook_dispatch)

    pat = struct.pack("<I", GIVE_NATIVE)
    n_native = 0
    i = bytes(data).find(pat)
    sites = []
    while i != -1:
        if data[i - 1] == 0x23:
            sites.append(i)
        i = bytes(data).find(pat, i + 1)
    assert len(sites) == 112, f"expected 112 callnative sites, found {len(sites)}"
    for s in sites:
        struct.pack_into("<I", data, s, hook_native)
        n_native += 1

    cur = struct.unpack_from("<I", data, BRANCH0_PTR_OFF)[0]
    assert cur == ORIG_INVALID, f"branch-0 ptr: {cur:#x} != {ORIG_INVALID:#x}"
    struct.pack_into("<I", data, BRANCH0_PTR_OFF, SCRIPT_ADDR)

    # --- 4b. trade gates: per-trade wrapper scripts + junction overlays ---
    txt_refuse = enc_text("Character Mode:\nthis trade is not in your roster.", cm)
    # build: refuse blob first (shared), then 4 wrappers
    refuse_addr = TRADE_SCRIPT_ADDR
    refuse = (op_delay(2) + op_loadword(0) + op_callstd(4) + bytes([0x6C]) + op_end())
    # fixup loadword inside refuse: txt after the 4 wrappers
    wrappers_addr = refuse_addr + len(refuse)
    trade_blob = bytearray(refuse)
    for j in TRADE_JUNCTIONS:
        w_addr = refuse_addr + len(trade_blob)
        resume = 0x08000000 + j + len(TRADE_JUNCTION_BYTES)
        w = bytearray()
        w += bytes([0x19, 0x04, 0x80, 0x08, 0x80])            # copyvar 0x8004, 0x8008
        w += bytes([0x19, 0x05, 0x80, 0x0A, 0x80])            # copyvar 0x8005, 0x800A
        w += bytes([0x23]) + struct.pack("<I", hook_trade)     # callnative CM_TradeCheck
        w += op_compare(0x800D, 0)
        w += op_goto_if(1, refuse_addr)
        w += bytes([0x25, 0x00, 0x01, 0x25, 0x01, 0x01, 0x27])  # special 0x100; 0x101; waitstate
        w += op_goto(resume)
        trade_blob += w
    txt_addr = refuse_addr + len(trade_blob)
    trade_blob += txt_refuse
    struct.pack_into("<I", trade_blob, len(op_delay(2)) + 2, txt_addr)  # loadword ptr
    splice(TRADE_SCRIPT_ADDR, bytes(trade_blob), "trade wrappers")

    w_addr = wrappers_addr
    per_w = (len(trade_blob) - len(refuse) - len(txt_refuse)) // len(TRADE_JUNCTIONS)
    for i, j in enumerate(TRADE_JUNCTIONS):
        cur = bytes(data[j:j + len(TRADE_JUNCTION_BYTES)])
        assert cur == TRADE_JUNCTION_BYTES, f"trade junction {j:#x}: {cur.hex()}"
        data[j:j + 5] = op_goto(wrappers_addr + i * per_w)

    print(f"patched: 2 BL sites, specials slot, {n_native} callnative ptrs, "
          f"branch-0 ptr, {len(TRADE_JUNCTIONS)} trade junctions "
          f"(wrappers @ {TRADE_SCRIPT_ADDR:#x}, {len(trade_blob)} B), "
          f"{len(BL_SITES_WILD)} wild-encounter BL sites "
          f"(wildmons @ {WILDMONS_ADDR:#x}, stride {wildmon_stride}, {len(wildmons)} B; "
          f"legendaries @ {LEGENDARY_ADDR:#x}, stride {legendary_stride}, {len(legendaries)} B)")

    # --- 5. outputs ---
    out_rom = BUILD / "lazarus_cm.gba"
    out_rom.write_bytes(data)
    print(f"wrote {out_rom} sha1={hashlib.sha1(data).hexdigest()}")

    flips = ROOT / "tools" / "bin" / "flips"
    bps = BUILD / "lazarus_cm.bps"
    r = subprocess.run([str(flips), "--create", "--bps", str(ROM_IN), str(out_rom), str(bps)],
                       capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    if bps.exists():
        print(f"patch: {bps} ({bps.stat().st_size} bytes)")

    # Selectable characters only: a hidden character's code is refused at the
    # naming screen, so listing it would promise something the ROM declines.
    _sel = [(code, c, s) for code, c, s in zip(typed_codes, chars, starters)
            if not c.get("hidden")]
    (BUILD / "codes.txt").write_text(
        "\n".join(f"{code}\t{c['character']}\tstarter={s}"
                  for code, c, s in _sel) + "\n")
    print(f"code list: {BUILD/'codes.txt'} ({len(_sel)} selectable of "
          f"{len(typed_codes)} characters)")
    print("Debug codes: CMDBGOFF, CMDBGGIVE1, CMDBGGIVE2 (case-insensitive)")


if __name__ == "__main__":
    main()
