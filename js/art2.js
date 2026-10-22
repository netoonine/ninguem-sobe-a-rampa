'use strict';
// Arte da expansao: Cisterna, Catavento, Estandarte e Mercado (3 niveis + 2 especializacoes cada),
// inimigos novos, mercenario e icones extras.

// torres desenhadas por codigo acompanham o tamanho das de sprite e da plataforma do lote
const TOWER_SCALE = 1.3;
const WATER = '#3aa3b8', WATER_L = '#8fe0ea', WATER_D = '#226f8a', BRONZE = '#b9853e', TILE = '#2f7fb0';

function waterTop(c, x, y, rx, ry, time) {
  A.ell(c, x, y, rx, ry, A.hgrad(c, x - rx, x + rx, WATER, 0.25, -0.25), OUT, 1.5);
  const w = Math.sin(time * 3 + x) * rx * 0.25;
  A.ell(c, x - rx * 0.25 + w * 0.3, y - ry * 0.2, rx * 0.35, ry * 0.25, 'rgba(255,255,255,0.45)');
}

// bico de bronze que gira para o alvo
function nozzle(c, x, y, t, len, col) {
  const ax = (t.aimX == null ? t.x - 50 : t.aimX) - t.x;
  const ang = ax >= 0 ? -0.35 : Math.PI + 0.35;
  c.save();
  c.translate(x, y);
  c.rotate(ang);
  A.rrect(c, -3, -3, len, 6, 2, A.hgrad(c, -3, len, col || BRONZE, 0.4, -0.3), OUT, 1.3);
  A.rect(c, len - 4, -4, 4, 8, U.shade(col || BRONZE, -0.2), OUT, 1);
  if (t.anim > 0.2) A.glow(c, len + 2, 0, 9, WATER_L, 0.8);
  c.restore();
  A.circ(c, x, y, 4, col || BRONZE, OUT, 1.2);
}

function zellige(c, x, y, w, h) {
  A.rect(c, x - w / 2, y, w, h, TILE, OUT, 1);
  for (let i = 0; i < Math.floor(w / 7); i++) {
    const xx = x - w / 2 + 3.5 + i * 7;
    A.poly(c, [[xx, y + 0.8], [xx + 2.2, y + h / 2], [xx, y + h - 0.8], [xx - 2.2, y + h / 2]], i % 2 ? '#e8e0c8' : '#e8b84a', null);
  }
}

// ------------------------------------------------------------ CISTERNA
A.tower.cistern = (c, t, time) => {
  if (t.spec === 'fountain') return A.tower.fountain(c, t, time);
  if (t.spec === 'geyser') return A.tower.geyser(c, t, time);
  if (t.tier === 1) {
    A.shadow(c, 0, 3, 30, 12);
    A.cyl(c, 0, -14, 0, 22, 9, '#b9a993', { bricks: 7, noTop: true });
    A.ell(c, 0, -14, 22, 9, '#a8977e', OUT, 2);
    waterTop(c, 0, -14, 17, 6.5, time);
    post(c, -18, -12, -46, WOOD_D, 4); post(c, 18, -12, -46, WOOD_D, 4);
    A.rect(c, -23, -51, 46, 6, A.hgrad(c, -23, 23, WOOD, 0.3, -0.3), OUT, 1.5);
    A.circ(c, 0, -42, 5, '#7a5230', OUT, 1.3);
    A.circ(c, 0, -42, 1.6, GOLD);
    const bob = Math.sin(time * 2) * 2;
    A.line(c, 0, -42, 0, -30 + bob, '#d8c8a0', 1.2);
    A.rrect(c, -4.5, -31 + bob, 9, 8, 2, A.hgrad(c, -4.5, 4.5, '#8a5a2e'), OUT, 1.1);
    A.line(c, -4.5, -28 + bob, 4.5, -28 + bob, '#4a3a2a', 1);
    nozzle(c, 14, -38, t, 12);
  } else if (t.tier === 2) {
    A.shadow(c, 0, 3, 31, 12);
    A.cyl(c, 0, -46, 0, 24, 10, SANDSTONE, { bricks: 8, noTop: true });
    zellige(c, 0, -30, 48, 6);
    A.ell(c, 0, -46, 24, 10, '#b8995e', OUT, 2);
    waterTop(c, 0, -46, 19, 7.5, time);
    A.rect(c, -6, -14, 12, 14, '#3a2412', OUT, 1.2);
    // biquinho escorrendo
    const k = (time * 1.3) % 1;
    A.circ(c, -20, -26 + k * 24, 1.6, WATER_L);
    nozzle(c, 0, -52, t, 15);
  } else {
    A.shadow(c, 0, 3, 33, 13);
    A.cyl(c, 0, -26, 0, 20, 8, SANDSTONE, { bricks: 8 });
    // tanque
    A.cyl(c, 0, -58, -26, 28, 11, '#5f8fa8', { noTop: true });
    for (const yy of [-52, -40, -30]) {
      c.beginPath(); c.ellipse(0, yy, 28, 11, 0, 0, Math.PI);
      c.strokeStyle = OUT; c.lineWidth = 3; c.stroke();
      c.strokeStyle = BRONZE; c.lineWidth = 1.8; c.stroke();
    }
    for (let i = -2; i <= 2; i++) A.line(c, i * 10, -56 + Math.abs(i) * 0.8, i * 10, -28 + Math.abs(i) * 0.8, U.rgba('#2a4a5a', 0.5), 1);
    A.ell(c, 0, -58, 28, 11, '#4a7a90', OUT, 2);
    waterTop(c, 0, -58, 22, 8.5, time);
    A.cone(c, 0, -60, 10, 4, 14, TEAL);
    A.circ(c, 0, -75, 2.5, GOLD, OUT, 1);
    // roda da bomba
    const a = time * 2;
    c.save(); c.translate(-26, -14);
    A.circ(c, 0, 0, 9, null, WOOD_D, 3);
    for (let i = 0; i < 4; i++) A.line(c, 0, 0, Math.cos(a + i * Math.PI / 2) * 9, Math.sin(a + i * Math.PI / 2) * 9, WOOD_D, 2);
    c.restore();
    nozzle(c, 20, -44, t, 16);
  }
};

A.tower.fountain = (c, t, time) => {
  const marble = '#e9e0cf';
  A.shadow(c, 0, 3, 36, 14);
  A.cyl(c, 0, -10, 0, 32, 13, marble, { noTop: true });
  zellige(c, 0, -8, 64, 5);
  A.ell(c, 0, -10, 32, 13, '#d2c6ae', OUT, 2);
  waterTop(c, 0, -10, 27, 10, time);
  A.cyl(c, 0, -42, -10, 6, 2.5, marble);
  A.cyl(c, 0, -46, -40, 17, 6.5, marble, { noTop: true });
  A.ell(c, 0, -46, 17, 6.5, '#d2c6ae', OUT, 1.6);
  waterTop(c, 0, -46, 13, 4.8, time + 1);
  A.cyl(c, 0, -60, -46, 3.5, 1.5, marble);
  A.ell(c, 0, -62, 8, 3, marble, OUT, 1.4);
  // jatos d'agua animados
  c.save();
  c.lineCap = 'round';
  for (let i = 0; i < 4; i++) {
    const s = i < 2 ? -1 : 1, far = i % 2 ? 1 : 0.6;
    c.beginPath();
    c.moveTo(s * 4, -63);
    c.quadraticCurveTo(s * 14 * far, -78, s * 15 * far + s * 2, -46 + (far > 0.8 ? 0 : 2));
    c.strokeStyle = 'rgba(150,225,240,0.85)'; c.lineWidth = 2.2; c.stroke();
    c.strokeStyle = 'rgba(255,255,255,0.6)'; c.lineWidth = 0.9; c.stroke();
  }
  for (let i = 0; i < 6; i++) {
    const k = ((time * 1.6 + i / 6) % 1);
    const s = i % 2 ? 1 : -1;
    A.circ(c, s * (17 + k * 8), -44 + k * 30, 1.4, WATER_L);
  }
  c.restore();
  if (t.anim > 0.2) A.glow(c, 0, -64, 18, WATER_L, 0.8);
  // folhagens
  const wv = Math.sin(time * 2) * 1.5;
  A.poly(c, [[-32, -8], [-42, -22 + wv], [-30, -16]], '#4f8a3c', OUT, 1);
  A.poly(c, [[32, -8], [42, -22 - wv], [30, -16]], '#4f8a3c', OUT, 1);
};

