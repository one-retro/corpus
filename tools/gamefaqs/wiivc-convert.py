#!/usr/bin/env python3
"""Wii Virtual Console save (a `data.bin` exported to SD) -> what the libretro cores load.

    wiivc-convert.py info DATA.BIN               print the header, banner title and files
    wiivc-convert.py extract DATA.BIN OUTDIR     write the decrypted NAND files as the Wii kept them
    wiivc-convert.py convert DATA.BIN OUTDIR     write the emulator save(s) for the VC platform found

`data.bin` (WiiBrew "Savegame Files"; Segher's tachtig; save-file-converter's Wii.js):
  0x0000  0xF0C0  header, AES-128-CBC with the SD key and SD IV: title ID, banner size,
                  permissions, MD5 of the header (computed with the MD5 blanker in its place),
                  then the "WIBN" banner (title and subtitle in UTF-16BE, icons)
  0xF0C0  0x80    "Bk" backup header, plain: size 0x70, magic 0x426B0001, console ID,
                  number of files, size of files, total size, title ID's game code at 0x64
  then per file   0x80 file header (magic 0x03ADF17E, size, permissions, attributes, type,
                  name, IV at 0x50), then the file, AES-128-CBC with the SD key and that IV,
                  padded to 0x40
  then            the console's certificates and signature (not checked here)

What each VC platform keeps (vcromclaim wiimetadata.py `extractsave`, n64save.py,
tgsave.py; save-file-converter Wii/ConvertFrom/*):
  N64   `EEP_<game>` (EEPROM or FlashRAM) or `RAM_<game>` (SRAM), console byte order.
        EEPROM: the first 0x800 bytes. SRAM 32 KiB / FlashRAM 128 KiB: kept as is, then
        stored with each 32-bit word reversed, as Mupen64Plus / ParaLLEl keep them.
  SNES  `savedata.bin`: the cartridge SRAM ("standard SRM files"), copied as is.
  PCE   `pcengine.bup`: "$PCE", a 4-byte seed, 8 bytes, then an 8 KiB BRAM with every
        4-byte block XORed with NOT the previous stored block, then 16 bytes. Converted to the
        2 KiB BRAM the cores keep, with the end pointer 0xA000 changed to 0x8800.

N64 output, for the cores in this corpus:
  <stem>.srm   296960 bytes, Mupen64Plus-Next / ParaLLEl N64's combined save: EEPROM at
               0x0, four Controller Paks at 0x800 (formatted as mupen64plus-core's
               format_mempak does, with an all-zero serial), SRAM at 0x20800, FlashRAM at
               0x28800; everything the save does not fill is 0xFF, as the cores start.
  <stem>.eep / .sra / .fla   standalone Mupen64Plus's per-chip file (same byte order).

Standard library only (AES is implemented below). Run with python3 -I.
"""

import hashlib
import json
import os
import struct
import sys

SD_KEY = bytes.fromhex("ab01b9d8e1622b08afbad84dbfc2a55d")
SD_IV = bytes.fromhex("216712e6aa1f689f95c5a22324dc6a98")
MD5_BLANKER = bytes.fromhex("0e65378199be4517ab06ec22451a5793")
HEADER_SIZE = 0xF0C0
BK_SIZE = 0x80
FILE_MAGIC = 0x03ADF17E

# ---------------------------------------------------------------- AES-128 (decrypt only)

SBOX = [0] * 256
INV_SBOX = [0] * 256


def _init_sbox():
    p = q = 1
    while True:
        p = p ^ ((p << 1) & 0xFF) ^ (0x1B if p & 0x80 else 0)
        q ^= q << 1
        q ^= q << 2
        q ^= q << 4
        q &= 0xFF
        if q & 0x80:
            q ^= 0x09
        x = q ^ ((q << 1 | q >> 7) & 0xFF) ^ ((q << 2 | q >> 6) & 0xFF) \
            ^ ((q << 3 | q >> 5) & 0xFF) ^ ((q << 4 | q >> 4) & 0xFF)
        SBOX[p] = x ^ 0x63
        if p == 1:
            break
    SBOX[0] = 0x63
    for i, v in enumerate(SBOX):
        INV_SBOX[v] = i


