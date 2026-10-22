'use strict';
// Sprites pre-renderizados no Blender (tools/blender/*.py -> tools/sprites/empacotar.py -> js/sprites_meta.js).
// Cada familia de torre tem as proprias folhas e so carregam as das torres levadas na fase (SPR.level, chamado
// pelo render.js). O clima da fase recompoe as folhas uma vez (tom do ceu por multiplicacao) e a luz das
// lanternas, cristais e braseiros vem por cima conforme SPR.glow.
// Se uma familia nao estiver carregada, a torre continua com o desenho por codigo (art_towers.js / art2.js).

const SPR = {
  imgs: [],        // folha -> Image ou canvas recomposto com o tom do clima
  raw: [],         // folha -> Image original
  fams: {},        // familia -> 'loading' | 'ready'
  glow: 0.25,      // intensidade da luz (0 = apagada); o render.js ajusta por cenario e tempestade
  glowBase: null,  // luz base do clima da fase (o render.js usa no lugar do padrao)
  tint: null,      // tom do clima (multiplica as folhas); null = dia
  _g: null,
  famOf: { archer: ['arqueiros', 'zarabatana'], mage: 'magos', artillery: 'artilharia', barracks: 'quartel', cistern: 'cisterna', windmill: 'catavento', banner: 'estandarte', market: 'mercado' },
  // clima de cada cenario: tom do ceu sobre as torres e luz base das lanternas
  THEMES: {
    oasis: null, dunes: null, qanat: null,
    canyon: { tint: '#ffe0c2', glow: 0.34 },
    ruins: { tint: '#f4e6d2', glow: 0.3 },
    citadel: { tint: '#c4c4dc', glow: 0.5 },
    storm: { tint: '#e8dcc4', glow: 0.3 },
    ember: { tint: '#f2c2ae', glow: 0.5 },
  },

  ok(fam) { return this.fams[fam] === 'ready'; },
  get ready() { return this.ok('arqueiros'); },

  // carrega as familias pedidas (o 'comum' sempre) e solta as outras
  want(list) {
    if (typeof SPRITE_META === 'undefined') return;
    const need = new Set(['comum', 'icones', ...list].filter(f => f && SPRITE_META.fams[f]));
    for (const f of Object.keys(this.fams)) if (!need.has(f)) this.drop(f);
    for (const f of need) if (!this.fams[f]) this.loadFam(f);
  },

  // torre de uma familia fora do arsenal da fase (desafio, teste, cheat): carrega na hora, sem soltar as outras
  need(fam) {
    if (typeof SPRITE_META === 'undefined' || !fam || this.fams[fam] || !SPRITE_META.fams[fam]) return;
    this.loadFam(fam);
  },

  loadFam(fam) {
    const ids = SPRITE_META.fams[fam];
    this.fams[fam] = 'loading';
    let left = ids.length;
    const gen = this._gen;
    for (const i of ids) {
      const im = new Image();
      im.onload = () => {
        if (gen !== this._gen || this.fams[fam] !== 'loading') return;
        this.raw[i] = im;
        this.imgs[i] = this.relight(im, i);
        if (--left === 0) this.fams[fam] = 'ready';
      };
      im.onerror = () => console.warn('sprite nao carregou: ' + SPRITE_META.sheets[i]);
      im.src = SPRITE_META.sheets[i];
    }
  },

  // cores da chapa nas torres: troca folhas, familias e conjuntos do SPRITE_META pelos da chapa escolhida
  // (js/sprites_meta_r.js para a Vermelha; sem ele, fica a Verde-Amarela) e recarrega o que estava em uso
  chapa: 'V',
  _gen: 0,
  setChapa(side) {
    if (typeof SPRITE_META === 'undefined') return;
    const k = side === 'R' && typeof SPRITE_META_R !== 'undefined' ? 'R' : 'V';
    if (k === this.chapa) return;
    if (!this._metaV) this._metaV = { sheets: SPRITE_META.sheets, fams: SPRITE_META.fams, glowSheets: SPRITE_META.glowSheets, sets: SPRITE_META.sets };
    const had = Object.keys(this.fams);
    for (const f of had) this.drop(f);
    this.imgs = []; this.raw = [];
    this._gen++;
    const M = k === 'R' ? SPRITE_META_R : this._metaV;
    Object.assign(SPRITE_META, { sheets: M.sheets, fams: M.fams, glowSheets: M.glowSheets, sets: M.sets });
    this.chapa = k;
    for (const f of had) if (SPRITE_META.fams[f]) this.loadFam(f);
  },

  drop(fam) {
    for (const i of SPRITE_META.fams[fam] || []) { this.imgs[i] = null; this.raw[i] = null; }
    delete this.fams[fam];
  },

  // folha com o tom do clima: multiplica a cor e devolve o alfa original (sem getImageData)
  relight(im, i) {
    if (!this.tint || (SPRITE_META.glowSheets || []).includes(i)) return im;
    try {
      const cv = document.createElement('canvas');
      cv.width = im.width; cv.height = im.height;
      const c = cv.getContext('2d');
      c.drawImage(im, 0, 0);
      c.globalCompositeOperation = 'multiply';
      c.fillStyle = this.tint;
      c.fillRect(0, 0, cv.width, cv.height);
      c.globalCompositeOperation = 'destination-in';
      c.drawImage(im, 0, 0);
      return cv;
    } catch (err) { return im; }
  },

  setTint(tint) {
    if (tint === this.tint) return;
    this.tint = tint;
    this.raw.forEach((im, i) => { if (im) this.imgs[i] = this.relight(im, i); });
  },

  // chamado a cada quadro pelo render.js: troca de fase -> carrega as familias e aplica o clima
  level(g) {
    if (g === this._g) return;
    this._g = g;
    const lo = g.loadout || [];
    const types = lo.length && lo.length <= (DATA.SLOTS || 5) ? lo : [...new Set((g.towers || []).map(t => t.type))];
    const th = this.THEMES[g.L && g.L.theme] || null;
    this.glowBase = th ? th.glow : null;
    // com a luz de cena do js/vfx.js (Light), o tom do clima vale para a cena inteira (AMBIENT la); aqui so sem ela
    this.setTint(th && typeof Light === 'undefined' ? th.tint : null);
    const amb = (this.bgLoad && this.bgLoad(g.levelIdx) && ((this.bg.C.palms || []).length || (g.forks || []).length)) ? ['ambiente'] : [];
    this.want([].concat(...types.map(t => this.famOf[t] || []), amb));
  },

  boot() {
    if (typeof SPRITE_META === 'undefined') return;
    this.want(['arqueiros']);
  },

  // desenha o quadro f com a ancora em (x, y); flip espelha na horizontal; k escala em torno da ancora
  draw(c, f, x, y, flip, k) {
    const im = f && this.imgs[f[0]];
    if (!im) return;
    const s = (k == null ? 1 : k) / SPRITE_META.scale;
    c.imageSmoothingEnabled = true;
    c.imageSmoothingQuality = 'high';
    if (flip || k != null) {
      c.save();
      c.translate(x, y);
      c.scale(flip ? -s : s, s);
      c.drawImage(im, f[1], f[2], f[3], f[4], -f[5], -f[6], f[3], f[4]);
      c.restore();
    } else {
      c.drawImage(im, f[1], f[2], f[3], f[4], x - f[5] * s, y - f[6] * s, f[3] * s, f[4] * s);
    }
  },
};
SPR.boot();

