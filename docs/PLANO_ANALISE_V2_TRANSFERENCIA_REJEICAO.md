# Plano de análise — V2: a transferência da rejeição da escolha para o item único (DS-3)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Status (2026-10-07): **PROPOSTO**, registrado **antes de qualquer run**. **TR-1 a TR-4 DECIDIDAS pelo Matheus em 2026-10-07, todas pela
recomendação** (seção 9). Decisão DS-3 do Matheus (2026-10-07,
`docs/DEFINICOES_V2_SEIS_PERGUNTAS.md`, seção 3): rodar o teste de transferência **antes** de qualquer mudança no aprendiz para o
achado 1.

**Regras deste plano:**
- Plano curto, uma validação só.
- O que não está aqui é descritivo pós hoc.
- Nada se ajusta olhando a validação.
- Os números de antes citam o artefato; os novos estão marcados PROPOSTO ou SEM FONTE.

## 1. A pergunta

**O achado 1** (`docs/DESCRITIVO_V2_PLATO.md`, `artifacts_v2_descritivo_plato/`): o cérebro A aprende a evitar a fruta ruim na escolha
entre frutas. Ele a escolhe em 2% a 11% das vezes, contra 29% a 65% do herdado. **Com uma fruta só, ele come o que houver.**

**Os três mecanismos candidatos** (definições, seção 3):
1. **aversão ao item:** a rejeição muda o valor da fruta e vale também sozinha. Garcia e Koelling 1966, `10.3758/BF03342209`, sustentam
   que esse mecanismo existe em animais;
2. **aprendiz de escolha relativa:** só o contraste entre opções presentes ensina, e uma opção sozinha não gera gradiente. Leitura nossa,
   SEM FONTE;
3. **valor do item separado do ato de comer:** o pet aprende sobre a fruta, mas a decisão de comer é dominada pela fome. Leitura nossa,
   SEM FONTE.

**A pergunta:** depois de um treino **só com escolha** (duas frutas ou mais), a rejeição da ruim **transfere** para a ruim oferecida
sozinha? E, se não transfere, a **fome baixa** a faz aparecer?

**Rótulo:** SEM APOIO DIRETO. A revisão não localizou trabalho que compare rejeição absoluta e escolha relativa. Nenhuma alegação de
novidade.

## 2. As vidas que já existem não respondem (por isso, run nova)

**O motivo** são as vidas da validação única e da comparação dos cérebros, regeneráveis por replay, como fez o descritivo do platô:
- **o calendário mistura as duas situações desde o dia 1.** A rotação tem 7 conjuntos, e 3 deles têm uma fruta só (`_rotacao_ofertas` em
  `digilab/config.py`): `a`, `c` e `b`;
- **o pet come a ruim sozinha** e recebe a consequência disso enquanto aprende a escolha. A transferência fica misturada com a
  reexperiência, que é justamente o que o teste tem de evitar (como o teste 1 das definições, seção 1);
- **a fome na hora da oferta não é controlada.** A oferta sai em horário fixo, com o pet em qualquer estado.

**Uma parte 0, descritiva, sem run nova** (fora da regra de decisão): nas mesmas vidas regeneradas, p(comer | só a ruim) e p(comer | só a
neutra) por faixa de fome (fome ≥ 0,70 e fome < 0,45), no P0 e no P1 do A, no descasado.
- É pós hoc e confundida pela reexperiência; serve só para dar a ordem de grandeza ao lado.
- Ela usa o `experiments/descritivo_plato.py` como está, mais o corte por fome, que a etapa 4 escreve.

**Sobre a fome:** no motor, `fome` é a saciedade (1 é cheio). "Fome baixa" é `fome` ≥ 0,70, e "fome alta" é `fome` < 0,45, o limiar da
regra `fome_moderada` do instinto. O 0,70 é PROPOSTO, SEM FONTE.

## 3. O desenho da run nova

| item | valor | fonte |
|---|---|---|
| cérebro | o A da montagem completa, no ponto da K2 (`g` S/2, `w0_info` S/4, ganho 4, canais ligados, T3) | `experiments/configs/v2_experimento_maior/validacao.json` |
| braços | **P0** (o instinto que vê as frutas) e **P1** (a consequência com a E2) | a bancada |
| mundo | **`descasado`**, a condição do achado 1. Lá a ruim é a preferida de nascença | `docs/DESCRITIVO_V2_PLATO.md` |
| dono | o atencioso, sem informação, sem pedido, sem K4 | o experimento maior |
| duração | 14 dias: **treino nos dias 1 a 10, sondas nos dias 11 a 14** | PROPOSTO |
| morte | desligada | — |

**O treino (dias 1 a 10): só escolha.** É o `CalendarioFrutas` com a rotação restrita aos 4 conjuntos de duas frutas ou mais: `bc`, `abc`,
`ab` e `ac`. Mesmos horários, mesma regra (a semente, não o estado), fora do orçamento.
- É uma variante do calendário. Dona: o D, na bancada.
- Nenhuma fruta é oferecida sozinha no treino.

