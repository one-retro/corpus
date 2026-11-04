# ColecoVision

Nothing filed. No ColecoVision cartridge from the console's lifetime has save memory (high
scores and settings are lost at power-off), and the library is the No-Intro retail set (139
games, no homebrew). The homebrew exceptions exist, and Gearcoleco emulates two of them.

## Evidence

Donkey Kong (USA, Europe) (v1.1) was booted in each runnable core with the BIOS
(`coleco.bin`, md5 00fd13b6..., from a Pocket's `Assets/coleco/Spiritualized.Coleco`, copied as
`coleco.rom` and `colecovision.rom`), from a fresh working directory.

| Core | Build | Result |
| --- | --- | --- |
| gearcoleco | Gearcoleco 1.7.6-8-g333b6c7 | runs; **save RAM 0 bytes**, no file written anywhere |
| jollycv | JollyCV 2.1.0 | runs; **save RAM 0 bytes**, no file written; no SRAM/EEPROM code in the core (nothing in its strings) |
| bluemsx | blueMSX | **refused the ROM**: blueMSX needs its `Machines/` and `Databases/` trees in the system directory (`Machines/COL - ColecoVision/...`), which are not on the drive. Not a save finding either way |

## The homebrew exceptions (Gearcoleco)

From `drhelius/Gearcoleco` (`src/game_db.h`, `StandardMapper.h`, `OCMMapper.h`,
`platforms/libretro/libretro.cpp`); the build used here carries the same database (its strings
include "Cartridge with SRAM", "Cartridge with OCM mapper" and the Opcode titles):

| Cartridge | Save memory | What Gearcoleco exposes as `RETRO_MEMORY_SAVE_RAM` (so `<stem>.srm`) |
| --- | --- | --- |
| Lord of the Dungeon (two CRCs; homebrew) | battery SRAM, 2 KiB mirrored through the cart window (`address & 0x7FF`) | 2048 bytes (`u8 m_SRAM[0x800]`) |
| Opcode Games carts on the OCM mapper (Amidar, DK Arcade, DK Jr. Arcade, Goonies, Gradius, Knightmare, Moon Cresta, Pacman DX, Penguin Adventure, Time Pilot (Opcode)) | serial EEPROM | 1024 bytes, initialised to 0xFF |

Every other cartridge returns save size 0. None of these is in the library (its "Time Pilot" is
Coleco's 1983 cart, not Opcode's).

## Games x cores

| Game | bluemsx | gearcoleco | jollycv |
| --- | --- | --- | --- |
| (none: no game in the library saves) | - | - | - |

| Core | Status |
| --- | --- |
| colecovision-mister (MiSTer) | not runnable. README documents save states only, no cartridge SRAM/EEPROM. Nothing to find |
| crabemu (standalone) | not runnable. Nothing found; no ColecoVision save support known |
| spiritualized-coleco (openFPGA) | not runnable. No save support documented; nothing found |

## Leads

- A played Gearcoleco save needs Lord of the Dungeon or an Opcode OCM cart (commercial homebrew).