_init_sbox()


def _xt(a):
    return ((a << 1) ^ 0x1B) & 0xFF if a & 0x80 else a << 1


def _mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = _xt(a)
        b >>= 1
    return r


MUL9 = [_mul(i, 9) for i in range(256)]
MUL11 = [_mul(i, 11) for i in range(256)]
MUL13 = [_mul(i, 13) for i in range(256)]
MUL14 = [_mul(i, 14) for i in range(256)]


def _expand_key(key):
    w = list(key)
    rcon = 1
    for i in range(4, 44):
        t = w[(i - 1) * 4:i * 4]
        if i % 4 == 0:
            t = [SBOX[t[1]] ^ rcon, SBOX[t[2]], SBOX[t[3]], SBOX[t[0]]]
            rcon = _xt(rcon)
        w += [w[(i - 4) * 4 + j] ^ t[j] for j in range(4)]
    return [w[r * 16:(r + 1) * 16] for r in range(11)]


def _decrypt_block(rk, block):
    s = [block[i] ^ rk[10][i] for i in range(16)]
    for rnd in range(9, -1, -1):
        # inverse shift rows (state is column-major: s[c*4 + r])
        s = [s[((c - r) % 4) * 4 + r] for c in range(4) for r in range(4)]
        s = [INV_SBOX[b] for b in s]
        s = [s[i] ^ rk[rnd][i] for i in range(16)]
        if rnd:
            o = []
            for c in range(4):
                a0, a1, a2, a3 = s[c * 4:c * 4 + 4]
                o += [MUL14[a0] ^ MUL11[a1] ^ MUL13[a2] ^ MUL9[a3],
                      MUL9[a0] ^ MUL14[a1] ^ MUL11[a2] ^ MUL13[a3],
                      MUL13[a0] ^ MUL9[a1] ^ MUL14[a2] ^ MUL11[a3],
                      MUL11[a0] ^ MUL13[a1] ^ MUL9[a2] ^ MUL14[a3]]
            s = o
    return bytes(s)


def aes128_cbc_decrypt(key, iv, data):
    assert len(data) % 16 == 0
    rk = _expand_key(key)
    out = bytearray()
    prev = iv
    for i in range(0, len(data), 16):
        blk = data[i:i + 16]
        out += bytes(a ^ b for a, b in zip(_decrypt_block(rk, blk), prev))
        prev = blk
    return bytes(out)

# ---------------------------------------------------------------- data.bin


def parse_databin(raw):
    if len(raw) < HEADER_SIZE + BK_SIZE:
        raise ValueError("too short for a Wii data.bin (%d bytes)" % len(raw))
    hdr = aes128_cbc_decrypt(SD_KEY, SD_IV, raw[:HEADER_SIZE])
    title_id = hdr[0:8]
    banner_size = struct.unpack(">I", hdr[8:12])[0]
    md5_stored = hdr[0x0E:0x1E]
    md5_calc = hashlib.md5(hdr[:0x0E] + MD5_BLANKER + hdr[0x1E:]).digest()
    banner = hdr[0x20:0x20 + banner_size]
    if banner[:4] != b"WIBN":
        raise ValueError("no WIBN banner after decryption: not a data.bin, or not SD-key encrypted")
    title = banner[0x20:0x60].decode("utf-16-be", "replace").split("\0")[0]
    subtitle = banner[0x60:0xA0].decode("utf-16-be", "replace").split("\0")[0]
    bk = raw[HEADER_SIZE:HEADER_SIZE + BK_SIZE]
    bk_size, bk_magic = struct.unpack(">II", bk[0:8])
    if bk_size != 0x70 or bk_magic != 0x426B0001:
        raise ValueError("no Bk header at 0x%X" % HEADER_SIZE)
    ng_id, n_files, files_size = struct.unpack(">III", bk[8:20])
    total_size = struct.unpack(">I", bk[0x1C:0x20])[0]
    files = []
    pos = HEADER_SIZE + BK_SIZE
    for _ in range(n_files):
        fh = raw[pos:pos + 0x80]
        magic, size = struct.unpack(">II", fh[0:8])
        if magic != FILE_MAGIC:
            raise ValueError("bad file header magic at 0x%X" % pos)
        perm, attr, ftype = fh[8], fh[9], fh[10]
        name = fh[0x0B:0x50].split(b"\0")[0].decode("ascii", "replace")
        iv = fh[0x50:0x60]
        padded = (size + 63) & ~63
        data = b""
        if ftype == 1:
            data = aes128_cbc_decrypt(SD_KEY, iv, raw[pos + 0x80:pos + 0x80 + padded])[:size]
        files.append({"name": name, "type": ftype, "size": size, "perm": perm, "attr": attr,
                      "data": data})
        pos += 0x80 + padded
    return {"title_id": title_id, "game_id": title_id[4:].decode("ascii", "replace"),
            "banner_size": banner_size, "md5_ok": md5_stored == md5_calc,
            "title": title, "subtitle": subtitle, "ng_id": ng_id, "n_files": n_files,
            "files_size": files_size, "total_size": total_size, "files": files,
            "trailer": len(raw) - pos}

