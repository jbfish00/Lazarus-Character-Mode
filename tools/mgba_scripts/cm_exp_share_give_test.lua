-- Live layer: the native Exp. Share give runs with Character Mode OFF (2026-10-21).
-- On build/lazarus_cm_expgive[_ctl].gba (tools/tests/build_expshare_testrom.py): the
-- University desk (8,8) runs `goto 0x08382D5F`, the base game's own Rotom Phone scene
-- (additem 461; setflag 0x495; additem 0x33C; then its messages).
-- From cm_red_active.ss, flag 0x2B0 is cleared first (CM off), and flag 0x495 and
-- any Exp. Share in the bag are asserted absent; the route to the desk is
-- cm_relearn_test.lua's. Then: flag 0x495 set and one item 461 in the bag.
-- The --control ROM enters after the setflag and must FAIL.
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local FLAG_CM, FLAG_EXP_SHARE, ITEM_EXP_SHARE = 0x2B0, 0x495, 461
local POCKETS = 0x0200B0D8            -- bag pocket descriptors {u32 slots*, u8 capacity}, stride 8
local SHOTS = os.getenv("CM_SHOTS")

local function expShareCount()
    local key = emu:read16(emu:read32(0x03003668) + 0xB0)
    local n = 0
    for p = 0, 7 do
        local slots, cap = emu:read32(POCKETS + 8 * p), emu:read8(POCKETS + 8 * p + 4)
        if slots >= 0x02000000 and slots < 0x02040000 and cap > 0 and cap <= 250 then
            for i = 0, cap - 1 do
                if emu:read16(slots + 4 * i) == ITEM_EXP_SHARE then
                    n = n + (emu:read16(slots + 4 * i + 2) ~ key)
                end
            end
        end
    end
    return n
end

local before, beforeFlag
H.onFrame(function(f)
    if f == 15 then
        local a = H.flagAddr(FLAG_CM)
        emu:write8(a, emu:read8(a) & (~(1 << (FLAG_CM % 8)) & 0xFF))
        before, beforeFlag = expShareCount(), H.flagGet(FLAG_EXP_SHARE)
        H.log(("setup: cm=%s 0x495=%s exp share in bag=%d"):format(tostring(H.flagGet(FLAG_CM)),
              tostring(H.flagGet(FLAG_EXP_SHARE)), before))
    end
    if f == 60 then H.press(K.RIGHT, 16) end
    if f == 120 then H.press(K.UP, 4) end
    if f == 160 then H.press(K.A, 6) end
    if f == 520 then
        if SHOTS then emu:screenshot(SHOTS .. "_given.png") end
        local n = expShareCount()
        H.log(("after the scene's give: cm=%s 0x495=%s exp share in bag=%d"):format(
              tostring(H.flagGet(FLAG_CM)), tostring(H.flagGet(FLAG_EXP_SHARE)), n))
        H.assertTrue("before: no Exp. Share in the bag and flag 0x495 clear", before == 0 and not beforeFlag)
        H.assertTrue("Character Mode stays off", not H.flagGet(FLAG_CM))
        H.assertTrue("flag 0x495 (IsExpShareEnabled) is set", H.flagGet(FLAG_EXP_SHARE))
        H.assertEq("one Exp. Share (item 461) is in the bag", n, 1)
        H.finish()
    end
end)
