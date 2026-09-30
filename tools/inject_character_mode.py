#!/usr/bin/env python3
"""Build the Character Mode patched ROM for Pokemon Lazarus v2.0.

Pipeline (all addresses CONFIRMED — docs/ROUTINE_MAP.md +
docs/SELECTION_MECHANISM.md, pinned to rom.sha1):

  1. Compile src/character_mode.c (three entry points) at SHIM_ADDR inside
     the big free block (ROM 0x095F0EA4+). The block is BL-unreachable from
     low ROM, but every reference to it is a full 32-bit pointer except the
     BL call-site patches, which go through 8-byte trampolines written over a
     DEAD function near them (TRAMPOLINE_BLOCK below; until 2026-09-29 they
     sat in 0xFF runs that were really trainer back-sprite pixels).
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

def _resolve_charmap():
    """Path to this repo's vendored game-text charmap (tools/charmap.txt).

    This was a hardcoded absolute path into the unrelated "Pokemon Rowe
    Alteration" working tree, which made this repo unbuildable and
    unverifiable from a fresh clone. The charmap is now vendored here
    (byte-identical, md5 b31d142ca98103d64d707f9894fa42e3). Resolution is
    anchored to this file's own location, never the cwd.

    Override with the CM_CHARMAP environment variable.
    """
    import os
    from pathlib import Path
    override = os.environ.get("CM_CHARMAP")
    if override:
        p = Path(override)
        if not p.is_file():
            raise SystemExit("CM_CHARMAP=%s is not a file" % override)
        return p
    # Walk up to the REPO ROOT only. An unbounded walk would keep climbing past
    # the repo into ~ and could silently pick up an unrelated tools/charmap.txt
    # -- reading the wrong charmap presents as "this game encodes text
    # differently", not as a missing file. Bound it at the .git directory.
    for parent in Path(__file__).resolve().parents:
        cand = parent / "tools" / "charmap.txt"
        if cand.is_file():
            return cand
        if (parent / ".git").exists():
            break
    raise SystemExit(
        "charmap.txt not found. Expected it vendored at <repo>/tools/charmap.txt; "
        "set CM_CHARMAP to override.")

CHARMAP = _resolve_charmap()

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
with open(HERE / "character_mode" / "characters_manifest.json") as _f:
    TOBIAS_CHAR_ID = next((i + 1 for i, c in enumerate(json.load(_f)["characters"])
                           if c["character"] == "Tobias"), 0)

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
# 2026-09-02: the four data blobs moved out of the 0x095Fxxxx window into the
# wide free area above LEGENDARY_ADDR, because the shim outgrew the 2,368-byte
# slot it had between SHIM_ADDR and the old BITMAPS_ADDR when the activation
# sweep was added. Nothing outside this file hardcodes them -- the C gets them
# as -D, and verify_artifacts.py parses them back out of this file -- and a
# save stores the character INDEX, never an address, so moving them is safe for
# existing saves. SCRIPT_ADDR and TRADE_SCRIPT_ADDR deliberately did NOT move:
# those are the two with pointers patched into shipped ROM regions.
# Above MARKER_ADDR's block (ends 0x09653B80). NOT 0x09620000: that whole
# window through 0x09648000 belongs to the Phase 3 sprite pointer table and
# blobs, and putting the bitmaps there collides -- which surfaces only as
# "target not 0xFF", never as "these two overlap". Hence the overlap check in
# splice() below.
BITMAPS_ADDR   = 0x09660000  # 238*196=46,648B -> ends 0x0966B638
CODES_ADDR     = 0x0966C000  # 238*11=2,618B   -> ends 0x0966CA3A
STARTERS_ADDR  = 0x0966CC00  # 238*2=476B      -> ends 0x0966CDDC
HIDDEN_ADDR    = 0x0966CE00  # (238+7)/8=30B   -> ends 0x0966CE1E
SCRIPT_ADDR    = 0x095FE000
# The shim runs from SHIM_ADDR up to (not into) the confirm script. Explicit,
# because the old guard was "< BITMAPS_ADDR" and silently became meaningless
# the moment the bitmaps moved away.
SHIM_MAX       = SCRIPT_ADDR - SHIM_ADDR
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

# ⚠️⚠️ THE TRAMPOLINES USED TO LIVE IN "0xFF RUNS" THAT WERE PIXELS. The
# 22-byte runs at 0x08470A5A / 0x0847125A were white pixels inside frames 114
# and 115 of a 64x64 trainer BACK SPRITE (SpriteFrameImage table 0x084829EC,
# 146 x 0x800; template #32 of the array at 0x08CCB108), so every catch/gift/
# wild/marker build drew code bytes on that trainer's head. Measured
# 2026-09-29 by rendering the frame from the base ROM and the build
# (rowe_parity.md §13.53). A run of 0xFF is not free space unless nothing
# points at it; "scans need a validity criterion".
#
# They now sit over the standalone IsRemovingLastPartyMon at 0x081DD61C. This
# build inlines it at all five call sites, so it has no BL callers and no
# pointer to its entry (verify_artifacts re-checks both on the base ROM), and
# it is 1.4 MB from the farthest hook (the marker's), well inside BL reach.
# The whole block is asserted to be the base ROM's function before it is
# cleared and reused.
TRAMPOLINE_BLOCK      = 0x081DD61C
TRAMPOLINE_BLOCK_ORIG = bytes.fromhex(
    "00b50a4b1b781b060020 1b16012b03d1074b1b78002b01d002bc0847054b1878".replace(" ", ""))
TRAMPOLINE_ADDR        = TRAMPOLINE_BLOCK + 0    # catch + gift gate
WILD_TRAMPOLINE_ADDR   = TRAMPOLINE_BLOCK + 8    # wild-encounter gate
MARKER_TRAMPOLINE_ADDR = TRAMPOLINE_BLOCK + 16   # encounter marker
# ROWE's second guard in the PC (src/character_mode.c CM_PSSLastMonGuard;
# docs/ROUTINE_MAP.md "PC second guard"). Five inlined IsRemovingLastPartyMon
# sites and CanShiftMon's call to CountPartyAliveNonEggMonsExcept (anchor:
# special 0x88's wrapper calls it) are retargeted through one trampoline.
PSS_GUARD_TRAMPOLINE_ADDR = TRAMPOLINE_BLOCK + 24
PSS_COUNT_ALIVE_EXCEPT = 0x081D4EDC
PSS_GUARD_BL_SITES = (0x1D662E, 0x1D66E8, 0x1D6BC8, 0x1D6C04, 0x1D6C3A)
PSS_CANSHIFT_BL    = 0x1DD718         # CanShiftMon (0x081DD6F4): bl Count
PSS_CANSHIFT_TAIL  = 0x1DD71C         # cmp r0,#0 ; bne -> b <epilogue 0x081DD710> ; nop
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

# --- egg-hatch sweep (../game_plans/rowe_parity.md §13.16/§13.18) ---
# The injected tail for the hatch script, 11 bytes, in a verified free run
# (0xFF in both the base ROM and every build). Script `goto` operands are
# absolute pointers, so there is no BL-reach constraint on where this lives.
# tools/character_mode/egg_hook.py carries the RE and the byte grammar.
EGG_TAIL_ADDR = 0x9670000

# --- PC-exit sweep (../game_plans/rowe_parity.md §13.24/§13.26c) ---
# Two 14-byte replayed tails, 0x20 apart, one per PC access script (they differ
# only in where their goto rejoins). tools/character_mode/pc_hook.py has the RE.
PC_TAIL_ADDR = 0x9671000

# --- in-game roster display (../game_plans/roster_display.md), PORTED from
# Seaglass 2026-09-27. The design transfers; every address below was
# re-derived from THIS binary (docs/ROUTINE_MAP.md "Roster display"). All of it
# lives in the verified-free run after the PC tails; splice() proves each
# region clear and non-overlapping. No BL-reach constraint anywhere: the table
# is reached through literals, the code through the table and `callnative`,
# the scripts through the desk's BG pointer and `goto`.
#
# The family ROOTS of every character's roster (emit_roster_roots.py).
ROSTER_ROOTS_ADDR = 0x09672000
_ROOTS_MANIFEST = json.loads(
    (HERE / "character_mode" / "roster_roots_manifest.json").read_text())
ROSTER_ROOTS_OFF = _ROOTS_MANIFEST["roots_offset_bytes"]
# sDynamicListMenuEventCollections, RELOCATED so the roster owns set 2. Found
# by its load pattern: four `cmp r1,#255` gated loads (0x0820BA6C, 0x0820BBCA,
# 0x0820BC80, 0x0820BF8E) through these three literals -- the Seaglass shape.
# NONE is 0xFF here too (the donor enum says 2). The 0x08CEBB34 literal at
# 0x0820CC0C is a different object 48 B on, not a table reference.
DYN_EVENT_TABLE_ORIG = 0x08CEBB04
DYN_EVENT_TABLE_REFS = (0x20BAA8, 0x20BD64, 0x20C078)   # literal-pool file offsets
DYN_EVENT_ENTRY_SIZE = 12
DYN_EVENT_ORIG_ENTRIES = 2
DYN_EVENT_SLOTS = 3
ROSTER_CB_SET = 2
DYN_EVENT_TABLE_ADDR = 0x09674000
# src/roster_display.c. 0x09675000 is left free on purpose: the negative test
# uses it as a known-free stray target.
ROSTER_MENU_ADDR = 0x09676000
# The pre-entry + roster block + row strings: their own region, so nothing in
# the pinned SCRIPT_ADDR / TRADE_SCRIPT_ADDR blobs moves.
ROSTER_SCRIPT_ADDR = 0x09677000
# The cheat-code desk script is reached from FOUR BG events (whole-ROM scan,
# asserted below): the University desk's two tiles (7,8) and (8,8), and (3,1)
# in two other maps -- the same spot as Seaglass's bedroom cheat device. All
# four are repointed, so every one of them gets the same menu with CM on and
# the unchanged stock script with CM off. (Only (8,8) was repointed at first,
# and the live test caught it: the player faces (7,8) in cm_red_active.ss.)
DESK_BG_PTR_OFFS = (0xEA28A0, 0xEA28AC, 0xEAAD54, 0xEAB010)
# The University desk (8,8): its BG event's script pointer, the stock script,
# and the point right after its "Would you like to enter a code?" yes/no --
# `delay 2; loadword "Please enter the code."` -- where "Enter a code" lands so
# the player is not asked twice.
DESK_BG_PTR_OFF = 0xEA28AC
DESK_ORIG_SCRIPT = 0x083287A7
DESK_AFTER_PROMPT = 0x083287BE
DESK_AFTER_PROMPT_BYTES = bytes([0x28, 0x02, 0x00, 0x0F, 0x00]) + struct.pack("<I", 0x0832B579)

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
def op_lockall():           return bytes([0x69])
def op_checkflag(flag):     return bytes([0x2B]) + struct.pack("<H", flag)
def op_dynmultichoice(cb_set, names):
    """dynmultichoice, script-pointer form: left 0, top 0, B allowed, default
    rows before scroll, unsorted, initial 0. Layout decoded from THIS ROM's
    handler (0x08209AE9): E3 u16 u16 u8 u8 u8 u16 u8(set) u8(argc) u32[argc]."""
    return (bytes([0xE3]) + struct.pack("<HH", 0, 0) + bytes([0, 0xFF, 0])
            + struct.pack("<H", 0) + bytes([cb_set, len(names)])
            + b"".join(struct.pack("<I", n) for n in names))
def op_dynmultistack(cb_set):
    """The STACK form: argc 1 and a NULL word, which the handler peeks but does
    not consume; it then runs as four `nop` (opcode 0x00 is 0x08208251,
    `movs r0,#0; bx lr`)."""
    return (bytes([0xE3]) + struct.pack("<HH", 0, 0) + bytes([0, 0xFF, 0])
            + struct.pack("<H", 0) + bytes([cb_set, 1]) + struct.pack("<I", 0))
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
                    f"-DTOBIAS_CHAR_ID={TOBIAS_CHAR_ID}",
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
    assert len(shim) <= SHIM_MAX, (
        f"shim too big: {len(shim)} > {SHIM_MAX} -- it would run into "
        f"SCRIPT_ADDR {SCRIPT_ADDR:#x}")

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

    # --- roster display: row pusher + callback set 2 (src/roster_display.c) ---
    roster_roots = (CM / "roster_roots.bin").read_bytes()
    assert _ROOTS_MANIFEST["characters"] == NUM_CHARACTERS, (
        "roster_roots.bin was emitted for %d characters, this build has %d -- "
        "re-run emit_roster_roots.py" % (_ROOTS_MANIFEST["characters"], NUM_CHARACTERS))
    assert len(roster_roots) == _ROOTS_MANIFEST["blob_size_bytes"]
    robj, relf, rbin = BUILD / "roster_display.o", BUILD / "roster_display.elf", BUILD / "roster_display.bin"
    subprocess.run(["arm-none-eabi-gcc", "-c", "-mthumb", "-mcpu=arm7tdmi",
                    "-O2", "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra",
                    f"-DNUM_CHARACTERS={NUM_CHARACTERS}",
                    f"-DROSTER_ROOTS_ADDR={ROSTER_ROOTS_ADDR:#x}",
                    f"-DROSTER_ROOTS_OFF={ROSTER_ROOTS_OFF}",
                    "-o", str(robj), str(ROOT / "src" / "roster_display.c")], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext", f"{ROSTER_MENU_ADDR:#x}",
                    "--entry", "CM_RosterPushRows",
                    "-o", str(relf), str(robj)], check=True)
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", str(relf), str(rbin)], check=True)
    roster_menu = rbin.read_bytes()
    rsym = subprocess.run(["arm-none-eabi-nm", str(relf)], check=True,
                          capture_output=True, text=True).stdout

    def roster_sym(name):
        m = re.search(rf"^([0-9a-f]+) [Tt] {name}$", rsym, re.M)
        assert m, f"{name} not found in:\n{rsym}"
        a = int(m.group(1), 16)
        assert ROSTER_MENU_ADDR <= a < ROSTER_MENU_ADDR + len(roster_menu), \
            f"{name} at {a:#x} outside the spliced blob"
        return a | 1

    ROSTER_PUSH = roster_sym("CM_RosterPushRows")
    ROSTER_CALLBACKS = (roster_sym("CM_RosterMenu_OnInit"),
                        roster_sym("CM_RosterMenu_OnSelectionChanged"),
                        roster_sym("CM_RosterMenu_OnDestroy"))
    print(f"roster display: {len(roster_menu)} bytes @ {ROSTER_MENU_ADDR:#x} "
          f"(push {ROSTER_PUSH:#x}, set {ROSTER_CB_SET} = "
          f"{', '.join(f'{c:#x}' for c in ROSTER_CALLBACKS)})")
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
    hook_sweep    = syms["CM_SweepPartyToPCNative"] | 1
    hook_pss_guard = syms["CM_PSSLastMonGuard"] | 1

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
           # Sweep AFTER the give, never before: beforehand the party holds only
           # the vanilla starter, which is off-roster, and the never-empty rule
           # would keep it and box nothing. See CM_SweepPartyToPCNative.
           + op_callnative(hook_sweep)
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
    spliced = []

    def splice(rom_addr, payload, label):
        off = rom_addr - 0x08000000
        assert rom_addr + len(payload) <= FREE_END_ROM, f"{label} overruns ROM"
        seg = data[off:off + len(payload)]
        assert all(b == 0xFF for b in seg), f"{label}: target not 0xFF @ {rom_addr:#x}"
        # The 0xFF precondition alone reports an overlap as "target not 0xFF",
        # which reads like a wrong base ROM rather than two blobs colliding --
        # it cost a build when the bitmaps were moved on top of the sprite
        # blobs. Check the regions against each other so the message names both.
        for o_off, o_len, o_label in spliced:
            assert off >= o_off + o_len or off + len(payload) <= o_off, \
                (f"{label} @ {rom_addr:#x} (+{len(payload)}) overlaps "
                 f"{o_label} @ {o_off + 0x08000000:#x} (+{o_len})")
        spliced.append((off, len(payload), label))
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

    # --- roster display: roots blob, relocated callback table, code, scripts ---
    splice(ROSTER_ROOTS_ADDR, roster_roots, "roster roots")
    _dyn_orig_off = DYN_EVENT_TABLE_ORIG - 0x08000000
    _dyn_live = bytes(data[_dyn_orig_off:
                           _dyn_orig_off + DYN_EVENT_ORIG_ENTRIES * DYN_EVENT_ENTRY_SIZE])
    for _w in struct.unpack(f"<{len(_dyn_live) // 4}I", _dyn_live):
        assert 0x08000000 <= _w < 0x0A000000 and _w & 1, (
            f"callback table at {DYN_EVENT_TABLE_ORIG:#x} holds {_w:#x}, not a "
            f"Thumb function pointer -- wrong address or wrong ROM")
    assert DYN_EVENT_SLOTS == ROSTER_CB_SET + 1 == DYN_EVENT_ORIG_ENTRIES + 1
    splice(DYN_EVENT_TABLE_ADDR, _dyn_live + struct.pack("<III", *ROSTER_CALLBACKS),
           "dynmultichoice callback table")
    for _roff in DYN_EVENT_TABLE_REFS:
        _cur = struct.unpack_from("<I", data, _roff)[0]
        assert _cur == DYN_EVENT_TABLE_ORIG, (
            f"callback-table literal {_roff + 0x08000000:#x} holds {_cur:#x}, "
            f"expected {DYN_EVENT_TABLE_ORIG:#x} -- wrong ROM, or already patched")
        struct.pack_into("<I", data, _roff, DYN_EVENT_TABLE_ADDR)
    splice(ROSTER_MENU_ADDR, roster_menu, "roster display code")

    # Pre-entry (the desk's BG pointer lands here) + shared roster block.
    #   checkflag CM; goto_if unset -> the stock desk script, unchanged
    #   lockall; dynmultichoice NONE [View roster, Enter a code]
    #   0 -> roster block; 1 -> the desk right after its yes/no; B -> release
    _o = DESK_AFTER_PROMPT - 0x08000000
    assert bytes(data[_o:_o + len(DESK_AFTER_PROMPT_BYTES)]) == DESK_AFTER_PROMPT_BYTES, (
        f"desk script at {DESK_AFTER_PROMPT:#x} is not `delay 2; loadword "
        f"\"Please enter the code.\"` -- the desk script has moved")
    _t_view = enc_text("View roster", cm)
    _t_code = enc_text("Enter a code", cm)

    def _roster_script(a):
        b = bytearray()
        b += op_checkflag(FLAG_CHARACTER_MODE) + op_goto_if(0, DESK_ORIG_SCRIPT)
        b += op_lockall()
        b += op_dynmultichoice(0xFF, [a["t_view"], a["t_code"]])
        b += op_compare(0x800D, 0) + op_goto_if(1, a["roster"])
        b += op_compare(0x800D, 1) + op_goto_if(1, DESK_AFTER_PROMPT)
        b += op_releaseall() + op_end()                               # B
        a["roster_here"] = len(b)
        b += op_callnative(ROSTER_PUSH)
        b += op_compare(0x800D, 0) + op_goto_if(1, a["roster_end"])   # no rows
        b += op_dynmultistack(ROSTER_CB_SET)
        a["roster_end_here"] = len(b)
        b += op_releaseall() + op_end()
        a["t_view_here"] = len(b); b += _t_view
        a["t_code_here"] = len(b); b += _t_code
        return b

    _ph = dict(t_view=0, t_code=0, roster=0, roster_end=0)
    _roster_script(_ph)
    _ra = dict(t_view=ROSTER_SCRIPT_ADDR + _ph["t_view_here"],
               t_code=ROSTER_SCRIPT_ADDR + _ph["t_code_here"],
               roster=ROSTER_SCRIPT_ADDR + _ph["roster_here"],
               roster_end=ROSTER_SCRIPT_ADDR + _ph["roster_end_here"])
    roster_script = bytes(_roster_script(_ra))
    splice(ROSTER_SCRIPT_ADDR, roster_script, "roster display scripts")
    _pat = struct.pack("<I", DESK_ORIG_SCRIPT)
    _all, _i = [], data.find(_pat)
    _own = range(ROSTER_SCRIPT_ADDR - 0x08000000,
                 ROSTER_SCRIPT_ADDR - 0x08000000 + len(roster_script))
    while _i != -1:
        if _i not in _own:          # the pre-entry's own CM-off goto
            _all.append(_i)
        _i = data.find(_pat, _i + 1)
    assert sorted(_all) == sorted(DESK_BG_PTR_OFFS), (
        f"references to the desk script {DESK_ORIG_SCRIPT:#x} are "
        f"{[hex(a) for a in _all]}, expected exactly {[hex(a) for a in DESK_BG_PTR_OFFS]}")
    for _off in DESK_BG_PTR_OFFS:
        struct.pack_into("<I", data, _off, ROSTER_SCRIPT_ADDR)
    print(f"roster display: roots {len(roster_roots)} B @ {ROSTER_ROOTS_ADDR:#x}; "
          f"callback table {DYN_EVENT_SLOTS} slots @ {DYN_EVENT_TABLE_ADDR:#x} "
          f"(was {DYN_EVENT_TABLE_ORIG:#x}, {len(DYN_EVENT_TABLE_REFS)} refs repointed); "
          f"{len(DESK_BG_PTR_OFFS)} desk BG events -> pre-entry @ {ROSTER_SCRIPT_ADDR:#x} "
          f"({len(roster_script)} B)")

    # --- egg-hatch sweep ---
    # The one enforcement hole reachable in ordinary play: eggs are exempt
    # everywhere by design so an egg event cannot block progress, and nothing
    # then looked at what the egg HATCHED INTO. This overlays the hatch
    # script's tail with a goto into a replayed tail that ends by calling the
    # activation sweep -- after the hatch's waitstate, so it sees the finished
    # Pokemon rather than the egg. docs/GIFT_EGGS.md lists the gift eggs this
    # covers; tools/character_mode/egg_hook.py has the RE.
    sys.path.insert(0, str(Path(__file__).resolve().parent / "character_mode"))
    import egg_hook
    egg_entry = struct.unpack_from("<I", data, egg_hook.CALLER_POOL_OFF)[0]
    assert egg_entry == egg_hook.SCRIPT_ENTRY, (
        f"egg-hatch script pointer is {egg_entry:#x}, expected "
        f"{egg_hook.SCRIPT_ENTRY:#x} -- the hatch caller has moved")
    egg_tail, egg_patches = egg_hook.build(EGG_TAIL_ADDR, hook_sweep)
    splice(EGG_TAIL_ADDR, egg_tail, "egg-hatch tail")
    for _eoff, _eorig, _erepl in egg_patches:
        _eseg = bytes(data[_eoff:_eoff + len(_eorig)])
        assert _eseg == _eorig, (
            f"egg splice site {_eoff + 0x08000000:#x} holds {_eseg.hex()}, "
            f"expected {_eorig.hex()} -- wrong ROM, or already patched")
        data[_eoff:_eoff + len(_erepl)] = _erepl
    print(f"egg-hatch sweep: tail {len(egg_tail)} B @ {EGG_TAIL_ADDR:#x}, "
          f"splice @ {egg_hook.SPLICE_ROM_ADDR:#x} -> callnative {hook_sweep:#x}")

    # --- PC-exit sweep ---
    # Enforcement routes off-roster mons INTO the PC and, until 2026-09-06,
    # nothing re-enforced the roster afterwards -- so a mon the catch gate had
    # just boxed could be withdrawn straight back and kept, no exploit required
    # (rowe_parity.md §13.24). The PC is opened from a SCRIPT whose special
    # carries a waitstate, exactly like the egg hatch, so this is the same
    # splice pointed at a different tail: the sweep runs AFTER the waitstate,
    # once the storage UI has closed and the party is whatever the player left.
    # ⚠️ ROWE's Cb2_ExitPSS semantics -- UNDO ON EXIT, not prevention -- and it
    # deliberately does NOT reproduce ROWE's IsRemovingLastAllowedPartyMon.
    # See pc_hook.py's docstring.
    import pc_hook
    for _sr, _sf, _so, _txtoff in pc_hook.SITES:
        _t = struct.unpack_from("<I", data, _txtoff)[0]
        assert _t == pc_hook.PC_TEXT_PTR, (
            f"PC script @{_sr:#x} shows message {_t:#x}, expected "
            f"{pc_hook.PC_TEXT_PTR:#x} -- the PC access script has moved")
    pc_blobs, pc_patches = pc_hook.build(PC_TAIL_ADDR, hook_sweep)
    for _addr, _blob in pc_blobs:
        splice(_addr, _blob, "PC-exit tail")
    for _poff, _porig, _prepl in pc_patches:
        _pseg = bytes(data[_poff:_poff + len(_porig)])
        assert _pseg == _porig, (
            f"PC splice site {_poff + 0x08000000:#x} holds {_pseg.hex()}, "
            f"expected {_porig.hex()} -- wrong ROM, or already patched")
        data[_poff:_poff + len(_prepl)] = _prepl
    print(f"PC-exit sweep: {len(pc_blobs)} tails @ {PC_TAIL_ADDR:#x}, "
          f"splices @ {', '.join(f'{s[0]:#x}' for s in pc_hook.SITES)} "
          f"-> callnative {hook_sweep:#x}")

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


    # The trampoline block: prove it is still the base ROM's dead function,
    # then clear it so splice()'s 0xFF precondition covers it like free space.
    _tb = TRAMPOLINE_BLOCK - 0x08000000
    assert bytes(data[_tb:_tb + len(TRAMPOLINE_BLOCK_ORIG)]) == TRAMPOLINE_BLOCK_ORIG, (
        "the dead IsRemovingLastPartyMon is not at %#x -- re-derive before "
        "overwriting it" % TRAMPOLINE_BLOCK)
    data[_tb:_tb + 32] = b"\xff" * 32

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

    # --- PC second guard: one trampoline, six retargeted BLs, one tail ---
    splice(PSS_GUARD_TRAMPOLINE_ADDR,
           struct.pack("<HH", 0x4B00, 0x4718) + struct.pack("<I", hook_pss_guard),
           "PC second-guard trampoline")
    for _site in PSS_GUARD_BL_SITES + (PSS_CANSHIFT_BL,):
        _cur = bytes(data[_site:_site + 4])
        _exp = thumb_bl(0x08000000 + _site, PSS_COUNT_ALIVE_EXCEPT)
        assert _cur == _exp, f"PC guard site {_site:#x}: {_cur.hex()} != {_exp.hex()}"
        data[_site:_site + 4] = thumb_bl(0x08000000 + _site, PSS_GUARD_TRAMPOLINE_ADDR)
    _cur = bytes(data[PSS_CANSHIFT_TAIL:PSS_CANSHIFT_TAIL + 4])
    assert _cur == bytes.fromhex("0028f4d1"), f"CanShiftMon tail: {_cur.hex()}"
    data[PSS_CANSHIFT_TAIL:PSS_CANSHIFT_TAIL + 4] = struct.pack("<HH", 0xE7F8, 0x46C0)
    print(f"PC second guard: {len(PSS_GUARD_BL_SITES)} deposit/move/release sites + "
          f"CanShiftMon -> {hook_pss_guard:#x} via {PSS_GUARD_TRAMPOLINE_ADDR:#x}")

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
    i = data.find(pat)
    sites = []
    while i != -1:
        if data[i - 1] == 0x23:
            sites.append(i)
        i = data.find(pat, i + 1)
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
