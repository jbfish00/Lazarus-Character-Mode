# SPRITE_COVERAGE — Lazarus Character Mode (Phase 3 survey)

Survey run 2026-07-17 via `tools/character_mode/sprite_coverage_survey.py`:
cross-references the **final 179-character manifest**
(`tools/character_mode/characters_manifest.json`) against ROWE's already-built
sprite report (`/home/jbfish00/Documents/Pokemon Rowe Alteration/tools/character_mode/sprite_report.txt`)
— same methodology as `../RadicalRed-Character-Mode/docs/SPRITE_COVERAGE.md`
and Unbound's survey, since the Gen 1–8 slice of this roster is the same set
of real-world characters ROWE already sourced donor art for.

All 179 characters appear in ROWE's 182-entry report (the RR survey's
"no entry at all" cases — Victor/Gloria — plus Hop/Hilbert/Olympia were
already trimmed from this project's roster during obtainability validation,
see `docs/OBTAINABILITY.md`).

## Coverage summary

| | count | % of 179 |
|---|---|---|
| Have an overworld sprite candidate | 100 | 55% |
| Have a trainer front-pic candidate | 70 | 39% |
| Have a battle back-pic candidate | 11 | 6% |
| Have AT LEAST ONE asset | 100 | 55% |
| Have NO assets in ROWE's tree | 79 | 44% |

Full ow+front+back coverage (11): Red, Leaf, Ethan, Kris, Brendan, May,
Steven, Wally, Lucas, Dawn, Barry.

## Zero-coverage pattern (matches the RR/Unbound precedent exactly)

The 79 zero-coverage characters, by generation:

- **Gen 1–5 anime-only (10)**: Ritchie, Tracey, Jessie, James, Lyra, Drew,
  Paul, Zoey, Nando, Trip — ROWE's own status notes already flagged these as
  never sourced.
- **Gen 6 (18)**: Calem, Serena, Diantha, Malva, Siebold, Wikstrom, Drasna,
  Viola, Grant, Korrina, Ramos, Clemont, Valerie, Wulfric, Shauna, Lysandre,
  Alain, Sawyer.
- **Gen 7 (20)**: Elio, Selene, Kukui, Hau, Molayne, Kahili, Acerola, Hala,
  Olivia, Nanu, Hapu, Gladion, Guzma, Plumeria, Lusamine, Lillie (anime),
  Kiawe (anime), Lana (anime), Mallow (anime), Sophocles.
- **Gen 8 (16)**: Leon, Milo, Nessa, Kabu, Bea, Allister, Opal, Gordie,
  Melony, Piers, Raihan, Bede, Marnie, Rose, Goh, Chloe.
- **Gen 9 (15)**: Geeta, Nemona, Rika, Poppy, Hassel, Katy, Brassius, Iono,
  Kofu, Larry, Ryme, Tulip, Grusha, Arven, Penny.

Same underlying reason established on Unbound/RR: GBA-style pixel art
genuinely doesn't exist (official or fan-made) for 3D-model-era characters;
per the long-standing user-accepted policy these get the lighter-weight
text/menu-only treatment, never bespoke pixel art.

## Decision: v1 SHIPS WITHOUT SPRITES — Phase 3 closed as survey-done, injection deferred

Per the definition of done ("sprites only if coverage allows — Track C,
never blocks") and matching the shipped Radical Red precedent (which also
shipped with `sprite_asset_id = 0xFFFF` everywhere and lists sprite
installation as cosmetic-only future work):

- Character Mode on Lazarus is **text-first by design**: selection happens at
  the Acrisia University cheat desk via typed character codes, and no UI
  surface in the shipped feature renders a character sprite. Sprites are
  purely cosmetic polish.
- `characters.bin`'s `sprite_asset_id` field stays `0xFFFF` (placeholder) in
  every record. The field exists so a future sprite pass needs no schema
  change.
- 55% coverage with a hard 44% floor of impossible characters means sprites
  could only ever be partial; that argues for doing it (if ever) as a
  deliberate post-ship cosmetic pass, not as a ship gate.

## If sprites are ever installed (future work, not queued)

1. **ROM-side tables are NOT located** for this ROM: pokeemerald-expansion's
   `gTrainerFrontPicTable` / `gTrainerBackPicTable` / palette tables and
   `gObjectEventGraphicsInfoPointers` equivalents were never hunted (nothing
   in Phase 1 needed them). RR's lesson applies: pull candidate addresses
   from engine-source layout knowledge, then verify byte-exact — and beware
   decoy copies (require code XREFs via `find_pointer_refs.py`).
2. Donor PNGs for the 100 covered characters live in ROWE's tree
   (`graphics/trainers/front_pics/`, `graphics/trainers/back_pics/`,
   `graphics/object_events/`); ROWE's `sprite_report.txt` gives symbol names,
   so symbol → PNG resolution needs ROWE's `spritesheet_rules.mk` /
   `graphics_file_rules.mk`.
3. Injection = LZ77-compress raw tiles/palettes, place in the big free block
   (`0x015F0EA4`+, data placement unconstrained), repoint table entries.
4. Same credits-file discipline as ROWE/RR: a `CREDITS.md` naming
   pret/pokefirered, sinnoh-remakes/pokeemerald-platinum,
   PokemonHnS-Development/pokemonHnS, DiegoWT's Gen5-in-Gen4-style resource,
   StreakOfSprites' Ash sheet.

## 2026-07-23 — Ash Gray donor sourcing (anime-only gap partially closed)

Pokemon Ash Gray v4.5.3 (metapod23) was built locally — BPS patch (RAPatches
mirror) onto a byte-matching pret/pokefirered build — and its sprites ripped
(`RadicalRed-Character-Mode/tools/rip_frlg_sprites.py`). **19 anime-character
trainer front pics** now staged as verbatim LZ77 blobs in
`sprites/donors/ashgray/` (64x64 4bpp + 32 B palette — the same format this
engine family consumes; see that directory's README for provenance).

Coverage delta for the "never sourced" anime-only list: **Ritchie ✓,
Tracey ✓, Jessie ✓ + James ✓ (as a duo pic)** — plus new-to-us Duplica, Todd,
Giselle, A.J., Otoshi, Samurai, Damian, Gary, Cissy, Danny, Rudy, Jessiebelle,
and anime-style Brock/Misty/Oak/Giovanni alternates. Ash overworld
(walk/bike/fishing) + back-pic sheet also ripped.

**Still missing** (web-archive survey 2026-07-23 found no GBA-style front
pics): Drew, Paul, Zoey, Nando, Trip, Lyra; Gen 6-9 policy unchanged
(portrait-only). Candidate OW-only source if ever needed: spherical-ice's
"Accurate FireRed Overworld Sprite Resource" (DeviantArt) — has some anime OW
sprites; The Spriters Resource search is JS-only (not scriptable).

**Pilot injection result (RadicalRed, 2026-07-23)**: all 19 donors injected
at 0x08CF0000 (15,364 B) by `tools/inject_sprites_pilot.py` (RR repo);
decode-back from the built ROM byte-exact; `gTrainerFrontPicTable`
consumption confirmed (12 literal-pool code refs incl. battle engine); the
all-slots test build boots to free-roam. The blob-copy + table-repoint
technique transfers to this project once its own table addresses are located.
