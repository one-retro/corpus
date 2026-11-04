# PC Engine / TurboGrafx-16 (HuCard)

Nine games, four runnable libretro cores: 36 played entries, all filed and every proof.png
checked by eye. HuCards have no battery of their own. Every game here except Populous saves to
the 2 KiB backup RAM ("BRAM", the file cabinet) of a CD-ROM² unit, Turbo Booster-Plus, Tennokoe
2 or Duo. The libretro cores emulate that unit for every HuCard by default. Populous is the one
card with RAM on the cartridge, and it is the case where the cores really disagree.

The cores agree on the size (2048) and the name (`<ROM stem>.srm`). They disagree on one header
byte, and on whether Populous keeps its backup-RAM file at all. No core wrote a `.sav`, a
`.bram` or any other extra file for a HuCard.

## The ten games (nine)

The save hardware is the same for all of them (2 KiB BRAM), apart from Populous. So the variety
comes from the file system inside it: file sizes from 18 to 428 bytes, one file or two per game,
fixed names or numbered slots, a non-zero file ID, and saves written by a menu, by a game-over
screen, or by the game on its own.

| Game (No-Intro) | BRAM file(s) the game wrote | Why | Script ends with (proof) |
| --- | --- | --- | --- |
| Neutopia (USA) | `NEUTOPIA1 ` 48 B (one of four cabinet slots) | 1Retro has a Neutopia parser; the classic HuCard save | after a reset, CONTINUE > File Cabinet: "Which file do you want to use? NEUTOPIA 1" |
| Dungeons & Dragons - Order of the Griffon (USA) | `GRIFFON 1 ` 428 B, the largest here | an RPG party save; US-only | SAVE GAME menu: "GRIFFON 1 -FULL-", slots 2-4 FREE |
| Davis Cup Tennis (USA) | `SLAYER 1  ` 225 B (the player's name is the file name) | a user-named file | after a reset, LOAD lists "SLAYER 1" |
| Bomberman '93 (USA) | `BOMBER93-1` 32 B | a continue-menu save; popular | "WHICH FILE TO SAVE TO? 1 BOMBER-93 A-1 ... OK" |
| Chew-Man-Fu (USA) | `CHEW-SR   ` 18 B **and** `CHEW  -01 ` 88 B | two files from one game (an index and an edit-mode room) | FILE CABINET with ROOM 01 lit |
| Jack Nicklaus' Turbo Golf (USA) | `JGF-SG.001` 302 B, **file ID 0x0B00** in the name field | a round in progress; the only file with a non-zero ID | after a reset: "Resume Saved Game? Yes or No" |
| Night Creatures (USA) | `NC3`, `NC2` 56 B each | save at the game-over menu; the game also writes slot 3 when SAVE AS opens | RESTORE GAME menu (the bytes show NC2 and NC3) |
| Darius Plus (Japan) (SG Enhanced) | `DARIUS.SCR` 276 B, file ID 0x0009 | the SuperGrafx-enhanced card that saves; the file is created during the first game (not at power-on, checked) | HISCORE RANKING after GAME OVER |
| Populous (Japan) | geargrafx: `POPULOUS. ` 84 B in BRAM. Beetle: the 32 KiB card RAM | the only HuCard with its own RAM | the world being played |

Scripts are in `scripts/pcengine/`. They all run from power-on with the cores' default options,
on plain `retro-run` (no options files).

Picked and swapped out (timeboxed):
- Neutopia II: the save woman was not in the first three houses of the first town.
- Super Volleyball: team edit takes six players. The sixth (the setter) would not take a
  uniform number.
- Falcon: menu input timing was erratic. The game writes `FALCON.HIS` (76 B) at power-on and
  `FALCON.SAV` (96 B) when LOAD GAME is opened.
- World Sports Competition: the name entry fought back. Writes `WS-RESULT` (160 B) at power-on.
- Soldier Blade: writes `SOLDIBLADE` (79 B, three score tables) at power-on, and its 2-minute
  table needs 100,000 points.
- Cratermaze: no continue menu was reached. It writes `CRATERMAZE` (17 B) by itself.
- Devil's Crush: no save prompt found by mashing.
These are all leads for the future: each writes a BRAM file with a different name and size.

Darius Plus and Populous are Japanese. Populous is the only card with on-card RAM. Darius Plus
is the only SuperGrafx-enhanced card in the set that saves.

## Games x cores

| Game | beetle-pce | beetle-pce-fast | beetle-supergrafx | geargrafx |
| --- | --- | --- | --- | --- |
| Neutopia | filed | filed | filed | filed |
| D&D Order of the Griffon | filed | filed | filed | filed |
| Davis Cup Tennis | filed | filed | filed | filed |
| Bomberman '93 | filed | filed | filed | filed |
| Chew-Man-Fu | filed | filed | filed | filed |
| Jack Nicklaus' Turbo Golf | filed | filed | filed | filed |
| Night Creatures | filed | filed | filed | filed |
| Darius Plus | filed | filed | filed | filed |
| Populous | filed (32 KiB card RAM, **no BRAM**) | filed (same) | filed (same) | filed (2 KiB BRAM, card RAM not saved) |

| Core | Status |
| --- | --- |
| agg23-pc-engine (openFPGA) | not runnable. The device-backup worker filed the owner's Pocket saves (Devil's Crush, Neutopia x2), not touched here. See "Downloaded entries and leads" |
| turbografx16-mister (MiSTer) | not runnable here. One downloaded entry (Soldier Blade, birdybro). See "Downloaded entries and leads" |
| mednafen (standalone) | not runnable here (GUI). See "Downloaded entries and leads" |

