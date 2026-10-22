'use strict';
// Arte das torres: 4 tipos x 3 niveis + 8 especializacoes.

const WOOD = '#9a6a3c', WOOD_D = '#6b4423', WOOD_L = '#c08a52';
const SANDSTONE = '#d2b07a', STONE = '#b9a993', TEAL = '#1f8f8a', GOLD = '#e8b84a';

function post(c, x, yb, yt, col, w) {
  w = w || 5;
  A.rect(c, x - w / 2, yt, w, yb - yt, A.hgrad(c, x - w / 2, x + w / 2, col || WOOD, 0.25, -0.3), OUT, 1.4);
}

function deck(c, y, w, h, d, col) {
  A.box(c, 0, y, w, h, d, col || WOOD);
  c.save();
  c.strokeStyle = U.rgba(WOOD_D, 0.55); c.lineWidth = 1;
  for (let i = 1; i < 5; i++) {
    const xx = -w / 2 + (w / 5) * i;
    c.beginPath(); c.moveTo(xx, y - h - d); c.lineTo(xx, y - h); c.stroke();
  }
  c.restore();
}

function railing(c, y, w, h) {
  for (let i = 0; i <= 4; i++) {
    const xx = -w / 2 + (w / 4) * i;
    A.line(c, xx, y, xx, y - h, WOOD_D, 2.2);
  }
  A.line(c, -w / 2 - 1, y - h, w / 2 + 1, y - h, WOOD_L, 3);
  A.line(c, -w / 2 - 1, y - h, w / 2 + 1, y - h, OUT, 0.8);
}

function aimInfo(t) {
  const facing = (t.aimX == null ? -1 : t.aimX - t.x) >= 0 ? 1 : -1;
  return { facing, shot: t.anim > 0 };
}

function mortarGun(c, x, y, s, col, facing, recoil, bands) {
  c.save();
  c.translate(x, y + recoil * 2);
  c.scale(s * facing, s);
  A.ell(c, 0, 2, 13, 6, U.shade(col, -0.35), OUT, 1.5);
  c.save();
  c.rotate(-0.55);
  A.rrect(c, -7, -24, 15, 24, 4, A.hgrad(c, -7, 8, col, 0.4, -0.4), OUT, 1.8);
  if (bands) { A.rect(c, -7.5, -20, 16, 3, bands, OUT, 1); A.rect(c, -7.5, -9, 16, 3, bands, OUT, 1); }
  A.ell(c, 0.5, -24, 8.5, 3.6, '#1c120c', OUT, 1.6);
  c.restore();
  A.circ(c, -2, 1, 3.4, U.shade(col, -0.2), OUT, 1.2);
  c.restore();
}

function ballPile(c, x, y) {
  A.circ(c, x - 4, y, 3.4, '#2e2a28', OUT, 1);
  A.circ(c, x + 3, y, 3.4, '#2e2a28', OUT, 1);
  A.circ(c, x - 0.5, y - 4.5, 3.4, '#3a3532', OUT, 1);
}

function keg(c, x, y) {
  A.rrect(c, x - 5, y - 11, 10, 11, 3, A.hgrad(c, x - 5, x + 5, '#8a5a2e'), OUT, 1.2);
  A.line(c, x - 5, y - 8, x + 5, y - 8, '#4a3a2a', 1.2);
  A.line(c, x - 5, y - 3, x + 5, y - 3, '#4a3a2a', 1.2);
}

A.tower = {};

