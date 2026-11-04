# Game Boy Color (`gbc`)

Ten games from the No-Intro "Nintendo - Game Boy Color" set, each played from power-on to a
genuine save by one shared script in `scripts/gbc/`, then replayed in every libretro core that
runs here. Link's Awakening DX was done before this pass (8 cores); the other nine add 64 filed
entries out of 72 attempted, so 72 of 80 (game, core) pairs are filed. Every proof.png was
checked by eye.

Cores: as in `gb/NOTES.md` (Gambatte v0.5.0-netlink 77f2567, mGBA 0.11-212-7a12d6d, SameBoy
1.0.5 90e2899, VBA-M 115defb, Gearboy 3.8.20-8-g37d0bf3, TGB Dual v0.8.3 0392c9c, fixGB Alpha
v0.8.2, IroGB v1.0.0). No boot ROMs, no options.

## The ten games

| Game (script) | Cartridge | Save | Why |
| --- | --- | --- | --- |
| Link's Awakening DX (done earlier) | MBC5 + 32 KiB | file 1 registered | popular, the pipeline's first entry |
| Tetris DX (`Tetris DX.txt`) | MBC1 + 8 KiB | ENTRY -> player 1 "AAA" | the GBC set's only MBC1 save; a 10-second save |
| Oracle of Seasons (`Legend of Zelda, The - Oracle of Seasons.txt`) | MBC5 + 8 KiB | NEW GAME, slot 1 "AAA" | popular; 8 KiB MBC5 |
| Pokemon Gold (`Pokemon Gold.txt`) | MBC3 + clock + 32 KiB | clock set to DAY 10:00, SAVE in the bedroom | MBC3 clock, GB-compatible |
| Pokemon Crystal (`Pokemon Crystal.txt`) | MBC3 + clock + 32 KiB | same, CHRIS | MBC3 clock, CGB-only, the clock game everyone syncs |
| Robopon Sun (`Robopon Sun.txt`) | HuC-3 (clock) + 32 KiB | start menu -> Save in Grandpa's lab, "Saved!" | HuC-3, the brief's ask |
| Pokemon Pinball (`Pokemon Pinball.txt`) | MBC5 + rumble + 8 KiB | pause -> SAVE mid-table; title then offers CONTINUE | rumble cartridge type |
| Kirby Tilt 'n' Tumble (`Kirby Tilt 'n' Tumble.txt`) | MBC7: accelerometer + 256-byte EEPROM | the game formats the EEPROM at power-on and writes the tilt calibration on BALANCE | EEPROM, not SRAM; see below |
| Game Boy Wars 3 (Japan) (`Game Boy Wars 3.txt`) | MBC5 + 128 KiB | NEW GAME, DATA1 commander "あ" | the largest GBC battery RAM |
| Harvest Moon GBC (`Harvest Moon GBC.txt`) | MBC3 + clock + 8 KiB | new farm, then sleep: day 1 -> 2 written | the 8 KiB clock variant |

Kirby's save is genuine but small: "TAMA" plus two calibration words. Playing a level needs tilt,
which retro-run cannot give, so file 1 stays empty. Harvest Moon has no save menu; the game keeps
its farm in battery RAM from the new-game setup on and the night's sleep rewrites it (byte 0x188b,
the day, goes 1 -> 2 in every filed core).

## Games x cores

| Game | gambatte | mgba | sameboy | vba-m | gearboy | tgb-dual | fixgb | irogb |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Link's Awakening DX | F | F | F | F | F | F | F | F |
| Tetris DX | F | F | F | F | F | F | F | F |
| Oracle of Seasons | F | F | F | F | F | F | F | F |
| Pokemon Gold | F | F | F | F | F | F | F | F |
| Pokemon Crystal | F | F | F | F | F | F | F | F |
| Robopon Sun | F | F | F | F | F | "Save Err:" in game | segfault | garbage screen (1) |
| Pokemon Pinball | F | F | F | F | F | F | F | F |
| Kirby Tilt 'n' Tumble | refuses (2) | F | F | EEPROM not saved (3) | F | F (4) | segfault | segfault |
| Game Boy Wars 3 | F | F | F | F | F | F | F | F |
| Harvest Moon GBC | F | F | dog in the way (5) | F | F | F | F | F |

