'use strict';
// Inimigos em sprites pre-renderizados no Blender (tools/blender/inimigos_glb.py -> tools/sprites/empacotar_inimigos.py).
// Cada inimigo tem folhas proprias (carregadas so quando ele aparece). Sem a folha pronta, o jogo usa o desenho antigo.

const ESPR = {
  // papel do motor (raider, jackal...) -> conjunto de sprites do personagem da turma rival da vez (DATA.setRival)
  key(type) { const E = typeof DATA !== 'undefined' && DATA.ENEMIES[type]; return (E && E.spr) || type; },
  imgs: {},      // indice da folha -> Image
  state: {},     // indice da folha -> 'loading' | 'ok' | 'err'

  has(type) { return typeof INIMIGOS_META !== 'undefined' && !!INIMIGOS_META.sets[this.key(type)]; },

  want(type) {
    if (!this.has(type)) return;
    for (const i of INIMIGOS_META.fams[this.key(type)] || []) {
      if (this.state[i]) continue;
      this.state[i] = 'loading';
      const im = new Image();
      im.onload = () => { this.state[i] = 'ok'; };
      im.onerror = () => { this.state[i] = 'err'; };
      im.src = INIMIGOS_META.sheets[i];
      this.imgs[i] = im;
    }
  },

  ready(type) {
    if (!this.has(type)) return false;
    const fam = INIMIGOS_META.fams[this.key(type)] || [];
    if (!fam.every(i => this.state[i] === 'ok')) { this.want(type); return false; }
    return true;
  },

  // carrega de antemao todos os inimigos das ondas da fase
  preload(L) {
    const seen = new Set();
    const walk = v => {
      if (typeof v === 'string') { if (this.has(v)) seen.add(v); }
      else if (Array.isArray(v)) v.forEach(walk);
    };
    walk(L.waves);
    if (seen.has('brood')) seen.add('scorpling');
    if (seen.has('warlord')) seen.add('raider');
    seen.forEach(t => this.want(t));
  },

  // px por unidade do jogo de uma folha: escala base x densidade extra do render (pxk) do inimigo dono da folha
  den(f) {
    if (!this._den) {
      this._den = {};
      for (const [t, idx] of Object.entries(INIMIGOS_META.fams)) for (const i of idx) this._den[i] = INIMIGOS_META.scale * (INIMIGOS_META.sets[t].pxk || 1);
    }
    return this._den[f[0]] || INIMIGOS_META.scale;
  },

  draw(c, f, flip) {
    const s = 1 / this.den(f);
    const im = this.imgs[f[0]];
    c.save();
    // a folha e mais densa que a tela: reduzir com filtro bom (sem isto o WebKit usa 'low' e serrilha)
    c.imageSmoothingEnabled = true;
    c.imageSmoothingQuality = 'high';
    if (flip) c.scale(-1, 1);
    c.drawImage(im, f[1], f[2], f[3], f[4], -f[5] * s, -f[6] * s, f[3] * s, f[4] * s);
    c.restore();
  },
};

// vista do andar pela direcao do passo na tela (hx, hy). As folhas novas tem 5 direcoes no chao (r leste, q nordeste,
// u norte, e sudeste, d sul; o oeste e o espelho). A camera ve o chao a 35 graus, entao o passo na tela vira angulo no
// chao dividindo o dy por sen 35. Folga de 8 graus nas fronteiras para a vista nao piscar numa curva. o._vw guarda a atual.
const DIR_ANG = { u: 90, q: 45, r: 0, e: -45, d: -90 };
const SIN_CAM = Math.sin((35 * Math.PI) / 180);
A.walkView = (S, o, hx, hy) => {
  if (!S.q) return hy < -0.62 && S.u ? 'u' : hy > 0.62 && S.d ? 'd' : 'r';   // folha antiga (3 vistas)
  const ang = (Math.atan2(-hy / SIN_CAM, Math.abs(hx)) * 180) / Math.PI;
  if (o._vw && S[o._vw] && Math.abs(ang - DIR_ANG[o._vw]) < 22.5 + 8) return o._vw;
  let best = 'r', bd = 1e9;
  for (const k in DIR_ANG) {
    const d = Math.abs(ang - DIR_ANG[k]);
    if (S[k] && d < bd) { bd = d; best = k; }
  }
  o._vw = best;
  return best;
};

