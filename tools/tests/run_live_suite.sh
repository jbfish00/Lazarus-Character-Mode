#!/bin/sh
# Full live regression suite for Lazarus Character Mode (headless mGBA).
# Runs every savestate-driven e2e against build/lazarus_cm.gba and prints a
# PASS/FAIL summary. ~2 min wall (harness os.exit-s at finish). Exit 0 = everything green.
#
# Layers not covered here (run separately):
#   python3 tools/tests/shim_unit_test.py      # GDB decision-table unit tests
#   python3 tools/tests/verify_artifacts.py    # static artifact verification
cd "$(dirname "$0")/../.."

MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
ROM=build/lazarus_cm.gba
fail=0

# ⭐ Every layer declares the number of assertions it MUST run, as the 4th
# argument. It reaches the script as CM_EXPECT_CHECKS, and H.finish() turns
# both "ran zero assertions" and "ran a different number than declared" into
# RESULT: FAIL -- so the grep below catches them with no extra plumbing
# (../game_plans/rowe_parity.md §1; proved by tools/tests/harness_guard_test.sh).
#
# Why: until 2026-08-20 H.finish() emitted RESULT: PASS whenever nothing had
# FAILED, and the pass count was printed and never read. A layer that
# mis-navigated, lost its savestate, or had its checks edited away was
# indistinguishable here from one that passed, so "LIVE SUITE: ALL PASS" was
# consistent with any number of these layers asserting nothing. Seaglass turned
# out to have exactly that (its boot layer checked nothing at all).
# If you change a layer's assertions, update its number; a changed tally is a
# regression until a human says otherwise.
run() { # name savestate script expected_checks
    name=$1; state=$2; script=$3; expect=$4
    log=build/live_$name.log
    if [ -n "$state" ]; then
        CM_EXPECT_CHECKS="$expect" timeout 110 "$MGBA" -t "$state" --script "$script" "$ROM" > "$log" 2>&1 || true
    else
        CM_EXPECT_CHECKS="$expect" timeout 110 "$MGBA" --script "$script" "$ROM" > "$log" 2>&1 || true
    fi
    if grep -aq "HARNESS RESULT: PASS" "$log"; then
        echo "[PASS] $name ($expect checks)"
    else
        echo "[FAIL] $name (see $log)"
        grep -a "HARNESS" "$log" | tail -6
        fail=1
    fi
}

# Injection addresses the Lua tests need, parsed from the injector rather than
# copied into them. build/ is gitignored, so this must be regenerated per run.
mkdir -p build
python3 - > build/cm_layout.lua <<'PYEOF'
import pathlib, re
src = pathlib.Path("tools/inject_character_mode.py").read_text()
def addr(name):
    m = re.search(r"^%s\s*=\s*(0x[0-9A-Fa-f]+)" % name, src, re.M)
    if not m:
        raise SystemExit("could not parse %s out of the injector" % name)
    return int(m.group(1), 16)
print("return {mugshot_addr=%d, bitmaps_addr=%d, hidden_addr=%d}"
      % (addr("CM_MUGSHOT_ADDR"), addr("BITMAPS_ADDR"), addr("HIDDEN_ADDR")))
PYEOF

run boot_smoke "" tools/mgba_scripts/boot_smoke.lua 4

echo 'return {cm_on=true}'  > build/cm_test_mode.lua
run catch_gate_on  tools/savestates/battle_bag.ss tools/mgba_scripts/cm_gate_test.lua 3
run starter_on     tools/savestates/spawn.ss      tools/mgba_scripts/cm_starter_test.lua 2
echo 'return {cm_on=false}' > build/cm_test_mode.lua
run catch_gate_off tools/savestates/battle_bag.ss tools/mgba_scripts/cm_gate_test.lua 1
run starter_off    tools/savestates/spawn.ss      tools/mgba_scripts/cm_starter_test.lua 1

