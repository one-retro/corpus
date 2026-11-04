# NES

Ten games, played in the six runnable cores (fceumm, fixnes, mesen, nestopia, quicknes, rustynes):
54 entries filed out of 60 runs. There are also downloaded MiSTer and FCE Ultra saves, and
Analogue Pocket device backups that another process filed (see DEVICE-BACKUPS.md at the root).

## How the runs were made (runner patch)

`tools/retro-run` crashes two NES cores at load. It calls `retro_set_environment`,
`retro_set_video_refresh` and the other callbacks before `retro_init`, and only then
`retro_get_system_info`.

- **Mesen 0.9.9** segfaults in `retro_set_video_refresh`: it dereferences its renderer, which is
  created in `retro_init`.
- **RustyNES 3.6.0** (rust-libretro 0.3.2) panics with "retro_set_environment: Core has not been
  initialized yet!".

The workaround is in `work/nes/`:

- `runner/retro-run.c` is a copy of the tool. It calls `retro_get_system_info`, then
  `retro_set_environment`, then `retro_init`, then the callbacks, which is RetroArch's order.
- The copy also accepts the disk control interface and adds the `flip`, `disk N`, `eject` and
  `insert` script commands, for FDS.
- `make-save-alt.py` is `tools/make-save.py` with its `harness_for` pointed at that binary.
- Every entry here was made that way, and its provenance `note` says so.
- The fix belongs in `tools/retro-run`. The save logic is untouched, so the files are what the cores
  write under RetroArch.

## The ten games

