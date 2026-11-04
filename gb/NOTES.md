# Game Boy (`gb`)

Ten DMG-set games (No-Intro "Nintendo - Game Boy"), each played from power-on to a genuine save by
one shared script in `scripts/gb/`, then replayed in every libretro core that runs here.
74 of 90 (game, core) runs were filed; every proof.png was checked by eye.

Cores and versions (buildbot nightlies, `tools/fetch-core.sh`): Gambatte v0.5.0-netlink 77f2567,
mGBA 0.11-212-7a12d6d, SameBoy 1.0.5 90e2899, VBA-M 115defb, Gearboy 3.8.20-8-g37d0bf3,
TGB Dual v0.8.3 0392c9c, fixGB Alpha v0.8.2, IroGB v1.0.0, SkyEmu adacd07. No boot ROMs were given
to any core (none was needed). SkyEmu needs `--options scripts/gb/skyemu.options` (see Harness).

## The ten games

| Game (script) | Cartridge | Save | Why |
| --- | --- | --- | --- |
| Link's Awakening (`Legend of Zelda, The - Link's Awakening.txt`) | MBC1 + 8 KiB | file 1 "ABC" registered | the most played GB save; same play as the done LADX entry |
| Pokemon Red (`Pokemon Red.txt`) | MBC3 + 32 KiB, no clock | SAVE from the start menu in the bedroom | most played; MBC3 without RTC |
| Pokemon Yellow (`Pokemon Yellow.txt`) | MBC5 + 32 KiB (CGB-compatible, in the GB set) | SAVE in the bedroom | MBC5 on a DMG-set game |
| Final Fantasy Adventure (`Final Fantasy Adventure.txt`) | MBC2 (512 x 4-bit RAM in the mapper) | Select -> Save -> slot 1 in the arena | MBC2, the half-byte RAM |
| Super Mario Land 2 (`Super Mario Land 2.txt`) | MBC1 + 8 KiB | the file room formats all three slots; pipe B starts file B | popular; a save written outside any menu |
| Pocket Camera (Japan) (`Pocket Camera.txt`) | Pocket Camera mapper + 128 KiB | one photo taken and kept (のこり30 -> 29) | the only 128 KiB DMG save (the US Game Boy Camera is not in the 1G1R set) |
| Itsudemo! Nyan to Wonderful (Japan) (`Itsudemo! Nyan to Wonderful.txt`) | MBC3 + clock + 8 KiB | clock set to AM 00:00, a puppy named "ア" registered | DMG clock carts are Japanese only |
| Pocket Family GB (Japan) (`Pocket Family GB.txt`) | HuC-3 (clock) + 32 KiB | move-in, then おわる -> セーブして おわる | HuC-3 on the DMG set |
| Pocket Monsters Midori (Japan) (`Pocket Monsters Midori.txt`, variants `.skyemu.txt`, `.fixgb.txt`) | MBC1 + 32 KiB (RAM banking) | レポート in the bedroom; proof is つづきから + the report summary after a reset | the only MBC1 32 KiB layout; same play as Red |
| Robot Ponkots Sun (Japan) (`Robot Ponkots Sun.txt`) | HuC-1 (infrared) + 32 KiB | start menu -> セーブ in the lab ("セーブしました") | HuC-1; same play as Robopon Sun on gbc |

## Games x cores

F = filed. Everything else is a finding, not filed.

| Game | gambatte | mgba | sameboy | vba-m | gearboy | tgb-dual | fixgb | irogb | skyemu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Link's Awakening | F | F | F | F | F | F | F | F | F |
| Pokemon Red | F | F | F | F | F | F | F | F | F |
| Pokemon Yellow | F | F | F | F | F | F | F | F | F |
| Final Fantasy Adventure | F | segfault (1) | F | F | F | F | F | F | bad save (2) |
| Super Mario Land 2 | F | F | F | F | F | F | F | F | F |
| Pocket Camera | refuses (3) | F | F | white screen, no save | F | white screen | segfault | refuses (3) | white screen |
| Nyan to Wonderful | F | F | F | F | F | F | F | F | F |
| Pocket Family GB | F | F | F | F | F | F | segfault | garbled (4) | white screen, RAM all 0 |
| Pocket Monsters Midori | F | F | F | F | F | F | F (variant) | F | F (variant) |
| Robot Ponkots Sun | in-game error (5) | F | F | garbled | F | white screen | garbled | F | white screen |

1. mGBA segfaults in `_GBMBC2Read` (EXC_BAD_ACCESS one page past its save buffer) on every MBC2
   game tried: Final Fantasy Adventure (before frame 60), Final Fantasy Legend, Kid Icarus, Kirby's
   Pinball Land, Golf, Wave Race, F-1 Race, Top Rank Tennis, Ultima, Lazlos' Leap. It reports a
   256-byte save (MBC2 packed two nibbles per byte), so no mGBA MBC2 file exists here. The crash is
   in the core's own memory handling, so RetroArch likely crashes the same way.
2. SkyEmu runs FFA and writes a file, but reading the slot back in game shows HP 65535, L255:
   its MBC2 RAM does not round-trip. Not filed.
3. Gambatte: "Pocket Camera ROM not supported"; IroGB: "Invalid game format".
4. IroGB runs Pocket Family with broken graphics and the script desyncs before the save.
5. Gambatte shows the game's own "ゲットバッファー ヌル エラー" (get buffer: null error) on a white
   screen, most likely the HuC-1 infrared check; the game never starts.

fixGB "segfault" = exit 139 at load, after reporting "save RAM 0 bytes": it has no Pocket Camera,
HuC-3 or MBC7 support and crashes rather than refusing.

## What differs between the cores' files

**Size of the battery file.** Every core writes `<rom stem>.srm` at the cartridge's RAM size,
except:
- SkyEmu writes 131072 bytes for every game (8 KiB and 32 KiB games alike), the game's data at the
  start and zeros after it.
- MBC2 (FFA): SameBoy, VBA-M, Gearboy, fixGB and IroGB write 512 bytes (one nibble per byte);
  Gambatte and TGB Dual write 8192 bytes (the 512 bytes, then 0xFF to 8 KiB; their two files are
  byte-identical); mGBA would write 256 (packed), see above.

**Fill of untouched RAM.** Gambatte, mGBA, SameBoy, VBA-M, Gearboy and TGB Dual start battery RAM
at 0xFF; fixGB, IroGB and SkyEmu start it at 0x00. So the same play gives files that differ in
every byte the game never wrote (LA: 5489 bytes 0xFF vs 0x00; Red/Yellow: 27616 bytes). This changes
game behaviour: Pocket Monsters Midori on Gambatte finds a "report" in 0xFF RAM and asks to
overwrite it, which the shared script answers.

**MBC2 nibbles.** The 4-bit cells are stored as 0x0N by Gambatte, TGB Dual, SameBoy, VBA-M,
Gearboy and IroGB, but as 0xFN by fixGB (unused cells 0xF0, never 0xFF). Unused cells: 0xFF
(Gambatte, TGB Dual, SameBoy, VBA-M, Gearboy), 0x00 (IroGB), 0xF0 (fixGB). A reader must mask
the high nibble.

**Clock (`.rtc` sidecar).** Under a libretro frontend every core that exposes a clock writes it
to `<stem>.rtc` (RETRO_MEMORY_RTC); none appends it to the `.srm`. Layouts seen:

| Core | MBC3 (Nyan) | HuC-3 (Pocket Family) | No clock |
| --- | --- | --- | --- |
| gambatte | 8: u64 LE Unix time of the clock's zero | 8: same | none |
| mgba | 48: 5 x u32 regs (s, m, h, d, dh), 5 x u32 latched, u64 LE Unix time (the VBA/BGB footer) | **none** (the HuC-3 clock is not saved) | none |
| vba-m | 48: same layout as mGBA | 8: u64 LE Unix time only | none |
| gearboy | 48: same layout | 20: 12 bytes of HuC-3 state + u64 LE Unix time | none |
| sameboy | 32: regs (5 bytes), latched (5), pad to 16, u64 LE Unix time, u64 cycle count | 32: zeros + time + cycles | none |
| tgb-dual | 4: u32 LE that counts seconds of emulated time | 4: same | **4, for every game** |
| skyemu | 14: two 5-byte register sets + flags, seeded from host wall-clock time | (no HuC-3) | **14, for every game** |
| fixgb, irogb | none (the clock is lost) | (no HuC-3) | none |

Gambatte, mGBA, VBA-M and SameBoy count the clock in host time, Gearboy and TGB Dual in emulated
time: in these headless runs (far faster than real time) a 145-second play left mGBA's registers at
1 s and Gearboy's at 2 min 25 s.

Against one-saves-registry `data/clocks.json`: **gambatte** (sidecar) agrees. **mgba**, **sameboy**
and **vba-m** are recorded as `appended` (8-byte timestamp); their libretro cores here write a
sidecar instead (mGBA and VBA-M the same 48-byte record, just not appended; SameBoy a 32-byte
record of its own), and mGBA writes no clock at all for HuC-3. **gearboy**, **tgb-dual** and
**skyemu** are absent from clocks.json; TGB Dual's and SkyEmu's `.rtc` exist even for games with
no clock. **gameboy-mister** / **sgb-mister** / **budude2-gb**: see Downloaded.

**SGB mode.** mGBA and Gearboy run SGB-flagged DMG games as a Super Game Boy by default (border
in the proof, title screens ~300 frames later), the others as DMG; CGB-compatible Yellow runs in
CGB mode everywhere. The saves are unaffected but scripts need the extra margin.

**Same data, different bytes.** Where the fill matches, files still differ a little from timing,
RNG and the clock (against SameBoy: Link's Awakening 0 bytes, Red 3-4, Pocket Family ~3000, the
game keeps live state in its RAM); no core reorders or pads the data itself except as above.

## Downloaded entries and leads

Filed by this pass (`"method": "downloaded"`, files under `.cache/downloads/gb/`):

- `gameboy-mister/Robot Ponkots - Sun Version (Japan) (SGB Enhanced)/`: from
  `Robopon_MiSTer_SAVE.zip` attached to budude2/openfpga-GBC issue #38 (the uploader made it on the
  MiSTer at the developer's request, to compare HuC-3 clocks). 33280 = 32768 + a 512-byte footer:
  `84 99 d0 65` (u32 LE Unix time, 2024-02-17), `19 8f 00 40 00 00` (HuC-3 clock state), then 0xFF.
  This is the HuC-3 release, not the HuC-1 Comic Bom Bom edition played above; the No-Intro name
  is assumed (the 1G1R set lacks it).
- `gameboy-mister/Donkey Kong (World) (Rev 1) (SGB Enhanced)/`: Gameboy_MiSTer issue #187 zip.
  8192 bytes, no footer (no clock), so the MiSTer file is the plain RAM image.

Leads, not filed: SGB_MiSTer issue #9 has only a savestate (`.cache/downloads/gb/103-sgbmister-dkl2/`);
boytacean issue #8 links a savestate, not a battery save; frederic-mahe/Analogue-Pocket issues
#41/#137 carry saves written by the Pocket's own firmware or of unknown origin. Nothing for
budude2-gb, spiritualized-*, doublecherrygb, emux-gb, higan-balanced or mednafen in their repos'
issues, GitHub-wide searches, PKHeX/PKSM issues, misterfpga.org, archive.org or Reddit.

Also present under `gb/`, but filed by another process during this pass with `"method":
"device-backup"` (an Analogue Pocket SD backup) and not reviewed here: spiritualized-gb (7),
spiritualized-gbc (4, DMG games on the GBC core), spiritualized-supergb (1, a physical cartridge
dump named `run_cartridge`), budude2-gb (1). Some folder names there are not No-Intro names (fan
translations) and one Pokemon Blue file is all 0xFF. What they show: budude2 appends a 16-byte
footer to every save, even without a clock (Super Mario Land 2: 8208 = 8192 + `c9ea9069 b9186400
0000` + 0xFF), while the Spiritualized cores write the bare RAM size.

## Not runnable here

higan-super-famicom-balanced (needs the Super Game Boy ROM, not in the library); budude2-gb,
spiritualized-gb, spiritualized-supergb (openFPGA: device backups only). Built from source since
(see BUILT-CORES.md): doublecherrygb, 7 of 10 filed; boytacean and emux-gb build but never hand the
frontend their save memory, so nothing is written. Played on the owner's MiSTer since: gameboy-mister
and sgb-mister (MISTER.md). mednafen (standalone) has nothing filed.

higan-super-famicom (x86_64, optional) was skipped: it plays GB only
through the Super Game Boy and needs `SGB1.sfc/program.rom` plus `sgb1.boot.rom` in its system
directory, and neither the SGB cartridge nor its boot ROM is in the ROM library.

## Harness notes

- SkyEmu segfaults in `opts_reload_all` (strcmp on a NULL option value) because retro-run answers
  core-options version 0 and SkyEmu never registers defaults that way. Workaround, no tools/ edit:
  `scripts/gb/skyemu.options` sets its four options (core override Automatic, firmware disabled).
- SkyEmu's `retro_reset` wipes battery RAM and fixGB ignores reset, so Midori's reset-to-proof is
  replaced by a variant script for those two cores.
- retro-run has no sensor interface (no tilt) and no subsystem loading (no SGB pairing).
- Titles that ignore input during animations (Pokemon's Pokemon swap, FFA's crawl) are entered by
  mashing START a few times rather than one timed press.

## Special save hardware (second pass)

A sweep of the cartridge header of every game in the GB and GBC 1G1R sets (1051 + 928 ROMs, read
inside the zips: type byte 0x147, RAM-size byte 0x149, plus the header of the last 32 KiB bank,
where an MMM01 multicart keeps its menu's header) against the games the corpus already has. The
battery-backed kinds in the two sets, and whether the corpus has one (any core):

| Cartridge type (0x147) | RAM (0x149) | Games in the sets | In the corpus |
| --- | --- | --- | --- |
| 03 MBC1+RAM+BATT | 8 KiB / 32 KiB | 115 / 14 | yes (LA, SML2, Tetris DX / Midori) |
| 06 MBC2+BATT | 512 x 4 bit in the mapper | 63 | yes (FFA) |
| 0D MMM01+RAM+BATT (last-bank header only; bank 0 says MBC1) | 8 KiB | 1: Momotarou Collection 2 | **attempted, nothing filed** (below) |
| 10 MBC3+TIMER+RAM+BATT | 8 KiB / 32 KiB | 8 / 8 | yes (Nyan, Harvest Moon / Gold, Crystal) |
| 13 MBC3+RAM+BATT | 8 KiB / 32 KiB | 1 / 4 | 32 KiB only (Red); the 8 KiB one (Shin Keiba Kizoku Pocket Jockey) is just a size combination, not added |
| 1B MBC5+RAM+BATT | 8 / 32 / 128 KiB | 384 / 97 / 3 | yes (Oracle / Yellow, LADX / GB Wars 3) |
| 1E MBC5+RUMBLE+RAM+BATT | 8 KiB / 32 KiB | 10 / 1 | 8 KiB (Pinball); the 32 KiB one (Chee-Chai Alien, also an IR sensor) not added |
| 20 MBC6 (+ 1 MiB flash) | 32 KiB | 1: Net de Get (GBC set) | **added, see `gbc/NOTES.md`** |
| 22 MBC7 (EEPROM) | none declared | 2 | yes (Kirby Tilt 'n' Tumble) |
| FC Pocket Camera | 128 KiB | 1 | yes |
| FD Bandai TAMA5 | none declared (32 bytes in the chip) | 1: Game de Hakken!! Tamagotchi | **added** |
| FE HuC-3 | 32 KiB | 6 | yes |
| FF HuC-1 | 32 KiB | 7 | yes |

No game in either set declares 2 KiB (0x01) or 64 KiB (0x05) of RAM, or MBC3+TIMER without RAM
(0x0F). 13 other ROMs have a last bank whose "type byte" reads 0x0B-0x0D, but only
Momotarou Collection 2 carries a real header there (title `MOMOCOL2`); the rest are code or graphics.

### Game de Hakken!! Tamagotchi - Osutchi to Mesutchi (Japan) (SGB Enhanced): TAMA5

Script `Tamagotchi - Osutchi to Mesutchi.txt`: さいしょから, Tamagotchi time (fast), clock 1997/1/1
0:00, the first egg, name "ああ"; the egg hatches; reset; つづきから brings the pet back in its room
(the proof). The TAMA5 has no SRAM chip: the game keeps its pet in 32 bytes inside the TAMA5
(read and written a nibble at a time through the mapper), beside the chip's own clock.

| gambatte | mgba | sameboy | vba-m | gearboy | tgb-dual | fixgb | irogb | skyemu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| refuses ("Bandai TAMA5 ROM not supported") | **F** | white screen, 0 bytes of save RAM | plays, but the pet is not kept (1) | **F** | white screen | segfault at load | plays, pet not kept (2) | white screen |

1. VBA-M runs the whole script, and after a soft reset the game continues (the TAMA5 state lives
   in the core's memory), but its `.srm` is 32768 bytes of zeros apart from `00 01` at the start:
   the 32 TAMA5 bytes are not in it. A fresh run started from those files offers only
   さいしょから. Its `.rtc` (64 bytes) does hold the TAMA5 clock: u32 LE registers (seconds `3a`,
   ...) and a u64 LE Unix time at 0x38.
2. IroGB writes an 85-byte `.srm`: 32 bytes of `01`, then what looks like its register state, then
   0xFF. Reloaded, the game finds no pet.

The two filed files: mGBA and Gearboy write the same 32-byte `.srm`, byte for byte (one file byte per
byte of TAMA5 RAM, full bytes such as `0c`, `40`, `42`, `62`, `8c`). The clock differs: **mGBA
writes no clock at all** for TAMA5 (no `.rtc`), **Gearboy writes a 72-byte `.rtc`**: 64 bytes of
TAMA5 clock registers (mostly 0x00-0x0F nibbles) then a u64 LE Unix time. Both reload their own
files (checked: a fresh run from the filed files reaches つづきから and the room). Neither TAMA5
layout is in one-saves-registry's `clocks.json`.

### Momotarou Collection 2 (Japan) (SGB Enhanced): MMM01, attempted, not filed

Momotarou Dengeki 2 (no save) and Momotarou Densetsu Gaiden (MBC2+BATT in its own header, saves to
the MMM01's 8 KiB) on one MMM01 cart. Only **mGBA, SameBoy and IroGB** run the MMM01 menu (each
then reports 8 KiB of save RAM). Gambatte, VBA-M, Gearboy, TGB Dual and fixGB boot straight into
the first game, Momotarou Dengeki 2, as a plain MBC1 cart (TGB Dual still writes an 8 KiB `.srm`,
the others none); SkyEmu shows a black screen and writes its usual 128 KiB.

In SameBoy, Gaiden's びんぼうがみ story was played for several minutes (the house, the overworld,
the first hut, talking to the people there) and the openings of やしゃひめ and うらしま were
played through; the 8 KiB stayed 0xFF throughout. In the ROM, Gaiden's routine that copies its save buffer to SRAM is reached only
through one entry of an event table, so the save is tied to some story event, which was not found
within the timebox. Nothing filed; the probe frames are the finding: MMM01 support is mGBA,
SameBoy and IroGB only.

### Net de Get (MBC6)

Filed under `gbc/`, see `gbc/NOTES.md`.
