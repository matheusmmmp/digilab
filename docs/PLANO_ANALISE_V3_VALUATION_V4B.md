# Plano de análise V3: VALUATION, a V4b, o empate do conserto com a baseline trivial com precisão

**Status: PROPOSTO.** Escrito em 2026-11-19 (Claude Code, Opus 5.5, branch `v3-valuation-v4b`), a pedido do Matheus: "Sim, escreve o
plano" (a pergunta era um plano da V4 maior, para fechar o empate com a TRIV). O orquestrador vai conferir este cabeçalho e recusar sem o
APROVADO. A tarefa é a [TAREFA_V3_VALUATION.md](TAREFA_V3_VALUATION.md).

## 0. O contexto e o que já foi visto

- **A V4** (69xxx, [RESULTADO_V3_VALUATION_VALIDACAO.md](RESULTADO_V3_VALUATION_VALIDACAO.md), #1013 na `main`) leu
  "indeterminado": CON − TRIV = −0,003 [−0,042; +0,036] no `longe_fixo`, com N = 200.
- **A razão é a precisão, não o sinal.** A margem efetiva (A6.5, o menor efeito com poder 0,8 pelo dp observado) foi 0,056, maior que
  δ = 0,032. Com o dp das diferenças por unidade (0,281), 200 unidades não bastam para que o IC95 caiba inteiro em ±0,032.
- **O que esta V4b usa da V4, e só isso:** o dp das diferenças, para dimensionar o N (seção 2.3). A média da V4 não entra em nada. As
  vidas da 69xxx **não se somam** às desta run: a V4 fica como saiu, e a V4b é uma run nova, em sementes novas.
- **A V4 não muda.** Esta V4b não reabre a leitura da V4 nem a da V3: o conserto continua reprovado pela exaustão e fora de qualquer pet.
- **Nenhum número deste plano** (a faixa, o N, a margem, a regra) é ajustado depois de vista uma vida da faixa nova.

## 1. A pergunta, a hipótese e a previsão

**A pergunta:** com o conserto do reflexo ligado, o modular fecha os episódios de fome no `longe_fixo` tão bem quanto a baseline
trivial, dentro de ±0,032?

**O contraste primário:** CON − TRIV na taxa por episódio (`episodios_fome.taxa`, a métrica da A1 e da V4, sem mudança), nas 4 células do
`longe_fixo`. A unidade é (base, semente), com a média das 4 células do dono da unidade, como na A1, na C4 e na V4.

**A previsão:** "≈ 0" (o empate). O tamanho é SEM FONTE; a V4 sugere um efeito perto de zero, mas não é previsão medida.

## 2. O desenho

### 2.1 O que não muda

- O motor, o corpo, o mundo, o `engine.py`, o modular e a métrica da A1.
- O cenário da A1, da C4 e da V4: o `CONFIG_MUNDO_MVP`, os 4 donos sem ensino, 14 dias, orçamento 16 por dia, morte desligada.
- **A TRIV** é a da A1, com o ponto já calibrado (fome 0,4, energia 0,1, tédio 0,5), lido do
  `artifacts_v3_baseline_trivial/calibracao/resultado.json` com o sha256 conferido. **Não há calibração nova.**
- **As vidas do CON** são as do `run_v3_valuation_conserto.py`, com a mesma conferência do reflexo decisão a decisão; a da TRIV é a do
  `run_v3_baseline_trivial.py`. São as mesmas funções que a V4 chamou.
- As chaves novas da `main` depois da V4 (a `reflexo_suave` da CORPO e outras) ficam **desligadas**, como no padrão.

### 2.2 Os braços e as células (VB4B-1, VB4B-2)

| braço | o que é |
|---|---|
| **TRIV** | a baseline trivial da A1, com o ponto da calibração da A1 |
| **CON** | o modular da C4 com a `guarda_fome_reflexo` ligada (o conserto da V3) |

- **Só as 4 células do `longe_fixo`** (os 4 donos), as do primário.
- **Sem o REL:** a réplica da A1 já saiu duas vezes no mesmo sentido (−0,083 na A1 e −0,102 na V4), e a pergunta é só CON − TRIV.
- **Sem o comedouro e o longe sorteado:** eles foram secundárias na V4 e não respondem a esta pergunta.

### 2.3 As sementes e o N (VB4B-3, VB4B-4)

- **O N pela regra de poder da A6.5,** com o dp da V4 (0,281) e δ = 0,032: (t₀,₉₅ + z₀,₈) × dp / √N ≤ δ pede N ≥ 483.
  - **A proposta é N = 600** (5 bases × K = 120), com a margem efetiva prevista em 0,0285.
  - A meia-largura prevista do IC95 é 0,023. O IC cabe em ±0,032 se a diferença verdadeira estiver a menos de cerca de 0,009 do zero.
- **A faixa:** 107101…107505, nas bases 107101, 107202, 107303, 107404 e 107505, com K = 120.
  - A derivação é a da C4: `derivar_semente("digibrain_prototipo", base, k)`.
  - A faixa entra no `FAIXAS_RESERVADAS` com a aprovação (VB4B-3). Ela foi conferida livre em 2026-11-19 no `faixas.py` da `main` e nos códigos, configs, testes e documentos de todos os branches remotos. A 105xxx, que também estava livre no `faixas.py`, já está pedida pela SOCIAL_PAR MD (branch `v3-social-par-md-plano`, MD-5) e ficou de fora.
- **As vidas:** 2 braços × 4 células × 600 unidades = **4 800 vidas**, cerca de 50 min com 4 processos (pela V4: 7 200 vidas em 1 h 13).

## 3. A análise

### 3.1 O primário

- **O teste:** o IC95 pelo t pareado sobre as 600 unidades e o p unilateral, com o `orq.contraste_t` da C4, como na V4.
- **Ao lado, rotulados e sem mudar a decisão:** o IC do bootstrap (10 000 reamostragens, semente 4242), o g1 e a margem efetiva.
- **Um contraste só, sem família.** A margem é δ = 0,032, a da A1, da C4 e da V4, SEM FONTE.

### 3.2 A regra de leitura, escrita antes

A classe é a de A6.6 (`run_v2_longe_regular.classe`), com as palavras da V4.

| classe do IC95 de CON − TRIV | a leitura |
|---|---|
| **> 0** | **ganho:** com o conserto, o modular fecha mais episódios que a TRIV |
| **≈ 0** (o IC inteiro dentro de ±0,032) | **nulo:** o conserto empata com a TRIV, e o gap da A1 fecha |
| **< 0** | **perda:** mesmo com o conserto, a TRIV fecha mais |
| **indeterminado** | **indeterminado:** o IC cruza o 0 sem caber na margem |

**Se sair "indeterminado" de novo,** a pergunta fecha assim e não se pede uma V4c: a resposta é que o efeito, se existe, é menor que a
precisão que se pode comprar com um custo razoável. A leitura vai ao Matheus como saiu.

### 3.3 O descritivo, sem gate

- A privação e a exaustão de cada braço, no `longe_fixo`, com CON − TRIV.
- Os episódios de fome por vida de cada braço.

### 3.4 O que a leitura não faz

- **Nenhuma leitura liga o conserto.** Ele reprovou na V3 pela G2, e um "nulo" aqui não muda isso: o pet continuaria exausto.
- **A V4b não se combina com a V4** em nenhuma conta (sem meta-análise, sem somar unidades).
- O resultado vai ao Matheus como saiu, no CHECKPOINT V4b.

## 4. Uma vez, e o que fica no git

- **A run roda uma vez.** O orquestrador recusa gravar por cima de uma pasta que existe.
- **Em `artifacts_v3_valuation/v4b/`** ficam o `meta.json`, o `resultado.json`, o `medidas.json` e o `vidas.tar.gz` determinístico,
  cada um com o sha256 no `meta.json`.
- **O `meta.json` grava** o commit e o `git_limpo`, o comando, as versões do Python e do Node, e o sha256 deste plano, da config, dos
  orquestradores e da calibração da A1.
- **O resultado** vai em `docs/RESULTADO_V3_VALUATION_V4B.md`.
- **O código** entra **depois** deste plano aprovado e antes da primeira vida:
  - o caminho mais curto é generalizar o `run_v3_valuation_validacao.py` para ler os braços, as células, as bases, o K, o plano e a
    saída da config (a V4 continua reproduzível pela config dela);
  - ou um orquestrador próprio, `run_v3_valuation_v4b.py`, que chama as mesmas funções.

  A escolha é técnica e vai no PR do código.
- **A run espera a vez da máquina:** uma run de pesquisa por vez e no máximo 4 processos (V3-D8), pelo `pre_run`.

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
| VB4B-1 | só os braços TRIV e CON | sim: a pergunta é só CON − TRIV, e a réplica do REL já saiu duas vezes | sem o REL, não se vê o gap da A1 nesta faixa; com ele, +2 400 vidas (+25 min) |
| VB4B-2 | só as 4 células do `longe_fixo` | sim: o primário; o comedouro e o longe já foram vistos na V4 | com as 12 células, 14 400 vidas e cerca de 2 h 30 |
| VB4B-3 | a faixa 107101…107505 | aprovar | uma faixa ocupada: a run ficaria sem fonte |
| VB4B-4 | N = 600 (5 bases × K = 120), pelo poder da A6.5 com o dp da V4 | sim: margem efetiva 0,0285 < δ | N = 500 fica no limite (0,031); N = 800 dá mais folga (0,025) por +1 600 vidas |
| VB4B-5 | a regra da seção 3.2, com δ = 0,032, e "indeterminado de novo fecha a pergunta" | sim: a régua da A1 e da V4 | outra margem: a V4b deixa de comparar com a V4 |

## 7. Referências

Nenhuma literatura nova. O método é o do `docs/PLANO_ANALISE_V3_VALUATION_VALIDACAO.md` e o do
`docs/PLANO_ANALISE_V3_BASELINE_TRIVIAL.md`; a regra de poder é a da A6.5 (`run_v2_longe_regular.margem_efetiva`).
