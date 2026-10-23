# Plano de produção

Conteúdo em `ROTEIRO.md`. Motor herdado do Guardiões da Mata (pasta irmã `Bastiao das Areias`), com as mesmas
ferramentas em `tools/` (Blender headless, empacotadores, testes Puppeteer; `tools/node_modules` aponta para lá).

## Etapas

- [x] 1. Projeto separado jogável: dados das duas chapas, 5 fases, escolha de chapa, textos (arte provisória da mata)
- [x] 2a. Conceitos v1 no KIE (`arte/conceitos/v1/`, painel em `arte/painel-conceitos-v1.jpg`)
- [x] 2b. Interface: peças KIE em `arte/conceitos/ui_pecas/` → `tools/sprites/ui_pecas.py` → `sprites/ui/`; logo novo
- [~] 3. Personagens (Higgsfield Tripo, 9 créditos cada): conceito KIE → GLB em `arte/modelos/rampa/` →
       `tools/blender/rampa_glb.py` (render/prova/vitrine) → `tools/sprites/empacotar_inimigos.py`
       - v1 (43 modelos, 387 créditos): 34 adversários + chefes, 4 heróis, aliados (bonecos genéricos)
       - v2 (20 pessoas, 180 créditos): foto + boneco v1 → rosto ainda genérico; GLBs guardados em `arte/modelos/rampa/v2/`
       - v3 (20 pessoas, 189 créditos): só a foto real + prompt de roupa (`arte/conceitos/para3d_v3/`, painel em
         `arte/painel-semelhanca-v3.jpg`); render em densidade 2.0 (`G.RES`); giros conferidos com `prova`
       - retratos dos heróis refeitos (`retrato.py -- <png> <modelo> -65 0.80 1.9`); moto do Capitão: sentado no banco, mão no guidão e joinha
       - esqueleto humano (`tools/blender/esqueleto.py`, `esqueleto='humano'` nas pessoas reais): pontas do corpo pela
         distância na superfície de uma cópia em voxels, braço seguindo o caminho até a mão, pesos de calor do Blender
         transferidos para o modelo; espera com gesto pequeno sobre a pose do modelo; ataque com braço até 0,7 rad
       - falta: lulinha sem foto (fica o genérico)
- [x] 4. Torres próprias de cada chapa (mesmo motor por vaga; nomes/textos em `DATA.CHAPA_TORRES`/`CHAPA_SPECS`, marcadores
       `{o:archer}` etc. em `DATA.fmt`). V em `arte/render/` → `js/sprites_meta.js`; R em `arte/render_r/` →
       `CHAPA=R tools/sprites/empacotar.py` → `js/sprites_meta_r.js` (o jogo troca no `SPR.setChapa`)
       - V: Laranjal (`torre_laranjal*.py`), Joias, Leite Condensado (`torre_leite.py`), Rachadinha, Lava a Jato, Zap,
         Live do Cercadinho (`torre_live.py`), Banco Vorcash
       - R: Mensalinho, Churrascão da Picanha (`torre_picanha.py`), Petrolão, Sindicato (`torre_sindicato.py`),
         Pedalinho do Sítio (`torre_pedalinho.py`), Carro de Som (`torre_carro_som.py`), CPI, Taxa das Blusinhas
         (`torre_blusinhas.py`); tropa do Sindicato = militantes (`soldier_r`, `lancers_r`, `monks_r`, `USPR.key`)
       - ícones: copiar `arte/render/icones` para `arte/render_r/icones` e rodar `CHAPA=R node tools/sprites/retratos.js`
- [x] 5. Cenários de Brasília no Blender: 5 fases, mapa e tela de início (luzes acendendo e flores de ipê no lugar da fumaça)
- [x] 6. Projéteis e efeitos temáticos: habilidades dos heróis (mão do L, Projeto de Lei, Imbrochável, Motociata), joias (corrente de ouro, baú),
       fake news, dinheiro, papelada; assinatura de cada personagem (`SIG_PROP` em `js/vfx.js` depende da posição dos adereços nas folhas)
- [x] 7. Sons e música: bossa (calm), samba (battle), plantão (boss), ambientes por fase, PF, urna (`tools/sons.html` para ouvir)
- [~] 8. Balanceamento (`tools/sim.js`): fases 3 e 5 com `bossHp`/`hpMul` (bot vence 26/30 e 24/30); falta a versão celular (`tools/web/montar_celular.py`)

