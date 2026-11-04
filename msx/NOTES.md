# MSX

Five cartridge games with battery SRAM, two runnable libretro cores, ten entries filed. The
two cores disagree on almost everything except the bytes of the save: **where** the file goes
(blueMSX: the save directory, fMSX: beside the ROM), **when** it is written (blueMSX only when the
cartridge is re-inserted, which RetroArch does only on reset; fMSX on unload), its **name**
(`.sram` vs `.sav`), and for Koei carts its **size** (32 KiB vs 8 KiB). Neither core uses
`RETRO_MEMORY_SAVE_RAM`, so RetroArch itself never writes an `.srm` for an MSX cartridge.

MSX2 shares both cores and everything below; see `msx2/NOTES.md` for its games.

## The games

The library has nine MSX1 cartridges with SRAM (found by matching the No-Intro set's sha1s
against blueMSX's `Databases/msxromdb.xml`, `work/msx/sramscan.py`): Xanadu, Deep Dungeon,
Deep Dungeon II, Syougun (ASCII8 + 8 KiB), Hydlide II, Harryfox MSX Special (ASCII16 + 2 KiB),
Genghis Khan, Nobunaga no Yabou Zenkoku Ban (Koei, 32 KiB), Game Master II (Konami, 8 KiB).
Hydlide 3 and Dragon Slayer IV are plain ASCII8 with no SRAM (they save to disk/tape). There is
no tenth; five were scripted, four were dropped (below).

| Game (No-Intro) | Mapper / SRAM | The save | Proof (last shot) |
| --- | --- | --- | --- |
| Hydlide II - Shine of Darkness (Japan) | ASCII16, 2 KiB | SET UP → CHARACTER をつくる, name ABC, accept | after reset: GAME START → NAME LIST shows ABC |
| Deep Dungeon (Japan) | ASCII8, 8 KiB | なまえとうろく, name ABC (joystick-only name grid) | after reset: roster ABC, HP 20, level 1 |
| Deep Dungeon II (Japan) | ASCII8, 8 KiB | register ABC (no password), start the game. The roster reaches SRAM only when the game starts; a reset straight after registering shows an empty roster | after reset: roster ABC HP 25 L1 |
| Dragon Slayer II - Xanadu (Japan) | ASCII8, 8 KiB | Start: the game builds its world state in SRAM (3.8 KB non-blank) | after reset the title menu comes up with **Continue** preselected (it does only when SRAM holds a game) |
| Nobunaga no Yabou - Zenkoku Ban (Japan) | Koei, 32 KiB | new game as Oda, そのた → 4 SAVE (save at season change), end turn, save to 1: RAM | after reset: Load data → 1: RAM → 1560 summer, Oda's commands |

Every script ends with `reset` and a reload of the save: the reset is what makes blueMSX write
its file (see below), and the proof shows the game reading the save back.

Dropped, each after several attempts:
- **Genghis Khan** (Koei 32 KiB): the setup (30 ability rolls, bonus-point allocation for five
  family members) drops most key presses while it redraws; a script never got past Temüjin's
  bonus points reliably.
- **Syougun** (ASCII8 8 KiB): in game, the cursor keys move the character, not the icon menu;
  the save command was not found. fMSX also needs the mapper forced to ASCII 8kB to start it.
- **Game Master II**: its SRAM stores positions of *other* Konami cartridges in slot 2. Alone it
  only offers SELF MODE (screen loader, SRAM↔disk utility, Tennis/Hockey, Biorhythm), none of
  which saves. blueMSX libretro cannot insert a second cartridge (its "additional cartridge"
  option only offers sound cartridges); fMSX has `fmsx_game_master` (loads GMASTER2.ROM from the
  system directory into the other slot), untested.
- **Harryfox MSX Special** (ASCII16 2 KiB): Japanese command-menu adventure; the save command
  was not found in the time box.

## Games x cores

| Game | bluemsx | fmsx |
| --- | --- | --- |
| Hydlide II | filed | filed (needs `fmsx_mapper_type_mode = ASCII 16kB`, `scripts/msx/fmsx-ascii16.opt`; the guessed mapper runs the title but the game never reacts to a key) |
| Deep Dungeon | filed | filed (port device Joystick + Emulated Keyboard) |
| Deep Dungeon II | filed | filed (same) |
| Xanadu | filed | filed |
| Nobunaga Zenkoku Ban | filed (32 KiB) | filed (**8 KiB**, see below) |

| Core | Status |
| --- | --- |
| msx-mister, msx1-mister (MiSTer) | not runnable; see "Downloaded entries and leads" |
| boogermann-msx (openFPGA) | not runnable; see "Downloaded entries and leads" |

Core builds: blueMSX `git e3086eb`, fMSX `6.0 4de1175` (buildbot, arm64). Default options except
where noted. Both cores ran an **MSX2+** machine: blueMSX's `Auto` machine type picks MSX2+ for
any `.rom` (libretro.c `get_media_type`), fMSX's `fmsx_mode` defaults to MSX2+.

System files: the libretro buildbot's `assets/system/blueMSX.zip` (the URL in the brief,
`BlueMSX.zip`, is a 404; the file is `blueMSX.zip`): `Machines/` and `Databases/` for blueMSX,
and from its `Machines/Shared Roms` the fMSX files `MSX.ROM, MSX2.ROM, MSX2EXT.ROM, MSX2P.ROM,
MSX2PEXT.ROM, KANJI.ROM, FMPAC.ROM` and `DISK.ROM` (= `PHILIPSDISK.rom`). fMSX shows "DISK.ROM
not loaded" and refuses disk content without it. No MSX BIOS was at hand.

