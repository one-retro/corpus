# Virtual Boy: notes

**No entries filed.** Beetle VB runs every game in the library and writes a save file for all
of them. But none of the scripts I tried in the time I had reached a genuine save: a
game-initiated write after play, as opposed to the format write a game does on first boot. This
file records what the library has, what Beetle writes, and what was tried, so a later pass can
start from it.

## Which games keep a save

There is no save flag in the VB ROM header, so this was measured. Each of the 22 games was booted
for about 2,000 frames with a few Start/A presses (`work/virtualboy/probe.txt`), and the
non-zero bytes of the `.srm` counted. Six games write their save memory on first boot, which
shows they have a battery save:

| Game (No-Intro) | Written on first boot | What it is |
| --- | --- | --- |
| 3-D Tetris (USA) | 1323 bytes, even addresses only, up to 0xCD0 | header `T&E SOFT`, then the high-score tables |
| Galactic Pinball (Japan, USA) (En) | 1824 bytes, even addresses only, up to 0x3FFE | the default high-score tables (8 KiB of cart RAM) |
| Golf (USA) | 16 bytes, even addresses | header `T&E VR GOLF p12` |
| Teleroboxer (Japan, USA) (En) | 240 bytes of 0xFF at 0x00-0xEF, **both even and odd addresses** | a cleared progress area |
| Virtual Boy Wario Land (Japan, USA) (En) | 216 bytes of 0xFF at 0x00-0xE7, both even and odd | a cleared progress area |
| Virtual Fishing (Japan) | 2004 bytes, even addresses only, up to 0x1BF6 | header `VFISHJPN`, then tables |

The other 16 wrote nothing in the probe. That is not proof they have no save:
- Nester's Funky Bowling, Virtual Bowling, SD Gundam - Dimension War and Space Invaders - Virtual
  Collection are reported to save, but only after play.
- Mario Clash, Mario's Tennis, Red Alarm, Panic Bomber, Vertical Force, Waterworld, Jack Bros. and
  Insmouth no Yakata are commonly listed as having no save.

## What was tried (and why nothing was filed)

- **Golf (USA).** This went furthest. A new player "A" is registered (MAIN MENU > Stroke Play >
  NEW PLAYER > name > END), and holes are played by mashing A. The game announces "New record!
  Your long-putt has improved to 20 feet" after hole 1, yet the save memory stays at the 16-byte
  header:
  - through three holes;
  - after QUIT, which only shows a password (484818), although the player list in RAM then
    lists A;
  - after changing OPTIONS (Auto Pause, Music).

  Records are apparently written only at the end of an 18-hole round. Mashing A plays very
  short shots, and the run reached Automatic Pause (every 30 minutes of game time) first. The
  menu sequence that works is in `work/virtualboy/golf.txt` and `golf4.txt`.
- **Nester's Funky Bowling:** a full 1-player game is reached and played by mashing A
  (`work/virtualboy/nfb.txt`, `nfb2.txt`: Start, Start, A, A, Start, Start, A; the name entry is
  left blank). It ends on FINAL SCORE 39, then LEAGUE LEADERS, whose default table runs 263 to
  144. At 39 the score does not make the table, and the save memory stays all zero. A score
  above 144 would need aimed throws.
- **Space Invaders - Virtual Collection:** the script never got past PUSH START BUTTON. Start
  was not taken at the times tried, so the timing needs work.
- **Galactic Pinball:** the ball was never launched (the plunger control was not found).

## What Beetle VB writes (from source and the probe files)

Beetle VB v1.31.0 d5ae54c, `mednafen_vb_libretro.dylib`. Source: libretro/beetle-vb-libretro
d5ae54c, libretro.cpp.

- **`<ROM stem>.srm` of exactly 65536 bytes for every game.** It is the core's `GPRAM`:
  - `GPRAM_Mask = 0xFFFF` at :551; zero-filled at :566;
  - mapped at 0x06000000 and mirrored every 64 KiB through 0x06FFFFFF (:555);
  - exposed as `RETRO_MEMORY_SAVE_RAM` (:1475, :1490).

  The size does not depend on the cartridge: a game without a save also gets 64 KiB of zeros.
  make-save flags such a file as blank and does not file it.
- **Fill byte 0x00.** It does not mean "erased".
- **Real cartridge RAM is 8 bits wide on the 16-bit bus.** The games put their data in the even
  bytes: 3-D Tetris's header reads `54 00 26 00 45 00 ...` = "T&E". Beetle stores the bus as
  plain bytes, so:
  - byte stores leave the odd bytes 0x00;
  - **16-bit stores also land in the odd bytes.** Teleroboxer and Wario Land clear their area
    with 0xFFFF halfwords, and Beetle keeps 0xFF in both halves. On a real cart the high byte
    would be lost.

  For one-saves, these differences matter:
  - a real-cartridge dump or another emulator's file may be 8 KiB of data bytes only, with no
    interleaving;
  - Beetle's file is 64 KiB, interleaved, and holds data bytes only up to 2 x the cart's RAM
    size;
  - the odd bytes can carry junk from halfword stores.

  Converting means taking the even bytes of the first 16 KiB (for an 8 KiB cart).
- **Other files:** none. There is no `.rtc` (the VB has no clock), and nothing in the system
  directory.

## Games x cores

| Game | beetle-vb | mednafen |
| --- | --- | --- |
| (all 22) | runs; no genuine save reached, nothing filed | not runnable (standalone, GUI) |

## Downloaded entries and leads

Nothing found. Standalone Mednafen writes `<stem>.<md5>.sav`, always 65536 bytes (the same
GPRAM), and only when the RAM is not all zero (mednafen vb.cpp:641, 757-768, per the search
done for this corpus). No Virtual Boy save attributable to Mednafen or any core turned up on
GitHub, Planet Virtual Boy or archive.org.
