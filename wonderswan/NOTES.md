# WonderSwan: notes

## The eight games

Save hardware comes from the cartridge footer (byte 5 of the last 10 ROM bytes; table in
`work/wonderswan/footers.txt`, made by `work/wonderswan/footers.py`). The games were picked for
save hardware first (128-byte EEPROM, 2 KiB EEPROM, 8 KiB and 32 KiB SRAM), then a quick save
that a reset can show. All are Japanese except Digimon (Hong Kong, English). Few WonderSwan
games were released anywhere else.

| Game (ROM) | Save hardware | How the script reaches a save | Proof |
| --- | --- | --- | --- |
| Puzzle Bobble (Japan) | EEPROM 128 B | 1人で遊ぼうかな, fire straight up until round 1 is lost; reset, 過去をふりかえる > 1人で遊ぼうかな | これまでの結果: ラウンド 1, スコア 420 |
| GunPey (Japan) | EEPROM 2 KiB | 1 PLAYER > ENDLESS with no input until game over (random panels still score 1200) | RESULT and the BEST SCORE table |
| Final Lap 2000 (Japan) | EEPROM 2 KiB | OPTION: HANDLING QUICK, TRANSMISSION AT, EXIT; reset, OPTION | the two settings read back |
| Tekken Card Challenge (Japan) | SRAM 8 KiB | アドベンチャー, JIN, into STAGE 01 (the game saves when the adventure starts); reset, アドベンチャー | CHARACTER SELECT "JIN Lv 1 STAGE01" |
| Nobunaga no Yabou for WonderSwan (Japan) | SRAM 32 KiB | 1 PLAY, NEW GAME, scenario 1 (1560), 武田, START > セーブ > slot 1 > はい; reset, 1 PLAY | slot list "1. 1560" |
| Digimon - Ver. WonderSwan (Hong Kong) (En) | SRAM 32 KiB | REBOOT (new pet), SYSTEM > SAVE&EXIT | back at the title after saving (264 bytes change; the proof only shows the title) |
| Wonder Stadium (Japan) | SRAM 8 KiB | とことん育成 > チームエディット > チーム作成 > はい, team type 打撃重視, take every player 選手発掘 offers; reset, チーム編成 | the new roster (おりけけ, おりんじ, ...) instead of the default (オリオク, オリオ, ...) |
| Wonder Stadium '99 (Japan) | SRAM 8 KiB | the same script as Wonder Stadium | the new roster (おりべろ, おりえこ, ...); a boot shows the default オリオク, ... |

Tried and dropped (each fought for more than a few attempts, or the save was out of reach):
Goraku Ou Tango! (long story opening before any save), Taikyoku Igo - Heisei Kiin (Beetle
shows only a white screen, although the game formats its SRAM), Chocobo no Fushigi na Dungeon
(long opening), Robot Works (program edits are not written to SRAM), Kaze no Klonoa (long story
opening), Rockman & Forte (OPTION is not saved; CONTINUE needs a cleared stage), Medarot Perfect
Edition (no save menu found after naming), Engacho! (the OPTION change is not written),
MobileWonderGate (needs the mobile adapter), Tenori-on (see "WonderWitch carts" below), Dokodemo
Hamster (the d-pad does not move the name-entry cursor, so the name is never confirmed),
Sangokushi for WonderSwan (same menus as Nobunaga up to the first turn, but START did not open
the save menu there), Langrisser Millennium WS (stays on PUSH START). Looked at
only: Makaimura, Lode Runner, Hunter X Hunter - Ishi o Tsugu Mono, Super Robot Taisen Compact,
Digital Partner, Langrisser Millennium WS.

## Games x cores

8 of 8 filed for beetle-wonderswan (Beetle WonderSwan v0.9.35.1 4b01295, retro-run). Every proof.png
was checked. Each entry is one `<ROM stem>.srm`.

