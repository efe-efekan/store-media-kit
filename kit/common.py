"""Shared helpers: devices, config loading, paths, headless Chrome, fonts."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(KIT, 'assets')
FONTS = os.path.join(ASSETS, 'fonts')
EXT_FONTS = os.path.join(FONTS, 'ext')  # downloaded by `kit.py fonts`, not committed

# Store canvas sizes (portrait). `frame`: phone | tablet. `notch`: island | punch | none.
# `status_bar`: height in px of the system status bar (clock, battery, signal) at the native
# size; the kit removes it from every capture (see clean_capture) because a visible status bar
# can get a listing rejected and always looks unfinished.
DEVICES = {
    # Apple App Store
    'iphone69': dict(w=1320, h=2868, frame='phone', notch='island', store='apple', status_bar=168,
                     asc='APP_IPHONE_67', label='iPhone 6.9"'),
    'ipad13': dict(w=2064, h=2752, frame='tablet', notch='none', store='apple', status_bar=52,
                   asc='APP_IPAD_PRO_3GEN_129', label='iPad 13"'),
    # Google Play
    'android_phone': dict(w=1080, h=1920, frame='phone', notch='punch', store='google', status_bar=72,
                          play='phoneScreenshots', label='Android phone'),
    'android_tablet7': dict(w=1200, h=1920, frame='tablet', notch='none', store='google', status_bar=64,
                            play='sevenInchScreenshots', label='Android 7" tablet'),
    'android_tablet10': dict(w=1600, h=2560, frame='tablet', notch='none', store='google', status_bar=72,
                             play='tenInchScreenshots', label='Android 10" tablet'),
}

# How many screenshots each store accepts per device.
STORE_LIMITS = {'apple': (1, 10), 'google': (2, 8)}

DEFAULT_THEME = dict(
    top='#2462e6', mid='#1a4cc4', bottom='#10338f',      # background gradient
    glow='rgba(140,190,255,.25)',                         # soft light behind the device
    headline='#fff6dc', accent='#ffd43b',                 # line 1 / line 2 colours
    shadow='rgba(0,0,0,.18)',                             # headline drop
    pill_bg='#fff5d6', pill_ink='#10338f', pill_edge='#e0a800',
    confetti=['#ff4d5e', '#ffb020', '#ffd43b', '#3dd68c', '#3aa0ff', '#a25cff', '#ff6fb5', '#28d0e0'],
    confetti_opacity=0.45,
    sparks=True,                                          # little sparks beside the pill
    device_body='#111418',                                # phone / tablet frame colour
)


def chrome():
    candidates = [
        os.environ.get('CHROME', ''),
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        shutil.which('google-chrome') or '',
        shutil.which('google-chrome-stable') or '',
        shutil.which('chromium') or '',
        shutil.which('chromium-browser') or '',
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    raise SystemExit('Google Chrome or Chromium not found. Install it or set CHROME=/path/to/chrome.')


def url(path):
    p = os.path.abspath(path).replace('\\', '/')
    return 'file://' + ('' if p.startswith('/') else '/') + p


def load_config(path):
    """Reads <project>/media.json; every relative path in it is relative to that file."""
    path = os.path.abspath(path)
    if os.path.isdir(path):
        path = os.path.join(path, 'media.json')
    if not os.path.exists(path):
        raise SystemExit(f'not found: {path} (create a project with `python3 kit.py init <folder>`)')
    cfg = json.load(open(path, encoding='utf-8'))
    cfg['_dir'] = os.path.dirname(path)
    theme = dict(DEFAULT_THEME)
    theme.update(cfg.get('theme', {}))
    cfg['theme'] = theme
    return cfg


def project_path(cfg, *parts):
    return os.path.join(cfg['_dir'], *parts)


def load_texts(cfg, locale):
    p = project_path(cfg, cfg.get('texts_dir', 'texts'), f'{locale}.json')
    if not os.path.exists(p):
        raise SystemExit(f'missing texts file: {p}')
    return json.load(open(p, encoding='utf-8'))


def text_locales(cfg):
    d = project_path(cfg, cfg.get('texts_dir', 'texts'))
    return sorted(f[:-5] for f in os.listdir(d) if f.endswith('.json') and not f.startswith('_'))


def render_html(html, out, w, h, budget_ms=5000, transparent=False):
    """Screenshots an HTML string at exactly w x h with headless Chrome.
    transparent=True keeps the alpha channel (art/logos); store images are always flattened."""
    work = tempfile.mkdtemp(prefix='smk_')
    try:
        page = os.path.join(work, 'page.html')
        open(page, 'w', encoding='utf-8').write(html)
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        subprocess.run([chrome(), '--headless=new', f'--user-data-dir={work}/profile', '--hide-scrollbars',
                        '--force-device-scale-factor=1', f'--window-size={w},{h}',
                        f'--virtual-time-budget={budget_ms}', '--allow-file-access-from-files',
                        *(['--default-background-color=00000000'] if transparent else []),
                        f'--screenshot={os.path.abspath(out)}', url(page)], check=True, capture_output=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    if not transparent:
        flatten_png(out)


def flatten_png(path):
    """Google Play rejects PNGs with an alpha channel; store images never need one."""
    try:
        from PIL import Image
    except ImportError:
        return
    im = Image.open(path)
    if im.mode in ('RGBA', 'LA', 'P'):
        im.convert('RGB').save(path, optimize=True)


def image_size(path):
    from PIL import Image
    with Image.open(path) as im:
        return im.size


# ---------- fonts ----------
# Headline faces bundled in assets/fonts (SIL OFL 1.1). Scripts the Latin fonts can't draw use
# open Noto fallbacks downloaded by `kit.py fonts` into assets/fonts/ext.
SCRIPT_FONTS = {
    'ja': ('noto-sans-jp', "'Noto Sans JP Variable'"),
    'ko': ('noto-sans-kr', "'Noto Sans KR Variable'"),
    'zh-Hans': ('noto-sans-sc', "'Noto Sans SC Variable'"),
    'zh-Hant': ('noto-sans-tc', "'Noto Sans TC Variable'"),
    'th': ('noto-sans-thai', "'Noto Sans Thai Variable'"),
    'hi': ('noto-sans-devanagari', "'Noto Sans Devanagari Variable'"),
    'ar': ('noto-sans-arabic', "'Noto Sans Arabic Variable'"),
    'he': ('noto-sans-hebrew', "'Noto Sans Hebrew Variable'"),
}
FONT_PACKAGES = [v[0] for v in SCRIPT_FONTS.values()]
CYRILLIC = {'ru', 'uk', 'bg', 'sr', 'kk', 'be', 'mk'}
TALL = {'th', 'hi'}           # stacked marks need more line height
RTL = {'ar', 'he', 'fa', 'ur'}


def script_key(locale):
    base = locale.replace('_', '-').split('-')[0]
    if locale in SCRIPT_FONTS:
        return locale
    if base == 'zh':
        return 'zh-Hant' if locale.endswith(('Hant', 'TW', 'HK', 'MO')) else 'zh-Hans'
    return base


def font_css(locale):
    """(<head> html, headline font-family, line-height, dir) for a locale."""
    f = lambda n: url(os.path.join(FONTS, n))
    head = f'''<style>
@font-face{{font-family:Anton;src:url({f('anton-latin-400-normal.woff2')}) format('woff2');}}
@font-face{{font-family:Anton;src:url({f('anton-latin-ext-400-normal.woff2')}) format('woff2');unicode-range:U+0100-024F,U+1E00-1EFF;}}
@font-face{{font-family:Archivo;src:url({f('archivo-latin-wdth-normal.woff2')}) format('woff2');font-weight:100 900;font-stretch:62% 125%;}}
@font-face{{font-family:Archivo;src:url({f('archivo-latin-ext-wdth-normal.woff2')}) format('woff2');font-weight:100 900;font-stretch:62% 125%;unicode-range:U+0100-024F,U+1E00-1EFF;}}
@font-face{{font-family:Archivo;src:url({f('archivo-vietnamese-wdth-normal.woff2')}) format('woff2');font-weight:100 900;font-stretch:62% 125%;unicode-range:U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+0300-0301,U+0303-0304,U+0308-0309,U+0323,U+0329,U+1EA0-1EF9,U+20AB;}}
@font-face{{font-family:Fredoka;src:url({f('fredoka-latin-wght-normal.woff2')}) format('woff2');font-weight:300 700;}}
@font-face{{font-family:Baloo2;src:url({f('baloo-2-latin-wght-normal.woff2')}) format('woff2');font-weight:400 800;}}
@font-face{{font-family:TitanOne;src:url({f('titan-one-latin-400-normal.woff2')}) format('woff2');}}
@font-face{{font-family:TitanOne;src:url({f('titan-one-latin-ext-400-normal.woff2')}) format('woff2');unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF;}}
@font-face{{font-family:LuckiestGuy;src:url({f('luckiest-guy-latin-400-normal.woff2')}) format('woff2');}}
@font-face{{font-family:LuckiestGuy;src:url({f('luckiest-guy-latin-ext-400-normal.woff2')}) format('woff2');unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF;}}
@font-face{{font-family:Baloo2;src:url({f('baloo-2-latin-ext-wght-normal.woff2')}) format('woff2');font-weight:400 800;unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF;}}
@font-face{{font-family:Baloo2;src:url({f('baloo-2-vietnamese-wght-normal.woff2')}) format('woff2');font-weight:400 800;unicode-range:U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+0300-0301,U+0303-0304,U+0308-0309,U+0323,U+0329,U+1EA0-1EF9,U+20AB;}}
@font-face{{font-family:FiraXC;font-weight:900;src:url({f('fira-sans-extra-condensed-cyrillic-900-normal.woff2')}) format('woff2');unicode-range:U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116;}}
@font-face{{font-family:FiraXC;font-weight:900;src:url({f('fira-sans-extra-condensed-cyrillic-ext-900-normal.woff2')}) format('woff2');unicode-range:U+0460-052F,U+1C80-1C88,U+20B4,U+2DE0-2DFF,U+A640-A69F,U+FE2E-FE2F;}}
</style>'''
    key = script_key(locale)
    fam, lh = 'Archivo', '.9'
    if key == 'vi':
        lh = '1.04'
    if key in CYRILLIC:
        fam, lh = 'Archivo, FiraXC', '.95'
    elif key in SCRIPT_FONTS:
        pkg, name = SCRIPT_FONTS[key]
        css = os.path.join(EXT_FONTS, pkg, 'package', 'index.css')
        if os.path.exists(css):
            head += f'<link rel="stylesheet" href="{url(css)}">'
        else:
            print(f'  ! {locale}: fallback font missing, run `python3 kit.py fonts` (a system font is used)',
                  file=sys.stderr)
        fam = f'Archivo, {name}, sans-serif'
        lh = '1.18' if key in TALL else '1.05'
    return head, fam, lh, ('rtl' if key in RTL else 'ltr')


def clean_capture(cfg, path, device):
    """Returns a copy of the capture without the system status bar (clock, battery, signal).

    The top `status_bar` pixels (scaled to the capture's width) are replaced by the row just
    below them, stretched upwards, so a coloured header or background simply continues to the
    top edge. media.json "status_bar": "remove" (default) | "keep" (captures rendered by the app
    itself, e.g. Flutter integration-test screenshots, have no status bar); per device override:
    "status_bar_px": {"iphone69": 180}. Cached in out/.clean/."""
    mode = cfg.get('status_bar', 'remove')
    if mode == 'keep':
        return path
    from PIL import Image
    dev = DEVICES[device]
    with Image.open(path) as im:
        im = im.convert('RGB')
        band = (cfg.get('status_bar_px') or {}).get(device, dev.get('status_bar', 0))
        band = round(band * im.width / dev['w'])
        if band <= 0 or band >= im.height // 4:
            return path
        rel = os.path.relpath(os.path.abspath(path), cfg['_dir']).replace(os.sep, '_').replace('..', '_')
        out = project_path(cfg, cfg.get('out_dir', 'out'), '.clean', f'{band}_{rel}')
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(path):
            return out
        os.makedirs(os.path.dirname(out), exist_ok=True)
        src_row = im.crop((0, band + 2, im.width, band + 3)).resize((im.width, band + 2))
        im.paste(src_row, (0, 0))
        im.save(out)
    return out
