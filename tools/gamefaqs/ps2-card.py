#!/usr/bin/env python3
"""ps2-card.py SAVE -o OUTDIR [--name DIR] [--time "YYYY-MM-DD HH:MM:SS"]

Puts one exported PS2 save on a freshly formatted memory card, the way the cores load it:

  OUTDIR/Mcd001.ps2        an 8 MiB PS2 memory card with ECC (512-byte pages + 16-byte spare,
                           8650752 bytes): what PCSX2, LRPS2, PCEE2 and ARMSX2 keep in their
                           memcards folder. Formatted and filled by mymcplus.
  OUTDIR/mc0/<DIR>/<file>  the same save as Play! keeps it (vfs/mc0/<save folder>/<files>: a
                           host folder per save, no card image).
  OUTDIR/info.json         what was read: the format (from the bytes), the save folder, its
                           files with sizes and SHA-1, the icon.sys title, and the outputs.

SAVE is read by its bytes, not its extension, with mymcplus (git.sr.ht/~thestr4ng3r/mymcplus,
the maintained mymc; GPL-3.0, on PyPI), the reference implementation for these containers:

  max  Max Drive / PowerSave ("Ps2PowerSave", LZARI-compressed files)
  cbs  CodeBreaker ("CFU\\0", RC4-encrypted zlib stream)
  sps  SharkPort / X-Port ("\\x0d\\0\\0\\0SharkPortSave"; both write the same format)
  psu  EMS Memory Adapter / uLaunchELF (raw directory entries + 1 KiB-padded files)
  psv  PS3 "Virtual Memory Card" export ("\\0VSP", PS2 type 2)
  card a raw PS2 card image ("Sony PS2 Memory Card Format"): copied as Mcd001.ps2 if it is
       already 8 MiB with ECC, otherwise its saves are moved onto a new card
  dir  a folder holding one save's files (a save copied off a card by a PC tool); the folder's
       name is the save's name unless --name gives it

mymcplus is not in the standard library: it is installed in a venv at .cache/venv-gamefaqs/
(`python3 -m venv .cache/venv-gamefaqs && .cache/venv-gamefaqs/bin/pip install mymcplus==3.0.5`),
and this script re-runs itself with that venv's python when `import mymcplus` fails.

Every timestamp mymcplus would take from the clock (the card's root directory when it formats,
Max Drive saves, which store no times, zeroed CodeBreaker times) is --time instead (default
2000-01-01 00:00:00, as a PS2 card stores it: JST), so the same input gives the same card.
"""

import argparse
import datetime
import hashlib
import importlib.metadata
import io
import json
import os
import shutil
import sys
import unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
VENV_PY = os.path.join(ROOT, ".cache", "venv-gamefaqs", "bin", "python3")

try:
    from mymcplus import ps2mc, ps2mc_dir
    from mymcplus.save import ps2save
except ImportError:
    if os.path.exists(VENV_PY) and os.path.realpath(sys.prefix) != os.path.realpath(os.path.dirname(os.path.dirname(VENV_PY))) \
            and not os.environ.get("PS2CARD_REEXEC"):
        os.environ["PS2CARD_REEXEC"] = "1"
        os.execv(VENV_PY, [VENV_PY, "-I", os.path.abspath(__file__)] + sys.argv[1:])
    sys.exit("mymcplus is needed: python3 -m venv .cache/venv-gamefaqs && "
             ".cache/venv-gamefaqs/bin/pip install mymcplus==3.0.5")

CARD_MAGIC = b"Sony PS2 Memory Card Format "
CARD_8M_ECC = 8650752
DF_FILE_MODE = ps2mc_dir.DF_RWX | ps2mc_dir.DF_FILE | ps2mc_dir.DF_0400 | ps2mc_dir.DF_EXISTS
DF_DIR_MODE = ps2mc_dir.DF_RWX | ps2mc_dir.DF_DIR | ps2mc_dir.DF_0400 | ps2mc_dir.DF_EXISTS


class Refused(Exception):
    """A name inside the save that is not safe to use as a host file name."""


def host_name(raw, what):
    """A directory or file name from inside a save (untrusted), checked before it is used as a
    host path: ASCII, not empty, not . or .., no /, \\ or NUL. Otherwise kept exactly."""
    try:
        name = raw.decode("ascii") if isinstance(raw, bytes) else raw
        name.encode("ascii")
    except (UnicodeDecodeError, UnicodeEncodeError):
        raise Refused(f"{what} {raw!r} is not ASCII")
    if name in ("", ".", "..") or any(c in name for c in "/\\\0"):
        raise Refused(f"{what} {raw!r} is not a safe file name")
    return name


def under(base, *parts):
    """os.path.join(base, *parts), refusing anything that resolves outside base."""
    path = os.path.join(base, *parts)
    rb, rp = os.path.realpath(base), os.path.realpath(path)
    if os.path.commonpath([rb, rp]) != rb or rp == rb:
        raise Refused(f"{os.path.join(*parts)!r} leaves the output folder")
    return path


