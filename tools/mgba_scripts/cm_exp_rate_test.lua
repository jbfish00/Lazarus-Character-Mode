-- Live layer: EXP rate (QoL, user 2026-10-29; src/character_mode.c "EXP rate").
-- cm_exp_share_test.lua's battle (battle_menu.ss: wild Hoppip, the move list open on Pound; Popplio copied into
-- slot 1 as a bench mon, foe hp 1 and speed 1, Exp. Share flag 0x495 set, Character Mode OFF: the rate works in every
-- save) with VAR_EXP_RATE (0x40E1) = RATE. Asserts the EXP gained by the battler and by the bench mon:
--   WANT0 / WANT1 = the expected gains (tools/tests/run_live_suite.sh pins them per rate:
--   x1 gain * N / 2, N = 2 (x1), 3 (x1.5), 4 (x2), 6 (x3), 1 (x0.5); a nonzero award never becomes 0).
local H = dofile("tools/mgba_scripts/harness.lua")
local M = dofile("tools/mgba_scripts/mon_decrypt.lua")
local K = H.KEY
local FLAG_CM, FLAG_EXP_SHARE, VAR_EXP_RATE = 0x2B0, 0x495, 0x40E1
local GBATTLEMONS = 0x02000360
local RATE = tonumber(os.getenv("RATE") or "0")
local WANT0, WANT1 = tonumber(os.getenv("WANT0") or "-1"), tonumber(os.getenv("WANT1") or "-1")
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
        setFlag(FLAG_EXP_SHARE, true)
        H.varSet(VAR_EXP_RATE, RATE)
        for k = 0, 99 do emu:write8(H.gPlayerParty + 100 + k, emu:read8(H.gPlayerParty + k)) end
        emu:write8(H.gPlayerPartyCount, 2)
        emu:write16(GBATTLEMONS + 0x60 + 0x2A, 1)
        emu:write16(GBATTLEMONS + 0x60 + 0x06, 1)
        before0, before1 = M.decode(H.gPlayerParty).exp, M.decode(H.gPlayerParty + 100).exp
    end
    if f == 30 then H.press(K.A, 6) end
    if f > 200 and f < 2400 and f % 40 == 0 then H.press(K.B, 6) end
    if f == 2600 then
        local a, b = M.decode(H.gPlayerParty), M.decode(H.gPlayerParty + 100)
        H.log(("rate %d: battler +%d, bench +%d (want %d / %d)"):format(RATE, a.exp - before0, b.exp - before1, WANT0, WANT1))
        H.assertTrue("Character Mode is off and both mons decrypt", not H.flagGet(FLAG_CM) and a.ok and b.ok)
        H.assertEq("the rate var survived the battle", H.varGet(VAR_EXP_RATE), RATE)
        H.assertEq("battler EXP gained", a.exp - before0, WANT0)
        H.assertEq("bench EXP gained (Exp. Share)", b.exp - before1, WANT1)
        H.finish()
    end
end)
