# PC Engine CD / TurboGrafx-CD

Eight games, three runnable libretro cores: 24 played entries, all filed, every proof.png checked
by eye. Ten downloaded MiSTer saves. Five Analogue Pocket saves were already here, filed by the
device-backup worker.

Every CD game saves to the same place: the 2 KiB backup RAM ("BRAM") of the CD-ROM² unit or the
Duo, through the System Card's `bm_*` routines. There is no other save hardware on this system.
None of these games touches the MB128. So the variety here comes from the BRAM file system:
- the file name each game uses;
- file sizes from 26 to 1171 bytes;
- games that create their file at power-on and fill it later, against games that create it only
  when you save.

The three cores agree on the size (2048) and on the name (`<image stem>.srm`). Only Geargrafx
writes a different file: one header byte, the HUBM end pointer, differs. No core wrote a `.sav`,
a `.bram`, `geargrafx_mb128.sav` or any other extra file for CD content.

## The games

| Game (Redump) | Image used | BRAM file the game wrote | Why | Script ends with (proof) |
| --- | --- | --- | --- | --- |
| Ys Book I & II (USA) | `tg-cd/Ys Book I & II (NA).chd` | `YS.DATA.01` 61 B | the CD game people play; a menu save | "1 : Minea Town   Saved" |
| Ys III - Wanderers from Ys (USA) | `tg-cd/Ys III - Wanderers from Ys (NA).chd` | `YS3.DAT.01` 64 B | the same studio, a different file layout; the Pocket has one too | SELECT > LOAD: "1 : Sarina" |
| Dungeon Explorer II (USA) | `tg16cd-2/.../Champion Collection 4-L/Dungeon Explorer II (NA).chd` | `DUNGEON2  ` 632 B | the file is written when it is made, before play starts | after a reset, START > YES: CHOOSE A FILE shows file 1 in use |
| Exile (USA) | `.../4-L/Exile (NA).chd` | `XZR_DATA_1` 112 B, file ID byte 0x01 | a Working Designs menu save | BACKUP > SAVE: "Saved." |
| Exile - Wicked Phenomenon (USA) | `.../4-L/Exile - Wicked Phenomenon (NA).chd` | `EXILE2DATA` **1171 B**, the largest here | creates its whole three-slot file at power-on, then the save fills slot 1 | SAVE again: "#1 ASSASSI" |
| Prince of Persia (USA) | `.../M-Z/Prince of Persia (NA).chd` | `PER01.DAT ` **26 B**, the smallest | the time left is in the save, so it shows timing differences | SELECT DATA: "L01 03 59:48" |
| Beyond Shadowgate (USA) | `.../4-L/Beyond Shadowgate (NA).chd` | `SHADOW  #1` 616 B, with the 2-byte ID "BS" in the header | a pause-menu save into three numbered slots | pause again: LOAD 1 shows a disk instead of an X |
| Akumajou Dracula X - Chi no Rondo (Japan) | `tg-cd/Akumajou Dracula X Chi no Rondo (JP) (US)/...cue` (cue/img/ccd/sub, not CHD) | `DRACULA X ` 160 B, file ID "X " | Rondo of Blood; the Pocket and the MiSTer have one too. Starting a game writes the player's record. The name entry alone writes nothing | after a reset, the file screen shows PLAYER1 AAA |

The scripts are in `scripts/pcenginecd/`. Each one runs from power-on and presses RUN on the
System Card screen. Make-save is passed `--name` with the Redump name, because the image files
on the drive use "(NA)", "(JP) (US)", etc.

Games tried and dropped, so the next person does not repeat them:
- **Cosmic Fantasy 2.** "Start a new game" erases and re-creates the game's `COSMIC2-n` files.
  That is a real write, but not a save. The field menu has no SAVE; saving needs a save point
  further on.
- **Dragon Slayer - The Legend of Heroes.** The field menu (SPELLS ITEMS EQUIP DROP STATUS
  OPTION) has no save.
- **Loom.** It creates `LOOM` (82 B) at power-on, but its pointer interface needs the cursor
  steered onto a button.
- **Valis III.** It writes `VALIS_III` (48 B) when a game starts. I found no screen that proves
  it reads the file back.
- **Might and Magic III.** It writes `MM3-USA` at power-on: **1985 bytes, nearly the whole
  BRAM**, which is worth a test on its own. SELECT gives SAVE/LOAD, but my one SAVE attempt left
  the file unchanged. Out of time.
