#!/usr/bin/env python3
"""The player's walk/run sprite follows the chosen character (2026-10-21).

Seaglass's design (../../Seaglass-Character-Mode docs/ROUTINE_MAP.md "Overworld
sprite"), every address re-derived from THIS binary and asserted on the base ROM
before anything is written (../game_plans/overworld_sprites.md, user 2026-10-21):
with Character Mode on, the character's own sprite is used walking and running;
bike, surf, fishing, field moves and underwater keep the stock player; no NPC or
opponent sprite changes; with the mode off nothing changes.

Lazarus differs from Seaglass in one way that matters: it has pokeemerald-
expansion's OUTFIT system (the Rotom Phone's Outfit Box). gOutfits (OUTFIT_TABLE,
15 x 0x4C) gives every outfit its own avatar ids, u16 avatarGfxIds[2][4] at +0x1C
(normal, bike, surf, underwater) then animGfxIds[2][5]. So the player's on-foot id
is one of 30 (outfit x gender), not just Brendan 0 / May 89, and all of them are
swapped (ON_FOOT_IDS), except 0x1D8 (Hylian Heroes, female), which two real map
NPCs use (map 0.113 local 50, map 9.28 local 1; scanned 2026-10-21 over all 682
maps / 4683 object templates). No map object uses any of the other 29.

  * GetObjectEventGraphicsInfo (GET_INFO, the only reader of
    gObjectEventGraphicsInfoPointers INFO_TABLE, through one literal) gets an
    8-byte entry trampoline (src/ow_sprite.c): for an on-foot id, with the mode on
    and a sprite for the character, it returns that character's graphics info;
    otherwise it replays the 8 overwritten bytes and resumes the original (r1 is
    free there). Var-driven object ids resolve INSIDE the original (after the
    entry), so a rival drawn through VAR_OBJ_GFX_ID_* never matches.
  * an info is a copy of the University outfit's male on-foot info (id 0: 16x32,
    player anims PLAYER_ANIMS, whose 24 anims decode identically to Seaglass's
    player anims: run anims 20-23 in pokeemerald order, so the sheets need no
    remap) with size, oam and subsprites for the sheet's frame size, its own
    palette tag (also its reflection tag) and its own plain 18-frame image table.
  * palettes are found by tag in sObjectEventSpritePalettes (PAL_TABLE, 104
    entries, 0x11FF terminator), read through 17 literals: copied, our tags
    0x1400+k appended before the terminator, all 17 repointed.
  * Lazarus's own player costumes go first (NATIVE): its hidden Johto / Kalos /
    Alolan Fashion outfits are Ethan & Lyra, Calem & Serena, Elio & Selene, full
    player sprites with run frames, used as-is through their own infos.

Everything lives in the base ROM's untouched all-0xFF tail (OW_CODE_ADDR,
OW_REGIONS), past every other Character Mode blob.
"""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHEETS = ROOT / "sprites" / "ow_player"
CHAR_MANIFEST = ROOT / "tools" / "character_mode" / "characters_manifest.json"

