# SPECIES_CAP — Lazarus v2.0 species table (verified 2026-07-15)

## Table location (gSpeciesInfo-analogue)

| Property | Value |
|---|---|
| Name-field base | ROM offset `0x00C7A364` (addr `0x08C7A364`), names at struct offset 0 |
| Stride | **212 bytes** (Seaglass was 208 — different expansion snapshot) |
| Indexing | SPECIES id: natdex order for base species (Caterpie=10, Pikachu=25, Fennekin=653, Rowlet=722), Gen 9 block starts at **Sprigatito=1289** (pre-natdex-refactor expansion layout), forms interleaved ~1000–1560 |
| Last real index | **1560** (Golisopod form entry) → **NUM_SPECIES = 1561** |
| Code XREFs (decoy defense) | Literal pools at `0x0810243C` and `0x08104948` point to the base ✓ |

Dump: `tools/dump_species_table.py` → `tools/character_mode/rom_species_table.json`.

## The curated-dex mechanism

**Pruned species have blanked names in the table itself** — e.g. Bulbasaur(1), Charmander(4), Squirtle(7), Mewtwo(150), Mew(151), Treecko(252) are blank while Pikachu(25) etc. are present. **661 named entries** out of 1561 slots (≈400+ base species + forms), matching the marketing claim.

Implications:
- Stage B roster resolution: match against named entries only; blank = genuinely absent from Lazarus.
- Bitmap sizing (`emit_bitmaps.py`): width = 1561 bits → 196 bytes per character (u8-aligned).
- Enforcement shim NUM_SPECIES boundary check: 1561.

## Notable form entries (for Stage B collision policy)

Duplicate names at multiple indices (Palafin 1352/1353, Tauros 1402–1404, Pikachu 25/1487/1493, Raichu 1543/1544, Mega/regional blocks). Policy unchanged from siblings: **lowest index wins = base form**; ambiguities logged to `stageb_ambiguous.txt`.

## Seaglass cross-note (feedback loop)

Same shape family confirmed on a second Nemo622 build: name-first struct, dex-ordered, stride drifts per expansion snapshot (208 vs 212). Method transfer: find title-case starter names → fit `base + stride*id` on two knowns → verify broadly → require code XREFs.
