#!/usr/bin/env python3
"""ps2-save.py CORE ROM SCRIPT [--options FILE] [--dry] [--name NAME] [--note TEXT]
               [--start-from ENTRY_DIR] [--device ID]

tools/make-save.py, specialised for PS2. The differences:

* PS2 cores keep their memory cards outside the libretro save directory:
  LRPS2, PCEE2 and ARMSX2 in <system>/pcsx2/memcards/, Play! in
  Documents/Play Data Files/vfs/mc0 and mc1 in the home folder. So each run gets a real system
  directory (system/pcsx2/bios/ with the BIOS *file* linked in, so the NVRAM the
  cores write beside the BIOS lands in the run, not in .cache/bios) and its own
  HOME (home/), and what the cores wrote there is filed under system/ and home/,
  keeping the paths the core used.
* armsx2's buildbot dylib links its libraries from the build machine's paths;
  DYLD_LIBRARY_PATH points at .cache/ps2-deps/lib: links to Homebrew's freetype,
  jpeg-turbo, lz4, libpng and sdl3, plus libplutovg.1/libplutosvg.0 built from
  tools/ps2/pluto-stubs.c (`cc -dynamiclib -o libplutovg.1.dylib pluto-stubs.c`,
  and with -DPLUTOSVG for libplutosvg.0).
* --start-from copies an earlier entry's card files in first (a card that
  already holds another game's save).

Filed: everything in saves/; under system/: memcards/** and bios/*.nvm, *.mec
(console NVRAM, like Dolphin's SRAM.raw); under home/: Play! vfs/mc0/** and
vfs/mc1/**. Everything else the core wrote (logs, inis, caches) is listed in the
status line but not filed.
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
DEPS = os.path.join(ROOT, ".cache", "ps2-deps", "lib")
BIOS = os.path.join(ROOT, ".cache", "bios", "ps2", "pcsx2", "bios", "ps2-0200a-20040614.bin")
CORES = {
    "lrps2": "pcsx2_libretro.dylib",
    "pcee2": "pcee2_libretro.dylib",
    "play": "play_libretro.dylib",
    "armsx2": "armsx2_libretro.dylib",
}
PLAY_VFS = os.path.join("home", "Documents", "Play Data Files", "vfs")
HASHES = os.path.join(ROOT, ".cache", "ps2-rom-sha1.json")


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def sha1_cached(path):
    st = os.stat(path)
    key = f"{os.path.realpath(path)}|{st.st_size}|{int(st.st_mtime)}"
    try:
        cache = json.load(open(HASHES))
    except (OSError, ValueError):
        cache = {}
    if key not in cache:
        cache[key] = sha1(path)
        json.dump(cache, open(HASHES, "w"), indent=1)
    return cache[key]


def rom_record(rom):
    rec = {"name": os.path.basename(rom), "sha1": sha1_cached(rom), "size": os.path.getsize(rom)}
    if rom.lower().endswith(".cue"):
        parts = []
        for line in open(rom, errors="replace"):
            line = line.strip()
            if line.upper().startswith("FILE"):
                name = line[line.index(" ") + 1:].rsplit(" ", 1)[0].strip().strip('"')
                p = os.path.join(os.path.dirname(rom), name)
                if os.path.isfile(p):
                    parts.append({"name": name, "sha1": sha1_cached(p), "size": os.path.getsize(p)})
        if parts:
            rec["tracks"] = parts
    return rec


def last_shot(script, depth=0):
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


def walk(d):
    for base, _, files in os.walk(d):
        for name in files:
            p = os.path.join(base, name)
            if not os.path.islink(p):
                yield os.path.relpath(p, d)


def keep(rel):
    """Is this file (relative to the run directory) a save to file?"""
    parts = rel.split(os.sep)
    if parts[0] == "saves":
        return True
    if parts[0] == "system":
        if len(parts) >= 3 and parts[1] == "pcsx2" and parts[2] == "memcards":
            return True
        if len(parts) == 4 and parts[1] == "pcsx2" and parts[2] == "bios" and parts[3].endswith((".nvm", ".mec")):
            return True
        return False
    if parts[0] == "home":
        vfs = PLAY_VFS.split(os.sep)
        return parts[:len(vfs)] == vfs and len(parts) > len(vfs) and parts[len(vfs)] in ("mc0", "mc1")
    return False


def blank(path):
    with open(path, "rb") as f:
        data = f.read()
    return len(data) > 0 and (data.count(0) == len(data) or data.count(0xFF) == len(data))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("core", choices=sorted(CORES))
    ap.add_argument("rom")
    ap.add_argument("script")
    ap.add_argument("--options")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--device")
    ap.add_argument("--name")
    ap.add_argument("--note", default="")
    ap.add_argument("--start-from", help="an entry directory whose card files are copied in first")
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--pace", type=float, help="frames per wall-clock second (retro-run --pace)")
    a = ap.parse_args()

    rom = os.path.abspath(a.rom)
    script = os.path.abspath(a.script)
    core = os.path.join(ROOT, ".cache", "cores", "arm64", CORES[a.core])
    exe = os.path.join(TOOLS, "retro-run", "retro-run")

    work = tempfile.mkdtemp(prefix=f"ps2-{a.core}-", dir=os.path.join(ROOT, ".cache"))
    saves, system, shots, home = (os.path.join(work, d) for d in ("saves", "system", "shots", "home"))
    for d in (saves, shots, home, os.path.join(system, "pcsx2", "bios")):
        os.makedirs(d)
    os.symlink(BIOS, os.path.join(system, "pcsx2", "bios", os.path.basename(BIOS)))
    if a.start_from:
        src = os.path.abspath(a.start_from)
        for rel in walk(src):
            if rel in ("provenance.json", "proof.png"):
                continue
            dst = os.path.join(work, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(src, rel), dst)
    before = {rel: sha1(os.path.join(work, rel)) for rel in walk(work)}

    info_path = os.path.join(work, "info.json")
    cmd = [exe, "--core", core, "--rom", rom, "--savedir", saves, "--sysdir", system,
           "--shots", shots, "--script", script, "--info", info_path, "--quiet"]
    if a.options:
        cmd += ["--options", os.path.abspath(a.options)]
    if a.device:
        cmd += ["--device", a.device]
    if a.pace:
        cmd += ["--pace", str(a.pace)]
    env = dict(os.environ, HOME=home, CFFIXED_USER_HOME=home)
    if a.core == "armsx2":
        env["DYLD_LIBRARY_PATH"] = DEPS
    t0 = datetime.datetime.now()
    try:
        run = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout, cwd=work, env=env)
        rc, err = run.returncode, run.stderr
    except subprocess.TimeoutExpired:
        rc, err = -1, "timed out"
    secs = (datetime.datetime.now() - t0).seconds
    with open(os.path.join(work, "stderr.txt"), "w") as f:
        f.write(err)
    info = json.load(open(info_path)) if os.path.exists(info_path) else {}

    present = sorted(rel for rel in walk(work) if rel.split(os.sep)[0] in ("saves", "system", "home"))
    filed = [f for f in present if keep(f)]
    other = [f for f in present if not keep(f) and before.get(f) != sha1(os.path.join(work, f))]
    blanks = [f for f in filed if blank(os.path.join(work, f))]
    shot = last_shot(script)
    proof = os.path.join(shots, f"{shot}.png") if shot else None

    game = a.name or os.path.splitext(os.path.basename(rom))[0]
    data = [f for f in filed if not f.endswith((".nvm", ".mec"))]
    ok = rc == 0 and any(f not in blanks for f in data)
    status = {"system": "ps2", "core": a.core, "game": game, "rc": rc, "seconds": secs,
              "frames": info.get("frames"), "files": filed, "blank": blanks, "not_filed": other,
              "work": work, "ok": bool(ok),
              "time": datetime.datetime.now().isoformat(timespec="seconds")}
    if rc != 0:
        status["error"] = err.strip().splitlines()[-5:]

    if ok and not a.dry:
        dest = os.path.join(ROOT, "ps2", a.core, game)
        if os.path.exists(dest):
            prev = os.path.join(dest, "provenance.json")
            try:
                mine = json.load(open(prev)).get("frontend", "").startswith("retro-run")
            except (OSError, ValueError):
                mine = False
            if not mine:
                sys.exit(f"{os.path.relpath(dest, ROOT)} exists and was not made by retro-run")
            shutil.rmtree(dest)
        os.makedirs(dest)
        for f in filed:
            os.makedirs(os.path.dirname(os.path.join(dest, f)), exist_ok=True)
            shutil.copy2(os.path.join(work, f), os.path.join(dest, f))
        if proof and os.path.exists(proof):
            shutil.copy2(proof, os.path.join(dest, "proof.png"))
        prov = {
            "method": "played",
            "system": "ps2",
            "core": a.core,
            "core_file": os.path.basename(core),
            "core_name": info.get("library_name"),
            "core_version": info.get("library_version"),
            "frontend": "retro-run (writes saves as RetroArch does)" + (
                f"; --pace {a.pace:g} (frames paced to wall-clock: the core emulates on its own "
                "thread and retro_run returns at once)" if a.pace else ""),
            "runner": "ps2-save.py: make-save.py with a fresh system directory and HOME per run "
                      "(PS2 cores write their cards there); see ps2/NOTES.md",
            "renderer": info.get("renderer"),
            "rom": rom_record(rom),
            "bios": {"name": os.path.basename(BIOS), "sha1": sha1(BIOS), "size": os.path.getsize(BIOS),
                     "what": "SCPH-70012 v2.00 USA (2004-06-14)"} if a.core != "play" else None,
            "device": a.device,
            "script": os.path.relpath(script, ROOT),
            "frames": info.get("frames"),
            "options": open(a.options).read() if a.options else None,
            "started_from": os.path.relpath(os.path.abspath(a.start_from), ROOT) if a.start_from else None,
            "files": {f: {"size": os.path.getsize(os.path.join(dest, f)), "sha1": sha1(os.path.join(dest, f))}
                      for f in filed},
            "also_written_not_filed": other or None,
            "created": datetime.date.today().isoformat(),
            "note": a.note or None,
        }
        with open(os.path.join(dest, "provenance.json"), "w") as f:
            json.dump(prov, f, indent=2)
            f.write("\n")
        status["filed"] = os.path.relpath(dest, ROOT)
        status["proof"] = os.path.relpath(os.path.join(dest, "proof.png"), ROOT)
        shutil.rmtree(work, ignore_errors=True)
        status["work"] = None

    if not a.dry:
        with open(os.path.join(ROOT, ".cache", "ps2-status.jsonl"), "a") as f:
            f.write(json.dumps(status) + "\n")
    print(json.dumps(status, indent=1))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
