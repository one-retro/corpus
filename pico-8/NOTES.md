# PICO-8

Eight BBS carts that keep a `cartdata` save, three libretro cores. 14 entries were filed out of
24 (cart, core) runs:
- **picante8:** 8 of 8.
- **fake-08:** 6 of 8. Two carts hit Lua errors in fake-08.
- **retro8:** 0 of 8, as expected: its `cartdata()` is empty, so it never writes anything.

The design note's file format holds. Where the file goes, when it is written, and how the id
becomes a file name all differ between the cores. Those differences are written up below.

PICO-8 is not in the one-saves registry. The system slug `pico-8` and the core slugs come from
the cloud backlog note `projects/backlog/pico8.md`.

## The carts

There is no DAT. Every cart is a `.p8.png` from the Lexaloffle BBS. Each was picked from an index
of every `cartdata()` id on the BBS, harvested from all 35,118 cart files there. The carts sit in
`.cache/roms/pico-8/` under their BBS file names, and each entry's `rom_source` is the cart's URL.

**Licence.** All eight are under CC4-BY-NC-SA, the BBS default. The individual posts were not
fetched to check for a different licence.

| Cart (entry folder) | Author | BBS thread | Cart file | `cartdata` id | What saves it (script) |
| --- | --- | --- | --- | --- | --- |
| Pico Dino | Yolwoocle | [tid 40759](https://www.lexaloffle.com/bbs/?tid=40759) | `picodino-2` | `yolwoocle_picodino_1` | die at the first cactus: new high score, `dset(0,52)` |
| Penny the Pumpkin - Director's Cut | kaimonkey | [tid 142093](https://www.lexaloffle.com/bbs/?tid=142093) | `penny_the_pumpkin-37` | `kai-pumpkin-2-v1-1` | walk into the next room: a checkpoint, slots 58-63 |
| Offline T-Rex Game v3 | Pordrack | [tid 32909](https://www.lexaloffle.com/bbs/?tid=32909) | `trexofflinegame-3` (not the latest) | `dinorunnerpico8-3` | jump a few times, hit a cactus: best score, slot 0 |
| Pico Racer | kometbomb | [tid 3198](https://www.lexaloffle.com/bbs/?tid=3198) | `20068` (2015, numbered) | `kb_picoracer` | race until the clock runs out, confirm on the course map: best score |
| Mot's Grand Prix | Mot | [tid 44700](https://www.lexaloffle.com/bbs/?tid=44700) | `mot_grandprix2-0` (menu cart) | `mot_gpp` | set Hard / Monza in the menu: slots 10-13 |
| Tiny Tactics | andrejtrindade | [tid 55172](https://www.lexaloffle.com/bbs/?tid=55172) | `tiny_tactics-5` | `ajt_tinytactics_1` | clear level 1-1 in 9 turns: "NEW RECORD! RECORD SAVED" |
| R-G-Blocks! 2 - Shapes | MoonShine | [tid 53347](https://www.lexaloffle.com/bbs/?tid=53347) | `rgblocks_2_shapes-4` | `r-g-blocks_2` | drop pieces until game over: high score, slot 0 |
| Cherry Bomb | Krystman | [tid 48986](https://www.lexaloffle.com/bbs/?tid=48986) | `cherrybomb-0` | `cherrybomb` | score 800, die, confirm on game over: high score, slot 0 |

Why these. They are well-known released carts, and between them they cover the design note's
edge cases:
- **Ids with a hyphen, which picante8 folds to `_`.** Three carts:
  - Penny: `kai-pumpkin-2-v1-1` is written as `kai_pumpkin_2_v1_1.p8d.txt`.
  - R-G-Blocks 2: `r-g-blocks_2` is written as `r_g_blocks_2.p8d.txt`.
  - T-Rex v3: `dinorunnerpico8-3`. Versions 4 and 5 of the same cart use `dinorunnerpico8_3`,
    so on picante8 two versions share one file (see the reload checks).
- **Ids bumped with a version suffix.**
  - Tiny Tactics: `ajt_tinytactics_1`.
  - Penny: v1.1 used `kai-pumkinv1` and then `kai-pumkinv1-1`. The Director's Cut used
    `kai-pumkin-2-v1-0`, then `kai-pumpkin-2-v1-0`, then `kai-pumpkin-2-v1-1`.
  - T-Rex: `dinorunnerremakepordrack`, then `dinorunnerpico8`, then `dinorunnerpico8-3`, then
    `dinorunnerpico8_3`.
  - R-G-Blocks!: version 9 moved to `r-g-blocks_2`, and version 10 went back to `r-g-blocks`.
- **One id, several carts.**
  - `cherrybomb` is used by 5 BBS threads: Krystman's shmup-tutorial game and four later
    threads by other authors.
  - `kb_picoracer` is used by 3 threads: Pico Racer, "Bicycle Race" and "SNOW RACER".
  - `r-g-blocks_2` is used by R-G-Blocks! 2 and by version 9 of the first R-G-Blocks!.
  - Mot's Grand Prix is a multicart. Its menu cart writes the chosen race into `mot_gpp`
    slots 14-16, then calls `load("#mot_grandprix2game")`. The game cart reads the same id, and
    `dget(30)` reports the result back to the menu. The game cart is not on the BBS as its own
    post and was not run.
  - The index shows the worst case: unrelated games colliding on a generic id. `highscore` is
    used by 4 threads from 3 authors. `0` is used by 12 threads, always through a variable.
- **Packed data.** Tiny Tactics packs three 10-bit level records into each 16.16 slot, so a
  slot is not always a number.
- **cstore.** Not played; see below.

### Tried and dropped

| Cart | Why it was dropped |
| --- | --- |
| Breakout Hero (`layzdevs_hero1_v2`) | It saves a high score only after the whole game is won. The first boot writes a default table, which is not play. |
| Just One Boss | It saves only when the boss is beaten. |
| ZEPTON | The table saves only a score above 0. Two attempts died at 0. |
| Witch n' Wiz | It writes a version number at boot. A real save needs a puzzle solved; not attempted. |
| Golf Sunday | It writes a default of 35 at boot. A real save needs a full round. |
| Mot's 8-Ball Pool | picante8 stops with `attempt to call a nil value (field 'unpack')`. |
| Terra | Both cores stop with `attempt to index ... 'lastitem'`. |
| Hoppencookie | Its menu wants a mouse. |
| CHOMP, Blockjoin | cstore carts. CHOMP needs timing to score. Blockjoin's level 1 did not respond to the scripted moves. |

## Carts x cores

| Cart | fake-08 | picante8 | retro8 |
| --- | --- | --- | --- |
| Pico Dino | filed | filed | parse error (`'}' expected near '\'`) |
| Penny the Pumpkin | filed | filed | parse error (P8SCII glyph in code) |
| Offline T-Rex Game v3 | filed | filed | plays; nothing written |
| Pico Racer | **failed**: mid-race Lua error, `attempt to get length of local 'c' (a number value)` | filed | plays to the course map; nothing written |
| Mot's Grand Prix | filed (the menu is drawn garbled, tiled down the screen; values right) | filed | parse error |
| Tiny Tactics | **failed**: `stack overflow` (line 799) on the first move | filed (`.picante8` script) | parse error (`\` integer division) |
| R-G-Blocks! 2 | filed | filed | parse error |
| Cherry Bomb | filed | filed | plays to "NEW HIGHSCORE!"; nothing written |
| Official PICO-8 | not runnable: paid software, not installed | | |

**The two fake-08 failures.**
- After a Lua error fake-08 drops to its built-in file browser. That screen prints the cart
  folder's absolute path, so such a frame must never become a proof.
- The error still unloads the cart, and unloading writes cartdata:
  - Pico Racer left an all-zero file.
  - Tiny Tactics left only its settings word (`06b00000`).
- Neither is a save of the play, so neither was filed. Both are kept out of the corpus, in
  `work/pico-8/rejected/`.

**retro8 (buildbot "0.1b ddc06a1")** runs three of the carts to the point where they call `dset`.
- It writes nothing, ever. `cartdata()` is `//TODO: implement` and returns nothing, and
  `dset`/`dget` only touch RAM. This is checked against `src/vm/lua_bridge.cpp` at
  libretro/retro8 `ddc06a14`.
- Five carts fail to parse: newer PICO-8 syntax (`\`, P8SCII glyphs in code).

## Buttons

| Core | O | X | Other |
| --- | --- | --- | --- |
| fake-08 | RetroPad **b** | RetroPad **a** | start: fake-08's pause menu |
| picante8 | RetroPad **a** | RetroPad **b** | Holding y (or select, an option) turns the d-pad into a mouse cursor. No pause menu: `menuitem()` is a TODO. |
| retro8 | RetroPad **a** | RetroPad **b** | |

fake-08 matches PICO-8's own pad layout: O is the bottom face button. picante8 and retro8 swap
O and X. So:
- Scripts press `a+b` wherever a cart treats O and X alike, and the d-pad wherever the cart
  allows (Pico Racer and T-Rex jump or accelerate with up).
- Tiny Tactics needs O and X apart. `Tiny Tactics.txt` is written for fake-08, and
  `Tiny Tactics.picante8.txt` (a and b swapped) is used for picante8 and retro8.

## The files

**Location and name.** Each core puts the file in its own folder under the frontend's save
directory:
- **fake-08:** `<savedir>/cdata/<id>.p8d.txt`. The id is used as given. fake-08 creates
  `cdata/` in `retro_init`.
- **picante8:** `<savedir>/picante8/<id>.p8d.txt`. Every character that is not `isalnum` or
  `_` becomes `_`: `-` folds, and uppercase is kept as it is. picante8 creates `picante8/` in
  `retro_load_game`.

Neither core writes anything else into the save directory. fake-08 has code to save a
`settings.ini` there, but nothing in the libretro build calls it.

**Format: identical in both cores.**
- 520 bytes: 8 lines, each 64 lowercase hex digits plus `\n`, and the last line ends in `\n`
  too. No header.
- Each 8-digit group is one slot, a 32-bit 16.16 value written most significant byte first,
  slots 0-63 in order.
- Real values from the corpus:
  - `00340000` = 52 (Pico Dino).
  - `0143a56e` = 323.646 (Pico Racer keeps the fraction).
  - `0028aa82` = 40.666 (T-Rex).
  - `06b02400` is Tiny Tactics' packed bits.

**Same play, same bytes.** For the same play the two cores write byte-identical files:
Pico Dino, Penny, Mot's Grand Prix and Cherry Bomb. T-Rex and R-G-Blocks differ only in the
score, because the random runs differed (30.67 vs 40.67, and 15 vs 5). Penny's two files are
identical even though the names differ.

**Reading the file back.** Both readers are lenient.
- fake-08 strips `\n`/`\r` and parses hex pairs.
- picante8 skips anything that is not a hex digit.
- So CRLF files and uppercase hex load in both.

**When the file is written**

| | fake-08 | picante8 |
| --- | --- | --- |
| Trigger | at unload (`retro_unload_game` → `CloseCart`), on `load()` of another cart, and when the cart switches id | after every PICO-8 frame in which `0x5e00-0x5eff` differs from what was last loaded or written (so `poke` counts as well as `dset`), and at unload |
| Killed mid-run (`kill -9` after Pico Dino's death screen) | no file: the save is lost | the file is already there |
| A cart that calls `cartdata` but never changes the data | writes an all-zero file at exit (T-Rex v5, Cherry Bomb's title) | writes nothing |
| More than one id per session | up to 4; the current id's data is saved before switching | only the first `cartdata()` counts; later calls return false and the data keeps going to the first id's file |

**Reload check.** Each cart was booted again with its own filed file in place.

| Cart | fake-08 | picante8 |
| --- | --- | --- |
| Pico Dino | HUD "HIGH 000052" | HUD "HIGH 000052" |
| T-Rex v3 | "BESTSCORE = 30" | "BESTSCORE = 40" |
| Mot's Grand Prix | menu opens on Hard / Monza | menu opens on Hard / Monza |
| R-G-Blocks! 2 | HI 15 | HI 5 |
| Cherry Bomb | title "HIGHSCORE 800" | title "HIGHSCORE 800" |
| Pico Racer | – | title "BEST SCORE 000323" |
| Tiny Tactics | – | skips the keyboard question; "TOTAL CLEARED: 1" |
| Penny | no visible change | no visible change |

- **Penny.** The cart does read slots 58-63 at init. The saved checkpoint, level 1 at tile
  (2,12), is next to the start.
- **What got rewritten.** No file changed on a reload except picante8's T-Rex: the run went on,
  and a better score was saved.
- **T-Rex v5 against v3's file.** Version 5 (id `dinorunnerpico8_3`) was booted on top of
  version 3's save:
  - picante8 shows v3's "BESTSCORE = 40", because both versions map to the same file.
  - fake-08 shows 0. It leaves `dinorunnerpico8-3.p8d.txt` alone and writes a new, all-zero
    `dinorunnerpico8_3.p8d.txt` beside it.

## The design note against the files

Confirmed:
- The file name `<id>.p8d.txt`, one shared folder for every cart, and the 8x64 hex format with
  16.16 values written most significant byte first.
- fake-08 and picante8 write identical bytes for the same play.
- retro8 writes nothing.
- picante8's folding of `-` to `_`, and that folding merges distinct ids. Here it merged two
  versions of one cart.
- Ids that are bumped and ids that are shared.

Wrong or missing:
- **"saved automatically with no flush"** holds only for picante8 (and presumably official
  PICO-8). fake-08 saves only at unload, cart switch or id switch: a crash or force-quit loses
  the session.
- **fake-08 writes all-zero files** for carts that never saved anything, and also after a Lua
  error. A sync should not treat a zero file as progress, and must not let it replace a real
  save from another device.
- **picante8 honours only the first `cartdata()` per session.** The note's "up to 4 ids" (172
  BBS threads) is wrong there: the extra ids' data lands in the first id's file.
- **picante8 refuses `load("#bbs_id")`.** Multicarts that chain by BBS id, like Mot's Grand Prix
  and Kalikan, cannot switch carts. fake-08 looks for `<id>.p8` or `<id>.p8.png` beside the cart.
- **cstore():**
  - fake-08 makes it a no-op (`picoluaapi.cpp`: "for now, not implementing this").
  - picante8 and retro8 do not define it, so a cart calling it stops with a Lua error.
  - A scan of the latest BBS carts found 143 that call `cstore`. Most are tools. The games among
    them are CHOMP, which keeps its high score in its own map, and Blockjoin, which keeps level
    progress there (`troske007_blockjoin_1`, which it opens with `cartdata` but never `dset`s).
  - On fake-08 their progress is silently lost. On picante8 they crash when they save.
- **Official PICO-8:** not checked. A short web search found no file written by it.

## Harness notes

- **retro8 blocks on stdin.** After any Lua error it calls `getchar()`, so a run with an open
  stdin hangs. Every run here had stdin from `/dev/null`: `work/pico-8/tools/file.sh` wraps
  `make-save.py` that way.
- **make-save's blank check misses fake-08's zero files.** It counts a file as blank only when
  every byte is `0x00` or `0xFF`, and fake-08's zero file is ASCII `0`s. So make-save files it as
  a save. Two such entries were caught by eye and moved out.
- **The cores are built from source.** Both builds are unmodified; see `BUILT-CORES.md`.
- **Frames are tiny.** They are 128x128: magnify before reading digits.
