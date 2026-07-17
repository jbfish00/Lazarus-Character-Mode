-- From cheat_ui.ss (desk dialogue open), A-mash through the dialogue until
-- the code-entry naming screen appears; screenshot every 120 frames so the
-- transition can be located, save naming.ss at the end.
-- Usage: mgba-headless -t tools/savestates/cheat_ui.ss \
--          --script tools/mgba_scripts/desk_to_naming.lua build/lazarus_cm.gba
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"

H.mash(H.KEY.A, 10, 600, 40)

H.onFrame(function(f)
    if f % 120 == 0 and f > 0 and f <= 960 then
        emu:screenshot(DIR .. string.format("naming_%03d.png", f))
    end
    if f == 960 then
        emu:saveStateFile(DIR .. "naming.ss")
        H.log("saved naming.ss")
        H.finish()
    end
end)
