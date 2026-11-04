# SuperGrafx

**Nothing filed: no SuperGrafx game saves.**

The No-Intro set has the five SuperGrafx-only HuCards that exist:
- 1941 - Counter Attack (Japan)
- Aldynes - The Misson Code for Rage Crisis (Japan)
- Battle Ace (Japan)
- Daimakaimura (Japan)
- Madou King Granzort (Japan)

None of them can save:
- None contains Hudson's backup-RAM library, whose "HUBM!BM FORMAT!" string is in every
  PC Engine card that saves (Neutopia, Bomberman '93, Darius Plus, Populous and the rest; see
  ../pcengine/NOTES.md).
- None writes to the BRAM unlock port $1807 (`STA/STX/STY/STZ $1807`).
- None maps bank $F7 (`LDA/LDX/LDY #$F7` followed by `TAM`).

The same scan finds known savers and misses known password games (Military Madness, Dungeon
Explorer, Final Lap Twin), so it can be trusted this far. The cards have no RAM of their own,
and no list of save-capable games (Black Falcon Games' system-save list, Tennokoe-compatible
lists) names any of them.

What the cores do anyway (Daimakaimura, booted to the title in each runnable core): both write
a 2048-byte `<stem>.srm` holding only a formatted, empty BRAM.
- beetle-supergrafx: `HUBM 00 88 10 80`.
- geargrafx: `HUBM 00 A0 10 80`, which it identifies as "Daimakaimura (J) (SGX)" from its
  database.

The make-save harness would file such a file, because it is neither all-0x00 nor all-0xFF. It
was not filed: the game never wrote it.

## The SuperGrafx-enhanced card that does save

Darius Plus (Japan) (SG Enhanced) runs on both a PC Engine and a SuperGrafx, and it saves
(`DARIUS.SCR`, 276 B, its high-score table). No-Intro lists it under PC Engine, so it is filed
under `pcengine/` for all four PC Engine cores, beetle-supergrafx and geargrafx included. See
../pcengine/NOTES.md. Darius Alpha (also SG-enhanced) has the BRAM library too, but was not tried.

## Cores

| Core | Status |
| --- | --- |
| beetle-supergrafx | runs SuperGrafx games (Daimakaimura checked); nothing to save |
| geargrafx | runs SuperGrafx games (Daimakaimura checked); nothing to save |
| agg23-pc-engine (openFPGA), mednafen (standalone), turbografx16-mister (MiSTer) | not runnable; nothing to look for online, since no SuperGrafx game saves |
