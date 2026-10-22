'use strict';
// Cenario procedural, icones e elementos de interface.

// luzes fixas do cenario por fase (preenchidas ao desenhar o terreno)
A.envLights = {};

const THEMES = {
  oasis: { base: '#e0bf84', light: '#f0d9a6', dark: '#c49d63', edge: '#a87a48', path: '#cfa56e', pathHi: '#dcb784', dunes: 7 },
  canyon: { base: '#cf9462', light: '#e3ae7e', dark: '#a76c42', edge: '#94582f', path: '#d4a273', pathHi: '#e0b488', dunes: 3 },
  ruins: { base: '#d9bd8b', light: '#ead4a6', dark: '#bb9a66', edge: '#9c7a4c', path: '#c9b08a', pathHi: '#d8c29e', dunes: 4, tiles: true },
  dunes: { base: '#e6c68a', light: '#f8e4b4', dark: '#c49c5c', edge: '#b08452', path: '#d6ae74', pathHi: '#e2c08c', dunes: 16, duneA: 1.7, ripples: 260 },
  citadel: { base: '#c6a272', light: '#d8b888', dark: '#98774e', edge: '#7e5e3a', path: '#b9a07c', pathHi: '#c9b28e', dunes: 4, tiles: true },
  storm: { base: '#c99a68', light: '#ddb486', dark: '#9a6a3c', edge: '#86572e', path: '#c9a070', pathHi: '#d8b488', dunes: 6, ripples: 200 },
  qanat: { base: '#d6c58e', light: '#e8dcaa', dark: '#ab9c62', edge: '#8e7a48', path: '#ccb07c', pathHi: '#dac294', dunes: 3 },
  ember: { base: '#8e6c54', light: '#a8846a', dark: '#5e4434', edge: '#4a3426', path: '#a08066', pathHi: '#b29276', dunes: 5, ripples: 120 },
};

// ------------------------------------------------------------ decoracoes
A.deco = {};
A.deco.palm = (c, x, y, s, r) => {
  c.save(); c.translate(x, y); c.scale(s, s);
  A.shadow(c, 14, 2, 26, 7, 0.22);
  const lean = (r() - 0.5) * 16;
  // tronco
  const segs = 7;
  for (let i = 0; i < segs; i++) {
    const k0 = i / segs, k1 = (i + 1) / segs;
    const x0 = lean * k0 * k0, y0 = -k0 * 58, x1 = lean * k1 * k1, y1 = -k1 * 58;
    const w = 6 - k0 * 2;
    A.poly(c, [[x0 - w, y0], [x1 - w + 0.5, y1], [x1 + w - 0.5, y1], [x0 + w, y0]], A.hgrad(c, x0 - w, x0 + w, '#9a7244', 0.25, -0.35), OUT, 1.3);
  }
  const tx = lean, ty = -58;
  const frond = (a, len, col) => {
    const ex = tx + Math.cos(a) * len, ey = ty + Math.sin(a) * len * 0.75 + 10;
    const mx = tx + Math.cos(a) * len * 0.5, my = ty + Math.sin(a) * len * 0.4 - 10;
    const nx = -Math.sin(a) * 7, ny = Math.cos(a) * 7 * 0.6;
    c.beginPath();
    c.moveTo(tx, ty);
    c.quadraticCurveTo(mx + nx, my + ny, ex, ey);
    c.quadraticCurveTo(mx - nx, my - ny, tx, ty);
    c.closePath();
    c.fillStyle = col; c.fill(); c.lineWidth = 1.3; c.strokeStyle = OUT; c.stroke();
    c.beginPath(); c.moveTo(tx, ty); c.quadraticCurveTo(mx, my, ex, ey);
    c.strokeStyle = U.rgba('#1f4a1e', 0.6); c.lineWidth = 1; c.stroke();
  };
  const greens = ['#3f7a35', '#4f8f3e', '#5ea047', '#477f39'];
  const n = 7;
  for (let i = 0; i < n; i++) {
    const a = Math.PI + (i / (n - 1)) * Math.PI + (r() - 0.5) * 0.3;
    if (Math.sin(a) < -0.2) frond(a, 30 + r() * 8, greens[i % 4]);
  }
  for (let i = 0; i < n; i++) {
    const a = (i / (n - 1)) * Math.PI + (r() - 0.5) * 0.3 - 0.1;
    frond(a, 32 + r() * 8, greens[(i + 1) % 4]);
  }
  A.circ(c, tx - 3, ty + 3, 3, '#7a4a22', OUT, 1);
  A.circ(c, tx + 3, ty + 4, 3, '#6b3f1c', OUT, 1);
  c.restore();
};

A.deco.rock = (c, x, y, s, r, col) => {
  col = col || '#a98a68';
  c.save(); c.translate(x, y); c.scale(s, s);
  A.shadow(c, 3, 2, 17, 6, 0.25);
  const pts = [];
  const n = 7;
  for (let i = 0; i < n; i++) {
    const a = Math.PI + (i / (n - 1)) * Math.PI;
    const rr = 11 + r() * 6;
    pts.push([Math.cos(a) * (rr + 3), Math.sin(a) * rr * 0.9]);
  }
  pts.push([15, 3], [-15, 3]);
  A.poly(c, pts, A.hgrad(c, -16, 16, col, 0.3, -0.35), OUT, 1.6);
  A.poly(c, [[-9, -6], [-3, -12], [3, -8], [-4, -3]], U.rgba('#ffffff', 0.2), null);
  c.restore();
};

A.deco.bush = (c, x, y, s, r, dry) => {
  c.save(); c.translate(x, y); c.scale(s, s);
  A.shadow(c, 2, 1, 12, 4, 0.2);
  const col = dry ? '#9a8a4a' : '#5f8f3e';
  for (let i = 0; i < 5; i++) {
    const bx = (i - 2) * 4.5 + (r() - 0.5) * 2, by = -5 - Math.abs(i - 2) * -1.5 - r() * 3;
    A.circ(c, bx, by, 5 + r() * 2, U.shade(col, (r() - 0.5) * 0.3), OUT, 1.1);
  }
  if (!dry) for (let i = 0; i < 3; i++) A.circ(c, (r() - 0.5) * 14, -7 - r() * 5, 1.3, '#c84a3a');
  c.restore();
};

A.deco.drybush = (c, x, y, s, r) => {
  c.save(); c.translate(x, y); c.scale(s, s);
  for (let i = 0; i < 9; i++) {
    const a = -Math.PI / 2 + (r() - 0.5) * 2.2;
    const l = 7 + r() * 9;
    A.line(c, 0, 0, Math.cos(a) * l, Math.sin(a) * l, '#7a5a32', 1.3);
    A.line(c, Math.cos(a) * l * 0.6, Math.sin(a) * l * 0.6, Math.cos(a + 0.6) * l * 0.9, Math.sin(a + 0.6) * l * 0.9, '#7a5a32', 1);
  }
  c.restore();
};

A.deco.tuft = (c, x, y, s, r, col) => {
  c.save(); c.translate(x, y); c.scale(s, s);
  for (let i = 0; i < 6; i++) {
    const a = -Math.PI / 2 + (i - 2.5) * 0.28;
    A.line(c, (i - 2.5) * 1.6, 0, (i - 2.5) * 1.6 + Math.cos(a) * 9, Math.sin(a) * 9, col || '#6f9a3a', 1.6);
  }
  c.restore();
};

A.deco.bones = (c, x, y, s, r) => {
  c.save(); c.translate(x, y); c.scale(s, s);
  A.shadow(c, 0, 1, 16, 5, 0.18);
  for (let i = 0; i < 5; i++) {
    c.beginPath();
    c.arc(-8 + i * 4, -1, 7 - Math.abs(i - 2), Math.PI * 1.05, Math.PI * 1.95);
    c.strokeStyle = OUT; c.lineWidth = 3.6; c.stroke();
    c.strokeStyle = '#efe4c8'; c.lineWidth = 2; c.stroke();
  }
  A.line(c, -12, 0, 10, 0, '#efe4c8', 2.4);
  A.ell(c, 14, -2, 5, 3.5, '#efe4c8', OUT, 1.1);
  A.circ(c, 15.5, -2.5, 1, '#3a2a1a');
  c.restore();
};

A.deco.skull = (c, x, y, s) => {
  c.save(); c.translate(x, y); c.scale(s, s);
  A.ell(c, 0, -3, 7, 5, '#efe4c8', OUT, 1.2);
  A.poly(c, [[-6, -6], [-14, -12], [-9, -5]], '#efe4c8', OUT, 1);
  A.poly(c, [[6, -6], [14, -12], [9, -5]], '#efe4c8', OUT, 1);
  A.circ(c, -2.5, -3.5, 1.4, '#3a2a1a'); A.circ(c, 2.5, -3.5, 1.4, '#3a2a1a');
  c.restore();
};

A.deco.column = (c, x, y, s, r, broken) => {
  c.save(); c.translate(x, y); c.scale(s, s);
  A.shadow(c, 6, 2, 16, 5, 0.25);
  const h = broken ? 22 + r() * 12 : 44;
  A.box(c, 0, 0, 20, 5, 6, '#c7b28c');
  A.cyl(c, 0, -h, -5, 7, 3, '#e3d2ae', { noTop: broken });
  for (let i = -1; i <= 1; i++) A.line(c, i * 3.5, -h + 2, i * 3.5, -6, U.rgba('#8a7552', 0.5), 1);
  if (broken) {
    A.poly(c, [[-7, -h], [-3, -h - 5], [1, -h - 2], [4, -h - 6], [7, -h]], '#d6c39e', OUT, 1.3);
  } else {
    A.box(c, 0, -h, 18, 4, 5, '#c7b28c');
  }
  c.restore();
};

A.deco.fallen = (c, x, y, s, r) => {
  c.save(); c.translate(x, y); c.scale(s, s);
  A.shadow(c, 0, 3, 26, 6, 0.22);
  A.rrect(c, -24, -11, 48, 12, 5, A.hgrad(c, -24, 24, '#e3d2ae', 0.1, -0.3), OUT, 1.4);
  for (let i = 0; i < 3; i++) A.line(c, -20, -8 + i * 3.5, 22, -8 + i * 3.5, U.rgba('#8a7552', 0.45), 1);
  A.ell(c, 24, -5, 4, 6, '#d2bf98', OUT, 1.3);
  A.ell(c, 24, -5, 2, 3, '#bba67e');
  c.restore();
};

