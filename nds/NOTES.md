# Nintendo DS

Ten games, six runnable libretro cores. The games cover every DS save chip the cores agree on:
EEPROM 512 B, 8 KiB, 64 KiB and 128 KiB; flash 256 KiB, 512 KiB (plain and with infrared) and
1 MiB. 59 of 60 (game, core) pairs are filed. The missing pair is SkyEmu on HeartGold, which
hangs on a black screen. An eleventh game with a NAND save (Jam with the Band) was played in
every core, but no core wrote a save the game could read back, so none of it is filed.

The cores differ on:
- who writes the file: the core itself (`.dsv`, `.sav`) or the frontend (`.srm`);
- the size: the exact chip size, 8 MiB for every game, or the chip plus a 122-byte footer;
- the fill byte: 0xFF or 0x00;
- how the chip type is found: a game-code database or autodetection;
- what the game sees as the owner's name.

All of it is written up below.

## The ten games

The save type comes from melonDS's game-code database (`src/ROMList.cpp`; type 1 = 512 B, 2 = 8 KiB,
3 = 64 KiB, 4 = 128 KiB, 5 = 256 KiB, 6 = 512 KiB, 7 = 1 MiB, 8-10 = NAND). Every core that
writes an exact-size file agrees with it, except DeSmuME on PMD (see below). That database has no
32 KiB FRAM type (NooDS and DeSmuME do have one), so no game here could be found with FRAM, and
FRAM is not covered.

| Game (No-Intro) | Save chip | Why | Script ends with (proof) |
| --- | --- | --- | --- |
| Bomberman (USA) | EEPROM 512 B (4 Kbit) | the one 512 B game with a quick save. Contra 4, LEGO and Puzzle Quest are also 512 B | File Select: File A "AREA 01-01" after a Quick Save |
| Tetris DS (USA, Australia) | EEPROM 8 KiB | very popular, button-driven; Marathon until game over writes the high score | new game, HIGH SCORE 234-256 |
| Mario Party DS (USA) | EEPROM 8 KiB | popular; the game formats the chip on first boot and then creates save file 1, named from the firmware user name | Select Data: file 1 "Player"/"DeSmuME"/"NooDS"/"Sky", MP Points 0 |
| Clubhouse Games (USA) (En,Fr,De,Es,It) | EEPROM 8 KiB | popular; first boot: pick an icon, "Saving data" | Main Menu with the chosen icon |
| Etrian Odyssey (USA) | EEPROM 64 KiB | 64 KiB with a real save menu: found guild "aaa", recruit, save at the inn | "Save successful." |
| Pokemon Mystery Dungeon - Explorers of Sky (USA) | **EEPROM 128 KiB (1 Mbit)** | the only 128 KiB game in the library; DeSmuME gets the type wrong | "Your adventure has been saved." (quicksave in Beach Cave B1F) |
| Mario Kart DS (USA, Australia) (En,Fr,De,Es,It) | flash 256 KiB | popular; confirming the nickname writes the profile | SELECT MODE (no first-run questions any more) |
| Pokemon - Pearl Version (USA) (Rev 5) | flash 512 KiB | Pokémon gen 4, plain flash | "AAA saved the game." (3 to 7 A's depending on timing) |
| Pokemon - HeartGold Version (USA) | flash 512 KiB **+ infrared** | the IR cartridge (melonDS models it as a separate cart class) | "AAAAAAA saved the game." |
| Picross 3D (USA) (En,Fr,Es) | flash 1 MiB (8 Mbit) | 1 MiB flash; the game formats all of it on first boot | title: slot 1 holds the new pink file |

Not filed, played anyway:

| Jam with the Band (Europe) (En,Fr,De,Es,It) | NAND 8 MiB | the only NAND game with a No-Intro-matching dump here (WarioWare D.I.Y. is the other NAND game) | see below |
| --- | --- | --- | --- |

Tried and dropped:
- New Super Mario Bros.: choosing a file and reaching the world map writes nothing; the first
  save needs levels played.
- Animal Crossing: Wild World: a long, touch-driven intro.
- Phoenix Wright 1 and 2: no save option found in the opening minutes of case 1.
- Castlevania: Portrait of Ruin: the save rooms need platforming past enemies.
- Advance Wars: Dual Strike: text timing in the tutorial mission.
- Style Savvy (1 MiB): a touch-driven start that wrote nothing in the first tries.
- Kirby Super Star Ultra (64 KiB): it saves on entering Spring Breeze, but nothing on screen
  shows the save.

### ROMs

The NDS library uses short names (`Picross 3D.nds`). Each ROM was
matched by CRC against No-Intro (libretro-database `metadat/no-intro/Nintendo - Nintendo DS.dat`,
version 2026.10.07, kept in `.cache/downloads/nds/libretro-dat/`). It was then symlinked under its
No-Intro name in `.cache/roms/nds/`, so cores name their saves the way they would for a No-Intro
set. Symlinks rather than copies because the disk was full.

Seven ROMs match No-Intro byte for byte. Three do not: Picross 3D, Pokemon HeartGold and
PMD Explorers of Sky.
- Their size is right and the secure area is decrypted.
- Everything after the header's "used ROM size" (0x80) is 0xFF. The matching dumps (e.g.
  NSMB) carry data right after that point, presumably the download-play RSA signature.
