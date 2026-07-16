-- Identify our just-nicknamed starter in EWRAM: struct Pokemon keeps the
-- nickname in PLAINTEXT at +0x08 (10 bytes). We typed "Aaaaaaa..." on the
-- nickname screen (Gen3 charmap: 'A'=0xBB, 'a'=0xD5), so scan EWRAM for
-- 0xBB 0xD5 0xD5 0xD5 and print every hit - 8 = struct base. Also dump the
-- known candidate 0x02005674's fields for comparison.
local EWRAM_START, EWRAM_END = 0x02000000, 0x02040000

local frame, done = 0, false
callbacks:add("frame", function()
    frame = frame + 1
    if done or frame < 120 then return end
    done = true
    local m = emu:readRange(EWRAM_START, EWRAM_END - EWRAM_START)
    console:log("PROBE scanning for nickname pattern...")
    local pat = string.char(0xBB, 0xD5, 0xD5, 0xD5)
    local i = 1
    while true do
        i = string.find(m, pat, i, true)
        if not i then break end
        local base = EWRAM_START + i - 1 - 8
        local function u8(a) return string.byte(m, a - EWRAM_START + 1) or 0 end
        local function u16(a) return u8(a) + 256 * u8(a + 1) end
        local function u32(a) return u16(a) + 65536 * u16(a + 2) end
        console:log(string.format(
            "PROBE nick@0x%08X -> base=0x%08X pid=0x%08X ot=0x%08X lvl=%d hp=%d/%d",
            EWRAM_START + i - 1, base, u32(base), u32(base + 4),
            u8(base + 0x54), u16(base + 0x56), u16(base + 0x58)))
        i = i + 1
    end
    -- dump candidate 0x02005674 header + nickname bytes
    local t = {}
    for a = 0x02005674, 0x02005674 + 0x17 do
        t[#t + 1] = string.format("%02X", string.byte(m, a - EWRAM_START + 1))
    end
    console:log("PROBE cand 0x02005674: " .. table.concat(t, " "))
end)