# ---------------------------------------------------------------- per platform


def wordswap(b):
    return b"".join(b[i:i + 4][::-1] for i in range(0, len(b), 4))


def format_mempak():
    """A blank Controller Pak as mupen64plus-core's format_mempak writes it, serial all zero
    (what Mupen64Plus-Next writes on macOS, see n64/NOTES.md)."""
    pak = bytearray(0x8000)
    idb = bytearray(32)
    idb[0x18:0x1C] = b"\x00\x01\x01\x00"          # device 0x0001, 1 bank, version 0
    s = sum(struct.unpack(">14H", idb[:28])) & 0xFFFF
    idb[0x1C:0x20] = struct.pack(">HH", s, (0xFFF2 - s) & 0xFFFF)
    for off in (0x20, 0x60, 0x80, 0xC0):
        pak[off:off + 32] = idb
    inode = bytearray(256)
    for i in range(5, 128):
        inode[i * 2:i * 2 + 2] = b"\x00\x03"
    inode[1] = sum(inode[10:]) & 0xFF
    pak[0x100:0x200] = inode
    pak[0x200:0x300] = inode
    return bytes(pak)


def n64_srm(eeprom=None, sram=None, flash=None, paks=None):
    """The libretro cores' 296960-byte save. sram/flash already in the stored (swapped) order."""
    srm = bytearray(b"\xFF" * 0x48800)
    blank = format_mempak()
    for i in range(4):
        p = (paks or {}).get(i, blank)
        srm[0x800 + i * 0x8000:0x800 + (i + 1) * 0x8000] = p
    if eeprom is not None:
        srm[0:len(eeprom)] = eeprom
    if sram is not None:
        srm[0x20800:0x20800 + len(sram)] = sram
    if flash is not None:
        srm[0x28800:0x28800 + len(flash)] = flash
    return bytes(srm)


def convert_n64(name, data):
    """vcromclaim n64save.convert / save-file-converter ConvertFromN64: type by size."""
    n = len(data)
    if n in (4 * 1024, 16 * 1024) or n <= 0x800:
        eep = data[:0x800]
        return {"kind": "eeprom", "eep": eep, "srm": n64_srm(eeprom=eep),
                "how": "%s (%d bytes, EEPROM): first 0x%X bytes at 0x0 of the .srm" % (name, n, len(eep))}
    if n in (32 * 1024, 48 * 1024):
        sram = wordswap(data[:0x8000])
        return {"kind": "sram", "sra": sram, "srm": n64_srm(sram=sram),
                "how": "%s (%d bytes, SRAM): first 0x8000 bytes, 32-bit words reversed, at 0x20800" % (name, n)}
    if n in (128 * 1024, 256 * 1024):
        fla = wordswap(data[:0x20000])
        return {"kind": "flash", "fla": fla, "srm": n64_srm(flash=fla),
                "how": "%s (%d bytes, FlashRAM): first 0x20000 bytes, 32-bit words reversed, at 0x28800" % (name, n)}
    raise ValueError("unknown N64 VC save size %d" % n)


