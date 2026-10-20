"""OptiMOB — posts do feed do Instagram.

Uso: python3 brand/source/feed.py
Gera em brand/instagram/feed/:
  4x5/<post>.png    1080 × 1350 (formato vertical recomendado para o feed)
  1x1/<post>.png    1080 × 1080
  preview.png       os três posts lado a lado
"""
import pathlib

BRAND = pathlib.Path(__file__).resolve().parent.parent
OUT = BRAND / 'instagram' / 'feed'
FONTS = BRAND / 'fonts'

GRAPHITE, CARBON, STEEL, ASH, BONE, BLUE, DEEP = '#1B1E1E', '#111313', '#2A2F30', '#8A918F', '#EEF0EA', '#3AA0FF', '#1F6FC2'


def logo(name, color=None):
    s = (BRAND / 'svg' / f'{name}.svg').read_text()
    if color:
        import re
        s = re.sub(r'fill="#[0-9A-Fa-f]{6}"', f'fill="{color}"', s)
    return s


# ---------------------------------------------------------------- nesting real (guilhotina)
SHEET_W, SHEET_H, TRIM, KERF = 2750, 1830, 10, 4
STRIPS = [  # (altura da faixa, [(código, largura), ...]) — cada faixa soma 2730 mm úteis
    (580, [('LAT', 2400), ('TRV', 326)]),
    (560, [('TPO', 1764), ('PRT', 962)]),
    (400, [('FRG', 679)] * 4),
    (258, [('TRS', 1100)] * 2),
]


def nesting():
    parts, y, count = [], TRIM, {}
    for h, row in STRIPS:
        x = TRIM
        for code, w in row:
            count[code] = count.get(code, 0) + 1
            parts.append(dict(code=code, idx=count[code], x=x, y=y, w=w, h=h))
            x += w + KERF
        last_x, last_h = x, h
        y += h + KERF
    sobra = dict(x=last_x, y=y - last_h - KERF, w=SHEET_W - TRIM - last_x, h=last_h)
    area = sum(p['w'] * p['h'] for p in parts)
    return parts, sobra, area / (SHEET_W * SHEET_H)


def sheet_svg(parts, sobra):
    o = [f'<rect x="0" y="0" width="{SHEET_W}" height="{SHEET_H}" fill="rgba(238,240,234,.02)" stroke="{ASH}" stroke-width="2" stroke-dasharray="14 10" vector-effect="non-scaling-stroke"/>']
    o.append(f'<defs><pattern id="h" width="34" height="34" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="34" stroke="{STEEL}" stroke-width="10"/></pattern></defs>')
    o.append(f'<rect x="{sobra["x"]}" y="{sobra["y"]}" width="{sobra["w"]}" height="{sobra["h"]}" fill="url(#h)"/>')
    o.append(f'<text x="{sobra["x"] + sobra["w"]/2}" y="{sobra["y"] + sobra["h"]/2 + 16}" fill="{ASH}" font-family="JetBrains Mono" font-size="64" text-anchor="middle">SOBRA</text>')
    for p in parts:
        o.append(f'<rect x="{p["x"]}" y="{p["y"]}" width="{p["w"]}" height="{p["h"]}" fill="rgba(58,160,255,.12)" stroke="{BLUE}" stroke-width="2" vector-effect="non-scaling-stroke"/>')
        fs = 86 if p['h'] >= 400 else 70
        o.append(f'<text x="{p["x"] + 30}" y="{p["y"] + 30 + fs}" fill="{BLUE}" font-family="JetBrains Mono" font-weight="500" font-size="{fs}">{p["code"]}·{p["idx"]}</text>')
        if p['w'] >= 640:
            o.append(f'<text x="{p["x"] + 30}" y="{p["y"] + 40 + fs * 1.95}" fill="{ASH}" font-family="JetBrains Mono" font-size="{fs*0.72:.0f}">{p["w"]} × {p["h"]}</text>')
    return f'<svg viewBox="-4 -4 {SHEET_W + 8} {SHEET_H + 8}" preserveAspectRatio="xMinYMid meet">{"".join(o)}</svg>'


def num(n):
    return f'{n:,}'.replace(',', ' ')


# ---------------------------------------------------------------- posts
def post_nesting(h):
    parts, sobra, yld = nesting()
    pct = f'{yld*100:.1f}'.replace('.', ',')
    return 'dark', f'''
<div class="lbl">Nesting automático</div>
<div class="grow sheet">{sheet_svg(parts, sobra)}</div>
<div class="stat"><b>{pct}<small>%</small></b><span>Aproveitamento<br>da chapa<br>{SHEET_W} × {SHEET_H} <em style="font-style:normal;text-transform:none">mm</em></span></div>
'''


