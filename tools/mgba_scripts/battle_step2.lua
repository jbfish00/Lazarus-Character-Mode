local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"
H.press(H.KEY.B, 6, 60)     -- back out of move menu
H.onFrame(function(f)
    if f == 150 then emu:screenshot(DIR.."bs3.png") end
    if f == 160 then H.press(H.KEY.RIGHT, 6, 30); H.press(H.KEY.A, 6, 60) end -- FIGHT -> BAG
    if f == 400 then emu:screenshot(DIR.."bs4.png"); emu:saveStateFile(DIR.."battle_bag.ss") end
    if f == 401 then H.finish() end
end)
