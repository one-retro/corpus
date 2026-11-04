# MiSTer saves

Saves written by MiSTer FPGA cores on the owner's MiSTer (DE10-Nano), played by script the same
way `tools/retro-run` plays libretro cores. Entries sit beside the libretro ones:
`corpus/<system>/<core>-mister/<game>/`, with `"method": "played"`, `"frontend": "mister"`.
Paths on the MiSTer are given relative to its SD card; `<sd>` stands for the card's mount point
where a full path is needed.

## What was made (2026-11-03/04)

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
| N64_MiSTer (N64_20260726) | n64 | | Super Mario 64, Yoshi's Story: loaded, Main created the `.eep`, but screenshots are black and the game never wrote its EEPROM; not pursued |
| Saturn, MegaCD, NeoGeo | | | not attempted (time): no MegaCD/Saturn scripts yet; NeoGeo needs the owner's `NEOGEO.CFG` changed (MVS->AES, Autosave) |

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
* **N64**: the scaler screenshot of the N64 core is black (640x240, all zero), so there was no
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

### The seed, and what a user's file would hold

Entries marked `started_from` began from a zero-filled file (see "Clean backup RAM" above).
Every byte the game wrote is the game's; the bytes it never wrote (the rest of an 8 KiB EEPROM
file, the unused half of a Pokemon flash, a MegaDrive file past the SRAM) are zero because of
the seed. On a user's MiSTer those bytes are whatever the memory held, which can be the previous
game's save: a sync tool must not expect them to be FF or 00, and should not treat them as
meaningful. GBA leftovers are real: a second Emerald run without a seed found the first run's
save.


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
written.

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

### Leaving the device as found

`mister.py cleanup --discard-unfiled` removes every save the rig made (filed or not), our
`config/*.CFG`, our screenshots, `corpus-tmp/`, and the `saves/<core>/` and
`savestates/<core>/` folders that the runs created (MegaDrive, SMS, GameGear, PSX, N64), loads
the menu core, then snapshots saves/, savestates/, screenshots/ and config/ again. On
2026-11-04 01:0x it printed "saves/, savestates/, screenshots/ match before.txt" and "config/
matches before-config.txt" (sizes, mtimes and sha1s identical), with the menu core running, no
uinput devices left and no 1Retro process at any point.

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
