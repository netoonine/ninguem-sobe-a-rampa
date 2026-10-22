'use strict';
// Interface (modo imediato): telas, menus, HUD e entrada do mouse.

const UI = {
  regions: [], hot: null, mx: -1, my: -1, cursor: 'default', tip: null,
  begin() { this.regions = []; this.tip = null; },
  add(key, shape, cb, cursor) {
    this.regions.push({ key, shape, cb, cursor: cursor || 'pointer' });
    return this.hot === key;
  },
  rect(key, x, y, w, h, cb, cursor) { return this.add(key, { x, y, w, h }, cb, cursor); },
  circle(key, x, y, r, cb, cursor) { return this.add(key, { cx: x, cy: y, r }, cb, cursor); },
  hit(s, x, y) {
    if (s.r != null) return (x - s.cx) * (x - s.cx) + (y - s.cy) * (y - s.cy) <= s.r * s.r;
    return x >= s.x && x <= s.x + s.w && y >= s.y && y <= s.y + s.h;
  },
  end() {
    let hot = null, cur = 'default';
    for (let i = this.regions.length - 1; i >= 0; i--) {
      const r = this.regions[i];
      if (this.hit(r.shape, this.mx, this.my)) { hot = r.key; cur = r.cursor; break; }
    }
    if (hot !== this.hot && hot && cur === 'pointer') Snd.play('hover', 1);
    this.hot = hot;
    this.cursor = cur;
  },
  click(x, y, btn) {
    for (let i = this.regions.length - 1; i >= 0; i--) {
      const r = this.regions[i];
      if (this.hit(r.shape, x, y)) { if (r.cb) r.cb(x, y, btn); return true; }
    }
    return false;
  },
  blocker(key) { this.rect(key || 'blocker', 0, 0, W, H, () => {}, 'default'); },
  setTip(x, y, title, lines, o) { this.tip = Object.assign({ x, y, title, lines }, o || {}); },
};

// ------------------------------------------------------------ ponte para o kit de UI (js/ui_kit.js)
// Usa o componente do kit quando ele existe; sem ele, desenha um equivalente simples (mesma assinatura).
const UKB = {
  glyph(c, g, x, y, s) {
    if (A.glyph) return A.glyph(c, g, x, y, s);
    A.circ(c, x, y, s * 0.38, U.rgba(UKB_GLYPH[g] || '#c99a72', 0.85));
  },
  chip(c, x, y, text, o = {}) {
    if (A.chip) return A.chip(c, x, y, text, o);
    c.font = `800 13px ${FONT_UI}`;
    const w = c.measureText(text).width + (o.icon ? 36 : 22);
    A.rrect(c, x, y - 13, w, 26, 13, o.bg || '#fff6e6', o.color ? U.rgba(o.color, 0.75) : SOFT.line, 1.5);
    if (o.icon) this.glyph(c, o.icon, x + 15, y, 15);
    A.text(c, text, x + (o.icon ? 27 : 11), y + 0.5, 13, o.color ? U.shade(o.color, -0.35) : SOFT.ink, 'left', null, false);
    return w;
  },
  rows(c, x, y, w, rows) {
    if (A.statRows) return A.statRows(c, x, y, w, rows);
    let yy = y;
    for (const r of rows) {
      this.glyph(c, r.g, x + 11, yy + 13, 18);
      A.text(c, r.label, x + 28, yy + 13, 14, SOFT.inkSoft, 'left', null, false);
      A.text(c, String(r.value), x + w - (r.next != null ? 74 : 0), yy + 13, 15, r.good === false ? '#c2564a' : SOFT.ink, 'right', null, false);
      if (r.next != null) A.text(c, '→ ' + r.next, x + w, yy + 13, 15, '#3f9a6a', 'right', null, false);
      A.line(c, x, yy + 28, x + w, yy + 28, 'rgba(120,80,40,0.14)', 1);
      yy += 30;
    }
    return yy - y;
  },
  // texto numa linha so: corta na palavra e poe reticencias
  fit(c, text, maxW, size, weight) {
    c.font = `${weight || 700} ${size}px ${FONT_UI}`;
    if (c.measureText(text).width <= maxW) return text;
    const words = text.split(' ');
    while (words.length > 1 && c.measureText(words.join(' ') + '…').width > maxW) words.pop();
    return words.join(' ').replace(/[,.;:]$/, '') + '…';
  },
};
const UKB_GLYPH = { hp: '#ec8a76', lives: '#ec8a76', gold: '#e9b84a', star: '#e9b84a', time: '#8a98d8', armor: '#9aa3ad', mres: '#ad94de', speed: '#62bfb2', flying: '#78b0e6', eye: '#bfa6e8', heal: '#79c37c', fire: '#ef8a5a', soldier: '#c99a72', range: '#62bfb2', dmg: '#ec8a76' };

// traços do inimigo em chips (avisos e bestiario)
function enemyChips(E) {
  const out = [];
  if (E.boss) out.push(['Chefe', 'star', '#e9b84a']);
  if (E.flying) out.push(['Voa', 'flying', '#78b0e6']);
  if (E.stealth) out.push(['Invisível', 'eye', '#ad94de']);
  if (E.frontShield) out.push(['Escudo frontal', 'armor', '#9aa3ad']);
  if (E.armor >= 0.4) out.push(['Blindado', 'armor', '#9aa3ad']);
  if (E.mres >= 0.4) out.push(['Resiste magia', 'mres', '#ad94de']);
  if (E.speed >= 48) out.push(['Rápido', 'speed', '#62bfb2']);
  if (E.heal) out.push(['Cura aliados', 'heal', '#79c37c']);
  if (E.sabotage) out.push(['Sabota torres', 'stun', '#ec8a76']);
  if (E.ranged) out.push(['Ataca de longe', 'range', '#62bfb2']);
  if (E.split) out.push(['Solta filhotes', 'soldier', '#c99a72']);
  if (E.summon) out.push(['Chama reforços', 'soldier', '#c99a72']);
  if (E.burrow || E.wormBurrow) out.push(['Cava na terra', 'speed', '#c99a72']);
  if (E.firestorm) out.push(['Incendeia torres', 'fire', '#ef8a5a']);
  return out;
}

// ------------------------------------------------------------ textos auxiliares
const dec = v => String(v).replace('.', ',');
const AB_FMT = {
  explosive: v => `Explosão de ${v} de dano`,
  eagle: v => `${Math.round(v * 100)}% de chance de crítico`,
  cloud: v => `${v} de dano por segundo`,
  corrosive: v => `-${Math.round(v * 100)}% de armadura no alvo`,
  overload: v => `${Math.round(v * 100)}% de chance de atordoar`,
  storm: v => `${v} raios por nuvem`,
  flash: v => `Atordoa por ${dec(v)}s`,
  burn: v => `${v} de dano por segundo`,
  cluster: v => `${v} mini-bombas`,
  barrel: v => `${v} de dano por segundo`,
  tremor: v => `${Math.round(v * 100)}% de chance de atordoar`,
  chasm: v => `Uma vez a cada ${v}s`,
  charge: v => `Primeiro golpe x${dec(v)}`,
  shield: v => `+${Math.round(v * 100)}% de armadura e vida`,
  heal: v => `Cura ${v} de vida`,
  palm: v => `${v} de dano em área`,
  spring: v => `Cura ${v} de vida por segundo`,
  mire: v => `Lama por ${dec(v)}s`,
  chill: v => `${Math.round(v * 100)}% de chance de congelar`,
  burst: v => `${v} de dano e atordoa`,
  twister: v => `${v} de dano e atordoa`,
  skyward: v => `Voadores no chão por ${dec(v)}s`,
  shred: v => `-${Math.round(v * 100)}% de armadura por 4s`,
  blind: v => `Cega por ${dec(v)}s`,
  warcry: v => `Dura ${dec(v)}s`,
  march: v => `+${Math.round(v * 100)}% de dano corpo a corpo`,
  mark: v => `+${Math.round(v * 100)}% de dano no marcado`,
  bounty: v => `+${Math.round(v * 100)}% de verba por abate`,
  mercs: v => `Um deputado do Centrão a cada ${v}s`,
  caravan: v => `+${v} de verba por onda`,
  compound: v => `Juros de ${Math.round(v * 100)}%`,
  vault: v => `Juros de até ${v} de verba`,
};
const PRIO_DESC = {
  first: 'Mira quem está mais perto da saída.',
  last: 'Mira quem acabou de entrar no alcance.',
  strong: 'Mira o adversário com mais vida.',
  flying: 'Prefere voadores; sem voadores, o primeiro.',
};

function pct(v) { return Math.round(v * 100) + '%'; }
function lvlWord(v) { return v <= 0 ? 'Nenhuma' : v < 0.3 ? 'Baixa' : v < 0.5 ? 'Média' : v < 0.7 ? 'Alta' : 'Muito alta'; }
function speedWord(s) { return s < 25 ? 'Muito lento' : s < 34 ? 'Lento' : s < 50 ? 'Normal' : s < 70 ? 'Rápido' : 'Muito rápido'; }
function shortName(n) { return n.split(',')[0]; }

function towerLines(g, type, tier, spec, abil, spot) {
  const S = g.towerStats({ type, tier, spec, abil: abil || {}, spot });
  const r = a => `${Math.round(a[0])}–${Math.round(a[1])}`;
  const rate = v => v.toFixed(v < 1 ? 2 : 1).replace('.', ',');
  const out = [];
  if (type === 'barracks') {
    out.push(`Soldados: 3 · Vida ${S.hp}`);
    out.push(`Dano ${r(S.dmg)} · Armadura ${pct(S.armor)}`);
    if (S.dodge) out.push(`Esquiva ${pct(S.dodge)}`);
  } else if (spec === 'sun') {
    out.push(`Dano por segundo: ${r(S.dps)}`);
    out.push(`Alcance ${Math.round(S.range)}`);
  } else if (spec === 'seismic') {
    out.push(`Dano ${r(S.dmg)} em todos ao redor`);
    out.push(`Ataque a cada ${rate(S.rate)}s · Lentidão 50%`);
  } else if (type === 'cistern') {
    out.push(`Dano ${r(S.dmg)} · Alcance ${Math.round(S.range)}`);
    out.push(`Molha por ${dec(S.wet)}s · Lentidão ${pct(1 - S.slow)}${S.push ? ' · Empurra' : ''}`);
  } else if (type === 'windmill') {
    out.push(`Dano ${r(S.dmg)} em área · x2 em voadores`);
    out.push(`Empurra ${Math.round(S.push)} · A cada ${rate(S.rate)}s · Alcance ${Math.round(S.range)}`);
  } else if (type === 'banner') {
    out.push(`Aura ${Math.round(S.range)}: +${pct(S.dmgB)} de dano e +${pct(S.rangeB)} de alcance`);
    if (S.rateB) out.push(`+${pct(S.rateB)} de velocidade de ataque`);
    out.push(S.seeBurrow ? 'Revela invisíveis e quem sumiu' : 'Revela quem age escondido');
  } else if (type === 'market') {
    out.push(`+${S.income} de verba a cada onda`);
    if (S.interest) out.push(`Juros: ${pct(S.interest)} da verba guardada (até ${S.cap})`);
  } else {
    out.push(`Dano ${r(S.dmg)}${S.radius ? ' · Área ' + Math.round(S.radius) : ''}`);
    out.push(`Ataque a cada ${rate(S.rate)}s · Alcance ${Math.round(S.range)}`);
    if (S.pierce) out.push(`Atravessa ${S.pierce} adversários`);
    if (S.jumps) out.push(`Salta para mais ${S.jumps} adversários`);
    if (S.poison) out.push(`Veneno ${S.poison}/s por 3s`);
  }
  if (type === 'artillery' && !spec) out.push('Não atinge voadores');
  return out;
}

function rangeColor(type) { return type === 'barracks' ? '#7fffd4' : type === 'banner' ? '#ffd27a' : '#ffffff'; }

// ------------------------------------------------------------ atributos em linhas estruturadas (tooltips v2, js/ui_kit.js)
const secs = v => (v < 1 ? v.toFixed(2) : v.toFixed(1)).replace('.', ',') + ' s';
const range2 = a => `${Math.round(a[0])}–${Math.round(a[1])}`;

// linhas [{g, label, value, next}] de uma torre; com `b` (outra configuracao) mostra o valor seguinte
function towerStatRows(g, a, b) {
  const S = g.towerStats(Object.assign({ abil: {} }, a));
  const N = b ? g.towerStats(Object.assign({ abil: {} }, b)) : null;
  const type = a.type, spec = b ? b.spec || a.spec : a.spec;
  const rows = [];
  const add = (gl, label, f) => {
    const v = f(S);
    const n = N ? f(N) : null;
    if (v == null && n == null) return;
    rows.push({ g: gl, label, value: v == null ? '—' : v, next: n });
  };
  if (type === 'barracks') {
    add('soldier', 'Soldados', () => 3);
    add('hp', 'Vida', s => s.hp);
    add('dmg', 'Dano', s => range2(s.dmg));
    add('armor', 'Armadura', s => pct(s.armor || 0));
    add('speed', 'Esquiva', s => (s.dodge ? pct(s.dodge) : null));
    add('time', 'Volta em', s => secs(s.respawn));
  } else if (spec === 'sun') {
    add('fire', 'Dano por segundo', s => (s.dps ? range2(s.dps) : range2(s.dmg)));
    add('range', 'Alcance', s => Math.round(s.range));
  } else if (spec === 'seismic') {
    add('area', 'Dano ao redor', s => range2(s.dmg));
    add('rate', 'Ataque a cada', s => secs(s.rate));
    add('slow', 'Lentidão', s => (s.slow ? pct(s.slow) : null));
  } else if (type === 'cistern') {
    add('dmg', 'Dano', s => range2(s.dmg));
    add('rate', 'Ataque a cada', s => secs(s.rate));
    add('range', 'Alcance', s => Math.round(s.range));
    add('wet', 'Molha por', s => secs(s.wet));
    add('slow', 'Lentidão', s => pct(1 - s.slow));
    add('push', 'Empurra', s => (s.push ? Math.round(s.push) : null));
  } else if (type === 'windmill') {
    add('area', 'Dano em área', s => range2(s.dmg));
    add('push', 'Empurra', s => Math.round(s.push));
    add('rate', 'Ataque a cada', s => secs(s.rate));
    add('range', 'Alcance', s => Math.round(s.range));
  } else if (type === 'banner') {
    add('range', 'Raio da aura', s => Math.round(s.range));
    add('dmg', 'Dano das vizinhas', s => '+' + pct(s.dmgB));
    add('range', 'Alcance das vizinhas', s => '+' + pct(s.rangeB));
    add('rate', 'Velocidade das vizinhas', s => (s.rateB ? '+' + pct(s.rateB) : null));
  } else if (type === 'market') {
    add('income', 'Verba por onda', s => '+' + s.income);
    add('gold', 'Juros da verba guardada', s => (s.interest ? pct(s.interest) : null));
    add('gold', 'Teto dos juros', s => (s.cap ? s.cap : null));
  } else {
    add('dmg', 'Dano', s => range2(s.dmg));
    add('area', 'Área da explosão', s => (s.radius ? Math.round(s.radius) : null));
    add('rate', 'Ataque a cada', s => secs(s.rate));
    add('range', 'Alcance', s => Math.round(s.range));
    add('pierce', 'Atravessa', s => (s.pierce ? s.pierce + ' adversários' : null));
    add('chain', 'Salta para', s => (s.jumps ? s.jumps + ' adversários' : null));
    add('poison', 'Veneno por segundo', s => (s.poison ? s.poison : null));
  }
  return rows;
}

// o que a torre faz, em chips curtos
const TYPE_CHIPS = {
  archer: [['Atinge voadores', 'flying', 'flying']],
  mage: [['Ignora armadura', 'mres', 'magic']],
  artillery: [['Dano em área', 'area', 'area'], ['Não atinge voadores', 'flying', 'bad']],
  barracks: [['Bloqueia o caminho', 'soldier', 'soldier']],
  cistern: [['Molha', 'wet', 'wet'], ['Retarda', 'slow', 'slow']],
  windmill: [['Empurra', 'push', 'push'], ['x2 em voadores', 'flying', 'flying']],
  banner: [['Não ataca', 'star', 'star'], ['Revela invisíveis', 'eye', 'eye']],
  market: [['Não ataca', 'gold', 'gold'], ['Verba a cada onda', 'income', 'income']],
};
const SPEC_CHIPS = {
  ballista: [['Atravessa adversários', 'pierce', 'pierce']], blowgun: [['Cheiro ignora couraça', 'poison', 'poison']],
  lightning: [['Salta entre adversários', 'chain', 'chain'], ['x1,8 em molhados', 'wet', 'wet']], sun: [['Esquenta mirando', 'fire', 'fire']],
  mortar: [['Longo alcance', 'range', 'range']], seismic: [['Atinge todos ao redor', 'area', 'area']],
  lancers: [['Muita armadura', 'armor', 'armor']], monks: [['Esquivam', 'speed', 'speed']],
  fountain: [['Molha grupos', 'wet', 'wet']], geyser: [['Empurra', 'push', 'push']],
  tornado: [['Arrasta grupos', 'push', 'push']], sandblast: [['Ataque rápido', 'rate', 'rate']],
  drums: [['Acelera vizinhas', 'rate', 'rate']], watch: [['Revela quem cava', 'eye', 'eye']],
  bazaar: [['Mercenários', 'soldier', 'soldier']], treasury: [['Juros', 'gold', 'gold']],
};
function chipsFor(type, spec) {
  const list = spec ? [...(SPEC_CHIPS[spec] || []), ...(TYPE_CHIPS[type] || []).filter(c => c[2] !== 'bad' || spec === null)] : TYPE_CHIPS[type] || [];
  return list.slice(0, 3).map(([text, icon, col]) => ({ text, icon, color: col === 'bad' ? UIK.bad : UIK.G[col] || UIK.inkSoft }));
}
const firstSentence = s => (s || '').split(/(?<=\.)\s/)[0];

// valor de cada nivel de habilidade: glifo, rotulo e numero
const AB_STAT = {
  explosive: ['area', 'Dano da explosão', v => v], eagle: ['crit', 'Chance de crítico', v => pct(v)], cloud: ['poison', 'Dano por segundo', v => v],
  corrosive: ['armor', 'Armadura do alvo', v => '-' + pct(v)], overload: ['stun', 'Chance de atordoar', v => pct(v)], storm: ['chain', 'Raios por nuvem', v => v],
  flash: ['stun', 'Atordoa por', v => secs(v)], burn: ['fire', 'Dano por segundo', v => v], cluster: ['area', 'Mini-bombas', v => v],
  barrel: ['fire', 'Dano por segundo', v => v], tremor: ['stun', 'Chance de atordoar', v => pct(v)], chasm: ['time', 'Recarga', v => secs(v)],
  charge: ['dmg', 'Primeiro golpe', v => 'x' + dec(v)], shield: ['armor', 'Armadura e vida', v => '+' + pct(v)], heal: ['heal', 'Cura', v => v],
  palm: ['area', 'Dano em área', v => v], spring: ['heal', 'Cura por segundo', v => v], mire: ['slow', 'Lama dura', v => secs(v)],
  chill: ['freeze', 'Chance de congelar', v => pct(v)], burst: ['area', 'Dano (e atordoa)', v => v], twister: ['push', 'Dano (e atordoa)', v => v],
  skyward: ['flying', 'Voadores no chão', v => secs(v)], shred: ['armor', 'Armadura por 4 s', v => '-' + pct(v)], blind: ['eye', 'Cega por', v => secs(v)],
  warcry: ['time', 'Duração', v => secs(v)], march: ['dmg', 'Dano corpo a corpo', v => '+' + pct(v)], mark: ['crit', 'Dano no marcado', v => '+' + pct(v)],
  bounty: ['gold', 'Verba por abate', v => '+' + pct(v)], mercs: ['soldier', 'Um deputado a cada', v => secs(v)], caravan: ['income', 'Verba por onda', v => '+' + v],
  compound: ['income', 'Juros', v => pct(v)], vault: ['gold', 'Teto de juros', v => v],
};