# cheat-UI activation (also regenerates cm_red_active.ss for the tests below)
echo 'return {code="red", expect="activate_red"}' > build/cm_ui_code.lua
run ui_activate_red tools/savestates/naming.ss tools/mgba_scripts/cm_cheat_ui_test.lua 9

echo 'return {code="cmdbggive2", expect="give2", open_desk=true}' > build/cm_ui_code.lua
run ui_give2_boxing tools/savestates/cm_red_active.ss tools/mgba_scripts/cm_cheat_ui_test.lua 3

run save_load tools/savestates/cm_red_active.ss tools/mgba_scripts/cm_saveload_test.lua 4

# In-game roster display (2026-09-27, ported from Seaglass). AFTER
# ui_activate_red, which regenerates cm_red_active.ss (player at the desk, CM
# on). These layers break on engine addresses, so the debugger stub is needed.
# CM_CHAR 10 (Misty) is deliberately NOT #1: a per-character test on the first
# record cannot catch an indexing error. Rows are derived from the manifest.
export MGBA_HEADLESS_DEBUGGER=1 CM_CHAR=10
eval "$(python3 tools/tests/roster_menu_env.py 10)" || fail=1
run mon_icon_path tools/savestates/cm_red_active.ss tools/mgba_scripts/mon_icon_path_probe.lua 7
MODE=roster; export MODE
run roster_menu tools/savestates/cm_red_active.ss tools/mgba_scripts/cm_roster_menu_test.lua 10
MODE=code; export MODE
run roster_code tools/savestates/cm_red_active.ss tools/mgba_scripts/cm_roster_menu_test.lua 3
MODE=off; export MODE
run roster_off tools/savestates/cm_red_active.ss tools/mgba_scripts/cm_roster_menu_test.lua 3
unset MODE CM_CHAR

sh tools/tests/run_trade_e2e.sh || fail=1
sh tools/tests/run_egg_e2e.sh || fail=1
sh tools/tests/run_pc_e2e.sh || fail=1
sh tools/tests/run_pc_guard_e2e.sh || fail=1
sh tools/tests/run_link_trade_sweep_e2e.sh || fail=1

# 100% catch for on-roster species (2026-10-09). Wild Hoppip at full HP:
# Erika (12) has it, Red (1) does not: his ball is refused. The odds are read at the hooked
# decision's successors. Seed 2 breaks out with CM off, so the sure runs on it
# are the hook's doing; a copy with the compare restored must FAIL "sure".
export MGBA_HEADLESS_DEBUGGER=1
for seed in 1 2 3; do
    CM_ON=1 CM_CHAR=12 SEED=$seed EXPECT=sure; export CM_ON CM_CHAR SEED EXPECT
    run sure_catch_$seed tools/savestates/battle_bag.ss tools/mgba_scripts/cm_sure_catch_test.lua 2
done
CM_ON=1 CM_CHAR=1 SEED=1 EXPECT=dodged; export CM_ON CM_CHAR SEED EXPECT
run sure_catch_offroster tools/savestates/battle_bag.ss tools/mgba_scripts/cm_sure_catch_test.lua 2
CM_ON=0 SEED=2 EXPECT=miss; export CM_ON SEED EXPECT
run sure_catch_cmoff tools/savestates/battle_bag.ss tools/mgba_scripts/cm_sure_catch_test.lua 2
python3 - "$ROM" build/lazarus_cm_nosure.gba <<'PY'
import sys
d = bytearray(open(sys.argv[1], "rb").read())
d[0x0A7354:0x0A7358] = bytes.fromhex("fe2e05d8")   # the base ROM's cmp r6,#254 ; bhi
open(sys.argv[2], "wb").write(d)
PY
CM_ON=1 CM_CHAR=12 SEED=2 EXPECT=sure; export CM_ON CM_CHAR SEED EXPECT
CM_EXPECT_CHECKS=2 timeout 110 "$MGBA" -t tools/savestates/battle_bag.ss \
    --script tools/mgba_scripts/cm_sure_catch_test.lua build/lazarus_cm_nosure.gba \
    > build/live_sure_catch_nohook.log 2>&1 || true
