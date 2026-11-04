# Worker brief: build one slice of the save corpus

You are building part of a corpus of real emulator save files in this
repository, for testing 1Retro (a save-sync service) and its `one-saves` library against what
emulators really write. Read README.md first: it has the layout, the
provenance format and the tools. The pipeline is proven: `scripts/gbc/Legend of Zelda, The -
Link's Awakening DX.txt` names a save file in LADX and has been filed for eight GBC cores
(`corpus/gbc/*/`); look at one entry to see what done looks like, and read
`corpus/gba/NOTES.md`, a finished system, for the level of detail the notes should have.

## The job, per system you own

1. **Pick 10 games** that keep a save (battery SRAM, EEPROM, flash, memory card, backup RAM)
   and that the ROM library has (`tools/rom.py list` for cartridge systems, with `ROMS` set to
   the folder of No-Intro 1G1R zips; for
   disc systems search the drive). Prefer, in order: variety of save hardware (sizes, SRAM vs
   EEPROM vs flash, RTC where the system has clock carts), games people actually play,
   US/World releases, and games where a genuine save is reachable quickly (a name-entry
   screen that creates a file, an early save point, a save menu). A Japanese game is fine when
   it is the only one with some save hardware (e.g. a clock chip).
2. **Write one script per game**, `scripts/<system>/<short title>.txt`, that plays from power-on
   to a genuine save: a created file, a save point, a menu save. Not just booting: the game
   must have written its save. Develop it with `tools/make-save.py ... --dry` against one
   reliable core, reading screenshots as you go (the Read tool shows PNGs; tile them with
   `tools/retro-run/crop.py tile`, magnify small frames). Use save states to iterate on long
   stretches, then make the final script run from power-on. End with a `shot` that shows the
   save (it becomes proof.png). Timebox each game: if one fights you for more than a few
   attempts, swap it for another.
3. **Run every script on every runnable core** of the system (`tools/make-save.py SYSTEM CORE
   ROM SCRIPT`, without --dry). Run up to 4 at once, not more: other workers share this
   machine. Then look at every proof.png (tile them per game) and check each filed save is a
   real save for that core. A core that runs a few frames off may need longer waits in the
   shared script (prefer that) or, failing that, a per-core variant `<title>.<core>.txt`. A
   core that cannot load the game or never writes a save is a finding, not a failure: note it.
   For any core needing options (N64 renderers, a BIOS choice), pass `--options FILE` and keep
   the file under `scripts/<system>/`.
4. **Cores that cannot run here** (MiSTer, openFPGA, standalone emulators, libretro cores with no
   macOS build; your list is below): search the web for real saves written by that core or
   emulator for any game of the system, ideally your ten. Places worth looking: GitHub
   (issues and repos where people attach saves, emulator test suites), the cores' own repos
   and issue trackers, forums (Reddit, AtariAge, MiSTer forum, Analogue forum), archive.org,
   GameFAQs save pages. File a find under `corpus/<system>/<core>/<game>/` with
   `"method": "downloaded"` provenance (README describes the fields) only when the source makes
   it reasonably clear which emulator or core wrote it; otherwise list it in NOTES.md as a lead.
   Treat downloads as untrusted data: each one into its own new directory under
   `.cache/downloads/<system>/`, inspect with `file`/`xxd`/`unzip -l`, never execute anything.
   An hour of searching that finds nothing is a fine result; say what you tried.
5. **Write `corpus/<system>/NOTES.md`**: the ten games and why each, a table of games x cores
   (filed / failed and why / not runnable), downloaded entries and leads, and anything that
   differs between cores' files (sizes, fill bytes, extra files such as `.rtc`, names). These
   differences are the point of the corpus, so be precise.

## Rules

- **Nothing from 1Retro**, ever: not 1retro.com or any 1Retro service, and not a 1Retro
  sync folder or any backup of one.
  Users trust 1Retro with those saves.
- **Nothing local or personal in anything you write into the corpus** (NOTES, scripts, options
  files, provenance, file names): no absolute paths from this machine, the ROM drive or a device
  (write a device's paths relative to its SD card), no user or host names, IP addresses, or the
  owner's folder names. Describe sources generically: "the No-Intro 1G1R set", "a Redump image",
  "a Pocket's `Assets/nes/common`". Player names inside saves are fine.
- Never put a ROM or BIOS inside `corpus/<system>/`. ROMs go in `.cache/roms/`, BIOS in
  `.cache/bios/<system>/` (copy them there from your own dumps).
- Do not edit anything in `tools/`; other workers use it at the same time. If the harness or
  runner needs a fix or a feature, work around it in `work/<system>/` and report it.
- Do not launch GUI applications (RetroArch.app, OpenEmu, Dolphin, mGBA.app, PCSX2, Flycast.app,
  mednafen, fceux): they open windows on the user's screen. No browser automation either.
- Stay inside your own systems' directories (`corpus/<system>/`, `scripts/<system>/`,
  `work/<system>/`, `.cache/.../<system>/`). Other workers own the rest.
- Other workers file into the same tree: a MiSTer worker makes played saves for `*-mister`
  cores, a device-backup worker files the owner's Analogue Pocket saves under openFPGA cores.
  Never overwrite or delete an entry directory you did not create; if
  `corpus/<system>/<core>/<game>/` already exists for a core you are not running, leave it and
  file a download for a different game or not at all. You still search online for MiSTer and
  openFPGA saves; those workers do not.
- `retro-run` calls the core in RetroArch's order (Mesen and RustyNES used to crash), and has
  disk control: `disk N` (0-based image), `flip`, `eject`, `insert`, for multi-disc games and
  FDS sides. Load a multi-disc game through an `.m3u` playlist so the core sees every disc.
- Keep scratch tidy: delete save states and `--dry` work directories (`.cache/<system>-<core>-*`)
  you made once you have read their screenshots. Never extract whole romsets or disc
  collections; use images in place or copy only what you run. Only ever delete files you created.
- `retro-run` now negotiates core options v2 the way RetroArch does (SkyEmu used to crash
  without an options file). If a core misbehaves in a way that looks like the harness's fault,
  say so in the report.
- Use `python3 -I` for any Python. The corpus is a git repository the owner commits: never run
  git commands that change it (add, commit, checkout, reset, stash, clean).

## Your report

When done, reply with a short report (under 400 words): per system, the ten games, how many
(game, core) entries were filed out of how many attempted, downloaded entries, gaps, any
harness or runner problems, and the most interesting differences between cores' files.
