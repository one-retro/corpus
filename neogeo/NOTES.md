# Neo Geo (AES / MVS cartridges)

Ten games, three runnable libretro cores. 26 of 30 (game, core) runs were filed. The four that
were not are FB Alpha 2012 in AES mode, where the core has no memory card and AES has no backup
RAM, so it writes nothing at all. Three FB Alpha 2012 Neo Geo saves were downloaded besides. No
MiSTer or Analogue Pocket save was found online. The cores disagree on almost everything about
the files: names, subdirectories, byte order, headers, compression, and even on how big a memory
card is.

## Where the ROMs and BIOS came from, and how games are named

- FinalBurn Neo and FB Alpha 2012 used the FBNeo romset (`Neo Geo AES - MVS/Final Burn Neo
  romset/<short>.zip`). The romset's own `neogeo.zip`, which also holds the AES BIOSes, was linked
  beside the ROM and into the system directory.
- Geolith used the drive's `Geolith romset/NEO files/*.neo`. Each one's CRC matches the
  LunaGarlic list in Geolith's `rename-neo.sh`. It was linked as `<mame short name>.neo`, the name
  `rename-neo.sh` gives it, so its saves are named `mslugx.mcr` and so on. Its BIOS was `aes.zip`
  from the library's `BIOS/` folder, plus the FBNeo `neogeo.zip` for MVS.
- Each game's directory is the MAME/FBNeo short name (`mslugx`). There is no No-Intro name for
  arcade sets, and the short name is what FBNeo and MAME name their files after.
- Nothing was copied. `.cache/roms/neogeo/` holds symlinks to the drive, because the disk is full.

## The ten games

| Game (short name) | Mode | Save hardware exercised | Why | Proof |
| --- | --- | --- | --- | --- |
| Metal Slug X (`mslugx`) | AES | card: "METAL SLUG X OPTION", NGH 0250 sub 1, 1 block | popular; leaving the title's OPTION menu saves to the card | OPTION shows DIFF. HARD after a power cycle |
| Fatal Fury 2 (`fatfury2`) | AES | card: NGH 0047, 1 block | MiSTer reference exists for the same game | CARD LOAD OK? after a power cycle |
| Samurai Shodown (`samsho`) | AES | card: NGH 0045, 1 block | the brief's example; "CARD SAVE OK ?" at game over | CARD LOAD OK ? |
| Samurai Shodown II (`samsho2`) | AES | card: NGH 0063, 1 block | "GAME DATA SAVE" at game over | GAME DATA LOAD |
| Puzzle Bobble (`pbobblen`) | MVS | backup RAM + card ("BUST A MOVE R=01", NGH 0083) | MVS game that saves to a card | CARD LOAD after a power cycle |
| Blazing Star (`blazstar`) | MVS | backup RAM (high-score name "AAAAAAAAA", 30th) + card (NGH 0239) | high-score entry kept in backup RAM | CARD SAVE OK? > YES ... SAVE OK |
| League Bowling (`lbowling`) | MVS | backup RAM + card ("BOWLING 1P", NGH 0019, **2 blocks**) | a save that needs no input: the MEMORY CARD SAVE timer runs out on YES | MEMORY CARD LOAD |
| Baseball Stars 2 (`bstars2`) | MVS | backup RAM + card ("BASEBALL STARS 2 COM", NGH 0041, **4 blocks**) | the largest card save; the pennant race is saved after TIME UP | MEMORY CARD LOAD OK ? |
| Jockey Grand Prix (`jockeygp`) | MVS | backup RAM + **8 KiB battery RAM on the cartridge** | one of only two carts with their own RAM | CREDIT 000002 after a power cycle |
| The King of Fighters '98 (`kof98`) | MVS, setting mode | backup RAM: soft DIPs (cabinet CONTINUE 2 COINS = 1 CREDIT; KOF'98 PLAY TIME LITTLE FAST, CONTINUE OFF) | the MVS BIOS's own settings, per slot | the soft-DIP page read back after a power cycle |

Scripts are in `scripts/neogeo/`. AES-mode games use the `*-aes.opt` files and MVS-mode games
use `*-mvs.opt`. `kof98` uses `*-mvs-setting.opt`, which turns on the MVS setting-mode DIP:
`geolith_settingmode = on`, `fbneo-dipswitch-kof98-Setting_mode = On`, and
`fbalpha2012_dipswitch_kof98_Setting_mode = On`. Every script runs from power-on. "Power cycle"
in a script means `retro_reset`: the proof shows the game reading the save back from memory,
not from the file.

