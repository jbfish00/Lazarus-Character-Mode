-- Stepwise battle UI driver: dismiss intro, screenshot the action menu.
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"
H.press(H.KEY.A, 6, 60)
H.onFrame(function(f)
    if f == 200 then emu:screenshot(DIR.."bs1.png") end
    if f == 210 then H.press(H.KEY.A, 6, 60) end
    if f == 400 then emu:screenshot(DIR.."bs2.png"); emu:saveStateFile(DIR.."battle_menu.ss") end
    if f == 401 then H.finish() end
end)
