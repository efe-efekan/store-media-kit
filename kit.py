#!/usr/bin/env python3
"""store-media-kit: store screenshots, banners and preview videos for any app (App Store + Google Play).

    python3 kit.py doctor                         # what is installed / missing
    python3 kit.py init  <folder>                 # new project from the template
    python3 kit.py fonts                          # one-time: CJK / Thai / Hindi / Arabic / Hebrew fonts
    python3 kit.py check <project>                # config, texts, captures and store limits
    python3 kit.py shots <project> [--device iphone69] [--locale en,tr] [--slides 1,4]
    python3 kit.py sheet <project> [--device iphone69] [--locale en,tr]   # one image to review
    python3 kit.py header <project> [--size 5244x2950|3840x1646]          # App Store header
    python3 kit.py feature <project>              # Google Play feature graphic 1024x500
    python3 kit.py video <project>                # set up <project>/video (Remotion) for the preview video
    python3 kit.py fastlane <project> <dir> [--device iphone69]          # copy into fastlane folders

Devices: iphone69 (6.9" iPhone), ipad13 (13" iPad), android_phone, android_tablet7, android_tablet10.
<project> is the folder that holds media.json. Full guide: README.md.
"""
import argparse
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import common, header, screens  # noqa: E402

KIT = common.KIT
DEVICE_CHOICES = sorted(common.DEVICES)


# ---------- setup ----------
def cmd_doctor(_):
    ok = True

    def row(name, good, hint=''):
        nonlocal ok
        ok &= good or name.startswith('(optional)')
        print(f'  {"OK " if good else "-- "} {name}{"" if good else "   -> " + hint}')

    print('store-media-kit doctor')
    row('Python 3.9+', sys.version_info >= (3, 9), 'install Python 3.9 or newer')
    try:
        import PIL  # noqa: F401
        row('Pillow', True)
    except ImportError:
        row('Pillow', False, 'pip3 install pillow')
    try:
        common.chrome()
        row('Google Chrome / Chromium', True)
    except SystemExit:
        row('Google Chrome / Chromium', False, 'install Chrome or set CHROME=/path/to/chrome')
    row('(optional) Node.js + npm, for videos', bool(shutil.which('node') and shutil.which('npm')), 'https://nodejs.org (20+)')
    fonts = all(os.path.exists(os.path.join(common.EXT_FONTS, p, 'package', 'index.css')) for p in common.FONT_PACKAGES)
    row('(optional) CJK/Thai/Hindi/Arabic/Hebrew fonts', fonts, 'python3 kit.py fonts')
    row('(optional) Xcode simulators (iOS captures)', platform.system() == 'Darwin' and bool(shutil.which('xcrun')), 'macOS + Xcode')
    row('(optional) adb (Android captures)', bool(shutil.which('adb')), 'Android SDK platform-tools')
    row('(optional) fastlane (uploads)', bool(shutil.which('fastlane') or shutil.which('bundle')), 'https://docs.fastlane.tools')
    print('ready.' if ok else 'fix the lines marked -- first.')
    sys.exit(0 if ok else 1)


def cmd_init(a):
    dst = os.path.abspath(a.project)
    if os.path.exists(os.path.join(dst, 'media.json')):
        raise SystemExit(f'{dst}/media.json already exists')
    shutil.copytree(os.path.join(KIT, 'template'), dst, dirs_exist_ok=True)
    vdst = os.path.join(dst, 'video')
    shutil.copytree(os.path.join(KIT, 'video'), vdst, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('node_modules', 'out', '.remotion'))
    if os.path.isdir(common.EXT_FONTS):
        shutil.copytree(common.EXT_FONTS, os.path.join(vdst, 'public', 'fonts', 'ext'), dirs_exist_ok=True)
    kit = os.path.join(KIT, 'kit.py')
    print(f'''new project: {dst}

  1. edit media.json (app name, colours, slides, languages) and texts/en.json
  2. put clean screenshots of your app in raw/iphone69/en/01.png ... (see docs/CAPTURE.md)
  3. python3 {kit} check {dst}
  4. python3 {kit} shots {dst}
  5. python3 {kit} sheet {dst}      -> out/sheet_iphone69.jpg to review everything at once
  video: cd {vdst} && npm install && npm run studio''')


