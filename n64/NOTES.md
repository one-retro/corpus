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
| n64-mister (MiSTer) | Not runnable here. 5 downloaded: Ocarina of Time (USA), Majora's Mask (USA), Banjo-Kazooie (USA), Donkey Kong 64 (USA), 007 - The World Is Not Enough (USA) (a `.cpk`) |

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
