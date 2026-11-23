#!/usr/bin/env bash
# Records App Preview clips from a Flutter integration test, frame-accurately.
#
#   capture/flutter/record_flutter.sh <app-dir> <udid> <out-dir> [target] [extra --dart-define ...]
#
# The test (default integration_test/preview_video_test.dart) drives the app and prints
# the protocol lines of capture/flutter/README.md. This script records the simulator
# with `xcrun simctl io <udid> recordVideo` from PREVIEW_READY to PREVIEW_DONE: ONE
# continuous take at normal speed, then cuts it into clips.
#
# Timing: the test turns the empty stage black at a logged moment
# (PREVIEW_SYNC <epoch ms>); this script finds that frame in take.mp4 and
# maps every logged epoch (clip edges, taps, automatic bay departures) onto
# the video's own clock, so taps.json is frame-accurate. Render latency is
# the same for the sync change and for the taps, so it cancels out.
#
# Output in <out-dir>:
#   take.mp4     the whole take
#   clipN.mp4    each clip, cut with macOS `avconvert` (re-encoded,
#                highest quality, same resolution)
#   clips.json   clip start/end in the take
#   clipN.taps.json  per clip: { "events": [{ "t", "x", "y" }] } (t = seconds from the
#                clip's first frame, x/y = 0-1 of the frame) - what the video template reads
# Use an iPhone 6.9" simulator (e.g. iPhone 17 Pro Max: 1320x2868).
# Copy clip*.mp4 and clip*.taps.json into <project>/video/public/clips/.
set -euo pipefail

