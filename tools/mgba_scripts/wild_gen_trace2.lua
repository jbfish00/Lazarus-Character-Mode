-- Breakpoint (not watchpoint) at the shared SetBoxMonData/SetMonData
-- dispatcher entry 0x081C36D0 (found: 3 direct BLs from CreateMon@0x080FC358,
-- and the wp trace confirmed the personality-field case lives inside it).
-- At true function entry (before its own push executes) LR is the genuine,
-- unclobbered return address -- unlike mid-function watchpoints where LR is
-- often reused as scratch. Log lr + r1 (field id) for every hit while
-- walking into grass from del_end.ss, to see the whole burst of field-sets
-- for ONE wild-mon creation and confirm they share a single caller (LR).
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

local hits = 0
local matched = 0
local seen_lr = {}
local id = emu:setBreakpoint(function()
    hits = hits + 1
    local lr = emu:readRegister("lr")
    local r1 = emu:readRegister("r1")
    local r0 = emu:readRegister("r0")
    matched = matched + 1
    if matched <= 30 then
        H.log(string.format("BP hit=%-4d frame=%-5d lr=0x%08X r0=0x%08X r1=0x%08X",
            hits, H.frame(), lr, r0, r1))
    end
    seen_lr[lr] = (seen_lr[lr] or 0) + 1
end, 0x081C0AC4)
H.log("breakpoint id=" .. tostring(id))

H.onFrame(function(f)
    if f ~= 30 then return end
    local slots = emu:read32(0x0200B0D8 + 8)
    local key = emu:read16(emu:read32(H.gSaveBlock2Ptr) + 0xB0)
    emu:write16(slots, 1); emu:write16(slots + 2, 10 ~ key)
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
            H.log(string.format("WILD BATTLE @f=%d pid=0x%08X lvl=%d totalHits=%d matched=%d", f, pid, lvl, hits, matched))
            for lr, n in pairs(seen_lr) do
                H.log(string.format("  LR=0x%08X count=%d", lr, n))
            end
        end
    end
    if battled and f % 120 == 0 then H.finish() end
    if f == 9000 then H.log("TIMEOUT"); H.finish() end
end)
