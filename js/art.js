'use strict';
// Arte procedural: primitivas, personagens, inimigos. Tudo desenhado com Canvas 2D.

const OUT = '#2b1a0f';
const FONT_UI = '"Avenir Next", "Avenir", "Trebuchet MS", sans-serif';
const FONT_TITLE = '"Rockwell", "Rockwell Nova", "American Typewriter", "Georgia", serif';
const FONT_HEAD = '"Copperplate", "Rockwell", "Georgia", serif';

const A = {};

// ------------------------------------------------------------ primitivas
A.ell = (c, x, y, rx, ry, fill, stroke, lw) => {
  c.beginPath();
  c.ellipse(x, y, Math.max(0.01, rx), Math.max(0.01, ry), 0, 0, U.TAU);
  if (fill) { c.fillStyle = fill; c.fill(); }
  if (stroke) { c.lineWidth = lw || 2; c.strokeStyle = stroke; c.stroke(); }
};
A.circ = (c, x, y, r, fill, stroke, lw) => A.ell(c, x, y, r, r, fill, stroke, lw);
A.poly = (c, pts, fill, stroke, lw) => {
  c.beginPath();
  c.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) c.lineTo(pts[i][0], pts[i][1]);
  c.closePath();
  if (fill) { c.fillStyle = fill; c.fill(); }
  if (stroke) { c.lineWidth = lw || 2; c.strokeStyle = stroke; c.lineJoin = 'round'; c.stroke(); }
};
A.rect = (c, x, y, w, h, fill, stroke, lw) => {
  if (fill) { c.fillStyle = fill; c.fillRect(x, y, w, h); }
  if (stroke) { c.lineWidth = lw || 2; c.strokeStyle = stroke; c.strokeRect(x, y, w, h); }
};
A.rrect = (c, x, y, w, h, r, fill, stroke, lw) => {
  c.beginPath();
  r = Math.min(r, w / 2, h / 2);
  c.moveTo(x + r, y);
  c.arcTo(x + w, y, x + w, y + h, r);
  c.arcTo(x + w, y + h, x, y + h, r);
  c.arcTo(x, y + h, x, y, r);
  c.arcTo(x, y, x + w, y, r);
  c.closePath();
  if (fill) { c.fillStyle = fill; c.fill(); }
  if (stroke) { c.lineWidth = lw || 2; c.strokeStyle = stroke; c.stroke(); }
};
A.line = (c, x1, y1, x2, y2, color, lw, cap) => {
  c.beginPath();
  c.moveTo(x1, y1); c.lineTo(x2, y2);
  c.strokeStyle = color; c.lineWidth = lw || 2; c.lineCap = cap || 'round';
  c.stroke();
};
A.shadow = (c, x, y, rx, ry, a) => A.ell(c, x, y, rx, ry, `rgba(45,22,6,${a == null ? 0.3 : a})`);
A.hgrad = (c, x0, x1, base, hi, lo) => {
  const g = c.createLinearGradient(x0, 0, x1, 0);
  g.addColorStop(0, U.shade(base, hi == null ? 0.28 : hi));
  g.addColorStop(0.42, base);
  g.addColorStop(1, U.shade(base, lo == null ? -0.38 : lo));
  return g;
};
A.glow = (c, x, y, r, color, a) => {
  const g = c.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, U.rgba(color, a == null ? 0.8 : a));
  g.addColorStop(1, U.rgba(color, 0));
  c.fillStyle = g;
  c.beginPath(); c.arc(x, y, r, 0, U.TAU); c.fill();
};

// cilindro em perspectiva (corpo de torre)
A.cyl = (c, x, yTop, yBot, rx, ry, base, opts = {}) => {
  c.beginPath();
  c.moveTo(x - rx, yTop);
  c.lineTo(x - rx, yBot);
  c.ellipse(x, yBot, rx, ry, 0, Math.PI, 0, true);
  c.lineTo(x + rx, yTop);
  c.ellipse(x, yTop, rx, ry, 0, 0, Math.PI, true);
  c.closePath();
  c.fillStyle = A.hgrad(c, x - rx, x + rx, base);
  c.fill();
  if (opts.bricks) {
    c.save();
    c.clip();
    c.strokeStyle = U.rgba(U.shade(base, -0.5), 0.45);
    c.lineWidth = 1.2;
    const rows = Math.max(1, Math.round((yBot - yTop) / (opts.bricks)));
    const hgt = (yBot - yTop) / rows;
    for (let i = 1; i <= rows; i++) {
      const yy = yTop + i * hgt;
      c.beginPath(); c.ellipse(x, yy, rx, ry, 0, 0, Math.PI); c.stroke();
      const n = Math.max(3, Math.round(rx / 7));
      for (let k = 0; k < n; k++) {
        const a = ((k + (i % 2) * 0.5 + 0.5) / n) * Math.PI;
        const bx = x + Math.cos(a) * rx;
        const by = yy + Math.sin(a) * ry;
        A.line(c, bx, by - hgt, bx, by, U.rgba(U.shade(base, -0.5), 0.4), 1.1, 'butt');
      }
    }
    c.restore();
  }
  c.lineWidth = opts.lw || 2; c.strokeStyle = OUT; c.lineJoin = 'round';
  c.beginPath();
  c.moveTo(x - rx, yTop); c.lineTo(x - rx, yBot);
  c.ellipse(x, yBot, rx, ry, 0, Math.PI, 0, true);
  c.lineTo(x + rx, yTop);
  c.stroke();
  if (opts.noTop) return;
  A.ell(c, x, yTop, rx, ry, opts.top || U.shade(base, 0.12), OUT, opts.lw || 2);
};

// ameias ao redor do topo de um cilindro
A.merlons = (c, x, y, rx, ry, color, n, h) => {
  n = n || 7; h = h || 6;
  const items = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * U.TAU + 0.2;
    items.push({ a, sx: Math.cos(a), sy: Math.sin(a) });
  }
  items.sort((p, q) => p.sy - q.sy);
  for (const it of items) {
    const mx = x + it.sx * rx * 0.92, my = y + it.sy * ry * 0.92;
    const w = 6.5 * (0.6 + 0.4 * Math.abs(it.sy) + 0.2);
    const col = it.sy > 0 ? U.shade(color, it.sx < 0 ? 0.08 : -0.18) : U.shade(color, -0.32);
    A.rect(c, mx - w / 2, my - h, w, h, col, OUT, 1.4);
    A.rect(c, mx - w / 2, my - h - 1.5, w, 2.5, U.shade(color, 0.2), null);
  }
};

