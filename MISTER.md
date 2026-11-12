# MiSTer saves

Saves written by MiSTer FPGA cores on the owner's MiSTer (DE10-Nano), played by script the same
way `tools/retro-run` plays libretro cores. Entries sit beside the libretro ones:
`corpus/<system>/<core>-mister/<game>/`, with `"method": "played"`, `"frontend": "mister"`.
Paths on the MiSTer are given relative to its SD card; `<sd>` stands for the card's mount point
where a full path is needed.

## Fourth session (2026-11-12): Command Master, tilt and a script that watches the screen

**Filed.** `gbc/gameboy-mister/Command Master (Japan)/`: the owner's Command Master (Japan), an MBC7
cartridge (93LC56 EEPROM + accelerometer) whose only save, MAIN MENU > セーブ, comes after a
tutorial that has to be tilted through (`gbc/NOTES.md`). The Gameboy core's MBC7 reads the
accelerometer as 0x81D0 minus player 1's left analog stick (`rtl/mappers/mbc7.v`), so the rig's
virtual pad tilts: stick right = ▷, up = △. The file is 1024 bytes: the 256-byte EEPROM four
times, in the same word order as mGBA's `.srm` (Gearboy's is word-swapped).

The 1Retro watcher was running again, so the run used `gbcx` (setname CORPUSGBC) and grabbed
frames itself, as in the third session. Afterwards `saves/`, `savestates/`, `screenshots/` and
`config/` matched this session's snapshot line for line (sizes, mtimes, sha1), `corpus-tmp/` was
removed, and the watcher (same process) had been left alone.