| Game | beetle-wonderswan | non-zero bytes |
| --- | --- | --- |
| Puzzle Bobble | 128 | 3 |
| GunPey | 2048 | 5 |
| Final Lap 2000 | 2048 | 4 |
| Tekken Card Challenge | 8192 | 404 |
| Nobunaga no Yabou | 32768 | 3509 |
| Digimon - Ver. WonderSwan | 32768 | 1666 |
| Wonder Stadium | 8192 | 361 |
| Wonder Stadium '99 | 8192 | 353 |

Not runnable here, nothing played: wonderswan-mister (MiSTer), agg23-wonderswan (openFPGA),
mednafen (standalone). Downloaded files for MiSTer and Mednafen are described below.

## Beetle's save file

From the core source (`work/wonderswan/src/`, libretro.c:601-611, :1721-1757, wswan-memory.c:461-497):

- **Contents.** `.srm` is the cartridge save only: the EEPROM if the footer declares one,
  otherwise the SRAM. The size is exactly what the footer says: 0x01 8 KiB, 0x02 32 KiB,
  0x03 128 KiB, 0x04 256 KiB, 0x05 512 KiB SRAM; 0x10 128 B, 0x20 2 KiB, 0x50 1 KiB EEPROM.
  There is no padding and no header or trailer.
- **Fill.** EEPROM and SRAM both start as 0x00 (eeprom.c:214, wswan-memory.c:497). An erased
  serial EEPROM reads 0xFF on hardware and on MiSTer (see below). Puzzle Bobble, Final Lap 2000
  and Engacho! leave a Beetle EEPROM all zero until they write it.
- **Same layout as Mednafen.** Standalone Mednafen writes its `.sav` as EEPROM then SRAM, raw.
  No cart has both, so a Beetle `.srm` and a Mednafen `.sav` hold the same bytes; only the name
  differs (`<ROM>.<md5>.sav`).
- **Not saved:** the console's internal EEPROM (owner name, birthday, sex, blood type). The core
  rebuilds it from core options at every start. Tekken Card Challenge shows it as NAME PLAYER,
  BIRTHDAY 19890623, FEMALE, blood O. The cart RTC is not saved either: rtc.c:186 reads the
  host's `localtime()` at power-on.
- **WonderWitch carts.** A 512 KiB ROM with the WonderWitch "ELISA" font and footer checksum is
  treated as WonderWitch. Its `.srm` is then the SRAM followed by the whole 512 KiB flash, which
  is the ROM image (wswan-memory.c:484-492). Tenori-on's `.srm` is 786432 bytes (256 KiB +
  512 KiB). It was not filed because it would carry the ROM. Mednafen standalone writes the
  flash to a separate `.flash` file.

Input: in the core's default keymap the d-pad drives the X pad and `l`/`r`/`l2`/`r2` drive the
Y pad. Portrait games use the Y pad for movement (`l` moves down, `r` moves up). Some of them
also use the X pad as buttons: in GunPey EX and Tetris (WSC), `down` (X3) confirms and `left`
(X4) goes back. Several menus drop the first press, and Nobunaga needs 12-frame holds.

## Downloaded entries and leads

Filed by the search agent from downloads. These are not runs of ours:

- `wonderswan-mister/Rockman & Forte - Mirai Kara no Chousensha (Japan)/`, from
  https://github.com/MiSTer-devel/WonderSwan_MiSTer/issues/10. RobertPeip, the core's author,
  posted it as "what is saved back from Mister". It keeps its GoodWSx name
  `Rockman & Forte - Mirai Kara no Chousen Sha (J) [M][!].sav`. 33280 bytes = 32 KiB SRAM +
  the 512-byte clock sector.