// cone (telhado)
A.cone = (c, x, yBase, rx, ry, h, base) => {
  c.beginPath();
  c.moveTo(x - rx, yBase);
  c.ellipse(x, yBase, rx, ry, 0, Math.PI, 0, true);
  c.lineTo(x, yBase - h);
  c.closePath();
  c.fillStyle = A.hgrad(c, x - rx, x + rx, base, 0.3, -0.45);
  c.fill();
  c.lineWidth = 2; c.strokeStyle = OUT; c.lineJoin = 'round'; c.stroke();
};

// caixa em vista 3/4 (frente + topo)
A.box = (c, x, y, w, h, d, base, opts = {}) => {
  const x0 = x - w / 2;
  A.rect(c, x0, y - h, w, h, opts.front || A.hgrad(c, x0, x0 + w, base, 0.12, -0.3), null);
  A.rect(c, x0, y - h - d, w, d, opts.top || U.shade(base, 0.2), null);
  c.lineWidth = 2; c.strokeStyle = OUT; c.lineJoin = 'round';
  c.strokeRect(x0, y - h - d, w, h + d);
  A.line(c, x0, y - h, x0 + w, y - h, OUT, 1.5);
};

A.flag = (c, x, y, h, color, t, opts = {}) => {
  A.line(c, x, y, x, y - h, '#5b3a1e', 2.2);
  const wv = Math.sin(t * 4 + x) * 2.2;
  const fw = opts.w || 14, fh = opts.h || 9;
  c.beginPath();
  c.moveTo(x, y - h);
  c.quadraticCurveTo(x + fw * 0.5, y - h - 2 + wv, x + fw, y - h + 1 + wv * 0.6);
  c.lineTo(x + fw - 3, y - h + fh * 0.5 + wv * 0.5);
  c.lineTo(x + fw, y - h + fh + wv * 0.4);
  c.quadraticCurveTo(x + fw * 0.5, y - h + fh - 2 + wv, x, y - h + fh);
  c.closePath();
  c.fillStyle = color; c.fill();
  c.lineWidth = 1.3; c.strokeStyle = OUT; c.stroke();
  A.circ(c, x, y - h - 1, 1.8, '#e8c25a', OUT, 1);
};

A.banner = (c, x, y, w, h, color, emblem) => {
  c.beginPath();
  c.moveTo(x - w / 2, y);
  c.lineTo(x + w / 2, y);
  c.lineTo(x + w / 2, y + h);
  c.lineTo(x, y + h - 5);
  c.lineTo(x - w / 2, y + h);
  c.closePath();
  c.fillStyle = A.hgrad(c, x - w / 2, x + w / 2, color, 0.2, -0.3);
  c.fill();
  c.lineWidth = 1.5; c.strokeStyle = OUT; c.stroke();
  A.line(c, x - w / 2 - 2, y, x + w / 2 + 2, y, '#6b4423', 2.5);
  if (emblem === 'sun') {
    A.circ(c, x, y + h * 0.42, w * 0.18, '#f2c94c', null);
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * U.TAU;
      A.line(c, x + Math.cos(a) * w * 0.22, y + h * 0.42 + Math.sin(a) * w * 0.22, x + Math.cos(a) * w * 0.32, y + h * 0.42 + Math.sin(a) * w * 0.32, '#f2c94c', 1.2);
    }
  } else if (emblem) {
    // duna estilizada (brasao do bastiao)
    c.beginPath();
    c.moveTo(x - w * 0.3, y + h * 0.55);
    c.quadraticCurveTo(x - w * 0.05, y + h * 0.18, x + w * 0.3, y + h * 0.55);
    c.closePath();
    c.fillStyle = '#f2c94c'; c.fill();
    A.circ(c, x + w * 0.12, y + h * 0.25, w * 0.09, '#f2c94c', null);
  }
};

// ------------------------------------------------------------ humanoides
const HEADS = {};

function limb(c, x1, y1, x2, y2, col, w) {
  c.lineCap = 'round';
  c.strokeStyle = OUT; c.lineWidth = w + 2.2;
  c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke();
  c.strokeStyle = col; c.lineWidth = w;
  c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke();
}

function weaponDraw(c, kind, col) {
  // desenha na origem = mao, apontando para +x
  switch (kind) {
    case 'dagger':
      A.poly(c, [[0, -1.2], [9, -0.6], [11, 0], [9, 0.8], [0, 1.2]], '#d9dde0', OUT, 1);
      A.line(c, 0, -2.5, 0, 2.5, '#6b4423', 2);
      break;
    case 'sword':
      A.poly(c, [[1, -1.3], [14, -1], [17, 0], [14, 1], [1, 1.3]], '#e3e7ea', OUT, 1.1);
      A.line(c, 1, -3.4, 1, 3.4, col || '#c9a24a', 2.2);
      A.line(c, -2, 0, 0, 0, '#5b3a1e', 2.4);
      break;
    case 'scimitar':
      c.beginPath();
      c.moveTo(1, -1.5);
      c.quadraticCurveTo(10, -3.5, 17, -0.5);
      c.quadraticCurveTo(10, 2.5, 1, 1.5);
      c.closePath();
      c.fillStyle = '#e8ecef'; c.fill();
      c.lineWidth = 1.1; c.strokeStyle = OUT; c.stroke();
      A.line(c, 1, -3.5, 1, 3.5, col || '#d7a93b', 2.2);
      break;
    case 'spear':
      A.line(c, -10, 0, 20, 0, '#7a5230', 2.2);
      A.poly(c, [[19, -2.4], [27, 0], [19, 2.4]], '#e3e7ea', OUT, 1);
      if (col) A.line(c, 17, -2.5, 17, 2.5, col, 1.6);
      break;
    case 'staff':
      A.line(c, 0, 12, 0, -20, '#6b4423', 2.4);
      break;
    case 'blowgun':
      A.line(c, -3, 0, 15, -1, '#9b7a3a', 2.6);
      break;
    case 'axe':
      A.line(c, -2, 0, 16, 0, '#6b4423', 2.6);
      c.beginPath();
      c.moveTo(12, -1); c.quadraticCurveTo(15, -9, 21, -7); c.quadraticCurveTo(19, 0, 21, 7); c.quadraticCurveTo(15, 9, 12, 1);
      c.closePath(); c.fillStyle = col || '#c58a3a'; c.fill(); c.lineWidth = 1.2; c.strokeStyle = OUT; c.stroke();
      break;
  }
}

