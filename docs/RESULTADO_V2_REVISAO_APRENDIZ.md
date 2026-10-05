# Resultado — revisão do aprendiz: teto, janela de crédito ou exposição? (2026-10-04)

Plano `docs/PLANO_ANALISE_V2_REVISAO_APRENDIZ.md` (commit `29e1233`, antes de qualquer run). Tarefa `docs/TAREFA_V2_REVISAO_APRENDIZ.md`.
**Diagnóstico, só sementes de calibração** (bases 18101…18505, K = 4: 20 unidades), sem gate e sem validação. Uma run, 1 h 50 min, 10
pontos × 120 vidas, todas rejogadas do disco bit a bit. Números de `artifacts_v2_revisao/calibracao/` (`<ponto>/resultado.json`,
`avaliacao.json`, `diagnostico.json`, `recomendacao.json`); os dois arquivos `pos_hoc_*.json` são **análises pós hoc**, fora do plano.
IC 95% por bootstrap sobre as 20 unidades; Δ = ponto − base, pareado na unidade. Dono atencioso, 14 dias, P0/P1/P3.

## 1. A base (o aprendiz de hoje no mundo das frutas)

| célula | aprendido decide (M1) | G_ap (P0 − braço, taxa da fruta ruim nos dias 8–14) | p(comer \| fruta) | consumos | acerto na tarefa | vidas no teto | razão da deriva 14/7 |
|---|---|---|---|---|---|---|---|
| descasado / P1 | 0,257 [0,249; 0,265] | **+0,109 [+0,050; +0,182]** | 0,283 | 72,5 | 0,368 | 20/20 | 2,92 |
| descasado / P3 | 0,247 [0,230; 0,264] | −0,033 [−0,136; +0,071] (18 un.) | 0,060 | 24,1 | 0,672 | 17/20 | 1,62 |
| casado / P1 | 0,254 [0,246; 0,262] | **−0,062 [−0,110; −0,018]** | 0,272 | 71,8 | 0,368 | 20/20 | 2,67 |
| casado / P3 | 0,249 [0,234; 0,265] | +0,093 [+0,018; +0,169] (19 un.) | 0,060 | 23,4 | 0,673 | 19/20 | 1,44 |
| P0 (descasado; casado) | — | 0 | 0,112; 0,115 | 41,2; 42,5 | 0,563; 0,564 | — | — |

- **O P1 come mais fruta e, no descasado, come menos a ruim que o P0** (taxa 0,323 × 0,432). No casado ele come mais a ruim que o P0
  (0,321 × 0,259): a taxa do P1 fica perto de 1/3 nos dois mundos.
- **O P3 quase não come fruta** (p 0,06) e não mexe nos pesos da fruta: o dono atencioso não julga as frutas.
- **Cuidado de si:** a fração fora de privação e a saúde não mudam em nenhum ponto (Δ = 0,000 em todos). O atencioso não deixa o pet em
  privação, então a trava "piora o cuidado de si" (seção 6 do plano) não excluiu nada e não informa nada aqui.

## 2. As alavancas (Δ pareado contra a base)

**Teto** (T1 2·S, T2 4·S, T3 16·S):
- **P1: nada muda.** Δ M1 0,000 e Δ G_ap +0,000 nos três, embora as vidas com peso no teto caiam de 20 para 16, 8 e 0. Os pesos do P1
  que batem no teto já estão onde o comportamento não muda mais: na sub-decisão da fruta, o peso da fruta ruim chega a 0 (w0 − teto)
  em 17 de 20 vidas no descasado, e o coeficiente tem o piso de 1/16 (pós hoc, `pos_hoc_pesos_fruta.json`).
- **P3: o aprendido decide mais e acerta menos a tarefa do dono.** Δ M1 no descasado +0,014 [−0,001; +0,030], +0,033 [+0,006; +0,066],
  +0,039 [+0,008; +0,079]; Δ acerto −0,022 [−0,038; −0,009], −0,028 [−0,053; −0,007], −0,026 [−0,055; −0,001].
- M1 do descasado (média P1 e P3): T1 +0,007 [−0,000; +0,015], T2 +0,017 [+0,003; +0,033], **T3 +0,020 [+0,004; +0,039]**.

**Janela de crédito** (traço J1 2 decisões λ = S/2, J2 4 decisões 3S/4, J3 8 decisões 7S/8):
- **Piora o que se quer medir.** Δ G_ap (P1, descasado) −0,006 [−0,019; +0,006], −0,017 [−0,034; +0,000], −0,027 [−0,041; −0,014];
  Δ M1 (descasado, P1 e P3) −0,019, −0,020, −0,018, todos com IC abaixo de 0.
- No P3 o traço derruba o acerto na tarefa do dono: −0,046, −0,091, −0,124 (ICs abaixo de 0). No P1 o acerto sobe um pouco (+0,006 a
  +0,028) e os consumos caem (J3 −7,9 [−12,2; −4,7]).