A.deco.wall = (c, x, y, s, r, col) => {
  col = col || '#cdb088';
  c.save(); c.translate(x, y); c.scale(s, s);
  A.shadow(c, 4, 2, 30, 7, 0.25);
  const w = 46 + r() * 20, h = 18 + r() * 14;
  const pts = [[-w / 2, 0], [-w / 2, -h]];
  const n = 5;
  for (let i = 1; i < n; i++) pts.push([-w / 2 + (w / n) * i, -h + (r() - 0.3) * 12]);
  pts.push([w / 2, -h * 0.6], [w / 2, 0]);
  A.poly(c, pts, A.hgrad(c, -w / 2, w / 2, col, 0.18, -0.3), OUT, 1.6);
  c.save();
  c.beginPath(); c.moveTo(pts[0][0], pts[0][1]); for (const p of pts) c.lineTo(p[0], p[1]); c.closePath(); c.clip();
  c.strokeStyle = U.rgba('#7a5a32', 0.45); c.lineWidth = 1;
  for (let row = 0; row < 6; row++) {
    const yy = -row * 6;
    c.beginPath(); c.moveTo(-w / 2, yy); c.lineTo(w / 2, yy); c.stroke();
    for (let k = 0; k < 8; k++) { const xx = -w / 2 + k * 9 + (row % 2) * 4.5; c.beginPath(); c.moveTo(xx, yy); c.lineTo(xx, yy - 6); c.stroke(); }
  }
  c.restore();
  c.restore();
};

A.deco.obelisk = (c, x, y, s) => {
  c.save(); c.translate(x, y); c.scale(s, s);
  A.shadow(c, 10, 2, 18, 5, 0.25);
  A.box(c, 0, 0, 22, 5, 7, '#9f8a6a');
  A.poly(c, [[-7, -5], [-5, -60], [5, -60], [7, -5]], A.hgrad(c, -7, 7, '#b39a76', 0.25, -0.35), OUT, 1.5);
  A.poly(c, [[-5, -60], [0, -68], [5, -60]], '#d7a93b', OUT, 1.2);
  for (let i = 0; i < 4; i++) A.line(c, -2.5, -50 + i * 11, 2.5, -50 + i * 11, U.rgba('#5a4428', 0.6), 1.1);
  c.restore();
};

A.deco.jars = (c, x, y, s, r) => {
  c.save(); c.translate(x, y); c.scale(s, s);
  A.shadow(c, 0, 1, 14, 4, 0.2);
  const jar = (jx, jy, js, col) => {
    c.beginPath();
    c.moveTo(jx - 3 * js, jy - 13 * js);
    c.quadraticCurveTo(jx - 9 * js, jy - 8 * js, jx - 5 * js, jy);
    c.lineTo(jx + 5 * js, jy);
    c.quadraticCurveTo(jx + 9 * js, jy - 8 * js, jx + 3 * js, jy - 13 * js);
    c.closePath();
    c.fillStyle = A.hgrad(c, jx - 8, jx + 8, col, 0.3, -0.3); c.fill(); c.lineWidth = 1.2; c.strokeStyle = OUT; c.stroke();
    A.ell(c, jx, jy - 13 * js, 3.4 * js, 1.3 * js, U.shade(col, -0.4), OUT, 1);
  };
  jar(-6, 0, 1.1, '#b8653a');
  jar(6, 1, 0.9, '#c9894a');
  c.restore();
};

A.deco.tent = (c, x, y, s, r) => {
  c.save(); c.translate(x, y); c.scale(s, s);
  A.shadow(c, 4, 2, 28, 8, 0.22);
  A.poly(c, [[-24, 0], [-14, -24], [14, -24], [24, 0]], A.hgrad(c, -24, 24, '#c2563a', 0.25, -0.3), OUT, 1.5);
  A.poly(c, [[-14, -24], [0, -32], [14, -24]], '#d8704a', OUT, 1.4);
  A.poly(c, [[-6, 0], [0, -18], [6, 0]], '#4a2414', OUT, 1.2);
  for (let i = -2; i <= 2; i++) A.line(c, i * 8, 0, i * 5, -24, U.rgba('#efe0c0', 0.5), 1.5);
  c.restore();
};

A.deco.brazier = (c, x, y, s, r, time) => {
  c.save(); c.translate(x, y); c.scale(s, s);
  A.shadow(c, 0, 1, 10, 3.5, 0.25);
  A.line(c, -5, 0, 0, -12, '#3a2a1a', 2); A.line(c, 5, 0, 0, -12, '#3a2a1a', 2);
  A.ell(c, 0, -13, 8, 3.5, '#5a4632', OUT, 1.2);
  c.restore();
};

// lagoa do oasis
A.pond = (c, x, y, rx, ry, r) => {
  A.ell(c, x, y + 4, rx + 10, ry + 7, '#7fa04a');
  A.ell(c, x, y + 2, rx + 6, ry + 4, '#b29a62', OUT, 2);
  const g = c.createRadialGradient(x - rx * 0.2, y - ry * 0.3, 2, x, y, rx);
  g.addColorStop(0, '#6fd0d8');
  g.addColorStop(0.6, '#3aa3b8');
  g.addColorStop(1, '#2a7f9a');
  A.ell(c, x, y, rx, ry, g, OUT, 2);
  c.save();
  c.beginPath(); c.ellipse(x, y, rx, ry, 0, 0, U.TAU); c.clip();
  for (let i = 0; i < 7; i++) {
    const wx = x + (r() - 0.5) * rx * 1.4, wy = y + (r() - 0.5) * ry * 1.2;
    A.line(c, wx - 10, wy, wx + 10, wy, 'rgba(255,255,255,0.45)', 1.6);
  }
  A.ell(c, x - rx * 0.3, y - ry * 0.35, rx * 0.35, ry * 0.18, 'rgba(255,255,255,0.25)');
  c.restore();
  // juncos
  for (let i = 0; i < 9; i++) {
    const a = r() * U.TAU;
    const px = x + Math.cos(a) * (rx + 2), py = y + Math.sin(a) * (ry + 2);
    A.deco.tuft(c, px, py, 1 + r() * 0.4, r, '#4f8a3c');
  }
};

// formacao rochosa grande (canion)
A.cliff = (c, x, y, w, h, r, col) => {
  col = col || '#b8673e';
  A.shadow(c, x + 10, y + 4, w * 0.6, h * 0.18, 0.28);
  const pts = [];
  const n = 9;
  for (let i = 0; i <= n; i++) {
    const k = i / n;
    const px = x - w / 2 + w * k;
    const py = y - h * (0.55 + 0.45 * Math.sin(k * Math.PI)) * (0.75 + r() * 0.35);
    pts.push([px, py]);
  }
  const poly = [[x - w / 2, y], ...pts, [x + w / 2, y]];
  A.poly(c, poly, A.hgrad(c, x - w / 2, x + w / 2, col, 0.22, -0.38), OUT, 2);
  c.save();
  c.beginPath(); c.moveTo(poly[0][0], poly[0][1]); for (const p of poly) c.lineTo(p[0], p[1]); c.closePath(); c.clip();
  for (let i = 1; i < 6; i++) {
    const yy = y - (h / 6) * i;
    c.beginPath(); c.moveTo(x - w / 2, yy + (r() - 0.5) * 6);
    c.quadraticCurveTo(x, yy + (r() - 0.5) * 12, x + w / 2, yy + (r() - 0.5) * 6);
    c.strokeStyle = U.rgba(i % 2 ? '#7a3e22' : '#e8a577', 0.45); c.lineWidth = 2; c.stroke();
  }
  // topo iluminado
  c.beginPath(); c.moveTo(pts[0][0], pts[0][1]);
  for (const p of pts) c.lineTo(p[0], p[1]);
  for (let i = pts.length - 1; i >= 0; i--) c.lineTo(pts[i][0], pts[i][1] + 7);
  c.closePath(); c.fillStyle = U.rgba('#f2b98a', 0.6); c.fill();
  c.restore();
  A.poly(c, poly, null, OUT, 2);
};

