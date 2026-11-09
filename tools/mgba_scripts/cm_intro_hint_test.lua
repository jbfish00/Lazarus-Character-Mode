-- Live layer: the wild-intro roster hint (QoL B9, 2026-11-08; src/character_mode.c
-- CM_BattleStringGated). Also the FIRST live check that the 2026-08 "destined for" marker reaches a
-- real battle in this ROM (RR's never did: its battles used a different intro path).
--
-- From del_end.ss (free roam, 6,33 town) the player walks wild_hunt.lua's route into grass until a wild encounter fires. At the
-- wild trampoline the rolled species is forced to FORCE_SPECIES with Character Mode still OFF, so
-- neither the 10% roster override nor the 1% legendary roll can replace it. CM is switched on as
-- CM_CHAR (CM_ON=1) at the marker trampoline, i.e. just before the shim reads it for the first
-- battle string. The layer records the src that BattleStringExpandPlaceholders (0x08088928) is
-- entered with, and decodes its dst (gDisplayedStringBattle) once the intro is written:
--   EXPECT=marker    -> "destined for <NAME>"
--   EXPECT=offroster -> "It is not on your roster."
--   EXPECT=vanilla   -> neither line (CM off, or the CM_NO_OFFROSTER control ROM)
-- Env: CM_ON 1/0, CM_CHAR, FORCE_SPECIES, EXPECT, CM_EXPECT_CHECKS, CM_SHOT (png path).
local H = dofile("tools/mgba_scripts/harness.lua")
local FLAG_CM, VAR_CM_CHAR = 0x2B0, 0x40E0
local CM_ON = os.getenv("CM_ON") == "1"
local CHAR = tonumber(os.getenv("CM_CHAR") or "1")
local FORCE = tonumber(os.getenv("FORCE_SPECIES") or "1")
local EXPECT = os.getenv("EXPECT") or "offroster"
local SHOT = os.getenv("CM_SHOT")
local WILD_TRAMP, MARKER_TRAMP, EXPAND = 0x081DD624, 0x081DD62C, 0x08088928
local INTROS = {[0x08575304] = true, [0x08575318] = true}
local MARKER_LO, MARKER_HI = 0x09650000, 0x09654000
local forced, armed, introR0, introDst, introAt, done = false, false, nil, nil, nil, false

emu:setBreakpoint(function()
    if forced then return end
    forced = true
    emu:writeRegister("r0", FORCE)
    H.log(string.format("wild trampoline: species forced to %d (CM off at the roll)", FORCE))
end, WILD_TRAMP)

emu:setBreakpoint(function()
    if not forced or armed then return end
    armed = true
    if CM_ON then
        H.flagSet(FLAG_CM); H.varSet(VAR_CM_CHAR, CHAR)
        H.log("CM on as char " .. CHAR .. " before the first battle string")
    end
end, MARKER_TRAMP)

emu:setBreakpoint(function()
    if introR0 or not forced then return end
    local r0 = emu:readRegister("r0")
    if INTROS[r0] or (r0 >= MARKER_LO and r0 < MARKER_HI) then
        introR0 = r0; introDst = emu:readRegister("r1"); introAt = H.frame()
    end
end, EXPAND)

local function decode(addr, n)
    local out = {}
    for i = 0, n - 1 do
        local b = emu:read8(addr + i)
        if b == 0xFF then break
        elseif b >= 0xBB and b <= 0xD4 then out[#out + 1] = string.char(65 + b - 0xBB)
        elseif b >= 0xD5 and b <= 0xEE then out[#out + 1] = string.char(97 + b - 0xD5)
        elseif b == 0x00 then out[#out + 1] = " "
        elseif b == 0xAB then out[#out + 1] = "!"
        elseif b == 0xAD then out[#out + 1] = "."
        elseif b == 0xB8 then out[#out + 1] = ","
        elseif b == 0xFE then out[#out + 1] = "/"
        else out[#out + 1] = string.format("{%02X}", b) end
    end
    return table.concat(out)
end

local K = H.KEY
H.onFrame(function(f)
    if f == 10 then
        H.flagClear = H.flagClear or function(id)
            local a = H.flagAddr(id); emu:write8(a, emu:read8(a) & (0xFF ~ (1 << (id % 8))))
        end
        H.flagClear(FLAG_CM)
        local seq = {}
        local function add(k, n) for _ = 1, n do seq[#seq + 1] = k end end
        -- wild_hunt.lua's route from del_end.ss (6,33 town): southwest into the flowery grass.
        add(K.DOWN, 3); add(K.LEFT, 4); add(K.DOWN, 2); add(K.LEFT, 6); add(K.DOWN, 3)
        for _ = 1, 40 do add(K.DOWN, 2); add(K.UP, 2); add(K.LEFT, 1); add(K.DOWN, 2); add(K.UP, 2); add(K.RIGHT, 1) end
        for _, k in ipairs(seq) do H.press(k, 16, 8) end
    end
    if done then return end
    if introAt and SHOT and f == introAt + 90 then emu:screenshot(SHOT) end
    if (introAt and f == introAt + 100) or f == 12000 then
        done = true
        local text = introDst and decode(introDst, 80) or ""
        H.log(string.format("intro r0=%s text=[%s]", introR0 and string.format("%08X", introR0) or "nil", text))
        H.assertTrue("a wild encounter fired and the intro was expanded", forced and introR0 ~= nil)
        local destined = text:find("destined for", 1, true) ~= nil
        local off = text:find("It is not on your roster.", 1, true) ~= nil
        if EXPECT == "marker" then H.assertTrue("the intro names the character", destined and not off)
        elseif EXPECT == "offroster" then H.assertTrue("the intro says 'It is not on your roster.'", off and not destined)
        else H.assertTrue("the vanilla intro (no roster line)", introR0 ~= nil and not off and not destined) end
        H.finish()
    end
end)
