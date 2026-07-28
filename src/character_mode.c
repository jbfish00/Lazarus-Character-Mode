/* Character Mode shims for Pokemon Lazarus v2.0.
 *
 * Entry points, all placed in the big free block (ROM 0x095F0EA4+)
 * and reached only through full 32-bit pointers, so no BL-range concerns
 * for the code itself (the BL call-site patches go through 8-byte
 * trampolines instead — see tools/inject_character_mode.py):
 *
 *  1. CM_CheatDispatchHook — replaces the specials-table slot for special
 *     0x222 (the cheat-code matcher). Runs the original matcher first; all
 *     40 native codes keep working. On no native match, compares the entered
 *     code (EWRAM 0x0203CCE0) case-insensitively against the 179 character
 *     codes; on match sets VAR_CM_CHAR/FLAG_CHARACTER_MODE and stashes the
 *     character's starter species in VAR_CM_STARTER for the script side
 *     (which shows the confirmation and delivers the mon). gSpecialVar_Result
 *     stays 0 so the script switch falls into our repointed branch-0.
 *
 *  2. CM_GiveMonToPlayerGated — the acquisition gate (ROWE/RR semantics):
 *     when Character Mode is on, an off-roster non-egg mon goes straight to
 *     the PC instead of the party. BL-retargeted callers: the wild-catch
 *     site 0x080A7BDA and ScriptGiveMon's internal call 0x0820D416. The
 *     daycare caller 0x0819FC8E stays original (eggs exempt; withdrawals
 *     are grandfathered — RR parity).
 *
 *  3. CM_GiveMonNativeGated — Lazarus's script gifts don't use
 *     GiveMonToPlayer; they use a custom callnative give (0x0820DF41,
 *     112 inline script pointers, all retargeted here). The native inserts
 *     into the party itself, so this wrapper post-checks: if the party
 *     grew and the new last slot is an off-roster non-egg, it is copied to
 *     the PC and removed from the party. Soft-lock guard: never removes
 *     the only party mon.
 *
 *  4. CM_TradeCheck — in-game trade gate, see below (unchanged this pass).
 *
 *  5. CM_CreateWildMonGated — wild-encounter roster injection (new,
 *     2026-07-17). Retargets the 9 BL callers of CreateWildMon(species,
 *     level) 0x0824AA54 — the single choke point every random-roll wild
 *     table funnels through after picking its species+level (land/cave,
 *     surf, rock smash, all 3 fishing rod tiers; confirmed by live
 *     breakpoint trace from a fresh encounter, see docs/ROUTINE_MAP.md).
 *     Static/scripted gifts never call this function, so they are
 *     untouched by construction — no exemption logic needed, unlike the
 *     GiveMonToPlayer daycare case. When Character Mode is on, 1-in-10
 *     calls (Random32()%10==0) get their species+level replaced with a
 *     random non-legendary roster member's evolution stage that best fits
 *     the originally-rolled level (nearest-stage fallback otherwise), then
 *     falls through to the untouched original CreateWildMon so
 *     personality/gender/nature/IVs/moveset generation is unaffected.
 *
 * Every fixed address below is CONFIRMED for this exact ROM (rom.sha1);
 * provenance in docs/ROUTINE_MAP.md + docs/SELECTION_MECHANISM.md.
 * MON_DATA_SPECIES=18 verified against GiveMonToPlayer's own slot probe;
 * MON_DATA_IS_EGG=52 ROM-confirmed from ScriptGiveMon's give-EGG SetMonData
 * (movs r1,#52 @ 0x0820D408 — the donor's 54 does NOT hold here; shipping 54
 * was caught by tools/tests/shim_unit_test.py's egg case).
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

/* 0 script refs (audited: no setflag/clearflag/checkflag operand anywhere in
   the ROM) AND outside every engine sweep range. The original pick, 0x945, was
   inside DAILY_FLAGS (0x920-0x95F), which ClearDailyFlags() (here at
   0x081143C2, memsetting SB1+0x140C for 8 bytes) wipes on every RTC day
   rollover -- Character Mode silently switched itself off at midnight while
   VAR_CM_CHAR stayed set. Any replacement must stay clear of the temp block
   (0x000-0x01F, ClearTempFieldEventData) and the daily block. Seaglass had the
   identical bug and took the identical fix. */