(() => {
  const BUILD_T = 0.6;      // obra rapida (demo/testes, sem t.buildDur)
  const UP_DELAY = 0.1;     // no upgrade rapido, um respiro a mais
  const POP_T = 0.24;       // tripulacao aparece com um quique
  const SHOOT_T = 0.42;     // duracao do disparo do arqueiro
  const COMBAT_T = 1.5;     // depois do ultimo tiro, continua mirando por este tempo
  const ANIM_FPS = 12;      // loop das pecas que mexem (tecido, aneis, chamas)
  const ROWS = 6;           // fiadas da obra
  const state = new WeakMap();
  const META = () => SPRITE_META.sets;

  const easeBack = x => { const k = 1.7; x -= 1; return 1 + (k + 1) * x * x * x + k * x * x; };
  const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };

  // ---------------------------------------------------------------- familias novas (base + pecas que mexem)
  // key: conjunto do nivel; crew: tripulacao no posto; windup/cast: tempos do ataque; fire: quadro do disparo
  // papeis nos postos (S.slots[i]): 'crew' = personagem (idle + ataque), 'gun' = canhao que espelha e recua,
  // 'hammer' = martelo que sobe e bate. Tempos: windup antes do disparo (t.chargeT ou t.cd), cast depois,
  // fire = quadro do disparo; after = a animacao inteira acontece depois do tiro (municiador recarregando).
  const MAGE = (set, extra) => Object.assign({ set, kind: 'crew', anim: 'cast', fire: 3, windup: 0.22, cast: 0.42 }, extra);
  const GUNNER = set => ({ set, kind: 'crew', anim: 'fire', fire: 3, windup: 0.3, cast: 0.5 });
  const LOADER = set => ({ set, kind: 'crew', anim: 'fire', fire: 0, after: 0.25, cast: 1.2 });
  const PUSH = (set, after) => ({ set, kind: 'crew', anim: 'act', fire: 0, after: after || 0, cast: 0.6 });
  const GESTURE = (set, every, cast) => ({ set, kind: 'crew', anim: 'act', every, cast: cast || 0.9 });
  const ARCHER = set => ({ set, kind: 'archer' });
  const HUNTER = set => ({ set, kind: 'crew', anim: 'shoot', fire: 0, cast: 0.5, alt: true });
  const SALUTE = set => ({ set, kind: 'crew', anim: 'act', fire: 0, after: 0, cast: 0.9, spawn: true });
  const FAMS = {
    mage: {
      fam: 'magos',
      key: t => t.spec === 'lightning' ? 'mgL' : t.spec === 'sun' ? 'mgS' : 'mg' + Math.max(1, Math.min(3, t.tier || 1)),
      roles: {
        mg1: [MAGE('mgA')], mg2: [MAGE('mgB')], mg3: [MAGE('mgC')],
        mgL: [MAGE('mgE', { fire: 4, cast: 0.3 })], mgS: [MAGE('mgP', { beam: true })],
      },
      orbs: true,
    },
    artillery: {
      fam: 'artilharia',
      key: t => t.spec === 'mortar' ? 'arM' : t.spec === 'seismic' ? 'arS' : 'ar' + Math.max(1, Math.min(3, t.tier || 1)),
      roles: {
        ar1: [{ set: 'arT1', kind: 'gun' }, GUNNER('arG')],
        ar2: [{ set: 'arT2', kind: 'gun' }, GUNNER('arG'), LOADER('arC')],
        ar3: [{ set: 'arT3', kind: 'gun' }, GUNNER('arG'), LOADER('arC')],
        arM: [{ set: 'arTM', kind: 'gun' }, GUNNER('arR')],
        arS: [{ set: 'arH', kind: 'hammer', anim: 'slam', fire: 5, windup: 0.7, cast: 0.3 }, { set: 'arE', kind: 'crew', anim: 'fire', fire: 0, after: 0, cast: 0.6 }],
      },
    },
    cistern: {
      fam: 'cisterna',
      key: t => t.spec === 'fountain' ? 'csF' : t.spec === 'geyser' ? 'csG' : 'cs' + Math.max(1, Math.min(3, t.tier || 1)),
      roles: {
        cs1: [{ set: 'csB1', kind: 'gun' }, { set: 'csC', kind: 'crew', anim: 'act', fire: 0, after: 0.3, cast: 1.0 }],
        cs2: [{ set: 'csB2', kind: 'gun' }], cs3: [{ set: 'csB3', kind: 'gun' }], csF: [{ set: 'csB3', kind: 'gun' }],
        csG: [{ set: 'csBG', kind: 'gun' }, { set: 'csE', kind: 'crew', anim: 'act', fire: 0, after: 0.1, cast: 0.7 }],
      },
    },
    windmill: {
      fam: 'catavento',
      key: t => t.spec === 'tornado' ? 'cvT' : t.spec === 'sandblast' ? 'cvS' : 'cv' + Math.max(1, Math.min(3, t.tier || 1)),
      roles: {
        cv1: [{ set: 'cvH1', kind: 'gun' }], cv2: [{ set: 'cvH2', kind: 'gun' }],
        cv3: [{ set: 'cvH3', kind: 'gun' }, PUSH('cvM')],
        cvT: [PUSH('cvM')],
        cvS: [{ set: 'cvHS', kind: 'gun' }, PUSH('cvO')],
      },
    },
    banner: {
      fam: 'estandarte',
      key: t => t.spec === 'drums' ? 'esD' : t.spec === 'watch' ? 'esW' : 'es' + Math.max(1, Math.min(3, t.tier || 1)),
      roles: {
        es1: [GESTURE('esP', 5)], es2: [GESTURE('esC', 6, 1.2)], es3: [GESTURE('esA', 5, 1.0)],
        esD: [{ set: 'esT', kind: 'crew', anim: 'act', loopWhen: t => t.warT > 0 }],
        esW: [GESTURE('esV', 3, 1.5)],
      },
    },
    market: {
      fam: 'mercado',
      key: t => t.spec === 'bazaar' ? 'mkB' : t.spec === 'treasury' ? 'mkT' : 'mk' + Math.max(1, Math.min(3, t.tier || 1)),
      roles: {
        mk1: [GESTURE('mkM', 4)], mk2: [GESTURE('mkM', 4)], mk3: [GESTURE('mkM', 4)],
        mkB: [GESTURE('mkM', 4), GESTURE('mkM', 5)], mkT: [GESTURE('mkG', 6)],
      },
    },
    // Torre de Arqueiros: dois arqueiros que se revezam (N1 a N3) ou a balestra que gira para o alvo (N4)
    archer: {
      fam: 'arqueiros',
      key: t => t.spec === 'ballista' ? 'n4' : 'n' + Math.max(1, Math.min(3, t.tier || 1)),
      roles: {
        n1: [ARCHER('a1'), ARCHER('a1')], n2: [ARCHER('a2'), ARCHER('a2')], n3: [ARCHER('a3'), ARCHER('a3b')],
        n4: [{ set: 'bal', kind: 'dirs', T: 1.0 }],
      },
    },
    // Zarabatana (especializacao da Torre de Arqueiros): dois cacadores que se revezam no sopro
    blowgun: {
      fam: 'zarabatana',
      key: () => 'zb',
      roles: { zb: [HUNTER('zbA'), HUNTER('zbB')] },
    },
    // quartel: o guarda bate a lanca e ergue o escudo quando soldados saem (t.units aumenta)
    barracks: {
      fam: 'quartel',
      key: t => t.spec === 'lancers' ? 'qtL' : t.spec === 'monks' ? 'qtM' : 'qt' + Math.max(1, Math.min(3, t.tier || 1)),
      roles: {
        qt1: [SALUTE('qtG')], qt2: [SALUTE('qtG'), SALUTE('qtG')], qt3: [SALUTE('qtS'), SALUTE('qtG')],
        qtL: [SALUTE('qtL_c'), SALUTE('qtL_c')], qtM: [SALUTE('qtM_c'), SALUTE('qtM_c')],
      },
    },
  };

  const famDef = t => t.type === 'archer' && t.spec === 'blowgun' ? FAMS.blowgun : FAMS[t.type];
  const usableGeneric = t => {
    const D = famDef(t);
    return !!(D && SPR.ok(D.fam) && SPR.ok('comum') && META()[D.key(t)]);
  };

  // a torre de sprite cuida da propria obra (A.drawTower nao poe andaime nem achata)
  A.selfBuild = t => usableGeneric(t);

  // altura visivel (px de tela) para quem mede a torre (A.towerH em art2.js)
  A.spriteH = (type, tier, spec) => {
    if (typeof SPRITE_META === 'undefined') return 0;
    const t = { type, tier, spec: spec || null };
    const D = famDef(t);
    const key = D && D.key(t);
    const S = key && META()[key];
    return S && S.height ? S.height : 0;
  };

  // ponto de disparo da torre de sprite, em unidades do jogo relativas ao pe da torre (y negativo = para cima)
  A.spriteTop = t => {
    const D = famDef(t);
    if (!D || typeof SPRITE_META === 'undefined') return null;
    const S = META()[D.key(t)];
    return S && S.points && S.points.top ? S.points.top : null;
  };

  // lanternas, cristais e braseiros da torre: [dx, dy, '#cor', halo] relativos ao pe (o js/vfx.js acende como luz de cena)
  A.spriteLanterns = t => {
    if (typeof SPRITE_META === 'undefined') return null;
    const key = usableGeneric(t) ? famDef(t).key(t) : null;
    const S = key && META()[key];
    if (!S || !S.lanterns) return null;
    // luzes vizinhas viram uma so (braseiros lado a lado) e no maximo 3 por torre, para nao estourar
    const out = [];
    for (const L of S.lanterns) {
      const q = [L[0], L[1], L[2] || '#ffb25a', L[3] == null ? 1 : L[3]];
      const near = out.find(o => Math.hypot(o[0] - q[0], o[1] - q[1]) < 26);
      if (near) { near[0] = (near[0] + q[0]) / 2; near[1] = (near[1] + q[1]) / 2; } else out.push(q);
    }
    return out.slice(0, 3);
  };

  function track(t, time, key) {
    let st = state.get(t);
    if (!st) {
      st = { key, prev: null, shots: t.shots || 0, shotT: -99, who: 0, anim: t.anim || 0 };
      state.set(t, st);
    }
    if (st.key !== key) { st.prev = st.key; st.key = key; }
    if ((t.shots || 0) !== st.shots) { st.shots = t.shots || 0; st.shotT = time; st.who = t.shooter || 0; }
    // torres sem contador de tiros: o pulso t.anim sobe a cada ataque
    const a = t.anim || 0;
    if (a > st.anim + 0.05 && !t.shots) st.shotT = time;
    st.anim = a;
    // quartel: soldado novo saindo pela porta conta como "ataque" (saudacao do guarda)
    const nu = t.units ? t.units.filter(u => !u.dead && !u.removed).length : 0;
    if (st.units != null && nu > st.units) st.shotT = time;
    st.units = nu;
    return st;
  }

  function loopFrame(S, time, t) {
    const ph = Math.floor(time * 12 + hash((t.x || 0) * 0.13 + (t.y || 0)) * 24);
    return S.loop[((ph % S.loop.length) + S.loop.length) % S.loop.length];
  }

  function animFrame(S, time, t) {
    const n = S.anim.length;
    const ph = Math.floor(time * ANIM_FPS + hash((t.x || 0) * 0.13 + (t.y || 0)) * n);
    return S.anim[((ph % n) + n) % n];
  }

  // corpo da torre: base parada + pecas que mexem (ou o loop inteiro, nos arqueiros)
  function body(c, S, time, t) {
    if (S.base) {
      SPR.draw(c, S.base, 0, 0);
      if (S.anim) SPR.draw(c, animFrame(S, time, t), 0, 0);
    } else SPR.draw(c, loopFrame(S, time, t), 0, 0);
  }

  function sparkles(c, age, n, seed, col) {
    if (age < 0 || age > 1.1) return;
    c.save();
    c.globalCompositeOperation = 'lighter';
    for (let i = 0; i < n; i++) {
      const h1 = hash(seed + i), h2 = hash(seed + i * 7.3), h3 = hash(seed + i * 3.1);
      const a = age - h3 * 0.3;
      if (a < 0 || a > 0.8) continue;
      const x = (h1 - 0.5) * 60;
      const y = -8 - h2 * 40 - a * 55;
      const r = (1 - a / 0.8) * (2 + h3 * 2.5);
      c.globalAlpha = 1 - a / 0.8;
      c.fillStyle = col ? col : h1 > 0.5 ? '#ffe08a' : '#fff6d8';
      c.beginPath();
      c.moveTo(x, y - r * 2); c.lineTo(x + r * 0.5, y - r * 0.5); c.lineTo(x + r * 2, y);
      c.lineTo(x + r * 0.5, y + r * 0.5); c.lineTo(x, y + r * 2); c.lineTo(x - r * 0.5, y + r * 0.5);
      c.lineTo(x - r * 2, y); c.lineTo(x - r * 0.5, y - r * 0.5); c.closePath(); c.fill();
    }
    c.restore();
  }

  function halo(c, x, y, r, col, a) {
    const g = c.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, col.replace('A', (0.55 * a).toFixed(3)));
    g.addColorStop(0.35, col.replace('A', (0.22 * a).toFixed(3)));
    g.addColorStop(1, col.replace('A', '0'));
    c.fillStyle = g;
    c.fillRect(x - r, y - r, r * 2, r * 2);
  }

  const rgba = hex => {
    const n = parseInt(hex.slice(1), 16);
    return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},A)`;
  };

  function glow(c, S, t, time) {
    // curva: de dia (0,25) a luz quase some; a noite (1) fica inteira
    const k = Math.pow(Math.max(0, SPR.glow), 1.8);
    if (k <= 0.01) return;
    const fl = 0.86 + 0.08 * Math.sin(time * 9.1 + (t.x || 0)) + 0.06 * Math.sin(time * 23.7 + (t.y || 0));
    c.save();
    c.globalCompositeOperation = 'lighter';
    c.globalAlpha = Math.min(1, k * fl);
    if (S.glow) SPR.draw(c, S.glow, 0, 0);
    for (const L of (typeof Light === 'undefined' ? S.lanterns || [] : [])) {
      if (L[3] === 0) continue;
      const r = 10 + 6 * k;
      c.globalAlpha = Math.min(1, k * fl);
      halo(c, L[0], L[1], r, L[2] ? rgba(L[2]) : 'rgba(255,190,100,A)', 1);
    }
    c.restore();
  }

  // ---------------------------------------------------------------- obra (andaime, pedreiro, fiadas subindo)
  function workRise(p) {
    const q = U.clamp((p - 0.06) / 0.86, 0, 1) * ROWS;
    if (q >= ROWS) return 1;
    const row = Math.floor(q);
    return (row + U.easeInOut(Math.min(1, (q - row) / 0.55))) / ROWS;
  }

  function clipDraw(c, y0, y1, fn) {
    c.save();
    c.beginPath();
    c.rect(-200, y0, 400, y1 - y0);
    c.clip();
    fn();
    c.restore();
  }

  function masonFrame(t) {
    const P = META().pedreiro;
    if (!P || !P.bate) return null;
    const u = 1 - U.clamp((t.knockT || 0) / 0.5, 0, 1);
    let f;
    if (u < 0.06) f = 6; else if (u < 0.14) f = 7; else if (u < 0.85) f = Math.min(4, Math.floor((u - 0.14) / 0.71 * 5)); else f = 5;
    return P.bate[f];
  }

  // obra generica: chao do lote, andaime recortado na altura da fiada, torre nova subindo por baixo da antiga
  function workScene(c, t, time, st, S, done, bt) {
    const C = META();
    const p = U.clamp(bt / done, 0, 1);
    const old = st.prev && C[st.prev];
    const H = Math.max(S.height || 90, old ? old.height || 0 : 0) + 4;
    const yl = U.lerp(10, -H, workRise(p));
    const grow = easeBack(U.clamp(p / 0.08, 0, 1));
    const top = yl - 20;
    SPR.draw(c, C.chao.base, 0, 0);
    if (C.andT) clipDraw(c, U.lerp(30, top, grow), 60, () => SPR.draw(c, C.andT.still[0], 0, 0));
    if (old) clipDraw(c, -400, yl, () => body(c, old, time, t));
    c.save(); c.globalAlpha = 0.14; body(c, S, time, t); c.restore();
    clipDraw(c, yl, 80, () => body(c, S, time, t));
    // poeira subindo da fiada
    c.save();
    for (let i = 0; i < 5; i++) {
      const h = hash(i * 9.7 + (t.id || 0) * 1.3);
      const k = (time * 0.9 + h) % 1;
      c.globalAlpha = 0.3 * (1 - k);
      c.fillStyle = '#ecdcb8';
      c.beginPath();
      c.arc((h - 0.5) * 70 + Math.sin(k * 4 + i) * 4, yl - 4 - k * 18, 3 + k * 6, 0, U.TAU);
      c.fill();
    }
    c.restore();
    if (C.andF) clipDraw(c, U.lerp(30, top, grow), 60, () => SPR.draw(c, C.andF.still[0], 0, 0));
    if (C.tabua && p > 0.03) {
      c.save(); c.globalAlpha = U.clamp(p / 0.06, 0, 1); SPR.draw(c, C.tabua.still[0], 0, yl + 14); c.restore();
    }
    const mf = p > 0.05 && masonFrame(t);
    if (mf) SPR.draw(c, mf, 14, yl + 6);
    if (C.pilha) {
      c.save(); c.globalAlpha = U.clamp((1 - p) * 3, 0, 1);
      SPR.draw(c, C.pilha.still[0], -44, 16, false, 0.4 + 0.6 * (1 - p));
      c.restore();
    }
    sparkles(c, (bt % 0.9) / 0.9, st.prev ? 8 : 6, (t.x || 0) + Math.floor(bt / 0.9) * 17);
  }

  // depois da obra: andaime cai e some, a torre brilha
  function workEnd(c, t, time, S, k) {
    const C = META();
    const fall = k * k, fade = Math.max(0, 1 - k * 1.6);
    if (fade <= 0) return;
    const H = (S.height || 90) + 4;
    c.save();
    c.globalAlpha = fade;
    clipDraw(c, -H - 20 + fall * 80, 60 + fall * 80, () => {
      c.translate(0, fall * 60);
      if (C.andF) SPR.draw(c, C.andF.still[0], 0, 0);
    });
    if (C.tabua) SPR.draw(c, C.tabua.still[0], 0, -H + 14 + fall * 140);
    c.restore();
  }

  // ---------------------------------------------------------------- tripulacao das familias novas
  const GUN_T = 0.6;         // recuo do canhao depois do tiro

  // quadro de ataque/descanso de um papel
  function roleFrame(t, time, st, R_, A_, i) {
    if (R_.kind === 'archer') {
      const since = time - st.shotT;
      if (st.who === i && since >= 0 && since < SHOOT_T) return A_.shoot[Math.min(A_.shoot.length - 1, Math.floor(since / SHOOT_T * A_.shoot.length))];
      if (since < COMBAT_T) return A_.aim[Math.floor(time * 5 + i * 2) % A_.aim.length];
      return A_.idle[Math.floor(time * 8 + i * 5 + hash((t.x || 0) + i) * 12) % A_.idle.length];
    }
    if (R_.kind === 'dirs') {
      const ax = (t.aimX == null ? (t.x || 0) - 50 : t.aimX) - (t.x || 0);
      const ay = ((t.aimY == null ? (t.y || 0) + 30 : t.aimY) - (t.y || 0)) / U.YS;
      const n = A_.ndirs || 16;
      const d = ((Math.round(Math.atan2(-ay, ax) / U.TAU * n) % n) + n) % n;
      const fr = A_['d' + (d < 10 ? '0' : '') + d];
      const since = time - st.shotT;
      return since >= 0 && since < R_.T ? fr[Math.min(fr.length - 1, Math.floor(since / R_.T * fr.length))] : fr[fr.length - 1];
    }
    const fr = A_[R_.anim || 'fire'] || [];
    const n = fr.length, F = R_.fire || 0;
    const sinceShot = time - st.shotT;
    const castT = t.castT != null ? t.castT : sinceShot;
    if (R_.kind === 'gun') {
      if (sinceShot >= 0 && sinceShot < GUN_T) return fr[Math.min(n - 1, Math.floor(sinceShot / GUN_T * n))];
      // parado: laco de espera quando o conjunto tem (o ventilador do Zap gira sempre)
      if (A_.idle && A_.idle.length) return A_.idle[Math.floor(time * ANIM_FPS + hash((t.x || 0) + i * 5) * 7) % A_.idle.length];
      return fr[n - 1];
    }
    if (R_.beam && t.beam) return fr[F + (Math.floor(time * 6) % 2)];
    // ataque continuo (tambores em guerra) ou gesto de tempos em tempos (torres que nao atacam)
    if (n && R_.loopWhen && R_.loopWhen(t)) return fr[Math.floor(time * 12) % n];
    if (n && R_.every) {
      const e = (time + hash((t.x || 0) * 0.3 + i) * R_.every) % R_.every;
      if (e < R_.cast) return fr[Math.min(n - 1, Math.floor(e / R_.cast * n))];
    }
    if (R_.after != null) {
      const e = sinceShot - R_.after;
      if (n && e >= 0 && e < R_.cast) return fr[Math.min(n - 1, Math.floor(e / R_.cast * n))];
    } else if (n && castT >= 0 && castT < R_.cast && (!R_.alt || st.who === i)) {
      return fr[Math.min(n - 1, F + Math.floor(castT / R_.cast * (n - F)))];
    } else if (n && F > 0 && t.chargeT > 0) {
      return fr[Math.min(F - 1, Math.floor(t.chargeT * F))];
    } else if (n && F > 0 && t.chargeT == null && t.cd != null && t.cd > 0 && t.cd < R_.windup && sinceShot < 8) {
      return fr[Math.min(F - 1, Math.floor((1 - t.cd / R_.windup) * F))];
    }
    if (A_.idle) return A_.idle[Math.floor(time * 8 + hash((t.x || 0) + 3 + i * 5) * 12) % A_.idle.length];
    return fr[0];
  }

  function crewGeneric(c, t, time, st, S, D, since) {
    const roles = D.roles[st.key] || [];
    const ax = t.aimX == null ? (t.x || 0) - 1 : t.aimX;
    roles.forEach((R_, i) => {
      const A_ = META()[R_.set];
      const sl = S.slots && S.slots[i];
      if (!A_ || !sl) return;
      const pop = U.clamp((since - i * 0.08) / POP_T, 0, 1);
      if (pop <= 0) return;
      const flip = R_.kind !== 'hammer' && R_.kind !== 'dirs' && ax < (t.x || 0) + sl[0];
      SPR.draw(c, roleFrame(t, time, st, R_, A_, i), sl[0], sl[1], flip, pop < 1 ? easeBack(pop) : null);
      // "vupt" da soltura do arqueiro: arco de vento saindo do arco
      const shotAge = time - st.shotT;
      if (R_.kind === 'archer' && st.who === i && shotAge >= 0 && shotAge < 0.16) {
        const e = shotAge / 0.16;
        const hx = sl[0] + (flip ? -1 : 1) * (9 + e * 10), hy = sl[1] - 19;
        c.save();
        c.globalCompositeOperation = 'lighter';
        c.globalAlpha = 0.7 * (1 - e);
        c.strokeStyle = '#fff4d6';
        c.lineWidth = 2.2 * (1 - e) + 0.6;
        c.beginPath();
        c.ellipse(hx, hy, 4 + e * 6, 6 + e * 5, 0, flip ? Math.PI * 0.6 : -Math.PI * 0.4, flip ? Math.PI * 1.4 : Math.PI * 0.4);
        c.stroke();
        c.restore();
      }
      // respingo de oleo no pe da broca da Sonda do Pre-Sal quando bate (Batedeira Industrial: leite condensado)
      if (R_.kind === 'hammer') {
        const e = (time - st.shotT) / 0.5;
        if (e >= 0 && e < 1) {
          const leite = typeof DATA !== 'undefined' && DATA.SIDE === 'V';
          c.save();
          for (let k = 0; k < 7; k++) {
            const a = k / 7 * U.TAU + 0.3;
            const r = 6 + e * 26;
            c.globalAlpha = (leite ? 0.75 : 0.55) * (1 - e);
            c.fillStyle = leite ? (k % 2 ? '#fffaf0' : '#efe2c2') : k % 2 ? '#1b1a20' : '#3a3742';
            c.beginPath();
            c.arc(sl[0] + Math.cos(a) * r, sl[1] + Math.sin(a) * r * 0.5 - e * 6, 4 + e * 7, 0, U.TAU);
            c.fill();
          }
          c.restore();
        }
      }
    });
  }

  // boca do canhao (unidades do jogo, relativa ao pe da torre), para fumaca e clarao do tiro (js/vfx.js)
  A.spriteMuzzle = t => {
    const D = famDef(t);
    if (!D || typeof SPRITE_META === 'undefined') return null;
    const S = META()[D.key(t)];
    const roles = D.roles[D.key(t)] || [];
    const gi = roles.findIndex(r => r.kind === 'gun');
    const G = gi >= 0 && META()[roles[gi].set];
    if (!S || !G || !G.points || !G.points.muzzle || !S.slots[gi]) return null;
    const sl = S.slots[gi];
    const ax = t.aimX == null ? (t.x || 0) - 1 : t.aimX;
    const k = ax < (t.x || 0) + sl[0] ? -1 : 1;
    return [sl[0] + k * G.points.muzzle[0], sl[1] + G.points.muzzle[1]];
  };

  // particulas subindo do orbe (a carga e o clarao do disparo sao do js/vfx.js)
  function orbFx(c, t, time, st, S) {
    const P = S.points && S.points.top;
    if (!P) return;
    c.save();
    c.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 4; i++) {
      const h = hash(i * 3.3 + (t.x || 0) * 0.7);
      const k = (time * 0.45 + h) % 1;
      c.globalAlpha = 0.8 * Math.sin(k * Math.PI);
      // brilho das joias: lilas no estojo, ametista na Corrente de Ouro, ouro no Relogio
      // na Vermelha o mago e o Churrascao da Picanha: brasinhas subindo da churrasqueira
      const cor = typeof DATA !== 'undefined' && DATA.SIDE === 'R' ? ['#ffe2a8', '#ff9a3a']
        : t.spec === 'sun' ? ['#fff1b8', '#ffd25a'] : t.spec === 'lightning' ? ['#f2d6ff', '#c99aff'] : ['#ffe6ff', '#e0a8ff'];
      c.fillStyle = i % 2 ? cor[0] : cor[1];
      c.beginPath();
      c.arc(P[0] + Math.sin(time * 1.3 + i * 2) * (6 + 4 * h), P[1] - 4 - k * 18, 1.1 + h, 0, U.TAU);
      c.fill();
    }
    c.restore();
  }

  function genericSprite(c, t, time) {
    const D = famDef(t);
    const key = D.key(t);
    const st = track(t, time, key);
    const S = META()[key];
    const bt = t.buildT == null ? 99 : t.buildT;
    const done = t.buildDur || BUILD_T + (st.prev ? UP_DELAY : 0);
    c.save();
    c.translate(t.x, t.y);
    if (bt < done && META().chao) {
      workScene(c, t, time, st, S, done, bt);
      c.restore();
      return true;
    }
    const sq = A.towerSquash && A.towerSquash(t);
    if (sq) c.scale(sq[0], sq[1]);
    body(c, S, time, t);
    crewGeneric(c, t, time, st, S, D, bt - done);
    if (S.front) SPR.draw(c, S.front, 0, 0);
    glow(c, S, t, time);
    if (D.orbs) orbFx(c, t, time, st, S);
    const flash = (bt - done) / 0.35;
    if (flash >= 0 && flash < 1) {
      c.save();
      c.globalCompositeOperation = 'lighter';
      c.globalAlpha = 0.45 * (1 - flash);
      body(c, S, time, t);
      c.restore();
    }
    if (bt - done < 0.6) workEnd(c, t, time, S, (bt - done) / 0.6);
    if (bt - done < 1) sparkles(c, (bt - done) / 0.9, st.prev ? 16 : 10, (t.x || 0) + (t.y || 0));
    c.restore();
    return true;
  }

  // gancho unico do A.drawTower: torres de sprite se desenham inteiras (com translate proprio)
  A.towerSprite = (c, t, time) => {
    if (typeof SPRITE_META === 'undefined') return false;
    if (usableGeneric(t)) return genericSprite(c, t, time || 0);
    const D = famDef(t);
    if (D) SPR.need(D.fam); // enquanto carrega, vale o desenho antigo
    return false;
  };

  // icones e menus chamam A.tower.archer direto (sem A.drawTower): desenha o sprite no lugar
  A.archerSprite = (c, t, time) => {
    if (!usableGeneric(t)) return false;
    c.save();
    c.translate(-(t.x || 0), -(t.y || 0));
    genericSprite(c, t, time || 0);
    c.restore();
    return true;
  };

  // ---------------------------------------------------------------- projeteis e impactos
  // flecha e virote em voo: sprite girado + rastro suave (os efeitos do mago sao do js/vfx.js)
  A.projSprite = (c, p) => {
    if (!SPR.ok('arqueiros')) return false;
    const key = p.kind === 'arrow' ? 'flecha' : p.kind === 'bolt' ? 'virote' : null;
    const one = f => Array.isArray(f[0]) ? f[0] : f;
    const S = key && META()[key];
    if (!S) return false;
    const big = key === 'virote';
    const len = big ? 38 : 20;
    c.save();
    c.translate(p.x, p.y);
    c.rotate(p.ang || 0);
    // indo para a esquerda, o envelope e a mala ficariam de cabeca para baixo: espelha na vertical
    if (Math.cos(p.ang || 0) < 0) c.scale(1, -1);
    const g = c.createLinearGradient(-len * 1.7, 0, -4, 0);
    g.addColorStop(0, 'rgba(255,246,220,0)');
    g.addColorStop(1, big ? 'rgba(255,240,205,0.6)' : 'rgba(255,246,220,0.5)');
    c.fillStyle = g;
    c.beginPath();
    c.ellipse(-len * 0.9, 0, len * 0.85, big ? 3.2 : 1.8, 0, 0, U.TAU);
    c.fill();
    SPR.draw(c, one(S.still), 0, 0, false, 1 / (S.pxk || 1));
    if (p.exp) {
      c.globalCompositeOperation = 'lighter';
      const gl = c.createRadialGradient(14, 0, 0, 14, 0, 14);
      gl.addColorStop(0, 'rgba(255,170,70,0.8)');
      gl.addColorStop(1, 'rgba(255,120,40,0)');
      c.fillStyle = gl;
      c.fillRect(0, -14, 28, 28);
    }
    c.restore();
    return true;
  };

  // flecha cravada no chao e impacto em "puff" de areia (no lugar das estrelinhas 2D)
  A.fxSprite = (c, f, k) => {
    if (!SPR.ok('arqueiros')) return false;
    if (f.kind === 'stuck' && !f.dart && META().cravada) {
      const S = META().cravada;
      c.save();
      c.globalAlpha = k > 0.6 ? (1 - k) / 0.4 : 1;
      SPR.draw(c, Array.isArray(S.still[0]) ? S.still[0] : S.still, f.x, f.y - 6, Math.cos(f.ang || 0) < 0, 1 / (S.pxk || 1));
      c.restore();
      return true;
    }
    if (f.kind === 'hit' && f.small) {
      const e = 1 - (1 - k) * (1 - k);
      c.save();
      for (let i = 0; i < 5; i++) {
        const a = i * 1.257 + (f.x % 3);
        const d = 3 + e * 9;
        const x = f.x + Math.cos(a) * d, y = f.y + Math.sin(a) * d * 0.7 - e * 4;
        const r = 4 + e * 4.5;
        const g = c.createRadialGradient(x, y, 0, x, y, r);
        g.addColorStop(0, `rgba(250,236,204,${0.95 * (1 - k)})`);
        g.addColorStop(0.6, `rgba(232,206,160,${0.5 * (1 - k)})`);
        g.addColorStop(1, 'rgba(232,206,160,0)');
        c.fillStyle = g;
        c.fillRect(x - r, y - r, r * 2, r * 2);
      }
      c.globalCompositeOperation = 'lighter';
      c.globalAlpha = (1 - k) * 0.8;
      c.fillStyle = '#fff2c8';
      for (let i = 0; i < 3; i++) {
        const a = i * 2.1 + f.y;
        c.beginPath();
        c.arc(f.x + Math.cos(a) * (4 + e * 12), f.y + Math.sin(a) * (3 + e * 8) - e * 6, 1.3 * (1 - k) + 0.3, 0, U.TAU);
        c.fill();
      }
      c.restore();
      return true;
    }
    return false;
  };

  // ---------------------------------------------------------------- icones da interface (tools/blender/icones.py e retratos)
  // torre: tw_<tipo>_<nivel>; especializacao: tw_<spec>; habilidades, feiticos e botoes pelo proprio nome
  A.iconSprite = (c, name, x, y, r, o = {}) => {
    if (!SPR.ok('icones')) return false;
    const S = META();
    let key = name;
    if (DATA.TOWERS[name]) key = `tw_${name}_${Math.max(1, Math.min(3, o.tier || 1))}`;
    else if (DATA.SPECS[name]) key = 'tw_' + name;
    const set = S[key];
    if (!set || !set.still) return false;
    const f = set.still[0];
    const im = SPR.imgs[f[0]];
    if (!im) return false;
    const portrait = key.startsWith('tw_');
    const box = r * (portrait ? 2.5 : 2.15);
    const k = box / Math.max(f[3], f[4]);
    const dw = f[3] * k, dh = f[4] * k;
    c.save();
    if (o.off || o.disabled) c.globalAlpha = 0.45;
    c.imageSmoothingEnabled = true;
    c.imageSmoothingQuality = 'high';
    c.drawImage(im, f[1], f[2], f[3], f[4], x - dw / 2, y - dh / 2 + (portrait ? -r * 0.05 : 0), dw, dh);
    c.restore();
    return true;
  };

  // ---------------------------------------------------------------- cenario do Blender (um fundo por fase)
  // tools/blender/cenario.py renderiza o chao, a estrada, a agua e os enfeites; aqui entram o fundo, a luz da lava e
  // dos braseiros, as tamareiras que balancam, o brilho da agua e os marcos dos lotes.
  const CEN = () => (typeof SPRITE_META !== 'undefined' && SPRITE_META.cenario) || [];
  const frameAt = (list, time, fps, ph) => list[Math.floor(time * fps + (ph || 0) * list.length) % list.length];

  // guarda no maximo dois fundos decodificados (a fase em jogo e a previa do mapa); SPR.bg e o ultimo usado
  SPR.bg = null;
  SPR.bgs = new Map();
  SPR.bgLoad = idx => {
    const C = CEN()[idx];
    if (!C) return null;
    let bg = SPR.bgs.get(idx);
    if (bg) {
      SPR.bgs.delete(idx);
      SPR.bgs.set(idx, bg);
    } else {
      bg = { idx, C, img: null, luz: null };
      SPR.bgs.set(idx, bg);
      for (const k of [...SPR.bgs.keys()]) if (SPR.bgs.size > 2 && k !== idx) SPR.bgs.delete(k);
      const im = new Image();
      im.onload = () => {
        bg.img = im;
        // redesenha o que ja tinha sido pintado com a areia lisa provisoria
        if (typeof Render !== 'undefined' && String(Render.bgKey).startsWith(idx + ':')) Render.bgKey = '';
        if (typeof WorldMap !== 'undefined') for (const k of Object.keys(WorldMap.previews)) if (k.startsWith(idx + ':')) delete WorldMap.previews[k];
      };
      im.onerror = () => console.warn('fundo nao carregou: ' + C.img);
      im.src = C.img;
      if (C.luz) { const gl = new Image(); gl.onload = () => { bg.luz = gl; }; gl.src = C.luz; }
    }
    SPR.bg = bg;
    return bg;
  };
  // fundo do mapa-mundi (tools/blender/mapa.py): chamado pelo WorldMap.paint; os nos e botoes vem por cima (ui.js)
  // regiao 2 (Rio das Duas Aguas): SPRITE_META.mapa2; sem ele ainda, o mapa 1 tingido de azul
  const mapas = {};
  A.worldSprite = (c, reg = 0) => {
    const SM = typeof SPRITE_META !== 'undefined' && SPRITE_META;
    const M = SM && (reg ? SM.mapa2 || SM.mapa : SM.mapa);
    if (!M) return false;
    let mapa = mapas[reg];
    if (!mapa) {
      mapa = mapas[reg] = { img: null, luz: null };
      const done = () => { if (typeof WorldMap !== 'undefined') WorldMap.bgKey = ''; };
      const im = new Image();
      im.onload = () => { mapa.img = im; done(); };
      im.src = M.img;
      if (M.luz) { const gl = new Image(); gl.onload = () => { mapa.luz = gl; done(); }; gl.src = M.luz; }
    }
    if (!mapa.img) return false;
    c.imageSmoothingEnabled = true;
    c.imageSmoothingQuality = 'high';
    c.drawImage(mapa.img, 0, 0, W, H);
    if (mapa.luz) {
      c.save();
      c.globalCompositeOperation = 'lighter';
      c.globalAlpha = 0.7;
      c.drawImage(mapa.luz, 0, 0, W, H);
      c.restore();
    }
    if (reg && !SM.mapa2) { c.fillStyle = 'rgba(30,70,100,0.28)'; c.fillRect(0, 0, W, H); }
    // vinheta leve para os paineis e botoes descolarem do fundo
    const vg = c.createRadialGradient(W / 2, H / 2, 320, W / 2, H / 2, 820);
    vg.addColorStop(0, 'rgba(60,30,5,0)');
    vg.addColorStop(1, 'rgba(60,30,5,0.32)');
    c.fillStyle = vg;
    c.fillRect(0, 0, W, H);
    return true;
  };

  const bgOn = () => !!(SPR.bg && SPR.bg.img);

  // chamado pelo A.terrain: desenha o fundo pronto (ou uma areia lisa enquanto a imagem chega)
  A.terrainSprite = (c, g) => {
    const bg = SPR.bgLoad(g.levelIdx);
    if (!bg) return false;
    A.envLights[g.levelIdx] = bg.C.env || [];
    if (!bg.img) { c.fillStyle = '#d9b88a'; c.fillRect(0, 0, W, H); return true; }
    c.imageSmoothingEnabled = true;
    c.imageSmoothingQuality = 'high';
    c.drawImage(bg.img, 0, 0, W, H);
    return true;
  };

  // camada viva logo acima do fundo (render.js): agua, luz da lava/braseiros e tamareiras
  A.ambient = (c, g, time) => {
    const bg = SPR.bgs.get(g.levelIdx);
    if (!bg || !bg.img) return;
    const L = g.L;
    // brilho da agua: reflexos curtos que correm devagar e piscam
    for (const [x, y, rx, ry] of L.water || []) {
      c.save();
      c.beginPath();
      c.ellipse(x, y, rx * 0.86, ry * 0.8, 0, 0, U.TAU);
      c.clip();
      c.globalCompositeOperation = 'lighter';
      const n = Math.round(rx / 7);
      for (let i = 0; i < n; i++) {
        const hx = hash(i + x), hy = hash(i * 3.1 + y);
        const px = x - rx + ((hx * rx * 2 + time * (6 + 5 * hy)) % (rx * 2));
        const py = y - ry * 0.8 + hy * ry * 1.6;
        const a = 0.5 + 0.5 * Math.sin(time * (1.1 + hx) + i * 2.3);
        c.fillStyle = `rgba(255,255,245,${0.22 * a * a})`;
        c.beginPath();
        c.ellipse(px, py, 5 + 7 * hy, 1.1, 0, 0, U.TAU);
        c.fill();
      }
      c.restore();
    }
    // rios: os mesmos reflexos, descendo com a correnteza ao longo de cada trecho
    for (const rv of L.rivers || []) {
      const hw = rv.w / 2;
      c.save();
      c.globalCompositeOperation = 'lighter';
      for (let s = 0; s < rv.pts.length - 1; s++) {
        const [ax, ay] = rv.pts[s], [bx, by] = rv.pts[s + 1];
        const dx = bx - ax, dy = by - ay, len = Math.hypot(dx, dy) || 1, ang = Math.atan2(dy, dx);
        const n = Math.round(len * hw / 900);
        for (let i = 0; i < n; i++) {
          const hx = hash(i + ax + s * 7.3), hy = hash(i * 3.1 + ay + s);
          const t = (hx + time * (9 + 6 * hy) / len) % 1;
          const off = (hy - 0.5) * 1.3 * hw;
          const px = ax + dx * t - (dy / len) * off, py = ay + dy * t + (dx / len) * off;
          const a = 0.5 + 0.5 * Math.sin(time * (1.1 + hx) + i * 2.3);
          c.fillStyle = `rgba(255,255,245,${0.2 * a * a})`;
          c.beginPath();
          c.ellipse(px, py, 5 + 7 * hy, 1.1, ang, 0, U.TAU);
          c.fill();
        }
      }
      c.restore();
    }
    // lava e braseiros: a luz pulsa devagar e cresce a noite e na tempestade
    if (bg.luz) {
      c.save();
      c.globalCompositeOperation = 'lighter';
      c.globalAlpha = Math.min(1, (0.35 + SPR.glow) * (0.85 + 0.15 * Math.sin(time * 1.7) + 0.05 * Math.sin(time * 5.3)));
      c.drawImage(bg.luz, 0, 0, W, H);
      c.restore();
    }
    // sombras de nuvem passando devagar (so nas fases de dia e ceu limpo)
    const day = ['oasis', 'canyon', 'ruins', 'dunes', 'qanat'].includes(L.theme);   // sombras de nuvem nas fases de dia
    if (day) {
      c.save();
      for (let i = 0; i < 3; i++) {
        const span = W + 900;
        const cx = ((hash(i * 7 + L.seed) * span + time * (7 + 3 * i)) % span) - 450;
        const cy = 90 + hash(i * 13 + L.seed) * (H - 180) + Math.sin(time * 0.05 + i) * 30;
        for (let k = 0; k < 3; k++) {
          const ox = (k - 1) * 120 + hash(i + k * 5) * 40, oy = (k % 2) * 30 - 15, r = 150 + 50 * hash(i * 3 + k);
          const gg = c.createRadialGradient(cx + ox, cy + oy, 0, cx + ox, cy + oy, r);
          gg.addColorStop(0, 'rgba(70,40,20,0.075)');
          gg.addColorStop(1, 'rgba(70,40,20,0)');
          c.fillStyle = gg;
          c.fillRect(cx + ox - r, cy + oy - r, r * 2, r * 2);
        }
      }
      c.restore();
    }
    const green = ['oasis', 'canyon', 'ruins', 'dunes', 'qanat', 'storm'].includes(L.theme);
    // feixes de luz entre as copas (manha na mata)
    if (['oasis', 'ruins', 'qanat', 'canyon'].includes(L.theme)) {
      c.save();
      c.globalCompositeOperation = 'lighter';
      for (let i = 0; i < 3; i++) {
        const x0 = 120 + i * 210 + 40 * Math.sin(time * 0.05 + i), a = 0.05 + 0.03 * Math.sin(time * 0.4 + i * 2.1);
        const gg = c.createLinearGradient(x0, 0, x0 + 260, H * 0.9);
        gg.addColorStop(0, `rgba(255,246,200,${a})`);
        gg.addColorStop(1, 'rgba(255,246,200,0)');
        c.fillStyle = gg;
        c.beginPath();
        c.moveTo(x0, -10); c.lineTo(x0 + 70, -10); c.lineTo(x0 + 330, H * 0.9); c.lineTo(x0 + 200, H * 0.9);
        c.closePath(); c.fill();
      }
      c.restore();
    }
    // vaga-lumes (Gruta dos Vaga-lumes): pontinhos que acendem e apagam, vagando devagar
    if (L.theme === 'citadel') {
      c.save();
      c.globalCompositeOperation = 'lighter';
      for (let i = 0; i < 46; i++) {
        const hx = hash(i * 1.7), hy = hash(i * 2.9 + 4);
        const x = hx * W + Math.sin(time * (0.3 + hx * 0.4) + i) * 30, y = hy * H + Math.cos(time * (0.25 + hy * 0.3) + i * 1.3) * 22;
        const blink = Math.max(0, Math.sin(time * (0.8 + hx) + i * 2.4));
        if (blink < 0.05) continue;
        const gg = c.createRadialGradient(x, y, 0, x, y, 9);
        gg.addColorStop(0, `rgba(220,255,160,${0.9 * blink})`);
        gg.addColorStop(0.35, `rgba(160,255,120,${0.35 * blink})`);
        gg.addColorStop(1, 'rgba(120,255,100,0)');
        c.fillStyle = gg;
        c.fillRect(x - 9, y - 9, 18, 18);
      }
      c.restore();
    }
    // borboletas do cerrado e flores de ipe caindo nas fases de dia
    if (green) {
      c.save();
      for (let i = 0; i < 6; i++) {
        const hx = hash(i * 9.7 + L.seed), hy = hash(i * 4.3 + L.seed);
        const cx = 80 + hx * (W - 160), cy = 90 + hy * (H - 200);
        const a = time * (0.22 + 0.12 * hx) + hx * U.TAU;
        const bx = cx + Math.cos(a) * 60, by = cy + Math.sin(a * 1.4) * 34 - 6 * Math.sin(time * 2.1 + i);
        const fl = Math.abs(Math.sin(time * 14 + i * 2));
        c.fillStyle = ['#fff6d8', '#ffd36a', '#8fd0ff', '#ff9ab0'][i % 4];
        c.beginPath(); c.ellipse(bx - 2, by, 2.4 * fl + 0.6, 1.8, 0, 0, U.TAU); c.fill();
        c.beginPath(); c.ellipse(bx + 2, by, 2.4 * fl + 0.6, 1.8, 0, 0, U.TAU); c.fill();
        c.fillStyle = 'rgba(40,50,20,0.14)';
        c.beginPath(); c.ellipse(bx + 4, by + 26, 3, 1.2, 0, 0, U.TAU); c.fill();
      }
      for (let i = 0; i < 5; i++) {
        const T = 14 + 6 * hash(i * 3.3), ph = ((time / T) + hash(i * 7.1)) % 1;
        const x = hash(i * 5.9 + L.seed) * W + ph * 160 + Math.sin(ph * 12 + i) * 18, y = -20 + ph * (H + 40);
        c.save();
        c.translate(x, y);
        c.rotate(Math.sin(ph * 9 + i) * 0.9);
        c.globalAlpha = Math.min(1, (1 - ph) * 3) * 0.85;
        // flor de ipe amarelo caindo (seca em Brasilia), no lugar da folha da mata
        c.fillStyle = i % 2 ? '#f7cf3c' : '#f2b81f';
        c.beginPath(); c.ellipse(0, 0, 4.2, 3, 0, 0, U.TAU); c.fill();
        c.fillStyle = '#d9822b';
        c.beginPath(); c.arc(0.6, 0, 1.1, 0, U.TAU); c.fill();
        c.restore();
      }
      c.restore();
    }
    // tamareiras na brisa
    if (SPR.ok('ambiente')) {
      const sets = [META().palmA, META().palmB, META().palmC];
      for (const [v, x, y, s, ph] of bg.C.palms || []) {
        const S = sets[v];
        if (!S) continue;
        SPR.draw(c, frameAt(S.balanca, time, 7, ph), x, y, false, s / (S.boost || 1));
      }
    }
  };

  const hoverRing = (c, rx, ry) => {
    c.save();
    const gg = c.createRadialGradient(0, 0, rx * 0.3, 0, 0, rx);
    gg.addColorStop(0, 'rgba(255,244,200,0)');
    gg.addColorStop(1, 'rgba(255,240,190,0.28)');
    c.scale(1, ry / rx);
    c.fillStyle = gg;
    c.beginPath(); c.arc(0, 0, rx, 0, U.TAU); c.fill();
    c.lineWidth = 2.2; c.strokeStyle = 'rgba(255,246,210,0.85)';
    c.stroke();
    c.restore();
  };

  // lote vazio: no cenario do Blender so a estaca com a bandeirola (o chao ja esta no fundo); sem ele, o lote inteiro
  A.spotSprite = (c, x, y, hover, time) => {
    if (bgOn() && SPR.ok('comum') && META().marco) {
      const S = META().marco;
      c.save();
      c.translate(x, y);
      if (hover) hoverRing(c, 36, 20);
      SPR.draw(c, frameAt(S.tremula, time || 0, 10, hash(x + y)), 0, 0);
      c.restore();
      return true;
    }
    const S = SPR.ok('comum') && META().lote;
    if (!S) return false;
    c.save();
    c.translate(x, y);
    const fake = { x, y };
    body(c, S, time || 0, fake);
    if (hover) {
      c.globalCompositeOperation = 'lighter';
      c.globalAlpha = 0.22;
      body(c, S, time || 0, fake);
      c.globalAlpha = 1;
      A.ell(c, 0, 1, 37, 21, null, 'rgba(255,240,180,0.6)', 2.5);
    }
    c.restore();
    return true;
  };

  // escombros de um lote de ruina (pagos para limpar)
  A.ruinSprite = (c, x, y, hover, cost, time) => {
    const S = bgOn() && SPR.ok('comum') && META().ruina;
    if (!S) return false;
    c.save();
    c.translate(x, y);
    if (hover) hoverRing(c, 38, 21);
    SPR.draw(c, S.still[0], 0, 0);
    c.restore();
    return true;
  };

  // alavanca da comporta: quadro pelo angulo do cabo (o mesmo do desenho 2D)
  A.leverSprite = (c, f, time, hover) => {
    const S = bgOn() && SPR.ok('ambiente') && META().alavanca;
    if (!S) return false;
    const ang = (f.state ? 0.6 : -0.6) * (f.flip > 0 ? 1 - f.flip * 2 : 1);
    const n = S.ang.length;
    c.save();
    c.translate(f.x, f.y);
    if (hover) hoverRing(c, 24, 12);
    SPR.draw(c, S.ang[Math.max(0, Math.min(n - 1, Math.round((ang + 0.6) / 1.2 * (n - 1))))], 0, 0);
    if (hover) A.glow(c, 0, -26, 24, '#ffe08a', 0.3);
    c.restore();
    return true;
  };

  // palicada atravessada no ramo fechado: quadro pela direcao do caminho no chao
  A.gateSprite = (c, x, y, dx, dy, time) => {
    const S = bgOn() && SPR.ok('ambiente') && META().palicada;
    if (!S) return false;
    const wy = -dy / Math.sin(35 * Math.PI / 180);
    let a = Math.atan2(wy, dx) + Math.PI / 2;
    a = ((a % Math.PI) + Math.PI) % Math.PI;
    const n = S.dir.length;
    SPR.draw(c, S.dir[Math.round(a / Math.PI * n) % n], x, y);
    return true;
  };
})();
