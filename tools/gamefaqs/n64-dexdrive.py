#!/usr/bin/env python3
"""GameFAQs "Nintendo 64 DexDrive Save" files -> what the N64 cores in this corpus load.

    n64-dexdrive.py info FILE
    n64-dexdrive.py convert FILE OUTDIR [--note NAME] [--raw eeprom|sram-swapped] [--keep-id]

What such a file can be, from its bytes:

  DexDrive .n64   "123-456-STD", a 0x40-byte header, 16 comments of 256 bytes (one per
                  note), then the 32 KiB Controller Pak (bryc/mpkedit wiki "DexDrive .N64
                  format"; save-file-converter N64/DexDrive.js). Some files stop after the last
                  used page; the pak is padded with 00 to 32 KiB. Some have an all-zero
                  0x1040-byte header with no magic (save-file-converter accepts these too).
  A cart save on the pak
                  A note with game code 3B AD D1 E5 and publisher FA DE is a cartridge save
                  copied onto the pak by a GameShark / Action Replay ("Memory Card Manager",
                  GamePak -> Controller Pak; save-file-converter GameSerialCodeUtil.js).
                  - EEPROM: the chip's bytes, console order. The device drops trailing pages
                    of padding; they are restored with 00 to 512 or 2048 bytes
                    (save-file-converter Mempack.js padCartSave).
                  - SRAM / FlashRAM: a 4-byte little-endian length (0x8000 / 0x20000), then
                    Haruhiko Okumura's LZARI stream (LZARI.C, 1989: N=4096, F=60, THRESHOLD=2,
                    15-bit arithmetic coder; the codec mymcplus uses for Max Drive saves);
                    it decodes to the chip in console order.
  The pak's ID block (page 0: 0x20, copies at 0x60, 0x80, 0xC0) carries two checksums over its
                  first 28 bytes: the sum of the 14 big-endian words, and 0xFFF2 minus that sum
                  (libultra __osIdCheckSum). Paks formatted by DexPlorer have 0xFFFE minus the sum
                  in every copy, and games then report a damaged Controller Pak. When no copy is
                  valid, the converter rewrites the two checksums of each copy and nothing else
                  (save-file-converter rebuilds the whole pak for the same reason); --keep-id
                  leaves the pak exactly as downloaded.
  A raw chip      no container: --raw eeprom (console order) or --raw sram-swapped (32-bit
                  words reversed, as Project64 and Mupen64Plus write .sra; a file Project64
                  wrote stops after the last byte the game wrote, and is padded with FF).

Output in OUTDIR:
  save.srm   296960 bytes for Mupen64Plus-Next and ParaLLEl N64: EEPROM at 0x0, Controller
             Paks 1-4 at 0x800 + n*0x8000, SRAM at 0x20800, FlashRAM at 0x28800 (n64/NOTES.md).
             Pak 1 is the file's pak as is; paks 2-4 are blank, formatted as
             mupen64plus-core's format_mempak does with an all-zero serial; chip regions the
             file does not fill are FF, as the cores start them. SRAM / FlashRAM are stored
             with each 32-bit word reversed, EEPROM and paks in console order.
  save.mpk   131072 bytes, standalone Mupen64Plus's four paks (same paks as above).
  save.eep / save.sra / save.fla   standalone Mupen64Plus's chip file (same bytes as the
             .srm region; .eep 512 or 2048 bytes).

Standard library only. Run with python3 -I.
"""

import hashlib
import json
import os
import struct
import sys

MAGIC = b"123-456-STD"
HDR = 0x1040
PAK = 0x8000
GS_CODE = bytes.fromhex("3badd1e5")
GS_PUB = bytes.fromhex("fade")

# N64 note-name characters (libultra font)
_CH = {0x00: "", 0x0F: " "}
_CH.update({0x10 + i: chr(48 + i) for i in range(10)})
_CH.update({0x1A + i: chr(65 + i) for i in range(26)})
_CH.update({0x34 + i: c for i, c in enumerate("!\"#'*+,-./:=?@")})


def n64_text(b):
    return "".join(_CH.get(x, "{%02x}" % x) for x in b).rstrip()

# ---------------------------------------------------------------- LZARI (Okumura, LZARI.C)