ROM_BASE = 0x08000000
GET_INFO = 0x081183B8                      # GetObjectEventGraphicsInfo
GET_INFO_ORIG = bytes.fromhex("404a94460304180c")   # ldr r2,[pc,#256]; mov ip,r2; lsls r3,r0,#16; lsrs r0,r3,#16
GET_INFO_LIT = 0x081184BC                  # the ldr's literal
GET_INFO_LIT_VALUE = 0xFE1C0000
INFO_TABLE = 0x087AC934                    # gObjectEventGraphicsInfoPointers
INFO_TABLE_REF = 0x081184C8                # its only literal
SET_GFX_ID = 0x08117C70                    # ObjectEventSetGraphicsId(objEvent, u16 id)
SET_GFX_ID_ORIG = bytes.fromhex("30b50c04240c05008480")   # ... strh r4,[r0,#4]
G_OBJECT_EVENTS = 0x0200566C               # gObjectEvents (literal at 0x08117CCC), stride 0x24
OUTFIT_TABLE = 0x085E4C38                  # gOutfits, 15 entries, stride 0x4C
OUTFIT_COUNT, OUTFIT_STRIDE = 15, 0x4C
OUTFIT_FIRST_NAME = "University Green"
NPC_USED_ON_FOOT = (0x1D8,)                # Hylian Heroes (f): two map NPCs use it
PLAYER_ANIMS = 0x087B1338
OAM_SUB = {(16, 32): (0x087B15D4, 0x087B1660), (32, 32): (0x087B15DC, 0x087B16B4)}
TEMPLATE_ID = 0                            # University Green, male, on foot
PAL_TABLE = 0x087B6704
PAL_TABLE_ENTRIES = 104
PAL_TABLE_REFS = (0x08115BD4, 0x08116538, 0x08117240, 0x0811743C, 0x08117B2C,
                  0x08117C68, 0x0811814C, 0x0811831C, 0x081186F4, 0x081187BC,
                  0x08118834, 0x08118874, 0x08118924, 0x081189E8, 0x081194E4,
                  0x081259D0, 0x081262FC)
PAL_TAG_NONE = 0x11FF
PAL_TAG_BASE = 0x1400
INFO_SIZE = 0x24
# Lazarus's own player costumes (hidden outfits): outfit index, gender.
NATIVE = {"Ethan": (10, 0), "Lyra": (10, 1), "Calem": (11, 0), "Serena": (11, 1),
          "Elio": (12, 0), "Selene": (12, 1)}
NATIVE_OUTFIT_NAMES = {10: "Johto Fashion", 11: "Kalos Fashion", 12: "Alolan Fashion"}
FLAG_CHARACTER_MODE = 0x2B0
VAR_CM_CHAR = 0x40E0
OW_CODE_ADDR = 0x09800000                  # src/ow_sprite.c
OW_CODE_MAX = 0x400
OW_REGIONS = ((0x09800400, 0x09C00000),)


def R(a):
    return a - ROM_BASE


def u32(rom, a):
    return struct.unpack_from("<I", rom, R(a))[0]


def sheets():
    return json.loads((SHEETS / "manifest.json").read_text())["characters"]


def info_ptr(rom, gid):
    return u32(rom, INFO_TABLE + 4 * gid)


def pal_entries(rom):
    return [struct.unpack_from("<IH", rom, R(PAL_TABLE) + 8 * i) for i in range(PAL_TABLE_ENTRIES + 1)]


def outfit_on_foot(rom):
    """[(outfit, gender, id)] for every outfit's on-foot (avatarGfxIds[g][0]) id."""
    out = []
    for k in range(OUTFIT_COUNT):
        e = R(OUTFIT_TABLE) + OUTFIT_STRIDE * k
        for g in (0, 1):
            out.append((k, g, struct.unpack_from("<H", rom, e + 0x1C + 8 * g)[0]))
    return out


def on_foot_ids(rom):
    return tuple(sorted(i for _, _, i in outfit_on_foot(rom) if i not in NPC_USED_ON_FOOT))


def _text(rom, a, cm):
    o, s = R(a), ""
    while rom[o] != 0xFF and len(s) < 40:
        s += cm.get(rom[o], "?")
        o += 1
    return s


