#!/usr/bin/env python3
"""Negative test for verify_artifacts.py section 15 -- the roster display
(roots blob, relocated callback table, desk entry, code). 2026-09-27.

Ported from Seaglass's three negative tests (roster_roots / dyn_event_table /
roster_entry), merged because Lazarus checks all three in one section. Each
case breaks a COPY of the built ROM in one way and requires the matching check
to report FAIL BY NAME (a tampered ROM also fails diff containment, so a bare
exit code proves nothing). Checks that must stay SILENT prove the tamper was
precise -- a checker that fails everything would "catch" every case.

⚠️ THE ROM IS NEVER MODIFIED IN PLACE.
"""
import json
import os
import re
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cm_tally import assert_cases  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
VERIFY = os.path.join(HERE, "verify_artifacts.py")
BUILT = os.path.join(ROOT, "build", "lazarus_cm.gba")
CM = os.path.join(ROOT, "tools", "character_mode")
_INJ = open(os.path.join(ROOT, "tools", "inject_character_mode.py"), encoding="utf-8").read()


def inj(name):
    return int(re.search(rf"^{name}\s*=\s*(0x[0-9A-Fa-f]+)", _INJ, re.M).group(1), 16)


ROOTS = inj("ROSTER_ROOTS_ADDR") - 0x08000000
TABLE = inj("DYN_EVENT_TABLE_ADDR") - 0x08000000
CODE = inj("ROSTER_MENU_ADDR") - 0x08000000
SCRIPT = inj("ROSTER_SCRIPT_ADDR") - 0x08000000
ROOTS_ADDR = inj("ROSTER_ROOTS_ADDR")
TABLE_ORIG = 0x08CEBB04
DESK_ORIG = 0x083287A7
_MAN = json.load(open(os.path.join(CM, "characters_manifest.json")))["characters"]
_RM = json.load(open(os.path.join(CM, "roster_roots_manifest.json")))
ESZ = _RM["entry_size_bytes"]
ROOTS_START = ROOTS + len(_MAN) * ESZ
NAME_BASE, STRIDE = int(_RM["species_table_base"], 16), _RM["species_table_stride"]

CHECKS = {
    "entry": "and root slice re-derive from the manifest",
    "tile": "entries tile roots[] exactly",
    "name": "resolves to a non-empty name in the BUILT ROM",
    "late": "late probe: character #",
    "empty": "characters with zero roots in-ROM ==",
    "copied": "callback table entries [0..1] == the base ROM's table",
    "slot2": "slot [2] == the roster set's",
    "lit": "table literal 0x820bd64 ->",
    "exhaust": "no reference to the old table remains",
    "none": "is gated by `cmp r1, #255`",
    "code": "roster code in-ROM == roster_display.bin",
    "consts": "compiled roster code carries ROSTER_ROOTS_ADDR",
    "desk": "all 4 desk BG events -> the pre-entry",
    "pre": "pre-entry: CM off -> stock desk",
    "after": "'Enter a code' -> right after the desk's own yes/no",
    "block": "roster block: callnative CM_RosterPushRows",
}


def _child_env():
    env = dict(os.environ)
    env.pop("CM_EXPECT_CHECKS", None)
    env.pop("CM_EXPECT_CASES", None)
    return env


def run(rom_path):
    src = open(VERIFY, encoding="utf-8").read()
    src = src.replace('ROM_OUT = ROOT / "build" / "lazarus_cm.gba"',
                      'ROM_OUT = Path(%r)' % rom_path, 1)
    path = os.path.join(HERE, "_negtest_verify_roster.py")
    open(path, "w", encoding="utf-8").write(src)
    try:
        p = subprocess.run([sys.executable, path], capture_output=True,
                           text=True, cwd=ROOT, env=_child_env())
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    return p.returncode, p.stdout + p.stderr


def _hit(out, key, marker):
    return any(line.strip().startswith(marker) and CHECKS[key] in line
               for line in out.splitlines())


def fc(d, ci):
    return struct.unpack_from("<HH", d, ROOTS + ci * ESZ)


EXPECT_CASES = 16


