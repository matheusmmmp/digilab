# Resultado — V2: a validação do mundo com o alvo aprendido

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Data: 2026-10-13. Plano: `docs/PLANO_ANALISE_V2_MUNDO_ALVO.md`, seções 8 e 9, com o desvio D1 (antes do piloto) e o adendo 1 (o K, o
poder, o G-USO do piloto e o custo, commitado antes da validação). PMA-1 a PMA-9 pela recomendação, autorizadas pelo Matheus em 2026-10-13.
Uma run, sem nada ajustado depois.

**Fonte dos números:** `artifacts_v2_mundo_alvo/validacao/`. Lá ficam `resultado.json` (os gates, o Holm, a leitura e os descritivos),
`medidas.json` (o registro compacto de cada vida), `medidas_completas.json` e `meta.json`. As vidas (`vidas/*.jsonl`) ficam fora do git e
saem de novo da config e do código. O piloto está em `artifacts_v2_mundo_alvo/piloto/`.
- **Comando:** `python experiments/run_v2_mundo_alvo.py --config experiments/configs/v2_mundo_alvo/validacao.json --processos 10`.
- **A run:** código em `7ba886a` (árvore limpa), Python 3.13.0, Windows, de 2026-10-13 15:56 a 16:22 (25 min de parede, 4,1 h de CPU,
  10 processos).
- **Os sha256** de `mundo.py`, `config.py`, `lobos.py`, `engine.py`, do plano (com o adendo 1), da config, da calibração do mundo e do
  resultado do piloto estão no `meta.json`. O motor é o da validação do J1: a ordem fixa no desempate do cheiro (PMA-8).
- **O replay:** cada vida foi gravada e rejogada a partir do texto do disco, bit a bit, e o replay da medição também foi conferido. A
  tabela do alvo no fim de cada dia sai de mais um replay, conferido contra a vida. Nenhuma divergência.

## Resumo

- **As duas premissas passam:**
  - **G-MUNDO:** P0z − P0 em `D_FE` **+0,0143 [+0,0065; +0,0216]**. Explorar ainda compensa para o instinto, então o P1 e o P1-alvo são
    lidos.
  - **G-USO:** o alvo escolhido difere do que o prior daria com o mesmo `u` em **0,0877 [0,0798; 0,0954]** das decisões com alvo dos
    últimos sete dias (limiar 0,05). O P1-alvo usou o que aprendeu.
- **G-ALVO: o alvo ATRAPALHA.** P1 − P1-alvo em `D_FE` **−0,0063 [−0,0105; −0,0022]** (t pareado −2,89, gl 19). Com o alvo aprendido, o
  déficit de fome e energia nos dias 8 a 14 fica **maior** que o do P1 com os alvos padrão do motor.
- **Com o cuidado fixo, não há diferença:** G-ALVO-AC, P1^ac − P1-alvo^ac, **−0,0003 [−0,0047; +0,0042]**. A perda aparece só em malha
  fechada, com o dono reagindo ao que o pet faz. Fica registrado ao lado, sem trocar a categoria.
- **O P1-alvo perde do instinto**, por mais que o P1 do J1: G-INSTINTO, P0 − P1-alvo, **−0,0137 [−0,0208; −0,0063]**. Na validação do
  J1, P0 − P1 deu −0,0097.
- **A leitura da seção 9:** "o alvo atrapalha: registrado. Os descritivos das classes dizem para onde o alvo levou o pet." **Resultado
  negativo, registrado.**

## 1. O que rodou

| bloco | braços | vidas por unidade |
|---|---|---|
| malha fechada | P0, P0z, P1, P1-alvo | 12 × 4 = 48 |
| acoplados ao P0z da mesma célula, filtro `nenhum` | P1^ac (`P1<P0z:nenhum`), P1-alvo^ac (`P1-alvo<P0z:nenhum`) | 12 × 2 = 24 |
| layout afastado (PMA-6) | P1 e P1-alvo em `fisico_afastado` | 12 × 2 = 24 |

**As condições:**
- **O mundo:** o da validação do J1 (`fisico`, `m` = 1, as frutas iguais, 14 dias, orçamento 224, morte desligada). O `Δ_MF` é o da A1.9
  (0,007675785900293976), reaproveitado (PMA-2).
