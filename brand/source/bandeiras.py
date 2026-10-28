"""Bandeiras simplificadas (SVG 30 × 20) para as artes de idiomas do OptiMOB.

Desenhos simplificados de propósito: os brasões e emblemas pequenos ficam reduzidos a formas simples,
porque a 30 px de largura não se leriam. Usar: svg(codigo_da_lingua, largura).
"""
import math


def star(cx, cy, r, rot=0, fill='#FFDE00'):
    pts = []
    for k in range(10):
        a = math.radians(-90 + rot + k * 36)
        rr = r if k % 2 == 0 else r * 0.382
        pts.append(f'{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}')
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'


def h3(a, b, c):  # três faixas horizontais
    return f'<rect width="30" height="20" fill="{a}"/><rect y="6.67" width="30" height="6.67" fill="{b}"/><rect y="13.33" width="30" height="6.67" fill="{c}"/>'


def v3(a, b, c):  # três faixas verticais
    return f'<rect width="30" height="20" fill="{b}"/><rect width="10" height="20" fill="{a}"/><rect x="20" width="10" height="20" fill="{c}"/>'


def nordic(bg, cross, x, w, y, h, inner=None):
    s = f'<rect width="30" height="20" fill="{bg}"/><rect x="{x}" width="{w}" height="20" fill="{cross}"/><rect y="{y}" width="30" height="{h}" fill="{cross}"/>'
    if inner:
        c, ix, iw, iy, ih = inner
        s += f'<rect x="{ix}" width="{iw}" height="20" fill="{c}"/><rect y="{iy}" width="30" height="{ih}" fill="{c}"/>'
    return s


def _gr():
    s = ''.join(f'<rect y="{i * 20 / 9:.3f}" width="30" height="{20 / 9 + .02:.3f}" fill="{"#0D5EAF" if i % 2 == 0 else "#FFFFFF"}"/>' for i in range(9))
    u = 20 / 9
    return s + f'<rect width="{5 * u:.2f}" height="{5 * u:.2f}" fill="#0D5EAF"/><rect x="{2 * u:.2f}" width="{u:.2f}" height="{5 * u:.2f}" fill="#fff"/><rect y="{2 * u:.2f}" width="{5 * u:.2f}" height="{u:.2f}" fill="#fff"/>'


def _my():
    u = 20 / 14
    s = ''.join(f'<rect y="{i * u:.3f}" width="30" height="{u + .02:.3f}" fill="{"#CC0001" if i % 2 == 0 else "#FFFFFF"}"/>' for i in range(14))
    return s + f'<rect width="15" height="{8 * u:.2f}" fill="#010066"/><circle cx="5.6" cy="5.7" r="3.6" fill="#FFCC00"/><circle cx="6.6" cy="5.7" r="3" fill="#010066"/>' + star(11, 5.7, 2.4, 0, '#FFCC00')


def _hr():
    s = h3('#FF0000', '#FFFFFF', '#171796')
    cells = ''
    for r in range(5):
        for c in range(5):
            cells += f'<rect x="{12.5 + c * 1.0:.1f}" y="{5.5 + r * 1.2:.1f}" width="1" height="1.2" fill="{"#FF0000" if (r + c) % 2 == 0 else "#FFFFFF"}"/>'
    return s + '<rect x="12.3" y="5.3" width="5.4" height="6.4" fill="#fff"/>' + cells


def _mk():
    rays = ''
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        x, y = 15 + 22 * math.cos(a), 10 + 22 * math.sin(a)
        p = math.radians(ang + 90)
        dx, dy = 2.6 * math.cos(p), 2.6 * math.sin(p)
        rays += f'<polygon points="15,10 {x + dx:.1f},{y + dy:.1f} {x - dx:.1f},{y - dy:.1f}" fill="#FFE600"/>'
    return f'<rect width="30" height="20" fill="#D20000"/>{rays}<circle cx="15" cy="10" r="3.6" fill="#FFE600" stroke="#D20000" stroke-width=".8"/>'


def _kr():
    tri = ''
    for cx, cy, ang in ((6, 4.5, 33.7), (24, 15.5, 33.7), (24, 4.5, -33.7), (6, 15.5, -33.7)):
        bars = ''.join(f'<rect x="-2.2" y="{-1.6 + i * 1.2:.1f}" width="4.4" height=".7" fill="#000"/>' for i in range(3))
        tri += f'<g transform="translate({cx} {cy}) rotate({ang})">{bars}</g>'
    yin = ('<path d="M10 10 A5 5 0 0 1 20 10 A2.5 2.5 0 0 1 15 10 A2.5 2.5 0 0 0 10 10Z" fill="#CD2E3A"/>'
           '<path d="M10 10 A5 5 0 0 0 20 10 A2.5 2.5 0 0 1 15 10 A2.5 2.5 0 0 0 10 10Z" fill="#0047A0"/>')
    return f'<rect width="30" height="20" fill="#fff"/><g transform="rotate(33.7 15 10)">{yin}</g>{tri}'


