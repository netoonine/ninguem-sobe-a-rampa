# Ninguém Sobe a Rampa — roteiro

Sátira política em forma de tower defense. Obra de ficção: nomes trocados, caricatura por adereços, escândalos tratados
como os casos públicos que são, mesmo peso para os dois lados. Motor: o do Guardiões da Mata (Canvas 2D + sprites do
Blender). Este arquivo é a fonte da verdade do conteúdo; o `js/data.js` segue daqui.

## Premissa

Brasília, véspera da posse. A faixa presidencial está no alto da Rampa do Planalto. Você escolhe a sua chapa e não deixa
a turma do outro lado subir. Nas suas torres, os escândalos que todo mundo já conhece, porque **o esquema não tem
partido**.

- Vidas = **votos**. Ouro = **verba**. Encanto = **delação**.
- Adversário derrotado **vira delator**: larga a bandeira e sai correndo. A Delação Premiada manda os últimos delatores de
  volta pela estrada, contra a própria turma.

## Chapas (heróis)

Cada chapa tem 2 heróis. Os heróis da chapa rival são os chefões das suas fases.

| Chapa | Herói | Quem é | Kit (base do motor) | Habilidades |
|---|---|---|---|---|
| Vermelha | **Lulalá** | o Barba | jaci (linha de frente) | Discurso de Palanque (gira o microfone, área) · Faz o L (o "L" voa e atordoa de longe) |
| Vermelha | **Janjinha** | a primeira-dama influencer | caipora (chama aliados) | Comitiva (2 assessores de viagem lutam 12 s) · Stories (adversários param para assistir e andam para trás) · Engajamento (+50% de delação) |
| Verde-Amarela | **Zero-Um** | o filho mais velho | benzedeira (suporte) | Projeto de Lei (de longe) · Cassação (tira na hora quem tem menos de 25% de vida) · Fundo Partidário (cura os aliados) |
| Verde-Amarela | **Capitão Mito** | o pai, de tornozeleira | boitatá (área) | Imbrochável! (grito em área) · Motociata (rastro de escapamento que fere) · Tornozeleira (não se afasta muito do ponto) |

## Torres (as mesmas para os dois lados)

| Motor | Torre | Nível 4 A | Nível 4 B |
|---|---|---|---|
| archer | **Mensalinho**: envelopes de mesada, tiro rápido, acerta voadores | **Mensalão** (malas que atravessam 3) | **Dólar na Cueca** (notas escondidas, veneno) |
| barracks | **Rachadinha**: gabinete que contrata 3 assessores que bloqueiam | **Chefe de Gabinete** (carteirada) | **Funcionários Fantasmas** (esquivam) |
| mage | **Joias da Arábia**: brilho de joia de presente, ignora armadura | **Corrente de Ouro** (salta entre 4) | **Relógio de Ouro** (feixe contínuo) |
| artillery | **Petrolão**: barris de petróleo em área | **Refinaria Superfaturada** (longo alcance) | **Sonda do Pré-Sal** (bate no chão, deixa lento) |
| cistern | **Lava a Jato**: jatos de alta pressão, molha e retarda | **Força-Tarefa** (arcos largos) | **Vaza Jato** (vazamento de alta pressão) |
| windmill | **Central do Zap**: rajadas de mensagem que empurram | **Disparo em Massa** (tornado) | **Corrente do Zap** (cega) |
| banner | **CPI**: não ataca, fortalece as vizinhas e revela quem age escondido | **Palanque da CPI** (aura de velocidade) | **Quebra de Sigilo** (revela até quem some) |
| market | **Banco Vorcash**: rende verba a cada onda | **Emenda Pix** (+verba e Centrão de aluguel) | **CDB de 140%** (juros sobre a verba guardada; o FGC garante) |

Escândalos de cada campo: Mensalinho e Petrolão (vermelho), Rachadinha e Joias (verde-amarelo); Lava a Jato, Zap, CPI e
Vorcash são de todo mundo.

## Feitiços

