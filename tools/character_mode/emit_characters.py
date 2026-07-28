#!/usr/bin/env python3
"""Generate a flat binary character table from rosters_mapped.json.

Adapted from Unbound-Character-Mode's emit_characters.py (itself adapted
from ROWE's C-header generator), for the same reason: Seaglass has no
compile step to hook into, so this emits raw, position-independent POD data
matching ROWE's `struct CharacterInfo` semantics as three flat blobs, to be
injected into ROM free space and pointer-patched by a later insert script
once Phase 1 confirms real hook/table addresses:

  characters.bin  - fixed-size records, one per character (layout below)
  rosters.bin     - each character's roster: u16 species ids, SPECIES_NONE-
                    terminated, concatenated back to back
  names.bin       - each character's display name, Gen3-charmap-encoded,
                    0xFF-terminated, concatenated back to back
  characters_manifest.json - human-readable record of every field, for the
                    later insert step and for debugging

Record layout (12 bytes, native ROM byte order = little-endian), OFFSETS
ARE RELATIVE TO THE START OF THEIR OWN BLOB, not final ROM addresses:
    u32 name_offset      -- offset into names.bin
    u32 roster_offset     -- offset into rosters.bin
    u16 sprite_asset_id   -- PLACEHOLDER 0xFFFF ("TBD") until Phase 3 finds
                             Seaglass's OW/trainer-pic tables
    u8  generation
    u8  flags             -- bit0: hasSignature: signature ace is roster[0]
                             bit1: hidden: under the six-fully-evolved
                                   playability threshold in this game's curated
                                   dex, so the code is refused at the naming
                                   screen. The RECORD STAYS -- a save stores the
                                   character index, so an existing save on a
                                   now-hidden character keeps loading and keeps
                                   being enforced. See character_drops.json.

hidden.bin is emitted alongside: one bit per character (LSB-first), bit i set =
character i is hidden. characters.bin itself is never injected into this ROM --
the shim reads codes/starters/bitmaps as separate blobs -- so the flag needs its
own blob to reach the code-matching loop.

TWO MODES, unlike Unbound's single-pass emitter, because map_species.py's
Stage A deliberately does NOT borrow untrustworthy donor numeric ids (see
docs/DONOR_CROSSWALK.md) -- every species_id in rosters_mapped.json is the
literal string "PENDING_PHASE1" until a Stage B pass (gated on Phase 1)
fills in real, ROM-verified ids:

  --dry-run (default): validates roster completeness/ordering (starter vs.
      legendary split, signature placement, 0-empty-roster check) against
      names/topology only. Writes names.bin (fully known already) and
      characters_manifest.json (with SPECIES_* consts, not numeric ids,
      recorded for review), but deliberately does NOT write characters.bin
      or rosters.bin -- those would be meaningless without real species ids,
      and a stray placeholder-filled build is a real risk of being injected
      by accident.
  --final: requires every species referenced by every character's roster to
      have a real integer id (i.e. rosters_mapped.json must have been
      through Stage B first, not just Stage A) -- errors out otherwise.
      Writes all three binaries.
"""
import argparse
import json
import os
import re
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
CHARMAP_PATH = "/home/jbfish00/Documents/Pokemon Rowe Alteration/charmap.txt"

# Legendary/mythical/Ultra Beast/Paradox evolution-family bases: kept on
# rosters (catchable) but never offered as starters. Full Gen 1-9 list,
# reused verbatim from ROWE (NOT Unbound's Gen-9-trimmed copy) -- Seaglass's
# confirmed cross-gen scope includes Gen 9 legendaries (Ogerpon, Koraidon/
# Miraidon, Terapagos, Pecharunt, etc.), unlike Unbound which has no Gen 9
# content at all.
LEGENDARY_BASES = {"SPECIES_" + s for s in """ARTICUNO ZAPDOS MOLTRES MEWTWO MEW
RAIKOU ENTEI SUICUNE LUGIA HO_OH CELEBI
REGIROCK REGICE REGISTEEL LATIAS LATIOS KYOGRE GROUDON RAYQUAZA JIRACHI DEOXYS
UXIE MESPRIT AZELF DIALGA PALKIA HEATRAN REGIGIGAS GIRATINA CRESSELIA PHIONE MANAPHY DARKRAI SHAYMIN ARCEUS
VICTINI COBALION TERRAKION VIRIZION TORNADUS THUNDURUS RESHIRAM ZEKROM LANDORUS KYUREM KELDEO MELOETTA GENESECT
XERNEAS YVELTAL ZYGARDE DIANCIE HOOPA VOLCANION
TYPE_NULL TAPU_KOKO TAPU_LELE TAPU_BULU TAPU_FINI COSMOG NECROZMA MAGEARNA MARSHADOW ZERAORA MELTAN
NIHILEGO BUZZWOLE PHEROMOSA XURKITREE CELESTEELA KARTANA GUZZLORD POIPOLE STAKATAKA BLACEPHALON
ZACIAN ZAMAZENTA ETERNATUS KUBFU ZARUDE REGIELEKI REGIDRAGO GLASTRIER SPECTRIER CALYREX ENAMORUS
WO_CHIEN CHIEN_PAO TING_LU CHI_YU KORAIDON MIRAIDON OKIDOGI MUNKIDORI FEZANDIPITI OGERPON TERAPAGOS PECHARUNT""".split()}

