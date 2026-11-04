#!/usr/bin/env python3
"""Find and extract ROMs from a No-Intro 1G1R library for a registry system.

    rom.py list SYSTEM [FILTER]     names of the games the library has
    rom.py get SYSTEM "NAME"        extract one, print its path

Cartridge systems come from the No-Intro 1G1R set in the folder $ROMS names, a
zip per system holding a zip per game. Extracted ROMs go to corpus/.cache/roms/SYSTEM/, which is never
committed: they are commercial dumps. Disc systems are not handled here; their
images are used in place.
"""

import io
import os
import sys
import zipfile

LIB = os.environ.get("ROMS", "")
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cache", "roms")

SETS = {
    "gb": "Nintendo - Game Boy",
    "gbc": "Nintendo - Game Boy Color",
    "gba": "Nintendo - Game Boy Advance",
    "nes": "Nintendo - Nintendo Entertainment System (Headered)",
    "fds": "Nintendo - Family Computer Disk System (FDS)",
    "snes": "Nintendo - Super Nintendo Entertainment System",
    "n64": "Nintendo - Nintendo 64 (BigEndian)",
    "virtualboy": "Nintendo - Virtual Boy",
    "genesis": "Sega - Mega Drive - Genesis",
    "mastersystem": "Sega - Master System - Mark III",
    "sega-gg": "Sega - Game Gear",
    "sg-1000": "Sega - SG-1000",
    "sega-32x": "Sega - 32X",
    "pcengine": "NEC - PC Engine - TurboGrafx-16",
    "supergrafx": "NEC - PC Engine SuperGrafx",
    "ngp": "SNK - NeoGeo Pocket",
    "ngpc": "SNK - NeoGeo Pocket Color",
    "wonderswan": "Bandai - WonderSwan",
    "wonderswan-color": "Bandai - WonderSwan Color",
    "atari-2600": "Atari - 2600",
    "atari-5200": "Atari - 5200",
    "atari-7800": "Atari - 7800",
    "atari-lynx": "Atari - Lynx (LYX)",
    "atari-jaguar": "Atari - Jaguar (J64)",
    "colecovision": "Coleco - ColecoVision",
    "intellivision": "Mattel - Intellivision",
    "odyssey2": "Magnavox - Odyssey 2",
    "vectrex": "GCE - Vectrex",
    "msx": "Microsoft - MSX",
    "msx2": "Microsoft - MSX2",
    "c64": "Commodore - Commodore 64",
}


def open_set(system):
    if system not in SETS:
        sys.exit(f"no cartridge set for {system}; known: {', '.join(sorted(SETS))}")
    if not LIB:
        sys.exit("set ROMS to the folder holding the No-Intro 1G1R zips")
    return zipfile.ZipFile(os.path.join(LIB, SETS[system] + ".zip"))


def games(z):
    for n in z.namelist():
        if n.endswith("/"):
            continue
        yield os.path.splitext(os.path.basename(n))[0], n


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, system = sys.argv[1], sys.argv[2]
    z = open_set(system)
    if cmd == "list":
        flt = sys.argv[3].lower() if len(sys.argv) > 3 else ""
        for name, _ in sorted(games(z)):
            if flt in name.lower():
                print(name)
    elif cmd == "get":
        want = sys.argv[3]
        hits = [(name, member) for name, member in games(z) if name == want]
        if not hits:
            hits = [(name, member) for name, member in games(z) if want.lower() in name.lower()]
        if len(hits) != 1:
            sys.exit(f"{len(hits)} matches for {want!r}: " + "; ".join(h[0] for h in hits[:20]))
        name, member = hits[0]
        out = os.path.join(CACHE, system)
        os.makedirs(out, exist_ok=True)
        data = z.read(member)
        if member.lower().endswith(".zip"):
            inner = zipfile.ZipFile(io.BytesIO(data))
            files = [i for i in inner.infolist() if not i.is_dir()]
            for i in files:
                # Flatten: a game zip holds one ROM, sometimes with a sidecar.
                path = os.path.join(out, os.path.basename(i.filename))
                if not os.path.exists(path):
                    with open(path, "wb") as f:
                        f.write(inner.read(i))
            print(os.path.abspath(os.path.join(out, os.path.basename(files[0].filename))))
        else:
            path = os.path.join(out, os.path.basename(member))
            if not os.path.exists(path):
                with open(path, "wb") as f:
                    f.write(data)
            print(os.path.abspath(path))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
