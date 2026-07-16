#!/usr/bin/env python3
"""Dump the Lazarus gSpeciesInfo-analogue name table to rom_species_table.json.

Shape (verified by probe): struct array, 212-byte stride, name field first,
indexed by SPECIES id (natdex order for base species in this expansion
snapshot). Base found empirically from title-case name hits:
    name_addr = 0x00C7A364 + 212 * species_id
(Fennekin=653, Litten=725, Rowlet=722, Pikachu=25, Sprigatito=1289 all land.)

Emits the same JSON format Seaglass's pipeline consumes:
    {"base": ..., "stride": ..., "entries": [{"index": i, "name": "..."}, ...]}
Only entries with a plausible decoded name are included (pruned species may
be blank / "??????").
"""
import json
import sys

ROM = sys.argv[1] if len(sys.argv) > 1 else "rom/lazarus-v2.gba"
OUT = sys.argv[2] if len(sys.argv) > 2 else "tools/character_mode/rom_species_table.json"
BASE = 0x00C7A364
STRIDE = 212
NAME_LEN = 16  # read window; names are 0xFF-terminated well before this

def decode(b):
    out = []
    for c in b:
        if c == 0xFF:
            break
        if 0xBB <= c <= 0xD4:
            out.append(chr(ord('A') + c - 0xBB))
        elif 0xD5 <= c <= 0xEE:
            out.append(chr(ord('a') + c - 0xD5))
        elif 0xA1 <= c <= 0xAA:
            out.append(chr(ord('0') + c - 0xA1))
        elif c == 0x00:
            out.append(' ')
        elif c == 0xB0:
            out.append('…')
        elif c == 0xAC:
            out.append('?')
        elif c == 0xAE:
            out.append('-')
        elif c == 0xB4:
            out.append("'")
        elif c == 0xB5:
            out.append('♂')
        elif c == 0xB6:
            out.append('♀')
        elif c == 0xBA:
            out.append('.')  # e.g. Mr. Mime
        elif c == 0x1B:
            out.append('é')  # Flabébé
        else:
            return None  # unknown byte -> not a clean name
    return ''.join(out)

# True table end verified empirically: last real entry is index 1560
# (Golisopod, end of the forms block); garbage decodes appear past it.
MAX_INDEX = 1560

rom = open(ROM, 'rb').read()
entries = []
i = 0
while i <= MAX_INDEX:
    off = BASE + STRIDE * i
    if off + NAME_LEN > len(rom):
        break
    name = decode(rom[off:off + NAME_LEN])
    if name is not None and name.strip('? ') != '' and len(name) > 0:
        entries.append({"index": i, "name": name, "name_offset": off})
    i += 1

last = entries[-1]["index"] if entries else -1
print(f"Scanned {i} slots; {len(entries)} named entries; last named index {last}")
for e in entries[:5] + entries[-5:]:
    print(f"  [{e['index']:5d}] {e['name']}")
# Same schema Seaglass's map_species_stage_b.py consumes ("species": {idx: name});
# blank/pruned slots are simply absent.
import hashlib
sha1 = hashlib.sha1(rom).hexdigest()
json.dump({"rom_sha1": sha1, "table_base_offset": BASE, "stride_bytes": STRIDE,
           "table_end_index": MAX_INDEX,
           "species": {str(e["index"]): e["name"] for e in entries}},
          open(OUT, 'w'), indent=1)
print(f"Wrote {OUT}")
