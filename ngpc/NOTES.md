# Neo Geo Pocket Color: notes

Ten games, two runnable cores, all 20 (game, core) pairs filed. The file formats and the two
cores' behaviour are described in `ngp/NOTES.md`; that part applies here unchanged:
- Beetle writes a `.flash` page list.
- RACE writes a `.ngf` of whole sectors.
- Beetle's flash erase is a no-op.
- Neither keeps a clock file.

This file has the NGPC games and what they add. The main addition is RACE's 64 KiB blocks,
which break Beetle and can crash it.

Buttons, for both cores: NGP A is libretro `b`, NGP B is libretro `a`, and Option is `start`.

## The ten games

Most NGPC games save only settings, records and play time to flash, so most scripts change a
setting, leave the menu (which rewrites the save sector), reset, and show the setting read back.
Neo Cherry Master Color is the one game with named save slots.

The choice aims at variety in cart size, which decides the flash layout:
- 4 Mbit, 8 Mbit and 16 Mbit carts;
- two 32 Mbit two-chip carts;
- saves in the small boot sectors, in a 32 KiB boot block, and in whole 64 KiB main sectors.

| Game (No-Intro) | Cart | Save area (RACE block list) | Script | Proof |
| --- | --- | --- | --- | --- |
| King of Fighters R-2 - Pocket Fighting Series (World) (En,Ja) | 16 Mbit | 0x3F8000 + 0x3FA000, 8 KiB each | SET UP, LEVEL -> HARD, EXIT | after a reset, SET UP shows LEVEL HARD |
| SNK vs. Capcom - The Match of the Millennium (World) (En,Ja) | **32 Mbit**, two chips | 0x3F8000 + 0x3FA000 (first chip; nothing written to the second) | SET UP, LEVEL -> HARD, EXIT | after a reset, LEVEL HARD |
| Metal Slug - 1st Mission (World) (En,Ja) | 16 Mbit | **0x3E0000, a whole 64 KiB sector** | SET UP, LEVEL -> HARD, EXIT | after a reset, LEVEL HARD |
| Neo Turf Masters (World) (En,Ja) | 16 Mbit | **0x3E0000, 64 KiB** | GAME OPTIONS > GAME LEVEL, NORMAL -> HARD | after a reset, GAME LEVEL HARD |
| Samurai Shodown! 2 - Pocket Fighting Series (World) (En,Ja) | 16 Mbit | 0x3F0000, 32 KiB (block 31, the one block Beetle can erase) | GAME OPTION, CPU LEVEL -> HARD, EXIT, SAVE? YES | after a reset, CPU LEVEL HARD and PLAYTIME 00-00-21 |
| Baseball Stars Color - Pocket Sports Series (World) (En,Ja) | 8 Mbit | 0x2F0000 32 KiB + 0x2F8000/0x2FA000 8 KiB, alternating | GAME OPTION, INNING and CALLED changed, EXIT (2P PLAY is skipped without a link cable, so one down reaches GAME OPTION) | RACE: 1 INNING / CALLED OFF kept. **Beetle: defaults**, the same stale-sector bug as mono Baseball Stars (provenance note) |
| Neo Cherry Master Color - Pocket Casino Series (World) (En,Ja) | 8 Mbit | 0x2F8000 + 0x2FA000 | ORIGINAL MODE, NEW GAME, name "AAA" (filed to slot 1, "COMPLETED"), notes in, POWER OFF, SAVE? YES | after a reset, CHOOSE FROM DATAS lists "AAA--- 100" |
| Bust-A-Move Pocket (USA) | 8 Mbit | **0x260000 + 0x270000, two 64 KiB sectors** | GAME OPTIONS, GAME-LEVEL LV 1 -> LV 2, EXIT | after a reset, LV 2 |
| Magical Drop Pocket (USA, Europe) | 8 Mbit | 0x2F0000, 32 KiB | OPTIONS, Total Games 3 -> 5, Exit | after a reset, Total Games 5 |
| Pocket Tennis Color - Pocket Sports Series (World) (En,Ja) | 4 Mbit | 0x27A000, 8 KiB | TOURNAMENT, NEW GAME, ALICE, the first match lost by serving with B over and over | TOURNAMENT -> CONTINUE (player select). Weak proof: the save is 3 to 6 bytes of tournament state at 0x27A008, which the game sets up on first boot and changes after the match |

Tried and dropped:
- **SNK vs. Capcom - Card Fighters' Clash - SNK Version:** naming SHIN writes only a 16-byte BCD
  time stamp at 0x3FA0B0. The real save comes after the tutorial card battle, which was out of
  reach.
- **Sonic The Hedgehog - Pocket Adventure:** it sets up its save on boot. Clearing Act 1 by
  holding right and spin-dashing got stuck in a loop section.
- **Metal Slug - 2nd Mission** (32 Mbit): the title menu is START / CONTINUE / OFFICE, and
  CONTINUE needs a cleared mission.
- **Faselei!, Biomotor Unitron, Dark Arms:** all have name entry, then long story openings, and
  none had written flash by the time the game proper began.