A.tower.geyser = (c, t, time) => {
  A.shadow(c, 0, 3, 34, 13);
  A.box(c, 0, 0, 56, 8, 14, '#8a7c6a');
  A.cyl(c, 0, -50, -8, 22, 9, BRONZE, { noTop: true });
  for (const yy of [-44, -28, -14]) {
    c.beginPath(); c.ellipse(0, yy, 22, 9, 0, 0, Math.PI);
    c.strokeStyle = OUT; c.lineWidth = 3; c.stroke();
    c.strokeStyle = '#7a5226'; c.lineWidth = 1.6; c.stroke();
  }
  for (let i = 0; i < 6; i++) A.circ(c, -18 + i * 7.2, -36 + Math.sin((i / 5) * Math.PI) * 6.5, 1.3, '#f2d08a', OUT, 0.6);
  A.ell(c, 0, -50, 22, 9, '#a87436', OUT, 2);
  // canos
  A.line(c, -26, -6, -26, -40, OUT, 6); A.line(c, -26, -6, -26, -40, '#c87533', 4);
  A.line(c, -26, -40, -18, -46, OUT, 6); A.line(c, -26, -40, -18, -46, '#c87533', 4);
  // manometro
  A.circ(c, 22, -22, 6, '#efe8d8', OUT, 1.4);
  const g = Math.sin(time * 2) * 0.8 + (t.anim > 0 ? 1.2 : 0);
  A.line(c, 22, -22, 22 + Math.cos(-2.4 + g) * 4.5, -22 + Math.sin(-2.4 + g) * 4.5, '#c62f2f', 1.3);
  // vapor
  for (let i = 0; i < 3; i++) {
    const k = (time * 0.8 + i / 3) % 1;
    c.save(); c.globalAlpha = (1 - k) * 0.55;
    A.circ(c, -26 + Math.sin(k * 6 + i) * 3, -50 - k * 26, 4 + k * 6, '#f4f2ee');
    c.restore();
  }
  nozzle(c, 0, -58, t, 20, '#c87533');
};

// ------------------------------------------------------------ CATAVENTO
function sails(c, x, y, r, n, ang, cloth, frame) {
  for (let i = 0; i < n; i++) {
    const a = ang + (i / n) * U.TAU;
    const ca = Math.cos(a), sa = Math.sin(a);
    const px = -sa, py = ca;
    const w0 = r * 0.08, w1 = r * 0.28;
    const p0 = [x + ca * r * 0.18 + px * w0, y + (sa * r * 0.18 + py * w0) * 0.9];
    const p1 = [x + ca * r + px * w1, y + (sa * r + py * w1) * 0.9];
    const p2 = [x + ca * r, y + sa * r * 0.9];
    const p3 = [x + ca * r * 0.18, y + sa * r * 0.18 * 0.9];
    A.poly(c, [p3, p0, p1, p2], cloth, OUT, 1.2);
    A.line(c, x, y, x + ca * r * 1.02, y + sa * r * 0.92, frame || WOOD_D, 2);
  }
  A.circ(c, x, y, Math.max(2.5, r * 0.12), GOLD, OUT, 1.2);
}

function windRot(t, time, mul) {
  return time * (mul || 1.6) + (t.anim > 0 ? t.anim * 8 : 0) + (t.id || 0);
}

A.tower.windmill = (c, t, time) => {
  if (t.spec === 'tornado') return A.tower.tornado(c, t, time);
  if (t.spec === 'sandblast') return A.tower.sandblast(c, t, time);
  const rot = windRot(t, time);
  if (t.tier === 1) {
    A.shadow(c, 0, 3, 28, 11);
    post(c, 0, 0, -22, WOOD_D, 6);
    A.line(c, -14, 0, 0, -14, WOOD_D, 2.4); A.line(c, 14, 0, 0, -14, WOOD_D, 2.4);
    A.box(c, 0, -20, 26, 24, 8, WOOD);
    A.poly(c, [[-15, -52], [0, -62], [15, -52]], A.hgrad(c, -15, 15, '#a8502e', 0.25, -0.35), OUT, 1.5);
    A.rect(c, -4, -32, 8, 10, '#3a2412', OUT, 1);
    sails(c, 0, -42, 26, 4, rot, '#efe2c4');
  } else if (t.tier === 2) {
    A.shadow(c, 0, 3, 30, 12);
    A.cyl(c, 0, -34, 0, 20, 8, '#c4a77c', { bricks: 8 });
    A.cone(c, 0, -34, 22, 8, 20, '#8a5a2e');
    A.rect(c, -5, -14, 10, 14, '#3a2412', OUT, 1.2);
    sails(c, 0, -50, 33, 4, rot, '#f2e6c8');
  } else {
    A.shadow(c, 0, 3, 32, 13);
    A.cyl(c, 0, -52, 0, 18, 7, SANDSTONE, { bricks: 8 });
    railing(c, -30, 40, 6);
    A.cone(c, 0, -52, 21, 8, 18, TEAL);
    A.rect(c, -5, -14, 10, 14, '#3a2412', OUT, 1.2);
    archWindow(c, 0, -38, 6, 10, false, time);
    sails(c, 0, -60, 38, 6, rot, '#f6ecd2');
    A.flag(c, 0, -70, 12, '#c62f2f', time);
  }
};

A.tower.tornado = (c, t, time) => {
  A.shadow(c, 0, 3, 33, 13);
  A.cyl(c, 0, -40, 0, 22, 9, '#9aa4a8', { bricks: 7 });
  for (const yy of [-34, -18]) A.rect(c, -22, yy, 44, 3, TEAL, OUT, 1);
  A.ell(c, 0, -40, 22, 9, '#7d878c', OUT, 2);
  // funil de vento
  c.save();
  for (let i = 0; i < 6; i++) {
    const k = i / 5;
    const rx = 8 + k * 22, yy = -46 - k * 34;
    const ph = time * 5 + i;
    c.beginPath();
    c.ellipse(Math.sin(ph) * 2, yy, rx, rx * 0.3, 0, ph % U.TAU, (ph % U.TAU) + 4.4);
    c.strokeStyle = `rgba(220,245,255,${0.85 - k * 0.35})`; c.lineWidth = 2.6 - k; c.stroke();
  }
  c.restore();
  sails(c, 0, -50, 30, 8, windRot(t, time, 4), 'rgba(235,245,250,0.9)', '#5a6a70');
  if (t.anim > 0.2) A.glow(c, 0, -60, 30, '#dff6ff', 0.5);
};

A.tower.sandblast = (c, t, time) => {
  // torre de vento persa (badgir)
  A.shadow(c, 0, 3, 32, 13);
  A.box(c, 0, 0, 44, 30, 12, '#d6b47a');
  A.box(c, 0, -30, 30, 40, 10, '#e2c48e');
  for (let i = 0; i < 4; i++) A.rect(c, -12 + i * 7, -66, 4, 16, '#3a2412', OUT, 1);
  A.rect(c, -16, -72, 32, 4, TEAL, OUT, 1.2);
  A.box(c, 0, -72, 34, 4, 6, '#c9a46c');
  zellige(c, 0, -24, 44, 5);
  A.rect(c, -6, -16, 12, 16, '#3a2412', OUT, 1.2);
  // areia saindo das janelas
  const r = U.rng(Math.floor(time * 10) + (t.id || 0));
  for (let i = 0; i < 6; i++) {
    const k = r();
    c.save(); c.globalAlpha = 0.7 * (1 - k);
    A.circ(c, (r() - 0.5) * 30, -64 - k * 18, 1.5 + r() * 2, '#e8c890');
    c.restore();
  }
  if (t.anim > 0.2) A.glow(c, 0, -66, 24, '#f0d090', 0.6);
};

// ------------------------------------------------------------ ESTANDARTE
function drum(c, x, y, r, col) {
  A.cyl(c, x, y - r * 1.1, y, r, r * 0.38, col || '#a8502e');
  A.ell(c, x, y - r * 1.1, r, r * 0.38, '#efe2c4', OUT, 1.4);
  for (let i = 0; i < 5; i++) {
    const a = (i / 5) * Math.PI;
    A.line(c, x + Math.cos(a) * r, y - r * 1.1 + Math.sin(a) * r * 0.38, x + Math.cos(a + 0.6) * r, y + Math.sin(a + 0.6) * r * 0.38, '#e8c25a', 1);
  }
}

