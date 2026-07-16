-- "Give item" debug capability (ROWE debug-menu port): write 10 Poke Balls
-- into bag pocket 2 (Balls). Structure from AddBagItem @0x0815CCD0 disasm:
--   pocket descriptor table @0x0200B0D8, stride 8, [pocket-1]: {u32 slots*, u8 cap}
--   slot: {u16 itemId, u16 qty XOR key}; key = u16 @ (*gSaveBlock2Ptr)+0xB0
--   Poke Ball item id = 1 (gItemsInfo @0x08868520, name +0x3C, pocket +0x69)
local H = dofile("tools/mgba_scripts/harness.lua")
local DIR = "tools/savestates/"
local POCKETS = 0x0200B0D8
H.onFrame(function(f)
    if f ~= 60 then return end
    local desc = POCKETS + 8 * (2 - 1)
    local slots = emu:read32(desc)
    local cap = emu:read8(desc + 4)
    local sb2 = emu:read32(H.gSaveBlock2Ptr)
    local key = emu:read16(sb2 + 0xB0)
    H.log(string.format("pocket2 slots=0x%08X cap=%d key=0x%04X slot0=%04X/%04X",
        slots, cap, key, emu:read16(slots), emu:read16(slots + 2)))
    emu:write16(slots, 1)            -- ITEM_POKE_BALL
    emu:write16(slots + 2, 10 ~ key) -- qty 10, encrypted
    H.log(string.format("wrote 10 Poke Balls; readback id=%d qty=%d",
        emu:read16(slots), emu:read16(slots + 2) ~ key))
end)
-- proof: open bag to the Balls pocket
H.onFrame(function(f)
    if f == 120 then H.press(H.KEY.START, 6, 40) end
    if f == 220 then H.press(H.KEY.DOWN, 6, 20); H.press(H.KEY.A, 6, 60) end
    if f == 420 then H.press(H.KEY.RIGHT, 6, 30) end
    if f == 560 then
        emu:screenshot(DIR .. "balls_proof.png")
        H.finish()
    end
end)
