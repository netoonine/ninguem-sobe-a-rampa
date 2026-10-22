'use strict';
// Motor do jogo: simulacao pura, sem desenho. Roda igual no navegador e no Node (simulador).

const LANE = 13;      // deslocamento lateral maximo dentro do caminho
const FLY_H = 34;     // altura de voo (visual)
const STEP = 1 / 60;
const MAGE_CHARGE = 0.4; // s de carga visivel do cristal antes do disparo

// altura do ponto de disparo de cada torre (tier 1..3, spec A, spec B)
const TOWER_TOP = DATA.TOWER_TOP;

// prioridades de alvo das torres
const PRIOS = ['first', 'last', 'strong', 'flying'];
const PRIO_NAMES = { first: 'Primeiro', last: 'Último', strong: 'Mais forte', flying: 'Voadores' };

class PathLine {
  constructor(ctrl) {
    const pts = [];
    const n = ctrl.length;
    const ctrlIdx = [];
    for (let i = 0; i < n - 1; i++) {
      ctrlIdx.push(pts.length);
      const p0 = ctrl[Math.max(0, i - 1)], p1 = ctrl[i], p2 = ctrl[i + 1], p3 = ctrl[Math.min(n - 1, i + 2)];
      const steps = Math.max(2, Math.ceil(Math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / 5));
      for (let s = 0; s < steps; s++) {
        const t = s / steps, t2 = t * t, t3 = t2 * t;
        const f = (a, b, c, d) => 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3);
        pts.push([f(p0[0], p1[0], p2[0], p3[0]), f(p0[1], p1[1], p2[1], p3[1])]);
      }
    }
    pts.push(ctrl[n - 1].slice());
    ctrlIdx.push(pts.length - 1);
    this.pts = pts;
    this.cum = new Float64Array(pts.length);
    for (let i = 1; i < pts.length; i++) {
      this.cum[i] = this.cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    }
    this.len = this.cum[pts.length - 1];
    // distancia percorrida em cada ponto de controle (usado nas bifurcacoes)
    this.ctrlD = ctrlIdx.map(k => this.cum[k]);
  }
  at(d, out) {
    out = out || {};
    const pts = this.pts, cum = this.cum;
    d = U.clamp(d, 0, this.len);
    let lo = 0, hi = pts.length - 1;
    while (hi - lo > 1) {
      const mid = (lo + hi) >> 1;
      if (cum[mid] <= d) lo = mid; else hi = mid;
    }
    const a = pts[lo], b = pts[hi];
    const sl = cum[hi] - cum[lo] || 1;
    const t = (d - cum[lo]) / sl;
    out.x = a[0] + (b[0] - a[0]) * t;
    out.y = a[1] + (b[1] - a[1]) * t;
    out.dx = (b[0] - a[0]) / sl;
    out.dy = (b[1] - a[1]) / sl;
    return out;
  }
  nearest(x, y) {
    let best = Infinity, bi = 0;
    const pts = this.pts;
    for (let i = 0; i < pts.length; i++) {
      const dx = pts[i][0] - x, dy = pts[i][1] - y;
      const d2 = dx * dx + dy * dy;
      if (d2 < best) { best = d2; bi = i; }
    }
    return { d: this.cum[bi], x: pts[bi][0], y: pts[bi][1], dist: Math.sqrt(best) };
  }
}

class Enemy {
  constructor(g, type, pathIdx, d0) {
    const T = DATA.ENEMIES[type];
    this.id = g.nextId++;
    this.type = type;
    this.T = T;
    this.pathIdx = pathIdx;
    this.path = g.paths[pathIdx];
    this.d = d0 || 0;
    this.lane = T.big ? U.rand(-0.15, 0.15) : U.rand(-0.85, 0.85);
    // bossHp da fase: chefes que vieram de fases mais avancadas do motor herdado
    this.hp = this.maxHp = Math.round(T.hp * (g.hpMul || 1) * (T.boss && g.L && g.L.bossHp ? g.L.bossHp : 1));
    this.flying = !!T.flying;
    this.x = 0; this.y = 0;
    this.slowF = 1; this.slowT = 0; this.stunT = 0;
    this.poisonDps = 0; this.poisonT = 0; this.burnDps = 0; this.burnT = 0;
    this.armorRed = 0; this.armorRedT = 0;
    this.wetT = 0; this.blindT = 0; this.markT = 0; this.markMul = 0; this.groundT = 0;
    this.pushRes = 0; this.revealed = false; this.seenBurrow = false;
    this.blocker = null;
    this.cd = U.rand(0.2, 0.8);
    this.abT = T.heal ? T.heal.cd * 0.5 : T.summon ? T.summon.cd * 0.6 : T.burrow ? T.burrow.every * U.rand(0.5, 1) : T.wormBurrow ? T.wormBurrow.every : 0;
    this.fsT = T.firestorm ? T.firestorm.cd * 0.5 : 0;
    this.sabT = T.sabotage ? U.rand(1, 2.5) : 0;
    this.burrowed = false;
    this.dead = false; this.reached = false;
    this.facing = 1; this.moving = true;
    this.walk = Math.random() * 10;
    this.atkAnim = 0; this.castAnim = 0; this.hurtT = 0; this.blockT = 0;
    this.trampleT = 0;
    this.fdone = 0;
  }
}

class Unit {
  constructor(g, o) {
    this.id = g.nextId++;
    this.kind = o.kind;
    this.tier = o.tier || 1;
    this.x = o.x; this.y = o.y;
    this.rx = o.rx != null ? o.rx : o.x;
    this.ry = o.ry != null ? o.ry : o.y;
    this.ox = o.ox || 0; this.oy = o.oy || 0;
    this.maxHp = o.hp; this.hp = o.hp;
    this.dmg = o.dmg; this.armor = o.armor || 0; this.rate = o.rate || 1;
    this.speed = o.speed || 75; this.guard = o.guard || 62;
    this.dodge = o.dodge || 0;
    this.owner = o.owner || null;
    this.slot = o.slot || 0;
    this.life = o.life || 0;
    this.target = null; this.cd = 0; this.dead = false; this.respawnT = 0; this.idleT = 0;
    this.atkAnim = 0; this.hurtT = 0; this.facing = 1; this.moving = false; this.order = null;
    this.walk = Math.random() * 10;
    this.abT = {};
    this.charged = false;
  }
}

class Game {
  constructor(levelIdx, opts = {}) {
    this.levelIdx = levelIdx;
    this.L = DATA.LEVELS[levelIdx];
    this.headless = !!opts.headless;
    this.mute = !!opts.mute;
    this.mode = opts.mode || 'normal';
    this.rules = Object.assign({}, opts.rules || {});
    this.up = Object.assign({ archer: 0, mage: 0, artillery: 0, barracks: 0, eng: 0, cmd: 0, charm: 0, spells: 0 }, opts.upgrades || {});
    // torres que podem ser construidas nesta partida
    let allowed = opts.loadout ? opts.loadout.slice() : DATA.TOWER_ORDER.slice();
    if (this.rules.only) allowed = allowed.filter(t => this.rules.only.includes(t));
    if (this.rules.ban) allowed = allowed.filter(t => !this.rules.ban.includes(t));
    this.loadout = DATA.TOWER_ORDER.filter(t => allowed.includes(t));
    this.paths = this.L.paths.map(p => new PathLine(p));
    this.spots = this.L.spots.map(([x, y, f, cost], i) => ({ i, x, y, tower: null, high: f === 'h', low: f === 'l', ruin: f === 'r' ? (cost || 60) : 0 }));
    this.forks = (this.L.forks || []).map(f => ({ paths: f.paths, d: this.paths[f.paths[0]].ctrlD[f.ctrl], gd: this.paths[f.paths[0]].ctrlD[f.ctrl + 1] + 46, state: f.state || 0, x: f.lever[0], y: f.lever[1], cd: 0, flip: 0 }));
    this.gold = Math.round(this.L.gold * (this.rules.startGold || 1)) + (this.up.cmd >= 3 ? 50 : 0);
    this.lives = this.maxLives = this.rules.lives || this.L.lives || 20;
    this.time = 0;
    this.nextId = 1;
    this.enemies = []; this.towers = []; this.units = []; this.projs = []; this.zones = [];
    this.fx = []; this.sounds = []; this.timers = []; this.texts = []; this.events = [];
    this.wave = 0;
    // ondas do modo: campanha/desafio usam as da fase; heroico, ferro e correnteza montam as suas (makeWaves)
    this.hpMul = (this.rules.hpMul || 1) * (this.L.hpMul || 1);
    this.waves = this.makeWaves();
    this.totalWaves = this.mode === 'endless' ? Infinity : this.waves.length;
    this.queue = [];
    this.countdown = -1; this.countdownMax = 1;
    this.state = 'prewave';
    this.stars = 0;
    this.seen = new Set(opts.seen || []);
    this.announce = [];
    this.stats = { kills: 0, earned: 0, spent: 0, leaked: 0, income: 0 };
    this.leaks = [];
    // tempestade de areia
    this.stormCfg = this.L.storm ? Object.assign({}, this.L.storm) : null;
    if (this.stormCfg && this.rules.stormMul) {
      this.stormCfg.every /= this.rules.stormMul;
      this.stormCfg.first /= this.rules.stormMul;
    }
    this.stormT = this.stormCfg ? this.stormCfg.first : 0;
    // cheia da varzea: a agua sobe de tempos em tempos (flood 0..1); acima da metade, os lotes baixos alagam
    this.floodCfg = this.L.flood || null;
    this.floodT = this.floodCfg ? this.floodCfg.first : 0;
    this.floodLeft = 0; this.flood = 0; this.floodWarned = false;
    this.stormLeft = 0; this.stormWarned = false; this.stormGustT = 0;
    const spCd = this.up.spells >= 3 ? 0.8 : 1;
    this.spells = {
      fury: { cd: 0, max: DATA.SPELLS.fury.cd * spCd },
      riders: { cd: 0, max: DATA.SPELLS.riders.cd * spCd },
      stampede: { cd: 0, max: DATA.SPELLS.stampede.cd },
    };
    // Encanto (libertacoes) e os bichos libertados que podem voltar no Estouro da Mata
    this.charm = 0; this.charmMul = 1;
    this.freed = [];
    this.herd = [];
    this.noSpells = !!this.rules.noSpells;
    // heroi escolhido no mapa (DATA.HEROES) e os talentos dele (indice 0/1 por nivel de DATA.TALENT_LVLS)
    this.heroId = DATA.HEROES[opts.hero] ? opts.hero : 'jaci';
    this.H = DATA.HEROES[this.heroId];
    this.talents = opts.talents || [];
    this.heroXp = opts.heroXp || 0;
    this.hero = this.makeHero(this.L.hero[0], this.L.hero[1]);
    this.charmMul = 1 + (this.H.charm || 0) + (this.up.charm >= 1 ? 0.25 : 0);
    if (this.rules.noHero) { this.hero.disabled = true; this.hero.dead = true; }
    else this.units.push(this.hero);
    this._tmp = {};
  }

  // ------------------------------------------------------------ utilidades
  sfx(name, vol) { if (!this.headless && !this.mute) this.sounds.push({ name, vol: vol == null ? 1 : vol }); }
  addFx(o) { if (!this.headless) { o.t = 0; this.fx.push(o); } }
  text(x, y, str, color, size) { if (!this.headless) this.fx.push({ kind: 'text', x, y, str, color: color || '#ffe08a', size: size || 18, t: 0, T: 1.1 }); }
  later(delay, fn) { this.timers.push({ t: this.time + delay, fn }); }
  hitY(e) { return e.y - (e.flying ? FLY_H : e.T.size * 0.75); }
  visible(e) { return e.x > -8 && e.x < W + 8 && e.y > -8 && e.y < H + 8; }
  targetable(e) { return !e.dead && !e.reached && !e.untargetable && (!e.burrowed || e.seenBurrow) && this.visible(e); }
  // torres so miram em quem enxergam (espectros precisam ser revelados)
  seeable(e) { return this.targetable(e) && (!e.T.stealth || e.revealed); }
  stormOn() { return this.stormLeft > 0; }
  // noite: fase noturna ou, na Correnteza, 5 ondas de dia e 5 de noite
  isNight() {
    if (this.L.night || (this.mode === 'endless' && Math.floor(this.wave / 5) % 2 === 1)) return true;
    // o Coracao da Fumaca escurece o ceu enquanto bate
    return !!(this.L.bossNight && this.enemies.some(e => e.T.final && !e.dead));
  }
  flooded(spot) { return !!(spot && spot.low && this.flood > 0.5); }
  stormK() {
    if (!this.stormCfg || this.stormLeft <= 0) return 0;
    const el = this.stormCfg.dur - this.stormLeft;
    return Math.min(1, el / 1.5, this.stormLeft / 1.5);
  }
  canBuildType(type) { return this.loadout.includes(type); }
  towerLimitReached() { return this.rules.maxTowers != null && this.towers.length >= this.rules.maxTowers; }

  // soma dos talentos escolhidos com este id (so os de nivel ja alcancado pelo heroi)
  tal(id) {
    let v = 0;
    const lvl = this.hero ? this.hero.level : this.heroLevelFor(this.heroXp);
    DATA.TALENT_LVLS.forEach((need, i) => {
      const pick = this.talents[i];
      if (pick == null || lvl < need) return;
      const T = this.H.talents[i][pick];
      if (T && T.id === id) v += T.v;
    });
    return v;
  }

  heroLevelFor(xp) {
    const t = DATA.HERO_XP;
    let l = 1;
    for (let i = 1; i < t.length; i++) if (xp >= t[i]) l = i + 1;
    return l;
  }

  makeHero(x, y) {
    const H = this.H;
    const u = new Unit(this, { kind: 'hero', x, y, hp: 1, dmg: [1, 1], armor: H.armor, rate: H.rate, speed: H.speed, guard: H.guard });
    u.heroId = this.heroId;
    u.sk = H.sprite;
    u.level = 0;
    this.applyHeroLevel(u, true);
    u.abT = { whirl: 3, hawk: 2, call: 4, trail: 3, herb: 1, bless: 2, heal: 3, flare: 4, firetrail: 5 };
    return u;
  }

  applyHeroLevel(u, full) {
    const H = this.H;
    const lvl = this.heroLevelFor(this.heroXp);
    if (lvl === u.level) return false;
    const up = u.level > 0;
    u.level = lvl;
    const ratio = u.maxHp > 1 ? u.hp / u.maxHp : 1;
    u.maxHp = Math.round((H.hp + H.hpLvl * (lvl - 1)) * (1 + this.tal('hp')));
    u.hp = full || up ? u.maxHp : u.maxHp * ratio;
    const dk = 1 + this.tal('dmg');
    u.dmg = [(H.dmg[0] + H.dmgLvl * (lvl - 1)) * dk, (H.dmg[1] + H.dmgLvl * (lvl - 1) * 1.4) * dk];
    u.armor = Math.min(0.6, H.armor + 0.015 * (lvl - 1));
    return up;
  }

  gainXp(a) {
    const max = DATA.HERO_XP[DATA.HERO_XP.length - 1];
    if (this.heroXp >= max || this.hero.disabled) return;
    this.heroXp = Math.min(max, this.heroXp + a * 0.25);
    if (this.applyHeroLevel(this.hero, false)) {
      this.text(this.hero.x, this.hero.y - 46, 'Nível ' + this.hero.level + '!', '#7fffd4', 22);
      this.addFx({ kind: 'levelup', x: this.hero.x, y: this.hero.y, T: 1 });
      this.sfx({ n: 'levelup', x: this.hero.x });
    }
  }

