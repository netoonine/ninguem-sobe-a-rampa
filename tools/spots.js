// Analisa (e opcionalmente otimiza) a posicao dos lotes de torre em cada fase.
// Mede tudo na metrica do alcance (elipse achatada na vertical, U.YS), que e como as torres enxergam.
// uso: node tools/spots.js [fase|all] [--fix] [--json]
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '..', 'js');
const code = ['util.js', 'data.js', 'game.js'].map(f => fs.readFileSync(path.join(root, f), 'utf8')).join('\n');
const ctx = { console, Math, Set, Map, Float64Array, Object, Array, JSON, Number, String, Infinity, isFinite };
vm.createContext(ctx);
vm.runInContext(code + '\nthis.U=U;this.DATA=DATA;this.Game=Game;', ctx);
const { U, DATA, Game } = ctx;

const args = process.argv.slice(2);
const which = args[0] || 'all';
const FIX = args.includes('--fix');
const R = 150;          // alcance de uma torre de arqueiros nivel 1
const PATH_HALF = 32;   // meia largura da pista desenhada
const optNum = (k, d) => { const a = args.find(x => x.startsWith('--' + k + '=')); return a ? parseFloat(a.split('=')[1]) : d; };
const SPOT_RX = optNum('rx', 31), SPOT_RY = optNum('ry', 16);
const TOWER_W = optNum('tw', 60), TOWER_H = optNum('th', 80);

function onScreen(x, y) { return x > -10 && x < 1290 && y > -10 && y < 730; }

function samples(g) {
  const out = [];
  g.paths.forEach((p, pi) => {
    for (let d = 0; d <= p.len; d += 6) {
      const q = p.at(d, {});
      if (!onScreen(q.x, q.y)) continue;
      out.push({ x: q.x, y: q.y, pi, d, k: d / p.len });
    }
  });
  return out;
}

// folga entre a borda da pista e a borda do lote (negativa = encosta/invade a pista)
function clearance(sx, sy, pts, rx, ry) {
  rx = rx || SPOT_RX; ry = ry || SPOT_RY;
  let worst = Infinity;
  for (const p of pts) {
    const dx = p.x - sx, dy = p.y - sy, d = Math.hypot(dx, dy) || 1;
    const c = dx / d, s = dy / d;
    const rr = 1 / Math.sqrt((c * c) / (rx * rx) + (s * s) / (ry * ry));
    worst = Math.min(worst, d - PATH_HALF - rr);
  }
  return worst;
}

function stats(sx, sy, pts) {
  let dmin = Infinity, cov = 0;
  for (const p of pts) {
    const rd = U.rangeDist(p.x - sx, p.y - sy);
    if (rd < dmin) dmin = rd;
    if (rd <= R) cov += 6;
  }
  return { dmin, cov };
}

const HUD = (x, y) => (x < 400 && y < 110) || (x > 1120 && y < 80) || (x < 300 && y > 600) || (x > 420 && x < 860 && y > 640);

function analyze(li) {
  const g = new Game(li, { headless: true });
  const pts = samples(g);
  const L = DATA.LEVELS[li];
  const rows = g.spots.map((s, i) => Object.assign({ i, x: s.x, y: s.y, flag: s.high ? 'h' : s.ruin ? 'r' : '' }, stats(s.x, s.y, pts), { clr: clearance(s.x, s.y, pts) }));
  // cobertura da pista: quantos lotes alcancam cada trecho
  const covCount = pts.map(p => g.spots.filter(s => U.rangeDist(p.x - s.x, p.y - s.y) <= R).length);
  const gaps = covCount.filter(n => n === 0).length * 6, thin = covCount.filter(n => n === 1).length * 6;
  const totalLen = pts.length * 6;
  return { g, pts, L, rows, gaps, thin, totalLen, covCount };
}

