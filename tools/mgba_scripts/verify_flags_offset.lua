-- Live verification of Phase 1d static findings (docs/ROUTINE_MAP.md):
--   FlagSet   = 0x0811478C
--   FlagClear = 0x08114844
--   flags array = *gSaveBlock1Ptr(0x03003664) + 0x12E8, byte = id/8, bit = id%8
--
-- Method: breakpoint FlagSet/FlagClear entry, record every regular-flag id
-- (< 0x4000) the intro/new-game init touches. At end of run, re-read
-- sb1+0x12E8+id/8 and check the bit matches the last recorded operation.
-- If the static offset were wrong, the observed bits would not line up.
--
-- Run (bounded — mgba-headless has no shutdown API):
--   timeout 180 ../Seaglass-Character-Mode/tools/mgba_src/build/mgba-headless \
--     --script tools/mgba_scripts/verify_flags_offset.lua rom/lazarus-v2.gba \
--     > /tmp/flagverify.log 2>&1 ; grep HARNESS /tmp/flagverify.log
local H = dofile("tools/mgba_scripts/harness.lua")

local FLAGS_OFF = 0x12E8
local FLAGSET   = 0x0811478C
local FLAGCLEAR = 0x08114844

-- mash A through title -> naming -> overworld spawn (naming accepted ~f3600)
H.mash(H.KEY.A, 300, 5400, 60)

local lastOp = {}   -- id -> true(set) / false(clear)
local hits = 0

local function record(op)
    local id = emu:readRegister("r0") % 0x10000
    if id == 0 or id >= 0x4000 then return end  -- special/EWRAM flags: out of scope
    lastOp[id] = op
    hits = hits + 1
    if hits <= 12 then
        H.log(string.format("BP %s id=0x%03X frame=%d",
            op and "FlagSet" or "FlagClear", id, H.frame()))
    end
end

emu:setBreakpoint(function() record(true) end, FLAGSET)
emu:setBreakpoint(function() record(false) end, FLAGCLEAR)

local done = false
H.onFrame(function(f)
    if f ~= 6000 or done then return end
    done = true
    local sb1 = emu:read32(H.gSaveBlock1Ptr)
    H.log(string.format("sb1=0x%08X, %d flag ops observed", sb1, hits))
    if sb1 < 0x02000000 or sb1 >= 0x02040000 then
        H.log("FAIL sb1 pointer not EWRAM")
        H.finish()
        return
    end
    local checked, ok = 0, 0
    for id, wantSet in pairs(lastOp) do
        local byte = emu:read8(sb1 + FLAGS_OFF + math.floor(id / 8))
        local bit = math.floor(byte / 2 ^ (id % 8)) % 2
        checked = checked + 1
        if (bit == 1) == wantSet then
            ok = ok + 1
        else
            H.log(string.format("  MISMATCH flag 0x%03X want %s got bit=%d",
                id, tostring(wantSet), bit))
        end
    end
    H.assertTrue("observed at least 5 distinct flags", checked >= 5)
    H.assertEq("flags matching at sb1+0x12E8", ok, checked)
    H.finish()
end)
