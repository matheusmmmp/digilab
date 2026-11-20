# Diagnóstico — desequilíbrio entre as 8 formas adultas do combate V21C

Status: **diagnóstico, só leitura** (2026-09-29). Nenhuma regra mudou: nada em `digilab/` nem em `web/`. Os
contrafactuais são montados no script, com as APIs públicas (`Perfil`, `ListaGambits`, `dataclasses.replace`, subclasses
de `Lutador` e `Condicao` definidas no próprio script).

- **Script:** `python experiments/diagnosticar_arquetipos.py --etapa todas` (~6 min com 8 processos).
- **Artefatos:** `artifacts_combate_v21c/diagnostico_arquetipos/` (`reproducao`, `mecanismo`, `atribuicao`, `leitura`,
  `epsilon`, `painel`, `candidatos`). Todo número abaixo vem deles, salvo os do E1, que vêm de
  `artifacts_linhagem/dono_ambiente/resultado.json` no branch `analise-dono-ambiente` (commit `44933d5`).
- **Regras:** as da validação V21C (`experiments/configs/v21c/validacao.json`, montadas por `run_bateria_v21.regras_de`;
  o `config_sha256` confere com o de `artifacts_combate_v21c/validacao/gates.json`).
- **Sementes:** só as de calibração (3101…3505), 100 partidas por par por semente e espécie (2.000 por par). As de
  validação (4101…4505) não foram usadas.
- **Força** de uma forma = média dos pontos contra as outras 7 (mesma espécie dos dois lados, média das 4 espécies).

## Resultado em cinco frases

1. **O colosso não tem lugar no ciclo.** O ciclo brigão > caçador > guardião > brigão existe; as três linhas dele
   vencem as duas formas do colosso. Titã e vigia perdem de todo mundo, exceto da muralha e um do outro.
2. **A causa principal é o pesado anunciado.** Toda lista adulta começa com "oponente preparando → resposta".
   O pesado do colosso é esquivado, interrompido, defendido e refletido, ou erra porque o caçador recuou. Sem essa
   leitura nos oponentes, o titã vai de 0,173 a 0,474 e o vigia de 0,248 a 0,494.
3. **O furioso vence pelas regras da base e pela lista do brigão, não pela passiva nem pelos stats.** Nenhuma alavanca
   da forma o leva abaixo de 0,66. Ele esmaga os caçadores (investida e avanço contra recuo) e os colossos (golpe
   rápido que interrompe o preparo, esquiva do pesado). Só perde para o contra-golpe (reflexo e parry).
4. **Stats de forma quase não pesam** (variação máxima 0,049). Técnica e lista de gambits decidem. A pele dura vale
   ~0 (titã −0,005, vigia −0,010), e a passiva do vigia só vale no confronto com o titã.
5. **O "tudo ou nada" é, em parte, determinismo dos bots; o desequilíbrio, não.** Com ε 0,30, os pares extremos caem
   de 17 para 11 de 28. A amplitude da força não cai (0,58 → 0,63) e o furioso passa a vencer todos.

## 0. Conferência (`reproducao.json`)

- A matriz de `artifacts_combate_v21c/calibracao/v4` (mesmas regras, N = 40) sai **idêntica byte a byte**. Os fontes
  de `v21/` mudaram desde a validação (`regras_sha256` diferente), mas as partidas não mudaram.
- Na base N = 100 de calibração, a força difere da validação em no máximo 0,005 por forma. O maior desvio de par é
  0,017 (muralha × vigia).

| forma | calibração (base) | validação |
|---|---|---|
| furioso | 0,755 | 0,753 |
| sentinela | 0,648 | 0,646 |
| espelho | 0,640 | 0,645 |
| emboscador | 0,615 | 0,616 |
| duelista | 0,521 | 0,518 |
| muralha | 0,400 | 0,403 |
| vigia | 0,248 | 0,248 |
| titã | 0,173 | 0,171 |

Equilíbrio na calibração: suporte de 5 (furioso 0,348, emboscador 0,202, muralha 0,202, espelho 0,198,
sentinela 0,051). Pares fora de [0,1; 0,9]: 17 de 28.

## 1. O que faz o furioso vencer (`mecanismo.json`, por partida)