  // ------------------------------------------------------------ torres
  abLvl(t, id) { return (t.abil && t.abil[id]) || 0; }
  abVal(t, id) {
    const l = this.abLvl(t, id);
    if (!l || !t.spec) return 0;
    const ab = DATA.SPECS[t.spec].abilities.find(a => a.id === id);
    return ab ? ab.vals[l - 1] : 0;
  }

  towerStats(t) {
    const up = this.up;
    const src = t.spec ? DATA.SPECS[t.spec] : DATA.TOWERS[t.type].tiers[t.tier - 1];
    const s = Object.assign({}, src);
    if (s.dmg) s.dmg = s.dmg.slice();
    if (s.dps) s.dps = s.dps.slice();
    const mulDmg = m => {
      if (s.dmg) { s.dmg[0] *= m; s.dmg[1] *= m; }
      if (s.dps) { s.dps[0] *= m; s.dps[1] *= m; }
    };
    if (t.type === 'archer') {
      if (up.archer >= 1) s.range *= 1.1;
      if (up.archer >= 2) mulDmg(1.15);
      if (up.archer >= 3) s.rate *= 0.89;
    } else if (t.type === 'mage') {
      if (up.mage >= 1) mulDmg(1.1);
      if (up.mage >= 2) s.range *= 1.08;
      if (up.mage >= 3) s.frost = true;
    } else if (t.type === 'artillery') {
      if (up.artillery >= 1 && s.radius) s.radius *= 1.12;
      if (up.artillery >= 2) mulDmg(1.15);
      if (up.artillery >= 3) s.range *= 1.1;
    } else if (t.type === 'barracks') {
      if (up.barracks >= 1) s.hp *= 1.15;
      if (up.barracks >= 2) s.armor += 0.1;
      if (up.barracks >= 3) s.respawn *= 0.7;
      if (t.spec === 'lancers') {
        const v = this.abVal(t, 'shield');
        s.armor += v; s.hp *= 1 + v;
      }
      s.armor = Math.min(0.8, s.armor);
      s.hp = Math.round(s.hp);
    } else if (t.type === 'cistern') {
      if (up.eng >= 1) s.wet += 2;
      if (up.eng >= 3) s.range *= 1.1;
    } else if (t.type === 'windmill') {
      if (up.eng >= 2) { s.push *= 1.25; mulDmg(1.1); }
      if (up.eng >= 3) s.range *= 1.1;
    } else if (t.type === 'banner') {
      if (up.cmd >= 1) s.dmgB += 0.05;
    } else if (t.type === 'market') {
      if (up.cmd >= 2) s.income = Math.round(s.income * 1.2);
    }
    // terreno elevado: +15% de alcance (tambem na aura do estandarte e no quartel)
    if (t.spot && t.spot.high && s.range) s.range *= 1.15;
    return s;
  }

  towerTop(t) {
    const arr = TOWER_TOP[t.type];
    if (!t.spec) return arr[t.tier - 1];
    return arr[DATA.TOWERS[t.type].specs.indexOf(t.spec) + 3];
  }

  build(spot, type) {
    const cost = DATA.TOWERS[type].tiers[0].cost;
    if (spot.tower || spot.ruin || this.flooded(spot) || this.gold < cost || !this.canBuildType(type) || this.towerLimitReached()) return null;
    this.gold -= cost;
    this.stats.spent += cost;
    const t = {
      id: this.nextId++, type, tier: 1, spec: null, abil: {}, x: spot.x, y: spot.y, spot,
      invested: cost, cd: 0.4, anim: 0, aimX: spot.x - 1, shooter: 0, shots: 0, abT: {}, buildT: 0,
      units: [], beam: null, beamT: 0, prio: 'first', disabledT: 0, bDmg: 0, bRange: 0, bRate: 0,
      working: false, buildDur: 0, prev: null, popT: 9, knockT: 0,
    };
    spot.tower = t;
    this.towers.push(t);
    t.S = this.towerStats(t);
    t.E = t.S;
    if (type === 'barracks') t.rally = this.defaultRally(t);
    this.sfx({ n: 'build', x: t.x });
    this.addFx({ kind: 'dust', x: t.x, y: t.y, T: 0.7, r: 40 });
    this.startWork(t, DATA.BUILD_TIME);
    return t;
  }

  // obra (construcao ou evolucao): a torre nao age ate terminar
  working(t) { return t.working; }

  startWork(t, dur) {
    t.buildT = 0;
    t.buildDur = this.quickBuild ? 0 : dur;
    t.knockT = 0.35;
    t.working = true;
    if (!t.buildDur) this.finishWork(t);
  }

  finishWork(t) {
    if (!t.working) return;
    t.working = false;
    t.buildT = Math.max(t.buildT, t.buildDur);
    t.cd = Math.min(t.cd, 0.3);
    if (t.type === 'barracks') {
      if (!t.units.length) this.makeSoldiers(t);
      else this.refreshSoldiers(t);
    }
    if (this.quickBuild) return;
    this.sfx({ n: t.prev ? 'upgrade' : 'built', x: t.x });
    this.addFx({ kind: 'sparkle', x: t.x, y: t.y - 30, T: 0.9 });
  }

  // martelos durante a obra (som e lascas)
  workTick(t, dt) {
    t.knockT -= dt;
    if (t.knockT > 0) return;
    t.knockT = U.rand(0.42, 0.62);
    if (t.buildT < t.buildDur - 0.3) this.sfx({ n: 'hammer', x: t.x }, 0.45);
  }

  clearRuin(spot) {
    if (!spot.ruin || this.gold < spot.ruin) return false;
    this.gold -= spot.ruin;
    this.stats.spent += spot.ruin;
    spot.ruin = 0;
    this.sfx({ n: 'rubble', x: spot.x });
    this.addFx({ kind: 'dust', x: spot.x, y: spot.y, T: 0.9, r: 50 });
    this.addFx({ kind: 'dirt', x: spot.x, y: spot.y - 6, T: 0.7, big: true });
    return true;
  }

  upgradeCost(t) {
    if (t.spec || t.tier >= 3) return null;
    return DATA.TOWERS[t.type].tiers[t.tier].cost;
  }

  upgrade(t) {
    const cost = this.upgradeCost(t);
    if (cost == null || this.gold < cost || t.working) return false;
    this.gold -= cost; this.stats.spent += cost;
    t.invested += cost;
    t.prev = { tier: t.tier, spec: t.spec };
    t.tier++;
    this.afterChange(t);
    return true;
  }

  specialize(t, specId) {
    if (t.spec || t.tier < 3 || t.working) return false;
    const S = DATA.SPECS[specId];
    if (!S || S.base !== t.type || this.gold < S.cost) return false;
    this.gold -= S.cost; this.stats.spent += S.cost;
    t.invested += S.cost;
    t.prev = { tier: t.tier, spec: t.spec };
    t.spec = specId;
    t.tier = 4;
    this.afterChange(t);
    if (specId === 'bazaar') t.rally = this.defaultRally(t);
    return true;
  }

  abilityCost(t, ab) {
    const l = this.abLvl(t, ab.id);
    return l >= 3 ? null : ab.costs[l];
  }

  buyAbility(t, abId) {
    if (!t.spec || t.working) return false;
    const ab = DATA.SPECS[t.spec].abilities.find(a => a.id === abId);
    const cost = ab && this.abilityCost(t, ab);
    if (cost == null || this.gold < cost) return false;
    this.gold -= cost; this.stats.spent += cost;
    t.invested += cost;
    t.abil[abId] = this.abLvl(t, abId) + 1;
    if (!t.abT[abId]) t.abT[abId] = 1;
    this.afterChange(t, true);
    return true;
  }

  afterChange(t, small) {
    t.S = this.towerStats(t);
    t.E = t.S;
    if (small) {
      t.popT = 0;
      if (t.type === 'barracks') this.refreshSoldiers(t);
      this.sfx({ n: 'ability', x: t.x });
      return;
    }
    // evolucao: os soldados do quartel so recebem o nivel novo quando a obra termina
    t.beam = null;
    this.sfx({ n: 'build', x: t.x });
    this.addFx({ kind: 'dust', x: t.x, y: t.y, T: 0.7, r: 40 });
    this.startWork(t, DATA.UPGRADE_TIME);
  }

  // antes da 1a onda, ou cancelando a construcao em andamento: reembolso total
  sellValue(t) {
    return this.wave === 0 || (t.working && !t.prev) ? t.invested : Math.floor(t.invested * 0.6);
  }

  sell(t) {
    const v = this.sellValue(t);
    this.gold += v;
    for (const u of t.units) { this.releaseTarget(u); u.removed = true; }
    this.units = this.units.filter(u => !u.removed);
    t.spot.tower = null;
    this.towers = this.towers.filter(x => x !== t);
    this.sfx({ n: 'sell', x: t.x });
    this.addFx({ kind: 'dust', x: t.x, y: t.y, T: 0.8, r: 46 });
    this.text(t.x, t.y - 40, '+' + v, '#ffd54a');
  }

  // prioridade de alvo: alterna entre as opcoes que fazem sentido para a torre
  prioOptions(t) {
    if (DATA.TOWERS[t.type].noTarget) return [];
    const ground = t.type === 'artillery';
    return PRIOS.filter(p => !(ground && p === 'flying'));
  }
  cyclePrio(t) {
    const opts = this.prioOptions(t);
    if (!opts.length) return null;
    t.prio = opts[(opts.indexOf(t.prio) + 1) % opts.length];
    this.sfx('click', 0.6);
    return t.prio;
  }

  // ------------------------------------------------------------ quartel
  defaultRally(t) {
    let best = null, bd = Infinity;
    const R = (t.S && t.S.range) || 150;
    for (const p of this.paths) {
      for (let i = 0; i < p.pts.length; i += 2) {
        const [x, y] = p.pts[i];
        if (x < 10 || x > W - 10 || y < 10 || y > H - 10) continue;
        const dx = x - t.x, dy = y - t.y;
        if (!U.inRange(dx, dy, R * 0.9)) continue;
        const d = Math.hypot(dx, dy);
        if (d < bd) { bd = d; best = { x, y }; }
      }
    }
    return best || { x: t.x, y: t.y + 40 };
  }

  canRally(t, x, y) {
    if (!U.inRange(x - t.x, y - t.y, t.S.range)) return false;
    for (const p of this.paths) if (p.nearest(x, y).dist < 42) return true;
    return false;
  }

  setRally(t, x, y) {
    if (!this.canRally(t, x, y)) return false;
    t.rally = { x, y };
    this.layoutRally(t);
    for (const u of t.units) this.releaseTarget(u);
    this.sfx({ n: 'rally', x });
    this.addFx({ kind: 'flag', x, y, T: 0.8 });
    return true;
  }

  soldierOpts(t) {
    const S = t.S;
    return {
      kind: t.spec || 'soldier', tier: t.tier, hp: S.hp, dmg: S.dmg, armor: S.armor, rate: S.rate,
      speed: 78, guard: 64, dodge: S.dodge || 0,
    };
  }

  makeSoldiers(t) {
    const o = this.soldierOpts(t);
    for (let i = 0; i < 3; i++) {
      const u = new Unit(this, Object.assign({}, o, { x: t.x + (i - 1) * 6, y: t.y + 10, owner: t, slot: i }));
      t.units.push(u);
      this.units.push(u);
    }
    this.layoutRally(t);
  }

  layoutRally(t) {
    const off = [[0, -11], [-15, 9], [15, 9]];
    t.units.forEach((u, i) => {
      u.rx = t.rally.x; u.ry = t.rally.y;
      u.ox = off[i][0]; u.oy = off[i][1];
    });
  }

  refreshSoldiers(t) {
    const o = this.soldierOpts(t);
    for (const u of t.units) {
      u.kind = o.kind; u.tier = o.tier;
      u.maxHp = o.hp; u.hp = o.hp;
      u.dmg = o.dmg; u.armor = o.armor; u.rate = o.rate; u.dodge = o.dodge;
      if (u.dead) {
        u.dead = false;
        u.x = t.x; u.y = t.y + 10;
      }
    }
  }

  // ------------------------------------------------------------ comportas
  toggleFork(i) {
    const f = this.forks[i];
    if (!f || f.cd > 0) return false;
    f.state = 1 - f.state;
    f.cd = 1.2; f.flip = 0.5;
    this.sfx({ n: 'gate', x: f.x });
    this.addFx({ kind: 'dust', x: f.x, y: f.y + 6, T: 0.5, r: 18 });
    return true;
  }

  // ------------------------------------------------------------ ondas
  canCallWave() {
    return this.wave < this.totalWaves && (this.state === 'prewave' || this.countdown > 0);
  }

  callWave() {
    if (!this.canCallWave()) return 0;
    let bonus = 0;
    if (this.state !== 'prewave' && this.countdown > 0) {
      bonus = Math.round(this.countdown * 2);
      this.gold += bonus;
      this.stats.earned += bonus;
      // chamar cedo tambem adianta os feiticos
      for (const k in this.spells) this.spells[k].cd = Math.max(0, this.spells[k].cd - this.countdown * 0.5);
    }
    this.startWave(this.wave);
    return bonus;
  }

  waveEntrances(i) {
    const idx = new Set();
    const w = this.waveAt(i);
    if (!w) return [];
    for (const g of w) {
      const p = g[4] == null ? 0 : g[4];
      if (p < 0) this.paths.forEach((_, k) => idx.add(k)); else idx.add(p);
    }
    return [...idx];
  }

  // composicao da onda; com pathSet, so o que entra por esses caminhos
  waveSummary(i, pathSet) {
    const w = this.waveAt(i);
    if (!w) return [];
    const m = new Map();
    const np = this.paths.length;
    for (const g of w) {
      const [type, n, , , p = 0] = g;
      let k = n;
      if (pathSet) {
        if (p >= 0) k = pathSet.includes(p) ? n : 0;
        else { k = 0; for (let j = 0; j < n; j++) if (pathSet.includes(j % np)) k++; }
      }
      if (k > 0) m.set(type, (m.get(type) || 0) + k);
    }
    return [...m.entries()].sort((a, b) => DATA.ENEMIES[b[0]].hp * b[1] - DATA.ENEMIES[a[0]].hp * a[1]);
  }

  startWave(i) {
    const w = this.waveAt(i);
    this.wave = i + 1;
    if (this.mode === 'endless') this.hpMul = 1 + 0.07 * i;   // correnteza: cada onda mais forte
    this.state = 'running';
    this.countdown = -1;
    for (const g of w) {
      const [type, n, gap, delay = 0, p = 0] = g;
      for (let k = 0; k < n; k++) {
        let pi = p;
        if (p === -1) pi = k % this.paths.length;
        else if (p === -2) pi = U.randi(0, this.paths.length - 1);
        this.queue.push({ t: this.time + delay + k * gap, type, p: pi });
      }
      this.markSeen(type);
    }
    this.queue.sort((a, b) => a.t - b.t);
    this.sfx(i === this.totalWaves - 1 ? 'hornBig' : 'horn');
    this.payIncome();
  }

