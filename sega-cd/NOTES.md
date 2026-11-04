# Sega CD / Mega-CD

Nine games, four runnable libretro cores. 30 (game, core) pairs were filed out of 36 tried.
All six failures are ClownMDEmu, which cannot run those games. There are also three downloaded
MiSTer saves. The cores agree on almost nothing about saves:

- **Genesis Plus GX** writes one 8 KiB internal backup RAM per BIOS region (`scd_U.brm`,
  `scd_E.brm`, `scd_J.brm`) and one 512 KiB RAM cart (`4Mbit_cart.brm`). Both files are shared by
  every game.
- **PicoDrive** writes an 8 KiB `<disc>.srm` per game. With its RAM cart turned on, that file is
  72 KiB.
- **ClownMDEmu** never writes a backup RAM image. It writes each BRAM *file* as its own host file,
  named after the 11-character BRAM file name.

The bytes inside the images agree: where two cores ran the same play, the backup RAM images are
byte-identical.

Only nine games, not ten. The tenth slot went to candidates that each cost too much (see "Tried
and dropped").

## BIOS

The brief said none had been found by file name. They are on the drive in two places:

- A Sega BIOS folder: `[BIOS] Sega CD (USA) (v1.10).md` and the rest of the No-Intro set
  (131072 bytes each, a `.md` extension), plus `Region Free CD BIOS/` (l_oliveira patches).
- A Mega EverDrive pack's `BIOS/`: the same, unpacked from the EverDrive pack.

Copied into `.cache/bios/sega-cd/` under the names libretro expects:

| File | Source | md5 |
| --- | --- | --- |
| `bios_CD_U.bin` | Sega CD (USA) (v1.10) | 2efd74e3232ff260e371b99f84024f7f |
| `bios_CD_E.bin` | Mega-CD (Europe) (v1.00) | e66fa1dc5820d254611fdcdba0662372 |
| `bios_CD_J.bin` | Mega-CD (Japan) (v1.00P) | 278a9397d192149e84e820ac621a8edd |

How each core uses them:

- **Genesis Plus GX** and **PicoDrive** boot the real BIOS. The proofs show the "Ver. 1.10" screen.
  Both pick the BIOS by the disc's region.
- **ClownMDEmu v1.6.12** loads no BIOS file at all, even with the three in its system directory. It
  boots discs directly with a high-level emulation of the BIOS calls, and logs "UNRECOGNISED BIOS
  CALL DETECTED (0x..)" for calls it lacks. It needs no BIOS, and that HLE is also why it fails on
  most games here.

## Discs

One folder had 6 discs. The real library is
a Trimmed Redump set: 240 Redump discs, mostly `.7z`, with seven
already unpacked.

The internal disk was full while this was done (it dropped to 134 MB free once). So:

- The unpacked discs are symlinked into `.cache/roms/sega-cd/<disc>/`, with a copy of the `.cue`.
- The `.7z` discs (Lunar, Prince of Persia, Might and Magic III, Eye of the Beholder, Dark Wizard,
  Sangokushi III) are unpacked by `work/sega-cd/bin/prep.sh`. It extracts the data track for real
  and makes each audio track a zero-filled sparse file of the exact size. The game runs with
  silent CD audio and identical timing.

The provenance of those six games says so in `note`. Its `rom.sha1` is the sha1 of the original
`.cue`. Disc images are deleted after use; `prep.sh "<disc>"` recreates one.

## The nine games

| Disc (Redump) | Save | Why | Script ends with (proof) |
| --- | --- | --- | --- |
| Sonic CD (USA) | `SONICCD____`, 11 blocks, created on first boot (time-attack table, progress) | the best-known Sega CD game | Palmtree Panic 1 in play. The file is the game's own initial save: it is written before the title, and nothing short of clearing a zone changes it |
| Shining Force CD (USA) (3R) | a 99-block save made when a book is started, plus a 1-block file. The game offers **INNERBACKUP or CARTRIDGE** | biggest internal save; uses the RAM cart when there is one | after a reset the book menu offers CONTINUE (Genesis Plus GX), or lists AAAAAAA SDMN LV 1 (PicoDrive) |
| Lunar - The Silver Star (USA) | 40 blocks; Nall's SAVE (the manual: about three Lunar saves fit in an empty unit) | classic RPG with a save menu | "1:DYNE'S MEMORIAL" "SAVED!" |
| Prince of Persia (USA) | 18 blocks, written in **protected (ECC) mode**. The game creates it at boot, rewrites it when level 1 starts, and has a pause-menu SAVE | the protected-mode case | level 1 after a reset and CONTINUE (ClownMDEmu: the pause menu) |
| Might and Magic III - Isles of Terra (Japan) | **all 125 free blocks** in one file, `MM3_SAVE_00` | a Japanese disc (`scd_J.brm`); a save that fills internal BRAM | "セーブしました" (saved) |
| Eye of the Beholder (USA) | **all 125 free blocks** in one file; CAMP > Save Game > slot 1 | a second full-BRAM game; pointer-driven menus | "Saved." |
| Sonic MegaMix (USA) (Unl) | 25 blocks (`S1MEGAMIX__`), created on first boot. START GAME > SAVE writes the slot | the only other disc ClownMDEmu runs | Green Hill Zone in play |
| Dark Wizard (USA) | 40 blocks; command menu SAVE | strategy RPG; a quick save on turn 1 | after a reset the title offers NEW GAME / **CONTINUE** / OPTIONS |
| Sangokushi III (Japan) | **six files, 628 blocks, on the RAM cart only**. The game refuses to play without a cart | a cart-only game | "データがセーブされました" (saved), slot S0 184年1月 公孫瓚 |

Scripts are in `scripts/sega-cd/`. Every one starts at power-on. The Genesis A, B and C buttons are
RetroPad y, b and a.

Variants and options:

- `*.clownmdemu.txt` (Sonic CD, Prince of Persia, Sonic MegaMix): ClownMDEmu has no BIOS intro, so
  everything comes 600 or more frames earlier. Its Prince of Persia variant stops after SAVE. After
  a reset ClownMDEmu's title menu first shows CONTINUE blank, and the press meant for it lands on
  FASTEST.
- `Sangokushi III.picodrive.txt` with `picodrive-ramcart.opt` (`picodrive_ramcart = enabled`):
  PicoDrive has no cart by default, and its cart starts unformatted. The game asks to format it
  (初期化), and the variant answers that first.

## Games x cores

| Game | genesis-plus-gx | genesis-plus-gx-wide | picodrive | clownmdemu |
| --- | --- | --- | --- | --- |
| Sonic CD | filed | filed | filed | filed (variant) |
| Shining Force CD | filed (save on the **cart**) | filed (cart) | filed (internal) | failed: black screen after the title (the book scene never loads). No error logged |
| Lunar - The Silver Star | filed | filed | filed | failed: stuck at "NOW LOADING", BIOS call 0x08 unimplemented |
| Prince of Persia | filed | filed | filed | filed (variant) |
| Might and Magic III | filed | filed | filed | failed: stuck on the CRI logo, BIOS call 0x19 unimplemented |
| Eye of the Beholder | filed | filed | filed | failed: the game runs, but "Select save area" lists no slots, so no save (BRAM HLE) |
| Sonic MegaMix | filed | filed | filed | filed (variant) |
| Dark Wizard | filed | filed | filed | failed: stuck at "NOW LOADING" |
| Sangokushi III | filed (cart) | filed (cart) | filed (cart, `--options`) | failed: stuck at the title. It has no cart, and writes only a blank `.srm` |

The failed ClownMDEmu runs wrote only the blank 64 KiB `.srm`, so `make-save.py` did not file them.
The `status.jsonl` lines say `ok: false`.

| Core | Status |
| --- | --- |
| megacd-mister (MiSTer) | not runnable. 3 downloaded (below) |
| jeremy-megacd (openFPGA) | not runnable. Nothing found; layout from its source below |

Core builds: Genesis Plus GX v1.7.4 f27655b, Genesis Plus GX Wide v1.7.4 b7ad005, PicoDrive
2.05-1890c29, ClownMDEmu v1.6.12 d43c270.

## How each core writes the backup RAM

| Core | Internal BRAM (8 KiB) | RAM cart | Per game or shared |
| --- | --- | --- | --- |
| genesis-plus-gx, -wide | `scd_U.brm` / `scd_E.brm` / `scd_J.brm`, 8192 bytes, chosen by the region of the BIOS that booted | `4Mbit_cart.brm`, 524288 bytes, **always plugged in and formatted** (8189 free blocks). It is written on every run, even when no game touches it | **shared**: one internal file per region and one cart for every game (options `genesis_plus_gx_system_bram = per bios`, `genesis_plus_gx_cart_bram = per cart`) |
| picodrive | `<disc>.srm`, 8192 bytes (RETRO_MEMORY_SAVE_RAM) | off by default. With `picodrive_ramcart = enabled`, `<disc>.srm` grows to **73728** bytes: the first 8 KiB are zeros (the core's description warns the internal BRAM is discarded), then a **64 KiB** cart (1021 blocks) that starts unformatted | **per game** |
| clownmdemu | no image. Each BRAM file is a host file `<NAME>.brm`: the 11-character BRAM file name as the game wrote it (`SONICCD____.brm`, `S1MEGAMIX__.brm`), or `<NAME>.wp.brm` for a file written in protected mode (`PRINCE_ARO_.wp.brm`) | none | shared by file name. Two games that used the same BRAM name would meet in one file, as on hardware |
| megacd-mister (from the downloads and Main_MiSTer source) | `saves/MegaCD/<disc>.sav`, 8192 bytes | with "Backup RAM: Internal+Cart", the same `.sav` is **532480** bytes: 8 KiB internal, then a 512 KiB cart | per game |
| jeremy-megacd (from its `data.json` and `megacd_top.sv`, no sample) | 8192 bytes. The save slot takes the slot-0 file name, which is the BIOS, so the file is `Saves/megacd/common/<BIOS stem>.sav` | not implemented | **shared per BIOS file**. Its README suggests copying the BIOS under other names to get separate banks |

Other files the cores write:

- **ClownMDEmu** also writes `<disc>.srm`: 65536 bytes, all zeros. That is the Mega Drive cartridge
  SRAM, exposed even for a CD. It is filed beside the `.brm` files because it is what the core
  writes, but it holds nothing.
- **Genesis Plus GX option names**, from dry runs not filed:
  - `per game` gives `<disc>.brm` (8192) and `<disc>_4Mbit_cart.brm` (524288).
  - `genesis_plus_gx_cart_size` changes the cart's name and size: `128Kbit_cart.brm` is 16384
    bytes. The names go up through `256Kbit_`, `512Kbit_`, `1Mbit_`, `2Mbit_` and `4Mbit_cart.brm`;
    the default is 4 Mbit.
  - `genesis_plus_gx_cart_size = disabled` crashed the core (see Runner problems).
- **Genesis Plus GX** (its internal images and its cart) and **PicoDrive** (the `.srm` with the cart
  off) format a new image themselves. A fresh internal image is the same 8192 bytes in both cores (sha1
  472cb08846…), and the fresh 512 KiB cart is sha1 2a170e18ca…, identical to one-saves'
  `4Mbit_cart.empty.brm`. PicoDrive's cart is the exception: it is left unformatted, so a game has
  to format it.

**Sharing in practice.** Every filed Genesis Plus GX entry started from fresh files, so each
`scd_*.brm` holds only that game's save. It is still the file every game of that region would
share. Two of the games show why that matters:

- Might and Magic III and Eye of the Beholder each take all 125 free blocks. With Genesis Plus GX's
  shared `scd_U.brm`, or on real hardware, neither can save once anything else is in the internal
  BRAM. PicoDrive's per-game `.srm` never has that conflict.
- Might and Magic III lists six slots (MM3_SAVE_00 to 05) in Genesis Plus GX and only slot 00 in
  PicoDrive. With a cart present, the game offers the cart's space for the other five.

**The same game, saved to different places.** Shining Force CD shows INNERBACKUP and CARTRIDGE
side by side when a cart exists. The script's "right" press picks CARTRIDGE in Genesis Plus GX and
does nothing in PicoDrive. So the same script leaves:

| Core | Cart | Internal BRAM |
| --- | --- | --- |
| Genesis Plus GX | the 99-block save, at 0x40 of `4Mbit_cart.brm` | only the 1-block file |
| PicoDrive | none | both files: the 1-block file at block 1, the 99-block save at 0x80 |

The 99 blocks of save data are **byte-identical** in the two places. MiSTer's Shining Force CD
(5R, 6R) download has the same internal layout as PicoDrive's: 24 blocks free, 2 files.

## Same play, same bytes

| Game | Result |
| --- | --- |
| Sonic CD, Lunar, Prince of Persia, Might and Magic III, Sonic MegaMix, Shining Force CD (cart, Genesis Plus GX and -wide) | identical across Genesis Plus GX, -wide and PicoDrive, byte for byte |
| Dark Wizard | Genesis Plus GX = PicoDrive; -wide differs in 4 bytes |
| Eye of the Beholder | Genesis Plus GX vs PicoDrive 2 bytes, vs -wide 13 bytes |
| Sangokushi III | the two Genesis Plus GX carts differ in 375 bytes. Genesis Plus GX vs PicoDrive's cart: 394 bytes in the data. The layout is the same: data from block 1 (+0x40), six directory entries below the footer |

The differing games are the ones where the game keeps random or timing state. Every other
difference is outside the game's data: file name, file size, whether a cart is attached, and the
footer's free-block count (0x1FFD for 512 KiB, 0x03FD for 64 KiB, 0x007D for 8 KiB, minus what is
used).

ClownMDEmu's file is the logical file content:

- `SONICCD____.brm` (704 bytes = 11 blocks) and `S1MEGAMIX__.brm` (1600 = 25 blocks) equal the
  bytes at 0x40 of the Genesis Plus GX image.
- `PRINCE_ARO_.wp.brm` is **576 bytes = 9 blocks**, while the game's file takes **18 blocks** in a
  real BRAM image. Protected mode stores everything twice with error correction, and ClownMDEmu
  apparently keeps only the logical data (not checked byte by byte, since the ECC form was not
  decoded). A converter between the two has to encode or decode it.

## Backup RAM format, as seen in these files

**Layout.**

- The image is 64-byte blocks.
- The last 0x40 bytes are the footer: `"___________"` (11 underscores) `00 00 00 00 40`, the
  free-block count as a u16 BE written 4 times, the file count as a u16 BE written 4 times,
  `"SEGA_CD_ROM" 00 01 00 00 00`, `"RAM_CARTRIDGE___"`.
- Files start at block 1 (0x40). The directory grows down from the footer, two 32-byte entries per
  64-byte block: Sonic CD's one file has its directory at 0x1F80-0x1FBF, and Sangokushi III's six
  files at 0x7FF00-0x7FFBF.
- The entries are not plain ASCII. The BIOS keeps the directory in protected (ECC) form, so file
  names cannot be read without decoding. ClownMDEmu is the only core here that names them.

**Block 0.** In internal BRAM booted with the real BIOS, the first 16 bytes of block 0 often hold
one 32-bit value written four times. It is not part of any file, and it varies by game:

| Game | Value |
| --- | --- |
| Sonic CD | FFFC0002 |
| Eye of the Beholder | FFFC0006 |
| Prince of Persia | FFC40004 |
| Lunar | 00000004 |
| Might and Magic III | 00000014 |
| Dark Wizard | FFF80012 (-wide: FFF80010) |
| Sangokushi III | FFEE0038, even though it saves only to the cart |

Shining Force CD and Sonic MegaMix leave it zero. In exploration runs, Heimdall (FFFC0002) and
Final Fight CD, Batman & Robin and Popful Mail (one non-zero block each, not decoded) wrote to
block 0 without ever saving a file. It is identical in Genesis Plus GX and
PicoDrive, so it comes from the BIOS's BRAM routines, not from a core. A save tool that treats
"blocks outside the files are zero" as a validity check would trip on it.

**A blank internal image is not empty.** A formatted image has 48 non-zero bytes (the footer), so
`make-save.py`'s "blank" check passes for an unused `scd_*.brm` or cart. That check is what kept
the first Genesis Plus GX Wide Lunar run, which never reached SAVE, from being flagged. It was
caught by comparing images and re-run with a longer wait.

## Downloaded entries (megacd-mister)

All three are from birdybro's whole MiSTer `saves/` folder, posted as `saves.zip` (2.6 MB) in
[save-file-converter #80](https://github.com/euan-forrester/save-file-converter/issues/80#issuecomment-1057487772)
on 2022-03-02. Attribution is by folder: Main_MiSTer writes MegaCD core saves to
`saves/MegaCD/<cue stem>.sav` (`support/megacd/megacd.cpp`).

- `Shining Force CD (USA) (5R, 6R)/`, 532480 bytes, "Internal+Cart":
  - Internal half: 24 free blocks, 2 files, the same shape as PicoDrive's Shining Force CD.
  - Cart half: formatted, empty, 8189 free. Its last sector equals Main_MiSTer's built-in blank
    footer, so no game formatted it.
- `Lunar - Eternal Blue (USA) (RE)/`, 8192 bytes, 4 files, 67 blocks free. Dated 1980-01-01 (a
  MiSTer without an RTC).
- `Popful Mail (USA) (RE)/`, 8192 bytes, 1 file, 112 blocks free. Byte-identical to
  save-file-converter's test file `Popful Mail (USA) (RE)-mister-internal-only.sav`.

None of these is a game played here (Lunar EB and Popful Mail were not playable in the time; see
below).

## Leads, not filed

- birdybro's zip (in `.cache/downloads/sega-cd/birdybro-saves-zip/`) also has:
  - `Shining Force CD (USA) (3R).sav`: 532480 bytes, but the cart half is all zeros with **no
    footer**, an odd case worth having.
  - `Sonic CD (USA).sav` and `Sonic CD (Europe).sav`: 8 KiB and identical to each other.
  - Ten more 8 KiB Japanese and US saves; Lords of Thunder's is only a formatted blank.

  The (3R) and Sonic CD files were left for the MiSTer worker, who makes played saves of those
  discs.
- [MegaCD_MiSTer #90](https://github.com/MiSTer-devel/MegaCD_MiSTer/issues/90) has `cart.brm.zip`.
  Genesis Plus GX wrote it, not the MiSTer.
- jeremy-megacd ([neutralinsomniac/openfpga-megacd](https://github.com/neutralinsomniac/openfpga-megacd)):
  its 15 issues have no save attachments. In #11 the developer asked for a Snatcher save; none was
  posted.

  Searched with nothing found: misterfpga.org (13 threads, no attachments; search is closed to
  guests), Reddit (blocks curl), archive.org, and GitHub code and issue search.
- Reference only, not copied: one-saves has a Genesis Plus GX Wide `scd_U.brm` (Sonic CD: 1 file,
  114 free, the same shape as ours) with a used and an empty `4Mbit_cart.brm`. It also has MiSTer
  Sonic CD (3 files) and Shining Force CD (3R) saves, internal only.

## Tried and dropped

These were dropped on the save mechanism, not the cores:

| Game | Why |
| --- | --- |
| Secret of Monkey Island | passwords only |
| Earthworm Jim SE, Final Fight CD, Jaguar XJ220 | no save seen |
| Ecco, Ecco: The Tides of Time, 3 Ninjas, Batman & Robin | no save at boot |
| Snatcher | asks INTERNAL or CART at boot. The first save needs Metal Gear, about an hour into the story |
| Popful Mail | its "RAM Cart detected. Use it?" prompt took no input from any button |
| Vay | unskippable anime intro |
| Theme Park (Europe) | would have given `scd_E.brm`; its in-park save menu was not found in time |
| Heimdall | the title menu ignored input |
| Dungeon Explorer | creates a protected 4-block `DUN_EXPL_00` at boot, but a slot save is past a long scroll |
| Nobunaga no Yabou - Haouden | set up, but the opening narration is long |
| Lunar - Eternal Blue | not tried (470 MB data track, with a full disk) |

## Runner problems (worked around, nothing in tools/ changed)

- **Genesis Plus GX dies with SIGBUS (rc -10) when `genesis_plus_gx_cart_size = disabled`.** It
  happens right after the BIOS loads, before frame 1, and the log shows "Sega/Mega CD RAM CART is
  located at: " with an empty path. I did not establish whether the core or retro-run is at fault.
  Nothing filed uses it.
- **Save states did not work for Genesis Plus GX with a CD.** After `loadstate`, the screen stayed
  black. So every script was developed by replaying from power-on (runs take seconds).
- The 23:37-to-fix window when retro-run crashed on Genesis Plus GX (SET_DISK_CONTROL_INTERFACE):
  every Genesis Plus GX run here returned rc 0, and everything filed was run after the fix.
- **Timing differs between cores.**
  - In Lunar, the Alex-and-Nall scene runs about 1000 frames longer in Genesis Plus GX Wide.
  - In Dark Wizard, PicoDrive prints dialogue more slowly.
  - After a reset, the BIOS shows "Put a DISC on the CD tray" until Start is pressed once, and needs
    a second Start to boot.

  The shared scripts take extra waits and spare B presses for all of these.
- **Disk.** The internal disk filled up during the run (ENOSPC once). Hence the sparse-audio
  unpacking, and the disc images deleted after filing.