Game-specific notes:
- On FBNeo and Geolith, Fatal Fury 2's "CARD SAVE OK?" prompt is up from frame ~7560 to ~7840.
  On both, Samurai Shodown's is up from ~11970 to ~12500 and Samurai Shodown II's from ~9210 to
  ~9790. All three default to NO, so the scripts press up, then A.
- Puzzle Bobble's and Blazing Star's play is seeded by the MVS clock, so their scripts keep
  pressing up/A on a cadence that covers every run. FBNeo and Geolith reached "SAVE OK" in
  Blazing Star on the same frame.
- Neo Geo A is RetroPad **b** and B is RetroPad **a** in all three cores. Coin is select.
  FBNeo's default "Diagnostic Input" is "Hold Start", so no script holds START for long.

## How to get a memory card in each core (the brief asked for this)

| Core | Card | Option / key | File |
| --- | --- | --- | --- |
| finalburn-neo | **off by default** | `fbneo-memcard-mode = per-game` (or `shared`) | `fbneo/<short>.memcard` (or `fbneo/shared.memcard`), written at unload |
| geolith | on by default | `geolith_memcard` (on/off), `geolith_memcard_wp` (write protect) | `<rom stem>.mcr` in the save dir, written at unload whether used or not |
| fb-alpha (FB Alpha 2012) | **none**: the libretro port never inserts one | none | none |
| neogeo-mister | always | none | inside the 73728-byte `.sav` |

When a game first writes to a blank card, the BIOS behaves differently in each mode:
- **AES BIOS (FBNeo):** shows "MEMORY CARD NOT FORMATTED. A BUTTON = YES / B BUTTON = NO", and
  the AES scripts press A. FBNeo's card starts all zero.
- **MVS BIOS:** formats the card without asking.
- **Geolith:** its card comes **pre-formatted**, so no prompt appears.

## Games x cores

| Game | finalburn-neo | geolith | fb-alpha |
| --- | --- | --- | --- |
| mslugx (AES) | filed: card | filed: card | **failed**: no card, no NVRAM in AES mode, nothing written |
| fatfury2 (AES) | filed: card | filed: card | failed (same) |
| samsho (AES) | filed: card | filed: card | failed (same) |
| samsho2 (AES) | filed: card | filed: card | failed (same) |
| pbobblen | filed: .fs + card | filed: .nv + card | filed: .fs (no card, so no CARD prompts) |
| blazstar | filed: .fs + card | filed: .nv + card | filed: .fs (no card) |
| lbowling | filed | filed | filed: .fs (no card) |
| bstars2 | filed | filed | filed: .fs (no card) |
| jockeygp | filed: .fs 72 KiB + blank card | filed: .nv + .srm + blank card | filed: .fs |
| kof98 | filed: .fs + blank card | filed: .nv + blank card | filed: .fs |

Every proof.png was checked on one tiled sheet. Core builds: FinalBurn Neo v1.0.0.03 da14132,
Geolith 0.5.0, FB Alpha 2012 v0.2.97.29 0ce3153.

| Core not runnable here | Status |
| --- | --- |
| neogeo-mister | Played on the owner's MiSTer since: 5 entries, see the last section below. (Before that: nothing found online; one-saves' 8 MiSTer saves were the reference) |
| mazamars312-neogeo | Nothing found (77 issues, 185 comments; users mention old saves causing "File ID [257] too large", but none attached one). Other workers have filed device backups under `mazamars312-neogeo/` and `_Mazamars312.NeoGeo_Overdrive/`; I left them alone. From the core's data.json and RTL: the card is slot 0x101, `<game>.sav`, at most 8192 bytes; the backup RAM is slot 0x102, one shared `backup.bak`, at most 65536 bytes. The RTL passes the bridge's 32-bit words through unswapped, so the byte order depends on the bridge's endianness (unverified) |
| finalburn-neo-neogeo-subset | Built from source since: all ten filed with the same options (BUILT-CORES.md) |

## How each core writes the files