| confronto | pontos | o que acontece |
|---|---|---|
| × sentinela | 1,00 | investida 63,1 de dano, golpe 37,7; o furioso sofre 26,6 e termina com 0,73 da vida |
| × emboscador | 1,00 | investida 51,1, golpe 40,5; sofre 28,1 |
| × titã | 0,99 | o titã prepara 5,53 pesados: 2,42 interrompidos; dos 2,93 executados, 1,08 esquivados. Golpe do furioso: 64,8 |
| × vigia | 0,99 | o vigia prepara 7,57: 3,74 interrompidos; dos 3,75 executados, 2,59 esquivados. Golpe do furioso: 100,5 |
| × duelista | 0,92 | 10,2 turnos; o duelista prepara 2,73 e 1,67 são interrompidos; golpe 65,1 × 42,5 |
| × espelho | 0,32 | o espelho reflete 91,3 (70,5 vindos do golpe rápido do furioso) |
| × muralha | 0,06 | a muralha reflete 80,0 (54,2 do golpe) e ainda tira 15,9 de parry |

- **Contra os caçadores**, quem decide é a regra da base. Com a fuga condicionada (C3), o recuo não afasta de quem
  avança, e a investida acerta na distância média. Sem a técnica, o furioso ainda faz 0,92 e 0,99
  (`atribuicao.json`). A passiva da sentinela (recuo que vale contra avanço) dispara 1,43 vez por partida contra o
  furioso e não muda nada: sem ela, a sentinela perde 0,001 de força.