// ------------------------------------------------------------ terreno completo
A.terrain = (c, g) => {
  if (A.terrainSprite && A.terrainSprite(c, g)) return; // fundo renderizado no Blender (js/sprites.js)
  const L = g.L;
  // temas novos (fundo do Blender ainda nao pronto): o pintor antigo usa um tema parecido
  const th = THEMES[L.theme] || THEMES[{ encontro: 'oasis', mangue: 'qanat', cheia: 'dunes', tepui: 'canyon' }[L.theme]] || THEMES.oasis;
  const r = U.rng(L.seed * 977 + 13);
  // base
  c.fillStyle = th.base; c.fillRect(0, 0, W, H);
  let grad = c.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, U.rgba(th.light, 0.35));
  grad.addColorStop(1, U.rgba(th.dark, 0.3));
  c.fillStyle = grad; c.fillRect(0, 0, W, H);
  for (let i = 0; i < 320; i++) {
    const x = r() * W, y = r() * H, rr = 20 + r() * 90;
    A.ell(c, x, y, rr, rr * 0.55, U.rgba(r() < 0.5 ? th.light : th.dark, 0.05 + r() * 0.07));
  }
  // dunas (manchas suaves de luz e sombra com uma crista)
  const soft = (x, y, rx, ry, col, a) => {
    c.save();
    c.translate(x, y); c.scale(1, ry / rx);
    const gg = c.createRadialGradient(0, 0, 0, 0, 0, rx);
    gg.addColorStop(0, U.rgba(col, a)); gg.addColorStop(0.55, U.rgba(col, a * 0.55)); gg.addColorStop(1, U.rgba(col, 0));
    c.fillStyle = gg; c.beginPath(); c.arc(0, 0, rx, 0, U.TAU); c.fill();
    c.restore();
  };
  for (let i = 0; i < th.dunes; i++) {
    const x = r() * W, y = r() * H, rx = 150 + r() * 200, ry = 46 + r() * 40;
    const da = th.duneA || 1;
    soft(x + rx * 0.08, y + ry * 0.45, rx, ry, th.dark, 0.34 * da);
    soft(x - rx * 0.1, y - ry * 0.25, rx * 0.8, ry * 0.75, th.light, Math.min(0.9, 0.45 * da));
    const lg = c.createLinearGradient(x - rx * 0.75, 0, x + rx * 0.75, 0);
    lg.addColorStop(0, U.rgba(th.light, 0)); lg.addColorStop(0.5, U.rgba(th.light, 0.75)); lg.addColorStop(1, U.rgba(th.light, 0));
    c.beginPath();
    c.moveTo(x - rx * 0.75, y + ry * 0.15);
    c.quadraticCurveTo(x - rx * 0.1, y - ry * 0.55, x + rx * 0.75, y + ry * 0.1);
    c.strokeStyle = lg; c.lineWidth = 2; c.stroke();
  }
  // ondulacoes de vento
  c.strokeStyle = U.rgba(th.dark, 0.18); c.lineWidth = 1.2;
  for (let i = 0; i < (th.ripples || 90); i++) {
    const x = r() * W, y = r() * H, l = 20 + r() * 40;
    c.beginPath(); c.moveTo(x, y); c.quadraticCurveTo(x + l / 2, y - 4, x + l, y); c.stroke();
  }

  // utilidades de posicionamento
  const pathPts = [];
  for (const p of g.paths) for (let i = 0; i < p.pts.length; i += 2) pathPts.push(p.pts[i]);
  const farPath = (x, y, d) => { const d2 = d * d; for (const p of pathPts) { const dx = p[0] - x, dy = p[1] - y; if (dx * dx + dy * dy < d2) return false; } return true; };
  const farSpot = (x, y, d) => g.spots.every(s => Math.hypot(s.x - x, (s.y - y) * 1.3) > d);
  const placed = [];
  const free = (x, y, d) => placed.every(p => Math.hypot(p[0] - x, p[1] - y) > d);
  const hudFree = (x, y) => !((x < 340 && y < 84) || (x > 1130 && y < 76) || (x < 300 && y > 610));
  // objetos altos nao podem cobrir lotes nem o caminho logo acima deles
  const clearAbove = (x, y, h, w) => {
    for (const s of g.spots) if (Math.abs(s.x - x) < w + 32 && y - s.y > -24 && y - s.y < h + 20) return false;
    for (const p of pathPts) if (Math.abs(p[0] - x) < w + 26 && y - p[1] > 0 && y - p[1] < h + 26) return false;
    return true;
  };
  const tall = { palm: [74, 34], column: [50, 12], obelisk: [70, 12], wall: [36, 34], tent: [34, 26], cliff: [110, 70] };
  const tryPlace = (n, rad, test) => {
    const out = [];
    for (let k = 0; k < n * 25 && out.length < n; k++) {
      const x = 15 + r() * (W - 30), y = 20 + r() * (H - 30);
      if (!farPath(x, y, 42 + rad) || !farSpot(x, y, 44 + rad) || !free(x, y, rad * 1.4) || !hudFree(x, y)) continue;
      if (typeof test === 'function' && !test(x, y)) continue;
      if (typeof test === 'string' && !clearAbove(x, y, tall[test][0], tall[test][1])) continue;
      placed.push([x, y]); out.push([x, y]);
    }
    return out;
  };

  // piso de pedra antigo (ruinas)
  if (th.tiles) {
    for (let i = 0; i < 14; i++) {
      const x = r() * W, y = r() * H;
      const cols = 3 + Math.floor(r() * 4), rows = 2 + Math.floor(r() * 3);
      for (let a = 0; a < cols; a++) for (let b = 0; b < rows; b++) {
        if (r() < 0.3) continue;
        const tx = x + a * 22 + (b % 2) * 11, ty = y + b * 14;
        A.rect(c, tx, ty, 20, 12, U.rgba(L.theme === 'citadel' ? '#8e7a5e' : '#b8a27c', 0.55), U.rgba('#6a5638', 0.35), 1);
      }
    }
  }
  // canais de irrigacao (qanat)
  if (L.canals) for (const cn of L.canals) {
    c.lineJoin = 'round'; c.lineCap = 'round';
    for (const [w, col] of [[26, '#8e7a48'], [20, '#b29a62'], [13, '#3a8fa8'], [6, 'rgba(160,230,240,0.55)']]) {
      c.beginPath(); c.moveTo(cn[0][0], cn[0][1]);
      for (let i = 1; i < cn.length; i++) c.lineTo(cn[i][0], cn[i][1]);
      c.strokeStyle = col; c.lineWidth = w; c.stroke();
    }
    for (const p of cn) placed.push(p);
  }
  // agua
  if (L.water) for (const [x, y, rx, ry] of L.water) { A.pond(c, x, y, rx, ry, r); placed.push([x, y]); }
  // terreno elevado: mesa de pedra sob o lote
  for (const s of g.spots) {
    if (!s.high) continue;
    const rock = L.theme === 'ember' ? '#5a4436' : L.theme === 'storm' || L.theme === 'canyon' ? '#a8643c' : '#b8935e';
    // tamanho proporcional a plataforma do lote (~38 x 22)
    const M = 1.22;
    A.shadow(c, s.x + 6, s.y + 24, 46 * M, 14, 0.3);
    c.beginPath();
    c.moveTo(s.x - 42 * M, s.y + 2);
    c.lineTo(s.x - 38 * M, s.y + 19); c.lineTo(s.x - 20 * M, s.y + 29); c.lineTo(s.x + 4 * M, s.y + 32); c.lineTo(s.x + 26 * M, s.y + 28); c.lineTo(s.x + 40 * M, s.y + 18); c.lineTo(s.x + 42 * M, s.y + 2);
    c.closePath();
    c.fillStyle = A.hgrad(c, s.x - 42 * M, s.x + 42 * M, U.shade(rock, -0.1), 0.15, -0.35); c.fill();
    c.lineWidth = 2; c.strokeStyle = OUT; c.stroke();
    for (let k = 0; k < 3; k++) A.line(c, s.x - 36 * M + k * 4, s.y + 11 + k * 6, s.x + 36 * M - k * 6, s.y + 10 + k * 6, U.rgba(U.shade(rock, -0.5), 0.35), 1.2);
    A.ell(c, s.x, s.y + 1, 42 * M, 25, A.hgrad(c, s.x - 42 * M, s.x + 42 * M, U.shade(rock, 0.2), 0.2, -0.2), OUT, 2);
    placed.push([s.x, s.y]);
  }

  // caminho
  const strokePaths = (w, col) => {
    c.lineJoin = 'round'; c.lineCap = 'round';
    for (const p of g.paths) {
      c.beginPath();
      c.moveTo(p.pts[0][0], p.pts[0][1]);
      for (let i = 1; i < p.pts.length; i++) c.lineTo(p.pts[i][0], p.pts[i][1]);
      c.strokeStyle = col; c.lineWidth = w; c.stroke();
    }
  };
  strokePaths(72, 'rgba(70,40,15,0.18)');
  strokePaths(64, th.edge);
  strokePaths(55, th.path);
  strokePaths(32, U.rgba(th.pathHi, 0.6));
  // sulcos e pedrinhas
  for (const p of g.paths) {
    const tmp = {};
    for (let d = 0; d < p.len; d += 7) {
      const q = p.at(d, tmp);
      for (const side of [-1, 1]) {
        if (r() < 0.55) {
          const off = side * (25 + r() * 5);
          A.ell(c, q.x - q.dy * off, q.y + q.dx * off, 2 + r() * 2.5, 1.4 + r() * 1.5, U.shade(th.edge, -0.15 - r() * 0.2));
        }
      }
      if (r() < 0.12) {
        const off = (r() - 0.5) * 34;
        A.ell(c, q.x - q.dy * off, q.y + q.dx * off, 1.5 + r() * 1.5, 1 + r(), U.rgba(th.edge, 0.7));
      }
    }
    c.save();
    c.setLineDash([16, 10]);
    for (const off of [-10, 10]) {
      c.beginPath();
      for (let d = 0; d < p.len; d += 6) {
        const q = p.at(d, tmp);
        const x = q.x - q.dy * off, y = q.y + q.dx * off;
        if (d === 0) c.moveTo(x, y); else c.lineTo(x, y);
      }
      c.strokeStyle = U.rgba(th.edge, 0.28); c.lineWidth = 2.5; c.stroke();
    }
    c.restore();
  }

  // decoracao por tema
  const draw = [];
  const add = (fn, list) => list.forEach(p => draw.push([p[0], p[1], fn]));
  if (L.theme === 'oasis') {
    if (L.water) for (const [x, y, rx, ry] of L.water) {
      for (let i = 0; i < 6; i++) {
        const a = r() * U.TAU, px = x + Math.cos(a) * (rx + 18 + r() * 20), py = y + Math.sin(a) * (ry + 12 + r() * 14);
        if (farPath(px, py, 50) && farSpot(px, py, 50) && hudFree(px, py) && clearAbove(px, py, 74, 34)) { draw.push([px, py, (cc, xx, yy) => A.deco.palm(cc, xx, yy, 0.8 + r() * 0.35, r)]); placed.push([px, py]); }
      }
    }
    add((cc, x, y) => A.deco.palm(cc, x, y, 0.75 + r() * 0.3, r), tryPlace(9, 26, 'palm'));
    add((cc, x, y) => A.deco.bush(cc, x, y, 0.9 + r() * 0.5, r, false), tryPlace(14, 12));
    add((cc, x, y) => A.deco.rock(cc, x, y, 0.6 + r() * 0.6, r), tryPlace(12, 14));
    add((cc, x, y) => A.deco.tuft(cc, x, y, 1 + r() * 0.5, r), tryPlace(30, 6));
    add((cc, x, y) => A.deco.tent(cc, x, y, 0.9, r), tryPlace(2, 30, 'tent'));
    add((cc, x, y) => A.deco.jars(cc, x, y, 1, r), tryPlace(3, 10));
  } else if (L.theme === 'canyon') {
    const cl = tryPlace(12, 70, 'cliff');
    add((cc, x, y) => A.cliff(cc, x, y, 110 + r() * 70, 70 + r() * 50, r), cl);
    add((cc, x, y) => A.deco.rock(cc, x, y, 0.7 + r() * 0.8, r, '#b0704a'), tryPlace(22, 14));
    add((cc, x, y) => A.deco.drybush(cc, x, y, 0.9 + r() * 0.5, r), tryPlace(20, 8));
    add((cc, x, y) => A.deco.bones(cc, x, y, 1, r), tryPlace(3, 14));
  } else if (L.theme === 'ruins') {
    add((cc, x, y) => A.deco.column(cc, x, y, 1, r, r() < 0.6), tryPlace(12, 16, 'column'));
    add((cc, x, y) => A.deco.fallen(cc, x, y, 0.9 + r() * 0.3, r), tryPlace(6, 26));
    add((cc, x, y) => A.deco.wall(cc, x, y, 0.9, r), tryPlace(6, 36, 'wall'));
    add((cc, x, y) => A.deco.palm(cc, x, y, 0.8 + r() * 0.3, r), tryPlace(6, 26, 'palm'));
    add((cc, x, y) => A.deco.rock(cc, x, y, 0.6 + r() * 0.5, r, '#b59d7a'), tryPlace(12, 12));
    add((cc, x, y) => A.deco.bush(cc, x, y, 0.8 + r() * 0.4, r, r() < 0.5), tryPlace(12, 10));
  } else if (L.theme === 'dunes') {
    add((cc, x, y) => A.deco.bones(cc, x, y, 1 + r() * 0.4, r), tryPlace(6, 16));
    add((cc, x, y) => A.deco.skull(cc, x, y, 1), tryPlace(5, 8));
    add((cc, x, y) => A.deco.drybush(cc, x, y, 0.9 + r() * 0.5, r), tryPlace(26, 8));
    add((cc, x, y) => A.deco.rock(cc, x, y, 0.6 + r() * 0.7, r, '#b89a70'), tryPlace(12, 14));
    add((cc, x, y) => A.deco.palm(cc, x, y, 0.75, r), tryPlace(3, 26, 'palm'));
  } else if (L.theme === 'citadel') {
    add((cc, x, y) => A.deco.wall(cc, x, y, 1, r, '#a8916c'), tryPlace(10, 36, 'wall'));
    add((cc, x, y) => A.deco.obelisk(cc, x, y, 0.9 + r() * 0.3), tryPlace(5, 18, 'obelisk'));
    add((cc, x, y) => A.deco.column(cc, x, y, 0.95, r, true), tryPlace(8, 16, 'column'));
    add((cc, x, y) => A.deco.fallen(cc, x, y, 0.85, r), tryPlace(5, 26));
    add((cc, x, y) => A.deco.bones(cc, x, y, 1, r), tryPlace(6, 14));
    add((cc, x, y) => A.deco.rock(cc, x, y, 0.6 + r() * 0.6, r, '#8e7656'), tryPlace(14, 12));
    // rachaduras no chao
    c.strokeStyle = 'rgba(60,35,15,0.35)'; c.lineWidth = 1.5;
    for (let i = 0; i < 26; i++) {
      let x = r() * W, y = r() * H;
      c.beginPath(); c.moveTo(x, y);
      for (let k = 0; k < 5; k++) { x += (r() - 0.5) * 30; y += (r() - 0.5) * 18; c.lineTo(x, y); }
      c.stroke();
    }
  } else if (L.theme === 'storm') {
    const cl = tryPlace(10, 70, 'cliff');
    add((cc, x, y) => A.cliff(cc, x, y, 100 + r() * 70, 70 + r() * 50, r, '#a8643c'), cl);
    add((cc, x, y) => A.deco.rock(cc, x, y, 0.7 + r() * 0.8, r, '#a8724a'), tryPlace(20, 14));
    add((cc, x, y) => A.deco.drybush(cc, x, y, 0.9 + r() * 0.5, r), tryPlace(18, 8));
    add((cc, x, y) => A.deco.bones(cc, x, y, 1, r), tryPlace(4, 14));
    add((cc, x, y) => A.deco.skull(cc, x, y, 1), tryPlace(3, 8));
  } else if (L.theme === 'qanat') {
    // lavouras
    for (let i = 0; i < 9; i++) {
      const pts = tryPlace(1, 46);
      if (!pts.length) continue;
      const [x, y] = pts[0];
      const w = 60 + r() * 40, h = 30 + r() * 16;
      A.rrect(c, x - w / 2, y - h / 2, w, h, 6, U.rgba('#7a8a3a', 0.45), U.rgba('#5a6a2a', 0.5), 1.5);
      for (let k = 1; k < 5; k++) A.line(c, x - w / 2 + 4, y - h / 2 + (h / 5) * k, x + w / 2 - 4, y - h / 2 + (h / 5) * k, U.rgba('#4f7a2c', 0.55), 2);
    }
    add((cc, x, y) => A.deco.palm(cc, x, y, 0.75 + r() * 0.3, r), tryPlace(8, 26, 'palm'));
    add((cc, x, y) => A.deco.bush(cc, x, y, 0.9 + r() * 0.4, r, false), tryPlace(14, 12));
    add((cc, x, y) => A.deco.wall(cc, x, y, 0.8, r, '#d2b484'), tryPlace(4, 36, 'wall'));
    add((cc, x, y) => A.deco.jars(cc, x, y, 1, r), tryPlace(4, 10));
    add((cc, x, y) => A.deco.tuft(cc, x, y, 1 + r() * 0.5, r), tryPlace(26, 6));
  } else if (L.theme === 'ember') {
    // fendas de lava (viram fontes de luz no js/vfx.js)
    c.lineCap = 'round';
    const env = A.envLights[g.levelIdx] = [];
    for (let i = 0; i < 22; i++) {
      let x = r() * W, y = r() * H;
      if (!farPath(x, y, 40)) continue;
      const pts = [[x, y]];
      for (let k = 0; k < 5; k++) { x += (r() - 0.5) * 36; y += (r() - 0.5) * 20; pts.push([x, y]); }
      env.push([pts[2][0], pts[2][1], '#ff6a1a']);
      for (const [w, col] of [[7, 'rgba(255,90,20,0.18)'], [3, '#ff7a1a'], [1.2, '#ffd27a']]) {
        c.beginPath(); c.moveTo(pts[0][0], pts[0][1]);
        for (const p of pts) c.lineTo(p[0], p[1]);
        c.strokeStyle = col; c.lineWidth = w; c.stroke();
      }
    }
    add((cc, x, y) => A.deco.rock(cc, x, y, 0.7 + r() * 0.8, r, '#3e3236'), tryPlace(22, 14));
    add((cc, x, y) => A.deco.obelisk(cc, x, y, 0.9 + r() * 0.2), tryPlace(4, 18, 'obelisk'));
    add((cc, x, y) => A.deco.bones(cc, x, y, 1, r), tryPlace(6, 14));
    add((cc, x, y) => A.deco.skull(cc, x, y, 1), tryPlace(6, 8));
    add((cc, x, y) => A.deco.drybush(cc, x, y, 0.9, r), tryPlace(10, 8));
  }
  draw.sort((a, b) => a[1] - b[1]);
  for (const [x, y, fn] of draw) fn(c, x, y);

  // marcadores da saida
  for (const p of g.paths) {
    let d = p.len;
    const tmp = {};
    let q = p.at(d, tmp);
    while (d > 0 && (q.x < 24 || q.x > W - 24 || q.y < 30 || q.y > H - 24)) { d -= 4; q = p.at(d, tmp); }
    const nx = -q.dy, ny = q.dx;
    for (const side of [-1, 1]) {
      const px = q.x + nx * side * 42, py = q.y + ny * side * 42;
      A.shadow(c, px, py + 2, 10, 4);
      A.box(c, px, py, 14, 30, 7, '#d6bc8c');
      A.box(c, px, py - 30, 18, 4, 7, '#c7a97a');
      A.banner(c, px, py - 26, 10, 18, TEAL, true);
      A.flag(c, px, py - 41, 18, TEAL, 0);
    }
  }

  // vinheta
  const vg = c.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 1.05);
  vg.addColorStop(0, 'rgba(0,0,0,0)');
  vg.addColorStop(1, 'rgba(60,25,5,0.42)');
  c.fillStyle = vg; c.fillRect(0, 0, W, H);
};

