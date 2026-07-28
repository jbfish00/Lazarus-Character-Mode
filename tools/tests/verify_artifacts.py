#!/usr/bin/env python3
"""Independent static verification of the built Lazarus Character Mode artifacts.

Deliberately does NOT reuse tools/inject_character_mode.py's build-time
assertions — it re-derives everything from the finished artifacts, so a bug
in the injector's own bookkeeping can't hide itself:

  1. rom/lazarus-v2.gba matches rom.sha1 (all pinned addresses valid).
  2. BPS round-trip: flips-apply build/lazarus_cm.bps onto a fresh copy of
     the original -> byte-identical to build/lazarus_cm.gba.
  3. Patched ROM differs from the original ONLY inside the intended regions:
     6 free-block payloads (shim/bitmaps/codes/starters/confirm script/trade
     wrappers), the 8-byte trampoline, 2 BLs, the specials-table slot, the
     112 callnative give pointers, the branch-0 goto pointer, and the 4
     five-byte trade-junction overlays. Nothing else moved.
  4. BL patches decode (independent decoder) to the trampoline; the original
     BLs decoded to GiveMonToPlayer; the trampoline decodes to
     ldr r3,[pc]; bx r3 with a Thumb literal inside the shim.
  5. Bitmaps in-ROM == rosters_expanded.bin; every character's manifest
     roster ids are set in their own bitmap; bitmaps are per-character
     distinct and not degenerate.
  6. Codes table decodes (charmap) to independently recomputed codes for all
     179 characters — unique case-folded, no native-code clash. Starters
     table == signature (or roster[0]) and each starter is on-bitmap.
  7. Specials slot 0x222: originally the native matcher, now a Thumb pointer
     into the shim (CM_CheatDispatchHook).
  8. All 112 callnative give sites (found independently in the ORIGINAL by
     the 0x23+ptr idiom) now share one Thumb shim pointer
     (CM_GiveMonNativeGated); no un-retargeted site remains in the patched
     ROM outside our own confirm script.
  9. Confirm-script walk: branch-0 pointer retargeted from the original
     invalid-code handler to our script; every opcode of entry/activation/
     off-handler decodes, internal pointers land where expected, and both
     message texts decode via the charmap.
 10. Trade gates: original 17-byte junctions verified, overlaid gotos ->
     wrapper scripts that decode fully (copyvars, callnative CM_TradeCheck,
     refusal path, resume goto == junction+17); refusal text decodes; the
     sIngameTrades species fields are sane.
 11. Wild-encounter override (new, 2026-07-17): all 9 BL callers of
     CreateWildMon 0x0824AA54 (grass/cave, surf, rock smash, all fishing
     rods) originally targeted CreateWildMon and now target the wild
     trampoline -> CM_CreateWildMonGated; exhaustive whole-ROM BL scan
     confirms exactly 9 callers pre-patch and 0 un-retargeted callers
     post-patch (so static/scripted gifts, which never call this function,
     are untouched by construction and nothing was missed); wildmons.bin in
     ROM byte-matches the pipeline output; every entry's species is NEVER
     one of that character's legendary/mythical roster members (cross-
     checked against emit_characters.LEGENDARY_BASES directly, not
     re-derived); every family's stage windows are gapless, monotonic, and
     confined to [1,100].

Usage: verify_artifacts.py   (exit 0 = all pass)
"""
import hashlib
import json
import re
import struct
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent

ROM_IN = ROOT / "rom" / "lazarus-v2.gba"
ROM_OUT = ROOT / "build" / "lazarus_cm.gba"
BPS = ROOT / "build" / "lazarus_cm.bps"
FLIPS = ROOT / "tools" / "bin" / "flips"
CHARMAP = Path("/home/jbfish00/Documents/Pokemon Rowe Alteration/charmap.txt")

ROM_SHA1 = "7dcdc7e280bc4631487e13dd37e6e0cea04adea6"

NUM_CHARACTERS = len(__import__("json").loads((Path(__file__).parent.parent.parent / "tools" / "character_mode" / "characters_manifest.json").read_text())["characters"])  # derived (2026-07-25, Volo); was a hardcoded literal

# Engine flag bookkeeping (the 0x945 daily-sweep bug, fixed 2026-07-24).
SB1_FLAGS_OFF = 0x12E8           # SaveBlock1.flags (docs/ROUTINE_MAP.md)
TEMP_FLAGS_START, TEMP_FLAGS_END = 0x000, 0x01F
DAILY_FLAGS_START, DAILY_FLAGS_END = 0x920, 0x95F
SCR_SETFLAG, SCR_CLEARFLAG, SCR_CHECKFLAG = 0x29, 0x2A, 0x2B
NUM_SPECIES = 1561
STRIDE = 196
CODE_LEN = 11

# Data placement is PARSED out of the injector, not copied. These are choices,
# not findings, and they move whenever the character count grows -- the 238-char
# audit rebase moved five of them at once. A copy here would not fail as "the
# addresses moved": it fails as "stray modified bytes outside the intended
# regions", which reads like a corrupt build. (The RE-derived addresses below
# are findings about the ROM and stay written down.)
_INJ_SRC = (Path(__file__).parent.parent / "inject_character_mode.py").read_text()


def _inj_addr(name):
    m = re.search(r"^%s\s*=\s*(0x[0-9A-Fa-f]+)" % name, _INJ_SRC, re.M)
    if not m:
        raise SystemExit("verify_artifacts: could not parse %s out of "
                         "inject_character_mode.py" % name)
    return int(m.group(1), 16)


SHIM_ADDR = _inj_addr("SHIM_ADDR")
BITMAPS_ADDR = _inj_addr("BITMAPS_ADDR")
CODES_ADDR = _inj_addr("CODES_ADDR")
STARTERS_ADDR = _inj_addr("STARTERS_ADDR")
HIDDEN_ADDR = _inj_addr("HIDDEN_ADDR")
SCRIPT_ADDR = _inj_addr("SCRIPT_ADDR")
TRADE_SCRIPT_ADDR = _inj_addr("TRADE_SCRIPT_ADDR")
CM_MUGSHOT_ADDR = _inj_addr("CM_MUGSHOT_ADDR")   # src/character_sprite.c
WILDMONS_ADDR = _inj_addr("WILDMONS_ADDR")
LEGENDARY_ADDR = _inj_addr("LEGENDARY_ADDR")
CM_SPRITE_PTRS_ADDR = _inj_addr("CM_SPRITE_PTRS_ADDR")
CM_SPRITE_BLOBS_ADDR = _inj_addr("CM_SPRITE_BLOBS_ADDR")

