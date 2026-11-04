# Atari 7800

Nothing filed. No retail 7800 cartridge has save memory. The two ways a 7800 game can save are
peripherals: Atari's **High Score Cartridge** (HSC, a pass-through cart with 2 KiB of
battery-backed RAM, unreleased in the 1980s and later reissued by homebrewers; a set of Atari
titles detect it, Centipede, Asteroids, Joust and Food Fight among them) and the
**SaveKey/AtariVox** used by homebrew. The only runnable core, ProSystem, emulates neither.

## Evidence

ProSystem 1.3e 8a88014 booted Centipede (USA), an HSC title, with the 7800 BIOS
(`7800 BIOS (U).rom`, md5 0763f1ff..., from a Pocket's `Assets/7800/common/7800bios.bin`) and
reported **save RAM 0 bytes**; no file appeared in the save, system or working directory.

From `libretro/prosystem-libretro` (`core/libretro.c`, `core/Cartridge.c`):
`retro_get_memory_data` returns only `RETRO_MEMORY_SYSTEM_RAM`; there is no HSC code (no
`hiscore.rom` loading, no 0x1000-0x17FF save RAM mapping) and no SaveKey. The core's only
external files are `7800 BIOS (U).rom` / `7800 BIOS (E).rom`. So there is no ProSystem save to
make, for any game.

## Games x cores

| Game | prosystem |
| --- | --- |
| (none possible: ProSystem has no HSC or SaveKey) | - |

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
