'use strict';
// Desenha uma fase em andamento: cenario, entidades, projeteis e efeitos.

const Render = {
  bg: null,
  bgKey: '',

  ensureBg(game, scale) {
    const key = game.levelIdx + ':' + scale.toFixed(3);
    if (this.bgKey === key && this.bg) return;
    const cv = document.createElement('canvas');
    cv.width = Math.ceil(W * scale);
    cv.height = Math.ceil(H * scale);
    const c = cv.getContext('2d');
    c.setTransform(scale, 0, 0, scale, 0, 0);
    A.terrain(c, game);
    this.bg = cv;
    this.bgKey = key;
  },

  // fundo em alta (imagem original do cenario) para quando a camera aproxima; null sem o fundo do Blender
  hiBg(g) {
    const bg = typeof SPR !== 'undefined' && SPR && SPR.bgs && SPR.bgs.get(g.levelIdx);
    return bg && bg.img && bg.img.naturalWidth > W * App.scale ? bg.img : null;
  },

  // projetil indo num boneco: o acerto do jogo fica na mesma altura (game.hitY), mas o desenho sobe junto com o
  // boneco maior (charLift) conforme chega perto do alvo
  projLift(p) {
    const e = p.target;
    if (!e || p.kind === 'bolt' || typeof charLift !== 'function') return 0;
    const lift = charLift(e);
    if (!lift) return 0;
    const w = p.T ? U.clamp(p.t / p.T, 0, 1) : U.clamp(1 - Math.hypot(p.x - e.x, p.y - e.y) / 120, 0, 1);
    return lift * w * w * (3 - 2 * w);
  },

  hpBarY(e) {
    const T = e.T;
    const top = A.enemyTop && ESPR.ready(e.type) && A.enemyTop(e);
    if (top) return top + 6;
    if (e.type === 'ifrit') return e.flying ? 132 : 104;
    if (e.flying) return FLY_H + T.size + 18;
    switch (e.type) {
      case 'golem': return 70;
      case 'warlord': return 66;
      case 'worm': return 62;
      case 'brute': return 46;
      case 'scorpion': return 36;
      case 'bulwark': return 38;
      case 'brood': return 44;
      case 'scorpling': return 20;
      case 'ifrit': return 132;
      default: return T.size * 2 + 16;
    }
  },

  // cheia: o fundo alagado (f<N>_cheia, da sessao do cenario) entra por cima com alfa = g.flood; sem ele, uma lamina
  // d'agua sobre os lotes baixos
  floodLayer(c, g, t) {
    const C = typeof SPRITE_META !== 'undefined' && SPRITE_META.cenario && SPRITE_META.cenario[g.levelIdx];
    if (C && C.cheia) {
      if (!this._cheia || this._cheia.src.indexOf(C.cheia) < 0) { this._cheia = new Image(); this._cheia.src = C.cheia; }
      if (this._cheia.complete && this._cheia.naturalWidth) {
        c.save(); c.globalAlpha = g.flood; c.drawImage(this._cheia, 0, 0, W, H); c.restore();
        return;
      }
    }
    c.save();
    for (const s of g.spots) {
      if (!s.low) continue;
      const r = 58 * g.flood;
      const gr = c.createRadialGradient(s.x, s.y, 0, s.x, s.y, r);
      gr.addColorStop(0, `rgba(96,150,170,${0.75 * g.flood})`);
      gr.addColorStop(0.75, `rgba(96,150,170,${0.55 * g.flood})`);
      gr.addColorStop(1, 'rgba(96,150,170,0)');
      c.fillStyle = gr;
      c.beginPath(); c.ellipse(s.x, s.y, r, r * 0.55, 0, 0, U.TAU); c.fill();
      c.strokeStyle = `rgba(230,245,250,${0.35 * g.flood})`; c.lineWidth = 1.5;
      c.beginPath(); c.ellipse(s.x, s.y, r * (0.6 + 0.1 * Math.sin(t * 2 + s.i)), r * 0.3, 0, 0, U.TAU); c.stroke();
    }
    c.restore();
  },

  level(c, g, v) {
    const t = g.time;
    A.clock = t;   // relogio das animacoes em laco dos sprites (espera das unidades)
    // luz das lanternas dos sprites: mais forte no Trono do Ifrit e nas tempestades
    if (typeof SPR !== 'undefined' && SPR) {
      if (SPR.level) SPR.level(g); // carrega as folhas das torres da fase e aplica o tom do clima
      const base = g.isNight() ? 0.95 : SPR.glowBase != null ? SPR.glowBase : g.L.theme === 'ember' ? 0.6 : 0.25;
      SPR.glow = base + Math.max(0, 0.6 - base) * g.stormK();
    }
    // folhas dos inimigos da fase (js/inimigos.js)
    if (typeof ESPR !== 'undefined' && this._pre !== g) {
      this._pre = g;
      ESPR.preload(g.L);
      // aliados de toda fase: heroina e guardioes (o resto carrega quando aparece)
      if (typeof USPR !== 'undefined') { USPR.want(g.H.sprite); USPR.want('soldier'); }
      // bichos libertos que a Caipora chama (onca e queixada, cores naturais)
      if (g.heroId === 'caipora') { ESPR.want('comitiva'); ESPR.want('comitiva_b'); }
    }
    // particulas e luz dinamica (js/vfx.js)
    Vfx.tick(g);
    Light.begin(g);
    Vfx.env(g, t);
    // tremor de tela
    let sx = 0, sy = 0;
    for (const f of g.fx) if (f.kind === 'shake') {
      const k = 1 - f.t / f.T;
      sx += (Math.random() - 0.5) * f.amp * 2 * k;
      sy += (Math.random() - 0.5) * f.amp * 2 * k;
    }
    c.save();
    c.translate(sx, sy);
    // camera (js/camera.js): close-up e zoom livre; o tremor fica na tela, o resto e mundo. Com zoom, o fundo vem
    // direto da imagem do Blender (3840 px) em vez do cache na resolucao da tela, para nao borrar
    const cam = v.cam && v.cam.z > 1.001 ? v.cam : null;
    if (cam) cam.apply(c);
    const hi = cam && this.hiBg(g);
    if (hi) { c.save(); c.imageSmoothingEnabled = true; c.imageSmoothingQuality = 'high'; c.drawImage(hi, 0, 0, W, H); c.restore(); }
    else c.drawImage(this.bg, 0, 0, W, H);
    if (g.flood > 0) this.floodLayer(c, g, t);
    if (A.ambient) A.ambient(c, g, t); // agua, lava e tamareiras do cenario do Blender (js/sprites.js)

    // camada do chao
    for (const f of g.fx) if (f.kind === 'scorch' || f.kind === 'stuck' || f.kind === 'chasm') { this.fx(c, f, g); Vfx.fxExtra(f, g); }
    for (const z of g.zones) { this.zone(c, z, t); Vfx.zoneExtra(z, g, t); }

    // auras dos estandartes
    for (const b of g.towers) {
      if (b.type !== 'banner' || b.disabledT > 0 || b.working) continue;
      const r = b.S.range;
      c.save();
      c.setLineDash([3, 9]); c.lineDashOffset = -t * 10;
      A.ell(c, b.x, b.y, r, r * U.YS, U.rgba(b.spec === 'watch' ? '#fff0a0' : '#ffd27a', 0.06), U.rgba(b.spec === 'watch' ? '#fff0a0' : '#ffcf5a', 0.38), 1.6);
      c.restore();
    }
    // lotes vazios (e ruinas)
    for (const s of g.spots) {
      if (s.tower) continue;
      const hov = v.hoverSpot === s || (v.sel && v.sel.spot === s);
      if (s.ruin) A.ruinSpot(c, s.x, s.y, hov, s.ruin, t);
      else A.spot(c, s.x, s.y, hov, t);
      if (s.high && !s.ruin) A.poly(c, [[s.x - 27, s.y + 11], [s.x - 22, s.y + 4], [s.x - 17, s.y + 11]], '#7fffd4', OUT, 1.2);
      // lote baixo (alaga na cheia): duas ondinhas azuis
      if (s.low && !s.ruin) for (const dy of [5, 10]) A.line(c, s.x - 29, s.y + dy, s.x - 17, s.y + dy - 2, '#5fb8e8', 2);
    }

    // alcance
    if (v.range) {
      const { x, y, r, color } = v.range;
      c.save();
      A.ell(c, x, y, r, r * U.YS, U.rgba(color || '#ffffff', 0.13));
      c.setLineDash([8, 6]); c.lineDashOffset = -t * 18;
      A.ell(c, x, y, r, r * U.YS, null, U.rgba(color || '#ffffff', 0.75), 2);
      c.restore();
    }
    if (v.rallyPreview) {
      const { x, y, ok } = v.rallyPreview;
      A.flag(c, x - 4, y + 6, 26, ok ? TEAL : '#b8432e', t);
      A.ell(c, x, y + 6, 12, 5, null, ok ? 'rgba(127,255,212,0.8)' : 'rgba(255,90,60,0.8)', 2);
    }

    // entidades ordenadas por profundidade
    const list = [];
    for (const tw of g.towers) list.push([tw.y, 0, tw]);
    for (const e of g.enemies) if (!e.flying) list.push([e.y, 1, e]);
    for (const u of g.units) if (!u.dead) list.push([u.y, 2, u]);
    for (const f of g.fx) if (f.kind === 'corpse' && !f.e.flying) list.push([f.y, 3, f]);
    for (const h of g.herd) list.push([h.y, 6, h]);
    // comportas: alavanca e portao no ramo fechado
    g.forks.forEach((f, i) => {
      list.push([f.y, 4, { f, i }]);
      const closed = g.paths[f.paths[1 - f.state]];
      const q = closed.at(f.gd, {});
      list.push([q.y, 5, q]);
    });
    list.sort((a, b) => a[0] - b[0]);
    for (const [, kind, o] of list) {
      if (kind === 0) {
        if (v.sel && v.sel.tower === o) A.ell(c, o.x, o.y + 2, 36, 15, null, 'rgba(127,255,212,0.7)', 2.5);
        A.drawTower(c, o, t);
        Vfx.tower(c, o, g, t);
        if (o.working) this.workBar(c, o, t);
        if (o.disabledT > 0) this.disabled(c, o, t);
        else if (o.bDmg > 0) this.buffMark(c, o, t);
        if (o.tarifT > 0 && !o.working && A.tarifMark) A.tarifMark(c, o, t, g);   // Tarifaco (Dudu por perto)
        if (o.rally && v.sel && v.sel.tower === o) A.flag(c, o.rally.x - 3, o.rally.y + 4, 22, TEAL, t);
      } else if (kind === 1) {
        // Pedalada Fiscal / Fuga para a Italia: sumida, vira o vulto disparando (js/satira.js)
        if (!(o.burrowed && A.burrowDash && A.burrowDash(c, o, t))) A.drawEnemy(c, o, t);
        Vfx.enemy(c, o, g, t);
        if (A.enemyPower) A.enemyPower(c, o, g, t);   // poderes dos escandalos presos no boneco
      }
      else if (kind === 2) A.drawUnit(c, o, t, v.heroSel && o.kind === 'hero');
      else if (kind === 4) A.lever(c, o.f, t, v.hoverLever === o.i);
      else if (kind === 5) A.gateBar(c, o.x, o.y, o.dx, o.dy, t);
      else if (kind === 6) A.drawHerd(c, o, t);
      else this.fx(c, o, g);
    }
    // voadores
    for (const e of g.enemies) if (e.flying) {
      A.drawEnemy(c, e, t);
      Vfx.enemy(c, e, g, t);
      if (A.enemyPower) A.enemyPower(c, e, g, t);
    }
    for (const f of g.fx) if (f.kind === 'corpse' && f.e.flying) this.fx(c, f, g);

    // feixes solares
    for (const tw of g.towers) if (tw.spec === 'sun' && tw.beam) this.sunBeam(c, tw, g, t);

    for (const p of g.projs) {
      const lift = this.projLift(p);
      if (lift) { c.save(); c.translate(0, -lift); }
      this.proj(c, p, g, t); Vfx.projExtra(p, g);
      if (lift) c.restore();
    }

    // efeitos
    for (const f of g.fx) {
      if (f.kind === 'scorch' || f.kind === 'stuck' || f.kind === 'chasm' || f.kind === 'corpse' || f.kind === 'shake' || f.kind === 'leak') continue;
      this.fx(c, f, g);
      Vfx.fxExtra(f, g);
    }

    Vfx.drawParts(c);
    Vfx.smoke(c, g, t);
    this.storm(c, g, t);
    // a luz entra depois do mundo e antes das barras de vida (que nao devem ser tingidas)
    Light.apply(c, g);
    if (A.afterLight) A.afterLight(c, g, t); // gancho para o sprites.js desenhar brilho depois da luz

    // barras de vida (a altura ja vem do topo do sprite, que cresce com o boneco; a largura acompanha)
    const CK = typeof charK === 'function' ? charK() : 1;
    for (const e of g.enemies) {
      if (!g.visible(e) || e.burrowed && e.type !== 'worm') continue;
      if (e.T.stealth && !e.revealed) continue;
      const bw = U.clamp(e.T.size * 2.1, 20, 64) * CK;
      const by = e.y - this.hpBarY(e);
      this.bar(c, e.x - bw / 2, by, bw, e.T.boss ? 6 : 4, e.hp / e.maxHp, '#e23b2e', '#7ad94a');
      let ix = e.x + bw / 2 + 4;
      if (e.poisonT > 0) { A.circ(c, ix, by + 2, 2.6, '#7fd04a', OUT, 1); ix += 6; }
      if (e.burnT > 0) { A.circ(c, ix, by + 2, 2.6, '#ff8a2a', OUT, 1); ix += 6; }
      if (e.slowT > 0) { A.circ(c, ix, by + 2, 2.6, '#7fc8ff', OUT, 1); ix += 6; }
      if (e.wetT > 0) { A.circ(c, ix, by + 2, 2.6, '#2f9fd8', OUT, 1); A.circ(c, ix - 0.8, by + 1.2, 0.8, '#dff6ff'); ix += 6; }
      if (e.armorRedT > 0) { A.rect(c, ix - 2.4, by - 0.4, 4.8, 4.8, '#a9b0b5', OUT, 1); ix += 6; }
      if (e.blindT > 0) { A.circ(c, ix, by + 2, 2.6, '#f4ecd8', OUT, 1); A.line(c, ix - 2, by + 4, ix + 2, by, '#8a6a3a', 1); ix += 6; }
      if (e.T.stealth) { A.ell(c, e.x - bw / 2 - 6, by + 2, 3.4, 2.2, '#fff8e0', OUT, 1); A.circ(c, e.x - bw / 2 - 6, by + 2, 1.1, '#1a5a56'); }
      if (v.selEnemy === e) A.ell(c, e.x, e.y + 1, (e.T.size + 8) * CK, (e.T.size + 8) * 0.42 * CK, null, 'rgba(255,90,60,0.8)', 2);
    }
    for (const u of g.units) {
      if (u.dead) continue;
      // com sprite do Blender a barra acompanha a altura real da unidade (A.unitTop)
      const top = A.unitTop && A.unitTop(u);
      if (u.kind === 'hero') {
        const hy = top ? top + 8 : 46;
        this.bar(c, u.x - 15, u.y - hy, 30, 4, u.hp / u.maxHp, '#e23b2e', '#5ad9c4');
        A.circ(c, u.x - 20, u.y - hy + 2, 6, '#1f8f8a', OUT, 1.5);
        A.text(c, String(u.level), u.x - 20, u.y - hy + 2.5, 8.5, '#fff', 'center', null, false);
      } else if (u.hp < u.maxHp - 0.5) {
        this.bar(c, u.x - 9, u.y - (top ? top + 5 : 30), 18, 3, u.hp / u.maxHp, '#e23b2e', '#9be15d');
      }
    }
    c.restore();

    // vermelho na borda quando vaza
    for (const f of g.fx) if (f.kind === 'leak') {
      const k = 1 - f.t / f.T;
      const vg = c.createRadialGradient(W / 2, H / 2, H * 0.4, W / 2, H / 2, H * 0.9);
      vg.addColorStop(0, 'rgba(200,0,0,0)');
      vg.addColorStop(1, `rgba(200,20,10,${0.35 * k})`);
      c.fillStyle = vg; c.fillRect(0, 0, W, H);
    }
  },

  // torre sabotada ou incendiada: fumaca e engrenagem riscada; sabotada por tinta (Damaris) ou greve (Pelego), a
  // tinta rosa escorre ou a placa fica fincada na frente no lugar da fumaca
  disabled(c, tw, t) {
    if (tw.sabEnd > t && A.sabMark) A.sabMark(c, tw, t, tw.sabKey, t - (tw.sabEnd - tw.sabDur), tw.sabEnd - t);
    else {
      const r = U.rng(Math.floor(t * 6) + tw.id * 13);
      c.save();
      for (let i = 0; i < 6; i++) {
        const k = (t * 0.7 + i / 6) % 1;
        c.globalAlpha = (1 - k) * 0.6;
        A.circ(c, tw.x + (r() - 0.5) * 30 + Math.sin(k * 5 + i) * 4, tw.y - 30 - k * 46, 7 + k * 9, i % 2 ? '#6a625c' : '#8a827a');
      }
      c.restore();
    }
    const y = tw.y - 108;
    A.circ(c, tw.x, y, 11, '#2a1a10', '#e8574a', 2);
    for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3 + t; A.line(c, tw.x + Math.cos(a) * 5, y + Math.sin(a) * 5, tw.x + Math.cos(a) * 8, y + Math.sin(a) * 8, '#c9c2b5', 2.2); }
    A.circ(c, tw.x, y, 3, '#c9c2b5');
    A.line(c, tw.x - 7, y - 7, tw.x + 7, y + 7, '#e8574a', 2.2);
    A.text(c, String(Math.ceil(tw.disabledT)), tw.x + 15, y - 6, 11, '#ffb0a0', 'center');
  },

  // obra: ampulheta e barra de progresso logo abaixo da plataforma
  workBar(c, tw, t) {
    const k = U.clamp(tw.buildT / tw.buildDur, 0, 1);
    const x = tw.x - 20, y = tw.y + 29;
    this.bar(c, x, y, 46, 5, k, '#4a3020', '#ffd54a');
    A.circ(c, x - 9, y + 2.5, 8, '#3a2414', OUT, 1.3);
    A.iconExtra.work(c, x - 9, y + 2.5, 7, { time: t });
  },

  buffMark(c, tw, t) {
    const x = tw.x + 24, y = tw.y + 2 + Math.sin(t * 3 + tw.id) * 1.5;
    A.poly(c, [[x - 5, y + 2], [x, y - 4], [x + 5, y + 2], [x + 3, y + 2], [x, y - 1], [x - 3, y + 2]], '#ffd54a', OUT, 1);
  },

  // tempestade de fake news (js/satira.js); sem ele, o temporal original: chuva inclinada, respingos e relampagos
  storm(c, g, t) {
    const k = g.stormK();
    if (k <= 0) return;
    if (A.fakeStorm) { A.fakeStorm(c, g, t, k); return; }
    c.save();
    c.fillStyle = `rgba(40,62,82,${0.3 * k})`;
    c.fillRect(-20, -20, W + 40, H + 40);
    const r = U.rng(7);
    // nuvens escuras rolando no alto
    for (let i = 0; i < 12; i++) {
      const rad = 140 + r() * 120;
      const x = ((r() * (W + 600) + t * (30 + r() * 30)) % (W + 600)) - 300, y = r() * H * 0.45 - 40;
      const gr = c.createRadialGradient(x, y, 0, x, y, rad);
      gr.addColorStop(0, `rgba(40,52,66,${0.32 * k})`); gr.addColorStop(1, 'rgba(40,52,66,0)');
      c.fillStyle = gr; c.fillRect(x - rad, y - rad, rad * 2, rad * 2);
    }
    // chuva
    c.lineCap = 'round';
    for (let i = 0; i < 230; i++) {
      const sp = 700 + r() * 300;
      const y = ((r() * (H + 200) + t * sp) % (H + 200)) - 100;
      const x = ((r() * (W + 300) - t * sp * 0.22) % (W + 300) + W + 300) % (W + 300) - 150;
      const l = 16 + r() * 18;
      c.strokeStyle = `rgba(205,225,245,${(0.25 + r() * 0.35) * k})`;
      c.lineWidth = 1 + r() * 0.9;
      c.beginPath(); c.moveTo(x, y); c.lineTo(x + l * 0.22, y - l); c.stroke();
    }
    // respingos
    for (let i = 0; i < 40; i++) {
      const ph = (t * 2.2 + r()) % 1;
      const x = r() * W, y = 120 + r() * (H - 140);
      c.strokeStyle = `rgba(220,235,250,${0.5 * (1 - ph) * k})`;
      c.lineWidth = 1.2;
      c.beginPath(); c.ellipse(x, y, 2 + ph * 7, (2 + ph * 7) * 0.4, 0, 0, U.TAU); c.stroke();
    }
    // relampago: um clarao curto a cada poucos segundos
    const cyc = 7.3, ph = (t % cyc) / cyc, seed = Math.floor(t / cyc);
    if (ph < 0.035 || (ph > 0.05 && ph < 0.07)) {
      const lx = 200 + U.rng(seed * 13)() * (W - 400);
      c.fillStyle = `rgba(230,240,255,${0.22 * k})`;
      c.fillRect(0, 0, W, H);
      if (typeof Light !== 'undefined') Light.add(lx, 200, 520, '#cfe2ff', 1.2 * k, 0.5);
    }
    const vg = c.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.95);
    vg.addColorStop(0, 'rgba(30,45,60,0)'); vg.addColorStop(1, `rgba(25,38,52,${0.45 * k})`);
    c.fillStyle = vg; c.fillRect(0, 0, W, H);
    c.restore();
  },

  bar(c, x, y, w, h, k, back, front) {
    A.rect(c, x - 1, y - 1, w + 2, h + 2, '#1a0d05');
    A.rect(c, x, y, w, h, back);
    A.rect(c, x, y, w * U.clamp(k, 0, 1), h, front);
    A.rect(c, x, y, w * U.clamp(k, 0, 1), h * 0.4, 'rgba(255,255,255,0.35)');
  },

  sunBeam(c, tw, g, t) {
    Vfx.sunBeam(c, tw, g, t);
  },

  zone(c, z, t) {
    const k = z.t / z.T;
    const fade = Math.min(1, (1 - k) * 4, z.t * 4);
    if (z.kind === 'oil') { if (A.fxOilSlick) A.fxOilSlick(c, z, t, fade); return; }   // Petrolao: mancha de oleo
    if (z.kind === 'fire' && z.moto && A.fxMotoZone) A.fxMotoZone(c, z, t, fade);   // Motociata: pneu e escapamento
    // torres da chapa do jogador (js/satira.js, "EFEITOS POR CHAPA")
    else if (z.kind === 'fire' && ladoV() && A.chCaramelZone) A.chCaramelZone(c, z, t, fade);     // Calda Quente
    else if (z.kind === 'tornado' && ladoR() && A.chListeners) A.chListeners(c, z, t, fade);      // Discurso de 3 Horas
    else if (z.kind === 'toxic' && ladoV() && A.chPulpZone) A.chPulpZone(c, z, t, fade);          // Nuvem de Bagaco
    else if (z.kind === 'tornado' && A.fxZapVortex) A.fxZapVortex(c, z, t, fade);   // Viralizou
    else if (z.kind === 'toxic' && A.fxNotesZone) A.fxNotesZone(c, z, t, fade);    // Chuva de Notas
    else if (z.kind === 'fire') {
      c.save();
      c.globalAlpha = fade;
      A.ell(c, z.x, z.y, z.r, z.r * U.YS, 'rgba(60,20,0,0.35)');
      A.glow(c, z.x, z.y, z.r, '#ff7a1a', 0.35);
      const r = U.rng((Math.floor(t * 14) + z.x) | 0);
      for (let i = 0; i < 16; i++) {
        const a = r() * U.TAU, d = Math.sqrt(r()) * z.r * 0.9;
        const fx = z.x + Math.cos(a) * d, fy = z.y + Math.sin(a) * d * U.YS;
        const h = 8 + r() * 12;
        c.beginPath();
        c.moveTo(fx - 4, fy);
        c.quadraticCurveTo(fx - 3, fy - h * 0.6, fx, fy - h);
        c.quadraticCurveTo(fx + 3, fy - h * 0.6, fx + 4, fy);
        c.closePath();
        c.fillStyle = r() < 0.5 ? 'rgba(255,140,30,0.85)' : 'rgba(255,210,80,0.85)';
        c.fill();
      }
      c.restore();
    } else if (z.kind === 'mud') {
      c.save();
      c.globalAlpha = fade;
      A.ell(c, z.x, z.y, z.r, z.r * U.YS, 'rgba(110,80,40,0.55)', 'rgba(70,45,20,0.6)', 2);
      A.ell(c, z.x - 8, z.y - 4, z.r * 0.55, z.r * 0.25, 'rgba(90,150,170,0.35)');
      const r = U.rng((Math.floor(t * 3) + z.x) | 0);
      for (let i = 0; i < 6; i++) A.circ(c, z.x + (r() - 0.5) * z.r * 1.4, z.y + (r() - 0.5) * z.r * 0.7, 1.5 + r() * 2.5, null, 'rgba(200,170,120,0.6)', 1);
      c.restore();
    } else if (z.kind === 'tornado') {
      c.save();
      c.globalAlpha = fade;
      A.shadow(c, z.x, z.y + 2, 26, 9, 0.3);
      for (let i = 0; i < 7; i++) {
        const kk = i / 6, rx = 8 + kk * 26, yy = z.y - kk * 70;
        const ph = t * 9 + i * 0.8;
        c.beginPath();
        c.ellipse(z.x + Math.sin(t * 4 + i) * 4, yy, rx, rx * 0.32, 0, ph % U.TAU, (ph % U.TAU) + 4.6);
        c.strokeStyle = `rgba(230,215,185,${0.9 - kk * 0.4})`; c.lineWidth = 3.2 - kk * 1.5; c.stroke();
      }
      c.restore();
    } else if (z.kind === 'toxic') {
      c.save();
      c.globalAlpha = fade * 0.85;
      for (let i = 0; i < 9; i++) {
        const a = (i / 9) * U.TAU + t * 0.4;
        const d = z.r * 0.5 + Math.sin(t * 2 + i) * 6;
        A.circ(c, z.x + Math.cos(a) * d, z.y + Math.sin(a) * d * U.YS - 8, z.r * 0.42, 'rgba(120,200,60,0.28)');
      }
      A.ell(c, z.x, z.y, z.r, z.r * U.YS, 'rgba(110,190,50,0.22)', 'rgba(90,160,40,0.5)', 1.5);
      const r = U.rng((Math.floor(t * 6) + z.y) | 0);
      for (let i = 0; i < 6; i++) A.circ(c, z.x + (r() - 0.5) * z.r * 1.4, z.y + (r() - 0.5) * z.r * 0.8 - 6, 2 + r() * 3, 'rgba(200,255,120,0.7)', 'rgba(60,110,20,0.6)', 1);
      c.restore();
    }
  },

  proj(c, p, g, t) {
    if (A.projSprite && A.projSprite(c, p, t)) return; // flecha/virote em sprite (js/sprites.js)
    // projeteis tematicos (js/satira.js): megafone/like/balao, lata de tinta/placa, saco de dinheiro, projeto de lei, o L
    if (p.kind === 'enemyArrow' && A.fxEnemyShot) { A.fxEnemyShot(c, p, t); return; }
    if (p.kind === 'pot' && A.fxThrow) { A.fxThrow(c, p, t); return; }
    if (p.kind === 'fireball' && A.fxBag) { A.fxBag(c, p, t); return; }
    if (p.kind === 'oilBarrel' && A.fxOilBarrel) { A.fxOilBarrel(c, p, t); return; }     // Petrolao
    if (p.kind === 'rouanetBag' && A.fxRouanetBag) { A.fxRouanetBag(c, p, t); return; }  // Verba da Rouanet
    if (p.kind === 'herb' && A.fxDoc) { A.fxDoc(c, p, t); return; }
    if (p.kind === 'hawk' && A.fxLHand) { A.fxLHand(c, p, t); return; }
    switch (p.kind) {
      case 'arrow': case 'enemyArrow': {
        c.save(); c.translate(p.x, p.y); c.rotate(p.ang);
        A.line(c, -9, 0, 5, 0, p.kind === 'arrow' ? '#6b4423' : '#3a2412', 1.8);
        A.poly(c, [[5, -2.2], [9, 0], [5, 2.2]], '#d0d4d8', OUT, 0.8);
        A.poly(c, [[-9, 0], [-12, -2.6], [-7, 0], [-12, 2.6]], '#efe8d8', null);
        c.restore();
        break;
      }
      case 'dart': {
        // Candidatura Laranja (Verde-Amarela): semente de laranja cuspida
        if (ladoV() && A.chSeed) { A.chSeed(c, p, t); break; }
        // Dolar na Cueca: nota de dolar enrolada (canudinho verde-acinzentado, pontas mais escuras)
        c.save(); c.translate(p.x, p.y); c.rotate(p.ang);
        A.line(c, -5, 0, 4, 0, '#5f7a55', 3.6);
        A.line(c, -4, 0, 3, 0, '#c2d2a8', 2.4);
        A.line(c, -2, -0.7, 1.5, -0.7, '#eef4e0', 0.7);
        c.restore();
        break;
      }
      case 'magic':
        Vfx.orb(c, p, g, t);
        break;
      case 'bomb': case 'bomblet': case 'barrel': case 'flask': {
        const k = Math.min(1, p.t / p.T);
        const gx = U.lerp(p.sx, p.tx, k), gy = U.lerp(p.sy + 24, p.ty, k);
        A.shadow(c, gx, gy, 7 * (0.6 + k * 0.4), 3 * (0.6 + k * 0.4), 0.25);
        c.save(); c.translate(p.x, p.y); c.rotate(p.ang);
        if ((p.kind === 'bomb' || p.kind === 'bomblet' || p.kind === 'barrel') && ladoV() && A.chCan) {
          // Leite Condensado (Verde-Amarela): lata; a da Chuva de Latinhas e menor e a da Calda Quente vem fervendo
          A.chCan(c, p.kind === 'bomblet' ? 0.55 : p.big ? 1.2 : 1, p.kind === 'barrel', t);
        } else if (p.kind === 'flask' && ladoV() && A.chHalfOrange) {
          A.chHalfOrange(c);   // Nuvem de Bagaco: meia laranja espremida
        } else if (p.kind === 'bomb' || p.kind === 'bomblet' || p.kind === 'barrel') {
          // barril de petroleo do Petrolao: preto, faixa amarela no meio e frisos; o da Chuva de Barris e menor e o do
          // Oleo em Chamas vem pegando fogo na tampa
          const s = p.kind === 'bomblet' ? 0.55 : p.big ? 1.25 : 1;
          const bw = 6.2 * s, bh = 8 * s;
          A.rrect(c, -bw, -bh, bw * 2, bh * 2, 2.4 * s, A.hgrad(c, -bw, bw, '#3a3a40', 0.3, -0.25), '#141418', 1.3);
          A.rrect(c, -bw, -1.6 * s, bw * 2, 3.2 * s, 0.8, '#f2c230');
          for (const yy of [-bh * 0.62, bh * 0.62]) A.line(c, -bw + 0.6, yy, bw - 0.6, yy, '#55555e', 1.1 * s);
          A.ell(c, 0, -bh, bw, 1.8 * s, '#2a2a30', '#141418', 1);
          A.ell(c, -bw * 0.45, -bh * 0.35, bw * 0.22, bh * 0.4, 'rgba(255,255,255,0.18)');
          if (p.kind === 'barrel') {
            A.glow(c, 0, -bh - 3, 11, '#ff8a2a', 0.9);
            A.ell(c, 0, -bh - 1.5, bw * 0.7, 2.6, '#ffb347', '#c8601e', 1);
          }
        } else {
          // maco de notas da Chuva de Notas: notas verdes com a cinta de papel
          A.rrect(c, -6.5, -4, 13, 8, 1.5, '#8ec67a', '#3f7f3a', 1.2);
          A.rrect(c, -5.5, -5.5, 13, 8, 1.5, '#a8d890', '#3f7f3a', 1);
          A.rrect(c, -1.6, -5.5, 3.2, 8, 0.6, '#f4efe2');
          A.circ(c, 4, -1.5, 1.4, '#e8f6c8');
        }
        c.restore();
        break;
      }
      case 'water': {
        // jato do igarape: fio d'agua em arco que afina no rabo, com brilho e gotas soltas
        c.save();
        const k = Math.min(1, p.t / p.T);
        const k0 = Math.max(0, k - 0.32);
        const at = kk => [U.lerp(p.sx, p.tx, kk), U.lerp(p.sy, p.ty, kk) - p.arc * 4 * kk * (1 - kk)];
        const W0 = p.big ? 6 : 4.5;
        c.lineCap = 'round';
        for (let i = 0; i < 8; i++) {
          const a0 = k0 + (k - k0) * (i / 8), a1 = k0 + (k - k0) * ((i + 1) / 8);
          const [x0, y0] = at(a0), [x1, y1] = at(a1);
          const w = W0 * (0.35 + 0.65 * (i + 1) / 8);
          c.strokeStyle = 'rgba(30,90,190,0.55)'; c.lineWidth = w + 1.6;
          c.beginPath(); c.moveTo(x0, y0); c.lineTo(x1, y1); c.stroke();
          c.strokeStyle = `rgba(110,180,250,${0.55 + 0.4 * (i / 8)})`; c.lineWidth = w;
          c.beginPath(); c.moveTo(x0, y0); c.lineTo(x1, y1); c.stroke();
          c.strokeStyle = 'rgba(235,252,255,0.7)'; c.lineWidth = Math.max(1, w * 0.3);
          c.beginPath(); c.moveTo(x0, y0 - w * 0.25); c.lineTo(x1, y1 - w * 0.25); c.stroke();
        }
        // ponta do jato com espuma de lava-jato (bolhas brancas) e gotas soltas
        A.circ(c, p.x, p.y, W0 * 0.75, '#8cc4fa', 'rgba(30,90,190,0.7)', 1);
        for (let i = 0; i < 4; i++) A.circ(c, p.x + Math.cos(i * 1.9 + t * 6) * W0 * 0.7, p.y + Math.sin(i * 1.9 + t * 6) * W0 * 0.5, W0 * 0.35, 'rgba(255,255,255,0.9)', 'rgba(150,190,230,0.6)', 0.8);
        for (let i = 0; i < 3; i++) {
          const kk = Math.max(0, k - 0.05 - i * 0.09);
          const [dx, dy] = at(kk);
          A.circ(c, dx + Math.sin(t * 20 + i) * 3, dy + 4 + i * 2, 1.3, 'rgba(225,240,255,0.85)');
        }
        c.restore();
        break;
      }
      case 'waterball': {
        A.circ(c, p.x, p.y, 8, '#4ab8d8', OUT, 1.5);
        A.circ(c, p.x - 2.5, p.y - 2.5, 2.5, '#e8fbff');
        break;
      }
      case 'gust': {
        // Carro de Som (Vermelha): ondas de som com notas (Jingle Chiclete: cor de chiclete)
        if (ladoR() && A.chSoundGust) { A.chSoundGust(c, p, t); break; }
        c.save(); c.translate(p.x, p.y); c.rotate(p.ang);
        for (let i = 0; i < 3; i++) {
          c.beginPath(); c.arc(-i * 6, 0, 9 - i * 2, -1.1, 1.1);
          c.strokeStyle = p.sand ? `rgba(240,214,110,${0.9 - i * 0.25})` : `rgba(235,248,255,${0.9 - i * 0.25})`; c.lineWidth = 2.6 - i * 0.6; c.stroke();
        }
        c.restore();
        // baloes de mensagem encaminhada levados pela rajada (sem texto: tres pontinhos); a Corrente do Zap solta
        // baloes amarelos de "repassem"
        for (let i = 0; i < 3; i++) {
          const a = t * 7 + i * 2.1;
          const back = 4 + i * 8;
          const bx = p.x - Math.cos(p.ang) * back + Math.cos(a) * 2.5, by = p.y - Math.sin(p.ang) * back + Math.sin(a * 1.3 + i) * 6;
          const w = 9 - i * 1.5, h = 6.5 - i;
          A.rrect(c, bx - w / 2, by - h / 2, w, h, 2.5, p.sand ? '#fff1a8' : (i % 2 ? '#dcf8c6' : '#ffffff'), 'rgba(40,110,90,0.7)', 1);
          A.poly(c, [[bx - w * 0.2, by + h / 2 - 0.5], [bx - w * 0.38, by + h / 2 + 2.6], [bx - w * 0.02, by + h / 2 - 0.5]], p.sand ? '#fff1a8' : '#ffffff', null);
          for (let d = -1; d <= 1; d++) A.circ(c, bx + d * w * 0.22, by, 0.75, '#3a8a6a');
        }
        break;
      }
      case 'pot': {
        c.save(); c.translate(p.x, p.y); c.rotate(p.ang * 0.5);
        A.circ(c, 0, 0, 4.5, '#b8653a', OUT, 1.2);
        A.rect(c, -1.5, -7, 3, 3, '#5a3a20', null);
        A.glow(c, 0, -8, 5, '#ffcf5a', 0.9);
        c.restore();
        break;
      }
      case 'fireball': {
        if (p.t < 0) break;
        c.save();
        c.globalCompositeOperation = 'lighter';
        A.glow(c, p.x, p.y, 22, '#ff7a1a', 0.9);
        A.circ(c, p.x, p.y, 6, '#ffe08a');
        c.restore();
        break;
      }
      case 'bolt': {
        c.save(); c.translate(p.x, p.y); c.rotate(p.ang);
        A.line(c, -16, 0, 10, 0, '#5b3a1e', 3);
        A.poly(c, [[9, -3.4], [16, 0], [9, 3.4]], '#d9dde0', OUT, 1);
        A.poly(c, [[-16, 0], [-20, -4], [-12, 0], [-20, 4]], '#c62f2f', null);
        if (p.exp) A.glow(c, 12, 0, 10, '#ff9a3a', 0.8);
        c.restore();
        break;
      }
      case 'herb': {
        // ramo de arruda girando no ar (Benzedeira)
        c.save(); c.translate(p.x, p.y); c.rotate(t * 14 + p.sx);
        A.line(c, -6, 0, 6, 0, '#4f7a2a', 1.6);
        for (const [lx, s] of [[-3, 1], [0, -1], [3, 1], [5, -1]]) A.ell(c, lx, s * 2.4, 2.6, 1.5, s > 0 ? '#7cbc5c' : '#9fd36a', null);
        c.restore();
        A.glow(c, p.x, p.y, 8, '#e6ff7a', 0.35);
        break;
      }
      case 'hawk': {
        const f = Math.sin(t * 22);
        c.save(); c.translate(p.x, p.y);
        if (Math.cos(p.ang) < 0) c.scale(-1, 1);
        A.poly(c, [[-8, 0], [0, -3], [8, 0], [0, 3]], '#7a5a3a', OUT, 1.2);
        A.poly(c, [[-3, -1], [-6, -10 - f * 4], [3, -2]], '#9a7a52', OUT, 1);
        A.poly(c, [[-3, 1], [-7, 9 + f * 3], [3, 2]], '#6a4a2a', OUT, 1);
        A.circ(c, 7, -1, 2.4, '#efe2c8', OUT, 1);
        A.poly(c, [[9, -1.5], [12, 0], [9, 0.8]], '#e8c25a', null);
        c.restore();
        break;
      }
    }
  },

  fx(c, f, g) {
    const k = f.t / f.T;
    if (A.fxSprite && A.fxSprite(c, f, k)) return; // flecha cravada e impacto em sprite (js/sprites.js)
    if (A.fxPoder && A.fxPoder(c, f, k, g)) return; // poderes dos escandalos dos adversarios (js/satira.js)
    // efeitos tematicos (js/satira.js)
    switch (f.kind) {
      case 'lpop': A.fxLPop(c, f, k); return;          // impacto do Faz o L
      case 'shout': A.fxShout(c, f, k); return;        // Imbrochavel!
      case 'cash':                                     // Mala Estourada / saco do Fundao
        if (f.torre && ladoV() && A.chJuice) A.chJuice(c, f, k);   // Suco Estourado do Laranjao
        else A.fxCash(c, f, k);
        return;
      case 'confetti': A.fxConfetti(c, f, k); return;  // chefe derrotado
      case 'court': A.fxCourt(c, f, k); return;        // Entrou com recurso!
      case 'poof': A.fxPoof(c, f, k); return;          // entrando e saindo do chao
      case 'sabhit': A.fxSabHit(c, f, k); return;      // tinta rosa / placa de greve
      case 'scorch': if (A.fxSkid) { A.fxSkid(c, f, k); return; } break;
      case 'chasm':
        if (ladoV() && A.chPudim) { A.chPudim(c, f, k, g.time); return; }   // Forma de Pudim
        if (A.fxOilChasm) { A.fxOilChasm(c, f, k, g.time); return; }
        break;
      case 'sandburst':
        if (ladoR() && A.chJingleBurst) { A.chJingleBurst(c, f, k); return; }   // Jingle Chiclete
        if (A.fxZapBurst) { A.fxZapBurst(c, f, k); return; }
        break;
      case 'gustHit': if (ladoR() && A.chJingleBurst) { A.chJingleBurst(c, f, k); return; } break;   // Carro de Som
      case 'explosion': if (ladoV() && A.chMilkSplash) { A.chMilkSplash(c, f, k); return; } break;  // lata estourando
      case 'quake': if (ladoV() && A.chQuake) { A.chQuake(c, f, k); return; } break;                // Batedeira
      case 'coins': if (ladoR() && A.chParcels) { A.chParcels(c, f, k); return; } break;            // Taxa das Blusinhas
      case 'skybolt':
        if (f.small && ladoR() && A.chSkewerDrop) {
          // Picanha pra Todos: espeto caindo da nuvem de fumaca
          A.chSkewerDrop(c, f, k, g.time);
          if (k > 0.3) Light.add(f.x, f.y - 6, 120, '#ffb070', 1.1 * (1 - k) * (1 - k), 0.5);
          return;
        }
        if (f.small && A.fxDiamond) {
          A.fxDiamond(c, f, k);
          if (k > 0.3) Light.add(f.x, f.y - 6, 120, '#cfefff', 1.1 * (1 - k) * (1 - k), 0.5);
          return;
        }
        break;
    }
    switch (f.kind) {
      case 'text': {
        const y = f.y - U.easeOutCubic(Math.min(1, k * 1.5)) * 26;
        c.save();
        c.globalAlpha = k > 0.7 ? (1 - k) / 0.3 : 1;
        const s = k < 0.15 ? 0.6 + (k / 0.15) * 0.4 : 1;
        A.text(c, f.str, f.x, y, f.size * s, f.color, 'center', { family: FONT_UI, weight: 900 });
        c.restore();
        break;
      }
      case 'dust': {
        const r = U.rng((f.x * 13 + f.y) | 0);
        c.save();
        c.globalAlpha = (1 - k) * 0.7;
        for (let i = 0; i < 8; i++) {
          const a = r() * U.TAU, d = f.r * (0.3 + k * 0.7) * (0.6 + r() * 0.4);
          A.circ(c, f.x + Math.cos(a) * d, f.y + Math.sin(a) * d * 0.5 - k * 10, 5 + r() * 6 + k * 6, '#d6bf96');
        }
        c.restore();
        break;
      }
      case 'sparkle': {
        const r = U.rng((f.x * 7 + f.y) | 0);
        c.save();
        c.globalAlpha = 1 - k;
        for (let i = 0; i < 9; i++) {
          const a = r() * U.TAU, d = 10 + k * 34 * (0.5 + r());
          A.star(c, f.x + Math.cos(a) * d, f.y + Math.sin(a) * d * 0.6 - k * 20, 3 + r() * 3, '#ffe27a', null);
        }
        c.restore();
        break;
      }
      case 'corpse': {
        const e = f.e;
        if (A.enemyCorpse && A.enemyCorpse(c, f, k)) break; // morte/libertacao em sprite (js/inimigos.js)
        const fn = A.enemy[e.type];
        if (!fn || e.type === 'worm') break;
        c.save();
        c.translate(e.x, e.y + k * 4);
        c.globalAlpha = 1 - k;
        if (e.facing < 0) c.scale(-1, 1);
        c.rotate(-k * 0.5 * (e.flying ? 2 : 1));
        if (e.flying) c.translate(0, k * FLY_H);
        fn(c, { type: e.type, id: 1, moving: false, walk: e.walk, atkAnim: 0, castAnim: 0, facing: 1, flying: e.flying }, g.time);
        c.restore();
        break;
      }
      case 'coin': {
        c.save();
        c.globalAlpha = k > 0.6 ? (1 - k) / 0.4 : 1;
        const y = f.y - U.easeOutCubic(Math.min(1, k * 2)) * 22;
        A.coin(c, f.x, y, 6);
        c.restore();
        break;
      }
      case 'explosion': {
        const r = f.r;
        c.save();
        if (k < 0.35) {
          const kk = k / 0.35;
          c.globalCompositeOperation = 'lighter';
          A.glow(c, f.x, f.y - 6, r * (0.6 + kk * 0.6), f.fire ? '#ff7a1a' : '#ffe2a8', (f.fire ? 1 : 0.6) * (1 - kk));
          A.ell(c, f.x, f.y - 4, r * (0.3 + kk * 0.5), r * (0.3 + kk * 0.5) * 0.7, `rgba(255,240,180,${1 - kk})`);
          c.globalCompositeOperation = 'source-over';
        }
        const rr = U.rng((f.x * 3 + f.y * 7) | 0);
        c.globalAlpha = 1 - k;
        // fumaca escura do barril estourando
        for (let i = 0; i < 9; i++) {
          const a = rr() * U.TAU, d = r * (0.2 + 0.6 * U.easeOutCubic(k)) * (0.5 + rr() * 0.5);
          A.circ(c, f.x + Math.cos(a) * d, f.y + Math.sin(a) * d * 0.6 - k * 22 - 6, r * 0.18 + k * r * 0.18,
            f.fire && k < 0.25 ? '#ff9a3a' : U.rgba(k < 0.2 ? '#6a6670' : '#4a4650', 0.7));
        }
        // respingos de oleo preto voando e caindo
        for (let i = 0; i < 7; i++) {
          const a = rr() * U.TAU, d = r * U.easeOutCubic(k) * (0.8 + rr() * 0.6);
          const hgt = Math.sin(k * Math.PI) * 30 * (0.4 + rr());
          const sz = 2.4 + rr() * 2.2;
          A.ell(c, f.x + Math.cos(a) * d, f.y + Math.sin(a) * d * 0.5 - hgt, sz, sz * 0.8, '#17161b');
          A.circ(c, f.x + Math.cos(a) * d - sz * 0.3, f.y + Math.sin(a) * d * 0.5 - hgt - sz * 0.3, sz * 0.3, 'rgba(255,255,255,0.35)');
        }
        // poca de oleo no chao
        if (k > 0.2) A.ell(c, f.x, f.y + 2, r * 0.42, r * 0.17, `rgba(20,18,24,${0.45 * (1 - k)})`);
        c.restore();
        break;
      }
      case 'hit': {
        c.save();
        c.globalAlpha = 1 - k;
        const n = f.big ? 8 : 5, rr = (f.big ? 16 : f.small ? 7 : 10) * (0.5 + k);
        for (let i = 0; i < n; i++) {
          const a = (i / n) * U.TAU + f.x;
          A.line(c, f.x + Math.cos(a) * rr * 0.4, f.y + Math.sin(a) * rr * 0.4, f.x + Math.cos(a) * rr, f.y + Math.sin(a) * rr, '#fff6c8', 1.8);
        }
        c.restore();
        break;
      }
      case 'magicHit':
        Vfx.magicHit(c, f, g);
        break;
      case 'stuck': {
        c.save();
        c.globalAlpha = k > 0.6 ? (1 - k) / 0.4 : 1;
        c.translate(f.x, f.y);
        c.rotate(f.ang * 0.4 + 0.9);
        if (f.dart && ladoV() && A.chSeedStuck) A.chSeedStuck(c);   // semente de laranja no chao
        else if (f.dart) {
          // nota de dolar enrolada espetada no chao (Dolar na Cueca)
          A.line(c, 0, 0, 0, -8, '#5f7a55', 3.4);
          A.line(c, 0, -1, 0, -7, '#c2d2a8', 2.2);
        } else {
          A.line(c, 0, 0, 0, -9, '#6b4423', 1.6);
          A.poly(c, [[0, -9], [-2.5, -12], [2.5, -12]], '#efe8d8', null);
        }
        c.restore();
        break;
      }
      case 'lightning':
        Vfx.lightning(c, f, g);
        break;
      case 'skybolt': {
        if (!f.small) { A.pfDrop(c, f, k); break; }
        c.save();
        c.globalCompositeOperation = 'lighter';
        const a = 1 - k;
        const r = U.rng((f.x * 31 + f.y) | 0);
        const pts = [[f.x + (r() - 0.5) * 40, f.y - 420]];
        for (let i = 1; i < 12; i++) pts.push([U.lerp(pts[0][0], f.x, i / 12) + (r() - 0.5) * 26, U.lerp(f.y - 420, f.y, i / 12)]);
        pts.push([f.x, f.y]);
        const w = f.small ? 0.6 : 1;
        for (const [lw, col] of [[14 * w, `rgba(120,180,255,${0.3 * a})`], [5 * w, `rgba(200,230,255,${0.9 * a})`], [2 * w, `rgba(255,255,255,${a})`]]) {
          c.beginPath(); c.moveTo(pts[0][0], pts[0][1]);
          for (const p of pts) c.lineTo(p[0], p[1]);
          c.strokeStyle = col; c.lineWidth = lw; c.lineJoin = 'round'; c.stroke();
        }
        A.glow(c, f.x, f.y, (f.small ? 30 : 60) * (0.6 + k), '#bfe0ff', a);
        c.restore();
        Light.add(f.x, f.y, f.small ? 150 : 280, '#9fd0ff', (f.small ? 1 : 1.5) * a * a, 0.6);
        if (!f.small) {
          c.save(); c.globalAlpha = a;
          A.ell(c, f.x, f.y, 30 + k * 40, (30 + k * 40) * 0.45, null, 'rgba(255,255,255,0.8)', 3);
          c.restore();
        }
        break;
      }
      case 'scorch': {
        c.save();
        c.globalAlpha = (1 - k) * 0.55;
        A.ell(c, f.x, f.y, 26, 11, '#2a1a10');
        A.ell(c, f.x, f.y, 16, 7, '#1a0d05');
        c.restore();
        break;
      }
      case 'stars': {
        const e = f.e;
        if (e.dead) break;
        const y = e.y - (e.flying ? FLY_H + e.T.size + 8 : e.T.size * 2 + 6);
        for (let i = 0; i < 3; i++) {
          const a = g.time * 6 + (i / 3) * U.TAU;
          A.star(c, e.x + Math.cos(a) * 9, y + Math.sin(a) * 3, 3.2, '#ffe45a', OUT);
        }
        break;
      }
      case 'whirl': {
        c.save();
        c.globalAlpha = 1 - k;
        for (let i = 0; i < 3; i++) {
          const a0 = k * 14 + i * 2.1;
          c.beginPath();
          c.ellipse(f.x, f.y - 10, 36 + i * 8, (36 + i * 8) * 0.45, 0, a0, a0 + 2);
          c.strokeStyle = i === 0 ? '#ffffff' : 'rgba(180,240,230,0.8)'; c.lineWidth = 3.5 - i; c.stroke();
        }
        c.restore();
        break;
      }
      case 'levelup': {
        c.save();
        c.globalAlpha = 1 - k;
        for (let i = 0; i < 3; i++) {
          const kk = (k + i * 0.2) % 1;
          A.ell(c, f.x, f.y - kk * 40, 18 + kk * 10, 7 + kk * 4, null, '#7fffd4', 2.5);
        }
        A.glow(c, f.x, f.y - 20, 40, '#7fffd4', 0.4 * (1 - k));
        c.restore();
        break;
      }
      case 'heal': {
        const r = U.rng((f.x * 5 + f.y * 3) | 0);
        c.save();
        c.globalAlpha = 1 - k;
        for (let i = 0; i < 6; i++) {
          const px = f.x + (r() - 0.5) * 40, py = f.y - 10 - r() * 20 - k * 26;
          A.rect(c, px - 1.5, py - 4, 3, 8, '#7af06a');
          A.rect(c, px - 4, py - 1.5, 8, 3, '#7af06a');
        }
        c.restore();
        break;
      }
      case 'enemyHeal': {
        c.save();
        c.globalAlpha = (1 - k) * 0.8;
        A.ell(c, f.x, f.y, f.r * k, f.r * k * U.YS, U.rgba('#c8ff6a', 0.15), '#c8ff6a', 2.5);
        c.restore();
        break;
      }
      case 'ring': {
        c.save();
        c.globalAlpha = 1 - k;
        A.ell(c, f.x, f.y, f.r * (0.4 + k * 0.6), f.r * (0.4 + k * 0.6) * U.YS, null, f.color, 3);
        c.restore();
        break;
      }
      case 'quake': {
        c.save();
        c.globalAlpha = (1 - k) * 0.8;
        const rr = f.r * U.easeOutCubic(k);
        A.ell(c, f.x, f.y, rr, rr * U.YS, null, '#b08a5a', 6 * (1 - k) + 1);
        A.ell(c, f.x, f.y, rr * 0.8, rr * 0.8 * U.YS, null, 'rgba(255,220,160,0.6)', 2);
        const r = U.rng((f.x + f.y) | 0);
        for (let i = 0; i < 12; i++) {
          const a = r() * U.TAU;
          A.rect(c, f.x + Math.cos(a) * rr - 2, f.y + Math.sin(a) * rr * U.YS - Math.sin(k * Math.PI) * 14 * r() - 2, 4, 4, '#7a5a3a');
        }
        c.restore();
        break;
      }
      case 'flash':
        Vfx.flash(c, f, g);
        break;
      case 'cloud':
        Vfx.cloud(c, f, g, g.time);
        break;
      case 'chasm': {
        c.save();
        const open = Math.sin(Math.min(1, k) * Math.PI);
        A.ell(c, f.x, f.y, 30 * open + 2, 12 * open + 1, '#140804', OUT, 2);
        A.glow(c, f.x, f.y, 26 * open, '#ff5a1a', 0.5 * open);
        c.restore();
        break;
      }
      case 'dirt': {
        const r = U.rng((f.x * 11 + f.y * 5) | 0);
        const n = f.big ? 18 : 9;
        c.save();
        c.globalAlpha = 1 - k;
        for (let i = 0; i < n; i++) {
          const a = -Math.PI * r(), sp = (f.big ? 60 : 30) * (0.5 + r());
          const px = f.x + Math.cos(a) * sp * k, py = f.y + Math.sin(a) * sp * k + 60 * k * k;
          A.circ(c, px, py, (f.big ? 4 : 2.5) + r() * 2, '#a8834e', OUT, 0.8);
        }
        c.restore();
        break;
      }
      case 'miss': {
        c.save();
        c.globalAlpha = 1 - k;
        A.text(c, 'Esquiva', f.x, f.y - k * 14, 11, '#bfe8ff', 'center');
        c.restore();
        break;
      }
      case 'steam': {
        c.save(); c.globalAlpha = (1 - k) * 0.7;
        for (let i = 0; i < 4; i++) A.circ(c, f.x + (i - 1.5) * 6, f.y - k * 24 - i * 3, 4 + k * 6, '#f4f2ee');
        c.restore();
        break;
      }
      case 'ice': {
        const e = f.e;
        if (e.dead || !(e.frozenT > 0)) break;
        c.save();
        c.globalAlpha = 0.85;
        const y = g.hitYV ? g.hitYV(e) : g.hitY(e);
        for (let i = 0; i < 5; i++) {
          const a = (i / 5) * U.TAU + 0.3, rr = e.T.size * 0.9;
          const x0 = e.x + Math.cos(a) * rr, y0 = y + Math.sin(a) * rr * 0.7;
          A.poly(c, [[x0, y0 - 6], [x0 + 3, y0], [x0, y0 + 4], [x0 - 3, y0]], 'rgba(200,240,255,0.85)', '#5a9ac0', 1);
        }
        c.restore();
        break;
      }
      case 'splash': case 'splashBig': {
        const n = f.kind === 'splashBig' ? 12 : 7;
        const rr = U.rng((f.x * 7 + f.y) | 0);
        c.save();
        c.globalAlpha = 1 - k;
        A.ell(c, f.x, f.y, f.r * (0.4 + k * 0.6), f.r * (0.4 + k * 0.6) * U.YS, 'rgba(90,190,220,0.2)', 'rgba(150,225,240,0.8)', 2);
        for (let i = 0; i < n; i++) {
          const a = -Math.PI * rr(), sp = (f.kind === 'splashBig' ? 40 : 24) * (0.5 + rr());
          A.circ(c, f.x + Math.cos(a) * sp * k, f.y - 10 + Math.sin(a) * sp * k + 50 * k * k, 2.2, '#8fe0ea', OUT, 0.7);
        }
        c.restore();
        break;
      }
      case 'jet': {
        c.save();
        c.globalAlpha = 1 - k;
        c.lineCap = 'round';
        for (const [w, col] of [[9, 'rgba(60,170,210,0.45)'], [4.5, 'rgba(150,230,245,0.95)'], [1.6, '#ffffff']]) {
          c.beginPath(); c.moveTo(f.x0, f.y0);
          c.quadraticCurveTo((f.x0 + f.x1) / 2, Math.min(f.y0, f.y1) - 24, f.x1, f.y1);
          c.strokeStyle = col; c.lineWidth = w; c.stroke();
        }
        A.glow(c, f.x1, f.y1, 14, '#bff4ff', 0.8);
        c.restore();
        break;
      }
      case 'geyserWarn': {
        c.save();
        c.globalAlpha = 0.5 + k * 0.5;
        A.ell(c, f.x, f.y, 26 + k * 14, (26 + k * 14) * U.YS, 'rgba(60,40,20,0.35)', 'rgba(150,225,240,0.9)', 2);
        const rr = U.rng(Math.floor(g.time * 20));
        for (let i = 0; i < 5; i++) A.circ(c, f.x + (rr() - 0.5) * 40, f.y + (rr() - 0.5) * 16, 2 + rr() * 2, null, '#bff4ff', 1.2);
        c.restore();
        break;
      }
      case 'geyser': {
        const h = 110 * Math.sin(Math.min(1, k * 1.6) * Math.PI * 0.5) * (1 - Math.max(0, k - 0.6) / 0.4);
        c.save();
        c.globalAlpha = 1 - Math.max(0, k - 0.6) / 0.4;
        const gr = c.createLinearGradient(0, f.y - h, 0, f.y);
        gr.addColorStop(0, 'rgba(230,250,255,0.9)'); gr.addColorStop(1, 'rgba(70,180,215,0.9)');
        c.fillStyle = gr;
        c.beginPath();
        c.moveTo(f.x - 14, f.y);
        c.quadraticCurveTo(f.x - 8, f.y - h * 0.6, f.x - 4 + Math.sin(g.time * 20) * 2, f.y - h);
        c.lineTo(f.x + 4, f.y - h);
        c.quadraticCurveTo(f.x + 8, f.y - h * 0.6, f.x + 14, f.y);
        c.closePath(); c.fill();
        for (let i = 0; i < 8; i++) A.circ(c, f.x + Math.cos(i) * (10 + k * 30), f.y - h + Math.sin(i * 2) * 10 + k * 40, 3, '#dff6ff', OUT, 0.7);
        A.ell(c, f.x, f.y, 30, 30 * U.YS, null, 'rgba(150,225,240,0.8)', 2);
        c.restore();
        break;
      }
      case 'gustHit': case 'sandburst': {
        c.save();
        c.globalAlpha = 1 - k;
        const sand = f.kind === 'sandburst';
        for (let i = 0; i < 3; i++) {
          const rr = f.r * (0.3 + k * 0.7) * (1 - i * 0.2);
          const a0 = k * 6 + i * 2;
          c.beginPath(); c.ellipse(f.x, f.y - 10, rr, rr * 0.45, 0, a0, a0 + 3.6);
          c.strokeStyle = sand ? 'rgba(232,200,140,0.9)' : 'rgba(235,248,255,0.85)'; c.lineWidth = 3 - i; c.stroke();
        }
        if (sand) {
          const r2 = U.rng((f.x * 3 + f.y) | 0);
          for (let i = 0; i < 12; i++) A.circ(c, f.x + (r2() - 0.5) * f.r * 2 * (0.5 + k), f.y - 10 + (r2() - 0.5) * f.r * (0.5 + k), 1.5 + r2(), '#e8c890');
        }
        c.restore();
        break;
      }
      case 'smoke': {
        const rr = U.rng((f.x * 5 + f.y) | 0);
        c.save();
        c.globalAlpha = (1 - k) * 0.8;
        for (let i = 0; i < 9; i++) {
          const a = rr() * U.TAU, d = 8 + k * 30 * rr();
          A.circ(c, f.x + Math.cos(a) * d, f.y + Math.sin(a) * d * 0.5 - k * 20, 6 + k * 12, f.fire ? (i % 2 ? '#5a3a2a' : '#ff8a3a') : (i % 2 ? '#7a7570' : '#a8a29a'));
        }
        c.restore();
        break;
      }
      case 'coins': {
        c.save();
        for (let i = 0; i < 6; i++) {
          const a = -Math.PI / 2 + (i - 2.5) * 0.35, sp = 40 + i * 6;
          c.globalAlpha = 1 - k;
          A.coin(c, f.x + Math.cos(a) * sp * k, f.y + Math.sin(a) * sp * k + 70 * k * k, 4);
        }
        c.restore();
        break;
      }
      case 'drops': {
        c.save();
        c.globalAlpha = 1 - k;
        for (let i = 0; i < 5; i++) {
          const a = (i / 5) * U.TAU, d = 10 + k * 26;
          A.circ(c, f.x + Math.cos(a) * d, f.y + Math.sin(a) * d * 0.5 + k * 10, 2.2, '#8fe0ea', OUT, 0.7);
        }
        c.restore();
        break;
      }
      case 'mark': {
        const e = f.e;
        if (e.dead || !(e.markT > 0)) break;
        const y = e.y - this.hpBarY(e) - 12;
        c.save();
        c.translate(e.x, y);
        c.rotate(g.time * 2);
        A.circ(c, 0, 0, 7, null, '#e04848', 2);
        for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2; A.line(c, Math.cos(a) * 4, Math.sin(a) * 4, Math.cos(a) * 10, Math.sin(a) * 10, '#e04848', 1.8); }
        c.restore();
        break;
      }
      case 'block': {
        c.save();
        c.globalAlpha = 1 - k;
        A.glow(c, f.x, f.y, 12, '#fff4c0', 0.8);
        for (let i = 0; i < 5; i++) { const a = (i / 5) * U.TAU + f.x; A.line(c, f.x + Math.cos(a) * 3, f.y + Math.sin(a) * 3, f.x + Math.cos(a) * 9, f.y + Math.sin(a) * 9, '#ffe9a0', 1.6); }
        c.restore();
        break;
      }
      case 'flag': {
        const s = U.easeOutBack(Math.min(1, k * 2));
        c.save();
        c.globalAlpha = 1 - Math.max(0, k - 0.6) / 0.4;
        c.translate(f.x, f.y);
        c.scale(1, s);
        A.flag(c, -3, 4, 22, TEAL, g.time);
        c.restore();
        break;
      }
    }
  },
};
