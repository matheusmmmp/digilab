# Plano de análise V3: VALUATION, a V4, a validação contra a baseline trivial

**Status: PROPOSTO.** Escrito em 2026-11-18 (Claude Code, Opus 5.5, branch `v3-valuation-v4`), a pedido do Matheus: "Então faz a
validação contra o baseline trivial". Nenhuma vida roda antes do "APROVADO pelo Matheus" neste cabeçalho; o orquestrador confere e recusa
sem ele. A tarefa é a [TAREFA_V3_VALUATION.md](TAREFA_V3_VALUATION.md).

## 0. O contexto e o que já foi visto

- **A frente estava encerrada** (D-VAL-23, "Encerrar, ir à V5"), sem a V4, porque o conserto reprovou na V3 pela exaustão (G2). O pedido de
  hoje reabre só a V4. Ele **não** muda a leitura da V3: o conserto continua reprovado e fora de qualquer pet.
- **O que já foi visto, e é a razão de escrever a previsão antes:**
  - **A1** (97xxx, `artifacts_v3_baseline_trivial/validacao/resultado.json`): REL − TRIV = −0,083 [−0,128; −0,038] no `longe_fixo`. A TRIV
    fechava 0,645 com a exaustão 1,000.
  - **V3** (73xxx, `artifacts_v3_valuation/conserto/resultado.json`): CON 0,671 e REL 0,564 no `longe_fixo`, CON − REL = +0,106.
  - Pela comparação **entre runs**, só descritiva, o CON ficaria perto da TRIV ou acima dela. Esse número não é um contraste, e esta V4
    existe para medi-lo de verdade, nas mesmas sementes.
- **Nenhum número deste plano** (as faixas, o N, a margem, a regra) é ajustado depois de vista uma vida da 81xxx.

## 1. A pergunta, a hipótese e a previsão

**A pergunta:** com o conserto do reflexo ligado, o modular fecha os episódios de fome no `longe_fixo` tão bem quanto a baseline trivial?

**O contraste primário:** CON − TRIV na taxa por episódio (`episodios_fome.taxa`, a métrica da A1, sem mudança), nas 4 células do
`longe_fixo`. A unidade é (base, semente), com a média das 4 células do dono da unidade, como na A1 e na C4.

**A previsão:** "≈ 0" ou "> 0" (o conserto fecha o gap da A1). O tamanho é SEM FONTE.

## 2. O desenho

### 2.1 O que não muda

- O motor, o corpo, o mundo, o `engine.py`, o modular e a métrica da A1.
- O cenário da A1 e da C4: o `CONFIG_MUNDO_MVP`, os 4 donos sem ensino, 14 dias, orçamento 16 por dia, morte desligada.
- **A baseline TRIV** é a da A1 (`experiments/bancada/baseline_trivial.py`), com o **ponto já calibrado** na A1 (fome 0,4, energia 0,1,
  tédio 0,5), lido do `artifacts_v3_baseline_trivial/calibracao/resultado.json` com o sha256 conferido contra o `meta.json` dela.
  **Não há calibração nova** (VB-2).
- **As vidas do REL e do CON** são as do `run_v3_valuation_conserto.py`, com a mesma conferência do reflexo decisão a decisão. A da TRIV
  é a do `run_v3_baseline_trivial.py`.

### 2.2 Os braços (VB-1)

| braço | o que é |
|---|---|
| **TRIV** | a baseline trivial da A1, com o ponto da calibração da A1 |
| **REL** | o modular da C4, com a chave do conserto desligada |
| **CON** | o REL com a `guarda_fome_reflexo` ligada (o conserto da V3, que reprovou pela exaustão) |

### 2.3 As células, as sementes e o N (VB-3, VB-4)

- **As 12 células da C4:** os 4 donos × `longe_fixo` (o primário), o comedouro e o longe sorteado.
- **A faixa:** 81101…81505, nas bases 81101, 81202, 81303, 81404 e 81505, com K = 40, ou seja, **N = 200 unidades**.
  - A derivação é a da C4: `derivar_semente("digibrain_prototipo", base, k)`.
  - A faixa foi conferida livre em 2026-11-18, no `faixas.py` da `main` e nos branches remotos.
  - Ela entra no `FAIXAS_RESERVADAS` antes da run.
- **As vidas:** 3 braços × 12 células × 200 unidades = **7 200 vidas**, cerca de 1 h 30 com 4 processos.

## 3. A análise