def post_manifesto(h):
    return 'bone', f'''
<div class="lbl" style="color:{DEEP}">Manifesto</div>
<div class="grow manif"><h1>Desenhe<br>uma vez.<br><span>Fabrique<br>sempre.</span></h1></div>
<div class="regua"><i class="o"></i><i class="b"></i><i class="h"></i></div>
'''


def slider(label, val, unit, pos):
    return f'''<div class="sl"><div class="sl-t"><span>{label}</span><b>{val}<small>{unit}</small></b></div>
<div class="sl-r"><i class="tk"></i><i class="fl" style="width:{pos*100:.0f}%"></i><i class="hd" style="left:{pos*100:.0f}%"></i></div></div>'''


def post_param(h):
    s = ''.join([slider('Largura', '1800', 'mm', .62), slider('Altura', '2400', 'mm', .80),
                 slider('Profundidade', '560', 'mm', .34), slider('Prateleiras', '5', 'un', .50)])
    return 'dark', f'''
<div class="lbl">Parâmetros</div>
<div class="grow sliders">{s}</div>
<p class="cap">Arraste um valor.<br><span>O módulo recalcula cada peça.</span></p>
'''


import math


def star(cx, cy, r, rot=0):
    pts = []
    for k in range(10):
        a = math.radians(-90 + rot + k * 36)
        rr = r if k % 2 == 0 else r * 0.382
        pts.append(f'{cx + rr*math.cos(a):.2f},{cy + rr*math.sin(a):.2f}')
    return f'<polygon points="{" ".join(pts)}" fill="#FFDE00"/>'


FLAGS = {  # desenhos simplificados, 60 × 40
    'PT': '<rect width="60" height="40" fill="#009C3B"/><path d="M30 4.5L55 20L30 35.5L5 20z" fill="#FFDF00"/>'
          '<circle cx="30" cy="20" r="9" fill="#002776"/>'
          '<path d="M21.3 17.6c6-1.6 12.6-.9 17.6 2.4" fill="none" stroke="#fff" stroke-width="1.6"/>',
    'EN': '<rect width="60" height="40" fill="#012169"/><path d="M0 0L60 40M60 0L0 40" stroke="#fff" stroke-width="8"/>'
          '<path d="M0 0L60 40M60 0L0 40" stroke="#C8102E" stroke-width="2.6"/><path d="M30 0v40M0 20h60" stroke="#fff" stroke-width="12"/>'
          '<path d="M30 0v40M0 20h60" stroke="#C8102E" stroke-width="7"/>',
    'ES': '<rect width="60" height="40" fill="#AA151B"/><rect y="10" width="60" height="20" fill="#F1BF00"/>',
    'FR': '<rect width="60" height="40" fill="#fff"/><rect width="20" height="40" fill="#002654"/><rect x="40" width="20" height="40" fill="#CE1126"/>',
    'RU': '<rect width="60" height="40" fill="#fff"/><rect y="13.33" width="60" height="13.34" fill="#0039A6"/><rect y="26.67" width="60" height="13.33" fill="#D52B1E"/>',
    'AR': '<rect width="60" height="40" fill="#fff"/><rect width="60" height="13.33" fill="#00732F"/><rect y="26.67" width="60" height="13.33" fill="#000"/><rect width="15" height="40" fill="#FF0000"/>',
    'VI': '<rect width="60" height="40" fill="#DA251D"/>' + star(30, 20.5, 12),
    'ZH': '<rect width="60" height="40" fill="#EE1C25"/>' + star(10, 10, 6) + star(20, 4, 2, 23) + star(24, 8, 2, 45) + star(24, 14, 2, 0) + star(20, 18, 2, 21),
}

LANGS = [('PT', 'Português', 'Largura', 'ltr'), ('EN', 'English', 'Width', 'ltr'),
         ('ES', 'Español', 'Ancho', 'ltr'), ('FR', 'Français', 'Largeur', 'ltr'),
         ('RU', 'Русский', 'Ширина', 'ltr'), ('AR', 'العربية', 'العرض', 'rtl'),
         ('VI', 'Tiếng Việt', 'Chiều rộng', 'ltr'), ('ZH', '中文', '宽度', 'ltr')]


