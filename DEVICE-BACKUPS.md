# Device backups

The owner's own saves from their own devices, filed on 2026-11-03 with the owner's approval of these
two backups. None of it comes from 1Retro or from a sync folder of it. Every entry's
`provenance.json` has `"method": "device-backup"`, the device, `backup_path` (relative to the device's SD card), how the
core was attributed and how sure that is.

| Source | Device | Filed |
| --- | --- | --- |
| `Saves/` | Analogue Pocket | 93 entries: all 86 saves outside the jotego folders, the one jotego save the core wrote, and 6 of the 369 jotego stock files as examples |
| `JKSV/` | Nintendo 2DS, JKSV | 12 titles under `3ds/_jksv/`, 244 files (22 save files, 222 extdata files) |

Used as evidence only, never filed: older card snapshots (December
2023, with `Cores/`, `Settings/`, `Presets/`, `pocket_updater_*.json` and `pocket-sync.json`;
their `Saves/` are empty), the card's `Assets/` (February 2026), the cores' published
sources and release dates on GitHub, and the No-Intro DATs.

## How a Pocket save was attributed

The Pocket files a save by platform, not by core: `Saves/<platform>/common/<the ROM's path under
Assets/<platform>/common>/<ROM stem>.sav`, and every core of that platform reads and writes the same
file. The folder settles the core only for cores that load instance JSONs (`Saves/<platform>/<core
id>/<instance name>.sav`: the Neo Geo and PC Engine CD cores) and for slots with a fixed file name
(`backup.bak`, `palram.bin`). Elsewhere the evidence was:

- **Which cores could have run.** The December 2023 snapshot's `Cores/` holds agg23.NES, agg23.PC
  Engine, agg23.SNES, Mazamars312.PC Engine CD, Spiritualized GB, GBC, GBA, Genesis, GG, NES,
  SG-1000, SMS and SuperGB. `Assets/` adds the three Neo Geo builds, the Analogizer builds,
  Spiritualized.SuperGB2 and 67 jotego cores. budude2's `gb_bios.bin` appears in
  `Assets/gb/common` on 2024-01-04. Release dates rule cores out: budude2 GB/GBC first released on
  2024-01-02 (split into two cores on 2024-01-04), mincer_ray.GBA on 2026-03-13 and drizzt.MegaDrive
  on 2026-07-30, both after this backup. Spiritualized.GB's last release (1.3.0, 2022) loads only
  `.gb`.
- **Size and padding.** Each core's rule is in the section below. In these files the rules never
  overlap: a 16-byte footer means budude2, 256 KiB means agg23.NES, 128 KiB means
  Spiritualized.Genesis.
- **Dates.** Each file's mtime is the Pocket's own clock. Three files are dated 2020-01-02, the
  Pocket's date before its clock is set. The `Settings/*/interact_persist.json` files in the 2023
  snapshots sit exactly one hour after the save they go with, in all three cases that pair up
  (Spiritualized.GBA against a GBA save on 2023-09-22, agg23.PC Engine against a PCE save on
  2023-05-21, Spiritualized.GBC against Kaeru on 2023-10-11), so the backups are offset by one hour
  from each other. Settings times are compared after allowing for that hour.
- **System.** The system is set by the game's No-Intro set, as elsewhere in the corpus: a Game Boy
  game the owner ran in the GBC core is under `gb/spiritualized-gbc/`, and a Game Boy Color game run
  in budude2.GB is under `gbc/budude2-gb/`. The Pocket's folder is kept in `pocket_platform`.
- **Names.** The game folder is the current No-Intro name, checked against the DAT, even where the
  card used an older one (`Rev A` → `Rev 1`, `Oracle of Ages (USA)` → `(USA, Australia)`). The file
  inside keeps the name the core gave it. Translations, hacks, ROMs named without a region and
  instance names keep the file's own stem. The owner moved the library about, so one game can have
  saves from several ROM paths (`games/...`, `Top 100 List - GameFAQs.com/001 ...`). When one core
  has more than one save for a game, each folder name ends in `[write date]`.

### The two judgement calls

1. **Game Boy Color games in `Saves/gb/common` written before 2024-02** (Link's Awakening DX,
   Bomberman Max Blue, Dragon Warrior III, both Dragon Warrior Monsters 2). Each is exactly the
   header's RAM size with no footer. The Dragon Warrior Monsters 2 Tara file is dated 2024-01-07,
   after budude2 was installed, but budude2 1.0.0-1.0.6 wrote 32777 bytes for every cart, so a
   Spiritualized core wrote all of these. The ROMs are `.gbc`, which Spiritualized.GB cannot pick.
   In 2023, Spiritualized.GBC loaded the same ROMs from `Assets/gbc/common/1 GBC US - A-L`. That
   folder is gone from `Saves/gbc`, and the owner merged the GBC library into `gb/common` in July
   2024 (`Assets/gbc/common/games -> ../../gb/common`, 2024-07-22). So these are filed as
   **spiritualized-gbc** with a save that was moved, at *medium* confidence. If the Pocket did not
   enforce `.gb` for Spiritualized.GB, that core wrote them instead. Both cores write the same
   layout.
2. **Kaeru no Tame ni Kane wa Naru (english translation)**, `gb/common`, 2023-10-11 21:48. The `.gb`
   ROM was only under `gb/common`, which points to Spiritualized.GB. But Spiritualized.GBC's
   settings were written at the same minute, so it is filed as spiritualized-gb at *medium*
   confidence.

Every other entry is *high*, except Link's Awakening (DMG, 2025) and Sonic 1, which are *medium*.
Link's Awakening is put down to Spiritualized.GB only because budude2's footer is missing. Sonic 1 is
put down to ericlewis.Genesis by its 64 KiB size, and Spiritualized.Genesis's unpublished source
might write 64 KiB too for a game without save RAM.

## Every filed entry

### Analogue Pocket

| System | Core | Game | Pocket path | Size | Attribution | Confidence |
| --- | --- | --- | --- | ---: | --- | --- |
| gb | budude2-gb | Super Mario Land 2 - 6 Golden Coins (USA, Europe) (Rev 2) | `gb/common/1 GB US - R-Z/Super Mario Land 2 - 6 Golden Coins (USA, Europe) (Rev 2).sav` | 8208 | 16-byte budude2 clock footer; gb folder | high |
| gb | spiritualized-gb | Donkey Kong (World) (Rev 1) (SGB Enhanced) | `gb/common/1 GB US - A-G/Donkey Kong (World) (Rev 1) (SGB Enhanced).sav` | 8192 | gb folder, .gb ROM, before budude2 existed; header RAM size, no footer | high |
| gb | spiritualized-gb | Kaeru no Tame ni Kane wa Naru (english translation) | `gb/common/4 Translations/Kaeru no Tame ni Kane wa Naru (english translation).sav` | 8192 | gb folder, .gb ROM; but GBC core's settings written the same minute | medium |
| gb | spiritualized-gb | Kirby's Dream Land 2 (USA, Europe) (SGB Enhanced) | `gb/common/1 GB US - H-Q/Kirby's Dream Land 2 (USA, Europe) (SGB Enhanced).sav` | 8192 | gb folder, .gb ROM, before budude2 existed; header RAM size, no footer | high |
| gb | spiritualized-gb | Legend of Zelda, The - Link's Awakening (USA, Europe) (Rev 2) | `gb/common/1 GB US - H-Q/Legend of Zelda, The - Link's Awakening (USA, Europe) (Rev 2).sav` | 8192 | no footer; budude2.GB (also installed) adds 16 B to every save | medium |
| gb | spiritualized-gb | Oni 4 - Kishin no Ketsuzoku (J) [T+Eng0.30_akujin] | `gb/common/4 Translations/Oni 4 - Kishin no Ketsuzoku (J) [T+Eng0.30_akujin].sav` | 8192 | gb folder, .gb ROM, before budude2 existed; header RAM size, no footer | high |
| gb | spiritualized-gb | Pokemon - Red Version (USA, Europe) (SGB Enhanced) | `gb/common/1 GB US - H-Q/Pokemon - Red Version (USA, Europe) (SGB Enhanced).sav` | 32768 | gb folder, .gb ROM, before budude2 existed; header RAM size, no footer | high |
| gb | spiritualized-gb | Pokemon - Yellow Version - Special Pikachu Edition (USA, Europe) (CGB+SGB Enhanced) | `gb/common/1 GB US - H-Q/Pokemon - Yellow Version - Special Pikachu Edition (USA, Europe) (CGB+SGB Enhanced).sav` | 32768 | gb folder, .gb ROM, before budude2 existed; header RAM size, no footer | high |
| gb | spiritualized-gbc | Pokemon - Blue Version (USA, Europe) (SGB Enhanced) | `gbc/common/Pokemon - Blue Version (USA, Europe) (SGB Enhanced).sav` | 32768 | gbc folder; only gbc core then; header RAM size, no footer | high |
| gb | spiritualized-gbc | Pokemon - Red Version (USA, Europe) (SGB Enhanced) | `gbc/common/Pokemon - Red Version (USA, Europe) (SGB Enhanced).sav` | 32768 | gbc folder; only gbc core then; header RAM size, no footer | high |
| gb | spiritualized-gbc | Super Mario Land 2 - 6 Golden Coins (USA, Europe) (Rev 2) | `gbc/common/Super Mario Land 2 - 6 Golden Coins (USA, Europe) (Rev B).sav` | 8192 | gbc folder; only gbc core then; header RAM size, no footer | high |
| gb | spiritualized-gbc | Wario Land - Super Mario Land 3 (World) | `gbc/common/Wario Land - Super Mario Land 3 (World).sav` | 8192 | gbc folder; only gbc core then; header RAM size, no footer | high |
| gb | spiritualized-supergb | run_cartridge (physical cartridge) | `sgb/common/run_cartridge.sav` | 8192 | sgb folder; only sgb core; run_cartridge.gb stub = physical cart | high |
| gba | spiritualized-gba | Bomberman Max 2 - Blue Advance (USA) | `gba/common/1 USA - A-C/Bomberman Max 2 - Blue Advance (USA).sav` | 8192 | only GBA core then; exact save-type size (mincer_ray pads to 64 KiB) | high |
| gba | spiritualized-gba | Castlevania - Aria of Sorrow (USA) | `gba/common/1 USA - A-C/Castlevania - Aria of Sorrow (USA).sav` | 32768 | only GBA core then; exact save-type size (mincer_ray pads to 64 KiB) | high |
| gba | spiritualized-gba | Castlevania - Circle of the Moon (USA) | `gba/common/1 USA - A-C/Castlevania - Circle of the Moon (USA).sav` | 32768 | only GBA core then; exact save-type size (mincer_ray pads to 64 KiB) | high |
| gba | spiritualized-gba | Dragon Quest Monsters - Caravan Heart (Japan) T+Eng v1 KaioShin | `gba/common/4 Translations/Dragon Quest Monsters - Caravan Heart (Japan) T+Eng v1 KaioShin.sav` | 8192 | only GBA core then; exact save-type size (mincer_ray pads to 64 KiB) | high |
| gba | spiritualized-gba | Drill Dozer (USA) | `gba/common/1 USA - D-H/Drill Dozer (USA).sav` | 32768 | only GBA core then; exact save-type size (mincer_ray pads to 64 KiB) | high |
| gba | spiritualized-gba | Legend of Zelda, The - A Link to the Past & Four Swords (USA) | `gba/common/1 USA - I-O/Legend of Zelda, The - A Link to the Past & Four Swords (USA).sav` | 8192 | only GBA core then; exact save-type size (mincer_ray pads to 64 KiB) | high |
| gba | spiritualized-gba | Legend of Zelda, The - The Minish Cap (USA) | `gba/common/1 USA - I-O/Legend of Zelda, The - The Minish Cap (USA).sav` | 8192 | only GBA core then; exact save-type size (mincer_ray pads to 64 KiB) | high |
| gba | spiritualized-gba | Mario & Luigi - Superstar Saga (USA) | `gba/common/Mario & Luigi - Superstar Saga (USA, Australia).sav` | 8192 | only GBA core then; exact save-type size (mincer_ray pads to 64 KiB) | high |
| gba | spiritualized-gba | Pokemon Pinball - Ruby & Sapphire (USA) | `gba/common/1 USA - P-S/Pokemon Pinball - Ruby & Sapphire (USA).sav` | 32768 | only GBA core then; exact save-type size (mincer_ray pads to 64 KiB) | high |
| gba | spiritualized-gba | Wario Land 4 (USA, Europe) | `gba/common/1 USA - T-Z/Wario Land 4 (USA, Europe).sav` | 32768 | only GBA core then; exact save-type size (mincer_ray pads to 64 KiB) | high |
| gbc | budude2-gb | Pokemon Trading Card Game (USA, Australia) (SGB Enhanced) (GB Compatible) | `gb/common/1 GBC US - M-Z/Pokemon Trading Card Game (USA, Australia) (SGB Enhanced) (GB Compatible).sav` | 32784 | 16-byte budude2 clock footer; gb folder | high |
| gbc | budude2-gb | Shantae (USA) | `gb/common/1 GBC US - M-Z/Shantae (USA).sav` | 8208 | 16-byte budude2 clock footer; gb folder | high |
| gbc | budude2-gb | Wario Land II (USA, Europe) (SGB Enhanced) (GB Compatible) | `gb/common/1 GBC US - M-Z/Wario Land II (USA, Europe) (SGB Enhanced) (GB Compatible).sav` | 32784 | 16-byte budude2 clock footer; gb folder | high |
| gbc | spiritualized-gbc | Bomberman Max - Blue Champion (USA) | `gb/common/1 GBC US - A-L/Bomberman Max - Blue Champion (USA).sav` | 8192 | .gbc ROM + no footer + no budude2 yet: GBC core, save moved from gbc/ when the library merged | medium |
| gbc | spiritualized-gbc | Dragon Warrior I & II (USA) (SGB Enhanced) (GB Compatible) | `gbc/common/Dragon Warrior I & II (USA) (SGB Enhanced).sav` | 8192 | gbc folder; only gbc core then; header RAM size, no footer | high |
| gbc | spiritualized-gbc | Dragon Warrior III (USA) | `gb/common/1 GBC US - A-L/Dragon Warrior III (USA).sav` | 32768 | .gbc ROM + no footer + no budude2 yet: GBC core, save moved from gbc/ when the library merged | medium |
| gbc | spiritualized-gbc | Dragon Warrior Monsters 2 - Cobi's Journey (USA) (SGB Enhanced) (GB Compatible) | `gb/common/1 GBC US - A-L/Dragon Warrior Monsters 2 - Cobi's Journey (USA) (SGB Enhanced) (GB Compatible).sav` | 32768 | .gbc ROM + no footer + no budude2 yet: GBC core, save moved from gbc/ when the library merged | medium |
| gbc | spiritualized-gbc | Dragon Warrior Monsters 2 - Tara's Adventure (USA) (SGB Enhanced) (GB Compatible) [2022-07-20] | `gbc/common/Dragon Warrior Monsters 2 - Tara's Adventure (USA) (SGB Enhanced).sav` | 32768 | gbc folder; only gbc core then; header RAM size, no footer | high |
| gbc | spiritualized-gbc | Dragon Warrior Monsters 2 - Tara's Adventure (USA) (SGB Enhanced) (GB Compatible) [2023-01-16] | `gbc/common/Dragon Warrior Monsters 2 - Tara's Adventure (USA).sav` | 32768 | gbc folder; only gbc core then; header RAM size, no footer | high |
| gbc | spiritualized-gbc | Dragon Warrior Monsters 2 - Tara's Adventure (USA) (SGB Enhanced) (GB Compatible) [2024-01-07] | `gb/common/1 GBC US - A-L/Dragon Warrior Monsters 2 - Tara's Adventure (USA) (SGB Enhanced) (GB Compatible).sav` | 32768 | .gbc ROM + no footer + no budude2 yet: GBC core, save moved from gbc/ when the library merged | medium |
| gbc | spiritualized-gbc | Legend of Zelda, The - Link's Awakening DX (USA, Europe) (Rev 2) (SGB Enhanced) (GB Compatible) | `gb/common/1 GBC US - A-L/Legend of Zelda, The - Link's Awakening DX (USA, Europe) (Rev 2) (SGB Enhanced) (GB Compatible).sav` | 32768 | .gbc ROM + no footer + no budude2 yet: GBC core, save moved from gbc/ when the library merged | medium |
| gbc | spiritualized-gbc | Legend of Zelda, The - Oracle of Ages (USA, Australia) | `gbc/common/Legend of Zelda, The - Oracle of Ages (USA).sav` | 8192 | gbc folder; only gbc core then; header RAM size, no footer | high |
| gbc | spiritualized-gbc | Legend of Zelda, The - Oracle of Seasons (USA, Australia) | `gbc/common/Legend of Zelda, The - Oracle of Seasons (USA).sav` | 8192 | gbc folder; only gbc core then; header RAM size, no footer | high |
| gbc | spiritualized-gbc | Pokemon Pinball (USA, Australia) (Rumble Version) (SGB Enhanced) (GB Compatible) | `gbc/common/Pokemon Pinball (USA) (SGB Enhanced).sav` | 8192 | gbc folder; only gbc core then; header RAM size, no footer | high |
| gbc | spiritualized-gbc | Super Mario Bros. Deluxe (USA, Europe) (Rev 1) | `gbc/common/Super Mario Bros. Deluxe (USA, Europe) (Rev A).sav` | 8192 | gbc folder; only gbc core then; header RAM size, no footer | high |
| gbc | spiritualized-gbc | Wario Land 3 (World) (En,Ja) | `gbc/common/Wario Land 3 (World) (En,Ja).sav` | 32768 | gbc folder; only gbc core then; header RAM size, no footer | high |
| genesis | ericlewis-genesis | Sonic The Hedgehog (USA, Europe) | `genesis/common/Sonic The Hedgehog (USA, Europe).sav` | 65536 | 64 KiB = ericlewis fixed size (Spiritualized wrote 128 KiB) | medium |
| genesis | spiritualized-genesis | Sonic The Hedgehog 3 (USA) | `genesis/common/1 US - Q-Z/Sonic The Hedgehog 3 (USA).sav` | 131072 | 128 KiB = Spiritualized slot max; ericlewis always 64 KiB | high |
| mame | _jotego.jtcps1 | megaman | `jtcps1/common/megaman.sav` | 128 | platform folder; not a jotego default | high |
| mame | _jotego.jtcps2 | sfa3 | `jtcps2/common/sfa3.sav` | 128 | jotego stock default (jtbin), not core-written | n/a (stock file) |
| mame | _jotego.jtriders | ssriders | `jtriders/common/ssriders.sav` | 128 | jotego stock default (jtbin), not core-written | n/a (stock file) |
| mame | _jotego.jtshouse | shadowld | `jtshouse/common/shadowld.sav` | 63552 | jotego stock default (jtbin), not core-written | n/a (stock file) |
| mame | _jotego.jtshouse | wldcourt | `jtshouse/common/wldcourt.sav` | 2048 | jotego stock default (jtbin), not core-written | n/a (stock file) |
| mame | _jotego.jtsimson | simpsons | `jtsimson/common/simpsons.sav` | 144 | jotego stock default (jtbin), not core-written | n/a (stock file) |
| mame | _jotego.jtxmen | xmen | `jtxmen/common/xmen.sav` | 128 | jotego stock default (jtbin), not core-written | n/a (stock file) |
| neogeo | _Mazamars312.NeoGeo_Overdrive | _backup-ram | `ng/Mazamars312.NeoGeo_Overdrive/backup.bak` | 65536 | core folder (build not in registry) | high |
| neogeo | mazamars312-neogeo | Metal Slug | `ng/Mazamars312.NeoGeo_Analogizer/Metal Slug.sav` | 8192 | core folder | high |
| neogeo | mazamars312-neogeo | Metal Slug 2 | `ng/Mazamars312.NeoGeo_Analogizer/Metal Slug 2.sav` | 8192 | core folder | high |
| neogeo | mazamars312-neogeo | Metal Slug 3 | `ng/Mazamars312.NeoGeo_Analogizer/Metal Slug 3.sav` | 8192 | core folder | high |
| neogeo | mazamars312-neogeo | _backup-ram [2024-07-23] | `ng/Mazamars312.NeoGeo/backup.bak` | 65536 | core folder | high |
| neogeo | mazamars312-neogeo | _backup-ram [2025-10-31] | `ng/common/backup.bak` | 65536 | mtime = Analogizer build's Metal Slug 2.sav, to the minute | medium |
| nes | agg23-nes | Crystalis (USA) | `nes/common/1 US - A-F/Crystalis (USA).sav` | 262144 | 256 KiB = agg23 slot size, always written whole | high |
| nes | agg23-nes | Dragon Warrior IV (USA) | `nes/common/1 US - A-F/Dragon Warrior IV (USA).sav` | 262144 | 256 KiB = agg23 slot size, always written whole | high |
| nes | agg23-nes | Lagrange Point (J) T+Eng v1.01 Aeon Genesis | `nes/common/4 Translations/English L-Z/Lagrange Point (J) T+Eng v1.01 Aeon Genesis.sav` | 262144 | 256 KiB = agg23 slot size, always written whole | high |
| nes | agg23-nes | Legend of Zelda, The (USA) (Rev 1) | `nes/common/1 US - G-Q/Legend of Zelda, The (USA) (Rev 1).sav` | 262144 | 256 KiB = agg23 slot size, always written whole | high |
| nes | agg23-nes | StarTropics (USA) | `nes/common/1 US - R-Z/StarTropics (USA).sav` | 262144 | 256 KiB = agg23 slot size, always written whole | high |
| nes | agg23-nes | The Legend of Zelda, Ancient Dungeon | `nes/common/games/Patched/The Legend of Zelda, Ancient Dungeon.sav` | 262144 | 256 KiB = agg23 slot size, always written whole | high |
| nes | spiritualized-nes | Dragon Warrior IV (USA) | `nes/common/games/1 US - A-F/Dragon Warrior IV (USA).sav` | 8192 | 8 KiB; agg23 always writes 256 KiB | high |
| nes | spiritualized-nes | Lagrange Point (J) T+Eng v1.01 Aeon Genesis | `nes/common/games/4 Translations/English L-Z/Lagrange Point (J) T+Eng v1.01 Aeon Genesis.sav` | 8192 | 8 KiB; agg23 always writes 256 KiB | high |
| nes | spiritualized-nes | Legend of Zelda, The (USA) (Rev 1) | `nes/common/games/1 US - G-Q/Legend of Zelda, The (USA) (Rev 1).sav` | 8192 | 8 KiB; agg23 always writes 256 KiB | high |
| nes | spiritualized-nes | _palette-ram (palram.bin) | `nes/Spiritualized.NES/palram.bin` | 2048 | core folder; the core's palette-RAM slot, not a game save | high |
| pcengine | agg23-pc-engine | Devil's Crush (USA) | `pce/common/4 Game Series Collections/Best-Of Lists/Top 10 Games - Blockfort.com/03. Devil's Crush (USA).sav` | 2048 | only PC Engine core | high |
| pcengine | agg23-pc-engine | Neutopia (USA) [2023-05-21] | `pce/common/games/Neutopia (USA).sav` | 2048 | only PC Engine core | high |
| pcengine | agg23-pc-engine | Neutopia (USA) [2026-02-14] | `pce/common/1 TurboGrafx-16 - A-Z/Neutopia (USA).sav` | 2048 | only PC Engine core | high |
| pcenginecd | mazamars312-pc-engine-cd | Akumajou Dracula X - Chi no Rondo (Japan) (FABT, FACT) | `pcecd/Mazamars312.PC Engine CD/Akumajou Dracula X - Chi no Rondo (Japan) (FABT, FACT).sav` | 2048 | core folder (instance JSON) | high |
| pcenginecd | mazamars312-pc-engine-cd | Dracula X ISO (Binchunker) | `pcecd/Mazamars312.PC Engine CD/Dracula X ISO (Binchunker).sav` | 2048 | core folder (instance JSON) | high |
| pcenginecd | mazamars312-pc-engine-cd | Dungeon Master - Theron's Quest (USA) | `pcecd/Mazamars312.PC Engine CD/Dungeon Master - Theron's Quest (USA).sav` | 2048 | core folder (instance JSON) | high |
| pcenginecd | mazamars312-pc-engine-cd | Ys Book I & II (USA) | `pcecd/Mazamars312.PC Engine CD/Ys Book I & II (USA).sav` | 2048 | core folder (instance JSON) | high |
| pcenginecd | mazamars312-pc-engine-cd | Ys III - Wanderers from Ys (USA) | `pcecd/Mazamars312.PC Engine CD/Ys III - Wanderers from Ys (USA).sav` | 2048 | core folder (instance JSON) | high |
| snes | agg23-snes | ActRaiser (USA) | `snes/common/games/1 US - A-E/ActRaiser (USA).sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Chrono Trigger | `snes/common/Chrono Trigger.sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Chrono Trigger BugFix | `snes/common/Chrono Trigger BugFix.sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Dragon Quest III - Soshite Densetsu e... (J) T+Eng v1.0c Rod Merida | `snes/common/games/4 Translations/English/English A-M/Dragon Quest III - Soshite Densetsu e... (J) T+Eng v1.0c Rod Merida.sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Dragon Quest V - Tenkuu no Hanayome (J) T+Eng v2.01F DeJap | `snes/common/games/4 Translations/English/English A-M/Dragon Quest V - Tenkuu no Hanayome (J) T+Eng v2.01F DeJap.sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Legend of Zelda, The - A Link to the Past (USA) [2022-12-20] | `snes/common/games/4 Game Series Collections/Best-Of Lists/Top 100 List - GameFAQs.com/001 Legend of Zelda, The - A Link to the Past (USA).sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Legend of Zelda, The - A Link to the Past (USA) [2023-05-12] | `snes/common/Top 100 List - GameFAQs.com/001 Legend of Zelda, The - A Link to the Past (USA).sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Legend of Zelda, The - A Link to the Past (USA) [2025-03-31] | `snes/common/games/1 US - F-M/Legend of Zelda, The - A Link to the Past (USA).sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Lufia & the Fortress of Doom (USA) [2023-01-17] | `snes/common/Top 100 List - GameFAQs.com/038 Lufia & the Fortress of Doom (USA).sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Lufia & the Fortress of Doom (USA) [2024-07-25] | `snes/common/games/1 US - F-M/Lufia & the Fortress of Doom (USA).sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Super Mario All-Stars (USA) | `snes/common/games/1 US - S/Super Mario All-Stars (USA).sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Super Mario Kart (USA) [2022-12-22] | `snes/common/Top 100 List - GameFAQs.com/008 Super Mario Kart (USA).sav` | 2048 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Super Mario Kart (USA) [2025-01-18] | `snes/common/games/1 US - S/Super Mario Kart (USA).sav` | 2048 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Super Mario RPG - Legend of the Seven Stars | `snes/common/Super Mario RPG - Legend of the Seven Stars.sav` | 32768 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Super Mario World | `snes/common/Super Mario World.sav` | 2048 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Super Mario World (USA) [2023-02-22] | `snes/common/Top 100 List - GameFAQs.com/003 Super Mario World (USA).sav` | 2048 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Super Mario World (USA) [2025-06-25] | `snes/common/games/1 US - S/Super Mario World (USA).sav` | 2048 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Super Metroid (Japan, USA) (En,Ja) [2023-01-10] | `snes/common/Top 100 List - GameFAQs.com/005 Super Metroid (Japan, USA) (En,Ja).sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Super Metroid (Japan, USA) (En,Ja) [2024-08-09] | `snes/common/games/1 US - S/Super Metroid (Japan, USA) (En,Ja).sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | Terranigma (Europe) | `snes/common/games/2 Europe - A-Z/PAL - S-Z/Terranigma (Europe).sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |
| snes | agg23-snes | backup_legend_of_zelda | `snes/common/backup_legend_of_zelda.sav` | 8192 | only SNES core; no .mk3sav; header SRAM size | high |

### Nintendo 2DS (JKSV)

Each title folder keeps JKSV's own layout:
`3ds/_jksv/<No-Intro name>/Saves/<JKSV name>/<YYYY.MM.DD_hh.mm.ss>/...`, plus `ExtData/<JKSV
name>/<stamp>/...` where the title has extdata. `provenance.json` gives every file its registry
role, `primary` or `extdata`. JKSV's title cache (`JKSV/titles`) gave the product code and title
ID. The No-Intro 3DS DAT gave the name, using the entry without a revision, since the backup does
not say which revision was used. All are *high* confidence: they are JKSV backups from real
hardware.

| Folder | JKSV name | Product code | Title ID | Save files | Extdata files | Bytes |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Dragon Quest VII - Fragments of the Forgotten Past (USA) | `DRAGON QUEST VII` | CTR-P-AD7E | 000400000018EF00 | 5 | 0 | 61992 |
| Dragon Quest VIII - Journey of the Cursed King (USA) | `Dragon Quest VIII` | CTR-P-BQ8E | 000400000018F100 | 1 | 1 | 212564 |
| Kirby - Triple Deluxe (USA) (En,Fr,Es) | `Kirby  Triple Deluxe` | CTR-P-BALE | 000400000010BF00 | 1 | 0 | 14560 |
| Legend of Zelda, The - Majora's Mask 3D (USA) (En,Fr,Es) | `Majora's Mask 3D` | CTR-P-AJRE | 0004000000125500 | 1 | 0 | 79384 |
| Metroid - Samus Returns (USA) (En,Fr,Es) | `Metroid  Samus Returns` | CTR-P-A9AE | 00040000001BB200 | 3 | 0 | 25751 |
| My Nintendo PICROSS | `My Nintendo PICROSS` | CTR-N-JHXA | 0004000000186700 | 1 | 0 | 920 |
| New Super Mario Bros. 2 (USA) (En,Fr,Es) | `New Super Mario Bros  2` | CTR-P-ABEE | 000400000007AE00 | 1 | 0 | 10296 |
| Legend of Zelda, The - Ocarina of Time 3D (USA) (En,Fr,Es) | `Ocarina of Time 3D` | CTR-P-AQEE | 0004000000033500 | 2 | 0 | 5374 |
| Super Mario 3D Land (USA) (En,Fr,Es) | `SUPER MARIO 3D LAND` | CTR-P-AREE | 0004000000054000 | 1 | 0 | 18444 |
| Super Mario Maker for Nintendo 3DS (USA) | `Super Mario Maker` | CTR-P-AJHE | 00040000001A0400 | 1 | 221 | 60421188 |
| Legend of Zelda, The - A Link Between Worlds (USA) (En,Fr,Es) | `The Legend of Zelda` | CTR-P-BZLE | 00040000000EC300 | 4 | 0 | 17420 |
| Ultimate NES Remix (USA) (En,Fr,Es) | `Ultimate NES Remix` | CTR-P-BFRE | 0004000000132000 | 1 | 0 | 244704 |

Notes on the 3DS backups:

- JKSV turns `:` and `.` in a title into spaces (`Kirby  Triple Deluxe`, `New Super Mario Bros  2`)
  and uses the short title, so A Link Between Worlds is `The Legend of Zelda`.
- The 2DS's clock was set to 2034, so every folder is stamped `2034.02.05_...`.
- The only extdata is Dragon Quest VIII's `linkage.bin` (4 bytes) and Super Mario Maker's 221 files:
  `course000`-`course220`, 274460 bytes each except `course220` (7196), 58 MB in total.
- My Nintendo PICROSS (CTR-N-JHXA) is download-only and not in the cartridge DAT, so its folder keeps
  JKSV's name.

## Not filed

- **363 jotego stock files.** 369 of the 370 files in `Saves/jt*/common` are byte-identical to
  jotego's own defaults in `github.com/jotego/jtbin` `pocket/raw/Saves/` (321 match the tree as of
  2024-07-27, the other 48 the current one). They all share the mtime 2025-03-21 18:18, the minute an
  updater installed the jotego assets (1282 files in `Assets/` carry the same stamp). No core
  wrote them on this device. Per core: jtcps2 312 (128 B each, 40 distinct contents), jtriders 13
  (128 B), jtshouse 13 (63552 B, except wldcourt at 2048 B), jtsimson 20 (144 B), jtxmen 11 (128 B).
  One of each kind is filed under `mame/_jotego.<core>/` with `"stock_default": true`. They show
  what a card holds once jotego cores are installed: a sync tool will find hundreds of these and
  should not take them for the user's saves. `jtcps1/common/megaman.sav` (128 zero bytes,
  2024-01-04) is not in jtbin at any commit, so the core wrote it. It is filed as a normal entry.
