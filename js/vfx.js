'use strict';
// Luz dinamica e efeitos de magia (arte original, toda desenhada por codigo).
// Light: luzes pontuais do quadro. Depois que o mundo e desenhado, um mapa de luz clareia e tinge
//   o que ja esta na tela (chao, inimigos, torres) em vez de so somar um brilho por cima.
// Vfx: particulas e os efeitos das Joias da Arabia (purpurina carregando a pedra, diamante em voo, cacos de joia,
//   Corrente de Ouro, bau da Chuva de Brilhantes, reflexo do Relogio de Ouro), a torre comprada pelo Fundao e as
//   assinaturas dos personagens (um toque tematico por caricatura enquanto anda).

const hexRgb = (() => {
  const cache = {};
  return hex => cache[hex] || (cache[hex] = [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16)]);
})();
const rgbaOf = (hex, a) => { const c = hexRgb(hex); return `rgba(${c[0]},${c[1]},${c[2]},${U.clamp(a, 0, 1)})`; };
// chapa do jogador: as torres sao dele, entao os efeitos das torres que mudaram de tema escolhem por aqui
// (desenhos em js/satira.js, bloco "EFEITOS POR CHAPA")
const ladoV = () => typeof DATA !== 'undefined' && DATA.SIDE === 'V';
const ladoR = () => typeof DATA !== 'undefined' && DATA.SIDE === 'R';

// paletas da magia
const MAGIC = {
  arc: { core: '#fff6ff', mid: '#f2c8ff', glow: '#b86cff', deep: '#5a2a9a' },   // brilho de joia (Joias da Arabia)
  frost: { core: '#ffffff', mid: '#d4f4ff', glow: '#6cc8ff', deep: '#2a6fb0' },
  bolt: { core: '#fffbe8', mid: '#ffe8a0', glow: '#ffc83a', deep: '#a8701a' },   // Corrente de Ouro
  sun: { core: '#fffbe8', mid: '#ffe08a', glow: '#ffae3a', deep: '#d0601a' },
  gold: { core: '#fffdf0', mid: '#ffe7a0', glow: '#ffc53a', deep: '#a86f12' },   // purpurina e po de ouro
  grill: { core: '#fff2c8', mid: '#ffc070', glow: '#ff7a2a', deep: '#b8400e' },  // brasa do Churrascao da Picanha
};
// brasinhas que sobem para o espeto carregando (Churrascao)
const EMBERS = ['#fff2c0', '#ffb347', '#ff8a2a', '#ffd36a'];
// pedrinhas das Joias da Arabia: diamante, agua-marinha, rosa e ouro (e a versao fria do Brilho que Cega)
const GEMS = ['#ffffff', '#9eeaff', '#ff9ed4', '#ffd84a'];
const GEMS_FRIO = ['#ffffff', '#c8f2ff', '#8fdcff', '#e8f8ff'];
// Corrente de Ouro: contorno, ouro e brilho dos elos
const CHAIN = { dark: '#7a4e0c', mid: '#f2bd38', hi: '#fff4c4' };
// estrela de 4 pontas sem transformacao (barata para muitas por quadro); w = cintura relativa
const brilho4 = (c, x, y, r, w) => {
  const q = r * w;
  c.beginPath();
  c.moveTo(x, y - r); c.lineTo(x + q, y - q); c.lineTo(x + r, y); c.lineTo(x + q, y + q);
  c.lineTo(x, y + r); c.lineTo(x - q, y + q); c.lineTo(x - r, y); c.lineTo(x - q, y - q);
  c.closePath(); c.fill();
};

// particulas solidas (mistura normal): cada uma desenhada na origem, ja girada por p.r. p.s = tamanho, p.c = cor
const OUTL = 'rgba(48,28,24,0.55)';
const giroPapel = (p, sp) => Math.max(0.18, Math.abs(Math.cos(p.t * sp + p.s * 7)));   // giro "3D" de papel e moeda
const SOLID = {
  // confete: tira colorida virando no ar
  conf(c, p) {
    const h = p.s * 1.1 * giroPapel(p, 9);
    c.fillStyle = p.c;
    c.fillRect(-p.s, -h / 2, p.s * 2, h);
  },
  // bandeirinha triangular (Partidao)
  pennant(c, p) {
    const f = giroPapel(p, 7) * p.s;
    c.beginPath(); c.moveTo(-f * 0.9, -p.s * 0.75); c.lineTo(-f * 0.9, p.s * 0.75); c.lineTo(f * 1.3, 0); c.closePath();
    c.fillStyle = p.c; c.fill();
    c.strokeStyle = OUTL; c.lineWidth = 0.5; c.stroke();
  },
  // bandeirinha de tres faixas (p.c = [cor, cor, cor])
  flag3(c, p) {
    const w = p.s * 2, h = p.s * 1.3 * giroPapel(p, 6);
    for (let i = 0; i < 3; i++) { c.fillStyle = p.c[i]; c.fillRect(-w / 2 + (w / 3) * i, -h / 2, w / 3 + 0.2, h); }
    c.strokeStyle = OUTL; c.lineWidth = 0.5; c.strokeRect(-w / 2, -h / 2, w, h);
  },
  // folha de papel esvoacando, com duas linhas de texto (riscos, nunca letras)
  paper(c, p) {
    const w = p.s * 1.6, h = p.s * 2 * giroPapel(p, 6);
    c.fillStyle = p.c; c.fillRect(-w / 2, -h / 2, w, h);
    c.strokeStyle = OUTL; c.lineWidth = 0.5; c.strokeRect(-w / 2, -h / 2, w, h);
    c.fillStyle = 'rgba(90,80,70,0.45)';
    c.fillRect(-w * 0.3, -h * 0.2, w * 0.6, 0.5); c.fillRect(-w * 0.3, h * 0.12, w * 0.45, 0.5);
  },
  // nota de dinheiro verde
  bill(c, p) {
    const w = p.s * 2.4, h = p.s * 1.25 * giroPapel(p, 5);
    c.fillStyle = '#79c463'; c.fillRect(-w / 2, -h / 2, w, h);
    c.strokeStyle = '#2f6b2a'; c.lineWidth = 0.6; c.strokeRect(-w / 2, -h / 2, w, h);
    c.fillStyle = '#d2f2bc';
    c.beginPath(); c.ellipse(0, 0, h * 0.32, h * 0.32, 0, 0, U.TAU); c.fill();
  },
  // moeda de ouro girando (fica fina de perfil)
  coin(c, p) {
    const f = Math.abs(Math.cos(p.t * 8 + p.s * 3));
    const rx = p.s * Math.max(0.22, f);
    c.fillStyle = f > 0.3 ? '#ffd23f' : '#e0a826';
    c.beginPath(); c.ellipse(0, 0, rx, p.s, 0, 0, U.TAU); c.fill();
    c.strokeStyle = '#9a6a10'; c.lineWidth = 0.7; c.stroke();
    if (f > 0.45) { c.fillStyle = '#fff4c0'; c.beginPath(); c.ellipse(-rx * 0.3, -p.s * 0.35, rx * 0.28, p.s * 0.22, 0, 0, U.TAU); c.fill(); }
  },
  // nota musical (colcheia) balancando
  note(c, p) {
    const s = p.s, sw = Math.sin(p.t * 5 + s * 3) * 1.4;
    c.translate(sw, 0);
    c.beginPath();
    c.ellipse(0, 0, s * 0.72, s * 0.52, -0.45, 0, U.TAU);
    c.moveTo(s * 0.62 + 0.55, 0); c.lineTo(s * 0.62 + 0.55, -s * 2.3); c.lineTo(s * 0.62 - 0.55, -s * 2.3); c.lineTo(s * 0.62 - 0.55, -0.2);
    c.moveTo(s * 0.62, -s * 2.3); c.quadraticCurveTo(s * 1.7, -s * 1.9, s * 1.45, -s * 1.1); c.quadraticCurveTo(s * 1.3, -s * 1.6, s * 0.62, -s * 1.65);
    c.strokeStyle = OUTL; c.lineWidth = 1.2; c.stroke();
    c.fillStyle = p.c; c.fill();
  },
  // folhinha ou capim
  leaf(c, p) {
    c.beginPath(); c.ellipse(0, 0, p.s, p.s * 0.42, 0, 0, U.TAU);
    c.fillStyle = p.c; c.fill();
    c.strokeStyle = 'rgba(30,70,20,0.55)'; c.lineWidth = 0.45; c.stroke();
    c.beginPath(); c.moveTo(-p.s * 0.8, 0); c.lineTo(p.s * 0.8, 0); c.stroke();
  },
  // pena caindo em zigue-zague
  feather(c, p) {
    c.rotate(Math.sin(p.t * 4 + p.s) * 0.6);
    c.beginPath(); c.ellipse(0, 0, p.s, p.s * 0.34, 0, 0, U.TAU);
    c.fillStyle = p.c; c.fill();
    c.strokeStyle = 'rgba(255,255,255,0.8)'; c.lineWidth = 0.45;
    c.beginPath(); c.moveTo(-p.s * 1.25, 0); c.lineTo(p.s * 0.85, 0); c.stroke();
  },
  // estrelinha de 5 pontas
  star5(c, p) {
    const R = p.s, r = p.s * 0.45;
    c.beginPath();
    for (let i = 0; i < 10; i++) {
      const a = -Math.PI / 2 + (i * Math.PI) / 5, q = i % 2 ? r : R;
      if (i) c.lineTo(Math.cos(a) * q, Math.sin(a) * q); else c.moveTo(Math.cos(a) * q, Math.sin(a) * q);
    }
    c.closePath();
    c.fillStyle = p.c; c.fill();
    c.strokeStyle = OUTL; c.lineWidth = 0.5; c.stroke();
  },
  // caixa de papelao com fita (General Logistica)
  box(c, p) {
    const s = p.s;
    c.fillStyle = '#c99a5e'; c.fillRect(-s, -s, s * 2, s * 2);
    c.fillStyle = '#e2bb82'; c.fillRect(-s, -s, s * 2, s * 0.55);
    c.fillStyle = '#f4e2bc'; c.fillRect(-s * 0.18, -s, s * 0.36, s * 2);
    c.strokeStyle = '#6e4a26'; c.lineWidth = 0.7; c.strokeRect(-s, -s, s * 2, s * 2);
  },
  // envelope pardo lacrado
  env(c, p) {
    const w = p.s * 2, h = p.s * 1.3 * giroPapel(p, 5);
    c.fillStyle = '#dcbb86'; c.fillRect(-w / 2, -h / 2, w, h);
    c.strokeStyle = '#7a5a30'; c.lineWidth = 0.6; c.strokeRect(-w / 2, -h / 2, w, h);
    c.beginPath(); c.moveTo(-w / 2, -h / 2); c.lineTo(0, h * 0.1); c.lineTo(w / 2, -h / 2); c.stroke();
    c.fillStyle = '#c8352f'; c.beginPath(); c.arc(0, h * 0.1, Math.max(0.5, h * 0.18), 0, U.TAU); c.fill();
  },
  // pingo de tinta: gota no ar, borrao achatado depois que cai no chao
  drip(c, p) {
    c.fillStyle = p.c;
    c.beginPath();
    if (!p.land) c.ellipse(0, 0, p.s * 0.5, p.s * 0.7, 0, 0, U.TAU);
    else {
      const g = Math.min(1, (p.t - p.land) * 7);
      c.ellipse(0, 0, p.s * (0.7 + 0.9 * g), p.s * (0.3 + 0.3 * g), 0, 0, U.TAU);
    }
    c.fill();
  },
  // sinal de porcentagem desenhado com dois aneis e um risco (Taxad)
  pct(c, p) {
    const s = p.s;
    c.beginPath();
    c.moveTo(-s * 0.2, -s * 0.62); c.arc(-s * 0.55, -s * 0.62, s * 0.35, 0, U.TAU);
    c.moveTo(s * 0.9, s * 0.62); c.arc(s * 0.55, s * 0.62, s * 0.35, 0, U.TAU);
    c.moveTo(s * 0.75, -s); c.lineTo(-s * 0.75, s);
    c.lineCap = 'round';
    c.strokeStyle = 'rgba(80,50,10,0.75)'; c.lineWidth = 2; c.stroke();
    c.strokeStyle = p.c; c.lineWidth = 0.95; c.stroke();
  },
  // pontinho solido (po de ouro que aparece ate sobre o brilho)
  speck(c, p, k) {
    c.fillStyle = p.c;
    c.beginPath(); c.arc(0, 0, p.s * (1 - k * 0.5), 0, U.TAU); c.fill();
  },
  // farelo (pao e mortadela)
  crumb(c, p) {
    c.fillStyle = p.c; c.fillRect(-p.s / 2, -p.s / 2, p.s, p.s);
    c.strokeStyle = OUTL; c.lineWidth = 0.4; c.strokeRect(-p.s / 2, -p.s / 2, p.s, p.s);
  },
  // balaozinho de mensagem (Robo de Zap): verde, com rabinho e tres pontinhos
  chat(c, p) {
    const w = p.s * 2.4, h = p.s * 1.6;
    c.beginPath();
    c.moveTo(-w * 0.2, h / 2 - 0.3); c.lineTo(-w * 0.34, h / 2 + h * 0.45); c.lineTo(0, h / 2 - 0.3);
    c.fillStyle = p.c; c.fill();
    A.rrect(c, -w / 2, -h / 2, w, h, h * 0.45, p.c, 'rgba(20,70,40,0.75)', 0.6);
    c.fillStyle = '#ffffff';
    for (let i = -1; i <= 1; i++) c.fillRect(i * w * 0.24 - 0.45, -0.45, 0.9, 0.9);
  },
  // redemoinho de vento
  swirl(c, p) {
    c.beginPath();
    c.arc(0, 0, p.s, 0.4, Math.PI * 1.6);
    c.arc(p.s * 0.3, -p.s * 0.12, p.s * 0.5, Math.PI * 1.6, Math.PI * 2.9);
    c.lineCap = 'round';
    c.strokeStyle = 'rgba(30,60,110,0.35)'; c.lineWidth = 2; c.stroke();
    c.strokeStyle = p.c; c.lineWidth = 1; c.stroke();
  },
  // caco de joia lapidado (losango com reflexo)
  gem(c, p) {
    const s = p.s;
    c.beginPath(); c.moveTo(0, -s); c.lineTo(s * 0.62, 0); c.lineTo(0, s); c.lineTo(-s * 0.62, 0); c.closePath();
    c.fillStyle = p.c; c.fill();
    c.strokeStyle = 'rgba(70,50,110,0.5)'; c.lineWidth = 0.5; c.stroke();
    c.fillStyle = 'rgba(255,255,255,0.9)';
    c.beginPath(); c.moveTo(0, -s); c.lineTo(-s * 0.62, 0); c.lineTo(-s * 0.1, -s * 0.1); c.closePath(); c.fill();
  },
};

// ------------------------------------------------------------ LUZ
// Tom do ambiente por fase (multiplica a cena; as luzes abrem buracos nele). So entra quando a folha
// de sprites nao estiver tingida (SPR.tint), para nao escurecer duas vezes.
const AMBIENT = {
  // o fundo do Blender ja traz a cor do tema: o tom aqui so acerta a hora do dia
  canyon: '#fff0e2', ruins: '#f8eedf', citadel: '#c4c4dc', storm: '#f2ead8', ember: '#f2c2ae',
};

const Light = {
  list: [],
  cv: null,
  RES: 0.5, // mapa de luz em meia resolucao (suave e barato)
  g: null,

  begin(g) {
    this.list.length = 0;
    this.g = g;
  },

  // x, y em coordenadas do jogo; r = raio; k = intensidade (0..~1,5); bloom = brilho no ar (0..1)
  add(x, y, r, color, k, bloom) {
    if (!(k > 0.01)) return;
    if (!Number.isFinite(x) || !Number.isFinite(y) || !Number.isFinite(k) || !(r >= 4)) {
      if (r < 4) return;
      if (!this._warned) { this._warned = 1; console.warn('Light.add com valor invalido', x, y, r, color, k, new Error().stack); }
      return;
    }
    this.list.push({ x, y, r, c: color, k, b: bloom || 0 });
  },

  // cor e intensidade da luz num ponto (para tingir sprites)
  at(x, y) {
    let r = 0, g = 0, b = 0, k = 0;
    for (const L of this.list) {
      const dx = (x - L.x) / L.r, dy = (y - L.y) / (L.r * 0.8);
      const d2 = dx * dx + dy * dy;
      if (d2 >= 1) continue;
      const f = 1 - Math.sqrt(d2);
      const w = f * f * L.k;
      const c = hexRgb(L.c);
      r += c[0] * w; g += c[1] * w; b += c[2] * w; k += w;
    }
    if (k <= 0) return { r: 0, g: 0, b: 0, k: 0 };
    return { r: r / k, g: g / k, b: b / k, k: Math.min(1.5, k) };
  },

  ambient(g) {
    if (g.isNight && g.isNight()) return '#3e4a7a';   // noite de lua: azul escuro, as luzes devolvem a cor
    if (typeof SPR !== 'undefined' && SPR && SPR.tint) return null;
    return AMBIENT[g.L && g.L.theme] || null;
  },

  paint(c, base, mul) {
    c.globalCompositeOperation = 'source-over';
    c.fillStyle = base;
    c.fillRect(0, 0, W, H);
    c.globalCompositeOperation = 'lighter';
    for (const L of this.list) {
      const gr = c.createRadialGradient(L.x, L.y, 0, L.x, L.y, L.r);
      const a = Math.min(1, L.k * mul);
      gr.addColorStop(0, rgbaOf(L.c, a));
      gr.addColorStop(0.35, rgbaOf(L.c, a * 0.55));
      gr.addColorStop(1, rgbaOf(L.c, 0));
      c.fillStyle = gr;
      c.save();
      c.translate(L.x, L.y); c.scale(1, 0.8); c.translate(-L.x, -L.y);
      c.fillRect(L.x - L.r, L.y - L.r, L.r * 2, L.r * 2);
      c.restore();
    }
  },

  // aplica no canvas principal (ja com a transformacao do jogo)
  apply(c, g) {
    const amb = this.ambient(g);
    if (!this.list.length && !amb) return;
    if (!this.cv) {
      this.cv = document.createElement('canvas');
      this.cv.width = Math.round(W * this.RES);
      this.cv.height = Math.round(H * this.RES);
      this.cx = this.cv.getContext('2d');
    }
    const lc = this.cx;
    lc.setTransform(this.RES, 0, 0, this.RES, 0, 0);
    c.save();
    // 1) ambiente: escurece/tinge a cena, e as luzes devolvem a cor onde batem
    if (amb) {
      this.paint(lc, amb, 1.1);
      c.globalCompositeOperation = 'multiply';
      c.drawImage(this.cv, 0, 0, W, H);
    }
    // 2) luz que tinge: soft-light sobre cinza neutro clareia e colore sem lavar o contorno
    if (this.list.length) {
      this.paint(lc, '#808080', 0.6);
      c.globalCompositeOperation = 'soft-light';
      c.drawImage(this.cv, 0, 0, W, H);
      // 3) brilho no ar (bloom) so das luzes fortes
      c.globalCompositeOperation = 'lighter';
      for (const L of this.list) {
        if (!L.b) continue;
        const r = L.r * 0.55;
        const gr = c.createRadialGradient(L.x, L.y, 0, L.x, L.y, r);
        gr.addColorStop(0, rgbaOf(L.c, Math.min(0.35, L.k * L.b * 0.35)));
        gr.addColorStop(1, rgbaOf(L.c, 0));
        c.fillStyle = gr;
        c.fillRect(L.x - r, L.y - r, r * 2, r * 2);
      }
    }
    c.restore();
  },
};

