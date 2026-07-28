#!/usr/bin/env python3
"""Regenerate README.md's "## Character codes" section from the injected data.

The code a player types at the Acrisia University desk is derived from the
character name by exactly one rule (tools/inject_character_mode.py's
`code_for`): strip accents, drop every non-alphanumeric character, cap at 10 --
the naming screen only takes 10. Keeping the tables hand-written meant they went
stale the moment characters moved, which is how Radical Red shipped 15
characters with no documented code at all.

Everything comes from characters_manifest.json (order, category, generation,
the granted starter) and rom_species_table.json (this ROM's own species names),
so this section cannot drift from the patch again.

Hidden characters -- under the six-fully-evolved playability threshold, flags
bit1 -- are omitted: the shim refuses their code at the naming screen, so
listing it would document something that does not work.

Run after emit_characters.py --final:
    python3 tools/character_mode/emit_readme_codes.py
"""
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.abspath(os.path.join(HERE, "..", ".."))
README = os.path.join(TARGET, "README.md")

SECTION_START = "## Character codes"
SECTION_END = "## Credits"

CATEGORY_LABEL = {
    "protagonist": "Protagonist", "rival": "Rival", "gymleader": "Gym Leader",
    "elite4": "Elite Four", "champion": "Champion", "villain": "Villain",
    "anime": "Anime", "professor": "Professor", "frontier": "Frontier Brain",
}


def code_for(display):
    """Mirrors tools/inject_character_mode.py's code_for exactly."""
    n = unicodedata.normalize("NFKD", display)
    n = "".join(ch for ch in n if not unicodedata.combining(ch))
    return "".join(ch for ch in n if ch.isalnum())[:10]


def display_name(disp):
    return disp[:-len(" (anime)")] if disp.endswith(" (anime)") else disp


def main():
    with open(os.path.join(HERE, "characters_manifest.json")) as f:
        chars = json.load(f)["characters"]
    with open(os.path.join(HERE, "rom_species_table.json")) as f:
        rom_names = {int(k): v for k, v in json.load(f)["species"].items()}

    if any("hidden" not in rec for rec in chars):
        raise SystemExit("characters_manifest.json predates the playability "
                         "threshold (no 'hidden' field) - re-run "
                         "derive_drops.py then emit_characters.py --final")
    n_hidden = sum(1 for rec in chars if rec["hidden"])
    chars = [rec for rec in chars if not rec["hidden"]]

    by_gen = defaultdict(list)
    for rec in chars:
        by_gen[rec["generation"]].append(rec)
    for g in by_gen:
        by_gen[g].sort(key=lambda r: display_name(r["character"]))

    out = [SECTION_START, ""]
    for gen in sorted(by_gen):
        out += ["### Generation %d" % gen, "",
                "| Type this code | Character | Role | Starter Pokemon |",
                "|---|---|---|---|"]
        for rec in by_gen[gen]:
            # Same choice the injector makes when it builds the starter table:
            # the curated signature ace if there is one, else roster[0].
            sid = (rec["signature_id"] if rec.get("has_signature")
                   and rec.get("signature_id")
                   else (rec["roster_species_ids"] or [0])[0])
            # The code comes from the FULL name, " (anime)" and all -- that is
            # what tools/inject_character_mode.py encodes into the ROM's code
            # table, so Kiawe (anime) is typed `Kiaweanime`. Stripping the
            # suffix here (as the sibling ports do, where the injector strips it
            # too) documented four codes the ROM does not accept.
            out.append("| `%s` | %s | %s | %s |"
                       % (code_for(rec["character"]),
                          rec["character"],
                          CATEGORY_LABEL.get(rec["category"],
                                             (rec["category"] or "").title()),
                          rom_names.get(sid, "—")))
        out.append("")

    with open(README, encoding="utf-8") as f:
        text = f.read()
    start = text.index(SECTION_START)
    end = text.index(SECTION_END)
    text = text[:start] + "\n".join(out) + "\n" + text[end:]

    # The intro sentence's count is generated too. Radical Red rewrote only the
    # tables and left the sentence reading "199 characters" through two later
    # rebuilds -- the same drift this script exists to stop, one paragraph above
    # the part it was fixing.
    text, n = re.subn(r"\b\d+ characters, Generations 1 through 9\.",
                      "%d characters, Generations 1 through 9." % len(chars),
                      text, count=1)
    if not n:
        print("  !! could not find the intro character-count sentence in "
              "README.md -- check it by hand", file=sys.stderr)
    with open(README, "w", encoding="utf-8") as f:
        f.write(text)

    print("rewrote README.md's character-code tables: %d selectable characters "
          "across generations %s (%d hidden below the threshold, omitted)"
          % (len(chars), ", ".join(str(g) for g in sorted(by_gen)), n_hidden))


if __name__ == "__main__":
    main()