  waveAt(i) {
    if (this.mode === 'endless' && !this.waves[i]) this.waves[i] = this.endlessWave(i);
    return this.waves[i];
  }

  // ondas de cada modo a partir das da fase: [tipo, quantidade, intervalo, atraso, caminho]
  makeWaves() {
    const base = this.L.waves;
    if (this.mode === 'heroic') {
      // 30% mais bichos e mais juntos; no fim, a ultima onda de novo, reforcada (elite)
      const ws = base.map(w => w.map(([t, n, gap, d = 0, p = 0]) => [t, Math.ceil(n * 1.3), gap * 0.9, d, p]));
      ws.push(ws[ws.length - 1].map(([t, n, gap, d, p]) => [t, Math.ceil(n * 1.25), gap * 0.85, d, p]));
      return ws;
    }
    if (this.mode === 'iron') {
      // tudo numa onda so: as ondas da campanha uma atras da outra, sem pausa para respirar
      const one = [];
      let off = 0;
      for (const w of base) {
        let end = 0;
        for (const [t, n, gap, d = 0, p = 0] of w) {
          one.push([t, n, gap * 0.85, off + d, p]);
          end = Math.max(end, d + n * gap * 0.85);
        }
        off += end + 4;
      }
      return [one];
    }
    if (this.mode === 'endless') return [];
    return base;
  }

  // Correnteza: a onda i escolhe bichos cada vez mais fortes da mata toda; chefe a cada 5 ondas
  endlessWave(i) {
    const types = Object.keys(DATA.ENEMIES).filter(k => !DATA.ENEMIES[k].boss && !DATA.ENEMIES[k].noEndless);
    types.sort((a, b) => DATA.ENEMIES[a].hp - DATA.ENEMIES[b].hp);
    const bosses = Object.keys(DATA.ENEMIES).filter(k => DATA.ENEMIES[k].boss && !DATA.ENEMIES[k].noEndless);
    const rng = U.rng(1000 + i * 7919);
    const hi = Math.min(types.length, 3 + i), lo = Math.max(0, hi - 6);
    const pick = () => types[lo + Math.floor(rng() * (hi - lo))];
    const w = [];
    const groups = 2 + Math.min(3, Math.floor(i / 4));
    for (let k = 0; k < groups; k++) {
      const t = pick(), T = DATA.ENEMIES[t];
      const n = Math.max(2, Math.round((5 + i * 0.9) * Math.min(1.6, 40 / Math.max(12, T.hp)) ));
      w.push([t, n, Math.max(0.35, 1.3 - i * 0.03), k * 3, -1]);
    }
    if ((i + 1) % 5 === 0 && bosses.length) w.push([bosses[Math.floor(i / 5) % bosses.length], 1, 0, 6, 0]);
    return w;
  }

  markSeen(type) {
    if (!this.seen.has(type)) { this.seen.add(type); this.announce.push(type); }
  }

  // mercados pagam quando a onda comeca
  payIncome() {
    for (const t of this.towers) {
      if (t.type !== 'market' || t.disabledT > 0) continue;
      const S = t.S;
      let v = S.income + this.abVal(t, 'caravan');
      if (t.spec === 'treasury') {
        const rate = this.abVal(t, 'compound') || S.interest;
        const cap = this.abVal(t, 'vault') || S.cap;
        v += Math.min(cap, Math.floor(this.gold * rate));
      }
      this.gold += v;
      this.stats.earned += v;
      this.stats.income += v;
      this.text(t.x, t.y - 50, '+' + v, '#ffd54a', 18);
      this.addFx({ kind: 'coins', x: t.x, y: t.y - 30, T: 1.1 });
      this.sfx({ n: 'coin', x: t.x }, 0.8);
    }
  }

  spawn(type, p, d0) {
    const e = new Enemy(this, type, p, d0);
    for (let k = 0; k < this.forks.length; k++) if ((d0 || 0) >= this.forks[k].d) e.fdone |= 1 << k;
    this.placeEnemy(e);
    this.enemies.push(e);
    return e;
  }

  // ------------------------------------------------------------ feiticos e heroi
  canCast(id) {
    const sp = this.spells[id];
    if (!sp || sp.cd > 0 || this.noSpells) return false;
    return id !== 'stampede' || this.charm >= this.stampedeCost();
  }

  stampedeCost() { return this.up.charm >= 3 ? 45 : DATA.SPELLS.stampede.cost; }

  // bichos da manada: os ultimos libertados (mais recente primeiro); sem nenhum ainda, os bichos de chao da fase
  herdPool() {
    if (this.freed.length) return this.freed.slice().reverse();
    const out = [];
    for (const w of this.waves) for (const gr of w) {
      const T = DATA.ENEMIES[gr[0]];
      if (!T.boss && !T.flying && !out.includes(gr[0])) out.push(gr[0]);
    }
    return out.length ? out : ['jackal'];
  }

  castSpell(id, x, y) {
    const sp = this.spells[id];
    if (!this.canCast(id) || this.state === 'won' || this.state === 'lost') return false;
    if (id === 'fury') {
      const S = DATA.SPELLS.fury;
      const n = S.bolts + (this.up.spells >= 1 ? 2 : 0);
      for (let i = 0; i < n; i++) {
        const a = (i / n) * U.TAU + U.rand(-0.4, 0.4), r = i === 0 ? 0 : U.rand(18, 42);
        this.later(0.12 + i * 0.2, () => this.furyStrike(x + Math.cos(a) * r, y + Math.sin(a) * r * 0.75));
      }
    } else if (id === 'riders') {
      const S = DATA.SPELLS.riders;
      const m = this.up.spells >= 2 ? 1.3 : 1;
      const n = S.n;
      for (let i = 0; i < n; i++) {
        const u = new Unit(this, {
          kind: 'rider', x: x + (i ? 14 : -14), y: y - 6, rx: x, ry: y, ox: i ? 14 : -14, oy: i ? 6 : -6,
          hp: Math.round(S.hp * m), dmg: [S.dmg[0] * m, S.dmg[1] * m], armor: S.armor, rate: 0.9, speed: 90, guard: 75, life: S.life,
        });
        this.units.push(u);
        this.addFx({ kind: 'dust', x: u.x, y: u.y, T: 0.6, r: 26 });
      }
      this.sfx({ n: 'riders', x });
    } else if (id === 'stampede') {
      // os bichos surgem no ponto da estrada mais perto do clique e correm contra o fluxo, rumo a entrada
      const S = DATA.SPELLS.stampede;
      let best = null;
      this.paths.forEach((p, i) => {
        const n = p.nearest(x, y);
        if (!best || n.dist < best.dist) best = { i, d: n.d };
      });
      const pool = this.herdPool();
      const n = S.n + (this.up.charm >= 2 ? 2 : 0);
      for (let k = 0; k < n; k++) {
        const type = pool[k % pool.length];
        this.herd.push({ id: this.nextId++, type, T: DATA.ENEMIES[type], path: best.i, d: best.d + 26 + k * 18, lane: U.rand(-0.9, 0.9), run: -k * 18, hit: new Set(), x, y, facing: 1, hdx: 0, hdy: 0 });
      }
      this.charm -= this.stampedeCost();
      this.addFx({ kind: 'dust', x, y, T: 0.8, r: 40 });
      this.sfx({ n: 'riders', x });
      this.sfx({ n: 'stampede', x });
    }
    sp.cd = sp.max;
    return true;
  }

  // Estouro da Mata: cada bicho corre pela estrada para tras e atropela uma vez cada possuido que encontra
  updateHerd(dt) {
    if (!this.herd.length) return;
    const S = DATA.SPELLS.stampede;
    const m = this.up.spells >= 2 ? 1.3 : 1;
    for (const h of this.herd) {
      const v = S.speed * dt;
      h.run += v;
      if (h.run < 0) continue;
      h.d -= v;
      const p = this.paths[h.path];
      const q = p.at(Math.max(0, h.d), this._tmp);
      h.x = q.x - q.dy * h.lane * LANE;
      h.y = q.y + q.dx * h.lane * LANE;
      h.hdx = -q.dx; h.hdy = -q.dy;
      if (Math.abs(q.dx) > 0.15) h.facing = -q.dx >= 0 ? 1 : -1;
      for (const e of this.enemies) {
        if (h.hit.has(e.id) || !this.targetable(e)) continue;
        if (e.flying && !h.T.flying) continue;
        if (!U.inRange(e.x - h.x, e.y - h.y, 14 + e.T.size)) continue;
        h.hit.add(e.id);
        this.damage(e, U.roll(S.dmg) * m, 'phys');
        if (!e.dead && !e.T.boss) {
          e.d = Math.max(0, e.d - S.push);
          this.stun(e, S.stun);
        }
        this.addFx({ kind: 'hit', x: e.x, y: this.hitY(e), T: 0.3 });
      }
      if (h.run >= S.dist || h.d <= 0) h.done = true;
    }
    this.herd = this.herd.filter(h => !h.done);
  }

  furyStrike(x, y) {
    const S = DATA.SPELLS.fury;
    this.addFx({ kind: 'skybolt', x, y, T: 0.45 });
    this.addFx({ kind: 'scorch', x, y, T: 4 });
    this.sfx({ n: 'thunder', x });
    for (const e of this.enemies) {
      if (!this.targetable(e)) continue;
      if (U.inRange(e.x - x, e.y - y, S.radius)) this.damage(e, U.roll(S.dmg), 'true', null, 'shock');
    }
  }

  moveHero(x, y) {
    const h = this.hero;
    if (h.disabled) return;
    x = U.clamp(x, 20, W - 20); y = U.clamp(y, 40, H - 16);
    h.rx = x; h.ry = y;
    if (h.dead) return;
    this.releaseTarget(h);
    h.order = { x, y };
    this.sfx('heroMove');
  }

  // ------------------------------------------------------------ combate
  // tag: 'shock' (raios), 'fire' (fogo), 'water' (agua)
  damage(e, amt, type, src, tag) {
    if (e.dead) return 0;
    let a = amt;
    if (type === 'phys') a *= 1 - Math.max(0, e.T.armor - e.armorRed);
    else if (type === 'magic') a *= 1 - e.T.mres;
    if (e.wetT > 0) {
      if (tag === 'shock') a *= 1.8;
      else if (type === 'magic') a *= 1.25;
      if (tag === 'fire') a *= 0.5;
      if (e.T.fire) a *= 1.4;
    }
    if (e.T.fire) {
      if (tag === 'fire') a = 0;
      else if (tag === 'water') a *= 3;
    }
    if (e.markT > 0) a *= 1 + e.markMul;
    e.hp -= a;
    e.hurtT = 0.12;
    if (src && src.kind === 'hero') this.gainXp(a);
    if (e.hp <= 0) this.kill(e);
    return a;
  }

  // escudo frontal: flecha que vem da frente perde quase todo o dano
  shieldMul(e, sx, sy) {
    const fs = e.T.frontShield;
    if (!fs || e.stunT > 0) return 1;
    const p = e.path.at(e.d, this._tmp);
    const dot = (sx - e.x) * p.dx + (sy - e.y) * p.dy;
    if (dot <= 0) return 1;
    e.blockT = 0.35;
    return 1 - fs;
  }

  kill(e) {
    if (e.dead) return;
    e.dead = true;
    e.hp = 0;
    let gold = e.blessed ? 0 : e.T.gold * (this.L.goldMul || 1);
    const bounty = this.bountyAt(e.x, e.y);
    if (bounty) gold *= 1 + bounty;
    gold = Math.round(gold);
    this.gold += gold;
    this.stats.earned += gold;
    this.stats.kills++;
    e.blocker = null;
    // libertacao: Encanto e o bicho entra na manada do Estouro da Mata (chefes nao correm na manada)
    const C = DATA.CHARM;
    const ck = (this.charmMul + this.tal('charm')) * (e.blessed ? 3 : 1);
    this.charm = Math.min(C.max, this.charm + (e.T.boss ? C.boss : e.T.big ? C.big : C.gain) * ck);
    if (!e.T.boss) {
      this.freed = this.freed.filter(t => t !== e.type);
      this.freed.push(e.type);
      if (this.freed.length > 6) this.freed.shift();
    }
    // fx longo o bastante para a libertacao (fumaca sai e o bicho corre para a mata; js/inimigos.js)
    this.addFx({ kind: 'corpse', e: { type: e.type, x: e.x, y: e.y, facing: e.facing, flying: e.flying, walk: e.walk }, x: e.x, y: e.y, T: e.T.boss ? 2.0 : 1.5 });
    this.addFx({ kind: 'coin', x: e.x, y: e.y - 20, T: 0.9, n: gold });
    this.sfx({ n: e.T.boss ? 'bossDie' : e.T.big ? 'bigDie' : 'die', x: e.x }, 0.7);
    if (e.T.boss && !e.T.final) this.sfx({ n: 'bossFreed', x: e.x }, 0.8);
    if (e.T.boss) {
      // chefe derrotado: chuva de confete nas cores das duas chapas (js/satira.js)
      this.addFx({ kind: 'confetti', x: e.x, y: e.y, r: 90, T: 1.6 });
      this.addFx({ kind: 'shake', T: 0.6, amp: 8 });
    }
    if (e.T.final) {
      this.events.push({ kind: 'heartFreed' });
      this.charm = DATA.CHARM.max;
    }
    if (e.T.split) {
      const S = e.T.split;
      for (let i = 0; i < S.n; i++) {
        const s = this.spawn(S.type, e.pathIdx, Math.max(0, e.d - 6 - i * 7));
        s.fdone = e.fdone;
        s.stunT = 0.3;
      }
      this.markSeen(S.type);
      this.addFx({ kind: 'dirt', x: e.x, y: e.y, T: 0.6 });
      this.sfx({ n: 'splat', x: e.x }, 0.7);
    }
  }

  slow(e, f, dur) {
    if (e.T.boss) f = 1 - (1 - f) * 0.5;
    e.slowF = e.slowT > 0 ? Math.min(e.slowF, f) : f;
    e.slowT = Math.max(e.slowT, dur);
  }

  stun(e, dur) {
    if (e.T.boss || e.dead) return;
    if (e.stunT <= 0) this.addFx({ kind: 'stars', e, T: dur });
    e.stunT = Math.max(e.stunT, dur);
  }

  freeze(e, dur) {
    if (e.T.boss || e.dead) return;
    this.addFx({ kind: 'ice', e, T: dur });
    e.stunT = Math.max(e.stunT, dur);
    e.frozenT = dur;
    this.sfx({ n: 'freeze', x: e.x }, 0.6);
  }

  poison(e, dps, dur, armorRed) {
    e.poisonDps = Math.max(e.poisonT > 0 ? e.poisonDps : 0, dps);
    e.poisonT = Math.max(e.poisonT, dur);
    if (armorRed) { e.armorRed = Math.max(e.armorRed, armorRed); e.armorRedT = dur; }
  }

  shred(e, v, dur) {
    e.armorRed = Math.max(e.armorRedT > 0 ? e.armorRed : 0, v);
    e.armorRedT = Math.max(e.armorRedT, dur);
  }

  wet(e, dur) {
    e.wetT = Math.max(e.wetT, dur);
    if (e.burnT > 0) { e.burnT = 0; this.addFx({ kind: 'steam', x: e.x, y: this.hitY(e), T: 0.6 }); }
  }

