-- Live layer: party-wide Exp. Share with Character Mode OFF (user, 2026-10-21).
--
-- Lazarus's Exp. Share is native and CM-independent: the pre-gym-1 Rotom Phone
-- scene (script bytes at 0x08382D5F: additem 461; setflag 0x495; additem 0x33C)
-- gives it to every player, and the battle engine's share test is
-- IsExpShareEnabled 0x080D1270 = FlagGet(0x495) (4 callers in the getexp code).
-- This layer runs a REAL battle to its end with CM off:
--   from battle_menu.ss (wild Hoppip, the move list open on Pound), flag 0x2B0 is cleared,
--   party slot 0 (Popplio) is copied into slot 1 as a bench mon that never
--   battles, the foe's battle HP is set to 1, and Pound wins (the foe's speed is set to 1 so it can't heal first).
--   SHARE=1: flag 0x495 set   -> the battler AND the bench mon gain EXP
--   SHARE=0: flag 0x495 clear -> the battler gains EXP, the bench mon does not
--            (the control: the bench mon's EXP comes from the flag, nothing else)
-- EXP is read by decrypting the party substructures (mon_decrypt.lua, checksum
-- validated).
local H = dofile("tools/mgba_scripts/harness.lua")
local M = dofile("tools/mgba_scripts/mon_decrypt.lua")
local K = H.KEY
local FLAG_CM, FLAG_EXP_SHARE = 0x2B0, 0x495
local GBATTLEMONS = 0x02000360        -- gBattleMons, stride 0x60 (cm_sure_catch_test.lua)
local SHARE = os.getenv("SHARE") == "1"
local SHOTS = os.getenv("CM_SHOTS")
local before0, before1

local function setFlag(id, on)
    local a = H.flagAddr(id)
    local v = emu:read8(a)
    local bit = 1 << (id % 8)
    emu:write8(a, on and (v | bit) or (v & (~bit & 0xFF)))
end

H.onFrame(function(f)
    if f == 5 then
        setFlag(FLAG_CM, false)
        setFlag(FLAG_EXP_SHARE, SHARE)
        for k = 0, 99 do emu:write8(H.gPlayerParty + 100 + k, emu:read8(H.gPlayerParty + k)) end
        emu:write8(H.gPlayerPartyCount, 2)
        emu:write16(GBATTLEMONS + 0x60 + 0x2A, 1)              -- foe hp = 1
        emu:write16(GBATTLEMONS + 0x60 + 0x06, 1)              -- foe speed = 1 (Hoppip outspeeds and heals)
        local a, b = M.decode(H.gPlayerParty), M.decode(H.gPlayerParty + 100)
        before0, before1 = a.exp, b.exp
        H.log(("setup: share=%s cm=%s 0x495=%s slot0 %d exp %d (ok %s), slot1 %d exp %d (ok %s), move1=%d"):format(
            tostring(SHARE), tostring(H.flagGet(FLAG_CM)), tostring(H.flagGet(FLAG_EXP_SHARE)), a.species, a.exp, tostring(a.ok),
            b.species, b.exp, tostring(b.ok), emu:read16(GBATTLEMONS + 0x0C)))
    end
    if f == 30 then H.press(K.A, 6) end                        -- the state opens on the move list: Pound
    if f > 200 and f < 2400 and f % 40 == 0 then H.press(K.B, 6) end
    if SHOTS and (f == 400 or f == 2500) then emu:screenshot(SHOTS .. "_" .. f .. ".png") end
    if f == 2600 then
        local a, b = M.decode(H.gPlayerParty), M.decode(H.gPlayerParty + 100)
        H.log(("after: slot0 exp %d -> %d, slot1 exp %d -> %d, foe battle hp %d"):format(
            before0, a.exp, before1, b.exp, emu:read16(GBATTLEMONS + 0x60 + 0x2A)))
        H.assertTrue("Character Mode is off", not H.flagGet(FLAG_CM))
        H.assertTrue("both party mons decrypt (checksums)", a.ok and b.ok and a.species == 728 and b.species == 728)
        H.assertTrue("the battler gained EXP (the battle was won)", a.exp > before0)
        if SHARE then
            H.assertTrue("the bench mon gained EXP too (party-wide Exp. Share)", b.exp > before1)
        else
            H.assertEq("control, flag 0x495 clear: the bench mon's EXP is unchanged", b.exp, before1)
        end
        H.finish()
    end
end)
