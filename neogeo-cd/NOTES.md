# Neo Geo CD

Nothing was filed. The library has no Neo Geo CD games, and no save written by the MiSTer core
or by NeoCD turned up online.

## What was looked for

- The Neo Geo CD folders hold only `systeminfo.txt`.
- I searched the whole drive (except 1Retro and the save and backup folders) for `.cue`, `.chd`,
  `.ccd` and `.iso` files and for names containing "neo geo cd" / "neogeocd". Every image found
  belongs to another system. Samurai Shodown, Metal Slug, KOF and Garou titles turned up only in
  PS2, Dreamcast, Saturn and SNES sets.
- The BIOS is present ( `front-sp1.bin`, `top-sp1.bin`,
  `neocd_f.rom`, `neocd_z.rom`, `000-lo.lo`, `uni-bioscd.rom`, ...), so NeoCD could run as soon as
  a disc image is added. No disc image was downloaded.

## Cores

| Core | Status |
| --- | --- |
| neocd | runnable (fetched, `neocd_libretro.dylib`), but no game to run |
| neogeo-mister | not runnable here; nothing found online (see below) |

Geolith 0.5.0 also runs Neo Geo CD (`.cue`/`.chd`, `geolith_cd_system_type`, BIOS `neocd.zip` /
`neocdz.zip`), but the registry does not list it for neogeo-cd. Its source writes the CD backup
RAM as `<stem>.brm` (8 KiB).

## What the cores write (from source; unverified here)

- **NeoCD** exposes the 8 KiB backup RAM as RETRO_MEMORY_SAVE_RAM, so RetroArch writes
  `<content stem>.srm` (8192 bytes). The core also manages a file of its own (`src/path.cpp`
  `make_srm_path`):
  - by default, `neocd.srm` under the **system** directory (one card for every game);
  - with `neocd_per_content_saves = On`, `<content filename>.srm` in the save directory.

  one-saves' two reference files (`data/saves/retroarch/neocd/*.srm`, Metal Slug and Garou
  Densetsu 2) are 8192 bytes. They hold an 8 KiB card in 68000 byte order: size word 0x4000 at
  0x0A, `NEO-GEO` signature, the first save at block 13.
- **neogeo-mister** (from `neogeo.sv` / `rtl/mem/memcard.v`, read by a helper):
  - CD games get the same 73728-byte `.sav` as cartridges: 64 KiB of (unused) backup RAM, then
    the 8 KiB card region with every 16-bit word byte-swapped. The code comment reads "64KB + 8KB
    regardless the selected system".
  - In CD mode the whole 8 KiB is the console's backup RAM. Since July 2023 there is one save
    per CD ("I've pushed commit into Main repository to make save per CD", issue #192).

## Searches with no result

- MiSTer-devel/NeoGeo_MiSTer: all 262 issues and 993 comments. The attachments are core builds
  and audio test zips only.
- libretro/neocd_libretro: no `.srm` attachments.
- misterfpga.org is closed to guests. Reddit blocks both the search tool and curl. Web searches
  turned up no attached Neo Geo CD saves.