// ------------------------------------------------------------ texto e interface
// Estilo "soft": cartoes creme com sombra difusa, capsulas de vidro cacau, botoes pastel em pilula,
// contornos na propria cor (nada de preto) e texto com contorno leve.
const SOFT = {
  card1: '#fbf1dc', card2: '#f3e2c2', line: '#c99a62', ink: '#5a3a22', inkSoft: '#8a6646', title: '#7a4426',
  glass1: 'rgba(132,86,52,0.94)', glass2: 'rgba(98,62,36,0.95)', glassLine: 'rgba(255,226,180,0.35)',
  gold: '#f2c84a', mint: '#8fd9c4', coral: '#e8826a', textOut: 'rgba(58,34,20,0.82)',
  wood1: '#efcb94', wood2: '#d9a86a', woodLine: '#9a6236', leaf: '#6aa84f', leafD: '#3f7f3a', river: '#2f9a9a',
  flower: ['#f08aa0', '#6aa0e0', '#f2c84a'],
};

// folha (elipse pontuda) e florzinha de cinco petalas, para os cantos de cipo
A.leaf = (c, x, y, len, ang, col) => {
  c.save();
  c.translate(x, y); c.rotate(ang);
  c.beginPath();
  c.moveTo(0, 0);
  c.quadraticCurveTo(len * 0.5, -len * 0.42, len, 0);
  c.quadraticCurveTo(len * 0.5, len * 0.42, 0, 0);
  c.closePath();
  c.fillStyle = col || SOFT.leaf; c.fill();
  c.lineWidth = Math.max(1, len * 0.08); c.strokeStyle = SOFT.leafD; c.stroke();
  c.beginPath(); c.moveTo(len * 0.1, 0); c.lineTo(len * 0.85, 0);
  c.strokeStyle = 'rgba(40,80,30,0.45)'; c.lineWidth = Math.max(0.8, len * 0.05); c.stroke();
  c.restore();
};
A.flower = (c, x, y, r, col) => {
  for (let i = 0; i < 5; i++) {
    const a = i * U.TAU / 5 - Math.PI / 2;
    A.ell(c, x + Math.cos(a) * r * 0.55, y + Math.sin(a) * r * 0.55, r * 0.5, r * 0.36, col, U.shade(col, -0.25), 0.8);
  }
  A.circ(c, x, y, r * 0.32, '#f6d65a', '#c9a032', 0.8);
};
// flor de ipe amarelo (Brasilia): cinco petalas redondas e miolo laranja; rot gira a flor
A.ipe = (c, x, y, r, rot) => {
  const a0 = (rot || 0) - Math.PI / 2;
  c.lineWidth = Math.max(0.8, r * 0.1);
  c.strokeStyle = '#d9961c';
  for (let i = 0; i < 5; i++) {
    const a = a0 + i * U.TAU / 5;
    c.beginPath();
    c.ellipse(x + Math.cos(a) * r * 0.52, y + Math.sin(a) * r * 0.52, r * 0.52, r * 0.42, a, 0, U.TAU);
    c.fillStyle = i % 2 ? '#f7cf3c' : '#fbd94e';
    c.fill(); c.stroke();
  }
  A.circ(c, x, y, r * 0.3, '#e0822b', '#b5601c', Math.max(0.7, r * 0.07));
  A.circ(c, x - r * 0.08, y - r * 0.1, r * 0.1, 'rgba(255,240,190,0.85)');
};
// mao em "L" (Faz o L): indicador para cima, polegar para o lado e o punho da manga vermelha; s = escala
// (s = 1 tem ~30 px de altura), rot gira em volta do centro visual
A.lHand = (c, x, y, s, rot) => {
  const SK = '#f4c38e', SKD = '#c98a58';
  c.save();
  c.translate(x, y);
  if (rot) c.rotate(rot);
  c.scale(s, s);
  c.translate(-4, 1.5);
  // polegar (atras da palma) e indicador
  A.rrect(c, 1, -2.5, 14, 6, 3, SK, OUT, 1.4);
  A.ell(c, 12.6, -0.4, 1.5, 1.6, '#ffe6cc');
  A.rrect(c, -6.8, -17.5, 6, 17, 3, SK, OUT, 1.4);
  A.ell(c, -3.8, -15, 1.7, 1.5, '#ffe6cc');
  // palma com os dedos dobrados
  A.rrect(c, -7, -3, 13.5, 11.5, 4.5, SK, OUT, 1.4);
  c.lineCap = 'round';
  c.strokeStyle = SKD; c.lineWidth = 1.1;
  c.beginPath();
  c.moveTo(-0.5, 0); c.lineTo(4.5, 0);
  c.moveTo(-0.5, 2.8); c.lineTo(4.5, 2.8);
  c.moveTo(-0.5, 5.6); c.lineTo(4, 5.6);
  c.stroke();
  A.ell(c, -4.4, 0.5, 1.4, 3, 'rgba(255,255,255,0.35)');
  // punho da manga vermelha com estrelinha branca
  A.rrect(c, -7.6, 7.5, 14.6, 6.5, 2.5, '#d6282b', '#7a1416', 1.4);
  A.line(c, -6.2, 9.2, 5.6, 9.2, 'rgba(255,255,255,0.3)', 1.2);
  c.beginPath();
  for (let i = 0; i < 10; i++) {
    const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? 0.9 : 2.1;
    if (i) c.lineTo(-0.3 + Math.cos(a) * rr, 10.9 + Math.sin(a) * rr); else c.moveTo(-0.3 + Math.cos(a) * rr, 10.9 + Math.sin(a) * rr);
  }
  c.closePath(); c.fillStyle = '#ffffff'; c.fill();
  c.restore();
};
// canto de cipo: um ramo curvo com folhas (e flor opcional) saindo do canto (sx, sy = direcao para dentro)
A.vine = (c, x, y, sx, sy, s, flowerCol) => {
  c.save();
  c.lineCap = 'round';
  c.beginPath();
  c.moveTo(x - sx * 4 * s, y + sy * 18 * s);
  c.quadraticCurveTo(x - sx * 2 * s, y - sy * 2 * s, x + sx * 26 * s, y - sy * 4 * s);
  // galho de ipe amarelo (Brasilia) no lugar do cipo da mata
  c.strokeStyle = '#7a5538'; c.lineWidth = 3 * s; c.stroke();
  for (const [fx, fy, fr] of [[6, -1, 6], [18, -4, 5], [-3, 12, 4.5], [12, 2, 4]]) {
    A.circ(c, x + sx * fx * s, y - sy * fy * s, fr * s, '#f7cf3c', '#e0a51f', 1);
    A.circ(c, x + sx * fx * s, y - sy * fy * s, fr * 0.35 * s, '#d9822b');
  }
  if (flowerCol) A.flower(c, x + sx * 2 * s, y + sy * 4 * s, 6 * s, flowerCol);
  c.restore();
};

