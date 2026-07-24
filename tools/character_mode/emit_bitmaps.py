#!/usr/bin/env python3
"""Emit per-character allowed-species bitmaps for the Phase 4 enforcement shim.

Lazarus version (rewritten from RR's, which expanded through an RR-specific
pokedex dump). Expansion chain per roster base-species id (from
characters_manifest.json, same record order as characters.bin):

  ROM id -> ROM name (rom_species_table.json)
         -> donor const (normalized-name match, same policy as Stage B)
         -> full evolution family (donor topology via first_stage_map)
         -> every family member's name
         -> ALL ROM indices bearing those names (base + regional/alt forms,
            e.g. Meowth 52 + Alolan 965 + Galarian 974 + partner 1494)

Output: rosters_expanded.bin — NUM_CHARACTERS x 196-byte records
(1561 bits, bit N = species id N allowed, LSB-first within each byte).
The shim tests `bitmap[species >> 3] & (1 << (species & 7))`.

NUM_SPECIES=1561 pinned by the species-table finding in docs/SPECIES_CAP.md.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from map_species import load_donor, first_stage_map, MACRO_FORM_CONST_OVERRIDES  # noqa: E402

NUM_SPECIES = 1561
STRIDE = (NUM_SPECIES + 7) // 8  # 196


def norm(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main():
    rom_table = json.load(open(HERE / "rom_species_table.json"))["species"]
    manifest = json.load(open(HERE / "characters_manifest.json"))

    name_to_const, parent = load_donor()
    for nm, c in MACRO_FORM_CONST_OVERRIDES.items():
        name_to_const.setdefault(nm, c)
    base_of = first_stage_map(parent)

    # normalized donor name -> const; const -> donor name
    donor_by_norm = {norm(nm): c for nm, c in name_to_const.items()}
    name_of_const = {c: nm for nm, c in name_to_const.items()}

    # base const -> all member consts of that family
    family = {}
    for c in name_to_const.values():
        family.setdefault(base_of.get(c, c), set()).add(c)

    # normalized name -> ALL rom indices with that name
    rom_ids_by_norm = {}
    id_to_norm = {}
    for idx_str, nm in rom_table.items():
        n = norm(nm)
        rom_ids_by_norm.setdefault(n, set()).add(int(idx_str))
        id_to_norm[int(idx_str)] = n

    out = bytearray()
    report = []
    unresolved = []
    for rec in manifest["characters"]:
        if "roster_species_ids" not in rec:
            continue  # warning-only entries
        allowed = set()
        for sid in rec["roster_species_ids"]:
            if not (0 < sid < NUM_SPECIES):
                continue
            allowed.add(sid)
            n = id_to_norm.get(sid)
            c = donor_by_norm.get(n) if n else None
            if c is None:
                unresolved.append((rec["character"], sid, n))
                continue
            for member in family.get(base_of.get(c, c), {c}):
                mnorm = norm(name_of_const[member])
                allowed.update(i for i in rom_ids_by_norm.get(mnorm, ())
                               if 0 < i < NUM_SPECIES)
        bm = bytearray(STRIDE)
        for s in allowed:
            bm[s >> 3] |= 1 << (s & 7)
        out += bm
        report.append((rec["character"], len(rec["roster_species_ids"]), len(allowed)))

    (HERE / "rosters_expanded.bin").write_bytes(out)
    n = len(report)
    print(f"emitted {n} bitmaps x {STRIDE} bytes = {len(out)} bytes -> rosters_expanded.bin")
    if unresolved:
        print(f"  WARNING: {len(unresolved)} roster ids had no donor const (bit still set, no expansion):")
        for ch, sid, nm in unresolved[:10]:
            print(f"    {ch}: id {sid} ({nm})")

    # sanity: Red's roster must allow the Pichu family (Pichu 172, Pikachu 25,
    # partner/alt Pikachu 1487/1493, Raichu forms) and never SPECIES_NONE(0).
    # (2026-07-23: Meowth flipped from excluded to EXPECTED -- the full-research
    # roster rebuild legitimately added Meowth to Red via his Let's Go Pikachu
    # Champion-team research; the old fixture assumed the pre-rebuild roster.)
    red_i = next(i for i, r in enumerate(report) if r[0] == "Red")
    bm = out[red_i * STRIDE:(red_i + 1) * STRIDE]
    def has(s): return bool(bm[s >> 3] & (1 << (s & 7)))
    checks = [("Pichu 172", has(172), True), ("Pikachu 25", has(25), True),
              ("Pikachu form 1487", has(1487), True),
              ("Meowth 52", has(52), True), ("SPECIES_NONE 0", has(0), False)]
    ok = True
    for name, got, want in checks:
        status = "OK" if got == want else "FAIL"
        if got != want:
            ok = False
        print(f"  sanity Red/{name}: {status}")
    if not ok:
        raise SystemExit("sanity checks FAILED")
    sizes = sorted(r[2] for r in report)
    print(f"  expanded roster sizes: min {sizes[0]}, median {sizes[n // 2]}, max {sizes[-1]}")


if __name__ == "__main__":
    main()
