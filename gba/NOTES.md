# Game Boy Advance

Ten games, six runnable libretro cores, every save type the GBA has. All 60 (game, core) pairs
were filed, plus three downloaded saves from two FPGA cores. The cores disagree on file size,
on the name of the file, on where EEPROM data sits, on its byte order, and on whether the clock
is kept at all. Those differences are written up below.

## The ten games

The save type comes from the library string in each ROM. The EEPROM size is not in that string,
so it was checked twice: mGBA sized it from the game's own DMA, and the data never goes past
0x200 in Klonoa's file.

| Game (No-Intro) | Save hardware | Why | Script ends with (proof) |
| --- | --- | --- | --- |
| Kirby - Nightmare in Dream Land (USA) | SRAM_V112, 32 KiB SRAM | popular; the file is written as soon as the adventure starts | GAME SELECT shows FILE1 "Water Drop" after a power cycle |
| Fire Emblem (USA, Australia) | SRAM_F_V102, 32 KiB FRAM | popular, and FRAM rather than SRAM | slot 1 "Prologue: A Girl from the Plains" |
| Klonoa - Empire of Dreams (USA) | EEPROM_V121, **512 B** (4 Kbit) | the one 4 Kbit game here with a quick genuine save (picking a file writes it). SMA1, Dr. Mario + Puzzle League, Donkey Kong Country and Denki Blocks are also 512 B, but none of them saves quickly | "Select a Save file" shows the Prologue file |
| Legend of Zelda, The - The Minish Cap (USA) | EEPROM_V124, 8 KiB (64 Kbit) | popular; naming a file writes it ("Saving file...") | CHOOSE A FILE shows the file |
| Boktai - The Sun Is in Your Hand (USA) | EEPROM_V122 8 KiB + **SIIRTC_V001** + solar sensor | a clock cartridge that isn't Pokémon, and EEPROM rather than flash | DATA.1 "DjangoAAAA, Road of Encounter" |
| Sonic Advance 2 (USA) (En,Ja,Fr,De,Es,It) | FLASH512_V130, 64 KiB flash | 64 KiB flash; the first boot asks for a name and saves it | OPTIONS shows PLAYER DATA "v" |
| Pokemon - FireRed Version (USA, Europe) (Rev 1) | FLASH1M_V103, 128 KiB flash, no clock | 128 KiB flash without the clock, to set against R/S/E | CONTINUE, player AAAAAAA |
| Pokemon - Emerald Version (USA, Europe) | FLASH1M_V103 + **SIIRTC_V001** | the clock game people actually play | CONTINUE, player AAAAAAA |
| Pokemon - Ruby Version (USA, Europe) (Rev 2) | FLASH1M_V103 + **SIIRTC_V001** | the game behind clocks.json's mGBA evidence (a Ruby footer) | CONTINUE, player AAAAAAA |
| Super Mario Advance 4 - Super Mario Bros. 3 (USA, Australia) (Rev 1) | FLASH1M_V102, 128 KiB flash (the older chip string) | 128 KiB flash outside Pokémon; the game formats all 128 KiB | Select a File shows File 1 [Continue] WORLD 1 |

The scripts are in `scripts/gba/`. Every one runs from power-on, saves inside the game, then
**power-cycles**: `dump cycle.srm`, `reset`, `srm cycle.srm`. The reset is there so the proof
shows the game reading its save back. The dump and reload are there because SkyEmu's
`retro_reset` wipes its save memory (see below). `cycle.srm` is written into the run directory,
never the save directory, so it is not filed. A core that keeps its save memory across a reset
reloads identical bytes. Beetle GBA exposes no save region, so for it the dump and reload do
nothing.

Variant scripts and options:
- `Pokemon - Ruby Version.gpsp.txt` and `Pokemon - Emerald Version.gpsp.txt` add two A presses
  before the proof. After gpSP's `retro_reset` the game shows "The internal battery has run
  dry" and then "However, clock-based events will no longer occur.".
- `skyemu.opt` is passed to every SkyEmu run. Without it SkyEmu crashes (see Runner problems).

## Games x cores

All 60 played entries are filed: 10 games x 6 cores, every proof.png checked by eye. The
non-runnable cores are at the end of the table.