// ------------------------------------------------------------ PARTICULAS E EFEITOS
const Vfx = {
  parts: [],
  g: null,
  last: 0,
  dt: 0,

  // avanca no tempo do jogo (pausa congela, x2 acelera)
  tick(g) {
    if (this.g !== g) { this.parts.length = 0; this.g = g; this.last = g.time; }
    this.dt = U.clamp(g.time - this.last, 0, 0.1);
    this.last = g.time;
    const dt = this.dt;
    if (!dt) return;
    const P = this.parts;
    for (let i = P.length - 1; i >= 0; i--) {
      const p = P[i];
      p.t += dt;
      if (p.t >= p.T) { P[i] = P[P.length - 1]; P.pop(); continue; }
      const dr = Math.pow(p.drag, dt);
      p.vx *= dr; p.vy = p.vy * dr + p.grav * dt;
      p.x += p.vx * dt; p.y += p.vy * dt;
      if (p.w) p.r += p.w * dt;
      // chao proprio (cacos de joia, caixas, moedas): quica e depois assenta
      if (p.fl != null && p.y > p.fl && p.vy > 0) {
        p.y = p.fl;
        if (p.bn > 0 && p.vy > 45) { p.vy *= -p.bn; p.vx *= 0.6; p.w *= 0.6; }
        else { p.vy = 0; p.vx *= 0.4; p.grav = 0; p.w = 0; if (!p.land) p.land = p.t; }
      }
    }
    if (P.length > 900) P.splice(0, P.length - 900);
  },

  // o: { kind, grav, drag, rot (giro inicial), spin (giro/s), floor (y do chao), bounce (0 = gruda no chao) }
  emit(x, y, vx, vy, T, s, color, o) {
    const p = { x, y, vx, vy, t: 0, T, s, c: color, grav: (o && o.grav) || 0, drag: (o && o.drag != null) ? o.drag : 0.2, kind: (o && o.kind) || 'dot', r: 0, w: 0, fl: null, bn: 0, land: 0 };
    if (o) {
      if (o.rot) p.r = o.rot;
      if (o.spin) p.w = o.spin;
      if (o.floor != null) { p.fl = o.floor; p.bn = o.bounce || 0; }
    }
    this.parts.push(p);
    return p;
  },

  // emissao continua com acumulador (por objeto) para nao depender da taxa de quadros
  rate(o, perSec) {
    o._em = (o._em || 0) + perSec * this.dt;
    const n = Math.floor(o._em);
    o._em -= n;
    return n;
  },

  burst(x, y, n, speed, color, o) {
    for (let i = 0; i < n; i++) {
      const a = U.rand(0, U.TAU), v = speed * U.rand(0.35, 1);
      this.emit(x, y, Math.cos(a) * v, Math.sin(a) * v * 0.8 - (o && o.up || 0), U.rand(0.25, 0.6) * ((o && o.life) || 1), U.rand(1.2, 2.6) * ((o && o.size) || 1), color, o);
    }
  },

  drawParts(c) {
    if (!this.parts.length) return;
    c.save();
    // fumaca (mistura normal) primeiro, luz (aditiva) por cima
    for (const p of this.parts) {
      if (p.kind !== 'smoke') continue;
      const k = p.t / p.T;
      c.fillStyle = rgbaOf(p.c, 0.42 * (1 - k) * Math.min(1, k * 6));
      c.beginPath();
      c.arc(p.x, p.y, p.s * (0.6 + k * 1.4), 0, U.TAU);
      c.fill();
    }
    // pecas solidas (confete, notas, moedas, cacos de joia...): mistura normal, giradas no proprio eixo
    const m = c.getTransform();
    let solid = 0;
    for (const p of this.parts) {
      const d = SOLID[p.kind];
      if (!d) continue;
      const k = p.t / p.T;
      c.globalAlpha = k < 0.1 ? k / 0.1 : k > 0.7 ? (1 - k) / 0.3 : 1;
      c.setTransform(m);
      c.translate(p.x, p.y);
      if (p.r) c.rotate(p.r);
      d(c, p, k);
      solid = 1;
    }
    if (solid) { c.setTransform(m); c.globalAlpha = 1; }
    c.globalCompositeOperation = 'lighter';
    c.lineCap = 'round';
    for (const p of this.parts) {
      if (p.kind === 'smoke') continue;
      const k = p.t / p.T;
      const a = k < 0.15 ? k / 0.15 : 1 - (k - 0.15) / 0.85;
      if (SOLID[p.kind]) {
        // caco de joia: pisca uma estrelinha de vez em quando
        if (p.kind !== 'gem') continue;
        const tw = Math.sin(p.t * 13 + p.s * 9);
        if (tw < 0.55) continue;
        c.fillStyle = rgbaOf('#ffffff', a * 0.95);
        brilho4(c, p.x, p.y, p.s * 2.6 * (tw - 0.55) / 0.45 + 0.5, 0.2);
      } else if (p.kind === 'glint') {
        // brilhinho de 4 pontas que cresce, pisca e some
        const tw = 0.7 + 0.3 * Math.sin(p.t * 24 + p.s * 5);
        c.fillStyle = rgbaOf(p.c, Math.min(1, a * 1.3));
        brilho4(c, p.x, p.y, p.s * tw * (0.5 + Math.sin(Math.PI * k)), 0.2);
      } else if (p.kind === 'spark') {
        c.strokeStyle = rgbaOf(p.c, a);
        c.lineWidth = p.s * (1 - k * 0.5);
        c.beginPath();
        c.moveTo(p.x, p.y);
        c.lineTo(p.x - p.vx * 0.035, p.y - p.vy * 0.035);
        c.stroke();
      } else {
        c.fillStyle = rgbaOf(p.c, a);
        c.beginPath();
        c.arc(p.x, p.y, p.s * (1 - k * 0.6), 0, U.TAU);
        c.fill();
      }
    }
    c.restore();
  },

  pal(t) {
    if (ladoR()) return MAGIC.grill;   // Churrascao da Picanha: brasa em todas as especializacoes
    if (t.spec === 'lightning') return MAGIC.bolt;
    if (t.spec === 'sun') return MAGIC.sun;
    return t.S && t.S.frost ? MAGIC.frost : MAGIC.arc;
  },

  topOf(t, g) {
    const p = A.spriteTop && A.spriteTop(t);
    return p ? [t.x + p[0], t.y + p[1]] : [t.x, t.y - g.towerTop(t)];
  },

  glow(c, x, y, r, hex, a) {
    if (!(a > 0) || !(r > 0) || !Number.isFinite(x) || !Number.isFinite(y)) return;
    const gr = c.createRadialGradient(x, y, 0, x, y, r);
    gr.addColorStop(0, rgbaOf(hex, a));
    gr.addColorStop(0.4, rgbaOf(hex, a * 0.45));
    gr.addColorStop(1, rgbaOf(hex, 0));
    c.fillStyle = gr;
    c.fillRect(x - r, y - r, r * 2, r * 2);
  },

  star(c, x, y, r, rot, hex, a) {
    c.save();
    c.translate(x, y);
    c.rotate(rot);
    c.fillStyle = rgbaOf(hex, a);
    for (let i = 0; i < 4; i++) {
      c.rotate(Math.PI / 2);
      c.beginPath();
      c.moveTo(0, -r); c.lineTo(r * 0.12, 0); c.lineTo(0, r * 0.12); c.lineTo(-r * 0.12, 0);
      c.closePath(); c.fill();
    }
    c.restore();
  },

  // diamante lapidado (mesa reta em cima, ponta embaixo) girando no eixo vertical; mistura normal
  gemIcon(c, x, y, r, spin, P, a) {
    if (!(r > 0.3) || !(a > 0.01)) return;
    const sx = Math.max(0.32, Math.abs(Math.cos(spin)));
    c.save();
    c.globalCompositeOperation = 'source-over';
    c.globalAlpha = Math.min(1, a);
    c.translate(x, y);
    c.scale(sx, 1);
    c.beginPath();
    c.moveTo(-r, -0.3 * r); c.lineTo(-0.5 * r, -0.8 * r); c.lineTo(0.5 * r, -0.8 * r); c.lineTo(r, -0.3 * r); c.lineTo(0, r);
    c.closePath();
    c.fillStyle = '#ffffff'; c.fill();
    c.strokeStyle = rgbaOf(P.deep, 0.75); c.lineWidth = Math.max(0.6, r * 0.12); c.stroke();
    // pavilhao tingido e as facetas
    c.beginPath(); c.moveTo(-r, -0.3 * r); c.lineTo(r, -0.3 * r); c.lineTo(0, r); c.closePath();
    c.fillStyle = rgbaOf(P.mid, 0.6); c.fill();
    c.beginPath();
    c.moveTo(-0.5 * r, -0.8 * r); c.lineTo(-0.25 * r, -0.3 * r); c.lineTo(0, r); c.lineTo(0.25 * r, -0.3 * r); c.lineTo(0.5 * r, -0.8 * r);
    c.moveTo(-r, -0.3 * r); c.lineTo(r, -0.3 * r);
    c.strokeStyle = rgbaOf(P.glow, 0.8); c.lineWidth = Math.max(0.4, r * 0.08); c.stroke();
    c.restore();
  },

  // elos da Corrente de Ouro: n elos guardados em _lx/_ly/_la (centro e angulo), alternando um de frente (anel)
  // e um de lado (barrinha) para parecerem enganchados. sc = escala do elo
  _lx: new Float32Array(1024), _ly: new Float32Array(1024), _la: new Float32Array(1024),
  links(c, n, sc, a) {
    if (n <= 0 || !(a > 0.01)) return;
    const X = this._lx, Y = this._ly, G = this._la;
    const rx = 3.3 * sc, ry = 1.9 * sc, hw = 3.1 * sc;
    c.globalAlpha = Math.min(1, a);
    c.lineCap = 'round';
    for (let pass = 0; pass < 2; pass++) {
      c.strokeStyle = pass ? CHAIN.mid : CHAIN.dark;
      c.beginPath();
      for (let i = 0; i < n; i += 2) {
        c.moveTo(X[i] + Math.cos(G[i]) * rx, Y[i] + Math.sin(G[i]) * rx);
        c.ellipse(X[i], Y[i], rx, ry, G[i], 0, U.TAU);
      }
      c.lineWidth = (pass ? 1.25 : 2.5) * sc; c.stroke();
      c.beginPath();
      for (let i = 1; i < n; i += 2) {
        const cx = Math.cos(G[i]) * hw, cy = Math.sin(G[i]) * hw;
        c.moveTo(X[i] - cx, Y[i] - cy); c.lineTo(X[i] + cx, Y[i] + cy);
      }
      c.lineWidth = (pass ? 1.45 : 2.8) * sc; c.stroke();
    }
    // reflexo claro no alto de cada anel
    c.fillStyle = CHAIN.hi;
    c.beginPath();
    const hr = 0.6 * sc;
    for (let i = 0; i < n; i += 2) { c.moveTo(X[i] - 0.6 * sc + hr, Y[i] - ry); c.arc(X[i] - 0.6 * sc, Y[i] - ry, hr, 0, U.TAU); }
    c.fill();
    c.globalAlpha = 1;
  },

  // enche _lx/_ly/_la com os elos de uma curva (quadratica de p0 a p1 com barriga sag), ate a fracao fr; devolve o total
  chainCurve(x0, y0, x1, y1, sag, fr, from, step) {
    const len = Math.hypot(x1 - x0, y1 - y0);
    const qx = (x0 + x1) / 2, qy = (y0 + y1) / 2 + sag;
    const nT = Math.max(2, Math.round(len / step));
    const nE = Math.min(Math.floor(nT * fr), 1023 - from);
    let n = from;
    for (let j = from > 0 ? 1 : 0; j <= nE; j++) {
      const u = j / nT, v = 1 - u;
      this._lx[n] = v * v * x0 + 2 * v * u * qx + u * u * x1;
      this._ly[n] = v * v * y0 + 2 * v * u * qy + u * u * y1;
      this._la[n] = Math.atan2(2 * v * (qy - y0) + 2 * u * (y1 - qy), 2 * v * (qx - x0) + 2 * u * (x1 - qx));
      n++;
    }
    return n;
  },

  // ---------------------------------------------------------- torre de magia: pedra carregando
  tower(c, tw, g, t) {
    this.towerExtra(c, tw, g, t);
    if (tw.type !== 'mage' || tw.working) return;
    const P = this.pal(tw);
    const [x, y] = this.topOf(tw, g);
    const off = tw.disabledT > 0;
    // brilho de repouso do cristal (luz que vaza para o chao e para a propria torre)
    const pulse = 0.85 + 0.15 * Math.sin(t * 2.3 + tw.id);
    Light.add(x, y + 34, 110, P.glow, off ? 0.06 : 0.2 * pulse);
    if (off) return;
    if (tw.spec === 'sun') {
      const k = tw.chargeT || 0;
      if (k <= 0.02) return;
      c.save();
      c.globalCompositeOperation = 'lighter';
      if (P === MAGIC.grill) {
        // Macarico: so a chama-piloto azul no bico e um calor em volta (a chama grande e o torchGrill)
        this.glow(c, x, y, 10 + 10 * k, P.glow, 0.25 + 0.2 * k);
        c.globalCompositeOperation = 'source-over';
        const fl = 0.8 + 0.2 * Math.sin(t * 29 + tw.id);
        c.fillStyle = 'rgba(90,150,255,0.85)';
        A.chFlame(c, x, y + 2, (6 + 4 * k) * fl, 2.4, Math.sin(t * 5) * 0.1);
        c.fillStyle = 'rgba(220,240,255,0.95)';
        A.chFlame(c, x, y + 2, (3 + 2 * k) * fl, 1.2, 0);
      } else {
        this.glow(c, x, y, 12 + 16 * k, P.glow, 0.35 + 0.35 * k);
        this.star(c, x, y, 14 + 20 * k, t * 0.6, P.mid, 0.5 * k);
        this.star(c, x, y, 8 + 10 * k, -t * 0.9 + 0.4, P.core, 0.6 * k);
      }
      c.restore();
      Light.add(x, y + 24, 100 + 60 * k, P.glow, 0.3 + 0.4 * k, 0.35);
      return;
    }
    const k = tw.chargeT || 0;
    const rel = tw.castT != null && tw.castT < 0.3 ? 1 - tw.castT / 0.3 : 0;
    c.save();
    c.globalCompositeOperation = 'lighter';
    const G = MAGIC.gold;
    // purpurina de ouro e de joia girando em espiral ate a pedra
    const grill = P === MAGIC.grill;
    if (k > 0.02) {
      const gems = grill ? EMBERS : P === MAGIC.frost ? GEMS_FRIO : GEMS;
      for (let i = 0; i < 9; i++) {
        const ph = (t * 1.5 + i / 9) % 1;
        const rr = 36 * (1 - ph);
        const ang = i * 0.698 + t * 3 + ph * 2.6;
        const px = x + Math.cos(ang) * rr, py = y + Math.sin(ang) * rr * 0.6;
        c.fillStyle = rgbaOf(i % 2 ? G.mid : gems[(i >> 1) % 4], k * Math.min(1, ph * 2.5));
        if (i % 3 === 0) brilho4(c, px, py, 1.8 + 2.8 * ph, 0.22);
        else { c.beginPath(); c.arc(px, py, 0.8 + 1.1 * ph, 0, U.TAU); c.fill(); }
      }
      this.glow(c, x, y, 8 + 14 * k, P.glow, 0.2 + 0.4 * k);
      this.star(c, x, y, 5 + 13 * k, t * 0.8 + tw.id, '#ffffff', 0.3 * k);
      // a pedra grande crescendo e girando no topo (Churrascao: o espeto de picanha esquentando)
      if (grill) this.skewerIcon(c, x, y, k, t, tw);
      else this.gemIcon(c, x, y, 1.6 + 4.6 * k, t * 2.6 + tw.id, P, 0.3 + 0.7 * k);
      // Rodizio: labaredas girando em volta do espeto
      if (grill && tw.spec === 'lightning' && k > 0.25) {
        const kk = Math.min(1, (k - 0.25) / 0.3);
        c.fillStyle = rgbaOf(P.mid, 0.7 * kk);
        for (let i = 0; i < 6; i++) {
          const an = t * 2.4 + tw.id + (i / 6) * U.TAU, fl = 0.75 + 0.25 * Math.sin(t * 23 + i * 2);
          A.chFlame(c, x + Math.cos(an) * 15, y + 6 + Math.sin(an) * 6, 7 * fl * kk, 2.2, Math.sin(t * 6 + i) * 0.2);
        }
      }
      // Corrente de Ouro: um laco de corrente girando em volta da pedra
      if (!grill && tw.spec === 'lightning' && k > 0.25) {
        const n = 12, kk = Math.min(1, (k - 0.25) / 0.3), spin = t * 1.8 + tw.id;
        for (let i = 0; i < n; i++) {
          const an = spin + (i / n) * U.TAU;
          this._lx[i] = x + Math.cos(an) * 15; this._ly[i] = y + 2 + Math.sin(an) * 6;
          this._la[i] = Math.atan2(Math.cos(an) * 6, -Math.sin(an) * 15);
        }
        c.save();
        c.globalCompositeOperation = 'source-over';
        this.links(c, n, 0.62, kk);
        c.restore();
      }
    }
    // soltura: anel de ouro se abrindo com diamantinhos montados nele
    if (rel > 0) {
      const rr = 8 + (1 - rel) * 28;
      c.strokeStyle = rgbaOf(grill ? P.mid : G.mid, rel);
      c.lineWidth = 2.5 * rel;
      c.beginPath(); c.ellipse(x, y, rr, rr * 0.6, 0, 0, U.TAU); c.stroke();
      c.fillStyle = rgbaOf(grill ? P.core : '#ffffff', rel);
      for (let i = 0; i < 6; i++) {
        const an = i * 1.047 + t;
        brilho4(c, x + Math.cos(an) * rr, y + Math.sin(an) * rr * 0.6, 2 + 2.5 * rel, 0.22);
      }
      this.glow(c, x, y, 24, grill ? P.mid : G.core, 0.55 * rel);
    }
    c.restore();
    const m = Math.max(k, rel);
    if (m > 0.02) Light.add(x, y + 24, 80 + 80 * m, P.glow, 0.15 + 0.55 * m, 0.3 * m);
  },

  // ---------------------------------------------------------- diamante em voo
  orb(c, p, g, t) {
    if (ladoR()) return this.orbGrill(c, p, g, t);
    const P = p.frost ? MAGIC.frost : MAGIC.arc;
    const R = p.big ? 1.65 : 1;
    const age = p.age || 0;
    c.save();
    c.globalCompositeOperation = 'lighter';
    c.lineCap = 'round';
    // rastro de cometa afinando
    const tr = p.trail || [];
    const all = tr.concat([[p.x, p.y]]);
    for (let i = 1; i < all.length; i++) {
      const a = i / all.length;
      c.strokeStyle = rgbaOf(P.glow, 0.32 * a);
      c.lineWidth = (2 + 9 * a) * R;
      c.beginPath(); c.moveTo(all[i - 1][0], all[i - 1][1]); c.lineTo(all[i][0], all[i][1]); c.stroke();
    }
    for (let i = Math.max(1, all.length - 6); i < all.length; i++) {
      const a = (i - all.length + 6) / 6;
      c.strokeStyle = rgbaOf(P.mid, 0.55 * a);
      c.lineWidth = (1 + 3 * a) * R;
      c.beginPath(); c.moveTo(all[i - 1][0], all[i - 1][1]); c.lineTo(all[i][0], all[i][1]); c.stroke();
    }
    // halo
    this.glow(c, p.x, p.y, 20 * R, P.glow, 0.5);
    this.glow(c, p.x, p.y, 10 * R, P.mid, 0.7);
    this.star(c, p.x, p.y, 12 * R, age * 4, P.core, 0.4);
    c.restore();
    // brilhinhos de ouro orbitando a pedra (estrelas de 4 pontas que piscam); solidos para aparecerem sobre o brilho
    const G = MAGIC.gold;
    const nv = p.big ? 5 : 3;
    for (let i = 0; i < nv; i++) {
      const a = age * (6 + i * 0.8) + (i * U.TAU) / nv;
      const rx = (9 + (i % 2) * 2.5) * R;
      const fx = p.x + Math.cos(a) * rx, fy = p.y + Math.sin(a) * rx * 0.5 - Math.cos(a) * 1.5;
      const pisca = 0.5 + 0.5 * Math.sin(age * (15 + i * 2) + i * 2.1);
      c.fillStyle = i % 2 ? '#f2b22a' : '#ffd84a';
      brilho4(c, fx, fy, (1.6 + 2.4 * pisca) * R, 0.22);
    }
    // a joia no centro: diamante lapidado girando
    this.gemIcon(c, p.x, p.y, 4.4 * R, age * 7, P, 1);
    // po de ouro que fica para tras (cai devagar) com uns brilhinhos
    const n = this.rate(p, p.big ? 50 : 30);
    for (let i = 0; i < n; i++) {
      const gl = i % 4 === 0;
      this.emit(p.x + U.rand(-3, 3), p.y + U.rand(-3, 3), U.rand(-20, 20), U.rand(-18, 14), U.rand(0.35, 0.7), gl ? U.rand(2.2, 3.2) * R : U.rand(0.6, 1.1) * R, gl ? '#ffffff' : i % 2 ? '#f2b22a' : '#ffd84a', { kind: gl ? 'glint' : 'speck', drag: 0.15, grav: gl ? 0 : 45 });
    }
    Light.add(p.x, p.y + 12, 90 * R, P.glow, p.big ? 0.8 : 0.5, p.big ? 0.35 : 0.15);
  },

  // ---------------------------------------------------------- estouro de joia
  magicHit(c, f, g) {
    if (ladoR()) return this.magicHitGrill(c, f, g);
    const P = f.frost ? MAGIC.frost : MAGIC.arc;
    const k = f.t / f.T, a = 1 - k;
    const R = f.big ? 1.6 : 1;
    const gx = f.gx != null ? f.gx : f.x, gy = f.gy != null ? f.gy : f.y + 14;
    if (!f._sp) {
      f._sp = 1;
      this.burst(f.x, f.y, f.big ? 28 : f.r ? 16 : 9, (f.big ? 260 : 170), P.mid, { kind: 'spark', drag: 0.05, grav: 160, size: R });
      this.burst(f.x, f.y, f.big ? 14 : 6, 60, P.core, { drag: 0.1, size: 1.2 * R, up: 30 });
      // cacos de joia saltam do impacto, quicam no chao em volta do alvo e somem piscando
      const gems = f.frost ? GEMS_FRIO : GEMS;
      const ns = f.big ? 16 : f.r ? 10 : 5, spread = f.r || 22;
      for (let i = 0; i < ns; i++) {
        const an = U.rand(0, U.TAU), sp = U.rand(25, 80) * R;
        this.emit(f.x, f.y, Math.cos(an) * sp, U.rand(-150, -70) * (f.r ? 1 : 0.7), U.rand(0.75, 1.15), U.rand(1.6, 2.4) * (f.big ? 1.15 : 1), gems[i % 4],
          { kind: 'gem', grav: 420, drag: 0.5, rot: U.rand(-0.4, 0.4), spin: U.rand(-7, 7), floor: gy + Math.sin(an) * spread * 0.55 * U.YS, bounce: 0.45 });
      }
    }
    c.save();
    c.globalCompositeOperation = 'lighter';
    // chao: onda de choque (e, no Brilho que Cega, um colar de diamantes que acende em volta)
    if (f.r) {
      const e = U.easeOutCubic(Math.min(1, k * 1.4));
      const rr = f.r * (0.3 + 0.8 * e);
      c.save();
      c.translate(gx, gy); c.scale(1, U.YS);
      this.glow(c, 0, 0, rr * 1.1, P.glow, 0.4 * a);
      c.strokeStyle = rgbaOf(P.mid, a);
      c.lineWidth = 1 + 2.5 * a;
      c.beginPath(); c.arc(0, 0, rr, 0, U.TAU); c.stroke();
      c.restore();
      if (f.frost) {
        const ra = f.r * (0.45 + 0.2 * e), rot = k * 1.3 + (f.x % 7), lift = 4 + 6 * e;
        const fa = Math.min(1, a * 1.8);
        // fio de ouro do colar
        c.save();
        c.globalCompositeOperation = 'source-over';
        c.globalAlpha = fa;
        c.strokeStyle = CHAIN.dark; c.lineWidth = 2.2;
        c.beginPath(); c.ellipse(gx, gy - lift, ra, ra * U.YS, 0, 0, U.TAU); c.stroke();
        c.strokeStyle = CHAIN.mid; c.lineWidth = 1.1; c.stroke();
        // as pedras: losangos em pe, de frente para a camera
        const nd = 12;
        for (let i = 0; i < nd; i++) {
          const an = rot + (i / nd) * U.TAU;
          const qx = gx + Math.cos(an) * ra, qy = gy - lift + Math.sin(an) * ra * U.YS;
          const s = (i % 3 ? 2.4 : 3.4) * (0.85 + 0.15 * Math.sin(an));
          c.beginPath(); c.moveTo(qx, qy - s * 1.25); c.lineTo(qx + s * 0.7, qy); c.lineTo(qx, qy + s); c.lineTo(qx - s * 0.7, qy); c.closePath();
          c.fillStyle = i % 3 ? '#eafaff' : '#bfeeff'; c.fill();
          c.strokeStyle = '#3f7ea8'; c.lineWidth = 0.6; c.stroke();
        }
        c.restore();
        // o brilho corre de pedra em pedra e o colar inteiro da um clarao no comeco
        c.fillStyle = rgbaOf('#ffffff', fa);
        for (let j = 0; j < 2; j++) {
          const i = (Math.floor(k * 30) + j * 6) % nd;
          const an = rot + (i / nd) * U.TAU;
          brilho4(c, gx + Math.cos(an) * ra, gy - lift + Math.sin(an) * ra * U.YS, 5 + 3 * Math.sin(k * 40), 0.2);
        }
        if (k < 0.25) {
          c.save();
          c.translate(gx, gy - lift); c.scale(1, U.YS);
          c.strokeStyle = rgbaOf(P.core, 0.8 * (1 - k / 0.25)); c.lineWidth = 3;
          c.beginPath(); c.arc(0, 0, ra, 0, U.TAU); c.stroke();
          c.restore();
        }
      }
    }
    // estouro no ponto do impacto: clarao de diamante
    this.glow(c, f.x, f.y, (16 + 20 * k) * R, P.glow, 0.6 * a);
    if (k < 0.3) this.glow(c, f.x, f.y, 14 * R, P.core, 0.85 * (1 - k / 0.3));
    if (k < 0.4) this.star(c, f.x, f.y, (8 + 14 * U.easeOutCubic(k / 0.4)) * R, 0.4 + k, '#ffffff', 0.85 * (1 - k / 0.4));
    c.strokeStyle = rgbaOf(MAGIC.gold.mid, a);
    c.lineWidth = 2 * a + 0.5;
    c.beginPath(); c.arc(f.x, f.y, (5 + 24 * U.easeOutCubic(k)) * R, 0, U.TAU); c.stroke();
    // Esfera Maior: coluna de luz
    if (f.big && k < 0.7) {
      const ka = 1 - k / 0.7, w = 22 * ka;
      const gr = c.createLinearGradient(0, gy - 170, 0, gy);
      gr.addColorStop(0, rgbaOf(P.glow, 0));
      gr.addColorStop(0.7, rgbaOf(P.mid, 0.55 * ka));
      gr.addColorStop(1, rgbaOf(P.core, 0.85 * ka));
      c.fillStyle = gr;
      c.fillRect(gx - w / 2, gy - 170, w, 170);
    }
    c.restore();
    Light.add(gx, gy, (f.r ? f.r * 2.4 : 70) * R, P.glow, Math.pow(a, 1.4) * (f.big ? 1.1 : f.r ? 0.85 : 0.6), f.big ? 0.5 : 0.25);
  },

  // ---------------------------------------------------------- Corrente de Ouro (salta de alvo em alvo)
  // Corrente de Ouro: a corrente sai do topo da torre, laca alvo por alvo e um brilho corre por ela
  lightning(c, f, g) {
    if (ladoR()) return this.lightningGrill(c, f, g);
    const P = MAGIC.gold;
    const k = f.t / f.T, a = k < 0.6 ? 1 : 1 - (k - 0.6) / 0.4;
    const pts = f.pts, ns = pts.length - 1;
    if (!f._sp) {
      f._sp = 1;
      for (let i = 1; i < pts.length; i++) {
        this.burst(pts[i][0], pts[i][1], 6, 150, i % 2 ? P.mid : P.core, { kind: 'spark', drag: 0.04, grav: 220 });
        for (let j = 0; j < 3; j++) this.emit(pts[i][0] + U.rand(-9, 9), pts[i][1] + U.rand(-9, 6), U.rand(-20, 20), U.rand(-40, -10), U.rand(0.35, 0.6), U.rand(2.4, 3.4), j % 2 ? '#ffffff' : P.mid, { kind: 'glint', drag: 0.3 });
      }
    }
    if (ns < 1) return;
    // a ponta da corrente chega ao ultimo alvo no primeiro quarto do tempo; depois ela balanca e estica
    const reach = U.easeOutCubic(Math.min(1, k / 0.26)) * ns;
    const whip = Math.sin(k * 20) * (1 - k) * 0.5;
    let n = 0;
    for (let i = 0; i < ns; i++) {
      const fr = U.clamp(reach - i, 0, 1);
      if (fr <= 0) break;
      const [x0, y0] = pts[i], [x1, y1] = pts[i + 1];
      const len = Math.hypot(x1 - x0, y1 - y0);
      const sag = Math.min(24, len * 0.12) * (1 + whip);
      n = this.chainCurve(x0, y0, x1, y1, sag, fr, n, i === 0 ? 5.6 : 5.2);
      Light.add((x0 + x1) / 2, (y0 + y1) / 2 + 16, 80, P.glow, 0.35 * a * fr);
    }
    c.save();
    // brilho quente por baixo dos elos
    c.globalCompositeOperation = 'lighter';
    c.strokeStyle = rgbaOf(P.glow, 0.28 * a); c.lineWidth = 8; c.lineJoin = 'round'; c.lineCap = 'round';
    c.beginPath();
    for (let i = 0; i < n; i += 3) { if (i) c.lineTo(this._lx[i], this._ly[i]); else c.moveTo(this._lx[i], this._ly[i]); }
    if (n > 1) c.lineTo(this._lx[n - 1], this._ly[n - 1]);
    c.stroke();
    c.globalCompositeOperation = 'source-over';
    this.links(c, n, 1, a);
    // o brilho correndo pela corrente, da torre ao ultimo alvo
    c.globalCompositeOperation = 'lighter';
    const q = (k - 0.12) / 0.5;
    if (q > 0 && q < 1 && n > 2) {
      const i = Math.min(n - 1, Math.floor(q * n));
      const gx = this._lx[i], gy = this._ly[i];
      this.glow(c, gx, gy, 14, P.glow, 0.8 * a);
      this.star(c, gx, gy, 9, k * 6, '#ffffff', a);
    }
    // ganchos nos alvos: clarao dourado onde a corrente prende
    for (let i = 1; i < pts.length; i++) {
      if (reach < i - 0.05) break;
      const [x, y] = pts[i];
      this.glow(c, x, y, 18, P.mid, 0.6 * a);
      Light.add(x, y + 14, 100, P.glow, 0.7 * a, 0.3);
    }
    c.restore();
  },

  // Chuva de Brilhantes: um bau de tesouro aberto flutuando sobre a area, balancando, com brilho de ouro;
  // os brilhantes que caem dele sao desenhados no render.js (skybolt). Sombra no chao como a da antiga nuvem
  cloud(c, f, g, t) {
    if (ladoR()) return this.cloudGrill(c, f, g, t);
    const G = MAGIC.gold;
    const a = Math.min(1, f.t * 3, (f.T - f.t) * 3);
    const pop = U.easeOutBack(Math.min(1, f.t * 2.6));
    const bob = Math.sin(t * 2.2 + f.x * 0.1) * 4;
    const cx = f.x, cy = f.y - 112 + bob;
    c.save();
    // sombra no chao (encolhe quando o bau sobe)
    c.save();
    c.translate(f.x, f.y + 4); c.scale(1, U.YS * 0.75);
    const sr = 62 - bob * 1.5;
    const sh = c.createRadialGradient(0, 0, 0, 0, 0, sr);
    sh.addColorStop(0, `rgba(48,30,12,${0.26 * a})`);
    sh.addColorStop(1, 'rgba(48,30,12,0)');
    c.fillStyle = sh;
    c.fillRect(-sr, -sr, sr * 2, sr * 2);
    c.restore();
    // aura de ouro atras do bau
    c.globalCompositeOperation = 'lighter';
    this.glow(c, cx, cy - 8, 74, G.glow, 0.42 * a * (0.85 + 0.15 * Math.sin(t * 5)));
    c.globalCompositeOperation = 'source-over';
    c.globalAlpha = a;
    c.translate(cx, cy);
    c.rotate(Math.sin(t * 1.7 + f.x) * 0.06);
    c.scale(pop * 1.15, pop * 1.15);
    const OL = '#4a2410';
    // tampa aberta para tras (vemos o lado de dentro)
    A.poly(c, [[-25, -10], [-21, -30], [21, -30], [25, -10]], '#6a3416', OL, 1.4);
    A.poly(c, [[-21, -30], [-18, -35], [18, -35], [21, -30]], '#8a4a20', OL, 1.2);
    A.line(c, -23, -12, -19.5, -31, '#f2c14e', 2.2);
    A.line(c, 23, -12, 19.5, -31, '#f2c14e', 2.2);
    // monte de ouro e joias saindo pela boca
    A.ell(c, 0, -10, 24, 7.5, '#f5c637', '#a8701a', 1);
    const bumps = [[-15, -12, 4], [-7, -15, 5], [3, -14, 5.5], [12, -12, 4.5], [18, -10, 3.5], [-2, -9, 4]];
    for (let i = 0; i < bumps.length; i++) {
      const [bx, by, br] = bumps[i];
      A.ell(c, bx, by, br, br * 0.7, i % 2 ? '#ffd84a' : '#ffe58a', '#b07a12', 0.8);
    }
    const jewels = [[-10, -16, '#ff6fae'], [6, -18, '#7fe0ff'], [14, -15, '#7ed957'], [-1, -19, '#ffffff']];
    for (const [jx, jy, col] of jewels) {
      c.beginPath(); c.moveTo(jx, jy - 3.4); c.lineTo(jx + 2.2, jy); c.lineTo(jx, jy + 2.8); c.lineTo(jx - 2.2, jy); c.closePath();
      c.fillStyle = col; c.fill(); c.strokeStyle = 'rgba(60,30,40,0.6)'; c.lineWidth = 0.7; c.stroke();
    }
    // um colar de perolas pendurado na beirada
    c.fillStyle = '#fff6ea';
    for (let i = 0; i < 6; i++) { c.beginPath(); c.arc(8 + i * 2.6, -8 + Math.sin(i * 0.6) * 4 + i * 0.6, 1.25, 0, U.TAU); c.fill(); }
    // corpo do bau: madeira, cintas de ouro e a fechadura
    A.rrect(c, -26, -10, 52, 26, 4, '#9a5426', OL, 1.6);
    A.line(c, -24, -1, 24, -1, '#7a3f1c', 1);
    A.line(c, -24, 7, 24, 7, '#7a3f1c', 1);
    for (const bx of [-17, 17]) A.rect(c, bx - 3, -10, 6, 26, '#f2c14e', '#a8701a', 0.9);
    A.rect(c, -26, -11.5, 52, 4, '#ffd658', '#a8701a', 0.9);
    A.rrect(c, -4.5, -6, 9, 10, 2, '#ffd84a', '#a8701a', 0.9);
    A.circ(c, 0, -2.5, 1.4, '#5a3410');
    A.rect(c, -0.6, -2, 1.2, 3.6, '#5a3410');
    c.restore();
    // brilhinhos piscando sobre o tesouro
    c.save();
    c.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 4; i++) {
      const tw = Math.sin(t * 7 + i * 1.9 + f.x);
      if (tw < 0.2) continue;
      const sx = cx + (-16 + i * 11) * 1.15 * pop, sy = cy + (-16 - (i % 2) * 5) * 1.15 * pop;
      c.fillStyle = rgbaOf('#ffffff', a * tw);
      brilho4(c, sx, sy, 2 + 4 * tw, 0.2);
    }
    c.restore();
    // de vez em quando uma pedra escorrega pela beirada, cai e quica no chao
    const n = this.rate(f, 7 * a);
    for (let i = 0; i < n; i++) {
      this.emit(cx + U.rand(-22, 22), cy - 6, U.rand(-25, 25), U.rand(-60, -20), 1.3, U.rand(1.8, 2.4), GEMS[(Math.random() * 4) | 0],
        { kind: 'gem', grav: 320, drag: 0.6, rot: U.rand(-0.4, 0.4), spin: U.rand(-6, 6), floor: f.y + U.rand(-30, 30) * U.YS, bounce: 0.4 });
    }
    Light.add(cx, f.y - 20, 140, G.glow, 0.4 * a * (0.85 + 0.15 * Math.sin(t * 6)), 0.25);
  },

  // ---------------------------------------------------------- marcas no inimigo
  enemy(c, e, g, t) {
    this.enemyExtra(e, g, t);
    this.sig(c, e, g, t);
    if (!(e.shockT > 0 || e.arcT > 0 || e.heatT > 0)) return;
    const y = g.hitY(e), s = e.T.size;
    c.save();
    if (e.shockT > 0 && ladoR()) this.searGrill(c, e, y, s, t);
    else if (e.shockT > 0) {
      // Corrente de Ouro / Choque de Quilates: lacos de corrente apertando em volta do corpo, com brilhinhos
      const a = Math.min(1, e.shockT / 0.4);
      const el = Math.max(0, 0.7 - e.shockT);
      const tight = 1 + 0.55 * (1 - U.easeOutCubic(Math.min(1, el / 0.18)));
      const loops = s > 18 ? 2 : 1;
      for (let L = 0; L < loops; L++) {
        const ly = y + (loops > 1 ? (L ? -s * 0.35 : s * 0.3) : 0);
        const rx = s * 1.05 * tight, ry = Math.max(3.5, s * 0.36) * tight;
        const spin = t * 2.4 * (L ? -1 : 1) + e.id;
        const n = Math.max(10, Math.min(28, Math.round((rx * 2 * Math.PI * 0.75) / 4.4) & ~1));
        // metade de tras mais apagada, metade da frente cheia: parece que a corrente da a volta no corpo
        for (let half = 0; half < 2; half++) {
          let m = 0;
          for (let i = 0; i < n; i++) {
            const an = spin + (i / n) * U.TAU;
            const front = Math.sin(an) > 0;
            if (front !== !!half) continue;
            this._lx[m] = e.x + Math.cos(an) * rx; this._ly[m] = ly + Math.sin(an) * ry;
            this._la[m] = Math.atan2(Math.cos(an) * ry, -Math.sin(an) * rx);
            m++;
          }
          this.links(c, m, 0.6, a * (half ? 1 : 0.45));
        }
      }
      c.globalCompositeOperation = 'lighter';
      c.fillStyle = rgbaOf('#ffffff', a);
      for (let i = 0; i < 3; i++) {
        const tw = Math.sin(t * 11 + i * 2.2 + e.id);
        if (tw < 0.3) continue;
        const an = t * 1.3 + i * 2.1 + e.id;
        brilho4(c, e.x + Math.cos(an) * s * 1.05, y + Math.sin(an) * s * 0.36 - 2, 2 + 3.5 * tw, 0.2);
      }
      c.globalCompositeOperation = 'source-over';
      Light.add(e.x, y + 10, 50 + s * 2, MAGIC.gold.glow, 0.45 * a);
    }
    c.globalCompositeOperation = 'lighter';
    if (e.arcT > 0) {
      const k = 1 - e.arcT / 0.45, PA = ladoR() ? MAGIC.grill : MAGIC.arc;   // R: brasa do Churrascao
      c.strokeStyle = rgbaOf(PA.mid, 1 - k);
      c.lineWidth = 2;
      c.beginPath(); c.ellipse(e.x, e.y + 1, s + 4 + k * 10, (s + 4 + k * 10) * 0.42, 0, 0, U.TAU); c.stroke();
      this.glow(c, e.x, y, s * 1.6, PA.glow, 0.45 * (1 - k));
    }
    if (e.heatT > 0) {
      const a = Math.min(1, e.heatT / 0.25);
      this.glow(c, e.x, y, s * 1.9, MAGIC.sun.glow, 0.5 * a);
      const n = this.rate(e, 18);
      for (let i = 0; i < n; i++) this.emit(e.x + U.rand(-s, s), y + U.rand(-4, 6), U.rand(-8, 8), U.rand(-60, -30), U.rand(0.4, 0.8), U.rand(1, 1.8), i % 2 ? MAGIC.sun.mid : MAGIC.sun.glow, { drag: 0.4 });
    }
    c.restore();
  },

  // ---------------------------------------------------------- feixe do Obelisco Solar
  sunBeam(c, tw, g, t) {
    if (ladoR()) return this.torchGrill(c, tw, g, t);
    const e = tw.beam;
    if (!e || e.dead) return;
    const P = MAGIC.sun;
    const [x0, y0] = this.topOf(tw, g);
    const x1 = e.x, y1 = g.hitY(e);
    const k = Math.min(1, tw.beamT / tw.S.ramp);
    const dx = x1 - x0, dy = y1 - y0, len = Math.hypot(dx, dy) || 1;
    const nx = -dy / len, ny = dx / len;
    const w = 3 + k * 7 + Math.sin(t * 31) * 0.8;
    c.save();
    c.globalCompositeOperation = 'lighter';
    c.lineCap = 'round';
    A.line(c, x0, y0, x1, y1, rgbaOf(P.deep, 0.25 + 0.2 * k), w * 3.6);
    A.line(c, x0, y0, x1, y1, rgbaOf(P.glow, 0.45 + 0.3 * k), w * 1.9);
    A.line(c, x0, y0, x1, y1, rgbaOf(P.mid, 0.8), w);
    A.line(c, x0, y0, x1, y1, rgbaOf(P.core, 0.95), Math.max(1.3, w * 0.35));
    // calor ondulando dos lados do feixe
    for (const sd of [-1, 1]) {
      c.beginPath();
      for (let i = 0; i <= 14; i++) {
        const q = i / 14;
        const off = sd * (w * 1.1 + Math.sin(q * 18 - t * 14 + sd) * (1.5 + 2.5 * k));
        const px = x0 + dx * q + nx * off, py = y0 + dy * q + ny * off;
        if (i) c.lineTo(px, py); else c.moveTo(px, py);
      }
      c.strokeStyle = rgbaOf(P.mid, 0.25 + 0.2 * k);
      c.lineWidth = 1.2;
      c.stroke();
    }
    // pulsos de luz correndo da lente ao alvo
    for (let i = 0; i < 4; i++) {
      const q = (t * (1.6 + k) + i / 4) % 1;
      this.glow(c, x0 + dx * q, y0 + dy * q, 6 + 6 * k, P.core, 0.7);
    }
    // ponto quente no alvo e marca no chao
    this.glow(c, x1, y1, 14 + 12 * k, P.glow, 0.7);
    this.glow(c, x1, y1, 7 + 5 * k, P.core, 0.85);
    c.save();
    c.translate(e.x, e.y + 2); c.scale(1, U.YS * 0.8);
    this.glow(c, 0, 0, 18 + 18 * k, P.deep, 0.5 + 0.3 * k);
    c.restore();
    // lente
    this.star(c, x0, y0, 16 + 18 * k, t * 0.7, P.mid, 0.6);
    c.restore();
    const n = this.rate(tw, 14 + 36 * k);
    for (let i = 0; i < n; i++) this.emit(x1 + U.rand(-6, 6), y1 + U.rand(-4, 4), U.rand(-40, 40), U.rand(-90, -20), U.rand(0.3, 0.6), U.rand(1, 2), i % 2 ? P.mid : P.glow, { kind: 'spark', grav: 140, drag: 0.2 });
    Light.add(x1, e.y - 4, 85 + 60 * k, P.glow, 0.5 + 0.4 * k, 0.3);
    Light.add(x0 + dx * 0.5, y0 + dy * 0.5 + 24, 70, P.glow, 0.25 + 0.2 * k);
  },

  // Clarao do Obelisco Solar
  flash(c, f, g) {
    if (ladoR()) return this.flashBeer(c, f, g);
    const k = f.t / f.T, a = 1 - k;
    const P = MAGIC.sun;
    c.save();
    c.globalCompositeOperation = 'lighter';
    this.glow(c, f.x, f.y - 10, f.r * (0.6 + k * 0.7), P.mid, a);
    c.translate(f.x, f.y - 10);
    c.rotate(k * 0.5);
    c.fillStyle = rgbaOf(P.core, 0.55 * a);
    for (let i = 0; i < 12; i++) {
      c.rotate(U.TAU / 12);
      const L = f.r * (0.5 + 0.9 * U.easeOutCubic(k)) * (i % 2 ? 0.7 : 1);
      c.beginPath(); c.moveTo(-3, 0); c.lineTo(0, -L); c.lineTo(3, 0); c.closePath(); c.fill();
    }
    c.restore();
    Light.add(f.x, f.y, f.r * 3.2, P.glow, 1.6 * a, 0.7);
  },
};