// personagem generico, pes na origem, olhando para a direita
A.humanoid = (c, o) => {
  const moving = o.moving;
  const w = moving ? Math.sin(o.walk || 0) : 0;
  const bob = moving ? Math.abs(Math.cos(o.walk || 0)) * 1.3 : 0;
  const skin = o.skin || '#c98d5c';
  const body = o.body || '#b07a44';
  const legs = o.legs || '#5d3d22';
  const wide = o.wide || 1;
  c.save();
  if (o.s) c.scale(o.s, o.s);
  // pernas
  limb(c, -2.4 * wide, -8, -2.4 * wide - w * 3, -0.5, legs, 3.4 * wide);
  limb(c, 2.4 * wide, -8, 2.4 * wide + w * 3, -0.5, legs, 3.4 * wide);
  if (o.boots) {
    A.ell(c, -2.4 * wide - w * 3 + 0.8, -0.5, 2.6, 1.6, o.boots, OUT, 1);
    A.ell(c, 2.4 * wide + w * 3 + 0.8, -0.5, 2.6, 1.6, o.boots, OUT, 1);
  }
  c.translate(0, -bob);
  // capa
  if (o.cape) {
    const fl = moving ? Math.sin((o.walk || 0) * 0.5) * 1.5 : 0;
    A.poly(c, [[-4 * wide, -18], [-10 * wide - fl, -3], [-2, -5], [4 * wide, -17]], o.cape, OUT, 1.4);
  }
  // braco de tras
  const atk = o.atk || 0;
  limb(c, -3.5 * wide, -15.5, -6 * wide, -9.5 + w * 1.5, U.shade(body, -0.15), 2.8 * wide);
  // escudo (lado de tras, mas visivel)
  if (o.shield) {
    A.ell(c, -5.5 * wide, -12, 4.8 * wide, 6.5, A.hgrad(c, -10, -1, o.shield, 0.3, -0.3), OUT, 1.5);
    A.circ(c, -5.5 * wide, -12, 1.4, '#e8c25a', OUT, 0.8);
  }
  // tronco
  c.beginPath();
  c.moveTo(-5 * wide, -18.5);
  c.quadraticCurveTo(0, -20, 5 * wide, -18.5);
  c.lineTo(6.6 * wide, -6.5);
  c.quadraticCurveTo(0, -4.5, -6.6 * wide, -6.5);
  c.closePath();
  c.fillStyle = A.hgrad(c, -7 * wide, 7 * wide, body, 0.25, -0.3);
  c.fill();
  c.lineWidth = 1.5; c.strokeStyle = OUT; c.stroke();
  if (o.belt) A.line(c, -6.2 * wide, -9.5, 6.2 * wide, -9.5, o.belt, 2);
  if (o.chest) A.poly(c, [[-4.5 * wide, -18], [4.5 * wide, -18], [5 * wide, -11], [-5 * wide, -11]], o.chest, OUT, 1.1);
  if (o.pauldron) {
    A.ell(c, 4.6 * wide, -17.2, 3.4, 2.4, o.pauldron, OUT, 1);
    A.ell(c, -4.6 * wide, -17.2, 3.4, 2.4, U.shade(o.pauldron, -0.2), OUT, 1);
  }
  // cabeca
  const hx = 0.6, hy = -23.5, hr = o.headR || 6;
  if (o.hair === 'tail') {
    const sw = moving ? Math.sin((o.walk || 0) * 0.5) * 1.5 : 0;
    A.poly(c, [[hx - 3, hy - 4], [hx - 11 - sw, hy + 3], [hx - 8 - sw, hy + 6], [hx - 2, hy]], '#2a1a14', OUT, 1);
  }
  A.circ(c, hx, hy, hr, skin, OUT, 1.5);
  // olhos
  if (o.eyes !== false) {
    A.circ(c, hx + 2.6, hy - 0.2, 0.95, o.eyeColor || '#20140c');
  }
  const head = o.head;
  if (head === 'turban') {
    c.beginPath();
    c.ellipse(hx - 0.4, hy - 3, hr + 1, hr * 0.72, 0, Math.PI * 0.95, Math.PI * 2.05);
    c.closePath();
    c.fillStyle = o.headColor || '#e9dcc0'; c.fill(); c.lineWidth = 1.4; c.strokeStyle = OUT; c.stroke();
    A.line(c, hx - hr, hy - 2.6, hx + hr, hy - 3.6, U.shade(o.headColor || '#e9dcc0', -0.25), 1.2);
    if (o.mask) A.poly(c, [[hx - 1, hy + 0.5], [hx + hr + 0.5, hy + 0.5], [hx + hr - 1, hy + 4.5], [hx + 1, hy + 5.5]], o.mask, OUT, 1);
  } else if (head === 'hood') {
    c.beginPath();
    c.moveTo(hx - hr - 1, hy + 4);
    c.quadraticCurveTo(hx - hr - 2, hy - hr - 3, hx + 1, hy - hr - 2);
    c.quadraticCurveTo(hx + hr + 2, hy - hr, hx + hr + 1, hy - 1);
    c.lineTo(hx + 2.5, hy - 2.4);
    c.quadraticCurveTo(hx, hy + 1, hx - 1.5, hy + 5);
    c.closePath();
    c.fillStyle = o.headColor || '#3d5b3a'; c.fill(); c.lineWidth = 1.4; c.strokeStyle = OUT; c.stroke();
  } else if (head === 'helmet') {
    c.beginPath();
    c.ellipse(hx, hy - 1, hr + 0.8, hr + 0.6, 0, Math.PI, Math.PI * 2);
    c.closePath();
    c.fillStyle = A.hgrad(c, hx - hr, hx + hr, o.headColor || '#a9b0b5', 0.35, -0.3); c.fill();
    c.lineWidth = 1.4; c.strokeStyle = OUT; c.stroke();
    A.line(c, hx - hr - 0.8, hy - 1, hx + hr + 0.8, hy - 1, U.shade(o.headColor || '#a9b0b5', -0.3), 1.6);
    if (o.plume) {
      c.beginPath();
      c.moveTo(hx - 1, hy - hr);
      c.quadraticCurveTo(hx - 7, hy - hr - 7, hx - 10, hy - hr + 1);
      c.quadraticCurveTo(hx - 5, hy - hr - 2, hx + 1, hy - hr + 1);
      c.closePath();
      c.fillStyle = o.plume; c.fill(); c.lineWidth = 1; c.strokeStyle = OUT; c.stroke();
    }
    if (o.horns) {
      A.poly(c, [[hx - hr + 1, hy - 3], [hx - hr - 5, hy - hr - 5], [hx - hr + 3, hy - 5]], '#efe2c4', OUT, 1);
      A.poly(c, [[hx + hr - 1, hy - 3], [hx + hr + 5, hy - hr - 5], [hx + hr - 3, hy - 5]], '#efe2c4', OUT, 1);
    }
  } else if (head === 'bald') {
    A.ell(c, hx - 1.6, hy - 3.2, 2, 1.2, 'rgba(255,255,255,0.35)');
  } else if (head === 'hair') {
    c.beginPath();
    c.ellipse(hx - 0.6, hy - 1.6, hr + 0.6, hr + 0.2, 0, Math.PI * 0.85, Math.PI * 2.05);
    c.quadraticCurveTo(hx + 1, hy - 2, hx - hr + 1, hy + 2);
    c.closePath();
    c.fillStyle = o.headColor || '#2a1a14'; c.fill(); c.lineWidth = 1.2; c.strokeStyle = OUT; c.stroke();
    if (o.band) A.line(c, hx - hr + 0.5, hy - 3, hx + hr - 0.5, hy - 3.8, o.band, 1.8);
  } else if (head === 'skull') {
    c.beginPath();
    c.ellipse(hx, hy - 2, hr + 1.5, hr + 0.5, 0, Math.PI, Math.PI * 2);
    c.closePath();
    c.fillStyle = '#efe6d2'; c.fill(); c.lineWidth = 1.2; c.strokeStyle = OUT; c.stroke();
    A.circ(c, hx + 2.5, hy - 4, 1.2, '#2a1a10');
    for (let i = 0; i < 3; i++) A.line(c, hx - 4 + i * 2, hy - hr - 1, hx - 7 + i * 3, hy - hr - 8, ['#58a65c', '#d9a23a', '#3a7fa8'][i], 1.6);
  }
  // braco da frente + arma
  const sx = 3.8 * wide, sy = -15.5;
  let ang;
  if (o.weapon === 'bow' || o.weapon === 'blowgun') ang = o.aim != null ? o.aim : 0;
  else if (atk > 0) {
    const k = 1 - atk / (o.atkMax || 0.28);
    ang = -2.0 + k * 2.7;
  } else ang = o.idleAng != null ? o.idleAng : 0.55;
  const ax = sx + Math.cos(ang) * 6.5, ay = sy + Math.sin(ang) * 6.5;
  if (o.weapon === 'bow') {
    limb(c, sx, sy, sx + 7, sy + 1, U.shade(body, 0.05), 2.8 * wide);
    c.save();
    c.translate(sx + 8, sy + 1);
    c.beginPath(); c.arc(-3, 0, 8, -1.15, 1.15);
    c.strokeStyle = OUT; c.lineWidth = 3.4; c.stroke();
    c.strokeStyle = o.bowColor || '#8a5a2b'; c.lineWidth = 1.8; c.stroke();
    const pull = atk > 0 ? 0 : 3;
    c.beginPath(); c.moveTo(-3 + Math.cos(-1.15) * 8, Math.sin(-1.15) * 8); c.lineTo(-pull, 0); c.lineTo(-3 + Math.cos(1.15) * 8, Math.sin(1.15) * 8);
    c.strokeStyle = 'rgba(240,240,230,0.85)'; c.lineWidth = 0.8; c.stroke();
    if (atk <= 0) A.line(c, -pull, 0, 9, 0, '#d8c8a0', 1);
    c.restore();
  } else {
    limb(c, sx, sy, ax, ay, U.shade(body, 0.05), 2.8 * wide);
    if (o.weapon) {
      c.save();
      c.translate(ax, ay);
      c.rotate(o.weapon === 'staff' ? 0 : ang - 0.25);
      weaponDraw(c, o.weapon, o.weaponColor);
      c.restore();
      if (o.weapon === 'staff' && o.orb) {
        A.glow(c, ax, ay - 21, 7, o.orb, 0.7);
        A.circ(c, ax, ay - 21, 2.6, o.orb, OUT, 1);
      }
    }
    A.circ(c, ax, ay, 1.9, skin, OUT, 0.9);
  }
  c.restore();
};

