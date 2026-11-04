# Famicom Disk System

There are seven games here, not ten (see "Tried and dropped"). They were played in five cores:
fixnes and rustynes from the registry, plus fceumm, mesen and nestopia, which also run FDS images.

- 28 entries filed out of 35 runs. All 7 RustyNES runs failed (below).
- 7 MiSTer saves were downloaded.

FDS BIOS: `.cache/bios/fds/disksys.rom`, copied from a Pocket's `Assets/nes/common/fds.bios`
(sha1 57fe1bde...).

**The registry is missing cores.** `cores.json` lists fds only for fceux, fixnes, mednafen, nes-mister,
rustynes and spiritualized-nes. fceumm, mesen and nestopia all run FDS images and write FDS saves, in
three different formats. They need `fds` in their `systems`.

## The format each core writes, which is the main finding

Every game here wrote the same disk in every core that saved. Each core's file was rebuilt into a
disk image (by applying the patch, or by stripping fixNES's CRC slots). For all seven games, fceumm,
fixNES, Mesen and Nestopia then give the byte-identical 131000-byte disk. Only the container differs:

| Core | File in the save directory | What it is |
| --- | --- | --- |
| fceumm | `<stem>.srm`, 131000 bytes (65500 x sides) | The **whole disk image**, raw sides with no fwNES header, even when the ROM has one. fceumm exposes the disk image itself as libretro SAVE_RAM. So RetroArch writes the `.srm` on every run, and on a run where the game wrote nothing the `.srm` is byte-identical to the ROM. |
| fixNES | `<stem>.srm`, 131072 bytes (**65536** x sides) | The whole disk in fixNES's own layout. Each side holds its blocks in order, with **a 2-byte slot after every block** (where the disk's CRC would be, always 00 00), zero-filled to 65536. It is not the .fds layout: offsets drift by 2 per block. Like fceumm, it is written on every run, and it does not depend on the ROM header. |
| Mesen | `<stem>.ips`, 17-504 bytes | An **IPS patch** against the ROM *file as loaded*. Written only when the disk changed; Mesen writes no `.srm` for FDS (save RAM 0). With a 16-byte fwNES header on the ROM, every offset moves by 16: Link no Bouken's record is at 0x00D1C9 headerless and at 0x00D1D9 headered. So the same save gives two different patches, depending on how the ROM was dumped. |
| Nestopia | `<stem>.sav`, 30-358 bytes | A **UPS1 patch** in a `.sav` file, against the ROM file as loaded. The input size in the patch is 131000 headerless and 131016 headered. All three CRC32s check. Written only when the disk changed; no `.srm`. |
| RustyNES 3.6.0 | `<savedir>/RustyNES/<sha256 of the ROM file>.fds.sav`, 131000 bytes | A whole image in a subfolder, named by hash, not by ROM name. In all seven games it is **byte-identical to the original disk**: the game's write failed inside RustyNES. Zelda showed "ERR 24". After a reset, F1 Race and Metroid stopped at the BIOS's "DISK TROUBLE ERR.24". **Not filed**: RustyNES does not save FDS games. |
| MiSTer (downloaded) | `<stem>.sav`, 131072 bytes | **16 zero bytes**, then the raw sides (65500 each, no header), then padding to a 512-byte multiple (56 bytes for 2 sides). The padding is zero in 2024 files and stale memory in 2021 files. |

Nestopia has an option for this format: `nestopia_fds_savefile_format`.

- `sav_ups`, labelled "SAV + UPS (Default)", is what was filed here.
- `ups` ("UPS (Standalone Nestopia)") writes `<stem>.ups` with the same bytes.
- `ips` ("IPS (Mesen)") writes `<stem>.ips`, **byte-identical to Mesen's**.
- Both variants were checked on Link no Bouken and kept in `work/fds/nestopia-variants/`. They were
  not filed: one entry per core.

From the cores' sources (via the search agent; not run here):

- FCEUX writes `sav/<rom>.fds`, a full raw image without a header, and only if the disk was written.
- Mednafen writes `sav/<name>.<md5>.fds`, also a full raw image.

## Disk side changes

Zelda no Densetsu keeps its file select and save on side B, so the disk has to be turned over.
`tools/retro-run` has no disk control. The patched runner in `work/nes/runner` adds a `flip` command
(see `nes/NOTES.md` for why there is a patched runner at all):

- **RustyNES** registers the libretro disk control interface, so `flip` sets the image index to
  index XOR 1.
- **fceumm, Nestopia, Mesen and fixNES** register none, so `flip` presses each core's own buttons.
  `work/nes/make-save-alt.py` sets them per core, found by probing:

| Core | Buttons |
| --- | --- |
| fceumm | R (eject), L (next side, only while ejected), R (insert) |
| Nestopia | L ("(FDS) Disk Side Change"; R only ejects) |
| Mesen | R ("Switch Disk Side"); L is "Insert Next Disk", and on a 1-disk game it gives "A B SIDE ERR 07" |
| fixNES | L ("FDS Switch Side") |

So the scripts are shared by all cores.

## The games

