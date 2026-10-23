'use strict';
// Unidades aliadas em sprites pre-renderizados no Blender (tools/blender/unidades_glb.py -> empacotar_inimigos.py --unidades):
// heroina, guardioes da Palafita, lanceiros, mateiros, guardioes do rio e mercenarios. Sem a folha pronta (ou sem
// js/unidades_meta.js), o A.drawUnit continua com o desenho 2D antigo.

const USPR = {
  imgs: {},
  state: {},

  has(kind) { return typeof UNIDADES_META !== 'undefined' && !!UNIDADES_META.sets[kind]; },

  // tropa da chapa: na Vermelha, quem sai do Sindicato sao militantes (conjuntos <tipo>_r), na Verde-Amarela, assessores
  key(u) {
    if (u.sk) return u.sk;
    const r = u.kind + '_r';
    return typeof DATA !== 'undefined' && DATA.SIDE === 'R' && this.has(r) ? r : u.kind;
  },

  want(kind) {
    if (!this.has(kind)) return;
    for (const i of UNIDADES_META.fams[kind] || []) {
      if (this.state[i]) continue;
      this.state[i] = 'loading';
      const im = new Image();
      im.onload = () => { this.state[i] = 'ok'; };
      im.onerror = () => { this.state[i] = 'err'; };
      im.src = UNIDADES_META.sheets[i];
      this.imgs[i] = im;
    }
  },

  ready(kind) {
    if (!this.has(kind)) return false;
    const fam = UNIDADES_META.fams[kind] || [];
    if (!fam.every(i => this.state[i] === 'ok')) { this.want(kind); return false; }
    return true;
  },

  den(f) {
    if (!this._den) {
      this._den = {};
      for (const [t, idx] of Object.entries(UNIDADES_META.fams)) for (const i of idx) this._den[i] = UNIDADES_META.scale * (UNIDADES_META.sets[t].pxk || 1);
    }
    return this._den[f[0]] || UNIDADES_META.scale;
  },

  draw(c, f) {
    const s = 1 / this.den(f);
    c.imageSmoothingEnabled = true;
    c.imageSmoothingQuality = 'high';
    c.drawImage(this.imgs[f[0]], f[1], f[2], f[3], f[4], -f[5] * s, -f[6] * s, f[3] * s, f[4] * s);
  },
};

// guardiao da Palafita cresce um pouco a cada nivel da torre
const USPR_TIER = [1, 1.06, 1.12];

A.unitFrame = u => {
  const S = UNIDADES_META.sets[USPR.key(u)];
  if (S.g && u.whirlT > 0) return S.g[Math.min(S.g.length - 1, Math.floor((1 - u.whirlT / 0.5) * S.g.length))];
  if (S.a && u.atkAnim > 0) {
    if (u.atkAnim > (u._am || 0) || !u._am) u._am = u.atkAnim;
    return S.a[Math.min(S.a.length - 1, Math.floor((1 - u.atkAnim / u._am) * S.a.length))];
  }
  u._am = 0;
  // parada: espera em laco (respira, olha em volta) de frente meio de lado (sudeste, espelhada pelo lado que olha),
  // cada unidade num ponto do laco; folha antiga sem espera: o quadro e_00. andando: a vista da direcao do passo
  if (!u.moving) {
    if (!S.i) return (S.e || S.r)[0];
    if (u._io == null) u._io = Math.random() * S.i.length;
    return S.i[Math.floor((A.clock || 0) * 12 + u._io) % S.i.length];
  }
  const seq = S[A.walkView(S, u, u.hdx || 0, u.hdy || 0)];
  const ph = ((u.walk || 0) / U.TAU) % 1;
  return seq[Math.floor((ph < 0 ? ph + 1 : ph) * seq.length) % seq.length];
};

// desenha a unidade ja transladada para os pes e virada (A.drawUnit); devolve false se ainda nao tem sprite
A.unitSprite = (c, u) => {
  if (!USPR.ready(USPR.key(u))) return false;
  const f = A.unitFrame(u);
  if (!f) return false;
  // na fase os bonecos saem maiores (CHAR_SCALE, js/inimigos.js)
  const k = (u.kind === 'soldier' ? USPR_TIER[Math.min(3, u.tier || 1) - 1] : 1) * charK();
  c.save();
  if (k !== 1) c.scale(k, k);
  USPR.draw(c, f);
  if (u.hurtT > 0) {
    c.globalCompositeOperation = 'lighter';
    c.globalAlpha = 0.4;
    USPR.draw(c, f);
  }
  c.restore();
  return true;
};

// topo do sprite acima dos pes (unidades do jogo): a barra de vida fica colada na cabeca
USPR.tops = {};
A.unitTop = u => {
  if (u.kind === 'beast') return A.beastTop ? A.beastTop(u) : null;
  const k = USPR.key(u);
  if (!USPR.has(k) || !USPR.ready(k)) return null;
  let t = USPR.tops[k];
  if (t === undefined) {
    t = Math.max(...UNIDADES_META.sets[k].r.map(f => f[6] / USPR.den(f)));
    USPR.tops[k] = t;
  }
  return t * (u.kind === 'soldier' ? USPR_TIER[Math.min(3, u.tier || 1) - 1] : 1) * charK();
};

