-- LIVE e2e for the link-trade sweep (CM_LinkTradeSweepThenExpand,
-- src/character_mode.c; verify_artifacts section 18; rowe_parity.md §13.53).
-- Added 2026-09-30.
--
-- A real link trade needs two consoles, which headless mGBA can't provide. What
-- CAN be run for real is the code the hook lives in: the two callbacks the link
-- trade installs after its animation and evolution (CB2_TryLinkTradeEvolution
-- 0x08226CC0/0x08226CF8), CB2_SaveAndEndTrade 0x08227424 and
-- CB2_SaveAndEndWirelessTrade 0x08227A98. This layer reuses the PC-guard
-- fixture (build/lazarus_cm_pctest.gba: party [Pikachu, an alive hatched
-- Poliwag], the PC open), installs one ender at state 0 the way the trade
-- does, and stops at the return of its hooked BL, before any link traffic.
--
-- ⭐ The SWAP is asserted (which personality went where), and it discriminates:
--   RED   (1):  Pikachu ON,  Poliwag OFF -> Poliwag boxed, Pikachu stays
--   MISTY (10): Pikachu OFF, Poliwag ON  -> Pikachu boxed, Poliwag stays
--   CM off                               -> nothing moves (vanilla)
-- and the --no-link-sweep ROM must FAIL. The expansion must still happen
-- ("Comm..." in gStringVar4), or the hook broke the screen text.
--
-- Env: CM_ON 1/0, CM_CHAR, EXPECT box1|box0|none, ENDER wired|wireless,
-- CM_PSS_ADDR, CM_SHIM_ADDR (0 on the no-hook ROM), CM_SHOT_PREFIX.
-- Needs MGBA_HEADLESS_DEBUGGER=1.
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

local FLAG_CM     = 0x2B0
local VAR_CM_CHAR = 0x40E0
local PARTY_COUNT = 0x0201B95D
local PARTY       = 0x0201B960
local MON_SIZE    = 100
local STORAGE_SCAN_BYTES = 0x8600

local CM_ON   = (os.getenv("CM_ON") == "1")
local CM_CHAR = tonumber(os.getenv("CM_CHAR") or "1")
local EXPECT  = os.getenv("EXPECT") or "box1"
local ENDER   = os.getenv("ENDER") or "wired"
local PSS     = tonumber(os.getenv("CM_PSS_ADDR") or "0")
local SHIM    = tonumber(os.getenv("CM_SHIM_ADDR") or "0")
local PREFIX  = os.getenv("CM_SHOT_PREFIX") or "build/linksweep"

local gMain_callback2 = 0x030014B8 + 4
local gMain_state     = 0x030014B8 + 0x438
local gStringVar4     = 0x0203CEE0
local ENDERS = {   -- callback | 1, the return address of its hooked BL
    wired    = {0x08227425, 0x0822744E},
    wireless = {0x08227A99, 0x08227B2C},
}
local CB2, EXPAND_RETURN = ENDERS[ENDER][1], ENDERS[ENDER][2]

local function inStorage(pers)
    local base = emu:read32(H.gPokemonStoragePtr)
    if base == 0 or pers == 0 then return nil end
    for off = 0, STORAGE_SCAN_BYTES - 4 do
        if emu:read32(base + off) == pers then return off end
    end
    return nil
end
local function inParty(pers)
    for i = 0, 5 do if emu:read32(PARTY + i * MON_SIZE) == pers then return i end end
    return nil
end

H.onFrame(function(f)
    if f ~= 15 then return end
    if CM_ON then
        H.flagSet(FLAG_CM)
        H.varSet(VAR_CM_CHAR, CM_CHAR)
    else
        local a = H.flagAddr(FLAG_CM)
        emu:write8(a, emu:read8(a) & ~(1 << (FLAG_CM % 8)))
    end
end)