def check_names(saves):
    for sf in saves:
        d = sf.get_directory()
        dn = host_name(d[8], "save folder name")
        for i in range(d[2]):
            ent, _ = sf.get_file(i)
            host_name(ent[8], f"file name in {dn}")


def sha1(data):
    return hashlib.sha1(data).hexdigest()


def fixed_clock(when):
    """Make mymcplus take every 'now' from `when` (a ToD tuple)."""
    ps2mc_dir.tod_now = lambda: when
    ps2mc.tod_now = lambda: when


def detect(path):
    if os.path.isdir(path):
        return "dir", None
    with open(path, "rb") as f:
        head = f.read(ps2mc_dir.PS2MC_DIRENT_LENGTH * 3)
    if head.startswith(CARD_MAGIC):
        return "card", None
    fmt = ps2save.poll_format(io.BytesIO(head))
    if fmt is None:
        return None, None
    return fmt.FORMAT_ID, fmt


FIXES = []  # departures from what mymcplus does on its own, recorded in info.json


def sps_fix_count(data):
    """SharkPort/X-Port: the directory's entry count (dirlen - 2) can count more files than the
    file holds (a card directory's length includes deleted entries). Return the data with the
    count set to the files actually present, or None if it already matches."""
    o = 17 + 4
    for _ in range(3):
        o += 4 + int.from_bytes(data[o:o + 4], "little")
    o += 4                                   # flen
    count_at = o + 2 + 64                    # hlen, name, then dirlen
    hlen = int.from_bytes(data[o:o + 2], "little")
    dirlen = int.from_bytes(data[count_at:count_at + 4], "little")
    o += hlen
    n = 0
    while o + 98 <= len(data) - 4:
        ehlen = int.from_bytes(data[o:o + 2], "little")
        flen = int.from_bytes(data[o + 66:o + 70], "little")
        if ehlen < 98 or o + ehlen + flen > len(data) - 4:
            break
        o += ehlen + flen
        n += 1
    if n == dirlen - 2 or o != len(data) - 4:
        return None
    FIXES.append(f"SharkPort directory says {dirlen - 2} files, the file holds {n} (then its "
                 f"4-byte checksum): read as {n}")
    return data[:count_at] + (n + 2).to_bytes(4, "little") + data[count_at + 4:]


def psv_mask_modes():
    """PSV: the PS3 keeps each file's PS2 mode in a 32-bit field; mymcplus packs it into the
    card's 16-bit field, so stray upper bits (seen: 0x07d7 in icon.sys's) stop it. Keep the
    low 16 bits, which are the PS2 mode."""
    from mymcplus.save import format_psv
    orig = format_psv.PS2FileInfo.__init__

    def init(self, d):
        orig(self, d)
        if self.mode > 0xFFFF:
            FIXES.append(f"PSV mode of {self.filename!r} is 0x{self.mode:08x}: kept 0x{self.mode & 0xFFFF:04x}")
            self.mode &= 0xFFFF
    format_psv.PS2FileInfo.__init__ = init


def load_container(path, fmt, when):
    sf = ps2save.PS2SaveFile()
    data = open(path, "rb").read()
    if fmt.FORMAT_ID == "sps":
        data = sps_fix_count(data) or data
    if fmt.FORMAT_ID == "psv":
        psv_mask_modes()
    f = io.BytesIO(data)
    if fmt.FORMAT_ID == "max":
        fmt.load(sf, f, when)
    else:
        fmt.load(sf, f)
    # Max Drive decompresses on first access; force it while the data is at hand.
    sf.get_directory()
    for i in range(sf.get_directory()[2]):
        sf.get_file(i)
    return [sf]


def load_dir(path, name, when):
    files = sorted(n for n in os.listdir(path) if os.path.isfile(os.path.join(path, n)))
    if any(os.path.isdir(os.path.join(path, n)) for n in os.listdir(path)):
        sys.exit(f"{path}: a save folder holds files only")
    sf = ps2save.PS2SaveFile()
    dirname = host_name(name or os.path.basename(os.path.normpath(path)), "save folder name").encode("ascii")
    sf.set_directory((DF_DIR_MODE, 0, len(files), when, 0, 0, when, 0, dirname))
    for i, n in enumerate(files):
        data = open(os.path.join(path, n), "rb").read()
        sf.set_file(i, (DF_FILE_MODE, 0, len(data), when, 0, 0, when, 0,
                        host_name(n, "file name").encode("ascii")), data)
    return [sf]


def load_card(path):
    f = open(path, "rb")
    mc = ps2mc.ps2mc(f, ignore_ecc=False)
    out = []
    for ent in list(mc.dir_open("/"))[2:]:
        if ent[0] & ps2mc_dir.DF_EXISTS and ps2mc_dir.mode_is_dir(ent[0]):
            out.append(mc.export_save_file("/" + ent[8].decode("ascii")))
    return out, mc, f


def tod_str(tod):
    sec, mi, h, d, mo, y = tod
    return f"{y:04d}-{mo:02d}-{d:02d} {h:02d}:{mi:02d}:{sec:02d}"