| | finalburn-neo | geolith | fb-alpha (2012) | neogeo-mister (reference) |
| --- | --- | --- | --- | --- |
| MVS backup RAM | `fbneo/<short>.fs`, **65536**, raw, every 16-bit word **byte-swapped** (`ABKCPUR MAO  K.!` at 0x10) | `<stem>.nv`, **65536**, 68000 byte order (`BACKUP RAM OK !` at 0x10) | `<short>.fs` in the save dir **root**, a **compressed state**: `FB1 FS1 ` header, chunk size, version 0x00029730 / min 0x00029713, the set name, then zlib (78 9C). Decompresses to 65536, byte-swapped like FBNeo. 356-1836 bytes on disk | first 64 KiB of the `.sav`, byte-swapped words |
| AES mode | no `.fs` at all | no `.nv` | nothing written | (same container) |
| Cartridge RAM (Jockey GP) | appended to the `.fs`: **73728** = 64 KiB + 8 KiB | separate **`<stem>.srm`, 8192**, 68000 order (`JOCKEY GRANDPRIX INIT KEY DATA04` at 0x14), written by the core itself, not via RETRO_MEMORY_SAVE_RAM (which is NULL in cartridge mode) | inside the state: decompresses to 73728 | in place of the card region (see one-saves README) |
| Memory card | `fbneo/<short>.memcard`: a 32-byte header `FB1 FC1 `, u32 chunk size (LE), u32 FBNeo version 0x00100003, u32 min version 0x00029713, 12 zero bytes; then the card with **each byte in the odd half of a 16-bit word** (even bytes 0x00) | `<stem>.mcr`, **2048**, bare card bytes | none | 8 KiB region at 0x10000, word-swapped |
| Card size the BIOS formats | **16 KiB** (size word 0x8000, 256 blocks; first save at **block 25**). FBNeo maps a 128 KiB region and the BIOS sizes the card by probing. File: 32 + 32768 = **32800** | **2 KiB** (size word 0x1000, 32 blocks; first save at block 5) | n/a | 2 KiB inside the 8 KiB region in cartridge mode |
| Card never written | **131104** (header + the whole 128 KiB region, all zero, unformatted) | 2048, already formatted, user name **"Rosy Lee"**, byte 0x0F = 0xFF | n/a | — |
| When written | at unload | at unload | at `retro_deinit` | — |

**Same play, same data.** Read through the card's own allocation chain, every save holds the same
bytes in FBNeo and Geolith except for the filler. Samurai Shodown II and League Bowling are
byte-identical. The others differ by 2 to 21 bytes. The difference is the erased-block pattern
(each unused word reads back as its own address) at the end of a 64-byte block, which differs
because the save sits at block 25 in one card and block 5 in the other (`0cac 0cb0 …` against
`02ac 02b0 …`).

The backup RAMs were compared after swapping FBNeo's words back: Puzzle Bobble differs by 2
bytes, Blazing Star 3, League Bowling 4, Jockey GP 7, KOF'98 31. The differences are the BIOS
clock and bookkeeping. Baseball Stars 2 differs by 367, because the CPU's pennant race goes
differently. FB Alpha 2012's decompressed RAM differs from Geolith's by 8 to 31 bytes (334 for
Baseball Stars 2), which is the same picture.

## Downloaded entries

