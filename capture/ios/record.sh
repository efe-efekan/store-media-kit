#!/usr/bin/env bash
# Records the simulator screen while YOU use the app, then you press Enter to stop.
#   capture/ios/record.sh <udid> <out.mp4>
# Record several short takes (5-8 s each, one idea per take) and list them as "shots"
# in media.json -> video.shots. For tap ripples, write <clip>.taps.json by hand:
#   { "events": [ { "t": 1.20, "x": 0.52, "y": 0.61 } ] }   (t seconds, x/y = 0-1 of the frame)
# or log them from the app (see capture/flutter/README.md).
set -euo pipefail
UDID="${1:?usage: record.sh <udid> <out.mp4>}"
OUT="${2:?usage: record.sh <udid> <out.mp4>}"
mkdir -p "$(dirname "$OUT")"
xcrun simctl status_bar "$UDID" override --time 9:41 --batteryState charged --batteryLevel 100 --wifiBars 3 --cellularBars 4 || true
xcrun simctl io "$UDID" recordVideo --codec=h264 --mask=ignored --force "$OUT" &
REC=$!
sleep 1
read -r -p "Recording… press Enter to stop " _
kill -INT "$REC"
wait "$REC" || true
echo "wrote $OUT"