def describe(sf):
    d = sf.get_directory()
    files = []
    for i in range(d[2]):
        ent, data = sf.get_file(i)
        files.append({"name": ent[8].decode("ascii"), "size": len(data), "sha1": sha1(data),
                      "mode": f"{ent[0]:04x}", "created": tod_str(ent[3]), "modified": tod_str(ent[6])})
    title = None
    try:
        isys = sf.get_icon_sys()
        if isys is not None:
            t = isys.get_title("unicode")
            title = [unicodedata.normalize("NFKC", s).strip() for s in t]
    except Exception as e:  # a broken icon.sys is worth knowing, not fatal
        title = f"icon.sys unreadable: {e}"
    return {"dir": d[8].decode("ascii"), "mode": f"{d[0]:04x}", "created": tod_str(d[3]),
            "modified": tod_str(d[6]), "files": files, "title": title}


def write_card(saves, out):
    with open(out, "w+b") as f:
        params = (True, ps2mc.PS2MC_STANDARD_PAGE_SIZE, ps2mc.PS2MC_STANDARD_PAGES_PER_ERASE_BLOCK,
                  ps2mc.PS2MC_STANDARD_PAGES_PER_CARD)
        ps2mc.ps2mc(f, True, params).close()
    with open(out, "r+b") as f:
        mc = ps2mc.ps2mc(f)
        for sf in saves:
            if not mc.import_save_file(sf, False):
                sys.exit(f"{sf.get_directory()[8]!r}: already on the card")
        mc.close()


def check_card(path, saves):
    """Read the card back and compare every file with what was put on it."""
    with open(path, "rb") as f:
        mc = ps2mc.ps2mc(f)
        for sf in saves:
            d = sf.get_directory()
            back = mc.export_save_file("/" + d[8].decode("ascii"))
            if back.get_directory()[2] != d[2]:
                sys.exit(f"{d[8]!r}: file count differs on the card")
            for i in range(d[2]):
                a, b = sf.get_file(i), back.get_file(i)
                if a[0][8] != b[0][8] or a[1] != b[1]:
                    sys.exit(f"{d[8]!r}/{a[0][8]!r}: differs on the card")
        mc.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("save")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--name", help="the save folder's name, for a folder input whose name was changed")
    ap.add_argument("--time", default="2000-01-01 00:00:00",
                    help="timestamp for everything the input does not date (JST, as on a card)")
    a = ap.parse_args()

    t = datetime.datetime.strptime(a.time, "%Y-%m-%d %H:%M:%S")
    when = (t.second, t.minute, t.hour, t.day, t.month, t.year)
    fixed_clock(when)

    kind, fmt = detect(a.save)
    if kind is None:
        sys.exit(f"{a.save}: not a PS2 save format this reads")
    card_out = os.path.join(a.out, "Mcd001.ps2")
    mc = cf = None
    if a.name and kind != "dir":
        sys.exit("--name is for folder inputs")
    try:
        if kind == "dir":
            saves = load_dir(a.save, a.name, when)
        elif kind == "card":
            saves, mc, cf = load_card(a.save)
        else:
            saves = load_container(a.save, fmt, when)
        check_names(saves)
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr)
        sys.exit(3)
    os.makedirs(a.out, exist_ok=True)

    if kind == "card" and os.path.getsize(a.save) == CARD_8M_ECC:
        shutil.copyfile(a.save, card_out)
        card_how = "the input card, copied as is (already an 8 MiB card with ECC)"
    else:
        write_card(saves, card_out)
        card_how = "formatted by mymcplus (8 MiB, ECC), the save imported with mymcplus"
    check_card(card_out, saves)

    play = os.path.join(a.out, "mc0")
    if os.path.exists(play):
        shutil.rmtree(play)
    os.makedirs(play)
    for sf in saves:
        d = sf.get_directory()
        dn = host_name(d[8], "save folder name")
        sd = under(play, dn)
        os.makedirs(sd)
        for i in range(d[2]):
            ent, data = sf.get_file(i)
            target = under(play, dn, host_name(ent[8], f"file name in {dn}"))
            if os.path.lexists(target):
                sys.exit(f"{dn}/{ent[8]!r}: two files of that name in the save")
            with open(target, "xb") as f:
                f.write(data)
    if mc:
        mc.close()
        cf.close()

    card = open(card_out, "rb").read()
    info = {
        "input": os.path.basename(os.path.normpath(a.save)),
        "format": kind,
        "saves": [describe(sf) for sf in saves],
        "card": {"path": "Mcd001.ps2", "size": len(card), "sha1": sha1(card), "how": card_how},
        "play": "mc0/",
        "time": a.time,
        "fixes": FIXES or None,
        "mymcplus": importlib.metadata.version("mymcplus"),
    }
    with open(os.path.join(a.out, "info.json"), "w") as f:
        json.dump(info, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"format": kind, "saves": [s["dir"] for s in info["saves"]],
                      "card_sha1": info["card"]["sha1"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