1. IroGB fills the screen with "TESTWILL", the game's own failed HuC-3 check.
2. Gambatte: "MBC7 ROM not supported".
3. VBA-M runs Kirby but writes 512 bytes of 0xFF: the EEPROM is never persisted (harness marks
   it blank, not filed).
4. TGB Dual writes 8192 bytes: "TAMA", a zero calibration (no accelerometer), then a 00 FF
   pattern; its level map differs from the other cores'.
5. On SameBoy the farm dog (RNG) sits on the only tile beside the bed's head, so the farmer never
   reaches the bed; a longer push, a detour and waits of 300-1800 frames all failed. Not filed.

## What differs between the cores' files

**Sizes.** All eight write the cartridge's RAM size, 8 KiB to 128 KiB, except MBC7: mGBA, SameBoy
and Gearboy write the EEPROM's 256 bytes, VBA-M 512 (blank), TGB Dual 8192.

**MBC7 byte order.** The 93LC56 holds 16-bit words. mGBA stores them little-endian
(`54 41 4D 41` = "TAMA", calibration `1D 00 1D 00`); SameBoy and Gearboy store them big-endian
(`41 54 41 4D` = "ATAM", `00 1D 00 1D`); TGB Dual like mGBA. The same EEPROM, two byte orders: a
converter has to swap every word.

**Fill.** Gambatte, mGBA, SameBoy, VBA-M, Gearboy and TGB Dual start battery RAM at 0xFF, fixGB
and IroGB at 0x00 (LADX: 29945 bytes differ; Gold: ~5000; Tetris DX: none, the game clears its RAM
itself, so all eight files are identical).

