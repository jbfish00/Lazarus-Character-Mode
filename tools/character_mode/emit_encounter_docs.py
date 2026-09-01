#!/usr/bin/env python3
"""Generate ENCOUNTERS.md -- what each character can actually meet in the wild.

rowe_parity.md §9 listed this as a gap the parity table never carried: ROWE and
Radical Red generate this document, Unbound writes its own, and Lazarus and
Seaglass had nothing -- so two of four ports did not document what a character
can meet in the wild.  That is the document the playability work makes most
useful, because in this game the median character matches only ~1.9% of the
game's own wild slots, which means the 10% roster override is doing nearly all
of the work of building a team.

Same principle as emit_roster_docs.py: derived from the data the ROM itself
reads, never hand-written, so it cannot drift from the patch.

Source is the EMITTED tables -- `wildmons.bin` (the 10% non-legendary pool) and
`legendaries.bin` (the 1% pool) -- deliberately NOT `rosters_mapped.json`.  That
file sits upstream of the level-band computation and of the per-game dex filter,
so documenting from it would promise families this ROM cannot actually spawn.

Hidden characters (below the six-fully-evolved threshold) are excluded, for the
same reason ROSTERS.md excludes them: the menu does not offer them, so their
encounter pools are not something a player can reach.

Run after emit_wildmons.py and emit_legendaries.py:
    python3 tools/character_mode/emit_encounter_docs.py
"""
import json
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "ENCOUNTERS.md")

GAME_TITLE = "Pokémon Lazarus v2.0"
LEGENDARY_CHANCE_PCT = 1     # keep in sync with src/character_mode.c
OVERRIDE_CHANCE_PCT = 10
# src/character_mode.c:146. Bit 15 of the species word marks the first stage of
# a family, which is how the shim walks a pool; strip it before naming anything.
FAMILY_START_BIT = 0x8000

CATEGORY_LABEL = {"protagonist": "Protagonist", "rival": "Rival",
                  "gymleader": "Gym Leader", "elite4": "Elite Four",
                  "champion": "Champion", "villain": "Villain",
                  "anime": "Anime", "professor": "Professor",
                  "warden": "Warden", "other": "Other"}


def load(path):
    with open(os.path.join(HERE, path), "rb") as f:
        return f.read()


def decode(blob, stride, index, names):
    """One character's pool as [[(name, lo, hi), ...], ...] grouped by family."""
    rec = blob[index * stride:(index + 1) * stride]
    families, cur = [], None
    for off in range(0, stride, 4):
        sp, lo, hi = struct.unpack_from("<HBB", rec, off)
        if sp == 0:
            break                      # species=0 sentinel terminates the record
        start = bool(sp & FAMILY_START_BIT)
        sp &= ~FAMILY_START_BIT
        entry = (names.get(sp, "species %d" % sp), lo, hi)
        if start or cur is None:
            cur = [entry]
            families.append(cur)
        else:
            cur.append(entry)
    return families


def band(e):
    name, lo, hi = e
    return "%s L%d–%d" % (name, lo, hi)


def main():
    with open(os.path.join(HERE, "characters_manifest.json")) as f:
        manifest = json.load(f)["characters"]
    with open(os.path.join(HERE, "rom_species_table.json")) as f:
        names = {int(k): v for k, v in json.load(f)["species"].items()}

    wild, leg = load("wildmons.bin"), load("legendaries.bin")
    n = len(manifest)
    ws, ls = len(wild) // n, len(leg) // n
    if ws * n != len(wild) or ls * n != len(leg):
        raise SystemExit("wildmons.bin/legendaries.bin are not a whole number "
                         "of records for %d characters -- re-run their emitters"
                         % n)

    rows = []
    for i, rec in enumerate(manifest):
        if rec.get("hidden"):
            continue
        rows.append({
            "name": rec["character"],
            "gen": rec.get("generation", 1) or 1,
            "cat": CATEGORY_LABEL.get(rec.get("category"), "Other"),
            "wild": decode(wild, ws, i, names),
            "leg": decode(leg, ls, i, names),
        })

    n_leg = sum(1 for r in rows if r["leg"])
    n_none = sum(1 for r in rows if not r["leg"] and not r["wild"])
    gens = sorted({r["gen"] for r in rows})

    out = []
    w = out.append
    w("# Character Mode — Wild Encounters (%s)\n" % GAME_TITLE)
    w("What each character can meet **in the wild**, on top of the game's own "
      "encounter tables. Two independent rolls replace the species the area "
      "would normally produce; the level is always the area's own rolled "
      "level, and the evolution stage whose band fits that level is the one "
      "you meet.\n")
    w("```\nroll %d%%   -> a legendary from this character's roster\n"
      "else roll %d%% -> a non-legendary roster member\n"
      "else          -> the game's own wild table\n```\n"
      % (LEGENDARY_CHANCE_PCT, OVERRIDE_CHANCE_PCT))
    w("**Legendaries retire once caught.** A legendary leaves the pool as soon "
      "as its Pokédex *caught* flag is set, so each one can be met once. A "
      "legendary caught before Character Mode was switched on is never "
      "offered.\n")
    w("GENERATED by `tools/character_mode/emit_encounter_docs.py` from "
      "`wildmons.bin` and `legendaries.bin`, the same tables the injected shim "
      "reads — do not hand-edit, regenerate.\n")
    w("### Coverage\n")
    w("- **%d characters** (the ones the menu offers; characters hidden below "
      "the six-fully-evolved threshold are not listed, same as `ROSTERS.md`)."
      % len(rows))
    w("- **%d have a legendary pool** (%d%%)." % (n_leg, round(100 * n_leg / max(len(rows), 1))))
    w("- **%d characters can meet nothing at all** — both pools empty.\n" % n_none)
    w("## Contents")
    for g in gens:
        w("- [Generation %d](#generation-%d)" % (g, g))
    w("")

    for g in gens:
        w("\n## Generation %d\n" % g)
        for r in sorted((x for x in rows if x["gen"] == g), key=lambda x: x["name"]):
            w("### %s — %s" % (r["name"], r["cat"]))
            legpct = LEGENDARY_CHANCE_PCT if r["leg"] else 0
            rospct = OVERRIDE_CHANCE_PCT if r["wild"] else 0
            w("**Effective rates:** %d%% legendary · %d%% roster · %d%% the "
              "game's own tables\n" % (legpct, rospct, 100 - legpct - rospct))
            if r["leg"]:
                w("**Legendary pool (%d):** %s\n"
                  % (len(r["leg"]), ", ".join(band(f[0]) for f in r["leg"])))
            else:
                w("**Legendary pool:** none — no legendary on this "
                  "character's roster.\n")
            if r["wild"]:
                w("**Roster pool (%d families):**\n" % len(r["wild"]))
                w("| # | Stages by level |")
                w("|---|---|")
                for k, fam in enumerate(r["wild"], 1):
                    w("| %d | %s |" % (k, " → ".join(band(e) for e in fam)))
                w("")
            else:
                w("**Roster pool:** none — nothing on this character's roster "
                  "can spawn in this game.\n")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("wrote %s: %d characters, %d with a legendary pool, %d with nothing"
          % (os.path.relpath(OUT, ROOT), len(rows), n_leg, n_none))


if __name__ == "__main__":
    main()