def check_engine(rom):
    assert rom[R(GET_INFO):R(GET_INFO) + 8] == GET_INFO_ORIG, "GetObjectEventGraphicsInfo moved"
    assert u32(rom, GET_INFO_LIT) == GET_INFO_LIT_VALUE
    assert u32(rom, INFO_TABLE_REF) == INFO_TABLE
    assert rom[R(SET_GFX_ID):R(SET_GFX_ID) + 10] == SET_GFX_ID_ORIG, "ObjectEventSetGraphicsId moved"
    assert u32(rom, SET_GFX_ID + 0x5C) == G_OBJECT_EVENTS
    refs = [o for o in range(0, len(rom) - 3, 4) if struct.unpack_from("<I", rom, o)[0] == INFO_TABLE]
    assert refs == [R(INFO_TABLE_REF)], [hex(r) for r in refs]
    pals = pal_entries(rom)
    assert pals[-1][1] == PAL_TAG_NONE and all(t != PAL_TAG_NONE for _, t in pals[:-1])
    refs = sorted(o + ROM_BASE for o in range(0, len(rom) - 3, 4)
                  if struct.unpack_from("<I", rom, o)[0] == PAL_TABLE)
    assert tuple(refs) == PAL_TABLE_REFS, [hex(r) for r in refs]
    # outfits: every name/desc pointer valid, the first is the default outfit;
    # its male/female on-foot ids are 0 / 89 (the Brendan/May slots)
    for k in range(OUTFIT_COUNT):
        e = OUTFIT_TABLE + OUTFIT_STRIDE * k
        assert all(0x08000000 <= u32(rom, e + o) < 0x0A000000 for o in (0x0C, 0x10, 0x40, 0x44, 0x48)), k
    assert not (0x08000000 <= u32(rom, OUTFIT_TABLE + OUTFIT_STRIDE * OUTFIT_COUNT + 0x0C) < 0x0A000000)
    feet = outfit_on_foot(rom)
    assert feet[0][2] == 0 and feet[1][2] == 89, feet[:2]
    assert len({i for *_, i in feet}) == 2 * OUTFIT_COUNT
    t = rom[R(info_ptr(rom, TEMPLATE_ID)):R(info_ptr(rom, TEMPLATE_ID)) + INFO_SIZE]
    assert struct.unpack_from("<Hhh", t, 6) == (512, 16, 32)
    assert struct.unpack_from("<III", t, 0x10) == OAM_SUB[(16, 32)] + (PLAYER_ANIMS,)
    # every on-foot info is a 16x32 player sprite on the player anims
    for _, _, gid in feet:
        i = rom[R(info_ptr(rom, gid)):R(info_ptr(rom, gid)) + INFO_SIZE]
        assert struct.unpack_from("<hh", i, 8) == (16, 32) and struct.unpack_from("<I", i, 0x18)[0] == PLAYER_ANIMS, hex(gid)
    for (w, h), (oam, sub) in OAM_SUB.items():
        assert any(struct.unpack_from("<hh", rom, R(info_ptr(rom, g)) + 8) == (w, h)
                   and struct.unpack_from("<II", rom, R(info_ptr(rom, g)) + 0x10) == (oam, sub)
                   for g in range(0x1E0)), (w, h)
    for lo, hi in OW_REGIONS + ((OW_CODE_ADDR, OW_CODE_ADDR + OW_CODE_MAX),):
        assert all(b == 0xFF for b in rom[R(lo):R(hi)]), f"{lo:#x}: base not free"


class Allocator:
    def __init__(self, rom, regions):
        self.pieces = [[R(s), R(e)] for s, e in regions]
        self.rom = rom

    def alloc(self, size, align=4):
        for p in self.pieces:
            s = (p[0] + align - 1) & ~(align - 1)
            if s + size <= p[1]:
                assert all(b == 0xFF for b in self.rom[s:s + size]), f"{s:#x} not free"
                p[0] = s + size
                return s
        raise RuntimeError(f"overworld data: out of space for {size} B")


