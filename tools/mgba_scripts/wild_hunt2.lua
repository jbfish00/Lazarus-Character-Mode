-- From hunt end (map 0.62 ~(4,2), tall grass just south): oscillate in grass.
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"
local K, STEP = H.KEY, 16
H.onFrame(function(f)
    if f ~= 30 then return end
    local seq = {}
    local function add(k, n) for _ = 1, n do seq[#seq+1] = k end end
    add(K.DOWN, 3)
    for _ = 1, 40 do add(K.LEFT, 1); add(K.RIGHT, 1); add(K.DOWN, 1); add(K.UP, 1) end
    for _, k in ipairs(seq) do H.press(k, STEP, 8) end
end)
local battled = false
H.onFrame(function(f)
    if not battled then
        local pid = emu:read32(H.gEnemyParty)
        local lvl = emu:read8(H.gEnemyParty + 0x54)
        if pid ~= 0 and lvl >= 1 and lvl <= 100 then
            battled = true
            H.log(string.format("WILD BATTLE @f=%d enemy pid=0x%08X lvl=%d", f, pid, lvl))
        end
    elseif f % 300 == 0 then
        emu:screenshot(DIR .. "wild_battle.png")
        emu:saveStateFile(DIR .. "wild_battle.ss")
        H.log("SAVED wild_battle.ss @f=" .. f)
        H.finish()
    end
    if f == 9000 then emu:screenshot(DIR.."hunt2_timeout.png"); H.log("TIMEOUT"); H.finish() end
end)
