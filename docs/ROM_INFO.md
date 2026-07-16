# ROM_INFO — Pokemon Lazarus v2.0

## Identity

| Field | Value |
|---|---|
| File | `rom/lazarus-v2.gba` (gitignored, chmod 444) |
| Size | 33,554,432 bytes (32 MiB — expanded from vanilla Emerald's 16 MiB) |
| SHA1 | `7dcdc7e280bc4631487e13dd37e6e0cea04adea6` (pinned in `rom.sha1`) |
| Header title | `POKEMON EMER` |
| Game code | `BPEE` (Pokemon Emerald USA/Europe) |
| Author | Nemo622 (also author of Emerald Seaglass — same private pokeemerald-expansion stack) |
| Version | v2.0 (current as of 2026-07; original v1.0 released 2025-03-21) |
| Source | Closed. No public repo. Distribution = BPS patch via Nemo622's Ko-fi. |

## Provenance chain (verified 2026-07-15, read-only)

1. `../Lazarus_Docs/README.txt` instructs patching a "Pokemon Emerald TrashMan ROM" with the official BPS.
2. `../Lazarus_Docs/Lazarus v2 Patch.bps` footer: **source CRC32 `0x1F1C08FB`** = the well-known clean Emerald (U) dump CRC; **target CRC32 `0x558AE42F`**.
3. `../lazarus-v2.zip` central directory: stored CRC32 for `lazarus-v2.gba` = `558ae42f` — **exact match** with the BPS target CRC.
4. Extracted ROM SHA1 matches the pin above.

Conclusion: `rom/lazarus-v2.gba` is provably the byte-exact output of applying the official v2 patch to clean Emerald.

## Distribution rule

Our shipped patch (`build/lazarus_cm.bps`) is created **against `lazarus-v2.gba`**, never against clean Emerald (that would embed and redistribute Nemo622's entire hack). End-user chain: clean Emerald → official Lazarus BPS → our Character Mode BPS.
