'use strict';
// Kit de interface (v2): escala de tipos, cores semanticas, glifos de atributo e componentes estruturados
// (cartao, chip, pilula de preco, linhas de atributo e o tooltip em cartao). Regras: fonte minima 13 px para
// informacao, no maximo uma linha curta de descricao e o resto em linhas "icone + rotulo + valor (-> proximo)".

const TYPE = { display: 38, h1: 24, h2: 19, body: 15, label: 13, cap: 11 };
const UIK = {
  // pele da mata (as mesmas cores da tabela SOFT do art_world.js): placa de madeira com miolo creme
  ink: '#5a3a22', inkSoft: '#8a6646', line: '#e2c79a', card: '#fbf1dc', card2: '#f3e2c2', zebra: 'rgba(233,208,165,0.45)',
  wood1: '#efcb94', wood2: '#d9a86a', woodLine: '#9a6236',
  good: '#3f8f3a', bad: '#cf5a48', gold: '#b7791f', tag: '#3f7f3a',
  // cor de cada atributo (glifo e realce)
  G: {
    dmg: '#de6a4e', rate: '#4f97d0', range: '#6c7fd6', area: '#e8963a', hp: '#e3647a', armor: '#7d8a9a', mres: '#9a6ad8',
    speed: '#3fb0a0', slow: '#4fa6d6', poison: '#58a848', fire: '#ef7a2a', gold: '#e0a83a', push: '#6fb4d8', pierce: '#b0784a',
    chain: '#e5b52e', stun: '#e8a83a', heal: '#45b868', time: '#8a7a6a', flying: '#6f98c8', soldier: '#b07a4a', eye: '#2f8f8a',
    lives: '#e04a5a', star: '#f0b83a', skull: '#6a5a62', crit: '#d9644a', magic: '#9a6ad8', wet: '#3fa9d6', freeze: '#7fc8e8', income: '#e0a83a',
  },
};

const ui_font = (size, weight) => `${weight || 800} ${size}px ${FONT_UI}`;

// texto sem contorno (o padrao da UI nova); devolve a largura
A.label = (c, str, x, y, size, color, align, weight) => {
  c.font = ui_font(size, weight);
  c.textAlign = align || 'left';
  c.textBaseline = 'middle';
  c.fillStyle = color || UIK.ink;
  c.fillText(str, x, y);
  return c.measureText(str).width;
};
A.measure = (c, str, size, weight) => { c.font = ui_font(size, weight); return c.measureText(str).width; };

