#!/usr/bin/env python3
"""Turn a downloaded PlayStation save into the raw 128 KiB memory card the cores load.

    psx-card.py OUT.mcr INPUT [INPUT...]     write a raw card
    psx-card.py --ls FILE                     list the saves on a card (or what INPUT holds) as JSON

Every runnable libretro PS1 core here (Beetle PSX / HW, PCSX-ReARMed, SwanStation) loads card 1
as a raw 131072-byte image (`<content>.srm`), so this always writes that.

One INPUT that is a whole card (any container) is unwrapped, its card bytes copied unchanged:

    raw card        131072 bytes, as is (DuckStation ImportCardGME: "some gme files are raw files
                    in disguise")
    DexDrive .gme   "123-456-STD", a 3904-byte (0xF40) header, then the card. A file shorter than
                    header + card is padded with zeroes (DuckStation ImportCardGME; MemcardRex reads
                    into a zeroed 134976-byte buffer, the same result); bytes past the card are
                    ignored. A 134976-byte file whose header is blank but has "MC" at 3904 is a
                    .gme "with corrupted header" (MemcardRex OpenMemoryCard).
    VGS             "VgsM", a 64-byte header, then the card (Connectix Virtual Game Station .mem/.vgs)
    VMP             "\\0PMV", a 128-byte header, then the card (PSP/PS3 virtual card, SCEVMC0.VMP)

Otherwise every INPUT is a single save, put on a freshly formatted card in order, the way
MemcardRex's OpenSingleSave + SetSaveBytes do it (ShendoXT/memcardrex, MemcardRex.Core/ps1card.cs):

    .psv (PS3)      "\\0VSP", byte 0x3C = 1 (a PS1 save), the 20-byte save name at 0x64, the save's
                    blocks from 0x84
    .mcs            a 128-byte directory frame ("Q"), then the blocks
    raw blocks      starts "SC" (the save's title frame); the directory name is not in the file, so
                    it is taken from the file name, its first 20 bytes (MemcardRex; DuckStation's
                    ImportRawSave uses the name without extension)

The fresh card is MemcardRex's: "MC" header frame (checksum 0x0E) and its copy in frame 63,
15 free directory frames (0xA0, next FFFF), 20 reserved frames (FF FF FF FF, next FFFF), every
other byte 0x00. A save gets the first free blocks: 0x51 on its first, 0x52 middle, 0x53 last,
next-block pointers chained, size in bytes in the first frame, each frame's XOR checksum at 0x7F.

Standard library only; run with python3 -I.
"""
import json
import os
import sys
import unicodedata

FRAME = 128
BLOCK = 8192
CARD = 131072
GME_HEADER = 0xF40  # 3904


def frame_xor(fr):
    x = 0
    for b in fr[:127]:
        x ^= b
    return x


def unwrap_card(data):
    """(card bytes, container description) if data is a whole card, else None."""
    n = len(data)
    if data[:11] == b"123-456-STD":
        body = data[GME_HEADER:GME_HEADER + CARD]
        desc = "DexDrive .gme: 3904-byte header + card"
        if len(body) < CARD:
            desc += f" (only {len(body)} card bytes, zero-padded to {CARD})"
            body = body + bytes(CARD - len(body))
        elif n > GME_HEADER + CARD:
            desc += f" (+{n - GME_HEADER - CARD} trailing bytes, ignored)"
        return bytes(body), desc
    if data[:4] == b"VgsM" and n == 64 + CARD:
        return bytes(data[64:]), "VGS (Connectix): 64-byte header + card"
    if data[:4] == b"\x00PMV" and n >= 128 + CARD:
        return bytes(data[128:128 + CARD]), "VMP (PSP/PS3 virtual card): 128-byte header + card"
    if n == CARD:
        return bytes(data), "raw card" + ("" if data[:2] == b"MC" else " (no MC header)")
    if n == GME_HEADER + CARD and data[GME_HEADER:GME_HEADER + 2] == b"MC":
        return bytes(data[GME_HEADER:]), "DexDrive .gme layout with a blank header (no 123-456-STD)"
    return None


def single_save(data, path):
    """(directory frame, blocks, description) for a single-save file, following MemcardRex."""
    if data[:4] == b"\x00VSP":
        if len(data) < 0x84 + BLOCK or data[0x3C] != 1:
            raise ValueError("a .psv that is not a PS1 save")
        hdr = bytearray(FRAME)
        hdr[0] = 0x51
        hdr[10:30] = data[0x64:0x64 + 20]
        return hdr, bytes(data[0x84:]), ".psv (PS3 export): 0x84-byte header + save"
    if data[:1] == b"Q" and (len(data) - FRAME) % BLOCK == 0:
        return bytearray(data[:FRAME]), bytes(data[FRAME:]), ".mcs: directory frame + save"
    if data[:2] in (b"SC", b"sc") and len(data) % BLOCK == 0:
        hdr = bytearray(FRAME)
        hdr[0] = 0x51
        name = os.path.basename(path).encode("latin-1", "replace")[:20]
        hdr[10:10 + len(name)] = name
        return hdr, bytes(data), "raw save blocks (no directory frame; name from the file name)"
    raise ValueError("not a PS1 card or single save")