// ------------------------------------------------------------ ARQUEIROS
A.tower.archer = (c, t, time) => {
  if (A.archerSprite && A.archerSprite(c, t, time)) return; // sprites do Blender (js/sprites.js)
  const { facing, shot } = aimInfo(t);
  const man = (x, y, i, extra) => A.towerman(c, x, y, facing, Object.assign({ atk: shot && t.shooter === i ? 0.2 : 0 }, extra || {}));
  if (t.spec === 'ballista') return A.tower.ballista(c, t, time, facing);
  if (t.spec === 'blowgun') return A.tower.blowgun(c, t, time, facing);
  if (t.tier === 1) {
    A.shadow(c, 0, 2, 32, 12);
    post(c, -14, -8, -32, WOOD_D); post(c, 14, -8, -32, WOOD_D);
    A.line(c, -19, 0, 19, -24, WOOD_D, 2.2); A.line(c, 19, 0, -19, -24, WOOD_D, 2.2);
    post(c, -20, 2, -28); post(c, 20, 2, -28);
    deck(c, -26, 50, 6, 13);
    man(-9, -35, 0); man(9, -35, 1);
    railing(c, -32, 50, 7);
  } else if (t.tier === 2) {
    A.shadow(c, 0, 3, 32, 13);
    A.cyl(c, 0, -20, 0, 24, 10, SANDSTONE, { bricks: 7 });
    post(c, -22, -34, -64, WOOD_D, 3.5); post(c, 22, -34, -64, WOOD_D, 3.5);
    // toldo
    const wv = Math.sin(time * 2) * 1;
    c.beginPath();
    c.moveTo(-27, -64); c.lineTo(27, -64); c.lineTo(28, -56 + wv); c.quadraticCurveTo(14, -52 + wv, 0, -56 + wv); c.quadraticCurveTo(-14, -52 + wv, -28, -56 + wv);
    c.closePath(); c.fillStyle = A.hgrad(c, -28, 28, TEAL, 0.25, -0.3); c.fill(); c.lineWidth = 1.6; c.strokeStyle = OUT; c.stroke();
    for (let i = -2; i <= 2; i++) A.line(c, i * 11, -64, i * 11, -55 + wv, U.rgba('#e9dcc0', 0.7), 2.5);
    deck(c, -20, 54, 6, 13);
    man(-10, -30, 0); man(10, -30, 1);
    railing(c, -26, 54, 7);
  } else {
    A.shadow(c, 0, 3, 33, 13);
    A.cyl(c, 0, -44, 0, 25, 11, SANDSTONE, { bricks: 8 });
    A.merlonsPart(c, 0, -44, 25, 11, SANDSTONE, 'back');
    man(-9, -45, 0); man(9, -46, 1);
    A.merlonsPart(c, 0, -44, 25, 11, SANDSTONE, 'front');
    A.banner(c, 0, -34, 15, 22, TEAL, true);
    // janela estreita
    A.rect(c, 13, -26, 3, 8, '#3a2412', null);
  }
};

A.tower.ballista = (c, t, time, facing) => {
  A.shadow(c, 0, 3, 34, 13);
  A.cyl(c, 0, -42, 0, 27, 12, '#c9a670', { bricks: 8 });
  A.ell(c, 0, -42, 24, 10, '#a98a5a', OUT, 1.5);
  A.banner(c, -12, -30, 10, 16, TEAL, false);
  A.banner(c, 12, -30, 10, 16, TEAL, false);
  // balestra giratoria
  const px = 0, py = -50;
  const ax = (t.aimX == null ? t.x - 50 : t.aimX) - t.x, ay = (t.aimY == null ? t.y : t.aimY) - t.y + 30;
  const ang = Math.atan2(ay * 0.6, ax);
  const fired = t.anim > 0;
  A.rect(c, -4, -50, 8, 9, WOOD_D, OUT, 1.3);
  c.save();
  c.translate(px, py);
  c.rotate(ang);
  // coronha
  A.rrect(c, -14, -3.5, 36, 7, 2, A.hgrad(c, -14, 22, WOOD, 0.3, -0.3), OUT, 1.6);
  // arco
  c.beginPath();
  c.moveTo(14, 0);
  c.quadraticCurveTo(20, -10, 12, -21);
  c.moveTo(14, 0);
  c.quadraticCurveTo(20, 10, 12, 21);
  c.strokeStyle = OUT; c.lineWidth = 5.4; c.stroke();
  c.strokeStyle = '#7a4f2a'; c.lineWidth = 3.4; c.stroke();
  const sx = fired ? 13 : -8;
  A.line(c, 12, -21, sx, 0, '#e8e0c8', 1.2);
  A.line(c, 12, 21, sx, 0, '#e8e0c8', 1.2);
  if (!fired) {
    A.line(c, -8, 0, 26, 0, '#5b3a1e', 2.4);
    A.poly(c, [[25, -3], [31, 0], [25, 3]], '#d9dde0', OUT, 1);
  }
  A.circ(c, 0, 0, 3, GOLD, OUT, 1.2);
  c.restore();
  // operador
  A.towerman(c, -facing * 16, -44, facing, { weapon: null, head: 'helmet', headColor: '#a2adb5', body: '#6e5a3a' });
};

