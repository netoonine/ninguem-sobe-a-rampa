'use strict';
// Versao do celular, depois do jogo carregado: toque, tela cheia, aviso de girar e o save guardado na conta.

// ------------------------------------------------------------ toque
// botao do anel: no dedo nao existe "passar por cima"; o 1o toque mostra o cartao, o 2o no mesmo botao confirma
UI.twoTap = (key, cb) => (x, y, b) => {
  if (UI.touch && UI._prevArmed !== key) { UI.armed = key; return; }
  if (cb) cb(x, y, b);
};

// textos de ajuda falam de toque (e somem os atalhos de teclado)
(() => {
  const tx = s => typeof s !== 'string' ? s : s.replace(/^Clique para /, 'Toque de novo para ')
    .replace(/Clique( \(ou \w\))?/g, 'Toque').replace(/clique/g, 'toque');
  const base = UI.setTip;
  UI.setTip = function (x, y, title, lines, o) {
    if (UI.touch) {
      if (lines) lines = lines.filter(l => !/^Atalho/.test(l)).map(tx);
      if (o) o = Object.assign({}, o, { action: tx(o.action), footer: tx(o.footer) });
    }
    return base.call(this, x, y, title, lines, o);
  };
})();

// o navegador so libera o som num toque terminado (pointerdown com dedo nao conta)
['pointerup', 'touchend'].forEach(t => window.addEventListener(t, () => { try { Snd.init(); } catch (e) { /* sem audio */ } }, { passive: true }));

// ------------------------------------------------------------ tela cheia e aviso de girar
(() => {
  const btn = document.getElementById('telaCheia');
  const girar = document.getElementById('girar');
  const doc = document;
  const pode = !!(doc.fullscreenEnabled || doc.webkitFullscreenEnabled);
  const cheia = () => !!(doc.fullscreenElement || doc.webkitFullscreenElement);
  const deitado = window.matchMedia('(orientation: portrait) and (pointer: coarse)');

  btn.addEventListener('click', () => {
    const el = doc.documentElement;
    const req = el.requestFullscreen || el.webkitRequestFullscreen;
    if (!req) return;
    try {
      const p = req.call(el, { navigationUI: 'hide' });
      const travar = () => { try { screen.orientation.lock('landscape').catch(() => {}); } catch (e) { /* sem trava */ } };
      if (p && p.then) p.then(travar).catch(() => { btn.hidden = true; });
      else travar();
    } catch (e) { btn.hidden = true; }
  });

  // botao no canto de cima a esquerda da area do jogo, so fora da batalha (la o canto e do HUD)
  const posiciona = () => {
    const ok = pode && !cheia() && App.canvas && App.screen !== 'level';
    btn.hidden = !ok;
    if (ok) {
      const r = App.canvas.getBoundingClientRect();
      btn.style.left = (r.left + App.offX + 12) + 'px';
      btn.style.top = (r.top + App.offY + 12) + 'px';
    }
    girar.hidden = !deitado.matches;
  };
  setInterval(posiciona, 400);
  window.addEventListener('resize', posiciona);
  window.addEventListener('load', posiciona);
})();

// ------------------------------------------------------------ save na conta
// O jogo grava no localStorage (Save.write). Aqui uma copia vai para o banco do artifact, na pasta particular de quem
// joga, e o mais novo dos dois vence ao abrir. Fora do claude.ai (ou sem login) fica so o localStorage.
(() => {
  const lsGet = k => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  const lsSet = (k, v) => { try { localStorage.setItem(k, String(v)); } catch (e) { /* sem armazenamento */ } };
  const KT = Save.key + '_t';
  let ref = null, enviado = null, ocupado = false, timer = 0, iniciou = false;

  const envia = async () => {
    timer = 0;
    if (!ref) return;
    if (!Save.data) { agenda(); return; }   // o App.init ainda nao leu o save
    if (ocupado) { agenda(); return; }
    const json = JSON.stringify(Save.data);
    if (json === enviado) return;
    ocupado = true;
    try { await ref.set({ json, t: +(lsGet(KT) || Date.now()), v: 1 }); enviado = json; } catch (e) { /* tenta na proxima gravacao */ }
    ocupado = false;
  };
  const agenda = () => { if (!timer) timer = setTimeout(envia, 1500); };

  const grava = Save.write;
  Save.write = function () {
    grava.call(this);
    lsSet(KT, Date.now());
    agenda();
  };
  window.addEventListener('visibilitychange', () => { if (document.hidden && timer) { clearTimeout(timer); envia(); } });
  window.addEventListener('load', () => { iniciou = true; window.__NATIVE_SAVE__ = null; });

  const usa = (json, t) => {
    lsSet(Save.key, json); lsSet(KT, t);
    if (!iniciou) { window.__NATIVE_SAVE__ = json; return; }   // o App.init ainda vai ler
    window.__NATIVE_SAVE__ = json;
    Save.load();
    window.__NATIVE_SAVE__ = null;
    try { Snd.setMusic(Save.data.music); Snd.setSfx(Save.data.sfx); } catch (e) { /* audio ainda fechado */ }
    if (typeof WorldMap !== 'undefined') WorldMap.bgKey = '';
  };

  (async () => {
    if (!window.claude || !window.claude.use) return;
    const [db, user] = await Promise.all([claude.use('db'), claude.use('user')]);
    if (!db || !user) return;
    const uid = await user.id();
    if (!uid) return;
    const r = db.doc('data/users/' + uid + '/save');
    let snap;
    try { snap = await r.get(); } catch (e) { return; }
    const nuvem = snap.exists ? snap.data() : null;
    const tLocal = +(lsGet(KT) || 0);
    if (nuvem && nuvem.json && (nuvem.t || 0) > tLocal && App.screen !== 'level') {
      usa(nuvem.json, nuvem.t);
      enviado = nuvem.json;
    } else if (nuvem && nuvem.json) enviado = nuvem.json;
    ref = r;
    // progresso local mais novo (ou a nuvem vazia): sobe
    if (lsGet(Save.key) && (!nuvem || tLocal > (nuvem.t || 0))) envia();
  })();
})();
