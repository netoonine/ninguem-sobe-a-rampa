'use strict';
// Inicializacao, salvamento, laco principal e entrada.

const Save = {
  key: (typeof window !== 'undefined' && window.__SAVE_KEY__) || 'ninguem_sobe_a_rampa_v1',
  data: null,
  def() {
    return {
      stars: DATA.LEVELS.map(() => 0), chal: DATA.LEVELS.map(() => false),
      up: { archer: 0, mage: 0, artillery: 0, barracks: 0, eng: 0, cmd: 0, charm: 0, spells: 0 },
      seen: [], heroXp: 0, music: true, sfx: true, cine: true, loadout: [], towersSeen: DATA.START_TOWERS.slice(), tips: [],
      hero: 'jaci', heroXps: {}, talents: {}, heroesSeen: ['jaci', 'benzedeira'], side: null,
      heroic: DATA.LEVELS.map(() => false), iron: DATA.LEVELS.map(() => false), endless: 0,
    };
  },
  load() {
    let raw = null;
    try { if (window.__NATIVE_SAVE__) raw = window.__NATIVE_SAVE__; } catch (e) { /* sem ponte nativa */ }
    if (!raw) { try { raw = localStorage.getItem(this.key); } catch (e) { raw = null; } }
    let d = null;
    try { d = raw ? JSON.parse(raw) : null; } catch (e) { d = null; }
    const def = this.def();
    this.data = Object.assign(def, d || {});
    // o Object.assign acima ja trocou def.up pelo up do save: as categorias novas vem de um padrao novo
    this.data.up = Object.assign(this.def().up, (d && d.up) || {});
    while (this.data.stars.length < DATA.LEVELS.length) this.data.stars.push(0);
    while (this.data.chal.length < DATA.LEVELS.length) this.data.chal.push(false);
    while (this.data.heroic.length < DATA.LEVELS.length) this.data.heroic.push(false);
    while (this.data.iron.length < DATA.LEVELS.length) this.data.iron.push(false);
    // quem ja tinha progresso nao recebe aviso de "nova torre" das que ja usava
    if (d && !d.towersSeen) this.data.towersSeen = this.unlockedTowers();
    // herois: a XP antiga (so a Jaci existia) vira a XP da Jaci
    if (this.data.heroXps.jaci == null) this.data.heroXps.jaci = this.data.heroXp || 0;
    this.applySide();
    // estrelas gastas nunca passam das ganhas
    if (this.spentStars() > this.totalStars()) for (const k in this.data.up) this.data.up[k] = 0;
    return this.data;
  },
  // chapa escolhida: herois da vez, turma rival e um heroi valido da chapa
  applySide() {
    DATA.setSide(this.data.side || 'R');
    if (typeof SPR !== 'undefined' && SPR.setChapa) SPR.setChapa(DATA.SIDE);   // torres na cor da chapa
    if (!this.heroUnlocked(this.data.hero)) this.data.hero = DATA.HERO_ORDER[0];
  },
  setSide(side) {
    this.data.side = side;
    this.applySide();
    this.write();
  },
  write() {
    const s = JSON.stringify(this.data);
    try { localStorage.setItem(this.key, s); } catch (e) { /* armazenamento indisponivel */ }
    try {
      if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.save) window.webkit.messageHandlers.save.postMessage(s);
    } catch (e) { /* fora do app nativo */ }
  },
  totalStars() {
    return this.data.stars.reduce((a, b) => a + b, 0) + this.data.chal.filter(Boolean).length
      + this.data.heroic.filter(Boolean).length + this.data.iron.filter(Boolean).length;
  },
  maxStars() { return DATA.LEVELS.length * 6; },
  spentStars() {
    let n = 0;
    for (const k in this.data.up) for (let i = 0; i < this.data.up[k]; i++) n += DATA.UPGRADE_COST[i];
    return n;
  },
  freeStars() { return this.totalStars() - this.spentStars(); },
  heroUnlocked(id) {
    const H = DATA.HEROES[id];
    return !!H && H.side === DATA.SIDE && (H.unlock == null || this.data.stars[H.unlock] > 0);
  },
  heroXpOf(id) { return this.data.heroXps[id] || 0; },
  unlockedTowers() {
    const u = DATA.START_TOWERS.slice();
    DATA.LEVELS.forEach((L, i) => { if (this.data.stars[i] > 0) for (const t of [].concat(L.unlock || [])) if (!u.includes(t)) u.push(t); });
    return DATA.TOWER_ORDER.filter(t => u.includes(t));
  },
};

