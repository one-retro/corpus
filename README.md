# Save corpus

Real save files, written by real emulator cores, for testing 1Retro and one-saves against what
emulators actually produce rather than what we think they produce.

```
corpus/
  <system>/                 registry system slug (one-saves-registry/data/systems.json)
    <core>/                 registry core slug (cores.json)
      <game>/               the ROM's No-Intro/Redump name, without extension
        <files...>          exactly what the core wrote, named as it named them
        provenance.json     how this entry was made (see below)
        proof.png           the last screenshot of the run, showing the save
    NOTES.md                the games chosen, a core-by-core table, gaps and surprises
    <core>@<app>/           the same core inside a frontend that is not RetroArch-style
                            (mgba@mgba for the mGBA app, gambatte@openemu, dolphin-emu@dolphin):
                            apps write different names and layouts than RetroArch does
    _<producer>/            a producer that is not a registry core (real hardware via a
                            save manager such as _jksv); used sparingly
  scripts/<system>/<game>.txt   input scripts, shared by every core of the system
  tools/                    the harness, the runner, the fetchers
```

Nothing here comes from 1Retro. Users trust 1Retro with their saves; none of them are used, not
from the service, not from a local sync folder, not from a backup of one.

## Three ways an entry is made

**Played.** A libretro core runs under `tools/retro-run`, a headless frontend that writes saves the
way RetroArch does: battery RAM to `<savedir>/<stem>.srm`, the clock region to `<stem>.rtc`, on
close and before the game is unloaded, plus whatever the core writes into its save directory on
its own (Beetle Saturn's `.bkr`/`.bcr`, Flycast's VMU files, PPSSPP's `SAVEDATA`). A script
presses the buttons that reach a genuine save in the game: a named file, a save point, a menu
save. The same script is replayed in every core of the system, so each core writes its own file
from the same play.

This was checked against RetroArch 1.22.2 itself (gambatte, mgba, beetle-gba, beetle-psx, see
`STANDALONE.md`): file names and contents were identical in every run, including files the cores
write on their own. RetroArch differs only in where and when: by default it saves into a per-core
subfolder (`saves/Gambatte/...`) and ignores a save in the flat folder; it autosaves every 10
seconds; and it skips writing a save that has not changed. Entries here are flat, as a user who
turned "sort saves by core" off would have them.

**Downloaded.** For cores that cannot run here (MiSTer and openFPGA cores, standalone emulators,
libretro cores with no macOS build), a save that core or emulator wrote, found online.
`provenance.json` then names the URL, the page it came from, who made it if known, any licence,
and the date fetched.

**Device backup.** The owner's own devices, from backups that are not 1Retro syncs: an
Analogue Pocket's SD card (`Saves/`), a 3DS's JKSV backups (`JKSV/`), and
saves made on the owner's MiSTer for this corpus. `"method": "device-backup"` (or `"played"` with
`"frontend": "mister"` when made by script on the MiSTer), with the backup path (relative to the device's SD card), the device, and
how the core was attributed when the folder alone does not say (a Pocket's `common/` folder is
shared by every core of a platform).

## provenance.json

```json
{
  "method": "played",            // or "downloaded"
  "system": "gbc", "core": "gambatte",
  "core_file": "gambatte_libretro.dylib", "core_name": "Gambatte", "core_version": "v0.5.0 77f2567",
  "frontend": "retro-run (writes saves as RetroArch does)",
  "rom": {"name": "...gbc", "sha1": "...", "size": 1048576},
  "script": "scripts/gbc/....txt", "frames": 1200, "options": null,
  "files": {"<name>.srm": {"size": 32768, "sha1": "..."}},
  "created": "2026-11-03", "note": null
}
```

A downloaded entry has `"method": "downloaded"`, `"url"`, `"source_page"`, `"source"` (site),
`"author"`, `"licence"`, `"fetched"`, `"what_it_is"` (one line: whose file, what state the game is
in, as far as the page says), plus `"files"` as above.

## Tools

All Python runs with `-I`.

| Tool | What it does |
| ---- | ------------ |
| `tools/fetch-core.sh SLUG...` | Downloads registry cores from the libretro buildbot into `.cache/cores/`, prints paths. `tools/cores.tsv` is the slug map; a slug it lacks has no macOS build. A core built from source (`BUILT-CORES.md`) at `.cache/cores/built/<arch>/<slug>_libretro.dylib` is used first, and a `.json` beside it (repo, commit, build) lands in provenance as `built_from`. |
| `tools/rom.py list SYSTEM [FILTER]` | Games a No-Intro 1G1R set has for a cartridge system. `$ROMS` names the folder of its zips. |
| `tools/rom.py get SYSTEM "NAME"` | Extracts one into `.cache/roms/SYSTEM/`, prints its path. |
| `tools/retro-run/retro-run` | The harness. `--help` lists the script commands. `retro-run-x86_64` is the same for Intel-only cores (Rosetta). |
| `tools/make-save.py SYSTEM CORE ROM SCRIPT` | Runs a script in a core in a fresh directory and files what it saved, with provenance and proof. `--dry` to develop a script without filing. Also files what the core wrote into its working directory (`cwd/`), its system directory with `--keep-sysdir` (`system/`), or its own HOME with `--home` (`home/`); `--subsystem ID --slot FILE` loads a subsystem (Sufami Turbo); `--rom-source URL` records a homebrew ROM's origin. |
| `tools/ps2-save.py CORE ROM SCRIPT` | make-save for PS2: a real system directory and HOME per run, filing the memory cards the cores keep there (`ps2/NOTES.md`). |
| `tools/retro-run/crop.py` | `crop` magnifies part of a frame, `tile` puts many frames on one sheet. |

### Script commands, briefly

```
wait N                 run N frames
press BTN[+BTN] [N]    hold for N frames (default 4)
tap BTN [COUNT] [GAP]  press, then wait GAP frames, COUNT times (mashing through text)
stick X Y [N]          left analog stick, -32767..32767 or min/max
key KEY [N] / type TXT keyboard, for computers
repeat N ... end       loop
shot NAME              screenshot (the last one becomes proof.png)
savestate P / loadstate P   for developing a long script a stretch at a time
dump P                 write battery RAM now
```

Buttons are libretro's: `b y select start up down left right a x l r l2 r2 l3 r3`. On a
PlayStation pad `b` is Cross, `a` Circle, `y` Square, `x` Triangle.

### Developing a script

1. `make-save.py ... --dry` against one reliable core, with `shot`s along the way. Read the PNGs
   (tile them with `crop.py tile`; GB/NES frames are tiny, magnify them).
2. For long games, `savestate work/<system>/x.state` at a milestone and continue from it with
   `--state`/`loadstate` while you work out the next stretch, then splice the stretches back
   into one script that runs from power-on. States are per core; scripts are not.
3. Wait generously. Cores differ by a few frames in boot and load times, and a press that lands
   a frame early in one core is lost. A script that works with margin works everywhere.
4. Finish with a `shot` that shows the save happened: the file on a file-select screen, a
   "saved" message, the memory card manager.

### Known core quirks

- N64: GLideN64 renders black frames here. Use the software RDP:
  `mupen64plus-rdp-plugin = angrylion` (Mupen64Plus-Next) and
  `parallel-n64-gfxplugin = angrylion` (ParaLLEl N64) in an `--options` file. The save layout does
  not depend on the renderer.
- OpenGL cores (Flycast, Dolphin, PPSSPP, Beetle PSX HW, Citra) get an offscreen OpenGL 4.1 core
  context. Vulkan-only cores cannot run.
- `retro-run` plugs a joypad into ports 1 and 2 (RetroArch plugs one into every port; bsnes-jg
  crashes without port 2). `--ports 1` gives the old port-1-only behaviour; replays of existing
  entries with the change wrote byte-identical saves.
- BIOS files go in `.cache/bios/<system>/`; each entry there (file or directory) is linked into
  the core's system directory, so `dc/dc_boot.bin` works.

## Not committed

`.cache/` (cores, ROMs, BIOS, scratch runs) and `work/` never leave this machine. ROMs and BIOS
are commercial dumps.

## Licence

[CC0 1.0](LICENSE): the tools, scripts, notes, and the saves made for this corpus (played,
device backups) are dedicated to the public domain, as far as the law allows.

Two exceptions. Downloaded entries (`"method": "downloaded"`) are other people's files and keep
their own terms; each one's `provenance.json` names where it came from and any licence it was
published under. And the games are their publishers': a save or screenshot holds the game's data
only as far as playing it put it there, and CC0 grants no rights in the games.
