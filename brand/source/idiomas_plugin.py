"""OptiMOB — arte "17 languages" (EN), inspirada no seletor de idioma do plugin.

Uso: python3 brand/source/idiomas_plugin.py
Gera brand/instagram/feed/4x5/05-languages-en.png (1080 × 1350) e
brand/instagram/stories/languages-en.png (1080 × 1920).
"""
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from bandeiras import svg as bandeira  # noqa: E402

BRAND = pathlib.Path(__file__).resolve().parent.parent
FONTS = BRAND / 'fonts'
LOGO = (BRAND / 'svg' / 'optimob-sem-regua.svg').read_text()

# (código, nome nativo, estado) — estado: ok | beta (árabe e hebraico: experimentais, sem RTL)
LANGS = [('AR', 'العربية', 'beta'), ('CS', 'Čeština', 'ok'), ('DE', 'Deutsch', 'ok'), ('EN', 'English', 'ok'),
         ('ES', 'Español', 'ok'), ('FR', 'Français', 'ok'), ('HE', 'עברית', 'beta'), ('HU', 'Magyar', 'ok'),
         ('IT', 'Italiano', 'ok'), ('NL', 'Nederlands', 'ok'), ('PL', 'Polski', 'ok'), ('PT', 'Português', 'ok'),
         ('RU', 'Русский', 'ok'), ('SR', 'Srpski', 'ok'), ('UK', 'Українська', 'ok'), ('VI', 'Tiếng Việt', 'ok'),
         ('ZH', '简体中文', 'ok')]
SELECTED = 'EN'

# as 39 línguas do email de confirmação (supabase/functions/confirmar-inscricao)
LANGS39 = sorted([('PT', 'Português'), ('EN', 'English'), ('ES', 'Español'), ('FR', 'Français'), ('RU', 'Русский'),
    ('AR', 'العربية'), ('VI', 'Tiếng Việt'), ('ZH', '简体中文'), ('DE', 'Deutsch'), ('IT', 'Italiano'),
    ('NL', 'Nederlands'), ('PL', 'Polski'), ('TR', 'Türkçe'), ('EL', 'Ελληνικά'), ('UK', 'Українська'),
    ('RO', 'Română'), ('CS', 'Čeština'), ('SK', 'Slovenčina'), ('HU', 'Magyar'), ('SV', 'Svenska'),
    ('DA', 'Dansk'), ('NB', 'Norsk'), ('FI', 'Suomi'), ('MK', 'Македонски'), ('BG', 'Български'),
    ('SR', 'Српски'), ('HR', 'Hrvatski'), ('HE', 'עברית'), ('FA', 'فارسی'), ('UR', 'اردو'),
    ('HI', 'हिन्दी'), ('BN', 'বাংলা'), ('ID', 'Bahasa Indonesia'), ('MS', 'Bahasa Melayu'), ('TH', 'ไทย'),
    ('JA', '日本語'), ('KO', '한국어'), ('SW', 'Kiswahili'), ('FIL', 'Filipino')])
LANGS39 = [(c, n, 'ok') for c, n in LANGS39]

CHECK = '<svg viewBox="0 0 20 20" width="{s}" height="{s}"><circle cx="10" cy="10" r="10" fill="#3FB950"/><path d="M5.5 10.3l3 3 6-6.3" fill="none" stroke="#0B1F12" stroke-width="2.4"/></svg>'
BETA = '<svg viewBox="0 0 20 20" width="{s}" height="{s}"><circle cx="10" cy="10" r="8.6" fill="none" stroke="#F0A04B" stroke-width="2.6"/></svg>'
TICK = '<svg viewBox="0 0 24 24" width="26" height="26"><path d="M4 12.5l5 5L20 6.5" fill="none" stroke="#3AA0FF" stroke-width="3"/></svg>'