# SPECIES_* aliases used by LEGENDARY_BASES/MACRO_FORM_CONST_OVERRIDES that
# don't match this donor's base-form spelling for a couple of multi-form
# legendaries (Arceus/Genesect/Type: Null already resolve fine via their
# plain alias; kept here only for clarity that no extra mapping is needed).
CATEGORIES = ["protagonist", "rival", "gymleader", "elite4", "champion", "villain", "anime"]


def load_charmap(path):
    table = {}
    pat = re.compile(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = pat.match(line.rstrip("\n"))
            if m:
                table[m.group(1)] = int(m.group(2), 16)
    return table


def encode_text(text, charmap):
    out = bytearray()
    for ch in text:
        if ch not in charmap:
            raise ValueError(f"character {ch!r} not in charmap (name: {text!r})")
        out.append(charmap[ch])
    out.append(0xFF)  # Gen3 string terminator
    return bytes(out)


def display_name(disp):
    if disp.endswith(" (anime)"):
        return disp[: -len(" (anime)")]
    return disp


def load_order(mapped):
    order = []
    with open(os.path.join(HERE, "characters.txt")) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            disp = line.split("|")[0].strip()
            if disp in mapped:
                order.append(disp)
    return order


def _signature_base_map():
    """Donor evolution topology: const -> its family-base const. Used to keep
    signatures whose ace is an evolved form (e.g. Red's Pikachu) when the
    roster stores only family bases (e.g. Pichu). Lazy import: map_species
    pulls the donor clone, which stays optional for --dry-run validation."""
    from map_species import load_donor, first_stage_map
    _, parent = load_donor()
    return first_stage_map(parent)


def build_rosters(mapped, order):
    """Compute starter/legendary split + signature placement per character.
    Returns (per-character dict, empty-roster list, warnings list) -- pure
    function of consts, independent of whether numeric ids exist yet."""
    base_of = _signature_base_map()
    built = {}
    empty = []          # emitted, but with no species -- see the note below
    warnings = []
    for disp in order:
        info = mapped[disp]
        species = info["species"]
        if not species:
            # An empty roster used to SKIP the character, emitting no record at
            # all. That is a save-corrupting bug the moment it happens to a
            # character that already shipped: a save stores the character INDEX,
            # so dropping a record renumbers everyone after it. The 2026-07-25
            # audit made it happen for real -- Viola (index 117), Rowan (182),
            # Burnet (185) and Magnolia (187) all emptied, because the audit
            # correctly removed other trainers' Pokemon from them and everything
            # genuinely theirs is absent from this ROM's curated dex.
            #
            # So: emit a record, keep the index, and let the playability
            # threshold hide the character from the menu. That is exactly the
            # case the threshold exists for, and it is the only option that
            # keeps existing saves valid.
            empty.append(disp)
            built[disp] = {
                "category": info.get("category"),
                "generation": info.get("gen", 0) or 1,
                "ordered_consts": [],
                "starter_count": 0,
                "has_signature": False,
                "signature_const": None,
            }
            warnings.append("%s: empty roster in this game -- record kept for "
                            "index stability, must be hidden by the threshold" % disp)
            continue

        consts = [s["const"] for s in species]
        starters = [c for c in consts if c not in LEGENDARY_BASES]
        legends = [c for c in consts if c in LEGENDARY_BASES]

        sig = info.get("signature")
        has_signature = 0
        sig_const = None
        if sig:
            sig_const = sig["const"]
            if sig_const in starters:
                starters.remove(sig_const)
            elif sig_const in legends:
                legends.remove(sig_const)
            else:
                # Ace is an evolved form; roster stores family bases. Accept
                # when the ace's family base is on the roster — the ace id
                # becomes roster[0] (the signature/starter give), and the
                # bitmap expansion covers the whole family either way.
                sig_base = base_of.get(sig_const, sig_const)
                if sig_base not in starters and sig_base not in legends:
                    warnings.append("%s: signature %s (base %s) not on roster, dropped"
                                    % (disp, sig_const, sig_base))
                    sig_const = None
            if sig_const:
                starters.insert(0, sig_const)
                has_signature = 1

        ordered_consts = starters + legends
        if not starters:
            warnings.append("%s: all-legendary roster, no starter to offer" % disp)

        built[disp] = {
            "category": info.get("category"),
            "generation": info.get("gen", 0) or 1,
            "ordered_consts": ordered_consts,
            "starter_count": len(starters),
            "has_signature": bool(has_signature),
            "signature_const": sig_const,
        }
    return built, empty, warnings


def load_hidden(order):
    """Resolve character_drops.json's names onto this build's character list.

    derive_drops.py writes names with a trailing " (anime)" stripped, because
    that is the name the ROM shows and the code the player types; characters.txt
    keeps the suffix. Resolving through display_name() bridges the two.

    Every dropped name MUST resolve, and no two characters may share a display
    name. A name that matched nothing would silently leave that character
    selectable -- the exact failure this pass exists to close, and one no
    downstream test can tell apart from "the threshold said keep". So both are
    assertions, not skips.
    """
    path = os.path.join(HERE, "character_drops.json")
    if not os.path.isfile(path):
        return set()
    with open(path, encoding="utf-8") as f:
        names = json.load(f).get("unselectable", [])
    by_display = {}
    collisions = []
    for disp in order:
        d = display_name(disp)
        if d in by_display:
            collisions.append(d)
        by_display[d] = disp
    if collisions:
        raise SystemExit(
            "%d display name(s) are shared by more than one character (%s) -- "
            "character_drops.json could not say which one it means"
            % (len(collisions), ", ".join(sorted(set(collisions)))))
    hidden, unresolved = set(), []
    for n in names:
        if n in by_display:
            hidden.add(by_display[n])
        else:
            unresolved.append(n)
    if unresolved:
        raise SystemExit(
            "character_drops.json names %d character(s) this build does not "
            "have: %s -- re-run derive_drops.py"
            % (len(unresolved), ", ".join(unresolved)))
    return hidden


def const_id_map(mapped):
    """SPECIES_* const -> this ROM's numeric id, from rosters_mapped.json's
    per-species "id" field. Fails loudly if anything is still PENDING_PHASE1,
    i.e. if Stage B has not run. Shared with derive_drops.py so the threshold
    counts the same species the binaries carry."""
    const_to_id = {}
    unresolved = set()
    for info in mapped.values():
        for s in info["species"]:
            if s["id"] == "PENDING_PHASE1":
                unresolved.add(s["const"])
            else:
                const_to_id[s["const"]] = s["id"]
        sig = info.get("signature")
        if sig:
            if sig["id"] == "PENDING_PHASE1":
                unresolved.add(sig["const"])
            else:
                const_to_id[sig["const"]] = sig["id"]
    if unresolved:
        raise SystemExit(
            "real species ids required for all species; %d still "
            "PENDING_PHASE1 (e.g. %s). Run Stage B first."
            % (len(unresolved), ", ".join(sorted(unresolved)[:5])))
    return const_to_id


def cmd_dry_run(mapped, order):
    charmap = load_charmap(CHARMAP_PATH)
    built, empty, warnings = build_rosters(mapped, order)

    names_blob = bytearray()
    manifest = []
    for disp in order:
        b = built[disp]
        name_off = len(names_blob)
        names_blob += encode_text(display_name(disp), charmap)
        manifest.append({
            "character": disp,
            "category": b["category"],
            "generation": b["generation"],
            "name_offset": name_off,
            "roster_species_consts": b["ordered_consts"],
            "starter_count": b["starter_count"],
            "has_signature": b["has_signature"],
            "signature_const": b["signature_const"],
            "sprite_asset_id": "TBD",
        })

    with open(os.path.join(HERE, "names.bin"), "wb") as f:
        f.write(names_blob)
    with open(os.path.join(HERE, "characters_manifest.json"), "w") as f:
        json.dump({"mode": "dry_run_names_topology_only",
                   "record_count": len(order),
                   "empty_roster": empty,
                   "warnings": warnings,
                   "characters": manifest}, f, indent=1)

    print("[dry-run] validated %d characters (%d with an empty roster, kept for index stability)" % (len(order), len(empty)))
    print("  names.bin: %d bytes (real, final content)" % len(names_blob))
    print("  characters.bin / rosters.bin: NOT written -- species ids are all")
    print("  PENDING_PHASE1; run with --final once Stage B fills in real ids.")
    if warnings:
        print("\nwarnings:")
        for w in warnings:
            print("  " + w)


def cmd_final(mapped, order):
    charmap = load_charmap(CHARMAP_PATH)
    built, empty, warnings = build_rosters(mapped, order)

    const_to_id = const_id_map(mapped)
    hidden_names = load_hidden(order)

    names_blob = bytearray()
    rosters_blob = bytearray()
    records = bytearray()
    hidden_bits = bytearray((len(order) + 7) // 8)
    manifest = []

    for i, disp in enumerate(order):
        b = built[disp]
        name_off = len(names_blob)
        names_blob += encode_text(display_name(disp), charmap)

        roster_off = len(rosters_blob)
        for const in b["ordered_consts"]:
            rosters_blob += struct.pack("<H", const_to_id[const])
        rosters_blob += struct.pack("<H", 0)  # SPECIES_NONE terminator

        hidden = disp in hidden_names
        if hidden:
            hidden_bits[i >> 3] |= 1 << (i & 7)
        flags = (int(b["has_signature"]) & 0x1) | (0x2 if hidden else 0)
        sprite_asset_id = 0xFFFF  # TBD -- Seaglass OW/trainer-pic table not yet located (Phase 1/3)
        records += struct.pack("<IIHBB", name_off, roster_off, sprite_asset_id, b["generation"], flags)

        sig_id = const_to_id[b["signature_const"]] if b["signature_const"] else None
        manifest.append({
            "character": disp, "category": b["category"], "generation": b["generation"],
            "name_offset": name_off, "roster_offset": roster_off,
            "roster_species_ids": [const_to_id[c] for c in b["ordered_consts"]],
            "starter_count": b["starter_count"], "has_signature": b["has_signature"],
            "signature_id": sig_id, "sprite_asset_id": "TBD",
            # Under the playability threshold: the code is refused at the naming
            # screen, but the record and its index stay so an existing save on
            # this character keeps loading and keeps being enforced.
            "hidden": hidden,
        })

    with open(os.path.join(HERE, "characters.bin"), "wb") as f:
        f.write(records)
    with open(os.path.join(HERE, "hidden.bin"), "wb") as f:
        f.write(hidden_bits)
    with open(os.path.join(HERE, "rosters.bin"), "wb") as f:
        f.write(rosters_blob)
    with open(os.path.join(HERE, "names.bin"), "wb") as f:
        f.write(names_blob)
    n_hidden = sum(1 for r in manifest if r["hidden"])
    with open(os.path.join(HERE, "characters_manifest.json"), "w") as f:
        json.dump({"mode": "final", "record_count": len(order),
                   "record_size_bytes": 12, "empty_roster": empty,
                   "selectable_count": len(manifest) - n_hidden,
                   "hidden_count": n_hidden,
                   "warnings": warnings, "characters": manifest}, f, indent=1)

    print("[final] emitted %d characters (%d with an empty roster, kept for index stability)" % (len(order), len(empty)))
    print("  %d selectable, %d hidden below the six-fully-evolved threshold"
          % (len(manifest) - n_hidden, n_hidden))
    print("  characters.bin: %d bytes (%d records x 12)" % (len(records), len(records) // 12))
    print("  hidden.bin:     %d bytes (1 bit per character)" % len(hidden_bits))
    print("  rosters.bin:    %d bytes" % len(rosters_blob))
    print("  names.bin:      %d bytes" % len(names_blob))
    print("\nsprite_asset_id is a PLACEHOLDER (0xFFFF) for every record -- Phase 3 fills")
    print("this in once Seaglass's OW/trainer-pic tables are located (Phase 1).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true",
                     help="emit real binaries (requires Stage B ids); default is --dry-run")
    args = ap.parse_args()

    with open(os.path.join(HERE, "rosters_mapped.json")) as f:
        mapped = json.load(f)
    order = load_order(mapped)

    if args.final:
        cmd_final(mapped, order)
    else:
        cmd_dry_run(mapped, order)


if __name__ == "__main__":
    main()
