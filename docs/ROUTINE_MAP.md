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
| gScriptCmdTable | `0x0828C7DC`, **0xEF (239) commands**, end `0x0828CB98` | `tools/find_script_cmd_table.py` (cmdTable/cmdTableEnd adjacent literal-pool-pair signature); 4 pool XREF pairs at ROM offsets `0x20B268/0x20B2F4/0x20B36C/0x20B4CC` (script.c engine, consistent with ScriptReadHalfword below); entries 0x29/2A/2B are 3 near-identical 16-byte handlers (setflag/clearflag/checkflag trio) |
| gSpecialVars ptr table | `0x0828CB9C` (4 bytes after cmd-table end) | referenced by GetVarPointer's ≥0x8000 path |

## Script engine + flags/vars (CONFIRMED 2026-07-16, Phase 1d — static disasm + live)

| Symbol | Address | Evidence |
|---|---|---|
| ScriptReadHalfword | `0x0820B1A4` | called by setflag/clearflag/checkflag/setvar handlers |
| GetVarPointer | `0x08114600` | from setvar handler (cmd 0x16 = `0x08208689`) |
| GetFlagPointer | `0x08114754` | flags.c layout, same math as FlagSet |
| FlagSet | `0x0811478C` | bl target of setflag handler (cmd 0x29 = `0x08208AD1`) |
| FlagToggle | `0x081147EA` | same shape as FlagSet but `eors` |
| FlagClear | `0x08114844` | bl target of clearflag handler (cmd 0x2A) |
| FlagGet | `0x081148A0` | bl target of checkflag handler (cmd 0x2B = `0x08208AF1`), result → ctx->comparisonResult |

**SaveBlock1 layout (the Phase 1d prize):**

| Field | Offset | Evidence |
|---|---|---|
| flags[0x12C] | **`+0x12E8`** | FlagSet & GetFlagPointer both compute `*0x03003664 + 0x12E8 + id/8` (pool literals); **live passive**: after new-game init (map 0.57, f≈6900) region +0x12E8..+0x1414 went 0 → 49 nonzero bytes while control region +0x1270 (vanilla offset) stayed all-zero (`bp_diag.lua`); **live active** (`verify_flags_offset.lua`): breakpoints on FlagSet/FlagClear captured 933 ops / 195 distinct flag ids during init — final bit state at +0x12E8 matches all 195 |
| vars | **`+0x1414`** | GetVarPointer computes `*0x03003664 + 2*(id-0x4000) + 0x1414`; live: 11 nonzero vars after init. Cross-check: 0x1414−0x12E8 = 0x12C = exactly 300 flag bytes (2400 flags, vanilla count; whole block shifted +0x78 vs vanilla 0x1270/0x139C) |

Special flags (id ≥ 0x4000): EWRAM `0x02005618` (block base for id 0x4000). Special vars (id ≥ 0x8000): ptr table `0x0828CB9C`. VARS_START = 0x4000, id < 0x4000 → GetVarPointer returns NULL — all vanilla-compatible.

Phase-4-relevant handlers already located: `setvar` `0x08208689` (0x16), `addvar` `0x082088A1` (0x17), `copyvar` `0x082086A9` (0x19), `setorcopyvar` `0x082086CD` (0x1A).

Note: SB1 pointer relocates on new game (0x0200E580 → 0x0200E55C observed) — always deref `0x03003664` fresh, never cache across a new-game boundary.

## Party globals (CONFIRMED 2026-07-16, Phase 1e — live + ref-count)

| Symbol | Address | Evidence |
|---|---|---|
| gPlayerParty | `0x0201B960`, stride **100** | starter found by typed-nickname pattern (BB D5 D5 D5 @ +8); 587 raw ROM refs (transient copies have ~0); slot0 lvl=5 hp=20/20 matches on-screen starter |
| gEnemyParty | `0x0201BBB8` | = party+600 → stride 100; 233 refs; zero-filled outside battle |
| gPlayerPartyCount | `0x0201B95D` (u8) | 51 refs; reads 1 with a 1-mon party (vanilla count-3-bytes-before-party layout) |

## Give-mon family (CONFIRMED 2026-07-16, Phase 1f — live watchpoint trace + static)

Found by catching a real wild Hoppip headlessly (`catch_trace.lua` from
`wild_battle.ss`) with WRITE watchpoints on gPlayerPartyCount + party slot 1:
count went 1→2, slot 1 received the wild mon's exact PID, and the faulting PC
pinned the give function. Static BL-scan then enumerated every caller.

