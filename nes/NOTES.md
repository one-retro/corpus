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
- **mednafen** (standalone), **bnes** and **emux-nes** (libretro, no macOS build): nothing found.

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
  d-pad, not A/Start, and the title timing differed between cores.
- **SD Gundam Gaiden, Magical Taruruuto-kun, DBZ Kyoushuu (24C01) and Minelvaton Saga, Kyonshiizu 2
  (X1-005).** No save was reached in about 3000 frames of play, or the name entry would not close.
  The X1-005 and 24C01 boards are still uncovered.