def lzari_decode(src, textsize):
    N, F, THRESHOLD = 4096, 60, 2
    M = 15
    Q1, Q2, Q3, Q4 = 1 << M, 2 << M, 3 << M, 4 << M
    MAX_CUM = Q1 - 1
    N_CHAR = 256 - THRESHOLD + F
    bitpos = [0]

    def getbit():
        p = bitpos[0]
        bitpos[0] = p + 1
        byte = src[p >> 3] if (p >> 3) < len(src) else 0xFF   # getc() at EOF gives -1
        return (byte >> (7 - (p & 7))) & 1

    char_to_sym = [0] * N_CHAR
    sym_to_char = [0] * (N_CHAR + 1)
    sym_freq = [0] * (N_CHAR + 1)
    sym_cum = [0] * (N_CHAR + 1)
    position_cum = [0] * (N + 1)
    for sym in range(N_CHAR, 0, -1):
        ch = sym - 1
        char_to_sym[ch] = sym
        sym_to_char[sym] = ch
        sym_freq[sym] = 1
        sym_cum[sym - 1] = sym_cum[sym] + sym_freq[sym]
    sym_freq[0] = 0
    for i in range(N, 0, -1):
        position_cum[i - 1] = position_cum[i] + 10000 // (i + 200)

    def update_model(sym):
        if sym_cum[0] >= MAX_CUM:
            c = 0
            for i in range(N_CHAR, 0, -1):
                sym_cum[i] = c
                sym_freq[i] = (sym_freq[i] + 1) >> 1
                c += sym_freq[i]
            sym_cum[0] = c
        i = sym
        while sym_freq[i] == sym_freq[i - 1]:
            i -= 1
        if i < sym:
            ch_i, ch_sym = sym_to_char[i], sym_to_char[sym]
            sym_to_char[i], sym_to_char[sym] = ch_sym, ch_i
            char_to_sym[ch_i], char_to_sym[ch_sym] = sym, i
        sym_freq[i] += 1
        for k in range(i):
            sym_cum[k] += 1

    st = {"low": 0, "high": Q4, "value": 0}
    for _ in range(M + 2):
        st["value"] = 2 * st["value"] + getbit()

    def renorm():
        low, high, value = st["low"], st["high"], st["value"]
        while True:
            if low >= Q2:
                value -= Q2; low -= Q2; high -= Q2
            elif low >= Q1 and high <= Q3:
                value -= Q1; low -= Q1; high -= Q1
            elif high > Q2:
                break
            low += low; high += high
            value = 2 * value + getbit()
        st["low"], st["high"], st["value"] = low, high, value

    def decode_char():
        rng = st["high"] - st["low"]
        x = ((st["value"] - st["low"] + 1) * sym_cum[0] - 1) // rng
        i, j = 1, N_CHAR
        while i < j:
            k = (i + j) // 2
            if sym_cum[k] > x:
                i = k + 1
            else:
                j = k
        sym = i
        low = st["low"]
        st["high"] = low + (rng * sym_cum[sym - 1]) // sym_cum[0]
        st["low"] = low + (rng * sym_cum[sym]) // sym_cum[0]
        renorm()
        ch = sym_to_char[sym]
        update_model(sym)
        return ch

    def decode_position():
        rng = st["high"] - st["low"]
        x = ((st["value"] - st["low"] + 1) * position_cum[0] - 1) // rng
        i, j = 1, N
        while i < j:
            k = (i + j) // 2
            if position_cum[k] > x:
                i = k + 1
            else:
                j = k
        pos = i - 1
        low = st["low"]
        st["high"] = low + (rng * position_cum[pos]) // position_cum[0]
        st["low"] = low + (rng * position_cum[pos + 1]) // position_cum[0]
        renorm()
        return pos

    text = bytearray(b" " * (N - F) + b"\0" * F)
    r = N - F
    out = bytearray()
    while len(out) < textsize:
        c = decode_char()
        if c < 256:
            out.append(c)
            text[r] = c
            r = (r + 1) & (N - 1)
        else:
            i = (r - decode_position() - 1) & (N - 1)
            for k in range(c - 255 + THRESHOLD):
                c2 = text[(i + k) & (N - 1)]
                out.append(c2)
                text[r] = c2
                r = (r + 1) & (N - 1)
    return bytes(out[:textsize]), (bitpos[0] + 7) // 8

# ---------------------------------------------------------------- Controller Pak


def id_checksums(idb):
    s = sum(struct.unpack(">14H", idb[:28])) & 0xFFFF
    return s, (0xFFF2 - s) & 0xFFFF


