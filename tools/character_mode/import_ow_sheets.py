#!/usr/bin/env python3
"""Vendor the player-grade overworld sheets this repo's characters use (2026-10-21).

Ported from Seaglass's tool of the same name. The sheets are the pokeemerald
player layout (stand and walk in frames 0-8, run frames 9-17, 4bpp + one
16-colour palette each) that Radical Red, Unbound, Seaglass and ROWE2 ship: ROWE's
built overworld art plus the generated sheets of ../game_plans/ow_generated. This
copies the ones whose character is in this repo's characters_manifest.json into
sprites/ow_player/, with a manifest holding only those, so the build never reads
outside this repo.

Sources are ARGUMENTS, never literal sibling paths (check_repo_selfcontained.py):

    python3 tools/character_mode/import_ow_sheets.py <source sprites/ow_player dir> \
        [--override Name=<path to sheet stem>:<W>x<H> ...]

--override replaces one character's sheet with <stem>.4bpp/.gbapal/.png (used
2026-10-21 for Lysandre: the newest ../game_plans/ow_generated/base_edit/lysandre.*,
32x32, while the sibling repos' copies were being edited).
"""
import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "sprites" / "ow_player"
CHAR_MANIFEST = ROOT / "tools" / "character_mode" / "characters_manifest.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--override", action="append", default=[])
    a = ap.parse_args()
    src = Path(a.src)
    m = json.loads((src / "manifest.json").read_text())
    names = {c["character"] for c in json.loads(CHAR_MANIFEST.read_text())["characters"]}
    keep = {n: dict(e) for n, e in m["characters"].items() if n in names}
    over = {}
    for o in a.override:
        name, rest = o.split("=", 1)
        stem, size = rest.rsplit(":", 1)
        w, h = (int(x) for x in size.lower().split("x"))
        assert name in names, f"--override {name}: not a character here"
        over[name] = (Path(stem), w, h)
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    for n, e in keep.items():
        if n in over:
            continue
        for ext in (".4bpp", ".gbapal", ".png"):
            shutil.copy2(src / f"{e['stem']}{ext}", DEST / f"{e['stem']}{ext}")
    for n, (stem, w, h) in over.items():
        out = "ovr_" + stem.name
        gfx = Path(str(stem) + ".4bpp").read_bytes()
        assert len(gfx) == 18 * w * h // 2, (n, len(gfx), w, h)
        for ext in (".4bpp", ".gbapal", ".png"):
            shutil.copy2(Path(str(stem) + ext), DEST / f"{out}{ext}")
        keep[n] = {"stem": out, "width": w, "height": h, "origin": "override",
                   "override_source": str(stem.name)}
    out = {"source": m["source"], "frames": m["frames"], "count": len(keep),
           "characters": dict(sorted(keep.items()))}
    (DEST / "manifest.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"{len(keep)} sheets -> {DEST.relative_to(ROOT)} ({len(over)} override)")


if __name__ == "__main__":
    main()
