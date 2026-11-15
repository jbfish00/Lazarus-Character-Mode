-- Live layer (QoL A3 instant HP bar, 2026-10-28; tools/inject_character_mode.py instant_hp).
-- From battle_menu.ss (wild Hoppip, the move list open on Pound): the lead's Attack and Sp. Atk are set to 999 and the
-- foe's speed to 1, so Pound KOs the full-HP foe first and its bar drains end to end. Every MoveBattleBar(HEALTH_BAR)
-- call (entry 0x0807D5A8, r2 == 0) is counted by frame, with the bar updates they belong to (an update starts while
-- gBattleSpritesDataPtr (0x02000864)->battleBars[b].currValue holds -32768).
--   WANT_INSTANT=1 -> at most 4 frames an update (the shipped ROM)
--   WANT_INSTANT=0 -> more than 4 (B_FAST_HP_DRAIN: maxHP/24 a frame; build/lazarus_cm_nohp.gba, the control)
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local GBATTLEMONS = 0x02000360        -- gBattleMons, stride 0x60: attack +2, speed +6, sp. atk +8, hp +0x2A
local WANT = tonumber(os.getenv("WANT_INSTANT") or "1")
local frames, updates, last, hpBefore = 0, 0, -1, nil
H.breakpoint("MoveBattleBar", 0x0807D5A8, function()
    if emu:readRegister("r2") & 0xFF ~= 0 then return end
    if H.frame() ~= last then frames = frames + 1; last = H.frame() end
    local bars = emu:read32(emu:read32(0x02000864) + 12)
    if emu:read32(bars + (emu:readRegister("r0") & 0xFF) * 20 + 16) == 0xFFFF8000 then updates = updates + 1 end
end)
-- WANT_DRAWN=1|0 (2026-11-14, user: bars low and red at battle start): the lead's Attack is 1 instead of 999, so the
-- low-level foe (max HP < 48: the fixed-point branch) stays alive and its bar is redrawn (measured: at full HP, Pound
-- does not land from this state). MoveBattleBarGraphically's
-- inlined CalcBarFilledPixels result (0x0807D80E: r5 = filled pixels; bar struct = sl + r8) is logged per battler; the
-- foe's last drawn bar must be floor(hp * 48 / max) pixels (1 if that is 0 with hp > 0). The 10-28 patch draws <= 1.
local DRAWN = os.getenv("WANT_DRAWN"); if DRAWN == "" then DRAWN = nil end
local lastPx, lastMax = {}, {}
if DRAWN then
    H.breakpoint("HpBarFilled", 0x0807D80E, function()
        local b = emu:readRegister("r10") + emu:readRegister("r8")
        local battler = emu:readRegister("r8") // 20
        lastPx[battler] = emu:readRegister("r5") & 0xFF
        lastMax[battler] = emu:read32(b + 4)
    end)
end
H.onFrame(function(f)
    if f == 5 then
        if DRAWN then emu:write16(GBATTLEMONS + 0x02, 1)                   -- lead Attack 1: Pound leaves the foe alive
        else emu:write16(GBATTLEMONS + 0x02, 999); emu:write16(GBATTLEMONS + 0x08, 999) end
        emu:write16(GBATTLEMONS + 0x60 + 0x06, 1)
        hpBefore = emu:read16(GBATTLEMONS + 0x60 + 0x2A)
    end
    if f == 30 then H.press(K.A, 6) end                        -- Pound
    if f > 200 and f < 1400 and f % 40 == 0 then H.press(K.B, 6) end
    if f == 1500 then
        H.log(("HP bar: %d frames of MoveBattleBar calls over %d updates; foe hp %d -> %d"):format(
            frames, updates, hpBefore, emu:read16(GBATTLEMONS + 0x60 + 0x2A)))
        H.assertTrue("the foe's bar drained (it started above 0 and the bar moved)", hpBefore > 0 and updates > 0)
        if DRAWN then
            local hp, mx = emu:read16(GBATTLEMONS + 0x60 + 0x2A), lastMax[1] or 0
            local want = mx > 0 and (hp * 48) // mx or -1
            if want == 0 and hp > 0 then want = 1 end
            H.log(("foe bar: hp %d / %d drawn %s px, want %d; lead hp %d drawn %s px"):format(hp, mx, tostring(lastPx[1]), want,
                emu:read16(GBATTLEMONS + 0x2A), tostring(lastPx[0])))
            H.assertTrue("the foe has max HP < 48 and is alive (its bar was redrawn)", mx > 0 and mx < 48 and hp > 0)
            if DRAWN == "1" then H.assertEq("the foe's bar is drawn at its HP", lastPx[1], want)
            else H.assertTrue("the foe's bar is drawn short (old patch)", lastPx[1] ~= nil and lastPx[1] < want) end
        end
        if DRAWN then H.finish(); return end            -- no drain in this mode: the speed layers are the other cases
        if WANT == 1 then
            H.assertTrue("instant HP bar: at most 4 frames per update", frames <= 4 * updates)
        else
            H.assertTrue("animated HP bar: more than 4 frames per update", frames > 4 * updates)
        end
        H.finish()
    end
end)
