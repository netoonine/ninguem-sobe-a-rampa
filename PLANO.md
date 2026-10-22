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
       - movimentos: pesos com a cabeça isolada do braço (`rig_biped`), espera com gesto pequeno sobre a pose do modelo,
         ataque com braço até 0,7 rad nas pessoas reais (`_limita_ergue`)
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

## Notas

- `L.theme` das fases continua com os nomes antigos (oasis, canyon, dunes, storm, tepui): o áudio e o tom de luz usam esses nomes.
- `tools/e2e.js` escolhe a Chapa Vermelha antes do mapa e usa as posições de `DATA.WORLD`.
- `tools/blender/arqueiros.py` (tripulação antiga) não é mais usado; a torre usa `mensalinho_pecas.py`.