| Game (script) | Board, save hardware | Why |
| --- | --- | --- |
| Legend of Zelda, The (USA) (Rev 1) (`Legend of Zelda.txt`) | MMC1, 8 KiB SRAM | The classic. You register "LINK" on the SELECT screen. 1Retro parser `zelda`. |
| Dragon Warrior (USA) (Rev 1) (`Dragon Warrior.txt`) | MMC1, 8 KiB | Begin a new quest as "ABC": the game writes Adventure Log 1 (ten copies). After a reset, CONTINUE lists it. Parser `dragon-warrior`. |
| Final Fantasy (USA) (`Final Fantasy.txt`) | MMC1, 8 KiB | New party, walk into Coneria, stay at the inn (400 G to 370 G). Parser `final-fantasy`. |
| Zelda II - The Adventure of Link (USA) (`Zelda II.txt`) | MMC1, 8 KiB | Register "LINK". There is also a MiSTer download of this game. |
| Destiny of an Emperor (USA) (`Destiny of an Emperor.txt`) | MMC1, 8 KiB | REGISTER HISTORY BOOK 1 ("00"). After a reset, GAME START lists it. Parser `destiny-of-an-emperor`. |
| Crystalis (USA) (`Crystalis.txt`) | MMC3, 8 KiB | Name "SIMEA", walk out of the cave into Leaf, save to file 1 from the save menu. Its layout is known to 1Retro (three 0x300 blocks, mirrored). |
| EarthBound Beginnings (USA, Europe) (Virtual Console) (`EarthBound Beginnings.txt`) | MMC3, 8 KiB | A new game saves itself to GAME(1) when play begins. After a reset, the menu shows "A Lvl 1". Parser `earth-bound`. |
| StarTropics (USA) (`StarTropics.txt`) | MMC6, 1 KiB inside the mapper | Register "MIKE". This is the odd size. Parser `startropics`. |
| Family Circuit '91 (Japan) (En) (`Family Circuit '91.txt`) | Namco 175 (mapper 210.1), 2 KiB | SETTING > GARAGE > SAVE slot A, named "ABBBBB". GARAGE > LOAD lists it. It has English menus. |
| Dragon Ball Z II - Gekishin Freeza!! (Japan) (Rev 1) (`Dragon Ball Z II.txt`) | Bandai LZ93D50 (mapper 16.5), 24C02 EEPROM, 256 bytes | The board menu's セーブ > データ1. This is the EEPROM case. |

## Games x cores

Legend: **F** filed, **x** failed (reason given), **n/r** not runnable here, **D** downloaded.
**dev** marks a device backup filed by another process; see DEVICE-BACKUPS.md.

| Game | fceumm | fixnes | mesen | nestopia | quicknes | rustynes |
| --- | --- | --- | --- | --- | --- | --- |
| Zelda | F | F | F | F | F | F |
| Dragon Warrior | F | F | F | F | F | F |
| Final Fantasy | F | F | F | F | F | F |
| Zelda II | F | F | F | F | F | F |
| Destiny of an Emperor | F | F | F | F | F | F |
| Crystalis | F | F | F | F | F | F |
| EarthBound Beginnings | F | F | F | F | F | F |
| StarTropics | F | F | F | F | F | F |
| Family Circuit '91 | x: no file (note 1) | F | F | x: not saved (note 2) | x: mapper 210 not supported, black screen | F (note 3) |
| Dragon Ball Z II | F | x: hangs at load (note 4) | F | x: writes nothing (note 5) | x: mapper 16 not supported, black screen | F |

Notes to the table:

1. fceumm does run Family Circuit '91, and GARAGE > LOAD shows ABBBBB. But it reports 0 bytes of
   save RAM for this board, so no file is ever written.
2. Nestopia writes an 8 KiB `.srm`, but the garage save never reached it. LOAD shows garbage in
   every slot, and the file holds only the work bytes at 0x780. The entry was not filed.
3. RustyNES's file is real: its 2 KiB at 0x1800 are byte-identical to Mesen's. But in RustyNES the
   game's LOAD list then showed slot A empty, so RustyNES reads that RAM back wrong. This is noted
   in the entry's provenance.
4. fixNES never gets past load. In the full run it sat at 0% CPU until killed. In a boot probe it
   exited with rc 1, as it did for every mapper 16, 153 and 159 cart tried.
5. Nestopia reports 0 bytes of save RAM for the EEPROM boards (mapper 16 and 159) and writes no
   file at all.

The remaining cores cannot run here:

- **agg23-nes** (openFPGA): dev for Zelda, Crystalis, StarTropics, Dragon Warrior IV and two
  hacks/translations.
- **spiritualized-nes** (openFPGA): dev for Zelda, Dragon Warrior IV and Lagrange Point, plus its
  `palram.bin`.
- **nes-mister** (MiSTer): D for Zelda, Dragon Warrior, Final Fantasy, Zelda II, Crystalis,
  StarTropics, Kirby's Adventure, Shingen the Ruler and both Wizardry games.
- **fceux** (standalone): D for Final Fantasy (an FCE Ultra 0.98.12 file; see below).
- **mednafen** (standalone): nothing found. **bnes** and **emux-nes** were built from source since
  (BUILT-CORES.md): bnes filed 7 of 10 (not StarTropics, Family Circuit '91 or DBZ II); emux-nes writes no save.

## What differs between the cores' files

All runnable cores write `<ROM stem>.srm` into the save directory. The exception is Mesen, which also
writes its own EEPROM file. The differences:

**Size.** For plain 8 KiB carts (MMC1, MMC3) every core writes 8192 bytes. For the others:

| Game / board | fceumm | fixnes | mesen | nestopia | quicknes | rustynes |
| --- | --- | --- | --- | --- | --- | --- |
| StarTropics, MMC6 1 KiB | 8192, the 1 KiB at 0x1000-0x13FF, rest 00 | **131072**, the 1 KiB at 0x1000, rest 00 | 1024 | 1024 | 8192, the 1 KiB at 0x1000, rest FF | 1024 |
| Family Circuit '91, N175 2 KiB | none (0 bytes of save RAM) | **131072**, the 2 KiB at 0x1800 | 2048 | 8192 (broken, see above) | (8192, never filed) | 8192, the 2 KiB at 0x1800 |
| Dragon Ball Z II, 24C02 | 256 `.srm` | (no load) | **`.eeprom256` 256 = the data, plus `.srm` 256 all 00** | none | (8192 FF, no load) | 256 `.srm` |

- Mesen 1024, Nestopia 1024 and RustyNES 1024 are byte-identical for StarTropics. fceumm and fixNES
  have the same 1 KiB at 0x1000, except 5 bytes of timing.
- Mesen's split matters most. For the Bandai EEPROM, Mesen keeps the real contents in
  `<stem>.eeprom256`. The `.srm` that RetroArch writes from `retro_get_memory(SAVE_RAM)` is 256
  zero bytes. A tool that syncs only the `.srm` loses the save.
- In the EEPROM, the bytes the game never wrote are 00 in fceumm and Mesen and FF in RustyNES, like
  an erased chip. The written bytes agree between fceumm and Mesen apart from 9 timing bytes.

**Fill.** QuickNES powers on battery RAM as FF. Every other core uses 00. So QuickNES's files differ
from the others' in every byte the game never wrote: Zelda 4 bytes, Zelda II 6379, Destiny 4102,
EarthBound 2653, Final Fantasy 1808. Every one of these is FF where Mesen has 00. In Dragon Warrior
6765 bytes differ, because the boot code that wipes the logs runs over an FF field.

**Identical files.** These are byte-identical in fceumm, fixNES, Mesen, Nestopia and RustyNES:
Zelda, Dragon Warrior, Zelda II, Destiny of an Emperor and EarthBound. Crystalis and Final Fantasy
differ by 1-46 bytes of timing (RNG and frame counters in the work-RAM part). Mesen and Nestopia
agree exactly on both.

**Boot probes (not saves: the save RAM size each core reports, from a 600-frame boot).** These are
for boards not in the ten. They are worth a look for the next pass:

| Board (game) | fceumm | fixnes | mesen | nestopia | quicknes | rustynes |
| --- | --- | --- | --- | --- | --- | --- |
| MMC5 32 KiB (Romance of the Three Kingdoms II) | 32768 | 65536 | 33792 (+1 KiB ExRAM) | 32768 | 8192 | 32768 |
| MMC5 8+8 KiB (Uncharted Waters) | 8192 | 65536 | 9216 | 8192 | 8192 | 8192 |
| MMC1 SOROM 8+8 KiB (Nobunaga's Ambition) | 8192 | 8192 | 8192 | 8192 | 8192 | **16384** |
| Taito X1-005, 128 B internal (Kyonshiizu 2, Minelvaton Saga) | 256 | 8192 | 256 | 0 | 8192 | 128 |
| Bandai 24C01, mapper 159 (SD Gundam Gaiden, DBZ Kyoushuu, Taruruuto-kun) | 128 | load fails | 128 + `.eeprom128` | 0 | 8192 | 128 |
| Bandai mapper 153 (Famicom Jump II) | 8192 | load fails | 8192 | 8192 | 8192 | 8192 |
| Namco 163 (Megami Tensei II) | 8192 | **393216** | 8192 | 8192 | 8192 | 8192 |

## Downloaded entries (`method: downloaded`)

Found by a search subagent. The files were sanity-checked here: sizes, non-blank, layout.

- **nes-mister**: Zelda, Zelda II, Final Fantasy, Dragon Warrior, Crystalis, Kirby's Adventure and
  StarTropics are 32768 bytes each. Shingen the Ruler and both Wizardry games are 8192.
  - They are birdybro's own MiSTer saves (a MiSTer contributor), attached to
    github.com/euan-forrester/save-file-converter issue #80.
  - MiSTer writes 32 KiB for an iNES 1.0-headered ROM and 8 KiB when a NES 2.0 header declares the
    PRG-NVRAM. So even StarTropics (1 KiB of RAM) is a 32 KiB file.
  - The 8 KiB comes first, then 24 KiB that is sometimes non-zero (stale SDRAM).
  - Two files keep the old No-Intro "(Rev A)" names.
- **fceux / Final Fantasy (USA)**: `Final Fantasy10-TempleofFiends.sav`, 8192 bytes, from
  fantasyanime.com. It was written by **FCE Ultra 0.98.12**, FCEUX's ancestor, not FCEUX itself.
  - The paired `.fc0` state's WRAM chunk is byte-identical to it.
  - The `.sav` format is the same raw 8 KiB.
  - Drop it if the slot must be FCEUX proper.
- **agg23-nes / spiritualized-nes**: Analogue Pocket device backups, filed by another process, not
  by this pass (see DEVICE-BACKUPS.md).
  - agg23.NES writes the whole 256 KiB slot (262144 bytes) for every battery cart.
  - Spiritualized.NES writes 8 KiB.

Leads not filed:

- birdybro's saves.zip holds about 100 more NES and FDS saves (Dragon Warrior II-IV, Ultima, Faria
  and others).
- His Dragon Ball Z II and SD Gundam Gaiden 2 MiSTer saves are all zero, the old EEPROM bug
  (NES_MiSTer #150).
- The other 12 fantasyanime FF1 saves are also FCE Ultra.
- Nothing was found for mednafen, bnes or emux-nes.
- Searched for agg23 and Spiritualized: their issue trackers, pocket-sync, the Analogue and MiSTer
  forums, GameFAQs and archive.org.

## Tried and dropped (timeboxed)

- **Kirby's Adventure.** The first save needs stage 1-1 cleared (completion count > 0).
- **Romance of the Three Kingdoms II and Nobunaga's Ambition.** Koei's Y/N prompts answer to the
  d-pad, not A/Start, and the title timing differed between cores. Done in the second pass (below):
  LEFT answers Y, RIGHT answers N.
- **SD Gundam Gaiden, Magical Taruruuto-kun, DBZ Kyoushuu (24C01) and Minelvaton Saga, Kyonshiizu 2
  (X1-005).** No save was reached in about 3000 frames of play, or the name entry would not close.
  X1-005 is covered by Taito Grand Prix in the second pass; 24C01 is still uncovered.

## Second pass: Koei boards and the board sweep

Five more games, each played to a genuine in-game save by one script in `scripts/nes/` and replayed
in all six runnable cores. Every proof.png was checked by eye, and every filed save was also
reloaded from its file in a fresh run of the same core. These runs used `tools/retro-run` directly (it now
calls the core in RetroArch's order), not the patched copy in `work/nes/`. 21 entries filed out of
30 runs.

### The sweep

All 1392 ROMs in the headered 1G1R set carry NES 2.0 headers, so mapper, submapper and PRG-NVRAM
size are declared. The battery-backed boards (mapper.submapper, PRG-RAM + PRG-NVRAM as declared):

| Board | NVRAM | Games | Corpus |
| --- | --- | --- | --- |
| 1 MMC1 (SxROM) | 8 KiB | 114 | yes (Zelda, DW, FF, Zelda II, Destiny) |
| 1 MMC1 SOROM | 8 KiB + 8 KiB volatile | 4 | **Nobunaga's Ambition** |
| 1 MMC1 SXROM | 32 KiB | 2 (Dezaemon, Best Play Pro Yakyuu Special) | attempted (below) |
| 4 MMC3 / 4.1 MMC6 | 8 KiB / 1 KiB | 73 / 2 | yes (Crystalis, EarthBound / StarTropics) |
| 5 MMC5 | 8 KiB | 3 (Gemfire, Just Breed, ...) | no (size already covered) |
| 5 MMC5 | 32 KiB | 3 | **Romance of the Three Kingdoms II** |
| 5 MMC5 | 8 KiB + 8 KiB volatile | 5 | **Uncharted Waters** |
| 10 MMC4 | 8 KiB | 3 (Fire Emblem x2, Famicom Wars) | no |
| 16.5 Bandai 24C02 | 256 B EEPROM | 6 | yes (DBZ II) |
| 159 Bandai 24C01 / 157 Datach | 128 B EEPROM | 4 / 1 | attempted (below) |
| 18, 21.2, 25.3, 26, 68, 69, 85.2, 118, 153, 155 | 8 KiB | 1-3 each | no (Jaleco SS88006, Konami VRC2/4/6/7, Sunsoft-4, FME-7, TxSROM, Bandai 153, 155) |
| 19.2 Namco 163, battery, no NVRAM declared (the save is the N163's internal 128 bytes) | (128 B in the mapper) | 6 (Hydlide 3, Famista '90, Battle Fleet, ...) | attempted (below) |
| 19.2/19.3/19.5 Namco 163 | 8 KiB | 6 | **Pac-Man - Championship Edition** |
| 80 Taito X1-005 | 128 B in the mapper | 5 | **Taito Grand Prix** |
| 82 Taito X1-017 | 8 KiB declared (5 KiB in the mapper) | 4 | attempted (below) |
| 210.1 Namco 175 | 2 KiB | 1 | yes (Family Circuit '91) |
| 547 | 8 KiB + 8 KiB | 4 (NHK Gakuen etc.) | no |

### The five games

| Game (script) | Board, save | Save | Why |
| --- | --- | --- | --- |
| Romance of the Three Kingdoms II (USA) (`Romance of the Three Kingdoms II.txt`) | MMC5, 32 KiB | scenario 1, one player as Yuan Shu, level 1; first turn SELECT -> 3.SAVE -> Y. Proof: after a reset, 7.Load Saved Game, Yuan Shu's orders, Jan 189 | the largest MMC5 RAM |
| Uncharted Waters (USA) (`Uncharted Waters.txt`) | MMC5, 8 KiB battery + 8 KiB volatile | hero "AAA", every bonus point spent, flagship named; Lisbon: SELECT -> Save -> Y, Quit? N. Proof: after a reset, Saved Game -> Lisbon, Feb 21 1502 | two RAM chips, one kept |
| Nobunaga's Ambition (USA) (`Nobunaga's Ambition.txt`, variant `.nestopia.txt`) | MMC1 SOROM, 8 KiB battery + 8 KiB volatile | 50 fiefs, Kakizaki of Ezo, skill 1; 20 Other -> 4 Save -> Y, then 17 Rest one season (the game writes at the end of the season). Proof: after a reset, New game? N loads 1560 Summer | the board where RustyNES writes 16 KiB |
| Taito Grand Prix - Eikou e no License (Japan) (`Taito Grand Prix.txt`) | Taito X1-005, 128 B inside the mapper | NORMAL -> なまえ とうろく "ああああ", SELECT, A. Proof: after a reset, PLAY SELECT shows レーサー ああああ, RANK D, 10万円 | X1-005 internal RAM; the previous pass's X1-005 games never reached a save |
| Pac-Man - Championship Edition (USA, Europe) (Namco Museum Archives Vol 1) (`Pac-Man - Championship Edition.txt`) | Namco 163 (19.3), 8 KiB | one NORMAL game with no input (40 points, three lives lost); the game keeps the result and a replay. Proof: after a reset, OPTIONS -> REPLAY NORMAL plays it back | Namco 163 with WRAM; a modern (2020) NES release |

