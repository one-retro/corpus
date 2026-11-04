# WonderSwan Color: notes

Same core and same save format as the mono WonderSwan. See `../wonderswan/NOTES.md` for how
Beetle builds its `.srm`, the input map, and the MiSTer, agg23 and Mednafen formats.

## The six games

Picked to cover the WSC save types: 32 KiB SRAM, 32 KiB SRAM on an RTC cart, 128-byte EEPROM
and 2 KiB EEPROM. All six are Japanese. The WSC library is almost all Japanese.

| Game (ROM) | Save hardware (footer) | How the script reaches a save | Proof |
| --- | --- | --- | --- |
| Makai Toushi Sa-Ga (Japan) | SRAM 32 KiB | はじめから, first character, name ああ..., in town START > セーブ > file 1 > はい; reset, つづき | load list: file 1 "ああ HP 60" |
| Dokodemo Hamster 3 - Odekake Saffron (Japan) (Rev 2) | SRAM 32 KiB + RTC | はじめから and the setup: owner name, birthday, blood type, date and time, hamster name. The game saves when the hamster reaches its room. Reset, つづきから | the hamster's room |
| Tetris (Japan) | EEPROM 128 B | OPTION: NEXT PIECE OFF, GHOST PIECE OFF, EXIT; reset, OPTION | both settings read back |
| Final Lap Special - GT & Formula Machine (Japan) | EEPROM 2 KiB | EXTRA GAME > GAME 1, hold A to the end (high score 723 m); reset, EXTRA GAME | "GAME 1 HIGH SCORE 00723M" |
| Kinnikuman II-Sei - Dream Tag Match (Japan) | EEPROM 128 B | オプション > オートセーブ: ON -> OFF; reset, オプション | オートセーブ with OFF selected |
| Romancing Sa-Ga (Japan) | SRAM 32 KiB | NEW GAME, Albert, name アルベルトあ; during the opening Y2 (`r`) opens the menu: セーブ > セーブ1 > はい; reset, LOAD (the cursor starts on LOAD when a save exists) | セーブ1: アルベルトあ 60/60, イスマス |

Tried and dropped: Final Fantasy (on the party screen, names were not reached quickly), GunPey EX
(an ENDLESS game with no input scores 0 and RECORDS stays as at boot), Golden Axe (menu
navigation went into ARCADE instead of OPTION), Another Heaven (text adventure, no save
reached), Dicing Knight. (no save point reached quickly), Star Hearts (SRAM 8 KiB; the hero is
named and the game starts, but no save menu was found), Gekitou! Crash Gear Turbo (SRAM 8 KiB;
the title menu cursor did not move off プロローグ, and the prologue runs into a battle and the
story), Mr. Driller (no button gets past Press Start), Wizardry Scenario 1 (forming a party
writes the roster, but nothing shows after a reset; the Training Grounds were not tried).
Looked at and set aside for long openings: SD Gundam G Generation - Gather Beat 2, Gensou Maden
Saiyuuki Retribution, Kidou Senshi Gundam Vol. 1, Super Robot Taisen Compact for WonderSwan
Color, Guilty Gear Petit 2, Final Fantasy II, Alchemist Marie & Elie, Tonpuusou (it opens
straight into a hand). Looked at only: Digimon Tamers - Battle Spirit. Dicing Knight. and Digimon Tamers -
Battle Spirit are `.wsc` files whose footer has the colour flag clear.

## Games x cores

6 of 6 filed for beetle-wonderswan (Beetle WonderSwan v0.9.35.1 4b01295, retro-run). Every
proof.png was checked. Each entry is one `<ROM stem>.srm`.

| Game | beetle-wonderswan | non-zero bytes |
| --- | --- | --- |
| Makai Toushi Sa-Ga | 32768 | 10078 |
| Dokodemo Hamster 3 | 32768 | 780 |
| Tetris | 128 | 49 (all zero before OPTION > EXIT) |
| Final Lap Special | 2048 | 8 |
| Kinnikuman II-Sei - Dream Tag Match | 128 | 32 (34 at boot) |
| Romancing Sa-Ga | 32768 | 13928 |

Not runnable here, nothing played: wonderswan-mister, agg23-wonderswan, mednafen.

**RTC.** Hamster 3 asks for the date and time, but the room clock then showed the host's time
(23:51), not the 0:00 entered. Beetle reads the cart clock from the host's `localtime()` at
power-on and does not save it. Re-running the script at another time of day may write
different SRAM bytes.

## Downloaded entries and leads

Filed by the search agent from birdybro's MiSTer saves.zip
(https://github.com/euan-forrester/save-file-converter/issues/80, written 2021-06-05,
probably only booted). These are not runs of ours:

- `wonderswan-mister/Another Heaven - Memory of those Days (Japan)/`: 2560 bytes (2 KiB
  EEPROM + 512).
- `wonderswan-mister/Final Fantasy (Japan)/`: 33280 bytes (32 KiB SRAM + 512).
- `wonderswan-mister/Dicing Knight. (Japan)/`: 262656 bytes (256 KiB SRAM + 512).

Each ends in the MiSTer clock sector: 32 copies of a 16-byte record `54 52` + 10 bytes of time +
4 zero bytes. Leads (MAME Judgement Silversword save, more MiSTer files in
`.cache/downloads/wonderswan/birdybro-mister-saves/`) and the searches with nothing found are
listed in `../wonderswan/NOTES.md`.

## Beetle vs MiSTer, where the games overlap

None of our six games is among the MiSTer downloads. These rows compare against a Beetle
power-on dump (1200 frames, not filed). The "MiSTer body" is the file minus its 512-byte trailer.

| Game | MiSTer | Beetle (boot) | MiSTer body vs Beetle |
| --- | --- | --- | --- |
| Another Heaven (EEPROM 2 KiB) | 2560 | 2048 | 8 bytes differ; both are near-empty boot states |
| Final Fantasy (SRAM 32 KiB) | 33280 | 32768 | 314 bytes |
| Dicing Knight. (SRAM 256 KiB) | 262656 | 262144 | 9972 bytes; the game formats its whole 256 KiB at boot on both |

A 2 KiB EEPROM has the same size on both, so the only difference is the trailer. Beetle's
2048-byte file plus the 512-byte record block is a MiSTer file.