def format_mempak():
    """mupen64plus-core format_mempak, serial all zero."""
    pak = bytearray(PAK)
    idb = bytearray(32)
    idb[0x18:0x1C] = b"\x00\x01\x01\x00"
    idb[0x1C:0x20] = struct.pack(">HH", *id_checksums(idb))
    for off in (0x20, 0x60, 0x80, 0xC0):
        pak[off:off + 32] = idb
    inode = bytearray(256)
    for i in range(5, 128):
        inode[i * 2:i * 2 + 2] = b"\x00\x03"
    inode[1] = sum(inode[10:]) & 0xFF
    pak[0x100:0x200] = inode
    pak[0x200:0x300] = inode
    return bytes(pak)


def read_pak(pak):
    """Notes of a pak: list of dicts with their pages followed through the index table."""
    inode = pak[0x100:0x200]
    if (sum(inode[10:]) & 0xFF) != inode[1]:
        backup = pak[0x200:0x300]
        if (sum(backup[10:]) & 0xFF) == backup[1]:
            inode = backup
    notes = []
    for n in range(16):
        e = pak[0x300 + n * 32:0x320 + n * 32]
        if not any(e):
            continue
        start = struct.unpack(">H", e[6:8])[0]
        pages, pg = [], start
        while 5 <= pg < 128 and len(pages) < 128:
            pages.append(pg)
            nxt = struct.unpack(">H", inode[pg * 2:pg * 2 + 2])[0]
            if nxt == 1:
                break
            pg = nxt
        notes.append({"index": n, "code": e[0:4], "pub": e[4:6], "start": start, "status": e[8],
                      "ext": n64_text(e[12:16]), "name": n64_text(e[16:32]), "pages": pages,
                      "data": b"".join(pak[p * 256:(p + 1) * 256] for p in pages)})
    idb = pak[0x20:0x40]
    return {"id_block": idb.hex(), "id_checksum_ok": id_checksums(idb) == struct.unpack(">HH", idb[28:32]),
            "index_checksum_ok": (sum(pak[0x10A:0x200]) & 0xFF) == pak[0x101], "notes": notes}


def cart_save_of(note):
    """A GameShark / Action Replay cart-save note -> (chip, bytes in console order, how)."""
    d = note["data"]
    size = struct.unpack("<I", d[:4])[0]
    if size in (0x8000, 0x20000) and len(d) < size:
        out, used = lzari_decode(d[4:], size)
        chip = "sram" if size == 0x8000 else "flash"
        return chip, out, "LZARI, %d bytes -> %d" % (4 + used, size)
    for want in (512, 2048):
        if len(d) <= want:
            return "eeprom", d + b"\0" * (want - len(d)), "raw EEPROM, %d bytes%s" % (
                len(d), "" if len(d) == want else ", padded with 00 to %d" % want)
    raise ValueError("cart-save note of %d bytes is neither EEPROM nor LZARI" % len(d))


def wordswap(b):
    return b"".join(b[i:i + 4][::-1] for i in range(0, len(b), 4))


def parse(raw):
    """-> dict(kind, comments, pak) for a DexDrive file (with or without magic)."""
    if raw.startswith(MAGIC):
        kind = "dexdrive"
    elif len(raw) == HDR + PAK and not any(raw[:HDR]):
        kind = "dexdrive-blank-header"
    else:
        return None
    comments = []
    for i in range(16):
        c = raw[0x40 + i * 256:0x40 + (i + 1) * 256].split(b"\0")[0]
        comments.append(c.decode("latin-1").strip())
    body = raw[HDR:]
    return {"kind": kind, "comments": comments, "pak_bytes": len(body),
            "pak": body[:PAK] + b"\0" * max(0, PAK - len(body))}


def sha1(b):
    return hashlib.sha1(b).hexdigest()


