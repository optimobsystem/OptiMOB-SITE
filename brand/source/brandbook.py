"""OptiMOB — Brandbook builder (HTML -> PDF via Chromium).
Uso: python3 brand/source/brandbook.py && python3 brand/source/render.py
"""
import math, base64, random, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(os.path.dirname(HERE))  # trabalha a partir de brand/
import logo as L
from logo import GRAPHITE, CARBON, BONE, BLUE, DEEP

STEEL = '#2A2F30'
ASH = '#8A918F'
MIST = '#C9D7E6'


def wm(**kw):
    return L.wordmark_svg(**kw)


def sym(**kw):
    return L.symbol_svg(**kw)


ORIG = base64.b64encode(open('source/logo-original.png', 'rb').read()).decode()

# ------------------------------------------------------------------ graphics

def iso(x, y, z, s=1.0):
    # projecção dimétrica: frente dominante, profundidade a subir para a direita
    return ((x * 0.94 + y * 0.62) * s, (x * 0.24 - y * 0.40 - z) * s)


def cabinet_svg(stroke=BLUE, sub=ASH, w=900, d=560, h=2000, s=0.16, dims=True, fill='none', label=True):
    """Roupeiro paramétrico isométrico (2 módulos, prateleiras, portas)."""
    lines = []
    def L3(a, b, col=stroke, sw=1.4, dash=None):
        (x1, y1), (x2, y2) = iso(*a, s), iso(*b, s)
        da = f' stroke-dasharray="{dash}"' if dash else ''
        lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{sw}"{da}/>')
    def box(x0, y0, z0, x1, y1, z1, col=stroke, sw=1.4):
        P = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]
        Q = [(x, y, z1) for x, y, _ in P]
        for i in range(4):
            L3(P[i], P[(i + 1) % 4], col, sw); L3(Q[i], Q[(i + 1) % 4], col, sw); L3(P[i], Q[i], col, sw)
    W = w * 2
    t = 18
    # carcaça
    box(0, 0, 0, W, d, h, stroke, 1.8)
    # divisória central e prateleiras (vista frontal y=0 é a face da frente)
    L3((w, 0, 0), (w, 0, h), stroke, 1.2)
    L3((w, 0, h), (w, d, h), sub, 0.8, '4 4')
    for z in (420, 900, 1380, 1760):
        L3((0, 0, z), (w, 0, z), sub, 0.9)
        L3((0, 0, z), (0, d, z), sub, 0.7, '3 4')
    for z in (100, 300, 1720):
        L3((w, 0, z), (W, 0, z), sub, 0.9)
    # varão
    L3((w + 60, 0, 1640), (W - 60, 0, 1640), stroke, 1.0, '2 3')
    # rodapé
    L3((0, 0, 80), (W, 0, 80), stroke, 1.0)
    parts = ''.join(lines)
    ann = ''
    if dims:
        def dim(a, b, off, txt, axis='x'):
            (x1, y1), (x2, y2) = iso(*a, s), iso(*b, s)
            ox, oy = off
            x1 += ox; x2 += ox; y1 += oy; y2 += oy
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            r = f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{BONE}" stroke-width="0.9"/>'
            for (px, py) in ((x1, y1), (x2, y2)):
                r += f'<rect x="{px-2.5:.1f}" y="{py-2.5:.1f}" width="5" height="5" fill="{BLUE}"/>'
            r += f'<text x="{mx:.1f}" y="{my-6:.1f}" fill="{BONE}" font-family="JetBrains Mono" font-size="10" text-anchor="middle">{txt}</text>'
            return r
        ann += dim((0, 0, 0), (W, 0, 0), (-14, 22), f'L = {W} mm')
        ann += dim((W, 0, 0), (W, d, 0), (18, 18), f'P = {d}')
        (hx, hy0), (_, hy1) = iso(0, 0, 0, s), iso(0, 0, h, s)
        hx -= 26
        ann += f'<line x1="{hx}" y1="{hy0}" x2="{hx}" y2="{hy1}" stroke="{BONE}" stroke-width="0.9"/>'
        ann += f'<rect x="{hx-2.5}" y="{hy0-2.5}" width="5" height="5" fill="{BLUE}"/><rect x="{hx-2.5}" y="{hy1-2.5}" width="5" height="5" fill="{BLUE}"/>'
        ann += f'<text x="{hx-8}" y="{(hy0+hy1)/2}" fill="{BONE}" font-family="JetBrains Mono" font-size="10" text-anchor="middle" transform="rotate(-90 {hx-8} {(hy0+hy1)/2})">A = {h} mm</text>'
    pts = [iso(x, y, z, s) for x in (0, W) for y in (0, d) for z in (0, h)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    pad = 60
    vb = f'{min(xs)-pad:.0f} {min(ys)-pad:.0f} {max(xs)-min(xs)+2*pad:.0f} {max(ys)-min(ys)+2*pad:.0f}'
    return f'<svg viewBox="{vb}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%">{parts}{ann}</svg>'


def nesting_svg(seed=7, sheet=(2750, 1830), stroke=BLUE, fill='rgba(58,160,255,.10)', label=True, bg='none'):
    rnd = random.Random(seed)
    W, H = sheet
    kerf = 12
    rects = []
    y = 0
    sizes = [(720, 560), (720, 560), (1960, 560), (560, 420), (880, 400), (600, 380), (1200, 300), (420, 300),
             (764, 380), (964, 300), (560, 560), (380, 280), (1800, 280), (700, 280), (480, 200), (1100, 160)]
    i = 0
    rows = [560, 420, 380, 300, 160]
    for rh in rows:
        x = 0
        while True:
            w = rnd.choice([380, 420, 480, 560, 600, 720, 764, 880, 964, 1200])
            if x + w > W:
                w = W - x
                if w < 200: break
            rects.append((x, y, w - kerf, rh - kerf))
            x += w
            if x >= W - 200: break
        y += rh
    used = sum(r[2] * r[3] for r in rects)
    sc = 1 / 5
    body = f'<rect x="0" y="0" width="{W*sc}" height="{H*sc}" fill="{bg}" stroke="{stroke}" stroke-width="1.2" stroke-dasharray="4 3"/>'
    for k, (x, y, w, h) in enumerate(rects):
        body += f'<rect x="{x*sc:.1f}" y="{y*sc:.1f}" width="{w*sc:.1f}" height="{h*sc:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
        if label and w > 300 and h > 200:
            body += f'<text x="{(x+12)*sc+2:.1f}" y="{(y+12)*sc+11:.1f}" font-family="JetBrains Mono" font-size="8" fill="{stroke}">P{k+1:02d} · {int(w)}×{int(h)}</text>'
    # sobra
    body += f'<text x="{W*sc-6}" y="{H*sc-8}" font-family="JetBrains Mono" font-size="8" fill="{ASH}" text-anchor="end">SOBRA</text>'
    return f'<svg viewBox="-4 -4 {W*sc+8} {H*sc+8}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%">{body}</svg>', used / (W * H)


def slider(label, val, unit='mm', pos=0.5, w='100%'):
    return f'''<div class="sl"><div class="sl-top"><span>{label}</span><b>{val}<i>{unit}</i></b></div>
<div class="sl-track"><span class="sl-tick"></span><span class="sl-fill" style="width:{pos*100}%"></span><span class="sl-h" style="left:{pos*100}%"></span></div></div>'''


def qr(seed=3, n=21, size=100, col=GRAPHITE):
    rnd = random.Random(seed)
    c = size / n
    out = ''
    def finder(x, y):
        return (f'<rect x="{x*c}" y="{y*c}" width="{7*c}" height="{7*c}" fill="{col}"/>'
                f'<rect x="{(x+1)*c}" y="{(y+1)*c}" width="{5*c}" height="{5*c}" fill="#fff"/>'
                f'<rect x="{(x+2)*c}" y="{(y+2)*c}" width="{3*c}" height="{3*c}" fill="{col}"/>')
    for i in range(n):
        for j in range(n):
            if (i < 8 and j < 8) or (i < 8 and j > n - 9) or (i > n - 9 and j < 8):
                continue
            if rnd.random() < 0.48:
                out += f'<rect x="{i*c:.2f}" y="{j*c:.2f}" width="{c+.2:.2f}" height="{c+.2:.2f}" fill="{col}"/>'
    out += finder(0, 0) + finder(n - 7, 0) + finder(0, n - 7)
    return f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;display:block">{out}</svg>'


NEST, NEST_YIELD = nesting_svg()
CAB = cabinet_svg()

# ------------------------------------------------------------------ social tiles (container-query scaled)

def tile(kind):
    if kind == 'logo':
        return f'<div class="tile t-dark t-center"><div class="t-grid"></div><div style="width:68cqw">{wm()}</div><div class="t-mono" style="margin-top:7cqw">FURNITURE DESIGN SYSTEM</div></div>'
    if kind == 'symbol':
        return f'<div class="tile t-blue t-center"><div style="width:52cqw">{sym(c_ring=GRAPHITE, c_bar=GRAPHITE, c_dot=BONE)}</div></div>'
    if kind == 'manifesto':
        return f'<div class="tile t-bone"><div class="t-label" style="color:{DEEP}">01 — MANIFESTO</div><div class="t-h" style="color:{GRAPHITE}">Desenhe<br>uma vez.<br><span style="color:{DEEP}">Fabrique<br>sempre.</span></div><div class="t-bar" style="background:{DEEP}"><i style="background:{DEEP}"></i></div></div>'
    if kind == 'nesting':
        return f'<div class="tile t-dark"><div class="t-label">NESTING AUTOMÁTICO</div><div style="position:absolute;left:8cqw;right:8cqw;top:22cqw;height:48cqw">{NEST}</div><div class="t-stat"><b>{NEST_YIELD*100:.1f}%</b><span>APROVEITAMENTO<br>DA CHAPA 2750×1830</span></div></div>'
    if kind == 'cabinet':
        return f'<div class="tile t-carbon"><div class="t-label">BLOCOS PARAMÉTRICOS</div><div style="position:absolute;inset:14cqw 6cqw 14cqw 6cqw">{CAB}</div><div class="t-foot"><span>ROUPEIRO_2M.skp</span><span style="color:{BLUE}">● LIVE</span></div></div>'
    if kind == 'slider':
        return f'''<div class="tile t-dark"><div class="t-label">PARÂMETROS</div><div class="t-sliders">{slider("LARGURA", "1800", pos=.62)}{slider("ALTURA", "2400", pos=.8)}{slider("PROFUNDIDADE", "560", pos=.35)}{slider("PRATELEIRAS", "5", "un", pos=.5)}</div></div>'''
    if kind == 'launch':
        return f'<div class="tile t-blue"><div class="t-label" style="color:{GRAPHITE}">LANÇAMENTO</div><div class="t-h" style="color:{GRAPHITE};font-size:17cqw">v1.0</div><div class="t-sub" style="color:{GRAPHITE}">Disponível na<br>Extension Warehouse</div><div class="t-bar" style="background:{GRAPHITE}"><i style="background:{GRAPHITE}"></i></div></div>'
    if kind == 'flow':
        return f'''<div class="tile t-dark t-center"><div class="t-flow"><span>3D</span><em></em><span class="b">PARAM</span><em></em><span>CNC</span></div><div class="t-mono" style="margin-top:6cqw;color:{ASH}">DO MODELO AO CORTE</div></div>'''
    if kind == 'pattern':
        return f'<div class="tile t-graph"><div class="t-pattern"></div><div style="position:absolute;left:8cqw;bottom:8cqw;width:44cqw">{wm(c_opti=BONE)}</div></div>'
    if kind == 'story':
        return f'''<div class="tile t-dark story"><div class="t-grid"></div><div class="st-top"><i></i><i class="on"></i><i></i></div>
<div class="st-head"><div class="av">{sym(bg=GRAPHITE)}</div><b>optimob.design</b><span>2 h</span></div>
<div style="position:absolute;left:10cqw;right:10cqw;top:30cqw">{CAB}</div>
<div class="st-cap">Ajuste. Gere. Corte.<br><span>Novo módulo de cozinhas →</span></div></div>'''
    raise ValueError(kind)


IG_TILES = ['logo', 'manifesto', 'symbol', 'nesting', 'cabinet', 'slider', 'flow', 'launch', 'pattern']

# ------------------------------------------------------------------ pages
pages = []
def page(sec, title, body, cls='', num=True):
    pages.append((sec, title, body, cls, num))


# 01 Capa
page('', '', f'''
<div class="cover-grid"></div>
<div class="cover-dim"><span></span></div>
<div class="cover-logo">{wm()}</div>
<div class="cover-sub mono">FURNITURE DESIGN SYSTEM</div>
<div class="cover-sub2 mono">SKETCHUP EXTENSION</div>
<div class="cover-meta mono"><div>BRAND GUIDELINES</div><div>VERSÃO 1.0</div><div>OUTUBRO 2026</div></div>
<div class="cover-coord mono">X 0.000 · Y 0.000 · Z 0.000</div>
<div class="cover-corner tl"></div><div class="cover-corner tr"></div><div class="cover-corner bl"></div><div class="cover-corner br"></div>
''', 'dark cover', num=False)

# 02 Índice
idx = [('01', 'Conceito'), ('02', 'Evolução da marca'), ('03', 'Logótipo'), ('04', 'Construção'), ('05', 'Símbolo'),
       ('06', 'Versões e assinaturas'), ('07', 'Área de proteção'), ('08', 'Cor'), ('09', 'Tipografia'),
       ('10', 'Usos incorretos'), ('11', 'Linguagem gráfica'), ('12', 'Iconografia'), ('13', 'Aplicações'),
       ('14', 'Redes sociais'), ('15', 'Behance & Web')]
page('00', 'Índice', f'''
<div class="h-xl" style="position:absolute;left:96px;top:150px">Índice</div>
<div class="toc">{''.join(f'<div class="toc-i"><span class="mono">{n}</span><b>{t}</b><em></em></div>' for n, t in idx)}</div>
''', 'dark')

# 03 Conceito
page('01', 'Conceito', f'''
<div class="two">
 <div>
  <div class="eyebrow">01 — CONCEITO</div>
  <div class="h-xl">O parâmetro<br>é a <span class="blue">forma.</span></div>
  <p class="lead">OptiMOB é um sistema de design de mobiliário para SketchUp: blocos paramétricos que se ajustam, se calculam e se transformam em peças prontas para o corte CNC.</p>
  <p class="body">A identidade nasce do gesto mais elementar do software — arrastar um valor. A régua com puxador quadrado sob “MOB” é um <b>controlo paramétrico</b>: uma cota viva que mede, ajusta e decide. Tudo o resto é redução: dois tons, uma tipografia, uma geometria ortogonal.</p>
 </div>
 <div class="pillars">
  <div class="pl"><span class="mono">A</span><b>Impactante</b><p>Contraste máximo entre Bone e Azul Parâmetro sobre Grafite. Lê-se a 16 px e a 16 metros.</p></div>
  <div class="pl"><span class="mono">B</span><b>Exclusivo</b><p>O ponto quadrado do “i” e o puxador da régua são assinaturas proprietárias — ninguém mais os tem.</p></div>
  <div class="pl"><span class="mono">C</span><b>Original</b><p>Nada de engrenagens, serras ou casas. A marca fala a linguagem do desenho técnico: cotas, origens, valores.</p></div>
  <div class="pl"><span class="mono">D</span><b>Minimalista</b><p>Um símbolo, uma régua, três cores. Cada elemento tem uma função — e só uma.</p></div>
 </div>
</div>
''', 'dark')

# 04 Evolução
page('02', 'Evolução da marca', f'''
<div class="eyebrow abs" style="left:96px;top:120px">02 — EVOLUÇÃO</div>
<div class="h-l abs" style="left:96px;top:150px">Mesma base. Mais precisão.</div>
<div class="evo">
 <div class="evo-c"><div class="evo-img"><img src="data:image/png;base64,{ORIG}"></div><div class="mono cap">ANTES — PROPOSTA ORIGINAL</div></div>
 <div class="evo-arrow"><span></span></div>
 <div class="evo-c"><div class="evo-img new"><div style="width:56%">{wm()}</div><div class="mono" style="margin-top:28px;letter-spacing:.42em;font-size:13px;color:{BONE}">FURNITURE DESIGN SYSTEM</div><div class="mono" style="margin-top:10px;letter-spacing:.42em;font-size:10px;color:{ASH}">SKETCHUP EXTENSION</div></div><div class="mono cap blue">DEPOIS — VERSÃO REFINADA</div></div>
</div>
<div class="evo-notes">
 <div><span class="mono blue">01</span><b>Glifos redesenhados</b><p>Inter Display convertida em vetor, com kerning ótico ajustado par a par. “Opti” em Regular, “MOB” em Bold.</p></div>
 <div><span class="mono blue">02</span><b>Ponto-parâmetro</b><p>O ponto do “i” passa a quadrado azul: liga “Opti” a “MOB” e antecipa o puxador.</p></div>
 <div><span class="mono blue">03</span><b>Régua de cota</b><p>A barra ganha marcador de origem e puxador proporcional. Passa a ser uma cota medida, não um sublinhado.</p></div>
 <div><span class="mono blue">04</span><b>Cores calibradas</b><p>Grafite, Bone e Azul extraídos do original e fixados em HEX, RGB e CMYK para ecrã e impressão.</p></div>
</div>
''', 'dark')

# 05 Logótipo principal
L.build_wordmark()
_M = dict(L.META)
_sc = 1000 / (_M['width'] - _M['left'])
_x0 = 300; _y0 = 450 - _M['height'] * _sc / 2
def _px(u): return _x0 + (u - _M['left']) * _sc
CALLOUTS = '<div class="callouts">' + ''.join(
    f'<div class="co" style="left:{x:.0f}px;top:{y:.0f}px"><i style="height:{h:.0f}px"></i><span class="mono">{k}</span> {t}</div>'
    for x, y, h, k, t in (
        (_px(_M['left'] + 30), _y0 - 70, 40, 'A', 'Opti — Inter Display Regular'),
        (_px(_M['cx']) - 11, _y0 - 70, 40, 'B', 'Ponto-parâmetro'),
        (_px(_M['mx0'] + 1900), _y0 - 70, 40, 'C', 'MOB — Inter Display Bold'),
    )) + f'<div class="co" style="left:{_px(_M["bx1"]) - 11:.0f}px;top:{_y0 + _M["by"]*_sc + 30:.0f}px"><span class="mono">D</span> Régua paramétrica: origem → puxador</div></div>'

page('03', 'Logótipo', f'''
<div class="hero-logo">{wm()}</div>
<div class="eyebrow abs" style="left:96px;top:120px">03 — LOGÓTIPO PRINCIPAL</div>
{CALLOUTS}
<p class="body abs" style="left:96px;bottom:100px;width:620px">O logótipo é sempre reproduzido a partir dos ficheiros vetoriais oficiais. Nunca deve ser redigitado com a fonte — o kerning, o ponto quadrado e a régua são desenhados à mão.</p>
''', 'dark')

# 06 Construção
M = L.META
def construction():
    inner, left, w, h = L.build_wordmark()
    t = M['top']; cap = t - 1490; xh = t - 1056
    g = ''
    for y, lbl in ((cap, 'ALTURA MAIÚSC.'), (xh, 'ALTURA X'), (t, 'LINHA DE BASE'), (M['by'], 'EIXO DA RÉGUA')):
        g += f'<line x1="{left-500}" x2="{w+500}" y1="{y}" y2="{y}" stroke="{BLUE}" stroke-width="9" stroke-dasharray="30 22" opacity=".85"/>'
        g += f'<text x="{left-480}" y="{y-24}" fill="{BLUE}" font-family="JetBrains Mono" font-size="88">{lbl}</text>'
    X = 1490
    g += f'<rect x="{M["mx0"]}" y="{cap}" width="{M["bx1"]-M["mx0"]}" height="{X}" fill="none" stroke="{ASH}" stroke-width="4" stroke-dasharray="10 10"/>'
    # tittle grid
    sq = M['sq']
    g += f'<rect x="{M["cx"]-sq/2}" y="{M["sy"]}" width="{sq}" height="{sq}" fill="none" stroke="{BONE}" stroke-width="6"/>'
    g += f'<text x="{M["cx"]}" y="{M["sy"]-40}" fill="{BONE}" font-family="JetBrains Mono" font-size="84" text-anchor="middle">1,12 h</text>'
    hs = M['hs']
    g += f'<text x="{M["bx1"]-hs/2}" y="{M["by"]+hs+70}" fill="{BONE}" font-family="JetBrains Mono" font-size="84" text-anchor="middle">0,15 X</text>'
    g += f'<text x="{(M["mx0"]+M["bx1"])/2}" y="{M["by"]+hs+70}" fill="{ASH}" font-family="JetBrains Mono" font-size="84" text-anchor="middle">régua = largura “MOB”</text>'
    g += f'<text x="{w+60}" y="{cap+X/2}" fill="{ASH}" font-family="JetBrains Mono" font-size="64">X</text>'
    return f'<svg viewBox="{left-560} {cap-260} {w-left+1180} {M["by"]-cap+620}" xmlns="http://www.w3.org/2000/svg" style="width:100%">{g}{inner}</svg>'

page('04', 'Construção', f'''
<div class="eyebrow abs" style="left:96px;top:120px">04 — CONSTRUÇÃO</div>
<div class="h-l abs" style="left:96px;top:150px">Geometria em módulos de X</div>
<div class="blueprint"></div>
<div class="abs" style="left:300px;right:300px;top:240px">{construction()}</div>
<div class="specs mono">
 <div><span>X</span>altura de maiúscula de “MOB”</div>
 <div><span>h</span>espessura da haste do “i”</div>
 <div><span>0,062 X</span>espessura da régua</div>
 <div><span>0,40 X</span>distância base → eixo da régua</div>
 <div><span>0,15 X</span>lado do puxador quadrado</div>
</div>
''', 'dark')

# 07 Símbolo
page('05', 'Símbolo', f'''
<div class="two" style="align-items:center">
 <div>
  <div class="eyebrow">05 — SÍMBOLO</div>
  <div class="h-xl">Origem +<br><span class="blue">parâmetro.</span></div>
  <p class="body">O símbolo destila o logótipo em dois gestos: o <b>“O”</b> de Opti como ponto de origem de um sistema de coordenadas, com o ponto-parâmetro no centro, e a <b>régua</b> que define a medida. Funciona como ícone da extensão, avatar e favicon.</p>
  <div class="sym-sizes">
   {''.join(f'<div><div style="width:{s}px;height:{s}px">{sym(bg=GRAPHITE if s>20 else None)}</div><span class="mono">{s}px</span></div>' for s in (128, 64, 32, 24, 16))}
  </div>
 </div>
 <div class="sym-big">
  <div class="sym-guide"></div>
  {sym()}
 </div>
</div>
''', 'dark')

# 08 Versões
page('06', 'Versões', f'''
<div class="eyebrow abs" style="left:96px;top:120px">06 — VERSÕES E ASSINATURAS</div>
<div class="vgrid">
 <div class="v" style="background:{GRAPHITE}"><div style="width:62%">{wm()}</div><span class="mono">PRINCIPAL · NEGATIVO</span></div>
 <div class="v" style="background:{BONE}"><div style="width:62%">{wm(c_opti=GRAPHITE, c_mob=DEEP, c_dot=DEEP, c_bar=DEEP)}</div><span class="mono" style="color:{GRAPHITE}">PRINCIPAL · POSITIVO</span></div>
 <div class="v" style="background:{BLUE}"><div style="width:62%">{wm(c_opti=GRAPHITE, c_mob=BONE, c_dot=BONE, c_bar=BONE)}</div><span class="mono" style="color:{GRAPHITE}">SOBRE AZUL</span></div>
 <div class="v" style="background:{GRAPHITE}"><div class="lock-v"><div style="width:110px">{sym()}</div><div style="width:280px;margin-top:22px">{wm(bar=False)}</div><div class="mono" style="font-size:10px;letter-spacing:.42em;margin-top:12px;color:{ASH}">FURNITURE DESIGN SYSTEM</div></div><span class="mono">VERTICAL</span></div>
 <div class="v" style="background:{CARBON}"><div class="lock-h"><div style="width:84px">{sym()}</div><i></i><div style="width:300px">{wm(bar=False)}<div class="mono" style="font-size:10px;letter-spacing:.38em;margin-top:10px;color:{ASH}">FURNITURE DESIGN SYSTEM</div></div></div><span class="mono">HORIZONTAL</span></div>
 <div class="v" style="background:#fff"><div style="width:62%">{wm(c_opti=CARBON, c_mob=CARBON, c_dot=CARBON, c_bar=CARBON)}</div><span class="mono" style="color:{CARBON}">MONOCROMÁTICO</span></div>
</div>
''', 'dark')

# 09 Área de proteção e mínimos
def clearspace():
    inner, left, w, h = L.build_wordmark()
    X = 1490 * 0.5
    t = M['top']; cap = t - 1490
    x0, y0, x1, y1 = left - X, cap - X, w + X, h + X - 70
    g = f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="rgba(58,160,255,.08)" stroke="{BLUE}" stroke-width="6" stroke-dasharray="24 16"/>'
    g += f'<rect x="{left}" y="{cap}" width="{w-left}" height="{h-cap-70}" fill="{GRAPHITE}"/>'
    for (x, y) in ((x0, y0), (x1 - X, y0), (x0, y1 - X), (x1 - X, y1 - X)):
        g += f'<rect x="{x}" y="{y}" width="{X}" height="{X}" fill="none" stroke="{ASH}" stroke-width="4"/>'
        g += f'<text x="{x+X/2}" y="{y+X/2+30}" fill="{ASH}" font-family="JetBrains Mono" font-size="90" text-anchor="middle">½X</text>'
    return f'<svg viewBox="{x0-40} {y0-40} {x1-x0+80} {y1-y0+80}" xmlns="http://www.w3.org/2000/svg" style="width:100%">{g}{inner}</svg>'

page('07', 'Área de proteção', f'''
<div class="two" style="grid-template-columns:1.25fr 1fr;align-items:center">
 <div>{clearspace()}</div>
 <div>
  <div class="eyebrow">07 — ÁREA DE PROTEÇÃO</div>
  <div class="h-l">Espaço para respirar.</div>
  <p class="body">Nenhum texto, imagem ou limite deve invadir a área de ½X à volta do logótipo, onde X é a altura das maiúsculas de “MOB”.</p>
  <div class="mins">
   <div><div style="width:200px">{wm()}</div><span class="mono">DIGITAL · MÍN. 120 px</span></div>
   <div><div style="width:150px">{wm()}</div><span class="mono">IMPRESSO · MÍN. 25 mm</span></div>
   <div><div style="width:130px">{wm(bar=False)}</div><span class="mono">ABAIXO DE 80 px · SEM RÉGUA</span></div>
  </div>
 </div>
</div>
''', 'dark')

# 10 Cor
colors = [
    ('Grafite', GRAPHITE, '27 30 30', '76 63 63 82', 'Fundo principal. 70% da composição.', BONE),
    ('Azul Parâmetro', BLUE, '58 160 255', '68 31 0 0', 'Cor de ação. Valores, puxadores, destaques.', GRAPHITE),
    ('Bone', BONE, '238 240 234', '5 3 7 0', 'Texto e “Opti”. Nunca branco puro em ecrã escuro.', GRAPHITE),
]
sub_colors = [('Carbono', CARBON, '17 19 19'), ('Aço', STEEL, '42 47 48'), ('Cinza Técnico', ASH, '138 145 143'), ('Azul Profundo', DEEP, '31 111 194'), ('Névoa', MIST, '201 215 230')]
page('08', 'Cor', f'''
<div class="eyebrow abs" style="left:96px;top:120px">08 — COR</div>
<div class="h-l abs" style="left:96px;top:150px">Três cores. Uma proporção.</div>
<div class="cmain">{''.join(f"""<div class="cm" style="background:{c};color:{tc}"><b>{n}</b><div class="mono cv"><span>HEX</span>{c}<br><span>RGB</span>{rgb}<br><span>CMYK</span>{cmyk}</div><p>{d}</p></div>""" for n, c, rgb, cmyk, d, tc in colors)}</div>
<div class="csub">{''.join(f'<div><i style="background:{c}"></i><b>{n}</b><span class="mono">{c} · {rgb}</span></div>' for n, c, rgb in sub_colors)}</div>
<div class="ratio"><i style="flex:70;background:{GRAPHITE};border:1px solid {STEEL}"></i><i style="flex:18;background:{BONE}"></i><i style="flex:12;background:{BLUE}"></i></div>
<div class="ratio-l mono"><span style="flex:70">70 — GRAFITE</span><span style="flex:18">18 — BONE</span><span style="flex:12">12 — AZUL</span></div>
''', 'dark')

# 11 Tipografia
page('09', 'Tipografia', f'''
<div class="eyebrow abs" style="left:96px;top:120px">09 — TIPOGRAFIA</div>
<div class="typo">
 <div class="ty">
  <div class="mono lbl">PRIMÁRIA — TÍTULOS E INTERFACE</div>
  <div class="ty-big disp">Aa</div>
  <div class="ty-name disp">Inter Display</div>
  <div class="ty-w disp"><span style="font-weight:300">Light</span><span style="font-weight:400">Regular</span><span style="font-weight:500">Medium</span><span style="font-weight:700">Bold</span></div>
  <div class="ty-chars disp">ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>abcdefghijklmnopqrstuvwxyz<br>0123456789 ÁÃÇÉÊÓÕÚ ← → ×</div>
 </div>
 <div class="ty">
  <div class="mono lbl">SECUNDÁRIA — DADOS, COTAS, ETIQUETAS</div>
  <div class="ty-big mono" style="font-weight:400">Aa</div>
  <div class="ty-name mono" style="font-weight:500">JetBrains Mono</div>
  <div class="ty-w mono"><span style="font-weight:300">Light</span><span style="font-weight:400">Regular</span><span style="font-weight:500">Medium</span><span style="font-weight:700">Bold</span></div>
  <div class="ty-chars mono" style="font-size:19px">ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>abcdefghijklmnopqrstuvwxyz<br>0123456789 L=1800 P=560 ±0.5</div>
 </div>
</div>
<div class="hier">
 <div><span class="mono">H1 · 72/76 · Bold · −2%</span><b class="disp" style="font-size:44px;font-weight:700;letter-spacing:-.02em">Do modelo ao corte.</b></div>
 <div><span class="mono">H2 · 36/42 · Medium</span><b class="disp" style="font-size:28px;font-weight:500">Blocos paramétricos</b></div>
 <div><span class="mono">BODY · 16/26 · Regular</span><b class="disp" style="font-size:16px;font-weight:400;color:{ASH}">Ajuste a largura e o módulo recalcula todas as peças.</b></div>
 <div><span class="mono">LABEL · 11 · Mono · +40%</span><b class="mono" style="font-size:12px;letter-spacing:.4em;color:{BLUE}">FURNITURE DESIGN SYSTEM</b></div>
</div>
''', 'dark')

# 12 Usos incorretos
def wrong(content, txt, style=''):
    return f'<div class="wr"><div class="wr-b" style="{style}">{content}<div class="x"></div></div><span class="mono">✕ {txt}</span></div>'
_inner, _l, _w, _h = L.build_wordmark()
page('10', 'Usos incorretos', f'''
<div class="eyebrow abs" style="left:96px;top:120px">10 — USOS INCORRETOS</div>
<div class="h-l abs" style="left:96px;top:150px">O que nunca fazer.</div>
<div class="wgrid">
 {wrong(f'<div style="width:70%;transform:scaleX(1.45)">{wm()}</div>', 'NÃO DISTORCER')}
 {wrong(f'<div style="width:70%">{wm(c_opti="#E25B45", c_mob="#7CD36B", c_dot="#7CD36B", c_bar="#7CD36B")}</div>', 'NÃO ALTERAR AS CORES')}
 {wrong(f'<div style="width:70%;transform:rotate(-12deg)">{wm()}</div>', 'NÃO RODAR')}
 {wrong(f'<div style="width:70%;filter:drop-shadow(6px 8px 0 #000) drop-shadow(0 0 14px #3AA0FF)">{wm()}</div>', 'NÃO APLICAR EFEITOS')}
 {wrong(f'<div class="disp" style="font-size:54px;color:{BONE}">Opti<b style="color:{BLUE}">MOB</b></div>', 'NÃO REDIGITAR COM FONTE')}
 {wrong(f'<div style="width:70%">{wm(c_mob=BLUE, c_bar=BONE)}</div>', 'NÃO TROCAR A COR DA RÉGUA')}
 {wrong(f'<div style="width:70%">{wm()}</div>', 'NÃO USAR SOBRE FUNDOS RUIDOSOS', f'background:repeating-linear-gradient(45deg,{BLUE} 0 10px,{BONE} 10px 20px)')}
 {wrong(f'<div style="width:70%;opacity:.35">{wm()}</div>', 'NÃO REDUZIR O CONTRASTE')}
</div>
''', 'dark')

# 13 Linguagem gráfica
page('11', 'Linguagem gráfica', f'''
<div class="eyebrow abs" style="left:96px;top:120px">11 — LINGUAGEM GRÁFICA</div>
<div class="h-l abs" style="left:96px;top:150px">O desenho técnico como ornamento.</div>
<div class="glgrid">
 <div class="gl"><div class="gl-v"><div class="blueprint" style="position:absolute;inset:0"></div></div><b>Grelha técnica</b><p>Malha de 8 px com linha forte a cada 64 px. Fundo de todas as superfícies escuras, sempre a 6–10% de opacidade.</p></div>
 <div class="gl"><div class="gl-v" style="display:flex;align-items:center;padding:0 40px"><div style="width:100%">{slider("LARGURA", "1800", pos=.6)}</div></div><b>Régua paramétrica</b><p>O controlo da marca. Usado como divisor, barra de progresso e indicador de valor.</p></div>
 <div class="gl"><div class="gl-v"><div style="position:absolute;inset:18px 30px">{NEST}</div></div><b>Nesting</b><p>Padrões de peças empacotadas como textura gráfica — o resultado real do produto vira imagem.</p></div>
 <div class="gl"><div class="gl-v"><div style="position:absolute;inset:4px 40px">{cabinet_svg(dims=True, s=0.085)}</div></div><b>Isometria de linha</b><p>Mobiliário representado em linha fina azul, sem sombras nem render. Cotas em Bone com terminais quadrados.</p></div>
 <div class="gl"><div class="gl-v cornerdemo"><i class="c1"></i><i class="c2"></i><i class="c3"></i><i class="c4"></i><span class="mono">X 1204.5 · Y 340.0</span></div><b>Cantos de enquadramento</b><p>Marcas de corte em L delimitam imagens e títulos, como numa folha de plotter.</p></div>
 <div class="gl"><div class="gl-v" style="display:flex;align-items:center;justify-content:center;gap:14px"><span class="chip">● LIVE</span><span class="chip o">PARAM</span><span class="chip">CNC READY</span></div><b>Etiquetas</b><p>Chips em mono, maiúsculas, com 1 px de contorno. Azul apenas para estado ativo.</p></div>
</div>
''', 'dark')

# 14 Iconografia
icons = {
 'Módulo': '<rect x="10" y="8" width="28" height="32" /><line x1="10" y1="20" x2="38" y2="20"/><line x1="24" y1="20" x2="24" y2="40"/>',
 'Parâmetros': '<line x1="8" y1="16" x2="40" y2="16"/><rect x="26" y="12" width="8" height="8" class="f"/><line x1="8" y1="32" x2="40" y2="32"/><rect x="14" y="28" width="8" height="8" class="f"/>',
 'Plano de corte': '<rect x="7" y="9" width="34" height="30"/><line x1="7" y1="24" x2="41" y2="24"/><line x1="22" y1="9" x2="22" y2="24"/><line x1="30" y1="24" x2="30" y2="39"/>',
 'Nesting': '<rect x="7" y="9" width="34" height="30" stroke-dasharray="3 3"/><rect x="11" y="13" width="12" height="10" class="f"/><rect x="26" y="13" width="11" height="22"/><rect x="11" y="26" width="12" height="9"/>',
 'Orçamento': '<rect x="11" y="7" width="26" height="34"/><line x1="16" y1="16" x2="32" y2="16"/><line x1="16" y1="23" x2="32" y2="23"/><line x1="16" y1="30" x2="25" y2="30"/><rect x="28" y="28" width="5" height="5" class="f"/>',
 'Exportar CNC': '<rect x="8" y="22" width="32" height="18"/><line x1="24" y1="6" x2="24" y2="28"/><polyline points="17,13 24,6 31,13"/>',
 'Materiais': '<rect x="8" y="10" width="26" height="8"/><rect x="11" y="20" width="26" height="8" /><rect x="14" y="30" width="26" height="8" class="f"/>',
 'Fitas de orla': '<rect x="10" y="10" width="28" height="28"/><line x1="10" y1="10" x2="38" y2="10" stroke-width="5" class="s"/><line x1="38" y1="10" x2="38" y2="38" stroke-width="5" class="s"/>',
 'Ferragens': '<circle cx="24" cy="24" r="12"/><rect x="21" y="21" width="6" height="6" class="f"/><line x1="24" y1="6" x2="24" y2="12"/><line x1="24" y1="36" x2="24" y2="42"/>',
 'Cotas': '<line x1="8" y1="24" x2="40" y2="24"/><rect x="5" y="21" width="6" height="6" class="f"/><rect x="37" y="21" width="6" height="6" class="f"/><line x1="8" y1="14" x2="8" y2="34"/><line x1="40" y1="14" x2="40" y2="34"/>',
 'Biblioteca': '<rect x="8" y="8" width="14" height="14"/><rect x="26" y="8" width="14" height="14" class="f"/><rect x="8" y="26" width="14" height="14"/><rect x="26" y="26" width="14" height="14"/>',
 'Definições': '<circle cx="24" cy="24" r="14"/><rect x="21" y="21" width="6" height="6" class="f"/>',
}
def ico(body, col=BONE, acc=BLUE):
    body = body.replace('class="f"', f'fill="{acc}" stroke="{acc}"').replace('class="s"', f'stroke="{acc}"')
    return f'<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%" fill="none" stroke="{col}" stroke-width="2.2" stroke-linecap="square">{body}</svg>'
page('12', 'Iconografia', f'''
<div class="two" style="grid-template-columns:1fr 1.5fr;align-items:center">
 <div>
  <div class="eyebrow">12 — ICONOGRAFIA</div>
  <div class="h-l">Ícones de barra de ferramentas.</div>
  <p class="body">Grelha de 48 × 48, traço de 2,2 px, terminais retos. Cada ícone contém no máximo <b>um</b> elemento azul — o “parâmetro” da ação. Desenhados para as barras de ferramentas do SketchUp a 24 e 32 px.</p>
  <div class="tb">{''.join(f'<i>{ico(b)}</i>' for b in list(icons.values())[:8])}</div>
  <div class="mono" style="font-size:11px;color:{ASH};margin-top:12px;letter-spacing:.2em">TOOLBAR · 24 px</div>
 </div>
 <div class="igrid">{''.join(f'<div><div class="ic">{ico(b)}</div><span class="mono">{n}</span></div>' for n, b in icons.items())}</div>
</div>
''', 'dark')

# 15 Aplicação: interface SketchUp
page('13', 'Interface', f'''
<div class="eyebrow abs" style="left:96px;top:96px">13 — APLICAÇÕES · INTERFACE DA EXTENSÃO</div>
<div class="app">
 <div class="app-bar"><i></i><i></i><i></i><span class="mono">Cozinha_Luanda_R02.skp — SketchUp Pro 2026</span></div>
 <div class="app-tools">{''.join(f'<i>{ico(b, col="#cfd3d0")}</i>' for b in list(icons.values())[:9])}</div>
 <div class="app-body">
  <div class="vp"><div class="vp-grid"></div><div class="vp-cab">{CAB}</div>
   <div class="vp-axes mono"><span style="color:#E25B45">X</span> <span style="color:#7CD36B">Y</span> <span style="color:{BLUE}">Z</span></div>
   <div class="vp-tag mono"><i></i>ROUPEIRO_2M · 24 peças</div></div>
  <div class="panel">
   <div class="pn-h"><div style="width:120px">{wm(bar=False)}</div><span class="mono">v1.0</span></div>
   <div class="pn-tabs mono"><span class="on">PARÂMETROS</span><span>MATERIAIS</span><span>CORTE</span></div>
   {slider("LARGURA TOTAL", "1800", pos=.6)}{slider("ALTURA", "2000", pos=.72)}{slider("PROFUNDIDADE", "560", pos=.35)}{slider("ESPESSURA", "18", pos=.2)}{slider("PRATELEIRAS", "4", "un", pos=.5)}
   <div class="pn-mat"><span class="mono">MATERIAL</span><div><i style="background:linear-gradient(135deg,#d9c3a1,#b99772)"></i>MDF Carvalho 18 mm</div></div>
   <div class="pn-sum mono"><div><span>PEÇAS</span><b>24</b></div><div><span>CHAPAS</span><b>2</b></div><div><span>APROV.</span><b class="blue">{NEST_YIELD*100:.1f}%</b></div></div>
   <div class="pn-btn">Gerar plano de corte <span>→</span></div>
  </div>
 </div>
</div>
''', 'dark')

# 16 Splash + loading
page('13', 'Ecrã de arranque', f'''
<div class="eyebrow abs" style="left:96px;top:96px">13 — APLICAÇÕES · SPLASH & LOADING</div>
<div class="splash">
 <div class="blueprint" style="position:absolute;inset:0;opacity:.8"></div>
 <div class="sp-corner a"></div><div class="sp-corner b"></div><div class="sp-corner c"></div><div class="sp-corner d"></div>
 <div class="sp-logo">{wm(bar=False)}</div>
 <div class="mono sp-sub">FURNITURE DESIGN SYSTEM</div>
 <div class="sp-load"><span class="sl-tick"></span><span class="sl-fill" style="width:64%"></span><span class="sl-h" style="left:64%"></span></div>
 <div class="mono sp-st"><span>A carregar biblioteca paramétrica…</span><span>64%</span></div>
 <div class="mono sp-foot"><span>v1.0.0 · build 2026.10</span><span>SketchUp Extension</span></div>
</div>
<div class="splash-icons">
 <div><div style="width:150px">{sym(bg=GRAPHITE)}</div><span class="mono">APP ICON · ESCURO</span></div>
 <div><div style="width:150px">{sym(bg=BLUE, c_ring=GRAPHITE, c_bar=GRAPHITE, c_dot=BONE)}</div><span class="mono">APP ICON · AZUL</span></div>
 <div><div style="width:150px">{sym(bg=BONE, c_ring=GRAPHITE, c_bar=DEEP, c_dot=DEEP)}</div><span class="mono">APP ICON · CLARO</span></div>
</div>
''', 'dark')

# 17 Papelaria
page('13', 'Papelaria', f'''
<div class="eyebrow abs" style="left:96px;top:96px">13 — APLICAÇÕES · PAPELARIA</div>
<div class="desk">
 <div class="card c-front"><div class="blueprint" style="position:absolute;inset:0;opacity:.6"></div><div style="width:58%;position:relative">{wm()}</div></div>
 <div class="card c-back"><div class="cb-top"><div style="width:44px">{sym()}</div><span class="mono">OPTIMOB</span></div>
  <div class="cb-name">Mateus Duarte</div><div class="mono cb-role">PRODUCT DESIGNER · FOUNDER</div>
  <div class="mono cb-info">+244 9XX XXX XXX<br>ola@optimob.design<br>optimob.design</div>
  <div class="cb-bar"></div></div>
 <div class="letter"><div class="lt-h"><div style="width:170px">{wm(c_opti=GRAPHITE, c_mob=DEEP, c_dot=DEEP, c_bar=DEEP)}</div><span class="mono">REF. OPT-2026-014</span></div>
  <div class="lt-lines">{''.join(f'<i style="width:{w}%"></i>' for w in (40, 0, 92, 96, 88, 94, 60, 0, 90, 95, 72))}</div>
  <div class="lt-f mono"><span>OPTIMOB · FURNITURE DESIGN SYSTEM</span><span>01/01</span></div><div class="lt-bar"></div></div>
</div>
''', 'dark')

# 18 Fabricação: painel gravado + etiqueta de peça
page('13', 'Fabricação', f'''
<div class="eyebrow abs" style="left:96px;top:96px">13 — APLICAÇÕES · OFICINA & CNC</div>
<div class="fab">
 <div class="ply"><div class="ply-grain"></div><div class="ply-edge"></div>
  <div class="ply-logo">{wm(c_opti="#5a3c21", c_mob="#4a2f18", c_dot="#4a2f18", c_bar="#4a2f18")}</div>
  <div class="mono ply-t">GRAVAÇÃO LASER · CONTRAPLACADO BÉTULA 18 mm</div></div>
 <div class="labels">
  <div class="tag">
   <div class="tag-h"><div style="width:110px">{wm(c_opti=GRAPHITE, c_mob=GRAPHITE, c_dot=GRAPHITE, c_bar=GRAPHITE, bar=False)}</div><span class="mono">P07 / 24</span></div>
   <div class="tag-b"><div class="tag-q">{qr(5)}</div>
    <div class="mono tag-d"><div><span>MÓDULO</span>ROUPEIRO_2M</div><div><span>PEÇA</span>LATERAL ESQ.</div><div><span>DIM.</span>2000 × 560 × 18</div><div><span>ORLA</span>▮ ▮ ▯ ▯</div></div></div>
   <div class="tag-bar"><i></i></div>
  </div>
  <div class="tag sm">
   <div class="tag-h"><div style="width:90px">{wm(c_opti=GRAPHITE, c_mob=GRAPHITE, c_dot=GRAPHITE, c_bar=GRAPHITE, bar=False)}</div><span class="mono">P12 / 24</span></div>
   <div class="tag-b"><div class="tag-q">{qr(9)}</div>
    <div class="mono tag-d"><div><span>PEÇA</span>PRATELEIRA</div><div><span>DIM.</span>864 × 540 × 18</div></div></div>
   <div class="tag-bar"><i></i></div>
  </div>
  <p class="body" style="margin-top:26px;font-size:15px">Etiquetas de peça impressas pela extensão: identificação, dimensões, orlas e QR de rastreio — a marca acompanha cada componente até à montagem.</p>
 </div>
</div>
''', 'dark')

# 19 Instagram perfil
ig_grid = ''.join(f'<div class="ig-cell">{tile(k)}</div>' for k in IG_TILES)
page('14', 'Instagram', f'''
<div class="eyebrow abs" style="left:96px;top:96px">14 — REDES SOCIAIS · INSTAGRAM</div>
<div class="h-l abs" style="left:96px;top:126px;width:520px">Um feed que parece software.</div>
<p class="body abs" style="left:96px;top:250px;width:470px">O grid alterna três ritmos — <b>marca</b>, <b>produto</b> e <b>prova técnica</b> — em diagonal, para que qualquer linha de três publicações seja equilibrada. Fundos Grafite dominam; Azul e Bone aparecem como pontuação.</p>
<div class="abs mono rhythm" style="left:96px;top:420px"><div><i style="background:{GRAPHITE};border:1px solid {STEEL}"></i>MARCA</div><div><i style="background:{BONE}"></i>MANIFESTO</div><div><i style="background:{BLUE}"></i>DESTAQUE</div></div>
<div class="phone" style="left:760px;top:60px">
 <div class="ph-scr ig">
  <div class="ig-status mono"><span>16:58</span><span>●●● ◐</span></div>
  <div class="ig-top"><b>optimob.design</b><span>☰</span></div>
  <div class="ig-prof"><div class="ig-av"><div>{sym(bg=GRAPHITE, radius=.5)}</div></div>
   <div class="ig-st"><div><b>48</b><span>publicações</span></div><div><b>12,4 mil</b><span>seguidores</span></div><div><b>86</b><span>a seguir</span></div></div></div>
  <div class="ig-bio"><b>OptiMOB · Furniture Design System</b><span class="cat">Software</span>Blocos paramétricos de marcenaria para SketchUp.<br>Do modelo 3D ao plano de corte CNC. ⌁<br><a>optimob.design/v1</a></div>
  <div class="ig-btns"><span>Seguir</span><span class="g">Mensagem</span><span class="g">▾</span></div>
  <div class="ig-hl">{''.join(f'<div><i>{c}</i><span>{t}</span></div>' for t, c in (("Tutoriais", "▶"), ("Cozinhas", "▦"), ("CNC", "⌗"), ("Novidades", "●"), ("Clientes", "◇")))}</div>
  <div class="ig-tabs"><span class="on">▦</span><span>▶</span><span>◫</span></div>
  <div class="ig-grid">{ig_grid}</div>
 </div>
</div>
''', 'dark')

# 20 Instagram publicações + story
page('14', 'Publicações', f'''
<div class="eyebrow abs" style="left:96px;top:96px">14 — REDES SOCIAIS · PUBLICAÇÕES E STORIES</div>
<div class="posts">
 {''.join(f"""<div class="post"><div class="post-h"><div class="pa">{sym(bg=GRAPHITE, radius=.5)}</div><b>optimob.design</b><span>···</span></div><div class="post-img">{tile(k)}</div><div class="post-a"><span>♡ ◯ ➤</span><span>⌑</span></div><div class="post-c"><b>{likes} gostos</b><br><b>optimob.design</b> {cap}</div></div>""" for k, likes, cap in (("nesting", "1.284", "Uma chapa, zero desperdício desnecessário. #cnc #marcenaria"), ("manifesto", "2.031", "O parâmetro é a forma. Bem-vindo ao OptiMOB."), ("slider", "946", "Arraste. O módulo recalcula cada peça."))) }
 <div class="story-ph"><div class="ph-scr st">{tile('story')}</div></div>
</div>
''', 'dark')

# 21 Behance
beh_mods = ''.join(f'<div class="bh-m">{tile(k)}</div>' for k in ('symbol', 'cabinet', 'launch'))
page('15', 'Behance', f'''
<div class="eyebrow abs" style="left:96px;top:80px">15 — BEHANCE · APRESENTAÇÃO DO PROJETO</div>
<div class="browser bh">
 <div class="br-bar"><i></i><i></i><i></i><div class="br-url mono">behance.net/gallery/2026/OptiMOB-Brand-Identity</div></div>
 <div class="bh-nav"><b>Bē</b><span>Explorar</span><span>Contratar</span><span>Assets</span><span class="sp"></span><span class="pill">Partilhe o seu trabalho</span></div>
 <div class="bh-body">
  <div class="bh-left">
   <div class="bh-title"><div class="pa">{sym(bg=GRAPHITE, radius=.5)}</div><div><b>OptiMOB — Brand Identity & Digital System</b><span>Mateus Duarte · Branding · UI/UX · Product Design</span></div></div>
   <div class="bh-hero"><div class="blueprint" style="position:absolute;inset:0"></div><div style="width:34%;position:relative">{wm()}</div><div class="mono" style="position:relative;margin-top:24px;letter-spacing:.42em;font-size:12px;color:{BONE}">FURNITURE DESIGN SYSTEM</div></div>
   <div class="bh-row">{beh_mods}</div>
   <div class="bh-wide"><div style="flex:1.2;padding:18px">{NEST}</div><div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:4px;padding-right:28px">{slider("LARGURA", "1800", pos=.6)}{slider("ALTURA", "2000", pos=.72)}</div></div>
  </div>
  <div class="bh-side">
   <div class="bh-av"><div>{sym(bg=GRAPHITE, radius=.5)}</div></div>
   <div class="bh-act"><i class="b">♥</i><span>Apreciar</span></div>
   <div class="bh-act"><i>＋</i><span>Guardar</span></div>
   <div class="bh-act"><i>↗</i><span>Partilhar</span></div>
   <div class="bh-stats mono"><div><b>2,4 mil</b>apreciações</div><div><b>18,9 mil</b>visualizações</div></div>
   <div class="bh-tags mono"><span>Branding</span><span>Logo</span><span>UI</span><span>SketchUp</span><span>Furniture</span></div>
  </div>
 </div>
</div>
''', 'dark')

# 22 Website
page('15', 'Website', f'''
<div class="eyebrow abs" style="left:96px;top:80px">15 — WEB · LANDING PAGE</div>
<div class="laptop">
 <div class="lp-scr">
  <div class="web">
   <div class="blueprint" style="position:absolute;inset:0"></div>
   <div class="w-nav"><div style="width:120px">{wm(bar=False)}</div><div class="mono w-links"><span>PRODUTO</span><span>BIBLIOTECA</span><span>PREÇOS</span><span>DOCS</span></div><span class="w-cta">Download</span></div>
   <div class="w-hero">
    <div class="w-txt"><div class="mono w-eb"><i></i>SKETCHUP EXTENSION · v1.0</div><div class="w-h">Do modelo<br>ao corte, em<br><span class="blue">um parâmetro.</span></div><p>Blocos paramétricos de marcenaria que calculam peças, orlas e chapas enquanto desenha.</p><div class="w-btns"><span class="w-cta big">Experimentar grátis →</span><span class="w-g mono">VER DEMO ▶</span></div></div>
    <div class="w-vis">{CAB}</div>
   </div>
   <div class="w-strip mono"><div><b>3D</b>modelação</div><div><b>PARAM</b>blocos dinâmicos</div><div><b>CNC</b>exportação</div><div><b class="blue">{NEST_YIELD*100:.0f}%</b>aproveitamento</div></div>
  </div>
 </div>
 <div class="lp-base"></div>
</div>
''', 'dark')

# 23 Contracapa
page('', '', f'''
<div class="cover-grid"></div>
<div class="back-sym">{sym()}</div>
<div class="back-txt"><div style="width:280px">{wm()}</div><div class="mono" style="margin-top:22px;color:{ASH};font-size:12px;letter-spacing:.32em">BRAND GUIDELINES · v1.0 · 2026</div></div>
<div class="mono back-f"><span>optimob.design</span><span>Este documento define as normas de utilização da marca OptiMOB.</span></div>
''', 'dark cover', num=False)

# ------------------------------------------------------------------ CSS
CSS = open('source/brandbook.css').read()
total = len(pages)
html = ['<!doctype html><html lang="pt"><head><meta charset="utf-8"><title>OptiMOB — Brand Guidelines</title><style>', CSS, '</style></head><body>']
for i, (sec, title, body, cls, num) in enumerate(pages, 1):
    chrome = ''
    if num:
        chrome = (f'<div class="pg-head mono"><span>OPTI<b>MOB</b> / BRAND GUIDELINES</span><span>{sec} — {title.upper()}</span></div>'
                  f'<div class="pg-foot mono"><span class="pf-bar"><i></i></span><span>{i:02d} / {total:02d}</span></div>')
    html.append(f'<section class="page {cls}">{chrome}{body}</section>')
html.append('</body></html>')
open('brandbook.html', 'w').write('\n'.join(html))
print('pages', total, 'yield', NEST_YIELD)
