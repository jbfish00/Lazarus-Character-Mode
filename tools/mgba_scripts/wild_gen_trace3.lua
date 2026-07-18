-- Which of the 15 static BL callers of CreateBoxMon (0x081C0AE8) actually
-- fires during a real wild encounter from del_end.ss? Breakpoint at the BL
-- instruction addresses themselves (return-address-4), so LR at each site
-- is still the value from whoever called THAT wrapper function, letting us
-- also see the wrapper's own caller in one more hop if useful.
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

local sites = {
  0x081C0AC4, 0x081C1034, 0x081C10F0, 0x081C11E6, 0x081C1242,
  0x081C1298, 0x081C1328, 0x081C13DC, 0x081C15DC, 0x081C1818,
  0x081C193C, 0x081C1B98, 0x081C1D80, 0x081C44B2, 0x081E10E4,
}
local hits = {}
for _, addr in ipairs(sites) do
    hits[addr] = 0
    emu:setBreakpoint(function()
        hits[addr] = hits[addr] + 1
        local lr = emu:readRegister("lr")
        local r0 = emu:readRegister("r0")
        H.log(string.format("SITE 0x%08X hit=%d frame=%d lr=0x%08X r0=0x%08X",
            addr, hits[addr], H.frame(), lr, r0))
    end, addr)
end

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
            H.log(string.format("WILD BATTLE @f=%d pid=0x%08X lvl=%d", f, pid, lvl))
        end
    end
    if battled and f % 120 == 0 then H.finish() end
    if f == 9000 then H.log("TIMEOUT"); H.finish() end
end)
