-- LIVE layer (QoL A3, 2026-10-28): a new game starts with battle animations off.
-- Cold boot with no save, A-mash the whole real intro (as the probe that found SetDefaultOptions did), then read
-- SaveBlock2+0x15 bit 2 (optionsBattleSceneOff). WANT=1 on the shipped ROM, WANT=0 on CM_NO_ANIMDEFAULT=1.
-- Also asserts SetDefaultOptions (0x08189604) ran, so a 0 cannot come from an intro that never reached it.
local H = dofile("tools/mgba_scripts/harness.lua")
local want = tonumber(os.getenv("WANT") or "1")
local ran = 0
H.breakpoint("SetDefaultOptions", 0x08189604, function() ran = ran + 1 end)
H.onFrame(function(f)
    local m = f % 24
    if m == 2 then emu:addKey(H.KEY.A) elseif m == 8 then emu:clearKey(H.KEY.A) end
    if f % 300 == 150 then emu:addKey(H.KEY.START) elseif f % 300 == 156 then emu:clearKey(H.KEY.START) end
    if f ~= 9000 then return end
    local sb2 = emu:read32(H.gSaveBlock2Ptr)
    H.assertTrue("SetDefaultOptions ran during the intro", ran >= 1)
    H.assertEq("text speed is the game's own default (fast, 2)", emu:read8(sb2 + 0x14) & 7, 2)
    H.assertEq("battle animations off (SaveBlock2+0x15 bit 2)", (emu:read8(sb2 + 0x15) >> 2) & 1, want)
    H.finish()
end)
