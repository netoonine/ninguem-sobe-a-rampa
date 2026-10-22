// Vitrine conjunta: 8 torres nivel 3 + os 18 inimigos parados na estrada, para conferir escala e luz.
const puppeteer = require(require('path').join(__dirname, '..', 'node_modules', 'puppeteer-core'));
const path = require('path');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new',
    args: ['--allow-file-access-from-files', '--autoplay-policy=no-user-gesture-required'], defaultViewport: { width: 1280, height: 720, deviceScaleFactor: 2 } });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('file://' + path.join(__dirname, '..', '..', 'index.html') + '#fase=' + (process.argv[3] || '3') + '&save=full&notips');
  for (let i = 0; i < 60; i++) { if (await page.evaluate(() => !!(window.App && App.game))) break; await sleep(200); }
  await page.evaluate(() => { SPR.want(Object.keys(SPRITE_META.fams)); });
  for (let i = 0; i < 150; i++) { if (await page.evaluate(() => Object.keys(SPRITE_META.fams).every(f => SPR.ok(f)))) break; await sleep(200); }
  await page.evaluate(() => { if (window.ESPR) Object.keys(INIMIGOS_META.sets).forEach(t => ESPR.want(t)); });
  for (let i = 0; i < 150; i++) { if (await page.evaluate(() => !window.ESPR || Object.keys(INIMIGOS_META.sets).every(t => ESPR.ready(t)))) break; await sleep(200); }
  await page.evaluate(() => {
    const g = App.game; g.gold = 1e6; g.canBuildType = () => true; g.rules = {};
    SPR.level = () => {};
    const fin = t => { t.working = false; t.buildT = 99; t.buildDur = 0; };
    const plan = [['archer', 3], ['mage', 3], ['artillery', 3], ['barracks', 3], ['cistern', 3], ['windmill', 3], ['banner', 3], ['market', 3]];
    g.spots.forEach((s, i) => {
      if (i >= plan.length) return;
      if (s.ruin) { g.gold += 999; g.clearRuin(s); }
      const [type, lv] = plan[i];
      const t = g.build(s, type); if (!t) return; fin(t);
      const n = typeof lv === 'number' ? lv : 3;
      for (let k = 1; k < n; k++) { g.upgrade(t); fin(t); }
      if (typeof lv === 'string') { g.specialize(t, lv); fin(t); }
    });
    // inimigos: espalhados pela estrada, parados no lugar mas animando
    const tipos = Object.keys(DATA.ENEMIES), np = g.paths.length;
    tipos.forEach((ty, i) => {
      const pi = i % np, P = g.paths[pi];
      const e = g.spawn(ty, pi, P.len * (0.12 + 0.76 * (i / tipos.length)));
      e.hp = e.maxHp = 1e9; e._d0 = e.d;
    });
    const up = g.update.bind(g);
    g.update = dt => { up(dt); g.enemies.forEach(e => { if (e._d0 != null) { e.d = e._d0; g.placeEnemy(e); } }); };
  });
  await sleep(2500);
  await page.screenshot({ path: process.argv[2], quality: 90 });
  console.log('erros', errors.length ? errors.join(' | ') : 'nenhum');
  await browser.close();
})();