A.tower.banner = (c, t, time) => {
  if (t.spec === 'drums') return A.tower.drums(c, t, time);
  if (t.spec === 'watch') return A.tower.watch(c, t, time);
  const wv = Math.sin(time * 2.2 + (t.id || 0)) * 1.5;
  if (t.tier === 1) {
    A.shadow(c, 0, 3, 28, 11);
    deck(c, 0, 44, 6, 12);
    A.line(c, 0, -10, 0, -66, '#5b3a1e', 3);
    A.banner(c, 4 + wv * 0.2, -60, 18, 30, TEAL, true);
    A.circ(c, 0, -67, 2.5, GOLD, OUT, 1);
    drum(c, -14, -8, 7);
  } else if (t.tier === 2) {
    A.shadow(c, 0, 3, 30, 12);
    A.box(c, 0, 0, 46, 10, 14, '#c7b28c');
    A.line(c, -12, -22, -12, -76, '#5b3a1e', 3);
    A.line(c, 12, -22, 12, -70, '#5b3a1e', 3);
    A.banner(c, -8 + wv * 0.2, -72, 16, 28, TEAL, true);
    A.banner(c, 16 - wv * 0.2, -66, 14, 24, '#c62f2f', 'sun');
    A.circ(c, -12, -77, 2.5, GOLD, OUT, 1); A.circ(c, 12, -71, 2.5, GOLD, OUT, 1);
    A.deco.brazier(c, 0, -22, 0.8);
    A.glow(c, 0, -34, 10 + Math.sin(time * 9) * 2, '#ffb347', 0.8);
  } else {
    A.shadow(c, 0, 3, 32, 13);
    A.box(c, 0, 0, 44, 8, 14, '#c7b28c');
    A.poly(c, [[-9, -22], [-7, -80], [7, -80], [9, -22]], A.hgrad(c, -9, 9, '#d9c39a', 0.25, -0.35), OUT, 1.6);
    A.banner(c, 0, -76, 24, 44, TEAL, true);
    A.line(c, -14, -76, 14, -76, '#6b4423', 3);
    // disco solar no topo
    const cy = -88;
    A.glow(c, 0, cy, 20, '#ffd34a', 0.55);
    A.circ(c, 0, cy, 7, A.hgrad(c, -7, 7, '#ffd75a', 0.5, -0.25), OUT, 1.5);
    for (const bx of [-24, 24]) {
      A.deco.brazier(c, bx, -2, 0.8);
      A.glow(c, bx, -14, 9 + Math.sin(time * 9 + bx) * 2, '#ffb347', 0.85);
    }
  }
};

A.tower.drums = (c, t, time) => {
  A.shadow(c, 0, 3, 34, 13);
  A.box(c, 0, 0, 58, 8, 16, '#c7a978');
  // pavilhao
  post(c, -24, -16, -58, WOOD_D, 4); post(c, 24, -16, -58, WOOD_D, 4);
  const hit = t.anim > 0 ? Math.sin(t.anim * 30) * 2 : 0;
  drum(c, -10, -16, 11, '#a8502e');
  drum(c, 12, -14, 8, '#8a3a1e');
  A.humanoid(c, { s: 0.85, moving: false, atk: t.anim > 0 ? 0.15 : 0, skin: '#c98d5c', body: '#c62f2f', legs: '#5a2a1a', head: 'turban', headColor: '#e8c25a', weapon: 'staff', idleAng: -0.6 - hit * 0.1 });
  c.beginPath();
  c.moveTo(-30, -56); c.quadraticCurveTo(0, -78, 30, -56);
  c.lineTo(28, -50); c.quadraticCurveTo(0, -66, -28, -50); c.closePath();
  c.fillStyle = A.hgrad(c, -30, 30, TEAL, 0.25, -0.35); c.fill(); c.lineWidth = 1.6; c.strokeStyle = OUT; c.stroke();
  for (let i = 0; i < 7; i++) {
    const x = -26 + i * 8.6;
    A.poly(c, [[x - 3, -52 + Math.abs(x) * 0.12], [x + 3, -52 + Math.abs(x) * 0.12], [x, -46 + Math.abs(x) * 0.12]], i % 2 ? GOLD : '#c62f2f', OUT, 0.8);
  }
  A.flag(c, 0, -70, 16, GOLD, time);
  if (t.warT > 0) A.glow(c, 0, -30, 46, '#ffb35a', 0.35 + Math.sin(time * 12) * 0.1);
};

A.tower.watch = (c, t, time) => {
  A.shadow(c, 0, 3, 32, 12);
  A.cyl(c, 0, -62, 0, 17, 7, '#e9e0cf', { noTop: true });
  for (const [y0, y1] of [[-48, -40], [-24, -16]]) {
    c.save();
    c.beginPath(); c.rect(-18, y0, 36, y1 - y0); c.clip();
    A.cyl(c, 0, y0, y1, 17, 7, '#c62f2f', { noTop: true });
    c.restore();
  }
  A.ell(c, 0, -62, 20, 8, '#8a7c6a', OUT, 2);
  railing(c, -62, 38, 6);
  // sala da lanterna
  A.rect(c, -9, -80, 18, 16, 'rgba(255,240,180,0.85)', OUT, 1.5);
  A.line(c, 0, -80, 0, -64, OUT, 1.2);
  A.cone(c, 0, -80, 12, 5, 12, '#2f6fb0');
  // facho girando
  const a = time * 1.2;
  const dir = Math.cos(a);
  c.save();
  c.globalCompositeOperation = 'lighter';
  const g = c.createLinearGradient(0, -72, dir * 70, -66);
  g.addColorStop(0, 'rgba(255,240,170,0.55)'); g.addColorStop(1, 'rgba(255,240,170,0)');
  c.fillStyle = g;
  c.beginPath(); c.moveTo(0, -74); c.lineTo(dir * 70, -84); c.lineTo(dir * 70, -60); c.closePath(); c.fill();
  c.restore();
  A.glow(c, 0, -72, 18, '#fff0a0', 0.9);
  // olho
  A.ell(c, 0, -72, 5, 3, '#fff8e0', OUT, 1);
  A.circ(c, Math.sin(a) * 1.5, -72, 1.6, '#1a5a56');
};

// ------------------------------------------------------------ MERCADO
function awning(c, x, y, w, h, c1, c2, time) {
  const n = 6, wv = Math.sin(time * 2 + x) * 0.8;
  for (let i = 0; i < n; i++) {
    const x0 = x - w / 2 + (w / n) * i, x1 = x0 + w / n;
    A.poly(c, [[x0, y], [x1, y], [x1 + 1, y + h + wv], [x0 + 1, y + h + wv]], i % 2 ? c1 : c2, null);
  }
  A.poly(c, [[x - w / 2, y], [x + w / 2, y], [x + w / 2 + 1, y + h + wv], [x - w / 2 + 1, y + h + wv]], null, OUT, 1.4);
  for (let i = 0; i < n; i++) {
    const xx = x - w / 2 + (w / n) * (i + 0.5);
    c.beginPath(); c.arc(xx + 1, y + h + wv, w / n / 2, 0, Math.PI);
    c.fillStyle = i % 2 ? c1 : c2; c.fill(); c.lineWidth = 1; c.strokeStyle = OUT; c.stroke();
  }
}

function sack(c, x, y, s, col) {
  c.save(); c.translate(x, y); c.scale(s, s);
  A.poly(c, [[-5, 0], [-6, -6], [-3, -10], [3, -10], [6, -6], [5, 0]], col || '#d9c08c', OUT, 1.1);
  A.line(c, -3, -9, 3, -9, '#8a6a3a', 1.2);
  c.restore();
}

function coinPile(c, x, y, n) {
  for (let i = 0; i < n; i++) A.ell(c, x + (i % 3 - 1) * 4, y - Math.floor(i / 3) * 2.4, 3.6, 1.6, '#f2c43c', '#a8701a', 0.8);
}

