'use strict';
// Todo o conteudo do jogo: inimigos, torres, heroi, feiticos, melhorias e fases.

const DATA = {};

// ---------------------------------------------------------------- INIMIGOS
// hp, speed (px/s), armor (0..1 fisico), mres (0..1 magico), gold, lives (vidas que tira),
// dmg/rate: ataque corpo a corpo, size: raio aproximado do corpo
DATA.ENEMIES = {
  // V: a turma verde-amarela (quem voce enfrenta jogando com a Chapa Vermelha); R: a turma vermelha (jogando com a
  // Verde-Amarela). Sem V/R, o adversario e o mesmo nos dois lados (o Centrao). DATA.setRival copia o lado da vez.
  raider: {
    hp: 34, speed: 38, armor: 0, mres: 0, gold: 6, lives: 1,
    dmg: [1, 4], rate: 1.0, size: 10,
    V: { spr: 'pneu', name: 'Patriota do Pneu', desc: 'Reza abraçado no pneu e marcha em fila. Fraco sozinho, chato em bando.' },
    R: { spr: 'mortadela', name: 'Militante da Mortadela', desc: 'Veio pelo sanduíche e ficou pela causa. Fraco sozinho, chato em bando.' },
    tip: 'Qualquer torre resolve.',
  },
  jackal: {
    hp: 20, speed: 84, armor: 0, mres: 0, gold: 4, lives: 1,
    dmg: [1, 3], rate: 0.8, size: 9,
    V: { spr: 'motociata', name: 'Motociata', desc: 'Passa roncando o motor antes que as torres reajam.' },
    R: { spr: 'rouanet', name: 'Bonde da Rouanet', desc: 'Artistas correndo atrás do edital antes que ele feche.' },
    tip: 'Os {tropa} seguram o bando; {o:archer} acaba com ele.',
  },
  nomad: {
    hp: 46, speed: 36, armor: 0, mres: 0, gold: 8, lives: 1,
    dmg: [2, 4], rate: 1.0, size: 10,
    ranged: { range: 115, dmg: [4, 8], rate: 1.5 },
    V: { spr: 'nicolau', name: 'Nicolau Selfie', desc: 'Para, filma e dispara lacração nos seus assessores e no herói.' },
    R: { spr: 'gleice', name: 'Gleice Megafone', desc: 'Grita palavra de ordem no megafone contra os seus assessores e o herói.' },
    tip: '{O:mage} e {o:artillery} o derrubam de longe. {h:blind} impede os disparos.',
  },
  scorpion: { aquatic: true,
    hp: 120, speed: 30, armor: 0.55, mres: 0, gold: 14, lives: 1,
    dmg: [6, 10], rate: 1.2, size: 14,
    V: { spr: 'general', name: 'General Logística', desc: 'Um manda, o outro obedece: marcha atrás de uma couraça de caixas de remédio.' },
    R: { spr: 'ze', name: 'Zé Guerreiro', desc: 'Punho erguido e jaqueta de guerreiro do povo: envelope e cotovelada não passam.' },
    tip: 'Couraça grossa: use {o:mage} ou {h:shred}.',
  },
  shaman: { aquatic: true,
    hp: 85, speed: 32, armor: 0, mres: 0.6, gold: 16, lives: 1,
    dmg: [2, 5], rate: 1.0, size: 10,
    heal: { r: 85, amt: 30, cd: 5 },
    V: { spr: 'michele', name: 'Michele Unção', desc: 'Canta no microfone e cura os aliados por perto.' },
    R: { spr: 'chuchu', name: 'Doutor Chuchu', desc: 'Médico de formação: receita calma e cura os aliados por perto.' },
    tip: 'Resiste {ao:mage}. {t:archer} e {tropa} primeiro.',
  },
  vulture: {
    hp: 44, speed: 56, armor: 0, mres: 0, gold: 9, lives: 1,
    flying: true, size: 12, dmg: [3, 6], rate: 1.0,
    V: { spr: 'dudu', name: 'Dudu Tarifaço', desc: 'Chega de balão, direto dos Estados Unidos, por cima dos assessores e dos barris.' },
    R: { spr: 'jatinho', name: 'Ministro do Jatinho', desc: 'Voa no jatinho oficial por cima dos assessores e dos barris.' },
    tip: '{t:archer}, {t:mage}, {t:cistern} e {t:windmill} o alcançam.',
  },
  beetle: {
    hp: 150, speed: 33, armor: 0.3, mres: 0, gold: 16, lives: 1,
    dmg: [5, 9], rate: 1.1, size: 12,
    burrow: { every: 6, dur: 2.4, speedMul: 1.7 },
    V: { spr: 'zambela', name: 'Zambela Fujona', desc: 'De vez em quando foge pra Itália: some, fica intocável e reaparece mais adiante.' },
    R: { spr: 'dilmae', name: 'Dilmãe Pedalada', desc: 'Dá pedaladas fiscais: some das contas, fica intocável e reaparece mais adiante.' },
    tip: 'Ataque quando ela volta. A {s:watch} acha até quem sumiu.',
  },
  bulwark: { aquatic: true,
    hp: 170, speed: 30, armor: 0.35, mres: 0, gold: 16, lives: 1,
    dmg: [5, 9], rate: 1.1, size: 12,
    frontShield: 0.8,
    V: { spr: 'boiada', name: 'Passador de Boiada', desc: 'Marcha atrás do boi, que segura tudo o que vem de frente.', tip: 'Torres atrás dele, {t:mage}, {t:artillery} e {tropa} ignoram o boi.' },
    R: { spr: 'taxad', name: 'Taxad', desc: 'Marcha atrás do Leão do Imposto, que segura tudo o que vem de frente.', tip: 'Torres atrás dele, {t:mage}, {t:artillery} e {tropa} ignoram o leão.' },
  },
  saboteur: { aquatic: true,
    hp: 75, speed: 56, armor: 0, mres: 0.3, gold: 14, lives: 1,
    dmg: [2, 5], rate: 0.9, size: 10,
    sabotage: { r: 85, dur: 5, cd: 9 },
    V: { spr: 'damaris', name: 'Damaris da Goiabeira', desc: 'Pinta as torres em volta de azul e de rosa. Pintada, a torre para.', tip: 'Mate-a rápido ou segure com {tropa}: bloqueada ela não pinta.' },
    R: { spr: 'pelego', name: 'Pelego da Greve', desc: 'Apita e as torres em volta entram em greve.', tip: 'Mate-o rápido ou segure com {tropa}: bloqueado ele não apita.' },
  },
  specter: { spr: 'lyra',
    name: 'Lyra Secreto', hp: 120, speed: 42, armor: 0, mres: 0.5, gold: 18, lives: 1,
    dmg: [4, 8], rate: 1.0, size: 11,
    stealth: true,
    desc: 'Do Centrão. Ninguém vê, ninguém sabe, ninguém assina: invisível para as torres. Na tempestade de fake news, corre ainda mais.',
    tip: '{O:banner} e os {tropa} por perto o revelam. Dano em área sempre acerta.',
  },
  brood: {
    hp: 420, speed: 22, armor: 0.5, mres: 0, gold: 28, lives: 2,
    dmg: [10, 16], rate: 1.3, size: 17,
    split: { type: 'scorpling', n: 5 },
    V: { spr: 'carluxo', name: 'Carluxo dos Robôs', desc: 'Carrega um notebook cheio de robôs. Ao cair, solta cinco.', tip: 'Tenha dano em área por perto para os robôs.' },
    R: { spr: 'busao', name: 'Busão da Caravana', desc: 'Ônibus fretado lotado. Ao parar, desce a excursão inteira.', tip: 'Tenha dano em área por perto para a excursão.' },
  },
  scorpling: {
    hp: 20, speed: 55, armor: 0.2, mres: 0, gold: 1, lives: 1,
    dmg: [1, 3], rate: 0.8, size: 7,
    V: { spr: 'robo', name: 'Robô de Zap', desc: 'Robozinho de mensagem em massa. Rápido e sempre em bando.' },
    R: { spr: 'excursao', name: 'Militante de Excursão', desc: 'Desceu do busão com bandeira e lanche. Rápido e sempre em bando.' },
    tip: '{t:artillery}, {s:geyser} e {s:tornado} limpam o bando.',
  },
  brute: {
    hp: 340, speed: 26, armor: 0.6, mres: 0, gold: 32, lives: 2,
    dmg: [14, 24], rate: 1.4, size: 15,
    V: { spr: 'valdomar', name: 'Valdomar do Partidão', desc: 'Carrega o partido nas costas e atropela assessores fracos.' },
    R: { spr: 'lulinha', name: 'Lulinha Ronaldinho', desc: 'O Ronaldinho dos negócios: dribla e atropela assessores fracos.' },
    tip: 'Couro duro: o dano {de:mage} passa direto.',
  },
  djinn: {
    hp: 130, speed: 46, armor: 0, mres: 0.75, gold: 22, lives: 1,
    flying: true, size: 13, dmg: [6, 10], rate: 1.0,
    V: { spr: 'veio', name: 'Véio da Estátua', desc: 'Voa montado na estátua da porta da loja. O brilho das joias mal arranha.' },
    R: { spr: 'pomba', name: 'Pomba do Foro', desc: 'Pomba vermelha que voa de reunião em reunião. O brilho das joias mal arranha.' },
    tip: '{t:archer} e {t:windmill} são a resposta.',
  },
  golem: { spr: 'centrao',
    name: 'O Centrão', hp: 950, speed: 19, armor: 0.75, mres: 0.1, gold: 60, lives: 3,
    dmg: [28, 42], rate: 1.8, size: 20, big: true,
    desc: 'Dezenas de deputados grudados num gigante só. Lento, enorme e sempre do lado de quem está ganhando.',
    tip: 'Concentre {o:mage} e segure-o com {tropa}.',
  },
  warlord: { spr: 'cacique',
    name: 'Cacique do Centrão', hp: 3000, speed: 22, armor: 0.45, mres: 0.25, gold: 250, lives: 10,
    dmg: [40, 60], rate: 1.6, size: 24, big: true, boss: true, aoe: 45,
    summon: { type: 'raider', n: 3, cd: 11 },
    desc: 'Manda na pauta: pisa em área e chama reforços de qualquer lado que pague mais.',
    tip: 'Mate os reforços rápido e segure-o longe da rampa.',
  },
  worm: {
    hp: 5000, speed: 15, armor: 0.35, mres: 0.3, gold: 600, lives: 20,
    size: 30, big: true, boss: true, unblockable: true, trample: { dmg: 30, r: 34 },
    wormBurrow: { every: 14, dur: 3.2, spawn: 'beetle', n: 3 },
    V: { spr: 'capitao_moto', name: 'Capitão Mito na Motociata', desc: 'Montado na moto gigante, ninguém segura. De tempos em tempos some e volta com a turma da fuga.' },
    R: { spr: 'janja_trio', name: 'Janjinha no Trio Elétrico', desc: 'Em cima do trio elétrico da comitiva, ninguém segura. De tempos em tempos sai do ar e volta com a turma da pedalada.' },
    tip: 'Não pode ser bloqueado. Dano máximo e Operação da PF.',
  },
  ifrit: { spr: 'fundao',
    name: 'Fundão Eleitoral', hp: 4300, speed: 13, armor: 0.3, mres: 0.5, gold: 900, lives: 20,
    size: 30, big: true, boss: true, flying: true, fire: true, dmg: [40, 70], rate: 1.5, aoe: 50,
    firestorm: { cd: 12, n: 3, r: 250, dur: 4 },
    summon: { type: 'djinn', n: 2, cd: 15 },
    desc: 'Bilhões voando por cima de tudo. Onde ele passa, as torres pegam fogo.',
    tip: 'Molhado {em:cistern}, ele encolhe e sofre muito mais. {s:tornado} pode derrubá-lo.',
  },
  heart: {
    hp: 9000, speed: 12, armor: 0.3, mres: 0.3, gold: 1000, lives: 20,
    size: 34, big: true, boss: true, final: true, unblockable: true, noEndless: true, trample: { dmg: 40, r: 38 },
    // entra com recurso duas vezes (66% e 33% da vida): some, volta pela estrada e chama a turma; perto dele as torres
    // atiram mais devagar (o mesmo motor do antigo Coracao da Fumaca)
    phases: [0.66, 0.33], smokeBack: 140, smokeSpawn: { types: ['raider', 'jackal', 'nomad'], n: 8 }, choke: { r: 140, rate: 1.4 },
    V: { spr: 'zeroum_chefe', name: 'Zero-Um, o Candidato', desc: 'O filho mais velho quer a faixa que foi do pai. Perto dele, as torres travam de medo do processo.' },
    R: { spr: 'lulala_chefe', name: 'Lulalá, o Candidato', desc: 'O Barba quer o quarto mandato. Perto dele, as torres travam de saudade.' },
    tip: 'Duas vezes ele entra com recurso: some e volta pela estrada com a turma. Perto dele, as torres atiram mais devagar.',
  },
};

