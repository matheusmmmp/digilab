# Resultado da investigação do núcleo da luta (LUTA_POC, N1 a N5)

Worker: Claude Code, Opus 5.5, worktrees `D:\Trab\digilab\v3-luta-nucleo-n1`, `-n3` e `-n4`, 2026-11-12, a pedido do Gerente de sprites e
luta. O plano é o `docs/PLANO_LUTA_NUCLEO.md` (APROVADO; as D-N-1 a D-N-7 e a D-N-5 decididas pelo Matheus). Este documento é a N5, o
relatório.

**Status:** a investigação acha as causas. **Nenhum número do jogo mudou, e nenhuma chave liga numa versão de pet (D-N-7).** O que vem
daqui são propostas para a calibração geral ("equilíbrio só no fim"). Os números novos são PROPOSTOS, SEM FONTE.

## 1. O que rodou

| etapa | o quê | os artefatos |
|---|---|---|
| **N1** | as releituras dos JSON das medidas da LP5 e da LP6, sem luta nova | `web/app/scripts/medicoes/luta_nucleo/n1/` |
| **N2** | as lutas fixas com os eventos, com o motor de hoje, nas lutas da v21, da v23 e da v29 (95 280 lutas cada) | `web/app/scripts/medicoes/luta_nucleo/n2/` |
| **N3** | as 4 chaves no núcleo, desligadas, com o gabarito das versões vivas antes (PR #893, na `main`) | `web/app/test/gabaritos/luta_nucleo_n3.json` |
| **N4** | 10 medidas inteiras da bancada (as 21 metas) na faixa `investigacao` (92101 a 92505): a base da v23, cada chave sozinha, as 4 juntas, e a base e as juntas da v29 | `web/app/scripts/medicoes/equilibrio_poc/n4_*/investigacao/` e a comparação em `web/app/scripts/medicoes/luta_nucleo/n4/` |

Os contrafactuais e os critérios de leitura foram registrados antes da primeira medida, na seção 8 do plano (commit `c16705f6` no branch `v3-luta-nucleo-n4`, `7a7dc06d` neste; D-N4-6). Cada medida
levou de 4 a 7 min, em 4 processos e uma por vez, cada uma liberada pelo `pre_run`. As 10 juntas levaram uns 50 min.

## 2. A resposta: a causa de cada meta

| meta | a causa | o que a N4 mostrou | de quem é |
|---|---|---|---|
| **V1** (a variedade) | o atributo. Ele explica de 0,83 a 0,97 da variância do V1 na v23 (N1) | com o `forcaAtr` 1,0, a amplitude cai de 0,31–0,44 para 0,12–0,21. A meta só falha porque alguma forma vence menos de 2 das outras | o núcleo (o `forca`) e a tabela das formas |
| **V2** (a espécie) | o atributo | com o 1,0, a amplitude fica em 0,007 a 0,16 (na base, de 0,03 a 0,26) | idem |
| **os 7 NPCs** (P2, P3) | o atributo, com a régua: o "sem treino" tem o piso da fração de pets com vantagem | com o 1,0, **os 9 outros NPCs passam**: o P3 inteiro e o P2 menos o Myotismon. O Guardromon e o Piedmon caem para 0,34 e 0,22 no sem treino | o núcleo e a régua |
| **o Myotismon** | a série de 3 sem cura no Castelo | nenhuma chave o salva; com o atributo menor, ele piora (0,25 → 0,002) | a série (o mapeamento) |
| **P5** (a vida até o Mega) | o atributo do colosso (o Growlmon, Virus, contra 8 Vaccine) | com o 1,0, o P5 vai de 0,24 para **0,85** e passa. Com 1,15, vai a 0,56; com 1,25, a 0,42 | o núcleo e a tabela das formas |
| **G1, G3** (a Liga, a Fábrica) | a série sem cura. Na v23, o pet típico é uns 5 % mais forte que o rival, e cada vitória custa metade da vida (N2: a soma das perdas na Liga é 3,30) | **nenhuma chave age** | o mapeamento (o `gama`, o `multVida`), da calibração geral |
| **G2** (a Torre) | a série sem cura, e o pet treinado que cai do Ringue pelo pulo | o `puloMax` e a `bordaRingue` levam o recorde de 1 a 2, longe dos 3 | a série, e um pouco a borda |
| **A1 no Ringue** | o recuo na preparação do tiro e a habilidade, que jogam quem atira para fora (N2) | a `bordaRingue` 0,9 o leva de 0,09–0,14 para 0,14–0,22 no Rookie, no Champion e no Ultimate. Nas juntas da v29, o Ultimate e o Mega chegam a 0,35 e 0,41 | o núcleo (a borda) e o mapa (o empurrão 7) |
| **A1 no Castelo** | não achada (N2) | nenhuma chave move | aberta |
| **T2** (o fôlego) | **não é o pulo.** O `puloMax` não move o fôlego (0,47 → 0,47). O `tiroDoMorto` o sobe um pouco (0,46–0,47 → 0,52–0,53) | a H-PULO cai para o T2 | aberta |
| **D2** (os empates) | o tiro de quem já caiu | com o `tiroDoMorto`, os empates vão de 4 % a **0**, e nenhuma meta quebra | o núcleo |
| **S1** (o espelho) | na beira da faixa, nos dois lados | com o `tiroDoMorto` e com as juntas, ele passa | o núcleo (os empates) |

## 3. O que cada chave move e quebra (a N4)

A tabela completa está em `web/app/scripts/medicoes/luta_nucleo/n4/comparacao.md`.

| a medida | passam (a base: 9) | o que passa a passar | o que quebra |
|---|---|---|---|
| `forcaAtr` 1,0 | 8 | P3, P5 | T3, E1, G4 |
| `forcaAtr` 1,15 | 6 | — | T3, E1, G4 |
| `forcaAtr` 1,25 | 7 | — | E1, G4 |
| `tiroDoMorto` | **10** | D2 | **nenhuma** |
| `puloMax` 75 | 7 | — | P4, T1 |
| `bordaRingue` 0,9 | 8 | — | T1 |
| as 4 juntas, na v23 | 7 | D2, S1 | T1, T3, E1, G4 |
| as 4 juntas, na v29 (a base da v29: 9) | 7 | D2, S1 | T1, T3, E1, G4 |

**O achado da N4: o atributo é o que dá incerteza à luta.** Sem ele (o `forcaAtr` 1,0), quem é um pouco mais forte vence quase sempre:
- o pet no teto vence de 0,89 a 0,99 (o T3 pede até 0,95);
- o pet de um estágio contra o de cima cai de 0,19 para 0,02 (o E1 pede de 0,10 a 0,35);
- o Salão vai a 0,87–0,996 (o G4 pede até 0,95).

Ou seja, a faixa do E1 e o teto do T3 só passavam na v23 porque o atributo sorteava o vencedor. O `gama` da v23 achatou os stats, e o
atributo e a variação de ±10 % no dano ficaram como a única fonte de surpresa.

**O `puloMax` e a `bordaRingue` tiram uma desvantagem do pet treinado.** O pet treinado deixa de pular para fora, e o T1 passa de 0,97.
As duas corrigem uma regra que pune o treino, mas sozinhas deixam o treino pesar demais.

## 4. O que vai para onde

**Para a calibração geral** (a rodada única, "equilíbrio só no fim"; PROPOSTO):
- **o `tiroDoMorto` ligado** na versão nova. Ele fecha o D2, ajuda o S1 e não quebra nada;
- **o `forcaAtr` como alavanca, junto com o mapeamento.** Sozinho, baixar o atributo fecha o V1 (quase), o V2, o P5 e 6 dos 7 NPCs, mas tira a
  incerteza da luta. A alavanca da incerteza é do mapeamento: o `gama`, o `multVida` e o `multAtk`, que decidem quanto um ponto e um
  estágio valem. A calibração precisa mexer nos dois juntos, na mesma grade;
- **o `puloMax` e a `bordaRingue` como alavancas**, com o T1 vigiado;
- **as séries sem cura (G1, G3, o Myotismon):** nenhuma chave do núcleo as move. Elas dependem de quanto o pet típico é mais forte que o
  rival (o mapeamento), ou de uma regra de série, que é decisão do Matheus (a decisão 5 da LP2).

**Para a tarefa da tabela das formas** (ainda sem tarefa):
- a distribuição dos atributos: 7 dos 10 NPCs são Virus, e no Champion 8 das 16 formas são Vaccine;
- o colosso de perto (o Gatomon);
- o V1 que sobra com o atributo menor (as formas que vencem menos de 2 das outras).

A recomendação é abrir essa tarefa depois que a calibração geral escolher o `forcaAtr`: quanto menor ele for, menos a distribuição dos
atributos pesa.

**Abertos:**
- **o Castelo:** nenhuma regra explica o A1 dele;
- **o T2:** o fôlego não pesa, e não é pelo pulo.

## 5. As decisões que sobram para o Matheus

| # | a pergunta | a recomendação | o custo de errar |
|---|---|---|---|
| **D-N-8** (fechar) | a investigação fecha aqui, com as causas da seção 2, e o próximo passo é o plano da calibração geral? | **sim.** As causas que o núcleo tem estão separadas, e o que sobra (o Castelo, o T2) não pede mais chave antes da calibração | seguir investigando gasta máquina em duas metas que a calibração pode aceitar; fechar sem o Castelo deixa o A1 dele fora da faixa |
| **D-N-9** (o `tiroDoMorto`) | o `tiroDoMorto` entra ligado na versão nova da luta, junto com a calibração geral? | **sim.** Fecha o D2 sem quebrar nenhuma meta | sem ele, os empates (4 %) seguem; ligar sozinho, antes da calibração, criaria uma versão de pet só para ele (a D-N-7 pede que não) |
| **D-N-10** (as alavancas) | a calibração geral tem como alavancas, numa grade conjunta, o `forcaAtr` (de 1,0 a 1,5) e o mapeamento (o `gama`, o `multVida` e o `multAtk`), com o `puloMax` e a `bordaRingue` ao lado? | **sim.** O `forcaAtr` sozinho fecha o V1, o V2 e o P5 mas quebra o E1, o T3 e o G4; o mapeamento devolve a incerteza | calibrar só o atributo troca 3 metas por outras 3; calibrar só o mapeamento (a LP5) não move o V1, o V2 nem os NPCs |
| **D-N-11** (a régua das séries) | o G1, o G3 e o critério do P2 e do P3 ficam como estão na calibração geral, ou são revistos antes dela? | **revistos no plano da calibração geral, antes de rodar.** O G3 (Mega canônico contra Mega canônico, sem cura) não chega a 0,25 nem com a cura. Pela conta, com 0,5 por luta, a série de 3 sai em 0,125 | manter a régua deixa 3 metas que nenhuma luta cumpre; trocá-la depois de ver a calibração é o erro que a conferência única evita |
| **D-N-12** (a tabela das formas) | a tarefa da tabela das formas abre depois da calibração geral escolher o `forcaAtr`? | **sim, depois.** Com o atributo menor, a distribuição pesa menos, e a tarefa fica menor | abrir antes pode mudar atributos que o `forcaAtr` já resolveria; nunca abrir deixa o Gatomon e o V1 que sobra |

## 6. Os desvios

`docs/registro/2026-11.md`, as seções da N0, da N1 e N2, da N3 e da N4 e N5.
