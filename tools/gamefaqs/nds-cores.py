#!/usr/bin/env python3
"""A raw DS save -> the file each corpus core loads, at the game's chip size.

    python3 -I nds-cores.py RAW --chip BYTES --stem STEM --out DIR [--drop-tail]

--chip is the game's save chip size (melonDS's game-code database, src/ROMList.cpp:
type 1 = 512, 2 = 8 KiB, 3 = 64 KiB, 4 = 128 KiB, 5 = 256 KiB, 6 = 512 KiB, 7 = 1 MiB).

Fitting the save to the chip:
- shorter: padded with 0xFF, as erased EEPROM/flash reads (DeSmuME's ensure() and the
  melonDS/NooDS fill do the same);
- longer: cut to the chip when the rest is all 0xFF, all 0x00, or copies of the chip
  (a dumper that read past the end of a small chip). Any other data past the chip
  stops the script unless --drop-tail is given; that data cannot be addressed on the
  real chip, and the script prints how much of it there was.

Written under DIR (the formats in nds/NOTES.md, "How each core writes the save"):
    raw/STEM.sav          the chip image
    melonds/STEM.sav      the chip image (melonDS reads <stem>.sav from its save dir)
    noods/STEM.sav        the chip image (NooDS reads <stem>.sav from its save dir)
    melonds-ds/STEM.srm   the chip image (the frontend loads it into SAVE_RAM)
    skyemu/STEM.srm       the chip image then 0x00 up to 8 MiB (SkyEmu's save_data)
    desmume/STEM.dsv      what DeSmuME's own import (import_duc/import_raw and
                          ensure(), src/mc.cpp) makes of the chip image: the data, 0xFF
                          up to DeSmuME's next save size (128 KiB becomes 256 KiB:
                          DeSmuME has no 1 Mbit size), then the 122-byte footer with
                          size = the data's length, padSize, type, addr_size, mem_size =
                          padSize, version 0. Used for desmume and desmume-2015.
"""
import argparse
import hashlib
import os
import struct
import sys

SAVE_SIZES = [512, 8 << 10, 32 << 10, 64 << 10, 256 << 10, 512 << 10, 1 << 20, 2 << 20,
              4 << 20, 8 << 20, 16 << 20, 32 << 20, 64 << 20]           # mc.cpp saveSizes
TYPE_SIZES = [None, 512, 8 << 10, 64 << 10, 32 << 10, 256 << 10, 512 << 10, 1 << 20,
              2 << 20, 4 << 20, 8 << 20, 16 << 20, 32 << 20, 64 << 20]   # mc.cpp save_types
TEXT = b"|<--Snip above here to create a raw sav by excluding this DeSmuME savedata footer:"
COOKIE = b"|-DESMUME SAVE-|"


def addr_size_for_old_save_size(n):
    if n == 512:
        return 1
    if n in (8 << 10, 32 << 10, 64 << 10):
        return 2
    if n in (128 << 10, 256 << 10, 512 << 10, 1 << 20, 2 << 20, 8 << 20):
        return 3
    return 0xFFFFFFFF


def dsv(chip):
    n = len(chip)
    pad = next(s for s in SAVE_SIZES if s >= n)
    typ = TYPE_SIZES.index(pad) if pad in TYPE_SIZES else 0
    footer = struct.pack("<6I", n, pad, typ, addr_size_for_old_save_size(n), pad, 0)
    return chip + b"\xff" * (pad - n) + TEXT + footer + COOKIE


def fit(raw, chip, drop_tail):
    if len(raw) <= chip:
        return raw + b"\xff" * (chip - len(raw)), (f"padded {len(raw)} -> {chip} with 0xFF"
                                                     if len(raw) < chip else "exact size")
    tail = raw[chip:]
    if tail.count(0xFF) == len(tail):
        how = "all 0xFF"
    elif tail.count(0) == len(tail):
        how = "all 0x00"
    elif len(raw) % chip == 0 and all(raw[i:i + chip] == raw[:chip] for i in range(0, len(raw), chip)):
        how = "copies of the chip"
    elif drop_tail:
        how = f"data ({len(tail) - tail.count(0xFF)} bytes not 0xFF), dropped (--drop-tail)"
    else:
        sys.exit(f"{len(tail)} bytes past the {chip}-byte chip hold data; --drop-tail to cut them")
    return raw[:chip], f"cut {len(raw)} -> {chip}; the rest was {how}"


def main():
    ap = argparse.ArgumentParser(description="A raw DS save -> each corpus core's file.")
    ap.add_argument("raw")
    ap.add_argument("--chip", type=int, required=True)
    ap.add_argument("--stem", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--drop-tail", action="store_true")
    a = ap.parse_args()
    chip, how = fit(open(a.raw, "rb").read(), a.chip, a.drop_tail)
    outs = {
        ("raw", ".sav"): chip, ("melonds", ".sav"): chip, ("noods", ".sav"): chip,
        ("melonds-ds", ".srm"): chip, ("skyemu", ".srm"): chip + bytes((8 << 20) - len(chip)),
        ("desmume", ".dsv"): dsv(chip),
    }
    print(how)
    for (core, ext), data in outs.items():
        d = os.path.join(a.out, core)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, a.stem + ext)
        open(p, "wb").write(data)
        print(f"{core}: {a.stem + ext} {len(data)} bytes sha1 {hashlib.sha1(data).hexdigest()}")


if __name__ == "__main__":
    main()