// ------------------------------------------------------------ tela: fase
const Level = {
  ringPos(cx, cy, r, angDeg) {
    const a = (angDeg * Math.PI) / 180;
    return [cx + Math.cos(a) * r, cy + Math.sin(a) * r];
  },
  ringAngles(n) {
    if (n === 4) return [-135, -45, 45, 135];
    if (n === 2) return [-135, -45];
    if (n === 1) return [-90];
    return Array.from({ length: n }, (_, i) => -90 + (i * 360) / n);
  },

  menuCenter(x, y) {
    return [U.clamp(x, 112, W - 112), U.clamp(y - 22, 108, H - 126)];
  },

  // raio do anel: 'tower' (menu da torre), 'ruin' e 'build' (com n tipos)
  ringR(kind, n) { return kind === 'build' ? (n >= 5 ? 82 : 76) : 78; },
  // posicao de cada botao do menu da torre (o e2e usa a mesma): evoluir, vender, lado (alvo/encontro) e as duas opcoes
  slotPos(kind, cx, cy) {
    const R = this.ringR('tower');
    const ang = { up: -90, sell: 90, side: 28, opt0: -145, opt1: -35 }[kind];
    const [x, y] = this.ringPos(cx, cy, R, ang);
    return kind === 'sell' ? [x, y - 8] : [x, y];
  },

  priceTag(c, x, y, v, ok) {
    A.pricePill(c, x, y, v, ok, { align: 'center', size: 13, h: 22 });
  },

  // fundo do anel de botoes: disco claro que abre com um pulo (lv.selT = tempo desde a selecao)
  ringBack(c, cx, cy, R) {
    this._ringC = [cx, cy];
    const k = U.clamp((App.lv.selT || 0) / 0.24, 0, 1), e = U.easeOutBack(k);
    c.save();
    c.globalAlpha = Math.min(1, k * 1.6);
    const im = A.skin('medalhao');
    if (im) {
      // aro de madeira com cipo pintado passando pelos botoes (fonte: centro 155,143; meio da faixa a 113 px)
      const kk = Math.max(0.01, R * e) / 113;
      c.imageSmoothingEnabled = true;
      c.imageSmoothingQuality = 'high';
      A.ell(c, cx, cy + 6, R * e + 18, (R * e + 18) * 0.9, 'rgba(60,35,15,0.16)');
      c.drawImage(im, cx - 155.5 * kk, cy - 143.5 * kk, im.naturalWidth * kk, im.naturalHeight * kk);
    } else {
      A.circ(c, cx, cy, Math.max(1, R * e + 4), 'rgba(255,248,236,0.2)');
      A.circ(c, cx, cy, Math.max(1, R * e), null, 'rgba(255,255,255,0.85)', 2.5);
    }
    c.restore();
  },

  // botao do anel: medalhao creme com aro colorido e icone 3D; sai do centro do anel ao abrir
  ringBtn(c, key, x, y, icon, cb, o = {}) {
    const skin = !!A.skin('botao_creme');
    const BR = skin ? 30 : 27; // o botao pintado tem aro de madeira mais largo
    const hov = UI.circle(key, x, y, BR + 2, cb);
    const C = this._ringC, k = U.clamp((App.lv.selT || 0) / 0.24, 0, 1), e = U.easeOutBack(k);
    c.save();
    if (C && k < 1) {
      c.translate(C[0] + (x - C[0]) * e, C[1] + (y - C[1]) * e);
      const sc = 0.45 + 0.55 * e;
      c.scale(sc, sc);
      c.globalAlpha = Math.min(1, k * 2);
    } else c.translate(x, y);
    const ring = o.disabled ? '#c9b8a4' : o.color || '#e2a95c';
    const s = hov ? 1.08 : 1;
    c.save();
    c.scale(s, s);
    A.ell(c, 0, BR - 2, BR * 0.85, 6, 'rgba(90,50,20,0.22)');
    if (hov && !o.disabled) A.glow(c, 0, 0, BR + 16, ring, 0.45);
    if (skin) {
      // miolo creme (cinza quando nao da) com aro de madeira e cipo; a cor do tipo fica no brilho do hover
      A.knob(c, 0, 0, 19.5, o.disabled ? 'botao_cinza' : 'botao_creme');
      A.icon(c, icon, 0, -1, 18.5, { tier: o.tier, time: App.time, disabled: o.disabled });
    } else {
      const gg = c.createRadialGradient(-6, -8, 2, 0, 0, BR);
      gg.addColorStop(0, '#fffdf8');
      gg.addColorStop(1, o.disabled ? '#eadfd2' : '#f6e6c8');
      A.circ(c, 0, 0, BR, gg, ring, 3.2);
      A.icon(c, icon, 0, -1, 19, { tier: o.tier, time: App.time, disabled: o.disabled });
    }
    c.restore();
    if (o.pips != null) {
      for (let i = 0; i < 3; i++) A.circ(c, -11 + i * 11, -BR + 1, 4.2, i < o.pips ? '#f6c044' : '#fff6e6', i < o.pips ? '#c98a1e' : 'rgba(150,110,80,0.55)', 1.4);
    }
    if (o.price != null) this.priceTag(c, 0, BR + 14, o.price, !o.disabled);
    if (o.label) A.chip(c, -A.measure(c, o.label, 12, 800) / 2 - 9, BR + 14, o.label, { color: ring, size: 12, h: 22 });
    c.restore();
    return hov;
  },

  draw(c, dt) {
    const g = App.game, lv = App.lv;
    const busy = lv.overlay || lv.paused;
    if (lv.sel !== lv._selPrev) { lv._selPrev = lv.sel; lv.selT = 0; }
    lv.selT = (lv.selT || 0) + dt;
    if (!lv.paused) lv.pauseT = 0;
    this._dt = dt;
    if (!busy) UI.rect('world', 0, 0, W, H, (x, y, b) => this.worldClick(x, y, b), lv.mode ? 'crosshair' : 'default');

    // vista
    const view = { sel: lv.sel, hoverSpot: null, range: null, heroSel: lv.mode === 'hero', selEnemy: lv.sel && lv.sel.enemy, hoverLever: -1 };
    const sel = lv.sel;
    if (sel && sel.tower && !lv.mode && sel.tower.type !== 'market') {
      const t = sel.tower;
      view.range = { x: t.x, y: t.y, r: (t.E || t.S).range, color: rangeColor(t.type) };
    }
    if (sel && sel.tower && sel.tower.spec === 'bazaar' && !lv.mode) view.range = { x: sel.tower.x, y: sel.tower.y, r: sel.tower.S.range, color: '#7fffd4' };
    if (lv.mode === 'rally' && sel && sel.tower) {
      const t = sel.tower;
      view.range = { x: t.x, y: t.y, r: t.S.range, color: '#7fffd4' };
      view.rallyPreview = { x: UI.mx, y: UI.my, ok: g.canRally(t, UI.mx, UI.my) };
    }
    if (lv.mode === 'spell') {
      const r = lv.spell === 'fury' ? DATA.SPELLS.fury.radius + 20 : 45;
      view.range = { x: UI.mx, y: UI.my, r, color: lv.spell === 'fury' ? '#9fd8ff' : lv.spell === 'stampede' ? '#b6ec4a' : '#ffd27a' };
    }
    if (lv.preview) view.range = lv.preview;
    lv.preview = null;

    // regioes clicaveis do mundo
    if (!busy && !lv.mode) {
      for (const s of g.spots) {
        if (s.tower) {
          const t = s.tower;
          if (UI.rect('tw' + t.id, t.x - 38, t.y - 92, 76, 108, () => this.selectTower(t))) view.hoverTower = t;
        } else if (UI.rect('sp' + s.i, s.x - 40, s.y - 26, 80, 50, () => this.selectSpot(s))) view.hoverSpot = s;
      }
      for (const e of g.enemies) {
        if (!g.targetable(e) || (e.T.stealth && !e.revealed)) continue;
        const hy = e.flying ? FLY_H : e.T.size;
        UI.rect('en' + e.id, e.x - e.T.size - 4, e.y - hy - e.T.size - 6, e.T.size * 2 + 8, e.T.size + hy + 10, () => { lv.sel = { enemy: e }; Snd.play('click'); });
      }
      const h = g.hero;
      if (!h.dead && !h.disabled) UI.rect('hero', h.x - 14, h.y - 40, 28, 44, () => this.toggleHero());
      g.forks.forEach((f, i) => {
        if (UI.circle('lever' + i, f.x, f.y - 18, 24, () => this.toggleFork(i))) {
          view.hoverLever = i;
          const open = this.branchName(g, f, f.state), other = this.branchName(g, f, 1 - f.state);
          UI.setTip(f.x, f.y, 'Manobra regimental', null, { card: true, icon: 'prio_first', tag: 'Manobra', desc: `A turma adversária segue pelo caminho ${open}.`, footer: `Clique (ou G) para desviar pelo ${other}` });
        }
      });
    }

    Render.ensureBg(g, App.scale);
    Render.level(c, g, view);

    this.notices(c, dt);
    if (!busy) {
      if (sel && sel.spot && !sel.spot.tower) this.buildMenu(c, sel.spot);
      else if (sel && sel.tower && !lv.mode) this.towerMenu(c, sel.tower);
      this.waveButtons(c);
    }
    this.hud(c);
    if (sel && (sel.enemy || sel.tower) && !busy) this.infoBar(c);
    this.banner(c, dt);
    if (lv.tutorial && !busy) this.tutorial(c, dt);
    if (lv.mode && !busy) this.modeHint(c);
    if (UI.tip) drawTip(c, UI.tip);
    if (lv.paused && !lv.overlay) this.pauseMenu(c);
    if (lv.overlay) this.endPanel(c, dt);
  },

  branchName(g, f, state) {
    const p = g.paths[f.paths[state]], q = g.paths[f.paths[1 - state]];
    let ya = 0, yb = 0;
    for (let k = 1; k <= 8; k++) { ya += p.at(f.d + k * 40, {}).y; yb += q.at(f.d + k * 40, {}).y; }
    return ya < yb ? 'de cima' : 'de baixo';
  },

  toggleFork(i) {
    const g = App.game;
    if (g.toggleFork(i)) Snd.play('click'); else Snd.play('error');
  },

  banner(c, dt) {
    const g = App.game, lv = App.lv;
    if (g.wave !== lv.lastWave) {
      lv.lastWave = g.wave;
      if (g.wave > 0) lv.banner = { t: 0, text: g.wave === g.totalWaves ? 'Última onda!' : `Onda ${g.wave}`, sub: g.wave === g.totalWaves ? 'Segure firme!' : `de ${wavesTxt(g)}` };
    }
    const b = lv.banner;
    if (!b) return;
    if (!lv.paused) b.t += dt;
    const T = 2.3;
    if (b.t > T) { lv.banner = null; return; }
    const kin = U.clamp(b.t / 0.45, 0, 1), kout = U.clamp((b.t - (T - 0.45)) / 0.45, 0, 1);
    const a = Math.min(kin * 1.8, 1) * (1 - kout);
    const y = 150 + 70 * U.easeOutBack(kin) - 26 * kout * kout;
    const accent = b.boss ? '#ec7f6e' : b.storm ? '#e0a45e' : '#e89a72';
    c.save();
    c.globalAlpha = a;
    c.font = `700 40px ${FONT_TITLE}`;
    const w = Math.max(230, c.measureText(b.text).width + 90), h = 74;
    const x = W / 2 - w / 2;
    // pontas da fita
    for (const sd of [-1, 1]) {
      const ex = sd < 0 ? x + 10 : x + w - 10;
      A.poly(c, [[ex, y + 16], [ex + sd * 42, y + 18], [ex + sd * 30, y + 37], [ex + sd * 42, y + 56], [ex, y + 58]], U.shade(accent, -0.08), U.shade(accent, -0.2), 1.5);
    }
    A.softShadow(c, x, y, w, h, 22, 22, 0.28, 8, SOFT.card1);
    const gr = c.createLinearGradient(0, y, 0, y + h);
    gr.addColorStop(0, SOFT.card1); gr.addColorStop(1, SOFT.card2);
    A.rrect(c, x, y, w, h, 22, gr, U.rgba(accent, 0.7), 2.5);
    A.text(c, b.text, W / 2, y + 30, 38, U.shade(accent, -0.25), 'center', { family: FONT_TITLE, weight: 700 }, 'rgba(255,255,255,0.9)', 5);
    if (b.sub) A.text(c, b.sub, W / 2, y + 58, 14, SOFT.inkSoft, 'center', null, false);
    c.restore();
  },

  bubble(c, x, y, text, dir) {
    const lines = A.wrap(c, text, 262, 15);
    const w = 292, h = 22 + lines.length * 21;
    let bx = x - w / 2, by = dir === 'down' ? y - h - 26 : y + 26;
    bx = U.clamp(bx, 10, W - w - 10);
    by = U.clamp(by, 70, H - h - 10);
    const bob = Math.sin(App.time * 3.2) * 3;
    A.softShadow(c, bx, by + bob, w, h, 18, 16, 0.26, 6, SOFT.card1);
    A.rrect(c, bx, by + bob, w, h, 18, SOFT.card1, SOFT.line, 2);
    const ay = dir === 'down' ? by + bob + h - 1 : by + bob + 1;
    const px = U.clamp(x, bx + 24, bx + w - 24);
    A.poly(c, dir === 'down' ? [[px - 11, ay], [px + 11, ay], [px, ay + 13]] : [[px - 11, ay], [px + 11, ay], [px, ay - 13]], SOFT.card1, null);
    A.line(c, px - 11, ay + (dir === 'down' ? 0.5 : -0.5), px, ay + (dir === 'down' ? 13 : -13), SOFT.line, 2);
    A.line(c, px + 11, ay + (dir === 'down' ? 0.5 : -0.5), px, ay + (dir === 'down' ? 13 : -13), SOFT.line, 2);
    lines.forEach((l, i) => A.text(c, l, bx + w / 2, by + bob + 22 + i * 21, 15, SOFT.ink, 'center', { family: FONT_UI, weight: 700 }, false));
  },

  tutorial(c, dt) {
    const g = App.game, lv = App.lv, T = lv.tut;
    if (g.state === 'prewave' && !g.towers.length) {
      const s = g.spots[3];
      if (!(lv.sel && lv.sel.spot === s)) this.bubble(c, s.x, s.y - 14, 'Clique neste terreno para construir sua primeira torre.', 'down');
      else this.bubble(c, s.x, s.y + 60, 'Escolha uma torre. Passe o mouse para ver o que cada uma faz.', 'up');
      return;
    }
    if (g.state === 'prewave') return;
    T.t += dt;
    if (!T.hero && g.wave >= 1) {
      if (T.t > 3 && T.t < 16 && !lv.mode) this.bubble(c, 52, 626, `Este é ${App.game.H.name}. Clique no herói e depois no mapa para levá-lo até a briga.`, 'down');
      if (lv.mode === 'hero' || T.t >= 16) { T.hero = true; T.t = 0; }
      return;
    }
    if (!T.spell && g.wave >= 2) {
      if (T.t < 10) this.bubble(c, 168, 636, 'Operações: clique e escolha o alvo. A PF contra grupos, a Bancada de Apoio para segurar a fila.', 'down');
      else { T.spell = true; T.t = 0; }
      return;
    }
    if (!T.up && g.wave >= 3) {
      const t = g.towers.find(tw => tw.tier < 3 && !tw.working && g.upgradeCost(tw) <= g.gold);
      if (t && T.t < 10) this.bubble(c, t.x, t.y - 66, 'Você tem verba para evoluir esta torre. Clique nela!', 'down');
      else if (T.t >= 10 || (lv.sel && lv.sel.tower)) { T.up = true; T.t = 0; }
      return;
    }
    if (!T.prio && g.wave >= 4) {
      const t = g.towers.find(tw => g.prioOptions(tw).length);
      if (t && T.t < 9) this.bubble(c, t.x, t.y - 66, 'Dica: no menu da torre, o botão da direita escolhe o alvo (primeiro, último, mais forte ou voadores).', 'down');
      else { T.prio = true; T.t = 0; }
    }
  },

  modeHint(c) {
    const lv = App.lv;
    const txt = lv.mode === 'hero' ? `Clique no mapa para mover ${App.game.H.name}` : lv.mode === 'rally' ? 'Clique no caminho para posicionar a tropa' : lv.spell === 'fury' ? 'Clique onde a PF deve chegar' : lv.spell === 'stampede' ? 'Clique na estrada: os delatores correm contra a própria turma' : 'Clique no caminho para chamar a Bancada de Apoio';
    A.darkPanel(c, W / 2 - 220, 76, 440, 34, 17);
    A.text(c, txt + '   (botão direito cancela)', W / 2, 93, 14, '#ffe9b0', 'center');
  },

  selectSpot(s) {
    const lv = App.lv;
    if (lv.sel && lv.sel.spot === s) { lv.sel = null; return; }
    lv.sel = { spot: s };
    Snd.play('open');
  },
  selectTower(t) {
    const lv = App.lv;
    if (lv.sel && lv.sel.tower === t) { lv.sel = null; return; }
    lv.sel = { tower: t, spot: t.spot };
    Snd.play('open');
  },
  toggleHero() {
    const lv = App.lv, g = App.game;
    if (g.hero.dead || g.hero.disabled) { Snd.play('error'); return; }
    if (lv.mode === 'hero') { lv.mode = null; return; }
    lv.mode = 'hero'; lv.sel = null;
    Snd.play('click');
  },
  castMode(id) {
    const lv = App.lv, g = App.game;
    if (!g.canCast(id)) { Snd.play('error'); return; }
    if (lv.mode === 'spell' && lv.spell === id) { lv.mode = null; return; }
    lv.mode = 'spell'; lv.spell = id; lv.sel = null;
    Snd.play('click');
  },
  cyclePrio() {
    const lv = App.lv, g = App.game;
    const t = lv.sel && lv.sel.tower;
    if (!t || !g.cyclePrio(t)) { Snd.play('error'); return; }
    g.text(t.x, t.y - 80, PRIO_NAMES[t.prio], '#bfe8ff', 16);
  },
  cancel() {
    const lv = App.lv;
    if (lv.mode) lv.mode = null;
    else lv.sel = null;
  },

  worldClick(x, y, btn) {
    const lv = App.lv, g = App.game;
    if (btn === 2) { this.cancel(); return; }
    if (lv.mode === 'spell') {
      if (lv.spell === 'riders' || lv.spell === 'stampede') {
        let ok = false;
        for (const p of g.paths) if (p.nearest(x, y).dist < 50) ok = true;
        if (!ok) { Snd.play('error'); return; }
      }
      if (g.castSpell(lv.spell, x, y)) lv.mode = null;
      return;
    }
    if (lv.mode === 'hero') {
      g.moveHero(x, y);
      g.addFx({ kind: 'flag', x, y, T: 0.7 });
      lv.mode = null;
      return;
    }
    if (lv.mode === 'rally') {
      const t = lv.sel && lv.sel.tower;
      if (t && g.setRally(t, x, y)) { lv.mode = null; lv.sel = null; }
      else Snd.play('error');
      return;
    }
    lv.sel = null;
  },

  buildMenu(c, s) {
    const g = App.game, lv = App.lv;
    const [cx, cy] = this.menuCenter(s.x, s.y);
    if (s.ruin) return this.ruinMenu(c, s, cx, cy);
    const types = g.loadout;
    const R = this.ringR('build', types.length);
    this.ringBack(c, cx, cy, R);
    const angs = this.ringAngles(types.length);
    const full = g.towerLimitReached();
    types.forEach((type, i) => {
      const D = DATA.TOWERS[type];
      const cost = D.tiers[0].cost;
      const [bx, by] = this.ringPos(cx, cy, R, angs[i]);
      const ok = g.gold >= cost && !full;
      const hov = this.ringBtn(c, 'b' + type, bx, by, type, () => {
        if (!ok) { Snd.play('error'); return; }
        const t = g.build(s, type);
        if (t) lv.sel = null;
      }, { price: cost, disabled: !ok, tier: 1, color: '#5fb8a8' });
      if (hov) {
        const S = g.towerStats({ type, tier: 1, abil: {}, spot: s });
        if (S.range) lv.preview = { x: s.x, y: s.y, r: S.range, color: rangeColor(type) };
        const chips = chipsFor(type, null);
        if (s.high) chips.unshift({ text: 'Terreno elevado: +15% de alcance', icon: 'range', color: UIK.good });
        UI.setTip(cx, cy, D.name, null, {
          card: true, icon: type, tier: 1, tag: 'Construir · nível 1', desc: firstSentence(D.desc),
          rows: towerStatRows(g, { type, tier: 1, spot: s }), chips, cost, ok: g.gold >= cost, gold: g.gold,
          action: 'Clique para construir', note: full ? `Limite do desafio: ${g.rules.maxTowers} torres` : null, noteColor: UIK.bad,
        });
      }
    });
  },

  ruinMenu(c, s, cx, cy) {
    const g = App.game, lv = App.lv;
    const R = this.ringR('ruin');
    this.ringBack(c, cx, cy, R);
    const [bx, by] = this.ringPos(cx, cy, R, -90);
    const ok = g.gold >= s.ruin;
    if (this.ringBtn(c, 'ruin', bx, by, 'ruin', () => {
      if (!g.clearRuin(s)) { Snd.play('error'); return; }
      lv.sel = { spot: s };
    }, { price: s.ruin, disabled: !ok, color: '#c9a06a' })) {
      UI.setTip(cx, cy, 'Terminar a obra', null, {
        card: true, icon: 'ruin', tag: 'Obra parada', desc: 'Termina a obra e libera um terreno novo para construir.',
        chips: s.high ? [{ text: 'Terreno elevado', icon: 'range', color: UIK.good }] : [], cost: s.ruin, ok, gold: g.gold, action: 'Clique para limpar',
      });
    }
  },

  towerMenu(c, t) {
    const g = App.game, lv = App.lv;
    const [cx, cy] = this.menuCenter(t.x, t.y - 4);
    const R = this.ringR('tower');
    this.ringBack(c, cx, cy, R);
    const D = DATA.TOWERS[t.type];
    const cur = { type: t.type, tier: t.tier, spec: t.spec, abil: t.abil, spot: t.spot };
    if (t.working) {
      const [bx, by] = this.slotPos('up', cx, cy);
      const left = Math.max(0, t.buildDur - t.buildT);
      if (this.ringBtn(c, 'work', bx, by, 'work', () => Snd.play('error'), { disabled: true, label: secs(left) })) {
        UI.setTip(cx, cy, t.prev ? 'Evoluindo' : 'Em construção', null, {
          card: true, icon: 'work', tag: 'Obra', desc: 'A torre fica parada até a obra terminar.',
          rows: [{ g: 'time', label: 'Falta', value: secs(left) }], footer: 'Melhorias e habilidades liberam depois',
        });
      }
    } else if (!t.spec && t.tier < 3) {
      const cost = g.upgradeCost(t), ok = g.gold >= cost;
      const [bx, by] = this.slotPos('up', cx, cy);
      if (this.ringBtn(c, 'up', bx, by, 'upgrade', () => { if (!g.upgrade(t)) Snd.play('error'); }, { price: cost, disabled: !ok, color: '#6cc25a' })) {
        const nxt = { type: t.type, tier: t.tier + 1, abil: {}, spot: t.spot };
        const nx = g.towerStats(nxt);
        if (nx.range) lv.preview = { x: t.x, y: t.y, r: nx.range, color: '#aaffaa' };
        UI.setTip(cx, cy, D.name, null, {
          card: true, icon: t.type, tier: t.tier + 1, tag: `Evoluir · nível ${t.tier} → ${t.tier + 1}`,
          rows: towerStatRows(g, cur, nxt), cost, ok, gold: g.gold, action: 'Clique para evoluir',
        });
      }
    } else if (!t.spec && t.tier === 3) {
      D.specs.forEach((sp, i) => {
        const S = DATA.SPECS[sp];
        const ok = g.gold >= S.cost;
        const [bx, by] = this.slotPos(i ? 'opt1' : 'opt0', cx, cy);
        if (this.ringBtn(c, 'sp' + sp, bx, by, sp, () => { if (!g.specialize(t, sp)) Snd.play('error'); }, { price: S.cost, disabled: !ok, color: '#e0a64a' })) {
          const nxt = { type: t.type, tier: 4, spec: sp, abil: {}, spot: t.spot };
          const st = g.towerStats(nxt);
          if (st.range) lv.preview = { x: t.x, y: t.y, r: st.range, color: '#ffe08a' };
          UI.setTip(cx, cy, S.name, null, {
            card: true, icon: sp, tag: 'Especialização', desc: firstSentence(S.desc), rows: towerStatRows(g, cur, nxt), chips: chipsFor(t.type, sp),
            bullets: S.abilities.map(a => ({ icon: a.id, title: a.name, text: a.desc })), cost: S.cost, ok, gold: g.gold, action: 'Clique para especializar', w: 360,
          });
        }
      });
    } else if (t.spec) {
      const S = DATA.SPECS[t.spec];
      S.abilities.forEach((ab, i) => {
        const cost = g.abilityCost(t, ab);
        const lvl = g.abLvl(t, ab.id);
        const ok = cost != null && g.gold >= cost;
        const [bx, by] = this.slotPos(i ? 'opt1' : 'opt0', cx, cy);
        const hov = this.ringBtn(c, 'ab' + ab.id, bx, by, ab.id, () => { if (!g.buyAbility(t, ab.id)) Snd.play('error'); }, { price: cost == null ? null : cost, disabled: cost == null ? false : !ok, pips: lvl, color: cost == null ? '#f0b83a' : '#e0a64a', label: cost == null ? 'Máximo' : null });
        if (hov) {
          const [gl, label, fmt] = AB_STAT[ab.id] || ['star', 'Efeito', v => v];
          UI.setTip(cx, cy, ab.name, null, {
            card: true, icon: ab.id, tag: 'Habilidade', pips: lvl, desc: ab.desc,
            rows: [{ g: gl, label, value: lvl > 0 ? fmt(ab.vals[lvl - 1]) : '—', next: lvl < 3 ? fmt(ab.vals[lvl]) : null }],
            cost: cost == null ? null : cost, ok, gold: g.gold, max: cost == null, action: lvl ? `Clique para o nível ${lvl + 1}` : 'Clique para aprender',
          });
        }
      });
    }
    // vender
    const sv = g.sellValue(t);
    const [sx, sy] = this.slotPos('sell', cx, cy);
    if (this.ringBtn(c, 'sell', sx, sy, 'sell', () => { g.sell(t); lv.sel = null; }, { price: sv, color: '#e88e74' })) {
      const full = g.wave === 0 || (t.working && !t.prev);
      UI.setTip(cx, cy, 'Vender torre', null, {
        card: true, icon: 'sell', tag: 'Vender', rows: [{ g: 'gold', label: 'Você recebe', value: sv }],
        note: g.wave === 0 ? 'Antes da 1ª onda: reembolso total' : t.working && !t.prev ? 'Obra cancelada: reembolso total' : 'Devolve 60% do que foi investido',
        noteIcon: 'gold', noteColor: full ? UIK.good : UIK.inkSoft, footer: 'Clique para vender',
      });
    }
    if (t.type === 'barracks' || t.spec === 'bazaar') {
      const [rx, ry] = this.slotPos('side', cx, cy);
      if (this.ringBtn(c, 'rally', rx, ry, 'rally', () => { lv.mode = 'rally'; Snd.play('click'); }, { color: '#5fb8a8' })) {
        UI.setTip(cx, cy, 'Ponto de encontro', null, {
          card: true, icon: 'rally', tag: t.type === 'barracks' ? 'Soldados' : 'Mercenários',
          desc: t.type === 'barracks' ? DATA.fmt('Onde os {tropa} seguram a turma adversária.') : 'Onde os deputados de aluguel vão lutar.', footer: 'Clique e escolha o lugar no mapa',
        });
      }
    } else if (g.prioOptions(t).length) {
      const [px, py] = this.slotPos('side', cx, cy);
      if (this.ringBtn(c, 'prio', px, py, 'prio_' + t.prio, () => this.cyclePrio(), { color: '#8a98d8' })) {
        const opts = g.prioOptions(t);
        UI.setTip(cx, cy, PRIO_NAMES[t.prio], null, {
          card: true, icon: 'prio_' + t.prio, tag: 'Alvo da torre', desc: PRIO_DESC[t.prio],
          chips: opts.map(p => ({ text: PRIO_NAMES[p], color: p === t.prio ? '#5a6ad0' : UIK.inkSoft, bg: p === t.prio ? 'rgba(138,152,216,0.25)' : null })),
          footer: 'Clique (ou T) para trocar',
        });
      }
    }
  },

  entrance(p) {
    const tmp = {};
    for (let d = 0; d < p.len; d += 4) {
      const q = p.at(d, tmp);
      if (q.x > 40 && q.x < W - 40 && q.y > 40 && q.y < H - 40) return [q.x, q.y];
    }
    return [W / 2, H / 2];
  },

  // entradas da proxima onda (caminhos que comecam no mesmo lugar viram um botao so)
  waveGroups(g) {
    const groups = [];
    for (const pi of g.waveEntrances(g.wave)) {
      let [x, y] = this.entrance(g.paths[pi]);
      if (x < 390 && y < 100) y = 104;
      // nao cobrir a fenda da Fumaca Negra (fase 12): o botao vai para o lado
      const CF = typeof SPRITE_META !== 'undefined' && SPRITE_META.cenario && SPRITE_META.cenario[g.levelIdx];
      if (CF && CF.fenda && Math.hypot(x - CF.fenda[0], y - CF.fenda[1]) < 70) x += 72;
      const gr = groups.find(q => Math.hypot(q.x - x, q.y - y) < 40);
      if (gr) gr.paths.push(pi); else groups.push({ x, y, paths: [pi] });
    }
    for (const gr of groups) for (const f of g.forks) if (gr.paths.some(p => f.paths.includes(p))) for (const p of f.paths) if (!gr.paths.includes(p)) gr.paths.push(p);
    return groups;
  },

  waveButtons(c) {
    const g = App.game;
    if (!g.canCallWave()) return;
    const pulse = 1 + Math.sin(App.time * 5) * 0.06;
    this.waveGroups(g).forEach((G, gi) => {
      const { x, y } = G;
      const hov = UI.circle('wave' + gi, x, y, 26, () => {
        const b = g.callWave();
        if (b) g.text(x, y - 34, '+' + b, '#ffd54a', 20);
        App.lv.sel = null;
      });
      c.save();
      c.translate(x, y);
      c.scale(pulse, pulse);
      A.glow(c, 0, 0, 44, '#ff5a3a', 0.35);
      A.roundBtn(c, 0, 0, 24, { hover: hov, color: '#ee7d6e' });
      A.skullIcon(c, 0, -1, 13);
      if (g.countdown > 0) {
        const k = g.countdown / g.countdownMax;
        c.beginPath();
        c.arc(0, 0, 28, -Math.PI / 2, -Math.PI / 2 + U.TAU * (1 - k));
        c.strokeStyle = '#ffd54a'; c.lineWidth = 4; c.stroke();
      }
      c.restore();
      const sum = g.waveSummary(g.wave, G.paths);
      this.waveStrip(c, x, y, sum, g);
      if (g.state === 'prewave') {
        // chip do lado oposto a previa de inimigos, com ponteira para o botao
        const by = Math.sin(App.time * 4) * 3;
        const label = 'Chamar a 1ª onda';
        c.font = `800 13px ${FONT_UI}`;
        const cw = c.measureText(label).width + 22;
        const below = y < 140 || y <= H - 120;
        const cy = (y < 140 ? y + 86 : below ? y + 46 : y - 86) + by;
        const cx = U.clamp(x - cw / 2, 10, W - cw - 10);
        A.softShadow(c, cx, cy - 13, cw, 26, 13, 10, 0.22, 3, '#fff6e6');
        A.poly(c, below ? [[x - 6, cy - 12], [x + 6, cy - 12], [x, cy - 19]] : [[x - 6, cy + 12], [x + 6, cy + 12], [x, cy + 19]], '#fff6e6', null);
        UKB.chip(c, cx, cy, label, { color: '#ec8a76' });
      }
      if (hov) {
        const lines = [];
        if (g.countdown > 0) lines.push(`Chamar agora: +${Math.round(g.countdown * 2)} de verba`);
        else lines.push('Chamar cedo dá verba e adianta as operações.');
        UI.setTip(x, y, `Onda ${g.wave + 1} de ${wavesTxt(g)}`, lines, { enemies: sum, seen: g.seen });
      }
    });
  },

  // icones dos inimigos que vem pela entrada
  waveStrip(c, x, y, sum, g) {
    const list = sum.slice(0, 4);
    if (!list.length) return;
    const n = list.length, sp = 36;
    const sy = y < 140 ? y + 48 : y - 48;
    const sx = U.clamp(x, 34 + (n - 1) * sp / 2, W - 34 - (n - 1) * sp / 2) - ((n - 1) * sp) / 2;
    A.softShadow(c, sx - 21, sy - 18, (n - 1) * sp + 42, 36, 18, 10, 0.22, 3, SOFT.card1);
    A.rrect(c, sx - 21, sy - 18, (n - 1) * sp + 42, 36, 18, null, SOFT.line, 1.5);
    list.forEach(([type, k], i) => {
      const ix = sx + i * sp;
      const isNew = !g.seen.has(type);
      A.circ(c, ix, sy, 14, isNew ? '#ffe9de' : SOFT.card2, isNew ? '#ec8a76' : SOFT.line, 1.6);
      A.icon(c, type, ix, sy, 12.5, { time: App.time });
      A.circ(c, ix + 11, sy + 10, 8.5, SOFT.ink, '#ffffff', 1.5);
      A.text(c, String(k), ix + 11, sy + 10.5, 11, '#ffffff', 'center', null, false);
    });
  },

  hud(c) {
    const g = App.game, lv = App.lv;
    // ouro "rola" ate o valor novo e a moeda pulsa; o coracao treme ao perder vida
    const dt = this._dt || 0;
    if (lv.hudGold == null || Math.abs(lv.hudGold - g.gold) > 5000) lv.hudGold = g.gold;
    if (g.gold > (lv.hudGoldPrev == null ? g.gold : lv.hudGoldPrev) + 0.5) lv.goldPulse = 1;
    lv.hudGoldPrev = g.gold;
    lv.hudGold += (g.gold - lv.hudGold) * Math.min(1, dt * 9);
    if (Math.abs(g.gold - lv.hudGold) < 0.5) lv.hudGold = g.gold;
    if (lv.hudLives != null && g.lives < lv.hudLives) lv.lifeHit = 1;
    lv.hudLives = g.lives;
    lv.goldPulse = Math.max(0, (lv.goldPulse || 0) - dt * 3.5);
    lv.lifeHit = Math.max(0, (lv.lifeHit || 0) - dt * 2.5);
    // barra de madeira pintada com tres encaixes (vidas, ouro, onda); sem a imagem, a capsula antiga
    const bar = A.skin && A.skin('barra');
    const shake = lv.lifeHit > 0 ? Math.sin(App.time * 60) * 3 * lv.lifeHit : 0;
    let fy = 68;
    if (bar) {
      const k = 0.36, bx = 4, by = -2;
      c.save();
      c.imageSmoothingEnabled = true;
      c.imageSmoothingQuality = 'high';
      c.drawImage(bar, bx, by, 1100 * k, 256 * k);
      c.restore();
      const cy = by + 145 * k;                       // meio dos encaixes (fonte 73..217)
      const sx = [139, 425, 712].map(v => bx + v * k);  // inicio de cada encaixe
      if (lv.lifeHit > 0) A.glow(c, sx[0] + 18, cy, 26, '#ff8a8a', 0.5 * lv.lifeHit);
      A.heart(c, sx[0] + 18 + shake, cy, 12 * (1 + 0.15 * lv.lifeHit));
      A.text(c, String(g.lives), sx[0] + 36, cy + 1, 22, lv.lifeHit > 0 ? '#ffc4c4' : '#fff', 'left');
      if (lv.goldPulse > 0) A.glow(c, sx[1] + 17, cy, 24, '#ffd77a', 0.55 * lv.goldPulse);
      A.coin(c, sx[1] + 17, cy, 11 * (1 + 0.22 * Math.sin(Math.PI * Math.min(1, lv.goldPulse))));
      A.text(c, String(Math.round(lv.hudGold)), sx[1] + 32, cy + 1, 20, '#ffe7a0', 'left');
      A.skullIcon(c, sx[2] + 17, cy - 1, 12);
      A.text(c, `${Math.max(1, g.wave)}/${wavesTxt(g)}`, sx[2] + 33, cy + 1, 20, '#fff', 'left');
      fy = 86;
    } else {
      A.darkPanel(c, 10, 8, 372, 54, 14);
      if (lv.lifeHit > 0) A.glow(c, 36, 35, 26, '#ff8a8a', 0.5 * lv.lifeHit);
      A.heart(c, 36 + shake, 35, 12 * (1 + 0.15 * lv.lifeHit));
      A.text(c, String(g.lives), 56, 36, 22, lv.lifeHit > 0 ? '#ffc4c4' : '#fff', 'left');
      if (lv.goldPulse > 0) A.glow(c, 116, 35, 24, '#ffd77a', 0.55 * lv.goldPulse);
      A.coin(c, 116, 35, 11 * (1 + 0.22 * Math.sin(Math.PI * Math.min(1, lv.goldPulse))));
      A.text(c, String(Math.round(lv.hudGold)), 134, 36, 22, '#ffe7a0', 'left');
      A.skullIcon(c, 246, 34, 12);
      A.text(c, `Onda ${Math.max(1, g.wave)}/${wavesTxt(g)}`, 264, 36, 17, '#fff', 'left');
    }
    // faixas de estado: desafio e tempestade
    if (g.mode === 'chal') {
      const ch = g.L.challenge;
      const label = `Desafio: ${ch.name} — ${ch.desc}`;
      c.font = `800 13px ${FONT_UI}`;
      A.darkPanel(c, 10, fy, Math.max(372, c.measureText(label).width + 54), 28, 10);
      A.star(c, 28, fy + 14, 8, '#7fffd4');
      A.text(c, label, 42, fy + 14.5, 13, '#bff8e8', 'left', null, false);
      fy += 34;
    }
    if (g.stormCfg && g.state === 'running') {
      const on = g.stormOn();
      const soon = !on && g.stormT <= g.stormCfg.warn;
      if (on || soon) {
        A.darkPanel(c, 10, fy, on ? 296 : 214, 28, 10);
        A.icon(c, 'sandstorm', 28, fy + 14, 11);
        A.text(c, on ? `Fake news: ${Math.ceil(g.stormLeft)}s · alcance -25%` : `Fake news em ${Math.ceil(g.stormT)}s`, 44, fy + 14.5, 13, on ? '#f2c890' : '#ffe9b0', 'left', null, false);
      }
    }

    // velocidade e pausa
    const busy = lv.overlay;
    let hov = UI.circle('speed', 1192, 36, 24, () => { lv.speed = lv.speed === 1 ? 2 : 1; Snd.play('click'); });
    A.roundBtn(c, 1192, 36, 23, { hover: hov, color: lv.speed > 1 ? '#f0b25c' : '#6aa84f' });
    A.text(c, lv.speed > 1 ? 'x2' : 'x1', 1192, 36, 19, '#fff', 'center');
    if (hov) UI.setTip(1192, 36, 'Velocidade', [lv.speed > 1 ? 'Rápido (2x). Clique para normal.' : 'Normal. Clique para 2x.', 'Atalho: F']);
    hov = UI.circle('pause', 1244, 36, 24, () => { if (!busy) { lv.paused = !lv.paused; Snd.play('click'); } });
    A.roundBtn(c, 1244, 36, 23, { hover: hov, color: '#c99a72' });
    A.icon(c, lv.paused ? 'play' : 'pause', 1244, 35, 16);

    // heroi
    const h = g.hero;
    const hx = 52, hy = 664;
    hov = UI.circle('heroPortrait', hx, hy, 36, () => this.toggleHero());
    A.softShadow(c, hx - 37, hy - 37, 74, 74, 37, 14, 0.3, 4, SOFT.card1);
    A.circ(c, hx, hy, 37, lv.mode === 'hero' ? SOFT.mint : SOFT.card1, lv.mode === 'hero' ? '#5fbfb0' : SOFT.line, 3);
    A.heroFace(c, hx, hy, 31, g.heroId);
    const med = A.skin && A.skin('medalhao');
    if (med) {
      // aro de madeira com folhas (fonte: centro 157x143, furo de raio ~86)
      const k = 33 / 86;
      c.save();
      c.imageSmoothingEnabled = true;
      c.drawImage(med, hx - 157 * k, hy - 143 * k, 320 * k, 284 * k);
      c.restore();
      if (lv.mode === 'hero') A.circ(c, hx, hy, 33, null, '#7fffd4', 3);
    }
    if (h.dead) A.circ(c, hx, hy, 31, 'rgba(25,20,18,0.62)');
    if (h.disabled) {
      A.lock(c, hx, hy, 16);
      if (hov) UI.setTip(hx, hy, `${g.H.name} está fora desta batalha`, ['Regra do desafio: sem herói.']);
    } else {
      c.beginPath(); c.arc(hx, hy, 34, -Math.PI / 2, -Math.PI / 2 + U.TAU * (h.dead ? 0 : h.hp / h.maxHp));
      c.strokeStyle = '#5ad9c4'; c.lineWidth = 4; c.stroke();
      A.circ(c, hx + 26, hy + 24, 11, '#5fbfb0', '#ffffff', 2);
      A.text(c, String(h.level), hx + 26, hy + 24.5, 12, '#fff', 'center');
      if (h.dead) A.text(c, String(Math.ceil(h.respawnT)), hx, hy, 26, '#fff', 'center');
      if (hov) {
        const H = g.H;
        const nx = DATA.HERO_XP[h.level] || null;
        UI.setTip(hx, hy, `${H.name}, ${H.title}`, [
          `Nível ${h.level} · Vida ${Math.ceil(h.hp)}/${h.maxHp}`,
          `Dano ${Math.round(h.dmg[0])}–${Math.round(h.dmg[1])} · Armadura ${pct(h.armor)}`,
          H.abilities.map(a => a.name).join(', ') + ' (automáticas)',
          nx ? `XP ${Math.floor(g.heroXp)}/${nx}` : 'Nível máximo',
          'Clique no retrato e depois no mapa (atalho: H)',
        ]);
      }
    }
    // feiticos
    [['fury', 134], ['riders', 204], ['stampede', 274]].forEach(([id, x], i) => {
      const sp = g.spells[id], y = 670;
      const ready = g.canCast(id);
      const hv = UI.circle('spell' + id, x, y, 30, () => this.castMode(id));
      if (ready) A.glow(c, x, y, 44, id === 'stampede' ? '#b6ec4a' : '#ffe08a', 0.25 + Math.sin(App.time * 4) * 0.1);
      A.roundBtn(c, x, y, 29, { hover: hv, color: lv.mode === 'spell' && lv.spell === id ? '#5fbfb0' : id === 'stampede' ? '#6aa84f' : '#b98f6c', disabled: g.noSpells });
      if (id === 'stampede') {
        // Encanto: anel enchendo ate o custo do Estouro; o bicho do botao e o ultimo libertado
        const cost = g.stampedeCost(), k = Math.min(1, g.charm / cost);
        c.beginPath(); c.arc(x, y, 33, -Math.PI / 2, -Math.PI / 2 + U.TAU * k);
        c.strokeStyle = k >= 1 ? '#e6ff7a' : '#9fd36a'; c.lineWidth = 4; c.lineCap = 'round'; c.stroke(); c.lineCap = 'butt';
        if (!A.freedIcon(c, g.herdPool()[0], x, y + 2, 19)) A.icon(c, 'riders', x, y, 20);
        A.chip(c, x - 22, y + 24, String(Math.floor(g.charm)), { color: '#3f6b2a', size: 12, h: 20 });
      } else A.icon(c, id, x, y, 20);
      if (g.noSpells) A.lock(c, x, y + 2, 13);
      else if (id === 'stampede') {
        if (!ready) { c.fillStyle = 'rgba(60,40,30,0.35)'; c.beginPath(); c.arc(x, y, 27, 0, U.TAU); c.fill(); }
      } else if (!ready) {
        c.beginPath(); c.moveTo(x, y);
        c.arc(x, y, 27, -Math.PI / 2, -Math.PI / 2 + U.TAU * (sp.cd / sp.max));
        c.closePath(); c.fillStyle = 'rgba(60,40,30,0.5)'; c.fill();
        A.text(c, String(Math.ceil(sp.cd)), x, y, 18, '#fff', 'center');
      }
      A.circ(c, x + 21, y - 21, 9, SOFT.card1, SOFT.line, 1.5);
      A.text(c, String(i + 1), x + 21, y - 20.5, 11, SOFT.ink, 'center', null, false);
      if (hv) {
        const S = DATA.SPELLS[id];
        UI.setTip(x, y, S.name, g.noSpells ? ['Regra do desafio: sem operações.'] : id === 'stampede'
          ? [S.desc, `Delação ${Math.floor(g.charm)}/${g.stampedeCost()}. ${DATA.CHARM.desc}`]
          : [S.desc, `Recarga ${Math.round(sp.max)}s`]);
      }
    });
  },

  infoBar(c) {
    const g = App.game, sel = App.lv.sel;
    const w = 520, h = 66, x = W / 2 - w / 2 + 40, y = H - h - 10;
    const chipsRow = (list, yy) => {
      let cx = x + 74;
      for (const ch of list) {
        const cw = A.measure(c, ch.text, 13, 800) + 18 + (ch.icon ? 18 : 0);
        if (cx + cw > x + w - 10) break;
        cx += A.chip(c, cx, yy, ch.text, { icon: ch.icon, color: ch.color || UIK.inkSoft, size: 13, h: 24 }) + 6;
      }
    };
    if (sel.enemy) {
      const e = sel.enemy;
      if (e.dead || e.reached) { App.lv.sel = null; return; }
      const T = e.T;
      A.card(c, x, y, w, h);
      A.medal(c, e.type, x + 36, y + h / 2, 25, { bg: '#ffeee6', ring: '#ec9a86' });
      A.label(c, 'INIMIGO', x + 74, y + 15, TYPE.cap, UIK.tag, 'left', 900);
      A.label(c, shortName(T.name), x + 74, y + 32, 17, UIK.ink, 'left', 900);
      const bx = x + 74 + Math.max(150, A.measure(c, shortName(T.name), 17, 900) + 16);
      Render.bar(c, bx, y + 20, 130, 10, e.hp / e.maxHp, '#f3d6cf', '#e2563a');
      A.label(c, `${Math.ceil(e.hp)} / ${e.maxHp}`, bx + 65, y + 36, 12, UIK.inkSoft, 'center', 800);
      const st = [];
      if (e.wetT > 0) st.push({ text: 'Molhado', icon: 'wet', color: UIK.G.wet });
      if (e.blindT > 0) st.push({ text: 'Cego', icon: 'eye', color: UIK.G.eye });
      if (e.markT > 0) st.push({ text: 'Marcado', icon: 'crit', color: UIK.G.crit });
      if (e.groundT > 0) st.push({ text: 'No chão', icon: 'flying', color: UIK.G.flying });
      if (e.frozenT > 0) st.push({ text: 'Congelado', icon: 'freeze', color: UIK.G.freeze });
      chipsRow([
        { text: 'Armadura ' + lvlWord(Math.max(0, T.armor - e.armorRed)), icon: 'armor', color: UIK.G.armor },
        { text: 'Magia ' + lvlWord(T.mres), icon: 'mres', color: UIK.G.mres },
        { text: speedWord(T.speed), icon: 'speed', color: UIK.G.speed },
        { text: `-${T.lives}`, icon: 'lives', color: UIK.G.lives },
        ...st,
      ].slice(0, 4), y + 52);
    } else if (sel.tower) {
      const t = sel.tower;
      const name = t.spec ? DATA.SPECS[t.spec].name : DATA.TOWERS[t.type].name;
      A.card(c, x, y, w, h);
      A.medal(c, t.spec || t.type, x + 36, y + h / 2, 25, { tier: t.tier });
      A.label(c, t.spec ? 'ESPECIALIZAÇÃO' : `TORRE · NÍVEL ${t.tier}`, x + 74, y + 15, TYPE.cap, UIK.tag, 'left', 900);
      A.label(c, name, x + 74, y + 32, 17, UIK.ink, 'left', 900);
      const rows = towerStatRows(g, { type: t.type, tier: t.tier, spec: t.spec, abil: t.abil, spot: t.spot }).slice(0, 3);
      const extra = [];
      if (g.prioOptions(t).length) extra.push({ text: 'Alvo: ' + PRIO_NAMES[t.prio], icon: 'range', color: '#6a7ad0' });
      if (t.bDmg > 0) extra.push({ text: `+${pct(t.bDmg)} dano`, icon: 'star', color: UIK.G.star });
      if (t.disabledT > 0) extra.push({ text: `Desligada ${Math.ceil(t.disabledT)} s`, icon: 'time', color: UIK.bad });
      chipsRow([...rows.map(r => ({ text: String(r.value), icon: r.g, color: UIK.G[r.g] })), ...extra], y + 52);
    }
  },

  notices(c, dt) {
    const lv = App.lv, g = App.game;
    while (g.announce.length) lv.noticeQ.push({ kind: 'enemy', type: g.announce.shift(), t: 0 });
    // primeira vez com Encanto para o Estouro da Mata: explica de onde ele vem
    if (g.charm >= g.stampedeCost() && !g.noSpells && !Save.data.tips.includes('charm')) {
      Save.data.tips.push('charm');
      Save.write();
      lv.noticeQ.push({ kind: 'tip', icon: 'riders', title: 'Delação cheia!', text: 'Cada adversário derrotado vira delator e rende Delação. Aperte 3 (ou o botão verde) e clique na estrada: os delatores voltam correndo contra a própria turma.', t: 0 });
    }
    const n = lv.noticeQ[0];
    if (!n || lv.overlay) return;
    if (n.t === 0) Snd.play('chime', 0.7);
    if (!lv.paused && !lv.overlay) n.t += dt;
    const T = 7;
    if (n.t > T) { lv.noticeQ.shift(); return; }
    const k = n.t < 0.5 ? U.easeOutBack(n.t / 0.5) : n.t > T - 0.4 ? 1 - U.easeInOut((n.t - (T - 0.4)) / 0.4) : 1;
    let label, title, text, accent, chips = [];
    if (n.kind === 'tower') {
      const D = DATA.TOWERS[n.type];
      label = 'Nova torre no arsenal'; title = D.name; text = D.desc; accent = '#5fbfb0';
      chips = [[`Custo ${D.tiers[0].cost}`, 'gold', '#e9b84a']];
    } else if (n.kind === 'tip') {
      label = 'Novidade nesta fase'; title = n.title; text = n.text; accent = '#e8b45c';
    } else {
      const E = DATA.ENEMIES[n.type];
      label = 'Novo adversário'; title = shortName(E.name); text = E.tip; accent = '#ec8a76';
      chips = [[`Vida ${E.hp}`, 'hp', '#ec8a76'], ...enemyChips(E)].slice(0, 4);
    }
    const w = 520, h = chips.length ? 112 : 86, x = W / 2 - w / 2, y = -h - 14 + k * (h + 84);
    UI.rect('notice', x, y, w, h, () => { lv.noticeQ.shift(); });
    c.save();
    c.globalAlpha = U.clamp(k * 1.5, 0, 1);
    A.softShadow(c, x, y, w, h, 20, 22, 0.28, 8, SOFT.card1);
    A.rrect(c, x, y, w, h, 20, SOFT.card1, SOFT.line, 2);
    c.save();
    c.beginPath(); c.roundRect ? c.roundRect(x, y, w, h, 20) : c.rect(x, y, w, h); c.clip();
    A.rect(c, x, y, 8, h, accent);
    A.rect(c, x, y + h - 4, w * (1 - n.t / T), 4, U.rgba(accent, 0.55));
    c.restore();
    A.circ(c, x + 50, y + 46, 31, U.rgba(accent, 0.18), U.rgba(accent, 0.65), 2.5);
    A.icon(c, n.kind === 'tip' ? n.icon : n.type, x + 50, y + 46, 25, { tier: 1, time: App.time });
    A.text(c, label.toUpperCase(), x + 94, y + 20, 11, U.shade(accent, -0.25), 'left', null, false);
    A.text(c, title, x + 94, y + 41, 19, SOFT.ink, 'left', { family: FONT_UI, weight: 900 }, false);
    A.text(c, UKB.fit(c, text, w - 112, 14, 600), x + 94, y + 63, 14, SOFT.inkSoft, 'left', { family: FONT_UI, weight: 600 }, false);
    let cx = x + 94;
    for (const [t, ic, col] of chips) cx += UKB.chip(c, cx, y + 89, t, { icon: ic, color: col }) + 6;
    c.restore();
  },

  pauseMenu(c) {
    const lv = App.lv;
    UI.blocker();
    lv.pauseT = (lv.pauseT || 0) + (this._dt || 0);
    const k = U.clamp(lv.pauseT / 0.3, 0, 1);
    c.fillStyle = `rgba(70,45,28,${0.38 * k})`; c.fillRect(0, 0, W, H);
    const x = 420, y = 170, w = 440, h = 520;
    const sc = 0.9 + 0.1 * U.easeOutBack(k);
    c.save();
    c.globalAlpha = Math.min(1, k * 1.6);
    c.translate(W / 2, y + h / 2); c.scale(sc, sc); c.translate(-W / 2, -(y + h / 2));
    A.panel(c, x, y, w, h);
    A.text(c, 'Pausa', W / 2, y + 52, 40, SOFT.title, 'center', { family: FONT_TITLE, weight: 700 }, 'rgba(255,255,255,0.9)', 5);
    const btn = (key, label, by, color, cb) => {
      const hv = UI.rect(key, x + 100, by, 240, 50, cb);
      A.btn(c, x + 100, by, 240, 50, label, { hover: hv, color });
    };
    btn('resume', 'Continuar', y + 96, 'green', () => { lv.paused = false; Snd.play('click'); });
    btn('restart', 'Recomeçar', y + 160, 'gold', () => { const g = App.game; App.endLevel(false); App.startLevel(g.levelIdx, g.mode, g.loadout); });
    btn('quit', 'Sair para o mapa', y + 224, 'red', () => { App.endLevel(false); App.go('map'); });
    soundToggles(c, W / 2 - 50, y + 306);
    // atalhos do teclado em teclas
    A.line(c, x + 30, y + 344, x + w - 30, y + 344, 'rgba(120,80,40,0.16)', 1.5);
    A.text(c, 'Atalhos', x + 34, y + 368, 16, SOFT.ink, 'left', { family: FONT_UI, weight: 900 }, false);
    const keys = [['Espaço', 'Pausa'], ['F', 'Velocidade'], ['1  2  3', 'Operações'], ['H', 'Herói'], ['N', 'Próxima onda'], ['T', 'Alvo da torre'], ['G', 'Manobra'], ['Esc', 'Cancelar']];
    keys.forEach(([key, label], i) => {
      const kx = x + 34 + (i % 2) * 196, ky = y + 400 + Math.floor(i / 2) * 30;
      c.font = `800 13px ${FONT_UI}`;
      const kw = Math.max(26, c.measureText(key).width + 16);
      A.rrect(c, kx, ky - 11, kw, 23, 7, '#ffffff', SOFT.line, 1.5);
      A.rect(c, kx + 2, ky + 9, kw - 4, 2, 'rgba(160,120,90,0.25)');
      A.text(c, key, kx + kw / 2, ky + 0.5, 13, SOFT.ink, 'center', null, false);
      A.text(c, label, kx + kw + 10, ky + 0.5, 14, SOFT.inkSoft, 'left', null, false);
    });
    c.restore();
  },

  endPanel(c, dt) {
    const g = App.game, lv = App.lv;
    lv.endT += dt;
    UI.blocker();
    const k = Math.min(1, lv.endT / 0.4);
    c.fillStyle = `rgba(70,45,28,${0.42 * k})`; c.fillRect(0, 0, W, H);
    const won = g.state === 'won';
    const s = U.easeOutBack(k);
    c.save();
    c.translate(W / 2, H / 2);
    c.scale(s, s);
    c.translate(-W / 2, -H / 2);
    const x = 390, y = 104, w = 500, h = 520;
    A.panel(c, x, y, w, h);
    const by = y + h - 86;
    // posicao dos botoes (o teste ponta a ponta le daqui)
    lv.endBtns = { a: [x + 60 + 85, by + 28], b: [x + 270 + 85, by + 28] };
    const rx = x + 70, rw = w - 140;
    if (won) {
      const chal = g.mode === 'chal';
      A.text(c, chal ? 'Desafio vencido!' : 'Vitória!', W / 2, y + 58, chal ? 44 : 54, '#e8a23e', 'center', { family: FONT_TITLE, weight: 700 }, 'rgba(255,255,255,0.95)', 7);
      for (let i = 0; i < 3; i++) {
        const t0 = 0.6 + i * 0.35;
        const kk = U.clamp((lv.endT - t0) / 0.3, 0, 1);
        const sx = W / 2 + (i - 1) * 92, sy = y + 140 - (i === 1 ? 12 : 0);
        if (chal && i !== 1) continue;
        const painted = !chal && A.starSkin;
        if (!(painted && A.starSkin(c, sx, sy, 40, false))) A.star(c, sx, sy, 36, 'rgba(160,120,90,0.22)', null);
        const has = chal ? true : i < g.stars;
        if (has && kk > 0) {
          if (!lv.starSnd[i]) { lv.starSnd[i] = true; Snd.play('stars'); }
          const rr = 40 * U.easeOutElastic(kk);
          if (!(painted && A.starSkin(c, sx, sy, rr, true))) A.star(c, sx, sy, 36 * U.easeOutElastic(kk), chal ? '#7fffd4' : '#ffd54a');
        }
      }
      const tm = Math.floor(g.endTime);
      const rows = [
        { g: 'lives', label: 'Votos restantes', value: `${g.lives} de ${g.maxLives}` },
        { g: 'dmg', label: 'Inimigos derrotados', value: String(g.stats.kills) },
        { g: 'time', label: 'Tempo', value: `${Math.floor(tm / 60)}:${String(tm % 60).padStart(2, '0')}` },
      ];
      if (lv.newStars > 0) rows.push({ g: 'star', label: 'Estrelas para Melhorias', value: '+' + lv.newStars, good: true });
      const rh = UKB.rows(c, rx, y + 194, rw, rows);
      const cy = y + 194 + rh + 14;
      if (lv.unlocked && lv.unlocked.length) {
        const un = lv.unlocked, n = un.length;
        A.rrect(c, rx, cy, rw, 66, 16, 'rgba(95,191,176,0.14)', '#5fbfb0', 2);
        un.forEach((tp, k) => {
          A.circ(c, rx + 36 + k * 54, cy + 33, 25, SOFT.card1, '#5fbfb0', 2);
          A.icon(c, tp, rx + 36 + k * 54, cy + 33, 21, { tier: 1, time: App.time });
        });
        const tx0 = rx + 18 + n * 54;
        A.text(c, n > 1 ? 'NOVAS TORRES LIBERADAS' : 'NOVA TORRE LIBERADA', tx0, cy + 22, 11, '#3f8f82', 'left', null, false);
        A.text(c, un.map(tp => DATA.TOWERS[tp].name).join(' e '), tx0, cy + 44, 19, SOFT.ink, 'left', { family: FONT_UI, weight: 900 }, false);
      } else if (g.levelIdx === DATA.LEVELS.length - 1 && !chal) {
        UKB.chip(c, rx, cy + 20, 'Ninguém subiu a rampa. A faixa é sua!', { icon: 'star', color: '#e9b84a' });
      } else if (!chal && !Save.data.chal[g.levelIdx]) {
        UKB.chip(c, rx, cy + 20, `Desafio liberado: ${g.L.challenge.name} (+1 estrela)`, { icon: 'star', color: '#5fbfb0' });
      }
      let hv = UI.rect('cont', x + 60, by, 170, 56, () => App.go('map'));
      A.btn(c, x + 60, by, 170, 56, 'Continuar', { hover: hv, color: 'green' });
      hv = UI.rect('again', x + 270, by, 170, 56, () => App.startLevel(g.levelIdx, g.mode, g.loadout));
      A.btn(c, x + 270, by, 170, 56, 'Repetir', { hover: hv, color: 'gold' });
    } else {
      A.text(c, 'Derrota', W / 2, y + 62, 54, '#d9705e', 'center', { family: FONT_TITLE, weight: 700 }, 'rgba(255,255,255,0.95)', 7);
      A.skullIcon(c, W / 2, y + 140, 40);
      const rh = UKB.rows(c, rx, y + 194, rw, [
        g.mode === 'endless'
          ? { g: 'time', label: App.lv.record ? 'Novo recorde na Recontagem!' : 'Recorde da Recontagem', value: `onda ${Save.data.endless}`, good: !!App.lv.record }
          : { g: 'time', label: 'A muralha caiu na onda', value: `${g.wave} de ${g.totalWaves}`, good: false },
        { g: 'dmg', label: 'Inimigos derrotados', value: String(g.stats.kills) },
      ]);
      const ty = y + 194 + rh + 16;
      A.rrect(c, rx, ty, rw, 58, 16, 'rgba(233,184,74,0.14)', '#e9b84a', 1.8);
      A.text(c, 'DICA', rx + 18, ty + 18, 11, '#a8782a', 'left', null, false);
      A.text(c, UKB.fit(c, dicaDerrota(g), rw - 36, 15, 700), rx + 18, ty + 39, 15, SOFT.ink, 'left', null, false);
      let hv = UI.rect('retry', x + 60, by, 170, 56, () => App.startLevel(g.levelIdx, g.mode, g.loadout));
      A.btn(c, x + 60, by, 170, 56, 'Tentar de novo', { hover: hv, color: 'green', size: 20 });
      hv = UI.rect('tomap', x + 270, by, 170, 56, () => App.go('map'));
      A.btn(c, x + 270, by, 170, 56, 'Mapa', { hover: hv, color: 'red' });
    }
    c.restore();
  },
};

