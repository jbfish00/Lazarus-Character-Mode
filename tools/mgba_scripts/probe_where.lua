-- Print current map group/num, player coords, party count, then exit.
-- Usage: mgba-headless -t <state.ss> --script tools/mgba_scripts/probe_where.lua <rom>
local H = dofile("tools/mgba_scripts/harness.lua")

H.onFrame(function(f)
    if f == 30 then
        local b1 = emu:read32(H.gSaveBlock1Ptr)
        H.log(string.format("map=%d.%d x=%d y=%d partyCount=%d",
            emu:read8(b1 + 4), emu:read8(b1 + 5),
            emu:read16(b1), emu:read16(b1 + 2),
            emu:read8(0x0201B95D)))
        H.log(string.format("flag945=%s varCHAR=%d varSTARTER=%d",
            tostring(H.flagGet(0x945)), H.varGet(0x40E0), H.varGet(0x40E4)))
        emu:screenshot("tools/savestates/probe_where.png")
        H.finish()
    end
end)
