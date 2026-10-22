'use strict';
// Efeitos proprios da satira (desenhados por codigo, por cima do motor do Guardioes).

// Operacao da PF: a viatura cai do ceu na area escolhida, bate no chao levantando poeira e a sirene pisca azul e
// vermelho ate sumir. k: 0..1 da vida do efeito (o dano acontece na hora, no game.furyStrike)
A.pfDrop = (c, f, k) => {
  const x = f.x, y = f.y;
  const fall = Math.min(1, k / 0.36);
  const e = fall * fall;
  const imp = Math.max(0, (k - 0.36) / 0.64);
  const fade = imp > 0.7 ? 1 - (imp - 0.7) / 0.3 : 1;
  const bump = imp > 0 ? Math.sin(Math.PI * Math.min(1, imp * 4)) : 0;
  const cy = y - 420 * (1 - e) - 8 * bump;
  c.save();
  c.globalAlpha = fade;
  // sombra crescendo no chao conforme a viatura chega
  A.ell(c, x, y + 3, 36 * (0.35 + 0.65 * e), 12 * (0.35 + 0.65 * e), 'rgba(20,20,30,0.32)');
  // poeira do impacto
  if (imp > 0) {
    for (let i = 0; i < 9; i++) {
      const a = (i / 9) * U.TAU + 0.3;
      const r = 14 + 46 * Math.sqrt(imp);
      A.circ(c, x + Math.cos(a) * r, y + Math.sin(a) * r * 0.42 - 4, 9 * (1 - imp) + 3, `rgba(214,190,150,${0.55 * (1 - imp)})`);
    }
  }
  // viatura: carroceria preta, faixa branca, cabine com vidros, rodas e giroflex
  c.translate(x, cy);
  c.scale(1 + 0.14 * bump, 1 - 0.14 * bump);
  A.rrect(c, -31, -24, 62, 20, 7, '#1f2430', '#0e1118', 2);
  A.rrect(c, -31, -15, 62, 5, 2, '#f2f2f2');
  A.rrect(c, -17, -36, 34, 15, 6, '#2a3140', '#0e1118', 2);
  A.rrect(c, -13, -33, 12, 9, 3, '#9fc6e8');
  A.rrect(c, 1, -33, 12, 9, 3, '#9fc6e8');
  for (const wx of [-18, 18]) {
    A.circ(c, wx, -4, 7, '#15171c');
    A.circ(c, wx, -4, 3, '#8a8f99');
  }
  const pisca = Math.floor(k * 18) % 2;
  A.rrect(c, -10, -42, 9, 6, 2, pisca ? '#4a7bff' : '#22356f');
  A.rrect(c, 1, -42, 9, 6, 2, pisca ? '#6b1f1f' : '#ff4a4a');
  c.restore();
  // luz da sirene no chao e no ar
  c.save();
  c.globalCompositeOperation = 'lighter';
  A.glow(c, x - 6, cy - 40, 22, '#4a7bff', (pisca ? 0.9 : 0.25) * fade);
  A.glow(c, x + 6, cy - 40, 22, '#ff4a4a', (pisca ? 0.25 : 0.9) * fade);
  c.restore();
  if (typeof Light !== 'undefined') Light.add(x, y - 10, 120, pisca ? '#4a7bff' : '#ff4a4a', 0.45 * fade, 0.6);
};