// ------------------------------------------------------------ inimigos
A.enemy = {};

A.enemy.raider = (c, e, t) => {
  A.humanoid(c, { moving: e.moving, walk: e.walk, atk: e.atkAnim, skin: '#b9784a', body: '#c9924f', legs: '#6b4a2c', belt: '#7c2a22', head: 'turban', headColor: '#e2d2b0', mask: '#a8322d', weapon: 'scimitar', boots: '#4a3220' });
};
A.enemy.nomad = (c, e, t) => {
  A.humanoid(c, { moving: e.moving, walk: e.walk, atk: e.atkAnim, atkMax: 0.3, skin: '#a86f45', body: '#3b4f8a', legs: '#2a3352', belt: '#c9a24a', head: 'hood', headColor: '#2f3f70', weapon: 'bow', bowColor: '#7a4a24', aim: -0.15, cape: '#283868' });
};
A.enemy.shaman = (c, e, t) => {
  const cast = e.castAnim > 0;
  A.humanoid(c, { moving: e.moving, walk: e.walk, atk: e.atkAnim, skin: '#8f6a48', body: '#5d6e34', legs: '#3a4422', belt: '#8a3fa0', head: 'skull', weapon: 'staff', orb: cast ? '#e6ff7a' : '#9be15d', idleAng: -0.2, cape: '#3c2a52' });
  if (cast) A.glow(c, 0, -14, 22, '#bfff6a', 0.35);
};
A.enemy.brute = (c, e, t) => {
  A.humanoid(c, { s: 1.32, wide: 1.25, moving: e.moving, walk: e.walk * 0.8, atk: e.atkAnim, atkMax: 0.3, skin: '#a8714a', body: '#b8793a', chest: '#d39a4e', legs: '#5b3c22', belt: '#3a2414', head: 'helmet', headColor: '#c48a3c', plume: '#a32a2a', weapon: 'axe', weaponColor: '#c98a3a', shield: '#b07432', pauldron: '#d39a4e', boots: '#3a2414' });
};
A.enemy.warlord = (c, e, t) => {
  A.humanoid(c, { s: 1.9, wide: 1.3, moving: e.moving, walk: e.walk * 0.7, atk: e.atkAnim, atkMax: 0.3, skin: '#9c6640', body: '#7c1d1d', chest: '#3a2a2a', legs: '#2c1c14', belt: '#d7a93b', head: 'helmet', headColor: '#4a4a52', horns: true, weapon: 'scimitar', weaponColor: '#e8b84a', cape: '#a3201e', pauldron: '#d7a93b', boots: '#1c120c', eyeColor: '#ff5a2a' });
  if (e.castAnim > 0) A.glow(c, 0, -30, 40, '#ff6a2a', 0.3);
};

