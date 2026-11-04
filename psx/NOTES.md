# PlayStation (psx)

Ten US games, each saved by script on the four libretro PS1 cores that run here, plus 15
option variants that show every other file name the cores can write: 55 played entries. Plus
21 downloaded entries written by DuckStation and the MiSTer PSX core. Every card file (74
played, 21 downloaded) was checked with `1saves convert` + `1saves inspect` and holds the
saves expected (or is an empty, formatted card where noted).

All cores ran SCPH-5501 (NTSC-U v3.0, md5 490f666e1afb15b7362b406ed1cea246), the BIOS each of
them picks for a US disc from `.cache/bios/psx/`. Discs were loaded as `.cue` from
the library's US discs; `provenance.json` hashes the `.cue` (the harness hashes
what it is given). The first data track of each disc is hashed at the end of this file.

## The ten games

| Game (script) | Save on the card | Blocks | Why |
| --- | --- | --- | --- |
| Gran Turismo (USA) (Rev 1) | `BASCUS-94194GT` "GT game data" | **5** | multi-block save; famous; Simulation Mode > Home > Load & Save, ~2 min in |
| Diablo (USA) (En,Fr,De,Sv) | `BASLUS-00619-DIAB-01` "DIABLO-1P L 1 WAR A" | **10** | the largest save here; new Warrior saved from the in-game menu in Tristram |
| Tekken 3 (USA) | `BASLUS-00402TEKKEN-3` "[TEKKEN 3] THE BATTLE BEGINS!!" | 1 | Options > Memory Card > Card Save; game writes only 8 of the block's 64 frames |
| Tony Hawk's Pro Skater 2 (USA) | `BASLUS-01066C??AG01` "THPS2 CAREER- CAREER A" | 1 | named file; 2-frame animated icon; the file name changes between runs (below) |
| R4 - Ridge Racer Type 4 (USA) | `BASLUSP00797RR4_GAME` "R4 Game Data" | 1 | PocketStation-capable product code (`SLUSP`) |
| Street Fighter Alpha 3 (USA) | `BASLUSP00821-ZERO3D` "ALPHA3 SAVE DATA" | 1 | PocketStation code; lets the player pick slot 1 or 2 (used for the card-2 variants) |
| Dance Dance Revolution Konamix (USA) | `BASLUS-01446system` "KONAMIX SYSTEM" | 1 | **saves ~45 s after power-on** (offers to create system data at boot) |
| Final Fantasy Chronicles - Chrono Trigger (USA) (Rev 1) | `BASLUS-01363-00001` "Chrono FILE01 Crono LV01 00:04" | 1 | RPG save from the world map after naming Crono and Lucca; writes scattered frames |
| Spyro the Dragon (USA) | `BASCUS-94228SPYRO` "SPYRO THE DRAGON" | 1 | creates its 3-slot file right after Press Start (~1.5 min) |
| Wipeout XL (USA) | `BASCUS-94351A` "WOXL A" | 1 | proof is the game's own card manager showing block 1 = WOXL A |

Tried and dropped: Metal Gear Solid (Mei Ling, 140.96, answers "NO RESPONSE" at the dock; the
first real save is past the elevator), Final Fantasy VII (first save point is deep in the Mako
reactor with random battles), Suikoden II (long prologue before a save), Ape Escape (refuses
to start without a DualShock; the harness plugs a digital pad), Crash Bandicoot 2 and Crash
Bash (no quick save path found), Yu-Gi-Oh! Forbidden Memories (name entry stalled),
Final Fantasy Origins (no save outside inns).

## Games x cores

| Game | beetle-psx | beetle-psx-hw | pcsx-rearmed | swanstation |
| --- | --- | --- | --- | --- |
| Gran Turismo | filed | filed | filed (+ `pcsx-card2.mcd`) | filed |
| Diablo | filed | filed | filed (+ card2) | filed |
| Tekken 3 | filed + 3 variants | filed + 1 variant | filed (+ card2) + 2 variants | filed + 3 variants |
| Tony Hawk's Pro Skater 2 | filed | filed | filed (+ card2) | filed |
| R4 | filed | filed | filed (+ card2) | filed |
| Street Fighter Alpha 3 | filed + slot-2 variant | filed + slot-2 variant | filed (+ card2) + slot-2 variant | filed + slot-2 variant |
| DDR Konamix | filed | filed | filed (+ card2) | filed |
| Chrono Trigger | filed | filed | filed (+ card2) | filed |
| Spyro the Dragon | filed | filed | filed with `Spyro the Dragon.pcsx-rearmed.txt` (+ card2) + serial variant | filed + per-game variant |
| Wipeout XL | filed | filed | filed (+ card2) | filed |

