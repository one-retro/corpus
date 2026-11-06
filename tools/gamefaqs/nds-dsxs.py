#!/usr/bin/env python3
""""DSXS" save container -> the raw save.

    python3 -I nds-dsxs.py IN OUT

No reference implementation was found; the layout is read from the one file here:
"DSXS", u8 1, u8 8, two zero bytes, four bytes of unknown meaning (not the CRC-32 of
the save or of the gzip data), then NUL-padded ASCII at 0x10 (game), 0x40 (save name) and 0x70
(description), zeros to 0x100, and from 0x100 one gzip member holding the raw save.
The gzip CRC-32 and length check the result.
"""
import gzip
import sys


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    b = open(sys.argv[1], "rb").read()
    if b[:4] != b"DSXS" or b[0x100:0x102] != b"\x1f\x8b":
        sys.exit("not a DSXS file with a gzip member at 0x100")
    s = lambda o, n: b[o:o + n].split(b"\0")[0].decode("latin-1")
    raw = gzip.decompress(b[0x100:])
    print(f"DSXS: game {s(0x10, 0x30)!r}, name {s(0x40, 0x30)!r}, description {s(0x70, 0x90)!r}; "
          f"gzip {len(b) - 0x100} -> {len(raw)} bytes")
    open(sys.argv[2], "wb").write(raw)


if __name__ == "__main__":
    main()
