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

## GameFAQs saves

On 2026-11-05 every GBA save on the GameFAQs pages of the corpus's GBA games was downloaded
(tools/GAMEFAQS.md): 376 files from the GameShark, GameShark SP, GameShark USB Connector and Pro
Action Replay sections of Pokemon Ruby/Sapphire/Emerald, FireRed/LeafGreen, Pokemon Pinball, Super
Mario Advance 4, Sonic Advance 2, Fire Emblem, Mario & Luigi, Castlevania Aria of Sorrow and Circle
of the Moon, Minish Cap, A Link to the Past & Four Swords, Wario Land 4, Boktai, Drill Dozer,
Klonoa and Bomberman Max 2. 375 are filed as `gba/_<device>/<release> [GameFAQs <id>]/`: the file
as GameFAQs served it, `provenance.json` (format, conversion, each core's file and result) and
`proof.png` (each core's frame, in the order mgba, vba-m, gpsp, vba-next, beetle-gba, skyemu). The
376th is not a GBA save (see the last part).

| Device dir | Files | What the bytes are |
| --- | ---: | --- |
| `_gameshark` | 291 | SharkPort `.sps` (GameShark sections); 7 of them malformed |
| `_action-replay` | 60 | SharkPort `.xps` (Pro Action Replay sections): the same format, named by its extension |
| `_gameshark-sp` | 7 | GameShark SP `.gsv` ("ADVSAVEG") |
| `_raw` | 15 | bare save images with no container, uploaded as `.sps` (6), `.xps` (3), `.gsv` (2), `.gsb` (4) |
| `_visualboyadvance` | 2 | gzip-compressed VisualBoyAdvance save states (`.sgm`, state versions 6 and 8), uploaded as `.gsv` and `.gsb` |

**Every save was booted in the release its bytes name.** A SharkPort header copies ROM 0xA0-0xBF:
title, game code, and the header complement byte, which tells revisions apart (Ruby (USA) 0x41,
Rev 1 0x40, Rev 2 0x3F). So a 2003 GameShark Ruby save is booted in `Pokemon - Ruby Version (USA)`,
not in the Rev 2 the played entries use. 182 of the 375 are for a release outside the No-Intro
1G1R set (European, Japanese, French, German and Chinese releases, earlier revisions, Virtual
Console); their ROMs came from a full No-Intro GBA collection, and no save was left without its
release. 22 saves sit in a GameFAQs region section that is not their release's (3 Japanese Sonic
Advance 2 saves under North America, US Pokemon saves under Europe, and so on). A `.gsv` names only
the 12-byte title, and a raw image nothing: those were given the section's region, and Pokemon
raw images the game their own save structure says (Emerald, Ruby/Sapphire or FireRed/LeafGreen).
Where a file does not say which revision, the revision the corpus uses was booted.

### Converting

Three converters in `tools/gamefaqs/`, standard library only:

- `gba-sharkport.py` reads SharkPort exactly as mGBA does (`src/gba/sharkport.c`): `u32 13,
  "SharkPortSave"`, `u32 0x000F0000`, three length-prefixed strings (title, date, notes), `u32 0x1C
  + payload size`, a 0x1C-byte cart header, the payload, a u32 checksum. It then imports the payload
  as mGBA's `_importSavedata` does: cut to the chip if larger; a payload of exactly 512 or 8192
  bytes (EEPROM) gets every 8-byte block reversed; the rest of the chip stays erased (0xFF).
- `gba-gsv.py` reads the GameShark SP format as mGBA does: payload at 0x430, its size from the
  type word (2 SRAM, 3 EEPROM 512, 4 EEPROM 8K, 5 flash 64K, 6 flash 128K, anything else the rest of
  the file). The same import follows. The second "unknown" word after the type equals the payload
  size in every file here.
- `gba-layout.py` lays the chip out as each core keeps it (the table "How each core writes the
  save" above): mGBA and VBA-M the bare chip; gpSP 128 KiB; SkyEmu 128 KiB with EEPROM blocks
  reversed; VBA Next 0x22000 with EEPROM at 0x20000; Beetle GBA `<stem>.<rom md5>.eep`, or a 64/128
  KiB `.sav`, put in its save directory before boot. It also takes the raw images as the chip
  (cut or padded with 0xFF, as mGBA maps a `.sav` of the wrong size). The chip type comes from the
  ROM's library string; EEPROM is 8 KiB except Klonoa's 512 B.

The other cores got their file the way RetroArch loads a `.srm`: copied into the core's save
memory after `retro_load_game`. Converted files stay in `.cache/gamefaqs-conv/gba/` (not
committed); provenance records each one's name, size and sha1.

What the SharkPort files say about their writers:
- Payload sizes: 64 KiB (252), 128 KiB (72), 32 KiB (12), 8 KiB (7), 512 B (1). The GameShark
  itself dumped only 64 or 128 KiB: VBA-M's importer refuses anything smaller. The exact-size
  payloads come from mGBA's exporter and from savefileconverter.com.
- The checksum (`sum += byte << (sum % 24)`) splits them in three. 212 files sum the bytes as
  signed chars, as VBA-M's exporter, mGBA's exporter (on x86) and the older GameShark software do.
  122 sum them unsigned: 57 of the 60 `.xps` files and 65 `.sps`, nearly all with the software's
  default title "Save<date> <n>". The 10 savefileconverter.com files match neither. mGBA does not
  test the checksum on import.
- Two `.sps` say "Exported from Visual Boy Advance-M" in their notes. They stay under `_gameshark`,
  because the file is a SharkPort container, not VBA-M's own save.

### Load scripts

`scripts/gba/<game>.load.txt` power on and stop on the screen that shows a save:
- Pokemon: the CONTINUE box. Sapphire, Emerald and the other releases use the Ruby script; LeafGreen
  uses FireRed's.
- SMA4: Select a File. Sonic Advance 2: OPTIONS, whose PLAYER DATA line shows the name.
- Fire Emblem: the title menu, where the chapter options appear only when there is a file.
- Pokemon Pinball: the POKeDEX.
- Elsewhere: the file select. Harmony of Dissonance uses Aria of Sorrow's script.
- Fire Emblem and A Link to the Past have `(Europe)` variants for their language screens.

Each was also run per core with no save, as the baseline. Things the scripts work around:
- Pokemon may say "The save file is corrupt(ed). The previous save file will be loaded." before the
  menu. The scripts shoot, press A (FireRed/LeafGreen: twice, its message has two pages) and shoot
  again.
- SMA4 reads its whole save at power-on. That takes about 450 frames for a whole save and about
  1500 for a 64 KiB GameShark dump. It may then report "Saved data is corrupted." part by part
  (seen with every part OK for the 64 KiB dumps). With no save it shows "Formatting saved data...".
  Its SMB3 title also swallows the first press.
- Pokemon Pinball's title ignores presses until about frame 2000.

### Results

`loads / rejected` per core:

| Game | saves | mgba | vba-m | gpsp | vba-next | beetle-gba | skyemu |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| Pokemon Pinball R&S | 6 | 6 / 0 | 6 / 0 | 6 / 0 | 6 / 0 | 6 / 0 | 6 / 0 |
| Pokemon R/S/E | 127 | 110 / 16 / 1 not run | 110 / 16 / 1 not run | 110 / 16 / 1 not run | 110 / 16 / 1 not run | 110 / 16 / 1 not run | 110 / 16 / 1 not run |
| Pokemon FR/LG | 68 | 48 / 20 | 48 / 20 | 48 / 20 | 48 / 20 | 48 / 20 | 48 / 20 |
| Super Mario Advance 4 | 35 | 33 / 2 | 33 / 2 | 33 / 2 | 33 / 2 | 33 / 2 | 33 / 2 |
| Sonic Advance 2 | 31 | 31 / 0 | 31 / 0 | 31 / 0 | 31 / 0 | 31 / 0 | 31 / 0 |
| Fire Emblem | 24 | 24 / 0 | 24 / 0 | 24 / 0 | 24 / 0 | 24 / 0 | 24 / 0 |
| Castlevania (AoS, CotM, HoD) | 32 | 31 / 1 | 31 / 1 | 31 / 1 | 31 / 1 | 31 / 1 | 31 / 1 |
| Minish Cap | 9 | 4 / 4 / 1 not run | 4 / 4 / 1 not run | 4 / 4 / 1 not run | 4 / 4 / 1 not run | 4 / 4 / 1 not run | 4 / 4 / 1 not run |
| ALttP & Four Swords | 6 | 4 / 2 | 4 / 2 | 4 / 2 | 4 / 2 | 4 / 2 | 4 / 2 |
| Mario & Luigi | 14 | 4 / 3 / 7 not run | 4 / 3 / 7 not run | 4 / 3 / 7 not run | 4 / 3 / 7 not run | 4 / 3 / 7 not run | 4 / 3 / 7 not run |
| Wario Land 4 | 9 | 9 / 0 | 9 / 0 | 9 / 0 | 9 / 0 | 9 / 0 | 9 / 0 |
| Boktai | 7 | 2 / 5 | 2 / 5 | 2 / 5 | 2 / 5 | 2 / 5 | 2 / 5 |
| Drill Dozer | 3 | 3 / 0 | 3 / 0 | 3 / 0 | 3 / 0 | 3 / 0 | 0 / 0 / 3 err |
| Klonoa | 3 | 0 / 3 | 0 / 3 | 0 / 3 | 0 / 3 | 0 / 3 | 0 / 3 |
| Bomberman Max 2 | 1 | 1 / 0 | 1 / 0 | 1 / 0 | 1 / 0 | 1 / 0 | 1 / 0 |
| **All** | 375 | 310 / 56 / 9 not run | 310 / 56 / 9 not run | 310 / 56 / 9 not run | 310 / 56 / 9 not run | 310 / 56 / 9 not run | 307 / 56 / 3 err / 9 not run |

**The cores agree.** For all 366 convertible saves, each core in its own layout (gpSP's and
SkyEmu's 128 KiB, VBA Next's 0x22000 with EEPROM at 0x20000, SkyEmu's reversed EEPROM, Beetle's
`.eep`/`.sav` beside the ROM) gave the same result as mGBA with the bare chip. No core rejected a
save that another loaded. Frames were compared pixel by pixel with mGBA's. Where they differed, they
were read side by side, and the differences are all cosmetic:
- **SkyEmu does not run Drill Dozer** (3 core-errors): white screen from power-on to the end of
  the script, with or without a save. The baseline is white too.
- **Boktai in gpSP and VBA Next**: when the game finds no save, it redoes the solar sensor
  calibration and stops at "FAILED SETTING". These cores emulate no sensor. Both still load the
  valid saves (the played entries already showed gpSP and VBA Next store 0 for the sensor).
- Beetle GBA draws a stray lilac bar over FireRed's "The save file has been deleted..." box.
- In Minish Cap, VBA-M, gpSP, Beetle GBA and SkyEmu are a few frames apart from mGBA and VBA Next,
  so one press lands in the file list. The proof shows file 1 highlighted, or the name entry of an
  empty file.
- Animated backgrounds (Fire Emblem, Minish Cap, Pokemon overworlds) differ frame to frame.

**What loads.** Of the 310 saves that load:
- 90 are 64 KiB GameShark dumps of a 128 KiB Pokemon flash. The game says the save is corrupt and
  loads the older of its two copies. The dump holds all of the first copy (sectors 0-13) and two
  sectors of the second.
- 33 of the 35 SMA4 saves load, the 64 KiB dumps of its 128 KiB flash included: after the long
  read the game shows their files.
- The Fire Emblem saves with only extras (support conversations, sound room, bonus disc) show New
  Game and Extras. That counts as loading: with no save, only New Game shows.

### Why 56 saves are rejected, in every core

- **22 Pokemon 64 KiB dumps are not a straight copy of the first flash bank.** Their first 48 KiB
  are flash sectors 16-27 (sectors 2-13 of the newest copy, which lives in the second bank). Their
  last 16 KiB are sectors 12-15. After the import neither copy is whole, and the game says the
  save has been deleted. Put back at 0x10000, the newest copy is complete. All 22 were checked in
  mGBA: the corrupt-save message, then CONTINUE with the newest name and time. The pattern
  (12 sectors of counter N, 2 of N-1, 2 of N) is easy to detect, but the converter does not repair
  it: it follows mGBA. A tool that imports GameShark Pokemon saves could. A GameShark evidently read
  the first 48 KiB with the flash still switched to the bank the game last wrote.
- **14 EEPROM SharkPorts hold the payload in emulator byte order**: Klonoa 2, ALttP (Europe) 2,
  Minish Cap 4, Mario & Luigi 2, Boktai 4. That is the order mGBA, VBA-M and raw `.sav` files use,
  where "AGBZELDA" reads "ADLEZBGA". The real GameShark files (and every `.gsv`) are in the
  other order, which mGBA's import reverses. So these 14 come out scrambled and the game finds no
  file. All 14 were checked in mGBA with the payload taken as is, and all load. They are
  hand-wrapped emulator saves (savefileconverter.com wrote two of them).
- 7 Pokemon saves were made once, into the second copy (counter 1, sectors 14-27), and the 64 KiB
  dump has only two of its fourteen sectors.
- 3 GameShark SP Pokemon files (Ruby, FireRed x2) hold `62 13 00 00` repeated: the Sanyo flash
  chip's ID, read while the chip was in ID mode. They are marked type 2 (SRAM), so only 32 KiB were
  read.
- Blank payloads: 3 Pokemon (all 0xFF or all 0x00), Klonoa 3076 (all zero), and Circle of the Moon
  34902 (only the "DRACULA AGB" signature).
- Bit errors from a poor cartridge contact. They show in the header ("\xd3ARIO&LUIGIP", "P#K\x03M{")
  of Mario & Luigi 3225 (Europe) and Emerald 7496 (Japan); the same damage is in their payloads.
  SMA4 22867 (`.gsv`) starts "SEA\x14EWE\x10" where the game writes "SMA4MWE0". The 64 KiB SMA4
  7305 lacks the game's mark altogether. Sapphire 3759's header is damaged too (it is also one of the 22 above). Three
  more files have damaged header bytes but sound payloads, and load: Sapphire 3758, FireRed 4077
  (Japan), Wario Land 4 25110.
- Boktai 13291 fails in both byte orders.

### Not run (9)

- 7 Mario & Luigi `.sps` files (one uploader, 2018) are hand-assembled and malformed. A date string
  follows a length of 0, and the payload size field says 0x2001C, though 8192 bytes follow with no
  checksum. mGBA's reader cannot find the payload, and neither can this converter, which guesses
  no offsets. Their cart headers say "MARIOLUIGI" without the "&", which mGBA would refuse anyway.
  Two of them are also byte-swapped in 16- or 32-bit units.
- 2 VisualBoyAdvance save states. The battery memory is inside, but getting it out means
  reimplementing VBA-M's whole `CPUReadState`, and no libretro core loads VBA desktop states.

### Mislabelled and odd files

- `GameFAQs 18679`, on the Circle of the Moon page, is a Harmony of Dissonance save (header
  CASTLEVANIA1 / ACHE). It is filed and loads as one.
- `GameFAQs 30881`, in FireRed/LeafGreen's GameShark SP section, is a Game Boy Pokemon
  Red/Blue/Yellow save: player RED, 151 caught, Gen 1 checksum valid. It is 32 KiB plus a 44-byte
  real-time-clock footer of the kind VBA-M and BGB append to MBC3 saves. It is not filed under
  gba; it was left for the Game Boy pass.
- All four `.gsb` files of the GameShark USB Connector section are bare images (64 KiB for a
  32 KiB SRAM and for Emerald; 128 KiB for FireRed and SMA4). The fifth is a VBA save state.
- 15 files in the container sections have no container: 6 `.sps`, 3 `.xps`, 2 `.gsv` and the 4
  `.gsb`.