// ---------------------------------------------------------------- glifos de atributo (desenhados, nitidos em 14-20 px)
A.glyph = (c, kind, x, y, s, color) => {
  const col = color || UIK.G[kind] || UIK.inkSoft;
  const r = s / 2;
  c.save();
  c.translate(x, y);
  c.fillStyle = col;
  c.strokeStyle = col;
  c.lineCap = 'round';
  c.lineJoin = 'round';
  const P = pts => { c.beginPath(); c.moveTo(pts[0][0] * r, pts[0][1] * r); for (let i = 1; i < pts.length; i++) c.lineTo(pts[i][0] * r, pts[i][1] * r); c.closePath(); c.fill(); };
  const ring = (rr, w) => { c.lineWidth = w * r; c.beginPath(); c.arc(0, 0, rr * r, 0, U.TAU); c.stroke(); };
  const dot = (dx, dy, rr) => { c.beginPath(); c.arc(dx * r, dy * r, rr * r, 0, U.TAU); c.fill(); };
  switch (kind) {
    case 'dmg': case 'crit':   // espada inclinada
      c.rotate(-Math.PI / 4);
      P([[-0.16, 0.25], [-0.16, -0.75], [0, -1], [0.16, -0.75], [0.16, 0.25]]);
      c.fillRect(-0.45 * r, 0.22 * r, 0.9 * r, 0.18 * r);
      c.fillRect(-0.09 * r, 0.38 * r, 0.18 * r, 0.42 * r);
      dot(0, 0.88, 0.13);
      if (kind === 'crit') { c.rotate(Math.PI / 4); dot(0.62, -0.62, 0.22); }
      break;
    case 'rate': case 'time':  // cronometro
      ring(0.72, 0.2);
      c.fillRect(-0.16 * r, -1.02 * r, 0.32 * r, 0.22 * r);
      c.lineWidth = 0.17 * r;
      c.beginPath(); c.moveTo(0, 0); c.lineTo(0, -0.45 * r); c.moveTo(0, 0); c.lineTo(0.34 * r, 0.16 * r); c.stroke();
      if (kind === 'rate') { c.beginPath(); c.moveTo(0.75 * r, -0.75 * r); c.lineTo(0.95 * r, -0.55 * r); c.stroke(); }
      break;
    case 'range':              // alvo
      ring(0.78, 0.16); ring(0.42, 0.16); dot(0, 0, 0.16);
      break;
    case 'area':               // explosao
      c.beginPath();
      for (let i = 0; i < 16; i++) { const a = i * Math.PI / 8, rr = i % 2 ? 0.45 : 0.98; c.lineTo(Math.cos(a) * rr * r, Math.sin(a) * rr * r); }
      c.closePath(); c.fill();
      break;
    case 'hp': case 'lives': case 'heal':
      if (kind === 'heal') { c.fillRect(-0.24 * r, -0.85 * r, 0.48 * r, 1.7 * r); c.fillRect(-0.85 * r, -0.24 * r, 1.7 * r, 0.48 * r); break; }
      c.beginPath();
      c.moveTo(0, 0.85 * r);
      c.bezierCurveTo(-1.15 * r, 0.05 * r, -0.7 * r, -1.05 * r, 0, -0.42 * r);
      c.bezierCurveTo(0.7 * r, -1.05 * r, 1.15 * r, 0.05 * r, 0, 0.85 * r);
      c.fill();
      break;
    case 'armor': case 'mres': // escudo
      c.beginPath();
      c.moveTo(0, -0.95 * r); c.lineTo(0.8 * r, -0.62 * r); c.lineTo(0.72 * r, 0.15 * r);
      c.quadraticCurveTo(0.5 * r, 0.7 * r, 0, 0.98 * r); c.quadraticCurveTo(-0.5 * r, 0.7 * r, -0.72 * r, 0.15 * r); c.lineTo(-0.8 * r, -0.62 * r);
      c.closePath(); c.fill();
      c.fillStyle = 'rgba(255,255,255,0.55)';
      if (kind === 'mres') { A.star(c, 0, 0, r * 0.42, 'rgba(255,255,255,0.85)'); } else c.fillRect(-0.08 * r, -0.65 * r, 0.16 * r, 1.3 * r);
      break;
    case 'speed':              // seta dupla
      for (const ox of [-0.42, 0.18]) P([[ox - 0.25, -0.7], [ox + 0.45, 0], [ox - 0.25, 0.7], [ox - 0.05, 0]]);
      break;
    case 'slow':               // caracol
      ring(0.42, 0.2);
      c.fillRect(-0.95 * r, 0.42 * r, 1.9 * r, 0.3 * r);
      dot(0.95, 0.25, 0.18);
      break;
    case 'poison': case 'wet': // gota
      c.beginPath();
      c.moveTo(0, -1 * r);
      c.bezierCurveTo(0.35 * r, -0.45 * r, 0.78 * r, 0, 0.72 * r, 0.35 * r);
      c.arc(0, 0.32 * r, 0.72 * r, 0, Math.PI);
      c.bezierCurveTo(-0.78 * r, 0, -0.35 * r, -0.45 * r, 0, -1 * r);
      c.fill();
      c.fillStyle = 'rgba(255,255,255,0.6)';
      dot(-0.28, 0.32, 0.16);
      break;
    case 'fire':
      c.beginPath();
      c.moveTo(0, -1 * r);
      c.bezierCurveTo(0.7 * r, -0.35 * r, 0.9 * r, 0.25 * r, 0.6 * r, 0.7 * r);
      c.quadraticCurveTo(0, 1.15 * r, -0.6 * r, 0.7 * r);
      c.bezierCurveTo(-0.9 * r, 0.2 * r, -0.4 * r, -0.2 * r, -0.2 * r, -0.5 * r);
      c.quadraticCurveTo(0.05 * r, -0.2 * r, 0, -1 * r);
      c.fill();
      c.fillStyle = '#ffd36a';
      c.beginPath(); c.ellipse(0, 0.5 * r, 0.28 * r, 0.36 * r, 0, 0, U.TAU); c.fill();
      break;
    case 'gold': case 'income':
      c.beginPath(); c.arc(0, 0, 0.88 * r, 0, U.TAU); c.fill();
      c.fillStyle = 'rgba(255,240,190,0.85)';
      c.beginPath(); c.arc(0, 0, 0.58 * r, 0, U.TAU); c.fill();
      c.fillStyle = col;
      c.fillRect(-0.1 * r, -0.4 * r, 0.2 * r, 0.8 * r);
      break;
    case 'push': case 'flying': // rajada de vento / asa
      c.lineWidth = 0.2 * r;
      if (kind === 'flying') {
        c.beginPath(); c.moveTo(-0.9 * r, 0.2 * r); c.quadraticCurveTo(-0.2 * r, -1.0 * r, 0.95 * r, -0.75 * r);
        c.quadraticCurveTo(0.4 * r, -0.4 * r, 0.75 * r, -0.15 * r); c.quadraticCurveTo(0.2 * r, 0.05 * r, 0.5 * r, 0.35 * r);
        c.quadraticCurveTo(-0.2 * r, 0.6 * r, -0.9 * r, 0.2 * r); c.fill();
        break;
      }
      for (const [yy, l] of [[-0.5, 0.75], [0, 1], [0.5, 0.6]]) {
        c.beginPath(); c.moveTo(-0.9 * r, yy * r); c.lineTo((l - 0.3) * r, yy * r);
        c.arc((l - 0.3) * r, (yy - 0.22) * r, 0.22 * r, Math.PI / 2, -Math.PI / 2, true); c.stroke();
      }
      break;
    case 'pierce':             // flecha
      c.rotate(-Math.PI / 4);
      c.fillRect(-0.07 * r, -0.55 * r, 0.14 * r, 1.45 * r);
      P([[-0.32, -0.45], [0, -1.02], [0.32, -0.45]]);
      P([[-0.07, 0.6], [-0.38, 0.95], [-0.38, 0.62], [-0.07, 0.3]]);
      P([[0.07, 0.6], [0.38, 0.95], [0.38, 0.62], [0.07, 0.3]]);
      break;
    case 'chain':              // raio
      P([[0.2, -1], [-0.55, 0.12], [-0.05, 0.12], [-0.25, 1], [0.6, -0.2], [0.08, -0.2], [0.35, -1]]);
      break;
    case 'stun':               // estrelinhas girando
      A.star(c, 0, -0.3 * r, r * 0.55, col);
      A.star(c, -0.6 * r, 0.5 * r, r * 0.35, col);
      A.star(c, 0.6 * r, 0.5 * r, r * 0.35, col);
      break;
    case 'freeze':             // floco
      c.lineWidth = 0.17 * r;
      for (let i = 0; i < 3; i++) { c.save(); c.rotate(i * Math.PI / 3); c.beginPath(); c.moveTo(0, -0.95 * r); c.lineTo(0, 0.95 * r); c.stroke(); c.restore(); }
      break;
    case 'soldier':            // elmo
      c.beginPath(); c.arc(0, 0.1 * r, 0.72 * r, Math.PI, 0); c.lineTo(0.72 * r, 0.75 * r); c.lineTo(0.25 * r, 0.75 * r); c.lineTo(0.25 * r, 0.25 * r);
      c.lineTo(-0.25 * r, 0.25 * r); c.lineTo(-0.25 * r, 0.75 * r); c.lineTo(-0.72 * r, 0.75 * r); c.closePath(); c.fill();
      c.fillRect(-0.1 * r, -0.95 * r, 0.2 * r, 0.4 * r);
      break;
    case 'eye':
      c.beginPath(); c.moveTo(-0.95 * r, 0); c.quadraticCurveTo(0, -0.85 * r, 0.95 * r, 0); c.quadraticCurveTo(0, 0.85 * r, -0.95 * r, 0); c.fill();
      c.fillStyle = '#fff'; dot(0, 0, 0.36);
      c.fillStyle = col; dot(0, 0, 0.2);
      break;
    case 'skull':
      c.beginPath(); c.arc(0, -0.15 * r, 0.78 * r, 0, U.TAU); c.fill();
      c.fillRect(-0.45 * r, 0.3 * r, 0.9 * r, 0.55 * r);
      c.fillStyle = '#fff';
      dot(-0.3, -0.12, 0.2); dot(0.3, -0.12, 0.2);
      c.fillRect(-0.06 * r, 0.32 * r, 0.12 * r, 0.5 * r);
      break;
    case 'star': case 'magic':
      A.star(c, 0, 0, r * 0.95, col);
      break;
    default:
      dot(0, 0, 0.5);
  }
  c.restore();
};

