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

- **2026-07-16 (b)**: **Phases 1e + 1f complete — PHASE 1 EXIT GATE CLOSED.** Full detail in docs/ROUTINE_MAP.md (all confirmed) + docs/INTRO_NAVIGATION.md.
  - 1e: intro is A-mash-only (no gates). Starter = default **Popplio** lvl 5 from Prof. Elia's lab (map 0.58). **gPlayerParty `0x0201B960` stride 100 / count `0x0201B95D` / gEnemyParty `0x0201BBB8`.** Savestates: `spawn.ss`, `c1_end.ss` (nickname screen), `have_starter.ss`, `del_end.ss` (town, near mart stall), `wild_battle.ss` (live wild Hoppip battle, 10 Poké Balls in bag), `battle_menu.ss`/`battle_bag.ss`, `after_catch.ss` (party of 2 post-catch).
  - 1f: **caught a wild Hoppip fully headlessly** and traced it with write-watchpoints: **GiveMonToPlayer `0x081C40BC`** (live-pinned), CopyMonToPC `0x081C4130`, ScriptGiveMon `0x0820D3F4`, CreateMon `0x080FC358`, Get/SetMonData `0x081C2FB8`/`0x081C37B0`. **Only 3 GiveMonToPlayer callers** (BL scan): battle/catch `0x080A7BDA`, daycare/hatch `0x0819FC8E`, script gift `0x0820D416` — the whole Phase 4 audit surface.
  - Bag cracked as a byproduct (needed balls — story hadn't given any; Rotom-Phone fetch quest skipped): AddBagItem `0x0815CCD0`, pocket table EWRAM `0x0200B0D8`, **qty XOR key = u16 @ SB2+0xB0**, gItemsInfo `0x08868520` (stride 80, name +0x3C, pocket +0x69, **Poké Ball = item id 1**). `give_pokeballs.lua` = working "give item" debug capability.
  - Gotchas: `H.finish()` does NOT stop the emulator (bound loops externally with `timeout`); watchpoints single-step like breakpoints (a 3500-frame catch run ≈ 10 min wall) — arm them as late as possible.
  - Next: **Phase 4 injection** (Track C sprites still deferred): selection mechanism (cheat-code system lead — find its string table/handler; several codes give mons), enforcement shim gating the 3 callers, trades, DexNav verify. Also pending: Seaglass feedback checkpoint #2 (catch-trace recipe → its 6 candidates; use watchpoint-on-partyCount method, their party globals are known).
- **2026-07-16 (a)**: **Phase 1d complete — flags + vars fully mapped, and headless breakpoints FIXED.**
  - Script command table found statically: **`0x0828C7DC`, 0xEF (239) cmds** via new `tools/find_script_cmd_table.py` (scans for the cmdTable/cmdTableEnd adjacent literal-pool-pair signature from the donor's ScriptContext init — single clean hit, 4 XREF pairs; engine-generic, works on any pokeemerald/pokefirered-family binary).
  - From cmd entries 0x29/2A/2B/0x16: FlagSet `0x0811478C`, FlagClear `0x08114844`, FlagGet `0x081148A0`, GetFlagPointer `0x08114754`, GetVarPointer `0x08114600`, ScriptReadHalfword `0x0820B1A4`, setvar handler `0x08208689`. **SaveBlock1: flags at `+0x12E8`, vars at `+0x1414`** (each derived from two independent code paths; deltas internally consistent — 0x12C flag bytes, vanilla count, shifted +0x78).
  - **Toolchain breakthrough (cross-project)**: `emu:setBreakpoint` NEVER worked on stock mgba-headless (returns -1: `core->debugger` is never created) — all prior breakpoint-based trace scripts silently logged nothing, which retroactively explains Seaglass's catch-trace stall and its "needs GUI + human" conclusion. Patched `../Seaglass-Character-Mode/tools/mgba_src/src/platform/headless-main.c` to attach a module-less debugger when **`MGBA_HEADLESS_DEBUGGER=1`** (additive, env-gated; free until breakpoints are armed, single-steps after) and rebuilt. Verified: 933 FlagSet/FlagClear ops traced live; all 195 distinct flags match bit state at `sb1+0x12E8` (`verify_flags_offset.lua` PASS). **Phase 1f live catch-trace is now fully unblocked headless.**
  - harness.lua: `H.SB1_FLAGS_OFF/H.SB1_VARS_OFF` + `flagGet/flagSet/varGet/varSet` helpers added; `H.breakpoint` now fails loudly if registration fails. New scripts: `verify_flags_offset.lua`, `bp_diag.lua`. Gotcha: SB1 base relocates on new game (`0x0200E580`→`0x0200E55C`) — deref fresh.
  - **Seaglass feedback checkpoint #1 DONE (same day)**: scanner found Seaglass's cmd table instantly (`0x0826D970`, 0xE7 cmds) → TRUE offsets flags `+0x13C0` / vars `+0x14EC`, live-verified 61/61 FlagGet round-trips via the new breakpoints. Big correction landed in Seaglass: its "flags base +0x157E / flag 0x74 gate" finding was actually **var 0x4050** (vars+2·0x50) and the Littleroot gate is a coord trigger on that var — flag 0x74 never opened it (live-disproven; its harness/scripts/docs corrected). Cross-notes added to Unbound, RadicalRed, Prism CLAUDE.md files. Lesson reinforced: same-author offsets do NOT transfer (0x12E8 vs 0x13C0), methods do.
  - **Phase 1e also DONE (same day, unexpectedly fast)**: Lazarus's intro has NO hard gates — A-mash-only from boot to free-overworld-with-starter (~12k frames): naming → new-game init → scripted Prof. Elia walk (town 0.57 → lab 0.58) → starter (default pick = **Popplio** lvl 5) → nickname → free. **gPlayerParty `0x0201B960` (stride 100, 587 refs), gPlayerPartyCount `0x0201B95D`, gEnemyParty `0x0201BBB8`** — found via typed-nickname byte pattern + ref-count disambiguation, live-verified. Savestates: `spawn.ss`, `c1_end.ss`, `have_starter.ss`. docs/INTRO_NAVIGATION.md written. New scripts: `intro_to_spawn.lua`, `continue_intro.lua`, `finish_nickname.lua`, `probe_party.lua`.
  - Next: **1f catch trace** — from have_starter.ss: exit lab → tall grass → wild battle savestate → breakpoint trace (MGBA_HEADLESS_DEBUGGER=1). Check Poké Ball availability EARLY (Seaglass's stall). Note: cmd-table entry[0x79] looks re-tabled (nop) — givemon lives elsewhere; the mon-giving cheat codes are an alternative give-family XREF source.
- **2026-07-15 (c)**: **Phase 1c complete — headless bring-up + SaveBlock trio.** Seaglass's `mgba-headless` runs Lazarus. Trio found by static literal-pool histogram + live verification (playerName "Amali" decoded in SB2 after A-mash through naming): **gSaveBlock1Ptr `0x03003664`, gSaveBlock2Ptr `0x03003668`, gPokemonStoragePtr `0x0300366C`** (Seaglass's addresses do NOT transfer; the *method* does). harness.lua updated; docs/ROUTINE_MAP.md started. New scripts: `find_saveblock_trio.lua`, `verify_trio.lua`. Gotcha: harness input takes `H.KEY.*` constants, not strings. Next: 1d flags-array offset (static, via script cmd table → FlagGet) + Seaglass feedback checkpoint #1; then 1e intro nav (A-mash already reaches naming ~f3600), 1f catch trace.
- **2026-07-15 (b)**: **Phases 1a, 1b, and ALL of Phase 2 complete.**
  - 1a: one 10.06 MiB 0xFF free block at `0x015F0EA4`→EOF (docs/FREE_SPACE.md); BL-unreachable from low ROM → trampolines needed for hooks; data unconstrained.
  - 1b: charmap intact ("Ilios" 200 hits). Species table at name-base `0x00C7A364`, **stride 212**, dex-indexed, Gen9 at 1289+, last index 1560 → **NUM_SPECIES=1561**; XREFs at `0x0810243C`/`0x08104948` (docs/SPECIES_CAP.md). Curated dex = blanked names in-table (666 named). Dumper: `tools/dump_species_table.py` (handles é; emits Stage-B schema).
  - Phase 2: Stage A 184 chars → Stage B 207 consts resolved → **obtainability validation** (new, docs/OBTAINABILITY.md): 284 wild + gifts = 186 obtainable bases → user-approved trim of 5 (Gloria/Hop/Victor 0, Hilbert/Olympia 1) → **179 characters final**, all binaries emitted incl. `rosters_expanded.bin` (179×196B bitmaps, sanity-checked). Note: `scrape_rosters.py` MERGES into existing rosters_raw.json — delete it when changing characters.txt.
  - **Phase 4 lead**: Lazarus has a native 10-char cheat-code system ("ILOVEALOLA" etc., see docs/OBTAINABILITY.md) — likely the character-select mechanism; find its string table/handler first.
  - Next: 1c headless bring-up + SaveBlock trio (try `0x030051B8/BC/C0`), 1d flags offset (then Seaglass feedback checkpoint #1), 1e intro nav, 1f catch trace. Phase 3 sprite survey pending.
- **2026-07-15 (a)**: Project scaffolded (Phase 0). Tools copied from Seaglass (scanners, Lua harness, ghidra scripts, roster pipeline, armips/flips) and RadicalRed (characters.txt 184-seed, emit_bitmaps.py, CreateAndDecompile.java, shim/injector/test templates, README template). ROM extracted, pinned, read-only; provenance chain recorded.
