# MAME (arcade)

Four played games, not ten. The drive has only two arcade romsets: the Neo Geo set, and a 2009
CPS1 set left over from a PS Vita emulator pack. Each MAME core accepts only a romset of its own
era, so each core could run only one of the two. 17 (game, core) entries were filed, against
31 attempts. Seven more games come from downloads, including the CPS2 EEPROM, which the drive
cannot supply.

## Romsets on the drive (searched; nothing downloaded)

- **Neo Geo, modern MAME set**: `Neo Geo AES - MVS/MAME
  romset/` (170 sets). The BIOS is the FBNeo `neogeo.zip` (a superset of MAME's).
- **CPS1, 2009 TorrentZip set**: a CPS1 folder (28 sets: 1941,
  3wonders, area88, captcomm, cawing, chikij, cworld2j, daimakai, dino, dynwar, ffight and
  clones). The set includes the 279-byte PLD stubs of MAME ~0.13x. The `CPS2/` folder there is
  empty.
- `ROMs/{arcade,mame,fbneo,fba,cps1,cps2,cps3}` hold only `systeminfo.txt`. No other MAME zips
  were found (searched by set name: sf2*, ssf2*, 19xx, ddtod, tmnt*, simpsons*, robotron*,
  joust*, mk*, nbajam*, defender*, smashtv, narc, ...).
- The Pocket's `Assets/jt*` and `obsidian.*` folders hold `.rom` files, which are
  MRA-assembled images, not MAME zips: CPS1/1.5/2, Simpsons, Sunset Riders, X-Men, TMNT, Outrun,
  System 16, Robotron, Joust 2, Defender, and more. Rebuilding MAME sets from them would need the
  MRAs and per-game de-interleaving, so it was not attempted. They are the obvious source if
  someone wants EEPROM/CMOS games here (Konami EEPROM, Williams CMOS, CPS2).

Which core takes which set:

| Core | Neo Geo (modern set) | CPS1 dino (2009 set) |
| --- | --- | --- |
| mame (0.289) | runs | refused: needs PLD files `cd63b.1a`, `iob1.12d`, `bprg1.11d`, `ioc1.ic1` the set lacks |
| mame-2016 (0.174) | runs | refused (same) |
| mame-2015 (0.160) | runs | refused (same) |
| mame-2010 (0.139) | runs | refused (same; core returned -11 after "required files are missing") |
| mame-2003-plus | refused: wants `083-p1.bin`, `sfix.sfx`, `mame.sm1`, `083-m1.bin`, `mamelo.lo` | runs |
| mame-2003-0-78 | refused | runs |
| mame-2000 (0.37b5) | refused | runs |
| finalburn-neo | (filed under `neogeo/`) | runs ("No missing files") |
| fb-alpha (2012) | (filed under `neogeo/`) | runs |
| mame-2003-midway | refused: only Midway drivers, and the drive has no Midway set | refused |

## The games

| Game | Save | Script (scripts/mame/) | Proof |
| --- | --- | --- | --- |
| Cadillacs and Dinosaurs (`dino`, CPS1 + QSound) | **93C46 EEPROM, 128 bytes** | service menu → SYSTEM CONFIGURATION: 1 COIN 2 CREDITS, CONTINUE OFF → EXIT ("CONFIGURATION SAVED") → power cycle | the menu reads the values back |
| The King of Fighters '98 (`kof98`) | MVS backup RAM: soft DIPs | test switch → SETTING UP THE SOFT DIP (as in `neogeo/`) | the soft-DIP page read back |
| Jockey Grand Prix (`jockeygp`) | MVS backup RAM + 8 KiB cartridge RAM (credits) | two coins, power cycle | CREDIT 000002 |
| Blazing Star (`blazstar`) | MVS backup RAM: high-score name "AAAAAAAAA" | coin, play, enter the name | GAME OVER after the name entry |

How the service menu is reached:
- **MAME cores:** F2 on the keyboard (`key f2`). It works in mame, 2016, 2015, 2010, 2003-plus,
  2003 and 2000.
- **FinalBurn Neo:** START held for 150 frames (its "Diagnostic Input" defaults to "Hold Start").
- **FB Alpha 2012:** the same, but its default is "None", so `scripts/mame/fb-alpha.opt` sets
  `fbneo-diagnostic-input = Hold Start`. Hence `dino.finalburn-neo.txt` and `dino.fb-alpha.txt`.
- **MAME 2010** maps Neo Geo A to RetroPad **a** and "back" to x, where the other cores use b and
  y. Hence `kof98.mame-2010.txt` and `blazstar.mame-2010.txt`.

## Games x cores

| Game | mame | mame-2016 | mame-2015 | mame-2010 | mame-2003-plus | mame-2003-0-78 | mame-2000 | finalburn-neo | fb-alpha | mame-2003-midway |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dino | refused (romset) | refused | refused | refused | filed | filed | filed | filed | filed | refused |
| kof98 | filed | filed | filed | filed (variant) | refused (romset) | refused; 1 downloaded | refused | (neogeo/) | (neogeo/) | — |
| jockeygp | filed | filed (see note) | filed | filed | refused | refused | refused | (neogeo/) | (neogeo/) | — |
| blazstar | filed | filed | filed | filed (variant) | refused | refused | refused | (neogeo/) | (neogeo/) | — |

All 17 proofs were checked on one sheet. mame-2009 (no builds) and finalburn-neo-cps12-subset
(no macOS build) are not runnable; nothing attributable to either was found.

## What each core writes into its save directory

Each core makes its own subdirectory, which is filed as the tree it wrote:

| Core | Tree | Neo Geo backup RAM | Byte order | Other files |
| --- | --- | --- | --- | --- |
| mame | `mame/nvram/<game>/saveram`, `mame/cfg/{default,<game>}.cfg` | **65536** | words byte-swapped (`ABKCPUR MAO  K.!`) | Jockey GP's cart RAM as **`mame/nvram/jockeygp/cslot1_cmc50_jockeygp_nvram`** (8192, swapped). cfg is XML (`<mameconfig version="10">`) with **coin counters** (`<coins index="0" number="2" />`) |
| mame-2016 | `mame2016/nvram/<game>/saveram`, `mame2016/cfg/…` (written, not filed: it holds the run's folder paths) | 65536 | swapped | **no cart RAM file** for Jockey GP. After `retro_reset` the game came back with no credits |
| mame-2015 | `mame2015/nvram/<game>/saveram`, `mame2015/cfg/…` (written, not filed: it holds the run's folder paths) | 65536 | swapped | no cart RAM file |
| mame-2010 | `mame2010/nvram/<game>.nv`, `mame2010/cfg/…`, **`mame2010/ini/mame.ini`** | **8192**: only the first 8 KiB of the 64 KiB | swapped | no cart RAM file. The core writes a full `mame.ini` (114 lines) into the save dir |
| mame-2003-0-78 | `mame2003/nvram/<game>.nv`, `mame2003/cfg/…`, `mame2003/hi/<game>.hi` | 8192 (downloaded) | **68000 order** (`BACKUP RAM OK !`) | cfg is binary (`MAMECFG\x09`); `hi/` comes from hiscore.dat (dino: 800 bytes) |
| mame-2003-plus | `mame2003-plus/{nvram,cfg,hi}/…` | — | — | the same files as mame2003; dino.hi is identical to mame2003's |
| mame-2000 | `mame2000/nvram/<game>.nv`, `mame2000/cfg/…` | — | — | no `hi/` |
| finalburn-neo | `fbneo/dino.nv` | — | — | for Neo Geo it writes `fbneo/<game>.fs` instead (see neogeo/NOTES.md) |
| fb-alpha | `dino.nv` in the save dir root | — | — | |

**dino's EEPROM is byte-identical in all five cores** that ran it: 128 bytes, sha1 c5cab3f8…,
starting `92 11 02 00 "CAD " 00 01 …`. Only the name and the folder differ (`mame2000/nvram/`,
`mame2003/nvram/`, `mame2003-plus/nvram/`, `fbneo/`, root). FB Alpha 2012 writes a raw `.nv` for
an EEPROM game, though for Neo Geo it writes a compressed `FB1 FS1` `.fs`.

The Neo Geo backup RAM comes in three forms:
- 64 KiB with swapped words: mame, 2015, 2016, FBNeo.
- **8 KiB** with swapped words: mame-2010.
- **8 KiB in 68000 order**: mame-2003.

Geolith (64 KiB, 68000 order) and MiSTer are a fourth and fifth form; see neogeo/NOTES.md.

## Downloaded entries

All are from [zwh8800/recalbox-saves](https://github.com/zwh8800/recalbox-saves) at commit `fc24fb8`
(Recalbox saves, no licence). They are attributed by the folder the core creates (`mame2003/nvram/`,
`mame2010/nvram/`). Game state is unknown for all of them.

- `mame-2003-0-78/{mslugx,kof98,mslug}`: Neo Geo backup RAM, 8192 bytes, 68000 order, from
  Recalbox's neogeo save folder (`saves/neogeo/mame2003/nvram/`).
- `mame-2010/{19xx,1944,sfz2al}`: **CPS2 EEPROMs**, 128 bytes (19xx shows "19X" at 0x2C).
- `mame-2010/lbowling`: Neo Geo backup RAM, 8192 bytes, swapped, the same form as the played
  mame-2010 entries.

Leads under `.cache/downloads/mame/`: the same repo's MAME 2010 nvram for kof98, kof99, kof2000,
kof2002, kof2003, mslug5, magdrop3, neobombe and rbff1; MAME 2003 Neo Geo nvram for doubledr,
fatfury1, kof2000, kof97a, kof98n, mslug2, mslug3, sengokh and zedblade; and a blank 2 KiB
`memcard/MEMCARD.000` from MAME 2003 (all zero).
