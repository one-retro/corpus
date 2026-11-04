# SNES

Nine games, 12 runnable libretro cores, 89 played entries (out of 96 attempted runs), plus 8
downloaded entries (MiSTer, Analogue Pocket). The 21 `device-backup` entries under `agg23-snes/`
were filed by someone else, not by this slice.

Firmware: `.cache/bios/snes/` holds `dsp1b.rom` (the No-Intro "DSP1 B (World) (Enhancement
Chip)" dump), plus `dsp1b.program.rom` (its first 6144 bytes) and `dsp1b.data.rom` (its last 2048
bytes). With them the bsnes family boots Super Mario Kart. No filed game needs them.

## The games

| Game (script) | Save hardware | Why |
| --- | --- | --- |
| Legend of Zelda, The - A Link to the Past (USA) | 8 KB SRAM, LoROM | Popular; registering the name "ABC" writes file 1 at once. |
| Chrono Trigger (USA) | 8 KB SRAM, HiROM | Popular; walks out of Crono's house and saves to slot 1 from the world map menu. |
| Super Tetris 3 (Japan) (En) | 2 KB SRAM | The 2 KB size. Registering player "ABC" writes the player record (3 bytes at `$0019`). The game formats SRAM at boot (`00 11 22 .. FF`). |
| SimCity (USA) | 32 KB SRAM | New city "ASDF", saved to slot 2 from LOAD.SAVE. |
| Kaite Tsukutte Asoberu Dezaemon (Japan) | 128 KB SRAM, LoROM | The 128 KB size. ETC. > Stage copy writes about 3.4 KB. On a blank cart the game first fills all 128 KB with its sample game ("S-RAM CHECK!"). |
| Kirby Super Star (USA) | SA-1, 8 KB BW-RAM | SA-1. A Gourmet Race Course 1 time trial writes the best time into the save block at `$1F00` (three copies of `0x51` bytes). The rest of BW-RAM is SA-1 work RAM and changes every frame. |
| Pebble Beach no Hatou New - Tournament Edition (Japan) | SA-1, 64 KB BW-RAM | SA-1 at 64 KB. Renaming member Player-1 to "ABC" writes `ABC` at `$E010`. |
| Daikaijuu Monogatari II (Japan) | S-RTC + 8 KB SRAM, ExHiROM (5 MB) | The clock chip. Sets the clock, sits through the opening, then saves on the save mark in the first cave. About 23.5k frames. |
| (no tenth game) | | See gaps. |

Every script ends with a shot of the save: the slot or record on screen, or a "saved" message.

## Games x cores

✔ filed, ✘ failed (reason below), – not run.

| core | ALttP | CT | ST3 | SimCity | Dezaemon | KSS | Pebble | Daikaijuu II |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| snes9x | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ `.rtc` 20 |
| snes9x-2010 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ `.rtc` 20 |
| snes9x-2005-plus | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ no RTC (a) |
| snes9x-2005 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✘ (b) |
| snes9x-2002 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✘ segfault on load |
| bsnes | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ `.rtc` 16 |
| bsnes-hd-beta | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ no `.rtc` (c) |
| bsnes-mercury (accuracy) | ✔ | ✔ | ✔ | ✔ | ✘ (d) | ✔ | ✔ | ✘ (e) |
| bsnes2014 (accuracy) | ✔ | ✔ | ✔ | ✔ | ✘ (d) | ✔ | ✔ | ✘ (e) |
| higan-super-famicom (x86_64) | ✔ | ✔ | ✔ | ✔ | ✘ (d) | ✔ | ✔ | ✔ `.rtc.ram` 16 |
| mednafen-bsnes | ✔ (f) | ✔ (f) | ✔ (f) | ✔ (f) | ✔ (f) | ✔ (f) | ✔ (f) | ✔ (f) `.rtc` 20 |
| mesen-s (Mesen2) | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ no `.rtc` (g) |
| snes-mister, agg23-snes, timboettiger-pro-action-replay, mednafen, beetle-supafaust, bsnes-jg, chimerasnes, higan-super-famicom-balanced | not runnable here |

Notes on the table:

- **(a)** snes9x-2005 and snes9x-2005-plus have no S-RTC. The game says 時刻の入力に失敗しました, ざんねんながらPLGシステムは使用できません ("setting the time failed; the PLG system can't be used") and plays on without a clock. The save is real; there is just no clock to save.
- **(b)** snes9x-2005 behaves as in (a), but the opening runs differently and the run stalls in the green temple room before the cave. A longer mash didn't help, so there is no save. The run was unfiled and noted in status.jsonl.
- **(c)** bsnes-hd-beta's clock runs in-game (the save screen shows 0:02:29), but the core writes no clock file, so the time is lost on reload.
- **(d)** Dezaemon reports "S-RAM BREAK DOWN!". These cores do not map all 128 KB of LoROM SRAM: the game's test pattern lands only in `0x0000-0x7FFF` and `0x10000-0x17FFF`, and the rest stays `0xFF`. The 131072-byte files are not saves. They were moved to `work/snes/rejected/` and noted in status.jsonl.
- **(e)** bsnes-mercury and bsnes2014 refuse to load the S-RTC game unless an `rtc.ram` exists in the *system* directory ("Cannot find requested file in system directory: .../system/rtc.ram"). Given a 16-byte `rtc.ram`, both crash with SIGTRAP right after "Load BIOS".
- **(f)** mednafen-bsnes (Mednafen bSNES v0.9.26) does not hand battery RAM to the frontend: libretro save RAM size is 0. It writes its own `<stem>.srm`, and a `<stem>.rtc` for every game, into the save directory. It then aborts (SIGABRT) while unloading, after the files are written, so make-save.py records the run as failed. These entries were filed from the run directory by `work/snes/file_aborted.py`; the note in provenance says so.
- **(g)** Mesen2 runs the S-RTC game, but the clock reads 0:00:00 throughout and the core writes no clock file.