**As sondas (dias 11 a 14): uma fruta só, com a fome controlada.** O calendário para. Em cada dia saem 4 sondas, numa ordem sorteada por
dia (rng `transferencia-sondas`, da semente):
- **a ruim com fome baixa:** no primeiro passo do dono com `fome` ≥ 0,70 desde a sonda anterior;
- **a neutra com fome baixa:** idem;
- **a ruim com fome alta:** no primeiro passo do dono com `fome` < 0,45 desde a sonda anterior;
- **a neutra com fome alta:** idem.

Regras das sondas:
- a fruta da sonda fica no cenário pela duração de sempre (120 min) e sai do mundo pela mesma regra das ofertas (fora do orçamento);
- a sonda que não acha o estado até o fim do dia é perdida, contada e relatada;
- a neutra é o controle de preferência e de fome: ela não pune;
- a boa não entra nas sondas;
- é uma regra do mundo que olha o estado. A diferença do calendário é declarada: a sonda depende da fome de propósito.

**Por que o P0 entra.** No descasado a ruim é a preferida de nascença, e o P0 já come mais a ruim sozinha (+0,08, descritivo do platô). A
transferência se lê na diferença P0 − P1, com a neutra como controle (seção 4).

## 4. As medidas

Por unidade, só nas sondas:
- **`R1(f, z)`:** se o pet comeu a fruta f na **primeira** sonda de f na faixa de fome z (0 ou 1). É a medida limpa: antes dela, o pet
  nunca comeu f sozinha;
- **`Rt(f, z)`:** a fração das 4 sondas de f na faixa z em que ele comeu. É descritiva, com reexperiência a partir da segunda.

**O índice de transferência** na faixa z:

`T(z) = [R1_P0(ruim, z) − R1_P1(ruim, z)] − [R1_P0(neutra, z) − R1_P1(neutra, z)]`

- T > 0: o P1 rejeita a ruim sozinha mais do que rejeita a neutra, além do que o P0 faz.
- O termo da neutra tira o que o aprendizado mudou no comer em geral, com qualquer fruta.

**A margem `Δ_T`, na escala de probabilidade:** metade da aversão aprendida na escolha, medida no treino da mesma run:
- `Δ_T = ½ × [p_P0(ruim | escolha) − p_P1(ruim | escolha)]`;
- p(ruim | escolha) é a fração de escolhas da ruim nas decisões de comer com ela e outra fruta presentes, nos dias 6 a 10;
- a média é das unidades.

**A ideia:** transferir pelo menos metade da aversão que a escolha aprendeu. A convenção de "metade" é a da regra 6.3 do experimento
maior.

**Descritivos:** o `Rt`, a latência até comer na sonda, as sondas perdidas por faixa, o peso da escolha e o termo de presença das três
frutas no fim do dia 10 (o que o descritivo do platô já lia).

## 5. A regra de decisão

Bootstrap sobre as unidades (10.000 reamostragens, semente 4242). Lida nesta ordem; vale a primeira que se aplica:

| leitura | condição | mecanismo apontado |
|---|---|---|
| **transfere** | `T(alta)`: limite inferior do IC95 > 0 | **1** (aversão ao item), mesmo com fome |
| **não transfere com fome; aparece sem fome** | `T(alta)` com o IC90 dentro de ±`Δ_T`, **e** `T(baixa)`: limite inferior do IC95 > 0 | **3** (o comer dominado pela fome) |
| **não transfere em nenhuma** | `T(alta)` e `T(baixa)` com o IC90 dentro de ±`Δ_T` | **2** (escolha relativa) |
| **inconclusivo** | o resto | nenhum |

