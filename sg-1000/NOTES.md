# SG-1000: notes

## No battery saves exist, so nothing is filed

No SG-1000, SC-3000 or Othello Multivision cartridge has battery-backed RAM. Checked
against MAME's `hash/sg1000.xml` (no `feature battery` anywhere; the only carts with RAM
are listed below) and SMS Power's MemoryBackup tag (42 games, all Master System or Game
Gear, none SG-1000/SC-3000). The 74 games in the library's No-Intro SG-1000 set include
none either. Filing ten "saves" here would mean filing blank or fake files, so this
directory has only this note.

What looks like saving on the system, and is not a battery save:

- **Cartridge RAM without a battery.** MAME lists extra RAM on The Castle (8 KB), Othello
  (2 KB), the Taiwanese DahJee/Jumbo/Aaronix boards (8-9 KB), and Home BASIC / Link World
  (32 KB, Level 3 BASIC). It is work RAM and is lost at power-off.
- **SC-3000 BASIC** keeps programs on cassette, not in the cartridge.
- **Terebi Oekaki** (the drawing tablet) has no backup memory.
- **"Memories" on the Analogue Pocket** are save states (spiritualized1997/openFPGA-SG1000
  issue #3 is about The Castle's memories), not cartridge saves.

## What the runnable cores do with these games

Run for 900 frames outside the corpus, nothing filed:

| Game | gearsystem | genesis-plus-gx | bluemsx |
| --- | --- | --- | --- |
| Castle, The (Japan), 8 KB RAM | runs, no save file | runs, no save file | runs, no save file |
| Othello (Japan), 2 KB RAM | runs, no save file | runs, no save file | runs, no save file |
| Flicky (Japan, New Zealand) (Ja), no RAM | runs, no save file | runs, no save file | not tried |

None of the cores invents a .srm for SG-1000 carts, unlike SMS Plus GX on the Master System
(not an SG-1000 core in the registry). genesis-plus-gx-wide is the same code as
genesis-plus-gx and was not run separately.

blueMSX refuses SG-1000 ROMs ("the core refused") unless its `Machines` and `Databases`
folders are in the system directory; with them (as another worker placed them in
`.cache/bios/msx/`, which has `Machines/SEGA - SG-1000`) it runs The Castle and Othello.
A future SG-1000 run on blueMSX needs those folders in `.cache/bios/sg-1000/`.

Not runnable here: colecovision-mister and sms-mister (MiSTer), crabemu (standalone, runs but has nothing to save here),
drizzt-sg-1000 and spiritualized-sg-1000 (openFPGA). Nothing to look for online either,
since there is no battery save for any of them to have written.
