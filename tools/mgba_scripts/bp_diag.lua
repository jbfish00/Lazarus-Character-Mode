-- Diagnostic: does emu:setBreakpoint actually fire on this mgba-headless build?
-- FlagGet (0x081148A0) is checked constantly once scripts/overworld run; if we
-- see zero hits after new-game spawn, breakpoints themselves are broken.
-- Also passively dumps the flag region so we get evidence either way.
local H = dofile("tools/mgba_scripts/harness.lua")

local FLAGGET = 0x081148A0
local hits = 0
local ret = emu:setBreakpoint(function()
    hits = hits + 1
    if hits <= 5 then
        H.log(string.format("FlagGet hit id=0x%03X frame=%d",
            emu:readRegister("r0") % 0x10000, H.frame()))
    end
end, FLAGGET)
H.log("setBreakpoint returned: " .. tostring(ret))

H.mash(H.KEY.A, 300, 6500, 60)

local function nonzero(base, off, len)
    local n = 0
    for i = 0, len - 1 do
        if emu:read8(base + off + i) ~= 0 then n = n + 1 end
    end
    return n
end

local marks = { [600]=true, [2400]=true, [4800]=true, [6900]=true }
H.onFrame(function(f)
    if not marks[f] then return end
    local sb1 = emu:read32(H.gSaveBlock1Ptr)
    H.log(string.format("f=%d hits=%d sb1=0x%08X", f, hits, sb1))
    if sb1 >= 0x02000000 and sb1 < 0x02040000 then
        H.log(string.format("  nonzero bytes: cand0x12E8=%d vanilla0x1270=%d vars0x1414=%d map=%d.%d",
            nonzero(sb1, 0x12E8, 0x12C), nonzero(sb1, 0x1270, 0x78),
            nonzero(sb1, 0x1414, 0x100), emu:read8(sb1+4), emu:read8(sb1+5)))
    end
    if f == 6900 then H.finish() end
end)