def fresh_card():
    card = bytearray(CARD)
    card[0:2] = b"MC"
    card[127] = 0x0E
    card[63 * FRAME:63 * FRAME + 2] = b"MC"
    card[63 * FRAME + 127] = 0x0E
    for s in range(15):
        o = (1 + s) * FRAME
        card[o] = 0xA0
        card[o + 8] = card[o + 9] = 0xFF
        card[o + 127] = frame_xor(card[o:o + FRAME])
    for i in range(20):
        o = 2048 + i * FRAME
        card[o:o + 4] = b"\xff\xff\xff\xff"
        card[o + 8] = card[o + 9] = 0xFF
    return card


def add_save(card, hdr, blocks):
    count = len(blocks) // BLOCK
    if count < 1 or count > 15:
        raise ValueError(f"a save of {len(blocks)} bytes")
    free = [s for s in range(15) if card[(1 + s) * FRAME] == 0xA0][:count]
    if len(free) < count:
        raise ValueError("not enough free blocks")
    first = (1 + free[0]) * FRAME
    card[first:first + FRAME] = hdr
    size = count * BLOCK
    card[first + 4:first + 8] = size.to_bytes(4, "little")
    for i, s in enumerate(free):
        card[(1 + s) * BLOCK:(2 + s) * BLOCK] = blocks[i * BLOCK:(i + 1) * BLOCK]
    for i, s in enumerate(free[:-1]):
        o = (1 + s) * FRAME
        card[o] = 0x52
        card[o + 8], card[o + 9] = free[i + 1], 0
    o = (1 + free[-1]) * FRAME
    card[o] = 0x53
    card[o + 8] = card[o + 9] = 0xFF
    card[first] = 0x51
    for s in free:
        o = (1 + s) * FRAME
        card[o + 127] = frame_xor(card[o:o + FRAME])


def title(block):
    raw = block[4:68].split(b"\x00")[0]
    try:
        t = raw.decode("shift_jis")
    except UnicodeDecodeError:
        t = raw.decode("shift_jis", "replace")
    return " ".join(unicodedata.normalize("NFKC", t).split())


def listing(card):
    """The saves on a raw card: first block, state, name, size, blocks, title."""
    out = []
    for s in range(15):
        fr = card[(1 + s) * FRAME:(2 + s) * FRAME]
        st = fr[0]
        if st not in (0x51, 0xA1):
            continue
        chain, nxt, seen = [s], int.from_bytes(fr[8:10], "little"), {s}
        while nxt != 0xFFFF and nxt < 15 and nxt not in seen:
            chain.append(nxt)
            seen.add(nxt)
            f2 = card[(1 + nxt) * FRAME:(2 + nxt) * FRAME]
            nxt = int.from_bytes(f2[8:10], "little")
        name = fr[10:30].split(b"\x00")[0].decode("latin-1")
        out.append({
            "block": s + 1, "deleted": st == 0xA1, "name": name,
            "size": int.from_bytes(fr[4:8], "little"), "blocks": len(chain),
            "checksum_ok": frame_xor(fr) == fr[127],
            "title": title(card[(1 + s) * BLOCK:(2 + s) * BLOCK]),
        })
    return out


def convert(inputs):
    datas = [open(p, "rb").read() for p in inputs]
    if len(inputs) == 1:
        got = unwrap_card(datas[0])
        if got:
            return got[0], got[1]
    card = fresh_card()
    descs = []
    for p, d in zip(inputs, datas):
        hdr, blocks, desc = single_save(d, p)
        add_save(card, hdr, blocks)
        descs.append(desc)
    return bytes(card), "; ".join(sorted(set(descs))) + f", {len(inputs)} save(s) put on a fresh card"


def main(argv):
    if len(argv) >= 2 and argv[0] == "--ls":
        card, desc = convert(argv[1:])
        print(json.dumps({"container": desc, "saves": listing(card)}, ensure_ascii=False, indent=1))
        return 0
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    out, inputs = argv[0], argv[1:]
    try:
        card, desc = convert(inputs)
    except ValueError as e:
        print(f"psx-card: {e}", file=sys.stderr)
        return 1
    with open(out, "wb") as f:
        f.write(card)
    print(desc)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
