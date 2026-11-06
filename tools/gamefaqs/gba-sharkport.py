#!/usr/bin/env python3
"""Read a GBA SharkPort save (GameShark .sps, Action Replay .xps) and write the
bare save chip, or the file one libretro core loads.

    gba-sharkport.py FILE                       print what the file holds (JSON)
    gba-sharkport.py FILE --rom ROM -o CHIP     write the chip image
    gba-sharkport.py FILE --rom ROM --core CORE --outdir DIR
                                                write CORE's file (gba-layout.py)

The format, as mGBA reads it (src/gba/sharkport.c,
GBASavedataSharkPortGetPayload / GBASavedataImportSharkPort), all integers
little-endian:

    u32 13, "SharkPortSave"
    u32 0x000F0000                    (GBA save)
    u32 n, n bytes                    title     (VBA-M: title)
    u32 n, n bytes                    date      (VBA-M: description)
    u32 n, n bytes                    notes
    u32 N                             0x1C + payload size
    0x1C bytes                        cart header: ROM 0xA0-0xAF (title, game
                                      code), 0, 0, complement check, maker, 1, 0...
    N - 0x1C bytes                    the save
    u32 checksum                      sum += byte << (sum % 24) over header and
                                      save (see below)

mGBA checks the first 15 header bytes (title and the game code without its
region letter) against the cartridge, then imports the payload as
gba-layout.py's import_payload describes (cut to the chip, EEPROM blocks
reversed).

The checksum is not needed to import (mGBA's import does not test it), but it
tells writers apart, so it is reported: "signed" when the bytes were summed as
signed chars (VBA-M's CPUWriteGSASnapshot, mGBA's exporter on x86), "unsigned"
when summed as unsigned bytes, "neither" otherwise.

A file mGBA's reader rejects (bad string lengths, a payload size that runs
past the end) is rejected here too: no offsets are guessed.
Python standard library only; run with python3 -I.
"""

import argparse
import hashlib
import json
import os
import runpy
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
MAGIC = b"\x0d\x00\x00\x00SharkPortSave"
MAX = 0x20000 + 0x1C


def checksum(data, signed):
    s = 0
    for b in data:
        if signed and b > 127:
            b -= 256
        s = (s + (b << (s % 24))) & 0xFFFFFFFF
    return s


def parse(data):
    """(info, cart header, payload), as mGBA's reader finds them."""
    if not data.startswith(MAGIC):
        raise ValueError("no SharkPortSave header")
    (kind,) = struct.unpack_from("<I", data, 17)
    if kind != 0x000F0000:
        raise ValueError(f"kind {kind:#x} is not 0x000F0000 (a GBA save)")
    o, fields = 21, []
    for _ in range(3):
        (n,) = struct.unpack_from("<I", data, o)
        if o + 4 + n > len(data):
            raise ValueError(f"string field at {o:#x} claims {n:#x} bytes, past the end of the file")
        fields.append(data[o + 4:o + 4 + n])
        o += 4 + n
    (size,) = struct.unpack_from("<I", data, o)
    if not 0x1C <= size <= MAX or o + 4 + size + 4 > len(data):
        raise ValueError(f"payload size {size:#x} at {o:#x} does not fit the file ({len(data):#x} bytes)")
    header = data[o + 4:o + 4 + 0x1C]
    payload = data[o + 4 + 0x1C:o + 4 + size]
    (stored,) = struct.unpack_from("<I", data, o + 4 + size)
    summed = header + payload
    info = {
        "fields": [f.decode("latin-1") for f in fields],
        "cart_title": header[:12].decode("latin-1"),
        "cart_code": header[12:16].decode("latin-1"),
        "header": header.hex(),
        "payload_offset": o + 4 + 0x1C,
        "payload_size": len(payload),
        "checksum": ("signed" if checksum(summed, True) == stored else
                     "unsigned" if checksum(summed, False) == stored else "neither"),
        "trailing_bytes": len(data) - (o + 4 + size + 4),
    }
    return info, header, payload


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--rom")
    ap.add_argument("--type", help="sram, flash64, flash128, eeprom512, eeprom8k (default: from the ROM)")
    ap.add_argument("-o", "--out", help="write the chip image here")
    ap.add_argument("--core")
    ap.add_argument("--outdir")
    a = ap.parse_args()
    if a.core and not (a.rom and a.outdir):
        ap.error("--core needs --rom and --outdir")
    lay = runpy.run_path(os.path.join(HERE, "gba-layout.py"))
    info, header, payload = parse(open(a.file, "rb").read())
    if a.rom or a.type:
        stype = a.type
        if a.rom:
            rom = lay["rom_info"](a.rom)
            info["rom_header_match"] = header[:15] == rom["header16"][:15]
            stype = stype or lay["save_type"](rom)
        chip, stype = lay["import_payload"](payload, stype)
        info["type"] = stype
        info["chip"] = {"size": len(chip), "sha1": hashlib.sha1(chip).hexdigest()}
        if a.out:
            with open(a.out, "wb") as f:
                f.write(chip)
        if a.core:
            name, out = lay["layout"](chip, a.rom, a.core, stype)
            os.makedirs(a.outdir, exist_ok=True)
            with open(os.path.join(a.outdir, name), "wb") as f:
                f.write(out)
            info["core_file"] = {"name": name, "size": len(out), "sha1": hashlib.sha1(out).hexdigest()}
    print(json.dumps(info))


if __name__ == "__main__":
    main()
