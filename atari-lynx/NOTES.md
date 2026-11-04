# Atari Lynx

No Lynx game released by Atari or its licensees (1989-1996) has save memory, and the library (the
No-Intro LYX set, 74 retail games, plus a GoodLynx 2.01 set) has no homebrew. The cartridge EEPROM
(93Cxx serial EEPROM, wired to the cart's AUDIN/strobe lines) is used by **aftermarket homebrew**,
so this system's entry is one freeware homebrew game, downloaded from its author's GitHub. 2 entries
filed out of 3 attempts.

## The game

| Game | Author, source, licence | What it saves |
| --- | --- | --- |
| 4Ttude (`4ttude.lnx`, LNX, 123916 bytes) | Nop90 (Gisberto Rondinella) with MARSS, 2019, for the Atari Lynx 30th Birthday Programming Competition. github.com/nop90-atari-lynx/4Ttude (`4ttude.lnx` in the repository). The bundled `4Ttude.txt`: "released as a freeware digital rom. The game can be freely distributed on the web ...; the distribution as a physical Atari Lynx homebrew cart is reserved" | three ranked save slots and the options, in a 93C46 (128 bytes). Script: Play vs CPU in slot 1 at CPU strength 0, win, and the slot's chart (Rank 0, Games 1) follows |

The LNX header's EEPROM byte (offset 0x3C) is 0x41: type 1 (93C46), bit 6 set ("save to SD" for a
LynxSD cart, where the game would use `/saves/4ttude.sav`), bit 7 clear (16-bit organisation). The
game formats a blank chip at boot ("TTTT" and the default options word 0x0007 at byte 6); a
ranked result is a real save: the record bytes `01 01 01 00` at 8-11 after one win. The
`provenance.json` files have `"rom_source"` with the download URL; the ROM stays in
`.cache/downloads/`.

## Games x cores

| Game | beetle-lynx | gearlynx | handy |
| --- | --- | --- | --- |
| 4Ttude | failed: runs and wins, no EEPROM, writes nothing | `4ttude.srm`, 128 | `4ttude.eeprom`, 128 |

Builds: Beetle Lynx v1.24.0 fcdefcf, Gearlynx 1.2.37-8-gd5c3b23, Handy 0.97 bc55d46, all with
`lynxboot.img` (md5 fcd403db..., from a Pocket's `Assets/lynx/common`). In beetle-lynx the chart
still reads Games 1, from work RAM; nothing survives.

## Where each core keeps the EEPROM

| Core | EEPROM | File | Size | Byte order |
| --- | --- | --- | --- | --- |
| handy | 93C46/56/66/76/86, 8- or 16-bit, type from the LNX header (`type & 7`, bit 7 = 8-bit) or its cart database | **`<savedir>/<content name>.eeprom`**, written by the core through the VFS on reset and at unload; no `.srm` | 128 here | host-order `uint16_t`: little-endian words |
| gearlynx | 93C46-93C86, 8-/16-bit, type from header, database, or the `gearlynx_eeprom_type` option | **`<stem>.srm`** via `RETRO_MEMORY_SAVE_RAM` | 128 here | host-order: little-endian words |
| beetle-lynx | none (no EEPROM code) | none | - | - |

**Handy's `4ttude.eeprom` and Gearlynx's `4ttude.srm` are byte-identical** (sha1 f7e3cade...): the
same 128 bytes under two names and extensions. Handy ignores header bit 6 (`type & 7`) and Gearlynx
also made a 93C46 of 0x41. A save moves between
them by renaming; a big-endian dump (a programmer reading the chip, or a MiSTer/BigPEmu style
file) would have every word swapped. Without an EEPROM type neither writes anything (California
Games, retail, gave save RAM 0 in all three cores).

Seen while choosing the script: 4Ttude's "Save and exit options menu" writes the options word as
0x0000 whatever the menu shows (Yes/Yes/Off or all on), and after a reset the menu reads No/No/Off,
identically in Handy and Gearlynx. So the script saves a ranked result instead.

## Cores not runnable here

| Core | Status |
| --- | --- |
| atarilynx-mister (MiSTer) | README "Missing features": no custom EEPROM ("not used in official games, only homebrew"); save states only. Nothing to find |
| budude2-lynx (openFPGA) | README documents no save support; nothing found |
| mednafen (standalone) | the same Lynx emulation as beetle-lynx: no EEPROM, nothing to find |

## Leads

- Handy's cart database flags these as `CART_EEPROM_93C46`, all aftermarket: 8-Bit Slicks, Alpine
  Games, A Bug's Trip Redux, MegaPak 1, Sky Raider Redux, "Unnamed", Vikings Saga (both), Wyvern
  Tales; it notes Eye of the Beholder's 16K NVRAM as not emulated. Most are boxed carts. Fadest's
  free "A Bug's Lynx" and the "A Bug's Trip Redux" demo (itch.io) say they save progress.
- Galaga by Shadester (GitHub, 2025-2026): high score in a 93C46, but no licence and Namco's name;
  not used. Odynexus demo (Ancient World, itch.io, pay what you want): EEPROM high scores; no stable
  download URL.