// lado da chapa rival: copia nome, descricao e dica do lado da vez para o topo de cada adversario
DATA.setRival = side => {
  DATA.RIVAL = side;
  for (const k in DATA.ENEMIES) {
    const E = DATA.ENEMIES[k];
    if (E.tipAll === undefined) E.tipAll = E.tip || '';
    const S = E[side];
    if (!S) continue;
    E.name = S.name; E.desc = S.desc; E.tip = S.tip || E.tipAll; E.spr = S.spr;
  }
};
DATA.setRival('V');

// ---------------------------------------------------------------- TORRES
// ordem em que aparecem no jogo (e nos menus)
DATA.TOWER_ORDER = ['archer', 'barracks', 'mage', 'artillery', 'cistern', 'windmill', 'banner', 'market'];
DATA.START_TOWERS = ['archer', 'barracks'];
// obra: segundos para construir e para evoluir (a torre fica parada enquanto isso)
DATA.BUILD_TIME = 3;
DATA.UPGRADE_TIME = 3;
DATA.SLOTS = 5;

DATA.TOWERS = {
  archer: {
    name: 'Mensalinho', short: 'Mensalinho',
    desc: 'Envelopes de mesada disparados do guichê, um atrás do outro. Acerta voadores.',
    tiers: [
      { cost: 70, range: 150, rate: 0.8, dmg: [4, 7] },
      { cost: 110, range: 165, rate: 0.68, dmg: [8, 12] },
      { cost: 160, range: 180, rate: 0.58, dmg: [12, 18] },
    ],
    specs: ['ballista', 'blowgun'],
  },
  mage: {
    name: 'Joias da Arábia', short: 'Joias',
    desc: 'Brilho de joia de presente que ignora couraça. Estoura a partir do nível 2; no 3, cada terceiro disparo é um Diamante.',
    tiers: [
      { cost: 100, range: 140, rate: 1.5, dmg: [10, 18] },
      // burst: [raio, fracao do dano em volta]; big: a cada N disparos, Esfera Maior (x2 de dano, explosao maior)
      { cost: 160, range: 152, rate: 1.5, dmg: [22, 38], burst: [34, 0.35] },
      { cost: 240, range: 165, rate: 1.5, dmg: [38, 66], burst: [40, 0.35], big: 3 },
    ],
    specs: ['lightning', 'sun'],
  },
  artillery: {
    name: 'Petrolão', short: 'Petrolão',
    desc: 'Barris de petróleo que estouram em área. Não atinge voadores.',
    ground: true,
    tiers: [
      { cost: 120, range: 150, rate: 3.0, dmg: [9, 16], radius: 58 },
      { cost: 180, range: 156, rate: 3.0, dmg: [20, 36], radius: 64 },
      { cost: 260, range: 166, rate: 3.0, dmg: [34, 58], radius: 70 },
    ],
    specs: ['mortar', 'seismic'],
  },
  barracks: {
    name: 'Rachadinha', short: 'Rachadinha',
    desc: 'Gabinete que contrata 3 assessores para bloquear o caminho. O salário, ninguém pergunta.',
    noTarget: true,
    tiers: [
      { cost: 70, range: 145, hp: 50, dmg: [1, 3], armor: 0, rate: 1.0, respawn: 10 },
      { cost: 110, range: 150, hp: 95, dmg: [3, 6], armor: 0.15, rate: 1.0, respawn: 10 },
      { cost: 150, range: 155, hp: 150, dmg: [6, 10], armor: 0.3, rate: 1.0, respawn: 10 },
    ],
    specs: ['lancers', 'monks'],
  },
  cistern: {
    name: 'Lava a Jato', short: 'Lava a Jato',
    desc: 'Jatos de alta pressão que molham e retardam. Molhados sofrem mais com joias e choques.',
    tiers: [
      { cost: 90, range: 140, rate: 1.2, dmg: [3, 6], wet: 4, slow: 0.8, splash: 28 },
      { cost: 130, range: 150, rate: 1.1, dmg: [7, 12], wet: 4, slow: 0.75, splash: 32 },
      { cost: 190, range: 160, rate: 1.0, dmg: [12, 20], wet: 4.5, slow: 0.7, splash: 36 },
    ],
    specs: ['fountain', 'geyser'],
  },
  windmill: {
    name: 'Central do Zap', short: 'Zap',
    desc: 'Rajadas de mensagem encaminhada que empurram os adversários de volta. Dano dobrado em voadores.',
    tiers: [
      { cost: 100, range: 135, rate: 2.6, dmg: [6, 10], push: 24, radius: 34 },
      { cost: 150, range: 145, rate: 2.4, dmg: [12, 18], push: 30, radius: 36 },
      { cost: 210, range: 155, rate: 2.2, dmg: [20, 30], push: 36, radius: 40 },
    ],
    specs: ['tornado', 'sandblast'],
  },
  banner: {
    name: 'CPI', short: 'CPI',
    desc: 'Não ataca. Fortalece as torres ao redor e revela quem age escondido.',
    noTarget: true, support: true,
    tiers: [
      { cost: 110, range: 120, dmgB: 0.1, rangeB: 0.05 },
      { cost: 150, range: 130, dmgB: 0.15, rangeB: 0.07 },
      { cost: 220, range: 140, dmgB: 0.2, rangeB: 0.1 },
    ],
    specs: ['drums', 'watch'],
  },
  market: {
    name: 'Banco Vorcash', short: 'Vorcash',
    desc: 'Não ataca. Rende verba sempre que uma onda começa.',
    noTarget: true, support: true,
    tiers: [
      { cost: 100, range: 0, income: 22 },
      { cost: 120, range: 0, income: 42 },
      { cost: 160, range: 0, income: 66 },
    ],
    specs: ['bazaar', 'treasury'],
  },
};

// especializacoes (nivel 4) — cada uma com 2 habilidades de 3 niveis
DATA.SPECS = {
  ballista: {
    base: 'archer', name: 'Mensalão', cost: 230,
    desc: 'Malas de dinheiro pesadas que atravessam até 3 adversários em linha.',
    range: 205, rate: 1.55, dmg: [42, 64], pierce: 3,
    abilities: [
      { id: 'explosive', name: 'Mala Estourada', costs: [200, 150, 150],
        desc: 'A cada 4 disparos, a mala estoura em área.', vals: [45, 75, 110] },
      { id: 'eagle', name: 'Olho no Plenário', costs: [150, 120, 120],
        desc: 'Chance de acerto crítico com dano triplo.', vals: [0.1, 0.2, 0.3] },
    ],
  },
  blowgun: {
    base: 'archer', name: 'Dólar na Cueca', cost: 210,
    desc: 'Notas escondidas disparadas rápido. O cheiro gruda e ignora couraça.',
    range: 175, rate: 0.36, dmg: [6, 10], poison: 5,
    abilities: [
      { id: 'cloud', name: 'Chuva de Notas', costs: [180, 140, 140],
        desc: 'Joga uma nuvem de notas que fere e atrasa quem estiver dentro.', vals: [12, 20, 28] },
      { id: 'corrosive', name: 'Elástico Apertado', costs: [150, 120, 120],
        desc: 'O cheiro derrete a couraça e fica mais forte.', vals: [0.12, 0.22, 0.32] },
    ],
  },
  lightning: {
    base: 'mage', name: 'Corrente de Ouro', cost: 300,
    desc: 'Uma corrente de ouro que salta entre 4 adversários. Devastadora contra molhados.',
    range: 172, rate: 1.8, dmg: [40, 76], jumps: 3,
    abilities: [
      { id: 'overload', name: 'Choque de Quilates', costs: [175, 150, 150],
        desc: 'Cada salto pode atordoar o alvo.', vals: [0.15, 0.25, 0.35] },
      { id: 'storm', name: 'Chuva de Brilhantes', costs: [225, 150, 150],
        desc: 'Uma nuvem despeja brilhantes na área.', vals: [4, 6, 8] },
    ],
  },
  sun: {
    base: 'mage', name: 'Relógio de Ouro', cost: 300,
    desc: 'Reflexo contínuo do relógio de presente: esquenta quanto mais tempo mira.',
    range: 162, dps: [24, 105], ramp: 2.6,
    abilities: [
      { id: 'flash', name: 'Clarão de Diamante', costs: [200, 150, 150],
        desc: 'Um clarão que atordoa todos em volta do alvo.', vals: [1.0, 1.5, 2.0] },
      { id: 'burn', name: 'Ouro Quente', costs: [150, 120, 120],
        desc: 'O reflexo incendeia o alvo (molhados não pegam fogo).', vals: [10, 17, 25] },
    ],
  },
  mortar: {
    base: 'artillery', name: 'Refinaria Superfaturada', cost: 350,
    desc: 'Barris enormes, de longo alcance, pelo dobro do preço.',
    range: 190, rate: 3.4, dmg: [62, 112], radius: 84,
    abilities: [
      { id: 'cluster', name: 'Chuva de Barris', costs: [225, 175, 175],
        desc: 'A cada 3 disparos, o barril solta barris menores.', vals: [4, 6, 8] },
      { id: 'barrel', name: 'Óleo em Chamas', costs: [200, 150, 150],
        desc: 'Incendeia o chão por alguns segundos.', vals: [16, 26, 36] },
    ],
  },
  seismic: {
    base: 'artillery', name: 'Sonda do Pré-Sal', cost: 330,
    desc: 'Perfura o chão: dano e lentidão em todos ao redor.',
    range: 128, rate: 2.2, dmg: [30, 52], slow: 0.5,
    abilities: [
      { id: 'tremor', name: 'Tremor de Sonda', costs: [200, 150, 150],
        desc: 'Chance de atordoar cada adversário atingido.', vals: [0.2, 0.3, 0.4] },
      { id: 'chasm', name: 'Poço sem Fundo', costs: [250, 200, 200],
        desc: 'Abre um poço e engole um adversário comum.', vals: [18, 15, 12] },
    ],
  },
  lancers: {
    base: 'barracks', name: 'Chefe de Gabinete', cost: 230,
    desc: 'Assessores de elite, de terno e crachá, que chegam dando carteirada.',
    range: 160, hp: 240, dmg: [14, 22], armor: 0.45, rate: 1.0, respawn: 12,
    abilities: [
      { id: 'charge', name: 'Carteirada', costs: [150, 120, 120],
        desc: 'O primeiro golpe em cada adversário causa dano extra e atordoa.', vals: [2, 2.5, 3] },
      { id: 'shield', name: 'Foro Privilegiado', costs: [150, 120, 120],
        desc: 'Mais couraça e mais vida.', vals: [0.1, 0.2, 0.3] },
    ],
  },
  monks: {
    base: 'barracks', name: 'Funcionários Fantasmas', cost: 220,
    desc: 'Ninguém nunca viu no gabinete: os golpes passam direto por eles.',
    range: 160, hp: 185, dmg: [10, 16], armor: 0.1, rate: 0.6, respawn: 10, dodge: 0.25,
    abilities: [
      { id: 'heal', name: 'Atestado Médico', costs: [150, 120, 120],
        desc: 'Curam a si mesmos e aos aliados próximos.', vals: [12, 22, 32] },
      { id: 'palm', name: 'Pancada de Pasta', costs: [175, 140, 140],
        desc: 'Golpe de pasta 007 que fere todos ao redor.', vals: [30, 50, 75] },
    ],
  },
  fountain: {
    base: 'cistern', name: 'Força-Tarefa', cost: 220,
    desc: 'Arcos largos de espuma que molham grupos inteiros.',
    range: 170, rate: 1.0, dmg: [18, 28], wet: 5, slow: 0.65, splash: 52,
    abilities: [
      { id: 'spring', name: 'Banho de Loja', costs: [150, 120, 120],
        desc: 'Cura os assessores e o herói dentro do alcance.', vals: [6, 10, 15] },
      { id: 'mire', name: 'Lama do Esquema', costs: [180, 140, 140],
        desc: 'Espalha lama no caminho: retarda e molha.', vals: [3, 4.5, 6] },
    ],
  },
  geyser: {
    base: 'cistern', name: 'Vaza Jato', cost: 260,
    desc: 'Vazamento de alta pressão: dano alto, empurra e molha.',
    range: 180, rate: 1.5, dmg: [40, 64], wet: 4, slow: 0.7, push: 12,
    abilities: [
      { id: 'chill', name: 'Água Gelada', costs: [175, 150, 150],
        desc: 'Chance de congelar alvos molhados.', vals: [0.15, 0.25, 0.35] },
      { id: 'burst', name: 'Grampo Estourado', costs: [200, 160, 160],
        desc: 'Um vazamento estoura sob o adversário mais forte.', vals: [70, 110, 160] },
    ],
  },
  tornado: {
    base: 'windmill', name: 'Disparo em Massa', cost: 260,
    desc: 'Mensagens em massa que arrastam grupos inteiros para trás.',
    range: 165, rate: 2.0, dmg: [26, 40], push: 44, radius: 44,
    abilities: [
      { id: 'twister', name: 'Viralizou', costs: [200, 160, 160],
        desc: 'Solta um redemoinho de mensagens que volta pelo caminho atordoando quem toca.', vals: [30, 50, 75] },
      { id: 'skyward', name: 'Derruba Avião', costs: [150, 120, 120],
        desc: 'Derruba voadores: no chão, assessores e barris os alcançam.', vals: [2, 3.5, 5] },
    ],
  },
  sandblast: {
    base: 'windmill', name: 'Corrente do Zap', cost: 240,
    desc: 'Correntes rápidas de "repassem para todos" que ferem e atrapalham.',
    range: 160, rate: 1.6, dmg: [20, 32], push: 18, radius: 44,
    abilities: [
      { id: 'shred', name: 'Áudio de 8 Minutos', costs: [175, 140, 140],
        desc: 'Lixa a couraça de quem é obrigado a ouvir.', vals: [0.15, 0.25, 0.35] },
      { id: 'blind', name: 'Fake News nos Olhos', costs: [150, 120, 120],
        desc: 'Cega: sem disparos, curas ou sabotagens, e golpes mais fracos.', vals: [1.5, 2.5, 3.5] },
    ],
  },
  drums: {
    base: 'banner', name: 'Palanque da CPI', cost: 230,
    desc: 'Aura maior, mais dano e ataques mais rápidos para as torres vizinhas.',
    range: 150, dmgB: 0.22, rangeB: 0.1, rateB: 0.12,
    abilities: [
      { id: 'warcry', name: 'Holofote', costs: [175, 140, 140],
        desc: 'A cada 14 s, as torres na aura atacam 40% mais rápido.', vals: [3, 4.5, 6] },
      { id: 'march', name: 'Discurso Inflamado', costs: [150, 120, 120],
        desc: 'Assessores e herói na aura causam mais dano.', vals: [0.2, 0.35, 0.5] },
    ],
  },
  watch: {
    base: 'banner', name: 'Quebra de Sigilo', cost: 240,
    desc: 'Aura enorme que revela invisíveis e até quem sumiu.',
    range: 175, dmgB: 0.15, rangeB: 0.12, seeBurrow: true,
    abilities: [
      { id: 'mark', name: 'Convocação', costs: [175, 140, 140],
        desc: 'Convoca o adversário mais forte na aura: ele sofre mais dano.', vals: [0.15, 0.25, 0.35] },
      { id: 'bounty', name: 'Acordo de Leniência', costs: [150, 120, 120],
        desc: 'Adversários derrotados na aura rendem mais verba.', vals: [0.15, 0.3, 0.45] },
    ],
  },
  bazaar: {
    base: 'market', name: 'Emenda Pix', cost: 200,
    desc: 'Mais verba por onda e deputados do Centrão de aluguel.',
    range: 150, income: 95,
    abilities: [
      { id: 'mercs', name: 'Centrão de Aluguel', costs: [180, 140, 140],
        desc: 'Chama um deputado do Centrão que luta do seu lado por 18 s.', vals: [24, 19, 14] },
      { id: 'caravan', name: 'Emenda de Relator', costs: [150, 120, 120],
        desc: 'Verba extra a cada onda.', vals: [15, 30, 45] },
    ],
  },
  treasury: {
    base: 'market', name: 'CDB de 140%', cost: 220,
    desc: 'Renda fixa e juros sobre a verba guardada a cada onda. Bom demais para ser verdade.',
    range: 0, income: 60, interest: 0.05, cap: 60,
    abilities: [
      { id: 'compound', name: 'Juros Mágicos', costs: [150, 120, 120],
        desc: 'Juros maiores sobre a verba guardada.', vals: [0.08, 0.11, 0.14] },
      { id: 'vault', name: 'O FGC Garante', costs: [150, 120, 120],
        desc: 'Teto de juros mais alto.', vals: [100, 150, 220] },
    ],
  },
};

