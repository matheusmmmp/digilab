# RESULTADO V3 — GOSTO_VISUAL, GV3b: a GV3 de novo, com o enjoo da imagem ligado (adendo 2) (2026-11-12, Claude Code, Opus 5.5)

**Os planos:**
- o [adendo 2](PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO2.md), APROVADO pelo Matheus em 2026-11-12 ("Adendo e faixa nova"), com as GV3B2-1 a 7
  DECIDIDAS pela recomendação (D-GV-GV3B2-12, empurrado antes da primeira vida, `40ceb5e5`);
- por baixo dele, o [adendo 1](PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO1.md) (as GV3B-1 a 8, as expectativas E1 a E4) e o
  [plano da GV3](PLANO_ANALISE_V3_GOSTO_VISUAL.md) (as frases da 7.2).

**Este resultado é descritivo**, como o plano. Todos os números são PROPOSTOS e SEM FONTE. O documento não afirma que o pet "gosta",
"enjoa" ou sente tédio: são nomes de mecanismo e de medida. **Nenhuma alegação de novidade.** Nenhuma referência é citada.

**A run parcial do adendo 1** (`artifacts_v3_gosto_visual/gosto_visual_enjoo/`, a faixa 90xxx, queimada) não entra aqui nem na comparação
(adendo 2, seções 3 e 4). A comparação é com a GV3 original (`docs/RESULTADO_V3_GOSTO_VISUAL.md`), **só lado a lado** (adendo 1, seção 7).

## 0. O piloto, a run e os artefatos

- **O piloto** (bases 91101 e 91202, K = 2, 24 vidas): `artifacts_v3_gosto_visual/piloto_enjoo2/`.
  - 4 processos, 2026-11-12, das 12:08:15 às 12:22:13 (838,1 s, `meta.json`, `duracao_s`). O custo foi 139,0 s por vida em média
    (`custo.json`).
  - **As duas conferências do adendo 2** (`analise.json`, `conferencia` e `sem_lugar`):
    - a GVP-7: 504 réplicas, a fração com uma olhada 0,952, mínimo 0,25;
    - o teto: 0 réplicas sem lugar em 504, teto 5 %, nenhuma célula acima.

    Resultado: **`a_run_pode_rodar: true`**. Nada foi ajustado olhando o piloto.
  - A pasta foi commitada e empurrada antes da run (`597638b2`), como pede a seção 7 do adendo 2.
- **A run** (bases 91303, 91404 e 91505, K = 12: 36 unidades, 216 vidas de 14 dias), **uma vez**:
  `artifacts_v3_gosto_visual/gosto_visual_enjoo2/`.
  - No commit `597638b2`, com o git limpo (`meta.json`: `git_head`, `git_limpo: true`), 4 processos, de 2026-11-12T12:23:30 a 12:51:13
    (1662,6 s de parede, `meta.json`, `duracao_s`). Nenhuma outra run de pesquisa ou medição rodava.
  - A medição do combate que rodava antes do piloto terminou antes dele.
  - **O custo** (`custo.json`): 30,6 s por vida em média, 102,7 s no máximo, 1660,1 s de parede nas vidas.
  - **A conferência por réplica** (`analise.json`, `conferencia`): 4536 réplicas, a fração com uma olhada 0,932.
- **Os arquivos:**
  - no git: `meta.json`, `medidas.json`, `analise.json`, `custo.json`, `vidas.tar.gz` (216 vidas e 216 sondas) e
    `contas_resultado.py`/`.json`;
  - fora do git: as vidas soltas (`.gitignore`).

  Os sha256 do `medidas.json`, do `analise.json` e do `custo.json` batem com os do `meta.json` (`artefatos_sha256`), que vale como o
  registro da execução (adendo 2, seção 8).
