# Design rules that make store media convert

Learned the hard way while shipping real apps. The defaults of the kit already follow them.

## Screenshots

1. **The first slide is the ad.** Most people never swipe. Show the core loop / main value and the
   strongest search keyword there.
2. **Headline: two short lines, keyword first.** `MATCH 3 / PUZZLE.` reads in one glance. Long
   sentences shrink to nothing on a phone.
3. **No subtitle under the headline.** One headline + one short caption pill at the bottom is enough.
4. **Big device.** The app is the product — let the device fill the canvas and bleed off the bottom.
5. **Every slide a different moment.** Never the same screen twice; one feature per slide.
6. **Tilt sparingly.** One or two slides at ±3° add rhythm; tilting all of them looks messy.
7. **One strong brand colour.** A single bold gradient beats patterns; light confetti at most.
8. **Clean captures, no status bar.** No clock / battery / signal bar (the kit removes it), no debug
   banners, no notifications, no half-loaded states, realistic tidy data.
   For games, avoid HUD clutter (score popups, combo text, menus) in the capture.
9. **Your own art only.** Small decorations from your app in the corners; never other brands.
10. **No numbers that change** (level counts, prices, user counts) and no claims you can't keep.
11. **Localise for each market**, using the words people there search for. Keep feature names identical
    to the app.

## Preview video

1. **Text only at the start.** A short title, then only real use of the app.
2. **Calm camera.** Slow push, gentle zoom towards the action; no fast cuts or shaky motion.
   No status bar in any frame (crop it out of recordings).
3. **Show touches.** Tap ripples or a pointing hand make it obvious what the user does.
4. **End on the logo** and let the music fade out — never stop abruptly.
5. **Poster frame on the title**, not on a random frame.
6. **One video in your main language is often enough**; other languages show it automatically.

## Header / feature graphic

- Only the logo on the brand background (plus subtle clouds/confetti). No phones, prices or text walls.
- On the App Store, only the central band shows on iPhone and the status bar covers the top —
  keep the logo central and check it in App Store Connect's Device Preview.
