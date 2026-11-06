#!/usr/bin/env python3
"""DraStic (Android) save state -> the battery save inside it.

    python3 -I nds-drastic-state.py IN OUT [--offset HEX]

DraStic is closed source; there is no reference implementation. The layout is read
from the two states here (both Pokemon Mystery Dungeon - Explorers of Sky, one USA,
one European):

    0x00  "DraStic-SaveState" padded with '-' to 0x20
    0x20  u32 fields (0x0E or 0x0F, 0x3F, 0, ...), the game code at 0x34
    0x40  u32 LE length of the zlib stream that follows at 0x44

In the inflated state, at 0x30000 in both files, sits a record that matches the
cartridge's save memory: u32 2, u32 address mask (0x1FFFF: a 128 KiB chip, which is
what melonDS's database gives the game), u32 0, u8 3 (address bytes), then mask+1
bytes. In both files those bytes are an Explorers of Sky save (its "POKE_DUN_SORA"
header at +4, the backup copy at +0xC800). The script checks the record before
writing it; --offset reads it elsewhere for a state laid out differently.
"""
import struct
import sys
import zlib


def main():
    args = sys.argv[1:]
    off = 0x30000
    if "--offset" in args:
        i = args.index("--offset")
        off = int(args[i + 1], 16)
        del args[i:i + 2]
    if len(args) != 2:
        sys.exit(__doc__)
    b = open(args[0], "rb").read()
    if not b.startswith(b"DraStic-SaveState"):
        sys.exit("not a DraStic save state")
    code = b[0x34:0x38].decode("latin-1")
    n = struct.unpack_from("<I", b, 0x40)[0]
    d = zlib.decompress(b[0x44:0x44 + n])
    typ, mask, zero, abytes = struct.unpack_from("<IIIB", d, off)
    size = mask + 1
    if size & mask or not 512 <= size <= 8 << 20 or zero != 0 or abytes not in (1, 2, 3):
        sys.exit(f"no save memory record at {off:#x} (type {typ}, mask {mask:#x}, {zero:#x}, {abytes})")
    save = d[off + 13:off + 13 + size]
    if len(save) != size:
        sys.exit("record runs past the end of the state")
    print(f"DraStic state for {code}; inflated {len(d)} bytes; save memory record at {off:#x}: "
          f"type {typ}, {size} bytes, {abytes}-byte addresses")
    open(args[1], "wb").write(save)


if __name__ == "__main__":
    main()
