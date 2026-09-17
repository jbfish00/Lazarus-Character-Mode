#!/usr/bin/env python3
"""Remove the pride-flag wall decorations from Pokemon Lazarus.

The flags are TILESET ART, not overworld objects and not game text: two 8x8
tiles (a rainbow flag and a trans flag, drawn side by side) living in two
secondary tilesets, both rendered with palette slot 3 of the primary tileset at
0x08D2D1C4.  They are placed on interior walls via 9 metatiles / 18 metatile
entries, which is why they recur in many buildings across many cities.

WHY THIS PATCHES METATILES AND NOT TILE PIXELS
Tile graphics are LZ77-compressed, so repainting the pixels means decompress →
edit → recompress → relocate (the repo's only compressor is store-only and
produces a LARGER stream) → repoint the tileset struct.  The metatile arrays are
UNCOMPRESSED, so redirecting the references is an in-place, same-size byte edit
with no relocation and no new free space.  Same visible result, far less risk.

  - a flag tile referenced from the TOP layer  -> entry 0x0000 (transparent),
    so the wall already drawn in the bottom layer shows through.
  - a flag tile referenced from the BOTTOM layer -> the wall tile used by the
    partner metatile that carries the SAME flag in its top layer.  (Zero is not
    usable here: in the bottom layer tile 0 is drawn opaquely, not skipped.)

NOTHING IS HARDCODED BY ADDRESS.  The tileset table, the flag tiles and every
referencing entry are all located by content, then cross-checked against pinned
expectations, because this repo has been bitten three times by hardcoded
addresses that moved (docs/ROUTINE_MAP.md).  The base ROM is never written.

Usage: remove_pride_flags.py <in.gba> <out.gba> [--dry-run]
"""
import struct, sys, os
# lz77.py is VENDORED in this repo's own tools/ (md5 e7430c38...), resolved from
# this script's location.  It is deliberately NOT imported out of a sibling hack
# repo: check_repo_selfcontained.py exists because a cross-repo absolute path on
# the build path made this tree unbuildable from a fresh clone once already.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lz77 import decompress

LO = 0x08000000
TABLE_LO, TABLE_HI = 0xE3E200, 0xE3EB40     # the tileset table's region
FLAG_PAL_SLOT = 3
# palette-3 index -> role, read from the ROM at run time; these are the indices
# the two flags are drawn with (verified against a live screenshot of the game).
RAINBOW_SEQ = [13, 14, 10, 7, 12, 15]        # red orange yellow green lblue purple
TRANS_SEQ   = [12, 11, 9, 9, 11, 12]         # lblue pink white white pink lblue
EXPECT_TILESETS   = 94                       # whole table, compressed AND not
EXPECT_FLAG_TILES = 4                        # 2 rainbow + 2 trans, whole ROM
EXPECT_REFS       = 18
EXPECT_METATILES  = 9


def tilesets(rom):
    """Every Tileset struct in the table region, COMPRESSED OR NOT.

    ⚠️ Do NOT filter on `flags & 1` here.  bit0 is isCompressed, so requiring it
    drops the ROM's UNCOMPRESSED tilesets -- 8 of 94 in Lazarus, 8 of 75 in
    Seaglass -- and they are perfectly ordinary tilesets.  Filtering them out is
    what made the table look like "four stride-24 runs with 48/168/56 byte
    gaps": those gaps were never in the ROM, they were the rejected entries.
    The table is really TWO runs (58, then the rest after a 32 B realignment).
    A scan that drops them is silently blind to whatever art they hold.
    """
    out = []
    for o in range(TABLE_LO, TABLE_HI, 4):
        c, s = rom[o], rom[o + 1]
        if s > 1 or rom[o + 2] or rom[o + 3]:
            continue
        t, pal, mt, mta, cb = struct.unpack_from("<IIIII", rom, o + 4)
        if not all(LO <= x < LO + len(rom) for x in (t, pal, mt, mta)):
            continue
        comp = bool(c & 1)
        if comp:
            if rom[t - LO] != 0x10:
                continue
            d = int.from_bytes(rom[t - LO + 1:t - LO + 4], "little")
            if not (32 <= d <= 512 * 32 and d % 32 == 0):
                continue
        out.append(dict(off=o, sec=s, tiles=t, pal=pal, mt=mt, mta=mta,
                        comp=comp))
    return out


def tile_bytes(rom, e):
    """Raw 4bpp tile data for a tileset, decompressing only if it is compressed."""
    if e["comp"]:
        return decompress(rom[e["tiles"] - LO:])
    # Uncompressed: bounded by whichever of the sibling pointers comes next.
    t = e["tiles"]
    ends = [x for x in (e["pal"], e["mt"], e["mta"]) if x > t]
    span = (min(ends) - t) if ends else 512 * 32
    return rom[t - LO:t - LO + min(span, 512 * 32)]