// altura do ponto de disparo de cada torre (tier 1..3, spec A, spec B)
DATA.TOWER_TOP = {
  archer: [53, 64, 82, 87, 54], // medido nos sprites do Blender (tools/sprites/empacotar.py): mao do arremesso, boca da mala, ponto 'top'
  // torres desenhadas por codigo: medidas na escala 1 e multiplicadas por TOWER_SCALE (1,3)
  mage: [53, 64, 74, 58, 30], // joia principal / medalhao / mostrador do relogio dos sprites (tools/sprites/empacotar.py)
  artillery: [43, 53, 64, 68, 40], // barril na concha do cavalete no disparo (tools/sprites/empacotar.py)
  barracks: [13, 13, 13, 13, 13],
  cistern: [17, 49, 58, 17, 57], // bico do canhao do lava-jato dos sprites
  windmill: [4, 6, 7, 74, 10], // centro da grade do ventilador dos sprites (Disparo em Massa: redemoinho de baloes do topo)
  banner: [37, 42, 47, 48, 54], // lente da lupa gigante dos sprites (Palanque: holofotes da trelica)
  market: [28, 32, 36, 26, 39], // cumeeira do banco / maquininha / monte de moedas dos sprites
};

// ---------------------------------------------------------------- CHAPAS E HEROIS
// cada chapa tem 2 herois; os da chapa rival sao os chefes das suas fases (worm e heart). Os ids internos sao os do
// motor original (jaci, caipora, benzedeira, boitata) porque o game.js escolhe o kit de habilidades por eles.
DATA.HERO_XP = [0, 200, 500, 900, 1400, 2000, 2700, 3500, 4400, 5400];
DATA.TALENT_LVLS = [3, 6, 9];
DATA.SIDES = {
  R: { name: 'Chapa Vermelha', heroes: ['jaci', 'caipora'], color: '#d8433b', dark: '#8f2420', lema: 'Faz o L!' },
  V: { name: 'Chapa Verde-Amarela', heroes: ['benzedeira', 'boitata'], color: '#2f9a4a', dark: '#1d6431', lema: 'Talkey?' },
};
DATA.HERO_ORDER = DATA.SIDES.R.heroes.slice();
DATA.HEROES = {
  jaci: {
    name: 'Lulalá', title: 'O Barba', side: 'R', sprite: 'hero', unlock: null,
    hp: 230, hpLvl: 26, dmg: [10, 17], dmgLvl: 2.2, armor: 0.25, rate: 0.85,
    speed: 92, respawn: 16, regen: 14, guard: 75,
    desc: 'O Barba voltou ao palanque. Segura a linha no gogó e manda o "L" em quem vem de longe.',
    abilities: [
      { id: 'whirl', name: 'Discurso de Palanque', desc: 'Gira o microfone e atinge todos ao redor.' },
      { id: 'hawk', name: 'Faz o L', desc: 'O "L" voa e atordoa um adversário distante.' },
    ],
    talents: [
      [{ id: 'hp', v: 0.2, name: 'Couro de Sindicalista', desc: '+20% de vida.' }, { id: 'dmg', v: 0.15, name: 'Gogó Afiado', desc: '+15% de dano.' }],
      [{ id: 'whirl', v: 0.35, name: 'Comício Longo', desc: 'Discurso de Palanque: +35% de dano e alcance.' }, { id: 'hawk', v: 0.5, name: 'L Turbinado', desc: 'O "L" volta 50% mais rápido.' }],
      [{ id: 'regen', v: 1, name: 'Picanha no Almoço', desc: 'Recupera vida 2x mais rápido.' }, { id: 'respawn', v: 0.5, name: 'Volta por Cima', desc: 'Volta na metade do tempo.' }],
    ],
  },
  caipora: {
    name: 'Janjinha', title: 'Primeira-Dama Influencer', side: 'R', sprite: 'caipora', unlock: 1,
    hp: 200, hpLvl: 22, dmg: [8, 14], dmgLvl: 1.8, armor: 0.15, rate: 0.9,
    speed: 100, respawn: 16, regen: 14, guard: 80, charm: 0.5,
    desc: 'Grava stories de tudo. Cada delação perto dela engaja mais, e a comitiva atende ao seu chamado.',
    abilities: [
      { id: 'call', name: 'Comitiva', desc: 'Dois assessores de viagem lutam ao lado dela por 12 s.' },
      { id: 'trail', name: 'Stories', desc: 'Os adversários em volta param para assistir e andam para trás por 2 s.' },
      { id: 'charm', name: 'Engajamento', desc: 'Passiva: +50% de Delação em todo adversário derrotado.' },
    ],
    talents: [
      [{ id: 'charm', v: 0.25, name: 'Viralizou', desc: '+25% de Delação (além do bônus dela).' }, { id: 'hp', v: 0.2, name: 'Look Blindado', desc: '+20% de vida.' }],
      [{ id: 'beasts', v: 1, name: 'Comitiva Maior', desc: 'A Comitiva traz 3 assessores.' }, { id: 'trail', v: 1, name: 'Live Longa', desc: 'Os Stories duram 1 s a mais.' }],
      [{ id: 'beastHp', v: 0.4, name: 'Seguranças Fortes', desc: 'Assessores da Comitiva com +40% de vida e dano.' }, { id: 'respawn', v: 0.5, name: 'Volta Ligeira', desc: 'Volta na metade do tempo.' }],
    ],
  },
  benzedeira: {
    name: 'Zero-Um', title: 'O Filho Mais Velho', side: 'V', sprite: 'benzedeira', unlock: null,
    hp: 180, hpLvl: 18, dmg: [6, 10], dmgLvl: 1.2, armor: 0.1, rate: 1.0,
    speed: 80, respawn: 16, regen: 18, guard: 70,
    desc: 'Herdou o sobrenome e o celular. Joga projetos de lei de longe, cassa quem está quase caindo e cura os aliados com o fundo partidário.',
    abilities: [
      { id: 'herb', name: 'Projeto de Lei', desc: 'Arremessa projetos de lei de longe (ignoram couraça).' },
      { id: 'bless', name: 'Cassação', desc: 'Cassa na hora um adversário com menos de 25% de vida: não dá verba, mas dá 3x mais Delação.' },
      { id: 'heal', name: 'Fundo Partidário', desc: 'Cura os aliados em volta dele.' },
    ],
    talents: [
      [{ id: 'heal', v: 0.4, name: 'Fundo Gordo', desc: 'O Fundo Partidário cura 40% a mais.' }, { id: 'hp', v: 0.2, name: 'Terno Blindado', desc: '+20% de vida.' }],
      [{ id: 'bless', v: 0.1, name: 'Cassação Ampla', desc: 'A Cassação pega quem tem até 35% de vida.' }, { id: 'herb', v: 0.4, name: 'Urgência Urgentíssima', desc: 'Os projetos de lei dão 40% a mais de dano.' }],
      [{ id: 'charm', v: 0.5, name: 'Delator de Estimação', desc: '+50% de Delação.' }, { id: 'respawn', v: 0.5, name: 'Volta Ligeira', desc: 'Volta na metade do tempo.' }],
    ],
  },
  boitata: {
    name: 'Capitão Mito', title: 'O Pai, de Tornozeleira', side: 'V', sprite: 'boitata', unlock: 1,
    hp: 260, hpLvl: 28, dmg: [9, 15], dmgLvl: 2, armor: 0.2, rate: 0.95,
    speed: 96, respawn: 18, regen: 12, guard: 60, fire: true,
    desc: 'Saiu de casa com tornozeleira e tudo, então não se afasta muito do ponto. Grita, acelera a moto e esquenta o ambiente.',
    abilities: [
      { id: 'flare', name: 'Imbrochável!', desc: 'Solta o grito e atinge todos em volta.' },
      { id: 'firetrail', name: 'Motociata', desc: 'Deixa um rastro de escapamento que fere quem passa.' },
      { id: 'burn', name: 'Ferro de Solda', desc: 'Passiva: os golpes queimam (água apaga).' },
    ],
    talents: [
      [{ id: 'dmg', v: 0.15, name: 'Talkey', desc: '+15% de dano.' }, { id: 'hp', v: 0.2, name: 'Histórico de Atleta', desc: '+20% de vida.' }],
      [{ id: 'flare', v: 0.35, name: 'Grito Maior', desc: 'Imbrochável!: +35% de dano e alcance.' }, { id: 'firetrail', v: 0.5, name: 'Motociata Longa', desc: 'O rastro dura 50% a mais.' }],
      [{ id: 'burn', v: 0.5, name: 'Solda Quente', desc: 'Queimaduras 50% mais fortes.' }, { id: 'respawn', v: 0.5, name: 'Volta Ligeira', desc: 'Volta na metade do tempo.' }],
    ],
  },
};
for (const k in DATA.HEROES) DATA.HEROES[k].id = k;
DATA.HERO = Object.assign(DATA.HEROES.jaci, { xp: DATA.HERO_XP });