- So these look like signature-stripped dumps of the same release. Their `rom.sha1` in the
  provenance is the file's own and will not match the DAT.
- HeartGold (USA) and (Europe) share the game code IPKE, so the region in that name is a guess.

## Games x cores

| Game | desmume | desmume-2015 | melonds | melonds-ds | noods | skyemu |
| --- | --- | --- | --- | --- | --- | --- |
| Bomberman | filed | filed | filed | filed | filed | filed |
| Tetris DS | filed | filed | filed | filed | filed | filed |
| Mario Party DS | filed | filed | filed | filed | filed | filed |
| Clubhouse Games | filed | filed | filed | filed | filed | filed |
| Etrian Odyssey | filed | filed | filed | filed | filed | filed |
| PMD Explorers of Sky | filed (as 256 KiB flash, see below) | filed (same) | filed | filed | filed | filed |
| Mario Kart DS | filed | filed | filed | filed | filed | filed |
| Pokemon Pearl | filed | filed | filed | filed | filed | filed |
| Pokemon HeartGold | filed | filed | filed | filed | filed | **failed**: going downstairs in the first house leaves a black screen and the game stops. The 8 MiB `.srm` is all 0x00. Entry removed |
| Picross 3D | filed | filed | filed | filed | filed | filed |
| *Jam with the Band* | game says "Saving..." and the file is 8 MiB, but the next boot starts the newcomer intro again | same | same | "Save error. Failed to save data." | "Save error"; no file written at all | "Save error", then "Load error" |

All six cores are runnable here; there are no non-runnable cores for this system, so nothing was
downloaded. Core builds (from provenance): DeSmuME git 95b4d79, DeSmuME 2015 git a06da0c (x86_64,
under Rosetta via `retro-run-x86_64`), melonDS 0.9.3 66b5d26, melonDS DS 1.4.0, NooDS 9a26653,
SkyEmu adacd078. No BIOS or firmware was used. Every core boots the cartridge directly with
built-in firmware defaults.

Every proof.png was checked by eye. Some saves were also booted again from the filed file:
- melonDS DS PMD: "Continue / Resume your adventure".
- DeSmuME PMD, its misdetected 256 KiB `.dsv`: same result.
- SkyEmu Pearl, the 8 MiB `.srm`: CONTINUE, player AAA.

### Jam with the Band (NAND)

- **melonDS 0.9.3 and DeSmuME (both builds):** the game shows "Saving... Please do not turn off
  the power." with all four bat icons, and the core writes an 8 MiB file. Booting either core
  again on its own file starts the "Hey, a newcomer" registration again, so the game finds no
  save. These files were filed at first, then removed as not genuine.
- **melonDS DS 1.4.0 and SkyEmu:** the game reports "Save error".
- **NooDS:** reports "Save error" and writes no file.

What the cores wrote:
- **melonDS:** a `.sav` of exactly 8 MiB, 0xFF fill, with data in five 64 KiB blocks (0x10000,
  0x20000, 0x40000, 0x90000, 0x7F0000).
- **DeSmuME:** "Slot1 auto-selected device type: Retail NAND" in its log, but the `.dsv` footer
  says type 10 (its "FLASH 64 Mbit"), address size 0, 8 MiB. The data is almost all 0x00.

The script is kept as `scripts/nds/Jam with the Band.txt`.

## Scripts, touch, and options

- Frame: every core renders the two screens stacked, 256x384, with no gap by default, so the
  bottom screen starts at y = 192 for `touch`.