function report(li, A) {
  const far = A.rows.filter(r => r.dmin > 110);
  const avg = A.rows.reduce((a, r) => a + r.dmin, 0) / A.rows.length;
  const avgCov = A.rows.reduce((a, r) => a + r.cov, 0) / A.rows.length;
  console.log(`Fase ${li + 1} ${A.L.name}: distancia media ${avg.toFixed(0)} (alcance), cobertura media ${avgCov.toFixed(0)}px, lotes longe ${far.length}/${A.rows.length}, trecho sem cobertura ${A.gaps}px, com 1 lote so ${A.thin}px (de ${A.totalLen}px)`);
  for (const r of A.rows) {
    const tag = r.dmin > 110 ? 'LONGE' : r.dmin > 95 ? 'meio longe' : '';
    console.log(`   lote ${String(r.i).padStart(2)} (${r.x},${r.y})${r.flag ? ' ' + r.flag : ''}  dist ${r.dmin.toFixed(0).padStart(3)}  cobre ${String(r.cov).padStart(4)}px  folga ${r.clr.toFixed(0).padStart(3)}  ${tag}`);
  }
}

// otimizacao global: cobre a pista inteira (com peso maior nas curvas, cruzamentos e perto da saida),
// mantendo cada lote perto da pista, sem encostar nela, em outro lote, na agua ou no HUD
const GAIN = [0, 1, 1.75, 2.3, 2.65, 2.85, 3.0];
function optimize(li, A) {
  const { pts, L } = A;
  const water = (L.water || []).map(([x, y, rx, ry]) => ({ x, y, rx: rx + 40, ry: ry + 30 }));
  const inWater = (x, y) => water.some(w => ((x - w.x) / w.rx) ** 2 + ((y - w.y) / w.ry) ** 2 < 1);
  const lever = (L.forks || []).map(f => ({ x: f.lever[0], y: f.lever[1] }));
  // botao de chamar onda (primeiro ponto da pista dentro da tela) e o texto embaixo dele
  const ents = A.g.paths.map(p => { for (let d = 0; d < p.len; d += 4) { const q = p.at(d, {}); if (q.x > 40 && q.x < 1240 && q.y > 40 && q.y < 680) return { x: q.x, y: Math.max(q.y, 104) }; } return null; }).filter(Boolean);
  const nearEntrance = (x, y) => ents.some(e => Math.hypot(e.x - x, e.y - y) < 82 || (e.y < 140 && Math.abs(Math.min(Math.max(e.x, 100), 1180) - x) < 120 && y > e.y + 50 && y < e.y + 120));
  const flags = A.rows.map(r => r.flag);
  // peso de cada trecho: avanco na pista, curvatura e encontro de caminhos
  const wts = pts.map((p, i) => {
    let w = 1 + 0.6 * p.k;
    const prev = pts[i - 2], next = pts[i + 2];
    if (prev && next && prev.pi === p.pi && next.pi === p.pi) {
      const a1 = Math.atan2(p.y - prev.y, p.x - prev.x), a2 = Math.atan2(next.y - p.y, next.x - p.x);
      let da = Math.abs(a2 - a1); if (da > Math.PI) da = 2 * Math.PI - da;
      w += Math.min(1.2, da * 6);
    }
    if (pts.some(q => q.pi !== p.pi && Math.hypot(q.x - p.x, q.y - p.y) < 20)) w += 0.5;
    return w;
  });
  const orig = A.rows.map(r => ({ x: r.x, y: r.y }));
  const cur = orig.map(o => ({ x: o.x, y: o.y }));
  const inR = (s, p) => U.rangeDist(p.x - s.x, p.y - s.y) <= R;
  const count = pts.map(p => cur.filter(s => inR(s, p)).length);
  const valid = (x, y, i) => {
    if (x < 45 || x > 1235 || y < 64 || y > 690 || HUD(x, y) || inWater(x, y)) return false;
    if (lever.some(l => Math.abs(l.x - x) < 60 && Math.abs(l.y - y) < 50)) return false;
    if (nearEntrance(x, y)) return false;
    if (flags[i] === 'h' ? clearance(x, y, pts, 54, 31) < 6 : clearance(x, y, pts) < 8) return false;
    // a torre sobe ~80px acima do lote: nao pode tapar a pista logo atras dela
    for (const p of pts) if (Math.abs(p.x - x) < TOWER_W / 2 && p.y < y && y - p.y < TOWER_H - 4) return false;
    for (let j = 0; j < cur.length; j++) {
      if (j === i) continue;
      if (Math.abs(cur[j].x - x) < Math.max(2 * SPOT_RX + 14, TOWER_W + 12) && Math.abs(cur[j].y - y) < Math.max(2 * SPOT_RY + 32, TOWER_H * 0.78)) return false;
    }
    return true;
  };
  for (let pass = 0; pass < 4; pass++) {
    for (let i = 0; i < cur.length; i++) {
      // tira o lote i da contagem
      pts.forEach((p, k) => { if (inR(cur[i], p)) count[k]--; });
      let best = null, bs = -Infinity;
      for (let dx = -110; dx <= 110; dx += 6) for (let dy = -100; dy <= 100; dy += 6) {
        const x = orig[i].x + dx, y = orig[i].y + dy;
        if (!valid(x, y, i)) continue;
        let gain = 0, dmin = Infinity;
        for (let k = 0; k < pts.length; k++) {
          const p = pts[k];
          const rd = U.rangeDist(p.x - x, p.y - y);
          if (rd < dmin) dmin = rd;
          if (rd <= R) gain += wts[k] * (GAIN[Math.min(6, count[k] + 1)] - GAIN[Math.min(6, count[k])]);
        }
        const score = gain * 6 - Math.max(0, dmin - 82) * 8 - Math.hypot(dx, dy) * 0.5;
        if (score > bs) { bs = score; best = { x, y }; }
      }
      if (best) cur[i] = best;
      pts.forEach((p, k) => { if (inR(cur[i], p)) count[k]++; });
    }
  }
  return cur;
}

