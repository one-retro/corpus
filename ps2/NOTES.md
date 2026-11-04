# PlayStation 2 (ps2)

Ten games, saved by script on the four libretro PS2 cores that load here (LRPS2, PCEE2, Play!,
ARMSX2) and in standalone PCSX2 2.9.63, plus option variants (slot 2, per-game cards, PCSX2
folder cards): **48 default entries (of 50 attempted), 9 option/slot variants, and 11 downloaded
PCSX2 cards**. Every card was read back with `1saves convert`/`inspect` (and with a small
card-filesystem reader, `work/ps2/tools/mcfs.py`) and holds the saves listed below.

All BIOS-using cores ran SCPH-70012 (USA v2.00, 2004-06-14, file `ps2-0200a-20040614.bin`,
md5 d333558cc14561c1fdc334c75d5f37b7) placed as `<system>/pcsx2/bios/`. Play! uses its own HLE
BIOS. Discs are the library's US images (one Japanese), renamed to Redump-style names in
`.cache/roms/ps2/`; the four CD games are single-track MODE2/2352 `.bin` files, given a one-line
`.cue` for the cores that need one (hashes at the end).

## The cores

| Core (registry) | What it is | Runs here? | How |
| --- | --- | --- | --- |
| `lrps2` | buildbot `pcsx2_libretro.dylib`, reports itself as **"ParaLLEl PS2" v2.0.0-da5b07e** (LRPS2, the libretro PCSX2 fork); native arm64 EE/IOP/VU JIT | yes | Its OpenGL renderer needs `GL_ARB_shading_language_420pack`, which macOS's GL 4.1 lacks ("there will be no picture"; emulation still runs). `pcsx2_renderer = Software (SW)` (CPU-only) gives frames: `scripts/ps2/options/lrps2.txt` |
| `pcee2` | buildbot `pcee2_libretro.dylib`, **PCEE2 v2.9.138** (commit 571962773), a libretro port of PCSX2 2.9 | yes | Default renderer Vulkan; `software` and `parallel-gs` also need Vulkan (no MoltenVK here). `pcsx2_renderer = metal` works: the core draws with its own Metal device and hands frames to the frontend (`options/pcee2.txt`) |
| `play` | buildbot `play_libretro.dylib`, **Play! 0.77-17-g1f27232** (HLE BIOS) | yes | OpenGL 3.2 core context; no options. Takes `.cue`, not a bare `.bin` |
| `armsx2` | buildbot `armsx2_libretro.dylib`, **ARMSX2 720f409f** (the ARM64 PCSX2 port) | yes, blind | See "ARMSX2" below: missing libraries, no picture, emulation on its own thread |
| `pcsx2` | standalone **PCSX2 v2.9.63** (macOS app, x86_64 under Rosetta) | yes | Isolated `-datapath`, input from an SDL virtual gamepad; see "PCSX2 standalone" |
| `yaps2` | no buildbot build for macOS (arm64 or x86_64) | no | A PCSX2 fork for ARM Linux handhelds (github.com/yaps2/yaps2, GPL-3.0), shipped as Qt, SDL and an experimental Vulkan-only `yaps2_libretro` in Rocknix/Batocera nightlies; discontinued 2026-09 and merged into ARMSX2. Its libretro core keeps PCSX2's defaults (`libretro_saves = false`), so cards would be `<system>/pcsx2/memcards/Mcd001.ps2`/`Mcd002.ps2` as in LRPS2. No saves found online |

### ARMSX2