- **Dynastic Hero.** It writes nothing until a save point in a town.
- **J.B. Harold Murder Club.** I found no save.
- **Vasteel.** It writes `VASTEELM` (896 B) on entering a mode. I did not explore further.
- **Cotton, Puyo Puyo CD, Panic Bomber, Dungeon Master.** All four write their file at power-on
  (`COTTON` 56 B, `PUYOPUYO` 144 B, `P.BOMBER` 182 B, `DMS-SG.001` 425 B). Cotton only adds a
  record after a score over 10000.

## Games x cores

| Game | beetle-pce | beetle-pce-fast | geargrafx |
| --- | --- | --- | --- |
| Ys Book I & II | filed | filed | filed |
| Ys III | filed | filed | filed |
| Dungeon Explorer II | filed | filed | filed |
| Exile | filed | filed | filed |
| Exile - Wicked Phenomenon | filed | filed | filed |
| Prince of Persia | filed | filed | filed |
| Beyond Shadowgate | filed | filed | filed |
| Akumajou Dracula X | filed | filed | filed |

| Core | Status |
| --- | --- |
| mazamars312-pc-engine-cd (openFPGA) | not runnable. 5 device-backup entries from the owner's Pocket, filed by the device-backup worker (not by me): Ys Book I & II (USA), Ys III (USA), Dungeon Master (USA), Akumajou Dracula X (Japan) (FABT, FACT), "Dracula X ISO (Binchunker)". See below |
| turbografx16-mister (MiSTer) | not runnable. 10 downloaded (below) |
| mednafen (standalone) | not runnable (GUI). Nothing searched or found for CD |

Core builds: Beetle PCE v1.29.0 b96c11e, Beetle PCE Fast v1.31.0.0, Geargrafx 1.8.7. No options
file was needed.

**BIOS.** `.cache/bios/pcenginecd/` holds two files, both copied from
the No-Intro PC Engine set:
- `syscard3.pce` = `[BIOS] Super CD-ROM System (Japan) (v3.0).pce`, sha1 79f5ff55…;
- `syscard3u.pce` = `[BIOS] TurboGrafx CD Super System Card (USA) (v3.0).pce`, sha1 d02611d9….

All three cores load **`syscard3.pce`, the Japanese card**, by default:
- `pce_cdbios` and `pce_fast_cdbios` default to "System Card 3". The log shows
  `MDFN_MakeFName: …/syscard3.pce`.
- `geargrafx_cdrom_bios` defaults to "System Card 3"; its log says "Loading BIOS: syscard3.pce",
  which it identifies as "Super CD-ROM System [3.0] (J)".

The US discs boot on the Japanese card in all three cores. `syscard3u.pce` is only used if
`pce_cdbios = System Card 3 US` is set (Geargrafx has no US-card choice). Geargrafx also looks
for `gexpress.pce` and logs a harmless "problem opening" when it is missing.

**Timing.** Geargrafx's CD is slower than Beetle's:
- Ys plays its whole opening (about 7000 frames) where Beetle skips it on RUN.
- Prince of Persia reaches its title about 200 frames later.

The shared scripts use long waits, or button presses that are harmless when they land early,
instead of per-core variants.

## How each core writes the file

