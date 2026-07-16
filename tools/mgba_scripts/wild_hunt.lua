-- From del_end.ss (6,33 town): give balls, walk SW into the flowery grass,
-- oscillate until a wild battle starts (gEnemyParty slot0 becomes a plausible
-- mon), then savestate wild_battle.ss.
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"
local K, STEP = H.KEY, 16
H.onFrame(function(f)
    if f ~= 30 then return end
    -- balls (same as give_pokeballs.lua)
    local slots = emu:read32(0x0200B0D8 + 8)
    local key = emu:read16(emu:read32(H.gSaveBlock2Ptr) + 0xB0)
    emu:write16(slots, 1); emu:write16(slots + 2, 10 ~ key)
    H.log("balls given")
    -- head southwest into the flower/grass area
    local seq = {}
    local function add(k, n) for _ = 1, n do seq[#seq+1] = k end end
    add(K.DOWN, 3); add(K.LEFT, 4); add(K.DOWN, 2)
    add(K.LEFT, 6); add(K.DOWN, 3)
    for _ = 1, 40 do add(K.DOWN, 2); add(K.UP, 2); add(K.LEFT, 1); add(K.DOWN, 2); add(K.UP, 2); add(K.RIGHT, 1) end
    for _, k in ipairs(seq) do H.press(k, STEP, 8) end
end)
local last, battled = nil, false
H.onFrame(function(f)
    local b = emu:read32(H.gSaveBlock1Ptr)
    if b >= 0x02000000 and b < 0x02040000 then
        local cur = string.format("x=%d y=%d map=%d.%d", emu:read16(b), emu:read16(b+2), emu:read8(b+4), emu:read8(b+5))
        if cur ~= last then H.log("f="..f.." "..cur); last = cur end
    end
    if not battled then
        local pid = emu:read32(H.gEnemyParty)
        local lvl = emu:read8(H.gEnemyParty + 0x54)
        if pid ~= 0 and lvl >= 1 and lvl <= 100 then
            battled = true
            H.log(string.format("WILD BATTLE: enemy pid=0x%08X lvl=%d", pid, lvl))
            -- wait for battle UI then save
        end
    end
    if battled and f % 300 == 0 then
        emu:screenshot(DIR .. "wild_battle.png")
        emu:saveStateFile(DIR .. "wild_battle.ss")
        H.log("SAVED wild_battle.ss @f=" .. f)
        H.finish()
    end
    if f == 9000 then
        emu:screenshot(DIR .. "hunt_timeout.png")
        H.log("TIMEOUT no battle"); H.finish()
    end
end)