// quadro do inimigo vivo: direcao do passo, passo, ataque ou conjuracao (parado e de lado, encarando o oponente)
A.enemyFrame = e => {
  const S = INIMIGOS_META.sets[ESPR.key(e.type)];
  // conjuracao (xama, sabotador, chefe chamando reforcos) usa o modo de ataque
  if (e.castAnim > (e._pc || 0)) e._cm = e.castAnim;
  e._pc = e.castAnim;
  // devolve [quadro, espelho, quadro da camada de brasa (G + modo) ou undefined]
  const out = (m, i) => [S[m][i], e.facing < 0, S['G' + m] && S['G' + m][i]];
  if (S.a && e.castAnim > 0 && e._cm) return out('a', Math.min(S.a.length - 1, Math.floor((1 - e.castAnim / e._cm) * S.a.length)));
  if (S.a && e.atkAnim > 0) return out('a', Math.min(S.a.length - 1, Math.floor((1 - e.atkAnim / 0.3) * S.a.length)));
  const view = e.moving === false && S.q ? 'r' : A.walkView(S, e, e.hdx || 0, e.hdy || 0);
  const seq = S[view];
  const ph = ((e.walk || 0) / U.TAU) % 1;
  return out(view, e.moving === false ? 0 : Math.floor((ph < 0 ? ph + 1 : ph) * seq.length) % seq.length);
};

// bicho libertado (cores naturais) por direcao: l leste, lq lu le ld (folha antiga: so l)
A.freeSet = S => S._free || (S._free = { r: S.l, q: S.lq, u: S.lu, e: S.le, d: S.ld, a: S.la });

// Estouro da Mata (game.updateHerd): bicho libertado correndo pela estrada, com poeira
A.drawHerd = (c, h, t) => {
  if (h.run < 0 || !ESPR.ready(h.type)) return;
  const S = INIMIGOS_META.sets[ESPR.key(h.type)];
  if (!S.l) return;
  const F = A.freeSet(S);
  const seq = F[A.walkView(F, h, h.hdx, h.hdy)];
  const dist = DATA.SPELLS.stampede.dist;
  c.save();
  c.translate(h.x, h.y);
  c.globalAlpha = Math.max(0, Math.min(1, h.run / 24, (dist - h.run) / 50));
  if (h.T.flying) c.translate(0, -FLY_H * 0.8);
  ESPR.draw(c, seq[Math.floor(h.run / 7) % seq.length], h.facing < 0);
  A.whiteFlag(c, h.facing < 0 ? 4 : -4, -Math.max(...seq.map(f => f[6] / ESPR.den(f))) + 4, h.run / 40, h.facing < 0 ? -1 : 1);
  c.restore();
  if (!h.T.flying && typeof Vfx !== 'undefined' && Math.random() < 0.3) {
    Vfx.emit(h.x + U.rand(-6, 6), h.y - 2, U.rand(-10, 10), U.rand(-18, -6), U.rand(0.4, 0.7), U.rand(3, 5), '#c9a27a', { kind: 'smoke', drag: 0.6 });
  }
};

// bicho liberto lutando do nosso lado (Chamado da Mata da Caipora): anda nas 5 direcoes e ataca com as cores naturais
A.beastSprite = (c, u) => {
  if (!ESPR.ready(u.beast)) { ESPR.want(u.beast); return false; }
  const F = A.freeSet(INIMIGOS_META.sets[ESPR.key(u.beast)]);
  if (!F.r) return false;
  let f;
  if (F.a && u.atkAnim > 0) f = F.a[Math.min(F.a.length - 1, Math.floor((1 - u.atkAnim / 0.28) * F.a.length))];
  else if (!u.moving) f = (F.e || F.r)[0];
  else {
    const seq = F[A.walkView(F, u, u.hdx || 0, u.hdy || 0)];
    const ph = ((u.walk || 0) / U.TAU) % 1;
    f = seq[Math.floor((ph < 0 ? ph + 1 : ph) * seq.length) % seq.length];
  }
  // a folha ja vem espelhada pelo A.drawUnit (facing): desenha sem flip
  c.globalAlpha = u.life > 0 && u.life < 1 ? u.life : 1;
  ESPR.draw(c, f, false);
  if (u.hurtT > 0) { c.globalCompositeOperation = 'lighter'; c.globalAlpha = 0.4; ESPR.draw(c, f, false); }
  return true;
};
A.beastTop = u => {
  const S = INIMIGOS_META.sets[ESPR.key(u.beast)];
  return S && S.l && ESPR.ready(u.beast) ? Math.max(...S.l.map(f => f[6] / ESPR.den(f))) : null;
};

