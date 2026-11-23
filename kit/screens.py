"""App Store screenshot compositor (one PNG per slide, per locale, per device).

Layout (designed on the 1320x2868 iPhone canvas, scaled for other devices):
  * a two-line headline at the top (line 1 light, line 2 in the accent colour),
    auto-shrunk to fit, both lines the same size;
  * the real app capture inside a device frame, pulled up right under the
    headline and bleeding off the bottom edge (fills the canvas);
  * optional decorations (your own app art) in the corners;
  * a short "pill" caption at the bottom.
"""
import os
import random

from .common import DEVICES, font_css, image_size, load_texts, project_path, render_html, url

BASE_W, BASE_H = 1320, 2868

def confetti_svg(theme, w, h, seed):
    colors = theme.get('confetti') or []
    if not colors:
        return ''
    rnd = random.Random(seed)
    k = w / BASE_W
    out = []
    for _ in range(int(46 * (w * h) / (BASE_W * BASE_H))):
        x = rnd.randint(0, w)
        y = rnd.randint(0, h)
        s = rnd.randint(10, 22) * k
        out.append(f'<rect x="{x}" y="{y}" width="{s*1.8:.0f}" height="{s:.0f}" rx="{s/2:.0f}" fill="{rnd.choice(colors)}" '
                   f'opacity="{theme.get("confetti_opacity", .45)}" transform="rotate({rnd.randint(0, 180)} {x} {y})"/>')
    return f'<svg class="layer" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{"".join(out)}</svg>'


def device_html(cfg, shot, dev, slide, k):
    """Device frame with the capture inside. Its `top` is set later by the page script.

    Default: a clean phone / tablet drawn in CSS (no third-party artwork). A project can use its
    own bezel PNG instead: media.json "frame_png": {"src": "art/frame.png", "w": 1470, "h": 3000,
    "screen": [75, 67, 1320, 2866], "radius": 175} (screen = x, y, w, h of the opening)."""
    tilt = slide.get('tilt', 0)
    width_frac = slide.get('device_width', cfg.get('device_width', 0.864 if dev['frame'] == 'phone' else 0.84))
    pw = dev['w'] * width_frac
    fp = cfg.get('frame_png')
    if fp and dev['frame'] == 'phone':
        s = pw / fp['w']
        sx, sy, sw, sh = (v * s for v in fp['screen'])
        return (f'<div class="device" id="device" style="left:{(dev["w"]-pw)/2:.1f}px;top:0;width:{pw:.1f}px;height:{fp["h"]*s:.1f}px;transform:rotate({tilt}deg)">'
                f'<img class="screen" src="{url(shot)}" style="left:{sx:.1f}px;top:{sy:.1f}px;width:{sw:.1f}px;height:{sh:.1f}px;border-radius:{fp.get("radius", 0)*s:.1f}px">'
                f'<img class="bezel" src="{url(project_path(cfg, fp["src"]))}"></div>')
    iw, ih = image_size(shot)
    phone = dev['frame'] == 'phone'
    bezel = pw * (0.045 if phone else 0.028)
    sw = pw - 2 * bezel
    sh = sw * ih / iw
    outer_r = pw * (0.16 if phone else 0.05)
    inner_r = max(outer_r - bezel, pw * 0.02)
    notch = ''
    if dev['notch'] == 'island':
        nw, nh = sw * 0.3, sw * 0.085
        notch = (f'<div class="notch" style="left:{(pw-nw)/2:.1f}px;top:{bezel + sw*0.03:.1f}px;width:{nw:.1f}px;'
                 f'height:{nh:.1f}px;border-radius:{nh/2:.1f}px"></div>')
    elif dev['notch'] == 'punch':
        d = sw * 0.045
        notch = (f'<div class="notch" style="left:{(pw-d)/2:.1f}px;top:{bezel + sw*0.03:.1f}px;width:{d:.1f}px;'
                 f'height:{d:.1f}px;border-radius:50%"></div>')
    buttons = ''
    if phone:
        bw = pw * 0.012
        buttons = (f'<i class="btn" style="right:{-bw:.1f}px;top:{sh*0.2:.1f}px;width:{bw:.1f}px;height:{sh*0.09:.1f}px"></i>'
                   f'<i class="btn" style="left:{-bw:.1f}px;top:{sh*0.16:.1f}px;width:{bw:.1f}px;height:{sh*0.05:.1f}px"></i>'
                   f'<i class="btn" style="left:{-bw:.1f}px;top:{sh*0.23:.1f}px;width:{bw:.1f}px;height:{sh*0.05:.1f}px"></i>')
    return (f'<div class="device drawn" id="device" style="left:{(dev["w"]-pw)/2:.1f}px;top:0;width:{pw:.1f}px;height:{sh + 2*bezel:.1f}px;'
            f'padding:{bezel:.1f}px;border-radius:{outer_r:.1f}px;transform:rotate({tilt}deg)">{buttons}'
            f'<img src="{url(shot)}" style="display:block;width:{sw:.1f}px;height:{sh:.1f}px;object-fit:cover;border-radius:{inner_r:.1f}px">'
            f'{notch}</div>')


