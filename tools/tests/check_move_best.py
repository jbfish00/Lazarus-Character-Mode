#!/usr/bin/env python3
"""Static check of the move "best version" edits (user 2026-11-23) in build/lazarus_cm.gba.

usage: python3 tools/tests/check_move_best.py [rom] [--no-tamper]
Pass = every applied row of tools/character_mode/move_changes.json reads its new value (secondary chances through the
move's additionalEffects pointer), an edited effect array differs from the base one only in that chance, no other bit of
an edited record and no other byte of the move table changed, and the counts equal the pinned EXPECT.
Controls (always run): a reverted edit, a stray table byte, a corrupted effect id in a repointed array, the base ROM,
a reverted medium flag, a reverted crit +2 row, the bit just above a crit field (alwaysCriticalHit)."""
import json, struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import movepatch

BASE = ROOT / "rom" / "lazarus-v2.gba"
TABLE = 0x088CFAC8 - 0x08000000            # live gMovesInfo (260 literal refs)
GEOM = dict(stride=52, pri=(20, 0), effptr=36, neff=(20, 18))
EXPECT = (545 + 46 + 25, 0)   # (applied, deferred), pinned 2026-11-23 (cheap + medium flags/target) + 2026-11-24 crit +2
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
    # Behaviour cards (2026-11-25) own a few move-table bits (Double-Edge recoil, Minimize punish, ignoresSubstitute on
    # sound moves); tests/check_behaviour_exp.py checks them. When the built ROM carries them they are folded into the
    # base here, so they don't read as stray move-table bytes; a CM_NO_BEHAVIOUR build is checked against the raw base.
    _bc = json.load((ROOT / "tools/character_mode/behaviour_cards.json").open())["edits"]
    _tb = [e for e in _bc if e["kind"] == "data"]
    if _tb and all(built[int(e["addr"], 16) - 0x08000000:][:len(e["to"]) // 2].hex() == e["to"] for e in _tb):
        base = bytearray(base)
        for e in _tb:
            o = int(e["addr"], 16) - 0x08000000
            assert TABLE <= o < TABLE + 0x10000 and base[o:o + len(e["from"]) // 2].hex() == e["from"], e
            base[o:o + len(e["to"]) // 2] = bytes.fromhex(e["to"])
        base = bytes(base)
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
        cm = next(x for x in todo if x.get("tier") == "medium" and x["field"] != "target")   # a medium flag bit too
        fb = SL["geom"]["flagbits"][cm["field"]]
        t4 = bytearray(built); o = TABLE + GEOM["stride"] * cm["hack_move_id"] + fb[0]; t4[o] ^= 1 << fb[1]
        cc = next(x for x in todo if x["field"] == "crit")                                # a crit +2 row too
        cb, clo, cn = SL["geom"]["crit"]
        t5 = bytearray(built); o = TABLE + GEOM["stride"] * cc["hack_move_id"] + cb
        struct.pack_into("<I", t5, o, struct.unpack_from("<I", built, o)[0] & ~(((1 << cn) - 1) << clo) | (cc["from"] << clo))
        t6 = bytearray(built); o = TABLE + GEOM["stride"] * cc["hack_move_id"] + cb
        struct.pack_into("<I", t6, o, struct.unpack_from("<I", built, o)[0] ^ (1 << (clo + cn)))   # the bit above the field
        ok = 0
        for name, t in [(f"an applied edit reverted ({c['move']} pp)", t1), ("a stray move-table byte", t2),
                        (f"{ch['move']}'s repointed effect array corrupted", t3), ("the unpatched base ROM's table", bytearray(base)),
                        (f"a medium flag edit reverted ({cm['move']} {cm['field']})", t4),
                        (f"a crit +2 edit reverted ({cc['move']})", t5), (f"the bit above {cc['move']}'s crit stage", t6)]:
            f = check(base, t)[0]
            print("caught" if f else "MISSED", name, len(f)); ok += bool(f)
        print(f"negative controls: {ok}/7")
        rc |= ok != 7
    sys.exit(rc)


if __name__ == "__main__":
    main()