- The 5 AppleDouble `._*.sav` files in `Saves/gbc/common` are macOS metadata, not saves. Also not
  filed: `.DS_Store` files, and JKSV's own `titles` and `nand` caches.
- The registry has no jotego CPS, Konami or Namco cores (only jtngp and jtngpc), so those entries
  sit under `mame/_jotego.<core id>/`. It also does not list Mazamars312.NeoGeo_Overdrive, which is
  under `neogeo/_Mazamars312.NeoGeo_Overdrive/`, nor agg23.NES_Analogizer (only
  RndMnkIII.NES_Analogizer is an alias of agg23-nes). Both are candidates for aliases.

## What each Pocket core writes

This is what 1Retro needs. "Shape" means `pocket::*` / `mister::*` in 1Retro's
`cloud/*/tests/corpus/src/shape.rs`, which is written from source reading. These files are what the
cores actually wrote.

| Core | Files here | What it writes | Against 1Retro's shape |
| --- | ---: | --- | --- |
| Spiritualized.GB | 7 | the header's RAM size exactly (8 or 32 KiB), raw, no footer | no shape |
| Spiritualized.GBC | 17 | the same as Spiritualized.GB, for GB and GBC games alike | no shape |
| budude2.GB (1.3.x) | 4 | the header's RAM size **plus 16 bytes on every save**, on MBC1 and MBC5 carts with no clock as well | **disagrees**: the shape adds 16 only "once the game uses an MBC3 clock" |
| Spiritualized.SuperGB | 1 | `run_cartridge.sav`, 8 KiB of 0xFF, when it boots the physical cart (`Assets/sgb/common/run_cartridge.gb`, a 4-byte stub) | no shape |
| Spiritualized.GBA | 10 | the save type's own size: 64-Kbit EEPROM is 8 KiB, SRAM is 32 KiB; no padding, no sidecar | the shape knows only mincer_ray (64 KiB, 0xFF-padded). Spiritualized.GBA cards hold 8 and 32 KiB files in the same `Saves/gba/common` |
| agg23.NES | 6 | always 262144 bytes, the PRG-RAM first. **What follows is not all zeros** (see below) | **disagrees**: the shape says "PRG-RAM first and zeros after it" |
| Spiritualized.NES | 3 + palram | 8 KiB of PRG-RAM; its palette RAM goes to `Saves/nes/Spiritualized.NES/palram.bin` (2 KiB) | agrees with the shape's guess of 8 KiB. `palram.bin` is not in it |
| agg23.SNES | 21 | the header's SRAM size (2, 8 or 32 KiB; Super Mario RPG has code 5, 32 KiB), raw; no `.mk3sav` | agrees |
| ericlewis.Genesis | 1 | 64 KiB (Sonic 1 has no save RAM: all 0xFF) | agrees on size. The packing could not be checked |
| Spiritualized.Genesis | 1 | **128 KiB, not packed**: the 8-bit save RAM on the odd bytes, 0xFF on the even ones, 0xFF past it (Sonic 3) | no shape. It differs from ericlewis/MiSTer, which pack one byte per byte into 64 KiB |
| agg23.PC Engine | 3 | 2 KiB backup RAM, `HUBM` first; a new file is just the formatted header | agrees |
| Mazamars312.PC Engine CD | 5 | 2 KiB backup RAM, `HUBM`, one file per instance JSON in the core's folder | (same rule as TurboGrafx16_MiSTer) |
| Mazamars312.NeoGeo family | 6 | memory card `<instance>.sav`, 8 KiB: a 2 KiB card, then 0xFF; `backup.bak` 64 KiB of MVS backup RAM | no shape. **Location varies**: `backup.bak` is in the core's folder for NeoGeo and Overdrive but in `Saves/ng/common` for the Analogizer build (2025), though all three `data.json` declare the slot the same way |
| jotego (jtcps1/2, jtriders, jtshouse, jtsimson, jtxmen) | 7 | the NVRAM/EEPROM image under the MAME set name: 128 B (CPS1, CPS2, riders, xmen), 144 B (simpsons, vendetta), 63552 B (shouse), 2048 B (wldcourt) | no shape. The defaults are shipped with the core (see above) |