A.tower.market = (c, t, time) => {
  if (t.spec === 'bazaar') return A.tower.bazaar(c, t, time);
  if (t.spec === 'treasury') return A.tower.treasury(c, t, time);
  if (t.tier === 1) {
    A.shadow(c, 0, 3, 30, 11);
    post(c, -18, 0, -34, WOOD_D, 3.5); post(c, 18, 0, -34, WOOD_D, 3.5);
    A.box(c, 0, 0, 40, 12, 8, WOOD);
    awning(c, 0, -40, 44, 8, '#c62f2f', '#efe2c4', time);
    A.humanoid(c, { s: 0.8, moving: false, skin: '#c98d5c', body: '#7a5a8a', legs: '#3a2a4a', head: 'turban', headColor: '#e8c25a', idleAng: 0.9 });
    A.deco.jars(c, -12, -12, 0.7);
    sack(c, 13, -12, 0.9);
  } else if (t.tier === 2) {
    A.shadow(c, 0, 3, 32, 12);
    A.deco.tent(c, 14, -2, 0.75);
    post(c, -24, 2, -36, WOOD_D, 3.5); post(c, 4, 2, -36, WOOD_D, 3.5);
    A.box(c, -10, 2, 34, 12, 8, WOOD);
    awning(c, -10, -42, 38, 8, '#1f8f8a', '#efe2c4', time);
    A.deco.jars(c, -20, -10, 0.7);
    coinPile(c, -2, -12, 5);
    sack(c, 22, 6, 1); sack(c, 30, 4, 0.8, '#c9a46c');
  } else {
    A.shadow(c, 0, 3, 34, 13);
    A.box(c, 0, 0, 54, 30, 14, '#d9be8a');
    c.beginPath(); c.moveTo(-9, 0); c.lineTo(-9, -16); c.arc(0, -16, 9, Math.PI, 0); c.lineTo(9, 0); c.closePath();
    c.fillStyle = '#4a2e18'; c.fill(); c.lineWidth = 1.6; c.strokeStyle = OUT; c.stroke();
    c.beginPath(); c.ellipse(0, -44, 14, 13, 0, Math.PI, 0); c.closePath();
    c.fillStyle = A.hgrad(c, -14, 14, TEAL, 0.35, -0.35); c.fill(); c.lineWidth = 1.8; c.strokeStyle = OUT; c.stroke();
    A.circ(c, 0, -58, 2.5, GOLD, OUT, 1);
    awning(c, -16, -30, 20, 6, '#c62f2f', '#efe2c4', time);
    awning(c, 16, -30, 20, 6, '#c62f2f', '#efe2c4', time + 1);
    sack(c, -30, 4, 1); sack(c, 30, 4, 1, '#c9a46c');
    coinPile(c, 22, -2, 4);
  }
};

A.tower.bazaar = (c, t, time) => {
  A.shadow(c, 0, 3, 38, 14);
  const tent = (x, y, w, h, c1, c2) => {
    A.poly(c, [[x - w / 2, y], [x, y - h], [x + w / 2, y]], A.hgrad(c, x - w / 2, x + w / 2, c1, 0.25, -0.35), OUT, 1.5);
    for (let i = -1; i <= 1; i++) A.line(c, x, y - h, x + i * w * 0.3, y, U.rgba(c2, 0.8), 2);
    A.poly(c, [[x - 4, y], [x, y - h * 0.4], [x + 4, y]], '#3a2412', OUT, 1);
  };
  tent(-18, -6, 34, 38, '#7a3fa0', '#e8c25a');
  tent(18, -4, 32, 34, '#c62f2f', '#efe2c4');
  tent(0, 6, 40, 30, '#1f8f8a', '#e8c25a');
  A.flag(c, -18, -44, 12, GOLD, time);
  A.flag(c, 18, -38, 12, TEAL, time + 1);
  // cordao de lanternas
  c.beginPath(); c.moveTo(-34, -24); c.quadraticCurveTo(0, -10, 34, -24); c.strokeStyle = '#5b3a1e'; c.lineWidth = 1; c.stroke();
  for (let i = 0; i < 5; i++) {
    const k = (i + 0.5) / 5, x = -34 + 68 * k, y = -24 + Math.sin(k * Math.PI) * 7;
    A.glow(c, x, y + 3, 6, '#ffcf5a', 0.6 + Math.sin(time * 4 + i) * 0.2);
    A.rrect(c, x - 2, y, 4, 6, 1.5, '#ffb347', OUT, 0.8);
  }
  sack(c, -34, 10, 1); coinPile(c, 32, 10, 6);
};

A.tower.treasury = (c, t, time) => {
  A.shadow(c, 0, 3, 34, 13);
  A.box(c, 0, 0, 52, 30, 14, '#b9a993');
  c.save();
  c.strokeStyle = U.rgba('#6a5638', 0.45); c.lineWidth = 1;
  for (let r = 1; r < 4; r++) { c.beginPath(); c.moveTo(-26, -r * 7.5); c.lineTo(26, -r * 7.5); c.stroke(); }
  c.restore();
  c.beginPath(); c.ellipse(0, -44, 18, 16, 0, Math.PI, 0); c.closePath();
  c.fillStyle = A.hgrad(c, -18, 18, '#f2c43c', 0.45, -0.35); c.fill(); c.lineWidth = 2; c.strokeStyle = OUT; c.stroke();
  A.ell(c, -6, -52, 4, 3, 'rgba(255,255,255,0.45)');
  A.line(c, 0, -60, 0, -68, GOLD, 2); A.circ(c, 0, -69, 2.6, GOLD, OUT, 1);
  // porta reforcada
  A.rect(c, -9, -20, 18, 20, '#5a3a20', OUT, 1.5);
  for (const yy of [-16, -8]) A.line(c, -9, yy, 9, yy, '#3a3532', 2);
  A.circ(c, 5, -10, 1.6, GOLD);
  coinPile(c, -22, 6, 6); coinPile(c, 24, 6, 5);
  const k = (time * 0.7) % 1;
  c.save(); c.globalAlpha = 1 - k;
  A.coin(c, 0, -74 - k * 14, 3.5);
  c.restore();
};

// ------------------------------------------------------------ INIMIGOS NOVOS
A.enemy.bulwark = (c, e, t) => {
  A.humanoid(c, { s: 1.12, wide: 1.1, moving: e.moving, walk: e.walk, atk: e.atkAnim, skin: '#b07a4a', body: '#8a6a3a', legs: '#4a3a2a', belt: '#3a2414', head: 'helmet', headColor: '#c48a3c', weapon: 'spear', weaponColor: '#c48a3c', boots: '#3a2414', idleAng: 0.15 });
  // escudo-torre na frente
  const flash = e.blockT > 0;
  c.save();
  c.translate(8, -15);
  A.rrect(c, -3, -13, 9, 26, 3, A.hgrad(c, -3, 6, flash ? '#ffe9a0' : '#c9903e', 0.35, -0.3), OUT, 1.6);
  A.line(c, 1.5, -11, 1.5, 11, U.shade('#c9903e', -0.35), 1.4);
  A.circ(c, 1.5, 0, 2.6, '#e8c25a', OUT, 1);
  if (flash) A.glow(c, 2, 0, 14, '#fff4c0', 0.7);
  c.restore();
};

A.enemy.saboteur = (c, e, t) => {
  A.humanoid(c, { moving: e.moving, walk: e.walk * 1.2, atk: e.atkAnim || (e.castAnim > 0 ? 0.2 : 0), skin: '#a86f45', body: '#3a3448', legs: '#262232', belt: '#a8322d', head: 'hood', headColor: '#2a2638', weapon: 'dagger', cape: '#2e2a3c' });
  // pote de fumaca nas costas
  A.circ(c, -7, -14, 4.2, '#b8653a', OUT, 1.2);
  A.rect(c, -8, -19.5, 2.4, 2.4, '#5a3a20', null);
  const sp = (t * 8) % 1;
  A.glow(c, -7, -21 - sp * 2, 4, '#ffcf5a', 0.9);
};

A.enemy.specter = (c, e, t) => {
  const bob = Math.sin(t * 3 + e.id) * 2;
  c.save();
  c.translate(0, -4 + bob);
  const wave = Math.sin(t * 6 + e.id);
  // manto que vira areia
  c.beginPath();
  c.moveTo(-7, -26);
  c.quadraticCurveTo(-10, -12, -11, 2);
  c.quadraticCurveTo(-7, -1 + wave * 2, -4, 3);
  c.quadraticCurveTo(-1, -1 - wave * 2, 2, 3);
  c.quadraticCurveTo(5, -1 + wave * 2, 9, 2);
  c.quadraticCurveTo(9, -12, 6, -26);
  c.closePath();
  const g = c.createLinearGradient(0, -28, 0, 4);
  g.addColorStop(0, '#d9c49a'); g.addColorStop(1, 'rgba(217,196,154,0.15)');
  c.fillStyle = g; c.fill(); c.lineWidth = 1.2; c.strokeStyle = 'rgba(43,26,15,0.7)'; c.stroke();
  // capuz
  A.circ(c, 0, -26, 7, '#c9b083', OUT, 1.3);
  A.ell(c, 1.5, -25, 4.5, 4, '#1a1008');
  A.circ(c, 3, -25.5, 1.2, '#7ff4ff');
  A.circ(c, -0.5, -25.5, 1.2, '#7ff4ff');
  A.glow(c, 1.5, -25.5, 6, '#7ff4ff', 0.6);
  // bracos espectrais
  A.line(c, 5, -18, 12, -12 + wave * 2, 'rgba(201,176,131,0.8)', 2.4);
  c.restore();
  // rastro de areia
  const r = U.rng(Math.floor(t * 12) + e.id);
  for (let i = 0; i < 4; i++) A.circ(c, -8 - r() * 10, -2 - r() * 8, 1 + r() * 1.5, 'rgba(217,196,154,0.6)');
};