// sombra difusa (o blur do canvas ignora a escala, entao compensa pela transformacao atual)
A.softShadow = (c, x, y, w, h, r, blur, alpha, dy, fill) => {
  const k = c.getTransform ? Math.abs(c.getTransform().a) || 1 : 1;
  c.save();
  c.shadowColor = `rgba(70,40,20,${alpha == null ? 0.28 : alpha})`;
  c.shadowBlur = (blur || 18) * k;
  c.shadowOffsetY = (dy == null ? 6 : dy) * k;
  A.rrect(c, x, y, w, h, r, fill || '#f6e8cf');
  c.restore();
};

A.text = (c, str, x, y, size, color, align, font, stroke, lw) => {
  c.font = `${font && font.weight ? font.weight : '800'} ${size}px ${font && font.family ? font.family : FONT_UI}`;
  c.textAlign = align || 'center';
  c.textBaseline = 'middle';
  if (stroke !== false) {
    c.lineJoin = 'round';
    c.strokeStyle = stroke || SOFT.textOut;
    c.lineWidth = lw || Math.max(2, size * 0.15);
    c.strokeText(str, x, y);
  }
  c.fillStyle = color || '#fff';
  c.fillText(str, x, y);
};

A.wrap = (c, str, maxW, size, weight) => {
  c.font = `${weight || 600} ${size}px ${FONT_UI}`;
  const words = str.split(' ');
  const lines = [];
  let cur = '';
  for (const w of words) {
    const test = cur ? cur + ' ' + w : w;
    if (c.measureText(test).width > maxW && cur) { lines.push(cur); cur = w; } else cur = test;
  }
  if (cur) lines.push(cur);
  return lines;
};

// ---------------------------------------------------------------- interface pintada (sprites/ui)
// pecas geradas no estilo do conceito (arte/conceitos/amazonia/ui.png) e recortadas por tools/sprites/ui_pecas.py;
// enquanto nao carregam (ou se faltarem) vale o desenho por codigo de antes
const SKIN = {};
['painel', 'pilula', 'pilula_dourada', 'pilula_vermelha', 'pilula_teal', 'pilula_creme', 'pilula_cinza', 'botao_verde', 'botao_vermelho',
  'botao_dourado', 'botao_teal', 'botao_creme', 'botao_cinza', 'estrela', 'estrela_vazia', 'barra', 'prancha', 'medalhao', 'logo'].forEach(n => {
  const im = new Image();
  im.src = 'sprites/ui/' + n + '.png';
  SKIN[n] = im;
});
A.skin = n => { const im = SKIN[n]; return im && im.complete && im.naturalWidth ? im : null; };

// imagem esticada num retangulo mantendo as quinas: cs = quina na fonte, k = escala das quinas
A.nine = (c, im, dx, dy, dw, dh, cs, k) => {
  const W = im.naturalWidth, H = im.naturalHeight;
  const cd = Math.min(cs * k, dw / 2, dh / 2);
  const sx = [0, cs, W - cs, W], sy = [0, cs, H - cs, H];
  const tx = [dx, dx + cd, dx + dw - cd, dx + dw], ty = [dy, dy + cd, dy + dh - cd, dy + dh];
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
    const ww = tx[i + 1] - tx[i], hh = ty[j + 1] - ty[j];
    if (ww > 0 && hh > 0) c.drawImage(im, sx[i], sy[j], sx[i + 1] - sx[i], sy[j + 1] - sy[j], tx[i], ty[j], ww + 0.6, hh + 0.6);
  }
};

// faixa esticada so no meio: pontas (cap px da fonte de cada lado) mantem a proporcao, com aperto opcional na largura
A.three = (c, im, dx, dy, dw, dh, cap, squeeze = 1) => {
  const W = im.naturalWidth, H = im.naturalHeight, k = dh / H;
  const cd = Math.min(cap * k * squeeze, dw / 2);
  c.drawImage(im, 0, 0, cap, H, dx, dy, cd + 0.6, dh);
  c.drawImage(im, cap, 0, W - 2 * cap, H, dx + cd, dy, dw - 2 * cd + 0.6, dh);
  c.drawImage(im, W - cap, 0, cap, H, dx + dw - cd, dy, cd, dh);
};

// placa de madeira clara com miolo creme e cantos de cipo (pele "Guardioes da Mata")
A.panel = (c, x, y, w, h, opts = {}) => {
  const r = opts.r || 24;
  A.softShadow(c, x, y, w, h, r, 26, 0.32, 10, SOFT.wood2);
  const pin = A.skin('painel');
  if (pin && opts.skin !== false) {
    // o retangulo pedido e a borda externa da madeira (fonte: 89..1110 x 85..816); folhas e flores passam para fora
    const t = U.clamp(Math.min(w, h) * 0.045, 9, 15), k = t / 84;
    c.save();
    c.imageSmoothingEnabled = true;
    c.imageSmoothingQuality = 'high';
    A.nine(c, pin, x - 89 * k, y - 85 * k, w + 179 * k, h + 162 * k, 300, k);
    c.restore();
    return;
  }
  const g = c.createLinearGradient(0, y, 0, y + h);
  g.addColorStop(0, SOFT.wood1); g.addColorStop(1, SOFT.wood2);
  A.rrect(c, x, y, w, h, r, g, SOFT.woodLine, 2.5);
  // veios da madeira
  c.save();
  c.beginPath(); c.roundRect ? c.roundRect(x, y, w, h, r) : c.rect(x, y, w, h); c.clip();
  c.strokeStyle = 'rgba(130,80,40,0.12)'; c.lineWidth = 1.2;
  for (let k = 0; k < 7; k++) {
    const yy = y + 6 + k * (h - 12) / 6;
    c.beginPath(); c.moveTo(x, yy); c.bezierCurveTo(x + w * 0.3, yy - 3, x + w * 0.7, yy + 3, x + w, yy); c.stroke();
  }
  c.restore();
  const m = opts.m || 10;
  const gi = c.createLinearGradient(0, y + m, 0, y + h - m);
  gi.addColorStop(0, opts.bg1 || SOFT.card1); gi.addColorStop(1, opts.bg2 || '#f6e8cc');
  A.rrect(c, x + m, y + m, w - m * 2, h - m * 2, Math.max(8, r - m), gi, U.rgba(SOFT.woodLine, 0.5), 1.5);
  if (opts.vines !== false) {
    const s = Math.min(1.25, Math.max(0.7, Math.min(w, h) / 320));
    A.vine(c, x + 6, y + 6, 1, -1, s, SOFT.flower[0]);
    A.vine(c, x + w - 6, y + h - 6, -1, 1, s, SOFT.flower[1]);
  }
};

// capsula de madeira escura (HUD, barra de info)
A.darkPanel = (c, x, y, w, h, r) => {
  const pr = A.skin('prancha');
  if (pr) {
    // retangulo = tabua (fonte 75..1020 x 80..232); as pontas com folhas ficam apertadas para o texto cair no sulco
    const k = h / 152, sq = 0.55;
    const ox = x - 75 * k * sq, ow = w + 155 * k * sq;
    A.softShadow(c, x, y, w, h, h / 2, 12, 0.24, 4, SOFT.wood2);
    c.save();
    c.imageSmoothingEnabled = true;
    A.three(c, pr, ox, y - 80 * k, ow, 236 * k, 250, sq);
    c.restore();
    return;
  }
  const rr = Math.min(h / 2, (r || 10) + 5);
  const g = c.createLinearGradient(0, y, 0, y + h);
  g.addColorStop(0, SOFT.glass1); g.addColorStop(1, SOFT.glass2);
  A.softShadow(c, x, y, w, h, rr, 16, 0.26, 5, g);
  A.rrect(c, x, y, w, h, rr, null, '#4e2f1a', 2);
  A.rrect(c, x + 2.5, y + 2.5, w - 5, h - 5, Math.max(4, rr - 2.5), null, SOFT.glassLine, 1.2);
  c.save();
  c.beginPath(); c.roundRect ? c.roundRect(x, y, w, h, rr) : c.rect(x, y, w, h); c.clip();
  c.strokeStyle = 'rgba(40,20,8,0.18)'; c.lineWidth = 1;
  for (let k = 1; k < 4; k++) { const yy = y + k * h / 4; c.beginPath(); c.moveTo(x, yy); c.bezierCurveTo(x + w * 0.4, yy - 2, x + w * 0.6, yy + 2, x + w, yy); c.stroke(); }
  c.restore();
};

