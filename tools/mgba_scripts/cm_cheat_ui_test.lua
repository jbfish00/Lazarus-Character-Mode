-- Phase 6 e2e: real cheat-entry UI flow at the Acrisia University desk.
-- From naming.ss (code-entry naming screen open, "Aaaa" pre-typed, cursor on
-- 'a'): clear with B, type the code in build/cm_ui_code.lua via cursor
-- navigation, confirm (START -> A), A-mash through the confirm script, then
-- assert the expected end state.
--
-- build/cm_ui_code.lua: return {
--   code = "red",            -- lowercase page chars only (a-z , .)
--   expect = "activate_red" | "give2",
--   open_desk = false,       -- true: start from overworld AT the desk
--                            -- (e.g. cm_red_active.ss): A + mash to reopen
--                            -- the code-entry screen first
-- }
-- Codes may end in digits (e.g. "cmdbggive2"): typed via the others page
-- (digits 0-9 on row 0; park at (0,0), SELECT needs ~60 frames of settle
-- before cursor moves register — probed empirically). Poking the code
-- buffer does NOT work: the naming screen flushes its internal buffer over
-- 0x0203CCE0 at commit.
--   activate_red: flag 0x945 on, var 0x40E0 == 1 (Red), party +1 (Pikachu 25
--                 on-roster stays in party), box0 unchanged, 0x40E4 == 0.
--   give2:        party unchanged, box0 +1 (off-roster boxed by the native
--                 wrapper), 0x40E4 == 0.
-- Usage: mgba-headless -t tools/savestates/naming.ss \
--          --script tools/mgba_scripts/cm_cheat_ui_test.lua build/lazarus_cm.gba
local H = dofile("tools/mgba_scripts/harness.lua")
local cfg = dofile("build/cm_ui_code.lua")
local DIR = "tools/savestates/"
local K = H.KEY

local FLAG_CM, VAR_CHAR, VAR_STARTER = 0x945, 0x40E0, 0x40E4
local CODE_BUF = 0x0203CCE0

-- lowercase keyboard page grid (calibrated from naming_960.png)
local ROWS = { "abcdef,", "ghijkl.", "mnopqrs", "tuvwxyz" }
local function findKey(ch)
    for r, row in ipairs(ROWS) do
        local c = row:find(ch, 1, true)
        if c then return r - 1, c - 1 end
    end
    error("char not on lowercase page: " .. ch)
end

local function storageBox0Count()
    local base = emu:read32(H.gPokemonStoragePtr)
    if base < 0x02000000 or base >= 0x02040000 then return -1 end
    local n = 0
    for slot = 0, 29 do
        if emu:read32(base + 4 + slot * 80) ~= 0 then n = n + 1 end
    end
    return n
end

