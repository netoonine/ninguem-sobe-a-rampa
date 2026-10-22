'use strict';
// Som 100% sintetizado (Web Audio): efeitos, ambiente de cada fase e musica procedural original.
// Ninguem Sobe a Rampa: Brasilia no cerrado, campanha eleitoral, urna, comicio, batucada e bossa (so o estilo, nada copiado).
// Efeitos: Snd.play(nome, vol, x) -- x (0..W) e opcional e vira pan estereo; nome tambem pode vir como { n, x }.

const Snd = {
  ctx: null, master: null, sfxGain: null, musicGain: null, ambGain: null, noiseBuf: null, pinkBuf: null, crackBuf: null,
  musicOn: true, sfxOn: true,
  last: {}, voices: {}, allV: [], ksc: {},
  track: null, nextT: 0, step: 0, timer: null,
  // disparo em andamento: barramento de saida, envio de reverb, altura sorteada e fim do som
  out: null, vsend: null, pm: 1, endT: 0,
  amb: null, ambG: null, ambTimer: null,
  // ultima sirene da Operacao da PF (uma por operacao, nao uma por viatura)
  sirT: -9,

  init() {
    if (this.ctx) { if (this.ctx.state === 'suspended') this.ctx.resume(); return; }
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    const c = this.ctx = new AC();
    this.last = {}; this.voices = {}; this.allV = []; this.ksc = {}; this.sirT = -9;
    this.master = c.createGain(); this.master.gain.value = 0.8;
    const comp = c.createDynamicsCompressor();
    comp.threshold.value = -14; comp.ratio.value = 4;
    // limitador de seguranca: so age em pico de batalha muito cheia
    const lim = c.createDynamicsCompressor();
    lim.threshold.value = -3; lim.knee.value = 0; lim.ratio.value = 20; lim.attack.value = 0.002; lim.release.value = 0.15;
    this.master.connect(comp); comp.connect(lim); lim.connect(c.destination);
    this.sfxGain = c.createGain(); this.sfxGain.gain.value = this.sfxOn ? 0.55 : 0;
    this.musicGain = c.createGain(); this.musicGain.gain.value = this.musicOn ? 0.32 : 0;
    this.sfxGain.connect(this.master); this.musicGain.connect(this.master);
    // nivel de cada trilha (as tres soam por igual por baixo dos efeitos)
    this.mus = c.createGain(); this.mus.gain.value = 1; this.mus.connect(this.musicGain);
    // ambiente passa pelo volume de efeitos (mesmo botao)
    this.ambGain = c.createGain(); this.ambGain.gain.value = 1; this.ambGain.connect(this.sfxGain);
    // ruidos: branco (efeitos), rosa estereo (vento, transito, multidao, chuva) e estalos (fogo, chuva, papel)
    this.noiseBuf = this.makeNoise(2, 1, false);
    this.pinkBuf = this.makeNoise(6, 2, true);
    this.crackBuf = this.makeCrackle(3);
    // reverb curto para a musica
    this.verb = c.createConvolver();
    const vl = c.sampleRate * 1.6;
    const vb = c.createBuffer(2, vl, c.sampleRate);
    for (let ch = 0; ch < 2; ch++) {
      const vd = vb.getChannelData(ch);
      for (let i = 0; i < vl; i++) vd[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / vl, 3);
    }
    this.verb.buffer = vb;
    const vg = c.createGain(); vg.gain.value = 0.28;
    this.verb.connect(vg); vg.connect(this.musicGain);
    // reverb de praca para os efeitos: curto, escuro e macio
    this.sverbIn = c.createConvolver();
    this.sverbIn.buffer = this.makeIR(1.3, 3, 0.75);
    const sg = c.createGain(); sg.gain.value = 0.25;
    this.sverbIn.connect(sg); sg.connect(this.sfxGain);
    if (this.track) this.startTrack(this.track, true);
    if (this.ambG) this.startAmb(this.ambG);
  },

  setMusic(on) {
    this.musicOn = on;
    if (this.musicGain) this.musicGain.gain.setTargetAtTime(on ? 0.32 : 0, this.ctx.currentTime, 0.1);
  },
  setSfx(on) {
    this.sfxOn = on;
    if (this.sfxGain) this.sfxGain.gain.setTargetAtTime(on ? 0.55 : 0, this.ctx.currentTime, 0.05);
  },

  // ------------------------------------------------------------ buffers
  makeNoise(sec, chs, pink) {
    const c = this.ctx, n = Math.floor(c.sampleRate * sec), f = pink ? 2048 : 0;
    const b = c.createBuffer(chs, n - f, c.sampleRate);
    for (let ch = 0; ch < chs; ch++) {
      const d = new Float32Array(n);
      let b0 = 0, b1 = 0, b2 = 0, pk = 0;
      for (let i = 0; i < n; i++) {
        const w = Math.random() * 2 - 1;
        if (!pink) { d[i] = w; continue; }
        b0 = 0.99765 * b0 + w * 0.099046; b1 = 0.963 * b1 + w * 0.2965164; b2 = 0.57 * b2 + w * 1.0526913;
        d[i] = b0 + b1 + b2 + w * 0.1848;
        if (Math.abs(d[i]) > pk) pk = Math.abs(d[i]);
      }
      // rosa: normaliza e emenda o fim no comeco (loop sem estalo)
      if (pink) {
        for (let i = 0; i < n; i++) d[i] *= 0.95 / pk;
        for (let i = 0; i < f; i++) { const a = i / f; d[i] = d[i] * a + d[n - f + i] * (1 - a); }
      }
      b.getChannelData(ch).set(d.subarray(0, n - f));
    }
    return b;
  },
  makeCrackle(sec) {
    const c = this.ctx, n = Math.floor(c.sampleRate * sec), b = c.createBuffer(1, n, c.sampleRate), d = b.getChannelData(0);
    for (let i = 0; i < n; i++) {
      if (Math.random() > 0.0012) continue;
      const a = Math.pow(Math.random(), 2.2), L = 4 + Math.floor(Math.random() * 60);
      for (let j = 0; j < L && i + j < n; j++) d[i + j] += a * (Math.random() * 2 - 1) * Math.exp(-j / (L * 0.25));
    }
    return b;
  },
  makeIR(sec, decay, dark) {
    const c = this.ctx, n = Math.floor(c.sampleRate * sec), b = c.createBuffer(2, n, c.sampleRate), pre = c.sampleRate * 0.006;
    for (let ch = 0; ch < 2; ch++) {
      const d = b.getChannelData(ch);
      let lp = 0;
      for (let i = 0; i < n; i++) {
        const x = i / n;
        lp += (Math.random() * 2 - 1 - lp) * (0.9 - dark * x * 0.85);
        d[i] = lp * Math.pow(1 - x, decay) * Math.min(1, i / pre);
      }
    }
    return b;
  },
  // corda Karplus-Strong pre-calculada (nv variantes por altura, ajuste fino pelo playbackRate)
  ksBuf(f, t60, bright, nv) {
    const key = Math.round(f) + '|' + t60 + '|' + bright + '|' + Math.floor(Math.random() * (nv || 3));
    if (this.ksc[key]) return this.ksc[key];
    // cache cheio: sai so o bloco mais antigo (limpar tudo de uma vez travava um quadro no meio da musica)
    const ks = Object.keys(this.ksc);
    if (ks.length > 150) for (const k of ks.slice(0, 40)) delete this.ksc[k];
    const c = this.ctx, sr = c.sampleRate, n = Math.ceil(sr * (t60 + 0.05));
    const N = Math.max(2, Math.round(sr / f - 0.5));
    const damp = Math.pow(0.001, 1 / (f * t60));
    const line = new Float32Array(N);
    let lp = 0, m = 0;
    const a = 0.12 + 0.88 * bright;
    for (let i = 0; i < N; i++) { lp += (Math.random() * 2 - 1 - lp) * a; line[i] = lp; m += lp; }
    m /= N;
    for (let i = 0; i < N; i++) line[i] -= m;
    const b = c.createBuffer(1, n, sr), d = b.getChannelData(0);
    let p = 0, pk = 1e-6;
    for (let i = 0; i < n; i++) {
      const cur = line[p];
      d[i] = cur;
      if (Math.abs(cur) > pk) pk = Math.abs(cur);
      line[p] = damp * 0.5 * (cur + line[(p + 1) % N]);
      p = (p + 1) % N;
    }
    for (let i = 0; i < n; i++) d[i] *= 0.9 / pk;
    b.f0 = sr / (N + 0.5);
    this.ksc[key] = b;
    return b;
  },
  // curva de saturacao (megafone), igual para qualquer contexto
  shapeC() {
    if (!this.shp) {
      const n = 1024, cv = new Float32Array(n);
      for (let i = 0; i < n; i++) { const x = i / (n - 1) * 2 - 1; cv[i] = Math.tanh(x * 4) / Math.tanh(4); }
      this.shp = cv;
    }
    return this.shp;
  },

  // ------------------------------------------------------------ blocos de sintese
  rn(a, b) { return a + Math.random() * (b - a); },
  pick(a) { return a[Math.floor(Math.random() * a.length)]; },
  // nota em semitons a partir do re (D4): os efeitos tocam em re maior, o tom da musica
  nt(s) { return 293.66 * Math.pow(2, s / 12); },
  // nota MIDI (a musica escreve em MIDI)
  mf(m) { return 440 * Math.pow(2, (m - 69) / 12); },
  WW() { return typeof W !== 'undefined' ? W : 1280; },
  dst(o) { return o.dest || this.out || this.sfxGain; },
  mark(t) { if (t > this.endT) this.endT = t; },
  // envio de reverb: musica usa o dela; efeito usa o do disparo (respeita volume e corte de voz)
  sendV() {
    if (!this.sverbIn) return null;
    if (!this.out) return this.sverbIn;
    if (!this.vsend) {
      this.vsend = this.ctx.createGain();
      this.vsend.gain.value = this.out.gain.value;
      this.vsend.connect(this.sverbIn);
    }
    return this.vsend;
  },
  // ganho novo nasce em 0: o padrao 1.0 vazava uma amostra (estalo) antes do primeiro evento
  gain0() { const g = this.ctx.createGain(); g.gain.value = 0; return g; },
  env(p, t0, dur, vol, a, hold) {
    const A = Math.min(a, dur * 0.5), H = Math.min(hold || 0, dur - A - 0.005);
    p.setValueAtTime(0.0001, t0);
    p.exponentialRampToValueAtTime(Math.max(0.0002, vol), t0 + A);
    if (H > 0) p.setValueAtTime(Math.max(0.0002, vol), t0 + A + H);
    p.exponentialRampToValueAtTime(0.0001, t0 + dur);
  },
  // vibrato num AudioParam de frequencia; dl = atraso ate o vibrato entrar (notas longas de sopro)
  vibr(param, t0, dur, rate, depth, dl) {
    const c = this.ctx, l = c.createOscillator(), lg = c.createGain();
    l.frequency.value = rate;
    if (dl) { lg.gain.setValueAtTime(0, t0); lg.gain.linearRampToValueAtTime(depth, t0 + dl + 0.15); } else lg.gain.value = depth;
    l.connect(lg); lg.connect(param);
    l.start(t0); l.stop(t0 + dur + 0.05);
  },

  tone(type, f0, t0, dur, vol, o = {}) {
    const c = this.ctx, k = o.dest ? 1 : this.pm;
    const osc = c.createOscillator();
    osc.type = type;
    osc.frequency.setValueAtTime(f0 * k, t0);
    if (o.to) osc.frequency.exponentialRampToValueAtTime(Math.max(20, o.to * k), t0 + (o.glide || dur));
    if (o.detune) osc.detune.value = o.detune;
    if (o.vib) this.vibr(osc.frequency, t0, dur, o.vib[0], o.vib[1] * f0 * k);
    const g = this.gain0();
    this.env(g.gain, t0, dur, vol, o.attack || 0.005, o.hold);
    let node = osc;
    if (o.lp) {
      const f = c.createBiquadFilter(); f.type = 'lowpass'; f.frequency.setValueAtTime(o.lp, t0);
      if (o.lpTo) f.frequency.exponentialRampToValueAtTime(o.lpTo, t0 + dur);
      if (o.q) f.Q.value = o.q;
      node.connect(f); node = f;
    }
    node.connect(g);
    g.connect(this.dst(o));
    if (o.verb) { const v = o.dest ? this.verb : this.sendV(); if (v) g.connect(v); }
    osc.start(t0); osc.stop(t0 + dur + 0.05);
    this.mark(t0 + dur);
    return osc;
  },

  // ruido filtrado; o: type, f, fTo, fPts [[t, f]...], q, buf, rate, env [[t, v]...], am [taxa, fundura]
  noise(t0, dur, vol, o = {}) {
    const c = this.ctx, k = o.dest ? 1 : this.pm;
    const src = c.createBufferSource();
    src.buffer = o.buf || this.noiseBuf;
    src.loop = true;
    if (o.rate) src.playbackRate.value = o.rate;
    const f = c.createBiquadFilter();
    f.type = o.type || 'lowpass';
    const fc = x => Math.min(20000, Math.max(20, x * k));
    f.frequency.setValueAtTime(fc(o.f || 1000), t0);
    if (o.fTo) f.frequency.exponentialRampToValueAtTime(fc(o.fTo), t0 + (o.fGlide || dur));
    if (o.fPts) for (const [d, fv] of o.fPts) f.frequency.exponentialRampToValueAtTime(fc(fv), t0 + d);
    f.Q.value = o.q || 0.8;
    const g = this.gain0();
    if (o.env) {
      g.gain.setValueAtTime(0, t0);
      for (const [d, v] of o.env) g.gain.linearRampToValueAtTime(vol * v, t0 + d);
    } else this.env(g.gain, t0, dur, vol, o.attack || 0.004, o.hold);
    src.connect(f);
    let node = f;
    if (o.am) {
      const ag = c.createGain(), l = c.createOscillator(), lg = c.createGain();
      ag.gain.value = 1 - o.am[1]; l.frequency.value = o.am[0]; lg.gain.value = o.am[1];
      l.connect(lg); lg.connect(ag.gain); node.connect(ag); node = ag;
      l.start(t0); l.stop(t0 + dur + 0.05);
    }
    node.connect(g);
    g.connect(this.dst(o));
    if (o.verb) { const v = o.dest ? this.verb : this.sendV(); if (v) g.connect(v); }
    src.start(t0, Math.random() * src.buffer.duration); src.stop(t0 + dur + 0.05);
    this.mark(t0 + dur);
  },

  // corda dedilhada (Karplus-Strong): violao, cavaquinho, elastico
  ks(f, t0, dur, vol, o = {}) {
    const c = this.ctx, base = o.base || f;
    const b = this.ksBuf(base, o.t60 || dur, o.bright == null ? 0.6 : o.bright, o.nv);
    const src = c.createBufferSource();
    src.buffer = b;
    src.playbackRate.value = (f / b.f0) * (o.dest ? 1 : this.pm);
    const g = this.gain0();
    g.gain.setValueAtTime(0, t0);
    g.gain.linearRampToValueAtTime(vol, t0 + 0.002);
    g.gain.setValueAtTime(vol, t0 + dur * 0.75);
    g.gain.linearRampToValueAtTime(0, t0 + dur);
    let node = src;
    if (o.lp) { const fl = c.createBiquadFilter(); fl.type = 'lowpass'; fl.frequency.value = o.lp; fl.Q.value = 0.5; node.connect(fl); node = fl; }
    node.connect(g);
    g.connect(this.dst(o));
    if (o.verb) { const v = o.dest ? this.verb : this.sendV(); if (v) g.connect(v); }
    src.start(t0); src.stop(t0 + dur + 0.05);
    this.mark(t0 + dur);
  },

  // sintese modal: madeira, metal, sino (modos = [razao, amplitude, decaimento])
  modal(f, t0, vol, modes, o = {}) {
    for (const [r, a, d] of modes) this.tone('sine', f * r, t0, d, vol * a, { attack: 0.0015, dest: o.dest });
    if (o.click) this.noise(t0, 0.014, vol * o.click, { type: 'bandpass', f: Math.min(9000, f * 4), q: 0.7, attack: 0.001, dest: o.dest });
  },
  WOOD: [[1, 1, 0.07], [2.76, 0.4, 0.035], [5.4, 0.15, 0.018]],
  STONE: [[1, 1, 0.12], [1.7, 0.5, 0.08], [2.9, 0.3, 0.04]],
  // barril de petroleo: lata grande e oca
  BARREL: [[1, 1, 0.35], [1.58, 0.6, 0.25], [2.35, 0.4, 0.15], [3.2, 0.2, 0.08]],
  // sino da caixa registradora
  BELL: [[1, 1, 0.7], [2.0, 0.4, 0.45], [2.76, 0.3, 0.3], [5.4, 0.1, 0.15]],

  // FM: sinos, joias, notificacoes
  fm(f, t0, dur, vol, o = {}) {
    const c = this.ctx, k = o.dest ? 1 : this.pm, r = o.ratio || 1.4, I = o.index == null ? 2 : o.index;
    const m = c.createOscillator(), mg = c.createGain(), dev = I * f * k * r;
    m.frequency.value = f * k * r;
    mg.gain.setValueAtTime(dev, t0);
    mg.gain.exponentialRampToValueAtTime(Math.max(0.5, dev * 0.06), t0 + dur * 0.6);
    m.connect(mg);
    const car = this.tone('sine', f, t0, dur, vol, o);
    mg.connect(car.frequency);
    m.start(t0); m.stop(t0 + dur + 0.05);
  },

  // metal (trompete, trombone): dois serrotes, filtro que abre no ataque, subidinha de altura e vibrato nas notas longas
  // o: dest, verb, bright (abertura do filtro), to (glissando), attack, hold
  metal(f, t0, dur, vol, o = {}) {
    const c = this.ctx, k = o.dest ? 1 : this.pm, F = f * k, br = o.bright || 5;
    const g = this.gain0();
    this.env(g.gain, t0, dur, vol, o.attack || 0.025, o.hold == null ? dur * 0.45 : o.hold);
    const fl = c.createBiquadFilter(); fl.type = 'lowpass'; fl.Q.value = 1.1;
    fl.frequency.setValueAtTime(Math.min(16000, F * 1.2), t0);
    fl.frequency.exponentialRampToValueAtTime(Math.min(16000, F * br), t0 + 0.05);
    fl.frequency.exponentialRampToValueAtTime(Math.min(16000, F * br * 0.55), t0 + dur);
    for (const dt of [-7, 7]) {
      const osc = c.createOscillator();
      osc.type = 'sawtooth'; osc.detune.value = dt;
      osc.frequency.setValueAtTime(F * 0.97, t0);
      osc.frequency.exponentialRampToValueAtTime(F, t0 + 0.045);
      if (o.to) osc.frequency.exponentialRampToValueAtTime(Math.max(20, o.to * k), t0 + dur);
      if (dur > 0.4) this.vibr(osc.frequency, t0, dur, 5.4, F * 0.007, 0.22);
      osc.connect(fl);
      osc.start(t0); osc.stop(t0 + dur + 0.05);
    }
    fl.connect(g);
    g.connect(this.dst(o));
    if (o.verb) { const v = o.dest ? this.verb : this.sendV(); if (v) g.connect(v); }
    this.mark(t0 + dur);
  },

  // voz por formantes (torcida, coro, megafone); o: to/glide, vib, q, fs (desloca formantes), para (vogal final), lp, dist, verb
  VOG: {
    a: [[730, 1], [1090, 0.5], [2440, 0.22]], e: [[530, 1], [1840, 0.5], [2480, 0.25]], i: [[300, 1], [2250, 0.4], [3000, 0.2]],
    o: [[570, 1], [840, 0.55], [2410, 0.15]], u: [[320, 1], [870, 0.35], [2240, 0.1]],
  },
  voz(f, t0, dur, vol, vg, o = {}) {
    const c = this.ctx, k = o.dest ? 1 : this.pm;
    const osc = c.createOscillator();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(f * k, t0);
    if (o.to) osc.frequency.exponentialRampToValueAtTime(Math.max(30, o.to * k), t0 + (o.glide || dur));
    if (o.vib) this.vibr(osc.frequency, t0, dur, o.vib[0], o.vib[1] * f * k);
    const sum = c.createGain();
    const F = this.VOG[vg] || this.VOG.a, F2 = o.para && this.VOG[o.para], fs = o.fs || 1;
    F.forEach(([ff, a], i) => {
      const bp = c.createBiquadFilter(); bp.type = 'bandpass'; bp.Q.value = o.q || 7;
      bp.frequency.setValueAtTime(ff * fs, t0);
      if (F2) bp.frequency.linearRampToValueAtTime(F2[i][0] * fs, t0 + dur * 0.8);
      const ag = c.createGain(); ag.gain.value = a * 3;
      osc.connect(bp); bp.connect(ag); ag.connect(sum);
    });
    let node = sum;
    // megafone: satura e corta graves e agudos (corneta)
    if (o.dist) {
      const sh = c.createWaveShaper(); sh.curve = this.shapeC();
      const hb = c.createBiquadFilter(); hb.type = 'bandpass'; hb.frequency.value = 1500; hb.Q.value = 0.7;
      node.connect(sh); sh.connect(hb); node = hb;
    }
    const g = this.gain0();
    this.env(g.gain, t0, dur, vol, o.attack || 0.03, o.hold);
    node.connect(g); node = g;
    if (o.lp) { const lp = c.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = o.lp; node.connect(lp); node = lp; }
    node.connect(this.dst(o));
    if (o.verb) { const v = o.dest ? this.verb : this.sendV(); if (v) node.connect(v); }
    osc.start(t0); osc.stop(t0 + dur + 0.05);
    this.mark(t0 + dur);
  },

  // bolha / "pop" de mensagem: seno que sobe rapido enquanto some
  bub(t0, f, dur, vol) { this.tone('sine', f, t0, dur, vol, { to: f * 1.9, glide: dur, attack: 0.003 }); },
  // estalos (fogo, chuva, papel)
  crk(t0, dur, vol, o = {}) { this.noise(t0, dur, vol, Object.assign({ buf: this.crackBuf, type: 'highpass', f: 1500, q: 0.5 }, o)); },
  drum(t, f, v) {
    this.tone('sine', f * 1.5, t, 0.32, v, { to: f, glide: 0.05, attack: 0.002 });
    this.tone('sine', f * 1.59, t, 0.12, v * 0.3, { attack: 0.002 });
    this.noise(t, 0.05, v * 0.35, { f: 900, attack: 0.001 });
  },
  whistle(t, f, v, to) { this.tone('sine', f, t, 0.22, v, { to: to || f, attack: 0.025, vib: [6, 0.008], verb: true }); this.noise(t, 0.18, v * 0.15, { type: 'bandpass', f: f, q: 3 }); },
  // passo de sapato no concreto (nao chamar de "step": e o contador da musica)
  foot(t, v) {
    this.noise(t, 0.05, v, { type: 'bandpass', f: this.rn(700, 1300), q: 0.9, attack: 0.002 });
    this.noise(t, 0.012, v * 0.5, { type: 'highpass', f: 3500, attack: 0.001 });
    this.tone('sine', this.rn(120, 160), t, 0.05, v * 0.4, { to: 80 });
  },
  ping(t, f, v) { this.fm(f, t, 0.2, v, { ratio: 1.41, index: 0.9 }); this.noise(t, 0.01, v * 0.4, { type: 'highpass', f: 5000, attack: 0.001 }); },
  beat(t, v) {
    this.tone('sine', 62, t, 0.17, v, { to: 42, attack: 0.004 });
    this.tone('sine', 56, t + 0.21, 0.22, v * 0.7, { to: 38, attack: 0.004 });
    this.noise(t, 0.07, v * 0.25, { f: 220 });
  },
  chirp(t, v) {
    const f = this.rn(2700, 4000), n = 2 + Math.floor(Math.random() * 4), gap = this.rn(0.07, 0.12);
    for (let i = 0; i < n; i++) this.tone('sine', f, t + i * gap, 0.055, v, { to: f * this.rn(1.15, 1.35), attack: 0.006 });
  },
  // bip eletronico macio (teclas da urna, maquininhas)
  bip(t, f, dur, v, o = {}) {
    this.tone('square', f, t, dur, v, { lp: Math.min(7000, f * 2.5), attack: 0.003, hold: dur * 0.7, dest: o.dest });
    this.tone('sine', f, t, dur, v * 0.6, { attack: 0.003, hold: dur * 0.7, dest: o.dest });
  },
  // o "fim" da urna, na nossa versao: tres bips curtos e um longo uma quarta acima
  urna(t, v) {
    for (let i = 0; i < 3; i++) this.bip(t + i * 0.075, 1560, 0.042, v);
    this.bip(t + 0.23, 2080, 0.2, v * 1.1);
  },
  // caixa registradora: a gaveta (cha) e o sino (ching)
  chaChing(t, v) {
    this.noise(t, 0.06, v * 0.9, { type: 'bandpass', f: 2800, q: 1.1, attack: 0.002 });
    this.modal(1900, t + 0.02, v * 0.35, [[1, 1, 0.04], [2.3, 0.4, 0.02]], { click: 0.4 });
    this.modal(2350, t + 0.075, v * 0.5, this.BELL, { click: 0.2 });
  },
  // carimbo no papel timbrado
  carimbo(t, v) {
    this.tone('sine', 170, t, 0.08, v, { to: 85, attack: 0.002 });
    this.noise(t, 0.05, v * 0.6, { f: 1400, attack: 0.001 });
    this.modal(620, t, v * 0.3, [[1, 1, 0.04], [2.4, 0.3, 0.02]], { click: 0.4 });
  },
  // martelo do juiz (madeira dura)
  martelo(t, v) {
    this.modal(this.rn(360, 400), t, v, [[1, 1, 0.12], [2.6, 0.5, 0.06], [4.2, 0.2, 0.03]], { click: 0.6 });
    this.tone('sine', 120, t, 0.12, v * 0.8, { to: 70 });
  },
  // pano batendo (bandeira, faixa)
  pano(t, v) { this.noise(t, 0.055, v, { type: 'bandpass', f: this.rn(650, 1100), q: 0.8, attack: 0.004 }); },
  // papelada (santinhos, processos, folhas)
  papel(t, dur, v) {
    this.noise(t, dur, v, { type: 'highpass', f: 2200, attack: 0.02, am: [this.rn(18, 30), 0.75] });
    this.crk(t, dur, v * 0.5, { f: 4000 });
  },
  // apito de manifestacao (com a bolinha chiando)
  apito(t, dur, vol, f) {
    f = f || this.rn(2700, 3100);
    this.tone('sine', f, t, dur, vol, { attack: 0.01, hold: dur * 0.6, vib: [this.rn(30, 42), 0.035] });
    this.noise(t, dur, vol * 0.3, { type: 'bandpass', f, q: 4, attack: 0.01, am: [36, 0.8] });
  },
  // buzina de carro (duas notas em terca)
  buzina(t, dur, vol, f) {
    f = f || 420;
    this.tone('square', f, t, dur, vol, { lp: 1600, attack: 0.012, hold: dur * 0.75 });
    this.tone('square', f * 1.26, t, dur, vol * 0.8, { lp: 1600, attack: 0.012, hold: dur * 0.75 });
  },
  // sirene de viatura: sobe e desce
  sirene(t, dur, vol) {
    const c = this.ctx, k = this.pm, osc = c.createOscillator();
    osc.type = 'sawtooth';
    const lo = 640 * k, hi = 1350 * k, per = 0.55;
    osc.frequency.setValueAtTime(lo, t);
    for (let x = 0; x < dur; x += per) {
      osc.frequency.linearRampToValueAtTime(hi, t + x + per * 0.5);
      osc.frequency.linearRampToValueAtTime(lo, t + x + per);
    }
    const fl = c.createBiquadFilter(); fl.type = 'lowpass'; fl.frequency.value = 2400; fl.Q.value = 0.7;
    const g = this.gain0();
    this.env(g.gain, t, dur, vol, 0.04, dur * 0.7);
    osc.connect(fl); fl.connect(g); g.connect(this.dst({}));
    const v = this.sendV(); if (v) g.connect(v);
    osc.start(t); osc.stop(t + dur + 0.05);
    this.mark(t + dur);
  },
  // freada (pneu cantando)
  freada(t, dur, vol) {
    this.noise(t, dur, vol, { type: 'bandpass', f: 2300, fTo: 1600, q: 9, attack: 0.02, hold: dur * 0.5 });
    this.tone('sawtooth', 1150, t, dur, vol * 0.18, { to: 880, lp: 2600, vib: [32, 0.03], attack: 0.02, hold: dur * 0.5 });
  },
  // porta de carro batendo
  porta(t, vol) {
    this.tone('sine', 95, t, 0.18, vol, { to: 55, attack: 0.002 });
    this.noise(t, 0.09, vol * 0.5, { f: 900, attack: 0.001 });
    this.modal(1500, t + 0.01, vol * 0.2, [[1, 1, 0.05], [2.6, 0.4, 0.03]], { click: 0.3 });
  },
  // notificacao de celular (generica): 0 plim de duas notas, 1 sininho, 2 dois pops, 3 bip
  notif(t, v, k) {
    k = k == null ? Math.floor(Math.random() * 4) : k;
    if (k === 0) { this.fm(1568, t, 0.3, v, { ratio: 2, index: 0.7 }); this.fm(2093, t + 0.09, 0.35, v, { ratio: 2, index: 0.7 }); }
    else if (k === 1) this.fm(1760, t, 0.45, v * 1.1, { ratio: 3.01, index: 1 });
    else if (k === 2) { this.bub(t, 700, 0.05, v * 3.1); this.bub(t + 0.1, 950, 0.05, v * 3.1); }
    else this.bip(t, 2200, 0.05, v * 0.67);
  },
  // celular vibrando na mesa
  celVibra(t, v) { for (let i = 0; i < 2; i++) this.tone('sawtooth', 165, t + i * 0.45, 0.32, v, { lp: 700, vib: [11, 0.04], attack: 0.01, hold: 0.25 }); },
  // camera do celular
  foto(t, v) {
    this.noise(t, 0.012, v, { type: 'highpass', f: 3000, attack: 0.001 });
    this.modal(2600, t, v * 0.4, [[1, 1, 0.02]]);
    this.noise(t + 0.06, 0.015, v * 0.8, { type: 'highpass', f: 2500, attack: 0.001 });
    this.modal(2200, t + 0.06, v * 0.3, [[1, 1, 0.02]]);
  },
  // moto acelerando (motociata) e o estouro do escapamento
  moto(t, dur, v) {
    this.tone('sawtooth', 46, t, dur, v, { to: 105, glide: dur * 0.55, lp: 600, lpTo: 1400, vib: [26, 0.1], attack: 0.05, hold: dur * 0.4 });
    this.tone('square', 92, t, dur, v * 0.35, { to: 210, glide: dur * 0.55, lp: 900, attack: 0.05, hold: dur * 0.4 });
    this.noise(t, dur, v * 0.5, { buf: this.pinkBuf, type: 'bandpass', f: 300, fTo: 700, q: 1, attack: 0.05 });
    this.noise(t + dur * 0.9, 0.05, v * 0.8, { f: 1500, attack: 0.001 });
    this.tone('sine', 90, t + dur * 0.9, 0.1, v, { to: 50 });
  },
  // fogos: o assobio subindo, o estouro e as faiscas
  fogos(t, v) {
    this.tone('sine', 900, t, 0.45, v * 0.15, { to: 2600, glide: 0.45, attack: 0.05, vib: [14, 0.02] });
    const b = t + 0.45;
    this.noise(b, 0.35, v, { f: 3000, fTo: 250, attack: 0.002 });
    this.tone('sine', 75, b, 0.3, v * 0.8, { to: 40 });
    this.crk(b + 0.05, 0.7, v * 0.6, { f: 2500 });
  },
  // corrente de ouro: elos tilintando
  corrente(t, v) {
    for (let i = 0; i < 5; i++) this.modal(this.rn(2600, 3800), t + i * this.rn(0.018, 0.035), v * (1 - i * 0.12), [[1, 1, 0.07], [2.41, 0.45, 0.05], [3.93, 0.2, 0.03]], { click: 0.2 });
  },
  barril(t, v, f) { this.modal(f || this.rn(200, 240), t, v, this.BARREL, { click: 0.3 }); },

  // torcida / multidao: varias vozes em vogal aberta, o chiado do povo e palmas
  // o: n (vozes), vg (vogais), lp (longe), cai (desanimo: a voz desce), para (vogal final), palmas (quantas)
  torcida(t, dur, vol, o = {}) {
    const n = o.n || 7, vgs = o.vg || ['e', 'a'];
    for (let i = 0; i < n; i++) {
      const fem = Math.random() < 0.45, f = fem ? this.rn(210, 300) : this.rn(115, 175), d0 = this.rn(0, 0.15), d = dur * this.rn(0.75, 1);
      this.voz(f * (o.cai ? 1.15 : 0.92), t + d0, d, vol * this.rn(0.6, 1), this.pick(vgs), {
        to: f * (o.cai ? 0.75 : 1.12), glide: d * (o.cai ? 0.9 : 0.35), vib: [this.rn(4.5, 7), 0.025],
        attack: this.rn(0.06, 0.2), hold: d * 0.3, q: 5, fs: fem ? 1.12 : 1, lp: o.lp || 3200, para: o.para, verb: true,
      });
    }
    this.noise(t, dur, vol * 0.6, { buf: this.pinkBuf, type: 'bandpass', f: o.lp ? Math.min(900, o.lp * 0.6) : 1100, q: 0.6, attack: dur * 0.2, hold: dur * 0.3 });
    if (o.palmas) for (let i = 0; i < o.palmas; i++) this.noise(t + Math.random() * dur * 0.8, 0.012, vol * this.rn(0.4, 0.9), { type: 'bandpass', f: this.rn(1400, 2600), q: 1.2, attack: 0.001 });
  },
  // megafone: silabas curtas, voz rouca e corneta
  megafone(t, dur, vol, o = {}) {
    const f0 = o.f || this.rn(150, 210);
    let tt = t;
    while (tt < t + dur) {
      const d = this.rn(0.09, 0.2);
      this.voz(f0 * this.rn(0.9, 1.2), tt, d, vol, this.pick(['a', 'e', 'o', 'a', 'i']), { to: f0 * this.rn(0.85, 1.1), q: 4, dist: true, lp: o.lp || 3400, attack: 0.012, hold: d * 0.5 });
      tt += d + this.rn(0.01, 0.06);
    }
  },

  // ------------------------------------------------------------ disparo
  // gap: intervalo minimo; max: vozes do mesmo efeito; pj: variacao de altura (semitons; 0 nos que tocam notas da escala);
  // vj: variacao de volume; g: ajuste de ganho (medido com OfflineAudioContext, ver tools/sons.html); pri: toca mesmo com a praca cheia
  FXG: 2.2,
  meta: {
    // interface
    click: { g: 1.28, gap: 0.04, max: 2, pj: 0.3, pri: 1 }, hover: { g: 1.15, gap: 0.05, max: 1, pj: 0.3 }, error: { g: 0.286, pj: 0, pri: 1 },
    chime: { g: 0.746, pj: 0, pri: 1 }, open: { g: 1.07, pj: 0, pri: 1 }, stars: { g: 0.65, pj: 0, pri: 1 }, upgrade: { g: 0.918, pj: 0, pri: 1 },
    sell: { g: 0.715, pj: 0.3, pri: 1 }, coin: { g: 0.696, gap: 0.08, max: 2, pj: 0.3 }, victory: { g: 0.557, pj: 0, vj: 0, pri: 1 },
    defeat: { g: 0.93, pj: 0, vj: 0, pri: 1 }, levelup: { g: 0.7, pj: 0, pri: 1 }, titleIn: { g: 0.694, pj: 0, vj: 0, pri: 1 },
    heroPick: { g: 1.37, pj: 0, max: 2, pri: 1 }, trailOpen: { g: 0.781, pj: 0, pri: 1 }, mapStep: { g: 0.797, gap: 0.1, max: 2, pj: 2, vj: 0.25 },
    flagDrop: { g: 0.802, pj: 0.5, pri: 1 }, talent: { g: 1.35, pj: 0, pri: 1 }, heroGo: { g: 0.51, pj: 0, pri: 1 }, heroNew: { g: 0.575, pj: 0, pri: 1 },
    mode_normal: { g: 1.24, pj: 0, pri: 1 }, mode_chal: { g: 0.36, pri: 1 }, mode_heroic: { g: 0.21, pj: 0, pri: 1 }, mode_iron: { g: 0.64, pri: 1 },
    mode_endless: { g: 0.586, pri: 1 },
    // torres
    arrow: { g: 5.61, gap: 0.04, max: 4, pj: 1.2 }, dart: { g: 3.69, gap: 0.05, max: 3, pj: 1.5 }, ballista: { g: 1.23, gap: 0.08, max: 2 },
    magic: { g: 1.2, gap: 0.06, max: 3, pj: 0 }, orbBig: { g: 0.861, max: 2, pj: 0 }, arcane: { g: 1.87, gap: 0.05, max: 3, pj: 0 },
    arcaneBig: { g: 0.9, max: 2, pj: 0 }, zap: { g: 1.79, gap: 0.07, max: 3, pj: 1.5 }, beam: { g: 1.66, gap: 0.3, max: 1 }, flash: { g: 1.08, pj: 0 },
    launch: { g: 0.669, gap: 0.08, max: 2, pj: 1 }, boom: { g: 0.6, gap: 0.07, max: 3, pj: 1 }, boomBig: { g: 0.618, gap: 0.12, max: 2, pri: 1 },
    fire: { g: 1.97, max: 2 }, splash: { g: 1.35, gap: 0.08, max: 3, pj: 1.5 }, slam: { g: 0.657, max: 2 }, rumble: { g: 0.662, max: 2 },
    water: { g: 3.35, gap: 0.06, max: 3, pj: 2 }, jet: { g: 1.6, gap: 0.08, max: 2, pj: 1.5 }, geyser: { g: 0.62, max: 2 },
    freeze: { g: 1.44, max: 2, pj: 0 }, gust: { g: 2.25, gap: 0.1, max: 2, pj: 1.5 }, sand: { g: 1.54, gap: 0.1, max: 2, pj: 1 },
    tornado: { g: 1.34, max: 2 }, drums: { g: 0.566, gap: 0.4, max: 1 }, mark: { g: 1.97, pj: 0.3 }, merc: { g: 1.27, max: 1 },
    rally: { g: 0.736, pj: 0.3 }, hammer: { g: 1.8, gap: 0.09, max: 3, pj: 1 }, build: { g: 0.81, pri: 1 }, built: { g: 0.453, pj: 0, pri: 1 },
    ability: { g: 0.601, pj: 0, pri: 1 }, rubble: { g: 0.74, pri: 1 }, gate: { g: 0.923, pri: 1 }, palm: { g: 1.46, max: 2, pj: 1 },
    herbHeal: { g: 1.0, max: 2, pj: 0 },
    // unidades e herois
    sword: { g: 3.13, gap: 0.06, max: 3, pj: 1.5 }, clang: { g: 1.79, gap: 0.12, max: 2, pj: 1 }, claw: { g: 0.913, max: 2 }, hawk: { g: 0.609, pj: 0, pri: 1 },
    whirl: { g: 1.19, pri: 1 }, heroMove: { g: 2.05, gap: 0.12, max: 1, pj: 0, pri: 1 }, heroDie: { g: 0.593, pj: 0, pri: 1 },
    heroBack: { g: 0.891, pj: 0, pri: 1 }, unitDie: { g: 1.12, gap: 0.1, max: 2 }, bless: { g: 0.55, pj: 0, pri: 1 },
    herb: { g: 9.57, gap: 0.1, max: 2, pj: 1.5 }, herbHit: { g: 1.74, gap: 0.08, max: 2, pj: 0 }, beastCall: { g: 1.4, pri: 1 },
    trail: { g: 1.23, pri: 1 }, flare: { g: 0.791, pri: 1 }, fireTrail: { g: 0.407, max: 2 }, ember: { g: 5.9, gap: 0.1, max: 2, pj: 1.5 },
    // adversarios
    die: { g: 2.11, gap: 0.04, max: 4, pj: 0, vj: 0.15 }, bigDie: { g: 0.993, max: 2, pj: 0 }, bossDie: { g: 0.713, max: 2, pri: 1 },
    bossFreed: { g: 0.8, max: 1, pj: 0, vj: 0, pri: 1 }, enemyHit: { g: 2.86, gap: 0.08, max: 3, pj: 2 }, leak: { g: 0.552, pj: 0, pri: 1 },
    heal: { g: 1.31, max: 2, pj: 0 }, warcry: { g: 1.02, max: 2 }, throw: { g: 7.1, gap: 0.1, max: 2, pj: 1.5 }, sabotage: { g: 0.194, max: 2 },
    firestorm: { g: 1.99, max: 2, pri: 1 }, splat: { g: 0.393, gap: 0.1, max: 2, pj: 1.5 }, thud: { g: 0.775, max: 2, pj: 1 },
    // ondas, operacoes e eventos
    horn: { g: 0.413, pj: 0, vj: 0, pri: 1 }, hornBig: { g: 0.554, pj: 0, vj: 0, pri: 1 }, thunder: { g: 0.85, max: 6, pri: 1 },
    riders: { g: 1.12, pj: 0, pri: 1 }, stampede: { g: 0.941, pri: 1 }, charmReady: { g: 0.94, pj: 0, pri: 1 }, windWarn: { g: 1.22, pri: 1 },
    wind: { g: 3.29, max: 2 }, stormStart: { g: 0.4, pri: 1 }, stormEnd: { g: 0.361, pri: 1 }, thunderFar: { g: 0.8, max: 2 },
    floodWarn: { g: 0.775, pri: 1 }, flood: { g: 0.954, pri: 1 }, floodEnd: { g: 1.17, pj: 0, pri: 1 }, bossCome: { g: 0.247, pj: 0, pri: 1 },
    heartBeat: { g: 0.639, max: 2, pj: 0.3, pri: 1 }, heartSmoke: { g: 0.706, pri: 1 }, heartBack: { g: 0.635, pri: 1 },
    heartFreed: { g: 0.462, pj: 0, vj: 0, pri: 1 }, nightFall: { g: 1.06, pj: 0, pri: 1 }, dawn: { g: 1.08, pj: 0, pri: 1 },
    // cidade e cerrado (ambiente)
    birdChirp: { g: 0.82, pj: 2 }, bemtevi: { g: 0.492, pj: 1 }, cicada: { g: 1.03, pj: 1 }, cricket: { g: 0.97, pj: 0.5 },
    pombo: { g: 0.513, pj: 1.5 }, revoada: { g: 1.86, pj: 1 }, carro: { g: 0.543, pj: 2 }, buzinaLonge: { g: 0.224, pj: 1 }, onibus: { g: 0.178, pj: 1 },
    burburinho: { g: 0.639, pj: 1 }, torcidaLonge: { g: 0.188, pj: 0.5 }, apitoLonge: { g: 0.2, pj: 1 }, megafoneLonge: { g: 0.544, pj: 1 },
    bandeira: { g: 3.75, pj: 1 }, notif: { g: 0.46, pj: 0 }, celular: { g: 0.473, pj: 0.5 },
  },
  play(name, vol, x) {
    if (!this.ctx || !this.sfxOn) return;
    if (name && typeof name === 'object') { x = name.x; name = name.n; }
    const fn = this.fx[name];
    if (!fn) return;
    const c = this.ctx, now = c.currentTime, M = this.meta[name] || {};
    if (this.last[name] && now - this.last[name] < (M.gap || 0.03)) return;
    // limite global: com muita coisa soando, os efeitos miudos ficam de fora
    this.allV = this.allV.filter(e => e > now);
    if (this.allV.length >= 36 && !M.pri) return;
    this.last[name] = now;
    // limite de vozes por efeito: a mais antiga sai com um fade curto
    const vs = (this.voices[name] || []).filter(v => v.end > now);
    if (vs.length >= (M.max || 3)) {
      const o = vs.shift();
      o.bus.gain.setTargetAtTime(0, now, 0.02);
      if (o.vs) o.vs.gain.setTargetAtTime(0, now, 0.02);
    }
    this.voices[name] = vs;
    // barramento do disparo: volume (com variacao) e pan pela posicao
    const bus = c.createGain();
    bus.channelCount = 1; bus.channelCountMode = 'explicit';
    bus.gain.value = (vol == null ? 1 : vol) * this.FXG * (M.g || 1) * (1 + (Math.random() * 2 - 1) * (M.vj == null ? 0.1 : M.vj));
    if (c.createStereoPanner) {
      const p = c.createStereoPanner();
      // pan suave (no maximo +-0,6) para nao cansar no fone
      p.pan.value = x == null ? 0 : Math.max(-0.6, Math.min(0.6, (x / this.WW() - 0.5) * 1.2));
      bus.connect(p); p.connect(this.sfxGain);
    } else bus.connect(this.sfxGain);
    this.out = bus; this.vsend = null; this.endT = now;
    this.pm = Math.pow(2, (Math.random() * 2 - 1) * (M.pj == null ? 0.5 : M.pj) / 12);
    // erro de som nunca trava o jogo (mas aparece no console)
    try { fn.call(this, now + 0.005, 1); } catch (e) { console.error('som ' + name + ': ' + e.message); } finally {
      vs.push({ bus, vs: this.vsend, end: this.endT + 0.05 });
      this.allV.push(this.endT + 0.05);
      this.out = null; this.vsend = null; this.pm = 1;
    }
  },

  // eventos do jogo (g.events) que ganham som proprio
  event(kind) {
    const m = { storm: 'stormStart', stormEnd: 'stormEnd', stormWarn: 'thunderFar', floodWarn: 'floodWarn', flood: 'flood', floodEnd: 'floodEnd', heartFreed: 'heartFreed' }[kind];
    if (m) this.play(m);
  },

  fx: {
    // ---------------------------------------------------------- interface (papel timbrado e teclas da urna)
    // clique: tecla de plastico da urna
    click(t) { this.modal(this.rn(1250, 1350), t, 0.16, [[1, 1, 0.04], [2.4, 0.3, 0.02]], { click: 0.25 }); this.tone('sine', 180, t, 0.03, 0.06, { to: 120 }); },
    hover(t) { this.tone('sine', 1900, t, 0.035, 0.05, { to: 1600, attack: 0.004 }); },
    // erro: CORRIGE, dois bips graves descendo
    error(t) { this.bip(t, 440, 0.09, 0.09); this.bip(t + 0.13, 330, 0.14, 0.09); },
    // aviso novo: duas notas de sino suaves
    chime(t) { this.fm(this.nt(17), t, 0.9, 0.09, { ratio: 3.5, index: 1.4, verb: true }); this.fm(this.nt(24), t + 0.1, 1.0, 0.08, { ratio: 3.5, index: 1.2, verb: true }); },
    // abrir painel: folha de papel timbrado e um dedilhado
    open(t) { this.papel(t, 0.16, 0.06); this.noise(t, 0.12, 0.05, { type: 'bandpass', f: 900, fTo: 2600, q: 1.2, attack: 0.03 }); this.ks(this.nt(12), t + 0.02, 0.35, 0.18, { bright: 0.5, verb: true }); },
    // estrela da fase: carimbo e um brilho
    stars(t) {
      this.carimbo(t, 0.22);
      this.fm(this.nt(31), t + 0.04, 0.8, 0.1, { ratio: 2, index: 1.5, verb: true });
      this.fm(this.nt(36), t + 0.1, 0.7, 0.05, { ratio: 2, index: 1, verb: true });
    },
    // melhoria: cavaquinho subindo e o bip de confirmacao
    upgrade(t) {
      [12, 16, 19, 24].forEach((s, i) => this.ks(this.nt(s), t + i * 0.06, 0.45, 0.14, { bright: 0.7, verb: true }));
      this.bip(t + 0.3, 2080, 0.14, 0.035);
    },
    // vender: desmonta (madeira), cha-ching e moedas
    sell(t) { this.modal(520, t, 0.12, this.WOOD, { click: 0.2 }); this.chaChing(t + 0.08, 0.12); [0, 0.07].forEach((d, i) => this.ping(t + 0.32 + d, 1900 + i * 260, 0.05)); },
    // verba entrando: cha-ching
    coin(t) { this.chaChing(t, 0.1); this.ping(t + 0.13, 2640, 0.04); },
    // vitoria: fanfarra de comicio, surdo, a torcida e fogos
    victory(t) {
      const N = [[0, 7, 0.12], [0.14, 7, 0.12], [0.28, 12, 0.12], [0.42, 16, 0.45], [0.95, 14, 0.12], [1.09, 16, 0.12], [1.23, 19, 1.1]];
      for (const [d, s, l] of N) { this.metal(this.nt(s), t + d, l, 0.07, { verb: true }); this.metal(this.nt(s - 12), t + d, l, 0.035); }
      [0, 4, 7].forEach(s => this.metal(this.nt(s), t + 1.23, 1.1, 0.03, { verb: true }));
      this.surdo(t, 0.3, true); this.surdo(t + 0.42, 0.3, true); this.surdo(t + 1.23, 0.4, true);
      this.caixa(t + 0.95, 0.05); this.caixa(t + 1.09, 0.05);
      this.prato(t + 1.23, 0.04, 1.4);
      this.torcida(t + 1.2, 1.8, 0.035, { n: 8, palmas: 30 });
      this.fogos(t + 1.6, 0.12);
    },
    // derrota: buzina triste e macia descendo, e o povo desanimado
    defeat(t) {
      [[0, -5, 0.3], [0.34, -6, 0.3], [0.68, -7, 0.3], [1.02, -8, 1.2]].forEach(([d, s, l]) => this.metal(this.nt(s), t + d, l, 0.08, { bright: 2.2, verb: true }));
      this.torcida(t + 0.9, 1.6, 0.025, { n: 6, vg: ['o', 'u'], cai: true, lp: 1800 });
    },
    // heroi sobe de nivel: brilho subindo e um "ee!" curtinho
    levelup(t) {
      [12, 16, 19, 24, 28].forEach((s, i) => this.fm(this.nt(s), t + i * 0.07, 0.6, 0.08, { ratio: 2.01, index: 1.2, verb: true }));
      this.torcida(t + 0.2, 0.6, 0.02, { n: 4 });
    },
    // logo entrando na tela de inicio: sobe, bate como carimbo e abre um acorde de cavaco e metais
    titleIn(t) {
      this.noise(t, 0.35, 0.07, { type: 'bandpass', f: 500, fTo: 2400, q: 1, attack: 0.15 });
      this.carimbo(t + 0.32, 0.3);
      [-12, -5, 0, 4, 7, 16].forEach((s, i) => this.ks(this.nt(s), t + 0.34 + i * 0.03, 1.0, 0.11, { bright: 0.6, verb: true }));
      [0, 4, 7].forEach(s => this.metal(this.nt(s), t + 0.36, 0.7, 0.03, { verb: true }));
      this.fm(this.nt(24), t + 0.45, 0.8, 0.05, { ratio: 3.5, index: 1, verb: true });
    },
    // heroi em vista na tela de herois: whoosh suave e acorde curto e brilhante
    heroPick(t) {
      this.noise(t, 0.25, 0.07, { type: 'bandpass', f: 400, fTo: 3000, q: 1, attack: 0.08 });
      [12, 16, 19, 24].forEach((s, i) => this.ks(this.nt(s), t + 0.12 + i * 0.03, 0.48, 0.12, { bright: 0.75, verb: true }));
      this.fm(this.nt(31), t + 0.16, 0.42, 0.04, { ratio: 2, index: 1.2, verb: true });
    },
    // caminho novo no mapa: passos no concreto e o bip no fim
    trailOpen(t) {
      [12, 16, 19, 24, 28].forEach((s, i) => {
        const tt = t + i * 0.2;
        this.foot(tt, 0.1);
        this.fm(this.nt(s), tt + 0.02, 0.3, 0.025, { ratio: 2.01, index: 0.8 });
      });
      this.bip(t + 1.05, 1760, 0.12, 0.035);
      this.fm(this.nt(31), t + 1.05, 0.5, 0.06, { ratio: 2, index: 1.5, verb: true });
    },
    // passo leve do heroi no mapa (toca a cada ~0,28 s)
    mapStep(t) { this.foot(t, 0.12); },
    // bandeira da fase nova cai: mastro de metal e o pano batendo
    flagDrop(t) {
      this.noise(t, 0.12, 0.05, { type: 'bandpass', f: 900, fTo: 1600, q: 1, attack: 0.03 });
      this.modal(520, t + 0.12, 0.16, [[1, 1, 0.25], [2.76, 0.4, 0.12], [5.1, 0.2, 0.05]], { click: 0.3 });
      this.pano(t + 0.14, 0.1); this.pano(t + 0.22, 0.07); this.pano(t + 0.3, 0.05);
      this.modal(540, t + 0.3, 0.05, [[1, 1, 0.15], [2.76, 0.3, 0.08]]);
    },
    // talento escolhido
    talent(t) { this.ks(this.nt(16), t, 0.4, 0.12, { bright: 0.7, verb: true }); this.ks(this.nt(24), t + 0.07, 0.5, 0.12, { bright: 0.7, verb: true }); this.fm(this.nt(31), t + 0.1, 0.4, 0.03, { ratio: 2, index: 1 }); },
    // "Levar a batalha": surdo e um golpe dos metais
    heroGo(t) {
      this.surdo(t, 0.35, true);
      [0, 4, 7, 12].forEach(s => this.metal(this.nt(s), t + 0.02, 0.35, 0.04, { verb: true }));
      this.surdo(t + 0.2, 0.3, false);
    },
    // heroi novo liberado: o povo comemora
    heroNew(t) {
      this.torcida(t, 0.9, 0.035, { n: 6, palmas: 14 });
      [19, 24, 28].forEach((s, i) => this.fm(this.nt(s), t + 0.1 + i * 0.1, 0.8, 0.06, { ratio: 2.01, index: 1.3, verb: true }));
    },
    // abas de modo da fase
    mode_normal(t) { this.fx.click.call(this, t); this.ks(this.nt(12), t, 0.3, 0.1, { bright: 0.5 }); },
    mode_chal(t) { this.surdo(t, 0.3, false); this.surdo(t + 0.11, 0.3, true); },
    mode_heroic(t) { this.metal(this.nt(-9), t, 0.45, 0.1, { bright: 4 }); this.surdo(t, 0.3, true); },
    mode_iron(t) { this.martelo(t, 0.22); this.tone('sine', 90, t, 0.2, 0.15, { to: 50 }); },
    // Recontagem: a maquininha contando e a papelada
    mode_endless(t) { for (let i = 0; i < 5; i++) this.bip(t + i * 0.08, 1400 + i * 60, 0.04, 0.03); this.papel(t, 0.5, 0.04); },

    // ---------------------------------------------------------- torres
    // Mensalinho: envelope atirado (papel cortando o ar e o peteleco)
    arrow(t) {
      this.noise(t, 0.09, 0.12, { type: 'bandpass', f: 2600, fTo: 1200, q: 1.4, attack: 0.006 });
      this.noise(t, 0.02, 0.07, { type: 'highpass', f: 3500, attack: 0.001 });
      this.tone('sine', 520, t, 0.04, 0.04, { to: 340, attack: 0.002 });
    },
    // Dolar na Cueca: o elastico estala e as notas saem
    dart(t) {
      this.tone('sine', 260, t, 0.09, 0.09, { to: 170, vib: [45, 0.06], attack: 0.002 });
      this.noise(t, 0.06, 0.1, { type: 'bandpass', f: 3000, fTo: 1800, q: 1.3, attack: 0.003 });
    },
    // Mensalao: os fechos da mala e a mala pesada voando
    ballista(t) {
      this.modal(1900, t, 0.08, [[1, 1, 0.03], [2.3, 0.4, 0.02]], { click: 0.3 });
      this.modal(2300, t + 0.04, 0.06, [[1, 1, 0.03], [2.3, 0.4, 0.02]], { click: 0.2 });
      this.noise(t + 0.03, 0.25, 0.14, { type: 'bandpass', f: 900, fTo: 350, q: 1, attack: 0.03 });
      this.tone('sine', 130, t + 0.03, 0.15, 0.12, { to: 80 });
    },
    // Joias da Arabia: brilho FM numa nota da escala e um sopro que sobe
    magic(t) {
      this.fm(this.nt(this.pick([24, 28, 31])), t, 0.35, 0.07, { ratio: 2.01, index: 1.2, verb: true });
      this.tone('sine', 500, t, 0.25, 0.08, { to: 1100, glide: 0.2, attack: 0.02 });
      this.noise(t, 0.22, 0.04, { type: 'bandpass', f: 1500, fTo: 4000, q: 2, attack: 0.03 });
    },
    orbBig(t) {
      this.tone('sine', 160, t, 0.5, 0.2, { to: 480, glide: 0.4, attack: 0.05 });
      this.noise(t, 0.45, 0.06, { type: 'bandpass', f: 700, fTo: 2600, q: 2, attack: 0.08 });
      [19, 24].forEach((s, i) => this.fm(this.nt(s), t + 0.08 + i * 0.07, 0.6, 0.06, { ratio: 2.01, index: 1.5, verb: true }));
    },
    // joia acertando: tilim de cristal e um baque leve
    arcane(t) {
      this.noise(t, 0.07, 0.1, { type: 'bandpass', f: 2200, q: 1.2, attack: 0.002 });
      this.fm(this.nt(this.pick([19, 24])), t, 0.3, 0.05, { ratio: 3.01, index: 1, verb: true });
      this.tone('sine', 200, t, 0.12, 0.12, { to: 100 });
    },
    arcaneBig(t) {
      this.tone('sine', 120, t, 0.5, 0.3, { to: 45 });
      this.noise(t, 0.45, 0.16, { f: 1800, fTo: 200 });
      [12, 19, 24].forEach((s, i) => this.fm(this.nt(s), t + 0.02 + i * 0.04, 0.8, 0.05, { ratio: 2.01, index: 1.2, verb: true }));
    },
    // Corrente de Ouro: elos tilintando e o choque que salta
    zap(t) {
      this.corrente(t, 0.06);
      this.tone('sawtooth', 70, t, 0.16, 0.05, { lp: 1600, lpTo: 400, vib: [38, 0.3] });
      this.crk(t, 0.12, 0.15, { f: 2500, rate: 1.6 });
    },
    // Relogio de Ouro: tique-taque e um zumbido quente em quinta
    beam(t) {
      this.modal(3100, t, 0.07, [[1, 1, 0.025], [2.2, 0.3, 0.012]], { click: 0.3 });
      this.modal(2500, t + 0.3, 0.06, [[1, 1, 0.025], [2.2, 0.3, 0.012]], { click: 0.3 });
      this.tone('sine', 220, t, 0.7, 0.04, { attack: 0.15 }); this.tone('sine', 330, t, 0.7, 0.025, { attack: 0.2, verb: true });
    },
    // Clarao de Diamante: o flash carrega, dispara e o diamante brilha
    flash(t) {
      this.tone('sine', 1800, t, 0.3, 0.03, { to: 5200, glide: 0.28, attack: 0.05 });
      this.foto(t + 0.28, 0.12);
      this.noise(t + 0.29, 0.06, 0.12, { type: 'highpass', f: 2500, attack: 0.001 });
      this.fm(this.nt(31), t + 0.3, 0.7, 0.06, { ratio: 2, index: 2, verb: true });
    },
    // Petrolao: o tubo dispara o barril (tum) e a lata ressoa
    launch(t) {
      this.tone('sine', 140, t, 0.2, 0.3, { to: 55, attack: 0.003 });
      this.noise(t, 0.12, 0.12, { f: 1200, fTo: 300, attack: 0.002 });
      this.barril(t + 0.01, 0.12);
    },
    // barril de petroleo caindo: lata, estouro e oleo borbulhando
    boom(t) {
      this.barril(t, 0.16, this.rn(180, 220));
      this.tone('sine', 100, t, 0.4, 0.4, { to: 40 });
      this.noise(t, 0.45, 0.28, { f: 900, fTo: 120 });
      for (let i = 0; i < 3; i++) this.bub(t + 0.08 + Math.random() * 0.2, this.rn(150, 300), 0.09, 0.04);
    },
    boomBig(t) {
      this.barril(t, 0.18, this.rn(150, 175));
      this.tone('sine', 85, t, 0.7, 0.5, { to: 28 });
      this.noise(t, 0.9, 0.4, { f: 1100, fTo: 80 });
      this.crk(t + 0.04, 0.5, 0.15, { f: 1000 });
      for (let i = 0; i < 5; i++) this.bub(t + 0.1 + Math.random() * 0.35, this.rn(120, 260), this.rn(0.08, 0.12), 0.04);
    },
    // Oleo em Chamas: o fogo pega (fuuump), chama e estalos
    fire(t) {
      this.noise(t, 0.35, 0.18, { type: 'bandpass', f: 500, fTo: 1800, q: 0.7, attack: 0.03 });
      this.noise(t + 0.1, 0.9, 0.16, { buf: this.pinkBuf, f: 600, fTo: 250, attack: 0.15 });
      this.crk(t + 0.05, 0.9, 0.3, { f: 1800 });
    },
    // agua caindo: chape, ploft grave e bolhas
    splash(t) {
      this.noise(t, 0.3, 0.16, { type: 'bandpass', f: 1600, fTo: 500, q: 0.9, attack: 0.005 });
      this.tone('sine', 140, t, 0.12, 0.12, { to: 70 });
      for (let i = 0; i < 5; i++) this.bub(t + 0.03 + Math.random() * 0.25, this.rn(350, 1100), this.rn(0.04, 0.09), this.rn(0.02, 0.05));
    },
    // Sonda do Pre-Sal (e brutamontes): pancada no chao com a lataria
    slam(t) {
      this.tone('sine', 70, t, 0.5, 0.5, { to: 30 });
      this.noise(t, 0.4, 0.3, { f: 500, fTo: 90 });
      this.modal(160, t, 0.2, this.STONE, { click: 0.3 });
      this.modal(this.rn(600, 700), t, 0.07, [[1, 1, 0.15], [2.7, 0.4, 0.08]], { click: 0.3 });
    },
    rumble(t) {
      this.noise(t, 1.4, 0.45, { buf: this.pinkBuf, f: 220, fTo: 60, attack: 0.15 });
      this.tone('sine', 46, t, 1.2, 0.3, { to: 32, attack: 0.1 });
      this.crk(t + 0.1, 1.0, 0.12, { type: 'bandpass', f: 900, q: 0.8 });
    },
    // Lava a Jato: jato da lavadora com o motorzinho
    water(t) {
      this.noise(t, 0.16, 0.12, { type: 'bandpass', f: 1900, fTo: 800, q: 1.1, attack: 0.01 });
      this.tone('sawtooth', 98, t, 0.18, 0.025, { lp: 500 });
      for (let i = 0; i < 3; i++) this.bub(t + 0.05 + Math.random() * 0.12, this.rn(500, 1300), this.rn(0.03, 0.06), this.rn(0.02, 0.04));
    },
    jet(t) {
      this.noise(t, 0.3, 0.16, { type: 'bandpass', f: 2600, fTo: 900, q: 0.9, attack: 0.01 });
      this.noise(t, 0.28, 0.05, { type: 'highpass', f: 5000, attack: 0.01 });
      this.tone('sawtooth', 104, t, 0.28, 0.03, { lp: 550 });
      for (let i = 0; i < 4; i++) this.bub(t + 0.05 + Math.random() * 0.2, this.rn(400, 1200), this.rn(0.04, 0.07), this.rn(0.02, 0.04));
    },
    // Vaza Jato: o cano estoura
    geyser(t) {
      this.tone('sine', 90, t, 0.5, 0.3, { to: 45 });
      this.noise(t, 1.0, 0.25, { type: 'bandpass', f: 1200, fTo: 300, q: 0.7, attack: 0.02 });
      this.noise(t + 0.05, 0.8, 0.06, { type: 'highpass', f: 3500, attack: 0.05 });
      for (let i = 0; i < 10; i++) this.bub(t + 0.05 + Math.random() * 0.8, this.rn(300, 1200), this.rn(0.04, 0.1), this.rn(0.02, 0.05));
    },
    // Agua Gelada: cristais finos
    freeze(t) {
      [36, 40, 43].forEach((s, i) => this.fm(this.nt(s), t + i * 0.03, 0.35, 0.035, { ratio: 1.5, index: 0.8, verb: true }));
      this.noise(t, 0.25, 0.06, { type: 'highpass', f: 5000 });
    },
    // Central do Zap: rajada de mensagens (sopro e os pops)
    gust(t) {
      this.noise(t, 0.4, 0.14, { buf: this.pinkBuf, type: 'bandpass', f: 500, fTo: 1600, q: 1.1, attack: 0.06 });
      this.tone('sine', 110, t, 0.3, 0.04, { to: 70, attack: 0.04 });
      for (let i = 0; i < 3; i++) this.bub(t + 0.05 + i * 0.07, this.rn(900, 1500), 0.045, 0.05);
    },
    // Corrente do Zap: enxurrada de mensagens que cega
    sand(t) {
      this.noise(t, 0.35, 0.07, { type: 'highpass', f: 2500, fTo: 4500, attack: 0.05 });
      this.noise(t, 0.3, 0.05, { buf: this.pinkBuf, type: 'bandpass', f: 800, q: 1, attack: 0.05 });
      for (let i = 0; i < 7; i++) this.bub(t + i * 0.035 + Math.random() * 0.02, this.rn(1000, 1800), 0.035, 0.03);
    },
    // Disparo em Massa: redemoinho de mensagens subindo
    tornado(t) {
      this.noise(t, 1.5, 0.2, { buf: this.pinkBuf, type: 'bandpass', f: 300, q: 2, attack: 0.25, fPts: [[0.4, 1100], [0.75, 500], [1.1, 1400], [1.5, 600]] });
      this.tone('sine', 70, t, 1.3, 0.07, { to: 110, attack: 0.3 });
      for (let i = 0; i < 12; i++) this.bub(t + 0.15 + i * 0.09 + Math.random() * 0.03, 700 + i * 70 + this.rn(0, 150), 0.04, 0.03);
    },
    // Palanque da CPI: a batucada chama
    drums(t) {
      this.caixa(t, 0.12); this.caixa(t + 0.09, 0.09); this.caixa(t + 0.18, 0.14);
      this.surdo(t + 0.27, 0.4, true); this.tamb(t + 0.4, 0.12); this.tamb(t + 0.47, 0.12); this.surdo(t + 0.54, 0.3, false);
    },
    // Convocacao (Quebra de Sigilo): carimbo, papel e um tlim
    mark(t) { this.carimbo(t, 0.2); this.papel(t, 0.12, 0.03); this.fm(this.nt(24), t + 0.08, 0.3, 0.03, { ratio: 3.5, index: 1 }); },
    // Centrao de Aluguel: chegam, assobiam e a verba cai
    merc(t) { this.foot(t, 0.12); this.foot(t + 0.15, 0.12); this.whistle(t + 0.05, 1600, 0.05, 1900); this.chaChing(t + 0.3, 0.09); },
    // ponto de reuniao dos assessores: apito curto e o pano
    rally(t) { this.apito(t, 0.16, 0.05); this.pano(t, 0.04); },
    // obra: martelo
    hammer(t) { this.modal(this.rn(380, 560), t, 0.18, this.WOOD, { click: 0.3 }); },
    build(t) {
      for (let i = 0; i < 3; i++) this.modal(420 + i * 60, t + i * 0.1, 0.16, this.WOOD, { click: 0.3 });
      this.papel(t, 0.3, 0.03);
    },
    // torre pronta: ultima martelada, acorde de cavaco e o bip da urna
    built(t) {
      this.modal(300, t, 0.14, this.WOOD, { click: 0.3 });
      [0, 4, 7, 12].forEach((s, i) => this.ks(this.nt(s + 12), t + 0.03 + i * 0.02, 0.45, 0.08, { bright: 0.75, verb: true }));
      this.urna(t + 0.2, 0.05);
    },
    ability(t) { [19, 24, 28].forEach((s, i) => this.fm(this.nt(s), t + i * 0.05, 0.6, 0.07, { ratio: 2.01, index: 1.2, verb: true })); this.bip(t + 0.15, 2080, 0.08, 0.02); },
    // obra parada liberada: entulho rolando e poeira
    rubble(t) {
      for (let i = 0; i < 5; i++) this.modal(this.rn(300, 700), t + i * 0.07 + Math.random() * 0.03, 0.12, [[1, 1, 0.06], [1.7, 0.5, 0.04]], { click: 0.4 });
      this.tone('sine', 80, t, 0.3, 0.25, { to: 45 });
      this.noise(t, 0.6, 0.08, { buf: this.pinkBuf, f: 800, fTo: 300, attack: 0.05 });
    },
    // Manobra regimental: a alavanca catraca, trava e da um bip
    gate(t) {
      for (let i = 0; i < 5; i++) this.modal(this.rn(2400, 2800), t + i * 0.03, 0.05, [[1, 1, 0.02], [2.3, 0.3, 0.01]], { click: 0.4 });
      this.modal(160, t + 0.18, 0.2, [[1, 1, 0.12], [2.3, 0.4, 0.06]], { click: 0.3 });
      this.tone('sine', 80, t + 0.18, 0.15, 0.15, { to: 45 });
      this.bip(t + 0.3, 1320, 0.07, 0.03);
    },
    // Pancada de Pasta (Funcionarios Fantasmas): couro, baque e a fivela
    palm(t) {
      this.noise(t, 0.06, 0.16, { type: 'bandpass', f: 1100, q: 0.9, attack: 0.002 });
      this.tone('sine', 110, t, 0.15, 0.22, { to: 55 });
      this.modal(this.rn(1700, 2000), t + 0.02, 0.05, [[1, 1, 0.04], [2.4, 0.4, 0.02]], { click: 0.2 });
    },
    // Fundo Partidario / Atestado Medico: dedilhado morno subindo e moedinhas
    herbHeal(t) {
      [0, 4, 7, 12].forEach((s, i) => this.ks(this.nt(s + 12), t + i * 0.07, 0.5, 0.08, { bright: 0.45, verb: true }));
      this.tone('sine', this.nt(7), t, 0.7, 0.04, { attack: 0.2, verb: true });
      this.ping(t + 0.3, 2400, 0.02); this.ping(t + 0.38, 2900, 0.018);
    },

    // ---------------------------------------------------------- unidades e herois
    // golpe corpo a corpo: braco cortando o ar e a pancada
    sword(t) {
      this.noise(t, 0.07, 0.14, { type: 'bandpass', f: 3200, fTo: 1300, q: 1.3, attack: 0.008 });
      this.modal(this.rn(260, 320), t + 0.03, 0.12, [[1, 1, 0.06], [2.4, 0.4, 0.03]], { click: 0.25 });
    },
    // golpe no escudo / pasta
    clang(t) { this.modal(this.rn(560, 640), t, 0.16, [[1, 1, 0.08], [2.32, 0.5, 0.05], [3.6, 0.3, 0.03]], { click: 0.4 }); },
    // o "L" acerta: blup e um baque
    claw(t) {
      this.tone('sine', 280, t, 0.1, 0.12, { to: 620, glide: 0.06 });
      this.tone('sine', 140, t, 0.12, 0.15, { to: 70 });
      this.noise(t, 0.05, 0.08, { type: 'bandpass', f: 1600, q: 1 });
    },
    // Faz o L (Lulala): o L passa voando e os metais respondem
    hawk(t) {
      this.noise(t, 0.5, 0.1, { type: 'bandpass', f: 600, q: 1.5, attack: 0.08, fPts: [[0.25, 2600], [0.5, 900]] });
      this.metal(this.nt(7), t + 0.05, 0.12, 0.07);
      this.metal(this.nt(12), t + 0.19, 0.3, 0.08, { verb: true });
    },
    // Discurso de Palanque: o microfone gira, uma microfonia leve e o povo
    whirl(t) {
      this.noise(t, 0.5, 0.16, { type: 'bandpass', f: 700, q: 1.6, attack: 0.04, fPts: [[0.15, 3000], [0.3, 1100], [0.45, 2600]] });
      this.tone('sine', 2350, t + 0.05, 0.35, 0.012, { attack: 0.15, vib: [6, 0.004] });
      this.torcida(t + 0.1, 0.6, 0.035, { n: 4 });
    },
    // heroi recebeu ordem de andar
    heroMove(t) { this.ks(this.nt(19), t, 0.18, 0.08, { bright: 0.5 }); this.ks(this.nt(24), t + 0.06, 0.22, 0.07, { bright: 0.5 }); this.foot(t, 0.06); },
    heroDie(t) { [7, 4, 0].forEach((s, i) => this.ks(this.nt(s), t + i * 0.15, 0.6, 0.17, { bright: 0.4, verb: true })); this.tone('sine', 110, t, 0.3, 0.2, { to: 50 }); },
    // heroi volta: brilho subindo e o povo saudando
    heroBack(t) {
      [0, 4, 7, 12].forEach((s, i) => this.fm(this.nt(s + 12), t + i * 0.08, 0.5, 0.06, { ratio: 2.01, index: 1, verb: true }));
      this.torcida(t + 0.1, 0.7, 0.03, { n: 5 });
    },
    unitDie(t) {
      this.tone('sine', 120, t, 0.18, 0.18, { to: 60 });
      this.noise(t, 0.12, 0.06, { f: 700 });
      this.tone('triangle', 330, t, 0.25, 0.05, { to: 165, lp: 1200 });
    },
    // Cassacao (Zero-Um): martelo do juiz duas vezes e o carimbo
    bless(t) {
      this.martelo(t, 0.22); this.martelo(t + 0.2, 0.26);
      this.carimbo(t + 0.45, 0.2);
      this.fm(this.nt(24), t + 0.5, 0.6, 0.04, { ratio: 3.5, index: 1.2, verb: true });
    },
    // Projeto de Lei: folhas voando
    herb(t) { this.noise(t, 0.18, 0.08, { type: 'bandpass', f: 2000, fTo: 1000, q: 1.2, attack: 0.02, am: [28, 0.6] }); this.crk(t, 0.15, 0.05, { f: 3500 }); },
    herbHit(t) { this.noise(t, 0.05, 0.07, { type: 'bandpass', f: 1500, q: 1 }); this.fm(this.nt(this.pick([24, 28])), t, 0.25, 0.025, { ratio: 2.01, index: 0.6 }); },
    // Comitiva (Janjinha): portas de carro, passos, apito e o povo
    beastCall(t) {
      this.porta(t, 0.15); this.porta(t + 0.25, 0.12);
      for (let i = 0; i < 4; i++) this.foot(t + 0.4 + i * 0.13, 0.13);
      this.apito(t + 0.1, 0.18, 0.03);
      this.torcida(t + 0.5, 0.6, 0.025, { n: 3 });
    },
    // Stories (Janjinha): a camera, o plim e o povo parando para ver
    trail(t) {
      this.foto(t, 0.12);
      this.notif(t + 0.12, 0.04, 0);
      this.noise(t, 0.6, 0.06, { buf: this.pinkBuf, type: 'bandpass', f: 900, q: 1.4, attack: 0.08, fPts: [[0.2, 2600], [0.4, 1200], [0.6, 2000]] });
      this.notif(t + 0.4, 0.03, 2);
    },
    // Imbrochavel! (Capitao Mito): o grito no megafone e o povo respondendo
    flare(t) {
      this.megafone(t, 0.45, 0.07, { f: 170 });
      this.torcida(t + 0.1, 0.8, 0.04, { n: 6, vg: ['e', 'a'] });
      this.tone('sine', 80, t, 0.35, 0.2, { to: 40 });
      this.noise(t, 0.3, 0.1, { buf: this.pinkBuf, type: 'lowpass', f: 400, fPts: [[0.1, 2500], [0.3, 300]] });
    },
    // Motociata: a moto acelera e deixa o escapamento estalando
    fireTrail(t) { this.moto(t, 0.9, 0.1); this.crk(t + 0.2, 0.8, 0.12, { f: 1700 }); },
    // Ferro de Solda: chiado curto por cima do golpe
    ember(t) { this.crk(t, 0.18, 0.2, { f: 2000 }); this.noise(t, 0.12, 0.05, { type: 'bandpass', f: 1200, fTo: 2400, q: 1 }); },

    // ---------------------------------------------------------- adversarios (derrotado vira delator: larga a bandeira e corre)
    // a bandeira cai (pano) e soa um plim numa nota da escala
    die(t) {
      this.pano(t, 0.08); this.pano(t + 0.07, 0.06);
      this.fm(this.nt(this.pick([19, 24, 28, 31])), t + 0.06, 0.45, 0.045, { ratio: 2.01, index: 0.9, verb: true });
      this.tone('sine', 300, t, 0.08, 0.04, { to: 200 });
    },
    bigDie(t) {
      this.pano(t, 0.1); this.pano(t + 0.08, 0.08); this.pano(t + 0.15, 0.05);
      this.tone('sine', 110, t, 0.3, 0.2, { to: 50 });
      const s = this.pick([12, 19]);
      this.fm(this.nt(s + 12), t + 0.12, 0.6, 0.05, { ratio: 2.01, index: 1, verb: true });
      this.fm(this.nt(s + 19), t + 0.22, 0.6, 0.045, { ratio: 2.01, index: 1, verb: true });
    },
    // chefe caiu (ou o candidato entrou com recurso): "ooo" do povo, metal descendo e o baque
    bossDie(t) {
      this.torcida(t, 1.4, 0.05, { n: 9, vg: ['o', 'a'] });
      this.metal(this.nt(-5), t, 0.9, 0.06, { to: this.nt(-17), bright: 3 });
      this.tone('sine', 90, t, 1.0, 0.3, { to: 32 });
      this.noise(t, 1.0, 0.12, { buf: this.pinkBuf, f: 1200, fTo: 200, attack: 0.04 });
    },
    // chefe derrotado: acorde quente, o povo comemora e fogos
    bossFreed(t) {
      [-12, -5, 0, 4, 7, 12, 16].forEach((s, i) => this.ks(this.nt(s), t + 0.3 + i * 0.045, 1.6, 0.11, { bright: 0.55, verb: true }));
      [0, 7, 12].forEach(s => this.tone('triangle', this.nt(s - 12), t + 0.25, 1.8, 0.05, { attack: 0.4, lp: 1000 }));
      this.torcida(t + 0.2, 1.8, 0.04, { n: 8, palmas: 25 });
      this.fogos(t + 0.5, 0.1); this.fogos(t + 1.0, 0.08);
    },
    // adversario golpeia um assessor
    enemyHit(t) { this.noise(t, 0.06, 0.14, { f: 1100, attack: 0.002 }); this.tone('sine', 190, t, 0.07, 0.12, { to: 110 }); },
    // adversario subiu a rampa (perdeu voto): metal abafado descendo, "uon-uon"
    leak(t) {
      this.metal(this.nt(-8), t, 0.2, 0.08, { bright: 3 });
      this.metal(this.nt(-12), t + 0.22, 0.4, 0.08, { bright: 2.5 });
      this.tone('sine', 110, t + 0.22, 0.4, 0.08, { to: 70 });
    },
    // curandeiro adversario (Michele Uncao, Doutor Chuchu): um coro curto de "aaah"
    heal(t) { [-12, -8, -5].forEach((s, i) => this.voz(this.nt(s), t + i * 0.04, 0.8, 0.035, 'a', { attack: 0.2, hold: 0.3, vib: [5, 0.012], q: 6, lp: 2800, verb: true })); },
    // chefe chama reforcos no megafone
    warcry(t) { this.megafone(t, 0.6, 0.08); this.noise(t, 0.5, 0.05, { buf: this.pinkBuf, type: 'bandpass', f: 800, q: 1, attack: 0.1 }); },
    throw(t) { this.noise(t, 0.18, 0.1, { type: 'bandpass', f: 1600, fTo: 600, q: 1.8, attack: 0.02 }); },
    // sabotador: lata de spray chacoalhando, o jato de tinta e um apitinho de greve
    sabotage(t) {
      this.modal(1300, t, 0.08, [[1, 1, 0.03], [2.2, 0.4, 0.02]], { click: 0.5 });
      this.modal(1350, t + 0.09, 0.08, [[1, 1, 0.03], [2.2, 0.4, 0.02]], { click: 0.5 });
      this.noise(t + 0.18, 0.6, 0.12, { type: 'highpass', f: 3500, attack: 0.02, hold: 0.4 });
      this.noise(t + 0.18, 0.6, 0.05, { type: 'bandpass', f: 6000, q: 1, attack: 0.02, hold: 0.4 });
      this.apito(t + 0.75, 0.15, 0.02);
    },
    // Fundao Eleitoral lanca bolas de fogo
    firestorm(t) {
      this.noise(t, 1.2, 0.2, { buf: this.pinkBuf, type: 'bandpass', f: 400, fTo: 1400, q: 0.7, attack: 0.25 });
      this.crk(t + 0.2, 1.0, 0.3, { f: 1600 });
      this.tone('sawtooth', 80, t, 1.0, 0.08, { to: 140, lp: 500, attack: 0.3 });
    },
    // busao / notebook abre e solta a turma: porta pneumatica e cinco pulinhos
    splat(t) {
      this.noise(t, 0.35, 0.1, { type: 'highpass', f: 2800, env: [[0.02, 1], [0.35, 0]] });
      for (let i = 0; i < 5; i++) this.bub(t + 0.1 + i * 0.06, this.rn(500, 900), 0.05, 0.05);
      this.tone('sine', 120, t, 0.12, 0.12, { to: 70 });
    },
    // voador derrubado: baque no chao
    thud(t) { this.tone('sine', 95, t, 0.25, 0.3, { to: 42 }); this.noise(t, 0.12, 0.12, { f: 600 }); this.crk(t, 0.1, 0.05, { f: 2500 }); },

    // ---------------------------------------------------------- ondas, operacoes e eventos
    // onda nova: chamada dos metais (la-re) com o surdo
    horn(t) {
      this.surdo(t, 0.3, true);
      this.metal(this.nt(7), t, 0.16, 0.09, { verb: true }); this.metal(this.nt(-5), t, 0.16, 0.05);
      this.metal(this.nt(12), t + 0.2, 0.55, 0.1, { verb: true }); this.metal(this.nt(0), t + 0.2, 0.55, 0.06);
      this.surdo(t + 0.2, 0.35, true);
    },
    // ultima onda: a chamada completa, a torcida e o apito
    hornBig(t) {
      this.fx.horn.call(this, t);
      this.metal(this.nt(16), t + 0.75, 0.2, 0.09, { verb: true });
      this.metal(this.nt(19), t + 0.95, 1.0, 0.1, { verb: true }); this.metal(this.nt(7), t + 0.95, 1.0, 0.05);
      this.surdo(t + 0.75, 0.35, true); this.surdo(t + 0.95, 0.4, true); this.prato(t + 0.95, 0.04, 1.2);
      this.torcida(t + 1.0, 1.4, 0.03, { n: 7 });
      this.apito(t + 1.5, 0.3, 0.025);
    },
    // Operacao da PF: a sirene (uma por operacao), a freada e a viatura chegando com tudo
    thunder(t) {
      const first = !(t - this.sirT < 2.2);
      if (first) { this.sirT = t; this.sirene(t, 1.1, 0.06); }
      this.freada(t + 0.02, first ? 0.4 : 0.22, 0.07);
      const h = t + (first ? 0.38 : 0.2);
      this.porta(h, 0.25);
      this.tone('sine', 70, h, 0.4, 0.25, { to: 35 });
      this.noise(h, 0.4, 0.15, { buf: this.pinkBuf, f: 800, fTo: 150 });
    },
    // Bancada de Apoio: chegam de carro, passos firmes e um toque de metal
    riders(t) {
      this.porta(t, 0.16); this.porta(t + 0.22, 0.13);
      for (let i = 0; i < 6; i++) this.foot(t + 0.35 + i * 0.12, 0.14);
      this.metal(this.nt(12), t + 0.4, 0.12, 0.05); this.metal(this.nt(16), t + 0.54, 0.25, 0.05, { verb: true });
    },
    // Delacao Premiada: os delatores correm de volta, papelada voando, apito e o "ooo"
    stampede(t) {
      for (let i = 0; i < 16; i++) this.foot(t + i * 0.07 + Math.random() * 0.03, this.rn(0.1, 0.16));
      this.papel(t, 1.0, 0.05);
      this.apito(t, 0.5, 0.035);
      this.torcida(t + 0.2, 1.0, 0.03, { n: 6, vg: ['o', 'a'] });
    },
    // Delacao cheia de novo: plim de celular e um brilho subindo
    charmReady(t) {
      this.notif(t, 0.04, 0);
      [19, 24, 28, 31].forEach((s, i) => this.fm(this.nt(s), t + 0.2 + i * 0.045, 0.4, 0.03, { ratio: 2.01, index: 0.8, verb: true }));
    },
    // aviso de tempestade (ou de cheia): o celular vibra e o vento cresce
    windWarn(t) {
      this.celVibra(t, 0.05);
      this.noise(t, 2.0, 0.12, { buf: this.pinkBuf, type: 'bandpass', f: 300, fTo: 800, q: 1.4, attack: 0.8 });
      this.notif(t + 1.0, 0.03, 1);
    },
    // rajada da tempestade: vento seco e santinhos voando
    wind(t) {
      this.noise(t, 2.4, 0.15, { buf: this.pinkBuf, type: 'bandpass', f: this.rn(380, 580), fTo: 900, q: 1.2, attack: 0.6 });
      this.noise(t + 0.3, 0.8, 0.03, { type: 'bandpass', f: 2500, q: 1.5, am: [22, 0.7], attack: 0.2 });
    },
    // tempestade de fake news: a chuva chega com uma enxurrada de notificacoes
    stormStart(t) {
      this.noise(t, 3, 0.1, { type: 'highpass', f: 2500, env: [[1.5, 1], [3, 0]] });
      this.crk(t, 3, 0.25, { type: 'bandpass', f: 3500, q: 0.7, rate: 2, env: [[1.5, 1], [3, 0]] });
      for (let i = 0; i < 6; i++) this.notif(t + 0.2 + i * this.rn(0.15, 0.35), 0.025);
      this.fx.thunderFar.call(this, t + 0.3);
    },
    // a tempestade passa: chuva sumindo, pombos e um bem-te-vi
    stormEnd(t) {
      this.noise(t, 2.5, 0.06, { type: 'highpass', f: 2800, env: [[0.1, 1], [2.5, 0]] });
      this.fx.pombo.call(this, t + 0.8);
      this.fx.bemtevi.call(this, t + 1.6);
    },
    thunderFar(t) {
      this.noise(t, 2.2, 0.22, { buf: this.pinkBuf, f: 300, attack: 0.3, fPts: [[0.6, 450], [1.2, 200], [2.2, 80]] });
      this.tone('sine', 45, t + 0.1, 1.5, 0.1, { attack: 0.3 });
    },
    // a agua subindo (sobra do motor; nenhuma fase de Brasilia alaga)
    floodWarn(t) {
      this.noise(t, 2.5, 0.16, { buf: this.pinkBuf, f: 300, fTo: 700, attack: 1.2 });
      this.tone('sine', 60, t, 2.2, 0.12, { to: 75, attack: 1 });
      for (let i = 0; i < 8; i++) this.bub(t + 0.4 + Math.random() * 1.8, this.rn(180, 450), this.rn(0.06, 0.12), this.rn(0.03, 0.05));
    },
    flood(t) {
      this.noise(t, 2.8, 0.22, { buf: this.pinkBuf, type: 'bandpass', f: 500, fTo: 1100, q: 0.6, attack: 0.5 });
      this.tone('sine', 55, t, 2.2, 0.15, { attack: 0.4 });
      for (let i = 0; i < 12; i++) this.bub(t + 0.2 + Math.random() * 2.2, this.rn(250, 900), this.rn(0.05, 0.1), this.rn(0.03, 0.05));
    },
    floodEnd(t) {
      for (let i = 0; i < 7; i++) this.bub(t + i * 0.12, 900 - i * 90, 0.08, 0.05);
      this.noise(t, 1.2, 0.08, { buf: this.pinkBuf, f: 700, fTo: 200, attack: 0.05 });
      this.fm(this.nt(24), t + 1.1, 0.7, 0.05, { ratio: 3.5, index: 1, verb: true });
    },
    // chefe chegou: rufo de timpano e um acorde dramatico dos metais (re menor com a sexta menor)
    bossCome(t) {
      for (let i = 0; i < 10; i++) this.timp(t + i * 0.055, 73.4, 0.06 + i * 0.012);
      const h = t + 0.6;
      [[-12, 0.07], [0, 0.07], [3, 0.06], [8, 0.05], [12, 0.05]].forEach(([s, v]) => this.metal(this.nt(s), h, 1.6, v, { verb: true, bright: 6 }));
      this.timp(h, 73.4, 0.35); this.surdo(h, 0.4, true);
      this.prato(h, 0.05, 1.8);
      this.tone('sawtooth', 73.4, h, 2.0, 0.05, { lp: 400, attack: 0.05 });
    },
    // o candidato rival: o coracao bate enquanto ele esta na pista
    heartBeat(t) { this.beat(t, 0.22); },
    // "Entrou com recurso!": martelo, papelada subindo e o grave
    heartSmoke(t) {
      this.martelo(t, 0.25);
      this.beat(t, 0.3);
      this.noise(t + 0.1, 1.4, 0.1, { buf: this.pinkBuf, type: 'bandpass', f: 300, fTo: 1600, q: 0.8, attack: 0.3 });
      this.papel(t + 0.2, 0.8, 0.04);
      this.tone('sine', 73, t, 1.4, 0.12, { to: 55, attack: 0.1 });
    },
    // recurso julgado: ele volta (sopro, carimbo e a batida)
    heartBack(t) {
      this.noise(t, 0.6, 0.14, { buf: this.pinkBuf, type: 'bandpass', f: 2000, fTo: 300, q: 0.8, env: [[0.55, 1], [0.6, 0]] });
      this.carimbo(t + 0.55, 0.25);
      this.beat(t + 0.55, 0.35);
    },
    // Recurso negado!: festa na rampa (fanfarra, povo, palmas e fogos)
    heartFreed(t) {
      this.surdo(t, 0.4, true);
      [[0, 12, 0.15], [0.16, 16, 0.15], [0.32, 19, 1.4]].forEach(([d, s, l]) => { this.metal(this.nt(s), t + d, l, 0.08, { verb: true }); this.metal(this.nt(s - 12), t + d, l, 0.04); });
      [0, 4, 7].forEach(s => this.metal(this.nt(s), t + 0.32, 1.4, 0.035, { verb: true }));
      this.prato(t + 0.32, 0.05, 1.8); this.surdo(t + 0.32, 0.45, true);
      [-12, -5, 0, 4, 7, 12, 16, 19].forEach((s, i) => this.ks(this.nt(s), t + 0.6 + i * 0.06, 2.0, 0.08, { bright: 0.5, verb: true }));
      this.torcida(t + 0.3, 2.6, 0.05, { n: 10, palmas: 45 });
      this.fogos(t + 0.8, 0.12); this.fogos(t + 1.4, 0.1); this.fogos(t + 2.0, 0.12);
    },
    // madrugada chegando: acorde grave descendo, a cidade zumbindo e os grilos
    nightFall(t) {
      [7, 4, 0].forEach((s, i) => this.tone('triangle', this.nt(s - 12), t + i * 0.25, 1.2, 0.05, { attack: 0.2, lp: 700, verb: true }));
      this.noise(t + 0.3, 2.0, 0.05, { buf: this.pinkBuf, f: 200, attack: 1.0 });
      this.fx.cricket.call(this, t + 1.0); this.fx.cricket.call(this, t + 1.4);
    },
    // dia voltando: dedilhado subindo, pombos e um bem-te-vi
    dawn(t) {
      [0, 4, 7, 12].forEach((s, i) => this.ks(this.nt(s + 12), t + i * 0.09, 0.6, 0.08, { bright: 0.6, verb: true }));
      this.fx.pombo.call(this, t + 0.4);
      this.fx.bemtevi.call(this, t + 1.0);
    },

    // ---------------------------------------------------------- cidade e cerrado (ambiente; tambem tocam soltos)
    birdChirp(t) { this.chirp(t, 0.03); },
    // bem-te-vi: tres notas, a ultima mais longa
    bemtevi(t) {
      this.tone('sine', 1900, t, 0.09, 0.03, { to: 2100, attack: 0.01 });
      this.tone('sine', 2300, t + 0.13, 0.09, 0.03, { to: 2400, attack: 0.01 });
      this.tone('sine', 2500, t + 0.27, 0.26, 0.035, { to: 2000, attack: 0.02, vib: [9, 0.01] });
    },
    // cigarra do cerrado: chiado agudo que cresce devagar e corta
    cicada(t) {
      const f = this.rn(4200, 5600), d = this.rn(2.5, 5);
      this.noise(t, d, 0.03, { type: 'bandpass', f, q: 7, am: [this.rn(70, 140), 0.6], env: [[d * 0.45, 1], [d * 0.85, 0.8], [d, 0]] });
    },
    cricket(t) {
      const f = this.rn(4300, 4900);
      for (let k = 0; k < 2; k++) for (let i = 0; i < 3; i++) this.tone('sine', f, t + k * 0.35 + i * 0.045, 0.028, 0.02, { attack: 0.004 });
    },
    // pombo: "ru-ruu-ru" com o ronronado da garganta
    pombo(t) {
      const f = this.rn(330, 420);
      [[0, 0.16, 1], [0.22, 0.42, 1.12], [0.7, 0.2, 0.95]].forEach(([d, l, k]) => this.tone('sine', f * k, t + d, l, 0.04, { to: f * k * 0.85, attack: 0.04, vib: [32, 0.04], lp: 900 }));
    },
    // revoada de pombos: as asas batendo
    revoada(t) {
      const n = 12 + Math.floor(Math.random() * 8);
      for (let i = 0; i < n; i++) this.noise(t + i * this.rn(0.05, 0.09), 0.05, 0.05 * (1 - i / (n + 4)), { type: 'bandpass', f: this.rn(900, 1600), q: 0.8, attack: 0.004 });
    },
    // carro passando ao longe
    carro(t) {
      const d = this.rn(2, 3.5);
      this.noise(t, d, 0.05, { buf: this.pinkBuf, type: 'bandpass', f: 250, q: 0.7, fPts: [[d * 0.5, this.rn(600, 900)], [d, 260]], env: [[d * 0.5, 1], [d, 0]] });
      this.noise(t, d, 0.012, { type: 'highpass', f: 1800, env: [[d * 0.5, 1], [d, 0]] });
    },
    // buzina ao longe (uma ou duas)
    buzinaLonge(t) {
      const f = this.rn(380, 470), d = this.rn(0.15, 0.35);
      this.buzina(t, d, 0.03, f);
      if (Math.random() < 0.5) this.buzina(t + d + 0.1, d * 0.8, 0.03, f);
    },
    // onibus da rodoviaria: o freio a ar
    onibus(t) {
      this.noise(t, 0.6, 0.04, { type: 'highpass', f: 3000, env: [[0.03, 1], [0.6, 0]] });
      this.tone('sine', 1900, t, 0.4, 0.006, { vib: [7, 0.01], attack: 0.05 });
    },
    // burburinho do povo: silabas soltas, longe
    burburinho(t) {
      const n = 2 + Math.floor(Math.random() * 3);
      let tt = t;
      for (let i = 0; i < n; i++) {
        const f = this.rn(110, 260), d = this.rn(0.08, 0.2);
        this.voz(f, tt, d, 0.02, this.pick(['a', 'e', 'o', 'i']), { to: f * this.rn(0.85, 1.15), lp: 1500, q: 5, attack: 0.02, hold: d * 0.4 });
        tt += d + this.rn(0.02, 0.12);
      }
    },
    // a multidao comemora ao longe
    torcidaLonge(t) { this.torcida(t, this.rn(1.5, 2.5), 0.03, { n: 8, lp: 1600, vg: ['e', 'a', 'o'] }); },
    // apito de manifestacao ao longe ("pri-pri-priii")
    apitoLonge(t) {
      const n = 1 + Math.floor(Math.random() * 3), f = this.rn(2600, 3100);
      for (let i = 0; i < n; i++) this.apito(t + i * 0.28, i === n - 1 ? this.rn(0.3, 0.5) : 0.15, 0.02, f);
    },
    // carro de som / megafone ao longe
    megafoneLonge(t) { this.megafone(t, this.rn(0.8, 1.6), 0.03, { lp: 1800 }); },
    // bandeirao batendo no vento
    bandeira(t) {
      const n = 4 + Math.floor(Math.random() * 6);
      let tt = t;
      for (let i = 0; i < n; i++) { this.pano(tt, this.rn(0.025, 0.05)); tt += this.rn(0.08, 0.16); }
    },
    // celular apitando (tempestade de fake news)
    notif(t) { this.notif(t, 0.03); },
    celular(t) { this.celVibra(t, 0.03); },
  },

  // ------------------------------------------------------------ ambiente por tema de fase
  // camas continuas (transito, vento, multidao, zumbido da cidade, chuva) + cidade e cerrado sorteados; tudo baixo, no volume de efeitos
  AMB: {
    oasis: { traffic: 1, wind: 0.3, crowd: 0.35, pigeons: 0.5, cicada: 0.45, birds: 0.25, horns: 0.6, bus: 0.7 },        // Eixo Monumental (rodoviaria)
    canyon: { traffic: 0.55, wind: 0.75, cicada: 1, birds: 0.4, pigeons: 0.2, crowd: 0.2, horns: 0.25 },                // Esplanada dos Ministerios
    dunes: { traffic: 0.35, wind: 0.3, crowd: 0.3, horns: 0.1, insects: 1, hum: 1 },                                     // Congresso Nacional (madrugada)
    storm: { traffic: 0.35, wind: 0.5, crowd: 0.55, pigeons: 1, flag: 0.9, whistle: 0.25, mega: 0.2 },                  // Praca dos Tres Poderes
    tepui: { traffic: 0.25, wind: 0.5, crowd: 1, flag: 0.5, cicada: 0.35, whistle: 0.45, mega: 0.35, horns: 0.15 },     // Rampa do Planalto
  },
  // ganho de cada cama (calibrado para ficar bem no fundo)
  BED: { traffic: 0.04, wind: 0.07, crowd: 0.03, hum: 0.04, rain: 0.036, drops: 0.065, river: 0.07 },
  ambThemes() { return Object.keys(this.AMB); },
  // jogo de mentira para a galeria e para a medicao
  ambMock(theme, o = {}) { return { L: { theme, storm: o.storm != null, flood: o.flood != null }, isNight: () => !!o.night, stormK: () => o.storm || 0, flood: o.flood || 0, state: 'running', enemies: [] }; },

  startAmb(g, manual) {
    this.stopAmb();
    this.ambG = g;
    if (!this.ctx || !g) return;
    const c = this.ctx, now = c.currentTime, L = g.L || {};
    const P = this.AMB[L.theme] || this.AMB.oasis;
    const A = this.amb = { P, g, beds: {}, srcs: [], night: null, can: null, beat: 0, out: c.createGain() };
    A.out.gain.setValueAtTime(0.0001, now);
    A.out.gain.exponentialRampToValueAtTime(1, now + 2.5);
    A.out.connect(this.ambGain);
    const bed = (name, buf, type, f, q, rate) => {
      const s = c.createBufferSource(); s.buffer = buf; s.loop = true;
      if (rate) s.playbackRate.value = rate;
      const fl = c.createBiquadFilter(); fl.type = type; fl.frequency.value = f; fl.Q.value = q;
      const gn = c.createGain(); gn.gain.value = 0;
      s.connect(fl); fl.connect(gn); gn.connect(A.out);
      s.start(now, Math.random() * buf.duration);
      A.srcs.push(s); A.beds[name] = { fl, g: gn, f0: f };
    };
    if (P.traffic) bed('traffic', this.pinkBuf, 'lowpass', 380, 0.6, 0.8);
    if (P.wind || L.storm) bed('wind', this.pinkBuf, 'bandpass', 520, 0.9);
    if (P.crowd) bed('crowd', this.pinkBuf, 'bandpass', 750, 0.9);
    // zumbido da cidade: sempre existe (a noite pode cair no meio da fase)
    bed('hum', this.pinkBuf, 'lowpass', 190, 0.8);
    if (L.storm) { bed('rain', this.pinkBuf, 'highpass', 2600, 0.5, 1.3); bed('drops', this.crackBuf, 'bandpass', 3800, 0.8, 2); }
    if (L.flood) bed('river', this.pinkBuf, 'lowpass', 650, 0.6);
    if (!manual) this.ambTimer = setInterval(() => { if (this.ctx) this.ambTick(this.ctx.currentTime); }, 250);
  },
  stopAmb() {
    if (this.ambTimer) clearInterval(this.ambTimer);
    this.ambTimer = null; this.ambG = null;
    const A = this.amb;
    this.amb = null;
    if (!A || !this.ctx) return;
    const t = this.ctx.currentTime;
    A.out.gain.cancelScheduledValues(t);
    A.out.gain.setTargetAtTime(0, t, 0.25);
    for (const s of A.srcs) s.stop(t + 1.5);
  },
  // renderiza o ambiente sem relogio (OfflineAudioContext da medicao)
  ambOffline(g, dur) { this.startAmb(g, true); for (let t = 0; t < dur; t += 0.25) this.ambTick(t); },

  ambTick(now) {
    const A = this.amb;
    if (!A) return;
    const g = A.g, P = A.P;
    let night = false, sk = 0, fl = 0;
    try { night = !!g.isNight(); sk = g.stormK ? g.stormK() : 0; fl = g.flood || 0; } catch (e) { return; }
    // madrugada chegando / dia voltando (o estado inicial da fase nao toca)
    if (A.night !== null && night !== A.night) this.play(night ? 'nightFall' : 'dawn');
    A.night = night;
    // Delacao Premiada ficou pronta
    try {
      const can = !!(g.canCast && g.canCast('stampede'));
      if (A.can === false && can) this.play('charmReady');
      A.can = can;
    } catch (e) { /* jogo de mentira */ }
    // o candidato rival: o coracao bate enquanto ele esta na pista (mais rapido quando fraco)
    const heart = g.enemies && g.enemies.find(e => e.T && e.T.final && !e.dead && !e.reached);
    if (heart && now >= A.beat) {
      this.play('heartBeat', heart.untargetable ? 0.5 : 1, heart.x);
      A.beat = now + (heart.hp < heart.maxHp * 0.35 ? 0.78 : 1.1);
    }
    // camas: nivel alvo com respiracao aleatoria
    const end = g.state === 'won' || g.state === 'lost' ? 0.6 : 1;
    const lv = {
      traffic: (P.traffic || 0) * (night ? 0.45 : 1),
      wind: (P.wind || 0) * (night ? 0.7 : 1) + sk * 0.7,
      crowd: (P.crowd || 0) * (night ? 0.55 : 1) * (1 - sk * 0.4),
      hum: night ? (P.hum || 0.6) : 0,
      rain: sk, drops: sk,
      river: fl * 0.6,
    };
    for (const k in A.beds) {
      const B = A.beds[k];
      let v = (lv[k] || 0) * this.BED[k] * end, f = B.f0, tc = 0.8;
      if (k === 'traffic') { v *= this.rn(0.7, 1.2); f *= this.rn(0.8, 1.3); tc = 1.5; }
      else if (k === 'wind') { v *= this.rn(0.35, 1.3); f *= this.rn(0.7, 1.6); tc = 1.2; }
      else if (k === 'crowd') { v *= this.rn(0.6, 1.3); f *= this.rn(0.85, 1.2); tc = 0.9; }
      else if (k === 'hum') { v *= this.rn(0.9, 1.1); tc = 2; }
      else if (k === 'river') { v *= this.rn(0.75, 1.15); f *= this.rn(0.85, 1.25) * (1 + fl * 0.4); tc = 0.5; }
      B.g.gain.setTargetAtTime(v, now, tc);
      B.fl.frequency.setTargetAtTime(f, now, tc);
    }
    if (!this.sfxOn) return;
    // cidade e cerrado, sorteados (taxa por segundo)
    const dt = 0.25, day = night ? 0 : 1, calm = 1 - sk;
    const ev = (rate, name, vol) => { if (Math.random() < rate * dt) this.ambEv(name, now + Math.random() * dt, vol); };
    ev(0.2 * (P.birds || 0) * day * calm, this.pick(['birdChirp', 'birdChirp', 'bemtevi']));
    ev(0.08 * (P.cicada || 0) * day * calm, 'cicada');
    ev(0.16 * (P.pigeons || 0) * day * calm, 'pombo');
    ev(0.015 * (P.pigeons || 0) * day, 'revoada');
    ev(0.9 * (P.insects || 0.5) * (night ? 1 : 0) * calm, 'cricket');
    ev(0.1 * (P.traffic || 0) * (night ? 0.4 : 1), 'carro');
    ev(0.035 * (P.horns || 0) * (night ? 0.3 : 1), 'buzinaLonge');
    ev(0.03 * (P.bus || 0) * day, 'onibus');
    ev(1.0 * (P.crowd || 0) * (night ? 0.4 : 1), 'burburinho');
    ev(0.025 * (P.crowd || 0) * (night ? 0.3 : 1), 'torcidaLonge');
    ev(0.035 * (P.whistle || 0), 'apitoLonge');
    ev(0.02 * (P.mega || 0), 'megafoneLonge');
    ev(0.16 * (P.flag || 0) * (1 + sk), 'bandeira');
    ev(0.9 * sk, 'notif');
    ev(0.12 * sk, 'celular');
    ev(0.03 * (P.thunderFar || 0) + 0.1 * sk, 'thunderFar', 0.7);
  },
  // toca um som da cidade no barramento do ambiente, com pan e altura sorteados
  ambEv(name, t, vol) {
    const fn = this.fx[name], A = this.amb;
    if (!fn || !A) return;
    const c = this.ctx, bus = c.createGain();
    bus.channelCount = 1; bus.channelCountMode = 'explicit';
    bus.gain.value = (vol == null ? 1 : vol) * this.FXG * ((this.meta[name] || {}).g || 1) * this.rn(0.55, 1);
    if (c.createStereoPanner) {
      const p = c.createStereoPanner(); p.pan.value = this.rn(-0.6, 0.6);
      bus.connect(p); p.connect(A.out);
    } else bus.connect(A.out);
    this.out = bus; this.vsend = null; this.pm = Math.pow(2, this.rn(-1, 1) / 12);
    try { fn.call(this, t, 1); } catch (e) { console.error('som ' + name + ': ' + e.message); } finally { this.out = null; this.vsend = null; this.pm = 1; }
  },

  // ------------------------------------------------------------ musica
  // tudo em re: calma e batalha em re maior, chefe em re menor. Notas em MIDI (62 = re central).
  startTrack(name, force) {
    if (this.track === name && !force && this.timer) return;
    this.track = name;
    if (!this.ctx) return;
    if (this.timer) clearInterval(this.timer);
    this.mus.gain.setTargetAtTime((this.tracks[name] || {}).lvl || 1, this.ctx.currentTime, 0.05);
    this.step = 0;
    this.nextT = this.ctx.currentTime + 0.1;
    this.timer = setInterval(() => this.schedule(), 40);
  },
  stopTrack() {
    this.track = null;
    if (this.timer) clearInterval(this.timer);
    this.timer = null;
  },

  schedule() {
    if (!this.ctx || !this.track) return;
    const T = this.tracks[this.track];
    const stepDur = 60 / T.bpm / 4;
    while (this.nextT < this.ctx.currentTime + 0.25) {
      T.play.call(this, this.step, this.nextT, stepDur);
      this.step++;
      this.nextT += stepDur;
    }
  },

  // ---- instrumentos da musica (todos no barramento da musica)
  // violao de nylon (cav = cavaquinho): corda Karplus-Strong com um buffer a cada 2 semitons
  corda(m, t, dur, vol, cav) {
    const f = this.mf(m), base = this.mf(m - (((m % 2) + 2) % 2));
    this.ks(f, t, dur, vol, cav
      ? { dest: this.mus, base, t60: 0.6, bright: 0.7, lp: 4200, nv: 2, verb: true }
      : { dest: this.mus, base, t60: 1.2, bright: 0.3, lp: 2300, nv: 2, verb: true });
  },
  // batida: as cordas uma depois da outra (para cima comeca pela aguda e soa mais leve)
  strum(v, t, dur, vol, cav, up) {
    const n = v.length, sp = cav ? 0.009 : 0.014;
    for (let i = 0; i < n; i++) {
      const j = up ? n - 1 - i : i;
      this.corda(v[j], t + i * sp, dur, vol * (up ? 0.8 : 1) * (0.85 + 0.15 * (j / n)), cav);
    }
  },
  // contrabaixo dedilhado
  baixo(m, t, dur, vol) {
    const M = this.mus, f = this.mf(m);
    this.tone('triangle', f, t, dur, vol, { dest: M, lp: 700, lpTo: 260, attack: 0.006 });
    this.tone('sine', f, t, dur * 0.9, vol * 0.6, { dest: M, attack: 0.006 });
  },
  vibrafone(m, t, dur, vol) {
    const M = this.mus, f = this.mf(m);
    this.fm(f, t, dur, vol, { ratio: 4, index: 0.45, dest: M, verb: true });
    this.tone('sine', f, t, dur * 1.2, vol * 0.5, { dest: M, attack: 0.004, verb: true });
  },
  flauta(m, t, dur, vol) {
    const M = this.mus, f = this.mf(m);
    this.tone('sine', f, t, dur, vol, { dest: M, attack: 0.045, hold: dur * 0.55, vib: [5.2, 0.005], verb: true });
    this.tone('triangle', f * 2, t, dur * 0.8, vol * 0.1, { dest: M, attack: 0.05, lp: 3000 });
    this.noise(t, Math.min(0.15, dur), vol * 0.12, { type: 'bandpass', f: f * 2, q: 2, attack: 0.02, dest: M });
  },
  // naipe de metais: trompetes nas vozes, trombone uma oitava abaixo da mais grave
  naipe(v, t, dur, vol) {
    const M = this.mus;
    for (const m of v) this.metal(this.mf(m), t, dur, vol, { dest: M, verb: true, hold: dur * 0.3 });
    this.metal(this.mf(v[0] - 12), t, dur, vol * 0.8, { dest: M, bright: 4, hold: dur * 0.3 });
  },
  pad(f, t, dur, vol) {
    const M = this.mus;
    this.tone('sawtooth', f, t, dur, vol, { dest: M, lp: 700, attack: dur * 0.3, verb: true });
    this.tone('sawtooth', f * 1.006, t, dur, vol * 0.8, { dest: M, lp: 600, attack: dur * 0.3 });
  },
  // pulso seco de plantao (semicolcheias)
  pulso(m, t, dur, vol) { this.tone('square', this.mf(m), t, dur, vol, { dest: this.mus, lp: 1800, lpTo: 500, attack: 0.003 }); },
  // percussao brasileira (o = { dest } na musica; sem dest toca como efeito)
  surdo(t, v, open, o = {}) {
    const f = open ? 58 : 76;
    this.tone('sine', f * 1.7, t, open ? 0.55 : 0.16, v, { to: f, glide: 0.035, attack: 0.002, dest: o.dest });
    this.tone('sine', f * 2.6, t, 0.06, v * 0.18, { attack: 0.002, dest: o.dest });
    this.noise(t, 0.04, v * 0.3, { f: 380, attack: 0.001, dest: o.dest });
  },
  caixa(t, v, o = {}) {
    this.noise(t, 0.07, v, { type: 'bandpass', f: 3800, q: 0.7, attack: 0.001, dest: o.dest });
    this.noise(t, 0.035, v * 0.5, { type: 'highpass', f: 6500, attack: 0.001, dest: o.dest });
    this.tone('triangle', 290, t, 0.03, v * 0.25, { attack: 0.001, dest: o.dest });
  },
  tamb(t, v, o = {}) {
    this.tone('sine', 960, t, 0.05, v, { to: 860, attack: 0.001, dest: o.dest });
    this.noise(t, 0.018, v * 0.6, { type: 'bandpass', f: 4200, q: 1.2, attack: 0.001, dest: o.dest });
  },
  agogo(t, hi, v, o = {}) { this.modal(hi ? 1230 : 920, t, v, [[1, 1, 0.22], [2.7, 0.18, 0.07]], { click: 0.3, dest: o.dest }); },
  ganza(t, v, o = {}) { this.noise(t, 0.05, v, { type: 'bandpass', f: 6500, q: 0.9, attack: 0.008, dest: o.dest }); },
  aro(t, v, o = {}) { this.modal(1650, t, v, [[1, 1, 0.035], [2.3, 0.4, 0.02]], { click: 0.5, dest: o.dest }); },
  timp(t, f, v, o = {}) {
    this.tone('sine', f * 1.02, t, 1.3, v, { to: f, glide: 0.08, attack: 0.003, dest: o.dest, verb: o.verb });
    this.tone('sine', f * 1.5, t, 0.7, v * 0.35, { attack: 0.003, dest: o.dest });
    this.noise(t, 0.05, v * 0.25, { f: 500, attack: 0.001, dest: o.dest });
  },
  prato(t, v, dur, o = {}) {
    this.noise(t, dur, v, { type: 'highpass', f: 5200, attack: 0.002, dest: o.dest, verb: o.verb });
    this.noise(t, dur * 0.5, v * 0.5, { type: 'bandpass', f: 3200, q: 0.8, attack: 0.002, dest: o.dest });
  },

  tracks: {
    // calma (titulo e mapa): bossa tranquila, violao na clave, baixo pontuado, ganza e um vibrafone esparso
    calm: {
      bpm: 100, lvl: 0.91,
      // por compasso: 1 ou 2 acordes [baixo, quinta, vozes do violao]
      H: [
        [[38, 45, [57, 61, 64, 66]]],                              // Dmaj9
        [[47, 42, [57, 61, 62, 66]]],                              // Bm9
        [[40, 47, [55, 59, 62, 66]]],                              // Em9
        [[45, 40, [55, 59, 61, 66]]],                              // A13
        [[42, 49, [57, 61, 64, 68]]],                              // F#m9
        [[47, 42, [57, 61, 63, 68]]],                              // B13
        [[40, 47, [55, 59, 62, 66]]],                              // Em9
        [[45, 40, [55, 59, 62, 66]], [45, 40, [55, 59, 61, 66]]],  // A13sus4 A13
        [[43, 50, [57, 59, 62, 66]]],                              // Gmaj9
        [[43, 50, [57, 58, 62, 64]]],                              // Gm6
        [[42, 49, [57, 61, 64, 66]]],                              // F#m7
        [[47, 42, [57, 61, 63, 68]]],                              // B13
        [[40, 47, [55, 59, 62, 66]]],                              // Em9
        [[45, 40, [55, 59, 61, 66]]],                              // A13
        [[38, 45, [57, 59, 64, 66]]],                              // D6/9
        [[40, 47, [55, 59, 62, 66]], [45, 40, [55, 59, 61, 66]]],  // Em9 A13
      ],
      // melodia (original): [passo, nota, duracao em passos]; os 4 ultimos compassos ficam so no violao
      MEL: {
        0: [[6, 69, 2], [8, 73, 4], [12, 76, 4]], 1: [[0, 74, 6], [6, 73, 2], [8, 69, 8]],
        2: [[6, 67, 2], [8, 71, 4], [12, 74, 4]], 3: [[0, 73, 6], [6, 71, 2], [8, 66, 8]],
        4: [[10, 68, 2], [12, 69, 4]], 5: [[0, 75, 6], [6, 73, 2], [8, 68, 8]],
        6: [[6, 66, 2], [8, 67, 4], [12, 71, 4]], 7: [[0, 69, 10]],
        8: [[4, 78, 4], [8, 76, 2], [10, 74, 6]], 9: [[0, 76, 6], [6, 74, 2], [8, 70, 8]],
        10: [[4, 73, 4], [8, 76, 2], [10, 69, 6]], 11: [[0, 69, 4], [4, 68, 4], [8, 66, 8]],
      },
      play(s, t, sd) {
        const T = this.tracks.calm, M = { dest: this.mus };
        const bar = Math.floor(s / 16) % 16, st = s % 16, cyc = Math.floor(s / 256) % 2;
        const H = T.H[bar], [b, q, v] = st >= 8 && H[1] ? H[1] : H[0];
        // baixo de bossa: fundamental pontuada e a quinta antecipada
        if (st === 0 || st === 8) this.baixo(b, t, sd * 5.5, 0.088);
        if (st === 6 || st === 14) this.baixo(q, t, sd * 2, 0.066);
        // violao na clave da bossa (o ultimo compasso de cada 4 vira a batida)
        const hits = bar % 4 === 3 ? [0, 3, 6, 9, 12, 14] : [0, 3, 6, 10, 13];
        const k = hits.indexOf(st);
        if (k >= 0) {
          const nx = k + 1 < hits.length ? hits[k + 1] : 16;
          this.strum(v, t, sd * (nx - st) * 0.95, st === 0 ? 0.085 : 0.11, false, false);
        }
        // ganza baixinho; aro (baqueta na borda) so na segunda parte
        this.ganza(t, (st % 4 === 2 ? 0.065 : 0.03) * (0.8 + Math.random() * 0.4), M);
        if (bar >= 8 && (st === 3 || st === 6 || st === 10 || st === 13)) this.aro(t, 0.085, M);
        // melodia esparsa: vibrafone numa volta, flauta na outra
        const mel = T.MEL[bar];
        if (mel) for (const [ms, m, len] of mel) {
          if (ms !== st) continue;
          if (cyc) this.flauta(m, t, sd * len * 0.95, 0.056); else this.vibrafone(m, t, sd * len + 0.3, 0.056);
        }
      },
    },
    // batalha: samba leve (surdo, caixa, tamborim, agogo, ganza), cavaquinho, flauta e metais curtos
    battle: {
      bpm: 116, lvl: 0.91,
      // acorde: [baixo, quinta, vozes do cavaquinho]
      V: {
        D6: [38, 45, [66, 69, 71, 74]], B7: [47, 42, [66, 69, 71, 75]], Em7: [40, 47, [67, 71, 74, 76]], A7: [45, 40, [67, 69, 73, 76]],
        D7: [38, 45, [66, 69, 72, 74]], G6: [43, 38, [67, 71, 74, 76]], Gm6: [43, 38, [67, 70, 74, 76]], DA: [45, 38, [66, 69, 74, 78]],
        Bm7: [47, 42, [66, 69, 71, 74]], Fs7: [42, 49, [64, 66, 70, 73]],
      },
      H: [['D6'], ['B7'], ['Em7'], ['A7'], ['D6'], ['D7'], ['G6', 'Gm6'], ['DA', 'A7'],
        ['Bm7'], ['Fs7'], ['Bm7'], ['B7'], ['Em7'], ['A7'], ['D6', 'B7'], ['Em7', 'A7']],
      // melodia da parte A (original)
      MEL: {
        0: [[2, 69, 1], [3, 71, 1], [4, 74, 2], [7, 78, 3], [10, 76, 2], [12, 74, 2], [14, 71, 2]],
        1: [[0, 75, 3], [3, 76, 1], [4, 78, 4], [8, 78, 2], [10, 75, 2], [12, 71, 4]],
        2: [[2, 71, 1], [3, 74, 1], [4, 76, 2], [7, 79, 3], [10, 78, 2], [12, 76, 2], [14, 74, 2]],
        3: [[0, 73, 3], [3, 74, 1], [4, 76, 4], [8, 76, 2], [10, 73, 2], [12, 69, 4]],
        4: [[2, 69, 1], [3, 71, 1], [4, 74, 2], [7, 78, 3], [10, 81, 2], [12, 78, 2], [14, 74, 2]],
        5: [[0, 78, 3], [3, 76, 1], [4, 74, 2], [7, 72, 3], [10, 74, 2], [12, 76, 2], [14, 78, 2]],
        6: [[0, 79, 6], [7, 76, 1], [8, 74, 2], [10, 70, 2], [12, 76, 4]],
        7: [[0, 78, 4], [4, 74, 4], [8, 76, 2], [10, 73, 2]],
      },
      // metais da parte B: [passo, nota (0 = golpe no acorde), duracao em passos]
      BR: {
        8: [[3, 0, 1], [6, 0, 1.5]], 9: [[0, 0, 3]], 10: [[3, 0, 1], [6, 0, 1.5]],
        11: [[0, 0, 3], [12, 66, 1], [13, 69, 1], [14, 71, 1], [15, 75, 1]],
        12: [[0, 76, 4], [6, 0, 1], [10, 0, 1.5]], 13: [[3, 0, 1], [6, 0, 1.5]], 14: [[0, 0, 3], [8, 0, 3]],
        15: [[0, 0, 2], [8, 69, 2], [10, 73, 2], [12, 76, 2], [14, 79, 2]],
      },
      // caixa: semicolcheias com acento na quarta de cada tempo
      CX: [0.9, 0.3, 0.5, 0.75, 0.4, 0.3, 0.5, 0.75, 0.9, 0.3, 0.5, 0.75, 0.4, 0.3, 0.5, 0.75],
      CV: { 0: 0.5, 2: 0.8, 3: 0.55, 5: 0.9, 7: 0.6, 8: 0.5, 10: 0.8, 11: 0.55, 13: 0.9, 15: 0.6 },
      TB: [0, 2, 5, 7, 9, 12, 14],
      AG: { 0: 1, 3: 1, 6: 0, 8: 1, 11: 1, 12: 0, 14: 0 },
      play(s, t, sd) {
        const T = this.tracks.battle, M = { dest: this.mus };
        const bar = Math.floor(s / 16) % 16, st = s % 16, cyc = Math.floor(s / 256) % 2, B = bar >= 8;
        const H = T.H[bar], [b, q, v] = T.V[st >= 8 && H[1] ? H[1] : H[0]];
        // baixo de samba: fundamental no 1, quinta na antecipacao e no 2
        if (st === 0 || st === 8) this.baixo(b, t, sd * 1.8, 0.13);
        if (st === 3 || st === 11) this.baixo(q, t, sd * 0.9, 0.078);
        if (st === 4 || st === 12) this.baixo(q, t, sd * 3.5, 0.11);
        // surdos: marcacao (aberto) no 2, resposta (abafado) no 1, corte na parte B
        if (st === 4 || st === 12) this.surdo(t, 0.27, true, M);
        if (st === 0 || st === 8) this.surdo(t, 0.16, false, M);
        if (B && bar % 2 && (st === 7 || st === 14)) this.surdo(t, 0.1, false, M);
        // caixa (mais leve na parte B) e a virada no fim da volta
        this.caixa(t, T.CX[st] * (B ? 0.12 : 0.17) * (0.85 + Math.random() * 0.3), M);
        if (bar === 15 && st >= 12) this.caixa(t + sd / 2, 0.09 + (st - 12) * 0.03, M);
        // tamborim teleco-teco (alterna as partes a cada volta), agogo na parte B, ganza sempre
        if ((B ? cyc : !cyc) || bar % 4 === 3) { if (T.TB.includes(st)) this.tamb(t, 0.11, M); }
        if (B && T.AG[st] != null) this.agogo(t, T.AG[st], 0.055, M);
        this.ganza(t, st % 2 ? 0.019 : 0.031, M);
        // cavaquinho: batida de samba (para baixo nos pares, para cima nos impares)
        const cv = T.CV[st];
        if (cv) this.strum(v, t, sd * 1.5, 0.105 * cv, true, st % 2 === 1);
        // melodia na parte A (na segunda volta so a primeira frase; depois os metais respondem)
        let br = null;
        if (!B) {
          const mel = T.MEL[bar];
          if (mel && (!cyc || bar < 4)) for (const [ms, m, len] of mel) if (ms === st) this.flauta(m, t, sd * len * 0.92, 0.064);
          if (cyc && bar >= 4) br = bar === 7 ? [[0, 0, 2], [8, 69, 2], [10, 73, 2], [12, 76, 2], [14, 79, 2]] : T.BR[8];
        } else br = T.BR[bar];
        if (br) for (const [ms, m, len] of br) {
          if (ms !== st) continue;
          if (m) { this.metal(this.mf(m), t, sd * len, 0.082, { dest: this.mus, verb: true }); this.metal(this.mf(m - 12), t, sd * len, 0.05, { dest: this.mus, bright: 4 }); }
          else this.naipe(v.slice(1), t, sd * len, 0.05);
        }
      },
    },
    // chefe: re menor, pulso de plantao, timpano, surdo em todo tempo, golpes de metal e o tema dos metais
    boss: {
      bpm: 126, lvl: 1.33,
      // acorde: [baixo, vozes dos metais]
      V: { Dm: [38, [62, 65, 69]], Bb: [46, [62, 65, 70]], A: [45, [61, 64, 69]], Gm: [43, [62, 67, 70]], Eb: [39, [63, 67, 70]], A7: [45, [61, 67, 69]] },
      H: ['Dm', 'Dm', 'Bb', 'A', 'Gm', 'Gm', 'Eb', 'A7'],
      // tema dos metais (original), na segunda metade
      MEL: {
        0: [[0, 69, 3], [3, 74, 3], [6, 77, 2], [8, 76, 4], [12, 74, 2], [14, 72, 2]], 1: [[0, 69, 8], [12, 65, 2], [14, 67, 2]],
        2: [[0, 70, 3], [3, 74, 3], [6, 77, 2], [8, 79, 4], [12, 77, 4]], 3: [[0, 76, 6], [6, 73, 2], [8, 69, 8]],
        4: [[0, 70, 3], [3, 74, 3], [6, 79, 2], [8, 77, 4], [12, 74, 4]], 5: [[0, 74, 8], [12, 70, 2], [14, 72, 2]],
        6: [[0, 75, 3], [3, 74, 3], [6, 70, 2], [8, 67, 8]], 7: [[0, 69, 4], [4, 73, 4], [8, 76, 4], [12, 79, 4]],
      },
      play(s, t, sd) {
        const T = this.tracks.boss, M = { dest: this.mus };
        const bar = Math.floor(s / 16) % 16, st = s % 16, ph = bar % 8, B = bar >= 8;
        const [b, v] = T.V[T.H[ph]];
        // pulso de plantao: semicolcheias secas na fundamental, oitava sim, oitava nao
        this.pulso(b + 24 + (st % 2 ? 12 : 0), t, sd * 0.55, st % 4 === 0 ? 0.06 : 0.036);
        // timpano nos compassos pares e o rufo antes da volta
        if (st === 0 && ph % 2 === 0) this.timp(t, this.mf(b), 0.18, { dest: this.mus, verb: true });
        if (ph === 7 && st >= 8) this.timp(t, this.mf(45), 0.03 + (st - 8) * 0.012, M);
        // surdo em todo tempo; caixa com acento no contratempo
        if (st % 4 === 0) this.surdo(t, st % 8 === 4 ? 0.25 : 0.18, st % 8 === 4, M);
        this.caixa(t, st % 4 === 2 ? 0.1 : st % 2 ? 0.033 : 0.048, M);
        // cordas graves sustentando o acorde
        if (st === 0) { this.pad(this.mf(b + 12), t, sd * 16, 0.041); this.pad(this.mf(v[1] - 12), t, sd * 16, 0.03); }
        // prato na virada de cada metade
        if (st === 0 && ph === 0) this.prato(t, 0.04, 1.6, M);
        if (!B) {
          // primeira metade: golpes de acorde em pergunta e resposta
          const hit = ph % 2 === 0 ? { 0: 3, 6: 1, 7: 2.5 }[st] : { 10: 1, 11: 1, 12: 3 }[st];
          if (hit) this.naipe(v, t, sd * hit, st === 0 ? 0.035 : 0.028);
        } else {
          // segunda metade: o tema, trompete com trombone uma oitava abaixo
          const mel = T.MEL[ph];
          if (mel) for (const [ms, m, len] of mel) {
            if (ms !== st) continue;
            this.metal(this.mf(m), t, sd * len * 0.95, 0.05, { dest: this.mus, verb: true });
            this.metal(this.mf(m - 12), t, sd * len * 0.95, 0.032, { dest: this.mus, bright: 4 });
          }
          if (st === 0) this.naipe(v, t, sd * 2, 0.022);
        }
      },
    },
  },
};
