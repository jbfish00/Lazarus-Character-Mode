-- Determine whether species id == national dex number for a legendary.
--
-- docs/ROUTINE_MAP.md ("Pokedex bitmaps") establishes dexSeen = SB1+0x32A8,
-- dexCaught = SB1+0x3329, bit index = natdex-1. It also establishes that species
-- id and natdex are NOT the same in this ROM: identity holds at species 25 and
-- 187 and fails at 728 (which sits at natdex 729), so exactly one dex slot is
-- inserted somewhere in (187, 728].
--
-- The nine legendaries the 1% encounter feature needs all live in 243..384, so
-- the whole question is whether that insertion is above or below them. No
-- savestate in tools/savestates/ contains a species in 188..727, so it cannot be
-- answered from existing data -- it needs one live observation, which is this.
--
-- METHOD. Walk into the grass from del_end.ss exactly as wild_gen_trace.lua
-- does, but breakpoint CreateWildMon (0x0824AA54, docs/ROUTINE_MAP.md) and
-- overwrite r0 -- the species argument -- with the species under test. The
-- battle then starts with that species, and the game sets its dexSeen bit
-- itself, using its own conversion. Reading which bit moved gives the mapping
-- directly, with no assumption about how the conversion is implemented.
--
-- Needs MGBA_HEADLESS_DEBUGGER=1 (stock headless never creates the debugger, so
-- setBreakpoint silently never fires).
--
--   CM_SPECIES=243 MGBA_HEADLESS_DEBUGGER=1 timeout 200 <mgba-headless> \
--     -t tools/savestates/del_end.ss \
--     --script tools/mgba_scripts/dex_natdex_probe.lua build/lazarus_cm.gba

local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

local SPECIES = tonumber(os.getenv("CM_SPECIES") or "243")   -- default Raikou
local DEX_SEEN_OFF = 0x32A8
local CREATE_WILD_MON = 0x0824AA54

H.log(string.format("probing species %d", SPECIES))

local function seenBit(natdex)
    local idx = natdex - 1
    local addr = emu:read32(H.gSaveBlock1Ptr) + DEX_SEEN_OFF + math.floor(idx / 8)
    return math.floor(emu:read8(addr) / 2 ^ (idx % 8)) % 2
end

local function dexSnapshot()
    local base = emu:read32(H.gSaveBlock1Ptr) + DEX_SEEN_OFF
    local t = {}
    for i = 0, 257 do t[i] = emu:read8(base + i) end
    return t
end
local function dexDiff(a, b)
    local out = {}
    local base = 0
    for i = 0, 257 do
        local x = a[i] or 0
        local y = b[i] or 0
        if x ~= y then
            for bit = 0, 7 do
                local bx = math.floor(x / 2 ^ bit) % 2
                local by = math.floor(y / 2 ^ bit) % 2
                if bx ~= by then
                    local arr = (i < 129) and "seen" or "caught"
                    local idx = (i % 129) * 8 + bit
                    out[#out+1] = string.format("%s natdex %d (%d->%d)", arr, idx + 1, bx, by)
                end
            end
        end
    end
    return out
end
local snap0

-- Snapshot the two candidate bits before anything happens: natdex == species
-- (identity) and natdex == species + 1 (shifted, the case species 728 shows).
local before = {}
H.onFrame(function(f)
    if f ~= 5 then return end
    before[SPECIES] = seenBit(SPECIES)
    before[SPECIES + 1] = seenBit(SPECIES + 1)
    snap0 = dexSnapshot()
    H.log(string.format("before: natdex %d = %d, natdex %d = %d",
                        SPECIES, before[SPECIES], SPECIES + 1, before[SPECIES + 1]))
end)

local forced = 0
local id = emu:setBreakpoint(function()
    -- r0 is the species argument. Overwrite it so the wild mon the game builds
    -- -- and registers in the dex -- is the one under test.
    if forced < 4 then
        emu:writeRegister("r0", SPECIES)
        forced = forced + 1
        H.log(string.format("CreateWildMon: forced r0 = %d (hit %d)", SPECIES, forced))
    end
end, CREATE_WILD_MON)
if not id or id < 0 then
    error("setBreakpoint failed (id=" .. tostring(id) ..
          ") -- run with MGBA_HEADLESS_DEBUGGER=1")
end

-- Same walk into the grass wild_gen_trace.lua uses, from del_end.ss.
H.onFrame(function(f)
    if f ~= 30 then return end
    local seq = {}
    local function add(k, n) for _ = 1, n do seq[#seq+1] = k end end
    add(K.DOWN, 3); add(K.LEFT, 4); add(K.DOWN, 2)
    add(K.LEFT, 6); add(K.DOWN, 3)
    for _ = 1, 40 do
        add(K.DOWN, 2); add(K.UP, 2); add(K.LEFT, 1)
        add(K.DOWN, 2); add(K.UP, 2); add(K.RIGHT, 1)
    end
    for _, k in ipairs(seq) do H.press(k, 16, 8) end
end)

-- Once the encounter exists, the walk keys do nothing. The dex "seen" bit is
-- set a little way INTO the battle, not at CreateWildMon time: wild_battle.ss
-- (early in a Hoppip battle) does NOT have Hoppip's seen bit, while
-- battle_menu.ss / battle_bag.ss (same battle, further along) do. So the intro
-- has to be advanced or nothing is ever registered.
H.onFrame(function(f)
    if forced > 0 and f % 12 == 0 then
        if (f // 12) % 2 == 0 then emu:addKey(K.A) else emu:clearKey(K.A) end
    end
end)

local done = false
H.onFrame(function(f)
    if done then return end
    if forced == 0 then
        if f > 40000 then
            done = true
            H.assertTrue("CreateWildMon was reached (no encounter triggered)", false)
            H.finish()
        end
        return
    end
    -- give the battle a moment to run its dex registration
    if f % 60 ~= 0 then return end
    local a, b = seenBit(SPECIES), seenBit(SPECIES + 1)
    if (a ~= before[SPECIES]) or (b ~= before[SPECIES + 1]) then
        done = true
        H.log(string.format("after: natdex %d = %d, natdex %d = %d", SPECIES, a, SPECIES + 1, b))
        if a == 1 and before[SPECIES] == 0 then
            H.assertTrue(string.format(
                "species %d registers at natdex %d -> IDENTITY holds here",
                SPECIES, SPECIES), true)
        elseif b == 1 and before[SPECIES + 1] == 0 then
            H.assertTrue(string.format(
                "species %d registers at natdex %d -> SHIFTED by +1 here",
                SPECIES, SPECIES + 1), true)
        else
            H.assertTrue("a dex bit moved but neither candidate explains it", false)
        end
        H.finish()
    elseif f > 60000 then
        done = true
        local d = dexDiff(snap0, dexSnapshot())
        H.log("whole-region dex diff: " .. (#d > 0 and table.concat(d, ", ") or "NOTHING CHANGED"))
        local ep = H.gEnemyParty
        H.log(string.format("gEnemyParty pid=0x%08X otid=0x%08X",
                            emu:read32(ep), emu:read32(ep + 4)))
        H.assertTrue("a dex bit moved for the forced species", false)
        H.finish()
    end
end)