| Game | beetle-gba | gpsp | mgba | skyemu | vba-m | vba-next |
| --- | --- | --- | --- | --- | --- | --- |
| Kirby NiDL | filed | filed | filed | filed | filed | filed |
| Fire Emblem | filed | filed | filed | filed | filed | filed |
| Klonoa | filed | filed | filed | filed | filed | filed |
| Minish Cap | filed | filed | filed | filed | filed | filed |
| Boktai | filed | filed | filed | filed | filed | filed (game says "Solar Sensor is broken." after saving) |
| Sonic Advance 2 | filed | filed | filed | filed | filed | filed |
| FireRed | filed | filed | filed | filed | filed | filed |
| Emerald | filed | filed (gpsp variant) | filed | filed | filed | filed |
| Ruby | filed | filed (gpsp variant) | filed | filed | filed | filed |
| SMA4 | filed | filed | filed | filed | filed | filed |

| Core | Status |
| --- | --- |
| gba-mister (MiSTer) | not runnable. 2 downloaded: Pokemon - Smaragd-Edition (Germany), Mario & Luigi - Superstar Saga (USA) |
| mincer-ray-gba (openFPGA) | not runnable. 1 downloaded: Pokemon - Emerald Version (USA, Europe), in the legacy appended-clock form |
| spiritualized-gba (openFPGA) | not runnable. Nothing filed; leads below |
| mednafen (standalone) | not runnable (GUI). Nothing found. Its file format should match beetle-gba's mednafen save method (`<stem>.<md5>.sav/.eep`), but that is unverified |
| tempgba (libretro, no macOS build) | not runnable. Nothing found |

Core builds used: Beetle GBA v0.9.36 b158166, gpSP v1.1.0-5819380, mGBA 0.11-212-7a12d6d,
SkyEmu adacd078, VBA-M 115defb, VBA Next v1.0.2. The BIOS (`gba_bios.bin`, sha1 300c20df…) was
in the system directory for every run. Beetle GBA's `gba_hle` option defaults to enabled, so it
presumably ran its HLE BIOS anyway. SkyEmu looks for the BIOS in `system/SkyEmu/gba_bios.bin`
and logged that it was using its bundled one. I did not check which BIOS the other four used.
None of this changes the save files.

## How each core writes the save

| Core | File names | SRAM/FRAM 32K | EEPROM 512 B | EEPROM 8 KiB | Flash 64K | Flash 128K | Clock |
| --- | --- | --- | --- | --- | --- | --- | --- |
| beetle-gba | `<ROM stem>.<ROM md5>.sav` / `.eep`, written by the core itself into the save dir; `RETRO_MEMORY_SAVE_RAM` is 0 so there is no `.srm` | `.sav` **65536**: data in the first 32 KiB, upper 32 KiB 0xFF | `.eep` **512**, plus a **blank 65536-byte `.sav`** (all 0xFF) | `.eep` 8192 + the same blank 64 KiB `.sav` | `.sav` 65536 | `.sav` 131072 | none written |
| gpsp | `<stem>.srm` | **131072**, data at 0, rest 0xFF | 131072 | 131072 | 131072 | 131072 | none (`RETRO_MEMORY_RTC` 0) |
| mgba | `<stem>.srm` | 32768 | 512 | 8192 | 65536 | 131072 | **none**: Ruby/Emerald `.srm` is exactly 131072, Boktai's exactly 8192 |
| skyemu | `<stem>.srm` + `<stem>.rtc` | **131072** (`cart_backup[128K]`), rest 0xFF | 131072 | 131072 | 131072 | 131072 | `.rtc` **48 bytes, for every game**, clock or not |
| vba-m | `<stem>.srm` | 32768 | 512 | 8192 | 65536 | 131072 | none |
| vba-next | `<stem>.srm` | **139264 (0x22000)**, data at 0 | 0x22000, data at **0x20000** | 0x22000, data at **0x20000** | 0x22000, data at 0 | 0x22000, data at 0, last 8 KiB 0xFF | none |

All unused space is 0xFF in every core. No core fills with 0x00.

**EEPROM byte order.** SkyEmu stores EEPROM with every 8-byte block reversed compared with all
the others. Minish Cap in mGBA starts `41 44 4C 45 5A 42 47 41` ("ADLEZBGA"); in SkyEmu it
starts `41 47 42 5A 45 4C 44 41` ("AGBZELDA"). After reversing each 8-byte block, SkyEmu's
Klonoa and Minish Cap are byte-identical to Beetle GBA's, gpSP's and VBA-M's. This was tested
both ways:
- SkyEmu's Minish Cap `.srm` loaded into mGBA: the game finds no file and asks for a name.
- The same file with its blocks reversed: mGBA shows the file.
- mGBA's `.srm` loaded into SkyEmu: no file.

