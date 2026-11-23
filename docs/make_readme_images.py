#!/usr/bin/env python3
"""Rebuilds the README images in docs/images from the two example projects.

    python3 examples/make_examples.py          # example captures + art
    python3 kit.py shots examples/habits --device iphone69   (and ipad13, android_phone; same for tiles)
    python3 kit.py header examples/tiles --size 3840x1646 && python3 kit.py feature examples/tiles
    python3 docs/make_readme_images.py [video-frames-dir]
"""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from kit.common import FONTS, render_html, url  # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'images')
EX = os.path.join(ROOT, 'examples')


def shot(ex, dev, loc, n):
    return url(os.path.join(EX, ex, 'out', 'screenshots', dev, loc, f'{n:02d}.png'))


CSS = f'''<style>
@font-face{{font-family:Archivo;src:url({url(os.path.join(FONTS, 'archivo-latin-wdth-normal.woff2'))}) format('woff2');font-weight:100 900;font-stretch:62% 125%;}}
html,body{{margin:0;overflow:hidden;font-family:Archivo,-apple-system,sans-serif;color:#fff}}
body{{background:radial-gradient(1200px 600px at 20% 0%,#2b3a8f 0,transparent 60%),radial-gradient(900px 600px at 100% 100%,#5a1f9e 0,transparent 55%),#0d1024}}
.row{{display:flex;gap:28px;align-items:flex-end;justify-content:center}}
.card{{border-radius:22px;box-shadow:0 30px 60px rgba(0,0,0,.45);display:block}}
.lab{{text-align:center;font-weight:700;font-size:22px;opacity:.85;margin-top:14px;letter-spacing:.02em}}
h1{{font-weight:900;font-stretch:75%;font-size:96px;margin:0;letter-spacing:-.01em;line-height:1}}
p.sub{{font-size:30px;opacity:.85;margin:16px 0 0}}
</style>'''


def page(body, w, h, name):
    render_html(f'<!doctype html><html><head><meta charset="utf-8">{CSS}</head><body style="width:{w}px;height:{h}px">{body}</body></html>',
                os.path.join(OUT, name), w, h)
    # README images as compact JPEGs
    from PIL import Image
    p = os.path.join(OUT, name)
    Image.open(p).convert('RGB').save(p[:-4] + '.jpg', quality=86, optimize=True)
    os.remove(p)
    print('wrote docs/images/' + name[:-4] + '.jpg')


def main():
    os.makedirs(OUT, exist_ok=True)
    # 1. hero
    fan = [('tiles', 1, -8, 40), ('habits', 1, -4, 10), ('tiles', 4, 0, 0), ('habits', 2, 4, 10), ('tiles', 2, 8, 40)]
    cards = ''.join(f'<img class="card" src="{shot(ex, "iphone69", "en", n)}" style="width:250px;transform:rotate({r}deg) translateY({y}px)">'
                    for ex, n, r, y in fan)
    page(f'''<div style="padding:70px 80px 0"><h1>store-media-kit</h1>
      <p class="sub">App Store &amp; Google Play screenshots, banners and preview videos for any app.</p></div>
      <div class="row" style="margin-top:50px">{cards}</div>''', 1600, 980, 'hero.png')
    # 2. devices
    page(f'''<div class="row" style="padding:60px 60px 0;align-items:flex-end">
      <div><img class="card" src="{shot('tiles', 'iphone69', 'en', 1)}" style="height:640px"><div class="lab">iPhone 6.9"</div></div>
      <div><img class="card" src="{shot('tiles', 'ipad13', 'en', 1)}" style="height:640px"><div class="lab">iPad 13"</div></div>
      <div><img class="card" src="{shot('tiles', 'android_phone', 'en', 1)}" style="height:640px"><div class="lab">Android phone</div></div>
      </div>''', 1600, 820, 'devices.png')
    # 3. languages
    langs = [('en', 'English'), ('es', 'Español'), ('ja', '日本語'), ('ar', 'العربية'), ('tr', 'Türkçe')]
    page('<div class="row" style="padding:60px 50px 0">' + ''.join(
        f'<div><img class="card" src="{shot("habits", "iphone69", l, 1)}" style="width:270px"><div class="lab">{t}</div></div>'
        for l, t in langs) + '</div>', 1600, 770, 'languages.png')
    # 4. both example sets
    rows = ''.join('<div class="row" style="margin-bottom:34px">' + ''.join(
        f'<img class="card" src="{shot(ex, "iphone69", "en", n)}" style="width:260px">' for n in range(1, 6)) + '</div>'
        for ex in ('habits', 'tiles'))
    page(f'<div style="padding:50px 40px 0">{rows}</div>', 1600, 1260, 'examples.png')
    # 5. banners
    page(f'''<div style="padding:60px 70px">
      <img class="card" src="{url(os.path.join(EX, 'tiles', 'out', 'header', 'header_3840x1646.png'))}" style="width:1460px">
      <div class="lab" style="text-align:left">App Store product page header (3840x1646 / 5244x2950)</div>
      <div style="display:flex;gap:40px;margin-top:40px;align-items:flex-end">
      <div><img class="card" src="{url(os.path.join(EX, 'habits', 'out', 'header', 'feature_graphic.png'))}" style="width:700px">
      <div class="lab" style="text-align:left">Google Play feature graphic (1024x500)</div></div>
      <div><img class="card" src="{url(os.path.join(EX, 'tiles', 'out', 'header', 'feature_graphic.png'))}" style="width:700px">
      <div class="lab" style="text-align:left">&nbsp;</div></div></div></div>''', 1600, 1150, 'banners.png')
    # 6. video frames
    frames = sys.argv[1] if len(sys.argv) > 1 else ''
    if frames and os.path.isdir(frames):
        rows = ''
        for ex in ('tiles', 'habits'):
            fs = sorted(glob.glob(os.path.join(frames, f'{ex}_*.png')), key=lambda f: float(os.path.basename(f)[len(ex) + 1:-4]))
            rows += '<div class="row" style="margin-bottom:30px">' + ''.join(
                f'<img class="card" src="{url(f)}" style="width:270px;border-radius:18px">' for f in fs) + '</div>'
        page(f'<div style="padding:50px 40px 0">{rows}</div>', 1600, 1300, 'video.png')


if __name__ == '__main__':
    main()