A.tower.blowgun = (c, t, time, facing) => {
  A.shadow(c, 0, 3, 32, 12);
  const bam = '#b9a64a';
  post(c, -15, -8, -28, U.shade(bam, -0.2), 4); post(c, 15, -8, -28, U.shade(bam, -0.2), 4);
  post(c, -20, 2, -24, bam, 4); post(c, 20, 2, -24, bam, 4);
  deck(c, -22, 52, 6, 14, '#a07a3a');
  // cabana
  A.cyl(c, 0, -60, -36, 18, 7, '#c9a066', { noTop: true });
  c.save();
  c.strokeStyle = U.rgba('#7a5a2a', 0.6); c.lineWidth = 1;
  for (let i = 0; i < 4; i++) { c.beginPath(); c.ellipse(0, -55 + i * 5, 18, 7, 0, 0.15, Math.PI - 0.15); c.stroke(); }
  c.restore();
  A.rect(c, -5, -50, 10, 12, '#3a2412', OUT, 1.2);
  A.cone(c, 0, -58, 26, 9, 26, '#d9b45a');
  for (let i = 0; i < 7; i++) {
    const a = (i / 7) * Math.PI;
    A.line(c, Math.cos(a) * 25, -58 + Math.sin(a) * 9, Math.cos(a) * 28, -52 + Math.sin(a) * 9, '#b8923e', 1.4);
  }
  // folhas
  const wv = Math.sin(time * 3) * 2;
  A.poly(c, [[-26, -58], [-34, -48 + wv], [-24, -52]], '#4f8a3c', OUT, 1);
  A.poly(c, [[26, -58], [34, -48 - wv], [24, -52]], '#4f8a3c', OUT, 1);
  const shot = t.anim > 0;
  const mk = { weapon: 'blowgun', head: 'hair', headColor: '#1a120c', band: '#4fae5c', body: '#6b8a3a', skin: '#b07a4a', aim: -0.05 };
  A.towerman(c, -11, -30, facing, Object.assign({ atk: shot && t.shooter === 0 ? 0.2 : 0 }, mk));
  A.towerman(c, 11, -30, facing, Object.assign({ atk: shot && t.shooter === 1 ? 0.2 : 0 }, mk));
  railing(c, -28, 52, 6);
};

// ------------------------------------------------------------ MAGOS
function orb(c, x, y, r, color, time) {
  const p = 0.6 + Math.sin(time * 3) * 0.2;
  A.glow(c, x, y, r * 3.2, color, 0.45 * p + 0.2);
  A.circ(c, x, y, r, color, OUT, 1.3);
  A.circ(c, x - r * 0.35, y - r * 0.35, r * 0.35, 'rgba(255,255,255,0.75)');
}

function archWindow(c, x, y, w, h, glow, time) {
  c.beginPath();
  c.moveTo(x - w / 2, y + h / 2);
  c.lineTo(x - w / 2, y - h / 2 + w / 2);
  c.arc(x, y - h / 2 + w / 2, w / 2, Math.PI, 0);
  c.lineTo(x + w / 2, y + h / 2);
  c.closePath();
  c.fillStyle = glow ? `rgba(255,${200 + Math.sin(time * 4 + x) * 30 | 0},120,0.95)` : '#2a1a12';
  c.fill(); c.lineWidth = 1.3; c.strokeStyle = OUT; c.stroke();
}