def main(argv):
    if len(argv) < 2 or argv[0] not in ("info", "convert"):
        sys.exit(__doc__)
    raw = open(argv[1], "rb").read()
    opts = {}
    rest = argv[2:]
    while rest:
        if rest[0] == "--keep-id":
            opts["keep-id"] = True
            rest = rest[1:]
        elif rest[0] in ("--note", "--raw") and len(rest) > 1:
            opts[rest[0][2:]] = rest[1]
            rest = rest[2:]
        else:
            opts.setdefault("outdir", rest[0])
            rest = rest[1:]
    dd = parse(raw)
    if argv[0] == "info":
        if not dd:
            print(json.dumps({"kind": "not a DexDrive file", "size": len(raw)}))
            return
        p = read_pak(dd["pak"])
        info = {"kind": dd["kind"], "pak_bytes": dd["pak_bytes"],
                "comments": [c for c in dd["comments"] if c], "id_block": p["id_block"],
                "id_checksum_ok": p["id_checksum_ok"], "index_checksum_ok": p["index_checksum_ok"],
                "notes": []}
        for n in p["notes"]:
            e = {k: (v.hex() if isinstance(v, bytes) and k in ("code", "pub") else v)
                 for k, v in n.items() if k != "data"}
            if n["code"][:1].isalpha():
                e["code"] = n["code"].decode("ascii", "replace")
                e["pub"] = n["pub"].decode("ascii", "replace")
            e["bytes"] = len(n["data"])
            if n["code"] == GS_CODE and n["pub"] == GS_PUB and n["pages"]:
                chip, data, how = cart_save_of(n)
                e["cart_save"] = {"chip": chip, "how": how, "sha1": sha1(data)}
            info["notes"].append(e)
        print(json.dumps(info, indent=1))
        return
    out = opts.get("outdir")
    if not out:
        sys.exit("convert needs OUTDIR")
    os.makedirs(out, exist_ok=True)
    eeprom = sram = flash = None
    pak1 = None
    how = []
    if dd:
        pak1 = dd["pak"]
        how.append("%s: pak = the %d bytes after the 0x1040-byte header%s" % (
            dd["kind"], dd["pak_bytes"], "" if dd["pak_bytes"] == PAK else ", padded with 00 to 32 KiB"))
        ids = [pak1[o:o + 32] for o in (0x20, 0x60, 0x80, 0xC0)]
        if not any(id_checksums(i) == struct.unpack(">HH", i[28:32]) for i in ids):
            if opts.get("keep-id"):
                how.append("ID block checksums wrong in every copy, kept (--keep-id)")
            else:
                fixed = bytearray(pak1)
                for o in (0x20, 0x60, 0x80, 0xC0):
                    fixed[o + 28:o + 32] = struct.pack(">HH", *id_checksums(fixed[o:o + 28]))
                old = struct.unpack(">HH", pak1[0x3C:0x40])
                pak1 = bytes(fixed)
                how.append("ID block checksums %04X/%04X wrong in every copy, rewritten as %04X/%04X" % (
                    old + id_checksums(pak1[0x20:0x3C])))
        p = read_pak(pak1)
        gs = [n for n in p["notes"] if n["code"] == GS_CODE and n["pub"] == GS_PUB and n["pages"]]
        if "note" in opts:
            gs = [n for n in gs if n["name"] == opts["note"]]
        if len(gs) > 1:
            sys.exit("several cart-save notes (%s): pick one with --note" % ", ".join(n["name"] for n in gs))
        if gs:
            chip, data, h = cart_save_of(gs[0])
            how.append("cart-save note %r (GameShark 3BADD1E5/FADE): %s" % (gs[0]["name"], h))
            if chip == "eeprom":
                eeprom = data
            elif chip == "sram":
                sram = wordswap(data)
            else:
                flash = wordswap(data)
    elif opts.get("raw") == "eeprom":
        if len(raw) > 0x800:
            sys.exit("too big for EEPROM")
        eeprom = raw
        how.append("raw EEPROM, %d bytes, console order" % len(raw))
    elif opts.get("raw") == "sram-swapped":
        if len(raw) > PAK:
            sys.exit("too big for SRAM")
        sram = raw + b"\xFF" * (PAK - len(raw))
        how.append("raw SRAM, %d bytes, words already reversed%s" % (
            len(raw), "" if len(raw) == PAK else ", padded with FF to 32 KiB"))
    else:
        sys.exit("not a DexDrive file: say what it is with --raw eeprom|sram-swapped")
    blank = format_mempak()
    paks = [pak1 or blank, blank, blank, blank]
    srm = bytearray(b"\xFF" * 0x48800)
    for i, pk in enumerate(paks):
        srm[0x800 + i * PAK:0x800 + (i + 1) * PAK] = pk
    if eeprom is not None:
        srm[0:len(eeprom)] = eeprom
    if sram is not None:
        srm[0x20800:0x28800] = sram
    if flash is not None:
        srm[0x28800:0x48800] = flash
    files = {"save.srm": bytes(srm)}
    if pak1:
        files["save.mpk"] = b"".join(paks)
    if eeprom is not None:
        files["save.eep"] = eeprom
    if sram is not None:
        files["save.sra"] = sram
    if flash is not None:
        files["save.fla"] = flash
    written = {}
    for name, data in files.items():
        open(os.path.join(out, name), "wb").write(data)
        written[name] = {"size": len(data), "sha1": sha1(data)}
    print(json.dumps({"how": "; ".join(how), "files": written}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
