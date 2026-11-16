# Plano de análise V3: o modular contra uma baseline trivial (EVIDENCIA A1)

**Status: APROVADO pelo Matheus em 2026-11-16,** com as BT-1 a BT-9 DECIDIDAS pela recomendação: "Aprovo, pode rodar", nesta sessão. Escrito em 2026-11-16 (Claude Code, Opus 5.5, branch `v3-evidencia-a1`), na fase A1 do pedido de
2026-11-16 (`docs/TAREFA_V3_EVIDENCIA.md`), depois do ok do Matheus à auditoria A0 e às 12 células da C4 ("Aprovo, siga a A1").

## 0. A trava e o que já foi visto

**Nenhuma vida da calibração nem da validação roda antes de três coisas:**
1. este plano commitado, com "APROVADO pelo Matheus" no cabeçalho (o `run_v3_baseline_trivial.py` confere e recusa sem);
2. as decisões BT-1 a BT-9 (seção 9) DECIDIDAS;
3. as duas faixas da seção 2.3 em `FAIXAS_RESERVADAS` (o orquestrador confere).

O código (a baseline, o orquestrador, as configs e os testes) entra **no mesmo commit que este plano**, antes de qualquer vida. Ele fica
no branch e não na `main`, porque o merge é do Matheus (BT-9).

**O que já foi visto antes deste plano** (para que nada daqui pareça escrito sem saber):
- **O nível do REL na C4,** no git (`artifacts_v2_digibrain_prototipo/memoria_autobio/run/resultado.json`): 0,583 no `longe_fixo`, 0,876
  no comedouro e 0,437 no longe, com dp por unidade de 0,117 no `longe_fixo`.
- **Duas vidas de fumaça de 14 dias,** semente 101 (uma semente dos testes, fora das duas faixas), dono relapso, `longe_fixo`:
  - um protótipo da baseline com X = 0,5, Y = 0,3 e Z ≈ 0,68 fechou 0,78 dos episódios de fome;
  - o REL da C4 fechou 0,38.

  Uma vida não mede nada. Elas só mostraram que a baseline roda nas fábricas da C4 e passa no T-CENARIO-1. Nenhum número deste plano
  (a grade, a margem, o K, a regra de leitura) foi ajustado por elas. A previsão da seção 1 é a do pedido, não a dessa vida.

**O que este plano não afirma:**
- que o modular é bom ou ruim fora do que a seção 1 mede;
- que a baseline é a melhor política trivial possível;
- que algum cérebro está pronto.

Nenhuma alegação de novidade.

## 1. A pergunta, a hipótese e a previsão, escritas antes

**A pergunta:** o DigiBrain modular vence uma política trivial de quatro regras nas mesmas células em que a C4 o mediu?

**A hipótese (H):** o modular fecha uma fração maior dos episódios de fome no `longe_fixo` do que a baseline trivial. A medida é a taxa de
fechamento por episódio de fome (`episodios_fome.taxa`, a mesma do primário da C1 e da C4).

**O contraste primário:** REL − TRIV na taxa por episódio, nas 4 células do `longe_fixo`. A unidade é (base, semente), com a média das 4
células do dono da unidade, como na C4 (A9.4). A previsão é **> 0** (a do pedido; o tamanho é SEM FONTE).

**A previsão não se afrouxa até passar.** Se o primário sair "≈ 0" ou "< 0", isso é registrado como está (seção 5.3).

## 2. O cenário e o desenho

### 2.1 O que não muda

- **O motor, o corpo, o mundo, o `engine.py`, o A e o modular.** Nenhum mecanismo novo.
- **O cenário da C4,** como está:
  - o `CONFIG_MUNDO_MVP` e o corpo do v11;
  - o pet sozinho e os quatro donos sem ensino;
  - 14 dias, orçamento de 16 por dia, morte desligada;
  - o motor que grava o corpo (`run_v2_longe_regular.MotorGravaCorpo`).
- **A vida do REL** é a de `run_v2_memoria_autobio._vida`, sem mudança: as mesmas fábricas, o replay do disco, as conferências da C4
  (mecanismo, memória, fins) e as medidas.

### 2.2 As células (BT-2, aprovada)

As 12 da C4: os 4 donos (atencioso, relapso, aleatório, incoerente) × os 3 lugares (`longe_fixo`, o primário; o comedouro e o longe
sorteado, secundários). O pedido falava em "3 lugares × 2 doadores". O meta da C4 tem 4 donos, e o Matheus aprovou as 12 em 2026-11-16
(D-EV-A0-2).

### 2.3 As sementes e o N (BT-3, BT-4, BT-5)

| etapa | faixa | bases | K por base | unidades | células | braços | vidas |
|---|---|---|---|---|---|---|---|
| calibração | 96101…96505 | 96101, 96202, 96303, 96404, 96505 | 5 | 25 | as 4 do `longe_fixo` | só TRIV, nos 96 pontos | 9 600 |
| validação | 97101…97505 | 97101, 97202, 97303, 97404, 97505 | 40 | **N = 200** | as 12 | REL e TRIV | 4 800 |