A.tower.mage = (c, t, time) => {
  const purple = '#6a3fa3';
  const cast = t.anim > 0;
  if (t.spec === 'lightning') return A.tower.lightning(c, t, time);
  if (t.spec === 'sun') return A.tower.sun(c, t, time);
  A.shadow(c, 0, 3, 30, 12);
  A.cyl(c, 0, -6, 0, 25, 10, '#a8977e');
  if (t.tier === 1) {
    A.cyl(c, 0, -34, -6, 18, 7, STONE, { bricks: 7 });
    archWindow(c, 0, -14, 8, 14, false, time);
    A.cone(c, 0, -34, 23, 8, 26, purple);
    orb(c, 0, -63, 4, cast ? '#ffd6ff' : '#c58cff', time);
  } else if (t.tier === 2) {
    A.cyl(c, 0, -46, -6, 20, 8, STONE, { bricks: 7 });
    archWindow(c, -8, -30, 6, 10, true, time);
    archWindow(c, 8, -30, 6, 10, true, time);
    archWindow(c, 0, -14, 9, 15, false, time);
    A.rect(c, -20, -47, 40, 3, GOLD, OUT, 1);
    A.cone(c, 0, -46, 25, 9, 32, purple);
    orb(c, 0, -81, 5, cast ? '#ffd6ff' : '#c58cff', time);
  } else {
    A.cyl(c, 0, -58, -6, 21, 8, '#b3a28a', { bricks: 8 });
    A.rect(c, -21, -44, 42, 3, GOLD, OUT, 1);
    A.rect(c, -21, -26, 42, 3, GOLD, OUT, 1);
    archWindow(c, 0, -35, 7, 12, true, time);
    archWindow(c, 0, -14, 9, 15, false, time);
    A.ell(c, 0, -58, 24, 9, '#8f7d66', OUT, 2);
    for (const px of [-17, 17]) A.rect(c, px - 2.5, -74, 5, 16, A.hgrad(c, px - 2.5, px + 2.5, STONE), OUT, 1.2);
    const bob = Math.sin(time * 2) * 3;
    const cy = -84 + bob;
    A.glow(c, 0, cy, 30, '#b07cff', cast ? 0.85 : 0.5);
    c.save();
    c.strokeStyle = U.rgba('#d8b8ff', 0.8); c.lineWidth = 1.5; c.setLineDash([4, 4]); c.lineDashOffset = -time * 20;
    c.beginPath(); c.ellipse(0, cy + 6, 18, 6, 0, 0, U.TAU); c.stroke();
    c.restore();
    A.poly(c, [[0, cy - 13], [7, cy], [0, cy + 11], [-7, cy]], A.hgrad(c, -7, 7, '#9c6bff', 0.5, -0.3), OUT, 1.5);
    A.line(c, 0, cy - 13, 0, cy + 11, 'rgba(255,255,255,0.5)', 1);
  }
};

A.tower.lightning = (c, t, time) => {
  A.shadow(c, 0, 3, 31, 12);
  A.cyl(c, 0, -6, 0, 25, 10, '#8a8478');
  A.cyl(c, 0, -54, -6, 20, 8, '#7d8088', { bricks: 8 });
  for (const yy of [-48, -34, -20]) A.rect(c, -20.5, yy, 41, 3.5, '#c87533', OUT, 1);
  archWindow(c, 0, -27, 7, 11, true, time);
  A.ell(c, 0, -54, 20, 8, '#5d6068', OUT, 2);
  // bobina
  A.rect(c, -3, -82, 6, 28, A.hgrad(c, -3, 3, '#c87533', 0.4, -0.3), OUT, 1.3);
  A.ell(c, 0, -66, 12, 4, null, '#c87533', 3);
  A.ell(c, 0, -74, 9, 3, null, '#c87533', 3);
  const cast = t.anim > 0;
  A.glow(c, 0, -86, cast ? 34 : 20, '#7fe8ff', cast ? 0.9 : 0.55);
  A.circ(c, 0, -86, 6, '#dffaff', OUT, 1.4);
  // faiscas
  const r = U.rng(Math.floor(time * 12) + t.id * 7);
  for (let i = 0; i < 2; i++) {
    let x = 0, y = -86;
    c.beginPath(); c.moveTo(x, y);
    const a = r() * U.TAU;
    for (let k = 0; k < 4; k++) { x += Math.cos(a) * 4 + (r() - 0.5) * 6; y += Math.sin(a) * 4 + (r() - 0.5) * 6; c.lineTo(x, y); }
    c.strokeStyle = 'rgba(200,250,255,0.9)'; c.lineWidth = 1.3; c.stroke();
  }
};

