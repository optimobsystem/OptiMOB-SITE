"""OptiMOB — Reel 02 «Satisfying» (EN).

Uso: python3 brand/source/reel_satisfying.py
Gera brand/instagram/reels/02-satisfying-en.mp4 (1080 × 1920, 30 fps) com som sintetizado:
um «toc» de madeira por peça, um «zip» por corte de serra e um acorde no fim.
Usa o mesmo nesting do post 01 do feed (94,6% de aproveitamento), com a chapa na vertical.
"""
import json, math, pathlib, shutil, subprocess, sys, wave
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import feed  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
BRAND = ROOT / 'brand'
OUT = BRAND / 'instagram' / 'reels'
FONTS = BRAND / 'fonts'
FPS, DUR = 30, 16.0
LOGO = (BRAND / 'svg' / 'optimob-sem-regua.svg').read_text()

EN = {'LAT': 'SIDE', 'TRV': 'RAIL', 'TPO': 'TOP', 'PRT': 'SHELF', 'FRG': 'DRAWER', 'TRS': 'BACK'}

# chapa na vertical: 1830 de largura no ecrã, 2750 de altura
SW, SH = feed.SHEET_H, feed.SHEET_W
BOX = dict(left=150, top=360, w=780)
BOX['h'] = BOX['w'] * SH / SW
SC = BOX['w'] / SW

parts, sobra, yld = feed.nesting()
# rodar: x_ecrã = y_mm, y_ecrã = x_mm
P = [dict(code=EN[p['code']], idx=p['idx'], x=p['y'], y=p['x'], w=p['h'], h=p['w']) for p in parts]
SOBRA = dict(x=sobra['y'], y=sobra['x'], w=sobra['h'], h=sobra['w'])
# cada coluna enche de baixo para cima
cols = sorted({p['x'] for p in P})
order = sorted(P, key=lambda p: (cols.index(p['x']), -p['y']))

T0, STEP, FALL = 1.2, 0.68, 0.5
for i, p in enumerate(order):
    p['t0'] = T0 + i * STEP
    p['land'] = p['t0'] + FALL
LAST = order[-1]['land']

# cortes de serra (guilhotina): entre colunas e entre peças da mesma coluna
K = feed.KERF
cuts = []
for c in cols[1:]:
    cuts.append(dict(x1=c - K / 2, y1=0, x2=c - K / 2, y2=SH))
for c in cols:
    col = sorted([p for p in P if p['x'] == c], key=lambda p: p['y'])
    w = max(p['w'] for p in col)
    for p in col:
        cuts.append(dict(x1=c, y1=p['y'] + p['h'] + K / 2, x2=c + w, y2=p['y'] + p['h'] + K / 2))
C0, CSTEP, CDUR = LAST + 0.45, 0.17, 0.22
for i, c in enumerate(cuts):
    c['t0'] = C0 + i * CSTEP
CEND = cuts[-1]['t0'] + CDUR
OFF_T = CEND + 0.15
END_T = OFF_T + 1.3

DATA = dict(P=P, SOBRA=SOBRA, CUTS=cuts, SC=SC, BOX=BOX, SW=SW, SH=SH, TRIM=feed.TRIM,
            YLD=yld * 100, OFF_T=OFF_T, END_T=END_T, AREA=SW * SH)

