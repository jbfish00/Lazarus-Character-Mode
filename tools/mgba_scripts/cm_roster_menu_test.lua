-- Live test of the in-game roster display in LAZARUS (2026-09-27).
-- Ported from the Seaglass port's tools/mgba_scripts/cm_roster_menu_test.lua;
-- the assertions transfer, every address was re-derived from this binary.
--
-- Starts from cm_red_active.ss (player AT the University desk, CM on) and
-- presses A on the desk. CM state is then preset in RAM (flag 0x2B0 +
-- VAR_CM_CHAR 0x40E0), so the character is a discriminating one, not #1.
--
--   MODE=roster  the pre-entry menu opens; row 0 "View roster" pushes the
--                character's family roots and opens the list with callback
--                set 2. Asserts the EXACT species pushed (CM_EXPECT_ROOTS, from
--                characters_manifest.json via roster_menu_env.py, never from the
--                blob), the first icon, the SECOND row's icon after one DOWN
--                (selectedItem is the species: "ID, not index"), and that B
--                tears everything down.
--   MODE=code    row 1 "Enter a code" reaches the desk's own naming special
--                (0x221), skipping its yes/no; no rows are pushed.
--   MODE=off     CM off: the desk runs its stock script. Answering its own
--                yes/no must reach the naming special 0x221 -- positive proof
--                the desk was used (a missed A would also show "no menu") --
--                with no dynmultichoice at all and no rows pushed.
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

local MODE = os.getenv("MODE") or "roster"
local CM_CHAR = tonumber(os.getenv("CM_CHAR") or "10")
local function envaddr(n)
    local v = os.getenv(n)
    if not v then error("missing env " .. n) end
    return tonumber(v)
