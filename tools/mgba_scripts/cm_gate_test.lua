-- Phase 4 catch-gate test. Run on build/lazarus_cm.gba from battle_bag.ss
-- (battle bag open on Items pocket, wild Hoppip = species 187, off Red's
-- roster). Reads build/cm_test_mode.lua for {cm_on=true|false}.
--   cm_on:  expect Hoppip redirected to PC (party stays 1, box gains a mon)
--   cm_off: expect normal catch (party grows to 2) — control run
-- Usage:
--   mgba-headless -t tools/savestates/battle_bag.ss \
--     --script tools/mgba_scripts/cm_gate_test.lua build/lazarus_cm.gba
local H = dofile("tools/mgba_scripts/harness.lua")
local cfg = dofile("build/cm_test_mode.lua")
local DIR = "build/"

local FLAG_CM = 0x945
local VAR_CM_CHAR = 0x40E0
local RED = 1

local function storageBox0Count()
    local base = emu:read32(H.gPokemonStoragePtr)
    if base < 0x02000000 or base >= 0x02040000 then return -1 end
    local n = 0
    for slot = 0, 29 do
        if emu:read32(base + 4 + slot * 80) ~= 0 then n = n + 1 end
    end
    return n
end

local before = {}
H.onFrame(function(f)
    if f == 10 then
        if cfg.cm_on then
            H.flagSet(FLAG_CM)
            H.varSet(VAR_CM_CHAR, RED)
        end
        before.party = emu:read8(H.gPlayerPartyCount)
        before.box = storageBox0Count()
        H.log(string.format("setup: cm_on=%s party=%d box0=%d flag=%s var=%d",
            tostring(cfg.cm_on), before.party, before.box,
            tostring(H.flagGet(FLAG_CM)), H.varGet(VAR_CM_CHAR)))
    end
    -- catch replay (identical timings to catch_trace.lua)
    if f == 60 then H.press(H.KEY.RIGHT, 6, 40) end
    if f == 170 then H.press(H.KEY.A, 6, 40) end
    if f == 310 then H.press(H.KEY.A, 6, 40) end
    if f > 600 and f < 3400 and f % 70 == 0 then H.press(H.KEY.A, 6, 30) end
    if f == 3500 then
        local party = emu:read8(H.gPlayerPartyCount)
        local box = storageBox0Count()
        local slot1pid = emu:read32(H.gPlayerParty + 100)
        H.log(string.format("end: party=%d box0=%d slot1pid=0x%08X", party, box, slot1pid))
        if cfg.cm_on then
            H.assertEq("party unchanged (gated)", party, before.party)
            H.assertEq("slot1 still empty", slot1pid, 0)
            H.assertEq("box0 gained the mon", box, before.box + 1)
        else
            H.assertEq("party grew (control)", party, before.party + 1)
        end
        emu:screenshot(DIR .. (cfg.cm_on and "gate_on.png" or "gate_off.png"))
        H.finish()
    end
end)
