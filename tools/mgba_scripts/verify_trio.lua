-- Verify the Lazarus SaveBlock trio candidate 0x03003664/68/6C by dumping
-- each target's first 32 bytes at several frames (title screen and beyond).
-- Expected shapes: SB1 begins s16 x, s16 y + WarpData; SB2 begins with the
-- 8-byte playerName (0xFF-terminated at new game); Storage begins currentBox
-- byte + box data (zero on empty).
local H = dofile("tools/mgba_scripts/harness.lua")
local TRIO = { 0x03003664, 0x03003668, 0x0300366C }
H.mash(H.KEY.A, 300, 4000, 60)
local function dump(base, len)
    local t = {}
    for i = 0, len - 1 do t[#t+1] = string.format("%02X", emu:read8(base + i)) end
    return table.concat(t, " ")
end
local marks = { [600]=true, [1800]=true, [3600]=true }
local done = false
H.onFrame(function(f)
    if done or not marks[f] then return end
    for i, p in ipairs(TRIO) do
        local v = emu:read32(p)
        H.log(string.format("f=%d [%d] 0x%08X -> 0x%08X", f, i, p, v))
        if v >= 0x02000000 and v < 0x02040000 then
            H.log("    " .. dump(v, 32))
        end
    end
    if f == 3600 then done = true; H.finish() end
end)