HTML = r'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:'JetBrains Mono';font-weight:400;src:url(__F__/jetbrains-mono-latin-400-normal.woff2)}
@font-face{font-family:'JetBrains Mono';font-weight:500;src:url(__F__/jetbrains-mono-latin-500-normal.woff2)}
@font-face{font-family:'JetBrains Mono';font-weight:700;src:url(__F__/jetbrains-mono-latin-700-normal.woff2)}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden;background:#1B1E1E;color:#EEF0EA;font-family:'Inter Display','Inter',sans-serif;-webkit-font-smoothing:antialiased}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(58,160,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(58,160,255,.06) 1px,transparent 1px);background-size:54px 54px;-webkit-mask-image:radial-gradient(ellipse at 50% 45%,#000 25%,transparent 80%)}
.top{position:absolute;left:80px;right:80px;top:150px;display:flex;justify-content:space-between;align-items:flex-start}
.top .lg{width:230px;margin-top:8px}
.y{text-align:right}
.y b{font:700 96px 'Inter Display';letter-spacing:-.05em;line-height:.85;color:#3AA0FF}
.y b small{font-size:.5em}
.y span{display:block;font:400 21px 'JetBrains Mono';letter-spacing:.22em;color:#8A918F;margin-top:12px}
.lbl{position:absolute;left:80px;top:268px;font:500 24px 'JetBrains Mono';letter-spacing:.24em;color:#8A918F}
.lbl b{color:#3AA0FF;font-weight:500}
#st{position:absolute;left:0;top:0;overflow:visible}
.end{position:absolute;left:80px;right:80px;top:520px}
.end .k{font:500 30px 'JetBrains Mono';letter-spacing:.24em;color:#3AA0FF}
.end h1{margin-top:36px;font-size:150px;font-weight:700;letter-spacing:-.05em;line-height:.93}
.end h1 span{color:#3AA0FF}
.end .cta{margin-top:90px;display:inline-flex;align-items:center;background:#3AA0FF;color:#1B1E1E;font:700 36px 'JetBrains Mono';padding:26px 32px;letter-spacing:.06em}
.end .sub{margin-top:24px;font:400 26px 'JetBrains Mono';letter-spacing:.22em;color:#8A918F}
.corner{position:absolute;width:40px;height:40px;border:0 solid #8A918F}
.c1{left:40px;top:110px;border-left-width:2px;border-top-width:2px}.c2{right:40px;top:110px;border-right-width:2px;border-top-width:2px}
.c3{left:40px;bottom:330px;border-left-width:2px;border-bottom-width:2px}.c4{right:40px;bottom:330px;border-right-width:2px;border-bottom-width:2px;border-color:#3AA0FF}
</style></head><body><div class="grid"></div>
<i class="corner c1"></i><i class="corner c2"></i><i class="corner c3"></i><i class="corner c4"></i>
<div id="root"></div>
<script>
var D = __DATA__, LOGO = __LOGO__;
var clamp = function(x){ return Math.max(0, Math.min(1, x)); };
var outBack = function(x){ x = clamp(x); var c = 1.25, c3 = c + 1; return 1 + c3 * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
var inQuad = function(x){ x = clamp(x); return x * x; };
var outCubic = function(x){ x = clamp(x); return 1 - Math.pow(1 - x, 3); };
var B = D.BOX, S = D.SC;
function X(mm){ return B.left + (mm + D.TRIM) * S; }
function Y(mm){ return B.top + (mm + D.TRIM) * S; }

window.render = function(t){
  var o = [];
  var sheetA = clamp((t - .1) / .9);
  var endA = clamp((t - D.END_T) / .4), mainA = 1 - endA;
  // chapa
  var per = 2 * (B.w + B.h);
  o.push('<rect x="' + B.left + '" y="' + B.top + '" width="' + B.w + '" height="' + B.h + '" fill="rgba(238,240,234,' + (.025 * sheetA) + ')" stroke="#8A918F" stroke-width="2" stroke-dasharray="' + per + '" stroke-dashoffset="' + (per * (1 - outCubic(sheetA))) + '"/>');
  // sobra
  if (t > D.OFF_T) {
    var a = clamp((t - D.OFF_T) / .5), so = D.SOBRA;
    var h = so.h * S * outCubic(a);
    o.push('<defs><pattern id="h" width="18" height="18" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="18" stroke="#2A2F30" stroke-width="6"/></pattern></defs>');
    o.push('<rect x="' + X(so.x) + '" y="' + Y(so.y) + '" width="' + so.w * S + '" height="' + h + '" fill="url(#h)"/>');
    o.push('<text x="' + (X(so.x) + so.w * S / 2) + '" y="' + (Y(so.y) + so.h * S / 2 + 8) + '" fill="#8A918F" font-family="JetBrains Mono" font-size="22" letter-spacing="3" text-anchor="middle" opacity="' + a + '">OFFCUT</text>');
  }
  // peças
  var area = 0;
  D.P.forEach(function(p){
    if (t < p.t0) return;
    var k = clamp((t - p.t0) / (p.land - p.t0));
    var dy = (1 - inQuad(k)) * -(Y(p.y) + p.h * S + 40);
    if (t >= p.land) { area += p.w * p.h; var b = clamp((t - p.land) / .18); dy = Math.sin(b * Math.PI) * -6 * (1 - b); }
    var flash = t >= p.land ? Math.max(0, 1 - (t - p.land) / .35) : 0;
    var x = X(p.x), y = Y(p.y) + dy, w = p.w * S, h = p.h * S;
    o.push('<g><rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" fill="rgba(58,160,255,' + (.13 + .35 * flash) + ')" stroke="#3AA0FF" stroke-width="2"/>');
    var fs = w > 150 ? 26 : 20;
    o.push('<text x="' + (x + 14) + '" y="' + (y + 14 + fs) + '" fill="#3AA0FF" font-family="JetBrains Mono" font-weight="500" font-size="' + fs + '">' + p.code + '·' + p.idx + '</text>');
    if (h > 120) o.push('<text x="' + (x + 14) + '" y="' + (y + 22 + fs * 2) + '" fill="#8A918F" font-family="JetBrains Mono" font-size="' + (fs * .78) + '">' + p.h + '×' + p.w + '</text>');
    o.push('</g>');
  });
  // cortes
  D.CUTS.forEach(function(c){
    if (t < c.t0) return;
    var k = outCubic((t - c.t0) / .22), fade = clamp((t - c.t0 - .22) / .6);
    var x1 = X(c.x1), y1 = Y(c.y1), x2 = x1 + (X(c.x2) - x1) * k, y2 = y1 + (Y(c.y2) - y1) * k;
    o.push('<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" stroke="#EEF0EA" stroke-width="' + (5 - 3 * fade) + '" opacity="' + (1 - .55 * fade) + '" style="filter:drop-shadow(0 0 8px #3AA0FF)"/>');
    if (k < 1) o.push('<circle cx="' + x2 + '" cy="' + y2 + '" r="9" fill="#EEF0EA" style="filter:drop-shadow(0 0 12px #3AA0FF)"/>');
  });
  var pct = (area / D.AREA * 100).toFixed(1).replace('.', ',');
  var n = D.P.filter(function(p){ return t >= p.land; }).length;
  var html = '<div style="opacity:' + mainA + '"><div class="top"><div class="lg">' + LOGO + '</div><div class="y"><b>' + pct + '<small>%</small></b><span>SHEET YIELD</span></div></div>' +
    '<div class="lbl" style="opacity:' + sheetA + '">SHEET 2750 × 1830 · <b>' + n + '/' + D.P.length + ' PARTS</b></div>' +
    '<svg id="st" width="1080" height="1920" viewBox="0 0 1080 1920">' + o.join('') + '</svg></div>';
  if (endA > 0) {
    var a = function(d){ var x = clamp((t - D.END_T - d) / .35); return 'opacity:' + x + ';transform:translateY(' + (1 - outCubic(x)) * 30 + 'px)'; };
    html += '<div class="top" style="opacity:' + endA + '"><div class="lg">' + LOGO + '</div></div><div class="end">' +
      '<div class="k" style="' + a(.05) + '">EVERY PART. ITS PLACE.</div>' +
      '<h1 style="' + a(.25) + '">Design<br>once.<br><span>Build<br>forever.</span></h1>' +
      '<div class="cta" style="' + a(.8) + '">GET EARLY ACCESS →</div><div class="sub" style="' + a(.95) + '">optimobsystem.com</div></div>';
  }
  document.getElementById('root').innerHTML = html;
};
render(0);
</script></body></html>'''


# ---------------------------------------------------------------- som
SR = 44100


def audio(path):
    n = int(SR * DUR)
    out = np.zeros(n)
    rng = np.random.default_rng(7)

    def add(t0, sig):
        i = int(t0 * SR)
        j = min(n, i + len(sig))
        out[i:j] += sig[:j - i]

    def tock(size):
        t = np.arange(int(SR * .35)) / SR
        f = 210 - 90 * size  # peças maiores soam mais graves
        body = np.sin(2 * np.pi * f * t) * np.exp(-t / .055)
        knock = np.sin(2 * np.pi * f * 2.7 * t) * np.exp(-t / .018) * .5
        click = rng.standard_normal(len(t)) * np.exp(-t / .004) * .35
        return (body + knock + click) * .55

    def zip_(dur=.24):
        t = np.arange(int(SR * dur)) / SR
        noise = rng.standard_normal(len(t))
        noise = np.diff(noise, prepend=0)  # agudo, tipo serra
        env = np.sin(np.pi * t / dur) ** 2
        tone = np.sin(2 * np.pi * (900 + 1400 * t / dur) * t) * .25
        return (noise * .08 + tone * .5) * env * .5

    def chime():
        t = np.arange(int(SR * 2.2)) / SR
        s = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((440, .5), (660, .35), (880, .25), (1320, .1)))
        return s * np.exp(-t / .7) * (1 - np.exp(-t / .01)) * .35

    big = max(p['w'] * p['h'] for p in P)
    for p in P:
        add(p['land'], tock(p['w'] * p['h'] / big))
    for c in cuts:
        add(c['t0'], zip_())
    add(OFF_T, tock(1.0) * .6)
    add(END_T + .25, chime())
    out = out / max(1e-9, np.abs(out).max()) * .85
    pcm = (out * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def main():
    from playwright.sync_api import sync_playwright
    html = HTML.replace('__F__', FONTS.as_uri()).replace('__DATA__', json.dumps(DATA)).replace('__LOGO__', json.dumps(LOGO))
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / '_reel.html'; tmp.write_text(html)
    frames = OUT / '_frames'
    shutil.rmtree(frames, ignore_errors=True); frames.mkdir()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.on('pageerror', lambda e: print('ERR', e))
        pg.goto(tmp.as_uri()); pg.wait_for_timeout(600)
        for i in range(int(FPS * DUR)):
            pg.evaluate(f'render({i / FPS})')
            pg.screenshot(path=str(frames / f'{i:04d}.png'))
        pg.evaluate(f'render({CEND + 0.6})'); pg.screenshot(path=str(OUT / '02-capa.png'))
        b.close()
    wav = OUT / '_som.wav'; audio(wav)
    mp4 = OUT / '02-satisfying-en.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', str(frames / '%04d.png'), '-i', str(wav),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'slow',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', str(mp4)], check=True)
    shutil.rmtree(frames); tmp.unlink(); wav.unlink()
    print('ok', mp4, f'peças {len(P)}, cortes {len(cuts)}, fim {END_T:.1f}s')


if __name__ == '__main__':
    main()