def page(w, h, row, fs, title_fs, pad_top, langs=None, cols=1):
    langs = langs or LANGS
    rows = []
    for code, name, st in langs:
        ic = (CHECK if st == 'ok' else BETA).format(s=int(row * .5))
        on = code == SELECTED
        tag = '<span class="beta">BETA</span>' if st == 'beta' else ''
        fl = bandeira(code, row * .62)
        rows.append(f'<div class="r{" on" if on else ""}">{ic}{fl}<b>{code}</b><i></i><span class="n">{name}</span>{tag}'
                    f'<span class="tk">{TICK if on else ""}</span></div>')
    sel = next(l for l in langs if l[0] == SELECTED)
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'JetBrains Mono';font-weight:500;src:url({(FONTS/'jetbrains-mono-latin-500-normal.woff2').as_uri()})}}
@font-face{{font-family:'JetBrains Mono';font-weight:700;src:url({(FONTS/'jetbrains-mono-latin-700-normal.woff2').as_uri()})}}
@font-face{{font-family:'Noto Sans Arabic';font-weight:500;src:url({(FONTS/'noto-sans-arabic-arabic-500-normal.woff2').as_uri()})}}
@font-face{{font-family:'Noto Sans Devanagari';font-weight:500;src:url({(FONTS/'noto-sans-devanagari-devanagari-500-normal.woff2').as_uri()})}}
@font-face{{font-family:'Noto Sans Bengali';font-weight:500;src:url({(FONTS/'noto-sans-bengali-bengali-500-normal.woff2').as_uri()})}}
@font-face{{font-family:'Noto Sans Thai';font-weight:500;src:url({(FONTS/'noto-sans-thai-thai-500-normal.woff2').as_uri()})}}
@font-face{{font-family:'Noto Sans Hebrew';font-weight:500;src:url({(FONTS/'noto-sans-hebrew-hebrew-500-normal.woff2').as_uri()})}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{w}px;height:{h}px;overflow:hidden;background:#1B1E1E;color:#EEF0EA;font-family:'Inter Display','Inter','Noto Sans Arabic','Noto Sans Hebrew','Noto Sans Devanagari','Noto Sans Bengali','Noto Sans Thai','Noto Sans CJK SC','Noto Sans CJK KR',sans-serif;-webkit-font-smoothing:antialiased}}
.post{{position:relative;width:{w}px;height:{h}px;padding:{pad_top}px 84px 70px;display:flex;flex-direction:column}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(58,160,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(58,160,255,.06) 1px,transparent 1px);background-size:54px 54px;-webkit-mask-image:radial-gradient(ellipse at 50% 40%,#000 20%,transparent 78%)}}
.post>*{{position:relative}}
.corner{{position:absolute;width:34px;height:34px;border:0 solid #8A918F}}
.c1{{left:36px;top:36px;border-left-width:2px;border-top-width:2px}}.c2{{right:36px;top:36px;border-right-width:2px;border-top-width:2px}}
.c3{{left:36px;bottom:36px;border-left-width:2px;border-bottom-width:2px}}.c4{{right:36px;bottom:36px;border-right-width:2px;border-bottom-width:2px;border-color:#3AA0FF}}
.lbl{{font:500 26px 'JetBrains Mono';letter-spacing:.26em;color:#3AA0FF}}
h1{{margin:18px 0 {int(title_fs*.45)}px;font-size:{title_fs}px;font-weight:700;letter-spacing:-.045em;line-height:1}}
h1 span{{color:#3AA0FF}}
.panel{{flex:1;min-height:0;display:flex;flex-direction:column;background:#111313;border:2px solid #2A2F30}}
.head{{display:flex;justify-content:space-between;align-items:center;padding:{int(row*.42)}px 24px}}
.head b{{font-size:{fs+2}px;font-weight:600}}
.head span{{font:500 {fs-8}px 'JetBrains Mono';color:#8A918F;border:2px solid #2A2F30;padding:8px 12px;display:flex;gap:8px;align-items:center}}
.sel{{display:flex;align-items:center;gap:14px;margin:0 24px;height:{max(int(row*1.25), 56)}px;flex:none;padding:0 18px;background:#1B1E1E;border:2px solid #3AA0FF;font-size:{fs}px}}
.sel b{{font:700 {fs}px 'JetBrains Mono'}} .sel i{{width:2px;height:{int(row*.5)}px;background:#2A2F30}} .sel .cv{{margin-left:auto;color:#3AA0FF}}
.list{{margin:{int(row*.3)}px 24px 24px;border:2px solid #2A2F30;background:#1B1E1E;flex:1;display:flex;flex-direction:column}}
.auto{{font-style:italic;color:#6F7674;font-size:{fs-2}px;padding:0 20px;height:{row}px;display:flex;align-items:center;border-bottom:2px solid #2A2F30}}
.r{{display:flex;align-items:center;gap:{12 if cols > 1 else 14}px;height:{row}px;padding:0 {14 if cols > 1 else 20}px;font-size:{fs}px;color:#C9CDCB}}
.r b{{font:700 {fs}px 'JetBrains Mono';color:#EEF0EA;width:{int(fs*(2.4 if cols > 1 else 1.75))}px}}
.r i{{width:2px;height:{int(row*.5)}px;background:#2A2F30}}
.r .n{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.r .beta{{font:700 {fs-10}px 'JetBrains Mono';letter-spacing:.14em;color:#F0A04B;border:2px solid rgba(240,160,75,.5);padding:3px 8px}}
.r .tk{{margin-left:auto;display:flex}}
.flag{{flex:none;box-shadow:0 0 0 1px rgba(238,240,234,.18)}}
.r.on{{background:rgba(58,160,255,.12);color:#EEF0EA;box-shadow:inset 4px 0 0 #3AA0FF}}
.foot{{display:flex;justify-content:space-between;align-items:center;padding-top:28px}}
.foot .lg{{width:200px}} .foot span{{font:500 21px 'JetBrains Mono';letter-spacing:.2em;color:#8A918F}}
</style></head><body><div class="post"><div class="grid"></div>
<i class="corner c1"></i><i class="corner c2"></i><i class="corner c3"></i><i class="corner c4"></i>
<div class="lbl">OPTIMOB FOR SKETCHUP</div>
<h1>Available in<br><span>{len(langs)} languages.</span></h1>
<div class="panel">
  <div class="head"><b>Language</b><span>↺ Restore defaults</span></div>
  <div class="sel">{CHECK.format(s=int(row*.5))}{bandeira(sel[0], max(row, 48) * .62)}<b>{sel[0]}</b><i></i>{sel[1]}<span class="cv">▾</span></div>
  <div class="list"><div class="auto">Automatic</div><div class="rows" style="display:grid;grid-template-columns:repeat({cols},minmax(0,1fr));grid-auto-flow:column;grid-template-rows:repeat({-(-len(rows)//cols)},auto)">{"".join(rows)}</div></div>
</div>
<div class="foot"><div class="lg">{LOGO}</div><span>OPTIMOBSYSTEM.COM</span></div>
</div></body></html>'''


def main():
    from playwright.sync_api import sync_playwright
    out = [(BRAND / 'instagram' / 'feed' / '4x5' / '05-languages-en.png', 1080, 1350, 41, 22, 64, 76, LANGS, 1),
           (BRAND / 'instagram' / 'stories' / 'languages-en.png', 1080, 1920, 59, 28, 96, 200, LANGS, 1),
           (BRAND / 'instagram' / 'feed' / '4x5' / '06-languages-39-en.png', 1080, 1350, 34, 20, 64, 76, LANGS39, 2),
           (BRAND / 'instagram' / 'stories' / 'languages-39-en.png', 1080, 1920, 50, 25, 96, 200, LANGS39, 2)]
    tmp = BRAND / 'instagram' / '_tmp.html'
    with sync_playwright() as p:
        b = p.chromium.launch()
        for path, w, h, row, fs, tfs, pt, langs, cols in out:
            path.parent.mkdir(parents=True, exist_ok=True)
            pg = b.new_page(viewport={'width': w, 'height': h})
            tmp.write_text(page(w, h, row, fs, tfs, pt, langs, cols)); pg.goto(tmp.as_uri()); pg.wait_for_timeout(400)
            over = pg.evaluate("(() => { const l=document.querySelector('.list'), r=document.querySelector('.rows')||l; return Math.round(r.getBoundingClientRect().bottom - l.getBoundingClientRect().bottom); })()")
            pg.screenshot(path=str(path)); pg.close()
            print(path.name, 'overflow', over)
        b.close()
    tmp.unlink()


if __name__ == '__main__':
    main()
