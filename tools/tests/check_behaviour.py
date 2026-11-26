#!/usr/bin/env python3
"""Static check of the move/ability behaviour cards (item 1, 2026-11-25) in a compiled expansion-binary ROM.

usage: check_behaviour_exp.py <hack> <repo root> [shipped.gba] [control.gba]
   hack = seaglass | lazarus | spirits | dreamstone; defaults: build/<hack>_cm.gba and build/<hack>_cm_nobeh.gba
   (the CM_NO_BEHAVIOUR=1 control). Master copy: game_plans/move_ability_best_2026-11-22/behaviour_all/gba/; each repo
   (and expansion-kit for Spirits / Dreamstone) keeps a copy in its tests folder.

Two layers, both must pass, and the controls below must each fail:
 1. bytes: every edit of tools/character_mode/behaviour_cards.json reads "to" in the shipped ROM and "from" in the
    control, and the two ROMs differ nowhere else (bpatch.verify). Edit count pinned per hack (EXPECT).
 2. meaning, decoded from the ROM itself with hand-pinned sites (this file never reads the card file for these): move
    fields through the move table, each patched instruction decoded, each multiplier followed to the value it loads.
Controls: the control ROM as "shipped" (layer 2 must fail every card), each edit reverted one at a time (layer 1 must
fail), one stray byte (layer 1), and a wrong pin (layer 2).
"""
import json, struct, sys
from pathlib import Path

GBA = 0x08000000
EXPECT = {"seaglass": 60, "lazarus": 60, "spirits": 61, "dreamstone": 60}      # pinned 2026-11-25 (round 2)
# move table (address, stride) and move ids (same ids in all four)
MT = {"seaglass": (0x086D29E0, 56), "lazarus": (0x088CFAC8, 52), "spirits": (0x0866F270, 48), "dreamstone": (0x08759858, 48)}
MID = dict(doubleedge=38, takedown=36, astonish=310, extrasensory=326, needlearm=302, phantomforce=566, stomp=23, tackle=33,
           growl=45, sing=47, hypervoice=304)
RECOIL = {"seaglass": ("u32", 20, 4, 7), "lazarus": ("u32", 20, 4, 7), "dreamstone": ("u32", 20, 4, 7), "spirits": ("u8", 28)}
BITS = {"seaglass": dict(sound=(23, 5), bypass=(25, 5), minimize=(24, 4)),
        "lazarus": dict(sound=(23, 5), bypass=(25, 5), minimize=(24, 4)),
        "dreamstone": dict(sound=(23, 4), bypass=(25, 4), minimize=(24, 3)),
        "spirits": dict(sound=(22, 5), bypass=(24, 5), minimize=(23, 4))}
NMOVES = 834
# hand-pinned code sites (from the 2026-11-25 generator run, each re-read by hand in the disassembly)
SITES = {
    "seaglass": dict(contact=[0x080C3084, 0x080C31D4, 0x080C31F2, 0x080C2E7C], ate=0x080CD16C,
                     protect=[0x080A0234, 0x080A9884], pb=(0x080CBC3C, 0x080CBC46), snow=None),
    "lazarus": dict(contact=[0x080C4D68, 0x080C45A4, 0x080C45C4, 0x080C4E1E], ate=0x080CE176,
                    protect=[0x080A11B0, 0x080AA6F4], pb=(0x080CCBCA, 0x080CCBD4), snow=None),
    "spirits": dict(contact=[0x080C3868, 0x080C3A3A, 0x080C3A8A, 0x080C36E6], ate=0x080C6BA0,
                    protect=None, pb=(0x080C5AEA, 0x080C5AF6), snow=(0x080C41D8, 0x080C41E6)),
    "dreamstone": dict(contact=[0x080C4588, 0x080C46D0, 0x080C46F2, 0x080C49C4], ate=0x080C9080,
                       protect=None, pb=(0x080C7876, 0x080C7880), snow=(0x080C369E, 0x080C36AC)),
}