The MiSTer save downloaded here (Mario & Luigi) and the one-saves reference mincer_ray Minish
Cap use the conventional order. Of everything seen, SkyEmu alone reverses the blocks.

**Same play, same bytes.** After trimming each file to the chip's size (and VBA Next's EEPROM
from 0x20000):
- Kirby, Klonoa and SMA4 are byte-identical across all six cores.
- Minish Cap is identical in four cores. mGBA and VBA Next named the file "AABC" instead of
  "AAABC" (a press landed on the title), which changes 14 bytes.
- Fire Emblem varies by 2 bytes.
- Boktai varies by 9-16 bytes. gpSP and VBA Next store 0 where the others store the
  solar-sensor reading (0xE7).
- The Pokémon saves differ by hundreds of bytes, as expected (trainer ID and RNG).
These files are a good set for testing size and offset normalisation, because the content
underneath is the same.

**Beetle GBA's save method.** The option `gba_use_mednafen_save_method = libretro` (default
`mednafen`) switches Beetle to a 0x22000 `.srm`, EEPROM at 0x20000, the same as VBA Next (both
descend from VBA). Checked in dry runs of Klonoa, Kirby and Minish Cap; not filed, since the
filed entries use defaults. VBA-M's libretro core used to write 136 KiB for every type too
(libretro forum threads). This build writes exact sizes.

## The clock, against one-saves-registry's clocks.json

None of the six libretro cores keeps the S-3511A clock inside the save. Five keep no clock at all.

