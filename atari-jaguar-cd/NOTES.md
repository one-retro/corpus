# Atari Jaguar CD

Nothing filed: the ROM library has no Jaguar CD images (searched the ROM folders for
Jaguar CD titles and `jagcd` names; there is no Jaguar CD folder, and the
`jagcd.bin` under `Analogue/Platforms/_images` is a platform picture, not a BIOS or a disc).

## The registry is out of date here

The registry lists no core for `atari-jaguar-cd`, but the current libretro **Virtual Jaguar**
(v3.11.0 34696082, the build used for `atari-jaguar`) runs Jaguar CD discs: HLE or real-BIOS boot
(retail and developer CD BIOS images are built in; `jagcd.bin`, `jaguarcd_bios.bin`, `Jaguar CD
BIOS.bin` and others are picked up from the system directory), CUE/CDI/CHD input, and a
`virtualjaguar_memory_track` option that emulates the **Memory Track** cartridge "alongside the
CD unit, as on real hardware ... its 128 KB NVRAM (stored in the save file)". `virtual-jaguar`
should be added to this system in `cores.json`.

What a Jaguar CD save from that core looks like, from its source (`libretro.c` at 34696082,
`retro_get_memory_size`), not yet seen in a played file:

| Content | `.srm` size | Layout |
| --- | --- | --- |
| a CD disc | 131328 | 0x00000 cart EEPROM (128 B) + 0x00080 CD-unit EEPROM (128 B) + 0x00100 Memory Track NVRAM (131072 B) |
| the Memory Track cart image itself (CRC32 FDF37F47) | 131072 | the NVRAM, raw |

EEPROM words are big-endian, as for cartridges. Before 2026-04 the core instead wrote
`<ROM basename>.cdrom.srm` (128 bytes, the CD-unit EEPROM) beside the cartridge `.srm` (see
`atari-jaguar/NOTES.md`).

## Leads

None searched: no non-runnable registry core exists for this system. BigPEmu (not a registry
core) also emulates the Memory Track; its file format would be worth comparing if Jaguar CD is
ever added.