// icone de bicho libertado (botao do Estouro da Mata): primeiro quadro andando, cabendo no circulo de raio r
A.freedIcon = (c, type, x, y, r) => {
  if (!ESPR.has(type) || !ESPR.ready(type)) return false;
  const S = INIMIGOS_META.sets[ESPR.key(type)];
  const f = (S.le || S.l || [])[0];
  if (!f) return false;
  const k = ESPR.den(f), fw = f[3] / k, fh = f[4] / k;
  const sc = Math.min((r * 1.9) / fh, (r * 2.1) / fw);
  c.save();
  c.translate(x, y);
  c.scale(sc, sc);
  c.translate(f[5] / k - fw / 2, f[6] / k - fh / 2);
  ESPR.draw(c, f, false);
  c.restore();
  return true;
};

// marca da possessao no chao: mancha de fumaca roxo-escura respirando embaixo do bicho (some quando ele e libertado)
A.possessionStain = (c, e, t) => {
  return;   // satira: ninguem esta possuido
  const r = Math.max(9, e.T.size * 1.35) * (e.flying ? 0.7 : 1);
  const k = 0.85 + 0.15 * Math.sin(t * 2.1 + e.id * 1.7);
  c.save();
  c.scale(1, 0.42);
  const g = c.createRadialGradient(0, 0, 0, 0, 0, r * k);
  g.addColorStop(0, `rgba(34,16,44,${(e.flying ? 0.22 : 0.4) * k})`);
  g.addColorStop(0.6, `rgba(40,20,52,${(e.flying ? 0.12 : 0.22) * k})`);
  g.addColorStop(1, 'rgba(40,20,52,0)');
  c.fillStyle = g;
  c.beginPath(); c.arc(0, 0, r * k, 0, U.TAU); c.fill();
  c.restore();
};

// escala de exibicao extra por tipo (vazia: o tamanho dos pequenos agora vem do proprio render, sem borrar)
const ESPR_SCALE = {};

// altura do topo do sprite acima dos pes (unidades do jogo, sem o balanco do voo): a barra de vida fica colada no corpo
ESPR.tops = {};
A.enemyTop = e => {
  if (!ESPR.has(e.type)) return null;
  // por vista: bicho comprido visto de costas ou de frente fica mais alto na tela que de lado
  const S = INIMIGOS_META.sets[ESPR.key(e.type)];
  const v = e._vw && S[e._vw] ? e._vw : 'r';
  let t = ESPR.tops[e.type + v];
  if (t === undefined) {
    t = Math.max(...(S[v] || []).map(f => f[6] / ESPR.den(f))) * (ESPR_SCALE[e.type] || 1);
    ESPR.tops[e.type + v] = t;
  }
  const fl = ESPR_FLY[e.type];
  if (fl) t += e.type === 'ifrit' && !e.flying ? 10 : FLY_H + fl[0];
  return t;
};

// desenha o inimigo (ja transladado para os pes); devolve false se ainda nao tem sprite
// altura extra dos voadores: [ajuste, ritmo e tamanho do balanco]. Os modelos novos (GLB) tem o ponto mais baixo
// na origem (antes era o centro do corpo), por isso o ajuste e negativo: desce o corpo para a mesma altura de voo
const ESPR_FLY = { vulture: [-9, 3, 2], djinn: [-12, 2.5, 3], ifrit: [-16, 1.8, 3] };