if grep -aq "HARNESS RESULT: PASS" build/live_sure_catch_nohook.log; then
    echo "[FAIL] sure_catch_nohook: the no-hook ROM passed 'sure'"; fail=1
else
    echo "[PASS] sure_catch_nohook (negative control: the no-hook ROM fails 'sure')"
fi
unset CM_ON CM_CHAR SEED EXPECT MGBA_HEADLESS_DEBUGGER
python3 tools/tests/sure_catch_negative_test.py || fail=1

# QoL 2026-10-17: egg moves in the relearner. The desk runs the real special ChooseMonForMoveRelearner; picking the
# lead sets VAR_0x8005 = the relearnable count. Shipped: its egg moves (> 0); CM_NO_EGGRELEARN control: 0.
# QoL A2 (2026-10-24): every level-up move too; the CM_NO_ANYLEVEL control (egg moves only) must count fewer.
# This lead's egg moves alone fill all 24 slots, so A2 is measured on test builds without them (CM_TEST_NO_EGG): the
# any-level list must count more than the same build with the level cut (CM_NO_ANYLEVEL): 24 (the cap) vs 16 here.
python3 tools/tests/build_relearn_testrom.py >/dev/null && python3 tools/tests/build_relearn_testrom.py --control >/dev/null \
    && python3 tools/tests/build_relearn_testrom.py --noegg >/dev/null \
    && python3 tools/tests/build_relearn_testrom.py --noegg --anylevel-control >/dev/null || fail=1
for c in "reltest pos" "reltest_ctl zero" "reltest_noegg pos" "reltest_noegg_lv less"; do
    set -- $c
    [ "$2" = less ] && set -- $1 "less:$(grep -ao 'RELEARN count=[0-9]*' build/live_relearn_reltest_noegg.log | tail -1 | cut -d= -f2)"
    CM_EXPECT_CHECKS=2 TAG=$1 WANT=$2 MGBA_HEADLESS_DEBUGGER=1 timeout 200 "$MGBA" -t tools/savestates/cm_red_active.ss \
        --script tools/mgba_scripts/cm_relearn_test.lua build/lazarus_cm_$1.gba > build/live_relearn_$1.log 2>&1 || true
    if grep -aq "HARNESS RESULT: PASS" build/live_relearn_$1.log; then
        echo "[PASS] relearner $1 ($(grep -ao 'RELEARN count=[0-9]*' build/live_relearn_$1.log | tail -1))"
    else
        echo "[FAIL] relearner $1 (build/live_relearn_$1.log)"; fail=1
    fi
done

# Early party-wide Exp. Share with CM OFF (user, 2026-10-21). Native and CM-independent:
# (1) the base game's own pre-gym-1 Rotom Phone give (0x08382D5F) run from the desk with CM off
#     sets flag 0x495 and adds item 461; the control ROM enters after the setflag and must FAIL;
# (2) a real battle with CM off: with 0x495 set a bench mon gains EXP; with it clear it doesn't.
python3 tools/tests/build_expshare_testrom.py >/dev/null && python3 tools/tests/build_expshare_testrom.py --control >/dev/null || fail=1
for c in "expgive PASS" "expgive_ctl FAIL"; do
    set -- $c
    CM_EXPECT_CHECKS=4 CM_SHOTS=build/live_$1 timeout 110 "$MGBA" -t tools/savestates/cm_red_active.ss \
        --script tools/mgba_scripts/cm_exp_share_give_test.lua build/lazarus_cm_$1.gba > build/live_$1.log 2>&1 || true
    if grep -aq "HARNESS RESULT: $2" build/live_$1.log; then
        echo "[PASS] exp_share give $1 (want $2)"
    else
        echo "[FAIL] exp_share give $1 (want $2, see build/live_$1.log)"; fail=1
    fi
