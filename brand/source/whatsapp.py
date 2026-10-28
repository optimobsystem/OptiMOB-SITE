"""OptiMOB — fundo de conversa para grupos de WhatsApp.

Uso: python3 brand/source/whatsapp.py
Gera brand/whatsapp/fundo-escuro.png e fundo-claro.png (1440 × 3120, ecrã de telemóvel)
e uma pré-visualização com conversa simulada.
Padrão "doodle" técnico: móveis em linha, chapas com peças, cotas, ferragens, o símbolo da marca.
Contraste baixo de propósito, para as mensagens continuarem legíveis.
"""
import math, pathlib, random

BRAND = pathlib.Path(__file__).resolve().parent.parent
OUT = BRAND / 'whatsapp'
FONTS = BRAND / 'fonts'
W, H = 1440, 3120

# ícones desenhados numa caixa 100 × 100, só traço
ICONS = {
    'roupeiro': '<path d="M22 14h56v74H22zM50 14v74M22 80h56"/><path d="M44 46v8M56 46v8"/>',
    'iso': '<path d="M18 38l32-16 32 16v34L50 88 18 72z"/><path d="M18 38l32 16 32-16M50 54v34"/><path d="M34 46v26M66 46v26" stroke-dasharray="4 5"/>',
    'chapa': '<path d="M10 22h80v56H10z" stroke-dasharray="5 4"/><path d="M14 26h40v24H14zM58 26h28v24H58zM14 54h22v20H14zM40 54h22v20H40z"/>',
    'cota': '<path d="M14 60h72M14 50v20M86 50v20M14 60l8-5M14 60l8 5M86 60l-8-5M86 60l-8 5"/>',
    'regua': '<path d="M10 40h80v20H10z"/><path d="M20 40v8M30 40v12M40 40v8M50 40v12M60 40v8M70 40v12M80 40v8"/>',
    'serra': '<circle cx="50" cy="50" r="30"/><circle cx="50" cy="50" r="6"/><path d="M50 20l6 8M80 50l-8 6M50 80l-6-8M20 50l8-6M71 29l-2 10M71 71l-10-2M29 71l2-10M29 29l10 2"/>',
    'dobradica': '<path d="M20 30h26v40H20zM54 30h26v40H54z"/><circle cx="50" cy="50" r="5"/><circle cx="30" cy="40" r="3"/><circle cx="30" cy="60" r="3"/><circle cx="70" cy="40" r="3"/><circle cx="70" cy="60" r="3"/>',
    'cavilha': '<path d="M38 14h24v72H38z"/><path d="M38 26l24 6M38 40l24 6M38 54l24 6M38 68l24 6"/>',
    'gaveta': '<path d="M16 26h68v48H16z"/><path d="M16 42h68M16 58h68M44 34h12M44 50h12M44 66h12"/>',
    'simbolo': '<circle cx="50" cy="40" r="24"/><rect x="46" y="36" width="8" height="8" class="f"/><path d="M24 80h44M24 75v10"/><rect x="68" y="74" width="12" height="12" class="f"/>',
    'esquadro': '<path d="M18 18v64h64z"/><path d="M30 46v24h24z"/>',
    'parafuso': '<path d="M38 18h24l-4 10H42z"/><path d="M44 28v50l6 8 6-8V28"/><path d="M44 38l12 4M44 48l12 4M44 58l12 4M44 68l12 4"/>',
    'prateleira': '<path d="M16 20h68v62H16z"/><path d="M16 40h68M16 60h68"/><path d="M26 32h10M40 52h14M60 74h12"/>',
}
TEXTS = ['L 1800', 'A 2400', 'P 580', '18 mm', '2750 × 1830', 'PRT·1', 'LAT·2', '94,6%', 'FRG·3', 'ORLA 1 mm', 'SERRA 4 mm']


def pattern(stroke, text_col, fill_col, seed=11):
    rnd = random.Random(seed)
    cell = 250
    cols, rows = W // cell + 2, H // cell + 2
    names = list(ICONS)
    out = []
    k = 0
    for r in range(rows):
        for c in range(cols):
            x = c * cell + (cell / 2 if r % 2 else 0) + rnd.uniform(-30, 30)
            y = r * cell * 0.86 + rnd.uniform(-24, 24)
            rot = rnd.choice([-18, -10, 0, 0, 8, 14, 22])
            k += 1
            if k % 5 == 0:
                t = rnd.choice(TEXTS)
                out.append(f'<text x="{x:.0f}" y="{y:.0f}" transform="rotate({rot} {x:.0f} {y:.0f})" '
                           f'font-family="JetBrains Mono" font-size="36" letter-spacing="4" fill="{text_col}" text-anchor="middle">{t}</text>')
            else:
                n = names[(k * 7 + r) % len(names)]
                s = rnd.uniform(1.35, 1.65)
                out.append(f'<g transform="translate({x:.0f} {y:.0f}) rotate({rot}) scale({s:.2f}) translate(-50 -50)">{ICONS[n]}</g>')
    return (f'<g fill="none" stroke="{stroke}" stroke-width="2.6" stroke-linecap="square" stroke-linejoin="miter">'
            f'<style>.f{{fill:{fill_col};stroke:none}}</style>{"".join(out)}</g>')