A.tower.sun = (c, t, time) => {
  A.shadow(c, 0, 3, 32, 12);
  A.box(c, 0, 0, 56, 6, 16, '#cdb07c');
  A.box(c, 0, -10, 40, 6, 12, '#d9be8a');
  // obelisco
  A.poly(c, [[-11, -22], [-7, -70], [7, -70], [11, -22]], A.hgrad(c, -11, 11, '#e2c48e', 0.25, -0.35), OUT, 1.8);
  c.save();
  c.strokeStyle = U.rgba('#8a6a3a', 0.7); c.lineWidth = 1.1;
  const glyph = [[-4, -60, 4, -60], [0, -56, 0, -50], [-4, -45, 4, -45], [-3, -40, 3, -36], [-4, -30, 4, -30]];
  for (const g of glyph) { c.beginPath(); c.moveTo(g[0], g[1]); c.lineTo(g[2], g[3]); c.stroke(); }
  c.beginPath(); c.arc(0, -53, 2.2, 0, U.TAU); c.stroke();
  c.restore();
  A.poly(c, [[-8, -70], [0, -80], [8, -70]], GOLD, OUT, 1.5);
  // disco solar
  const beam = !!t.beam;
  const k = beam ? Math.min(1, t.beamT / ((t.S && t.S.ramp) || 2.6)) : 0;
  const cy = -92 + Math.sin(time * 1.5) * 1.5;
  A.glow(c, 0, cy, 26 + k * 18, '#ffd34a', 0.45 + k * 0.45);
  for (let i = 0; i < 12; i++) {
    const a = (i / 12) * U.TAU + time * 0.6;
    A.line(c, Math.cos(a) * 12, cy + Math.sin(a) * 12, Math.cos(a) * (17 + (i % 2) * 3), cy + Math.sin(a) * (17 + (i % 2) * 3), '#f6c945', 2.2);
  }
  A.circ(c, 0, cy, 11, A.hgrad(c, -11, 11, '#ffd75a', 0.5, -0.25), OUT, 1.8);
  A.circ(c, -3, cy - 3, 3.5, 'rgba(255,255,255,0.7)');
};

// ------------------------------------------------------------ ARTILHARIA
A.tower.artillery = (c, t, time) => {
  const { facing } = aimInfo(t);
  const rec = t.anim > 0 ? Math.min(1, t.anim / 0.25) : 0;
  if (t.spec === 'mortar') return A.tower.mortar(c, t, time, facing, rec);
  if (t.spec === 'seismic') return A.tower.seismic(c, t, time);
  if (t.tier === 1) {
    A.shadow(c, 0, 3, 32, 12);
    deck(c, 0, 56, 9, 20);
    mortarGun(c, 2, -18, 0.85, '#4a4440', facing, rec);
    ballPile(c, -18, -12);
    A.towerman(c, 18 * -facing, -14, facing, { weapon: null, head: 'turban', headColor: '#e2d2b0', body: '#7a5a3a' });
  } else if (t.tier === 2) {
    A.shadow(c, 0, 3, 34, 13);
    A.cyl(c, 0, -16, 0, 30, 12, '#c4a77c', { bricks: 8 });
    A.ell(c, 0, -16, 26, 10, '#9a8060', null);
    mortarGun(c, 0, -18, 1.05, '#3e3a38', facing, rec);
    ballPile(c, -17, -16);
    keg(c, 18, -14);
    A.towerman(c, 15 * -facing, -18, facing, { weapon: null, head: 'turban', headColor: '#e2d2b0', body: '#7a5a3a' });
  } else {
    A.shadow(c, 0, 3, 35, 14);
    A.cyl(c, 0, -22, 0, 31, 13, '#c9a978', { bricks: 7 });
    A.ell(c, 0, -22, 27, 11, '#9e8462', null);
    A.merlonsPart(c, 0, -22, 31, 13, '#c9a978', 'back', 9);
    mortarGun(c, 0, -24, 1.25, '#34302e', facing, rec, '#8a6a3a');
    keg(c, -18, -18); keg(c, 19, -18);
    A.merlonsPart(c, 0, -22, 31, 13, '#c9a978', 'front', 9);
  }
  if (t.anim > 0.2) A.glow(c, 10 * facing, -50, 16, '#ffd08a', 0.6);
};