done
for sh in 1 0; do
    SHARE=$sh CM_EXPECT_CHECKS=4 timeout 110 "$MGBA" -t tools/savestates/battle_menu.ss \
        --script tools/mgba_scripts/cm_exp_share_test.lua "$ROM" > build/live_exp_share_$sh.log 2>&1 || true
    if grep -aq "HARNESS RESULT: PASS" build/live_exp_share_$sh.log; then
        echo "[PASS] exp_share battle share=$sh ($(grep -ao 'slot1 exp [0-9]* -> [0-9]*' build/live_exp_share_$sh.log | tail -1))"
    else
        echo "[FAIL] exp_share battle share=$sh (see build/live_exp_share_$sh.log)"; fail=1
    fi
done

# overworld sprite (2026-10-22): five cases + a no-hook negative control
if bash tools/tests/run_ow_sprite_test.sh > build/live_ow_sprite.log 2>&1; then
    echo "[PASS] overworld sprite ($(grep -c '  PASS' build/live_ow_sprite.log) cases incl. negative control)"
else
    echo "[FAIL] overworld sprite (see build/live_ow_sprite.log)"; grep -a '  FAIL' build/live_ow_sprite.log; fail=1
fi

# QoL A3 (2026-10-28): a new game starts with battle animations off (cold boot, real intro); control = CM_NO_ANIMDEFAULT
CM_NO_ANIMDEFAULT=1 python3 tools/inject_character_mode.py > build/anim_ctl_build.log 2>&1 \
    && python3 tools/inject_character_mode.py > build/anim_build.log 2>&1 || { echo "[FAIL] A3 builds"; fail=1; }
for c in "lazarus_cm 1" "lazarus_cm_noanim 0" "lazarus_cm_noanim 1"; do
    set -- $c
    WANT=$2 CM_EXPECT_CHECKS=3 MGBA_HEADLESS_DEBUGGER=1 timeout 600 "$MGBA" \
        --script tools/mgba_scripts/cm_anim_default_test.lua build/$1.gba > build/live_anim_$1_$2.log 2>&1 || true
    want=PASS; [ "$1 $2" = "lazarus_cm_noanim 1" ] && want=FAIL     # the control must not pass as 'off'
    if grep -aq "HARNESS RESULT: $want" build/live_anim_$1_$2.log; then
        echo "[PASS] new game battle animations: $1 WANT=$2 -> $want"
    else
        echo "[FAIL] new game battle animations: $1 WANT=$2 (want $want, see build/live_anim_$1_$2.log)"; fail=1
    fi
done

# QoL A3 instant HP bar (2026-10-28): a full-HP foe KO'd by Pound (battle_menu.ss) drains its bar in <= 4 frames an
# update on the shipped ROM, more on the CM_NO_INSTANTHP control, and the control asked for instant must FAIL
CM_NO_INSTANTHP=1 python3 tools/inject_character_mode.py > build/hp_ctl_build.log 2>&1 \
    && python3 tools/inject_character_mode.py > build/hp_build.log 2>&1 || { echo "[FAIL] instant HP builds"; fail=1; }
for c in "lazarus_cm 1" "lazarus_cm_nohp 0" "lazarus_cm_nohp 1"; do
    set -- $c
    WANT_INSTANT=$2 CM_EXPECT_CHECKS=2 MGBA_HEADLESS_DEBUGGER=1 timeout 200 "$MGBA" -t tools/savestates/battle_menu.ss \
        --script tools/mgba_scripts/cm_instant_hp_test.lua build/$1.gba > build/live_hp_$1_$2.log 2>&1 || true
    want=PASS; [ "$1 $2" = "lazarus_cm_nohp 1" ] && want=FAIL     # the control must not pass as 'instant'
    if grep -aq "HARNESS RESULT: $want" build/live_hp_$1_$2.log; then
        echo "[PASS] instant HP bar: $1 WANT_INSTANT=$2 -> $want"
    else
        echo "[FAIL] instant HP bar: $1 WANT_INSTANT=$2 (want $want, see build/live_hp_$1_$2.log)"; fail=1
    fi
done