def cmd_fonts(_):
    os.makedirs(common.EXT_FONTS, exist_ok=True)
    if not shutil.which('npm'):
        raise SystemExit('npm is needed to download the fonts (https://nodejs.org)')
    for pkg in common.FONT_PACKAGES:
        dst = os.path.join(common.EXT_FONTS, pkg)
        if os.path.exists(os.path.join(dst, 'package', 'index.css')):
            print('ok', pkg)
            continue
        tmp = tempfile.mkdtemp()
        subprocess.run(['npm', 'pack', f'@fontsource-variable/{pkg}', '--silent'], cwd=tmp, check=True,
                       stdout=subprocess.DEVNULL)
        tgz = next(f for f in os.listdir(tmp) if f.endswith('.tgz'))
        os.makedirs(dst, exist_ok=True)
        with tarfile.open(os.path.join(tmp, tgz)) as t:
            try:
                t.extractall(dst, filter='data')
            except TypeError:  # Python < 3.12
                t.extractall(dst)
        shutil.rmtree(tmp, ignore_errors=True)
        print('downloaded', pkg)


def cmd_video(a):
    """Creates / refreshes <project>/video from the template and copies every file media.json
    "video" points at (opening image, logo, screenshots used as shots…) into video/public/."""
    import json
    cfg = common.load_config(a.project)
    vdst = common.project_path(cfg, 'video')
    shutil.copytree(os.path.join(KIT, 'video'), vdst, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('node_modules', 'out', '.remotion'))
    if os.path.isdir(common.EXT_FONTS):
        shutil.copytree(common.EXT_FONTS, os.path.join(vdst, 'public', 'fonts', 'ext'), dirs_exist_ok=True)
    v = cfg.get('video') or {}
    refs = [v.get('opening', {}).get('image'), v.get('end', {}).get('image'), v.get('end', {}).get('logo'), v.get('music')]
    for s in v.get('shots', []):
        refs += [s.get('clip'), s.get('image'), s.get('taps') if isinstance(s.get('taps'), str) else None]
    copied = 0
    raw_dir = cfg.get('raw_dir', 'raw')
    for r in filter(None, refs):
        src = common.project_path(cfg, r)
        dst = os.path.join(vdst, 'public', r)
        if os.path.exists(src):
            parts = r.replace('\\', '/').split('/')
            if len(parts) > 2 and parts[0] == raw_dir and parts[1] in common.DEVICES:
                src = common.clean_capture(cfg, src, parts[1])  # screenshots: status bar removed
            elif os.path.exists(dst):
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
            copied += 1
        elif not os.path.exists(dst):
            print(f'  ! {r}: put this file in {os.path.join(vdst, "public", r)}')
    print(f'video project ready: {vdst} ({copied} files copied into public/)\n'
          f'  cd {vdst} && npm install && npm run studio      # live preview\n'
          f'  npm run render -- en                            # out/en.mp4 for the App Store\n'
          f'  npm run render -- en --preset play              # out/en-play.mp4 for Google Play / YouTube')


# ---------- render ----------
def locales_arg(cfg, value):
    return [x.strip() for x in value.split(',') if x.strip()] if value else common.text_locales(cfg)


def cmd_shots(a):
    cfg = common.load_config(a.project)
    only = {int(x) for x in a.slides.split(',')} if a.slides else None
    for loc in locales_arg(cfg, a.locale):
        screens.render(cfg, loc, a.device, only)


def cmd_header(a):
    header.render(common.load_config(a.project), a.size)


def cmd_feature(a):
    header.render(common.load_config(a.project), '1024x500')