**budude2's footer.** The 16 bytes are `u32` LE host time, then 48 bits of packed MBC3 registers
(seconds 6, minutes 6, hours 5, days 10, overflow, halt; the bits above 29 zero), then six 0xFF.
That is the layout `clocks.json` and one-saves-convert's `rtc.rs` give. The clock runs on carts that
have none:

| Save | Cart | Footer | Host time | File mtime | Clock |
| --- | --- | --- | --- | --- | --- |
| Super Mario Land 2 (Rev 2) | MBC1 | `c9ea9069 b91864000000 ffffffffffff` | 2026-02-14 21:36:09 | 2026-02-14 21:36 | 50 d 01:34:57 |
| Shantae | MBC5 | `abf26a67 4d0000000000 ffffffffffff` | 2024-12-24 17:43:07 | 2024-12-24 17:43 | 0 d 00:01:13 |
| Pokemon Trading Card Game | MBC5 | `a7226068 350200000000 ffffffffffff` | 2025-06-28 17:13:11 | 2025-06-27 18:13 | 0 d 00:08:53 |
| Wario Land II | MBC5 | `a46e6168 47392b000000 ffffffffffff` | 2025-06-29 16:49:40 | 2025-06-28 17:49 | 21 d 19:37:07 |

The source does not explain the footer on these carts. In v1.3.2, `save_handler.sv` reports size +
16 only `if (RTC_inuse)`, which `mbc3.v` and `huc3.v` drive, and `mappers.v` declares `tri0
RTC_inuse_b`. The built core evidently reports it set anyway. Note too that the host time equals the
mtime in the winter files but runs 23 hours ahead of it in the two June 2025 ones. Earlier budude2
releases differ again: 1.0.0-1.0.6 wrote a constant `0x8009`, 32777 bytes, for every cart with a
save (`core_top.sv`), and 1.0.7-1.0.8 added 9, not 16, with a clock. A card from early 2024 may hold
32777-byte budude2 files; none are here. In short, 1Retro should split a 16-byte budude2 footer
whatever the cartridge type, and should not assume a non-MBC3 save from budude2 is bare.

