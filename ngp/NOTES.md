# Neo Geo Pocket: notes

The library has only nine NGP (monochrome) games. Five of them were scripted to a genuine save
and filed for both runnable cores: 10 entries out of 10 attempted. The other four are listed
below with the reason. The NGPC set (`ngpc/NOTES.md`) uses the same two cores and the same file
formats. That file has the 64 KiB block problem, which no mono game here triggers.

## How NGP saves work

A Neo Geo Pocket cartridge has no battery RAM. Games save by reprogramming sectors of their own
flash ROM through BIOS calls: `VECT_FLASHWRITE` writes 256-byte pages and `VECT_FLASHERS` erases a
block. Neither emulator stores the whole flash. Each writes a NeoPop-style block list of the regions
the game touched:

```
u16 0x0053   u16 block_count   u32 total_file_length (header included)
then block_count times:  u32 CPU address (0x200000.. chip 0, 0x800000.. chip 1)   length   data
```

The length field is where the two cores differ (see below). The BIOS is not needed: both cores
emulate it at a high level and boot straight into the game, with no language or clock setup
screen. The language comes from a core option (`ngp_language` / `race_language`, both English by
default). The console clock is read from the host, so Neo Cherry Master shows DATE 1103 and
TIME 2345 at the moment it was played. Neither core writes a `.rtc` or any other clock file.

Buttons, for both cores: NGP A is libretro `b`, NGP B is libretro `a`, and Option is `start`.
Every script says so at the top.

## The games

| Game (No-Intro) | Cart | Where it saves | Script reaches | Proof |
| --- | --- | --- | --- | --- |
| King of Fighters R-1 - Pocket Fighting Series (Japan, Europe) (En,Ja) | 16 Mbit | the two 8 KiB boot sectors 0x3F8000/0x3FA000 | SET UP, LEVEL -> HARD, EXIT (writes the settings and the empty RECORD table) | after a reset, SET UP shows LEVEL HARD |
| Baseball Stars - Pocket Sports Series (Japan, Europe) (En,Ja) | 8 Mbit | 0x2F0000 (32 KiB boot block) plus two 8 KiB sectors 0x2F8000/0x2FA000, which it alternates between | GAME OPTION, INNING and CALLED changed, EXIT | after a reset, GAME OPTION shows 1 INNING / CALLED OFF (RACE). Beetle shows the defaults: see "Beetle's erase" |
| Neo Cherry Master - Real Casino Series (Japan) (En,Ja) | 8 Mbit | 0x2F8000/0x2FA000 | SIMPLE MODE, NEW GAME, four notes in, menu EXIT, SAVE? YES, SAVED | after a reset, CONTINUE brings back CREDIT 100 |
| Pocket Tennis - Pocket Sports Series (Japan, Europe) (En,Ja) | 4 Mbit | one 8 KiB sector 0x27A000 ("CUPSDATA") | a TOURNAMENT match, lost by serving with B over and over. The game writes its cup record when the match is lost | the RECORD trophy shelf (empty; no cup was won). Weak proof: the save is the record block the game creates after its first tournament, not a visible change |
| Shougi no Tatsujin (Japan) | 4 Mbit | one 8 KiB sector 0x278000 (the board) | 本将棋, 初心者, one pawn move, the computer answers, Option -> セーブ／ロード, A saves | after a reset and a new game, Option -> ロード -> A brings the position back |

Not filed (the rest of the library):
- **Samurai Shodown! (Japan, Europe):** GAME OPTION changes are not written to flash (an 8-byte
  RACE file, then defaults after a reset). Losing a 1P fight writes nothing either.
- **NeoGeo Cup '98 (Japan, Europe):** nothing was written to flash within a few minutes of the
  story mode. Not pursued.
- **Renketsu Puzzle Tsunagete Pon! (Japan):** it formats 96 KiB (0x260000 64 KiB + 0x270000
  32 KiB) on first boot. A game played to game over with no score writes nothing new; the
  rankings need a real score.