A.enemy.brood = (c, e, t) => {
  c.save();
  c.scale(1.35, 1.35);
  A.scorpionBody(c, e, t, '#5a2a3a', '#8a4a5a', '#2e1018');
  // ovos nas costas
  for (const [x, y, r] of [[-5, -13, 3.4], [0, -14.5, 3.8], [5, -13, 3.2], [-2, -10.5, 2.8], [3, -10.5, 2.8]]) {
    A.circ(c, x, y, r, '#efe2c4', OUT, 1);
    A.circ(c, x - r * 0.3, y - r * 0.3, r * 0.3, 'rgba(255,255,255,0.6)');
  }
  c.restore();
};

A.enemy.scorpling = (c, e, t) => {
  c.save();
  c.scale(0.55, 0.55);
  A.scorpionBody(c, e, t, '#b8653a', '#d98a52', '#6a3018');
  c.restore();
};

A.enemy.ifrit = (c, e, t) => {
  const y0 = (e.flying ? -FLY_H - 14 : -10) + Math.sin(t * 1.8) * 3;
  c.save();
  c.translate(0, y0);
  const cast = e.castAnim > 0;
  A.glow(c, 0, -20, 70, '#ff7a1a', cast ? 0.55 : 0.35);
  const fl = k => Math.sin(t * 9 + k) * 3;
  // cauda de fogo
  c.beginPath();
  c.moveTo(-14, 8);
  c.quadraticCurveTo(-8, 34, -22 + fl(1), 52);
  c.quadraticCurveTo(0, 40, 14, 8);
  c.closePath();
  const tg = c.createLinearGradient(0, 4, 0, 52);
  tg.addColorStop(0, 'rgba(255,140,30,0.95)'); tg.addColorStop(1, 'rgba(255,200,80,0)');
  c.fillStyle = tg; c.fill();
  // tronco musculoso
  c.beginPath();
  c.moveTo(-20, -30); c.quadraticCurveTo(0, -38, 20, -30);
  c.quadraticCurveTo(22, -8, 12, 10); c.quadraticCurveTo(0, 14, -12, 10);
  c.quadraticCurveTo(-22, -8, -20, -30); c.closePath();
  c.fillStyle = A.hgrad(c, -20, 20, '#c8401e', 0.35, -0.35); c.fill(); c.lineWidth = 2; c.strokeStyle = OUT; c.stroke();
  A.line(c, 0, -28, 0, -8, 'rgba(90,20,5,0.6)', 1.5);
  A.line(c, -10, -18, -2, -16, 'rgba(90,20,5,0.5)', 1.3); A.line(c, 10, -18, 2, -16, 'rgba(90,20,5,0.5)', 1.3);
  A.rect(c, -13, 2, 26, 4, GOLD, OUT, 1.2);
  // bracos
  const up = cast ? -16 : 0;
  limb(c, -18, -28, -32, -14 + up, '#c8401e', 7);
  limb(c, 18, -28, 32, -14 + up, '#c8401e', 7);
  A.circ(c, -32, -14 + up, 4, GOLD, OUT, 1.2);
  A.circ(c, 32, -14 + up, 4, GOLD, OUT, 1.2);
  if (cast) { A.glow(c, -32, -20 + up, 16, '#ffcf5a', 0.9); A.glow(c, 32, -20 + up, 16, '#ffcf5a', 0.9); }
  // cabeca
  A.circ(c, 0, -44, 11, A.hgrad(c, -11, 11, '#d8502a', 0.3, -0.3), OUT, 2);
  A.poly(c, [[-8, -50], [-16, -66], [-4, -54]], '#2a1a14', OUT, 1.2);
  A.poly(c, [[8, -50], [16, -66], [4, -54]], '#2a1a14', OUT, 1.2);
  A.circ(c, -4, -45, 2, '#fff6b0'); A.circ(c, 4, -45, 2, '#fff6b0');
  A.glow(c, 0, -45, 10, '#fff2a0', 0.5);
  A.line(c, -8, -50, -2, -47, '#3a0e04', 2.2); A.line(c, 8, -50, 2, -47, '#3a0e04', 2.2);
  c.beginPath(); c.moveTo(-5, -39); c.quadraticCurveTo(0, -36, 5, -39); c.strokeStyle = '#5a1a0a'; c.lineWidth = 1.6; c.stroke();
  // barba de chamas
  c.beginPath(); c.moveTo(-6, -36); c.quadraticCurveTo(0, -24 + fl(4) * 0.5, 6, -36); c.closePath();
  c.fillStyle = 'rgba(255,190,60,0.9)'; c.fill();
  // cabelo de chamas
  for (let i = 0; i < 6; i++) {
    const x = -10 + i * 4;
    c.beginPath();
    c.moveTo(x - 3, -52);
    c.quadraticCurveTo(x + fl(i) * 0.6, -64 - (i % 2) * 6, x + 2 + fl(i + 2) * 0.8, -72 - (i % 3) * 4);
    c.quadraticCurveTo(x + 3, -60, x + 3, -52);
    c.closePath();
    c.fillStyle = i % 2 ? 'rgba(255,170,40,0.95)' : 'rgba(255,230,120,0.9)';
    c.fill();
  }
  c.restore();
};

A.unit.merc = (c, u, t) => {
  A.humanoid(c, { moving: u.moving, walk: u.walk, atk: u.atkAnim, skin: '#b9784a', body: '#7a3a2a', chest: '#a8763e', legs: '#3a2a1a', belt: '#e8c25a', head: 'turban', headColor: '#7a1a1a', weapon: 'scimitar', weaponColor: '#e8c25a', boots: '#3a2616', shield: '#8a5a32' });
};

// ------------------------------------------------------------ elementos do mapa
// escombros sobre um lote (ruinas a limpar)
A.ruinSpot = (c, x, y, hover, cost, time) => {
  if (A.ruinSprite && A.ruinSprite(c, x, y, hover, cost, time)) return;
  c.save();
  c.translate(x, y);
  c.scale(1.22, 1.3);
  A.shadow(c, 0, 3, 34, 14, 0.25);
  A.ell(c, 0, 0, 31, 15, '#9a8466', OUT, 2);
  A.deco.fallen(c, -6, 4, 0.55, () => 0.5);
  A.deco.rock(c, 14, 2, 0.55, U.rng(5), '#b8a27c');
  A.deco.rock(c, -18, -2, 0.45, U.rng(9), '#a8926c');
  A.deco.column(c, 4, -2, 0.55, U.rng(3), true);
  if (hover) {
    c.globalCompositeOperation = 'lighter';
    A.ell(c, 0, -1, 30, 14, null, 'rgba(255,240,180,0.6)', 2.5);
    c.globalCompositeOperation = 'source-over';
  }
  c.restore();
};

// comporta: alavanca + portao fechando o ramo inativo
A.lever = (c, f, time, hover) => {
  if (A.leverSprite && A.leverSprite(c, f, time, hover)) return;
  c.save();
  c.translate(f.x, f.y);
  A.shadow(c, 0, 3, 18, 7);
  A.box(c, 0, 0, 26, 10, 8, '#8a7c6a');
  const ang = (f.state ? 0.6 : -0.6) * (f.flip > 0 ? 1 - f.flip * 2 : 1);
  c.save();
  c.translate(0, -12);
  c.rotate(ang);
  A.line(c, 0, 0, 0, -26, OUT, 5.5);
  A.line(c, 0, 0, 0, -26, '#6b4423', 3.5);
  A.circ(c, 0, -27, 4.5, '#c62f2f', OUT, 1.4);
  c.restore();
  A.circ(c, 0, -12, 3.5, GOLD, OUT, 1.2);
  if (hover) A.glow(c, 0, -20, 26, '#ffe08a', 0.35);
  c.restore();
};