def cmd_sheet(a):
    from PIL import Image
    cfg = common.load_config(a.project)
    base = common.project_path(cfg, cfg.get('out_dir', 'out'), 'screenshots', a.device)
    locs = [l for l in locales_arg(cfg, a.locale) if os.path.isdir(os.path.join(base, l))]
    n = len(cfg['slides'])
    tw = 240
    rows = []
    for loc in locs:
        ims = [Image.open(os.path.join(base, loc, f'{i:02d}.png')).convert('RGB') for i in range(1, n + 1)
               if os.path.exists(os.path.join(base, loc, f'{i:02d}.png'))]
        if ims:
            th = int(tw * ims[0].height / ims[0].width)
            rows.append([im.resize((tw, th)) for im in ims])
    if not rows:
        raise SystemExit(f'nothing rendered yet for {a.device}: run `kit.py shots {a.project} --device {a.device}`')
    th = rows[0][0].height
    sheet = Image.new('RGB', (n * (tw + 8), len(rows) * (th + 8)), (24, 24, 32))
    for r, row in enumerate(rows):
        for c, im in enumerate(row):
            sheet.paste(im, (c * (tw + 8), r * (th + 8)))
    out = common.project_path(cfg, cfg.get('out_dir', 'out'), f'sheet_{a.device}.jpg')
    sheet.save(out, quality=85)
    print('wrote', os.path.relpath(out, cfg['_dir']), f'({len(rows)} locales: {", ".join(locs)})')


# ---------- hand-off to fastlane ----------
def cmd_fastlane(a):
    """Apple: <dir>/<store-locale>/NN_<device>.png (deliver).
    Google: <dir>/<play-locale>/images/<phoneScreenshots|...>/N.png (supply, metadata/android)."""
    cfg = common.load_config(a.project)
    dev = common.DEVICES[a.device]
    base = common.project_path(cfg, cfg.get('out_dir', 'out'), 'screenshots', a.device)
    key = 'play_locales' if dev['store'] == 'google' else 'store_locales'
    mapping = cfg.get(key) or {l: [l] for l in common.text_locales(cfg)}
    count = 0
    for text_loc, store_locs in mapping.items():
        src_dir = os.path.join(base, text_loc)
        if not os.path.isdir(src_dir):
            print(f'  ! {text_loc}: not rendered for {a.device}, skipped')
            continue
        pngs = sorted(f for f in os.listdir(src_dir) if f.endswith('.png'))
        for store_loc in store_locs:
            if dev['store'] == 'google':
                dst = os.path.join(a.fastlane, store_loc, 'images', dev['play'])
                os.makedirs(dst, exist_ok=True)
                for f in os.listdir(dst):
                    if f.endswith('.png'):
                        os.remove(os.path.join(dst, f))
                for i, f in enumerate(pngs, 1):
                    shutil.copy(os.path.join(src_dir, f), os.path.join(dst, f'{i}.png'))
                    count += 1
            else:
                dst = os.path.join(a.fastlane, store_loc)
                os.makedirs(dst, exist_ok=True)
                for f in os.listdir(dst):
                    if f.endswith(f'_{a.device}.png'):
                        os.remove(os.path.join(dst, f))
                for f in pngs:
                    shutil.copy(os.path.join(src_dir, f), os.path.join(dst, f'{f[:-4]}_{a.device}.png'))
                    count += 1
    if dev['store'] == 'google':
        fg = common.project_path(cfg, cfg.get('out_dir', 'out'), 'header', 'feature_graphic.png')
        if os.path.exists(fg):
            for store_locs in mapping.values():
                for store_loc in store_locs:
                    dst = os.path.join(a.fastlane, store_loc, 'images')
                    os.makedirs(dst, exist_ok=True)
                    shutil.copy(fg, os.path.join(dst, 'featureGraphic.png'))
    print(f'copied {count} files into {a.fastlane}')