const BTN_COLORS = { green: '#6aa84f', gold: '#f2b84a', red: '#e8826a', blue: '#2f9a9a', teal: '#2f9a9a', grey: '#f3e2c2', cream: '#f3e2c2' };

// botao em pilula colorida dentro de um aro de madeira; levanta um pouco no hover
const PILULA = { green: 'pilula', gold: 'pilula_dourada', red: 'pilula_vermelha', blue: 'pilula_teal', teal: 'pilula_teal', grey: 'pilula_creme', cream: 'pilula_creme' };
A.btn = (c, x, y, w, h, label, o = {}) => {
  const key = o.color || 'green';
  let base = BTN_COLORS[key] || key;
  if (o.disabled) base = '#d8cbb8';
  const cream = !o.disabled && (key === 'grey' || key === 'cream');
  const lift = o.hover && !o.disabled ? 2 : 0;
  const r = Math.min(h / 2, 22);
  const yy = y - lift;
  const pil = A.skin(o.disabled ? 'pilula_cinza' : (PILULA[key] || 'pilula'));
  if (pil) {
    // retangulo = moldura de madeira da pilula (fonte 88..850 x 60..339)
    const k = h / 279;
    A.softShadow(c, x, yy, w, h, h / 2, o.hover ? 16 : 10, 0.3, o.hover ? 7 : 4, SOFT.wood2);
    c.save();
    c.imageSmoothingEnabled = true;
    c.imageSmoothingQuality = 'high';
    A.three(c, pil, x - 88 * k, yy - 60 * k, w + 138 * k, 377 * k, 230);
    if (o.hover && !o.disabled) { c.globalCompositeOperation = 'lighter'; c.globalAlpha = 0.12; A.three(c, pil, x - 88 * k, yy - 60 * k, w + 138 * k, 377 * k, 230); }
    c.restore();
    const sz = o.size || Math.min(24, h * 0.42);
    if (label) A.text(c, label, x + w / 2, yy + h / 2 + 1, sz, cream ? SOFT.ink : o.disabled ? '#fbf6ee' : '#ffffff', 'center', o.font,
      cream ? false : U.shade(base, -0.5), Math.max(2, sz * 0.16));
    return;
  }
  // aro de madeira
  const gw = c.createLinearGradient(0, yy, 0, yy + h);
  gw.addColorStop(0, SOFT.wood1); gw.addColorStop(1, SOFT.wood2);
  A.softShadow(c, x, yy, w, h, r, o.hover ? 16 : 10, 0.32, o.hover ? 7 : 4, SOFT.wood2);
  A.rrect(c, x, yy, w, h, r, gw, SOFT.woodLine, 2);
  // miolo colorido
  const ins = Math.max(4, Math.min(6, h * 0.1));
  const g = c.createLinearGradient(0, yy + ins, 0, yy + h - ins);
  g.addColorStop(0, U.shade(base, 0.22 + (o.hover ? 0.08 : 0)));
  g.addColorStop(1, U.shade(base, -0.1));
  A.rrect(c, x + ins, yy + ins, w - ins * 2, h - ins * 2, Math.max(6, r - ins), g, U.shade(base, -0.28), 1.5);
  A.rrect(c, x + ins + 5, yy + ins + 2, w - ins * 2 - 10, (h - ins * 2) * 0.36, Math.max(4, (r - ins) * 0.6), 'rgba(255,255,255,0.26)');
  if (key === 'green' && !o.disabled && w >= 150) {
    A.ipe(c, x + w - 12, yy + 7, 8, 0.3);
    A.ipe(c, x + w - 25, yy + 3, 5.5, -0.4);
    A.flower(c, x + w - 14, yy + h - 8, 5, SOFT.flower[0]);
  }
  const sz = o.size || Math.min(24, h * 0.42);
  if (label) A.text(c, label, x + w / 2, yy + h / 2 + 1, sz, cream ? SOFT.ink : o.disabled ? '#fbf6ee' : '#ffffff', 'center', o.font,
    cream ? false : U.shade(base, -0.45), Math.max(2, sz * 0.14));
};

// botao redondo: aro de madeira com centro colorido e uma folhinha
// cor pedida -> botao pintado mais proximo (verde, coral, dourado, verde-agua ou creme)
const roundSkin = col => {
  const c0 = String(col).toLowerCase();
  if (c0 === '#5fbfb0' || c0 === '#2f9a9a') return 'botao_teal';
  if (c0 === '#f0b25c' || c0 === '#f2b84a' || c0 === '#e8b84a') return 'botao_dourado';
  if (c0 === '#6aa84f' || c0 === '#7cbc5c') return 'botao_verde';
  if (c0 === '#f3e2c2' || c0 === '#fbf1dc') return 'botao_creme';
  return 'botao_vermelho';
};
A.roundBtn = (c, x, y, r, o = {}) => {
  const base = o.disabled ? '#cdbfae' : (o.color || '#e8826a');
  const lift = o.hover && !o.disabled ? 1.5 : 0;
  const yy = y - lift;
  const bt = A.skin(o.disabled ? 'botao_cinza' : roundSkin(base));
  if (bt) {
    // aro externo da madeira com raio 110 em torno de (128, 129.5) na fonte 256x247
    const k = r / 110;
    const kk = c.getTransform ? Math.abs(c.getTransform().a) || 1 : 1;
    c.save();
    c.shadowColor = 'rgba(70,40,20,0.3)';
    c.shadowBlur = (o.hover ? 12 : 8) * kk;
    c.shadowOffsetY = (o.hover ? 4 : 2.5) * kk;
    c.imageSmoothingEnabled = true;
    c.imageSmoothingQuality = 'high';
    c.drawImage(bt, x - 128 * k, yy - 129.5 * k, 256 * k, 247 * k);
    c.restore();
    if (o.hover && !o.disabled) A.circ(c, x, yy, r * 0.62, 'rgba(255,255,255,0.12)');
    return;
  }
  const k = c.getTransform ? Math.abs(c.getTransform().a) || 1 : 1;
  c.save();
  c.shadowColor = 'rgba(70,40,20,0.32)';
  c.shadowBlur = (o.hover ? 14 : 9) * k;
  c.shadowOffsetY = (o.hover ? 5 : 3) * k;
  A.circ(c, x, yy, r, SOFT.wood2);
  c.restore();
  const gw = c.createLinearGradient(0, yy - r, 0, yy + r);
  gw.addColorStop(0, SOFT.wood1); gw.addColorStop(1, SOFT.wood2);
  A.circ(c, x, yy, r, gw, SOFT.woodLine, 1.8);
  const ri = r - Math.max(3.5, r * 0.17);
  const g = c.createLinearGradient(0, yy - ri, 0, yy + ri);
  g.addColorStop(0, U.shade(base, 0.25 + (o.hover ? 0.08 : 0)));
  g.addColorStop(1, U.shade(base, -0.12));
  A.circ(c, x, yy, ri, g, U.shade(base, -0.3), 1.2);
  A.ell(c, x, yy - ri * 0.45, ri * 0.6, ri * 0.28, 'rgba(255,255,255,0.22)');
  if (r >= 20 && o.leaf !== false) A.ipe(c, x - r * 0.7, yy + r * 0.68, r * 0.26, 0.4);
};

// estrela de recompensa pintada: cheia (dourada) ou vazia (madeira); r = raio da ponta
A.starSkin = (c, x, y, r, full) => {
  const im = A.skin(full ? 'estrela' : 'estrela_vazia');
  if (!im) return false;
  const k = (r * 2.25) / im.naturalWidth;
  c.save();
  c.imageSmoothingEnabled = true;
  c.imageSmoothingQuality = 'high';
  c.drawImage(im, x - im.naturalWidth * k / 2, y - im.naturalHeight * k * 0.5, im.naturalWidth * k, im.naturalHeight * k);
  c.restore();
  return true;
};

A.star = (c, x, y, r, fill, stroke) => {
  const pts = [];
  for (let i = 0; i < 10; i++) {
    const a = -Math.PI / 2 + (i / 10) * U.TAU;
    const rr = i % 2 ? r * 0.45 : r;
    pts.push([x + Math.cos(a) * rr, y + Math.sin(a) * rr]);
  }
  A.poly(c, pts, fill || '#ffd54a', stroke === undefined ? U.shade(fill && fill[0] === '#' ? fill : '#ffd54a', -0.32) : stroke, Math.max(1.2, r * 0.1));
  if (fill !== '#5a4a3a' && fill !== 'rgba(0,0,0,0.35)') A.poly(c, [[x, y - r * 0.85], [x + r * 0.28, y - r * 0.15], [x, y]], 'rgba(255,255,255,0.4)', null);
};

A.coin = (c, x, y, r) => {
  A.circ(c, x, y + r * 0.18, r, '#d39a3a');
  A.circ(c, x, y, r, '#f6cd5c', '#c98f2c', Math.max(1, r * 0.12));
  A.circ(c, x, y, r * 0.62, null, '#dca43c', Math.max(1, r * 0.11));
  A.circ(c, x - r * 0.3, y - r * 0.3, r * 0.2, 'rgba(255,255,255,0.7)');
};

A.heart = (c, x, y, r) => {
  c.beginPath();
  c.moveTo(x, y + r * 0.9);
  c.bezierCurveTo(x - r * 1.4, y - r * 0.1, x - r * 0.7, y - r * 1.1, x, y - r * 0.35);
  c.bezierCurveTo(x + r * 0.7, y - r * 1.1, x + r * 1.4, y - r * 0.1, x, y + r * 0.9);
  c.closePath();
  c.fillStyle = A.hgrad(c, x - r, x + r, '#f07a84', 0.3, -0.2); c.fill();
  c.lineWidth = Math.max(1.2, r * 0.12); c.strokeStyle = '#c4505e'; c.stroke();
  A.ell(c, x - r * 0.45, y - r * 0.35, r * 0.22, r * 0.15, 'rgba(255,255,255,0.6)');
};

