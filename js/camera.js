'use strict';
// Camera da fase: zoom livre (roda do mouse, pinca com dois dedos, arrastar para andar) e close-ups curtos nos
// momentos de piada (adversario novo, chefe chegando, habilidade do heroi). Uma transformacao so mundo <-> tela:
// o Render.level desenha o mundo com ela e as regioes clicaveis do mundo (UI.cam) convertem o ponteiro com ela.
// HUD, menus e botoes ficam na tela. x, y = canto de cima da vista no mundo; z = zoom (1 = mapa inteiro).

const CAM_ZMAX = 2;   // zoom livre: de 1x (padrao, mapa inteiro) a 2x
// close-up: entra em 0,35 s, segura 1,2 s, sai em 0,45 s; zoom 1,6x; no maximo um a cada 6 s; o jogo anda a 0,5x
const CINE = { IN: 0.35, HOLD: 1.2, OUT: 0.45, ZOOM: 1.6, GAP: 6, SLOW: 0.5 };
// habilidades ativas do heroi com close-up: a primeira vez na fase e depois no maximo a cada 40 s cada uma
// (Faz o L, Discurso de Palanque, Comitiva, Stories, Cassacao, Imbrochavel!, Motociata)
const CINE_AB = { hawk: 1, whirl: 1, call: 1, trail: 1, bless: 1, flare: 1, firetrail: 1 };
const CINE_AB_GAP = 40;