# round 2 (2026-11-25): one list per card, meaning per card in meaning() below
SITES2 = {
    "seaglass": {"crash": [0x080A07AA], "transistor": [0x080CD35A, 0x080CD0A0], "brick_break": [0x080A60C8], "payback": [0x080CB844], "gale_wings": [0x08084EB2], "intimidate": [0x0826B144], "leaf_guard": [0x08267C27], "parting_shot": [0x0826603A], "heal_bell": [0x080A37A2, 0x080A37B2], "protean": [0x0808F1C2], "disguise": [0x0826A945]},
    "lazarus": {"crash": [0x080A1722], "transistor": [0x080CE2DC, 0x080CE13E], "brick_break": [0x080A719C], "payback": [0x080CC800], "gale_wings": [0x08086088], "intimidate": [0x08289F86], "leaf_guard": [0x08286A2C], "parting_shot": [0x08284ECF], "heal_bell": [0x080A4822, 0x080A4832], "protean": [0x0809053C], "disguise": [0x0828975E]},
    "spirits": {"crash": [0x080978B6], "transistor": [0x080C6860, 0x080C6856], "brick_break": [0x0808662C], "destiny_bond": [0x080BCCEC], "payback": [0x080C6DA4], "gale_wings": [0x0807B822, 0x0807B8B0], "intimidate": [0x0809FAD6, 0x0809FB08], "leaf_guard": [0x08255438], "parting_shot": [0x08253C3C], "heal_bell": [0x0808DEDE, 0x0808DF22], "dauntless_intrepid": [0x080C4602, 0x080C3DEC], "protean": [0x080B741A], "disguise": [0x08257C69]},
    "dreamstone": {"crash": [0x08099C80], "transistor": [0x080C8BF4, 0x080C8C0C], "brick_break": [0x080852E2], "destiny_bond": [0x080C0D8C], "payback": [0x080BBB22], "gale_wings": [0x08079E6C], "intimidate": [0x080A2802, 0x080A2834], "leaf_guard": [0x08266FBB], "parting_shot": [0x082654A4], "heal_bell": [0x0808D1BC, 0x0808D200], "dauntless_intrepid": [0x080C395E, 0x080C3E52], "protean": [0x080B74C2], "disguise": [0x08269B69]},
}


def u16(r, a): return struct.unpack_from("<H", r, a - GBA)[0]
def u32(r, a): return struct.unpack_from("<I", r, a - GBA)[0]


def lit(r, a):
    h = u16(r, a)
    assert h >> 11 == 0b01001, "%#x: not ldr pc (%04x)" % (a, h)
    return u32(r, ((a + 4) & ~3) + (h & 0xFF) * 4)


def bl(r, a):
    hi, lo = u16(r, a), u16(r, a + 2)
    if hi >> 11 != 0b11110 or lo >> 11 != 0b11111:
        return None
    off = ((hi & 0x7FF) << 12) | ((lo & 0x7FF) << 1)
    return a + 4 + (off - (1 << 23) if off & (1 << 22) else off)


