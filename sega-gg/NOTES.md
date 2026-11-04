# Game Gear: notes

## The ten games

Battery games were taken from MAME's `hash/gamegear.xml` (`feature battery`, `dataarea ram`
sizes, `slot eeprom`) and SMS Power's MemoryBackup tag. Picked for save hardware first
(8 KB, 16 KB, 24 KB and 32 KB SRAM, and the 93C46 serial EEPROM), then US/World releases,
then a quick genuine save. Six are Japanese because the US releases with a battery are few
(Crystal Warriors, Defenders of Oasis, Shining Force II, Popils, the baseball EEPROM carts)
and the 16 KB and 24 KB boards exist only on Japanese titles.

| Game (ROM) | Save hardware (MAME) | How the script reaches a save | Proof |
| --- | --- | --- | --- |
| Shining Force - The Sword of Hajya (USA) | 32 KB SRAM | Storyteller START, book 1, name "ABC" (the book is written at naming); reset, CONT. | book list "1 ABC BTL 1" |
| Defenders of Oasis (USA, Europe) | 8 KB SRAM | New Game, the audience with the King; the game autosaves while you play; reset, Continue | "Game 1 LV 1 Chap. 1" |
| Magical Puzzle Popils (World) (En,Ja) | 8 KB SRAM | MAP EDIT round 1, two blocks, SAVE MAP > YES | "SAVE OK" |
| The Majors - Pro Baseball (USA) | 93C46 EEPROM (128 bytes) | 1P PLAY > PENNANT START, 32 games, Toronto (written as the season starts); reset, PENNANT CONTINUE | the saved standings |
| Shining Force Gaiden - Ensei, Jashin no Kuni e (Japan) | 16 KB SRAM | as Sword of Hajya, name "あいうえお"; reset, つづきから | "1 あいうえお バトル 1" |
| Moldorian - Hikari to Yami no Sister (Japan) | 24 KB SRAM | さいしょから, default name ナバル, wake up, menu システム > セーブ > slot 1 | "きろくを おわりました" |
| Eternal Legend - Eien no Densetsu (Japan) | 8 KB SRAM | はじめから, opening at the Hark Inn, menu システム > セーブ > 1 | "セーブ しました!!" |
| Nazo Puyo 2 (Japan) | 8 KB SRAM | QUEST MODE, solve QUEST 001; reset | QUEST MODE "CONTINUE 002" |
| Magic Knight Rayearth (Japan) | 8 KB SRAM | Into Mokona's tent, sleep, セーブしますか? はい, セーブ1 | "セーブしました。いつでも つづきを はじめられます。" |
| Lunar - Sanposuru Gakuen (Japan) | 8 KB SRAM | はじめから, the opening, menu セーブ, book 1, はい | save list, book 1 now "だい2しょう" |

Tried and dropped (each fought for more than a few attempts): Crystal Warriors (saves only
at a town inn, reached by winning or crossing the first battle map), World Series Baseball
(the pennant is not written until a game is played; TEAM EDIT is long), Phantasy Star
Gaiden and Sylvan Tale (no save in the field menu; save spot not found quickly), Shining
Force Gaiden - Final Conflict (a long prologue no button skips), Taisen-gata Daisenryaku G
(開始 needs a setup first), Pet Club Inu Daisuki (no save after creating owner and dog),
Madou Monogatari I, Megami Tensei Gaiden Last Bible, Magic Knight Rayearth 2.

## Games x cores

39 of 40 (game, core) pairs filed, each checked against its proof.png. Core versions:
Genesis Plus GX v1.7.4 f27655b, Genesis Plus GX Wide v1.7.4 b7ad005, Gearsystem
3.9.24-9-gf1202e8, SMS Plus GX 1.8 3844b46.

| Game | genesis-plus-gx | genesis-plus-gx-wide | gearsystem | sms-plus-gx |
| --- | --- | --- | --- | --- |
| Shining Force - The Sword of Hajya | 26752 | 26752 | 32768 | 32768 |
| Defenders of Oasis | 3840 | 3840 | 32768 | 32768 |
| Magical Puzzle Popils | 8192 | 8192 | 32768 | 32768 |
| The Majors - Pro Baseball | 49 | 49 | **128** | failed: hangs (black screen after the MLBPA logo), no EEPROM |
| Shining Force Gaiden | 16384 | 16384 | 32768 | 32768 |
| Moldorian | 32768 | 32768 | 32768 | 32768 |
| Eternal Legend | 720 | 720 | 32768 | 32768 |
| Nazo Puyo 2 | 8192 | 8192 | 32768 | 32768 |
| Magic Knight Rayearth | 8192 | 8192 | 32768 | 32768 |
| Lunar - Sanposuru Gakuen | 1026 | 1026 | 32768 | 32768 |

