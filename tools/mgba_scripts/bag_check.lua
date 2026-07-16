-- Open START menu -> find BAG -> screenshot pockets to check for Poke Balls.
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"
H.press(H.KEY.START, 6, 40)
H.onFrame(function(f)
    if f == 120 then emu:screenshot(DIR .. "menu.png") end
    if f == 130 then
        -- assume BAG is an entry; try DOWN once then A (adjust after seeing menu.png)
        H.press(H.KEY.DOWN, 6, 20)
        H.press(H.KEY.A, 6, 60)
    end
    if f == 300 then emu:screenshot(DIR .. "bag1.png") end
    if f == 310 then H.press(H.KEY.RIGHT, 6, 30) end
    if f == 450 then emu:screenshot(DIR .. "bag2.png"); H.finish() end
end)
