# Sega Saturn

Ten US games, two runnable libretro cores. All 20 (game, core) pairs were filed. Five
downloaded saves were filed for two cores that cannot run here: three from real MiSTers and two
from standalone Mednafen. YabaSanshiro is in the brief's runnable list, but it cannot run on this
Mac (see below).

The Saturn has no per-game save chip. Every game writes named files into one filesystem, the
console's 32 KiB backup RAM, and can also use a Backup RAM Cart. So the differences worth testing
are mostly in how each core packages that filesystem: the container, the cart, the clock file, and
the file names. Where a game puts its file also depends on whether a cart is plugged in. Beetle
Saturn plugs one in by default and Yabause has none, so the same play lands in different files.

## Setup

**BIOS.** No Saturn BIOS is in the ROM library. I checked by name, by size (all 12,490 files of
524,288 bytes; I hashed the 227 that don't have a ROM extension and grepped them for Saturn
strings), and by the names of archives. The only copy on this machine is the owner's
RetroArch system folder, `mpr-17933.bin`, sha1 `faa8ea18…3fbc3`
(the US/EU v1.00 BIOS). That is a BIOS folder, not a save or sync folder, and I copied it to
`.cache/bios/saturn/`. Nothing was downloaded. Both cores booted through this real BIOS:

- Beetle Saturn looks for `mpr-17933.bin` for US discs.
- Yabause 0.9.15 tries `saturn_bios.bin`, then `sega_101.bin`, then `mpr-17933.bin`, and only
  falls back to its HLE BIOS when it finds none of them.

