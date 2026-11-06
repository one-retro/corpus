# GameCube (gc)

The played entries (`dolphin-emu@dolphin/`, Dolphin.app with a TAS movie) are described in
`STANDALONE.md`. This file so far holds the GameFAQs pass.

## GameFAQs saves

Every GameCube save on the GameFAQs pages of the two corpus games, Kirby Air Ride and Mario Kart:
Double Dash!!: 20 files, filed under `gc/_usb-memory-adapter/` (19) and `gc/_max-drive/` (1) as
`<Redump name> [GameFAQs <id>]/`, each with its provenance and, where a core ran it, a proof.png
(the libretro frame, then Dolphin.app's frame dump).

### Formats

| GameFAQs section | Files | What the bytes are | Conversion |
| --- | ---: | --- | --- |
| GameCube USB Memory Adapter Save | 19 | **GCI**: the card's 64-byte directory entry (game code, maker, file name, modified time, block count, comment offset) and the save's 8 KiB blocks. | None: a GCI goes into Dolphin's GCI folder (`GC/<region>/Card A/`) as it is. `tools/gamefaqs/gc-gci.py place` copies it there under the name Dolphin gives it (`<maker>-<game code>-<file name>.gci`, special characters escaped `__xx__`). |
| GameCube MaxDrive Save | 1 (5922) | **MaxDrive .sav** (Datel's PC software): a 0x80-byte header (`DATELGC_SAVE`, a title, a description), the directory entry with bytes 0x06/0x07 and every pair from 0x2C to 0x3F byte-swapped, then the blocks. | `gc-gci.py place` drops the header and swaps the entry back, as Dolphin's `GCMemcardUtils` reads a `.sav`; the result is a 24640-byte GCI. |

GCI is not only the USB Memory Adapter's format: Dolphin and homebrew card managers export the
same bytes, and nothing in a GCI says which tool wrote it. The seven uploads from 2016 on (24609,
24767, 29622, 32586, 33503, 35054, 35306) are likely such exports. They are filed under
`_usb-memory-adapter` as the brief maps `.gci`.

Every section's region matches the game code in the file: North America is GKYE/GM4E, Japan
GKYJ/GM4J, Europe GM4P. Things seen in the bytes:

- Six files are Time Trial **ghosts**, not game data. A ghost is a card file of its own (5 blocks),
  named with encoded characters (`5#R%#*EV*31!!!ECS^\`3>GE>*2"5!aa`). Its comment carries the time
  (`Ghost Data 2:29:682`, `Geist-Daten 2:00:640`, `Données fantôme 1'47"332`).
- 3315 (Japan) is dated **2045-07-27** in its directory entry and its comment (`ゲームデータ 45/07/27`).
  The console's clock was set that way; the game writes both from it.
- 5922 (MaxDrive) has a modified time of 2039-09-21 10:48:41, which matches nothing. Its comment
  reads `Game Data 02/09/04`. Dolphin's reader does not swap this field, and neither does gc-gci.py.
- Japanese comments are Shift-JIS (`カービィのエアライド` / `セーブデータ 2025/08/23`). The European
  ghosts' comments are Windows-1252.

### Cores and results

The cores were `dolphin-emu`, the libretro buildbot core 2609.0.169+32c61f9d0e under
`tools/retro-run`, and `dolphin-emu@dolphin`, Dolphin.app 2606a. Each save ran in its own fresh
folder, with no other file on the card.

| Release (Redump) | Saves | dolphin-emu | dolphin-emu@dolphin |
| --- | ---: | --- | --- |
| Kirby Air Ride (USA) | 3 | 3 loads | 3 loads |
| Kirby's Airride (Japan) | 1 | not-run | not-run |
| Mario Kart - Double Dash!! (USA) | 7 + 1 ghost | 8 loads | 8 loads |
| Mario Kart - Double Dash!! (Japan) | 1 | not-run | not-run |
| Mario Kart - Double Dash!! (Europe, Australia) (En,Fr,De,Es,It) | 2 + 5 ghosts | not-run | not-run |
| **Total** | 20 | **11 loads, 0 rejected, 0 core-error, 9 not-run** | **11 loads, 0 rejected, 0 core-error, 9 not-run** |

Not-run means the library has no image of that release. It has only the USA discs of both games,
plus Kirby Air Ride (Europe), and none of the saves is for that one.

What "loads" showed, the same screen in both cores:

- **Kirby Air Ride**: Air Ride > Records > Checklist (`scripts/gc/Kirby Air Ride.load.txt`).
  - 35054 and 24767 show 120/120. 3515 shows 38/120 ("about 1/2 of goals").
  - With no save, the libretro core stops at "There is no Kirby Air Ride data ... Make a new save data
    file?". Dolphin.app made the file without asking, as in its played entry.
- **Mario Kart: Double Dash!!**: title menu > RECORDS > GRAND PRIX
  (`scripts/gc/Mario Kart - Double Dash!!.load.txt`).
  - Each save's Mushroom Cup trophies, times, points and initials appear: MEM, CBT, CCC, ANL, ESS, FOO, JON.
  - With no save, the game asks to create data.
  - A save with everything unlocked also changes the title art (Toad, Toadette, Petey and King Boo
    appear) and the character select (20 drivers instead of 16).
- **Ghost (29622)**: the game first asks to create its main data (YES). Then Time Trials > Star Cup
  > Yoshi Circuit opens LOAD GHOST DATA, listing "Yoshi Circuit 2:29:682 MII, 09/17/23"
  (`... .ghost.load.txt`). With no save, the race starts directly.

Kirby Air Ride rewrites its file on the way to the checklist, in both cores: a new modified time,
first block 5 on Dolphin's virtual card, and about ten payload bytes. Mario Kart leaves its file
untouched when only its records are viewed. The filed files are the downloads, not these
rewrites.

### Running the cores

- **libretro Dolphin.** The buildbot core runs here with the OpenGL 4.1 core context.
  - It needs Dolphin's `Sys` folder at `<system>/dolphin-emu/Sys`. It was copied from Dolphin.app.
  - It keeps its user folder at `<savedir>/User/`, with slot A a GCI folder (`User/GC/USA/Card A/`).
  - By default it emulates on its own CPU thread, and `retro_run` returns at once: 1800 script
    frames took 2 s. `dolphin_main_cpu_thread = disabled` makes script frames emulated frames.
  - `dolphin_osd_enabled = disabled` removes the "OpenGL driver does not support
    ARB_buffer_storage" messages from the frames. Both options are in
    `scripts/gc/dolphin-single-core.opt`.
- **Dolphin.app.** Isolated as in `STANDALONE.md` (`-u`, `-b`, movie with `-m`, frame dumps).
  - **Both games read the pad twice per video frame.** A movie advances one input per read, so
    the `.load.dtm.txt` plans are the libretro scripts with every count doubled. The first,
    undoubled try ran through the menus before they could take input.
  - The menus that take the analog stick (Mario Kart's title menu, cup and course select) get
    `stick 128 0` (down) and `stick 255 128` (right). The GameCube's Y axis points up.

### one-saves (1saves)

1saves was run on every original: 0.4.0 as installed and 0.7.0 built from its repository.

- **It does not read a loose save.** `1saves convert x.gci` answers "could not tell what this file is;
  name the format with --from". It says the same with `--from dolphin`, `--from gci` or `--system gc`.
- **A MaxDrive `.sav` is misread.** It is taken as an unidentified "flat cartridge save": one 24768-byte
  part, the Datel header kept, no game. With `--system gc`, only the system is added.
- **On a card it agrees with gc-gci.py, with three exceptions.** `tools/gamefaqs/gc-gci.py card`
  stores the save in a blank card made by `1saves new gc` (`--shift-jis` for the Japanese ones). On
  that card, both versions read the same game code, file name, modified time and payload for all
  20. They disagree with gc-gci.py on:
  - 33503 (GKYJ) and 3315 (GM4J): no label at all. The Shift-JIS comment is not decoded, even on a
    Shift-JIS card.
  - 5742: the label is only "Mario Kart: Double Dash!!". The second comment line, `Données fantôme
    1'47"332` (Windows-1252 é and ô), is dropped.

The card that `gc-gci.py card` writes is a real card. With slot A set to Memory Card
(`SlotA = 1`), the libretro core loaded 35054 from such a 251-block card, and the checklist
showed 120/120, as from the GCI folder.
