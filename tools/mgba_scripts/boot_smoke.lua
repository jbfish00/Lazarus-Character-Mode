-- Phase 4 boot smoke: run a ROM (original or patched) from boot, A-mash
-- through title/naming, and verify the SaveBlock trio goes live and the
-- overworld spawn map is reached. Pass/fail via harness summary.
-- Usage: mgba-headless --script tools/mgba_scripts/boot_smoke.lua <rom>
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "build/"

H.mash(H.KEY.A, 300, 6800, 60)

local done = false
H.onFrame(function(f)
    if f == 7200 and not done then
        done = true
        local b1 = emu:read32(H.gSaveBlock1Ptr)
        local b2 = emu:read32(H.gSaveBlock2Ptr)
        local b3 = emu:read32(H.gPokemonStoragePtr)
        H.assertTrue("SB1 in EWRAM", b1 >= 0x02000000 and b1 < 0x02040000)
        H.assertTrue("SB2 in EWRAM", b2 >= 0x02000000 and b2 < 0x02040000)
        H.assertTrue("Storage in EWRAM", b3 >= 0x02000000 and b3 < 0x02040000)
        if b1 >= 0x02000000 and b1 < 0x02040000 then
            local map = string.format("%d.%d", emu:read8(b1 + 4), emu:read8(b1 + 5))
            H.assertEq("spawn map", map, "0.57")
            H.log("map=" .. map .. string.format(" x=%d y=%d", emu:read16(b1), emu:read16(b1 + 2)))
        end
        emu:screenshot(DIR .. "boot_smoke.png")
        H.finish()
    end
end)
