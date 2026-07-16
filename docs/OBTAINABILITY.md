# OBTAINABILITY — Lazarus v2.0 (validated 2026-07-15)

New pipeline step Seaglass lacked, made possible by the official docs bundle.

## Pipeline

1. `tools/character_mode/extract_encounters.py` — pdftotext over the official
   Encounters PDF → `encounters.json`. **284 wild species resolved, 0 unmatched
   fragments** (form qualifiers stripped: Alolan/Galarian/Hisuian/Paldean,
   Flabébé flower colors, Oricorio styles, Minior cores, Basculin stripes;
   PDF typo "Sligoo"→Sliggoo aliased).
2. `tools/character_mode/validate_obtainability.py` — obtainable family bases =
   wild ∪ enumerable gifts (9 starters; cheat-code trios ILOVEALOLA/ILOVEKALOS/
   ILOVPALDEA/IWANTMONKE/IMISSJOHTO; WORLDCHAMP Litten, MASKEDOGRE Ogerpon,
   LEGENDS ZA Floette, HOUSESTARK Rockruff, MOSEY Meowth). Evolution closure is
   implicit (rosters store family bases). → `obtainability_report.json`.

**Result: 186 obtainable family bases.** Every gift species is also wild.

## Known gaps (can only ADD obtainability — trim is conservative)

- In-game trades (RE'd in Phase 4), unlisted quest gifts, fossil species
  (Fossil House on Marmaro Island; species not enumerated in the PDFs),
  random-pool codes (NEMOS FAVE, WATCHPHAUN, MONO *).
- Ogerpon has no donor const in the Stage A parser (macro-form) — warning only,
  no character roster depends on it.

## Trim decision (user-approved 2026-07-15)

Cut **5** characters (commented in `characters.txt` with reason):

| Character | Obtainable | Note |
|---|---|---|
| Gloria, Hop, Victor | 0 | Galar rosters absent from Lazarus's dex entirely |
| Hilbert | 1 (Eevee) | single-family run, cut per Seaglass precedent |
| Olympia | 1 (Froakie) | single-family run, cut per Seaglass precedent |

**Final list: 179 characters.** 0 empty, 0 single-species; mean 8.8 obtainable
species per character (median expanded-bitmap size 32 ids, max 97, min 6).

## Emitted artifacts (Phase 2 exit gate met)

| File | Size | Contents |
|---|---|---|
| `characters.bin` | 2,148 B | 179 × 12-byte records (sprite_asset_id still 0xFFFF placeholder pending Phase 3) |
| `rosters.bin` | 3,874 B | u16 base-species ROM ids, SPECIES_NONE-terminated |
| `names.bin` | 1,169 B | Gen3-charmap names, 0xFF-terminated |
| `rosters_expanded.bin` | 35,084 B | 179 × 196-byte allowed-species bitmaps (1561 bits, LSB-first; includes all evolution stages + all form indices per family) |

## Phase 4 lead discovered during extraction

Lazarus has a **native cheat-code system** (10-char codes: "ILOVEALOLA",
"9RARECANDY", "JUSTCATCH!", …) that already grants Pokemon and toggles modes.
This is exactly the RR character-select pattern (naming-screen code entry) —
locate the code string table + handler in ROM (`search_gametext.py` on the code
strings) and the selection mechanism may be an *extension of an existing
data-driven table* rather than a repointed BG event. Strong candidate to
simplify Phase 4 significantly.
