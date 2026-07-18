# TESTING — Lazarus Character Mode

Four automated layers, mirroring (and exceeding) the Radical Red suite.
Everything runs headless; no GUI or human input needed.

## Layer 1 — Shim unit tests (GDB, real code in the real emulator)

```
python3 tools/tests/shim_unit_test.py        # 20/20 expected (was 16/16 before the wild-encounter cases)
```

Boots `build/lazarus_cm.gba` under `mgba-qt -g` (xvfb if headless) +
`gdb-multiarch`, builds a **fake zeroed SaveBlock1** in scratch EWRAM and
repoints `gSaveBlock1Ptr` at it, then drives the real shim entries with
synthetic state:

- **Acquisition gate (10 cases)** — enters `CM_GiveMonToPlayerGated` (decoded
  from the shipped trampoline literal, not hardcoded) with a synthetic mon;
  the branch taken is observed by breakpoints on the real `GiveMonToPlayer`
  (pass) / `CopyMonToPC` (enforce) entries. Covers: flag off, empty party
  (soft-lock guard), on-roster, off-roster, char 0, egg exemption, char out
  of range, per-character bitmap differences, out-of-model species,
  max in-model species.
- **Trade gate (6 cases)** — calls `CM_TradeCheck` (decoded from the trade
  wrapper's callnative pointer) with `VAR_0x8004` (storage resolved from the
  ROM's own special-vars pointer table) set to each trade index; verdict read
  back from `gSpecialVar_Result`. Covers CM off, all 4 trades as Red
  (all refuse), and out-of-range index (allow).

Gotchas encoded in the test (see the mGBA GDB memory note): the stub ignores
CPSR T-bit writes, so the first entry goes through an ARM→Thumb `bx`
trampoline in scratch EWRAM; later entries set `$pc` directly from Thumb
context.

**Wild-encounter override trials (new, 2026-07-17, 4 more cases: 20/20).**
Same GDB session, same Thumb-context reuse. Observation point is
`CreateWildMon`'s own real entry `0x0824AA54` — the gate always tail-calls
it whether or not it overrode, so whatever `(r0=species, r1=level)` it's
entered with IS the gate's decision:
- **CM off, 20 trials, fixed input** → every trial must reproduce the input
  species+level unchanged (proves the override path costs nothing and can't
  fire when Character Mode is off — `Random32()` is never even called since
  `gateActive()` short-circuits first).
- **CM on (Red), 200 trials, fixed off-roster input** → count how many
  trials return something other than the input; asserts the rate lands in
  [4%, 20%] (loose band around the 10% target, sized for ~200 Bernoulli
  trials without flaking).
- **Exclusion** → every overridden species must be a member of Red's own
  `wildmons.bin` row (independently re-derived from the shipped artifact,
  not re-trusting the pipeline) — since that table is built exclusively
  from `roster_species_ids[0:starter_count]` (the non-legendary slice), this
  also proves legendary/mythical exclusion without duplicating
  `LEGENDARY_BASES` logic in the test.
- **Level sanity** → every overridden level stays in [1,100].

This test caught a real bug on the first pass: `pickRosterWildSpecies`'s
stage-picker loop declared its species-extraction local as `u8 sp` instead
of `u16 sp`, silently truncating any roster species id ≥256 to its low byte
(Kleavor 900→132, Wailmer 320→64 — both observed as real failures before the
fix). Fixed in `src/character_mode.c`; rebuilt, re-tested, 0 bad after.

## Layer 2 — Boot smoke

```
sh tools/tests/run_boot_smoke.sh             # original + patched ROM
```

Cold boot → A-mash → asserts the SaveBlock trio goes live in EWRAM and the
overworld spawn map (0.57) is reached. Also first item of the live suite.

## Layer 3 — Static artifact verification

```
python3 tools/tests/verify_artifacts.py      # ALL PASS expected (grew past the original 56 with the wild-encounter section)
```

Re-derives everything from the finished artifacts (never trusts the
injector's bookkeeping): SHA1 pin, BPS round-trip byte-identity, whole-ROM
diff confined to intended regions, independent BL decode of both patch
sites + trampoline, bitmaps byte-equal to the pipeline output + roster bits
set + non-degenerate, codes decode/unique/no native clash, starters
on-bitmap, specials-slot hook, all 112 callnative give sites retargeted
with none left over, full opcode walk of the confirm script and all 4 trade
wrappers, refusal text, **and the exhaustive `GiveMonToPlayer` BL scan**:

> The whole 32 MiB ROM contains exactly 3 BL callers of GiveMonToPlayer
> (battle/catch `0x0A7BDA`, daycare `0x19FC8E`, script gift `0x20D416`).
> In the patched ROM only the deliberately exempt daycare caller remains —
> so **every** in-battle acquisition path, DexNav included, funnels through
> the gate. DexNav needs no separate live test: there is no fourth path.

**New (2026-07-17): the same exhaustion argument for the wild-encounter
override.** The whole ROM contains exactly 9 BL callers of `CreateWildMon`
(land/cave, surf, rock smash, all fishing rods, plus 2 Battle
Frontier/Safari-style contexts); the patched ROM has 0 left un-retargeted.
Static/scripted gifts never call `CreateWildMon` at all, so they are
excluded by construction — no exemption list needed, unlike the daycare
case above. Also checks: `wildmons.bin` in ROM byte-matches the pipeline
output; no legendary/mythical species anywhere in any character's table
(cross-checked against `emit_characters.LEGENDARY_BASES` directly); every
family's per-stage level windows are gapless, monotonic, and confined to
[1,100].

**Wild-encounter override note**: no dedicated Layer 4 live e2e was added for
it — triggering real wild encounters with a controlled rate/species read-out
in the overworld is much slower and less deterministic than driving the
exact shipped entry point (the wild trampoline literal decoded straight from
the ROM, exactly as GIVEMON's entry already is) via GDB, and the Layer 1
wild trials already exercise the real compiled code through the real
9-BL-site hook, not a mock. Layer 3's exhaustive BL scan independently
proves those 9 real call sites reach it. Considered sufficient; a human
playthrough will still see it happen organically (10% of any wild
encounter while Character Mode is on).

## Layer 4 — Live end-to-end (headless mGBA + savestates)

```
sh tools/tests/run_live_suite.sh             # everything below, ~2 min
```

| test | savestate | proves |
|---|---|---|
| `boot_smoke` | (cold boot) | patched ROM boots to overworld |
| `catch_gate_on` | `battle_bag.ss` | wild Hoppip (off-roster) → PC, party unchanged |
| `catch_gate_off` | `battle_bag.ss` | control: stock catch, party grows |
| `starter_on` | `spawn.ss` | Popplio delivered despite CM-Red (empty-party guard), nothing boxed |
| `starter_off` | `spawn.ss` | control: stock starter flow |
| `ui_activate_red` | `naming.ss` | real desk UI: type `red` → flag 0x945 + VAR_CM_CHAR=1 set, Pikachu starter delivered via retargeted native give, marker var reset; saves `cm_red_active.ss` |
| `ui_give2_boxing` | `cm_red_active.ss` | real desk UI: type `cmdbggive2` (digit via others page) → native-give wrapper boxes the off-roster Ekans, party unchanged |
| `save_load` | `cm_red_active.ss` | in-game save → hard reset → continue; flag/var/party survive (stale RAM sentinel-zeroed post-reset so the pass can't be fake) |
| `trade e2e ×2` | `cm_red_active.ss` | real trade script → junction → `CM_TradeCheck`: CM-on shows "Character Mode: this trade is not in your roster." and keeps the party; CM-off control completes the trade (SEASOR the Horsea arrives) |

The trade e2e runs on a **test-only ROM variant** (built on the fly by
`run_trade_e2e.sh`, never shipped): the University desk's second BG event
(8,8) is repointed to the in-game-trade script `0x082B6182` so the full
native trade flow is reachable without story progression. The junction and
wrapper bytes exercised are the identical shared bytes every real trade NPC
runs. That script is `sIngameTrades` **index 2** (scripts hardcode their
index via `setvar 0x8008`; junction order is 2,0,1,3 vs table order): the
NPC gives Horsea 116 and wants Bagon 371 — the test injects a synthetic
valid Bagon into party slot 3 (personality/otId 0 → xor key 0).

## Hard-won harness facts (do not relearn)

- `H.finish()` now `os.exit`s the emulator (added 2026-07-17; mGBA used to
  idle forever afterwards) — still bound every run with `timeout` as a
  belt-and-braces in case a build sandboxes `os.exit` away.
- The naming screen keeps an internal buffer and **flushes it over
  `0x0203CCE0` at commit** — poking the code buffer does not work; type for
  real. Digits live on the "others" page (SELECT, ~60 frames of settle
  before cursor moves register; digits 0-9 on row 0; cursor carries over).
- Use **B-mash, not A-mash**, to drain trailing msgboxes near the desk —
  A re-triggers the BG event and leaves the UI open in your savestate.
- `SaveBlock1` head is vanilla-layout: pos @0, location @+4,
  continueGameWarp @+0xC (normally zeros), lastHealLocation @+0x1C.
  **Writing a nonzero continueGameWarp bricks the boot** (black screen,
  crash at title) — warp by editing `location` only. Even then the
  continue-load comes up with a black screen and locked input; warping
  around the world this way is NOT currently usable (the trade e2e avoids
  it via the desk repoint instead).
- In-game save from a fresh file needs THREE confirms (save? → yes,
  overwrite? → yes, done msg) and ~900 frames for the flash write.
- The party menu is a 2-column grid: slot 3 is one DOWN from slot 1.
- True `gMapGroups` = file `0xFAF098` (34 groups; group 0 base `0xFAE5F0`).
  A decoy 88-entry pointer run sits just before it at `0xFAEFC0`.
- Trade NPC home maps (via event→header→group chain): SEASOR 7.4 (door on
  town 0.15 at (12,24)), DOTS 11.10, PLUSES 11.15, MEOWOW 26.48.