#define FLAG_CHARACTER_MODE 0x2B0
#define VAR_CM_CHAR         0x40E0
#define VAR_CM_STARTER      0x40E4
#define CM_STARTER_OFF_MARKER 0xFFFF

/* NUM_CHARACTERS comes from the injector, which derives it from
   characters_manifest.json. It used to be a literal here, and a stale literal
   is the single most repeated bug in this workspace -- it never presents as a
   count error. Too LOW and the tail of the table becomes unselectable and
   unenforced; too HIGH and gateActive() trusts an out-of-range index and
   onRoster() reads a bitmap past the end of the blob. */
#ifndef NUM_CHARACTERS
#error "compile with -DNUM_CHARACTERS= (derived from characters_manifest.json)"
#endif
#define TOBIAS_CHAR_ID 0     /* Tobias TRIMMED from Lazarus (Darkrai/Latios not in this ROM's dex) — id 0 never matches; branch kept for parity with RR/Seaglass */
#define NUM_SPECIES    1561
#define BITMAP_STRIDE  196
#define CODE_LEN       11
#define PARTY_SIZE     6
#define MON_SIZE       100

#define MON_DATA_SPECIES 18
#define MON_DATA_IS_EGG  52

/* Confirmed functions (Thumb: +1). */
#define FlagSet         ((u8   (*)(u16))              0x0811478D)
#define FlagClear       ((u8   (*)(u16))              0x08114845)
#define FlagGet         ((u8   (*)(u16))              0x081148A1)
#define GetVarPointer   ((u16 *(*)(u16))              0x08114601)
#define GetMonData      ((u32  (*)(void *, int, void *)) 0x081C2FB9)
#define GiveMonToPlayer ((u8   (*)(void *))           0x081C40BD)
#define CopyMonToPC     ((u8   (*)(void *))           0x081C4131)
#define OrigCheatDispatch ((void (*)(void))           0x0813F86D)
#define OrigGiveMonNative ((void (*)(void *))         0x0820DF41)
/* CreateWildMon(species, level) — live breakpoint-trace-confirmed 2026-07-17
 * (docs/ROUTINE_MAP.md): pushes {r4-r7,lr}; r0=species truncated to u16 via
 * lsl16/lsr16, r1=level truncated to u8 via lsl24/lsr24, exactly matching the
 * donor prototype CreateWildMon(enum Species species, u8 level). */
#define OrigCreateWildMon ((void (*)(u16, u8))        0x0824AA55)
/* Random32 — the JKISS-shaped low-level RNG primitive (state update matches
 * modern pokeemerald-expansion's Random()/Random32 shape exactly: x+=const;
 * y^=y<<5/y>>9/... ; z,w,c rotate), called pervasively by personality/nature
 * generation. No args, returns a fresh u32 in r0 each call. */
#define Random32        ((u32  (*)(void))             0x081F59FD)

#define gSpecialVar_Result (*(volatile u16 *) 0x0200560C)
#define gPlayerPartyCount  (*(volatile u8 *)  0x0201B95D)
#define gPlayerParty       ((u8 *)            0x0201B960)
#define sCodeBuffer        ((const u8 *)      0x0203CCE0)

/* Injection-time data placement. */
#ifndef CODES_ADDR
#error "compile with -DCODES_ADDR= -DSTARTERS_ADDR= -DBITMAPS_ADDR= -DHIDDEN_ADDR= -DDBG_GIVE2_SPECIES= -DWILDMONS_ADDR= -DWILDMON_STRIDE="
#endif
#define sCodes    ((const u8 *)  CODES_ADDR)    /* N x 11, charmap, 0xFF pad  */
#define sStarters ((const u16 *) STARTERS_ADDR) /* N x u16 ROM species id     */
#define sBitmaps  ((const u8 *)  BITMAPS_ADDR)  /* N x 196 allowed-species    */
/* One bit per character, LSB-first: set = under the six-fully-evolved
 * playability threshold in this game's curated dex. Its code is refused at the
 * naming screen, but the record keeps its index and gateActive() ignores this
 * bit entirely, so a save already on such a character still loads and is still
 * enforced. tools/character_mode/hidden.bin, from character_drops.json. */