USAGE="usage: record_flutter.sh <app-dir> <udid> <out-dir> [target] [--dart-define=K=V ...]"
ROOT="$(cd "${1:?$USAGE}" && pwd)"
UDID="${2:?$USAGE}"
mkdir -p "${3:?$USAGE}"
OUT="$(cd "$3" && pwd)"
TARGET="${4:-integration_test/preview_video_test.dart}"
shift $(( $# < 4 ? $# : 4 ))
EXTRA=("$@")
LOG="$OUT/drive.log"
REC_LOG="$OUT/record.log"
TAKE="$OUT/take.mp4"
TMP="$(mktemp -d)"

mkdir -p "$OUT"
rm -f "$LOG" "$REC_LOG" "$TAKE" "$OUT"/clip*.mp4 "$OUT"/clip*.taps.json "$OUT/clips.json"

cd "$ROOT"
flutter drive \
  --driver=test_driver/integration_test.dart \
  --target="$TARGET" \
  -d "$UDID" \
  "${EXTRA[@]+"${EXTRA[@]}"}" >"$LOG" 2>&1 &
DRIVE_PID=$!

REC_PID=""
cleanup() {
  [ -n "$REC_PID" ] && kill -INT "$REC_PID" 2>/dev/null || true
  kill "$DRIVE_PID" 2>/dev/null || true
  rm -rf "$TMP"
}
trap cleanup EXIT

wait_for() { # <pattern> <file>
  until grep -q "$1" "$2" 2>/dev/null; do
    if ! kill -0 "$DRIVE_PID" 2>/dev/null; then
      echo "flutter drive ended before '$1':" >&2
      tail -40 "$LOG" >&2
      exit 1
    fi
    sleep 0.1
  done
}

echo "Building and launching (log: $LOG)…"
wait_for PREVIEW_READY "$LOG"

xcrun simctl io "$UDID" recordVideo --codec=h264 --mask=ignored --force "$TAKE" >"$REC_LOG" 2>&1 &
REC_PID=$!
until grep -q "Recording started" "$REC_LOG" 2>/dev/null; do
  kill -0 "$REC_PID" 2>/dev/null || { cat "$REC_LOG" >&2; exit 1; }
  sleep 0.02
done
echo "Recording…"

wait_for PREVIEW_DONE "$LOG"
kill -INT "$REC_PID"
wait "$REC_PID" || true
REC_PID=""
wait "$DRIVE_PID" || { tail -40 "$LOG" >&2; exit 1; }
grep -q "All tests passed" "$LOG" || { tail -40 "$LOG" >&2; exit 1; }

# Presentation time (s) of the first frame whose middle is black.
cat >"$TMP/find_sync.swift" <<'SWIFT'
import AVFoundation
let asset = AVURLAsset(url: URL(fileURLWithPath: CommandLine.arguments[1]))
let track = asset.tracks(withMediaType: .video)[0]
let reader = try! AVAssetReader(asset: asset)
let output = AVAssetReaderTrackOutput(track: track, outputSettings: [
  kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
])
reader.add(output)
reader.startReading()
while let sample = output.copyNextSampleBuffer() {
  guard let pixels = CMSampleBufferGetImageBuffer(sample) else { continue }
  CVPixelBufferLockBaseAddress(pixels, .readOnly)
  let w = CVPixelBufferGetWidth(pixels), h = CVPixelBufferGetHeight(pixels)
  let row = CVPixelBufferGetBytesPerRow(pixels)
  let base = CVPixelBufferGetBaseAddress(pixels)!.assumingMemoryBound(to: UInt8.self)
  var black = true
  for (fx, fy) in [(0.5, 0.5), (0.3, 0.62), (0.7, 0.4), (0.5, 0.8)] {
    let p = base + Int(fy * Double(h)) * row + Int(fx * Double(w)) * 4
    if (Int(p[0]) + Int(p[1]) + Int(p[2])) / 3 > 40 { black = false }
  }
  CVPixelBufferUnlockBaseAddress(pixels, .readOnly)
  if black {
    print(CMSampleBufferGetPresentationTimeStamp(sample).seconds)
    exit(0)
  }
}
exit(1)
SWIFT
SYNC_VIDEO_S="$(xcrun swift "$TMP/find_sync.swift" "$TAKE" 2>/dev/null)" ||
  { echo "sync frame not found in $TAKE" >&2; exit 1; }

python3 - "$LOG" "$SYNC_VIDEO_S" "$OUT" <<'PY'
import json, re, subprocess, sys
log, sync_video_s, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
sync_ms = next(int(m.group(1)) for l in lines
               if (m := re.search(r"PREVIEW_SYNC (\d+)", l)))
def video_s(epoch_ms):          # epoch → seconds on the take's clock
    return sync_video_s + (epoch_ms - sync_ms) / 1000

edges, events = {}, {}
for l in lines:
    if m := re.search(r"PREVIEW_CLIP (\S+) (start|end) (\d+)", l):
        edges.setdefault(m.group(1), {})[m.group(2)] = video_s(int(m.group(3)))
    elif m := re.search(r"PREVIEW_EVENT (\S+) (\{.*\})", l):
        events.setdefault(m.group(1), []).append(json.loads(m.group(2)))

clips, taps = [], {}
for name in sorted(edges):
    s, e = edges[name]["start"], edges[name]["end"]
    if s < 0:
        sys.exit(f"{name} starts before the recording ({s:.3f} s)")
    clips.append({"name": name, "start": round(s, 3), "end": round(e, 3),
                  "duration": round(e - s, 3), "file": f"{name}.mp4"})
    rel = lambda ms: None if ms is None else round(video_s(ms) - s, 3)
    out_events = []
    for ev in events.get(name, []):
        if "x" in ev and "y" in ev:
            out_events.append({"t": rel(ev["e"]), "x": ev["x"], "y": ev["y"]})
    taps[name] = {"events": out_events}

json.dump({"take": "take.mp4", "sync_frame_s": round(sync_video_s, 4),
           "clips": clips}, open(f"{out}/clips.json", "w"), indent=2)
for name, t in taps.items():
    json.dump(t, open(f"{out}/{name}.taps.json", "w"), indent=2)
for c in clips:
    subprocess.run(["avconvert", "--preset", "PresetHighestQuality",
                    "--source", f"{out}/take.mp4", "--output", f"{out}/{c['file']}",
                    "--start", str(c["start"]), "--duration", str(c["duration"]),
                    "--replace"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"{c['file']}: {c['start']:.2f}–{c['end']:.2f} s of the take "
          f"({c['duration']:.2f} s, {len(taps[c['name']]['events'])} events)")
PY
echo "Done: $OUT"