- **Contra os colossos**, o golpe rápido barato interrompe o preparo, e a regra 1 da lista ("oponente preparando →
  esquivar") lê o pesado.
- A passiva dispara 4,04 vezes por partida e rende 5,56 de dano. Desligada, custa só 0,023.

## 2. O que faz titã e vigia perderem

| confronto | titã | vigia | mecanismo |
|---|---|---|---|
| × sentinela | 0,02 | 0,03 | o caçador recua durante os 2 turnos do preparo: 4,98 dos 5,17 pesados do titã erram por distância (vigia: 2,86 de 2,96). 75% (titã) e 98% (vigia) acabam no limite. O titã causa 4,6 de dano e sofre 80,2; usa a pele 10,3 vezes para evitar 2,1 |
| × emboscador | 0,01 | 0,03 | igual: 4,83 de 5,01 erram por distância (vigia 2,90 de 3,00) |
| × espelho | 0,04 | 0,01 | o espelho lê o preparo e responde com contra-golpe: 3,94 dos 4,18 pesados do titã são defendidos (vigia 5,09 de 5,38), e o reflexo do pesado tira 61,3 (vigia 54,9) |
| × furioso | 0,01 | 0,01 | ver acima: interrupção e esquiva |
| × duelista | 0,48 | 0,09 | o vigia prepara 8,14: 4,15 são interrompidos, e 2,83 dos 3,90 executados são esquivados |
| × muralha | 0,61 | 0,61 | a única vitória fora da linha: 106,5 de pesado contra 102,5 de reflexo; os dois terminam quase mortos |
| titã × vigia | — | 0,955 | a passiva do vigia (ver a intenção de preparar e golpear antes) dispara 11,73 vezes e interrompe 6,98 preparos por partida |

- **Pesado anunciado** (`leitura.json`). Tirando dos 7 oponentes as regras com `oponente_preparando`, o titã
  vai a 0,474 (+0,301) e o vigia a 0,494 (+0,247). O titã passa a vencer o espelho (0,04 → 0,92) e a muralha
  (0,61 → 1,00). Continua perdendo do furioso (0,07) e dos caçadores (0,03 e 0,04): esses dois problemas são outros.
- **A pele dura não responde a nada disso.** Ela só impede a interrupção (1,34 preparos protegidos por partida no
  titã) e corta o dano pela metade. Não impede esquiva, postura, reflexo nem fuga. Desligar a técnica custa 0,005
  (titã) e 0,010 (vigia).
- **A passiva do vigia vale quase só contra o titã.** Sem ela, o vigia vai de 0,955 a 0,04 contra o titã. Contra o
  resto quase não muda (o maior efeito é contra o duelista, 0,09 → 0,04). No total, −0,142.
- **Limite da linguagem:** não há condição sobre o próprio efeito ativo ("estou com pele"). O colosso não consegue
  escrever "só prepare sob pele". Dos 6,85 preparos do titã por partida, 2,06 são interrompidos, e preparo
  interrompido é, por definição, preparo sem pele.

## 3. Atribuição da força (`atribuicao.json`, `leitura.json`)

Uma alavanca por vez, só na forma medida; os oponentes são os bots canônicos. As partidas usam os mesmos nomes e
sementes da base (números aleatórios comuns). O erro padrão entre sementes fica em ≤ 0,005 para todas as células.

| forma | força | (a) sem passiva | (b) sem técnica | (c) stats sem delta da forma | (c′) stats só da espécie | (d) gambits da irmã | (e) passiva da irmã | sem ler o preparo | oponentes sem ler |
|---|---|---|---|---|---|---|---|---|---|
| furioso | 0,755 | −0,023 | −0,094 | −0,012 | −0,038 | −0,052 | −0,022 | −0,042 | +0,086 |
| sentinela | 0,648 | −0,001 | −0,150 | −0,005 | −0,021 | −0,105 | +0,066 | −0,011 | 0,000 |
| espelho | 0,640 | −0,151 | −0,516 | +0,030 | −0,109 | −0,301 | −0,147 | −0,307 | +0,025 |
| emboscador | 0,615 | −0,048 | −0,163 | +0,010 | −0,001 | +0,094 | −0,052 | −0,008 | +0,001 |
| duelista | 0,521 | −0,011 | −0,384 | −0,012 | +0,009 | +0,090 | +0,042 | −0,079 | +0,183 |
| muralha | 0,400 | −0,019 | −0,373 | −0,049 | −0,171 | +0,197 | −0,016 | −0,265 | +0,009 |
| vigia | 0,248 | −0,142 | −0,010 | +0,007 | −0,036 | −0,150 | −0,018 | −0,103 | +0,247 |
| titã | 0,173 | −0,048 | −0,005 | −0,003 | −0,057 | +0,006 | −0,048 | −0,037 | +0,301 |

Leitura:

- **Técnica** é o pilar do duelista, das duas guardiãs e dos caçadores (−0,15 a −0,52). No furioso vale −0,094; nos
  colossos, nada.
- **Stats da forma** não explicam nada (|Δ| ≤ 0,049). Os stats da linha pesam na guardiã (c′: muralha −0,171,
  espelho −0,109).
- **Gambits** são a segunda maior alavanca. A lista da muralha é a pior da linha: com a do espelho, ela sobe +0,197.
  O duelista sobe +0,090 com a lista do furioso.
- **Passiva** pesa no espelho (−0,151, o contra-golpe à distância contra o disparo) e no vigia (−0,142, só contra o
  titã). Nas outras formas fica em ≤ 0,05.
- **(e) Trocar a passiva do vigia e do titã** não tem efeito próprio. A passiva do vigia só existe pela condição
  `oponente_vai_preparar` da lista dele. O titã com a passiva do vigia não tem regra que a use: por construção,
  equivale a "sem passiva".

## 4. Efeito do ε (`epsilon.json`)

ε trocado nos 8 bots, dos dois lados.

| ε | furioso | sentinela | espelho | emboscador | duelista | muralha | vigia | titã | pares fora de [0,1; 0,9] | amplitude | suporte |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0,750 | 0,679 | 0,732 | 0,554 | 0,500 | 0,375 | 0,250 | 0,161 | 19 | 0,589 | 3 |
| 0,05 (hoje) | 0,755 | 0,648 | 0,640 | 0,615 | 0,521 | 0,400 | 0,248 | 0,173 | 17 | 0,582 | 5 |
| 0,15 | 0,805 | 0,634 | 0,522 | 0,644 | 0,550 | 0,332 | 0,294 | 0,218 | 12 | 0,587 | 3 |
| 0,30 | 0,872 | 0,619 | 0,404 | 0,640 | 0,580 | 0,241 | 0,341 | 0,304 | 11 | 0,631 | 1 (furioso domina) |

- Com ε 0 não há acaso nenhum, porque a resolução não usa rng: cada par e espécie tem um resultado por ordem de
  lados. Os confrontos 0/1 são, em parte, isso: o ε tira 8 dos 19 pares extremos.
- **O desequilíbrio é da regra e das listas.** A amplitude fica em 0,58–0,63 com qualquer ε. Mais ruído ajuda o
  agressivo (furioso 0,872) e derruba os reativos, que dependem de ler o oponente (espelho 0,404, muralha 0,241).
- **Aumentar o ε não é correção.** Com ε 0,30 o furioso vence todas as outras formas.

## 5. Contra o painel B da pesquisa (`painel.json`)

Pet = bot canônico da forma (caráter canônico, condição 1,0, sem treino). Painel = os 32 bots, pelo método de
`run_educacao._painel_do_ovo`: 50 partidas por bot por semente, lados trocados na metade. ε do pet 0,05 (canônico)
e 0,15 (pet sem disciplina).

| forma | painel, 4 espécies (ε 0,05) | brasa (ε 0,05) | brasa (ε 0,15) | E1, brasa (pets reais; n) |
|---|---|---|---|---|
| furioso | 0,702 | 0,748 | 0,716 | 0,710 (17) |
| duelista | 0,532 | 0,642 | 0,591 | 0,627 (57) |
| emboscador | 0,612 | 0,553 | 0,535 | 0,567 (94) |
| sentinela | 0,615 | 0,519 | 0,511 | 0,523 (5) |
| espelho | 0,608 | 0,551 | 0,463 | 0,406 (158) |
| muralha | 0,406 | 0,457 | 0,361 | 0,279 (128) |
| vigia | 0,287 | 0,282 | 0,267 | 0,286 (6) |
| titã | 0,235 | 0,251 | 0,224 | 0,189 (16) |

- Com o bot canônico no lugar do pet, a ordem e o intervalo do E1 se repetem (brasa: 0,748 × 0,251, contra
  0,710 × 0,189 no E1).
- **O 0,71 × 0,19 do E1 é a matriz de arquétipos vista pelo painel.** Não vem dos donos nem dos pets.
- Espelho e muralha dos pets reais ficam abaixo do bot canônico. O ε do pet (0,15) explica parte disso: 0,551 → 0,463
  e 0,457 → 0,361. As formas reativas são as que mais perdem com ruído (seção 4).

## 6. Candidatos de correção (NÃO aplicados)

Mudar qualquer um deles muda o hash das regras V21C e pede uma versão nova do combate. A web teria de acompanhar
(motor TS e gabaritos de paridade), e as sementes de gambits dos pets também.

**A. O preparo sob pele dura não é visível.** `oponente_preparando` fica falso quando o preparo foi feito com a pele
ativa: a pele passa a esconder o pesado, além de protegê-lo.
- **Medido** (prévia na calibração, `candidatos.json`, subclasse de `Condicao` no script, uma rodada sem ajuste):

  | | titã | vigia | espelho | muralha | duelista | furioso |
  |---|---|---|---|---|---|---|
  | força | 0,466 (+0,293) | 0,327 (+0,079) | 0,445 (−0,195) | 0,313 (−0,087) | 0,471 | 0,718 |

  Amplitude 0,582 → 0,405; pares extremos 17 → 14; suporte 5 → 4.
- **Risco:**
  - inverte colosso × guardião: titã × espelho 0,87, titã × muralha 0,91;
  - o vigia passa a perder do titã (0,13);
  - não resolve colosso × caçador (titã 0,02 e 0,01) nem colosso × furioso (0,06 e 0,22);
  - a muralha, já fraca, cai.
- **Recalibrar:**
  - E1–E5 e G8/G9, e o E3 da pele dura (a resposta declarada "ficar longe" continua funcionando);
  - E4 do colosso;
  - S1/S2 (o colosso partido usa a lista do titã);
  - escala e campanha (validacao_escala, calibrar_escala);
  - o painel B e as runs de pesquisa que dependem dele;
  - paridade web.

**B. O contra-golpe não reflete o pesado** ("pesado quebra guarda" passa a valer também para a postura do guardião).
- **Não medido:** exigiria um gancho em `regras.resolver` (fração do reflexo por tipo de ataque).
- **Previsto pelo mecanismo:** o reflexo do pesado, por partida, é:
  - titã × espelho 61,3; titã × muralha 102,5;
  - vigia × espelho 54,9; vigia × muralha 102,7;
  - duelista × espelho 39,5; duelista × muralha 55,6;
  - furioso × espelho 15,6; furioso × muralha 25,9.

  Colosso e duelista sobem contra a guardiã; o furioso quase não muda (o reflexo dele vem do golpe rápido).
- **Risco:** a guardiã já é a única resposta ao furioso. Tirar o reflexo do pesado não toca nisso, mas derruba a
  guardiã contra o duelista (0,81 e 0,72 hoje) e contra os colossos, como em A. A e B atacam o mesmo confronto:
  escolher um.
- **Recalibrar:** E3 do contra-golpe, `fracao_contra_golpe` no E5/G8, bastião rachado (S1/S2), e o mesmo resto de A.

**C. Lista nova da muralha, a partir da do espelho** (só dados: bot e semente de gambits do pet).
- **Medido:** sozinha, +0,197 (0,400 → 0,597; `atribuicao.json`, alavanca d), mas o suporte cai para 3 e a muralha
  vira mais uma caçadora de colossos (titã × muralha 0,61 → 0,01). Junto com A (`candidatos.json`), a muralha volta
  a 0,402, o espelho vai a 0,406 e o suporte fica em 3.
- **Leitura:** C só serve de remendo do efeito colateral de A ou B. Sozinho, piora o colosso.
- **Recalibrar:** E1, E4 da guardiã, as runs de pesquisa (a muralha é a 2ª forma mais comum no E1: 128 pets), e as
  sementes de gambits dos pets na web (os pets existentes mudariam de comportamento: pede versão de pet).

**D. Furioso: mexer na base, não na forma.**
- **Evidência:** nenhuma alavanca medida da forma o leva abaixo de 0,66 (a maior é a técnica, −0,094). Com A ele
  ainda faz 0,718.
- **Proposta:** o excesso vem de 5 vitórias acima de 0,9, todas por regra da base: C3 contra os caçadores, e o golpe
  rápido que interrompe o preparo, contra os colossos e o duelista. O único freio medido é a postura (parry 15,9 por
  partida contra ele na muralha). Seria testar parry maior ou golpe rápido mais caro.
- **Não medido:** dá para montar com `dataclasses.replace` na `ConfigCombateV2C`, mas mexe na base V2C inteira e
  precisaria rodar G1–G9 de novo; fica para a calibração do redesenho.
- **Risco:** alto (todos os confrontos de corpo a corpo, a campanha inteira).

## 7. Gate proposto para o redesenho — PROPOSTO

Avaliar nas sementes de **validação** (4101…4505), com N = 100 por par por semente, depois de calibrar só na
calibração. Continuam valendo E2–E5, G6b, G8 e S1.

| gate | critério | hoje (calibração) | candidato A (prévia) |
|---|---|---|---|
| A1 força entre formas | as 8 formas em [0,40; 0,60] contra as outras 7 (ε 0,05) | 2 de 8 (duelista 0,521, muralha 0,400) | 3 de 8 |
| A2 força contra o painel B | as 8 em [0,40; 0,60] (pet canônico, 4 espécies, ε 0,05) | 2 de 8 (duelista 0,532, muralha 0,406) | não medido |
| A3 suporte | equilíbrio com suporte ≥ 6 | 5 | 4 |
| A4 decisividade | no máximo 7 dos 28 pares fora de [0,10; 0,90] com ε 0,05, e no máximo 4 com ε 0,15 | 17 e 12 | 14 com ε 0,05 |
| A5 amplitude | força máxima − mínima ≤ 0,20 com ε 0,05 e com ε 0,15 | 0,582 e 0,587 | 0,405 |
| A6 lugar no ciclo | toda forma vence (> 0,5) pelo menos 2 das outras 7 | titã vence 1 (muralha 0,613) | titã vence 4; muralha vence 2 |

## 8. O que não foi medido, e por quê

- **B** (reflexo do pesado), e qualquer ideia de "pele que impede esquiva ou postura": exigiriam gancho em
  `regras.resolver`.
- **D** (parry e custo do golpe): exigiria calibrar a base V2C de novo (G1–G9).
- **Combinações de alavancas:** medidas só uma por vez, salvo a prévia A + C.
- **Pets reais:** caráter, temperamento, treino, ε da disciplina e condição variam. O painel usa o bot canônico; só o
  ε 0,15 foi testado.
- **Espécie:** o mecanismo está agregado sobre as 4 espécies (os pontos por espécie estão em
  `mecanismo.json > pontos_por_especie`). A interação espécie × forma (E2) ficou fora.
- **Escala e campanha:** não foram medidas; os candidatos pedem recalibrar as duas.
- **Adolescentes (E4) e sombrias:** fora deste diagnóstico.
- **Incerteza:** o erro padrão entre as 5 sementes é só indicativo; não há bootstrap. Com 2.000 partidas por par e
  bots quase determinísticos, as diferenças abaixo de ~0,01 não devem ser lidas.