const Cam = {
  x: 0, y: 0, z: 1,                       // camera final do quadro
  snap: { x: 0, y: 0, z: 1 },             // retrato do quadro (guardado nas regioes do mundo)
  u: { cx: W / 2, cy: H / 2, z: 1 },       // camera do jogador (centro e zoom), atual
  ut: { cx: W / 2, cy: H / 2, z: 1 },      // ... e o alvo dela (a roda anima ate ele)
  cine: null, w: 0, queue: [], lastStart: -1e9, g: null,
  press: null, pan: null, pinch: null, quietUntil: 0, lastTap: null,
  typesSeen: new Set(), bossSeen: new Set(), abPrev: {}, abLast: {},

  reset() {
    this.u = { cx: W / 2, cy: H / 2, z: 1 };
    this.ut = { cx: W / 2, cy: H / 2, z: 1 };
    this.x = 0; this.y = 0; this.z = 1;
    this.snap = { x: 0, y: 0, z: 1 };
    this.cine = null; this.w = 0; this.queue = []; this.lastStart = -1e9;
    this.press = null; this.pan = null; this.pinch = null; this.lastTap = null;
    this.typesSeen = new Set(); this.bossSeen = new Set(); this.abPrev = {}; this.abLast = {};
    this.g = App.game;
  },

  // ------------------------------------------------------------ transformacao
  // centro valido para o zoom z: a vista nunca sai do mapa
  clampC(cx, cy, z) {
    const hw = W / (2 * z), hh = H / (2 * z);
    return [U.clamp(cx, hw, W - hw), U.clamp(cy, hh, H - hh)];
  },
  toWorld(sx, sy, s) { s = s || this; return [s.x + sx / s.z, s.y + sy / s.z]; },
  // margin: com zoom, prende o ponto dentro da tela (botoes presos ao mundo que sairam da vista)
  toScreen(wx, wy, s, margin) {
    s = s || this;
    let x = (wx - s.x) * s.z, y = (wy - s.y) * s.z;
    if (margin && s.z > 1.001) { x = U.clamp(x, margin, W - margin); y = U.clamp(y, margin, H - margin); }
    return [x, y];
  },
  apply(c) { c.scale(this.z, this.z); c.translate(-this.x, -this.y); },
  userCam() { const u = this.u; return { x: u.cx - W / (2 * u.z), y: u.cy - H / (2 * u.z), z: u.z }; },

  zoomed() { return this.u.z > 1.01 || this.ut.z > 1.01; },
  busy() { return !!(this.press || this.pan || this.pinch); },
  dragging() { return !!((this.press && this.press.moved) || (this.pan && this.pan.moved) || this.pinch); },
  timeK() { return 1 - CINE.SLOW * this.w; },
  inLevel() { return App.screen === 'level' && !!App.game && !!App.lv; },

  // ------------------------------------------------------------ zoom livre
  zoomAt(sx, sy, f) {
    if (!this.inLevel()) return;
    this.takeOver();
    const t = this.ut, z0 = t.z, z1 = U.clamp(z0 * f, 1, CAM_ZMAX);
    if (Math.abs(z1 - z0) < 1e-4) return;
    // o ponto do mundo debaixo do cursor fica debaixo do cursor
    const wx = t.cx - W / (2 * z0) + sx / z0, wy = t.cy - H / (2 * z0) + sy / z0;
    [t.cx, t.cy] = this.clampC(wx - sx / z1 + W / (2 * z1), wy - sy / z1 + H / (2 * z1), z1);
    t.z = z1;
  },
  wheel(sx, sy, dy, pinch) {
    const lv = App.lv;
    if (!this.inLevel() || lv.paused || lv.overlay) return;
    this.zoomAt(sx, sy, U.clamp(Math.exp(-dy * (pinch ? 0.01 : 0.0018)), 0.6, 1.6));
  },
  resetZoom() { this.ut = { cx: W / 2, cy: H / 2, z: 1 }; },
  // anda com a camera do jogador (dx, dy em px da tela)
  panBy(dx, dy) {
    const u = this.u, t = this.ut;
    u.cx -= dx / u.z; u.cy -= dy / u.z;
    t.cx -= dx / u.z; t.cy -= dy / u.z;
    [u.cx, u.cy] = this.clampC(u.cx, u.cy, u.z);
    [t.cx, t.cy] = this.clampC(t.cx, t.cy, t.z);
  },
  // o jogador pegou a camera no meio de um close-up: ela fica onde esta e passa a ser dele
  takeOver() {
    if (!this.cine) return;
    const z = U.clamp(this.z, 1, CAM_ZMAX), cx = this.x + W / (2 * this.z), cy = this.y + H / (2 * this.z);
    this.u = { cx, cy, z };
    this.ut = { cx, cy, z };
    this.cine = null; this.w = 0;
  },

  // ------------------------------------------------------------ ponteiro (mouse e toque de compatibilidade)
  // devolve true quando o clique fica para depois (ou foi usado aqui); false = o UI.click segue como sempre
  pointerDown(x, y, btn) {
    if (!this.inLevel()) return false;
    const now = performance.now();
    if (now < this.quietUntil) return true;   // fim de pinca ou arrasto no dedo: engole o clique de compatibilidade
    const r = UI.regionAt(x, y);
    if (!r || !r.cam) return false;            // HUD, menus e botoes: clique na hora
    if (!this.zoomed()) return false;          // sem zoom: tudo como antes
    // clique duplo (ou toque duplo) no chao, fora dos modos de mira: volta ao mapa inteiro
    if (r.key === 'world' && !App.lv.mode) {
      const p = this.lastTap;
      if (p && now - p.t < 320 && Math.hypot(x - p.x, y - p.y) < 28) { this.lastTap = null; this.resetZoom(); return true; }
      this.lastTap = { t: now, x, y };
    } else this.lastTap = null;
    // com zoom, apertar no mundo espera soltar: sem arrastar vira clique, arrastando anda com a camera
    this.press = { x, y, lx: x, ly: y, btn, moved: false };
    return true;
  },
  pointerMove(x, y) {
    const p = this.press;
    if (!p) return;
    if (!p.moved && Math.hypot(x - p.x, y - p.y) > 6) { p.moved = true; this.lastTap = null; this.takeOver(); }
    if (p.moved) this.panBy(x - p.lx, y - p.ly);
    p.lx = x; p.ly = y;
  },
  pointerUp() {
    const p = this.press;
    if (!p) return;
    this.press = null;
    if (!p.moved) UI.click(p.x, p.y, p.btn);
  },

  // ------------------------------------------------------------ toque: pinca (2 dedos) e arrastar (1 dedo, com zoom)
  // o toque simples continua chegando como mouse (eventos de compatibilidade do navegador)
  touch(ev, kind) {
    if (!this.inLevel()) return;
    const ts = ev.touches, pts = [];
    for (let i = 0; i < ts.length; i++) pts.push(App.toLogical(ts[i]));
    const now = performance.now();
    if (kind === 'start') {
      if (ts.length >= 2) {
        ev.preventDefault();
        this.takeOver();
        const [a, b] = pts;
        const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
        const [wx, wy] = this.toWorld(mx, my, this.userCam());
        this.pinch = { d0: Math.hypot(a[0] - b[0], a[1] - b[1]) || 1, z0: this.u.z, wx, wy };
        this.pan = null; this.press = null; this.lastTap = null;
        this.quietUntil = now + 500;
      } else if (ts.length === 1 && !this.pinch) {
        const [x, y] = pts[0];
        const r = UI.regionAt(x, y);
        this.pan = this.zoomed() && r && r.cam ? { x, y, lx: x, ly: y, moved: false } : null;
      }
    } else if (kind === 'move') {
      if (this.pinch && ts.length >= 2) {
        ev.preventDefault();
        const [a, b] = pts, P = this.pinch;
        const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
        const z = U.clamp(P.z0 * (Math.hypot(a[0] - b[0], a[1] - b[1]) || 1) / P.d0, 1, CAM_ZMAX);
        // o ponto do mundo que estava entre os dedos continua entre eles (pinca e arrasto juntos)
        const [cx, cy] = this.clampC(P.wx - mx / z + W / (2 * z), P.wy - my / z + H / (2 * z), z);
        this.u = { cx, cy, z };
        this.ut = { cx, cy, z };
        this.quietUntil = now + 500;
      } else if (this.pan && ts.length === 1) {
        const [x, y] = pts[0], p = this.pan;
        if (!p.moved && Math.hypot(x - p.x, y - p.y) > 8) { p.moved = true; this.takeOver(); }
        if (p.moved) { ev.preventDefault(); this.panBy(x - p.lx, y - p.ly); this.quietUntil = now + 400; }
        p.lx = x; p.ly = y;
      }
    } else {
      if (this.pinch && ts.length < 2) {
        this.pinch = null;
        this.quietUntil = now + 500;
        // sobrou um dedo: continua arrastando dali, sem pulo
        if (ts.length === 1 && this.zoomed()) { const [x, y] = pts[0]; this.pan = { x, y, lx: x, ly: y, moved: true }; }
      } else if (!ts.length) {
        if (this.pan && this.pan.moved) this.quietUntil = now + 400;
        this.pan = null;
      }
    }
  },

  // ------------------------------------------------------------ close-ups
  // vivo e visivel (quem cavou, sumiu ou esta invisivel nao ganha close-up)
  alive(s) { return !!s && !s.dead && !s.removed && !s.reached && !s.burrowed && !s.untargetable && !(s.T && s.T.stealth && !s.revealed); },
  inView(s) { return s.x > 40 && s.x < W - 40 && s.y > 70 && s.y < H - 30; },
  // ponto de mira: meio do corpo (topo do sprite, que ja inclui o voo e o CHAR_SCALE)
  topOf(s) {
    if (s.T) return (A.enemyTop && typeof ESPR !== 'undefined' && ESPR.ready(s.type) && A.enemyTop(s)) || s.T.size * 2.6;
    return (A.unitTop && A.unitTop(s)) || 46;
  },

  request(kind, subj, o) {
    if (Save.data.cine === false) return;
    this.queue = this.queue.filter(q => q.subj !== subj || q.kind !== kind);
    this.queue.push(Object.assign({ kind, subj, at: App.time, until: App.time + (o.wait || 1) }, o));
  },
  stopCine() {
    this.queue = [];
    if (this.cine && this.cine.out == null) { this.cine.out = 0; this.cine.w0 = this.w; }
  },

  // depois de cada passo do jogo (App.afterUpdate): o que merece close-up
  watch(g, lv) {
    if (g !== this.g) return;
    // adversario novo: o g.announce ainda nao foi lido pelo aviso "Novo adversario" (Level.notices, no desenho)
    for (const type of g.announce) {
      if (this.typesSeen.has(type)) continue;
      this.typesSeen.add(type);
      const e = g.enemies.find(o => o.type === type && !o.dead);
      if (!e || e.T.boss) continue;   // chefe tem o close-up dele
      this.request('new', e, { pri: 2, wait: 5, label: shortName(e.T.name), caption: 'Novo adversário', accent: '#ec8a76' });
    }
    // chefe entrando
    for (const e of g.enemies) {
      if (!e.T.boss || this.bossSeen.has(e.id)) continue;
      this.bossSeen.add(e.id);
      this.request('boss', e, { pri: 3, wait: 6, label: shortName(e.T.name), caption: 'Chegou à Esplanada', accent: '#e0574a' });
    }
    // habilidade ativa do heroi: o tempo de recarga dela pula para cima quando ela dispara
    const h = g.hero;
    if (h && h.abT) {
      for (const k in h.abT) {
        const v = h.abT[k], p = this.abPrev[k];
        this.abPrev[k] = v;
        if (!CINE_AB[k] || h.dead || p == null || !(v > p + 2)) continue;
        if (this.abLast[k] != null && App.time - this.abLast[k] < CINE_AB_GAP) continue;
        this.request('ability', h, { pri: 1, wait: 0.6, ab: k });   // o nome da habilidade ja sobe da cabeca dele
      }
    }
  },

  // um quadro (Level.draw): anima a camera do jogador, conduz o close-up e monta a camera final
  frame(dt, g, lv) {
    if (this.g !== g) this.reset();
    dt = Math.min(dt || 0, 0.1);
    const u = this.u, t = this.ut, k = 1 - Math.exp(-dt * 14);
    u.z += (t.z - u.z) * k; u.cx += (t.cx - u.cx) * k; u.cy += (t.cy - u.cy) * k;
    if (Math.abs(t.z - u.z) < 1e-3 && Math.abs(t.cx - u.cx) < 0.05 && Math.abs(t.cy - u.cy) < 0.05) { u.z = t.z; u.cx = t.cx; u.cy = t.cy; }
    [u.cx, u.cy] = this.clampC(u.cx, u.cy, u.z);
    this.cineStep(dt, g, lv);
    let z = u.z, cx = u.cx, cy = u.cy;
    const C = this.cine, w = this.w;
    if (C && w > 0) {
      // zoom em escala geometrica e centro linear: o personagem chega ao meio da tela sem voltar
      const cz = Math.max(CINE.ZOOM, u.z);
      const [fx, fy] = this.clampC(C.fx, C.fy, cz);
      z = u.z * Math.pow(cz / u.z, w);
      cx = u.cx + (fx - u.cx) * w; cy = u.cy + (fy - u.cy) * w;
    }
    [cx, cy] = this.clampC(cx, cy, z);
    if (z < 1.0005) { this.z = 1; this.x = 0; this.y = 0; }
    else { this.z = z; this.x = cx - W / (2 * z); this.y = cy - H / (2 * z); }
    this.snap = { x: this.x, y: this.y, z: this.z };
  },

  cineStep(dt, g, lv) {
    const C = this.cine;
    // mexendo no jogo (menu aberto, mira, arrastando) ou close-ups desligados: o close-up sai antes da hora
    const blocked = Save.data.cine === false || lv.overlay || this.busy() || !!lv.mode || !!(lv.sel && (lv.sel.spot || lv.sel.tower));
    if (C) {
      if (!lv.paused) {
        C.t += dt;
        if (this.alive(C.subj)) {
          // segue o personagem andando, sem tremer com o balanco do passo
          const s = C.subj, top = this.topOf(s), kk = 1 - Math.exp(-dt * 8);
          C.top += (top - C.top) * kk;
          C.fx += (s.x - C.fx) * kk; C.fy += (s.y - top * 0.5 - C.fy) * kk;
        }
      }
      if (C.out == null && (blocked || C.t >= CINE.IN + CINE.HOLD)) { C.out = 0; C.w0 = this.w; }
      if (C.out != null) {
        if (!lv.paused) C.out += dt;
        const q = Math.min(1, C.out / CINE.OUT);
        this.w = C.w0 * (1 - U.easeInOut(q));
        if (q >= 1) { this.cine = null; this.w = 0; }
      } else this.w = U.easeInOut(Math.min(1, C.t / CINE.IN));
      return;
    }
    this.w = 0;
    const now = App.time;
    if (!this.queue.length) return;
    this.queue = this.queue.filter(q => q.until > now && this.alive(q.subj));
    if (blocked || lv.paused || g.state !== 'running' || now - this.lastStart < CINE.GAP) return;
    let best = null;
    for (const q of this.queue) if (this.inView(q.subj) && (!best || q.pri > best.pri)) best = q;
    if (!best) return;
    this.queue.splice(this.queue.indexOf(best), 1);
    const s = best.subj, top = this.topOf(s);
    this.cine = { kind: best.kind, subj: s, label: best.label, caption: best.caption, accent: best.accent, fx: s.x, fy: s.y - top * 0.5, top, t: 0, out: null, w0: 0 };
    this.lastStart = now;
    if (best.ab) this.abLast[best.ab] = now;
  },

  // por cima do mundo, antes do HUD: vinheta suave e o nome do personagem perto dele
  overlay(c) {
    const C = this.cine, w = this.w;
    if (!C || w < 0.01) return;
    c.save();
    const vg = c.createRadialGradient(W / 2, H / 2, H * 0.42, W / 2, H / 2, H * 0.98);
    vg.addColorStop(0, 'rgba(30,14,6,0)');
    vg.addColorStop(1, `rgba(30,14,6,${0.36 * w})`);
    c.fillStyle = vg;
    c.fillRect(0, 0, W, H);
    c.restore();
    // o chefe ja tem a faixa com o nome no alto; o nome perto dele entra quando a faixa sai
    if (!C.label || (C.kind === 'boss' && App.lv.banner)) return;
    const pop = U.easeOutBack(U.clamp(C.t / 0.4, 0, 1));
    const a = U.clamp(w * 1.5, 0, 1) * U.clamp(C.t / 0.15, 0, 1);
    if (a < 0.02) return;
    c.save();
    c.font = `700 32px ${FONT_TITLE}`;
    const nw = c.measureText(C.label).width;
    c.font = `800 12px ${FONT_UI}`;
    const cw = c.measureText(C.caption.toUpperCase()).width;
    const bw = Math.max(nw, cw) + 44, bh = 66;
    // em cima da cabeca; sem espaco (perto do alto da tela), embaixo dos pes
    let [hx, hy] = this.toScreen(C.fx, C.fy - C.top * 0.5 - 8);
    let below = false;
    if (hy - bh - 14 < 96) { [hx, hy] = this.toScreen(C.fx, C.fy + C.top * 0.5 + 10); below = true; }
    const bx = U.clamp(hx - bw / 2, 12, W - bw - 12), by = below ? hy + 14 : hy - bh - 14;
    const acc = C.accent || '#ec8a76';
    c.globalAlpha = a;
    c.translate(hx, below ? by : by + bh);
    c.scale(0.86 + 0.14 * pop, 0.86 + 0.14 * pop);
    c.translate(-hx, -(below ? by : by + bh));
    A.softShadow(c, bx, by, bw, bh, 18, 18, 0.28, 6, SOFT.card1);
    const gr = c.createLinearGradient(0, by, 0, by + bh);
    gr.addColorStop(0, SOFT.card1); gr.addColorStop(1, SOFT.card2);
    A.rrect(c, bx, by, bw, bh, 18, gr, U.rgba(acc, 0.75), 2.5);
    // ponteira para o personagem
    const px = U.clamp(hx, bx + 22, bx + bw - 22);
    if (below) A.poly(c, [[px - 9, by + 1], [px + 9, by + 1], [px, by - 11]], SOFT.card1, null);
    else A.poly(c, [[px - 9, by + bh - 1], [px + 9, by + bh - 1], [px, by + bh + 11]], SOFT.card2, null);
    A.text(c, C.caption.toUpperCase(), bx + bw / 2, by + 17, 12, U.shade(acc, -0.25), 'center', null, false);
    A.text(c, C.label, bx + bw / 2, by + 43, 32, U.shade(acc, -0.35), 'center', { family: FONT_TITLE, weight: 700 }, 'rgba(255,255,255,0.9)', 4);
    c.restore();
  },
};