def meaning(h, r):
    """{card: ok?} decoded from the ROM. True = the card's behaviour is present."""
    T, S = MT[h]; rec = lambda m: T + S * MID[m]
    out = {}
    k = RECOIL[h]
    de = (u32(r, rec("doubleedge") + k[1]) >> k[2]) & ((1 << k[3]) - 1) if k[0] == "u32" else r[rec("doubleedge") + k[1] - GBA]
    td = (u32(r, rec("takedown") + k[1]) >> k[2]) & ((1 << k[3]) - 1) if k[0] == "u32" else r[rec("takedown") + k[1] - GBA]
    out["Double-Edge 1/4 recoil"] = de == 25 and td == 25
    mb, mbit = BITS[h]["minimize"]
    bit = lambda m, b: r[rec(m) + b[0] - GBA] >> b[1] & 1
    out["Astonish/Extrasensory/Needle Arm/Phantom Force punish Minimize"] = all(
        bit(m, (mb, mbit)) for m in ("astonish", "extrasensory", "needlearm", "phantomforce")) and not bit("tackle", (mb, mbit))
    sb, bb = BITS[h]["sound"], BITS[h]["bypass"]
    snd = [i for i in range(1, NMOVES) if r[T + S * i + sb[0] - GBA] >> sb[1] & 1]
    out["sound moves stopped by Substitute"] = len(snd) >= 25 and all(bit(m, sb) for m in ("growl", "sing", "hypervoice")) \
        and not any(r[T + S * i + bb[0] - GBA] >> bb[1] & 1 for i in snd)
    s = SITES[h]
    out["Static/Flame Body/Poison Point/Cute Charm 1/3"] = all(u16(r, a) == 0x2169 and u16(r, a + 2) == 0x2202 for a in s["contact"]) \
        or all(u16(r, a) == 0x2169 and any(u16(r, a + d) == 0x2202 for d in (2, 4, 6)) for a in s["contact"])
    a = s["ate"]
    if u16(r, a) >> 11 == 0b01001:
        v = lit(r, a)
    else:
        t = bl(r, a); v = lit(r, t) if t else None
    out["-ate 1.3x"] = v in (0x14CC, 0x14CD)
    if s["protect"]:
        ok = True
        for p in s["protect"]:
            t = u32(r, p)
            tbl = struct.unpack_from("<16H", r, t - GBA)
            ok &= tbl == (0xFFFF, 0x7FFF, 0x3FFF) + (0x1FFF,) * 13
        out["Protect 1/8 floor"] = ok
    m, l = s["pb"]
    out["Parental Bond 50%"] = u16(r, m) & 0xF8FF == 0x2080 and (u16(r, l) >> 6) & 0x1F == 4
    if s["snow"]:
        mv, ld = s["snow"]
        sc = lit(r, ld)
        out["Snow Warning sets Hail"] = u16(r, mv) == 0x2106 and r[sc - GBA + 12:sc - GBA + 15] == bytes([0x45, 0x07, 0x0C])
    # ---- round 2
    S2 = SITES2[h]
    bt = lambda a: (a + 4 + 2 * (((u16(r, a) & 0x7FF) ^ 0x400) - 0x400)) if u16(r, a) >> 11 == 0b11100 else \
        (a + 4 + 2 * (((u16(r, a) & 0xFF) ^ 0x80) - 0x80)) if u16(r, a) >> 12 == 0xD else None
    nop = lambda a: u16(r, a) == 0x46C0
    p32 = lambda a: u32(r, a) if a % 4 == 0 else struct.unpack_from("<I", r, a - GBA)[0]
    if h in ("seaglass", "lazarus"):
        out["HJK/JK crash 1 HP"] = u16(r, S2["crash"][0]) == 0x2001 and u16(r, S2["crash"][0] + 2) == 0x2001
        out["Transistor 1.5x"] = bt(S2["transistor"][0] + 6) == S2["transistor"][1] and u16(r, S2["transistor"][1] + 4) == 0x02DB
        out["Intimidate Gen VII"] = all(p32(S2["intimidate"][0] + 8 * i + 4) == S2["intimidate"][0] + 8 * (i + 1) for i in range(4))
        lg = 3
    else:
        out["HJK/JK crash 1 HP"] = u16(r, S2["crash"][0]) == 0x2001
        m = S2["transistor"][1]
        out["Transistor 1.5x"] = bt(S2["transistor"][0] + 2) == m and u16(r, m) & 0xF8FF == 0x20C0 and (u16(r, m + 2) >> 6) == 5
        out["Destiny Bond no fail"] = u32(r, S2["destiny_bond"][0]) == 0x47702000
        out["Intimidate Gen VII"] = all(nop(a) for a in S2["intimidate"])
        out["Dauntless Shield / Intrepid Sword every switch-in"] = all(nop(a) for a in S2["dauntless_intrepid"])
        lg = 6 if h == "spirits" else 3
    out["Brick Break through immunity"] = u16(r, S2["brick_break"][0]) & 0xF8FF == 0x2000
    out["Payback doubles on switch"] = nop(S2["payback"][0])
    out["Gale Wings any HP"] = all(nop(a) or u16(r, a) >> 11 == 0b11100 for a in S2["gale_wings"])
    out["Leaf Guard lets Rest work"] = p32(S2["leaf_guard"][0] + lg) == S2["leaf_guard"][0] + lg + 4
    out["Parting Shot always switches"] = p32(S2["parting_shot"][0] + 14) == S2["parting_shot"][0] + 18
    lp, pt = S2["heal_bell"]
    out["Heal Bell cures Soundproof"] = u16(r, lp) >> 11 == 0b11100 and nop(pt)
    out["Protean / Libero every move"] = nop(S2["protean"][0])
    out["Disguise no HP loss"] = p32(S2["disguise"][0] + 4) == S2["disguise"][0] + 8
    return out


