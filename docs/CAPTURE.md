# Capturing clean screens

The kit puts **your app's real screen** inside the device frame, so the capture decides the quality.
Aim for: the exact store size, a tidy status bar, real but neat content, nothing private.

## Checklist (every platform)

- [ ] Right size: iPhone **1320×2868**, iPad **2064×2752**, Android phone **1080×1920**, 7" **1200×1920**, 10" **1600×2560**
- [ ] No debug banner, dev menu, FPS meter, test watermark
- [ ] No notifications, no real names / e-mails / phone numbers, no personal photos
- [ ] Realistic demo data (a filled list, a nice level, a profile with an avatar)
- [ ] Each of the 5 captures shows a **different** screen or moment
- [ ] Games: as little HUD clutter as possible (pause the timer, hide popups)

If your UI has no text, one English set (`raw/<device>/en/`) is used for every language. If it does,
switch the app's language and capture into `raw/<device>/<locale>/`.

## iOS (simulator, macOS + Xcode)

Use **iPhone 17 Pro Max** (or any 6.9" model) for 1320×2868 and **iPad Pro 13-inch** for 2064×2752.

```bash
xcrun simctl list devices booted                          # find the UDID
capture/ios/still.sh <udid> my-app/store-media/raw/iphone69/en/01.png
capture/ios/record.sh <udid> my-app/store-media/video/public/clips/clip1.mp4    # press Enter to stop
```
`still.sh` sets the status bar to 9:41, full battery and full signal. Simulator recordings include the
Dynamic Island area; set `"crop": { "scale": 1.062, "origin": "50% 100%" }` in `media.json → video`.

## Android (emulator or device, any OS with adb)

Create an emulator with a **1080×1920** screen (Pixel-style 9:16) for phone shots, 1200×1920 / 1600×2560 for tablets.

```bash
adb devices                                               # emulator or USB device
capture/android/still.sh my-app/store-media/raw/android_phone/en/01.png
capture/android/record.sh my-app/store-media/video/public/clips/clip1.mp4      # press Enter to stop
```
Both turn on Android's **demo mode** (12:00, full battery and signal, no notification icons) while capturing.

## Flutter, React Native and others

- **Flutter**: an integration test that boots a special "screenshot mode" gives pixel-perfect captures
  and frame-accurate video clips with tap positions. Step-by-step: [CAPTURE-FLUTTER.md](CAPTURE-FLUTTER.md).
- **React Native / native**: use the simulator/emulator scripts above, or your UI-test framework's
  screenshot API (XCUITest `XCUIScreen.main.screenshot()`, Espresso/`UiDevice.takeScreenshot`, Detox, Maestro `takeScreenshot`).
- **Web apps / PWAs**: open Chrome DevTools → device toolbar at 1320×2868 → *Capture full size screenshot*.

## Tap positions for video ripples

Ripples need where and when you tapped, in a JSON file next to the clip (or inline in `media.json`):

```json
{ "events": [ { "t": 1.20, "x": 0.52, "y": 0.61 }, { "t": 2.85, "x": 0.30, "y": 0.44 } ] }
```
`t` = seconds from the clip start, `x` / `y` = 0–1 of the screen. Easiest: play the clip in QuickTime /
VLC, note the moments, and estimate the positions; the Flutter recorder writes this file for you.