THEMES = {
    'escuro': dict(bg='#111313', stroke='rgba(58,160,255,.19)', text='rgba(238,240,234,.12)', fill='rgba(58,160,255,.22)'),
    'claro': dict(bg='#EEF0EA', stroke='rgba(31,111,194,.16)', text='rgba(27,30,30,.12)', fill='rgba(31,111,194,.24)'),
}


def page(t):
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'JetBrains Mono';src:url({(FONTS/'jetbrains-mono-latin-500-normal.woff2').as_uri()})}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;background:{t['bg']}}}
</style></head><body><svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{pattern(t['stroke'], t['text'], t['fill'])}</svg></body></html>'''


def preview(paths):
    # telemóveis com conversa simulada por cima do fundo, para avaliar a legibilidade
    def phone(img, dark):
        bub_in, bub_out, txt, meta, top = (('#1F2C34', '#005C4B', '#E9EDEF', '#8696A0', '#1F2C34') if dark
                                           else ('#FFFFFF', '#D9FDD3', '#111B21', '#667781', '#F0F2F5'))
        msgs = [('in', 'Mateus', 'Bom dia! Nova versão do OptiMOB já está na pasta do grupo 🙌'),
                ('in', 'Ana', 'Testei o nesting no roupeiro de 2 módulos, ficou em 94,6%'),
                ('out', '', 'Top! Alguém testou o rodapé com 80 mm?'),
                ('in', 'Rui', 'Sim, a lista de corte bateu certo com a serra'),
                ('out', '', 'Perfeito 👌')]
        b = ''
        for side, who, m in msgs:
            al = 'flex-end' if side == 'out' else 'flex-start'
            bg = bub_out if side == 'out' else bub_in
            name = f'<div style="font-size:12px;font-weight:600;color:#3AA0FF;margin-bottom:2px">{who}</div>' if who else ''
            b += f'<div style="display:flex;justify-content:{al}"><div style="max-width:76%;background:{bg};color:{txt};padding:7px 10px 6px;border-radius:8px;font-size:14px;line-height:1.35;box-shadow:0 1px .5px rgba(0,0,0,.13)">{name}{m}<div style="text-align:right;font-size:11px;color:{meta};margin-top:2px">10:4{len(m)%10}</div></div></div>'
        return f'''<div style="width:390px;height:844px;border-radius:44px;overflow:hidden;border:10px solid #050606;position:relative;background:url({img.as_uri()}) center/cover">
<div style="background:{top};color:{txt};height:96px;display:flex;align-items:flex-end;padding:0 18px 12px;gap:12px;font-family:Inter,sans-serif">
<div style="width:38px;height:38px;border-radius:50%;background:#1B1E1E;display:flex;align-items:center;justify-content:center"><svg viewBox="0 0 100 100" width="28" height="28"><circle cx="50" cy="40" r="24" fill="none" stroke="#EEF0EA" stroke-width="8"/><rect x="45" y="35" width="10" height="10" fill="#3AA0FF"/><rect x="24" y="78" width="44" height="6" fill="#3AA0FF"/><rect x="68" y="74" width="12" height="12" fill="#3AA0FF"/></svg></div>
<div><div style="font-weight:600;font-size:16px">OptiMOB · Beta</div><div style="font-size:12px;color:{meta}">Mateus, Ana, Rui, você</div></div></div>
<div style="display:flex;flex-direction:column;gap:6px;padding:18px 12px;font-family:Inter,sans-serif">{b}</div></div>'''
    return f'''<!doctype html><html><body style="margin:0;background:#0b0c0c;display:flex;gap:48px;padding:48px;width:max-content">
{phone(paths['escuro'], True)}{phone(paths['claro'], False)}</body></html>'''


def main():
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / '_tmp.html'
    paths = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': W, 'height': H})
        for name, t in THEMES.items():
            tmp.write_text(page(t)); pg.goto(tmp.as_uri()); pg.wait_for_timeout(300)
            paths[name] = OUT / f'fundo-{name}.png'
            pg.screenshot(path=str(paths[name]))
        pg = b.new_page(viewport={'width': 960, 'height': 960})
        tmp.write_text(preview(paths)); pg.goto(tmp.as_uri()); pg.wait_for_timeout(500)
        pg.screenshot(path=str(OUT / 'preview.png'), full_page=True)
        b.close()
    tmp.unlink()
    print('ok', OUT)


if __name__ == '__main__':
    main()