## How each core writes the save

| | blueMSX | fMSX |
| --- | --- | --- |
| File | `<ROM stem>.sram` | `<ROM path minus extension>.sav` |
| Where | the frontend's **save directory** (`boardSetDirectory(save_dir)`) | **beside the ROM** (the name is built from the content path; `rfopen` of that path) |
| When | only when the cartridge is removed: `retro_reset` re-inserts it and so writes it; `retro_unload_game` never destroys the board, so **closing content writes nothing**. Checked: Hydlide II played without the reset leaves the save directory empty | on unload (`TrashMSX` ejects the cartridge) and on cartridge change; not on reset |
| Read back | on insert, from the same path | on load, from the same path |
| `RETRO_MEMORY_SAVE_RAM` | 0 (only SYSTEM_RAM is exposed) | NULL for cartridges (used only for the "Save disk changes: To/From SRAM" disk mode) |
| ASCII16 (2 KiB) | 2048 | 2048 (0x800) |
| ASCII8 (8 KiB) | 8192 | 8192 |
| Koei (32 KiB) | **32768** (four 8 KiB banks; untouched banks stay 0xFF) | **8192**: fMSX has no Koei mapper, runs it as ASCII8 and keeps one 8 KiB SRAM page |
| Game Master 2 | 8192 (not filed) | 0x1000 + 0x1000 from two pages (source, not filed) |
| Blank fill | 0xFF | 0xFF (`NORAM`) |
| Extra files | none (the MSX2+ machine's battery CMOS would go to `<save dir>/<machine>.cmos` on machine destroy, which never happens in libretro) | `CMOS.ROM`, 52 bytes (`RTC[4][13]`), written **into the system directory** (`chdir(ProgDir)`) on unload whenever the RTC was written, i.e. on every MSX2/2+ boot. `RETRO_MEMORY_RTC` is deliberately 0. Filed as `system/CMOS.ROM` (location `sysdir`) |

Consequences for a frontend or sync service: in RetroArch, a blueMSX cartridge save exists only
if the user reset the game before quitting; an fMSX save sits in the ROM folder, not in
`saves/`, and (inferred from the code, not tested) is lost when the ROM is loaded from an archive
that RetroArch extracts to a temporary directory.

`provenance.json` gives each file a `location` (`savedir`, `content-dir`, `sysdir`), because
`tools/make-save.py` only files the save directory. These entries were made with
`work/msx/make-save-x.py` (copies the ROM into the run directory, so fMSX's `.sav` lands there
and `.cache/roms` stays clean).

## Same play, different bytes

| Game | bluemsx vs fmsx |
| --- | --- |
| Xanadu | identical 8192 bytes |
| Hydlide II | 10 bytes differ, all in 0x1D-0x31 right after the name "ABC": a run of small per-character values that are 2/1 in blueMSX where fMSX has 1/2 (random starting values) |
| Deep Dungeon, Deep Dungeon II | exactly 0x400-0x7FF differs: 0x00 in blueMSX, 0xAA in fMSX; the roster itself is identical |
| Nobunaga | blueMSX 32 KiB vs fMSX 8 KiB; within the first 8 KiB 286 bytes differ (Oda's ability rolls and the AI's moves differ between runs) |

## fMSX input (a harness gap, worked around)

fMSX reads the host keyboard **only** when port 0's device is "Keyboard"
(`RETRO_DEVICE_KEYBOARD`); with RetroPad (what `retro-run` always sets) the keyboard is ignored,
and with "Joystick + Emulated Keyboard" (subclass 0, id 257) the pad drives the joystick and
a few keys (Y = space, Start = F1, L3 = Enter, R3 = Esc). `retro-run` cannot choose the device,
so `work/msx/retro-run-x/` is a patched copy with `--device0 N` (also `key kcN` for raw keycodes
and `--keep-temp`, used for C64). Keyboard games ran with 3, joystick games with 257;
`provenance.json` records it as `port0_device`. blueMSX reads keyboard and joypad at once.

## Downloaded entries and leads (MiSTer, openFPGA)

Nothing filed: no save file was found that a source attributes to one of these cores. Searched:
the cores' GitHub repos, issues and comments (API sweeps for attachments), Main_MiSTer and
Distribution_MiSTer, the misterfpga.org MSX threads (the site answers 403 to fetches; its
mirror's attachments need a login), msx.org, Reddit, archive.org, save-file-converter's test
data. What the sources say:

- **msx-mister** (MiSTer-devel/MSX_MiSTer, the OCM/1chipMSX port): the only writable image is the
  `S,VHD` SD-card image (FAT16) that MSX-DOS writes in place; the cartridge slots offer only
  MegaSCC+/MegaRAM, so there is no cartridge-SRAM or `.sav` path at all.
- **msx1-mister** (MSX1_MiSTer by Molekula/tdlabac): the build update_all installs
  (`MSX1_20250108.rbf`, `main` branch) keeps Game Master 2 SRAM in memory only and writes `.DSK`
  images in place. The `MSX2` branch has "SRAM Save/Load" and `rtl/nvram_backup.sv`; loading a
  ROM in slot A mounts `saves/MSX1/<rom>.sav` (Main_MiSTer `FileGenerateSavePath`), by
  the source a raw cartridge-SRAM dump sized from the ROM database, prefilled 0xFF ("Zatím umíme
  pouze CART SRAM"). Commit 3e11a883 (2025-07-29) disconnected `img_mounted` with a TODO, so
  builds after it probably write nothing; MSX2-branch builds 20230203-20250727 appear to.
  Lead: misterfpga "New MSX Core In The Works", page 4 (wark91, 2023-07-07, saving via Game
  Master 2 to a DSK).
- **boogermann-msx** (opengateware/computer-msx 0.9.2, Pocket): no nonvolatile slot in
  `data.json`, `sleep_supported: false`, disk and cassette not implemented: it saves nothing.

## msx-mister and msx1-mister on the owner's MiSTer (2026-11-04)

Checked on the device (MSX_20260603.rbf, MSX1_20250108.rbf), nothing filed:

- **msx1-mister** (MSX1_20250108, `main` branch): its CONF_STR has no backup-RAM option and only
  one SD image, the `.DSK` drive (written in place). Loaded by MGL with the blueMSX `MSX.ROM` as
  BIOS (file index 1, `P2F1,ROM,Load BIOS`) and Hydlide II in slot A (index 2), the core gave no
  picture (the scaler screenshots were 1x1) and no `saves/MSX1/` folder was created. The device has
  no MSX1 BIOS set up (`games/MSX1/` is empty), so the core may simply not have started; not
  pursued, since the build has no save path for cartridge SRAM anyway (Game Master 2's SRAM lives
  in FPGA memory only, as the source says).
- **msx-mister** (the OCM/1chipMSX port) was not run: it boots only from a FAT16 VHD with
  OCM-BIOS and MSX-DOS (none on the device; `games/MSX/` is empty), and the VHD is the only thing
  it ever writes. Cartridge ROMs run from the VHD through loaders, into MegaSCC+/MegaRAM, which are
  RAM without a battery: there is no cartridge-SRAM save to make. The same holds for MSX2.