- **Melon-chan no Seichou Nikki (Japan):** a raising game with a clock. In Beetle, はじめから goes
  to the two name entries and the bedroom, but no flash write happened in 40,000 frames, and no
  save command was found. **RACE cannot start a new game at all.** After はじめから it shows a
  plain grey screen and never reaches the name entry; it was waited out to 2,000 frames, and
  Option turns the screen black. That is a RACE bug worth knowing about. The scripts in
  `work/ngp/melon*.txt` show the path.

## Games x cores

10 of 10 filed. Every proof.png was checked by eye.

| Game | beetle-neopop | race |
| --- | --- | --- |
| King of Fighters R-1 | filed, 536 B `.flash` | filed, 16408 B `.ngf` |
| Baseball Stars | filed, 7208 B, **the game reads back its old options** (provenance note) | filed, 49184 B |
| Neo Cherry Master | filed, 14880 B | filed, 16408 B |
| Pocket Tennis | filed, 272 B | filed, 8208 B |
| Shougi no Tatsujin | filed, 272 B | filed, 8208 B |
| Melon-chan no Seichou Nikki | not filed (no save found) | not filed: **hangs on a grey screen at New Game** |

| Core | Status |
| --- | --- |
| jotego-jtngp (openFPGA) | not runnable. Nothing exists to download: the Analogue Pocket build does not save cartridge flash at all (see Downloaded) |
| mednafen (standalone) | not runnable (GUI). No attributable files found. Same format as Beetle (see below) |

Builds: Beetle NeoPop v1.29.0.0 a50d5ac (`mednafen_ngp_libretro.dylib`), RACE v2.16 c7810dd
(`race_libretro.dylib`). Default core options, no BIOS.

## What each core writes

| | beetle-neopop | race |
| --- | --- | --- |
| File name | `<ROM stem>.flash`, written by the core into the save dir (`MDFN_MakeFName(MDFNMKF_SAV, "flash")`, mednafen/ngp/system.c:22,40) | `<ROM stem>.ngf` (flash.c `setupNGFfilename`) |
| `RETRO_MEMORY_SAVE_RAM` | 0, so no `.srm` | 0, so no `.srm` |
| When written | only at unload (`rom_unload` -> `flash_commit`, rom.c:87) | at unload, and also mid-run when a game driving the chip directly sends the reset command 0xF0 (flash.c:527,548,647) |
| A game that never writes | **no file** | **an 8-byte file with 0 blocks** (`53 00 00 00 08 00 00 00`): `flashShutdown` always writes. KOF R-1, Samurai Shodown, NeoGeo Cup '98, Pocket Tennis, Shougi and Melon-chan all leave one after a boot. make-save counts it as a real file, so be careful when filing RACE runs. |
| Block granularity | the 256-byte pages the game wrote (`flash_write(addr, n*256)`), merged when adjacent (`flash_optimise_blocks`). Most mono files are a few hundred bytes | **whole flash sectors**: 64 KiB main blocks, or the boot-block pieces 32 KiB / 8 KiB / 8 KiB / 16 KiB (flash.c `blockSize`) |
| Block header | `u32 address, u16 length, 2 bytes struct padding` (`FlashFileBlockHeader`, flash.c:47-53). The padding was 0 in every filed file | `u32 address, u32 length` (`blockStruct`, flash.c:63-67) |
| Flash semantics | a write is a plain store, and **erase is a no-op** except for block 31 of a 2 MiB cart (biosHLE.c:229-251, `VECT_FLASHERS`) | erase sets 0xFF and a write ANDs, as real flash does (flash.c `flashWriteByte`) |
| Second chip (32 Mbit carts) | addresses 0x800000+ | addresses 0x800000+ (`blockNumToAddr(1,i)+0x600000`) |

Byte for byte, the files agree wherever both cores define the address and the core works
(trimmed to Beetle's ranges, missing bytes counted as 0xFF). KOF R-1 differs in 8 bytes, Neo
Cherry Master in 20, Pocket Tennis and Shougi in 5. Those are clock stamps and RNG, since each
run reads the host clock. Baseball Stars differs in 306 bytes: Beetle's stale sector (next
section).

