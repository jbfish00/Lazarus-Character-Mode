-- Live layer: 100% catch for on-roster species (2026-10-09).
-- From battle_bag.ss (battle bag open on Items, wild Hoppip = species 187):
-- Poke Balls are already in the bag; the RNG is seeded from SEED right before
-- the throw. Breakpoints on both successors of the hooked decision
-- (0x080A7358 fall-through, 0x080A7364 caught) read r6, the capture odds the
-- game decides on, the first time either is reached:
--   EXPECT=sure    -> odds 255, and the party grows (caught on the first throw)
--   EXPECT=vanilla -> odds below 255 (the ball's own maths); outcome not asserted
--   EXPECT=dodged  -> off-roster with CM on: refused before the decision, never caught
--   EXPECT=miss    -> as vanilla, and the throw fails (party unchanged): with
--                     the seed the sure runs catch on, so the guarantee is the hook's
-- Hoppip is on Erika's roster (char 12) and off Red's (char 1). The enemy's
-- battle HP is set to its max first, so "full HP" is a fact, not an assumption.
-- Env: CM_ON 1/0, CM_CHAR, SEED, EXPECT.
local H = dofile("tools/mgba_scripts/harness.lua")
local FLAG_CM, VAR_CM_CHAR = 0x2B0, 0x40E0
local RNG_STATE = 0x0300392C          -- Random32()'s SFC32 state (0x081F59FC)
local GBATTLEMONS = 0x02000360        -- gBattleMons (literal 0x080A75A0, Cmd_handleballthrow's r7), stride 0x60
local CM_ON = os.getenv("CM_ON") == "1"
local EXPECT = os.getenv("EXPECT") or "sure"
local SEED = tonumber(os.getenv("SEED") or "1")
local odds, before = nil, nil

local function grab() if odds == nil then odds = emu:readRegister("r6") end end
H.breakpoint("odds fall-through", 0x080A7358, grab)
H.breakpoint("odds caught", 0x080A7364, grab)

H.onFrame(function(f)
    if f == 10 then
        if CM_ON then
            H.flagSet(FLAG_CM); H.varSet(VAR_CM_CHAR, tonumber(os.getenv("CM_CHAR") or "12"))
        end
        local foe = GBATTLEMONS + 0x60 * 1
        emu:write16(foe + 0x2A, emu:read16(foe + 0x2E))     -- hp = maxHP
        before = emu:read8(H.gPlayerPartyCount)
        H.log(string.format("setup: cm=%s char=%d seed=%d party=%d foe hp %d/%d",
            tostring(CM_ON), H.varGet(VAR_CM_CHAR), SEED, before,
            emu:read16(foe + 0x2A), emu:read16(foe + 0x2E)))
    end
    if f == 60 then H.press(H.KEY.RIGHT, 6, 40) end
    if f == 170 then H.press(H.KEY.A, 6, 40) end
    if f == 305 then
        for i = 0, 3 do emu:write32(RNG_STATE + 4 * i, (SEED * 0x9E3779B9 + i * 0x85EBCA6B) & 0xFFFFFFFF) end
    end
    if f == 310 then H.press(H.KEY.A, 6, 40) end
    if f > 600 and f < 3400 and f % 70 == 0 then H.press(H.KEY.B, 6, 30) end
    if os.getenv("CM_SHOT_PREFIX") and f >= 300 and f <= 1500 and f % 60 == 0 then
        emu:screenshot(os.getenv("CM_SHOT_PREFIX") .. "_" .. f .. ".png")
    end
    if f == 3500 then
        local party = emu:read8(H.gPlayerPartyCount)
        H.log(string.format("odds at the decision=%s party %d -> %d", tostring(odds), before, party))
        if EXPECT == "sure" then
            H.assertEq("odds at the caught/shake decision", odds, 255)
            H.assertEq("caught on the first throw at full HP (party grew)", party, before + 1)
        elseif EXPECT == "dodged" then
            H.assertTrue("the ball never reaches the odds decision (dodged: off-roster is uncatchable)", odds == nil)
            H.assertEq("not caught (party unchanged)", party, before)
        elseif EXPECT == "miss" then
            H.assertTrue("odds are the ball's own (below 255)", odds ~= nil and odds < 255)
            H.assertEq("this seed's vanilla roll breaks out (party unchanged)", party, before)
        else
            H.assertTrue("the throw reached the decision", odds ~= nil)
            H.assertTrue("odds are the ball's own (below 255)", odds ~= nil and odds < 255)
        end
        H.finish()
    end
end)
