// Simulador sem tela: joga as fases com um bot para achar bugs e calibrar o balanceamento.
// uso: node tools/sim.js [fase(1-8)|all] [vezes] [--stars=N] [--xp=N] [--plan=nome] [--chal] [--layout] [-v]
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '..', 'js');
const code = ['util.js', 'data.js', 'game.js'].map(f => fs.readFileSync(path.join(root, f), 'utf8')).join('\n');
const ctx = { console, Math, Set, Map, Float64Array, Object, Array, JSON, Number, String, Infinity, isFinite };
vm.createContext(ctx);
vm.runInContext(code + '\nthis.U=U;this.DATA=DATA;this.Game=Game;this.STEP=STEP;this.W=W;this.H=H;', ctx);
const { U, DATA, Game, STEP } = ctx;

const args = process.argv.slice(2);
const which = args[0] || 'all';
const runs = parseInt(args[1] || '3', 10);
const opt = k => { const a = args.find(x => x.startsWith('--' + k + '=')); return a ? a.split('=')[1] : null; };
const verbose = args.includes('-v');

function coverage(g, s, r) {
  let c = 0;
  for (const p of g.paths) for (let k = 0; k < p.pts.length; k += 3) {
    const [x, y] = p.pts[k];
    if (x < 0 || x > 1280 || y < 0 || y > 720) continue;
    if (U.inRange(x - s.x, y - s.y, r || 160)) c++;
  }
  return c;
}

function layout(li) {
  const L = DATA.LEVELS[li];
  const g = new Game(li, { headless: true });
  g.spots.forEach((s, i) => {
    let md = Infinity;
    for (const p of g.paths) md = Math.min(md, p.nearest(s.x, s.y).dist);
    const cov = coverage(g, s);
    let ms = Infinity, mj = -1;
    g.spots.forEach((o, j) => { if (j !== i) { const d = Math.hypot(o.x - s.x, o.y - s.y); if (d < ms) { ms = d; mj = j; } } });
    const flag = md < 52 ? 'PERTO DO CAMINHO' : md > 125 ? 'longe' : '';
    const flag2 = ms < 78 ? 'COLADO em ' + mj : '';
    const hud = (s.x < 300 && s.y > 600) || (s.x < 390 && s.y < 80) || (s.x > 1130 && s.y < 80) || (s.x > 420 && s.x < 860 && s.y > 650) ? 'HUD!' : '';
    console.log(`  spot ${i} (${s.x},${s.y})${s.high ? ' alto' : ''}${s.ruin ? ' ruina' + s.ruin : ''} caminho=${md.toFixed(0)} vizinho=${ms.toFixed(0)} cobertura=${cov} ${flag} ${flag2} ${hud}`);
  });
  g.paths.forEach((p, i) => console.log(`  caminho ${i}: ${p.len.toFixed(0)}px (~${(p.len / 38).toFixed(0)}s p/ saqueador)`));
  let hp = 0, gold = 0;
  L.waves.forEach(w => w.forEach(gr => { hp += DATA.ENEMIES[gr[0]].hp * gr[1]; gold += DATA.ENEMIES[gr[0]].gold * gr[1]; }));
  console.log(`  HP total ${hp}, ouro de abates ${Math.round(gold * (L.goldMul || 1))}, ondas ${L.waves.length}`);
}

// torres liberadas ao comecar a fase li (todas as anteriores vencidas)
function unlockedAt(li) {
  const u = DATA.START_TOWERS.slice();
  for (let i = 0; i < li; i++) if (DATA.LEVELS[i].unlock) u.push(DATA.LEVELS[i].unlock);
  return u;
}

const PLANS = {
  mix: ['archer', 'barracks', 'mage', 'artillery', 'archer', 'mage', 'cistern', 'barracks', 'artillery', 'archer', 'mage', 'windmill', 'artillery', 'archer', 'mage', 'barracks', 'archer'],
  arch: ['archer', 'barracks', 'archer', 'mage', 'archer', 'artillery', 'archer', 'mage', 'barracks', 'archer', 'mage', 'archer', 'windmill', 'archer'],
  water: ['archer', 'barracks', 'cistern', 'mage', 'mage', 'archer', 'cistern', 'mage', 'banner', 'archer', 'mage', 'barracks', 'windmill', 'archer', 'mage', 'cistern'],
  wind: ['archer', 'barracks', 'windmill', 'artillery', 'archer', 'mage', 'windmill', 'artillery', 'banner', 'archer', 'mage', 'barracks', 'artillery', 'archer', 'mage'],
  eco: ['archer', 'barracks', 'market', 'mage', 'archer', 'artillery', 'market', 'mage', 'banner', 'archer', 'windmill', 'artillery', 'mage', 'archer', 'barracks', 'mage'],
};
const SPECS = [
  { archer: 'ballista', mage: 'lightning', artillery: 'mortar', barracks: 'lancers', cistern: 'geyser', windmill: 'tornado', banner: 'drums', market: 'bazaar' },
  { archer: 'blowgun', mage: 'sun', artillery: 'seismic', barracks: 'monks', cistern: 'fountain', windmill: 'sandblast', banner: 'watch', market: 'treasury' },
];