- The buildbot dylib links nine libraries by absolute paths of the build machine
  (the buildbot's `.../armsx2/.deps/lib/libwebp.7.dylib`, `libSDL3.0`, `liblz4.1`,
  `libjpeg.62`, `libpng16.16`, `libzstd.1`, `libfreetype.6`, `libplutovg.1`, `libplutosvg.0`), so
  `dlopen` fails. Workaround: `DYLD_LIBRARY_PATH=.cache/ps2-deps/lib`, holding links to Homebrew's
  copies (jpeg-turbo's `libjpeg.8` under the name `libjpeg.62`) and two stub libraries for
  plutovg/plutosvg (`tools/ps2/pluto-stubs.c`: they only draw SVG icons for PCSX2's own OSD).
- It renders only through Vulkan, from a frontend hardware context (retro-run offers OpenGL only,
  and there is no Vulkan here), and falls back to **Null GS: no picture**; the proofs are black.
  Its software renderer also needs the Vulkan device.
- The VM runs on its own thread at real-time speed (59.9 fps, frame-limited) and `retro_run`
  returns at once (2.1 million `retro_run` calls in 30 s), so script frames meant nothing. A
  `retro-run --pace 60` (originally a patch, now in `tools/retro-run`: sleep so that frames run at 60 per
  wall-clock second) maps script frames to emulated frames closely enough; the scripts ran
  unchanged.
- It cannot open a `.cue` ("Unable to identify the ISO image type"): the CD games ran from the
  `.bin`.
- The saves are verified by the card contents alone (they match the other cores, below).

### Running several at once

PCEE2 and ARMSX2 create a POSIX shared-memory object with a fixed name, `/GS.mem`, exclusively: a
second instance on the same machine aborts at load ("Failed to open /GS.mem due to File
exists ... Failed to allocate GS memory storage"). They were run one at a time. LRPS2 and Play!
run in parallel with anything.

## The ten games

| Game (script) | Serial | What is saved | Why |
| --- | --- | --- | --- |
| Marvel vs. Capcom 2 - New Age of Heroes (USA) | SLUS-20486 (CD) | `BASLUS-20486SYS`, 3 files, 53808 B; menu SAVE/LOAD > SAVE > SLOT 1 (or SLOT 2) | system file; offers both slots (the slot-2 variant) |
| Sega Ages 2500 Series Vol. 5 - Golden Axe (Japan) | SLPM-62385 (CD) | `BISLPM-62385GA`, 3 files; written by itself at power-on after "format? YES" | Japanese `BI` region prefix; first-boot system file |
| Rune - Viking Warlord (USA) | SLUS-20109 (CD) | `BASLUS-20109`, 3 files incl. a 64 KiB data file; at power-on | first-boot settings file |
| Gradius V (USA) | SLUS-20712 (CD) | `BASLUS-20712`, 3 files, 36340 B; SAVE/LOAD > SAVE | small system file (scores) |
| Max Payne 2 - The Fall of Max Payne (USA) | SLUS-20814 | `BASLUS-20814MaxPay2`, **15 files, 1.1 MB**: options, six 150 KiB empty slots, three icons; at power-on | many files in one save; large |
| Ecco the Dolphin - Defender of the Future (USA) | SLUS-20394 | `BASLUS-20394`, 9 files: a player file `ECCO_AAA` (initials entered), five `TEMP_n` | named player file |
| Shadow the Hedgehog (USA) | SLUS-21261 | `BASLUS-21261`, 5 files (8 KiB data, three 47800-byte icons) at power-on | first-boot game data |
| Ratchet & Clank (USA) | SCUS-97199 | `BASCUS-97199RATCHET`, 8 files, 341 KiB: five 58 KiB slots, save0 = new game | New Game creates a file |
| Ratchet & Clank - Going Commando (USA) | SCUS-97268 | `BASCUS-97268RATCHET`, 7 files, 468 KiB; played **on the card R&C 1 left** (`--start-from`), so that card holds **two games' saves**; Going Commando reads R&C 1 data | several saves on one card |
| Gran Turismo 4 (USA) | SCUS-97328 | `BASCUS-97328GAMEDATA`, 4 files, **1.5 MB** (1498 KB required, the game says); name entry "Lll" | the largest save |

Every save carries `icon.sys` and one or more 3D icons (`.ico`). Golden Axe, Rune, Max Payne 2,
Shadow and GT4 write without any menu save (at boot or on creating game data).

Tried and dropped in a quick survey: Inuyasha - Feudal Combat (asks to format, then no save
reached quickly), Marvel - Ultimate Alliance (no early save), Gradius III and IV (no save prompt
in the first two minutes).

## Games x cores

Default entries (the shared script, default options except the renderer):

| Game | lrps2 | pcee2 | play | armsx2 | pcsx2 (standalone) |
| --- | --- | --- | --- | --- | --- |
| Marvel vs. Capcom 2 | filed | filed | filed | filed | filed |
| Golden Axe (Japan) | filed | filed | filed | filed | filed |
| Rune | filed | filed | filed | filed | filed |
| Gradius V | filed | filed | filed | filed | filed |
| Max Payne 2 | filed | filed | filed with `.play.txt` (below) | filed | filed |
| Ecco the Dolphin | filed with `.lrps2.txt` | filed | filed | filed with `.lrps2.txt` | filed with `.lrps2.txt` |
| Shadow the Hedgehog | filed | filed | filed | filed | filed |
| Ratchet & Clank | **hangs** at the end of the intro | filed | **hangs** at the end of the intro | filed | filed |
| R&C - Going Commando | filed (blank card: R&C 1 hangs) | filed, card also holds R&C 1 | filed (empty card) | filed, card also holds R&C 1 | filed, card also holds R&C 1 |
| Gran Turismo 4 | filed | filed | filed | filed | filed |

48 of 50 filed. Not runnable here: yaps2 (no macOS build, nothing found online).

Variants (entry folder `<game> [variant]`):

| Variant | Cores | What it shows |
| --- | --- | --- |
| `Marvel vs. Capcom 2 ... [slot2]` (script `... [slot2].txt`) | lrps2, pcee2, play, armsx2, pcsx2 | the save on the slot-2 card: `Mcd002.ps2` (slot 1 `Mcd001.ps2` stays unformatted), Play! `vfs/mc1/` |
| `Golden Axe ... [per-game card]` (`options/lrps2-pergame.txt`) | lrps2 | `pcsx2_shared_memory_cards = disabled`: the card is `saves/<content name>.ps2` |
| `Marvel vs. Capcom 2 ... [slot2, per-game card]` | lrps2 | with per-game cards LRPS2 plugs **no card into slot 2**; the slot-2 press found nothing and the game saved to slot 1 |
| `Golden Axe ... [folder]`, `Max Payne 2 ... [folder]` | pcsx2 | PCSX2 **folder memory card** in slot 1 |

Script variants: `Ecco ... .lrps2.txt` waits 3300 instead of 2000 frames for the title (the
intro, title and attract demo cycle with no input, and START only works while the title
shows: 1500-2400 frames after the language screen in PCEE2/Play!, 2400-4800 in LRPS2, ARMSX2 and
standalone PCSX2). `Max Payne 2 ... .play.txt` presses at 3000 instead of 5000: Play!'s card is
always formatted, so the game asks "create a savegame folder?" instead of "format?", and that
prompt times out back into the intro before frame 5000.

## What each core writes

### Card files and folders

| Core | Slot 1 | Slot 2 | Format | Other files it writes |
| --- | --- | --- | --- | --- |
| lrps2 (default: `pcsx2_shared_memory_cards = enabled`) | `<system>/pcsx2/memcards/Mcd001.ps2` | `<system>/pcsx2/memcards/Mcd002.ps2` | raw 8 MiB card with ECC, **8650752 bytes**, created **unformatted (all 0xFF)** at load: the game formats it | `<system>/pcsx2/bios/<bios>.nvm` (1024 B NVRAM) and `.mec` (4 B), beside the BIOS; empty `cache/`, `cheats*/` folders. **No `.srm`** (save RAM size 0), nothing in the save directory |
| lrps2, `pcsx2_shared_memory_cards = disabled` | **`<savedir>/<content name>.ps2`** (e.g. `Sega Ages 2500 Series Vol. 5 - Golden Axe (Japan).ps2`) | **none**: slot 2 is empty (MvC2 shows no card) | same raw card | same NVRAM files |
| pcee2 | `<system>/pcsx2/memcards/Mcd001.ps2` | `Mcd002.ps2` | same, unformatted at creation | `.nvm`/`.mec`, `inis/playtime.dat`, `logs/emulog.txt`; options can disable either slot (`pcsx2_memcard_slot1_enable`, `..._slot2_enable`) |
| armsx2 | `<system>/pcsx2/memcards/Mcd001.ps2` | `Mcd002.ps2` | same | `.mec` only (no `.nvm`: the VM is never shut down at unload, see 0x210 below), `inis/armsx2-libretro.ini`, `inis/playtime.dat`, `logs/`, `cache/vu_jit/packs/<serial>_<crc>/*.pack` |
| play | **`$HOME/Documents/Play Data Files/vfs/mc0/<save folder>/<files>`**: a host folder per save, no card image | `.../vfs/mc1/...` | none: the "card" is a directory, always formatted, so no game asked to format | `config.xml` (absolute paths of all its folders) and empty `vfs/hdd`, `host`, `rom0`, `arcaderoms`, `states`. **It ignores the libretro save and system directories**: the runner gives it its own `HOME` |
| pcsx2 (standalone) | `<data>/memcards/Mcd001.ps2` (file card, the default) | `Mcd002.ps2` | same 8650752-byte raw card, created unformatted | `<data>/bios/<bios>.nvm` (1024 B) and `.mec` (4 B) |
| pcsx2, folder card (slot 1 pre-created as an empty folder card, as "Create Memory Card > Folder" does) | `<data>/memcards/Mcd001.ps2/` **a directory**: `_pcsx2_superblock` (8192 B), and one folder per save holding the save's files plus `_pcsx2_index` | `Mcd002.ps2` file card | no image on disk: PCSX2 builds the card in memory and writes the files out ("FolderMcd: Writing data for slot 0 to file system") | `_pcsx2_superblock` = the first 16 pages (data only, no ECC) of the equivalent file card, with 0xFF at the 0x210 bytes; `_pcsx2_index` is one-line flow-style YAML: `{$ROOT: {timeCreated: N, timeModified: N}, <file>: {order: K, timeCreated: N, timeModified: N}, ...}`, N = the JST wall time as Unix seconds (UTC+9 shifted). No root-level index. The save files are byte-identical to the file card's (Max Payne 2's `options.sav`/`.crc` differ run to run, as between cores) |

Entries keep the core's own paths: `system/pcsx2/...` (relative to the libretro system
directory), `saves/...` (save directory), `home/Documents/Play Data Files/...` (relative to the
home folder), and for standalone PCSX2 `memcards/...`, `bios/...` (relative to its data folder).
The `.nvm`/`.mec` files are console NVRAM, filed like Dolphin's `SRAM.raw`: not game saves, but
they sit next to the BIOS and a sync tool will meet them.

### Inside the files

- **Same save, same bytes, across cores.** Read through the card filesystem
  (`work/ps2/tools/compare.py`), the save files of MvC2 (both slots), Golden Axe, Rune and Gradius V are byte-identical in all five
  cores (lrps2, pcee2, armsx2, play, pcsx2), icons and `icon.sys` included, and so are the per-game
  and folder-card variants. So are all icons and `icon.sys` of every game, and the R&C/R&C2
  empty slots. Differences are in the game's own data where it depends
  on emulator state, not on the core's format:
  - Max Payne 2's six "empty" 150 KiB `savegameN.sav` and Ecco's five `TEMP_n` are **uninitialised
    game RAM** written as is; Max Payne 2's match in the whole PCSX2 family (lrps2 = pcee2 = armsx2
    = pcsx2) but differ in Play! (an HLE BIOS, so different memory contents), and Ecco's differ in
    every core.
  - Shadow's `BASLUS-21261`, GT4's `BASCUS-97328GAMEDATA` and `garage`, R&C's `save0.bin` and
    Max Payne 2's `options.sav`/`.crc` differ in every core: timers/play-time and RNG state.
- **Timestamps.** Every card directory entry has created/modified times; all PCSX2-family cores
  write the host's clock converted to **JST (UTC+9)**, as the PS2 does (a save made at 11:39 PST
  is stamped 04:39 the next day). Play! has no card, so no PS2 timestamps: only host file times.
- **The card superblock is identical** in all PCSX2-family cores and the downloads: "Sony PS2
  Memory Card Format 1.2.0.0", page 512, 2 pages/cluster, 16 pages/block, 8192 clusters,
  alloc_offset 41, alloc_end 8135, root at cluster 0, indirect FAT cluster 8, bad-block
  replacements at blocks 1023/1022, card_type 2, flags 0x2B.
- **8 bytes at raw offset 0x210** (page 1 of the card, which the PS2 filesystem does not use;
  its ECC is left as for 0xFF): PCSX2's `FileMcd` writes 8 bytes there when it **closes** a card
  that was written (its log says "Warning: checksum sector overwritten"). They depend on the
  card's contents: the same game gives the same 8 bytes in LRPS2, PCEE2 and standalone PCSX2
  (Golden Axe `15ed882888c03899`, MvC2 `b8692403e5579468`, Gradius V `6e530b630b0d0863`).
  **ARMSX2 leaves 0xFF** there: its libretro unload never shuts the VM down (no "NVRAM saved",
  no `.nvm`, no card close), so its cards differ from the others in these 8 bytes. Standalone
  PCSX2 too, if it is killed rather than quit (the first runs here; they were redone with a
  clean quit). Most downloaded cards have the bytes set. A tool that hashes whole cards sees
  this.
- Apart from that, two cores' cards for the same game differ only in the directory entries'
  timestamps and their ECC bytes (Golden Axe lrps2 vs pcee2: 15 pages, 4 runs: the root and save
  directory clusters 41-44, cluster 100, and the copies at clusters 8185-8188).
- **Slot 2 untouched = 8650752 bytes of 0xFF** (sha1 eac18874c24d...) in every PCSX2-family
  core, written at load whether or not a game looks at it; the same file appears six times among
  the downloads. Play! writes nothing for an unused slot.

## PCSX2 standalone

- The installed app is used only as a source: a copy (`work/ps2/pcsx2/PCSX2.app`) re-signed ad
  hoc, without the hardened runtime, so that `DYLD_INSERT_LIBRARIES` works. It is x86_64 and runs
  under Rosetta. The owner's PCSX2 folder (`Library/Application Support/PCSX2`) was never
  touched: every run has `-datapath <run dir>/data` (PCSX2 then uses `<data>/PCSX2/` for
  everything, inis included), `HOME=<run dir>/home`, `-nogui -batch -fastboot`.
- The ini is written beforehand from the full default PCSX2 wrote on a first run, with: setup
  wizard done, BIOS folder and file set (copied in), auto-update and achievements off, Null
  audio, keyboard and mouse sources off, Pad1 bound to `SDL-0`, and every hotkey removed except
  Screenshot (bound to a virtual paddle). The very first launch, before this, opened the setup
  wizard on screen (no BIOS); that instance was stopped.
- **Input:** `work/ps2/pcsx2/sdlpad.c`, injected with `DYLD_INSERT_LIBRARIES`, interposes the app's
  `SDL_InitSubSystem` and `SDL_PollEvent`: it attaches an **SDL3 virtual gamepad** (PCSX2 sees
  "sdlpad virtual gamepad" as SDL-0) and advances a timeline one step per drained input poll,
  which PCSX2 does once per vsync. Polls before the VM starts ("Opening GS" in the log) are not
  counted. `pcsx2-run.py` expands the same `scripts/ps2/*.txt` frame by frame as retro-run does;
  `shot` presses the Screenshot hotkey (PCSX2 saves an RGBA PNG at 2x, converted to a 640x480 RGB
  `proof.png`).
- A watchdog lists the app's windows (`CGWindowListCopyWindowInfo`, layer 0) every second and kills
  the app if a second window or a window without a running VM appears; only the game window
  ever showed after the first two runs (the setup wizard, above; and the main window flashing up
  when a ShutdownVM hotkey ended the run, so that hotkey was dropped). The run ends 5 s after the script with **SIGINT**, which PCSX2 treats as a clean
  exit request: the VM shuts down, the cards are closed (writing the 0x210 bytes described above) and the
  NVRAM is saved, with no window or dialog. (The first runs ended with SIGKILL: the card data was
  already written through, but those two closing writes were missing; every entry was redone.)
- **Input recording (`.p2m2`)** was looked at first: PCSX2 2.9 can play one only from the GUI
  (Tools > Input Recording) and has no command-line switch for it; PINE (IPC) reads and writes
  memory and states but has no pad input. Synthetic keyboard events are blocked here (no
  Accessibility permission), so neither route was usable.
- Every shared script worked unchanged except Ecco, whose title comes later than in PCEE2/Play!
  (as in LRPS2): it used `Ecco ... .lrps2.txt`. R&C 1 does not hang here.

## Harness notes

- `make-save.py` could not be used as is: PS2 cores keep their cards in the system directory
  (LRPS2, PCEE2, ARMSX2) or under `Documents` in the home folder (Play!), and its BIOS links would make the cores
  write `.nvm`/`.mec` into `.cache/bios`. `tools/ps2-save.py` is make-save with: a real
  system directory per run with only the BIOS file linked into `system/pcsx2/bios/`, a private
  `HOME`, filing of `system/pcsx2/memcards/**`, `system/pcsx2/bios/*.nvm|*.mec` and Play!'s
  `vfs/mc0|mc1/**` besides `saves/`, `--start-from ENTRY` (begin with another entry's cards),
  `DYLD_LIBRARY_PATH` for armsx2, and `--pace`.
- **retro-run `--pace FPS`** (first a patch, now in `tools/retro-run`) sleeps in
  `run_frames` so that at most FPS frames run per wall-clock second. Only ARMSX2 needed it.
- No core needed `--device`: all accept the default joypad (`pcsx2_analog_mode` etc. left alone).
- The first Play! test ran without the private `HOME` and created `Documents/Play Data Files`
  (config, empty folders, no saves) in the owner's home folder; it was deleted again (it held
  only what that test wrote). Every later Play! run had its own `HOME`.
- Ratchet & Clank (USA) **hangs** in LRPS2 (software renderer) and in Play! at the end of its
  intro (100% CPU, no more frames, at the "© 2002 Sony" card after the comet movie), with or
  without START pressed early. Not filed for those two; R&C 2 was then made on a blank card
  there. Going Commando in turn hangs in both a little after the save, after the script ends.

## Downloaded entries and leads

Searched by a helper agent on 2026-11-04 (about 45 minutes): GitHub issue attachments and repos,
the cores' trackers, the web. 35 cards were downloaded into `.cache/downloads/ps2/` (manifest
`MANIFEST.tsv` there); 11 PCSX2 entries were filed, chosen for variety, all `"method":
"downloaded"`, all from reporters on PCSX2's own issue tracker (PCSX2/pcsx2) who state their
PCSX2 version. No licence is stated on any of those pages. Folder names are `<the issue's game>
[PCSX2 issue N, ...]`, so they never collide with the played entries.

