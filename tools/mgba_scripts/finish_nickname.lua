-- From c1_end.ss (Popplio nickname screen, some 'a's typed): press START to
-- jump to OK, A to confirm, then A-mash through remaining dialogue and save
-- have_starter.ss.
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"

H.press(H.KEY.START, 6, 20)
H.press(H.KEY.A, 6, 20)
H.mash(H.KEY.A, 120, 2800, 60)

local last = nil
H.onFrame(function(f)
    local b = emu:read32(H.gSaveBlock1Ptr)
    if b >= 0x02000000 and b < 0x02040000 then
        local cur = string.format("x=%d y=%d map=%d.%d",
            emu:read16(b), emu:read16(b + 2), emu:read8(b + 4), emu:read8(b + 5))
        if cur ~= last then H.log("f=" .. f .. " " .. cur); last = cur end
    end
    if f == 1500 then emu:screenshot(DIR .. "nick_mid.png") end
    if f == 3000 then
        emu:screenshot(DIR .. "have_starter.png")
        emu:saveStateFile(DIR .. "have_starter.ss")
        H.log("SAVED " .. DIR .. "have_starter.ss")
        H.finish()
    end
end)