#define sHidden   ((const u8 *)  HIDDEN_ADDR)
/* 179 x WILDMON_STRIDE bytes; each character's region is a sequence of
 * 4-byte {u16 species (bit15 = family-start marker), u8 minLevel, u8
 * maxLevel} entries grouped by roster family, 0-terminated. See
 * tools/character_mode/emit_wildmons.py. */
#define sWildmons ((const u8 *)  WILDMONS_ADDR)
#define WILDMON_FAMILY_START 0x8000

/* The 1% legendary wild-encounter pool. Same 4-byte entry format and same
 * family grouping as sWildmons, but built from the LEGENDARY tail of each
 * roster (roster_species_ids[starter_count:]) instead of the non-legendary
 * head. tools/character_mode/emit_legendaries.py.
 * Spec: ../game_plans/legendary_encounters.md. */
#define sLegendaries ((const u8 *) LEGENDARY_ADDR)

/* Pokedex caught bitmap, for spec §1.2/§1.3 "offered until caught" -- which is
 * what makes this cost ZERO new save state.
 * docs/ROUTINE_MAP.md "Pokedex bitmaps": dexCaught at SaveBlock1 +0x3329, 129
 * bytes, bit index natdex-1. Species id == natdex across 25..384, established
 * live (tools/mgba_scripts/dex_natdex_probe.lua), and every legendary in this
 * game's rosters is 243..384 -- so the species id is used directly and no
 * conversion table is needed. Anything above 384 must be re-checked first. */
#define gSaveBlock1Ptr     (*(u8 * const *) 0x03003664)
#define DEX_CAUGHT_OFF     0x3329
#define DEX_FLAG_BYTES     129

static u8 dexCaught(u16 natdex)
{
    u32 idx;

    /* Out of range reads as "already caught" so it can never be offered --
     * failing closed, because the alternative is reading past the bitmap. */
    if (natdex == 0)
        return 1;
    idx = (u32) natdex - 1;
    if (idx >= DEX_FLAG_BYTES * 8)
        return 1;
    return (u8) ((gSaveBlock1Ptr[DEX_CAUGHT_OFF + (idx >> 3)] >> (idx & 7)) & 1);
}

/* Charmap case fold: A-Z = 0xBB-0xD4, a-z = 0xD5-0xEE. */
static u8 fold(u8 c)
{
    if (c >= 0xD5 && c <= 0xEE)
        return c - 0x1A;
    return c;
}

static int codeEq(const u8 *entered, const u8 *code)
{
    int j;
    for (j = 0; j < CODE_LEN; j++) {
        u8 a = fold(entered[j]);
        u8 b = fold(code[j]);
        if (a != b)
            return 0;
        if (a == 0xFF)
            return 1;
    }
    return 1;
}

/* index is 0-based here (charId - 1). */
static int isHidden(u16 index)
{
    return (sHidden[index >> 3] >> (index & 7)) & 1;
}

static int onRoster(u16 charId, u32 species)
{
    const u8 *bm = sBitmaps + (charId - 1) * BITMAP_STRIDE;
    if (species == 0 || species >= NUM_SPECIES)
        return 1; /* out-of-model species: never block */
    return (bm[species >> 3] >> (species & 7)) & 1;
}

/* Debug codes, charmap-encoded ("CMDBGOFF", "CMDBGGIVE1", "CMDBGGIVE2");
 * matching is case-folded so CMDbgOff etc. work too. */
static const u8 sDbgOff[CODE_LEN]   = {0xBD,0xC7,0xBE,0xBC,0xC1,0xC9,0xC0,0xC0,0xFF,0xFF,0xFF};
static const u8 sDbgGive1[CODE_LEN] = {0xBD,0xC7,0xBE,0xBC,0xC1,0xC1,0xC3,0xD0,0xBF,0xA2,0xFF};
static const u8 sDbgGive2[CODE_LEN] = {0xBD,0xC7,0xBE,0xBC,0xC1,0xC1,0xC3,0xD0,0xBF,0xA3,0xFF};