FLAGS = {
    'BR': '<rect width="30" height="20" fill="#009C3B"/><path d="M15 2.2L27.6 10L15 17.8L2.4 10z" fill="#FFDF00"/><circle cx="15" cy="10" r="4.6" fill="#002776"/><path d="M10.6 8.8c3-.8 6.4-.5 8.9 1.2" fill="none" stroke="#fff" stroke-width=".9"/>',
    'GB': '<rect width="30" height="20" fill="#012169"/><path d="M0 0L30 20M30 0L0 20" stroke="#fff" stroke-width="4"/><path d="M0 0L30 20M30 0L0 20" stroke="#C8102E" stroke-width="1.3"/><path d="M15 0v20M0 10h30" stroke="#fff" stroke-width="6"/><path d="M15 0v20M0 10h30" stroke="#C8102E" stroke-width="3.6"/>',
    'ES': '<rect width="30" height="20" fill="#AA151B"/><rect y="5" width="30" height="10" fill="#F1BF00"/>',
    'FR': v3('#002654', '#FFFFFF', '#CE1126'),
    'RU': h3('#FFFFFF', '#0039A6', '#D52B1E'),
    'AE': h3('#00732F', '#FFFFFF', '#000000') + '<rect width="7.5" height="20" fill="#FF0000"/>',
    'VN': '<rect width="30" height="20" fill="#DA251D"/>' + star(15, 10.4, 6),
    'CN': '<rect width="30" height="20" fill="#EE1C25"/>' + star(5, 5, 3) + star(10, 2, 1, 23) + star(12, 4, 1, 45) + star(12, 7, 1) + star(10, 9, 1, 21),
    'DE': h3('#000000', '#DD0000', '#FFCE00'),
    'IT': v3('#009246', '#FFFFFF', '#CE2B37'),
    'NL': h3('#AE1C28', '#FFFFFF', '#21468B'),
    'PL': '<rect width="30" height="20" fill="#fff"/><rect y="10" width="30" height="10" fill="#DC143C"/>',
    'TR': '<rect width="30" height="20" fill="#E30A17"/><circle cx="11" cy="10" r="5" fill="#fff"/><circle cx="12.3" cy="10" r="4" fill="#E30A17"/>' + star(17, 10, 2.3, -90, '#fff'),
    'GR': _gr(),
    'UA': '<rect width="30" height="20" fill="#0057B7"/><rect y="10" width="30" height="10" fill="#FFD700"/>',
    'RO': v3('#002B7F', '#FCD116', '#CE1126'),
    'CZ': '<rect width="30" height="20" fill="#fff"/><rect y="10" width="30" height="10" fill="#D7141A"/><path d="M0 0L15 10L0 20z" fill="#11457E"/>',
    'SK': h3('#FFFFFF', '#0B4EA2', '#EE1C25') + '<path d="M7 5h7v6.5c0 2.2-1.6 3.6-3.5 4.3C8.6 15.1 7 13.7 7 11.5z" fill="#EE1C25" stroke="#fff" stroke-width=".6"/><path d="M10.5 6.5v7.5M8.6 8.6h3.8M9 10.6h3" stroke="#fff" stroke-width=".9"/>',
    'HU': h3('#CE2939', '#FFFFFF', '#477050'),
    'SE': nordic('#006AA7', '#FECC00', 9.4, 3.75, 8, 4),
    'DK': nordic('#C8102E', '#FFFFFF', 9.7, 3.25, 8.57, 2.86),
    'NO': nordic('#BA0C2F', '#FFFFFF', 8.18, 5.45, 7.5, 5, ('#00205B', 9.55, 2.73, 8.75, 2.5)),
    'FI': nordic('#FFFFFF', '#003580', 8.33, 5, 7.27, 5.45),
    'MK': _mk(),
    'BG': h3('#FFFFFF', '#00966E', '#D62612'),
    'RS': h3('#C6363C', '#0C4076', '#FFFFFF'),
    'HR': _hr(),
    'IL': '<rect width="30" height="20" fill="#fff"/><rect y="2" width="30" height="2.8" fill="#0038B8"/><rect y="15.2" width="30" height="2.8" fill="#0038B8"/><path d="M15 6.2l3.3 5.7h-6.6zM15 13.8l-3.3-5.7h6.6z" fill="none" stroke="#0038B8" stroke-width=".8"/>',
    'IR': h3('#239F40', '#FFFFFF', '#DA0000') + '<circle cx="15" cy="10" r="2" fill="none" stroke="#DA0000" stroke-width=".9"/>',
    'PK': '<rect width="30" height="20" fill="#01411C"/><rect width="7.5" height="20" fill="#fff"/><circle cx="18.5" cy="10" r="5.4" fill="#fff"/><circle cx="20" cy="8.8" r="4.6" fill="#01411C"/>' + star(21.6, 7.4, 1.7, 20, '#fff'),
    'IN': h3('#FF9933', '#FFFFFF', '#138808') + '<circle cx="15" cy="10" r="2.6" fill="none" stroke="#000080" stroke-width=".7"/><circle cx="15" cy="10" r=".6" fill="#000080"/>',
    'BD': '<rect width="30" height="20" fill="#006A4E"/><circle cx="13.5" cy="10" r="6" fill="#F42A41"/>',
    'ID': '<rect width="30" height="20" fill="#fff"/><rect width="30" height="10" fill="#FF0000"/>',
    'MY': _my(),
    'TH': '<rect width="30" height="20" fill="#A51931"/><rect y="3.33" width="30" height="13.34" fill="#F4F5F8"/><rect y="6.67" width="30" height="6.66" fill="#2D2A4A"/>',
    'JP': '<rect width="30" height="20" fill="#fff"/><circle cx="15" cy="10" r="6" fill="#BC002D"/>',
    'KR': _kr(),
    'TZ': '<rect width="30" height="20" fill="#00A3DD"/><path d="M0 0H30L0 20z" fill="#1EB53A"/><path d="M0 20L30 0" stroke="#FCD116" stroke-width="7.5"/><path d="M0 20L30 0" stroke="#000" stroke-width="5"/>',
    'PH': '<rect width="30" height="20" fill="#0038A8"/><rect y="10" width="30" height="10" fill="#CE1126"/><path d="M0 0L17.3 10L0 20z" fill="#fff"/><circle cx="5.8" cy="10" r="2.1" fill="#FCD116"/>' + star(2, 3, 1, 0, '#FCD116') + star(2, 17, 1, 0, '#FCD116') + star(14.6, 10, 1, 0, '#FCD116'),
}