A.enemy.jackal = (c, e, t) => {
  const w = e.moving ? e.walk * 1.4 : 0;
  const s1 = Math.sin(w) * 3.5, s2 = Math.sin(w + Math.PI) * 3.5;
  const fur = '#c4813f', dark = '#7a4a22';
  // pernas
  limb(c, -6, -7, -6 + s1, 0, dark, 2.2);
  limb(c, 6, -7, 6 + s2, 0, dark, 2.2);
  // cauda
  c.beginPath(); c.moveTo(-9, -9); c.quadraticCurveTo(-15, -11, -17, -6 + Math.sin(w) * 1.5); c.quadraticCurveTo(-13, -8, -9, -7);
  c.closePath(); c.fillStyle = dark; c.fill(); c.lineWidth = 1.2; c.strokeStyle = OUT; c.stroke();
  // corpo
  A.ell(c, 0, -9, 10, 4.6, A.hgrad(c, -10, 10, fur, 0.25, -0.25), OUT, 1.5);
  limb(c, -4, -7, -4 - s1, 0, fur, 2.2);
  limb(c, 7.5, -7, 7.5 - s2, 0, fur, 2.2);
  // cabeca
  A.poly(c, [[7, -13], [11, -17], [17, -13], [19.5, -11.5], [16, -9.5], [9, -9]], fur, OUT, 1.4);
  A.poly(c, [[9.5, -15.5], [9.5, -21], [12.5, -16.5]], dark, OUT, 1.1);
  A.poly(c, [[12, -16], [13.5, -21], [14.6, -15.6]], dark, OUT, 1.1);
  A.circ(c, 14, -13.5, 0.9, '#2a1508');
  A.circ(c, 19.4, -11.6, 0.9, '#2a1508');
};

A.scorpionBody = (c, e, t, shell, hi, dark) => {
  const w = e.moving ? e.walk * 1.3 : 0;
  // pernas
  for (let i = 0; i < 4; i++) {
    const ph = Math.sin(w + i * 1.3) * 2.2;
    const lx = -6 + i * 4.2;
    limb(c, lx, -6, lx - 4 + ph, 0, dark, 1.8);
    limb(c, lx + 1, -6, lx + 4 - ph, 1, dark, 1.8);
  }
  // cauda (segmentos)
  const tw = e.atkAnim > 0 ? (1 - e.atkAnim / 0.3) : 0;
  const seg = [[-10, -9], [-15, -15], [-15, -22], [-11, -27], [-5 + tw * 6, -28 + tw * 6]];
  for (let i = 0; i < seg.length; i++) A.circ(c, seg[i][0], seg[i][1], 4.6 - i * 0.5, i % 2 ? shell : hi, OUT, 1.3);
  const st = seg[seg.length - 1];
  A.poly(c, [[st[0] + 1, st[1] - 2], [st[0] + 7, st[1] + 2], [st[0] + 1, st[1] + 2]], '#efe0b0', OUT, 1);
  // corpo
  A.ell(c, 0, -7, 11, 5.6, A.hgrad(c, -11, 11, shell, 0.3, -0.3), OUT, 1.6);
  for (let i = -1; i <= 1; i++) A.line(c, i * 4.5, -12, i * 4.5 + 1, -2, U.rgba(dark, 0.6), 1);
  // pincas
  const cl = e.atkAnim > 0 ? 2 : 0;
  limb(c, 7, -8, 13, -11, shell, 2.4);
  A.poly(c, [[12, -13], [19 + cl, -15], [17, -11], [20 + cl, -9], [12, -9]], hi, OUT, 1.2);
  limb(c, 8, -5, 14, -3, shell, 2.4);
  A.poly(c, [[13, -5], [20 + cl, -6], [18, -3], [21 + cl, -1], [13, -1]], hi, OUT, 1.2);
  A.circ(c, 8.5, -10, 1, '#ffde59');
};
A.enemy.scorpion = (c, e, t) => A.scorpionBody(c, e, t, '#8a3b22', '#b85a32', '#4e1e10');

