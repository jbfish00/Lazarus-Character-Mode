# FREE_SPACE — Lazarus v2.0 (audited 2026-07-15)

Tool: `tools/scan_free_space.py` against pinned `rom/lazarus-v2.gba`.

## 0xFF runs (reliable free space)

Exactly **one** contiguous run ≥ 0x400:

| ROM offset | Length | Notes |
|---|---|---|
| `0x015F0EA4` | 10,547,548 B (**10.06 MiB**) | Runs to EOF (32 MiB ROM). Primary injection target. |

## 0x00 runs (UNRELIABLE — may be real data padding; use only as last resort)

51 runs ≥ 0x1000 totaling 0.58 MiB; largest `0x00E89A68` (69.5 KiB), `0x00536899` (55 KiB). Standing rule from Seaglass: do not treat 0x00 runs as free without proving nothing references the region.

## BL reachability constraint

Thumb `BL` reaches ±4 MiB. The free tail starts at ~22.9 MiB; vanilla-derived code lives in the low megabytes — **direct BL from low-ROM hook sites into the free tail is impossible.**

Plan (RR-proven): hook sites get a tiny **trampoline** placed nearby (small local slack — e.g. alignment padding near the hook, or a 0x00-run vetted as truly free) that performs an absolute jump (`ldr pc, [pc]` + literal) into the main shim in the free tail. Alternatively the shim's entry veneer uses `BX` via register. Data blobs (characters/rosters/names/bitmaps) have no reachability constraint — they're accessed via absolute pointers — so all data goes straight into the `0x015F0EA4` tail.

Decision deferred to Phase 4 once hook addresses are known; record chosen trampoline sites here when made.
