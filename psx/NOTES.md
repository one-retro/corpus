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

## GameFAQs saves

Every save on GameFAQs' PlayStation pages for the games here (and their sibling releases) in a
format of the console's own devices: 297 files from the "PlayStation DexDrive Save" sections and
70 zips from "PlayStation PS3 Virtual Memory Card Save (ZIP)", downloaded 2026-11-05 and filed as
367 downloaded entries, `psx/_<device>/<release> [GameFAQs <id>]/`, each with the file(s) exactly
as served (a zip replaced by what is in it, inner paths kept), `provenance.json` and a `proof.png`
tiling every core's frame (order in `verified.proof_order`).

### What the files really are

| Device (folder) | Files | What the bytes are | GameFAQs section |
| --- | ---: | --- | --- |
| `_dexdrive` | 285 | DexDrive `.gme`: `123-456-STD`, a 3904-byte (0xF40) header with the per-block comments, then the 131072-byte card. 254 are whole; **22 are cut short** to the blocks in use (20288, 28480, 102208 or 126784 bytes: 2, 3, 12 or 15 of the card's 16 blocks); **8 have the header zeroed** (134976 bytes, `MC` at 3904, no `123-456-STD`); one has 345 extra bytes (below) | DexDrive |
| `_raw-card` | 9 | a raw 131072-byte card served as `.gme` | DexDrive (mislabelled) |
| `_vgs` | 2 | Connectix Virtual Game Station card: `VgsM`, 64-byte header, the card | DexDrive (mislabelled) |
| `_raw-save` | 3 | one raw 8192-byte save block, starting with the save's `SC` title frame and no directory frame: one served as `.gme` (no name anywhere), two in zips named `BESLES-01514SILENT00.PSV` / `BESCES-01237TEKKEN-3.PSV` (the name is the file name) | DexDrive / PS3 (mislabelled) |
| `_ps3` | 63 | zips of PS3 exports (`.PSV`): `\0VSP`, a 0x84-byte header (signature, byte 0x3C = 1 for a PS1 save, the 20-byte save name at 0x64), then the save's blocks; 8324 bytes for a 1-block save, 16516 for 2, 41092 for 5. Four zips hold two `.PSV`s, one a stray `__MACOSX/._` file, one a `desktop.ini` | PS3 |
| `_psp` | 3 | zips of a PSP save folder for a PSone Classic (`SCUS94491/`, `SLUS00292/`: `PARAM.SFO`, `ICON0.PNG`, `CONFIG.BIN`, `SCEVMC0.VMP`, `SCEVMC1.VMP`); a `.VMP` is `\0PMV`, a 128-byte header, the card; `SCEVMC0` is slot 1 | PS3 (mislabelled) |
| `_epsxe` | 2 | zips of ePSXe's `epsxe000.mcr`, a raw card | PS3 (mislabelled) |

So 19 files sit in the wrong section. Three are filed under a region other than their saves': two
"Europe" FF7 zips hold the US save `BASCUS-94163FF7-S01` (one also the European `S03`), and a
"Europe" Tekken 3 raw card holds the Japanese `BISLPS-01300TEKKEN-3`. The European Star Ocean
saves are named `BASCES-02159...` (region letter A, a PAL serial). 11 cards hold no save at all,
though their descriptions promise one: 10 DexDrive cards (FF4, FF7, R4, Tekken 3 x2, THPS2 x5)
whose directory is all free and whose 15 data blocks each repeat one 8 KiB pattern, `MC`
followed by what looks like PC memory (a failed DexDrive read), and one all-zero VGS card
(Alundra 2). One European FF7 card holds only a deleted save. A card often holds other games'
saves; the entry is the whole card and is verified for the game its page is for.

`<release>` comes from the serial in the game's save name (`BASLUS-00422...` is SLUS-00422):
the library's Redump name for US discs, a redump.org lookup by serial for the others. For the
games whose serial is shared by two revisions in the library (Gran Turismo, Suikoden, FF
Chronicles) the entry names, and is verified on, the `(Rev 1)` disc the corpus already uses; the
save fits both. Multi-disc games are named for the disc whose serial the save carries (all of
these are Disc 1 serials). The R4 page also carries saves of the bonus discs packed with it
(`Ridge Racer Bonus Turbo Mode Disc (USA)`, `Ridge Racer Hi-Spec Demo (Europe)`,
`Ridge Racer - High Spec Ver. & Namco Catalogue '98 (Japan, Asia)`).

### Converting

`tools/gamefaqs/psx-card.py OUT.mcr INPUT...` writes the raw 131072-byte card that every
runnable core loads as card 1 (`<content>.srm`, loaded with `retro-run --srm`, never written
back). A whole card is unwrapped with its bytes unchanged, following DuckStation's
`ImportCardGME` / `ImportCardVGS` (skip 0xF40 or 64 bytes; a short `.gme` padded with zeroes; a
131072-byte `.gme` taken as raw) and MemcardRex's `OpenMemoryCard` (`PMV` 128-byte header; a
134976-byte file with `MC` at 3904 is a "GME with corrupted header"). Single saves (`.psv`, raw
blocks, `.mcs`) go onto a freshly formatted card as MemcardRex's `OpenSingleSave` +
`SetSaveBytes` do: name from 0x64 of a `.psv`; a raw block is named after its file, which for
`final-fantasy-vii.34525.gme` gives `final-fantasy-vii.34`, a name no game looks for (that block
is a European FF7 save, so it was not run anyway). `--ls` lists a card's saves. Converted cards
are in `.cache/gamefaqs-conv/psx/<id>/card1.mcr` (not filed); provenance records their sha1.