A.enemy.beetle = (c, e, t) => {
  const w = e.moving ? e.walk * 1.4 : 0;
  if (e.burrowed) {
    // monte de areia que se move
    const k = Math.sin(t * 12) * 1.2;
    A.ell(c, 0, -2, 13, 5.5 + k * 0.3, '#b8915a', OUT, 1.3);
    A.ell(c, -2, -4, 7, 2.6, '#d4b07a');
    for (let i = 0; i < 3; i++) A.circ(c, -10 + i * 9 + Math.sin(t * 9 + i) * 2, -2 + Math.cos(t * 8 + i) * 1.5, 1.4, '#a07a48');
    return;
  }
  for (let i = 0; i < 3; i++) {
    const ph = Math.sin(w + i * 2) * 2;
    limb(c, -5 + i * 5, -5, -8 + i * 5 + ph, 0, '#1d2a2a', 1.8);
  }
  A.ell(c, 0, -8, 12, 7.5, A.hgrad(c, -12, 12, '#2e6b6a', 0.35, -0.45), OUT, 1.6);
  A.line(c, -1, -15, -1, -1.5, U.rgba('#0f2a2a', 0.8), 1.4);
  A.ell(c, -4, -11, 4, 2, 'rgba(255,255,255,0.28)');
  A.ell(c, 11, -7, 4.5, 4, '#1f3a3a', OUT, 1.3);
  A.poly(c, [[13, -9], [20, -16], [17, -8]], '#c9b98a', OUT, 1.1);
  for (let i = 0; i < 3; i++) {
    const ph = Math.sin(w + i * 2 + 1) * 2;
    limb(c, -4 + i * 5, -4, -2 + i * 5 - ph, 1, '#1d2a2a', 1.8);
  }
};

A.enemy.vulture = (c, e, t) => {
  const f = Math.sin(t * 9 + e.id) ;
  const y0 = -FLY_H;
  c.save();
  c.translate(0, y0 + Math.sin(t * 3 + e.id) * 2);
  const wing = '#4a3326', wingHi = '#6b4c36';
  // asa de tras
  c.beginPath(); c.moveTo(-2, -2); c.quadraticCurveTo(-8, -14 - f * 8, -20, -10 - f * 10); c.quadraticCurveTo(-12, -4, -4, 2); c.closePath();
  c.fillStyle = U.shade(wing, -0.2); c.fill(); c.lineWidth = 1.3; c.strokeStyle = OUT; c.stroke();
  // corpo
  A.ell(c, 0, 0, 10, 5, A.hgrad(c, -10, 10, wingHi, 0.2, -0.3), OUT, 1.5);
  A.poly(c, [[-9, -1], [-16, 2], [-9, 3]], wing, OUT, 1.1);
  // pescoco e cabeca
  A.ell(c, 9, -3, 3.5, 2.6, '#efe2c8', OUT, 1.1);
  A.circ(c, 13, -5, 3, '#d98a7a', OUT, 1.2);
  A.poly(c, [[15, -6], [19.5, -4.5], [15.5, -3.5]], '#e8c25a', OUT, 1);
  A.circ(c, 13.6, -5.8, 0.8, '#1a0d08');
  // asa da frente
  c.beginPath(); c.moveTo(-2, 0); c.quadraticCurveTo(2, -10 - f * 9, -12, -16 - f * 11); c.quadraticCurveTo(-8, -6, -6, 3); c.closePath();
  c.fillStyle = wing; c.fill(); c.lineWidth = 1.3; c.strokeStyle = OUT; c.stroke();
  for (let i = 0; i < 3; i++) A.line(c, -4 - i * 2.5, -2 - f * 2, -9 - i * 2, -12 - f * 9 + i * 2, U.rgba('#2a1a10', 0.6), 1);
  c.restore();
};

A.enemy.djinn = (c, e, t) => {
  const y0 = -FLY_H - 4 + Math.sin(t * 2.5 + e.id) * 3;
  c.save();
  c.translate(0, y0);
  A.glow(c, 0, -2, 26, '#5ad1ff', 0.35);
  // cauda de vento
  c.beginPath();
  c.moveTo(-6, 2);
  c.quadraticCurveTo(-4, 14, -14 + Math.sin(t * 5) * 3, 22);
  c.quadraticCurveTo(0, 16, 6, 3);
  c.closePath();
  const g = c.createLinearGradient(0, 0, 0, 22);
  g.addColorStop(0, 'rgba(90,190,255,0.95)');
  g.addColorStop(1, 'rgba(90,190,255,0)');
  c.fillStyle = g; c.fill();
  // tronco
  A.ell(c, 0, -3, 8, 8.5, A.hgrad(c, -8, 8, '#3aa0e0', 0.35, -0.25), OUT, 1.4);
  // bracos
  const a = Math.sin(t * 4 + e.id) * 0.4;
  limb(c, -6, -6, -12, -12 + a * 4, '#3aa0e0', 3);
  limb(c, 6, -6, 13, -10 - a * 4, '#3aa0e0', 3);
  // cabeca
  A.circ(c, 1, -15, 5.5, '#4ab4ee', OUT, 1.4);
  A.poly(c, [[-4, -18], [1, -27], [6, -18]], '#e8c25a', OUT, 1.1);
  A.circ(c, 3.4, -15.5, 1.2, '#fffbd0');
  A.glow(c, 3.4, -15.5, 4, '#ffffff', 0.7);
  A.line(c, -1, -10.5, 5, -11, '#1f5a8a', 1);
  c.restore();
};

A.enemy.golem = (c, e, t) => {
  const w = e.moving ? Math.sin(e.walk * 0.7) : 0;
  const stone = '#c79a5e', dark = '#8e6a3c';
  c.save();
  c.scale(1.1, 1.1);
  // pernas
  A.rect(c, -10 - w * 2, -14, 8, 14, A.hgrad(c, -10, -2, stone), OUT, 1.6);
  A.rect(c, 2 + w * 2, -14, 8, 14, A.hgrad(c, 2, 10, stone), OUT, 1.6);
  const bob = Math.abs(w) * 1.5;
  c.translate(0, -bob);
  // braco de tras
  A.rrect(c, -20, -34 + w * 2, 8, 22, 3, U.shade(stone, -0.2), OUT, 1.6);
  // tronco
  A.poly(c, [[-14, -40], [14, -42], [16, -14], [-15, -12]], A.hgrad(c, -15, 16, stone, 0.25, -0.35), OUT, 2);
  A.line(c, -8, -36, -3, -22, U.rgba(dark, 0.8), 1.4);
  A.line(c, 6, -40, 9, -27, U.rgba(dark, 0.8), 1.4);
  // runas
  const pulse = 0.55 + Math.sin(t * 3 + e.id) * 0.25;
  A.glow(c, 0, -27, 9, '#5af0ff', pulse * 0.6);
  A.poly(c, [[0, -33], [4, -27], [0, -21], [-4, -27]], U.rgba('#9ff8ff', pulse), null);
  // cabeca
  A.rrect(c, -7, -52, 14, 12, 3, A.hgrad(c, -7, 7, stone, 0.3, -0.3), OUT, 1.6);
  A.rect(c, 0, -48, 5, 2.2, '#7ff4ff');
  // braco da frente
  const sw = e.atkAnim > 0 ? (1 - e.atkAnim / 0.3) * 10 : 0;
  A.rrect(c, 12, -36 + sw * 0.6 - w * 2, 9, 24, 3, A.hgrad(c, 12, 21, stone), OUT, 1.6);
  A.rrect(c, 11, -14 + sw * 0.6 - w * 2, 11, 9, 3, U.shade(stone, -0.1), OUT, 1.5);
  c.restore();
};

