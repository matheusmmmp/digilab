# RESULTADO V3 — AÇÕES NOVAS: a run única da AN4, com o passeio ligado e desligado (2026-11-05, worker do resultado, Claude Code, Opus 5.5, branch `v3-acoes-novas-an4-resultado`)

**A leitura é a linha 2 da seção 7.4 do plano.** As premissas passam e a guarda G-COMEDOURO-AN **falha**, com a classe "< 0". Nestas
condições, **o passeio tira o pet do comedouro.** Por isso a subchave `passeio` fica desligada e a AN5 (o porte ao jogo) não roda. O MOV
sobe (+0,024, com o limite inferior do IC95 acima de 0), mas o MOV não é gate e não muda a linha. O resultado negativo fica registrado
como está, sem nenhum ajuste, e a run não se repete.

- **O plano:** `docs/PLANO_ANALISE_V3_ACOES_NOVAS.md`, APROVADO pelo Matheus em 2026-11-05, com o registro da run na seção 14.
- **A tarefa:** `docs/TAREFA_V3_ACOES_NOVAS.md`.
- **Os artefatos:** ficam em `artifacts_v3_acoes_novas/run/`. Cada número abaixo traz o caminho do campo no `resultado.json`, salvo onde
  outro arquivo é indicado.

## 1. A run

