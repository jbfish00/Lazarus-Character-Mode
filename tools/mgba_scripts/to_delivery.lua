-- From nx_end.ss (33,10 town 0.57, outside lab): retrace intro path backwards
-- toward spawn area where the "!" NPCs stood.
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"
local K, STEP = H.KEY, 16
local seq = {}
local function add(k, n) for _ = 1, n do seq[#seq+1] = {k, STEP} end end
add(K.RIGHT, 2)
add(K.UP, 3)
H.onFrame(function(f)
    if f == 60 then for _, m in ipairs(seq) do H.press(m[1], m[2], 8) end end
end)
local last = nil
H.onFrame(function(f)
    local b = emu:read32(H.gSaveBlock1Ptr)
    if b >= 0x02000000 and b < 0x02040000 then
        local cur = string.format("x=%d y=%d map=%d.%d", emu:read16(b), emu:read16(b+2), emu:read8(b+4), emu:read8(b+5))
        if cur ~= last then H.log("f="..f.." "..cur); last = cur end
    end
    if f == 2400 then
        emu:screenshot(DIR .. "del_end.png"); emu:saveStateFile(DIR .. "del_end.ss")
        H.log("SAVED del_end.ss"); H.finish()
    end
end)
