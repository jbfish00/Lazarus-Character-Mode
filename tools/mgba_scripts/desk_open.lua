-- Walk from have_starter.ss (map 0.58, x=6 y=12) to the cheat-code desk BG
-- event at (7,8)/(8,8) (kind 1 = face north), press A, and screenshot the
-- result. Saves cheat_ui.ss at the end for the typing test.
-- Usage: mgba-headless -t tools/savestates/have_starter.ss \
--          --script tools/mgba_scripts/desk_open.lua build/lazarus_cm.gba
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"
local K = H.KEY

local function where()
    local b1 = emu:read32(H.gSaveBlock1Ptr)
    return emu:read16(b1), emu:read16(b1 + 2)
end

H.sequence({
    { K.RIGHT, 16, 8 },   -- (6,12) -> (7,12)
    { K.UP, 16, 8 },      -- -> (7,11)
    { K.UP, 16, 8 },      -- -> (7,10)
    { K.UP, 16, 8 },      -- -> (7,9)
    { K.UP, 4, 12 },      -- short tap: face north (blocked by desk = no move)
})

local shot = false
H.onFrame(function(f)
    if f == 200 then
        local x, y = where()
        H.log(string.format("pre-A pos: x=%d y=%d", x, y))
        H.assertEq("standing below desk", string.format("%d,%d", x, y), "7,9")
        emu:screenshot(DIR .. "desk_preA.png")
        H.press(K.A, 4)
    end
    if f == 500 and not shot then
        shot = true
        emu:screenshot(DIR .. "desk_ui.png")
        emu:saveStateFile(DIR .. "cheat_ui.ss")
        H.log("saved cheat_ui.ss + desk_ui.png")
        H.finish()
    end
end)