A.tower.mortar = (c, t, time, facing, rec) => {
  A.shadow(c, 0, 3, 36, 14);
  A.cyl(c, 0, -22, 0, 32, 13, '#8e826e', { bricks: 7 });
  A.ell(c, 0, -22, 28, 11, '#6a604f', null);
  A.merlonsPart(c, 0, -22, 32, 13, '#8e826e', 'back', 9);
  mortarGun(c, 0, -26, 1.55, '#b9853e', facing, rec, GOLD);
  A.merlonsPart(c, 0, -22, 32, 13, '#8e826e', 'front', 9);
  A.flag(c, -26, -26, 30, '#c62f2f', time);
  A.flag(c, 26, -26, 30, '#c62f2f', time + 1);
  if (t.anim > 0.2) A.glow(c, 14 * facing, -62, 22, '#ffd08a', 0.7);
};

A.tower.seismic = (c, t, time) => {
  A.shadow(c, 0, 3, 36, 14);
  A.cyl(c, 0, -12, 0, 32, 13, '#a4927a', { bricks: 6 });
  A.ell(c, 0, -12, 26, 10, '#7d6c56', OUT, 1.5);
  // runas no chao
  c.save();
  c.strokeStyle = U.rgba('#ffb35a', 0.4 + (t.anim > 0 ? 0.5 : 0)); c.lineWidth = 1.5;
  c.beginPath(); c.ellipse(0, -12, 18, 7, 0, 0, U.TAU); c.stroke();
  c.restore();
  post(c, -22, -8, -70, WOOD_D, 6); post(c, 22, -8, -70, WOOD_D, 6);
  A.rect(c, -28, -76, 56, 8, A.hgrad(c, -28, 28, WOOD, 0.3, -0.3), OUT, 1.6);
  let hy = -54;
  if (t.anim > 0) {
    const a = t.anim;
    if (a > 0.42) hy = U.lerp(-54, -22, U.easeInCubic((0.6 - a) / 0.18));
    else hy = U.lerp(-22, -54, U.easeInOut((0.42 - a) / 0.42));
  }
  A.line(c, 0, -68, 0, hy - 8, '#4a3a2a', 4);
  A.line(c, -8, -70, -8, -66, OUT, 2); A.line(c, 8, -70, 8, -66, OUT, 2);
  A.box(c, 0, hy + 8, 30, 12, 8, '#8a7c6a');
  A.rect(c, -15, hy - 2, 30, 3, '#c87533', null);
  A.glow(c, 0, hy + 2, 10, '#ffb35a', 0.4);
};

// ------------------------------------------------------------ QUARTEL
A.tower.barracks = (c, t, time) => {
  if (t.spec === 'lancers') return A.tower.keep(c, t, time, true);
  if (t.spec === 'monks') return A.tower.temple(c, t, time);
  if (t.tier === 1) {
    A.shadow(c, 2, 3, 32, 12);
    A.flag(c, 14, -24, 44, TEAL, time);
    // lateral
    A.poly(c, [[20, 0], [30, -10], [12, -46], [0, -36]], A.hgrad(c, 0, 30, '#d9c9a4', 0.1, -0.35), OUT, 1.6);
    // frente
    A.poly(c, [[-22, 0], [0, -36], [20, 0]], '#efe2c4', OUT, 1.8);
    c.save();
    c.beginPath(); c.moveTo(-22, 0); c.lineTo(0, -36); c.lineTo(20, 0); c.closePath(); c.clip();
    for (let i = -3; i <= 3; i++) A.line(c, i * 7, 0, 0, -36, U.rgba(TEAL, 0.75), 2.4);
    c.restore();
    A.poly(c, [[-22, 0], [0, -36], [20, 0]], null, OUT, 1.8);
    A.poly(c, [[-7, 0], [0, -18], [7, 0]], '#3a2412', OUT, 1.3);
    A.line(c, -26, 2, -22, 0, WOOD_D, 1.4); A.line(c, 24, 2, 20, 0, WOOD_D, 1.4);
  } else if (t.tier === 2) {
    A.shadow(c, 0, 4, 34, 13);
    A.box(c, 0, -6, 46, 24, 14, WOOD);
    A.poly(c, [[-27, -30], [0, -50], [27, -30], [23, -44], [0, -58], [-23, -44]], null);
    A.poly(c, [[-27, -28], [-23, -46], [23, -46], [27, -28]], A.hgrad(c, -27, 27, '#a8502e', 0.25, -0.35), OUT, 1.6);
    A.line(c, -23, -46, 23, -46, '#c86a3e', 2);
    A.flag(c, 0, -46, 22, TEAL, time);
    // paliçada
    for (let i = -6; i <= 6; i++) {
      if (Math.abs(i) <= 1) continue;
      const x = i * 4.6;
      A.poly(c, [[x - 2.3, 6], [x - 2.3, -8], [x, -12], [x + 2.3, -8], [x + 2.3, 6]], A.hgrad(c, x - 2.3, x + 2.3, WOOD_L, 0.2, -0.3), OUT, 1.1);
    }
    A.rect(c, -7, -12, 14, 18, '#3a2412', OUT, 1.3);
    A.line(c, -30, -2, 30, -2, WOOD_D, 2);
  } else {
    A.tower.keep(c, t, time, false);
  }
};

