# GameFAQs saves: download, convert, verify

Brief for the pass that files every GameFAQs save for the games in this corpus, and checks that
the corpus's cores load each one. Read README.md and tools/BRIEF.md first: layout, provenance,
tools and rules there all apply. This file adds what is different.

## What was downloaded

On 2026-11-05 every GameFAQs save page for a game (product) in the corpus was listed, and every
save in a format of that **system's own hardware or save devices** was downloaded: 1,082 files.
Saves on the same product page for other platforms (a SNES game's DS remake, a PS1 game's PC
port) were left out. Wii Virtual Console saves of a corpus game were kept.

| System | GameFAQs section (format) | Files |
| --- | --- | ---: |
| psx | PlayStation DexDrive Save | 297 |
| psx | PlayStation PS3 Virtual Memory Card Save (ZIP) | 70 |
| ps2 | PlayStation2 Max Drive / CodeBreaker / SharkPort 2 / X-Port Save, PlayStation 2 PS3 Virtual Memory Card Save (ZIP) | 185 |
| gba | GameBoy Advance GameShark / GameShark SP / GameShark USB Connector / Pro Action Replay Save | 376 |
| nds | Action Replay Max DS (.duc), (.dst), (1.00-1.03) Game Save | 79 |
| n64 | Nintendo 64 DexDrive Save | 21 |
| gc | GameCube USB Memory Adapter Save, GameCube MaxDrive Save | 20 |
| psp | PSP Game Save Directory (ZIP) | 17 |
| n64, snes, pcenginecd | Wii VC Game Save File | 17 |

