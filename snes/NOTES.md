# SNES

Nine games, 12 runnable libretro cores, 89 played entries (out of 96 attempted runs), plus 8
downloaded entries (MiSTer, Analogue Pocket). The 21 `device-backup` entries under `agg23-snes/`
were filed by someone else, not by this slice.

A second pass added the special chips (see [Special chips](#special-chips)): ST010, ST011, BS-X
and Sufami Turbo now have entries, 24 more in all (about 60 runs); ST018, SuperFX, SPC7110,
S-DD1 and OBC1 still have none.

Firmware: `.cache/bios/snes/` holds `dsp1b.rom` (the No-Intro "DSP1 B (World) (Enhancement
Chip)" dump), plus `dsp1b.program.rom` (its first 6144 bytes) and `dsp1b.data.rom` (its last 2048
bytes). With them the bsnes family boots Super Mario Kart. No filed game needs them.

For the special chips it also holds:
- `st010.rom`, `st011.rom` (53248 bytes) and `st018.rom` (163840): the No-Intro "ST010 (Japan,
  USA)", "ST011 (Japan)" and "ST018 (Japan) (Enhancement Chip)" dumps, found among the library's
  enhancement-chip dumps (they are not in the 1G1R set). Also split as `stNNN.program.rom` +
  `stNNN.data.rom`: 0xC000 + 0x1000 for the ST010/ST011, 0x20000 + 0x8000 for the ST018. The
  bsnes family reads the split names, Mesen2 either. No Cx4/DSP2-4 game was needed, so those dumps
  were left out.
- `STBIOS.bin` (snes9x) and `SufamiTurbo.sfc` (Mesen2): copies of "Sufami Turbo (Japan)", the base
  cart, which these cores want in the system directory when a mini-cart is loaded on its own.
- `BS-X.bin`: a copy of the BS-X cart, which bsnes, snes9x and Mesen2 look for when a `.bs` memory
  pack is loaded on its own. No filed run used it.

## The games

| Game (script) | Save hardware | Why |
| --- | --- | --- |
| Legend of Zelda, The - A Link to the Past (USA) | 8 KB SRAM, LoROM | Popular; registering the name "ABC" writes file 1 at once. |
| Chrono Trigger (USA) | 8 KB SRAM, HiROM | Popular; walks out of Crono's house and saves to slot 1 from the world map menu. |
| Super Tetris 3 (Japan) (En) | 2 KB SRAM | The 2 KB size. Registering player "ABC" writes the player record (3 bytes at `$0019`). The game formats SRAM at boot (`00 11 22 .. FF`). |
| SimCity (USA) | 32 KB SRAM | New city "ASDF", saved to slot 2 from LOAD.SAVE. |
| Kaite Tsukutte Asoberu Dezaemon (Japan) | 128 KB SRAM, LoROM | The 128 KB size. ETC. > Stage copy writes about 3.4 KB. On a blank cart the game first fills all 128 KB with its sample game ("S-RAM CHECK!"). |
| Kirby Super Star (USA) | SA-1, 8 KB BW-RAM | SA-1. A Gourmet Race Course 1 time trial writes the best time into the save block at `$1F00` (three copies of `0x51` bytes). The rest of BW-RAM is SA-1 work RAM and changes every frame. |
| Pebble Beach no Hatou New - Tournament Edition (Japan) | SA-1, 64 KB BW-RAM | SA-1 at 64 KB. Renaming member Player-1 to "ABC" writes `ABC` at `$E010`. |
| Daikaijuu Monogatari II (Japan) | S-RTC + 8 KB SRAM, ExHiROM (5 MB) | The clock chip. Sets the clock, sits through the opening, then saves on the save mark in the first cave. About 23.5k frames. |
| (no tenth game) | | See gaps. |

Every script ends with a shot of the save: the slot or record on screen, or a "saved" message.

## Games x cores

✔ filed, ✘ failed (reason below), – not run.