// Coracao da Fumaca sem sprite ainda: o Mapinguari maior, escurecido
A.enemy.heart = (c, e, t) => {
  c.save();
  c.scale(1.35, 1.35);
  A.enemy.golem(c, e, t);
  c.globalCompositeOperation = 'source-atop';
  c.fillStyle = 'rgba(40,24,48,0.55)';
  c.fillRect(-60, -90, 120, 100);
  c.restore();
  A.glow(c, 0, -36, 16, '#ff7a2a', 0.6 + 0.3 * Math.sin(t * 5));
};

A.enemy.worm = (c, e, t, g) => {
  // corpo segue o caminho para tras da cabeca
  const segs = 11, spacing = 15;
  const pts = [];
  const tmp = {};
  for (let i = segs; i >= 1; i--) {
    const p = e.path.at(e.d - i * spacing, tmp);
    pts.push([p.x - e.x, p.y - e.y - 6 - Math.sin(t * 4 - i * 0.7) * 2]);
  }
  if (e.burrowed) {
    for (let i = 0; i < pts.length; i += 2) {
      A.ell(c, pts[i][0], pts[i][1] + 8, 14, 5, '#a8834e', OUT, 1.2);
    }
    A.ell(c, 0, 0, 24, 8, '#a8834e', OUT, 1.5);
    A.ell(c, -4, -2, 12, 3, '#c9a46c');
    return;
  }
  for (let i = 0; i < pts.length; i++) {
    const r = 10 + (i / pts.length) * 12;
    const [x, y] = pts[i];
    A.ell(c, x, y + r * 0.35, r, r * 0.55, 'rgba(45,22,6,0.25)');
    A.circ(c, x, y - r * 0.4, r, A.hgrad(c, x - r, x + r, i % 2 ? '#9a6a48' : '#b07d55', 0.3, -0.35), OUT, 1.8);
    A.line(c, x - r * 0.7, y - r * 0.8, x + r * 0.5, y - r * 0.9, U.rgba('#e8c8a0', 0.5), 1.6);
  }
  // cabeca
  const open = 0.5 + Math.sin(t * 3) * 0.3;
  A.circ(c, 0, -24, 26, A.hgrad(c, -26, 26, '#b9875c', 0.3, -0.35), OUT, 2.2);
  A.ell(c, 6 * e.facing, -24, 15, 15 * open + 4, '#3a0e0e', OUT, 2);
  for (let i = 0; i < 10; i++) {
    const a = (i / 10) * U.TAU;
    const x = 6 * e.facing + Math.cos(a) * 13, y = -24 + Math.sin(a) * (13 * open + 3);
    A.poly(c, [[x, y], [x + Math.cos(a + 2.6) * 5, y + Math.sin(a + 2.6) * 5], [x + Math.cos(a - 2.6) * 5, y + Math.sin(a - 2.6) * 5]], '#f3ead2', OUT, 0.8);
  }
  A.glow(c, 6 * e.facing, -24, 10, '#ff5a2a', 0.35);
};

A.drawEnemy = (c, e, t) => {
  const fn = A.enemy[e.type];
  c.save();
  c.translate(e.x, e.y);
  const T = DATA.ENEMIES[e.type];
  // espectro escondido: so um vulto tremulando
  const hidden = T.stealth && !e.revealed;
  // Coracao da Fumaca virado fumaca: so um vulto
  if (e.untargetable) c.globalAlpha = 0.28;
  // sprite do Blender (js/inimigos.js): ja traz a propria sombra
  const spr = A.enemySprite && ESPR.ready(e.type) && !e.burrowed;
  if (spr) {
    if (hidden) c.globalAlpha = 0.22 + Math.sin(t * 7 + e.id) * 0.06;
    if (e.flying) A.shadow(c, 0, 2, T.size * 0.9, T.size * 0.32, 0.18);
    if (T.flying && !e.flying && e.type !== 'ifrit') c.translate(0, FLY_H - 8);
    if (A.enemySprite(c, e, t, hidden)) { c.restore(); return; }
  }
  if (!e.flying && e.type !== 'worm') A.shadow(c, 0, 0, T.size * 1.05, T.size * 0.42);
  if (e.flying) A.shadow(c, 0, 2, T.size * 0.9, T.size * 0.32, 0.18);
  if (e.type === 'worm') { fn(c, e, t); c.restore(); return; }
  if (hidden) c.globalAlpha = 0.22 + Math.sin(t * 7 + e.id) * 0.06;
  // voador derrubado: desenha perto do chao
  if (T.flying && !e.flying && e.type !== 'ifrit') c.translate(0, FLY_H - 8);
  if (e.facing < 0) c.scale(-1, 1);
  fn(c, e, t);
  // clarao de dano sem ctx.filter (o WebKit do app nao suporta): redesenha somando luz
  if (e.hurtT > 0 && !e.burrowed && !hidden) { c.globalCompositeOperation = 'lighter'; c.globalAlpha = 0.45; fn(c, e, t); }
  else if (e.frozenT > 0) { c.globalCompositeOperation = 'lighter'; c.globalAlpha = 0.35 + Math.min(1, e.frozenT) * 0.25; fn(c, e, t); }
  c.restore();
};