- **A origem dos números:**
  - todo número da GV3b sai do `analise.json` da run, salvo os marcados `contas_resultado.json`, que saem do `contas_resultado.py` da mesma
    pasta, só sobre o `medidas.json`;
  - o `contas_resultado.py` refaz a análise e a contagem das sem lugar a partir do `medidas.json`, e as quatro saem iguais
    (`analise_refeita_igual`);
  - os números da GV3 saem de `artifacts_v3_gosto_visual/gosto_visual/analise.json`.

## 1. As réplicas sem lugar (adendo 2, seção 2)

`analise.json`, `sem_lugar`: **0 réplicas sem lugar em 4536 tentadas** no total (fração 0,0), e **0 em 756 em cada uma das seis
células**, contra o teto de 5 %. Nenhuma célula fica acima do teto, então nenhuma frase leva a ressalva. Nenhum dia ficou sem sonda e
nenhum pet ficou sem sonda válida (`contas_resultado.json`: `dias_sem_sonda` 0 e `replicas_sem_lugar` 0; `analise.json`,
`sem_sonda_valida` 0 nas seis células).

## 2. A familiarização (plano, 2.2)

`analise.json`, `familiarizacao`: **213 das 216 vidas passaram no critério**, então `nao_estabilizou: false`.
- **As estáveis por célula, em 36:** próprio × nenhum 36, × calmo 36, × agitado 35; vazio × nenhum 34, × calmo 36, × agitado 36.
- **A fração média das decisões acordadas olhando a TV da vida** fica entre 0,024 e 0,026 nas seis células (`fracao_media_olhando`).
- **Na GV3:** 168 de 216, e a fração entre 0,043 e 0,061.

## 3. A tabela, análise principal (216 vidas, 36 pets por célula), lado a lado com a GV3

`analise.json`, `principal.celulas`, nas duas pastas. Nenhuma medida ficou sem variância em nenhuma célula.

| genoma × dono | GV3b escolha | GV3b tempo relativo | GV3b tempo total | GV3 escolha | GV3 tempo relativo | GV3 tempo total |
|---|---|---|---|---|---|---|
| próprio × nenhum | 0,488 | 0,488 | 0,115 | 0,497 | 0,502 | 0,205 |
| próprio × calmo | 0,469 | 0,479 | 0,117 | 0,511 | 0,507 | 0,211 |
| próprio × agitado | 0,491 | 0,499 | 0,115 | 0,518 | 0,509 | 0,209 |
| vazio × nenhum | 0,502 | 0,510 | 0,116 | 0,513 | 0,520 | 0,219 |
| vazio × calmo | 0,482 | 0,498 | 0,115 | 0,483 | 0,494 | 0,253 |
| vazio × agitado | 0,492 | 0,520 | 0,119 | 0,531 | 0,526 | 0,248 |

### 3.1 A parte do genoma: Spearman(Δ_I, medida) nos genomas próprios, IC95 do bootstrap por unidade (2000, 0 indefinidas)

O Δ_I dos 108 pets de genoma próprio vai de −444 a 620, com 39 positivos; no vazio, Δ_I = 0 em todos (`contas_resultado.json`).

| dono | GV3b escolha | GV3b tempo relativo | GV3 tempo relativo |
|---|---|---|---|
| nenhum | −0,053 [−0,384; 0,283] | 0,309 [−0,045; 0,559] | 0,244 [−0,085; 0,555] |
| calmo | −0,120 [−0,479; 0,234] | 0,042 [−0,356; 0,389] | 0,137 [−0,195; 0,436] |
| agitado | −0,159 [−0,482; 0,164] | 0,154 [−0,199; 0,484] | 0,231 [−0,098; 0,530] |

**Na GV3b, a parte do genoma não aparece com 36 unidades** em nenhum dono e em nenhuma das duas medidas: todo IC95 contém 0. Na GV3, também
não aparecia.

### 3.2 A parte do dono: diferenças dentro da unidade, média sobre 36 unidades, IC95

