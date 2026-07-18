#!/usr/bin/env python3
"""Emit per-character wild-encounter override tables for the Phase 7 shim.

New feature (2026-07-17): a 10% chance for wild encounters (grass/cave,
surf, rock smash, all fishing rods) to be overridden with a member of the
active character's roster, picking the evolution STAGE whose canon level
range best fits the level the game originally rolled.

Data needed that the existing pipeline doesn't have: per-species evolution
LEVEL thresholds, so we can compute a [minLevel, maxLevel] window for every
stage of every family a roster base belongs to. The donor's
src/data/pokemon/species_info/gen_N_families.h inlines exactly this
(`.evolutions = EVOLUTION({EVO_LEVEL, 16, SPECIES_IVYSAUR})`); non-level
evolution methods (item/trade/friendship/move/etc.) carry no level, so a
level-proportional default breakpoint is substituted (16 for stage1->2,
36 for stage2->3, +20 per stage beyond that) -- this only affects the
*window edges* for non-level branches, never which species are eligible.

LEGENDARY EXCLUSION: characters_manifest.json's `roster_species_ids` is
already split as `[0:starter_count]` = non-legendary bases,
`[starter_count:]` = legendary/mythical bases (emit_characters.py's
LEGENDARY_BASES filter). We only ever expand the non-legendary slice here --
legendaries never enter this table, so the runtime shim needs no legendary
check at all.

Output: wildmons.bin -- NUM_CHARACTERS x WILDMON_STRIDE bytes. Each
character's region is a sequence of 4-byte entries {u16 species, u8
minLevel, u8 maxLevel}, terminated by a species=0 sentinel entry, zero-
padded to the stride. WILDMON_STRIDE is computed from the real maximum
entry count actually needed (printed at the end) plus the terminator.

Entries are grouped by roster BASE (family), in roster order, not sorted
globally -- the shim needs family boundaries intact to implement "pick a
RANDOM roster member, then its best-fitting stage" (not "pick whichever
stage across all families fits best", which would silently favor whichever
family's window happens to match first). Bit 15 of the species field marks
the first entry of each family group (species ids fit in 11 bits, NUM_SPECIES
1561, so the top bits are always free for this).
"""
import json
import re
import struct
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from map_species import load_donor, first_stage_map, MACRO_FORM_CONST_OVERRIDES, FAMILY_DIR, FAMILY_FILES  # noqa: E402

NUM_SPECIES = 1561
MAX_STAGES = 6            # safety cap on chain-walk depth (no real family is this deep)
DEFAULT_BASE = 16         # fallback level for a stage1->2 non-level evolution
DEFAULT_STEP = 20         # each subsequent fallback threshold adds this
FAMILY_START_BIT = 0x8000


def norm(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())


def parse_children_with_levels(path):
    """Like map_species.parse_family_file, but keeps (target_const, level)
    pairs instead of collapsing to a bare set -- level is the EVO_LEVEL
    numeric param when present, else None for every other evolution method."""
    text = path.read_text(encoding="utf-8")
    starts = list(re.finditer(r"\[(SPECIES_[A-Z0-9_]+)\]\s*=\s*\{", text))
    out = {}
    for i, m in enumerate(starts):
        const = m.group(1)
        block_start = m.end()
        block_end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        block = text[block_start:block_end]
        evo_m = re.search(r"\.evolutions\s*=\s*EVOLUTION\(", block)
        children = []
        if evo_m:
            captured = []
            for line in block[evo_m.end():].split("\n"):
                if line.strip().startswith(".") and "=" in line:
                    break
                captured.append(line)
            evo_text = "\n".join(captured)
            for tm in re.finditer(
                    r"\{\s*(EVO_[A-Z0-9_]+)\s*,\s*([^,]+),\s*(SPECIES_[A-Z0-9_]+)", evo_text):
                method, param, target = tm.group(1), tm.group(2).strip(), tm.group(3)
                if target == const:
                    continue
                level = None
                if method == "EVO_LEVEL":
                    try:
                        level = int(param, 0)
                    except ValueError:
                        level = None
                    # EVO_LEVEL is reused for friendship/time/location-gated
                    # evolutions with param=0 and the real condition living in
                    # a trailing CONDITIONS(...) (e.g. Eevee->Espeon/Umbreon,
                    # Nosepass->Probopass) -- 0 is never a real evolution
                    # level, treat it as "no level info" like any other
                    # non-level method so the fallback breakpoint applies.
                    if level == 0:
                        level = None
                out.setdefault(const, []).append((target, level))
    return out


def load_children_with_levels():
    merged = {}
    for fname in FAMILY_FILES:
        for const, kids in parse_children_with_levels(Path(FAMILY_DIR) / fname).items():
            merged.setdefault(const, []).extend(kids)
    return merged