// ------------------------------------------------------------ ASSINATURAS DOS PERSONAGENS
// Cada caricatura carrega um toque proprio enquanto anda: poucas particulas pequenas presas ao adereco dela
// (celular, microfone, balao, megafone, caixas, moto...). Satira pelo objeto, nunca pela pessoa.
// B = corpo na tela: x, base (pe do sprite, ja com a altura do voo), h (altura do sprite), top, d (lado para onde
// olha), hx/hy (direcao do passo, para tras = -hx/-hy), mv (andando), s (raio do corpo). R = acumuladores de emissao
const SIG_COR = {
  notas: ['#8a5cf0', '#ff5fa2', '#2f8fe8', '#f0a020'],
  eua: ['#e0393a', '#ffffff', '#3256c8'],
  br: ['#2fa84f', '#ffd21f', '#2453c4'],
  festa: ['#e0393a', '#ffd21f', '#ffffff', '#ff7fb6', '#3aa0ff'],
  arco: ['#e0393a', '#ff9a2a', '#ffd21f', '#3fbf5f', '#3a8cff', '#9a5cf0'],
  ita: ['#2f9a4a', '#ffffff', '#d8433b'],
  capim: ['#6aa84f', '#9ccc65'],
};
const sigPick = arr => arr[(Math.random() * arr.length) | 0];
// onde fica o adereco em cada vista da folha (r leste, e sudeste, d frente, q nordeste, u costas), medido nos
// quadros sem espelho: [x, y] em fracoes da altura do sprite (x > 0 = direita da folha, y a partir do topo).
// Na tela o x vira pelo lado para onde o boneco olha (a folha e espelhada quando ele anda para a esquerda).
// Medido nas folhas de 22/10/2026: se o modelo do personagem mudar no Blender, conferir de novo.
const SIG_PROP = {
  nicolau: { r: [0.3, 0.18], e: [0.15, 0.35], d: [0, 0.4], q: [0.25, 0.05], u: [0, 0.05] },              // celular da selfie
  gleice: { r: [0.4, 0.4, 0], e: [0.3, 0.6, 0.5], d: [0.1, 0.66, 1.4], q: [0.32, 0.15, -0.5], u: [0.1, 0.3, -1.2] },   // boca do megafone e direcao
  michele: { r: [0.25, 0.4], e: [0.05, 0.45], d: [-0.1, 0.45], q: [0.2, 0.35], u: [0, 0.2] },             // microfone
  ze: { r: [0.4, 0.3], e: [0.25, 0.4], d: [0.15, 0.52], q: [0.2, 0.3], u: [0.2, 0.3] },                   // punho erguido
  pelego: { r: [0.12, 0.6], e: [0, 0.58], d: [0, 0.62], q: [0.1, 0.6], u: [0, 0.6] },                     // boca (apito), embaixo da faixa
  mortadela: { r: [0.15, 0.55], e: [0.25, 0.5], d: [0.1, 0.55], q: [0.15, 0.5], u: [-0.2, 0.5] },        // sanduiche
  rolo: { r: [0.15, 0.55], e: [-0.35, 0.45], d: [-0.3, 0.35], q: [0.05, 0.6], u: [0.3, 0.35] },           // rolo de tinta da Damaris
  balde: { r: [0.1, 0.7], e: [0.25, 0.75], d: [0.3, 0.8], q: [0.05, 0.7], u: [-0.25, 0.65] },             // balde de tinta
  carluxo: { r: [0.3, 0.55], e: [0.25, 0.6], d: [0.1, 0.7], q: [0.3, 0.45], u: [0, 0.4] },                // notebook
  zeroum_chefe: { r: [-0.15, 0.4], e: [-0.1, 0.3], d: [-0.2, 0.3], q: [-0.05, 0.4], u: [0.15, 0.35] },   // celular no ouvido
  lulinha: { r: [0.15, 0.95], e: [-0.15, 0.95], d: [-0.25, 0.95], q: [0.15, 0.95], u: [0.35, 0.9] },     // bola
  chuchu: { r: [0.3, 0.45], e: [0.3, 0.5], d: [0.15, 0.65], q: [0.2, 0.55], u: [-0.25, 0.4] },            // chuchu na mao
  lyra: { r: [0.15, 0.6], e: [0.05, 0.6], d: [-0.05, 0.55], q: [0.15, 0.6], u: [0, 0.55] },               // envelope
  psiu: { r: [0.15, 0.45], e: [0, 0.42], d: [-0.05, 0.42], q: [0.1, 0.4], u: [0, 0.3] },                  // mao no queixo, "psiu"
  maleta: { r: [-0.1, 0.6], e: [0.25, 0.6], d: [0.35, 0.7], q: [-0.3, 0.55], u: [-0.35, 0.6] },          // maleta do Cacique
  taxad: { r: [-0.45, 0.1], e: [-0.05, 0.05], d: [0.2, 0.05], q: [-0.45, 0.3], u: [-0.1, 0.35] },         // cabeca do homem (o leao vai na frente)
  veio: { r: [0.33, 0.8], e: [0.15, 0.82], d: [-0.38, 0.85], q: [0.45, 0.68], u: [0.3, 0.58] },          // tocha da estatua (montaria)
  caixas: { r: [0.2, 0.28], e: [-0.2, 0.38], d: [-0.12, 0.42], q: [0.12, 0.18], u: [0.1, 0.18] },         // caixas de som do trio eletrico
};
const SIG = {
  // ---- turma verde-amarela (aparece jogando com a Chapa Vermelha)
  // Patriota do Pneu: poeirinha do pneu rolando
  pneu(V, e, B, R) {
    if (B.mv && V.rate(R[0], 1.2)) V.sigDust(B, 5, 2.4, '#e4ddd2');
  },
  // Motociata: fumacinha do escapamento
  motociata(V, e, B, R) {
    if (B.mv) for (let n = V.rate(R[0], 6); n > 0; n--) V.sigExhaust(B, 14, 5, 2.4);
  },
  // Nicolau Selfie: o flash da camera dele piscando
  nicolau(V, e, B, R, t, c) {
    const ph = (t * 0.7 + e.id * 0.37) % 1;
    if (ph > 0.14) return;
    const k = ph / 0.14, a = 1 - k;
    V.prop(B, SIG_PROP.nicolau);
    const x = B.px, y = B.py;
    c.save();
    c.globalCompositeOperation = 'lighter';
    V.glow(c, x, y, 10, '#ffffff', 0.85 * a);
    c.fillStyle = rgbaOf('#ffffff', a);
    brilho4(c, x, y, 3 + 7 * U.easeOutCubic(k), 0.16);
    c.restore();
    if (k < 0.3) Light.add(x, y + 10, 46, '#ffffff', 0.6 * a);
  },
  // General Logistica: de vez em quando uma caixa cai da pilha, quica e fica para tras
  general(V, e, B, R) {
    if (!B.mv || !V.rate(R[0], 0.45)) return;
    V.emit(B.x - B.hx * 3 + U.rand(-3, 3), B.top + B.h * 0.18, -B.hx * U.rand(18, 32) + U.rand(-6, 6), U.rand(-60, -40), 1.7, U.rand(2.2, 2.7), '#c99a5e',
      { kind: 'box', grav: 280, drag: 0.6, rot: U.rand(-0.4, 0.4), spin: U.rand(-7, 7), floor: B.base + U.rand(-1, 3), bounce: 0.35 });
  },
  // Michele: notas musicais saindo do microfone
  michele(V, e, B, R) {
    if (!V.rate(R[0], 1.3)) return;
    V.prop(B, SIG_PROP.michele);
    V.emit(B.px + U.rand(-2, 2), B.py - 2, B.d * U.rand(6, 14), U.rand(-26, -16), 1.6, U.rand(2.4, 3), sigPick(SIG_COR.notas), { kind: 'note', drag: 0.7, rot: U.rand(-0.25, 0.25) });
  },
  // Dudu: confete de listras e estrelas caindo do balao
  dudu(V, e, B, R) {
    for (let n = V.rate(R[0], 3); n > 0; n--) {
      const st = Math.random() < 0.25;
      V.emit(B.x + U.rand(-7, 7), B.top + B.h * 0.42, U.rand(-8, 8), U.rand(0, 10), 1.5, st ? 1.7 : U.rand(1.3, 1.7), st ? '#ffffff' : sigPick(SIG_COR.eua),
        { kind: st ? 'star5' : 'conf', grav: 34, drag: 0.35, rot: U.rand(0, 3), spin: U.rand(-4, 4) });
    }
  },
  // Zambela Fujona: papeis e etiquetas de mala (verde, branco e vermelho) voando para tras, poeira da corrida
  zambela(V, e, B, R) {
    if (V.rate(R[0], 1.2)) {
      const tag = Math.random() < 0.4;
      V.emit(B.x - B.hx * 6 + U.rand(-3, 3), B.top + B.h * U.rand(0.35, 0.6), -B.hx * U.rand(16, 28), U.rand(-22, -6), 1.4, tag ? 1.7 : U.rand(1.7, 2.1), tag ? SIG_COR.ita : '#f6f1e4',
        { kind: tag ? 'flag3' : 'paper', grav: 18, drag: 0.45, rot: U.rand(-1, 1), spin: U.rand(-5, 5) });
    }
    if (B.mv && V.rate(R[1], 1.4)) V.sigDust(B, 4, 2.2);
  },
  // Passador de Boiada: poeira atras da boiada e capim chutado pelos cascos
  boiada(V, e, B, R) {
    if (!B.mv) return;
    for (let n = V.rate(R[0], 4); n > 0; n--) V.sigDust(B, B.s * 2.1, U.rand(2.8, 3.8));
    for (let n = V.rate(R[1], 2.2); n > 0; n--) {
      V.emit(B.x + B.hx * B.s * 0.8 + U.rand(-6, 6), B.base - 1, -B.hx * U.rand(10, 30), U.rand(-55, -30), 0.9, U.rand(1.1, 1.5), sigPick(SIG_COR.capim),
        { kind: 'leaf', grav: 220, drag: 0.5, rot: U.rand(0, 3), spin: U.rand(-9, 9), floor: B.base + U.rand(0, 3) });
    }
  },
  // Damaris: pingos de tinta (rosa do rolo, azul do balde) que ficam na estrada
  damaris(V, e, B, R) {
    if (!V.rate(R[0], 1.6)) return;
    const rosa = (R[1].k = !R[1].k);
    V.prop(B, rosa ? SIG_PROP.rolo : SIG_PROP.balde);
    V.emit(B.px + U.rand(-1.5, 1.5), B.py, B.d * U.rand(-3, 3), U.rand(-10, 0), 2.2, U.rand(2.2, 2.8), rosa ? '#ff6fb1' : '#4f9cff',
      { kind: 'drip', grav: 300, drag: 0.4, floor: B.base + U.rand(-2, 2) });
  },
  // Carluxo: balaozinho de "digitando..." saindo do notebook
  carluxo(V, e, B, R, t, c) {
    const ph = (t * 0.3 + e.id * 0.23) % 1;
    if (ph > 0.55) return;
    const k = ph / 0.55;
    const pop = U.easeOutBack(Math.min(1, k * 7)) * (k > 0.85 ? (1 - k) / 0.15 : 1);
    V.prop(B, SIG_PROP.carluxo);
    // ao lado da cabeca, do lado do notebook (acima dela fica a barra de vida)
    V.sigBubble(c, B.px + B.d * 7, B.top + B.h * 0.14 - k * 3, 10, 6.4, '#ffffff', '#3a7bd5', t, pop, B.d);
  },
  // Robo de Zap (a cabeca ja e um balao): de vez em quando dispara um balaozinho verde de mensagem
  robo(V, e, B, R) {
    if (!V.rate(R[0], 0.7)) return;
    V.emit(B.x + U.rand(-3, 3), B.top + B.h * 0.2, U.rand(-14, 14), U.rand(-34, -22), 1.1, U.rand(1.9, 2.3), '#4fd27a', { kind: 'chat', drag: 0.5, rot: U.rand(-0.3, 0.3) });
  },
  // Valdomar do Partidao: bandeirinhas coloridas saindo da mochila
  valdomar(V, e, B, R) {
    if (!V.rate(R[0], 1.6)) return;
    V.emit(B.x - B.hx * 8 + U.rand(-5, 5), B.top + B.h * 0.12, -B.hx * U.rand(8, 18) + U.rand(-6, 6), U.rand(-26, -12), 1.5, U.rand(1.8, 2.2), sigPick(SIG_COR.festa),
      { kind: 'pennant', grav: 22, drag: 0.5, rot: U.rand(-1, 1), spin: U.rand(-3, 3) });
  },
  // Veio da Estatua: a tocha da estatua soltando faiscas de ouro
  veio(V, e, B, R, t, c) {
    V.prop(B, SIG_PROP.veio);
    const x = B.px, y = B.py - 2;
    c.save();
    c.globalCompositeOperation = 'lighter';
    V.glow(c, x, y, 9, '#ffc53a', 0.45 + 0.15 * Math.sin(t * 9 + e.id));
    c.restore();
    for (let n = V.rate(R[0], 4); n > 0; n--) V.emit(x + U.rand(-2, 2), y + U.rand(-1, 2), U.rand(-8, 8), U.rand(-30, -14), U.rand(0.4, 0.8), U.rand(0.9, 1.5), Math.random() < 0.5 ? '#ffe7a0' : '#ffc53a', { drag: 0.5 });
    if (V.rate(R[1], 1.6)) V.emit(x + U.rand(-4, 4), y + U.rand(-4, 2), 0, U.rand(-12, -4), 0.5, U.rand(2.4, 3.2), '#ffffff', { kind: 'glint', drag: 0.4 });
    Light.add(x, y + 14, 48, '#ffc53a', 0.35);
  },
  // Capitao na Motociata: fumaca do escapamento e confete verde e amarelo
  capitao_moto(V, e, B, R) {
    if (B.mv) for (let n = V.rate(R[0], 7); n > 0; n--) V.sigExhaust(B, B.s * 1.1, 9, 3.6);
    for (let n = V.rate(R[1], 3); n > 0; n--) {
      V.emit(B.x + U.rand(-14, 14), B.top + B.h * 0.2, U.rand(-14, 14) - B.hx * 10, U.rand(-30, -14), 1.5, U.rand(1.5, 2), sigPick(SIG_COR.br),
        { kind: 'conf', grav: 30, drag: 0.4, rot: U.rand(0, 3), spin: U.rand(-5, 5) });
    }
  },
  // Zero-Um: ondinhas do celular no ouvido e estrelinhas verdes e amarelas
  zeroum_chefe(V, e, B, R, t, c) {
    V.prop(B, SIG_PROP.zeroum_chefe);
    V.sigWaves(c, B.px, B.py - 2, -Math.PI / 2, t * 1.2 + e.id * 0.2, 0.6, 3, 11, 2);
    for (let n = V.rate(R[0], 2.2); n > 0; n--) V.sigEdgeStar(B, Math.random() < 0.5 ? '#2fa84f' : '#ffd21f');
  },

  // ---- turma vermelha (aparece jogando com a Chapa Verde-Amarela)
  // Militante da Mortadela: farelo do sanduiche
  mortadela(V, e, B, R) {
    if (!V.rate(R[0], 1.6)) return;
    V.prop(B, SIG_PROP.mortadela);
    V.emit(B.px + U.rand(-2, 2), B.py, B.d * U.rand(-6, 10), U.rand(-25, -5), 1.3, U.rand(1.5, 1.9), Math.random() < 0.55 ? '#f6d698' : '#f59cab',
      { kind: 'crumb', grav: 260, drag: 0.5, rot: U.rand(0, 1.5), spin: U.rand(-8, 8), floor: B.base + U.rand(-1, 2), bounce: 0.3 });
  },
  // Bonde da Rouanet: confete colorido e notinhas de quem vai para o palco
  rouanet(V, e, B, R) {
    if (!V.rate(R[0], 1.6)) return;
    const nt = Math.random() < 0.35;
    V.emit(B.x - B.hx * 6 + U.rand(-5, 5), B.top + B.h * 0.25, -B.hx * U.rand(8, 16), U.rand(-26, -12), 1.3, nt ? U.rand(1.8, 2.2) : U.rand(1.3, 1.7), sigPick(nt ? SIG_COR.notas : SIG_COR.arco),
      nt ? { kind: 'note', drag: 0.7 } : { kind: 'conf', grav: 26, drag: 0.4, rot: U.rand(0, 3), spin: U.rand(-5, 5) });
  },
  // Gleice Megafone: ondas de som saindo do megafone
  gleice(V, e, B, R, t, c) {
    V.prop(B, SIG_PROP.gleice);
    V.sigWaves(c, B.px + Math.cos(B.pa) * 2, B.py + Math.sin(B.pa) * 2, B.pa, t * 1.4 + e.id * 0.17, 0.6, 3, 14, 3);
  },
  // Ze Guerreiro: o punho erguido solta um "pow" de risquinhos vermelhos
  ze(V, e, B, R, t, c) {
    const ph = (t * 0.6 + e.id * 0.29) % 1;
    if (ph > 0.24) return;
    const k = ph / 0.24;
    V.prop(B, SIG_PROP.ze);
    const x = B.px, y = B.py;
    const r0 = 2.5 + 3 * k, r1 = 5 + 8 * U.easeOutCubic(k);
    c.save();
    c.lineCap = 'round';
    c.globalAlpha = 1 - k;
    c.beginPath();
    for (let i = 0; i < 7; i++) {
      const an = -Math.PI / 2 + (i - 3) * 0.42;
      c.moveTo(x + Math.cos(an) * r0, y + Math.sin(an) * r0); c.lineTo(x + Math.cos(an) * r1, y + Math.sin(an) * r1);
    }
    c.strokeStyle = '#c81f24'; c.lineWidth = 2.1; c.stroke();
    c.strokeStyle = '#ffe2da'; c.lineWidth = 0.8; c.stroke();
    c.restore();
  },
  // Doutor Chuchu: folhinhas de chuchu e um brilho no estetoscopio
  chuchu(V, e, B, R) {
    if (V.rate(R[0], 1)) {
      V.prop(B, SIG_PROP.chuchu);
      V.emit(B.px + U.rand(-2, 2), B.py + 3, B.d * U.rand(2, 8) - B.hx * 6, U.rand(0, 8), 1.1, U.rand(1.6, 2), Math.random() < 0.5 ? '#9bd36a' : '#6fb848',
        { kind: 'leaf', grav: 55, drag: 0.5, rot: U.rand(0, 3), spin: U.rand(-3, 3), floor: B.base + U.rand(-1, 3) });
    }
    if (V.rate(R[1], 0.6)) V.emit(B.x + U.rand(-3, 3), B.top + B.h * 0.42, 0, -6, 0.55, U.rand(2.6, 3.4), '#ffffff', { kind: 'glint', drag: 0.4 });
  },
  // Ministro do Jatinho: rastro fino de condensacao (duas linhas)
  jatinho(V, e, B, R) {
    for (let n = V.rate(R[0], 30); n > 0; n--) {
      const o = (R[1].k = -(R[1].k || 1)) * 1.7;
      V.emit(B.x - B.hx * 15 - B.hy * o, B.top + B.h * 0.55 - B.hy * 15 + B.hx * o, -B.hx * 4, 0, 0.8, 1.3, '#ffffff', { kind: 'smoke', drag: 0.5 });
    }
  },
  // Dilmae Pedalada: redemoinhos de vento atras da bicicleta
  dilmae(V, e, B, R) {
    if (!B.mv || !V.rate(R[0], 2)) return;
    V.emit(B.x - B.hx * 12 + U.rand(-2, 2), B.base - U.rand(4, 10), -B.hx * U.rand(10, 18), U.rand(-8, -2), 0.9, U.rand(2.2, 2.8), '#8cc4ff',
      { kind: 'swirl', drag: 0.5, rot: U.rand(0, 6), spin: B.hx > 0 ? -5 : 5 });
  },
  // Taxad: sinais de porcentagem subindo e brilho de moeda (o homem vem atras do leao)
  taxad(V, e, B, R) {
    V.prop(B, SIG_PROP.taxad);
    if (V.rate(R[0], 0.8)) V.emit(B.px + U.rand(-3, 3), B.py - 3, U.rand(-4, 4), U.rand(-20, -14), 1.5, U.rand(2.4, 2.8), '#f5c542', { kind: 'pct', drag: 0.7, rot: U.rand(-0.2, 0.2) });
    if (V.rate(R[1], 1.4)) V.emit(B.px + U.rand(-8, 8), B.py + B.h * U.rand(0.1, 0.4), 0, U.rand(-10, -4), 0.5, U.rand(2.4, 3.2), '#ffe7a0', { kind: 'glint', drag: 0.4 });
  },
  // Pelego da Greve: o apito soltando risquinhos de som dos dois lados da cabeca (embaixo da faixa)
  pelego(V, e, B, R, t, c) {
    const ph = (t * 0.9 + e.id * 0.31) % 1;
    if (ph > 0.3) return;
    const k = ph / 0.3;
    V.prop(B, SIG_PROP.pelego);
    const x = B.px, y = B.py;
    const r0 = B.h * 0.17 + 1.5 * k, r1 = B.h * 0.2 + 4 + 5 * k;
    c.save();
    c.lineCap = 'round';
    c.globalAlpha = 1 - k;
    c.beginPath();
    for (let i = 0; i < 6; i++) {
      const an = (i < 3 ? 0 : Math.PI) + ((i % 3) - 1) * 0.42 * (i < 3 ? 1 : -1) - 0.25 * (i < 3 ? 1 : -1);
      c.moveTo(x + Math.cos(an) * r0, y + Math.sin(an) * r0); c.lineTo(x + Math.cos(an) * r1, y + Math.sin(an) * r1);
    }
    c.strokeStyle = 'rgba(60,30,30,0.55)'; c.lineWidth = 2.2; c.stroke();
    c.strokeStyle = '#ffffff'; c.lineWidth = 1; c.stroke();
    c.restore();
  },
  // Busao da Caravana: poeira e fumaca para tras
  busao(V, e, B, R) {
    if (!B.mv) return;
    for (let n = V.rate(R[0], 4); n > 0; n--) V.sigDust(B, B.s * 2, U.rand(3, 4));
    if (V.rate(R[1], 2)) V.sigExhaust(B, B.s * 2.2, 4, 2.6);
  },
  // Militante de Excursao: so uma poeirinha (anda em bando)
  excursao(V, e, B, R) {
    if (B.mv && V.rate(R[0], 0.8)) V.sigDust(B, 3, 1.8);
  },
  // Lulinha Ronaldinho: capim chutado pela bola e um brilho nela
  lulinha(V, e, B, R) {
    V.prop(B, SIG_PROP.lulinha);
    const bx = B.px, by = B.py - 2;
    if (B.mv && V.rate(R[0], 1.5)) {
      V.emit(bx + U.rand(-2, 2), by, -B.hx * U.rand(5, 20), U.rand(-45, -25), 0.8, U.rand(1, 1.3), sigPick(SIG_COR.capim),
        { kind: 'leaf', grav: 220, drag: 0.5, rot: U.rand(0, 3), spin: U.rand(-9, 9), floor: B.base + 1 });
    }
    if (V.rate(R[1], 0.7)) V.emit(bx, by - 2, 0, -8, 0.5, 2.8, '#ffffff', { kind: 'glint', drag: 0.4 });
  },
  // Pomba do Foro: penas vermelhas caindo em zigue-zague
  pomba(V, e, B, R) {
    if (!V.rate(R[0], 1.1)) return;
    V.emit(B.x + U.rand(-6, 6), B.top + B.h * 0.55, U.rand(-8, 8) - B.hx * 8, U.rand(-4, 6), 1.8, U.rand(2.8, 3.4), Math.random() < 0.6 ? '#e2483c' : '#f39088',
      { kind: 'feather', grav: 16, drag: 0.4, rot: U.rand(-0.6, 0.6) });
  },
  // Janjinha no Trio Eletrico: notas e confete saindo das caixas de som
  janja_trio(V, e, B, R) {
    V.prop(B, SIG_PROP.caixas);
    for (let n = V.rate(R[0], 2.2); n > 0; n--) {
      V.emit(B.px + U.rand(-B.h * 0.08, B.h * 0.08), B.py, U.rand(-12, 12) - B.d * 6, U.rand(-30, -18), 1.6, U.rand(2.4, 3), sigPick(SIG_COR.notas), { kind: 'note', drag: 0.7, rot: U.rand(-0.25, 0.25) });
    }
    for (let n = V.rate(R[1], 5); n > 0; n--) {
      V.emit(B.px + U.rand(-B.h * 0.15, B.h * 0.15), B.py - 4, U.rand(-25, 25), U.rand(-55, -30), 1.6, U.rand(1.4, 1.9), sigPick(SIG_COR.festa),
        { kind: 'conf', grav: 60, drag: 0.5, rot: U.rand(0, 3), spin: U.rand(-6, 6) });
    }
  },
  // Lulala: estrelinhas vermelhas (e uma branca ou outra) subindo
  lulala_chefe(V, e, B, R) {
    for (let n = V.rate(R[0], 2.2); n > 0; n--) V.sigEdgeStar(B, Math.random() < 0.75 ? '#e8352f' : '#ffffff');
  },

  // ---- Centrao (o mesmo nos dois lados)
  // Lyra Secreto (so quando revelado): envelopes lacrados escapando da mao e um sopro de "psiu"
  lyra(V, e, B, R) {
    if (V.rate(R[0], 0.7)) {
      V.prop(B, SIG_PROP.lyra);
      V.emit(B.px, B.py, B.d * U.rand(14, 26), U.rand(-40, -25), 1.4, U.rand(2, 2.4), '#dcbb86',
        { kind: 'env', grav: 130, drag: 0.5, rot: U.rand(-0.5, 0.5), spin: U.rand(-6, 6), floor: B.base + U.rand(0, 3) });
    }
    if (V.rate(R[1], 0.5)) {
      V.prop(B, SIG_PROP.psiu);
      V.emit(B.px + B.d * 2, B.py, B.d * 10, -4, 0.8, 2, '#eef0f4', { kind: 'smoke', drag: 0.4 });
    }
  },
  // O Centrao: brilho nas maletas e moeda caindo
  centrao(V, e, B, R) {
    if (V.rate(R[0], 2)) V.emit(B.x + U.rand(-B.h * 0.45, B.h * 0.45), B.base - B.h * U.rand(0.15, 0.4), 0, U.rand(-10, -4), 0.55, U.rand(2.6, 3.6), '#fff1b0', { kind: 'glint', drag: 0.4 });
    if (V.rate(R[1], 0.8)) {
      V.emit(B.x + U.rand(-B.h * 0.4, B.h * 0.4), B.base - B.h * 0.3, U.rand(-20, 20), U.rand(-50, -30), 1.3, U.rand(2.2, 2.6), '#ffd23f',
        { kind: 'coin', grav: 300, drag: 0.5, floor: B.base + U.rand(-2, 4), bounce: 0.4 });
    }
  },
  // Cacique do Centrao: moedas escapando da maleta
  cacique(V, e, B, R) {
    V.prop(B, SIG_PROP.maleta);
    const mx = B.px, my = B.py;
    if (V.rate(R[0], 1)) {
      V.emit(mx + U.rand(-3, 3), my, -B.d * U.rand(5, 20), U.rand(-45, -25), 1.3, U.rand(2.2, 2.6), '#ffd23f',
        { kind: 'coin', grav: 300, drag: 0.5, floor: B.base + U.rand(-2, 4), bounce: 0.4 });
    }
    if (V.rate(R[1], 1)) V.emit(mx + U.rand(-4, 4), my + U.rand(-4, 4), 0, -6, 0.5, U.rand(2.8, 3.6), '#fff1b0', { kind: 'glint', drag: 0.4 });
  },
  // Fundao Eleitoral: a chuva de dinheiro esta no enemyExtra; aqui so os brilhinhos
  fundao(V, e, B, R) {
    if (V.rate(R[0], 4)) V.emit(B.x + U.rand(-24, 24), B.top + B.h * U.rand(0.2, 0.8), 0, U.rand(-10, 4), U.rand(0.4, 0.6), U.rand(2.6, 3.6), '#ffffff', { kind: 'glint', drag: 0.3 });
  },
};