// escolhe a chapa: herois da vez e a turma rival como adversaria
DATA.setSide = side => {
  DATA.SIDE = DATA.SIDES[side] ? side : 'R';
  DATA.HERO_ORDER = DATA.SIDES[DATA.SIDE].heroes.slice();
  DATA.setRival(DATA.SIDE === 'R' ? 'V' : 'R');
};
DATA.setSide('R');

// ---------------------------------------------------------------- OPERACOES (feiticos)
DATA.SPELLS = {
  fury: { name: 'Operação da PF', cd: 60, dmg: [60, 95], radius: 55, bolts: 3,
    desc: 'As viaturas da PF chegam às 6 da manhã na área escolhida. Molhados sofrem muito mais.' },
  riders: { name: 'Bancada de Apoio', cd: 16, n: 2, hp: 110, dmg: [5, 9], armor: 0.2, life: 20,
    desc: 'Dois deputados aliados entram na luta por 20 segundos.' },
  stampede: { name: 'Delação Premiada', cd: 6, cost: 60, n: 5, dmg: [26, 40], speed: 150, dist: 280, push: 28, stun: 0.5,
    desc: 'Os últimos delatores voltam correndo pela estrada, contra a própria turma: dano, empurrão e tontura.' },
};

// ---------------------------------------------------------------- RECONTAGEM
// ondas sem fim (game.endlessWave) no mapa de uma fase; libera ao vencer a fase unlock; recorde em Save.data.endless
DATA.ENDLESS = { level: 3, unlock: 3, name: 'Recontagem',
  desc: 'Ondas sem fim, cada vez mais fortes, com um chefe a cada 5. De 5 em 5 ondas, a sessão vira a madrugada. Até onde você segura?' };

// ---------------------------------------------------------------- DELACAO
// cada adversario derrotado vira delator e rende Delacao (gasta na Delacao Premiada)
DATA.CHARM = { max: 100, gain: 3, big: 6, boss: 25,
  desc: 'Cada adversário derrotado vira delator e rende Delação. Com a barra cheia, chame a Delação Premiada (tecla 3).' };

// ---------------------------------------------------------------- MELHORIAS (estrelas)
// custo em estrelas de cada nivel: ninguem compra tudo, entao a escolha importa
DATA.UPGRADE_COST = [1, 2, 2];
DATA.UPGRADES = {
  archer: { name: '{t:archer}', icon: 'archer', list: [
    { name: 'Guichê Alto', desc: '+10% de alcance.', V: { name: 'Pé Mais Alto' } },
    { name: 'Envelope Recheado', desc: '+15% de dano.', V: { name: 'Laranja Graúda' } },
    { name: 'Fila Rápida', desc: '+12% de velocidade de ataque.', V: { name: 'Colheita Rápida' } },
  ] },
  mage: { name: '{t:mage}', icon: 'mage', list: [
    { name: 'Quilate Puro', desc: '+10% de dano {de:mage}.', R: { name: 'Picanha Nobre' } },
    { name: 'Lupa de Joalheiro', desc: '+8% de alcance.', R: { name: 'Espeto Longo' } },
    { name: 'Brilho que Cega', desc: 'O brilho deixa o alvo 25% mais lento.', R: { name: 'Fumaça nos Olhos', desc: 'A fumaça deixa o alvo 25% mais lento.' } },
  ] },
  artillery: { name: '{t:artillery}', icon: 'artillery', list: [
    { name: 'Barril Cheio', desc: '+12% de raio de explosão.', V: { name: 'Lata Cheia' } },
    { name: 'Óleo Pesado', desc: '+15% de dano.', V: { name: 'Leite Grosso' } },
    { name: 'Mira Calibrada', desc: '+10% de alcance.' },
  ] },
  barracks: { name: '{t:barracks}', icon: 'barracks', list: [
    { name: 'Concurso Interno', desc: '+15% de vida dos {tropa}.', R: { name: 'Filiação em Massa' } },
    { name: 'Crachá Blindado', desc: '+10% de couraça.', R: { name: 'Colete do Sindicato' } },
    { name: 'Ponto Facultativo', desc: '{Tropa} voltam 30% mais rápido.', R: { name: 'Assembleia Relâmpago' } },
  ] },
  eng: { name: '{t:cistern} e {t:windmill}', icon: 'windmill', list: [
    { name: 'Sabão Forte', desc: '{t:cistern}: o molhado dura +2 s.', R: { name: 'Água do Lago' } },
    { name: 'Grupo da Família', desc: '{t:windmill}: +25% de empurrão, +10% de dano.', R: { name: 'Caixa de Som Extra' } },
    { name: 'Antena Nova', desc: '{t:cistern} e {t:windmill}: +10% de alcance.', R: { name: 'Megafone Novo' } },
  ] },
  cmd: { name: '{t:banner} e {t:market}', icon: 'banner', list: [
    { name: 'Relator Amigo', desc: '{t:banner}: +5% de bônus de dano.', V: { name: 'Engajamento Orgânico' } },
    { name: 'Taxa de Administração', desc: '{t:market}: +20% de verba por onda.', R: { name: 'Taxa sobre a Taxa' } },
    { name: 'Caixa Dois', desc: '+50 de verba inicial em toda fase.' },
  ] },
  charm: { name: 'Delação', icon: 'charm', list: [
    { name: 'Delator Falante', desc: '+25% de Delação em todo adversário derrotado.' },
    { name: 'Delação em Grupo', desc: 'Delação Premiada com 2 delatores a mais.' },
    { name: 'Acordo Rápido', desc: 'A Delação Premiada custa 45 de Delação.' },
  ] },
  spells: { name: 'Operações', icon: 'fury', list: [
    { name: 'Operação Grande', desc: 'Operação da PF com +2 viaturas.' },
    { name: 'Bancada Forte', desc: 'Bancada de Apoio com +30% de vida e dano.' },
    { name: 'Vazou Antes', desc: 'Recarga das operações 20% menor.' },
  ] },
};