const App = {
  screen: 'title', game: null, lv: null, time: 0, scale: 1, dpr: 1, offX: 0, offY: 0,
  canvas: null, ctx: null,

  init() {
    this.canvas = document.getElementById('game');
    this.ctx = this.canvas.getContext('2d');
    Save.load();
    if (window.DBG) DBG.applySave();
    Snd.musicOn = Save.data.music; Snd.sfxOn = Save.data.sfx;
    window.addEventListener('resize', () => this.resize());
    this.resize();
    this.bindInput();
    // atalho de desenvolvimento: #fase=N abre a fase direto
    const m = /fase=(\d+)/.exec(location.hash);
    if (m) this.startLevel(parseInt(m[1], 10) - 1, /mode=chal/.test(location.hash) ? 'chal' : 'normal');
    else this.go('title');
    let last = performance.now();
    let acc = 0;
    const frame = now => {
      let dt = Math.min(0.1, (now - last) / 1000);
      last = now;
      this.time += dt;
      if (this.screen === 'level' && this.game && !this.lv.paused) {
        const g = this.game;
        acc += dt * this.lv.speed * Cam.timeK();   // camera lenta (ate 0,5x) durante o close-up
        let n = 0;
        while (acc >= STEP && n < 10) { g.update(STEP); acc -= STEP; n++; }
        if (n >= 10) acc = 0;
        this.afterUpdate(dt);
      }
      this.draw(dt);
      requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  },

  resize() {
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const w = window.innerWidth, h = window.innerHeight;
    this.canvas.width = Math.round(w * dpr);
    this.canvas.height = Math.round(h * dpr);
    this.canvas.style.width = w + 'px';
    this.canvas.style.height = h + 'px';
    const s = Math.min(w / W, h / H);
    this.scale = s * dpr;
    this.dpr = dpr;
    this.offX = (w - W * s) / 2;
    this.offY = (h - H * s) / 2;
  },

  toLogical(ev) {
    const r = this.canvas.getBoundingClientRect();
    const s = this.scale / this.dpr;
    return [(ev.clientX - r.left - this.offX) / s, (ev.clientY - r.top - this.offY) / s];
  },

  bindInput() {
    const cv = this.canvas;
    cv.addEventListener('mousemove', ev => { const [x, y] = this.toLogical(ev); UI.mx = x; UI.my = y; });
    cv.addEventListener('mouseleave', () => { UI.mx = -1; UI.my = -1; });
    cv.addEventListener('mousedown', ev => {
      Snd.init();
      const [x, y] = this.toLogical(ev);
      UI.mx = x; UI.my = y;
      if (ev.button === 2 && this.screen === 'level') { Level.cancel(); return; }
      // com zoom, apertar no mundo espera soltar: toque vira clique, arrasto anda com a camera (js/camera.js)
      if (Cam.pointerDown(x, y, ev.button)) return;
      UI.click(x, y, ev.button);
    });
    window.addEventListener('mousemove', ev => { if (Cam.press) { const [x, y] = this.toLogical(ev); Cam.pointerMove(x, y); } });
    window.addEventListener('mouseup', ev => { const [x, y] = this.toLogical(ev); Cam.pointerUp(x, y); });
    // zoom livre: roda do mouse (ou pinca do trackpad) e dois dedos na tela
    cv.addEventListener('wheel', ev => {
      if (this.screen !== 'level') return;
      ev.preventDefault();
      const [x, y] = this.toLogical(ev);
      Cam.wheel(x, y, ev.deltaY * (ev.deltaMode === 1 ? 33 : ev.deltaMode === 2 ? 600 : 1), ev.ctrlKey);
    }, { passive: false });
    cv.addEventListener('touchstart', ev => Cam.touch(ev, 'start'), { passive: false });
    cv.addEventListener('touchmove', ev => Cam.touch(ev, 'move'), { passive: false });
    cv.addEventListener('touchend', ev => Cam.touch(ev, 'end'), { passive: false });
    cv.addEventListener('touchcancel', ev => Cam.touch(ev, 'end'), { passive: false });
    cv.addEventListener('contextmenu', ev => ev.preventDefault());
    window.addEventListener('keydown', ev => {
      Snd.init();
      if (this.screen !== 'level') {
        if (ev.key === 'Escape') {
          if (this.screen === 'map' && WorldMap.panel != null) { WorldMap.panel = null; return; }
          if (this.screen !== 'title') this.go(this.screen === 'map' ? 'title' : 'map');
        }
        return;
      }
      const lv = this.lv, g = this.game;
      if (lv.overlay) return;
      const k = ev.key.toLowerCase();
      if (k === ' ' || k === 'p') { lv.paused = !lv.paused; ev.preventDefault(); }
      else if (k === 'escape') { if (lv.mode || lv.sel) Level.cancel(); else lv.paused = !lv.paused; }
      if (lv.paused) return;
      if (k === '1') Level.castMode('fury');
      else if (k === '2') Level.castMode('riders');
      else if (k === '3') Level.castMode('stampede');
      else if (k === 'h') Level.toggleHero();
      else if (k === 'f') lv.speed = lv.speed === 1 ? 2 : 1;
      else if (k === 't') Level.cyclePrio();
      else if (k === 'g' && g.forks.length) Level.toggleFork(0);
      else if (k === 'n' || k === 'w') { const b = g.callWave(); if (b) g.text(W / 2, 120, '+' + b + ' de verba', '#ffd54a', 22); }
      else if (k === '0') Cam.resetZoom();   // zoom livre: 0 volta ao mapa inteiro, + e - aproximam e afastam
      else if (k === '+' || k === '=') Cam.zoomAt(W / 2, H / 2, 1.25);
      else if (k === '-') Cam.zoomAt(W / 2, H / 2, 0.8);
    });
  },

  setMusic(on) { Snd.setMusic(on); Save.data.music = on; Save.write(); },
  setCine(on) { Save.data.cine = on; Save.write(); if (!on) Cam.stopCine(); Snd.play('click'); },
  setSfx(on) { Snd.setSfx(on); Save.data.sfx = on; Save.write(); if (on) Snd.play('click'); },

  go(screen) {
    if (this.screen === 'level' && screen !== 'level') this.game = null;
    this.screen = screen;
    UI.hot = null;
    WorldMap.panel = null;
    if (screen === 'title') Title.demo = null;
    Snd.startTrack(screen === 'level' ? 'battle' : 'calm');
    if (screen !== 'level') Snd.stopAmb();
    Snd.play('click');
  },

  // regras de cada modo: desafio (da fase), heroico (1 vida, inimigos +15%), ferro (1 vida, onda unica, 3 torres)
  rulesFor(i, mode) {
    const L = DATA.LEVELS[i];
    if (mode === 'chal') return L.challenge.rules;
    if (mode === 'heroic') return { lives: 1, hpMul: 1.15 };
    if (mode === 'iron') return { lives: 1, only: L.iron || ['archer', 'barracks', 'artillery'] };
    return {};
  },

  slotsFor(i, mode) {
    const rules = this.rulesFor(i, mode);
    return rules.slots || DATA.SLOTS;
  },

  // torres levadas para a fase: as escolhidas no arsenal, respeitando as regras e o limite
  loadoutFor(i, mode) {
    const rules = this.rulesFor(i, mode);
    const slots = this.slotsFor(i, mode);
    let usable = Save.unlockedTowers();
    if (rules.only) usable = usable.filter(t => rules.only.includes(t));
    if (rules.ban) usable = usable.filter(t => !rules.ban.includes(t));
    if (usable.length <= slots) return usable;
    const pick = (Save.data.loadout || []).filter(t => usable.includes(t)).slice(0, slots);
    for (const t of usable) if (pick.length < slots && !pick.includes(t)) pick.push(t);
    return DATA.TOWER_ORDER.filter(t => pick.includes(t));
  },

  // jogo vazio para textos de interface fora da fase
  dummyGame() {
    if (!this._dummy) this._dummy = new Game(0, { headless: true });
    this._dummy.up = Object.assign({}, Save.data.up);
    return this._dummy;
  },

  startLevel(i, mode, loadout) {
    mode = mode || 'normal';
    if (typeof VSPR !== 'undefined') VSPR.release();   // herois grandes do inicio/tela de herois: ~280 MB decodificados
    const L = DATA.LEVELS[i];
    loadout = loadout || this.loadoutFor(i, mode);
    const hero = Save.data.hero;
    this.game = new Game(i, { upgrades: Save.data.up, hero, heroXp: Save.heroXpOf(hero), talents: Save.data.talents[hero] || [], seen: Save.data.seen, loadout, mode, rules: this.rulesFor(i, mode) });
    this.lv = {
      sel: null, mode: null, paused: false, speed: 1, overlay: false, endT: 0, noticeQ: [], starSnd: [], newStars: 0, saved: false, boss: false,
      lastWave: 0, banner: null, tutorial: i === 0 && !Save.data.stars[0] && mode === 'normal', tut: { t: 0 }, unlocked: null,
    };
    // avisos: torres novas no arsenal e novidades do mapa
    const lv = this.lv;
    for (const t of this.game.loadout) if (!Save.data.towersSeen.includes(t)) { lv.noticeQ.push({ kind: 'tower', type: t, t: 0 }); Save.data.towersSeen.push(t); }
    const tip = (id, icon, title, text) => { if (!Save.data.tips.includes(id)) { lv.noticeQ.push({ kind: 'tip', icon, title, text, t: 0 }); Save.data.tips.push(id); } };
    if (L.spots.some(s => s[2] === 'h')) tip('high', 'high', 'Terraço alto', 'Lotes no alto dos terraços dão +15% de alcance à torre.');
    if (L.spots.some(s => s[2] === 'r')) tip('ruin', 'ruin', 'Obra parada', 'Clique na obra parada e pague para liberar um terreno extra.');
    if (L.forks) tip('gate', 'gate', 'Manobra regimental', 'Clique na alavanca (ou G) para mandar a turma pelo outro caminho.');
    if (L.storm) tip('storm', 'sandstorm', 'Tempestade de fake news', 'De tempos em tempos, a enxurrada de mentira corta 25% do alcance das torres.');
    if (L.flood) tip('flood', 'cistern', 'Cheia da várzea', 'De tempos em tempos o rio sobe: torres nos lotes baixos (ondinhas azuis) param e os bichos do rio nadam mais rápido.');
    if (L.night || mode === 'endless') tip('night', 'mage', 'Votação de madrugada', DATA.fmt('No escuro {o:archer} enxerga 15% menos e o dano {de:mage} sobe 20%.'));
    Save.write();
    this.screen = 'level';
    UI.hot = null;
    Cam.reset();
    Snd.startTrack('battle', true);
    Snd.play('open');
    Snd.startAmb(this.game);
  },

  afterUpdate(dt) {
    const g = this.game, lv = this.lv;
    for (const s of g.sounds) Snd.play(s.name, s.vol);
    g.sounds.length = 0;
    while (g.events.length) {
      const ev = g.events.shift();
      Snd.event(ev.kind);
      if (ev.kind === 'storm') lv.banner = { t: 0, text: 'Tempestade de fake news!', sub: 'Alcance das torres -25%', storm: true };
      else if (ev.kind === 'floodWarn') lv.banner = { t: 0, text: 'O rio está subindo!', sub: 'A cheia vai alagar os lotes baixos', storm: true };
      else if (ev.kind === 'flood') lv.banner = { t: 0, text: 'Cheia!', sub: 'Torres nos lotes baixos param; bichos do rio nadam mais rápido', storm: true };
      else if (ev.kind === 'heartFreed') lv.banner = { t: 0, text: 'Recurso negado!', sub: 'O candidato rival não subiu a rampa', boss: true };
      else if (ev.kind === 'floodEnd') lv.banner = { t: 0, text: 'A água baixou', sub: 'Os lotes baixos voltam a funcionar' };
    }
    Cam.watch(g, lv);   // close-ups: adversario novo, chefe chegando e habilidade do heroi (js/camera.js)
    const boss = g.enemies.find(e => e.T.boss);
    if (!lv.boss && boss) {
      lv.boss = true;
      Snd.startTrack('boss');
      Snd.play('bossCome');
      lv.banner = { t: 0, text: shortName(boss.T.name), sub: 'chegou à Esplanada!', boss: true };
    }
    if (lv.boss && !g.enemies.some(e => e.T.boss) && g.state === 'running') { lv.boss = false; Snd.startTrack('battle'); }
    if ((g.state === 'won' || g.state === 'lost') && !lv.saved) {
      lv.saved = true;
      this.endLevel(g.state === 'won');
      setTimeout(() => { if (this.lv === lv) { lv.overlay = true; lv.endT = 0; } }, 1500);
    }
  },

  endLevel(won) {
    const g = this.game;
    if (!g) return;
    Save.data.heroXps[g.heroId] = Math.max(Save.heroXpOf(g.heroId), g.heroXp);
    if (g.heroId === 'jaci') Save.data.heroXp = Save.data.heroXps.jaci;
    Save.data.seen = [...new Set([...Save.data.seen, ...g.seen])];
    // Correnteza: guarda a onda mais longe alcancada
    if (g.mode === 'endless') {
      this.lv.record = g.wave > (Save.data.endless || 0);
      Save.data.endless = Math.max(Save.data.endless || 0, g.wave);
    }
    if (won) {
      const i = g.levelIdx;
      if (g.mode === 'chal' || g.mode === 'heroic' || g.mode === 'iron') {
        const box = g.mode === 'chal' ? Save.data.chal : Save.data[g.mode];
        this.lv.newStars = box[i] ? 0 : 1;
        box[i] = true;
      } else {
        const prev = Save.data.stars[i];
        this.lv.newStars = Math.max(0, g.stars - prev);
        Save.data.stars[i] = Math.max(prev, g.stars);
        const un = g.L.unlock;
        if (prev === 0 && un) this.lv.unlocked = [].concat(un);
      }
    }
    Save.write();
  },

  draw(dt) {
    const c = this.ctx;
    c.setTransform(1, 0, 0, 1, 0, 0);
    c.fillStyle = '#1a0d05';
    c.fillRect(0, 0, this.canvas.width, this.canvas.height);
    const s = this.scale;
    c.setTransform(s, 0, 0, s, this.offX * this.dpr, this.offY * this.dpr);
    c.save();
    c.beginPath(); c.rect(0, 0, W, H); c.clip();
    UI.begin();
    if (this.screen === 'title') Title.draw(c, dt);
    else if (this.screen === 'map') WorldMap.draw(c, dt);
    else if (this.screen === 'upgrades') Upgrades.draw(c, dt);
    else if (this.screen === 'heroes') Heroes.draw(c, dt);
    else if (this.screen === 'bestiary') Bestiary.draw(c, dt);
    else if (this.screen === 'level' && this.game) Level.draw(c, dt);
    UI.end();
    c.restore();
    this.canvas.style.cursor = Cam.dragging() ? 'grabbing' : UI.cursor;
  },
};

window.addEventListener('load', () => App.init());
