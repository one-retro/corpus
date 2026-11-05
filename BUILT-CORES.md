# Cores built from source

Registry cores that the libretro buildbot does not publish for macOS, built here from their
upstream sources and run in `tools/retro-run` like any other core. Each build sits at
`.cache/cores/built/arm64/<slug>_libretro.dylib` with a `<that file>.json` holding
`{"repo", "commit", "build"}`; `tools/fetch-core.sh` prefers it, and `tools/make-save.py` copies the
JSON into each entry's provenance as `built_from`. Every core here is a native arm64 build.

Nothing was installed. The builds used what was already on the machine: Apple clang 21 (Command
Line Tools), the system make (3.81) and perl, and rustc/cargo 1.99.1 from rustup.

Only scripts that existed when this pass started were replayed. One script was added,
`scripts/mame/dino.mame-2009.txt` (see MAME 2009). 70 entries were filed.

## The cores

| Slug | Upstream (commit) | Build | Result |
| --- | --- | --- | --- |
| beetle-supafaust | github.com/libretro/supafaust (`642d1d1b`) | `make`, after a one-line patch (below) | 8/8 snes |
| chimerasnes | github.com/jamsilva/chimerasnes (`04c57c29`) | `make` | 8/8 snes |
| higan-super-famicom-balanced | github.com/libretro/nSide (`5b2b5da3`) | `make -C nSide target=libretro binary=library platform=macos compiler=clang++` | 8/8 snes (core crashes at deinit, see below) |
| bsnes-jg | github.com/libretro/bsnes-jg, branch `libretro` (`5a1ea189`) | `make -C libretro` | 8/8 snes (needs a pad in port 2) |
| bnes | github.com/libretro/bnes-libretro (`8e26e89a`) | `make platform=osx CC="cc -DIOS -DHAVE_POSIX_MEMALIGN=1" CXX="c++ -DIOS"` | 7/10 nes |
| emux-nes, emux-gb, emux-sms | github.com/libretro/emux (`3e558cb1`) | `cd libretro && make -f Makefile.osx_x86_64 MACHINE=<nes,gb,sms> CC=cc AR=ar AS=as` | builds and plays, but can never save (below) |
| boytacean | github.com/joamag/boytacean (`4d806d07`) | `cd frontends/libretro && cargo build --release` | builds and plays, but can never save (below) |
| doublecherrygb | github.com/TimOelrichs/doublecherryGB-libretro (`d432f976`) | `make` | 7/10 gb, 9/10 gbc |
| finalburn-neo-neogeo-subset | github.com/libretro/FBNeo (`384609f7`) | `make -C src/burner/libretro SUBSET=neogeo generate-files`, then the same with `-j` and no target | 10/10 neogeo |
| finalburn-neo-cps12-subset | github.com/libretro/FBNeo (`384609f7`) | the same with `SUBSET=cps12` | 1/1 mame (dino) |
| mame-2009 | github.com/libretro/mame2009-libretro (`29b38f53`) | variable overrides on the command line (below) | 4/4 mame |
| vice-x64dtv | github.com/libretro/vice-libretro (`5ebe7d33`, the commit of the buildbot's other VICE cores) | `make EMUTYPE=x64dtv CC="cc -Dfdopen=fdopen"` | builds; Elite hangs while loading, so no save |

Full commits are in each entry's `built_from`. All builds used `-j12` or `-j14`. Not rebuilt:
- **rustynes**: upstream main is still the buildbot's 3.6.0.
- **frodo** and **mame-2003-midway**: nothing in the build would change why they fail.
All three were retried; see the per-system sections.

### Build notes

- **What the subset builds are.** `finalburn-neo-*-subset` is the ordinary FBNeo libretro core built
  with `SUBSET=cps12` or `SUBSET=neogeo`. `src/burner/libretro/Makefile` then includes
  `Makefile.cps12` or `Makefile.neogeo`, which compile only the CPS-1/CPS-2 (`-DBUILD_CAPCOM`) or
  Neo Geo drivers. The library is named `fbneo_cps12` / `fbneo_neogeo`, and the core reports
  "FinalBurn Neo (cps12 subset)" / "(neogeo subset)". The repo's CI builds them only for the 3DS.
  - The build must regenerate the driver list (`generate-files`, which `REGEN_HEADERS=1` runs).
    The shipped `src/dep/generated/driverlist.h` names every driver, so without it the link fails
    with hundreds of missing `_BurnDrv*` symbols.
  - macOS make 3.81 ignores the Makefile's `.WAIT`, so `REGEN_HEADERS=1 -j` compiles while it is
    still generating (`m68ki_cycles` undeclared). Hence the separate `generate-files` step.
  - Both subsets keep FBNeo's option names (`fbneo-neogeo-mode`, `fbneo-memcard-mode`, ...) and
    its save paths, so `scripts/neogeo/fbneo-*.opt` work unchanged.
- **beetle-supafaust.** As shipped, it does not compile on macOS:
  - `mednafen/config.h` defines `HAVE_SEM_TIMEDWAIT` for every platform but the Switch, and macOS
    has no `sem_timedwait` (`MThreading_POSIX.cpp:635: use of undeclared identifier
    'sem_timedwait'`). This is why there is no macOS build.
  - The one patch adds `&& !defined(__APPLE__)` to that `#if`. The core then uses its own
    condition-variable semaphores, the path already written for platforms without `sem_timedwait`.
- **bnes** (2019) fails on arm64 macOS in two places:
  - `libco/aarch64.c` includes `<malloc.h>`.
  - nall uses `struct stat64`.
  The code's own `IOS` define covers both. `HAVE_POSIX_MEMALIGN=1` selects `posix_memalign` over
  `memalign`. No source edits.
- **emux.** The repo's macOS makefile (`libretro/Makefile.osx_x86_64`) targets an osxcross
  toolchain. Pointing CC/AR/AS at the native tools builds arm64. The output
  `emux_<m>_libretro.osx_x86_64.dylib` was renamed.
- **higan-super-famicom-balanced** is libretro's nSide fork. Its `.gitlab-ci.yml` has an osx-arm64
  job, and that command builds unmodified. The core is **v106.25** "higan (Super Famicom
  Balanced)", not the v105 nSide that the core info names.