local pssAt, p0, p1, installed, shimHits, done = nil, nil, nil, nil, 0, false
H.breakpoint("pss", PSS, function(fr)
    if pssAt == nil then pssAt = fr end
end)
if SHIM ~= 0 then
    H.breakpoint("shim", SHIM, function() shimHits = shimHits + 1 end)
end
H.breakpoint("expand_return", EXPAND_RETURN, function(fr)
    if done or not installed then return end
    done = true
    emu:screenshot(PREFIX .. "_after.png")
    H.log(("RESULT ender=%s f=%d shimHits=%d party=%d p0 party=%s pc=%s  p1 party=%s pc=%s  str=%d,%d,%d,%d"):format(
        ENDER, fr, shimHits, emu:read8(PARTY_COUNT),
        tostring(inParty(p0)), tostring(inStorage(p0)),
        tostring(inParty(p1)), tostring(inStorage(p1)),
        emu:read8(gStringVar4), emu:read8(gStringVar4 + 1),
        emu:read8(gStringVar4 + 2), emu:read8(gStringVar4 + 3)))
    H.assertTrue("state 0 of the trade ender reached its expand BL", true)
    H.assertTrue("gStringVar4 was still expanded (\"Comm\")",
        emu:read8(gStringVar4) == 0xBD and emu:read8(gStringVar4 + 1) == 0xE3
        and emu:read8(gStringVar4 + 2) == 0xE1 and emu:read8(gStringVar4 + 3) == 0xE1)
    if EXPECT == "box1" then
        H.assertTrue("Pikachu (on the roster) stayed in the party", inParty(p0) ~= nil)
        H.assertTrue("Poliwag (off the roster) left the party", inParty(p1) == nil)
        H.assertTrue("...and is in the PC", inStorage(p1) ~= nil)
    elseif EXPECT == "box0" then
        H.assertTrue("Poliwag (on the roster) stayed in the party", inParty(p1) ~= nil)
        H.assertTrue("Pikachu (off the roster) left the party", inParty(p0) == nil)
        H.assertTrue("...and is in the PC", inStorage(p0) ~= nil)
    else
        H.assertTrue("Pikachu stayed in the party", inParty(p0) ~= nil)
        H.assertTrue("Poliwag stayed in the party", inParty(p1) ~= nil)
        H.assertTrue("party count is still 2", emu:read8(PARTY_COUNT) == 2)
    end
    H.finish()
end)

-- The proven route to the desk (cm_pc_guard_test.lua), then B through the egg
-- and the inline hatch until the storage system opens.
H.onFrame(function(f)
    if f == 60 then H.press(K.RIGHT, 16) end
    if f == 120 then H.press(K.UP, 4) end
    if f == 160 then H.press(K.A, 6) end
end)
H.onFrame(function(f)
    if f < 200 or installed then return end
    if not pssAt then
        if (f // 22) % 2 == 0 then emu:addKey(K.B) else emu:clearKey(K.B) end
        return
    end
    emu:clearKey(K.B)
    if f < pssAt + 60 then return end
    p0 = emu:read32(PARTY)
    p1 = emu:read32(PARTY + MON_SIZE)
    H.log(("fixture f=%d party=%d p0=0x%08X p1=0x%08X cm=%s char=%d"):format(
        f, emu:read8(PARTY_COUNT), p0, p1, tostring(H.flagGet(FLAG_CM)), H.varGet(VAR_CM_CHAR)))
    H.assertTrue("fixture: party of 2, the PC open",
        emu:read8(PARTY_COUNT) == 2 and p0 ~= 0 and p1 ~= 0)
    emu:screenshot(PREFIX .. "_before.png")
    emu:write8(gMain_state, 0)
    emu:write32(gMain_callback2, CB2)
    installed = f
end)

H.onFrame(function(f)
    if f == 6000 and not done then
        H.log("timeout: pssAt=" .. tostring(pssAt) .. " installed=" .. tostring(installed))
        H.assertTrue("reached the trade ender's expand BL (timeout)", false)
        H.finish()
    end
end)
