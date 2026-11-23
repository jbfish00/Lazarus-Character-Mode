#!/usr/bin/env python3
"""Static check of the move "best version" edits (user 2026-11-23) in build/lazarus_cm.gba.

usage: python3 tools/tests/check_move_best.py [rom] [--no-tamper]
Pass = every applied row of tools/character_mode/move_changes.json reads its new value (secondary chances through the
move's additionalEffects pointer), an edited effect array differs from the base one only in that chance, no other bit of
an edited record and no other byte of the move table changed, and the counts equal the pinned EXPECT.
Controls (always run): a reverted edit, a stray table byte, a corrupted effect id in a repointed array, the base ROM."""
import json, struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import movepatch

BASE = ROOT / "rom" / "lazarus-v2.gba"
TABLE = 0x088CFAC8 - 0x08000000            # live gMovesInfo (260 literal refs)
GEOM = dict(stride=52, pri=(20, 0), effptr=36, neff=(20, 18))
EXPECT = (545, 0)                 # (applied, deferred), pinned 2026-11-23
SL = json.load((ROOT / "tools/character_mode/move_changes.json").open())
N = max(c["hack_move_id"] for c in SL["changes"])


def check(base, built):
    todo, deferred, _, _ = movepatch.plan(SL, "exp")
    bad = movepatch.verify(base, built, SL, TABLE, "exp", N, **GEOM)
    if (len(todo), len(deferred)) != EXPECT:
        bad.append(f"counts {len(todo)}/{len(deferred)} (want {EXPECT})")
    return bad, todo


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    built = bytearray(Path(a[0] if a else ROOT / "build" / "lazarus_cm.gba").read_bytes())
    base = BASE.read_bytes()
    bad, todo = check(base, built)
    for b in bad[:20]:
        print("FAIL", b)
    print(f"move edits checked: {len(todo)} applied, {len(bad)} failures (want 0)")
    rc = 1 if bad else 0
    if "--no-tamper" not in sys.argv:
        c = next(x for x in todo[len(todo) // 2:] if x["field"] == "pp")
        t1 = bytearray(built); o = TABLE + GEOM["stride"] * c["hack_move_id"] + 14; t1[o] = base[o]
        t2 = bytearray(built); t2[TABLE + GEOM["stride"] * 200 + 4] ^= 0x40          # description pointer byte of move 200
        ch = next(x for x in todo if x["field"] == "chance")
        p = struct.unpack_from("<I", built, TABLE + GEOM["stride"] * ch["hack_move_id"] + GEOM["effptr"])[0] - 0x08000000
        t3 = bytearray(built); t3[p] ^= 0x01                                         # the repointed array's effect id
        ok = 0
        for name, t in [(f"an applied edit reverted ({c['move']} pp)", t1), ("a stray move-table byte", t2),
                        (f"{ch['move']}'s repointed effect array corrupted", t3), ("the unpatched base ROM's table", bytearray(base))]:
            f = check(base, t)[0]
            print("caught" if f else "MISSED", name, len(f)); ok += bool(f)
        print(f"negative controls: {ok}/4")
        rc |= ok != 4
    sys.exit(rc)


if __name__ == "__main__":
    main()