| Entry | PCSX2 | File(s) | What makes it useful |
| --- | --- | --- | --- |
| Largo Winch - Empire Under Threat [PCSX2 issue 12764, 32 MiB card] | v2.3.387 | `jizzle.ps2`, **34603008 B** | a 32 MiB card under a user-chosen name; 7 saves incl. Rune SLUS-20109 (identical to ours) |
| Atelier (Japan) [PCSX2 issue 12083, slot 2 card] | v2.3.56 | `Mcd002.ps2` | a slot-2 card on its own |
| Super Robot Taisen Alpha 3 (Japan) [PCSX2 issue 2588] | 1.5.0-dev-2550 | `MCD001.PS2` | upper-case name from an old build; 7 Japanese saves |
| Inuyasha - Feudal Combat [PCSX2 issue 13036, 43 saves] | v2.5.68 | `Mcd001.ps2` | a nearly full card, 43 saves of all regions |
| Thunder Force VI (Japan) [PCSX2 issue 13202, both slots] | v2.5.139 | `Mcd001.ps2`, `Mcd002.ps2` | both slots used (12 + 2 saves); Mcd001 includes a played Gradius V save |
| Gran Turismo 4 (USA) [PCSX2 issue 8303] | v1.7.4145-4169 | `Mcd001.ps2` | GT4 game data from an older build (same 4 files, 1528584 B) |
| Hitman - Blood Money [PCSX2 issue 12599, card named by serial] | 2.3.319 (macOS) | `SLUS-20552.ps2` | card named after a serial; holds GTA: Vice City and **BADATA-SYSTEM** |
| Obscure [PCSX2 issue 12843, with BADATA-SYSTEM] | v2.3.417 | `Mcd001.ps2` | several saves incl. Ratchet & Clank SCUS-97199 and **BADATA-SYSTEM** |
| Ratchet - Deadlocked (USA) [PCSX2 issue 14459] | v2.7.346 | `Mcd001.ps2` | a recent build, one 10-file save |
| The Punisher (USA) [PCSX2 issue 7166, file and folder card] | 1.7.3398 | `punisher.ps2` and `punisher folder.ps2/` | the same game as a file card and as a **folder card** (with `_N.del` deleted-file entries; the reporter calls the folder card corrupted) |
| The SpongeBob SquarePants Movie (USA) [PCSX2 issue 6708, folder card] | 1.7 nightly (2024-02) | `SpongeBob.ps2/` | folder card with `_pcsx2_meta/` per-file metadata |

