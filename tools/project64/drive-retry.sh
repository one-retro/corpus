#!/bin/bash
# drive-retry.sh ROM PLAN OUT TIMEOUT [TRIES]: ~/Wine/project64/drive.sh, again when Wine dies
# before the plan quits (Project64 under Wine crashes now and then, more often the longer it runs).
#
# Save/ is emptied before the first try only. If the plan saves states ({"at": n, "key": "74"}, F5;
# the harness keeps each as OUT/try<t>/state<n>.pj.zip), a later try puts back the last state saved
# at least 60 polls before the crash, loads it (F7 at poll 150) and carries on from poll n.
# START_STATE=<state.pj.zip> START_FRAME=<n> STATE_NAME=<folder/name.pj.zip under Save/> make the
# first try start that way too. At the end each try's pictures are gathered in OUT and log.txt holds
# every try's log, one after the other.
rom="$1" plan="$2" out="$3" timeout="$4" tries="${5:-3}"
save="$HOME/Wine/project64/Project64/Save"
rm -rf "$out"; mkdir -p "$out"
rm -rf "$save/"*
gather() { for d in "$out"/try*; do cp "$d"/*.png "$d"/*.bin "$out"/ 2>/dev/null; echo "== $(basename "$d")"; cat "$d/log.txt"; done >"$out/log.txt"; }
resume_plan() { # resume_plan <poll> <dst>: the plan's steps after <poll>, after loading the state
  python3 -I - "$plan" "$1" "$2" <<'PY'
import json, sys
plan, s, dst = sys.argv[1], int(sys.argv[2]), sys.argv[3]
p = json.load(open(plan))
p["steps"] = [{"at": 150, "key": "76"}, {"at": 150, "setframe": s}] + [x for x in p["steps"] if x["at"] > s]
json.dump(p, open(dst, "w"))
PY
}
put_state() { mkdir -p "$(dirname "$save/$STATE_NAME")"; cp "$1" "$save/$STATE_NAME"; }
cur="$plan" from=0
if [ -n "$START_STATE" ]; then
  put_state "$START_STATE"; from="$START_FRAME"; resume_plan "$from" "$out/resume0.json"; cur="$out/resume0.json"
fi
for ((t = 1; t <= tries; t++)); do
  pkill -f Project64.exe 2>/dev/null; sleep 1
  "$HOME/Wine/project64/drive.sh" "$rom" "$cur" "$out/try$t" "$timeout" >/dev/null
  if grep -q ': quit' "$out/try$t/log.txt" 2>/dev/null; then echo "try $t: finished"; gather; exit 0; fi
  echo "try $t: died at $(grep tick "$out/try$t/log.txt" | tail -1)"
  # The state file's name under Save/, from the harness's "kept" lines.
  [ -z "$STATE_NAME" ] && STATE_NAME=$(grep -ho 'kept .*' "$out"/try*/log.txt | head -1 | sed 's/^kept //; s/.*\\Save\\//; s#\\#/#g')
  last=$(grep -oE '^[0-9]+' "$out/try$t/log.txt" | sort -n | tail -1)
  s=$(ls "$out/try$t" | sed -n 's/^state\([0-9]*\)\.pj\.zip$/\1/p' | sort -n | awk -v l="$last" '$1 + 60 <= l' | tail -1)
  if [ -n "$s" ]; then cp "$out/try$t/state$s.pj.zip" "$out/state$s.pj.zip"; from=$s; fi
  if [ "$from" -gt 0 ] && [ -n "$STATE_NAME" ]; then
    if [ -f "$out/state$from.pj.zip" ]; then put_state "$out/state$from.pj.zip"; else put_state "$START_STATE"; fi
    resume_plan "$from" "$out/resume$t.json"; cur="$out/resume$t.json"; echo "  resume from poll $from"
  fi
done
gather
exit 1