### Load scripts and runs

One `scripts/psx/<game>.load.txt` per game (27), from power-on to the screen that lists a save's
content: a Load/Continue file list for the RPGs and most others, the auto-load message for
Street Fighter Alpha 3 and DDR Konamix (frames every 40 from 1000 to 3000; the closest to the
message is kept), Simulation Mode > My Home for Gran Turismo (day, credits, car), Player Select
for Tekken 3 (unlocked fighters), the career / replay / park lists for THPS2 (Options > Memory
Card > Load Data and Load Replay, Park Editor > Load), Load Character for Diablo's
"saved characters" files. FF7 pages its 15-file list so the frame shows the save's slot. Each
script was run once per core with no card (baseline, `.cache/gamefaqs-conv/psx/_baseline/`) and
once per save per core.

The cores reach a title menu at very different times: PCSX-ReARMed reaches most titles after
fewer Start presses than Beetle, SwanStation sometimes after more (its intros run longer), and
an extra press picks the first menu item. Where the shared press count missed, a per-core
variant `<game>.<core>.load.txt` uses the core's own count (Air Combat, Diablo, Silent Hill on
PCSX-ReARMed and SwanStation; Mega Man X5, R4, T'ai Fu on PCSX-ReARMed) or, for SFA3 and DDR on
PCSX-ReARMed, an earlier frame window; provenance names it under `verified.script_variants`. SwanStation's Silent Hill title gives way to the intro movie
within a few seconds if left alone. Beetle PSX HW ran the same scripts as Beetle PSX with
identical timing.

### Results

Per core, over all 367 entries (`not-run` for 78 saves of releases the library lacks; DuckStation
and the MiSTer core cannot run here):

| Core | loads | rejected | core-error | not-run |
| --- | ---: | ---: | ---: | ---: |
| beetle-psx | 275 | 14 | 0 | 78 |
| beetle-psx-hw | 275 | 14 | 0 | 78 |
| pcsx-rearmed | 275 | 14 | 0 | 78 |
| swanstation | 275 | 14 | 0 | 78 |
| duckstation | 0 | 0 | 0 | 367 |
| psx-mister | 0 | 0 | 0 | 367 |

Per game (saves of the US releases the library has):

