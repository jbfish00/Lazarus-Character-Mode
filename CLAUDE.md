# CLAUDE.md — Lazarus-Character-Mode

Handoff doc for porting **Character Mode** into **Pokemon Lazarus v2.0**. Read this before doing anything in this subproject. Update this file (Status section) at every pause — cold-handoff rule.

## What this is

Opt-in "Character Mode": the player picks 1 of ~184 iconic Pokemon characters and is restricted to catching/keeping only that character's Bulbapedia-documented roster, expanded to full evolution families. Ported from the Pokemon ROWE reference implementation, following the binary-hack methodology proven on Radical Red (shipped) and developed on Seaglass/Unbound/Prism.

## The target ROM

- **Pokemon Lazarus v2.0** by **Nemo622** — the same author as Emerald Seaglass, same stack: closed-source hack built privately on `rh-hideout/pokeemerald-expansion` over Emerald (BPEE). No public source → binary RE + free-space injection + BPS output.
- ROM: `rom/lazarus-v2.gba` (gitignored, chmod 444), 32 MiB, SHA1 pinned in `rom.sha1` = `7dcdc7e280bc4631487e13dd37e6e0cea04adea6`.
- **Provenance verified**: official `../Lazarus_Docs/Lazarus v2 Patch.bps` footer: source CRC32 `0x1F1C08FB` (clean Emerald "TrashMan" dump), target CRC32 `0x558AE42F` — byte-matches the stored CRC of `lazarus-v2.gba` in `../lazarus-v2.zip`. Our ROM is provably the official patch's exact output. Details: `docs/ROM_INFO.md`.
- Official docs: `../Lazarus_Docs/` — general PDF, **Encounters PDF** (drives the obtainability-validation step), Item Locations PDF, dex sprite sheet PNG.
- Dex: curated ~400+ species spanning Gen 1–9. GBC-style visual overhaul, day/night, **DexNav** (extra catch path — must be enforced), Megas.

## Standing rules

1. **Never write `rom/lazarus-v2.gba` in place.** All ROM-mutating work targets `build/` copies (armips two-filename `.open "in","out",addr` form). The source ROM is the SHA1-pinned fixed point (kept chmod 444).
2. **Distribution is a patch, never a ROM.** Our BPS is created against `lazarus-v2.gba` (the official patch's output), NEVER against clean Emerald — a clean-Emerald BPS would embed Nemo622's entire hack. End-user chain: clean Emerald → official BPS → our BPS.
3. **Donor is topology/names only.** The `pokeemerald-expansion` donor clone (reused read-only from `../Seaglass-Character-Mode/tools/pokeemerald_expansion_donor/`) informs struct shapes, call topology, and script-command opcodes. NEVER trust donor numeric `SPECIES_*` IDs — real IDs come from this ROM's own dumped species name table.
4. **Never assume vanilla or Seaglass RAM/ROM addresses hold here.** Same author/engine makes Seaglass values excellent *first guesses* — always verify empirically before recording.
5. Checkpoint rule: update this file + the plan at every pause. Commit only on explicit user request. ROMs/savestates/ghidra projects stay gitignored.
6. Ask questions until 95% confident before consequential decisions.

## Definition of done (user-locked)

Full Radical Red parity: playable `build/lazarus_cm.gba` + distributable `build/lazarus_cm.bps`, character-select at game start, catch/keep enforcement, trade enforcement, **DexNav enforcement verified live**, automated regression suite green (unit + boot smoke + static artifacts + live e2e), end-user README. Sprites only if coverage allows (Track C, never blocks).

## Seaglass feedback loop (user-locked)

Same author/engine → findings likely mirror. When a technique cracks here, apply it to `../Seaglass-Character-Mode/` in a timeboxed excursion (session-end or during background scans only; never preempt the Lazarus critical path mid-step):
- Flags-array offset → try on Seaglass, set flag 0x74, retest its Route 101 gate (45 min).
- Script command table location method → Seaglass FlagGet (30 min).
- Catch-handler trace recipe → Seaglass's 6 standing candidates (60 min).
- Species stride / party anchors → cross-notes in both docs (5 min).
Reverse direction applies too.

## Toolchain

- `tools/bin/armips` v0.11.0, `tools/bin/flips` — proven prebuilt binaries (from Unbound via Seaglass).
- `arm-none-eabi-gcc` (system) for the freestanding Thumb shim (`src/character_mode.c`, RR template).
- **Headless mGBA**: reuse Seaglass's patched build by absolute path — `../Seaglass-Character-Mode/tools/mgba_src/build/mgba-headless` (has the video-buffer screenshot fix + `--script`). Do NOT rebuild. Known gotchas (cost real time on Seaglass — don't relearn):
  - Never pipe its output through `grep|head` — redirect to a file, then grep.
  - Bulk-read RAM with `emu:readRange`, never per-byte loops.
  - Bound every periodic-screenshot loop with a frame check (~1800 fps headless).
  - Key bit indices: A=0 B=1 SELECT=2 START=3 RIGHT=4 LEFT=5 UP=6 DOWN=7 R=8 L=9.