| Symbol | Address | Evidence |
|---|---|---|
| **GiveMonToPlayer** | `0x081C40BC` | live: count-write watchpoint fired at its `strb` (0x081C411C) during the catch; disasm is the exact donor shape (SetMonData OT fields from SB2, scan 6×100 party slots, memcpy into free slot, count=i+1, full→PC fallback). Literal pools independently re-confirm gPlayerParty `0x0201B960` + count `0x0201B95D` + gSaveBlock2Ptr `0x03003668` |
| **CopyMonToPC** (SendMonToPC-equiv) | `0x081C4130` | GiveMonToPlayer's full-party fallback (bl @0x081C4102) |
| **ScriptGiveMon** | `0x0820D3F4` | script-engine caller: builds a mon on the stack via CreateMon then BLs GiveMonToPlayer @0x0820D416 (vanilla's givemon cmd slot 0x79 is re-tabled to a nop here — the script path enters via this special instead) |
| CreateMon | `0x080FC358` | called by ScriptGiveMon with (mon*, species, level, …) |
| GetMonData | `0x081C2FB8` | empty-slot probe inside GiveMonToPlayer |
| SetMonData | `0x081C37B0` | OT-name/gender stamping inside GiveMonToPlayer |
| memcpy | `0x083E7F2C` | slot copy; also used by AddBagItem |

**Complete caller set of GiveMonToPlayer (Thumb BL scan over whole ROM — the
Phase 4 hook/audit surface, only 3):**

| BL site | Subsystem | Classification |
|---|---|---|
| `0x080A7BDA` | battle engine | **the catch path** (only battle-engine caller; active during our live catch) |
| `0x0819FC8E` | daycare/hatch region | daycare-withdraw/hatch family (works over 100-byte records + daycare struct); audit in Phase 4, egg-exemption decision applies |
| `0x0820D416` | script engine | ScriptGiveMon (gift path) |

CopyMonToPC's other callers: `0x0820DB1E`, `0x0820DD94` (script gift-to-PC
variants — audit with the above).

## Bag / items (CONFIRMED 2026-07-16 — byproduct of getting Poké Balls)

| Symbol | Address | Evidence |
|---|---|---|
| AddBagItem | `0x0815CCD0` | bl target of additem handler (cmd 0x44 = `0x08208915`); VarGet = `0x08114644`; gSpecialVar_Result = `0x0200560C` |
| Bag pocket descriptor table | EWRAM `0x0200B0D8`, stride 8: {u32 slots*, u8 capacity} | from AddBagItem disasm; pocket 2 = Poké Balls (cap 20, slots→`0x0200EBB8` in our save) |
| Item quantity XOR key | u16 @ `SB2+0xB0` | AddBagItem's `eors`; live-verified (wrote 10 balls, bag UI shows "Poké Ball ×10") |
| gItemsInfo | `0x08868520`, stride 80; name inline +0x3C, pocket byte +0x69; max id 0x362 | "Poké Ball" found inline at item **id 1** (expansion re-ids: 1=Poké, 2=Great, 3=Ultra, 4=Master…) |

## Phase 1 EXIT GATE: CLOSED (2026-07-16)

Catch handler caller ✓, gift handler (ScriptGiveMon) ✓, SendMonToPC ✓,
gPlayerParty+stride ✓, SaveBlock trio ✓, flags/vars offsets ✓, script command
table ✓, free space ✓. Remaining leads for Phase 4 (not gate items):
cheat-code string table + handler ("ILOVEALOLA" — selection mechanism
candidate), DexNav funnel verification (unlocks post-gym-2; regression-test in
Phase 6).

## Headless bring-up notes (Lazarus-specific)

- Seaglass's patched `mgba-headless` runs Lazarus fine (`--script`, screenshots OK).
- Mashing A from frame 300 (every 60f) reaches new-game naming and accepts a
  default name by ~f=3600 — the intro is shorter than Seaglass's truck intro so far.
- Emulator debug spew is huge (~15 MB/min): ALWAYS redirect to a file and grep
  for `HARNESS` (Seaglass gotcha, reconfirmed).
- `H.mash`/`H.press` take `H.KEY.*` numeric constants, not strings.
- **`emu:setBreakpoint` needs `MGBA_HEADLESS_DEBUGGER=1`** (2026-07-16). Stock
  headless never creates `core->debugger`, so script breakpoints returned `-1`
  and silently never fired (0 hits on FlagGet across 6900 frames — harness's
  "empirically verified" claim covered callability, not firing; this also
  explains why Seaglass's breakpoint trace scripts were dead ends headless).
  **Fixed** by a local patch to `mgba_src/src/platform/headless-main.c`
  (attach a module-less debugger when the env var is set) + rebuild. With the
  env var: `setBreakpoint` returns an id ≥ 1 and fires reliably (170 FlagGet
  hits; 933 FlagSet/FlagClear ops traced through new-game init). Costs nothing
  while no breakpoints are set (debugger loop uses `core->runLoop` until
  `hasBreakpoints`); with breakpoints armed the core single-steps — set the
  env var only for trace runs. Watchpoints (`emu:setWatchpoint`) go through
  the same path and should now work too (not yet exercised).