void CM_CheatDispatchHook(void)
{
    u16 i;

    OrigCheatDispatch();
    if (gSpecialVar_Result != 0)
        return; /* a native Lazarus code matched */

    if (codeEq(sCodeBuffer, sDbgOff)) {
        FlagClear(FLAG_CHARACTER_MODE);
        *GetVarPointer(VAR_CM_CHAR) = 0;
        *GetVarPointer(VAR_CM_STARTER) = CM_STARTER_OFF_MARKER;
        return;
    }
    if (codeEq(sCodeBuffer, sDbgGive1)) {
        u16 id = *GetVarPointer(VAR_CM_CHAR);
        /* on-roster test give: the current character's own starter
         * (falls back to character 1's starter when mode is off) */
        *GetVarPointer(VAR_CM_STARTER) =
            sStarters[(id >= 1 && id <= NUM_CHARACTERS) ? id - 1 : 0];
        return;
    }
    if (codeEq(sCodeBuffer, sDbgGive2)) {
        /* off-roster test give (species picked at injection time) */
        *GetVarPointer(VAR_CM_STARTER) = DBG_GIVE2_SPECIES;
        return;
    }

    for (i = 0; i < NUM_CHARACTERS; i++) {
        if (codeEq(sCodeBuffer, sCodes + i * CODE_LEN)) {
            /* Under the playability threshold: fall through to the same
             * refusal an unknown code gets, rather than inventing a second
             * failure message. Deliberately NOT a check inside gateActive():
             * a save already on this character must keep working. */
            if (isHidden(i))
                break;
            *GetVarPointer(VAR_CM_CHAR) = i + 1;
            FlagSet(FLAG_CHARACTER_MODE);
            *GetVarPointer(VAR_CM_STARTER) = sStarters[i];
            return;
        }
    }
    /* Nothing matched: clear the marker, else the confirm script's branch-0
     * (compare VAR_CM_STARTER, 0) would treat a stale species from an earlier
     * activation as a fresh give on any invalid code. */
    *GetVarPointer(VAR_CM_STARTER) = 0;
}

static int gateActive(void)
{
    u16 id;
    if (!FlagGet(FLAG_CHARACTER_MODE))
        return 0;
    id = *GetVarPointer(VAR_CM_CHAR);
    return id >= 1 && id <= NUM_CHARACTERS;
}

u8 CM_GiveMonToPlayerGated(void *mon)
{
    if (gateActive() && gPlayerPartyCount != 0
     && !GetMonData(mon, MON_DATA_IS_EGG, 0)) {
        u32 species = GetMonData(mon, MON_DATA_SPECIES, 0);
        if (!onRoster(*GetVarPointer(VAR_CM_CHAR), species))
            return CopyMonToPC(mon);
    }
    return GiveMonToPlayer(mon);
}

/* In-game trade gate. Called via `callnative` from the 4 patched trade
 * scripts right after the trade index is copied into VAR_0x8004 (special
 * vars resolve through the 0x0828CB9C pointer table inside GetVarPointer).
 * Writes 1 (allowed) / 0 (refuse) to gSpecialVar_Result; the wrapper script
 * shows the polite refusal and ends on 0. sIngameTrades = 0x08E4D578,
 * stride 60, received species at +14 (docs/ROUTINE_MAP.md). */
#define VAR_0x8004 0x8004
#define TRADE_TABLE ((const u8 *) 0x08E4D578)
#define TRADE_COUNT 4

void CM_TradeCheck(void *ctx)
{
    u16 allowed = 1;
    (void) ctx;
    if (gateActive()) {
        u16 idx = *GetVarPointer(VAR_0x8004);
        if (idx < TRADE_COUNT) {
            const u8 *e = TRADE_TABLE + idx * 60;
            u16 species = (u16) (e[14] | (e[15] << 8));
            allowed = onRoster(*GetVarPointer(VAR_CM_CHAR), species) ? 1 : 0;
        }
    }
    gSpecialVar_Result = allowed;
}

