/* OptiMOB — configurador paramétrico (desenho, lista de corte, nesting, etiquetas). Sem dependências. */
(function () {
  'use strict';

  var C = { blue: '#3AA0FF', bone: '#EEF0EA', ash: '#8A918F', steel: '#2A2F30', graphite: '#1B1E1E' };
  var SHEET = { W: 2750, H: 1830, kerf: 4, trim: 10 };
  var NS = 'http://www.w3.org/2000/svg';

  // ---------- estado ----------
  var PRESETS = {
    roupeiro: { name: 'Roupeiro 2 módulos', file: 'ROUPEIRO_2M', L: 1800, A: 2400, P: 580, M: 2, N: 4, E: 18, doors: true, plinth: true },
    base: { name: 'Base de cozinha', file: 'COZINHA_BASE_80', L: 800, A: 720, P: 560, M: 1, N: 1, E: 18, doors: true, plinth: true },
    aereo: { name: 'Módulo aéreo', file: 'COZINHA_AEREO_90', L: 900, A: 700, P: 330, M: 1, N: 2, E: 16, doors: true, plinth: false },
    estante: { name: 'Estante aberta', file: 'ESTANTE_120', L: 1200, A: 1800, P: 320, M: 2, N: 5, E: 18, doors: false, plinth: true },
    tv: { name: 'Móvel de TV', file: 'MOVEL_TV_200', L: 2000, A: 500, P: 420, M: 3, N: 0, E: 19, doors: true, plinth: true },
    sapateira: { name: 'Sapateira', file: 'SAPATEIRA_90', L: 900, A: 1100, P: 350, M: 1, N: 6, E: 16, doors: true, plinth: true }
  };
  var state = Object.assign({}, PRESETS.roupeiro);
  var activeSheet = 0;

  // ---------- geometria ----------
  // projecção dimétrica: frente dominante, profundidade a subir para a direita
  function pr(x, y, z) { return [x * 0.94 + y * 0.62, x * 0.24 - y * 0.40 - z]; }

  function compute(s) {
    var E = s.E, L = s.L, A = s.A, P = s.P, M = s.M, N = s.N;
    var R = s.plinth ? 80 : 0;
    var w = (L - 2 * E - (M - 1) * E) / M;           // vão interior de cada módulo
    var hin = A - R - 2 * E;                            // altura interior
    var dpm = s.doors ? (w > 600 ? 2 : 1) : 0;         // portas por módulo
    var nd = M * dpm;
    var parts = [
      { code: 'LAT', name: 'Lateral', q: 2, c: A, l: P, orla: A },
      { code: 'TPO', name: 'Tampo', q: 1, c: L - 2 * E, l: P, orla: L - 2 * E },
      { code: 'BAS', name: 'Base', q: 1, c: L - 2 * E, l: P, orla: L - 2 * E }
    ];
    if (M > 1) parts.push({ code: 'DIV', name: 'Divisória', q: M - 1, c: hin, l: P - 2, orla: hin });
    if (N > 0) parts.push({ code: 'PRT', name: 'Prateleira', q: M * N, c: Math.round(w - 2), l: P - 22, orla: Math.round(w - 2) });
    if (R) parts.push({ code: 'ROD', name: 'Rodapé', q: 1, c: L - 2 * E, l: R, orla: L - 2 * E });
    if (nd) {
      var dw = Math.round(L / nd - 3), dh = A - R - 3;
      parts.push({ code: 'POR', name: 'Porta', q: nd, c: dh, l: dw, orla: 2 * (dw + dh) });
    }
    parts.forEach(function (p) { p.c = Math.round(p.c); p.l = Math.round(p.l); });
    var fundo = { code: 'FUN', name: 'Fundo HDF 3 mm', q: 1, c: Math.round(A - R - 4), l: Math.round(L - 4), orla: 0, aux: true };
    var orla = parts.reduce(function (t, p) { return t + p.q * p.orla; }, 0) / 1000;
    var nest = pack(parts);
    var pecas = parts.reduce(function (t, p) { return t + p.q; }, 0) + 1;
    return { R: R, w: w, dpm: dpm, parts: parts, fundo: fundo, orla: orla, nest: nest, pecas: pecas };
  }

  // nesting MaxRects (encostado à esquerda), rotação livre, espessura de serra e refilo
  function pack(parts) {
    var k = SHEET.kerf, W = SHEET.W - 2 * SHEET.trim + k, H = SHEET.H - 2 * SHEET.trim + k;
    var items = [];
    parts.forEach(function (p) {
      for (var i = 0; i < p.q; i++) items.push({ code: p.code, idx: i + 1, w: p.c + k, h: p.l + k });
    });
    items.sort(function (x, y) { return (y.w * y.h - x.w * x.h) || (Math.max(y.w, y.h) - Math.max(x.w, x.h)); });
    var sheets = [];
    function newSheet() { var s = { free: [{ x: 0, y: 0, w: W, h: H }], parts: [] }; sheets.push(s); return s; }
    function fit(free, w, h) {
      var best = null;
      free.forEach(function (f) {
        [[w, h], [h, w]].forEach(function (o) {
          if (o[0] <= f.w && o[1] <= f.h) {
            // encosta à esquerda: menor aresta direita, depois mais acima, depois melhor encaixe
            var right = f.x + o[0], ss = Math.min(f.w - o[0], f.h - o[1]);
            if (!best || right < best.right || (right === best.right && (f.y < best.y || (f.y === best.y && ss < best.ss))))
              best = { x: f.x, y: f.y, w: o[0], h: o[1], right: right, ss: ss };
          }
        });
      });
      return best;
    }
    function place(sh, r) {
      var out = [];
      sh.free.forEach(function (f) {
        if (r.x >= f.x + f.w || r.x + r.w <= f.x || r.y >= f.y + f.h || r.y + r.h <= f.y) { out.push(f); return; }
        if (r.x > f.x) out.push({ x: f.x, y: f.y, w: r.x - f.x, h: f.h });
        if (r.x + r.w < f.x + f.w) out.push({ x: r.x + r.w, y: f.y, w: f.x + f.w - r.x - r.w, h: f.h });
        if (r.y > f.y) out.push({ x: f.x, y: f.y, w: f.w, h: r.y - f.y });
        if (r.y + r.h < f.y + f.h) out.push({ x: f.x, y: r.y + r.h, w: f.w, h: f.y + f.h - r.y - r.h });
      });
      sh.free = out.filter(function (a, i) {
        return !out.some(function (b, j) {
          return i !== j && a.x >= b.x && a.y >= b.y && a.x + a.w <= b.x + b.w && a.y + a.h <= b.y + b.h && (j < i || a.w !== b.w || a.h !== b.h || a.x !== b.x || a.y !== b.y);
        });
      });
    }
    items.forEach(function (it) {
      var spot = null, sh = null;
      for (var i = 0; i < sheets.length && !spot; i++) { spot = fit(sheets[i].free, it.w, it.h); sh = sheets[i]; }
      if (!spot) { sh = newSheet(); spot = fit(sh.free, it.w, it.h); }
      if (!spot) return; // peça maior que a chapa: fica fora do plano
      place(sh, spot);
      sh.parts.push({ code: it.code, idx: it.idx, x: spot.x, y: spot.y, w: spot.w - k, h: spot.h - k });
    });
    var area = 0, SW = SHEET.W, SH = SHEET.H, t = SHEET.trim;
    sheets.forEach(function (s) { s.area = s.parts.reduce(function (a, p) { return a + p.w * p.h; }, 0); area += s.area; });
    // a última chapa só conta até onde foi cortada; o resto é sobra reutilizável
    var consumed = sheets.length * SW * SH;
    var last = sheets[sheets.length - 1];
    if (last && last.parts.length) {
      var ex = t + Math.max.apply(null, last.parts.map(function (p) { return p.x + p.w; })) + k;
      var ey = t + Math.max.apply(null, last.parts.map(function (p) { return p.y + p.h; })) + k;
      var sx = (SW - ex) * SH, sy = (SH - ey) * SW;
      if (sx >= sy && SW - ex >= 300) last.sobra = { x: ex, y: 0, w: SW - ex, h: SH };
      else if (SH - ey >= 300) last.sobra = { x: 0, y: ey, w: SW, h: SH - ey };
      if (last.sobra) consumed -= last.sobra.w * last.sobra.h;
    }
    return { sheets: sheets, yield: area / consumed };
  }

  // ---------- desenho isométrico ----------
  function drawCabinet(s, r, opt) {
    opt = opt || {};
    var dims = opt.dims !== false;
    var L = s.L, A = s.A, P = s.P, E = s.E, R = r.R;
    var out = [];
    var pts = [];
    function P2(x, y, z) { var q = pr(x, y, z); pts.push(q); return q; }
    function line(a, b, col, sw, dash) {
      var p = P2(a[0], a[1], a[2]), q = P2(b[0], b[1], b[2]);
      out.push('<line x1="' + p[0].toFixed(1) + '" y1="' + p[1].toFixed(1) + '" x2="' + q[0].toFixed(1) + '" y2="' + q[1].toFixed(1) +
        '" stroke="' + col + '" stroke-width="' + sw + '"' + (dash ? ' stroke-dasharray="' + dash + '"' : '') + ' vector-effect="non-scaling-stroke"/>');
    }
    function poly(list, fill, stroke, sw) {
      var d = list.map(function (v) { var q = P2(v[0], v[1], v[2]); return q[0].toFixed(1) + ',' + q[1].toFixed(1); }).join(' ');
      out.push('<polygon points="' + d + '" fill="' + fill + '"' + (stroke ? ' stroke="' + stroke + '" stroke-width="' + sw + '" vector-effect="non-scaling-stroke"' : '') + '/>');
    }
    var main = opt.main || C.blue, sub = opt.sub || C.ash;
    // faces visíveis com leve preenchimento
    poly([[0, 0, A], [L, 0, A], [L, P, A], [0, P, A]], 'rgba(58,160,255,.06)');
    poly([[L, 0, 0], [L, P, 0], [L, P, A], [L, 0, A]], 'rgba(58,160,255,.11)');
    // arestas ocultas
    line([0, P, 0], [0, P, A], sub, 0.8, '3 4');
    line([0, P, 0], [L, P, 0], sub, 0.8, '3 4');
    line([0, 0, 0], [0, P, 0], sub, 0.8, '3 4');
    // interior visto de frente
    var inner = s.doors ? sub : main, innerW = s.doors ? 0.7 : 1.1, innerD = s.doors ? '3 4' : null;
    line([E, 0, R], [E, 0, A - E], inner, innerW, innerD);
    line([L - E, 0, R], [L - E, 0, A - E], inner, innerW, innerD);
    line([E, 0, A - E], [L - E, 0, A - E], inner, innerW, innerD);
    line([E, 0, R + E], [L - E, 0, R + E], inner, innerW, innerD);
    if (R) line([0, 0, R], [L, 0, R], main, 1.1);
    var x0 = E;
    for (var m = 0; m < s.M; m++) {
      var xa = x0, xb = x0 + r.w;
      for (var n = 1; n <= s.N; n++) {
        var z = R + E + n * (A - R - 2 * E) / (s.N + 1);
        line([xa, 0, z], [xb, 0, z], s.doors ? sub : C.bone, s.doors ? 0.6 : 0.9, s.doors ? '2 4' : null);
        if (!s.doors) line([xa, 0, z], [xa, P * 0.85, z], sub, 0.5, '2 4');
      }
      if (m < s.M - 1) {
        line([xb, 0, R + E], [xb, 0, A - E], inner, innerW, innerD);
        line([xb + E, 0, R + E], [xb + E, 0, A - E], inner, innerW, innerD);
      }
      x0 = xb + E;
    }
    // portas
    if (s.doors) {
      var nd = s.M * r.dpm, dw = L / nd;
      for (var d = 0; d < nd; d++) {
        var a = d * dw + 1.5, b = (d + 1) * dw - 1.5, zb = R + 1.5, zt = A - 1.5;
        poly([[a, -1, zb], [b, -1, zb], [b, -1, zt], [a, -1, zt]], 'rgba(58,160,255,.07)', main, 1.1);
        // puxador quadrado no lado de abertura
        var hx = (d % 2 === 0 && nd > 1) ? b - 40 : a + 40;
        if (nd === 1) hx = b - 40;
        var hz = A > 1200 ? R + (A - R) * 0.5 : zt - 60;
        var c = pr(hx, -1, hz), sz = Math.max(18, Math.min(L, A) * 0.022);
        out.push('<rect x="' + (c[0] - sz / 2).toFixed(1) + '" y="' + (c[1] - sz / 2).toFixed(1) + '" width="' + sz.toFixed(1) + '" height="' + sz.toFixed(1) + '" fill="' + main + '"/>');
      }
    }
    // caixa exterior visível
    var ext = [[[0, 0, 0], [L, 0, 0]], [[L, 0, 0], [L, 0, A]], [[L, 0, A], [0, 0, A]], [[0, 0, A], [0, 0, 0]],
      [[0, 0, A], [0, P, A]], [[L, 0, A], [L, P, A]], [[0, P, A], [L, P, A]], [[L, P, A], [L, P, 0]], [[L, 0, 0], [L, P, 0]]];
    ext.forEach(function (e) { line(e[0], e[1], main, 1.6); });

    // cotas
    var span = Math.max(L * 0.94 + P * 0.62, A + L * 0.24 + P * 0.4);
    var fs = span * 0.032, tk = fs * 0.36;
    if (dims) {
      var off = fs * 2.2;
      dimLine(pr(0, 0, 0), pr(L, 0, 0), 0, off, 'L ' + L);
      var a1 = pr(0, 0, 0), a2 = pr(0, 0, A);
      dimLine(a1, a2, -off, 0, 'A ' + A, true);
      dimLine(pr(L, 0, 0), pr(L, P, 0), off * 0.7, off * 0.7, 'P ' + P);
    }
    function dimLine(p, q, ox, oy, txt, vertical) {
      var x1 = p[0] + ox, y1 = p[1] + oy, x2 = q[0] + ox, y2 = q[1] + oy;
      pts.push([x1, y1], [x2, y2]);
      out.push('<line x1="' + x1.toFixed(1) + '" y1="' + y1.toFixed(1) + '" x2="' + x2.toFixed(1) + '" y2="' + y2.toFixed(1) + '" stroke="' + C.bone + '" stroke-width="0.8" vector-effect="non-scaling-stroke"/>');
      [[x1, y1], [x2, y2]].forEach(function (t) {
        out.push('<rect x="' + (t[0] - tk).toFixed(1) + '" y="' + (t[1] - tk).toFixed(1) + '" width="' + (2 * tk).toFixed(1) + '" height="' + (2 * tk).toFixed(1) + '" fill="' + C.blue + '"/>');
      });
      var mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
      var ang = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
      if (vertical) ang = -90;
      if (ang > 90) ang -= 180; if (ang < -90) ang += 180;
      var dy = -fs * 0.55;
      var tx = mx + (vertical ? dy : 0), ty = my + (vertical ? 0 : dy);
      if (!vertical) { var rad = ang * Math.PI / 180; tx = mx + Math.sin(rad) * fs * 0.55; ty = my - Math.cos(rad) * fs * 0.55; }
      var tw = txt.length * fs * 0.62;
      pts.push([tx - tw / 2, ty - fs], [tx + tw / 2, ty + fs]);
      out.push('<text x="' + tx.toFixed(1) + '" y="' + ty.toFixed(1) + '" fill="' + C.bone + '" font-family="JetBrains Mono, monospace" font-size="' + fs.toFixed(1) +
        '" text-anchor="middle" transform="rotate(' + ang.toFixed(1) + ' ' + tx.toFixed(1) + ' ' + ty.toFixed(1) + ')">' + txt + '</text>');
    }
    var xs = pts.map(function (p) { return p[0]; }), ys = pts.map(function (p) { return p[1]; });
    var minx = Math.min.apply(null, xs), maxx = Math.max.apply(null, xs), miny = Math.min.apply(null, ys), maxy = Math.max.apply(null, ys);
    var pad = span * (opt.pad || 0.04);
    return '<svg xmlns="' + NS + '" viewBox="' + (minx - pad).toFixed(0) + ' ' + (miny - pad).toFixed(0) + ' ' + (maxx - minx + 2 * pad).toFixed(0) + ' ' + (maxy - miny + 2 * pad).toFixed(0) +
      '" preserveAspectRatio="xMidYMid meet">' + out.join('') + '</svg>';
  }

  // ---------- nesting SVG ----------
  function drawSheet(sh, opt) {
    opt = opt || {};
    var W = SHEET.W, H = SHEET.H, t = SHEET.trim;
    var o = ['<rect x="0" y="0" width="' + W + '" height="' + H + '" fill="rgba(238,240,234,.025)" stroke="' + C.ash + '" stroke-width="1" stroke-dasharray="6 5" vector-effect="non-scaling-stroke"/>'];
    sh.parts.forEach(function (p) {
      var x = p.x + t, y = p.y + t;
      o.push('<rect x="' + x + '" y="' + y + '" width="' + p.w + '" height="' + p.h + '" fill="rgba(58,160,255,.13)" stroke="' + C.blue + '" stroke-width="1" vector-effect="non-scaling-stroke"/>');
      if (opt.labels !== false && p.w > 300 && p.h > 140) {
        var fsz = Math.min(46, p.h * 0.28);
        o.push('<text x="' + (x + 22) + '" y="' + (y + 22 + fsz) + '" fill="' + C.blue + '" font-family="JetBrains Mono, monospace" font-size="' + fsz.toFixed(0) + '">' + p.code + '·' + p.idx + '</text>');
        if (p.h > 220 && p.w > 520) o.push('<text x="' + (x + 22) + '" y="' + (y + 30 + fsz * 2.1) + '" fill="' + C.ash + '" font-family="JetBrains Mono, monospace" font-size="' + (fsz * 0.78).toFixed(0) + '">' + p.w + '×' + p.h + '</text>');
      }
    });
    if (sh.sobra) {
      var so = sh.sobra;
      o.push('<defs><pattern id="hatch" width="28" height="28" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="28" stroke="' + C.steel + '" stroke-width="8"/></pattern></defs>');
      o.push('<rect x="' + so.x + '" y="' + so.y + '" width="' + so.w + '" height="' + so.h + '" fill="url(#hatch)"/>');
      var lx = so.x + so.w / 2, ly = so.y + so.h / 2;
      o.push('<text x="' + lx + '" y="' + (ly - 6) + '" fill="' + C.ash + '" font-family="JetBrains Mono, monospace" font-size="44" text-anchor="middle">SOBRA</text>');
      o.push('<text x="' + lx + '" y="' + (ly + 48) + '" fill="' + C.ash + '" font-family="JetBrains Mono, monospace" font-size="38" text-anchor="middle">' + so.w + ' × ' + so.h + '</text>');
    }
    var pct = Math.round(sh.area / ((W * H) - (sh.sobra ? sh.sobra.w * sh.sobra.h : 0)) * 100);
    o.push('<text x="0" y="' + (H + 66) + '" fill="' + C.ash + '" font-family="JetBrains Mono, monospace" font-size="42">' + sh.parts.length + ' peças · ' + pct + '% de aproveitamento</text>');
    o.push('<text x="' + W + '" y="' + (H + 66) + '" fill="' + C.ash + '" font-family="JetBrains Mono, monospace" font-size="42" text-anchor="end">serra ' + SHEET.kerf + ' mm · refilo ' + SHEET.trim + ' mm</text>');
    return '<svg xmlns="' + NS + '" viewBox="-6 -6 ' + (W + 12) + ' ' + (H + 96) + '">' + o.join('') + '</svg>';
  }

  // ---------- UI ----------
  var $ = function (id) { return document.getElementById(id); };
  var inputs = { L: $('pL'), A: $('pA'), P: $('pP'), M: $('pM'), N: $('pN') };
  var units = { L: 'mm', A: 'mm', P: 'mm', M: 'un', N: 'un' };
  var fmt = function (n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ' '); };

  function syncInputs() {
    Object.keys(inputs).forEach(function (k) {
      var el = inputs[k];
      el.value = state[k];
      el.style.setProperty('--p', ((el.value - el.min) / (el.max - el.min) * 100) + '%');
      $('o' + k).innerHTML = fmt(state[k]) + '<small>' + units[k] + '</small>';
    });
    var r = document.querySelector('input[name=pE][value="' + state.E + '"]'); if (r) r.checked = true;
    $('pDoors').checked = state.doors; $('pPlinth').checked = state.plinth;
  }

  function render() {
    var r = compute(state);
    $('drawing').innerHTML = drawCabinet(state, r);
    $('sPecas').textContent = r.pecas;
    $('sChapas').textContent = r.nest.sheets.length;
    $('sAprov').textContent = (r.nest.yield * 100).toFixed(1).replace('.', ',') + '%';
    $('sOrla').textContent = r.orla.toFixed(1).replace('.', ',') + ' m';
    $('appFile').textContent = state.file + '.skp — OptiMOB';
    $('viewTag').textContent = state.file + ' · ' + r.pecas + ' peças';
    $('listMat').textContent = 'MDF ' + state.E + ' mm';
    // lista
    var rows = r.parts.concat([r.fundo]).map(function (p) {
      return '<tr' + (p.aux ? ' class="aux"' : '') + '><td>' + p.code + '</td><td>' + p.name + '</td><td class="r">' + p.q + '</td><td class="r">' + fmt(p.c) + ' × ' + fmt(p.l) +
        '</td><td class="r">' + (p.orla ? (p.q * p.orla / 1000).toFixed(2).replace('.', ',') + ' m' : '—') + '</td></tr>';
    }).join('');
    document.querySelector('#cutList tbody').innerHTML = rows;
    // chapas
    if (activeSheet >= r.nest.sheets.length) activeSheet = 0;
    var tabs = $('sheetTabs');
    tabs.innerHTML = r.nest.sheets.map(function (s, i) {
      return '<button type="button" role="tab" aria-selected="' + (i === activeSheet) + '" data-i="' + i + '">Chapa ' + (i + 1) + '</button>';
    }).join('');
    $('nesting').innerHTML = drawSheet(r.nest.sheets[activeSheet]);
    renderLabels(r);
    current = r;
  }
  var current = null;

  $('sheetTabs').addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    activeSheet = +b.dataset.i; render();
  });

  Object.keys(inputs).forEach(function (k) {
    inputs[k].addEventListener('input', function () {
      state[k] = +this.value;
      if (state.file.indexOf('_CUSTOM') < 0) state.file = state.file.split('_')[0] + '_CUSTOM';
      syncInputs(); render();
    });
  });
  document.querySelectorAll('input[name=pE]').forEach(function (el) {
    el.addEventListener('change', function () { state.E = +this.value; render(); });
  });
  $('pDoors').addEventListener('change', function () { state.doors = this.checked; render(); });
  $('pPlinth').addEventListener('change', function () { state.plinth = this.checked; render(); });
  $('params').addEventListener('submit', function (e) { e.preventDefault(); });

  // ---------- funcionalidades ----------
  var ICONS = {
    blocos: '<rect x="10" y="8" width="28" height="32"/><line x1="10" y1="20" x2="38" y2="20"/><line x1="24" y1="20" x2="24" y2="40"/>',
    param: '<line x1="8" y1="16" x2="40" y2="16"/><rect x="26" y="12" width="8" height="8" data-a/><line x1="8" y1="32" x2="40" y2="32"/><rect x="14" y="28" width="8" height="8"/>',
    nesting: '<rect x="7" y="9" width="34" height="30" stroke-dasharray="3 3"/><rect x="11" y="13" width="12" height="10" data-a/><rect x="26" y="13" width="11" height="22"/><rect x="11" y="26" width="12" height="9"/>',
    orla: '<rect x="10" y="10" width="28" height="28"/><line x1="10" y1="10" x2="38" y2="10" stroke-width="5" data-s/><line x1="38" y1="10" x2="38" y2="38" stroke-width="5" data-s/>',
    orca: '<rect x="11" y="7" width="26" height="34"/><line x1="16" y1="16" x2="32" y2="16"/><line x1="16" y1="23" x2="32" y2="23"/><line x1="16" y1="30" x2="25" y2="30"/><rect x="28" y="28" width="5" height="5" data-a/>',
    cnc: '<rect x="8" y="22" width="32" height="18"/><line x1="24" y1="6" x2="24" y2="28"/><polyline points="17,13 24,6 31,13"/><rect x="21" y="30" width="6" height="6" data-a/>'
  };
  function icon(body) {
    body = body.replace(/data-a/g, 'fill="' + C.blue + '" stroke="' + C.blue + '"').replace(/data-s/g, 'stroke="' + C.blue + '"');
    return '<svg viewBox="0 0 48 48" fill="none" stroke="' + C.bone + '" stroke-width="2.2" stroke-linecap="square" aria-hidden="true">' + body + '</svg>';
  }
  var FEATS = [
    ['blocos', 'Blocos paramétricos', 'Módulos construídos com laterais, tampo, base, divisórias e prateleiras reais. Cada peça sabe a sua espessura e o seu encaixe.'],
    ['param', 'Ajuste por valores', 'Altere largura, altura, profundidade ou número de vãos e o módulo recalcula todas as peças internas de uma vez.'],
    ['nesting', 'Plano de corte', 'Distribui as peças pelas chapas com espessura de serra e margem de refilo, e mostra o aproveitamento de cada chapa.'],
    ['orla', 'Orlas por peça', 'Indica que lados de cada peça levam orla e soma os metros lineares de orla do projeto inteiro.'],
    ['orca', 'Base para orçamento', 'Resume chapas, orla, ferragens e peças num quadro pronto para levar para o orçamento.'],
    ['cnc', 'Saída para a oficina', 'Exporta a lista de corte e as etiquetas de peça para a seccionadora, a CNC ou a impressora.']
  ];
  $('feats').innerHTML = FEATS.map(function (f) {
    return '<article class="feat"><div class="ic">' + icon(ICONS[f[0]]) + '</div><h3>' + f[1] + '</h3><p>' + f[2] + '</p></article>';
  }).join('');

  // ---------- biblioteca ----------
  var libEl = $('lib');
  libEl.innerHTML = Object.keys(PRESETS).map(function (k) {
    var p = PRESETS[k], r = compute(p);
    return '<button type="button" class="lib-card" data-k="' + k + '"><div class="lib-draw">' + drawCabinet(p, r, { dims: false, pad: 0.06 }) + '</div>' +
      '<div class="lib-meta"><div><b>' + p.name + '</b><span class="mono">' + p.L + ' × ' + p.A + ' × ' + p.P + ' · ' + r.pecas + ' peças</span></div><span class="mono lib-go">Abrir →</span></div></button>';
  }).join('');
  libEl.addEventListener('click', function (e) {
    var b = e.target.closest('.lib-card'); if (!b) return;
    state = Object.assign({}, PRESETS[b.dataset.k]); activeSheet = 0;
    syncInputs(); render();
    $('configurador').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  });

  // ---------- etiquetas ----------
  var LOGO_TAG = document.querySelector('.nav-logo svg');
  function qr(seed) {
    var n = 21, o = '', s = seed;
    function rnd() { s = (s * 9301 + 49297) % 233280; return s / 233280; }
    function finder(x, y) { return '<rect x="' + x + '" y="' + y + '" width="7" height="7"/><rect x="' + (x + 1) + '" y="' + (y + 1) + '" width="5" height="5" fill="#F6F7F3"/><rect x="' + (x + 2) + '" y="' + (y + 2) + '" width="3" height="3"/>'; }
    for (var i = 0; i < n; i++) for (var j = 0; j < n; j++) {
      if ((i < 8 && j < 8) || (i < 8 && j > n - 9) || (i > n - 9 && j < 8)) continue;
      if (rnd() < 0.47) o += '<rect x="' + i + '" y="' + j + '" width="1.02" height="1.02"/>';
    }
    return '<svg viewBox="0 0 21 21" fill="#1B1E1E" shape-rendering="crispEdges" aria-hidden="true">' + o + finder(0, 0) + finder(14, 0) + finder(0, 14) + '</svg>';
  }
  function renderLabels(r) {
    var pick = ['LAT', 'PRT', 'POR'], total = r.pecas, out = '', k = 0;
    var map = {}; r.parts.forEach(function (p) { map[p.code] = p; });
    var order = r.parts.map(function (p) { return p.code; });
    pick.filter(function (c) { return map[c]; }).concat(['TPO']).slice(0, 3).forEach(function (code) {
      var p = map[code]; k++;
      var num = 1; for (var i = 0; i < order.indexOf(code); i++) num += r.parts[i].q;
      var logo = LOGO_TAG ? LOGO_TAG.outerHTML.replace(/fill="#[0-9A-Fa-f]{6}"/g, 'fill="#1B1E1E"') : 'OptiMOB';
      out += '<div class="tag"><div class="tag-h"><div class="tl">' + logo + '</div><b>P' + String(num).padStart(2, '0') + ' / ' + total + '</b></div>' +
        '<div class="tag-b"><div class="tag-q">' + qr(num * 7 + p.c) + '</div><div class="tag-d">' +
        '<span>Módulo</span><em>' + state.file + '</em><span>Peça</span><em>' + p.name + '</em><span>Dim.</span><em>' + fmt(p.c) + ' × ' + fmt(p.l) + ' × ' + state.E + '</em>' +
        '<span>Orla</span><em>' + (code === 'POR' ? '▮ ▮ ▮ ▮' : '▮ ▯ ▯ ▯') + '</em></div></div><div class="tag-bar"></div></div>';
    });
    $('labels').innerHTML = out;
  }

  // ---------- lista de espera ----------
  // Para onde vão os registos:
  //  - USE_NETLIFY_FORMS = true -> Netlify Forms (o Netlify recebe o POST para "/").
  //  - FORM_ENDPOINT com URL -> serviço externo, por exemplo Formspree ('https://formspree.io/f/xxxxxxx').
  //    Necessário no GitHub Pages, que não recebe formulários.
  // Na pré-visualização (build.py marca window.OPTIMOB_PREVIEW) não há servidor para receber.
  var FORM_ENDPOINT = '';
  var USE_NETLIFY_FORMS = false;   // true só se o site estiver alojado no Netlify
  var PREVIEW = !!window.OPTIMOB_PREVIEW || location.protocol === 'file:';
  var NO_SERVICE = !FORM_ENDPOINT && !USE_NETLIFY_FORMS;
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  document.querySelectorAll('form.wl').forEach(function (form) {
    var msg = form.querySelector('.wl-msg'), btn = form.querySelector('.wl-btn');
    function say(text, kind) { msg.textContent = text; msg.className = 'wl-msg mono' + (kind ? ' ' + kind : ''); }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var email = form.elements.email, perfil = form.elements.perfil;
      email.removeAttribute('aria-invalid'); perfil.removeAttribute('aria-invalid');
      if (!EMAIL_RE.test(email.value.trim())) { email.setAttribute('aria-invalid', 'true'); email.focus(); say('Escreva um email válido, por exemplo nome@oficina.com.', 'err'); return; }
      if (!perfil.value) { perfil.setAttribute('aria-invalid', 'true'); perfil.focus(); say('Escolha o tipo de trabalho que faz.', 'err'); return; }
      var addr = email.value.trim();
      function done() {
        form.classList.add('ok');
        say(PREVIEW ? 'Pré-visualização: no site publicado, ' + addr + ' entra na lista de espera.' : 'Está na lista. Vamos escrever para ' + addr + ' quando a versão de teste estiver pronta.', 'ok');
        btn.disabled = true;
      }
      if (PREVIEW) { done(); return; }
      if (NO_SERVICE) { say('A inscrição online abre em breve. Até lá, escreva para optimobsystem@gmail.com com o assunto "Lista de espera".'); return; }
      btn.disabled = true; say('A registar…');
      fetch(FORM_ENDPOINT || '/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json' }, body: new URLSearchParams(new FormData(form)).toString() })
        .then(function (r) { if (!r.ok) throw new Error(r.status); done(); })
        .catch(function () { btn.disabled = false; say('Não foi possível registar agora. Tente outra vez ou escreva para optimobsystem@gmail.com.', 'err'); });
    });
  });

  // ---------- hero: módulo a ajustar a largura sozinho ----------
  var heroEl = $('heroDraw');
  if (heroEl) {
    var hs = { L: 1800, A: 2100, P: 560, M: 2, N: 3, E: 18, doors: true, plinth: true, file: 'HERO' };
    var hL = $('hvL'), hP = $('hvP'), hO = $('hvO');
    var drawHero = function (L) {
      hs.L = Math.round(L / 10) * 10;
      hs.M = hs.L >= 1500 ? 2 : 1;
      var r = compute(hs);
      heroEl.innerHTML = drawCabinet(hs, r, { pad: 0.05 });
      hL.textContent = hs.L; hP.textContent = r.pecas; hO.textContent = r.orla.toFixed(1).replace('.', ',');
    };
    var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
    drawHero(1800);
    if (!still) {
      var visible = true, t0 = performance.now(), last = 0;
      if ('IntersectionObserver' in window) new IntersectionObserver(function (en) { visible = en[0].isIntersecting; }).observe(heroEl);
      var tick = function (t) {
        if (visible && t - last > 70) {
          last = t;
          var ph = ((t - t0) / 9000) % 1;                  // ciclo de 9 s
          var e = 0.5 - 0.5 * Math.cos(ph * 2 * Math.PI);  // vai e volta suave
          drawHero(1200 + e * 1200);
        }
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    }
  }

  syncInputs(); render();
})();
