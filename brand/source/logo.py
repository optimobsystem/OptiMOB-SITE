"""OptiMOB — geração vetorial do logótipo (glifos convertidos em paths)."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

INTER = '/usr/share/fonts/opentype/inter/InterDisplay-{}.otf'
_fonts = {}

def font(w):
    if w not in _fonts:
        _fonts[w] = TTFont(INTER.format(w))
    return _fonts[w]

# ---------- paleta ----------
GRAPHITE = '#1B1E1E'
CARBON = '#111313'
BONE = '#EEF0EA'
BLUE = '#3AA0FF'
DEEP = '#1F6FC2'

def glyph_path(w, gname, dx, dy=0, scale=1.0):
    f = font(w)
    gs = f.getGlyphSet()
    pen = SVGPathPen(gs)
    # flip Y: font units y-up -> svg y-down
    tp = TransformPen(pen, (scale, 0, 0, -scale, dx, dy))
    gs[gname].draw(tp)
    return pen.getCommands()

def glyph_bounds(w, gname):
    f = font(w)
    gs = f.getGlyphSet()
    bp = BoundsPen(gs)
    gs[gname].draw(bp)
    return bp.bounds

def adv(w, gname):
    return font(w)['hmtx'][gname][0]

CAP = 1490
META = {}
# Kerning óptico manual (unidades da fonte) — afinado para a palavra OptiMOB
KERN = {('O', 'p'): -20, ('p', 't'): -30, ('t', 'dotlessi'): -10,
        ('dotlessi', 'M'): 36, ('M', 'O'): -15, ('O', 'B'): -20}
TRACK = {'Light': -12, 'Regular': -12, 'Bold': -24}


def build_wordmark(c_opti=BONE, c_mob=BLUE, c_dot=BLUE, c_bar=BLUE, bar=True, w_opti='Regular'):
    """Devolve (svg_inner, width, height) em unidades da fonte; origem no topo da caixa."""
    seq = [('O', w_opti), ('p', w_opti), ('t', w_opti), ('dotlessi', w_opti),
           ('M', 'Bold'), ('O', 'Bold'), ('B', 'Bold')]
    top = 1560  # acima da altura de maiúsculas (ascendente de 'O' ~ overshoot)
    x = 0
    parts = []
    xs = {}
    prev = None
    for i, (g, w) in enumerate(seq):
        if prev:
            x += KERN.get((prev, g), 0)
        col = c_opti if w != 'Bold' else c_mob
        d = glyph_path(w, g, x, top)
        parts.append(f'<path fill="{col}" d="{d}"/>')
        b = glyph_bounds(w, g)
        xs[i] = (x + b[0], x + b[2], b)
        x += adv(w, g) + TRACK[w]
        prev = g
    # tittle quadrado (o "ponto-parâmetro")
    ib = xs[3]
    stem = ib[1] - ib[0]
    sq = stem * 1.12
    cx = (ib[0] + ib[1]) / 2
    xh = 1080
    sy = top - (xh + 210 + sq)
    parts.append(f'<rect fill="{c_dot}" x="{cx - sq/2:.1f}" y="{sy:.1f}" width="{sq:.1f}" height="{sq:.1f}"/>')
    width = xs[6][1]
    left = xs[0][0]
    height = top + 470  # descendente de p
    if bar:
        mx0, bx1 = xs[4][0], xs[6][1]
        th = CAP * 0.062
        by = top + CAP * 0.40
        hs = CAP * 0.15
        parts.append(f'<rect fill="{c_bar}" x="{mx0:.1f}" y="{by - th/2:.1f}" width="{bx1 - mx0 - hs:.1f}" height="{th:.1f}"/>')
        # marcador de origem (cota)
        parts.append(f'<rect fill="{c_bar}" x="{mx0:.1f}" y="{by - hs*0.42:.1f}" width="{th:.1f}" height="{hs*0.84:.1f}"/>')
        # puxador paramétrico
        parts.append(f'<rect fill="{c_bar}" x="{bx1 - hs:.1f}" y="{by - hs/2:.1f}" width="{hs:.1f}" height="{hs:.1f}"/>')
        height = max(height, by + hs / 2)
    META.update(top=top, left=left, width=width, height=height, sq=sq, sy=sy, cx=cx, mx0=xs[4][0], bx1=xs[6][1], ox1=xs[3][1], stem=stem)
    if bar: META.update(by=by, th=th, hs=hs)
    return '\n'.join(parts), left, width, height


def wordmark_svg(pad=0.0, bg=None, **kw):
    inner, left, w, h = build_wordmark(**kw)
    p = pad * w
    vb = f'{left - p:.0f} {-p:.0f} {w - left + 2*p:.0f} {h + 2*p:.0f}'
    bgr = f'<rect x="{left-p:.0f}" y="{-p:.0f}" width="{w-left+2*p:.0f}" height="{h+2*p:.0f}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{bgr}{inner}</svg>'


def symbol_inner(c_ring=BONE, c_bar=BLUE, c_dot=BLUE, s=100):
    """Símbolo: o 'O' (origem) sobre a régua paramétrica com puxador. Caixa 0..s."""
    r = s * 0.27
    sw = s * 0.078
    cx, cy = s * 0.5, s * 0.40
    th = s * 0.05
    by = s * 0.84
    hs = s * 0.13
    x0, x1 = s * 0.20, s * 0.80
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c_ring}" stroke-width="{sw}"/>'
            f'<rect x="{cx - sw*0.55:.2f}" y="{cy - sw*0.55:.2f}" width="{sw*1.1:.2f}" height="{sw*1.1:.2f}" fill="{c_dot}"/>'
            f'<rect x="{x0}" y="{by - th/2}" width="{x1 - x0 - hs}" height="{th}" fill="{c_bar}"/>'
            f'<rect x="{x0}" y="{by - hs*0.42}" width="{th}" height="{hs*0.84}" fill="{c_bar}"/>'
            f'<rect x="{x1 - hs}" y="{by - hs/2}" width="{hs}" height="{hs}" fill="{c_bar}"/>')


def symbol_svg(bg=None, radius=0.22, **kw):
    bgr = f'<rect width="100" height="100" rx="{100*radius}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{bgr}{symbol_inner(**kw)}</svg>'


if __name__ == '__main__':
    import os, sys
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    variants = {
        'optimob-principal-escuro': dict(bg=GRAPHITE),
        'optimob-principal-transparente': dict(),
        'optimob-positivo-claro': dict(bg=BONE, c_opti=GRAPHITE, c_mob=DEEP, c_dot=DEEP, c_bar=DEEP),
        'optimob-mono-branco': dict(c_opti=BONE, c_mob=BONE, c_dot=BONE, c_bar=BONE),
        'optimob-mono-preto': dict(c_opti=CARBON, c_mob=CARBON, c_dot=CARBON, c_bar=CARBON),
        'optimob-sem-regua': dict(bar=False),
    }
    for n, kw in variants.items():
        pad = 0.12 if 'bg' in kw else 0.0
        open(f'{out}/{n}.svg', 'w').write(wordmark_svg(pad=pad, **kw))
    open(f'{out}/optimob-simbolo.svg', 'w').write(symbol_svg())
    open(f'{out}/optimob-app-icon.svg', 'w').write(symbol_svg(bg=GRAPHITE))
    open(f'{out}/optimob-app-icon-azul.svg', 'w').write(symbol_svg(bg=BLUE, c_ring=GRAPHITE, c_bar=GRAPHITE, c_dot=BONE))
    print('ok')
