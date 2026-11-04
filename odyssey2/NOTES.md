# Odyssey 2 / Videopac

Nothing filed. The Odyssey 2 (Videopac G7000) and its successors (Videopac+ G7400, Jopac) have no
save memory, and no cartridge adds any: the library (No-Intro, 75 games) has nothing that saves,
and no homebrew exception is known. Nothing to make, nothing to download.

## Evidence

O2EM 1.18 679d6fe booted K.C. Munchkin (USA) with the BIOS (`o2rom.bin`, md5 562d5ebf..., the
standard Odyssey 2 BIOS, from a Pocket's `Assets/odyssey2/Spiritualized.Odyssey2/o2bios.bin`); it
reached the console's SELECT GAME screen and reported **save RAM 0 bytes**. No file appeared in
the save, system or working directory. The core's only external files are BIOS images
(`o2rom.bin`, `c52.bin`, `g7400.bin`, `jopac.bin`); its strings have nothing about SRAM, EEPROM,
NVRAM or high scores.

## Games x cores

| Game | o2em |
| --- | --- |
| (none: nothing in the system saves) | - |

| Core | Status |
| --- | --- |
| odyssey2-mister (MiSTer) | not runnable. README documents no save support. Nothing to find |
| spiritualized-odyssey2 (openFPGA) | not runnable. Nothing to find |