- **O comando** foi o do registro (o plano, seção 14):
  `python experiments/run_v3_acoes_novas.py --config experiments/configs/v3_acoes_novas/acoes_novas.json --processos 4`.
  - A run saiu da `main` em `cff554fd` (o merge do #581), com a árvore limpa: `git_head` e `git_limpo` = true no `meta.json`.
  - Usou 4 processos e Python 3.13.0.
- **As vidas:** 200 unidades da faixa 78101…78505 (5 bases × K = 40) × 2 braços × 8 células, 14 dias e orçamento de 16: **3 200 vidas**.
  - A run foi das 15h59 às 17h38 de 2026-11-05: 5 931 s de parede nas vidas e 5 934 s com a análise, cerca de 1 h 39 min (`meta.json`,
    `inicio`, `fim`, `vidas_parede_s`, `duracao_s`). O processo saiu com 0 (`run.log`, a última linha).
  - O CPU por vida foi de 4,32 s no LAB e 4,38 s no LAB+P (`meta.json`, `custo`). O tempo real passou da estimativa do plano, de 45 min
    a 1 h 15 min (o desvio D-AN4R-3).
- **As conferências da run** falham alto e rodaram em cada vida (o plano, seção 11; o orquestrador do #581):
  - o replay bit a bit do disco (o G1), o T-CENARIO-1, o G-MECANISMO com a conferência do crédito e a `conferir_memoria` da C4;
  - os fins conhecidos de cada braço. Saíram só os conhecidos: no LAB+P, os do LAB mais o `interrompido` (`meta.json`, `fins_conhecidos`;
    `descritivo.outros.fins_somados`);
  - no LAB+P: a urgência no limiar ou abaixo em toda decisão que continua um passeio, o alvo no ponto do passeio e o `interrompido` sem
    subir o F;
  - no LAB: nenhum passeio.
- **A conferência depois da run,** feita neste PR sem nenhuma vida:
  - os sha256 do `medidas.json` e do `resultado.json` são os do `meta.json` (`artefatos_sha256`);
  - os sha256 do código na árvore são os do registro (`meta.json`, `sha256`; a seção 14 do plano);
  - a análise refeita a partir do `medidas.json` gravado (`analisar`, sem mudança) sai igual ao `resultado.json`, byte a byte;
  - uma conta da guarda feita fora do orquestrador, direto nas taxas por vida, dá a mesma média (−0,02630) e o mesmo t (−5,22) sobre as
    mesmas 200 unidades;
  - nenhuma taxa por episódio deu `None`, e há 1 600 vidas por braço;
  - o `vidas.tar.gz` tem as 3 200 vidas.
- **Os artefatos,** em `artifacts_v3_acoes_novas/run/`:
  - o `meta.json` (sha256 `5cd9401c…dac3`), com o sha256 da config (`452de2ad…503a`), do orquestrador (`5aa5b836…5278`), do plano
    (`9133b0ed…2790`) e dos módulos;
  - o `medidas.json` (sha256 `9f992e9c…96f5`, 29,8 MB, no git sem compressão porque fica abaixo dos 100 MB da seção 5 do plano) e o
    `resultado.json` (sha256 `70b7fc96…1a16`), os mesmos do `meta.json`;
  - o `run.log`, a saída da run em LF (sha256 `bde44a87…97b0`): o resumo ASCII do orquestrador e a linha `saida=0`;
  - o `vidas.tar.gz` com as 3 200 vidas (sha256 `3fe40da4…dccd`, 14,5 MB).
  - As vidas soltas (`vidas/`) ficam fora do git.

## 2. As premissas (7.1): passam as duas

| premissa | a medida | o valor | IC95 (t, 200 unidades) | o limiar | passa | onde |
|---|---|---|---|---|---|---|
| **P-PASSEIO** | no LAB+P, nas 4 células do comedouro: a fração das decisões fora do dormir que continuam um passeio | **0,0836** | [0,0823; 0,0849] | limite inferior > 0,01 | **sim** | `premissas.P-PASSEIO` |
| **G-ELEGIVEL-EP** | a fração das vidas do comedouro com 3 episódios ou mais | LAB **1,000** (800 vidas); LAB+P **0,999** (800) | — | ≥ 0,80 nos dois | **sim** | `premissas.G-ELEGIVEL-EP` |

O resultado é **conclusivo** (`premissas.conclusivo` = true). O passeio durou perto da ração, em cerca de 8 % das decisões fora do dormir, e
os donos deram episódios de sobra: 17,2 por vida no comedouro, nos dois braços (`descritivo.longe.episodios_fome_por_vida`).

## 3. A guarda G-COMEDOURO-AN (7.2), o único gate: falha

O contraste é LAB+P − LAB na taxa de fechamento por episódio de fome, nas 4 células do comedouro, sobre 200 unidades (`guarda`).

| a medida | o valor |
|---|---|
| a média | **−0,0263** |
| o IC95 pelo t | **[−0,0362; −0,0164]** (199 gl; t = −5,22) |
| o p unilateral da hipótese "> 0" | 0,9999998 |
| o g1 das diferenças | −0,09 (acima de −0,5, então sem a ressalva da A4.4.6) |
| o IC percentil do bootstrap (a convenção da seção 5.2.1, anticonservadora com 5 bases) | IC95 [−0,0350; −0,0176]; IC90 [−0,0336; −0,0192] |
| a margem δ | 0,018 |
| a margem efetiva (o menor efeito com poder 0,8 pelo dp observado, 0,0712) | 0,0142 |
| **a classe de A6.6** | **"< 0"**: o limite superior fica abaixo de 0, e o IC não cabe inteiro em (−0,018; +0,018) |
| **falha** | **sim** (`guarda.falha` = true) |

- **Nos níveis** (`descritivo.longe.episodio.niveis`), o LAB fecha 0,881 [0,874; 0,888] dos episódios no comedouro, e o LAB+P fecha
  0,855 [0,847; 0,862]. São cerca de 2,6 pontos a menos.
- **Por dono, no comedouro** (`descritivo.outros.por_dono`, só a média), a taxa cai em todos:

  | dono | LAB | LAB+P |
  |---|---|---|
  | atencioso | 0,890 | 0,864 |
  | relapso | 0,850 | 0,827 |
  | aleatório | 0,894 | 0,864 |

  O incoerente no comedouro é a célula repetida do atencioso (a seção 2 do plano).
- **O tamanho:** a estimativa (2,6 pontos) passa da margem de 1,8 ponto, mas o IC vai de 1,6 a 3,6 pontos. O dano verdadeiro pode, então,
  ficar um pouco abaixo da margem. A classe é "< 0" pela regra de A6.6, que exige o IC fora de (−δ, +δ), e não o IC inteiro abaixo de −δ.
  Isso fica registrado como está.
- **O dp observado** (0,0712) ficou abaixo do σ de planejamento (0,0915) e perto do maior dp da C4 (0,0763). A run, portanto, detecta um
  dano menor que o planejado: a margem efetiva é 0,0142.

## 4. O movimento MOV (7.3): o passeio move o pet

O contraste é LAB+P − LAB na fração das decisões fora do dormir que saem do lugar, nas 8 células, sobre 200 unidades (`movimento`).

| a medida | o valor |
|---|---|
| a média | **+0,0236** |
| o IC95 pelo t | **[+0,0203; +0,0269]** (t = 14,15) |
| o g1 | 0,27 |
| o IC percentil do bootstrap (rotulado como na A4.4) | [+0,0227; +0,0246] |
| "o passeio move o pet" (o limite inferior acima de 0) | **sim** (`movimento.move` = true) |

- O nulo plausível escrito antes (seção 1 do plano) não aconteceu. O explorar ganhou decisões (+11,9 por vida no comedouro) que antes eram
  de ficar parado: o ocioso caiu 4,6 por vida e o chamar atenção caiu 13,0 (a seção 5 abaixo).
- **Por lugar** (`descritivo.movimento.mov`; a classe sai só como descrição):

  | lugar | LAB | LAB+P | o contraste [IC95] |
  |---|---|---|---|
  | comedouro | 0,641 | 0,668 | +0,0270 [+0,0241; +0,0298] |
  | `longe_fixo` | 0,549 | 0,569 | +0,0203 [+0,0139; +0,0267] |

- **A distância por dia** (`descritivo.movimento.distancia_por_dia`):
  - comedouro: de 1 886 para 1 908 unidades de posição, +21,4 [+14,2; +28,6];
  - `longe_fixo`: de 1 613 para 1 633, +19,9 [−0,2; +40,0], "indeterminado".

## 5. O descritivo (seção 8 do plano; não muda a linha)

**1. A secundária LONGE-AN** (`descritivo.longe.LONGE-AN`; sem previsão de sinal e sem gate):

| a medida | o valor |
|---|---|
| o contraste LAB+P − LAB na taxa por episódio, no `longe_fixo` | −0,0169 [−0,0340; +0,0001], t = −1,96 |
| a classe | "indeterminado" |
| a margem efetiva | 0,0243 (o dp observado é 0,122) |
| os níveis | LAB 0,581 [0,565; 0,597]; LAB+P 0,564 [0,549; 0,579] |
| os episódios de fome por vida | LAB 13,2; LAB+P 13,8 |

O sinal vai no mesmo sentido do comedouro, mas a run não separa esse custo de 0.

**2. O zigue-zague** (`descritivo.movimento.zigue_zague`): só em nível, somado sobre as vidas, nas corridas de `explorar` de 2 decisões ou
mais (a ação, não só o vagar; o D-AN4-3).

| lugar | braço | líquido / caminho | os pares de passos que invertem o anterior |
|---|---|---|---|
| comedouro | LAB | 0,474 | 0,524 (58 833 de 112 194) |
| comedouro | LAB+P | **0,615** | **0,329** (42 233 de 128 396) |
| `longe_fixo` | LAB | 0,544 | 0,475 (35 019 de 73 710) |
| `longe_fixo` | LAB+P | **0,699** | **0,262** (23 991 de 91 650) |

Com o passeio, o explorar anda mais reto e inverte menos o passo anterior. Isso é a "forma legível" da pergunta, sem limiar e sem contraste
(a LP-2). A escala da AN0 (0,49 e 50,5 %) é a das corridas de vagar pela escolha, numa base diferente (o D-AN4-3).

**3. O passeio** (só no LAB+P; `descritivo.passeio`):

| a medida | comedouro | `longe_fixo` |
|---|---|---|
| os passeios por dia (`por_dia`) | 7,85 [7,76; 7,94] | 5,68 [5,49; 5,87] |
| a duração média em decisões, média das vidas (`duracao_media_por_vida`) | 1,55 | 1,64 |
| os passeios abertos e acabados (`somados`) | 87 889 / 87 842 | 63 592 / 63 566 |
| as decisões que continuam um passeio (`somados`) | 47 380 | 39 460 |
| os fins (`fins_somados`) | `meta` 42 454 (48 %); `interrompido` 29 511 (34 %); `trocou` 15 877 (18 %); `desistiu` 0 | `meta` 37 484 (59 %); `interrompido` 13 618 (21 %); `trocou` 12 464 (20 %); `desistiu` 0 |
| a P-PASSEIO (`p_passeio`) | 0,0836 [0,0823; 0,0849] | 0,0675 [0,0651; 0,0699] |
| a urgência máxima nas aberturas | 512, o limiar, por construção (o D-AN4-2) | 512 |
| o crédito descartado pelo gesto | 0 | 0 |

O crédito descartado saiu 0, como o plano previa (4.4): nenhum gesto do dono (carinho, elogio, tapa, repreender) caiu no intervalo de um
passeio, e o teste da AN2 é que fecha a conferência da 3.3. **Um passeio em três, no comedouro, acaba `interrompido`,** ou seja, uma necessidade passou do limiar no meio
dele.

**4. O corpo** (`descritivo.corpo`; as classes saem só como descrição, porque a margem foi feita para a taxa por episódio): LAB+P − LAB.

| medida | comedouro | `longe_fixo` |
|---|---|---|
| a privação de hoje (`privacao_de_hoje`) | +0,0056 [+0,0004; +0,0109], "≈ 0 +" | +0,0088 [−0,0138; +0,0313], "indeterminado" |
| a menor necessidade, média nos dias 8 a 14 (`dias_8_14\|menor_media`) | **−0,0161 [−0,0185; −0,0138], "< 0"** | **−0,0118 [−0,0212; −0,0024], "< 0"** |
| a menor necessidade, mínimo nos dias 8 a 14 (`dias_8_14\|menor_minimo`) | −0,0083 [−0,0151; −0,0016], "≈ 0 −" | −0,0121 [−0,0173; −0,0069], "≈ 0 −" |
| a fração dos ticks fora, dias 8 a 14 (`dias_8_14\|fracao_fora`) | +0,0053 [−0,0001; +0,0108], "≈ 0" | +0,0094 [−0,0140; +0,0327], "indeterminado" |
| a menor necessidade, média na vida (`vida\|menor_media`) | −0,0142 [−0,0156; −0,0128], "≈ 0 −" | −0,0072 [−0,0150; +0,0007], "≈ 0" |
| a exaustão (`exaustao`) | +0,0218 [+0,0190; +0,0245], "> 0" | +0,0057 [−0,0035; +0,0148], "≈ 0" |

Em tudo o que tem sinal, o corpo vai no sentido de "pior": a menor necessidade cai e a privação e a exaustão sobem. Os "< 0" da menor
necessidade média nos dias 8 a 14 voltam ao Matheus como dado, ao lado da linha (7.4), e não como gate.

**5. Os outros** (`descritivo.outros`):

- **As ações por vida, LAB+P − LAB** (`acoes_por_tipo`):

  | ação | comedouro | `longe_fixo` |
  |---|---|---|
  | `explorar` | +11,9 [+10,4; +13,4] | +11,1 |
  | `dormir` | +6,0 | +3,1 |
  | `comer` | +1,4 [+0,7; +2,0] | +1,8 |
  | `ocioso` | −4,6 | −3,2 |
  | `chamar_atencao` | −13,0 | −11,6 |
  | `brincar` | −1,3 | −1,2 |
  | `emburrar` | "indeterminado" | "indeterminado" |

- **A fração das decisões `explorar`** (`exploracao`): +0,0088 no comedouro e +0,0083 no `longe_fixo`, "≈ 0 +" nos dois.
- **A G-PESA da persistência** (`g_pesa_por_modulo.persistencia`, no comedouro) sobe de 0,0025 no LAB para 0,0206 no LAB+P. A do afeto cai
  de 0,018 para 0,014. A do aprendido sobe de 0,207 para 0,228.
- **Os fins das intenções** (`fins_somados`) somam, no comedouro:
  - LAB: `meta` 81 758, `trocou` 16 040, `achou` 6 035;
  - LAB+P: `meta` 121 105, `trocou` 34 494, `interrompido` 29 511, `achou` 6 654.

## 6. A regra de leitura (7.4)

| ordem | premissas | G-COMEDOURO-AN | MOV | serve? |
|---|---|---|---|---|
| 1 | passam | — | — | não: as premissas passam |
| **2** | **passam** | **"< 0"** | **qualquer (aqui, > 0)** | **sim** |

- **O que diria** (`leitura.o_que_diria`): "a guarda falha: nestas condições, o passeio tira o pet do comedouro".
- **O que se faz** (`leitura.o_que_se_faz`): fica registrado como está, a `passeio` fica desligada e a AN5 não roda
  (`leitura.an5_pode_rodar` = false).
- **O que vem ao lado**, sem mudar a linha:
  - o MOV sobe, e o zigue-zague diminui;
  - o LONGE-AN sai "indeterminado", com o sinal −;
  - no corpo, a menor necessidade média dos dias 8 a 14 sai "< 0" nos dois lugares.
- **A run não se repete,** e nada se ajusta olhando para ela. Uma faixa nova só vem com um adendo novo (7.4).

## 7. O que o resultado não demonstra (`nao_demonstra`)

- o apego do jogador, que não se mede no Python;
- que o pet "parece passear" ao jogador (SEM FONTE; isso cabe ao Matheus, jogando);
- que o modular supera o A;
- um tamanho de efeito fora das condições da run: o cenário da C4, os 4 donos sem ensino, 14 dias, orçamento de 16, o comedouro e o
  `longe_fixo`, o `urgencia_lambda` de S/2 e os inatos do #428;
- qualquer novidade.

Também **não demonstra o porquê** do custo. A run mede o contraste. Ela não diz se o pet perde o episódio por estar longe quando a
fome aperta, por perder tempo no caminho ou por outra razão. A pergunta aberta abaixo trata disso, sem rodar nada.

## 8. A pergunta aberta para o Matheus (fora do plano; nada rodado)

**O que fazer com o passeio depois do negativo?** O dado ao lado é este:
- um passeio em três, no comedouro, acaba `interrompido` (seção 5, item 3);
- a abertura já exige a urgência no limiar ou abaixo (o D-AN4-2);
- o pet com o passeio come mais vezes (+1,4 decisões de `comer` por vida), mas fecha menos episódios.

Daí sai uma leitura [HIPÓTESE, SEM FONTE, não medida]: **o passeio leva o pet a 4 a 12 células do comedouro, e, quando a fome passa do
limiar, a guarda corta a persistência, mas não traz o pet de volta.** O episódio vence no caminho de volta. Seria um custo da distância, e
não da persistência.

| opção | o que é | custo de errar |
|---|---|---|
| **(a) fechar a frente como negativa** (a recomendada) | a `passeio` fica desligada; a "Vida do pet" segue pelo passo 2 (a cena, só vista); o ganho do MOV e do zigue-zague fica registrado como dado para um desenho futuro | perder, por ora, o que o produto pediu (+2,4 pontos no MOV e um andar mais reto, a seção 4) e manter o pet de hoje no jogo |
| (b) uma tarefa nova com outro desenho de passeio (por exemplo, um destino limitado perto da necessidade, ou um limiar de abertura mais baixo) | um papel novo (AN-x), um plano novo, uma faixa nova e uma run nova; o `urgencia_lambda` e o raio do vagar são números PROPOSTOS, que a rodada de equilíbrio do fim calibraria | escolher o desenho novo olhando esta run é ajustar pela validação (a regra do CLAUDE.md): só vale como hipótese nova com um plano próprio, nunca como "conserto" desta; mais uma run na fila da máquina (V3-D8), e o achado pode depender do cenário de 14 dias sem ensino |

**Recomendação: (a).** A calibração do `urgencia_lambda` e do raio do vagar fica para a rodada de equilíbrio, no fim (a regra
"Calibração no fim"). Um desenho novo do passeio, se o Matheus quiser, entra como tarefa própria depois dela, e não como repetição desta
run.