- **Operação da PF** (era Fúria do Temporal): viaturas caem na área às 6 da manhã.
- **Bancada de Apoio** (Guardiões do Rio): 2 deputados aliados entram na luta por 20 s.
- **Delação Premiada** (Estouro da Mata): os últimos delatores voltam correndo contra a própria turma.

## Adversários

Mesma mecânica nos dois lados; muda quem é. Você enfrenta o lado oposto ao da sua chapa, mais o Centrão.

| Motor | Mecânica | Contra a Chapa Vermelha (verde-amarelos) | Contra a Chapa Verde-Amarela (vermelhos) |
|---|---|---|---|
| raider | básico, em fila | Patriota do Pneu | Militante da Mortadela |
| jackal | rápido, em bando | Motociata | Bonde da Rouanet |
| nomad | atira de longe nos aliados | Nikolas Selfie | Gleisi Megafone |
| scorpion | couraça | General Logística | Zé Guerreiro |
| shaman | cura os aliados | Michelle Unção | Doutor Chuchu |
| vulture | voa | Dudu Tarifaço (de balão, vindo dos EUA) | Ministro do Jatinho |
| beetle | some e corre | Zambelli Fujona (foge pra Itália) | Dilmãe Pedalada (pedalada fiscal) |
| bulwark | escudo na frente | Passador de Boiada (atrás do boi) | Taxad (atrás do Leão do Imposto) |
| saboteur | desliga torres | Damares da Goiabeira (pinta as torres de azul e rosa) | Pelego da Greve (as torres entram em greve) |
| brood → scorpling | ao cair, solta 5 | Carluxo dos Robôs → Robô de Zap | Busão da Caravana → Militante de Excursão |
| brute | pesado, atropela aliados | Valdemar Bigodão | Lulinha Ronaldinho (dribla os aliados) |
| djinn | voa e resiste a joias | Véio da Estátua (voa na estátua da loja) | Pomba do Foro |
| specter | invisível | **Lira Secreto** (Centrão, os dois lados) | idem |
| golem | gigante lento | **O Centrão** (deputados grudados num gigante) | idem |
| worm | chefe imbloqueável | Capitão Mito na Motociata Imbrochável | Janjinha no Trio Elétrico da Comitiva |
| warlord | chefe final, chama reforços | Zero-Um | Lulalá |

## Fases (Brasília)

1. **Eixo Monumental**: a rodoviária e o começo da caminhada.
2. **Esplanada dos Ministérios**: os blocos iguais, ipês amarelos.
3. **Congresso Nacional**: as cúpulas e o espelho d'água; votação de madrugada (noite). Chefe: o vice da chapa rival.
4. **Praça dos Três Poderes**: pombos, bandeirão; Tempestade de Fake News (alcance −25%). Aparece O Centrão.
5. **Rampa do Planalto**: a final. Chefe: o candidato rival.
- Modo sem fim: **Recontagem** (ondas sem fim).

## Direção de arte

- O mesmo 3D macio do Guardiões, com personagens **cabeçudos de caricatura**, como os bonecos de Olinda: cabeça grande,
  corpo pequeno, engraçados sem ser grotescos. A semelhança vem dos adereços (barba, tornozeleira, celular, faixa), não
  de rosto realista. Nada de imagem realista feita por IA.
- Brasília: concreto branco curvo, terra vermelha do cerrado, ipê amarelo, céu azul de seca, espelhos d'água.
- Interface: papel timbrado, carimbos, teclas da urna (CONFIRMA verde, CORRIGE laranja, BRANCO).
- Tela de início com o aviso: "Sátira política. Obra de ficção. Qualquer semelhança é mera coincidência… ou não."

## Regras de cuidado

- Nomes trocados; nada de crime inventado atribuído a pessoa real; escândalo citado é caso público.
- Mesmo número de adversários e o mesmo poder para os dois lados.
- Nada de ataque por gênero, aparência física ou religião em si: a piada é sobre o que a pessoa fez ou disse em público.
- Privado até depois da eleição (2º turno em 25/10/2026).