40/40 default entries filed. Not runnable here: duckstation (11 downloaded entries),
psx-mister (10 downloaded), mednafen standalone, pcsx1 and rustation (nothing found); see
"Downloaded entries" below.

Core versions: Beetle PSX / Beetle PSX HW 0.9.44.1 71ee81e (HW ran its OpenGL renderer),
PCSX-ReARMed r26 7b0e8f8, SwanStation 1.0.0 631f0fb (OpenGL).

Script notes:
- SwanStation leaves controller port 2 empty, so games grey out and skip their 2-player menu
  items (THPS2 "Player 2 Controls", SFA3 "Versus Mode"). The shared scripts count menu items
  from the other end (or wrap) so they land on the same item in every core.
- PCSX-ReARMed always has a second card in slot 2 (`pcsx-card2.mcd`, below). Spyro then asks
  "Select memory card: Slot 1 / Slot 2" first, hence the per-core script. It also reached that
  prompt ~400 frames later than the others.
- Wipeout XL drops 4-frame presses; its script holds every button 10 frames.

## What each core writes

All card files are raw 131072-byte PS1 cards (no header, no DexDrive/.gme wrapper), whatever
the extension (`.srm`, `.mcr`, `.mcd`). Names below use `<stem>` = the content file name
without extension (here the `.cue` name), as RetroArch would.

### Defaults

| Core | Card 1 | Card 2 |
| --- | --- | --- |
| beetle-psx, beetle-psx-hw | `<stem>.srm` (libretro SRAM, written by the frontend) | none (slot 2 is empty by default in this build) |
| pcsx-rearmed | `<stem>.srm` | **`pcsx-card2.mcd`**, a card *shared between all games*, created in the save dir at load even if never used |
| swanstation | `<stem>.srm` | none |

So every default PCSX-ReARMed entry has two files, and `pcsx-card2.mcd` in a user's save
folder belongs to no single game.

### Options that change it (all filed as `<game> [variant]` entries; option files in `scripts/psx/options/`)

| Core / option | Files written |
| --- | --- |
| Beetle `beetle_psx_use_mednafen_memcard0_method = mednafen` (HW: `beetle_psx_hw_...`) | card 1 as `<stem>.0.mcr`; **no `.srm`** (the core reports no SRAM) — `Tekken 3 (USA) [memcard0-mednafen]` on both Beetles |
| Beetle `beetle_psx_enable_memcard1 = enabled` | `<stem>.srm` + `<stem>.1.mcr`; the `.1.mcr` is written at unload even when the game never touched it (a blank formatted card) — `Tekken 3 [memcard1-enabled]`; with a save in slot 2: `Street Fighter Alpha 3 [slot2-memcard1-enabled]` (`.1.mcr` holds the save, `.srm` blank) |
| Beetle `shared_memory_cards = enabled` (+ mednafen method + memcard1) | `mednafen_psx_libretro_shared.0.mcr` and `.1.mcr` (the HW core uses the same base name); with the libretro method only slot 2 becomes shared — `Tekken 3 [shared-mednafen]` |
| Beetle `memcard_left_index` / `memcard_right_index` (0-63) | the `N` in `<stem>.N.mcr` (left only with the mednafen method); not filed |
| PCSX `pcsx_rearmed_memcard1 = serial` | `<SERIAL>_1.mcd`, no `.srm`. The serial is PCSX's 9-character CdromId with a dash inserted before the first digit: Spyro (`\SCUS_942.28`) gives `SCUS-94228_1.mcd`, but Tekken 3 boots from `\TEKKEN3\SLUS_004.02` and gives **`TEKKEN-3SL_1.mcd`** — `Spyro [memcard1-serial]`, `Tekken 3 [memcard1-serial]` |
| PCSX `pcsx_rearmed_memcard1 = shared` | `pcsx-card1.mcd`, no `.srm` — `Tekken 3 [memcard1-shared]` (with `memcard2 = serial`: `TEKKEN-3SL_2.mcd`, blank, created at load) |
| PCSX `pcsx_rearmed_memcard2 = none / serial / shared` | no card 2 / `<SERIAL>_2.mcd` / `pcsx-card2.mcd` (default). SFA3 saved to slot 2: `Street Fighter Alpha 3 [slot2-defaults]` (`pcsx-card2.mcd` holds the save) |
| SwanStation `swanstation_MemoryCards_Card1Type = PerGame` | `<SERIAL>_1.mcd` with the disc's real serial (`SLUS-00402_1.mcd`, `SCUS-94228_1.mcd`), no `.srm` |
| SwanStation `Card1Type = PerGameTitle` | `<title>_1.mcd` where title is the content file title: `Tekken 3 (USA)_1.mcd` (no game-database title in this build) |
| SwanStation `Card1Type = Shared` | `duckstation_shared_card_1.mcd` (not `shared_card_1.mcd` as standalone DuckStation names it) |
| SwanStation `Card2Type = Shared / PerGame / PerGameTitle` | `duckstation_shared_card_2.mcd` / `<SERIAL>_2.mcd` / `<title>_2.mcd`; written even when the game never used slot 2 (blank, FF-filled). SFA3 saved to slot 2: `Street Fighter Alpha 3 [slot2-card2-pergametitle]` → `Street Fighter Alpha 3 (USA)_2.mcd` |
| SwanStation `UsePlaylistTitle` | only matters for `.m3u` playlists with per-title cards; not filed |

