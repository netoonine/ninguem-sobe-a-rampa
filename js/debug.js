'use strict';
// Ferramentas de teste (so ativas com parametros na URL, ex.: index.html#fase=2&ff=90&save=full)

(function () {
  const h = location.hash;
  if (!h || h.length < 2) return;
  const P = {};
  h.slice(1).split('&').forEach(kv => { const [k, v] = kv.split('='); P[k] = v == null ? '1' : decodeURIComponent(v); });
  window.__DBG__ = P;

  window.addEventListener('error', ev => {
    const d = document.createElement('div');
    d.style.cssText = 'position:fixed;left:0;top:0;right:0;background:#a00;color:#fff;font:14px monospace;padding:8px;z-index:9;white-space:pre-wrap';
    d.textContent = 'ERRO: ' + ev.message + '\n' + (ev.error && ev.error.stack ? ev.error.stack : ev.filename + ':' + ev.lineno);
    document.body.appendChild(d);
  });

  // aplicado no App.init, antes de abrir a fase
  window.DBG = {
    P,
    applySave() {
      const D = Save.data;
      if (P.save === 'full') {
        D.stars = DATA.LEVELS.map(() => 3);
        D.chal = DATA.LEVELS.map((_, i) => i < 3);
        D.seen = Object.keys(DATA.ENEMIES);
        D.heroXp = 4400;
        D.heroXps = { jaci: 4400 };
        D.towersSeen = DATA.TOWER_ORDER.slice();
        D.tips = ['high', 'ruin', 'gate', 'storm'];
        if (P.up) for (const k in D.up) D.up[k] = parseInt(P.up, 10);
      } else if (P.save === 'mid') {
        D.stars = DATA.LEVELS.map((_, i) => (i < 4 ? 3 - (i % 2) : 0));
        D.seen = ['raider', 'jackal', 'nomad', 'scorpion', 'vulture', 'shaman', 'beetle', 'brute', 'djinn', 'golem', 'warlord', 'bulwark'];
        D.heroXp = 1500;
        D.heroXps = { jaci: 1500 };
      }
      if (P.lo) D.loadout = P.lo.split(',');
      if (P.notips) { D.tips = ['high', 'ruin', 'gate', 'storm', 'charm', 'night']; D.towersSeen = DATA.TOWER_ORDER.slice(); D.heroesSeen = DATA.HERO_ORDER.slice(); }
    },
  };

  function bot(g, t) {
    const plan = (P.plan || 'archer,barracks,mage,artillery,cistern,windmill,banner,archer,mage,artillery,archer,mage,windmill').split(',').filter(x => g.canBuildType(x));
    if (!plan.length) plan.push(g.loadout[0]);
    const specs = { archer: P.sa || 'ballista', mage: P.sm || 'lightning', artillery: P.sr || 'mortar', barracks: P.sb || 'lancers', cistern: P.sc || 'geyser', windmill: P.sw || 'tornado', banner: P.sn || 'drums', market: P.sk || 'bazaar' };
    const ranked = g.spots.map(s => {
      let c = 0;
      for (const p of g.paths) for (let k = 0; k < p.pts.length; k += 3) {
        const [x, y] = p.pts[k];
        if (x < 0 || x > W || y < 0 || y > H) continue;
        if (U.inRange(x - s.x, y - s.y, 160)) c++;
      }
      return { s, c };
    }).sort((a, b) => b.c - a.c);
    let ti = 0, think = 0, placed = false;
    const steps = Math.round(t / STEP);
    for (let i = 0; i < steps && g.state !== 'won' && g.state !== 'lost'; i++) {
      think -= STEP;
      if (think <= 0) {
        think = 0.3;
        const next = ranked[ti];
        const type = plan[ti % plan.length];
        if (next && next.s.ruin && g.gold >= next.s.ruin) g.clearRuin(next.s);
        if (next && !next.s.ruin && g.gold >= DATA.TOWERS[type].tiers[0].cost) { g.build(next.s, type); ti++; }
        else if (!next || ti > ranked.length * 0.5) {
          for (const tw of g.towers) {
            if (!tw.spec && tw.tier < 3) { if (g.upgrade(tw)) break; }
            else if (!tw.spec) { if (g.specialize(tw, specs[tw.type])) break; }
            else { const ab = DATA.SPECS[tw.spec].abilities.find(a => g.abilityCost(tw, a) != null); if (ab && g.buyAbility(tw, ab.id)) break; }
          }
        }
        if (!placed && !g.hero.disabled) { const b = g.towers.find(x => x.type === 'barracks'); if (b) { g.moveHero(b.rally.x + 30, b.rally.y); placed = true; } }
        if (g.state === 'prewave' && g.towers.length >= 3) g.callWave();
        if (!g.noSpells && g.spells.fury.cd <= 0) { const c = g.densest(640, 360, 4000, false, 55); if (c && g.enemiesIn(c.x, c.y, 55, false).length >= 4) g.castSpell('fury', c.x, c.y); }
      }
      g.update(STEP);
      if (i < steps - 90) { g.fx.length = 0; g.sounds.length = 0; g.events.length = 0; }
    }
  }

  // #ranges: desenha o alcance de um arqueiro nivel 1 em cada lote (revisao do posicionamento)
  if (P.ranges) {
    window.addEventListener('load', () => {
      const orig = Render.level;
      Render.level = function (c, g, v) {
        orig.call(this, c, g, v);
        c.save();
        for (const s of g.spots) {
          A.ell(c, s.x, s.y, 150, 150 * U.YS, 'rgba(80,200,255,0.05)', 'rgba(40,120,220,0.55)', 1.2);
          A.text(c, String(s.i), s.x, s.y - 2, 14, '#fff', 'center');
        }
        c.restore();
      };
    });
  }

  window.addEventListener('load', () => {
    setTimeout(() => {
      if (P.screen) App.go(P.screen);
      if (P.panel) WorldMap.openPanel(parseInt(P.panel, 10));
      if (P.pmode && WorldMap.panel != null) WorldMap.setMode(WorldMap.panel, P.pmode);
      if (P.fase && App.game) {
        const g = App.game;
        if (P.gold) g.gold = parseInt(P.gold, 10);
        if (P.ff) bot(g, parseFloat(P.ff));
        if (P.storm) { g.state = 'running'; g.stormLeft = g.stormCfg ? g.stormCfg.dur - 3 : 0; }
        if (P.gate) g.toggleFork(0);
        if (P.sel) {
          const [kind, idx] = [P.sel.replace(/\d+/, ''), parseInt(P.sel.replace(/\D+/, ''), 10)];
          if (kind === 'spot') App.lv.sel = { spot: g.spots[idx] };
          if (kind === 'tower') App.lv.sel = { tower: g.towers[idx], spot: g.towers[idx].spot };
          if (kind === 'enemy') App.lv.sel = { enemy: g.enemies[idx] };
        }
        if (P.mx) { UI.mx = parseFloat(P.mx); UI.my = parseFloat(P.my); }
        if (P.pause) App.lv.paused = true;
        if (P.end) { g.state = P.end; g.stars = 3; g.endTime = 300; App.lv.overlay = true; App.lv.endT = 3; if (P.unl) App.lv.unlocked = P.unl; }
        if (P.clearq) App.lv.noticeQ = [];
      }
      if (P.mx && !P.fase) { UI.mx = parseFloat(P.mx); UI.my = parseFloat(P.my); }
    }, 50);
  });
})();
