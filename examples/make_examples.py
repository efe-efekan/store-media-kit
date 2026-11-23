#!/usr/bin/env python3
"""Builds the two example projects' raw "app captures" and artwork from HTML.

    python3 examples/make_examples.py

The apps are fictional demos ("Demo Habits", a habit tracker, and "Demo Tiles", a tile puzzle
game). Real projects use real captures of their app instead (see docs/CAPTURE.md); this script
only exists so the examples work out of the box with no third-party artwork.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from kit.common import DEVICES, render_html  # noqa: E402

SIZES = {d: (DEVICES[d]['w'], DEVICES[d]['h']) for d in DEVICES}  # every supported device

BASE_CSS = '''
html,body{margin:0;width:100%;height:100%;overflow:hidden;font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
*{box-sizing:border-box}
.status{height:3.4vw;min-height:44px}
'''

# ---------------------------------------------------------------- Demo Habits (non-game)
HABITS = [('Morning run', '#34c759', '🏃', 12, True), ('Read 20 pages', '#ff9f0a', '📚', 31, True),
          ('Drink water', '#0a84ff', '💧', 8, False), ('Meditate', '#bf5af2', '🧘', 19, True),
          ('No sugar', '#ff375f', '🍎', 5, False), ('Sleep by 11', '#5e5ce6', '🌙', 23, False)]


def habits_screen(n, w, h):
    u = w / 100  # 1 unit = 1% of the width
    tablet = w / h > 0.6
    if tablet:
        u *= 0.82
    head = f'''<div style="background:linear-gradient(160deg,#0f9d7a,#0b7d63);color:#fff;padding:{6*u}px {6*u}px {8*u}px">
      <div class="status"></div>
      <div style="font-size:{3.6*u}px;opacity:.8">{['Today', 'This week', 'Streaks', 'Reminders', 'Focus'][n-1]}</div>
      <div style="font-size:{8*u}px;font-weight:800;margin-top:{1*u}px">{['Good morning', 'Your progress', 'Keep it going', 'Never forget', 'Deep work'][n-1]}</div></div>'''
    body = ''
    if n == 1:
        rows = ''.join(f'''<div style="display:flex;align-items:center;background:#fff;border-radius:{4*u}px;padding:{4*u}px;margin-bottom:{3*u}px;box-shadow:0 {0.6*u}px {2*u}px rgba(0,0,0,.06)">
          <div style="width:{11*u}px;height:{11*u}px;border-radius:{3.4*u}px;background:{c}22;display:flex;align-items:center;justify-content:center;font-size:{6*u}px">{e}</div>
          <div style="flex:1;margin-left:{4*u}px"><div style="font-size:{4.6*u}px;font-weight:700;color:#1c1c1e">{t}</div>
          <div style="font-size:{3.4*u}px;color:#8e8e93;margin-top:{0.6*u}px">🔥 {s} day streak</div></div>
          <div style="width:{8*u}px;height:{8*u}px;border-radius:50%;border:{0.8*u}px solid {c};background:{c if done else 'transparent'};color:#fff;display:flex;align-items:center;justify-content:center;font-size:{5*u}px">{'✓' if done else ''}</div></div>'''
                       for t, c, e, s, done in HABITS)
        body = f'<div style="padding:{5*u}px">{rows}</div>'
    elif n == 2:
        vals = [62, 80, 45, 90, 72, 100, 84]
        bars = ''.join(f'''<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end">
          <div style="width:62%;height:{v*0.55*u}px;border-radius:{2*u}px;background:linear-gradient(#34c759,#0f9d7a)"></div>
          <div style="font-size:{3.2*u}px;color:#8e8e93;margin-top:{1.5*u}px">{d}</div></div>''' for v, d in zip(vals, 'MTWTFSS'))
        cards = ''.join(f'''<div style="flex:1;background:#fff;border-radius:{4*u}px;padding:{4*u}px;box-shadow:0 {0.6*u}px {2*u}px rgba(0,0,0,.06)">
          <div style="font-size:{3.4*u}px;color:#8e8e93">{k}</div><div style="font-size:{8*u}px;font-weight:800;color:{c}">{v}</div></div>'''
                        for k, v, c in [('Completed', '86%', '#0f9d7a'), ('Best streak', '31', '#ff9f0a')])
        body = f'''<div style="padding:{5*u}px"><div style="display:flex;gap:{3*u}px;margin-bottom:{4*u}px">{cards}</div>
          <div style="background:#fff;border-radius:{4*u}px;padding:{5*u}px;height:{72*u}px;display:flex;align-items:flex-end;gap:{1*u}px;box-shadow:0 {0.6*u}px {2*u}px rgba(0,0,0,.06)">{bars}</div></div>'''
    elif n == 3:
        cells = ''.join(f'<div style="aspect-ratio:1;border-radius:{1.6*u}px;background:{c}"></div>'
                        for c in [['#e5e5ea', '#b7ebc9', '#6fd59a', '#34c759', '#0f9d7a'][(i * 7 + i // 5) % 5] for i in range(35 * 3)])
        body = f'''<div style="padding:{5*u}px"><div style="background:#fff;border-radius:{4*u}px;padding:{5*u}px;box-shadow:0 {0.6*u}px {2*u}px rgba(0,0,0,.06)">
          <div style="font-size:{5*u}px;font-weight:700;margin-bottom:{4*u}px">Last 15 weeks</div>
          <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:{1.6*u}px">{cells}</div></div></div>'''
    elif n == 4:
        rows = ''.join(f'''<div style="display:flex;align-items:center;background:#fff;border-radius:{4*u}px;padding:{4.5*u}px;margin-bottom:{3*u}px;box-shadow:0 {0.6*u}px {2*u}px rgba(0,0,0,.06)">
          <div style="font-size:{8*u}px;font-weight:800;color:#1c1c1e;width:{30*u}px">{t}</div>
          <div style="flex:1;font-size:{4.2*u}px;color:#3a3a3c">{e} {name}</div>
          <div style="width:{13*u}px;height:{7.6*u}px;border-radius:{4*u}px;background:{'#34c759' if on else '#e5e5ea'};position:relative">
          <div style="position:absolute;top:{0.6*u}px;{'right' if on else 'left'}:{0.6*u}px;width:{6.4*u}px;height:{6.4*u}px;border-radius:50%;background:#fff"></div></div></div>'''
                       for t, e, name, on in [('07:00', '🏃', 'Morning run', True), ('08:30', '💧', 'Drink water', True),
                                              ('13:00', '🧘', 'Meditate', False), ('21:30', '📚', 'Read 20 pages', True),
                                              ('22:45', '🌙', 'Sleep by 11', True)])
        body = f'<div style="padding:{5*u}px">{rows}</div>'
    else:
        body = f'''<div style="display:flex;flex-direction:column;align-items:center;padding-top:{12*u}px">
          <div style="width:{70*u}px;height:{70*u}px;border-radius:50%;background:conic-gradient(#0f9d7a 0 68%,#e5e5ea 68% 100%);display:flex;align-items:center;justify-content:center">
          <div style="width:{58*u}px;height:{58*u}px;border-radius:50%;background:#f2f2f7;display:flex;flex-direction:column;align-items:center;justify-content:center">
          <div style="font-size:{14*u}px;font-weight:800;color:#1c1c1e">17:42</div><div style="font-size:{4*u}px;color:#8e8e93">focus session</div></div></div>
          <div style="margin-top:{10*u}px;padding:{4*u}px {16*u}px;border-radius:{8*u}px;background:#0f9d7a;color:#fff;font-size:{5*u}px;font-weight:700">Pause</div></div>'''
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}body{{background:#f2f2f7}}</style></head><body>{head}{body}</body></html>'


# ---------------------------------------------------------------- Demo Tiles (game)
TILE = ['#ff5a5f', '#ffb400', '#3ddc97', '#4a8cff', '#b45cff', '#ff7ac6']


def tiles_screen(n, w, h):
    u = w / 100
    tablet = w / h > 0.6
    cols = 8 if not tablet else 9
    board_w = 92 * u if not tablet else 80 * u
    cell = board_w / cols
    top = f'''<div style="display:flex;justify-content:space-between;align-items:center;padding:{4*u}px {5*u}px 0">
      <div style="background:rgba(255,255,255,.18);color:#fff;border-radius:{5*u}px;padding:{1.6*u}px {4*u}px;font-weight:800;font-size:{4.4*u}px">⭐ {[1240, 3980, 0, 2210, 5600][n-1]}</div>
      <div style="background:rgba(255,255,255,.18);color:#fff;border-radius:{5*u}px;padding:{1.6*u}px {4*u}px;font-weight:800;font-size:{4.4*u}px">{['Level 12', 'Level 27', 'World map', 'Level 40', 'Daily'][n-1]}</div></div>'''

    def board(seed, glow=None):
        cells = []
        for r in range(cols):
            for c in range(cols):
                col = TILE[(r * 3 + c * 5 + seed + (r * c) % 4) % len(TILE)]
                g = glow and (r, c) in glow
                cells.append(f'''<div style="position:absolute;left:{c*cell+cell*0.06:.1f}px;top:{r*cell+cell*0.06:.1f}px;width:{cell*0.88:.1f}px;height:{cell*0.88:.1f}px;
                  border-radius:{cell*0.24:.1f}px;background:linear-gradient(160deg,#fff6 0,{col} 38%,{col});box-shadow:inset 0 -{cell*0.08:.1f}px 0 rgba(0,0,0,.18){',0 0 '+str(int(cell*0.5))+'px #fff' if g else ''};
                  {'transform:scale(1.08);' if g else ''}"></div>''')
        return (f'<div style="position:relative;margin:0 auto;width:{board_w:.1f}px;height:{board_w:.1f}px;background:rgba(10,0,40,.35);'
                f'border-radius:{4*u}px">{"".join(cells)}</div>')
    body = ''
    if n == 1:
        body = board(0) + f'<div style="text-align:center;margin-top:{6*u}px;color:#fff;font-size:{5*u}px;font-weight:800">Match 3 to clear!</div>'
    elif n == 2:
        body = board(2, glow={(3, 2), (3, 3), (3, 4), (3, 5)}) + f'<div style="text-align:center;margin-top:{6*u}px;color:#ffe066;font-size:{9*u}px;font-weight:900;text-shadow:0 {0.8*u}px 0 #a0521c">COMBO!</div>'
    elif n == 3:
        step = (h * 0.78) / 9
        pts = [((20 + 30 * (1 + (-1) ** i * (0.9 if i % 3 else 0.2))) * u, h * 0.12 + i * step) for i in range(9)]
        path = ' '.join(f'{"M" if i == 0 else "L"}{x + 7.5*u:.0f},{y + 7.5*u:.0f}' for i, (x, y) in enumerate(pts))
        dots = ''.join(f'''<div style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{15*u}px;height:{15*u}px;border-radius:50%;
          background:{'#ffd43b' if i < 5 else '#ffffff55'};border:{1.2*u}px solid #fff;color:#4a2a00;font-weight:900;font-size:{5.5*u}px;display:flex;align-items:center;justify-content:center;box-shadow:0 {1*u}px 0 rgba(0,0,0,.25)">{i+1 if i < 5 else '🔒'}</div>'''
                       for i, (x, y) in enumerate(pts))
        body = (f'<svg style="position:absolute;left:0;top:0" width="{w}" height="{h}"><path d="{path}" fill="none" stroke="#ffffff66" '
                f'stroke-width="{1.6*u:.0f}" stroke-dasharray="{3*u:.0f} {2.5*u:.0f}" stroke-linecap="round"/></svg>{dots}')
    elif n == 4:
        boost = ''.join(f'''<div style="flex:1;background:#fff;border-radius:{4*u}px;padding:{3*u}px;text-align:center;box-shadow:0 {1*u}px 0 rgba(0,0,0,.2)">
          <div style="font-size:{9*u}px">{e}</div><div style="font-weight:800;color:#3a1d6e;font-size:{3.6*u}px">{t}</div></div>'''
                        for e, t in [('💣', 'Bomb'), ('🌈', 'Rainbow'), ('🔀', 'Shuffle'), ('⏱️', '+30s')])
        body = board(4, glow={(r, 4) for r in range(cols)}) + f'<div style="display:flex;gap:{3*u}px;padding:{6*u}px {5*u}px">{boost}</div>'
    else:
        chests = ''.join(f'''<div style="background:#fff;border-radius:{4*u}px;padding:{4*u}px;text-align:center;opacity:{1 if i < 3 else .55}">
          <div style="font-size:{10*u}px">{'🎁' if i != 2 else '💎'}</div><div style="font-weight:800;color:#3a1d6e;font-size:{3.8*u}px">Day {i+1}</div></div>'''
                         for i in range(6))
        body = f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:{3*u}px;padding:{10*u}px {6*u}px">{chests}</div>'
    if n != 3:
        # Centre the play area in the remaining height.
        body = f'<div style="position:absolute;left:0;right:0;top:{14*u}px;bottom:{4*u}px;display:flex;flex-direction:column;justify-content:center">{body}</div>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}body{{position:relative;background:radial-gradient(circle at 50% 20%,#7b5cff,#3b1a99 60%,#24105f)}}</style></head>'
            f'<body><div class="status"></div>{top}{body}</body></html>')


# ---------------------------------------------------------------- artwork (transparent PNGs)
def logo_html(name, sub, c1, c2, icon):
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:transparent;font-family:-apple-system,"Segoe UI",Roboto,Arial,sans-serif}}</style></head>
<body><div style="display:inline-flex;align-items:center;gap:40px;padding:30px 50px;white-space:nowrap">
<div style="width:300px;height:300px;border-radius:80px;background:linear-gradient(150deg,{c1},{c2});display:flex;align-items:center;justify-content:center;font-size:170px;box-shadow:0 18px 0 rgba(0,0,0,.18)">{icon}</div>
<div><div style="font-size:170px;font-weight:900;color:#fff;letter-spacing:-3px;line-height:.9;text-shadow:0 12px 0 rgba(0,0,0,.2)">{name}</div>
<div style="font-size:64px;font-weight:700;color:#ffffffcc;margin-top:16px">{sub}</div></div></div></body></html>'''


def emoji_art(e, size=400):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:transparent}}</style></head>'
            f'<body><div style="width:{size}px;height:{size}px;display:flex;align-items:center;justify-content:center;font-size:{int(size*0.8)}px">{e}</div></body></html>')


def trim(path, pad=24):
    """Crops transparent margins so logos centre properly."""
    from PIL import Image
    im = Image.open(path)
    l, t, r, b = im.getbbox()
    im.crop((max(0, l - pad), max(0, t - pad), min(im.width, r + pad), min(im.height, b + pad))).save(path)


def main():
    for name, screen in [('habits', habits_screen), ('tiles', tiles_screen)]:
        root = os.path.join(HERE, name)
        for dev, (w, h) in SIZES.items():
            for n in range(1, 6):
                render_html(screen(n, w, h), os.path.join(root, 'raw', dev, 'en', f'{n:02d}.png'), w, h)
        print('captures', name)
    art = os.path.join(HERE, 'habits', 'art')
    render_html(logo_html('Demo Habits', 'small steps, every day', '#3ddc97', '#0f9d7a', '🌱'), os.path.join(art, 'logo.png'), 1580, 380, transparent=True)
    trim(os.path.join(art, 'logo.png'))
    for e, f in [('🔥', 'flame.png'), ('✅', 'check.png'), ('🏆', 'trophy.png')]:
        render_html(emoji_art(e), os.path.join(art, f), 400, 400, transparent=True)
    art = os.path.join(HERE, 'tiles', 'art')
    render_html(logo_html('Demo Tiles', 'match · combo · win', '#ffb400', '#ff5a5f', '💎'), os.path.join(art, 'logo.png'), 1500, 380, transparent=True)
    trim(os.path.join(art, 'logo.png'))
    for e, f in [('💎', 'gem.png'), ('💣', 'bomb.png'), ('⭐', 'star.png')]:
        render_html(emoji_art(e), os.path.join(art, f), 400, 400, transparent=True)
    # Video opening backgrounds (886x1920): brand gradient, soft dots, logo up top.
    for ex, bg, logo_dir in [('habits', 'linear-gradient(180deg,#24c79a,#0f9d7a 55%,#065a47)', 'habits'),
                             ('tiles', 'radial-gradient(circle at 50% 30%,#8f6bff,#4a22c9 55%,#24105f)', 'tiles')]:
        logo = os.path.join(HERE, logo_dir, 'art', 'logo.png')
        dots = ''.join(f'<div style="position:absolute;left:{(i*137)%886}px;top:{(i*263)%1920}px;width:{14+i%3*8}px;height:{14+i%3*8}px;'
                       f'border-radius:50%;background:#fff;opacity:.{2+i%4}"></div>' for i in range(40))
        html = (f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;width:886px;height:1920px;overflow:hidden;background:{bg}}}</style></head>'
                f'<body>{dots}<img src="file://{logo}" style="position:absolute;left:63px;top:420px;width:760px"></body></html>')
        render_html(html, os.path.join(HERE, ex, 'art', 'opening.png'), 886, 1920)
    print('art done')


if __name__ == '__main__':
    main()
