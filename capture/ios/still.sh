#!/usr/bin/env bash
# Screenshot of a booted simulator (neutral 9:41 / full battery). The status bar is still in the
# PNG; `kit.py shots` removes it, because store images must not show a clock, battery or signal.
#   capture/ios/still.sh <udid> <out.png>
# Use an iPhone 6.9" simulator (iPhone 17 Pro Max: 1320x2868) or iPad 13" (2064x2752).
# Tip: hide debug banners / dev UI in your app; the kit adds the headline and frame.
set -euo pipefail
UDID="${1:?usage: still.sh <udid> <out.png>}"
OUT="${2:?usage: still.sh <udid> <out.png>}"
mkdir -p "$(dirname "$OUT")"
xcrun simctl status_bar "$UDID" override --time 9:41 --dataNetwork wifi --wifiMode active --wifiBars 3 \
  --cellularMode active --cellularBars 4 --batteryState charged --batteryLevel 100
xcrun simctl io "$UDID" screenshot --type=png "$OUT" >/dev/null
echo "wrote $OUT ($(sips -g pixelWidth -g pixelHeight "$OUT" | awk '/pixel/{printf $2" "}'))"
