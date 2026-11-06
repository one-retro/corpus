#!/usr/bin/env python3
"""GameCube memory card saves from GameFAQs: read them, and write what Dolphin loads.

    python3 -I gc-gci.py info FILE                 describe a .gci or MaxDrive .sav (JSON)
    python3 -I gc-gci.py gci FILE OUT.gci          write the plain GCI (a .gci is copied as is,
                                                   a MaxDrive .sav is unwrapped)
    python3 -I gc-gci.py place FILE CARD_DIR       write the plain GCI into a Dolphin GCI folder
                                                   (GC/<region>/Card A/) under the name Dolphin
                                                   itself gives it; prints the path
    python3 -I gc-gci.py card FILE BLANK.raw OUT.raw
                                                   copy a blank formatted card (e.g. from
                                                   `1saves new gc`) and store the save in it,
                                                   as a card manager would: for tools that read
                                                   whole cards (.raw) but not loose saves

Formats (layouts as Dolphin reads them, Source/Core/Core/HW/GCMemcard/GCMemcardUtils.cpp):

  .gci   the card's 64-byte directory entry (DEntry), then the save's 8 KiB blocks. Written by
         Dolphin, the Datel/Codejunkies "USB Memory Adapter" software and most card managers.
  .sav   MaxDrive (Datel's PC software): a 0x80-byte header ("DATELGC_SAVE", then a title and
         a description), then the DEntry with some bytes swapped, then the blocks. Dolphin's
         reader swaps bytes 0x06/0x07 (unused byte and banner/icon flags) and every byte pair
         from 0x2C to 0x3F (image offset, icon formats, animation speeds, permissions, copy
         counter, first block, block count, unused, comment offset) back.

DEntry fields (big-endian): 0x00 game code[4], 0x04 maker[2], 0x06 unused (0xFF), 0x07 banner/icon
flags, 0x08 file name[32], 0x28 modified time (s since 2000-01-01), 0x2C image offset,
0x30 icon formats, 0x32 animation speeds, 0x34 permissions, 0x35 copy counter, 0x36 first block,
0x38 block count, 0x3A 0xFFFF, 0x3C comment offset.

Standard library only. Reads untrusted files: nothing in them is executed or used as a path
except the card file name, which is escaped as Dolphin escapes it.
"""
import datetime
import hashlib
import json
import os
import struct
import sys

DENTRY = 0x40
BLOCK = 0x2000
MAXDRIVE_HEADER = 0x80
MAXDRIVE_MAGIC = b"DATELGC_SAVE"


def unswap_maxdrive(d):
    d = bytearray(d)
    d[0x06], d[0x07] = d[0x07], d[0x06]
    for i in range(0x2C, 0x40, 2):
        d[i], d[i + 1] = d[i + 1], d[i]
    return bytes(d)


def split(data):
    """Return (kind, maxdrive_header or None, dentry, payload) for a .gci or MaxDrive .sav."""
    if data[:len(MAXDRIVE_MAGIC)] == MAXDRIVE_MAGIC:
        if len(data) < MAXDRIVE_HEADER + DENTRY:
            raise ValueError("MaxDrive file shorter than its header")
        head = data[:MAXDRIVE_HEADER]
        dentry = unswap_maxdrive(data[MAXDRIVE_HEADER:MAXDRIVE_HEADER + DENTRY])
        return "maxdrive", head, dentry, data[MAXDRIVE_HEADER + DENTRY:]
    if len(data) < DENTRY:
        raise ValueError("shorter than a directory entry")
    return "gci", None, data[:DENTRY], data[DENTRY:]


def cstr(b):
    return b.split(b"\0", 1)[0].decode("latin-1")


def parse_dentry(d):
    (img_off, icon_fmt, anim, perm, copies, first, blocks, pad, comment_off) = struct.unpack(
        ">IHHBBHHHI", d[0x2C:0x40])
    mtime = struct.unpack(">I", d[0x28:0x2C])[0]
    return {
        "game_code": d[0:4].decode("latin-1"),
        "maker": d[4:6].decode("latin-1"),
        "unused": d[6],
        "banner_flags": d[7],
        "file_name": cstr(d[8:0x28]),
        "modified": (datetime.datetime(2000, 1, 1) + datetime.timedelta(seconds=mtime)).isoformat(),
        "modified_raw": mtime,
        "image_offset": img_off,
        "icon_formats": icon_fmt,
        "anim_speeds": anim,
        "permissions": perm,
        "copy_counter": copies,
        "first_block": first,
        "block_count": blocks,
        "pad": pad,
        "comment_offset": comment_off,
    }


def comments(dentry, payload):
    off = struct.unpack(">I", dentry[0x3C:0x40])[0]
    if off == 0xFFFFFFFF or off + 64 > len(payload):
        return None
    return [cstr(payload[off:off + 32]), cstr(payload[off + 32:off + 64])]


def escape(name):
    """Common::EscapeFileName: control characters and "*/:<>?\\| become __xx__."""
    out = []
    for ch in name:
        if ord(ch) < 0x20 or ch in '"*/:<>?\\|':
            out.append("__%02x__" % ord(ch))
        else:
            out.append(ch)
    return "".join(out)


