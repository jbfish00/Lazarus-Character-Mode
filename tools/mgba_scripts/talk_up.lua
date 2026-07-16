-- Face up, press A, mash A, screenshot the dialogue/shop menu.
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"
H.press(H.KEY.UP, 6, 30)
H.press(H.KEY.A, 6, 60)
H.onFrame(function(f)
    if f == 300 then emu:screenshot(DIR.."talk1.png") end
    if f == 320 then H.press(H.KEY.A, 6, 40) end
    if f == 600 then emu:screenshot(DIR.."talk2.png") end
    if f == 620 then H.press(H.KEY.A, 6, 40) end
    if f == 900 then
        emu:screenshot(DIR.."talk3.png")
        emu:saveStateFile(DIR.."talk_end.ss")
        H.finish()
    end
end)