A.tower.keep = (c, t, time, lancer) => {
  const col = lancer ? '#d9b67a' : SANDSTONE;
  A.shadow(c, 0, 4, 35, 13);
  A.box(c, 0, 0, 50, 32, 16, col);
  c.save();
  c.strokeStyle = U.rgba('#7a5a2e', 0.45); c.lineWidth = 1;
  for (let r = 1; r < 4; r++) { c.beginPath(); c.moveTo(-25, -r * 8); c.lineTo(25, -r * 8); c.stroke(); }
  for (let r = 0; r < 4; r++) for (let k = 0; k < 4; k++) {
    const x = -25 + k * 14 + (r % 2) * 7;
    c.beginPath(); c.moveTo(x, -r * 8); c.lineTo(x, -r * 8 - 8); c.stroke();
  }
  c.restore();
  // ameias
  for (let i = 0; i < 6; i++) {
    const x = -25 + i * 9.4;
    A.rect(c, x, -54, 6, 6, U.shade(col, 0.05), OUT, 1.2);
  }
  // porta em arco
  c.beginPath(); c.moveTo(-8, 0); c.lineTo(-8, -14); c.arc(0, -14, 8, Math.PI, 0); c.lineTo(8, 0); c.closePath();
  c.fillStyle = '#4a2e18'; c.fill(); c.lineWidth = 1.6; c.strokeStyle = OUT; c.stroke();
  A.line(c, 0, -22, 0, 0, '#2a180c', 1.2);
  A.banner(c, -17, -30, 9, 18, lancer ? '#c62f2f' : TEAL, lancer ? 'sun' : false);
  A.banner(c, 17, -30, 9, 18, lancer ? '#c62f2f' : TEAL, lancer ? 'sun' : false);
  A.flag(c, 0, -48, 24, lancer ? GOLD : TEAL, time);
  if (lancer) {
    for (let i = 0; i < 3; i++) {
      const x = 28 + i * 3;
      A.line(c, x, 4, x - 4, -34, '#7a5230', 1.8);
      A.poly(c, [[x - 5.5, -33], [x - 4, -40], [x - 2.5, -33]], '#e3e7ea', OUT, 0.8);
    }
  }
};

A.tower.temple = (c, t, time) => {
  A.shadow(c, 0, 4, 33, 13);
  A.box(c, 0, 2, 54, 6, 16, '#d9cdb5');
  A.cyl(c, 0, -30, -8, 24, 10, '#efe6d6', { noTop: true });
  // cupula
  c.beginPath();
  c.ellipse(0, -30, 24, 22, 0, Math.PI, 0);
  c.ellipse(0, -30, 24, 10, 0, 0, Math.PI);
  c.closePath();
  c.fillStyle = A.hgrad(c, -24, 24, '#2f6fb0', 0.35, -0.35); c.fill();
  c.lineWidth = 2; c.strokeStyle = OUT; c.stroke();
  A.ell(c, -8, -42, 6, 4, 'rgba(255,255,255,0.3)');
  A.line(c, -24, -30, 24, -30, GOLD, 2.4);
  A.line(c, 0, -52, 0, -62, GOLD, 2);
  A.circ(c, 0, -64, 3, GOLD, OUT, 1.2);
  c.beginPath(); c.moveTo(-7, -8); c.lineTo(-7, -18); c.arc(0, -18, 7, Math.PI, 0); c.lineTo(7, -8); c.closePath();
  c.fillStyle = '#5a3a20'; c.fill(); c.lineWidth = 1.4; c.strokeStyle = OUT; c.stroke();
  // bandeirolas
  const cols = ['#e07a2a', '#e8c25a', '#1f8f8a', '#c62f2f', '#e8e0c8'];
  c.beginPath(); c.moveTo(-30, -10); c.quadraticCurveTo(0, 0, 30, -10); c.strokeStyle = '#5b3a1e'; c.lineWidth = 1; c.stroke();
  for (let i = 0; i < 7; i++) {
    const k = (i + 0.5) / 7;
    const x = -30 + 60 * k, y = -10 + Math.sin(k * Math.PI) * 5;
    A.poly(c, [[x - 3, y], [x + 3, y], [x, y + 6 + Math.sin(time * 4 + i) * 0.8]], cols[i % 5], OUT, 0.8);
  }
};

