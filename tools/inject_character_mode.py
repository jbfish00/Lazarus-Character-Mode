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

NUM_CHARACTERS = 179
BITMAP_STRIDE = 196
CODE_LEN = 11

# --- confirmed layout constants ---
FREE_FILE_BASE = 0x15F0EA4          # big 0xFF block start (file offset)
SHIM_ADDR      = 0x095F1000
BITMAPS_ADDR   = 0x095F1800
CODES_ADDR     = 0x095FA200
STARTERS_ADDR  = 0x095FAA00
SCRIPT_ADDR    = 0x095FAC00
FREE_END_ROM   = 0x08000000 + 0x2000000  # 32 MiB ROM end

TRAMPOLINE_ADDR = 0x08470A64        # 8B inside a 22B 0xFF run (word-aligned)

BL_SITE_CATCH = 0x0A7BDA            # battle-engine catch caller (live-pinned)
BL_SITE_GIFT  = 0x20D416            # ScriptGiveMon's internal call
GIVEMON_ADDR  = 0x081C40BC

SPECIALS_SLOT_222 = 0x28D47C        # specials table entry for special 0x222
ORIG_DISPATCH = 0x0813F86D

GIVE_NATIVE = 0x0820DF41            # callnative give fn (inline script ptrs)

BRANCH0_PTR_OFF = 0x3287D7          # goto_if target when VAR_RESULT == 0
ORIG_INVALID = 0x08328994           # original "invalid code" branch
RECEIVED_MSG_SUB = 0x083289DB       # fanfare + "received!" script subroutine

FLAG_CHARACTER_MODE = 0x945
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
TRADE_SCRIPT_ADDR = 0x095FB000

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
def op_releaseall():        return bytes([0x6B])
def op_end():               return bytes([0x02])
def op_callnative_give(fn_thumb, species, level):
    # exact idiom of the ROM's own MONO/starter gives (docs/SELECTION_MECHANISM.md)
    return (bytes([0x23]) + struct.pack("<I", fn_thumb)
            + bytes([0x00, 0x06]) + struct.pack("<HHI", species, level, 0))


def main():
    data = bytearray(ROM_IN.read_bytes())
    got = hashlib.sha1(data).hexdigest()
    if got != ROM_SHA1:
        raise SystemExit(f"ROM sha1 mismatch: {got} (expected {ROM_SHA1})")

    cm = load_charmap()
    with open(HERE / "character_mode" / "characters_manifest.json") as f:
        manifest = json.load(f)
    chars = manifest["characters"]
    assert len(chars) == NUM_CHARACTERS, len(chars)
    bitmaps = (HERE / "character_mode" / "rosters_expanded.bin").read_bytes()
    assert len(bitmaps) == NUM_CHARACTERS * BITMAP_STRIDE, len(bitmaps)

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
        sig = c["signature_id"] if c.get("has_signature") and c.get("signature_id") else c["roster_species_ids"][0]
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
                    f"-DDBG_GIVE2_SPECIES={dbg_give2}",
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
                 "CM_GiveMonNativeGated", "CM_TradeCheck"):
        assert need in syms, f"missing symbol {need}"
    assert len(shim) <= BITMAPS_ADDR - SHIM_ADDR, f"shim too big: {len(shim)}"
    print(f"shim: {len(shim)} bytes @ {SHIM_ADDR:#x}; entries: "
          + ", ".join(f"{k}={v:#x}" for k, v in syms.items() if k.startswith("CM_")))

    hook_dispatch = syms["CM_CheatDispatchHook"] | 1
    hook_gate     = syms["CM_GiveMonToPlayerGated"] | 1
    hook_native   = syms["CM_GiveMonNativeGated"] | 1
    hook_trade    = syms["CM_TradeCheck"] | 1

    # --- 2. confirm script ---
    txt_on  = enc_text("Character Mode is now active!\nOff-roster catches go to the PC.", cm)
    txt_off = enc_text("Character Mode is now off.", cm)

    # layout: [entry][act][off][txt_on][txt_off] — compute sizes first
    entry_sz = len(op_compare(0, 0) + op_goto_if(5, 0) + op_goto(0))
    # NOTE: RECEIVED_MSG_SUB is a goto-only tail (every path ends in
    # releaseall/end, target 0x083289D9 IS releaseall/end) — it never returns,
    # so everything must happen BEFORE we enter it, and we goto, not call.
    act = (op_compare(VAR_CM_STARTER, 0xFFFF) + op_goto_if(1, 0)  # ptr fixed below
           + op_delay(2) + op_loadword(0)  # txt_on ptr fixed below
           + op_callstd(4)
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
    # loadword ptr inside act: after compare(5) + goto_if(6) + delay(3), skip "0F 00"
    lw_on_off = entry_sz + 5 + 6 + 3 + 2
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
    splice(SCRIPT_ADDR, bytes(script), "script")

    # trampoline: ldr r3,[pc,#0]; bx r3; .word gate|1
    tramp = struct.pack("<HH", 0x4B00, 0x4718) + struct.pack("<I", hook_gate)
    assert TRAMPOLINE_ADDR % 4 == 0
    splice(TRAMPOLINE_ADDR, tramp, "trampoline")

    # --- 4. patches (verify-then-write) ---
    for site in (BL_SITE_CATCH, BL_SITE_GIFT):
        cur = bytes(data[site:site + 4])
        expect = thumb_bl(0x08000000 + site, GIVEMON_ADDR)
        assert cur == expect, (f"BL site {site:#x}: {cur.hex()} != {expect.hex()} "
                               "(wrong ROM or already patched)")
        data[site:site + 4] = thumb_bl(0x08000000 + site, TRAMPOLINE_ADDR)

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
          f"(wrappers @ {TRADE_SCRIPT_ADDR:#x}, {len(trade_blob)} B)")

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

    (BUILD / "codes.txt").write_text(
        "\n".join(f"{code}\t{c['character']}\tstarter={s}"
                  for code, c, s in zip(typed_codes, chars, starters)) + "\n")
    print(f"code list: {BUILD/'codes.txt'} ({len(typed_codes)} characters)")
    print("Debug codes: CMDBGOFF, CMDBGGIVE1, CMDBGGIVE2 (case-insensitive)")


if __name__ == "__main__":
    main()