# EXP rate (QoL, user 2026-10-29): the Exp. Share battle (CM off) at every rate gives x1 * N / 2 to the battler and
# the bench mon (pinned below); the CM_NO_EXPRATE control ignores the rate, so asked for x2 it must FAIL, and its shim
# fails verify_artifacts' compiled-code check. START > Exp. Rate: three chooser cases, and the same ROM with the input
# handler's original bytes back (it fades to black first) must FAIL the "opened over the field" check.
CM_NO_EXPRATE=1 python3 tools/inject_character_mode.py > build/er_ctl_build.log 2>&1 || { echo "[FAIL] EXP rate control build"; fail=1; }
if python3 tools/tests/verify_artifacts.py 2>&1 | grep -aq "\[FAIL\] compiled CM_ApplyExpMultipliers"; then
    echo "[PASS] EXP rate: verify_artifacts' compiled-code check FAILS on the CM_NO_EXPRATE shim"
else
    echo "[FAIL] EXP rate: the compiled-code check did not fail on the control shim"; fail=1
fi
python3 tools/inject_character_mode.py > build/er_build.log 2>&1 || { echo "[FAIL] EXP rate build"; fail=1; }
for c in "lazarus_cm 0 35 18 PASS" "lazarus_cm 1 52 27 PASS" "lazarus_cm 2 70 36 PASS" "lazarus_cm 3 105 54 PASS" \
         "lazarus_cm 4 17 9 PASS" "lazarus_cm_noexprate 2 70 36 FAIL" "lazarus_cm_noexprate 2 35 18 PASS"; do
    set -- $c
    RATE=$2 WANT0=$3 WANT1=$4 CM_EXPECT_CHECKS=4 timeout 110 "$MGBA" -t tools/savestates/battle_menu.ss \
        --script tools/mgba_scripts/cm_exp_rate_test.lua build/$1.gba > build/live_er_$1_$2_$3.log 2>&1 || true
    if grep -aq "HARNESS RESULT: $5" build/live_er_$1_$2_$3.log; then
        echo "[PASS] EXP rate: $1 rate $2 -> +$3 / +$4 is $5 ($(grep -ao 'battler +[0-9]*, bench +[0-9]*' build/live_er_$1_$2_$3.log | tail -1))"
    else
        echo "[FAIL] EXP rate: $1 rate $2 want +$3 / +$4 $5 (see build/live_er_$1_$2_$3.log)"; fail=1
    fi
done
python3 - <<'PY'
d = bytearray(open("build/lazarus_cm.gba", "rb").read())
o = 0x21BE54
d[o:o + 56] = bytes.fromhex("2c4a9a1a511e8a412b49591a481e814111402a4a9a1a501e82410a40"
                            "2849591a481e81411142d7d0264a9342d4d00021012029f71bf9cfe7")
open("build/lazarus_cm_erfade.gba", "wb").write(d)
PY
for c in "lazarus_cm DDA 2 PASS" "lazarus_cm UA 4 PASS" "lazarus_cm B 0 PASS" "lazarus_cm_erfade DDA 2 FAIL"; do
    set -- $c
    KEYS=$2 WANT=$3 CM_EXPECT_CHECKS=4 timeout 60 "$MGBA" -t tools/savestates/cm_red_active.ss \
        --script tools/mgba_scripts/cm_exp_rate_ui_test.lua build/$1.gba > build/live_erui_$1_$2.log 2>&1 || true
    if grep -aq "HARNESS RESULT: $4" build/live_erui_$1_$2.log \
       && { [ "$4" = PASS ] || grep -aq "FAIL the chooser opened over the field" build/live_erui_$1_$2.log; }; then
        echo "[PASS] EXP rate START row: $1 keys $2 -> $3 is $4"
    else
        echo "[FAIL] EXP rate START row: $1 keys $2 want $4 (see build/live_erui_$1_$2.log)"; fail=1
    fi
done

echo
[ $fail -eq 0 ] && echo "LIVE SUITE: ALL PASS" || echo "LIVE SUITE: FAILURES"
exit $fail
