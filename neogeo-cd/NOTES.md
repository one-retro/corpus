# Neo Geo CD

Seven games played in NeoCD (2026-11-20), from the Redump set in
`/Volumes/Games/ROMS Library/snk-neo-geo-cd-redump-collection` (`.chd`). The copy of that set had
reached "Magical Drop 2" (55 discs, A to M) when this was done; the rest of the set has not been
tried.

| Entry | Data name on the card (BIOS list) | When the game writes |
| --- | --- | --- |
| 2020 Super Baseball (Japan) (En,Ja) | SUPER BASEBALL 1P | during play (two writes) |
| ADK World (Japan) | ADK-WORLD | asks to format the card, then saves as the town is played |
| Baseball Stars 2 (Japan) (En,Ja) | BASEBALL STARS 2 COM | "GAME DATA SAVE" during play |
| Baseball Stars Professional (Japan) (En,Ja) | BASEBALL STARS 1P VS | asks to format the card, then saves after the first innings |
| Big Tournament Golf ~ Neo Turf Masters (Japan) (En,Ja) | BIG TOURNAMENT GOLF | at boot |
| Galaxy Fight - Universal Warriors (Japan) (En,Ja,Es) | GALAXY FIGHT RANKING | at boot |
| League Bowling (Japan) (En,Ja) | BOWLING 1P | "GAME DATA SAVE: YES" after the first game |

## Scripts

`scripts/neogeo-cd/<game>.txt`. Neo Geo A is the RetroPad `b` (`a` is Neo Geo B; a first scan
pressing `a` reached no save in any game). Each script presses START, A, A in a fixed cycle that
goes through the title and menus into play. The number of cycles comes from a trace that dumped the
card after every cycle; it stops one cycle after the game's last write. Then it resets, and on the
BIOS CD player it opens MEMORY: the **backup memory utility** (1 format, 2 data name list, 3 erase,
4 user name, 5 exit). "2" lists the card's data names. That list is each proof.png.

The utility's cursor starts on 1 (format). An extra A there asks whether to erase a card that holds
data, so the scripts press A once to open the utility and move down before the next A.

## What NeoCD writes

NeoCD 2022 b1e04c7 (libretro buildbot, arm64), default options. BIOS from the owner's library in
`.cache/bios/neogeo-cd/neocd/` (`front-sp1.bin`, `neocd_*.rom`, `000-lo.lo`, ...). The front-loader
BIOS shows its CD player at boot.

- **Two identical files.** The frontend writes the 8 KiB backup RAM (`RETRO_MEMORY_SAVE_RAM`) as
  `<content stem>.srm`. The core also keeps the card itself in `<system>/neocd/neocd.srm`
  (`neocd_per_content_saves` off, the default), and loads it at start. In all seven entries the two
  files are byte-identical. Both are filed: the second under `system/neocd/` (`--keep-sysdir`).
- **One card for every game.** With the default option `neocd.srm` is shared, so a user's real
  file holds every game's data. Each entry here started from no card, so each holds one game.
- **An unused card is all zeros**, not formatted. Booting the BIOS and playing games that never
  save leaves it at zeros. A game that saves formats it first (ADK World and Baseball Stars
  Professional ask, "このバックアップメモリーはフォーマットされていません"; the others do it
  silently). The BIOS utility's "1" formats it too: a formatted, empty card has 7866 non-zero bytes.
- **Layout seen in the files.** A header with `NEO-GEO` at 0x20 (in the even bytes; the odd bytes
  hold a table of pointers 0x40, 0x44, ...), a block table from 0x40, and the first data name at
  0x340 in plain ASCII, padded with spaces to 20 bytes ("BOWLING 1P"). one-saves' two reference
  files (Metal Slug, Garou Densetsu 2) have the same header, and both hold "METAL SLUG" at 0x340:
  the shared card again.

## Games that saved nothing

With the A mapping fixed and a formatted card, the same START/A/A cycle (60 cycles, about 15000
frames) left the card unchanged in the other discs of the copy: all KOF ('94 to '99, '96 NeoGeo
Collection), Fatal Fury 1/2/3/Special, Art of Fighting 3, Last Blade 1 and 2, Savage Reign,
Windjammers, Crossed Swords I and II, Far East of Eden, Joy Joy Kid, and the rest. King of Fighters
'95 and Art of Fighting 3 were also tried changing their options: no write. Some of these may save
deeper in play (a ranking after a high score, an unlock); not pursued. Double Dragon (Export)
crashed NeoCD (segfault); Magical Drop 2 may have been a partial copy.

## Cores

| Core | Status |
| --- | --- |
| neocd | 7 played |
| neogeo-mister | not runnable here; nothing found online (searches of 2026-11-04: MiSTer-devel/NeoGeo_MiSTer issues, libretro/neocd_libretro, web) |

From source, unverified here: the MiSTer core writes CD games the same 73728-byte `.sav` as
cartridges, 64 KiB of unused backup RAM and then the 8 KiB card with every 16-bit word
byte-swapped, one save per CD since July 2023 (issue #192). Geolith 0.5.0 also runs Neo Geo CD and
writes `<stem>.brm` (8 KiB), but the registry does not list it for neogeo-cd.

## Harness change

`tools/make-save.py` linked each entry of `.cache/bios/<system>/` into the system directory as is,
so the `neocd/` folder was a link to the cache and NeoCD wrote `neocd.srm` into the cache, where it
would carry into the next run. A directory is now recreated in each run with its files linked one
by one; what the core writes stays in the run. (The stray file was all zeros and was removed.)
