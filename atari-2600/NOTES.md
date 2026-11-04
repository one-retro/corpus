# Atari 2600

Nothing filed, and nothing to file from this library: no 2600 game released in the console's
lifetime has save memory, and the library is the No-Intro retail set (482 games, no homebrew,
no aftermarket titles). The only 2600 saves in practice are homebrew high scores on an
**AtariVox/SaveKey** (a 32 KiB 24LC256 I2C EEPROM plugged into joystick port 2) and the flash
of a few modern bankswitching carts. The libretro Stella builds emulate the SaveKey but, as built
on the buildbot today, cannot persist it through the frontend.

## Evidence

All four runnable cores booted Pitfall! (USA) under retro-run, run from a fresh working directory,
and reported **save RAM 0 bytes**; none created any file in the save directory, the system
directory or the working directory.

| Core | Build | Save RAM | SaveKey/AtariVox emulated | Where the EEPROM file would go |
| --- | --- | --- | --- | --- |
| stella | Stella 8.0_pre b52ccb02e (upstream commit of 2026-03-29) | 0 | yes | `./nvram/savekey_eeprom.dat` (or `atarivox_eeprom.dat`) relative to the **frontend's working directory**, and only if that `nvram` directory already exists |
| stella-2023 | Stella 7.0_pre ba52c43 | 0 | yes | same as stella |
| stella-2014 | Stella 3.9.3 7d1361e | 0 | yes | `./savekey_eeprom.dat` in the working directory |
| tia | tia 20+6ae5bf9 | 0 | no (no EEPROM code at all) | none |

How that was established, from the sources at those commits:
- `retro_get_memory_data` in Stella's libretro port returns only `RETRO_MEMORY_SYSTEM_RAM`; there
  is no `SAVE_RAM`, so RetroArch never writes a 2600 `.srm`.
- The SaveKey is `MicroChip24LC<32_KB>`: 32768 bytes, initialised to 0xFF, written to its data
  file in the destructor (when the game is unloaded) through `FSNode::write`. Stella 8 builds that
  path as `nvramDir() / "savekey_eeprom.dat"` (`Console.cxx`).
- In the libretro port at b52ccb02e, `OSystemLIBRETRO::getBaseDirectories` sets the base directory
  to `"./"`; `FSNodeLIBRETRO::makeDir()` returns false and the node has no `write`, so
  `FSNode::write` falls back to a plain `std::ofstream` on `./nvram/savekey_eeprom.dat`. The
  `nvram` directory is never created, so in a normal RetroArch setup the SaveKey contents are lost
  at unload. The test run here confirms no `nvram/` appears in the working directory.
- Stella upstream fixed this on 2026-05-17 (commits 51994c0fe "Make FSNodeLIBRETRO a proper FSNode
  implementation" and the base-directory change): the base directory is now
  `<frontend save dir>/stella/`, so a newer build would write
  **`<savedir>/stella/nvram/savekey_eeprom.dat`** (one file shared by every game, not
  `<stem>.srm`). The buildbot `stella` core used here predates that.
- stella2014 (`libretro/stella2014-libretro`): `MT24LC256` opens `myDataFile` with `ofstream`
  and writes it at destruction if the file did not exist or the data changed; the path is
  `myOSystem->nvramDir() + "savekey_eeprom.dat"`, and the port's `OSystem` never sets
  `myNVRamDir`, so the file lands in the working directory. Its 2014 properties database only
  enables the SaveKey for the homebrew it knew then.
- Stella's newer properties database marks SaveKey games by name, e.g. "Amoeba Jump (2019)
  (SaveKey)", "Bot & Tom (2023) (SaveKey)", "Lode Runner (2022) (SaveKey)"; Stella 6+ also
  auto-detects SaveKey access in the ROM. Carts with their own flash use
  `nvram/<cart name>_flash.dat` / `_eeprom.dat` the same way.

Not tested in a played run: there is no SaveKey game in the library, and fetching one (the
freeware Amoeba Jump from AtariAge) was not possible from here.

## Games x cores

| Game | stella | stella-2014 | stella-2023 | tia |
| --- | --- | --- | --- | --- |
| (none: no game in the library saves) | - | - | - | - |

| Core | Status |
| --- | --- |
| atari7800-mister (MiSTer) | not runnable. Its 2600 mode has a SaveKey port option; saves would be the core's `.sav` (see `atari-7800/NOTES.md`). Nothing found online |
| spiritualized-2600 (openFPGA) | not runnable. No save support documented; nothing found |

## Leads

- A SaveKey file from standalone Stella (`.config/stella/nvram/savekey_eeprom.dat` or
  `Library/Application Support/Stella/nvram/` in the home folder) would show the 32 KiB 0xFF-filled layout, but
  it is not a registry core.
- github.com/atariage-community/savekey-allocation-list: which homebrew uses which SaveKey pages
  (64-byte blocks), useful to label a SaveKey file's contents.
