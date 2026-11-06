# Nintendo 64

I picked ten games that cover every N64 save type the libretro cores support: 4 Kbit EEPROM, 16 Kbit
EEPROM, 256 Kbit SRAM, 1 Mbit FlashRAM, and a Controller Pak note from a game with no cartridge save.
I ran them in the two runnable cores, and all 20 (game, core) pairs were filed. Online I found 7 more
saves: 2 written by standalone mupen64plus and 5 written by the MiSTer core.

Both libretro cores write one 296960-byte `.srm` holding a whole console's storage. In every game,
the cartridge regions of the two cores' files are byte-identical, with one exception: Majora's Mask
has 19 random digits that differ. The cores always disagree on the Controller Paks, because each
gives its paks a different ID block.

SRAM and FlashRAM are stored with each 32-bit word's bytes reversed, in both libretro cores and in
the MiSTer files. EEPROM and Controller Paks are stored in console order everywhere.

## The ten games

| Game (No-Intro) | Save hardware | Why | Script ends with (proof) |
| --- | --- | --- | --- |
| Super Mario 64 (USA) | EEPROM 4 Kbit | the 4 Kbit reference; analog cursor | after a reset, SELECT FILE shows the sound button reading MONO |
| Banjo-Kazooie (USA) (Rev 1) | EEPROM 4 Kbit | a second 4 Kbit game, with a real game file rather than a setting | after power-on again, Banjo's bed: "GAME 1: TIME 0:00:28, 0 JIGSAWS, 0 NOTES" |
| Yoshi's Story (USA) (En,Ja) | EEPROM 16 Kbit | 16 Kbit; the game formats all 2 KiB | after a reset, Options shows "Audio (MONO)" |
| Perfect Dark (USA) (Rev 1) | EEPROM 16 Kbit **and** a Controller Pak note | popular, and it writes both a chip and the pak in one run | Choose Your Reality, Game Pak: agent "Dark" |
| Legend of Zelda, The - Ocarina of Time (USA) (Rev 2) | SRAM 256 Kbit | the SRAM game people play; naming a file writes it | after a reset, File 1 "AAAA" |
| Super Smash Bros. (USA) | SRAM 256 Kbit | a second SRAM game, written only up to 0xBDB | after a reset, Option: Sound Stereo/**Mono** |
| Legend of Zelda, The - Majora's Mask (USA) | FlashRAM 1 Mbit | popular FlashRAM; naming a file writes it, with no owl statue needed | after a reset, File 1 "AAAA" |
| Paper Mario (USA) | FlashRAM 1 Mbit | FlashRAM, written with a readable magic ("Mario Story 006") that shows the byte order | after a reset, File 1 "A", First Play |
| Pokemon Stadium (USA) (Rev 2) | FlashRAM 1 Mbit | FlashRAM written almost to the end (0x1F85F) | after a reset, OPTIONS: SOUND MONO |
| Tony Hawk's Pro Skater (USA) (Rev 1) | **Controller Pak only** (no cartridge save) | a pak-only game with a quick menu save | "SAVE SUCCESSFUL." with note TH-AA on the pak |

Considered and dropped:
- **Mario Kart 64.** Its ghost save to the pak needs three clean scripted laps. I timeboxed the
  driving and gave up.
- **Diddy Kong Racing.** Entering initials writes nothing; it saves only after a race.
- **Turok.** It needs a save point in the level.
- **Dezaemon 3D (Japan).** This is the only 768 Kbit SRAM game, and it does not fit: see "Dezaemon 3D"
  below.
- **Banjo-Tooie, F-Zero X.** Not needed once the other games covered their save types.

### Scripts and options

The scripts are in `scripts/n64/`. Each one plays from power-on to a genuine save. Where a reset can
show the save being read back, the script resets and goes back to the screen that shows it.
Banjo-Kazooie is the exception: it saves on "SAVE AND QUIT", and the game then restarts by itself.

Three menus follow the analog stick and need `stick`, not the D-pad: Super Mario 64's hand cursor,
Yoshi's Story's menus, and Banjo-Kazooie's pause menu. The N64 A button is the RetroPad `b`.

| Options file | Contents | Why |
| --- | --- | --- |
| `mupen64plus-next.opt` | `mupen64plus-rdp-plugin = angrylion` | GLideN64 renders black frames in retro-run |
| `parallel-n64.opt` | `parallel-n64-gfxplugin = angrylion`, `parallel-n64-pak1 = memory` | ParaLLEl's `pak1` default is `none` (libretro_core_options.h). Without this line Perfect Dark writes no pak note and THPS cannot save. Mupen64Plus-Next's default is already `memory` |

The pak option does not change what is filed for the eight games that never touch the pak: the core
formats all four paks into the `.srm` either way. With and without the option, the formatted pak 1 is
byte-identical.

Core builds: Mupen64Plus-Next "3.0-Vulkan 15bada8" and ParaLLEl N64 "1.0 e8cbdbb", both arm64.
Renderer: angrylion, software. CPU and RSP were left at their defaults.

## Games x cores

All 20 played entries are filed, and I checked every proof.png by eye. Both cores ran every script
unchanged, on the same frame counts: no per-core variants were needed.

| Game | mupen64plus-next | parallel-n64 |
| --- | --- | --- |
| Super Mario 64 | filed | filed |
| Banjo-Kazooie | filed (24664 frames, about 7 minutes of intro) | filed |
| Yoshi's Story | filed | filed |
| Perfect Dark | filed | filed |
| Ocarina of Time | filed | filed |
| Super Smash Bros. | filed | filed |
| Majora's Mask | filed | filed |
| Paper Mario | filed | filed |
| Pokemon Stadium | filed | filed |
| Tony Hawk's Pro Skater | filed | filed |

| Core | Status |
| --- | --- |
| mupen64plus (standalone) | Not runnable here. 2 downloaded: Banjo-Tooie (USA), Mischief Makers (USA) |
| n64-mister (MiSTer) | Not runnable here. 5 downloaded: Ocarina of Time (USA), Majora's Mask (USA), Banjo-Kazooie (USA), Donkey Kong 64 (USA), 007 - The World Is Not Enough (USA) (a `.cpk`). 11 played on the owner's MiSTer: see "n64-mister, played on the owner's MiSTer" below |

## The libretro `.srm`

Both cores write `<ROM stem>.srm` of exactly **296960 bytes (0x48800)**. It is `RETRO_MEMORY_SAVE_RAM`,
the core's `save_memory_data` struct. ParaLLEl's struct also holds a 64DD disk, but it reports the size
without it unless a disk is loaded. Nothing else is written: no `.rtc`, and no files of the core's own
in the save directory. The size and layout do not depend on the game:

| Offset | Length | What | Fresh (never written) |
| --- | --- | --- | --- |
| 0x00000 | 0x800 | EEPROM. A 4 Kbit game uses 0x000-0x1FF; the rest stays 0xFF | 0xFF |
| 0x00800 | 4 x 0x8000 | Controller Paks, ports 1-4, each a full 32 KiB pak image | formatted paks (below) |
| 0x20800 | 0x8000 | SRAM | 0xFF |
| 0x28800 | 0x20000 | FlashRAM | 0xFF |

### What each game wrote

The ranges are the bytes that are no longer 0xFF. They are the same in both cores.

| Game | EEPROM | SRAM | FlashRAM | Pak 1 note |
| --- | --- | --- | --- | --- |
| Super Mario 64 | 0x000-0x1FF | - | - | - |
| Banjo-Kazooie | 0x000-0x1FF | - | - | - |
| Yoshi's Story | 0x000-0x7FF (all 2 KiB, almost all 0x00) | - | - | - |
| Perfect Dark | 0x000-0x7CF | - | - | `NPDE` "4Y" "PERFECT DARK", 28 pages, **written on boot** |
| Ocarina of Time | - | 0x0000-0x79FF | - | - |
| Super Smash Bros. | - | 0x0000-0x0BDB | - | - |
| Majora's Mask | - | - | 0x00000-0x17FFF | - |
| Paper Mario | - | - | 0x0000-0x137F | - |
| Pokemon Stadium | - | - | 0x0000-0x1F85F | - |
| Tony Hawk's Pro Skater | - | - | - | `NTFE` "52" "TH-AA" ext "G", 11 pages |

So a single file can hold a chip and a pak note together (Perfect Dark). It can also hold no
cartridge save at all (THPS). No game touched pak ports 2-4.

### Byte order

- **EEPROM: console order.** Super Mario 64's file and menu signatures read `44 41` ("DA") and
  `48 49` ("HI") as stored.
- **SRAM: each 32-bit word reversed.** Ocarina of Time's "ZELDAZ" magic reads `44 4C 45 5A 00 00 5A 41`
  ("DLEZ", "..ZA"). The first word reads `41 44 4C 45` ("ADLE").
- **FlashRAM: each 32-bit word reversed.** Paper Mario's "Mario Story 006" reads
  `iraMtS o yro.600`. Majora's Mask's "ZELDA3" reads "DLEZ" "..3A".
- **Controller Paks: console order.** The note table reads `NTFE`/`NPDE` as stored, and the index table
  is big-endian (`00 71`, `00 03`...).
- **The two cores agree on all four.**

### Where the two cores differ

1. **The Controller Pak ID blocks.** This is the only difference in 9 of the 10 games. Page 0 holds
   the ID block at 0x20 and its copies at 0x60, 0x80 and 0xC0; the rest of page 0 is zeros. Pages 1
   and 2 hold identical index tables (checksum `0x71`, entries 5-127 = `00 03`). The note table and
   data pages are zeros.
   - **Mupen64Plus-Next: an all-zero serial in all four ports**, so the four paks are identical. The
     ID block is `00`x24, then `00 01` `01` `00` `01 01` `FE F1`: device 0x0001, 1 bank, version 0,
     checksum 0x0101/0xFEF1. The source (`format_saved_memory`) asks a xoshiro256++ generator for a
     random serial. That generator is seeded from `time()` in `main_run`, which appears to run after
     the paks were formatted in `retro_load_game`. The generator's state is still zero, so the
     serial is zero. Every run gave the same bytes.
   - **ParaLLEl N64: a different serial per port, the same on every run.** The serials come from
     `rand()`, and nothing seeds it. Pak 1 begins `00 00 41 A7 10 D6 3A F1`, which is 16807 and 16807²:
     macOS libc's minimal-standard generator. All ten games got the same four ID blocks. On another
     libc the values will differ, but they will still be fixed.
   - The one-saves doc for `read_srm` says "Each core formats all four with a random serial". That
     is not what these builds do on macOS.
2. **Majora's Mask: 38 bytes in FlashRAM**, 19 in each of its two save copies (0x0FEE-0x0FFF and
   0x1008; 0x2FEE-0x2FFF and 0x3008). They are the digits the game rolls when a file is created (the
   Bombers' code and the lottery) and the checksum after them. This is game RNG, not a core difference.
3. **Perfect Dark's pak note** differs in 157 bytes across its data pages, besides the ID block. The
   EEPROM is identical. Tony Hawk's note is byte-identical between the cores.

### Checks against one-saves (`crates/one-saves-convert/src/n64.rs`, read only)

- **Layout:** the table matches exactly, including the total of 296960 bytes.
- **`WordOrder::Swapped` for SRAM/FlashRAM in a `.srm`, EEPROM never swapped:** confirmed in both
  cores.
- **"Every current core formats with ones":** true for the chip regions of both libretro cores. It
  is not true of MiSTer files from before 2026-01 (zeros; see below).
- **`chip_written`:** without a named chip, SM64 and Banjo-Kazooie (data only up to 0x1FF) would be
  refused as "4 Kbit or 16 Kbit". Yoshi's Story and Perfect Dark write past 0x200, so they would be
  inferred as 16 Kbit. THPS has no cartridge region written, so it would come out as a device holding
  only pak 1.
- **`order_of_producer` in the CLI** does not know `n64-mister`, so it would ask for `--n64-order`.
  The MiSTer files below are **swapped**, like mupen64plus's.
- The `1saves` binary in `target/release` (bundle spec 0.4, built 2026-10-19) predates the `.srm`
  device code. Converting these files with it gives a single opaque 296960-byte part. I did not build
  or change one-saves.

### Dezaemon 3D, the 768 Kbit SRAM game (dry run only, not filed)

Booted to its GAME EDIT screen in both cores. Both cores turn the whole SRAM region (0x20800-0x287FF)
into **0x00**, and nothing else changes. The game clears what it can reach, and the `.srm` has room for
only one of its three 32 KiB banks. This agrees with one-saves' note that no libretro core saves this
chip.

## Downloaded entries

- **`mupen64plus/Banjo-Tooie (USA)/Banjo-Tooie (U) [!]-40E98FAA.eep`**
  - Source: [mupen64plus-core #1069](https://github.com/mupen64plus/mupen64plus-core/issues/1069). A
    core contributor (Jj0YzL5nvJ) attached their own game on 2025-12-30 so others could reproduce a
    bug.
  - Contents: 2048 bytes (16 Kbit). GAME 1 TIME 18:05:18, 32 JIGGIES.
  - Attribution rests on the name, which is mupen64plus-core's current form,
    `<GoodName>-<first 8 hex of the ROM MD5>.eep`. The No-Intro ROM's MD5 does start `40e98faa`.
  - Loads unchanged at offset 0 of a Mupen64Plus-Next `.srm`.
- **`mupen64plus/Mischief Makers (USA)/Mischief Makers (U) [!].eep`**
  - Source: [mupen64plus-core #409](https://github.com/mupen64plus/mupen64plus-core/issues/409),
    2017. The reporter ran the m64p build, which is mupen64plus-core.
  - A **4 Kbit game written as 2048 bytes**: 512 bytes of data, then 1536 bytes of 0xFF. This is the
    older mupen64plus behaviour that one-saves' `normalize` trims. n64.rs says "before 2017"; this
    file is from September 2017.
  - Loads in Mupen64Plus-Next: file "aaa", 1 hr 18 min. The revision is a guess: the GoodName has no
    version, so I named it (USA).
- **`n64-mister/*` (5 entries).** All five come from one zip,
  [save-file-converter #297](https://github.com/euan-forrester/save-file-converter/issues/297):
  "Example files: MiSTer N64 saves.zip". The converter's author attached it in April 2024. The same
  five files are that project's MiSTer N64 test data.
  - Attribution: the issue text, and MiSTer's naming (`<ROM stem>.eep/.sra/.fla`, `_1.cpk`) in Main's
    `support/n64/n64.cpp`. The original MiSTer user is not named.
  - The files are dated 2023-12 to 2024-02. That is after Main split the single `.sav` into one file
    per chip and per pak.
  - **Sizes** are the chip's own: BK `.eep` 512, DK64 `.eep` 2048, OoT `.sra` 32768, MM `.fla` 131072,
    TWINE `_1.cpk` 32768.
  - **Byte order** is the same as the libretro `.srm`: SRAM and FlashRAM word-swapped, EEPROM as is.
    OoT, MM and BK copied unchanged into the matching `.srm` regions all load in Mupen64Plus-Next (OoT:
    two files "ABC"; MM: "LINK", "FZS"; BK: 0:09:26). These are the proofs filed.
  - **Fill is 0x00, not 0xFF.** Main of that time created new save files with `memset(0)`. Main
    commit bc49794 (2026-01-13) changed this to 0xFF because some games hang on zeros. MiSTer files
    made before then differ from libretro files in every unused byte.
  - **The `.cpk` is in console order.** Main swaps pak data to and from the core. Its ID block is the
    classic mupen64plus-core template (`FF FF FF FF 05 1A 5F 13 ... 01 FF 66 25 99 CD`), not Main's
    own header of the time, so the pak was brought to the MiSTer from an emulator. It holds TWINE
    notes for both `NO7P` (PAL) and `NO7E` (USA).
  - Main now formats new paks itself, since July 2026: a random 16-byte serial, then the bytes
    "MiSTer", device byte 0x81. Pak files are `<stem>_1.cpk` to `_4.cpk`, numbered from 1 whether or
    not the game has a cartridge file.
  - **Possible clash:** the MiSTer worker may file a played Majora's Mask (USA) under
    `n64/n64-mister/`. make-save.py replaces an existing directory, so a played run there would
    replace the downloaded entry.

## Leads, not filed

- **[mupen64plus-core #935](https://github.com/mupen64plus/mupen64plus-core/issues/935)**, Jet Force
  Gemini (U) [!].fla. It is 131072 bytes, from m64p in 2022, and the zip also holds a save state.
  The reporter moved the save to Project64 and back, so the last writer could be Project64. It is
  kept in `.cache/downloads/n64/m64p-core-935-jfg/`.
- **[N64_MiSTer #86](https://github.com/MiSTer-devel/N64_MiSTer/issues/86)**, "Mischief Makers 100%
  save files (USA & Europe).zip". These were most likely converted from GameFAQs DexDrive saves, not
  written by the core. Not downloaded.
- **Other N64_MiSTer issues** (#4, #7, #29, #36, #85) describe the save files but attach none.
  - #85 is the source of the 0x00-to-0xFF change.
  - #4 describes `_1..4.cpk` files being created for all four ports.
- **Searches that found nothing usable:** RMG issues; mupen64plus-user-issues; mupen64plus-core
  comments (only save states otherwise); and Main_MiSTer issues. GitHub code search hit its rate
  limit.

## Runner notes

- **No harness problems.** retro-run ran both cores with default options plus the two option files.
- **Disk:** once, commands could not start because the disk was full (ENOSPC). I deleted my
  dry-run directories and the work continued. All scratch has since been deleted.

## n64-mister, played on the owner's MiSTer (2026-11-04)

The scripts above, replayed on the owner's MiSTer (N64_20260726.rbf, Main of 2026-10-19) as
described in `MISTER.md`; entries `"method": "played"`, `"frontend": "mister"`. The first session's
black screens had a simple cause: the core needs the N64 PIF ROM as `games/N64/boot.rom`
(N64_MiSTer README), and the device had none. The owner put their own dump there; nothing else was
needed. Autosave is On by default in this core, so no config file was written. Main's Auto Detect
(`games/N64/N64-database.txt`) picks the save type and the controller accessory per game.

| Game | n64-mister | Files (sizes) |
| --- | --- | --- |
| Super Mario 64 | filed (stick moves onto MONO shortened: Main's stick emulation moves the hand further) | `.eep` 512 |
| Banjo-Kazooie | filed | `.eep` 512 |
| Yoshi's Story | filed, but only the game's first-boot format: the MONO step never landed in three runs (the title and its attract story come at a different frame every run) | `.eep` 2048 |
| Perfect Dark | filed, but no pak note (below) | `.eep` 2048, `_1.tpk`, `_2.cpk`-`_4.cpk` 32768 each |
| Ocarina of Time | filed | `.sra` 32768 |
| Super Smash Bros. | filed | `.sra` 32768 |
| Majora's Mask | filed as `Legend of Zelda, The - Majora's Mask (USA) (played)`, since the `(USA)` folder holds the downloaded entry; MiSTer variant (START twice after 1700 frames) | `.fla` 131072 |
| Paper Mario | filed | `.fla` 131072 |
| Pokemon Stadium | filed, with a Transfer Pak holding Pokemon Red (below) | `.fla` 131072, `_1.tpk` 32768, and the Game Boy save and its `_bak` in `saves/GAMEBOY/` |
| Tony Hawk's Pro Skater | filed | `_1.cpk`-`_4.cpk` 32768 each |
| Dezaemon 3D (Japan) | filed: the 768 Kbit SRAM as the game sets it up at first boot (GAME EDIT reached; the SAVE button was not, the tutorial takes the cursor) | `.sra` 98304 |

Several scripts needed MiSTer variants for timing (`scripts/mister/n64/`): the N64 core's ROM
load time varies by several seconds from run to run, so a title that the libretro scripts reach at
a fixed frame can come up to ~10 s later; the variants wait longer before START.

### What Main writes

One file per chip and per pak, in `saves/N64/`, named after the ROM (Main `support/n64/n64.cpp`):

| Save | File | Size | Byte order | Compared with Mupen64Plus-Next's `.srm` region |
| --- | --- | --- | --- | --- |
| EEPROM 4 Kbit | `<rom>.eep` | 512 | console order | SM64 identical; Banjo-Kazooie 10 bytes (play time and checksum) |
| EEPROM 16 Kbit | `<rom>.eep` | 2048 | console order | Perfect Dark identical; Yoshi's Story 4 bytes (the sound setting the script did not change) |
| SRAM 256 Kbit | `<rom>.sra` | 32768 | 32-bit words reversed | Ocarina of Time identical; Smash Bros. 6 bytes (counters) |
| SRAM 768 Kbit | `<rom>.sra` | 98304 | not shown (only 00 and FF were written) | none: no libretro core keeps it |
| FlashRAM 1 Mbit | `<rom>.fla` | 131072 | 32-bit words reversed | Paper Mario: 160 bytes FF here, 00 in both libretro cores (bytes inside written pages the game never filled), 4 bytes of game data; Majora's Mask 34 bytes (the digits rolled at file creation, as between the libretro cores); Pokemon Stadium identical |
| Controller Pak | `<rom>_N.cpk`, N = 1-4 | 32768 each | console order | THPS: the note identical; the four ID blocks (108 bytes) differ |
| Transfer Pak | `<rom>_1.tpk`, or the Game Boy game's own save (below) | 32768 | Game Boy order | the copy is byte-identical to the Game Boy save it was made from |

- **Byte order, verified:** the `.sra` and `.fla` files are in the libretro `.srm` order, each
  32-bit word reversed (one-saves' "swapped"): Ocarina of Time's `.sra` is byte-identical to
  Mupen64Plus-Next's SRAM region, `ADLE` at 0x08. The `.eep` files and the paks are in console
  order. Main itself byte-swaps only the Controller and Transfer Pak data (`needs_byteswap`); chip
  data reaches the file as the core hands it over.
- **Fill:** Main creates each file when the ROM loads, before the game runs: chips filled with FF
  (since Main bc49794, 2026-01; the downloaded entries from 2023-24 have 00), Controller Paks
  formatted by Main, Transfer Pak files FF.
- **Controller Paks:** four files `_1.cpk` to `_4.cpk`, numbered from 1 after the cartridge file;
  the number counts mounted files, so a game with no cartridge save still starts at `_1`. Main
  formats each new pak itself: ID block at 0x20/0x60/0x80/0xC0 with a random 16-byte serial (a
  different one per pak and per run), then `MiSTer`, device 0x81, 1 bank, checksums; index tables
  as in the libretro paks. A sync tool comparing paks across devices will always see the ID blocks
  differ.
- **Database pak choice:** Pad 1 gets the first pak tag of the game's line. Perfect Dark's line is
  `eeprom2k|rpak|cpak|tpak`: pad 1 got a Rumble Pak, so no note was written, while Main still
  mounted a Transfer Pak file `_1.tpk` (the `tpak` tag) and three Controller Pak files.
- **Transfer Pak** (N64_MiSTer supports it: core line `F2,GBCGB,Load GB-Transfer`, Pad 1 type
  TransferPak). Pokemon Stadium with Pokemon Red: the MGL loads the Game Boy ROM first (file index
  2), then the N64 ROM, and Auto Detect (`flash128k|tpak`) puts the Transfer Pak on pad 1. The
  Transfer Pak's memory *is the Game Boy game's own save*: Main mounts `saves/GAMEBOY/<gb rom>.sav`
  (the folder of the Game Boy core, or of the folder under `games/` the GB ROM came from), and when
  that file exists it first copies it to `saves/GAMEBOY/<gb rom>_bak.sav` and to
  `saves/N64/<n64 rom>_1.tpk` (padded to 32 KiB). With no Game Boy game loaded, `_1.tpk` itself is
  mounted (32768 bytes of FF) and Stadium stops at "There is a problem with the GB Game Pak's
  connector". Stadium's Game Pak Check read Red's save (RED, ID 59173) and wrote 32 bytes at
  0x0000-0x001F of the cartridge RAM: the Game Boy save changed, in plain Game Boy order, while the
  `.tpk` and `_bak` stayed copies of the original. A sync tool sees an N64 game modify a Game Boy
  save, plus two extra files.
- **Dezaemon 3D's 768 Kbit SRAM** is saved whole: `.sra` of 98304 bytes, the three 32 KiB banks in
  order. The game's first boot clears bank 0 to 00 and leaves banks 1-2 alone (FF from Main), the
  same as the libretro cores did in the one bank they have.
- **Timing:** the N64 core's ROM load takes a different time on every run (a timeline of Majora's
  Mask put the title at frame ~1600 after the script started; another run reached the file select
  with the libretro script's frame 1200), so START presses at fixed frames are fragile here.

## GameFAQs saves

The 29 N64 files of the GameFAQs pass (2026-11-05, `tools/GAMEFAQS.md`): the 21 in GameFAQs'
"Nintendo 64 DexDrive Save" sections and the 8 N64 "Wii VC Game Save File"s. Each is filed under
`n64/_<device>/<release> [GameFAQs <id>]/` exactly as served, with provenance and a proof
(Mupen64Plus-Next, ParaLLEl N64, standalone Mupen64Plus, in that order). Converted files are in
`.cache/gamefaqs-conv/n64/<id>/` (not committed); provenance records how and their hashes.

### What the files really are

| GameFAQs section says | Files | What the bytes show | Filed as |
| --- | ---: | --- | --- |
| DexDrive | 16 | DexDrive `.n64`: `123-456-STD`, 0x40 header, 16 comments of 256 bytes, a 32 KiB pak. Two stop early (943: pages 0-6; 11670: pages 0-11). 7 hold game notes (TWINE, Perfect Dark, THPS); 9 hold **GameShark cart saves** (below) | `_dexdrive` |
| DexDrive | 2 | Paks built by **savefileconverter.com** from an emulator EEPROM: 31112 says so in its comment; 33367 has the same ID-block pattern and an all-zero 0x1040-byte header | `_save-file-converter` |
| DexDrive | 1 | 18976: a raw `.sra`, 3036 bytes, words reversed, cut after the last byte written: Project64's way | `_project64` |
| DexDrive | 2 | 32471: a raw 16 Kbit EEPROM, no container. 32751: 135232 bytes, **all zeros** | `_unknown` |
| Wii VC | 8 | Wii `data.bin`: decrypted with the SD key, header MD5 valid for all 8 | `_wii-vc` |

**GameShark cart saves.** A pak note with game code `3B AD D1 E5` and publisher `FA DE` (named
`SMSM`, `BKBK`, `DODO`, `ZLZL`, with extension `1` or none) is a cartridge save that a GameShark's
Memory Card Manager copied onto the pak, so a DexDrive could read it (save-file-converter
`GameSerialCodeUtil.js`). This is why Ocarina of Time, Super Mario 64, Banjo-Kazooie and DK64,
which never use a Controller Pak, have DexDrive saves.
- **EEPROM** notes are the chip's bytes in console order, 2 pages for 4 Kbit. The device drops
  trailing padding pages: DK64's `DODO` is 7 pages and is padded with 00 to 2048 bytes, as
  save-file-converter does.
- **SRAM** notes (Ocarina of Time's `ZLZL`, 24 or 7 pages for a 32 KiB chip) are compressed: a
  4-byte **little-endian** length (`00 80 00 00` = 0x8000), then an **LZARI** stream (Okumura's
  LZARI.C: 4096-byte window, 60-byte matches, 15-bit arithmetic coder, the codec of Datel's PS2
  Max Drive). It decodes to the SRAM in console order, and all six OoT slots in both files have
  valid checksums. I found no public tool that decodes these: save-file-converter handles only
  uncompressed (EEPROM) notes. `n64-dexdrive.py`'s decoder matches mymcplus's LZARI byte for byte.

**DexPlorer ID blocks are invalid.** Every pak that DexPlorer formatted (943, 1043, 1091, 1156,
1263, 1260, 11670, 1704, 903: header bytes `0000010000 0303...`) has an all-zero serial and
checksums `0101`/`FEFD` in all four ID copies. libultra wants the second checksum to be
`0xFFF2 - sum` = `FEF1`. Given the pak as downloaded, Perfect Dark says **Damaged Controller Pak**,
TWINE says **Corrupt Controller Pak Detected... Attempt To Repair?**, and THPS offers to repair,
in all three cores. `n64-dexdrive.py` rewrites only the two checksums of each copy when no copy
is valid (`--keep-id` turns this off). The as-downloaded paks were also run for 943, 1043, 1704
and 903 to show the dialog. Mupen64Plus-Next formats its own paks with `FEF1`.

**Wii VC.** `data.bin` = AES-128-CBC header (0xF0C0: title ID, banner "WIBN", MD5), the plain
"Bk" header, then each file with its own IV (WiiBrew "Savegame Files"; save-file-converter
`Wii.js`). The N64 VC file is `RAM_<code>` (SRAM) or `EEP_<code>` (EEPROM or FlashRAM), the
chip **in console byte order** (vcromclaim `n64save.py` word-swaps it for Mupen64Plus):
- OoT `RAM_CZLE` / `RAM_NZLP`, SSB `RAM_NALP` / `RAM_NALJ`: 32768 bytes.
- Paper Mario `EEP_NMQE`: 131072 bytes of FlashRAM.
- Majora's Mask `EEP_NZSP`: **262144 bytes**: the 128 KiB flash, then 128 KiB of `AA`. The
  converter keeps the first half; save-file-converter keeps all of it as the `.fla`.
- **The VC fills untouched chip memory with `AA`**, not `FF`: whole unused FlashRAM pages, SRAM
  tails, OoT EU's header padding. No game objected.

### Conversion

`tools/gamefaqs/n64-dexdrive.py` (DexDrive, savefileconverter paks, raw `--raw eeprom` /
`--raw sram-swapped`) and `tools/gamefaqs/wiivc-convert.py` (Wii VC; also SNES and PCE) write:
- `save.srm`: the libretro cores' 296960-byte file. The pak goes in port 1 as is (padded with 00
  if the file stops early), ports 2-4 are blank paks formatted as mupen64plus-core does (zero
  serial, `FEF1`), and chip regions the file does not fill are `FF`.
- SRAM and FlashRAM words reversed (`WordOrder::Swapped`), EEPROM and paks in console order.
- For standalone Mupen64Plus, the same bytes as `.eep` / `.sra` / `.fla` / `.mpk` (four paks),
  copied into its save folder under its own name: GoodName (32 chars) + `-` + MD5 (8). 32 KiB
  `.sra` and 128 KiB `.fla` are byte-identical to the `.srm` regions.

### Saves x cores

All three cores agree on every save: **25 loads, 2 rejected, 2 not run each**. That took 81 save
runs, 12 runs of the as-downloaded paks, and a no-save baseline per game and core (45). Load scripts: `scripts/n64/<game>.load.txt`, with one
standalone variant (`007 - The World Is Not Enough.mupen64plus.load.txt`: a Down held 10 frames
moved two lines in that emulator's menu, so it is held 2).

| Id | Device | Release | Mupen64Plus-Next | ParaLLEl N64 | Mupen64Plus |
| --- | --- | --- | --- | --- | --- |
| 943 | `_dexdrive` | 007 - The World Is Not Enough (USA) | loads | loads | loads |
| 1083 | `_dexdrive` | 007 - The World Is Not Enough (USA) | loads | loads | loads |
| 1141 | `_dexdrive` | Banjo-Kazooie (USA) (Rev 1) | loads | loads | loads |
| 1156 | `_dexdrive` | Donkey Kong 64 (USA) | loads | loads | loads |
| 1263 | `_dexdrive` | Legend of Zelda, The - Ocarina of Time (USA) (Rev 2) | loads | loads | loads |
| 1260 | `_dexdrive` | the same (byte-identical to 1263) | loads | loads | loads |
| 11670 | `_dexdrive` | Legend of Zelda, The - Ocarina of Time (USA) (Rev 2) | loads | loads | loads |
| 1043, 725, 1704, 594 | `_dexdrive` | Perfect Dark (USA) (Rev 1) | loads | loads | loads |
| 34 | `_dexdrive` | Perfect Dark (USA) (Rev 1) | **rejected** | **rejected** | **rejected** |
| 1169 | `_dexdrive` | Perfect Dark (Europe) (En,Fr,De,Es,It) | loads | loads | loads |
| 1091 | `_dexdrive` | Super Mario 64 (USA) | loads | loads | loads |
| 1173 | `_dexdrive` | Super Mario 64 (Europe) (En,Fr,De) | loads | loads | loads |
| 903 | `_dexdrive` | Tony Hawk's Pro Skater (USA) (Rev 1) | **rejected** | **rejected** | **rejected** |
| 31112 | `_save-file-converter` | Super Mario 64 (USA) | loads | loads | loads |
| 33367 | `_save-file-converter` | Mischief Makers (USA) (Rev 1) | loads | loads | loads |
| 18976 | `_project64` | Super Smash Bros. (USA) | loads | loads | loads |
| 32471 | `_unknown` | Donkey Kong 64 (USA) | loads | loads | loads |
| 32751 | `_unknown` | Yoshi's Story (USA) (En,Ja) | not run: all zeros | not run | not run |
| 26519 | `_wii-vc` | Legend of Zelda, The - Majora's Mask (Europe) (En,Fr,De,Es) (Rev 1) | loads | loads | loads |
| 30445 | `_wii-vc` | Legend of Zelda, The - Ocarina of Time (USA) (Rev 2) | loads | loads | loads |
| 26520 | `_wii-vc` | Legend of Zelda, The - Ocarina of Time (Europe) (En,Fr,De) (Rev 1) | loads | loads | loads |
| 31013, 22873, 31011 | `_wii-vc` | Paper Mario (USA) | loads | loads | loads |
| 35242 | `_wii-vc` | Nintendo All-Star! Dairantou Smash Brothers (Japan) | not run: no ROM | not run | not run |
| 26527 | `_wii-vc` | Super Smash Bros. (Europe) (En,Fr,De) | loads | loads | loads |

The two rejections are the files' fault, the same in every core:
- **903 (THPS)**: the note `TH-ETR` has lost its extension byte; THPS lists only notes with
  extension `G` and says NO TONY HAWK GAME NOTES FOUND. With that one byte set to `G` (a
  diagnostic, not filed) it lists "ETR".
- **34 (Perfect Dark)**: the pak and its 28-page note are intact, but Choose Your Reality lists
  no agent. It was posted 11 days after the US release, so it may be from the first revision;
  the library has only Rev 1.

Content notes:
- **22873 (Paper Mario)** holds only a level-2 file "James": the "perfect game" in its description
  is not in the upload.
- **26520** holds three "LINK" files; the perfect one is File 3.
- The cartridge revision is never recorded in a pak note or a GameShark copy. Entries are named
  for the library's release that was used: Rev 1 / Rev 2.

### Releases the library lacks, and leads

- 35242 is the Japanese VC Smash Bros. (`NALJ`). It was converted, but not run.
- PAL releases came from the library's other N64 set and were copied to `.cache/roms/n64/` under
  No-Intro names: Europe OoT Rev 1, MM Rev 1, Perfect Dark, SM64, SSB.

### one-saves

`1saves` reads DexDrive files only for PS1 and has no Wii `data.bin` reader, so there was
nothing to compare. For the `.srm` reader:
- **ID blocks:** paks from DexDrive files carry DexPlorer's invalid `FEFD` ID checksum. A tool
  that validates paks should expect it; the games themselves offer to repair it.
- **Index checksums:** savefileconverter.com writes a 00 index-table checksum.
- **Unused bytes:** VC-derived chips have `AA` there, not `FF`.