def post_idiomas(h):
    cards = ''.join(f'''<div class="lc{' on' if i == 0 else ''}"><svg class="fl" viewBox="0 0 60 40" preserveAspectRatio="none">{FLAGS[c]}</svg>
<div class="lt"><em>{c} · <span dir="{d}">{n}</span></em><b dir="{d}">{w}</b></div></div>'''
                    for i, (c, n, w, d) in enumerate(LANGS))
    return 'dark', f'''
<div class="lbl">Multilíngue · {len(LANGS)} idiomas</div>
<div class="grow langs"><div class="lg-grid">{cards}</div></div>
<p class="cap">Uma extensão.<br><span>Na língua da sua oficina.</span></p>
'''


POSTS = {'01-nesting': post_nesting, '02-manifesto': post_manifesto, '03-parametros': post_param, '04-idiomas': post_idiomas}


def page(kind_body, h):
    kind, body = kind_body
    dark = kind == 'dark'
    fg = BONE if dark else GRAPHITE
    foot_logo = logo('optimob-sem-regua') if dark else logo('optimob-sem-regua', None).replace(f'fill="{BONE}"', f'fill="{GRAPHITE}"').replace(f'fill="{BLUE}"', f'fill="{DEEP}"')
    sq = h == 1080
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'JetBrains Mono';font-weight:400;src:url({(FONTS/'jetbrains-mono-latin-400-normal.woff2').as_uri()})}}
@font-face{{font-family:'JetBrains Mono';font-weight:500;src:url({(FONTS/'jetbrains-mono-latin-500-normal.woff2').as_uri()})}}
@font-face{{font-family:'Noto Sans Arabic';font-weight:600;src:url({(FONTS/'noto-sans-arabic-arabic-600-normal.woff2').as_uri()})}}
@font-face{{font-family:'JetBrains Mono';font-weight:700;src:url({(FONTS/'jetbrains-mono-latin-700-normal.woff2').as_uri()})}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:{h}px;overflow:hidden}}
body{{font-family:'Inter Display','Inter',sans-serif;color:{fg};background:{GRAPHITE if dark else BONE};-webkit-font-smoothing:antialiased}}
.post{{position:relative;width:1080px;height:{h}px;padding:{72 if sq else 88}px 84px {64 if sq else 76}px;display:flex;flex-direction:column}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(58,160,255,{.06 if dark else .0}) 1px,transparent 1px),linear-gradient(90deg,rgba(58,160,255,{.06 if dark else .0}) 1px,transparent 1px);background-size:54px 54px;-webkit-mask-image:radial-gradient(ellipse at 50% 45%,#000 20%,transparent 78%)}}
.post>*{{position:relative}}
.corner{{position:absolute;width:34px;height:34px;border:0 solid {ASH if dark else '#B9BEB8'}}}
.c1{{left:36px;top:36px;border-left-width:2px;border-top-width:2px}} .c2{{right:36px;top:36px;border-right-width:2px;border-top-width:2px}}
.c3{{left:36px;bottom:36px;border-left-width:2px;border-bottom-width:2px}} .c4{{right:36px;bottom:36px;border-right-width:2px;border-bottom-width:2px;border-color:{BLUE if dark else DEEP}}}
.lbl{{font:500 28px 'JetBrains Mono';letter-spacing:.26em;text-transform:uppercase;color:{BLUE}}}
.grow{{flex:1;min-height:0;display:flex;align-items:center}}
.sheet{{padding:{30 if sq else 56}px 0 {34 if sq else 56}px}}
.sheet svg{{width:100%;height:100%}}
.stat{{display:flex;align-items:flex-end;gap:34px;padding-bottom:{40 if sq else 58}px}}
.stat b{{font-size:{170 if sq else 196}px;font-weight:700;letter-spacing:-.05em;line-height:.78}}
.stat small{{font-size:.55em;letter-spacing:-.02em;margin-left:6px}}
.stat span{{font:400 25px/1.55 'JetBrains Mono';letter-spacing:.16em;text-transform:uppercase;color:{ASH};padding-bottom:4px}}
.manif h1{{font-size:{150 if sq else 176}px;font-weight:700;letter-spacing:-.045em;line-height:.95;color:{GRAPHITE}}}
.manif h1 span{{color:{DEEP}}}
.regua{{position:relative;height:{110 if sq else 150}px}}
.regua i{{position:absolute;background:{DEEP}}}
.regua .b{{left:0;right:0;top:50%;height:6px;margin-top:-3px}}
.regua .o{{left:0;top:50%;width:6px;height:36px;margin-top:-18px}}
.regua .h{{right:0;top:50%;width:30px;height:30px;margin-top:-15px}}
.sliders{{flex-direction:column;justify-content:center;align-items:stretch;gap:{34 if sq else 82}px;padding:{34 if sq else 0}px 0}}
.sl-t{{display:flex;justify-content:space-between;align-items:baseline;font:500 28px 'JetBrains Mono';letter-spacing:.2em;text-transform:uppercase;color:{ASH}}}
.sl-t b{{font:500 {48 if sq else 60}px 'JetBrains Mono';letter-spacing:-.01em;color:{BONE};text-transform:none}}
.sl-t small{{font-size:24px;color:{ASH};margin-left:10px;letter-spacing:.05em}}
.sl-r{{position:relative;height:30px;margin-top:{14 if sq else 22}px}}
.sl-r::before{{content:"";position:absolute;left:0;right:0;top:13px;height:4px;background:{STEEL}}}
.sl-r .fl{{position:absolute;left:0;top:13px;height:4px;background:{BLUE}}}
.sl-r .tk{{position:absolute;left:0;top:3px;width:4px;height:24px;background:{BLUE}}}
.sl-r .hd{{position:absolute;top:0;width:30px;height:30px;margin-left:-15px;background:{BLUE};box-shadow:0 0 0 8px {GRAPHITE}}}
.cap{{font-size:{38 if sq else 46}px;font-weight:600;letter-spacing:-.03em;line-height:1.1;padding-bottom:{40 if sq else 56}px}}
.cap span{{color:{BLUE};font-weight:500}}
.langs{{padding:{26 if sq else 44}px 0}}
.lg-grid{{width:100%;display:grid;grid-template-columns:1fr 1fr;gap:{16 if sq else 22}px}}
.lc{{display:flex;align-items:center;gap:26px;padding:{20 if sq else 30}px 26px;border:2px solid {STEEL};background:rgba(17,19,19,.55);position:relative}}
.lc .fl{{width:{84 if sq else 96}px;height:{56 if sq else 64}px;flex:none;box-shadow:0 0 0 2px rgba(238,240,234,.12)}}
.lc .lt{{min-width:0;display:flex;flex-direction:column;gap:{6 if sq else 10}px}}
.lc em{{font:500 18px 'JetBrains Mono','Noto Sans CJK SC','Noto Sans Arabic';font-style:normal;letter-spacing:.16em;text-transform:uppercase;color:{ASH};white-space:nowrap}}
.lc b{{font-family:'Inter Display','Inter','Noto Sans CJK SC','Noto Sans Arabic',sans-serif;font-size:{40 if sq else 46}px;font-weight:600;letter-spacing:-.02em;line-height:1.1;color:{BONE};white-space:nowrap;text-align:left}}
.lc.on{{border-color:{BLUE};background:rgba(58,160,255,.12)}}
.lc.on em{{color:{BLUE}}}
.foot{{display:flex;justify-content:space-between;align-items:center;border-top:2px solid {STEEL if dark else '#D5D9D2'};padding-top:30px}}
.foot .lg{{width:190px}}
.foot span{{font:400 22px 'JetBrains Mono';letter-spacing:.2em;color:{ASH};text-transform:uppercase}}
</style></head><body><div class="post"><div class="grid"></div>
<i class="corner c1"></i><i class="corner c2"></i><i class="corner c3"></i><i class="corner c4"></i>
{body}
<div class="foot"><div class="lg">{foot_logo}</div><span>optimobsystem.com</span></div>
</div></body></html>'''


def main():
    from playwright.sync_api import sync_playwright
    for d in ('4x5', '1x1'):
        (OUT / d).mkdir(parents=True, exist_ok=True)
    tmp = OUT / '_render.html'
    with sync_playwright() as p:
        b = p.chromium.launch()
        for folder, h in (('4x5', 1350), ('1x1', 1080)):
            pg = b.new_page(viewport={'width': 1080, 'height': h})
            for name, fn in POSTS.items():
                tmp.write_text(page(fn(h), h))
                pg.goto(tmp.as_uri()); pg.wait_for_timeout(300)
                pg.screenshot(path=str(OUT / folder / f'{name}.png'))
            pg.close()
        # pré-visualização lado a lado
        imgs = ''.join(f'<img src="{(OUT/"4x5"/f"{n}.png").as_uri()}">' for n in POSTS)
        pg = b.new_page(viewport={'width': 40 + 584 * len(POSTS), 'height': 780})
        tmp.write_text(f'<body style="margin:0;background:#0c0d0d;display:flex;gap:24px;padding:40px">'
                       f'<style>img{{width:560px;height:700px;display:block}}</style>{imgs}</body>')
        pg.goto(tmp.as_uri())
        pg.wait_for_timeout(300)
        pg.screenshot(path=str(OUT / 'preview.png'))
        b.close()
    tmp.unlink()
    _, _, y = nesting()
    print('ok', OUT, f'aproveitamento {y*100:.1f}%')


if __name__ == '__main__':
    main()
