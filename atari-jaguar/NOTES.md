# Atari Jaguar

One runnable core (Virtual Jaguar, libretro), one kind of save hardware (the cartridge's 93C46
serial EEPROM: 64 x 16-bit words, 128 bytes), five games with a genuine save, all filed. The
interesting part is not the five files, which all have the same shape, but how Virtual Jaguar has
stored this EEPROM over the years: three different layouts under two different names, the
current one big-endian and zero-filled when the game never writes.

## The five games

Every Jaguar cart in the library that saves uses the same 128-byte EEPROM, so there is no save
hardware variety to pick for. The games were picked for a quick save that is a real decision of
the player (a created slot, a saved game, a changed option), not the format a game writes when it
first sees a blank EEPROM. Each script then resets the console and shows the save read back.

| Game (No-Intro) | Save | Script ends with (proof) | Bytes the save changed |
| --- | --- | --- | --- |
| Rayman (World) | creates save slot 1 (B on an empty slot makes "AAA", 3 lives, 5 continues) | after a reset, PLAYER SELECT shows 1: AAA | slot header `4B 58` "KX", name "aaa " at 0x02 |
| Alien vs Predator (World) | a saved game: Pause, Option, GAME 1, B - SAVE, in the first Alien level | after a reset, RESTORE GAME lists RESTORE GAME 1, then [NO GAME] twice | 50 non-zero bytes; nothing was written before the save |
| Tempest 2000 (World) | GAME OPTIONS > DISPLAY SETUP: FAT VECTORS to SKINNY VECTORS | after a reset, DISPLAY OPTIONS shows SKINNY VECTORS | byte 0 `01`->`03`, checksum byte 0x7C `69`->`6B` |
| Doom (World) | start menu: Difficulty Hurt me plenty -> Ultra-Violence, then start a game | after a reset, the start menu shows Ultra-Violence | byte 3 `02`->`03`, byte 0x0F (checksum) |
| Iron Soldier (World) | OPTIONS: DIFFICULTY MEDIUM -> HARD, QUIT | after a reset, OPTIONS shows HARD | byte 0x1B `01`->`02`, byte 3 (checksum) |

The "bytes changed" column compares the filed file with a dump taken just before the decisive
press, in the same run. Tempest 2000 writes nothing at power-on; it writes the whole EEPROM
(settings, the Top Guns table, a checksum) when the options are first opened and again when they
are left. Doom, Iron Soldier and Rayman format a blank EEPROM at power-on, so their files would be
non-zero even without the save; the scripts' saves change bytes on top of that.

Scripts: `scripts/atari-jaguar/*.txt`. They use the core's default pad mapping, which is not the
obvious one (from `libretro.c`): RetroPad B = Jaguar B, A = A, **Y = C**, **Select = Pause**,
**Start = Option**, X = keypad 0, L/R/L2/R2/L3/R3 = keypad 1-6. No options file is needed.

## Games x cores

| Game | virtual-jaguar |
| --- | --- |
| Rayman | filed |
| Alien vs Predator | filed |
| Tempest 2000 | filed |
| Doom | filed |
| Iron Soldier | filed |

5 of 5 attempted, every proof.png checked by eye. The registry has no non-runnable Jaguar cores,
so nothing was searched for online. (BigPEmu and the standalone Virtual Jaguar are not registry
cores.)

Core build: Virtual Jaguar v3.11.0 34696082 (libretro buildbot, 2026-11-02), HLE BIOS (the
default; the boot ROMs are built into the core, no BIOS file needed).

Tried and dropped, each for a stated reason:
- Atari Karts: OPTIONS > ENTER NAME ONE takes a name, but leaving the options writes nothing; the
  EEPROM holds best-lap records ("PHiL" x n), so a save needs a finished race.
- Super Burnout: OPTIONS (drones, laps) are not written to the EEPROM; it keeps BEST RACERS.
- Breakout 2000: the settings panel is not written on change or on START.
- Missile Command 3D: never writes at power-on or from OPTIONS (MUSIC TEST, CLEAR MEMORY, VIRTUAL
  CONTROLS); only a high score would, or CLEAR MEMORY, which only writes defaults.
- Zoop: menus too slow to reach in the time box. Theme Park (5 park slots) not tried; whether a
  park fits in 128 bytes, or the cart has a bigger EEPROM the core does not emulate, is open.

Which games touch the EEPROM on their own: all 46 carts in the library were run for ~3300 frames
with a few Start/B/A presses. 34 wrote the EEPROM (mostly a format of the blank chip with default
settings and high-score tables); 12 did not: Alien vs Predator, Brutal Sports Football, Bubsy,
Cybermorph, Fever Pitch Soccer, Flip Out!, Hover Strike, Missile Command 3D, Syndicate, Theme
Park, Towers II, Zool 2. With no input at all for 3300 frames, Tempest 2000 writes nothing;
Zoop, Iron Soldier, Doom, Defender 2000, Breakout 2000, Pinball Fantasies and Super Burnout write
the same bytes they write with input.

## How Virtual Jaguar stores the EEPROM

Current build (v3.x, since commit 0505cdd5e, 2026-04-03, "Use libretro SRAM interface for save
data persistence"):

- **Name and place**: the frontend's battery save, `<savedir>/<ROM stem>.srm`. The core writes no
  file of its own.
- **Size**: 128 bytes for a cartridge. For a Jaguar CD disc, 131328 bytes (128 cart EEPROM +
  128 CD-unit EEPROM + 131072 Memory Track NVRAM); for the Memory Track cartridge image itself
  (CRC32 FDF37F47), its 131072 bytes raw. See `atari-jaguar-cd/NOTES.md`.
- **Byte order**: big-endian words, i.e. the chip's word order. Text in the EEPROM reads straight
  through: Iron Soldier's file has "IronSold v #0003" at 0x1C, Rayman's "KXaaa ".
- **Unwritten EEPROM is all 0x00, not 0xFF.** The core packs the EEPROM into the save buffer only
  when the game writes it; until then the buffer is the zeros it was cleared to. A game that never
  writes produces a 128-byte all-zero `.srm` (Tempest 2000 after 1200 idle frames, Alien vs
  Predator until the save). Worse, the buffer is unpacked into the emulated chip on the first
  frame whether or not a save was loaded, so a fresh game sees an EEPROM of zeros where a blank
  93C46 reads 0xFFFF. A tool that creates an "empty" Jaguar save should write zeros to match what
  this core makes, and should not treat an all-zero file as a real save.
- The EEPROM survives `retro_reset` (the scripts rely on it).

Older builds, worth knowing because their files are still on people's disks (from the source at
the parent of 0505cdd5e, and libretro/virtualjaguar-libretro issue #8):
- Before ~2014: the core wrote `<CRC32>.eeprom` into the frontend's working directory (issue #8,
  "written as _crc_.eeprom in the same directory as retroarch.exe").
- Until 2026-04: the core wrote `<savedir>/<ROM basename>.srm` itself, big-endian, on every EEPROM
  write or erase, plus `<ROM basename>.cdrom.srm` for the CD unit. **At the same time** it exposed
  its in-memory `uint16_t eeprom_ram[64]` as `RETRO_MEMORY_SAVE_RAM`, so RetroArch wrote
  `<stem>.srm` too, in host byte order: **little-endian words** on x86 and ARM. Same file name,
  two byte orders, last writer wins (normally the frontend, on exit). An old Jaguar `.srm` may
  therefore be either word order; text in it ("XKaa a" instead of "KXaaa ") tells which.

## Downloaded entries and leads

None. No non-runnable registry core exists for this system.