def build_chain(base_const, children):
    """Walk base_const forward, one deterministic branch at a time (sorted by
    target const name for reproducibility), recording the level threshold at
    which each stage becomes the next. Returns [(const, level_in)], where
    level_in is the level the PREVIOUS stage evolves at to reach this one
    (None for the base stage itself)."""
    chain = [(base_const, None)]
    seen = {base_const}
    cur = base_const
    for _ in range(MAX_STAGES - 1):
        kids = children.get(cur, [])
        if not kids:
            break
        kids = sorted(kids, key=lambda t: (t[1] is None, t[0]))
        nxt, lvl = kids[0]
        if nxt in seen:
            break
        chain.append((nxt, lvl))
        seen.add(nxt)
        cur = nxt
    return chain


def stage_windows(chain):
    """[(const, minLevel, maxLevel)] covering 1..100 with no gaps, using real
    EVO_LEVEL thresholds where known and DEFAULT_BASE/+DEFAULT_STEP fallback
    breakpoints otherwise."""
    n = len(chain)
    thresholds = []  # thresholds[i] = level at which stage i -> stage i+1
    for i in range(1, n):
        lvl = chain[i][1]
        if lvl is None:
            lvl = DEFAULT_BASE + DEFAULT_STEP * (i - 1)
        # keep monotonic increasing even if donor data is inconsistent
        if thresholds and lvl <= thresholds[-1]:
            lvl = thresholds[-1] + 1
        thresholds.append(min(lvl, 100))
    windows = []
    lo = 1
    for i in range(n):
        hi = thresholds[i] - 1 if i < len(thresholds) else 100
        hi = max(hi, lo)
        windows.append((chain[i][0], lo, hi))
        lo = thresholds[i] if i < len(thresholds) else 100
    return windows


def main():
    rom_table = json.load(open(HERE / "rom_species_table.json"))["species"]
    manifest = json.load(open(HERE / "characters_manifest.json"))

    name_to_const, parent = load_donor()
    for nm, c in MACRO_FORM_CONST_OVERRIDES.items():
        name_to_const.setdefault(nm, c)
    children = load_children_with_levels()

    donor_by_norm = {norm(nm): c for nm, c in name_to_const.items()}
    name_of_const = {c: nm for nm, c in name_to_const.items()}
    rom_ids_by_norm = {}
    id_to_norm = {}
    for idx_str, nm in rom_table.items():
        n = norm(nm)
        rom_ids_by_norm.setdefault(n, set()).add(int(idx_str))
        id_to_norm[int(idx_str)] = n

    def rom_id_for_const(c):
        nm = name_of_const.get(c)
        if not nm:
            return None
        ids = rom_ids_by_norm.get(norm(nm))
        return min(ids) if ids else None

    per_char = []
    max_entries = 0
    unresolved = []
    for rec in manifest["characters"]:
        if "roster_species_ids" not in rec:
            per_char.append([])
            continue
        bases = rec["roster_species_ids"][: rec["starter_count"]]  # legendaries EXCLUDED by construction
        families = []         # list of per-base stage-window lists (grouping preserved)
        seen_species = set()
        for sid in bases:
            if not (0 < sid < NUM_SPECIES):
                continue
            n = id_to_norm.get(sid)
            c = donor_by_norm.get(n) if n else None
            if c is None:
                unresolved.append((rec["character"], sid, n))
                continue
            base_const = c  # roster ids are already family bases (Stage A/B)
            chain = build_chain(base_const, children)
            family_entries = []
            for const, lo, hi in stage_windows(chain):
                rid = rom_id_for_const(const)
                if rid is None or not (0 < rid < NUM_SPECIES) or rid in seen_species:
                    continue
                seen_species.add(rid)
                family_entries.append((rid, lo, hi))
            if family_entries:
                families.append(family_entries)
        per_char.append(families)
        max_entries = max(max_entries, sum(len(f) for f in families))

    stride_entries = max_entries + 1  # +1 for the SPECIES_NONE terminator
    stride = stride_entries * 4
    out = bytearray()
    for families in per_char:
        n = 0
        for family_entries in families:
            for j, (rid, lo, hi) in enumerate(family_entries):
                sp = rid | (FAMILY_START_BIT if j == 0 else 0)
                out += struct.pack("<HBB", sp, lo, hi)
                n += 1
        pad = stride - n * 4
        out += b"\x00" * pad

    (HERE / "wildmons.bin").write_bytes(out)
    total_entries = sum(sum(len(f) for f in families) for families in per_char)
    print(f"emitted {len(per_char)} characters x stride {stride} "
          f"(max {max_entries} stage entries, {total_entries} total) = {len(out)} bytes -> wildmons.bin")
    if unresolved:
        print(f"  WARNING: {len(unresolved)} roster bases had no donor const (skipped in wildmons):")
        for ch, sid, nm in unresolved[:10]:
            print(f"    {ch}: id {sid} ({nm})")
    zero = sum(1 for families in per_char if not families)
    if zero:
        print(f"  NOTE: {zero} characters have 0 wild-override entries (all-legendary or "
              f"unresolved roster) -- override silently no-ops for them (falls through to the roll).")


if __name__ == "__main__":
    main()
