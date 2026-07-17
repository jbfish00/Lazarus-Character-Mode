# SELECTION_MECHANISM — riding Lazarus's native cheat-code system

Decision (2026-07-16): character selection reuses Lazarus's own Acrisia
University cheat-code entry, exactly the RR pattern. No repointed BG event
needed — the game already ships a 10-char code-entry naming screen wired to a
string-match special. We replace one specials-table pointer and one script
branch pointer; everything else is additive free-space code/data.

## The native system (all addresses static-XREF-confirmed 2026-07-16)

Player flow: NPC/desk at Acrisia University (starting city per docs + Phase 1e
map notes) → yes/no "enter a code?" → naming screen → match → effect.

| Piece | Address | Detail |
|---|---|---|
| Code string table | `0x087D9294`.. | 40 codes, charmap text, 0xFF-terminated, 4-aligned (NOT fixed stride: MOSEY is 8 bytes) |
| Code ptr literals | pool `0x0813FAE4`–`0x0813FB88` | literal pool of the dispatcher, one word per code + buffer ptr + result ptr |
| Entry-screen special **0x221** | fn `0x0813F848` | `DoNamingScreen(template=5, dest=0x0203CCE0, 0, 0, 0, cb=0x08190B55)`; DoNamingScreen = `0x08186BC8` |
| Code buffer | EWRAM `0x0203CCE0` | 10 chars + 0xFF terminator, written by the naming screen |
| Match special **0x222** | fn `0x0813F86C` | if/else chain: `StringCompare(buffer, code_i)` for i=1..40; writes **1-based match index, 0 if none** to `gSpecialVar_Result` |
| StringCompare | `0x08005D40` | r0/r1 = strings, returns 0 on equal |
| gSpecialVar_Result | EWRAM `0x0200560C` | (independently re-confirmed; matches AddBagItem finding) |
| Specials table | `0x0828CBF4` | base; special ID = (slot − base)/4. Slot for 0x222 = ROM `0x0828D47C` (file `0x28D47C`) |
| Calling script | `special 0x222` at `0x083287CD` | preceded by msgbox yes/no + `special 0x221; waitstate` |
| Script switch | `0x083287D0`–`0x08328993` | `compare VAR_RESULT(0x800D), k; goto_if_eq branch_k` for k=0..0x28, then `end` |
| No-match branch ptr | file **`0x3287D7`** (4 bytes) | `goto_if_eq` target for result==0 → `0x08328994` ("invalid code" msg text `0x0832B667`) |
| Special 0x223 | fn `0x0813FB8D` | post-pool fn (active-code query family; see save-collision note) |

Toggle-code state lives in **SB1+0x1494..0x1499** (u16 bitfield @ +0x1496
with set-bit-count guards, u16 @ +0x1498) — avoid when picking CM save
fields. EWRAM `0x020055FC` also used by the special-flag path.

## Our injection (design, Phase 4)

1. **`characters_codes.bin`** (pipeline addition): 179 entries × 11 bytes
   (10 charmap chars + 0xFF), index-aligned with `characters.bin`. Code =
   character name, spaces/punctuation stripped, truncated to 10 (RR scheme,
   case preserved as typed: `LtSurge`, `CrasherWak`, `LillieAnim`,
   `MallowAnim`). Verified: 179 codes unique, zero clash with the 40 native
   codes.
2. **Dispatcher hook**: overwrite the 4-byte specials-table slot at file
   `0x28D47C` → our C function in free space (`0x015F0EA4` block; it's a
   *data* pointer so BL-reachability doesn't apply — no trampoline).
   Hook logic:
   - call original `0x0813F86D`; if `gSpecialVar_Result != 0` → native code
     matched → return (all 40 native codes keep working unchanged).
   - else scan our code table with `StringCompare`; on match `i`:
     `CM_CHAR var = i+1`, `CM_ON flag` set, give the character's starter
     (signature species if `has_signature`, else first roster entry) at Lv. 5
     via `CreateMon 0x080FC358` + `GiveMonToPlayer 0x081C40BC`, set
     `CM_MSG var = 1` for the script side.
   - debug codes first-class (RR parity): `CMDbgOff`, `CMDbgGive1`,
     `CMDbgGive2`.
3. **Confirmation message**: 4-byte patch at file `0x3287D7` repoints the
   result==0 branch to a small free-space script:
   `compare CM_MSG,1 → goto_if_eq confirm` (msgbox "…Character Mode
   activated!", `setvar CM_MSG 0`, end); else `goto 0x08328994` (original
   invalid-code path preserved).
4. **Flag/var IDs**: pick from ranges with zero hits in a whole-ROM scripted
   bytecode scan (plan step 5) AND clear of SB1+0x1494..0x1499.

Total ROM-side edits to shipped regions: 8 bytes (two 4-byte pointers).
Everything else is new free-space content.

**As implemented (final, 2026-07-17)** — two deltas from the sketch above:
the starter is delivered by the *script* via the retargeted native give
(`callnative CM_GiveMonNativeGated`, species from VAR_CM_STARTER), not by
the C hook calling CreateMon; and the confirm script's activation branch is
ordered: mode msgbox → copy/buffer species → `setvar VAR_CM_STARTER 0` →
callnative give → **`goto` (never `call`)** the ROM's own received-mon tail
at `0x083289DB` — that tail ends every path with `releaseall/end` and
cannot return, so anything placed after a `call` to it is dead code (this
bit us: see CLAUDE.md Status 2026-07-17). The C hook also clears
VAR_CM_STARTER when nothing matches, so a stale marker can never re-trigger
the give on an invalid code.

## Why not the RR repointed-BG-event route

The native system already provides: early availability (starting city),
naming-screen text entry, a script-side switch designed for extension, and
player familiarity (docs advertise the codes). Riding it is a strictly
smaller patch than repointing a bedroom object script.

## Open items (not blockers)

- Live-verify University code-entry NPC reachability from `have_starter.ss`
  (needed anyway for Phase 6 e2e walk).
- Naming-screen template 5 keyboard pages: confirm lowercase available
  (native codes are all-caps; RR-style mixed-case codes need lowercase —
  if template 5 is caps-only, fall back to all-caps codes; uniqueness
  already verified case-insensitively).
- Selection timing vs. Popplio starter: player may activate CM after taking
  the lab starter; RR semantics (enforce at acquisition, existing party
  grandfathered) apply — document in README.