function dicaDerrota(g) {
  const dicas = [
    'Chame ondas cedo só com a defesa folgada.',
    DATA.fmt('O dano {de:mage} ignora couraça; {o:archer} acerta voadores.'),
    DATA.fmt('{Um:barracks} perto das curvas segura a fila.'),
    'Redistribua as estrelas nas Melhorias.',
    'Operação da PF: ótima em grupos e chefes.',
    'Troque o Arsenal olhando os adversários da fase.',
    'Alvo "Mais forte" ajuda muito contra chefes.',
  ];
  const leaked = g.leaks.map(s => s.split('@')[0]);
  const count = t => leaked.filter(x => x === t).length;
  if (count('specter') >= 3) return DATA.fmt('O Lyra Secreto passou sem ninguém ver: leve {um:banner}.');
  if (count('scorpling') >= 5) return `${DATA.ENEMIES.scorpling.name}: dano em área na saída.`;
  if (count('bulwark') >= 3) return DATA.fmt(`${DATA.ENEMIES.bulwark.name}: use {t:mage}, {t:artillery} ou {tropa}.`);
  if (leaked.includes('ifrit')) return DATA.fmt('O Fundão voa: molhe-o {em:cistern} e derrube-o com {s:tornado}.');
  return dicas[(g.wave + g.levelIdx) % dicas.length];
}