// ---------------------------------------------------------------- FASES
// grupos de onda: [tipo, quantidade, intervalo, atraso, caminho]
// caminho: 0/1/2 = indice; -1 = alterna entre caminhos
// lotes: [x, y] normal, [x, y, 'h'] terreno elevado, [x, y, 'r', custo] ruinas
// unlock: torre liberada ao vencer; challenge: regra do desafio (vale 1 estrela)
const LV_BASE = [
  {
    name: 'Igarapé do Sossego', theme: 'oasis', gold: 300, lives: 20, gap: 16, seed: 11,
    desc: 'A aldeia ribeirinha precisa do igarapé limpo. A fumaça já chegou.',
    unlock: 'mage',
    challenge: { name: 'Só flechas', desc: 'Apenas Mirantes dos Arqueiros e só 5 vidas.', rules: { only: ['archer'], lives: 5 } },
    paths: [
      [[1340, 196], [1150, 196], [1010, 214], [930, 290], [900, 390], [800, 446], [660, 436], [580, 362], [540, 272], [450, 222], [330, 236], [258, 320], [266, 440], [356, 520], [470, 572], [540, 646], [558, 770]],
    ],
    spots: [[1100, 134], [1010, 316], [986, 396], [802, 378], [620, 632], [688, 374], [544, 188], [350, 324], [172, 402], [364, 442], [546, 542], [906, 202]],
    hero: [700, 360],
    water: [[790, 600, 120, 54], [690, 118, 92, 36]],
    waves: [
      [['raider', 6, 1.7]],
      [['raider', 8, 1.3], ['jackal', 3, 1.0, 7]],
      [['raider', 10, 1.1], ['nomad', 3, 2.2, 4]],
      [['jackal', 8, 0.7], ['raider', 8, 1.2, 3], ['scorpion', 1, 0, 11]],
      [['scorpion', 3, 3.5], ['raider', 10, 1.0, 2], ['nomad', 4, 1.6, 8]],
      [['raider', 14, 0.8], ['scorpion', 4, 2.6, 4], ['jackal', 10, 0.5, 12], ['nomad', 4, 1.5, 16]],
    ],
  },
  {
    name: 'Barranco Vermelho', theme: 'canyon', gold: 270, lives: 20, gap: 16, seed: 23,
    desc: 'O atalho pelo barranco é estreito. Os morros altos dão alcance extra.',
    unlock: 'artillery',
    challenge: { name: 'Sem reforços', desc: 'Sem a heroína: só torres e feitiços.', rules: { noHero: true } },
    paths: [
      [[620, -50], [620, 92], [540, 162], [380, 172], [262, 232], [250, 332], [340, 392], [560, 392], [760, 380], [900, 320], [1020, 252], [1132, 300], [1150, 420], [1060, 512], [880, 540], [760, 612], [760, 780]],
    ],
    spots: [[340, 306, 'h'], [750, 316], [532, 92], [164, 322], [536, 470], [1024, 454], [1054, 346, 'h'], [896, 242], [1234, 416], [696, 572], [706, 76], [858, 638]],
    hero: [640, 330],
    waves: [
      [['raider', 8, 1.3], ['jackal', 4, 0.8, 8]],
      [['vulture', 4, 1.6], ['raider', 8, 1.1, 3]],
      [['nomad', 6, 1.3], ['raider', 12, 0.8, 2], ['scorpion', 3, 2.6, 8]],
      [['shaman', 2, 4], ['raider', 14, 0.7, 1], ['jackal', 10, 0.45, 10], ['scorpion', 2, 3, 14]],
      [['vulture', 10, 0.9], ['scorpion', 5, 2.0, 3], ['nomad', 5, 1.4, 8]],
      [['jackal', 18, 0.4], ['shaman', 3, 3, 5], ['raider', 14, 0.7, 7]],
      [['scorpion', 7, 1.6], ['vulture', 8, 0.9, 4], ['shaman', 3, 3, 9], ['nomad', 8, 1.1, 12]],
      [['raider', 26, 0.45], ['scorpion', 8, 1.4, 4], ['vulture', 14, 0.6, 10], ['shaman', 5, 2.2, 14], ['brute', 3, 2.6, 18]],
    ],
  },
  {
    name: 'Cidade Perdida', theme: 'ruins', gold: 440, lives: 20, gap: 17, seed: 37,
    desc: 'Duas trilhas antigas se cruzam nas ruínas. Limpe os escombros para ganhar terreno.',
    unlock: 'cistern',
    challenge: { name: 'Engenharia enxuta', desc: 'No máximo 3 torres e sem a heroína.', rules: { maxTowers: 3, noHero: true } },
    paths: [
      [[-50, 120], [120, 122], [260, 150], [400, 150], [520, 170], [640, 214], [600, 290], [470, 330], [330, 362], [268, 440], [340, 520], [520, 542], [720, 522], [900, 472], [1040, 500], [1062, 590], [920, 642], [770, 650], [722, 780]],
      [[1330, 120], [1160, 122], [1020, 150], [880, 150], [760, 170], [640, 214], [600, 290], [470, 330], [330, 362], [268, 440], [340, 520], [520, 542], [720, 522], [900, 472], [1040, 500], [1062, 590], [920, 642], [770, 650], [722, 780]],
    ],
    spots: [[210, 374], [408, 276], [514, 254], [630, 132], [700, 292], [882, 228], [978, 230], [362, 452], [518, 478, 'r', 60], [226, 522], [932, 572], [750, 446], [710, 608], [1150, 536, 'r', 50], [828, 576], [310, 294]],
    hero: [640, 300],
    waves: [
      [['raider', 8, 1.2, 0, 0], ['raider', 8, 1.2, 4, 1]],
      [['jackal', 10, 0.5, 0, -1], ['nomad', 6, 1.4, 4, -1], ['raider', 8, 1, 8, -1]],
      [['scorpion', 4, 2.2, 0, 0], ['beetle', 4, 2.5, 3, 1], ['raider', 14, 0.8, 5, -1]],
      [['vulture', 10, 0.9, 0, -1], ['shaman', 3, 3, 4, -1], ['raider', 14, 0.8, 6, -1], ['scorpion', 3, 2, 12, -1]],
      [['brute', 3, 4, 0, -1], ['raider', 18, 0.6, 2, -1], ['nomad', 8, 1.0, 8, -1]],
      [['beetle', 8, 1.4, 0, -1], ['jackal', 16, 0.35, 6, -1], ['shaman', 4, 2.2, 10, -1], ['scorpion', 4, 2, 14, -1]],
      [['scorpion', 8, 1.3, 0, -1], ['vulture', 12, 0.6, 2, -1], ['brute', 4, 3, 9, -1]],
      [['raider', 30, 0.45, 0, -1], ['beetle', 8, 1.2, 5, -1], ['shaman', 5, 2, 10, -1], ['nomad', 10, 0.9, 12, -1]],
      [['brute', 6, 2.4, 0, -1], ['vulture', 14, 0.5, 3, -1], ['scorpion', 10, 1.0, 8, -1], ['jackal', 20, 0.3, 15, -1]],
      [['raider', 20, 0.5, 0, -1], ['warlord', 1, 0, 6, 0], ['beetle', 8, 1.3, 10, 1], ['shaman', 5, 2.5, 16, -1], ['brute', 4, 2.6, 22, -1], ['nomad', 10, 0.8, 26, -1]],
    ],
  },
  {
    name: 'Várzea Alagada', theme: 'dunes', gold: 450, goldMul: 1.15, lives: 20, gap: 17, seed: 41,
    desc: 'Água até o horizonte. O céu está cheio de asas, e os tracajás marcham em fila.',
    unlock: 'windmill',
    challenge: { name: 'Barranco frágil', desc: 'Apenas 5 vidas.', rules: { lives: 5 } },
    paths: [
      [[1340, 110], [1050, 110], [860, 128], [760, 198], [800, 292], [980, 322], [1128, 372], [1140, 462], [1020, 524], [800, 524], [620, 482], [500, 400], [460, 290], [360, 200], [230, 200], [150, 282], [160, 400], [262, 472], [362, 552], [420, 642], [432, 780]],
    ],
    spots: [[846, 238], [1080, 280], [684, 262], [810, 460], [1052, 436, 'h'], [1230, 448], [624, 410], [500, 628], [394, 334], [140, 176], [276, 272, 'h'], [234, 376], [900, 606], [338, 648], [664, 582]],
    hero: [560, 330],
    waves: [
      [['raider', 10, 1.0], ['vulture', 4, 1.4, 5]],
      [['jackal', 12, 0.5], ['nomad', 6, 1.4, 4]],
      [['djinn', 3, 3.0], ['raider', 12, 0.8, 2]],
      [['bulwark', 4, 2.2], ['vulture', 8, 0.9, 4], ['shaman', 3, 3, 8]],
      [['beetle', 8, 1.3], ['djinn', 4, 2.2, 6]],
      [['golem', 1, 0], ['raider', 16, 0.6, 2], ['bulwark', 4, 1.8, 8]],
      [['vulture', 16, 0.5], ['djinn', 6, 1.6, 6], ['jackal', 14, 0.4, 9]],
      [['brute', 4, 2.6], ['shaman', 4, 2.4, 3], ['bulwark', 6, 1.4, 6]],
      [['golem', 2, 8], ['beetle', 8, 1.2, 3], ['djinn', 6, 1.4, 10]],
      [['raider', 34, 0.35], ['nomad', 12, 0.7, 4], ['vulture', 16, 0.45, 8], ['brute', 4, 2.6, 12]],
      [['djinn', 9, 1.0], ['golem', 2, 6, 4], ['shaman', 6, 1.8, 6], ['bulwark', 8, 1.1, 12]],
      [['golem', 3, 5], ['brute', 6, 2.0, 3], ['djinn', 8, 1.1, 8], ['vulture', 18, 0.4, 12], ['bulwark', 8, 1.0, 16]],
    ],
  },
  {
    name: 'Gruta dos Vaga-lumes', theme: 'citadel', gold: 800, goldMul: 1.3, lives: 20, gap: 18, seed: 59,
    desc: 'Na gruta escura, algo enorme acordou. Ninhos de tucandeira infestam os túneis.',
    unlock: 'banner',
    challenge: { name: 'Arsenal de 3', desc: 'Leve só 3 tipos de torre.', rules: { slots: 3 } },
    paths: [
      [[180, -50], [186, 90], [290, 170], [450, 184], [570, 150], [680, 186], [690, 280], [640, 380], [560, 430], [440, 460], [360, 540], [420, 620], [580, 640], [760, 600], [920, 560], [1060, 600], [1110, 680], [1120, 780]],
      [[1340, 330], [1190, 312], [1070, 256], [950, 270], [880, 360], [760, 420], [640, 436], [560, 430], [440, 460], [360, 540], [420, 620], [580, 640], [760, 600], [920, 560], [1060, 600], [1110, 680], [1120, 780]],
    ],
    spots: [[332, 114], [444, 386], [466, 114], [546, 362], [598, 242, 'h'], [752, 346], [856, 262], [1182, 234], [800, 520], [602, 572], [322, 636], [324, 458], [458, 564, 'r', 70], [908, 642], [1174, 622], [1018, 672]],
    hero: [560, 520],
    waves: [
      [['raider', 10, 1.0, 0, 0], ['raider', 10, 1.0, 3, 1]],
      [['jackal', 10, 0.5, 0, -1], ['vulture', 6, 1.2, 4, -1], ['nomad', 4, 1.5, 8, 1]],
      [['scorpion', 6, 1.6, 0, -1], ['shaman', 3, 3, 5, -1], ['raider', 12, 0.8, 7, -1]],
      [['beetle', 8, 1.3, 0, -1], ['djinn', 3, 2.5, 5, -1]],
      [['brute', 4, 2.5, 0, -1], ['nomad', 8, 1.0, 4, -1], ['vulture', 10, 0.7, 8, -1]],
      [['golem', 1, 0, 0, 0], ['golem', 1, 0, 6, 1], ['brood', 2, 4, 2, -1], ['raider', 16, 0.5, 4, -1]],
      [['djinn', 8, 1.1, 0, -1], ['shaman', 5, 2.0, 4, -1], ['scorpion', 8, 1.2, 8, -1]],
      [['jackal', 24, 0.3, 0, -1], ['brood', 4, 2.4, 5, -1], ['brute', 4, 2.4, 10, -1]],
      [['warlord', 1, 0, 0, 1], ['raider', 20, 0.5, 2, 0], ['nomad', 8, 1.0, 8, -1]],
      [['golem', 2, 4, 0, -1], ['vulture', 20, 0.4, 3, -1], ['djinn', 8, 1.2, 9, -1]],
      [['brute', 6, 1.8, 0, -1], ['shaman', 5, 1.9, 4, -1], ['bulwark', 8, 1.1, 8, -1]],
      [['beetle', 14, 0.8, 0, -1], ['golem', 2, 5, 4, -1], ['brood', 4, 2, 10, -1]],
      [['djinn', 10, 0.9, 0, -1], ['vulture', 20, 0.4, 4, -1], ['brute', 6, 2, 8, -1], ['shaman', 6, 2, 12, -1]],
      [['golem', 4, 3.5, 0, -1], ['warlord', 1, 0, 8, 0], ['raider', 24, 0.4, 10, -1], ['nomad', 10, 0.8, 14, -1]],
      [['worm', 1, 0, 0, 0], ['beetle', 10, 1.2, 6, 1], ['djinn', 10, 1.0, 12, -1], ['brute', 6, 2.0, 18, -1], ['golem', 2, 6, 26, 1]],
    ],
  },
  {
    name: 'Temporal no Rio Negro', theme: 'storm', gold: 680, goldMul: 1.15, lives: 20, gap: 17, seed: 71,
    desc: 'O temporal encurta a visão das torres. Algo invisível caminha na chuva.',
    unlock: 'market',
    storm: { first: 55, every: 80, dur: 16, warn: 6 },
    challenge: { name: 'Temporal eterno', desc: 'Os temporais chegam com o dobro da frequência.', rules: { stormMul: 2 } },
    paths: [
      [[1340, 560], [1160, 566], [1030, 520], [980, 420], [1030, 316], [1010, 206], [880, 140], [720, 150], [620, 230], [650, 340], [720, 420], [650, 520], [500, 540], [370, 470], [350, 350], [260, 250], [140, 250], [80, 330], [-50, 400]],
    ],
    spots: [[1076, 462], [926, 348], [948, 262], [1068, 152, 'h'], [724, 240, 'h'], [624, 124], [468, 460], [742, 322, 'h'], [730, 564], [782, 484], [318, 522], [604, 466], [234, 332, 'h'], [46, 244], [394, 278], [956, 550]],
    hero: [700, 330],
    waves: [
      [['raider', 12, 1.0], ['jackal', 6, 0.6, 6]],
      [['nomad', 6, 1.3], ['bulwark', 4, 2.2, 4]],
      [['specter', 4, 2.5], ['raider', 12, 0.8, 3]],
      [['vulture', 10, 0.8], ['specter', 5, 2, 5], ['bulwark', 4, 2, 8]],
      [['brute', 4, 2.6], ['shaman', 3, 3, 4], ['raider', 14, 0.6, 6]],
      [['djinn', 6, 1.4], ['specter', 6, 1.6, 5], ['jackal', 16, 0.4, 9]],
      [['golem', 2, 6], ['bulwark', 10, 1.2, 3], ['nomad', 10, 0.9, 6]],
      [['specter', 12, 0.9], ['vulture', 16, 0.45, 4], ['brute', 5, 2.2, 8]],
      [['brood', 4, 3.5], ['beetle', 10, 1.1, 3], ['shaman', 4, 2.4, 8]],
      [['golem', 3, 5], ['specter', 12, 0.9, 4], ['djinn', 10, 1.1, 8]],
      [['bulwark', 14, 0.9], ['brute', 8, 1.8, 4], ['specter', 14, 0.8, 8], ['vulture', 18, 0.4, 12]],
      [['warlord', 1, 0], ['golem', 3, 4.5, 6], ['specter', 16, 0.75, 4], ['djinn', 12, 0.9, 10], ['brood', 4, 2.6, 14]],
    ],
  },
  {
    name: 'Furos e Comportas', theme: 'qanat', gold: 840, goldMul: 1.25, lives: 20, gap: 17, seed: 83,
    desc: 'Os furos do rio têm comportas: decida por onde a coluna passa. Cuidado com o Boto.',
    challenge: { name: 'Sem palafitas', desc: 'Palafitas proibidas.', rules: { ban: ['barracks'] } },
    paths: [
      [[-50, 120], [120, 130], [240, 170], [330, 250], [470, 230], [620, 240], [760, 262], [900, 340], [960, 440], [1000, 560], [900, 640], [720, 660], [560, 640], [440, 700], [400, 780]],
      [[-50, 120], [120, 130], [240, 170], [330, 250], [360, 370], [450, 460], [600, 500], [760, 470], [860, 400], [900, 340], [960, 440], [1000, 560], [900, 640], [720, 660], [560, 640], [440, 700], [400, 780]],
      [[1340, 200], [1200, 200], [1080, 250], [1000, 330], [960, 440], [1000, 560], [900, 640], [720, 660], [560, 640], [440, 700], [400, 780]],
    ],
    forks: [{ paths: [0, 1], ctrl: 2, lever: [226, 250] }],
    spots: [[610, 174], [278, 114], [374, 180], [734, 188], [936, 280], [492, 404], [786, 370, 'r', 70], [432, 322, 'r', 60], [514, 584], [688, 592], [886, 572], [1046, 422], [1078, 510], [1048, 190], [1042, 632], [264, 312]],
    hero: [600, 320],
    water: [[610, 420, 70, 26]],
    waves: [
      [['raider', 10, 1.0, 0, 0], ['jackal', 6, 0.6, 5, 2]],
      [['saboteur', 3, 3, 0, 0], ['raider', 12, 0.8, 3, -1]],
      [['scorpion', 6, 1.6, 0, 0], ['bulwark', 4, 2, 4, 2], ['nomad', 6, 1.2, 6, -1]],
      [['brood', 2, 5, 0, 0], ['saboteur', 4, 2, 4, 2], ['vulture', 10, 0.7, 6, -1]],
      [['beetle', 8, 1.2, 0, -1], ['specter', 6, 1.6, 4, 0], ['shaman', 4, 2.4, 6, -1]],
      [['golem', 2, 6, 0, 0], ['saboteur', 6, 1.5, 3, 2], ['raider', 18, 0.5, 5, -1]],
      [['brute', 6, 2, 0, 0], ['bulwark', 8, 1.2, 4, 2], ['djinn', 6, 1.4, 8, -1]],
      [['brood', 4, 3, 0, -1], ['saboteur', 6, 1.2, 4, -1], ['specter', 8, 1.2, 6, 0]],
      [['warlord', 1, 0, 0, 0], ['raider', 20, 0.5, 2, 2], ['nomad', 10, 0.8, 8, -1]],
      [['golem', 3, 4, 0, -1], ['djinn', 10, 1, 5, -1], ['saboteur', 8, 1, 8, 2]],
      [['bulwark', 14, 0.8, 0, 0], ['brute', 6, 2, 4, -1], ['vulture', 18, 0.4, 8, -1]],
      [['brood', 5, 2.5, 0, -1], ['specter', 12, 0.9, 4, 0], ['saboteur', 8, 1, 6, 2], ['golem', 2, 5, 10, 0]],
      [['warlord', 1, 0, 0, 0], ['golem', 3, 4, 6, -1], ['brute', 8, 1.6, 4, 2], ['djinn', 12, 0.8, 10, -1], ['saboteur', 10, 0.8, 14, -1]],
    ],
  },
  {
    name: 'Coração em Chamas', theme: 'ember', gold: 1200, goldMul: 1.45, lives: 20, gap: 18, seed: 97,
    desc: 'A queimada chegou ao coração da mata. O Boitatá desperta: é a batalha final.',
    storm: { first: 70, every: 95, dur: 15, warn: 6 },
    challenge: { name: 'Paneiro vazio', desc: 'Comece com 60% do ouro.', rules: { startGold: 0.6 } },
    paths: [
      [[-50, 150], [140, 160], [300, 220], [430, 200], [560, 250], [600, 360], [500, 440], [420, 540], [520, 620], [700, 620], [860, 560], [1000, 600], [1080, 680], [1100, 780]],
      [[1330, 150], [1140, 160], [990, 220], [860, 200], [740, 250], [600, 360], [500, 440], [420, 540], [520, 620], [700, 620], [860, 560], [1000, 600], [1080, 680], [1100, 780]],
    ],
    spots: [[266, 138], [366, 142], [520, 334], [640, 218, 'h'], [864, 282], [1146, 244], [996, 150], [656, 422, 'h'], [420, 418], [374, 612], [520, 548, 'r', 80], [624, 564], [726, 540], [882, 642], [1140, 632], [1026, 538], [410, 284, 'h']],
    hero: [560, 450],
    waves: [
      [['raider', 12, 0.9, 0, 0], ['raider', 12, 0.9, 3, 1]],
      [['jackal', 14, 0.4, 0, -1], ['nomad', 8, 1.2, 4, -1]],
      [['bulwark', 8, 1.4, 0, -1], ['saboteur', 4, 2, 4, -1]],
      [['djinn', 6, 1.6, 0, -1], ['vulture', 12, 0.6, 4, -1]],
      [['brood', 4, 3, 0, -1], ['shaman', 4, 2.5, 5, -1]],
      [['golem', 2, 6, 0, -1], ['specter', 8, 1.2, 4, -1]],
      [['brute', 8, 1.8, 0, -1], ['saboteur', 6, 1.4, 4, -1], ['nomad', 10, 0.9, 8, -1]],
      [['djinn', 8, 1.1, 0, -1], ['vulture', 14, 0.5, 4, -1], ['specter', 8, 1.2, 8, -1]],
      [['warlord', 1, 0, 0, 0], ['golem', 2, 5, 4, 1], ['raider', 24, 0.4, 6, -1]],
      [['brood', 6, 2.2, 0, -1], ['beetle', 12, 1, 4, -1], ['shaman', 6, 2, 8, -1]],
      [['bulwark', 16, 0.7, 0, -1], ['brute', 8, 1.6, 4, -1], ['saboteur', 8, 1, 8, -1]],
      [['golem', 3, 3.5, 0, -1], ['djinn', 10, 1.0, 6, -1], ['specter', 12, 0.8, 8, -1]],
      [['warlord', 1, 0, 0, 1], ['brood', 4, 2.4, 4, 0], ['vulture', 18, 0.4, 6, -1], ['brute', 6, 1.6, 10, -1]],
      [['golem', 4, 3.2, 0, -1], ['bulwark', 12, 0.7, 4, -1], ['specter', 12, 0.8, 8, -1], ['saboteur', 8, 0.9, 10, -1]],
      [['ifrit', 1, 0, 0, 0], ['djinn', 12, 1, 8, -1], ['brute', 8, 1.6, 14, -1], ['golem', 3, 5, 20, -1], ['specter', 12, 0.8, 24, -1]],
    ],
  },
  {
    name: 'Encontro das Águas', theme: 'encontro', gold: 1300, goldMul: 1.5, lives: 20, gap: 17, seed: 101,
    desc: 'O Negro e o Solimões correm lado a lado sem se misturar. A fumaça vem pelas duas margens.',
    challenge: { name: 'Sem catapultas', desc: 'Catapultas proibidas.', rules: { ban: ['artillery'] } },
    iron: ['archer', 'mage', 'cistern'], reg: 1,
    paths: [
      [[720, -50], [730, 70], [820, 160], [940, 190], [1040, 230], [1056, 330], [1062, 440], [1000, 540], [880, 612], [770, 650], [700, 780]],
      [[-50, 372], [110, 370], [250, 384], [360, 380], [430, 430], [470, 540], [530, 620], [640, 664], [700, 780]],
    ],
    spots: [[328, 432], [648, 616], [824, 96], [976, 456], [920, 232], [128, 320], [848, 672], [512, 520], [728, 616], [1112, 424], [240, 336], [720, 136], [928, 528]],
    hero: [760, 520],
    rivers: [{ pts: [[-80, 80], [150, 115], [330, 175], [470, 245], [600, 305]], w: 104, cor: 'negro' }, { pts: [[-80, 660], [150, 615], [330, 545], [470, 460], [600, 400]], w: 104, cor: 'barro' }, { pts: [[600, 352], [800, 362], [1000, 334], [1180, 304], [1360, 294]], w: 168, cor: ['negro', 'barro'] }],
    pontes: [[1055, 325, 81], [446, 474, 70]],
    waves: [
      [['saboteur', 4, 1.6, 0, 0], ['raider', 12, 0.8, 2, 1]],
      [['jackal', 12, 0.5, 0, 1], ['nomad', 8, 1.0, 3, 0]],
      [['scorpion', 5, 1.8, 0, -1], ['shaman', 3, 2.5, 4, 0]],
      [['bulwark', 5, 1.6, 0, 1], ['saboteur', 6, 1.2, 3, 0], ['vulture', 8, 0.7, 6, -1]],
      [['beetle', 6, 1.5, 0, -1], ['shaman', 4, 2, 4, 1], ['raider', 16, 0.5, 6, 0]],
      [['brood', 2, 5, 0, 0], ['saboteur', 8, 1, 3, 1], ['djinn', 4, 1.6, 6, -1]],
      [['brute', 4, 2.4, 0, -1], ['bulwark', 8, 1.1, 4, 1], ['specter', 4, 1.8, 8, 0]],
      [['golem', 2, 6, 0, 0], ['scorpion', 8, 1.2, 2, 1], ['nomad', 12, 0.7, 6, -1]],
      [['warlord', 1, 0, 0, 0], ['saboteur', 10, 0.8, 3, 1], ['vulture', 14, 0.5, 6, -1]],
      [['brood', 4, 3, 0, -1], ['shaman', 6, 1.6, 4, -1], ['bulwark', 10, 0.9, 6, 1]],
      [['golem', 3, 4, 0, -1], ['djinn', 10, 1, 5, -1], ['brute', 6, 1.6, 8, 1]],
      [['specter', 12, 0.9, 0, 0], ['saboteur', 12, 0.7, 4, 1], ['beetle', 10, 1, 8, -1]],
      [['brute', 8, 1.4, 0, -1], ['golem', 3, 4, 4, 1], ['vulture', 20, 0.4, 8, -1], ['shaman', 6, 1.4, 10, 0]],
      [['worm', 1, 0, 0, 1], ['bulwark', 12, 0.8, 4, 0], ['saboteur', 12, 0.7, 6, 1], ['djinn', 12, 0.8, 10, -1], ['golem', 2, 5, 14, 0]],
    ],
  },
  {
    name: 'Manguezal ao Luar', theme: 'mangue', gold: 1350, goldMul: 1.55, lives: 20, gap: 17, seed: 113,
    desc: 'Noite no mangue. No escuro, só as brasas denunciam os possuídos entre as raízes.',
    challenge: { name: 'Escuridão total', desc: 'Sem feitiços.', rules: { noSpells: true } },
    iron: ['mage', 'barracks', 'windmill'], reg: 1,
    night: true,
    paths: [
      [[1340, 140], [1180, 150], [1020, 188], [860, 206], [720, 200], [610, 236], [560, 300], [540, 384], [610, 456], [650, 548], [650, 640], [640, 780]],
      [[1340, 424], [1180, 430], [1040, 404], [900, 420], [760, 444], [610, 456]],
    ],
    spots: [[648, 384], [688, 496], [728, 248], [1080, 128], [1136, 376], [920, 464], [960, 144], [592, 600], [1160, 200], [560, 472], [1152, 472], [824, 160], [896, 376]],
    hero: [700, 380],
    water: [[230, 420, 60, 24], [1000, 680, 70, 22]],
    rivers: [{ pts: [[-80, 250], [200, 296], [420, 278], [640, 326], [860, 300], [1360, 262]], w: 70, cor: 'salobra' }, { pts: [[260, 800], [360, 620], [520, 528], [700, 560], [900, 520], [1360, 610]], w: 62, cor: 'salobra' }],
    pontes: [[558, 308, 103], [650, 551, 90]],
    waves: [
      [['raider', 14, 0.7, 0, 0], ['scorpling', 16, 0.4, 4, 1]],
      [['vulture', 10, 0.6, 0, -1], ['nomad', 8, 1, 3, 0]],
      [['specter', 4, 2, 0, 0], ['raider', 16, 0.6, 3, 1], ['jackal', 10, 0.4, 7, -1]],
      [['brood', 2, 5, 0, -1], ['scorpling', 20, 0.3, 4, 1], ['vulture', 8, 0.6, 6, 0]],
      [['shaman', 4, 2, 0, 0], ['specter', 6, 1.5, 3, 1], ['beetle', 5, 1.6, 6, -1]],
      [['djinn', 6, 1.2, 0, -1], ['saboteur', 8, 1, 3, 1], ['raider', 20, 0.5, 6, 0]],
      [['brute', 4, 2.4, 0, 0], ['specter', 8, 1.2, 4, 1], ['vulture', 14, 0.5, 8, -1]],
      [['golem', 2, 6, 0, 1], ['brood', 3, 4, 3, 0], ['scorpling', 24, 0.3, 6, -1]],
      [['warlord', 1, 0, 0, 0], ['specter', 10, 1, 3, 1], ['djinn', 8, 1.2, 7, -1]],
      [['beetle', 10, 1, 0, -1], ['shaman', 6, 1.5, 4, 0], ['nomad', 16, 0.6, 6, 1]],
      [['brute', 6, 1.8, 0, -1], ['djinn', 12, 0.8, 4, -1], ['specter', 12, 0.9, 8, 0]],
      [['golem', 3, 4, 0, -1], ['brood', 4, 3, 4, 1], ['vulture', 20, 0.4, 8, -1]],
      [['warlord', 1, 0, 0, 1], ['brute', 8, 1.4, 4, 0], ['specter', 14, 0.8, 6, -1], ['djinn', 10, 1, 10, -1]],
      [['ifrit', 1, 0, 0, 0], ['golem', 4, 3.5, 4, 1], ['specter', 16, 0.7, 6, -1], ['djinn', 14, 0.7, 10, -1], ['brood', 4, 3, 14, 0]],
    ],
  },
  {
    name: 'Cheia da Várzea', theme: 'cheia', gold: 1400, goldMul: 1.6, lives: 20, gap: 18, seed: 127,
    desc: 'O rio sobe de tempos em tempos. Na cheia, os lotes baixos alagam e as torres deles param.',
    challenge: { name: 'Só 3 torres', desc: 'Leve só 3 tipos de torre.', rules: { slots: 3 } },
    iron: ['archer', 'barracks', 'mage'], reg: 1,
    flood: { first: 55, every: 75, dur: 24, rise: 4, warn: 7 },
    paths: [
      [[-50, 196], [150, 208], [300, 276], [380, 396], [520, 466], [700, 440], [820, 330], [960, 250], [1100, 300], [1150, 440], [1060, 560], [900, 620], [780, 680], [740, 780]],
      [[1340, 120], [1200, 150], [1060, 200], [960, 250]],
    ],
    spots: [[1088, 248], [1040, 488, 'l'], [432, 368, 'l'], [712, 368, 'l'], [168, 272], [992, 312], [896, 672], [1176, 208], [512, 392, 'l'], [904, 336], [128, 152], [1088, 424], [616, 400, 'l'], [264, 320]],
    hero: [700, 520],
    water: [[600, 320, 70, 26], [300, 470, 50, 20]],
    rivers: [{ pts: [[-80, 560], [200, 520], [420, 560], [640, 600], [900, 560], [1360, 520]], w: 56, cor: 'barro' }],
    pontes: [[1071, 545, 127]],
    waves: [
      [['saboteur', 6, 1.4, 0, 0], ['raider', 14, 0.7, 3, 1]],
      [['jackal', 14, 0.4, 0, -1], ['shaman', 3, 2.5, 3, 0], ['nomad', 8, 1, 5, 1]],
      [['bulwark', 5, 1.6, 0, 0], ['scorpion', 5, 1.6, 3, 1]],
      [['saboteur', 10, 0.9, 0, -1], ['vulture', 10, 0.6, 4, 1], ['beetle', 4, 1.8, 6, 0]],
      [['brood', 3, 4, 0, 0], ['shaman', 5, 1.8, 3, 1], ['raider', 18, 0.5, 6, -1]],
      [['scorpion', 8, 1.2, 0, -1], ['saboteur', 10, 0.8, 4, 1], ['djinn', 5, 1.4, 8, 0]],
      [['golem', 2, 6, 0, 0], ['bulwark', 8, 1.1, 3, 1], ['vulture', 14, 0.5, 6, -1]],
      [['brute', 5, 2, 0, -1], ['shaman', 6, 1.5, 4, 0], ['saboteur', 12, 0.7, 6, 1]],
      [['warlord', 1, 0, 0, 0], ['scorpion', 10, 1, 3, 1], ['nomad', 14, 0.6, 6, -1]],
      [['beetle', 10, 1, 0, -1], ['bulwark', 10, 0.9, 4, 1], ['djinn', 8, 1.2, 8, 0]],
      [['golem', 3, 4, 0, -1], ['saboteur', 14, 0.6, 4, 1], ['specter', 8, 1.2, 8, 0]],
      [['brute', 8, 1.4, 0, 0], ['brood', 4, 3, 4, 1], ['vulture', 20, 0.4, 8, -1]],
      [['golem', 4, 3.5, 0, -1], ['shaman', 8, 1.2, 4, -1], ['saboteur', 14, 0.6, 8, 1], ['djinn', 12, 0.8, 12, 0]],
      [['worm', 1, 0, 0, 0], ['golem', 3, 4, 6, 1], ['bulwark', 14, 0.7, 4, -1], ['brute', 8, 1.4, 8, 1], ['djinn', 14, 0.7, 12, -1]],
    ],
  },
  {
    name: 'O Tepui da Fumaça', theme: 'tepui', gold: 1600, goldMul: 1.7, lives: 20, gap: 18, seed: 131,
    desc: 'No alto do tepui fica a fenda de onde sai a Fumaça Negra. O Coração dela bate lá dentro.',
    challenge: { name: 'Sem herói', desc: 'Enfrente o Coração sem herói.', rules: { noHero: true } },
    iron: ['archer', 'mage', 'artillery'], reg: 1,
    bossNight: true,
    paths: [
      [[620, -50], [630, 60], [520, 132], [380, 160], [300, 240], [360, 332], [520, 362], [700, 330], [860, 362], [940, 462], [880, 560], [1000, 640], [1160, 620], [1340, 600]],
      [[-50, 470], [120, 480], [260, 520], [420, 560], [600, 592], [760, 602], [880, 560]],
    ],
    spots: [[440, 256, 'h'], [808, 488], [1016, 576], [408, 464], [136, 536], [656, 384], [600, 536], [608, 128, 'h'], [1144, 576], [952, 528], [360, 248, 'h'], [816, 408], [488, 480], [720, 544]],
    hero: [640, 470],
    water: [[820, 190, 60, 22]],
    waves: [
      [['raider', 16, 0.6, 0, 0], ['jackal', 12, 0.4, 4, 1]],
      [['nomad', 10, 0.9, 0, -1], ['vulture', 10, 0.6, 3, 0]],
      [['scorpion', 5, 1.6, 0, 0], ['beetle', 5, 1.6, 3, 1], ['shaman', 3, 2.4, 6, -1]],
      [['brood', 3, 4, 0, -1], ['specter', 5, 1.6, 3, 0], ['saboteur', 8, 1, 6, 1]],
      [['brute', 4, 2.4, 0, 0], ['djinn', 6, 1.2, 3, 1], ['raider', 20, 0.5, 6, -1]],
      [['golem', 2, 6, 0, -1], ['bulwark', 8, 1.1, 3, 0], ['vulture', 14, 0.5, 6, 1]],
      [['warlord', 1, 0, 0, 0], ['specter', 8, 1.2, 3, 1], ['nomad', 14, 0.6, 6, -1]],
      [['brood', 4, 3, 0, -1], ['shaman', 6, 1.5, 4, 0], ['djinn', 10, 1, 6, 1]],
      [['brute', 8, 1.4, 0, -1], ['saboteur', 12, 0.7, 4, 1], ['beetle', 10, 1, 8, 0]],
      [['golem', 3, 4, 0, -1], ['specter', 12, 0.9, 4, 0], ['vulture', 20, 0.4, 8, 1]],
      [['worm', 1, 0, 0, 1], ['bulwark', 12, 0.8, 4, 0], ['djinn', 12, 0.8, 8, -1]],
      [['ifrit', 1, 0, 0, 0], ['brute', 8, 1.4, 4, 1], ['brood', 4, 3, 8, -1]],
      [['golem', 4, 3.5, 0, -1], ['warlord', 1, 0, 6, 1], ['specter', 14, 0.8, 4, 0], ['djinn', 14, 0.7, 10, -1]],
      [['heart', 1, 0, 0, 0], ['golem', 3, 4, 8, 1], ['brute', 8, 1.4, 12, -1], ['djinn', 16, 0.6, 16, -1], ['specter', 12, 0.8, 20, 0]],
    ],
  },
];

