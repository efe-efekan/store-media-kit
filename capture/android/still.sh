#!/usr/bin/env bash
# Screenshot of an Android emulator or device in demo mode (no notification icons, fixed clock and
# battery). The status bar is still in the PNG; `kit.py shots` removes it (store images must not show it).
#   capture/android/still.sh <out.png> [adb-serial]
# Use a 1080x1920 (or any 9:16) emulator for phone shots; tablets: 1200x1920 / 1600x2560.
set -euo pipefail
OUT="${1:?usage: still.sh <out.png> [adb-serial]}"
ADB=(adb); [ -n "${2:-}" ] && ADB=(adb -s "$2")
mkdir -p "$(dirname "$OUT")"
"${ADB[@]}" shell settings put global sysui_demo_allowed 1
demo() { "${ADB[@]}" shell am broadcast -a com.android.systemui.demo -e command "$@" >/dev/null; }
demo enter
demo clock -e hhmm 1200
demo battery -e level 100 -e plugged false
demo network -e wifi show -e level 4 -e mobile show -e datatype none -e level 4
demo notifications -e visible false
sleep 0.5
"${ADB[@]}" exec-out screencap -p > "$OUT"
demo exit
echo "wrote $OUT"