## What differs between the cores' files

**Names.** Every core writes `<rom stem>.srm`. The clock files differ:
- `<stem>.rtc`: bsnes, snes9x, snes9x-2010, mednafen-bsnes.
- `<stem>.rtc.ram`: higan. The core writes this file itself, not the frontend.
- An empty `<stem>.rtc` for *every* game: mednafen-bsnes (0 bytes for the games without a clock).
- No clock file: bsnes-hd-beta, mesen-s, snes9x-2005-plus.

**Sizes.** Every core that ran a game wrote the same `.srm` size, and it is the header's size: 2048, 8192, 32768, 65536 or 131072.

**Fill of untouched SRAM.** This is the main difference, and it makes otherwise equal saves differ byte for byte:

| Cores | Fill |
| --- | --- |
| bsnes, bsnes-hd-beta, bsnes-mercury, bsnes2014, higan, mednafen-bsnes | `0xFF` |
| snes9x, snes9x-2010 | `0x60` (snes9x's SRAM initial value) |
| snes9x-2002, snes9x-2005, snes9x-2005-plus | `0x00` |
| mesen-s (Mesen2) | Random bytes (its default RAM power-on state), so its files differ from run to run |

In ALttP, for example, `0x1E00-0x1FFF` is `FF…` in bsnes, `60…` in snes9x, `00…` in snes9x-2002 and noise in Mesen2. The game data itself agrees.

Games that format all of SRAM themselves come out byte-identical across all cores that ran them:
- Super Tetris 3: 12 cores, sha1 `af7270c9…`.
- Dezaemon: 9 cores, `fe972f66…`.

**SA-1 BW-RAM.** It doubles as work RAM, so KSS files differ between cores even where the record is identical (10 distinct sha1s out of 12; bsnes = bsnes-hd-beta and bsnes-mercury = bsnes2014). The record block at `$1F00` is what to compare. The recorded time also varies by a fraction of a second between cores: most show 01:00:94, a few are slightly slower.

**RTC layouts (Daikaijuu II).** The game was set to 1996-08-02 00:00, so the default clock. The S-RTC digit order is: seconds lo/hi, minutes lo/hi, hours lo/hi, day lo/hi, month, year lo/hi, century, weekday.
- **bsnes, higan:** 16 bytes. 8 bytes of registers, two BCD digits per byte (e.g. `30 02 00 02 68 99 05 00` = 00:02:30, day 2, month 8, '96, century 9, weekday 5), then an 8-byte little-endian Unix time.
- **snes9x, snes9x-2010, mednafen-bsnes:** 20 bytes. 16 bytes with one digit per byte, then a 4-byte little-endian Unix time. The three padding bytes after the weekday are `00` in snes9x and `FF` in mednafen-bsnes.
- **snes9x's clock** runs far too fast under retro-run, about 6 clock-seconds per frame: its save shows 11:55:40 where bsnes shows 0:02:29. snes9x-2010 keeps time (0:02:31).

**Chips, as far as these runs show:**
- **SA-1:** every core, snes9x-2002 included.
- **S-RTC:** bsnes, higan, snes9x, snes9x-2010 and mednafen-bsnes keep a clock. bsnes-hd-beta ticks but does not save it. Mesen2 does not tick. snes9x-2005 and 2005-plus have none. snes9x-2002 crashes on this 5 MB ExHiROM. bsnes-mercury and bsnes2014 cannot load it (e).
- **SPC7110 + RTC (Tengai Makyou Zero):**
  - On a blank SRAM the game runs Hudson's "SPC7110 CHECK PROGRAM" and needs A, `reset`, B, `reset`.
  - bsnes passes both modes and boots.
  - snes9x fails "RTC TIME NG" forever.
  - Mesen2 fails the Mode 2 RTC backup check; its `.rtc` there is 24 bytes (16 one-digit registers, then an 8-byte big-endian time).
  - Momotarou Dentetsu Happy (SPC7110 without RTC) passes the check program on snes9x.
- **128 KB LoROM SRAM:** see (d).

## Gaps and attempts

**Not done**
- **SuperFX: no entry.**
  - *Yoshi's Island:* the run gets past the first pillar of 1-1, then hits a taller wall.
  - *Stunt Race FX:* Speed Trax Easy Ride is reachable, but blind throttle patterns either crash or finish too slowly. bsnes and snes9x also drift apart from the same inputs (GSU timing).
  - *Winter Gold:* the menu won't accept a selection in snes9x.
  - Note that the GSU RAM is work RAM, so snes9x writes 32 KB for Yoshi's Island and 64 KB for Stunt Race FX.
- **Tengai Makyou Zero:** boots in bsnes (script start in `work/snes/dev/tmA-boot.txt`), but no save point was found in the first village.
- **Tenth game:**
  - *Super Mario Kart* (DSP-1, 2 KB): boots in bsnes with the firmware, but a blind 5-lap time trial was too slow to develop.
  - *Harvest Moon:* the OK in name entry could not be reached.
  - *EarthBound:* the home phone only says "Beeeep...".
  - *Kirby's Dream Land 3:* a new file is not written until a stage is cleared.
  - *Ultima Runes of Virtue II* and *FF Mystic Quest:* long openings.

**Leads**

Downloaded, inspected, not filed (not clearly attributable):
- **SNES_MiSTer issues:**
  - [#54](https://github.com/MiSTer-devel/SNES_MiSTer/issues/54): Secret of Mana northtown save; the poster also refers to original hardware.
  - [#53](https://github.com/MiSTer-devel/SNES_MiSTer/issues/53): Super Mario RPG, 32 KB, origin not stated.
  - [#138](https://github.com/MiSTer-devel/SNES_MiSTer/issues/138): `tmz_english_beginning.sav`; the poster compares bsnes and MiSTer.
  - [#59](https://github.com/MiSTer-devel/SNES_MiSTer/issues/59): Marvelous 1.07 translation, 65536 bytes, a patched ROM.
  - [#313](https://github.com/MiSTer-devel/SNES_MiSTer/issues/313): `SOE.sav` in the issue body, renamed.
  - [#72](https://github.com/MiSTer-devel/SNES_MiSTer/issues/72): a 100% Yoshi's Island `.srm`, from an emulator.
  - [#364](https://github.com/MiSTer-devel/SNES_MiSTer/issues/364): Trials of Mana, taken from fantasyanime.com.
- **openfpga-SNES:** [#43](https://github.com/agg23/openfpga-SNES/issues/43) `Saves.zip` holds 8 KB starter saves for the SPC7110 games, which the Pocket core needs to get past its check. Their origin is not stated.

Not found: anything attributable to standalone Mednafen, Supafaust, bsnes-jg, ChimeraSNES, higan balanced or the Pro Action Replay core. What was searched:
- **GitHub:** issue and comment text of agg23/openfpga-SNES and MiSTer-devel/SNES_MiSTer, all of it pulled through `gh api`.
- **Web:** searches for the cores' save attachments.

Two facts from that search:
- **MiSTer SPC7110 clock:** reads the host's real time ([#139](https://github.com/MiSTer-devel/SNES_MiSTer/issues/139)).
- **MiSTer fill bug:** early-2020 builds filled only every other byte of fresh SRAM with `FF` ([#189](https://github.com/MiSTer-devel/SNES_MiSTer/issues/189)). The downloaded Illusion of Gaia save shows exactly that `FF 00` pattern.

## Downloaded entries

| core | game | files | what |
| --- | --- | --- | --- |
| agg23-snes | Chrono Trigger (USA) | `... - Reboot1.sav`, `... - Reboot2.sav` (8192, identical), `... - End.sav` (65536) | From [openfpga-SNES #2](https://github.com/agg23/openfpga-SNES/issues/2). End is the corrupt 64 KB file the Pocket left after "Load SMC" (firmware bug). |
| agg23-snes | Donkey Kong Country (USA) (Rev 2) | Reboot1/Reboot2 (2048, identical), End (8192) | Same thread. The Doom "save" in the zip is byte-identical to the DKC one, so it is not filed. |
| snes-mister | Chrono Trigger (USA) | `Chrono Trigger (U) [!].sav` 8192 | Issue #38. |
| snes-mister | Illusion of Gaia (USA) | `.sav` 8192 | Issue #183. Has the `FF 00` fill. |
| snes-mister | Secret of Mana (USA) | `.sav` 8192 | Issue #202. |
| snes-mister | Secret of Evermore (USA) | `.sav` 8192 | Issue #313. |
| snes-mister | Super Mario RPG - Legend of the Seven Stars (USA) | `.sav` 32768 | Issue #39. MiSTer sized BW-RAM from the header (32 KB). |
| snes-mister | Shinseiki Odysselya (Japan) | `.sav` 8192 | Issue #258. |

## Harness and runner notes

- **Aborting cores:** make-save.py treats any non-zero exit as failure, even when the core wrote its saves before aborting (mednafen-bsnes). Workaround: `work/snes/file_aborted.py`.
- **Re-pressing a button:** two `press` lines back to back do not release the button in between, so a second press of the same button needs a gap or another command.
- **Disk:** the disk was full (about 130 MB free) during this run. This slice's scratch was deleted to make room.
