#!/usr/bin/env python3
"""Split a Game Boy battery save that carries a VBA/BGB-style clock footer.

    gb-footer.py SAVE OUT.srm [--sram-size N]

Emulators that write the MBC3 clock into the save file append it after the cartridge RAM:
5 x u32 LE clock registers (seconds, minutes, hours, day low, day high/control), 5 x u32 LE
latched copies, then the Unix time of the write, as u32 LE (44 bytes, the older footer) or u64
LE (48 bytes, what mGBA, VBA-M and BGB write now). The libretro cores read the RAM alone (a
clock, when they keep one, goes to a separate .rtc), so this writes the RAM to OUT.srm and
prints the footer it found as JSON. With no --sram-size the RAM size is the file size rounded
down to a multiple of 8 KiB (2 KiB for the smallest carts).
"""
import hashlib
import json
import struct
import sys
import time


def split(data, sram_size=None):
    if sram_size is None:
        unit = 0x2000 if len(data) >= 0x2000 else 0x800
        sram_size = len(data) - len(data) % unit
    ram, footer = data[:sram_size], data[sram_size:]
    info = {"sram": len(ram), "footer": len(footer)}
    if len(footer) in (44, 48):
        regs = struct.unpack_from("<10I", footer)
        stamp = struct.unpack_from("<I" if len(footer) == 44 else "<Q", footer, 40)[0]
        info.update({
            "clock": dict(zip(("sec", "min", "hour", "day_low", "day_high"), regs[:5])),
            "latched": dict(zip(("sec", "min", "hour", "day_low", "day_high"), regs[5:])),
            "unix_time": stamp,
            "written": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(stamp)),
            "layout": "VBA/BGB footer, %d-bit time" % (32 if len(footer) == 44 else 64),
        })
    elif footer:
        info["layout"] = "unrecognised trailing bytes"
    return ram, info


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    size = None
    if "--sram-size" in argv:
        i = argv.index("--sram-size")
        size = int(argv[i + 1], 0)
        argv = argv[:i] + argv[i + 2:]
    data = open(argv[0], "rb").read()
    ram, info = split(data, size)
    with open(argv[1], "wb") as f:
        f.write(ram)
    info["out"] = {"size": len(ram), "sha1": hashlib.sha1(ram).hexdigest()}
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