def unmangle_pce(data):
    """tgsave.py unmangle_tgsave / ConvertFromPcEngine.js."""
    if data[:4] != b"$PCE":
        raise ValueError("no $PCE magic")
    body = data[16:-16]
    prev = bytes(~b & 0xFF for b in data[4:8])
    out = bytearray()
    for i in range(0, len(body), 4):
        blk = body[i:i + 4]
        out += bytes(a ^ (~b & 0xFF) for a, b in zip(blk, prev))
        prev = blk
    if out[:4] != b"HUBM":
        raise ValueError("decoded BRAM has no HUBM")
    if any(out[0x800:]):
        raise ValueError("BRAM holds data past 2 KiB")
    bram = bytearray(out[:0x800])
    bram[4:6] = struct.pack("<H", 0x8800)
    return bytes(out), bytes(bram)


def platform_of(files):
    names = [f["name"] for f in files]
    if any(n.startswith(("EEP_", "RAM_")) for n in names):
        return "n64"
    if "pcengine.bup" in names:
        return "pcenginecd"
    if "savedata.bin" in names:
        return "snes"
    return None


def sha1(b):
    return hashlib.sha1(b).hexdigest()


def main(argv):
    if len(argv) < 2 or argv[0] not in ("info", "extract", "convert"):
        sys.exit(__doc__)
    raw = open(argv[1], "rb").read()
    d = parse_databin(raw)
    files = d["files"]
    if argv[0] == "info":
        info = {k: v for k, v in d.items() if k not in ("files", "title_id")}
        info["title_id"] = d["title_id"].hex()
        info["files"] = [{k: (v if k != "data" else sha1(v)) for k, v in f.items()} for f in files]
        info["platform"] = platform_of(files)
        print(json.dumps(info, indent=1, ensure_ascii=False))
        return
    out = argv[2]
    os.makedirs(out, exist_ok=True)
    if argv[0] == "extract":
        for f in files:
            if f["type"] == 1:
                safe = f["name"].replace("/", "_")
                open(os.path.join(out, safe), "wb").write(f["data"])
                print(safe, f["size"], sha1(f["data"]))
        return
    plat = platform_of(files)
    written = {}
    if plat == "n64":
        f = next(f for f in files if f["name"].startswith(("EEP_", "RAM_")))
        r = convert_n64(f["name"], f["data"])
        for ext in ("srm", "eep", "sra", "fla"):
            if ext in r:
                p = os.path.join(out, "save." + ext)
                open(p, "wb").write(r[ext])
                written[os.path.basename(p)] = {"size": len(r[ext]), "sha1": sha1(r[ext])}
        how = r["how"]
    elif plat == "snes":
        f = next(f for f in files if f["name"] == "savedata.bin")
        p = os.path.join(out, "save.srm")
        open(p, "wb").write(f["data"])
        written["save.srm"] = {"size": f["size"], "sha1": sha1(f["data"])}
        how = "savedata.bin (%d bytes): the SRAM, as is" % f["size"]
    elif plat == "pcenginecd":
        f = next(f for f in files if f["name"] == "pcengine.bup")
        full, bram = unmangle_pce(f["data"])
        p = os.path.join(out, "save.srm")
        open(p, "wb").write(bram)
        written["save.srm"] = {"size": len(bram), "sha1": sha1(bram)}
        how = "pcengine.bup: unmangled 8 KiB BRAM, first 2 KiB, end pointer 0x8800"
    else:
        sys.exit("no VC save file found in %s" % [f["name"] for f in files])
    print(json.dumps({"platform": plat, "game_id": d["game_id"], "title": d["title"],
                      "how": how, "files": written}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
