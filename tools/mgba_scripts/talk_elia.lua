local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"
H.press(H.KEY.UP, 6, 30)      -- face Elia
H.mash(H.KEY.A, 60, 2400, 50) -- talk + mash through
local last=nil
H.onFrame(function(f)
    local b = emu:read32(H.gSaveBlock1Ptr)
    if b >= 0x02000000 and b < 0x02040000 then
        local cur = string.format("x=%d y=%d map=%d.%d", emu:read16(b), emu:read16(b+2), emu:read8(b+4), emu:read8(b+5))
        if cur ~= last then H.log("f="..f.." "..cur); last = cur end
    end
    if f == 800 then emu:screenshot(DIR.."elia1.png") end
    if f == 1600 then emu:screenshot(DIR.."elia2.png") end
    if f == 2500 then
        emu:screenshot(DIR.."elia3.png")
        emu:saveStateFile(DIR.."after_elia.ss")
        H.log("SAVED after_elia.ss")
        H.finish()
    end
end)