// ------------------------------------------------------------ MOTION E EFEITOS ESPECIAIS TEMATICOS
// Tudo desenhado por codigo, sem gradiente nem array por quadro nos lacos: o sorteio e deterministico (rnd) a partir
// da posicao do efeito, entao cada efeito repete o mesmo desenho a cada quadro e so o tempo (k) anda.
(function () {
  // sorteio fixo 0..1 (i = indice da peca, s = semente do efeito)
  const rnd = (i, s) => { const v = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - Math.floor(v); };
  const eo = U.easeOutCubic;
  const CHAPAS = ['#1f9a4c', '#ffd21f', '#2453c4', '#d6282b', '#ffffff'];
  const flipOf = v => (v < 0 ? Math.min(-0.18, v) : Math.max(0.18, v));

  const star4 = (c, x, y, r) => {
    c.beginPath();
    c.moveTo(x, y - r);
    c.quadraticCurveTo(x, y, x + r, y);
    c.quadraticCurveTo(x, y, x, y + r);
    c.quadraticCurveTo(x, y, x - r, y);
    c.quadraticCurveTo(x, y, x, y - r);
    c.fill();
  };
  const star5 = (c, x, y, r) => {
    c.beginPath();
    for (let i = 0; i < 10; i++) {
      const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r;
      if (i) c.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); else c.moveTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr);
    }
    c.closePath();
  };
  const heartPath = (c, x, y, r) => {
    c.beginPath();
    c.moveTo(x, y + r * 0.9);
    c.bezierCurveTo(x - r * 1.4, y - r * 0.1, x - r * 0.7, y - r * 1.1, x, y - r * 0.35);
    c.bezierCurveTo(x + r * 0.7, y - r * 1.1, x + r * 1.4, y - r * 0.1, x, y + r * 0.9);
    c.closePath();
  };
  // nota de dinheiro verde com o oval claro; fx < 0 espelha (a nota virando no ar)
  const note = (c, x, y, w, h, rot, fx) => {
    c.save();
    c.translate(x, y); c.rotate(rot); c.scale(flipOf(fx), 1);
    c.fillStyle = fx < 0 ? '#7db86a' : '#8ec67a'; c.fillRect(-w / 2, -h / 2, w, h);
    c.strokeStyle = '#3f7f3a'; c.lineWidth = 1; c.strokeRect(-w / 2, -h / 2, w, h);
    c.fillStyle = '#d4ecbf';
    c.beginPath(); c.ellipse(0, 0, h * 0.42, h * 0.33, 0, 0, U.TAU); c.fill();
    c.restore();
  };
  // folha de papel (processo, projeto de lei) com linhas de texto cinza
  const paper = (c, x, y, w, h, rot, fx) => {
    c.save();
    c.translate(x, y); c.rotate(rot); c.scale(flipOf(fx), 1);
    c.fillStyle = fx < 0 ? '#e8e5da' : '#fbfaf4'; c.fillRect(-w / 2, -h / 2, w, h);
    c.strokeStyle = '#7d828c'; c.lineWidth = 0.9; c.strokeRect(-w / 2, -h / 2, w, h);
    c.strokeStyle = '#a9aeb8'; c.beginPath();
    for (let i = 1; i <= 3; i++) { const yy = -h / 2 + h * i / 4.2; c.moveTo(-w / 2 + 1.5, yy); c.lineTo(w / 2 - 1.5 - (i === 3 ? w * 0.3 : 0), yy); }
    c.stroke();
    c.restore();
  };
  // balao de conversa com os tres pontinhos
  const bubble = (c, x, y, w, h, fill, line) => {
    A.rrect(c, x - w / 2, y - h / 2, w, h, Math.min(h * 0.45, 4), fill, line, 1);
    c.beginPath(); c.moveTo(x - w * 0.24, y + h / 2 - 0.8); c.lineTo(x - w * 0.38, y + h / 2 + h * 0.38); c.lineTo(x - w * 0.02, y + h / 2 - 0.8); c.closePath();
    c.fillStyle = fill; c.fill();
    const dr = Math.max(0.6, h * 0.1);
    c.fillStyle = line;
    c.beginPath();
    for (let d = -1; d <= 1; d++) { c.moveTo(x + d * w * 0.22 + dr, y); c.arc(x + d * w * 0.22, y, dr, 0, U.TAU); }
    c.fill();
  };
  // pedacinho de confete (retangulo girando e virando)
  const chip = (c, x, y, w, h, rot, sx, col) => {
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(flipOf(sx), 1);
    c.fillStyle = col; c.fillRect(-w / 2, -h / 2, w, h);
    c.restore();
  };
  // carimbo de madeira com a base vermelha
  const stamp = (c, x, y, s) => {
    A.rect(c, x - 1.2 * s, y - 6 * s, 2.4 * s, 4.5 * s, '#8a5a32');
    A.circ(c, x, y - 7 * s, 2.6 * s, '#a0683a', OUT, 1);
    A.rrect(c, x - 5 * s, y - 2 * s, 10 * s, 3.6 * s, 1, '#7a4e2c', OUT, 1);
    A.rect(c, x - 4.6 * s, y + 1.6 * s, 9.2 * s, 1.6 * s, '#c8323a');
  };
  // diamante lapidado
  const gem = (c, x, y, s, rot) => {
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s);
    c.beginPath(); c.moveTo(-5, -2); c.lineTo(-2.6, -5); c.lineTo(2.6, -5); c.lineTo(5, -2); c.lineTo(0, 6); c.closePath();
    c.fillStyle = '#bff0ff'; c.fill(); c.lineWidth = 1.2; c.strokeStyle = '#2f6f9f'; c.lineJoin = 'round'; c.stroke();
    c.beginPath(); c.moveTo(-5, -2); c.lineTo(5, -2); c.moveTo(-1.3, -5); c.lineTo(-2.2, -2); c.lineTo(0, 6); c.lineTo(2.2, -2); c.lineTo(1.3, -5);
    c.strokeStyle = 'rgba(255,255,255,0.9)'; c.lineWidth = 0.8; c.stroke();
    c.beginPath(); c.moveTo(-2.6, -5); c.lineTo(-1.3, -5); c.lineTo(-2.2, -2); c.lineTo(-4.4, -2); c.closePath();
    c.fillStyle = 'rgba(255,255,255,0.85)'; c.fill();
    c.restore();
  };

  // ---------------------------------------------------------------- herois
  // Faz o L (Lulala): a mao em L voa girando como bumerangue, com linhas de velocidade e dois fantasmas atras
  A.fxLHand = (c, p, t) => {
    const dx = Math.cos(p.ang || 0), dy = Math.sin(p.ang || 0), spin = t * 10;
    c.save();
    c.lineCap = 'round';
    for (let i = 0; i < 3; i++) {
      const o = (i - 1) * 7, nx = -dy * o, ny = dx * o, l0 = 16 + Math.abs(i - 1) * 3, l1 = l0 + 18 - Math.abs(i - 1) * 5;
      c.strokeStyle = i === 1 ? 'rgba(255,255,255,0.8)' : 'rgba(255,120,110,0.7)';
      c.lineWidth = i === 1 ? 2.6 : 1.9;
      c.beginPath(); c.moveTo(p.x - dx * l0 + nx, p.y - dy * l0 + ny); c.lineTo(p.x - dx * l1 + nx, p.y - dy * l1 + ny); c.stroke();
    }
    c.globalAlpha = 0.16; A.lHand(c, p.x - dx * 24, p.y - dy * 24, 1.05, spin - 0.9);
    c.globalAlpha = 0.34; A.lHand(c, p.x - dx * 12, p.y - dy * 12, 1.15, spin - 0.45);
    c.globalAlpha = 1;
    A.circ(c, p.x, p.y, 18, 'rgba(255,244,230,0.25)');
    A.lHand(c, p.x, p.y, 1.25, spin);
    c.restore();
  };
  // impacto do L: estalo branco e estrelinhas vermelhas e brancas espirrando
  A.fxLPop = (c, f, k) => {
    const e = eo(k), s = f.x * 0.37 + f.y;
    c.save();
    c.globalAlpha = 1 - k;
    if (k < 0.25) A.circ(c, f.x, f.y, 13 * (1 - k / 0.25) + 3, 'rgba(255,250,235,0.85)');
    A.ell(c, f.x, f.y, 6 + 22 * e, (6 + 22 * e) * 0.8, null, '#ffffff', 3.4 * (1 - k) + 0.6);
    c.lineWidth = 1;
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * U.TAU + rnd(i, s) * 0.5, d = 6 + 28 * e * (0.7 + 0.3 * rnd(i + 9, s));
      star5(c, f.x + Math.cos(a) * d, f.y + Math.sin(a) * d * 0.8 - 8 * e, (i % 2 ? 3.4 : 4.4) * (1 - k * 0.5));
      c.fillStyle = i % 2 ? '#ffffff' : '#e8423f'; c.fill();
      c.strokeStyle = i % 2 ? '#c9a49c' : '#8f2420'; c.stroke();
    }
    c.restore();
  };
  // Projeto de Lei (Zero-Um): folha girando e virando no ar, com papeizinhos tremulando atras
  A.fxDoc = (c, p, t) => {
    const dx = Math.cos(p.ang || 0), dy = Math.sin(p.ang || 0), sd = p.sx || 0;
    c.save();
    for (let i = 0; i < 3; i++) {
      const b = 9 + i * 7, w = Math.sin(t * 18 + i * 2 + sd) * 3;
      c.globalAlpha = 0.75 - i * 0.2;
      chip(c, p.x - dx * b - dy * w, p.y - dy * b + dx * w, 4.4 - i * 0.8, 3.2 - i * 0.5, t * 9 + i * 1.7, Math.cos(t * 15 + i), '#f4f2ea');
    }
    c.globalAlpha = 1;
    A.circ(c, p.x, p.y, 11, 'rgba(255,255,240,0.3)');
    c.translate(p.x, p.y);
    c.rotate(Math.sin(t * 7 + sd) * 0.6 + t * 3);
    const fl = Math.cos(t * 8 + sd);
    c.scale(1.35 * Math.max(0.5, Math.abs(fl)), 1.35);
    A.rrect(c, -5.5, -7, 11, 14, 1.2, fl > 0 ? '#fbfaf4' : '#e6e2d4', '#4f5560', 1.2);
    A.poly(c, [[2.5, -7], [5.5, -4], [2.5, -4]], '#d6d3c8', '#4f5560', 0.8);
    if (fl > 0) {
      c.strokeStyle = '#9aa0aa'; c.lineWidth = 1; c.lineCap = 'round';
      c.beginPath();
      c.moveTo(-3.4, -3.8); c.lineTo(1, -3.8);
      c.moveTo(-3.4, -1.5); c.lineTo(3.4, -1.5);
      c.moveTo(-3.4, 0.8); c.lineTo(3.4, 0.8);
      c.moveTo(-3.4, 3.1); c.lineTo(-0.4, 3.1);
      c.stroke();
      A.circ(c, 2.3, 4.2, 2.1, '#1f9a4c', '#125c2c', 0.7);
      A.circ(c, 2.3, 4.2, 0.95, '#ffd21f');
    }
    c.restore();
  };
  // Imbrochavel! (Capitao Mito): o grito vira onda de choque verde e amarela, linhas de grito e confete
  A.fxShout = (c, f, k) => {
    const r = f.r || 70, e = eo(k), s = f.x * 0.71 + f.y * 0.3;
    c.save();
    if (k < 0.2) {
      const kk = k / 0.2, rr = r * (0.28 + 0.25 * kk);
      c.globalAlpha = (1 - kk) * 0.55;
      A.ell(c, f.x, f.y - 14, rr, rr * 0.8, '#fffbe0');
    }
    for (let i = 0; i < 3; i++) {
      const kk = (k - i * 0.13) / 0.62;
      if (kk <= 0 || kk >= 1) continue;
      const rr = r * (0.2 + 0.9 * eo(kk));
      c.globalAlpha = 1 - kk;
      A.ell(c, f.x, f.y - 2, rr, rr * U.YS, null, 'rgba(43,26,15,0.3)', 6 * (1 - kk) + 3);
      A.ell(c, f.x, f.y - 2, rr, rr * U.YS, null, i % 2 ? '#1f9a4c' : '#ffd21f', 5 * (1 - kk) + 1.4);
    }
    // linhas de grito em volta da cabeca
    c.lineCap = 'round';
    c.globalAlpha = k < 0.55 ? 1 : (1 - k) / 0.45;
    c.beginPath();
    for (let i = 0; i < 10; i++) {
      const a = (i / 10) * U.TAU + 0.3, d0 = 16 + r * 0.5 * e, d1 = d0 + 8 + 7 * (1 - k);
      c.moveTo(f.x + Math.cos(a) * d0, f.y - 24 + Math.sin(a) * d0 * 0.7);
      c.lineTo(f.x + Math.cos(a) * d1, f.y - 24 + Math.sin(a) * d1 * 0.7);
    }
    c.strokeStyle = 'rgba(43,26,15,0.45)'; c.lineWidth = 4.4; c.stroke();
    c.strokeStyle = '#ffffff'; c.lineWidth = 2.2; c.stroke();
    // confete verde e amarelo
    const fa = k < 0.7 ? 1 : (1 - k) / 0.3;
    for (let i = 0; i < 16; i++) {
      const a = rnd(i, s) * U.TAU, sp = r * (0.5 + 0.7 * rnd(i + 20, s));
      const px = f.x + Math.cos(a) * sp * e;
      const py = f.y - 24 + Math.sin(a) * sp * e * 0.55 - Math.sin(Math.min(1, k * 1.5) * Math.PI * 0.5) * 28 * (0.5 + rnd(i + 40, s)) + 52 * k * k;
      c.globalAlpha = fa;
      chip(c, px, py, 4.4, 2.8, a + k * 12 * (rnd(i + 60, s) - 0.5), Math.cos(k * 18 + i), i % 2 ? '#1f9a4c' : '#ffd21f');
    }
    c.restore();
  };
  // Motociata (Capitao Mito): marcas de pneu de cavalo de pau no chao e fumaca de escapamento cinza-azulada
  A.fxMotoZone = (c, z, t, fade) => {
    const r = z.r, s = z.x * 0.13 + z.y * 0.07;
    c.save();
    c.globalAlpha = fade * 0.62;
    c.translate(z.x, z.y);
    c.scale(1, U.YS);
    c.rotate(rnd(1, s) * U.TAU);
    c.lineCap = 'round';
    c.beginPath();
    for (const rr of [r * 0.46, r * 0.46 + 9]) {
      const px = Math.cos(0.2) * rr, py = Math.sin(0.2) * rr, L = r * 0.75;
      c.moveTo(px + Math.sin(0.2) * L, py - Math.cos(0.2) * L);
      c.lineTo(px, py);
      c.arc(0, 0, rr, 0.2, 3.7);
    }
    c.strokeStyle = '#2a2626'; c.lineWidth = 5; c.stroke();
    c.setLineDash([2.5, 3]);
    c.strokeStyle = 'rgba(96,90,86,0.9)'; c.lineWidth = 1.8; c.stroke();
    c.setLineDash([]);
    c.restore();
    c.save();
    for (let i = 0; i < 10; i++) {
      const ph = (t * 0.5 + i / 10) % 1;
      const bx = z.x + (rnd(i, s) - 0.5) * r * 1.5, by = z.y + (rnd(i + 10, s) - 0.5) * r * 0.75;
      const dir = rnd(i + 20, s) < 0.5 ? -1 : 1;
      const px = bx + dir * ph * 24 + Math.sin(t * 2 + i) * 3, py = by - 6 - ph * 34, rad = 7 + ph * 13;
      c.globalAlpha = fade * 0.9 * Math.sin(ph * Math.PI);
      A.circ(c, px, py, rad, i % 2 ? '#7f8ca3' : '#94a0b5', 'rgba(70,80,100,0.35)', 1.2);
      A.circ(c, px - rad * 0.28, py - rad * 0.3, rad * 0.55, '#c3cbd8');
    }
    c.restore();
  };

  // ---------------------------------------------------------------- feiticos
  // rastro da Operacao da PF: duas marcas de pneu escuras e poeirinha (aparecem quando a viatura pousa)
  A.fxSkid = (c, f, k) => {
    const land = U.clamp((k - 0.035) / 0.02, 0, 1);
    if (land <= 0) return;
    const s = f.x * 0.53 + f.y * 0.29;
    c.save();
    c.globalAlpha = land * Math.min(1, (1 - k) * 2.2) * 0.62;
    c.translate(f.x, f.y);
    c.scale(1, U.YS);
    c.rotate((rnd(2, s) - 0.5) * 0.9);
    c.lineCap = 'round';
    c.beginPath();
    for (const o of [-7, 7]) { c.moveTo(-25, o + 2); c.quadraticCurveTo(0, o - 5, 24, o + 3); }
    c.strokeStyle = '#1e1a1a'; c.lineWidth = 5.5; c.stroke();
    c.setLineDash([3, 3]); c.strokeStyle = 'rgba(95,88,84,0.85)'; c.lineWidth = 1.8; c.stroke(); c.setLineDash([]);
    c.restore();
    const dk = (k - 0.035) / 0.12;
    if (dk > 0 && dk < 1) {
      c.save();
      c.globalAlpha = (1 - dk) * 0.85;
      for (let i = 0; i < 8; i++) {
        const a = rnd(i, s) * U.TAU, d = 14 + 30 * eo(dk) * (0.5 + 0.5 * rnd(i + 8, s));
        A.circ(c, f.x + Math.cos(a) * d, f.y + Math.sin(a) * d * 0.45 - 12 * dk * rnd(i + 16, s), (2 + 2.6 * rnd(i + 24, s)) * (1 - dk * 0.5), '#d9c8a4');
      }
      c.restore();
    }
  };

  // ---------------------------------------------------------------- adversarios
  // tiro de longe: 'gleice' = ondas do megafone; 'nicolau' = "like" do celular com brilho de flash; outros = balao com "!"
  A.fxEnemyShot = (c, p, t) => {
    const ang = p.ang || 0, dx = Math.cos(ang), dy = Math.sin(ang);
    c.save();
    c.lineCap = 'round';
    if (p.skey === 'gleice') {
      c.translate(p.x, p.y); c.rotate(ang);
      for (let i = 0; i < 3; i++) {
        const ph = (t * 5 + i / 3) % 1, rr = 3 + ph * 11;
        c.globalAlpha = 1 - ph;
        c.beginPath(); c.arc(-10 + ph * 6, 0, rr, -0.85, 0.85);
        c.strokeStyle = 'rgba(43,26,15,0.45)'; c.lineWidth = 4.2; c.stroke();
        c.strokeStyle = '#ffe45a'; c.lineWidth = 2.2; c.stroke();
      }
      c.globalAlpha = 1;
      A.circ(c, 0, 0, 2.6, '#fff6c8', 'rgba(43,26,15,0.5)', 1);
    } else if (p.skey === 'nicolau') {
      c.fillStyle = '#ffffff';
      for (let i = 0; i < 3; i++) {
        const b = 7 + i * 6, w = Math.sin(t * 25 + i * 2) * 2;
        c.globalAlpha = 0.95 - i * 0.27;
        star4(c, p.x - dx * b - dy * w, p.y - dy * b + dx * w, 3.6 - i * 0.7);
      }
      c.globalAlpha = 1;
      A.circ(c, p.x, p.y, 8, 'rgba(255,255,255,0.4)');
      const hr = 4.8 * (1 + 0.12 * Math.sin(t * 22));
      heartPath(c, p.x, p.y, hr);
      c.fillStyle = '#ff4f7a'; c.fill(); c.lineWidth = 1.1; c.strokeStyle = '#8f1f3c'; c.stroke();
      A.ell(c, p.x - hr * 0.4, p.y - hr * 0.35, hr * 0.24, hr * 0.16, 'rgba(255,255,255,0.8)');
    } else {
      for (let i = 0; i < 2; i++) {
        const o = i ? 3 : -3, b0 = 9, b1 = 18 - i * 3;
        A.line(c, p.x - dx * b0 - dy * o, p.y - dy * b0 + dx * o, p.x - dx * b1 - dy * o, p.y - dy * b1 + dx * o, 'rgba(255,255,255,0.7)', 1.6);
      }
      const bx = p.x, by = p.y + Math.sin(t * 14) * 1;
      A.poly(c, [[bx - 3, by + 4], [bx - 6.5, by + 9], [bx + 1.5, by + 4]], '#ffffff', OUT, 1.2);
      A.rrect(c, bx - 7, by - 5.5, 14, 11, 4, '#ffffff', OUT, 1.2);
      A.poly(c, [[bx - 2.4, by + 4.2], [bx - 4.6, by + 6.8], [bx + 0.8, by + 4.2]], '#ffffff', null);
      A.line(c, bx, by - 3, bx, by + 0.8, '#e8423f', 2.3);
      A.circ(c, bx, by + 3.1, 1.2, '#e8423f');
    }
    c.restore();
  };
  // sabotagem em voo: 'pelego' joga uma plaquinha vermelha de greve; os outros (Damaris) uma lata de tinta rosa
  A.fxThrow = (c, p, t) => {
    const k = Math.min(1, p.t / p.T);
    A.shadow(c, U.lerp(p.sx, p.tx, k), U.lerp(p.sy + 18, p.ty + 24, k), 6, 2.4, 0.22);
    c.save();
    c.translate(p.x, p.y);
    if (p.skey === 'pelego') {
      c.rotate(Math.sin(p.ang) * 0.5);
      A.line(c, 0, 1, 0, 13, '#8a5a32', 2.2);
      A.rrect(c, -8, -9, 16, 11, 1.6, '#d6282b', '#6e1214', 1.3);
      c.strokeStyle = 'rgba(255,255,255,0.9)'; c.lineWidth = 1.5; c.lineCap = 'round';
      c.beginPath(); c.moveTo(-5, -5.8); c.lineTo(5, -5.8); c.moveTo(-4, -2.4); c.lineTo(2.5, -2.4); c.stroke();
    } else {
      c.rotate(p.ang * 0.7);
      c.beginPath(); c.arc(0, -5, 4.8, Math.PI, 0); c.strokeStyle = '#4a505a'; c.lineWidth = 1; c.stroke();
      A.rrect(c, -4.8, -5, 9.6, 10.5, 1.6, '#c9ced6', '#4a505a', 1.1);
      A.rect(c, -4.8, -1.4, 9.6, 3.6, '#ff6fae');
      A.ell(c, 0, -5, 4.8, 1.6, '#ff6fae', '#4a505a', 0.9);
      A.circ(c, 3.6, -3, 1.4, '#ff6fae');
      A.ell(c, -2.6, 1.2, 0.8, 3, 'rgba(255,255,255,0.45)');
    }
    c.restore();
    if (p.skey !== 'pelego') {
      c.save();
      for (let i = 1; i <= 3; i++) {
        const kk = Math.max(0, k - i * 0.06);
        c.globalAlpha = 0.85 - i * 0.2;
        A.circ(c, U.lerp(p.sx, p.tx, kk), U.lerp(p.sy, p.ty, kk) - p.arc * 4 * kk * (1 - kk) + i * 3, 1.9 - i * 0.3, '#ff6fae');
      }
      c.restore();
    }
  };
  // impacto da sabotagem: tinta rosa espirrando na torre, ou a placa fincando com poeirinha
  A.fxSabHit = (c, f, k) => {
    const s = f.x * 0.3 + f.y * 0.7, e = eo(Math.min(1, k * 2.5));
    c.save();
    if (f.skey === 'pelego') {
      const x = f.x + 20, y = f.y + 38;
      c.globalAlpha = 1 - k;
      c.lineCap = 'round';
      c.beginPath();
      for (let i = 0; i < 5; i++) {
        const a = -Math.PI * (0.15 + 0.7 * i / 4), d0 = 8 + 10 * e, d1 = d0 + 6;
        c.moveTo(x + Math.cos(a) * d0, y - 20 + Math.sin(a) * d0); c.lineTo(x + Math.cos(a) * d1, y - 20 + Math.sin(a) * d1);
      }
      c.strokeStyle = '#ffffff'; c.lineWidth = 2; c.stroke();
      for (let i = 0; i < 6; i++) {
        const a = rnd(i, s) * Math.PI, d = 6 + 18 * e;
        A.circ(c, x + Math.cos(a) * d * (rnd(i + 6, s) < 0.5 ? -1 : 1), y - 2 - 6 * e * rnd(i + 12, s), 3 + 3 * e, '#dccaa6');
      }
    } else {
      const pop = k < 0.12 ? U.easeOutBack(k / 0.12) : 1;
      c.globalAlpha = k < 0.7 ? 1 : (1 - k) / 0.3;
      c.fillStyle = '#ff6fae';
      c.beginPath();
      c.moveTo(f.x + 8 * pop, f.y); c.arc(f.x, f.y, 8 * pop, 0, U.TAU);
      for (let i = 0; i < 7; i++) {
        const a = (i / 7) * U.TAU + rnd(i, s), d = 8 * pop * (0.7 + 0.5 * rnd(i + 7, s)), rr = (2.5 + 3 * rnd(i + 14, s)) * pop;
        const x = f.x + Math.cos(a) * d, y = f.y + Math.sin(a) * d * 0.8;
        c.moveTo(x + rr, y); c.arc(x, y, rr, 0, U.TAU);
      }
      c.fill();
      A.ell(c, f.x - 3, f.y - 3, 2.6 * pop, 1.6 * pop, 'rgba(255,255,255,0.6)');
      for (let i = 0; i < 9; i++) {
        const a = -Math.PI * rnd(i + 21, s), sp = 22 + 30 * rnd(i + 30, s);
        A.circ(c, f.x + Math.cos(a) * sp * e, f.y + Math.sin(a) * sp * e * 0.7 + 40 * k * k, 2.2 * (1 - k * 0.5), '#ff6fae');
      }
      c.lineCap = 'round';
      for (let i = 0; i < 3; i++) {
        const ox = (i - 1) * 6 + 1, len = (6 + 8 * rnd(i + 40, s)) * eo(k);
        A.line(c, f.x + ox, f.y + 3, f.x + ox, f.y + 3 + len, '#ff6fae', 2.4);
        A.circ(c, f.x + ox, f.y + 3 + len, 1.8, '#ff6fae');
      }
    }
    c.restore();
  };
  // marca da sabotagem enquanto a torre esta parada: tinta rosa escorrendo, ou a placa de greve fincada na frente
  A.sabMark = (c, tw, t, kind, age, rem) => {
    c.save();
    c.globalAlpha = Math.min(1, rem / 0.5, age * 6);
    if (kind === 'pelego') {
      c.translate(tw.x + 20, tw.y + 14);
      A.shadow(c, 0, 1, 7, 2.5, 0.25);
      c.rotate(Math.sin(t * 2.4 + tw.id) * 0.08 - 0.06);
      A.line(c, 0, 0, 0, -20, '#8a5a32', 2.8);
      A.rrect(c, -10, -34, 20, 15, 2, '#d6282b', '#6e1214', 1.5);
      c.strokeStyle = 'rgba(255,255,255,0.9)'; c.lineWidth = 1.8; c.lineCap = 'round';
      c.beginPath(); c.moveTo(-6.5, -29.5); c.lineTo(6.5, -29.5); c.moveTo(-5, -25); c.lineTo(3.5, -25); c.stroke();
    } else {
      const grow = Math.min(1, age / 1.6), y0 = tw.y - 44;
      c.fillStyle = '#ff6fae';
      c.beginPath();
      for (const [ox, oy, rr] of [[-9, 0, 6.5], [7, -11, 5], [2, 7, 4.5], [-2, -6, 4]]) { c.moveTo(tw.x + ox + rr, y0 + oy); c.arc(tw.x + ox, y0 + oy, rr, 0, U.TAU); }
      c.fill();
      c.lineCap = 'round';
      for (const [ox, oy, l] of [[-11, 4, 14], [-6, 5, 9], [7, -7, 12], [3, 10, 7]]) {
        const len = l * (0.35 + 0.65 * grow);
        A.line(c, tw.x + ox, y0 + oy, tw.x + ox, y0 + oy + len, '#ff6fae', 2.6);
        A.circ(c, tw.x + ox, y0 + oy + len, 1.9, '#ff6fae');
      }
      A.ell(c, tw.x - 11, y0 - 2, 2.2, 1.4, 'rgba(255,255,255,0.6)');
    }
    c.restore();
  };
  // Fundao Eleitoral: saco de dinheiro com "$" caindo, soltando notas pelo caminho
  A.fxBag = (c, p, t) => {
    if (p.t < 0) return;
    const k = Math.min(1, p.t / p.T);
    let vx = p.tx - p.sx, vy = (p.ty - p.sy) - p.arc * 4 * (1 - 2 * k);
    const vl = Math.hypot(vx, vy) || 1; vx /= vl; vy /= vl;
    c.save();
    for (let i = 0; i < 2; i++) {
      const b = 13 + i * 11, w = Math.sin(t * 9 + i * 2.3) * 5;
      c.globalAlpha = 0.85 - i * 0.3;
      note(c, p.x - vx * b - vy * w, p.y - vy * b + vx * w, 9, 5, t * 6 + i * 2, Math.cos(t * 11 + i));
    }
    c.globalAlpha = 1;
    c.translate(p.x, p.y);
    c.rotate(Math.sin(p.ang * 0.8) * 0.35);
    c.scale(1.2, 1.2);
    A.ell(c, 0, 2.5, 8.5, 7.8, '#d8b26a', '#6e4a1c', 1.4);
    A.poly(c, [[-3.4, -4.6], [-6.4, -10], [-1.2, -7], [0, -10.5], [1.2, -7], [6.4, -10], [3.4, -4.6]], '#d8b26a', '#6e4a1c', 1.2);
    A.line(c, -4.4, -4.6, 4.4, -4.6, '#8a3a20', 1.8);
    A.ell(c, -4, 0.4, 1.7, 3, 'rgba(255,255,255,0.32)');
    A.text(c, '$', 0.6, 3.4, 10, '#2e7d3a', 'center', { weight: 900 }, false);
    c.restore();
  };
  // dinheiro estourando (Mala Estourada do Mensalao e o saco do Fundao): notas, moedas e confete de papel
  A.fxCash = (c, f, k) => {
    const r = f.r || 50, e = eo(k), s = f.x * 0.61 + f.y * 0.17;
    c.save();
    if (k < 0.22) {
      const kk = k / 0.22, rr = r * (0.25 + 0.4 * kk);
      c.globalAlpha = (1 - kk) * 0.7;
      A.ell(c, f.x, f.y - 8, rr, rr * 0.75, '#fff3c4');
    }
    if (k < 0.5) {
      const kk = k / 0.5, rr = r * (0.3 + 0.8 * eo(kk));
      c.globalAlpha = 1 - kk;
      A.ell(c, f.x, f.y, rr, rr * U.YS, null, '#ffd54a', 3 * (1 - kk) + 1);
    }
    const fa = k < 0.6 ? 1 : (1 - k) / 0.4;
    c.globalAlpha = fa;
    for (let i = 0; i < 12; i++) {
      const a = rnd(i + 80, s) * U.TAU, d = r * (0.3 + 1.0 * e) * (0.5 + 0.5 * rnd(i + 90, s));
      const up = Math.sin(Math.min(1, k * 2) * Math.PI * 0.5) * 50 * rnd(i + 100, s) - 20 * k * k;
      chip(c, f.x + Math.cos(a) * d, f.y - 10 + Math.sin(a) * d * 0.5 - up, 3, 2, k * 14 * (rnd(i + 110, s) - 0.5), Math.cos(k * 20 + i), i % 3 === 0 ? '#ffe08a' : i % 3 === 1 ? '#ffffff' : '#cfe8b8');
    }
    for (let i = 0; i < 7; i++) {
      const a = rnd(i + 50, s) * U.TAU, sp = r * (0.5 + 0.6 * rnd(i + 60, s));
      const hgt = Math.max(0, Math.sin(Math.min(1, k * 1.4) * Math.PI)) * 34 * (0.6 + 0.4 * rnd(i + 70, s));
      A.coin(c, f.x + Math.cos(a) * sp * e, f.y - 2 + Math.sin(a) * sp * e * 0.5 - hgt, 3.6);
    }
    for (let i = 0; i < 10; i++) {
      const a = rnd(i, s) * U.TAU, d = r * (0.25 + 0.8 * e) * (0.55 + 0.45 * rnd(i + 10, s));
      const up = Math.sin(Math.min(1, k * 1.8) * Math.PI * 0.5) * 42 * (0.5 + rnd(i + 20, s)) - 26 * k * k;
      note(c, f.x + Math.cos(a) * d + Math.sin(k * 9 + i) * 4, f.y - 6 + Math.sin(a) * d * 0.5 - up, 12, 6.5,
        (rnd(i + 30, s) - 0.5) * 2 + k * 5 * (rnd(i + 40, s) - 0.5), Math.cos(k * 16 + i * 1.3));
    }
    c.restore();
  };
  // chefe derrotado: chuva de confete nas cores das duas chapas, papeis voando e estrelas
  A.fxConfetti = (c, f, k) => {
    const r = f.r || 90, tt = k * (f.T || 1.6), s = f.x * 0.37 + f.y * 0.91;
    c.save();
    if (k < 0.15) {
      const kk = k / 0.15, rr = r * (0.3 + 0.5 * kk);
      c.globalAlpha = (1 - kk) * 0.6;
      A.ell(c, f.x, f.y - 26, rr, rr * 0.8, '#fffbe8');
    }
    for (let i = 0; i < 2; i++) {
      const kk = (k - i * 0.1) / 0.45;
      if (kk <= 0 || kk >= 1) continue;
      const rr = r * (0.3 + 0.9 * eo(kk));
      c.globalAlpha = 1 - kk;
      A.ell(c, f.x, f.y, rr, rr * U.YS, null, i ? '#1f9a4c' : '#ffd21f', 5 * (1 - kk) + 1.5);
    }
    if (k < 0.6) {
      const kk = k / 0.6;
      c.globalAlpha = 1 - kk;
      c.lineWidth = 1.2; c.strokeStyle = '#c99a1f'; c.fillStyle = '#ffe45a';
      for (let i = 0; i < 6; i++) {
        const a = (i / 6) * U.TAU + 0.4, d = 20 + r * 0.8 * eo(kk);
        star5(c, f.x + Math.cos(a) * d, f.y - 30 + Math.sin(a) * d * 0.6, 6.5 * (1 - kk * 0.4));
        c.fill(); c.stroke();
      }
    }
    const fa = k < 0.7 ? 1 : (1 - k) / 0.3;
    c.globalAlpha = fa;
    for (let i = 0; i < 6; i++) {
      const a = rnd(i + 200, s) * U.TAU, sp = 40 + 70 * rnd(i + 210, s), dr = (1 - Math.exp(-2 * tt)) / 2;
      paper(c, f.x + Math.cos(a) * sp * dr * 1.4 + Math.sin(tt * 4 + i) * 10 * k, f.y - 40 - (160 + 80 * rnd(i + 220, s)) * dr + 55 * tt * tt,
        10, 12.5, Math.sin(tt * 3 + i) * 0.6, Math.cos(tt * 5 + i));
    }
    const dr = (1 - Math.exp(-2.2 * tt)) / 2.2;
    for (let i = 0; i < 56; i++) {
      const a = rnd(i, s) * U.TAU, sp = 90 + 190 * rnd(i + 40, s);
      const px = f.x + Math.cos(a) * sp * dr + Math.sin(tt * 6 + i) * 8 * k;
      const py = f.y - 30 - (120 + 220 * rnd(i + 80, s)) * dr + Math.sin(a) * sp * 0.3 * dr + 85 * tt * tt;
      chip(c, px, py, 7, 4.2, tt * (5 + 9 * rnd(i + 120, s)), Math.cos(tt * (8 + 6 * rnd(i + 160, s)) + i), CHAPAS[i % 5]);
    }
    c.restore();
  };
  // "Entrou com recurso!": redemoinho de papeis do processo e carimbos; na volta (out = false) o carimbo bate no chao
  A.fxCourt = (c, f, k) => {
    const r = f.r || 70, s = f.x * 0.21 + f.y * 0.43, e = eo(k), out = !!f.out, sg = out ? 1 : -1;
    c.save();
    c.lineCap = 'round';
    c.globalAlpha = (1 - k) * 0.75;
    for (let i = 0; i < 2; i++) {
      const rr = (out ? r * (0.3 + 0.7 * e) : r * (1 - 0.6 * e)) * (1 - i * 0.22), a0 = sg * k * 9 + i * Math.PI;
      c.beginPath(); c.ellipse(f.x, f.y - 30, rr, rr * 0.42, 0, a0, a0 + 2.4);
      c.strokeStyle = i ? '#c9b8e8' : '#ffffff'; c.lineWidth = 3 - i; c.stroke();
    }
    const fa = out ? (k < 0.6 ? 1 : (1 - k) / 0.4) : Math.min(1, k * 5) * (k < 0.7 ? 1 : (1 - k) / 0.3);
    c.globalAlpha = fa;
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * U.TAU + sg * k * 7 + rnd(i, s);
      const rr = 12 + r * (out ? e : 1 - e) * (0.6 + 0.4 * rnd(i + 12, s));
      const hgt = out ? 20 + k * 70 * (0.5 + rnd(i + 24, s)) : 30 + (1 - e) * 40 * rnd(i + 24, s);
      const x = f.x + Math.cos(a) * rr, y = f.y - hgt + Math.sin(a) * rr * 0.4;
      if (i % 4 === 3) stamp(c, x, y, 1); else paper(c, x, y, 8, 10, a * 0.5, Math.cos(k * 12 + i));
    }
    if (!out && k > 0.45) {
      const kk = (k - 0.45) / 0.55, sc = kk < 0.15 ? 1.8 - 0.8 * U.easeOutBack(kk / 0.15) : 1;
      c.globalAlpha = kk < 0.75 ? 1 : (1 - kk) / 0.25;
      c.save();
      c.translate(f.x + 4, f.y + 4); c.scale(sc, sc * 0.55); c.rotate(-0.2);
      c.strokeStyle = '#c8323a';
      c.lineWidth = 3; c.beginPath(); c.arc(0, 0, 18, 0, U.TAU); c.stroke();
      c.lineWidth = 1.6; c.beginPath(); c.arc(0, 0, 13, 0, U.TAU); c.stroke();
      c.lineWidth = 2.4; c.beginPath(); c.moveTo(-8, -3.5); c.lineTo(8, -3.5); c.moveTo(-9, 1); c.lineTo(9, 1); c.moveTo(-6, 5.5); c.lineTo(6, 5.5); c.stroke();
      c.restore();
      if (kk < 0.35) {
        c.globalAlpha = 1 - kk / 0.35;
        stamp(c, f.x + 4, f.y - 4 - 46 * (1 - Math.min(1, kk / 0.12)) - 10 * Math.max(0, kk - 0.12), 2.2);
      }
    }
    c.restore();
  };
  // Zambela/Dilmae entrando e saindo do chao (e o chefe da Motociata/Trio): poeira, fumaca e papeis voando
  A.fxPoof = (c, f, k) => {
    const big = !!f.big, s = f.x * 0.27 + f.y * 0.63, e = eo(k);
    c.save();
    const n = big ? 11 : 6, R = big ? 36 : 18;
    for (let i = 0; i < n; i++) {
      const a = rnd(i, s) * U.TAU, d = R * (0.35 + 0.65 * e) * (0.6 + 0.4 * rnd(i + 11, s));
      const px = f.x + Math.cos(a) * d, py = f.y - 4 + Math.sin(a) * d * 0.45 - e * (big ? 20 : 11) * rnd(i + 22, s);
      const rad = (big ? 9.5 : 5.5) * (0.6 + 0.8 * e) * (0.7 + 0.5 * rnd(i + 33, s));
      c.globalAlpha = (1 - k) * 0.85;
      const smoke = big && i % 2 === 0;
      A.circ(c, px, py, rad, smoke ? '#95a1b4' : '#cdbf9f');
      A.circ(c, px - rad * 0.28, py - rad * 0.3, rad * 0.55, smoke ? '#c3cbd8' : '#e6dcc4');
    }
    if (big) {
      // escapamento: tracos de fumaca saindo de lado
      c.globalAlpha = (1 - k) * 0.7;
      c.lineCap = 'round';
      for (let i = 0; i < 3; i++) {
        const y = f.y - 6 - i * 7, x0 = f.x + 18 + e * 20, x1 = x0 + 14 + 18 * e;
        A.line(c, x0, y, x1, y + 2, '#a7b2c3', 3 - i * 0.6);
      }
    }
    const np = big ? 6 : 3, fa = k < 0.6 ? 1 : (1 - k) / 0.4;
    c.globalAlpha = fa;
    for (let i = 0; i < np; i++) {
      const h = rnd(i + 44, s), w = big ? 50 : 28;
      const px = f.x + (h - 0.5) * 2 * w * e + Math.sin(k * 10 + i) * 4;
      const py = f.y - 8 - Math.sin(Math.min(1, k * 1.4) * Math.PI * 0.5) * (big ? 54 : 32) * (0.6 + 0.4 * rnd(i + 55, s)) + 22 * k * k;
      paper(c, px, py, big ? 7 : 6, big ? 9 : 7.5, k * 8 * (h - 0.5) * 2, Math.cos(k * 14 + i));
    }
    c.restore();
  };

  // ---------------------------------------------------------------- torres
  // Poco sem Fundo (Petrolao): fenda de oleo preto borbulhando com um jorro pequeno
  A.fxOilChasm = (c, f, k, t) => {
    const open = Math.sin(Math.min(1, k) * Math.PI), s = f.x * 0.77 + f.y * 0.19;
    const rx = 30 * open + 2, ry = 12 * open + 1;
    c.save();
    c.beginPath();
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * U.TAU, j = 0.72 + 0.4 * rnd(i, s);
      const x = f.x + Math.cos(a) * rx * j, y = f.y + Math.sin(a) * ry * j;
      if (i) c.lineTo(x, y); else c.moveTo(x, y);
    }
    c.closePath();
    c.fillStyle = '#121016'; c.fill();
    c.lineWidth = 2; c.strokeStyle = OUT; c.lineJoin = 'round'; c.stroke();
    A.ell(c, f.x - rx * 0.1, f.y - ry * 0.15, rx * 0.55, ry * 0.42, 'rgba(70,66,90,0.75)');
    c.strokeStyle = 'rgba(255,255,255,0.5)'; c.lineWidth = 1.4; c.lineCap = 'round';
    c.beginPath(); c.ellipse(f.x - rx * 0.25, f.y - ry * 0.3, rx * 0.3, ry * 0.25, 0, Math.PI * 1.1, Math.PI * 1.7); c.stroke();
    for (let i = 0; i < 5; i++) {
      const ph = (k * 3.2 + rnd(i + 5, s)) % 1;
      const bx = f.x + (rnd(i + 10, s) - 0.5) * rx * 1.1, by = f.y + (rnd(i + 15, s) - 0.5) * ry * 0.8;
      if (ph < 0.8) {
        const br = (1 + 3 * ph) * open;
        A.circ(c, bx, by - br * 0.5, br, '#1c1922', 'rgba(150,144,168,0.9)', 1);
        A.circ(c, bx - br * 0.35, by - br * 0.85, br * 0.25, 'rgba(255,255,255,0.75)');
      } else {
        const pk = (ph - 0.8) / 0.2;
        c.globalAlpha = 1 - pk;
        A.circ(c, bx, by - 2, 2 + 4 * pk, null, 'rgba(170,164,188,0.9)', 1);
        c.globalAlpha = 1;
      }
    }
    if (k > 0.2 && k < 0.85) {
      // jorro curto: coluna grossa que abre numa coroa de gotas e respinga para os lados
      const gk = (k - 0.2) / 0.65, h = Math.sin(gk * Math.PI) * 30, wob = Math.sin(t * 22) * 1.2, x = f.x + 1, top = f.y - h;
      c.beginPath();
      c.moveTo(x - 7, f.y);
      c.quadraticCurveTo(x - 3, f.y - h * 0.55, x - 5 + wob, top);
      c.lineTo(x + 5 + wob, top);
      c.quadraticCurveTo(x + 4, f.y - h * 0.55, x + 8, f.y);
      c.closePath();
      c.fillStyle = '#141218'; c.fill(); c.strokeStyle = OUT; c.lineWidth = 1.2; c.stroke();
      // coroa
      c.beginPath();
      for (let i = 0; i < 5; i++) {
        const ox = (i - 2) * 3.6 + wob, oy = Math.abs(i - 2) * 1.5 - 2 - 2.5 * Math.sin(t * 18 + i), rr = 3.4 - Math.abs(i - 2) * 0.5;
        c.moveTo(x + ox + rr, top + oy); c.arc(x + ox, top + oy, rr, 0, U.TAU);
      }
      c.fillStyle = '#141218'; c.fill();
      A.ell(c, x - 2 + wob, top - 4, 2.4, 1.2, 'rgba(200,195,220,0.55)');
      A.line(c, x - 1 + wob * 0.5, top + 4, x - 0.5, f.y - 4, 'rgba(160,155,180,0.55)', 1.4);
      for (let i = 0; i < 8; i++) {
        const side = i % 2 ? 1 : -1, ph = (gk * 3 + i * 0.13) % 1, sp = 10 + 12 * rnd(i + 30, s);
        const dx = x + wob + side * sp * ph, dy = top - 4 - 16 * ph + 34 * ph * ph;
        A.circ(c, dx, dy, 2.3 * (1 - ph * 0.35), '#16141a');
        A.circ(c, dx - 0.6, dy - 0.7, 0.65, 'rgba(255,255,255,0.65)');
      }
    }
    c.restore();
  };
  // Viralizou (Central do Zap): redemoinho de baloes, carinhas amarelas e selinhos vermelhos de notificacao
  A.fxZapVortex = (c, z, t, fade) => {
    c.save();
    c.globalAlpha = fade;
    A.shadow(c, z.x, z.y + 2, 26, 9, 0.3);
    c.lineCap = 'round';
    for (let i = 0; i < 6; i++) {
      const kk = i / 5, rx = 7 + kk * 24, yy = z.y - 4 - kk * 62, ph = (t * 8 + i * 0.9) % U.TAU;
      c.beginPath(); c.ellipse(z.x + Math.sin(t * 4 + i) * 3, yy, rx, rx * 0.3, 0, ph, ph + 4.2);
      c.globalAlpha = fade * 0.4;
      c.strokeStyle = '#2f7a5e'; c.lineWidth = 4.2 - kk * 1.6; c.stroke();
      c.globalAlpha = fade * (0.9 - kk * 0.35);
      c.strokeStyle = '#dcf8c6'; c.lineWidth = 2.6 - kk * 1.2; c.stroke();
    }
    for (let i = 0; i < 12; i++) {
      const lv = (i / 12 + t * 0.22) % 1, rad = 8 + lv * 24, ang = t * (5.5 - lv * 2.5) + i * 2.4;
      const sa = Math.sin(ang), dep = 0.8 + 0.2 * sa;
      const px = z.x + Math.cos(ang) * rad + Math.sin(t * 4 + lv * 6) * 3, py = z.y - 6 - lv * 60 + sa * rad * 0.3;
      c.globalAlpha = fade * Math.min(1, lv * 6, (1 - lv) * 5) * (sa < 0 ? 0.7 : 1);
      const ty = i % 3;
      if (ty === 0) bubble(c, px, py, 11 * dep, 7.5 * dep, i % 2 ? '#ffffff' : '#dcf8c6', '#2f7a5e');
      else if (ty === 1) {
        const er = 3.8 * dep;
        A.circ(c, px, py, er, '#ffd84a', '#b58a12', 0.9);
        A.circ(c, px - er * 0.35, py - er * 0.2, er * 0.16, OUT);
        A.circ(c, px + er * 0.35, py - er * 0.2, er * 0.16, OUT);
        c.beginPath(); c.arc(px, py + er * 0.05, er * 0.5, 0.35, Math.PI - 0.35); c.strokeStyle = OUT; c.lineWidth = 0.8; c.stroke();
      } else {
        const br = 3.4 * dep;
        A.circ(c, px, py, br, '#e8423f', '#ffffff', 1);
        A.line(c, px, py - br * 0.5, px, py + br * 0.1, '#ffffff', 1.1);
        A.circ(c, px, py + br * 0.45, 0.55, '#ffffff');
      }
    }
    c.restore();
  };
  // Corrente do Zap: estouro de baloes de mensagem encaminhada
  A.fxZapBurst = (c, f, k) => {
    const e = eo(k), s = f.x * 0.45 + f.y * 0.55, r = f.r || 50;
    c.save();
    c.globalAlpha = 1 - k;
    const rr = r * (0.3 + 0.7 * k);
    c.beginPath(); c.ellipse(f.x, f.y - 10, rr, rr * 0.45, 0, k * 6, k * 6 + 3.6);
    c.strokeStyle = 'rgba(220,248,198,0.9)'; c.lineWidth = 3; c.stroke();
    const pop = k < 0.18 ? U.easeOutBack(k / 0.18) : 1;
    c.globalAlpha = Math.pow(1 - k, 0.7);
    for (let i = 0; i < 9; i++) {
      const a = (i / 9) * U.TAU + rnd(i, s) * 0.6, d = r * (0.15 + 0.85 * e) * (0.65 + 0.35 * rnd(i + 9, s));
      bubble(c, f.x + Math.cos(a) * d, f.y - 10 + Math.sin(a) * d * 0.5 - 10 * k, 11 * pop, 8 * pop,
        i % 3 === 0 ? '#fff1a8' : i % 3 === 1 ? '#dcf8c6' : '#ffffff', '#2f7a5e');
    }
    c.restore();
  };
  // Chuva de Notas (Dolar na Cueca): notas verdes caindo balancando e se amontoando no chao
  A.fxNotesZone = (c, z, t, fade) => {
    const r = z.r, s = z.x * 0.31 + z.y * 0.77;
    c.save();
    c.globalAlpha = fade;
    A.ell(c, z.x, z.y, r, r * U.YS, 'rgba(170,210,100,0.16)', 'rgba(120,170,60,0.35)', 1.2);
    const n = Math.floor(14 * Math.min(1, z.t / 2.2));
    for (let i = 0; i < n; i++) {
      const a = rnd(i, s) * U.TAU, d = Math.sqrt(rnd(i + 30, s)) * r * 0.8;
      c.save();
      c.translate(z.x + Math.cos(a) * d, z.y + Math.sin(a) * d * U.YS);
      c.scale(1, 0.55);
      c.rotate(rnd(i + 60, s) * U.TAU);
      c.fillStyle = i % 2 ? '#8ec67a' : '#9fd28a'; c.fillRect(-5.5, -3, 11, 6);
      c.strokeStyle = '#3f7f3a'; c.lineWidth = 1; c.strokeRect(-5.5, -3, 11, 6);
      c.fillStyle = '#d4ecbf'; c.beginPath(); c.ellipse(0, 0, 2.2, 1.8, 0, 0, U.TAU); c.fill();
      c.restore();
    }
    for (let i = 0; i < 10; i++) {
      const ph = (t * 0.55 + rnd(i + 90, s)) % 1;
      const a = rnd(i + 120, s) * U.TAU, d = Math.sqrt(rnd(i + 150, s)) * r * 0.85;
      c.globalAlpha = fade * Math.min(1, ph * 6, (1 - ph) * 8);
      note(c, z.x + Math.cos(a) * d + Math.sin(t * 2.6 + i) * 7, z.y + Math.sin(a) * d * U.YS - 8 - (1 - ph) * 80, 11, 6, Math.sin(t * 3 + i) * 0.7, Math.cos(t * 6 + i * 1.7));
    }
    c.restore();
  };
  // Chuva de Brilhantes (Joias): cada raio vira um diamante caindo com rastro de brilho e um estalo de purpurina
  A.fxDiamond = (c, f, k) => {
    const s = f.x * 0.83 + f.y * 0.11, fk = Math.min(1, k / 0.3);
    c.save();
    if (fk < 1) {
      const e = fk * fk, x = f.x - (1 - e) * 46, y = f.y - 10 - (1 - e) * 250;
      c.lineCap = 'round';
      c.strokeStyle = 'rgba(170,230,255,0.5)'; c.lineWidth = 6;
      c.beginPath(); c.moveTo(x, y); c.lineTo(x - 0.181 * 56, y - 0.983 * 56); c.stroke();
      c.strokeStyle = 'rgba(255,255,255,0.95)'; c.lineWidth = 2;
      c.beginPath(); c.moveTo(x, y); c.lineTo(x - 0.181 * 34, y - 0.983 * 34); c.stroke();
      c.fillStyle = '#ffffff';
      for (let i = 0; i < 3; i++) {
        const b = 12 + i * 14;
        star4(c, x - 0.181 * b + (rnd(i, s) - 0.5) * 10, y - 0.983 * b, 3.2 - i * 0.6);
      }
      gem(c, x, y, 1.15, 0.18);
    } else {
      const ik = (k - 0.3) / 0.7, ie = eo(ik);
      c.globalAlpha = 1 - ik;
      A.ell(c, f.x, f.y, 6 + 26 * ie, (6 + 26 * ie) * 0.45, null, '#ffffff', 2.4 * (1 - ik) + 0.5);
      gem(c, f.x, f.y - 6 - 4 * ie, 1.15 * (1 - ik * 0.4), 0.18);
      for (let i = 0; i < 7; i++) {
        const a = (i / 7) * U.TAU + rnd(i, s), d = 5 + 22 * ie * (0.6 + 0.4 * rnd(i + 7, s));
        const tw = 0.6 + 0.4 * Math.sin(k * 40 + i * 2);
        c.fillStyle = i % 2 ? '#ffffff' : '#bff0ff';
        star4(c, f.x + Math.cos(a) * d, f.y - 6 + Math.sin(a) * d * 0.55 - 12 * ie, (3.8 * (1 - ik) + 0.8) * tw);
      }
    }
    c.restore();
  };

  // ---------------------------------------------------------------- clima
  // tempestade de fake news (Praca dos Tres Poderes): ceu fechado, baloes cinza, selos vermelhos de "!" e papeis
  // caindo na diagonal; o relampago vira um clarao roxo-avermelhado com faixas de "glitch". k = forca (0..1)
  A.fakeStorm = (c, g, t, k) => {
    c.save();
    c.fillStyle = `rgba(46,48,78,${0.3 * k})`;
    c.fillRect(-20, -20, W + 40, H + 40);
    const r = U.rng(7);
    for (let i = 0; i < 12; i++) {
      const rad = 140 + r() * 120;
      const x = ((r() * (W + 600) + t * (30 + r() * 30)) % (W + 600)) - 300, y = r() * H * 0.45 - 40;
      const gr = c.createRadialGradient(x, y, 0, x, y, rad);
      gr.addColorStop(0, `rgba(48,44,70,${0.32 * k})`); gr.addColorStop(1, 'rgba(48,44,70,0)');
      c.fillStyle = gr; c.fillRect(x - rad, y - rad, rad * 2, rad * 2);
    }
    for (let i = 0; i < 34; i++) {
      const sp = 70 + r() * 60, w = 15 + r() * 8, a = 0.6 + r() * 0.3, ox = r(), oy = r();
      const y = ((oy * (H + 160) + t * sp) % (H + 160)) - 80;
      const x = ((ox * (W + 300) + t * sp * 0.5) % (W + 300)) - 150 + Math.sin(t * 1.6 + i) * 6;
      c.globalAlpha = a * k;
      bubble(c, x, y, w, w * 0.68, '#d5d9e4', '#5a6074');
    }
    for (let i = 0; i < 14; i++) {
      const sp = 110 + r() * 60, br = 6 + r() * 2, a = 0.8 + r() * 0.2, ox = r(), oy = r();
      const y = ((oy * (H + 160) + t * sp) % (H + 160)) - 80;
      const x = ((ox * (W + 300) + t * sp * 0.5) % (W + 300)) - 150;
      c.globalAlpha = a * k;
      A.circ(c, x, y, br, '#e8423f', '#ffffff', 1.2);
      A.line(c, x, y - br * 0.5, x, y + br * 0.1, '#ffffff', 1.6);
      A.circ(c, x, y + br * 0.45, 0.85, '#ffffff');
    }
    c.fillStyle = '#f1efe6';
    for (let i = 0; i < 22; i++) {
      const sp = 90 + r() * 70, hw = 3.2 + r() * 2, a = 0.65 + r() * 0.3, ox = r(), oy = r(), spin = 1.5 + r() * 3;
      const y = ((oy * (H + 160) + t * sp) % (H + 160)) - 80;
      const x = ((ox * (W + 300) + t * sp * 0.55) % (W + 300)) - 150;
      const rot = t * spin + i, fl = Math.cos(t * 4 + i), hh = hw * 1.3;
      const ca = Math.cos(rot), sa = Math.sin(rot), ux = ca * hw * fl, uy = sa * hw * fl, vx = -sa * hh, vy = ca * hh;
      c.globalAlpha = a * k;
      c.beginPath();
      c.moveTo(x - ux - vx, y - uy - vy); c.lineTo(x + ux - vx, y + uy - vy); c.lineTo(x + ux + vx, y + uy + vy); c.lineTo(x - ux + vx, y - uy + vy);
      c.closePath(); c.fill();
    }
    c.globalAlpha = 1;
    // "relampago": clarao roxo-avermelhado curto com faixas deslocadas
    const cyc = 7.3, ph = (t % cyc) / cyc, seed = Math.floor(t / cyc);
    if (ph < 0.035 || (ph > 0.05 && ph < 0.07)) {
      const rg = U.rng(seed * 13 + Math.floor(t * 24));
      c.fillStyle = `rgba(190,60,150,${0.14 * k})`;
      c.fillRect(0, 0, W, H);
      for (let i = 0; i < 6; i++) {
        const y = rg() * H, h = 4 + rg() * 18, dx = (rg() - 0.5) * 40;
        c.fillStyle = i % 2 ? `rgba(255,70,130,${0.24 * k})` : `rgba(80,220,255,${0.18 * k})`;
        c.fillRect(dx, y, W, h);
      }
      if (typeof Light !== 'undefined') Light.add(200 + U.rng(seed * 13)() * (W - 400), 200, 480, '#e070ff', 0.7 * k, 0.35);
    }
    const vg = c.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.95);
    vg.addColorStop(0, 'rgba(36,32,58,0)'); vg.addColorStop(1, `rgba(32,28,52,${0.45 * k})`);
    c.fillStyle = vg; c.fillRect(0, 0, W, H);
    c.restore();
  };
})();