function buyUpgrades(nStars, plan) {
  const up = { archer: 0, mage: 0, artillery: 0, barracks: 0, eng: 0, cmd: 0, spells: 0 };
  const order = ['archer', 'mage', 'barracks', 'spells', 'artillery', 'eng', 'cmd'];
  let left = nStars, guard = 0;
  while (left > 0 && guard++ < 100) {
    let bought = false;
    for (const k of order) {
      if (up[k] >= 3) continue;
      const c = DATA.UPGRADE_COST[up[k]];
      if (c <= left) { up[k]++; left -= c; bought = true; break; }
    }
    if (!bought) break;
  }
  return up;
}

function runLevel(li, o) {
  const unlocked = unlockedAt(li);
  // arsenal: as 5 primeiras torres do plano que estejam liberadas
  const loadout = [];
  for (const t of o.plan) if (unlocked.includes(t) && !loadout.includes(t) && loadout.length < (o.rules && o.rules.slots || DATA.SLOTS)) loadout.push(t);
  const g = new Game(li, { headless: true, upgrades: o.up, heroXp: o.xp, loadout, rules: o.rules });
  const plan = o.plan.filter(t => g.loadout.includes(t));
  if (!plan.length) plan.push(g.loadout[0]);
  const ranked = g.spots.map(s => ({ s, c: coverage(g, s) })).sort((a, b) => b.c - a.c);
  const used = new Set();
  const pickSpot = type => {
    const free = ranked.filter(r => !used.has(r.s) && !r.s.tower);
    if (!free.length) return null;
    if (type === 'market') return free[free.length - 1].s;
    if (type === 'banner') {
      let best = null, bs = -1;
      for (const r of free) {
        const n = g.towers.filter(t => !DATA.TOWERS[t.type].support && t.type !== 'barracks' && U.inRange(t.x - r.s.x, t.y - r.s.y, 125)).length;
        if (n > bs) { bs = n; best = r.s; }
      }
      return best;
    }
    return free[0].s;
  };
  let pi = 0, think = 0, heroPlaced = false, firstCalled = false;
  const specPick = o.specs;
  const maxT = 3600;
  while (g.state !== 'won' && g.state !== 'lost' && g.time < maxT) {
    think -= STEP;
    if (think <= 0) {
      think = 0.25;
      for (let guard = 0; guard < 4; guard++) {
        const built = g.towers.length;
        const nextType = plan[pi % plan.length];
        const nextCost = DATA.TOWERS[nextType].tiers[0].cost;
        let best = null, bc = Infinity;
        for (const t of g.towers) {
          if (t.working) continue;
          let c = null, act = null;
          if (!t.spec && t.tier < 3) { c = g.upgradeCost(t); act = () => g.upgrade(t); }
          else if (!t.spec && t.tier === 3) {
            const sp = specPick[t.type];
            c = DATA.SPECS[sp].cost; act = () => { if (g.specialize(t, sp) && sp === 'ballista') t.prio = 'strong'; };
          } else if (t.spec) {
            for (const ab of DATA.SPECS[t.spec].abilities) {
              const ac = g.abilityCost(t, ab);
              if (ac != null && ac < (c || Infinity)) { c = ac; act = () => g.buyAbility(t, ab.id); }
            }
          }
          const w = t.type === 'market' ? 0.7 : t.tier >= 3 ? 1.3 : 1;
          if (c != null && c * w < bc) { bc = c; best = act; }
        }
        const room = !g.towerLimitReached() && ranked.some(r => !r.s.tower && !used.has(r.s));
        const wantBuild = room && (built < Math.min(g.spots.length, 5 + Math.floor(g.wave / 2)) || nextCost <= bc * 0.6);
        if (wantBuild) {
          const s = pickSpot(nextType);
          if (s) {
            const extra = s.ruin || 0;
            if (g.gold >= nextCost + extra) {
              if (extra) g.clearRuin(s);
              if (g.build(s, nextType)) { used.add(s); pi++; continue; }
            }
          }
        }
        if (!wantBuild && best && g.gold >= bc) { best(); continue; }
        break;
      }
      if (!heroPlaced && !g.hero.disabled) {
        const b = g.towers.find(t => t.type === 'barracks');
        if (b) { g.moveHero(b.rally.x + 30, b.rally.y); heroPlaced = true; }
      }
      // comporta: manda a coluna para o ramo mais bem defendido
      for (let k = 0; k < g.forks.length; k++) {
        const f = g.forks[k];
        const score = f.paths.map(pi2 => {
          const p = g.paths[pi2];
          let sc = 0;
          for (let d = f.d; d < p.len; d += 20) {
            const q = p.at(d, {});
            for (const t of g.towers) if (!DATA.TOWERS[t.type].noTarget && U.inRange(q.x - t.x, q.y - t.y, t.S.range)) sc += t.invested;
          }
          return sc;
        });
        const want = score[1] > score[0] ? 1 : 0;
        if (f.state !== want) g.toggleFork(k);
      }
      if (!firstCalled && (g.towers.length >= 3 || g.gold < 70)) { g.callWave(); firstCalled = true; }
      if (o.early && g.countdown > 0 && g.countdown < g.countdownMax - 4 && g.enemies.length < 6) g.callWave();
      if (!g.noSpells && g.spells.fury.cd <= 0) {
        const boss = g.enemies.find(e => e.T.boss && g.targetable(e));
        const c = boss || g.densest(640, 360, 4000, false, 55);
        if (c && (boss || g.enemiesIn(c.x, c.y, 55, false).length >= 4)) g.castSpell('fury', c.x, c.y);
      }
      if (!g.noSpells && g.spells.riders.cd <= 0) {
        let front = null;
        for (const e of g.enemies) if (!e.flying && g.targetable(e) && e.d / e.path.len > 0.55 && (!front || e.d / e.path.len > front.d / front.path.len)) front = e;
        if (front) g.castSpell('riders', front.x, front.y);
      }
    }
    g.update(STEP);
  }
  if (verbose) for (const e of g.enemies) if (e.T.boss) console.log('     chefe', e.type, 'vida', Math.round(e.hp), 'progresso', Math.round(100 * e.d / e.path.len) + '%');
  return { leaks: g.leaks, state: g.state, lives: g.lives, stars: g.stars, time: g.time, wave: g.wave, gold: g.gold, towers: g.towers.map(t => (t.spec || t.type + t.tier)).join(','), xp: Math.round(g.heroXp), kills: g.stats.kills, income: g.stats.income, loadout: g.loadout.join(',') };
}

