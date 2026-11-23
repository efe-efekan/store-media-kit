# AGENTS.md — instructions for AI assistants

You are helping someone make **store media** for their app with store-media-kit: App Store and
Google Play screenshots, the App Store product page header, the Google Play feature graphic and
a preview video. This file is the single source of truth for any assistant (Claude, ChatGPT/Codex,
Gemini, Copilot, Cursor, Aider…). `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` and
`.cursor/rules/` point here.

Reply in the user's language. Keep them in the loop: show results, ask before anything irreversible.

## 0. Ground rules

- **Never upload, overwrite or delete anything in App Store Connect or Google Play Console without the
  user's explicit "yes" for that specific upload.** Rendering locally is always fine.
- **Never write credentials** (Apple ID, passwords, API keys, Play service-account JSON, team ids) into
  any file of this repo or the user's project. Read them from environment variables
  (`FASTLANE_USER`, `FASTLANE_TEAM_ID`, `SUPPLY_JSON_KEY`) that the user sets.
- **Use real captures of the user's app.** Never invent UI, never mock a screen, never use another
  company's artwork, logos or characters.
- Don't commit the user's `out/`, raw captures with personal data, or anything under `node_modules/`.
- Run `python3 kit.py check <project>` before rendering and fix every error it prints.

## 1. Learn the app (ask, don't guess)

Ask the user, in one message:
1. App name, one-line pitch, game or not, target stores (App Store / Google Play / both), devices (iPhone, iPad, Android phone/tablets).
2. The 5 things a new user should see, in order (slide 1 = the core loop / main value).
3. Brand colours (or a screenshot / icon to pick them from) and their logo file.
4. Languages to ship.
If they already have an App Store or Play listing, read its keywords/title and reuse those words.

## 2. Set up a project

```bash
python3 <kit>/kit.py doctor                    # fix anything marked --
python3 <kit>/kit.py init <app>/store-media    # creates media.json, texts/, raw/, art/
python3 <kit>/kit.py fonts                     # once, if any locale is ja/ko/zh/th/hi/ar/he
```

Fill `media.json` (reference: `docs/MEDIA-JSON.md`): `app`, `theme` colours, `devices`, 5 `slides`
(tilt only 1–2 of them by ±3°), `store_locales` / `play_locales`, `header.logo`.

## 3. Capture clean screens

Follow `docs/CAPTURE.md`. Targets: iPhone `raw/iphone69/en/NN.png` 1320×2868 (iPhone 6.9" simulator),
iPad `raw/ipad13/en/` 2064×2752, Android `raw/android_phone/en/` 1080×1920.
- iOS: `capture/ios/still.sh <udid> <out.png>` (sets 9:41, full battery). Android: `capture/android/still.sh <out.png>`.
- Hide debug banners, test data, personal names/e-mails, notifications, sign-in walls. Use tidy, realistic demo content.
- For games, prefer moments without heavy HUD clutter; show different moments on every slide.
- If UI has no text, one English set serves every language; otherwise capture per locale (`raw/<device>/<locale>/`).

## 4. Write captions (texts/<locale>.json)

```json
{ "slides": [ { "line1": "MATCH 3", "line2": "PUZZLE.", "pill": "TAP. MATCH. CLEAR." } ],
  "video": { "line1": "MATCH.", "line2": "COMBO. WIN." } }
```
- `line1` + `line2` = one short headline split in two (≤ ~14 characters per line), **keyword-driven**
  (words people search for), the second line is highlighted. **No subtitle.**
- `pill` = ≤ 3 short words or one benefit, uppercase.
- No numbers that will change ("500 levels"), no unverifiable claims ("#1", "best", "always solvable").
- Every language is **written for its market** (search terms people actually use), not translated
  word by word. Keep product and feature names exactly as the app shows them.
- CJK / Thai / Hindi: use `·` or `・` between words in pills; no trailing periods needed.

## 5. Render and review

```bash
python3 <kit>/kit.py check <project>
python3 <kit>/kit.py shots <project> --locale en           # then --device ipad13 / android_phone
python3 <kit>/kit.py sheet <project> --locale en           # out/sheet_<device>.jpg
```
Look at the sheet yourself before showing it: headline readable, device big, nothing cut off,
decorations not covering the app, every slide different. Show the user **English (+ their own
language)** first; render the other languages only after they approve.

## 6. Banners

```bash
python3 <kit>/kit.py header <project> --size 3840x1646     # App Store header (also 5244x2950)
python3 <kit>/kit.py feature <project>                     # Google Play 1024x500
```
Header = only the logo on the brand background. On iPhone only a central band shows; tune
`header.logo_width_wide` / `logo_top_wide` if the user reports it looks small or high.

## 7. Preview video

```bash
python3 <kit>/kit.py video <project>
cd <project>/video && npm install && npm run render -- en              # App Store 886×1920
npm run render -- en --preset play                                     # Google Play / YouTube 1080×1920
```
- Text only in the opening title; after that only real use of the app. Calm camera, no fast cuts.
- 15–30 s total (Apple). End card with the logo, music fades out.
- Shots can be screen recordings (`clip`) or screenshots (`image`); add `taps` for ripples.
- After uploading to Apple, set the poster frame on the opening title (`upload/set_poster.rb`).

## 8. Upload (only after explicit approval)

App Store: `kit.py fastlane <project> <app>/fastlane/screenshots [--device ipad13]`, then the user's
`fastlane ios upload_screenshots_only` (lanes in `upload/Fastfile.snippet`). Videos:
`upload/upload_previews.rb`. Then always `upload/verify_media.rb` and report counts per locale.
Google Play: `kit.py fastlane <project> <app>/fastlane/metadata/android --device android_phone`, then
`fastlane android upload_play_images`. Play promo video = YouTube URL (the user uploads it).
Use `LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8` with fastlane when texts are not ASCII.

## 9. When something looks wrong

| Symptom | Fix |
| --- | --- |
| Tofu boxes / wrong glyphs in ja/ko/zh/th/hi/ar/he | `python3 kit.py fonts`, render again |
| Headline tiny | caption too long: shorten `line1`/`line2` (`kit.py check` warns at 22 chars) |
| Capture cropped / stretched | wrong size: recapture on the right simulator / emulator (`kit.py check` warns) |
| Decoration covers the app | move it (`x`, `y` in 1320×2868 design pixels) or shrink `w` |
| Play rejects images | screenshots must be PNG/JPEG without alpha (the kit flattens them) and 2–8 per device |
| Apple rejects the video | 15–30 s, H.264, ≤ 500 MB, exact size for the device |

## Repo map

`kit.py` CLI · `kit/screens.py` screenshot HTML template · `kit/header.py` banners · `kit/common.py`
devices, fonts, Chrome · `video/` Remotion template · `upload/` App Store Connect scripts + Fastfile lanes ·
`capture/` iOS / Android / Flutter capture · `examples/` two fictional demo apps · `docs/` guides.