- **Puzzle Link:** formats 96 KiB at boot. Its OPTION menu holds only rankings and cards.

## Games x cores

20 of 20 filed. Every proof.png was checked by eye.

| Game | beetle-neopop `.flash` | race `.ngf` | RACE file loaded in Beetle | Beetle file loaded in RACE |
| --- | --- | --- | --- | --- |
| King of Fighters R-2 | 2600 B, 4 page runs | 16408 B (2 x 8 KiB) | works | works |
| SvC Match of the Millennium | 3112 B | 16408 B | works | works |
| Metal Slug 1st Mission | 272 B (one page) | 65552 B (one 64 KiB block) | **save silently lost** (LEVEL NORMAL) | works |
| Neo Turf Masters | 1560 B | 65552 B (one 64 KiB block) | **save silently lost** (NORMAL) | works |
| Samurai Shodown! 2 | 784 B | 32784 B | works | works |
| Baseball Stars Color | 7208 B (stale sector, see note) | 49184 B | works (options come back) | defaults (Beetle's stale data) |
| Neo Cherry Master Color | 14880 B | 16408 B | works (AAA 100) | works |
| Bust-A-Move Pocket | 7192 B | 131096 B (two 64 KiB blocks) | **Beetle segfaults** (retro-run exit 139) | works |
| Magical Drop Pocket | 272 B | 32784 B | works | works |
| Pocket Tennis Color | 272 B | 8208 B | not checked (no read-back screen) | not checked |

| Core | Status |
| --- | --- |
| jotego-jtngpc (openFPGA) | not runnable. Its Pocket build saves no cartridge flash (see Downloaded) |
| mednafen (standalone) | not runnable. Same block-list format as Beetle; nothing attributable found |

Builds: Beetle NeoPop v1.29.0.0 a50d5ac, RACE v2.16 c7810dd, default options, no BIOS.

## The 64 KiB block problem

RACE stores whole flash sectors. On these 8 and 16 Mbit chips the main sectors are 64 KiB, so a
game that saves outside the boot block gets a block with length 0x10000. Three of the ten do:
Metal Slug 1st Mission, Neo Turf Masters and Bust-A-Move Pocket. Tsunagete Pon (mono) and Puzzle
Link do too.

Beetle's block header has a u16 length (`FlashFileBlockHeader`, mednafen/ngp/flash.c:47-53),
read straight from the file with no check (`do_flash_read`, flash.c:116-150):
- **One such block** (Metal Slug, Neo Turf Masters): Beetle reads the length as 0, copies
  nothing, and the game boots with its defaults. Nothing is reported.
- **Two such blocks** (Bust-A-Move): after a length-0 block, Beetle takes the 64 KiB of data as
  the next block header. The bogus address and length it reads there make it crash.

Beetle's own files never hit this: it records 256-byte pages, and only `flash_optimise_blocks`
merging more than 64 KiB of contiguous pages could overflow the same u16. None of the ten does.
For one-saves, a RACE -> Beetle conversion must split blocks at 0xFFFF bytes or trim the 0xFF
tails.

## How the two files compare

Trimmed to Beetle's ranges, with missing bytes counted as 0xFF:
- **Identical:** KOF R-2, Bust-A-Move, Magical Drop, Neo Turf Masters.
- **A few bytes apart:** Neo Cherry Master Color (20), Pocket Tennis Color (3). These are clock
  stamps and RNG; each run reads the host clock.
- **SvC (48) and Metal Slug (55):** small game-state differences.
- **Samurai Shodown! 2 (89):** the PLAYTIME counter and its checksums.
- **Baseball Stars Color (325):** Beetle's stale sector.

Beetle's files are 272 B to 15 KiB. RACE's are 8 KiB to 128 KiB, mostly 0xFF.

## Downloaded entries and leads

Nothing filed for ngpc.
- **jotego-jtngpc (openFPGA):** the Pocket build's `.sav` is a 12356-byte RAM/ports/RTC dump, not
  flash (jtcores @4e225b7b macros.def:31-36, mem.yaml:57-75; issue #1487 says in-game saves are
  MiSTer-only).
- **Lead:** `.cache/downloads/ngpc/jtcores-ngp-ver-saves/` holds `Dark Arms - Beast Buster 1999
  (JUE) [!].sav` (768 B) and `Metal Slug - 1st Mission (JUE).sav` (512 B). They are test fixtures
  from jtcores PR #1346, the MiSTer jtngp build, now removed: a 256-byte header with the max/min
  page as LE u16, then the pages (jtngp_flash.v:168-229). Not filed, because the registry has no
  MiSTer jtngp core and the fixtures are not the openFPGA core's output. Still useful: the Metal
  Slug file is a third, page-range format for the save that sits at 0x3E0000 in the entries
  above.
- **mednafen:** `.flash`, the same block list as Beetle (ngp/flash.cpp:35-58, 257-306).
- Searched without result: jtcores NGP issues, beetle-ngp issues, Reddit/freeplaytech,
  archive.org.
