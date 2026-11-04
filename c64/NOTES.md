# Commodore 64

Two disk games, four runnable VICE cores, eight entries filed; Frodo filed nothing (why below).
A C64 game saves by writing to a floppy, so the question here is not "what file does the core
write" but "**which disk image** does the write land in, and does it survive". The answers:

- **VICE, `.d64`/`.g64` content:** in place, into the content file itself (write protection is off
  by default). Filed as `<image>.changes.json` (the changed blocks), since the image is the game.
- **VICE, `.nib` content (how the No-Intro set ships disks):** into a G64 that VICE converts the
  NIB to, in `<save dir>/TEMP/`, which VICE **deletes in `retro_deinit`**. The save is lost when
  the content is closed. Verified on all four cores.
- **VICE save disk:** `<content stem>.save0.d64` in the save directory, stored **gzip-compressed**
  as `.save0.d64.gz`. Created by the "Toggle Save Disk" hotkey (unmapped by default) or an M3U
  `#SAVEDISK:` line. This is the only one of the three that RetroArch-style sync would see.
- **Frodo:** in place into a `.d64` (`r+b`), by its source; no game could be made to save, because
  Frodo cannot load the formats the protected originals need.

## The library

`tools/rom.py get c64` reads "Commodore - Commodore 64": **230 `.crt` cartridges and 4 `.d64`**
(Viking Raider's loader disk and the three exercise disks of Der Rechtschreiblöwe, both of which
need their cartridge). None of the cartridges can save on their own: the hardware types are 0, 5,
7, 8, 11, 15, 17, 18, 19 (no EasyFlash, no GMod2/EEPROM). Disk games are in "Commodore - Commodore
64 (PP)" as NIBTools raw dumps (`.nib`, 1310 games); tapes in "(Tapes)" as `.tap`. These were
extracted by hand into `.cache/roms/c64pp/` (rom.py covers only the main set). Several PP dumps
are tagged `(b-highscores)`: the dumpers' disks had high scores written to them, which is how
these games save.

## The games

