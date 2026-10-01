#!/usr/bin/env python3
"""Negative test for verify_artifacts.py section 18 -- the link-trade sweep
(src/character_mode.c CM_LinkTradeSweepThenExpand; rowe_parity.md §13.53),
2026-09-30.

Each case breaks a COPY of the built ROM in one way the hook could be wrong and
requires the matching check to report FAIL BY NAME; the other built-ROM
section-18 checks must stay PASS, proving the tamper was precise.

  1. control                          -- every section-18 check passes
  2. the WIRELESS site left vanilla    -- one ender skips the sweep: the
                                          partial-port shape
  3. the wired site aimed at +24       -- the PC guard's trampoline, a REAL
                                          neighbour: the plausible-wrong shape
  4. the trampoline aimed elsewhere    -- at CM_PSSLastMonGuard, a real entry
  5. the shim's BL to the sweep bent   -- +4 bytes: into the middle of
                                          CM_SweepPartyToPCNative
  6. control again                     -- proves 2-5 left nothing behind

⚠️ THE ROM IS NEVER MODIFIED IN PLACE.
"""
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

# Derived from the injector, never restated.
_INJ = open(os.path.join(ROOT, "tools", "inject_character_mode.py"),
            encoding="utf-8").read()


def _inj(name):
    return int(re.search(rf"^{name}\s*=\s*(0x[0-9A-Fa-f]+)", _INJ, re.M).group(1), 16)


# The injector writes it as TRAMPOLINE_BLOCK + 24; assert that shape rather
# than silently assuming it.
assert re.search(r"^LINK_TRADE_TRAMPOLINE_ADDR\s*=\s*TRAMPOLINE_BLOCK \+ 32", _INJ, re.M)
LINK_TRAMP = _inj("TRAMPOLINE_BLOCK") + 32
GUARD_TRAMP = _inj("TRAMPOLINE_BLOCK") + 24
SITES = tuple(int(x, 16) for x in re.findall(r"0x[0-9A-Fa-f]+", re.search(
    r"^LINK_TRADE_BL_SITES\s*=\s*\(([^)]*)\)", _INJ, re.M).group(1)))
EXPAND = _inj("STRING_EXPAND_PLACEHOLDERS")


def _syms():
    out = subprocess.run(["arm-none-eabi-nm", os.path.join(ROOT, "build", "character_mode.elf")],
                         check=True, capture_output=True, text=True).stdout
    return {m.group(2): int(m.group(1), 16)
            for m in re.finditer(r"^([0-9a-f]+) [Tt] (\w+)$", out, re.M)}


def thumb_bl(src, dst):
    off = ((dst - (src + 4)) >> 1) & 0x3FFFFF
    return struct.pack("<HH", 0xF000 | ((off >> 11) & 0x7FF), 0xF800 | (off & 0x7FF))


CHECKS = {
    "site": "built: both sites call the link trampoline",
    "tramp": "link trampoline is ldr r3,[pc]; bx r3 -> CM_LinkTradeSweepThenExpand",
    "lits": "compiled link shim (read from the ROM) BLs CM_SweepPartyToPCNative",
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
    path = os.path.join(HERE, "_negtest_verify_linksweep.%d.py" % os.getpid())  # unique per run; gitignored
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
    # This verifier prints "[PASS]" / "[FAIL]" (Seaglass's prints them bare).
    return any(line.strip().startswith("[%s]" % marker) and CHECKS[key] in line
               for line in out.splitlines())


# A deliberate LITERAL -- see cm_tally.assert_cases.
EXPECT_CASES = 6


def main():
    if not os.path.isfile(BUILT):
        print("SKIP: no built ROM -- run the injector first")
        return 0
    good = bytearray(open(BUILT, "rb").read())
    syms = _syms()
    shim = syms["CM_LinkTradeSweepThenExpand"] & ~1
    sweep = syms["CM_SweepPartyToPCNative"] & ~1
    guard = syms["CM_PSSLastMonGuard"]
    fails, passes = [], 0

    with tempfile.TemporaryDirectory() as tmp:

        def case(name, mutate, want_fail, also_pass=()):
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
                detail = "every section-18 check passes"
            else:
                ok = _hit(out, want_fail, "FAIL")
                detail = "%r reported FAIL" % CHECKS[want_fail]
                for k in also_pass:
                    if not _hit(out, k, "PASS"):
                        ok = False
                        detail += "; but %r did not PASS" % CHECKS[k]
            print("  [%s] %s -- %s" % ("PASS" if ok else "MISS", name, detail))
            if ok:
                passes += 1
            else:
                fails.append(name)

        print("negative test: verify_artifacts section 18, link-trade sweep")
        case("1 control -- the real build", None, None)

        def leave_wireless(d):
            d[SITES[1]:SITES[1] + 4] = thumb_bl(0x08000000 + SITES[1], EXPAND)
        case("2 the wireless site left calling StringExpandPlaceholders", leave_wireless,
             "site", also_pass=("tramp", "lits"))

        def site_to_guard(d):
            d[SITES[0]:SITES[0] + 4] = thumb_bl(0x08000000 + SITES[0], GUARD_TRAMP)
        case("3 the wired site aimed at the PC guard's trampoline", site_to_guard,
             "site", also_pass=("tramp", "lits"))

        def aim_elsewhere(d):
            struct.pack_into("<I", d, LINK_TRAMP - 0x08000000 + 4, guard | 1)
        case("4 the trampoline aimed at CM_PSSLastMonGuard", aim_elsewhere,
             "tramp", also_pass=("site", "lits"))

        def bend_sweep_bl(d):
            o = shim - 0x08000000
            ks = [k for k in range(0, 0x1C, 2)
                  if bytes(d[o + k:o + k + 4]) == thumb_bl(shim + k, sweep)]
            assert len(ks) == 1, f"the shim's BL to the sweep found {len(ks)} times -- re-derive"
            d[o + ks[0]:o + ks[0] + 4] = thumb_bl(shim + ks[0], sweep + 4)
        case("5 the shim's BL to the sweep bent by +4", bend_sweep_bl,
             "lits", also_pass=("site", "tramp"))

        case("6 control again -- nothing left behind", None, None)

    total = passes + len(fails)
    if fails:
        print("RESULT: %d/%d -- MISSED: %s" % (passes, total, ", ".join(fails)))
        return 1
    print("RESULT: %d/%d ALL PASS" % (passes, total))
    return assert_cases(total, EXPECT_CASES, "link_trade_sweep_negative_test")


if __name__ == "__main__":
    sys.exit(main())