A.skullIcon = (c, x, y, r, col) => {
  A.circ(c, x, y - r * 0.12, r * 0.8, col || '#f3e9d2', OUT, Math.max(1.3, r * 0.13));
  A.rrect(c, x - r * 0.42, y + r * 0.35, r * 0.84, r * 0.48, r * 0.12, col || '#f3e9d2', OUT, Math.max(1.3, r * 0.13));
  A.circ(c, x - r * 0.3, y - r * 0.1, r * 0.2, '#3a2010');
  A.circ(c, x + r * 0.3, y - r * 0.1, r * 0.2, '#3a2010');
};

A.lock = (c, x, y, r) => {
  c.beginPath(); c.arc(x, y - r * 0.2, r * 0.5, Math.PI, 0);
  c.strokeStyle = OUT; c.lineWidth = r * 0.36; c.stroke();
  c.strokeStyle = '#b8b0a0'; c.lineWidth = r * 0.2; c.stroke();
  A.rrect(c, x - r * 0.7, y - r * 0.2, r * 1.4, r * 1.1, r * 0.2, '#d7a93b', OUT, Math.max(1.2, r * 0.13));
  A.circ(c, x, y + r * 0.3, r * 0.15, '#3a2010');
};

// retrato do heroi: busto renderizado do modelo 3D (tools/blender/retrato_jaci.py); sem a imagem, o desenho antigo
const JACI = new Image();
JACI.src = 'sprites/ui/jaci_retrato.png';
const RETRATOS = { jaci: JACI };
const RETRATO_BG = { jaci: ['#ff8a7a', '#b8322a'], caipora: ['#ffb0c4', '#c8455e'], benzedeira: ['#9be3a8', '#2f8a4a'], boitata: ['#ffe27a', '#3f9a4a'] };
A.heroFace = (c, x, y, r, id = 'jaci') => {
  let im = RETRATOS[id];
  if (!im) { im = RETRATOS[id] = new Image(); im.src = `sprites/ui/retrato_${id}.png`; }
  c.save();
  c.beginPath(); c.arc(x, y, r, 0, U.TAU); c.clip();
  const bg = c.createLinearGradient(0, y - r, 0, y + r);
  const cols = RETRATO_BG[id] || RETRATO_BG.jaci;
  bg.addColorStop(0, cols[0]); bg.addColorStop(1, cols[1]);
  c.fillStyle = bg; c.fillRect(x - r, y - r, r * 2, r * 2);
  if (im.complete && im.naturalWidth) {
    c.imageSmoothingEnabled = true;
    c.imageSmoothingQuality = 'high';
    c.drawImage(im, x - r * 1.08, y - r * 1.02, r * 2.16, r * 2.16);
    c.restore();
    A.circ(c, x, y, r, null, OUT, 2.5);
    return;
  }
  if (id !== 'jaci') {
    // sem retrato ainda: o sprite do heroi parado, de frente
    const H = DATA.HEROES[id], sk = H && H.sprite;
    if (sk && typeof USPR !== 'undefined' && USPR.has(sk)) {
      if (USPR.ready(sk)) {
        const S = UNIDADES_META.sets[sk], f = (S.e || S.r)[0];
        const k = USPR.den(f), fh = f[4] / k, sc = (r * 2.6) / fh;
        c.translate(x, y + r * 1.25);
        c.scale(sc, sc);
        USPR.draw(c, f);
      }
    }
    c.restore();
    A.circ(c, x, y, r, null, OUT, 2.5);
    return;
  }
  const s = r / 30;
  c.translate(x, y + 4 * s);
  c.scale(s, s);
  // cabelo atras
  A.poly(c, [[-14, -18], [-30, 0], [-24, 12], [-12, -2]], '#22150f', OUT, 2);
  // pescoco / ombros
  A.ell(c, 0, 34, 30, 16, '#1f8f8a', OUT, 2);
  A.ell(c, -20, 30, 9, 6, '#e8c25a', OUT, 1.6);
  A.ell(c, 20, 30, 9, 6, '#e8c25a', OUT, 1.6);
  A.rect(c, -6, 6, 12, 14, '#b9804f', OUT, 1.6);
  // rosto
  A.ell(c, 0, -6, 17, 20, '#c98d5c', OUT, 2);
  // cabelo frente
  c.beginPath();
  c.moveTo(-18, -2); c.quadraticCurveTo(-20, -30, 2, -28); c.quadraticCurveTo(20, -27, 18, -6);
  c.quadraticCurveTo(10, -20, -4, -18); c.quadraticCurveTo(-12, -14, -18, -2);
  c.closePath(); c.fillStyle = '#22150f'; c.fill(); c.lineWidth = 2; c.strokeStyle = OUT; c.stroke();
  A.line(c, -17, -14, 17, -16, '#e8c25a', 3);
  // olhos
  A.ell(c, -6.5, -4, 3, 2.2, '#fff', OUT, 1);
  A.ell(c, 6.5, -4, 3, 2.2, '#fff', OUT, 1);
  A.circ(c, -6, -4, 1.4, '#1a5a56'); A.circ(c, 7, -4, 1.4, '#1a5a56');
  A.line(c, -10, -9, -3, -8.5, '#22150f', 1.8); A.line(c, 3, -8.5, 10, -9, '#22150f', 1.8);
  A.line(c, -3, 7, 3, 7, '#8a4a32', 1.6);
  A.line(c, 0, -2, -1.2, 3, '#a8704a', 1.2);
  // lenco
  A.poly(c, [[-14, 14], [14, 14], [10, 22], [-10, 22]], '#16706c', OUT, 1.6);
  c.restore();
  A.circ(c, x, y, r, null, OUT, 2.5);
};

