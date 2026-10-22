// Teste ponta a ponta: joga clicando como uma pessoa e falha se aparecer erro de JavaScript.
// uso: node tools/e2e.js [pasta_de_screenshots]
const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const OUT = process.argv[2] || path.join(__dirname, 'shots');
fs.mkdirSync(OUT, { recursive: true });
const URL = 'file://' + path.join(__dirname, '..', 'index.html');
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: 'new',
    args: ['--autoplay-policy=no-user-gesture-required', '--window-size=1280,720'],
    defaultViewport: { width: 1280, height: 720, deviceScaleFactor: 1 },
  });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + (e.stack || e.message).split('\n').slice(0, 4).join(' | ')));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); else if (m.type() === 'warn' && m.text().includes('invalid')) console.log('AVISO ' + m.text().slice(0, 400)); });
  let n = 0;
  const shot = async name => { await page.screenshot({ path: path.join(OUT, `${String(++n).padStart(2, '0')}_${name}.png`) }); };
  const click = async (x, y, wait = 250) => { await page.mouse.move(x, y); await sleep(60); await page.mouse.down(); await sleep(40); await page.mouse.up(); await sleep(wait); };
  const ev = (fn, ...a) => page.evaluate(fn, ...a);
  const step = async (label, cond, arg) => {
    const ok = await page.evaluate(cond, arg);
    console.log((ok ? 'OK   ' : 'FALHA') + ' ' + label);
    if (!ok) errors.push('falhou: ' + label);
  };
  // posicao de um botao do anel do menu de construcao
  const ringBtn = (spotIdx, type) => ev((i, ty) => {
    const s = App.game.spots[i];
    const [cx, cy] = Level.menuCenter(s.x, s.y);
    const types = App.game.loadout;
    const R = Level.ringR('build', types.length);
    const a = Level.ringAngles(types.length)[types.indexOf(ty)];
    return Level.ringPos(cx, cy, R, a);
  }, spotIdx, type);
  const build = async (spotIdx, type, open = true) => {
    const s = await ev(i => [App.game.spots[i].x, App.game.spots[i].y], spotIdx);
    if (open) await click(s[0], s[1], 250);
    const b = await ringBtn(spotIdx, type);
    await click(b[0], b[1], 300);
  };
  // fase no mapa: o heroi anda pela trilha ate ela e o painel abre na chegada
  const clickNode = async (x, y, i) => {
    await click(x, y, 200);
    for (let k = 0; k < 30 && !(await ev(j => WorldMap.panel === j, i)); k++) await sleep(100);
  };
  const panelGo = () => ev(() => [140 + 520 + 222, 40 + 640 - 52]);

  await page.goto(URL);
  await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await page.reload();
  await sleep(1200);
  await shot('titulo');
  await step('tela de titulo', () => App.screen === 'title');

  await click(640, 508, 600);
  await step('escolha da chapa aberta', () => Title.choose === true);
  await shot('chapa');
  await click(340, 623, 800);   // "Escolher" da Chapa Vermelha
  await step('mapa aberto', () => App.screen === 'map' && DATA.SIDE === 'R');
  await shot('mapa');
  await clickNode(...(await ev(() => [DATA.WORLD[0].x, DATA.WORLD[0].y - 10])), 0);
  await step('painel da fase 1', () => WorldMap.panel === 0);
  await step('arsenal inicial so com arqueiros e quartel', () => WorldMap.sel.join() === 'archer,barracks');
  await shot('painel_fase');
  const go = await panelGo();
  await click(go[0], go[1], 800);
  await step('fase 1 iniciada', () => App.screen === 'level' && App.game.levelIdx === 0);
  await step('fase 1 so permite arqueiros e quartel', () => App.game.loadout.join() === 'archer,barracks');
  await shot('fase1_tutorial');

  // construir
  const sp3 = await ev(() => [App.game.spots[3].x, App.game.spots[3].y]);
  await click(sp3[0], sp3[1], 300);
  await step('menu de construcao aberto', () => !!(App.lv.sel && App.lv.sel.spot === App.game.spots[3]));
  const ab = await ringBtn(3, 'archer');
  await page.mouse.move(ab[0], ab[1]); await sleep(300);
  await shot('menu_construcao_hover');
  await click(ab[0], ab[1], 400);
  await step('torre de arqueiros construida', () => App.game.spots[3].tower && App.game.spots[3].tower.type === 'archer');
  await step('torre nasce em obra de 3 s', () => { const t = App.game.spots[3].tower; return t.working && t.buildDur === DATA.BUILD_TIME; });
  await build(1, 'barracks');
  await step('quartel construido', () => App.game.spots[1].tower && App.game.spots[1].tower.type === 'barracks');
  await step('quartel sem soldados durante a obra', () => App.game.spots[1].tower.units.length === 0);
  await build(9, 'archer');
  await step('segunda torre de arqueiros', () => App.game.spots[9].tower && App.game.spots[9].tower.type === 'archer');
  await shot('tres_torres');

  // previa da onda e chamada
  const wb = await ev(() => { const gr = Level.waveGroups(App.game)[0]; return [gr.x, gr.y]; });
  await page.mouse.move(wb[0], wb[1]); await sleep(300);
  await shot('previa_onda');
  await click(wb[0], wb[1], 400);
  await step('onda 1 chamada', () => App.game.wave === 1 && App.game.state === 'running');
  await sleep(6000);
  await shot('onda1');
  await step('obra concluida', () => !App.game.spots[3].tower.working && !App.game.spots[9].tower.working);
  await step('soldados saem quando o quartel fica pronto', () => App.game.spots[1].tower.units.length === 3);

  // mover heroina
  await click(52, 664, 300);
  await step('modo heroina', () => App.lv.mode === 'hero');
  await click(960, 250, 300);
  await step('heroina recebeu ordem', () => !!App.game.hero.order || Math.abs(App.game.hero.rx - 960) < 2);

  // feitico pelo teclado
  await sleep(4000);
  await page.keyboard.press('1');
  await step('modo feitico', () => App.lv.mode === 'spell' && App.lv.spell === 'fury');
  const target = await ev(() => { const e = App.game.enemies.find(x => App.game.visible(x)); return e ? [e.x, e.y] : [1000, 230]; });
  await click(target[0], target[1], 300);
  await step('furia lancada', () => App.game.spells.fury.cd > 0);
  await sleep(500);
  await shot('furia');

  // evoluir e trocar o alvo da torre
  await ev(() => { App.game.gold += 500; });
  await click(sp3[0], sp3[1] - 20, 300);
  await step('torre selecionada', () => !!(App.lv.sel && App.lv.sel.tower));
  const upb = await ev(() => { const t = App.game.spots[3].tower; const [cx, cy] = Level.menuCenter(t.x, t.y - 4); return Level.slotPos('up', cx, cy); });
  await page.mouse.move(upb[0], upb[1]); await sleep(300);
  await shot('menu_torre');
  await click(upb[0], upb[1], 300);
  await step('torre evoluida', () => App.game.spots[3].tower.tier === 2);
  await step('evolucao em obra de 3 s', () => { const t = App.game.spots[3].tower; return t.working && t.buildDur === DATA.UPGRADE_TIME && !!t.prev; });
  await page.mouse.move(upb[0], upb[1] + 2); await sleep(400);
  await shot('torre_em_obra');
  await click(upb[0], upb[1], 300);
  await step('nao evolui de novo durante a obra', () => App.game.spots[3].tower.tier === 2);
  const pb = await ev(() => { const t = App.game.spots[3].tower; const [cx, cy] = Level.menuCenter(t.x, t.y - 4); return Level.slotPos('side', cx, cy); });
  await page.mouse.move(pb[0], pb[1]); await sleep(250);
  await shot('alvo_da_torre');
  await click(pb[0], pb[1], 300);
  await step('alvo trocado pelo menu', () => App.game.spots[3].tower.prio === 'last');
  await page.keyboard.press('t'); await sleep(200);
  await step('alvo trocado pelo atalho T', () => App.game.spots[3].tower.prio === 'strong');
  await click(20, 400, 200);

  // ponto de encontro do quartel
  const sp1 = await ev(() => [App.game.spots[1].x, App.game.spots[1].y]);
  await click(sp1[0], sp1[1] - 20, 300);
  const rb = await ev(() => { const t = App.game.spots[1].tower; const [cx, cy] = Level.menuCenter(t.x, t.y - 4); return Level.slotPos('side', cx, cy); });
  await click(rb[0], rb[1], 300);
  await step('modo ponto de encontro', () => App.lv.mode === 'rally');
  const rp = await ev(() => { const t = App.game.spots[1].tower; const p = App.game.paths[0]; for (let d = 0; d < p.len; d += 5) { const q = p.at(d, {}); if (App.game.canRally(t, q.x, q.y) && Math.hypot(q.x - t.rally.x, q.y - t.rally.y) > 40) return [q.x, q.y]; } return [t.rally.x, t.rally.y]; });
  await click(rp[0], rp[1], 300);
  await step('ponto de encontro movido', () => App.lv.mode === null);

  // velocidade e pausa
  await click(1192, 36, 200);
  await step('velocidade 2x', () => App.lv.speed === 2);
  await page.keyboard.press('Space'); await sleep(300);
  await step('pausado', () => App.lv.paused === true);
  await shot('pausa');
  await click(640, 291, 300);
  await step('despausado', () => App.lv.paused === false);

  // clicar num inimigo
  await sleep(1500);
  const en = await ev(() => { const e = App.game.enemies.find(x => App.game.targetable(x) && !x.flying); return e ? [e.x, e.y - 10] : null; });
  if (en) {
    await click(en[0], en[1], 300);
    await step('info do inimigo', () => !!(App.lv.sel && App.lv.sel.enemy));
    await shot('info_inimigo');
  }

  // acelerar ate o fim
  await ev(() => {
    const g = App.game;
    g.gold += 3000;
    g.quickBuild = true;
    for (const t of g.towers) { g.finishWork(t); g.upgrade(t); g.upgrade(t); }
    for (const s of g.spots) if (!s.tower) g.build(s, ['archer', 'barracks'][s.i % 2]);
    for (let i = 0; i < 60 * 600 && g.state !== 'won' && g.state !== 'lost'; i++) { if (g.canCallWave()) g.callWave(); g.update(STEP); }
  });
  await sleep(2600);
  await step('fase vencida', () => App.game.state === 'won' && App.lv.overlay);
  await step('Rachadinha (magos) liberada na vitoria', () => [].concat(App.lv.unlocked).includes('mage') && Save.unlockedTowers().includes('mage'));
  await shot('vitoria');
  await step('estrelas salvas', () => Save.data.stars[0] > 0 && JSON.parse(localStorage.getItem(Save.key)).stars[0] > 0);
  const cont = await ev(() => App.lv.endBtns.a);
  await click(cont[0], cont[1], 600);
  await step('voltou ao mapa', () => App.screen === 'map');
  await shot('mapa_apos_vitoria');

  // melhorias (custo 1, 2, 2)
  await click(805, 652, 500);
  await step('tela de melhorias', () => App.screen === 'upgrades');
  await click(40 + 96, 26 + 248, 300);
  await step('melhoria comprada', () => Save.data.up.archer === 1 && Save.freeStars() === Save.totalStars() - 1);
  await click(40 + 96, 26 + 248 + 128, 300);
  await step('nivel II custa 2 estrelas', () => Save.data.up.archer === 2 && Save.spentStars() === 3);
  await shot('melhorias');
  await click(40 + 1200 - 140, 26 + 668 - 45, 400);
  await step('voltou das melhorias', () => App.screen === 'map');

  // bestiario
  await click(1016, 652, 500);
  await step('bestiario', () => App.screen === 'bestiary');
  await shot('bestiario');
  await click(40 + 1200 - 140, 26 + 668 - 45, 400);

  // desafio da fase 1
  await clickNode(...(await ev(() => [DATA.WORLD[0].x, DATA.WORLD[0].y - 10])), 0);
  await click(140 + 520 + 113 + 52, 40 + 47, 300);   // 2a de 4 abas (campanha, desafio, heroico, ferro)
  await step('aba de desafio', () => WorldMap.mode === 'chal' && WorldMap.sel.join() === 'archer');
  await shot('painel_desafio');
  const go2 = await panelGo();
  await click(go2[0], go2[1], 800);
  await step('desafio iniciado so com arqueiros', () => App.game.mode === 'chal' && App.game.loadout.join() === 'archer');
  await ev(() => {
    const g = App.game;
    g.gold = 9000;
    g.quickBuild = true;
    for (const s of g.spots) { const t = g.build(s, 'archer'); if (t) { g.upgrade(t); g.upgrade(t); g.specialize(t, 'ballista'); } }
    for (let i = 0; i < 60 * 600 && g.state !== 'won' && g.state !== 'lost'; i++) { if (g.canCallWave()) g.callWave(); g.update(STEP); }
  });
  await sleep(2600);
  await step('desafio vencido vale estrela', () => App.game.state === 'won' && Save.data.chal[0] === true);
  await shot('desafio_vencido');

  // progresso completo para testar o resto
  await ev(() => {
    Save.data.stars = DATA.LEVELS.map(() => 3);
    Save.data.seen = Object.keys(DATA.ENEMIES);
    Save.data.heroXp = 4000;
    Save.data.trilhas = DATA.WORLD.map((_, i) => i);   // sem a animacao das trilhas novas
    Save.write();
    App.go('map');
  });
  await sleep(400);
  await clickNode(...(await ev(() => [DATA.WORLD[4].x, DATA.WORLD[4].y - 10])), 4);
  await step('painel da fase 5', () => WorldMap.panel === 4);
  await step('arsenal com 5 de 8 torres', () => WorldMap.sel.length === 5 && Save.unlockedTowers().length === 8);
  // troca: tira a artilharia e poe o mercado
  // posicao das cartas do arsenal publicada pela tela (WorldMap._ars)
  const ars = await ev(() => WorldMap._ars);
  const card = (k) => [ars.rx + 4 + (k % 4) * 110 + 50, 0];
  const ary = ars.ry + 18 + 42;
  await click(card(3)[0], ary, 250);
  await step('artilharia saiu do arsenal', () => !WorldMap.sel.includes('artillery'));
  await click(card(7)[0], ary + 92, 250);
  await step('mercado entrou no arsenal', () => WorldMap.sel.includes('market') && WorldMap.sel.length === 5);
  await shot('arsenal_trocado');
  const go3 = await panelGo();
  await click(go3[0], go3[1], 800);
  await step('fase 5 com o arsenal escolhido', () => App.game.levelIdx === 4 && App.game.loadout.includes('market') && !App.game.loadout.includes('artillery'));
  await ev(() => { App.lv.noticeQ = []; });

  // mercado (Banco Vorcash) pagando na largada; a satira nao tem ruinas nem comporta
  await ev(() => { App.game.gold = 3000; });
  await build(2, 'market');
  await step('mercado construido', () => App.game.spots[2].tower && App.game.spots[2].tower.type === 'market');
  const wb5 = await ev(() => { const gr = Level.waveGroups(App.game)[0]; return [gr.x, gr.y]; });
  await click(wb5[0], wb5[1], 400);
  await step('mercado pagou na largada', () => App.game.stats.income > 0);
  await ev(() => { const g = App.game; for (let i = 0; i < 60 * 40; i++) g.update(STEP); });
  await sleep(500);
  await shot('fase5_em_jogo');

  // tempestade na fase 4 (Praca dos Tres Poderes)
  await ev(() => { App.startLevel(3); App.lv.noticeQ = []; });
  await ev(() => {
    const g = App.game;
    g.gold = 20000;
    g.quickBuild = true;
    const plan = ['archer', 'mage', 'banner', 'barracks', 'cistern'];
    g.spots.forEach((s, i) => { const t = g.build(s, plan[i % plan.length]); if (t) { g.upgrade(t); g.upgrade(t); } });
    g.callWave();
    for (let i = 0; i < 60 * 400 && !g.stormOn(); i++) { if (g.canCallWave() && g.countdown > 0) g.callWave(); g.update(STEP); }
    for (let i = 0; i < 60 * 3; i++) g.update(STEP);
  });
  await sleep(800);
  await step('tempestade ativa', () => App.game.stormOn());
  await step('estandartes revelam os furtivos', () => { const g = App.game; return g.enemies.filter(e => e.T.stealth).every(e => typeof e.revealed === 'boolean'); });
  await shot('tempestade');

  // chefe final: o candidato da chapa rival sobe a rampa na ultima onda da fase 5
  await ev(() => { App.startLevel(4); App.lv.noticeQ = []; });
  await ev(() => {
    const g = App.game;
    g.gold = 90000;
    g.quickBuild = true;
    const plan = [['archer', 'ballista'], ['cistern', 'geyser'], ['windmill', 'tornado'], ['mage', 'lightning'], ['banner', 'drums']];
    g.spots.forEach((s, i) => { const [ty, sp] = plan[i % plan.length]; const t = g.build(s, ty); if (t) { g.upgrade(t); g.upgrade(t); g.specialize(t, sp); for (const ab of DATA.SPECS[sp].abilities) { g.buyAbility(t, ab.id); g.buyAbility(t, ab.id); g.buyAbility(t, ab.id); } } });
    g.startWave(DATA.LEVELS[4].waves.length - 1);
    for (let i = 0; i < 60 * 30; i++) g.update(STEP);
  });
  await sleep(1200);
  await step('candidato rival na tela', () => App.game.enemies.some(e => e.type === 'heart'));
  await shot('chefe_candidato');
  await ev(() => { const g = App.game; for (let i = 0; i < 60 * 300 && g.state === 'running'; i++) g.update(STEP); });
  await sleep(2600);
  await shot('fim_fase5');
  await step('fase 5 terminou', () => App.game.state === 'won' || App.game.state === 'lost');

  // derrota
  await ev(() => { App.startLevel(1); const g = App.game; g.lives = 1; g.callWave(); for (let i = 0; i < 60 * 200 && g.state !== 'lost'; i++) g.update(STEP); });
  await sleep(2600);
  await step('tela de derrota', () => App.game.state === 'lost' && App.lv.overlay);
  await shot('derrota');

  console.log('\nErros:', errors.length ? '\n' + errors.join('\n') : 'nenhum');
  await browser.close();
  process.exit(errors.length ? 1 : 0);
})().catch(e => { console.error('FALHA GERAL', e); process.exit(2); });
