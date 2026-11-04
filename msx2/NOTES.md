# MSX2

Three MSX2 cartridges with SRAM, five entries filed. Same two cores as MSX (blueMSX, fMSX) with
the same behaviour; **read `msx/NOTES.md` first** for where and when each core writes, the
system files, and the input workaround. This file only adds what is MSX2-specific.

## The games

The MSX2 set has 30 SRAM cartridges (blueMSX database match, `work/msx/sramscan.py`): 15 Koei
(32 KiB), 9 ASCII8 + 8 KiB, 5 ASCII16 + 2 KiB, plus Super Lode Runner. Three were scripted:

| Game (No-Intro) | Mapper / SRAM | The save | Proof (last shot) |
| --- | --- | --- | --- |
| Ultima Exodus (Japan) | ASCII8, 8 KiB | なまえ とうろく: register the name いう in roster slot 1 (the first press on あ is taken while the grid opens) | after reset: the roster shows いう |
| Wizardry (Japan) | ASCII8, 8 KiB (512 KiB ROM) | Training Grounds (English text): create ABC, human, good, fighter, KEEP | after reset: typing ABC at the Training Grounds finds L1 G-FIG HUMAN |
| A Ressha de Ikou MSX (Japan) | ASCII16, 2 KiB | new game, Q セーブ: SAVE THE MAP? Y, OK? Y | after reset: NEW GAME? N resumes the map at day 1 (it was saved at day 1, 1 h) |

Tried and dropped: Sangokushi and Genghis Khan-style Koei setups (keys pressed while the game
redraws are lost; the setup never ran reliably), Heroes of the Lance (minutes of unskippable
character introductions before play), Super Daisenryaku and the mahjong/go titles (not tried
in depth). Koei 32 KiB SRAM is covered on MSX1 by Nobunaga no Yabou Zenkoku Ban.

## Games x cores

| Game | bluemsx | fmsx |
| --- | --- | --- |
| Ultima Exodus | filed | filed (bytes identical to blueMSX's) |
| Wizardry | filed | **failed: fMSX never writes this cartridge's SRAM** (below) |
| A Ressha de Ikou | filed | filed with `fmsx_mapper_type_mode = ASCII 16kB` (`scripts/msx2/fmsx-ascii16.opt`); with the guessed mapper the title never takes a key. fMSX draws the map's terrain black, but the game runs and saves |

| Core | Status |
| --- | --- |
| msx-mister (MiSTer) | not runnable; it has no cartridge-SRAM save path at all (only its SD-card VHD is written); nothing found online. See `msx/NOTES.md`, "Downloaded entries and leads" |

## Wizardry and fMSX

Wizardry is a 512 KiB ASCII8 cartridge that pages its SRAM in by writing **0x80** to the bank
registers at 7000h/7800h (the ROM has `LD A,80h / LD (7000h),A` and the same for 7800h, and
nothing else in 40h-FFh). blueMSX's ASCII8-SRAM mapper selects SRAM for any value with a bit
above the ROM mask (`value & ~romMask`); fMSX's ASCII8 code only for `V & (ROMMask+1)`, i.e.
0x40 for a 512 KiB ROM. In fMSX the writes go nowhere: no `.sav` is ever written (not even after
the game's own "copy all data to the S-RAM cartridge" format, boot-prompt option 1), and the
Training Grounds reports "THE ROSTER IS FULL" because the SRAM reads as 0xFF. Forcing
`ASCII 8kB` changes nothing. In blueMSX, the blank 0xFF SRAM is accepted as an empty roster
without the format; after a format the boot prompt gains a third option ("read data from
S-RAM"), so the script skips the format to keep option 2 = start.

## Byte comparison

| Game | bluemsx vs fmsx |
| --- | --- |
| Ultima Exodus | identical 8192 bytes |
| A Ressha de Ikou | 5 of 2048 bytes differ (at 0xEA-0x128; fMSX's game was saved at day 1, 3 h, blueMSX's at day 1, 1 h). Both start `55 AA` and are otherwise mostly 0x00 |

fMSX also wrote `system/CMOS.ROM` (52 bytes) for both its entries, as on MSX1.

## msx-mister on the owner's MiSTer (2026-11-04)

Not run: see `msx/NOTES.md`, "msx-mister and msx1-mister on the owner's MiSTer". The core writes
only its VHD; no cartridge SRAM save exists to make.