-- build the key plan: 10x B (clear), nav+A per char (page-switch for
-- digits), START, A (confirm). Each step = {key, frames-until-next}.
local steps = {}
local function add(key, wait) steps[#steps + 1] = { key, wait or 16 } end
for _ = 1, 10 do add(K.B) end
local cr, cc = 0, 0
local onOthers = false
for i = 1, #cfg.code do
    local ch = cfg.code:sub(i, i)
    if ch:match("%d") then
        if not onOthers then
            -- park at (0,0), then switch page; digits land on row 0 with
            -- the cursor carried to '0'
            while cr > 0 do add(K.UP) cr = cr - 1 end
            while cc > 0 do add(K.LEFT) cc = cc - 1 end
            add(K.SELECT, 70)
            onOthers = true
        end
        local d = ch:byte() - ("0"):byte()
        while cc < d do add(K.RIGHT, 24) cc = cc + 1 end
        while cc > d do add(K.LEFT, 24) cc = cc - 1 end
        add(K.A, 24)
    else
        assert(not onOthers, "letters after digits not supported")
        local r, c = findKey(ch)
        while cr < r do add(K.DOWN) cr = cr + 1 end
        while cr > r do add(K.UP) cr = cr - 1 end
        while cc < c do add(K.RIGHT) cc = cc + 1 end
        while cc > c do add(K.LEFT) cc = cc - 1 end
        add(K.A)
    end
end
add(K.START, 24)
add(K.A)

local before = {}
-- open_desk: reopen the code-entry screen from the overworld first
-- (A on the desk at f=30, mash through the dialogue, screen up well
-- before f=1300 — desk_to_naming.lua measured ~960 from mid-dialogue)
local t0 = cfg.open_desk and 1300 or 30
if cfg.open_desk then
    H.onFrame(function(f)
        if f == 30 then H.press(K.A, 6) end
        if f == 1290 then emu:screenshot(DIR .. "ui_reopen.png") end
    end)
    H.mash(K.A, 60, 1100, 40)
end
H.onFrame(function(f)
    if f == 10 then
        before.party = emu:read8(0x0201B95D)
        before.box0 = storageBox0Count()
        H.log(string.format("before: party=%d box0=%d flag=%s char=%d",
            before.party, before.box0, tostring(H.flagGet(FLAG_CM)), H.varGet(VAR_CHAR)))
    end
end)
local at = t0
for _, st in ipairs(steps) do
    local key, when = st[1], at
    H.onFrame(function(f)
        if f == when then H.press(key, 6) end
    end)
    at = at + st[2]
end
local tEnd = at
-- A-mash through confirm-script dialogue (fanfare + "give nickname?" yes/no —
-- A-mash lands on YES and opens the nickname naming screen)
H.mash(K.A, tEnd + 60, tEnd + 1400, 40)
-- confirm the nickname screen: START jumps to OK, A commits (mon ends up
-- named "Aaaa..." — harmless), then mash A through the rest of the script
-- (setvar VAR_CM_STARTER 0 -> "Character Mode is now active!" msgbox)
H.onFrame(function(f)
    if f == tEnd + 1450 then H.press(K.START, 6) end
    if f == tEnd + 1490 then H.press(K.A, 6) end
end)
-- B, not A: dismisses any remaining msgbox but cannot re-trigger the desk
-- BG event, so the end state (and cm_red_active.ss) is a clean overworld
H.mash(K.B, tEnd + 1530, tEnd + 2300, 40)

H.onFrame(function(f)
    if f == tEnd + 20 then
        local b = {}
        for i = 0, 10 do b[#b + 1] = string.format("%02X", emu:read8(CODE_BUF + i)) end
        H.log("code buffer: " .. table.concat(b, " "))
        emu:screenshot(DIR .. "ui_typed.png")
    end
    if f == tEnd + 2400 then
        emu:screenshot(DIR .. "ui_done.png")
        local party = emu:read8(0x0201B95D)
        local box0 = storageBox0Count()
        H.log(string.format("after: party=%d box0=%d flag=%s char=%d starter=%d",
            party, box0, tostring(H.flagGet(FLAG_CM)), H.varGet(VAR_CHAR),
            H.varGet(VAR_STARTER)))
        if cfg.expect == "activate_red" then
            H.assertTrue("flag 0x945 set", H.flagGet(FLAG_CM))
            H.assertEq("VAR_CM_CHAR == Red(1)", H.varGet(VAR_CHAR), 1)
            H.assertEq("party grew (starter give)", party, before.party + 1)
            H.assertEq("box0 unchanged (on-roster)", box0, before.box0)
            H.assertEq("VAR_CM_STARTER reset", H.varGet(VAR_STARTER), 0)
            emu:saveStateFile(DIR .. "cm_red_active.ss")
            H.log("saved cm_red_active.ss")
        elseif cfg.expect == "give2" then
            H.assertEq("party unchanged (boxed)", party, before.party)
            H.assertEq("box0 +1 (wrapper boxed off-roster)", box0, before.box0 + 1)
            H.assertEq("VAR_CM_STARTER reset", H.varGet(VAR_STARTER), 0)
        end
        H.finish()
    end
end)
