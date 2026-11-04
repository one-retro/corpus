# Atari 5200

Nothing filed. The 5200 has no battery RAM and no 5200 cartridge carries any; the library (No-Intro,
71 games) has nothing that saves, and no homebrew exception is known for the 5200 (the flash and
EEPROM carts below are 8-bit computer carts). Nothing to make, nothing to download.

## Evidence

Pac-Man (USA) was booted in both runnable cores with no BIOS file on hand (none on the drive:
searched for `5200.rom` and variants); both still ran the game.

| Core | Build | Result |
| --- | --- | --- |
| a5200 | a5200 2.0.2 40c6f2f | runs; **save RAM 0 bytes**, no file written anywhere |
| atari800 | Atari800 7.0.0 4e7fbc7 | runs; **save RAM 0 bytes**, no file written in the save, system or working directory |

Atari800's strings list writable computer cartridges (Atarimax 128 KB / 1 MB flash, Corina with
8K EEPROM, Flash MegaCart 4 MB); those belong to the 400/800/XL/XE side, which this registry
system does not cover.

## Games x cores

| Game | a5200 | atari800 |
| --- | --- | --- |
| (none: nothing in the system saves) | - | - |

| Core | Status |
| --- | --- |
| atari800-mister (MiSTer) | not runnable. In 5200 mode nothing saves. (Its 8-bit computer mode can write flash carts back to the CAR/ROM file since March 2026, per the README; not this system.) Nothing to find |
