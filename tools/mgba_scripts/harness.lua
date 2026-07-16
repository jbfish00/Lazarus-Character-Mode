-- Seaglass Character Mode — reusable test harness (mgba-headless).
--
-- This is the closed-binary port of Pokemon ROWE's testing methodology.
-- ROWE (full C source) compiled an in-game DEBUG MENU into the ROM
-- (src/debug.c: Give Pokemon, set VAR_CHARACTER_ID, warp, heal party,
-- toggle FLAG_SYS_NO_CATCHING, access PC) and drove it by hand through
-- mgba-qt with xdotool keypresses + screenshots. See docs/TESTING.md for
-- the full method-by-method mapping and what does/doesn't port.
--
-- We cannot compile a C menu into a closed binary. Instead every debug-menu
-- CAPABILITY is reproduced here from OUTSIDE the ROM, via mGBA's scripting
-- API: direct RAM read/write (= "Give Pokemon"/"set var"/"set flag"),
-- scripted controller input (= the human pressing buttons), breakpoints on
-- ROM addresses (= something ROWE's menu could NOT do at all), and state
-- assertions. Everything runs headless and deterministically, so unlike
-- ROWE's one-off manual playtests these are repeatable regression tests.
--
-- Usage from another script:
--   local H = dofile("tools/mgba_scripts/harness.lua")
--   H.onFrame(function(f) ... end)
--   H.press(H.KEY.A, 4)          -- press A for 4 frames, then release
--   H.sequence({{H.KEY.A, 4}, {H.KEY.DOWN, 2}})
--   H.log("something")
--   H.assertEq("party count", H.rd8(addr), 1)
--   H.finish()                   -- prints PASS/FAIL summary
--
-- Run:
--   ./tools/mgba_src/build/mgba-headless --script <yourscript.lua> \
--     [-t savestate] "rom/seaglass v3.0.gba" 2>&1 | grep -E "HARNESS|PASS|FAIL"
--
-- All API calls used here were empirically verified against this exact
-- mgba-headless build (see CLAUDE.md's Toolchain section) — emu:setBreakpoint,
-- emu:addKey/clearKey (genuinely drives the emulated pad, confirmed via
-- getKeys() observing 0->1->0), emu:read8/16/32, console:log.

local H = {}

-- GBA key bit indices, from mgba's include/mgba/internal/gba/input.h
H.KEY = {
    A = 0, B = 1, SELECT = 2, START = 3,
    RIGHT = 4, LEFT = 5, UP = 6, DOWN = 7,
    R = 8, L = 9,
}

-- ---------------------------------------------------------------- RAM anchors
--
-- CONFIRMED 2026-07-15 on rom/lazarus-v2.gba @ rom.sha1 (Seaglass's trio
-- 0x030051B8/BC/C0 does NOT transfer — reads zero here):
--   Static literal-pool histogram (find_saveblock_trio method): the three
--   most-referenced consecutive IWRAM words are 0x03003664 (905 refs) /
--   0x03003668 (719) / 0x0300366C (91). Live (verify_trio.lua): all three
--   hold EWRAM pointers by the title screen (0x0200E580 / 0x0200D59C /
--   0x0201213C), and after mashing A through new-game naming, [2]'s target
--   begins BB E1 D5 E0 DD FF = "Amali" + terminator = SaveBlock2.playerName.
--     0x03003664 -> gSaveBlock1Ptr     (coords/WarpData fill on overworld spawn)
--     0x03003668 -> gSaveBlock2Ptr     (playerName verified live)
--     0x0300366C -> gPokemonStoragePtr (all zero at new game = empty PC)
--   Same consecutive SB1/SB2/Storage ordering as Seaglass, relocated address.
H.SAVEBLOCK_PTRS = { 0x03003664, 0x03003668, 0x0300366C }
H.gSaveBlock1Ptr = 0x03003664
H.gSaveBlock2Ptr = 0x03003668
H.gPokemonStoragePtr = 0x0300366C
-- SaveBlock1 field offsets (vanilla pokeemerald struct SaveBlock1):
H.SB1_POS_X   = 0x00  -- s16
H.SB1_POS_Y   = 0x02  -- s16
H.SB1_MAPGRP  = 0x04  -- u8
H.SB1_MAPNUM  = 0x05  -- u8

-- TODO / NOT YET CONFIRMED — these are what unlock the *state-mutation* half
-- of the ROWE debug-menu port ("Give Pokemon", "set var", "toggle catching").
-- They are much easier to find from a save that actually HAS a party than by
-- static analysis, which is why find_ram_anchors.lua exists: run it against a
-- savestate with Pokemon in the party and it will locate gPlayerParty by
-- scanning EWRAM for real 100-byte Pokemon structs. Until then, leave nil —
-- every helper below that needs one will fail loudly rather than poke a
-- guessed address (poking the wrong EWRAM address is exactly how you get a
-- "bug" that isn't real).
-- CONFIRMED 2026-07-16 (Phase 1e): starter located in EWRAM by its distinctive
-- typed nickname ("Aaaa..." = BB D5 D5 D5 at struct+8), then the global (vs
-- transient copies) pinned by ROM literal-ref count: 587 refs. gEnemyParty =
-- +600 (233 refs) => stride 100 (vanilla size kept). Count byte 3 before the
-- array (51 refs), live-verified reading 1 with a 1-mon party.
H.gPlayerParty = 0x0201B960      -- EWRAM base of the 6x100-byte party array
H.PARTY_STRIDE = 100
H.gEnemyParty = 0x0201BBB8       -- gPlayerParty + 600
H.gPlayerPartyCount = 0x0201B95D -- u8 party count

-- CONFIRMED 2026-07-16 (Phase 1d, docs/ROUTINE_MAP.md): flags/vars live inside
-- SaveBlock1 at these offsets (static disasm of FlagSet/GetFlagPointer/
-- GetVarPointer + live verification of 195 distinct flags via breakpoints).
-- SB1 base RELOCATES on new game — always deref H.gSaveBlock1Ptr fresh.
H.SB1_FLAGS_OFF = 0x12E8   -- u8 flags[0x12C] (2400 flags; ids < 0x4000)
H.SB1_VARS_OFF  = 0x1414   -- u16 vars[]      (ids 0x4000..0x7FFF)

function H.flagAddr(id)
    return emu:read32(H.gSaveBlock1Ptr) + H.SB1_FLAGS_OFF + math.floor(id / 8)
end
function H.flagGet(id)
    return math.floor(emu:read8(H.flagAddr(id)) / 2 ^ (id % 8)) % 2 == 1
end
function H.flagSet(id)
    local a = H.flagAddr(id)
    emu:write8(a, emu:read8(a) | (2 ^ (id % 8)))
end
function H.varAddr(id)
    return emu:read32(H.gSaveBlock1Ptr) + H.SB1_VARS_OFF + 2 * (id - 0x4000)
end
function H.varGet(id) return emu:read16(H.varAddr(id)) end
function H.varSet(id, v) emu:write16(H.varAddr(id), v) end

-- ------------------------------------------------------------------- plumbing

local frame = 0
local frameHooks = {}
local passes, failures = 0, {}

function H.log(msg)
    console:log("HARNESS " .. tostring(msg))
end

function H.frame() return frame end

function H.onFrame(fn)
    table.insert(frameHooks, fn)
end

-- ------------------------------------------------------------------- memory

function H.rd8(a)  return emu:read8(a)  end
function H.rd16(a) return emu:read16(a) end
function H.rd32(a) return emu:read32(a) end

-- Writes are the "debug menu" half — give a Pokemon, set a var, flip a flag.
-- mGBA exposes write8/16/32 on the same emu object as the reads.
function H.wr8(a, v)  emu:write8(a, v)  end
function H.wr16(a, v) emu:write16(a, v) end
function H.wr32(a, v) emu:write32(a, v) end

function H.hex(v, width)
    return string.format("0x%0" .. (width or 8) .. "X", v)
end

-- Deref the save-block pointer trio (they're pointers, not the blocks).
function H.saveBlocks()
    local out = {}
    for i, p in ipairs(H.SAVEBLOCK_PTRS) do
        out[i] = emu:read32(p)
    end
    return out
end

-- ------------------------------------------------------------------ assertions

function H.assertEq(what, got, want)
    if got == want then
        passes = passes + 1
        H.log("PASS " .. what .. " = " .. tostring(got))
        return true
    end
    local msg = what .. ": got " .. tostring(got) .. ", want " .. tostring(want)
    table.insert(failures, msg)
    H.log("FAIL " .. msg)
    return false
end

function H.assertTrue(what, cond)
    return H.assertEq(what, cond and true or false, true)
end

function H.finish()
    H.log("---- SUMMARY ----")
    H.log(string.format("PASSED %d, FAILED %d", passes, #failures))
    for _, f in ipairs(failures) do
        H.log("  FAILURE: " .. f)
    end
    if #failures == 0 then
        H.log("RESULT: PASS")
    else
        H.log("RESULT: FAIL")
    end
end

-- ---------------------------------------------------------------------- input
--
-- Scripted controller input. This replaces ROWE's xdotool-driven manual
-- keypresses (their CLAUDE.md notes >=0.4s holds were needed for the real
-- GUI to register). Here we drive the emulated pad directly, so timing is
-- exact and deterministic in frames — no flakiness, no host focus stealing.

local pending = {}   -- queue of {key=, frames=} steps
local active = nil
local activeUntil = 0

-- Queue a keypress: hold `key` for `frames`, then release and wait `gap`.
function H.press(key, frames, gap)
    table.insert(pending, { key = key, frames = frames or 4, gap = gap or 6 })
end

-- Queue a whole sequence: {{KEY.A, 4}, {KEY.DOWN, 2}, ...}
function H.sequence(steps)
    for _, s in ipairs(steps) do
        H.press(s[1] or s.key, s[2] or s.frames, s[3] or s.gap)
    end
end

-- Mash a key every `every` frames from `fromFrame` to `toFrame`. Useful for
-- clicking through dialogue of unknown length (ROWE's tests had the same
-- problem and solved it by holding A repeatedly).
function H.mash(key, fromFrame, toFrame, every)
    every = every or 20
    local held = false
    H.onFrame(function(f)
        if f >= fromFrame and f <= toFrame and (f % every) == 0 then
            if held then emu:clearKey(key) else emu:addKey(key) end
            held = not held
        elseif f == toFrame + 1 and held then
            emu:clearKey(key)
            held = false
        end
    end)
end

local function pumpInput()
    if active then
        if frame >= activeUntil then
            emu:clearKey(active.key)
            activeUntil = frame + active.gap
            active = nil
        end
        return
    end
    if frame < activeUntil then return end  -- inter-press gap
    local step = table.remove(pending, 1)
    if step then
        emu:addKey(step.key)
        active = step
        activeUntil = frame + step.frames
    end
end

-- ------------------------------------------------------------------ breakpoints
--
-- Something ROWE's in-game debug menu could not do at all: halt on an
-- arbitrary ROM address and inspect CPU state. This is the core tool for
-- the Phase 1 routine-mapping work (see docs/ROUTINE_MAP.md).
--
-- REQUIRES MGBA_HEADLESS_DEBUGGER=1 in the environment (2026-07-16): stock
-- headless never creates core->debugger, so emu:setBreakpoint returns -1 and
-- silently never fires. Our patched headless-main.c attaches a module-less
-- debugger when the env var is set. Emulation single-steps while breakpoints
-- are armed — only set the env var for trace runs.

function H.breakpoint(name, addr, fn)
    local id = emu:setBreakpoint(function()
        local pc = emu:readRegister("pc")
        H.log(string.format("BP %-16s frame=%-5d pc=%s r0=%s r1=%s r2=%s",
            name, frame, H.hex(pc), H.hex(emu:readRegister("r0")),
            H.hex(emu:readRegister("r1")), H.hex(emu:readRegister("r2"))))
        if fn then fn(frame) end
    end, addr)
    if not id or id < 0 then
        error("H.breakpoint('" .. name .. "') failed to register (id=" ..
            tostring(id) .. ") — run with MGBA_HEADLESS_DEBUGGER=1")
    end
    return id
end

-- ---------------------------------------------------------------------- driver

callbacks:add("frame", function()
    frame = frame + 1
    pumpInput()
    for _, fn in ipairs(frameHooks) do
        fn(frame)
    end
end)

return H
