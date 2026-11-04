# Atari 7800

Nothing filed. No retail 7800 cartridge has save memory. The two ways a 7800 game can save are
peripherals: Atari's **High Score Cartridge** (HSC, a pass-through cart with 2 KiB of
battery-backed RAM and its own ROM, unreleased in the 1980s and later reissued by homebrewers; a set
of Atari titles detect it, Centipede, Asteroids, Joust and Food Fight among them) and the
**SaveKey/AtariVox** used by homebrew. The only runnable core, ProSystem, emulates neither, and the
library has no HSC ROM, so no played save can be made here.

## The High Score Cartridge, checked again

- **ProSystem has no HSC support, in this build or upstream.** The buildbot core is ProSystem 1.3e
  8a88014, which is also the head of `libretro/prosystem-libretro` (commit of 2026-08-22, "fix
  CORETONE CDF loading"). Its `core/` has no HSC code: nothing loads a high-score ROM (the only
  external files are `7800 BIOS (U).rom` / `7800 BIOS (E).rom`), nothing maps RAM at 0x1000-0x17FF,
  and `Cartridge.c` reads the A78 header up to byte 57 (controllers, region) but not byte 58, the
  save-device byte (0 none, 1 HSC, 2 SaveKey). `retro_get_memory_data` returns only
  `RETRO_MEMORY_SYSTEM_RAM`, so there is no `.srm` either. Its core options are colour depth,
  low-pass filter and a dual-stick hack.
- **No HSC ROM in the library.** Searched every BIOS folder under the ROM library drive (Sega CD,
  PS2, PC Engine, Game Gear, Neo Geo, a PS Vita emulator set) and the 7800 folders of the Pocket
  SD-card backups (`Assets/7800/common/` holds only `7800bios.bin`, the BIOS already used), plus a
  name search of the whole drive (outside save folders) for `hiscore`, `highscore`, `hsc` and
  `7800`. The GoodTools 7800 set there (Good7800 2.04) has no HSC ROM either: its only BIOS entry is
  "7800 DEV OS BIOS (PD)", and its HSC-related entries are two dumps of "Desert Falcon (2004) (HSC
  Hack)". Nothing was copied to `.cache/bios/atari-7800/` and nothing was downloaded.

Even with the ROM, ProSystem would ignore it. A played HSC save needs a core that emulates it
(MiSTer's Atari7800, below; A7800/MAME-derived emulators, which are not registry cores here).

## Evidence of no save

ProSystem 1.3e 8a88014 booted Centipede (USA), an HSC title, with the 7800 BIOS
(`7800 BIOS (U).rom`, md5 0763f1ff..., from a Pocket's `Assets/7800/common/7800bios.bin`) and
reported **save RAM 0 bytes**; no file appeared in the save, system or working directory.

## Games x cores

| Game | prosystem |
| --- | --- |
| (none possible: ProSystem has no HSC or SaveKey, and there is no HSC ROM) | - |

| Core | Status |
| --- | --- |
| atari7800-mister (MiSTer) | not runnable. **Does save**: README "Supports High Score Cart saving"; `Atari7800.sv` reads a cart_save byte from the A78 header (0 none, 1 HSC, 2 SaveKey), keeps HSC/SaveKey data in one 32 KiB dual-port RAM and writes it as the core's save file through the standard MiSTer backup path (64 sectors, 32 KiB for a SaveKey). Nothing found online; this is one for the MiSTer worker (an HSC title with a high-score entry, e.g. Asteroids or Centipede, with HSC enabled in the OSD) |
| spiritualized-7800 (openFPGA) | not runnable. No save support documented; nothing found |

## Leads

- The A78 header's save-device byte (offset 58: 0 none, 1 HSC, 2 SaveKey) is what the MiSTer core
  keys on with its "High Score Cart" OSD option at Auto. The No-Intro `.a78` files in this library
  are **headerless** (Centipede (USA).a78 is the bare 16384-byte ROM), so with them the HSC has to
  be set to On in the OSD, or no save is made.
- github.com/johnkharvey/savekey7800: SaveKey test code for the 7800 (no save files).
- 7800 homebrew that saves to a SaveKey would need a core with SaveKey support; ProSystem has none.
