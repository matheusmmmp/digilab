# RESULTADO V3 — CORPO: a validação do teto baixo (C4), a run única (2026-11-20, Claude Code, Fable 5.2)

**O plano:** [PLANO_ANALISE_V3_CORPO_C4.md](PLANO_ANALISE_V3_CORPO_C4.md), APROVADO pelo Matheus em 2026-11-20 ("Aprovo todas"), na `main`
antes da primeira vida (#1039), com o código (#1043). O pré-registro: a seção `PR-CORPO-C4` do [PREREGISTRO.md](PREREGISTRO.md), escrita
antes da run. A tarefa: [TAREFA_V3_CORPO.md](TAREFA_V3_CORPO.md). A run que escolheu o braço: [RESULTADO_V3_CORPO_C3.md](RESULTADO_V3_CORPO_C3.md).

**A leitura, pela regra da seção 6 do plano: "confirma com ressalva".**
- **A primária passa.** O pet com o DTB passa mais tempo bem: DTB − CTRL no "Tempo bem" dá +0,062 [+0,058; +0,067] nas 12 células e
  +0,064 [+0,059; +0,068] nas 11 distintas, "> 0" nas duas, com p ≤ 0,025.
- **Nenhuma das sete guardas reprova.** A saúde, a taxa por episódio, o "Tempo bem" nos três lugares e o S2 passam.
- **A ressalva é uma célula: o aleatório no comedouro.** Ali a saúde do DTB cai −0,049 [−0,061; −0,038] ("< 0"). As outras cinco células
  dos donos que deixam faltar comida não saem em "< 0".
- **Todas as premissas se cumprem.** Nenhuma medida sai "inconclusiva por premissa".

**As hipóteses do plano (seção 1):**
- **H1, a primária "> 0" nas 12 e nas 11 células:** confirma.
- **H2, nenhuma guarda reprova:** confirma.
- **H3, a saúde do DTB abaixo da do CTRL no aleatório do comedouro:** confirma (−0,049; na C3, −0,048). O plano previu "confirma com
  ressalva", e foi o que saiu.

**O que a leitura pede (seção 9 do plano):** "confirma com ressalva" volta ao Matheus com a célula nomeada. Ele decide se a ressalva é
aceitável, se pede outra mudança, ou se o corpo fica como está. **Este é o CHECKPOINT da C4.** Nenhum braço está ligado no jogo.

**Três ressalvas, antes de ler os números:**
- **O T_B = C/2 é SEM FONTE.** A run validou um teto só. Ela não diz nada sobre outro teto.
- **O ganho não é igual em todo lugar.** No comedouro o "Tempo bem" sobe pouco (+0,029, dentro de δ), a privação não desce (+0,005) e a
  saúde média desce um pouco (−0,012, dentro de δ). O ganho grande está no longe e no `longe_fixo` (seção 3.1).
- **A célula da ressalva não aparece na primária.** No aleatório do comedouro, o "Tempo bem" do DTB é igual ao do CTRL
  (−0,001 [−0,005; +0,002]) e a saúde cai. A leitura por célula é o que mostra essa célula.

## 1. A run

| comando (o do `meta.json`) | commit | vidas | sementes | duração |
|---|---|---|---|---|
| `python experiments/run_v3_corpo_c4.py --config experiments/configs/v3_corpo_c4/run.json --processos 4` | `64a25595` (a `main` com o #1039 e o #1043) | 4 800 (2 braços × 12 células × 200 unidades) e 1 000 pares (2 braços × 500) | bloco I 107001…107200, k = 1, derivação `digibrain_prototipo`; bloco II 107301…107800, k = 1, prefixo `corpo_par` | 1 h 19 min (12:37–13:56 de 2026-11-20) |

- **O ambiente:** Python 3.13.0 e Node v24.19.0; o Node só fica gravado.
- **O pre_run:** a run esperou o replay do sono da PET_VIVO terminar (12:37:11) e saiu dois segundos depois, pelo orquestrador, que chama
  o `tools/pre_run.py`: o plano igual ao da `origin/main`, a faixa reservada e nenhuma outra run.
- **A saída:** código 0, o `run.err` vazio. As conferências rodaram vida a vida (o replay, o T-CENARIO-1, as da C4 do modular e a de cada
  braço).
- **A árvore:** o `meta.json` grava `git_limpo = true`. Os logs ficaram fora da worktree (`D:\Trab\digilab\logs_run_corpo_c4`).
- **O disco:** 78,3 GB livres no `D:` antes da run (o piso é 10 GB).
- **A duração:** 1 h 19 min, dentro da estimativa do plano (1 h a 1 h 40 min). As vidas levaram 67 min 40 s e os pares, 9 min 10 s.
- **A run rodou uma vez.** Nada foi ajustado depois de olhar.

**Os artefatos,** em `artifacts_v3_corpo/c4/`. O sha256 de cada arquivo no disco é igual ao do `meta.json`:

| arquivo | sha256 | tamanho |
|---|---|---|
| `resultado.json` | `136c3048…9f2d` | 128 kB |
| `medidas.json` | `c20881a8…e8a7` | 55,0 MB, abaixo dos 100 MB; vai sem `.gz` |
| `custos.json` | `a1e15518…f0aa` | 0,6 MB, o tempo de cada vida, fora das medidas |
| `pares.json` | `7cae1e19…743c` | 1,2 MB |
| `vidas.tar.gz` | `aabebacc…5745` | 22,4 MB, as 4 800 vidas |
| `pares.tar.gz` | `35fc3804…35c4` | 3,0 MB, os 1 000 pares |
| `meta.json` | `070067a3…907d` | |

- **As medidas sem o relógio:** o tempo de cada vida está só no `custos.json` (D-C4-8). O `medidas.json` e o `resultado.json` de uma
  réplica devem sair iguais byte a byte. Na fumaça, o teste confere isso; a run inteira não foi replicada.
- **A pasta crua:** o orquestrador conferiu os dois `.tar.gz` arquivo a arquivo contra as pastas `vidas/` e `pares/` (4 800 e 1 000
  arquivos) e apagou as pastas (`pasta_crua_apagada` no `meta.json`).

## 2. Os critérios (seção 6 do plano)

O contraste é DTB − CTRL, pareado por unidade (n = 200 no bloco I, 500 pares no bloco II), com o IC95 pelo t e as classes da A6.6, com
δ = 0,032 no bloco I. No S2, δ é 10 % do nível do CTRL na própria run (1,079 decisão, SEM FONTE).

**Como ler a classe "≈ 0":** pela regra da A6.6, um IC inteiro dentro de (−δ, +δ) é "≈ 0", mesmo quando ele não cruza o zero. Onde isso
acontece, a tabela traz o sinal.

**A primária, o "Tempo bem"** (a fração das decisões dos dias 1 a 14 sem privação e sem exaustão):

| onde | CTRL | DTB | DTB − CTRL | IC95 | classe | t (gl 199) | p unilateral |
|---|---|---|---|---|---|---|---|
| as 12 células | 0,633 | 0,695 | **+0,062** | [+0,058; +0,067] | > 0 | 28,1 | 1,4 × 10⁻⁷¹ |
| as 11 células distintas | 0,608 | 0,672 | **+0,064** | [+0,059; +0,068] | > 0 | 26,5 | 1,5 × 10⁻⁶⁷ |

- **A primária passa:** "> 0" nas duas, com p ≤ 0,025 nas duas.
- **O bootstrap** dá o mesmo intervalo nas 12 células: [+0,058; +0,067].

**As sete guardas, vinculantes:**

| guarda | reprova com | CTRL | DTB − CTRL | IC95 | classe | passa? |
|---|---|---|---|---|---|---|
| saúde, 12 células | < 0 | 0,628 | +0,056 | [+0,049; +0,064] | > 0 | sim |
| saúde, o relapso e o aleatório (6 células) | < 0 | 0,508 | +0,013 | [+0,005; +0,022] | ≈ 0, sinal + | sim |
| a taxa por episódio de fome, `longe_fixo` | < 0 | 0,572 | +0,126 | [+0,112; +0,140] | > 0 | sim |
| "Tempo bem", comedouro | < 0 | 0,757 | +0,029 | [+0,027; +0,031] | ≈ 0, sinal + | sim |
| "Tempo bem", longe | < 0 | 0,528 | +0,070 | [+0,062; +0,078] | > 0 | sim |
| "Tempo bem", `longe_fixo` | < 0 | 0,613 | +0,088 | [+0,078; +0,098] | > 0 | sim |
| S2, o tempo até o reencontro, em decisões | > 0 | 10,79 | −3,30 | [−4,31; −2,29] | < 0 | sim |

Nas 11 células distintas, as guardas dão a mesma leitura (o `guardas_11_celulas` do `resultado.json`): a saúde +0,061 [+0,053; +0,069] e
o "Tempo bem" do comedouro +0,023 [+0,021; +0,025], as duas passando.

**A saúde por célula** (a saúde média dos dias 8 a 14; uma célula em "< 0" não reprova, mas vira ressalva):

| célula | CTRL | DTB | DTB − CTRL | IC95 | classe |
|---|---|---|---|---|---|
| **aleatório, comedouro** | 0,397 | 0,347 | **−0,049** | [−0,061; −0,038] | **< 0, a ressalva** |
| aleatório, longe | 0,171 | 0,186 | +0,015 | [−0,001; +0,032] | ≈ 0 |
| aleatório, `longe_fixo` | 0,299 | 0,294 | −0,006 | [−0,022; +0,010] | ≈ 0 |
| relapso, comedouro | 0,965 | 0,957 | −0,008 | [−0,010; −0,006] | ≈ 0, sinal − |
| relapso, longe | 0,442 | 0,530 | +0,089 | [+0,051; +0,126] | > 0 |
| relapso, `longe_fixo` | 0,773 | 0,812 | +0,039 | [+0,020; +0,059] | > 0 |

**As premissas** (seção 5.2 do plano; todas se cumprem):

| premissa | de que medida | piso | na run |
|---|---|---|---|
| vidas com o "Tempo bem" em 0 ou em 1 | a primária | no máximo 5 % | CTRL 0 %; DTB 0,08 % (2 vidas de 2 400, as duas em 1) |
| a ponte no teto, fração dos ticks do DTB | o braço | pelo menos 0,10 em cada lugar | comedouro 0,27; longe 0,46; `longe_fixo` 0,36 |
| episódios de fome por vida, `longe_fixo` | a taxa por episódio | média de 8 ou mais; no máximo 2 % sem episódio | CTRL 13,0; DTB 17,4; nenhuma vida sem episódio |
| pares em que a janela do reencontro cabe | o S2 | pelo menos 90 % | 100 % nos dois braços |
| chutes por vida do CTRL, `longe_fixo` | o descritivo dos chutes | média de 1 ou mais; 50 % das vidas com chute | 2,49 por vida; 81 % das vidas |

**O veredito do orquestrador:** `leitura = "confirma com ressalva"`, `celulas_em_ressalva = ["aleatorio|comedouro"]`, nenhuma guarda
reprovada, nenhuma premissa descumprida, nenhuma medida inconclusiva.

**A precisão prevista e a que saiu** (a meia largura do IC95, seção 5.3 do plano):

| medida | prevista | na run | δ |
|---|---|---|---|
| "Tempo bem", 12 células | 0,004 | 0,004 | 0,032 |
| "Tempo bem", 11 células | 0,005 | 0,005 | 0,032 |
| a taxa por episódio, `longe_fixo` | 0,015 | 0,014 | 0,032 |
| saúde, 12 células | 0,007 | 0,008 | 0,032 |
| saúde, o aleatório no comedouro | 0,010 | 0,011 | 0,032 |
| saúde, o relapso no longe | 0,036 | 0,037 | 0,032 |
| S2, com 500 pares | 0,97 | 1,01 | 1,079 |

O relapso no longe saiu com a meia largura acima de δ, como previsto, mas a classe ali foi "> 0". O S2 coube em δ com os 500 pares.

## 3. O descritivo (sem teste)

Nada nesta seção entra na leitura. Os intervalos são o IC95 pelo t sobre as 200 unidades, sem p e sem correção.

### 3.1 Por lugar

| medida | comedouro | longe | `longe_fixo` | 12 células |
|---|---|---|---|---|
| "Tempo bem", dias 1 a 14 | +0,029 [+0,027; +0,031] | +0,070 [+0,062; +0,078] | +0,088 [+0,078; +0,098] | +0,062 [+0,058; +0,067] |
| "Tempo bem", dias 8 a 14 | +0,035 [+0,031; +0,039] | +0,098 [+0,083; +0,112] | +0,102 [+0,088; +0,115] | +0,078 [+0,072; +0,085] |
| privação, a vida toda | +0,008 [+0,006; +0,010] | −0,053 [−0,061; −0,045] | −0,070 [−0,081; −0,059] | −0,038 [−0,043; −0,033] |
| exaustão, a vida toda | −0,054 [−0,056; −0,052] | −0,098 [−0,101; −0,094] | −0,087 [−0,092; −0,082] | −0,080 [−0,082; −0,077] |
| saúde média, dias 8 a 14 | −0,012 [−0,016; −0,009] | +0,093 [+0,076; +0,111] | +0,088 [+0,073; +0,103] | +0,056 [+0,049; +0,064] |
| a taxa por episódio de fome | +0,071 [+0,063; +0,079] | +0,088 [+0,075; +0,101] | +0,126 [+0,112; +0,140] | +0,095 [+0,088; +0,102] |
| episódios de fome por vida | +3,6 (17,2 → 20,8) | +3,4 (11,6 → 14,9) | +4,4 (13,0 → 17,4) | +3,8 (13,9 → 17,7) |
| refeições por dia | +0,41 (4,02 → 4,43) | +0,36 (2,42 → 2,78) | +0,58 (3,00 → 3,58) | +0,45 (3,15 → 3,60) |
| fração dos ticks dormindo | −0,081 (0,467 → 0,386) | −0,094 (0,466 → 0,372) | −0,088 (0,462 → 0,374) | −0,088 (0,465 → 0,377) |
| "brincar" por vida | +23,6 (21,6 → 45,1) | +14,5 (29,0 → 43,5) | +20,1 (29,6 → 49,7) | +19,4 (26,7 → 46,1) |
| reflexos por vida | −72 (207 → 135) | −130 (332 → 203) | −116 (268 → 152) | −106 (269 → 163) |

- **De onde vem o ganho no "Tempo bem":** nas 12 células, a exaustão desce −0,080 e a privação desce −0,038. No comedouro só a exaustão
  desce; a privação sobe +0,008.
- **O comedouro é o lugar em que o DTB ganha menos,** como na C3. Ali a saúde média desce −0,012 [−0,016; −0,009]. Fica dentro de δ, e
  a saúde por lugar não é guarda neste plano. Fica escrito porque é o único lugar em que a saúde desce.
- **O pet dorme menos e brinca mais** com o DTB, nos três lugares.
- **Os episódios de fome a mais do DTB** (+3,8 por vida) repetem a C3. A causa continua sem explicação; a seção 3.6 traz a fome medida
  de outro jeito, e ela desce na média.

### 3.2 As guardas da C3, ao lado (dias 8 a 14)

| guarda da C3 | C3, DTB − CTRL | C4, DTB − CTRL |
|---|---|---|
| privação, comedouro | +0,005 [+0,002; +0,008] | +0,005 [+0,002; +0,009] |
| privação, longe | −0,087 [−0,101; −0,072] | −0,085 [−0,100; −0,070] |
| privação, `longe_fixo` | −0,070 [−0,082; −0,057] | −0,084 [−0,098; −0,069] |
| privação, 12 células | −0,050 [−0,057; −0,044] | −0,054 [−0,061; −0,048] |
| exaustão, `longe_fixo` | −0,099 [−0,106; −0,092] | −0,100 [−0,107; −0,093] |
| exaustão, 12 células | −0,095 [−0,098; −0,092] | −0,095 [−0,098; −0,092] |
| saúde, 12 células | +0,051 [+0,044; +0,058] | +0,056 [+0,049; +0,064] |
| saúde, o relapso e o aleatório | +0,007 [−0,002; +0,015] | +0,013 [+0,005; +0,022] |

### 3.3 A comparação com a C3, nas medidas da C4

| medida | C3 (a run que escolheu o braço) | C4 (sementes novas) |
|---|---|---|
| "Tempo bem", 12 células | +0,062 [+0,058; +0,066] | +0,062 [+0,058; +0,067] |
| "Tempo bem", 11 células | +0,063 [+0,059; +0,068] | +0,064 [+0,059; +0,068] |
| "Tempo bem", comedouro | +0,030 [+0,028; +0,032] | +0,029 [+0,027; +0,031] |
| "Tempo bem", longe | +0,073 [+0,065; +0,081] | +0,070 [+0,062; +0,078] |
| "Tempo bem", `longe_fixo` | +0,083 [+0,074; +0,093] | +0,088 [+0,078; +0,098] |
| a taxa por episódio, `longe_fixo` | +0,120 [+0,105; +0,135] | +0,126 [+0,112; +0,140] |
| saúde, o aleatório no comedouro | −0,048 [−0,058; −0,037] | −0,049 [−0,061; −0,038] |
| S2, o tempo até o reencontro | −2,34 [−4,53; −0,15], 100 pares | −3,30 [−4,31; −2,29], 500 pares |

Os números da C3 vêm do `artifacts_v3_corpo/c3/resultado.json` e do `artifacts_v3_corpo/c3_tempo_bem/resumo.json` (os sha256 estão em
`comparacao_com_a_c3.fontes_sha256`). Em sementes novas, cada medida repete a C3 dentro do intervalo.

### 3.4 Por dono (o "Tempo bem" por célula)

| célula | CTRL | DTB | DTB − CTRL | IC95 |
|---|---|---|---|---|
| atencioso, comedouro | 0,901 | 0,949 | +0,048 | [+0,044; +0,052] |
| atencioso, longe | 0,663 | 0,753 | +0,090 | [+0,065; +0,114] |
| atencioso, `longe_fixo` | 0,725 | 0,879 | +0,155 | [+0,129; +0,180] |
| incoerente, comedouro | 0,901 | 0,949 | +0,048 | [+0,044; +0,052] |
| incoerente, longe | 0,656 | 0,764 | +0,108 | [+0,088; +0,128] |
| incoerente, `longe_fixo` | 0,738 | 0,867 | +0,129 | [+0,108; +0,151] |
| relapso, comedouro | 0,739 | 0,760 | +0,021 | [+0,019; +0,024] |
| relapso, longe | 0,461 | 0,511 | +0,050 | [+0,040; +0,060] |
| relapso, `longe_fixo` | 0,589 | 0,633 | +0,044 | [+0,035; +0,052] |
| aleatório, comedouro | 0,488 | 0,487 | −0,001 | [−0,005; +0,002] |
| aleatório, longe | 0,333 | 0,366 | +0,032 | [+0,025; +0,040] |
| aleatório, `longe_fixo` | 0,401 | 0,425 | +0,024 | [+0,017; +0,031] |

- **O ganho é maior com os donos que alimentam** (o atencioso e o incoerente) e menor com o relapso e o aleatório.
- **A célula da ressalva, o aleatório no comedouro:** o "Tempo bem" não muda, a privação dos dias 8 a 14 sobe +0,026 [+0,021; +0,031], a
  exaustão desce −0,079, as refeições por dia não mudam (2,61 e 2,62) e a saúde cai −0,049. No CTRL o pet já vive mal ali (saúde 0,397).
- **O relapso no comedouro** vai na mesma direção, em tamanho menor: a privação sobe +0,025 e a saúde desce −0,008.
- **O incoerente no comedouro** sai igual ao atencioso em 200 de 200 vidas, nos dois braços. As 12 células têm 11 distintas, e por isso
  a primária foi lida nas duas contagens.

### 3.5 Os chutes por vida (D-C4-4)

| lugar | CTRL | DTB | DTB − CTRL | IC95 | vidas com chute, CTRL e DTB |
|---|---|---|---|---|---|
| comedouro | 0,015 | 0,005 | −0,010 | [−0,022; +0,002] | 1,1 % e 0,4 % |
| longe | 0,95 | 1,38 | +0,44 | [+0,24; +0,63] | 42 % e 47 % |
| `longe_fixo` | 2,49 | 2,72 | +0,23 | [+0,05; +0,41] | 81 % e 86 % |

- **No comedouro o descritivo sai quase vazio,** como o plano avisou: a bola quase nunca é chutada ali.
- **Fora do comedouro, o DTB chutou mais que o CTRL.** A contagem nas sementes dos testes, escrita no plano antes da run, tinha o
  contrário (45 chutes contra 64 em 20 vidas, 5 unidades). Com 200 unidades, ela não se repete.
- **Não é guarda.** Não há teste nem correção aqui.

### 3.6 A fome (replay acrescentado depois da aprovação)

Um descritivo acrescentado depois da aprovação do plano. **Não tem teste nem classe, não entra na leitura da seção 6 e não muda regra
nenhuma.**
- **De onde vem:** a Gerência sugeriu olhar a fome diretamente (a fome média e a fração do tempo com a fome acima de 0,5, por lugar e
  por célula). A sugestão chegou depois da aprovação. O Matheus escolheu, em 2026-11-20, "Replay depois": o descritivo entra por um
  replay das vidas gravadas, e o orquestrador da run não muda.
- **O que ele faz:** o `experiments/run_v3_corpo_c4_fome.py` refaz as 4 800 vidas, confere cada uma contra o `log_sha256` e o "Tempo bem"
  do `medidas.json` (todas bateram; uma que não batesse parava o replay), e mede a fome nas decisões dos dias 1 a 14
  (`digilab.metrics.fome_nas_decisoes`).
- **A medida:** a fome é o complemento da fome da `Observacao`, de 0 (saciado) a 1. O corte de 0,5 é o teto do DTB (C/2), SEM FONTE.
  "Acima" é estrito: a decisão com a fome exatamente no teto não conta.
- **O replay:** rodou em 2026-11-20, das 15:13 às 15:48 (34 min 53 s, 4 processos), no commit `d5176552` da `main`, com a saída 0 e o
  log de erros vazio. Ele esperou a run de outra frente liberar a máquina.
- **Os artefatos,** em `artifacts_v3_corpo/c4_fome/`: `fome.json` (`2d779867…8a4c`, as 4 800 vidas), `resumo.json` (`215533cc…c6c3`) e
  `meta.json` (`26cc294b…8a3e`). O `meta.json` grava o sha256 do `medidas.json` e do `meta.json` da run.

**Por lugar** (o IC95 pelo t sobre as 200 unidades):

| onde | fome média: CTRL | DTB | DTB − CTRL | acima de 0,5: CTRL | DTB | DTB − CTRL |
|---|---|---|---|---|---|---|
| comedouro | 0,382 | 0,385 | +0,003 [+0,002; +0,005] | 0,302 | 0,332 | +0,030 [+0,028; +0,033] |
| longe | 0,598 | 0,557 | −0,041 [−0,047; −0,035] | 0,572 | 0,542 | −0,030 [−0,038; −0,022] |
| `longe_fixo` | 0,519 | 0,463 | −0,056 [−0,064; −0,048] | 0,465 | 0,421 | −0,044 [−0,054; −0,034] |
| as 12 células | 0,500 | 0,469 | −0,031 [−0,035; −0,028] | 0,446 | 0,432 | −0,015 [−0,019; −0,010] |
| as 11 células distintas | 0,525 | 0,493 | −0,032 [−0,036; −0,028] | 0,480 | 0,464 | −0,016 [−0,020; −0,011] |

**Por célula:**

| célula | fome média: CTRL | DTB | DTB − CTRL | acima de 0,5: CTRL | DTB | DTB − CTRL |
|---|---|---|---|---|---|---|
| atencioso, comedouro | 0,222 | 0,196 | −0,026 [−0,028; −0,024] | 0,079 | 0,075 | −0,004 [−0,007; −0,001] |
| atencioso, longe | 0,470 | 0,406 | −0,064 [−0,083; −0,045] | 0,383 | 0,327 | −0,055 [−0,078; −0,032] |
| atencioso, `longe_fixo` | 0,412 | 0,290 | −0,122 [−0,142; −0,102] | 0,304 | 0,184 | −0,120 [−0,145; −0,095] |
| incoerente, comedouro | 0,222 | 0,196 | −0,026 [−0,028; −0,024] | 0,079 | 0,075 | −0,004 [−0,007; −0,001] |
| incoerente, longe | 0,480 | 0,399 | −0,081 [−0,097; −0,065] | 0,394 | 0,319 | −0,075 [−0,094; −0,056] |
| incoerente, `longe_fixo` | 0,402 | 0,302 | −0,100 [−0,117; −0,083] | 0,291 | 0,197 | −0,094 [−0,115; −0,073] |
| relapso, comedouro | 0,491 | 0,531 | +0,041 [+0,038; +0,043] | 0,460 | 0,546 | +0,086 [+0,080; +0,091] |
| relapso, longe | 0,694 | 0,686 | −0,008 [−0,016; −0,000] | 0,728 | 0,737 | +0,009 [−0,002; +0,021] |
| relapso, `longe_fixo` | 0,587 | 0,591 | +0,004 [−0,003; +0,011] | 0,579 | 0,609 | +0,030 [+0,020; +0,041] |
| aleatório, comedouro | 0,594 | 0,617 | +0,023 [+0,020; +0,027] | 0,588 | 0,633 | +0,045 [+0,039; +0,051] |
| aleatório, longe | 0,750 | 0,738 | −0,011 [−0,018; −0,004] | 0,785 | 0,785 | +0,001 [−0,009; +0,011] |
| aleatório, `longe_fixo` | 0,676 | 0,669 | −0,007 [−0,013; −0,000] | 0,687 | 0,693 | +0,006 [−0,004; +0,015] |

**O que as tabelas mostram:**
- **Na média das 12 células, o pet com o DTB tem menos fome,** e não mais: a fome média desce de 0,500 para 0,469, e a fração do tempo
  acima de 0,5 desce de 0,446 para 0,432. A ponte passa a subir a fome, mas o pet come mais (+0,45 refeição por dia, seção 3.1).
- **A queda vem do longe e do `longe_fixo`.** No comedouro a fome média quase não muda (+0,003), e o tempo acima de 0,5 sobe +0,030.
- **Com os donos que alimentam** (o atencioso e o incoerente), a fome desce em todo lugar, até −0,122 no `longe_fixo`.
- **Com o relapso e o aleatório no comedouro, a fome sobe:** o relapso passa +0,086 a mais do tempo acima de 0,5, e o aleatório,
  +0,045. São as duas células em que a saúde desce (seção 2). É o mesmo quadro do diagnóstico da D, em tamanho menor: sem comida a
  mais, a falta que ia para o cansaço vai para a fome.
- **A célula da ressalva, o aleatório no comedouro:** a fome média sobe +0,023 [+0,020; +0,027], num pet que no CTRL já passa 0,588
  do tempo acima de 0,5.

**O que elas não explicam:** os episódios de fome a mais do DTB (+3,8 por vida). A fome média desce e os episódios sobem. Isso é
compatível com episódios mais curtos, mas a duração dos episódios não foi medida aqui.

### 3.7 O bloco II

Os 1 000 pares (500 por braço, 5 dias). A janela do reencontro coube em todos. O tempo médio até o reencontro foi de 10,79 decisões
no CTRL e 7,49 no DTB. A bola fica fora da leitura dos pares (D-C4-4).

## 4. O que fica em aberto

- **O CHECKPOINT da C4 (do Matheus):** a leitura é "confirma com ressalva", e a célula é o aleatório no comedouro. Pela seção 9 do plano,
  ele decide entre três caminhos: aceitar a ressalva e seguir para a C5 (a síntese e a especificação); pedir outra mudança; ou deixar o
  corpo como está.
- **Ligar o DTB no jogo não está em decisão aqui.** Pelo plano, é uma decisão à parte, depois da C5.
- **O T_B = 225 000 continua PROPOSTO e SEM FONTE.** Passar a DECIDIDO é do Matheus.
- **O comedouro:** o lugar em que o DTB ganha menos, com a privação um pouco acima e a saúde um pouco abaixo, tudo dentro de δ.
- **Os episódios de fome a mais do DTB** continuam sem explicação: a fome média desce com o DTB (seção 3.6), e a duração dos episódios
  não foi medida.
- **O incoerente no comedouro** é o atencioso; a causa exata fica para o replay dos donos (o R-c), que espera a confirmação do Matheus.
- **A run inteira não foi replicada.** O `medidas.json` sem o relógio permite a réplica byte a byte.

**O que esta run não demonstra** (o `nao_demonstra` do `resultado.json`): nada sobre o jogo web, onde a chave fica desligada; nada sobre
outro teto além de C/2; nada sobre a E e a C5 com o teto; nada sobre o social além do substrato, porque nenhum mecanismo social entra.