There is no Japanese BIOS (`sega_101.bin`), so Beetle refuses Japanese discs ("Cannot open BIOS
file sega_101.bin", rc 1). That ruled out Kakinoki Shougi and Deadalus, and is why all ten games
are US releases.

**The clock screen never appeared.** Beetle's `beetle_saturn_autortc` (on by default) sets the
SMPC clock from the host's local time at load. Yabause also starts the clock at host time, and its
BIOS did not ask either. The clock therefore reads the time of the run in both cores, which matters
for saves the game stamps (see the dirent notes below).

**Discs.** The machine's disk was almost full (100 MB to 6 GB free while I worked), and a Saturn
disc is 300–650 MB. I unpacked games from zipped discs onto a 2.5 GB
RAM disk (`hdiutil attach -nomount ram://…`, mounted at `work/saturn/ram`) instead of
`.cache/roms/`. Most games were run from the **data track alone**, with a cue that lists only
track 01 and is named like the Redump cue, so the save names match. The provenance `note` says
when this was done. The exceptions:

- Croc ran from a full Redump image.
- Legend of Oasis and Virtua Fighter 2 were unpacked in full.

**Pad.** Both cores map the libretro pad the same way: Saturn A=`b`, B=`a`, C=`r`, X=`y`, Y=`x`,
Z=`l`, L=`l2`, R=`r2`. Beetle plugs a pad into port 2 by default; Yabause doesn't. Daytona and
Sonic R grey out or skip their 2-player items without one.

## The ten games

Sizes are the game's own byte count from the save's directory entry. Every save was checked with
`1saves convert --system saturn` and then `1saves inspect`.

| Game (Redump) | What the game writes | Script ends with (proof) |
| --- | --- | --- |
| Nights into Dreams... (USA, Brazil) | Two files. NIGHTS___01 "Score data" (1856 B) is rewritten when a diary is named. NIGHTS___02 "A-life" (12544 B, 196 blocks) is the largest internal save here | Select Diary lists the diary "AAB" |
| Daytona USA - Championship Circuit Edition (USA) | DAYTONA96_0 "RECORDS" (4033 B), written on first boot. With a cart present it also writes DAYTONA96_1 "GHOST" (61713 B), which can't fit in internal memory | RECORDS screen |
| Croc - Legend of the Gobbos (USA) | CROCFISAVE1 "SAVED GAME" (224 B), from SAVE GAME on the first map. A real progress save | the slot grid with slot 0 filled |
| Sonic R (USA, Brazil) | SONICR___01 "SAVE_DATA" (336 B), from LOAD on the empty INT. DATA 1 | SELECT MODE |
| Sega Rally Championship (USA) | SEGARALLY_0 "RECORDS" (5056 B), written when leaving Options. The game prefers the cart | the main menu after Options → EXIT |
| Duke Nukem 3D (USA) | DUKENUKEM3D "save games" (832 B), after the game says "There was no save file. A save file will be created." and the player presses OK. The Saturn port saves progress only between levels | main menu |
| Tetris Plus (USA) | TETRIS_PLUS (2076 B), written on boot. With a cart present the game first asks SYSTEM or CARTRIDGE MEMORY | title |
| Virtua Fighter 2 (USA) | VFIGHTER2_X "VF2 data" (11432 B), written on boot | title |
| Fighters Megamix (USA) | FIGHTERS_MM "FI.MEGAMIX" (1396 B), written on boot | MODE SELECT |
| Legend of Oasis, The (USA) | OASIS2__SYS "Config." (148 B), written on boot. The story saves only at save points, which are too far for a script | NEW GAME: Leon's house |

Six of the ten files are written by the game on its own at first boot (records, options, unlocks).
That is a real file the game creates, but no player action is involved. NiGHTS (a named diary),
Croc (SAVE GAME), Sonic R (a data slot), Sega Rally (leaving Options) and Duke (OK on "a save file
will be created") are written because of what the script does.

Per-core scripts and shared parts:

- `Croc - Legend of the Gobbos.beetle-saturn.txt` and `Tetris Plus.beetle-saturn.txt` exist
  because the Beetle cart makes the game ask one more question: CHOOSE BACKUP / SELECT SYSTEM OR
  CARTRIDGE MEMORY. Both answer with the console's memory, so the file lands where it does in
  Yabause.
- `Fighters Megamix.beetle-saturn.txt` has different waits. Yabause plays the TrueMotion intro
  black and slowly and has to skip it early; Beetle needs two presses at other times.
- `_croc-to-save-menu.inc` and `_fighters-megamix.inc` are the parts each pair shares.

## Games x cores

| Game | beetle-saturn | yabause |
| --- | --- | --- |
| NiGHTS | filed | filed |
| Daytona USA CCE | filed (both files on the **cart**; internal empty) | filed (RECORDS only) |
| Croc | filed (beetle-saturn variant) | filed |
| Sonic R | filed (the same file in internal **and** cart) | filed |
| Sega Rally Championship | filed (file on the **cart**; internal empty) | filed |
| Duke Nukem 3D | filed (no `.bcr`: Beetle's database gives this game no cart) | filed |
| Tetris Plus | filed (beetle-saturn variant) | filed |
| Virtua Fighter 2 | filed | filed (the game later hangs in its attract demo at LOADING...PLEASE WAIT; the save was already written) |
| Fighters Megamix | filed (variant) | filed |
| Legend of Oasis | filed | filed |

| Core | Status |
| --- | --- |
| beetle-saturn | Beetle Saturn v1.32.1, real BIOS, default options |
| yabause | Yabause v0.9.15 8926b0c, real BIOS (found as `mpr-17933.bin`), default options |
| yabasanshiro | **not runnable here.** v3.4.2 09ed8e5 asks for a compatibility GL context, which macOS caps at 2.1, and aborts in `YglTMInit`. A test harness (`work/saturn/rr/`, `RR_FORCE_CORE=1`) gave it a 4.1 core profile; its shaders then failed with `version '430' is not supported`, and every polygon mode does the same. It needs GL 4.3, which macOS doesn't have. Before dying it writes `<savedir>/yabasanshiro/backup.bin`, described below. Downloads: a lead only |
| kronos | not runnable (no macOS build). Nothing found to file; leads below |
| mednafen | not runnable here (standalone). 2 downloaded |
| saturn-mister | not runnable here. 3 downloaded (real MiSTer files) |

## How each core writes the save

| | beetle-saturn | yabause | yabasanshiro (written at load, no game) |
| --- | --- | --- | --- |
| internal | `<stem>.srm` **32768**, packed. The frontend writes it through `RETRO_MEMORY_SAVE_RAM` (32768) | `<stem>.srm` **65536**, byte-expanded: each data byte on an odd offset, **0xFF** on every even one. **The core writes it itself** (`%s/%s.srm`); `RETRO_MEMORY_SAVE_RAM` is 0, so the frontend has nothing to write | `<savedir>/yabasanshiro/backup.bin`, **8388608** bytes. It is byte-expanded with 0xFF and holds one 4 MiB volume with 64-byte blocks (the signature is repeated 4 times). It is one file for all games, not per game |
| cart | `<stem>.bcr` **524288**, packed, written by the core. Plugged in by default ("Auto Detect" picks Backup Memory for most games, None for Duke Nukem 3D). Formatted by the core with the signature repeated **32×** (the whole 512-byte first block) | none: `yabause_addon_cartridge` offers only 1M/4M RAM carts | none |
| clock | `<stem>.smpc` **12** bytes (see below) | none | none |

**Same play, same bytes.** After collapsing Yabause's expanded file to 32 KiB:

- Croc, Legend of Oasis and Sonic R are byte-identical to Beetle's `.srm`.
- Duke, Tetris Plus and NiGHTS differ only in the dirent's timestamp minute (offset 0x9D) and, for
  NiGHTS, 2 bytes of game data.
- Fighters Megamix differs in 5 bytes and VF2 in 1.
- Daytona and Sega Rally differ wholesale, because Beetle put their files on the cart and left
  internal memory blank.

The payloads `1saves` reports match across cores for Croc, Daytona's RECORDS, Duke, Oasis,
NiGHTS, Sega Rally, Sonic R and Tetris. Only Fighters Megamix and VF2 differ.

**Placement depends on the cart.** This is the biggest trap for a sync tool, because the same
game in the same frontend splits its data differently by core:

- Daytona with a cart: RECORDS and the 61713-byte GHOST go to the cart, and the internal `.srm` is
  an empty, formatted volume. Without one, RECORDS goes to internal memory and GHOST is never
  written.
- Sega Rally: the cart if there is one, otherwise internal memory.
- Sonic R with a cart: the same 336-byte file is written to **both** (identical bytes).
- Croc and Tetris Plus ask the player which device to use.

**`.smpc`** (Beetle). For example, `01 20 26 3b 04 00 26 56 00 00 00 00` is:

- valid = 1;
- year BCD 2026;
- weekday 3 (high nibble) with month 0xB = November;
- day 04, 00:26:56. That is the host's **local** time when the core saved (the run ended at 00:26
  local; UTC was 08:26);
- BIOS SaveMem `00000000`: language 0, English.

Every filed `.smpc` differs only in the time.

**Dirents are the game's choice, not the core's.** Each save's 34-byte entry carries a language
byte and a timestamp (minutes since 1980). Both are written by the game through the BIOS, so
they match across cores:

| Language byte | Games |
| --- | --- |
| 0 | NiGHTS, VF2, Oasis, Sega Rally |
| 1 | Daytona, Croc, Sonic R, Duke, Tetris Plus, Fighters Megamix |

Timestamps:

- Most games stamp the SMPC time, i.e. the moment of the run.
- Sonic R writes 0 (1980-01-01 00:00).
- Croc writes a fixed 1980-01-01 00:30.
- Tetris Plus writes the right day and time but **five years late** (2031-11-04), in both cores. A
  date parser should not reject future dates.

**Yabause's HLE BIOS** (`yabause_force_hle_bios = enabled`, dry run, not filed) writes the
language byte as 0 where the real BIOS wrote the game's 1. That was Sonic R's only differing byte.

**Yabause's `retro_reset` loses backup RAM writes.** After a reset, a NiGHTS diary written just
before was gone. The core reloads backup RAM from its own `.srm` on disk, which it only writes
at unload. A frontend dump can't carry the data across either, because the core exposes no save
RAM region. So no script here power-cycles, and the proofs show the save in-game instead. In
RetroArch, "Reset" would lose unsaved progress the same way.

**Beetle Saturn's other save layouts** (dry runs of Sonic R, not filed):

| Option | Files written |
| --- | --- |
| `beetle_saturn_save_method = mednafen` | `<stem>.bkr` (32768, packed, written by the core) instead of `.srm`. Unlike standalone Mednafen, the name has **no md5** |
| `beetle_saturn_backup_memory_size = 4MB` | `<stem>.4mb.bcr`, 4194304 bytes, 1024-byte blocks (signature 64×); the `.bcr` is not written |
| `beetle_saturn_shared_int` + `_shared_ext = enabled` | the per-game `.srm` stays; the cart and clock become `mednafen_saturn_libretro_shared.bcr` / `.smpc` |

The brief says Beetle writes `.bkr`. In this build that is true only with the `mednafen` save
method; the default is `.srm` through the frontend.

## Downloaded entries

All five come from the test data of euan-forrester/save-file-converter (GPL-3.0; commit
0a9786f6b43d). That converter's author collected the files from users while adding Saturn
support, and the repository says which device or emulator made each one.

- `saturn-mister/Rayman (USA) (R2)/`, 1114112 bytes = 64 KiB internal + 1 MiB cart, both expanded
  with 0xFF. PR #340: "a file containing internal + cart saves from a real MiSTer". **The cart
  volume was formatted by the BIOS, which writes the signature only 4 times (0x40 bytes) even with
  512-byte blocks.** Mednafen and Beetle fill the whole block (32×).
  - one-saves' `saturn-backup` takes the block size from that repeat count, so it reads this
    cart with 64-byte blocks and rejects the file ("the save in block 528 states 1190 bytes and
    its blocks hold 144").
  - The crate README's "the number of times it repeats **is** the block size divided by sixteen"
    does not hold for hardware-formatted carts. The converter sizes blocks by file length for
    this reason.
- `saturn-mister/Daytona USA - Championship Circuit Edition (USA)/`, 65536 bytes, internal only,
  expanded with **0x00** rather than 0xFF. The converter's test says "Some files we were given
  from the mister are byte expanded out with 0x00". This is an early core build, before cart
  support.
- `saturn-mister/Sega Rally Championship Plus (Japan)/`, 65536 bytes, 0x00 expansion, with
  **garbage** in the even bytes of the first 0x40. It was attached to
  [Saturn_MiSTer #283](https://github.com/MiSTer-devel/Saturn_MiSTer/issues/283), where srg320
  (the core's author) explains that the high byte is ignored and reads 0xFF on hardware.
- `mednafen/Daytona USA - Championship Circuit Edition (USA)/`, a gzip member of 4375 bytes (OS
  byte 0x13, like the one-saves Mednafen sample) that inflates to the 512 KiB cart volume. It
  holds DAYTONA96_0 and DAYTONA96_1, the same two files Beetle wrote to its cart. Only standalone
  Mednafen gzips the cart. The file was renamed from Mednafen's `<stem>.<md5>.bcr`.
- `mednafen/Hyper Duel (Japan)/`, `.bkr` 32768 packed, plain. The converter's mednafen test uses
  it as the internal memory file.

What the MiSTer core does, from #283 and save-file-converter:

- One `.sav` per game: the internal memory expanded to 64 KiB, with the 512 KiB cart (expanded to
  1 MiB) appended once cart support arrived (Dec 2024).
- Fill bytes were 0x00 in older builds and 0xFF in newer ones.
- A Sept 2025 MiSTer main-branch update briefly broke Saturn saving
  ([SHIRO](https://www.segasaturnshiro.com/2025/09/05/new-mister-main-update-breaks-saturn-game-saving/)).

## Leads, not filed

- **YabaSanshiro**: save-file-converter's `segasaturn/yabasanshiro/backup.bin`.
  - 8 MiB, 25 saves from many games (PANDRA_3_01–03, B_RANGERS__, PANDRA_ZWEI, GUARDIAN_HE,
    NIGHTS___01/02, VFIGHTER_01, …), the same layout this machine's YabaSanshiro wrote.
  - It is one shared file, not per game, so it does not fit `<core>/<game>/`.
  - Downloaded to `.cache/downloads/saturn/sfc-yabasanshiro/`.
- **Yabause**: the same repository's `yabause/Akumajou Dracula X - Gekka no Yasoukyoku (Japan)
  (2M).srm`, 65536 bytes, 0xFF-expanded, from savefileconverter issue #365. Yabause runs here, so
  it is not filed. Downloaded beside the other.
- **Mednafen**: `Shining Force III Scenario 3 (English v25.1).bkr/.bcr` (a fan translation, not a
  Redump name; the converter notes that its own gzip output differs from Mednafen's by one bit)
  and `Dezaemon 2 (Japan).bkr`.
- **Kronos**: nothing found. The libretro forum thread "Kronos & Beetle: Sega Saturn Saves"
  (forums.libretro.com/t/19083, 2018) describes these files, but its attachments were on the
  defunct tinyupload:
  - per-game `<game>.ram` (internal, expanded with FF), and `<game>-ext512K.ram` for the cart
    (expanded to 1 MiB);
  - `shared_bup.ram` when saves are not per game;
  - the standalone build keeps `bkram.bin` (FCare/Kronos #1595).
  - The FCare/Kronos issue tracker has no save attachments.
- **Saturn_MiSTer issues**: the srg320 tracker has no save attachments; #17 notes a 64 KiB
  `boot.sav`, written when the BIOS is loaded by hand.

## Games tried and dropped

| Game | Why it was dropped |
| --- | --- |
| Christmas NiGHTS | NIGHTS_XMAS appears on boot, but the game's own "Set Clock" screen took left/right and nothing else (OK, A/B/C/Start, up/down) in Yabause, so the game never started |
| Dragon Force | both cores dropped to the BIOS CD player with the data-track-only cue (the Redump cue has two tracks) |
| SimCity 2000 | black after the SEGA logo in Yabause |
| Guardian Heroes, Last Bronx, Virtua Cop | black in Yabause |
| X-Men: Children of the Atom | fell into the CD player |
| Sonic 3D Blast | the TrueMotion intro ran at a few fps in Yabause |
| Worms | the menu didn't respond |
| Shining Force III, Shining Wisdom, the Legend of Oasis story, Panzer Dragoon Saga | first save point too far to script |
| Kakinoki Shougi, Deadalus | Japanese, so they need `sega_101.bin` in Beetle |
| Habitat II | needs the NetLink modem |
| Jonah Lomu Rugby (France) | no save written by the menus tried |

## Runner problems (worked around, nothing in tools/ changed)

- **make-save.py takes proof.png from the main script only.** A last `shot` inside an `include`d
  file is ignored and no proof is filed. The first Virtua Fighter 2 and Fighters Megamix entries
  were re-run with the final `shot` moved into the main script.
- **YabaSanshiro**: retro-run gives a compatibility-profile request the legacy 2.1 context, as
  RetroArch on macOS would. A core profile doesn't help either (GLSL 430). The patched copy in
  `work/saturn/rr/` is for diagnosis only.
- **Timing**: Beetle's loads are slower than Yabause's by 300–1500 frames, depending on the game.
  Shared scripts use generous waits, and the variants above cover the rest.
  - Most runs repeated frame for frame. One Tetris Plus timeline in Beetle was about 400 frames
    slower than every later run; I didn't find out why.
  - Yabause took minutes over intro movies (Sonic 3D Blast, Croc's attract demo) but always
    finished.
- `1saves inspect` reads only `.1saves` bundles. I wrapped each file first with
  `1saves convert FILE --system saturn` (it detects packed, expanded and gzip containers).