// ---------------------------------------------------------------- componentes
A.card = (c, x, y, w, h, o = {}) => {
  const r = o.r || 18;
  if (o.variant === 'glass') {
    A.softShadow(c, x, y, w, h, r, 18, 0.3, 6, 'rgba(98,62,36,0.92)');
    A.rrect(c, x, y, w, h, r, null, 'rgba(255,226,180,0.35)', 1.5);
    return;
  }
  // moldura pintada do conceito (sprites/ui/painel) quando carregou; senao a placa desenhada abaixo
  if (o.skin !== false && A.skin && A.skin('painel')) { A.panel(c, x, y, w, h, { r }); return; }
  // placa de madeira (aro) com miolo creme e um raminho de cipo no canto
  A.softShadow(c, x, y, w, h, r, 22, 0.28, 8, UIK.wood2);
  const g = c.createLinearGradient(0, y, 0, y + h);
  g.addColorStop(0, UIK.wood1);
  g.addColorStop(1, UIK.wood2);
  A.rrect(c, x, y, w, h, r, g, UIK.woodLine, 2);
  A.rrect(c, x + 5, y + 5, w - 10, h - 10, r - 4, UIK.card, 'rgba(154,98,54,0.35)', 1.2);
  if (o.vine !== false && A.vine) A.vine(c, x + 6, y + 8, 1, 1, 0.75, o.flower || (SOFT.flower && SOFT.flower[0]));
};