### 3.1 O primário

- **O teste:** o IC95 pelo t pareado sobre as 200 unidades e o p unilateral, com o `orq.contraste_t` da C4.
- **Ao lado, rotulados e sem mudar a decisão:** o IC do bootstrap (10 000 reamostragens, semente 4242) e o g1.
- **Um contraste só, sem família.** A margem é δ = 0,032, a da A1 e da C4, SEM FONTE.

### 3.2 A regra de leitura, escrita antes

A classe é a de A6.6 (`run_v2_longe_regular.classe`). A leitura usa as palavras do pedido: ganho, perda, nulo e indeterminado.

| classe do IC95 de CON − TRIV | a leitura |
|---|---|
| **> 0** | **ganho:** com o conserto, o modular fecha mais episódios que a TRIV |
| **≈ 0** (o IC inteiro dentro de ±0,032) | **nulo:** o conserto empata com a TRIV, e o gap da A1 fecha |
| **< 0** | **perda:** mesmo com o conserto, a TRIV fecha mais |
| **indeterminado** | **indeterminado:** o IC cruza o 0 sem caber na margem |

### 3.3 As secundárias e o descritivo, sem gate

- **REL − TRIV no `longe_fixo`:** a réplica da A1 em sementes novas, lida pela mesma classe e sem previsão nova.
- **CON − TRIV no comedouro e no longe sorteado,** pela mesma classe.
- **A privação e a exaustão de cada braço, em cada lugar,** com CON − TRIV e REL − TRIV. A V3 já mostrou que o CON é mais exausto que o REL,
  e a A1, que a TRIV fica exausta o tempo todo. Aqui isso é só descritivo.

### 3.4 O que a leitura não faz

- **Nenhuma leitura liga o conserto.** Ele reprovou na V3 pela G2, e um "ganho" ou "nulo" aqui não muda isso: o pet continuaria exausto.
- O resultado vai ao Matheus como saiu, no CHECKPOINT V4.

## 4. Uma vez, e o que fica no git

- **A run roda uma vez.** O orquestrador recusa gravar por cima de uma pasta que existe.
- **Em `artifacts_v3_valuation/validacao/`** ficam os artefatos, cada um com o sha256 no `meta.json`:
  - o `meta.json`, o `resultado.json` e o `medidas.json`;
  - o `vidas.tar.gz` determinístico.
- **O `meta.json` grava:**
  - o commit e o `git_limpo`;
  - o comando;
  - as versões do Python e do Node;
  - o sha256 deste plano, da config, dos orquestradores e da calibração da A1.
- **O resultado** vai em `docs/RESULTADO_V3_VALUATION_VALIDACAO.md`.
- **O código** (o `experiments/run_v3_valuation_validacao.py`, a config e os testes) entra **depois** deste plano aprovado e antes da
  primeira vida.

## 5. Se algo falhar

Uma falha alta para a run, que volta ao Matheus com o comando, a saída e a lacuna. Falha alta é qualquer uma destas:
- o replay;
- o T-CENARIO-1;
- as conferências da C4 e a do reflexo;
- o sha256 da calibração da A1.

Nada se conserta para o número sair.

## 6. As decisões para o Matheus

| id | decisão | a recomendação | o custo de errar |
|---|---|---|---|
| VB-1 | os 3 braços TRIV, REL e CON | sim: o CON é o que a pergunta mede, e o REL dá a réplica da A1 na mesma faixa, por pouco custo | sem o REL, não há como ver se a 81xxx repete o gap da A1 |
| VB-2 | a TRIV com o ponto da calibração da A1, sem calibrar de novo | sim: a mesma baseline que a A1 julgou, e a calibração não se repete | uma calibração nova gastaria uma faixa e mudaria a régua |
| VB-3 | a faixa 81101…81505, K = 40, N = 200 | aprovar | uma faixa ocupada: a run ficaria sem fonte |
| VB-4 | as 12 células, com o primário no `longe_fixo` | sim: as da A1 e da V3 | só o `longe_fixo`: sem o descritivo do comedouro e do longe |
| VB-5 | a regra da seção 3.2, com δ = 0,032 | sim: a régua da A1 | outra margem: a V4 deixa de comparar com a A1 |

## 7. Referências

Nenhuma literatura nova. O método é o do `docs/PLANO_ANALISE_V3_BASELINE_TRIVIAL.md` e o do
`docs/PLANO_ANALISE_V3_VALUATION_CONSERTO.md`.