function soundToggles(c, x, y) {
  let hv = UI.circle('music', x, y, 22, () => { App.setMusic(!Snd.musicOn); });
  A.roundBtn(c, x, y, 21, { hover: hv, color: '#c99a72' });
  A.icon(c, 'music', x, y, 18, { off: !Snd.musicOn });
  hv = UI.circle('sfx', x + 100, y, 22, () => { App.setSfx(!Snd.sfxOn); });
  A.roundBtn(c, x + 100, y, 21, { hover: hv, color: '#c99a72' });
  A.icon(c, 'sfx', x + 100, y, 18, { off: !Snd.sfxOn });
}

function drawTip(c, tip) {
  // cartao estruturado (v2); as dicas antigas (so linhas de texto) caem no formato simples abaixo
  if (tip.card && A.tipCard) { A.tipCard(c, tip); return; }
  const pad = 16, w = 320;
  const lines = [];
  for (const l of tip.lines || []) for (const s of A.wrap(c, l, w - pad * 2, 14, 600)) lines.push(s);
  const rows = tip.enemies ? Math.ceil(tip.enemies.length / 6) : 0;
  const h = pad * 2 + 26 + lines.length * 20 + (tip.cost != null ? 34 : 0) + rows * 42;
  let x = tip.x + 96, y = tip.y - h / 2;
  if (x + w > W - 8) x = tip.x - 96 - w;
  if (x < 8) x = 8;
  y = U.clamp(y, 74, H - h - 8);
  A.card(c, x, y, w, h);
  A.label(c, tip.title, x + pad, y + pad + 11, TYPE.h2, UIK.ink, 'left', 900);
  let yy = y + pad + 38;
  for (const l of lines) { A.label(c, l, x + pad, yy, 14, UIK.inkSoft, 'left', 600); yy += 20; }
  if (tip.enemies) {
    tip.enemies.forEach(([type, n], i) => {
      const ex = x + pad + 16 + (i % 6) * 48, ey = yy + 12 + Math.floor(i / 6) * 42;
      const isNew = tip.seen && !tip.seen.has(type);
      A.circ(c, ex, ey, 17, isNew ? '#ffe9de' : UIK.card2, isNew ? '#ec8a76' : UIK.line, 1.5);
      A.icon(c, type, ex, ey, 14, { time: App.time });
      A.label(c, 'x' + n, ex + 13, ey + 13, 12, UIK.ink, 'left', 900);
      if (isNew) A.label(c, 'NOVO', ex, ey - 19, 9, '#d9624e', 'center', 900);
    });
    yy += rows * 42;
  }
  if (tip.cost != null) A.pricePill(c, x + pad, yy + 8, tip.cost, tip.ok);
}