A.gateBar = (c, x, y, dx, dy, time) => {
  if (A.gateSprite && A.gateSprite(c, x, y, dx, dy, time)) return;
  // paliçada de estacas atravessada no caminho fechado
  const nx = -dy, ny = dx;
  const deep = Math.abs(ny) > 0.7; // caminho na horizontal: a cerca some na profundidade
  const h = deep ? 16 : 22, skew = deep ? 4 : 0;
  const stakes = [];
  for (let k = -3; k <= 3; k++) stakes.push([x + nx * k * 9 + k * skew, y + ny * k * (deep ? 8 : 7)]);
  stakes.sort((p, q) => p[1] - q[1]);
  A.shadow(c, x, y + 3, deep ? 26 : 34, deep ? 22 : 12, 0.22);
  for (const [px, py] of stakes) {
    A.poly(c, [[px - 3.5, py], [px - 3.5, py - h], [px, py - h - 6], [px + 3.5, py - h], [px + 3.5, py]], A.hgrad(c, px - 3.5, px + 3.5, WOOD_L, 0.2, -0.35), OUT, 1.3);
  }
  const f = stakes[0], l = stakes[stakes.length - 1];
  for (const off of deep ? [6, 12] : [8, 16]) {
    c.beginPath(); c.moveTo(f[0], f[1] - off); c.lineTo(l[0], l[1] - off);
    c.strokeStyle = OUT; c.lineWidth = 3.5; c.stroke();
    c.strokeStyle = '#8a6a3a'; c.lineWidth = 2; c.stroke();
  }
};

// ------------------------------------------------------------ icones extras (habilidades e alvo)
A.iconExtra = {
  // ampulheta de areia (torre em obra)
  work: (c, x, y, r, o) => {
    const w = r * 0.55, h = r * 0.8, k = ((o && o.time) || 0) % 2 / 2;
    A.rect(c, x - w - 1.5, y - h - 2.5, (w + 1.5) * 2, 3, WOOD_D, OUT, 1.2);
    A.rect(c, x - w - 1.5, y + h - 0.5, (w + 1.5) * 2, 3, WOOD_D, OUT, 1.2);
    A.poly(c, [[x - w, y - h], [x + w, y - h], [x + 1.5, y], [x + w, y + h], [x - w, y + h], [x - 1.5, y]], 'rgba(220,240,255,0.55)', OUT, 1.4);
    const top = h * (1 - k) * 0.85, bot = h * k * 0.85;
    if (top > 0.5) A.poly(c, [[x - w * top / h, y - top], [x + w * top / h, y - top], [x, y]], '#e8c27a');
    A.poly(c, [[x - w, y + h], [x + w, y + h], [x + w * (1 - bot / h), y + h - bot], [x - w * (1 - bot / h), y + h - bot]], '#e8c27a');
    A.line(c, x, y, x, y + h - bot, '#e8c27a', 1.2);
  },
  spring: (c, x, y, r) => {
    for (const [dx, dy] of [[-0.3, 0.1], [0.3, 0.1], [0, -0.3]]) {
      c.beginPath(); c.moveTo(x + dx * r, y + dy * r - r * 0.35);
      c.quadraticCurveTo(x + dx * r + r * 0.28, y + dy * r + r * 0.1, x + dx * r, y + dy * r + r * 0.25);
      c.quadraticCurveTo(x + dx * r - r * 0.28, y + dy * r + r * 0.1, x + dx * r, y + dy * r - r * 0.35);
      c.fillStyle = WATER_L; c.fill(); c.lineWidth = 1.4; c.strokeStyle = OUT; c.stroke();
    }
    A.rect(c, x + r * 0.35, y - r * 0.65, r * 0.14, r * 0.42, '#6fe06a', null);
    A.rect(c, x + r * 0.21, y - r * 0.51, r * 0.42, r * 0.14, '#6fe06a', null);
  },
  mire: (c, x, y, r) => {
    A.ell(c, x, y + r * 0.2, r * 0.8, r * 0.38, '#7a5a32', OUT, 1.6);
    A.ell(c, x - r * 0.2, y + r * 0.12, r * 0.3, r * 0.12, '#a07a48');
    A.circ(c, x + r * 0.3, y, r * 0.12, null, '#c9a46c', 1.4);
  },
  chill: (c, x, y, r) => {
    for (let i = 0; i < 3; i++) {
      const a = (i / 3) * Math.PI;
      A.line(c, x - Math.cos(a) * r * 0.7, y - Math.sin(a) * r * 0.7, x + Math.cos(a) * r * 0.7, y + Math.sin(a) * r * 0.7, OUT, 4);
      A.line(c, x - Math.cos(a) * r * 0.7, y - Math.sin(a) * r * 0.7, x + Math.cos(a) * r * 0.7, y + Math.sin(a) * r * 0.7, '#cff4ff', 2.2);
    }
  },
  burst: (c, x, y, r) => {
    A.ell(c, x, y + r * 0.5, r * 0.6, r * 0.2, '#7a5a32', OUT, 1.4);
    A.poly(c, [[x - r * 0.3, y + r * 0.5], [x - r * 0.15, y - r * 0.7], [x + r * 0.15, y - r * 0.7], [x + r * 0.3, y + r * 0.5]], WATER_L, OUT, 1.5);
    for (const s of [-1, 1]) A.circ(c, x + s * r * 0.4, y - r * 0.55, r * 0.14, WATER_L, OUT, 1);
  },
  twister: (c, x, y, r) => {
    for (let i = 0; i < 4; i++) {
      const k = i / 3;
      A.ell(c, x + (k - 0.5) * r * 0.2, y - r * 0.55 + k * r * 0.9, r * (0.7 - k * 0.45), r * 0.16, null, i % 2 ? '#e8f6ff' : '#9fc8d8', 2.4);
    }
  },
  skyward: (c, x, y, r) => {
    A.poly(c, [[x - r * 0.6, y - r * 0.3], [x, y - r * 0.05], [x + r * 0.6, y - r * 0.3], [x + r * 0.15, y + r * 0.05], [x, y + r * 0.25], [x - r * 0.15, y + r * 0.05]], '#7a5a3a', OUT, 1.4);
    A.poly(c, [[x - r * 0.18, y + r * 0.35], [x + r * 0.18, y + r * 0.35], [x, y + r * 0.75]], '#e8f6ff', OUT, 1.2);
  },
  shred: (c, x, y, r) => {
    A.poly(c, [[x - r * 0.55, y - r * 0.6], [x + r * 0.55, y - r * 0.6], [x + r * 0.5, y + r * 0.1], [x, y + r * 0.7], [x - r * 0.5, y + r * 0.1]], '#a9b0b5', OUT, 2);
    A.line(c, x - r * 0.2, y - r * 0.55, x + r * 0.05, y - r * 0.1, OUT, 2);
    A.line(c, x + r * 0.05, y - r * 0.1, x - r * 0.1, y + r * 0.35, OUT, 2);
    for (let i = 0; i < 4; i++) A.circ(c, x + r * (0.35 + i * 0.1), y + r * (-0.2 + i * 0.2), r * 0.07, '#e8c890');
  },
  blind: (c, x, y, r) => {
    A.ell(c, x, y, r * 0.75, r * 0.42, '#fff8e0', OUT, 2);
    A.circ(c, x, y, r * 0.28, '#5a4a3a');
    A.line(c, x - r * 0.75, y + r * 0.45, x + r * 0.75, y - r * 0.45, '#e8c890', 4);
  },
  warcry: (c, x, y, r) => { drum(c, x, y + r * 0.45, r * 0.55); A.line(c, x + r * 0.2, y - r * 0.45, x + r * 0.65, y - r * 0.8, '#6b4423', 2.4); },
  march: (c, x, y, r) => {
    A.poly(c, [[x - r * 0.5, y + r * 0.6], [x - r * 0.1, y - r * 0.1], [x - r * 0.5, y - r * 0.1]], '#e8c25a', OUT, 1.4);
    A.line(c, x - r * 0.6, y + r * 0.7, x + r * 0.5, y - r * 0.5, '#e3e7ea', 3);
    A.line(c, x + r * 0.6, y + r * 0.7, x - r * 0.5, y - r * 0.5, '#e3e7ea', 3);
  },
  mark: (c, x, y, r) => {
    A.circ(c, x, y, r * 0.6, null, '#e04848', 2.5);
    A.circ(c, x, y, r * 0.25, '#e04848', OUT, 1);
    for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2; A.line(c, x + Math.cos(a) * r * 0.45, y + Math.sin(a) * r * 0.45, x + Math.cos(a) * r * 0.85, y + Math.sin(a) * r * 0.85, '#e04848', 2); }
  },
  bounty: (c, x, y, r) => { A.coin(c, x - r * 0.2, y + r * 0.1, r * 0.45); A.coin(c, x + r * 0.25, y - r * 0.15, r * 0.4); },
  mercs: (c, x, y, r) => { c.translate(x, y + r * 0.7); c.scale(r / 26, r / 26); A.unit.merc(c, { moving: false, walk: 0, atkAnim: 0 }, 0); },
  caravan: (c, x, y, r) => { sack(c, x - r * 0.25, y + r * 0.4, r / 14); coinPile(c, x + r * 0.3, y + r * 0.35, 4); },
  compound: (c, x, y, r) => {
    A.coin(c, x - r * 0.25, y + r * 0.2, r * 0.4);
    A.poly(c, [[x + r * 0.1, y - r * 0.1], [x + r * 0.45, y - r * 0.6], [x + r * 0.8, y - r * 0.1]], '#6fe06a', OUT, 1.4);
    A.rect(c, x + r * 0.33, y - r * 0.12, r * 0.24, r * 0.45, '#6fe06a', OUT, 1.2);
  },
  vault: (c, x, y, r) => {
    A.rrect(c, x - r * 0.6, y - r * 0.5, r * 1.2, r, r * 0.15, '#8a8478', OUT, 2);
    A.circ(c, x, y, r * 0.28, '#c9c2b5', OUT, 1.5);
    for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2 + 0.4; A.line(c, x, y, x + Math.cos(a) * r * 0.25, y + Math.sin(a) * r * 0.25, OUT, 1.2); }
  },
  // prioridade de alvo
  prio_first: (c, x, y, r) => {
    A.poly(c, [[x - r * 0.55, y - r * 0.4], [x + r * 0.05, y], [x - r * 0.55, y + r * 0.4]], '#fff', OUT, 1.5);
    A.poly(c, [[x - r * 0.05, y - r * 0.4], [x + r * 0.55, y], [x - r * 0.05, y + r * 0.4]], '#ffd54a', OUT, 1.5);
  },
  prio_last: (c, x, y, r) => {
    A.poly(c, [[x + r * 0.55, y - r * 0.4], [x - r * 0.05, y], [x + r * 0.55, y + r * 0.4]], '#fff', OUT, 1.5);
    A.poly(c, [[x + r * 0.05, y - r * 0.4], [x - r * 0.55, y], [x + r * 0.05, y + r * 0.4]], '#ffd54a', OUT, 1.5);
  },
  prio_strong: (c, x, y, r) => { A.skullIcon(c, x, y, r * 0.62, '#ffd0c0'); A.circ(c, x, y, r * 0.8, null, '#e04848', 2); },
  prio_flying: (c, x, y, r) => {
    A.poly(c, [[x - r * 0.8, y - r * 0.15], [x, y + r * 0.15], [x + r * 0.8, y - r * 0.15], [x + r * 0.2, y + r * 0.35], [x, y + r * 0.6], [x - r * 0.2, y + r * 0.35]], '#9fd8ff', OUT, 1.5);
  },
  ruin: (c, x, y, r) => { A.deco.column(c, x, y + r * 0.6, r / 34, U.rng(3), true); },
  // tempestade de fake news: celular com balao na tela e o selo vermelho de "!"
  sandstorm: (c, x, y, r) => {
    const pw = r * 0.95, ph = r * 1.6, px = x - pw / 2 - r * 0.08, py = y - ph / 2 + r * 0.05;
    A.rrect(c, px, py, pw, ph, r * 0.2, '#2c3140', OUT, Math.max(1.2, r * 0.12));
    A.rrect(c, px + r * 0.1, py + r * 0.18, pw - r * 0.2, ph - r * 0.42, r * 0.08, '#cfe6ff');
    A.rrect(c, px + r * 0.18, py + r * 0.36, pw * 0.62, r * 0.36, r * 0.12, '#ffffff');
    A.rrect(c, px + pw * 0.3, py + r * 0.86, pw * 0.55, r * 0.32, r * 0.1, '#dcf8c6');
    A.circ(c, px + pw / 2, py + ph - r * 0.13, r * 0.07, '#8a90a0');
    const bx = px + pw - r * 0.02, by = py + r * 0.12, br = r * 0.42;
    A.circ(c, bx, by, br, '#e8423f', '#ffffff', Math.max(1, r * 0.1));
    A.line(c, bx, by - br * 0.52, bx, by + br * 0.12, '#ffffff', Math.max(1.4, br * 0.3));
    A.circ(c, bx, by + br * 0.48, Math.max(0.8, br * 0.15), '#ffffff');
  },
  gate: (c, x, y, r) => { A.lever(c, { x, y: y + r * 0.6, state: 1, flip: 0 }, 0, false); },
  high: (c, x, y, r) => {
    A.poly(c, [[x - r * 0.8, y + r * 0.5], [x - r * 0.3, y - r * 0.4], [x + r * 0.2, y + r * 0.1], [x + r * 0.45, y - r * 0.15], [x + r * 0.8, y + r * 0.5]], '#c9a06a', OUT, 1.6);
    A.poly(c, [[x, y - r * 0.75], [x + r * 0.3, y - r * 0.45], [x - r * 0.3, y - r * 0.45]], '#7fffd4', OUT, 1.2);
  },
};

