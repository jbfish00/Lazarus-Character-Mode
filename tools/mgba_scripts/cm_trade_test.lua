-- Phase 6 e2e: in-game trade gating, driven through the REAL trade script.
-- Runs on a TEST ROM variant (never shipped): build/lazarus_cm.gba with
-- the University desk's (8,8) BG event repointed to the in-game-trade
-- script at 0x082B6182, so the full native trade flow (yes/no -> party
-- select -> species match -> junction -> CM_TradeCheck wrapper) can be
-- exercised from cm_red_active.ss without story progression. The junction/
-- wrapper bytes are identical to what every real trade NPC runs.
--
-- That script is sIngameTrades index 2 = SEASOR (the scripts hardcode their
-- index via setvar 0x8008: junction order 2,0,1,3 vs table order): the NPC
-- gives Horsea 116 (off Red's roster -> gate must refuse) and wants a
-- Bagon 371. A synthetic Bagon (personality/otId 0 -> xor key 0, checksum
-- valid), nicknamed "BAGON", is injected into party slot 3 so the outcome
-- is readable as plaintext nickname bytes.
--
-- build/cm_trade_mode.lua: return {cm_on=true|false}
--   cm_on  (Red): junction wrapper refuses (Horsea off-roster) — party
--                 count and slot-3 nickname unchanged.
--   cm_off: control — trade completes, slot 3 becomes SEASOR the Horsea.
-- Usage: mgba-headless -t tools/savestates/cm_red_active.ss \
--          --script tools/mgba_scripts/cm_trade_test.lua <test rom>
local H = dofile("tools/mgba_scripts/harness.lua")
local cfg = dofile("build/cm_trade_mode.lua")
local DIR = "tools/savestates/"
local K = H.KEY

local FLAG_CM = 0x945
local PARTY_COUNT = 0x0201B95D
local PARTY = 0x0201B960
local MON_SIZE = 100
local BAGON = 371

local function u16sum(addr, n)
    local s = 0
    for i = 0, n - 1 do s = (s + emu:read16(addr + 2 * i)) % 0x10000 end
    return s
end

local function injectRalts()
    local mon = PARTY + 2 * MON_SIZE
    for i = 0, MON_SIZE - 1 do emu:write8(mon + i, 0) end
    -- nickname "BAGON" @ +8 (charmap upper A-Z = 0xBB..)
    local nick = { 0xBC, 0xBB, 0xC1, 0xC9, 0xC8, 0xFF }
    for i, b in ipairs(nick) do emu:write8(mon + 8 + i - 1, b) end
    emu:write8(mon + 18, 2)          -- language ENG
    emu:write8(mon + 19, 0x02)       -- hasSpecies
    emu:write8(mon + 20, 0xBB)       -- otName "A"
    emu:write8(mon + 21, 0xFF)
    emu:write16(mon + 32, BAGON)     -- Growth: species
    emu:write16(mon + 44, 1)         -- Attacks: move Pound
    emu:write8(mon + 52, 35)         -- pp
    emu:write8(mon + 41, 70)         -- friendship
    emu:write16(mon + 28, u16sum(mon + 32, 24))  -- checksum
    emu:write8(mon + 84, 10)         -- level
    emu:write16(mon + 86, 30)        -- hp
    emu:write16(mon + 88, 30)        -- maxHP
    for off = 90, 98, 2 do emu:write16(mon + off, 12) end
    emu:write8(PARTY_COUNT, 3)
    H.log("synthetic Bagon injected in slot 3")
end

local function slot3nick()
    local mon = PARTY + 2 * MON_SIZE
    local s = {}
    for i = 0, 4 do s[#s + 1] = string.format("%02X", emu:read8(mon + 8 + i)) end
    return table.concat(s, " ")
end

H.onFrame(function(f)
    if f == 15 and not cfg.cm_on then
        local sb1 = emu:read32(H.gSaveBlock1Ptr)
        local b = sb1 + H.SB1_FLAGS_OFF + (FLAG_CM >> 3)
        emu:write8(b, emu:read8(b) & ~(1 << (FLAG_CM % 8)))
        H.log("control: flag 0x945 cleared")
    end
    if f == 20 then injectRalts() end
    -- walk (7,9)->(8,9), face the (8,8) desk tile, talk. Cadence probed:
    -- 4 intro pages -> YES/NO -> party menu -> select slot 3 -> confirm
    if f == 60 then H.press(K.RIGHT, 16) end
    if f == 120 then H.press(K.UP, 4) end
    for _, t in ipairs({160, 260, 360, 460}) do   -- talk + 3 page advances
        if f == t then H.press(K.A, 6) end
    end
    if f == 560 then H.press(K.A, 6) end          -- YES
    if f == 700 then emu:screenshot(DIR .. "trade_party.png") end
    -- party menu is a 2-column grid: slot 3 is directly below slot 1
    if f == 760 then H.press(K.DOWN, 6) end
    if f == 840 then H.press(K.A, 6) end          -- select the Bagon
    if f == 1000 then emu:screenshot(DIR .. "trade_confirm.png") end
end)
-- confirm dialog(s) + (control run) the whole trade cutscene
H.mash(K.A, 1060, 4200, 40)

H.onFrame(function(f)
    if f == 4400 then emu:screenshot(DIR .. "trade_done.png") end
    if f == 4500 then
        local n = slot3nick()
        H.log(string.format("end: party=%d slot3nick=%s flag=%s",
            emu:read8(PARTY_COUNT), n, tostring(H.flagGet(FLAG_CM))))
        if cfg.cm_on then
            H.assertEq("party count unchanged", emu:read8(PARTY_COUNT), 3)
            H.assertEq("slot 3 still BAGON (trade refused)",
                n, "BC BB C1 C9 C8")
        else
            H.assertEq("party count unchanged", emu:read8(PARTY_COUNT), 3)
            H.assertEq("slot 3 became SEASOR the Horsea (trade done)",
                n:sub(1, 11), "CD BF BB CD")
        end
        H.finish()
    end
end)