# língua → bandeira (escolhas: PT Brasil, EN Reino Unido, AR Emirados, SW Tanzânia)
LINGUA = {'AR': 'AE', 'BG': 'BG', 'BN': 'BD', 'CS': 'CZ', 'DA': 'DK', 'DE': 'DE', 'EL': 'GR', 'EN': 'GB', 'ES': 'ES',
          'FA': 'IR', 'FI': 'FI', 'FIL': 'PH', 'FR': 'FR', 'HE': 'IL', 'HI': 'IN', 'HR': 'HR', 'HU': 'HU', 'ID': 'ID',
          'IT': 'IT', 'JA': 'JP', 'KO': 'KR', 'MK': 'MK', 'MS': 'MY', 'NB': 'NO', 'NL': 'NL', 'PL': 'PL', 'PT': 'BR',
          'RO': 'RO', 'RU': 'RU', 'SK': 'SK', 'SR': 'RS', 'SV': 'SE', 'SW': 'TZ', 'TH': 'TH', 'TR': 'TR', 'UK': 'UA',
          'UR': 'PK', 'VI': 'VN', 'ZH': 'CN'}


def svg(lang, w):
    h = w * 2 / 3
    return (f'<svg class="flag" viewBox="0 0 30 20" width="{w:.0f}" height="{h:.0f}" preserveAspectRatio="none">'
            f'<clipPath id="c{lang}"><rect width="30" height="20"/></clipPath><g clip-path="url(#c{lang})">{FLAGS[LINGUA[lang]]}</g></svg>')


if __name__ == '__main__':
    # folha de prova com todas as bandeiras
    import pathlib
    cells = ''.join(f'<div style="display:flex;align-items:center;gap:10px;font:14px monospace;color:#eee">{svg(c, 60)}{c}</div>' for c in sorted(LINGUA))
    out = pathlib.Path('/tmp/claude-0/-home-claude/b2449931-47b8-5ce8-8b11-520d2018e276/scratchpad/flags.html')
    out.write_text(f'<body style="margin:0;background:#1B1E1E;padding:20px;display:grid;grid-template-columns:repeat(6,140px);gap:14px">{cells}</body>')
    print(out)