// ------------------------------------------------------------ OBRA (construcao e evolucao)
// A torre sobe em fiadas dentro de um andaime, com um pedreiro martelando na beira da obra.
// Na evolucao o nivel novo sobe por baixo e substitui o antigo. A Torre de Arqueiros de sprite
// cuida da propria montagem (js/sprites.js).
const WORK_ROWS = 6;
const towerHCache = {};

// altura visivel da torre desenhada por codigo, medida uma vez num canvas fora da tela
A.towerH = (type, tier, spec) => {
  const hs = A.spriteH && A.spriteH(type, tier, spec); // torre de sprite: altura do render (js/sprites.js)
  if (hs) return hs;
  const key = type + tier + (spec || '');
  if (towerHCache[key] != null) return towerHCache[key];
  let h = 110;
  try {
    const cw = 260, by = 250;
    const cv = document.createElement('canvas');
    cv.width = cw; cv.height = by + 40;
    const c = cv.getContext('2d');
    c.translate(cw / 2, by);
    c.scale(TOWER_SCALE, TOWER_SCALE);
    A.tower[type](c, { type, tier, spec: spec || null, x: 0, y: 0, anim: 0, aimX: 1, buildT: 9, id: 1, abil: {}, units: [] }, 0);
    const d = c.getImageData(0, 0, cw, by).data;
    let top = by;
    for (let y = 0; y < by && top === by; y++) {
      for (let x = 0; x < cw; x++) if (d[(y * cw + x) * 4 + 3] > 60) { top = y; break; }
    }
    h = by - top;
  } catch (err) { /* sem DOM: fica a altura padrao */ }
  return (towerHCache[key] = h);
};

// fiadas: cada uma sobe rapido e assenta, no ritmo das marteladas
function workRise(t) {
  const p = U.clamp(t.buildT / t.buildDur, 0, 1);
  const q = U.clamp((p - 0.05) / 0.85, 0, 1) * WORK_ROWS;
  if (q >= WORK_ROWS) return 1;
  const row = Math.floor(q);
  return (row + U.easeInOut(Math.min(1, (q - row) / 0.55))) / WORK_ROWS;
}

function workTop(t) {
  const hNew = A.towerH(t.type, t.tier, t.spec);
  const hOld = t.prev ? A.towerH(t.type, t.prev.tier, t.prev.spec) : 0;
  return -Math.max(hNew, hOld) - 4;
}

function pole(c, x, y0, y1) {
  A.line(c, x, y0, x, y1, OUT, 5.2);
  A.line(c, x, y0, x, y1, WOOD, 3.4);
  A.line(c, x - 0.8, y0, x - 0.8, y1, WOOD_L, 1.1);
}

