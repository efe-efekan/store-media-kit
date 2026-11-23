# media.json reference

One `media.json` per app. Every path is relative to the file. Keys starting with `_` are comments.
Complete examples: [`examples/habits/media.json`](../examples/habits/media.json) (app) and
[`examples/tiles/media.json`](../examples/tiles/media.json) (game).

## app

| Key | Example | Used by |
| --- | --- | --- |
| `name` | `"Demo Tiles"` | logs |
| `bundle_id` | `"com.example.demotiles"` | App Store upload scripts (finds your app) |

## theme

| Key | Default | Meaning |
| --- | --- | --- |
| `top`, `mid`, `bottom` | `#2462e6`, `#1a4cc4`, `#10338f` | background gradient (top → bottom) |
| `glow` | `rgba(140,190,255,.25)` | soft light behind the device |
| `headline` | `#fff6dc` | headline line 1 colour |
| `accent` | `#ffd43b` | headline line 2 colour and the sparks |
| `shadow` | `rgba(0,0,0,.18)` | headline drop shadow |
| `pill_bg`, `pill_ink`, `pill_edge` | cream, navy, gold | bottom caption pill |
| `confetti` | 8 candy colours | small confetti dots; `[]` turns them off |
| `confetti_opacity` | `0.45` | |
| `sparks` | `true` | little lines beside the pill |
| `device_body` | `#111418` | colour of the drawn phone / tablet frame |

## devices

`["iphone69", "ipad13", "android_phone", "android_tablet7", "android_tablet10"]` — the devices
`kit.py check` validates. Render each with `kit.py shots <project> --device <name>`.

## slides (3–10 for the App Store, 2–8 for Google Play; 5 is the sweet spot)

```json
{ "tilt": 3, "device_width": 0.86, "raw": "01.png",
  "decos": [ { "src": "art/coin.png", "x": -70, "y": 2330, "w": 300, "rot": -14, "flip": false, "badge": false, "z": 5 } ] }
```

| Key | Meaning |
| --- | --- |
| `tilt` | device rotation in degrees. Keep most slides at 0, tilt 1–2 slides by ±3°. |
| `device_width` | device width as a fraction of the canvas (default 0.864 phone, 0.84 tablet) |
| `raw` | capture file name (default `NN.png` for slide N) |
| `decos` | your own small artwork in the corners. `x`, `y`, `w` are in **1320×2868 design pixels** and scale to every device. `badge: true` draws a white round border (for avatars). Decorations mirror automatically for right-to-left languages (`"mirror_rtl": false` to disable). |

Top-level options: `status_bar` (`"remove"` default: the system status bar is stripped from every
capture; `"keep"` for captures that have none, e.g. rendered by the app itself), `status_bar_px`
(per-device band height override, e.g. `{ "iphone69": 200 }`), `headline_right` (default 186, space kept free beside the headline for a
top-corner decoration), `headline_weight` (900), `headline_stretch` (`"62%"`), `fallback_locale` (`"en"`),
`raw_dir` (`"raw"`), `texts_dir` (`"texts"`), `out_dir` (`"out"`).

### Layouts

`"layout"` (top level, or per slide) picks the style:

| Layout | Look | Best for |
| --- | --- | --- |
| `framed` (default) | big headline at the top, the capture inside a device frame, caption pill at the bottom | apps, and games that want a polished look |
| `fullscreen` | the capture fills the whole image (no device frame), a rounded brand panel at the bottom with a two-line caption in a bold rounded font (line 1 gold, line 2 white) | **games**: the in-game screen speaks for itself |

Mixing both in one set works well (e.g. slides 2 and 4 fullscreen). For `fullscreen`, use captures
without buttons or HUD. Options:

```json
"fullscreen": { "panel_height": 0.2, "panel_top": "#2462e6", "panel_bottom": "#10338f", "panel_rim": "#ffd43b",
                "outline": "#0b2a7a", "line1_colors": ["#ffd43b", "#ff9f1a"], "line2_color": "#ffffff",
                "focus_y": 0, "font": "Baloo2", "upper": true }
```
`focus_y` = which part of a taller capture stays visible (0 top … 1 bottom); per slide `"focus_y"` too.
`fs_decos` (per slide) = decorations for this layout. Captions come from the same `line1` / `line2`
(the pill is not used).

### frame_png (optional)

Use your own device bezel instead of the drawn frame:

```json
"frame_png": { "src": "art/frame.png", "w": 1470, "h": 3000, "screen": [75, 67, 1320, 2866], "radius": 175 }
```
`screen` is the x, y, width, height of the screen opening inside the PNG.

## header

| Key | Default | Meaning |
| --- | --- | --- |
| `logo` | `art/logo.png` | transparent PNG, trimmed tightly |
| `logo_width` / `logo_width_wide` | `0.40` / `0.5625` | logo width: fraction of the banner width (or pixels if > 1). `_wide` applies to 3840×1646 and 1024×500. |
| `logo_top` / `logo_top_wide` | `45.5` / `49` | vertical centre in % of the height |
| `clouds` | `true` | soft clouds at the edges |

## store_locales / play_locales

Which store languages get which caption file:

```json
"store_locales": { "en": ["en-US", "en-GB", "en-AU"], "es": ["es-ES", "es-MX"], "pt-BR": ["pt-BR"] },
"play_locales":  { "en": ["en-US", "en-GB"], "es": ["es-ES", "es-419"], "pt-BR": ["pt-BR"] }
```
Apple locale codes: `en-US`, `de-DE`, `fr-FR`, `ja`, `zh-Hans`… Google Play codes: `en-US`, `de-DE`,
`fr-FR`, `ja-JP`, `zh-CN`… Store languages without screenshots show the primary language's set.

## video

```json
"video": {
  "width": 886, "height": 1920, "fps": 30,
  "transitions": "wipe", "stripes": true,
  "opening": { "image": "art/opening.png", "seconds": 2.4, "line1_size": 150, "line2_size": 200, "bottom": 240 },
  "shots": [
    { "clip": "clips/clip1.mp4", "seconds": 6, "push": [1.0, 1.03], "taps": "clips/clip1.taps.json", "trim": 0.5 },
    { "image": "raw/iphone69/en/02.png", "seconds": 5, "push": [1.05, 1.0], "taps": [ { "t": 1.2, "x": 0.5, "y": 0.6 } ] },
    { "clip": "clips/clip3.mp4", "seconds": 5, "focus": { "at": 1.0, "until": 2.6, "x": 0.5, "y": 0, "zoom": 1.22 } }
  ],
  "crop": { "scale": 1.0, "origin": "50% 100%" },
  "end": { "image": "art/opening.png", "logo": "art/logo.png", "logo_width": 700, "stars": false, "seconds": 3, "background": "#10338f" },
  "music": "audio/music.m4a", "music_volume": 0.85,
  "colors": { "headline": "#ffffff", "accent": "#ffd43b", "shadow": "#0b3f9e", "confetti": ["#fff", "#ffd43b"] }
}
```

| Key | Meaning |
| --- | --- |
| `width`, `height` | default canvas (886×1920 = 6.9" iPhone App Preview). `npm run render -- en --preset play` renders 1080×1920. |
| `transitions` | `wipe`, `slide` or `fade` between shots; `stripes` adds a brand-colour sweep on cuts |
| `opening` | background image under the title (title text comes from `texts/<locale>.json → video`) |
| `shots[].clip` / `.image` | a screen recording, or a still screenshot animated with a slow camera move |
| `shots[].seconds` | how long the shot stays (the whole video must be 15–30 s for Apple) |
| `shots[].push` | camera zoom from → to over the shot |
| `shots[].taps` | tap ripples: inline list or a JSON file `{ "events": [ { "t", "x", "y" } ] }` (seconds; x/y 0–1) |
| `shots[].focus` | glide-in zoom between `at` and `until` seconds towards `x`, `y` (0 = top edge) |
| `shots[].trim` | skip the first seconds of a clip |
| `crop` | zoom every clip, e.g. `{ "scale": 1.07, "origin": "50% 100%" }` keeps a simulator's status bar and Dynamic Island out of frame (screenshots used as shots are cleaned automatically) |
| `end` | logo end card; `stars: true` adds three bouncing stars (nice for games) |
| `music` | an audio file in `video/public/`; it fades in and out |

All media paths are relative to `<project>/video/public/`. `kit.py video <project>` copies the files
that `media.json` points at from your project into `video/public/` for you.

## preview (App Store upload)

```json
"preview": { "store_locales": ["en-US", "en-GB"], "poster": "00:00:01:15", "file": "video/out/en.mp4", "type": "IPHONE_67" }
```
`poster` is the still frame shown before playback (HH:MM:SS:FF) — put it on your opening title.