### Differences inside the files

- **Fill of a fresh card.** Block 0 is byte-identical in all three formatters ("MC" header frame
  with checksum 0x0E, 15 free directory frames `A0 00 00 00 .. FF FF .. A0`, 20 broken-sector
  frames `FF FF FF FF 00 00 00 00 FF FF ..`, frame 63 a copy of the "MC" frame). The 15 data
  blocks are **0x00 in Beetle and PCSX-ReARMed but 0xFF in SwanStation** (DuckStation's
  formatter). An untouched Beetle `.1.mcr` / `shared.1.mcr` and PCSX `pcsx-card2.mcd` /
  `TEKKEN-3SL_2.mcd` are the same bytes (sha1 1b3c99be5527...); SwanStation's untouched card is
  0371ac92474c... "Untouched" is not "unused": Spyro and Wipeout XL wrote frame 63 of PCSX's
  empty card 2 while probing it (sha1 506988ab99c8...), so a "blank" second card can differ.
- **The fill shows through partial saves.** Games often write fewer than the 64 frames of a
  block: Tekken 3 writes 8 (0x400 bytes), Wipeout XL 0x900, Spyro 0x1400, THPS2 0x1C80,
  Chrono Trigger a scattered set of frames. The rest of the block keeps the format fill, so
  SwanStation's save blocks end in FF where the others end in 00. A save copied between cores
  is a different byte string even when the game data matches.
- **Frame 63** (the BIOS "write test" frame) is overwritten with `03 00 00 00 80 0C 5A 27 ..`
  (SFA3: `13 00 ..`) by Tekken 3, THPS2, Spyro, Chrono Trigger and SFA3 on every core; for Wipeout
  XL only PCSX-ReARMed's cards (both slots) have it overwritten, the others keep the "MC" copy.
  GT, Diablo, R4 and DDR leave it alone. Anything comparing whole block 0 will see this.
- **Beetle PSX and Beetle PSX HW** wrote byte-identical cards for all ten games.
- **Same save, different bytes, by timing** (the game's own data, not the core's format):
  GT, R4 and DDR save blocks are identical on all cores. THPS2 puts two varying letters in
  its file name (`BASLUS-01066CCIAG01` on Beetle, `CFKAG01` PCSX, `CDCAG01` SwanStation; it
  changes between runs on one core too), so even the directory frame differs. Tekken 3's data
  is scrambled with a varying key; Spyro stores a 2-byte value in the last palette entry of its
  header (0x7E); Chrono Trigger, SFA3 (total play time) and Diablo differ in a few counters.
