# Store specs (what the stores accept)

Always double-check the official pages before a release — stores change their rules:
[App Store screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications) ·
[App preview specifications](https://developer.apple.com/help/app-store-connect/reference/app-preview-specifications) ·
[Google Play preview assets](https://support.google.com/googleplay/android-developer/answer/9866151).

## App Store (Apple)

| Asset | Size used by the kit | Rules |
| --- | --- | --- |
| iPhone screenshots | **1320×2868** (6.9") | 1–10 per language; the 6.9" set is scaled down for smaller iPhones |
| iPad screenshots | **2064×2752** (13") | required if your app runs on iPad; 1–10 per language |
| App Preview video | **886×1920** (6.9" iPhone) | 15–30 s, H.264 or ProRes, ≤ 500 MB, up to 3 per language; set a poster frame |
| Product page header ("creative asset") | **5244×2950** or **3840×1646** | uploaded in App Store Connect (no API); check *Device Preview → iPhone* |
| Format | PNG or JPEG, RGB, no transparency | |

Languages without their own screenshots or video use the primary language's.

## Google Play

| Asset | Size used by the kit | Rules |
| --- | --- | --- |
| Phone screenshots | **1080×1920** | 2–8, 16:9 or 9:16, each side 320–3840 px, PNG/JPEG without alpha, ≤ 8 MB |
| 7" tablet screenshots | **1200×1920** | up to 8 |
| 10" tablet screenshots | **1600×2560** | up to 8 |
| Feature graphic | **1024×500** | required; JPEG or 24-bit PNG without alpha |
| Promo video | a **YouTube URL** | render `--preset play` (1080×1920), upload to YouTube, paste the link in Play Console |
| App icon | 512×512 | not made by this kit |

## Text in images

Neither store indexes text inside screenshots for search, but both review it: don't promise features
the app doesn't have, don't show prices that differ by country, and avoid "#1 / best" claims unless
you can prove them.