- Touch needs an options file for three cores. These are in `scripts/nds/` and were passed on
  every run of those cores:
  - `melonds.opt`: `melonds_touch_mode = Touch`. The default (Mouse) reads relative mouse motion.
  - `melonds-ds.opt`: `melonds_touch_mode = touch`. The value `touch` is labelled "Pointer"; the
    default is Joystick.
  - `desmume.opt`: `desmume_pointer_type = touch`, for both DeSmuME builds.
  - NooDS (Auto) and SkyEmu take the pointer without options.
- Games ignore touches while text is printing or a character is moving. HeartGold's touch
  menu needs about 300 frames of quiet first.
- Text that A both advances and answers is timing-sensitive across cores. The scripts use B to
  drain text where A could start a new conversation (HeartGold).
- **Every script ends with `wait 2400`, for melonDS 0.9.3.** That core writes its `.sav` from
  `retro_run`, only once more than 2 s of wall-clock time (`time()`) have passed since the game's
  last write (`NDSCart_SRAMManager::Flush`). Under `__LIBRETRO__` it does not flush on
  `retro_unload_game`/`NDS::DeInit`.
  - A dry run of Pearl that quit about 600 frames after "saved the game" left **no `.sav` at
    all**.
  - In RetroArch, closing content within a few seconds of saving in this core would lose the
    save.
  - Here melonDS runs about 600 frames/s (6,600 frames in 11.9 s, start-up included), so
    2400 frames is about 4 s: enough, but with little margin. DeSmuME 2015 under Rosetta is
    about as fast (10.5 s for the same run).

## How each core writes the save

| Core | File(s) | Who writes it | Size | Fill | Chip type from |
| --- | --- | --- | --- | --- | --- |
| desmume, desmume-2015 | `<stem>.dsv` | the core, into the save dir (it exposes no `RETRO_MEMORY_SAVE_RAM`); the file exists from boot | chip size **+ 122-byte footer** | 0xFF | **autodetection** from the game's SPI commands; no database |
| melonds (0.9.3) | `<stem>.sav` | the core, into the save dir, 2 s after the last write (above) | exact chip size | 0xFF | the game-code database built into the core |
| melonds-ds (1.4.0) | `<stem>.srm` (+ an **empty directory `melonDS DS/`** in the save dir, not filed) | the frontend (`RETRO_MEMORY_SAVE_RAM` is the chip size, e.g. 8192 for NSMB at boot) | exact chip size | **0x00** | database |
| noods | `<stem>.sav` | the core, into the save dir | exact chip size | 0xFF | a database in the libretro build. The game codes are in the binary; upstream `cartridge.cpp` only guesses 512 B / 64 KiB / 512 KiB from the first command |
| skyemu | `<stem>.srm` + `<stem>.rtc` | the frontend | **8,388,608 bytes for every game** (`save_data[8 MiB]`); data at offset 0 | **0x00**, inside the chip's range too | database (`nds_rom_database`); unknown games default to EEPROM 128 KiB |

Sizes filed, by chip:

| Chip | desmume / -2015 `.dsv` | melonds `.sav` | melonds-ds `.srm` | noods `.sav` | skyemu `.srm` |
| --- | --- | --- | --- | --- | --- |
| EEPROM 512 B | 634 | 512 | 512 | 512 | 8388608 |
| EEPROM 8 KiB | 8314 | 8192 | 8192 | 8192 | 8388608 |
| EEPROM 64 KiB | 65658 | 65536 | 65536 | 65536 | 8388608 |
| EEPROM 128 KiB (PMD) | **262266** (as 256 KiB flash) | 131072 | 131072 | 131072 | 8388608 |
| flash 256 KiB | 262266 | 262144 | 262144 | 262144 | 8388608 |
| flash 512 KiB (+IR) | 524410 | 524288 | 524288 | 524288 | 8388608 (Pearl; HG hangs) |
| flash 1 MiB | 1048698 | 1048576 | 1048576 | 1048576 | 8388608 |

### DeSmuME's footer

A `.dsv` is the raw chip image followed by:
- the 82-byte text `|<--Snip above here to create a raw sav by excluding this DeSmuME savedata footer:`;
- six little-endian u32: size, padSize, type, addr_size, mem_size, version (0);
- the 16-byte cookie `|-DESMUME SAVE-|`.

That is 122 bytes in all. Both builds write identical footers. The values filed:

| Game | size (1st field) | padSize | type | addr_size | mem_size |
| --- | --- | --- | --- | --- | --- |
| Bomberman | 512 | 512 | 1 (EEPROM 4 Kbit) | 1 | 512 |
| Tetris DS | 8192 | 8192 | 2 (EEPROM 64 Kbit) | 2 | 8192 |
| Clubhouse Games | **513** | 8192 | 2 | 2 | 8192 |
| Etrian Odyssey | 53981 | 65536 | 3 (EEPROM 512 Kbit) | 2 | 65536 |
| PMD Explorers of Sky | 65537 | 262144 | **5 (FLASH 2 Mbit)** | 3 | 262144 |
| Mario Kart DS | 200449 | 262144 | 5 | 3 | 262144 |
| Pearl, HeartGold | 262145 | 524288 | 6 (FLASH 4 Mbit) | 3 | 524288 |
| Picross 3D | 1047041 | 1048576 | 7 (FLASH 8 Mbit) | 3 | 1048576 |

The first field is not the chip size. A parser must use padSize/mem_size, or the file length
minus 122. The data before the footer is always padSize bytes.

**DeSmuME gets PMD Explorers of Sky wrong.** The real chip is a 1 Mbit EEPROM with 3-byte
addresses. DeSmuME autodetects it as 2 Mbit flash and writes 256 KiB:
- The upper 128 KiB are all 0xFF.
- The lower 128 KiB match melonDS's file in layout (about 1,100 bytes differ from gameplay).
- The game runs and saves, and DeSmuME reloads it ("Continue").
- Trimmed to 128 KiB, the data is what the other cores hold. Feeding the 256 KiB file to a core
  that expects 128 KiB needs the trim.

### Fill byte: 0x00 in melonDS DS and SkyEmu

- melonDS 0.9.3 fills the chip with 0xFF before the game runs, as erased EEPROM/flash reads.
  The files show it, and current melonDS's `CartRetail` does the same. So do NooDS
  (`resizeSave`) and DeSmuME.
- melonDS DS 1.4.0 and SkyEmu start from zeros. SkyEmu clears `save_data` when no save file
  exists.
- The games do not mind: every one of them formatted or wrote its blocks and saved fine.
- The files, though, differ wherever the game never wrote:
  - Pearl: 400,633 bytes are 0x00 instead of 0xFF, including the whole first 256 KiB, which the
    game has not written yet;
  - Picross 3D: 1,007,872 bytes;
  - MKDS: 240,128 bytes;
  - Etrian: 1,040 bytes;
  - Tetris DS: none, because it writes all 8 KiB.

Bytes that differ from melonDS 0.9.3, after trimming every file to the chip size. The "fill"
count is bytes that are 0xFF in one file and 0x00 in the other.

| Game | desmume | desmume-2015 | melonds-ds | noods | skyemu |
| --- | --- | --- | --- | --- | --- |
| Bomberman | 0 | 18 | 0 | 16 | 16 |
| Tetris DS | 337 | 338 | 338 | 337 | 338 |
| Mario Party DS | 0 | 22 | 6 + 88 fill | 28 | 26 + 88 fill |
| Clubhouse Games | 20 | 40 | 20 + 1004 fill | 38 | 38 + 1004 fill |
| Etrian Odyssey | 0 | 0 | 0 + 1040 fill | 0 | 0 + 1040 fill |
| PMD Explorers of Sky | 1035 | 1465 | 1284 + 14940 fill | 1060 | 1015 + 15004 fill |
| Mario Kart DS | 19998 | 22000 | 21536 + 240128 fill | 22000 | 22000 + 240128 fill |
| Pokemon Pearl | 53 | 52 | 56 + 400633 fill | 53 | 58 + 400633 fill |
| Pokemon HeartGold | 533 | 533 | 536 + 386729 fill | 536 | - |
| Picross 3D | 136 | 130 | 120 + 1007872 fill | 196 | 116 + 1007872 fill |

Etrian Odyssey is byte-identical in all six cores once the fill is accounted for. Most of the small
differences elsewhere follow from the owner's name and the clock (next section) and from
timing (Tetris piece sequences).

### The owner's name and the clock live in the save