| Game (script) | saves | beetle-psx | beetle-psx-hw | pcsx-rearmed | swanstation |
| --- | ---: | --- | --- | --- | --- |
| Air Combat | 3 | 2 loads, 1 rejected | 2 loads, 1 rejected | 2 loads, 1 rejected | 2 loads, 1 rejected |
| Alundra 2 | 2 | 1 loads, 1 rejected | 1 loads, 1 rejected | 1 loads, 1 rejected | 1 loads, 1 rejected |
| Breath of Fire III | 12 | 12 loads | 12 loads | 12 loads | 12 loads |
| CTR - Crash Team Racing | 9 | 9 loads | 9 loads | 9 loads | 9 loads |
| Casper | 2 | 2 loads | 2 loads | 2 loads | 2 loads |
| Chrono Trigger | 4 | 4 loads | 4 loads | 4 loads | 4 loads |
| Dance Dance Revolution Konamix | 4 | 4 loads | 4 loads | 4 loads | 4 loads |
| Diablo | 4 | 4 loads | 4 loads | 4 loads | 4 loads |
| Emperor's New Groove | 1 | 1 loads | 1 loads | 1 loads | 1 loads |
| Final Fantasy IV | 5 | 4 loads, 1 rejected | 4 loads, 1 rejected | 4 loads, 1 rejected | 4 loads, 1 rejected |
| Final Fantasy VII | 47 | 46 loads, 1 rejected | 46 loads, 1 rejected | 46 loads, 1 rejected | 46 loads, 1 rejected |
| Gran Turismo | 14 | 14 loads | 14 loads | 14 loads | 14 loads |
| Legend of Dragoon | 19 | 19 loads | 19 loads | 19 loads | 19 loads |
| Loaded | 6 | 6 loads | 6 loads | 6 loads | 6 loads |
| Mega Man X5 | 6 | 6 loads | 6 loads | 6 loads | 6 loads |
| Persona | 4 | 4 loads | 4 loads | 4 loads | 4 loads |
| R4 - Ridge Racer Type 4 | 3 | 2 loads, 1 rejected | 2 loads, 1 rejected | 2 loads, 1 rejected | 2 loads, 1 rejected |
| Silent Hill | 12 | 12 loads | 12 loads | 12 loads | 12 loads |
| Spyro the Dragon | 8 | 8 loads | 8 loads | 8 loads | 8 loads |
| Star Ocean - The Second Story | 17 | 17 loads | 17 loads | 17 loads | 17 loads |
| Street Fighter Alpha 3 | 2 | 2 loads | 2 loads | 2 loads | 2 loads |
| Suikoden | 19 | 18 loads, 1 rejected | 18 loads, 1 rejected | 18 loads, 1 rejected | 18 loads, 1 rejected |
| T'ai Fu - Wrath of the Tiger | 1 | 1 loads | 1 loads | 1 loads | 1 loads |
| Tekken 3 | 6 | 4 loads, 2 rejected | 4 loads, 2 rejected | 4 loads, 2 rejected | 4 loads, 2 rejected |
| Tony Hawk's Pro Skater 2 | 55 | 50 loads, 5 rejected | 50 loads, 5 rejected | 50 loads, 5 rejected | 50 loads, 5 rejected |
| Warhammer - Shadow of the Horned Rat | 1 | 1 loads | 1 loads | 1 loads | 1 loads |
| Xenogears | 23 | 22 loads, 1 rejected | 22 loads, 1 rejected | 22 loads, 1 rejected | 22 loads, 1 rejected |

Releases the library lacks (every core `not-run`; the cards were still converted):

| Release | Saves |
| --- | ---: |
| Air Combat (Europe) | 1 |
| Breath of Fire III (Europe) | 1 |
| CTR - Crash Team Racing (Europe) (En,Fr,De,Es,It,Nl) | 5 |
| Crash Bandicoot Racing (Japan, Asia) | 1 |
| Diablo (Europe) (En,Fr,De,Sv) | 1 |
| Final Fantasy VII (Europe) (Disc 1) | 10 |
| Final Fantasy VII (Japan) (Disc 1) | 2 |
| Final Fantasy VII International (Japan) (Disc 1) | 2 |
| Gran Turismo (Europe) (En,Fr,De,Es,It) | 4 |
| Gran Turismo (Japan, Asia) | 8 |
| Legend of Dragoon, The (Europe) (Disc 1) | 4 |
| Loaded (Europe) (En,Fr,De) | 1 |
| Megami Ibunroku - Persona - Be Your True Mind (Japan) | 1 |
| Ridge Racer - High Spec Ver. & Namco Catalogue '98 (Japan, Asia) | 1 |
| Ridge Racer Hi-Spec Demo (Europe) | 1 |
| Rockman X5 (Japan) | 4 |
| Silent Hill (Europe) (En,Fr,De,Es,It) | 5 |
| Silent Hill (Japan) | 2 |
| Spyro the Dragon (Europe, Australia) (En,Fr,De,Es,It) | 2 |
| Spyro the Dragon (Japan, Asia) (Shokai Genteiban) | 1 |
| Star Ocean - The Second Story (Europe) (Disc 1) | 2 |
| Street Fighter Alpha 3 (Europe) | 1 |
| Street Fighter Zero 3 (Japan) | 5 |
| Suikoden (Europe) | 2 |
| T'ai Fu - Wrath of the Tiger (Europe) | 1 |
| Tekken 3 (Europe, Australia) | 4 |
| Tekken 3 (Japan, Asia) | 6 |