- **As 12 células:** os 4 donos da v1, só com o cuidado (PMF-3), × 3 lugares (comedouro, perto, longe).
- **As unidades:** 20 (bases 48101…48505, K = 4 pelo adendo 1, prefixo `mundo`).
- **Total:** 1.920 vidas.
- **O cérebro:** o P1 do J1 (T3, montagem completa, canais ligados, ganho 4). O P1-alvo é esse P1 com `ConfigLobos.alvo_aprendido` e o
  `w0_alvo` padrão (S/16): 792 pesos, contra 756 do P1. Nada foi calibrado (PMA-3), e o corpo ficou desligado (PMA-4).
- **O desvio D1** (antes do piloto, decisão do Matheus): no `_creditar_canais`, o alvo aprendido conta como leitor da comida. Sem ele, o
  P1-alvo que comia comida podre falhava alto. A linha só tira a falha; nenhum crédito muda.

## 2. As premissas

| premissa | regra | resultado | passa |
|---|---|---|---|
| G-MUNDO | P0z − P0 em `D_FE`, limite inferior do IC95 > 0 | +0,0143 [+0,0065; +0,0216] | **sim** |
| G-USO | a fração do G-USO no P1-alvo, limite inferior do IC95 > 0,05 | 0,0877 [0,0798; 0,0954] | **sim** |

- **O G-USO** usa os ~94 alvos por vida dos dias 8 a 14 e nenhuma célula ficou sem decisão. Na vida toda, o alvo escolhido saiu do padrão
  do motor em 6,6% das 51.820 decisões com alvo do P1-alvo.

## 3. O primário: G-ALVO

| contraste | média | IC95 | IC90 | categoria |
|---|---|---|---|---|
| P1 − P1-alvo em `D_FE` | **−0,0063** | **[−0,0105; −0,0022]** | [−0,0099; −0,0028] | **o alvo atrapalha** |

- **A regra:** as categorias da seção 9, exclusivas e nesta ordem: o limite inferior do IC95 não passa de 0 (não ajuda), e o superior fica
  abaixo de 0. É a segunda categoria.
- **O tamanho:** a perda (0,0063) é um pouco menor que o `Δ_MF` (0,0077).

## 4. Os secundários (Holm, α = 0,05)

| gate | contraste | média | IC95 | p | p ajustado | passa |
|---|---|---|---|---|---|---|
| G-ALVO-AC | P1^ac − P1-alvo^ac em `D_FE` | −0,0003 | [−0,0047; +0,0042] | 0,567 | 1,0 | não |
| G-INSTINTO | P0 − P1-alvo em `D_FE` | −0,0137 | [−0,0208; −0,0063] | 0,9997 | 1,0 | não |
| G-PERM-A | inclinação da permanência sobre o custo de viagem, P1-alvo − P1 | +6,1 | [−6,3; +19,3] | 0,178 | 0,534 | não |
| G-DIST-A | [P1-alvo(afastado) − P1-alvo(padrão)] − [P1(afastado) − P1(padrão)], permanência média (min) | **+27,0** | **[+5,4; +49,3]** | 0,006 | 0,023 | **sim** |

- **O p** é a fração das reamostragens do bootstrap com a média ≤ 0, no sentido de cada predição.
- **Os poderes do adendo 1:** o G-ALVO-AC tinha 0,93 a 0,0125; o G-INSTINTO saiu subpotenciado (0,31 a 0,0125). Aqui a direção dele é
  oposta à predita, com o IC inteiro abaixo de 0.
- **G-PERM-A e G-DIST-A** não têm Δ nem poder (seção 7).
- **G-DIST-A:** com o layout afastado, a permanência média do P1-alvo sobe mais que a do P1. É a direção predita para quem escolhe para
  onde ir, mas, como no J1, ficar mais não paga: o `D_FE` piora.

## 5. Para onde o alvo levou o pet (descritivos, sem gate)

**As classes escolhidas** (a fração de cada classe, juntando as 240 vidas do P1-alvo em malha fechada):

| ação | dia | decisões | classes |
|---|---|---|---|
| comer | 1 | 1.955 | comida 0,70, cheiro 0,29, continuar 0,01, podre 0,001 |
| comer | 7 | 2.589 | comida 0,82, cheiro 0,17, continuar 0,003, podre 0,002 |
| comer | 14 | 2.764 | comida 0,66, cheiro 0,33, continuar 0,01, podre 0,001 |
| explorar | 1 | 2.476 | vagar 0,52, cheiro 0,28, continuar 0,14, casa 0,07 |
| explorar | 7 | 1.290 | cheiro 0,48, vagar 0,33, casa 0,12, continuar 0,07 |
| explorar | 14 | 227 | cheiro 0,60, vagar 0,24, casa 0,12, continuar 0,04 |

