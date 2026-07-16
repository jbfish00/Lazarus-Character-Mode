-- THE 1f TRACE. From battle_bag.ss (battle bag open, Items pocket):
-- page RIGHT to Balls, select Poke Ball, throw. Watchpoints (write) on
-- gPlayerPartyCount and gPlayerParty slot1 catch the give-path PC.
-- Run with MGBA_HEADLESS_DEBUGGER=1.
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"

local hits = 0
local function wp(name, addr, typ)
    local id = emu:setWatchpoint(function()
        hits = hits + 1
        if hits <= 40 then
            H.log(string.format("WP %-10s pc=0x%08X lr=0x%08X r0=0x%08X r1=0x%08X",
                name, emu:readRegister("pc"), emu:readRegister("lr"),
                emu:readRegister("r0"), emu:readRegister("r1")))
        end
    end, addr, typ)
    H.log(name .. " watchpoint id=" .. tostring(id))
end
-- WATCHPOINT_WRITE_CHANGE=5: only actual value changes (count 1->2)
wp("partyCount", H.gPlayerPartyCount, 5)
wp("slot1.pid", H.gPlayerParty + 100, 5)

H.onFrame(function(f)
    if f == 60 then H.press(H.KEY.RIGHT, 6, 40) end        -- Items -> Balls
    if f == 160 then emu:screenshot(DIR.."ct1.png") end
    if f == 170 then H.press(H.KEY.A, 6, 40) end           -- select Poke Ball
    if f == 300 then emu:screenshot(DIR.."ct2.png") end
    if f == 310 then H.press(H.KEY.A, 6, 40) end           -- confirm use/throw
    if f == 500 then emu:screenshot(DIR.."ct3.png") end
    -- catch animation runs several hundred frames; mash A after to advance
    if f > 600 and f < 3400 and f % 70 == 0 then H.press(H.KEY.A, 6, 30) end
    if f == 3500 then
        emu:screenshot(DIR.."ct4.png")
        H.log(string.format("end: partyCount=%d slot1pid=0x%08X wpHits=%d",
            emu:read8(H.gPlayerPartyCount), emu:read32(H.gPlayerParty + 100), hits))
        emu:saveStateFile(DIR.."after_catch.ss")
        H.finish()
    end
end)
