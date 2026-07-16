-- Phase 1e step 1: A-mash from boot through title + naming to the new-game
-- overworld spawn (map 0.57 by ~f6900 per bp_diag), then checkpoint:
-- savestate + screenshot + coord log. No breakpoints — run WITHOUT
-- MGBA_HEADLESS_DEBUGGER for full speed.
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"

H.mash(H.KEY.A, 300, 6800, 60)

local last = nil
H.onFrame(function(f)
    local b = emu:read32(H.gSaveBlock1Ptr)
    if b < 0x02000000 or b >= 0x02040000 then return end
    local cur = string.format("x=%d y=%d map=%d.%d",
        emu:read16(b), emu:read16(b + 2), emu:read8(b + 4), emu:read8(b + 5))
    if cur ~= last then H.log("f=" .. f .. " " .. cur); last = cur end
    if f == 7000 then emu:screenshot(DIR .. "spawn_a.png") end
    if f == 7400 then
        emu:screenshot(DIR .. "spawn_b.png")
        emu:saveStateFile(DIR .. "spawn.ss")
        H.log("SAVED " .. DIR .. "spawn.ss")
        H.finish()
    end
end)
