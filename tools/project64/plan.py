#!/usr/bin/env python3
"""Turn a retro-run script into a Project64 harness plan (~/Wine/project64/Project64/Scripts/harness.js).

    plan.py SCRIPT OUT.json [--scale F] [--offset N]

One retro-run frame becomes F controller polls (default 1). RetroPad -> N64 as Mupen64Plus-Next maps
it: b=A, y=B, l2=Z, start=START, l=L, r=R, D-pad = D-pad; `stick X Y N` holds the analog stick
(values scaled from +-32767 to +-80). `shot` becomes a framebuffer PNG; the plan ends with quit.
"""
import json, sys

MAP = {"b": "A", "y": "B", "l2": "Z", "start": "START", "l": "L", "r": "R",
       "up": "DU", "down": "DD", "left": "DL", "right": "DR",
       "x": "CU", "a": "CR"}

def stickval(v):
    v = {"min": -32767, "max": 32767}.get(v, v)
    return round(int(v) * 80 / 32767)

def expand(lines):
    out, i = [], 0
    while i < len(lines):
        t = lines[i]
        if t[0] == "repeat":
            depth, j = 1, i + 1
            while depth:
                depth += {"repeat": 1, "end": -1}.get(lines[j][0], 0); j += 1
            body = expand(lines[i + 1:j - 1])
            out += body * int(t[1]); i = j
        else:
            out.append(t); i += 1
    return out

def main():
    a = sys.argv[1:]
    scale = float(a[a.index("--scale") + 1]) if "--scale" in a else 1.0
    offset = int(a[a.index("--offset") + 1]) if "--offset" in a else 0
    lines = [l.split("#")[0].split() for l in open(a[0])]
    lines = expand([l for l in lines if l])
    f, steps = 0.0, []
    at = lambda: int(round(f * scale)) + 1 + offset
    for t in lines:
        c = t[0]
        if c == "wait":
            f += int(t[1])
        elif c == "press":
            n = int(t[2]) if len(t) > 2 else 4
            steps.append({"at": at(), "press": " ".join(MAP[b] for b in t[1].split("+")), "hold": max(1, round(n * scale))})
            f += n
        elif c == "tap":
            count = int(t[2]) if len(t) > 2 else 1; gap = int(t[3]) if len(t) > 3 else 12
            for _ in range(count):
                steps.append({"at": at(), "press": MAP[t[1]], "hold": max(1, round(4 * scale))}); f += 4 + gap
        elif c == "stick":
            n = int(t[3]) if len(t) > 3 else 4
            steps.append({"at": at(), "press": "SX:%d SY:%d" % (stickval(t[1]), -stickval(t[2])), "hold": max(1, round(n * scale))})
            f += n
        elif c == "shot":
            steps.append({"at": at(), "shot": t[1]})
        else:
            sys.exit("unsupported: " + " ".join(t))
    steps.append({"at": at() + 30, "quit": True})
    json.dump({"steps": steps}, open(a[1], "w"), indent=0)
    print(a[1], len(steps), "steps, last poll", steps[-1]["at"])

main()
