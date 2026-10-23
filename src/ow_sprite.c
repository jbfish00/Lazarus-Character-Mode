/*
 * ow_sprite.c — the player's walk/run sprite follows the character
 * (2026-10-21, ../game_plans/overworld_sprites.md; Seaglass's design).
 *
 * Linked on its own at OW_CODE_ADDR (tools/character_mode/lazarus_ow_player.py
 * has the measurements). Entry points:
 *
 *   CM_GetObjectEventGraphicsInfo  GetObjectEventGraphicsInfo (0x081183B8)
 *       jumps here from an 8-byte entry trampoline. For one of the player's
 *       on-foot ids (OW_IDS: every outfit x gender, see the builder) with
 *       Character Mode on and a sprite for the character, it returns that
 *       character's graphics info. Everything else goes to
 *       CM_OrigGetObjectEventGraphicsInfo, which replays the 8 overwritten bytes
 *       and resumes the original at +8. Bike, surf, field move, fishing and
 *       underwater use other ids, so they stay stock.
 *   CM_RefreshPlayerAvatar  ObjectEventSetGraphicsId(player, its current id),
 *       the game's own sprite swap, so the new look shows at once.
 *   CM_SweepThenRefresh  the activation script's callnative: the party sweep it
 *       always ran (CM_SweepPartyToPCNative, SWEEP_PARTY), then the refresh. One
 *       callnative, the same 5 bytes, so the confirm script keeps its length.
 *       The debug off code (CMDBGOFF) doesn't refresh: the stock look returns at
 *       the next map load.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#if !defined(OW_INFO_TABLE) || !defined(NUM_CHARACTERS) || !defined(GET_INFO_RESUME) \
    || !defined(SWEEP_PARTY) || !defined(OW_IDS) || !defined(NUM_OW_IDS)
#error "the injector passes OW_INFO_TABLE, OW_IDS, NUM_OW_IDS, NUM_CHARACTERS, GET_INFO_RESUME and SWEEP_PARTY"
#endif

#define FLAG_CHARACTER_MODE 0x2B0
#define VAR_CM_CHAR         0x40E0

#define FlagGet       ((u8 (*)(u16)) 0x081148A1)
#define GetVarPointer ((u16 *(*)(u16)) 0x08114601)
#define ObjectEventSetGraphicsId ((void (*)(u8 *, u16)) 0x08117C71)
#define OBJECT_EVENTS ((u8 *) 0x0200566C)                           /* gObjectEvents, stride 0x24 */
#define OBJECT_EVENT_SIZE 0x24
#define OBJECT_EVENT_COUNT 16
#define OBJECT_EVENT_GFX_ID 4                                       /* u16 graphicsId */
#define OBJ_ACTIVE    (1u << 0)
#define OBJ_IS_PLAYER (1u << 16)                                    /* in the u32 flags word at +0 */

#define OW_INFOS ((const void *const *) OW_INFO_TABLE)
#define ON_FOOT  ((const u16 *) OW_IDS)

const void *CM_OrigGetObjectEventGraphicsInfo(u16 graphicsId);

static int isOnFoot(u16 graphicsId)
{
    u32 i;

    for (i = 0; i < NUM_OW_IDS; i++)
        if (ON_FOOT[i] == graphicsId)
            return 1;
    return 0;
}

const void *CM_GetObjectEventGraphicsInfo(u16 graphicsId)
{
    if (isOnFoot(graphicsId) && FlagGet(FLAG_CHARACTER_MODE))
    {
        u16 id = *GetVarPointer(VAR_CM_CHAR);
        if (id != 0 && id <= NUM_CHARACTERS && OW_INFOS[id - 1] != 0)
            return OW_INFOS[id - 1];
    }
    return CM_OrigGetObjectEventGraphicsInfo(graphicsId);
}

/* The player's object is found by its isPlayer bit (Lazarus has Pokemon
 * followers too, as Seaglass does). */
void CM_RefreshPlayerAvatar(void)
{
    u32 i;

    for (i = 0; i < OBJECT_EVENT_COUNT; i++)
    {
        u8 *obj = OBJECT_EVENTS + i * OBJECT_EVENT_SIZE;
        u32 flags = *(u32 *) obj;
        if ((flags & (OBJ_ACTIVE | OBJ_IS_PLAYER)) == (OBJ_ACTIVE | OBJ_IS_PLAYER))
        {
            ObjectEventSetGraphicsId(obj, *(u16 *) (obj + OBJECT_EVENT_GFX_ID));
            return;
        }
    }
}

void CM_SweepThenRefresh(void)
{
    ((void (*)(void)) SWEEP_PARTY)();
    CM_RefreshPlayerAvatar();
}

/* The original's first 8 bytes, replayed (r2 = its literal 0xFE1C0000), then a
 * jump to the rest of it. r1 is free there: the original sets it before every
 * read. Its own `pop {r1}; bx r1` returns to our caller. */
#define STR_(x) #x
#define STR(x) STR_(x)
__asm__(
    "    .syntax unified\n"
    "    .text\n"
    "    .align 2\n"
    "    .global CM_OrigGetObjectEventGraphicsInfo\n"
    "    .thumb_func\n"
    "CM_OrigGetObjectEventGraphicsInfo:\n"
    "    ldr r2, 1f\n"
    "    mov ip, r2\n"
    "    lsls r3, r0, #16\n"
    "    lsrs r0, r3, #16\n"
    "    ldr r1, 2f\n"
    "    bx r1\n"
    "    .align 2\n"
    "1:  .word 0xFE1C0000\n"
    "2:  .word " STR(GET_INFO_RESUME) "\n"
    "    .syntax divided\n");