## Fase 2 (pedida em 2026-10-23)

### 9. Ver melhor os personagens (a piada está neles)
- [x] 9a. Personagens 30% maiores na fase (`CHAR_SCALE` em `js/inimigos.js`)
- [x] 9b. 30% menos inimigos comuns por onda (`DATA.HORDA = 0.7`), cada um com 1/0,7 de vida e verba; fase 4 `hpMul 1.1`,
       fase 5 `hpMul 0.95` (bot: 30, 30, 25, 29 e 21 vitórias em 30)
- [x] 9c. Zoom de cinema nos momentos da piada: adversário novo (nome na tela), entrada do chefe, poder do herói
- [x] 9d. Zoom livre opcional (roda do mouse / pinça, até 2x, arrastar para mover), com clique certo em qualquer zoom
- [x] 9e. Cenários das 5 fases em 7680x4320 (6 px por unidade; `empacotar.py --cenario`), com meio-fio, marcas de pneu,
       pedrisco, capim, flores de ipê, bancos, lixeiras, base dos postes e poças na tempestade
- [ ] 9f. Peso do jogo na web: a tela inicial baixa 53 MB (todas as torres das duas chapas) e cada fase mais ~20 MB;
       carregar as torres só da chapa escolhida e os adversários só da fase, e uma versão web em meia resolução

### 10. A zoeira vai para o outro lado
Quem escolhe a Verde-Amarela vê o PT sendo zoado, e vice-versa. As torres do jogador viram símbolos simpáticos do
próprio lado; os escândalos ficam com a turma adversária, como poderes.
- [x] 10a. Torres amigáveis (`DATA.CHAPA_TORRES`/`CHAPA_SPECS`): V = Pomar do Agro, Gabinete Patriota, Tesouro
       Verde-Amarelo, Pão com Leite Condensado, Lava a Jato, Grupo do Zap da Família, Live do Cercadinho, Central do Pix;
       R = Carta ao Povo Brasileiro, Sindicato, Churrascão, Pré-Sal, Domingo no Sítio, Carro de Som, CPI, Indústria
       Nacional. Arte da Carta ao Povo: `tools/blender/torre_carta*.py` (cartas, malotes e santinhos, sem dinheiro)
- [x] 10b. Adversários com poderes de escândalo (`e.T.poder`, `updatePower` em `js/game.js`; Joias, Tarifaço, Vorcash e Mensalão
       afrouxados pelo bot) da turma deles, com nome, efeito visual e texto na tela:
       - rival Vermelha: Jatinho "Petrolão" (óleo na pista, quem passa escorrega mais rápido — novo), Zé Guerreiro
         "Mensalão" (suborna uma torre, que para — como a sabotagem), Dilmãe "Pedalada Fiscal" (some e reaparece à
         frente), Taxad "Leão da Receita" (escudo), Rouanet "Verba da Rouanet" (ao cair, cura quem está perto),
         Lulalá chefe "Entrou com recurso!"
       - rival Verde-Amarela: Zero-Um chefe "Rachadinha" (rouba parte da verba — novo), Capitão Mito "Joias da Arábia"
         (escudo de joias por alguns segundos — novo), Zambela "Fuga para a Itália", Michele "Vaquinha do Pix" (cura;
         sai a "Unção", sem piada com religião), Dudu "Tarifaço" (torres mais lentas perto dele), Carluxo
         "Gabinete do Ódio" (robôs), Damaris "Menino Veste Azul" (pinta a torre)
       - os dois lados: Lyra "Orçamento Secreto" (invisível), Cacique "Banco Vorcash" (cura a turma com dinheiro),
         Fundão Eleitoral
- [x] 10c. Dicas, bestiário e textos revisados (o bestiário mostra o poder como primeiro chip)

## Notas

- `L.theme` das fases continua com os nomes antigos (oasis, canyon, dunes, storm, tepui): o áudio e o tom de luz usam esses nomes.
- `tools/e2e.js` escolhe a Chapa Vermelha antes do mapa e usa as posições de `DATA.WORLD`.
- `tools/blender/arqueiros.py` (tripulação antiga) não é mais usado; a torre usa `mensalinho_pecas.py`.