Core builds: Beetle PCE v1.29.0 b96c11e, Beetle PCE Fast v1.31.0.0, Beetle SuperGrafx v1.29.0
9c11dcd, Geargrafx 1.8.7. No BIOS is needed for HuCards.

## How each core writes the save

| | beetle-pce, beetle-pce-fast, beetle-supergrafx | geargrafx |
| --- | --- | --- |
| File | `<ROM stem>.srm`, 2048 B | `<ROM stem>.srm`, 2048 B |
| Empty BRAM as the core formats it | `48 55 42 4D 00 88 10 80`, then 0x00 to the end | `48 55 42 4D 00 A0 10 80`, then 0x00 |
| Header pointer at 4-5 (end of BRAM) | **0x8800**: 2 KiB at $8000, as the hardware has | **0xA000**: an 8 KiB BRAM, though only 2 KiB exist and are saved (`k_backup_ram_init_string` in src/memory.h; `memset(m_backup_ram, 0xFF, 0x2000)` then zeroes the first 0x800) |
| Unused space | 0x00 | 0x00 |
| Populous | `.srm` is the **32 KiB card RAM** (`retro_get_memory_data` returns `PopRAM` when `IsPopulous`). Mednafen's huc.cpp maps **no BRAM at all** for Populous (`UseBRAM` stays false), so the game's `POPULOUS.` file never exists | `.srm` is the 2 KiB BRAM with the game's `POPULOUS.` file (84 B). The 32 KiB card RAM is emulated ("Media has 32KB of cartridge RAM") but **not saved anywhere** |
| Options | no BRAM option for HuCards | `geargrafx_backup_ram` = Enabled (default) / Disabled. `geargrafx_mb128` = Auto (default): an MB128 is plugged in only for titles in its database (all CD games). It writes `geargrafx_mb128.sav`, **one file for every game**, into the save directory. Not triggered by any HuCard here |

**Header byte 5 is the only difference** between the four cores' files for six of the nine
games. Bomberman '93, Chew-Man-Fu, Davis Cup, D&D, Night Creatures and Darius Plus are
byte-identical across all three Beetle cores, and Geargrafx's file differs only at offset 5
(0x88 vs 0xA0).
- Neutopia: the password bytes inside the file differ between cores (24-26 bytes; Beetle PCE
  Fast and Beetle SuperGrafx are identical to each other). The password depends on game timing.