- **No .srm when the core manages the card**: with Beetle's mednafen method, PCSX serial/shared
  card 1 and SwanStation non-Libretro card 1, the core reports 0 bytes of SRAM and the frontend
  writes no `.srm` at all.

### one-saves

`1saves convert --system psx --from <core>` + `inspect` read all 74 played card files: one save per
card where expected, blank cards as a card with no saves. One gap: the PocketStation-style
product codes `BASLUSP00797` (R4) and `BASLUSP00821` (SFA3) are left "game unidentified",
while `BASLUS-00402...` resolves to SLUS-00402. Also no single file name tells 1Retro which
game a `pcsx-card2.mcd`, `pcsx-card1.mcd`, `duckstation_shared_card_N.mcd` or
`mednafen_psx_libretro_shared.N.mcr` belongs to: they are multi-game cards.

## Downloaded entries and leads

Searched by a helper agent on 2026-11-04 (about 35 minutes); 21 cards filed with
`"method": "downloaded"` provenance (URL, page, author, licence, what it is). All are raw
131072-byte cards; `1saves inspect` reads every one (deleted directory entries are skipped).

**duckstation** (11 entries). DuckStation's own issue tracker is closed; the unofficial tracker
(`duckstation-unoff-issue-tracker-admin/duckstation-unofficial-issue-tracker`, now
`duckstation-unofficial/issue-tracker`) has reporters attaching their memory cards and stating
the DuckStation build:

| Folder | File | Saves | Build / source |
| --- | --- | --- | --- |
| Alone in the Dark - The New Nightmare (USA) (Disc 1) | `..._1.mcd` | 2 | 0.1-5325, issue #29 |
| Alundra 2 - A New Legend Begins (USA) | `..._1.mcd` | 1 | 0.1-6292, issue #128 |
| Casper (USA) | `Casper (USA)_1.mcd` | 1 (2 blocks) | 0.1-5437, issue #87 |
| Disney's The Emperor's New Groove (Europe) | `..._1.mcd` | 1 (PAL) | 0.1-9179, issue #221 |
| T'ai Fu - Wrath of the Tiger (Italy) | `..._1.mcd` | 1 (PAL) | 0.1-5536, issue #105 |
| Xenogears (USA) (Disc 2) | `Xenogears (USA) (Disc 2)_1.mcd` | 1 | 0.1-5437, issue #83 (a per-disc card) |
| (shared card) Breath of Fire III, Legend of Dragoon, Star Ocean 2, FF7 | `shared_card_1.mcd` | 8 | 0.1-5437, issue #84 |
| Mega Man X5 (USA) | `Mega Man X5 (USA)_1.mcd` | 1 | archive.org, PhoenixStormJr, from DuckStation's `memcards` folder |
| Cross Tantei Monogatari (Japan) | `..._1.mcd` | 5 | GitHub snake7594/cross-tantei-monogatari-korean #16, "latest DuckStation" |
| (shared card) Air Combat, 2022-12-04 | `shared_card_1.mcd` | 1 | archive.org, Ladislav Svoboda, Public Domain Mark |
| (shared card) Air Combat to 4x4 World Trophy, 2026-08-09 | `shared_card_1.mcd` | 8 (6 games) | the same card four years later |

Standalone DuckStation names cards `<Title>_1.mcd` (title from its game list, Redump-style
with region and disc) and `shared_card_1.mcd`, where SwanStation says
`duckstation_shared_card_1.mcd`. Unused blocks are 0xFF, as in SwanStation.