**Os pesos do alvo no fim do dia 14** (a média das vidas; o prior de toda classe é 64, S/16):
- **no comer:** o `cheiro` desce a −465 (fome moderada) e a −462 (fome urgente), e a `comida_podre` a −262 e −300; a `comida` sobe a ~137.
  O alvo aprendeu a evitar ir comer pelo cheiro e pela comida podre.
- **no explorar** (fruta no cenário): a `casa` sobe a 226 (no tempo livre, 128). Os outros ficam perto do prior.
- **brincar** quase não aparece (3 a 25 decisões por dia somando as vidas): o peso da bola fica no prior.

**O que os descritivos sugerem** (leitura, não teste):
- **O explorar some.** As decisões de explorar com alvo caem de 2.476 no dia 1 para 227 no dia 14. Nas que ficam, o pet vai mais ao cheiro
  e à casa e menos ao vagar.
- **No comer, a direção é a do R-1.** O alvo foge do cheiro, que é a ida longa. O crédito imediato paga o andar na decisão que anda e deixa
  o ganho com a que come (seção 11).

**O resto:**

| medida | P1 | P1-alvo |
|---|---|---|
| `D_FE` dias 8–14 | 0,388 | 0,394 |
| privação dias 8–14 | 0,156 | 0,164 |
| consumos na vida | 102,6 | 98,1 |
| visitas às manchas por vida | 18,5 | 17,4 |
| permanência média (min) | 321 | 311 |

- **G-OPORT** (só descritivo): inclinação sobre a taxa recente, P1-alvo − P1, −15,6 [−108,5; +73,6].
- **A taxa no abandono:** P1-alvo − P1 −0,011 [−0,166; +0,136].
- **P1 − P1-alvo por dono:** atencioso −0,0144 [−0,0246; −0,0047]; aleatório −0,0058 [−0,0140; +0,0019]; relapso −0,0030 [−0,0098;
  +0,0036]; incoerente −0,0021 [−0,0106; +0,0061].
- **Por lugar:** longe −0,0174 [−0,0271; −0,0084]; perto −0,0010 [−0,0063; +0,0040]; comedouro −0,0006 [−0,0107; +0,0104].
- **A perda se concentra no dono atencioso e no lugar longe** (descritivo, R-4). Com a comida longe, a ida é longa, e é aí que o alvo que
  foge do cheiro pesa.

## 6. O custo

| braço | P0 | P0z | P1 | P1-alvo | P1^ac | P1-alvo^ac | P1 afastado | P1-alvo afastado |
|---|---|---|---|---|---|---|---|---|
| s de CPU por vida | 6,75 | 3,79 | 8,45 | 8,98 | 8,42 | 8,49 | 8,45 | 8,45 |

O P1-alvo inclui as medidas do alvo (o G-USO, as classes e o replay da tabela do fim do dia).

## 7. O que este resultado não diz

- **Nada sobre o J1.** O resultado da validação do mundo físico fica como está: esta é outra run, com outras unidades.
- **Nada sobre o crédito entre decisões nem sobre o pet que planeja.** O alvo aprendeu com o sinal de sempre, a janela imediata. A seção 11
  registra as alternativas; pela tabela de leitura, elas entravam com "equivalente ou inconclusivo com o G-USO passando". Com "atrapalha",
  a decisão de abrir esse plano é do Matheus.
- **O porquê da perda só em malha fechada** (G-ALVO-AC nulo) fica sem teste. Os descritivos por dono e lugar apontam para o atencioso e o
  longe.

## 8. O que mudou no código para esta run

`experiments/bancada_v2.py` (o braço P1-alvo e as faixas 47101…/48101…), `digilab/metrics.py` (`uso_do_alvo`, `classes_por_dia`),
`experiments/run_v2_mundo_alvo.py`, as configs `experiments/configs/v2_mundo_alvo/` e o desvio D1 no `digilab/policies/lobos.py` (uma
linha). `engine.py` e `mundo.py` não mudaram. A suíte inteira passa com o D1 (2753 passed, 2 skipped).
