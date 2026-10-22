// Retratos das torres para os icones da interface: monta cada torre (niveis 1-3 e especializacoes) com tripulacao,
// canhoes e pecas que mexem no proprio jogo (Chrome headless, A.towerSprite) e salva um PNG por torre em
// arte/render/icones/tw_<tipo>_<nivel> ou tw_<especializacao>, com o meta.json do conjunto.
// uso: node tools/sprites/retratos.js     (depois: python3 tools/sprites/empacotar.py icones)
//      CHAPA=R node tools/sprites/retratos.js   (torres da Chapa Vermelha em arte/render_r/icones; depois CHAPA=R empacotar.py icones)
const puppeteer = require(require('path').join(__dirname, '..', 'node_modules', 'puppeteer-core'));
const path = require('path'), fs = require('fs');
const ROOT = path.join(__dirname, '..', '..');
const CHAPA = (process.env.CHAPA || 'V').toUpperCase().slice(0, 1) === 'R' ? 'R' : 'V';
const OUT = path.join(ROOT, 'arte', CHAPA === 'R' ? 'render_r' : 'render', 'icones');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new',
    args: ['--allow-file-access-from-files'], defaultViewport: { width: 1280, height: 720, deviceScaleFactor: 1 } });
  const page = await browser.newPage();
  page.on('pageerror', e => console.log('erro:', e.message));
  await page.goto('file://' + path.join(ROOT, 'index.html') + '#fase=1&save=full&notips');
  for (let i = 0; i < 60; i++) { if (await page.evaluate(() => !!(window.App && App.game))) break; await sleep(200); }
  await page.evaluate(side => { Save.setSide(side); App.lv.speed = 0; SPR.want(Object.keys(SPRITE_META.fams)); }, CHAPA);
  for (let i = 0; i < 150; i++) { if (await page.evaluate(() => Object.keys(SPRITE_META.fams).every(f => SPR.ok(f)))) break; await sleep(200); }
  const shots = await page.evaluate(() => {
    const g = App.game; g.gold = 1e6; g.quickBuild = true; g.loadout = DATA.TOWER_ORDER.slice(); g.rules = {}; g.canBuildType = () => true;
    const s = g.spots[0];
    const out = {};
    const fin = t => { t.working = false; t.buildT = 99; t.buildDur = 0; if (g.finishWork) g.finishWork(t); };
    const snap = (t, key) => {
      const K = 1.6, cv = document.createElement('canvas');
      cv.width = 160; cv.height = 192;
      const c = cv.getContext('2d');
      c.setTransform(K, 0, 0, K, 80 - t.x * K, 160 - t.y * K);
      A.towerSprite(c, t, 0.5);
      out[key] = cv.toDataURL('image/png');
    };
    for (const type of DATA.TOWER_ORDER) {
      for (const sp of [null, ...DATA.TOWERS[type].specs]) {
        if (s.tower) g.sell(s.tower);
        const t = g.build(s, type); fin(t);
        if (!sp) { snap(t, `tw_${type}_1`); g.upgrade(t); fin(t); snap(t, `tw_${type}_2`); g.upgrade(t); fin(t); snap(t, `tw_${type}_3`); continue; }
        g.upgrade(t); fin(t); g.upgrade(t); fin(t); g.specialize(t, sp); fin(t);
        snap(t, `tw_${sp}`);
      }
    }
    return out;
  });
  const meta = JSON.parse(fs.readFileSync(path.join(OUT, 'meta.json'), 'utf8'));
  for (const [key, url] of Object.entries(shots)) {
    fs.mkdirSync(path.join(OUT, key), { recursive: true });
    fs.writeFileSync(path.join(OUT, key, 'still_00.png'), Buffer.from(url.split(',')[1], 'base64'));
    meta.sets[key] = { w: 160, h: 192, anchor: [80, 160], modes: { still: 1 }, icon: 1, portrait: 1 };
  }
  fs.writeFileSync(path.join(OUT, 'meta.json'), JSON.stringify(meta, null, 1));
  console.log('RETRATOS_OK', Object.keys(shots).length);
  await browser.close();
})();