(file sizes in bytes; every entry is one `<ROM stem>.srm`)

The Majors on sms-plus-gx was first filed by the runner (it wrote a 32 KB file of zeros with
one non-zero byte, which passed the blank check) and then removed by hand: its proof was
black, the game never reached its menus. status.jsonl still has that run's line.

Not runnable here, nothing filed: drizzt-gg (openFPGA), mednafen (standalone), sms-mister
(MiSTer), spiritualized-gg (openFPGA).

## How the cores' files differ

- **The EEPROM cart.** The Majors stores its season in a 93C46 serial EEPROM, not SRAM.
  Gearsystem writes exactly the EEPROM: 128 bytes. Genesis Plus GX keeps the EEPROM in its
  SRAM buffer and trims trailing 0xFF as usual, giving 49 bytes that equal the first 49 of
  Gearsystem's file (the rest is 0xFF). SMS Plus GX does not emulate it at all. Three cores,
  three outcomes for one cart, and a 128-byte .srm is the only "true" size.
- **Size.** Gearsystem and SMS Plus GX always write 32 KB, whatever the board (8, 16, 24 KB
  or EEPROM). Genesis Plus GX writes up to the last non-0xFF byte, so the file size follows
  what the game wrote: 720 (Eternal Legend), 1026 (Lunar), 3840 (Defenders of Oasis, which
  fills unused space with 0xFF itself), 16384 (Shining Force Gaiden fills its 16 KB),
  26752 (Sword of Hajya), 32768 (Moldorian clears the full 32 KB window, more than MAME's
  24 KB board).
- **Fill.** Genesis Plus GX and Gearsystem start the cart RAM as 0xFF, SMS Plus GX as 0x00;
  untouched bytes keep the fill. Where the game formats its whole area (Popils "BACKUP
  INITIALIZED" 8 KB, Defenders of Oasis 8 KB, Nazo Puyo 2) Gearsystem and SMS Plus GX agree
  inside it and differ only beyond (0xFF vs 0x00 from 0x2000).
- **Content.** GPGX and Gearsystem agree byte for byte over the GPGX length for Sword of
  Hajya, Popils, Eternal Legend, Lunar, Rayearth and Nazo Puyo 2. Small game-state
  differences: Defenders of Oasis 46 bytes (the autosave caught a different moment),
  Moldorian 4, Shining Force Gaiden 1 (offset 0x22BC, 0xE9 vs 0xE8, also the only place the
  two GPGX builds ever differed).
- **Files without a battery.** SMS Plus GX writes a 32 KB all-zero .srm for any Game Gear
  game, e.g. Sonic The Hedgehog (tried outside the corpus).
- **States carry no SRAM** in GPGX; scripts all run from power-on. Several games ignore a
  press made right after a state loads.

## Downloads and leads

Nothing filed as downloaded. Searched: spiritualized1997/openFPGA-GG issues, MiSTer
SMS_MiSTer issues and source, misterfpga.org, euan-forrester/save-file-converter.

- save-file-converter `Mister/GameGear.js`: "The MiSTer makes saves that are 64kB in size and
  the emulator I tried makes saves that are 32kB." No MiSTer Game Gear file in its test data.
  Current SMS_MiSTer source uses a 32 KB 0xFF-initialised backup RAM saved in 64 x 512-byte
  blocks, and has EEPROM mapper support, so newer MiSTer GG saves are probably 32 KB.
- spiritualized1997/openFPGA-GG issue #9 is a cart-dumping request, no saves.

## Harness problem (worked around)

At 23:37 `tools/retro-run/retro-run.c` was rebuilt with a disk-control change whose
`ENV_SET_DISK_CONTROL_INTERFACE` handler `memcpy`s from `data` without a NULL check. Genesis
Plus GX calls it with NULL at load, so every GPGX run crashes (SIGSEGV, rc 139). Entries up
to Magic Knight Rayearth were filed with the earlier harness. For Lunar and The Majors I built
`work/sega-gg/retro-run` from the same source with one line added (`if (!data) {
have_disk_cb = false; return true; }`) and ran `work/sega-gg/make-save-local.py`, a copy of
`tools/make-save.py` that uses it. Nothing else differs; provenance still says retro-run.