TRAMPOLINE_ADDR = 0x08470A64
WILD_TRAMPOLINE_ADDR = 0x08470A6C
BL_SITES = (0x0A7BDA, 0x20D416)
GIVEMON_ADDR = 0x081C40BC
CREATEWILDMON_ADDR = 0x0824AA54
BL_SITES_WILD = (0x1036FE, 0x103876, 0x24AC24, 0x24ACF0, 0x24AD50,
                 0x24ADC8, 0x24ADF6, 0x24B4E2, 0x24B504)
SPECIALS_SLOT_222 = 0x28D47C
ORIG_DISPATCH = 0x0813F86D
GIVE_NATIVE = 0x0820DF41
BRANCH0_PTR_OFF = 0x3287D7
ORIG_INVALID = 0x08328994
RECEIVED_MSG_SUB = 0x083289DB

VAR_CM_STARTER = 0x40E4

TRADE_JUNCTIONS = (0x2B61E5, 0x2C8442, 0x2C8E00, 0x319684)
TRADE_JUNCTION_BYTES = bytes([0x19, 0x04, 0x80, 0x08, 0x80,
                              0x19, 0x05, 0x80, 0x0A, 0x80,
                              0x25, 0x00, 0x01, 0x25, 0x01, 0x01, 0x27])
TRADE_TABLE_OFF = 0xE4D578
TRADE_STRIDE = 60

NATIVE_CODES = {"9RARECANDY", "JUSTCATCH", "WORLDCHAMP", "WATCHPHAUN",
                "ILOVEALOLA", "ILOVEKALOS", "IWANTMONKE", "ILOVPALDEA",
                "NEMOSFAVE", "JUSTSHOWME", "WISHINGSTR", "GIMMENUGS",
                "IMISSJOHTO", "MASKEDOGRE", "LEGENDSZA", "HOUSESTARK",
                "DRESSUP", "HYLIANFIT", "WILDNATURE", "PORTABLEPC",
                "MOSEY", "BATTLEPASS"} | {f"MONO{t}" for t in
                ("BUG", "DARK", "DRAGN", "ELECT", "FAIRY", "FIGHT", "FIRE",
                 "FLYIN", "GHOST", "GRASS", "GROUN", "ICE", "NORML", "POISN",
                 "PSYCH", "ROCK", "STEEL", "WATER")}

failures = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def decode_bl(halfwords_bytes, site_rom_addr):
    hw1, hw2 = struct.unpack("<HH", halfwords_bytes)
    if (hw1 & 0xF800) != 0xF000 or (hw2 & 0xF800) != 0xF800:
        return None
    off = ((hw1 & 0x7FF) << 11) | (hw2 & 0x7FF)
    if off & 0x200000:
        off -= 0x400000
    return site_rom_addr + 4 + (off << 1)