// as 5 fases de Brasilia usam, por enquanto, o tracado das fases do motor original (LV_BASE); os cenarios novos
// seguem esse tracado. unlock: torres liberadas ao vencer (lista)
const geo = i => { const L = LV_BASE[i], o = {}; for (const k of ['paths', 'spots', 'hero', 'water', 'rivers', 'pontes', 'forks', 'iron']) if (L[k]) o[k] = L[k]; return o; };
DATA.LEVELS = [
  Object.assign(geo(0), { name: 'Eixo Monumental', theme: 'oasis', gold: 300, lives: 20, gap: 16, seed: 11,
    desc: 'A caminhada começa na rodoviária. A turma do outro lado já desceu do ônibus.',
    unlock: ['mage', 'market'],
    challenge: { name: 'Só o básico', desc: 'Só {t:archer} e só 5 votos.', rules: { only: ['archer'], lives: 5 } },
    waves: LV_BASE[0].waves }),
  Object.assign(geo(1), { name: 'Esplanada dos Ministérios', theme: 'canyon', gold: 270, lives: 20, gap: 16, seed: 23,
    desc: 'Os blocos iguais dos ministérios. Os terraços altos dão alcance extra.',
    unlock: ['artillery', 'cistern'],
    challenge: { name: 'Sem herói', desc: 'Sem herói: só torres e operações.', rules: { noHero: true } },
    waves: LV_BASE[1].waves }),
  Object.assign(geo(3), { name: 'Congresso Nacional', theme: 'dunes', gold: 450, goldMul: 1.15, lives: 20, gap: 17, seed: 41, night: true, bossHp: 0.3,
    desc: 'Votação de madrugada: no escuro, sobe a rampa quem ninguém viu. O vice da chapa rival vem pessoalmente.',
    unlock: ['windmill', 'banner'],
    challenge: { name: 'Quórum baixo', desc: 'Apenas 5 votos.', rules: { lives: 5 } },
    waves: [...LV_BASE[3].waves, [['worm', 1, 0, 0, 0], ['raider', 10, 0.9, 4], ['jackal', 8, 0.6, 12]]] }),
  Object.assign(geo(5), { name: 'Praça dos Três Poderes', theme: 'storm', gold: 680, goldMul: 1.15, lives: 20, gap: 17, seed: 71,
    desc: 'Pombos, bandeirão e uma tempestade de fake news que encurta a visão das torres.',
    storm: LV_BASE[5].storm,
    challenge: { name: 'Fake news sem fim', desc: 'As tempestades chegam com o dobro da frequência.', rules: { stormMul: 2 } },
    waves: LV_BASE[5].waves }),
  Object.assign(geo(11), { name: 'Rampa do Planalto', theme: 'tepui', gold: 1200, goldMul: 1.45, lives: 20, gap: 18, seed: 131, hpMul: 0.8, bossHp: 0.4, bossNight: LV_BASE[11].bossNight,
    desc: 'A última subida. O candidato rival vem em pessoa, com recurso e tudo.',
    challenge: { name: 'Sem herói', desc: 'Enfrente o candidato sem herói.', rules: { noHero: true } },
    waves: [...LV_BASE[7].waves.filter(w => !w.some(g => g[0] === 'ifrit')), [['heart', 1, 0, 0, 0], ['brute', 4, 2, 6, -1], ['raider', 12, 0.8, 8, -1]]] }),
];