// ------------------------------------------------------------ titulo (com partida demonstrativa ao fundo)
const Title = {
  demo: null,
  SUB: 'Não deixe a turma do outro lado subir a rampa',
  choose: false,
  makeDemo() {
    const g = new Game(0, { mute: true, upgrades: { archer: 3, mage: 3, artillery: 3, barracks: 3, eng: 3, cmd: 3, spells: 3 }, heroXp: 3000 });
    g.gold = 1e6;
    g.quickBuild = true;
    const plan = [[3, 'archer', 'ballista'], [5, 'cistern', null], [1, 'artillery', 'mortar'], [7, 'barracks', null], [9, 'mage', 'lightning'], [2, 'windmill', null], [6, 'artillery', null], [4, 'barracks', 'lancers'], [8, 'archer', 'blowgun'], [0, 'mage', 'sun']];
    for (const [si, type, spec] of plan) {
      const t = g.build(g.spots[si], type);
      if (!t) continue;
      g.upgrade(t); g.upgrade(t);
      if (spec) g.specialize(t, spec);
    }
    g.callWave();
    g.fx = [];
    this.demo = g;
  },
  // cena propria do inicio (sprites/titulo_*, da sessao do cenario): fundo, frente com alfa e luz das brasas, em
  // paralaxe leve com o mouse; os 4 herois em espera na clareira (pes em x/y, 2 de cada lado virados para o meio)
  imgs: null,
  t0: null,
  px: 0, py: 0,
  // camera do fundo: perspectiva 40 mm a 2,2 m, pes a 9,5 m vistos a ~12,5 graus (a vitrine e de 13: casa);
  // 148,7 px por metro nos pes. [sprite, x, y, espelha, escala]; o Boitata e grande, vai um pouco menor
  HEROES: [['hero', 190, 650, false, 1], ['caipora', 330, 650, false, 1], ['benzedeira', 950, 650, true, 1], ['boitata', 1090, 650, true, 1]],
  HERO_K: 2.3,
  // eixo da pluma da Fumaca Negra na tela (pe em baixo) e pivos das folhas da camada da frente
  PLUMA: [[1084, 309], [1089, 256], [1103, 187], [1123, 119], [1151, 51], [1180, 0]],
  scene() {
    const M = typeof SPRITE_META !== 'undefined' && SPRITE_META.titulo;   // {fundo, frente, luz}: caminhos das camadas
    if (!M) return null;
    if (!this.imgs) {
      this.imgs = {};
      for (const k of ['fundo', 'frente', 'luz']) {
        if (!M[k]) continue;
        const im = new Image();
        im.onload = () => { this.imgs[k] = im; };
        im.src = M[k];
      }
    }
    return this.imgs.fundo;
  },
  layer(c, im, k, mode, alpha) {
    if (!im) return;
    const z = 1 + k * 0.0035;
    c.save();
    if (mode) c.globalCompositeOperation = mode;
    if (alpha != null) c.globalAlpha = alpha;
    c.drawImage(im, (W - W * z) / 2 - this.px * k, (H - H * z) / 2 - this.py * k * 0.6, W * z, H * z);
    c.restore();
  },
  // ponto da pluma a uma altura 0..1 (0 = pe)
  pluma(u) {
    const P = this.PLUMA, f = Math.min(P.length - 1.001, u * (P.length - 1)), i = Math.floor(f), s = f - i;
    return [P[i][0] + (P[i + 1][0] - P[i][0]) * s, P[i][1] + (P[i + 1][1] - P[i][1]) * s];
  },
  drawScene(c, dt, t) {
    const mx = UI.mx >= 0 ? UI.mx / W - 0.5 : 0, my = UI.my >= 0 ? UI.my / H - 0.5 : 0;
    const e = Math.min(1, (dt || 0) * 2.5);
    this.px += (mx - this.px) * e; this.py += (my - this.py) * e;
    const bx = -this.px * 10, by = -this.py * 6;   // o que mora no fundo anda junto com ele
    this.layer(c, this.imgs.fundo, 10);
    this.layer(c, this.imgs.luz, 10, 'lighter', 0.38 + 0.12 * Math.sin(t * 1.7) + 0.05 * Math.sin(t * 5.3));
    // luzes acendendo no entardecer: janelas do Planalto, torres do Congresso e postes (pontos do titulo.json)
    const LZ = (SPRITE_META.titulo.cam && SPRITE_META.titulo.cam.luzes) || [];
    c.save();
    c.globalCompositeOperation = 'lighter';
    LZ.forEach(([lx, ly, tipo], i) => {
      const on = 0.55 + 0.25 * Math.sin(t * (tipo === 'poste' ? 1.3 : 0.6) + i * 1.7);
      A.glow(c, lx + bx, ly + by, tipo === 'poste' ? 16 : 26, tipo === 'poste' ? '#ffd890' : '#ffe6b0', 0.35 * on);
    });
    c.restore();
    // herois em espera
    this.HEROES.forEach(([k, x, y, flip, sc], i) => {
      A.heroShow(c, k, x - this.px * 16, y - this.py * 8, t, { flip, off: i * 7, scale: this.HERO_K * sc, tint: 'rgba(255,160,80,0.10)' });
    });
    // folhas da frente balancando: cada canto gira um pouco em volta do proprio pivo (galho e cipos no alto,
    // taiobas embaixo); o meio da camada e vazio, entao o recorte por quadrante nao aparece
    const fr = this.imgs.frente;
    if (fr) {
      for (const [qx, qy, px, py, amp, sp] of [[0, 0, 130, 0, 0.012, 0.8], [640, 0, 1195, 0, 0.01, 0.65], [0, 360, 0, 720, 0.016, 1.1], [640, 360, 1280, 720, 0.016, 0.95]]) {
        c.save();
        c.beginPath(); c.rect(qx, qy, 640, 360); c.clip();
        const a = amp * Math.sin(t * sp + qx * 0.01 + qy * 0.02);
        c.translate(px, py); c.rotate(a); c.translate(-px, -py);
        this.layer(c, fr, 26);
        c.restore();
      }
    }
    // flores de ipe caindo devagar dos galhos dos cantos de cima
    for (let i = 0; i < 14; i++) {
      const ph = (t * (0.035 + (i % 4) * 0.008) + i * 0.137) % 1;
      const esq = i % 2 === 0;
      const x0 = esq ? 40 + ((i * 71) % 260) : 980 + ((i * 53) % 260);
      const x = x0 + ph * (esq ? 120 : -120) + Math.sin(t * 1.4 + i) * 14 - this.px * 20;
      const y = 60 + ph * 640 - this.py * 10;
      c.save();
      c.translate(x, y);
      c.rotate(t * 1.5 + i);
      c.globalAlpha = Math.min(1, (1 - ph) * 4, ph * 8) * 0.9;
      c.fillStyle = i % 3 ? '#f7cf3c' : '#f2b81f';
      c.beginPath(); c.ellipse(0, 0, 5, 3.5, 0, 0, U.TAU); c.fill();
      c.fillStyle = '#d9822b';
      c.beginPath(); c.arc(0.8, 0, 1.2, 0, U.TAU); c.fill();
      c.restore();
    }
  },
  draw(c, dt) {
    const t = App.time;
    if (this.scene()) this.drawScene(c, dt, t);
    else {
    if (!this.demo) this.makeDemo();
    const g = this.demo;
    g.gold = 1e6;
    for (let i = 0; i < 2; i++) g.update(STEP);
    if (g.countdown > 3) g.countdown = 3;
    if (g.state === 'won' || g.state === 'lost' || g.lives < 5) this.makeDemo();
    g.sounds.length = 0;
    Render.ensureBg(g, App.scale);
    Render.level(c, g, {});
    // escurecimento
    const gr = c.createLinearGradient(0, 0, 0, H);
    gr.addColorStop(0, 'rgba(25,10,0,0.75)');
    gr.addColorStop(0.45, 'rgba(25,10,0,0.25)');
    gr.addColorStop(1, 'rgba(25,10,0,0.8)');
    c.fillStyle = gr; c.fillRect(0, 0, W, H);
    }
    // logo: entra caindo e quicando na primeira vez que a tela aparece
    if (this.t0 == null) { this.t0 = t; Snd.play('titleIn'); }
    const ent = Math.min(1, (t - this.t0) / 1.1);
    const bob = Math.sin(t * 1.4) * 4 - 300 * (1 - U.bounce(ent));
    A.glow(c, W / 2, 150 + bob, 300, '#ffd27a', 0.22);
    const logo = A.skin && A.skin('logo');
    if (logo) {
      // logo de madeira entalhada pintado no estilo do conceito (sprites/ui/logo.png)
      const lw = 620, lh = lw * logo.naturalHeight / logo.naturalWidth;
      c.save();
      c.imageSmoothingEnabled = true;
      c.imageSmoothingQuality = 'high';
      c.drawImage(logo, W / 2 - lw / 2, 178 + bob - lh / 2, lw, lh);
      c.restore();
    } else {
    c.save();
    c.font = `800 96px ${FONT_TITLE}`;
    c.textAlign = 'center'; c.textBaseline = 'middle';
    const lg = c.createLinearGradient(0, 96, 0, 196);
    lg.addColorStop(0, '#fff4c0'); lg.addColorStop(0.5, '#f2c84a'); lg.addColorStop(1, '#c87a2a');
    c.lineJoin = 'round';
    c.strokeStyle = '#4e2f1a'; c.lineWidth = 15; c.strokeText('NINGUÉM', W / 2, 146 + bob);
    c.fillStyle = lg; c.fillText('NINGUÉM', W / 2, 146 + bob);
    c.font = `800 50px ${FONT_TITLE}`;
    const sw = c.measureText('SOBE A RAMPA').width;
    c.strokeStyle = '#fbf1dc'; c.lineWidth = 10; c.strokeText('SOBE A RAMPA', W / 2, 222 + bob);
    c.fillStyle = '#3f7f3a'; c.fillText('SOBE A RAMPA', W / 2, 222 + bob);
    c.restore();
    // flores de ipe amarelo ao lado do "sobe a rampa"
    for (const sd of [-1, 1]) {
      A.ipe(c, W / 2 + sd * (sw / 2 + 30), 220 + bob, 15, t * 0.4 * sd);
      A.ipe(c, W / 2 + sd * (sw / 2 + 50), 204 + bob, 9, -t * 0.5 * sd + 1);
    }
    }
    c.font = `800 17px ${FONT_UI}`;
    const stw = c.measureText(Title.SUB).width + 40;
    const sty = A.skin && A.skin('logo') ? 322 : 254;   // o logo pintado e mais alto que o de texto
    A.softShadow(c, W / 2 - stw / 2, sty + bob, stw, 34, 17, 12, 0.25, 4, 'rgba(255,248,236,0.92)');
    A.text(c, Title.SUB, W / 2, sty + 17.5 + bob, 17, SOFT.ink, 'center', null, false);
    const hv = UI.rect('play', W / 2 - 130, 470, 260, 76, () => { if (!Save.data.side) { this.choose = true; Snd.play('open'); } else App.go('map'); });
    // botao respirando (cresce um pouco no ritmo do logo)
    const pk = 1 + 0.025 * Math.sin(t * 2.6) * Math.min(1, ent * 2);
    c.save();
    c.translate(W / 2, 508); c.scale(pk, pk); c.translate(-W / 2, -508);
    c.globalAlpha = Math.min(1, ent * 1.6);
    A.btn(c, W / 2 - 130, 470, 260, 76, 'JOGAR', { hover: hv, color: 'green', size: 34, font: { family: FONT_HEAD, weight: 700 } });
    c.restore();
    // no alto a direita: embaixo ficam os herois
    soundToggles(c, 1150, 40);
    c.font = `800 13px ${FONT_UI}`;
    const CRED = 'Sátira política · obra de ficção · caricaturas feitas com IA · sem vínculo com partidos ou candidatos';
    const crw = c.measureText(CRED).width + 28;
    A.rrect(c, W / 2 - crw / 2, 677, crw, 26, 13, 'rgba(255,248,236,0.8)', SOFT.line, 1.2);
    A.text(c, CRED, W / 2, 690.5, 13, SOFT.inkSoft, 'center', null, false);
    if (this.choose) this.drawChoose(c, t);
  },
  // escolha da chapa: um cartao por chapa, com os 2 herois em espera e quem ela enfrenta; a outra vira a turma rival
  drawChoose(c, t) {
    UI.blocker('chooseBlock');
    c.fillStyle = 'rgba(22,12,6,0.66)';
    c.fillRect(0, 0, W, H);
    A.text(c, 'Escolha a sua chapa', W / 2, 58, 40, '#fff4dc', 'center', { family: FONT_TITLE, weight: 700 }, 'rgba(40,20,8,0.9)', 7);
    A.text(c, 'A outra chapa vira a turma adversária. Dá para trocar depois, no mapa.', W / 2, 98, 16, '#f3e3c4', 'center', null, false);
    for (const [sd, x] of [['R', 80], ['V', 680]]) {
      const S = DATA.SIDES[sd], rv = sd === 'R' ? 'V' : 'R', y = 124, w = 520, h = 548;
      const hv = UI.rect('chapa' + sd, x, y, w, h, () => {
        Save.setSide(sd);
        this.choose = false;
        Snd.play('open');
        App.go('map');
      });
      c.save();
      if (hv) { c.translate(x + w / 2, y + h / 2); c.scale(1.015, 1.015); c.translate(-x - w / 2, -y - h / 2); }
      A.panel(c, x, y, w, h, { vines: false });
      // faixa da chapa
      A.rrect(c, x + 18, y + 18, w - 36, 64, 18, S.color, S.dark, 3);
      A.text(c, S.name, x + w / 2, y + 50, 30, '#fff', 'center', { family: FONT_TITLE, weight: 700 }, S.dark, 5);
      // os dois herois num tablado
      A.ell(c, x + w / 2, y + 306, 190, 34, 'rgba(90,50,20,0.16)');
      S.heroes.forEach((k, i) => {
        const H = DATA.HEROES[k];
        A.heroShow(c, H.sprite, x + w / 2 + (i ? 92 : -92), y + 306, t, { flip: i === 1, off: i * 9, scale: 1.55 });
        A.text(c, H.name, x + w / 2 + (i ? 110 : -110), y + 340, 22, SOFT.ink, 'center', { family: FONT_UI, weight: 900 }, false);
        A.text(c, H.title, x + w / 2 + (i ? 110 : -110), y + 363, 14, SOFT.inkSoft, 'center', null, false);
      });
      // quem vem pela estrada
      const E = DATA.ENEMIES;
      const contra = ['raider', 'nomad', 'beetle', 'bulwark'].map(k => E[k][rv].name).join(', ');
      A.text(c, 'VOCÊ ENFRENTA', x + 40, y + 396, 12, S.dark, 'left', null, false);
      A.wrap(c, contra + ' e muito mais. No fim, ' + E.heart[rv].name.split(',')[0] + '.', w - 80, 16, 700).slice(0, 3)
        .forEach((l, j) => A.text(c, l, x + 40, y + 420 + j * 21, 16, SOFT.ink, 'left', { family: FONT_UI, weight: 700 }, false));
      A.btn(c, x + w / 2 - 120, y + h - 78, 240, 58, 'Escolher', { hover: hv, color: sd === 'R' ? 'red' : 'green', size: 24 });
      c.restore();
    }
    const hx = UI.circle('chooseX', 1236, 44, 22, () => { this.choose = false; Snd.play('click'); });
    A.roundBtn(c, 1236, 44, 21, { hover: hx, color: '#ee7d6e' });
    A.text(c, '×', 1236, 42, 30, '#fff', 'center', { family: FONT_UI, weight: 900 });
  },
};