DEFAULT = "lazarus"         # repo copies set their hack here, so `python3 tools/tests/check_behaviour.py` runs with no args


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a and DEFAULT:
        a = [DEFAULT, str(Path(__file__).resolve().parents[2])]
    h, root = a[0], Path(a[1])
    sys.path.insert(0, str(root / "tools"))
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))   # expansion-kit keeps bpatch in kit/tools
    import bpatch
    shipped = bytearray(Path(a[2] if len(a) > 2 else root / "build" / ("%s_cm.gba" % h)).read_bytes())
    control = bytearray(Path(a[3] if len(a) > 3 else root / "build" / ("%s_cm_nobeh.gba" % h)).read_bytes())
    cards = bpatch.load(root / "tools" / "character_mode" / "behaviour_cards.json")
    rc = 0
    bad = bpatch.verify(shipped, control, cards)
    n = len(cards["edits"])
    if n != EXPECT[h]:
        bad.append("edit count %d, want %d" % (n, EXPECT[h]))
    for b in bad[:20]:
        print("FAIL bytes:", b)
    print("bytes layer: %d edits, %d failures (want 0)" % (n, len(bad)))
    rc |= bool(bad)
    m = meaning(h, shipped)
    for k, v in m.items():
        print("%s %s" % ("PASS" if v else "FAIL", k))
    rc |= not all(m.values())
    print("meaning layer: %d/%d cards present" % (sum(m.values()), len(m)))
    # ---- controls (each must fail) ----
    ok = 0; want = 0
    mc = meaning(h, control)
    want += 1
    if not any(mc.values()):
        ok += 1
    else:
        print("CONTROL FAIL: control ROM shows cards", [k for k, v in mc.items() if v])
    for e in cards["edits"]:
        t = bytearray(shipped); o = int(e["addr"], 16) - GBA; f = bytes.fromhex(e["from"])
        t[o:o + len(f)] = f
        want += 1
        if bpatch.verify(t, control, cards):
            ok += 1
        else:
            print("CONTROL FAIL: reverted edit not caught", e["card"], e["addr"])
    t = bytearray(shipped); t[0x00100000] ^= 1; want += 1
    if bpatch.verify(t, control, cards):
        ok += 1
    else:
        print("CONTROL FAIL: stray byte not caught")
    s0 = dict(SITES[h]); SITES[h] = dict(s0, pb=(s0["pb"][0] + 2, s0["pb"][1])); want += 1
    if not meaning(h, shipped)["Parental Bond 50%"]:
        ok += 1
    else:
        print("CONTROL FAIL: wrong pin not caught")
    SITES[h] = s0
    print("negative controls: %d/%d" % (ok, want))
    rc |= ok != want
    print("ALL PASS" if not rc else "FAILED")
    return rc


if __name__ == "__main__":
    sys.exit(main())