From [zwh8800/recalbox-saves](https://github.com/zwh8800/recalbox-saves) at commit `fc24fb8`, a
personal backup of RetroArch save folders with no licence. The attribution comes from the path
only: `rg40xxh/sdcard/saves_RA/Roms/NEOGEO/FB Alpha 2012 Neo Geo/`. That is the folder RetroArch
makes for the `fbalpha2012_neogeo` build, the Neo Geo-only build of the FB Alpha 2012 core.
- `fb-alpha/kof97/kof97.fs` (456 bytes), `fb-alpha/goalx3/goalx3.fs` (500),
  `fb-alpha/mslug/mslug.fs` (476). Each has the same `FB1 FS1` + zlib layout and version
  0x00029730 as the played entries. Game state unknown.

Leads, not filed: the same repo's `retroarch/saves/fba/{kof98,mslug}.fs` have version
**0x00029743**. That is the later libretro "FB Alpha" core (0.2.97.43, in an `fba/` subfolder),
which is not a registry slug of its own, so they are not filed under fb-alpha. Under `.cache/downloads/neogeo/`.

## neogeo-mister, played on the owner's MiSTer (2026-11-04)

Five entries made by script on the owner's MiSTer (NeoGeo_20260603.rbf, Main of 2026-10-19), with
`"method": "played"`, `"frontend": "mister"`; how the rig works is in `MISTER.md`. The scripts are
the ones above with longer boot waits (the exact MiSTer scripts are in `scripts/mister/neogeo/`).

| Game | Mode, BIOS | What the game wrote | Proof |
| --- | --- | --- | --- |
| mslugx | AES, UniBIOS 4.0 | card: METAL SLUG X OPTION (UniBIOS asked MEMORY CARD NOT FORMATTED, A = yes) | OPTION shows DIFF. HARD after a reload |
| jockeygp | MVS, UniBIOS | backup RAM (2 credits: byte 0x34 = 02) + the cartridge's 8 KiB RAM | the betting board after a reload (sprites drawn wrong, see below) |
| lbowling | MVS, UniBIOS | backup RAM + card BOWLING 1P (UniBIOS formatted the card without asking) | MEMORY CARD LOAD YES after a reload |
| blazstar | MVS, UniBIOS | backup RAM (name AAAAAAAA, 30th) + card (NGH 0239) | CARD SAVE OK? > YES ... SAVE OK |
| kof98 | MVS, **original BIOS** (sp-s2.sp1, ASIA/S3 Ver. 6), setting mode | backup RAM: cabinet COIN2 2COINS=2CREDITS; K.O.F.'98 PLAY TIME LITTLE FAST, CONTINUE OFF | the soft DIP page after a reload |

Not attempted: fatfury2, samsho, samsho2, pbobblen, bstars2 (the save kinds were covered). The
device has no AES original BIOS under the name the core loads (`neo-epo.sp1`; it has
`neo-epo.sp1.bin`), so AES ran with UniBIOS, the default when `uni-bios.rom` is present.

**One file, always 73728 bytes**, `saves/NEOGEO/<name>.sav`, where `<name>` is the `.neo` file's
stem (or the romset folder's name for a MAME-style set): `mslugx.neo` saves `mslugx.sav`. The
owner's own sets are named `Metal Slug X (mslugx).neo`, so their saves are
`Metal Slug X (mslugx).sav`. Layout (NeoGeo_MiSTer `neogeo.sv`, `bk_lba` 0x00-0x8F):

| Offset | Size | What | Byte order |
| --- | --- | --- | --- |
| 0x00000 | 65536 | MVS backup RAM | each 16-bit word byte-swapped (`ABKCPUR MAO  K.!` at 0x10), **the same as FinalBurn Neo's `.fs`**: the raw first 64 KiB differ from FBNeo's file by 16-61 bytes per game (BIOS clock, bookkeeping, UniBIOS's `V2` block at 0x00) |
| 0x10000 | 8192 | the memory card (2 KiB used: 0x10000-0x107FF; the rest never written) **or**, for a cartridge with its own RAM (jockeygp, vliner), that RAM instead | each 16-bit word byte-swapped |

- **AES:** the backup RAM is not connected, so the first 64 KiB stay as loaded: all FF in a new
  file. The card is the only data.
- **Jockey GP:** the cartridge RAM takes the card's place, so the file is the same size and layout
  as FinalBurn Neo's 73728-byte `.fs` (64 KiB + 8 KiB, same byte order; 90 bytes of game state
  differ). No card is saved for this game. The core marks a save pending only on backup-RAM or
  card writes, not on cartridge-RAM writes: the coins (backup RAM) are what made it write.
- **Fill:** no seed was needed. The core reloads the save after every ROM load ("always load
  backup so it will erase the memory"), and Main hands it FF blocks when the file does not exist,
  so everything the game never wrote is FF (the unused 6 KiB of the card region, the AES backup
  RAM).
- **The card, compared with Geolith's `.mcr`:** every saved block is byte-identical; only the
  32-byte card header differs (22 bytes). UniBIOS writes bytes 0-5 as FF (MVS) or `56 32 02 32 FF
  FF` (AES), byte 0x0F = 00, and a user name of 8 spaces then 8 FF; Geolith's pre-formatted card
  has zeros, 0x0F = FF and "Rosy Lee". The original MVS BIOS in setting mode (kof98) left no
  formatted card: each 16-bit word of the 2 KiB reads back its own address (unswapped `00 00 00 04
  00 08 ...`), the erased pattern described above.
- **Backup RAM, compared with Geolith's `.nv`** (after swapping the words back): 14-61 bytes
  differ, at 0x00-0x05 (UniBIOS's block), 0x20-0x22, 0x34 (credits), 0x41-0x5D (clock and
  bookkeeping) and the games' own entries.

Device findings that are not about the files:
- **Metal Slug X** needs a patched P ROM on this core (no protection quirk for NGH 0x250 in Main's
  `.neo` loader): the Geolith `.neo` hangs on the WARNING screen. The entry used a copy of the
  owner's own `.neo`, which carries the patch.
- **Sprites with vertical shrink are drawn as streaks** (jockeygp's race picture, blazstar's
  attract): the device has no `games/NeoGeo/000-lo.lo`, the shrink table Main loads. It does not
  affect saves.
- Setting System Type, BIOS and the Settings DIP needs `config/NEOGEO.CFG`, which the owner had
  (MVS). The rig wrote its own for each run and put the owner's back byte-identical, mtime included.
