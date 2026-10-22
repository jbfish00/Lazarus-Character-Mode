#!/usr/bin/env python3
"""Negative test for verify_artifacts.py section 21 -- early party-wide Exp. Share,
CM on or off (native; 2026-10-21).

Each case breaks a COPY of the built ROM in one way and requires the matching
section-21 check to report FAIL BY NAME (any tamper also fails the BPS round-trip,
so a bare non-zero exit would prove nothing); the other section-21 check must stay PASS.

  1. control                                      -- both checks pass
  2. the scene's setflag made 0x496                -- the give no longer arms the share
  3. IsExpShareEnabled's literal made 0x496         -- the battle reads another flag
  4. one getexp caller's BL aimed one halfword off  -- a caller no longer reaches it
  5. control again                                  -- nothing left behind

THE ROM IS NEVER MODIFIED IN PLACE.
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cm_tally import assert_cases  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
VERIFY = os.path.join(HERE, "verify_artifacts.py")
BUILT = os.path.join(ROOT, "build", "lazarus_cm.gba")

CHECKS = {
    "give": "the Rotom Phone scene still gives the Exp. Share and sets flag 0x495",
    "test": "IsExpShareEnabled 0x080D1270 is FlagGet(0x495) and its 4 getexp callers still call it",
}
SETFLAG = 0x382D67
IS_ENABLED_LIT = 0x0D127C
CALLER = 0x0953A4


def _child_env():
    env = dict(os.environ)
    env.pop("CM_EXPECT_CHECKS", None)
    env.pop("CM_EXPECT_CASES", None)
    return env


def run(rom_path):
    src = open(VERIFY, encoding="utf-8").read()
    src = src.replace('ROM_OUT = ROOT / "build" / "lazarus_cm.gba"',
                      'ROM_OUT = Path(%r)' % rom_path, 1)
    path = os.path.join(HERE, "_negtest_verify_expshare.%d.py" % os.getpid())  # gitignored
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
    return any(line.strip().startswith("[%s]" % marker) and CHECKS[key] in line
               for line in out.splitlines())


# A deliberate LITERAL -- see cm_tally.assert_cases.
EXPECT_CASES = 6



# A deliberate LITERAL -- see cm_tally.assert_cases.
EXPECT_CASES = 5


def main():
    if not os.path.isfile(BUILT):
        print("SKIP: no built ROM -- run the injector first")
        return 0
    good = bytearray(open(BUILT, "rb").read())
    fails, passes = [], 0

    with tempfile.TemporaryDirectory() as tmp:

        def case(name, mutate, want_fail):
            nonlocal passes
            data = bytearray(good)
            if mutate is not None:
                mutate(data)
                if data == good:
                    fails.append(name)
                    print("  [MISS] %s -- TAMPER CHANGED NOTHING" % name)
                    return
            rom = os.path.join(tmp, "tampered.gba")
            open(rom, "wb").write(bytes(data))
            _rc, out = run(rom)
            if want_fail is None:
                ok = all(_hit(out, k, "PASS") for k in CHECKS)
                detail = "every section-21 check passes"
            else:
                ok = _hit(out, want_fail, "FAIL")
                detail = "%r reported FAIL" % CHECKS[want_fail]
                for k in CHECKS:
                    if k != want_fail and not _hit(out, k, "PASS"):
                        ok = False
                        detail += "; but %r did not PASS" % CHECKS[k]
            print("  [%s] %s -- %s" % ("PASS" if ok else "MISS", name, detail))
            if ok:
                passes += 1
            else:
                fails.append(name)

        print("negative test: verify_artifacts section 21, native Exp. Share (CM on or off)")
        case("1 control -- the real build", None, None)

        def flag496(d):
            assert d[SETFLAG:SETFLAG + 3] == bytes.fromhex("299504")
            d[SETFLAG + 1] = 0x96
        case("2 the scene's setflag made 0x496", flag496, "give")

        def lit496(d):
            assert d[IS_ENABLED_LIT:IS_ENABLED_LIT + 4] == (0x495).to_bytes(4, "little")
            d[IS_ENABLED_LIT] = 0x96
        case("3 IsExpShareEnabled's literal made 0x496", lit496, "test")

        def caller_off(d):
            hw2 = int.from_bytes(d[CALLER + 2:CALLER + 4], "little")
            d[CALLER + 2:CALLER + 4] = (hw2 + 1).to_bytes(2, "little")
        case("4 one getexp caller's BL aimed one halfword off", caller_off, "test")

        case("5 control again -- nothing left behind", None, None)

    total = passes + len(fails)
    if fails:
        print("RESULT: %d/%d -- MISSED: %s" % (passes, total, ", ".join(fails)))
        return 1
    print("RESULT: %d/%d ALL PASS" % (passes, total))
    return assert_cases(total, EXPECT_CASES, "exp_share_negative_test")


if __name__ == "__main__":
    sys.exit(main())