**agg23.NES past the PRG-RAM.** Counting non-zero bytes per 8 KiB block of the 32 in each file:
Lagrange Point is clean, and StarTropics has one stray byte. Crystalis has 1-3 stray bytes in most
blocks. Zelda (Rev 1) has about 300 per block from block 7 to the end. Dragon Warrior IV has dense
data in blocks 1, 2, 4 and 5 (7416, 7528, 5428 and 1012 bytes). Ancient Dungeon (a hack, 2022) is
non-zero through all 256 KiB. This looks like stale memory, not save data. 1Retro should take the
first 8 KiB as the save and must not expect, or require, zeros after it. Anything that hashes or
compares the whole file will see two otherwise identical saves as different.

**Smaller things.**

- Spiritualized.NES and agg23.NES saves for the same game sit side by side, from two copies of the
  ROM (`nes/common/games/...` and `nes/common/...`).
- The Neo Geo memory cards are named after the instance JSON (`Metal Slug 2.sav`), not the MAME set.
  The three here are byte-identical empty cards.
- The two `backup.bak` files of Mazamars312.NeoGeo and its Overdrive build are byte-identical,
  dated 2024-07-23 and 2020-01-02.

## clocks.json against this card

| Core in clocks.json | Says | Here |
| --- | --- | --- |
| budude2-gb | packed, reserved 16, timestamp_width 4 | **agrees on the layout** (four files). **Disagrees on when**: present on every save, not only MBC3 ones |
| budude2-gbc | the same | no budude2.GBC file on this card |
| mincer-ray-gba | sidecar `.rtc` | no file: the core postdates the backup, and no GBA game here has a clock |
| agg23-wonderswan | packed, reserved 12 | no WonderSwan saves |

clocks.json has no entry for the Spiritualized cores (GB, GBC, SuperGB, GBA), agg23.SNES or NES,
ericlewis/Spiritualized Genesis or the Mazamars312 cores. None of their files here is from a
cartridge with a clock, so the card does not settle any of them. The nearest are Pokemon Red/Blue,
MBC3 without a timer, which got no footer from either Spiritualized GB core.