**Why the MiSTer script watches the screen.** The libretro scripts are per core because cores
reach the same text box after different numbers of A presses (395 taps to the V-change in mGBA,
383 in Gearboy, about 402 here). On the MiSTer it is worse: two calibration runs of the very same
fixed taps were five taps apart at the same box, since real-time input lands a frame earlier or
later now and then and that adds up over hundreds of boxes. So the MiSTer script taps A until the
screen shows the box a stretch ends on, then goes on with fixed timing, which is all relative to a
press from there (the V-change's six timing points, the battle commands). Every stretch matched on
the first full run (23446 frames, under 7 minutes).

**Rig changes, fourth session** (`work/mister/mrun.py`): `stickhold X Y` leaves the left stick
deflected across later presses until the next `stickhold`; `refs FILE` loads screen references;
`tapuntil BTN GAP REF MAX` presses BTN (4 frames, then GAP) until the screen matches REF, at most
MAX times; `waituntil REF MAX` polls every 2 frames. A reference is a region thresholded at its own
mean brightness (`work/gbc/cm/mkref.py`, made from mGBA frames), so it matches the same screen in a
core whose colours differ: the MiSTer's frames matched mGBA's at 0.000. A region with too little
contrast never matches (a white fade would otherwise pass for some). Not reaching a reference ends
the script. The references used are in `scripts/mister/gbc/Command Master.refs`; the run used
`--fps 59.7275`, the Game Boy's frame rate, rather than 60.

## Third session (2026-11-10): Robopon, and what the cores read

The owner's 1Retro watcher (`1retro-mister watch`) was running and stayed running, so this session
wrote nothing a sync tool reads: every game ran under a setname no tool watches (`CORPUSGBC`,
`CORPUSGB`, `CORPUSGBA`, `CORPUSMD`, so `saves/CORPUS*/` and `config/CORPUS*.CFG`), and the
screen was read from the scaler's frame buffer rather than through `screenshot`, which always
writes into `screenshots/`. Main tells cores apart by their own name (`user_io.cpp` `orig_name`),
not the setname, which only names the folders. Afterwards `saves/`, `savestates/`,
`screenshots/` and `config/` matched the snapshot taken before, and the watcher had uploaded
nothing.

**Filed.** `gbc/gameboy-mister/Robopon - Sun Version (USA) (SGB Enhanced) (GB Compatible) (played)/`:
the corpus script, from no save file (Main hands a missing save to the Gameboy core as FF, so the
HuC-3 clock starts from an FF footer, which the core takes as a clock at zero). "Saved!" after
16034 frames. 33280 bytes; the footer is `3b85f36a` (1794344251, the save written at 20:57:31 PST
counted as though it were UTC, eight hours behind the instant), the HuC-3 state `05 01 00 00 00 00`
(day 0, 00:04 and 5 seconds), then FF. The `(played)` suffix keeps it apart from the downloaded
entry of the same release. Unlike Pocket Family GB, Robopon never announces elapsed days at the
title, so the libretro script needed no change.

**Main's clock.** `send_rtc` (`user_io.cpp`) hands cores `t + (t - mktime(gmtime(t)))`: `mktime` reads
`gmtime`'s fields with `tm_isdst = 0`, so the offset added is the zone's standard one, summer and
winter alike. Every MiSTer core that keeps a clock anchor gets that scale.

**What the cores read** (the save put in place, the game loaded, the screen read; no save written):

| core | save given | read? |
| ---- | ---------- | ----- |
| Gameboy (FFA, MBC2) | Gambatte's 8192-byte file (512 nibbles, then FF) | yes, slot 1 as the MiSTer's own |
| Gameboy (FFA, MBC2) | SameBoy's 512-byte file | yes |
| GBA (Klonoa, 4 Kbit EEPROM) | mGBA's 512-byte file | **no**: every slot NO DATA |
| GBA (Klonoa) | the same bytes padded with FF to 8192 | yes, the Prologue file |
| GBA (Klonoa) | gpSP's 131072-byte file | yes |
| MegaDrive (WSB '95, odd-lane SRAM) | Genesis Plus GX's 63804-byte file (byte-expanded) | **no**: EXHIBITION only |
| MegaDrive (WSB '95) | BlastEm's 32768-byte file (packed) | yes, CONTINUE LEAGUE |
| MegaDrive (WSB '95) | Genesis Plus GX's bytes packed by hand, padded to 65536 | yes |
| MegaDrive (Evander, 24C01 EEPROM) | Genesis Plus GX's 128-byte file | yes, RESUME OLD CAREER |
| MegaDrive (WSB '95) | one-saves' `extract --to mister` of Genesis Plus GX's save | yes |
| GBA (Klonoa) | one-saves' `extract --to mister` of mGBA's save | yes |

So a MiSTer needs a 4 Kbit EEPROM at 8 KiB and Mega Drive SRAM packed, and takes every MBC2
length. The reverse was checked in libretro Genesis Plus GX (`tools/make-save.py --dry --srm`):
the MiSTer's WSB '95 file as it is shows EXHIBITION only, and one-saves' layout of it for Genesis
Plus GX shows CONTINUE LEAGUE.

**Rig changes, third session.** `MISTER_SSH_OPTS` (extra ssh options, here a session's own
`ControlPath`), `MISTER_CREATED` and `MISTER_BEFORE` (this session's lists) are read from the
environment. Cores `gbcx`, `gbx`, `gbax`, `mdx` are the Gameboy, GBA and MegaDrive cores under a
`CORPUS*` setname; for those the daemon guard lets the run share the device with a watcher, and
`mrun.py` grabs frames itself (`MRUN_SHOT_DIR`, `grab_frame`: the scaler's RGB frame at
0x20000000 through `/dev/mem`, as `scaler.cpp` reads it) into `corpus-tmp/shots/` as PPM, which
`mister.py` turns into PNG. `work/mister/robopon/view.py NAME CORE ROM SAVE SCRIPT` puts a save in
place, loads the game, plays SCRIPT, fetches the frames and removes the save again; its scripts are
in `work/mister/robopon/vs/`.

## What was made, second session (2026-11-04)

The same rig, extended (see "Rig changes, second session"), for the cores the first session had
not reached and for the special cartridges the other workers scripted meanwhile. Every filed entry
was checked on its screenshots and compared byte for byte with the libretro entries of the game.

| core (.rbf) | system | filed | not filed |
| ----------- | ------ | ----- | --------- |
| NeoGeo_MiSTer (NeoGeo_20260603) | neogeo | mslugx (AES, card), jockeygp (MVS, cartridge RAM), lbowling and blazstar (MVS, backup RAM + card), kof98 (MVS, original BIOS, soft DIPs) (5) | fatfury2, samsho, samsho2, pbobblen, bstars2 not attempted (the save kinds were covered) |
| N64_MiSTer (N64_20260726) | n64 | Super Mario 64, Banjo-Kazooie (EEPROM 4K); Yoshi's Story (16K, only the game's first-boot format), Perfect Dark (16K); Ocarina of Time, Super Smash Bros. (SRAM); Majora's Mask (filed as `(USA) (played)`: a downloaded `(USA)` entry exists), Paper Mario (FlashRAM); Pokemon Stadium (FlashRAM + Transfer Pak with Pokemon Red); Tony Hawk's Pro Skater (Controller Paks); Dezaemon 3D (768 Kbit SRAM, first-boot set-up) (11) | |
| S32X_MiSTer (S32X_20260603) | sega-32x | WSB Starring Deion Sanders, Golf Magazine 36 Great Holes (2) | NBA Jam TE (EEPROM): after the script's 74k frames the game was still in a quarter, so no record and no file; the script is timed for PicoDrive |
| SGB_MiSTer (SGB_20260802) | gb | Link's Awakening, Pokemon Red, Super Mario Land 2, Final Fantasy Adventure (4) | |
| MegaDrive_MiSTer, file line FS2,SMS | mastersystem | Penguin Land, Phantasy Star (2): the MegaDrive core does run Master System cartridges | |
| MegaDrive_MiSTer | genesis | Frank Thomas Big Hurt Baseball (24C65), NFL Quarterback Club 96 (24C16), Micro Machines - Military (Codemasters 24C08, J-Cart) (3) | |
| SNES_MiSTer (SNES_20260823) | snes | F1-ROC II (ST010), BS-X, SD Gundam Generation - Ichinen Sensouki (Sufami Turbo) (3) | Hayazashi Nidan Morita Shougi (ST011: the board never moved, no file written; the core's README lists only the ST010). SuperFX, SPC7110, S-DD1, OBC1: no corpus scripts exist for them, so nothing to replay |
| Gameboy_MiSTer | gb, gbc | Tamagotchi (TAMA5), Net de Get (MBC6) (2) | MMM01: no script exists (the GB worker's Momotarou Collection 2 was attempted and dropped) |
| NES_MiSTer (NES_20260823) | nes | Romance of the Three Kingdoms II (MMC5 32 KiB), Uncharted Waters (MMC5 8+8 KiB), Nobunaga's Ambition (SOROM), Taito Grand Prix (X1-005), Pac-Man Championship Edition (Namco 163) (5) | |
| C64_MiSTer (C64_20260823) | c64 | | Summer Games: ran from the G64 (typed `LOAD"*",8,1` / `RUN`), but the 100m dash ended in FAULT twice, so no record was written to the disk (its sha1 unchanged); Elite not attempted (a disk swap needs the OSD). See `c64/NOTES.md` |
| MSX1_MiSTer (MSX1_20250108) | msx | | Hydlide II: with the blueMSX `MSX.ROM` loaded as BIOS (file index 1) and the cartridge in slot A (index 2) the core gave no picture (1x1 screenshots) and created no `saves/MSX1/`; its CONF_STR has no save option at all (only a `.DSK` drive written in place). Not pursued |
| MSX_MiSTer (MSX_20260603, OCM) | msx, msx2 | | not attempted: the core runs only from a VHD with OCM-BIOS and MSX-DOS (none on the device), its slots offer only MegaSCC+/MegaRAM, and nothing but the VHD is ever written: no cartridge SRAM exists to save |

The N64 core had failed in the first session for a simple reason: it needs the N64 PIF ROM as
`games/N64/boot.rom` (N64_MiSTer README), which the device lacked. The owner put their own dump
there for this session (it stays; it is theirs). Details of every system are in its NOTES.md
(`neogeo`, `n64`, `sega-32x`, `c64`, `msx`); the Game Boy, NES, SNES, Genesis and Master System
findings are below, since those NOTES belong to other workers.

## What was made (first session, 2026-11-03/04)

Saves made by script on the MiSTer and filed with `"method": "played"`, `"frontend": "mister"`;
each entry has the file(s) exactly as the core wrote them in `saves/<folder>/`, `provenance.json`
(core `.rbf`, the corpus script, the exact MiSTer script under `scripts/mister/`, the config
written, whether a seed was used) and `proof.png`, a MiSTer screenshot. Where the corpus script
has a power-cycle section, the proof was taken after loading the game again, so it shows the
save as read back from the SD card.

| core (.rbf) | system | filed | not filed |
| ----------- | ------ | ----- | --------- |
| GBA_MiSTer (GBA_20260530) | gba | Emerald, FireRed, Klonoa, Fire Emblem, Sonic Advance 2, SMA4, Kirby NiDL (7) | Minish Cap (see below) |
| Gameboy_MiSTer (Gameboy_20260603), as GAMEBOY | gb | Link's Awakening, FFA, Pokemon Red, Pokemon Yellow, SML2, Itsudemo! Nyan to Wonderful, Pocket Camera (7) | Pocket Family GB (HuC-3, see below) |
| Gameboy_MiSTer, setname GBC | gbc | Link's Awakening DX, Pokemon Silver (MBC3 clock), Oracle of Seasons, Tetris DX (4) | |
| SNES_MiSTer (SNES_20260823) | snes | Kirby Super Star, SimCity (2) | Dezaemon (free-cursor script lands elsewhere in real time) |
| NES_MiSTer (NES_20260823) | nes | EarthBound Beginnings, Family Circuit '91, Dragon Ball Z II (EEPROM) (3) | every other scripted NES game has a save on the device |
| MegaDrive_MiSTer (MegaDrive_20260603) | genesis | Evander Holyfield (EEPROM), World Series Baseball '95, Might and Magic, Jack Nicklaus' Power Challenge Golf (4) | Shining Force (the game ignored every input), Phantasy Star IV (a downloaded entry exists) |
| SMS_MiSTer (SMS_20260823) | mastersystem | Phantasy Star, Miracle Warriors, Ys, Golden Axe Warrior, Penguin Land (5) | |
| SMS_MiSTer, setname GameGear | sega-gg | Shining Force - Sword of Hajya, Magical Puzzle Popils, Defenders of Oasis (3) | |
| TurboGrafx16_MiSTer (TurboGrafx16_20260603) | pcengine | Chew-Man-Fu, Davis Cup Tennis, Bomberman '93, Jack Nicklaus' Turbo Golf, Night Creatures (5) | |
| PSX_MiSTer (PSX_20260807) | psx | Gran Turismo (memory card) (1) | |
| N64_MiSTer (N64_20260726) | n64 | | Super Mario 64, Yoshi's Story: loaded, Main created the `.eep`, but screenshots are black and the game never wrote its EEPROM (no PIF ROM on the device; done in the second session) |
| Saturn, MegaCD, NeoGeo | | | not attempted (time): no MegaCD/Saturn scripts yet; NeoGeo needed the owner's `NEOGEO.CFG` changed (done in the second session, with the owner's approval) |

Not filed, with reasons:

* **Minish Cap**: twice the file select froze half drawn (the file list slid off the left edge,
  no button did anything) right after the title, with a zero seed and again with an FF seed. The EEPROM was formatted (four "TINI" blocks and "KNIL"), but no file could be made.
* **Pocket Family GB**: the MiSTer HuC-3 clock appears to start from the host's time, not
  zero (its footer carries a real Unix timestamp), so the game spends the script's presses
  announcing elapsed days ("2000ねん11がつ04にち に なりました", then 05にち, ...) and never
  reaches the save. A MiSTer-specific script would have to mash
  through an unknown number of days.
* **Shining Force (Genesis)**: two runs, the intro never reacted to Start or C, although the
  same pad worked in four other MegaDrive games. Unexplained.
* **Dezaemon**: the copy needs the hand cursor on exact pixels (1 px per held frame); held in
  real time it stopped beside the OK button. The SRAM was only the S-RAM CHECK fill.
* **N64** (explained in the second session: the device had no `games/N64/boot.rom`, the PIF ROM
  the core needs): the scaler screenshot of the N64 core is black (640x240, all zero), so there was no
  way to see the game, and neither game wrote its EEPROM within 30 s (the files stayed all FF
  as Main created them). The N64 `.eep` naming was confirmed: Main 2026-10 writes
  `<rom>.eep`/`.sra`/`.fla`/`<rom>_N.cpk` (support/n64/n64.cpp), not one `.sav`.

## What the files look like

Sizes are the files the cores wrote; "libretro" is the same play in a libretro core of the
corpus.

**GBA_MiSTer.** The file is the backup memory rounded to the save type, plus one 512-byte
sector of clock when the cartridge has an RTC: EEPROM (4 or 64 Kbit) 8192, SRAM/FRAM 32768,
flash 64K 65536, flash 128K 131072, Emerald 131072 + 512 = 131584. The size comes from the
game's first access to save memory, or from an existing file's size if there is one (power of
two = no clock sector). A 4 Kbit EEPROM game (Klonoa) gets 8192 bytes: its 512 bytes, then
whatever the core's memory held (zero here, because of the seed). The EEPROM bytes are in the
same order as mGBA's and VBA-M's (SkyEmu swaps each 64-bit word). The clock sector (Emerald) is
32 copies of one 16-byte record: `54 52` ("RT" as a little-endian 16-bit word), 10 bytes of
little-endian bit field (bits 0-41: the S-3511 registers, seconds 7 bits, minutes 7, hours 6,
weekday 3, day 6, month 5, year 8, BCD; bits 42-73: the host's time as a 32-bit Unix timestamp,
which is local wall time, here 2026-11-03 23:27:39 for a save made at 23:27 PST), then 4 zero
bytes. That is `clocks.json`'s gba-mister entry (packed, 512 reserved, 4-byte timestamp); note
the timestamp is not byte-aligned: it starts at bit 42 of the field, i.e. inside byte 7.

**Gameboy_MiSTer.** RAM size from the header, (ram_mask_file + 1) sectors: 2K 2048, 8K 8192,
32K 32768, 128K (Pocket Camera) 131072; MBC2 1024 (the 512 nibbles one per byte with the high
nibble 0, as IroGB writes and unlike the F-filled nibbles of most libretro cores, then 512
bytes of whatever the memory held). MBC3 with a timer (Pokemon Silver, Itsudemo) and HuC-3 add
one 512-byte sector: Unix timestamp (4 bytes LE, local wall time), the 48-bit clock state
(MBC3: the latched registers; HuC-3 packed its own way), then FF to the end: Silver 33280,
Itsudemo 8704. That is clocks.json's gameboy-mister entry. The same core under setname GBC saves
to `saves/GBC/` and keeps `config/GBC.CFG`; the device's own Crystal save there is 32768 bytes,
i.e. was not written with a clock sector by this core. Yellow loaded as `.gb` ran in DMG mode.

**SNES_MiSTer.** BSRAM at its header size (KSS's SA-1 BW-RAM 8192, SimCity 32768). The core
fills BSRAM with FF on every ROM load ("Thrash the BSRAM"), so unwritten bytes are FF, as in
snes9x; no seed was used or needed.

**NES_MiSTer.** 64 sectors (32768) unless the header is NES 2.0 with PRG-NVRAM = 8 KiB (shift
7): then 16 sectors (EarthBound Beginnings, 8192). Family Circuit '91 declares 2 KiB (shift 5)
and still gets 32768; its first 2048 bytes equal Mesen's 2 KiB .srm. Mappers with a serial
EEPROM keep it in block RAM and write 4 sectors: Dragon Ball Z II's 24C02 is 2048 bytes, 256
of EEPROM then 1792 zeros (the core's own, no seed). Autosave is on by default.

**MegaDrive_MiSTer.** Always 128 sectors, 65536 bytes, whatever the cartridge has. Byte-wide
SRAM (odd addresses only) is stored packed, one byte per SRAM byte, like BlastEm (World Series
Baseball '95's first 32 KiB are byte-identical to BlastEm's 32768-byte .srm) and unlike Genesis
Plus GX and PicoDrive, which store 16-bit words with the SRAM byte in the odd half (and FF or 00
in the even). Serial EEPROM (Evander, 24C01) is its 128 bytes at the start, then zeros (seed).

**SMS_MiSTer** (and as GameGear). Always 64 sectors, 32768 bytes. Penguin Land's file is
byte-identical to SMS Plus GX's 32 KiB .srm; Phantasy Star's first 8188 bytes equal Genesis
Plus GX's 8188-byte file.

**TurboGrafx16_MiSTer.** HuCards get the 2 KiB backup RAM of a CD-ROM2/Tennokoe system, 4
sectors, 2048 bytes, `HUBM` header and directory: byte-identical to Beetle PCE's .srm for
Chew-Man-Fu and Davis Cup Tennis.

**PSX_MiSTer.** Memory card 1 is a raw 128 KiB card (`MC` header frame, directory frames,
blocks). Main names it after the game's folder, not the `.cue`, and creates it at mount as a
formatted blank card (support/psx/psx.cpp), so it exists before the game saves. Gran Turismo's
card is byte-identical to Beetle PSX's.

**NeoGeo_MiSTer** (second session). One `.sav` per game, always 73728 bytes (0x90 sectors),
named after the `.neo` file (or the romset folder): 64 KiB of MVS backup RAM, then an 8 KiB region
holding the memory card (2 KiB used) or, for Jockey GP and V-Liner, the cartridge's own RAM in its
place. Every 16-bit word byte-swapped: the backup RAM in exactly FinalBurn Neo's `.fs` order, so a
Jockey GP `.sav` has the layout and size of FBNeo's 73728-byte `.fs`. AES leaves the backup RAM as
loaded (FF). The card's saved blocks are byte-identical to Geolith's `.mcr`; only the 32-byte card
header differs (UniBIOS formats it its own way). Details in `neogeo/NOTES.md`.

**N64_MiSTer** (second session). One file per chip and per pak in `saves/N64/`, named after the ROM:
`.eep` 512 or 2048, `.sra` 32768 (98304 for Dezaemon 3D's 768 Kbit SRAM), `.fla` 131072,
`_1.cpk`-`_4.cpk` 32768 each, `_1.tpk` 32768. SRAM and FlashRAM files are in the libretro `.srm`
order (each 32-bit word reversed, one-saves' "swapped"): Ocarina of Time's `.sra` is
byte-identical to Mupen64Plus-Next's SRAM region. EEPROM and paks are in console order. Main
creates the files at ROM load (chips FF, paks formatted by Main with a random serial and "MiSTer").
The Transfer Pak works: its memory is the Game Boy game's own save in `saves/GAMEBOY/` (Pokemon
Stadium wrote 32 bytes into Pokemon Red's), and Main leaves two copies of the original beside it,
`<gb rom>_bak.sav` and `saves/N64/<n64 rom>_1.tpk`. Details in `n64/NOTES.md`.

**S32X_MiSTer** (second session). Always 65536 bytes, `saves/S32X/<rom>.sav`. Byte-wide SRAM is
stored *expanded*, the game's bytes at odd offsets, like PicoDrive but with FF (not 00) in the even
bytes; every byte the games wrote matches PicoDrive's. That is the opposite of MegaDrive_MiSTer,
which packs byte-wide SRAM. Details in `sega-32x/NOTES.md`.

**SGB_MiSTer** (second session). `saves/SGB/<rom>.sav`, the Game Boy cartridge RAM at the size the
Gameboy core writes (LA 8192, Pokemon Red 32768, SML2 8192, FFA's MBC2 1024 with the nibbles one
per byte, high nibble 0). Unwritten bytes are FF: Link's Awakening's file is byte-identical to
Gambatte's `.srm`; Red differs from Gambatte's in 5 bytes of game data, SML2 in 144. The core needs
the Super Game Boy BIOS (the SNES cartridge, `.sfc`) through its `FC4` file line; the MGL loads it
first, and Main stores its path in `config/SGB.f4` (a file the rig removed afterwards). The
optional SGB boot ROM (`FC5`, `.bin`) was not needed.

**MegaDrive_MiSTer with Master System cartridges** (second session). The 2026-06-03 core has a
second file line, `FS2,SMS` (Power Base Converter mode). Saves go to `saves/MegaDrive/`, 65536
bytes like every MegaDrive save: the first 32768 bytes are byte-identical to SMS_MiSTer's whole
32768-byte file for the same game (Penguin Land, Phantasy Star), the rest is what the memory held
(the zero seed here). SMS buttons 1/2 are the MD pad's B and C.

**MegaDrive_MiSTer, serial EEPROMs** (second session). The core's EEPROM map covers Acclaim's
24C65 (Frank Thomas) and 24C16 (NFL QB Club 96) boards and the Codemasters 24C08 on the J-Cart
(Micro Machines - Military), all at the start of the 65536-byte file: Frank Thomas's first 8192
bytes equal Genesis Plus GX's and BlastEm's 8192-byte files; NFL QB Club 96's and Micro Machines'
first 8192 bytes equal PicoDrive's 8192-byte files (00 where never written).

**SNES_MiSTer, special chips** (second session). ST010 (F1-ROC II): the core takes the chip's
firmware appended to the ROM (`st010.rom`, 53248 bytes, program then data ROM), and saves 2048
bytes: the *upper half* of the ST010's 4 KB data RAM, i.e. bytes 0x800-0xFFF of the libretro
cores' 4096-byte file, identical to theirs where the game wrote (the player at 0x10 here, 0x810
there); the chip's lower 2 KB work area is not saved, and never-written bytes are FF (00 in the
libretro files). ST011 (Morita Shougi, firmware appended the same way): Main flags it, but the core's README
lists only the ST010; the game showed its board and never moved (neither the script's move nor the
computer's), and no save file was written. BS-X: the base cart loaded
as the ROM gives a 32768-byte `.sav` byte-identical to bsnes's `.srm`, and no PSRAM file. Sufami
Turbo: Main expects one image, the base cart padded to 1 MiB, then mini-cart A (and B) on 1 MiB
boundaries, each starting `BANDAI SFC-ADX`; the save, named after that image (so here after the
mini-cart), is cart A's 8192 bytes, like Mesen2's (snes9x writes 16384).

**Gameboy_MiSTer, special mappers** (second session). TAMA5 (Tamagotchi): 1024 bytes, the TAMA5's
32 bytes at 0x000 and repeated at 0x100, 0x200, 0x300, FF elsewhere, one file byte per TAMA5 byte
like mGBA's and Gearboy's 32-byte `.srm`; no clock saved (mGBA saves none either; Gearboy adds a
72-byte `.rtc`). MBC6 (Net de Get, as GBC): 32768 bytes, the SRAM only, no flash (like IroGB;
Gearboy's file adds the 1 MiB flash).

**NES_MiSTer, special boards** (second session). Uncharted Waters (MMC5, 8 KiB battery + 8 KiB
volatile) and Nobunaga's Ambition (SOROM, the same split) get 8192-byte files, and both hold the
*battery* chip (Nobunaga's has nothing at 0x000-0x3FF, the layout of fceumm's and Nestopia's files;
fixNES, Mesen and QuickNES save the work chip there). Uncharted Waters differs from fceumm, Mesen
and Nestopia in 4 bytes (the rolled stats); no MMC5 ExRAM is saved. Taito X1-005 (Taito Grand
Prix): the mapper's 128 bytes at 0x00 of a 32768-byte file, byte-identical to Nestopia's 128-byte
file. Namco 163 (Pac-Man CE): 8192 bytes, the N163's own 128 bytes not saved; the `sav` block
matches every libretro core, but 0x000-0x6F1 (what looks like the recorded replay) is all 00 here,
where the five libretro files agree on 1217 non-zero bytes; the game still offers and plays the
replay after a reload. A run of Taito Grand Prix without a seed showed the leftover problem for
real: past the 128 bytes the file held the previous game's battery and work RAM (Nobunaga's). Romance of the Three Kingdoms II (MMC5, 32 KiB): 32768 bytes like fceumm's, Nestopia's and RustyNES's; its title took START only when held 20 frames on this core.

### The seed, and what a user's file would hold

Entries marked `started_from` began from a zero-filled file (see "Clean backup RAM" above).
Every byte the game wrote is the game's; the bytes it never wrote (the rest of an 8 KiB EEPROM
file, the unused half of a Pokemon flash, a MegaDrive file past the SRAM) are zero because of
the seed. On a user's MiSTer those bytes are whatever the memory held, which can be the previous
game's save: a sync tool must not expect them to be FF or 00, and should not treat them as
meaningful. GBA leftovers are real: a second Emerald run without a seed found the first run's
save.

A correction from the second session: some cores *do* reload the save after every ROM load, file
or no file, and Main hands them FF blocks when the file does not exist (user_io.cpp: a save that
"will be created upon write" reads as `memset(-1)`, except for the cores with their own blank
format: MegaCD, PCE, PSX, Saturn, 3DO). For those cores a fresh user file has **FF** wherever the
game never wrote, and no seed is needed: NeoGeo, S32X, SGB, Gameboy (its `new_load`), TurboGrafx16
(no `img_size` check). The cores that load only an existing file (`|img_size & bk_ena`: NES, SMS,
MegaDrive, SNES) keep whatever the memory held, and SNES then fills with FF itself. The first
session's Gameboy entries were seeded with zeros, so their never-written bytes are 00 where a
user's file has FF; the SGB entries of the second session, from the same Game Boy logic, show the
FF.


## The rig

Two programs, both in `work/mister/` (not committed; copy them back from here if lost):

* `mrun.py` runs **on the MiSTer** (python3 3.9, no evdev module) from `corpus-tmp/` on the SD card.
  It creates two uinput devices with `fcntl`/`struct` only: a gamepad (`corpus virtual pad`,
  1209:c0de) and a keyboard (1209:c0df), then plays a script.
* `mister.py` runs **here** (`python3 -I`). It checks the device, writes the MGL and the core
  config, turns a corpus script into a MiSTer script, runs `mrun.py` over ssh, fetches the
  screenshots and the save, and files the entry. `batch.sh LIST` runs a list of games one after
  another.

```
python3 -I work/mister/mister.py check                       # is a 1Retro daemon running?
python3 -I work/mister/mister.py run gba ROM SCRIPT --tag emerald --seed 131584
python3 -I work/mister/mister.py file work/mister/runs/<run> gba "<game>"
python3 -I work/mister/mister.py cleanup                      # see "Leaving the device as found"
```

ssh: key authentication as root, with `BatchMode=yes`.

### Loading a game: MGL through /dev/MiSTer_cmd

`/dev/MiSTer_cmd` is a FIFO Main_MiSTer reads (input.cpp). Commands: `load_core PATH` (`.rbf`,
`.mra`, `.mgl`), `screenshot [scaled] [NAME]`, `volume`, `video_mode`, `fb_cmd`. An MGL
(support/arcade/mra_loader.cpp `scan_mgl`, menu.cpp) names the core and the file:

```xml
<mistergamedescription>
	<rbf>_Console/GBA</rbf>                      <!-- newest _Console/GBA_*.rbf -->
	<setname>GBC</setname>                       <!-- optional: CoreName2, so saves/GBC/, config/GBC.CFG -->
	<file delay="1" type="f" index="0" path="<sd>/corpus-tmp/roms/gba/X.gba"/>
</mistergamedescription>
```

`type` is `f` (an `F` line of the core's CONF_STR) or `s` (an `S` line, CD images); `index`
is the digit after `F`/`FS`/`FC` in that line (no digit = 0); `delay` is seconds after the core
starts; a path starting with `/` is absolute, so ROMs copied to `corpus-tmp/` load
without touching `games/`. The save is named after the ROM, not its folder:
`saves/<CoreName2>/<rom stem>.sav` (file_io.cpp `FileGenerateSavePath`), so a ROM loaded from
corpus-tmp saves exactly where one from `games/` would. Indexes used:

| core | rbf | file line | MGL |
| ---- | --- | --------- | --- |
| GBA | `_Console/GBA` | `FS,GBA` | f 0 |
| Gameboy (GB) | `_Console/Gameboy` | `FS1,GBCGB BIN` | f 1 |
| Gameboy (GBC) | `_Console/Gameboy` + setname `GBC` | same | f 1 |
| SNES | `_Console/SNES` | `FS1,SFCSMCBINBS` | f 1 |
| NES / FDS | `_Console/NES` | `FS,NESFDSNSF` | f 0 |
| MegaDrive | `_Console/MegaDrive` | `FS1,BINGENMD` | f 1 |
| SMS | `_Console/SMS` | `H8FS1,SMSSG SC` | f 1 |
| Game Gear | `_Console/SMS` + setname `GameGear` | `H8FS2,GG` | f 2 |
| PSX | `_Console/PSX` | `H7S1,CUECHD` | s 1 |
| NeoGeo | `_Console/NeoGeo` | `FS1,*` (`.neo` or a romset folder) | f 1 |
| N64 | `_Console/N64` | `FS1,N64z64n64v64`; `F2,GBCGB` = the Transfer Pak's Game Boy game, loaded first | f 1 (f 2) |
| 32X | `_Console/S32X` | `FS,32X` | f 0 |
| MegaDrive, Master System cartridge | `_Console/MegaDrive` | `FS2,SMS` | f 2 |
| SGB | `_Console/SGB` | `FC4,SFC` the SGB BIOS (loaded first), `FS1,GBCGB` the game | f 4, then f 1 |
| C64 | `_Computer/C64` | `H7S0,D64G64T64D81` drive #8 | s 0 |
| MSX1 | `_Computer/MSX1` | `P2F1,ROM` BIOS, `H3F2,ROM` slot A | f 1, then f 2 |

### Input: a uinput gamepad Main maps by default

A gamepad with no map file gets Main's built-in map (`def_mmap` in input.cpp): hat 0 = d-pad,
`BTN_EAST` = A, `BTN_SOUTH` = B, `BTN_NORTH` = X, `BTN_WEST` = Y, `BTN_TL`/`BTN_TR` = L/R,
`BTN_SELECT`, `BTN_START`, `BTN_MODE` = OSD. In a core, `map_joystick` (joymapping.cpp) then
gives each of the core's buttons the pad button of the same name, using the CONF_STR `jn` line
(`gamepad_defaults=0`, the default). That "virtual SNES" layout is libretro's RetroPad, so the
corpus scripts' button names carry over unchanged for GBA, GB, SNES, NES, TG16, PSX
(b=Cross a=Circle y=Square x=Triangle). Two cores need a translation, which `mister.py`
applies (`BUTTON_MAP`):

* MegaDrive / MegaCD: `jn,A,B,R,Start,Select,X,Y,L` puts Genesis C on R and Z on L, while the
  corpus scripts use Genesis Plus GX's y/b/a = A/B/C, l/x/r = X/Y/Z. Mapped y->a, a->r, l->x,
  x->y, r->l.
* SMS / Game Gear: `jn,A|P,B,...` puts button 1 on A and button 2 on B; Genesis Plus GX has
  b = button 1, a = button 2. Mapped b<->a.

The first button press assigns the pad to player 1 (the owner's HORI pad is idle, so it stays
unassigned); the `controller_info=6` "Map:" popup that follows is an Info OSD and does not take
input from the core. Nothing is written to `config/inputs/`: Main saves maps only when a user
defines one.

Script language (`mrun.py`): `wait N`, `press BTN[+BTN] [N]`, `tap BTN [COUNT] [GAP]`,
`stick X Y [N]`, `rstick`, `key KEY [N]`, `type`, `repeat N ... end`, `include`, `shot NAME`,
`echo`, `quit` as in retro-run, plus `load MGL [SECS]`, `osd` (tap F12), `save [SECS]` (F12,
wait, F12) and `sleep SECS`. Frames are wall-clock 1/60 s on a fixed schedule (no drift; a
slow step resyncs instead of rushing). The cores run at their own rate in real time, so a
script frame is about one console frame (GBA 59.73 Hz, NES/SNES 60.1 Hz); the corpus scripts'
generous waits absorb the difference, and none needed retiming.

`mister.py run` builds the MiSTer script from a corpus script: `load` the MGL; the corpus
script up to its power-cycle section (the first `dump`/`reset`/`srm`); `save`; `shot final`;
then the power cycle done for real: `load` the MGL again, which makes the core read the `.sav`
back from the SD card, followed by the corpus script's lines after the cycle. Its last `shot`
(the title's CONTINUE, the file list...) is `proof.png`, so every proof shows the save as read
back from the card. The exact script that ran is kept in `scripts/mister/<system>/`.

### Seeing the screen

`echo "screenshot corpus-NAME.png" > /dev/MiSTer_cmd` writes the scaler's input frame (the
core's native resolution, no OSD) as `screenshots/corpus-NAME.png`: a name ending in
`.png` goes straight into `screenshots/` (file_io.cpp `FileGenerateScreenshotName`); without
one it goes to `screenshots/<core>/<rom>-<date>.png`. Main takes one screenshot at a time and
silently drops a request made while one is pending (scaler.cpp), so `mrun.py` waits for the
file to appear before going on; a `shot` right before an F12 was lost before that. The OSD is
never in a screenshot (it is mixed in after the scaler), so OSD navigation would be blind; the
rig avoids needing it.

### Making the save reach the SD card

The cores keep battery RAM in FPGA memory and write it as an SD image (`sd_lba`/`sd_wr`)
only when asked: the OSD's "Save Backup RAM" trigger, or, with **Autosave** on, the moment
the OSD opens (`OSD_STATUS` rising) while a write is pending (`bk_pending`/`sav_pending`).
Autosave is off by default in GBA (status bit 23), Gameboy (13), SNES (23), MegaDrive (13),
SMS (25), TurboGrafx16 (23), MegaCD (13), Saturn (26), NeoGeo (24); on by default in NES, N64,
PSX. Rather than walk the OSD blind, `mister.py` writes the core's config file before loading:
`config/<CoreName2>.CFG` is the 16-byte status bitmap Main loads at core start
(user_io.cpp; `CONF_STR` `v,N` would add `_vN` to the name, none of these cores has one), so a
file with only the Autosave bit set means "every option default, Autosave on". The `save` step
then presses F12 (open), waits 2-3 s, F12 (close). These CFG files did not exist on the device;
they are removed afterwards. A config that already exists (the owner's `NEOGEO.CFG`) is never
written, unless the owner allows it: in the second session they did, for `NEOGEO.CFG`, and the rig
put it back byte-identical after every run (see "Rig changes, second session"). Second-session
Autosave bits: S32X 13, SGB 23, NeoGeo 24; N64 has Autosave On by default (bit 42 = Off), so no
N64 config was written; C64 has no backup RAM (disks are written in place).

### Clean backup RAM: the zero-filled seed

The cores do not clear their save memory when a game is loaded without a save file (SNES is
the exception: it fills BSRAM with FF on every ROM load). GBA keeps it in SDRAM/DDR3, and it
survives a core reload: the second Emerald run found the first run's save ("There is already a
saved file. Is it okay to overwrite it?"). So before loading, `mister.py run --seed SIZE` puts a
zero-filled `.sav` of exactly the size the core will write; the core loads it (clearing the
memory to what the first, clean run started from: zeros), the game runs, and on save the core
rewrites the whole file. The size must be the core's own, or the core would use the seed's
(GBA takes its save size from an existing file). Provenance says `started_from` when a seed was
used.

### A bug worth knowing about (fixed)

`frames_pass` used to "catch up" when the schedule had fallen behind, and a `shot` (which waits
for the file) left it behind, so the next `press` was released the instant it was made: a 0 ms
press, which the core never samples. Every press right after a screenshot was lost. It showed
as scripts going off the rails exactly one step after a `shot` (Phantasy Star's END,
Evander's "accept", Kirby Super Star's Retire). Now `shot` restarts the schedule, and a step that
starts late still gets its full length. Runs made before the fix were redone or are noted in
their provenance (Miracle Warriors' proof, Kirby Super Star's).

### Rig changes, second session

* **New cores** in `CORES`: `neogeo`, `n64` (now working), `s32x`, `mdsms` (MegaDrive core,
  `FS2,SMS`), `sgb`, `c64`, `msx1`; button maps for Neo Geo (libretro b/a/y/x = Neo A/B/C/D, select
  = Coin, which is the core's L), 32X (as MegaDrive), Master System on the MD core (b/a = MD B/C)
  and C64 (fire = the pad's A).
* **`--cfg-bits N,M,...`** sets status bits besides Autosave in the core config: NeoGeo System
  Type (bit 1, MVS), BIOS (bit 22, Original), [DIP] Settings (bit 7); C64 Swap Joysticks (bit 3,
  port 2).
* **An owner's config, changed and restored.** `config/NEOGEO.CFG` existed (the owner's: MVS,
  UniBIOS, Autosave off), and the owner allowed changing it for the runs. The rig copied the
  device's whole `config/` to `work/mister/config-backup/` before any run; for a core marked
  `cfg_restore` it writes its own 16 bytes, runs, and in a `finally` puts the owner's bytes back,
  sets the mtime back to the one in `before-config.txt` (`python3` `os.utime` on the device) and
  checks the sha1. Every NeoGeo run ended with "restored config/NEOGEO.CFG".
* **`--pre-file TYPE,INDEX,FILE`** adds an MGL `<file>` before the game (the SGB BIOS, the Transfer
  Pak's Game Boy game, the MSX BIOS); `%20` stands for a space, since `batch.sh` splits options on
  spaces. Main processes MGL items in order, each `delay` seconds after the previous one.
* **`--pre FILE`** lines now also follow the power-cycle reload (the SGB's 300-frame BIOS intro).
* **`--view`** runs over our own existing save with `--no-save` (to read a save back).
* `run` uploads `mrun.py` every time; `file --script S` names the corpus script a MiSTer variant
  came from, `--cfgdesc TEXT` describes the config written. MiSTer variants of corpus scripts (only
  where timing or the boot differs) were written in `work/mister/vscripts/`; the exact script that
  ran is in `scripts/mister/<system>/` as before.
* `mrun.py` knows `lbracket rbracket backslash grave rctrl ralt` (the C64's `*` is the key right of
  `P`, i.e. `]`).
* A fresh baseline: the first session's `before*.txt`, `after.txt`, `created.txt` and
  `config-backup/` moved to `work/mister/session1/`.
* Lesson: a `Monitor`/wait on `runs/<core>-<tag>-*/run.json` must not match an older run directory
  with the same tag (a Yoshi run of the first session did).

### Leaving the device as found

`mister.py cleanup --discard-unfiled` removes every save the rig made (filed or not), our
`config/*.CFG`, our screenshots, `corpus-tmp/`, and the `saves/<core>/` and
`savestates/<core>/` folders that the runs created (MegaDrive, SMS, GameGear, PSX, N64), loads
the menu core, then snapshots saves/, savestates/, screenshots/ and config/ again. On
2026-11-04 01:0x it printed "saves/, savestates/, screenshots/ match before.txt" and "config/
matches before-config.txt" (sizes, mtimes and sha1s identical), with the menu core running, no
uinput devices left and no 1Retro process at any point.

Second session (2026-11-04): a fresh baseline was taken before the first run (`before.txt`,
`before-config.txt`; the device's `config/` copied to `config-backup/`); the owner's
`config/NEOGEO.CFG` was put back after every NeoGeo run (same sha1 and mtime, checked). At 14:2x
`cleanup --discard-unfiled` removed every save, config (`C64`, `GAMEBOY`, `GBC`, `MegaDrive`,
`S32X`, `SGB`, `SNES` `.CFG` and Main's `SGB.f4`), screenshot and folder the runs made (`saves/N64`,
`S32X`, `SGB`, `MegaDrive`, `savestates/N64`, `SGB`), including the Pokemon Red save and its
`_bak` that the Transfer Pak run used in `saves/GAMEBOY/`; `corpus-tmp/` was removed whole. It
printed "saves/, savestates/, screenshots/ match before.txt" and "config/ matches
before-config.txt", with the menu core loaded, no uinput devices left and no 1Retro process at any
point. The one change left on purpose is the owner's: `games/N64/boot.rom`, their PIF ROM, put
there for this session and kept.

### Safety

* `guard()` runs `ps w` before every run and refuses if any process mentions 1retro (the
  1Retro daemon is started only from the Scripts menu or `user-startup.sh`; it never ran).
* Before anything, `work/mister/before.txt` recorded saves/, savestates/ and screenshots/
  (size, mtime, sha1) and `before-config.txt` config/; `config-backup/` holds a copy.
* A run refuses when `saves/<folder>/` already has a file with the game's stem. Every file put
  on the device is listed in `work/mister/created.txt`; `forget` and `cleanup` delete only
  those, and refuse anything that is in before.txt.
* Everything else lives in `corpus-tmp/` (mrun.py, MGLs, scripts, ROMs, discs),
  removed at the end.