  burn(e, dps, dur) {
    if (e.wetT > 0 || e.T.fire) return;
    e.burnDps = Math.max(e.burnT > 0 ? e.burnDps : 0, dps);
    e.burnT = Math.max(e.burnT, dur);
  }

  blind(e, dur) {
    if (e.T.boss) dur *= 0.5;
    e.blindT = Math.max(e.blindT, dur);
  }

  // voador derrubado: fica no chao por alguns segundos
  ground(e, dur) {
    if (!e.T.flying || e.dead) return;
    if (e.T.boss) dur *= 0.5;
    if (e.groundT <= 0) {
      this.addFx({ kind: 'dust', x: e.x, y: e.y, T: 0.6, r: 26 });
      this.sfx({ n: 'thud', x: e.x }, 0.6);
    }
    e.groundT = Math.max(e.groundT, dur);
    e.flying = false;
  }

  push(e, px) {
    if (e.dead || e.reached) return;
    if (e.T.boss) px *= 0.25;
    else if (e.T.big) px *= 0.5;
    px *= Math.max(0.25, 1 - e.pushRes);
    e.pushRes = Math.min(0.75, e.pushRes + 0.25);
    e.d = Math.max(0, e.d - px);
    if (e.blocker) { this.releaseTarget(e.blocker); e.blocker = null; }
    this.placeEnemy(e);
  }

  findTarget(x, y, range, ground, prio) {
    prio = prio || 'first';
    let best = null, bs = Infinity;
    for (const e of this.enemies) {
      if (!this.seeable(e)) continue;
      if (ground && e.flying) continue;
      if (!U.inRange(e.x - x, e.y - y, range)) continue;
      const rem = e.path.len - e.d;
      let s;
      if (prio === 'last') s = -rem;
      else if (prio === 'strong') s = -e.hp * 10 + rem * 0.01;
      else if (prio === 'flying') s = (e.flying ? -1e6 : 0) + rem;
      else s = rem;
      if (s < bs) { bs = s; best = e; }
    }
    return best;
  }

  enemiesIn(x, y, r, ground) {
    const out = [];
    for (const e of this.enemies) {
      if (!this.targetable(e)) continue;
      if (ground && e.flying) continue;
      if (U.inRange(e.x - x, e.y - y, r)) out.push(e);
    }
    return out;
  }

  densest(x, y, range, ground, r) {
    const list = this.enemiesIn(x, y, range, ground);
    let best = null, bn = 0;
    for (const e of list) {
      let n = 0;
      for (const o of list) if (U.inRange(o.x - e.x, o.y - e.y, r)) n++;
      if (n > bn) { bn = n; best = e; }
    }
    return best;
  }

  predict(e, t) {
    if (e.blocker && e.blocker.target === e && U.dist(e.x, e.y, e.blocker.x, e.blocker.y) < e.T.size + 26) return { x: e.x, y: e.y };
    if (e.stunT > 0) return { x: e.x, y: e.y };
    const p = e.path.at(e.d + e.T.speed * e.slowF * t, {});
    return { x: p.x - p.dy * e.lane * LANE, y: p.y + p.dx * e.lane * LANE };
  }

  // look 'cash': a mala do Mensalao estoura em notas e moedas; sem look, o barril de petroleo estoura em oleo
  explode(x, y, r, dmgR, src, big, look) {
    for (const e of this.enemiesIn(x, y, r, true)) {
      const d = U.rangeDist(e.x - x, e.y - y);
      this.damage(e, U.roll(dmgR) * (1 - 0.5 * Math.min(1, d / r)), 'phys', src);
    }
    if (look === 'cash') {
      // torre: so desenho (na Verde-Amarela o caixote do Laranjao estoura em suco, js/satira.js)
      this.addFx({ kind: 'cash', x, y, r, T: big ? 1.0 : 0.9, torre: true });
      this.sfx({ n: 'coin', x }, 0.5);
    } else this.addFx({ kind: 'explosion', x, y, r, T: big ? 0.8 : 0.6 });
    this.sfx({ n: big ? 'boomBig' : 'boom', x }, 0.8);
  }

  // ------------------------------------------------------------ auras (estandartes) e revelacao
  updateAuras(dt) {
    for (const t of this.towers) { t.bDmg = 0; t.bRange = 0; t.bRate = 0; }
    const banners = [];
    for (const b of this.towers) {
      if (b.type !== 'banner') continue;
      if (b.warT > 0) b.warT -= dt;
      if (b.disabledT > 0 || b.working) continue;
      banners.push(b);
      const S = b.S, war = b.warT > 0 ? 0.4 : 0;
      for (const t of this.towers) {
        if (t === b || DATA.TOWERS[t.type].support || t.type === 'barracks') continue;
        if (!U.inRange(t.x - b.x, t.y - b.y, S.range)) continue;
        t.bDmg = Math.max(t.bDmg, S.dmgB);
        t.bRange = Math.max(t.bRange, S.rangeB);
        t.bRate = Math.max(t.bRate, (S.rateB || 0) + war);
      }
    }
    this.banners = banners;
    const stormMul = this.stormOn() ? 0.75 : 1;
    const night = this.isNight();
    for (const t of this.towers) {
      const S = t.S;
      // noite: arqueiros enxergam menos (-15% de alcance), vaga-lumes brilham mais (+20% de dano)
      const nr = night && t.type === 'archer' ? 0.85 : 1, nd = night && t.type === 'mage' ? 1.2 : 1;
      if (!t.bDmg && !t.bRange && !t.bRate && stormMul === 1 && nr === 1 && nd === 1) { t.E = S; continue; }
      const E = Object.assign({}, S);
      if (!DATA.TOWERS[t.type].noTarget) E.range = S.range * (1 + t.bRange) * stormMul * nr;
      if (S.dmg && (t.bDmg || nd !== 1)) E.dmg = [S.dmg[0] * (1 + t.bDmg) * nd, S.dmg[1] * (1 + t.bDmg) * nd];
      if (S.dps && t.bDmg) E.dps = [S.dps[0] * (1 + t.bDmg), S.dps[1] * (1 + t.bDmg)];
      if (S.rate && t.bRate) E.rate = S.rate / (1 + t.bRate);
      t.E = E;
    }
    // revela espectros e (com o Farol) quem esta sob a areia
    for (const e of this.enemies) {
      if (e.T.stealth) {
        let rev = false;
        for (const b of banners) if (U.inRange(e.x - b.x, e.y - b.y, b.S.range)) { rev = true; break; }
        if (!rev) for (const u of this.units) if (!u.dead && Math.abs(u.x - e.x) < 70 && U.dist(u.x, u.y, e.x, e.y) < 70) { rev = true; break; }
        e.revealed = rev;
      }
      if (e.burrowed) {
        let see = false;
        for (const b of banners) if (b.S.seeBurrow && U.inRange(e.x - b.x, e.y - b.y, b.S.range)) { see = true; break; }
        e.seenBurrow = see;
      } else e.seenBurrow = false;
    }
  }

  bountyAt(x, y) {
    let v = 0;
    for (const b of this.banners || []) {
      if (b.spec !== 'watch') continue;
      const bv = this.abVal(b, 'bounty');
      if (bv && U.inRange(x - b.x, y - b.y, b.S.range)) v = Math.max(v, bv);
    }
    return v;
  }

  marchAt(x, y) {
    let v = 0;
    for (const b of this.banners || []) {
      if (b.spec !== 'drums') continue;
      const mv = this.abVal(b, 'march');
      if (mv && U.inRange(x - b.x, y - b.y, b.S.range)) v = Math.max(v, mv);
    }
    return v;
  }

  // ------------------------------------------------------------ unidades
  releaseTarget(u) {
    if (u.target && u.target.blocker === u) u.target.blocker = null;
    u.target = null;
  }

  hitUnit(u, dmg) {
    if (u.dead) return;
    if (u.dodge && Math.random() < u.dodge) {
      this.addFx({ kind: 'miss', x: u.x, y: u.y - 26, T: 0.6 });
      return;
    }
    u.hp -= dmg * (1 - u.armor);
    u.hurtT = 0.15;
    u.idleT = 0;
    if (u.hp <= 0) this.killUnit(u);
  }

  killUnit(u) {
    u.dead = true;
    u.hp = 0;
    this.releaseTarget(u);
    u.order = null;
    this.addFx({ kind: 'dust', x: u.x, y: u.y, T: 0.6, r: 22 });
    if (u.kind === 'hero') {
      u.respawnT = this.H.respawn * (1 - this.tal('respawn'));
      this.sfx({ n: 'heroDie', x: u.x });
    } else if (u.owner && u.owner.type === 'barracks') {
      u.respawnT = u.owner.S.respawn;
      this.sfx({ n: 'unitDie', x: u.x }, 0.6);
    } else {
      u.removed = true;
    }
  }

  acquire(u) {
    const hx = u.rx, hy = u.ry;
    let best = null, bs = Infinity;
    for (const e of this.enemies) {
      if (!this.targetable(e) || e.flying || e.burrowed) continue;
      const dr = U.dist(e.x, e.y, hx, hy);
      if (dr > u.guard) continue;
      let s = U.dist(e.x, e.y, u.x, u.y);
      const free = !e.blocker || e.blocker.dead || e.blocker.target !== e;
      if (!free) s += 400;
      if (e.T.unblockable) s += 200;
      if (s < bs) { bs = s; best = e; }
    }
    return best;
  }

  updateUnit(u, dt) {
    if (u.dead) {
      u.respawnT -= dt;
      if (u.respawnT <= 0) {
        if (u.kind === 'hero') {
          u.dead = false; u.hp = u.maxHp; u.x = u.rx; u.y = u.ry;
          this.addFx({ kind: 'sparkle', x: u.x, y: u.y - 20, T: 0.9 });
          this.sfx({ n: 'heroBack', x: u.x });
        } else if (u.owner) {
          u.dead = false; u.hp = u.maxHp; u.x = u.owner.x; u.y = u.owner.y + 10;
        }
      }
      return;
    }
    if (u.life > 0) {
      u.life -= dt;
      if (u.life <= 0) {
        this.releaseTarget(u);
        u.removed = true;
        this.addFx({ kind: 'dust', x: u.x, y: u.y, T: 0.6, r: 26 });
        return;
      }
    }
    u.atkAnim = Math.max(0, u.atkAnim - dt);
    u.hurtT = Math.max(0, u.hurtT - dt);
    u.cd -= dt;
    for (const k in u.abT) u.abT[k] -= dt;

    if (u.order) {
      const dx = u.order.x - u.x, dy = u.order.y - u.y, d = Math.hypot(dx, dy);
      const step = u.speed * 1.15 * dt;
      if (d <= step) {
        u.x = u.order.x; u.y = u.order.y; u.order = null; u.moving = false;
      } else {
        u.x += (dx / d) * step; u.y += (dy / d) * step;
        u.facing = dx >= 0 ? 1 : -1; u.moving = true; u.walk += dt * 11;
        u.hdx = dx / d; u.hdy = dy / d;
      }
      u.idleT += dt;
      if (u.kind === 'hero' && u.idleT > 2) u.hp = Math.min(u.maxHp, u.hp + this.H.regen * (1 + this.tal('regen')) * dt);
      return;
    }

    let t = u.target;
    if (t && (t.dead || t.reached || t.burrowed || t.flying || U.dist(t.x, t.y, u.rx, u.ry) > u.guard + 45)) {
      this.releaseTarget(u);
      t = null;
    }
    if (!t || (t.blocker && t.blocker !== u && t.blocker.target === t)) {
      // procura alvo livre (ou troca de "ajudante" para "bloqueador")
      const n = this.acquire(u);
      if (n && n !== t) {
        if (t) this.releaseTarget(u);
        t = n;
        u.target = n;
        u.charged = false;
      }
    }

    if (u.kind === 'hero') this.heroAbilities(u);
    else if (u.kind === 'monks') this.monkAbilities(u);

    if (t) {
      u.idleT = 0;
      if (!t.T.unblockable && (!t.blocker || t.blocker.dead || t.blocker.target !== t)) t.blocker = u;
      const side = u.x < t.x ? -1 : 1;
      const gx = t.x + side * (t.T.size + 9);
      const gy = t.y + (u.slot - 1) * 5;
      const dx = gx - u.x, dy = gy - u.y, d = Math.hypot(dx, dy);
      if (d > 3) {
        const step = Math.min(d, u.speed * dt);
        u.x += (dx / d) * step; u.y += (dy / d) * step;
        u.moving = true; u.walk += dt * 11;
        u.hdx = dx / d; u.hdy = dy / d;
      } else u.moving = false;
      u.facing = t.x >= u.x ? 1 : -1;
      if (d < 16 && u.cd <= 0) {
        u.cd = u.rate;
        u.atkAnim = 0.28;
        let dmg = U.roll(u.dmg);
        if (u.kind === 'lancers' && !u.charged) {
          const mul = this.abVal(u.owner, 'charge');
          if (mul) { dmg *= mul; this.stun(t, 0.6); this.addFx({ kind: 'hit', x: t.x, y: this.hitY(t), T: 0.35, big: true }); }
          u.charged = true;
        }
        const march = this.marchAt(u.x, u.y);
        if (march) dmg *= 1 + march;
        if (u.heroId === 'boitata') {
          // mordida de brasa: dano magico de fogo e queimadura (agua apaga; bicho de fogo nao queima)
          this.damage(t, dmg, 'magic', u, 'fire');
          if (!t.dead) this.burn(t, (4 + u.level) * (1 + this.tal('burn')), 2.5);
        } else this.damage(t, dmg, 'phys', u);
        this.addFx({ kind: 'hit', x: (t.x + u.x) / 2, y: this.hitY(t), T: 0.25 });
        this.sfx({ n: 'sword', x: u.x }, 0.5);
        if (u.heroId === 'boitata') this.sfx({ n: 'ember', x: t.x }, 0.5);
      }
    } else {
      const hx = u.rx + u.ox, hy = u.ry + u.oy;
      const dx = hx - u.x, dy = hy - u.y, d = Math.hypot(dx, dy);
      if (d > 2) {
        const step = Math.min(d, u.speed * dt);
        u.x += (dx / d) * step; u.y += (dy / d) * step;
        u.facing = dx >= 0 ? 1 : -1; u.moving = true; u.walk += dt * 11;
        u.hdx = dx / d; u.hdy = dy / d;
      } else u.moving = false;
      u.idleT += dt;
      if (u.idleT > 2) {
        const reg = u.kind === 'hero' ? this.H.regen * (1 + this.tal('regen')) : u.maxHp * 0.1;
        u.hp = Math.min(u.maxHp, u.hp + reg * dt);
      }
    }
  }

