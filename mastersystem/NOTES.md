# Master System: notes

## The games, and why only eight

Only eight Master System cartridges released outside Japan have battery-backed RAM, and all
eight are in the library, so all eight are here. Three sources agree on the list: MAME's
`hash/sms.xml` (`feature battery`), SMS Power's MemoryBackup tag
(https://www.smspower.org/Tags/MemoryBackup) and Retro Sales' list. The other battery
carts are Japanese versions of these same games (Haja no Fuuin, Doki Doki Penguin Land,
Phantasy Star and Ys for the Mark III), and the 1G1R set holds only the
export versions, so there is no ninth or tenth game to add. All eight carts have one 8 KB
SRAM, so there is no variety of save hardware to be had on this system; the variety is in
how each game uses the 8 KB and in what each core writes around it.

| Game (ROM) | How the script reaches a save | Proof |
| --- | --- | --- |
| Phantasy Star (USA, Europe) (Rev A) | New game, Nero's death, field menu SAVE, slot 1, name "ABC"; reset, CONTINUE | slot list "1 ABC" |
| Ys - The Vanished Omens (USA, Europe, Brazil) (En) | New game starts in Minea; button 2 menu, SAVE DATA, slot 1 | "Finished." / "1 MINEA" |
| Ultima IV - Quest of the Avatar (Europe, Brazil) (En) | Avatar "ABC", the gypsy's seven questions, Camp > Save, record 1 | Records of Journey "ABC Level 2", "Done." |
| Miracle Warriors - Seal of The Dark Lord (USA, Europe, Brazil) (En) | Hero "ABC", menu QUIT > SAVE > SAVE 1; reset, CONTINUE NO.1 | ABC loaded back on the beach |
| Golden Axe Warrior (USA, Europe, Brazil) (En) | Hero "ABC", walk west into the village inn, the elder: YES, FILE NO. 1 | "Your game data is saved." FILE NO. 1 ABC |
| Monopoly (USA, Europe) (Rev A) | Players A and B, roll for first, MORE OPTIONS > SAVE GAME | "GAME SAVED" |
| Golfamania (Europe, Brazil) (En) | Stroke play, new golfer "ABCDEFGH", first tee (the record of play is written as the round starts); reset, STROKE PLAY > CONTINUE | ABCD back on the first tee |
| Penguin Land (USA, Europe) | EDITOR, three bricks, palette SAVE-01; reset, EDITOR, LOAD-01 | the three bricks loaded back |

Scripts: `scripts/mastersystem/<short title>.txt`; Monopoly also has
`Monopoly.picodrive.txt` and `Monopoly.sms-plus-gx.txt` (see below).

## Games x cores

All 40 (game, core) pairs on the runnable cores are filed, each checked against its
proof.png. Core versions: Genesis Plus GX v1.7.4 f27655b, Genesis Plus GX Wide v1.7.4
b7ad005, Gearsystem 3.9.24-9-gf1202e8, PicoDrive 2.05-1890c29, SMS Plus GX 1.8 3844b46.

| Game | genesis-plus-gx | genesis-plus-gx-wide | gearsystem | picodrive | sms-plus-gx |
| --- | --- | --- | --- | --- | --- |
| Phantasy Star | 8188 | 8188 | 32768 | 32768 | 32768 |
| Ys | 8191 | 8191 | 32768 | 32768 | 32768 |
| Ultima IV | 8192 | 8192 | 32768 | 32768 | 32768 |
| Miracle Warriors | 1536 | 1536 | 32768 | 32768 | 32768 |
| Golden Axe Warrior | 8191 | 8191 | 32768 | 32768 | 32768 |
| Monopoly | 8192 | 8192 | 32768 | 32768 (own script) | 32768 (own script) |
| Golfamania | 8192 | 8192 | 32768 | 32768 | 32768 |
| Penguin Land | 7201 | 7201 | 32768 | 32768 | 32768 |

(file sizes in bytes; every entry is one `<ROM stem>.srm`, no other files)

Not runnable here, nothing filed: crabemu (standalone), drizzt-sms (openFPGA), emux-sms
(libretro, no macOS build), mednafen (standalone), megadrive-mister and sms-mister (MiSTer),
spiritualized-sms (openFPGA). See "Downloads and leads".

## How the cores' files differ

- **Size.** Gearsystem, PicoDrive and SMS Plus GX always write 32 KB (the largest Sega-mapper
  cart RAM) although every one of these carts has 8 KB. Genesis Plus GX (both builds) writes
  only up to the last byte that is not 0xFF: its libretro `retro_get_memory_size` scans the
  64 KB SRAM buffer backwards for a non-0xFF byte while the game runs. So its file size
  depends on what the game wrote: 1536 (Miracle Warriors touches 0x000-0x5FF only), 7201
  (Penguin Land), 8188, 8191, 8192. A sync service cannot infer the cart's RAM size from a
  GPGX file, and the same game can produce different sizes on different days.
- **Fill.** Genesis Plus GX and Gearsystem power the cart RAM on as 0xFF; PicoDrive and SMS
  Plus GX as 0x00. Bytes the game never writes keep that fill, so the four 32 KB files differ
  from 0x2000 to 0x7FFF (0xFF vs 0x00), and also inside the first 8 KB wherever the game
  leaves holes (Ys bytes 0x00-0x0F, Penguin Land and Miracle Warriors most of the 8 KB).
- **Content.** Phantasy Star clears 0x0000-0x1FFB itself, so all five files are identical
  there and differ only in fill after it. For Golden Axe Warrior and Penguin Land the
  0xFF-fill pair (GPGX, Gearsystem) agree byte for byte over the GPGX length and the 0x00-fill
  pair (PicoDrive, SMS Plus GX) are identical files; the two pairs differ only in holes the
  game never wrote. Elsewhere the cores also differ in a few dozen bytes of game state (Ys
  111 bytes between GPGX and Gearsystem, Monopoly 71, Ultima IV 43, Golfamania 16, Miracle
  Warriors 2) because the game was in a slightly different state when it saved (timers,
  RNG, positions), not because of the format. The two Genesis Plus GX builds always wrote
  identical files.
- **Monopoly and zero-filled RAM.** Monopoly treats all-zero cart RAM as a valid saved game.
  On PicoDrive and SMS Plus GX (zero fill) the title asks PLAY SAVED GAME / PLAY NEW GAME and
  MORE OPTIONS gains a PLAY SAVED GAME line before SAVE GAME; restoring that "game" shows GAME
  RESTORED over an empty board, and PicoDrive then crashed (SIGBUS, rc -10). Those two cores
  use per-core scripts that pick PLAY NEW GAME and one more line down; their provenance
  carries a note. On 0xFF-fill cores the menus are as on a fresh cart.
- **Files for games with no battery.** Tried outside the corpus (nothing filed):
  SMS Plus GX writes a 32 KB all-zero .srm for every game, even ones with no cart RAM
  (Alex Kidd in Miracle World). For Desert Speedtrap, which has 8 KB of work RAM but no
  battery, Genesis Plus GX writes an 8189-byte .srm and PicoDrive and SMS Plus GX a 32 KB
  .srm full of the game's work data (7649 non-fill bytes); Gearsystem writes nothing. The
  Terminator (32 KB work RAM, no battery) got a .srm only from SMS Plus GX (all zero) in the
  first 30 seconds. A sync service will see "saves" for games that cannot save.
- **States carry no SRAM.** A Genesis Plus GX save state loaded into a fresh run does not
  restore cart RAM (Phantasy Star's header was missing, Monopoly menus differed), so every
  script runs from power-on.

## Downloads and leads

Nothing filed as downloaded. Searched: GitHub issues of MiSTer-devel/SMS_MiSTer and
spiritualized1997/openFPGA-SMS, the misterfpga.org forum ("What Games Save?"),
euan-forrester/save-file-converter (test data and format notes), general web searches for
MiSTer/Pocket/mednafen SMS saves. Leads, not files:

- spiritualized1997/openFPGA-SMS issue #10, "Ultima IV ingame save feature doesn't work"
  (and #8, it would not run): a user report, no save attached.
- MiSTer SMS core source (SMS.sv, current master): backup RAM is a 32 KB dpram initialised
  from `rtl/nvram_ff.mif` and written to the .sav in 64 blocks of 512 bytes, so MiSTer
  files should be 32 KB with 0xFF fill; the core now also handles the 93C46 EEPROM mapper.
  save-file-converter's `Mister/Sms.js` says older MiSTer SMS saves were padded to 32 KB with
  0x00. A misterfpga.org post says the core captures the RAM-enable signal and writes a .sav
  for games that never use it (Out Run, Wonder Boy).
- save-file-converter test data holds Phantasy Star saves from an SMS flash cart and from
  SMS Advance (GBA), not from any core in the registry.

## Harness notes

The harness was rebuilt at 23:37 with a change that makes Genesis Plus GX crash at load
(NULL `SET_DISK_CONTROL_INTERFACE`, see `work/sega-gg/`). All Master System entries were
filed before that and were unaffected.
