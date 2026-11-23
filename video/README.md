# Preview video template (Remotion)

Created inside a project by `python3 kit.py video <project>`. It reads `../media.json` (`video`) and
`../texts/<locale>.json` (`video.line1/line2`); media files live in `public/`.

```bash
npm install
npm run studio                      # live preview at http://localhost:3000
npm run render -- en                # out/en.mp4       886×1920 App Store App Preview
npm run render -- de --preset play  # out/de-play.mp4  1080×1920 Google Play / YouTube
```

Edit `src/Composition.tsx` for deeper changes (opening, ripples, transitions, end card).
Remotion is free for individuals and small companies; larger companies need a
[Remotion company license](https://www.remotion.dev/license).
