#!/usr/bin/env python3
"""Print `export` lines for cm_ow_sprite_test.lua, and write the expected art.

The 18 frames + 32-byte palette come from the SOURCE sheet (sprites/ow_player/).
For Lazarus's own costumes (Ethan, Lyra, Calem, Serena, Elio, Selene) the
expected images table comes from that outfit's on-foot graphics info in the
BASE ROM -- never from the built ROM, so the live test cannot agree with the
build by construction.

Usage: eval "$(python3 tools/tests/ow_sprite_env.py <character name>)"
"""
import os
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "character_mode"))
import lazarus_ow_player as owp  # noqa: E402

name = sys.argv[1]
out = os.environ.get("CM_OW_EXPECT", "/tmp/lz_ow_expect.bin")
sheets = owp.sheets()
if name in owp.NATIVE:
    base = (ROOT / "rom" / "lazarus-v2.gba").read_bytes()
    outfit, gender = owp.NATIVE[name]
    gid = next(i for k, g, i in owp.outfit_on_foot(base) if (k, g) == (outfit, gender))
    info = owp.info_ptr(base, gid)
    images, = struct.unpack_from("<I", base, owp.R(info) + 0x1C)
    Path(out).write_bytes(bytes(18 * 256 + 32))   # unused: the images table is asserted
    print(f"export CM_OW_EXPECT={out} CM_OW_FRAME_BYTES=256 CM_OW_NATIVE_IMAGES={images:#x}")
elif name in sheets:
    e = sheets[name]
    fb = e["width"] * e["height"] // 2
    frames = (owp.SHEETS / f"{e['stem']}.4bpp").read_bytes()
    pal = (owp.SHEETS / f"{e['stem']}.gbapal").read_bytes()
    Path(out).write_bytes(frames + pal)
    print(f"export CM_OW_EXPECT={out} CM_OW_FRAME_BYTES={fb}")
    print("unset CM_OW_NATIVE_IMAGES")
else:
    sys.exit(f"ow_sprite_env: {name} has no overworld sprite")