// ------------------------------------------------------------ mapa-mundi
// uma linha curta por fase no painel (a descricao longa fica no data.js)
const LEVEL_TAG = [
  'A turma desceu do ônibus na rodoviária.',
  'Terraços altos entre os blocos iguais.',
  'Votação de madrugada. O vice rival vem junto.',
  'A tempestade de fake news encurta a visão das torres.',
  'A última subida. O candidato rival em pessoa.',
]
const WorldMap = {
  bg: null, bgKey: '', previews: {}, panel: null, mode: 'normal', sel: [], reg: null,
  REGS: ['Brasília'],
  // regiao inicial: a da fase mais adiantada ja liberada
  autoReg() {
    let r = 0;
    DATA.WORLD.forEach((p, i) => { if (this.unlocked(i)) r = p.reg || 0; });
    return r;
  },
  ensureBg() {
    if (this.reg == null) this.reg = this.autoReg();
    const key = App.scale.toFixed(3) + ':' + this.reg;
    if (this.bgKey === key) return;
    const cv = document.createElement('canvas');
    cv.width = Math.ceil(W * App.scale); cv.height = Math.ceil(H * App.scale);
    const c = cv.getContext('2d');
    c.setTransform(App.scale, 0, 0, App.scale, 0, 0);
    this.paint(c);
    this.bg = cv; this.bgKey = key;
  },
  paint(c) {
    if (A.worldSprite && A.worldSprite(c, this.reg)) return; // fundo do mapa-mundi renderizado no Blender (js/sprites.js)
    const r = U.rng(4242);
    c.fillStyle = '#2a170a'; c.fillRect(0, 0, W, H);
    // pergaminho
    const px = 24, py = 18, pw = W - 48, ph = H - 36;
    c.save();
    c.beginPath();
    c.moveTo(px + 10, py);
    for (let x = px + 10; x < px + pw; x += 18) c.lineTo(x, py + (r() - 0.5) * 6);
    for (let y = py; y < py + ph; y += 18) c.lineTo(px + pw + (r() - 0.5) * 6, y);
    for (let x = px + pw; x > px; x -= 18) c.lineTo(x, py + ph + (r() - 0.5) * 6);
    for (let y = py + ph; y > py; y -= 18) c.lineTo(px + (r() - 0.5) * 6, y);
    c.closePath();
    const g = c.createRadialGradient(W / 2, H / 2, 100, W / 2, H / 2, 760);
    g.addColorStop(0, '#f4e2b4'); g.addColorStop(0.7, '#e2c48a'); g.addColorStop(1, '#b8894e');
    c.fillStyle = g; c.fill();
    c.clip();
    for (let i = 0; i < 400; i++) A.ell(c, r() * W, r() * H, 10 + r() * 60, 6 + r() * 30, U.rgba(r() < 0.5 ? '#c49a5a' : '#fff4d0', 0.05 + r() * 0.05));
    // mar a noroeste
    c.beginPath();
    c.moveTo(0, 0); c.lineTo(330, 0);
    c.bezierCurveTo(300, 60, 220, 70, 200, 140);
    c.bezierCurveTo(170, 230, 80, 220, 0, 300);
    c.closePath();
    c.fillStyle = '#8fb7b0'; c.fill();
    c.strokeStyle = '#5a7a70'; c.lineWidth = 2.5; c.stroke();
    for (let i = 0; i < 6; i++) {
      c.beginPath(); c.moveTo(40 + i * 30, 40 + i * 30); c.quadraticCurveTo(60 + i * 30, 30 + i * 30, 80 + i * 30, 40 + i * 30);
      c.strokeStyle = 'rgba(255,255,255,0.5)'; c.lineWidth = 1.5; c.stroke();
    }
    // rio
    c.beginPath();
    c.moveTo(210, 120);
    c.bezierCurveTo(330, 260, 500, 300, 610, 400);
    c.bezierCurveTo(700, 480, 860, 520, 1000, 640);
    c.strokeStyle = '#6a9ab0'; c.lineWidth = 9; c.stroke();
    c.strokeStyle = '#9fd0e0'; c.lineWidth = 4; c.stroke();
    // canais de qanat (fase 7)
    c.lineCap = 'round';
    for (const [x0, y0, x1, y1] of [[1090, 360, 1210, 380], [1100, 430, 1230, 440], [1150, 340, 1150, 470]]) {
      A.line(c, x0, y0, x1, y1, '#6a9ab0', 5); A.line(c, x0, y0, x1, y1, '#9fd0e0', 2);
    }
    for (let i = 0; i < 6; i++) A.rect(c, 1080 + (i % 3) * 52, 448 + Math.floor(i / 3) * 26, 40, 16, 'rgba(110,140,60,0.35)', 'rgba(80,100,40,0.5)', 1);
    // montanhas
    const mountain = (x, y, s, col) => {
      A.poly(c, [[x - 26 * s, y], [x, y - 34 * s], [x + 26 * s, y]], col || '#c9a06a', '#b98d64', 2);
      A.poly(c, [[x, y - 34 * s], [x + 26 * s, y], [x + 6 * s, y]], 'rgba(90,50,20,0.35)', null);
      A.poly(c, [[x - 7 * s, y - 25 * s], [x, y - 34 * s], [x + 7 * s, y - 25 * s], [x, y - 22 * s]], '#f4ead0', null);
    };
    for (const [x, y, s] of [[790, 170, 1.1], [840, 150, 0.9], [940, 180, 1.2], [990, 210, 0.8], [760, 230, 0.8], [700, 320, 0.7], [960, 290, 0.9]]) mountain(x, y, s);
    // redemoinho de areia no passo (fase 6)
    for (let i = 0; i < 3; i++) { c.beginPath(); c.ellipse(900, 300 - i * 9, 22 - i * 5, 6 - i, 0, 0.3, 5.2); c.strokeStyle = 'rgba(140,90,40,0.6)'; c.lineWidth = 1.6; c.stroke(); }
    // vulcao do ifrit (fase 8)
    A.poly(c, [[1050, 220], [1110, 130], [1140, 130], [1200, 220]], '#7a5a4a', '#4a2a1a', 2);
    A.poly(c, [[1110, 130], [1125, 150], [1140, 130]], '#ff7a1a', null);
    for (let i = 0; i < 4; i++) A.circ(c, 1125 + (i - 1.5) * 8, 112 - i * 6, 6 + i * 2, U.rgba('#6a5a5a', 0.35));
    // dunas
    for (let i = 0; i < 40; i++) {
      const x = 300 + r() * 700, y = 260 + r() * 340;
      c.beginPath(); c.moveTo(x - 18, y); c.quadraticCurveTo(x, y - 9, x + 18, y);
      c.strokeStyle = 'rgba(140,90,40,0.55)'; c.lineWidth = 1.8; c.stroke();
    }
    // oasis e palmeiras pequenas
    A.ell(c, 1060, 560, 34, 16, '#7fb8c0', '#4a7a80', 2);
    for (const [x, y] of [[1020, 548], [1100, 552], [1060, 584]]) {
      A.line(c, x, y, x + 2, y - 16, '#7a5230', 2.5);
      for (let k = 0; k < 5; k++) { const a = Math.PI + (k / 4) * Math.PI; A.line(c, x + 2, y - 16, x + 2 + Math.cos(a) * 10, y - 16 + Math.sin(a) * 6 + 4, '#4f8a3c', 2.5); }
    }
    // ruinas e cidadela
    for (let i = 0; i < 4; i++) A.rect(c, 520 + i * 12, 420 - (i % 2) * 8, 7, 18 + (i % 2) * 8, '#c7b28c', '#b98d64', 1.5);
    A.poly(c, [[560, 120], [560, 90], [580, 80], [600, 90], [620, 80], [640, 90], [660, 80], [660, 120]], '#a8916c', '#5a3a1e', 2);
    // rosa dos ventos
    const cx = 170, cy = 470;
    A.circ(c, cx, cy, 44, 'rgba(255,240,200,0.4)', '#b98d64', 2);
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * U.TAU - Math.PI / 2, l = i % 2 ? 26 : 42;
      A.poly(c, [[cx + Math.cos(a) * l, cy + Math.sin(a) * l], [cx + Math.cos(a + 0.25) * 9, cy + Math.sin(a + 0.25) * 9], [cx, cy], [cx + Math.cos(a - 0.25) * 9, cy + Math.sin(a - 0.25) * 9]], i % 2 ? '#c9a06a' : '#8a3a1e', '#4a2a10', 1.2);
    }
    A.text(c, 'N', cx, cy - 56, 16, '#4a2a10', 'center', { family: FONT_HEAD, weight: 700 }, false);
    c.restore();
    // borda escura
    const vg = c.createRadialGradient(W / 2, H / 2, 300, W / 2, H / 2, 800);
    vg.addColorStop(0, 'rgba(60,30,5,0)'); vg.addColorStop(1, 'rgba(60,30,5,0.45)');
    c.fillStyle = vg; c.fillRect(0, 0, W, H);
  },

  preview(i) {
    const key = i + ':' + App.scale.toFixed(3);
    if (this.previews[key]) return this.previews[key];
    const s = 0.36 * App.scale;
    const cv = document.createElement('canvas');
    cv.width = Math.ceil(W * s); cv.height = Math.ceil(H * s);
    const c = cv.getContext('2d');
    c.setTransform(s, 0, 0, s, 0, 0);
    const g = new Game(i, { headless: true });
    A.terrain(c, g);
    for (const sp of g.spots) { if (sp.ruin) A.ruinSpot(c, sp.x, sp.y, false, sp.ruin, 0); else A.spot(c, sp.x, sp.y, false, 0); }
    this.previews[key] = cv;
    return cv;
  },

  unlocked(i) { return i === 0 || Save.data.stars[i - 1] > 0; },

  // ---------------------------------------------------------------- trilhas e heroi no mapa
  // pontos de cada trilha (fase i -> i+1) a cada ~4 px, na curva de sempre
  trailPts(i) {
    this._tr = this._tr || {};
    if (this._tr[i]) return this._tr[i];
    const a = DATA.WORLD[i], b = DATA.WORLD[i + 1];
    const qx = (a.x + b.x) / 2 + 40, qy = (a.y + b.y) / 2 + 30;
    const pts = [[a.x, a.y]];
    let acc = 0, px = a.x, py = a.y;
    for (let k = 1; k <= 240; k++) {
      const s = k / 240, x = (1 - s) * (1 - s) * a.x + 2 * (1 - s) * s * qx + s * s * b.x, y = (1 - s) * (1 - s) * a.y + 2 * (1 - s) * s * qy + s * s * b.y;
      acc += Math.hypot(x - px, y - py); px = x; py = y;
      if (acc >= 4 || k === 240) { pts.push([x, y]); acc = 0; }
    }
    return (this._tr[i] = pts);
  },

  // trilha de terra batida (pegadas alternadas, seixos na borda); o resto, ainda fechado, e trilha tomada pelo mato.
  // k: quanto ja abriu (0..1); a ponta que abre solta poeira e brilho
  trail(c, i, k, t) {
    const pts = this.trailPts(i), n = pts.length;
    const r = U.rng(7000 + i * 31);
    const path = (from, to) => { c.beginPath(); c.moveTo(pts[from][0], pts[from][1]); for (let j = from + 1; j <= to; j++) c.lineTo(pts[j][0], pts[j][1]); };
    const j1 = Math.floor(k * (n - 1));
    c.save();
    c.lineCap = 'round'; c.lineJoin = 'round';
    if (k < 1) {
      path(j1, n - 1);
      c.setLineDash([2, 10]); c.strokeStyle = 'rgba(120,96,64,0.32)'; c.lineWidth = 3.5; c.stroke(); c.setLineDash([]);
      for (let j = j1 + 3; j < n - 3; j += 5) {
        const [x, y] = pts[j], w = 1.1 + ((j * 37) % 5) / 8, sd = (j * 13) % 3 - 1;
        for (const d of [-1, 0, 1]) A.line(c, x + sd * 4 + d * 3, y + 2, x + sd * 4 + d * 4.6 * w, y - 6.5 * w, d ? '#3f6f35' : '#5c8f45', 2);
      }
    }
    if (j1 >= 1) {
      path(0, j1);
      c.translate(0, 2);
      c.strokeStyle = 'rgba(45,28,12,0.28)'; c.lineWidth = 14; c.stroke();
      c.translate(0, -2);
      c.strokeStyle = '#a8743f'; c.lineWidth = 10; c.stroke();
      c.strokeStyle = 'rgba(222,178,118,0.75)'; c.lineWidth = 4.5; c.stroke();
      for (let j = 2; j < j1 - 1; j += 4) {
        const ang = Math.atan2(pts[j + 1][1] - pts[j - 1][1], pts[j + 1][0] - pts[j - 1][0]), sd = (j / 4) % 2 ? 1 : -1;
        c.save();
        c.translate(pts[j][0] - Math.sin(ang) * 2.2 * sd, pts[j][1] + Math.cos(ang) * 2.2 * sd);
        c.rotate(ang);
        A.ell(c, 0, 0, 2.6, 1.5, 'rgba(98,60,30,0.55)');
        c.restore();
      }
      for (let j = 3; j < j1; j += 5) {
        const sd = r() < 0.5 ? -1 : 1, off = 6.5 + r() * 2, rx = 1.8 + r(), ry = 1.3 + r() * 0.6, cor = r() < 0.5 ? '#efe2c4' : '#bdb1a0';
        const ang = Math.atan2(pts[j][1] - pts[j - 1][1], pts[j][0] - pts[j - 1][0]);
        A.ell(c, pts[j][0] - Math.sin(ang) * off * sd, pts[j][1] + Math.cos(ang) * off * sd, rx, ry, cor);
      }
      if (k < 1) {
        const [hx, hy] = pts[j1];
        A.glow(c, hx, hy, 24, '#ffe7a0', 0.65);
        for (let q = 0; q < 5; q++) A.circ(c, hx + Math.sin(t * 9 + q * 1.7) * 9, hy - 3 - ((t * 30 + q * 7) % 14), 2.2, 'rgba(225,190,140,0.55)');
      }
    }
    c.restore();
  },

  // heroi escolhido em pe no mapa, ao lado da fase mais adiantada da regiao (M = this.mh serve de unidade para o
  // A.drawUnit: espera parada, andar nas 8 direcoes pela trilha)
  heroHome() {
    let h = -1;
    DATA.WORLD.forEach((p, i) => { if ((p.reg || 0) === this.reg && this.unlocked(i) && !(this.reveal && this.reveal.nodes.includes(i))) h = i; });
    return h;
  },
  heroSpot(i) { const p = DATA.WORLD[i]; return [p.x - 48, p.y + 4]; },
  ensureHero() {
    if (this.mh && this.mh.reg === this.reg) return;
    const h = this.heroHome();
    if (h < 0) { this.mh = null; return; }
    const [x, y] = this.heroSpot(h);
    this.mh = { kind: 'hero', node: h, reg: this.reg, x, y, path: null, walk: 0, hdx: 0, hdy: 1, moving: false, facing: 1, stepT: 0 };
  },
  // clicou numa fase: o heroi anda pela trilha ate ela e o painel abre na chegada; clicar de novo durante a
  // caminhada pula para o fim
  goTo(i, open = true) {
    const M = this.mh;
    if (M && M.path) {
      const end = M.path[M.path.length - 1];
      M.x = end[0]; M.y = end[1]; M.path = null; M.then = null; M.moving = false;
    }
    if (!M || M.node === i || (DATA.WORLD[i].reg || 0) !== M.reg) { if (open) this.openPanel(i); return; }
    const pts = [[M.x, M.y]];
    const dir = i > M.node ? 1 : -1;
    for (let n = M.node; n !== i; n += dir) {
      const seg = this.trailPts(dir > 0 ? n : n - 1);
      pts.push(...(dir > 0 ? seg : seg.slice().reverse()));
    }
    pts.push(this.heroSpot(i));
    const cum = [0];
    for (let k = 1; k < pts.length; k++) cum.push(cum[k - 1] + Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]));
    const len = cum[cum.length - 1];
    Object.assign(M, { path: pts, cum, k: 1, d: 0, len, speed: Math.max(260, len / 1.1), node: i, then: open ? () => this.openPanel(i) : null });
  },
  updateHero(dt) {
    const M = this.mh;
    if (!M) return;
    if (!M.path) { M.moving = false; return; }
    M.d += M.speed * dt;
    if (M.d >= M.len) {
      const end = M.path[M.path.length - 1];
      M.x = end[0]; M.y = end[1]; M.path = null; M.moving = false;
      M.facing = 1;
      const fn = M.then; M.then = null;
      if (fn) fn();
      return;
    }
    while (M.k < M.path.length - 1 && M.cum[M.k] < M.d) M.k++;
    const a = M.path[M.k - 1], b = M.path[M.k], s = (M.d - M.cum[M.k - 1]) / Math.max(1e-6, M.cum[M.k] - M.cum[M.k - 1]);
    const nx = a[0] + (b[0] - a[0]) * s, ny = a[1] + (b[1] - a[1]) * s;
    const dx = nx - M.x, dy = ny - M.y, dl = Math.hypot(dx, dy);
    if (dl > 0.01) {
      M.hdx = dx / dl; M.hdy = dy / dl;
      if (Math.abs(dx) > 0.3 * dl) M.facing = dx >= 0 ? 1 : -1;
    }
    M.x = nx; M.y = ny; M.moving = true; M.walk += dt * 16;
    M.stepT -= dt;
    if (M.stepT <= 0) { M.stepT = 0.28; Snd.play('mapStep', 0.5); }
  },
  drawHero(c, t) {
    const M = this.mh;
    if (!M) return;
    M.sk = DATA.HEROES[Save.data.hero].sprite;
    A.clock = t;
    c.save();
    c.translate(M.x, M.y); c.scale(1.6, 1.6); c.translate(-M.x, -M.y);
    A.drawUnit(c, M, t);
    c.restore();
    if (!M.path) {
      const hv = UI.circle('mhero', M.x, M.y - 26, 22, () => { App.go('heroes'); Snd.play('open'); });
      if (hv) UI.setTip(M.x, M.y - 52, DATA.HEROES[Save.data.hero].name, ['Clique para trocar de herói e escolher os talentos.']);
    }
  },

  draw(c, dt) {
    this.ensureBg();
    c.drawImage(this.bg, 0, 0, W, H);
    const t = App.time;
    // cartucho do titulo
    // placa e contador mais altos e finos: nao cobrem os muros da cidadela no fundo do mapa
    A.darkPanel(c, 480, 10, 320, 44, 16);
    A.text(c, this.REGS[this.reg], W / 2, 33, 24, '#ffe08a', 'center', { family: FONT_TITLE, weight: 700 });
    // troca de regiao: seta para a outra (a 2 libera ao vencer a ultima fase da 1)
    const first2 = DATA.WORLD.findIndex(p => p.reg === 1);
    if (first2 > 0) {
      const toR = this.reg === 0 ? 1 : 0, ax = this.reg === 0 ? 1232 : 48, ok = toR === 0 || this.unlocked(first2);
      const hva = UI.circle('reg', ax, 340, 28, () => {
        if (!ok) { Snd.play('error'); return; }
        this.reg = toR; this.bgKey = ''; this.panel = null; Snd.play('open');
      });
      if (ok && toR === 1 && !Save.data.stars[first2]) A.glow(c, ax, 340, 52, '#ffe08a', 0.35 + Math.sin(App.time * 4) * 0.15);
      A.roundBtn(c, ax, 340, 27, { hover: hva, color: ok ? '#5fbfb0' : '#b9ac9c' });
      A.text(c, toR === 1 ? '›' : '‹', ax + (toR === 1 ? 2 : -2), 336, 34, '#fff', 'center', { family: FONT_HEAD, weight: 700 });
      if (!ok) A.lock(c, ax, 372, 9);
      if (hva) UI.setTip(ax, 340, this.REGS[toR], ok ? ['Ir para esta região do mapa.'] : [`Vença a fase ${first2} para liberar.`]);
    }
    // trilhas: terra batida com pegadas e seixos; trancada = tomada pelo mato. Trilha nova abre pegada por pegada
    // (Save.data.trilhas guarda as ja mostradas), a bandeira da fase cai no fim e o heroi vai ate la
    const P = DATA.WORLD;
    const segOk = i => (P[i].reg || 0) === this.reg && (P[i + 1].reg || 0) === this.reg;
    const segs = P.slice(1).map((_, i) => i);
    if (!Save.data.trilhas) { Save.data.trilhas = segs.filter(i => this.unlocked(i + 1)); Save.write(); }
    if (!this.reveal) {
      const novas = segs.filter(i => segOk(i) && this.unlocked(i + 1) && !Save.data.trilhas.includes(i));
      if (novas.length) { this.reveal = { t0: t, segs: novas, nodes: novas.map(i => i + 1), boom: false }; Snd.play('trailOpen'); }
    }
    const R = this.reveal, rt = R ? t - R.t0 : 0;
    if (R && rt >= 1.4 && !R.boom) { R.boom = true; Snd.play('flagDrop'); }
    if (R && rt >= 2.1) {
      for (const i of R.segs) if (!Save.data.trilhas.includes(i)) Save.data.trilhas.push(i);
      Save.write();
      this.reveal = null;
      const M = this.mh;
      if (M && !M.path && R.segs.includes(M.node)) this.goTo(M.node + 1, false);
    }
    for (const i of segs) {
      if (!segOk(i)) continue;
      const k = R && R.segs.includes(i) ? Math.min(1, rt / 1.4) : this.unlocked(i + 1) ? 1 : 0;
      this.trail(c, i, k, t);
    }
    this.ensureHero();
    this.updateHero(dt || 0);
    // nos
    P.forEach((p, i) => {
      if ((p.reg || 0) !== this.reg) return;
      const L = DATA.LEVELS[i];
      // fase recem-liberada: a bandeira fica trancada enquanto a trilha abre e depois cai quicando
      const drop = R && R.nodes.includes(i);
      const dk = drop ? (rt - 1.4) / 0.6 : 1;
      const open = this.unlocked(i) && dk >= 0;
      const st = Save.data.stars[i];
      const next = open && st === 0;
      const hv = open && !drop ? UI.circle('lvl' + i, p.x, p.y - 10, 34, () => this.goTo(i)) : false;
      const bob = next && !drop ? Math.sin(t * 4) * 4 : 0;
      const fall = dk >= 0 && dk < 1 ? -70 * (1 - U.bounce(dk)) : 0;
      A.shadow(c, p.x, p.y + 6, 26 * (1 + fall / 140), 9);
      if (next) A.glow(c, p.x, p.y - 14, 60, '#ffe08a', 0.4 + Math.sin(t * 4) * 0.15);
      if (drop && dk >= 0.25 && dk < 1) A.glow(c, p.x, p.y, 40 + 60 * dk, '#fff2b0', 0.7 * (1 - dk));
      // bandeira-escudo
      c.save();
      c.translate(p.x, p.y - 14 + bob + fall - (hv ? 3 : 0));
      const col = !open ? '#8a8072' : st ? '#1f8f8a' : '#c0392b';
      A.line(c, 0, 20, 0, -42, '#4a2a10', 3.5);
      A.poly(c, [[-24, -30], [24, -30], [24, -4], [0, 14], [-24, -4]], A.hgrad(c, -24, 24, col, 0.3, -0.2), U.shade(col[0] === '#' ? col : '#b9ac9c', -0.28), 2);
      A.poly(c, [[-18, -25], [18, -25], [18, -6], [0, 8], [-18, -6]], null, 'rgba(255,240,200,0.6)', 1.5);
      if (open) A.text(c, String(i + 1), 0, -11, 24, '#fff', 'center', { family: FONT_HEAD, weight: 700 });
      else A.lock(c, 0, -12, 10);
      c.restore();
      if (open) {
        for (let s = 0; s < 3; s++) A.star(c, p.x - 22 + s * 22, p.y + 22, 9, s < st ? '#ffd54a' : '#5a4a3a');
        if (Save.data.chal[i]) A.star(c, p.x + 40, p.y + 22, 8, '#7fffd4');
      }
      if (hv) {
        A.darkPanel(c, p.x - 120, p.y - 96, 240, 34, 12);
        A.text(c, L.name, p.x, p.y - 79, 16, '#ffe08a', 'center');
      }
    });
    this.drawHero(c, t);
    // heroi escolhido (clique: tela de herois)
    const hid = Save.data.hero, HD = DATA.HEROES[hid], hxp = Save.heroXpOf(hid);
    const lvl = new Game(0, { headless: true }).heroLevelFor(hxp);
    const hvh = UI.rect('mapHero', 40, 610, 270, 76, () => { App.go('heroes'); Snd.play('open'); });
    A.darkPanel(c, 40, 610, 270, 76, 14);
    if (hvh) A.rrect(c, 40, 610, 270, 76, 14, null, '#ffe08a', 2);
    A.heroFace(c, 82, 648, 28, hid);
    A.text(c, `${HD.name} · Nível ${lvl}`, 120, 634, 17, '#ffe08a', 'left');
    const nx = DATA.HERO_XP[lvl] || null;
    const pv = DATA.HERO_XP[lvl - 1] || 0;
    Render.bar(c, 120, 652, 170, 8, nx ? (hxp - pv) / (nx - pv) : 1, '#2a1a10', '#5ad9c4');
    A.text(c, nx ? `XP ${Math.floor(hxp)}/${nx}` : 'Nível máximo', 120, 672, 11, '#e8dcc4', 'left', null, false);
    const novos = DATA.HERO_ORDER.filter(k => Save.heroUnlocked(k) && !Save.data.heroesSeen.includes(k));
    if (novos.length) {
      if (!this.heroSnd) { this.heroSnd = true; Snd.play('heroNew'); }
      A.glow(c, 300, 614, 26, '#e6ff7a', 0.5 + Math.sin(App.time * 5) * 0.2);
      UKB.chip(c, 214, 598, 'Novo herói!', { color: '#6aa84f' });
    }
    if (hvh) UI.setTip(175, 610, 'Heróis', ['Escolha quem vai para a batalha e os talentos de cada herói.']);
    // chapa da vez: clique para trocar
    const SD = DATA.SIDES[DATA.SIDE];
    const hch = UI.rect('chapa', 244, 10, 214, 44, () => { App.go('title'); Title.choose = true; });
    A.darkPanel(c, 244, 10, 214, 44, 16);
    A.circ(c, 270, 32, 10, SD.color, '#fff', 2);
    A.text(c, SD.name, 288, 33, 16, hch ? '#ffe08a' : '#fff', 'left', { family: FONT_UI, weight: 900 });
    if (hch) UI.setTip(351, 54, 'Trocar de chapa', ['A outra chapa vira a turma adversária. As estrelas continuam suas.']);
    // estrelas
    A.darkPanel(c, 40, 10, 190, 44, 16);
    A.star(c, 72, 32, 14);
    A.text(c, `${Save.totalStars()}/${Save.maxStars()}`, 92, 33, 21, '#fff', 'left');
    // botoes
    const free = Save.freeStars();
    let hv = UI.rect('upg', 700, 622, 210, 60, () => { App.go('upgrades'); });
    A.btn(c, 700, 622, 210, 60, 'Melhorias', { hover: hv, color: 'teal', size: 22 });
    if (free > 0) {
      A.circ(c, 902, 626, 16, '#ee8676', '#ffffff', 2);
      A.text(c, String(free), 902, 627, 15, '#fff', 'center');
    }
    hv = UI.rect('best', 926, 622, 180, 60, () => { App.go('bestiary'); });
    A.btn(c, 926, 622, 180, 60, 'Bestiário', { hover: hv, color: 'gold', size: 22 });
    hv = UI.rect('menu', 1122, 622, 118, 60, () => { App.go('title'); });
    A.btn(c, 1122, 622, 118, 60, 'Menu', { hover: hv, color: 'grey', size: 20 });
    // Correnteza (ondas sem fim): libera ao vencer a ultima fase da primeira regiao
    const E = DATA.ENDLESS, eOpen = Save.data.stars[E.unlock] > 0;
    hv = UI.rect('endless', 494, 622, 194, 60, () => {
      if (!eOpen) { Snd.play('error'); return; }
      Snd.play('mode_endless');
      App.startLevel(E.level, 'endless');
    });
    A.btn(c, 494, 622, 194, 60, E.name, { hover: hv, color: eOpen ? 'blue' : 'grey', size: 20 });
    if (!eOpen) A.lock(c, 672, 630, 9);
    else if (Save.data.endless) UKB.chip(c, 530, 676, `recorde: onda ${Save.data.endless}`, { color: '#2f9a9a' });
    if (hv) UI.setTip(591, 622, E.name, eOpen ? [E.desc] : [E.desc, `Vença a fase ${E.unlock + 1} para liberar.`]);
    // som e musica na barra de baixo (o vulcao fica livre no canto)
    soundToggles(c, 362, 652);

    if (this.panel != null) this.levelPanel(c, this.panel);
  },

  openPanel(i) {
    this.panel = i;
    this.mode = 'normal';
    this.sel = App.loadoutFor(i, 'normal');
    Snd.play('open');
  },

  setMode(i, mode) {
    this.mode = mode;
    this.sel = App.loadoutFor(i, mode);
    Snd.play('mode_' + mode);
  },

  // inimigos da fase na ordem em que aparecem
  levelEnemies(i) {
    const out = [];
    for (const w of DATA.LEVELS[i].waves) for (const g of w) {
      if (!out.includes(g[0])) out.push(g[0]);
      const E = DATA.ENEMIES[g[0]];
      if (E.split && !out.includes(E.split.type)) out.push(E.split.type);
    }
    return out;
  },

  levelPanel(c, i) {
    const L = DATA.LEVELS[i];
    UI.rect('lpBlock', 0, 0, W, H, () => { this.panel = null; }, 'default');
    c.fillStyle = 'rgba(20,10,0,0.55)'; c.fillRect(0, 0, W, H);
    const x = 140, y = 40, w = 1000, h = 640;
    UI.rect('lpBody', x, y, w, h, () => {}, 'default');
    A.panel(c, x, y, w, h);
    A.text(c, L.name, x + 260, y + 44, 32, SOFT.title, 'center', { family: FONT_TITLE, weight: 700 }, 'rgba(255,255,255,0.9)', 5);
    // previa e descricao
    const pv = this.preview(i);
    const pw = 440, ph = 248, px = x + 36, py = y + 78;
    A.softShadow(c, px - 5, py - 5, pw + 10, ph + 10, 14, 12, 0.22, 4, SOFT.card1);
    A.rrect(c, px - 5, py - 5, pw + 10, ph + 10, 14, null, SOFT.line, 2);
    c.drawImage(pv, px, py, pw, ph);
    A.text(c, LEVEL_TAG[i] || UKB.fit(c, L.desc, pw, 16, 700), px, py + ph + 28, 16, SOFT.ink, 'left', { family: FONT_UI, weight: 700 }, false);
    // numeros da fase em chips
    const ent = L.paths.length - (L.forks ? L.forks.length : 0);
    let chx = px;
    for (const [t, ic, col] of [[`${L.waves.length} ondas`, 'time', '#8a98d8'], [`Verba inicial ${L.gold}`, 'gold', '#e9b84a'],
      [`${L.lives || 20} votos`, 'lives', '#ec8a76'], [ent > 1 ? `${ent} entradas` : '1 entrada', 'range', '#62bfb2']]) {
      chx += UKB.chip(c, chx, py + ph + 62, t, { icon: ic, color: col }) + 6;
    }
    let fy = py + ph + 106;
    // caracteristicas do mapa
    const feats = [];
    const sp = L.spots;
    if (sp.some(s => s[2] === 'h')) feats.push(['high', 'Terreno elevado', '+15% de alcance']);
    if (sp.some(s => s[2] === 'r')) feats.push(['ruin', 'Obras paradas', 'pague para liberar lotes']);
    if (L.forks) feats.push(['gate', 'Manobra regimental', 'desvie a turma adversária']);
    if (L.storm) feats.push(['sandstorm', 'Fake news', '-25% de alcance periódico']);
    feats.forEach(([ic, t1, t2], k) => {
      const fx = px + (k % 2) * 224, yy = fy + Math.floor(k / 2) * 44;
      A.circ(c, fx + 18, yy + 4, 18, SOFT.card2, SOFT.line, 1.5);
      A.icon(c, ic, fx + 18, yy + 4, 14, { time: App.time });
      A.text(c, t1, fx + 44, yy - 5, 15, SOFT.ink, 'left', { family: FONT_UI, weight: 900 }, false);
      A.text(c, t2, fx + 44, yy + 14, 13, SOFT.inkSoft, 'left', null, false);
    });

    // coluna da direita
    const rx = x + 520, rw = 444;
    // modo: campanha / desafio (vencer 1 vez) / heroico e ferro (3 estrelas na campanha)
    const chOpen = Save.data.stars[i] > 0, hrOpen = Save.data.stars[i] >= 3;
    const tw = (rw - 24) / 4;
    const tab = (key, label, tx, active, enabled, cb) => {
      const hv = UI.rect(key, tx, y + 26, tw, 42, enabled ? cb : () => Snd.play('error'));
      const bg = active ? '#e8997a' : enabled ? (hv ? '#fbe3c8' : SOFT.card2) : '#e6ddd0';
      A.softShadow(c, tx, y + 26, tw, 42, 21, active ? 12 : 6, active ? 0.28 : 0.15, active ? 4 : 2, bg);
      A.rrect(c, tx, y + 26, tw, 42, 21, null, active ? U.shade('#e8997a', -0.2) : SOFT.line, 1.5);
      A.text(c, label, tx + tw / 2, y + 47, 15, active ? '#ffffff' : enabled ? SOFT.ink : '#b3a597', 'center', null, active ? U.shade('#e8997a', -0.4) : false, 3);
      return hv;
    };
    const MODES = [
      ['normal', 'Campanha', true, null, null],
      ['chal', 'Desafio', chOpen, Save.data.chal[i], ['Desafio bloqueado', 'Vença a fase uma vez para liberar o desafio.']],
      ['heroic', 'Heroico', hrOpen, Save.data.heroic[i], ['Heroico bloqueado', 'Faça 3 estrelas na campanha desta fase.']],
      ['iron', 'Ferro', hrOpen, Save.data.iron[i], ['Ferro bloqueado', 'Faça 3 estrelas na campanha desta fase.']],
    ];
    MODES.forEach(([m, label, en, done, lockTip], k) => {
      const tx = rx + k * (tw + 8);
      if (tab('m' + m, label, tx, this.mode === m, en, () => this.setMode(i, m)) && !en) UI.setTip(tx + tw / 2, y + 47, lockTip[0], [lockTip[1]]);
      if (!en) A.lock(c, tx + tw - 14, y + 30, 8);
      else if (done) A.star(c, tx + tw - 12, y + 30, 8, m === 'chal' ? '#7fffd4' : m === 'heroic' ? '#ff9a5a' : '#c9d2e0');
    });
    let ry = y + 92;
    if (this.mode === 'normal') {
      for (let s = 0; s < 3; s++) A.star(c, rx + 20 + s * 34, ry + 14, 14, s < Save.data.stars[i] ? '#ffd54a' : '#5a4a3a');
      A.text(c, Save.data.stars[i] ? 'Melhor resultado' : 'Ainda não vencida', rx + 124, ry + 15, 15, SOFT.inkSoft, 'left', null, false);
    } else {
      const info = {
        chal: [L.challenge.name, L.challenge.desc, '#7fffd4', Save.data.chal[i]],
        heroic: ['Heroico', '1 vida, ondas maiores e mais fortes', '#ff9a5a', Save.data.heroic[i]],
        iron: ['Ferro', `1 vida, onda única, só ${App.rulesFor(i, 'iron').only.length} torres`, '#c9d2e0', Save.data.iron[i]],
      }[this.mode];
      A.star(c, rx + 20, ry + 14, 14, info[3] ? info[2] : '#5a4a3a');
      A.text(c, UKB.fit(c, `${info[0]}: ${info[1]}`, rw - 50, 15, 900), rx + 44, ry + 7, 15, '#2f7f70', 'left', { family: FONT_UI, weight: 900 }, false);
      A.text(c, info[3] ? 'Concluído' : 'Vale 1 estrela extra', rx + 44, ry + 26, 13, SOFT.inkSoft, 'left', null, false);
    }
    // inimigos
    ry += 46;
    A.text(c, 'Inimigos desta fase', rx, ry, 17, SOFT.ink, 'left', { family: FONT_UI, weight: 900 }, false);
    const seen = new Set(Save.data.seen);
    const ens = this.levelEnemies(i);
    ens.forEach((type, k) => {
      const ex = rx + 22 + (k % 10) * 44, ey = ry + 34 + Math.floor(k / 10) * 46;
      const known = seen.has(type);
      const hv = UI.circle('le' + type, ex, ey, 19, null, 'default');
      A.circ(c, ex, ey, 19, known ? SOFT.card2 : '#ece2d2', DATA.ENEMIES[type].boss ? '#ec8a76' : SOFT.line, 1.8);
      if (known) A.icon(c, type, ex, ey, 17, { time: App.time });
      else { c.drawImage(silhouette(type), ex - 21, ey - 21, 42, 42); A.text(c, '?', ex, ey + 1, 18, '#5a3a1e', 'center', null, false); }
      if (hv) {
        const E = DATA.ENEMIES[type];
        UI.setTip(ex, ey, known ? shortName(E.name) : 'Adversário desconhecido', known ? [E.desc, 'Dica: ' + E.tip] : ['Você ainda não enfrentou este adversário.']);
      }
    });
    ry += 34 + Math.ceil(ens.length / 10) * 46;
    // arsenal
    this.arsenal(c, i, rx, ry, rw);

    const hv = UI.rect('go', rx + rw / 2 - 130, y + h - 82, 260, 60, () => {
      if (!this.sel.length) { Snd.play('error'); return; }
      if (this.mode === 'normal') { Save.data.loadout = this.sel.slice(); Save.write(); }
      const sel = this.sel.slice(), mode = this.mode;
      this.panel = null;
      App.startLevel(i, mode, sel);
    });
    A.btn(c, rx + rw / 2 - 130, y + h - 82, 260, 60, { chal: 'Encarar o desafio!', heroic: 'Batalha heroica!', iron: 'Encarar o ferro!' }[this.mode] || 'Batalhar!', { hover: hv, color: 'red', size: 24, font: { family: FONT_HEAD, weight: 700 } });
    const cx = UI.circle('lpClose', x + w - 22, y + 22, 18, () => { this.panel = null; Snd.play('click'); });
    A.roundBtn(c, x + w - 22, y + 22, 17, { hover: cx, color: '#ee8676' });
    A.text(c, '×', x + w - 22, y + 20, 24, '#fff', 'center');
  },

  arsenal(c, i, rx, ry, rw) {
    const L = DATA.LEVELS[i];
    const rules = App.rulesFor(i, this.mode);
    const slots = App.slotsFor(i, this.mode);
    const unlocked = Save.unlockedTowers();
    const allowed = t => unlocked.includes(t) && (!rules.only || rules.only.includes(t)) && !(rules.ban && rules.ban.includes(t));
    const usable = DATA.TOWER_ORDER.filter(allowed);
    const choose = usable.length > slots;
    // posicao das cartas (o teste ponta a ponta le daqui)
    this._ars = { rx, ry };
    A.text(c, 'Arsenal', rx, ry, 17, SOFT.ink, 'left', { family: FONT_UI, weight: 900 }, false);
    UKB.chip(c, rx + 74, ry, `${this.sel.length} de ${Math.min(slots, usable.length)}`, { color: '#5fbfb0' });
    A.text(c, choose ? 'Escolha as torres desta batalha' : 'Todas as torres liberadas entram', rx + rw, ry + 1, 13, SOFT.inkSoft, 'right', null, false);
    DATA.TOWER_ORDER.forEach((type, k) => {
      const tx = rx + 4 + (k % 4) * 110, ty = ry + 18 + Math.floor(k / 4) * 92;
      const D = DATA.TOWERS[type];
      const isUnl = unlocked.includes(type);
      const ok = allowed(type);
      const on = this.sel.includes(type);
      const hv = UI.rect('ar' + type, tx, ty, 100, 84, () => {
        if (!ok || !choose) { Snd.play('error'); return; }
        if (on) this.sel = this.sel.filter(x => x !== type);
        else if (this.sel.length < slots) this.sel = DATA.TOWER_ORDER.filter(x => x === type || this.sel.includes(x));
        else { Snd.play('error'); return; }
        Snd.play('click');
      });
      A.rrect(c, tx, ty, 100, 84, 14, on ? '#eefaf5' : ok ? (hv ? '#fff6e6' : '#f6ead2') : '#e6ddd0', on ? '#5fbfb0' : SOFT.line, on ? 3 : 1.6);
      if (isUnl) {
        c.save();
        if (!ok) c.globalAlpha = 0.4;
        A.icon(c, type, tx + 50, ty + 34, 26, { tier: 1, time: on ? App.time : 0 });
        c.restore();
        A.text(c, D.short, tx + 50, ty + 72, 13, ok ? SOFT.ink : '#a89a86', 'center', null, false);
        if (on) A.circ(c, tx + 88, ty + 12, 8, '#5fbfb0', '#ffffff', 1.5);
        if (on) A.poly(c, [[tx + 84, ty + 12], [tx + 87, ty + 15], [tx + 92, ty + 9]], null, '#fff', 2);
        if (!ok) UKB.chip(c, tx + 14, ty + 40, 'proibida', { color: '#ec8a76' });
      } else {
        A.lock(c, tx + 50, ty + 34, 14);
        const from = DATA.LEVELS.findIndex(Lv => [].concat(Lv.unlock || []).includes(type));
        A.text(c, from >= 0 ? `Fase ${from + 1}` : '', tx + 50, ty + 70, 13, SOFT.inkSoft, 'center', null, false);
      }
      if (hv && isUnl) UI.setTip(tx + 50, ty + 40, D.name, [D.desc, ...towerLines(App.dummyGame(), type, 1)]);
    });
  },
};

