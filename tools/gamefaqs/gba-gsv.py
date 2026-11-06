#!/usr/bin/env python3
"""Read a GameShark SP save (.gsv, "ADVSAVEG") and write the bare save chip,
or the file one libretro core loads.

    gba-gsv.py FILE                             print what the file holds (JSON)
    gba-gsv.py FILE --rom ROM -o CHIP           write the chip image
    gba-gsv.py FILE --rom ROM --core CORE --outdir DIR
                                                write CORE's file (gba-layout.py)

The format, as mGBA reads it (src/gba/sharkport.c, GBASavedataGSVPayloadSize /
GBASavedataGSVGetPayload / GBASavedataImportGSV), integers little-endian:

    0x000  "ADVSAVEG"
    0x008  u32 checksum (algorithm unknown; mGBA does not check it)
    0x00C  12 bytes: the cart's title (ROM 0xA0-0xAB), compared with the cart
    0x018  u32 padding
    0x01C  u32 type: 2 SRAM 32K, 3 EEPROM 512, 4 EEPROM 8K, 5 flash 64K,
           6 flash 128K; any other value: the rest of the file
    0x020  u32 unknown[3] (the second one equals the payload size in every
           file seen here)
    0x02C  description, 0x400 bytes
    0x42C  "xV4\\x12" (0x12345678)
    0x430  the save, as many bytes as the type says

The payload is then imported as gba-layout.py's import_payload describes (cut
to the chip, EEPROM blocks reversed), as mGBA's _importSavedata does.
Python standard library only; run with python3 -I.
"""

import argparse
import hashlib
import json
import os
import runpy
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
TYPES = {2: 0x8000, 3: 0x200, 4: 0x2000, 5: 0x10000, 6: 0x20000}


def parse(data):
    if data[:8] != b"ADVSAVEG":
        raise ValueError("no ADVSAVEG header")
    if data[0x42C:0x430] != b"xV4\x12":
        raise ValueError("no 0x12345678 footer at 0x42C")
    (stored,) = struct.unpack_from("<I", data, 8)
    (kind,) = struct.unpack_from("<I", data, 0x1C)
    unk = struct.unpack_from("<3I", data, 0x20)
    size = TYPES.get(kind, len(data) - 0x430)
    payload = data[0x430:0x430 + size]
    if len(payload) != size:
        raise ValueError(f"type {kind} wants {size} bytes, the file has {len(data) - 0x430}")
    info = {
        "ident": data[0xC:0x18].decode("latin-1"),
        "type": kind,
        "unknown": [hex(u) for u in unk],
        "checksum": hex(stored),
        "description": data[0x2C:0x42C].split(b"\0")[0].decode("latin-1"),
        "payload_size": size,
        "trailing_bytes": len(data) - 0x430 - size,
    }
    return info, data[0xC:0x18], payload


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--rom")
    ap.add_argument("--type", help="sram, flash64, flash128, eeprom512, eeprom8k (default: from the ROM)")
    ap.add_argument("-o", "--out")
    ap.add_argument("--core")
    ap.add_argument("--outdir")
    a = ap.parse_args()
    if a.core and not (a.rom and a.outdir):
        ap.error("--core needs --rom and --outdir")
    lay = runpy.run_path(os.path.join(HERE, "gba-layout.py"))
    info, ident, payload = parse(open(a.file, "rb").read())
    if a.rom or a.type:
        stype = a.type
        if a.rom:
            rom = lay["rom_info"](a.rom)
            info["rom_header_match"] = ident == rom["header16"][:12]
            stype = stype or lay["save_type"](rom)
        chip, stype = lay["import_payload"](payload, stype)
        info["chip_type"] = stype
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