  heroAbilities(u) {
    if (this.heroId === 'caipora') return this.caiporaAbilities(u);
    if (this.heroId === 'benzedeira') return this.benzAbilities(u);
    if (this.heroId === 'boitata') return this.boitataAbilities(u);
    const lvl = u.level;
    const wk = 1 + this.tal('whirl');
    if (u.abT.whirl <= 0) {
      const near = this.enemiesIn(u.x, u.y, 62 * wk, true);
      if (near.length >= 2 || (near.length === 1 && u.target)) {
        u.abT.whirl = 10;
        u.atkAnim = 0.5; u.whirlT = 0.5;
        for (const e of near) this.damage(e, (34 + 9 * lvl) * wk, 'phys', u);
        this.addFx({ kind: 'whirl', x: u.x, y: u.y, T: 0.5 });
        this.sfx({ n: 'whirl', x: u.x });
      } else u.abT.whirl = 0.3;
    }
    if (u.abT.hawk <= 0) {
      let tgt = null, bs = -1;
      for (const e of this.enemies) {
        if (!this.seeable(e)) continue;
        if (!U.inRange(e.x - u.x, e.y - u.y, 240)) continue;
        const s = (e.flying ? 2000 : 0) + e.hp;
        if (s > bs) { bs = s; tgt = e; }
      }
      if (tgt) {
        u.abT.hawk = 7 * (1 - this.tal('hawk'));
        this.projs.push({ kind: 'hawk', x: u.x, y: u.y - 30, target: tgt, tx: tgt.x, ty: this.hitY(tgt), back: false, owner: u, dmg: 26 + 8 * lvl, ang: 0 });
        this.text(u.x, u.y - 50, 'Faz o L!', '#ff7a6a', 16);
        this.sfx({ n: 'hawk', x: u.x });
      } else u.abT.hawk = 0.5;
    }
  }

  // Caipora: chama bichos libertos (onca e queixada) e confunde os possuidos com a Trilha Falsa
  caiporaAbilities(u) {
    const lvl = u.level;
    if (u.abT.call <= 0) {
      const alive = this.units.some(o => o.kind === 'beast' && !o.dead && !o.removed);
      const foe = this.enemies.some(e => this.targetable(e) && !e.flying && U.inRange(e.x - u.x, e.y - u.y, 160));
      if (foe && !alive) {
        u.abT.call = 16;
        u.atkAnim = 0.4;
        const n = 2 + this.tal('beasts'), k = 1 + this.tal('beastHp');
        const types = ['comitiva', 'comitiva_b', 'comitiva'];   // seguranca e assessor de viagem (tools/blender/rampa_glb.py)
        for (let i = 0; i < n; i++) {
          const ox = (i - (n - 1) / 2) * 24;
          const b = new Unit(this, { kind: 'beast', x: u.x + ox, y: u.y + 12, rx: u.x + ox, ry: u.y + 8, ox: 0, oy: 0, hp: Math.round((110 + 12 * lvl) * k),
            dmg: [(6 + lvl) * k, (11 + 1.5 * lvl) * k], armor: 0.1, rate: 0.75, speed: 115, guard: 95, life: 12 });
          b.beast = types[i % types.length];
          b.slot = i % 3;
          this.units.push(b);
          this.addFx({ kind: 'dust', x: b.x, y: b.y, T: 0.6, r: 22 });
        }
        this.text(u.x, u.y - 50, 'Comitiva!', '#b6ec4a', 16);
        this.sfx({ n: 'riders', x: u.x });
        this.sfx({ n: 'beastCall', x: u.x });
      } else u.abT.call = 0.5;
    }
    if (u.abT.trail <= 0) {
      const near = this.enemiesIn(u.x, u.y, 78, true);
      if (near.length >= 2 || (near.length === 1 && u.target)) {
        u.abT.trail = 12;
        const dur = 2 + this.tal('trail');
        for (const e of near) e.backT = Math.max(e.backT || 0, e.T.boss ? dur * 0.4 : dur);
        this.addFx({ kind: 'ring', x: u.x, y: u.y, r: 78, color: '#b6ec4a', T: 0.5 });
        this.text(u.x, u.y - 50, 'Stories!', '#e6ff7a', 15);
        this.sfx({ n: 'whirl', x: u.x }, 0.6);
        this.sfx({ n: 'trail', x: u.x });
      } else u.abT.trail = 0.3;
    }
  }

  // Benzedeira: ervas de longe, benze (liberta) quem esta quase vencido e cura os aliados em volta
  benzAbilities(u) {
    const lvl = u.level;
    if (u.abT.bless <= 0) {
      const lim = 0.25 + this.tal('bless');
      const tgt = this.enemies.find(e => this.seeable(e) && !e.T.boss && e.hp < e.maxHp * lim && U.inRange(e.x - u.x, e.y - u.y, 140));
      if (tgt) {
        u.abT.bless = 5;
        u.atkAnim = 0.35;
        tgt.blessed = true;
        this.addFx({ kind: 'ring', x: tgt.x, y: tgt.y, r: 30, color: '#e6ff7a', T: 0.5 });
        this.text(tgt.x, tgt.y - 40, 'Cassado!', '#e6ff7a', 15);
        this.sfx({ n: 'bless', x: tgt.x });
        this.kill(tgt);
      } else u.abT.bless = 0.4;
    }
    if (u.abT.heal <= 0) {
      const hurt = this.units.filter(o => !o.dead && !o.removed && o.hp < o.maxHp * 0.85 && U.dist(o.x, o.y, u.x, u.y) < 100);
      if (hurt.length) {
        u.abT.heal = 7;
        const k = 1 + this.tal('heal');
        for (const o of hurt) o.hp = Math.min(o.maxHp, o.hp + o.maxHp * 0.3 * k + 2 * lvl);
        this.addFx({ kind: 'heal', x: u.x, y: u.y, T: 0.8 });
        this.sfx({ n: 'herbHeal', x: u.x }, 0.8);
      } else u.abT.heal = 0.5;
    }
    if (u.abT.herb <= 0) {
      let tgt = null, bd = 1e9;
      for (const e of this.enemies) {
        if (!this.seeable(e)) continue;
        const d = U.dist(e.x, e.y, u.x, u.y);
        if (d < 135 && d < bd) { bd = d; tgt = e; }
      }
      if (tgt) {
        u.abT.herb = 1.3;
        if (!u.target) { u.atkAnim = 0.28; u.facing = tgt.x >= u.x ? 1 : -1; }
        const sy = u.y - 26, dist = U.dist(u.x, sy, tgt.x, this.hitY(tgt));
        this.projs.push({ kind: 'herb', sx: u.x, sy, x: u.x, y: sy, ox: u.x, oy: u.y, target: tgt, tx: tgt.x, ty: this.hitY(tgt), t: 0, T: 0.3 + dist / 520, arc: 10 + dist * 0.18, dmg: (8 + 1.6 * lvl) * (1 + this.tal('herb')), ang: 0, owner: u });
        this.sfx({ n: 'herb', x: u.x }, 0.5);
      } else u.abT.herb = 0.3;
    }
  }

  // Boitata: Bote de Fogo (explosao em volta) e Rastro de Fogo (fogo na estrada)
  boitataAbilities(u) {
    const lvl = u.level;
    const fk = 1 + this.tal('flare');
    if (u.abT.flare <= 0) {
      const near = this.enemiesIn(u.x, u.y, 70 * fk, true);
      if (near.length >= 2 || (near.length === 1 && u.target)) {
        u.abT.flare = 10;
        u.atkAnim = 0.45;
        for (const e of near) {
          this.damage(e, (30 + 8 * lvl) * fk, 'magic', u, 'fire');
          if (!e.dead) this.burn(e, (5 + lvl) * (1 + this.tal('burn')), 3);
        }
        // o grito vira onda de choque verde e amarela (js/satira.js)
        this.addFx({ kind: 'shout', x: u.x, y: u.y, r: 70 * fk, T: 0.75 });
        this.text(u.x, u.y - 50, 'Imbrochável!', '#ffe45a', 16);
        this.sfx({ n: 'boom', x: u.x }, 0.6);
        this.sfx({ n: 'flare', x: u.x });
      } else u.abT.flare = 0.3;
    }
    if (u.abT.firetrail <= 0) {
      if (u.target && !u.target.dead) {
        u.abT.firetrail = 14;
        const t = u.target;
        // moto: mesma zona de dano, desenhada como marcas de pneu e fumaca de escapamento
        this.zones.push({ kind: 'fire', moto: true, x: t.x, y: t.y, r: 58, t: 0, T: 4 * (1 + this.tal('firetrail')), dps: 10 + 2 * lvl, tick: 0 });
        this.text(u.x, u.y - 50, 'Motociata!', '#9be37a', 16);
        this.sfx({ n: 'fireTrail', x: t.x }, 0.7);
      } else u.abT.firetrail = 0.5;
    }
  }

  monkAbilities(u) {
    const t = u.owner;
    const heal = this.abVal(t, 'heal');
    if (heal && (u.abT.heal == null || u.abT.heal <= 0)) {
      const hurt = this.units.filter(o => !o.dead && o.hp < o.maxHp * 0.9 && U.dist(o.x, o.y, u.x, u.y) < 70);
      if (hurt.length) {
        u.abT.heal = 4;
        for (const o of hurt) o.hp = Math.min(o.maxHp, o.hp + heal);
        this.addFx({ kind: 'heal', x: u.x, y: u.y, T: 0.8 });
        this.sfx({ n: 'herbHeal', x: u.x }, 0.5);
      } else u.abT.heal = 0.5;
    }
    const palm = this.abVal(t, 'palm');
    if (palm && u.target && (u.abT.palm == null || u.abT.palm <= 0)) {
      u.abT.palm = 6;
      u.atkAnim = 0.4;
      for (const e of this.enemiesIn(u.x, u.y, 55, true)) this.damage(e, palm, 'phys', u);
      this.addFx({ kind: 'ring', x: u.x, y: u.y, r: 55, color: '#ffd27a', T: 0.4 });
      this.sfx({ n: 'palm', x: u.x }, 0.7);
    }
  }

  nearestUnit(x, y, r) {
    let best = null, bd = r;
    for (const u of this.units) {
      if (u.dead || u.order) continue;
      const d = U.dist(x, y, u.x, u.y);
      if (d < bd) { bd = d; best = u; }
    }
    return best;
  }

  // ------------------------------------------------------------ inimigos
  placeEnemy(e) {
    const p = e.path.at(e.d, this._tmp);
    e.x = p.x - p.dy * e.lane * LANE;
    e.y = p.y + p.dx * e.lane * LANE;
    const bk = e.backT > 0 ? -1 : 1;   // andando para tras (Trilha Falsa): vira para o outro lado
    if (Math.abs(p.dx) > 0.15) e.facing = p.dx * bk >= 0 ? 1 : -1;
    e.hdx = p.dx * bk; e.hdy = p.dy * bk; // direcao do passo (o sprite escolhe lado, costas ou frente)
  }

  updateEnemy(e, dt) {
    const T = e.T;
    e.hurtT = Math.max(0, e.hurtT - dt);
    e.blockT = Math.max(0, e.blockT - dt);
    if (e.poisonT > 0) { e.poisonT -= dt; this.damage(e, e.poisonDps * dt, 'true', null); }
    if (e.burnT > 0) { e.burnT -= dt; this.damage(e, e.burnDps * dt, 'true', null, 'fire'); }
    if (e.dead) return;
    if (e.armorRedT > 0) { e.armorRedT -= dt; if (e.armorRedT <= 0) e.armorRed = 0; }
    if (e.slowT > 0) { e.slowT -= dt; if (e.slowT <= 0) e.slowF = 1; }
    if (e.wetT > 0) e.wetT -= dt;
    if (e.blindT > 0) e.blindT -= dt;
    // marcas visuais de magia (choque, arcano, calor do feixe)
    if (e.shockT > 0) e.shockT -= dt;
    if (e.arcT > 0) e.arcT -= dt;
    if (e.heatT > 0) e.heatT -= dt;
    if (e.markT > 0) e.markT -= dt;
    if (e.frozenT > 0) e.frozenT -= dt;
    if (e.pushRes > 0) e.pushRes = Math.max(0, e.pushRes - 0.25 * dt);
    if (e.groundT > 0) {
      e.groundT -= dt;
      if (e.groundT <= 0) {
        e.flying = true;
        if (e.blocker) { this.releaseTarget(e.blocker); e.blocker = null; }
      }
    }
    e.atkAnim = Math.max(0, e.atkAnim - dt);
    e.castAnim = Math.max(0, e.castAnim - dt);
    if (e.stunT > 0) { e.stunT -= dt; e.moving = false; return; }
    const blind = e.blindT > 0;

    // habilidades especiais (cegos nao conjuram)
    if (!blind) e.abT -= dt;
    if (T.heal && e.abT <= 0) {
      const hurt = this.enemies.filter(o => !o.dead && o.hp < o.maxHp && U.dist(o.x, o.y, e.x, e.y) < T.heal.r);
      if (hurt.length) {
        e.abT = T.heal.cd; e.castAnim = 0.7;
        for (const o of hurt) o.hp = Math.min(o.maxHp, o.hp + T.heal.amt);
        this.addFx({ kind: 'enemyHeal', x: e.x, y: e.y, r: T.heal.r, T: 0.8 });
        this.sfx({ n: 'heal', x: e.x }, 0.5);
      } else e.abT = 0.5;
    }
    if (T.summon && e.abT <= 0 && this.visible(e)) {
      e.abT = T.summon.cd; e.castAnim = 0.8;
      for (let i = 0; i < T.summon.n; i++) {
        const s = this.spawn(T.summon.type, e.pathIdx, Math.max(0, e.d - 30 - i * 14));
        s.fdone = e.fdone;
        this.addFx({ kind: T.flying ? 'sparkle' : 'dust', x: s.x, y: s.y, T: 0.6, r: 22 });
      }
      this.markSeen(T.summon.type);
      this.sfx({ n: 'warcry', x: e.x });
    }
    if (T.firestorm && !blind && this.visible(e)) {
      e.fsT -= dt;
      if (e.fsT <= 0) this.firestorm(e);
    }
    if (T.sabotage && !blind && !e.blocker && this.visible(e)) {
      e.sabT -= dt;
      if (e.sabT <= 0) this.sabotage(e);
    }
    if (T.burrow && e.abT <= 0 && this.visible(e)) {
      if (!e.burrowed) {
        e.burrowed = true; e.abT = T.burrow.dur;
        if (e.blocker) { this.releaseTarget(e.blocker); e.blocker = null; }
        this.addFx({ kind: 'poof', x: e.x, y: e.y, T: 0.7 });
      } else {
        e.burrowed = false; e.abT = T.burrow.every;
        this.addFx({ kind: 'poof', x: e.x, y: e.y, T: 0.7 });
      }
    }
    if (T.wormBurrow && e.abT <= 0 && this.visible(e)) {
      const B = T.wormBurrow;
      if (!e.burrowed) {
        e.burrowed = true; e.abT = B.dur;
        this.addFx({ kind: 'poof', x: e.x, y: e.y, T: 1.0, big: true });
        this.addFx({ kind: 'shake', T: 0.5, amp: 5 });
        this.sfx({ n: 'rumble', x: e.x });
      } else {
        e.burrowed = false; e.abT = B.every;
        this.addFx({ kind: 'poof', x: e.x, y: e.y, T: 1.0, big: true });
        this.addFx({ kind: 'shake', T: 0.5, amp: 6 });
        this.sfx({ n: 'rumble', x: e.x });
        for (let i = 0; i < B.n; i++) {
          const s = this.spawn(B.spawn, e.pathIdx, Math.max(0, e.d - 40 - i * 22));
          s.fdone = e.fdone;
          this.addFx({ kind: 'poof', x: s.x, y: s.y, T: 0.7 });
        }
      }
    }
    if (T.trample && !e.burrowed) {
      e.trampleT -= dt;
      if (e.trampleT <= 0) {
        e.trampleT = 0.6;
        for (const u of this.units) {
          if (!u.dead && U.dist(u.x, u.y, e.x, e.y) < T.trample.r + 8) this.hitUnit(u, T.trample.dmg);
        }
      }
    }

    // bloqueado por soldado?
    const b = e.blocker;
    if (b && (b.dead || b.target !== e || b.removed)) e.blocker = null;
    if (e.blocker && !e.burrowed) {
      const bu = e.blocker;
      if (U.dist(e.x, e.y, bu.x, bu.y) < T.size + 24) {
        e.moving = false;
        e.facing = bu.x >= e.x ? 1 : -1;
        e.cd -= dt;
        if (e.cd <= 0) {
          e.cd = T.rate || 1;
          e.atkAnim = 0.3;
          const dmg = (T.dmg ? U.roll(T.dmg) : 10) * (blind ? 0.5 : 1);
          this.hitUnit(bu, dmg);
          if (T.aoe) {
            for (const o of this.units) if (o !== bu && !o.dead && U.dist(o.x, o.y, e.x, e.y) < T.aoe) this.hitUnit(o, dmg * 0.6);
            this.addFx({ kind: 'ring', x: e.x, y: e.y, r: T.aoe, color: '#ff8a5a', T: 0.35 });
            this.sfx({ n: 'slam', x: e.x }, 0.6);
          } else this.sfx({ n: 'enemyHit', x: e.x }, 0.4);
        }
        return;
      }
    }

    // atirador: dispara enquanto anda devagar (nunca para de vez, para nao travar a fase)
    let aimSlow = 1, aimFace = 0;
    if (T.ranged && !e.burrowed && !blind && this.visible(e)) {
      e.cd -= dt;
      const tu = this.nearestUnit(e.x, e.y, T.ranged.range);
      if (tu) {
        aimSlow = 0.4;
        aimFace = tu.x >= e.x ? 1 : -1;
        if (e.cd <= 0) {
          e.cd = T.ranged.rate;
          e.atkAnim = 0.3;
          const sy = e.y - 18;
          const dist = U.dist(e.x, sy, tu.x, tu.y - 14);
          // skey: chave do sprite de quem atira (megafone, selfie...), so para o desenho do tiro (js/satira.js)
          const skey = T.spr || e.type;
          this.projs.push({ kind: 'enemyArrow', skey, sx: e.x, sy, x: e.x, y: sy, target: tu, tx: tu.x, ty: tu.y - 14, t: 0, T: 0.3 + dist / 800, arc: 14 + dist * 0.15, dmg: U.roll(T.ranged.dmg), ang: 0 });
          if (skey === 'gleice') this.sfx({ n: 'megafoneLonge', x: e.x }, 0.9);
          else if (skey === 'nicolau') this.sfx({ n: 'notif', x: e.x }, 0.8);
          else this.sfx({ n: 'arrow', x: e.x }, 0.3);
        }
      }
    }

    let sp = T.speed * e.slowF * aimSlow * (e.burrowed && T.burrow ? T.burrow.speedMul : 1);
    if (T.stealth && this.stormOn()) sp *= 1.3;
    if (T.final) this.updateHeart(e, dt);
    // cheia: os bichos do rio nadam mais rapido
    if (T.aquatic && this.flood > 0.5) sp *= 1.3;
    // Trilha Falsa (Caipora): perdido, anda de volta pela estrada
    if (e.backT > 0) { e.backT -= dt; sp = -sp * 0.8; if (e.d + sp * dt < 0) sp = 0; }
    e.d += sp * dt;
    e.moving = true;
    e.walk += dt * (2 + sp * 0.12);
    // bifurcacao: a comporta decide o ramo
    for (let k = 0; k < this.forks.length; k++) {
      const f = this.forks[k];
      if (e.fdone & (1 << k) || e.d < f.d || !f.paths.includes(e.pathIdx)) continue;
      e.fdone |= 1 << k;
      const want = f.paths[f.state];
      if (want !== e.pathIdx) { e.pathIdx = want; e.path = this.paths[want]; }
    }
    if (e.d >= e.path.len) {
      e.reached = true;
      this.lives = Math.max(0, this.lives - T.lives);
      this.stats.leaked += T.lives;
      this.leaks.push(e.type + '@' + this.wave + (T.boss ? '(' + Math.round(e.hp) + ')' : ''));
      this.sfx('leak');
      this.addFx({ kind: 'leak', T: 0.6 });
      if (this.lives <= 0) this.lose();
      return;
    }
    this.placeEnemy(e);
    if (aimFace) e.facing = aimFace;
  }

