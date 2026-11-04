# Genesis / Mega Drive

Thirteen games, played from power-on in every runnable core: Genesis Plus GX (v1.7.4 f27655b),
Genesis Plus GX Wide (v1.7.4 b7ad005), PicoDrive (2.05-1890c29), clownmdemu (v1.6.12 d43c270) and
BlastEm (1.0.1-pre). The first ten were the original pass (45 entries filed out of 50 attempts); a
second pass added three EEPROM types the corpus lacked (11 filed out of 15). 56 of 65 in all; the 9
misses are core findings, below.

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
| Frank Thomas Big Hurt Baseball (USA, Europe) | Acclaim serial EEPROM **24C65, 8 KB**, 16-bit word addresses; Acclaim's 32 Mbit board wiring (SCL and SDA on 0x200000/0x200001); header `RA E8 40` 200001-200001 | the largest EEPROM; Season with Baltimore, Resume after reset |
| NFL Quarterback Club 96 (USA, Europe) | Acclaim serial EEPROM **24C16, 2 KB** (device-address paging), same 32 Mbit wiring, same header | five season slots; COWBOYS 1996 saved to slot 1, listed by Resume Season |
| Micro Machines - Military (Europe) (J-Cart) | Codemasters serial EEPROM **24C08, 1 KB** on the J-Cart board (write lines at 0x300000, SDA read at 0x380001 bit 7); **no `RA` header** and a blank product code, found by checksum 0x168B and the "DNLD" stack pointer | the Codemasters wiring; driver Spider renamed "AB" |

No 16-bit (word-wide) SRAM title exists in the library: a scan of the `RA` headers of all 933
Genesis ROMs (`work/genesis/scan_headers.py`) found 201 carts declaring backup RAM, with type bytes
`F8 20` (odd-byte SRAM, 157), `E8 40` (serial EEPROM, 38) and `F8 40` (6, Accolade/EA sports games),
and no `E0`/`F0` (both bytes, or even bytes). The only start address on an even byte is Rent a Hero's
(200000-203FFF, still typed `F8`). So the corpus has byte-wide SRAM on odd addresses, FRAM, five
EEPROM wirings (Sega, EA, Acclaim's 16 and 32 Mbit boards, Codemasters' J-Cart) in five sizes
(X24C01 128 bytes, 24C02 256, 24C08 1 KB, 24C16 2 KB, 24C65 8 KB), and nothing word-wide.

Genesis Plus GX's database (`core/cart_hw/eeprom_i2c.c`) lists every EEPROM board by product code.
Types still missing here: 24C02 in device-address mode (NFL Quarterback Club) and 24C04 (NBA Jam
Tournament Edition), see below.

Swapped out after a few attempts: Wonder Boy in Monster World (no save point found in the timebox),
College Slam (24C65, 8 KB; its menus ignored our input in Genesis Plus GX; Frank Thomas took its
place as the 24C65).

Tried again in the second pass and still not filed:

- **Mega Man - The Wily Wars (Europe)** (X24C01, Sega wiring, product T-12046, `RA E8 40`
  200001-200001). The EEPROM is formatted at first boot ("CAPCOM" at 0x2C) and written again only
  when a stage is cleared; option mode (key config, sound test) saves nothing. Controls are B shoot,
  C jump, A weapon window. Cut Man's stage (Mega Man 1, file 1) was scripted from save states in
  Genesis Plus GX through the opening run of platforms and Bunby Helis, the pipe steps and the
  first Blaster shaft, about half the stage, before the timebox ran out. Blind play from
  screenshots costs several runs per screen, and the boss and five cores' timing were still to come.
  It is still the only Sega-wired EEPROM game besides Evander, so it would add a second file of the
  same type, not a new type.
- **NFL Quarterback Club (World)** (24C02 in device-address mode, the one board of that type). Like
  College Slam (same developer, same engine) it ignores 4-6 frame presses: its title only gives way
  to presses of about 30 frames, and then its main menu (QB Challenge / Play NFL / Simulation)
  moved its highlight but never took B, in Genesis Plus GX and PicoDrive, with a 3- or 6-button pad.
  A lead for both games: hold every button much longer.