// ------------------------------------------------------------ unidades aliadas
A.unit = {};
A.unit.soldier = (c, u, t) => {
  const tier = u.tier || 1;
  const P = [
    { body: '#7a5a3a', chest: null, head: 'helmet', headColor: '#8e7a62', shield: '#8a5a32', weapon: 'sword', legs: '#4a3a2a' },
    { body: '#6e7b86', chest: '#8d99a3', head: 'helmet', headColor: '#a2adb5', shield: '#1f8f8a', weapon: 'sword', legs: '#3c4650' },
    { body: '#1f7f7a', chest: '#c3cbd1', head: 'helmet', headColor: '#d5dce1', plume: '#e8b84a', shield: '#1f8f8a', weapon: 'sword', legs: '#2c3a40', pauldron: '#c3cbd1' },
  ][Math.min(3, tier) - 1];
  A.humanoid(c, Object.assign({ moving: u.moving, walk: u.walk, atk: u.atkAnim, skin: '#d69a6a', belt: '#4a2f1a', boots: '#3a2616' }, P));
};
A.unit.lancers = (c, u, t) => {
  A.humanoid(c, { s: 1.08, moving: u.moving, walk: u.walk, atk: u.atkAnim, skin: '#c98d5c', body: '#c98a3a', chest: '#e7b04d', legs: '#5a3a1e', head: 'helmet', headColor: '#e2b04a', plume: '#c62f2f', shield: '#d79a3a', weapon: 'spear', weaponColor: '#c62f2f', pauldron: '#e7b04d', boots: '#3a2616', idleAng: 0.1 });
};
A.unit.monks = (c, u, t) => {
  A.humanoid(c, { moving: u.moving, walk: u.walk, atk: u.atkAnim, skin: '#c58a58', body: '#e07a2a', legs: '#a6521a', belt: '#7a2a12', head: 'bald', weapon: 'staff', idleAng: 0.3, cape: '#c4621e' });
};
A.unit.rider = (c, u, t) => {
  const w = u.moving ? u.walk : 0;
  const s1 = Math.sin(w) * 4, s2 = Math.sin(w + Math.PI) * 4;
  const fur = '#d2a36a', dark = '#9a6f3e';
  c.save();
  c.scale(0.95, 0.95);
  limb(c, -9, -14, -9 + s1, 0, dark, 2.6);
  limb(c, 8, -14, 8 + s2, 0, dark, 2.6);
  A.ell(c, 0, -17, 13, 6.5, A.hgrad(c, -13, 13, fur, 0.25, -0.3), OUT, 1.6);
  A.ell(c, -1, -23, 6, 5, fur, OUT, 1.4);
  // pescoco e cabeca
  c.beginPath(); c.moveTo(9, -19); c.quadraticCurveTo(15, -24, 15, -32); c.lineTo(19, -32); c.quadraticCurveTo(19, -22, 12, -14); c.closePath();
  c.fillStyle = fur; c.fill(); c.lineWidth = 1.4; c.strokeStyle = OUT; c.stroke();
  A.ell(c, 19, -33, 5, 3.2, fur, OUT, 1.3);
  A.circ(c, 19.5, -34.2, 0.8, '#1a0d08');
  limb(c, -6, -14, -6 - s1, 0, fur, 2.6);
  limb(c, 11, -14, 11 - s2, 0, fur, 2.6);
  // sela
  A.rect(c, -6, -26, 11, 4, '#1f8f8a', OUT, 1.2);
  // cavaleiro
  c.translate(-1, -24);
  A.humanoid(c, { s: 0.85, moving: false, atk: u.atkAnim, skin: '#c98d5c', body: '#e9dcc0', legs: '#1f8f8a', head: 'turban', headColor: '#1f8f8a', weapon: 'spear', weaponColor: '#e8b84a', idleAng: -0.25 });
  c.restore();
};
A.unit.hero = (c, u, t) => {
  const whirl = u.whirlT > 0;
  if (whirl) {
    c.save();
    c.rotate(0);
  }
  A.humanoid(c, { s: 1.22, moving: u.moving, walk: u.walk, atk: u.atkAnim, atkMax: 0.28, skin: '#c98d5c', body: '#1f8f8a', chest: '#e8c25a', legs: '#2a2a3a', belt: '#7a2a22', head: 'hair', headColor: '#22150f', hair: 'tail', band: '#e8c25a', weapon: 'scimitar', weaponColor: '#e8c25a', cape: '#16706c', pauldron: '#e8c25a', boots: '#3a2616' });
  if (whirl) c.restore();
};
A.drawUnit = (c, u, t, selected) => {
  c.save();
  c.translate(u.x, u.y);
  if (selected) {
    const p = 0.5 + Math.sin(t * 6) * 0.25;
    A.ell(c, 0, 0, 17, 7, null, `rgba(127,255,212,${p + 0.3})`, 2.4);
  }
  // bicho liberto chamado pela Caipora: sprite natural da folha do inimigo (js/inimigos.js)
  if (u.kind === 'beast') {
    if (u.facing < 0) c.scale(-1, 1);
    if (!(A.beastSprite && A.beastSprite(c, u))) A.unit.soldier(c, u, t);
    c.restore();
    return;
  }
  const big = u.kind === 'rider' || u.kind === 'hero';
  // sprite do Blender (js/unidades.js) ja traz a propria sombra; sem ele, o desenho 2D antigo
  const spr = typeof USPR !== 'undefined' && USPR.ready(USPR.key(u));
  if (!spr) A.shadow(c, 0, 0, big ? 13 : 8.5, big ? 5 : 3.4);
  if (u.facing < 0) c.scale(-1, 1);
  if (!(spr && A.unitSprite(c, u))) {
    const fn = A.unit[u.kind] || A.unit.soldier;
    fn(c, u, t);
    if (u.hurtT > 0) { c.globalCompositeOperation = 'lighter'; c.globalAlpha = 0.4; fn(c, u, t); }
  }
  c.restore();
};

// arqueiro / atirador em cima de torre
A.towerman = (c, x, y, facing, o) => {
  c.save();
  c.translate(x, y);
  if (facing < 0) c.scale(-1, 1);
  A.humanoid(c, Object.assign({ s: 0.85, moving: false, skin: '#d29a6a', body: '#3f6a3a', legs: '#3a2a1a', head: 'hood', headColor: '#2f5530', weapon: 'bow', aim: -0.1 }, o));
  c.restore();
};
