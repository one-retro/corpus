#!/usr/bin/env python3
"""Lay a bare GBA save chip image out the way one libretro core keeps it.

    gba-layout.py CHIP --rom ROM --core CORE --outdir DIR [--type TYPE]
    gba-layout.py --info --rom ROM

CHIP is the cartridge's save memory as mGBA and VBA-M hold it: SRAM/FRAM
32 KiB, flash 64 or 128 KiB, EEPROM 512 B or 8 KiB with the bytes in the order
mGBA's GBASavedata keeps them (a GameShark file stores each 8-byte EEPROM block
reversed; gba-sharkport.py and gba-gsv.py undo that). A raw dump (an emulator
.sav uploaded under another name) can be passed as it is: it is cut or padded
with 0xFF to the chip's size, the way mGBA maps a .sav of the wrong size.

The file written is the one CORE reads at boot, named as the core names it,
with the size and offsets that core writes (corpus gba/NOTES.md, "How each
core writes the save"):

    mgba, vba-m   <stem>.srm, exactly the chip
    gpsp          <stem>.srm, 131072 bytes, chip at 0, rest 0xFF
    skyemu        <stem>.srm, 131072 bytes, chip at 0, rest 0xFF; EEPROM with
                  every 8-byte block reversed (SkyEmu's own order)
    vba-next      <stem>.srm, 0x22000 bytes; EEPROM at 0x20000, others at 0
    beetle-gba    <stem>.<rom md5>.eep (EEPROM, exactly the chip) or
                  <stem>.<rom md5>.sav (64 KiB for SRAM and 64K flash, 128 KiB
                  for 128K flash), read by the core from its save directory

TYPE (sram, flash64, flash128, eeprom512, eeprom8k) defaults to what the ROM's
library string says (SRAM_V/SRAM_F_V, FLASH_V/FLASH512_V, FLASH1M_V, EEPROM_V).
The library string does not give an EEPROM's size: it is 8 KiB unless the game
is in EEPROM512 below (checked against the games' own saves in this corpus).

--info prints the ROM's title, game code, library strings and save type.
Python standard library only; run with python3 -I.
"""

import argparse
import hashlib
import json
import os
import re
import sys

SIZES = {"sram": 0x8000, "flash64": 0x10000, "flash128": 0x20000, "eeprom512": 0x200, "eeprom8k": 0x2000}
# Games with a 4 Kbit (512-byte) EEPROM, by the first three letters of the game
# code (the fourth is the region). Klonoa's own saves are 512 bytes in mGBA and
# VBA-M (gba/NOTES.md).
EEPROM512 = {"AKL"}
CORES = ("mgba", "vba-m", "gpsp", "skyemu", "vba-next", "beetle-gba")


def rom_info(rom):
    data = open(rom, "rb").read()
    libs = sorted({m.group().decode() for m in re.finditer(
        rb"(EEPROM_V\d\d\d|SRAM_F_V\d\d\d|SRAM_V\d\d\d|FLASH1M_V\d\d\d|FLASH512_V\d\d\d|FLASH_V\d\d\d|SIIRTC_V\d\d\d)", data)})
    return {
        "title": data[0xA0:0xAC].rstrip(b"\0").decode("latin-1"),
        "code": data[0xAC:0xB0].decode("latin-1"),
        "header16": data[0xA0:0xB0],
        "libs": libs,
        "md5": hashlib.md5(data).hexdigest(),
        "size": len(data),
    }


def save_type(info):
    libs = " ".join(info["libs"])
    if "FLASH1M_V" in libs:
        return "flash128"
    if "FLASH512_V" in libs or "FLASH_V" in libs:
        return "flash64"
    if "SRAM" in libs:
        return "sram"
    if "EEPROM_V" in libs:
        return "eeprom512" if info["code"][:3] in EEPROM512 else "eeprom8k"
    return None


def fit(chip, size):
    """Cut or pad (0xFF, an erased chip) to size."""
    chip = bytes(chip[:size])
    return chip + b"\xff" * (size - len(chip))


def reverse8(data):
    return b"".join(data[i:i + 8][::-1] for i in range(0, len(data), 8))


def import_payload(payload, stype):
    """A save device's payload as the chip, as mGBA's _importSavedata
    (src/gba/sharkport.c) puts it into the cartridge: a 64K-flash cart given more
    than 64 KiB becomes 128K flash; a payload larger than the chip is cut to
    the chip; one of exactly 512 or 8192 bytes (EEPROM) has each 8-byte block
    reversed; a shorter payload fills the start of an erased (0xFF) chip.
    Returns (chip, type)."""
    if stype == "flash64" and len(payload) > SIZES["flash64"]:
        stype = "flash128"
    size = min(len(payload), SIZES[stype])
    data = bytes(payload[:size])
    if size in (0x200, 0x2000):
        data = reverse8(data)
    return fit(data, SIZES[stype]), stype


def layout(chip, rom, core, stype=None):
    """(file name, bytes) of CHIP as CORE keeps it for ROM."""
    info = rom_info(rom)
    stype = stype or save_type(info)
    if stype not in SIZES:
        raise SystemExit(f"no save type for {rom}; pass --type")
    chip = fit(chip, SIZES[stype])
    eeprom = stype.startswith("eeprom")
    stem = os.path.splitext(os.path.basename(rom))[0]
    if core in ("mgba", "vba-m"):
        return stem + ".srm", chip
    if core == "gpsp":
        return stem + ".srm", fit(chip, 0x20000)
    if core == "skyemu":
        return stem + ".srm", fit(reverse8(chip) if eeprom else chip, 0x20000)
    if core == "vba-next":
        if eeprom:
            return stem + ".srm", b"\xff" * 0x20000 + fit(chip, 0x2000)
        return stem + ".srm", fit(chip, 0x22000)
    if core == "beetle-gba":
        if eeprom:
            return f"{stem}.{info['md5']}.eep", chip
        return f"{stem}.{info['md5']}.sav", fit(chip, 0x20000 if stype == "flash128" else 0x10000)
    raise SystemExit(f"unknown core {core}; known: {', '.join(CORES)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chip", nargs="?")
    ap.add_argument("--rom", required=True)
    ap.add_argument("--core", choices=CORES)
    ap.add_argument("--type", choices=sorted(SIZES))
    ap.add_argument("--outdir")
    ap.add_argument("--info", action="store_true")
    a = ap.parse_args()
    info = rom_info(a.rom)
    if a.info:
        out = {k: v for k, v in info.items() if k != "header16"}
        out["type"] = a.type or save_type(info)
        print(json.dumps(out))
        return
    if not (a.chip and a.core and a.outdir):
        ap.error("CHIP, --core and --outdir are required")
    name, data = layout(open(a.chip, "rb").read(), a.rom, a.core, a.type)
    os.makedirs(a.outdir, exist_ok=True)
    path = os.path.join(a.outdir, name)
    with open(path, "wb") as f:
        f.write(data)
    print(json.dumps({"file": path, "size": len(data), "sha1": hashlib.sha1(data).hexdigest()}))


if __name__ == "__main__":
    main()