| core | ALttP | CT | ST3 | SimCity | Dezaemon | KSS | Pebble | Daikaijuu II |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| snes9x | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ `.rtc` 20 |
| snes9x-2010 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ `.rtc` 20 |
| snes9x-2005-plus | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ no RTC (a) |
| snes9x-2005 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✘ (b) |
| snes9x-2002 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✘ segfault on load |
| bsnes | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ `.rtc` 16 |
| bsnes-hd-beta | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ no `.rtc` (c) |
| bsnes-mercury (accuracy) | ✔ | ✔ | ✔ | ✔ | ✘ (d) | ✔ | ✔ | ✘ (e) |
| bsnes2014 (accuracy) | ✔ | ✔ | ✔ | ✔ | ✘ (d) | ✔ | ✔ | ✘ (e) |
| higan-super-famicom (x86_64) | ✔ | ✔ | ✔ | ✔ | ✘ (d) | ✔ | ✔ | ✔ `.rtc.ram` 16 |
| mednafen-bsnes | ✔ (f) | ✔ (f) | ✔ (f) | ✔ (f) | ✔ (f) | ✔ (f) | ✔ (f) | ✔ (f) `.rtc` 20 |
| mesen-s (Mesen2) | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ no `.rtc` (g) |
| snes-mister, agg23-snes, timboettiger-pro-action-replay, mednafen | not runnable here |
| beetle-supafaust, bsnes-jg, chimerasnes, higan-super-famicom-balanced (nSide) | built from source since, 8 of 8 each (BUILT-CORES.md) |

Notes on the table:

- **(a)** snes9x-2005 and snes9x-2005-plus have no S-RTC. The game says 時刻の入力に失敗しました, ざんねんながらPLGシステムは使用できません ("setting the time failed; the PLG system can't be used") and plays on without a clock. The save is real; there is just no clock to save.
- **(b)** snes9x-2005 behaves as in (a), but the opening runs differently and the run stalls in the green temple room before the cave. A longer mash didn't help, so there is no save. The run was unfiled and noted in status.jsonl.
- **(c)** bsnes-hd-beta's clock runs in-game (the save screen shows 0:02:29), but the core writes no clock file, so the time is lost on reload.
- **(d)** Dezaemon reports "S-RAM BREAK DOWN!". These cores do not map all 128 KB of LoROM SRAM: the game's test pattern lands only in `0x0000-0x7FFF` and `0x10000-0x17FFF`, and the rest stays `0xFF`. The 131072-byte files are not saves. They were moved to `work/snes/rejected/` and noted in status.jsonl.
- **(e)** bsnes-mercury and bsnes2014 refuse to load the S-RTC game unless an `rtc.ram` exists in the *system* directory ("Cannot find requested file in system directory: .../system/rtc.ram"). Given a 16-byte `rtc.ram`, both crash with SIGTRAP right after "Load BIOS".
- **(f)** mednafen-bsnes (Mednafen bSNES v0.9.26) does not hand battery RAM to the frontend: libretro save RAM size is 0. It writes its own `<stem>.srm`, and a `<stem>.rtc` for every game, into the save directory. It then aborts (SIGABRT) while unloading, after the files are written, so make-save.py records the run as failed. These entries were filed from the run directory by `work/snes/file_aborted.py`; the note in provenance says so.
- **(g)** Mesen2 runs the S-RTC game, but the clock reads 0:00:00 throughout and the core writes no clock file.

## What differs between the cores' files

**Names.** Every core writes `<rom stem>.srm`. The clock files differ:
- `<stem>.rtc`: bsnes, snes9x, snes9x-2010, mednafen-bsnes.
- `<stem>.rtc.ram`: higan. The core writes this file itself, not the frontend.
- An empty `<stem>.rtc` for *every* game: mednafen-bsnes (0 bytes for the games without a clock).
- No clock file: bsnes-hd-beta, mesen-s, snes9x-2005-plus.

**Sizes.** Every core that ran a game wrote the same `.srm` size, and it is the header's size: 2048, 8192, 32768, 65536 or 131072.

**Fill of untouched SRAM.** This is the main difference, and it makes otherwise equal saves differ byte for byte:

| Cores | Fill |
| --- | --- |
| bsnes, bsnes-hd-beta, bsnes-mercury, bsnes2014, higan, mednafen-bsnes | `0xFF` |
| snes9x, snes9x-2010 | `0x60` (snes9x's SRAM initial value) |
| snes9x-2002, snes9x-2005, snes9x-2005-plus | `0x00` |
| mesen-s (Mesen2) | Random bytes (its default RAM power-on state), so its files differ from run to run |

In ALttP, for example, `0x1E00-0x1FFF` is `FF…` in bsnes, `60…` in snes9x, `00…` in snes9x-2002 and noise in Mesen2. The game data itself agrees.

Games that format all of SRAM themselves come out byte-identical across all cores that ran them:
- Super Tetris 3: 12 cores, sha1 `af7270c9…`.
- Dezaemon: 9 cores, `fe972f66…`.

**SA-1 BW-RAM.** It doubles as work RAM, so KSS files differ between cores even where the record is identical (10 distinct sha1s out of 12; bsnes = bsnes-hd-beta and bsnes-mercury = bsnes2014). The record block at `$1F00` is what to compare. The recorded time also varies by a fraction of a second between cores: most show 01:00:94, a few are slightly slower.

**RTC layouts (Daikaijuu II).** The game was set to 1996-08-02 00:00, so the default clock. The S-RTC digit order is: seconds lo/hi, minutes lo/hi, hours lo/hi, day lo/hi, month, year lo/hi, century, weekday.
- **bsnes, higan:** 16 bytes. 8 bytes of registers, two BCD digits per byte (e.g. `30 02 00 02 68 99 05 00` = 00:02:30, day 2, month 8, '96, century 9, weekday 5), then an 8-byte little-endian Unix time.
- **snes9x, snes9x-2010, mednafen-bsnes:** 20 bytes. 16 bytes with one digit per byte, then a 4-byte little-endian Unix time. The three padding bytes after the weekday are `00` in snes9x and `FF` in mednafen-bsnes.
- **snes9x's clock** runs far too fast under retro-run, about 6 clock-seconds per frame: its save shows 11:55:40 where bsnes shows 0:02:29. snes9x-2010 keeps time (0:02:31).

**Chips, as far as these runs show:**
- **SA-1:** every core, snes9x-2002 included.
- **S-RTC:** bsnes, higan, snes9x, snes9x-2010 and mednafen-bsnes keep a clock. bsnes-hd-beta ticks but does not save it. Mesen2 does not tick. snes9x-2005 and 2005-plus have none. snes9x-2002 crashes on this 5 MB ExHiROM. bsnes-mercury and bsnes2014 cannot load it (e).
- **SPC7110 + RTC (Tengai Makyou Zero):**
  - On a blank SRAM the game runs Hudson's "SPC7110 CHECK PROGRAM" and needs A, `reset`, B, `reset`.
  - bsnes passes both modes and boots.
  - snes9x fails "RTC TIME NG" forever.
  - Mesen2 fails the Mode 2 RTC backup check; its `.rtc` there is 24 bytes (16 one-digit registers, then an 8-byte big-endian time).
  - Momotarou Dentetsu Happy (SPC7110 without RTC) passes the check program on snes9x.
- **128 KB LoROM SRAM:** see (d).
- **ST010, ST011, ST018, BS-X, Sufami Turbo:** see [Special chips](#special-chips).

## Special chips

A second pass over the chips the corpus lacked, every game tried in all 12 runnable cores.

| Chip | Game (script) | Save hardware | Save made |
| --- | --- | --- | --- |
| ST010 | F1-ROC II - Race of Champions (USA) (`F1-ROC II.txt`) | The ST010's own 4 KB data RAM, battery-backed; no cart SRAM (header SRAM size 0, type `F6`) | GRAND PRIX → PLAYER SELECT → slot 1 → name "ABC" → START. The player is written at once; PLAYER SELECT lists "1. ABC GROUP C". The player record lies in `$0810-$086F`. |
| ST011 | Hayazashi Nidan Morita Shougi (Japan) (`Hayazashi Nidan Morita Shougi.txt`, `.snes9x.txt`) | The ST011's 4 KB data RAM, as above | 入門教室 → あなたが先手, play 7六歩, resign, セーブ to slot 1 without a comment. The ロード list then shows "1 棋譜1 .入門". The game refuses to save a game with no moves. |
| ST018 | Hayazashi Nidan Morita Shougi 2 (Japan) | 8 KB cart SRAM (header `03`) | None: see (n). |
| BS-X | BS-X - Sore wa Namae o Nusumareta Machi no Monogatari (Japan) (Rev 1) (`BS-X.txt`) | 32 KB SRAM, plus 512 KB PSRAM and a memory pack slot | Registers "ああ", boy; with no satellite the game drops you in the town. A `reset` then goes straight to the town: the registration was read back. The name is Shift-JIS `82A0 82A0` at `$0006`, behind an `SG` header and a checksum, mirrored at `$3006`. |
| Sufami Turbo | SD Gundam Generation - Ichinen Sensouki (Japan), a mini-cart (`SD Gundam Generation - Ichinen Sensouki.txt`) | 8 KB SRAM in the mini-cart (`.st` header byte `$37` = 4) | Event mode → the STAGE 1 map → START → セーブ → YES. セーブ shows over the map for about a second. |

The library has the No-Intro Sufami Turbo set: 13 mini-carts. Six SD Gundam Generation carts have 8
KB of SRAM; SD Ultra Battle (Ultraman, Seven) and Poi Poi Ninja World have 2 KB; the other four
have none. SD Ultra Battle formats its SRAM on first boot (Aカセットのバックアップをしょきかしました),
and Poi Poi Ninja World's stage editor has a ファイル:セーブ that does nothing on an empty stage.
SD Gundam was the quickest real save.

### Games x cores

✔ filed, ✘ failed (reason below).

| core | F1-ROC II (ST010) | Morita Shougi (ST011) | Morita Shougi 2 (ST018) | BS-X | SD Gundam G., `.st` alone | SD Gundam G. + SD Ultra Battle, two slots |
| --- | --- | --- | --- | --- | --- | --- |
| snes9x | ✔ | ✔ (v) | ✘ hangs (o) | ✔ | ✔ 16384 (s) | ✔ two files (t) |
| snes9x-2010 | ✔ | ✔ (v) | ✘ hangs (o) | ✔ | ✘ refuses the `.st` | ✘ refuses its own subsystem (u) |
| snes9x-2005-plus | ✔ | ✔ (v) | ✘ hangs (o) | ✘ black screen, blank `.srm` | ✘ black screen | – no subsystem |
| snes9x-2005 | ✔ | ✔ (v) | ✘ hangs (o) | ✘ black screen, blank `.srm` | ✘ black screen | – no subsystem |
| snes9x-2002 | ✘ no ST010: skips to QUALIFY with garbled graphics, no save RAM | ✘ no ST011: the flow never reaches the save menu, and no save RAM | ✘ "TRANSMIT WAIT" | ✘ black screen, blank `.srm` | ✘ crashes (SIGBUS) | – no subsystem |
| bsnes | ✘ plays, writes no file (i) | ✘ plays and saves in game, writes no file (i) | ✘ (n) | ✔ `.srm` + `.psr` | ✘ black screen, writes a 256 KB `.srm` | – no Sufami subsystem (bsx and sgb only) |
| bsnes-hd-beta | ✘ plays, writes no file (i) | ✘ writes no file (i); ends in the same replay screen as the snes9x cores with this script, so its computer seems to resign at once too | ✘ black screen | ✔ `.srm` only | ✘ black screen, 256 KB `.srm` | – no Sufami subsystem |
| bsnes-mercury | ✔ | ✔ | ✘ (n) | ✘ refuses the cart on its own (w) | ✘ black screen, no file | ✘ refuses the subsystem (u) |
| bsnes2014 | ✔ | ✔ | ✘ (n) | ✘ refuses the cart on its own (w) | ✘ black screen, no file | ✘ refuses the subsystem (u) |
| higan-super-famicom | ✔ | ✔ | ✘ (n) | ✘ refuses the cart | ✘ black screen, 8 KB `.srm` | – no subsystems |
| mednafen-bsnes | ✘ plays, 0-byte `.srm` (x) | ✘ 0-byte `.srm` (x); neither script's flow fits | ✘ (n) | ✘ black screen, blank `.srm` | ✘ black screen, aborts | – no subsystems |
| mesen-s (Mesen2) | ✔ | ✔ | ✘ (n) | ✔ `BsxBios.srm` + `BsxBios.bs` (y) | ✔ 8192 | – no Sufami subsystem (sgb only) |

- **(i)** bsnes v115 and bsnes-hd-beta run the ST010 and ST011 from the firmware, and the games save in play (the player is listed, the 棋譜 is in the ロード list), but the cores write nothing: the chip's data RAM is not part of what they save. A real loss for a user of these cores.
- **(n)** Morita Shougi 2 plays in every core that runs the ST018 (bsnes, bsnes-mercury, bsnes2014, higan, mednafen-bsnes, Mesen2): the ARM answers moves. But セーブ never takes, in 入門教室 or 対局室, with or without a comment: the slot stays なし and the 8 KB SRAM stays all `FF` in bsnes and mednafen-bsnes. The same flow saves in Morita Shougi 1, so this looks like a common emulation gap (or a step the game needs that was not found), not the script. Note the sizes anyway: bsnes, bsnes-hd-beta, Mesen2 and mednafen-bsnes write 8192 bytes; bsnes-mercury, bsnes2014 and higan expose 16384 bytes of the ARM's RAM as save RAM instead; the snes9x cores write 4096.
- **(o)** snes9x's ST018 is not enough: the board comes up but there is no cursor and the game goes no further.
- **(v)** The snes9x cores emulate the ST011 at high level, and its computer resigns right after your first move (あなたの勝ちです). The game then offers the same menu, so `Hayazashi Nidan Morita Shougi.snes9x.txt` dismisses the result with B instead of resigning. Their saves hold one move; the firmware cores' hold two.
- **(s)** snes9x's `.srm` for a lone mini-cart is 16384 bytes: the 8 KB cart RAM, then 8 KB of `0x60`.
- **(t)** Through snes9x's "Multi-Cart Link" subsystem (Cart A = SD Gundam, Cart B = SD Ultra Battle), RetroArch-style naming gives one file per slot, each named after that slot's file: `SD Gundam Generation - Ichinen Sensouki (Japan).srm` (memory `0x300`) and `SD Ultra Battle - Ultraman Densetsu (Japan).srm` (`0x400`), 16384 bytes each. A's first 8 KB equal the lone-cart file byte for byte; the second half is `00` here, not `0x60`. B's file is all `00`: slot B is never booted. The subsystem needs both carts; with only Cart A, snes9x says "Multirom loading failed". Filed under the folder name `SD Gundam Generation - Ichinen Sensouki (Japan) + SD Ultra Battle - Ultraman Densetsu (Japan)`.
- **(u)** bsnes-mercury and bsnes2014 declare a "Sufami Turbo" subsystem (slots: Sufami A, Sufami B, Sufami BIOS; `.srm` for A and B, memory `0x300`/`0x400`) but refuse every load tried: A, (none), BIOS; A, B, BIOS; BIOS, A, B; with game type `0x1103`, `0x103` or `0x3`. snes9x-2010 declares "st" (two cart slots, no memory at all, so RetroArch would write no save even if it loaded) and refuses with one or two carts and every id tried.
- **(w)** bsnes-mercury and bsnes2014 load the BS-X cart only through their "BSX" subsystem with a memory pack (`.srm` + `.psrm`, named after the pack); not tried.
- **(x)** mednafen-bsnes writes a 0-byte `.srm` (and its usual 0-byte `.rtc`) for the ST010 and ST011 games, then aborts as usual.
- **(y)** Mesen2 names the BS-X saves after the BIOS, not the ROM: `BsxBios.srm` (32768) and `BsxBios.bs` (1048576, all `FF`: the empty memory pack).

Not runnable here, as before: snes-mister, agg23-snes and the other cores in the first table.

### What differs

**ST010 / ST011 data RAM (4096 bytes in every core that saved).** The game's record agrees everywhere (F1-ROC II's player in `$0810-$086F`). The rest is the chip's work area, `$0000-$00E1` in F1-ROC II, so files differ between cores: snes9x = snes9x-2010 byte for byte; snes9x-2005 and 2005-plus differ from them only in `$0000-$0015`, `$0040` and `$00C0-$00E1`; bsnes-mercury, bsnes2014, higan and Mesen2 differ in `$0000-$00E1` a little more. Untouched data RAM (`$0D00-$0FFF` in F1-ROC II, `$0700-$0FFF` in Morita) is `00` in every core except Mesen2, where it is random, as its other RAM is. Morita: the four snes9x cores' files are identical (sha1 `ea79601d…`); the firmware cores differ in the 棋譜 itself (the computer's answer varies, 8四歩 or 3四歩) and at `$0180-$0649`.

**BS-X SRAM (32768).** `$0000-$5FFF` is the same in every core (the game formats it at boot); `$6000-$7FFF` is never touched and shows each core's fill: `FF` in bsnes and bsnes-hd-beta, `60` in snes9x and snes9x-2010, random in Mesen2. bsnes adds `<stem>.psr`, the 512 KB PSRAM, all `FF`; bsnes-hd-beta does not. bsnes and bsnes-hd-beta `.srm` are identical, as are snes9x and snes9x-2010.

**Sufami Turbo.** Names follow how the cart was loaded: a lone `.st` gives `<mini-cart stem>.srm`; a two-slot subsystem gives one file per slot named after each mini-cart; nothing is named after the base cart. Sizes: 8192 in Mesen2 (the cart's size), 16384 in snes9x (both ways). snes9x and Mesen2 differ in 18 bytes of the save itself (`$0032-$1A5B`).

**Cores that write their own files.** bsnes v115 and Mesen2 report 0 bytes of save RAM to the frontend (`retro_get_memory_size`), so a frontend's own save code writes nothing for them, and retro-run's `dump` cannot read it; they write `<stem>.srm` (and bsnes `.psr`, Mesen2 `BsxBios.*`) into the save directory themselves. That is why Mesen2's BS-X names ignore the ROM.

### Scripts and the MiSTer replay

- `F1-ROC II.txt`, `BS-X.txt`, `SD Gundam Generation - Ichinen Sensouki.txt` and `Hayazashi Nidan Morita Shougi.txt` are for every core; use `Hayazashi Nidan Morita Shougi.snes9x.txt` only where the computer resigns at once after the first move (v). The firmware flow resigns by hand after the computer's answer.
- Waits are generous; Morita's menus drop presses shorter than about 15 frames, so its presses are long. `BS-X.txt` ends with a `reset`.
- SD Gundam's title is up only from about frame 1200 to 1500 after power-on before the attract mode starts; the script presses START at 1350. A slower boot needs that wait adjusted.
- The two-slot entry was made with `make-save.py --subsystem multicart_addon --slot FILE` (below); a lone mini-cart needs only the usual `make-save.py` with the `.st` as ROM.

### Not done

- **SuperFX (Yoshi's Island).** A new file writes nothing to the save area (`$7C00-$7E7F` of the 32 KB is unchanged after starting file 1); the game saves when 1-1 is cleared. 1-1 was played by segments in snes9x: past the first Shy Guys (a jump at frame 44), over the first slanted block (B held 50 at the wall), and over the pillar beyond it by jumping from the top of that block (right 6, then right+B 70, release, right+B 40). That lands on a row of blocks before a wall taller than a flutter; holding right on the blocks does not move Yoshi, and no way on was found in a few tries. Stunt Race FX and Winter Gold: as in the first pass.
- **SPC7110 (Tengai Makyou Zero).** In bsnes the check-program dance, the birthday entry (the defaults, 1995-12-22) and about 26000 frames of prologue (A every 50 frames) reach Higan's village. The field menu (X) has まきもの, もちもの, そうび, つよさ, さくせん, せってい, こよみ, とけい; no save, and the clock reads 1995年12月22日 12:08. Saving is probably at a temple; none was found by walking north.
- **S-DD1 (Star Ocean).** New Game → name entry (おわり at once keeps ラティクス) → about 13000 frames of opening (A every 60 frames) → Ratix's house in Kratus. The menu (X) has セーブ, but it does nothing in town; saving needs the world map or a save point, and leaving the house was not managed.
- **OBC1 (Metal Combat).** Boots to the title in bsnes and snes9x, but the game is Super Scope only and retro-run has no light gun device.
- **ST018 (Morita Shougi 2):** no save takes anywhere, see (n).

### Harness notes for this pass

- **Subsystems.** Sufami Turbo with two carts (and BS-X with a memory pack) need `retro_load_game_special`. `retro-run --subsystem IDENT --slot FILE` (repeatable, `-` for an empty slot; `--list-subsystems` prints what a core offers) loads them that way and names each slot's saves after that slot's file, as RetroArch does; `make-save.py` passes the same options through.
- **`dump` and cores that save by themselves:** see "Cores that write their own files" above.
- **Morita Shougi's AI** is not deterministic across runs (the reply to 7六歩 varied), so its files differ between runs of one core.

## Gaps and attempts

**Not done** (the special-chip pass adds to this list; see [Special chips](#special-chips))
- **SuperFX: no entry.**
  - *Yoshi's Island:* the run gets past the first pillar of 1-1, then hits a taller wall. The second pass got further; see below.
  - *Stunt Race FX:* Speed Trax Easy Ride is reachable, but blind throttle patterns either crash or finish too slowly. bsnes and snes9x also drift apart from the same inputs (GSU timing).
  - *Winter Gold:* the menu won't accept a selection in snes9x.
  - Note that the GSU RAM is work RAM, so snes9x writes 32 KB for Yoshi's Island and 64 KB for Stunt Race FX.
- **Tengai Makyou Zero:** boots in bsnes (script start in `work/snes/dev/tmA-boot.txt`), but no save point was found in the first village.
- **Tenth game:**
  - *Super Mario Kart* (DSP-1, 2 KB): boots in bsnes with the firmware, but a blind 5-lap time trial was too slow to develop.
  - *Harvest Moon:* the OK in name entry could not be reached.
  - *EarthBound:* the home phone only says "Beeeep...".
  - *Kirby's Dream Land 3:* a new file is not written until a stage is cleared.
  - *Ultima Runes of Virtue II* and *FF Mystic Quest:* long openings.

**Leads**

Downloaded, inspected, not filed (not clearly attributable):
- **SNES_MiSTer issues:**
  - [#54](https://github.com/MiSTer-devel/SNES_MiSTer/issues/54): Secret of Mana northtown save; the poster also refers to original hardware.
  - [#53](https://github.com/MiSTer-devel/SNES_MiSTer/issues/53): Super Mario RPG, 32 KB, origin not stated.
  - [#138](https://github.com/MiSTer-devel/SNES_MiSTer/issues/138): `tmz_english_beginning.sav`; the poster compares bsnes and MiSTer.
  - [#59](https://github.com/MiSTer-devel/SNES_MiSTer/issues/59): Marvelous 1.07 translation, 65536 bytes, a patched ROM.
  - [#313](https://github.com/MiSTer-devel/SNES_MiSTer/issues/313): `SOE.sav` in the issue body, renamed.
  - [#72](https://github.com/MiSTer-devel/SNES_MiSTer/issues/72): a 100% Yoshi's Island `.srm`, from an emulator.
  - [#364](https://github.com/MiSTer-devel/SNES_MiSTer/issues/364): Trials of Mana, taken from fantasyanime.com.
- **openfpga-SNES:** [#43](https://github.com/agg23/openfpga-SNES/issues/43) `Saves.zip` holds 8 KB starter saves for the SPC7110 games, which the Pocket core needs to get past its check. Their origin is not stated.

Not found: anything attributable to standalone Mednafen, Supafaust, bsnes-jg, ChimeraSNES, higan balanced or the Pro Action Replay core. What was searched:
- **GitHub:** issue and comment text of agg23/openfpga-SNES and MiSTer-devel/SNES_MiSTer, all of it pulled through `gh api`.
- **Web:** searches for the cores' save attachments.

Two facts from that search:
- **MiSTer SPC7110 clock:** reads the host's real time ([#139](https://github.com/MiSTer-devel/SNES_MiSTer/issues/139)).
- **MiSTer fill bug:** early-2020 builds filled only every other byte of fresh SRAM with `FF` ([#189](https://github.com/MiSTer-devel/SNES_MiSTer/issues/189)). The downloaded Illusion of Gaia save shows exactly that `FF 00` pattern.

## Downloaded entries

| core | game | files | what |
| --- | --- | --- | --- |
| agg23-snes | Chrono Trigger (USA) | `... - Reboot1.sav`, `... - Reboot2.sav` (8192, identical), `... - End.sav` (65536) | From [openfpga-SNES #2](https://github.com/agg23/openfpga-SNES/issues/2). End is the corrupt 64 KB file the Pocket left after "Load SMC" (firmware bug). |
| agg23-snes | Donkey Kong Country (USA) (Rev 2) | Reboot1/Reboot2 (2048, identical), End (8192) | Same thread. The Doom "save" in the zip is byte-identical to the DKC one, so it is not filed. |
| snes-mister | Chrono Trigger (USA) | `Chrono Trigger (U) [!].sav` 8192 | Issue #38. |
| snes-mister | Illusion of Gaia (USA) | `.sav` 8192 | Issue #183. Has the `FF 00` fill. |
| snes-mister | Secret of Mana (USA) | `.sav` 8192 | Issue #202. |
| snes-mister | Secret of Evermore (USA) | `.sav` 8192 | Issue #313. |
| snes-mister | Super Mario RPG - Legend of the Seven Stars (USA) | `.sav` 32768 | Issue #39. MiSTer sized BW-RAM from the header (32 KB). |
| snes-mister | Shinseiki Odysselya (Japan) | `.sav` 8192 | Issue #258. |

## Harness and runner notes

- **Aborting cores:** make-save.py treats any non-zero exit as failure, even when the core wrote its saves before aborting (mednafen-bsnes). Workaround: `work/snes/file_aborted.py`.
- **Re-pressing a button:** two `press` lines back to back do not release the button in between, so a second press of the same button needs a gap or another command.
- **Disk:** the disk was full (about 130 MB free) during this run. This slice's scratch was deleted to make room.

## GameFAQs saves

The GameFAQs pass (2026-11-05, `tools/GAMEFAQS.md`) found 8 SNES saves, all in "Wii VC Game Save
File" sections. A ninth file, posted in the Wii VC section of the TurboGrafx-CD Ys III page, turned
out to be this system's: the SNES Ys III's SRAM.

| Id | Filed as | Release | What it is |
| --- | --- | --- | --- |
| 22056, 21934, 21935, 21936, 21937 | `_wii-vc` | Chrono Trigger (USA) | `data.bin`, title `JECE`, `savedata.bin` 8192 |
| 24072 | `_wii-vc` | Kirby's Fun Pak (Europe) | `data.bin`, `JCCP`, `savedata.bin` 8192 |
| 22019 | `_wii-vc` | Super Mario RPG - Legend of the Seven Stars (USA, Europe) (Virtual Console) | `data.bin`, `JCBM` (the European VC release is the US game), `savedata.bin` **32768** |
| 35117 | `_wii-vc` | Super Metroid (Japan, USA) (En,Ja) | `data.bin`, `JAVE`, `savedata.bin` 8192, plus `nocopy/dummy` (348032 bytes, the VC's own data) |
| 26177 | `_unknown` | Ys III - Wanderers from Ys (USA) | a raw 8 KiB SRAM, no container: "Wanderes from Ys (Ys-3) Programed by N.Fujisawa 91-04-24" at 0x20 is in the SNES ROM, not on the TurboGrafx-CD disc |

**Conversion.** `tools/gamefaqs/wiivc-convert.py` decrypts the `data.bin`: the header is
AES-128-CBC with the SD key, and every header MD5 checks. It takes `savedata.bin`, which is the
cartridge SRAM byte for byte (vcromclaim: "VC SNES saves are standard SRM files"). The Ys III file
needed nothing. Each was loaded both ways:
- as `<ROM stem>.srm` in the save folder, for cores that read their own file (mednafen-bsnes);
- with `--srm`, into the core's save RAM.

Bytes worth knowing:
- Super Metroid's `savedata.bin` has 3271 bytes of `60`, the same value snes9x fills fresh SRAM
  with.
- Super Mario RPG's VC SRAM is 32 KiB, as MiSTer's file is (see Downloaded entries).
- one-saves has no Wii `data.bin` reader.

**Saves x cores: every save loads in all 16 runnable cores.**
- The cores: snes9x, snes9x-2010, snes9x-2005-plus, snes9x-2005, snes9x-2002, bsnes, bsnes-hd-beta,
  bsnes-mercury, bsnes2014, higan-super-famicom, mednafen-bsnes, mesen-s, beetle-supafaust,
  bsnes-jg, chimerasnes, higan-super-famicom-balanced.
- The totals: 144 loads, 0 rejected, 0 core errors, 0 not run. Each core also had a baseline with
  no save.
- Two cores end the same way every time, after all frames have run: mednafen-bsnes aborts
  (SIGABRT) at unload and higan-super-famicom-balanced traps (SIGTRAP) in `retro_deinit`. Both are
  noted above and in BUILT-CORES.md, and both had already drawn every frame.

| Save | What every core shows |
| --- | --- |
| 22056 | load screen: slot 1 "The Final Battle", End of Time, 11:30, LV 99s |
| 21934-21937 | three slots each, named for the endings' save points ("The Final Battle", "We're Back!", "Tata and the Frog", "Forward to the Past" ...), with time, gold and save count |
| 24072 | Kirby 1 at 100% |
| 22019 | MARIO1 LV25 Mario's Pad, MARIO2 LV23 Factory, MARIO3 LV15 Monstro Town |
| 35117 | SAMUS A 02:13, B 09:49, C 02:09 |
| 26177 | LOAD MENU slot "ENTRANCE TO REDMONT"; loaded: Adol at 255/255 HP, 65535 EXP, 61597 gold |

Load scripts: `scripts/snes/<game>.load.txt`. Chrono Trigger with a save goes from the title
straight to its load screen; with no save, Start begins a new game. Kirby's Fun Pak's title is up
only from about frame 800 to 1050.
