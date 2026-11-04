# Vectrex

Nothing filed. No Vectrex cartridge released by GCE/Milton Bradley (1982-84) has save memory,
and the library (No-Intro, 29 games) is that retail set. The modern exception is homebrew on
**flash cartridges** that the game writes to: Vectrex_MiSTer's README names Malban's Vectorblade
("four-bank 256 KiB flash cartridge ... persistent settings, scores, and game-managed progress")
and Telengard ("persistent character saves at Inns"), on SST39SF020A-style flash. The only
runnable core, vecx, does not emulate cartridge writes.

## Evidence

vecx 1.2 dccff54 booted Scramble (USA, Europe) (vecx has the Vectrex BIOS built in) and reported
**save RAM 0 bytes**; no file appeared in the save, system or working directory. The core's
strings have nothing about SRAM, EEPROM, flash or NVRAM.

## Games x cores

| Game | vecx |
| --- | --- |
| (none: no game in the library saves) | - |

| Core | Status |
| --- | --- |
| vectrex-mister (MiSTer) | not runnable. Supports the 256 KiB flash homebrew with persistent saves, and bundles Vectorblade v1.13 and Telengard v1.03 with the author's permission. That makes it the one Vectrex core that can produce a save; a job for the MiSTer worker. Nothing found online |
| obsidian-vectrex (openFPGA) | not runnable. No save support documented; nothing found |

## Leads

- Vectorblade / Telengard on Vectrex_MiSTer: what the MiSTer writes (the whole 256 KiB flash
  image, or the cart file rewritten in place) is not documented in the README.
