#!/usr/bin/env python3
"""Prove ROSTERS.md and README.md describe exactly what the BUILT ROM offers.

`emit_roster_docs.py` generates the docs from `rosters_expanded.bin`, so docs
and build agree by construction -- which means a bug in the generator would make
them agree with each other and still disagree with the game. This closes that
loop by reading the enforcement data back out of `build/lazarus_cm.gba`, at the
addresses the injector actually wrote it to, and re-deriving every claim from
those bytes.

Checks:
  1. the allow-bitmaps in the built ROM == rosters_expanded.bin
  2. the hidden bitmap in the built ROM == the manifest's flags bit1 ==
     character_drops.json -- in BOTH directions, so neither a character that
     should be offered and is not, nor one that should not be and is, survives
  3. every character in ROSTERS.md is offered by the ROM, and every character
     the ROM offers is in ROSTERS.md
  4. every Pokemon listed under a character is genuinely allowed by that
     character's in-ROM bitmap
  5. every final evolution the in-ROM bitmap allows is actually listed
  6. the sprite pages mirror ROSTERS.md character for character, row for row
  7. the character counts in ROSTERS.md, ROSTERS_SPRITES.md and README.md agree
     with the number the ROM offers
  8. every code in README.md matches the code table in the ROM, byte for byte,
     and no hidden character's code is documented

The addresses are parsed out of tools/inject_character_mode.py rather than
copied, so a rebase there cannot leave this test reading the wrong bytes.

Exit 1 on any mismatch. Run after emit_roster_docs.py + emit_readme_codes.py,
on a built ROM.
"""
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import emit_roster_docs as erd            # noqa: E402
from map_species_stage_b import normalize  # noqa: E402

BUILT = os.path.join(ROOT, "build", "lazarus_cm.gba")
INJECTOR = os.path.join(ROOT, "tools", "inject_character_mode.py")
STRIDE = 196
CODE_LEN = 11


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def injector_addr(name):
    m = re.search(r"^%s\s*=\s*(0x[0-9A-Fa-f]+)" % name, read(INJECTOR), re.M)
    if not m:
        raise SystemExit("could not parse %s out of inject_character_mode.py" % name)
    return int(m.group(1), 16)


def code_for(display):
    """Mirrors tools/inject_character_mode.py's code_for exactly."""
    n = unicodedata.normalize("NFKD", display)
    n = "".join(ch for ch in n if not unicodedata.combining(ch))
    return "".join(ch for ch in n if ch.isalnum())[:10]


def parse_doc(text):
    """{character: [listed Pokemon names]} from a ROSTERS.md-shaped file.

    ROSTERS.md lists one Pokemon per table row -- `| Name | Source |` -- since
    the doc-Sources port replaced the old single comma-separated line.  Reading
    it as a comma list makes every roster parse as EMPTY, which reports as the
    docs omitting everything rather than as a parse failure, so keep the table
    shape and this function in step.
    """
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^### (.+?) — ", line)
        if m:
            cur = m.group(1).strip()
            out[cur] = []
            continue
        m = re.match(r"^\| (.+?) \| (.*?) \|$", line)
        if m and cur is not None and m.group(1) not in ("Pokémon", "---"):
            out[cur].append(m.group(1).strip())
    return out

def _resolve_charmap():
    """Path to this repo's vendored game-text charmap (tools/charmap.txt).

    This was a hardcoded absolute path into the unrelated "Pokemon Rowe
    Alteration" working tree, which made this repo unbuildable and
    unverifiable from a fresh clone. The charmap is now vendored here
    (byte-identical, md5 b31d142ca98103d64d707f9894fa42e3). Resolution is
    anchored to this file's own location, never the cwd.

    Override with the CM_CHARMAP environment variable.
    """
    import os
    from pathlib import Path
    override = os.environ.get("CM_CHARMAP")
    if override:
        p = Path(override)
        if not p.is_file():
            raise SystemExit("CM_CHARMAP=%s is not a file" % override)
        return p
    # Walk up to the REPO ROOT only. An unbounded walk would keep climbing past
    # the repo into ~ and could silently pick up an unrelated tools/charmap.txt
    # -- reading the wrong charmap presents as "this game encodes text
    # differently", not as a missing file. Bound it at the .git directory.
    for parent in Path(__file__).resolve().parents:
        cand = parent / "tools" / "charmap.txt"
        if cand.is_file():
            return cand
        if (parent / ".git").exists():
            break
    raise SystemExit(
        "charmap.txt not found. Expected it vendored at <repo>/tools/charmap.txt; "
        "set CM_CHARMAP to override.")