// posicao das fases no mapa de Brasilia (1280x720), ao lado dos marcos do fundo (tools/blender/mapa_brasilia.py, NODES):
// Rodoviaria, Esplanada, Congresso e Praca pela beira sul do Eixo Monumental; o Planalto ao norte da praca
DATA.WORLD = [
  { x: 300, y: 468 },
  { x: 604, y: 484 },
  { x: 806, y: 484 },
  { x: 1016, y: 470 },
  { x: 930, y: 190 },
];

// ---------------------------------------------------------------- TORRES DE CADA CHAPA
// Cada chapa defende a rampa com o proprio arsenal (escandalos e memes publicos do proprio lado); o motor e o mesmo
// em cada vaga, so mudam nome, textos e arte (folhas em js/sprites_meta.js para a V e js/sprites_meta_r.js para a R).
// art: artigo do nome curto (o/a/os/as) para os textos com marcadores ({o:archer}, {de:mage}...).
DATA.CHAPA_TORRES = {
  V: {
    tropa: 'assessores',
    archer: { name: 'Laranjal', short: 'Laranjal', art: 'o', desc: 'Laranjas arremessadas do pé, uma atrás da outra. Acerta voadores.' },
    mage: { name: 'Joias da Arábia', short: 'Joias', art: 'as' },
    artillery: { name: 'Leite Condensado', short: 'Leite Condensado', art: 'o', desc: 'Latas de leite condensado que estouram em área. Não atinge voadores.' },
    barracks: { name: 'Rachadinha', short: 'Rachadinha', art: 'a' },
    cistern: { name: 'Lava a Jato', short: 'Lava a Jato', art: 'o' },
    windmill: { name: 'Central do Zap', short: 'Zap', art: 'o' },
    banner: { name: 'Live do Cercadinho', short: 'Live', art: 'a', desc: 'Não ataca. O cercadinho anima as torres ao redor e revela quem age escondido.' },
    market: { name: 'Banco Vorcash', short: 'Vorcash', art: 'o' },
  },
  R: {
    tropa: 'militantes',
    archer: { name: 'Mensalinho', short: 'Mensalinho', art: 'o' },
    mage: { name: 'Churrascão da Picanha', short: 'Churrascão', art: 'o', desc: 'Espetos de picanha em brasa que ignoram couraça. Estoura a partir do nível 2; no 3, cada terceiro espeto é uma Picanha Premium.' },
    artillery: { name: 'Petrolão', short: 'Petrolão', art: 'o' },
    barracks: { name: 'Sindicato', short: 'Sindicato', art: 'o', desc: 'Sede do sindicato que manda 3 militantes de faixa e apito para bloquear o caminho.' },
    cistern: { name: 'Pedalinho do Sítio', short: 'Pedalinho', art: 'o', desc: 'Pedalinhos do lago do sítio que esguicham água: molham e retardam. Molhados sofrem mais com brasa e choques.' },
    windmill: { name: 'Carro de Som do Comício', short: 'Carro de Som', art: 'o', desc: 'Discurso no último volume que empurra os adversários de volta. Dano dobrado em voadores.' },
    banner: { name: 'CPI', short: 'CPI', art: 'a' },
    market: { name: 'Taxa das Blusinhas', short: 'Blusinhas', art: 'as', desc: 'Não ataca. Taxa cada pacote que chega: rende verba sempre que uma onda começa.' },
  },
};
// especializacoes que mudam de cara numa chapa: nome, descricao e habilidades (por id)
DATA.CHAPA_SPECS = {
  V: {
    ballista: { name: 'Laranjão', desc: 'Caixotes de laranja pesados que atravessam até 3 adversários em linha.', ab: {
      explosive: ['Suco Estourado', 'A cada 4 disparos, o caixote estoura em área.'],
      eagle: ['Laranja Premiada', 'Chance de acerto crítico com dano triplo.'] } },
    blowgun: { name: 'Candidatura Laranja', desc: 'Sementes cuspidas rápido. O azedo gruda e ignora couraça.', ab: {
      cloud: ['Nuvem de Bagaço', 'Joga uma nuvem de bagaço que fere e atrasa quem estiver dentro.'],
      corrosive: ['Ácido Cítrico', 'O azedo derrete a couraça e fica mais forte.'] } },
    mortar: { name: 'Compra de 15 Milhões', desc: 'Latas enormes, de longo alcance, pelo preço de 15 milhões.', ab: {
      cluster: ['Chuva de Latinhas', 'A cada 3 disparos, a lata solta latinhas menores.'],
      barrel: ['Calda Quente', 'Espalha calda quente no chão por alguns segundos.'] } },
    seismic: { name: 'Batedeira Industrial', desc: 'Bate o chão sem parar: dano e lentidão em todos ao redor.', ab: {
      tremor: ['Bate Forte', 'Chance de atordoar cada adversário atingido.'],
      chasm: ['Forma de Pudim', 'Abre uma forma de pudim e engole um adversário comum.'] } },
    drums: { name: 'Live de Quinta', desc: 'Aura maior, mais dano e ataques mais rápidos para as torres vizinhas.', ab: {
      warcry: ['Talkei?', 'A cada 14 s, as torres na aura atacam 40% mais rápido.'],
      march: ['Cercadinho Lotado', 'Assessores e herói na aura causam mais dano.'] } },
    watch: { name: 'Câmera da Live', desc: 'Aura enorme que revela invisíveis e até quem sumiu.', ab: {
      mark: ['Exposed na Live', 'Expõe o adversário mais forte na aura: ele sofre mais dano.'],
      bounty: ['Pix do Apoiador', 'Adversários derrotados na aura rendem mais verba.'] } },
  },
  R: {
    lightning: { name: 'Rodízio', desc: 'O espeto passa de prato em prato e salta entre 4 adversários. Devastador contra molhados.', ab: {
      overload: ['Brasa Viva', 'Cada salto pode atordoar o alvo.'],
      storm: ['Picanha pra Todos', 'Uma nuvem de fumaça despeja espetos na área.'] } },
    sun: { name: 'Maçarico do Churrasqueiro', desc: 'Chama contínua do maçarico: esquenta quanto mais tempo mira.', ab: {
      flash: ['Cervejinha Gelada', 'Uma rodada gelada que deixa todos em volta do alvo parados.'],
      burn: ['Bem Passado', 'A chama incendeia o alvo (molhados não pegam fogo).'] } },
    lancers: { name: 'Diretoria do Sindicato', desc: 'Militantes de elite, de colete e apito, que chegam fazendo piquete.', ab: {
      charge: ['Piquete', 'O primeiro golpe em cada adversário causa dano extra e atordoa.'],
      shield: ['Estabilidade no Emprego', 'Mais couraça e mais vida.'] } },
    monks: { name: 'Pelegos', desc: 'Ninguém sabe se trabalham: os golpes passam direto por eles.', ab: {
      heal: ['Licença Remunerada', 'Curam a si mesmos e aos aliados próximos.'],
      palm: ['Bandeirada', 'Golpe de bandeira que fere todos ao redor.'] } },
    fountain: { name: 'Lago do Sítio', desc: 'Arcos largos de água do lago que molham grupos inteiros.', ab: {
      spring: ['Domingo no Sítio', 'Cura os militantes e o herói dentro do alcance.'],
      mire: ['Barro do Sítio', 'Espalha barro no caminho: retarda e molha.'] } },
    geyser: { name: 'Pedalada Fiscal', desc: 'Pedalada de alta pressão: dano alto, empurra e molha.', ab: {
      chill: ['Água de Coco Gelada', 'Chance de congelar alvos molhados.'],
      burst: ['Pedalada Turbo', 'Um jato estoura sob o adversário mais forte.'] } },
    tornado: { name: 'Comício na Praça', desc: 'Discurso em massa que arrasta grupos inteiros para trás.', ab: {
      twister: ['Discurso de 3 Horas', 'Solta uma roda de ouvintes que volta pelo caminho e faz dormir quem toca.'],
      skyward: ['Microfonia', 'Derruba voadores: no chão, militantes e barris os alcançam.'] } },
    sandblast: { name: 'Jingle Chiclete', desc: 'Um jingle que gruda na cabeça: fere e atrapalha.', ab: {
      shred: ['Companheiros e Companheiras', 'Lixa a couraça de quem é obrigado a ouvir o discurso.'],
      blind: ['Volume no Máximo', 'Ensurdece: sem disparos, curas ou sabotagens, e golpes mais fracos.'] } },
    bazaar: { name: 'Receita do Taxad', desc: 'Mais verba por onda, e até o Centrão aparece para ajudar.', ab: {
      mercs: ['Centrão de Aluguel', 'O Centrão atende os dois lados: um deputado luta do seu lado por 18 s.'],
      caravan: ['Taxou!', 'Verba extra a cada onda.'] } },
    treasury: { name: 'Arcabouço Fiscal', desc: 'Renda fixa e juros sobre a verba guardada a cada onda. O arcabouço segura.', ab: {
      compound: ['Arrecadação Recorde', 'Juros maiores sobre a verba guardada.'],
      vault: ['Teto Flexível', 'Teto de juros mais alto.'] } },
  },
};

