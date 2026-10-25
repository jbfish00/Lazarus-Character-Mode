-- LIVE relearner layer (QoL 2026-10-17) on build/lazarus_cm_reltest[_ctl].gba (tools/tests/build_relearn_testrom.py).
-- From cm_red_active.ss walk to the University desk (cm_egg_hatch_test.lua's route); its test entry runs the real
-- special ChooseMonForMoveRelearner; A picks the lead. VAR_0x8005 = the relearnable count the game computed.
-- WANT=pos (shipped: the lead's egg moves) | zero (CM_NO_EGGRELEARN control: vanilla count 0) | less:N (QoL A2:
-- the CM_NO_ANYLEVEL build counts fewer than N, the any-level count of the same no-egg test build).
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local V8005 = tonumber(os.getenv("VAR_8005") or "0x20055fe")
H.onFrame(function(f)
    if f == 15 then emu:write16(V8005, 0xBEEF) end
    if f == 60 then H.press(K.RIGHT, 16) end
    if f == 120 then H.press(K.UP, 4) end
    if f == 160 then H.press(K.A, 6) end
    if f == 300 then H.press(K.A, 6) end            -- pick the lead in the party menu
    if f == 600 then
        emu:screenshot("tools/savestates/relearn_" .. (os.getenv("TAG") or "x") .. ".png")
        local n = emu:read16(V8005)
        H.log("RELEARN count=" .. n)
        H.assertTrue("ChooseMonForMoveRelearner wrote VAR_0x8005 (sentinel replaced)", n ~= 0xBEEF)
        local want = os.getenv("WANT") or ""
        if want == "zero" then
            H.assertEq("vanilla relearnable count (no egg moves)", n, 0)
        elseif want:match("^less:") then   -- QoL A2 control (CM_NO_ANYLEVEL): fewer than the any-level count of the same build
            local ship = tonumber(want:sub(6))
            H.assertTrue("level-cut count " .. n .. " is below the any-level count " .. ship, n < ship)
        else
            H.assertTrue("the lead has relearnable moves (its egg moves)", n > 0 and n <= 24)
        end
        H.finish()
    end
end)
