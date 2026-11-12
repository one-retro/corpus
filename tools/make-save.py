#!/usr/bin/env python3
"""Play a game in a libretro core from a script and file what it saved.

    make-save.py SYSTEM CORE ROM SCRIPT [--options FILE] [--keep-sysdir]
                 [--bios FILE ...] [--dry] [--note TEXT] [--home]
                 [--subsystem ID --slot FILE ...] [--rom-source URL]

SYSTEM and CORE are registry slugs. ROM is a path (tools/rom.py get prints one).
SCRIPT is a retro-run script, normally scripts/SYSTEM/<game>.txt; its last
`shot` becomes the entry's proof.png.

The core runs in a fresh directory with its own save directory and a system
directory of symlinks to the BIOS files named (or every file in
.cache/bios/SYSTEM/ when none are). Afterwards everything in the save
directory is filed, exactly as the core named it, under

    corpus/SYSTEM/CORE/<ROM stem>/

beside provenance.json (what made it) and proof.png. Files the core writes into
its working directory are filed under cwd/ (Stella puts its SaveKey there). With
--keep-sysdir, files the core created in the system directory are filed under
system/; with --home the core runs with its own HOME and what it writes there is
filed under home/ (Play! keeps its memory cards under Documents in the home folder). provenance's
"files" lists every filed file by its path in the entry. Every run, filed or
not, appends one line to .cache/status.jsonl.

--subsystem loads ROM and the --slot files through retro_load_game_special, as
RetroArch loads a subsystem (Sufami Turbo); saves are named after each slot.

--dry runs and reports without filing anything, for developing a script.
"""

import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TOOLS = os.path.join(ROOT, "tools")


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rom_record(rom):
    """The ROM's identity. A .cue or .m3u is a few bytes of text, so for those
    the files it names are hashed too: those are the disc."""
    rec = {"name": os.path.basename(rom), "sha1": sha1(rom), "size": os.path.getsize(rom)}
    ext = os.path.splitext(rom)[1].lower()
    if ext in (".cue", ".m3u", ".gdi"):
        base, parts = os.path.dirname(rom), []
        for line in open(rom, errors="replace"):
            line = line.strip()
            if ext == ".cue":
                if not line.upper().startswith("FILE"):
                    continue
                name = line[line.index(" ") + 1:].rsplit(" ", 1)[0].strip().strip('"')
            elif ext == ".gdi":
                bits = line.split()
                if len(bits) < 5:
                    continue
                name = bits[4].strip('"')
            else:
                if not line or line.startswith("#"):
                    continue
                name = line
            path = os.path.join(base, name)
            if os.path.isfile(path):
                parts.append({"name": name, "sha1": sha1(path), "size": os.path.getsize(path)})
        if parts:
            rec["tracks"] = parts
    return rec


