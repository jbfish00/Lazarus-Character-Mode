# Intro navigation — Lazarus v2.0

Phase 1e log. All savestates under `tools/savestates/` (gitignored).
Run everything WITHOUT `MGBA_HEADLESS_DEBUGGER` unless breakpoints are needed
(armed breakpoints single-step the core).

## Big picture (2026-07-16): the intro is A-mash-only — no hard gates

Unlike Seaglass (truck, wall-clock minigame, flag-gated town exit), Lazarus's
entire opening runs on scripted rails: **mashing A every 60 frames from boot
reaches a free overworld with the starter in the party in ~12,000 frames
(~7 s wall-clock headless)**. No directional input, no minigame, no gate.

Sequence observed (`intro_to_spawn.lua` → `continue_intro.lua` →
`finish_nickname.lua`):

1. Boot → title → new-game naming: accepts default name by ~f3600
   (name ends up "Amali" — default confirmed via SB2 playerName).
2. New-game init fires ~f5175 (933 FlagSet/Clear ops — the
   verify_flags_offset.lua run), spawn on **map 0.57** (starting town) at
   (6,34).
3. **Scripted Prof. Elia walk**: the game auto-walks the player through town
   ((8,34)→(8,27)→(13,27)→(13,13)→(33,8), Elia commenting) into her **lab,
   map 0.58**. "Oho! Looks like a few Pokémon are out and about this
   morning!" → students dialogue.
4. **Starter selection inside the lab** — A-mash takes the default:
   **Popplio** (lvl 5). (A deliberate character run will need to see the
   actual selection UI — revisit from `spawn.ss` with slower stepping when
   Phase 4 needs it.)
5. Nickname prompt (A-mash enters it and types "Aaaaaaa…" — deliberately kept:
   the BB D5 D5 D5 nickname bytes are how the party struct was located).
   START→A confirms.
6. Free overworld in the lab at (6,12) map 0.58.

## Savestates

| File | Where |
|---|---|
| `spawn.ss` | f7400 from boot: mid-Elia-walk, town map 0.57, (28,13) |
| `c1_end.ss` | Popplio nickname screen in the lab (typed "Aaaa…") |
| `have_starter.ss` | **free overworld, lab (6,12) map 0.58, party = 1× lvl-5 Popplio named "Aaaaaaaa"** — the working state for 1f catch tracing |

## What this unlocked (see ROUTINE_MAP.md)

- gPlayerParty `0x0201B960` (stride 100), gPlayerPartyCount `0x0201B95D`,
  gEnemyParty `0x0201BBB8`.

## Next (1f)

From `have_starter.ss`: exit the lab, find tall grass (Encounters PDF: the
first route's day/night tables), trigger a wild battle, savestate, then
breakpoint-trace the catch handler (`MGBA_HEADLESS_DEBUGGER=1`; needs Poké
Balls — check the bag / buy / or find a gift; Seaglass stalled exactly on
having no balls, check early).
