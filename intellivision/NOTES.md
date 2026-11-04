# Intellivision

Nothing filed. No Intellivision cartridge from Mattel, INTV Corp. or the 1980s third parties has
save memory; the console has no battery RAM, and the ECS add-on saved BASIC programs to cassette.
The one modern exception is homebrew on the **JLP** cartridge board (and the LTO Flash!), which
gives games flash "save game sectors"; the library is the No-Intro retail set (144 games) and
has none. The only runnable core cannot save anything.

## Evidence

FreeIntv 1.2 ef3e0fe booted BurgerTime (USA, Europe) and reported **save RAM 0 bytes**; no file
appeared in the save, system or working directory. `src/libretro.c` in libretro/FreeIntv:
`retro_get_memory_data` and `retro_get_memory_size` answer only `RETRO_MEMORY_SYSTEM_RAM`
(0x10000); the core has no JLP flash emulation. So no FreeIntv save is possible for any game.

The run had no BIOS: FreeIntv wants `exec.bin` (8 KiB) and `grom.bin` (2 KiB). The only
Intellivision files on the drive are under a Pocket's `Assets/intv/Spiritualized.Intv`: `exec.intv`
(8208 bytes, a 16-byte-header format, md5 b1c7415f..., not the plain `exec.bin`) and `012.BIN`
(2048 bytes, md5 24b90294..., the Intellivoice `sp0256-012.bin` by Intv_MiSTer's naming, not
the GROM). FreeIntv showed its "LOAD EXEC FAIL / LOAD GROM FAIL" screen. That does not change the
answer: the save-RAM size is fixed at 0 in code, BIOS or not.

## Games x cores

| Game | freeintv |
| --- | --- |
| (none: no game in the library saves) | - |

| Core | Status |
| --- | --- |
| bliss (standalone) | not runnable. Nothing found |
| intv-mister (MiSTer) | not runnable. README lists JLP support "with ... FLASH save game sectors", so a JLP homebrew could make a MiSTer save. Nothing found online |
| spiritualized-intv (openFPGA) | not runnable. No save support documented; nothing found |

## Leads

- JLP homebrew with flash saves (on Intv_MiSTer, or in jzIntv, which keeps JLP flash in a
  separate save-game file; jzIntv is not a registry core) is the only way to an Intellivision
  save file.