- **NBA Jam - Tournament Edition (World)** (24C04, the one board of that type). It writes 16 bytes at
  boot; like NBA Jam it records initials only after a whole game, about 40k frames. Not attempted
  for time.

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
| Frank Thomas | 8192 | 8192 | 8192 | failed: never boots (blue and black stripes) | 8192 |
| NFL QB Club 96 | **253** | 253 | 8192 | failed: never boots (stripes) | 2048 |
| Micro Machines Military | **673** | 673 | 8192 | failed: no EEPROM (65536 zeros) | failed: 1024 bytes of 0xFF, nothing written |

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

The bigger EEPROMs of the second pass:

- **Frank Thomas (24C65): one file in four cores.** All four write 8192 bytes, byte-identical (sha1
  8b1b5972...). The game fills the whole chip at first boot (team names, schedules; only 2 of 8192
  bytes stay 0xFF), so neither GPGX's trimming nor PicoDrive's zero fill can show, and PicoDrive's
  fixed 8192-byte EEPROM file happens to be the chip's size. The season itself changes 16 bytes.
- **NFL Quarterback Club 96 (24C16): three sizes.** GPGX writes **253 bytes**, the 2 KB chip cut after
  its last byte that is not 0xFF; BlastEm writes the chip, 2048 bytes, 0xFF past the data; PicoDrive
  8192 bytes, 0x00 wherever the game never wrote (bytes 0-4 and 253-2047, then its own zero tail).
  Bytes 5-252 are the same in all three. So a 24C16 save can arrive as 253, 2048 or 8192 bytes.
- **Micro Machines - Military (24C08, J-Cart).** GPGX 673 bytes (trimmed), PicoDrive 8192, identical
  over the first 673. The game formats the chip at first boot: "hasreset", then `00 FF` pairs, then
  the drivers' six-letter names from 0x14C; the save rewrites Spider's, at 0x176, as "AB". BlastEm maps
  this cart's EEPROM in rom.db (by sha1, with a "TODO: J-Cart" note) but nothing reached the chip:
  its file is 1024 bytes of 0xFF and the run is not filed. In BlastEm and clownmdemu the proof screen
  still shows "AB" after the reset, because the game keeps the names in work RAM across a reset; the
  files show nothing was saved.
- **clownmdemu and the Acclaim 32 Mbit boards.** Frank Thomas and NFL QB Club 96 never get past a
  screen of blue and black vertical stripes (the files stay 65536 zeros). Genesis Plus GX shows the
  same stripes if NFL QB Club 96 is soft-reset after saving, so that script proves the save by
  backing out to Resume Season instead of resetting; Frank Thomas survives the reset.

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
  format their save RAM at first boot, as do Wily Wars ("CAPCOM" at 0x2C), College Slam (4688
  bytes in GPGX), Frank Thomas (team names), Micro Machines Military ("hasreset", names) and NBA Jam
  TE (16 bytes). A boot-only file is not a save, so every script goes on to a real one.

## Scripts

`scripts/genesis/<game>.txt`, shared by GPGX, GPGX Wide, PicoDrive and clownmdemu, and
`<game>.blastem.txt` beside each one that presses A/B/C (generated from the shared script by
`work/genesis/blastemize.py`; NBA Jam's also has the shorter loop). Sonic 3, S&K + Sonic 3 and WSB
'95 press only Start and the D-pad and have no variant. NBA Jam and NHLPA 93 play whole CPU games
(about 40k and 70k frames); the other scripts are under 10k frames. Second pass: `Frank Thomas Big
Hurt Baseball.txt`, `NFL Quarterback Club 96.txt` and `Micro Machines - Military.txt`, each with a
generated `.blastem.txt`. Development scripts for them, for Wily Wars (with `gen.py`, which expands
a compact input list with mashed fire) and for NFL Quarterback Club are in `work/genesis/eep/`.

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
