-- Trace wild-encounter GENERATION (not the catch). From del_end.ss (town,
-- near mart), walk into the grass exactly like wild_hunt.lua, but instead of
-- just detecting the battle, arm a write-watchpoint (type 5 = WRITE_CHANGE)
-- on gEnemyParty+0 (personality field, same offset trick as slot1.pid in
-- catch_trace.lua) to catch the PC/LR of the code that actually creates the
-- wild mon -- i.e. CreateBoxMon and its caller chain (CreateMon-equivalent
-- used by CreateMonWithIVs, called from CreateWildMon). Run with
-- MGBA_HEADLESS_DEBUGGER=1.
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"
local K = H.KEY

local hits = 0
local function wp(name, addr, typ)
    local id = emu:setWatchpoint(function()
        hits = hits + 1
        H.log(string.format("WP %-10s hit=%-3d frame=%-5d pc=0x%08X lr=0x%08X r0=0x%08X r1=0x%08X r2=0x%08X",
            name, hits, H.frame(), emu:readRegister("pc"), emu:readRegister("lr"),
            emu:readRegister("r0"), emu:readRegister("r1"), emu:readRegister("r2")))
    end, addr, typ)
    H.log(name .. " watchpoint id=" .. tostring(id))
end
wp("enemy.pid", H.gEnemyParty, 5)

H.onFrame(function(f)
    if f ~= 30 then return end
    local slots = emu:read32(0x0200B0D8 + 8)
    local key = emu:read16(emu:read32(H.gSaveBlock2Ptr) + 0xB0)
    emu:write16(slots, 1); emu:write16(slots + 2, 10 ~ key)
    H.log("balls given")
    local seq = {}
    local function add(k, n) for _ = 1, n do seq[#seq+1] = k end end
    add(K.DOWN, 3); add(K.LEFT, 4); add(K.DOWN, 2)
    add(K.LEFT, 6); add(K.DOWN, 3)
    for _ = 1, 40 do add(K.DOWN, 2); add(K.UP, 2); add(K.LEFT, 1); add(K.DOWN, 2); add(K.UP, 2); add(K.RIGHT, 1) end
    for _, k in ipairs(seq) do H.press(k, 16, 8) end
end)

local battled = false
H.onFrame(function(f)
    if not battled then
        local pid = emu:read32(H.gEnemyParty)
        local lvl = emu:read8(H.gEnemyParty + 0x54)
        if pid ~= 0 and lvl >= 1 and lvl <= 100 then
            battled = true
            H.log(string.format("WILD BATTLE @f=%d enemy pid=0x%08X lvl=%d totalHits=%d", f, pid, lvl, hits))
        end
    end
    if battled and f % 120 == 0 then
        H.log("done, finishing. totalHits=" .. hits)
        H.finish()
    end
    if f == 9000 then
        H.log("TIMEOUT no battle. totalHits=" .. hits)
        H.finish()
    end
end)