- **A ordem resolve a sobreposição** entre "confirma" e "equivale" que a leitura da validação única apontou (PR #196).
- **Não há Holm:** as leituras são uma árvore de decisão, e não testes paralelos. Cada nó usa um IC.
- **O que a leitura autoriza:** só o próximo passo do aprendiz (DS-3: não "consertar" antes). Um "mecanismo 2" pede mudar a regra de
  aprendizado da escolha; um "3", a decisão de comer; um "1" diz que o achado 1 era do treino misturado, não do aprendiz. A mudança em si é
  tarefa própria.

## 6. Piloto e validação (sementes)

**Não há calibração:** o ponto do A é o da K2 e nada se escolhe. As sementes de calibração servem de **piloto**, só para três coisas:
- o N;
- as sondas perdidas: se mais de 20% das sondas de uma faixa se perdem no piloto, o adendo pode trocar o limiar daquela faixa, antes da
  validação e sem olhar o `T`;
- o custo.

| uso | faixa | bases |
|---|---|---|
| piloto | **35101…35505** | 35101, 35202, 35303, 35404, 35505 (K = 4, N = 20) |
| validação | **36101…36505** | 36101, 36202, 36303, 36404, 36505 (K do adendo) |

**O N:** o menor K, de 4 a 20 por base (N de 20 a 100), com poder simulado ≥ 0,8 para detectar `T(alta)` = `Δ_T`. É um bootstrap das
diferenças do piloto, deslocadas, com 2.000 réplicas por K.
- Cada unidade custa só 2 vidas (P0 e P1), então o teto é largo.
- Se nem K = 20 chega, a validação roda com K = 20 e o poder sai declarado.

**O adendo:** o N, o `Δ_T` do piloto (só como referência: o da validação é medido nela mesma, seção 4), as sondas perdidas e o custo
entram no adendo 1 deste arquivo, num commit antes da validação.

**Conferências das sementes, em 2026-10-07, no `origin/main` (`ceea204`) e em todos os branches remotos:**
- as duas faixas estão fora de `FAIXAS_RESERVADAS` e da `FAIXAS_QUEIMADAS` (`experiments/bancada_v2.py`);
- elas também ficam fora da 23101…27505, da 31101…32505 (mundo físico) e da 33101…34505 (corpo);
- `git grep` das dez bases em `docs/`, `experiments/`, `tests/` (fora os gabaritos), `digilab/`, `web/app/` e `CLAUDE.md` não acha uso.

O D registra as duas faixas, com a fonte deste plano, e o prefixo de unidades `"transferencia"`.

## 7. O que precisa existir antes (donos de arquivo)

| peça | dono | o quê |
|---|---|---|
| calendário só de escolha | **D** (bancada) | a variante do `CalendarioFrutas` com a rotação restrita, nos dias de treino |
| sondas por estado | **D** (bancada), pela regra do mundo | as 4 sondas por dia da seção 3, com a rng `transferencia-sondas` |
| medidas | **D** (`digilab/metrics.py`) | `R1`, `Rt`, `T(z)`, `Δ_T`, as sondas perdidas |
| gates de mecanismo | **D** | G1 (replay bit a bit); a run de hoje sem a variante, byte a byte; nenhuma fruta sozinha nos dias 1 a 10; cada sonda no estado certo |
| parte 0 | **C** ou **D** | o corte por fome no `experiments/descritivo_plato.py`, só leitura |

**Nenhuma mudança no cérebro A** (DS-3), em `frutas.py` nem no `engine.py`.

## 8. Riscos

| # | risco | o que o plano faz |
|---|---|---|
| R-1 | **A primeira sonda é uma só por faixa e fruta.** O `R1` é binário e ruidoso por unidade | o N vem do poder simulado, e cada unidade custa 2 vidas. O `Rt` sai ao lado |
| R-2 | **A fome alta põe a regra `fome_moderada` em jogo** (comer ou chamar, 50/50), e o aprendiz mexe nela | a neutra é o controle na mesma faixa, e o `T` é uma diferença de diferenças |
| R-3 | **As sondas por estado dependem do pet.** P0 e P1 recebem as sondas em ticks diferentes | é declarado: o que se fixa é o estado de fome, e não o tick. A ordem das sondas sai da semente |
| R-4 | **O treino só de escolha muda a nutrição.** O pet come mais fruta no treino que no calendário de sempre | é o mesmo para P0 e P1; a fome é controlada nas sondas |
| R-5 | **A ruim é a preferida de nascença no descasado** | o P0 e a neutra entram como controles. O casado fica fora (lá a ruim é a menos preferida, e o piso de p(comer) apagaria o efeito) |
| R-6 | **O limiar 0,70 é PROPOSTO** | as sondas perdidas são vistas no piloto. Uma troca do limiar só pode acontecer no adendo, sem olhar o `T` |
| R-7 | **Generalizar para outros cérebros** | o plano é só do A. O C e o B entram por adendo |

## 9. Decisões do Matheus

**DECIDIDAS em 2026-10-07: TR-1 a TR-4, todas como recomendado.**

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| TR-1 | Run nova, e não só o descritivo nas vidas de hoje | **sim**: nas vidas de hoje a ruim sozinha aparece desde o dia 1, com reexperiência e sem a fome controlada. A parte 0 sai ao lado, só como ordem de grandeza | só o descritivo: o teste confunde a transferência com a reexperiência, e o mecanismo fica sem resposta |
| TR-2 | O desenho: treino só de escolha nos dias 1 a 10, sondas por estado de fome nos dias 11 a 14, P0 e P1 no descasado, a neutra como controle | **sim** | sem a neutra ou sem o P0: a preferência de nascença entra no índice |
| TR-3 | A regra de decisão em árvore (seção 5), com a `Δ_T` medida na própria run | **sim** | uma `Δ_T` fixa sem dado pode ser larga demais ou estreita demais |
| TR-4 | As faixas de sementes | **35101…35505** (piloto) e **36101…36505** (validação) | uma colisão tira o "novo" das unidades |