const levels = which === 'all' ? DATA.LEVELS.map((_, i) => i) : [parseInt(which, 10) - 1];
const result = {};
for (const li of levels) {
  const A = analyze(li);
  report(li, A);
  if (FIX) {
    const nw = optimize(li, A);
    result[li] = nw;
    // reavalia com as posicoes novas
    const g = A.g;
    nw.forEach((p, i) => { g.spots[i].x = p.x; g.spots[i].y = p.y; });
    const pts = A.pts;
    const rows = nw.map((p, i) => Object.assign({ i }, stats(p.x, p.y, pts)));
    const far = rows.filter(r => r.dmin > 110).length;
    const avg = rows.reduce((a, r) => a + r.dmin, 0) / rows.length;
    const covCount = pts.map(p => nw.filter(s => U.rangeDist(p.x - s.x, p.y - s.y) <= R).length);
    console.log(`   -> otimizado: distancia media ${avg.toFixed(0)}, lotes longe ${far}, sem cobertura ${covCount.filter(n => n === 0).length * 6}px, com 1 lote ${covCount.filter(n => n === 1).length * 6}px`);
    nw.forEach((p, i) => { const o = A.rows[i]; if (p.x !== o.x || p.y !== o.y) console.log(`      lote ${i}: (${o.x},${o.y}) -> (${p.x},${p.y})`); });
  }
}
if (args.includes('--json')) fs.writeFileSync(path.join(__dirname, 'spots_novos.json'), JSON.stringify(result));

// trechos sem cobertura depois da otimizacao (para decidir onde criar lotes novos)
if (args.includes('--gaps')) {
  for (const li of levels) {
    const A = analyze(li);
    const nw = result[li] || A.rows.map(r => ({ x: r.x, y: r.y }));
    let run = null;
    const out = [];
    A.pts.forEach((p, k) => {
      const n = nw.filter(s => U.rangeDist(p.x - s.x, p.y - s.y) <= R).length;
      const prev = A.pts[k - 1];
      if (n === 0 && run && prev && prev.pi === p.pi) { run.len += 6; run.x1 = p.x; run.y1 = p.y; }
      else if (n === 0) { if (run) out.push(run); run = { pi: p.pi, k: p.k, len: 6, x0: p.x, y0: p.y, x1: p.x, y1: p.y }; }
      else if (run) { out.push(run); run = null; }
    });
    if (run) out.push(run);
    console.log(`Fase ${li + 1} buracos:`, out.filter(r => r.len >= 30).map(r => `caminho ${r.pi} ${Math.round(r.k * 100)}% ${r.len}px (${Math.round(r.x0)},${Math.round(r.y0)})->(${Math.round(r.x1)},${Math.round(r.y1)})`).join(' | '));
  }
}