// chip arredondado com icone opcional; devolve a largura
A.chip = (c, x, y, str, o = {}) => {
  const size = o.size || 12, h = o.h || 22;
  const tw = A.measure(c, str, size, 800);
  const w = tw + 18 + (o.icon ? 18 : 0);
  const col = o.color || UIK.inkSoft;
  A.rrect(c, x, y - h / 2, w, h, h / 2, o.bg || U.rgba(col, 0.13), o.border || U.rgba(col, 0.45), 1.2);
  let tx = x + 9;
  if (o.icon) { A.glyph(c, o.icon, x + 16, y, 13, col); tx += 18; }
  A.label(c, str, tx, y + 0.5, size, o.ink || U.shade(col, -0.3), 'left', 800);
  return w;
};

// pilula de preco: creme com borda dourada (ou coral quando falta ouro); devolve a largura
A.pricePill = (c, x, y, cost, ok, o = {}) => {
  const size = o.size || 15, h = o.h || 26;
  const s = String(cost);
  const w = A.measure(c, s, size, 900) + h + 14;
  const left = o.align === 'center' ? x - w / 2 : x;
  A.rrect(c, left, y - h / 2, w, h, h / 2, ok ? '#fff3d6' : '#fde5df', ok ? '#e2b25e' : '#ea8b7c', 1.6);
  A.coin(c, left + h / 2 + 1, y, h * 0.3);
  A.label(c, s, left + h + 4, y + 0.5, size, ok ? '#9a6420' : '#c2564a', 'left', 900);
  return w;
};