Object.assign(Vfx, {
  // geometria do corpo do inimigo na tela (um objeto so, reaproveitado)
  bodyOf(e, g, t) {
    const B = this._B || (this._B = { x: 0, base: 0, h: 0, top: 0, d: 1, hx: 1, hy: 0, mv: true, s: 10, v: 'r', px: 0, py: 0, pa: 0 });
    const T = e.T;
    let base = e.y, lift = 0;
    if (T.flying && !e.flying && e.type !== 'ifrit') base += FLY_H - 8;
    const fl = typeof ESPR_FLY !== 'undefined' ? ESPR_FLY[e.type] : null;
    if (fl) {
      const low = e.type === 'ifrit' && !e.flying;
      lift = low ? 10 : FLY_H + fl[0];
      base += (low ? -10 : -FLY_H - fl[0]) + Math.sin(t * fl[1] + e.id) * fl[2];
    }
    const top = A.enemyTop ? A.enemyTop(e) : null;
    B.h = top != null ? Math.max(12, top - lift) : T.size * 2.4;
    B.x = e.x; B.base = base; B.top = base - B.h;
    B.d = e.facing < 0 ? -1 : 1;
    const hl = Math.hypot(e.hdx || 0, e.hdy || 0);
    B.hx = hl > 0.05 ? e.hdx / hl : B.d; B.hy = hl > 0.05 ? e.hdy / hl : 0;
    B.mv = e.moving !== false;
    B.s = T.size;
    // vista da folha em uso (parado ou atacando ele fica de lado)
    B.v = !B.mv || e.atkAnim > 0 || e.castAnim > 0 ? 'r' : e._vw || 'r';
    return B;
  },

  // posicao do adereco na tela (B.px, B.py) e, se a tabela tiver, a direcao dele (B.pa)
  prop(B, tab) {
    const p = tab[B.v] || tab.r;
    B.px = B.x + B.d * p[0] * B.h;
    B.py = B.top + p[1] * B.h;
    if (p.length > 2) B.pa = B.d > 0 ? p[2] : Math.PI - p[2];
    return B;
  },

  // assinatura do personagem (chamada logo depois do sprite dele)
  sig(c, e, g, t) {
    if (e.dead || e.reached || e.burrowed || e.untargetable || (e.T.stealth && !e.revealed)) return;
    const fn = typeof ESPR !== 'undefined' && SIG[ESPR.key(e.type)];
    if (!fn) return;
    const R = e._sg || (e._sg = [{}, {}]);
    fn(this, e, this.bodyOf(e, g, t), R, t, c);
  },

  // poeira clarinha dos pes (ou das rodas), para tras do passo
  sigDust(B, back, s, col) {
    this.emit(B.x - B.hx * back + U.rand(-3, 3), B.base - 1 - B.hy * back + U.rand(-1.5, 1.5), -B.hx * U.rand(6, 16) + U.rand(-4, 4), U.rand(-12, -4), U.rand(0.55, 0.95), s * U.rand(1.05, 1.45), col || '#f1dfc2', { kind: 'smoke', drag: 0.5 });
  },

  // fumaca de escapamento: sai para tras, na altura do cano
  sigExhaust(B, back, up, s) {
    this.emit(B.x - B.hx * back + U.rand(-1.5, 1.5), B.base - up - B.hy * back, -B.hx * U.rand(14, 26) + U.rand(-4, 4), U.rand(-14, -6), U.rand(0.5, 0.8), s * U.rand(0.9, 1.3), Math.random() < 0.5 ? '#6f7680' : '#959ba3', { kind: 'smoke', drag: 0.4 });
  },

  // estrelinha subindo pelas bordas da silhueta (nunca por cima do rosto)
  sigEdgeStar(B, col) {
    const sd = Math.random() < 0.5 ? -1 : 1;
    this.emit(B.x + sd * B.h * U.rand(0.3, 0.42), B.top + B.h * U.rand(0.1, 0.55), sd * U.rand(2, 8), U.rand(-24, -12), 1.4, U.rand(2.2, 3), col,
      { kind: 'star5', drag: 0.6, rot: U.rand(-0.5, 0.5), spin: U.rand(-1.5, 1.5) });
  },

  // ondas de som: arcos que se abrem e somem saindo de (x, y) na direcao ang
  sigWaves(c, x, y, ang, ph, span, r0, r1, n) {
    c.save();
    c.lineCap = 'round';
    const a0 = ang - span;
    for (let i = 0; i < n; i++) {
      const q = (((ph + i / n) % 1) + 1) % 1;
      c.globalAlpha = Math.min(1, q * 5) * (1 - q);
      c.beginPath(); c.arc(x, y, r0 + q * (r1 - r0), a0, a0 + span * 2);
      c.strokeStyle = 'rgba(60,30,30,0.55)'; c.lineWidth = 2.4; c.stroke();
      c.strokeStyle = '#ffffff'; c.lineWidth = 1.1; c.stroke();
    }
    c.restore();
  },

  // balaozinho de conversa com os tres pontinhos de "digitando" pulando (sem letras)
  sigBubble(c, x, y, w, h, fill, dot, t, pop, d) {
    if (!(pop > 0.02)) return;
    c.save();
    c.translate(x, y);
    c.scale(pop * (d < 0 ? -1 : 1), pop);
    const OL = 'rgba(30,40,60,0.7)';
    A.poly(c, [[-w * 0.22, h / 2 - 0.6], [-w * 0.36, h / 2 + h * 0.5], [-w * 0.02, h / 2 - 0.6]], fill, OL, 0.8);
    A.rrect(c, -w / 2, -h / 2, w, h, h * 0.45, fill, OL, 0.8);
    c.fillStyle = dot;
    for (let i = 0; i < 3; i++) {
      const j = Math.max(0, Math.sin(t * 9 - i * 0.9)) * h * 0.18;
      c.beginPath(); c.arc((i - 1) * w * 0.25, -j, h * 0.13, 0, U.TAU); c.fill();
    }
    c.restore();
  },
});

