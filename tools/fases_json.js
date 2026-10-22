// Exporta a geometria das fases (estradas ja suavizadas, lotes, agua, comportas) para o Blender montar o cenario.
// uso: node tools/fases_json.js > arte/render/cenario/fases.json
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '..', 'js');
const code = ['util.js', 'data.js', 'game.js'].map(f => fs.readFileSync(path.join(root, f), 'utf8')).join('\n');
const ctx = { console, Math, Set, Map, Float64Array, Object, Array, JSON, Number, String, Infinity, isFinite };
vm.createContext(ctx);
vm.runInContext(code + '\nthis.U=U;this.DATA=DATA;this.Game=Game;this.W=W;this.H=H;', ctx);
const { DATA, Game } = ctx;
const r1 = v => Math.round(v * 10) / 10;
const out = DATA.LEVELS.map((L, i) => {
  const g = new Game(i, { headless: true });
  return {
    idx: i, name: L.name, theme: L.theme, seed: L.seed,
    paths: g.paths.map(p => p.pts.map(q => [r1(q[0]), r1(q[1])])),
    spots: g.spots.map((s, k) => ({ x: s.x, y: s.y, high: s.high, ruin: s.ruin, low: !!s.low || L.spots[k][2] === 'l' })),
    water: L.water || [], canals: L.canals || [], rivers: L.rivers || [], pontes: L.pontes || [],
    forks: g.forks.map(f => {
      const p = g.paths[f.paths[0]], q = p.at(f.gd, {});
      const p2 = g.paths[f.paths[1]], q2 = p2.at(g.paths[f.paths[1]].ctrlD[DATA.LEVELS[i].forks[0].ctrl + 1] + 46, {});
      return { lever: [f.x, f.y], gates: [[r1(q.x), r1(q.y), q.dx, q.dy], [r1(q2.x), r1(q2.y), q2.dx, q2.dy]] };
    }),
    hero: L.hero, storm: !!L.storm, night: !!L.night, flood: !!L.flood,
  };
});
process.stdout.write(JSON.stringify(out));