### Findings

- **No core rejects a valid card.** All four cores agree on every one of the 289 runnable saves:
  the same 275 load and the same 14 do not, and their frames show the same content, each core at
  its own resolution. The differences between cores are all timing: PCSX-ReARMed skips the BIOS
  start-up logo (SFA3 says "AUTO LOAD COMPLETE!" before frame 1000 there, around frame 1750 on
  Beetle PSX), and SwanStation plays some intros longer. The one visible difference: PCSX-ReARMed
  always has a card in slot 2 (`pcsx-card2.mcd`, above), so games that show both slots say slot 2
  holds no data (Silent Hill "No data file", Diablo "EMPTY", Xenogears' second block grid) where
  the other cores say no card is inserted.
- **The 14 that no core loads**, by cause: 11 cards hold no save at all (above); Air Combat 10841
  is a `.gme` damaged in transit: every 0x0A byte has a 0x0D before it (345 each, exactly the
  file's excess over 134976), the mark of a text-mode LF to CRLF transfer, so the card the
  references unwrap has its save block shifted. Removing those 0x0D bytes by hand gives a card
  that Beetle PSX loads (eight squadrons, F-22s, as described). Suikoden 1954's save has a
  wrong directory checksum (0x12, should be 0x1B); with it corrected by hand Suikoden lists the
  save (Marth, Lv. 60). The converter keeps the card's bytes as DuckStation does; MemcardRex
  recomputes directory checksums on open, so a card exported from it would load. Xenogears 223
  holds one live save, `BASLUS-006640` ("XENOGEARS/No.01 First and Last"), with a valid directory
  frame, which Xenogears does not mark; cause not found.
- **Cut-short `.gme`s load.** All 22 hold their saves in the blocks present, and zero padding
  (DuckStation's behaviour) gives a card the cores and games accept: of the 21 runnable, all
  load but Suikoden 1954 (its checksum, above). The 8 `.gme`s with a blank header load too
  (those runnable).
- **Silent Hill 6847** loads its save without being asked: with that card the game shows
  "Finished loading" (File 1, Child's room) before the title and drops Harry into the room the
  file was saved in, on every core, so its proof shows the room rather than the file list.
- Saves for Japanese and European releases cannot be checked here: the library holds US discs
  only. A US disc does not list them (FF7 19350 holds a US and a European save; the US disc
  lists only the US one).

### one-saves

`1saves convert --system psx` + `inspect` + `extract` were run on every original. It reads 330
of the 367; for those, its card lists the same live saves as `psx-card.py`'s in every case, and
every live save's blocks are byte-identical. It does not read: the 22 cut-short `.gme`s, the 8
`.gme`s with a blank header and the one with 345 extra bytes ("a PS1 memory card is 131072
bytes, or that behind a DexDrive, VGS or PSP header"), the three raw save blocks (an 8192-byte
`.gme`, and the two zips of a raw block named `.PSV`: "holds no card and no save this reads"),
and the three PSP save folders ("this archive holds 2 cards"). DuckStation's importer reads the
first three kinds. The cards it extracts differ from the converter's for 193 inputs, never in a live save:
it drops deleted directory entries (49 cards had some), zeroes the free blocks (a DexDrive card
keeps whatever was in them, often `MC` pages) and writes free directory frames with a `FFFF`
next pointer. 34 saves with PocketStation-style serials (`BISLPSP01777`, `BESCESP03043`,
`BASLUSP00797`, `BASLUSP00821`, `BASLUSP00896`, `BESLESP01863`, `BASLUSP01060`) are left
"unidentified" while `BASLUS-00422...` resolves to SLUS-00422, as already seen for R4 and SFA3.