| Game (No-Intro PP) | The save | Where it goes | Proof (last shot) |
| --- | --- | --- | --- |
| Summer Games (USA, Europe) | 100m dash as ABC (France): waggling left/right every 2 frames runs 9.75 s against the 10.47 record; the game writes the record table to the **game disk** (sectors 15/6, 18/0 BAM, 18/1 directory) | in place into the `.g64` | after a reset (VICE's default reset re-runs the content) and a reboot from disk, 5) SEE WORLD RECORDS shows 100m DASH ABC 09.75 |
| Elite (Europe) | docked at Lave: `@` (disk menu), 3 Change To Disk, 2 Save Commander ABC. The game disk has 0 blocks free, so the save goes to a second disk, as on the real machine | VICE save disk `Elite (Europe).save0.d64.gz` (gzip of a 174848-byte d64 named SAVE DISK 0 holding one 1-block PRG `ABC`) | 1 Load New Commander ABC: COMMANDER ABC, docked at Lave |

Tried and dropped:
- **Viking Raider (USA, Europe)** (cartridge + `.d64`, run through an M3U with `#COMMAND:-cartcrt
  ... -8 ...`): the cartridge loads the game from the disk ("Please Select Game Copy 1 or 2" picks
  one of two copies of the program on the disk, with a DISK ERRORS counter). No save command
  exists among the 26 letter commands, F1-F8, RUN/STOP, CTRL+S; nothing was written to the disk.
- **Lode Runner, Championship Lode Runner**: save high scores / levels to the master disk, but
  boot only from the NIB/G64 (from a `.d64` the protection check corrupts the screen); not
  scripted for lack of time.

Scripts: `scripts/c64/Summer Games.txt` (+ `SummerGames.start.txt`), `scripts/c64/Elite.txt`.
Options: `vice-x128.opt` (`vice_c128_go64 = enabled`), `vice-elite.opt` (save disk hotkey on
F12, otherwise defaults), `vice-x128-elite.opt` (+ go64), `vice-xscpu64-elite.opt` (+ SuperCPU
speed Normal).

## Games x cores

| Game | vice-x64 | vice-x64sc | vice-x128 | vice-xscpu64 | frodo |
| --- | --- | --- | --- | --- | --- |
| Summer Games (`.g64`) | filed | filed | filed (`go64`) | filed | failed: no G64/NIB support; from a `.d64` decoded from the NIB the game reaches its menu, but loading the 100m dash resets to BASIC |
| Summer Games (`.nib`, the library file) | written to TEMP, deleted: not filed | same | same | same | cannot load `.nib` |
| Elite (`.nib` + save disk) | filed | filed | filed (`go64`) | filed (SuperCPU at 1 MHz; at the default 20 MHz the fast loader hangs at LOADING ELITE) | not run: Frodo has no second-disk or save-disk mechanism and the decoded game disk has 0 blocks free, so the save could only fail |

| Core | Status |
| --- | --- |
| c64-mister (MiSTer), markus-zzz-myc64 (openFPGA) | not runnable; see "Downloaded entries and leads" |
| vice-x64dtv (libretro, no macOS build) | not runnable |

Core builds: VICE 3.10 `5ebe7d3` (x64, x64sc, x128, xscpu64; libretro buildbot, arm64), Frodo
`V4_2`. No BIOS files are needed (both cores carry the ROMs).

## Summer Games: in place, and lost from TEMP

The PP set has only `Summer Games (USA, Europe).nib`. VICE's libretro loader converts a `.nib` to
`<save dir>/TEMP/<name>.g64` (libretro-core.c, `nib_convert`) and attaches that. Disk writes then go
into the temporary G64, and `retro_deinit` (and `retro_init`) call `remove_recurse(TEMP)`: after
the run the save directory holds only an empty `TEMP/` directory. Within the session the record is
real (the reset-and-reboot proof shows it read back from the disk); after closing it is gone.
`work/msx/retro-run-x --keep-temp` copies TEMP out after `retro_unload_game` and before
`retro_deinit`: the kept G64 differs from the unwritten conversion in 1817-1822 bytes, on tracks
15 and 18, on all four cores. Screenshots in `work/c64/evidence/`.

To get a file that keeps the write, the content was VICE's own conversion: the TEMP G64 of a run
that wrote nothing (sha1 `025714c88dc3…`, identical from all four cores), used as `.g64` content.
VICE then writes into that file in place. The filed entry is `Summer Games (USA,
Europe).g64.changes.json`: the 256-byte blocks of the G64 file that changed, old and new bytes in
hex, and the sha1 of the original and modified image (rebuilding from the JSON reproduces the
sha1). `provenance.json` has `rom_source` (the NIB) and `logical_change`.

Differences between the cores' writes:
- Decoded as sectors (`work/c64/g64sectors.py`), all four cores wrote **identical data**: sectors
  15/6, 18/0 and 18/1 changed, nothing else.
- As G64 bytes they differ: x64sc and xscpu64 produced the same file (sha1 `261e7ba8…`), x64
  (`4fc3c078…`) differs from them by 328 bytes on track 18, x128 (`76c39e69…`) by 328 bytes on
  tracks 15 and 18. The GCR around a rewritten sector depends on where the write splice falls.
  A rewritten data block ends early: the two "off" bytes after the checksum are cut, so a
  decoder must not require them.
- The track lengths in the G64 did not change.

A `.d64` decoded from the NIB (`work/c64/nib2d64.py`, all 683 sectors) boots in VICE and Frodo
but the 100m dash never loads (VICE hangs at NEXT EVENT, Frodo resets to BASIC): the event loader
needs the copy protection that only the GCR image keeps.

## Elite: the VICE save disk

With `vice_mapper_save_disk_toggle = RETROK_F12`, F12 creates `<save dir>/Elite (Europe).save0.d64`
(blank, volume name SAVE DISK 0) and swaps it into drive 8 (by the code, a second press swaps
back). Elite
then saves `ABC` to it with the KERNAL. On unload VICE writes it as `.save0.d64.gz`: 569 bytes,
gunzipping to a standard 174848-byte d64 (a blank save disk compresses to 272 bytes). All four
cores' save disks are byte-identical after gunzip. A sync service has to expect a gzip-wrapped
disk image with the `.gz` suffix kept after `.d64`.

The disk menu is on `@`, which in VICE's default positional keymap is the host's `[` key.
`retro-run` has no name for that key; the patched runner sends it as `key kc91` (raw RETROK
code). The disk menu defaults to tape ("TAPE ACCESS MENU"); option 3 switches it to disk.

## Frodo

- Content: `d64|t64|x64|p00|lnx|lyx|zip` only. No `.g64`, `.nib`, `.crt` or `.tap`, so nothing in
  the No-Intro C64 sets loads as shipped; disks need a lossy conversion to `.d64`, which loses the
  copy protection.
- The drive is emulated at DOS level (`Emul1541Proc` is false and not an option), so custom
  fast loaders fail even where the protection would pass.
- No autostart: a script must type `LOAD"*",8,1` and `RUN` (positional keymap: `"` is shift+2,
  `*` is host `]`, sent as `key kc93`).
- The joystick is the numeric keypad (KP8/2/4/6, KP0 fire, `key kc256`...); the RetroPad does not
  move it in the default mode. The attempt is `work/c64/frodo-sg.txt` (not filed: it fails).
- Writes: `ImageDrive` opens the image `r+b` and writes sectors in place (`1541d64.cpp`); not
  exercised by a game here.

## Files the cores write besides saves

- VICE writes `vice/vicerc-dump-C64` (a resource dump) into the **system** directory on every
  start, and leaves an empty `TEMP/` in the save directory. Neither is a save; not filed.

## Harness notes

- `retro-run` cannot send keys outside its name table; the patched copy in `work/msx/retro-run-x`
  adds `key kcN` (raw RETROK code; `#` would start a comment) and `--keep-temp DIR`.
- `work/c64/make-save-x.py` files new files in the save directory and beside the content, and
  replaces a content file the core modified with `<name>.changes.json` (never a full game image).

## Work disk (not working under retro-run)

`vice_work_disk = 8_d64` should create and attach `<save dir>/vice_work.d64` when the content is not
a floppy. Set from the start in an options file (tried with the Elite tape), no file was created
and no "Work disk" log line appeared in 20000 frames: `update_work_disk()` runs only from
`retro_run` when `request_update_work_disk` is set, which in this harness never happened.
Possibly it needs the option to change while running, as in RetroArch's menu. Not pursued.

## Downloaded entries and leads (MiSTer, openFPGA, x64dtv)

Nothing filed. Searched the cores' GitHub repos, issues and comments, Main_MiSTer, misterfpga.org
(403 to fetches; mirror attachments need a login), Reddit, archive.org.

- **c64-mister**: README: "C1541 implementation works in raw GCR mode (D64 format is converted to
  GCR and then back when saved)", saved in the background, images inside a zip read-only. Issue
  #92 (2021): a written D64 grew from 174848 to 177152 bytes (a padding "tail", fixed in Main).
  EasyFlash saves since 2025-08 (issue #137): `saves/C64/<crt>.sav`, "the same as
  original cartridge, so can be renamed to crt", trimmed to the 64-byte CRT header plus the
  non-0xFF CHIP packets; manual "Save cartridge" and an Autosave option. Leads, downloaded to
  `.cache/downloads/c64/mister-empty-*` but not filed (blank disks, not saves, and the
  attribution is inference): the repo's `releases/Empty.g64` (333744 bytes, name MISTER, ID 99,
  raw unaligned GCR, sha1 5e5694dd…), `Empty.d64` (174848, sha1 a45a5fc3…), `Empty.d81`
  (819200, sha1 e0684834…).
- **markus-zzz-myc64** (Pocket): the 1541 is "(currently read-only)", G64 only, no nonvolatile
  slot: it saves nothing.
- **vice-x64dtv**: no SRAM; the floppy write-protection and work-disk options are compiled out
  for DTV (`#if !defined(__X64DTV__)`), the M3U `#SAVEDISK:` support is not. Nothing found.