def deco_html(cfg, d, sx, sy, rtl=False):
    src = project_path(cfg, d['src'])
    if rtl and cfg.get('mirror_rtl', True):  # right-to-left: decorations swap sides with the headline
        d = dict(d, x=BASE_W - d['x'] - d['w'], rot=-d.get('rot', 0))
    t = f'rotate({d.get("rot", 0)}deg)' + (' scaleX(-1)' if d.get('flip') else '')
    cls = 'deco badge' if d.get('badge') else 'deco'
    return (f'<img class="{cls}" src="{url(src)}" style="left:{d["x"]*sx:.0f}px;top:{d["y"]*sy:.0f}px;'
            f'width:{d["w"]*sx:.0f}px;transform:{t};z-index:{d.get("z", 5)}">')


def raw_capture(cfg, locale, device, n, slide):
    """raw/<device>/<locale>/NN.png, else raw/<device>/en/NN.png (captures without text serve every locale)."""
    raw = project_path(cfg, cfg.get('raw_dir', 'raw'), device)
    name = slide.get('raw', f'{n:02d}.png')
    for loc in (locale, cfg.get('fallback_locale', 'en')):
        p = os.path.join(raw, loc, name)
        if os.path.exists(p):
            return p
    raise SystemExit(f'missing capture: {os.path.join(raw, locale, name)} (or {cfg.get("fallback_locale", "en")})')


