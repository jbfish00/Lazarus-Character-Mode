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

NUM_CHARACTERS = 179
NUM_SPECIES = 1561
STRIDE = 196
CODE_LEN = 11

SHIM_ADDR = 0x095F1000
BITMAPS_ADDR = 0x095F1800
CODES_ADDR = 0x095FA200
STARTERS_ADDR = 0x095FAA00
SCRIPT_ADDR = 0x095FAC00
TRADE_SCRIPT_ADDR = 0x095FB000
WILDMONS_ADDR = 0x095FC000

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
    check("wildmons.bin length is a multiple of 179", len(wildmons) % NUM_CHARACTERS == 0)
    wildmon_stride = len(wildmons) // NUM_CHARACTERS if len(wildmons) % NUM_CHARACTERS == 0 else 0

    print("== 3. diff confined to intended regions ==")
    intended = [
        (SHIM_ADDR - 0x08000000, BITMAPS_ADDR - 0x08000000),
        (BITMAPS_ADDR - 0x08000000, BITMAPS_ADDR - 0x08000000 + len(bitmaps)),
        (CODES_ADDR - 0x08000000, CODES_ADDR - 0x08000000 + NUM_CHARACTERS * CODE_LEN),
        (STARTERS_ADDR - 0x08000000, STARTERS_ADDR - 0x08000000 + NUM_CHARACTERS * 2),
        (SCRIPT_ADDR - 0x08000000, TRADE_SCRIPT_ADDR - 0x08000000),
        (TRADE_SCRIPT_ADDR - 0x08000000, TRADE_SCRIPT_ADDR - 0x08000000 + 0x400),
        (WILDMONS_ADDR - 0x08000000, WILDMONS_ADDR - 0x08000000 + len(wildmons)),
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
    check("179 characters in manifest", len(chars) == NUM_CHARACTERS, str(len(chars)))

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
        sig = (c["signature_id"] if c.get("has_signature") and c.get("signature_id")
               else c["roster_species_ids"][0])
        if starter != sig or not bit(ci, starter):
            bad_starter += 1
            if bad_starter <= 3:
                print(f"    starter mismatch [{ci}] {c['character']}: "
                      f"{starter} (want {sig}, on-bitmap={bit(ci, starter)})")
    check("all 179 codes decode to recomputed names, unique, no native clash",
          bad_code == 0, f"{bad_code} bad")
    check("all 179 starters == signature/roster[0] and on own bitmap",
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
    ok &= expect("loadword", bytes([0x0F, 0x00]))
    txt_on_addr = take_u32()
    ok &= expect("callstd 4 (mode msgbox)", bytes([0x09, 4]))
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

    print(f"\n{'ALL PASS' if not failures else 'FAILURES: ' + ', '.join(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
