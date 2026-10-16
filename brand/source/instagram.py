"""OptiMOB — capas dos destaques do Instagram.

Uso: python3 brand/source/instagram.py
Gera em brand/instagram/:
  svg/<nome>.svg                 ícone em vetor (fundo Grafite)
  capa-story/<nome>.png          1080 × 1920, para carregar como capa do destaque
  quadrado/<nome>.png            1080 × 1080
  preview.png                    como ficam no perfil
"""
import os
import pathlib

BRAND = pathlib.Path(__file__).resolve().parent.parent
OUT = BRAND / 'instagram'

GRAPHITE, CARBON, STEEL, ASH, BONE, BLUE = '#1B1E1E', '#111313', '#2A2F30', '#8A918F', '#EEF0EA', '#3AA0FF'

# Grelha 48 × 48, traço 2,4, terminais retos — mesma regra da iconografia da marca.
SW = 2.4
ICONS = {
    'tutoriais': ('Tutoriais',
        f'<polygon points="17,12.5 36,24 17,35.5" fill="{BLUE}"/>'),
    'cozinhas': ('Cozinhas',
        # elevação de cozinha: aéreos em cima, base em baixo, puxadores quadrados
        f'<g fill="none" stroke="{BLUE}" stroke-width="{SW}" stroke-linejoin="miter">'
        f'<rect x="9" y="8" width="30" height="11"/><line x1="24" y1="8" x2="24" y2="19"/>'
        f'<rect x="9" y="24" width="30" height="13"/><line x1="24" y1="24" x2="24" y2="37"/>'
        f'<line x1="7" y1="40.5" x2="41" y2="40.5"/></g>'
        f'<g fill="{BLUE}"><rect x="19" y="14" width="3" height="3"/><rect x="26" y="14" width="3" height="3"/>'
        f'<rect x="19" y="26.5" width="3" height="3"/><rect x="26" y="26.5" width="3" height="3"/></g>'),
    'cnc': ('CNC',
        # linhas de corte em grelha com a fresa (quadrado) num cruzamento
        f'<g stroke="{BLUE}" stroke-width="{SW}" stroke-linecap="square">'
        f'<line x1="18" y1="9" x2="18" y2="39"/><line x1="30" y1="9" x2="30" y2="39"/>'
        f'<line x1="9" y1="18" x2="39" y2="18"/><line x1="9" y1="30" x2="39" y2="30"/></g>'
        f'<rect x="26" y="26" width="8" height="8" fill="{BLUE}"/>'
        f'<rect x="28" y="28" width="4" height="4" fill="{GRAPHITE}"/>'),
    'novidades': ('Novidades',
        f'<circle cx="24" cy="24" r="14" fill="none" stroke="{BLUE}" stroke-width="1.6" opacity=".55"/>'
        f'<circle cx="24" cy="24" r="8" fill="{BLUE}"/>'),
    'clientes': ('Clientes',
        f'<polygon points="24,9 39,24 24,39 9,24" fill="none" stroke="{BLUE}" stroke-width="{SW}" stroke-linejoin="miter"/>'
        f'<rect x="21.5" y="21.5" width="5" height="5" fill="{BLUE}"/>'),
}


def icon_svg(body, size=48):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="{size}" height="{size}">{body}</svg>'


def cover_svg(body, w, h, icon=400, grid=True):
    """Fundo Grafite, grelha técnica suave em círculo, ícone ao centro."""
    cx, cy = w / 2, h / 2
    g = ''
    if grid:
        g = (f'<defs><pattern id="g" width="40" height="40" patternUnits="userSpaceOnUse">'
             f'<path d="M40 0H0V40" fill="none" stroke="{BLUE}" stroke-opacity=".10" stroke-width="2"/></pattern>'
             f'<radialGradient id="m"><stop offset="0" stop-color="#fff"/><stop offset=".55" stop-color="#fff" stop-opacity=".6"/>'
             f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
             f'<mask id="k"><circle cx="{cx}" cy="{cy}" r="{w*0.5}" fill="url(#m)"/></mask></defs>'
             f'<rect width="{w}" height="{h}" fill="url(#g)" mask="url(#k)"/>')
    s = icon / 48
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<rect width="{w}" height="{h}" fill="{GRAPHITE}"/>{g}'
            f'<g transform="translate({cx - icon/2} {cy - icon/2}) scale({s})">{body}</g></svg>')


def preview_html():
    items = ''.join(
        f'<div class="it"><div class="ring"><div class="av">{cover_svg(b, 1080, 1080, 540, grid=True)}</div></div><span>{n}</span></div>'
        for n, b in ICONS.values())
    return f'''<html><head><style>
body{{margin:0;background:#0c0d0d;font-family:Inter,sans-serif;color:#f5f5f5}}
.wrap{{padding:56px 64px;display:flex;gap:44px}}
.it{{display:flex;flex-direction:column;align-items:center;gap:14px}}
.ring{{box-sizing:border-box;width:168px;height:168px;border-radius:50%;padding:5px;border:2px solid #3a3d3d}}
.av{{box-sizing:border-box;width:100%;height:100%;border-radius:50%;overflow:hidden;border:5px solid #0c0d0d}}
.av svg{{width:100%;height:100%;display:block}}
span{{font-size:24px}}
</style></head><body><div class="wrap">{items}</div></body></html>'''


def main():
    from playwright.sync_api import sync_playwright
    for d in ('svg', 'capa-story', 'quadrado'):
        (OUT / d).mkdir(parents=True, exist_ok=True)
    for key, (name, body) in ICONS.items():
        (OUT / 'svg' / f'{key}.svg').write_text(cover_svg(body, 1080, 1080, 540))
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        for key, (name, body) in ICONS.items():
            for folder, (w, h, ic) in {'capa-story': (1080, 1920, 460), 'quadrado': (1080, 1080, 540)}.items():
                pg.set_viewport_size({'width': w, 'height': h})
                pg.set_content(f'<html><body style="margin:0">{cover_svg(body, w, h, ic)}</body></html>')
                pg.locator('svg').first.screenshot(path=str(OUT / folder / f'{key}.png'))
        pg.set_viewport_size({'width': 1200, 'height': 330})
        pg.set_content(preview_html())
        pg.screenshot(path=str(OUT / 'preview.png'))
        b.close()
    print('ok', OUT)


if __name__ == '__main__':
    main()
