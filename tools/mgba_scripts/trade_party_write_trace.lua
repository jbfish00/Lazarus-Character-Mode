-- PROBE (not a suite layer): drive an in-game trade all the way through the
-- cutscene and observe WHAT WRITES gPlayerParty. Port of Seaglass's probe of
-- the same name (2026-09-19), which found its trade's writer in one run.
--
-- ⭐ WHY. tools/tests/check_party_writes.py's 2026-09-28 primitive fixes
-- (high registers, WINDOW 96, k*MON_SIZE) found three new copy sites here. One,
-- 0x08224D26, decodes as pokeemerald's TradeMons(playerIdx, partnerIdx): it
-- swaps gPlayerParty[a] and gEnemyParty[b] through a temp buffer. That identity
-- came from reading the disassembly and from Seaglass's twin. This probe checks
-- it by watching the write happen.
--
-- ⚠️ CM IS OFF HERE, and that is forced, not chosen. The only in-game trade
-- whose species exists in this dex is sIngameTrades index 2 (receives Horsea
-- 116), and NO offered character has Horsea on its roster, so with CM on the
-- gate always refuses it. The copy code is identical either way: CM_TradeCheck
-- decides in the script before special 0x100/0x101, and nothing gates the copy
-- itself. So the allowed path is only reachable with CM off.
--
-- Method: cm_trade_test.lua's control route (test ROM from run_trade_e2e.sh,
-- desk (8,8) -> trade script 0x082B6182; synthetic Bagon in slot index 2). A
-- breakpoint on TradeMons entry logs the caller (lr) and the two indices, then
-- arms a WRITE_CHANGE watchpoint on slot 2's PID word, so the watchpoint only
-- single-steps the few instructions that matter. The watchpoint reports the
-- writing PC/LR.
--
-- Usage (needs MGBA_HEADLESS_DEBUGGER=1 for the breakpoint):
--   sh tools/tests/run_trade_e2e.sh      # builds build/lazarus_cm_tradetest.gba
--   MGBA_HEADLESS_DEBUGGER=1 timeout 300 \
--     tools/mgba_src/build/mgba-headless \
--     -t tools/savestates/cm_red_active.ss \
--     --script tools/mgba_scripts/trade_party_write_trace.lua \
--     build/lazarus_cm_tradetest.gba
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

local FLAG_CM     = 0x2B0
local PARTY       = H.gPlayerParty
local PARTY_COUNT = H.gPlayerPartyCount
local MON_SIZE    = H.PARTY_STRIDE
local SLOT        = 2                     -- the injected "BAGON" (party slot 3)
local TRADE_MONS  = 0x08224D18            -- TradeMons(playerIdx, partnerIdx)
local BAGON       = 371

local function u16sum(addr, n)
    local s = 0
    for i = 0, n - 1 do s = (s + emu:read16(addr + 2 * i)) % 0x10000 end
    return s
end

-- Same synthetic mon as cm_trade_test.lua (xor key 0, valid checksum).
local function injectAt(slot, nick)
    local mon = PARTY + slot * MON_SIZE
    for i = 0, MON_SIZE - 1 do emu:write8(mon + i, 0) end
    for i, b in ipairs(nick) do emu:write8(mon + 8 + i - 1, b) end
    emu:write8(mon + 18, 2)
    emu:write8(mon + 19, 0x02)
    emu:write8(mon + 20, 0xBB)
    emu:write8(mon + 21, 0xFF)
    emu:write16(mon + 32, BAGON)
    emu:write16(mon + 44, 1)
    emu:write8(mon + 52, 35)
    emu:write8(mon + 41, 70)
    emu:write16(mon + 28, u16sum(mon + 32, 24))
    emu:write8(mon + 84, 10)
    emu:write16(mon + 86, 30)
    emu:write16(mon + 88, 30)
    for off = 90, 98, 2 do emu:write16(mon + off, 12) end
end