def dolphin_name(dentry):
    """GCMemcardUtils GenerateFilename: <maker>-<game code>-<file name>.gci."""
    d = parse_dentry(dentry)
    return escape("%s-%s-%s" % (d["maker"], d["game_code"], d["file_name"])) + ".gci"


def info(path):
    data = open(path, "rb").read()
    kind, head, dentry, payload = split(data)
    d = parse_dentry(dentry)
    out = {
        "file": os.path.basename(path),
        "size": len(data),
        "sha1": hashlib.sha1(data).hexdigest(),
        "container": kind,
        "dentry": d,
        "payload_size": len(payload),
        "payload_matches_block_count": len(payload) == d["block_count"] * BLOCK,
        "comments": comments(dentry, payload),
        "dolphin_name": dolphin_name(dentry),
    }
    if head is not None:
        out["maxdrive_title"] = cstr(head[0x10:0x48]).strip()
        out["maxdrive_description"] = cstr(head[0x48:0x80]).strip()
    return out


def gci_bytes(path):
    data = open(path, "rb").read()
    kind, head, dentry, payload = split(data)
    d = parse_dentry(dentry)
    if len(payload) != d["block_count"] * BLOCK:
        raise ValueError("payload is %d bytes, block count says %d" % (len(payload), d["block_count"] * BLOCK))
    return dentry + payload


def checksums(buf):
    """Dolphin's calc_checksumsBE: sum of the big-endian u16 words, and sum of their inverses."""
    s = i = 0
    for (w,) in struct.iter_unpack(">H", buf):
        s = (s + w) & 0xFFFF
        i = (i + (w ^ 0xFFFF)) & 0xFFFF
    if s == 0xFFFF:
        s = 0
    if i == 0xFFFF:
        i = 0
    return s, i


def store_in_card(gci, blank):
    """Put one save into a blank card: directory entry in the first free slot, blocks from 5 on,
    the block allocation table chained, update counters raised, both copies rewritten
    (layout: Dolphin's GCMemcard.h: header 0, directory 1/2, BAT 3/4, data from block 5)."""
    card = bytearray(blank)
    nblocks = len(card) // BLOCK
    dentry, payload = bytearray(gci[:DENTRY]), gci[DENTRY:]
    count = len(payload) // BLOCK
    first = 5
    if first + count > nblocks:
        raise ValueError("card too small")
    struct.pack_into(">H", dentry, 0x36, first)
    # directory: blocks 1 and 2, 127 entries, update counter at 0x1FFA, checksums at 0x1FFC
    d = bytearray(card[BLOCK:2 * BLOCK])
    for slot in range(127):
        if d[slot * DENTRY:slot * DENTRY + 4] == b"\xff\xff\xff\xff":
            break
    else:
        raise ValueError("directory full")
    d[slot * DENTRY:(slot + 1) * DENTRY] = dentry
    upd = (struct.unpack(">H", d[0x1FFA:0x1FFC])[0] + 1) & 0xFFFF
    struct.pack_into(">H", d, 0x1FFA, upd)
    struct.pack_into(">HH", d, 0x1FFC, *checksums(d[:0x1FFC]))
    # BAT: blocks 3 and 4: csum, inv, update counter, free blocks, last allocated, map[block-5]
    b = bytearray(card[3 * BLOCK:4 * BLOCK])
    for k in range(count):
        nxt = 0xFFFF if k == count - 1 else first + k + 1
        struct.pack_into(">H", b, 0x0A + 2 * (first + k - 5), nxt)
    upd_b = (struct.unpack(">H", b[4:6])[0] + 1) & 0xFFFF
    free = struct.unpack(">H", b[6:8])[0] - count
    struct.pack_into(">HHH", b, 4, upd_b, free, first + count - 1)
    struct.pack_into(">HH", b, 0, *checksums(b[4:]))
    card[BLOCK:2 * BLOCK] = d
    card[2 * BLOCK:3 * BLOCK] = d
    card[3 * BLOCK:4 * BLOCK] = b
    card[4 * BLOCK:5 * BLOCK] = b
    card[first * BLOCK:(first + count) * BLOCK] = payload
    return bytes(card)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "card" and len(sys.argv) > 4:
        out = store_in_card(gci_bytes(sys.argv[2]), open(sys.argv[3], "rb").read())
        with open(sys.argv[4], "wb") as f:
            f.write(out)
        print(json.dumps({"out": sys.argv[4], "size": len(out), "sha1": hashlib.sha1(out).hexdigest()}))
        return
    if cmd == "info":
        print(json.dumps(info(sys.argv[2]), indent=1))
    elif cmd == "gci":
        out = gci_bytes(sys.argv[2])
        with open(sys.argv[3], "wb") as f:
            f.write(out)
        print(json.dumps({"out": sys.argv[3], "size": len(out), "sha1": hashlib.sha1(out).hexdigest()}))
    elif cmd == "place":
        out = gci_bytes(sys.argv[2])
        os.makedirs(sys.argv[3], exist_ok=True)
        dest = os.path.join(sys.argv[3], dolphin_name(out[:DENTRY]))
        with open(dest, "wb") as f:
            f.write(out)
        print(dest)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