DS games copy the firmware user name into their save (Mario Party DS file 1, Bomberman File A,
Mario Kart DS's nickname). Without a firmware dump each core supplies its own:
- **"Player"** in DeSmuME (current), melonDS 0.9.3 and melonDS DS. They take the frontend's
  username (`RETRO_ENVIRONMENT_GET_USERNAME`; retro-run answers "Player"). In RetroArch this
  would be the user's own name.
- **"DeSmuME"** in DeSmuME 2015.
- **"NooDS"** in NooDS.
- **"Sky"** in SkyEmu.

The same game's save therefore differs between cores around the UTF-16 name:
16-28 bytes in Bomberman and Mario Party DS.

The clock is the console's, not the cartridge's: no DS cartridge here has an RTC. Every core
reads the host clock; Clubhouse Games shows it on screen.

**SkyEmu writes a `.rtc` anyway, 40 bytes, for every game.** It is a raw `nds_rtc_t` (src/nds.h
at adacd078), little-endian:

| Offset | Field | Value in these files |
| --- | --- | --- |
| 0x00 | `u32 serial_state` | |
| 0x04 | `u32 serial_bits_clocked` | |
| 0x08 | `u64 input_register` | |
| 0x10 | `u64 output_register` | |
| 0x18 | `u32 state` | 0xFFFFFFFF |
| 0x1C | `u8 status_register` | 0x40 (24-hour mode) |
| 0x1D | pad | |
| 0x1E | `u16 year` | BCD; 0x0026 is 2026 |
| 0x20 | `u8 month` | BCD; 0x11 |
| 0x21 | `u8 day` | BCD; 0x04 |
| 0x22 | `u8 day_of_week` | 0x03 |
| 0x23 | `u8 hour` | BCD |
| 0x24 | `u8 minute` | BCD |
| 0x25 | `u8 second` | BCD |
| 0x26 | pad | |

Bomberman's `.rtc` holds 00:23:42, the local time of that run. It is a snapshot of the last time
the game read the clock, not a clock offset. one-saves should treat it as a SkyEmu sidecar with
no counterpart in other cores. For clocks.json: none of the DS cores keeps a cartridge clock;
SkyEmu's `.rtc` is a console-RTC register dump.

## Runner and harness

- No harness problems. `touch` works as documented in all six cores, given the options above.
  Core options v2 negotiation works: SkyEmu ran NDS with no options file.
- The blank check in `make-save.py` counts files, so a run whose save is blank still counts as
  ok if a sidecar is not. SkyEmu on HeartGold was "ok" because its `.rtc` is not blank, even
  though its `.srm` was all 0x00. That entry was removed by hand.
- melonDS 0.9.3's delayed flush (above) means a script must leave wall-clock time after the last
  save. A faster machine needs more frames. A `wait`-by-seconds command, or a final flush on
  unload, would make this robust.
- The disk was full when this work started. ROMs are symlinks, and dry-run directories were
  deleted as they finished.

## GameFAQs saves

All 79 saves on GameFAQs' save pages for this corpus's DS games, fetched 2026-11-05 from the
three "Action Replay Max DS" sections (`.duc`, `.dst`, `(1.00-1.03)`). Each is filed as it was
served under `nds/<writer>/<release> [GameFAQs <id>]/` with `provenance.json` and, when it was
run, `proof.png` (one frame per core, in the order of `verified.proof_order`). Products: Pokemon
Diamond / Pearl / Platinum (25), HeartGold / SoulSilver (21), Mario Kart DS (12), Pokemon Mystery
Dungeon: Explorers (10), Bomberman (3), Mario Party DS (3), Clubhouse Games (2), Tetris DS (2),
Picross 3D (1).

### What the files are

Read from the bytes, not from the section (see "Mislabelled" below):

| What it is | Files | Filed under | Converter |
| --- | ---: | --- | --- |
| Action Replay DS, version 1: `ARDS000000000001`, 500-byte header, then the raw save | 53 | `_action-replay-ds` | `nds-ards.py` |
| the same header, then the save **block-RLE compressed** (11581 Tetris DS, 12118 Mario Kart DS) | 2 | `_action-replay-ds` | `nds-ards.py` |
| the same header around a DeSmuME `.dsv` (33877) or a no$gba file (19144), padded with 0xFF | 2 | `_action-replay-ds` | `nds-ards.py`, then `nds-dsv.py` / `nds-nocash.py` |
| Action Replay DS, version 2: 0xA4-byte header (17815) | 1 | `_action-replay-ds` | `nds-ards.py` |
| DeSmuME `.dsv` (raw + 122-byte footer) | 4 | `desmume` | `nds-dsv.py` |
| DeSmuME save state (`DeSmuME SState`, zlib) | 4 | `desmume` | `nds-desmume-state.py` |
| no$gba backup file (`NocashGbaBackupMediaSavDataFile`, method 1) | 1 | `_nogba` | `nds-nocash.py` |
| DraStic save state (`DraStic-SaveState`, zlib) | 2 | `_drastic` | `nds-drastic-state.py` |
| `DSXS` container: 256-byte header, then a gzip member (20563) | 1 | `_dsxs` | `nds-dsxs.py` |
| raw chip image, no header (512 KiB, one 1 MiB) | 9 | `_raw` | none |

- **Headers.** Of the 57 version-1 Action Replay files, only 9 carry what a user typed on the
  device (game, save name, description). 39 have a converter's header (`Converted Savegame` /
  `Savegame`, ASCII `shuny conv`), 7 another converter's (`Converted Saves` / `Conversion code by
  UniqueGeeks.Net`), 2 the DualScene.net archive's. None holds a game code: the release was
  worked out from the save itself (below).
- **The `shuny conv` converter writes 262,144 bytes whatever the chip.** For the 512 B, 8 KiB
  and 128 KiB chips the rest is 0xFF and is cut. For Pokemon's 512 KiB flash it keeps only the
  first half, one of the game's two save copies (padded back with 0xFF): 11 of the 12 such
  Pokemon saves that could be run load from that copy (20884 is rejected, below). For Picross 3D
  (1 MiB) it keeps a quarter.
- **The DeSmuME `.dsv` files** all have footer type 0 (Autodetect) and size = padSize; 21611
  (2011) also has mem_size 0. DeSmuME itself writes the real type (6 for 512 KiB) and the highest
  address written as the first field, so these were probably made by an older DeSmuME or a tool.
- **The DeSmuME states** hold the save in the MMU chunk (61) as DeSmuME's backup device stores it,
  and three of them the ROM header (chunk 130): IPKE (HeartGold, 0.9.10 and 0.9.11) and ADAD
  (German Diamond, Rev 5, 0.9.13). The fourth (22072, an older state format) records no ROM and
  holds 188,672 bytes of a 256 KiB flash, which DeSmuME pads with 0xFF on load, as the converter does.
- **The DraStic states** are closed-format. Inflated, both have at 0x30000 a record that is plainly
  the cartridge's save memory: u32 2, u32 mask 0x1FFFF, u32 0, u8 3, then 128 KiB, which is an
  Explorers of Sky save (its header and backup copy where they belong). The game code at 0x34
  (C2SE, C2SP) gives the release. Both convert; the USA one loads in every core.
- **DSXS**: the uploader calls it "GDS GameSharkCheatSaves Format". No documentation was found;
  the layout is in `nds-dsxs.py`. The gzip member's own CRC-32 checks the save.
- **The compressed Action Replay payload** (in the two oldest `.dst` uploads, 2006): u32 LE total,
  u32 LE block count, then per 8 KiB block u32 BE output size, u32 BE input size, an escape byte
  and RLE data (ESC 00 = the escape byte, ESC n v = n+1 copies of v). Both decode exactly to the
  chip size and load. DeSmuME's `import_duc` does not know this and would import the compressed
  bytes as the save.

### Converting to each core's file

`tools/gamefaqs/nds-*.py`, standard library only. The container converters write the raw save
they find; `nds-cores.py` fits it to the game's chip (melonDS's game-code database) and writes
each core's file, as described in "How each core writes the save":

- shorter than the chip: padded with 0xFF; longer: cut, but only when the rest is 0xFF, 0x00 or
  copies of the chip, unless `--drop-tail` (used once, 35489: its upper 128 KiB hold a second,
  different Explorers of Sky save that the 1 Mbit chip cannot address);
- melonDS, NooDS: `<stem>.sav` in the save directory; melonDS DS: `<stem>.srm` through SAVE_RAM;
  SkyEmu: the chip then 0x00 to 8 MiB, through SAVE_RAM;
- DeSmuME and DeSmuME 2015: the `.dsv` DeSmuME's own import would write (`import_duc` /
  `import_raw`, `ensure()`): the data padded with 0xFF to DeSmuME's next size, then the footer.
  A 128 KiB Explorers of Sky save becomes 256 KiB, type 5 (FLASH 2Mbit), addr_size 3, which is
  what DeSmuME writes for that game itself.

Each provenance records the chain (`converted_with`), the chip image's hash (`converted`) and
every core file's name, size and hash (`core_files`).

What DeSmuME's own *Import Backup Memory* would make of these files, from `mc.cpp`:
- it imports an Action Replay payload at whatever size it has, with addr_size from that size. A
  256 KiB `Converted Savegame` of an 8 KiB EEPROM game becomes "FLASH 2Mbit" with 3-byte
  addresses: Mario Party DS (27509 imported
  that way, `--chip 262144`) stops on "Unable to write data. Please turn off the power and
  reinsert the Game Card." in both DeSmuME builds. Cut to the 8 KiB chip, it loads in all six.
- it does not unwrap an Action Replay file holding a `.dsv`, a no$gba file or the RLE payload.
- a `.dss` is treated as an Action Replay file; none of the seven `.dss` here is one.

### Verifying

One load script per game, `scripts/nds/<game>.load.txt`, goes to the screen that shows a save's
content and shoots it: Pokemon's CONTINUE panel, Explorers' Adventure Record, Mario Kart DS's
SELECT CUP, Mario Party DS's Select Data, Bomberman's File Select, Tetris DS's Marathon HIGH
SCORE, Dawn of Sorrow's file list. Each ran once per core with no save (the baseline, under
`work/`) and once per save, with the same options files and no BIOS or firmware, as the played
entries.

Results (L loads, R rejected, E core-error, N not-run):

| Game | saves | desmume | desmume-2015 | melonds | melonds-ds | noods | skyemu |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| Bomberman | 3 | 2 L, 1 N | 2 L, 1 N | 2 L, 1 N | 2 L, 1 N | 2 L, 1 N | 2 L, 1 N |
| Clubhouse Games (Europe, Japan) | 2 | 2 N | 2 N | 2 N | 2 N | 2 N | 2 N |
| Mario Kart DS | 12 | 6 L, 6 N | 6 L, 6 N | 6 L, 6 N | 6 L, 6 N | 6 L, 6 N | 6 L, 6 N |
| Mario Party DS | 3 | 1 L, 2 N | 1 L, 2 N | 1 L, 2 N | 1 L, 2 N | 1 L, 2 N | 1 L, 2 N |
| Picross 3D (Japan) | 1 | 1 N | 1 N | 1 N | 1 N | 1 N | 1 N |
| Pokemon Diamond / Pearl | 13 | 8 L, 3 R, 2 N | 8 L, 3 R, 2 N | **8 E**, 3 R, 2 N | 8 L, 3 R, 2 N | 8 L, 3 R, 2 N | 8 L, 3 R, 2 N |
| Pokemon Platinum | 9 | 5 L, 4 N | 5 L, 4 N | **5 E**, 4 N | 5 L, 4 N | 5 L, 4 N | 5 L, 4 N |
| Pokemon HeartGold / SoulSilver | 21 | 14 L, 7 N | 14 L, 7 N | **14 E**, 7 N | 14 L, 7 N | 14 L, 7 N | 14 L, 7 N |
| Castlevania - Dawn of Sorrow (on the Pokemon page) | 3 | 3 L | 3 L | **3 R** | 3 L | **3 R** | **3 R** |
| Mystery Dungeon - Explorers of Time / Darkness | 4 | 3 L, 1 N | 3 L, 1 N | 3 L, 1 N | 3 L, 1 N | 3 L, 1 N | 3 L, 1 N |
| Mystery Dungeon - Explorers of Sky | 6 | 5 L, 1 N | 5 L, 1 N | 5 L, 1 N | 5 L, 1 N | 5 L, 1 N | 5 L, 1 N |
| Tetris DS | 2 | 2 L | 2 L | 2 L | 2 L | 2 L | 2 L |
| **All** | 79 | 49 L, 3 R, 27 N | 49 L, 3 R, 27 N | 19 L, 6 R, 27 E, 27 N | 49 L, 3 R, 27 N | 46 L, 6 R, 27 N | 46 L, 6 R, 27 N |

- The 27 not-run are saves for releases the library has no image of (below).
- The 3 saves every core rejects are broken files, not core problems: 20884 ("The save file has
  been erased due to corruption or damage."), 15053 and 19576 (no valid save at all; the game
  starts a new one).
- Where the European English and the USA release share a game code (Pokemon ADAE, APAE, CPUE,
  IPKE, IPGE), a save was run in whichever of the two the library has, and provenance says so.
  The library's Diamond is the European release; its Platinum, HeartGold and SoulSilver match no
  No-Intro hash, so their region is unknown.
- Version cross-checks, in desmume: the Time/Darkness saves (17564, 22072, 25597) show the same
  Adventure Record in Explorers of Darkness as in Time, and a SoulSilver save (31668) loads in
  HeartGold. So the version cannot be told by loading; it was taken from the description or, for
  Pokemon, from the game that caught the player's own Pokemon (provenance `note`).

### What differs between cores

- **melonDS 0.9.3 cannot continue any Pokemon Diamond, Pearl, Platinum, HeartGold or SoulSilver
  save here (27 core-errors).** Where the other five show the CONTINUE panel it shows "A
  communication error has occurred" (Diamond/Pearl/Platinum: "...returned to wherever you last
  saved", then a white screen; HeartGold/SoulSilver: "...returned to the title screen"). It
  does the same with melonDS's own Pearl save from this corpus. It does not with a broken or
  missing save (those reach the corruption message or the introduction), so the game finds the
  save and then fails a wireless check. melonDS 0.9.3 runs on FreeBIOS and its own firmware
  here; melonDS DS 1.4.0, under the same conditions, is fine.
- **Castlevania - Dawn of Sorrow: melonDS 0.9.3, NooDS and SkyEmu reject a save that DeSmuME
  (both builds) and melonDS DS load.** At boot the game says "Save data is corrupted. Data has
  been deleted." The bytes are the same: melonDS DS's `.srm` is byte-identical to melonDS's and
  NooDS's `.sav`, and all three databases give the game (ACVE) an 8 KiB EEPROM. The game deletes
  the data at that point, so a user of those cores would lose this save. Nothing else here
  explains the difference; Dawn of Sorrow was not among the played games, so no core's own save
  of it was tried.
- Everything else behaves the same in all six cores: SkyEmu's 8 MiB `.srm`, melonDS DS's
  SAVE_RAM, DeSmuME's 256 KiB `.dsv` of a 128 KiB EEPROM (Explorers of Sky), the 256 KiB
  half-saves of 512 KiB Pokemon flash, the DraStic and DeSmuME state extractions and the RLE
  payloads all show the save's content.
- Save messages are the game's, and the same in every core: Platinum 19144 reports "The most
  recent Battle Video is corrupted." before its CONTINUE panel; Explorers of Sky saves with the
  Special Episodes unlocked answer Continue with "Main Story / Special Episodes". The load scripts
  take a second (and for Platinum a third) shot for these, and provenance names the frame used.

### Mislabelled sections and products

- **Format sections.** `(1.00-1.03)` holds no Action Replay file at all: 2 DraStic states, a
  no$gba file, a DeSmuME `.dsv` and 3 raw saves. `(.dst)` holds 3 Action Replay files, 4 DeSmuME
  save states, a `.dsv` and a raw save. `(.duc)` holds 55 Action Replay files (one version 2, two
  wrapping a `.dsv` or a no$gba file), 2 `.dsv`, 5 raw saves and the DSXS file. DeSmuME treats
  `.duc` and `.dss` alike as Action Replay files, so a `.dss` from this site would fail its import.
- **Product.** 13729, 15744 (North America) and 14593 (Japan) on the Pokemon Diamond / Pearl /
  Platinum page, described as Pokemon saves, are one Castlevania - Dawn of Sorrow save
  (the Action Replay header's ASCII copy says "castlevania"). Filed as Dawn of Sorrow (USA).
- **Region.** 19096 and 18826 (North America) are Japanese Platinum saves (language 1, the
  player's own Pokemon from Japanese Platinum). 18295 (Europe, "fr save game") is English.
  31688 (Europe) and 31689 (Japan) are the same file; so are 19741 and 19742, and 25417 and
  28633. 27509 (North America) carries the same player name as 16307 (Europe, same description)
  but the USA game code.

### Releases the library lacks

Not run, no image in the library: Bomberman (Europe); 42 All-Time Classics (Europe) and Daredemo
Asobi Taizen (Japan) (Clubhouse Games); Mario Kart DS (Europe) x5 and (Japan); Mario Party DS
(Europe) and (Japan); Rittai Picross (Japan) (Picross 3D, and only a quarter of its 1 MiB is in
the file); Pokemon Diamant-Edition (Germany), Edicion Diamante (Spain); Pocket Monsters Platinum
(Japan) x4; Pocket Monsters HeartGold (Japan) x2 and SoulSilver (Japan) x3; Edicion Oro HeartGold
(Spain); Version Argent SoulSilver (France); Mystery Dungeon Explorers of Time (Europe) and of Sky
(Europe). All 27 converted without error.

`one-saves` has no reader for any of these DS formats, so `1saves` was not run on them.