def row_indices(raw, t):
    seq = []
    for y in range(8):
        idx = []
        for xb in range(4):
            b = raw[t * 32 + y * 4 + xb]
            idx += [b & 0xF, b >> 4]
        seq.append(max(set(idx), key=idx.count))
    return seq


def find_flag_tiles(rom, tss):
    """Locate flag tiles by their row-index signature (palette independent)."""
    found = []
    for e in tss:
        try:
            raw = tile_bytes(rom, e)
        except Exception:
            continue
        for t in range(len(raw) // 32):
            seq = row_indices(raw, t)
            s = "".join(f"{v:x}" for v in seq)
            if "".join(f"{v:x}" for v in RAINBOW_SEQ) in s:
                found.append((e, t, "RAINBOW"))
            elif "".join(f"{v:x}" for v in TRANS_SEQ) in s:
                found.append((e, t, "TRANS"))
    return found


def main():
    if len(sys.argv) < 3:
        print(__doc__); return 2
    src, dst = sys.argv[1], sys.argv[2]
    dry = "--dry-run" in sys.argv
    rom = bytearray(open(src, "rb").read())
    assert os.path.abspath(src) != os.path.abspath(dst), "refusing to write over the input"

    tss = tilesets(rom)
    ncomp = sum(1 for e in tss if e["comp"])
    print(f"tilesets located by content: {len(tss)} "
          f"({ncomp} compressed, {len(tss) - ncomp} uncompressed)")
    assert len(tss) >= EXPECT_TILESETS, \
        f"expected at least {EXPECT_TILESETS} tilesets, found {len(tss)} -- " \
        f"the table walk regressed; a short walk is silently blind, not empty"
    flags = find_flag_tiles(rom, tss)
    print(f"flag tiles found: {len(flags)}")
    for e, t, kind in flags:
        print(f"  {kind:7s} tileset {e['off']:#x} tiles {e['tiles']:#x} tile {t}")
    assert len(flags) == EXPECT_FLAG_TILES, \
        f"expected {EXPECT_FLAG_TILES} flag tiles, found {len(flags)} -- ROM changed, re-verify before patching"

    # group the flag tile ids per tileset, in metatile-entry addressing
    per_ts = {}
    for e, t, kind in flags:
        per_ts.setdefault(e["off"], (e, {}))[1][(512 + t) if e["sec"] else t] = kind

    edits = []          # (file_offset, old_u16, new_u16, note)
    for off, (e, want) in sorted(per_ts.items()):
        mb = e["mt"] - LO
        nmeta = max(1, min((e["mta"] - e["mt"]) // 16, 1024))
        tops, bottoms = [], []
        for m in range(nmeta):
            for slot in range(8):
                o = mb + m * 16 + slot * 2
                if o + 2 > len(rom):
                    break
                v = struct.unpack_from("<H", rom, o)[0]
                if (v & 0x3FF) in want:
                    (tops if slot >= 4 else bottoms).append((m, slot, v, o))
        # TOP layer -> transparent
        for m, slot, v, o in tops:
            edits.append((o, v, 0x0000, f"ts{off:#x} m{m} slot{slot} TOP -> transparent"))
        # BOTTOM layer -> the wall tile from the partner metatile whose TOP holds
        # the same flag.  Derived, then sanity-checked.
        topmeta = {m for m, _, _, _ in tops}
        for m, slot, v, o in bottoms:
            donors = [d for d in sorted(topmeta) if d < m]
            assert donors, f"no donor metatile before m{m} in ts{off:#x}"
            dm = donors[-1]
            wall = struct.unpack_from("<H", rom, mb + dm * 16 + slot * 2)[0]
            assert (wall & 0x3FF) not in want, \
                f"donor m{dm} slot{slot} is itself a flag tile"
            assert (wall >> 12) & 0xF != FLAG_PAL_SLOT, \
                f"donor wall tile uses the flag palette; refusing"
            assert wall != 0, f"donor m{dm} slot{slot} is empty, not a wall"
            edits.append((o, v, wall,
                          f"ts{off:#x} m{m} slot{slot} BOTTOM -> wall t{wall & 0x3FF} "
                          f"p{(wall >> 12) & 0xF} (from m{dm})"))

    print(f"\nreferences to patch: {len(edits)} across {len(set((o // 16) for o, *_ in edits))} metatiles")
    for o, old, new, note in edits:
        print(f"  {o:#09x}  {old:#06x} -> {new:#06x}   {note}")
    assert len(edits) == EXPECT_REFS, \
        f"expected {EXPECT_REFS} references, found {len(edits)}"
    assert len(set(o // 16 for o, *_ in edits)) == EXPECT_METATILES, \
        f"expected {EXPECT_METATILES} metatiles"

    if dry:
        print("\n--dry-run: nothing written"); return 0
    for o, old, new, _ in edits:
        assert struct.unpack_from("<H", rom, o)[0] == old, f"value moved at {o:#x}"
        struct.pack_into("<H", rom, o, new)
    open(dst, "wb").write(bytes(rom))
    print(f"\nwrote {dst}  ({len(edits)} entries patched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