Koei input: numbers go up/down (RIGHT moves to the next digit), every (Y/N) is answered by the
d-pad, LEFT = Y and RIGHT = N; A and START do nothing there. Random events (an alliance letter in
RoTK II; revolts, wars and the rolled abilities in Nobunaga) differ between cores, so the scripts
wait long and handle an event either way: RoTK II presses B then A twice (B
skips the letter's prompt, A reopens the orders menu), Nobunaga rests rather than passes (a
neighbour's attack in the first season waits for input after Pass, but the computer fights it for a
resting daimyo). In Nestopia Tsugaru attacked Ezo before Kakizaki's first turn anyway, so its
variant plays the 17-fief game as Uesugi with the same save steps.

| Game | fceumm | fixnes | mesen | nestopia | quicknes | rustynes |
| --- | --- | --- | --- | --- | --- | --- |
| Romance of the Three Kingdoms II | F | F | F | F | x: garbage screen after the player count (1) | F |
| Uncharted Waters | F | F | F | F | x: corrupt screen, stuck at "Save game?" | x: writes 8 KiB of 00 (2) |
| Nobunaga's Ambition | F | x: wrong chip (3) | x: wrong chip (3) | F (variant) | x: wrong chip (3) | F |
| Taito Grand Prix | F | F | F | F | x: mapper 80, black screen, 8 KiB of FF | x: 128 bytes of 00 (4) |
| Pac-Man Championship Edition | F | F | F | F | x: mapper 19, black screen, 8 KiB of FF | F |