// troca os marcadores de um texto pelos nomes da chapa da vez:
// {t:tipo} nome curto, {T:tipo} nome completo, {o:tipo}/{O:tipo} com artigo, {de:..} {em:..} {ao:..} {um:..}/{Um:..}
// contracoes, {s:espec} especializacao, {h:habilidade} habilidade, {tropa}/{Tropa} quem sai do quartel
DATA.fmt = str => {
  if (!str || str.indexOf('{') < 0) return str;
  const C = DATA.CHAPA_TORRES[DATA.SIDE] || DATA.CHAPA_TORRES.R;
  const cap = x => x.charAt(0).toUpperCase() + x.slice(1);
  const CONTR = { de: { o: 'do', a: 'da', os: 'dos', as: 'das' }, em: { o: 'no', a: 'na', os: 'nos', as: 'nas' },
    ao: { o: 'ao', a: 'à', os: 'aos', as: 'às' }, um: { o: 'um', a: 'uma', os: 'uns', as: 'umas' } };
  return str.replace(/\{(\w+)(?::(\w+))?\}/g, (m, k, id) => {
    if (k === 'tropa') return C.tropa;
    if (k === 'Tropa') return cap(C.tropa);
    if (k === 's') return DATA.SPECS[id] ? DATA.SPECS[id].name : m;
    if (k === 'h') { for (const sp in DATA.SPECS) for (const a of DATA.SPECS[sp].abilities || []) if (a.id === id) return a.name; return m; }
    const T = C[id];
    if (!T) return m;
    if (k === 't') return T.short;
    if (k === 'T') return T.name;
    if (k === 'o' || k === 'O') { const w = T.art + ' ' + T.short; return k === 'O' ? cap(w) : w; }
    const low = k.toLowerCase();
    if (CONTR[low]) { const w = CONTR[low][T.art] + ' ' + T.short; return k === low ? w : cap(w); }
    return m;
  });
};

// aplica nomes, textos e especializacoes da chapa (guarda os textos de base na primeira vez)
DATA.applyChapaTorres = side => {
  const C = DATA.CHAPA_TORRES[side] || DATA.CHAPA_TORRES.R;
  for (const k in DATA.TOWERS) {
    const T = DATA.TOWERS[k];
    if (!T._base) T._base = { name: T.name, short: T.short, desc: T.desc };
    const o = C[k] || {};
    T.name = o.name || T._base.name; T.short = o.short || T._base.short; T.desc = o.desc || T._base.desc;
  }
  const SP = DATA.CHAPA_SPECS[side] || {};
  for (const k in DATA.SPECS) {
    const S = DATA.SPECS[k];
    if (!S._base) S._base = { name: S.name, desc: S.desc, ab: (S.abilities || []).map(a => [a.name, a.desc]) };
    const o = SP[k];
    S.name = o ? o.name : S._base.name;
    S.desc = o ? o.desc : S._base.desc;
    (S.abilities || []).forEach((a, i) => {
      const ab = o && o.ab && o.ab[a.id];
      a.name = ab ? ab[0] : S._base.ab[i][0];
      a.desc = ab ? ab[1] : S._base.ab[i][1];
    });
  }
  for (const k in DATA.UPGRADES || {}) {
    const G = DATA.UPGRADES[k];
    if (G._name === undefined) G._name = G.name;
    G.name = DATA.fmt(G._name);
    for (const u of G.list) {
      if (u._name === undefined) { u._name = u.name; u._desc = u.desc; }
      const o = u[side] || {};
      u.name = DATA.fmt(o.name || u._name);
      u.desc = DATA.fmt(o.desc || u._desc);
    }
  }
  for (const L of DATA.LEVELS || []) {
    const ch = L.challenge;
    if (!ch) continue;
    if (ch._desc === undefined) ch._desc = ch.desc;
    ch.desc = DATA.fmt(ch._desc);
  }
  // dica: sempre a partir do modelo (da variante do rival ou a comum), nunca do texto ja resolvido
  for (const k in DATA.ENEMIES) { const E = DATA.ENEMIES[k]; const S = E[DATA.RIVAL]; E.tip = DATA.fmt((S && S.tip) || E.tipAll || ''); }
  // altura de onde sai o disparo (ponto 'top' de cada arte; o empacotador mede): a do Churrascao difere das Joias
  if (!DATA.TOWER_TOP._base) DATA.TOWER_TOP._base = JSON.parse(JSON.stringify(DATA.TOWER_TOP));
  const TOPS = { R: { mage: [56, 62, 70, 57, 43] } }[side] || {};
  for (const k in DATA.TOWER_TOP._base) {
    const arr = TOPS[k] || DATA.TOWER_TOP._base[k];
    DATA.TOWER_TOP[k].splice(0, arr.length, ...arr);
  }
};
{
  const setSide0 = DATA.setSide;
  DATA.setSide = side => { setSide0(side); DATA.applyChapaTorres(DATA.SIDE); };
}
DATA.applyChapaTorres(DATA.SIDE);