Notes on them: the Largo Winch card's Rune folder is **byte-identical** to the Rune saves made
here (a fresh settings file; only the directory timestamps differ), and its filesystem is the
32 MiB geometry (32768 clusters, alloc_offset 137). Thunder Force's Gradius V folder has the same
icons as ours but a played data file. Six other downloaded slot-2 cards (not filed) are the
untouched all-0xFF card. One user (issues 12764, 13036, 13405) appears three times.

**one-saves** (`1saves` 0.4.0) reads every played file card and most downloads, but:
- any card holding the console's `BADATA-SYSTEM`/`BEDATA-SYSTEM`/`BIDATA-SYSTEM` folder (no game
  code in the name) fails `convert` with `header.game: is empty`: 10 downloaded cards, among them
  the two filed above and issue 14390's card (the other Ratchet & Clank card found);
- folder cards (PCSX2's `Mcd001.ps2/` directories, Play!'s `vfs/mc0/<save>/` folders, zipped or
  not) are not read at all ("Is a directory"; "holds no card and no save this reads");
- two downloaded cards are rejected as corrupt (issue 6647: a root entry that is all 0xFF; a
  16 MiB file with an 8 MiB filesystem from a dotfiles repo). Not filed.

**Leads, not filed:**
- ARMSX2 issues 15 and 18 (ARMSX2 v1.1, Android): two 32 MiB cards with 56 saves; one save was
  made in ARMSX2 but the card was built up before ARMSX2 existed (probably AetherSX2). Downloaded.
