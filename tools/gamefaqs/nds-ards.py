#!/usr/bin/env python3
"""Action Replay DS save (.duc, .dss, .dst) -> the save it holds.

    python3 -I nds-ards.py IN OUT

Follows DeSmuME's BackupDevice::import_duc (src/mc.cpp):

- version 1: the file starts "ARDS000000000001"; the save follows a 500-byte header.
  The header holds UTF-16LE strings at 0x10 (game), 0x50 (save name), 0x90
  (description) and ASCII copies further on; no game code.
- version 2: the file starts with four zero bytes and has 0xC0 at 0xA3; bytes 0xA1
  and 0xA2 give the save size (b[0xA1] << 8 | b[0xA2] << 16); the save follows a
  0xA4-byte header, and DeSmuME rejects the file unless its size matches.

Some version-1 files (two here, both from GameFAQs' ".dst" section) hold a
compressed payload instead of the raw save. DeSmuME does not know it and would
load the compressed bytes as the save. The layout, read from the bytes:

    u32 LE  total size of the save
    u32 LE  number of blocks
    per block:
      u32 BE  bytes the block decodes to
      u32 BE  bytes of the block that follow (escape byte included)
      u8      escape byte
      ...     RLE: ESC 00 is a literal ESC, ESC n v is n+1 copies of v, any
              other byte is itself
    zero padding to the end of the file

It is recognised only when every block decodes to exactly its stated size, the
sizes add up to the total and only zeros follow; the save is then written
decompressed. Everything else is written exactly as it follows the header.
The size is not changed here: nds-cores.py fits the save to the game's chip.
"""
import struct
import sys


def utf16(b, off, n):
    return b[off:off + n].decode("utf-16-le", "replace").split("\0")[0]


def unrle(p):
    """Decode the block-RLE payload, or return None if p is not one."""
    if len(p) < 17:
        return None
    total, nblocks = struct.unpack_from("<II", p, 0)
    if not (0 < nblocks <= 4096 and 0 < total <= 16 << 20):
        return None
    out = bytearray()
    o = 8
    for _ in range(nblocks):
        if o + 9 > len(p):
            return None
        usize, csize = struct.unpack_from(">II", p, o)
        data = p[o + 8:o + 8 + csize]
        if len(data) != csize or csize < 1:
            return None
        esc = data[0]
        blk = bytearray()
        i = 1
        while i < len(data):
            x = data[i]
            if x != esc:
                blk.append(x)
                i += 1
            elif i + 1 < len(data) and data[i + 1] == 0:
                blk.append(esc)
                i += 2
            elif i + 2 < len(data):
                blk += bytes([data[i + 2]]) * (data[i + 1] + 1)
                i += 3
            else:
                return None
        if len(blk) != usize:
            return None
        out += blk
        o += 8 + csize
    if len(out) != total or any(p[o:]):
        return None
    return bytes(out)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1:]
    b = open(src, "rb").read()
    if b[:16] == b"ARDS000000000001":
        print(f"Action Replay DS, version 1 (500-byte header): game {utf16(b, 0x10, 64)!r}, "
              f"name {utf16(b, 0x50, 64)!r}, description {utf16(b, 0x90, 200)!r}")
        payload = b[500:]
    elif b[:4] == b"\0\0\0\0" and len(b) > 0xA4 and b[0xA3] == 0xC0:
        size = (b[0xA1] << 8) | (b[0xA2] << 16)
        if size != len(b) - 0xA4:
            sys.exit(f"version 2 header says {size} bytes, file holds {len(b) - 0xA4}")
        strings = [s.decode("latin-1") for s in b[4:0xA0].split(b"\0") if s]
        print(f"Action Replay DS, version 2 (0xA4-byte header), size {size}: strings {strings}")
        payload = b[0xA4:]
    else:
        sys.exit("not an Action Replay DS save (neither header version matches)")
    raw = unrle(payload)
    if raw is not None:
        n = struct.unpack_from("<I", payload, 4)[0]
        print(f"payload is block-RLE compressed: {len(payload)} bytes, {n} blocks -> {len(raw)} bytes")
    else:
        raw = payload
        print(f"payload: {len(raw)} bytes")
    open(dst, "wb").write(raw)


if __name__ == "__main__":
    main()