void CM_GiveMonNativeGated(void *ctx)
{
    u8 before = gPlayerPartyCount;
    u8 after;

    OrigGiveMonNative(ctx);

    if (!gateActive())
        return;
    after = gPlayerPartyCount;
    if (after > before && after >= 2) {
        u8 *mon = gPlayerParty + (after - 1) * MON_SIZE;
        if (!GetMonData(mon, MON_DATA_IS_EGG, 0)) {
            u32 species = GetMonData(mon, MON_DATA_SPECIES, 0);
            if (!onRoster(*GetVarPointer(VAR_CM_CHAR), species)
             && CopyMonToPC(mon) == 1) { /* MON_GIVEN_TO_PC; boxes full -> stays in party */
                int j;
                for (j = 0; j < MON_SIZE; j++)
                    mon[j] = 0;
                gPlayerPartyCount = after - 1;
                /* The give tails branch on this: 1 = "transferred to the PC"
                 * (and skips the party-mon nickname flow, which would now
                 * target a phantom slot). */
                gSpecialVar_Result = 1;
            }
        }
    }
}

/* Wild-encounter roster override (new, 2026-07-17). Picks a RANDOM roster
 * family (base + evolution chain), then within that family the stage whose
 * [minLevel,maxLevel] window contains the rolled level; if none contains it
 * (shouldn't happen — each family's windows partition 1..100 — but handled
 * defensively per spec), picks the nearest stage by level distance. Returns
 * SPECIES_NONE (0) if the character has no eligible entries at all (e.g. an
 * unresolved/all-legendary roster), in which case the caller must not
 * override. Never touches legendaries: the table is built exclusively from
 * roster_species_ids[0:starter_count], the non-legendary slice — see
 * tools/character_mode/emit_wildmons.py. */
/* Best-fitting stage within ONE family of a wildmons-format table, starting at
 * entry index `start`. Same rule pickRosterWildSpecies uses: the stage whose
 * [minLevel,maxLevel] window contains the rolled level, else the nearest by
 * level distance. Returns 0 if the family is empty.
 *
 * Factored out because the legendary roll has to evaluate every family TWICE --
 * once to count how many are still uncaught, once to pick the chosen one -- and
 * the two passes must agree exactly or the count and the pick disagree. */
static u16 bestStageInFamily(const u8 *tbl, u16 stride, int start, u8 level,
                             u8 *outLevel)
{
    u16 bestSpecies = 0;
    u8 bestLevel = level;
    int bestDist = 0x7FFFFFFF;
    int i;

    for (i = start; i + 4 <= (int) stride; i += 4) {
        u16 raw = (u16) (tbl[i] | (tbl[i + 1] << 8));
        u8 lo, hi;
        u16 sp;
        int dist;

        if (raw == 0)
            break;
        if ((raw & WILDMON_FAMILY_START) && i != start)
            break;
        lo = tbl[i + 2];
        hi = tbl[i + 3];
        sp = (u16) (raw & (WILDMON_FAMILY_START - 1));
        if (level >= lo && level <= hi) {
            *outLevel = level;
            return sp;
        }
        dist = (level < lo) ? (lo - level) : (level - hi);
        if (dist < bestDist) {
            bestDist = dist;
            bestSpecies = sp;
            bestLevel = (u8) ((level < lo) ? lo : hi);
        }
    }
    *outLevel = bestLevel;
    return bestSpecies;
}

/* The 1% legendary pool. Returns SPECIES_NONE (0) when this character has no
 * legendary, or when every legendary it has is already caught.
 *
 * "Offered until caught" is filtered on the stage that would ACTUALLY be
 * offered, not on the family's base species. Today every legendary in this
 * game's rosters is single-stage so the two coincide, but filtering on the base
 * would silently keep offering an evolved legendary forever the moment a
 * multi-stage line (a Cosmog/Kubfu shape) is added.
 *
 * Consumes NO RNG -- see the note at the call site. */
static u16 pickLegendaryWildSpecies(u16 charId, u8 level, u8 *outLevel,
                                    int *outEligible, int pick)
{
    const u8 *tbl = sLegendaries + (charId - 1) * LEGENDARY_STRIDE;
    int i, eligible = 0;

    for (i = 0; i + 4 <= LEGENDARY_STRIDE; i += 4) {
        u16 raw = (u16) (tbl[i] | (tbl[i + 1] << 8));
        u16 sp;
        u8 lvl;

        if (raw == 0)
            break;
        if (!(raw & WILDMON_FAMILY_START))
            continue;                    /* only family heads start a family */
        sp = bestStageInFamily(tbl, LEGENDARY_STRIDE, i, level, &lvl);
        if (sp == 0 || dexCaught(sp))
            continue;
        if (pick == eligible) {
            *outLevel = lvl;
            if (outEligible)
                *outEligible = eligible + 1;
            return sp;
        }
        eligible++;
    }
    if (outEligible)
        *outEligible = eligible;
    return 0;
}

