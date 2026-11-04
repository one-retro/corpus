#!/usr/bin/env python3
"""Crop, magnify and tile the PNGs `snes-harness` writes.

A console frame is 256x224, and its font is 8 pixels tall. At that size a 3 and
a 5 are one pixel apart and are genuinely easy to misread, which is how you end
up confidently recording a number the game never showed. Magnifying first is
not a nicety.

`tile` is the other half: when you are comparing twenty variants of one save,
twenty separate images is twenty chances to lose track of which was which. One
sheet, in a known order, is one look.

    python3 crop.py crop in.png out.png X Y W H [SCALE]
    python3 crop.py tile out.png COLS in1.png in2.png ...

Pure standard library, so it runs wherever Python does; no Pillow.
"""

import struct
import sys
import zlib


def read_png(path):
    """Return (width, height, rows) with rows as RGB bytes, one per scanline."""
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"{path}: not a PNG")
    pos, width, height, idat = 8, 0, 0, b""
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        tag = data[pos + 4 : pos + 8]
        body = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if tag == b"IHDR":
            width, height = struct.unpack(">II", body[:8])
            if body[8] != 8 or body[9] != 2:
                raise SystemExit(f"{path}: only 8-bit truecolour PNGs are handled")
        elif tag == b"IDAT":
            idat += body
    raw = zlib.decompress(idat)
    stride = width * 3
    rows, prev, off = [], bytearray(stride), 0

    def paeth(a, b, c):
        p = a + b - c
        pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
        return a if pa <= pb and pa <= pc else (b if pb <= pc else c)

    for _ in range(height):
        filt = raw[off]
        off += 1
        line = bytearray(raw[off : off + stride])
        off += stride
        if filt == 1:
            for x in range(3, stride):
                line[x] = (line[x] + line[x - 3]) & 255
        elif filt == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif filt == 3:
            for x in range(stride):
                left = line[x - 3] if x >= 3 else 0
                line[x] = (line[x] + (left + prev[x]) // 2) & 255
        elif filt == 4:
            for x in range(stride):
                left = line[x - 3] if x >= 3 else 0
                upleft = prev[x - 3] if x >= 3 else 0
                line[x] = (line[x] + paeth(left, prev[x], upleft)) & 255
        elif filt != 0:
            raise SystemExit(f"{path}: unknown row filter {filt}")
        rows.append(bytes(line))
        prev = line
    return width, height, rows


def write_png(path, width, height, rows):
    def chunk(tag, body):
        return (
            struct.pack(">I", len(body))
            + tag
            + body
            + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)
        )

    raw = b"".join(b"\x00" + r for r in rows)
    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    out += chunk(b"IDAT", zlib.compress(raw, 9))
    out += chunk(b"IEND", b"")
    open(path, "wb").write(out)


def crop(src, x0, y0, w, h, scale):
    """A magnified rectangle, clipped to what the image actually has."""
    width, height, rows = read_png(src)
    x0, y0 = max(0, x0), max(0, y0)
    w, h = min(w, width - x0), min(h, height - y0)
    if w <= 0 or h <= 0:
        raise SystemExit(f"{src}: the requested crop is outside a {width}x{height} image")
    out = []
    for y in range(y0, y0 + h):
        row = rows[y]
        line = b"".join(row[x * 3 : x * 3 + 3] * scale for x in range(x0, x0 + w))
        out.extend([line] * scale)
    return w * scale, h * scale, out


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    mode = sys.argv[1]

    if mode == "crop":
        if len(sys.argv) not in (8, 9):
            raise SystemExit("usage: crop.py crop in.png out.png X Y W H [SCALE]")
        src, dst = sys.argv[2], sys.argv[3]
        x0, y0, w, h = (int(v) for v in sys.argv[4:8])
        scale = int(sys.argv[8]) if len(sys.argv) == 9 else 3
        cw, ch, rows = crop(src, x0, y0, w, h, scale)
        write_png(dst, cw, ch, rows)
        print(f"{dst} {cw}x{ch}")

    elif mode == "tile":
        if len(sys.argv) < 5:
            raise SystemExit("usage: crop.py tile out.png COLS in1.png in2.png ...")
        dst, cols, srcs = sys.argv[2], int(sys.argv[3]), sys.argv[4:]
        cells = [read_png(s) for s in srcs]
        cw = max(c[0] for c in cells)
        ch = max(c[1] for c in cells)
        rows = []
        for start in range(0, len(cells), cols):
            band = cells[start : start + cols]
            for y in range(ch):
                line = b""
                for w, h, r in band:
                    # Pad a short or narrow cell with black rather than
                    # stretching it, so a sheet stays a grid you can index.
                    px = r[y] if y < h else b""
                    line += px + b"\x00" * (cw * 3 - len(px))
                rows.append(line + b"\x00" * ((cols - len(band)) * cw * 3))
            # A red rule between bands, so rows stay countable at a glance.
            rows.extend([b"\xff\x00\x00" * (cols * cw)] * 2)
        write_png(dst, cols * cw, len(rows), rows)
        print(f"{dst} {cols * cw}x{len(rows)} ({len(cells)} cells)")

    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
