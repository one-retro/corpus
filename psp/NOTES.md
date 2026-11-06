# PSP (psp)

The played entry (`ppsspp@ppsspp/Lumines (USA)`, PPSSPPSDL.app over its debugger) is described
in `STANDALONE.md`. This file so far holds the GameFAQs pass.

## GameFAQs saves

Every save on the GameFAQs page of the corpus's PSP game, Lumines: 17 files from the section
"PSP Game Save Directory (ZIP)". They are filed under `psp/_psp/<release> [GameFAQs <id>]/`. Each
zip is replaced by what it held, with its inner paths: `ULUS10002LUMINES/PARAM.SFO` and so on.

### Formats

Every zip holds one PSP save folder: PARAM.SFO, DATA.BIN, ICON0.PNG and PIC1.PNG.

- **DATA.BIN** is 18464 bytes in all 17. It is encrypted by the system's savedata call, so nothing in
  it is readable.
- **The folder name** is PARAM.SFO's SAVEDATA_DIRECTORY: the game ID plus `LUMINES`.
- **No conversion is needed.** The folder goes under the memory stick's `PSP/SAVEDATA/`.
  `tools/gamefaqs/psp-savedata.py memstick` lays it out there and takes the folder name from
  PARAM.SFO. `psp-savedata.py info` prints the files and the PARAM.SFO fields.

| Game ID | Release | Saves |
| --- | --- | ---: |
| ULUS10002 | Lumines (USA) | 11 |
| ULJS00005 | Lumines (Japan) | 2 (6028, 6361) |
| ULES00043 | Lumines (Europe) (En,Fr,De,Es,It) | 4 (10693, 12894, 13975, 35055) |

The releases are named as the corpus's own `Lumines (USA)` entry is: the No-Intro name without
its version tag. No-Intro has `Lumines (USA) (v1.01)`; Redump has `Lumines - Puzzle Fusion (USA) (En,Ja)`.

What the zips hold beyond that:

- **One mislabelled section.** 11599 is posted under Europe, but it is a USA save (ULUS10002). It
  loads in the USA game.
- **One save without its folder.** 10693 has its four files at the zip's root. Its folder name,
  ULES00043LUMINES, is read from PARAM.SFO.
- **Three Windows thumbnail caches.** 6028, 6965 and 13975 also hold a Thumbs.db that indexes
  ICON0.PNG and PIC1.PNG. It is filed as served; PPSSPP ignores it.
- **Two kinds of SAVEDATA_FILE_LIST in PARAM.SFO:**
  - **No file name.** 13 saves have a 4-byte value that looks like a PSP RAM address
    (`98986a08`, `785f6908`), then zeros: the 2005 US saves, both Japanese saves and 35055.
  - **DATA.BIN and a 16-byte hash.** 10693, 11599, 12894 and 13975 (posted 2006) list it this way,
    as PPSSPP's own saves do.
  - The field looks to depend on the system software the save was made on. Both kinds load in
    PPSSPP: 11599 and the 2005 US saves.
  - 35055 is posted in 2026 but has the old kind, so it is not a PPSSPP save.

### Cores and results

The cores were `ppsspp`, the libretro buildbot core fd81cf7e under `tools/retro-run`, and
`ppsspp@ppsspp`, PPSSPPSDL.app 1.20.4. Each save ran on a memory stick holding nothing else.

| Release | Saves | ppsspp | ppsspp@ppsspp |
| --- | ---: | --- | --- |
| Lumines (USA) | 11 | 11 loads | 11 loads |
| Lumines (Japan) | 2 | not-run | not-run |
| Lumines (Europe) (En,Fr,De,Es,It) | 4 | not-run | not-run |
| **Total** | 17 | **11 loads, 0 rejected, 0 core-error, 6 not-run** | **11 loads, 0 rejected, 0 core-error, 6 not-run** |

Not-run means the library has Lumines (USA) only.

**What "loads" showed.** `scripts/psp/Lumines.load.txt` waits through the logos into the attract
demo, then presses START twice. With a save, the main menu shows the save's log-in character in its
top right corner, avatar and name: ROB (6965), RWPHSH (7486, 8368), MATT (6935, 6976), QUACOR (6895,
6907, 6931, 6963), USER (7123), PETER (11599). The uploader of 7486 names the character RWPHSH.
With no save, the same presses open "LOG-IN: Create log-in character", and the game writes a
fresh ULUS10002LUMINES at boot. The games did not rewrite a loaded save on the way to the menu.

### Running the cores

- **libretro PPSSPP (core option).** `ppsspp_backend = opengl` asks the frontend for a legacy
  OpenGL context. On macOS that is OpenGL 2.1, and the game never got past "Starting graphics": all
  frames were black. `auto` takes the OpenGL 4.1 core context and runs
  (`scripts/psp/ppsspp-auto.opt`).
- **libretro PPSSPP (timing).** The core emulates on its own thread in real time, so `retro_run`
  does not pace the game. Unpaced, 1800 script frames took 3 s and the game stayed black. With
  `--pace 60`, script frames are wall-clock sixtieths.
  - How long the boot takes depends on how fast the image is read: from the ROM drive it varied
    by a few hundred frames. The script therefore waits until the attract demo (frame 3000), where
    two STARTs reach the menu, and runs from a local copy of the image. Two runs from the copy gave
    identical frames.
- **PPSSPPSDL.app.** Isolated as in `STANDALONE.md` (HOME in the work folder, debugger WebSocket).
  - **No screenshot from the debugger.** `gpu.buffer.screenshot`, and `gpu.buffer.renderColor`
    with the CPU stepped, answer "Could not download output" on every backend tried: OpenGL with
    `VerticalSync = False`, Vulkan, and the software renderer.
  - **The frame read from VRAM instead.** With the software renderer the PSP framebuffer lives in
    emulated VRAM. `memory.read` of 0x04000000 (480x272, stride 512, 8888) is the frame, and those
    frames are the app's half of each proof.png.
  - **The name in RAM as well.** A dump of user RAM at the menu holds the character's name, the
    current log-in at one address and the save's score table (999,999 for RWPHSH) at another.
  - **Tools.** The client is `ppsspp_ws.py` from `STANDALONE.md` with `vramdump` and `ramdump`
    added (`work/gamefaqs/psp/`). The plan is `scripts/psp/Lumines.load.ws.txt`.

### one-saves (1saves)

1saves (0.4.0 and 0.7.0) has no PSP save format. `1saves convert lumines.<id>.zip` answers "this
archive holds no card and no save this reads" and lists the four files.
