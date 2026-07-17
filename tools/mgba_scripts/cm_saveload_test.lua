-- Phase 6 e2e: save/load round-trip of the Character Mode state.
-- From cm_red_active.ss (clean overworld at the University desk, CM on as
-- Red, party = 2): in-game save via the START menu (Save = index 3), hard
-- reset, CONTINUE from the title, then assert flag 0x945 / VAR_CM_CHAR /
-- party count all survived the flash round-trip.
--
-- Anti-false-positive: right after the reset (title barely up, save data
-- not yet loaded) the stale EWRAM copies of party count and the CM flag
-- byte are zeroed, so the final asserts can only pass if CONTINUE really
-- restored them from flash.
-- Usage: mgba-headless -t tools/savestates/cm_red_active.ss \
--          --script tools/mgba_scripts/cm_saveload_test.lua build/lazarus_cm.gba
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"
local K = H.KEY

local FLAG_CM, VAR_CHAR = 0x945, 0x40E0
local PARTY_COUNT = 0x0201B95D

local function flagByteAddr()
    local sb1 = emu:read32(H.gSaveBlock1Ptr)
    return sb1 + H.SB1_FLAGS_OFF + (FLAG_CM >> 3)
end

-- 1) open menu, cursor Pokemon->Save (DOWN x3), A, A (yes), A (overwrite
--    existing file: yes), then wait out the "saving..." flash write and
--    dismiss "saved the game"
local plan = {
    { 30, K.START }, { 80, K.DOWN }, { 100, K.DOWN }, { 120, K.DOWN },
    { 150, K.A }, { 220, K.A }, { 300, K.A }, { 1200, K.A },
}
for _, pk in ipairs(plan) do
    H.onFrame(function(f) if f == pk[1] then H.press(pk[2], 6) end end)
end

local RESET_AT = 1500
H.onFrame(function(f)
    if f == RESET_AT - 20 then
        emu:screenshot(DIR .. "saveload_saved.png")
        H.log(string.format("pre-reset: party=%d flag=%s char=%d",
            emu:read8(PARTY_COUNT), tostring(H.flagGet(FLAG_CM)),
            H.varGet(VAR_CHAR)))
    end
    if f == RESET_AT then
        emu:reset()
        H.log("hard reset")
    end
    -- 2) sentinel: zero the stale EWRAM state before the save loads
    if f == RESET_AT + 60 then
        emu:write8(PARTY_COUNT, 0)
        emu:write8(flagByteAddr(), 0)
        H.log("sentinel: stale party count + CM flag byte zeroed")
    end
    -- 4) assert well after CONTINUE finished
    if f == RESET_AT + 4500 then
        emu:screenshot(DIR .. "saveload_loaded.png")
        H.log(string.format("post-load: party=%d flag=%s char=%d",
            emu:read8(PARTY_COUNT), tostring(H.flagGet(FLAG_CM)),
            H.varGet(VAR_CHAR)))
        H.assertEq("party count restored", emu:read8(PARTY_COUNT), 2)
        H.assertTrue("flag 0x945 survived save/load", H.flagGet(FLAG_CM))
        H.assertEq("VAR_CM_CHAR survived save/load", H.varGet(VAR_CHAR), 1)
        H.finish()
    end
end)
-- 3) A-mash from title through CONTINUE (stops long before the assert so a
--    stray A on the desk can't leave a script mid-run)
H.mash(K.A, RESET_AT + 120, RESET_AT + 2500, 40)