static u16 pickRosterWildSpecies(u16 charId, u8 level, u8 *outLevel)
{
    const u8 *tbl = sWildmons + (charId - 1) * WILDMON_STRIDE;
    int i, familyCount, target, cur, start;

    familyCount = 0;
    for (i = 0; i + 4 <= WILDMON_STRIDE; i += 4) {
        u16 raw = (u16) (tbl[i] | (tbl[i + 1] << 8));
        if (raw == 0)
            break;
        if (raw & WILDMON_FAMILY_START)
            familyCount++;
    }
    if (familyCount == 0)
        return 0;

    target = (int) (Random32() % (u32) familyCount);

    start = -1;
    cur = -1;
    for (i = 0; i + 4 <= WILDMON_STRIDE; i += 4) {
        u16 raw = (u16) (tbl[i] | (tbl[i + 1] << 8));
        if (raw == 0)
            break;
        if (raw & WILDMON_FAMILY_START) {
            cur++;
            if (cur == target) {
                start = i;
                break;
            }
        }
    }
    if (start < 0)
        return 0;

    /* Shared with the legendary pool: ONE implementation of the stage rule, so
       the two tables cannot disagree about which stage a level maps to. */
    return bestStageInFamily(tbl, WILDMON_STRIDE, start, level, outLevel);
}

void CM_CreateWildMonGated(u16 species, u8 level)
{
    if (gateActive()) {
        u16 id = *GetVarPointer(VAR_CM_CHAR);
        u32 hit;
        int eligible = 0;
        u8 scratchLevel = level;

        /* --- the 1% legendary roll (spec §1.1), BEFORE the 10% one ----------
         *
         * THE DATA CHECK MUST PRECEDE THE RNG CALL. Counting eligible
         * legendaries consumes no randomness, so a character with none -- 214
         * of the 238 here -- takes exactly the same number of Random32() draws
         * per encounter as it did before this feature existed. Roll first and
         * every one of them gets a shifted encounter stream for nothing, which
         * is invisible in testing and breaks the spec's promise that they are
         * completely unaffected. Unbound hit this; ROWE shipped it wrong and
         * had to fix it in a5befab7.
         *
         * The two rolls are independent, legendary first, so the rates compose
         * to ~1% legendary / ~9.9% roster / ~89% the game's own table. */
        pickLegendaryWildSpecies(id, level, &scratchLevel, &eligible, -1);
        if (eligible > 0 && (Random32() % 100) == 0) {
            u8 newLevel = level;
            u16 newSpecies = pickLegendaryWildSpecies(
                id, level, &newLevel, (int *) 0,
                (int) (Random32() % (u32) eligible));
            if (newSpecies != 0) {
                species = newSpecies;
                level = newLevel;
                OrigCreateWildMon(species, level);
                return;
            }
        }

        /* Tobias (user spec 2026-07-23): 1% per roll, and his table is
         * legendary-INCLUSIVE (Darkrai/Latios -- see emit_wildmons.py's
         * special case). Everyone else keeps the standard 10%.
         * DEAD BRANCH HERE: Tobias is trimmed from Lazarus and TOBIAS_CHAR_ID
         * is 0, which never matches a 1-based id. Kept for cross-repo parity;
         * the general rule above subsumes it. */
        hit = (id == TOBIAS_CHAR_ID) ? ((Random32() % 100) == 0)
                                     : ((Random32() % 10) == 0);
        if (hit) {
            u8 newLevel = level;
            u16 newSpecies = pickRosterWildSpecies(id, level, &newLevel);
            if (newSpecies != 0) {
                species = newSpecies;
                level = newLevel;
            }
        }
    }
    OrigCreateWildMon(species, level);
}