// ------------------------------------------------------------ melhorias
const Upgrades = {
  draw(c) {
    WorldMap.ensureBg();
    c.drawImage(WorldMap.bg, 0, 0, W, H);
    c.fillStyle = 'rgba(20,10,0,0.5)'; c.fillRect(0, 0, W, H);
    UI.blocker();
    const x = 40, y = 26, w = 1200, h = 668;
    A.panel(c, x, y, w, h);
    A.text(c, 'Melhorias', W / 2, y + 44, 38, SOFT.title, 'center', { family: FONT_TITLE, weight: 700 }, 'rgba(255,255,255,0.9)', 5);
    const free = Save.freeStars();
    // cabecalho: estrelas livres e custo dos niveis em chips
    c.font = `800 13px ${FONT_UI}`;
    const t1 = `${free} estrela${free === 1 ? '' : 's'} para gastar`, t2 = 'Níveis custam 1, 2 e 2';
    const cw = c.measureText(t1).width + 36 + c.measureText(t2).width + 22 + 8;
    let chx = W / 2 - cw / 2;
    chx += UKB.chip(c, chx, y + 86, t1, { icon: 'star', color: '#e9b84a' }) + 8;
    UKB.chip(c, chx, y + 86, t2, { color: '#b9ac9c' });
    const cats = Object.keys(DATA.UPGRADES);
    const up = Save.data.up;
    const unl = Save.unlockedTowers();
    const step = Math.min(168, (w - 100) / cats.length);
    cats.forEach((cat, ci) => {
      const cx = x + 50 + step / 2 + ci * step;
      const D = DATA.UPGRADES[cat];
      const locked = (cat === 'eng' && !unl.includes('cistern') && !unl.includes('windmill')) || (cat === 'cmd' && !unl.includes('banner') && !unl.includes('market')) || (DATA.TOWERS[cat] && !unl.includes(cat));
      A.circ(c, cx, y + 142, 32, SOFT.card1, SOFT.line, 2.5);
      c.save(); if (locked) c.globalAlpha = 0.45;
      A.icon(c, D.icon, cx, y + 142, cat === 'spells' ? 22 : 26, { tier: 3, time: App.time });
      c.restore();
      A.text(c, D.name, cx, y + 188, 17, locked ? '#b3a597' : SOFT.ink, 'center', { family: FONT_UI, weight: 900 }, false);
      D.list.forEach((u, k) => {
        const ny = y + 248 + k * 128;
        const cost = DATA.UPGRADE_COST[k];
        const bought = up[cat] > k;
        const avail = up[cat] === k && free >= cost;
        const bw = Math.min(156, step - 10), bx = cx - bw / 2, bt = ny - 44, bh = 112;
        if (k > 0) A.poly(c, [[cx - 7, bt - 12], [cx + 7, bt - 12], [cx, bt - 4]], bought ? '#5fbfb0' : '#d8c6ae', null);
        const hv = UI.rect('u' + cat + k, bx, bt, bw, bh, () => {
          if (avail) { up[cat]++; Save.write(); Snd.play('upgrade'); } else Snd.play('error');
        });
        if (avail) A.glow(c, cx, ny + 12, 92, '#ffe08a', 0.22 + Math.sin(App.time * 4) * 0.08);
        const bg = bought ? '#eefaf5' : avail ? (hv ? '#fffdf6' : '#fffaf1') : '#f1e8da';
        A.softShadow(c, bx, bt - (hv && avail ? 2 : 0), bw, bh, 16, hv && avail ? 14 : 8, 0.2, 3, bg);
        A.rrect(c, bx, bt - (hv && avail ? 2 : 0), bw, bh, 16, null, bought ? '#5fbfb0' : avail ? '#e9b84a' : SOFT.line, bought || avail ? 2.2 : 1.5);
        const oy = bt - (hv && avail ? 2 : 0);
        c.save();
        if (!bought && !avail) c.globalAlpha = 0.62;
        // nivel e preco
        A.circ(c, bx + 22, oy + 22, 13, bought ? '#5fbfb0' : SOFT.card2, bought ? '#ffffff' : SOFT.line, 1.5);
        A.text(c, ['I', 'II', 'III'][k], bx + 22, oy + 22.5, 13, bought ? '#ffffff' : SOFT.ink, 'center', null, false);
        if (bought) UKB.chip(c, bx + bw - 86, oy + 22, 'Comprada', { color: '#5fbfb0' });
        else {
          A.rrect(c, bx + bw - 58, oy + 10, 46, 24, 12, '#fff3d6', '#e9bd6a', 1.5);
          A.star(c, bx + bw - 44, oy + 22, 8, '#ffd54a');
          A.text(c, String(cost), bx + bw - 26, oy + 22.5, 14, '#9a6420', 'center', null, false);
        }
        // nome e efeito
        const nf = bw < 150 ? 13 : 14, df = bw < 150 ? 12 : 13;
        A.text(c, UKB.fit(c, u.name, bw - 10, nf, 900), cx, oy + 52, nf, SOFT.ink, 'center', { family: FONT_UI, weight: 900 }, false);
        const eff = A.wrap(c, u.desc.replace(/\.$/, ''), bw - 16, df, 700).slice(0, 2);
        eff.forEach((l, j) => A.text(c, l, cx, oy + 76 + j * 16, df, bought ? '#3f8f70' : SOFT.inkSoft, 'center', { family: FONT_UI, weight: 700 }, false));
        c.restore();
      });
      if (locked) UKB.chip(c, cx - 52, y + 212, 'bloqueada', { color: '#ec8a76' });
    });
    let hv = UI.rect('reset', x + 40, y + h - 70, 200, 50, () => {
      for (const k in up) up[k] = 0;
      Save.write(); Snd.play('sell');
    });
    A.btn(c, x + 40, y + h - 70, 200, 50, 'Restaurar', { hover: hv, color: 'red', size: 20 });
    if (hv) UI.setTip(x + 140, y + h - 70, 'Restaurar', ['Devolve todas as estrelas para redistribuir de outro jeito.']);
    hv = UI.rect('done', x + w - 240, y + h - 70, 200, 50, () => App.go('map'));
    A.btn(c, x + w - 240, y + h - 70, 200, 50, 'Pronto', { hover: hv, color: 'green', size: 22 });
  },
};

// ------------------------------------------------------------ herois
// escolhe o heroi da proxima batalha e os talentos (1 de 2 nos niveis 3, 6 e 9; pode trocar quando quiser)
// total de ondas para mostrar (a Correnteza nao tem fim)
const wavesTxt = g => (g.totalWaves === Infinity ? '∞' : g.totalWaves);

