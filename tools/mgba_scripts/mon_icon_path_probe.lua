-- Roster display: the MON-icon path in LAZARUS, proved live (2026-09-27).
-- Ported from the Seaglass port's tools/mgba_scripts/mon_icon_path_probe.lua;
-- the method transfers, every address below was re-derived from THIS binary
-- (docs/ROUTINE_MAP.md "Mon icons").
--
-- Opens the party menu from cm_red_active.ss (one Pikachu, species 25) and checks:
--   1. the party menu calls CreateMonIcon (0x081CFE08) with species 25;
--   2. the icon sprite's `images` is *(gSpeciesInfo + 25*212 + 120);
--   3. the sprite's VRAM tiles equal frame 0 and, as it animates, frame 1;
--   4. the OBJ palette equals gMonIconPaletteTable[low 3 bits of +134].
-- ⚠️ gSpeciesInfo is 0x08C7A338 and the stride is 212 (Seaglass: 208); the
-- documented "species name table" 0x08C7A364 is the name field at +44.
--
-- Run: MGBA_HEADLESS_DEBUGGER=1 CM_EXPECT_CHECKS=7 <mgba-headless> \
--        --script tools/mgba_scripts/mon_icon_path_probe.lua \
--        -t tools/savestates/cm_red_active.ss build/lazarus_cm.gba
local H = dofile("tools/mgba_scripts/harness.lua")

local gSpeciesInfo = 0x08C7A338
local SPECIES_INFO_SIZE = 212
local ICON_SPRITE_OFF, ICON_PAL_OFF = 120, 134
local gMonIconPaletteTable = 0x08CCC360
local CreateMonIcon = 0x081CFE08
local gSprites, SPRITE_SIZE = 0x0203B5CC, 68
local SPECIES = 25   -- Pikachu, Red's starter and the savestate's only party member

local rec = gSpeciesInfo + SPECIES * SPECIES_INFO_SIZE
local iconPtr = emu:read32(rec + ICON_SPRITE_OFF)
local palIdx = emu:read8(rec + ICON_PAL_OFF) & 7

local createdWith = nil
emu:setBreakpoint(function()
    if createdWith == nil then createdWith = emu:readRegister("r0") end
end, CreateMonIcon)

local function iconSprite()
    if iconPtr < 0x08000000 or iconPtr >= 0x0A000000 then return nil end
    for i = 0, 63 do
        local b = gSprites + i * SPRITE_SIZE
        if emu:read32(b + 12) == iconPtr and (emu:read8(b + 62) & 1) == 1 then return b end
    end
end

local function tilesEqual(vram, src)
    for k = 0, 511 do
        if emu:read8(vram + k) ~= emu:read8(src + k) then return false end
    end
    return true
end

local sawFrame = { [0] = false, [1] = false }
local spr
H.onFrame(function(f)
    if f == 20 then H.press(H.KEY.START, 4, 10) end
    if f == 95 then H.press(H.KEY.A, 4, 10) end
    if f >= 220 and f < 320 then
        spr = spr or iconSprite()
        if spr then
            local vram = 0x06010000 + (emu:read16(spr + 4) & 0x3FF) * 32
            for fr = 0, 1 do
                if tilesEqual(vram, iconPtr + fr * 512) then sawFrame[fr] = true end
            end
        end
    end
    if f == 320 then
        emu:screenshot("tools/savestates/mon_icon_party.png")
        H.assertEq("party menu called CreateMonIcon with species", createdWith, SPECIES)
        H.assertTrue("icon pointer is a ROM address", iconPtr >= 0x08000000 and iconPtr < 0x0A000000)
        H.assertTrue("an in-use sprite draws from gSpeciesInfo[25]+120", spr ~= nil)
        H.assertTrue("VRAM equals frame 0 of the icon", sawFrame[0])
        H.assertTrue("VRAM equals frame 1 of the icon (it animates)", sawFrame[1])
        local ok = spr ~= nil
        if ok then
            local palNum = (emu:read16(spr + 4) >> 12) & 15
            local romPal = emu:read32(gMonIconPaletteTable + palIdx * 8)
            for k = 0, 15 do
                if emu:read16(0x05000200 + palNum * 32 + k * 2) ~= emu:read16(romPal + k * 2) then ok = false end
            end
        end
        H.assertTrue("OBJ palette equals gMonIconPaletteTable[+134 & 7]", ok)
        H.assertEq("palette table tag is POKE_ICON_BASE_PAL_TAG + index",
            emu:read16(gMonIconPaletteTable + palIdx * 8 + 4), 0xDAC0 + palIdx)
        H.finish()
    end
end)