**Clock (`.rtc` sidecar).** Same layouts as on gb (see `gb/NOTES.md`): Gambatte 8 bytes (u64 LE
Unix time of the clock's zero), mGBA / VBA-M / Gearboy 48 bytes for MBC3 (5 x u32 registers,
5 x u32 latched, u64 LE Unix time), SameBoy 32 bytes, TGB Dual 4 bytes for every game including
Tetris DX and Pinball, fixGB and IroGB none (their Gold/Crystal/Harvest Moon clocks are lost when
the core closes). For HuC-3 (Robopon): Gambatte 8, VBA-M 8 (timestamp only), Gearboy 20, SameBoy
32, and **mGBA none**. No core appends the clock to the `.srm`: every `.srm` is exactly the RAM
size. Against one-saves-registry `data/clocks.json`: gambatte (sidecar) agrees; mgba, sameboy
and vba-m are recorded as `appended` with an 8-byte timestamp, but their libretro cores write a
sidecar; gearboy and tgb-dual are not in the file. Gearboy and TGB Dual count the clock in emulated
time, the others in host time (Gold, a 145-second play run in a few real seconds: Gearboy's
registers 2 min 25 s, mGBA's and VBA-M's 1 s, SameBoy's 11 s).

**Same play, different bytes.** Against SameBoy, the 0xFF-fill cores differ by 0 bytes (LADX,
Tetris DX), 4-5 (Robopon), 20-23 (Gold: clock-derived values the game stores).

## Downloaded entries and leads

Filed by this pass (`"method": "downloaded"`, files under `.cache/downloads/gbc/` and `gb/`):

- `gameboy-mister/Pokemon - Crystal Version (USA, Europe)/`: a playthrough save posted on
  projectpokemon.org (topic 65688) because PKHeX rejected its size; the poster re-saved it on the
  MiSTer core. 33280 = 32768 + 512: the footer starts with the same 48-byte record mGBA and VBA-M
  write as `.rtc` (5 x u32 registers `26 1a 16 10 be`, the same 5 latched, u64 LE Unix time
  2024-09-09), then 464 bytes of 0xFF. Revision not stated; the folder uses the Rev 0 name.
- `gameboy-mister/Robopon - Sun Version (USA) (SGB Enhanced) (GB Compatible)/`: from the zip on
  budude2/openfpga-GBC issue #38. 33280 = 32768 + 512, but the HuC-3 footer is packed differently:
  `f7 98 d0 65` (u32 LE Unix time, 2024-02-17) then `72 8e 00 40 00 00`, then 0xFF.

So one-saves-registry's `gameboy-mister` entry (packed, 512 reserved, 4-byte timestamp) holds for
HuC-3, but MBC3 Crystal carries the 48-byte VBA-style record with an 8-byte timestamp inside the
512. Leads and the searches that found nothing: see `gb/NOTES.md`.

Also present under `gbc/`, filed by another process with `"method": "device-backup"` (Analogue
Pocket SD backup), not reviewed here: spiritualized-gbc (13; three Dragon Warrior Monsters 2
folders carry a `[date]` suffix, two files are blank) and budude2-gb (3, GBC games under the gb
slug; budude2-gbc would be the registry's slug). Their budude2 files again end in a 16-byte footer
on clockless games (Wario Land II: 32784 = 32768 + `a46e6168 47392b00 0000` + 0xFF).

## Not runnable here

Built from source since (BUILT-CORES.md): doublecherrygb, 9 of 10 filed; boytacean and emux-gb write no save.
higan-super-famicom-balanced needs the Super Game Boy ROM. gameboy-mister was played on the owner's
MiSTer since (MISTER.md). Still nothing: budude2-gbc, spiritualized-gbc (openFPGA); mednafen (standalone).
higan-super-famicom is not a gbc core.

## Harness notes

- retro-run has no sensor interface, so MBC7 games cannot be played past calibration.
- Headless runs go far faster than real time, so host-clock cores record little elapsed time in
  their `.rtc` (see above); a real session would differ.
- Oracle of Seasons' title takes only START (A is ignored); Pokemon Gold/Crystal's title menu
  ignores START, so START is mashed to get there.

## Special save hardware (second pass)

The header sweep of both sets is in `gb/NOTES.md`. The only GBC-set battery type the corpus lacked
was MBC6, and the GBC set has exactly one MBC6 game.

### Net de Get - Minigame @ 100 (Japan): MBC6, 32 KiB SRAM + 1 MiB flash

Script `Net de Get - Minigame @ 100.txt`: past the intro and the rabbit's six pages to the room menu,
オプション: text speed おそい -> はやい, sound モノラル -> ステレオ, back out (the game writes its
settings block to SRAM). Reset; the proof is オプション read back as はやい / ステレオ. The flash
holds minigames downloaded through the Mobile Adapter, so it stays erased here (all 0xFF); the
game itself uses only the first 8 KiB of SRAM (it zeroes it on first boot and keeps ~80 bytes of
settings and state there).

| gambatte | mgba | sameboy | vba-m | gearboy | tgb-dual | fixgb | irogb |
| --- | --- | --- | --- | --- | --- | --- | --- |
| refuses ("MBC6 ROM not supported") | segfault (1) | white screen, 0 bytes of save RAM | refuses ("Unknown cartridge type 20") | **F** | black screen, 32 KiB of 0xFF | segfault at load | **F** |

1. mGBA reports 1081344 bytes of save RAM (32 KiB + 1 MiB) and then crashes in its first
   `retro_run`: EXC_BAD_ACCESS in `memset` under `GBResizeSram` <- `GBLoadSave`, so it never shows a
   frame. The crash is in the core's own save sizing, so RetroArch likely crashes the same way.

Both filed cores reload their own file (checked from a fresh run). The files:

- **Gearboy: 1081601 bytes** = 32768 SRAM + 1048576 flash + 257 bytes (256 x 0xFF, then one 0x00:
  apparently the core's flash-controller state). One file holds both memories.
- **IroGB: 32768 bytes**, the SRAM only; IroGB has no MBC6 flash in its save at all.
- The first 8 KiB are byte-identical between the two. The untouched 24 KiB after it are 0xFF in
  Gearboy and 0x00 in IroGB (the usual fill difference). So a converter between the two must cut or
  add the 1 MiB + 257-byte tail.
