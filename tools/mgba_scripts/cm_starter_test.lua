-- Phase 4 native-give wrapper test. From spawn.ss (party empty, pre-starter)
-- on build/lazarus_cm.gba, A-mash through the Prof. Elia walk + starter
-- pickup (Popplio 728, OFF Red's roster). Reads build/cm_test_mode.lua.
--   cm_off: starter joins party (control — wrapper passes native give through)
--   cm_on (Red): starter STILL joins party (soft-lock guard: party was empty)
--                and nothing lands in the PC box.
-- Usage:
--   mgba-headless -t tools/savestates/spawn.ss \
--     --script tools/mgba_scripts/cm_starter_test.lua build/lazarus_cm.gba
local H = dofile("tools/mgba_scripts/harness.lua")
local cfg = dofile("build/cm_test_mode.lua")
local DIR = "build/"

local FLAG_CM = 0x945
local VAR_CM_CHAR = 0x40E0
local RED = 1
local ENDF = 8000

H.mash(H.KEY.A, 120, ENDF - 100, 60)

local function box0Count()
    local base = emu:read32(H.gPokemonStoragePtr)
    if base < 0x02000000 or base >= 0x02040000 then return -1 end
    local n = 0
    for slot = 0, 29 do
        if emu:read32(base + 4 + slot * 80) ~= 0 then n = n + 1 end
    end
    return n
end

local before = {}
local gotAt = nil
H.onFrame(function(f)
    if f == 10 then
        if cfg.cm_on then
            H.flagSet(FLAG_CM)
            H.varSet(VAR_CM_CHAR, RED)
        end
        before.party = emu:read8(H.gPlayerPartyCount)
        before.box = box0Count()
        H.log(string.format("setup: cm_on=%s party=%d box0=%d",
            tostring(cfg.cm_on), before.party, before.box))
    end
    if f > 10 and gotAt == nil and emu:read8(H.gPlayerPartyCount) > 0 then
        gotAt = f
        H.log("party count went nonzero at f=" .. f)
    end
    if f == ENDF then
        local party = emu:read8(H.gPlayerPartyCount)
        local box = box0Count()
        H.log(string.format("end: party=%d box0=%d", party, box))
        H.assertEq("starter in party", party, 1)
        if cfg.cm_on then
            H.assertEq("nothing boxed (soft-lock guard)", box, before.box)
        end
        emu:screenshot(DIR .. (cfg.cm_on and "starter_on.png" or "starter_off.png"))
        H.finish()
    end
end)