// separa ameias de tras e da frente (para colocar personagens no meio)
A.merlonsPart = (c, x, y, rx, ry, color, part, n) => {
  n = n || 8;
  const h = 7;
  const items = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * U.TAU + 0.2;
    const sy = Math.sin(a);
    if (part === 'back' ? sy >= 0 : sy < 0) continue;
    items.push({ sx: Math.cos(a), sy });
  }
  items.sort((p, q) => p.sy - q.sy);
  for (const it of items) {
    const mx = x + it.sx * rx * 0.93, my = y + it.sy * ry * 0.93;
    const w = 7;
    const col = it.sy > 0 ? U.shade(color, it.sx < 0 ? 0.1 : -0.22) : U.shade(color, -0.3);
    A.rect(c, mx - w / 2, my - h, w, h, col, OUT, 1.3);
    A.rect(c, mx - w / 2 + 0.7, my - h + 0.7, w - 1.4, 2, U.shade(color, 0.22), null);
  }
};

A.drawTower = (c, t, time) => {
  if (A.towerSprite && A.towerSprite(c, t, time)) return; // torre de sprite do Blender (js/sprites.js)
  if (A.drawWork && A.drawWork(c, t, time)) return; // obra em andamento (art2.js)
  c.save();
  c.translate(t.x, t.y);
  if (!(A.selfBuild && A.selfBuild(t))) {
    const sq = A.towerSquash && A.towerSquash(t);
    if (sq) c.scale(sq[0], sq[1]);
    c.scale(TOWER_SCALE, TOWER_SCALE);
  }
  A.tower[t.type](c, t, time);
  c.restore();
  if (A.drawWorkEnd) A.drawWorkEnd(c, t, time);
};

// lote vazio para construir
A.spot = (c, x, y, hover, time) => {
  if (A.spotSprite && A.spotSprite(c, x, y, hover, time)) return;
  c.save();
  c.translate(x, y);
  A.shadow(c, 0, 3, 33, 14, 0.22);
  A.ell(c, 0, 0, 31, 16, '#a88d62', OUT, 2);
  A.ell(c, 0, -1.5, 27, 13, hover ? '#d9c08c' : '#c4a978', null);
  c.save();
  c.beginPath(); c.ellipse(0, -1.5, 27, 13, 0, 0, U.TAU); c.clip();
  c.strokeStyle = U.rgba('#8a6f48', 0.55); c.lineWidth = 1.1;
  c.beginPath(); c.moveTo(-27, -1); c.lineTo(27, -2); c.moveTo(-9, -14); c.lineTo(-11, 12); c.moveTo(10, -14); c.lineTo(12, 12); c.stroke();
  c.restore();
  for (const [sx, sy] of [[-26, 3], [24, 5], [-14, 12], [16, -11]]) A.ell(c, sx, sy, 3.2, 2.2, '#8f7a5a', OUT, 1);
  A.line(c, 18, 2, 18, -22, '#6b4423', 2.2);
  const wv = Math.sin(time * 3 + x) * 1.5;
  A.poly(c, [[18, -22], [29, -19 + wv], [18, -15]], TEAL, OUT, 1.1);
  if (hover) {
    c.globalCompositeOperation = 'lighter';
    A.ell(c, 0, -1, 29, 14, null, 'rgba(255,240,180,0.6)', 2.5);
  }
  c.restore();
};
