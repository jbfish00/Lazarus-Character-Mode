# ROUTINE_MAP — Lazarus v2.0

Confirmed addresses only; candidates are marked. Every entry needs XREF or
live verification before Phase 4 may hook it (standing rule).

## RAM anchors (CONFIRMED 2026-07-15, live + static)

| Symbol | Address | Evidence |
|---|---|---|
| gSaveBlock1Ptr | `0x03003664` | 905 literal-pool refs (top-3 consecutive IWRAM histogram); EWRAM ptr by title screen |
| gSaveBlock2Ptr | `0x03003668` | 719 refs; target begins playerName — decoded "Amali" live after new-game naming (verify_trio.lua) |
| gPokemonStoragePtr | `0x0300366C` | 91 refs; zero-filled target at new game |

Seaglass's trio `0x030051B8/BC/C0` does **not** transfer (reads zero). Method
that worked: static histogram of IWRAM addresses in ROM literal pools →
top three consecutive words → live shape verification. **Feedback loop note:
this static histogram method is exactly how Seaglass's trio was originally
found; the transferable part is the method + consecutive-trio expectation.**

Other frequently-referenced IWRAM words (candidates for later): `0x03003BC0`
(2026 refs — likely gMain or a callback slot), `0x030014B8` (654).

## Data tables (CONFIRMED)

| Table | Address | Evidence |
|---|---|---|
| gSpeciesInfo names | `0x08C7A364`, stride 212, NUM_SPECIES 1561 | docs/SPECIES_CAP.md; XREFs `0x0810243C`, `0x08104948` |

## Pending (Phase 1d–1f)

- SaveBlock1 flags-array offset (via script command table → checkflag handler → FlagGet immediate)
- Script command table (gScriptCmdTable-equivalent)
- Battle strings table + catch-success handler ("Gotcha!" trace)
- GiveMonToPlayer-family / SendMonToPC / ScriptGiveMon
- gPlayerParty + struct stride (find_ram_anchors.lua, needs a party)
- Cheat-code string table + handler ("ILOVEALOLA" etc. — Phase 4 selection mechanism lead)

## Headless bring-up notes (Lazarus-specific)

- Seaglass's patched `mgba-headless` runs Lazarus fine (`--script`, screenshots OK).
- Mashing A from frame 300 (every 60f) reaches new-game naming and accepts a
  default name by ~f=3600 — the intro is shorter than Seaglass's truck intro so far.
- Emulator debug spew is huge (~15 MB/min): ALWAYS redirect to a file and grep
  for `HARNESS` (Seaglass gotcha, reconfirmed).
- `H.mash`/`H.press` take `H.KEY.*` numeric constants, not strings.
