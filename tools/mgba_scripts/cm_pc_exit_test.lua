-- LIVE PC-exit e2e on the TEST-ONLY ROM (build/lazarus_cm_pctest.gba, built by
-- tools/tests/build_pc_testrom.py).
--
-- ../game_plans/rowe_parity.md §13.33 item 1. The PC-exit hook shipped in all
-- four GBA games on STATIC evidence alone; Seaglass got the first live layer on
-- 2026-09-10 and this is the port. §13.20 is why it matters: four live layers in
-- three repos were once found dead behind a fully green static suite.
--
-- From cm_red_active.ss we step onto the University desk tile (the same
-- (7,9)->(8,9)->face-up route the trade and egg layers use) and press A. In the
-- test ROM the desk runs
--   giveegg 60 ; setvar 0x8004,1 ; <inline hatch> ; goto 0x08326A28
-- and everything from that goto onward is SHIPPED, unmodified: the overlay, the
-- replayed `special 0x3F` + `waitstate` that opens the storage system and waits
-- for it to close, and the `callnative CM_SweepPartyToPCNative` that runs when
-- it does.
--
-- ⚠️ The hatch is FIXTURE, not the thing under test. It is the only way to get an
-- off-roster mon INTO the party: the gift gate boxes an off-roster gift on the
-- way in, while eggs are exempt everywhere. The savestate's own party mon is the
-- never-empty anchor -- without SOME keeper the sweep keeps the hatchling for
-- every character and the layer discriminates nothing.
--
-- ⭐ THE ASSERTION IS A SWAP, NOT A COUNT, and a count is actively wrong here:
-- the sweep looks at the WHOLE party, so on a run where the pre-existing party
-- mon is also off-roster it is boxed too and the count lands in the same place
-- either way. Only "which personality moved" separates the cases.
--
-- ⭐⭐ AND IT BREAKPOINTS THE STORAGE SYSTEM'S OWN HANDLER, gSpecials[0x3F],
-- passed in by the runner (derived from the built ROM's table -- never hardcoded
-- here). That is what turns "the script ran" into "the PC opened": if
-- `special 0x3F` did nothing, its waitstate would release at once, the sweep
-- would still fire, and the hook would look perfectly green while never having
-- involved a PC at all.
--
-- build/cm_pc_mode.lua: return {cm_on=true|false, char=<id or nil>,
--                               expect="box"|"party", name="..."}
-- Needs MGBA_HEADLESS_DEBUGGER=1 and CM_SWEEP_ADDR + CM_PSS_ADDR in the
-- environment (both derived by the runner; a stale sweep literal would report
-- "the PC exit never reached the sweep" on a ROM where it plainly did).
local H = dofile("tools/mgba_scripts/harness.lua")
local cfg = dofile("build/cm_pc_mode.lua")
local K = H.KEY

local FLAG_CM     = 0x2B0
local VAR_CM_CHAR = 0x40E0
local PARTY_COUNT = 0x0201B95D
local PARTY       = 0x0201B960
local MON_SIZE    = 100
local SWEEP       = tonumber(os.getenv("CM_SWEEP_ADDR") or "0")
local PSS         = tonumber(os.getenv("CM_PSS_ADDR") or "0")
-- The PC is opened, HELD open, then closed. Left to the B-mash it backs out in
-- the same frame the menu appears, which makes the open window an accident of
-- the mash cadence rather than something this layer controls.
local HOLD_OPEN     = 90
local MIN_UI_FRAMES = 60
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

-- Prove the SHIPPED tail was reached. The sweep sits after the replayed
-- waitstate, so its entry firing means the overlay's goto landed, the storage
-- system opened, and it closed again -- the whole hook, in order.
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

local pssAt = nil
if PSS ~= 0 then
    H.breakpoint("pss", PSS, function(fr)
        if pssAt == nil then
            pssAt = fr
            H.log(("storage system special entered f=%d"):format(fr))
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

-- ⚠️ B, NOT A, and now for THREE reasons. B advances the "Huh?" msgbox and the
-- "hatched from the egg!" message, it DECLINES the nickname prompt (A opens the
-- naming screen and the run wedges in a keyboard it has no route out of), and it
-- is what backs out of the storage system -- where A would dive INTO a box, with
-- no route back out either.
-- ⭐ The mash PAUSES while the PC is open, so the open window is deterministic
-- and assertable rather than an accident of the cadence.
H.onFrame(function(f)
    if f < 200 or f > 3800 then return end
    if pssAt and f < pssAt + HOLD_OPEN then emu:clearKey(K.B); return end
    if (f // 22) % 2 == 0 then emu:addKey(K.B) else emu:clearKey(K.B) end
end)

H.onFrame(function(f)
    if pssAt and f == pssAt + 45 then
        emu:screenshot("tools/savestates/pcexit_" .. (cfg.name or "run")
                       .. "_open.png")
    end
end)

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
        emu:screenshot("tools/savestates/pcexit_" .. (cfg.name or "run") .. ".png")
        local pers = egg.pers or 0
        local box = (pers ~= 0) and inStorage(pers) or nil
        local slot = (pers ~= 0) and inParty(pers) or nil
        H.log(("after: party=%d pers=0x%08X box=%s partySlot=%s"):format(
            emu:read8(PARTY_COUNT), pers, tostring(box), tostring(slot)))

        H.log(("storage special f=%s, sweep f=%s -- UI up for %s frames"):format(
            tostring(pssAt), tostring(swept),
            tostring(swept and pssAt and (swept - pssAt))))

        H.assertTrue("giveegg put an egg in the party", egg.count == before.party + 1)
        H.assertTrue("the new party member WAS an egg (sanity bit 2)",
                     (egg.sanity or 0) & 0x04 ~= 0)
        H.assertTrue("closing the PC reached the shipped sweep", swept ~= nil)
        H.assertTrue("the storage system special really ran, BEFORE the sweep",
                     pssAt ~= nil and swept ~= nil and pssAt < swept)
        H.assertTrue("...and the PC stayed open long enough to be real "
                     .. "(not a no-op special)",
                     swept ~= nil and pssAt ~= nil
                     and (swept - pssAt) >= MIN_UI_FRAMES)
        if cfg.expect == "box" then
            H.assertTrue("the off-roster hatchling's personality is in the PC", box ~= nil)
            H.assertTrue("...and no longer in the party", slot == nil)
        else
            H.assertTrue("the hatchling's personality is still in the party",
                         slot ~= nil)
            H.assertTrue("...and not in the PC", box == nil)
        end
        H.finish()
    end
    if f == 4000 and endAt == nil then
        H.log("timeout: swept=" .. tostring(swept) .. " egg=" .. tostring(egg.pers)
              .. " pssAt=" .. tostring(pssAt))
        H.assertTrue("closing the PC reached the shipped sweep (timeout)", false)
        H.finish()
    end
end)
