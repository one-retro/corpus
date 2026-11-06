#!/usr/bin/env python3
"""DeSmuME save state (.dst, .ds0-.ds9) -> the battery save inside it.

    python3 -I nds-desmume-state.py IN OUT

Follows DeSmuME's savestate_load and mmu_loadstate (src/saves.cpp) and
BackupDevice::load_state (src/mc.cpp). The file is "DeSmuME SState\\0\\0", u32 LE state
version, DeSmuME version, length and compressed length (0xFFFFFFFF: not compressed),
then the (zlib) body: chunks of u32 type, u32 size, data, ending with type 0xFFFFFFFF.

Chunk 61 is the MMU: u32 version; from version 2 it starts with the backup device:
u32 version, bool32 write_enable, u32 com, u32 addr_size, u32 addr_counter, u32 state,
then the save as a u32-length-prefixed buffer (what DeSmuME's .dsv holds before its
footer). Versions 0 and 1 hold u32 size (and type) and the data directly.
Chunk 130 holds the ROM header (game code, title, revision), printed when present.

DeSmuME pads the data with 0xFF up to a save size when it loads the state; here it
is written as stored, and nds-cores.py fits it to the game's chip.
"""
import struct
import sys
import zlib


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    b = open(sys.argv[1], "rb").read()
    if b[:16] != b"DeSmuME SState\0\0":
        sys.exit("not a DeSmuME save state")
    ssver, dver, length, clen = struct.unpack_from("<4I", b, 16)
    body = b[32:32 + length] if clen == 0xFFFFFFFF else zlib.decompress(b[32:32 + clen])
    if len(body) != length:
        sys.exit(f"body is {len(body)} bytes, header says {length}")
    save = game = None
    o = 0
    while o + 4 <= len(body):
        t = struct.unpack_from("<I", body, o)[0]
        if t == 0xFFFFFFFF:
            break
        size = struct.unpack_from("<I", body, o + 4)[0]
        chunk = body[o + 8:o + 8 + size]
        if t == 61:
            mver = struct.unpack_from("<I", chunk, 0)[0]
            if mver == 0:
                n = struct.unpack_from("<I", chunk, 4)[0]
                save, how = chunk[8:8 + n], f"MMU chunk version 0, {n} bytes"
            elif mver == 1:
                typ, n = struct.unpack_from("<II", chunk, 4)
                save, how = chunk[12:12 + n], f"MMU chunk version 1, type {typ}, {n} bytes"
            else:
                bver, _we, _com, asz, _ctr, _st, n = struct.unpack_from("<7I", chunk, 4)
                save = chunk[32:32 + n]
                how = f"MMU chunk version {mver}, backup device version {bver}, addr_size {asz}, {n} bytes"
        elif t == 130:
            q = 0
            while q + 12 <= len(chunk):
                desc = chunk[q:q + 4]
                sz, cnt = struct.unpack_from("<II", chunk, q + 4)
                v = chunk[q + 12:q + 12 + sz * cnt]
                if desc == b"GINF":
                    game = (f"{v[0:12].rstrip(bytes(1)).decode('latin-1')} "
                            f"{v[12:16].decode('latin-1')} rev {v[0x1E]}")
                q += 12 + sz * cnt
        o += 8 + size
    if save is None:
        sys.exit("no MMU chunk")
    if len(save) == 0:
        sys.exit("the state holds no save data")
    print(f"DeSmuME state version {ssver}, DeSmuME {dver:#x}; ROM {game or 'not recorded'}; {how}")
    open(sys.argv[2], "wb").write(save)


if __name__ == "__main__":
    main()