**Exposição** (X1 `w_fruta` 12, X2 `w_fruta` 24, X3 8 ofertas por dia):
- p(comer | fruta) do P1 na base é 0,283, abaixo de 0,30: a condição da leitura vale.
- Os consumos sobem (P1 no descasado: +5,1 [+3,0; +7,2], +6,3 [+3,7; +8,7], **+63,5 [+60,8; +66,7]**), mas o **G_ap não sobe**:
  −0,030 [−0,067; +0,009], **−0,064 [−0,106; −0,024]**, +0,003 [−0,046; +0,062]. O `w_fruta` maior também faz o P0 comer mais (p 0,112 → 0,255
  no X2), e a diferença entre os dois diminui.

## 3. Diagnóstico e ponto recomendado (pelas regras registradas)

- **Diagnóstico (seção 6):** o teto **segura** (metade ou mais das vidas no teto na base, e os pontos T aumentam M1 com IC inferior > 0,
  pelo P3); a janela **não segura**; a exposição **não segura** (sobem os consumos, não o G_ap). Nenhum ponto piora o cuidado de si.
- **Recomendação (seção 7):** nenhum ponto ajuda pelo G_ap. Pelo M1, o teto vai para **T3 (teto 16·S = 16384)**; janela e exposição
  ficam na base. Uma alavanca só saiu da base, então não houve conferência da combinação.
- **T3 contra T2** (risco 2 do plano): o P1 é idêntico nos dois; no P3, M1 +0,020 × +0,017 e vidas no teto (descasado) 2/20 × 13/20,
  com o mesmo acerto. O T2 dá quase o mesmo com teto finito.
- **Ponto recomendado para a calibração do N5 e do experimento maior:** `passo` 512, **`teto` 16384**, sem traço, ganho 4, E2,
  `w_fruta` 6, 4 ofertas por dia. A grade do `w0_info` do N5 ({S/4, S/2, 3S/4}) fica bem abaixo do teto, e o "limitado pelo teto" do N5
  (risco 2 daquele plano) perde a razão de existir.

## 4. O que segura de fato (pós hoc, fora do plano)

A regra escolhe o teto por causa do P3, mas **nenhuma das três alavancas mexe no que o P1 aprende sobre as frutas**. Duas leituras pós
hoc da base mostram por quê (`pos_hoc_pesos_fruta.json`, `pos_hoc_oferta_unica.json`; a vida inteira, não só os dias 8–14):

- **O P1 aprende qual fruta evitar.** Peso médio no fim da vida (prior 1024): fruta boa ~1700, neutra ~990, ruim ~90 no descasado, com 17
  de 20 vidas no zero; no casado, 1603, 952, 67.
- **Mas a escolha só age quando há duas frutas ou mais.** Fruta ruim entre os consumos:

| | P0, duas ou mais | P1, duas ou mais | P0, uma só | P1, uma só |
|---|---|---|---|---|
| casado | 0,222 | **0,146** | 0,319 | **0,447** |
| descasado | 0,436 | **0,293** | 0,400 | **0,372** |

  Com uma fruta só no cenário, 55% dos consumos do P1, ele come o que houver. A decisão de comer ou não vê só `fruta` (o maior incentivo
  no cenário), não **qual** fruta está lá. E o P1 come muito mais fruta que o P0, porque a nutrição dá sinal positivo.
- **Leitura:** o gargalo para o N5 e para a predição do descasado é **a decisão de comer não saber qual fruta está no cenário**. Não é o
  teto, nem a janela, nem a exposição. É desenho, não calibração: mudar a entrada `fruta` dos lobos (por exemplo, o valor aprendido da
  melhor fruta presente) muda o prior do instinto e o N5-2. Fica para o Matheus decidir (seção 5).

## 5. Decisões para o Matheus

**Decididas pelo Matheus em 2026-10-05: todas como recomendadas (R1–R4).** R1 = T3 (teto 16·S) como ponto de partida das
calibrações; R2 vira tarefa da rodada 7, dividida entre o chat A (o mundo diz qual fruta está no cenário) e o chat B (a decisão de comer
lê isso). A N5-2 continua valendo: a informação do dono só entra na escolha de qual fruta.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| R1 | Ponto da calibração do N5 e do experimento maior | **T3 (teto 16·S), pela regra registrada**; o T2 (4·S) é a alternativa de teto finito, com quase o mesmo efeito | Com o teto de hoje, metade ou mais das vidas fica no teto e o "limitado pelo teto" do N5 continua; o teto não muda o P1 nas frutas |
| R2 | A decisão de comer ou não passar a saber qual fruta está no cenário (tarefa nova, com o chat A) | **Sim, antes da calibração do N5** | Sem isso, o P1 e o P2 aprendem a escolher entre frutas, mas comem a ruim quando ela está sozinha: a taxa de fruta ruim mede pouco do que aprendem, e G-EF, G-PIORA e G-REC ficam fracos por construção |
| R3 | O traço de elegibilidade | Fica no código, desligado (0) | Ligado, piora o G_ap e o acerto do P3 |
| R4 | A exposição | `w_fruta` 6 e 4 ofertas como estão; o X3 (8 ofertas) só se o N5 sair inconclusivo por exposição | O `w_fruta` maior faz o P0 comer mais a ruim e encolhe a diferença |

## 6. Limites

- 20 unidades, 14 dias, um dono; contrastes sem correção de multiplicidade (diagnóstico).
- A trava de cuidado de si não informa com o atencioso (privação 0 em todas as vidas).
- As seções 4 e 5 (R2) vêm de análise pós hoc; o plano registrado não as previa.
