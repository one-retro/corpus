# Atari 2600

No retail 2600 game saves, and the library is the No-Intro retail set (482 games, no homebrew). The
2600's save device is the **SaveKey/AtariVox**: a 32 KiB 24LC256 I2C EEPROM in joystick port 2,
shared by every game, each using its own 64-byte pages (github.com/atariage-community/savekey-allocation-list).
Homebrew uses it, so this system's entries are two homebrew games whose authors give them away,
downloaded from their GitHub releases. 3 entries filed out of 8 attempts.

## The games

| Game | Author, source, licence | What it saves |
| --- | --- | --- |
| Paul's HappyBird v1.08 (NTSC, PlusROM build), `happybird-v1.08-NTSC-PLUSROM.bin`, 16 KiB F6 | Bruno Steux, 2023. github.com/steux/happybird release v1.08. GPL-3.0 | the high score, 2 bytes at SaveKey 0x1480, written at game over. Script: pass the first pipes (score 1) and crash |
| Grizzards v1.1 (NTSC), `Grizzards.NTSC.a26`, 64 KiB EF | Bruce-Robert Pocock, 2022. github.com/brpocock/grizzards release v1.1. CC BY-NC-SA 4.0 (`COPYING`; the cart is commercially licensed to AtariAge, the ROM is on GitHub by the author) | three game slots; a new game writes slot 1 at once (0x1100-0x11E3, starting "GRIZ0"). Script: name BAAAAA, take Aquax, BEGIN; reset shows RESUME BAAAAA SLOT 1. The game refuses to start without a SaveKey |

Each `provenance.json` has `"rom_source"` with the download URL. The ROMs stay in `.cache/downloads/`;
the folder name is the release's file name. Gate Racer II (Atarius Maximus, 2013; best time saved
on any crash) was the third candidate, but its only source is an AtariAge forum attachment, and
AtariAge answers non-browser requests with HTTP 403: blocked, not used.

## Games x cores

| Game | stella | stella-2014 | stella-2023 | tia |
| --- | --- | --- | --- | --- |
| HappyBird | `cwd/savekey_eeprom.dat`, 32768 | failed: runs, no SaveKey | `cwd/savekey_eeprom.dat`, 32768 | failed: runs, no SaveKey |
| Grizzards | failed: "MEMORY DEVICE NEEDED 00F497" at BEGIN | failed: same message at boot | `cwd/savekey_eeprom.dat`, 32768 | failed: black screen |

Builds: stella = Stella 8.0_pre b52ccb02e, stella-2023 = Stella 7.0_pre ba52c43, stella-2014 = Stella
3.9.3 7d1361e, tia = tia 20+6ae5bf9. HappyBird's two files are byte-identical (sha1 ffcb649c...):
0xFF everywhere except `00 01` at 0x1480. Grizzards' file is 0xFF except 210 bytes in 0x1100-0x11E3.

## Where each core keeps the SaveKey

None of them uses the libretro save RAM interface: no 2600 core here has a `.srm`.

- **stella and stella-2023: `savekey_eeprom.dat` in the frontend's current working directory**, 32768
  bytes, initialised to 0xFF, written when the game is unloaded, one file for every game. Both
  detect the SaveKey on their own for these two ROMs (port 2 set to SaveKey/AtariVox). Their libretro
  file layer (`FSNodeLIBRETRO`) maps Stella's `./nvram/` to `./`, so the file is `./savekey_eeprom.dat`,
  not `./nvram/...` as these notes said before. `make-save.py` files what the core wrote into
  its working directory under `cwd/` in the entry, and `--rom-source` records where the ROM came
  from (`rom_source`). In RetroArch the file lands in whatever directory RetroArch was started from.
- **The file is never read back.** `FSNodeLIBRETRO::read` returns the loaded ROM image whatever path
  is asked for, and the EEPROM class accepts a data file only if it is exactly 32768 bytes. With a
  16 or 64 KiB ROM the SaveKey therefore starts blank on every boot (and, flagged as changed, is
  rewritten at every unload). Tested: with HappyBird's saved `savekey_eeprom.dat` copied into the
  working directory, a fresh boot shows HIGH 000 in both cores. From the code, not tested: a 32 KiB
  ROM would get its own ROM bytes as SaveKey contents.
- **Reset differs.** After a libretro reset stella-2023 keeps the EEPROM in memory (HappyBird shows
  HIGH 001, Grizzards RESUME BAAAAA); stella rebuilds the console, rereads the "file" and starts
  blank (HIGH 000). So HappyBird's script proves the save on the game-over screen, before any reset.
- **stella fails Grizzards' save.** Stella 8.0_pre finds the device at boot (SELECT SLOT appears), but
  after BEGIN the game reports "MEMORY DEVICE NEEDED 00F497" and only 7 bytes (zeros, 0x1130-0x1136)
  reach the file; Stella 7 (stella-2023) writes the whole slot. Stella 8 replaced the old `MT24LC256`
  class with a templated `MicroChip24LC`; this looks like a regression in it. Not filed.
- **stella-2014: only for the ROMs its 2014 database knows.** It sets the right port from
  `Controller.Right` in its properties and has no detection and no device override. Its database
  marks four titles, all `ATARIVOX` (file `atarivox_eeprom.dat`, working directory): AtariVox Test
  ROM, Man Goes Down (2006 prototype), Strat-O-Gems Deluxe (2005), Juno First (2009, NTSC and
  PAL60). HappyBird runs without a SaveKey; Grizzards stops at "MEMORY DEVICE NEEDED".
- **tia: no SaveKey at all.** HappyBird runs; Grizzards (EF bankswitching) shows a black screen.
- Upstream Stella fixed the libretro file layer on 2026-05-17 (commit 51994c0fe and the base
  directory change): a newer build would write `<savedir>/stella/nvram/savekey_eeprom.dat`. The
  buildbot `stella` used here predates it.

## Cores not runnable here

| Core | Status |
| --- | --- |
| atari7800-mister (MiSTer) | its 2600 mode has a SaveKey port option; saves would be the core's `.sav` (see `atari-7800/NOTES.md`). Nothing found online |
| spiritualized-2600 (openFPGA) | no save support documented; nothing found |

## Leads

- Gate Racer II and its 2024 remake (Atarius Maximus, free ROMs attached to his AtariAge topics
  209959 and 359422): fetchable only with a browser.
- Grizzards' free 32 KiB demo (F4) is on the same GitHub releases page.
- Amoeba Jump: reportedly only the cartridge version saves to a SaveKey, not the free forum ROMs.
- Strat-O-Gems Deluxe (John Payson, 2005), if a free copy with the md5 in stella-2014's database
  turns up, would give a stella-2014 AtariVox file.
- Standalone Stella keeps `nvram/savekey_eeprom.dat` in its own settings folder; not a registry core.