- Jack Nicklaus: 8 bytes differ, plus the entry checksum.
- Populous: no common format at all (see the table above).

Cross-loading works both ways. Geargrafx's Neutopia `.srm` (end pointer 0xA000) loaded into
Beetle PCE Fast, and Beetle PCE's loaded into Geargrafx, both show "NEUTOPIA 1" in the file
cabinet. Not tested: a game that trusts the 0xA000 end pointer when it computes free space, on
a core that has only 2 KiB.

**The BRAM file system as written (for a parser).**
- Header: "HUBM", u16 LE end pointer, u16 LE next-free pointer (logical, base $8000: used bytes
  = pointer - 0x8000), 8 zero bytes.
- Entries from 0x10: u16 LE total length (16-byte header included), u16 LE checksum, u16 file ID,
  10-byte name (space padded), data.
- The checksum is the two's complement of the 16-bit sum of the entry from byte 4 (ID, name and
  data) to its end. It held for all ten entries checked.
- A zero length ends the list.
- IDs seen: 0x0000 for most, 0x0B00 (bytes `00 0B`) for Jack Nicklaus, 0x0009 (bytes `09 00`)
  for Darius Plus.

**Beetle and `.sav`.** The brief expected Beetle to write a `.sav` of its own. None of the three
Beetle libretro cores does. Their `MDFN_MakeFName` only resolves firmware paths, and the
`MDFN_DumpToFile(... "sav" ...)` calls in mednafen/pce/huc.cpp are commented out. The `.sav` is
standalone Mednafen's (`<stem>.<md5>.sav`, written only when `IsBRAMUsed()`, i.e. the BRAM
differs from the freshly formatted state; for Populous the 32 KiB `PopRAM`).

## Runner notes

No harness problems. `retro-run` played everything with default options. Two things matter when
writing scripts:
- Some games read the pad only a while after a screen appears (Bomberman's file list, Falcon's
  menus), so a press that comes early is lost.
- Night Creatures takes SAVE on RUN, not button I.

## Downloaded entries and leads

**Filed: `turbografx16-mister/Soldier Blade (USA)/`.** It comes from birdybro's zip of a whole
MiSTer saves folder, attached to euan-forrester/save-file-converter issue #80 on 2022-03-02 (the
same zip the fds worker used). The file is in `saves/TGFX16` and dated 2021-06-06.

What the file shows about the MiSTer format:
- It is a raw 2048-byte BRAM, with no padding and no MB128 part.
- The header is `HUBM 00 88 5F 80`, the same 0x8800 end pointer as Beetle.
- It is **byte-identical** to the file beetle-pce-fast writes after booting Soldier Blade to the
  title. The game creates its `SOLDIBLADE` score file at power-on, and the scores are the
  defaults. So this is genuine core output, but not a played state.

The rest of the zip's HuCard saves are not filed:
- Neutopia II, Bomberman (USA), Devil's Crush and Dragon's Curse are all the empty formatted
  BRAM (`HUBM 00 88 10 80`, sha1 21c54249ad98...).
- That is byte-identical to the agg23 Pocket's Devil's Crush save already filed here.
- So MiSTer, the Pocket core and the three Beetle cores all format the BRAM the same way.
  Geargrafx is the odd one out (0xA000).

The zip's CD saves are passed to the pcenginecd worker.

Leads not filed:
- The MiSTer core author says that with MB128 enabled, the `.sav` is the 2 KiB BRAM followed by
  the 128 KiB MB128, 130 KiB in all (MiSTer-devel/TurboGrafx16_MiSTer issue #79). No such file
  was found.
- The issue attachments in that repo are all CD games (#87, #95, #133, #165, #240).
- `fullmem.zip` and `MB128_savefiles.zip` were made by other tools or devices, not by the core.

Nothing was found for agg23-pc-engine beyond the owner's own saves, or for standalone mednafen
(older builds gzip their `.sav`). Searched: the agg23/openfpga-pcengine issues and trees, GitHub
code, commit and repo search, archive.org, Reddit, the mednafen forum and speedrun.com.
misterfpga.org search needs a login.