1. QuickNES reports 8 KiB for this 32 KiB MMC5 board and the screen turns to tile garbage at the
   game-level prompt.
2. RustyNES runs Uncharted Waters and saves in session (a soft reset continues), but its `.srm` is
   8192 zero bytes, not the chip the game saved to. A fresh run from the file starts a New
   Adventure. Its RoTK II (one 32 KiB chip) is fine.
3. fixNES, Mesen and QuickNES write one 8 KiB file whose layout is that of RustyNES's *first*
   8 KiB, the volatile work chip (work data at 0x0000-0x03FF). fceumm and Nestopia write the battery
   chip (nothing at 0x0000-0x03FF, the layout of RustyNES's *second* 8 KiB). fixNES and QuickNES
   fail even within the session: after the soft reset the game says "Data can't be used / Hit any
   key", so they do not bank SOROM's two chips. Mesen does: in session the save loads (1560 Summer),
   but its `.srm` is the wrong chip, and a fresh run from it ignores "New game? N".
4. RustyNES shows the registered racer in session but its 128-byte file is all zeros; reloaded, the
   racer list is empty. The X1-005 RAM is not persisted.

### What differs between the files (second pass)

| Game / board | fceumm | fixnes | mesen | nestopia | rustynes |
| --- | --- | --- | --- | --- | --- |
| RoTK II, MMC5 32 KiB | 32768 | **65536**: 32 KiB of 00, then the 32 KiB | **33792** = 32 KiB + 1 KiB ExRAM | 32768 | 32768 |
| Uncharted Waters, MMC5 8+8 | 8192 | **65536**: the 8 KiB at 0x2000, other RAM at 0xA000 | **9216** = 8 KiB + 1 KiB ExRAM | 8192 | (8192 of 00) |
| Nobunaga, SOROM 8+8 | 8192 (battery chip) | (8192, work chip) | (8192, work chip) | 8192 (battery chip) | **16384**: work chip, then battery chip |
| Taito Grand Prix, X1-005 128 B | **256: 128 of 00, then the 128** | **8192: the 128 at 0, then 00** | **256: the 128, mirrored twice** | 128 | (128 of 00) |
| Pac-Man CE, N163 + 8 KiB | 8192 | **393216**: the 8 KiB, then 00 | 8192 | 8192 | 8192 |

- RoTK II: Mesen (first 32 KiB), fixNES (second 32 KiB), Nestopia and RustyNES are byte-identical;
  fceumm differs in 298 bytes: a different random event at the start changed the game state (the
  province figures in its proof differ). The data runs from 0x2006 to 0x7D82; the first 8 KiB stay
  zero. Mesen appends the MMC5's 1 KiB ExRAM (416 non-zero bytes); no other core saves it.
- Uncharted Waters: fceumm, Mesen (first 8 KiB) and Nestopia identical; fixNES's 0x2000-0x3FFF is
  the same 8 KiB and 0xA000-0xBFFF holds 2108 more non-zero bytes (the volatile chip). Mesen's ExRAM
  tail: 488 non-zero bytes.
- Taito Grand Prix: the 128 bytes agree in every core that kept them, but sit at different
  offsets: at 0x00 in Nestopia (the whole file) and fixNES, at 0x80 in fceumm (0x00-0x7F zero), and
  at both 0x00 and 0x80 in Mesen. A reader has to know each core's offset. Nestopia, which reported 0 bytes
  for the X1-005 games Kyonshiizu 2 and Minelvaton Saga in the first pass, keeps 128 here, so its
  X1-005 support depends on the game, not only the board.
- Pac-Man CE: the 8 KiB is byte-identical in all five; no core saves the Namco 163's own 128 bytes
  for this board. fixNES's 393216 is the size it also reports for Megami Tensei II (another N163).
- No core here wrote any file besides `<stem>.srm` for these five.

### Attempted, not filed (timeboxed)

Boot probes (900 frames; save RAM bytes each core reports):

| Board (game) | fceumm | fixnes | mesen | nestopia | quicknes | rustynes |
| --- | --- | --- | --- | --- | --- | --- |
| MMC1 SXROM 32 KiB (Dezaemon) | 32768 | **8192** | 32768 | **0** | 8192 | 32768 |
| Namco 163, internal 128 B only (Hydlide 3) | 8192 | 262144 | **0** | **0** | 8192 | 8192 |
| Taito X1-017 (SD Keiji Blader) | 8192 | 8192 | 8192 | **0** | 8192 | 8192 |
| Bandai 24C01 (Magical Taruruuto-kun 2) | 128 | load fails (rc 1) | 128 + `.eeprom128` | **0** | 8192 | 128 |

So for the N163-internal-RAM games no core offers a 128-byte save: Mesen and Nestopia report none
and the others report an 8 KiB (or larger) WRAM the board does not have. Nestopia's 0 for SXROM and
X1-017 means RetroArch would write no `.srm` at all for a Dezaemon or SD Keiji save in Nestopia.

- **Dezaemon (SXROM).** Battery RAM stayed zero after painting attempts in the player editor. Its
  COMMAND panel has LOAD/SAVE icons worked by a blinking, accelerating pointer, and placing it was
  not worked out in the timebox.
- **Magical Taruruuto-kun 2 (24C01).** A file is named and started, but the EEPROM stays blank: the
  game is an action board game that saves at some later point.
- **SD Keiji Blader (X1-017).** A new file is named and play reaches police HQ, but no save point was
  found there (the doctor heals, the commander repeats his order); CONTINUE still lists three empty
  files.
- **Kyuukyoku Harikiri Stadium III (X1-017).** Changing a setting changed one byte of the 8 KiB; the
  team editor (さくせい) opens a 30000-point roster screen, and no save was reached in the timebox.
- **Hydlide 3 (N163 internal).** Its menu has no save; the 8 KiB fceumm exposes stays zero.
- **Famista '90 (N163 internal).** Only the attract loop was seen.
