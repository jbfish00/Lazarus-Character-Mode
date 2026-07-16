#!/usr/bin/env python3
"""Locate the gScriptCmdTable-equivalent in a pokeemerald(-expansion) binary hack.

Signature (from donor source, script.c ScriptContext init):
    ctx->cmdTable    = gScriptCmdTable;
    ctx->cmdTableEnd = gScriptCmdTableEnd;
compiles to two literal-pool loads whose pool words sit CONSECUTIVELY in ROM:
    [A]   = table start (ROM address)
    [A+4] = table end   (ROM address, = start + 4*numCmds)
and the table itself is a dense run of odd (Thumb) ROM function pointers.

We scan for such adjacent word pairs, validate the pointed-to run, and report.
This doubles as XREF evidence: the literal-pool pair's own offset is where the
script engine references the table.
"""
import argparse
import struct
import sys

ROM_BASE = 0x08000000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom")
    ap.add_argument("--min-cmds", type=int, default=0x80,
                    help="minimum command count (vanilla emerald ~0xE2)")
    ap.add_argument("--max-cmds", type=int, default=0x400)
    args = ap.parse_args()

    data = open(args.rom, "rb").read()
    n = len(data)
    words = struct.unpack(f"<{n // 4}I", data[: n // 4 * 4])

    rom_lo, rom_hi = ROM_BASE, ROM_BASE + n

    def is_thumb_ptr(v):
        return rom_lo <= v < rom_hi and (v & 1) == 1

    # candidate tables keyed by start addr -> (count, [pair pool offsets])
    tables = {}
    for i in range(len(words) - 1):
        a, b = words[i], words[i + 1]
        if not (rom_lo <= a < b < rom_hi):
            continue
        if (b - a) % 4:
            continue
        cnt = (b - a) // 4
        if not (args.min_cmds <= cnt <= args.max_cmds):
            continue
        # validate the run [a, b) is all Thumb pointers
        s = (a - ROM_BASE) // 4
        e = (b - ROM_BASE) // 4
        if e > len(words):
            continue
        run = words[s:e]
        if all(is_thumb_ptr(v) for v in run):
            tables.setdefault(a, [cnt, []])
            tables[a][1].append(i * 4)

    if not tables:
        print("No candidates found.")
        sys.exit(1)

    for a, (cnt, pools) in sorted(tables.items()):
        s = (a - ROM_BASE) // 4
        run = words[s : s + cnt]
        uniq = len(set(run))
        print(f"table @ 0x{a:08X}  cmds={cnt} (0x{cnt:X})  unique_handlers={uniq}")
        print(f"  literal-pool pair refs at ROM offsets: "
              + ", ".join(f"0x{p:08X}" for p in pools))
        # print a few interesting entries
        for idx in (0x00, 0x1B, 0x23, 0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x79):
            if idx < cnt:
                print(f"  entry[0x{idx:02X}] = 0x{run[idx]:08X}")
        print()


if __name__ == "__main__":
    main()
