'use strict';
// Utilidades gerais (matematica, aleatoriedade, easing)

const W = 1280, H = 720;

const U = {
  TAU: Math.PI * 2,
  // achatamento vertical do alcance (perspectiva 3/4 de cima)
  YS: 0.72,
  clamp: (v, a, b) => (v < a ? a : v > b ? b : v),
  lerp: (a, b, t) => a + (b - a) * t,
  dist: (ax, ay, bx, by) => Math.hypot(bx - ax, by - ay),
  rand: (a, b) => a + Math.random() * (b - a),
  randi: (a, b) => Math.floor(a + Math.random() * (b - a + 1)),
  pick: arr => arr[Math.floor(Math.random() * arr.length)],
  chance: p => Math.random() < p,
  roll: r => r[0] + Math.random() * (r[1] - r[0]),

  inRange(dx, dy, r) {
    const ey = dy / U.YS;
    return dx * dx + ey * ey <= r * r;
  },
  rangeDist(dx, dy) {
    return Math.hypot(dx, dy / U.YS);
  },

  // PRNG com semente (mulberry32), usado na geracao do cenario
  rng(seed) {
    let s = seed >>> 0;
    return function () {
      s = (s + 0x6d2b79f5) | 0;
      let t = Math.imul(s ^ (s >>> 15), 1 | s);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  },

  segDist(px, py, ax, ay, bx, by) {
    const vx = bx - ax, vy = by - ay;
    const l2 = vx * vx + vy * vy || 1;
    const t = U.clamp(((px - ax) * vx + (py - ay) * vy) / l2, 0, 1);
    return Math.hypot(px - (ax + vx * t), py - (ay + vy * t));
  },

  easeOutCubic: t => 1 - Math.pow(1 - t, 3),
  easeInCubic: t => t * t * t,
  easeOutBack: t => {
    const c1 = 1.70158, c3 = c1 + 1;
    return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
  },
  easeInOut: t => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2),
  easeOutElastic: t => {
    if (t <= 0) return 0;
    if (t >= 1) return 1;
    return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * ((2 * Math.PI) / 3)) + 1;
  },

  // cor: clareia (amt>0) ou escurece (amt<0) um hex #rrggbb
  shade(hex, amt) {
    let n = parseInt(hex.slice(1), 16);
    let r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
    if (amt >= 0) {
      r += (255 - r) * amt; g += (255 - g) * amt; b += (255 - b) * amt;
    } else {
      r *= 1 + amt; g *= 1 + amt; b *= 1 + amt;
    }
    return '#' + ((1 << 24) | (Math.round(r) << 16) | (Math.round(g) << 8) | Math.round(b)).toString(16).slice(1);
  },
  rgba(hex, a) {
    const n = parseInt(hex.slice(1), 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
  },
  fmt(n) {
    return String(Math.floor(n));
  },
  // 0..1 que cai e quica no 1 (bandeira caindo, logo entrando)
  bounce(x) {
    const n = 7.5625, d = 2.75;
    if (x < 1 / d) return n * x * x;
    if (x < 2 / d) return n * (x -= 1.5 / d) * x + 0.75;
    if (x < 2.5 / d) return n * (x -= 2.25 / d) * x + 0.9375;
    return n * (x -= 2.625 / d) * x + 0.984375;
  },
};
