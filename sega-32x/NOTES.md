# Sega 32X

Only PicoDrive (2.05-1890c29) runs the 32X here; S32X_MiSTer cannot. Three games filed, three
attempted that fit: ten do not exist. The 32X library on the drive has 34 games; only six declare
backup RAM in their cartridge header, and none of the others is known to save.

## The 32X games that save

| Game | Header at 0x1B0 | Here |
| ---- | ---- | ---- |
| World Series Baseball Starring Deion Sanders (USA) | `RA F8 20` 200001-20FFFF, byte-wide SRAM on odd addresses | **filed**: NEW LEAGUE, CONTINUE LEAGUE after reset |
| Golf Magazine Presents - 36 Great Holes Starring Fred Couples (Japan, USA) (En) | `RA F8 20` 200001-20FFFF | **filed**: Player Edit -> NEW PLAYER, listed under Fred Couples |
| NBA Jam - Tournament Edition (World) | `RA E8 40` 200000-200001, serial EEPROM | **filed**: initials record after a full CPU game |
| Knuckles' Chaotix (Japan, USA) (En) | `RA F8 20` 200001-2003FF (512 bytes) | not filed: Data 1 / Auto save starts the prologue, but nothing is saved until a zone is cleared; not reached in the timebox |
| NFL Quarterback Club (World) | `RA E8 40` 200000-200001, serial EEPROM | not attempted past the title (nothing written at boot) |
| Sangokushi IV (Japan) | `RA F8 20` 200001-20FFFF | not filed: Register New Officer reaches the stat screen, but the 70 bonus points must be spent digit by digit before 決定 is enabled |

Checked and without save RAM in the header: the other 28, among them Virtua Racing Deluxe, Star
Wars Arcade, Doom, Virtua Fighter, Stellar Assault (Shadow Squadron), Primal Rage, Tempo, Metal Head.

## Games x cores

| Game | PicoDrive | S32X_MiSTer |
| ---- | ---- | ---- |
| WSB Starring Deion Sanders | 65536 | not runnable |
| Golf Magazine 36 Great Holes | 65536 | not runnable |
| NBA Jam TE | 8192 | not runnable |

## Layouts

PicoDrive treats 32X carts like Genesis ones (see `genesis/NOTES.md`):

- The two SRAM carts are 65536-byte files covering 0x200000-0x20FFFF, byte-expanded: the game's
  bytes on odd offsets, 0x00 on every even one, 0x00 where unwritten. Both games format their save
  area at first boot (last non-zero byte at 0xAFA1 for Golf, 0xFD3B for WSB), so a file exists
  before any play; the scripts go on to a real save.
- NBA Jam TE's EEPROM is an 8192-byte file (PicoDrive gives every EEPROM 0x2000 bytes) holding the
  chip's data in its first 256 bytes ("Snake 1995" at 0x08, records after), 0xFF in unused record
  slots, and zeros from 0x100 on. Same layout as the Genesis NBA Jam's file in PicoDrive ("Snake
  1993").

## Scripts

`scripts/sega-32x/<game>.txt`, Genesis button names (y=A b=B a=C). NBA Jam TE presses Start every
1500 frames through the game: it pauses and unpauses play and is the only button that leaves the
SUBSTITUTION screen between quarters, so the game takes about 74k frames. It is timed for PicoDrive.

## Downloaded and leads

Nothing filed. S32X_MiSTer issue #32 (Chaotix) says the core did not support backup memory as of
2023; a contributor posted an unstable build with SRAM then, and nobody attached a save. No other
source of 32X saves written by a known emulator turned up. save-file-converter's test data has
32X saves from MegaSD and Mega EverDrive Pro flash carts (Chaotix, 36 Great Holes); those are
cartridge dumps, not core output.