| genoma | diferença | GV3b escolha | GV3b tempo relativo | GV3 tempo relativo |
|---|---|---|---|---|
| próprio | calmo − agitado | −0,022 [−0,065; 0,018] | −0,020 [−0,047; 0,006] | −0,002 [−0,026; 0,023] |
| próprio | calmo − nenhum | −0,019 [−0,059; 0,023] | −0,010 [−0,036; 0,019] | 0,005 [−0,028; 0,039] |
| próprio | agitado − nenhum | 0,003 [−0,043; 0,046] | 0,010 [−0,024; 0,044] | 0,008 [−0,031; 0,044] |
| vazio | calmo − agitado | −0,010 [−0,047; 0,029] | −0,022 [−0,056; 0,010] | −0,032 [−0,066; 0,006] |
| vazio | calmo − nenhum | −0,020 [−0,051; 0,013] | −0,012 [−0,045; 0,021] | −0,026 [−0,062; 0,008] |
| vazio | agitado − nenhum | −0,010 [−0,046; 0,026] | 0,010 [−0,021; 0,039] | 0,006 [−0,021; 0,034] |

**Na GV3b, a parte do dono não aparece com 36 unidades** em nenhum genoma: todo IC95 contém 0. Na GV3, também não aparecia.
- **O sinal de `calmo − agitado`:** no tempo relativo, os pontos ficam negativos nos dois genomas (−0,020 e −0,022), o lado que a E3b
  escreveu antes como possível.
- **O IC95 contém 0** nos dois (o próprio passa de 0 em 0,006, o vazio em 0,010). Pela regra, a frase é "não aparece", não "o contrário do
  esperado", e a E3b não é citada como explicação de um efeito que não aparece.

### 3.3 A interação, a divergência e a repetibilidade

- **A interação** (`principal.interacao`): na GV3b, a escolha −0,012 [−0,068; 0,044] e o tempo relativo 0,002 [−0,037; 0,046]. **Não
  aparece com 36 unidades.** Na GV3: 0,041 [−0,025; 0,106] e 0,029 [−0,011; 0,070], também não aparecia.
- **A divergência** (`principal.divergencia`): na GV3b, 51 de 216 pets com a escolha e o tempo relativo de lados opostos de 0,5, e o
  Spearman entre as duas medidas por pet é 0,719. Na GV3: 45 de 216 e 0,750.
- **A repetibilidade** (`principal.repetibilidade`, o ICC(1) das médias por dia, só o ponto): próprio 0,009 na escolha e 0,001 no tempo
  relativo; vazio 0,033 e 0,022. Na GV3: 0,0, 0,0, 0,044 e 0,031. Nas duas, quase nada da variação entre os dias é do pet.

### 3.4 A parte da exposição no agrado do cérebro (descritivo; GV3B-8: o agrado sem o tédio)

Δ_agora − Δ_I, a média por célula (`contas_resultado.json`, `exposicao_delta_agora_menos_delta_inato`):

| genoma | nenhum | calmo | agitado |
|---|---|---|---|
| próprio | −7,4 | 8,2 | −18,7 |
| vazio | 8,7 | 30,3 | −18,8 |

O sinal acompanha o dono no vazio (o `calmo` para o lado de A, o `agitado` para o lado de B), como na GV3, onde as médias do vazio eram
67,2 e −85,5 (`artifacts_v3_gosto_visual/gosto_visual/contas_resultado.json`). Como a E3 escreveu, aqui elas são menores; isso é só lado a
lado, sem teste. O comportamento na sonda não acompanha o deslocamento (a seção 3.2).

## 4. A análise "só estáveis" (213 vidas)

`analise.json`, `so_estaveis`: a mesma leitura. Todo IC95 da parte do genoma, da parte do dono e da interação contém 0.
- **A parte do genoma:** o Spearman com o tempo relativo é 0,309 [−0,045; 0,559] (nenhum), 0,042 [−0,356; 0,389] (calmo) e 0,147
  [−0,213; 0,485] (agitado).