// ------------------------------------------------------------ LUZ E PARTICULAS DAS OUTRAS TORRES, INIMIGOS E CENARIO
const FIRE = { core: '#fff2c0', mid: '#ffb347', glow: '#ff7a1a', deep: '#c0400a' };
const flick = (t, seed) => 0.82 + 0.1 * Math.sin(t * 13.1 + seed) + 0.08 * Math.sin(t * 29.7 + seed * 1.7);

Object.assign(Vfx, {
  // fontes fixas do cenario (fendas de lava do Trono do Ifrit)
  env(g, t) {
    // queimada (Coracao em Chamas): brasas subindo pela tela
    if (g.L && g.L.theme === 'ember') {
      const n = this.rate(this, 12);
      for (let i = 0; i < n; i++) this.emit(U.rand(0, W), U.rand(H * 0.4, H + 10), U.rand(-12, 18), U.rand(-60, -30), U.rand(2.2, 4), U.rand(1.2, 2.4), i % 3 ? FIRE.mid : FIRE.glow, { drag: 0.6 });
    }
    // fenda do tepui (cenario do Blender): a Fumaca Negra sai do chao com brasas, mais forte enquanto o Coracao bate
    const C = typeof SPRITE_META !== 'undefined' && SPRITE_META.cenario && SPRITE_META.cenario[g.levelIdx];
    if (C && C.fenda) {
      const [fx, fy] = C.fenda, boss = g.enemies.some(e => e.T.final);
      const n = this.rate(this._fenda || (this._fenda = {}), boss ? 16 : 7);
      for (let i = 0; i < n; i++) this.emit(fx + U.rand(-22, 22), fy + U.rand(-4, 6), U.rand(-10, 10), U.rand(-34, -16), U.rand(1.4, 2.4), U.rand(6, 11), i % 2 ? '#2a2422' : '#3c3431', { kind: 'smoke', drag: 0.4 });
      if (Math.random() < 0.3) this.emit(fx + U.rand(-16, 16), fy, U.rand(-14, 14), U.rand(-60, -30), U.rand(0.6, 1.2), U.rand(1, 1.8), '#ff8a3a', { drag: 0.2 });
    }
    const L = A.envLights && A.envLights[g.levelIdx];
    if (!L) return;
    for (let i = 0; i < L.length; i++) Light.add(L[i][0], L[i][1], L[i][3] || 75, L[i][2], 0.32 * flick(t, i * 3.1));
  },

  // torre comprada: moedas e notas girando num redemoinho que sobe em volta dela (as de tras menores e
  // apagadas, as da frente cheias), aura de ouro pulsando e uma moeda ou outra caindo e quicando no chao
  bought(c, tw, g, t, a) {
    const top = Math.min(90, g.towerTop(tw));
    const pul = 0.75 + 0.25 * Math.sin(t * 6 + tw.id);
    c.save();
    c.globalCompositeOperation = 'lighter';
    this.glow(c, tw.x, tw.y - top * 0.5, 50, '#ffc53a', 0.38 * a * pul);
    c.globalCompositeOperation = 'source-over';
    const m = c.getTransform();
    const q = this._q || (this._q = { t: 0, s: 0, c: '' });
    for (let pass = 0; pass < 2; pass++) {
      for (let i = 0; i < 10; i++) {
        const ang = t * (2.2 + (i % 3) * 0.35) + (i * U.TAU) / 10 + tw.id;
        const front = Math.sin(ang) > 0;
        if (front !== !!pass) continue;
        const h = (t * 0.32 + i * 0.1) % 1;
        const rx = 26 + 5 * Math.sin(i * 1.7) - h * 6;
        const px = tw.x + Math.cos(ang) * rx, py = tw.y - 4 - h * (top + 14) + Math.sin(ang) * rx * 0.34;
        c.globalAlpha = a * Math.min(1, h * 6, (1 - h) * 5) * (front ? 1 : 0.6);
        c.setTransform(m);
        c.translate(px, py);
        q.t = t + i * 0.37; q.s = front ? 3 : 2.4;
        if (i % 3 === 0) { c.rotate(Math.sin(t * 3 + i) * 0.6 + ang * 0.2); SOLID.bill(c, q); }
        else SOLID.coin(c, q);
      }
    }
    c.restore();
    const n = this.rate(tw, 3.5 * a);
    for (let i = 0; i < n; i++) {
      if (i % 2) this.emit(tw.x + U.rand(-24, 24), tw.y - U.rand(10, top), U.rand(-10, 10), U.rand(-20, -5), U.rand(0.4, 0.7), U.rand(2.4, 3.6), '#ffffff', { kind: 'glint', drag: 0.4 });
      else this.emit(tw.x + U.rand(-20, 20), tw.y - U.rand(top * 0.4, top), U.rand(-30, 30), U.rand(-60, -30), 1.3, U.rand(2.2, 2.8), '#ffd23f', { kind: 'coin', grav: 300, drag: 0.5, floor: tw.y + U.rand(2, 12), bounce: 0.4 });
    }
    Light.add(tw.x, tw.y - 20, 130, '#ffd54a', 0.6 * a * pul, 0.3);
  },

  // torres que nao sao de magia
  towerExtra(c, tw, g, t) {
    // lanternas dos sprites (o sprites.js deixa de desenhar o halo 2D quando a Light existe)
    const lan = A.spriteLanterns && A.spriteLanterns(tw);
    if (lan) {
      const night = typeof SPR !== 'undefined' && SPR ? Math.max(0.25, SPR.glow || 0) : 0.25;
      for (let i = 0; i < lan.length; i++) {
        const L = lan[i];
        Light.add(tw.x + L[0], tw.y + L[1] + 10, L[3] === 0 ? 40 : 60, L[2] || '#ffb25a', (0.25 + 0.6 * night) * flick(t, tw.id + i), L[3] === 0 ? 0 : 0.25 * night);
      }
    }
    // torre comprada pelo Fundao Eleitoral: redemoinho de moedas e notas em volta, brilho de ouro pulsando
    if (tw.fireT > 0) this.bought(c, tw, g, t, Math.min(1, tw.fireT / 0.6));
    if (tw.working || tw.disabledT > 0) return;
    // Bombarda: clarao e fumaca na boca do canhao a cada tiro
    if (tw.type === 'artillery' && tw.spec !== 'seismic') {
      const prev = tw._va || 0;
      tw._va = tw.anim;
      if (tw.anim > prev + 0.05) tw._mz = 0.16;
      if (tw._mz > 0) {
        tw._mz -= this.dt;
        const mp = A.spriteMuzzle && A.spriteMuzzle(tw);
        const mx = mp ? tw.x + mp[0] : tw.x, my = mp ? tw.y + mp[1] : tw.y - g.towerTop(tw);
        // Leite Condensado: a lata sai num sopro de vapor branco e respingos de leite, sem clarao de fogo
        const leite = ladoV();
        if (tw._mz > 0.14) {
          for (let i = 0; i < 7; i++) this.emit(mx + U.rand(-4, 4), my + U.rand(-3, 3), U.rand(-30, 30), U.rand(-55, -15), U.rand(0.7, 1.2), U.rand(5, 9), leite ? (i % 2 ? '#e8e2d8' : '#fbf8f2') : i % 2 ? '#8a8279' : '#b3aca2', { kind: 'smoke', drag: 0.25 });
          if (leite) for (let i = 0; i < 6; i++) this.emit(mx, my, U.rand(-60, 60), U.rand(-110, -40), U.rand(0.5, 0.8), U.rand(1.6, 2.4), i % 2 ? '#fffaf0' : '#f2e6c8', { kind: 'speck', grav: 380, drag: 0.3 });
          else this.burst(mx, my, 6, 120, FIRE.mid, { kind: 'spark', drag: 0.05, grav: 200 });
        }
        const k = Math.max(0, tw._mz / 0.16);
        c.save();
        c.globalCompositeOperation = 'lighter';
        this.glow(c, mx, my, 20 * k + 6, leite ? '#fff4dc' : FIRE.mid, leite ? 0.6 * k : k);
        c.restore();
        Light.add(mx, my + 30, 120, leite ? '#fff0d0' : FIRE.glow, (leite ? 0.6 : 1.1) * k, 0.4);
      }
    }
    // Estandarte: Tambores em guerra pulsam; o Farol da Vigilia gira um facho de luz
    if (tw.type === 'banner') {
      const top = g.towerTop(tw);
      if (tw.warT > 0) {
        const ph = (t * 1.6) % 1;
        c.save();
        c.globalAlpha = (1 - ph) * 0.8;
        A.ell(c, tw.x, tw.y + 2, 30 + ph * 70, (30 + ph * 70) * U.YS, null, '#ffcf5a', 3 * (1 - ph) + 0.5);
        c.restore();
        Light.add(tw.x, tw.y, 140, '#ffb347', 0.45 + 0.25 * Math.sin(t * 10), 0.2);
      }
      if (tw.spec === 'watch') {
        const lx = tw.x, ly = tw.y - top - 8;
        const ang = t * 1.4 + tw.id;
        const R = (tw.E || tw.S).range * 0.85;
        const sx = tw.x + Math.cos(ang) * R, sy = tw.y + Math.sin(ang) * R * U.YS;
        c.save();
        c.globalCompositeOperation = 'lighter';
        const w = 16;
        const gr = c.createLinearGradient(lx, ly, sx, sy);
        gr.addColorStop(0, 'rgba(255,244,200,0.5)');
        gr.addColorStop(1, 'rgba(255,244,200,0)');
        c.fillStyle = gr;
        const dx = sx - lx, dy = sy - ly, len = Math.hypot(dx, dy) || 1, nx = -dy / len, ny = dx / len;
        c.beginPath();
        c.moveTo(lx + nx * 2, ly + ny * 2); c.lineTo(sx + nx * w * 2, sy + ny * w); c.lineTo(sx - nx * w * 2, sy - ny * w); c.lineTo(lx - nx * 2, ly - ny * 2);
        c.closePath(); c.fill();
        if (ladoV()) this.ringLight(c, tw, lx, ly, t);   // Camera da Live: ring light e flash de foto
        else {
          this.glow(c, lx, ly, 18, '#fff4c8', 0.9);
          this.star(c, lx, ly, 14, t * 0.8, '#ffffff', 0.6);
        }
        c.restore();
        Light.add(lx, ly + 40, 110, '#fff0b0', 0.45, 0.4);
        Light.add(sx, sy, 70, '#fff0b0', 0.55);
      }
    }
    // Mercado: brilho de ouro discreto
    if (tw.type === 'market' && tw.spec === 'treasury') Light.add(tw.x, tw.y - 20, 70, '#ffd54a', 0.22 + 0.08 * Math.sin(t * 3 + tw.id));
  },

  // inimigos que brilham ou queimam
  enemyExtra(e, g, t) {
    const y = g.hitY(e);
    // satira: sem brasa nem fumaca de possessao nos adversarios
    if (e.burnT > 0) {
      const n = this.rate(e, 14);
      for (let i = 0; i < n; i++) this.emit(e.x + U.rand(-e.T.size, e.T.size), y + U.rand(-4, 6), U.rand(-10, 10), U.rand(-70, -30), U.rand(0.3, 0.6), U.rand(1.2, 2.4), i % 2 ? FIRE.mid : FIRE.glow, { drag: 0.4 });
      Light.add(e.x, e.y - 6, 60 + e.T.size * 2, FIRE.glow, 0.55 * flick(t, e.id), 0.2);
    }
    if (e.type === 'ifrit') {
      // Fundao Eleitoral: brilho dourado e dinheiro caindo por onde ele passa
      const fy = e.flying ? e.y - FLY_H - 30 : e.y - 40;
      Light.add(e.x, e.y - 10, 190, '#ffd54a', 0.6 * flick(t, e.id), 0.35);
      const n = this.rate(e, 9);
      for (let i = 0; i < n; i++) {
        const bill = Math.random() < 0.45;
        this.emit(e.x + U.rand(-30, 30), fy + U.rand(-20, 20), U.rand(-20, 20), U.rand(10, 40), U.rand(0.9, 1.4), bill ? U.rand(2.4, 3) : U.rand(2, 2.6), bill ? '#79c463' : '#ffd23f',
          { kind: bill ? 'bill' : 'coin', grav: bill ? 30 : 90, drag: 0.4, rot: U.rand(-0.6, 0.6), spin: bill ? U.rand(-3, 3) : 0 });
      }
    } else if (e.type === 'specter' && e.revealed) {
      Light.add(e.x, e.y - 10, 70, '#cfe8ff', 0.25);
    }
    if (e.frozenT > 0) Light.add(e.x, e.y - 6, 60, '#bff0ff', 0.4);
  },

  // projeteis com fogo ou pavio
  projExtra(p, g) {
    if ((p.kind === 'bomb' || p.kind === 'bomblet' || p.kind === 'barrel') && ladoV()) {
      // lata de leite condensado: pinguinhos de leite caindo (a da Calda Quente solta vapor)
      Light.add(p.x, p.y + 10, p.kind === 'bomblet' ? 36 : 54, p.kind === 'barrel' ? '#ffc070' : '#fff0d0', 0.25);
      const n = this.rate(p, p.kind === 'bomblet' ? 6 : 12);
      for (let i = 0; i < n; i++) {
        if (p.kind === 'barrel' && i % 2 === 0) this.emit(p.x + U.rand(-2, 2), p.y - 6, U.rand(-6, 6), U.rand(-26, -10), U.rand(0.5, 0.8), U.rand(2.5, 4), '#fbf6ee', { kind: 'smoke', drag: 0.4 });
        else this.emit(p.x + U.rand(-3, 3), p.y + U.rand(0, 4), U.rand(-8, 8), U.rand(0, 20), U.rand(0.35, 0.6), U.rand(0.9, 1.5), p.kind === 'barrel' ? '#e09a3a' : '#fffaf0', { kind: 'speck', grav: 200, drag: 0.3 });
      }
    } else if (p.kind === 'bomb' || p.kind === 'bomblet' || p.kind === 'barrel') {
      Light.add(p.x, p.y + 10, p.kind === 'bomblet' ? 40 : 60, FIRE.mid, 0.35);
      const n = this.rate(p, p.kind === 'bomblet' ? 10 : 22);
      for (let i = 0; i < n; i++) this.emit(p.x + U.rand(-2, 2), p.y + U.rand(-2, 2), U.rand(-8, 8), U.rand(-14, 2), U.rand(0.4, 0.8), U.rand(2.5, 4.5), '#a49c92', { kind: 'smoke', drag: 0.4 });
    } else if (p.kind === 'fireball' && p.t >= 0) {
      // saco de dinheiro do Fundao a caminho da torre: rastro de po de ouro, brilhinhos e uma moeda ou outra
      Light.add(p.x, p.y + 20, 120, '#ffd54a', 0.85, 0.35);
      const n = this.rate(p, 36);
      for (let i = 0; i < n; i++) {
        const r = i % 6;
        if (r === 0) this.emit(p.x + U.rand(-5, 5), p.y + U.rand(-5, 5), U.rand(-15, 15), U.rand(-20, 5), U.rand(0.35, 0.6), U.rand(2.6, 3.6), i % 12 ? '#ffffff' : '#ffe7a0', { kind: 'glint', drag: 0.3 });
        else if (r === 3) this.emit(p.x + U.rand(-4, 4), p.y + U.rand(-2, 4), U.rand(-25, 25), U.rand(-30, 0), U.rand(0.7, 1), U.rand(2, 2.6), '#ffd23f', { kind: 'coin', grav: 260, drag: 0.4 });
        else this.emit(p.x + U.rand(-5, 5), p.y + U.rand(-5, 5), U.rand(-25, 25), U.rand(-25, 10), U.rand(0.3, 0.6), U.rand(1, 2), i % 2 ? '#ffe7a0' : '#ffc53a', { drag: 0.2, grav: 40 });
      }
    } else if (p.kind === 'bolt' && p.exp) {
      Light.add(p.x, p.y + 10, 70, FIRE.mid, 0.5);
    }
  },

  // zonas no chao
  zoneExtra(z, g, t) {
    const k = z.t / z.T;
    const fade = Math.min(1, (1 - k) * 4, z.t * 4);
    if (z.kind === 'fire' && z.moto) {
      // Motociata: so fumaca de escapamento cinza-azulada subindo (sem chama nem luz de fogo)
      const n = this.rate(z, 7 * fade);
      for (let i = 0; i < n; i++) {
        const a = U.rand(0, U.TAU), d = Math.sqrt(Math.random()) * z.r * 0.8;
        this.emit(z.x + Math.cos(a) * d, z.y + Math.sin(a) * d * U.YS - 6, U.rand(-14, 14), U.rand(-26, -12), U.rand(1, 1.6), U.rand(5, 8), i % 2 ? '#8e9aae' : '#a9b3c4', { kind: 'smoke', drag: 0.5 });
      }
    } else if (z.kind === 'fire' && ladoV()) {
      // Calda Quente: so um calor ambar baixo e vapor branco subindo da calda
      Light.add(z.x, z.y - 6, z.r * 2.2, '#ffb050', 0.45 * fade, 0.2);
      const n = this.rate(z, 6 * fade);
      for (let i = 0; i < n; i++) {
        const a = U.rand(0, U.TAU), d = Math.sqrt(Math.random()) * z.r * 0.7;
        this.emit(z.x + Math.cos(a) * d, z.y + Math.sin(a) * d * U.YS - 6, U.rand(-8, 8), U.rand(-30, -16), U.rand(1, 1.6), U.rand(4, 7), i % 2 ? '#f6f2ea' : '#ffffff', { kind: 'smoke', drag: 0.5 });
      }
    } else if (z.kind === 'fire') {
      Light.add(z.x, z.y - 10, z.r * 2.6, FIRE.glow, 0.85 * fade * flick(t, z.x), 0.35);
      const n = this.rate(z, 22 * fade);
      for (let i = 0; i < n; i++) {
        const a = U.rand(0, U.TAU), d = Math.sqrt(Math.random()) * z.r * 0.9;
        this.emit(z.x + Math.cos(a) * d, z.y + Math.sin(a) * d * U.YS - 8, U.rand(-8, 8), U.rand(-80, -40), U.rand(0.4, 0.8), U.rand(1.2, 2.4), i % 2 ? FIRE.mid : FIRE.core, { drag: 0.4 });
      }
    } else if (z.kind === 'toxic') {
      // Chuva de Notas: brilho suave verde-dourado do dinheiro
      Light.add(z.x, z.y - 6, z.r * 2, ladoV() ? '#ffc070' : '#d4e07a', 0.3 * fade);   // V: Nuvem de Bagaco
    } else if (z.kind === 'tornado') {
      Light.add(z.x, z.y - 30, 90, ladoR() ? '#ffe6cc' : '#dcf8c6', 0.25 * fade);     // R: Discurso de 3 Horas
    }
  },

  // efeitos que ja tem desenho proprio no render.js: luz e particulas
  fxExtra(f, g) {
    const k = f.t / f.T, a = 1 - k;
    switch (f.kind) {
      case 'explosion': {
        if (ladoV()) {
          // Leite Condensado: respingos de leite (ou de calda) e vapor, luz quente e baixa
          if (!f._sp) {
            f._sp = 1;
            const r = f.r || 40;
            this.burst(f.x, f.y - 6, 8 + Math.round(r / 6), 120 + r * 1.6, f.fire ? '#ffd08a' : '#fff6e0', { kind: 'spark', drag: 0.05, grav: 420 });
            for (let i = 0; i < 4 + Math.round(r / 14); i++) this.emit(f.x + U.rand(-r * 0.4, r * 0.4), f.y - U.rand(0, 12), U.rand(-20, 20), U.rand(-40, -15), U.rand(0.8, 1.3), U.rand(r * 0.1, r * 0.18), i % 2 ? '#f4efe6' : '#ffffff', { kind: 'smoke', drag: 0.35 });
          }
          Light.add(f.x, f.y, (f.r || 40) * 2.8, f.fire ? '#ffb050' : '#ffe8b8', 0.9 * a * a, 0.4);
          break;
        }
        if (!f._sp) {
          f._sp = 1;
          const r = f.r || 40;
          this.burst(f.x, f.y - 6, 12 + Math.round(r / 5), 160 + r * 2.2, f.fire ? FIRE.glow : FIRE.mid, { kind: 'spark', drag: 0.05, grav: 420 });
          this.burst(f.x, f.y - 6, 8, 70, FIRE.core, { up: 60, life: 1.6, drag: 0.4 });
          for (let i = 0; i < 6 + Math.round(r / 10); i++) this.emit(f.x + U.rand(-r * 0.4, r * 0.4), f.y - U.rand(0, 16), U.rand(-25, 25), U.rand(-45, -15), U.rand(0.9, 1.6), U.rand(r * 0.12, r * 0.22), i % 2 ? '#6e655c' : '#948b80', { kind: 'smoke', drag: 0.35 });
        }
        Light.add(f.x, f.y, (f.r || 40) * 3.4, f.fire ? '#ff5a10' : FIRE.glow, 1.35 * a * a, 0.55);
        break;
      }
      case 'chasm': break; // Poco sem Fundo: oleo preto, sem brilho de lava
      // efeitos tematicos sem fogo (js/satira.js): brilhos claros, nada de luz laranja
      case 'shout': Light.add(f.x, f.y - 10, (f.r || 70) * 2.2, '#f2ff9a', 0.6 * a * a, 0.25); break;
      case 'lpop': Light.add(f.x, f.y, 70, '#fff0e8', 0.5 * a); break;
      case 'cash': {
        const suco = f.torre && ladoV();   // Suco Estourado do Laranjao
        if (!f._sp) {
          f._sp = 1;
          this.burst(f.x, f.y - 8, 10 + Math.round((f.r || 50) / 8), 150 + (f.r || 50) * 1.5, suco ? '#ffc060' : '#ffe08a', { kind: 'spark', drag: 0.05, grav: 320 });
        }
        Light.add(f.x, f.y, (f.r || 50) * 2.4, suco ? '#ffb84a' : '#ffd54a', 0.8 * a * a, 0.35);
        break;
      }
      case 'confetti':
        if (!f._sp) {
          f._sp = 1;
          this.burst(f.x, f.y - 30, 18, 260, '#fff2c0', { kind: 'spark', drag: 0.05, grav: 260 });
        }
        Light.add(f.x, f.y - 20, 260, '#fff2c0', 1.0 * a * a, 0.4);
        break;
      case 'court': Light.add(f.x, f.y - 20, 150, '#d8ccff', 0.5 * a, 0.25); break;
      case 'sabhit': if (f.skey !== 'pelego') Light.add(f.x, f.y, 60, '#ff9ac8', 0.35 * a); break;
      case 'poof':
        if (f.big && !f._sp) {
          f._sp = 1;
          for (let i = 0; i < 8; i++) this.emit(f.x + U.rand(-26, 26), f.y - U.rand(0, 12), U.rand(-30, 30), U.rand(-30, -10), U.rand(1, 1.6), U.rand(7, 11), i % 2 ? '#8e9aae' : '#a9b3c4', { kind: 'smoke', drag: 0.4 });
        }
        break;
      case 'smoke': if (f.fire) Light.add(f.x, f.y, 90, FIRE.glow, 0.45 * a); break;
      case 'enemyHeal': Light.add(f.x, f.y, (f.r || 60) * 1.8, '#b8ff5a', 0.55 * a, 0.2); break;
      case 'heal': Light.add(f.x, f.y, 90, '#9fffb0', 0.45 * a); break;
      case 'levelup': Light.add(f.x, f.y - 10, 160, '#ffe08a', 0.9 * a, 0.45); break;
      case 'sparkle': Light.add(f.x, f.y + 20, 100, '#fff2c0', 0.55 * a, 0.25); break;
      case 'coins': Light.add(f.x, f.y, 70, '#ffd54a', 0.4 * a); break;
      case 'geyser': Light.add(f.x, f.y, 100, '#bff0ff', 0.45 * a); break;
      // 'ice' acompanha o inimigo congelado (sem x/y proprios): a luz vem do enemyExtra (frozenT)
      case 'quake':
        if (!f._sp) {
          f._sp = 1;
          // Batedeira Industrial (V): nuvenzinha de farinha e acucar no lugar da poeira
          const cor = ladoV() ? '#f1ebe0' : '#b39570';
          for (let i = 0; i < 12; i++) {
            const an = (i / 12) * U.TAU;
            this.emit(f.x + Math.cos(an) * f.r * 0.5, f.y + Math.sin(an) * f.r * 0.5 * U.YS, Math.cos(an) * 60, U.rand(-30, -10), U.rand(0.8, 1.4), U.rand(8, 13), cor, { kind: 'smoke', drag: 0.3 });
          }
        }
        break;
      default: break;
    }
  },
});

