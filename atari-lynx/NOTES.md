# Atari Lynx

Nothing filed. No Lynx game released by Atari or its licensees (1989-1996) has save memory; the
cartridge EEPROM (93Cxx serial EEPROM, wired to the cart's AUDIN/strobe lines) is used only by
**aftermarket homebrew**, and the library (the No-Intro LYX set, 74 retail games, plus a GoodLynx
2.01 set) contains none. Two of the three runnable cores
do emulate the EEPROM, in different files with the same bytes.

## Which games have an EEPROM

Handy's own cart database (`lynx/cart_db.h`, used for headerless LYX files) flags exactly these
with `CART_EEPROM_93C46`, all aftermarket: 8-Bit Slicks, Alpine Games, A Bug's Trip Redux,
MegaPak 1, Sky Raider Redux, "Unnamed", Vikings Saga - Protect The Love, Vikings Saga - Save The
Love, Wyvern Tales. It notes Eye of the Beholder (prototype dumps and a later release, none in
the No-Intro 1G1R set here) as having "16K NVRAM", which Handy does not emulate. LNX files made for homebrew carry the EEPROM type in
the header instead. MiSTer's AtariLynx core README says the same thing from the other side:
"Custom external EEPROM not supported (not used in official games, only homebrew)".

## Evidence from the cores

California Games was booted in each core both as the No-Intro `.lyx` and as the GoodLynx `.lnx`,
with `lynxboot.img` (md5 fcd403db..., from a Pocket's `Assets/lynx/common`). All three loaded both
files. Without an EEPROM all three report **save RAM 0 bytes** and write nothing.

| Core | Build | EEPROM | File | Size | Byte order |
| --- | --- | --- | --- | --- | --- |
| beetle-lynx | Beetle Lynx v1.24.0 fcdefcf | not emulated (no EEPROM code in the core) | none | - | - |
| handy | Handy 0.97 bc55d46 | 93C46/56/66/76/86, 8- or 16-bit organisation, type from the LNX header or the cart database | **`<savedir>/<content name>.eeprom`**, written by the core itself through the VFS, on `retro_reset` and at unload; there is no `.srm` | type-dependent: 128 (93C46 x16) up to 2048 | host-order `uint16_t romdata[]`: **little-endian words** in 16-bit mode |
| gearlynx | Gearlynx 1.2.37-8-gd5c3b23 | 93C46-93C86, 8-/16-bit, type from header, database, or the `gearlynx_eeprom_type` option | **`<stem>.srm`** via `RETRO_MEMORY_SAVE_RAM` | type-dependent | host-order `u16 m_rom_data[]`: little-endian words in 16-bit mode |

Measured: Gearlynx with `gearlynx_eeprom_type = 93C46_16bit` forced on California Games (which
never touches an EEPROM) exposes 128 bytes of save RAM and writes a 128-byte `.srm` of all 0xFF,
the blank chip. Not filed: the game wrote nothing. Handy fills its buffer with 0xFF too
(`memset(romdata, 0xff, ...)`), but writes its `.eeprom` only when the cart has an EEPROM type.

So a homebrew save moves between Handy and Gearlynx by renaming `<name>.eeprom` to `<name>.srm`:
both store the chip as host-order 16-bit words. A MiSTer/BigPEmu-style big-endian dump would not
match; none was found to compare.

## Games x cores

| Game | beetle-lynx | gearlynx | handy |
| --- | --- | --- | --- |
| (none: no game in the library has an EEPROM) | - | - | - |

| Core | Status |
| --- | --- |
| atarilynx-mister (MiSTer) | not runnable. No EEPROM support (README "Missing features"); it has save states only. Nothing to find |
| budude2-lynx (openFPGA) | not runnable. README documents no save support; nothing found |
| mednafen (standalone) | not runnable. Same Lynx emulation as beetle-lynx: no EEPROM, nothing to find |

## Leads

- A played Handy/Gearlynx save needs an EEPROM homebrew ROM (e.g. the freeware releases among the
  titles above); none is in the library.