Each file is in `.cache/downloads/gamefaqs/<id>/` exactly as GameFAQs served it (its name is
GameFAQs' `<game-slug>.<id>.<ext>`). `work/gamefaqs/manifest.json` lists them: GameFAQs id,
corpus system, the product page, the section (format and region), the uploader, the date posted,
the listed size, the uploader's description, URLs, and the local path, size and sha1.

A GameFAQs product page covers sibling releases (Pokemon Ruby / Sapphire / Emerald, Diamond /
Pearl / Platinum, Final Fantasy Chronicles), so a save on it may be for a game the corpus does not
have yet. File it too, verified against that game's ROM or disc if the library has it.

## The entry

```
<system>/_<device>/<release> [GameFAQs <id>]/
    <the save files>        as GameFAQs served them; a .zip is replaced by what is in it,
                            with its inner paths (a PSP SAVEDATA folder, a .psv)
    provenance.json
    proof.png               a tile of every core's frame showing the save (order in provenance)
```

`_<device>` names what wrote the file, from its contents (not from GameFAQs' section, which
uploaders get wrong; note a mismatch): `_dexdrive`, `_ps3` (a PS3 export, .psv), `_max-drive`,
`_codebreaker`, `_sharkport` (SharkPort / X-Port share a format; use `_x-port` for X-Port),
`_gameshark` (GBA GameShark/SharkPort .sps), `_gameshark-sp` (.gsv), `_action-replay` (GBA),
`_action-replay-ds`, `_usb-memory-adapter` (GameCube .gci via the Datel adapter), `_max-drive`
(GameCube), `_psp`, `_wii-vc`. If the contents show an emulator wrote it (a raw `.sav` from
VBA, a Project64 `.eep`), use that core's registry slug instead, as any downloaded entry would.

`<release>` is the No-Intro / Redump name of the release the save is for, worked out from the
file: the PS1/PS2 product code in the save's name, the GBA game code or title in a SharkPort
header, the DS game code in an Action Replay header. A European save of a game the corpus has
in its US release is named for the European release, whether or not the library has it.

### provenance.json

```json
{
  "method": "downloaded",
  "system": "gba", "core": "_gameshark",
  "url": "https://gamefaqs.gamespot.com/gba/<page>/saves/<id>",
  "source_page": "https://gamefaqs.gamespot.com/gba/<page>/saves",
  "source": "GameFAQs (section 'GameBoy Advance GameShark Save (North America)')",
  "author": "<uploader>", "licence": null, "posted": "YYYY-MM-DD", "fetched": "2026-11-05",
  "what_it_is": "<the uploader's description, as written>",
  "gamefaqs": {"id": 13291, "product": "<GameFAQs product name>", "section": "...",
               "region": "North America", "served_as": "<slug>.<id>.sps", "listed_size": "65KB"},
  "format": "one line: what the file is, as read from its bytes (header, payload size)",
  "files": {"<name>": {"size": 0, "sha1": "..."}},
  "verified": {
    "date": "2026-11-05",
    "rom": {"name": "...", "sha1": "...", "size": 0},
    "converted_with": "tools/gamefaqs/<converter> <args>: what it does in one line",
    "converted": {"size": 0, "sha1": "..."},
    "script": "scripts/<system>/<game>.load.txt",
    "cores": {
      "mgba": {"result": "loads", "detail": "file select shows RUBY, badges 3, 12:34 — as described"},
      "gpsp": {"result": "rejected", "detail": "game reports the save is corrupted"}
    },
    "proof_order": ["mgba", "gpsp"]
  },
  "note": null
}
```

`result` is one of: `loads` (the game shows this save's content: the name, time, level or
progress the file holds), `rejected` (the game sees no save, a blank or corrupt one, or offers to
format), `core-error` (the core failed to start or crashed), `not-run` (say why in `detail`: no
image of that release in the library, the core cannot run here). A converter that cannot read the
file at all is `"converted_with": null` and every core `not-run`, with the reason in `note`.

## Convert

No core loads these containers as they are (except a GameCube `.gci` in Dolphin's GCI folder and
a PSP save folder in PPSSPP's memory stick). Write one converter per format family in
`tools/gamefaqs/` (Python, standard library, run with `python3 -I`), taking the original file
and writing what the core loads: a raw card, a raw `.sav`, a combined `.srm`. Follow the
reference implementations rather than guessing offsets: mGBA (`src/gba/sharkport.c`, GameShark SP
`.gsv`), VBA-M, DeSmuME (`.duc`/`.dss` import), mymcplus for PS2 (`.max` LZARI, `.cbs` RC4+zlib,
`.psu`, `.sps`/`.xps`, `.psv`), the DexDrive header (PS1: 3904 bytes before a 128 KiB card; N64:
`123-456-STD`, 0x1040 bytes before a 32 KiB pak). Pure Python first; if a format needs a library
(mymcplus is on PyPI, GPL), install it into a venv under `.cache/venv-gamefaqs/` and say so.
Converted files go under `.cache/gamefaqs-conv/<system>/<id>/` and are not filed; provenance
records how they were made and their hash. The converters are committed, so anyone can redo it.

Where `1saves` (one-saves) reads the format too (PS1 `.gme`/`.psv`/`.mcs`; a GameCube save once
it is on a card image, not a bare `.gci`), also run `1saves convert` + `1saves inspect` on the
original (or the card) and note in NOTES.md where it disagrees with the converter. Do not change
one-saves.

## Verify

For each game, write one load script, `scripts/<system>/<game>.load.txt`: power on and go to the
screen that shows a save's content (file select, Continue / Load menu with name, time, level),
and `shot` it. Run it once per core with no save (the baseline), then once per save per core with
the converted save loaded (`tools/make-save.py SYSTEM CORE ROM SCRIPT --dry --srm FILE`, or
`retro-run` directly; memory cards go where that core reads them, see the system's NOTES.md).
Read the frames: a save `loads` when its frame differs from the baseline and shows what the save
holds. Tile each save's frames into its proof.png (`tools/retro-run/crop.py tile`).

Every runnable core of the system in this corpus, in the release the save is for. If a system's
runs are slow (PS2), run every save on one fast core first, then the other cores, and say in the
report how far you got.

## NOTES.md

Add a section `## GameFAQs saves` to `<system>/NOTES.md`: the formats found (and how each
was converted), a table of saves x cores with counts per result, saves for releases the library
lacks, mislabelled sections, and what differs between cores (a core that rejects a valid save
is the interesting finding). Do not rewrite the rest of the file.

## Rules on top of tools/BRIEF.md

- The downloads are untrusted: inspect with `file`/`xxd`/`unzip -l` before extracting, extract
  into a new directory under `.cache/downloads/gamefaqs/<id>/x/`, never execute anything in them.
- Stay inside your systems: `<system>/_*/`, `<system>/NOTES.md` (the new section only),
  `scripts/<system>/*.load.txt`, `tools/gamefaqs/<system>-*.py`, `work/gamefaqs/<system>/`,
  `.cache/gamefaqs-conv/<system>/`. Do not touch other entries, other tools or the manifest.
- The uploader names and descriptions are public GameFAQs text and go in provenance as written.
  Nothing from this machine does (paths, user names, the ROM drive's folders).
- GUI apps only where the system's NOTES/STANDALONE.md already drive one (Dolphin with a TAS
  movie, PPSSPP over its debugger socket), isolated as done there. No browser.
- Run at most 3 emulators at once (PS2: 2). Other workers share the machine.