  sabotage(e) {
    const S = e.T.sabotage;
    let best = null, bd = Infinity;
    for (const t of this.towers) {
      if (t.disabledT > 0 || t.working) continue;
      if (!U.inRange(t.x - e.x, t.y - e.y, S.r)) continue;
      const d = U.dist(t.x, t.y, e.x, e.y);
      if (d < bd) { bd = d; best = t; }
    }
    if (!best) { e.sabT = 0.4; return; }
    e.sabT = S.cd;
    e.castAnim = 0.5;
    const sy = e.y - 18, ty = best.y - 24;
    this.projs.push({ kind: 'pot', skey: e.T.spr || e.type, sx: e.x, sy, x: e.x, y: sy, tx: best.x, ty, t: 0, T: 0.6, arc: 50, ang: 0, tower: best, dur: S.dur });
    this.sfx({ n: 'throw', x: e.x }, 0.6);
  }

  firestorm(e) {
    const S = e.T.firestorm;
    e.fsT = S.cd;
    const list = this.towers.filter(t => t.disabledT <= 0 && U.inRange(t.x - e.x, t.y - e.y, S.r))
      .sort((a, b) => b.invested - a.invested).slice(0, S.n);
    if (!list.length) { e.fsT = 1; return; }
    e.castAnim = 1;
    list.forEach((t, i) => {
      const sx = e.x, sy = e.y - FLY_H - 20;
      this.projs.push({ kind: 'fireball', sx, sy, x: sx, y: sy, tx: t.x, ty: t.y - 20, t: -i * 0.18, T: 0.9, arc: 110, ang: 0, tower: t, dur: S.dur });
    });
    this.sfx({ n: 'firestorm', x: e.x });
  }

  disableTower(t, dur) {
    if (!t || !this.towers.includes(t)) return;
    t.disabledT = Math.max(t.disabledT, dur);
    t.beam = null;
  }

  // ------------------------------------------------------------ torres em acao
  updateTower(t, dt) {
    t.anim = Math.max(0, t.anim - dt);
    t.buildT += dt;
    t.popT += dt;
    if (t.fireT > 0) t.fireT -= dt;
    if (t.working) {
      if (t.disabledT > 0) t.disabledT -= dt;
      if (t.buildT >= t.buildDur) this.finishWork(t);
      else { this.workTick(t, dt); return; }
    }
    if (t.disabledT > 0) { t.disabledT -= dt; t.cd = Math.max(t.cd, 0.2); return; }
    const S = t.E || t.S;
    // fumaca do Coracao: recarga mais lenta
    if (t.chokeT > 0) { t.chokeT -= dt; t.cd -= dt / DATA.ENEMIES.heart.choke.rate; } else t.cd -= dt;
    for (const k in t.abT) t.abT[k] -= dt;
    const top = this.towerTop(t);
    const spec = t.spec;

    if (t.type === 'archer') {
      if (t.cd > 0) return;
      const e = this.findTarget(t.x, t.y, S.range, false, t.prio);
      if (!e) { t.cd = 0.08; return; }
      t.cd = S.rate; t.anim = 0.3; t.aimX = e.x; t.aimY = e.y; t.shots++;
      t.shooter = (t.shooter + 1) % 2;
      if (spec === 'ballista') {
        const sx = t.x, sy = t.y - top;
        const pp = this.predict(e, 0.12);
        const ty = pp.y - (e.flying ? FLY_H : e.T.size * 0.75);
        const dx = pp.x - sx, dy = ty - sy, d = Math.hypot(dx, dy) || 1;
        const exp = this.abLvl(t, 'explosive') && t.shots % 4 === 0 ? this.abVal(t, 'explosive') : 0;
        this.projs.push({ kind: 'bolt', x: sx, y: sy, ox: t.x, oy: t.y, vx: (dx / d) * 980, vy: (dy / d) * 980, left: S.range * 1.45, pierce: S.pierce, hit: new Set(), dmg: S.dmg, crit: this.abVal(t, 'eagle'), exp, ang: Math.atan2(dy, dx) });
        this.sfx({ n: 'ballista', x: t.x });
      } else {
        const sx = t.x + (t.shooter ? 9 : -9), sy = t.y - top;
        const ty = this.hitY(e);
        const dist = U.dist(sx, sy, e.x, ty);
        if (spec === 'blowgun') {
          const corr = this.abVal(t, 'corrosive');
          this.projs.push({ kind: 'dart', sx, sy, ox: t.x, oy: t.y, x: sx, y: sy, target: e, tx: e.x, ty, t: 0, T: 0.12 + dist / 1200, arc: 6 + dist * 0.05, dmg: U.roll(S.dmg), poison: S.poison + (corr ? corr * 25 : 0), corr, ang: 0 });
          this.sfx({ n: 'dart', x: t.x }, 0.5);
          if (this.abLvl(t, 'cloud') && t.abT.cloud <= 0) {
            const c = this.densest(t.x, t.y, S.range, true, 60);
            if (c) {
              t.abT.cloud = 8;
              this.projs.push({ kind: 'flask', sx, sy, x: sx, y: sy, tx: c.x, ty: c.y, t: 0, T: 0.7, arc: 60, dps: this.abVal(t, 'cloud'), ang: 0 });
            }
          }
        } else {
          this.projs.push({ kind: 'arrow', sx, sy, ox: t.x, oy: t.y, x: sx, y: sy, target: e, tx: e.x, ty, t: 0, T: 0.2 + dist / 850, arc: 16 + dist * 0.17, dmg: U.roll(S.dmg), ang: 0 });
          this.sfx({ n: 'arrow', x: t.x }, 0.45);
        }
      }
      return;
    }

    if (t.type === 'mage') {
      t.castT = (t.castT || 0) + dt;
      if (spec === 'sun') return this.updateSun(t, dt, top, S);
      // carga: com alvo na mira, o cristal acumula energia nos ultimos MAGE_CHARGE s antes do disparo;
      // sem alvo, fica so um brilho baixo de prontidao
      t.chargeT = t.armed ? U.clamp(1 - t.cd / MAGE_CHARGE, 0, 1) : Math.max(0, (t.chargeT || 0) - dt * 3);
      if (t.cd > 0) return;
      const e = this.findTarget(t.x, t.y, S.range, false, t.prio);
      t.armed = !!e;
      if (!e) { t.cd = 0.08; return; }
      t.cd = S.rate; t.anim = 0.45; t.aimX = e.x; t.aimY = e.y;
      t.castT = 0; t.chargeT = 0; t.shots = (t.shots || 0) + 1;
      const sx = t.x, sy = t.y - top;
      if (spec === 'lightning') {
        const chain = [e];
        let cur = e;
        const dmg = U.roll(S.dmg);
        const pts = [[sx, sy], [e.x, this.hitY(e)]];
        for (let j = 0; j < S.jumps; j++) {
          let nb = null, nd = 110;
          for (const o of this.enemies) {
            if (!this.seeable(o) || chain.includes(o)) continue;
            const d = U.dist(o.x, o.y, cur.x, cur.y);
            if (d < nd) { nd = d; nb = o; }
          }
          if (!nb) break;
          chain.push(nb); pts.push([nb.x, this.hitY(nb)]); cur = nb;
        }
        const st = this.abVal(t, 'overload');
        chain.forEach((o, i) => {
          o.shockT = 0.7;
          this.damage(o, dmg * Math.pow(0.72, i), 'magic', null, 'shock');
          if (st && Math.random() < st) this.stun(o, 1.0);
          if (S.frost) this.slow(o, 0.75, 1);
        });
        this.addFx({ kind: 'lightning', pts, T: 0.34, seed: t.shots });
        this.sfx({ n: 'zap', x: t.x }, 0.7);
        if (this.abLvl(t, 'storm') && t.abT.storm <= 0) {
          t.abT.storm = 10;
          this.zones.push({ kind: 'storm', x: e.x, y: e.y, r: 62, t: 0, T: 2.2, n: this.abVal(t, 'storm'), done: 0 });
          this.addFx({ kind: 'cloud', x: e.x, y: e.y, T: 2.6 });
        }
      } else {
        // nivel 3: a cada S.big disparos sai uma Esfera Maior
        const big = S.big && t.shots % S.big === 0;
        const burst = S.burst ? (big ? [S.burst[0] * 1.45, Math.min(1, S.burst[1] + 0.15)] : S.burst) : null;
        this.projs.push({ kind: 'magic', x: sx, y: sy, sx, sy, target: e, tx: e.x, ty: this.hitY(e), gx: e.x, gy: e.y, dmg: U.roll(S.dmg) * (big ? 2 : 1), frost: S.frost, burst, big, age: 0, trail: [], id: this.nextId++ });
        this.sfx({ n: big ? 'orbBig' : 'magic', x: t.x }, big ? 0.8 : 0.55);
      }
      return;
    }

    if (t.type === 'artillery') {
      if (spec === 'seismic') {
        if (this.abLvl(t, 'chasm') && t.abT.chasm <= 0) {
          let v = null;
          for (const e of this.enemiesIn(t.x, t.y, S.range * 1.15, true)) {
            if (e.T.boss || e.hp > 1000) continue;
            if (!v || e.hp > v.hp) v = e;
          }
          if (v) {
            t.abT.chasm = this.abVal(t, 'chasm');
            this.addFx({ kind: 'chasm', x: v.x, y: v.y, T: 1.2 });
            v.hp = 0;
            this.kill(v);
            this.sfx({ n: 'rumble', x: v.x });
          } else t.abT.chasm = 1;
        }
        if (t.cd > 0) return;
        const list = this.enemiesIn(t.x, t.y, S.range, true);
        if (!list.length) { t.cd = 0.1; return; }
        t.cd = S.rate; t.anim = 0.6;
        const tr = this.abVal(t, 'tremor');
        const R = S.range, dmgR = S.dmg;
        this.later(0.18, () => {
          for (const e of this.enemiesIn(t.x, t.y, R, true)) {
            this.damage(e, U.roll(dmgR), 'phys', null);
            this.slow(e, S.slow, 1.3);
            if (tr && Math.random() < tr) this.stun(e, 1.4);
          }
          this.addFx({ kind: 'quake', x: t.x, y: t.y, r: R, T: 0.6 });
          this.addFx({ kind: 'shake', T: 0.2, amp: 2 });
          this.sfx({ n: 'slam', x: t.x }, 0.8);
        });
        return;
      }
      if (spec === 'mortar' && this.abLvl(t, 'barrel') && t.abT.barrel <= 0) {
        const c = this.densest(t.x, t.y, S.range, true, 60);
        if (c) {
          t.abT.barrel = 12;
          const p = this.predict(c, 1.0);
          this.projs.push({ kind: 'barrel', sx: t.x, sy: t.y - top, x: t.x, y: t.y - top, tx: p.x, ty: p.y, t: 0, T: 1.0, arc: 120, dps: this.abVal(t, 'barrel'), ang: 0 });
          this.sfx({ n: 'launch', x: t.x }, 0.7);
        } else t.abT.barrel = 0.5;
      }
      if (t.cd > 0) return;
      const e = this.findTarget(t.x, t.y, S.range, true, t.prio);
      if (!e) { t.cd = 0.1; return; }
      t.cd = S.rate; t.anim = 0.5; t.shots++; t.aimX = e.x;
      const sx = t.x, sy = t.y - top;
      const dist = U.dist(sx, sy, e.x, e.y);
      const T = 0.75 + dist / 700;
      const p = this.predict(e, T);
      const cluster = spec === 'mortar' && this.abLvl(t, 'cluster') && t.shots % 3 === 0 ? this.abVal(t, 'cluster') : 0;
      this.projs.push({ kind: 'bomb', sx, sy, x: sx, y: sy, tx: p.x, ty: p.y, t: 0, T, arc: 90 + dist * 0.35, dmg: S.dmg, r: S.radius, big: spec === 'mortar', cluster, ang: 0 });
      this.sfx({ n: 'launch', x: t.x }, 0.6);
      return;
    }

    if (t.type === 'cistern') return this.updateCistern(t, dt, top, S);
    if (t.type === 'windmill') return this.updateWindmill(t, dt, top, S);
    if (t.type === 'banner') return this.updateBanner(t, dt, S);
    if (t.type === 'market') return this.updateMarket(t, dt, S);
  }