- **bsnes-jg.** It needed no Jolly Good frontend: libretro keeps a libretro port in the `libretro`
  branch of github.com/libretro/bsnes-jg. That port is bsnes-jg 2.1.0, and it builds unmodified.
- **mame-2009** (MAME 0.135u4). No source edits, but the Makefile's `osx` section cannot build on
  arm64 with current clang. Every fix is a command-line variable:
  - It compiles MAME's C sources with `CC = c++`, and clang refuses `-std=gnu89` for C++. Fix:
    `CC="cc ..."`, `NATIVECC=cc`.
  - `PTR64` is set only when `uname -m` is x86_64. Fix: `PTR64=1`.
  - It would pick the x86-64 DRC back end. Fix: `FORCE_DRC_C_BACKEND=1`.
  - `osd_stat` uses `struct stat64`. Fix: `-DSDLMAME_NO64BITIO`, as the iOS target sets.
  - `osd_yield_processor` is defined only for x86/PPC. Fix: `ARM_ENABLED=1`, as iOS.
  - It sets no `ARFLAGS`. Fix: `ARFLAGS=-crs`.
  - macOS `ar` refuses the empty `libsoftfloat.a`. Fix: `AR=` a two-line shell wrapper that
    writes an empty archive, as GNU ar does.
  - Modern C errors are downgraded: `-Wno-error=implicit-function-declaration`, `int-conversion`,
    `incompatible-function-pointer-types`, `incompatible-pointer-types`.
  - The repo holds both `Makefile` (libretro) and `makefile` (MAME's), and on a case-insensitive
    disk only one is checked out. So `git show HEAD:Makefile > libretro-Makefile.mk` and
    `make -f libretro-Makefile.mk`.
  - The exact command is in each entry's `built_from`.
  - A clean rebuild with that command gives the same 39.8 MB library.
- **vice-x64dtv.** The bundled zlib (`deps/libz/zutil.h`) defines `fdopen(fd,mode)` as `NULL`
  whenever `TARGET_OS_MAC` is set, which breaks the current SDK's `<stdio.h>`. `-Dfdopen=fdopen`
  skips that block.
  - x64dtv also needs `dtvrom.bin` (the DTV flash ROM), which VICE ships in
    `vice/data/C64DTV/`. It was copied from the source tree into a BIOS directory passed with
    `--bios`, so the core finds it as `system/vice/C64DTV/dtvrom.bin`.
  - Without it the screen stays black ("Reading C64DTV ROM rev:2 image: 'dtvrom.bin' failed").

### Runtime notes

- **bsnes-jg crashes on frame 1 under plain retro-run** (SIGSEGV in `SuperFamicom::CPU::joypadEdge`).
  - retro-run calls `retro_set_controller_port_device` for port 1 only. bsnes-jg leaves port 2's
    controller null, then reads it.
  - RetroArch sets every port, so this is the harness, not the core.
  - Workaround (no tools/ edit): `.cache/build/make-save-pad2.py` is `tools/make-save.py`
    unchanged except that retro-run gets `--pad2`. Each entry's provenance note says so.
  - **retro-run should plug a joypad into every port the core declares, as RetroArch does.**
- **higan-super-famicom-balanced exits with SIGTRAP** (rc 133) in `retro_deinit`
  (`Program::~Program`).
  - This happens after the run, the save write and `retro_unload_game`, so every file is complete.
  - make-save.py counts the exit as a failure. The eight entries were filed from the run
    directories by `.cache/build/file_aborted.py`, which applies make-save's rules plus a
    provenance note.
- **emux and boytacean have no way to save under libretro:**
  - emux's `retro_get_memory_*` answer only `RETRO_MEMORY_SYSTEM_RAM`. It writes nothing into the
    save directory.
  - boytacean's `retro_get_memory_size` returns 0 and `retro_get_memory_data` NULL for every id.
  - Both play the games: emux-nes registers LINK in Zelda and saves SIMEA in Crystalis on
    screen; boytacean shows "RED saved the game" and "GOLD saved the game". The save is lost at
    unload, and nothing is written.
  - Every run ended with an empty save directory, so nothing was filed.
- **emux needs firmware.**
  - emux-gb refuses to start without `dmg_boot.bin` ("Could not map boot ROM!").
  - emux-sms wants `bios.sms`.
  - Both were passed with `--bios` from copies kept outside `.cache/bios/<system>/`, so other
    workers' runs are not affected. The copies come from the owner's ROM library and match the
    core info's MD5s (`32fbbd84…`, `840481177…`). SameBoy, for one, would pick up a
    `dmg_boot.bin` in its system directory.

## By system

### snes (8 scripts)

| Game | beetle-supafaust | chimerasnes | higan-…-balanced | bsnes-jg |
| --- | --- | --- | --- | --- |
| Chrono Trigger | ✔ | ✔ | ✔ | ✔ |
| Daikaijuu Monogatari II (S-RTC) | ✔ clock stuck at 0:00:00, no clock file | ✔ `.rtc` 20, clock stuck at 0:00:00 | ✔ clock ticks (0:02:29), no clock file | ✔ `.rtc` 16 |
| Dezaemon (128 KB) | ✔ | ✔ | ✔ | ✔ |
| Kirby Super Star (SA-1) | ✔ | ✔ (time 01:00:99) | ✔ | ✔ |
| ALttP | ✔ | ✔ | ✔ | ✔ |
| Pebble Beach (SA-1 64 KB) | ✔ | ✔ | ✔ | ✔ |
| SimCity | ✔ | ✔ | ✔ | ✔ |
| Super Tetris 3 | ✔ | ✔ | ✔ | ✔ |

All 32 proofs were checked. Dezaemon passes its S-RAM check in all four cores: "コピーしました",
and the file is the common sha1 `fe972f66…`. That includes nSide balanced, though the higan
accuracy core (x86_64) fails it.

### nes (10 scripts)

| Game | bnes | emux-nes |
| --- | --- | --- |
| Zelda, Dragon Warrior, Zelda II, Destiny of an Emperor, EarthBound Beginnings, Crystalis, Final Fantasy | ✔ | plays, nothing written |
| StarTropics (MMC6) | ✘ name registered, but SELECT then shows empty slots; the 8192-byte `.srm` is all zero | plays, nothing written |
| Family Circuit '91 (Namco 175) | ✘ no frame is ever drawn, save RAM 0 (mapper 210 unsupported) | ✘ refused ("Failed to initialize machine!") |
| Dragon Ball Z II (Bandai 24C02) | ✘ game shows "セーブしています", but the core reports save RAM 0 and writes nothing | ✘ refused (mapper 16) |

### gb (10 scripts) and gbc (10 scripts)

| Game | doublecherrygb | boytacean | emux-gb |
| --- | --- | --- | --- |
| gb: Link's Awakening, Pokemon Red, Pokemon Yellow, Final Fantasy Adventure (MBC2), Super Mario Land 2, Nyan to Wonderful (MBC3+clock), Pocket Monsters Midori | ✔ (7) | plays, nothing written | LA and SML2 play, nothing written; Midori segfaults at load; the rest refused (MBC2, MBC3, MBC5) |
| gb: Pocket Camera | ✘ white screen; its 131072-byte file is not a save (moved out) | ✘ panics: "No MBC controller available for POCKET CAMERA" | ✘ refused (cart type 252) |
| gb: Pocket Family GB (HuC-3) | ✘ white screen, RAM all zero | ✘ panics (HuC3) | ✘ refused (254) |
| gb: Robot Ponkots Sun (HuC-1) | ✘ striped garbage on screen; file has 0xB9 blocks (moved out) | ✘ panics (HuC1) | ✘ refused (255) |
| gbc: Tetris DX, Oracle of Seasons, Pokemon Gold, Pokemon Crystal, Pokemon Pinball, Game Boy Wars 3, Harvest Moon GBC, LADX, Kirby Tilt 'n' Tumble (MBC7) | ✔ (9) | plays, nothing written (Kirby panics: "MBC6 + SENSOR + RUMBLE", boytacean's name for MBC7) | Tetris DX plays, nothing written; the rest refused (MBC3/5/7, HuC-3) |
| gbc: Robopon Sun (HuC-3) | ✘ "Save Err:" in game, as in TGB Dual (moved out) | ✘ panics (HuC3) | ✘ refused |

DoubleCherryGB, a TGB Dual fork, fails exactly where TGB Dual fails (the HuC-1/HuC-3 games and the
Pocket Camera), except that its Kirby EEPROM does hold the calibration (below). Its colours are
paler than TGB Dual's in the GBC proofs.

higan-super-famicom-balanced's gb/gbc pairs were not run: they need the Super Game Boy ROM.

### mastersystem (8 scripts)

emux-sms: all eight games load with `bios.sms`, nothing is ever written. Ys is garbled.

### neogeo (10 scripts) and mame (4 scripts)

| Game | finalburn-neo-neogeo-subset | finalburn-neo-cps12-subset | mame-2009 |
| --- | --- | --- | --- |
| neogeo: all ten, with the same `fbneo-*.opt` as finalburn-neo | ✔ (10) | – | – |
| mame: dino (CPS1 EEPROM) | – | ✔ (`dino.finalburn-neo.txt`) | ✔ (`dino.mame-2009.txt`) |
| mame: kof98 | – | not in the subset: runs 1813 frames with no video, writes nothing | ✔ |
| mame: jockeygp, blazstar | – | – | ✔ ✔ |

**MAME 2009 is the only MAME core here that runs both romsets on the drive.** It runs the 2009
CPS1 set (with its PLD stubs) and the modern Neo Geo sets. Its pad mapping:
- **CPS1 button 1 is RetroPad a.** `press b` does nothing there, so the dino script got a variant.
- **Neo Geo A is RetroPad b**, so the shared kof98, jockeygp and blazstar scripts run unchanged.
  The `.mame-2010` variants (a/x) do nothing in it.
- **kof98:** the BIOS's cabinet menu reads COIN1, COIN2, …, so the script's cabinet change set
  COIN2 rather than CONTINUE. K.O.F.'98's own soft DIPs are as intended. Both quirks are in the
  provenance notes.

### Retried buildbot cores

- **rustynes / fds** (buildbot 3.6.0, now with retro-run's native disk control): all seven fail
  as before.
  - Five games show "DISK TROUBLE ERR.24": F1 Race, 3D Hot Rally, Golf Japan and US, and Metroid.
  - Link no Bouken sits on "WAIT" for 9,000 frames after the name is entered.
  - Zelda no Densetsu's SELECT screen comes back empty.
  - `RustyNES/<sha256>.fds.sav` is byte-identical to the ROM every time. Not filed.
- **frodo / c64:** not rerun. The reasons in `c64/NOTES.md` still hold:
  - It cannot load `.g64`/`.nib`.
  - From a `.d64` decoded from the NIB, Summer Games fails to load its event in VICE as well.
  - Elite needs a second disk, and Frodo has no disk control.
- **vice-x64dtv / c64:** Elite reaches "LOADING ELITE." and stays there, with the fast loader
  and with the slow one. A stock DTV has no disk drive (the IEC port is a hobbyist add-on), so
  disk saves do not really make sense on it.
  - The empty save disk that the hotkey creates is not a save. Not filed.
- **mame-2003-midway:** still no Midway romset on the drive. A search for mk, mk2, mk3, umk3,
  nbajam(te), smashtv, narc, trog, totcarn, wwfmania, openice, nbahangt, rampage, spyhunt, tapper,
  joust, robotron, defender, sinistar, gauntlet, strkforc, hiimpact and term2 found nothing.

## How the built cores' files differ from the corpus's

**SNES**
- **Names.** All four write `<stem>.srm`, at the header's size, like every other SNES core.
- **Fill of untouched SRAM.** Supafaust and ChimeraSNES use `0x00`, like snes9x-2002/2005. nSide
  balanced and bsnes-jg use `0xFF`, like bsnes and higan.
- **Identical files.**
  - Supafaust and ChimeraSNES are byte-identical to snes9x-2002/2005 for ALttP, Pebble Beach and
    SimCity. Chrono Trigger is 2 bytes off.
  - nSide balanced and bsnes-jg are byte-identical to bsnes and higan for Chrono Trigger, ALttP,
    Pebble Beach and SimCity.
  - nSide balanced's Kirby Super Star file equals higan accuracy's.
  - bsnes-jg's Kirby file differs from bsnes's in 30 bytes, which is SA-1 work RAM.
- **S-RTC (Daikaijuu Monogatari II)**, four behaviours:
  - **bsnes-jg** writes bsnes's 16-byte `.rtc`: 8 BCD register bytes (`30 02 00 02 68 99 05 00`,
    i.e. 00:02:30), then a u64 LE Unix time.
  - **ChimeraSNES** writes snes9x's 20-byte layout: 16 one-digit registers, `00` padding, then a
    u32 LE time. Its registers read 00:00:00: the clock never ticks, and the game's save screen
    shows 0:00:00. snes9x-2005, the code it was forked from, has no S-RTC at all.
  - **nSide balanced** ticks (0:02:29 on screen) but exposes no RTC memory and writes no
    `.rtc.ram`, unlike the higan accuracy core, which does. The time is lost.
  - **Supafaust** neither ticks nor saves, like Mesen2.

**NES (bnes)**
- `<stem>.srm`, 8192 bytes for every board it supports, fill `0x00`.
- Zelda, Dragon Warrior, Zelda II, Destiny and EarthBound are byte-identical to fceumm and Mesen.
  Crystalis differs from Mesen in 31 bytes, Final Fantasy in 1, which is timing.
- No MMC6, Namco 175 or Bandai EEPROM support.

**GB/GBC (DoubleCherryGB vs its parent TGB Dual)**
- **Fill.** Battery RAM starts at `0x00`, not TGB Dual's `0xFF`. So Pokemon Red and Yellow differ
  from TGB Dual in 27,612 bytes of filler, and Crystal in 7,860.
- **Clock file.** A `<stem>.rtc` of **8 zero bytes** for every game, clock games included (Nyan,
  Gold, Crystal, Harvest Moon). TGB Dual writes a 4-byte seconds counter.
- **MBC2 (FFA).** 8192 bytes: the 512 cells as `0x0N`, then **`0x00`** to 8 KiB. TGB Dual pads
  with `0xFF`.
- **MBC7 EEPROM (Kirby).** An 8192-byte `.srm` with `TAMA 1d00 1d00`, then zeros. Those are the
  calibration words, little-endian per word. TGB Dual stores `TAMA 0000 0000` then `00ff…`, with
  no calibration. SameBoy stores 256 bytes with each word byte-swapped (`ATAM 001d 001d`).
- **Identical files.** Games that format their RAM give TGB Dual's file: Nyan to Wonderful and
  Game Boy Wars 3 (131072). Tetris DX is identical in DoubleCherryGB, TGB Dual and SameBoy.

**Neo Geo / arcade**
- **FBNeo subsets.** The same names and sizes as finalburn-neo: `fbneo/<short>.fs`, 65536 with
  swapped words (73728 for Jockey GP), and `fbneo/<short>.memcard`.
  - Every memory card is byte-identical to finalburn-neo's.
  - The backup RAMs differ in 4 to 7 bytes. They are the same offsets each time (`0x20-0x23`,
    `0x5a-0x5d`, `0xa1a2`, `0xa1ce`): the MVS calendar and bookkeeping of a run on another day,
    from a newer build (`GIT384609f` vs `da14132`).
  - The cps12 subset's `fbneo/dino.nv` is the common 128-byte EEPROM (`c5cab3f8…`).
- **MAME 2009** writes a tree like MAME 2010's:
  - `mame2009/nvram/<game>.nv` holds 8192 bytes of Neo Geo backup RAM with swapped words (only
    the first 8 KiB, and no Jockey GP cartridge-RAM file). It is 4 to 8 bytes off MAME 2010's.
    dino.nv is the common `c5cab3f8…`.
  - `mame2009/cfg/{default,<game>}.cfg` are short XML files (`<mameconfig version="10">`), with
    the same sha1 as MAME 2010's. There are no coin counters and no paths, so they were filed.
  - Unlike MAME 2010, it writes no `ini/mame.ini`.

## Leftovers (not committed)

- Sources and objects: `.cache/build/<slug>/`, including the unbuilt `rustynes/` and `frodo/`
  clones.
- The helper scripts are in `.cache/build/`: `install.py`, `runjobs.py` (4 jobs at a time),
  `mkjobs.py`, `compare.py`, `file_aborted.py` and `make-save-pad2.py`.
- The three rejected DoubleCherryGB entries (Pocket Camera, Robot Ponkots, Robopon) are under
  `.cache/build/rejected/`.

## PICO-8: fake-08 and picante8

Built in a later pass, for `pico-8/` (not a registry system yet; see `pico-8/NOTES.md`). Neither
core has a macOS build on the buildbot. Both build unmodified with the system clang and make,
in seconds, as native arm64. The sources are under `work/pico-8/src/`.

| Slug | Upstream (commit) | Build | Result |
| --- | --- | --- | --- |
| fake-08 | github.com/jtothebell/fake-08 (`814991a2`, submodule `libs/z8lua` at `e6928578`) | `git submodule update --init`, then `make -C platform/libretro` | 6/8 pico-8 (Lua errors in two carts) |
| picante8 | github.com/MustardOS/picante8, muOS's Retro8 fork (`080de0f6`) | `make` | 8/8 pico-8 |

- **Names.** fake-08's makefile names its library `fake08_libretro.dylib`. It was installed as
  `fake-08_libretro.dylib` to match the slug.
- **Versions.**
  - fake-08 reports itself as "fake-08" `0.0.2.20a`, a version hard-coded in `libretro.cpp`.
  - picante8 reports "Picante8" `1.0.0 080de0f`.
- **retro8** comes from the buildbot (`tools/fetch-core.sh retro8`, "0.1b ddc06a1") and was not
  rebuilt.