const levels = which === 'all' ? DATA.LEVELS.map((_, i) => i) : which.split(',').map(x => parseInt(x, 10) - 1);
if (args.includes('--layout')) {
  for (const li of levels) { console.log(`Fase ${li + 1}: ${DATA.LEVELS[li].name}`); layout(li); }
  process.exit(0);
}
const planNames = opt('plan') ? opt('plan').split(',') : Object.keys(PLANS);
const chal = args.includes('--chal');
for (const li of levels) {
  const xp = opt('xp') != null ? parseInt(opt('xp'), 10) : [0, 150, 600, 1500, 2600, 3500, 4300, 5000][li];
  const nStars = opt('stars') != null ? parseInt(opt('stars'), 10) : [0, 3, 6, 9, 11, 14, 17, 20][li];
  const rules = chal ? DATA.LEVELS[li].challenge.rules : null;
  console.log(`\nFase ${li + 1}: ${DATA.LEVELS[li].name}${chal ? ' [DESAFIO ' + DATA.LEVELS[li].challenge.name + ']' : ''} (estrelas ${nStars}, xp ${xp}, torres ${unlockedAt(li).join('/')})`);
  for (const pn of planNames) {
    const plan = PLANS[pn];
    const up = buyUpgrades(nStars, plan);
    for (let si = 0; si < SPECS.length; si++) {
      const res = [];
      for (let r = 0; r < runs; r++) res.push(runLevel(li, { plan, specs: SPECS[si], up, xp, early: r % 2 === 1, rules }));
      const wins = res.filter(r => r.state === 'won').length;
      const avgL = (res.reduce((a, r) => a + r.lives, 0) / res.length).toFixed(1);
      console.log(`  ${pn.padEnd(5)}/spec${si}: vitorias ${wins}/${runs}  vidas medias ${avgL}  [${res.map(r => r.state[0] + r.lives + '@w' + r.wave).join(' ')}]  t=${res[0].time.toFixed(0)}s${res[0].income ? ' renda=' + res[0].income : ''}`);
      if (verbose) { console.log('     arsenal:', res[0].loadout, ' torres:', res[0].towers); console.log('     vazou:', res.map(r => r.leaks.join(' ')).join(' | ')); }
    }
  }
}