# ---------- checks ----------
def cmd_check(a):
    cfg = common.load_config(a.project)
    errors, warnings = [], []
    n = len(cfg.get('slides', []))
    if not n:
        errors.append('media.json has no slides')
    devices = cfg.get('devices', ['iphone69'])
    for d in devices:
        if d not in common.DEVICES:
            errors.append(f'unknown device "{d}" (use one of: {", ".join(DEVICE_CHOICES)})')
            continue
        lo, hi = common.STORE_LIMITS[common.DEVICES[d]['store']]
        if not lo <= n <= hi:
            errors.append(f'{d}: {common.DEVICES[d]["store"]} store accepts {lo}-{hi} screenshots, you have {n} slides')
    for loc in common.text_locales(cfg):
        t = common.load_texts(cfg, loc)
        if len(t.get('slides', [])) != n:
            errors.append(f'texts/{loc}.json: {len(t.get("slides", []))} slides, media.json has {n}')
        for i, s in enumerate(t.get('slides', []), 1):
            for k in ('line1', 'line2'):
                if not s.get(k):
                    errors.append(f'texts/{loc}.json slide {i}: empty {k}')
                elif len(s[k]) > 22:
                    warnings.append(f'texts/{loc}.json slide {i}: {k} is {len(s[k])} chars, it will be small (keep it short)')
            if len(s.get('pill', '')) > 30:
                warnings.append(f'texts/{loc}.json slide {i}: pill is {len(s["pill"])} chars (keep it under ~25)')
    for dev in devices:
        if dev not in common.DEVICES:
            continue
        want = common.DEVICES[dev]
        for i, slide in enumerate(cfg.get('slides', []), 1):
            try:
                shot = screens.raw_capture(cfg, cfg.get('fallback_locale', 'en'), dev, i, slide)
                w, h = common.image_size(shot)
                if abs(w / h - want['w'] / want['h']) > 0.03:
                    warnings.append(f'{os.path.relpath(shot, cfg["_dir"])}: {w}x{h}, a {want["label"]} capture is {want["w"]}x{want["h"]} (it will be cropped)')
            except SystemExit as e:
                errors.append(str(e))
    for i, slide in enumerate(cfg.get('slides', []), 1):
        for d in slide.get('decos', []):
            srcs = [d['src']]
            if '{locale}' in d['src']:  # per-language image: check every text locale
                srcs = [d['src'].replace('{locale}', loc) for loc in common.text_locales(cfg)] or [d['src']]
            for src in srcs:
                if not os.path.exists(common.project_path(cfg, src)):
                    errors.append(f'slide {i}: missing decoration {src}')
    for key in ('store_locales', 'play_locales'):
        mapped = set(cfg.get(key, {}))
        for loc in mapped - set(common.text_locales(cfg)):
            errors.append(f'{key}: "{loc}" has no texts/{loc}.json')
    if cfg.get('status_bar', 'remove') == 'keep':
        warnings.append('"status_bar": "keep" - make sure no capture shows a clock, battery or signal (stores may reject it)')
    for w in warnings:
        print('warning:', w)
    for e in errors:
        print('error:  ', e)
    print('ok' if not errors else f'{len(errors)} error(s)')
    sys.exit(1 if errors else 0)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('doctor', help='check what is installed'); s.set_defaults(f=cmd_doctor)
    s = sub.add_parser('init', help='new project'); s.add_argument('project'); s.set_defaults(f=cmd_init)
    s = sub.add_parser('fonts', help='download non-Latin fonts once'); s.set_defaults(f=cmd_fonts)
    s = sub.add_parser('check', help='validate a project'); s.add_argument('project'); s.set_defaults(f=cmd_check)
    s = sub.add_parser('shots', help='render screenshots'); s.add_argument('project'); s.add_argument('--locale')
    s.add_argument('--slides'); s.add_argument('--device', default='iphone69', choices=DEVICE_CHOICES); s.set_defaults(f=cmd_shots)
    s = sub.add_parser('sheet', help='one review image of every locale'); s.add_argument('project'); s.add_argument('--locale')
    s.add_argument('--device', default='iphone69', choices=DEVICE_CHOICES); s.set_defaults(f=cmd_sheet)
    s = sub.add_parser('header', help='App Store product page header'); s.add_argument('project')
    s.add_argument('--size', default='5244x2950', choices=['5244x2950', '3840x1646']); s.set_defaults(f=cmd_header)
    s = sub.add_parser('feature', help='Google Play feature graphic 1024x500'); s.add_argument('project'); s.set_defaults(f=cmd_feature)
    s = sub.add_parser('video', help='set up the preview video project'); s.add_argument('project'); s.set_defaults(f=cmd_video)
    s = sub.add_parser('fastlane', help='copy renders into fastlane folders'); s.add_argument('project'); s.add_argument('fastlane')
    s.add_argument('--device', default='iphone69', choices=DEVICE_CHOICES); s.set_defaults(f=cmd_fastlane)
    a = p.parse_args()
    a.f(a)


if __name__ == '__main__':
    main()
