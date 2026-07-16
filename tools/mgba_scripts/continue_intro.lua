-- Phase 1e: continue from a savestate, A-mash through cutscene/dialogue,
-- log coords, screenshot periodically, save an end-state. Edit TAG/END per run.
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"
local TAG = "c1"
local ENDF = 9000

H.mash(H.KEY.A, 60, ENDF - 100, 60)

local last = nil
H.onFrame(function(f)
    local b = emu:read32(H.gSaveBlock1Ptr)
    if b >= 0x02000000 and b < 0x02040000 then
        local cur = string.format("x=%d y=%d map=%d.%d",
            emu:read16(b), emu:read16(b + 2), emu:read8(b + 4), emu:read8(b + 5))
        if cur ~= last then H.log("f=" .. f .. " " .. cur); last = cur end
    end
    if f % 900 == 0 then
        emu:screenshot(string.format("%s%s_%05d.png", DIR, TAG, f))
    end
    if f == ENDF then
        emu:screenshot(DIR .. TAG .. "_end.png")
        emu:saveStateFile(DIR .. TAG .. "_end.ss")
        H.log("SAVED " .. DIR .. TAG .. "_end.ss")
        H.finish()
    end
end)
