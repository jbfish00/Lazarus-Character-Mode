-- Phase 1f nav workhorse: from a savestate, run MOVES, log every coord/map
-- change, screenshot + savestate at end. Edit MOVES/TAG per run.
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"
local TAG = "nx"
local STEP, GAP = 16, 8
local K = H.KEY

-- EDIT PER RUN: from nx_end.ss at (6,14) lab 0.58 — right toward the door
-- mat at bottom-right, then down/out.
local MOVES = {
    { K.RIGHT, STEP }, { K.RIGHT, STEP }, { K.DOWN, STEP }, { K.DOWN, STEP },
    { K.LEFT, STEP }, { K.DOWN, STEP }, { K.RIGHT, STEP }, { K.DOWN, STEP },
}
local ENDF = 1400

local last = nil
H.onFrame(function(f)
    if f == 60 then
        for _, m in ipairs(MOVES) do H.press(m[1], m[2] or STEP, m[3] or GAP) end
    end
    local b = emu:read32(H.gSaveBlock1Ptr)
    if b >= 0x02000000 and b < 0x02040000 then
        local cur = string.format("x=%d y=%d map=%d.%d",
            emu:read16(b), emu:read16(b + 2), emu:read8(b + 4), emu:read8(b + 5))
        if cur ~= last then H.log("f=" .. f .. " " .. cur); last = cur end
    end
    if f == ENDF then
        emu:screenshot(DIR .. TAG .. "_end.png")
        emu:saveStateFile(DIR .. TAG .. "_end.ss")
        H.log("SAVED " .. TAG)
        H.finish()
    end
end)