def core_path(slug):
    out = subprocess.run([os.path.join(TOOLS, "fetch-core.sh"), slug], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(out.stderr.strip() or f"could not fetch core {slug}")
    return out.stdout.strip().splitlines()[-1]


def harness_for(core):
    arch = "x86_64" if "/x86_64/" in core else "arm64"
    exe = os.path.join(TOOLS, "retro-run", "retro-run" + ("-x86_64" if arch == "x86_64" else ""))
    if not os.path.exists(exe):
        subprocess.run(["make", "-C", os.path.join(TOOLS, "retro-run")], check=True)
    return exe


def last_shot(script, depth=0):
    """The name of the script's last `shot`, following `include`s as retro-run does."""
    name = None
    if depth > 8:
        return None
    with open(script) as f:
        for line in f:
            line = line.split("#", 1)[0].split()
            if not line:
                continue
            if line[0] == "shot":
                name = line[1] if len(line) > 1 else None
            elif line[0] == "include" and len(line) > 1:
                inc = line[1] if os.path.isabs(line[1]) else os.path.join(os.path.dirname(script), line[1])
                if os.path.exists(inc):
                    name = last_shot(inc, depth + 1) or name
    return name


def blank(path):
    with open(path, "rb") as f:
        data = f.read()
    return len(data) > 0 and (data.count(0) == len(data) or data.count(0xFF) == len(data))


def walk(d):
    for base, _, files in os.walk(d):
        for name in files:
            p = os.path.join(base, name)
            if not os.path.islink(p):
                yield os.path.relpath(p, d)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("system")
    ap.add_argument("core")
    ap.add_argument("rom")
    ap.add_argument("script")
    ap.add_argument("--options")
    ap.add_argument("--bios", action="append", default=[])
    ap.add_argument("--keep-sysdir", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--no-hw", action="store_true")
    ap.add_argument("--device", help="libretro controller device id, e.g. 0x305 for a DualShock")
    ap.add_argument("--srm", help="battery save to start from (a continuation of another save)")
    ap.add_argument("--name", help="folder name for the game, default the ROM stem")
    ap.add_argument("--note", default="")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--home", action="store_true", help="run with HOME in the work directory, file what lands there")
    ap.add_argument("--subsystem", help="libretro subsystem ident, e.g. multicart_addon")
    ap.add_argument("--slot", action="append", default=[], help="a further subsystem slot file (- for empty)")
    ap.add_argument("--ports", help="controller ports to plug a pad into (retro-run default 2)")
    ap.add_argument("--pace", help="frames per wall-clock second (cores with their own real-time thread)")
    ap.add_argument("--accelerometer", action="store_true",
                    help="offer the core an accelerometer (sensor interface), driven by the script's `tilt`")
    ap.add_argument("--rom-source", help="URL a freely distributed homebrew ROM came from")
    a = ap.parse_args()

    rom = os.path.abspath(a.rom)
    script = os.path.abspath(a.script)
    core = core_path(a.core)
    exe = harness_for(core)

    work = tempfile.mkdtemp(prefix=f"{a.system}-{a.core}-", dir=os.path.join(ROOT, ".cache"))
    saves, system, shots, home = (os.path.join(work, d) for d in ("saves", "system", "shots", "home"))
    for d in (saves, system, shots, home):
        os.makedirs(d)
    # Each entry of .cache/bios/SYSTEM/ (file or directory) is linked into the
    # system directory, so a core that wants dc/dc_boot.bin finds it.
    bios_dir = os.path.join(ROOT, ".cache", "bios", a.system)
    bios = list(a.bios)
    if not bios and os.path.isdir(bios_dir):
        bios = [os.path.join(bios_dir, f) for f in sorted(os.listdir(bios_dir))]
    for b in bios:
        b = os.path.abspath(b)
        os.symlink(b, os.path.join(system, os.path.basename(b)))

    info_path = os.path.join(work, "info.json")
    cmd = [exe, "--core", core, "--rom", rom, "--savedir", saves, "--sysdir", system,
           "--shots", shots, "--script", script, "--info", info_path, "--quiet"]
    if a.options:
        cmd += ["--options", os.path.abspath(a.options)]
    if a.no_hw:
        cmd += ["--no-hw"]
    if a.device:
        cmd += ["--device", a.device]
    if a.srm:
        cmd += ["--srm", os.path.abspath(a.srm)]
    if a.subsystem:
        cmd += ["--subsystem", a.subsystem]
        for sl in a.slot:
            cmd += ["--slot", sl if sl == "-" else os.path.abspath(sl)]
    if a.ports:
        cmd += ["--ports", a.ports]
    if a.pace:
        cmd += ["--pace", a.pace]
    if a.accelerometer:
        cmd += ["--accelerometer"]
    env = dict(os.environ, HOME=home, CFFIXED_USER_HOME=home) if a.home else None
    try:
        run = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout, cwd=work, env=env)
        rc, err = run.returncode, run.stderr
    except subprocess.TimeoutExpired:
        rc, err = -1, "timed out"
    info = json.load(open(info_path)) if os.path.exists(info_path) else {}

    written = sorted(walk(saves))
    sys_new = sorted(walk(system)) if a.keep_sysdir else []
    home_new = sorted(walk(home)) if a.home else []
    # Anything else in the work directory was written by the core into its cwd.
    ours = tuple(d + os.sep for d in ("saves", "system", "shots", "home"))
    cwd_new = sorted(f for f in walk(work) if not f.startswith(ours) and f != "info.json")
    blanks = [f for f in written if blank(os.path.join(saves, f))]
    extra = [os.path.join("cwd", f) for f in cwd_new] + [os.path.join("home", f) for f in home_new]
    extra_ok = any(not blank(os.path.join(work, f.split(os.sep, 1)[1] if f.startswith("cwd" + os.sep) else f))
                   for f in extra)
    shot = last_shot(script)
    proof = os.path.join(shots, f"{shot}.png") if shot else None

    game = a.name or os.path.splitext(os.path.basename(rom))[0]
    status = {
        "system": a.system, "core": a.core, "game": game, "rc": rc,
        "files": written, "blank": blanks, "sysdir_files": sys_new,
        "cwd_files": cwd_new, "home_files": home_new,
        "frames": info.get("frames"), "work": work,
        "time": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    # A clock file is not a save: a run whose only non-blank file is a clock
    # (SkyEmu writes a .rtc for every game) saved nothing.
    clocks = (".rtc", ".smpc")
    data = [f for f in written if not f.lower().endswith(clocks)]
    ok = rc == 0 and ((data and any(f not in blanks for f in data)) or extra_ok)
    status["ok"] = bool(ok)
    if rc != 0:
        status["error"] = err.strip().splitlines()[-5:]

    if ok and not a.dry:
        dest = os.path.join(ROOT, a.system, a.core, game)
        if os.path.exists(dest):
            # Replace only an entry this runner made. Downloads, device
            # backups and MiSTer or standalone saves are someone else's.
            prev = os.path.join(dest, "provenance.json")
            try:
                mine = json.load(open(prev)).get("frontend", "").startswith("retro-run")
            except (OSError, ValueError):
                mine = False
            if not mine:
                sys.exit(f"{os.path.relpath(dest, ROOT)} exists and was not made by retro-run; "
                         "not replacing it (use --name for a different folder)")
            shutil.rmtree(dest)
        os.makedirs(dest)
        for f in written:
            os.makedirs(os.path.dirname(os.path.join(dest, f)), exist_ok=True)
            shutil.copy2(os.path.join(saves, f), os.path.join(dest, f))
        filed = list(written)
        for sub, src, names in (("system", system, sys_new), ("cwd", work, cwd_new), ("home", home, home_new)):
            for f in names:
                target = os.path.join(dest, sub, f)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copy2(os.path.join(src, f), target)
                filed.append(os.path.join(sub, f))
        if proof and os.path.exists(proof):
            shutil.copy2(proof, os.path.join(dest, "proof.png"))
        prov = {
            "method": "played",
            "system": a.system,
            "core": a.core,
            "core_file": os.path.basename(core),
            "core_name": info.get("library_name"),
            "core_version": info.get("library_version"),
            "frontend": "retro-run (writes saves as RetroArch does)",
            "renderer": info.get("renderer"),
            "rom": rom_record(rom),
            "rom_source": a.rom_source,
            "subsystem": ({"ident": a.subsystem,
                           "slots": [rom_record(rom)] + [None if s == "-" else rom_record(os.path.abspath(s)) for s in a.slot],
                           "loaded_with": "retro_load_game_special, as RetroArch loads a subsystem (retro-run --subsystem)"}
                          if a.subsystem else None),
            "device": a.device,
            **({"accelerometer": "offered through the libretro sensor interface; the script's `tilt` sets its readings"}
               if a.accelerometer else {}),
            "script": os.path.relpath(script, ROOT),
            "frames": info.get("frames"),
            "options": open(a.options).read() if a.options else None,
            "started_from": os.path.relpath(os.path.abspath(a.srm), ROOT) if a.srm else None,
            "files": {f: {"size": os.path.getsize(os.path.join(dest, f)), "sha1": sha1(os.path.join(dest, f))}
                      for f in filed},
            "created": datetime.date.today().isoformat(),
            "note": a.note or None,
        }
        # A core built from source carries <core>.json beside it: repo, commit, build command.
        if os.path.exists(core + ".json"):
            prov["built_from"] = json.load(open(core + ".json"))
        with open(os.path.join(dest, "provenance.json"), "w") as f:
            json.dump(prov, f, indent=2)
            f.write("\n")
        status["filed"] = os.path.relpath(dest, ROOT)
        shutil.rmtree(work, ignore_errors=True)
        status["work"] = None

    if not a.dry:
        with open(os.path.join(ROOT, ".cache", "status.jsonl"), "a") as f:
            f.write(json.dumps(status) + "\n")
    print(json.dumps(status, indent=1))
    if not ok and rc != 0:
        sys.stderr.write(err[-3000:])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