const Heroes = {
  view: null,
  chegaAt: 0,
  shown: null,
  draw(c) {
    WorldMap.ensureBg();
    c.drawImage(WorldMap.bg, 0, 0, W, H);
    c.fillStyle = 'rgba(20,10,0,0.5)'; c.fillRect(0, 0, W, H);
    UI.blocker();
    const x = 40, y = 26, w = 1200, h = 668;
    A.panel(c, x, y, w, h);
    A.text(c, 'Heróis', W / 2, y + 44, 38, SOFT.title, 'center', { family: FONT_TITLE, weight: 700 }, 'rgba(255,255,255,0.9)', 5);
    if (!this.view || !DATA.HEROES[this.view]) this.view = Save.data.hero;
    for (const k of DATA.HERO_ORDER) if (Save.heroUnlocked(k) && !Save.data.heroesSeen.includes(k)) { Save.data.heroesSeen.push(k); Save.write(); }
    const game = new Game(0, { headless: true });
    const id = this.view, Hd = DATA.HEROES[id], open = Save.heroUnlocked(id);
    // o heroi em vista entra com a pose de chegada (ao abrir a tela e a cada troca)
    if (this.shown !== id) { this.shown = id; this.chegaAt = App.time; }
    this.stage(c, id, open, App.time - this.chegaAt);
    // medalhoes para trocar de heroi (embaixo do palco)
    DATA.HERO_ORDER.forEach((hid, i) => {
      const op = Save.heroUnlocked(hid), sel = hid === id;
      const mx = 302 + (i - 1.5) * 104, r = 38;
      const hv = UI.rect('hcard' + hid, mx - r - 6, 600 - r - 6, 2 * r + 12, 2 * r + 12, () => {
        if (this.view !== hid) Snd.play('heroPick');
        this.view = hid;
      });
      const my = 600 - (sel ? 6 : hv ? 3 : 0);
      A.ell(c, mx, 604 + r - 4, r * 0.8, 7, 'rgba(60,35,15,0.22)');
      if (sel) A.glow(c, mx, my, r + 22, '#ffd27a', 0.5);
      c.save();
      if (!op) c.globalAlpha = 0.5;
      A.heroFace(c, mx, my, r, hid);
      c.restore();
      A.circ(c, mx, my, r, null, sel ? '#f2c14e' : '#fff7e8', sel ? 4 : 2.5);
      if (!op) A.lock(c, mx, my, 12);
      else {
        const lvl = game.heroLevelFor(Save.heroXpOf(hid));
        A.circ(c, mx + r * 0.72, my + r * 0.72, 13, '#3f8f70', '#ffffff', 2);
        A.text(c, String(lvl), mx + r * 0.72, my + r * 0.72 + 1, 13, '#ffffff', 'center', { family: FONT_UI, weight: 900 }, false);
        if (Save.data.hero === hid) A.ipe(c, mx - r * 0.72, my - r * 0.72, 11, 0.3);
      }
    });
    // detalhes do heroi em vista (direita)
    const rx = x + 520, ry = y + 92, rw = w - 560;
    const lvl = game.heroLevelFor(Save.heroXpOf(id));
    A.text(c, `${Hd.name}, ${Hd.title}`, rx, ry + 10, 24, SOFT.ink, 'left', { family: FONT_UI, weight: 900 }, false);
    A.wrap(c, Hd.desc, rw, 15, 700).slice(0, 2).forEach((l, j) => A.text(c, l, rx, ry + 40 + j * 20, 15, SOFT.inkSoft, 'left', null, false));
    const st = `Vida ${Hd.hp} · Dano ${Hd.dmg[0]}–${Hd.dmg[1]} · Armadura ${Math.round(Hd.armor * 100)}% · Velocidade ${Hd.speed}`;
    UKB.chip(c, rx, ry + 92, st, { color: '#b98f6c' });
    if (!open) A.text(c, `Vença a fase ${Hd.unlock + 1} para liberar`, rx + rw, ry + 10, 15, '#c0634e', 'right', { family: FONT_UI, weight: 900 }, false);
    else if (Save.data.hero === id) UKB.chip(c, rx + rw - 96, ry, 'Na batalha', { color: '#5fbfb0' });
    else A.text(c, `Nível ${lvl}`, rx + rw, ry + 10, 16, '#3f8f70', 'right', { family: FONT_UI, weight: 900 }, false);
    // habilidades
    A.text(c, 'Habilidades', rx, ry + 130, 17, SOFT.ink, 'left', { family: FONT_UI, weight: 900 }, false);
    Hd.abilities.forEach((a, j) => {
      const ay = ry + 156 + j * 34;
      A.circ(c, rx + 12, ay, 10, '#e9b84a', '#ffffff', 1.5);
      A.text(c, a.name, rx + 30, ay - 8, 15, SOFT.ink, 'left', { family: FONT_UI, weight: 900 }, false);
      A.text(c, UKB.fit(c, a.desc, rw - 30, 13, 700), rx + 30, ay + 9, 13, SOFT.inkSoft, 'left', null, false);
    });
    // talentos
    const ty0 = ry + 172 + Hd.abilities.length * 34;
    A.text(c, 'Talentos', rx, ty0, 17, SOFT.ink, 'left', { family: FONT_UI, weight: 900 }, false);
    const picks = Save.data.talents[id] || (Save.data.talents[id] = []);
    DATA.TALENT_LVLS.forEach((need, tier) => {
      const ty = ty0 + 20 + tier * 74;
      const ok = open && lvl >= need;
      A.text(c, `Nível ${need}`, rx, ty + 30, 14, ok ? '#3f8f70' : '#b3a597', 'left', { family: FONT_UI, weight: 900 }, false);
      Hd.talents[tier].forEach((T, k) => {
        const bx = rx + 76 + k * ((rw - 80) / 2), bw = (rw - 80) / 2 - 10, bh = 62;
        const on = picks[tier] === k;
        const hv = UI.rect('tal' + tier + k, bx, ty, bw, bh, () => {
          if (!ok) { Snd.play('error'); return; }
          picks[tier] = k; Save.write(); Snd.play('talent');
        });
        const bg = on ? '#eefaf5' : ok ? (hv ? '#fffdf6' : '#fffaf1') : '#f1e8da';
        A.softShadow(c, bx, ty, bw, bh, 14, 6, 0.14, 2, bg);
        A.rrect(c, bx, ty, bw, bh, 14, null, on ? '#5fbfb0' : ok ? '#e9b84a' : SOFT.line, on ? 2.4 : 1.5);
        c.save();
        if (!ok) c.globalAlpha = 0.55;
        A.text(c, UKB.fit(c, T.name, bw - 30, 15, 900), bx + 14, ty + 18, 15, SOFT.ink, 'left', { family: FONT_UI, weight: 900 }, false);
        // descricao em ate 2 linhas (a coluna ficou mais estreita com o palco)
        const dl = A.wrap(c, T.desc, bw - 24, 12, 700);
        if (dl.length > 2) dl[1] = UKB.fit(c, dl.slice(1).join(' '), bw - 24, 12, 700);
        dl.slice(0, 2).forEach((l, j) => A.text(c, l, bx + 14, ty + (dl.length > 1 ? 36 : 41) + j * 15, 12, on ? '#3f8f70' : SOFT.inkSoft, 'left', null, false));
        c.restore();
        if (!ok) A.lock(c, bx + bw - 18, ty + 18, 8);
      });
    });
    // escolher e voltar
    if (open && Save.data.hero !== id) {
      const hv = UI.rect('hpick', x + w - 470, y + h - 70, 210, 50, () => { Save.data.hero = id; Save.write(); Snd.play('heroGo'); });
      A.btn(c, x + w - 470, y + h - 70, 210, 50, 'Levar à batalha', { hover: hv, color: 'gold', size: 19 });
    }
    const hv = UI.rect('hdone', x + w - 240, y + h - 70, 200, 50, () => App.go('map'));
    A.btn(c, x + w - 240, y + h - 70, 200, 50, 'Pronto', { hover: hv, color: 'green', size: 22 });
  },

  // palco: o ceu de Brasilia com o heroi grande em espera num palanque de concreto na cor da chapa, luz da cor do
  // heroi e o efeito de cada um (estrelas, curtidas, notificacoes, confete)
  stage(c, id, open, chegaT) {
    const t = App.time;
    const sx = 76, sy = 86, sw = 452, sh = 470, cx = sx + sw / 2, gy = sy + sh - 78;
    const cols = (typeof RETRATO_BG !== 'undefined' && RETRATO_BG[id]) || ['#f2b65a', '#c46a2a'];
    const SD = DATA.SIDES[(DATA.HEROES[id] || {}).side] || DATA.SIDES.R;
    c.save();
    A.softShadow(c, sx, sy, sw, sh, 26, 10, 0.22, 3, '#3d5a7a');
    A.rrect(c, sx, sy, sw, sh, 26);
    c.clip();
    const bg = c.createLinearGradient(0, sy, 0, sy + sh);
    bg.addColorStop(0, '#4f8fcf'); bg.addColorStop(0.55, '#9cc8ec'); bg.addColorStop(1, '#ead9a6');
    c.fillStyle = bg; c.fillRect(sx, sy, sw, sh);
    // cupulas do Congresso bem ao fundo, claras de neblina seca
    c.fillStyle = 'rgba(255,255,255,0.35)';
    c.beginPath(); c.ellipse(sx + 96, gy - 150, 46, 16, 0, Math.PI, 0); c.fill();
    c.beginPath(); c.ellipse(sx + sw - 92, gy - 166, 50, 18, 0, 0, Math.PI); c.fill();
    c.fillRect(sx + sw / 2 - 30, gy - 260, 22, 110); c.fillRect(sx + sw / 2 + 4, gy - 260, 22, 110);
    // luz de cima (raios) e a aura da cor do heroi atras dele
    c.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 4; i++) {
      const rx0 = sx + 60 + i * 110 + Math.sin(t * 0.3 + i) * 12;
      const g = c.createLinearGradient(0, sy, 0, gy);
      g.addColorStop(0, 'rgba(255,248,214,0.16)'); g.addColorStop(1, 'rgba(255,248,214,0)');
      c.fillStyle = g;
      c.beginPath(); c.moveTo(rx0, sy); c.lineTo(rx0 + 46, sy); c.lineTo(rx0 + 120, gy); c.lineTo(rx0 + 30, gy); c.closePath(); c.fill();
    }
    c.globalCompositeOperation = 'source-over';
    const au = c.createRadialGradient(cx, gy - 150, 10, cx, gy - 150, 230);
    au.addColorStop(0, U.rgba ? U.rgba(cols[0], 0.55) : cols[0]); au.addColorStop(1, 'rgba(0,0,0,0)');
    c.globalAlpha = 0.55 + 0.1 * Math.sin(t * 1.3);
    c.fillStyle = au; c.fillRect(sx, sy, sw, sh);
    c.globalAlpha = 1;
    // galhos de ipe amarelo nos cantos de cima, balancando
    for (const [lx, ly, dir] of [[sx + 10, sy + 14, 1], [sx + sw - 10, sy + 20, -1]]) {
      const sway = 0.05 * Math.sin(t * 0.9 + lx);
      c.save();
      c.translate(lx, ly); c.rotate(sway);
      c.strokeStyle = '#6b4a32'; c.lineWidth = 5; c.lineCap = 'round';
      c.beginPath(); c.moveTo(-dir * 20, -10); c.quadraticCurveTo(dir * 30, 20, dir * 70, 26); c.stroke();
      for (let i = 0; i < 9; i++) {
        const fx = dir * (10 + i * 8 + (i % 3) * 4), fy = 6 + ((i * 37) % 26);
        A.circ(c, fx, fy, 7 + (i % 3), i % 2 ? '#f7cf3c' : '#f2b81f');
        A.circ(c, fx, fy, 2.2, '#d9822b');
      }
      c.restore();
    }
    // palanque de concreto com a faixa da chapa
    A.ell(c, cx + 8, gy + 22, 170, 34, 'rgba(30,40,60,0.28)');
    c.fillStyle = '#e2dccd';
    c.beginPath(); c.ellipse(cx, gy + 14, 156, 34, 0, 0, Math.PI); c.lineTo(cx - 156, gy); c.ellipse(cx, gy, 156, 34, 0, Math.PI, 0, true); c.closePath(); c.fill();
    c.fillStyle = SD.color;
    c.beginPath(); c.ellipse(cx, gy + 9, 156, 34, 0, 0.12, Math.PI - 0.12); c.ellipse(cx, gy + 3, 156, 34, 0, Math.PI - 0.12, 0.12, true); c.closePath(); c.fill();
    A.ell(c, cx, gy, 156, 34, '#f6f3ec', '#cfc6b4', 2);
    A.ell(c, cx - 10, gy - 4, 120, 22, '#fbf9f4');
    // bandeirinhas da chapa nas pontas do palanque
    for (const fx of [cx - 140, cx + 140]) {
      c.strokeStyle = '#8a7a66'; c.lineWidth = 3;
      c.beginPath(); c.moveTo(fx, gy + 2); c.lineTo(fx, gy - 70); c.stroke();
      const w = 6 * Math.sin(t * 3 + fx);
      c.fillStyle = SD.color;
      c.beginPath(); c.moveTo(fx, gy - 70); c.quadraticCurveTo(fx + 18, gy - 64 + w, fx + 34, gy - 62); c.lineTo(fx, gy - 50); c.closePath(); c.fill();
    }
    // o heroi (silhueta se ainda trancado)
    const top = A.heroShow(c, Hd_sprite(id), cx, gy + 4, t, { chegaT: open ? chegaT : null, sil: !open, scale: 2.85 });
    if (!top) A.heroFace(c, cx, gy - 120, 90, id);
    // confete na chegada, nas cores da chapa
    if (open && chegaT < 0.8) {
      const k = chegaT / 0.8;
      for (let i = 0; i < 14; i++) {
        const a = Math.PI + (i / 13) * Math.PI;
        const r = 40 + 130 * k;
        c.globalAlpha = 1 - k;
        c.save();
        c.translate(cx + Math.cos(a) * r, gy + Math.sin(a) * r * 0.4 - 12 * k);
        c.rotate(a + k * 6);
        c.fillStyle = i % 2 ? SD.color : '#f7cf3c';
        c.fillRect(-5, -3, 10, 6);
        c.restore();
      }
      c.globalAlpha = 1;
    }
    // efeito de cada heroi
    const ht = top || 300;
    for (let i = 0; i < 12; i++) {
      const ph = (t * (0.18 + (i % 4) * 0.04) + i * 0.137) % 1;
      const px = cx + Math.sin(i * 2.7 + t * 0.8) * (60 + (i % 3) * 40);
      if (id === 'boitata') {
        // confete verde e amarelo caindo
        const py = sy + ph * (gy - sy);
        c.save(); c.translate(px, py); c.rotate(t * 3 + i);
        c.globalAlpha = 0.85 * (1 - ph * 0.6);
        c.fillStyle = i % 2 ? '#2f9a4a' : '#f7cf3c';
        c.fillRect(-5, -3, 10, 6);
        c.restore();
      } else if (id === 'benzedeira') {
        // notificacoes do celular subindo
        const py = gy - ht * 0.5 - ph * 150;
        c.globalAlpha = 0.8 * (1 - ph);
        A.circ(c, cx + 40 + Math.sin(ph * 5 + i) * 34, py, 8, i % 3 ? '#2f9a4a' : '#e8463c', '#ffffff', 2);
      } else if (id === 'caipora') {
        // curtidas (coracoes) subindo do pau de selfie
        const py = gy - ht * 0.7 - ph * 160;
        const hx = cx + 60 + Math.sin(ph * 4 + i) * 40, r = 7 + ph * 4;
        c.globalAlpha = 0.85 * (1 - ph);
        c.fillStyle = i % 2 ? '#ff6b8a' : '#ff9db0';
        c.beginPath(); c.moveTo(hx, py + r * 0.9);
        c.bezierCurveTo(hx - r * 1.4, py - r * 0.2, hx - r * 0.6, py - r * 1.3, hx, py - r * 0.4);
        c.bezierCurveTo(hx + r * 0.6, py - r * 1.3, hx + r * 1.4, py - r * 0.2, hx, py + r * 0.9);
        c.fill();
      } else {
        // estrelinhas vermelhas do palanque
        const py = gy - 40 - ((i * 53) % Math.max(1, ht)) + Math.sin(t * 1.7 + i) * 12;
        const on = 0.5 + 0.5 * Math.sin(t * 2.3 + i * 1.9);
        c.globalAlpha = 0.9 * on;
        c.fillStyle = '#e8463c';
        c.beginPath();
        for (let j = 0; j < 10; j++) {
          const rr = j % 2 ? 3 : 7.5, aa = -Math.PI / 2 + j * Math.PI / 5;
          c.lineTo(px + Math.cos(aa) * rr, py + Math.sin(aa) * rr);
        }
        c.closePath(); c.fill();
      }
      c.globalAlpha = 1;
    }
    c.restore();
    A.rrect(c, sx, sy, sw, sh, 26, null, '#e0c79a', 3);
  },
};

function Hd_sprite(id) { return (DATA.HEROES[id] && DATA.HEROES[id].sprite) || 'hero'; }

// ------------------------------------------------------------ bestiario
// silhueta de inimigo ainda nao visto (sem ctx.filter, que o WebKit do app nao suporta)
const SIL = {};
function silhouette(type) {
  const s = App.scale, key = type + ':' + s.toFixed(3);
  if (SIL[key]) return SIL[key];
  const cv = document.createElement('canvas');
  cv.width = Math.ceil(100 * s); cv.height = Math.ceil(100 * s);
  const c = cv.getContext('2d');
  c.setTransform(s, 0, 0, s, 0, 0);
  A.icon(c, type, 50, 50, 40, { time: 0 });
  c.setTransform(1, 0, 0, 1, 0, 0);
  c.globalCompositeOperation = 'source-in';
  c.fillStyle = 'rgba(70,40,15,0.45)';
  c.fillRect(0, 0, cv.width, cv.height);
  SIL[key] = cv;
  return cv;
}

function enemySpecials(E) {
  const out = [];
  if (E.boss) out.push('Chefe');
  if (E.flying) out.push('Voa');
  if (E.stealth) out.push('Invisível');
  if (E.frontShield) out.push('Escudo frontal');
  if (E.sabotage) out.push('Sabota torres');
  if (E.split) out.push('Solta filhotes');
  if (E.heal) out.push('Cura aliados');
  if (E.ranged) out.push('Ataca de longe');
  if (E.burrow || E.wormBurrow) out.push('Cava na terra');
  if (E.summon) out.push('Chama reforços');
  if (E.firestorm) out.push('Incendeia torres');
  if (E.unblockable) out.push('Não pode ser bloqueado');
  return out;
}

const Bestiary = {
  sel: 'raider',
  draw(c) {
    WorldMap.ensureBg();
    c.drawImage(WorldMap.bg, 0, 0, W, H);
    c.fillStyle = 'rgba(20,10,0,0.5)'; c.fillRect(0, 0, W, H);
    UI.blocker();
    const x = 40, y = 26, w = 1200, h = 668;
    A.panel(c, x, y, w, h);
    A.text(c, 'Bestiário', W / 2, y + 44, 38, SOFT.title, 'center', { family: FONT_TITLE, weight: 700 }, 'rgba(255,255,255,0.9)', 5);
    const types = Object.keys(DATA.ENEMIES);
    const seen = new Set(Save.data.seen);
    const cols = 6;
    types.forEach((type, i) => {
      const col = i % cols, row = Math.floor(i / cols);
      const cx = x + 80 + col * 104, cy = y + 140 + row * 160;
      const known = seen.has(type);
      const hv = UI.rect('be' + type, cx - 48, cy - 54, 96, 148, () => { if (known) { this.sel = type; Snd.play('click'); } });
      A.rrect(c, cx - 47, cy - 53, 94, 146, 16, this.sel === type ? '#fff4ec' : hv ? '#fff6e6' : '#f6ead2', this.sel === type ? '#ec8a76' : SOFT.line, 2.5);
      if (known) A.icon(c, type, cx, cy + 4, 38, { time: App.time });
      else {
        c.drawImage(silhouette(type), cx - 46, cy - 42, 92, 92);
        A.text(c, '?', cx, cy + 4, 32, '#5a3a1e', 'center', null, false);
      }
      const nm = known ? shortName(DATA.ENEMIES[type].name) : '???';
      const ls = A.wrap(c, nm, 88, 13, 800);
      ls.slice(0, 2).forEach((l, j) => A.text(c, l, cx, cy + 58 + j * 15, 13, SOFT.ink, 'center', null, false));
    });
    // detalhes: nome, uma linha, atributos em linhas com icone, tracos em chips e dica em cartao
    const E = DATA.ENEMIES[this.sel];
    const dx = x + 668, dy = y + 86;
    A.rrect(c, dx, dy, 496, 500, 20, 'rgba(255,252,244,0.75)', SOFT.line, 2);
    if (seen.has(this.sel)) {
      A.circ(c, dx + 96, dy + 100, 72, SOFT.card2, SOFT.line, 3);
      A.icon(c, this.sel, dx + 96, dy + 104, 64, { time: App.time });
      const nm = A.wrap(c, E.name, 270, 22, 900).slice(0, 2);
      nm.forEach((l, j) => A.text(c, l, dx + 190, dy + 46 + j * 26, 22, SOFT.ink, 'left', { family: FONT_UI, weight: 900 }, false));
      const ls = A.wrap(c, E.desc, 280, 15, 600).slice(0, 3);
      ls.forEach((l, j) => A.text(c, l, dx + 190, dy + 56 + nm.length * 26 + j * 20, 15, SOFT.inkSoft, 'left', { family: FONT_UI, weight: 600 }, false));
      UKB.rows(c, dx + 28, dy + 190, 440, [
        { g: 'hp', label: 'Vida', value: String(E.hp) },
        { g: 'armor', label: 'Armadura', value: lvlWord(E.armor) },
        { g: 'mres', label: 'Resistência mágica', value: lvlWord(E.mres) },
        { g: 'speed', label: 'Velocidade', value: speedWord(E.speed) },
        { g: 'lives', label: 'Votos que tira', value: String(E.lives) },
        { g: 'gold', label: 'Recompensa', value: E.gold + ' de verba' },
      ]);
      let chx = dx + 28;
      for (const [t, ic, col] of enemyChips(E).slice(0, 3)) chx += UKB.chip(c, chx, dy + 386, t, { icon: ic, color: col }) + 6;
      A.rrect(c, dx + 28, dy + 410, 440, 72, 16, 'rgba(95,191,176,0.12)', '#5fbfb0', 1.8);
      A.text(c, 'DICA', dx + 46, dy + 428, 11, '#3f8f82', 'left', null, false);
      A.wrap(c, E.tip, 404, 15, 700).slice(0, 2).forEach((l, j) => A.text(c, l, dx + 46, dy + 449 + j * 19, 15, SOFT.ink, 'left', null, false));
    }
    UKB.chip(c, x + 60, y + h - 44, `${types.filter(t => seen.has(t)).length} de ${types.length} descobertos`, { icon: 'eye', color: '#ad94de' });
    const hv = UI.rect('back', x + w - 240, y + h - 70, 200, 50, () => App.go('map'));
    A.btn(c, x + w - 240, y + h - 70, 200, 50, 'Voltar', { hover: hv, color: 'green', size: 22 });
  },
};
