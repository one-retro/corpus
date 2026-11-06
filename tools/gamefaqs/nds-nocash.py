#!/usr/bin/env python3
"""no$gba backup file ("NocashGbaBackupMediaSavDataFile") -> the raw save.

    python3 -I nds-nocash.py IN OUT

Follows DeSmuME's no_gba_unpackSAV (src/mc.cpp): the 31-byte id, 0x1A at 0x1F, "SRAM"
at 0x40 and a u32 method at 0x44. Method 0: u32 size at 0x48, the data at 0x4C.
Method 1: u32 packed size at 0x48, u32 unpacked size at 0x4C, then from 0x50 a run
of codes: 00 ends; 80 v n16 is n16 copies of v; 81..FF v is (code-0x80) copies of
v; 01..7F is that many literal bytes.

DeSmuME then trims trailing 0xFF rows and pads up to a save type; here the unpacked
data is written as it is, and nds-cores.py fits it to the game's chip.
"""
import struct
import sys

ID = b"NocashGbaBackupMediaSavDataFile"


def unpack(b):
    if len(b) < 0x50 or b[:31] != ID or b[0x1F] != 0x1A or b[0x40:0x44] != b"SRAM":
        sys.exit("not a no$gba backup file")
    method = struct.unpack_from("<I", b, 0x44)[0]
    if method == 0:
        n = struct.unpack_from("<I", b, 0x48)[0]
        return method, n, b[0x4C:0x4C + n]
    if method != 1:
        sys.exit(f"unknown no$gba method {method}")
    packed, n = struct.unpack_from("<II", b, 0x48)
    out = bytearray()
    s = 0x50
    while True:
        cc = b[s]
        s += 1
        if cc == 0:
            break
        if cc == 0x80:
            out += bytes([b[s]]) * struct.unpack_from("<H", b, s + 1)[0]
            s += 3
        elif cc > 0x80:
            out += bytes([b[s]]) * (cc - 0x80)
            s += 1
        else:
            out += b[s:s + cc]
            s += cc
    if len(out) != n:
        sys.exit(f"unpacked {len(out)} bytes, header says {n}")
    return method, n, bytes(out)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    b = open(sys.argv[1], "rb").read()
    method, n, raw = unpack(b)
    print(f"no$gba backup, method {method}, {n} bytes")
    open(sys.argv[2], "wb").write(raw)


if __name__ == "__main__":
    main()
