#!/usr/bin/env python3
"""Per-character obtainability validation (new for Lazarus).

Seaglass lesson: dex-presence != catchable. Lazarus ships official encounter
docs, so we can compute, per character, how many roster species the player can
actually obtain:

    obtainable = wild (encounters.json)
               ∪ gifts (enumerable gift/cheat-code species from the official
                        general documentation PDF)
    (evolution closure is implicit: rosters are stored as evolution-family
     BASE species, and every obtainable form's family base counts.)

Not covered (best-effort limitations, documented in docs/OBTAINABILITY.md):
in-game trades (RE'd in Phase 4), non-enumerable random-pool codes
(NEMOS FAVE / WATCHPHAUN / MONO *), unlisted quest gifts, fossils (species not
enumerated in the PDFs). These can only ADD obtainability, so the trim list
computed here is conservative in the safe direction... for trimming we only
cut characters that remain empty even with these unknowns considered unlikely
to save them; 1-species characters are flagged for the user, not auto-cut.

Outputs: obtainability_report.json + a printed per-character table sorted by
obtainable count; exit code 0 always (reporting tool, decisions are the
user's).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from map_species import load_donor, first_stage_map, MACRO_FORM_CONST_OVERRIDES  # noqa: E402

# Enumerable gift species from the official documentation PDF (v2.0):
# - starter selection at game start: 9 starters (Alola/Kalos/Paldea trios)
# - cheat codes: ILOVEALOLA/ILOVEKALOS/ILOVPALDEA/IWANTMONKE/IMISSJOHTO trios,
#   WORLDCHAMP (Litten), MASKEDOGRE (Ogerpon), "LEGENDS ZA" (Eternal Flower
#   Floette -> Flabébé family), HOUSESTARK (Rockruff), MOSEY (Alolan Meowth)
GIFT_SPECIES = [
    "Rowlet", "Litten", "Popplio",          # Alola trio (also starters)
    "Chespin", "Fennekin", "Froakie",       # Kalos trio (also starters)
    "Sprigatito", "Fuecoco", "Quaxly",      # Paldea trio (also starters)
    "Pansage", "Pansear", "Panpour",        # IWANTMONKE
    "Chikorita", "Cyndaquil", "Totodile",   # IMISSJOHTO
    "Ogerpon",                              # MASKEDOGRE
    "Floette",                              # LEGENDS ZA
    "Rockruff",                             # HOUSESTARK
    "Meowth",                               # MOSEY (Alolan Meowth -> Meowth family)
]


def main():
    name_to_const, parent = load_donor()
    base_of = first_stage_map(parent)
    const_of = dict(name_to_const)
    for name, const in MACRO_FORM_CONST_OVERRIDES.items():
        const_of.setdefault(name, const)

    def to_base_const(name):
        c = const_of.get(name)
        if c is None:
            print(f"  WARNING: no donor const for {name!r}", file=sys.stderr)
            return None
        return base_of.get(c, c)

    wild = json.load(open(os.path.join(HERE, "encounters.json")))["wild"]
    obtainable_bases = set()
    for name in wild:
        b = to_base_const(name)
        if b:
            obtainable_bases.add(b)
    n_wild = len(obtainable_bases)
    for name in GIFT_SPECIES:
        b = to_base_const(name)
        if b:
            obtainable_bases.add(b)
    print(f"obtainable family bases: {len(obtainable_bases)} "
          f"({n_wild} wild + {len(obtainable_bases) - n_wild} gift-only)")

    rosters = json.load(open(os.path.join(HERE, "rosters_mapped.json")))
    report = {}
    for char, data in rosters.items():
        roster_consts = [s["const"] for s in data["species"]]
        ok = sorted(c for c in roster_consts if c in obtainable_bases)
        report[char] = {
            "category": data.get("category"),
            "gen": data.get("gen"),
            "roster_in_rom": len(roster_consts),
            "obtainable": len(ok),
            "obtainable_consts": ok,
        }

    out = os.path.join(HERE, "obtainability_report.json")
    json.dump({"obtainable_bases": sorted(obtainable_bases),
               "characters": report}, open(out, "w"), indent=1)

    rows = sorted(report.items(), key=lambda kv: (kv[1]["obtainable"], kv[0]))
    print(f"\n{'character':22s} {'cat':12s} {'in-ROM':>6s} {'obtainable':>10s}")
    for char, r in rows:
        flag = "  <-- TRIM?" if r["obtainable"] <= 1 else ""
        print(f"{char:22s} {str(r['category']):12s} {r['roster_in_rom']:6d} "
              f"{r['obtainable']:10d}{flag}")
    n0 = sum(1 for _, r in rows if r["obtainable"] == 0)
    n1 = sum(1 for _, r in rows if r["obtainable"] == 1)
    avg = sum(r["obtainable"] for _, r in rows) / max(1, len(rows))
    print(f"\n{len(rows)} characters; {n0} with 0 obtainable, {n1} with exactly 1; "
          f"mean obtainable {avg:.1f}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