### Beetle's erase (Baseball Stars)

Baseball Stars keeps two copies of its options in the 8 KiB sectors 0x2F8000 and 0x2FA000. To
save, it writes the new copy to one sector and erases the other. Beetle's HLE `VECT_FLASHERS`
does nothing for this cart, so the boot-time copy at 0x2F8000 stays valid. After a reset, the game
reads that old copy:
- Beetle's proof shows EXTRA INNINGS / CALLED ON, the defaults.
- RACE's shows 1 INNING / CALLED OFF.

Beetle's file reproduces this: 0x2F8000 still holds the old data, where RACE's has 0xFF.

Loading the files into the other core (renamed):

| File | loaded into | Result |
| --- | --- | --- |
| RACE's `.ngf` | Beetle | the options come back correctly |
| Beetle's `.flash` | RACE | the defaults, because the stale sector is in the file |

So the bug lives in Beetle's emulation, not its file format. The Beetle entry is filed anyway,
since it is what Beetle really writes, with a provenance note. The same happens in Baseball
Stars Color (ngpc).

### Can the two cores read each other's files?

Every pair here was loaded into the other core with the file renamed (`.flash` <-> `.ngf`), and
the proof screen was checked again (`work/tools/cross.sh`, `crossall.sh`).
- **Beetle `.flash` -> RACE:** always works. Beetle's 8-byte block header with zero padding is a
  valid RACE header, because the u16 length plus the zero padding equals the u32.
- **RACE `.ngf` -> Beetle:** works for all five mono games. Every block here is 32 KiB or smaller,
  so the u32 length fits Beetle's u16.

A RACE block of exactly 64 KiB does not fit. Beetle reads its length as 0, and the save is
silently lost, or with two such blocks **Beetle segfaults**. No mono game here saves into a
64 KiB sector, but three NGPC games do; see `ngpc/NOTES.md`.

For one-saves:
- Convert RACE to Beetle by splitting blocks over 0xFFFF bytes, or trimming them.
- Convert Beetle to RACE by renaming.
- To get a flash image for a whole-image consumer such as jtngp on MiSTer, apply the blocks over
  0xFF.

## Downloaded entries and leads

Nothing filed for ngp.
- **jotego-jtngp (openFPGA):** the Analogue Pocket build saves no cartridge flash. Its `.sav` is
  a 12356-byte dump: 12 KiB CPU RAM, 64 B ports and 4 B RTC (jtcores @4e225b7b
  macros.def:31-36, mem.yaml:57-75, jtngp_game.v:25). jtcores issue #1487 confirms in-game saves
  are MiSTer-only. So an openFPGA "save" for NGP is not a game save at all, and has no relation
  to the files above.
- **jtngp on MiSTer** (PR #1346, since removed from the core): a 256-byte header holding the
  max and min 256-byte page numbers as LE u16, then those flash pages (jtngp_flash.v:168-229).
  Two test fixtures from that PR are kept as leads in
  `.cache/downloads/ngpc/jtcores-ngp-ver-saves/`: Dark Arms 768 B and Metal Slug 1st Mission
  512 B. Both are NGPC games and come from the MiSTer build, not the openFPGA core the registry
  slug names.
- **mednafen (standalone):** `ngp/flash.cpp` writes the same block list as Beetle (id 0x0053, u32
  address, u16 length; flash.cpp:35-58, 257-306), named `<stem>.<md5>.flash`. No downloadable
  file could be attributed.
- Searched with nothing found: jtcores NGP issues (#825, #1487, #788 and others), beetle-ngp
  issues, the freeplaytech and Reddit threads, archive.org.

## Scratch

`work/ngp/` holds the probe scripts (Melon-chan, Samurai Shodown, Tsunagete Pon, NeoGeo Cup).
`work/tools/ngf.py` parses a block list, `ngfcmp.py` compares two as memory images, and
`cross.sh`/`crossall.sh` boot one core's file in the other core. The core sources quoted are
libretro/beetle-ngp-libretro a50d5ac and libretro/RACE c7810dd.