// ------------------------------------------------------------ EFEITOS POR CHAPA (torres do jogador)
// Cada chapa tem as proprias torres nos mesmos encaixes (DATA.CHAPA_TORRES). Aqui ficam os desenhos das torres que
// mudaram de tema; o render.js e o vfx.js escolhem pela chapa (ladoV/ladoR, js/vfx.js) e as que nao mudaram seguem
// com o desenho de antes. Mesma regra do bloco acima: nada de gradiente nos lacos, sorteio fixo por efeito (rnd).
//   Verde-Amarela: Laranjal (semente, bagaco, suco) e Leite Condensado (lata, calda, batedeira, forma de pudim)
//   Vermelha: Churrascao da Picanha (espeto, labareda), Carro de Som (ondas, notas, ouvintes com sono) e
//   Taxa das Blusinhas (pacotinhos, blusinhas e o carimbo de %)
(function () {
  const rnd = (i, s) => { const v = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - Math.floor(v); };
  const eo = U.easeOutCubic;
  const LAR = { peel: '#ff9a1f', dark: '#c45a0c', pulp: '#ffcf6a', light: '#fff0c0' };
  // contorno fechado e macio (poca, respingo): n pontos com raio vezes ru(i), curvas pelos pontos medios
  const blob = (c, x, y, rx, ry, n, ru) => {
    const px = i => x + rx * ru(i % n) * Math.cos((i % n) / n * U.TAU), py = i => y + ry * ru(i % n) * Math.sin((i % n) / n * U.TAU);
    c.beginPath();
    c.moveTo((px(n - 1) + px(0)) / 2, (py(n - 1) + py(0)) / 2);
    for (let i = 0; i < n; i++) c.quadraticCurveTo(px(i), py(i), (px(i) + px(i + 1)) / 2, (py(i) + py(i + 1)) / 2);
    c.closePath();
  };

  // ---------------------------------------------------------------- Laranjal (Verde-Amarela)
  // Candidatura Laranja: semente cuspida, girando de leve, com respingos de suco atras
  A.chSeed = (c, p, t) => {
    c.save();
    c.translate(p.x, p.y); c.rotate(p.ang || 0);
    for (let i = 0; i < 3; i++) {
      c.globalAlpha = 0.8 - i * 0.24;
      A.circ(c, -6.5 - i * 4.2, Math.sin(t * 30 + i * 2) * 1.2, 1.6 - i * 0.35, i ? '#ffc24a' : '#ff9f2a');
    }
    c.globalAlpha = 1;
    c.rotate(Math.sin(t * 24 + (p.sx || 0)) * 0.25);
    c.beginPath();
    c.moveTo(4.8, 0);
    c.quadraticCurveTo(1.6, -3.1, -2.6, -2.3);
    c.quadraticCurveTo(-4.8, 0, -2.6, 2.3);
    c.quadraticCurveTo(1.6, 3.1, 4.8, 0);
    c.closePath();
    c.fillStyle = '#f6e7bc'; c.fill();
    c.strokeStyle = '#9c7432'; c.lineWidth = 1; c.stroke();
    A.ell(c, -0.6, -1, 1.9, 0.7, 'rgba(255,255,255,0.85)');
    c.restore();
  };
  // semente que caiu no chao (no lugar da nota espetada), ja no sistema girado do 'stuck'
  A.chSeedStuck = c => {
    A.ell(c, 0, 0.5, 3.4, 1.3, 'rgba(255,160,40,0.45)');
    c.beginPath();
    c.moveTo(0, 0.5); c.quadraticCurveTo(-2.6, -2.5, -1.6, -5.6); c.quadraticCurveTo(0, -7.6, 1.6, -5.6); c.quadraticCurveTo(2.6, -2.5, 0, 0.5);
    c.closePath();
    c.fillStyle = '#f6e7bc'; c.fill(); c.strokeStyle = '#9c7432'; c.lineWidth = 0.9; c.stroke();
    A.ell(c, -0.6, -4.6, 0.6, 1.3, 'rgba(255,255,255,0.8)');
  };
  // Nuvem de Bagaco: meia laranja espremida voando (desenhada na origem, o render.js ja girou)
  A.chHalfOrange = c => {
    A.ell(c, 0, 1.2, 7.2, 5.6, LAR.peel, LAR.dark, 1.2);
    A.ell(c, 0, -0.6, 5.8, 3.9, LAR.pulp, '#e89a2a', 0.8);
    c.strokeStyle = 'rgba(232,140,30,0.85)'; c.lineWidth = 0.7;
    c.beginPath();
    for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3; c.moveTo(0, -0.6); c.lineTo(Math.cos(a) * 5, -0.6 + Math.sin(a) * 3.3); }
    c.stroke();
    A.circ(c, 0, -0.6, 1.1, LAR.light);
    A.ell(c, -3.8, 2.6, 1.5, 0.8, 'rgba(255,255,255,0.4)');
  };
  // pedacinhos de bagaco: 0 = gomo de polpa, 1 = tirinha de casca, 2 = semente
  const pulpBit = (c, x, y, s, rot, kind) => {
    if (kind === 0) {
      c.save(); c.translate(x, y); c.rotate(rot);
      A.ell(c, 0, 0, 2.9 * s, 1.6 * s, '#ffc443', '#e2861c', 0.8);
      A.ell(c, -0.8 * s, -0.45 * s, 1.1 * s, 0.45 * s, 'rgba(255,255,255,0.75)');
      c.restore();
    } else if (kind === 1) {
      c.beginPath(); c.arc(x, y, 3.3 * s, rot, rot + 1.9);
      c.strokeStyle = LAR.dark; c.lineWidth = 2.7 * s; c.stroke();
      c.strokeStyle = LAR.peel; c.lineWidth = 1.6 * s; c.stroke();
    } else {
      A.ell(c, x, y, 1.7 * s, 1.1 * s, '#f6e7bc', '#9c7432', 0.7);
    }
  };
  // Nuvem de Bagaco no chao: poca de suco, nevoa de laranja, bagaco caindo girando e se amontoando
  A.chPulpZone = (c, z, t, fade) => {
    const r = z.r, s = z.x * 0.31 + z.y * 0.77;
    c.save();
    c.lineCap = 'round';
    c.globalAlpha = fade;
    A.ell(c, z.x, z.y, r, r * U.YS, 'rgba(255,170,50,0.2)', 'rgba(230,130,30,0.45)', 1.2);
    c.globalAlpha = fade * 0.7;
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * U.TAU + t * 0.35, d = r * 0.45 + Math.sin(t * 1.8 + i) * 5;
      A.circ(c, z.x + Math.cos(a) * d, z.y + Math.sin(a) * d * U.YS - 10 - Math.sin(t * 2 + i * 1.3) * 3, r * 0.3, 'rgba(255,196,96,0.3)');
    }
    c.globalAlpha = fade;
    // tres meias laranjas espremidas largadas no chao e o bagaco que vai se amontoando
    const grow = Math.min(1, z.t / 2.2);
    for (let i = 0; i < 3; i++) {
      const pk = U.clamp((grow - i * 0.25) * 3, 0, 1);
      if (pk <= 0) continue;
      const a = rnd(i + 200, s) * U.TAU, d = (0.25 + 0.45 * rnd(i + 210, s)) * r;
      c.save();
      c.translate(z.x + Math.cos(a) * d, z.y + Math.sin(a) * d * U.YS);
      c.scale(0.95 * pk, 0.8 * pk);
      A.chHalfOrange(c);
      c.restore();
    }
    const n = Math.floor(20 * grow);
    for (let i = 0; i < n; i++) {
      const a = rnd(i, s) * U.TAU, d = Math.sqrt(rnd(i + 30, s)) * r * 0.82;
      pulpBit(c, z.x + Math.cos(a) * d, z.y + Math.sin(a) * d * U.YS, 1.2, rnd(i + 60, s) * U.TAU, i % 3);
    }
    for (let i = 0; i < 10; i++) {
      const ph = (t * 0.6 + rnd(i + 90, s)) % 1;
      const a = rnd(i + 120, s) * U.TAU, d = Math.sqrt(rnd(i + 150, s)) * r * 0.85;
      c.globalAlpha = fade * Math.min(1, ph * 6, (1 - ph) * 8);
      pulpBit(c, z.x + Math.cos(a) * d + Math.sin(t * 2.6 + i) * 6, z.y + Math.sin(a) * d * U.YS - 8 - (1 - ph) * 80, 1.4, t * (3 + (i % 3)) + i, i % 3);
    }
    c.restore();
  };
  // rodela de laranja virando no ar
  const slice = (c, x, y, rr, rot, fl) => {
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(Math.max(0.2, Math.abs(fl)), 1);
    A.circ(c, 0, 0, rr, LAR.peel, LAR.dark, 1);
    A.circ(c, 0, 0, rr * 0.78, LAR.pulp);
    c.strokeStyle = '#fff2c8'; c.lineWidth = 0.8;
    c.beginPath();
    for (let i = 0; i < 3; i++) { const a = i * Math.PI / 3; c.moveTo(Math.cos(a) * rr * 0.72, Math.sin(a) * rr * 0.72); c.lineTo(-Math.cos(a) * rr * 0.72, -Math.sin(a) * rr * 0.72); }
    c.stroke();
    c.restore();
  };
  // Suco Estourado (Laranjao): o caixote estoura em suco, rodelas de laranja e lascas de madeira
  A.chJuice = (c, f, k) => {
    const r = f.r || 50, e = eo(k), s = f.x * 0.61 + f.y * 0.17;
    c.save();
    if (k < 0.22) {
      const kk = k / 0.22, rr = r * (0.25 + 0.4 * kk);
      c.globalAlpha = (1 - kk) * 0.7;
      A.ell(c, f.x, f.y - 8, rr, rr * 0.75, '#fff0c4');
    }
    if (k < 0.5) {
      const kk = k / 0.5, rr = r * (0.3 + 0.8 * eo(kk));
      c.globalAlpha = 1 - kk;
      A.ell(c, f.x, f.y, rr, rr * U.YS, null, '#ffb03a', 3 * (1 - kk) + 1);
    }
    if (k > 0.12) {
      const pk = eo(Math.min(1, (k - 0.12) * 4));
      c.globalAlpha = (1 - k) * 0.85;
      A.ell(c, f.x, f.y + 2, r * 0.5 * pk, r * 0.2 * pk, 'rgba(255,160,40,0.55)');
      A.ell(c, f.x - r * 0.1 * pk, f.y + 1, r * 0.18 * pk, r * 0.05 * pk + 0.3, 'rgba(255,240,200,0.7)');
    }
    c.globalAlpha = k < 0.6 ? 1 : (1 - k) / 0.4;
    for (let i = 0; i < 14; i++) {
      const a = rnd(i + 80, s) * U.TAU, d = r * (0.25 + 0.9 * e) * (0.5 + 0.5 * rnd(i + 90, s));
      const up = Math.sin(Math.min(1, k * 2) * Math.PI * 0.5) * 46 * rnd(i + 100, s) - 30 * k * k;
      const rr = 1.6 + 1.6 * rnd(i + 110, s);
      A.ell(c, f.x + Math.cos(a) * d, f.y - 8 + Math.sin(a) * d * 0.5 - up, rr, rr * 1.15, i % 3 ? '#ffb43a' : '#ffd36a');
    }
    for (let i = 0; i < 6; i++) {
      const a = rnd(i + 50, s) * U.TAU, sp = r * (0.5 + 0.6 * rnd(i + 60, s));
      const hgt = Math.max(0, Math.sin(Math.min(1, k * 1.4) * Math.PI)) * 34 * (0.6 + 0.4 * rnd(i + 70, s));
      c.save();
      c.translate(f.x + Math.cos(a) * sp * e, f.y - 2 + Math.sin(a) * sp * e * 0.5 - hgt);
      c.rotate(a + k * 9 * (rnd(i + 75, s) - 0.5));
      A.rect(c, -4, -1.1, 8, 2.2, '#d8a868', '#8a5a2a', 0.7);
      c.restore();
    }
    for (let i = 0; i < 8; i++) {
      const a = rnd(i, s) * U.TAU, d = r * (0.25 + 0.8 * e) * (0.55 + 0.45 * rnd(i + 10, s));
      const up = Math.sin(Math.min(1, k * 1.8) * Math.PI * 0.5) * 42 * (0.5 + rnd(i + 20, s)) - 26 * k * k;
      slice(c, f.x + Math.cos(a) * d + Math.sin(k * 9 + i) * 3, f.y - 6 + Math.sin(a) * d * 0.5 - up, 4.4,
        (rnd(i + 30, s) - 0.5) * 2 + k * 5 * (rnd(i + 40, s) - 0.5), Math.cos(k * 14 + i * 1.3));
    }
    c.restore();
  };

  // ---------------------------------------------------------------- Leite Condensado (Verde-Amarela)
  // lata de leite condensado sem letreiro (na origem, ja girada): branca, faixa azul com uma gota de leite, friso
  // amarelo e tampa de lata; a da Calda Quente vem aberta, transbordando calda e soltando vapor
  A.chCan = (c, s, hot, t) => {
    const bw = 6.4 * s, bh = 7 * s;
    A.rrect(c, -bw, -bh, bw * 2, bh * 2, 1.4 * s, '#f7f3ea', '#34405e', 1.2);
    A.rect(c, -bw + 0.6, -bh * 0.52, bw * 2 - 1.2, bh * 0.86, '#2f5fc4');
    A.rect(c, -bw + 0.6, bh * 0.34, bw * 2 - 1.2, 1.5 * s, '#ffd21f');
    c.beginPath();
    c.moveTo(0, -bh * 0.4); c.quadraticCurveTo(2.3 * s, -bh * 0.02, 0, bh * 0.2); c.quadraticCurveTo(-2.3 * s, -bh * 0.02, 0, -bh * 0.4);
    c.fillStyle = '#ffffff'; c.fill();
    A.line(c, -bw + 0.6, bh - 0.9 * s, bw - 0.6, bh - 0.9 * s, '#b8c0ca', 1.1 * s);
    A.ell(c, -bw * 0.52, 0, bw * 0.17, bh * 0.75, 'rgba(255,255,255,0.3)');
    A.ell(c, 0, -bh, bw, 1.9 * s, hot ? '#8a929e' : '#dfe4ea', '#6c7686', 1);
    if (!hot) { A.ell(c, 0, -bh, bw * 0.62, 1.05 * s, null, '#a7b0bc', 0.7); return; }
    A.ell(c, 0, -bh - 0.7 * s, bw * 0.86, 2.3 * s, '#d98a2b', '#8a4a12', 1);
    A.ell(c, -bw * 0.3, -bh - 1.3 * s, bw * 0.3, 0.75 * s, 'rgba(255,232,172,0.85)');
    A.line(c, bw * 0.55, -bh, bw * 0.6, -bh + (4 + Math.sin(t * 6)) * s, '#d98a2b', 1.8 * s);
    A.line(c, -bw * 0.68, -bh, -bw * 0.7, -bh + 2.6 * s, '#d98a2b', 1.5 * s);
    c.strokeStyle = 'rgba(255,255,255,0.75)'; c.lineWidth = 1.2; c.lineCap = 'round';
    for (const sx of [-2.2, 2.4]) {
      const y0 = -bh - 3 * s;
      c.beginPath(); c.moveTo(sx * s, y0); c.quadraticCurveTo(sx * s + 2.5 * Math.sin(t * 7 + sx), y0 - 4 * s, sx * s, y0 - 8 * s); c.stroke();
    }
  };
  // a lata estoura em leite condensado: clarao suave, coroa de gotas grossas, poca cremosa e a tampa voando
  // (fire = Calda Quente: as mesmas gotas em calda de caramelo)
  A.chMilkSplash = (c, f, k) => {
    const r = f.r || 40, e = eo(k), s = f.x * 0.37 + f.y * 0.53, hot = !!f.fire;
    const C1 = hot ? '#e09a3a' : '#fffaf0', C2 = hot ? '#b8661c' : '#efe2c2', HI = hot ? '#ffe2a8' : '#ffffff';
    const LN = hot ? 'rgba(120,60,10,0.6)' : 'rgba(150,130,100,0.55)';
    c.save();
    if (k < 0.25) {
      const kk = k / 0.25, rr = r * (0.25 + 0.35 * kk);
      c.globalAlpha = (1 - kk) * 0.5;
      A.ell(c, f.x, f.y - 8, rr, rr * 0.75, hot ? '#ffe0a0' : '#fffbe8');
    }
    // poca cremosa meio transparente (o adversario continua aparecendo por cima dela)
    const pk = eo(Math.min(1, k * 3.5));
    c.globalAlpha = 0.62 * (k < 0.7 ? 1 : (1 - k) / 0.3);
    blob(c, f.x, f.y + 2, r * 0.36 * pk + 0.5, r * 0.36 * pk * U.YS * 0.75 + 0.5, 10, i => 0.75 + 0.35 * rnd(i, s));
    c.fillStyle = C2; c.fill(); c.strokeStyle = LN; c.lineWidth = 1; c.lineJoin = 'round'; c.stroke();
    A.ell(c, f.x, f.y + 1, r * 0.3 * pk, r * 0.3 * pk * U.YS * 0.6, C1);
    A.ell(c, f.x - r * 0.1 * pk, f.y - 0.5, r * 0.12 * pk, r * 0.035 * pk + 0.4, HI);
    c.globalAlpha = k < 0.65 ? 1 : (1 - k) / 0.35;
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * U.TAU + rnd(i, s) * 0.5, d = r * (0.15 + 0.75 * e) * (0.55 + 0.45 * rnd(i + 12, s));
      const hgt = Math.sin(Math.min(1, k * 1.5) * Math.PI) * (20 + 22 * rnd(i + 24, s));
      const rr = (2.4 + 2 * rnd(i + 36, s)) * (1 - 0.4 * k);
      const x = f.x + Math.cos(a) * d, y = f.y - 4 + Math.sin(a) * d * 0.5 - hgt;
      A.ell(c, x, y, rr, rr * 1.2, C1, LN, 0.8);
      A.circ(c, x - rr * 0.35, y - rr * 0.4, rr * 0.3, HI);
    }
    if (!hot && r > 60) {
      for (let i = 0; i < 2; i++) {
        const a = i ? -0.6 : -2.5, d = r * 0.5 * e, hgt = Math.sin(Math.min(1, k * 1.3) * Math.PI) * 44;
        c.save();
        c.translate(f.x + Math.cos(a) * d, f.y - 6 - hgt);
        c.scale(Math.max(0.2, Math.abs(Math.cos(k * 16 + i))), 1);
        A.circ(c, 0, 0, 3.6, '#dfe4ea', '#6c7686', 0.9);
        A.circ(c, 0, 0, 2.2, null, '#a7b0bc', 0.6);
        c.restore();
      }
    }
    c.restore();
  };
  // Calda Quente: poca de calda de caramelo lisa e brilhante, bolhas estourando e fios de vapor
  A.chCaramelZone = (c, z, t, fade) => {
    const r = z.r, s = z.x * 0.53 + z.y * 0.29, grow = eo(Math.min(1, z.t * 3));
    c.save();
    c.globalAlpha = fade;
    blob(c, z.x, z.y, r * 0.9 * grow + 0.5, r * 0.9 * grow * U.YS + 0.5, 12, i => (0.8 + 0.2 * rnd(i, s)) * (0.97 + 0.03 * Math.sin(t * 2 + i)));
    c.fillStyle = 'rgba(176,96,24,0.66)'; c.fill();
    c.strokeStyle = 'rgba(110,52,10,0.55)'; c.lineWidth = 1.6; c.stroke();
    blob(c, z.x, z.y - 1, r * 0.6 * grow + 0.5, r * 0.6 * grow * U.YS * 0.8 + 0.5, 9, i => 0.85 + 0.15 * rnd(i + 20, s));
    c.fillStyle = 'rgba(226,146,56,0.72)'; c.fill();
    c.strokeStyle = 'rgba(255,236,190,0.75)'; c.lineWidth = 2; c.lineCap = 'round';
    c.beginPath(); c.ellipse(z.x - r * 0.12, z.y - r * 0.08, r * 0.42 * grow + 0.1, r * 0.2 * grow + 0.1, 0, Math.PI * 1.1, Math.PI * 1.6); c.stroke();
    for (let i = 0; i < 7; i++) {
      const ph = (t * 1.1 + rnd(i + 5, s)) % 1;
      const a = rnd(i + 10, s) * U.TAU, d = Math.sqrt(rnd(i + 15, s)) * r * 0.7 * grow;
      const bx = z.x + Math.cos(a) * d, by = z.y + Math.sin(a) * d * U.YS;
      if (ph < 0.8) {
        const br = 1 + 3.2 * ph;
        A.circ(c, bx, by - br * 0.5, br, 'rgba(236,160,64,0.95)', 'rgba(130,64,12,0.7)', 0.8);
        A.circ(c, bx - br * 0.35, by - br * 0.85, br * 0.28, 'rgba(255,245,220,0.9)');
      } else {
        const pk = (ph - 0.8) / 0.2;
        c.globalAlpha = fade * (1 - pk);
        A.circ(c, bx, by - 2, 2 + 4 * pk, null, 'rgba(255,220,160,0.9)', 1);
        c.globalAlpha = fade;
      }
    }
    c.strokeStyle = '#ffffff'; c.lineWidth = 2.2;
    for (let i = 0; i < 5; i++) {
      const ph = (t * 0.7 + rnd(i + 40, s)) % 1;
      const a = rnd(i + 45, s) * U.TAU, d = Math.sqrt(rnd(i + 50, s)) * r * 0.6;
      const x = z.x + Math.cos(a) * d, y = z.y + Math.sin(a) * d * U.YS - 4 - ph * 30;
      c.globalAlpha = fade * 0.55 * Math.sin(ph * Math.PI);
      c.beginPath(); c.moveTo(x, y + 8); c.quadraticCurveTo(x + 4 * Math.sin(t * 4 + i), y + 2, x, y - 6); c.stroke();
    }
    c.restore();
  };
  // Batedeira Industrial: cada batida espalha uma onda de massa cremosa com respingos na beirada
  A.chQuake = (c, f, k) => {
    const s = f.x * 0.71 + f.y * 0.13, rr = f.r * eo(k);
    c.save();
    c.globalAlpha = (1 - k) * 0.85;
    A.ell(c, f.x, f.y, rr, rr * U.YS, null, 'rgba(170,140,100,0.6)', 6 * (1 - k) + 2);
    A.ell(c, f.x, f.y, rr, rr * U.YS, null, '#fff3dc', 4 * (1 - k) + 1);
    A.ell(c, f.x, f.y, rr * 0.75, rr * 0.75 * U.YS, null, 'rgba(255,238,186,0.8)', 2.4);
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * U.TAU + rnd(i, s) * 0.4;
      const hgt = Math.sin(k * Math.PI) * (8 + 12 * rnd(i + 12, s));
      const x = f.x + Math.cos(a) * rr, y = f.y + Math.sin(a) * rr * U.YS - hgt;
      const br = 2.2 + 1.4 * rnd(i + 24, s);
      A.ell(c, x, y, br, br * 1.15, '#fffaf0', 'rgba(150,130,100,0.6)', 0.7);
      A.circ(c, x - br * 0.3, y - br * 0.4, br * 0.3, '#ffffff');
    }
    c.restore();
  };
  // Forma de Pudim: a forma de aluminio abre no chao cheia de calda, engole o adversario e um pudim sobe tremendo
  A.chPudim = (c, f, k, t) => {
    const open = Math.sin(Math.min(1, k) * Math.PI), s = f.x * 0.77 + f.y * 0.19;
    const rx = 30 * open + 2, ry = 12 * open + 1;
    c.save();
    A.ell(c, f.x, f.y, rx + 3 * open, ry + 1.6 * open, '#cfd5dc', '#6c7686', 1.6);
    A.ell(c, f.x, f.y + 0.6, rx, ry, '#5e2e0e');
    A.ell(c, f.x, f.y + 1.2 * open, rx * 0.9, ry * 0.78, '#a8561a');
    c.strokeStyle = 'rgba(255,220,160,0.7)'; c.lineWidth = 1.4; c.lineCap = 'round';
    c.beginPath(); c.ellipse(f.x - rx * 0.2, f.y - ry * 0.05, rx * 0.45, ry * 0.4, 0, Math.PI * 1.05, Math.PI * 1.6); c.stroke();
    for (let i = 0; i < 4; i++) {
      const ph = (k * 3 + rnd(i + 5, s)) % 1;
      if (ph > 0.8) continue;
      const bx = f.x + (rnd(i + 10, s) - 0.5) * rx * 1.2, by = f.y + 1 + (rnd(i + 15, s) - 0.5) * ry * 0.7, br = (0.8 + 2.4 * ph) * open;
      A.circ(c, bx, by - br * 0.5, br, '#c26a22', 'rgba(90,40,8,0.7)', 0.7);
      A.circ(c, bx - br * 0.35, by - br * 0.85, br * 0.28, 'rgba(255,240,210,0.85)');
    }
    // o tubo do meio da forma
    A.ell(c, f.x, f.y - 1.5 * open, rx * 0.2, ry * 0.26 + 0.5, '#e3e8ee', '#6c7686', 1);
    A.ell(c, f.x, f.y - 1.5 * open, rx * 0.1, ry * 0.12 + 0.3, '#8a929e');
    if (k > 0.3 && k < 0.92) {
      const pk = (k - 0.3) / 0.62, up = Math.sin(pk * Math.PI), wob = 1 + 0.12 * Math.sin(t * 26) * up;
      const h = 17 * up, w = 15 * up, by = f.y + 2, ty = by - h;
      if (w > 1.5) {
        c.save();
        c.translate(f.x, by); c.scale(1 / wob, wob); c.translate(-f.x, -by);
        c.beginPath(); c.moveTo(f.x - w, by); c.lineTo(f.x - w * 0.72, ty); c.lineTo(f.x + w * 0.72, ty); c.lineTo(f.x + w, by);
        c.quadraticCurveTo(f.x, by + w * 0.3, f.x - w, by); c.closePath();
        c.fillStyle = '#f6d27a'; c.fill(); c.strokeStyle = '#b07a2a'; c.lineWidth = 1.2; c.lineJoin = 'round'; c.stroke();
        A.ell(c, f.x - w * 0.55, by - h * 0.45, w * 0.1, h * 0.25, 'rgba(255,255,255,0.4)');
        A.ell(c, f.x - w * 0.45, ty + h * 0.22, w * 0.07, h * 0.18, '#a8561a');
        A.ell(c, f.x + w * 0.3, ty + h * 0.16, w * 0.07, h * 0.13, '#a8561a');
        A.ell(c, f.x, ty, w * 0.72, w * 0.22, '#a8561a', '#6e3410', 1);
        A.ell(c, f.x - w * 0.25, ty - w * 0.05, w * 0.22, w * 0.05 + 0.3, 'rgba(255,230,180,0.85)');
        c.restore();
      }
    }
    c.restore();
  };

  // ---------------------------------------------------------------- Churrascao da Picanha (Vermelha)
  // labareda em gota com a ponta para cima (fill ja escolhido); lean inclina a ponta
  A.chFlame = (c, x, y, h, w, lean) => {
    c.beginPath();
    c.moveTo(x - w, y);
    c.quadraticCurveTo(x - w * 0.9, y - h * 0.55, x + lean * h, y - h);
    c.quadraticCurveTo(x + w * 0.9, y - h * 0.55, x + w, y);
    c.quadraticCurveTo(x, y + w * 0.7, x - w, y);
    c.closePath(); c.fill();
  };
  // espeto de picanha na origem, ponta para +x: vareta de metal com tres pedacos tostados, capa de gordura e
  // as marquinhas da grelha
  A.chSkewer = (c, s) => {
    A.line(c, -12 * s, 0, 12.5 * s, 0, '#6f7480', 2.2 * s);
    A.line(c, -12 * s, -0.45 * s, 12.5 * s, -0.45 * s, '#d4d7dc', 0.9 * s);
    A.circ(c, -13.6 * s, 0, 1.9 * s, null, '#6f7480', 1.1 * s);
    for (let i = 0; i < 3; i++) {
      const x = -6.4 * s + i * 6.4 * s;
      A.rrect(c, x - 2.8 * s, -3.3 * s, 5.6 * s, 6.6 * s, 1.9 * s, '#b0583a', '#6e2e1e', 0.9);
      A.rrect(c, x - 2.6 * s, -3.6 * s, 5.2 * s, 2.1 * s, 1 * s, '#fbe6c4');
      A.ell(c, x - 1.1 * s, 0.6 * s, 0.9 * s, 1.6 * s, 'rgba(232,140,110,0.6)');
      c.strokeStyle = 'rgba(70,28,16,0.8)'; c.lineWidth = 0.8 * s;
      c.beginPath();
      c.moveTo(x - 1.8 * s, 2.6 * s); c.lineTo(x + 0.2 * s, -1.1 * s);
      c.moveTo(x + 0.4 * s, 2.8 * s); c.lineTo(x + 2.2 * s, -0.5 * s);
      c.stroke();
    }
    A.poly(c, [[12.4 * s, -1.1 * s], [15.4 * s, 0], [12.4 * s, 1.1 * s]], '#dfe2e6', '#6f7480', 0.6);
  };
  // espeto em brasa em qualquer angulo: labaredas sempre para cima (inclinadas contra o movimento) e o espeto
  A.chSkewerLit = (c, x, y, ang, s, t, seed) => {
    const ca = Math.cos(ang), sa = Math.sin(ang), lean = -ca * 0.35;
    c.fillStyle = 'rgba(255,128,36,0.85)';
    for (let i = 0; i < 3; i++) {
      const lx = (-6.4 + i * 6.4) * s, fl = 0.75 + 0.25 * Math.sin(t * 31 + i * 2.1 + seed);
      A.chFlame(c, x + ca * lx, y + sa * lx - 2.5 * s, (8 + 3 * fl) * s, 2.6 * s, lean);
    }
    c.save();
    c.translate(x, y); c.rotate(ang);
    if (ca < 0) c.scale(1, -1);
    A.chSkewer(c, s);
    c.restore();
    c.fillStyle = 'rgba(255,214,110,0.95)';
    for (let i = 0; i < 3; i++) {
      const lx = (-6.4 + i * 6.4) * s, fl = 0.75 + 0.25 * Math.sin(t * 27 + i * 1.7 + seed);
      A.chFlame(c, x + ca * lx, y + sa * lx - 3.4 * s, (4 + 2 * fl) * s, 1.4 * s, lean);
    }
  };
  // Picanha pra Todos: cada espeto cai da nuvem de fumaca de ponta, crava no chao balancando e chia
  A.chSkewerDrop = (c, f, k, t) => {
    const s = f.x * 0.83 + f.y * 0.11, fk = Math.min(1, k / 0.3);
    const dx = 0.12, dy = 0.99;
    c.save();
    c.lineCap = 'round';
    if (fk < 1) {
      const e = fk * fk, x = f.x - (1 - e) * 30, y = f.y - 10 - (1 - e) * 250;
      c.strokeStyle = 'rgba(214,206,198,0.5)'; c.lineWidth = 6;
      c.beginPath(); c.moveTo(x, y); c.lineTo(x - dx * 56, y - dy * 56); c.stroke();
      c.strokeStyle = 'rgba(255,170,70,0.9)'; c.lineWidth = 2;
      c.beginPath(); c.moveTo(x, y); c.lineTo(x - dx * 32, y - dy * 32); c.stroke();
      c.fillStyle = '#ffcf6a';
      for (let i = 0; i < 3; i++) { c.beginPath(); c.arc(x - dx * (14 + i * 13) + (rnd(i, s) - 0.5) * 8, y - dy * (14 + i * 13), 1.6 - i * 0.3, 0, U.TAU); c.fill(); }
      A.chSkewerLit(c, x, y, Math.atan2(dy, dx), 0.8, t, s);
    } else {
      const ik = (k - 0.3) / 0.7, ie = eo(ik);
      c.globalAlpha = 1 - ik;
      A.ell(c, f.x, f.y, 6 + 26 * ie, (6 + 26 * ie) * 0.45, null, '#ffd9a0', 2.4 * (1 - ik) + 0.5);
      c.fillStyle = '#ffb347';
      for (let i = 0; i < 6; i++) {
        const a = (i / 6) * U.TAU + rnd(i, s), d = 5 + 20 * ie * (0.6 + 0.4 * rnd(i + 7, s));
        c.beginPath(); c.arc(f.x + Math.cos(a) * d, f.y - 4 + Math.sin(a) * d * 0.55 - 10 * ie, 1.8 * (1 - ik) + 0.5, 0, U.TAU); c.fill();
      }
      for (let i = 0; i < 3; i++) A.circ(c, f.x + (i - 1) * 7, f.y - 8 - ie * 18 - i * 2, 3.5 + ie * 5, 'rgba(226,220,214,0.6)');
      c.globalAlpha = ik < 0.7 ? 1 : (1 - ik) / 0.3;
      c.save();
      const sw = Math.sin(ik * 22) * 0.3 * (1 - ik);
      c.translate(f.x, f.y + 1); c.rotate(Math.PI / 2 - 0.12 + sw); c.translate(-12.2, 0);
      A.chSkewer(c, 0.8);
      c.restore();
    }
    c.restore();
  };

  // ---------------------------------------------------------------- Carro de Som do Comicio (Vermelha)
  // nota musical: colcheia ou duas colcheias ligadas (contorno escuro por baixo, cor por cima)
  const noteG = (c, x, y, s, col, line, pair) => {
    c.save();
    c.translate(x, y); c.scale(s, s);
    c.beginPath();
    if (pair) {
      c.ellipse(-3, 3, 2.4, 1.8, -0.4, 0, U.TAU);
      c.moveTo(5.4, 2); c.ellipse(3, 2, 2.4, 1.8, -0.4, 0, U.TAU);
      c.rect(-1.3, -5, 1.2, 8); c.rect(4.7, -6, 1.2, 8);
      c.moveTo(-1.3, -5.2); c.lineTo(5.9, -6.4); c.lineTo(5.9, -4.2); c.lineTo(-1.3, -3); c.closePath();
    } else {
      c.ellipse(0, 3, 2.6, 1.9, -0.4, 0, U.TAU);
      c.rect(1.5, -5.5, 1.2, 8.5);
      c.moveTo(2.7, -5.5); c.quadraticCurveTo(6.6, -4, 5.6, -0.4); c.quadraticCurveTo(5.1, -2.9, 2.7, -3); c.closePath();
    }
    c.strokeStyle = line; c.lineWidth = 2; c.lineJoin = 'round'; c.stroke();
    c.fillStyle = col; c.fill();
    c.restore();
  };
  A.chNote = noteG;
  // ondas de som em leque com notas pegando carona (Jingle Chiclete: tudo cor de chiclete)
  A.chSoundGust = (c, p, t) => {
    const gum = !!p.sand;
    c.save();
    c.translate(p.x, p.y); c.rotate(p.ang);
    c.lineCap = 'round';
    for (let i = 0; i < 3; i++) {
      c.beginPath(); c.arc(-i * 6, 0, 9 - i * 2 + Math.sin(t * 30 + i) * 0.6, -1.0, 1.0);
      c.strokeStyle = 'rgba(90,24,34,0.32)'; c.lineWidth = 4.4 - i; c.stroke();
      c.strokeStyle = gum ? `rgba(255,140,200,${0.95 - i * 0.25})` : `rgba(255,246,240,${0.95 - i * 0.25})`;
      c.lineWidth = 2.6 - i * 0.6; c.stroke();
    }
    c.restore();
    for (let i = 0; i < 3; i++) {
      const a = t * 7 + i * 2.1, back = 4 + i * 8;
      const bx = p.x - Math.cos(p.ang) * back + Math.cos(a) * 2.5, by = p.y - Math.sin(p.ang) * back + Math.sin(a * 1.3 + i) * 6;
      noteG(c, bx, by, 0.95 - i * 0.15, gum ? (i % 2 ? '#ffb3d6' : '#ff7eb8') : (i % 2 ? '#ffffff' : '#e8423f'), '#5a1a22', i === 1);
    }
  };
  // impacto do som: ondas abrindo e notas pulando para fora; no Jingle Chiclete uma bola de chiclete enche e estoura
  A.chJingleBurst = (c, f, k) => {
    const e = eo(k), s = f.x * 0.45 + f.y * 0.55, r = f.r || 50, gum = f.kind === 'sandburst';
    c.save();
    c.lineCap = 'round';
    for (let i = 0; i < 2; i++) {
      const kk = Math.max(0, k - i * 0.12) / (1 - i * 0.12), rr = r * (0.2 + 0.8 * eo(kk));
      c.globalAlpha = 1 - kk;
      c.beginPath(); c.ellipse(f.x, f.y - 10, rr, rr * 0.45, 0, 0, U.TAU);
      c.strokeStyle = gum ? 'rgba(255,150,205,0.9)' : 'rgba(255,240,235,0.9)'; c.lineWidth = 3 - i; c.stroke();
    }
    if (gum) {
      if (k < 0.32) {
        const kk = k / 0.32, br = 4 + 9 * eo(kk);
        c.globalAlpha = 1;
        A.circ(c, f.x, f.y - 18, br, '#ff8cc6', '#c2457e', 1.2);
        A.ell(c, f.x - br * 0.35, f.y - 18 - br * 0.4, br * 0.3, br * 0.2, 'rgba(255,255,255,0.85)');
      } else {
        const kk = (k - 0.32) / 0.68, ke = eo(kk);
        c.globalAlpha = 1 - kk;
        for (let i = 0; i < 7; i++) {
          const a = (i / 7) * U.TAU + 0.3, d = 6 + 20 * ke;
          A.ell(c, f.x + Math.cos(a) * d, f.y - 18 + Math.sin(a) * d * 0.7 + 14 * kk * kk, 2.6 * (1 - kk * 0.5), 1.7, '#ff8cc6', '#c2457e', 0.8);
        }
      }
    }
    const pop = k < 0.18 ? U.easeOutBack(k / 0.18) : 1;
    c.globalAlpha = Math.pow(1 - k, 0.7);
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * U.TAU + rnd(i, s) * 0.6, d = r * (0.15 + 0.8 * e) * (0.65 + 0.35 * rnd(i + 9, s));
      noteG(c, f.x + Math.cos(a) * d, f.y - 12 + Math.sin(a) * d * 0.5 - 14 * k, pop * 1.05,
        gum ? (i % 2 ? '#ffb3d6' : '#ff7eb8') : (i % 2 ? '#ffffff' : '#e8423f'), '#5a1a22', i % 3 === 0);
    }
    c.restore();
  };
  // Discurso de 3 Horas: uma roda de ouvintes cochilando rola de volta pela estrada, soltando "Zzz"
  const SKIN = ['#f3cba5', '#d9a273', '#a8714a', '#f6dcc0', '#c48a5a'];
  const HAIR = ['#3a2a20', '#6b4a2a', '#2a2a2a', '#b98a40', '#e6e2da'];
  const sleeper = (c, x, y, hr, i, t) => {
    A.ell(c, x, y + hr * 1.3, hr * 1.3, hr * 0.8, i % 2 ? '#d6282b' : '#f4f1ea', 'rgba(60,30,30,0.6)', 1);
    A.circ(c, x, y, hr, SKIN[i % 5], 'rgba(80,45,30,0.6)', 1);
    c.beginPath(); c.arc(x, y - hr * 0.12, hr * 1.02, Math.PI * 1.04, Math.PI * 1.96); c.closePath();
    c.fillStyle = HAIR[(i + 2) % 5]; c.fill();
    c.strokeStyle = 'rgba(60,35,25,0.9)'; c.lineWidth = 0.9;
    c.beginPath();
    c.arc(x - hr * 0.38, y + hr * 0.05, hr * 0.22, 0.25, Math.PI - 0.25);
    c.moveTo(x + hr * (0.38 + 0.22 * Math.cos(0.25)), y + hr * (0.05 + 0.22 * Math.sin(0.25)));
    c.arc(x + hr * 0.38, y + hr * 0.05, hr * 0.22, 0.25, Math.PI - 0.25);
    c.stroke();
    if (i % 2 === 0) A.ell(c, x, y + hr * 0.52, hr * 0.17, hr * 0.22 * (0.6 + 0.4 * Math.sin(t * 3 + i)), '#7a3a2a');
  };
  const zee = (c, x, y, s) => {
    c.beginPath(); c.moveTo(x - s, y - s); c.lineTo(x + s, y - s); c.lineTo(x - s, y + s); c.lineTo(x + s, y + s);
    c.strokeStyle = '#3a3550'; c.lineWidth = s * 0.9 + 1.6; c.stroke();
    c.strokeStyle = '#eef0ff'; c.lineWidth = s * 0.55 + 0.4; c.stroke();
  };
  A.chListeners = (c, z, t, fade) => {
    c.save();
    c.globalAlpha = fade;
    A.shadow(c, z.x, z.y + 2, 28, 9, 0.3);
    c.lineCap = 'round'; c.lineJoin = 'round';
    for (let i = 0; i < 2; i++) {
      const ph = t * 8 + i * 3;
      c.beginPath(); c.ellipse(z.x, z.y - 4, 26 + i * 6, 8 + i * 2, 0, ph, ph + 2.2);
      c.strokeStyle = 'rgba(235,220,190,0.75)'; c.lineWidth = 2.4 - i; c.stroke();
    }
    const n = 5, R0 = 15, roll = t * 2.6;
    for (let pass = 0; pass < 2; pass++) {
      for (let i = 0; i < n; i++) {
        const an = roll + (i / n) * U.TAU, front = Math.sin(an) > 0;
        if (front !== !!pass) continue;
        const dep = 0.82 + 0.18 * Math.sin(an), bob = Math.abs(Math.sin(t * 6 + i * 1.3)) * 2.2;
        c.globalAlpha = fade * (front ? 1 : 0.85);
        sleeper(c, z.x + Math.cos(an) * R0, z.y - 13 + Math.sin(an) * R0 * 0.32 - bob, 5.6 * dep, i, t);
      }
      if (!pass) {
        c.globalAlpha = fade;
        sleeper(c, z.x + Math.sin(t * 2) * 2, z.y - 26 - Math.abs(Math.sin(t * 5)) * 2, 6.2, 5, t);
      }
    }
    for (let j = 0; j < 3; j++) {
      const ph = (t * 0.55 + j / 3) % 1;
      c.globalAlpha = fade * Math.min(1, ph * 5, (1 - ph) * 3);
      zee(c, z.x + 10 + ph * 16 + Math.sin(t * 2 + j) * 3, z.y - 40 - ph * 30, 2.2 + ph * 2.8);
    }
    c.restore();
  };

  // ---------------------------------------------------------------- Taxa das Blusinhas (Vermelha)
  const parcel = (c, x, y, s, rot) => {
    c.save(); c.translate(x, y); c.rotate(rot);
    A.rect(c, -4.2 * s, -3.3 * s, 8.4 * s, 6.6 * s, '#d9a865', '#7a5228', 0.9);
    A.rect(c, -4.2 * s, -3.3 * s, 8.4 * s, 1.9 * s, '#e8c08a');
    A.rect(c, -0.8 * s, -3.3 * s, 1.6 * s, 6.6 * s, '#f4e6c8');
    c.restore();
  };
  const blouse = (c, x, y, s, rot, col) => {
    c.save(); c.translate(x, y); c.rotate(rot);
    c.beginPath();
    c.moveTo(-4.6 * s, -2.6 * s); c.lineTo(-2 * s, -3.7 * s); c.lineTo(2 * s, -3.7 * s); c.lineTo(4.6 * s, -2.6 * s);
    c.lineTo(3.9 * s, -0.5 * s); c.lineTo(3 * s, -0.9 * s); c.lineTo(3 * s, 3.5 * s); c.lineTo(-3 * s, 3.5 * s);
    c.lineTo(-3 * s, -0.9 * s); c.lineTo(-3.9 * s, -0.5 * s); c.closePath();
    c.fillStyle = col; c.fill();
    c.strokeStyle = 'rgba(70,40,60,0.6)'; c.lineWidth = 0.8; c.lineJoin = 'round'; c.stroke();
    c.beginPath(); c.moveTo(-1.6 * s, -3.7 * s); c.lineTo(0, -1.7 * s); c.lineTo(1.6 * s, -3.7 * s); c.stroke();
    A.line(c, -3 * s, 1.2 * s, 3 * s, 1.2 * s, 'rgba(70,40,60,0.3)', 0.7);
    c.restore();
  };
  const BLUSA = ['#ff9ec4', '#a6d8f0', '#c9b6f2'];
  // carimbo vermelho de "%" (aro + sinal de porcentagem desenhado, sem fonte)
  const pctStamp = (c, x, y, s) => {
    c.save();
    c.translate(x, y); c.rotate(-0.25); c.scale(s, s);
    c.strokeStyle = '#d6282b'; c.lineCap = 'round';
    c.lineWidth = 1.6; c.beginPath(); c.arc(0, 0, 6.4, 0, U.TAU); c.stroke();
    c.lineWidth = 1.3;
    c.beginPath();
    c.moveTo(-1.1, -2.3); c.arc(-2.2, -2.3, 1.1, 0, U.TAU);
    c.moveTo(3.3, 2.3); c.arc(2.2, 2.3, 1.1, 0, U.TAU);
    c.moveTo(2.8, -3.4); c.lineTo(-2.8, 3.4);
    c.stroke();
    c.restore();
  };
  // renda da onda: pacotinhos, blusinhas dobradas e moedas pulam da loja; o carimbo de % bate no pacote do meio
  A.chParcels = (c, f, k) => {
    c.save();
    let sx = f.x, sy = f.y;
    for (let i = 0; i < 7; i++) {
      const a = -Math.PI / 2 + (i - 3) * 0.34, sp = 46 + (i % 3) * 8;
      const x = f.x + Math.cos(a) * sp * k, y = f.y + Math.sin(a) * sp * k + 70 * k * k;
      c.globalAlpha = 1 - k;
      const m = i % 3, rot = (i - 3) * 0.25 + k * 3 * (i % 2 ? 1 : -1);
      if (m === 0) parcel(c, x, y, 1.35, i === 3 ? rot * 0.3 : rot);
      else if (m === 1) blouse(c, x, y, 1.35, rot * 0.6, BLUSA[i % 3]);
      else A.coin(c, x, y, 4.4);
      if (i === 3) { sx = x; sy = y; }
    }
    if (k > 0.18 && k < 0.95) {
      const kk = (k - 0.18) / 0.77, sc = kk < 0.14 ? 2 - U.easeOutBack(kk / 0.14) : 1;
      c.globalAlpha = (kk < 0.7 ? 1 : (1 - kk) / 0.3) * Math.min(1, kk / 0.05);
      pctStamp(c, sx + 1, sy, sc * 1.3);
    }
    c.restore();
  };
})();