| Game (script) | What was saved | Disk file written |
| --- | --- | --- |
| Zelda no Densetsu - The Hyrule Fantasy (Japan) (Collector's Edition) (`Zelda no Densetsu.txt`) | Name アイウ registered in slot 1 | side B, file #28 (id 224, unnamed), 1308 bytes, 7 changed. It needs the side flip. |
| Link no Bouken - The Legend of Zelda 2 (Japan) (Rev 1) (Collector's Edition) (`Link no Bouken.txt`) | "LINK" registered | side A #6 `SAVE-DAT`, 824 bytes, 4 changed |
| Metroid (Japan) (Rev 3) (`Metroid.txt`) | アイウ registered, then the file started (registering alone writes nothing). After a reset the select screen reads it back. | side A #14, 117 bytes, 4 changed. The game also **rewrites that file's header**: id 0x0F becomes 0x0E and the name `SAVEDATA` becomes `01 01 01 01 01 01 01 01`. Anything that finds the save by file name loses it. |
| Famicom Grand Prix - F1 Race (Japan) (DV 1) (Disk Writer) (`Famicom Grand Prix - F1 Race.txt`) | The Disk Writer service form (ナマエ トウロク), name アイウ, "save" | side A #10 `FC_SAVE `, 336 bytes, 226 changed |
| Golf - Japan Course (Japan) (DV 2) (`Golf - Japan Course.txt`) | The same form | side A #7 `DATA    `, 256 bytes, 11 changed |
| Golf - US Course (Japan) (DV 2) (Disk Writer) (`Golf - US Course.txt`) | The same form | side A #8 `DATA    `, 208 bytes, 13 changed |
| Famicom Grand Prix II - 3D Hot Rally (Japan) (DV 8) (Disk Writer) (Famicom 3D System) (`Famicom Grand Prix II - 3D Hot Rally.txt`) | The same form | side A #6 `TDREDATA`, 384 bytes, 19 changed |

The four Disk Writer games share `scripts/fds/_service-form.inc`. The "save" cell is 10 steps right
in F1 Race and 12 in the others. Each of those scripts resets the console and opens the form again,
so the proof shows the name read back from the disk.

`work/fds/fdscheck.py ROM SAVE...` rebuilds the disk from any of these formats and lists the changed
files: whole image, fixNES layout, MiSTer layout, IPS or UPS. `work/fds/checkall.sh` runs it on
every entry.

## Games x cores

| Game | fceumm | fixnes | mesen | nestopia | rustynes | nes-mister | fceux, mednafen, spiritualized-nes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Zelda no Densetsu | F | F | F | F | x (write fails, disk unchanged) | D (Rev 1, not the Collector's Edition) | n/r, nothing found |
| Link no Bouken | F | F | F | F | x | D (Rev 1) | n/r |
| Metroid | F | F | F | F | x | - | n/r |
| F1 Race | F | F | F | F | x | - | n/r |
| Golf - Japan Course | F | F | F | F | x | - | n/r |
| Golf - US Course | F | F | F | F | x | - | n/r |
| 3D Hot Rally | F | F | F | F | x | - | n/r |

## Downloaded entries (`fds/nes-mister/`)

These are birdybro's own MiSTer FDS saves, from github.com/euan-forrester/save-file-converter issue
#80. Most are from 2024 (posted when the converter's author asked for MiSTer FDS saves); Dead Zone and
Akuu Senki Raijin are from a 2021 zip. There are seven:

- Zelda no Densetsu (Rev 1)
- Link no Bouken (Rev 1)
- Akumajou Dracula (Rev 2, Disk Writer)
- Esper Dream (Rev 1, Disk Writer)
- Ginga Denshou (Rev 1)
- Dead Zone
- Akuu Senki Raijin

They were checked with `fdscheck.py` against the No-Intro images where the library has the same
revision:

- Esper Dream: side B `RECORD`, 10 bytes changed.
- Dead Zone: side A `BUFF`, 7 bytes.
- Akuu Senki Raijin: side A `ID`, 6 bytes.
- Akumajou Dracula: the disk is **identical to the original**. It is a MiSTer container with no
  in-game save, and its provenance says so.

The registry does not list agg23-nes for fds. For Spiritualized.NES's FDS saves, FCEUX and Mednafen,
nothing was found online.

## Tried and dropped (timeboxed)

- **Hikari Shinwa (Kid Icarus).** Registering a name writes nothing; `REG SAVE` is written only
  later in play.
- **Akumajou Dracula and Dracula II.** The name registers, but no disk write followed. Dracula saves
  at game over.
- **Nazo no Kabe.** The pointer-driven name menu.
- **Wrecking Crew (1 side).** Its DESIGN > SAVE writes, but with no design the bytes equal the
  original, and the editor would not exit.
- **Famimaga Disk Vol. 3 (1 side).** SAVE with nothing played writes identical bytes.
- **Vs. Excitebike.** Track select would not start.
- **Yume Koujou Doki Doki Panic.** It saves only after a chapter.

A one-sided disk game is the main gap left. fceumm wrote 65500 bytes for one, and the other cores
are untested there.