- **A parte do dono:** `calmo − agitado` no tempo relativo é −0,016 [−0,043; 0,010] no próprio e −0,022 [−0,056; 0,010] no vazio.
- **A divergência:** 50 de 213 pets; o Spearman é 0,722.
- **As células:** a escolha fica entre 0,469 e 0,501, o tempo relativo entre 0,479 e 0,520, e o tempo total entre 0,114 e 0,119.

## 5. A leitura

- **O que a run mostra.** Com o enjoo ligado, nem a parte do genoma, nem a parte do dono, nem a interação aparecem com 36 unidades, nas
  duas medidas e nas duas análises. Isto é o resultado negativo, registrado como está. Ele não diz que o genoma ou o dono "não têm
  efeito": diz que, neste cérebro, com o enjoo e nesta sonda, com 36 unidades, o efeito não se separa do ruído.
- **Lado a lado com a GV3:** nas duas runs, todas as frases da regra são "não aparece com 36 unidades". Nenhuma diferença entre as duas
  tabelas é atribuída ao enjoo (adendo 1, seção 7).
- **E1 (a escolha perto de 0,5):** confere. As seis células ficam entre 0,469 e 0,502.
- **E2 (o tempo relativo acompanha Δ_I no genoma próprio):** não se vê. Os pontos do Spearman são positivos (0,042 a 0,309), mas todo IC95
  contém 0.
- **E3 (a parte do dono menor que a do genoma):** não se pode conferir, porque nenhuma das duas aparece.
  - O deslocamento do agrado do cérebro pelo dono, no vazio, fica menor que o da GV3 no lado a lado (seção 3.4).
- **E3b (a parte do dono com o sinal trocado):** os pontos de `calmo − agitado` no tempo relativo são negativos nos dois genomas, mas o IC95
  contém 0, então a frase é "não aparece".
- **E4 (menos tempo na TV, descritiva):** confere no lado a lado.
  - O tempo total na sonda fica entre 0,115 e 0,119 na GV3b, contra 0,205 a 0,253 na GV3 (seção 3).
  - A fração olhando a TV da vida fica entre 0,024 e 0,026, contra 0,043 a 0,061 (seção 2).
  - As runs têm unidades diferentes e não há teste de diferença entre elas; o número não diz quanto disso é do enjoo.
- **Os efeitos que ficam na sonda e não vêm do gosto (adendo 1, seção 2; GV3B-3):**
  - o **estresse de B**: o volume e o movimento de B (0,8 C) passam do corte do estresse (0,75 C);
  - o **salto de volume de A para B**: passar de A (C/5) para B (4C/5) sobe o volume em mais que C/2 e dá susto; de B para A, não.

  Os dois valem para todo pet, inclusive o vazio (Δ_I = 0).
  - **Toda diferença entre A e B nesta run é lida com eles.** O desvio de 0,5 numa célula (por exemplo o tempo relativo 0,479 no próprio ×
    calmo, ou 0,520 no vazio × agitado) pode vir desses efeitos, do sorteio ou da exposição. A run não os separa, e este documento não
    atribui nenhuma dessas diferenças ao gosto.
  - A run não mede o sentido de cada efeito sobre o olhar.
- **O custo:** a run custou 30,6 s por vida, e o piloto, 139,0 s. A run da GV3 custou 23,5 s. O piloto rodou logo depois de uma medição do
  combate e com outras cargas leves na máquina (um `tsc`), e a diferença entre o piloto e a run não foi investigada.

## 6. O negativo

Registrado como está:
- a parte do genoma, a parte do dono e a interação não aparecem com 36 unidades, nas duas medidas e nas duas análises, como na GV3;
- a repetibilidade fica perto de 0.

Não houve réplica sem lugar, medida sem variância, familiarização que não estabilizou, nem pet que quase não olhou: a fração das réplicas
com uma olhada foi 0,932.
