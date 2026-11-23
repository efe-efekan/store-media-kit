"""Brand banners: just the logo on the brand background, with soft clouds and confetti.

* App Store product page header ("creative asset"): 5244x2950 or 3840x1646. On iPhone only a
  central band shows and the status bar + back/share buttons cover the top, so the logo sits in
  the middle, slightly high, and nothing important goes near the edges.
* Google Play feature graphic: 1024x500 (required for every Play listing).
"""
import os
import random

from .common import project_path, render_html, url

SIZES = {'5244x2950': (5244, 2950), '3840x1646': (3840, 1646), '1024x500': (1024, 500)}


def cloud(cx, cy, w, flip, op, uid):
    """A soft cartoon cloud: merged puffs, a top-lit gradient, cool underside, soft shadow."""
    h = w * 0.46
    puffs = [(170, 300, 120), (320, 220, 165), (520, 170, 200), (720, 230, 160), (860, 310, 115),
             (430, 300, 150), (620, 310, 140)]
    if flip:
        puffs = [(1000 - x, y, r) for x, y, r in puffs]
    shape = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in puffs) + \
        '<rect x="60" y="300" width="880" height="100" rx="50"/>'
    return f'''<svg class="cloud" style="left:{cx - w/2:.0f}px;top:{cy - h/2:.0f}px;width:{w:.0f}px;height:{h:.0f}px;opacity:{op}" viewBox="0 0 1000 460">
<defs>
 <linearGradient id="{uid}g" gradientUnits="userSpaceOnUse" x1="0" y1="20" x2="0" y2="410"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#f4f8ff"/><stop offset="1" stop-color="#c9dbff"/></linearGradient>
 <radialGradient id="{uid}h" gradientUnits="userSpaceOnUse" cx="420" cy="140" r="430"><stop offset="0" stop-color="#ffffff" stop-opacity=".95"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
 <clipPath id="{uid}c">{shape}</clipPath>
</defs>
<g transform="translate(0,26)" opacity=".35" style="filter:blur(18px)"><g fill="#0a2a80">{shape}</g></g>
<g fill="url(#{uid}g)">{shape}</g>
<g clip-path="url(#{uid}c)"><rect width="1000" height="460" fill="url(#{uid}h)"/>
 <ellipse cx="500" cy="470" rx="560" ry="120" fill="#9fbdf7" opacity=".35"/></g>
</svg>'''


def render(cfg, size='5244x2950'):
    W, H = SIZES[size]
    wide = W / H > 2
    sx, sy = W / 5244, H / 2950
    th = cfg['theme']
    hc = cfg.get('header', {})
    logo = project_path(cfg, hc.get('logo', 'art/logo.png'))
    if not os.path.exists(logo):
        raise SystemExit(f'missing header logo: {logo}')
    # Logo width (fraction of the banner width, or pixels if > 1) and vertical centre (% of the
    # height); tuned on the iPhone product page preview in App Store Connect.
    logo_w = hc.get('logo_width_wide' if wide else 'logo_width', 0.5625 if wide else 0.40)
    if logo_w <= 1:
        logo_w *= W
    logo_y = hc.get('logo_top_wide' if wide else 'logo_top', 49 if wide else 45.5)
    rnd = random.Random(7)
    conf = ''.join(
        f'<rect x="{(x := rnd.randint(0, W))}" y="{(y := rnd.randint(0, H))}" width="{(s := rnd.randint(22, 46) * sx)*1.8:.0f}" height="{s:.0f}" '
        f'rx="{s/2:.0f}" fill="{rnd.choice(th["confetti"])}" opacity="0.3" transform="rotate({rnd.randint(0, 180)} {x} {y})"/>'
        for _ in range(60)) if th.get('confetti') else ''
    clouds = ''
    if hc.get('clouds', True):
        def c(cx, cy, w, flip, op, uid):
            return cloud(cx * sx, cy * sy, w * (sx + sy) / 2, flip, op, uid)
        clouds = (c(500, 2720, 1500, False, 1, 'a') + c(1700, 2860, 1250, True, 1, 'b') + c(4650, 2700, 1550, True, 1, 'd')
                  + c(3550, 2880, 1100, False, 1, 'e') + c(4500, 230, 900, False, .9, 'f') + c(700, 160, 760, True, .85, 'g'))
    html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden}}
body{{position:relative;background:
  radial-gradient(ellipse {2000*sx:.0f}px {1200*sy:.0f}px at {W/2:.0f}px {(0.5 if wide else 0.454)*H:.0f}px, rgba(150,200,255,.6), rgba(150,200,255,0) 70%),
  linear-gradient(180deg,{th['top']} 0%,{th['mid']} 50%,{th['bottom']} 100%)}}
.layer{{position:absolute;left:0;top:0}}
.cloud{{position:absolute;z-index:2;overflow:visible}}
.logo{{position:absolute;left:50%;top:{logo_y}%;width:{logo_w}px;transform:translate(-50%,-50%);z-index:8;
  filter:drop-shadow(0 {26*sx:.0f}px 0 rgba(8,30,100,.35)) drop-shadow(0 {50*sx:.0f}px {80*sx:.0f}px rgba(0,0,0,.25))}}
</style></head><body>
<svg class="layer" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{conf}</svg>
{clouds}
<img class="logo" src="{url(logo)}">
</body></html>'''
    name = 'feature_graphic' if size == '1024x500' else f'header_{size}'
    out = project_path(cfg, cfg.get('out_dir', 'out'), 'header', f'{name}.png')
    render_html(html, out, W, H)
    print('wrote', os.path.relpath(out, cfg['_dir']))
    return out
