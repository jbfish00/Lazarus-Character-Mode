-- LIVE layer: QoL C11/C16 starter kit for EVERY new game (2026-11-07; src/character_mode.c CM_NewGameKit, hooked
-- at Lazarus's NewGameInitData last BL 0x08189842). Cold boot with no save, A-mash the real intro (as
-- intro_to_spawn.lua); Character Mode is never turned on. Then:
--   EXPECT=granted (shipped build)          -> Running Shoes 0x8C0, Rydel's 0x5A, Mach Bike 707, Shiny 691, Oval 690
--   EXPECT=none    (CM_NO_STARTKIT=1 build) -> no 0x5A, no 707/691/690 (the discriminating control)
-- Both assert the BL site ran exactly once (breakpoint on it: same address in both builds) and CM stayed off.
--   MGBA_HEADLESS_DEBUGGER=1 CM_EXPECT_CHECKS=7|6 EXPECT=granted|none mgba-headless --script <this> build/lazarus_cm.gba
local H = dofile("tools/mgba_scripts/harness.lua")
local want = os.getenv("EXPECT") or "granted"
local shot = os.getenv("SHOT") or "/tmp/lz_newgame_kit.png"
local END_FRAME = 7400
local ngRan = 0
H.breakpoint("NewGameInitData last call", 0x08189842, function() ngRan = ngRan + 1 end)
H.mash(H.KEY.A, 300, 6800, 60)
local POCKETS = 0x0200B0D8      -- {u32 slots*, u8 capacity} x 8 (docs/ROUTINE_MAP.md "Bag pocket descriptor table")
local function bagHas(item)
    for p = 0, 7 do
        local slots, cap = H.rd32(POCKETS + 8 * p), H.rd8(POCKETS + 8 * p + 4)
        if slots >= 0x02000000 and slots < 0x02040000 then
            for i = 0, cap - 1 do
                if H.rd16(slots + 4 * i) == item then H.log("item " .. item .. " in pocket " .. p); return true end
            end
        end
    end
    return false
end
H.onFrame(function(f)
    if f ~= END_FRAME then return end
    emu:screenshot(shot)
    H.assertEq("NewGameInitData's last call ran once (the intro reached the new game)", ngRan, 1)
    H.assertEq("Character Mode never turned on (flag 0x2B0)", H.flagGet(0x2B0) and 1 or 0, 0)
    if want == "granted" then
        H.assertEq("Running Shoes (FLAG_SYS_B_DASH 0x8C0)", H.flagGet(0x8C0) and 1 or 0, 1)
        H.assertEq("Rydel's FLAG_RECEIVED_BIKE (0x5A)", H.flagGet(0x5A) and 1 or 0, 1)
        H.assertTrue("Mach Bike (707) in the bag", bagHas(707))
        H.assertTrue("Shiny Charm (691) in the bag", bagHas(691))
        H.assertTrue("Oval Charm (690) in the bag", bagHas(690))
    else
        H.assertEq("no kit: Rydel's flag 0x5A stays off", H.flagGet(0x5A) and 1 or 0, 0)
        H.assertTrue("no kit: no Mach Bike", not bagHas(707))
        H.assertTrue("no kit: no Shiny Charm", not bagHas(691))
        H.assertTrue("no kit: no Oval Charm", not bagHas(690))
    end
    H.finish()
end)