  updateSun(t, dt, top, S) {
    let e = t.beam;
    if (e && (!this.seeable(e) || !U.inRange(e.x - t.x, e.y - t.y, S.range))) e = null;
    if (!e) {
      e = this.findTarget(t.x, t.y, S.range, false, t.prio);
      t.beamT = 0;
    }
    if (e !== t.beam) t.beamT = 0;
    t.beam = e;
    if (!e) { t.chargeT = Math.max(0, (t.chargeT || 0) - dt * 2); return; }
    t.beamT += dt;
    t.aimX = e.x;
    const k = Math.min(1, t.beamT / S.ramp);
    this.damage(e, U.lerp(S.dps[0], S.dps[1], k) * dt, 'magic', null);
    const burn = this.abVal(t, 'burn');
    if (burn && !e.dead) this.burn(e, burn, 2);
    if (S.frost && !e.dead) this.slow(e, 0.75, 0.3);
    if (t.cd <= 0) { t.cd = 1.2; this.sfx({ n: 'beam', x: t.x }, 0.3); }
    t.chargeT = k;
    e.heatT = 0.25;
    if (this.abLvl(t, 'flash') && t.abT.flash <= 0) {
      t.abT.flash = 9;
      const dur = this.abVal(t, 'flash');
      for (const o of this.enemiesIn(e.x, e.y, 85, false)) { this.stun(o, dur); this.damage(o, 30, 'magic', null); }
      this.addFx({ kind: 'flash', x: e.x, y: e.y, r: 85, T: 0.5 });
      this.sfx({ n: 'flash', x: e.x });
    }
  }

  updateCistern(t, dt, top, S) {
    const spec = t.spec;
    // fonte: cura aliados no alcance
    const spring = spec === 'fountain' ? this.abVal(t, 'spring') : 0;
    if (spring && (t.abT.spring == null || t.abT.spring <= 0)) {
      t.abT.spring = 1;
      let any = false;
      for (const u of this.units) {
        if (u.dead || u.hp >= u.maxHp || !U.inRange(u.x - t.x, u.y - t.y, S.range)) continue;
        u.hp = Math.min(u.maxHp, u.hp + spring);
        any = true;
      }
      if (any) this.addFx({ kind: 'drops', x: t.x, y: t.y - top, T: 0.8 });
    }
    // fonte: lamacal no caminho
    if (spec === 'fountain' && this.abLvl(t, 'mire') && t.abT.mire <= 0) {
      const c = this.densest(t.x, t.y, S.range, true, 60);
      if (c) {
        t.abT.mire = 11;
        const p = this.predict(c, 0.6);
        this.projs.push({ kind: 'waterball', sx: t.x, sy: t.y - top, x: t.x, y: t.y - top, tx: p.x, ty: p.y, t: 0, T: 0.6, arc: 80, dur: this.abVal(t, 'mire'), ang: 0 });
        this.sfx({ n: 'splash', x: t.x }, 0.6);
      } else t.abT.mire = 0.5;
    }
    // geiser: erupcao sob o mais forte
    if (spec === 'geyser' && this.abLvl(t, 'burst') && t.abT.burst <= 0) {
      const e = this.findTarget(t.x, t.y, S.range, true, 'strong');
      if (e) {
        t.abT.burst = 8;
        const x = e.x, y = e.y, dmg = this.abVal(t, 'burst');
        this.addFx({ kind: 'geyserWarn', x, y, T: 0.45 });
        this.later(0.45, () => {
          for (const o of this.enemiesIn(x, y, 46, false)) {
            this.damage(o, dmg, 'phys', null, 'water');
            this.wet(o, S.wet);
            this.stun(o, 0.8);
          }
          this.addFx({ kind: 'geyser', x, y, T: 0.9 });
          this.sfx({ n: 'geyser', x });
        });
      } else t.abT.burst = 0.5;
    }
    if (t.cd > 0) return;
    const e = this.findTarget(t.x, t.y, S.range, false, t.prio);
    if (!e) { t.cd = 0.08; return; }
    t.cd = S.rate; t.anim = 0.35; t.aimX = e.x;
    const sx = t.x, sy = t.y - top;
    if (spec === 'geyser') {
      const ty = this.hitY(e);
      this.addFx({ kind: 'jet', x0: sx, y0: sy, x1: e.x, y1: ty, T: 0.22 });
      this.damage(e, U.roll(S.dmg), 'phys', null, 'water');
      const chill = this.abVal(t, 'chill');
      if (chill && e.wetT > 0 && Math.random() < chill) this.freeze(e, 1.5);
      this.wet(e, S.wet);
      this.slow(e, S.slow, 1.2);
      this.push(e, S.push);
      this.sfx({ n: 'jet', x: t.x }, 0.6);
    } else {
      const ty = this.hitY(e);
      const dist = U.dist(sx, sy, e.x, ty);
      const big = spec === 'fountain';
      this.projs.push({ kind: 'water', sx, sy, x: sx, y: sy, target: e, tx: e.x, ty, t: 0, T: 0.28 + dist / 700, arc: 30 + dist * 0.25, dmg: U.roll(S.dmg), wet: S.wet, slow: S.slow, splash: S.splash, big, ang: 0 });
      this.sfx({ n: 'water', x: t.x }, 0.5);
    }
  }

  updateWindmill(t, dt, top, S) {
    const spec = t.spec;
    if (spec === 'tornado' && this.abLvl(t, 'twister') && t.abT.twister <= 0) {
      const e = this.findTarget(t.x, t.y, S.range, true, 'first');
      if (e) {
        t.abT.twister = 12;
        this.zones.push({ kind: 'tornado', path: e.path, pathIdx: e.pathIdx, d: e.d + 30, x: e.x, y: e.y, r: 30, t: 0, T: 3.2, dmg: this.abVal(t, 'twister'), hit: new Set() });
        this.sfx({ n: 'tornado', x: t.x });
      } else t.abT.twister = 0.5;
    }
    if (t.cd > 0) return;
    const e = this.findTarget(t.x, t.y, S.range, false, t.prio);
    if (!e) { t.cd = 0.08; return; }
    t.cd = S.rate; t.anim = 0.5; t.aimX = e.x;
    const sx = t.x, sy = t.y - top;
    const p = this.predict(e, 0.3);
    const ty = p.y - (e.flying ? FLY_H : e.T.size * 0.6);
    const sand = spec === 'sandblast';
    this.projs.push({ kind: 'gust', sx, sy, x: sx, y: sy, tx: p.x, ty, gx: p.x, gy: p.y, t: 0, T: 0.3, dmg: S.dmg, push: S.push, r: S.radius, sand, shred: sand ? this.abVal(t, 'shred') : 0, blind: sand ? this.abVal(t, 'blind') : 0, sky: spec === 'tornado' ? this.abVal(t, 'skyward') : 0, ang: Math.atan2(ty - sy, p.x - sx) });
    this.sfx({ n: sand ? 'sand' : 'gust', x: t.x }, 0.6);
  }

  updateBanner(t, dt, S) {
    if (t.spec === 'drums' && this.abLvl(t, 'warcry') && t.abT.warcry <= 0) {
      const busy = this.enemies.some(e => this.targetable(e) && U.inRange(e.x - t.x, e.y - t.y, S.range + 120));
      if (busy) {
        t.abT.warcry = 14;
        t.warT = this.abVal(t, 'warcry');
        t.anim = 0.8;
        this.addFx({ kind: 'ring', x: t.x, y: t.y, r: S.range, color: '#ffb35a', T: 0.7 });
        this.sfx({ n: 'drums', x: t.x });
      } else t.abT.warcry = 0.5;
    }
    if (t.spec === 'watch' && this.abLvl(t, 'mark') && t.abT.mark <= 0) {
      let best = null;
      for (const e of this.enemies) {
        if (!this.targetable(e) || e.markT > 0 || !U.inRange(e.x - t.x, e.y - t.y, S.range)) continue;
        if (!best || e.hp > best.hp) best = e;
      }
      if (best) {
        t.abT.mark = 6;
        best.markT = 6; best.markMul = this.abVal(t, 'mark');
        this.addFx({ kind: 'mark', e: best, T: 6 });
        this.sfx({ n: 'mark', x: t.x }, 0.6);
      } else t.abT.mark = 0.5;
    }
  }

  updateMarket(t, dt, S) {
    if (t.spec !== 'bazaar' || !this.abLvl(t, 'mercs')) return;
    if (t.abT.mercs == null) t.abT.mercs = 2;
    if (t.abT.mercs > 0 || this.state !== 'running') return;
    t.units = t.units.filter(u => !u.removed);
    if (t.units.length >= 2) { t.abT.mercs = 1; return; }
    t.abT.mercs = this.abVal(t, 'mercs');
    const r = t.rally || this.defaultRally(t);
    const u = new Unit(this, { kind: 'merc', x: t.x, y: t.y + 10, rx: r.x, ry: r.y, ox: (t.units.length ? 12 : -12), oy: 4, hp: 150, dmg: [9, 15], armor: 0.25, rate: 0.9, speed: 82, guard: 70, life: 18, owner: t });
    t.units.push(u);
    this.units.push(u);
    this.addFx({ kind: 'dust', x: u.x, y: u.y, T: 0.6, r: 22 });
    this.sfx({ n: 'merc', x: t.x }, 0.7);
  }

