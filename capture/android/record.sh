#!/usr/bin/env bash
# Records the Android screen while YOU use the app; press Enter to stop (max 180 s).
#   capture/android/record.sh <out.mp4> [adb-serial]
# Record short takes (5-8 s, one idea each) and list them in media.json -> video.shots.
set -euo pipefail
OUT="${1:?usage: record.sh <out.mp4> [adb-serial]}"
ADB=(adb); [ -n "${2:-}" ] && ADB=(adb -s "$2")
mkdir -p "$(dirname "$OUT")"
"${ADB[@]}" shell settings put global sysui_demo_allowed 1
"${ADB[@]}" shell am broadcast -a com.android.systemui.demo -e command enter >/dev/null
"${ADB[@]}" shell am broadcast -a com.android.systemui.demo -e command clock -e hhmm 1200 >/dev/null
"${ADB[@]}" shell screenrecord --bit-rate 12000000 /sdcard/smk_take.mp4 &
REC=$!
sleep 1
read -r -p "Recording… press Enter to stop " _
"${ADB[@]}" shell pkill -INT screenrecord || kill -INT "$REC" || true
wait "$REC" 2>/dev/null || true
sleep 1
"${ADB[@]}" pull /sdcard/smk_take.mp4 "$OUT" >/dev/null
"${ADB[@]}" shell rm /sdcard/smk_take.mp4
"${ADB[@]}" shell am broadcast -a com.android.systemui.demo -e command exit >/dev/null
echo "wrote $OUT"