local function nick(slot)
    local mon = PARTY + slot * MON_SIZE
    local s = {}
    for i = 0, 4 do s[#s + 1] = string.format("%02X", emu:read8(mon + 8 + i)) end
    return table.concat(s, " ")
end

local countBefore, tmCalls, tmLr, tmR0, tmR1 = nil, 0, nil, nil, nil
local wpArmed, wpHits, writers = false, 0, {}

H.breakpoint("TradeMons", TRADE_MONS, function()
    tmCalls = tmCalls + 1
    tmLr = emu:readRegister("lr")
    tmR0, tmR1 = emu:readRegister("r0"), emu:readRegister("r1")
    H.log(("TradeMons call #%d lr=0x%08X playerIdx=%d partnerIdx=%d")
        :format(tmCalls, tmLr, tmR0, tmR1))
    if not wpArmed then
        wpArmed = true
        emu:setWatchpoint(function()
            wpHits = wpHits + 1
            local pc, lr = emu:readRegister("pc"), emu:readRegister("lr")
            local key = string.format("%08X/%08X", pc, lr)
            if not writers[key] then
                writers[key] = true
                H.log(("WP slot%d pc=0x%08X lr=0x%08X r0=0x%08X r1=0x%08X r2=0x%08X")
                    :format(SLOT, pc, lr, emu:readRegister("r0"),
                            emu:readRegister("r1"), emu:readRegister("r2")))
            end
        end, PARTY + SLOT * MON_SIZE, 5)
        H.log("watchpoint armed on slot " .. SLOT .. "'s PID")
    end
end)

H.onFrame(function(f)
    if f == 15 then
        local sb1 = emu:read32(H.gSaveBlock1Ptr)
        local b = sb1 + H.SB1_FLAGS_OFF + (FLAG_CM >> 3)
        emu:write8(b, emu:read8(b) & ~(1 << (FLAG_CM % 8)))
        H.log("CM off (flag 0x2B0 cleared): the only way to reach the allowed copy")
    end
    if f == 20 then
        injectAt(1, { 0xBB, 0xC6, 0xC6, 0xBF, 0xC8, 0xFF })   -- "ALLEN"
        injectAt(2, { 0xBC, 0xBB, 0xC1, 0xC9, 0xC8, 0xFF })   -- "BAGON"
        emu:write8(PARTY_COUNT, 3)
        countBefore = 3
        H.log("before: slot2 nick=" .. nick(SLOT))
    end
    if f == 60 then H.press(K.RIGHT, 16) end
    if f == 120 then H.press(K.UP, 4) end
    for _, t in ipairs({160, 260, 360, 460}) do
        if f == t then H.press(K.A, 6) end
    end
    if f == 560 then H.press(K.A, 6) end
    if f == 760 then H.press(K.DOWN, 6) end
    if f == 840 then H.press(K.A, 6) end
end)
H.mash(K.A, 1060, 4200, 40)

H.onFrame(function(f)
    if f ~= 4500 then return end
    local n = nick(SLOT)
    local nw = 0
    for _ in pairs(writers) do nw = nw + 1 end
    H.log(("end: party=%d slot2 nick=%s TradeMons calls=%d wpHits=%d writers=%d")
        :format(emu:read8(PARTY_COUNT), n, tmCalls, wpHits, nw))
    H.assertEq("slot 3 became SEASOR the Horsea (trade done)", n:sub(1, 11), "CD BF BB CD")
    H.assertEq("gPlayerPartyCount is unchanged by the trade",
               emu:read8(PARTY_COUNT), countBefore)
    H.assertEq("TradeMons ran exactly once", tmCalls, 1)
    H.assertTrue("TradeMons was called from an IN-GAME trade caller "
                 .. "(0x0822558E or 0x08226ADA), not the link caller 0x0822733A",
                 tmLr == 0x08225593 or tmLr == 0x08226ADF)
    H.assertEq("playerIdx is the chosen slot", tmR0, SLOT)
    H.assertEq("partnerIdx is 0", tmR1, 0)
    H.assertTrue("the slot's PID was written while armed", wpHits > 0)
    H.finish()
end)