// linhas de atributo: [{g, label, value, next, good}] -> altura usada
A.statRows = (c, x, y, w, rows, o = {}) => {
  const rh = o.rh || 27;
  rows.forEach((row, i) => {
    const yy = y + i * rh + rh / 2;
    // cada linha numa faixa de madeira clara, como no cartao do conceito
    A.rrect(c, x, yy - rh / 2 + 1.5, w, rh - 3, 9, 'rgba(226,186,128,0.3)', 'rgba(154,98,54,0.2)', 1);
    A.glyph(c, row.g, x + 15, yy, 15);
    A.label(c, row.label, x + 30, yy + 0.5, TYPE.label, UIK.inkSoft, 'left', 700);
    let vx = x + w - 10;
    if (row.next != null && row.next !== row.value) {
      const nw = A.label(c, String(row.next), vx, yy + 0.5, 15, row.good === false ? UIK.bad : UIK.good, 'right', 900);
      vx -= nw + 6;
      A.label(c, '→', vx, yy, 13, UIK.inkSoft, 'right', 800);
      vx -= 18;
      A.label(c, String(row.value == null ? '—' : row.value), vx, yy + 0.5, 14, UIK.inkSoft, 'right', 800);
    } else {
      A.label(c, String(row.value), vx, yy + 0.5, 15, UIK.ink, 'right', 900);
    }
  });
  return rows.length * rh;
};

// botao pintado (sprites/ui/botao_*): aro de madeira com cipo e miolo de raio r em (x, y); false se a peca nao carregou
// fonte 256x247: miolo com centro (128, 124) e raio 68, aro ate ~108
A.knob = (c, x, y, r, name = 'botao_creme') => {
  const im = A.skin && A.skin(name);
  if (!im) return false;
  const k = r / 68;
  c.save();
  c.imageSmoothingEnabled = true;
  c.imageSmoothingQuality = 'high';
  c.drawImage(im, x - 128 * k, y - 124 * k, im.naturalWidth * k, im.naturalHeight * k);
  c.restore();
  return true;
};

// medalhao redondo com o icone (sprite quando existir)
A.medal = (c, name, x, y, r, o = {}) => {
  if (A.knob(c, x, y, r * 0.8)) {
    A.icon(c, name, x, y, r * 0.72, { tier: o.tier || 1, time: App.time });
    return;
  }
  A.circ(c, x, y + 1.5, r, 'rgba(120,80,40,0.16)');
  A.circ(c, x, y, r, o.bg || UIK.card2, o.ring || UIK.line, 2);
  A.icon(c, name, x, y, r * 0.78, { tier: o.tier || 1, time: App.time });
};

