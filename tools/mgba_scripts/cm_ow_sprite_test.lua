-- Live test: the player's overworld sprite follows the character (2026-10-22).
--
-- From naming.ss (the code-entry screen open at the Acrisia University desk),
-- type CM_CODE the way cm_cheat_ui_test.lua does, mash through the shipped
-- activation script, then read the player straight out of OBJ VRAM and palette
-- RAM against the expected art (tools/tests/ow_sprite_env.py writes it from the
-- SOURCE sheet, or for a native costume from the BASE ROM, never from the build).
--
--   CM_EXPECT=on   after the script: VRAM shows one of the character's frames
--                  and the palette is theirs; then walking in all four
--                  directions every sample is that direction's frame and each
--                  direction draws a step frame of its own.
--   CM_EXPECT=off  the code is refused: the player is not the character.
--
-- Env: CM_CODE (lowercase), CM_EXPECT, CM_OW_EXPECT, CM_OW_FRAME_BYTES,
--      CM_SHOTS (screenshot prefix), CM_OW_NATIVE_IMAGES (a native costume:
--      its images table is asserted instead of VRAM bytes).
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local FLAG_CM, VAR_CHAR = 0x2B0, 0x40E0
local code = os.getenv("CM_CODE") or "misty"
local expectMode = os.getenv("CM_EXPECT") or "on"
local FB = tonumber(os.getenv("CM_OW_FRAME_BYTES") or "256")
local SHOTS = os.getenv("CM_SHOTS") or "/tmp/lz_ow"
local NATIVE_IMAGES = tonumber(os.getenv("CM_OW_NATIVE_IMAGES") or "")

local fh = assert(io.open(os.getenv("CM_OW_EXPECT"), "rb"))
local blob = fh:read("a"); fh:close()
local FRAMES, PAL = {}, {}
for i = 0, 17 do FRAMES[i] = blob:sub(i * FB + 1, (i + 1) * FB) end
for k = 0, 15 do PAL[k] = string.unpack("<I2", blob, 18 * FB + 2 * k + 1) end

-- pokeemerald's player layout: walk stands 0-2, walk steps 3-8 (south, north,
-- west; east is west flipped).
local WALK = { DOWN = { 0, 3, 4 }, UP = { 1, 5, 6 }, LEFT = { 2, 7, 8 }, RIGHT = { 2, 7, 8 } }
local RUN = { DOWN = { 9, 12, 13 }, UP = { 10, 14, 15 }, LEFT = { 11, 16, 17 }, RIGHT = { 11, 16, 17 } }

local G_OBJECT_EVENTS, OBJ_STRIDE = 0x0200566C, 0x24
local GSPRITES, SPRITE_SIZE = 0x0203B5CC, 0x44
-- The player's object by its active + isPlayer bits (flags word bits 0 and 16),
-- its sprite id at +0x23 (the same expansion layout Seaglass measured).
local function playerSprite()
    for i = 0, 15 do
        local o = G_OBJECT_EVENTS + i * OBJ_STRIDE
        if (emu:read32(o) & 0x10001) == 0x10001 then return GSPRITES + emu:read8(o + 0x23) * SPRITE_SIZE end
    end
    return nil