def build(rom, characters):
    """Plan every write. Returns (writes, word_patches, info_table_addr, ids_addr,
    n_ids, info_ptrs, sources): writes [(file off, bytes)], word_patches
    [(file off, old, new)], the u32[len(characters)] info-pointer table
    (0 = keep the stock sprite), the u16 on-foot id list, and
    {name: "sheet" | "native"}."""
    check_engine(rom)
    have = sheets()
    pals = pal_entries(rom)
    used_tags = {t for _, t in pals}
    tmpl = bytearray(rom[R(info_ptr(rom, TEMPLATE_ID)):R(info_ptr(rom, TEMPLATE_ID)) + INFO_SIZE])
    alloc = Allocator(rom, OW_REGIONS)
    writes, patches = [], []
    feet = {(k, g): i for k, g, i in outfit_on_foot(rom)}

    names = [c["character"] for c in characters]
    sheet_names = [n for c, n in zip(characters, names)
                   if not c.get("hidden") and n not in NATIVE and n in have]
    assert all(PAL_TAG_BASE + k not in used_tags for k in range(len(sheet_names)))

    pal_table = bytearray((len(pals) + len(sheet_names)) * 8)
    for i, (p, tag) in enumerate(pals[:-1]):
        struct.pack_into("<IHH", pal_table, i * 8, p, tag, 0)
    pal_table_off = alloc.alloc(len(pal_table))

    frame_at, infos, sources = {}, {}, {}
    for k, name in enumerate(sheet_names):
        e = have[name]
        w, h = e["width"], e["height"]
        fb = w * h // 2
        gfx = (SHEETS / f"{e['stem']}.4bpp").read_bytes()
        assert len(gfx) == 18 * fb, (name, len(gfx))
        images = bytearray()
        for f in range(18):
            fr = gfx[f * fb:(f + 1) * fb]
            if fr not in frame_at:
                frame_at[fr] = alloc.alloc(fb)
                writes.append((frame_at[fr], fr))
            images += struct.pack("<IHH", ROM_BASE + frame_at[fr], fb, 0)
        pal = (SHEETS / f"{e['stem']}.gbapal").read_bytes()
        assert len(pal) == 32, name
        pal_off = alloc.alloc(32)
        writes.append((pal_off, pal))
        tag = PAL_TAG_BASE + k
        struct.pack_into("<IHH", pal_table, (len(pals) - 1 + k) * 8, ROM_BASE + pal_off, tag, 0)
        images_off = alloc.alloc(len(images))
        writes.append((images_off, bytes(images)))
        info = bytearray(tmpl)
        oam, sub = OAM_SUB[(w, h)]
        struct.pack_into("<HHHhh", info, 2, tag, tag, fb, w, h)
        struct.pack_into("<II", info, 0x10, oam, sub)
        struct.pack_into("<I", info, 0x1C, ROM_BASE + images_off)
        info_off = alloc.alloc(INFO_SIZE)
        writes.append((info_off, bytes(info)))
        infos[name], sources[name] = ROM_BASE + info_off, "sheet"
    struct.pack_into("<IHH", pal_table, (len(pals) - 1 + len(sheet_names)) * 8,
                     pals[-1][0], PAL_TAG_NONE, 0)
    writes.append((pal_table_off, bytes(pal_table)))
    for ref in PAL_TABLE_REFS:
        patches.append((R(ref), PAL_TABLE, ROM_BASE + pal_table_off))

    for c, name in zip(characters, names):
        if name in NATIVE and not c.get("hidden"):
            infos[name], sources[name] = info_ptr(rom, feet[NATIVE[name]]), "native"
    ptrs = [0 if c.get("hidden") else infos.get(n, 0) for c, n in zip(characters, names)]
    table = struct.pack(f"<{len(ptrs)}I", *ptrs)
    table_off = alloc.alloc(len(table))
    writes.append((table_off, table))
    ids = on_foot_ids(rom)
    ids_blob = struct.pack(f"<{len(ids)}H", *ids)
    ids_off = alloc.alloc(len(ids_blob))
    writes.append((ids_off, ids_blob))
    return writes, patches, ROM_BASE + table_off, ROM_BASE + ids_off, len(ids), ptrs, sources


if __name__ == "__main__":
    rom = (ROOT / "rom" / "lazarus-v2.gba").read_bytes()
    chars = json.loads(CHAR_MANIFEST.read_text())["characters"]
    writes, patches, table, ids, nids, ptrs, sources = build(rom, chars)
    offered = sum(1 for c in chars if not c.get("hidden"))
    print(f"{sum(1 for v in sources.values() if v == 'sheet')} sheets, "
          f"{sum(1 for v in sources.values() if v == 'native')} native "
          f"({sum(1 for p in ptrs if p)}/{offered} offered); {nids} on-foot ids; "
          f"{sum(len(b) for _, b in writes):,} B in {len(writes)} writes; table @ {table:#x}")
