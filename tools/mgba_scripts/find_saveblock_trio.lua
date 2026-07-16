-- Discover the SaveBlock pointer trio on Lazarus (Seaglass's 0x030051B8/BC/C0
-- read zero here). Strategy: mash Start/A to get past the title screen into a
-- new game (which forces SetSaveBlocksPointers), and every 120 frames scan
-- IWRAM for THREE consecutive 32-bit words that each point into EWRAM
-- (0x02000000-0x0203FFFF) -- the gSaveBlock1Ptr/gSaveBlock2Ptr/
-- gPokemonStoragePtr trio signature. For each candidate, dump the first bytes
-- of word[1]'s target so SB1 (s16 x, s16 y, WarpData) is recognizable.
local H = dofile("tools/mgba_scripts/harness.lua")

local IWRAM_LO, IWRAM_SPAN = 0x03000000, 0x7F00
local function isEwram(v) return v >= 0x02000000 and v < 0x02040000 end

-- alternate Start and A presses to clear title/menus
H.mash(H.KEY.START, 200, 2600, 40)
H.mash(H.KEY.A, 220, 2600, 40)

local reported = {}
local done = false
H.onFrame(function(f)
    if done or f < 240 or f % 120 ~= 0 then return end
    local data = emu:readRange(IWRAM_LO, IWRAM_SPAN)
    local found = 0
    for off = 0, IWRAM_SPAN - 12, 4 do
        local function w(o)
            local b1,b2,b3,b4 = string.byte(data, o+1, o+4)
            return b1 + b2*256 + b3*65536 + b4*16777216
        end
        local a, b, c = w(off), w(off+4), w(off+8)
        if isEwram(a) and isEwram(b) and isEwram(c) and a ~= b and b ~= c then
            local ptr = IWRAM_LO + off
            found = found + 1
            local key = string.format("%08X", ptr)
            if not reported[key] then
                reported[key] = true
                local x  = emu:read16(a)
                local y  = emu:read16(a + 2)
                local g  = emu:read8(a + 4)
                local n  = emu:read8(a + 5)
                H.log(string.format(
                    "f=%d trio@0x%08X -> %08X %08X %08X | [1]: x=%d y=%d grp=%d num=%d",
                    f, ptr, a, b, c, x, y, g, n))
            end
        end
    end
    if f >= 2520 then
        H.log(string.format("scan done at f=%d, candidates(total)=%d", f, found))
        done = true
        H.finish()
    end
end)