**psx-mister** (10 entries, all from MiSTer-devel/PSX_MiSTer issue attachments): Loaded (USA)
(En,Fr) (#122, "successfully written to microSD" by the core: the clearest), Final Fantasy VII
(USA) (#384), Silent Hill (USA) (`Silent Hill.sav`, #149), Suikoden (USA) (#164, 2 blocks),
Revelations - Persona (USA) (`Persona.sav`, #308, three 2-block saves), Aconcagua (Japan)
(#215), Warhammer - Shadow of the Horned Rat (USA) (#252), Doraemon 2 (Japan) (#370), Tekken 3
(USA) (#358; mixed NTSC/PAL saves of other games and five deleted entries, so the contents were
probably assembled elsewhere), CTR - Crash Team Racing (USA) (#99, keeps a deleted 2-block ghost,
directory state 0xA1). The core's save is `<rom name>.sav`, one raw 128 KiB card, unused
blocks 0x00 (like Beetle/PCSX), deleted entries left in place.

**Not found**: mednafen (standalone; searched GitHub for `.0.mcr`/`.1.mcr`, the Mednafen forum,
the web: only Beetle threads), pcsx1 (PCSX-R/PCSX issue trackers, `Mcd001.mcr`, GameFAQs),
rustation (no sign it persists cards at all).

**Leads, not filed** (emulator unclear or unreachable):
- speedrun.com resources: Spyro 1 NTSC-J 120% for DuckStation (`spyroce` y989s, a
  `Spyro the Dragon (Japan) (Shokai Genteiban)_1.mcd`), Ape Escape practice save "for use with
  DuckStation" (`ae1` rf3gc), Crash 3 Japan 100% (`crash3` sip4a, DuckStation-style name, emulator
  unstated; Wayback copy exists). speedrun.com download links sit behind a Cloudflare check.
  Breath of Fire 3 "Savefiles for DUCKSTATION" (`bof3` d3lmc) is a 322 MB rar.
- MiSTer issues: SuperSponge (#310, unused blocks 0xFF, the same issue says loading saves fails,
  so probably made elsewhere), CTR `[B-D Ghosts].mcd` and Tokimeki Memorial 2 `.mcd` (#99, #152;
  `.mcd` names suggest cards started outside the core).
- Super Robot Taisen Alpha (Japan) card in the Cross Tantei zip (dated 2024, older than the report).
- Beyblade 2002 P1/P2 DuckStation netplay cards (archive.org, TheWhiteDevil27): emulator inferred.
- Intermediate snapshots of the Svoboda shared card (2024-06-02, 2025-01-26, 2026-03-29, and an
  "-MSI" copy) are in `.cache/downloads/psx/` but not filed.


## Disc hashes (first track)

| Game | Track file | Size | SHA-1 |
| --- | --- | --- | --- |
| Gran Turismo (USA) (Rev 1) | `Gran Turismo (USA) (Rev 1).bin` | 693668304 | `5433c55806f7cd5ca2e42a6c39ff816d442ed6b6` |
| Tekken 3 (USA) | `Tekken 3 (USA) (Track 1).bin` | 632532768 | `68f32a8657376cb4d4504c160fd5e8ae4a4f18d6` |
| Tony Hawk's Pro Skater 2 (USA) | `Tony Hawk's Pro Skater 2 (USA).bin` | 748037136 | `f5cb80a7d55aaced7fcc9c5a82a6c28b89dc489a` |
| R4 - Ridge Racer Type 4 (USA) | `R4 - Ridge Racer Type 4 (USA).bin` | 621421920 | `75f0dab5c1f71ba80f3d1e2fefd043f3f2b9ee2e` |
| Street Fighter Alpha 3 (USA) | `Street Fighter Alpha 3 (USA) (Track 1).bin` | 484081584 | `ec98188f53dbfa08a59d89c981e9ca68b7f1748e` |
| Dance Dance Revolution Konamix (USA) | `Dance Dance Revolution Konamix (USA).bin` | 452437776 | `e88014e32c934def78b286ae2255e33089032cc8` |
| Final Fantasy Chronicles - Chrono Trigger (USA) (Rev 1) | `Final Fantasy Chronicles - Chrono Trigger (USA) (Rev 1).bin` | 547484448 | `d169c65f4d2ed543ac9bcb961e429c04a2674f28` |
| Spyro the Dragon (USA) | `Spyro the Dragon (USA).bin` | 661547040 | `cf3ce6bedeb89dfbc40990336180f3b9b0f40d9f` |
| Diablo (USA) (En,Fr,De,Sv) | `Diablo (USA) (En,Fr,De,Sv).bin` | 653239776 | `5e3669fd2920b953f9a164426e044c21e109fd26` |
| Wipeout XL (USA) | `Wipeout XL (USA) (Track 01).bin` | 86045568 | `5694008c30fa9896d17afdd6281e4bebb9f63953` |