- **Ghidra**: reuse Unbound's Ghidra 12.0.2 + gba loader install; import `-noanalysis` into a Lazarus-local `ghidra_project/`; disassemble on-demand via `tools/ghidra_scripts/` (InspectRegions/DecompileFunc/FindXrefs from Seaglass + CreateAndDecompile from RR). Full auto-analysis times out — don't.
- ROM scanners: `tools/scan_free_space.py`, `search_gametext.py`, `decode_gametext.py`, `find_pointer_refs.py`, `dump_all_strings.py` (game-agnostic; default charmap = ROWE's `charmap.txt`).
- mGBA Lua harness: `tools/mgba_scripts/` (Seaglass suite; `harness.lua` fails loudly on unconfirmed addresses — Seaglass-confirmed values are kept as candidates, not truths).

## RE method (learned the hard way on siblings)

Strings/pointers for **data tables**; **live headless breakpoint tracing for code** — on this engine every code subsystem funnels into indirect jump tables that static Ghidra `-noanalysis` cannot recover. Don't burn time on static code analysis past the first wall. Decoy-table defense: any located table must have code XREFs (`find_pointer_refs.py`), not just matching bytes. Free-space blocks for hooks must be BL-reachable (±4 MB Thumb) or get a trampoline (RR-proven).

## Phases

- **Phase 0** — scaffold + provenance. **DONE** (this commit).
- **Phase 1** — RE: 1a free space → 1b charmap+species table → 1c headless+SaveBlock trio (try Seaglass's `0x030051B8/BC/C0` first) → 1d flags-array offset via script command table→`checkflag`→`FlagGet` immediate (do EARLY — it's the intro-gate skeleton key AND Seaglass's blocker) → 1e intro nav to starter+party (`find_ram_anchors.lua`) → 1f catch-handler live trace ("Gotcha!" string → callers → breakpoints). Exit gate: `docs/ROUTINE_MAP.md` fully confirmed.
- **Phase 2** (Track B, parallel after 1b) — roster pipeline: Stage A (scrape+donor topology, 184-char RR seed) → Stage B (real IDs from `rom_species_table.json`) → **obtainability validation** (new: `extract_encounters.py` + `validate_obtainability.py` from the Encounters PDF; trim list goes to the user before locking) → `emit_characters.py --final` + `emit_bitmaps.py`.
- **Phase 3** (Track C, deferred) — sprites; never blocks.
- **Phase 4** — injection: script-chain character select (RR naming-screen alias pattern, repointed early BG event), enforcement shim gating GiveMonToPlayer-family callers (FULL caller audit first), trades, DexNav verification.
- **Phase 5** — BPS assembly + round-trip verification.
- **Phase 6** — test suite to RR's bar + live e2e (incl. DexNav catch + save/load round-trip) + end-user README.

Full plan: `/home/jbfish00/.claude/plans/plan-how-to-make-dazzling-hammock.md`.

## Status

- **2026-07-15**: Project scaffolded (Phase 0). Tools copied from Seaglass (scanners, Lua harness, ghidra scripts, roster pipeline, armips/flips) and RadicalRed (characters.txt 184-seed, emit_bitmaps.py, CreateAndDecompile.java, shim/injector/test templates, README template). ROM extracted, pinned, read-only; provenance chain recorded. Next: Phase 1a free-space audit + 1b species-table dump; Phase 2 Stage A in parallel.
