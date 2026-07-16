#!/usr/bin/env python3
"""Extract the wild-encounter species set from the official Lazarus Encounters PDF.

New step for Lazarus (Seaglass had no official docs): obtainability validation
needs to know what is actually catchable, not merely present in the species
table. The PDF is a columnar Google-Sheets export; per-location fidelity is
unreliable after pdftotext, so the contract here is deliberately modest:

  - a FLAT set of wild-obtainable species (the requirement), plus
  - best-effort acquisition tags (day/night/fishing/surfing/underwater) taken
    from the section a hit appears under.

Species names are resolved to donor-canonical names (the same
pokeemerald_expansion donor Stage A uses) with form/qualifier stripping:
"Alolan Grimer" -> Grimer, "Flabebe Red Flower" -> Flabébé,
"Oricorio Baile" -> Oricorio, "White-Striped Basculin" -> Basculin.

Output: encounters.json  {"wild": [donor names], "tags": {name: [tags]},
                          "unmatched": [raw strings]}
"""
import json
import os
import re
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "..", "..", "..", "Lazarus_Docs",
                   "Pokemon Lazarus Documentation - Encounters.pdf")
OUT = os.path.join(HERE, "encounters.json")

sys.path.insert(0, HERE)
from map_species import load_donor, MACRO_FORM_CONST_OVERRIDES  # noqa: E402

# PDF typos / spellings that differ from donor canonical names
ALIASES = {"Sligoo": "Sliggoo"}


def norm(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())


# Words that are qualifiers, never part of a base species name we care about.
QUALIFIERS = {
    "alolan", "galarian", "hisuian", "paldean", "whitestriped", "redstriped",
    "bluestriped", "red", "blue", "orange", "white", "yellow", "flower",
    "baile", "pompom", "pau", "sensu", "old", "good", "super", "rod",
    "male", "female", "east", "west", "incarnate",
}

SECTION_TAGS = [
    (re.compile(r"Land Encounters \(Day\)", re.I), "day"),
    (re.compile(r"Land Encounters \(Night\)", re.I), "night"),
    (re.compile(r"^Fishing:", re.I), "fishing"),
    (re.compile(r"^Surfing:", re.I), "surfing"),
    (re.compile(r"^Underwater:", re.I), "underwater"),
]

NAME_PCT = re.compile(r"([A-Za-z][A-Za-z'’.:\- ]{1,40}?)\s*\((\d{1,3})%\)")


def main():
    name_to_const, _parent = load_donor()
    # donor canonical name lookup by normalized form; macro-form species
    # (Flabébé, Minior, ...) are absent from load_donor()'s parse but valid
    canon = {}
    for name in name_to_const:
        canon[norm(name)] = name
    for name in MACRO_FORM_CONST_OVERRIDES:
        canon.setdefault(norm(name), name)
    for typo, real in ALIASES.items():
        canon[norm(typo)] = real

    txt = subprocess.run(["pdftotext", "-layout", PDF, "-"],
                         capture_output=True, text=True, check=True).stdout

    tag = "day"
    found = {}       # donor name -> set of tags
    unmatched = set()
    pending_prefix = ""   # handles names split before a "(NN%)" on the next line

    for line in txt.splitlines():
        for rex, t in SECTION_TAGS:
            if rex.search(line):
                tag = t
                break
        hits = NAME_PCT.findall(pending_prefix + " " + line)
        for raw, _pct in hits:
            words = [w for w in re.split(r"\s+", raw.strip()) if w]
            # progressively strip qualifier words; find longest run of words
            # whose concatenation matches a donor species name
            resolved = None
            content = [w for w in words if norm(w) not in QUALIFIERS]
            for size in range(len(content), 0, -1):
                for start in range(len(content) - size + 1):
                    cand = norm("".join(content[start:start + size]))
                    if cand in canon:
                        resolved = canon[cand]
                        break
                if resolved:
                    break
            if resolved:
                found.setdefault(resolved, set()).add(tag)
            elif content:  # qualifier-only fragments ("Old Rod") are noise
                unmatched.add(raw.strip())
        # carry a trailing bare species name (no percentage on this line) so
        # "White-Striped Basculin" + next-line "Super(20%) Rod" still resolves
        tail = re.sub(NAME_PCT, "", line).strip()
        pending_prefix = tail if re.match(r"^[A-Z][A-Za-z'’.:\- ]+$", tail) else ""

    wild = sorted(found)
    json.dump({"wild": wild,
               "tags": {k: sorted(v) for k, v in sorted(found.items())},
               "unmatched": sorted(unmatched)},
              open(OUT, "w"), indent=1, ensure_ascii=False)
    print(f"wild species resolved: {len(wild)}; unmatched fragments: {len(unmatched)}")
    for u in sorted(unmatched):
        print("  UNMATCHED:", u)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