def load_charmap():
    enc, dec = {}, {}
    pat = re.compile(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$")
    with open(CHARMAP, encoding="utf-8") as f:
        for line in f:
            m = pat.match(line.rstrip("\n"))
            if not m:
                continue
            ch, b = m.group(1), int(m.group(2), 16)
            if ch not in enc:
                enc[ch] = b
            # several chars share a byte -> prefer the ASCII one for decoding
            if b not in dec or (not dec[b].isascii() and ch.isascii()):
                dec[b] = ch
    return enc, dec


def code_for(display):
    n = unicodedata.normalize("NFKD", display)
    n = "".join(ch for ch in n if not unicodedata.combining(ch))
    return "".join(ch for ch in n if ch.isalnum())[:10]


def main():
    orig = ROM_IN.read_bytes()
    patched = ROM_OUT.read_bytes()
    _, dec = load_charmap()

    def text_at(rom, addr, maxlen=96):
        raw = rom[addr - 0x08000000: addr - 0x08000000 + maxlen]
        end = raw.find(0xFF)
        if end < 0:
            return None
        return "".join("\n" if b == 0xFE else dec.get(b, "?") for b in raw[:end])

    def u32(rom, off):
        return struct.unpack_from("<I", rom, off)[0]

    print("== 1. baseline ==")
    check("original ROM sha1 pinned", hashlib.sha1(orig).hexdigest() == ROM_SHA1)
    check("patched ROM same size as original", len(patched) == len(orig))

    print("== 2. BPS round-trip ==")
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "roundtrip.gba"
        r = subprocess.run([str(FLIPS), "--apply", str(BPS), str(ROM_IN), str(out)],
                           capture_output=True, text=True)
        applied = out.read_bytes() if out.exists() else b""
    check("flips applies patch cleanly", b"" != applied, r.stdout + r.stderr)
    check("round-trip byte-identical to built ROM", applied == patched)

    # independently locate the 112 callnative give sites in the ORIGINAL
    pat = struct.pack("<I", GIVE_NATIVE)
    native_sites = []
    i = orig.find(pat)
    while i != -1:
        if orig[i - 1] == 0x23:
            native_sites.append(i)
        i = orig.find(pat, i + 1)
    check("112 callnative give sites found in original", len(native_sites) == 112,
          f"found {len(native_sites)}")

    bitmaps = (ROOT / "tools" / "character_mode" / "rosters_expanded.bin").read_bytes()
    check("rosters_expanded.bin is 179 x 196", len(bitmaps) == NUM_CHARACTERS * STRIDE)
    wildmons = (ROOT / "tools" / "character_mode" / "wildmons.bin").read_bytes()
    check(f"wildmons.bin length is a multiple of {NUM_CHARACTERS}", len(wildmons) % NUM_CHARACTERS == 0)
    legendaries = (ROOT / "tools" / "character_mode" / "legendaries.bin").read_bytes()
    check(f"legendaries.bin length is a multiple of {NUM_CHARACTERS}",
          len(legendaries) % NUM_CHARACTERS == 0)
    wildmon_stride = len(wildmons) // NUM_CHARACTERS if len(wildmons) % NUM_CHARACTERS == 0 else 0

    print("== 3. diff confined to intended regions ==")

    _spr_blobs = (ROOT / "tools" / "character_mode" / "cm_sprite_blobs.bin").read_bytes() if (ROOT / "tools" / "character_mode" / "cm_sprite_blobs.bin").is_file() else b""
    _spr_offs = (ROOT / "tools" / "character_mode" / "cm_sprite_offsets.bin").read_bytes() if (ROOT / "tools" / "character_mode" / "cm_sprite_offsets.bin").is_file() else b""
    _spr_ptrs = bytearray()
    for _i in range(len(_spr_offs) // 8):
        _gof, _pof = struct.unpack_from("<II", _spr_offs, _i * 8)
        _spr_ptrs += (struct.pack("<II", 0, 0) if _gof == 0xFFFFFFFF else
                      struct.pack("<II", CM_SPRITE_BLOBS_ADDR + _gof,
                                        CM_SPRITE_BLOBS_ADDR + _pof))
    # renderer blob length: scan forward from its base to the next 0xFF run
    _m = CM_MUGSHOT_ADDR - 0x08000000
    _mend = _m
    while not all(b == 0xFF for b in patched[_mend:_mend + 32]):
        _mend += 32
    _mugshot_len = _mend - _m

    intended = [
        (SHIM_ADDR - 0x08000000, BITMAPS_ADDR - 0x08000000),
        (BITMAPS_ADDR - 0x08000000, BITMAPS_ADDR - 0x08000000 + len(bitmaps)),
        (CODES_ADDR - 0x08000000, CODES_ADDR - 0x08000000 + NUM_CHARACTERS * CODE_LEN),
        (STARTERS_ADDR - 0x08000000, STARTERS_ADDR - 0x08000000 + NUM_CHARACTERS * 2),
        (HIDDEN_ADDR - 0x08000000,
         HIDDEN_ADDR - 0x08000000 + (NUM_CHARACTERS + 7) // 8),
        (SCRIPT_ADDR - 0x08000000, TRADE_SCRIPT_ADDR - 0x08000000),
        (TRADE_SCRIPT_ADDR - 0x08000000, TRADE_SCRIPT_ADDR - 0x08000000 + 0x400),
        (WILDMONS_ADDR - 0x08000000, WILDMONS_ADDR - 0x08000000 + len(wildmons)),
        (LEGENDARY_ADDR - 0x08000000, LEGENDARY_ADDR - 0x08000000 + len(legendaries)),
        (CM_SPRITE_BLOBS_ADDR - 0x08000000, CM_SPRITE_BLOBS_ADDR - 0x08000000 + len(_spr_blobs)),
        (CM_SPRITE_PTRS_ADDR - 0x08000000, CM_SPRITE_PTRS_ADDR - 0x08000000 + len(_spr_ptrs)),
        (CM_MUGSHOT_ADDR - 0x08000000, CM_MUGSHOT_ADDR - 0x08000000 + _mugshot_len),
        (TRAMPOLINE_ADDR - 0x08000000, TRAMPOLINE_ADDR - 0x08000000 + 8),
        (WILD_TRAMPOLINE_ADDR - 0x08000000, WILD_TRAMPOLINE_ADDR - 0x08000000 + 8),
        *[(s, s + 4) for s in BL_SITES],
        *[(s, s + 4) for s in BL_SITES_WILD],
        (SPECIALS_SLOT_222, SPECIALS_SLOT_222 + 4),
        (BRANCH0_PTR_OFF, BRANCH0_PTR_OFF + 4),
        *[(s, s + 4) for s in native_sites],
        *[(j, j + 5) for j in TRADE_JUNCTIONS],
    ]
    stray = []
    CHUNK = 4096
    for base in range(0, len(orig), CHUNK):
        if orig[base:base + CHUNK] == patched[base:base + CHUNK]:
            continue
        for k in range(base, min(base + CHUNK, len(orig))):
            if orig[k] != patched[k] and not any(a <= k < b for a, b in intended):
                stray.append(k)
                if len(stray) > 5:
                    break
        if len(stray) > 5:
            break
    check("no stray modified bytes outside the intended regions",
          not stray, f"first strays at {[hex(x) for x in stray]}")

    print("== 4. BL patches + trampoline ==")
    for site in BL_SITES:
        old = decode_bl(orig[site:site + 4], 0x08000000 + site)
        check(f"BL at {site:#x} originally -> GiveMonToPlayer", old == GIVEMON_ADDR,
              f"decoded {old and hex(old)}")
        tgt = decode_bl(patched[site:site + 4], 0x08000000 + site)
        check(f"BL at {site:#x} -> trampoline", tgt == TRAMPOLINE_ADDR,
              f"decoded {tgt and hex(tgt)}")
    toff = TRAMPOLINE_ADDR - 0x08000000
    hw1, hw2 = struct.unpack_from("<HH", patched, toff)
    gate = u32(patched, toff + 4)
    check("trampoline = ldr r3,[pc]; bx r3", (hw1, hw2) == (0x4B00, 0x4718))
    check("trampoline literal is Thumb ptr into shim",
          (gate & 1) == 1 and SHIM_ADDR <= (gate & ~1) < BITMAPS_ADDR, hex(gate))
    check("shim code present at gate target",
          patched[(gate & ~1) - 0x08000000] != 0xFF)
    check("trampoline bytes were free (0xFF) in original",
          all(b == 0xFF for b in orig[toff:toff + 8]))

    # exhaustive GiveMonToPlayer caller scan — the DexNav coverage proof.
    # DexNav (and every other in-battle acquisition) can only reach the
    # player's party through a BL to GiveMonToPlayer; if the patched ROM
    # contains no such BL outside the 2 gated sites + the deliberately
    # exempt daycare caller, no bypass path exists.
    DAYCARE_SITE = 0x19FC8E
    def bl_callers(rom, target):
        sites = []
        for off in range(0, len(rom) - 3, 2):
            if (rom[off + 1] & 0xF8) == 0xF0 and (rom[off + 3] & 0xF8) == 0xF8:
                if decode_bl(rom[off:off + 4], 0x08000000 + off) == target:
                    sites.append(off)
        return sites
    orig_callers = bl_callers(orig, GIVEMON_ADDR)
    check("original ROM: exactly 3 GiveMonToPlayer BL callers",
          sorted(orig_callers) == sorted([*BL_SITES, DAYCARE_SITE]),
          f"found {[hex(x) for x in orig_callers]}")
    left = bl_callers(patched, GIVEMON_ADDR)
    check("patched ROM: only the exempt daycare caller still BLs GiveMonToPlayer "
          "(DexNav/battle funnel fully gated)", left == [DAYCARE_SITE],
          f"found {[hex(x) for x in left]}")

    print("== 5. bitmaps ==")
    boff = BITMAPS_ADDR - 0x08000000
    check("bitmaps in ROM == rosters_expanded.bin",
          patched[boff:boff + len(bitmaps)] == bitmaps)
    with open(ROOT / "tools" / "character_mode" / "characters_manifest.json") as f:
        manifest = json.load(f)
    chars = manifest["characters"]
    # NOT `len(chars) == NUM_CHARACTERS` -- NUM_CHARACTERS is DERIVED from this
    # very manifest at the top of this file, so that comparison is a tautology
    # that cannot fail. What is worth checking is that nothing in the build
    # chain has REINTRODUCED a hardcoded count: the injector and both C shims
    # must derive it (the injector from the manifest, the shims from the
    # injector's -DNUM_CHARACTERS). A stale literal is this workspace's most
    # repeated bug and never presents as a count error.
    check("injector derives NUM_CHARACTERS from the manifest",
          re.search(r"^NUM_CHARACTERS\s*=\s*\d+", _INJ_SRC, re.M) is None
          and "_derive_num_characters()" in _INJ_SRC)
    for _src in ("character_mode.c", "character_sprite.c"):
        _txt = (ROOT / "src" / _src).read_text()
        check(f"{_src} takes NUM_CHARACTERS from the injector",
              re.search(r"^#define\s+NUM_CHARACTERS\s+\d+", _txt, re.M) is None
              and "#ifndef NUM_CHARACTERS" in _txt)
    check(f"injector passes -DNUM_CHARACTERS to both shims",
          _INJ_SRC.count('f"-DNUM_CHARACTERS={NUM_CHARACTERS}"') == 2)

    # --- the playability threshold, read back out of the built ROM ---------
    with open(ROOT / "tools" / "character_mode" / "character_drops.json") as f:
        _drops = set(json.load(f)["unselectable"])
    _hoff = HIDDEN_ADDR - 0x08000000
    _hbits = patched[_hoff:_hoff + (NUM_CHARACTERS + 7) // 8]
    _rom_hidden = {chars[i]["character"] for i in range(NUM_CHARACTERS)
                   if _hbits[i >> 3] & (1 << (i & 7))}
    _man_hidden = {c["character"] for c in chars if c.get("hidden")}
    check(f"hidden bitmap in ROM matches the manifest ({len(_man_hidden)} hidden)",
          _rom_hidden == _man_hidden)
    check("hidden bitmap in ROM matches character_drops.json",
          {re.sub(r"\s*\(anime\)$", "", c) for c in _rom_hidden} == _drops)
    # Hiding must not disable enforcement: a save already on one of these
    # characters keeps loading, and its bitmap must still be there to enforce.
    check("hidden characters still carry a non-empty allow-bitmap where their "
          "roster is non-empty",
          all(any(patched[boff + i * STRIDE:boff + (i + 1) * STRIDE])
              for i, c in enumerate(chars)
              if c.get("hidden") and c["roster_species_ids"]))

    def bit(ci, sp):
        return (patched[boff + ci * STRIDE + (sp >> 3)] >> (sp & 7)) & 1

    bad_roster = 0
    degenerate = 0
    for ci, c in enumerate(chars):
        ids = c["roster_species_ids"]
        if not all(0 < sp < NUM_SPECIES and bit(ci, sp) for sp in ids):
            bad_roster += 1
            if bad_roster <= 3:
                miss = [sp for sp in ids if not (0 < sp < NUM_SPECIES and bit(ci, sp))]
                print(f"    roster bits missing [{ci}] {c['character']}: {miss}")
        pop = sum(bin(b).count("1")
                  for b in patched[boff + ci * STRIDE: boff + (ci + 1) * STRIDE])
        if pop < len(ids) or pop > NUM_SPECIES // 2:
            degenerate += 1
    check("every character's manifest roster ids set in own bitmap (in ROM)",
          bad_roster == 0, f"{bad_roster} bad")
    check("no degenerate bitmaps (empty / half-full)", degenerate == 0, str(degenerate))
    distinct = len({bytes(patched[boff + i * STRIDE: boff + (i + 1) * STRIDE])
                    for i in range(NUM_CHARACTERS)})
    check("bitmaps mostly distinct across characters", distinct > NUM_CHARACTERS * 3 // 4,
          f"only {distinct} distinct")

    print("== 6. codes + starters ==")
    coff = CODES_ADDR - 0x08000000
    soff = STARTERS_ADDR - 0x08000000
    bad_code = bad_starter = 0
    seen = set()
    for ci, c in enumerate(chars):
        raw = patched[coff + ci * CODE_LEN: coff + (ci + 1) * CODE_LEN]
        end = raw.find(0xFF)
        decoded = "".join(dec.get(b, "?") for b in (raw[:end] if end >= 0 else raw))
        want = code_for(c["character"])
        key = decoded.upper()
        ok = (decoded == want and 1 <= len(decoded) <= 10
              and key not in seen and key not in NATIVE_CODES)
        seen.add(key)
        if not ok:
            bad_code += 1
            if bad_code <= 3:
                print(f"    code mismatch [{ci}] {c['character']}: {decoded!r} != {want!r}")
        starter = struct.unpack_from("<H", patched, soff + ci * 2)[0]
        if c.get("has_signature") and c.get("signature_id"):
            sig = c["signature_id"]
        elif c["roster_species_ids"]:
            sig = c["roster_species_ids"][0]
        else:
            # Empty roster: the record exists only to hold its index stable and
            # the threshold hides it, so the injector writes SPECIES_NONE, which
            # is correctly OFF the bitmap. Checking `bit(ci, 0)` would demand
            # the opposite.
            if starter != 0 or not c.get("hidden"):
                bad_starter += 1
                print(f"    empty roster [{ci}] {c['character']}: starter "
                      f"{starter} (want 0), hidden={c.get('hidden')}")
            continue
        if starter != sig or not bit(ci, starter):
            bad_starter += 1
            if bad_starter <= 3:
                print(f"    starter mismatch [{ci}] {c['character']}: "
                      f"{starter} (want {sig}, on-bitmap={bit(ci, starter)})")
    check("all codes decode to recomputed names, unique, no native clash",
          bad_code == 0, f"{bad_code} bad")
    check("all starters == signature/roster[0] and on own bitmap",
          bad_starter == 0, f"{bad_starter} bad")

    print("== 7. specials slot (selection hook) ==")
    check("slot 0x222 originally -> native matcher",
          u32(orig, SPECIALS_SLOT_222) == ORIG_DISPATCH)
    disp = u32(patched, SPECIALS_SLOT_222)
    check("slot 0x222 -> Thumb ptr into shim (CM_CheatDispatchHook)",
          (disp & 1) == 1 and SHIM_ADDR <= (disp & ~1) < BITMAPS_ADDR, hex(disp))

    print("== 8. callnative give sites ==")
    vals = {u32(patched, s) for s in native_sites}
    hook_native = vals.pop() if len(vals) == 1 else None
    check("all 112 sites share one retargeted pointer", hook_native is not None,
          f"{len(vals) + 1} distinct values")
    if hook_native is not None:
        check("retargeted give ptr is Thumb ptr into shim",
              (hook_native & 1) == 1 and SHIM_ADDR <= (hook_native & ~1) < BITMAPS_ADDR,
              hex(hook_native))
        leftovers = []
        i = patched.find(pat)
        while i != -1:
            if patched[i - 1] == 0x23:
                leftovers.append(i)
            i = patched.find(pat, i + 1)
        check("no un-retargeted callnative give site remains", not leftovers,
              f"at {[hex(x) for x in leftovers]}")

    print("== 9. confirm script walk ==")
    check("branch-0 ptr originally -> invalid-code handler",
          u32(orig, BRANCH0_PTR_OFF) == ORIG_INVALID)
    check("branch-0 ptr retargeted to confirm script",
          u32(patched, BRANCH0_PTR_OFF) == SCRIPT_ADDR)

    p = SCRIPT_ADDR - 0x08000000

    def expect(desc, blob):
        nonlocal p
        got = patched[p:p + len(blob)]
        ok = got == blob
        if not ok:
            check(f"script: {desc}", False, f"@ +{p - (SCRIPT_ADDR - 0x08000000):#x}: "
                  f"{bytes(got).hex()} != {blob.hex()}")
        p += len(blob)
        return ok

    def take_u32():
        nonlocal p
        v = u32(patched, p)
        p += 4
        return v

    ok = True
    # entry: compare VAR_CM_STARTER,0; goto_if NE -> act; goto ORIG_INVALID
    ok &= expect("compare(VAR_CM_STARTER, 0)",
                 bytes([0x21]) + struct.pack("<HH", VAR_CM_STARTER, 0))
    ok &= expect("goto_if 5 (NE)", bytes([0x06, 5]))
    act_addr = take_u32()
    ok &= expect("goto", bytes([0x05]))
    ok &= take_u32() == ORIG_INVALID
    check("entry block decodes (incl. fallthrough -> orig invalid handler)",
          ok and act_addr == 0x08000000 + p)

    # activation handler: mode msgbox FIRST, marker consumed BEFORE the give,
    # then goto (never call) into the ROM's own received-mon tail — the tail
    # ends every path with releaseall/end and cannot return.
    ok = expect("compare(VAR_CM_STARTER, 0xFFFF)",
                bytes([0x21]) + struct.pack("<HH", VAR_CM_STARTER, 0xFFFF))
    ok &= expect("goto_if 1 (EQ)", bytes([0x06, 1]))
    off_addr = take_u32()
    ok &= expect("delay", bytes([0x28]) + struct.pack("<H", 2))
    # The mugshot bracket: show before the message, hide after callstd 4
    # returns (it blocks until A). Operands are checked below rather than here,
    # since nothing in this file should know the renderer's internal layout.
    ok &= expect("callnative show-mugshot", bytes([0x23]))
    show_mugshot = take_u32()
    ok &= expect("loadword", bytes([0x0F, 0x00]))
    txt_on_addr = take_u32()
    ok &= expect("callstd 4 (mode msgbox)", bytes([0x09, 4]))
    ok &= expect("callnative hide-mugshot", bytes([0x23]))
    hide_mugshot = take_u32()
    ok &= expect("copyvar(0x8000, VAR_CM_STARTER)",
                 bytes([0x19]) + struct.pack("<HH", 0x8000, VAR_CM_STARTER))
    ok &= expect("bufferspecies(0, var 0x8000)",
                 bytes([0x7D, 0x00]) + struct.pack("<H", 0x8000))
    ok &= expect("setvar(0x4001, 0x8000)",
                 bytes([0x16]) + struct.pack("<HH", 0x4001, 0x8000))
    ok &= expect("setvar(VAR_CM_STARTER, 0) before the give",
                 bytes([0x16]) + struct.pack("<HH", VAR_CM_STARTER, 0))
    ok &= expect("callnative give", bytes([0x23]))
    give_ptr = take_u32()
    ok &= give_ptr == hook_native
    ok &= expect("give args (species=var 0x8000, L5)",
                 bytes([0x00, 0x06]) + struct.pack("<HHI", 0x8000, 5, 0))
    ok &= expect("goto received-msg tail",
                 bytes([0x05]) + struct.pack("<I", RECEIVED_MSG_SUB))
    check("activation handler decodes (incl. give via shim ptr)", ok)

    # off handler
    ok = (0x08000000 + p) == off_addr
    ok &= expect("off: setvar(VAR_CM_STARTER, 0)",
                 bytes([0x16]) + struct.pack("<HH", VAR_CM_STARTER, 0))
    ok &= expect("off: delay", bytes([0x28]) + struct.pack("<H", 2))
    ok &= expect("off: loadword", bytes([0x0F, 0x00]))
    txt_off_addr = take_u32()
    ok &= expect("off: callstd 4; releaseall; end", bytes([0x09, 4, 0x6B, 0x02]))
    check("off handler decodes at goto_if target", ok)

    t_on = text_at(patched, txt_on_addr)
    t_off = text_at(patched, txt_off_addr)
    check("activation text decodes",
          t_on == "Character Mode is now active!\nOff-roster catches go to the PC.",
          repr(t_on))
    check("off text decodes", t_off == "Character Mode is now off.", repr(t_off))

    print("== 10. trade gates ==")
    for k, j in enumerate(TRADE_JUNCTIONS):
        check(f"junction {k} original bytes intact",
              orig[j:j + 17] == TRADE_JUNCTION_BYTES)
    wrapper_addrs = []
    for k, j in enumerate(TRADE_JUNCTIONS):
        got = patched[j:j + 5]
        ok = got[0] == 0x05
        wa = u32(patched, j + 1) if ok else 0
        ok = ok and TRADE_SCRIPT_ADDR <= wa < TRADE_SCRIPT_ADDR + 0x400
        check(f"junction {k} overlaid with goto wrapper", ok, bytes(got).hex())
        check(f"junction {k} tail untouched",
              patched[j + 5:j + 17] == TRADE_JUNCTION_BYTES[5:])
        wrapper_addrs.append(wa)

    hook_trade = None
    for k, (j, wa) in enumerate(zip(TRADE_JUNCTIONS, wrapper_addrs)):
        w = wa - 0x08000000
        ok = patched[w:w + 10] == TRADE_JUNCTION_BYTES[:10]  # the 2 copyvars
        ok = ok and patched[w + 10] == 0x23
        tptr = u32(patched, w + 11)
        if hook_trade is None:
            hook_trade = tptr
        ok = ok and tptr == hook_trade and (tptr & 1) == 1 \
            and SHIM_ADDR <= (tptr & ~1) < BITMAPS_ADDR
        ok = ok and patched[w + 15] == 0x21 \
            and struct.unpack_from("<HH", patched, w + 16) == (0x800D, 0)
        ok = ok and patched[w + 20] == 0x06 and patched[w + 21] == 1
        refuse_addr = u32(patched, w + 22)
        ok = ok and refuse_addr == TRADE_SCRIPT_ADDR
        ok = ok and patched[w + 26:w + 33] == TRADE_JUNCTION_BYTES[10:]  # specials+waitstate
        ok = ok and patched[w + 33] == 0x05 \
            and u32(patched, w + 34) == 0x08000000 + j + 17
        check(f"wrapper {k} decodes (check, refuse-on-0, resume at junction+17)", ok)

    r = TRADE_SCRIPT_ADDR - 0x08000000
    ok = patched[r:r + 3] == bytes([0x28]) + struct.pack("<H", 2)
    ok = ok and patched[r + 3:r + 5] == bytes([0x0F, 0x00])
    refuse_txt_addr = u32(patched, r + 5)
    ok = ok and patched[r + 9:r + 13] == bytes([0x09, 4, 0x6C, 0x02])
    msg = text_at(patched, refuse_txt_addr) if ok else None
    check("refusal script decodes", ok)
    check("refusal text decodes",
          msg == "Character Mode:\nthis trade is not in your roster.", repr(msg))

    n_bad_species = 0
    for k in range(4):
        sp = struct.unpack_from("<H", orig, TRADE_TABLE_OFF + k * TRADE_STRIDE + 14)[0]
        if not (0 < sp < NUM_SPECIES):
            n_bad_species += 1
    check("sIngameTrades received-species fields sane (4 trades)", n_bad_species == 0)

    print("== 11. wild-encounter override ==")
    for site in BL_SITES_WILD:
        old = decode_bl(orig[site:site + 4], 0x08000000 + site)
        check(f"wild BL at {site:#x} originally -> CreateWildMon", old == CREATEWILDMON_ADDR,
              f"decoded {old and hex(old)}")
        tgt = decode_bl(patched[site:site + 4], 0x08000000 + site)
        check(f"wild BL at {site:#x} -> wild trampoline", tgt == WILD_TRAMPOLINE_ADDR,
              f"decoded {tgt and hex(tgt)}")
    wtoff = WILD_TRAMPOLINE_ADDR - 0x08000000
    whw1, whw2 = struct.unpack_from("<HH", patched, wtoff)
    hook_wild = u32(patched, wtoff + 4)
    check("wild trampoline = ldr r3,[pc]; bx r3", (whw1, whw2) == (0x4B00, 0x4718))
    check("wild trampoline literal is Thumb ptr into shim",
          (hook_wild & 1) == 1 and SHIM_ADDR <= (hook_wild & ~1) < BITMAPS_ADDR, hex(hook_wild))
    check("shim code present at wild gate target",
          patched[(hook_wild & ~1) - 0x08000000] != 0xFF)
    check("wild trampoline bytes were free (0xFF) in original",
          all(b == 0xFF for b in orig[wtoff:wtoff + 8]))

    # exhaustive CreateWildMon caller scan: every random-roll wild table
    # (land/cave, surf, rock smash, fishing) funnels species+level through
    # this one function; static/scripted gifts never call it, so gating it
    # exclusively cannot touch them, and exhaustion proves no 10th site was
    # missed.
    orig_wild_callers = bl_callers(orig, CREATEWILDMON_ADDR)
    check("original ROM: exactly 9 CreateWildMon BL callers",
          sorted(orig_wild_callers) == sorted(BL_SITES_WILD),
          f"found {[hex(x) for x in orig_wild_callers]}")
    left_wild = bl_callers(patched, CREATEWILDMON_ADDR)
    check("patched ROM: no un-retargeted CreateWildMon BL caller remains",
          not left_wild, f"found {[hex(x) for x in left_wild]}")

    check("wildmons.bin in ROM == pipeline output",
          patched[WILDMONS_ADDR - 0x08000000: WILDMONS_ADDR - 0x08000000 + len(wildmons)]
          == wildmons)

    # ---- the 1% legendary pool (game_plans/legendary_encounters.md) ---------
    print("== the 1% legendary wild pool ==")

    check("legendaries.bin in ROM == pipeline output",
          patched[LEGENDARY_ADDR - 0x08000000: LEGENDARY_ADDR - 0x08000000 + len(legendaries)]
          == legendaries)

    leg_stride = len(legendaries) // NUM_CHARACTERS

    # THE CHECK SEAGLASS DOES NOT HAVE. Its WILDPOOL_STRIDE is 104 in the shim
    # and 176 in the data, so every character but the first reads a misaligned
    # slice of someone else's pool -- and it shipped precisely because its
    # verifier validates the .bin and never the COMPILED constant. The shim
    # materialises LEGENDARY_ADDR in a literal pool, so its presence proves the
    # shim in the ROM was built against the address the data was spliced to.
    _shim = (ROOT / "build" / "character_mode.bin").read_bytes()
    check("the compiled shim carries the LEGENDARY_ADDR literal "
          "(shim and data agree on placement)",
          struct.pack("<I", LEGENDARY_ADDR) in _shim,
          f"{LEGENDARY_ADDR:#x} not found in the {len(_shim)} B shim")

    # Every entry has to decode, or the shim walks garbage.
    _bad, _fams, _species = [], 0, set()
    for c in range(NUM_CHARACTERS):
        base = c * leg_stride
        for off in range(0, leg_stride, 4):
            raw = int.from_bytes(legendaries[base + off: base + off + 2], "little")
            lo, hi = legendaries[base + off + 2], legendaries[base + off + 3]
            if raw == 0:
                # the rest of this character's region must be zero padding
                if any(legendaries[base + off: base + leg_stride]):
                    _bad.append(f"char {c}: data after terminator")
                break
            sp = raw & 0x7FFF
            if raw & 0x8000:
                _fams += 1
            if not (0 < sp < NUM_SPECIES):
                _bad.append(f"char {c}: species {sp} out of range")
            if not (1 <= lo <= hi <= 100):
                _bad.append(f"char {c}: bad level window {lo}-{hi}")
            _species.add(sp)
    check("every legendary entry decodes (species in range, lo<=hi, padded)",
          not _bad, "; ".join(_bad[:5]))
    check("the legendary pool is not empty", _fams > 0)

    # The pool must describe exactly the manifest's legendary slice -- the same
    # cross-check emit_legendaries.py makes, re-made here against the ROM.
    _man = __import__("json").loads(
        (ROOT / "tools" / "character_mode" / "characters_manifest.json").read_text())
    _mismatch = []
    for c, rec in enumerate(_man["characters"]):
        has_blob = any(legendaries[c * leg_stride: c * leg_stride + 2])
        has_man = bool(rec.get("roster_species_ids", [])[rec.get("starter_count", 0):])
        if has_blob != has_man:
            _mismatch.append(rec.get("character", str(c)))
    check("blob agrees with the manifest on who has a legendary",
          not _mismatch, f"disagree: {_mismatch[:5]}")

    # Every species in the pool must be one emit_characters calls legendary --
    # otherwise the 1% roll is quietly handing out ordinary Pokemon.
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location(
        "_ec", ROOT / "tools" / "character_mode" / "emit_characters.py")
    _ec = _ilu.module_from_spec(_spec)
    try:
        _spec.loader.exec_module(_ec)
    except SystemExit:
        pass
    _rom_tbl = __import__("json").loads(
        (ROOT / "tools" / "character_mode" / "rom_species_table.json").read_text())["species"]
    _legend_names = {n.replace("SPECIES_", "").replace("_", "").lower()
                     for n in getattr(_ec, "LEGENDARY_BASES", set())}
    check("emit_characters.LEGENDARY_BASES extracted (not silently empty)",
          len(_legend_names) > 90, f"got {len(_legend_names)}")
    _not_legend = [sp for sp in sorted(_species)
                   if _rom_tbl.get(str(sp), "?").replace(" ", "").replace("-", "").replace(".", "").lower()
                   not in _legend_names]
    check("every species in the legendary pool is actually a legendary",
          not _not_legend,
          f"non-legendary: {[(sp, _rom_tbl.get(str(sp))) for sp in _not_legend[:5]]}")

    sys.path.insert(0, str(ROOT / "tools" / "character_mode"))
    import emit_characters  # noqa: E402
    LEGENDARY_BASES = emit_characters.LEGENDARY_BASES
    sp_table = json.loads((ROOT / "tools" / "character_mode" / "rom_species_table.json").read_text())["species"]
    from map_species import load_donor, MACRO_FORM_CONST_OVERRIDES  # noqa: E402
    name_to_const, _ = load_donor()
    for nm, c in MACRO_FORM_CONST_OVERRIDES.items():
        name_to_const.setdefault(nm, c)
    const_by_norm = {}
    for nm, c in name_to_const.items():
        n = unicodedata.normalize("NFD", nm)
        n = "".join(ch for ch in n if unicodedata.category(ch) != "Mn")
        n = re.sub(r"[^a-z0-9]", "", n.lower())
        const_by_norm.setdefault(n, c)

    def const_for_species_id(sid):
        nm = sp_table.get(str(sid))
        if not nm:
            return None
        n = unicodedata.normalize("NFD", nm)
        n = "".join(ch for ch in n if unicodedata.category(ch) != "Mn")
        n = re.sub(r"[^a-z0-9]", "", n.lower())
        return const_by_norm.get(n)

    legendary_leaks = []
    window_bad = 0
    zero_entry_chars = 0
    # A zero stride means wildmons.bin is malformed. Guarding the scan on it
    # made the two guarantees below ("no legendary anywhere", "windows gapless")
    # report success having examined ZERO bytes. Fail loudly instead, then skip.
    check("wildmon stride is usable (a 0 stride would silently void the two "
          "wild-encounter guarantees below)", wildmon_stride > 0, str(wildmon_stride))
    if wildmon_stride:
        woff = WILDMONS_ADDR - 0x08000000
        for ci in range(NUM_CHARACTERS):
            base = woff + ci * wildmon_stride
            i = 0
            n_entries = 0
            fam_lo = fam_hi = None
            while i + 4 <= wildmon_stride:
                raw, lo, hi = struct.unpack_from("<HBB", patched, base + i)
                if raw == 0:
                    break
                n_entries += 1
                sid = raw & 0x7FFF
                is_start = bool(raw & 0x8000)
                const = const_for_species_id(sid)
                if const and const in LEGENDARY_BASES:
                    legendary_leaks.append((ci, sid))
                if not (1 <= lo <= hi <= 100):
                    window_bad += 1
                elif is_start:
                    fam_lo, fam_hi = lo, hi
                else:
                    if fam_hi is not None and lo != fam_hi + 1:
                        window_bad += 1
                    fam_lo, fam_hi = lo, hi
                i += 4
            if n_entries == 0:
                zero_entry_chars += 1
    check("no legendary/mythical species anywhere in wildmons.bin",
          not legendary_leaks, f"{len(legendary_leaks)} leaks, e.g. {legendary_leaks[:5]}")
    check("every family's stage windows are gapless/monotonic within [1,100]",
          window_bad == 0, f"{window_bad} bad windows")
    if zero_entry_chars:
        print(f"    NOTE: {zero_entry_chars} characters have 0 wild-override entries "
              f"(override no-ops for them) — expected for all-legendary/unresolved rosters")

    distinct_hooks = {gate & ~1, (disp & ~1),
                      (hook_native or 0) & ~1, (hook_trade or 0) & ~1, hook_wild & ~1}
    check("5 shim entry points are distinct", len(distinct_hooks) == 5,
          str([hex(x) for x in distinct_hooks]))

    print("\n== CM flag id survives the engine's sweeps ==")
    # ClearTempFieldEventData() wipes flags 0x000-0x01F on every map load;
    # ClearDailyFlags() wipes 0x920-0x95F on every RTC day rollover. A flag in
    # either range silently deactivates Character Mode mid-save -- that was the
    # 0x945 bug (fixed 2026-07-24; Seaglass had it too). Re-derived from the
    # ROM here rather than trusted as a constant.
    src = (ROOT / "src" / "character_mode.c").read_text()
    m = re.search(r"#define\s+FLAG_CHARACTER_MODE\s+(0x[0-9A-Fa-f]+)", src)
    check("FLAG_CHARACTER_MODE parsed from src/character_mode.c", m is not None)
    flag = int(m.group(1), 16) if m else -1
    check(f"flag {flag:#x} outside the temp-flag sweep (0x0-0x1f)",
          not (TEMP_FLAGS_START <= flag <= TEMP_FLAGS_END))
    check(f"flag {flag:#x} outside the daily-flag sweep (0x920-0x95f)",
          not (DAILY_FLAGS_START <= flag <= DAILY_FLAGS_END))
    # ClearDailyFlags: `ldr r0,[gSaveBlock1Ptr]; ldr r3,=off; mov ip,r3;
    # push {lr}; movs r2,#8; movs r1,#0; add r0,ip; bl memset`.
    sig = bytes.fromhex("9c4600b5082200216044")
    i = orig.find(sig)
    check("ClearDailyFlags located in the original ROM", i != -1)
    if i != -1:
        swept = struct.unpack_from("<I", orig, i + 22)[0]
        check(f"ClearDailyFlags wipes SB1+{swept:#x} == flags[{DAILY_FLAGS_START:#x}] (8 B); "
              f"our flag byte is SB1+{SB1_FLAGS_OFF + flag // 8:#x}",
              swept == SB1_FLAGS_OFF + DAILY_FLAGS_START // 8)
    refs = sum(orig.count(bytes([op]) + struct.pack("<H", flag))
               for op in (SCR_SETFLAG, SCR_CLEARFLAG, SCR_CHECKFLAG))
    check(f"no script setflag/clearflag/checkflag references flag {flag:#x}", refs == 0, str(refs))

    print("\n== mugshot renderer (Phase 3 render surface) ==")
    mb = ROOT / "build" / "character_sprite.bin"
    if mb.is_file():
        blob = mb.read_bytes()
        check("renderer blob in ROM == build/character_sprite.bin",
              patched[_m:_m + len(blob)] == blob, f"{len(blob)} bytes")
    check("renderer starts with push {..,lr}", patched[_m + 1] == 0xB5)

    # The two callnative operands the confirm script names are re-derived here
    # from the ROM alone -- no build artifact says what they should be.
    check("mugshot callnative operands are Thumb pointers into the renderer",
          all(a & 1 and CM_MUGSHOT_ADDR <= (a & ~1) < CM_MUGSHOT_ADDR + _mugshot_len
              for a in (show_mugshot, hide_mugshot)),
          f"show={show_mugshot:#x} hide={hide_mugshot:#x} "
          f"blob=[{CM_MUGSHOT_ADDR:#x},{CM_MUGSHOT_ADDR + _mugshot_len:#x})")
    check("show and hide are distinct entry points", show_mugshot != hide_mugshot,
          f"both {show_mugshot:#x}")

    # Re-locate the SpriteTemplate in the ROM and check every pointer it hands
    # the engine. A template that assembles cleanly but names a wrong address
    # draws garbage rather than crashing, so it is worth pinning here.
    GDUMMY_ANIM, GDUMMY_AFFINE = 0x08E68F18, 0x08E68F1C
    SPRITE_CB_DUMMY = 0x08004141
    tmpl = None
    for o in range(_m, _mend - 24, 4):
        w = struct.unpack_from("<5I", patched, o + 4)
        if w[1] == GDUMMY_ANIM and w[3] == GDUMMY_AFFINE and w[4] == SPRITE_CB_DUMMY:
            tmpl = o
            break
    check("SpriteTemplate located in the renderer blob", tmpl is not None)
    if tmpl is not None:
        tile_tag, pal_tag = struct.unpack_from("<HH", patched, tmpl)
        oam_ptr, _a, images, _b, _c = struct.unpack_from("<5I", patched, tmpl + 4)
        check("template tile/palette tags are distinct and non-TAG_NONE",
              tile_tag != pal_tag and 0xFFFF not in (tile_tag, pal_tag),
              f"{tile_tag:#x}/{pal_tag:#x}")
        check("template images == NULL (required when tileTag != TAG_NONE)",
              images == 0, hex(images))
        check("template oam pointer lands inside the renderer blob",
              CM_MUGSHOT_ADDR <= oam_ptr < CM_MUGSHOT_ADDR + _mugshot_len, hex(oam_ptr))
        if CM_MUGSHOT_ADDR <= oam_ptr < CM_MUGSHOT_ADDR + _mugshot_len:
            attr0, attr1, attr2, _d = struct.unpack_from("<4H", patched,
                                                         oam_ptr - 0x08000000)
            # 64x64 = square shape (attr0 bits 14-15 == 0) + size 3 (attr1 bits
            # 14-15 == 3), 4bpp, priority 0.
            check("OAM describes a 64x64 4bpp square sprite at priority 0",
                  (attr0 >> 14) == 0 and ((attr0 >> 13) & 1) == 0
                  and (attr1 >> 14) == 3 and ((attr2 >> 10) & 3) == 0,
                  f"attr0={attr0:#06x} attr1={attr1:#06x} attr2={attr2:#06x}")

    print(f"\n{'ALL PASS' if not failures else 'FAILURES: ' + ', '.join(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