A.enemySprite = (c, e, t, hidden) => {
  if (!ESPR.ready(e.type)) return false;
  const [f, flip, gf] = A.enemyFrame(e);
  if (!f) return false;
  if (!hidden) A.possessionStain(c, e, t);
  const fl = ESPR_FLY[e.type];
  if (fl) {
    const bob = Math.sin(t * fl[1] + e.id) * fl[2];
    c.translate(0, e.type === 'ifrit' && !e.flying ? -10 + bob : -FLY_H - fl[0] + bob);
  }
  const k = ESPR_SCALE[e.type];
  if (k) c.scale(k, k);
  ESPR.draw(c, f, flip);
  // brasas da possessao respirando como carvao vivo (cada bicho no seu ritmo)
  if (gf && !hidden) {
    c.save();
    c.globalCompositeOperation = 'lighter';
    c.globalAlpha = 0.3 + 0.45 * (0.5 + 0.5 * Math.sin(t * 3.1 + e.id * 2.3));
    ESPR.draw(c, gf, flip);
    c.restore();
  }
  // dano: clarao somando luz; congelado: brilho frio por cima
  if ((e.hurtT > 0 && !hidden) || e.frozenT > 0) {
    c.save();
    c.globalCompositeOperation = 'lighter';
    c.globalAlpha = e.hurtT > 0 ? 0.42 : 0.3 + Math.min(1, e.frozenT) * 0.2;
    ESPR.draw(c, f, flip);
    c.restore();
  }
  return true;
};

// libertacao (fx 'corpse' com os quadros l): a Fumaca Negra sai num sopro com brasas, o bicho estremece num clarao
// e, de volta as cores naturais, corre para a borda mais perto da tela, sumindo na mata
const LIB_A = 0.22;
A.enemyFreed = (c, f, k, S, sk) => {
  const e = f.e;
  const fl = ESPR_FLY[e.type];
  const lift = e.flying ? FLY_H + (fl ? fl[0] : 0) : e.type === 'ifrit' ? 10 : 0;
  if (!f._lib) {
    f._lib = 1;
    f.dir = e.x < W / 2 ? -1 : 1;
    if (typeof Vfx !== 'undefined') {
      const top = A.enemyTop(e) || 24, cy = e.y - top * 0.55, big = top > 40 ? 1.7 : 1;
      // virou delator: papelada voando (folhas do processo) e umas notas de dinheiro
      for (let i = 0; i < 12; i++) Vfx.emit(e.x + U.rand(-10, 10) * big, cy + U.rand(-8, 8) * big, U.rand(-40, 40), U.rand(-85, -35), U.rand(0.9, 1.5), U.rand(1.8, 2.6) * big, i % 2 ? '#f6f1e4' : '#e9e0cc', { kind: 'paper', grav: 40, drag: 0.5, rot: U.rand(-1, 1), spin: U.rand(-5, 5) });
      for (let i = 0; i < 8; i++) Vfx.emit(e.x + U.rand(-8, 8) * big, cy, U.rand(-50, 50), U.rand(-110, -50), U.rand(0.8, 1.2), U.rand(2.2, 2.8), '#79c463', { kind: 'bill', grav: 60, drag: 0.4, rot: U.rand(-1, 1), spin: U.rand(-4, 4) });
      for (let i = 0; i < 6; i++) Vfx.emit(e.x + U.rand(-12, 12) * big, e.y - U.rand(4, top), U.rand(-25, 25), U.rand(-40, -10), U.rand(0.6, 1.1), U.rand(1.2, 2.2), '#ffffff', { drag: 0.3 });
    }
  }
  c.save();
  c.translate(e.x, e.y);
  if (k < LIB_A) {
    const fr = S.x[Math.min(S.x.length - 1, Math.floor((k / LIB_A) * 3))];
    c.translate(Math.sin(k * 90) * 1.5, -lift);
    if (sk) c.scale(sk, sk);
    ESPR.draw(c, fr, e.facing < 0);
    c.globalCompositeOperation = 'lighter';
    c.globalAlpha = 0.55 * (1 - k / LIB_A);
    ESPR.draw(c, fr, e.facing < 0);
  } else {
    const kb = (k - LIB_A) / (1 - LIB_A);
    const dist = 90 * (0.5 * kb + 0.5 * kb * kb);
    c.translate(f.dir * dist, -dist * 0.22 - lift - (e.flying ? 40 * kb : 0));
    c.globalAlpha = kb < 0.6 ? 1 : Math.max(0, 1 - (kb - 0.6) / 0.4);
    if (sk) c.scale(sk, sk);
    ESPR.draw(c, S.l[Math.floor(kb * S.l.length * 2.4) % S.l.length], f.dir < 0);
    if (sk) c.scale(1 / sk, 1 / sk);
    A.whiteFlag(c, -f.dir * 4, -(A.enemyTop(e) || 24) + 4, kb * 9, f.dir);
  }
  c.restore();
  return true;
};