def main():
    fails = []

    if not os.path.isfile(BUILT):
        print("no built ROM at %s -- run tools/inject_character_mode.py first"
              % os.path.relpath(BUILT, ROOT))
        return 1
    with open(BUILT, "rb") as f:
        rom = f.read()
    with open(os.path.join(HERE, "characters_manifest.json")) as f:
        manifest = json.load(f)["characters"]
    with open(os.path.join(HERE, "rosters_expanded.bin"), "rb") as f:
        staged = f.read()
    with open(os.path.join(HERE, "rom_species_table.json")) as f:
        rom_names = {int(k): v for k, v in json.load(f)["species"].items()}
    with open(os.path.join(HERE, "character_drops.json")) as f:
        drops = set(json.load(f)["unselectable"])

    n = len(manifest)
    bitmaps_addr = injector_addr("BITMAPS_ADDR")
    hidden_addr = injector_addr("HIDDEN_ADDR")
    codes_addr = injector_addr("CODES_ADDR")

    # --- 1. the docs' input is what the ROM carries ------------------------
    off = bitmaps_addr - 0x08000000
    in_rom = rom[off:off + n * STRIDE]
    if in_rom != staged:
        fails.append("bitmaps in the built ROM differ from rosters_expanded.bin "
                     "-- the docs were generated from data the ROM does not carry")

    # --- 2. hidden: ROM bits == manifest bit1 == character_drops.json ------
    hoff = hidden_addr - 0x08000000
    hbits = rom[hoff:hoff + (n + 7) // 8]
    rom_hidden = {manifest[i]["character"] for i in range(n)
                  if hbits[i >> 3] & (1 << (i & 7))}
    man_hidden = {rec["character"] for rec in manifest if rec.get("hidden")}
    if rom_hidden != man_hidden:
        fails.append("the ROM's hidden bitmap and the manifest's flags bit1 "
                     "disagree about %d character(s) (%s) -- re-run "
                     "emit_characters.py --final then the injector"
                     % (len(rom_hidden ^ man_hidden),
                        ", ".join(sorted(rom_hidden ^ man_hidden)[:6])))
    stripped = {re.sub(r"\s*\(anime\)$", "", c) for c in rom_hidden}
    if stripped != drops:
        fails.append("the ROM hides %d character(s) but character_drops.json "
                     "lists %d (%s) -- re-run derive_drops.py, "
                     "emit_characters.py --final and the injector"
                     % (len(stripped), len(drops),
                        ", ".join(sorted(stripped ^ drops)[:6])))

    # --- re-derive every doc row from the ROM's own bytes ------------------
    index = erd.FinalIndex()
    rom_allowed, rom_finals = {}, {}
    for i, rec in enumerate(manifest):
        bits = in_rom[i * STRIDE:(i + 1) * STRIDE]
        allowed = {rom_names[s] for s in rom_names
                   if s < STRIDE * 8 and bits[s >> 3] & (1 << (s & 7))}
        rom_allowed[rec["character"]] = allowed
        rom_finals[rec["character"]] = {
            index.donor[c]["name"] for c in index.finals_for_names(allowed)}

    doc = parse_doc(read(os.path.join(ROOT, "ROSTERS.md")))

    # --- 0. the parse itself worked ---------------------------------------
    # When parse_doc fell out of step with ROSTERS.md's shape it returned every
    # character with an EMPTY row list, and that surfaced as 246 content
    # failures ("the doc omits 12 final evolutions") rather than as what it
    # was.  An offered character always has at least six fully-evolved Pokemon
    # -- that is the threshold rule that decides it is offered at all -- so a
    # heading with no rows under it cannot be a real roster, only a bad parse.
    empty = sorted(c for c, rows in doc.items() if not rows)
    if not doc or empty:
        print("verify_docs: PARSE FAILURE -- %d of %d headings in ROSTERS.md "
              "yielded no rows (%s). parse_doc no longer matches the file's "
              "shape; fix the parser before reading anything below."
              % (len(empty), len(doc), ", ".join(empty[:6]) or "no headings"))
        return 1

    # --- 3. offered <-> documented, both directions ------------------------
    for char in doc:
        if char not in rom_allowed:
            fails.append("%s: in ROSTERS.md but not in characters_manifest.json"
                         % char)
    for char in rom_allowed:
        # A hidden character still HAS a bitmap in the ROM -- that is the point,
        # old saves keep being enforced -- but the naming screen refuses its
        # code, so documenting it would advertise a code that gets rejected.
        if char in rom_hidden:
            if char in doc:
                fails.append("%s: hidden from selection but still listed in "
                             "ROSTERS.md -- re-run emit_roster_docs.py" % char)
            continue
        if char not in doc:
            fails.append("%s: offered by the ROM but missing from ROSTERS.md"
                         % char)

    # --- 4/5. every listed row allowed, every allowed final listed ---------
    for char, listed in doc.items():
        if char not in rom_allowed:
            continue
        allowed_norm = {normalize(x) for x in rom_allowed[char]}
        for mon in listed:
            bare = re.sub(r"[ᵃᵍ]", "", mon)
            if normalize(bare) not in allowed_norm:
                fails.append("%s: doc lists %s, which its in-ROM bitmap does "
                             "not allow" % (char, bare))
        missing = rom_finals[char] - {re.sub(r"[ᵃᵍ]", "", m) for m in listed}
        if missing:
            fails.append("%s: in-ROM bitmap allows %d final evolution(s) the "
                         "doc omits (%s)"
                         % (char, len(missing), ", ".join(sorted(missing)[:6])))

    # --- 6. the sprite pages mirror ROSTERS.md ----------------------------
    sprite_chars = {}
    sprites_dir = os.path.join(ROOT, "sprites")
    for path in sorted(os.listdir(sprites_dir)):
        if not re.match(r"gen_\d+\.md$", path):
            continue
        cur = None
        for line in read(os.path.join(sprites_dir, path)).splitlines():
            m = re.match(r"^### (.+?) — ", line)
            if m:
                cur = m.group(1).strip()
                sprite_chars[cur] = 0
                continue
            if cur is not None:
                sprite_chars[cur] += len(re.findall(r"<sub>([^<]+)</sub>", line))
    for char, listed in doc.items():
        if char not in sprite_chars:
            fails.append("%s: in ROSTERS.md but missing from the sprite pages"
                         % char)
        elif sprite_chars[char] != len(listed):
            fails.append("%s: %d rows in ROSTERS.md but %d sprite cells"
                         % (char, len(listed), sprite_chars[char]))
    for char in sprite_chars:
        if char not in doc:
            fails.append("%s: on a sprite page but not in ROSTERS.md" % char)

    # --- 7. the counts the docs advertise ---------------------------------
    offered = n - len(rom_hidden)
    for fname, pat in (("ROSTERS.md", r"\*\*(\d+) selectable characters\.\*\*"),
                       ("ROSTERS_SPRITES.md", r"\*\*(\d+) selectable characters\.\*\*"),
                       ("README.md", r"\b(\d+) characters, Generations 1 through 9\.")):
        m = re.search(pat, read(os.path.join(ROOT, fname)))
        if not m:
            fails.append("%s: no character count found" % fname)
        elif int(m.group(1)) != offered:
            fails.append("%s says %s characters; the ROM offers %d"
                         % (fname, m.group(1), offered))

    # --- 8. README codes == the ROM's own code table ----------------------
    coff = codes_addr - 0x08000000
    charmap = {}
    for line in read(str(_resolve_charmap())).splitlines():
        m = re.match(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$", line)
        if m and m.group(1) not in charmap:
            charmap[m.group(1)] = int(m.group(2), 16)
    decode = {v: k for k, v in charmap.items()}
    rom_codes = {}
    for i, rec in enumerate(manifest):
        raw = rom[coff + i * CODE_LEN:coff + (i + 1) * CODE_LEN]
        rom_codes[rec["character"]] = "".join(
            decode.get(b, "?") for b in raw[:raw.index(0xFF)] if b != 0xFF)
    readme_codes = set(re.findall(r"^\| `([^`]+)` \|", read(os.path.join(ROOT, "README.md")),
                                  re.M))
    for char, code in rom_codes.items():
        # The injector encodes the FULL display name, " (anime)" included --
        # Kiawe (anime) is typed `Kiaweanime`. Do not "helpfully" strip it.
        expected = code_for(char)
        if code != expected:
            fails.append("%s: code table in the ROM says %r, the naming rule "
                         "says %r" % (char, code, expected))
        if char in rom_hidden and code in readme_codes:
            fails.append("%s: hidden, but its code `%s` is documented in "
                         "README.md" % (char, code))
        if char not in rom_hidden and code not in readme_codes:
            fails.append("%s: offered, but its code `%s` is missing from "
                         "README.md" % (char, code))

    if fails:
        print("verify_docs: %d FAILURE(S)" % len(fails))
        for f in fails:
            print("  FAIL " + f)
        return 1
    print("verify_docs: ALL PASS -- %d characters in the table, %d offered, "
          "%d hidden; %d doc rows re-derived from the built ROM"
          % (n, offered, len(rom_hidden), sum(len(v) for v in doc.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