end
local ON_INIT = envaddr("CM_ROSTER_ONINIT") & ~1
local ON_SEL = envaddr("CM_ROSTER_ONSEL") & ~1
local ON_DESTROY = envaddr("CM_ROSTER_ONDESTROY") & ~1
local EXPECT = {}
for s in (os.getenv("CM_EXPECT_ROOTS") or ""):gmatch("%d+") do EXPECT[#EXPECT + 1] = tonumber(s) end

local VAR_RESULT = 0x0200560C
local FLAG_CM, VAR_CM_CHAR = 0x2B0, 0x40E0
local DYNMULTI_HANDLER = 0x08209AE8           -- ScrCmd_dynmultichoice
local PUSH_ELEMENT = 0x0820B93C               -- MultichoiceDynamic_PushElement
local CURSOR_MOVE = 0x0820BA64                -- list cursor move, before the NONE test
local NAMING_SPECIAL = 0x0813F848             -- gSpecials[0x221], the desk's code screen
local gSpeciesInfo, STRIDE, ICON_OFF = 0x08C7A338, 212, 120
local gSprites, SPRITE_SIZE = 0x0203B5CC, 68

local pushed, selSeen, dynCalls = {}, {}, 0
local hits = { init = 0, sel = 0, destroy = 0, naming = 0, move = 0 }
emu:setBreakpoint(function() pushed[#pushed + 1] = emu:readRegister("r1") end, PUSH_ELEMENT)
emu:setBreakpoint(function() dynCalls = dynCalls + 1 end, DYNMULTI_HANDLER)
emu:setBreakpoint(function() hits.init = hits.init + 1 end, ON_INIT)
emu:setBreakpoint(function()
    hits.sel = hits.sel + 1
    selSeen[#selSeen + 1] = emu:read16(emu:readRegister("r0") + 4)   -- args->selectedItem
end, ON_SEL)
emu:setBreakpoint(function() hits.destroy = hits.destroy + 1 end, ON_DESTROY)
emu:setBreakpoint(function() hits.naming = hits.naming + 1 end, NAMING_SPECIAL)
emu:setBreakpoint(function() hits.move = hits.move + 1 end, CURSOR_MOVE)

local function iconSpriteFor(s)
    local img = emu:read32(gSpeciesInfo + s * STRIDE + ICON_OFF)
    for i = 0, 63 do
        local b = gSprites + i * SPRITE_SIZE
        if (emu:read8(b + 62) & 1) == 1 and emu:read32(b + 12) == img then return b end
    end
end
local function anyRosterIcon()
    for _, s in ipairs(EXPECT) do if iconSpriteFor(s) then return true end end
    return false
end

local phase, nextAt = "prep", 5
local t, firstIcon, secondIcon, secondPrio = {}, nil, nil, nil
local moveBase, selBase = 0, 0
H.onFrame(function(f)
    if dynCalls > 0 and t.menu == nil then t.menu = f; phase = "menu_shot"; nextAt = f + 40 end
    if f < nextAt then return end
    if phase == "prep" then
        local a = H.flagAddr(FLAG_CM)
        if MODE == "off" then emu:write8(a, emu:read8(a) & ~(1 << (FLAG_CM % 8)))
        else H.flagSet(FLAG_CM); H.varSet(VAR_CM_CHAR, CM_CHAR) end
        emu:write16(VAR_RESULT, 0x1234)
        phase = "talk"; nextAt = 30
    elseif phase == "talk" then
        H.press(K.A, 6); t.talked = f; phase = "wait"; nextAt = f + 1
    elseif phase == "wait" then
        if MODE == "off" then
            if f == t.talked + 150 then emu:screenshot("tools/savestates/roster_off_prompt.png") end
            if hits.naming > 0 then phase = "done"
            elseif f > t.talked + 1500 then phase = "done"
            elseif f > t.talked + 150 and (f - t.talked) % 40 == 0 then H.press(K.A, 6) end
        elseif f > 1500 then phase = "done" end
        if phase == "wait" then nextAt = f + 1 end
    elseif phase == "menu_shot" then
        emu:screenshot(("tools/savestates/roster_%s_menu.png"):format(MODE))
        moveBase = hits.move
        phase = (MODE == "code") and "to_code" or "pick"; nextAt = f + 1
    elseif phase == "to_code" then
        if hits.move > moveBase then phase = "pick"; nextAt = f + 20
        elseif f - t.menu > 600 then phase = "done"
        else H.press(K.DOWN, 8, 8); nextAt = f + 20 end
    elseif phase == "pick" then
        H.press(K.A, 6); t.picked = f
        phase = (MODE == "code") and "code_wait" or "list_wait"; nextAt = f + 1
    elseif phase == "code_wait" then
        -- "Please enter the code." needs an A before the special runs
        if hits.naming > 0 then phase = "code_shot"; nextAt = f + 60
        elseif f - t.picked > 900 then phase = "done"
        else
            if (f - t.picked) % 40 == 20 then H.press(K.A, 6) end
            nextAt = f + 1
        end
    elseif phase == "code_shot" then
        emu:screenshot("tools/savestates/roster_code_naming.png"); phase = "done"
    elseif phase == "list_wait" then
        if hits.init > 0 and hits.sel > 0 then t.list = f; phase = "list_shot"; nextAt = f + 40
        elseif f - t.picked > 600 then phase = "done" else nextAt = f + 1 end
    elseif phase == "list_shot" then
        firstIcon = iconSpriteFor(EXPECT[1] or 0) ~= nil
        emu:screenshot(("tools/savestates/roster_list_c%d_row0.png"):format(CM_CHAR))
        selBase = hits.sel
        phase = "down"; nextAt = f + 1
    elseif phase == "down" then
        if hits.sel > selBase then phase = "down_shot"; nextAt = f + 40
        elseif f - t.list > 600 then phase = "close"
        else H.press(K.DOWN, 8, 8); nextAt = f + 20 end
    elseif phase == "down_shot" then
        local b = iconSpriteFor(EXPECT[2] or 0)
        secondIcon = b ~= nil
        secondPrio = b and ((emu:read8(b + 5) >> 2) & 3)
        emu:screenshot(("tools/savestates/roster_list_c%d_row1.png"):format(CM_CHAR))
        phase = "close"; nextAt = f + 1
    elseif phase == "close" then
        if hits.destroy > 0 then phase = "settle"; nextAt = f + 60
        elseif f - t.list > 1500 then phase = "done"
        else H.press(K.B, 8, 8); nextAt = f + 20 end
    elseif phase == "settle" then
        emu:screenshot(("tools/savestates/roster_closed_c%d.png"):format(CM_CHAR))
        phase = "done"
    end
    if phase == "done" then
        phase = "finished"
        local p, s = {}, {}
        for _, v in ipairs(pushed) do p[#p + 1] = tostring(v) end
        for _, v in ipairs(selSeen) do s[#s + 1] = tostring(v) end
        H.log(("mode=%s char=%d dynmultichoice=%d pushed=[%s] sel=[%s] init=%d destroy=%d naming=%d")
            :format(MODE, CM_CHAR, dynCalls, table.concat(p, ","), table.concat(s, ","),
                    hits.init, hits.destroy, hits.naming))
        if MODE == "roster" then
            H.assertEq("rows pushed == the character's family roots, in order",
                table.concat(p, ","), table.concat(EXPECT, ","))
            H.assertTrue("set 2 OnInit ran once", hits.init == 1)
            H.assertEq("first OnSelectionChanged got the first root's SPECIES", selSeen[1], EXPECT[1])
            H.assertTrue("the first root's icon was drawn from gSpeciesInfo+120", firstIcon == true)
            H.assertEq("after one DOWN, OnSelectionChanged got the SECOND root's species",
                selSeen[#selSeen], EXPECT[2])
            H.assertTrue("the second root's icon replaced it", secondIcon == true)
            H.assertEq("the icon is above the window layer (oam priority)", secondPrio, 0)
            H.assertTrue("B closed the list: set 2 OnDestroy ran", hits.destroy == 1)
            H.assertTrue("no roster icon survives the close", not anyRosterIcon())
            H.assertEq("VAR_RESULT is B (127)", emu:read16(VAR_RESULT), 127)
        elseif MODE == "code" then
            H.assertTrue("the pre-entry menu opened", dynCalls == 1)
            H.assertTrue("row 1 reached the desk's naming special 0x221", hits.naming == 1)
            H.assertTrue("no roster rows were pushed", #pushed == 0)
        else
            H.assertTrue("CM off: the stock desk script reached its naming special 0x221",
                hits.naming == 1)
            H.assertTrue("CM off: no dynmultichoice opened", dynCalls == 0)
            H.assertTrue("CM off: no roster rows were pushed", #pushed == 0)
        end
        H.finish()
    end
end)