// bandeirinha branca de quem virou delator: mastro curto e pano tremulando, a partir de (x, y) para cima
A.whiteFlag = (c, x, y, t, dir = 1) => {
  c.save();
  c.strokeStyle = '#7a6650'; c.lineWidth = 1.6; c.lineCap = 'round';
  c.beginPath(); c.moveTo(x, y); c.lineTo(x, y - 18); c.stroke();
  const w = 2.2 * Math.sin(t * 7);
  c.fillStyle = '#ffffff'; c.strokeStyle = 'rgba(80,70,60,0.5)'; c.lineWidth = 0.8;
  c.beginPath(); c.moveTo(x, y - 18);
  c.quadraticCurveTo(x - dir * 6, y - 18 + w, x - dir * 12, y - 16);
  c.lineTo(x - dir * 12, y - 9);
  c.quadraticCurveTo(x - dir * 6, y - 11 - w, x, y - 10);
  c.closePath(); c.fill(); c.stroke();
  c.restore();
};

// cadaver: animacao de morte e desvanecer (fx 'corpse', k = 0..1); com os quadros l, vira libertacao
A.enemyCorpse = (c, f, k) => {
  const e = f.e;
  if (!ESPR.ready(e.type)) return false;
  const S = INIMIGOS_META.sets[ESPR.key(e.type)];
  if (S.l) return A.enemyFreed(c, f, k, S, ESPR_SCALE[e.type]);
  if (!S.x) return false;
  // candidato derrotado: a papelada da campanha voa e cai uma chuva de confete de festa da vitoria
  if (DATA.ENEMIES[e.type].final && !f._fin && typeof Vfx !== 'undefined') {
    f._fin = 1;
    for (let i = 0; i < 30; i++) Vfx.emit(e.x + U.rand(-30, 30), e.y - U.rand(10, 90), U.rand(-60, 60), U.rand(-90, -20), U.rand(1.2, 2.0), U.rand(2.4, 3.4), i % 2 ? '#f6f1e4' : '#e9e0cc', { kind: 'paper', grav: 30, drag: 0.5, rot: U.rand(-1, 1), spin: U.rand(-5, 5) });
    for (let i = 0; i < 80; i++) Vfx.emit(e.x + U.rand(-20, 20), e.y - U.rand(20, 70), U.rand(-140, 140), U.rand(-180, -40), U.rand(1.6, 2.8), U.rand(1.6, 2.4), ['#f7cf3c', '#2f9a4a', '#d8433b', '#ffffff'][i % 4], { kind: 'conf', grav: 70, drag: 0.35, rot: U.rand(0, 3), spin: U.rand(-6, 6) });
  }
  if (DATA.ENEMIES[e.type].final && typeof Light !== 'undefined') Light.add(e.x, e.y - 40, 260 * (1 - k * 0.6), '#fff1b0', 1.2 * (1 - k), 0.8);
  const fr = S.x[Math.min(S.x.length - 1, Math.floor(Math.min(1, k / 0.65) * S.x.length))];
  c.save();
  c.translate(e.x, e.y);
  c.globalAlpha = k < 0.6 ? 1 : Math.max(0, (1 - k) / 0.4);
  if (e.flying) c.translate(0, -FLY_H * (1 - Math.min(1, k * 1.6)));
  const sk = ESPR_SCALE[e.type];
  if (sk) c.scale(sk, sk);
  ESPR.draw(c, fr, e.facing < 0);
  c.restore();
  return true;
};
