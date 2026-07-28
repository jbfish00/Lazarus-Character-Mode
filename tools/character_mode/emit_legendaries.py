#!/usr/bin/env python3
"""Emit legendaries.bin -- the 1% legendary wild-encounter pool, per character.

Spec: ../../../Character Hacks/game_plans/legendary_encounters.md (design locked
by the user 2026-07-26; shipped in Radical Red, Unbound and ROWE).

This is the exact mirror of emit_wildmons.py, with one difference: where that
script builds from `roster_species_ids[0:starter_count]` -- the NON-legendary
slice -- this one builds from `[starter_count:]`, the legendary/mythical slice
that emit_characters.py's LEGENDARY_BASES filter puts at the tail.

Deliberately a SEPARATE script rather than a flag on emit_wildmons.py: that file
is being edited by another workstream, and the two outputs are independent blobs
with independent strides. Everything shared is imported from it, so the family
expansion and level windows cannot drift between the two.

Output format is byte-identical in shape to wildmons.bin, so the shim reads it
with the same walker:

    4 bytes per entry: u16 species (| 0x8000 on a family's first stage),
                       u8 minLevel, u8 maxLevel
    per character: entries, then a SPECIES_NONE terminator, padded to stride

⚠️ NOT YET WIRED INTO THE INJECTOR. The 1% roll also needs the "offered until
caught" filter from spec §1.2/§1.3, which reads the Pokedex caught bitmap -- and
that offset is NOT yet known for this ROM (docs/ROUTINE_MAP.md maps SaveBlock1's
flags and vars but not the dex). Emitting the blob is safe and inert; shipping
the roll without the filter would make every legendary infinitely repeatable at
1%, which is a gameplay change the spec does not sanction (Lazarus has NO
all-legendary characters, so §1.2's repeatable exemption never applies here).
"""

import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import emit_wildmons as W  # noqa: E402  -- shared family/level-window logic


def main():
    rom_table = json.load(open(HERE / "rom_species_table.json"))["species"]
    manifest = json.load(open(HERE / "characters_manifest.json"))

    name_to_const, _parent = W.load_donor()
    for nm, c in W.MACRO_FORM_CONST_OVERRIDES.items():
        name_to_const.setdefault(nm, c)
    children = W.load_children_with_levels()

    donor_by_norm = {W.norm(nm): c for nm, c in name_to_const.items()}
    name_of_const = {c: nm for nm, c in name_to_const.items()}
    rom_ids_by_norm = {}
    id_to_norm = {}
    for idx_str, nm in rom_table.items():
        n = W.norm(nm)
        rom_ids_by_norm.setdefault(n, set()).add(int(idx_str))
        id_to_norm[int(idx_str)] = n

    def rom_id_for_const(c):
        nm = name_of_const.get(c)
        if not nm:
            return None
        ids = rom_ids_by_norm.get(W.norm(nm))
        return min(ids) if ids else None

    per_char = []
    max_entries = 0
    unresolved = []
    distinct = set()

    for rec in manifest["characters"]:
        if "roster_species_ids" not in rec:
            per_char.append([])
            continue
        # THE ONE DIFFERENCE from emit_wildmons.py: the legendary tail.
        bases = rec["roster_species_ids"][rec["starter_count"]:]
        families = []
        seen_species = set()
        for sid in bases:
            if not (0 < sid < W.NUM_SPECIES):
                continue
            n = id_to_norm.get(sid)
            c = donor_by_norm.get(n) if n else None
            if c is None:
                unresolved.append((rec["character"], sid, n))
                continue
            chain = W.build_chain(c, children)
            family_entries = []
            for const, lo, hi in W.stage_windows(chain):
                rid = rom_id_for_const(const)
                if rid is None or not (0 < rid < W.NUM_SPECIES) or rid in seen_species:
                    continue
                seen_species.add(rid)
                family_entries.append((rid, lo, hi))
                distinct.add(rid)
            if family_entries:
                families.append(family_entries)
        per_char.append(families)
        max_entries = max(max_entries, sum(len(f) for f in families))

    if max_entries == 0:
        sys.exit("emit_legendaries: every character came out with an empty "
                 "legendary pool -- the manifest's starter_count split is not "
                 "what this script assumes, and the blob would be all zeros")

    stride_entries = max_entries + 1   # + SPECIES_NONE terminator
    stride = stride_entries * 4
    out = bytearray()
    for families in per_char:
        n = 0
        for family_entries in families:
            for j, (rid, lo, hi) in enumerate(family_entries):
                sp = rid | (W.FAMILY_START_BIT if j == 0 else 0)
                out += struct.pack("<HBB", sp, lo, hi)
                n += 1
        out += b"\x00" * (stride - n * 4)

    (HERE / "legendaries.bin").write_bytes(out)

    with_any = sum(1 for f in per_char if f)
    total = sum(sum(len(f) for f in fams) for fams in per_char)
    print("emitted %d characters x stride %d (max %d stage entries, %d total) "
          "= %d bytes -> legendaries.bin"
          % (len(per_char), stride, max_entries, total, len(out)))
    print("  %d of %d characters have at least one legendary; %d distinct species"
          % (with_any, len(per_char), len(distinct)))
    if unresolved:
        print("  WARNING: %d legendary bases had no donor const (skipped):"
              % len(unresolved))
        for ch, sid, nm in unresolved[:10]:
            print("    %s: id %d (%s)" % (ch, sid, nm))


if __name__ == "__main__":
    main()