- **A derivação** é a da C4: semente `derivar_semente("digibrain_prototipo", base, k)`, k = 0…K−1.
- **As faixas foram conferidas livres** em 2026-11-16, em `faixas.py` e em todos os branches remotos. A 94xxx, a primeira candidata, já está
  com o EQUILIBRIO_CUIDADO (os PRs #898 e #906).
- **As duas faixas nunca se misturam:** a calibração não toca a 97xxx, e a validação não muda nada da calibração.

### 2.4 Os braços (BT-1)

- **REL:** o modular da C4, `SUBCHAVES_C4["REL"]`. É o braço com a memória autobiográfica ligada, o melhor modular medido no `longe_fixo`.
- **TRIV:** a baseline da seção 3, com o X, o Y e o Z da calibração.

## 3. A baseline trivial

`experiments/bancada/baseline_trivial.py`, com o teste em `tests/test_baseline_trivial.py`. As quatro regras do pedido, nesta ordem, e nada
mais:
1. **come** se a fome < X;
2. **dorme** se a energia < Y;
3. **brinca** se o tédio > Z;
4. **senão explora.**

**Como as entradas são lidas:**
- A fome e a energia vêm do `vetor_estado`, de 0 a 1, com 1 = satisfeito (como na `PoliticaInstinto`).
- O tédio vem do receptor do corpo (`PercepcaoCorpo.tedio`, de 0 a S, S = 1024), lido como fração de S. Sem o receptor, falha alto.

**O que a baseline não faz:**
- não aprende, não lembra e não lê a rng;
- não escolhe o alvo: o motor do mundo usa o alvo padrão (`mundo.alvo_padrao_de`). No comer, é a comida boa vista mais próxima, senão o
  cheiro; no explorar, continuar, o cheiro forte ou vagar; no brincar, a bola, se houver;
- os ganchos que o motor e o `Registro` chamam (`observar`, `consequencia_corpo`, `receber_acao_dono`) ficam sem efeito.

**As medidas da baseline** saem do ramo do A11 em `orq.medidas`, que só lê o motor e o registro: a taxa por episódio, a privação, a exaustão
e o d_fe. São as mesmas funções de `metrics.py` que medem o REL.

## 4. A calibração (só as sementes dela)

**4.1 As vidas.** Só a TRIV, nas 4 células do `longe_fixo`, nas 25 unidades da 96xxx, em cada ponto da grade (BT-4). As vidas não são
gravadas em disco: o replay é conferido do log em memória e as medidas vão para `artifacts_v3_baseline_trivial/calibracao/medidas.json`.

**4.2 A grade (BT-6), 6 × 4 × 4 = 96 pontos:**
- X (a fome) ∈ {0,3; 0,4; 0,5; 0,6; 0,7; 0,8};
- Y (a energia) ∈ {0,1; 0,2; 0,3; 0,4};
- Z (o tédio, em fração de S) ∈ {0,5; 0,7; 0,9; 1,0}. Z = 1,0 nunca brinca, porque o tédio não passa de S.

**4.3 A regra da escolha (BT-7), escrita antes:**
- Em cada ponto, a média sobre as 25 unidades da taxa por episódio, média nas 4 células do `longe_fixo`.
- **Vence a maior.** No empate exato, vence o menor (X, Y, Z) na ordem lexicográfica.
- Um ponto sem nenhuma unidade com episódio de fome falha alto.

O objetivo é o próprio primário: a baseline mais forte que a grade dá na medida em que o modular vai ser julgado. Assim o teste é o mais
duro para o modular.

**4.4 Depois da calibração:**
- A validação lê o ponto escolhido do `calibracao/resultado.json`, com o sha256 conferido contra o `calibracao/meta.json`, e o grava no
  meta dela. Ninguém escreve o X, o Y e o Z à mão.
- A grade não muda depois de vista. Se o ponto escolhido cair na borda da grade, isso é registrado e não muda a validação.

## 5. A validação (uma vez)

### 5.1 O teste

- O IC95 pelo t sobre as 200 unidades e o p unilateral, com o `orq.contraste_t` da C4 (o t pareado, A4.4.6).
- Ao lado, rotulados e sem mudar a decisão: o IC percentil do bootstrap (10 000 reamostragens, semente 4242) e o g1 com a ressalva.
- **Um contraste primário só, sem família e sem Holm.**

### 5.2 A margem (BT-8)

δ = 0,032, a da C4 (AD9-5), SEM FONTE: é o "efeito trivial". A margem efetiva (o menor efeito com poder 0,8 pelo dp observado) vai ao lado.
Pelo dp das diferenças por unidade da C4 (REL − SEM: margem efetiva 0,019 com 200 unidades), o N = 200 dá folga. O dp de REL − TRIV pode
ser outro, e o resultado reporta o observado.

### 5.3 A regra de leitura, escrita antes

A classe é a de A6.6 (`run_v2_longe_regular.classe`), na ordem:

| classe do IC95 de REL − TRIV | condição | a leitura |
|---|---|---|
| **≈ 0** | o IC inteiro dentro de (−0,032; +0,032) | empate: a baseline trivial faz o mesmo que o modular nesta medida. **H refutada** |
| **> 0** e inferior ≥ 0,032 | — | o modular vence, e o IC exclui o efeito trivial. **H confirmada** |
| **> 0** e inferior < 0,032 | — | o modular vence, mas o IC não exclui um efeito trivial. **H confirmada só no sinal** |
| **< 0** | — | a baseline vence o modular. **H refutada** |
| **indeterminado** | o IC cruza o 0 sem caber na margem | **H não confirmada nem refutada** |

**O que refutaria H:** um IC95 de REL − TRIV que inclui o 0 dentro da margem ("≈ 0") ou que fica todo abaixo do 0 ("< 0").

**O que o CHECKPOINT A2 faz com a leitura:** a classe vai ao Matheus como saiu, nas palavras do pedido. Se a baseline vencer ou empatar,
a definição do jogo muda e a poda (L5) fica obrigatória. Se o modular vencer com o IC que exclui o efeito trivial, a poda fica opcional.
Esta run não decide isso.

### 5.4 As secundárias e o descritivo (sem gate)

- **REL − TRIV no comedouro e no longe sorteado,** lidas pela mesma classe, sem previsão de sinal.
- **Os níveis de cada braço em cada lugar:** a taxa por episódio, a privação, a exaustão, o d_fe e o número de episódios por vida.
- **As ações somadas** por braço e lugar.

## 6. Uma vez, e o que fica no git

- **A validação roda uma vez.** O orquestrador recusa gravar por cima de uma pasta que existe.
- **Em `artifacts_v3_baseline_trivial/calibracao/`:** o `meta.json`, o `medidas.json` e o `resultado.json`.
- **Em `artifacts_v3_baseline_trivial/validacao/`:**
  - o `meta.json`;
  - o `medidas.json` (o `.gz` só se passar de 100 MB, como o pedido manda);
  - o `resultado.json`;
  - o `vidas.tar.gz` determinístico: nomes em ordem, mtime 0, dono 0, modo 0644, gzip com mtime 0. As vidas soltas ficam fora do git.
- **Cada meta grava:**
  - o commit (`git_head`) e o `git_limpo`;
  - o comando exato;
  - as versões do Python e do Node (a run não usa o Node; a versão fica como o pedido manda);
  - o sha256 do plano, da config, do orquestrador, da baseline, do protótipo e da C4;
  - o sha256 de cada artefato.
- **O resultado** vai em `docs/RESULTADO_V3_BASELINE_TRIVIAL.md`, com a leitura pela seção 5.3.

## 7. Se algo falhar

Uma falha alta (o replay, o T-CENARIO-1, as conferências da C4) **para a run, que volta ao Matheus** com o comando, a saída e a lacuna.
Nada se conserta para o número sair. Uma calibração que falhe alto não deixa a validação rodar.

## 8. O custo esperado

Medido na fumaça de hoje: cerca de 1,3 s de CPU por vida de 14 dias do REL, e menos na TRIV, mais o replay e as conferências.

| etapa | vidas | processos | parede estimada |
|---|---|---|---|
| calibração | 9 600 (TRIV) | 4 | ~1 h |
| validação | 4 800 (2 400 REL, 2 400 TRIV) | 4 | ~1 h |

Com a máquina livre (V3-D8), cada etapa é a única run de pesquisa na hora dela.

## 9. As decisões para o Matheus

Todas DECIDIDAS pela recomendação em 2026-11-16 ("Aprovo, pode rodar"); os números seguem SEM FONTE onde dito.

| id | decisão | a recomendação | o custo de errar |
|---|---|---|---|
| BT-1 | o modular é o REL da C4 | sim: o melhor modular medido no `longe_fixo`, o mais forte contra a baseline | com outro braço, a comparação não fala do modular que o C4 validou |
| BT-2 | as 12 células da C4 | **DECIDIDA** (2026-11-16, "Aprovo, siga a A1") | — |
| BT-3 | as faixas 96101…96505 (calibração) e 97101…97505 (validação) | aprovar | uma faixa ocupada: a run ficaria sem fonte |
| BT-4 | K = 5 na calibração (25 unidades por ponto) | sim: 9 600 vidas, ~1 h | pouco K: o ponto escolhido pelo ruído, e uma baseline um pouco mais fraca |
| BT-5 | K = 40 na validação (N = 200) | sim: o N da C4 | N menor: o IC mais largo, e mais chance de "indeterminado" |
| BT-6 | a grade 6 × 4 × 4 | aprovar | uma grade estreita: uma baseline mais fraca do que poderia, a favor do modular |
| BT-7 | a calibração maximiza o próprio primário | sim: o teste mais duro para o modular | outra medida: uma baseline mais fraca no primário |
| BT-8 | δ = 0,032 (a da C4) | sim: a mesma régua | outra margem: a leitura deixa de comparar com a C4 |
| BT-9 | o código no branch, não na `main`, antes da run | sim: o pedido pede a ordem dos commits no PR, e o merge é do Matheus | nenhum para o número: o meta grava o commit |

## 10. Referências

Nenhuma literatura nova. O método (o t sobre as unidades, a classe de A6.6, a margem e o bootstrap rotulado) é o do
`docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, adendos 6 e 9.
