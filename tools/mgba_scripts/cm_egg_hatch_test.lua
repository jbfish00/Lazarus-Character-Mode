-- LIVE egg-hatch e2e on the TEST-ONLY ROM (build/lazarus_cm_eggtest.gba, built
-- by tools/tests/build_egg_testrom.py).
--
-- ../game_plans/rowe_parity.md §13.21 item 1: the hatch hook was verified
-- statically and by every pre-existing live layer, but no hatch had ever been
-- WALKED in an emulator here. This walks one.
--
-- From cm_red_active.ss we step onto the University desk tile (the same
-- (7,9)->(8,9)->face-up route run_trade_e2e.sh uses) and press A. In the test
-- ROM the desk runs
--   giveegg <species> ; setvar 0x8004,1 ; goto EventScript_EggHatch
-- and everything from that goto onward is SHIPPED, unmodified: the spliced
-- tail, the replayed special EggHatch / waitstate / releaseall, and the
-- callnative into CM_SweepPartyToPCNative.
--
-- ⭐ THE ASSERTION IS A SWAP, NOT A COUNT. We capture the EGG's personality out
-- of the party before the hatch and afterwards require that exact 32-bit value
-- to be either in the PC (enforced) or still in the party (control). A count
-- alone also holds when neither the give nor the sweep happened.
--
-- ⚠️ AND A COUNT IS ACTIVELY WRONG HERE. The sweep looks at the WHOLE party, so
-- on a run where the pre-existing party mon is off the active character's
-- roster it is boxed too and the count lands in the same place either way.
-- Only "which personality moved" separates the cases.
--
-- build/cm_egg_mode.lua: return {cm_on=true|false, char=<id or nil>,
--                                expect="box"|"party"}
-- Needs MGBA_HEADLESS_DEBUGGER=1 (breakpoint) and CM_SWEEP_ADDR in the
-- environment (derived from build/character_mode.elf by the runner -- never
-- hardcoded: it moves on every shim rebuild, and a stale breakpoint would
-- report "the tail was never reached" on a ROM where it plainly was).
local H = dofile("tools/mgba_scripts/harness.lua")
local cfg = dofile("build/cm_egg_mode.lua")
local K = H.KEY

local FLAG_CM     = 0x2B0
local VAR_CM_CHAR = 0x40E0
local PARTY_COUNT = 0x0201B95D
local PARTY       = 0x0201B960
local MON_SIZE    = 100
local SWEEP       = tonumber(os.getenv("CM_SWEEP_ADDR") or "0")
local STORAGE_SCAN_BYTES = 0x8600   -- covers struct PokemonStorage's box array

-- Byte-wise so nothing is assumed about where in struct PokemonStorage the box
-- array starts or how it is strided -- only that a boxed mon still carries its
-- personality as its first four bytes, which is what makes the value a usable
-- fingerprint at all.
local function inStorage(pers)
    local base = emu:read32(H.gPokemonStoragePtr)
    if base == 0 then return nil end
    for off = 0, STORAGE_SCAN_BYTES - 4 do
        if emu:read8(base + off) == (pers & 0xFF)
            and emu:read8(base + off + 1) == ((pers >> 8) & 0xFF)
            and emu:read8(base + off + 2) == ((pers >> 16) & 0xFF)
            and emu:read8(base + off + 3) == ((pers >> 24) & 0xFF) then
            return off
        end
    end
    return nil
end

local function inParty(pers)
    for i = 0, 5 do
        if emu:read32(PARTY + i * MON_SIZE) == pers then return i end
    end
    return nil
end

local before, egg = {}, {}
H.onFrame(function(f)
    if f ~= 15 then return end
    before.party = emu:read8(PARTY_COUNT)
    if cfg.cm_on then
        H.flagSet(FLAG_CM)
        if cfg.char then H.varSet(VAR_CM_CHAR, cfg.char) end
        H.log(("CM ON char=%d"):format(H.varGet(VAR_CM_CHAR)))
    else
        local a = H.flagAddr(FLAG_CM)
        emu:write8(a, emu:read8(a) & ~(1 << (FLAG_CM % 8)))
        H.log("CM OFF (control)")
    end
    H.log("start party=" .. before.party)
end)

-- Prove the SHIPPED tail was reached. The sweep is the last command in it, so
-- its entry firing means the goto landed, the replayed hatch ran and the
-- waitstate released -- the whole hook, in order.
local swept = nil
if SWEEP ~= 0 then
    H.breakpoint("sweep", SWEEP, function(fr)
        if swept == nil then
            swept = fr
            H.log(("CM_SweepPartyToPCNative entered f=%d party=%d"):format(
                fr, emu:read8(PARTY_COUNT)))
        end
    end)
end

-- walk (7,9)->(8,9), face the (8,8) desk tile, talk. Same cadence as the trade
-- e2e; only what the desk RUNS differs in this ROM.
H.onFrame(function(f)
    if f == 60 then H.press(K.RIGHT, 16) end
    if f == 120 then H.press(K.UP, 4) end
    if f == 160 then H.press(K.A, 6) end
end)

-- ⚠️ B, NOT A. B advances the "Huh?" msgbox and the "hatched from the egg!"
-- message just as A does, and -- the reason it must be B -- DECLINES the
-- nickname prompt. Mashing A there opens the naming screen and the run wedges
-- in a keyboard it has no scripted route out of.
H.mash(K.B, 200, 3800, 22)

-- Latch the egg the moment it exists, before anything can hatch it.
H.onFrame(function(f)
    if egg.pers or f < 200 then return end
    local n = emu:read8(PARTY_COUNT)
    if n == before.party + 1 then
        local m = PARTY + before.party * MON_SIZE
        local p = emu:read32(m)
        if p ~= 0 then
            egg.pers, egg.sanity, egg.count = p, emu:read8(m + 19), n
            H.log(("egg latched f=%d slot=%d pers=0x%08X sanity=0x%02X"):format(
                f, before.party, p, egg.sanity))
        end
    end
end)

local endAt = nil
H.onFrame(function(f)
    if swept and endAt == nil then endAt = f + 90 end
    if endAt and f == endAt then
        emu:screenshot("tools/savestates/egg_" .. (cfg.name or "run") .. ".png")
        local pers = egg.pers or 0
        local box = (pers ~= 0) and inStorage(pers) or nil
        local slot = (pers ~= 0) and inParty(pers) or nil
        H.log(("after: party=%d pers=0x%08X box=%s partySlot=%s"):format(
            emu:read8(PARTY_COUNT), pers, tostring(box), tostring(slot)))

        H.assertTrue("giveegg put an egg in the party", egg.count == before.party + 1)
        H.assertTrue("the new party member IS an egg (sanity bit 2)",
                     (egg.sanity or 0) & 0x04 ~= 0)
        H.assertTrue("the shipped hatch tail reached the sweep", swept ~= nil)
        if cfg.expect == "box" then
            H.assertTrue("the hatchling's personality is in the PC", box ~= nil)
            H.assertTrue("...and no longer in the party", slot == nil)
        else
            H.assertTrue("the hatchling's personality is still in the party",
                         slot ~= nil)
            H.assertTrue("...and not in the PC", box == nil)
        end
        H.finish()
    end
    if f == 4000 and endAt == nil then
        H.log("timeout: swept=" .. tostring(swept) .. " egg=" .. tostring(egg.pers))
        H.assertTrue("the shipped hatch tail reached the sweep (timeout)", false)
        H.finish()
    end
end)