| Core | Here | clocks.json | |
| --- | --- | --- | --- |
| mgba | nothing: no footer, `RETRO_MEMORY_RTC` 0; the game reads the host clock | `appended`, width 8, from "a real Pokemon Ruby footer" | **disagrees for the libretro core.** The 16-byte footer is what mGBA writes when it owns the save file (the standalone app). The libretro core exposes only the bare chip, and RetroArch's `.srm` from it has no clock. A Ruby `.srm` from RetroArch's mGBA is plain 131072 bytes |
| vba-m | nothing | `appended`, width 8 (from Game Boy MBC3 evidence) | **disagrees for the GBA**: the libretro VBA-M writes no GBA clock |
| skyemu | `.rtc` sidecar, 48 bytes, written for **every** game | absent | **new.** It is a raw dump of SkyEmu's `gba_rtc_t` (src/gba.h at adacd078), little-endian: `u32 serial_state`, `u32 serial_bits_clocked`, `u64 input_register`, `u64 output_register`, `u32 state` (0x00-0x1B, all zero in these files), `u8 status_register` at **0x1C** (0x40 in Boktai/Ruby/Emerald, i.e. 24-hour mode as the game set it; 0x00 in non-clock games), 3 bytes padding, `u64 initial_rtc_time` at **0x20** (`time(NULL)` when the ROM was loaded, e.g. 0x6AEADA9F = 2026-11-04 07:11 UTC), `u64 total_clocks_ticked` at **0x28**. The game reads `initial_rtc_time + total_clocks_ticked / 2^24` (gba.h:1042), so a restored `.rtc` resumes from the moment it was saved: time spent powered off is lost |
| gpsp | nothing; `gpsp_rtc_time_source` defaults to `deterministic` (the clock follows emulated frames, so it is not even the host's) | absent | fine |
| beetle-gba, vba-next | nothing | absent | fine |
| gba-mister | downloaded Smaragd: 0x20200 bytes, the 512 bytes after 0x20000 are **32 identical 16-byte records** (`54 52 00 A2 …`) | `packed`, reserved 512, timestamp 4 | **agrees** |
| mincer-ray-gba | downloaded Emerald (April 2026): 131088 = 128 KiB + **16 appended bytes**, starting with a u32 LE Unix time (0x69EE6B09 = 2026-04-26 19:44:09 UTC, the file's own date) | `sidecar` (16-byte `.rtc`) | **agrees for 0.8.0+, but the core's README says ≤0.7.1 appended the same 16 bytes to the `.sav`**. Saves in that legacy form are still around (this one, and the kf_savs lead below, including non-clock games that got the 16 bytes by mistake). clocks.json could carry both |

What the games did with the clock:
- **gpSP's `retro_reset`** leaves the clock reading as stopped, so Ruby and Emerald report a dry
  battery after the in-run power cycle. Booting gpSP fresh with the same `.srm` shows CONTINUE
  with no message, so the save is fine and the reset is the cause.
- In all other cores, and in gpSP on a fresh boot, Ruby and Emerald start cleanly. Each
  core's own Ruby save was booted fresh, and all six reached CONTINUE.

## Runner problems (worked around, nothing in tools/ changed)

- **SkyEmu segfaults in `load_rom` → `opts_reload_all` (strcmp on NULL)** unless every option has
  a value. retro-run answers `GET_CORE_OPTIONS_VERSION` with 0, and SkyEmu never sends
  `SET_VARIABLES`. Its `GET_VARIABLE` calls then fail with a NULL value, which SkyEmu passes to
  strcmp unchecked. Fix: `--options scripts/gba/skyemu.opt` sets `system_core_override`
  and the three `*_bios_enable` keys. retro-run could take its option defaults from
  `SET_CORE_OPTIONS_V2` (or report version 2) to cover such cores.
- **SkyEmu's `retro_reset` throws away save memory.** It reloads the ROM, fills `cart_backup`
  with 0xFF and looks for a save file of its own ("Could not find save file"), which the
  frontend never wrote. Hence the dump/reset/reload idiom in every script. In RetroArch, a reset
  in SkyEmu would lose unsaved progress the same way.
- One stray line in `status.jsonl` (beetle-gba, Kirby, rc 1, "No such file or directory",
  23:10:26) came from a mis-split batch command of mine. It is not a core failure.

## Downloaded entries

- `gba-mister/Pokemon - Smaragd-Edition (Germany)/`: attached by RobertPeip, the core's
  author, to [GBA_MiSTer #138](https://github.com/MiSTer-devel/GBA_MiSTer/issues/138) to show
  the clock appended at 0x20000. Not booted (no German ROM in the 1G1R set).
- `gba-mister/Mario & Luigi - Superstar Saga (USA)/`: the reporter's own save in
  [GBA_MiSTer #101](https://github.com/MiSTer-devel/GBA_MiSTer/issues/101); the core's author
  says "I used your savegame". The file is 8192 bytes and is dated 1980-01-01 00:00 UTC, the
  stamp a MiSTer without an RTC board puts on files. It loads unchanged in mGBA (file 1, 2:39).
  The origin is inferred, and the provenance says so.
- `mincer-ray-gba/Pokemon - Emerald Version (USA, Europe)/`: from
  [openfpga-GBA #24](https://github.com/mincer-ray/openfpga-GBA/issues/24). The game was started
  in mGBA and continued on the Pocket core; the file as attached is the core's legacy appended
  form. With the 16 bytes cut, it loads in mGBA (Patric, 27:07, 6 badges).

## Leads, not filed

- [openfpga-GBA #2](https://github.com/mincer-ray/openfpga-GBA/issues/2), `kf_savs.zip`. ROM
  hacks and Apotris, in three states:
  - "Initial Save", played on spiritualized-gba (plain 131072/32768);
  - "After m-r core", mincer_ray legacy builds (+16 appended bytes, even for non-clock games,
    a bug since fixed);
  - converted back with savefileconverter.
  Not No-Intro games, so not filed. The useful facts are recorded here.
- GBA_MiSTer attachments whose origin is unclear:
  - [#96](https://github.com/MiSTer-devel/GBA_MiSTer/issues/96) ALttP & Four Swords `.sav`
    (8 KiB, dated 2013, older than the core, so probably from an earlier emulator);
  - [#143](https://github.com/MiSTer-devel/GBA_MiSTer/issues/143) "Pokemon Fire Red Version (U).sav"
    (128 KiB, 2020-10-28);
  - [#20](https://github.com/MiSTer-devel/GBA_MiSTer/issues/20) "WarioWare Inc. (U).sav"
    (32 KiB, 2019-12-06).
  All are downloaded under `.cache/downloads/gba/`.
- spiritualized-gba: its issue tracker (73 issues, 170 comments) has no save attachments. An
  Analogue-Pocket community issue (frederic-mahe/Analogue-Pocket #125) describes all-0xFF
  Emerald `.sav` files after Memories, but attaches nothing.
- tempgba, mednafen standalone: a web search and the libretro forums turned up no files that
  could be attributed.
- Reference only, not copied: one-saves `data/saves` holds mincer_ray saves. Its Minish Cap is
  65536 bytes, i.e. 8 KiB EEPROM padded to 64 KiB, in conventional byte order. Its Emerald comes
  with a 16-byte `.rtc` sidecar (the 0.8.0+ form). There is also a gba-mister Ruby at 131584,
  the same packed 512-byte block as Smaragd.