def page(cfg, locale, device, n, slide, text):
    dev = DEVICES[device]
    W, H = dev['w'], dev['h']
    sx, sy = W / BASE_W, H / BASE_H
    k = sx
    th = cfg['theme']
    head, fam, lh, direction = font_css(locale)
    decos = ''.join(deco_html(cfg, d, sx, sy, direction == 'rtl') for d in slide.get('decos', []))
    shot = raw_capture(cfg, locale, device, n, slide)
    weight = cfg.get('headline_weight', 900)
    stretch = cfg.get('headline_stretch', '62%')
    sparks = ''
    if th.get('sparks'):
        spark = lambda side, lines: (f'<svg class="spark" style="{side}:{150*k:.0f}px" viewBox="0 0 70 90"><g stroke="{th["accent"]}" '
                                     f'stroke-width="10" stroke-linecap="round">{lines}</g></svg>')
        sparks = (spark('left', '<line x1="60" y1="10" x2="40" y2="30"/><line x1="66" y1="45" x2="30" y2="45"/><line x1="60" y1="80" x2="40" y2="60"/>')
                  + spark('right', '<line x1="10" y1="10" x2="30" y2="30"/><line x1="4" y1="45" x2="40" y2="45"/><line x1="10" y1="80" x2="30" y2="60"/>'))
    pill = text.get('pill', '')
    # Room for a corner decoration on the side the headline ends (mirrored for right-to-left).
    hl_far = cfg.get('headline_right', 186)
    return f'''<!doctype html><html lang="{locale}" dir="{direction}"><head><meta charset="utf-8">{head}<style>
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden}}
body{{position:relative;background:
  radial-gradient(ellipse {900*k:.0f}px {800*k:.0f}px at 50% {1700*sy:.0f}px, {th['glow']}, rgba(255,255,255,0) 70%),
  linear-gradient(180deg, {th['top']} 0%, {th['mid']} 45%, {th['bottom']} 100%);}}
.layer{{position:absolute;left:0;top:0}}
.deco{{position:absolute;filter:drop-shadow(0 {26*k:.0f}px {30*k:.0f}px rgba(5,20,80,.45))}}
.badge{{border-radius:50%;border:{12*k:.0f}px solid #fff;box-shadow:0 {18*k:.0f}px 0 rgba(10,40,120,.35)}}
.hl{{position:absolute;left:{(hl_far if direction == 'rtl' else 64)*k:.0f}px;right:{(64 if direction == 'rtl' else hl_far)*k:.0f}px;top:{60*sy:.0f}px;height:{620*sy:.0f}px;display:flex;flex-direction:column;z-index:7}}
.hl span{{display:block;font-family:{fam};font-weight:{weight};font-stretch:{stretch};line-height:{lh};letter-spacing:-.005em;white-space:nowrap;
  text-transform:uppercase;text-shadow:0 {8*k:.0f}px 0 {th['shadow']}}}
.l1{{color:{th['headline']}}} .l2{{color:{th['accent']}}}
.device{{position:absolute;z-index:4;filter:drop-shadow(0 {50*k:.0f}px {60*k:.0f}px rgba(5,25,90,.55));transform-origin:50% 50%;box-sizing:border-box}}
.device .screen{{position:absolute;object-fit:cover}}
.device .bezel{{position:absolute;left:0;top:0;width:100%;height:100%}}
.device.drawn{{background:linear-gradient(145deg,#3a3f47,{th['device_body']} 18%,{th['device_body']} 82%,#2b3038);
  box-shadow:inset 0 0 0 {3*k:.0f}px rgba(255,255,255,.12), inset 0 0 0 {7*k:.0f}px {th['device_body']}}}
.device .notch{{position:absolute;background:#050607}}
.device .btn{{position:absolute;background:#2a2e35;border-radius:{4*k:.0f}px}}
.pill{{position:absolute;left:50%;bottom:{70*sy:.0f}px;transform:translateX(-50%);z-index:9;background:{th['pill_bg']};color:{th['pill_ink']};
  font-family:{fam};font-weight:900;font-stretch:75%;font-size:{82*k:.0f}px;letter-spacing:.02em;padding:{22*k:.0f}px {64*k:.0f}px {24*k:.0f}px;
  border-radius:999px;white-space:nowrap;box-shadow:0 {14*k:.0f}px 0 {th['pill_edge']}, 0 {30*k:.0f}px {50*k:.0f}px rgba(0,0,0,.3)}}
.spark{{position:absolute;bottom:{80*sy:.0f}px;z-index:9;width:{70*k:.0f}px;height:{90*k:.0f}px}}
</style></head><body>
{confetti_svg(th, W, H, n)}
{decos}
<div class="hl" id="hl"><span class="l1">{text.get('line1', '')}</span><span class="l2">{text.get('line2', '')}</span></div>
{device_html(cfg, shot, dev, slide, k)}
{sparks if pill else ''}
{f'<div class="pill" id="pill">{pill}</div>' if pill else ''}
<script>
(async () => {{
  await document.fonts.ready;
  const box = document.getElementById('hl');
  const maxW = box.clientWidth, maxH = box.clientHeight;
  const l1 = box.querySelector('.l1'), l2 = box.querySelector('.l2');
  // Both lines start large and shrink until they fit; then they share the smaller size.
  let s1 = {360*k:.0f}, s2 = {360*k:.0f};
  const fit = () => {{ l1.style.fontSize = s1 + 'px'; l2.style.fontSize = s2 + 'px'; }};
  fit();
  while (l1.scrollWidth > maxW && s1 > 40) {{ s1 -= 4; fit(); }}
  while (l2.scrollWidth > maxW && s2 > 40) {{ s2 -= 4; fit(); }}
  const s = Math.min(s1, s2); s1 = s2 = s; fit();
  while (box.scrollHeight > maxH && s1 > 40) {{ s1 -= 4; s2 -= 4; fit(); }}
  // Device right under the headline's real height.
  const textH = (l1.textContent ? l1.offsetHeight : 0) + (l2.textContent ? l2.offsetHeight : 0);
  document.getElementById('device').style.top = (box.offsetTop + textH + {46*k:.0f}) + 'px';
  const pill = document.getElementById('pill');
  if (pill) {{ let ps = {78*k:.0f}; while (pill.offsetWidth > {1000*k:.0f} && ps > 30) {{ ps -= 2; pill.style.fontSize = ps + 'px'; }} }}
}})();
</script></body></html>'''


def render(cfg, locale, device='iphone69', only=None):
    texts = load_texts(cfg, locale)['slides']
    slides = cfg['slides']
    if len(texts) != len(slides):
        raise SystemExit(f'{locale}: {len(texts)} texts for {len(slides)} slides')
    dev = DEVICES[device]
    out_dir = project_path(cfg, cfg.get('out_dir', 'out'), 'screenshots', device, locale)
    written = []
    for n, (slide, text) in enumerate(zip(slides, texts), start=1):
        if only and n not in only:
            continue
        out = os.path.join(out_dir, f'{n:02d}.png')
        render_html(page(cfg, locale, device, n, slide, text), out, dev['w'], dev['h'])
        written.append(out)
        print('wrote', os.path.relpath(out, cfg['_dir']))
    return written