function lashing(c, x, y) {
  A.line(c, x - 2.6, y - 1.2, x + 2.6, y + 1.2, '#e2cf9a', 1.6);
  A.line(c, x - 2.6, y + 0.6, x + 2.6, y + 2.6, '#e2cf9a', 1.6);
}

// andaime: estacas de tras, ou a frente com a tabua onde fica o pedreiro
function scaffold(c, part, yl, grow, alpha) {
  const pts = part === 'back' ? [[-27, -12], [27, -12]] : [[-37, 9], [37, 9]];
  c.save();
  c.globalAlpha *= alpha;
  for (const [x, y] of pts) {
    const yt = U.lerp(y, yl - 18, grow);
    if (yt < y - 2) pole(c, x, y, yt);
  }
  if (part === 'front') {
    // travessas laterais (da estaca da frente ate a de tras), a cada 26 px
    for (const sx of [-1, 1]) {
      const yt = U.lerp(9, yl - 18, grow);
      for (let h = 22; 9 - h > yt + 6; h += 26) {
        A.line(c, sx * 37, 9 - h, sx * 27, -12 - h, OUT, 3.4);
        A.line(c, sx * 37, 9 - h, sx * 27, -12 - h, WOOD_D, 2);
        lashing(c, sx * 37, 9 - h);
      }
    }
  }
  c.restore();
}

function plank(c, y, alpha, rot) {
  c.save();
  c.globalAlpha *= alpha;
  c.translate(0, y);
  if (rot) c.rotate(rot);
  A.rrect(c, -44, -1, 88, 6, 1.5, A.hgrad(c, -44, 44, WOOD, 0.2, -0.25), OUT, 1.3);
  for (const x of [-22, 0, 22]) A.line(c, x, 0, x, 4, WOOD_D, 1);
  lashing(c, -37, 1.5); lashing(c, 37, 1.5);
  c.restore();
}

// pedreiro na tabua: o martelo desce a cada batida (t.knockT vem do motor, junto com o som)
function mason(c, x, y, t, flip) {
  c.save();
  c.translate(x, y);
  if (flip) c.scale(-1, 1);
  A.line(c, -2, 0, -2.6, -5.5, '#5a3a22', 2.6);
  A.line(c, 2, 0, 2.4, -5.5, '#5a3a22', 2.6);
  A.poly(c, [[-4.6, -4.5], [4.6, -4.5], [3.6, -12.5], [-3.6, -12.5]], '#eadfc4', OUT, 1.1);
  A.line(c, -4.1, -7.6, 4.1, -7.6, TEAL, 1.7);
  A.circ(c, -0.4, -16, 3.5, '#c98b5a', OUT, 1.1);
  A.ell(c, -0.2, -18.4, 3.9, 2.3, '#f3ecda', OUT, 1);
  const k = U.clamp(t.knockT / 0.5, 0, 1);
  const u = 1 - k;
  const lift = u < 0.72 ? U.easeInOut(u / 0.72) : 1 - Math.pow((u - 0.72) / 0.28, 2);
  const a = U.lerp(-0.7, 1.95, lift);
  const sx = -2.4, sy = -11.2, L = 7;
  const hx = sx - Math.cos(a) * L, hy = sy - Math.sin(a) * L;
  A.line(c, sx, sy, hx, hy, '#c98b5a', 2.3);
  const ex = hx - Math.cos(a) * 6, ey = hy - Math.sin(a) * 6;
  A.line(c, hx, hy, ex, ey, WOOD_D, 1.8);
  const px = -Math.sin(a) * 3, py = Math.cos(a) * 3;
  A.line(c, ex - px, ey - py, ex + px, ey + py, '#7d7d86', 3.4);
  // lascas e faisca logo depois da batida
  if (u < 0.14) {
    const e = u / 0.14;
    c.save();
    c.globalCompositeOperation = 'lighter';
    c.globalAlpha = 1 - e;
    for (let i = 0; i < 4; i++) {
      const ang = -0.4 - i * 0.75;
      A.circ(c, ex + Math.cos(ang) * (2 + e * 9), ey + Math.sin(ang) * (2 + e * 7), 1.5 * (1 - e) + 0.4, i % 2 ? '#ffe08a' : '#fff6d8');
    }
    c.restore();
  }
  c.restore();
}

function blockPile(c, n) {
  const spots = [[-48, 18], [-40, 19], [-44, 13], [-52, 13], [-48, 8]];
  for (let i = 0; i < n; i++) {
    const [x, y] = spots[i];
    A.rect(c, x - 4.5, y - 3.5, 9, 5, U.shade(SANDSTONE, i % 2 ? -0.06 : 0.04), OUT, 1);
    A.line(c, x - 3.5, y - 2.6, x + 3.5, y - 2.6, U.shade(SANDSTONE, 0.25), 0.9);
  }
}

A.drawWork = (c, t, time) => {
  if (!t.working || !t.buildDur || (A.selfBuild && A.selfBuild(t))) return false;
  const p = U.clamp(t.buildT / t.buildDur, 0, 1);
  const grow = U.easeOutBack(U.clamp(p / 0.1, 0, 1));
  const top = workTop(t), y0 = 22;
  const yl = U.lerp(y0, top, workRise(t));
  const old = t.prev ? Object.assign({}, t, { tier: t.prev.tier, spec: t.prev.spec }) : null;
  const draw = (o, clip) => {
    c.save();
    if (clip) { c.beginPath(); c.rect(-170, clip[0], 340, clip[1] - clip[0]); c.clip(); }
    c.scale(TOWER_SCALE, TOWER_SCALE);
    A.tower[t.type](c, o, time);
    c.restore();
  };
  c.save();
  c.translate(t.x, t.y);
  A.shadow(c, 0, 5, 46, 18, 0.24);
  scaffold(c, 'back', yl, grow, 1);
  // planta do nivel novo, bem clarinha
  c.save(); c.globalAlpha = 0.16; draw(t); c.restore();
  if (old) draw(old, [-400, yl]);
  draw(t, [yl, 200]);
  // poeira subindo da fiada
  c.save();
  for (let i = 0; i < 5; i++) {
    const h = Math.sin(i * 91.7 + t.id * 13.1) * 0.5 + 0.5;
    const k = (time * 0.9 + h) % 1;
    c.globalAlpha = 0.32 * (1 - k);
    A.circ(c, (h - 0.5) * 70 + Math.sin(k * 4 + i) * 4, yl - 4 - k * 18, 3 + k * 6, '#e9d6ae');
  }
  c.restore();
  scaffold(c, 'front', yl, grow, 1);
  plank(c, yl, U.clamp(p / 0.06, 0, 1));
  if (p > 0.04) mason(c, 21, yl - 1, t, false);
  blockPile(c, Math.ceil((1 - p) * 5));
  c.restore();
  return true;
};

// depois da obra: o andaime cai, a torre brilha e assenta
A.drawWorkEnd = (c, t, time) => {
  if (!t.buildDur || t.working || (A.selfBuild && A.selfBuild(t))) return;
  const k = (t.buildT - t.buildDur) / 0.5;
  if (k < 0 || k >= 1) return;
  const top = workTop(t);
  c.save();
  c.translate(t.x, t.y);
  c.save();
  c.globalCompositeOperation = 'lighter';
  c.globalAlpha = 0.5 * (1 - k);
  const sq = A.towerSquash(t);
  if (sq) c.scale(sq[0], sq[1]);
  c.scale(TOWER_SCALE, TOWER_SCALE);
  A.tower[t.type](c, t, time);
  c.restore();
  const fall = k * k, fade = Math.max(0, 1 - k * 1.7);
  for (const sx of [-1, 1]) {
    c.save();
    c.translate(sx * 37, 9);
    c.rotate(sx * fall * 1.5);
    c.globalAlpha = fade;
    pole(c, 0, 0, top - 18 - 9);
    c.restore();
  }
  plank(c, top + fall * 150, fade, fall * 0.6);
  c.restore();
};

// assentar depois da obra (e o "pulo" ao comprar habilidade)
A.towerSquash = t => {
  let s = 0;
  if (t.buildDur && !t.working) {
    const k = (t.buildT - t.buildDur) / 0.45;
    if (k >= 0 && k < 1) s = Math.sin(k * Math.PI * 2) * (1 - k) * 0.07;
  }
  if (t.popT != null && t.popT < 0.35) s = Math.sin(t.popT / 0.35 * Math.PI * 2) * (1 - t.popT / 0.35) * 0.08;
  return s ? [1 - s * 0.5, 1 + s] : null;
};