// icones
A.icon = (c, name, x, y, r, o = {}) => {
  if (A.iconSprite && A.iconSprite(c, name, x, y, r, o)) return; // icones 3D (js/sprites.js)
  c.save();
  switch (name) {
    case 'upgrade': {
      const g = c.createLinearGradient(0, y - r, 0, y + r);
      g.addColorStop(0, '#8fe35a'); g.addColorStop(1, '#3f8a2a');
      A.poly(c, [[x, y - r * 0.8], [x + r * 0.7, y], [x + r * 0.28, y], [x + r * 0.28, y + r * 0.75], [x - r * 0.28, y + r * 0.75], [x - r * 0.28, y], [x - r * 0.7, y]], g, OUT, 2);
      break;
    }
    case 'sell': A.coin(c, x, y, r * 0.6); A.text(c, '$', x, y + 1, r * 0.7, '#8a5a10', 'center', null, false); break;
    case 'rally': A.flag(c, x - r * 0.25, y + r * 0.7, r * 1.4, TEAL, 0, { w: r * 0.9, h: r * 0.6 }); break;
    case 'heart': A.heart(c, x, y, r * 0.7); break;
    case 'charm': {
      // Engajamento / Delacao: balao de "curtida" rosa com coracao branco
      const br = r * 0.72, by = y - r * 0.06;
      A.poly(c, [[x - br * 0.55, by + br * 0.62], [x - br * 0.85, by + br * 1.18], [x - br * 0.05, by + br * 0.86]], '#ff4f74', OUT, 1.5);
      A.circ(c, x, by, br, '#ff4f74', OUT, 1.6);
      A.poly(c, [[x - br * 0.53, by + br * 0.66], [x - br * 0.72, by + br * 1.0], [x - br * 0.12, by + br * 0.8]], '#ff4f74', null);
      A.ell(c, x - br * 0.35, by - br * 0.5, br * 0.32, br * 0.18, 'rgba(255,255,255,0.35)');
      const hr = br * 0.52, hy = by + br * 0.04;
      c.beginPath();
      c.moveTo(x, hy + hr * 0.9);
      c.bezierCurveTo(x - hr * 1.4, hy - hr * 0.1, x - hr * 0.7, hy - hr * 1.1, x, hy - hr * 0.35);
      c.bezierCurveTo(x + hr * 0.7, hy - hr * 1.1, x + hr * 1.4, hy - hr * 0.1, x, hy + hr * 0.9);
      c.closePath(); c.fillStyle = '#ffffff'; c.fill();
      break;
    }
    case 'coin': A.coin(c, x, y, r * 0.7); break;
    case 'skull': A.skullIcon(c, x, y, r * 0.7); break;
    case 'star': A.star(c, x, y, r * 0.8); break;
    case 'lock': A.lock(c, x, y, r * 0.7); break;
    case 'pause':
      A.rrect(c, x - r * 0.45, y - r * 0.5, r * 0.3, r, 2, '#fff', OUT, 1.5);
      A.rrect(c, x + r * 0.15, y - r * 0.5, r * 0.3, r, 2, '#fff', OUT, 1.5);
      break;
    case 'play': A.poly(c, [[x - r * 0.35, y - r * 0.5], [x + r * 0.5, y], [x - r * 0.35, y + r * 0.5]], '#fff', OUT, 1.5); break;
    case 'speed1': case 'speed2': {
      const n = name === 'speed2' ? 2 : 1;
      for (let i = 0; i < n; i++) {
        const ox = (i - (n - 1) / 2) * r * 0.55;
        A.poly(c, [[x + ox - r * 0.3, y - r * 0.45], [x + ox + r * 0.3, y], [x + ox - r * 0.3, y + r * 0.45]], '#fff', OUT, 1.5);
      }
      break;
    }
    case 'music': {
      A.line(c, x - r * 0.15, y + r * 0.35, x - r * 0.15, y - r * 0.5, OUT, 4);
      A.line(c, x - r * 0.15, y - r * 0.5, x + r * 0.4, y - r * 0.3, OUT, 4);
      A.line(c, x - r * 0.15, y + r * 0.35, x - r * 0.15, y - r * 0.5, '#fff', 2);
      A.line(c, x - r * 0.15, y - r * 0.5, x + r * 0.4, y - r * 0.3, '#fff', 2);
      A.ell(c, x - r * 0.32, y + r * 0.38, r * 0.22, r * 0.17, '#fff', OUT, 1.5);
      if (o.off) A.line(c, x - r * 0.6, y - r * 0.6, x + r * 0.6, y + r * 0.6, '#e04848', 3.5);
      break;
    }
    case 'sfx': {
      A.poly(c, [[x - r * 0.55, y - r * 0.2], [x - r * 0.25, y - r * 0.2], [x + r * 0.1, y - r * 0.5], [x + r * 0.1, y + r * 0.5], [x - r * 0.25, y + r * 0.2], [x - r * 0.55, y + r * 0.2]], '#fff', OUT, 1.5);
      if (!o.off) {
        c.beginPath(); c.arc(x + r * 0.15, y, r * 0.35, -0.8, 0.8); c.strokeStyle = '#fff'; c.lineWidth = 2; c.stroke();
        c.beginPath(); c.arc(x + r * 0.15, y, r * 0.6, -0.8, 0.8); c.stroke();
      } else A.line(c, x - r * 0.6, y - r * 0.6, x + r * 0.6, y + r * 0.6, '#e04848', 3.5);
      break;
    }
    case 'fury': {
      A.ell(c, x, y - r * 0.35, r * 0.7, r * 0.32, '#5a6a8a', OUT, 1.5);
      A.ell(c, x - r * 0.3, y - r * 0.45, r * 0.35, r * 0.25, '#7a8aaa');
      A.poly(c, [[x + r * 0.05, y - r * 0.15], [x - r * 0.3, y + r * 0.3], [x - r * 0.02, y + r * 0.3], [x - r * 0.2, y + r * 0.8], [x + r * 0.35, y + r * 0.15], [x + r * 0.05, y + r * 0.15], [x + r * 0.25, y - r * 0.15]], '#ffe45a', OUT, 1.5);
      break;
    }
    case 'riders': {
      c.translate(x - r * 0.1, y + r * 0.55); c.scale(r / 30, r / 30);
      A.unit.rider(c, { moving: false, atkAnim: 0, walk: 0 }, 0);
      break;
    }
    case 'hero': A.heroFace(c, x, y, r); break;
    case 'explosive':
      A.glow(c, x + r * 0.2, y, r * 0.8, '#ff9a3a', 0.8);
      A.line(c, x - r * 0.7, y + r * 0.2, x + r * 0.3, y - r * 0.1, '#6b4423', 4);
      A.poly(c, [[x + r * 0.25, y - r * 0.3], [x + r * 0.7, y - r * 0.2], [x + r * 0.35, y + r * 0.15]], '#d9dde0', OUT, 1.2);
      break;
    case 'eagle':
      A.ell(c, x, y, r * 0.75, r * 0.45, '#fff8e0', OUT, 2);
      A.circ(c, x, y, r * 0.32, '#d79a2a', OUT, 1.5);
      A.circ(c, x, y, r * 0.14, '#1a0d08');
      break;
    case 'cloud':
      for (const [dx, dy, rr] of [[-0.3, 0.1, 0.4], [0.15, -0.15, 0.45], [0.4, 0.15, 0.35]]) A.circ(c, x + dx * r, y + dy * r, rr * r, '#7fd04a', OUT, 1.4);
      A.circ(c, x - r * 0.1, y - r * 0.15, r * 0.12, 'rgba(255,255,255,0.6)');
      break;
    case 'corrosive':
      c.beginPath(); c.moveTo(x, y - r * 0.7); c.quadraticCurveTo(x + r * 0.6, y + r * 0.1, x, y + r * 0.6); c.quadraticCurveTo(x - r * 0.6, y + r * 0.1, x, y - r * 0.7);
      c.fillStyle = '#7fd04a'; c.fill(); c.lineWidth = 2; c.strokeStyle = OUT; c.stroke();
      A.circ(c, x - r * 0.15, y + r * 0.05, r * 0.12, 'rgba(255,255,255,0.6)');
      break;
    case 'overload': case 'storm':
      if (name === 'storm') A.ell(c, x, y - r * 0.4, r * 0.7, r * 0.3, '#6a7a9a', OUT, 1.5);
      A.poly(c, [[x + r * 0.1, y - r * 0.6], [x - r * 0.35, y + r * 0.1], [x, y + r * 0.1], [x - r * 0.15, y + r * 0.7], [x + r * 0.4, y - r * 0.1], [x + r * 0.05, y - r * 0.1], [x + r * 0.3, y - r * 0.6]], '#9ff0ff', OUT, 1.5);
      break;
    case 'flash':
      A.glow(c, x, y, r, '#fff4a0', 0.9);
      A.star(c, x, y, r * 0.6, '#fff8c0');
      break;
    case 'burn': case 'barrel':
      if (name === 'barrel') { A.rrect(c, x - r * 0.4, y - r * 0.1, r * 0.8, r * 0.75, 4, '#8a5a2e', OUT, 1.5); }
      c.beginPath(); c.moveTo(x, y - r * 0.75); c.quadraticCurveTo(x + r * 0.6, y - r * 0.1, x + r * 0.25, y + r * 0.35);
      c.quadraticCurveTo(x, y + r * 0.1, x - r * 0.25, y + r * 0.35); c.quadraticCurveTo(x - r * 0.6, y - r * 0.1, x, y - r * 0.75);
      c.fillStyle = '#ff8a2a'; c.fill(); c.lineWidth = 1.8; c.strokeStyle = OUT; c.stroke();
      A.ell(c, x, y + r * 0.05, r * 0.15, r * 0.25, '#ffe45a');
      break;
    case 'cluster':
      for (const [dx, dy] of [[-0.35, 0.2], [0.35, 0.2], [0, -0.3]]) A.circ(c, x + dx * r, y + dy * r, r * 0.3, '#3a3532', OUT, 1.4);
      break;
    case 'tremor':
      c.strokeStyle = OUT; c.lineWidth = 3;
      c.beginPath(); c.moveTo(x - r * 0.7, y); c.lineTo(x - r * 0.3, y - r * 0.3); c.lineTo(x, y + r * 0.2); c.lineTo(x + r * 0.3, y - r * 0.2); c.lineTo(x + r * 0.7, y + r * 0.1); c.stroke();
      c.strokeStyle = '#ffb35a'; c.lineWidth = 1.5; c.stroke();
      break;
    case 'chasm':
      A.ell(c, x, y + r * 0.1, r * 0.75, r * 0.4, '#1a0d05', OUT, 2);
      A.ell(c, x, y + r * 0.1, r * 0.45, r * 0.2, '#ff6a2a');
      break;
    case 'charge':
      A.line(c, x - r * 0.7, y + r * 0.5, x + r * 0.4, y - r * 0.4, '#7a5230', 3.5);
      A.poly(c, [[x + r * 0.25, y - r * 0.55], [x + r * 0.75, y - r * 0.75], [x + r * 0.55, y - r * 0.25]], '#e3e7ea', OUT, 1.4);
      break;
    case 'shield':
      A.poly(c, [[x - r * 0.55, y - r * 0.6], [x + r * 0.55, y - r * 0.6], [x + r * 0.5, y + r * 0.1], [x, y + r * 0.7], [x - r * 0.5, y + r * 0.1]], A.hgrad(c, x - r * 0.55, x + r * 0.55, '#d79a3a', 0.35, -0.3), OUT, 2);
      A.circ(c, x, y - r * 0.05, r * 0.18, '#f6e2a0', OUT, 1.2);
      break;
    case 'heal':
      A.rect(c, x - r * 0.18, y - r * 0.6, r * 0.36, r * 1.2, '#6fe06a', OUT, 1.6);
      A.rect(c, x - r * 0.6, y - r * 0.18, r * 1.2, r * 0.36, '#6fe06a', null);
      A.line(c, x - r * 0.6, y - r * 0.18, x - r * 0.6, y + r * 0.18, OUT, 1.6);
      A.line(c, x + r * 0.6, y - r * 0.18, x + r * 0.6, y + r * 0.18, OUT, 1.6);
      break;
    case 'palm':
      A.ell(c, x, y + r * 0.1, r * 0.4, r * 0.5, '#e8b88a', OUT, 2);
      for (let i = 0; i < 4; i++) A.rrect(c, x - r * 0.38 + i * r * 0.2, y - r * 0.75, r * 0.17, r * 0.5, 3, '#e8b88a', OUT, 1.2);
      A.circ(c, x, y + r * 0.1, r * 0.75, null, '#ffd27a', 2);
      break;
    case 'whirl':
      for (let i = 0; i < 3; i++) { c.beginPath(); c.arc(x, y, r * (0.25 + i * 0.2), i, i + 4.2); c.strokeStyle = i === 2 ? '#e8ecef' : '#bfe8e4'; c.lineWidth = 2.5; c.stroke(); }
      break;
    case 'hawk':
      // Faz o L: a mao em L com o punho vermelho
      A.lHand(c, x, y, r / 17, -0.12);
      break;
    default:
      if (A.iconExtra && A.iconExtra[name]) {
        A.iconExtra[name](c, x, y, r, o);
      } else if (DATA.TOWERS[name] || DATA.SPECS[name]) {
        const spec = DATA.SPECS[name];
        const type = spec ? spec.base : name;
        const fake = { type, tier: o.tier || (spec ? 4 : 1), spec: spec ? name : null, x: 0, y: 0, anim: 0, aimX: 1, buildT: 1, id: 1, abil: {}, units: [] };
        c.translate(x, y + r * 0.62);
        const sc = r / 46;
        c.scale(sc, sc);
        A.tower[type](c, fake, o.time || 0);
      } else if (typeof ESPR !== 'undefined' && ESPR.has(name) && ESPR.ready(name)) {
        // inimigo em sprite (js/inimigos.js): primeiro quadro andando (de frente meio de lado), centralizado no circulo
        const SE = INIMIGOS_META.sets[ESPR.key(name)], f = (SE.e || SE.r)[0];
        const k = ESPR.den(f), fw = f[3] / k, fh = f[4] / k;
        const sc = Math.min((r * 2.15) / fh, (r * 2.5) / fw);
        c.translate(x, y);
        c.scale(sc, sc);
        c.translate(f[5] / k - fw / 2, f[6] / k - fh / 2);
        ESPR.draw(c, f, false);
      } else if (A.enemy[name]) {
        const T = DATA.ENEMIES[name];
        const bossFly = T.flying && T.boss;
        const sc = bossFly ? r / 62 : r / (T.size * (T.flying ? 3.3 : 2.3) + 6);
        c.translate(x, y + r * (bossFly ? 0.62 : T.flying ? 0.95 : 0.55));
        c.scale(sc, sc);
        const fake = { type: name, id: 3, moving: false, walk: 0, atkAnim: 0, castAnim: 0, facing: 1, burrowed: false, flying: !!T.flying && !bossFly, e: 0, revealed: true };
        if (name === 'worm') { A.wormIcon(c); } else A.enemy[name](c, fake, o.time || 0.3);
      }
  }
  c.restore();
};

A.wormIcon = (c) => {
  for (let i = 4; i >= 1; i--) A.circ(c, -i * 12, -10 - i * 2, 10 + (4 - i) * 2, i % 2 ? '#9a6a48' : '#b07d55', OUT, 1.8);
  A.circ(c, 6, -24, 24, A.hgrad(c, -18, 30, '#b9875c', 0.3, -0.35), OUT, 2.2);
  A.ell(c, 12, -24, 13, 11, '#3a0e0e', OUT, 2);
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * U.TAU;
    A.circ(c, 12 + Math.cos(a) * 10, -24 + Math.sin(a) * 8, 2, '#f3ead2');
  }
};