| | beetle-pce | beetle-pce-fast | geargrafx |
| --- | --- | --- | --- |
| File | `<image stem>.srm`, e.g. `Ys Book I & II (NA).srm`, `Akumajou Dracula X Chi no Rondo (JP) (US).srm` (the cue's stem) | same | same |
| Size | 2048 | 2048 | 2048 |
| BRAM header | `HUBM`, end **0x8800**, next free | same | `HUBM`, end **0xA000**, next free |
| After the last entry | 0x00 | 0x00 | 0x00 |
| Extra files | none | none | none (`geargrafx_mb128.sav` is only written for MB128 games; the MB128 option is Auto and none of these is in its list) |

- **Beetle PCE and Beetle PCE Fast wrote byte-identical files for all eight games.**
- **Geargrafx differs from them at offset 5 only** (0x88 against 0xA0) in seven games.
  Prince of Persia differs at 3 bytes: offset 5, the entry checksum at 0x12, and the time left
  at 0x22 (59:50 against 59:48, the CD-timing difference).
- Geargrafx's header byte comes from its init string `HUBM 00 A0 10 80`
  (src/memory.h). Internally it keeps an 8 KiB buffer: the first 2 KiB are zeroed and the rest
  is 0xFF. It exposes only 2048 bytes as `RETRO_MEMORY_SAVE_RAM`. So its file claims to end at
  0xA000 (8 KiB) while it is 2 KiB long. Beetle's `BRAM_Init_String` says 0x8800, as real
  hardware does.
- Not tested: whether a Geargrafx file loads in Beetle and the other way round. The game data
  is the same, so only a game or BIOS that checks the end pointer could object.

**Unformatted BRAM.** All three cores format the BRAM themselves (`HUBM`, end pointer,
next free 0x8010) before the game or BIOS sees it, so on a fresh start the System Card never
meets an unformatted one. To see what happens without that, I loaded an all-zero 2048-byte
`.srm` with `--srm` into beetle-pce-fast and geargrafx:
- System Card 3.0 left idle for 300 frames does not format it. The file stays all zeros.
- Cotton normally creates its `COTTON` file at power-on. On the zeroed BRAM it wrote nothing:
  the BIOS's `bm_` routines refuse an unformatted BRAM, and the file stayed all zeros.

So a zero-filled placeholder `.srm`, as a sync tool might create, silently breaks saving on all
three cores, until the user formats it in the System Card's BRAM manager (not tried here).

## Downloaded entries (turbografx16-mister)

All ten come from one zip:
- the zip: birdybro's whole MiSTer saves folder, attached to
  [save-file-converter #80](https://github.com/euan-forrester/save-file-converter/issues/80#issuecomment-1057487772)
  on 2022-03-02;
- downloaded and extracted by the pcengine worker into
  `.cache/downloads/pcengine/birdybro-mister-saves/` (sha1 9ced6d6c…);
- the files were copied from its `TGFX16/` folder.

Every file is raw 2048-byte BRAM with end pointer 0x8800, the same as Beetle, not 0xA000.

| Entry | BRAM content |
| --- | --- |
| Fantastic Night Dreams - Cotton (USA) | `COTTON` 56 B, the default ranking. Its first 64 bytes equal what beetle-pce-fast writes at power-on |
| Puyo Puyo CD (Japan) | `PUYOPUYO` 144 B. Same header and checksum as beetle-pce-fast's power-on file, so probably the defaults |
| Puyo Puyo CD Tsuu (Japan) | `PUYO2 B4` 144 B |
| Bomberman - Panic Bomber (Japan) (FAAT) | `P.BOMBER` 182 B. The checksum differs from the power-on default, so it holds played data |
| Bomberman - Panic Bomber (Japan) (FABT) | `P.BOMBER` 182 B, another played state |
| Dynastic Hero, The (USA) | the header says empty (next free 0x8010), but a `DYNASTIC01` entry is still in the bytes: a deleted file. A good test for parsers that must not trust leftover data |
| 1552 Tenka Tairan (Japan) | `KOUENJI` 17 B |
| Space Fantasy Zone (Japan) (Unreleased) | `SPACEFANTA` 96 B |
| Castlevania - Rondo of Blood - Arranged Perfect Audio + English Text (Japan) | `DRACULA X ` 160 B with player records |
| Castlevania - Rondo of Blood - English Text, Original Narrator (Japan) | the same |

The two Castlevania entries come from fan-patched images of Akumajou Dracula X - Chi no Rondo
(Japan). Their folders keep the user's image names, as the Pocket worker's "Dracula X ISO
(Binchunker)" does, because no Redump name fits a patched disc. The file name in the zip,
"Ys I & II (Japan)", is a formatted-only BRAM and is not filed.

## The Pocket entries (mazamars312-pc-engine-cd)

These are not mine. They are what makes them comparable with the played files:
- **Header.** End pointer 0x8800, the same as Beetle and the MiSTer.
- **Ys Book I & II (USA)** holds five `YS.DATA.0n` files (61 B each).
- **Ys III (USA)** holds `YS3.DAT.01`, 64 B, like ours.
- **Akumajou Dracula X (FABT, FACT)** holds the five Ys files *and* `DRACULA X `: one BRAM image
  carried from game to game, as on a real Duo. Its bytes after the last entry are not all zero
  (0x01, 0x20 appear), so the space past "next free" is not guaranteed to be clean.
- **Dungeon Master** holds `DMS-SG.001`, 425 B, the size this disc creates at power-on.

## Leads, not filed

- I made no separate web search for CD saves from the Pocket core, MiSTer core or standalone
  mednafen. These leads are for the next pass:
  - the Mazamars312 core's issue tracker on GitHub (PCE CD for the Pocket);
  - the MiSTer forum's TurboGrafx16 CD threads;
  - save-file-converter's other issues.
- Might and Magic III (its whole-BRAM file), Cosmic Fantasy 2 and Dynastic Hero (a town save,
  to compare with the MiSTer file) are the next games worth scripting.

## Runner notes

No harness problems. CHD and cue/img both load in all three cores. `--srm` worked for the
unformatted-BRAM test. The helper scripts used during development are in `work/pcenginecd/`.

## Standalone Mednafen (added after the libretro pass)

All eight scripts were replayed in standalone Mednafen 1.32.1, with an isolated data folder.
**8 entries filed out of 8 runs**, in `pcenginecd/mednafen/`. This replaces "mednafen (standalone):
not runnable" above. How Mednafen was driven is in `STANDALONE.md`. The libretro script buttons
map as: a = I, b = II, start = RUN.

- **Module and BIOS.** Mednafen picks its `pce` module for CD games, not `pce_fast`. It loads
  `pce.cdbios = syscard3.pce`, the Japanese System Card 3.0, by default, as the libretro cores do.
- **No CHD.** Mednafen 1.32.1 cannot open CHD. Seven discs were loaded as cue/bin files, extracted
  from the same CHDs with `chdman extractcd` into `.cache/roms/pcenginecd/`. Dracula X was loaded
  from its cue/img in place. Each entry's `rom` names the CHD the libretro entries used.
- **Where and what.** The file is `.mednafen/sav/<cue name>.<md5>.sav` in the home folder
  (`$MEDNAFEN_HOME/sav/`), for example
  `Ys Book I & II (NA).19afebaa65477f9de7d4d8c50a342358.sav`.
  - The md5 is the **"CD Layout" hash** Mednafen logs at load. It is computed from the disc's
    layout, not from the image file.
  - The file is the 2048-byte BRAM, raw.
  - The header is `HUBM` with end pointer **0x8800**, like Beetle, the MiSTer and the Pocket. It is
    not Geargrafx's 0xA000.
  - It is the same memory that the libretro cores write as `<image stem>.srm`. Only the name
    differs: an md5 is inserted and the extension is `.sav`.
- **Written on exit, and only if something wrote the BRAM.** A run that sat on the System Card
  screen for 330 frames left **no file**. RetroArch-style frontends write a `.srm` on every exit.
- **Same bytes as Beetle.** Seven of the eight files are byte-identical to the `beetle-pce` and
  `beetle-pce-fast` entries. They differ from Geargrafx's only at offset 5.
  - Prince of Persia differs at 0x12 (the entry checksum) and 0x22 (time left 59:49, against
    59:48 in Beetle and 59:50 in Geargrafx). That is CD timing again.
- **One weaker proof.** In Exile - Wicked Phenomenon, the proof frame shows the field menu a few
  frames before the slot list opens. The BRAM is still byte-identical to Beetle's, which shows
  `#1 ASSASSI`.

| Game | mednafen |
| --- | --- |
| Ys Book I & II | filed, = beetle-pce |
| Ys III | filed, = beetle-pce |
| Dungeon Explorer II | filed, = beetle-pce |
| Exile | filed, = beetle-pce |
| Exile - Wicked Phenomenon | filed, = beetle-pce |
| Prince of Persia | filed, time byte differs (59:49) |
| Beyond Shadowgate | filed, = beetle-pce |
| Akumajou Dracula X | filed, = beetle-pce |

## GameFAQs saves

The GameFAQs pass (2026-11-05, `tools/GAMEFAQS.md`) found one save for a PC Engine CD game here:
GameFAQs 26177, in the "Wii VC Game Save File (North America)" section of Ys III: Wanderers from
Ys. **It is not a PC Engine CD save:**
- It is 8192 bytes with no `$PCE` header and no `HUBM`, so it is neither a Wii export nor a BRAM.
- At 0x20 it holds "Wanderes from Ys (Ys-3) Programed by N.Fujisawa 91-04-24", a string found in
  the SNES Ys III ROM and not on the TurboGrafx-CD disc.

It is filed under `snes/_unknown/Ys III - Wanderers from Ys (USA) [GameFAQs 26177]/` and loads in
all 16 SNES cores (see snes/NOTES.md). No PC Engine CD core was run.

For a real VC TurboGrafx(-CD) save, `tools/gamefaqs/wiivc-convert.py` already handles
`pcengine.bup`:
- the file is `$PCE`, a seed, then an 8 KiB BRAM, each 4-byte block XORed with the NOT of the
  block stored before it (vcromclaim `tgsave.py`);
- it becomes the cores' 2 KiB BRAM, with the end pointer 0xA000 changed to 0x8800.

This path is untested: no such file turned up in this pass.

That BRAM header is worth knowing: the VC's 8 KiB BRAM ends at 0xA000, like Geargrafx's.
