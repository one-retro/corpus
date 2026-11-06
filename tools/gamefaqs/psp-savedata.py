#!/usr/bin/env python3
"""PSP save folders from GameFAQs ("PSP Game Save Directory (ZIP)"): read them, and lay them
out on a memory stick as PPSSPP (and a real PSP) reads them.

    python3 -I psp-savedata.py info ZIP          the zip's files and its PARAM.SFO fields (JSON)
    python3 -I psp-savedata.py memstick ZIP DIR  write DIR/PSP/SAVEDATA/<SAVEDATA_DIRECTORY>/<files>

A PSP save is a folder PSP/SAVEDATA/<game ID><save name>/ holding PARAM.SFO, DATA.BIN (or the
game's own file names), ICON0.PNG and optional PIC1.PNG / SND0.AT3 / ICON1.PMF. The folder name is
PARAM.SFO's SAVEDATA_DIRECTORY, so a zip whose files sit at its root (no folder) still lands in
the right place. Every file of the zip is copied as it is (a stray Windows Thumbs.db too: the
firmware and PPSSPP ignore files a save's SAVEDATA_FILE_LIST does not name).

PARAM.SFO: "\\0PSF", version, key table offset, data table offset, entry count; 16-byte entries
(key offset u16, format u16: 0x0004 binary ("utf8-s", not terminated: SAVEDATA_FILE_LIST,
SAVEDATA_PARAMS), 0x0204 utf8 string, 0x0404 u32; length u32, max u32, data offset u32). Standard library only; the zip is read with zipfile, names are reduced to
their last component so nothing is written outside DIR.
"""
import hashlib
import json
import os
import struct
import sys
import zipfile


def sfo(data):
    if data[:4] != b"\0PSF":
        raise ValueError("not a PARAM.SFO")
    _, kt, dt, n = struct.unpack("<IIII", data[4:20])
    out = {}
    for i in range(n):
        ko, fmt, ln, mx, do = struct.unpack("<HHIII", data[20 + 16 * i:36 + 16 * i])
        key = data[kt + ko:data.index(b"\0", kt + ko)].decode("ascii", "replace")
        raw = data[dt + do:dt + do + ln]
        if fmt == 0x0404:
            out[key] = struct.unpack("<I", raw[:4])[0]
        elif fmt == 0x0204:
            out[key] = raw.split(b"\0", 1)[0].decode("utf-8", "replace")
        else:
            out[key] = {"binary": ln, "head": raw[:32].hex(), "sha1": hashlib.sha1(raw).hexdigest()}
    return out


def members(z):
    for zi in z.infolist():
        if zi.is_dir():
            continue
        name = zi.filename.replace("\\", "/")
        parts = [p for p in name.split("/") if p]
        if not parts or any(p in (".", "..") for p in parts):
            raise ValueError("unsafe name in zip: %r" % zi.filename)
        yield zi, parts


def read(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        files = []
        param = None
        for zi, parts in members(z):
            data = z.read(zi)
            files.append({"path": "/".join(parts), "size": len(data), "sha1": hashlib.sha1(data).hexdigest()})
            if parts[-1].upper() == "PARAM.SFO":
                param = sfo(data)
                folder = parts[:-1]
        return files, param, ("/".join(folder) if param is not None else None)


def info(zip_path):
    files, param, folder = read(zip_path)
    return {"zip": os.path.basename(zip_path), "folder_in_zip": folder or None, "files": files, "param_sfo": param}


def memstick(zip_path, out):
    files, param, _ = read(zip_path)
    if param is None:
        raise ValueError("no PARAM.SFO in the zip")
    savedir = param.get("SAVEDATA_DIRECTORY")
    if not savedir or "/" in savedir or savedir in (".", ".."):
        raise ValueError("bad SAVEDATA_DIRECTORY %r" % savedir)
    dest = os.path.join(out, "PSP", "SAVEDATA", savedir)
    os.makedirs(dest, exist_ok=True)
    written = []
    with zipfile.ZipFile(zip_path) as z:
        for zi, parts in members(z):
            data = z.read(zi)
            p = os.path.join(dest, parts[-1])
            with open(p, "wb") as f:
                f.write(data)
            written.append({"path": "PSP/SAVEDATA/%s/%s" % (savedir, parts[-1]), "size": len(data),
                            "sha1": hashlib.sha1(data).hexdigest()})
    return {"savedata_directory": savedir, "files": written}


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    if sys.argv[1] == "info":
        print(json.dumps(info(sys.argv[2]), indent=1, ensure_ascii=False))
    elif sys.argv[1] == "memstick" and len(sys.argv) > 3:
        print(json.dumps(memstick(sys.argv[2], sys.argv[3]), indent=1, ensure_ascii=False))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