end
local function vramFrames()
    local b = playerSprite()
    if not b then return nil end
    local at = 0x06010000 + (emu:read16(b + 4) & 0x3FF) * 32
    local t = {}
    for k = 0, FB - 1, 4 do t[#t + 1] = string.pack("<I4", emu:read32(at + k)) end
    local cur, hit = table.concat(t), {}
    for i = 0, 17 do if FRAMES[i] == cur then hit[#hit + 1] = i end end
    return #hit > 0 and hit or nil
end
local function paletteOk()
    local b = playerSprite()
    if not b then return false end
    local pal = (emu:read16(b + 4) >> 12) & 15
    for k = 1, 15 do
        if emu:read16(0x05000200 + pal * 32 + 2 * k) ~= PAL[k] then return false end
    end
    return true
end
local function contains(t, v) for _, x in ipairs(t) do if x == v then return true end end return false end

-- ---- type the code (cm_cheat_ui_test.lua's lowercase grid and timing) ----
local ROWS = { "abcdef,", "ghijkl.", "mnopqrs", "tuvwxyz" }
local function findKey(ch)
    for r, row in ipairs(ROWS) do
        local c = row:find(ch, 1, true)
        if c then return r - 1, c - 1 end
    end
    error("char not on lowercase page: " .. ch)
end
local steps = {}
local function add(key, wait) steps[#steps + 1] = { key, wait or 16 } end
for _ = 1, 10 do add(K.B) end
local cr, cc = 0, 0
for i = 1, #code do
    local r, c = findKey(code:sub(i, i))
    while cr < r do add(K.DOWN) cr = cr + 1 end
    while cr > r do add(K.UP) cr = cr - 1 end
    while cc < c do add(K.RIGHT) cc = cc + 1 end
    while cc > c do add(K.LEFT) cc = cc - 1 end
    add(K.A)
end
add(K.START, 24)
add(K.A)
local at = 30
for _, st in ipairs(steps) do
    local key, when = st[1], at
    H.onFrame(function(f) if f == when then H.press(key, 6) end end)
    at = at + st[2]
end
local tEnd = at
-- The A mash ends on the starter's nickname screen: START + A leaves it, then B
-- (A at the desk would reopen it).
H.mash(K.A, tEnd + 60, tEnd + 1400, 40)
H.onFrame(function(f)
    if f == tEnd + 1450 then H.press(K.START, 6) end
    if f == tEnd + 1490 then H.press(K.A, 6) end
end)
H.mash(K.B, tEnd + 1530, tEnd + 2300, 40)

-- ---- after the script: the look, then a walk in each direction ----
local walk = { { "DOWN", 40 }, { "RIGHT", 40 }, { "UP", 40 }, { "LEFT", 40 } }
local CHECK_AT, GAP, TURN = tEnd + 2400, 30, 3
local got, bad, si, t0, runSeen = {}, {}, 1, nil, false

H.onFrame(function(f)
    if f == CHECK_AT then
        local hit = vramFrames()
        emu:screenshot(SHOTS .. "_stand.png")
        H.log(("after the script: flag=%s char=%d frame=%s"):format(tostring(H.flagGet(FLAG_CM)),
              H.varGet(VAR_CHAR), hit and table.concat(hit, "+") or "none"))
        H.assertTrue("the player's object was found", playerSprite() ~= nil)
        if expectMode == "off" then
            H.assertTrue("mode stays off", not H.flagGet(FLAG_CM))
            H.assertTrue("the player is not drawn with the character's art", hit == nil)
            H.finish()
            return
        end
        H.assertTrue("mode on", H.flagGet(FLAG_CM))
        if NATIVE_IMAGES then
            H.assertEq("the sprite uses the native costume's images table",
                       emu:read32(playerSprite() + 12), NATIVE_IMAGES)
            H.finish()
            return
        end
        H.assertTrue("right after activation VRAM holds one of the character's frames", hit ~= nil)
        H.assertTrue("and the palette is the character's", paletteOk())
        t0 = f + 1
    elseif t0 and si <= #walk and f >= t0 then
        local dir, hold = walk[si][1], walk[si][2]
        local dt = f - t0
        if dt == 0 then
            emu:addKey(K[dir])
        elseif dt <= hold then
            if dt > TURN then
                local hit = vramFrames()
                local ok = hit and (contains(hit, WALK[dir][1]) or contains(hit, WALK[dir][2])
                                    or contains(hit, WALK[dir][3]) or contains(hit, RUN[dir][1]))
                if not ok then bad[#bad + 1] = ("%s:%s"):format(dir, hit and table.concat(hit, "+") or "x") end
                if hit then
                    for _, v in ipairs(hit) do
                        if v == WALK[dir][2] or v == WALK[dir][3] then got[dir] = true end
                    end
                end
            end
            if dt == hold // 2 then emu:screenshot(("%s_%d_%s.png"):format(SHOTS, si, dir)) end
        elseif dt == hold + 1 then
            emu:clearKey(K[dir])
        elseif dt >= hold + GAP then
            si, t0 = si + 1, f + 1
            if si > #walk then
                H.assertTrue("every sample shows its own direction's frame (stray: "
                             .. (#bad == 0 and "none" or table.concat(bad, " ")) .. ")", #bad == 0)
                for _, d in ipairs({ "DOWN", "RIGHT", "UP", "LEFT" }) do
                    H.assertTrue(("walk %s: a step frame was drawn"):format(d), got[d])
                end
                H.finish()
            end
        end
    end
end)