- More PCSX2 folder cards: `Doomwhite/pcsx2` (a "PCSX2 nightly" data repo, `MemCardAutoP1.ps2/`,
  block-style YAML `_pcsx2_index`; the repo also holds a BIOS, not fetched), `vivifalls/dotfiles`
  (`vivicard.ps2/`), `alexkimbrell31/NCAA-PS2-Dynasty-Save-Editor` (MIT; a card made by PCSX2's
  file-to-folder converter, one-line flow-style `_pcsx2_index`). Downloaded, not filed: the
  played folder-card entries cover the format.
- About 40 more PCSX2 issue attachments were seen but not fetched (e.g. issues 2795, 2812, 3147,
  3339, 4116, 4575, 6623-6625, 7424, 7656, 8320, 8602, 10519, 12112, 12197, 12629).
- Play!: nothing found (its trackers only link `.psu` exports of unknown origin). yaps2: two
  issues in its tracker, no saves.

## Disc hashes

| Image | Size | SHA-1 |
| --- | --- | --- |
| Marvel vs. Capcom 2 - New Age of Heroes (USA).bin | 239673504 | 3445ddf09b57bf5b2d493e75e21ff0cd9caa2759 |
| Sega Ages 2500 Series Vol. 5 - Golden Axe (Japan).bin | 156622032 | feee7bcfc73a81ae9bcb0f36cdfc62ada3639004 |
| Rune - Viking Warlord (USA).bin | 682364592 | 4204e6bd525b50af9f9ad254dc77cd2a5ae65f4b |
| Gradius V (USA).bin | 465832416 | 57a4a82fa3aa89d2fdd68c0d354aacca0fc82fd2 |
| Max Payne 2 - The Fall of Max Payne (USA).iso | 2602237952 | d0b049e29459be920668ee17d12231ed2822a1a5 |
| Ecco the Dolphin - Defender of the Future (USA).iso | 2318499840 | 38ceb0e7a0af144396023c8f20dc12cbfffbdd11 |
| Shadow the Hedgehog (USA).iso | 4493967360 | 4b10891453f72732a04dedc08252f5e53fbd088c |
| Ratchet & Clank (USA).iso | 4214095872 | aee9275384f739c9b24cd5de6f7e200292db7b01 |
| Ratchet & Clank - Going Commando (USA).iso | 3828350976 | f2cfaf0eb12b3c0d8fd6db7aa49ce032e8a6020b |
| Gran Turismo 4 (USA).iso | 5314478080 | 5b1dbf056f45f8023e8e4958e6d7deb31fc64a47 |
