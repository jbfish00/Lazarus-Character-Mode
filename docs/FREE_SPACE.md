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

## Hook trampolines and veneers as built (2026-10-30)

The tail is out of BL reach, so every BL-hooked site jumps through an 8-byte `ldr r3,[pc,#0]; bx r3; .word target|1`
near it. ⚠️ The first trampolines (2026-07) sat in "0xFF runs" at `0x08470A5A` / `0x0847125A` that were pixels of a
trainer back sprite; a run of 0xFF is not free unless nothing points at it (rowe_parity.md §13.53).

| address | what lives there | why it is free |
|---|---|---|
| `0x081DD61C` +0 / +8 / +16 / +24 / +32 | catch + gift gate, wild gate, encounter marker, PC second guard, link-trade sweep | the standalone IsRemovingLastPartyMon: inlined at all 5 call sites, no BL caller, no pointer (verify §17) |
| `0x081DD644` | 100% catch veneer | the same function's tail + pool; nothing points, BLs or pc-loads into `0x081DD640..0x081DD653` (verify §20) |
| `0x081DD64C` | EXP rate veneer (getexp BL `0x0809562E`) | the last 8 bytes of that pool (verify §24). **The block is now full.** |
| `0x081183B8` | overworld sprite entry trampoline | GetObjectEventGraphicsInfo's own first 8 bytes, replayed by the hook |

Patched in place, no trampoline: SetDefaultOptions `0x08189612`, MoveBattleBar `0x0807D5E8`, the START menu builder
tail `0x0821B5D8` and input handler `0x0821BE54` (EXP rate). Data in the tail is listed by the injector's `*_ADDR`
constants; `splice()` asserts each lands on 0xFF and overlaps nothing else.