// tooltip em cartao: {x, y, icon, title, tag, pips, desc, rows, chips, bullets, cost, ok, max, note, w}
A.tipCard = (c, tip) => {
  const pad = A.skin && A.skin('painel') ? 20 : 16, w = tip.w || 340, inner = w - pad * 2; // a moldura pintada e mais grossa
  const desc = tip.desc ? A.wrap(c, tip.desc, inner, 14, 600).slice(0, 2) : [];
  const head = 56;
  const chipsH = tip.chips && tip.chips.length ? 30 : 0;
  const bul = tip.bullets || [];
  const footer = tip.cost != null || tip.max || tip.footer ? 46 : 0;
  const note = tip.note ? 22 : 0;
  const rows = tip.rows || [];
  const h = pad + head + (desc.length ? desc.length * 19 + 8 : 0) + (rows.length ? rows.length * 27 + 8 : 0) + chipsH +
    (bul.length ? bul.length * 44 + 6 : 0) + note + footer + pad - (footer ? 6 : 0);
  let x = tip.x + 104, y = tip.y - h / 2;
  if (x + w > W - 10) x = tip.x - 104 - w;
  x = U.clamp(x, 10, W - w - 10);
  y = U.clamp(y, 74, H - h - 10);
  A.card(c, x, y, w, h);
  // cabecalho: medalhao, titulo e etiqueta
  let yy = y + pad;
  const knob = !!(A.skin && A.skin('botao_creme')); // o botao pintado tem aro largo: empurra o titulo
  const hx = tip.icon ? x + pad + (knob ? 64 : 50) : x + pad;
  if (tip.icon) A.medal(c, tip.icon, x + pad + (knob ? 26 : 22), yy + 22, 23, { tier: tip.tier });
  if (tip.tag) {
    const tw = A.label(c, tip.tag.toUpperCase(), hx, yy + 10, TYPE.cap, tip.tagColor || UIK.tag, 'left', 900);
    if (tip.pips != null) for (let i = 0; i < 3; i++) A.circ(c, hx + tw + 12 + i * 11, yy + 10, 4, i < tip.pips ? '#f0b83a' : 'rgba(150,110,80,0.25)');
  }
  A.label(c, tip.title, hx, yy + (tip.tag ? 32 : 22), TYPE.h2, UIK.ink, 'left', 900);
  yy += head;
  if (desc.length) {
    desc.forEach((l, i) => A.label(c, l, x + pad, yy + 8 + i * 19, 14, UIK.inkSoft, 'left', 600));
    yy += desc.length * 19 + 8;
  }
  if (rows.length) {
    yy += A.statRows(c, x + pad - 4, yy, inner + 8, rows) + 8;
  }
  if (chipsH) {
    let cx = x + pad;
    for (const ch of tip.chips) {
      const o = typeof ch === 'string' ? { text: ch } : ch;
      const cw = A.measure(c, o.text, 12, 800) + 18 + (o.icon ? 18 : 0);
      if (cx + cw > x + w - pad) break;
      cx += A.chip(c, cx, yy + 12, o.text, o) + 6;
    }
    yy += chipsH;
  }
  for (const b of bul) {
    A.rrect(c, x + pad - 4, yy + 2, inner + 8, 40, 10, 'rgba(255,255,255,0.7)', UIK.line, 1.2);
    A.medal(c, b.icon, x + pad + 15, yy + 22, 15);
    A.label(c, b.title, x + pad + 38, yy + 14, 14, UIK.ink, 'left', 900);
    const t = A.wrap(c, b.text, inner - 44, 12, 700)[0] || '';
    A.label(c, t, x + pad + 38, yy + 31, 12, UIK.inkSoft, 'left', 700);
    yy += 44;
  }
  if (bul.length) yy += 6;
  if (note) {
    A.glyph(c, tip.noteIcon || 'star', x + pad + 7, yy + 10, 12, tip.noteColor || UIK.G.eye);
    A.label(c, tip.note, x + pad + 20, yy + 10.5, 12.5, tip.noteColor || U.shade(UIK.G.eye, -0.2), 'left', 800);
    yy += note;
  }
  if (footer) {
    A.line(c, x + 12, yy + 4, x + w - 12, yy + 4, UIK.line, 1.5);
    const fy = yy + 26;
    if (tip.max) {
      A.chip(c, x + pad, fy, 'Nível máximo', { color: UIK.G.star, icon: 'star', size: 13, h: 26 });
    } else if (tip.cost != null) {
      const pw = A.pricePill(c, x + pad, fy, tip.cost, tip.ok);
      const msg = tip.ok ? (tip.action || 'Clique para comprar') : `Faltam ${tip.cost - (tip.gold || 0)} de verba`;
      A.label(c, msg, x + pad + pw + 12, fy + 0.5, 13, tip.ok ? UIK.good : UIK.bad, 'left', 800);
    } else if (tip.footer) {
      A.label(c, tip.footer, x + pad, fy + 0.5, 13, UIK.inkSoft, 'left', 800);
    }
  }
};
