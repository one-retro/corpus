# Standalone emulators and emulator apps

Saves written by standalone emulators (registry `kind: standalone`, filed as
`<system>/<core>/<game>/`) and by cores inside apps that are not RetroArch-style (filed as
`<system>/<core>@<app>/<game>/`), plus a check of how faithfully `tools/retro-run` writes saves
compared with the real RetroArch.app. Made on 2026-11-03/04 on the owner's Mac, by the one worker
allowed to open GUI apps. Work files, tools and logs: `work/standalone/`.

## How input was driven (and what macOS allowed)

Synthetic keyboard input to app windows is **not available** here: the process tree running this
work (`claude` under the terminal) is not trusted for Accessibility (`AXIsProcessTrusted() = false`,
`CGPreflightPostEventAccess() = false`). A test posting key events to FCEUX with
`CGEventPostToPid` reached nothing (FCEUX's Lua saw no buttons). Screen capture of other apps'
windows is also off (`screencapture` returns black). Nothing in System Settings was changed. To
allow window-level input later, the owner would add the terminal app (the process that runs
`claude`) under System Settings > Privacy & Security > **Accessibility** (and **Screen Recording**
for screenshots of app windows).

So every save here came from input the emulator accepts from inside its own process:

| Route | Used for | Tool |
| --- | --- | --- |
| The emulator's own scripting | FCEUX Lua (`--loadlua`, `joypad.set`, `emu.exit`) | `work/standalone/tools/gen_fceux_lua.py` |
| A TAS movie the emulator plays | Dolphin `.dtm` (`-m`) | `work/standalone/tools/gen_dtm.py` |
| The emulator's debugger socket | PPSSPP WebSocket (`RemoteDebuggerOnStartup`) | `work/standalone/tools/ppsspp_ws.py` |
| A plugin the emulator loads | Mupen64Plus input plugin API | `work/standalone/tools/m64feed.c` |
| SDL events synthesized in-process | Mednafen (Homebrew, ad-hoc signed, so `DYLD_INSERT_LIBRARIES` works) | `work/standalone/tools/sdlfeed.c`, `gen_sdlfeed.py` |
| State handoff | mGBA.app 0.10.5 (no `--script` in 0.10; hardened runtime) | `work/standalone/mgba/handoff.py` |
| An FM2 movie played from Lua | FCEUX for FDS (movies have disk-side commands, Lua has none) | `work/standalone/tools/gen_fceux_fds.py` |
| Memory pokes from an injected x86_64 dylib | CrabEmu 0.2.0 Cocoa app under Rosetta (unsigned, so `DYLD_INSERT_LIBRARIES` works) | `work/standalone/crabemu/crabfeed.c`, `gen_crabfeed.py` |

All of them replay the same `scripts/<system>/*.txt` the libretro entries use (via
`work/standalone/tools/timeline.py`, which expands a retro-run script exactly as `retro-run.c`
does), except GameCube and PSP, which have no libretro scripts (their plans are in
`scripts/gc/*.dtm.txt` and `scripts/psp/*.ws.txt`), and one Mednafen variant for Spyro
(`work/standalone/mednafen/spyro-variant.txt`).

`method` in provenance: `played` (input replayed inside the app/emulator), `handoff` (see mGBA),
never `downloaded`. Every app ran with an isolated data directory; see "Safety" at the end.

## FCEUX 2.6.6 (`nes/fceux/`, standalone)

- Homebrew `fceux` (Qt). Isolation: `FCEUX_HOME=<dir>`; FCEUX then uses `<dir>/.fceux/`.
- Input: the retro-run script becomes a Lua table; each frame `joypad.set(1, …)` then
  `emu.frameadvance()`; `shot` -> `gui.savescreenshotas`; `reset` -> `emu.softreset`; the end
  calls `emu.exit()`, which makes FCEUX close the game and write battery RAM. FCEUX then
  segfaults (rc 139) on every run, after the file is written.
- **Where / name:** `.fceux/sav/<ROM file name without extension>.sav` in the home folder, raw battery RAM, written
  when the game is closed.
- Filed (played): Zelda, Dragon Warrior, Zelda II, Destiny of an Emperor, Crystalis, EarthBound
  Beginnings, StarTropics, Dragon Ball Z II. (Final Fantasy already had a downloaded FCE Ultra
  entry, left alone.)
- Findings: Zelda, DW, Zelda II, DoE and EBB are byte-identical to fceumm/mesen/nestopia.
  StarTropics (MMC6): **8192 bytes**, like fceumm (mesen/nestopia write the real 1 KiB).
  **Dragon Ball Z II (24C02 EEPROM): a 0-byte `.sav`** although the game showed its save
  message; fceumm/mesen write 256 bytes. Family Circuit '91 (Namco 175): **no file at all**, as in
  fceumm.

### FCEUX and FDS (`fds/fceux/`, added 2026-11-04)

- **Input.** FCEUX's Lua has no disk-side call, so `gen_fceux_fds.py` writes the retro-run script
  as an **FM2 movie**. Each frame line carries pad 1 and a command field:
  - `reset` becomes command 1 (soft reset);
  - `flip` becomes command 4 (eject), then 8 (select side) 30 frames later, then 4 (insert) 30
    frames after that. FCEUX will not select a side while a disk is in.

  A Lua driver starts the movie read-only (`movie.play`) at turbo speed, takes the screenshots, and
  calls `emu.exit()`. The movie's `romChecksum` is the base64 MD5 of the `.fds` file.
- **Setup.** `disksys.rom` goes in the FCEUX base folder (`$FCEUX_HOME/.fceux/`). FCEUX
  auto-inserts side A at power-on. The ROM was copied into each work folder.
- **Where / name.** `.fceux/sav/<ROM file name without extension>.fds` in the home folder.
  - It holds the **whole disk, raw 65500-byte sides, 131000 bytes, with no fwNES header** (also
    from a headered ROM).
  - It is written when the game closes, **only if the disk was written**: booting to a title
    leaves no file.
  - On the next load it is read instead of the ROM.
- **Results.** Filed all seven FDS scripts. All seven files are byte-identical to fceumm's `.srm`.
  Details are in `fds/NOTES.md`.

## mGBA.app 0.10.5 (`gba|gb|gbc/mgba@mgba/`)

- mGBA 0.10.5 has scripting, but no command-line way to load a script (`--script` arrived later),
  and its hardened runtime forbids injection. Route used, `method: handoff`: the retro-run script
  runs in the libretro mGBA core (0.11-212) up to the press that starts the game's save; a save
  state and the battery RAM are taken 2 frames later; the app starts with that state (`-t`),
  the dump beside the ROM as its `.sav`, and **no input**. The game's own save routine then runs
  inside the app and the app writes the file. GBA states had to have their version word lowered
  (0x0100000B -> 0x01000007, the newest 0.10.5 accepts); they loaded with only a BIOS-checksum
  warning. GB states (0x00400003) loaded unmodified.
- Isolation: `XDG_CONFIG_HOME=<dir>`; the ROM was copied into the work dir so the app's default
  (save beside the ROM) could be used. Quit with SIGTERM (the `.sav` is a mapped file, written as
  the game writes).
- **Where / name:** beside the ROM, `<ROM file name without extension>.sav`.
  **The clock is appended to the `.sav`, never a sidecar:**
  GBA: 16 bytes, 7 BCD bytes `YY MM DD WD hh mm ss`, a control byte (0x40 = 24 h), a u64
  `lastLatch` (Emerald: `26 11 04 03 00 08 26 40 00…` = 2026-11-04 Wed 00:08:26);
  GB MBC3: 48 bytes, the same layout libretro mGBA writes as a separate `.rtc`.
  libretro mGBA writes **no** clock at all for GBA, and a `.rtc` sidecar for GB.
- Filed: Emerald (131088 = 128 KiB + 16), FireRed (131072), Minish Cap (8192 EEPROM), Boktai
  (8208 = 8 KiB EEPROM + 16), Pokemon Crystal (32816 = 32 KiB + 48), Pokemon Red (32768).
  `proof.png` is the libretro core booting with the app's file (the game lists the save); Crystal
  shows `TIME ???` without the clock footer and `0:00` with it.
- Not possible: Link's Awakening DX writes SRAM on the very frame START is pressed, so there is no
  frame to hand off between input and write.

## Dolphin 2606a (`gc/dolphin-emu@dolphin/`)

- Isolation: `-u <dir>` (user folder), batch mode `-b`, `-e <game> -m <movie.dtm>`, stopped with
  SIGINT (graceful: "A signal was received"). Config written beforehand: analytics asked/off,
  auto-update off, `UsePanicHandlers = False` (no modal dialogs), no audio, frame dump to PNG
  (pruned to every 60th frame) for screenshots.
- `.dtm` by hand: 256-byte header + 8 bytes per pad poll. Two traps found: **`tickCount` must be
  set** (zero ends playback at the first poll, `CheckInputEnd`), and with `bSaveConfig = 0` Dolphin
  calls `GetSettings()`, which marks the movie as starting from a **clear save when the GCI folder
  is empty, and then writes to `GC/USA/Movie/Card A/`** instead of the normal folder. A
  `placeholder.txt` in the empty `Card A` folder avoids that (non-`.gci` files are ignored by the
  card but count as "has saves").
- **Where / name:** Dolphin's default slot A is now a **GCI folder** (EXI device type 8), not a raw
  card: `<user>/GC/<region>/Card A/<maker>-<game code>-<card file name>.gci` (64-byte header =
  the directory entry, then 8 KiB blocks). Also `<user>/GC/SRAM.raw` (68 bytes, IPL SRAM, written
  on stop; filed alongside, it is not a game save). The `.gci` time field comes from the movie's
  `recordingStartTime`.
- Filed (played): Mario Kart: Double Dash!! (`01-GM4E-MarioKart Double Dash!!.gci`, 24640 bytes,
  "Would you like to create data…? YES"), Kirby Air Ride (`01-GKYE-KA030621_0100_T030529_2154.gci`,
  32832 bytes, created by itself at boot: the file name carries no title). F-Zero GX: no save in
  100 s of START/A mashing; not filed.

## PPSSPP 1.20.4 (`psp/ppsspp@ppsspp/`)

- Installed with `brew install --cask ppsspp-emulator` (PPSSPPSDL.app, 89 MB). Isolation:
  `HOME=<dir>` (the macOS SDL build keeps its memstick in `.config/ppsspp` under `HOME`). Debugger
  WebSocket on a fixed port (`RemoteDebuggerOnStartup = True`, `RemoteISOPort = 45678`); stdlib
  WebSocket client. Quit with SIGTERM (clean: "Leaving main").
- **Where / name:** `<memstick>/PSP/SAVEDATA/<GAMEID><save name>/` with `PARAM.SFO`, `DATA.BIN`
  (game-encrypted), `ICON0.PNG`, `PIC1.PNG`, written as the game saves.
- Filed: Lumines (USA) `ULUS10002LUMINES` (system save the game writes by itself at boot).
  No proof.png: `gpu.buffer.screenshot` fails on Vulkan ("Could not download output") and the
  OpenGL backend stalls when the window is not visible. PPSSPP attempted outbound HTTP at start
  (Cloudflare addresses; failed).

## Mupen64Plus 2.6.0 (`n64/mupen64plus/`, standalone)

- Installed with `brew install mupen64plus` (4 MB; it also upgraded the shared `sdl2-compat`
  bottle to 2.32.74). `mupen64plus-ui-console` with `--configdir`, `--set Core[SaveSRAMPath]=…`,
  glide64mk2 video, rsp-hle, dummy audio, `--nospeedlimit`.
- Input: `m64feed`, a real Mupen64Plus input plugin that replays the retro-run script by VI frame
  (the core's frame callback), RetroPad mapped as Mupen64Plus-Next does (b=A, y=B, l2=Z), controller
  1 with a Controller Pak, `M64CMD_STOP` at the end.
- **Where / name:** `Core[SaveSRAMPath]` (default `Library/Application Support/Mupen64Plus/save/` in the home folder),
  name = **first 32 characters of the mupen64plus.ini good name + `-` + first 8 hex digits of the
  ROM MD5**, e.g. `Super Smash Bros. (U) [!]-F7C52568.sra`,
  `Legend of Zelda, The - Ocarina o-57A9719A.sra`, `Tony Hawk's Pro Skater (U) (V1.1-AFF424A1.mpk`.
  Extensions `.eep` (512 or 2048), `.sra` (32768), `.fla` (131072), `.mpk` (131072 = 4 x 32 KiB
  Controller Paks, written whenever a game touches the pak: Perfect Dark and Banjo-Kazooie write
  one at boot).
- Filed (played): Super Smash Bros., Ocarina of Time, Majora's Mask, Paper Mario, Perfect Dark,
  Tony Hawk's Pro Skater, Banjo-Kazooie, Pokemon Stadium; partial: Super Mario 64 and Yoshi's Story
  (the games formatted their EEPROM at boot, but the stick-driven menu change did not happen: the
  replayed analog stick, scaled to ±80, did not move their cursors far enough).

## Mednafen 1.32.1 (`<system>/mednafen/`, standalone)

- Homebrew `mednafen` (ad-hoc signed, no hardened runtime). Isolation: `MEDNAFEN_HOME=<dir>`
  (firmware linked in from `.cache/bios`). `-sound 0 -video.glvsync 0`: with GL vsync on and the
  window not visible, SDL3's Cocoa swap waits on the display link and the emulator crawls.
- Input: `sdlfeed.dylib`, loaded with `DYLD_INSERT_LIBRARIES`, interposes `SDL_PollEvent` and
  `SDL_GL_SwapWindow` and synthesizes `SDL_KEYDOWN/UP` events (in-process, no window server) on
  presented frames, from the retro-run script mapped to Mednafen's default keyboard map and to the
  native button each Beetle core maps the RetroPad button to (`gen_sdlfeed.py`). `shot` taps F9
  (snapshot), `reset` F10, and the run ends with F12 (exit: Mednafen writes saves on exit).
  The launcher must not pass through a SIP-protected binary (`perl`, `timeout` wrappers strip
  `DYLD_*`). `flip` (FDS) taps F8, F6, F8 (eject, select disk side, insert), 30 frames apart.
- **Where / name:** `.mednafen/sav/<ROM file name without extension>.<MD5>.<ext>` in the home folder
  (`filesys.fname_sav = %f.%M%x`; the MD5 is Mednafen's game hash, e.g. of the NES ROM without its
  iNES header). `.sav` for battery RAM, **`.srm` for the `snes` module**, PSX cards
  `<name>.<MD5>.0.mcr` and `.1.mcr` (**both slots get a card**, formatted by Mednafen at load),
  written on exit.

| System | Game | File (size) | Against the libretro entries |
| --- | --- | --- | --- |
| nes | Legend of Zelda | `.sav` 8192 | byte-identical to fceumm/mesen/nestopia/FCEUX |
| nes | StarTropics (MMC6) | `.sav` 8192 | 8 KiB like fceumm/FCEUX (mesen/nestopia: 1 KiB) |
| nes | Dragon Ball Z II (24C02) | `.sav` 256 | same size as fceumm/mesen; FCEUX writes 0 bytes |
| gb | Pokemon Red (MBC3, no clock) | `.sav` **32816** | 32 KiB + a 48-byte clock footer even though the cart has no clock |
| gbc | Pokemon Crystal (MBC3 + clock) | `.sav` 32816 | 32 KiB + 48-byte footer (VBA layout); libretro cores use a `.rtc` sidecar |
| gba | Pokemon Emerald | `.sav` 131072 | **needs a hand-made `<name>.<md5>.type` (`flash 128`, `rtc`)**; without it 64 KiB flash and the game hangs at the save. No clock in the file |
| snes | A Link to the Past | **`.srm`** 8192 | module `snes` (bsnes-based) names it `.srm` |
| pcengine | Neutopia | `.sav` 2048 | byte-identical to beetle-pce-fast's `.srm` |
| genesis | Phantasy Star IV | `.sav` 16384 | byte-identical to genesis-plus-gx (odd bytes, 0xFF-padded) |
| mastersystem | Phantasy Star | `.sav` 32768 | byte-identical to picodrive and sms-plus-gx |
| sega-gg | Shining Force Gaiden | `.sav` 32768 | same size as gearsystem/sms-plus-gx (genesis-plus-gx 16384) |
| psx | Spyro the Dragon | `.0.mcr` + `.1.mcr`, 131072 each | card 1 differs from beetle-psx's `.srm` in 2 bytes; Mednafen variant script (one Cross press was not taken) |
| wonderswan | GunPey | `.sav` 2048 | same size/layout as beetle-wonderswan; weak: the hands-off game scored 0 here, so only the boot bytes (`01 51`) are set |
| wonderswan-color | Makai Toushi Sa-Ga | `.sav` 32768 | same size as beetle-wonderswan |
| ngp | Baseball Stars | `.flash` 7208 | NeoPop block format, same size as beetle-neopop |
| ngpc | King of Fighters R-2 | `.flash` 2600 | byte-identical to beetle-neopop |
| fds | all 7 scripts (Zelda no Densetsu, Link no Bouken, Metroid, F1 Race, both Golfs, 3D Hot Rally) | **`.fds` 131000**: the whole disk | same disk as fceumm/FCEUX except **one byte**: `0xFF` right after the last block written |
| pcenginecd | all 8 scripts (Ys I & II, Ys III, Dungeon Explorer II, Exile, Exile 2, Prince of Persia, Beyond Shadowgate, Dracula X) | `.sav` 2048 (BRAM) | 7 byte-identical to beetle-pce/beetle-pce-fast; Prince of Persia's time-left byte differs (CD timing) |

Not done in Mednafen: saturn (no corpus Saturn entries to compare yet and no BIOS run here),
virtualboy, lynx, pcfx, supergrafx (no scripts, or not attempted for time).

### Mednafen: FDS and PC Engine CD (added 2026-11-04)

**FDS (`fds/mednafen/`, 7 of 7 filed).**

- **Setup.** `disksys.rom` goes in `firmware/`. The disk starts inserted, side A.
- **Input.** `gen_sdlfeed.py` now maps `flip` to F8 (`command.insert_eject_disk`), then F6
  (`command.select_disk`) and F8 again, 30 frames apart.
- **Where / name.** `.mednafen/sav/<ROM name>.<md5>.fds` in the home folder.
  - The md5 is of the disk sides without any fwNES header. A headered and a headerless dump give
    the same name.
  - The file is the **whole disk, raw sides, 131000 bytes, no header**.
  - It is written on exit **only if the disk was written**, and read back instead of the ROM next
    time.
- **Against fceumm and FCEUX.** Each file differs in exactly one byte, the one right after the last
  block the game wrote: `0xFF` here, `0x00` in the ROM and in fceumm/FCEUX. Details are in
  `fds/NOTES.md`.

**PC Engine CD (`pcenginecd/mednafen/`, 8 of 8 filed).**

- **Module and BIOS.** Mednafen uses module `pce` and the Japanese System Card 3.0 by default
  (`pce.cdbios = syscard3.pce`, linked into `firmware/`).
- **No CHD.** Mednafen 1.32.1 has no CHD support. Seven discs were loaded as cue/bin extracted
  with `chdman extractcd`; Dracula X was loaded from its cue/img in place.
- **Where / name.** `.mednafen/sav/<cue name>.<CD layout md5>.sav` in the home folder.
  - The md5 is the one Mednafen logs as "CD Layout" at load.
  - The file is the raw 2 KiB BRAM, header `HUBM` with end pointer 0x8800.
  - It is written on exit, but **not at all if nothing wrote the BRAM**: a run idle on the System
    Card screen left no file.
- More in `pcenginecd/NOTES.md`.


## CrabEmu 0.2.0 (`mastersystem/crabemu/`, standalone; added 2026-11-04)

**The build.** There is no macOS release newer than 0.2.0 (2013). Development stopped and its SMS
core lives on in OpenEmu. The official `CrabEmu-0.2.0.dmg` from SourceForge (sha1 f454f00c…,
downloaded into `.cache/downloads/mastersystem/crabemu-0.2.0-dmg/`) holds a universal app with
**ppc, i386 and x86_64** slices.

- The x86_64 slice **runs under Rosetta 2**, started straight from its `Contents/MacOS/CrabEmu`.
- It is unsigned and not hardened, and its symbols are not stripped.
- The 0.2.0 source (`.cache/build/crabemu/CrabEmu-0.2.0/`) has Qt4 and SDL 1.2 clients and was
  only read, not built. Neither builds against what is installed here.

**Input and setup** (`work/standalone/crabemu/`):

- `crabfeed.dylib` is an x86_64 library loaded with `DYLD_INSERT_LIBRARIES`.
  - **Frames.** The emulation thread waits once per frame on the app's sound semaphore
    (`sound_wait`, which calls `semaphore_wait(sem)`). That call is interposed and counted.
  - **Pad.** On each frame the retro-run buttons are written into `sms_pad` (active low): b is
    button 1 and a is button 2, as in the libretro SMS cores.
  - **Pause and reset.** `start` calls `sms_z80_nmi()` (Pause). `reset` calls `sms_soft_reset()`,
    which is what the app's Reset menu item does.
  - **ROM.** It is opened with the app delegate's `application:openFiles:`.
  - **Screenshots.** The framebuffer pointer is taken from the app's own `glTexSubImage2D` upload
    and dumped (ARGB1555) at each `shot`.
  - **End.** `[NSApp terminate:]`, after which the app writes the save.
  - Addresses are the binary's symbols plus the ASLR slide.
- **Isolation.**
  - `CFFIXED_USER_HOME=<work>/home` moves `~` (the app's Application Support folders). The work
    home needs `Library/Application Support` created beforehand: the 2013 code uses
    `createDirectoryAtPath:attributes:`, which does not create parents.
  - Preferences still go through cfprefsd to the real home, whatever the environment says (tested
    on a throwaway domain, then deleted). So the dylib turns `NSUserDefaults` setters and
    `synchronize` and the recent-documents list into no-ops.
  - `-ApplePersistenceIgnoreState YES` is passed.
  - Afterwards there was no CrabEmu file in the owner's Preferences, Application Support or Saved
    Application State.
- **Region.** `-SMSDomestic NO` is passed on the command line. The app's default is the Japanese
  console.

**Where / name.** `Library/Application Support/ljsdcdev/CrabEmu/SRAM Saves/` in the home folder
(preference `SaveDirectory`).

- The file is named `<ROM file name *with* its extension>.ces`, for example
  `Phantasy Star (USA, Europe) (Rev A).sms.ces`. The Qt and SDL clients use the same `<rom>.ces`,
  beside the ROM by default.
- It is always **32768 bytes**: the whole cart-RAM buffer, `0x00` past what the game uses. A
  93C46 EEPROM game would get 128 bytes.
- It is written when the app quits or closes the ROM, and only if the game enabled cartridge RAM.

| Game | Filed | Against the other cores |
| --- | --- | --- |
| Phantasy Star | yes | byte-identical to mednafen, picodrive, sms-plus-gx, sms-mister |
| Ys | yes | same layout, play-state bytes differ (as every core here differs) |
| Ultima IV | yes | 9-10 bytes of play state differ from picodrive/sms-plus-gx |
| Miracle Warriors | yes | 2 bytes differ from picodrive/sms-plus-gx |
| Golden Axe Warrior | yes | byte-identical to picodrive, sms-plus-gx, sms-mister |
| Golfamania | yes | byte-identical to picodrive, sms-plus-gx |
| Penguin Land | yes | byte-identical to picodrive, sms-plus-gx, sms-mister |
| Monopoly | yes, with `Monopoly.sms-plus-gx.txt` | see below |

**Monopoly.**

- The shared script reached "GAME RESTORED" and was not filed. CrabEmu powers cart RAM on as zeros,
  which Monopoly takes for a saved game, as in picodrive and sms-plus-gx. So the zero-RAM variant
  script was used.
- Its file differs from every other core in about 5400 of the first 8192 bytes: `0xF0` where the
  others have `0x00`.
- CrabEmu fills the console's 8 KiB work RAM with `0xF0` at power-on (`smsmem.c`), and Monopoly
  copies uninitialised work RAM into its save. **The emulator's power-on RAM pattern ends up in the
  save file.**

**ColecoVision and SG-1000.** Nothing to file in either: no game in the library saves.

- CrabEmu has no ColecoVision save code at all.
- Its SG-1000 mapper never enables cart-RAM saving. An idle run of The Castle (8 KiB of cart RAM)
  wrote no `.ces`.
- The ColecoVision smoke test was stopped: a wrong BIOS path made the app show an error dialog on
  the owner's screen, and the instance was killed. Neither test was repeated, per the
  coordinator's instruction.

## RetroArch.app 1.22.2 versus tools/retro-run (fidelity)

Method (`work/standalone/retroarch/fidelity.sh`): the same buildbot core from `.cache/cores`, the
same content, the same starting files (a corpus entry's saves), the same number of frames, once
under `tools/retro-run` and once under RetroArch.app (`--config` to an isolated config,
`--max-frames=N`, which exits cleanly), then compare everything each wrote.

| Test | Core | Start | Frames | Bytes | Names | Directory |
| --- | --- | --- | --- | --- | --- | --- |
| Pokemon Crystal | gambatte | corpus `.srm` + 8-byte `.rtc` | 600 | identical `.srm` and `.rtc` | identical | RetroArch: `sav/Gambatte/` |
| Link's Awakening DX | gambatte | no save (game initialises SRAM) | 900 | identical (`ef199a21…`) | identical | `sav/Gambatte/` |
| Pokemon Emerald | mgba | corpus `.srm` | 900 | identical, and **no `.rtc` in either** | identical | `sav/mGBA/` |
| Boktai | beetle-gba (writes its own files) | `<stem>.<md5>.eep` + `.sav` | 900 | identical, no `.srm` in either | identical | core told `GET_SAVE_DIRECTORY = sav/Beetle GBA` |
| Street Fighter Alpha 3 | beetle-psx, `beetle_psx_enable_memcard1` | `.srm` + `.1.mcr` | 1200 | identical (both changed card 0 the same way at boot; `.1.mcr` untouched by both) | identical | `sav/Beetle PSX/` |

So **the bytes and file names retro-run writes are what RetroArch writes**, for core-written
files too. Three differences, all in where and when, not what:

1. **Folder per core.** RetroArch 1.22.2's defaults (dumped from a saved config) have
   `sort_savefiles_enable = "true"` (and `sort_savestates_enable = "true"`), so saves go to
   `<savefile_directory>/<core's library_name>/<content>.srm` (`Gambatte/`, `mGBA/`,
   `Beetle GBA/`, `Beetle PSX/`), and cores that write their own files get that subfolder from
   `RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY`. A save placed in the flat folder is **not loaded**
   (first run: "Skipping SRAM load", the game started fresh). retro-run writes flat.
2. **Autosave.** `autosave_interval = "10"` by default: RetroArch rewrites the `.srm`/`.rtc` every
   10 s while running (in place, same inode; it touched an unchanged Crystal `.srm`). retro-run
   writes only at exit.
3. **Skip when unchanged.** At unload RetroArch compares and logs `(unchanged, skipping write)`;
   with autosave off (`--appendconfig` `autosave_interval = "0"`) an unchanged `.srm` kept its
   mtime. retro-run always rewrites the file at exit.

Other defaults seen: `savefiles_in_content_dir = false`, `save_file_compression = false`,
`savestate_file_compression = true`, `block_sram_overwrite = false`. RetroArch also writes its
core options file and creates `states/<core>/` and `cheats/<core>/` folders; no other save files.

## Apps not run, and why

| App / core | Status | What it would take |
| --- | --- | --- |
| OpenEmu | **not run** (owner's instruction: it imports into the owner's library, no isolated mode) | A separate macOS user account, or a copy of OpenEmu's data folder swapped in and out while OpenEmu is closed; input needs Accessibility (OpenEmu has no scripting). OpenEmu keeps battery saves per core, `Library/Application Support/OpenEmu/<Core>/Battery Saves/` in the home folder. |
| DuckStation (`duckstation@duckstation`) | not installed: no Homebrew cask exists any more | Download the official macOS release; its hardened runtime rules out injection, it has no scripting, so input needs Accessibility. A "last resort" run would not help: DuckStation only writes a card that the game changed. Per-game cards are `memcards/<title>_1.mcd` by default. |
| melonDS (`melonds@melonds`) | not installed: the cask is disabled (fails Gatekeeper since 2026-09-01) | Same as DuckStation: no scripting; needs Accessibility. |
| Azahar (`azahar@azahar`) | not installed: no cask | Same; also decrypted 3DS dumps. |
| Snes9x for macOS (`snes9x@snes9x`) | not run | Cask exists, but the app has no scripting or CLI input, no isolated data folder (it uses `Library/Application Support/Snes9x` in the home folder), and quitting cleanly needs a menu/Apple Event; needs Accessibility. |
| Flycast.app 2.7 (`flycast@flycast`) | not run | The macOS build has no Lua (only the translation strings), SDL is linked statically (no interposition), and no data-dir override was found; needs Accessibility. VMU files are `vmu_save_A1.bin` style under `Library/Application Support/Flycast/` in the home folder. |
| PCSX2 2.9.63 (`pcsx2`, ps2) | booted, nothing filed | Isolation works (`-datapath <dir> -nogui -batch -fastboot`). Booting Ratchet & Clank made `memcards/Mcd001.ps2` and `Mcd002.ps2`, **8650752 bytes each, UNFORMATTED (all 0xFF)**; no game data without input (no scripting; PINE is memory-only). Not filed: a blank card is not a save. |
| bliss, 4do, emuthreeds | no macOS builds worth chasing | — |

## Safety

- The apps' own data folders and preferences were checksummed before any app ran and compared
  after every session: **identical**. Every app ran with an isolated data folder.
- `ps` checked for a 1Retro process before every app session (matching the executable path:
  another worker's `bfs … -path ./1Retro -prune` command line contains the word). None ran.
- New installs: PPSSPPSDL.app (89 MB, cask), mupen64plus (4 MB, formula; upgraded the shared
  sdl2-compat bottle). Scratch kept under `work/standalone/` (ROM copies, states, frame dumps and
  memory cards deleted).
- 2026-11-04 session (FDS, PC Engine CD, CrabEmu): Mednafen and FCEUX ran with `MEDNAFEN_HOME` /
  `FCEUX_HOME` in `work/standalone/`, each ROM copied into its work folder.
  - The owner's `.mednafen` and `.fceux` (and any matching preferences) were hashed and listed
    before and after (`work/standalone/snap2.sh`, `baseline/t4/`): **unchanged**.
  - CrabEmu: see its section above. No file in the owner's Library.
  - Nothing new was installed.
  - The PC Engine CD cue/bin extracted from CHDs were deleted after the runs. Re-extract with
    `chdman extractcd` to repeat a run.
