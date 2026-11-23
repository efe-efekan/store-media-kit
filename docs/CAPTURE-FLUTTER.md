# Clean captures from a Flutter app

The kit only needs **clean** captures: the real app screen with no debug banner, no
dev overlays, no sign-in walls and (for games) no HUD clutter. In Flutter the reliable
way is an integration test that boots a special "screenshot mode" and drives the app.

## 1. Screenshot mode (compile-time, never in a store build)

```dart
// lib/src/dev/screenshot_mode.dart
const bool kScreenshotMode = bool.fromEnvironment('SCREENSHOT_MODE');
const String kScreenshotLocale = String.fromEnvironment('LOCALE', defaultValue: 'en');
```

```dart
// main.dart — first line of main()
if (kScreenshotMode) return ScreenshotMode.run(); // tree-shaken away without the define
```

`ScreenshotMode.run()` starts the app with fixed local state: **no backend, no
analytics, no purchases, no ads, no onboarding/consent popups**, the language from
`LOCALE`, fake but realistic data (a nice level, a filled-in profile). It must never
reach production services.

## 2. Stills: `integration_test/screenshots_test.dart`

```dart
final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
testWidgets('store stills', (tester) async {
  await binding.convertFlutterSurfaceToImage();   // iOS: needed before takeScreenshot
  // ...drive the app to moment 1...
  await binding.takeScreenshot('01');             // png bytes arrive in the driver
});
```

`test_driver/integration_test.dart` writes them to `store-media/raw/iphone69/<LOCALE>/01.png`:

```dart
Future<void> main() => integrationDriver(
  onScreenshot: (name, bytes, [args]) async {
    const locale = String.fromEnvironment('LOCALE', defaultValue: 'en');
    final f = File('store-media/raw/iphone69/$locale/$name.png');
    await f.create(recursive: true);
    await f.writeAsBytes(bytes);
    return true;
  },
);
```

Run on an **iPhone 17 Pro Max** simulator (1320x2868 = the 6.9" store size):

```bash
flutter drive --driver=test_driver/integration_test.dart \
  --target=integration_test/screenshots_test.dart -d <udid> \
  --dart-define=SCREENSHOT_MODE=true --dart-define=LOCALE=en
```

Flutter renders these itself, so there is no simulator Dynamic Island or status bar in them.
If the UI has no text, one English capture serves every locale (the kit falls back to `en`).

## 3. Video clips with tap ripples: `integration_test/preview_video_test.dart`

`capture/flutter/record_flutter.sh` records the simulator while the test plays and
cuts the take into clips. The test prints these lines (`debugPrint`):

| line | meaning |
| --- | --- |
| `PREVIEW_READY` | app is on screen; recording starts |
| `PREVIEW_SYNC <epoch ms>` | the screen turns fully black for ~0.3 s at this moment (sync frame) |
| `PREVIEW_CLIP <clipN> start\|end <epoch ms>` | clip boundaries |
| `PREVIEW_EVENT <clipN> {"e": <epoch ms>, "x": 0.52, "y": 0.61}` | a tap (x/y = 0-1 of the screen) |
| `PREVIEW_DONE` | stop recording |

```dart
int now() => DateTime.now().millisecondsSinceEpoch;
void mark(String l) => debugPrint(l);

mark('PREVIEW_READY');
await Future.delayed(const Duration(seconds: 1));
// show a black full-screen overlay for 300 ms, then:
mark('PREVIEW_SYNC ${now()}');
mark('PREVIEW_CLIP clip1 start ${now()}');
final p = tester.getCenter(find.byKey(const Key('buy')));
final size = tester.view.physicalSize / tester.view.devicePixelRatio;
mark('PREVIEW_EVENT clip1 ${jsonEncode({'e': now(), 'x': p.dx / size.width, 'y': p.dy / size.height})}');
await tester.tap(find.byKey(const Key('buy')));
// ...real-time pumping (tester.pump(Duration(milliseconds: 16)) in a loop)...
mark('PREVIEW_CLIP clip1 end ${now()}');
mark('PREVIEW_DONE');
```

```bash
<kit>/capture/flutter/record_flutter.sh . <udid> store-media/video/public/clips \
  integration_test/preview_video_test.dart \
  --dart-define=SCREENSHOT_MODE=true --dart-define=PREVIEW_VIDEO=true --dart-define=LOCALE=en
```

Output: `clip1.mp4`, `clip1.taps.json`, … ready for `media.json → video.shots`.

Tips that mattered in practice:

- Play at **normal speed** and pump real time; the store video must feel like real use.
- One idea per clip (5-8 s). Show the core loop first, then features.
- A tutorial hand / pointer drawn by the app reads better than nothing; the template adds ripples on top.
- Simulator recordings include the Dynamic Island: set `video.crop` to
  `{ "scale": 1.062, "origin": "50% 100%" }` to zoom it out of frame.
