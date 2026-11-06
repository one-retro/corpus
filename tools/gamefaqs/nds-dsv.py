#!/usr/bin/env python3
"""DeSmuME .dsv -> the raw save before its footer.

    python3 -I nds-dsv.py IN OUT

Follows DeSmuME's BackupDevice::GetDSVFileInfo and import_dsv (src/mc.cpp). A .dsv is
the chip image, then the 82-byte text "|<--Snip above here to create a raw sav by
excluding this DeSmuME savedata footer:", six u32 LE (size, padSize, type, addr_size,
mem_size, version 0) and the 16-byte cookie "|-DESMUME SAVE-|". The data before the
footer is padSize bytes; that is what is written. The first field is the highest
address the game wrote, not the chip size.

DeSmuME requires the cookie at the very end of the file. A .dsv another tool padded
with 0xFF (seen inside an Action Replay file) is accepted when only 0xFF follows
the cookie; the script says so.
"""
import struct
import sys

TEXT = b"|<--Snip above here to create a raw sav by excluding this DeSmuME savedata footer:"
COOKIE = b"|-DESMUME SAVE-|"
FOOTER = len(TEXT) + 24 + len(COOKIE)
TYPES = ["Autodetect", "EEPROM 4kbit", "EEPROM 64kbit", "EEPROM 512kbit", "FRAM 256kbit",
         "FLASH 2Mbit", "FLASH 4Mbit", "FLASH 8Mbit", "FLASH 16Mbit", "FLASH 32Mbit",
         "FLASH 64Mbit", "FLASH 128Mbit", "FLASH 256Mbit", "FLASH 512Mbit"]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1:]
    b = open(src, "rb").read()
    end = b.rfind(COOKIE)
    if end < 0:
        sys.exit("no DeSmuME footer cookie")
    end += len(COOKIE)
    tail = b[end:]
    if tail and tail.count(0xFF) != len(tail):
        sys.exit("data follows the DeSmuME footer")
    size, pad, typ, asz, mem, ver = struct.unpack_from("<6I", b, end - len(COOKIE) - 24)
    if ver != 0:
        sys.exit(f"footer version {ver}, DeSmuME accepts only 0")
    if b[end - FOOTER:end - FOOTER + len(TEXT)] != TEXT:
        sys.exit("footer text missing")
    if pad != end - FOOTER:
        sys.exit(f"footer padSize {pad} but {end - FOOTER} bytes precede the footer")
    tname = TYPES[typ] if typ < len(TYPES) else "?"
    print(f"DeSmuME footer: size {size}, padSize {pad}, type {typ} ({tname}), addr_size {asz}, "
          f"mem_size {mem}" + (f"; {len(tail)} bytes of 0xFF after the cookie" if tail else ""))
    open(dst, "wb").write(b[:pad])


if __name__ == "__main__":
    main()