  // ------------------------------------------------------------ projeteis
  updateProj(p, dt) {
    switch (p.kind) {
      case 'arrow': case 'dart': case 'enemyArrow': case 'water': case 'herb': {
        p.t += dt;
        const k = Math.min(1, p.t / p.T);
        const tg = p.target;
        const alive = tg && !tg.dead && !tg.burrowed && !tg.reached;
        if (alive) {
          if (p.kind === 'enemyArrow') { p.tx = tg.x; p.ty = tg.y - 14; } else { p.tx = tg.x; p.ty = this.hitY(tg); }
        }
        const nx = U.lerp(p.sx, p.tx, k), ny = U.lerp(p.sy, p.ty, k) - p.arc * 4 * k * (1 - k);
        p.ang = Math.atan2(ny - p.y, nx - p.x);
        p.x = nx; p.y = ny;
        if (k >= 1) {
          p.done = true;
          if (p.kind === 'enemyArrow') {
            if (tg && !tg.dead) this.hitUnit(tg, p.dmg);
          } else if (p.kind === 'water') {
            this.splash(p, alive ? tg : null);
          } else if (p.kind === 'herb') {
            if (alive) {
              this.damage(tg, p.dmg, 'magic', p.owner);
              this.addFx({ kind: 'hit', x: p.x, y: p.y, T: 0.2, small: true });
              this.sfx({ n: 'herbHit', x: p.x }, 0.4);
            }
          } else if (alive) {
            const m = this.shieldMul(tg, p.ox, p.oy);
            this.damage(tg, p.dmg * m, 'phys', null);
            if (p.kind === 'dart') this.poison(tg, p.poison * (m < 1 ? 0.5 : 1), 3, p.corr);
            this.addFx({ kind: m < 1 ? 'block' : 'hit', x: p.x, y: p.y, T: m < 1 ? 0.35 : 0.2, small: true });
            if (m < 1) this.sfx({ n: 'clang', x: p.x }, 0.4);
          } else {
            this.addFx({ kind: 'stuck', x: p.x, y: p.y + 8, ang: p.ang, T: 1.4, dart: p.kind === 'dart' });
          }
        }
        break;
      }
      case 'magic': {
        const tg = p.target;
        const alive = tg && !tg.dead && !tg.burrowed && !tg.reached;
        if (alive) { p.tx = tg.x; p.ty = this.hitY(tg); p.gx = tg.x; p.gy = tg.y; }
        const dx = p.tx - p.x, dy = p.ty - p.y, d = Math.hypot(dx, dy);
        const step = (p.big ? 360 : 430) * dt;
        p.age += dt;
        if (!this.headless) { p.trail.push([p.x, p.y]); if (p.trail.length > 14) p.trail.shift(); }
        if (d <= step + 3) {
          p.done = true;
          if (alive) {
            this.damage(tg, p.dmg, 'magic', null);
            if (p.frost) this.slow(tg, 0.75, 1);
            tg.arcT = 0.45;
          }
          // explosao arcana em volta (nivel 2+)
          if (p.burst) {
            for (const o of this.enemiesIn(p.gx, p.gy, p.burst[0], false)) {
              if (o === tg) continue;
              this.damage(o, p.dmg * p.burst[1], 'magic', null);
              o.arcT = 0.35;
            }
          }
          this.addFx({ kind: 'magicHit', x: p.tx, y: p.ty, gx: p.gx, gy: p.gy, r: p.burst ? p.burst[0] : 0, big: p.big, frost: p.frost, T: p.big ? 0.75 : p.burst ? 0.55 : 0.4 });
          if (p.big) this.addFx({ kind: 'shake', T: 0.18, amp: 2.5 });
          this.sfx({ n: p.big ? 'arcaneBig' : 'arcane', x: p.tx }, p.burst ? 0.6 : 0.45);
        } else {
          p.x += (dx / d) * step; p.y += (dy / d) * step;
        }
        break;
      }
      case 'bomb': case 'bomblet': case 'barrel': case 'flask': case 'waterball': case 'pot': case 'fireball': {
        p.t += dt;
        if (p.t < 0) break;
        const k = Math.min(1, p.t / p.T);
        const nx = U.lerp(p.sx, p.tx, k), ny = U.lerp(p.sy, p.ty, k) - p.arc * 4 * k * (1 - k);
        p.ang += dt * 8;
        p.x = nx; p.y = ny;
        if (k >= 1) {
          p.done = true;
          if (p.kind === 'bomb') {
            this.explode(p.tx, p.ty, p.r, p.dmg, null, p.big);
            if (p.cluster) {
              for (let i = 0; i < p.cluster; i++) {
                const a = U.rand(0, U.TAU), r = U.rand(25, 75);
                this.projs.push({ kind: 'bomblet', sx: p.tx, sy: p.ty - 10, x: p.tx, y: p.ty, tx: p.tx + Math.cos(a) * r, ty: p.ty + Math.sin(a) * r * 0.7, t: 0, T: U.rand(0.35, 0.55), arc: 40, ang: 0 });
              }
            }
          } else if (p.kind === 'bomblet') {
            this.explode(p.tx, p.ty, 34, [14, 24], null, false);
          } else if (p.kind === 'barrel') {
            this.zones.push({ kind: 'fire', x: p.tx, y: p.ty, r: 68, t: 0, T: 4, dps: p.dps, tick: 0 });
            this.addFx({ kind: 'explosion', x: p.tx, y: p.ty, r: 50, T: 0.5, fire: true });
            this.sfx({ n: 'fire', x: p.tx });
          } else if (p.kind === 'flask') {
            this.zones.push({ kind: 'toxic', x: p.tx, y: p.ty, r: 66, t: 0, T: 4, dps: p.dps, tick: 0, slow: 0.6 });
            this.sfx({ n: 'splash', x: p.tx }, 0.6);
          } else if (p.kind === 'waterball') {
            this.zones.push({ kind: 'mud', x: p.tx, y: p.ty, r: 64, t: 0, T: p.dur, tick: 0 });
            this.addFx({ kind: 'splashBig', x: p.tx, y: p.ty, r: 60, T: 0.6 });
            this.sfx({ n: 'splash', x: p.tx }, 0.8);
          } else if (p.kind === 'pot') {
            this.disableTower(p.tower, p.dur);
            // marca visual da sabotagem (tinta rosa ou placa de greve) enquanto a torre fica parada
            if (p.tower && this.towers.includes(p.tower)) { p.tower.sabKey = p.skey; p.tower.sabDur = p.dur; p.tower.sabEnd = this.time + p.dur; }
            this.addFx({ kind: 'sabhit', skey: p.skey, x: p.tx, y: p.ty, T: 1.0 });
            this.sfx({ n: 'sabotage', x: p.tx });
          } else if (p.kind === 'fireball') {
            this.disableTower(p.tower, p.dur);
            if (p.tower) p.tower.fireT = Math.max(p.tower.fireT || 0, p.dur);
            // o saco de dinheiro estoura em notas e moedas (a torre "comprada" e desenhada no vfx.js pelo fireT)
            this.addFx({ kind: 'cash', x: p.tx, y: p.ty + 20, r: 52, T: 0.9 });
            for (const u of this.units) if (!u.dead && U.dist(u.x, u.y, p.tx, p.ty + 20) < 55) this.hitUnit(u, 30);
            this.sfx({ n: 'boom', x: p.tx }, 0.7);
          }
        }
        break;
      }
      case 'gust': {
        p.t += dt;
        const k = Math.min(1, p.t / p.T);
        p.x = U.lerp(p.sx, p.tx, k); p.y = U.lerp(p.sy, p.ty, k);
        if (k >= 1) {
          p.done = true;
          let n = 0;
          for (const e of this.enemies) {
            if (!this.targetable(e)) continue;
            if (!U.inRange(e.x - p.gx, e.y - p.gy, p.r)) continue;
            const fly = e.flying;
            this.damage(e, U.roll(p.dmg) * (fly ? 2 : 1), 'phys', null);
            if (e.dead) continue;
            this.push(e, p.push * (fly ? 1.5 : 1));
            if (p.shred) this.shred(e, p.shred, 4);
            if (p.blind) this.blind(e, p.blind);
            if (p.sky && fly) this.ground(e, p.sky);
            n++;
          }
          this.addFx({ kind: p.sand ? 'sandburst' : 'gustHit', x: p.gx, y: p.gy, r: p.r, T: 0.5 });
        }
        break;
      }
      case 'bolt': {
        const mx = p.vx * dt, my = p.vy * dt;
        p.x += mx; p.y += my;
        p.left -= Math.hypot(mx, my);
        for (const e of this.enemies) {
          if (!this.targetable(e) || p.hit.has(e)) continue;
          if (e.T.stealth && !e.revealed) continue;
          if (U.dist(p.x, p.y, e.x, this.hitY(e)) < e.T.size + 9) {
            p.hit.add(e);
            let dmg = U.roll(p.dmg) * this.shieldMul(e, p.ox, p.oy);
            if (p.crit && Math.random() < p.crit) {
              dmg *= 3;
              this.text(e.x, e.y - 40, 'Crítico!', '#ff6b4a', 16);
            }
            this.damage(e, dmg, 'phys', null);
            this.addFx({ kind: 'hit', x: e.x, y: this.hitY(e), T: 0.3 });
            if (p.exp) {
              this.explode(e.x, e.y, 60, [p.exp * 0.8, p.exp * 1.2], null, false, 'cash');
              p.left = 0;
              break;
            }
            p.pierce--;
            if (p.pierce <= 0) break;
          }
        }
        if (p.left <= 0 || p.pierce <= 0 || p.x < -40 || p.x > W + 40 || p.y < -40 || p.y > H + 40) p.done = true;
        break;
      }
      case 'hawk': {
        const tg = p.target;
        if (!p.back) {
          const alive = tg && !tg.dead && !tg.burrowed && !tg.reached;
          if (alive) { p.tx = tg.x; p.ty = this.hitY(tg); }
          const dx = p.tx - p.x, dy = p.ty - p.y, d = Math.hypot(dx, dy);
          const step = 400 * dt;
          p.ang = Math.atan2(dy, dx);
          if (d <= step + 4) {
            if (alive) {
              this.damage(tg, p.dmg, 'phys', p.owner);
              this.stun(tg, 0.6);
              this.addFx({ kind: 'lpop', x: p.tx, y: p.ty, T: 0.45 });
              this.sfx({ n: 'claw', x: p.tx }, 0.6);
            }
            p.back = true;
          } else { p.x += (dx / d) * step; p.y += (dy / d) * step; }
        } else {
          const h = p.owner;
          const dx = h.x - p.x, dy = h.y - 30 - p.y, d = Math.hypot(dx, dy);
          const step = 430 * dt;
          p.ang = Math.atan2(dy, dx);
          if (d <= step + 4 || h.dead) p.done = true;
          else { p.x += (dx / d) * step; p.y += (dy / d) * step; }
        }
        break;
      }
    }
  }

  // agua da cisterna: molha o alvo e quem estiver perto
  splash(p, tg) {
    const x = tg ? tg.x : p.tx, y = tg ? tg.y : p.ty + 20;
    if (tg) {
      this.damage(tg, p.dmg, 'phys', null, 'water');
      this.wet(tg, p.wet);
      this.slow(tg, p.slow, 1.4);
    }
    for (const e of this.enemies) {
      if (e === tg || !this.targetable(e) || !U.inRange(e.x - x, e.y - y, p.splash)) continue;
      if (p.big) this.damage(e, p.dmg * 0.5, 'phys', null, 'water');
      this.wet(e, p.wet);
      this.slow(e, p.slow, 1.0);
    }
    this.addFx({ kind: p.big ? 'splashBig' : 'splash', x, y, r: p.splash, T: 0.45 });
  }

  updateZone(z, dt) {
    z.t += dt;
    if (z.kind === 'fire' || z.kind === 'toxic') {
      z.tick -= dt;
      if (z.tick <= 0) {
        z.tick = 0.25;
        for (const e of this.enemiesIn(z.x, z.y, z.r, true)) {
          this.damage(e, z.dps * 0.25, 'true', null, z.kind === 'fire' ? 'fire' : null);
          if (z.slow) this.slow(e, z.slow, 0.4);
        }
      }
    } else if (z.kind === 'mud') {
      z.tick -= dt;
      if (z.tick <= 0) {
        z.tick = 0.25;
        for (const e of this.enemiesIn(z.x, z.y, z.r, true)) { this.slow(e, 0.5, 0.4); this.wet(e, 1.5); }
      }
    } else if (z.kind === 'tornado') {
      // anda para tras no caminho
      z.d = Math.max(0, z.d - 75 * dt);
      const q = z.path.at(z.d, {});
      z.x = q.x; z.y = q.y;
      for (const e of this.enemies) {
        if (z.hit.has(e) || !this.targetable(e)) continue;
        if (!U.inRange(e.x - z.x, e.y - z.y, z.r + e.T.size)) continue;
        z.hit.add(e);
        this.damage(e, z.dmg, 'phys', null);
        this.stun(e, 1.1);
        this.push(e, 30);
      }
      if (z.d <= 0) z.t = z.T;
    } else if (z.kind === 'storm') {
      const due = Math.floor((z.t / z.T) * z.n);
      while (z.done < Math.min(due, z.n)) {
        z.done++;
        const a = U.rand(0, U.TAU), r = U.rand(0, z.r);
        const x = z.x + Math.cos(a) * r, y = z.y + Math.sin(a) * r * 0.7;
        for (const e of this.enemiesIn(x, y, 40, false)) this.damage(e, 32, 'magic', null, 'shock');
        this.addFx({ kind: 'skybolt', x, y, T: 0.5, small: true });   // diamante caindo (js/satira.js)
        this.sfx({ n: 'zap', x }, 0.4);
      }
    }
    if (z.t >= z.T) z.done = true;
  }

  // ------------------------------------------------------------ ciclo
  lose() {
    if (this.state === 'lost' || this.state === 'won') return;
    this.state = 'lost';
    this.endTime = this.time;
    this.sfx('defeat');
  }

  win() {
    this.state = 'won';
    this.endTime = this.time;
    const r = this.lives / this.maxLives;
    this.stars = r >= 0.9 ? 3 : r >= 0.3 ? 2 : 1;
    this.sfx('victory');
  }

  updateFlood(dt) {
    const C = this.floodCfg;
    if (!C) return;
    if (this.state === 'running' || this.flood > 0) {
      if (this.floodLeft > 0) {
        this.floodLeft -= dt;
        this.flood = Math.min(1, this.flood + dt / C.rise);
        if (this.floodLeft <= 0) { this.floodLeft = 0; this.floodT = C.every; this.events.push({ kind: 'floodEnd' }); }
      } else {
        this.flood = Math.max(0, this.flood - dt / C.rise);
        if (this.state !== 'running') return;
        this.floodT -= dt;
        if (!this.floodWarned && this.floodT <= C.warn) { this.floodWarned = true; this.events.push({ kind: 'floodWarn' }); this.sfx('windWarn'); }
        if (this.floodT <= 0) { this.floodLeft = C.dur; this.floodWarned = false; this.events.push({ kind: 'flood' }); this.sfx('water', 0.8); }
      }
    }
    // torres em lote baixo alagado param
    if (this.flood > 0.5) for (const t of this.towers) if (t.spot && t.spot.low) t.disabledT = Math.max(t.disabledT, 0.2);
  }

  // Coracao da Fumaca: em cada fase de vida vira fumaca, volta pela estrada e chama possuidos; sufoca as torres perto
  updateHeart(e, dt) {
    const T = e.T;
    e.phase = e.phase || 0;
    if (e.smokeT > 0) {
      e.smokeT -= dt;
      if (e.smokeT <= 0) { e.untargetable = false; this.addFx({ kind: 'court', x: e.x, y: e.y, r: 70, T: 1.0 }); }
      if (e.smokeT <= 0) this.sfx({ n: 'heartBack', x: e.x });
    }
    if (e.phase < T.phases.length && e.hp < e.maxHp * T.phases[e.phase]) {
      e.phase++;
      e.smokeT = 2.4; e.untargetable = true;
      // redemoinho de papeis do processo e carimbos (js/satira.js)
      this.addFx({ kind: 'court', out: true, x: e.x, y: e.y, r: 80, T: 1.2 });
      this.addFx({ kind: 'shake', T: 0.5, amp: 6 });
      e.d = Math.max(0, e.d - T.smokeBack);
      this.placeEnemy(e);
      const S = T.smokeSpawn;
      for (let k = 0; k < S.n; k++) this.spawn(S.types[k % S.types.length], e.pathIdx, Math.max(0, e.d - 10 - k * 9));
      this.text(e.x, e.y - 70, 'Entrou com recurso!', '#c9b8e8', 18);
      this.sfx({ n: 'bossDie', x: e.x }, 0.5);
      this.sfx({ n: 'heartSmoke', x: e.x });
    }
    // torres perto atiram mais devagar (a fumaca sufoca)
    for (const t of this.towers) if (U.inRange(t.x - e.x, t.y - e.y, T.choke.r)) t.chokeT = 0.2;
  }

  updateStorm(dt) {
    const C = this.stormCfg;
    if (!C || this.state !== 'running') return;
    if (this.stormLeft > 0) {
      this.stormLeft -= dt;
      this.stormGustT -= dt;
      if (this.stormGustT <= 0) { this.stormGustT = 2.2; this.sfx('wind', 0.8); }
      if (this.stormLeft <= 0) { this.stormLeft = 0; this.stormT = C.every; this.events.push({ kind: 'stormEnd' }); }
      return;
    }
    this.stormT -= dt;
    if (!this.stormWarned && this.stormT <= C.warn) { this.stormWarned = true; this.events.push({ kind: 'stormWarn' }); this.sfx('windWarn'); }
    if (this.stormT <= 0) {
      this.stormLeft = C.dur; this.stormWarned = false; this.stormGustT = 0;
      this.events.push({ kind: 'storm' });
    }
  }

  update(dt) {
    if (this.state === 'won' || this.state === 'lost') {
      this.ageFx(dt);
      return;
    }
    this.time += dt;

    while (this.queue.length && this.queue[0].t <= this.time) {
      const q = this.queue.shift();
      this.spawn(q.type, q.p, 0);
    }
    if (this.state === 'running' && this.wave < this.totalWaves) {
      if (this.countdown < 0) {
        if (!this.queue.length) { this.countdown = this.countdownMax = this.L.gap || 16; }
      } else {
        this.countdown -= dt;
        if (this.countdown <= 0) this.startWave(this.wave);
      }
    }

    if (this.timers.length) {
      const due = this.timers.filter(t => t.t <= this.time);
      if (due.length) {
        this.timers = this.timers.filter(t => t.t > this.time);
        for (const t of due) t.fn();
      }
    }

    for (const k in this.spells) this.spells[k].cd = Math.max(0, this.spells[k].cd - dt);
    for (const f of this.forks) { if (f.cd > 0) f.cd -= dt; if (f.flip > 0) f.flip -= dt; }
    this.updateStorm(dt);
    this.updateFlood(dt);
    this.updateAuras(dt);

    for (const e of this.enemies) if (!e.dead && !e.reached) this.updateEnemy(e, dt);
    for (const u of this.units) if (!u.removed) this.updateUnit(u, dt);
    this.updateHerd(dt);
    for (const t of this.towers) this.updateTower(t, dt);
    for (const p of this.projs) if (!p.done) this.updateProj(p, dt);
    for (const z of this.zones) this.updateZone(z, dt);

    this.enemies = this.enemies.filter(e => !e.dead && !e.reached);
    if (this.units.some(u => u.removed)) this.units = this.units.filter(u => !u.removed);
    this.projs = this.projs.filter(p => !p.done);
    this.zones = this.zones.filter(z => !z.done);
    this.ageFx(dt);

    if (this.state === 'running' && this.wave >= this.totalWaves && !this.queue.length && !this.enemies.length && this.lives > 0) this.win();
  }

  ageFx(dt) {
    if (this.headless) return;
    for (const f of this.fx) f.t += dt;
    this.fx = this.fx.filter(f => f.t < f.T);
  }
}