// fumaca da queimada passando devagar (Coracao em Chamas)
Vfx.smoke = function (c, g, t) {
  if (!g.L || g.L.theme !== 'ember') return;
  const r = U.rng(31);
  c.save();
  for (let i = 0; i < 9; i++) {
    const rad = 160 + r() * 140;
    const x = ((r() * (W + 700) + t * (12 + r() * 14)) % (W + 700)) - 350;
    const y = ((r() * (H + 400) - t * (6 + r() * 6)) % (H + 400) + H + 400) % (H + 400) - 200;
    const gr = c.createRadialGradient(x, y, 0, x, y, rad);
    gr.addColorStop(0, 'rgba(48,40,38,0.2)'); gr.addColorStop(1, 'rgba(48,40,38,0)');
    c.fillStyle = gr; c.fillRect(x - rad, y - rad, rad * 2, rad * 2);
  }
  c.restore();
};

// ------------------------------------------------------------ EFEITOS POR CHAPA: luz e particulas
// Churrascao da Picanha (Vermelha) no lugar das Joias da Arabia e a ring light da Camera da Live (Verde-Amarela).
// Os desenhos (espeto, labareda, notas...) sao do js/satira.js; aqui ficam o brilho, as particulas e a luz.
Object.assign(Vfx, {
  // espeto pequeno no topo da torre carregando: cresce, balanca e pega fogo
  skewerIcon(c, x, y, k, t, tw) {
    c.save();
    c.globalCompositeOperation = 'source-over';
    c.globalAlpha = Math.min(1, 0.3 + 0.7 * k);
    A.chSkewerLit(c, x, y + Math.sin(t * 3 + tw.id) * 1.5, -0.3 + Math.sin(t * 2.2 + tw.id) * 0.12, 0.25 + 0.4 * k, t, tw.id);
    c.restore();
  },

  // espeto de picanha em brasa voando (Picanha Premium: maior, com brilhinhos dourados)
  orbGrill(c, p, g, t) {
    const P = MAGIC.grill, R = p.big ? 1.35 : 1, age = p.age || 0;
    const tr = p.trail || [];
    const q = tr.length > 2 ? tr[tr.length - 3] : null;
    const ang = q && Math.hypot(p.x - q[0], p.y - q[1]) > 0.5 ? Math.atan2(p.y - q[1], p.x - q[0]) : Math.atan2(p.ty - p.y, p.tx - p.x);
    c.save();
    c.globalCompositeOperation = 'lighter';
    c.lineCap = 'round';
    // rastro de brasa, fino e curto
    for (let i = 1; i <= tr.length; i++) {
      const a = i / (tr.length + 1), p0 = tr[i - 1], p1 = i < tr.length ? tr[i] : null;
      c.strokeStyle = rgbaOf(P.glow, 0.3 * a);
      c.lineWidth = (1.5 + 6 * a) * R;
      c.beginPath(); c.moveTo(p0[0], p0[1]); c.lineTo(p1 ? p1[0] : p.x, p1 ? p1[1] : p.y); c.stroke();
    }
    this.glow(c, p.x, p.y, 18 * R, P.glow, 0.45);
    c.restore();
    c.save();
    A.chSkewerLit(c, p.x, p.y, ang, 0.72 * R, age, p.id || 0);
    if (p.big) {
      for (let i = 0; i < 4; i++) {
        const a = age * (6 + i) + i * 1.57, pisca = 0.5 + 0.5 * Math.sin(age * 15 + i * 2);
        c.fillStyle = i % 2 ? '#ffd84a' : '#fff4c0';
        brilho4(c, p.x + Math.cos(a) * 15, p.y + Math.sin(a) * 7 - 3, 1.6 + 2.6 * pisca, 0.22);
      }
    }
    c.restore();
    // fumacinha e brasas que ficam para tras
    const n = this.rate(p, p.big ? 30 : 20);
    for (let i = 0; i < n; i++) {
      if (i % 4 === 0) this.emit(p.x + U.rand(-4, 4), p.y - 4, U.rand(-10, 10), U.rand(-30, -12), U.rand(0.5, 0.9), U.rand(2.5, 4) * R, i % 8 ? '#cfc8c0' : '#e8e3dc', { kind: 'smoke', drag: 0.4 });
      else this.emit(p.x + U.rand(-4, 4), p.y + U.rand(-3, 3), U.rand(-20, 20), U.rand(-40, -5), U.rand(0.3, 0.55), U.rand(0.8, 1.4) * R, i % 2 ? P.mid : P.glow, { drag: 0.2, grav: -20 });
    }
    Light.add(p.x, p.y + 12, 90 * R, P.glow, p.big ? 0.8 : 0.5, p.big ? 0.35 : 0.15);
  },

  // o espeto chia no alvo: labareda curta, brasinhas, farofa pulando e uma fumacinha
  magicHitGrill(c, f, g) {
    const P = MAGIC.grill, k = f.t / f.T, a = 1 - k, R = f.big ? 1.6 : 1;
    const gx = f.gx != null ? f.gx : f.x, gy = f.gy != null ? f.gy : f.y + 14;
    if (!f._sp) {
      f._sp = 1;
      this.burst(f.x, f.y, f.big ? 26 : f.r ? 16 : 9, f.big ? 240 : 160, P.mid, { kind: 'spark', drag: 0.05, grav: 160, size: R });
      this.burst(f.x, f.y, f.big ? 12 : 5, 60, P.core, { drag: 0.1, size: 1.2 * R, up: 30 });
      const ns = f.big ? 14 : f.r ? 9 : 5, spread = f.r || 22;
      for (let i = 0; i < ns; i++) {
        const an = U.rand(0, U.TAU), sp = U.rand(25, 75) * R;
        this.emit(f.x, f.y, Math.cos(an) * sp, U.rand(-140, -60) * (f.r ? 1 : 0.7), U.rand(0.7, 1.1), U.rand(1.3, 2), i % 3 ? '#e8b25a' : '#c9772e',
          { kind: 'crumb', grav: 420, drag: 0.5, rot: U.rand(0, 3), spin: U.rand(-6, 6), floor: gy + Math.sin(an) * spread * 0.55 * U.YS, bounce: 0.35 });
      }
      for (let i = 0; i < (f.big ? 6 : 3); i++) this.emit(f.x + U.rand(-8, 8), f.y + U.rand(-6, 4), U.rand(-12, 12), U.rand(-40, -20), U.rand(0.7, 1.1), U.rand(4, 7) * R, i % 2 ? '#cfc8c0' : '#ebe6e0', { kind: 'smoke', drag: 0.4 });
    }
    c.save();
    c.globalCompositeOperation = 'lighter';
    this.glow(c, f.x, f.y, (16 + 20 * k) * R, P.glow, 0.45 * a);
    if (k < 0.3) this.glow(c, f.x, f.y, 12 * R, P.core, 0.6 * (1 - k / 0.3));
    // labaredas e aneis em mistura normal: laranja de verdade, legivel no chao claro
    c.globalCompositeOperation = 'source-over';
    // estouro em area (nivel 2+): onda de calor no chao com labaredinhas acendendo na beirada
    if (f.r) {
      const e = U.easeOutCubic(Math.min(1, k * 1.4)), rr = f.r * (0.3 + 0.8 * e);
      c.save();
      c.translate(gx, gy); c.scale(1, U.YS);
      c.globalCompositeOperation = 'lighter';
      this.glow(c, 0, 0, rr * 1.1, P.glow, 0.3 * a);
      c.globalCompositeOperation = 'source-over';
      c.strokeStyle = rgbaOf('#e8641c', 0.75 * a); c.lineWidth = 1 + 2.5 * a;
      c.beginPath(); c.arc(0, 0, rr, 0, U.TAU); c.stroke();
      c.restore();
      for (let pass = 0; pass < 2; pass++) {
        c.fillStyle = pass ? rgbaOf('#ffd36a', 0.95 * a) : rgbaOf('#ff7a24', 0.85 * a);
        for (let i = 0; i < 8; i++) {
          const an = (i / 8) * U.TAU + f.x * 0.1, fl = 0.7 + 0.3 * Math.sin(k * 40 + i * 2);
          A.chFlame(c, gx + Math.cos(an) * rr, gy + Math.sin(an) * rr * U.YS, (7 + 6 * Math.sin(k * Math.PI)) * fl * (pass ? 0.5 : 1), pass ? 1.4 : 2.6, 0);
        }
      }
    }
    if (k < 0.6) {
      const kk = k / 0.6;
      for (let pass = 0; pass < 2; pass++) {
        c.fillStyle = pass ? rgbaOf('#ffe08a', 0.95 * (1 - kk)) : rgbaOf('#ff7a24', 0.9 * (1 - kk));
        for (let i = 0; i < 5; i++) {
          const ox = (i - 2) * 4 * R, fl = 0.7 + 0.3 * Math.sin(k * 50 + i * 2.3);
          A.chFlame(c, f.x + ox, f.y + 4, (11 + 8 * (1 - Math.abs(i - 2) / 2)) * R * fl * (1 - kk * 0.5) * (pass ? 0.55 : 1), (pass ? 1.6 : 3.2) * R, ox * 0.02);
        }
      }
    }
    c.strokeStyle = rgbaOf('#ff9a3a', 0.8 * a);
    c.lineWidth = 2 * a + 0.5;
    c.beginPath(); c.ellipse(f.x, f.y, (5 + 22 * U.easeOutCubic(k)) * R, (5 + 22 * U.easeOutCubic(k)) * R * 0.6, 0, 0, U.TAU); c.stroke();
    c.globalCompositeOperation = 'lighter';
    // Picanha Premium: coluna de fogo de churrasqueira
    if (f.big && k < 0.7) {
      const ka = 1 - k / 0.7, w = 22 * ka;
      const gr = c.createLinearGradient(0, gy - 150, 0, gy);
      gr.addColorStop(0, rgbaOf(P.glow, 0));
      gr.addColorStop(0.7, rgbaOf(P.mid, 0.5 * ka));
      gr.addColorStop(1, rgbaOf(P.core, 0.8 * ka));
      c.fillStyle = gr;
      c.fillRect(gx - w / 2, gy - 150, w, 150);
    }
    c.restore();
    Light.add(gx, gy, (f.r ? f.r * 2.4 : 70) * R, P.glow, Math.pow(a, 1.4) * (f.big ? 1.1 : f.r ? 0.85 : 0.6), f.big ? 0.5 : 0.25);
  },

  // Rodizio: o espeto passa de prato em prato, pulando em arco de um alvo ao outro e deixando um rastro de fumaca
  lightningGrill(c, f, g) {
    const P = MAGIC.grill, k = f.t / f.T, a = k < 0.7 ? 1 : 1 - (k - 0.7) / 0.3;
    const pts = f.pts, ns = pts.length - 1;
    if (ns < 1) return;
    const tv = Math.min(1, k / 0.62) * ns;
    const seg = Math.min(ns - 1, Math.floor(tv)), u = tv >= ns ? 1 : U.easeInOut(tv - seg);
    const reached = tv >= ns ? ns : Math.floor(tv);
    f._hit = f._hit || 0;
    while (f._hit < reached) {
      f._hit++;
      const [hx, hy] = pts[f._hit];
      this.burst(hx, hy, 7, 140, f._hit % 2 ? P.mid : P.core, { kind: 'spark', drag: 0.04, grav: 220 });
      for (let j = 0; j < 2; j++) this.emit(hx + U.rand(-6, 6), hy + U.rand(-6, 2), U.rand(-10, 10), U.rand(-36, -18), U.rand(0.6, 0.9), U.rand(3.5, 5.5), j ? '#d8d2ca' : '#eeeae4', { kind: 'smoke', drag: 0.4 });
    }
    // arco do pulo i (quadratica com o pico acima do meio)
    const hop = i => {
      const [x0, y0] = pts[i], [x1, y1] = pts[i + 1];
      const h = 16 + Math.hypot(x1 - x0, y1 - y0) * 0.22;
      return [x0, y0, (x0 + x1) / 2, (y0 + y1) / 2 - 2 * h, x1, y1];
    };
    c.save();
    c.lineCap = 'round';
    c.setLineDash([3, 5]);
    c.lineDashOffset = -k * 40;
    c.strokeStyle = rgbaOf('#e6dfd6', 0.75 * a); c.lineWidth = 2.2;
    for (let i = 0; i <= seg; i++) {
      const fr = i < seg ? 1 : u;
      if (fr <= 0) break;
      const [x0, y0, qx, qy, x1, y1] = hop(i);
      c.beginPath(); c.moveTo(x0, y0);
      for (let j = 1; j <= 10; j++) { const v = fr * j / 10, w = 1 - v; c.lineTo(w * w * x0 + 2 * w * v * qx + v * v * x1, w * w * y0 + 2 * w * v * qy + v * v * y1); }
      c.stroke();
    }
    c.setLineDash([]);
    c.lineDashOffset = 0;
    // clarao de brasa nos pratos ja servidos
    c.globalCompositeOperation = 'lighter';
    for (let i = 1; i <= reached; i++) this.glow(c, pts[i][0], pts[i][1], 18, P.mid, 0.55 * a);
    c.globalCompositeOperation = 'source-over';
    if (k < 0.9) {
      const [x0, y0, qx, qy, x1, y1] = hop(seg), w = 1 - u;
      const x = w * w * x0 + 2 * w * u * qx + u * u * x1, y = w * w * y0 + 2 * w * u * qy + u * u * y1;
      const tx = 2 * w * (qx - x0) + 2 * u * (x1 - qx), ty = 2 * w * (qy - y0) + 2 * u * (y1 - qy);
      c.globalAlpha = Math.min(1, (0.9 - k) / 0.2);
      A.chSkewerLit(c, x, y, Math.atan2(ty, tx), 0.75, g.time, f.seed || 0);
      Light.add(x, y + 16, 80, P.glow, 0.6 * a);
    }
    c.restore();
    for (let i = 1; i <= reached; i++) Light.add(pts[i][0], pts[i][1] + 14, 90, P.glow, 0.6 * a, 0.25);
  },

  // Picanha pra Todos: nuvem de fumaca de churrasco em cima de uma grelha em brasa (os espetos que caem sao do
  // render.js, skybolt pequeno -> A.chSkewerDrop)
  cloudGrill(c, f, g, t) {
    const P = MAGIC.grill;
    const a = Math.min(1, f.t * 3, (f.T - f.t) * 3);
    const pop = U.easeOutBack(Math.min(1, f.t * 2.6));
    const bob = Math.sin(t * 2.2 + f.x * 0.1) * 4;
    const cx = f.x, cy = f.y - 112 + bob;
    c.save();
    c.save();
    c.translate(f.x, f.y + 4); c.scale(1, U.YS * 0.75);
    const sr = 62 - bob * 1.5;
    const sh = c.createRadialGradient(0, 0, 0, 0, 0, sr);
    sh.addColorStop(0, `rgba(48,30,12,${0.24 * a})`);
    sh.addColorStop(1, 'rgba(48,30,12,0)');
    c.fillStyle = sh;
    c.fillRect(-sr, -sr, sr * 2, sr * 2);
    c.restore();
    c.globalCompositeOperation = 'lighter';
    this.glow(c, cx, cy + 20, 62, P.glow, 0.34 * a * (0.85 + 0.15 * Math.sin(t * 5)));
    c.globalCompositeOperation = 'source-over';
    c.globalAlpha = a;
    c.translate(cx, cy);
    c.scale(pop * 1.1, pop * 1.1);
    // grelha com brasa piscando entre as barras
    A.rrect(c, -28, 15, 56, 7, 3, '#ff8a2a');
    for (let i = 0; i < 6; i++) {
      const fl = 0.5 + 0.5 * Math.sin(t * 9 + i * 1.7);
      A.circ(c, -22 + i * 8.8, 18.5, 1.8 + fl, fl > 0.6 ? '#ffe08a' : '#ffb347');
    }
    c.strokeStyle = '#3a3a42'; c.lineWidth = 1.6;
    c.beginPath();
    for (let i = 0; i <= 8; i++) { const x = -28 + i * 7; c.moveTo(x, 15); c.lineTo(x, 22); }
    c.stroke();
    A.rrect(c, -30, 14, 60, 9, 3, null, '#2a2a30', 1.6);
    // nuvem de fumaca: bolas cinza-claras com sombra embaixo e brilho em cima
    const PF = this._puffs || (this._puffs = [[-24, 0, 11], [-11, -9, 14], [6, -11, 15], [21, -3, 12], [0, 2, 14], [-15, 4, 10], [15, 5, 11]]);
    for (let pass = 0; pass < 3; pass++) {
      for (let i = 0; i < PF.length; i++) {
        const [px, py, pr] = PF[i], r = pr * (1 + 0.05 * Math.sin(t * 3 + i * 1.3));
        if (pass === 0) A.circ(c, px, py + 3, r, '#8f8a86');
        else if (pass === 1) A.circ(c, px, py, r, '#d8d3ce');
        else A.circ(c, px - r * 0.3, py - r * 0.35, r * 0.5, '#f3f0ec');
      }
    }
    c.restore();
    const n = this.rate(f, 9 * a);
    for (let i = 0; i < n; i++) {
      if (i % 2) this.emit(cx + U.rand(-20, 20), cy - 14, U.rand(-6, 6), U.rand(-24, -10), U.rand(1, 1.6), U.rand(5, 8), '#d8d3ce', { kind: 'smoke', drag: 0.5 });
      else this.emit(cx + U.rand(-24, 24), cy + 24, U.rand(-10, 10), U.rand(10, 40), U.rand(0.6, 1), U.rand(1, 1.6), i % 4 ? FIRE.mid : FIRE.core, { drag: 0.3, grav: 80 });
    }
    Light.add(cx, f.y - 20, 140, P.glow, 0.4 * a * (0.85 + 0.15 * Math.sin(t * 6)), 0.25);
  },

  // Brasa Viva / Rodizio no alvo: labaredinhas dando a volta no corpo (as de tras mais apagadas)
  searGrill(c, e, y, s, t) {
    const a = Math.min(1, e.shockT / 0.4);
    for (let half = 0; half < 2; half++) {
      c.fillStyle = rgbaOf(half ? FIRE.mid : FIRE.glow, a * (half ? 0.85 : 0.45));
      for (let i = 0; i < 7; i++) {
        const an = t * 2.2 + e.id + (i / 7) * U.TAU;
        if ((Math.sin(an) > 0) !== !!half) continue;
        const fl = 0.7 + 0.3 * Math.sin(t * 19 + i * 2.3 + e.id);
        A.chFlame(c, e.x + Math.cos(an) * s * 0.95, y + s * 0.35 + Math.sin(an) * s * 0.34, (5 + s * 0.35) * fl, 2.2, Math.sin(t * 7 + i) * 0.15);
      }
    }
    c.fillStyle = rgbaOf(FIRE.core, 0.8 * a);
    for (let i = 0; i < 7; i++) {
      const an = t * 2.2 + e.id + (i / 7) * U.TAU;
      if (Math.sin(an) <= 0) continue;
      const fl = 0.7 + 0.3 * Math.sin(t * 23 + i * 1.7 + e.id);
      A.chFlame(c, e.x + Math.cos(an) * s * 0.95, y + s * 0.35 + Math.sin(an) * s * 0.34, (2.5 + s * 0.15) * fl, 1.1, 0);
    }
    Light.add(e.x, y + 10, 50 + s * 2, FIRE.glow, 0.45 * a);
  },

  // Macarico do Churrasqueiro: chama continua em cone, com nucleo azul no bico, que abre em labareda no alvo
  torchGrill(c, tw, g, t) {
    const e = tw.beam;
    if (!e || e.dead) return;
    const [x0, y0] = this.topOf(tw, g);
    const x1 = e.x, y1 = g.hitY(e);
    const k = Math.min(1, tw.beamT / tw.S.ramp);
    const dx = x1 - x0, dy = y1 - y0, len = Math.hypot(dx, dy) || 1;
    const nx = -dy / len, ny = dx / len;
    // cone do bico ate "to" do caminho, largura de w0 a w1, bordas tremulando
    const cone = (w0, w1, to, col, wob, ph) => {
      c.beginPath();
      for (let i = 0; i <= 10; i++) {
        const q = i / 10, w = (w0 + (w1 - w0) * q) * (1 + wob * Math.sin(q * 14 - t * 30 + ph));
        const px = x0 + dx * q * to + nx * w, py = y0 + dy * q * to + ny * w;
        if (i) c.lineTo(px, py); else c.moveTo(px, py);
      }
      for (let i = 10; i >= 0; i--) {
        const q = i / 10, w = (w0 + (w1 - w0) * q) * (1 + wob * Math.sin(q * 13 - t * 27 + ph + 1.7));
        c.lineTo(x0 + dx * q * to - nx * w, y0 + dy * q * to - ny * w);
      }
      c.closePath(); c.fillStyle = col; c.fill();
    };
    const Wk = 1 + 0.6 * k;
    c.save();
    // brilho quente por baixo (aditivo, fraco) e a chama em mistura normal, para ler laranja e nao virar laser
    c.globalCompositeOperation = 'lighter';
    cone(4, 12 * Wk, 1, rgbaOf(FIRE.glow, 0.18 + 0.1 * k), 0.2, 0);
    c.save();
    c.translate(e.x, e.y + 2); c.scale(1, U.YS * 0.8);
    this.glow(c, 0, 0, 18 + 18 * k, FIRE.deep, 0.4 + 0.3 * k);
    c.restore();
    c.globalCompositeOperation = 'source-over';
    cone(2.4, 7.5 * Wk, 1, rgbaOf('#ff6a1c', 0.6 + 0.15 * k), 0.18, 1);
    cone(1.8, 5 * Wk, 0.97, rgbaOf('#ffa63a', 0.85), 0.14, 2);
    cone(1.1, 2.6 * Wk, 0.9, rgbaOf('#ffe08a', 0.92), 0.1, 3);
    cone(2.8, 1.4, 0.2, 'rgba(70,130,245,0.9)', 0.05, 4);
    cone(1.4, 0.5, 0.15, 'rgba(225,242,255,0.95)', 0, 5);
    for (let pass = 0; pass < 2; pass++) {
      c.fillStyle = pass ? 'rgba(255,224,138,0.95)' : 'rgba(255,110,32,0.85)';
      for (let i = 0; i < 5; i++) {
        const fl = 0.7 + 0.3 * Math.sin(t * 23 + i * 1.9);
        A.chFlame(c, x1 + (i - 2) * 4.5, y1 + 4, (10 + 7 * k) * fl * (1 - Math.abs(i - 2) * 0.2) * (pass ? 0.55 : 1), pass ? 1.6 : 3, (i - 2) * 0.12);
      }
    }
    c.globalCompositeOperation = 'lighter';
    this.glow(c, x1, y1, 12 + 10 * k, FIRE.glow, 0.45);
    this.glow(c, x0, y0, 9, '#8fc0ff', 0.5);
    c.restore();
    const n = this.rate(tw, 14 + 30 * k);
    for (let i = 0; i < n; i++) {
      if (i % 5 === 4) this.emit(x1 + U.rand(-5, 5), y1 - 4, U.rand(-8, 8), U.rand(-34, -18), U.rand(0.6, 1), U.rand(3, 5), '#d8d2ca', { kind: 'smoke', drag: 0.4 });
      else this.emit(x1 + U.rand(-6, 6), y1 + U.rand(-4, 4), U.rand(-40, 40), U.rand(-90, -20), U.rand(0.3, 0.6), U.rand(1, 2), i % 2 ? FIRE.mid : FIRE.glow, { kind: 'spark', grav: 140, drag: 0.2 });
    }
    Light.add(x1, e.y - 4, 85 + 60 * k, FIRE.glow, 0.5 + 0.4 * k, 0.3);
    Light.add(x0 + dx * 0.5, y0 + dy * 0.5 + 24, 70, FIRE.glow, 0.25 + 0.2 * k);
  },

  // Cervejinha Gelada: a caneca sobe no "tim-tim", espuma abre em anel no chao, gotas de cerveja e pedrinhas de gelo
  flashBeer(c, f, g) {
    const k = f.t / f.T, a = 1 - k, e = U.easeOutCubic(k), r = f.r;
    if (!f._sp) {
      f._sp = 1;
      this.burst(f.x, f.y - 12, 14, 200, '#ffd36a', { kind: 'spark', drag: 0.05, grav: 300 });
      for (let i = 0; i < 9; i++) {
        const an = U.rand(0, U.TAU), sp = U.rand(40, 100);
        this.emit(f.x, f.y - 12, Math.cos(an) * sp, U.rand(-170, -80), U.rand(0.8, 1.2), U.rand(1.8, 2.6), i % 2 ? '#e8f8ff' : '#bfeaff',
          { kind: 'gem', grav: 420, drag: 0.5, rot: U.rand(-0.5, 0.5), spin: U.rand(-6, 6), floor: f.y + Math.sin(an) * r * 0.4 * U.YS, bounce: 0.4 });
      }
    }
    c.save();
    c.globalCompositeOperation = 'lighter';
    this.glow(c, f.x, f.y - 10, r * (0.5 + 0.6 * e), '#bfe6ff', 0.7 * a);
    c.globalCompositeOperation = 'source-over';
    // anel de espuma abrindo no chao: faixa branca com bolhas grudadas
    const rr = r * (0.2 + 0.55 * e);
    c.globalAlpha = Math.min(1, a * 1.6);
    c.beginPath(); c.ellipse(f.x, f.y, rr, rr * U.YS, 0, 0, U.TAU);
    c.strokeStyle = 'rgba(190,160,90,0.45)'; c.lineWidth = 6 * (1 - k) + 3; c.stroke();
    c.strokeStyle = '#fffdf6'; c.lineWidth = 6 * (1 - k) + 1; c.stroke();
    for (let i = 0; i < 14; i++) {
      const an = (i / 14) * U.TAU + f.x * 0.05, br = (2.6 + 1.6 * Math.sin(i * 2.7)) * (1 - 0.4 * k);
      A.circ(c, f.x + Math.cos(an) * rr, f.y + Math.sin(an) * rr * U.YS - 1, br, '#fffdf6', 'rgba(190,160,90,0.5)', 0.7);
    }
    // gotas de cerveja: gotinhas ambar em pe, com pontinha de espuma
    for (let i = 0; i < 10; i++) {
      const an = (i / 10) * U.TAU + 0.4, d = r * (0.12 + 0.5 * e) * (0.7 + 0.3 * Math.sin(i * 3.3));
      const hgt = Math.sin(Math.min(1, k * 1.4) * Math.PI) * (26 + 12 * Math.sin(i * 1.7));
      const x = f.x + Math.cos(an) * d, y = f.y - 10 + Math.sin(an) * d * 0.5 - hgt;
      c.beginPath(); c.moveTo(x, y - 3.4); c.quadraticCurveTo(x + 2.2, y + 0.4, x, y + 1.8); c.quadraticCurveTo(x - 2.2, y + 0.4, x, y - 3.4);
      c.fillStyle = '#f6bd45'; c.fill(); c.strokeStyle = 'rgba(140,90,20,0.55)'; c.lineWidth = 0.7; c.stroke();
      A.circ(c, x - 0.6, y - 0.2, 0.6, '#fffbe8');
    }
    if (k < 0.8) {
      const pk = U.easeOutBack(Math.min(1, k / 0.22));
      c.globalAlpha = k < 0.6 ? 1 : (0.8 - k) / 0.2;
      c.save();
      c.translate(f.x, f.y - 56 - 8 * e);   // acima da barra de vida do alvo
      c.rotate(Math.sin(k * 14) * 0.22 * (1 - k));
      c.scale(pk, pk);
      c.lineCap = 'round';
      c.beginPath(); c.arc(8, 1, 4.6, -Math.PI / 2, Math.PI / 2);
      c.strokeStyle = 'rgba(120,150,170,0.9)'; c.lineWidth = 3.4; c.stroke();
      c.strokeStyle = '#eef6fb'; c.lineWidth = 1.8; c.stroke();
      A.rrect(c, -8, -7, 16, 17, 2.5, '#f4b13a', '#8a5a14', 1.3);
      A.rect(c, -6.6, -3, 2.2, 11, 'rgba(255,255,255,0.45)');
      for (let i = 0; i < 4; i++) A.circ(c, -1 + (i % 2) * 4, 7 - i * 3 - ((k * 30 + i) % 3), 0.8, 'rgba(255,248,220,0.9)');
      A.circ(c, -5, -7, 4, '#fffdf6', 'rgba(190,160,90,0.6)', 0.8);
      A.circ(c, 5, -7.5, 3.8, '#fffdf6', 'rgba(190,160,90,0.6)', 0.8);
      A.circ(c, 0, -9, 4.6, '#fffdf6', 'rgba(190,160,90,0.6)', 0.8);
      A.ell(c, 7.2, -3, 1.6, 3, '#fffdf6');
      c.fillStyle = 'rgba(255,255,255,0.85)';
      c.beginPath(); c.arc(3, 0, 0.7, 0, U.TAU); c.moveTo(-1.3, 5); c.arc(-2, 5, 0.7, 0, U.TAU); c.fill();
      c.restore();
    }
    c.globalCompositeOperation = 'lighter';
    c.globalAlpha = 1;
    for (let i = 0; i < 6; i++) {
      const tw = Math.sin(k * 30 + i * 2.1);
      if (tw < 0.2) continue;
      const an = i * 1.05 + 0.3, d = r * (0.3 + 0.4 * e);
      c.fillStyle = rgbaOf('#ffffff', a * tw);
      brilho4(c, f.x + Math.cos(an) * d, f.y - 14 + Math.sin(an) * d * 0.45, 2 + 4 * tw, 0.2);
    }
    c.restore();
    Light.add(f.x, f.y, r * 2.2, '#d8f2ff', 0.6 * a, 0.2);
  },

  // Camera da Live (Verde-Amarela): ring light acesa no lugar do farol, flash de foto de tempos em tempos e o
  // pontinho vermelho de gravando. Chamado dentro da mistura aditiva do towerExtra
  ringLight(c, tw, lx, ly, t) {
    this.glow(c, lx, ly, 22, '#eef4ff', 0.35);
    // aro da ring light e o celular no meio, em mistura normal para o desenho aparecer sobre o brilho
    c.save();
    c.globalCompositeOperation = 'source-over';
    c.beginPath(); c.ellipse(lx, ly, 9, 9, 0, 0, U.TAU);
    c.strokeStyle = '#3c3f4a'; c.lineWidth = 5; c.stroke();
    c.strokeStyle = '#fbfdff'; c.lineWidth = 2.6; c.stroke();
    A.rrect(c, lx - 2.6, ly - 4.2, 5.2, 8.4, 1.3, '#2a2d36', '#15171c', 0.8);
    A.circ(c, lx, ly - 2.4, 1, '#7fb0ff');
    c.restore();
    const ph = (t + tw.id * 0.77) % 3.4;
    if (ph < 0.2) {
      const fk = 1 - ph / 0.2;
      this.glow(c, lx, ly, 28, '#ffffff', 0.55 * fk);
      this.star(c, lx, ly, 8 + 16 * fk, 0.6, '#ffffff', 0.85 * fk);
      Light.add(lx, ly + 30, 130, '#f4f8ff', 0.6 * fk, 0.2);
    }
    c.save();
    c.globalCompositeOperation = 'source-over';
    if (Math.sin(t * 5) > -0.2) A.circ(c, lx + 12, ly - 9, 2.1, '#ff3b3b', 'rgba(90,10,10,0.6)', 0.8);
    c.restore();
  },
});