// ---------------------------------------------------------------- vitrine (tela de herois e inicio)
// herois grandes renderizados com a camera baixa (unidades_glb.py -- vitrine -> empacotar_inimigos.py --vitrine):
// espera em laco (i) e chegada (c, gesto grande que volta ao quadro 0 da espera)
const VSPR = {
  imgs: {},
  state: {},
  FPS: 12,
  has(k) { return typeof VITRINE_META !== 'undefined' && !!VITRINE_META.sets[k]; },
  ready(k) {
    if (!this.has(k)) return false;
    const fam = VITRINE_META.fams[k] || [];
    for (const i of fam) {
      if (this.state[i]) continue;
      this.state[i] = 'loading';
      const im = new Image();
      im.onload = () => { this.state[i] = 'ok'; };
      im.onerror = () => { this.state[i] = 'err'; };
      im.src = VITRINE_META.sheets[i];
      this.imgs[i] = im;
    }
    return fam.every(i => this.state[i] === 'ok');
  },
  // solta as folhas (a fase precisa da memoria); voltam a carregar quando o inicio ou a tela de herois pedirem
  release() { this.imgs = {}; this.state = {}; for (const k in VSIL) delete VSIL[k]; },
  // quadro da vez: chegada enquanto chegaT < duracao, depois a espera (off desencontra herois lado a lado)
  frame(k, time, chegaT, off = 0) {
    const S = VITRINE_META.sets[k];
    if (chegaT != null && S.c && chegaT < S.c.length / this.FPS) return S.c[Math.max(0, Math.floor(chegaT * this.FPS))];
    const t = chegaT != null ? chegaT - S.c.length / this.FPS : time;
    return S.i[Math.floor(t * this.FPS + off) % S.i.length];
  },
};

// silhueta (heroi ainda trancado), feita uma vez por heroi; sem ctx.filter (o WebKit do app nao tem)
const VSIL = {};
function vitrineSil(k, f) {
  if (VSIL[k]) return VSIL[k];
  const cv = document.createElement('canvas');
  cv.width = f[3]; cv.height = f[4];
  const c = cv.getContext('2d');
  c.drawImage(VSPR.imgs[f[0]], f[1], f[2], f[3], f[4], 0, 0, f[3], f[4]);
  // so o corpo: o alfa vezes ele mesmo 5 vezes some com a sombra no chao (meio transparente, viraria uma mancha) e
  // deixa o corpo inteiro (sem getImageData: a imagem de file:// suja a tela no app)
  c.globalCompositeOperation = 'destination-in';
  for (let i = 0; i < 5; i++) c.drawImage(VSPR.imgs[f[0]], f[1], f[2], f[3], f[4], 0, 0, f[3], f[4]);
  c.globalCompositeOperation = 'source-in';
  c.fillStyle = 'rgba(52,34,22,0.82)';
  c.fillRect(0, 0, f[3], f[4]);
  return (VSIL[k] = cv);
}

// desenha o heroi k de pe em (x, y) (pes). escala: px da tela por px do render no heroi de referencia, dividida pelo
// boost de cada um, para todos ficarem na proporcao real entre si. o: {scale, chegaT, off, flip, sil, alpha}
// devolve a altura do topo do quadro acima dos pes (para particulas e etiquetas) ou 0 se ainda carrega
A.heroShow = (c, k, x, y, time, o = {}) => {
  if (!VSPR.ready(k)) return 0;
  const S = VITRINE_META.sets[k];
  const f = o.sil ? S.i[0] : VSPR.frame(k, time, o.chegaT, o.off || 0);
  const s = (o.scale || 2.7) / S.boost;
  c.save();
  c.translate(x, y);
  if (o.flip) c.scale(-1, 1);
  c.scale(s, s);
  if (o.alpha != null) c.globalAlpha *= o.alpha;
  c.imageSmoothingEnabled = true;
  c.imageSmoothingQuality = 'high';
  if (o.sil) c.drawImage(vitrineSil(k, f), -f[5], -f[6]);
  else if (o.tint) {
    // tingido (luz do entardecer no inicio): pinta por cima so onde o heroi existe, numa tela de apoio
    const cv = VSPR._tc || (VSPR._tc = document.createElement('canvas'));
    if (cv.width < f[3] || cv.height < f[4]) { cv.width = Math.max(cv.width, f[3]); cv.height = Math.max(cv.height, f[4]); }
    const tc = cv.getContext('2d');
    tc.globalCompositeOperation = 'source-over';
    tc.clearRect(0, 0, f[3], f[4]);
    tc.drawImage(VSPR.imgs[f[0]], f[1], f[2], f[3], f[4], 0, 0, f[3], f[4]);
    tc.globalCompositeOperation = 'source-atop';
    tc.fillStyle = o.tint;
    tc.fillRect(0, 0, f[3], f[4]);
    c.drawImage(cv, 0, 0, f[3], f[4], -f[5], -f[6], f[3], f[4]);
  } else c.drawImage(VSPR.imgs[f[0]], f[1], f[2], f[3], f[4], -f[5], -f[6], f[3], f[4]);
  c.restore();
  return f[6] * s;
};