- `mednafen@openemu/Rockman & Forte - Mirai Kara no Chousensha (Japan)/` is the original from the
  same issue: 32768 bytes of raw SRAM named `<ROM>.523004d48e9d606e1557c2c57af6790b.sav` (that
  hash is the No-Intro ROM's MD5). The author called it "mednafen, the default for OpenEmu", and
  standalone Mednafen writes the same name and bytes. Caveat: the zip's AppleDouble entry shows
  this copy passed through his savefileconverter dev server (localhost:8080).
- birdybro's MiSTer saves.zip, from https://github.com/euan-forrester/save-file-converter/issues/80,
  written 2021-06-05 and probably only booted: `wonderswan-mister/` Puzzle Bobble 2560 (the
  128 B EEPROM, all 0xFF, zero-padded to 2048, + 512), Kaze no Klonoa 8704, Tekken Card
  Challenge 8704, Taikyoku Igo 131584, Tenori-on 262656, MobileWonderGate (Rev 1) 524800.
- Every MiSTer file ends in 512 bytes: one 16-byte record repeated 32 times, `54 52` ("RT"
  LE), 10 bytes of time (42-bit saved RTC + 32-bit Unix time), then 4 zero bytes. It is there
  even for carts without an RTC.

Save formats from source (search agent):

- wonderswan-mister (WonderSwan.sv @64d055a5) always appends the clock sector (has_rtc = 1'b1,
  :970; :1097, :1106, :1110). EEPROM saves are always 4 blocks, i.e. 2048 bytes (:993-995). A
  mounted save whose size is not a power of two gets size/512 - 2 blocks (:1003).
- agg23-wonderswan (@073213a2) uses `.sav` slot id 11 in data.json. The EEPROM is always 2048
  bytes (wonderswan.sv:635-637). The slot size is save + 12 (core_top.v:694), and the 12 bytes
  are the first 12 of the MiSTer record (:681-683). No files were found.
- mednafen names files `%f.%M%x`. The WonderSwan `.sav` is cart EEPROM then SRAM, raw
  (wswan/memory.cpp:717-735). The internal EEPROM is rebuilt from settings and never saved
  (:767-768). WonderWitch carts get a 512 KiB `.flash`.

Leads, not filed: `.cache/downloads/wonderswan/birdybro-mister-saves/` holds about 68 more
MiSTer WonderSwan saves. An archive.org MAME 0.288 Judgement Silversword save
("judgement-silversword-savefile") and a RetroArch .srm for SD Gundam Operation U.C. were not
downloaded. Searched with nothing found: every agg23 and WonderSwan_MiSTer issue (agg23 #3
describes EEPROM .sav files but attaches none), beetle-wswan issues, OpenEmu issues,
archive.org, misterfpga.org, Reddit.

## Beetle vs MiSTer, where the games overlap

Compared against our filed files, and for the other games against a Beetle power-on dump
(1200 frames, not filed). The "MiSTer body" is the file minus its 512-byte trailer.

| Game | MiSTer | Beetle | MiSTer body vs Beetle |
| --- | --- | --- | --- |
| Puzzle Bobble (EEPROM 128 B) | 2560 | 128 (filed) | first 128 bytes all 0xFF on MiSTer (never written), all 0x00 on a Beetle boot; the rest of MiSTer's 2048 is 0x00 padding |
| Tekken Card Challenge (SRAM 8 KiB) | 8704 | 8192 (filed) | 1869 bytes differ (different progress and owner profile) |
| Rockman & Forte (SRAM 32 KiB) | 33280 | 32768 (boot) | MiSTer vs Mednafen: 2 bytes (0x8A1, 0x8A5). Beetle title-screen boot vs Mednafen: 317 bytes |
| Kaze no Klonoa (SRAM 8 KiB) | 8704 | 8192 (boot) | 2466 bytes (MiSTer went further than the title) |
| Taikyoku Igo (SRAM 128 KiB) | 131584 | 131072 (boot) | 11828 bytes (Beetle stays on a white screen) |
| MobileWonderGate (SRAM 512 KiB) | 524800 | 524288 (boot) | 61 bytes |
| Tenori-on (SRAM 256 KiB, WonderWitch) | 262656 | 786432 (boot) | MiSTer saves only the SRAM; Beetle adds the 512 KiB flash |

To go from Beetle to MiSTer: append the 512-byte trailer, and pad an EEPROM save to 2048
bytes first. To go back: drop the last 512 bytes, and for a 128-byte or 1 KiB EEPROM keep only
the first 128 or 1024 bytes. Our MiSTer samples are all-0xFF EEPROM where the game never
wrote, and Beetle files are all-0x00 there. A game that checks for a blank EEPROM may treat the
two differently.
