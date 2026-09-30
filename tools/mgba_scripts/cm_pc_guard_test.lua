-- LIVE e2e for the PC second guard (CM_PSSLastMonGuard), ported 2026-09-29
-- from the Seaglass layer. Runs on the PC-exit test ROM
-- (build/lazarus_cm_pctest.gba, tools/tests/build_pc_testrom.py 60 1), whose
-- desk script already builds the fixture: giveegg Poliwag + an INLINE hatch ->
-- party [savestate mon, alive Poliwag] -> the SHIPPED storage system.
--
-- The rule (ROWE's IsRemovingLastAllowedPartyMon): the storage system must
-- refuse to DEPOSIT the last alive, non-egg, ON-ROSTER party mon. With an alive
-- hatchling beside it VANILLA ALLOWS depositing slot 0, so only the guard can
-- refuse -- and only for a character whose roster has slot 0's species but
-- not Poliwag. Choose DEPOSIT, pick slot 0, STORE, confirm.
--
-- ⭐ The swap is asserted (slot 0's personality, latched at frame 15), while
-- the PC is still open -- before the exit sweep runs.
--
-- Config: build/cm_pc_mode.lua returns {cm_on, char, expect="refused"|
-- "deposited", name}. Env: CM_PSS_ADDR, CM_GUARD_ADDR (derived by the runner).
local H = dofile("tools/mgba_scripts/harness.lua")
local cfg = dofile("build/cm_pc_mode.lua")
local K = H.KEY

local FLAG_CM     = 0x2B0
local VAR_CM_CHAR = 0x40E0
local PARTY_COUNT = 0x0201B95D
local PARTY       = 0x0201B960
local MON_SIZE    = 100
local PSS         = tonumber(os.getenv("CM_PSS_ADDR") or "0")
local GUARD       = tonumber(os.getenv("CM_GUARD_ADDR") or "0")
local STORAGE_SCAN_BYTES = 0x8600

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
local function shot(n) emu:screenshot("tools/savestates/pcguard_" .. (cfg.name or "run") .. "_" .. n .. ".png") end

local slot0
H.onFrame(function(f)
    if f ~= 15 then return end
    slot0 = emu:read32(PARTY)
    if cfg.cm_on then
        H.flagSet(FLAG_CM)
        if cfg.char then H.varSet(VAR_CM_CHAR, cfg.char) end
        H.log(("CM ON char=%d"):format(H.varGet(VAR_CM_CHAR)))
    else
        local a = H.flagAddr(FLAG_CM)
        emu:write8(a, emu:read8(a) & ~(1 << (FLAG_CM % 8)))
        H.log("CM OFF (control)")
    end
    H.log(("start party=%d slot0=0x%08X"):format(emu:read8(PARTY_COUNT), slot0))
end)

local pssAt, guardHits = nil, 0
H.breakpoint("pss", PSS, function(fr)
    if pssAt == nil then pssAt = fr; H.log(("storage system opened f=%d party=%d"):format(fr, emu:read8(PARTY_COUNT))) end
end)
if GUARD ~= 0 then
    H.breakpoint("guard", GUARD, function(fr)
        guardHits = guardHits + 1
        H.log(("CM_PSSLastMonGuard entered f=%d slot(r0)=%d lr=0x%08X"):format(
            fr, emu:readRegister("r0"), emu:readRegister("lr")))
    end)
end

-- The proven route to the desk, then B through the egg + inline hatch. The
-- B-mash STOPS for good once the storage system is open.
H.onFrame(function(f)
    if f == 60 then H.press(K.RIGHT, 16) end
    if f == 120 then H.press(K.UP, 4) end
    if f == 160 then H.press(K.A, 6) end
end)
H.onFrame(function(f)
    if f < 200 or pssAt then return end
    if (f // 22) % 2 == 0 then emu:addKey(K.B) else emu:clearKey(K.B) end
end)

-- Inside the PC: Withdraw / Deposit / ... -> DOWN, A = Deposit; A = slot 0's
-- action menu; A = STORE; A = confirm the box (or dismiss the refusal).
local STEPS = {
    {60,  nil,    "1_pc_menu"},
    {10,  K.DOWN, nil},
    {40,  K.A,    "2_deposit_mode"},
    {160, K.A,    "3_party"},
    {60,  K.A,    "4_store_menu"},
    {90,  K.A,    "5_after_store"},
    {150, nil,    "6_result"},
}
local stepI, stepAt, done = 1, nil, false
H.onFrame(function(f)
    if not pssAt or done then return end
    if stepAt == nil then emu:clearKey(K.B); stepAt = pssAt end
    local s = STEPS[stepI]
    if s == nil then
        done = true
        local box, slot = inStorage(slot0), inParty(slot0)
        H.log(("RESULT slot0 box=%s partySlot=%s guardHits=%d"):format(
            tostring(box), tostring(slot), guardHits))
        H.assertTrue("the storage system opened with a party of 2 or more", pssAt ~= nil)
        if cfg.expect == "refused" then
            H.assertTrue("the deposit reached CM_PSSLastMonGuard", guardHits > 0)
            H.assertTrue("slot 0 (the last on-roster mon) is still in the party", slot ~= nil)
            H.assertTrue("...and NOT in the PC", box == nil)
        else
            H.assertTrue("slot 0 was deposited into the PC", box ~= nil)
            H.assertTrue("...and left the party", slot == nil)
        end
        H.finish()
        return
    end
    if f >= stepAt + s[1] then
        if s[3] then shot(s[3]) end
        if s[2] then H.press(s[2], 8) end
        stepI = stepI + 1; stepAt = f
    end
end)

H.onFrame(function(f)
    if f == 6000 and not done then
        H.log("timeout: pssAt=" .. tostring(pssAt))
        H.assertTrue("reached the deposit (timeout)", false)
        H.finish()
    end
end)
