"""OptiMOB — Reel 01 «Da medida ao plano de corte».

Uso: python3 brand/source/reel.py
Gera brand/instagram/reels/01-medida-plano-de-corte.mp4 (1080 × 1920, 30 fps, sem áudio:
junte uma música em tendência na própria app do Instagram).
O desenho, a lista de corte e o nesting são calculados pelo mesmo código do configurador do site.
"""
import pathlib, subprocess, shutil

ROOT = pathlib.Path(__file__).resolve().parents[2]
BRAND = ROOT / 'brand'
OUT = BRAND / 'instagram' / 'reels'
FONTS = BRAND / 'fonts'
FPS, DUR = 30, 15.0

app = (ROOT / 'site' / 'src' / 'app.js').read_text().splitlines()
start = next(i for i, l in enumerate(app) if l.strip().startswith('var C = {'))
end = next(i for i, l in enumerate(app) if '// ---------- UI ----------' in l)
CORE = '\n'.join(app[start:end])
LOGO = (BRAND / 'svg' / 'optimob-sem-regua.svg').read_text()

HTML = r'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:'JetBrains Mono';font-weight:400;src:url(__F__/jetbrains-mono-latin-400-normal.woff2)}
@font-face{font-family:'JetBrains Mono';font-weight:500;src:url(__F__/jetbrains-mono-latin-500-normal.woff2)}
@font-face{font-family:'JetBrains Mono';font-weight:700;src:url(__F__/jetbrains-mono-latin-700-normal.woff2)}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden;background:#1B1E1E;color:#EEF0EA;font-family:'Inter Display','Inter',sans-serif;-webkit-font-smoothing:antialiased}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(58,160,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(58,160,255,.06) 1px,transparent 1px);background-size:54px 54px;-webkit-mask-image:radial-gradient(ellipse at 50% 45%,#000 25%,transparent 80%)}
.sc{position:absolute;inset:0;padding:150px 80px 0}
.mono{font-family:'JetBrains Mono',monospace}
.lbl{font:500 30px 'JetBrains Mono';letter-spacing:.26em;text-transform:uppercase;color:#3AA0FF}
.top{position:absolute;left:80px;right:80px;top:150px;display:flex;justify-content:space-between;align-items:center}
.top .lg{width:230px}
.timer{font:500 44px 'JetBrains Mono';color:#3AA0FF;display:flex;align-items:center;gap:16px}
.timer i{width:18px;height:18px;background:#3AA0FF;display:block}
.hook{position:absolute;left:80px;right:80px;top:560px}
.hook h1{font-size:112px;font-weight:700;letter-spacing:-.045em;line-height:1.0}
.hook h1 span{display:inline-block}
.hook p{margin-top:56px;font-size:60px;font-weight:600;letter-spacing:-.03em;color:#3AA0FF}
.cab{position:absolute;left:80px;right:80px;top:250px;height:530px;display:flex;align-items:center;justify-content:center}
.cab svg{width:100%;height:100%}
.sls{position:absolute;left:80px;right:80px;top:790px}
.sl{margin-bottom:34px}
.sl-t{display:flex;justify-content:space-between;align-items:baseline;font:500 28px 'JetBrains Mono';letter-spacing:.2em;text-transform:uppercase;color:#8A918F}
.sl-t b{font:500 54px 'JetBrains Mono';letter-spacing:-.01em;color:#EEF0EA}
.sl-t b.hot{color:#3AA0FF}
.sl-t small{font-size:24px;color:#8A918F;margin-left:10px}
.sl-r{position:relative;height:30px;margin-top:12px}
.sl-r::before{content:"";position:absolute;left:0;right:0;top:13px;height:4px;background:#2A2F30}
.sl-r .fl{position:absolute;left:0;top:13px;height:4px;background:#3AA0FF}
.sl-r .hd{position:absolute;top:0;width:30px;height:30px;margin-left:-15px;background:#3AA0FF;box-shadow:0 0 0 8px #1B1E1E}
.sl-r .hd.grab{box-shadow:0 0 0 8px #1B1E1E,0 0 0 18px rgba(58,160,255,.25)}
table{position:absolute;left:80px;right:80px;top:1090px;width:920px;border-collapse:collapse;font:400 30px 'JetBrains Mono'}
th{font:500 22px 'JetBrains Mono';letter-spacing:.2em;color:#8A918F;text-align:left;padding:0 0 14px;border-bottom:2px solid #2A2F30}
td{padding:8px 0;border-bottom:1px solid #2A2F30;color:#C9CDCB}
td:first-child{color:#3AA0FF;font-weight:500;width:120px}
td.n{text-align:right} th.n{text-align:right}
td.hot{color:#EEF0EA;background:rgba(58,160,255,.12)}
.nh{position:absolute;left:80px;right:80px;top:270px;display:flex;justify-content:space-between;align-items:flex-end}
.nh h2{font-size:72px;font-weight:700;letter-spacing:-.04em;line-height:1}
.nh .y{text-align:right}
.nh .y b{font:700 110px 'Inter Display';letter-spacing:-.05em;line-height:.85;color:#3AA0FF}
.nh .y b small{font-size:.5em}
.nh .y span{display:block;font:400 22px 'JetBrains Mono';letter-spacing:.2em;color:#8A918F;margin-top:12px}
.sheets{position:absolute;left:80px;right:80px;top:470px;display:grid;grid-template-columns:1fr 1fr;gap:26px 30px}
.sheets svg{width:100%;display:block}
.sheets .sh{opacity:0}
.end{position:absolute;left:80px;right:80px;top:470px}
.end .steps{font:500 34px 'JetBrains Mono';letter-spacing:.06em;color:#8A918F;line-height:1.9}
.end .steps b{color:#3AA0FF;font-weight:500}
.end h1{margin-top:40px;font-size:132px;font-weight:700;letter-spacing:-.05em;line-height:.95}
.end h1 span{color:#3AA0FF}
.end .lg2{width:560px;margin-top:110px}
.end .cta{margin-top:46px;display:inline-flex;gap:22px;align-items:center;background:#3AA0FF;color:#1B1E1E;font:700 34px 'JetBrains Mono';padding:24px 30px;letter-spacing:.04em}
.end .sub{margin-top:22px;font:400 24px 'JetBrains Mono';letter-spacing:.22em;color:#8A918F;text-transform:uppercase}
.corner{position:absolute;width:40px;height:40px;border:0 solid #8A918F}
.c1{left:40px;top:110px;border-left-width:2px;border-top-width:2px}.c2{right:40px;top:110px;border-right-width:2px;border-top-width:2px}
.c3{left:40px;bottom:330px;border-left-width:2px;border-bottom-width:2px}.c4{right:40px;bottom:330px;border-right-width:2px;border-bottom-width:2px;border-color:#3AA0FF}
</style></head><body><div class="grid"></div>
<i class="corner c1"></i><i class="corner c2"></i><i class="corner c3"></i><i class="corner c4"></i>
<div id="root"></div>
<script>
(function(){
__CORE__
window.OPT = { PRESETS: PRESETS, compute: compute, drawCabinet: drawCabinet, drawSheet: drawSheet };
})();
var LOGO = __LOGO__;
var clamp = function(x){ return Math.max(0, Math.min(1, x)); };
var ease = function(x){ x = clamp(x); return x < .5 ? 4*x*x*x : 1 - Math.pow(-2*x + 2, 3) / 2; };
var seg = function(t, a, b){ return clamp((t - a) / (b - a)); };
var fmt = function(n){ return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ' '); };
var base = OPT.PRESETS.roupeiro;
var FINAL = Object.assign({}, base, { L: 2400, N: 6 });
var RF = OPT.compute(FINAL);

function params(t){
  var L = Math.round((base.L + (FINAL.L - base.L) * ease(seg(t, 3.6, 6.0))) / 10) * 10;
  var N = Math.round(base.N + (FINAL.N - base.N) * ease(seg(t, 6.6, 8.0)));
  return Object.assign({}, base, { L: L, N: N });
}
function timer(t){
  var e = Math.max(0, Math.min(t, 12.4) - 3.0);
  var s = e.toFixed(1).replace('.', ',');
  return '<div class="timer"><i></i>00:' + (e < 10 ? '0' : '') + s + 's</div>';
}
function header(t){ return '<div class="top"><div class="lg">' + LOGO + '</div>' + (t >= 3 ? timer(t) : '') + '</div>'; }

function hook(t){
  var words = 'Quanto tempo demoras a fazer a lista de corte de um roupeiro?'.split(' ');
  var h = words.map(function(w, i){
    var a = clamp((t - 0.15 - i * 0.11) / 0.18);
    return '<span style="opacity:' + a + ';transform:translateY(' + (1 - a) * 30 + 'px)">' + w + '</span>';
  }).join(' ');
  var p = clamp((t - 1.85) / .25);
  return '<div class="hook"><div class="lbl" style="margin-bottom:40px">Marcenaria · SketchUp</div><h1>' + h +
    '</h1><p style="opacity:' + p + '">Com o OptiMOB: segundos. ↓</p></div>';
}

function slider(label, val, unit, pos, hot){
  return '<div class="sl"><div class="sl-t"><span>' + label + '</span><b class="' + (hot ? 'hot' : '') + '">' + fmt(val) + '<small>' + unit + '</small></b></div>' +
    '<div class="sl-r"><i class="fl" style="width:' + (pos * 100).toFixed(1) + '%"></i><i class="hd' + (hot ? ' grab' : '') + '" style="left:' + (pos * 100).toFixed(1) + '%"></i></div></div>';
}

function config(t){
  var s = params(t), r = OPT.compute(s);
  var hotL = t > 3.4 && t < 6.3, hotN = t > 6.4 && t < 8.3;
  var sl = slider('Largura', s.L, 'mm', (s.L - 600) / (3000 - 600), hotL) +
           slider('Prateleiras por módulo', s.N, 'un', s.N / 8, hotN);
  var rows = r.parts.map(function(p){
    var hot = (hotL && /TPO|BAS|ROD|POR|PRT/.test(p.code)) || (hotN && p.code === 'PRT');
    return '<tr><td>' + p.code + '</td><td>' + p.name + '</td><td class="n">' + p.q + '</td><td class="n' + (hot ? ' hot' : '') + '">' + p.c + ' × ' + p.l + '</td></tr>';
  }).join('');
  var foot = '<tr><td></td><td style="color:#8A918F">' + r.pecas + ' peças · ' + r.orla.toFixed(1).replace('.', ',') + ' m de orla</td><td></td><td></td></tr>';
  return '<div class="cab">' + OPT.drawCabinet(s, r, { pad: .06 }) + '</div><div class="sls">' + sl + '</div>' +
    '<table><tr><th>PEÇA</th><th></th><th class="n">QTD</th><th class="n">C × L (mm)</th></tr>' + rows + foot + '</table>';
}

function nesting(t){
  var sheets = RF.nest.sheets, all = [];
  sheets.forEach(function(sh, i){ sh.parts.forEach(function(p, j){ all.push([i, j]); }); });
  var k = Math.floor(all.length * ease(seg(t, 9.2, 11.6)));
  var shown = sheets.map(function(){ return 0; });
  all.slice(0, k).forEach(function(a){ shown[a[0]]++; });
  var done = t >= 11.6;
  var svgs = sheets.map(function(sh, i){
    var parts = sh.parts.slice(0, shown[i]);
    var c = { parts: parts, area: parts.reduce(function(a, p){ return a + p.w * p.h; }, 0), sobra: done ? sh.sobra : null };
    var a = clamp((t - 8.9 - i * 0.06) / 0.25);
    return '<div class="sh" style="opacity:' + a + '">' + OPT.drawSheet(c) + '</div>';
  }).join('');
  var y = RF.nest.yield * 100 * ease(seg(t, 9.2, 11.8));
  return '<div class="nh"><div><div class="lbl" style="margin-bottom:22px">Nesting automático</div><h2>Plano de corte</h2></div>' +
    '<div class="y"><b>' + y.toFixed(1).replace('.', ',') + '<small>%</small></b><span>APROVEITAMENTO</span></div></div>' +
    '<div class="sheets">' + svgs + '</div>' +
    '<div class="mono" style="position:absolute;left:80px;top:' + (470 + Math.ceil(sheets.length / 2) * 360) + 'px;font-size:26px;letter-spacing:.14em;color:#8A918F;opacity:' + clamp((t - 11.6) / .3) + '">' +
    sheets.length + ' CHAPAS 2750 × 1830 · SERRA 4 MM · REFILO 10 MM</div>';
}

function end(t){
  var a = function(d){ var x = clamp((t - 12.7 - d) / .3); return 'opacity:' + x + ';transform:translateY(' + (1 - x) * 26 + 'px)'; };
  return '<div class="end"><div class="steps" style="' + a(0) + '">Medidas <b>→</b> lista de corte <b>→</b> plano de corte</div>' +
    '<h1 style="' + a(.25) + '">Desenhe<br>uma vez.<br><span>Fabrique<br>sempre.</span></h1>' +
    '<div class="cta" style="' + a(.9) + '">ACESSO ANTECIPADO →</div><div class="sub" style="' + a(1.05) + '">optimobsystem.com</div></div>';
}

function scene(t, a, b, fn){
  var o = Math.min(clamp((t - a) / .3), clamp((b - t) / .3));
  if (a === 0) o = clamp((b - t) / .3);
  if (b >= 99) o = clamp((t - a) / .3);
  return o > 0 ? '<div class="sc" style="opacity:' + o + '">' + fn(t) + '</div>' : '';
}
window.render = function(t){
  document.getElementById('root').innerHTML = header(t) +
    scene(t, 0, 3.0, hook) + scene(t, 2.85, 8.9, config) + scene(t, 8.75, 12.55, nesting) + scene(t, 12.45, 99, end);
};
render(0);
</script></body></html>'''


def main():
    from playwright.sync_api import sync_playwright
    import json
    html = HTML.replace('__F__', FONTS.as_uri()).replace('__CORE__', CORE).replace('__LOGO__', json.dumps(LOGO))
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / '_reel.html'; tmp.write_text(html)
    frames = OUT / '_frames'
    shutil.rmtree(frames, ignore_errors=True); frames.mkdir()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.goto(tmp.as_uri()); pg.wait_for_timeout(600)
        n = int(FPS * DUR)
        for i in range(n):
            pg.evaluate(f'render({i / FPS})')
            pg.screenshot(path=str(frames / f'{i:04d}.png'))
        for name, t in (('capa', 13.9),):
            pg.evaluate(f'render({t})'); pg.screenshot(path=str(OUT / f'01-{name}.png'))
        b.close()
    mp4 = OUT / '01-medida-plano-de-corte.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', str(frames / '%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'slow', '-movflags', '+faststart', str(mp4)], check=True)
    shutil.rmtree(frames); tmp.unlink()
    print('ok', mp4)


if __name__ == '__main__':
    main()
