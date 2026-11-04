# Genesis / Mega Drive

Ten games, played from power-on in every runnable core: Genesis Plus GX (v1.7.4 f27655b), Genesis
Plus GX Wide (v1.7.4 b7ad005), PicoDrive (2.05-1890c29), clownmdemu (v1.6.12 d43c270) and BlastEm
(1.0.1-pre). 45 entries filed out of 50 attempts; the 5 misses are core findings, below.

## The games

| Game | Save hardware (cart header at 0x1B0) | Why |
| ---- | ---- | ---- |
| Sonic The Hedgehog 3 (USA) | FRAM, byte-wide on odd addresses, `RA F8 20` 200001-2003FF (512 bytes) | the one FRAM cart; Data Select slot 1, proof after reset |
| Sonic & Knuckles + Sonic The Hedgehog 3 (USA) (Lock-on Combination) | the same FRAM, reached through S&K's lock-on (S&K's header has no `RA`) | same game, but cores size it from a different header |
| Phantasy Star IV (USA) | SRAM, odd, `RA F8 20` 200001-203FFF (8 KB) | popular RPG; Start -> SYS -> SAVE at first control |
| Shining Force (USA) | SRAM, odd, 200001-203FFF (8 KB) | popular; new adventure 1 named "A", Ch.1 after reset |
| World Series Baseball '95 (USA) | SRAM, odd, `RA F8 20` 200001-20FFFF (32 KB, the largest declared range) | big save; NEW LEAGUE, CONTINUE LEAGUE after reset |
| Might and Magic - Gates to Another World (USA, Europe) | SRAM, odd, **no `RA` header** (BlastEm's rom.db: 32 KB) | headerless SRAM; Create Character "A", listed in the inn |
| Jack Nicklaus' Power Challenge Golf (USA, Europe) | SRAM, odd, header `RA F8 40` 200001-2007FF (1 KB): the 0x40 bit EEPROM carts use | odd header; Create Club Member "AB" |
| Evander Holyfield's 'Real Deal' Boxing (World) | Sega serial EEPROM 24C01, 128 bytes, `RA E8 40` | EEPROM (Sega wiring); career boxer "ABC", RESUME OLD CAREER after reset |
| NBA Jam (USA, Europe) (Rev 1) | Acclaim serial EEPROM 24C02, 256 bytes | EEPROM (Acclaim wiring); initials record after a full CPU game |
| NHLPA Hockey 93 (USA, Europe) (EA Sports) | EA serial EEPROM X24C01, 128 bytes | EEPROM (EA wiring); first playoff game played out |

No 16-bit (word-wide) SRAM title exists in the library: a scan of the `RA` headers of all 933
Genesis ROMs (`work/genesis/scan_headers.py`) found 201 carts declaring backup RAM, with type bytes
`F8 20` (odd-byte SRAM, 157), `E8 40` (serial EEPROM, 38) and `F8 40` (6, Accolade/EA sports games),
and no `E0`/`F0` (both bytes, or even bytes). The only start address on an even byte is Rent a Hero's
(200000-203FFF, still typed `F8`). So the corpus has byte-wide SRAM on odd addresses, FRAM, three
EEPROM wirings, and nothing word-wide.

Swapped out after a few attempts: Wonder Boy in Monster World (no save point found in the timebox),
Mega Man - The Wily Wars (the EEPROM is only formatted, "CAPCOM" at 0x2C, at first boot; a real save
needs a stage cleared), College Slam (24C65, 8 KB; its menus ignored our input in Genesis Plus GX).

## Games x cores

| Game | GPGX | GPGX Wide | PicoDrive | clownmdemu | BlastEm |
| ---- | ---- | ---- | ---- | ---- | ---- |
| Sonic 3 | 604 | 604 | 1024 | 65536 | 512 |
| S&K + Sonic 3 | 980 | 980 | **16384** | 65536 | 512 |
| Phantasy Star IV | 16384 | 16384 | 16384 | 65536 | 8192 |
| Shining Force | **16382** | 16382 | 16384 | 65536 | 8192 |
| WSB '95 | 63804 | 63804 | 65536 | 65536 | 32768 |
| Might and Magic | 16384 | 16384 | 16384 | failed: no SRAM for a headerless cart | 32768 |
| Jack Nicklaus | 3996 | 3996 | failed: no file | 65536 | 1024 |
| Evander Holyfield | 128 | 128 | 8192 | failed: no EEPROM | 128 |
| NBA Jam | 256 | 256 | 8192 | failed: no EEPROM | 256 |
| NHLPA 93 | 128 | 128 | 8192 | failed: no EEPROM | 128 |

Sizes in bytes, every file `<ROM stem>.srm`. BlastEm runs the `<title>.blastem.txt` variants (see
Scripts). Not runnable here: drizzt-megadrive, ericlewis-genesis, spiritualized-genesis (openFPGA),
megadrive-mister (MiSTer), mednafen (standalone): see Downloaded.

## How each core lays out the same save

The key finding: four layouts and four fill rules for one cartridge.

- **Genesis Plus GX (and Wide): byte-expanded, 0xFF-filled, trimmed.** It keeps a 64 KB image of
  0x200000-0x20FFFF, so an odd-byte SRAM byte sits at the odd offset and every even byte is 0xFF.
  Backup RAM starts as 0xFF. On save the libretro port reports the size up to the last byte that is
  not 0xFF (`retro_get_memory_size`, libretro.c), so the file length depends on the data: Sonic 3 is
  604 bytes, S3&K 980, WSB '95 63804, and Shining Force 16382, two bytes short of its 16 KB window
  because the game left 0xFF at the end. A tool that reads the declared size will find these short;
  GPGX itself reads back up to 64 KB and pads with 0xFF. EEPROMs go through the same buffer: 128 or
  256 bytes, unexpanded (and would be trimmed too if they ended in 0xFF).
- **PicoDrive: byte-expanded, 0x00-filled, the header's range.** Size = header end - start + 1 with
  start rounded down and end up to a word (1024 for Sonic 3, 16384 for 8 KB carts, 65536 for WSB
  '95). With no `RA` header it assumes 0x200000-0x203FFF, so the S&K lock-on gets 16384 bytes where
  Sonic 3 alone gets 1024. Every EEPROM is an 8192-byte file (`Pico.sv.size = 0x2000`, cart.c) with
  the chip's 128/256 bytes first and zeros after. It writes no file at all while the buffer is all
  zeros (libretro.c).
- **clownmdemu: byte-expanded, 0x00-filled, always 65536 bytes.** It has no serial EEPROM: Evander,
  NBA Jam and NHLPA 93 ran but their files were all zeros (not filed); NBA Jam hangs at team select
  and NHLPA 93 never leaves the FINAL board, and Evander's career is gone after a reset. It maps no
  SRAM for Might and Magic (no header): the inn's roster comes up empty and the file stays zero.
- **BlastEm: packed (odd bytes only), 0x00-filled, the cart's real size.** 512 bytes for Sonic 3 and
  the lock-on, 8192 for 8 KB carts, 32768 for WSB '95 and for Might and Magic (its rom.db entry; the
  game itself uses only the first 8 KB), 1024 for Jack Nicklaus. EEPROMs are the chip's bytes, 0xFF
  where unwritten, byte-identical to GPGX's for Evander and NBA Jam. Same layout as MiSTer's (below).

The data agree once the layout is undone: Phantasy Star IV's odd bytes are identical in all five
cores; NBA Jam's 256 EEPROM bytes are identical in GPGX, GPGX Wide, BlastEm and PicoDrive's first
256. Where they differ, it is the fill showing through: Sonic 3's 30 different bytes are all 0xFF in
GPGX against 0x00 elsewhere (bytes the game never writes), and Evander's PicoDrive EEPROM differs in
6 bytes (unwritten 0x00 instead of 0xFF, and so a different checksum). Shining Force, WSB '95 and
NHLPA 93 also differ in game data (random draws, CPU opponents, and the hockey game's result), not
just layout.

Other surprises:

- **PicoDrive and the `F8 40` header.** PicoDrive treats bit 0x40 of header byte 0x1B3 as "this is
  an EEPROM" (cart.c). Jack Nicklaus' Power Challenge Golf declares `RA F8 40` but has plain SRAM
  (GPGX, BlastEm and clownmdemu all show the member "AB" at the odd bytes), so in PicoDrive its
  writes go nowhere and no `.srm` is written: the club member is lost. The other five `F8 40` carts
  (Barkley 2, Brett Hull Hockey 95, Pele!, Pele II, Unnecessary Roughness '95) are worth a look.
- **BlastEm's button map.** Its libretro port maps the RetroPad b=A a=B r=C y=X x=Y l=Z (libblastem.c),
  where GPGX, PicoDrive and clownmdemu use y=A b=B a=C l=X x=Y r=Z. Any script that presses a face
  button needs a BlastEm variant; `work/genesis/blastemize.py` writes them.
- **BlastEm appears to run NBA Jam (header region "UE") as a 50 Hz console**: the CPU game reaches
  its final stats after about 96 rounds of 306 frames instead of about 117 in GPGX (5/6 of the
  frames), so its variant plays 86 rounds of B, not 105. The other carts needed no timing change.
- Sonic 3, Phantasy Star IV, Might and Magic, WSB '95, NBA Jam ("Snake 1993" at 0x08) and NHLPA 93
  format their save RAM at first boot, as do Wily Wars ("CAPCOM" at 0x2C) and College Slam (4688
  bytes in GPGX). A boot-only file is not a save, so every script goes on to a real one.

## Scripts

`scripts/genesis/<game>.txt`, shared by GPGX, GPGX Wide, PicoDrive and clownmdemu, and
`<game>.blastem.txt` beside each one that presses A/B/C (generated from the shared script by
`work/genesis/blastemize.py`; NBA Jam's also has the shorter loop). Sonic 3, S&K + Sonic 3 and WSB
'95 press only Start and the D-pad and have no variant. NBA Jam and NHLPA 93 play whole CPU games
(about 40k and 70k frames); the other scripts are under 10k frames.

## Downloaded

- `megadrive-mister/Phantasy Star IV (USA)/`: `Phantasy_Star_IV_USA-from-mister-zero-padded.sav`,
  65536 bytes, from save-file-converter's test data (GPL-3.0), a file a user brought "from MiSTer"
  (issue #118, PR #127, May 2022). Packed like BlastEm's, "PHANTASY STAR 4" header at offset 2, then
  0x00 to 64 KB. The converter's notes say MiSTer normally pads Genesis saves to 64 KB with 0xFF and
  keeps EEPROM saves unexpanded; this one is 0x00-padded.
- Present but not added by me: `spiritualized-genesis/Sonic The Hedgehog 3 (USA)/` (131072 bytes,
  byte-expanded with 0xFF on every even byte and 0xFF past the data, like GPGX's image but untrimmed
  and twice the 64 KB window) and
  `ericlewis-genesis/Sonic The Hedgehog (USA, Europe)/` (65536 bytes of 0xFF; Sonic 1 has no save
  RAM), both `"method": "device-backup"` from an Analogue Pocket backup.

Leads, not filed: save-file-converter's other MiSTer Genesis files (`Wonder Boy in Monster World
mister.sav`, `phantasy-star-ii.18168-mister.sav`, `...-from-mega-sd.sav`, `...-from-retrode-to-
mister.sav`) are converter output, not MiSTer-written. MegaDrive_MiSTer issue #6 says EEPROM support
was added to that core (Genesis_MiSTer never had it) and lists the EEPROM titles; #27 notes it keys
Wily Wars' EEPROM on the product code T-12046. Nothing found for drizzt-megadrive or mednafen (MD
saves there are gzip-compressed by default, `filesys.disablesavegz`).

## Harness notes

- Genesis Plus GX save states do not carry SRAM/EEPROM: after `loadstate` the save RAM is whatever
  was loaded at start (0xFF), so Shining Force showed three garbage adventures and EEPROM games
  wrote nothing. Develop GPGX scripts from power-on, or use another core for states.
- `make-save.py` treats an all-zero file as blank, which is what caught clownmdemu's missing EEPROM.