def main():
    if not os.path.isfile(BUILT):
        print("SKIP: no built ROM -- run the injector first")
        return 0
    good = bytearray(open(BUILT, "rb").read())
    late = len(_MAN) - 1
    big = max(ci for ci in range(len(_MAN)) if fc(good, ci)[1] >= 4)
    # A real species SLOT with no name, measured in this ROM (not assumed).
    blank = next(s for s in range(1, 1561)
                 if good[NAME_BASE + s * STRIDE] in (0x00, 0xFF))
    fails, passes = [], 0

    with tempfile.TemporaryDirectory() as tmp:

        def case(name, mutate, want_fail, also_pass=()):
            nonlocal passes
            data = bytearray(good)
            if mutate is not None:
                mutate(data)
                if data == good:
                    fails.append("%s: TAMPER CHANGED NOTHING" % name)
                    print("  [MISS] %s -- TAMPER CHANGED NOTHING" % name)
                    return
            rom = os.path.join(tmp, "tampered.gba")
            open(rom, "wb").write(bytes(data))
            _rc, out = run(rom)
            if want_fail is None:
                ok = all(_hit(out, k, "[PASS]") for k in CHECKS)
                detail = "every section-15 check passes"
            else:
                wants = want_fail if isinstance(want_fail, tuple) else (want_fail,)
                ok = all(_hit(out, k, "[FAIL]") for k in wants)
                detail = " and ".join("%r reported FAIL" % CHECKS[k] for k in wants)
                for k in also_pass:
                    if not _hit(out, k, "[PASS]"):
                        ok = False
                        detail += "; but %r did not PASS" % CHECKS[k]
            print("  [%s] %s -- %s" % ("PASS" if ok else "MISS", name, detail))
            if ok:
                passes += 1
            else:
                fails.append(name)

        print("negative test: verify_artifacts section 15, roster display")
        case("1 control -- the real build", None, None)

        def blank_name(d):
            f, _c = fc(d, big)
            struct.pack_into("<H", d, ROOTS_START + f * 2, blank)
        case("2 a root bent to a nameless species slot", blank_name, "name")

        def bend_first(d):
            f, c = fc(d, big)
            struct.pack_into("<HH", d, ROOTS + big * ESZ, f + 1, c)
        case("3 a first_root bent into another character's roots (real names)",
             bend_first, "entry", also_pass=("name",))

        def bend_last(d):
            f, c = fc(d, late)
            struct.pack_into("<HH", d, ROOTS + late * ESZ, f, c + 1)
        case("4 the last character's count bent -- roots no longer tile", bend_last, "tile")

        def bend_late(d):
            f, c = fc(d, late)
            if c == 0:      # the last character may be empty: bend the nearest non-empty one
                return
            cur, = struct.unpack_from("<H", d, ROOTS_START + f * 2)
            struct.pack_into("<H", d, ROOTS_START + f * 2, 25 if cur != 25 else 26)
        if fc(good, late)[1]:
            case("5 the LATE probe's own roots bent", bend_late, "late")
        else:
            case("5 the LATE probe's count bent (character #%d is empty)" % (late + 1),
                 bend_last, "late")

        def zero_count(d):
            f, _c = fc(d, big)
            struct.pack_into("<HH", d, ROOTS + big * ESZ, f, 0)
        case("6 a count zeroed -- an empty roster appears", zero_count, "empty")

        def bend_copied(d):
            v, = struct.unpack_from("<I", d, TABLE + 12 + 4)
            struct.pack_into("<I", d, TABLE + 12 + 4, v + 4)
        case("7 a copied set-1 callback bent", bend_copied, "copied", also_pass=("slot2",))

        def swap_slot2(d):
            struct.pack_into("<I", d, TABLE + 24 + 4, struct.unpack_from("<I", d, TABLE + 12 + 4)[0])
        case("8 set 2's OnSelectionChanged swapped for set 1's (a real callback)",
             swap_slot2, "slot2", also_pass=("copied",))

        def leave_lit(d):
            struct.pack_into("<I", d, 0x20BD64, TABLE_ORIG)
        case("9 one literal left at the OLD table", leave_lit, ("lit", "exhaust"),
             also_pass=("copied", "slot2"))

        def none_two(d):
            o = 0x0820BA66 - 0x08000000
            assert struct.unpack_from("<H", d, o)[0] == 0x29FF, "re-derive the NONE cmp"
            struct.pack_into("<H", d, o, 0x2902)
        case("10 NONE changed from 0xFF to 2 at one load", none_two, "none")

        def bend_code(d):
            d[CODE + 8] ^= 1
        case("11 roster code bent", bend_code, "code", also_pass=("pre", "block"))

        def bend_roots_lit(d):
            for i in range(CODE, CODE + 0x400, 4):
                if struct.unpack_from("<I", d, i)[0] == ROOTS_ADDR:
                    struct.pack_into("<I", d, i, ROOTS_ADDR + 4)
        case("12 compiled roots literal one entry off", bend_roots_lit, "consts",
             also_pass=("pre", "block"))

        def revert_desk(d):
            struct.pack_into("<I", d, 0xEA28A0, DESK_ORIG)   # (7,8) left on the stock script
        case("13 one desk BG event left on the stock script", revert_desk, "desk",
             also_pass=("pre", "after"))

        def bend_after(d):
            o = SCRIPT + 10 + 12 + 8 + 11 + 7                # row 1's goto_if target
            struct.pack_into("<I", d, o, DESK_ORIG)          # would re-ask the yes/no
        case("14 'Enter a code' re-aimed at the stock script start", bend_after, "after",
             also_pass=("desk", "block"))

        def set_one(d):
            rb = struct.unpack_from("<I", d, SCRIPT + 10 + 12 + 8 + 7)[0] - 0x08000000
            d[rb + 26] = 1
        case("15 roster block callback set 2 -> 1 (item icons)", set_one, "block",
             also_pass=("pre", "after"))

        case("16 control again -- nothing left behind", None, None)

    total = passes + len(fails)
    if fails:
        print("RESULT: %d/%d -- MISSED: %s" % (passes, total, ", ".join(fails)))
        return 1
    print("RESULT: %d/%d ALL PASS" % (passes, total))
    return assert_cases(total, EXPECT_CASES, "roster_display_negative_test")


if __name__ == "__main__":
    sys.exit(main())
