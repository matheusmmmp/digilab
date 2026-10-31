# Resultado — V2: a avaliação única do DigiBrain modular (o protótipo, etapa 1)

Data: 2026-10-26. Plano: `docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, seções 5 a 8 e adendos 1 e 2 (com as decisões do Matheus
no fim do adendo 2). Tarefa: `docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`. Executor: worker D, Claude Code, Opus 5.5.

## Antes dos números

As notas que o Matheus pediu explícitas (2026-10-26):
- **A calibração não atingiu os critérios de fechamento.** Os valores da rodada 3 são a melhor rodada disponível, não uma calibração
  bem-sucedida (adendo 1).
- **O G-MVP podia falhar,** e falhou. No piloto, a fração já tinha ficado em 0,5.
- **O G-ABLA-PERS é inconclusivo por premissa se a G-PESA da persistência falhar,** e ela falhou.
- **Nada disto declara o produto pronto** (seção 5.6). O G-MVP é necessário e não suficiente. O gate de compatibilidade do produto (o
  G-PAR, o G-CUSTO e o E2E-COMIDA na web) é outro.

**A queda da primeira tentativa** está no registro, na seção "2026-10-26 — DIGIBRAIN-MODULAR-AVALIACAO, a queda da primeira run"
(`docs/registro/2026-10.md`).
- A primeira run, com 16 processos, caiu depois de 336 vidas, com `BrokenProcessPool`. Nenhuma medida foi calculada nem lida.
- O Matheus autorizou rodar de novo uma vez, com 8 processos, guardando a pasta da queda.
- As 336 vidas da queda são byte a byte as da run nova
  (`artifacts_v2_digibrain_prototipo/avaliacao/conferencia_queda_1.json`: 336 de 336 iguais).

## Como rodou

**Fonte dos números:** `artifacts_v2_digibrain_prototipo/avaliacao/`. As vidas ficam fora do git.

| arquivo | o que traz |
|---|---|
| `resultado.json` | os gates, as premissas, a comparação com o A11, o D-1, o D-2, os descritivos, a leitura com 11 células e o custo |
| `medidas.json` | uma linha por vida |
| `meta.json` | o commit, a árvore limpa, as sementes, os valores, o K e o g_apr do adendo 2, os sha256 |
| `relato.json` | os descritivos da seção 8 que o resultado não grava inteiros: as curvas por dia do D-2, a cadeia por célula e as PE. Sai de `experiments/relato_avaliacao_digibrain.py`, que só lê os artefatos |

- **O comando, uma vez:** `python experiments/run_v2_digibrain_prototipo.py --config experiments/configs/v2_digibrain_prototipo/avaliacao.json --processos 8`.
- **A fronteira:** o commit `5fc8943`, no remoto antes da primeira vida. Ele traz a config, a leitura com 11 células e o teste dela. A
  run rodou nesse commit, com a árvore limpa (`git_limpo` no meta), das 10:12:31 às 10:42:53 (1 822 s de parede), em Python 3.13.0.
- **As sementes:** as bases 64101, 64202, 64303, 64404 e 64505, com K = 10 e o prefixo `digibrain_prototipo`. São 50 unidades, os 9
  braços e as 12 células: **5 400 vidas de 14 dias.**
- **Os valores:**
  - os do `config.py` (a rodada 3);
  - o K = 10 e o g_apr do M4-con = 1 919, lidos do piloto pelo `adendo_do_piloto()` (`meta.json`, campo `adendo_2`).
- **As conferências, em toda vida:** o replay do disco, bit a bit (G1), e as falhas altas de cada braço. Antes da run passaram o G2 (as
  196 vidas e o MVP), o G1, o G-MECANISMO e os T-PONTO-1 a 3 (59 testes).
- **Nada foi ajustado** olhando para a faixa.

## Resumo

**A leitura da seção 5.5:** o G-MECANISMO passa, e o G-MVP falha. **"Com o oráculo (o T-CADEIA-1) passando, a aprendizagem não chega
lá: falha de implementação ou de calibração (D4), não da arquitetura."**
- Da família G-ABLA, dois passam: a memória e o incentivo.
- O hábito não passa (o sinal é o contrário do previsto).
- A persistência é inconclusiva por premissa.
- Nenhum G-MOD passa.

| gate | contraste (por unidade; positivo = a direção da espec) | média | IC95 | p unilateral | regra | veredito |
|---|---|---|---|---|---|---|
| **G-MVP** (primário) | a fração de vidas do M3 com a taxa de fechamento ≥ 0,5 | **0,485** | [0,475; 0,495] | — | limite inferior ≥ 0,8 | **falha** |
| G-ELEGIVEL (premissa) | as vidas do M3 com 3 rações elegíveis ou mais | 1,0 (600 de 600) | — | — | ≥ 0,8 | passa |
| G-ABLA-MEM (Holm, posto 1) | taxa de fechamento(M3) − (M2), no comedouro | 0,150 | [0,131; 0,169] | < 0,0001 | p ≤ 0,0125 | **passa** |
| G-ABLA-P1 (Holm, posto 2) | `falta_ao_comer`(M0) − (M1) | 0,045 | [0,039; 0,050] | < 0,0001 | p ≤ 0,0167 | **passa** |
| G-ABLA-PERS (Holm, posto 3) | `intencoes_com_meta`(M3) − (M3-sp) | 0,006 | [−0,002; 0,015] | 0,0765 | p ≤ 0,025 | **inconclusivo por premissa** (e o Holm não rejeita) |
| G-ABLA-P2 (Holm, posto 4) | `repeticao_apos_alivio`(M2) − (M1) | −0,011 | [−0,016; −0,008] | 1,0 | — | **não passa** |
| G-MOD-CON (Holm) | `D_FE`(M4-con) − (M4) | 0,003 | [−0,003; 0,008] | 0,158 | p ≤ 0,025 | não passa |
| G-MOD-EMB (Holm) | `D_FE`(M4-emb) − (M4) | −0,001 | [−0,005; 0,003] | 0,709 | — | não passa |

| premissa G-PESA | braço | média | IC95 | regra | veredito |
|---|---|---|---|---|---|
| o incentivo | M1 | 0,0184 | [0,0178; 0,0190] | limite inferior > 0,01 | passa |
| o hábito | M2 | 0,1752 | [0,1697; 0,1806] | idem | passa |
| a memória | M3 | 0,1231 | [0,1184; 0,1274] | idem | passa |
| a persistência | M3 | 0,0014 | [0,0012; 0,0015] | idem | **falha** |

- **O Holm** (α 0,05; `resultado.json`, `G-ABLA.*.holm`):
  - a memória e o incentivo rejeitam;
  - a persistência (p 0,0765, contra o limiar 0,025 do posto 3) não rejeita, e o Holm para ali;
  - a leitura dela fica "inconclusivo por premissa" de qualquer jeito (seção 5.2.1, item 4).
- **O G-MVP é o mesmo padrão do piloto.** Fecham a cadeia o comedouro do aleatório e do relapso, e o perto dos quatro donos (de 0,94 a
  1,0 das vidas). O longe nunca fecha, nem o comedouro do atencioso e do incoerente (`relato.json`, `cadeia_por_celula.M3`).
- **O que isto diz e o que não diz:**
  - na pesquisa Python, com estes valores, o modular não fecha a cadeia comida → corpo em 80% das vidas;
  - a memória e o incentivo pesam no sentido previsto;
  - o hábito, medido pela repetição depois do alívio, vai ao contrário;
  - a persistência quase não decide.

  Não diz nada do produto (seção 5.6), e a nota da calibração vale para os três: o G-MVP, o P1 e o PERS.

## 1. A leitura com 11 células (descritiva, sem gate)

A decisão do Matheus: a análise principal é a das 12 células. Esta leitura tira a célula incoerente/comedouro, cuja vida é byte a byte
a do atencioso, e não decide nada (`resultado.json`, `descritivo_11_celulas`).

| medida | 12 células (principal) | 11 células | IC95 (11) |
|---|---|---|---|
| G-MVP, a fração | 0,485 | 0,529 | [0,518; 0,540] |
| G-ABLA-MEM (3 células do comedouro) | 0,150 | 0,182 | [0,160; 0,204] |
| G-ABLA-P1 | 0,045 | 0,043 | [0,037; 0,049] |
| G-ABLA-P2 | −0,011 | −0,013 | [−0,018; −0,009] |
| G-ABLA-PERS | 0,006 | 0,007 | [−0,002; 0,017] |
| G-MOD-CON | 0,003 | 0,002 | [−0,004; 0,006] |
| G-MOD-EMB | −0,001 | −0,002 | [−0,005; 0,002] |
| G-PESA da persistência (M3) | 0,0014 | 0,0014 | [0,0013; 0,0015] |
| G-ELEGIVEL | 1,0 | 1,0 (550 vidas) | — |

Nenhum sinal muda, e o G-MVP continua longe de 0,8. A duplicata pesa sobretudo no G-ABLA-MEM e na fração do G-MVP, porque o comedouro
do atencioso não fecha.

## 2. A comparação com o A (seção 7, descritiva; o D6)

Sem gate, sem Holm e sem margem (`resultado.json`, `comparacao_com_o_a`). O sinal é o da diferença: negativo no `D_FE` e na privação é o
modular melhor.

| medida | M3 − A11 | IC95 | M0 − A11 | IC95 |
|---|---|---|---|---|
| `D_FE` (dias 8 a 14) | −0,054 | [−0,061; −0,045] | −0,042 | [−0,047; −0,038] |
| privação | −0,518 | [−0,534; −0,498] | −0,498 | [−0,508; −0,487] |
| refeições por dia | 2,609 | [2,552; 2,658] | 1,736 | [1,710; 1,764] |
| taxa de fechamento | 0,393 | [0,387; 0,401] | 0,257 | [0,251; 0,264] |
| fração de vidas com a cadeia | 0,485 | [0,475; 0,495] | 0,197 | [0,185; 0,210] |

- **O A11 nunca fecha a cadeia** em vida nenhuma, e come 0,91 vez por dia (`relato.json`, `A11_refeicoes_por_dia`; os descritivos do
  `resultado.json`).
- **A referência do diagnóstico do MVP** (1 ou 2 refeições por vida em 2 dias) fica ao lado, só como ordem de grandeza. O dono, o motor
  e o horizonte são outros, e os dois não se comparam.
- **O inato modular sozinho** (o M0) já passa do A em todas as medidas. O D6 sozinho não é limitação nem mérito
  (`TAREFA_V2_CEREBRO_A_BASELINE`, seção 3).

## 3. As leituras descritivas (seção 8, sem gate)

**D-2, "memória cedo, hábito depois"** [HIPÓTESE; Lengyel e Dayan 2007] (`resultado.json`, `D-2`; as curvas em `relato.json`,
`D-2_curvas`):
- **A diferença** `centro_temporal`(hábito) − `centro_temporal`(memória) no M3 é 0,425, IC95 [0,302; 0,529]. É positiva, a ordem
  prevista.
- **Por lugar:**
  - o comedouro: 0,687 [0,508; 0,895];
  - o perto: 1,342 [0,784; 1,924];
  - o longe: −0,587 [−0,656; −0,514]. No longe a memória vem depois: ela sobe até o dia 14 (0,248), e o hábito tem o pico no dia 8 e
    cai.
- **As curvas no total** (a fração das decisões em que o módulo decidiu, por dia):
  - a memória sobe de 0,015 no dia 1 para 0,156 no dia 14;
  - o hábito sobe de 0,003 para 0,162 no dia 12 e fica em 0,147 no dia 14.

**D-1, se a excitação mexe mais na exploração que na taxa de aprendizado** [HIPÓTESE EXPERIMENTAL] (`resultado.json`, `D-1`). É o M4 − M4-con,
com o efeito padronizado pelo desvio padrão das unidades do M4-con:

| medida | bruto | efeito padronizado | IC95 (padronizado) |
|---|---|---|---|
| a fração de explorar | 0,001 | 0,134 | [−0,186; 0,460] |
| a entropia das ações por dia | −0,004 | −0,187 | [−0,523; 0,150] |
| \|Δd̂\| por consumo (o P1) | 0,324 | 0,094 | [−0,037; 0,233] |
| \|ΔH\| por consequência (o P2) | 0,222 | **1,433** | [1,164; 1,704] |

**A leitura:** a excitação **não** mexe mais na exploração. O que se move é a taxa do hábito (o P2), com o IC acima dos da exploração.
A ressalva do plano vale: no protótipo, a excitação age só pelo `g_apr`.

**As PE "no protótipo"** (`relato.json`, `PE`):

| PE | o que mostra |
|---|---|
| PE-6 (`N_desiste`) | as intenções acabam só por "meta" ou "trocou", em todo braço; nenhuma acabou por desistência. No M3: 48 667 por meta e 17 243 por troca, nas 600 vidas |
| PE-10 (o decaimento do H) | uma vida em 600 com H no teto, no M4 (`pesos_no_teto` médio 2,1 × 10⁻⁵); nenhuma nos outros braços |
| PE-16 (N_ep = 16) | no M3 saem 65,5 episódios por vida, 32,6 deles com r > 0; nos M4, de 69,6 a 71,0 |

**Os outros descritivos** (`resultado.json`, `descritivos`):

| braço | `D_FE` | privação | exaustão | refeições por dia |
|---|---|---|---|---|
| A11 | 0,644 | 0,819 | 0,024 | 0,91 |
| M0 | 0,602 | 0,321 | 0,201 | 2,65 |
| M1 | 0,589 | 0,309 | 0,193 | 2,85 |
| M2 | 0,589 | 0,308 | 0,205 | 3,54 |
| M3 | 0,590 | 0,301 | 0,230 | 3,52 |
| M3-sp | 0,592 | 0,305 | 0,231 | 3,50 |
| M4 | 0,590 | 0,292 | 0,223 | 3,85 |
| M4-con | 0,593 | 0,300 | 0,224 | 3,88 |
| M4-emb | 0,589 | 0,292 | 0,221 | 3,87 |

**As visitas ao lugar lembrado** (o T-MEM-4 na vida): no M3, foram 19 331 visitas, e a medida conta as 19 331 como vazias; nos outros
braços com memória, também todas. Leitura minha do código, sem gate: a visita é a decisão de explorar até o ponto, e o comer só vem numa
decisão seguinte (`digilab/digibrain/adapt.py`, a consequência). Por isso a medida `visitas_vazias` não separa a visita que achou comida
da que não achou. Isso fica registrado como achado; nada mudou.

> **Nota (2026-10-26, a implementação do adendo 3):** a correção desta medida é a DX-1 do adendo 3 do plano (A3.1). A medida de hoje fica
> com o nome `visitas_vazias_v1` nas runs novas, ao lado da corrigida. Os números acima e o `avaliacao/medidas.json` não mudam.

## 4. O custo em Python

Do `resultado.json`, `custo`: a CPU por vida, com a gravação, o replay e as conferências.
- **O modular:** de 2,41 s (M0) a 2,54 s (M3-sp).
- **O A11:** 2,08 s.
- **A avaliação inteira:** 1 822 s de parede em 8 processos.

## 5. O que fica para o Matheus

- **A leitura D4 do G-MVP:** pela seção 5.5, a falha vai à implementação ou à calibração, não à arquitetura.
  - As hipóteses que o registro da calibração e do piloto já levantou continuam as candidatas: o sono nas janelas da ração, o cheiro sem
    peso inato e a persistência que não decide.
  - O conserto, se houver, é da AF-3: uma rodada de diagnóstico e uma faixa nova. As 64101…64505 não voltam.
- **O G-ABLA-P2 ao contrário** e **a persistência sem peso** vão ao diagnóstico da fiação (D2).
- **As células iguais do comedouro** e **a medida das visitas vazias** ficam como achados.

O registro está na seção "2026-10-26 — DIGIBRAIN-MODULAR-AVALIACAO" de `docs/registro/2026-10.md`.

## 6. A calibração do conserto (2026-10-27, worker D, Claude Code, Opus 5.5; adendo 3, A3.11)

- **O que rodou:** só o M3\* (as duas subchaves do cheiro, o "achou" sem frustração do #426), nas bases 65101 e 65202, com K = 2, as 12
  células e 14 dias: 48 vidas por rodada, três rodadas (o máximo). Cada rodada foi registrada em A3.11, num commit empurrado antes da
  primeira vida. Nenhum outro braço e nenhuma outra base rodaram.
- **O critério não fechou.** A melhor rodada é a 3:
  - o fechamento por episódio do M3\*, a mediana das vidas: 0,8397 (≥ 0,5);
  - o teto do hábito: 0;
  - a G-PESA do incentivo 0,0149, do hábito 0,0758 e da memória 0,1117;
  - a G-PESA da persistência: **0,0027, abaixo de 0,01**.
- **Os valores da rodada 3** (PROPOSTOS; não escritos no `digilab/config.py`): `eta_h` S/256, `w_pers` 4S, `tau_c` 15, o peso do cheiro
  S/4 e o N_desiste_cheiro 6.
- **A persistência tem um teto estrutural.** O termo h só existe da segunda decisão de uma intenção em diante, cerca de 3% das decisões, e
  a ativação é cortada em A_max. Com as alavancas permitidas, ela não chega a 0,01.
- **Os números da calibração não são evidência** do G-MVP nem das ablações (a seção 6.1). Nada aqui afirma superioridade do modular.
- **Os artefatos** estão em `artifacts_v2_digibrain_prototipo/conserto/calibracao/rodada_<n>/`: o `meta.json`, o `medidas.json`, o
  `resultado.json` e o `diagnostico.json`. As vidas ficam fora do git, na worktree `v2-modular-calibracao-conserto`.
- **O que fica para o Matheus:** congelar (ou não) os valores da rodada 3, o que muda as vidas de todos os braços modulares e o gabarito
  G2, e o piloto do conserto (65303 a 65505), que não começou.
- **O congelamento (2026-10-27, autorizado pelo Matheus; A3.12):** os valores da rodada 3 (`eta_h` S/256, `w_pers` 4S, `tau_c` 15) passaram
  a ser os padrões do `digilab/config.py`, e o gabarito G2 do #425 foi regravado por eles num commit próprio. O merge do #427 não aprovou
  todos os critérios: a G-PESA da persistência falhou nas três rodadas, e a persistência segue como ablação inconclusiva por premissa
  (seção 5.3). O congelamento não muda isso.

## 7. O piloto do conserto (2026-10-27, worker D, Claude Code, Opus 5.5; adendo 3, A3.8 e A3.13)

**Antes dos números:**
- **é uma avaliação exploratória dos braços** (a autorização do Matheus em 2026-10-27). Pela seção 6.2, nenhum número do piloto é
  evidência, e o piloto não tem leitura de gate (A3.8). **Ele não prova superioridade do cérebro modular;**
- **a persistência:** o G-ABLA-PERS é **inconclusivo por premissa** (seção 5.3). A G-PESA dela falhou nas três rodadas do #427 e falha
  de novo aqui. O piloto não demonstra a contribuição da persistência;
- **os valores** são os calibrados do #428 (`eta_h` S/256, `w_pers` 4S, `tau_c` 15, o cheiro S/4 e 6), que seguem PROPOSTOS.

**Como rodou:** registrado em A3.13 antes da primeira vida, no commit `4adce20`, de onde a run saiu com a árvore limpa (o `meta.json`:
`git_head`, `git_limpo` = true e o sha256 da config `bdffc2af…4735`, o registrado).
- As bases 65303, 65404 e 65505, com K = 2 (6 unidades), os 12 braços nas 12 células, 14 dias e 8 processos: **864 vidas,** em 313 s de
  parede para as vidas e 375 s no total.
- Toda vida foi rejogada do disco bit a bit dentro da run (o G1).
- Nenhuma vida das faixas 64xxx, 65101/65202 ou 66xxx rodou.
- Os artefatos estão em `artifacts_v2_digibrain_prototipo/conserto/piloto/`: o `meta.json`, o `medidas.json` e o `resultado.json`. As
  vidas ficam fora do git, na worktree `v2-modular-piloto-conserto`. Todos os números abaixo saem do `resultado.json`, salvo o tempo e o
  M4-con (o `meta.json`).

**O efeito de cada contraste,** só como relato (positivo = a direção da espec; 6 unidades em 3 bases; o IC95 percentil do bootstrap
agrupado por base, 10 000 reamostragens, semente 4242; o p unilateral é descritivo):

| contraste | a medida | média | IC95 | p |
|---|---|---|---|---|
| G-ABLA-P1 | `falta_ao_comer`(M0) − (M1) | 0,0341 | [0,0105; 0,0553] | 0,0000 |
| G-ABLA-P2 | o índice de repetição (M2) − (M1) | −0,0120 | [−0,0264; −0,0048] | 1,0000 |
| G-ABLA-MEM | o fechamento (M3) − (M2), no comedouro | 0,1660 | [0,1208; 0,2137] | 0,0000 |
| G-ABLA-PERS | `intencoes_com_meta`(M3) − (M3-sp) | −0,0012 | [−0,0152; 0,0078] | 0,5923 |
| G-MOD-CON | `D_FE`(M4-con) − (M4) | −0,0054 | [−0,0099; 0,0007] | 0,9669 |
| G-MOD-EMB | `D_FE`(M4-emb) − (M4) | −0,0024 | [−0,0083; 0,0010] | 0,7015 |
| G-DX-INATO, longe | o fechamento por episódio (M3\*) − (M3\*−inato) | 0,0403 | [0,0082; 0,0687] | 0,0000 |
| G-DX-INTENCAO, longe | o fechamento por episódio (M3\*) − (M3\*−intencao) | 0,0227 | [−0,0482; 0,0739] | 0,2539 |
| G-DX-INATO, todas | idem, nas 12 células | 0,0227 | [0,0054; 0,0386] | 0,0000 |
| G-DX-INTENCAO, todas | idem, nas 12 células | 0,0080 | [−0,0262; 0,0290] | 0,2539 |

- **O G-ABLA-P2 e os dois G-MOD** saem com o sinal contrário ao previsto, como no piloto do #420. O G-ABLA-PERS também (−0,0012), e a
  leitura dele é a de premissa, acima.
- **O 2 × 2 do cheiro, no longe** (o fechamento por episódio, a média das unidades): M3\* 0,4564; M3\*−intencao 0,4336; M3\*−inato 0,4161;
  M3-420 0,3416. A interação é −0,0517 [−0,0924; 0,0110]. Nas 12 células: 0,7515, 0,7434, 0,7288 e 0,7041.

**O G-MVP** (sem gate; só o poder):
- **por episódio (a primária, A3.3):** a fração de vidas do M3\* com o fechamento ≥ 0,5 é **0,8056.** O valor de planejamento fica em
  0,8028;
- **por ração (a secundária obrigatória):** **0,4722.**

**As premissas** (seção 5.3; A3.3), só relatadas:

| premissa | braço | média | IC95 | o limiar |
|---|---|---|---|---|
| G-PESA, o incentivo | M1 | 0,0191 | [0,0173; 0,0215] | limite inferior > 0,01 |
| G-PESA, o hábito | M2 | 0,0805 | [0,0678; 0,0884] | idem |
| G-PESA, a memória | M3\* | 0,1219 | [0,1140; 0,1297] | idem |
| G-PESA, a persistência | M3\* | **0,0033** | [0,0029; 0,0039] | idem: **falha** |
| G-ELEGIVEL | M3\* | 1,0 (as 72 vidas) | — | ≥ 0,8 |
| G-ELEGIVEL-EP | M3\* | 1,0 (as 72 vidas) | — | ≥ 0,8 |

- **Quantos episódios as vidas têm:** no M3\*, a média é 16,8 e a mediana 15, com o mínimo 5. Em todos os braços modulares, todas as vidas
  têm 3 episódios ou mais.

**O K** (seção 6.3): **10, e o alvo não é alcançado.**
- Entram na conta o G-ABLA-P1 (efeito de planejamento 0,0171), o G-ABLA-MEM (0,0830) e o G-MVP por episódio (0,8028).
- O G-ABLA-P2, o G-ABLA-PERS e os dois G-MOD saem da conta, pelo sinal contrário.
- O P1 e o MEM já passam de 0,8 com K = 4 (0,968 e 0,994).
- **O G-MVP não chega:** o poder dele fica entre 0,105 e 0,126 de K = 4 a 10 (0,1085 com K = 10), porque a fração do piloto (0,8056) quase
  não passa do limiar. Pela seção 6.3, o K fica em 10, e o poder sai declarado.
- A G-DX fica fora do K: com K = 10, o poder é 0,417 (INATO) e 0,201 (INTENCAO).

**O valor do M4-con da reavaliação:** a média do `g_apr` das vidas M4 é 1 922,89, que arredonda para **1 923** (PROPOSTO).

**O custo:** de 2,05 a 2,19 s de CPU por vida nos braços modulares, e 1,78 s no A11. A reavaliação estimada, com K = 10 e os 12 braços (7 200
vidas), fica em 15 273 s de CPU.

**Os descritivos** (sem gate):
- **a comparação com o A11** (seção 7; a diferença bruta, M3\* − A11):
  - o fechamento por episódio: +0,2800 [0,2349; 0,3128];
  - a fração de vidas com a cadeia por episódio: +0,0694 [0,0000; 0,1667];
  - as refeições por dia: +2,3135;
  - a privação: −0,5783;
- **a DX-5** (A3.5, exploratória), M2 − M1, pelas ações com recompensa possível: −0,0298 [−0,0490; −0,0113] no total. No comer, +0,0552
  [0,0303; 0,0777]; no explorar, −0,0332 [−0,0556; −0,0170]. O brincar e o aliviar ficam sem valor (menos de 2 grupos). O índice de hoje
  é −0,0120;
- **as medidas de mecanismo do cheiro**, por braço e lugar, estão no `descritivos_conserto` do `resultado.json`.

**O que fica para o Matheus:** a leitura do piloto e o adendo 4 (A3.8), que traz para a reavaliação (66101 a 66505) o efeito, as
premissas, o M4-con, o K e o custo. Nada da reavaliação começou.

## 8. A reavaliação na 66xxx (2026-10-29, worker D, Claude Code, Opus 5.5; adendo 4, A4.10)

**Antes dos números** (a leitura do adendo 4, como foi decidida):
- **é uma estimativa** (A4.1): quanto o protótipo fecha, com que incerteza. **O G-MVP é só estimativa, sem passa nem falha** (A4.2). O 0,8
  é só referência, não gate;
- **a avaliação não demonstra a prontidão do protótipo nem a superioridade modular** (A4.2 e A4.6):
  - sem passa, o gate de prontidão (seção 5.6, ii) não é cumprido, e o A segue como o cérebro do MVP;
  - a comparação com o A11 segue descritiva. Os contrastes são entre os braços do próprio modular: medem módulos, não arquiteturas;
  - um contraste rejeitado não se lê como "o modular vai à comida pelos próprios módulos" (isso exige o G-MVP passar, seção 5.5);
- **a persistência:** o G-ABLA-PERS é **inconclusivo por premissa** qualquer que seja o p (seção 5.3; A4.0). A G-PESA dela falha de novo
  aqui;
- **a ressalva do g1:** um contraste com g1 ≤ −0,5 sai com a frase de A4.4.6, e uma rejeição nele não é lida como confirmação. **O
  limiar −0,5 segue PROPOSTO** (A4.9);
- **a G-MOD tem o erro de família a 5,9 % sob a nula global** (A4.4.4), registrado como ressalva da família. A G-MOD é secundária;
- **os valores** são os calibrados do #428 (`eta_h` S/256, `w_pers` 4S, `tau_c` 15, o cheiro S/4 e 6), que seguem PROPOSTOS.

**Como rodou:** registrado em A4.10 antes da primeira vida (#432). A run saiu do commit `988cf0d`, com a árvore limpa, uma vez (o
`meta.json`: `git_head`, `git_limpo` = true, o sha256 da config `d1d99106…325e`, o registrado, e os sha do orquestrador, do `config.py`,
do `engine.py` e do `metrics.py`, iguais aos de A4.10).
- **As bases** 66101, 66202, 66303, 66404 e 66505, com K = 10 (50 unidades). Os 12 braços nas 12 células, 14 dias, orçamento de 16, o
  M4-con com o `g_apr` 1 923: **7 200 vidas.**
- **4 processos,** pela decisão do Matheus sobre a máquina (o registro "DIGIBRAIN-MODULAR-REAVALIACAO-PROCESSOS"). Nenhum processo
  morreu.
- **O tempo:** 7 060 s de parede para as vidas e 7 065 s no total (cerca de 1 h 58 min), acima da estimativa de 1 h 30 min. O custo por
  vida subiu: de 3,15 a 3,25 s de CPU nos braços modulares e 2,70 s no A11, contra 2,05 a 2,19 e 1,78 s no piloto.
- **Toda vida foi rejogada do disco bit a bit dentro da run** (o G1), e o G-MECANISMO foi conferido em cada uma. Nada divergiu.
- **Os artefatos** estão em `artifacts_v2_digibrain_prototipo/reavaliacao/`:
  - o `meta.json` (sha256 `0c3dca0e…198e`);
  - o `medidas.json` (54 MB, sha256 `73ae8a8a…df01`), no git sem compressão, pela decisão do Gerente;
  - o `resultado.json` (sha256 `18eddd7a…813c`).
  - As 7 200 vidas (518 MB) ficam fora do git, na worktree `v2-modular-reavaliacao`. Todos os números abaixo saem do `resultado.json`,
    salvo o tempo (o `meta.json`).

**O G-MVP** (a estimativa; o IC95 pelo t sobre as 50 unidades; o percentil do bootstrap ao lado, descritivo e anticonservador com 5
bases):

| | a medida | estimativa | IC95 (t) | IC95 (percentil) | em relação a 0,8 |
|---|---|---|---|---|---|
| **G-MVP-EP** (a primária, A3.3) | a fração de vidas do M3\* com o fechamento por episódio ≥ 0,5 | **0,8083** | [0,7909; 0,8257] | [0,7967; 0,8217] | o IC95 contém 0,8 |
| G-MVP (por ração, a secundária obrigatória) | a fração de vidas do M3\* com o fechamento ≥ 0,5 | **0,4050** | [0,3871; 0,4229] | [0,3883; 0,4183] | o IC95 inteiro abaixo de 0,8 |

- **As premissas de elegibilidade passam:** o G-ELEGIVEL-EP e o G-ELEGIVEL dão 1,0 (as 600 vidas do M3\*). Nenhuma vida fica sem
  episódio.
- **A leitura** (A4.2): a estimativa por episódio fica em 0,81, com o IC95 contendo a referência. Por ração, fica em 0,41. Sem passa nem
  falha.

**As famílias com o Holm** (α 0,05 por família; o p unilateral do t sobre as 50 unidades, salvo o G-MOD-EMB, pelo t sobre as 5 médias de
base; positivo = a direção da espec):

| contraste | a medida (células) | média | IC95 (t) | p | p Holm | rejeita | g1 | a leitura (A4.6) |
|---|---|---|---|---|---|---|---|---|
| G-ABLA-P1 | `falta_ao_comer`(M0) − (M1) (12) | 0,0427 | [0,0373; 0,0482] | < 10⁻²⁰ | < 10⁻¹⁹ | sim | −0,04 | o módulo pesa no sentido previsto dentro do M3\*, nestas condições |
| G-ABLA-MEM | o fechamento (M3\*) − (M2) (4, comedouro) | 0,1356 | [0,1150; 0,1562] | < 10⁻¹⁷ | < 10⁻¹⁶ | sim | 0,07 | idem |
| G-ABLA-PERS | `intencoes_com_meta`(M3\*) − (M3-sp) (12) | 0,0033 | [−0,0019; 0,0085] | 0,1048 | 0,2097 | não | −0,36 | **inconclusivo por premissa** |
| G-ABLA-P2 | o índice de repetição (M2) − (M1) (12) | −0,0176 | [−0,0217; −0,0134] | 1,0000 | 1,0000 | não | 0,62 | o Holm não rejeita |
| G-MOD-EMB | `D_FE`(M4-emb) − (M4) (12) | 0,0013 | [−0,0020; 0,0045] | 0,1719 | 0,3439 | não | **−0,55** | o Holm não rejeita; a ressalva do g1 |
| G-MOD-CON | `D_FE`(M4-con) − (M4) (12) | 0,0011 | [−0,0037; 0,0060] | 0,3234 | 0,3439 | não | 0,29 | o Holm não rejeita |
| G-DX-INATO, longe | o fechamento por episódio (M3\*) − (M3\*−inato) (4) | 0,0129 | [−0,0132; 0,0390] | 0,1623 | 0,3247 | não | −0,01 | o Holm não rejeita |
| G-DX-INTENCAO, longe | idem, (M3\*) − (M3\*−intencao) (4) | 0,0005 | [−0,0204; 0,0214] | 0,4799 | 0,4799 | não | 0,52 | o Holm não rejeita |
| G-DX-INATO, todas | idem, nas 12 células | 0,0076 | [−0,0077; 0,0229] | 0,1607 | 0,3214 | não | −0,19 | o Holm não rejeita |
| G-DX-INTENCAO, todas | idem, nas 12 células | 0,0008 | [−0,0096; 0,0113] | 0,4376 | 0,4376 | não | **−0,63** | o Holm não rejeita; a ressalva do g1 |

- **O G-MOD-EMB pelas 5 médias de base:** 0,0006, 0,0056, −0,0014, 0,0008 e 0,0006 (t = 1,07, 4 gl).
- **As ressalvas do g1** caem em dois contrastes, o G-MOD-EMB e o G-DX-INTENCAO nas 12 células. Nenhum deles é rejeitado, e a ressalva
  não muda o p, o Holm nem a decisão gravada. Os dois rejeitados (o P1 e o MEM) têm g1 perto de zero.
- **A G-MOD** não rejeita nenhum dos dois, com a ressalva da família (5,9 % sob a nula global).
- **O G-ABLA-P2** sai com o sinal contrário ao previsto, como no piloto do #420 e no do conserto.
- **O 2 × 2 do cheiro, no longe** (o fechamento por episódio, a média das unidades): M3\* 0,4339; M3\*−intencao 0,4334; M3\*−inato
  0,4211; M3-420 0,4272. A interação é 0,0066 [−0,0300; 0,0432]. Nas 12 células: 0,7360, 0,7352, 0,7284 e 0,7292, com a interação 0,0016
  [−0,0159; 0,0191].

**As premissas, a G-PESA** (seção 5.3; o limite inferior do IC95 pelo t > 0,01):

| módulo | braço | média | IC95 (t) | passa |
|---|---|---|---|---|
| o incentivo | M1 | 0,0192 | [0,0185; 0,0199] | sim |
| o hábito | M2 | 0,0817 | [0,0793; 0,0842] | sim |
| a memória | M3\* | 0,1101 | [0,1062; 0,1139] | sim |
| a persistência | M3\* | **0,0035** | [0,0033; 0,0037] | **não** |

- **Quantos episódios as vidas têm:** no M3\*, a média é 16,6 e a mediana 15, com o mínimo 4. Todas as vidas dos braços modulares têm 3
  episódios ou mais; no A11, 57,8 %.

**Os descritivos** (sem gate; o IC95 pelo t):
- **a comparação com o A11** (seção 7; a diferença bruta, M3\* − A11):
  - o fechamento por episódio: +0,3189 [0,2893; 0,3486];
  - a fração de vidas com a cadeia por episódio: +0,1733 [0,1255; 0,2211];
  - as refeições por dia: +2,2833 [2,2415; 2,3252];
  - a privação: −0,5383 [−0,5554; −0,5212];
  - o `D_FE`: −0,0670 [−0,0739; −0,0601];
- **a DX-5** (A3.5, exploratória), M2 − M1, pelas ações com recompensa possível: −0,0211 [−0,0285; −0,0137] no total. No comer, +0,0242
  [0,0027; 0,0456]; no explorar, −0,0175 [−0,0263; −0,0086]. O brincar e o aliviar ficam sem valor;
- **a D-2** (o hábito menos a memória): 0,7607 [0,5710; 0,9503]. **A D-1** (a entropia por dia, padronizada): −0,2066 [−0,4192; 0,0059];
- **a leitura com 11 células** (sem a duplicata do comedouro): o G-MVP-EP fica em 0,7909 [0,7719; 0,8099], e o G-MVP por ração, em 0,4418
  [0,4223; 0,4614];
- **as medidas de mecanismo do cheiro**, por braço e lugar, estão no `descritivos_conserto` do `resultado.json`.

**O que fica para o Matheus:**
- **a leitura da reavaliação:**
  - o G-MVP-EP estimado em 0,81, com o IC95 contendo 0,8, e o G-MVP por ração em 0,41;
  - os módulos do incentivo e da memória pesam no sentido previsto dentro do M3\*, nestas condições;
  - o G-ABLA-P2 (o hábito), os dois G-MOD e a G-DX não rejeitam;
  - a persistência segue inconclusiva por premissa;
- **o que a reavaliação não diz:** que o protótipo está pronto, ou que o modular é superior ao A;
- **o que segue PROPOSTO:** os valores do #428 e o limiar −0,5 do g1.

## 9. O descritivo da reavaliação (2026-10-29, worker D, Claude Code, Opus 5.5; exploratório, pós hoc)

**Antes dos números:**
- **é um descritivo exploratório e pós hoc, como o #199:**
  - nenhuma vida, nenhum replay, nenhuma faixa nova;
  - nenhum teste de hipótese, nenhum IC e nenhum gate;
  - nada aqui muda a leitura do adendo 4 (a seção 8) nem os valores PROPOSTOS.
- **A comparação com o A11 é só descritiva,** sem leitura de superioridade (A4.2).
- **A fonte e o script:**
  - os números saem de `experiments/descritivo_reavaliacao_digibrain.py`, que lê três `medidas.json`: o da reavaliação, o do piloto do
    conserto e o da avaliação única (#420), todos no git;
  - ele grava `artifacts_v2_digibrain_prototipo/descritivo_reavaliacao/descritivo.json`, com o sha256 de cada fonte e o do próprio
    script;
  - antes de gravar, refaz as duas frações do G-MVP pela regra do orquestrador e confere que são as do `resultado.json` da reavaliação
    (0,4050 e 0,8083). Se não forem, falha alto.
- **As contas:**
  - cada número é uma soma sobre as vidas ou uma média por vida (as vidas com valor), como no #422;
  - as frações e as taxas são as de cada medida, com o limiar 0,5 da vida.

### 9.1 O episódio contra a ração, no M3\* (600 vidas)

**As mesmas vidas, duas contas:**

| | por ração (o G-MVP) | por ração com a W(d) | por episódio (o G-MVP-EP) |
|---|---|---|---|
| a fração das vidas com a taxa ≥ 0,5 | 0,405 | 0,418 | 0,808 |
| a taxa por vida, média (mediana) | 0,399 (0,297) | 0,429 (0,393) | 0,736 (0,827) |
| a taxa sobre as somas | 0,234 (9 386 de 40 118) | 0,255 | 0,785 (7 845 de 9 988) |

- **A tabela 2 × 2 das vidas:**
  - 242 vidas passam de 0,5 nas duas medidas, e 114 em nenhuma;
  - **243 passam só por episódio;**
  - 1 passa só por ração.
- **A diferença está quase toda nessas 243 vidas.** Pelo episódio, a vida fecha; pela ração, não.

**A primeira causa é o denominador.** As duas medidas contam coisas diferentes (`digilab/metrics.py`):
- a por ração conta **cada ração** posta com a fome abaixo de 0,5, e cada uma só fecha se o pet comer **aquela** ração em 8 decisões;
- a por episódio conta **um episódio** por trecho contínuo de fome. Ele fecha se, na janela W(d0), o pet comer **qualquer** ração madura
  do dono que baixe a fome.

Nas somas, a identidade é exata:

> taxa por ração = (rações fechadas por episódio fechado) × (taxa por episódio) × (episódios por ração elegível)

| | rações elegíveis por episódio | rações fechadas por episódio fechado | taxa por episódio | taxa por ração |
|---|---|---|---|---|
| **M3\*, todas** | **4,02** | 1,20 | 0,785 | 0,234 |
| atencioso | 6,32 | 1,20 | 0,854 | 0,163 |
| incoerente | 6,32 | 1,20 | 0,856 | 0,162 |
| aleatório | 1,85 | 1,32 | 0,708 | 0,507 |
| relapso | 1,52 | 1,11 | 0,717 | 0,524 |
| comedouro | 3,79 | 1,25 | 0,816 | 0,270 |
| perto | 1,92 | 1,22 | 0,964 | 0,612 |
| longe | **7,81** | 0,98 | 0,447 | **0,056** |

- **A leitura:**
  - num trecho de fome, o dono põe em média 4 rações, e o pet fecha cerca de 1,2 delas;
  - a medida por ração conta as outras 2,8 como falhas, mesmo quando o episódio fechou;
  - o atencioso e o incoerente põem 6,3 rações por episódio e chegam à taxa por ração mais baixa (0,16), com a taxa por episódio mais
    alta (0,85). No relapso e no aleatório, com cerca de 1,5 a 1,9 ração por episódio, as frações das vidas ficam perto (0,66 · 0,67 e 0,64 · 0,73);
  - **no longe, as duas coisas se somam:** 7,8 rações por episódio e menos da metade dos episódios fechando.
- **A célula incoerente/comedouro** repete a atencioso/comedouro em todos os números deste descritivo. É a duplicata conhecida, a que a
  leitura com 11 células tira.

**A segunda causa é a janela, pequena:** com a W(d) no lugar das 8 decisões fixas, a taxa por ração sobe de 0,234 para 0,255, e a fração
das vidas, de 0,405 para 0,418. No longe, sobe de 0,056 para 0,072.

**Onde as rações elegíveis ficam** (na janela W(d) de cada uma; as 40 118):

| | visível em k0 | entrou na visão na janela | nunca na visão na janela | a menor distância, média por vida |
|---|---|---|---|---|
| todas | 37 % | 21 % | 42 % | 5,4 células |
| comedouro | 45 % | 48 % | 7 % | 1,6 |
| perto | 100 % | 0 % | 0 % | 0,9 |
| longe | 6 % | 12 % | **82 %** | 13,7 |

O `medidas.json` guarda essas contagens por vida, não o destino de cada ração. Por isso não dá para cruzar a visão com o fechamento ração a
ração. Uma ração nunca vista ainda pode fechar pelo cheiro.

**Onde os episódios não fecham:**
- **os fins:** dos 9 988 episódios, 7 845 fecham, 2 117 vencem a janela e 26 acabam com a vida. Nenhum é saciado por outra comida. Em 306,
  a oferta muda dentro da janela;
- **pela distância da ração mais próxima na abertura** (d0):

  | | episódios | fecham | taxa |
  |---|---|---|---|
  | na visão (até 6 células) | 6 115 | 5 769 | 0,94 |
  | só no cheiro (até 24 células) | 3 420 | 1 984 | 0,58 |
  | além do cheiro | 453 | 92 | 0,20 |

  - no perto, quase todos os episódios abrem na visão (4 117 de 4 172);
  - no longe, só 433 de 2 503 abrem na visão: 1 629 abrem no cheiro, e 441 além dele.
- **depois da janela:** em 2 060 dos 2 117 episódios vencidos, o pet come uma ração do dono mais tarde na mesma fome, com a mediana de 21 decisões
  depois da abertura.
- **As trocas de meta** (os fins das intenções na vida inteira, por vida):

  | | a meta | trocou | achou | as buscas pelo cheiro que trocaram |
  |---|---|---|---|---|
  | todas | 71,7 | 35,3 | 12,2 | 9,5 |
  | comedouro | 69,9 | 17,7 | 11,9 | 2,6 |
  | perto | 79,0 | 12,8 | 7,1 | 0,1 |
  | longe | 66,2 | **75,3** | 17,6 | **25,7** |

  - a troca de meta é cerca de quatro vezes mais frequente no longe que no comedouro;
  - a busca pelo cheiro só troca com alguma frequência no longe.
- **As refeições:** o pet come 3,18 rações por dia. Das 26 688 refeições de ração, 7 845 fecham um episódio, e 18 843 caem fora de
  episódio aberto: com a fome acima de 0,5, ou depois de o episódio daquela fome fechar ou vencer.

**Por dono e por lugar** (a fração das vidas ≥ 0,5, por ração e por episódio):

| | comedouro | perto | longe |
|---|---|---|---|
| atencioso | 0,00 · 1,00 | 0,42 · 1,00 | 0,00 · 0,68 |
| relapso | 0,98 · 1,00 | 1,00 · 1,00 | 0,00 · 0,00 |
| aleatório | 0,92 · 0,98 | 1,00 · 1,00 | 0,00 · 0,22 |
| incoerente | 0,00 · 1,00 | 0,54 · 1,00 | 0,00 · 0,82 |

- **Nenhuma vida do longe passa de 0,5 por ração,** com qualquer dono.
- **No comedouro,** o atencioso e o incoerente fecham por episódio em toda vida, e por ração em nenhuma: 7,2 rações por episódio.
- **No relapso e no aleatório,** fora do longe, as duas medidas quase coincidem.

### 9.2 O hábito ao contrário (o G-ABLA-P2, M2 − M1)

O índice "ganhou, fica" (a média por vida), nas três runs:

| | avaliação única (#420) | piloto do conserto | reavaliação |
|---|---|---|---|
| M1 | −0,083 | −0,088 | −0,083 |
| M2 | −0,094 | −0,100 | −0,101 |
| **M2 − M1, todas** | −0,011 | −0,012 | **−0,018** |
| M2 − M1, comedouro | +0,008 | 0,000 | −0,004 |
| M2 − M1, perto | +0,004 | +0,001 | −0,004 |
| M2 − M1, **longe** | **−0,046** | **−0,038** | **−0,045** |
| M2 − M1, atencioso/longe | −0,099 | −0,087 | −0,085 |
| M2 − M1, incoerente/longe | −0,099 | −0,065 | −0,082 |
| M2 − M1, relapso (todos os lugares) | +0,022 | +0,014 | +0,013 |

**O padrão é o mesmo nas três runs:**
- a diferença negativa mora no **longe,** e dentro dele no **atencioso e no incoerente;**
- no comedouro e no perto, o M2 − M1 fica perto de zero;
- no relapso, ele é positivo nas três.
- A diferença da reavaliação é um pouco maior. O comedouro e o perto saem levemente negativos, e o perto, que era positivo no #420,
  também.

**Por ação** (a DX-5: só os pares cuja primeira decisão é de uma ação com r possível). Os números são M1 / M2 / M2 − M1. O `medidas.json`
do #420 não tem a DX-5, que veio no adendo 3, então a comparação por ação é só com o piloto:

| | piloto, todas | reavaliação, todas | reavaliação, comedouro | reavaliação, perto | reavaliação, longe |
|---|---|---|---|---|---|
| com r possível (total) | 0,009 / −0,020 / −0,030 | 0,002 / −0,019 / −0,021 | +0,013 (M2 − M1) | +0,008 | **−0,086** |
| comer | −0,072 / −0,043 / +0,029 | −0,068 / −0,056 / +0,012 | +0,002 | +0,047 | −0,004 |
| explorar | 0,034 / 0,000 / −0,034 | 0,025 / 0,007 / −0,018 | +0,021 | +0,002 | **0,056 / −0,021 / −0,077** |
| brincar | (poucas vidas: 3 e 4) | (14 e 18 vidas) | — | — | — |
| aliviar | (nenhum par) | (nenhum par) | — | — | — |

- **O explorar no longe** é onde o M2 perde: o M1 fica +0,056 depois de um r positivo do explorar, e o M2, −0,021. O piloto dá +0,079 e
  −0,025; o #422 achou +0,055 e −0,091. **O mesmo sinal nas três leituras.**
- **No comer, o hábito sobe o "ganhou, fica"** no piloto, nos três lugares (+0,018, +0,027 e +0,043). Na reavaliação, isso só acontece
  claramente no perto (+0,047); no comedouro (+0,002) e no longe (−0,004), fica perto de zero. É a parte da H-P2a do #422 que esta run não
  repete.
- **As ações sem r** (dormir, chamar a atenção, ocioso, emburrar):
  - elas abrem cerca de dois terços dos pares (0,678 no M1 e 0,669 no M2), sempre do lado r ≤ 0;
  - nelas, o pet repete a ação 36 % e 35 % das vezes. Isso puxa o índice para baixo nos dois braços: o total do M1 é −0,083, e o das ações
    com r possível, +0,002;
  - **a diferença M2 − M1 quase não vem delas:** −0,021 nas ações com r possível, contra −0,018 no total. A conta dos pares sem r sai do
    total menos a DX-5 (o lado r > 0 é o mesmo nos dois, e o script confere).
- **O lado r > 0:** o M2 fica menos depois de um r positivo que o M1 (0,236 contra 0,262), e só um pouco menos depois de um r ≤ 0 (0,337
  contra 0,345).

### 9.3 O A11 ao lado (só descritivo, sem leitura de superioridade)

As mesmas contas do 9.1, nas 600 vidas do A11:

| | M3\* | A11 |
|---|---|---|
| a fração das vidas ≥ 0,5, por ração · por episódio | 0,405 · 0,808 | **0,000** · 0,635 |
| a taxa sobre as somas, por ração · por episódio | 0,234 · 0,785 | 0,033 · 0,630 |
| rações elegíveis por episódio | 4,02 | **10,81** |
| rações fechadas por episódio fechado | 1,20 | **0,56** |
| refeições de ração por dia | 3,18 | 0,89 |
| refeições fora de episódio aberto | 71 % | 47 % |
| as rações visíveis em k0 · nunca na visão | 37 % · 42 % | 63 % · 33 % |
| episódios na visão: n, taxa | 6 115, 0,94 | 5 495, 0,64 |
| episódios vencidos · com o fim da vida | 2 117 · 26 | 2 351 · 1 |

- **Nenhuma vida do A11 passa de 0,5 por ração;** 381 das 600 passam por episódio.
- **O A11 fecha um episódio sem fechar a ração elegível com mais frequência que o M3\*:**
  - fecha 0,56 ração por episódio fechado, e 0,04 no comedouro;
  - come pouco (0,89 ração por dia);
  - as somas são compatíveis com o A11 comer, no episódio, uma ração que não é a elegível daquela janela (uma posta antes, sem fome), ou
    comê-la depois das 8 decisões. O `medidas.json` não guarda qual ração fechou cada episódio, então isso não se confirma daqui.
- **O relapso e o aleatório,** no A11, têm 18 a 22 rações por episódio, e as vidas comem 0,07 a 0,08 ração por dia.
- O A11 não grava os fins das intenções nem o cheiro: essas linhas ficam sem ele.

**O que fica para o Matheus:** a leitura deste descritivo, que é só exploratório. As sugestões estão no PR, nas "Questões abertas", e
nenhuma mecânica mudou.

## 10. A etapa L0 do longe (2026-10-29, worker D, Claude Code, Opus 5.5; diagnóstico)

**Antes dos números:**
- **é um diagnóstico só de leitura,** a etapa L0 da `docs/PROPOSTA_LONGE_DIGIBRAIN_MODULAR.md`. O registro está na seção 8 dela,
  commitado em `442ff86` antes do replay e conferido pelo Gerente;
- **o que não houve:** nenhuma vida nova, nenhuma semente, nenhum gate;
- **o que não mudou:** o motor, o `engine.py`, o corpo, os cérebros e as medidas por vida;
- **a 66xxx fica gasta** para qualquer uso confirmatório futuro (o registro "DIGIBRAIN-MODULAR-LONGE-L0");
- **a regra de escolha** é a da seção 2 da proposta, como está, com os limiares PROPOSTOS e SEM FONTE.

**Como rodou:**
- **o comando:** `experiments/longe_l0_digibrain.py`, do commit `f5a8a9c`, com a árvore limpa e 4 processos;
- **as vidas:** 1 200 (o M0 e o M3\*, nas 12 células e nas 50 unidades), em 349 s;
- **os logs:** os da run da reavaliação (o commit `988cf0d`), só lidos, na worktree `v2-modular-reavaliacao`;
- **o G1 passou nas 1 200 vidas:**
  - cada uma, rejogada do log, refez as medidas gravadas no `medidas.json` (sha256 `73ae8a8a…df01`), campo a campo, menos o `custo`;
  - os 15 arquivos de código têm os sha do `meta.json` da reavaliação;
- **a saída:** `artifacts_v2_digibrain_prototipo/longe_l0/l0.json` (sha256 `6541fbe8…940e`), com o sha de cada um dos 1 200 logs;
- **a conferência cruzada:** as buscas trocadas por vida no longe do M3\* (25,7) são as do descritivo da seção 9 (`fins_busca`).

### 10.1 A regra (o longe do M3\*; o M0 ao lado)

| | o critério (PROPOSTO, SEM FONTE) | M3\* | M0 | pesa? |
|---|---|---|---|---|
| **a percepção** (M-L1) | a direção do cheiro a mais de 45° de toda ração a menos de R, em ≥ 25 % das decisões | **5,8 %** (de 98 497) | 6,4 % (de 81 492) | **não** |
| **a decisão** (M-L2) | ≥ metade das buscas trocadas quebradas pelo reflexo do sono, ou por outra unidade com a ração a menos de R | **99,9 %** (5 138 de 5 142) | 100 % (4 372 de 4 372) | **sim** |

**A regra aponta a L-2, a decisão,** no M3\*, e o M0 concorda.

- **A direção 0** (a ração a menos de R, nenhuma comida vista e sem direção do cheiro): 5 005 decisões no longe do M3\*, 4,8 % das que têm
  a ração a menos de R e nenhuma comida vista; 6,7 % no M0. No comedouro, 0; no perto, 0,1 %. **A fração é pequena:** o cheiro quase
  sempre tem direção.
- **Uma ressalva sobre o critério da decisão:** ele passa em todo lugar, e não só no longe. No comedouro, dá 100 % (513 buscas trocadas); no
  perto, 95,5 % (22).
  - Quase toda busca trocada é trocada por uma unidade que não come, e quase sempre há ração a menos de R. **O que separa o longe é a
    contagem:** 25,7 buscas trocadas por vida, contra 2,6 no comedouro e 0,1 no perto.
  - A ressalva não muda o veredito, que é o da regra registrada.

### 10.2 As medidas (o M3\*, por lugar)

**M-L1, a percepção:**

| | comedouro | perto | longe |
|---|---|---|---|
| decisões (a ração a menos de R, nenhuma comida vista, direção ≠ 0) | 34 288 | 12 074 | 98 497 |
| a direção a mais de 45° de **toda** ração | 0,9 % | 0,5 % | **5,8 %** |
| a direção a mais de 45° da ração **mais próxima** | 0,9 % | 1,2 % | **35,3 %** |
| o ângulo à mais próxima, mediana | 13,2° | 13,4° | 26,5° |
| rações a menos de R, mediana | 2 | 1 | 2 |

- **No longe, o cheiro costuma apontar para alguma ração, mas não para a mais próxima** em um terço das decisões. Isso combina com o campo
  que é soma de várias fontes (a seção 1.2 da proposta): a direção puxa para um grupo de rações, e não para a mais perto.
- **Pela regra, não chega a pesar:** fora de toda ração, só 5,8 %.

**M-L2, a decisão (as buscas pelo cheiro trocadas):**

| | comedouro | perto | longe |
|---|---|---|---|
| buscas trocadas por vida | 2,6 | 0,1 | **25,7** |
| quebradas pelo reflexo do sono | 363 (71 %) | 10 | **4 096 (80 %)** |
| por outra unidade, com a ração a menos de R | 150 | 11 | 1 042 (20 %) |
| para comer (não é quebra) | 0 | 1 | 3 |

- **As vencedoras no longe:** dormir 4 318 (4 096 pelo reflexo e 222 pelo sorteio); chamar a atenção, 330; emburrar, 9; brincar, 5; comer
  a comida vista, 3.
- **As intenções de comer trocadas** (ao lado da regra): 935 no longe, 4,7 por vida; 706 pelo reflexo do sono, e 134 para outra unidade de
  comer.
- **O que a medida mostra:** no longe, a busca pelo cheiro é interrompida sobretudo pelo sono. É a parte (b) da L-2, "a intenção que
  sobrevive ao sono". A histerese da parte (a) atacaria os outros 20 %.

**M-L3, o andado** (os episódios de fome, na janela):

| | comedouro, fechados | comedouro, não fechados | longe, fechados | longe, não fechados |
|---|---|---|---|---|
| episódios | 2 703 | 610 | 1 120 | 1 383 |
| decisões acordado na janela | 54 % | 44 % | 64 % | 52 % |
| decisões em que o pet andou | 47 % | 31 % | 51 % | 36 % |
| o andado líquido em direção ao alvo, mediana (em decisões de passo) | 0,95 | 1,03 | 1,02 | **0,15** |
| o n_min(d0), mediana | 2 | 3 | 3 | **5** |
| episódios com o andado líquido ≥ n_min | 12 % | 1 % | 10 % | **0,1 %** |

No longe, o episódio que não fecha quase não se aproxima do alvo: 0,15 passo líquido na mediana, para os 5 de que precisaria.

**M-L4, a distância no cheiro** (o d0 de 6 a 24 células):

| a faixa de d0 | comedouro: episódios, taxa | longe: episódios, taxa |
|---|---|---|
| de 6 a 12 células | 1 270, 0,81 | 784, **0,52** |
| de 12 a 18 | 416, 0,56 | 420, 0,32 |
| de 18 a 24 | 50, 0,22 | 425, 0,29 |
| a mediana do d0 | 9,9 células | 12,3 células |

**A diferença do 0,74 × 0,41 não é só de distância.** Na mesma faixa de 6 a 12 células, o comedouro fecha 0,81 e o longe, 0,52. O longe
tem também mais episódios longe dentro da faixa (a mediana de 12,3 células, contra 9,9).

**M-L5, a ração que fecha** (a questão aberta do #433):

| | comedouro | perto | longe |
|---|---|---|---|
| episódios fechados | 2 703 | 4 022 | 1 120 |
| a ração comida era a mais próxima na abertura | 63 % | 70 % | 50 % |
| ela estava na oferta da abertura | 68 % | 72 % | 63 % |
| ela era elegível na medida por ração | 87 % | 96 % | 87 % |
| a idade dela ao fechar, mediana (decisões desde a posta) | 4 | 1 | 8 |

Um terço dos episódios fecha com uma ração que ainda não estava no chão na abertura: o dono põe outra durante a janela.

**M-L6, as fontes do cheiro** (rações maduras a menos de R, por decisão): no longe, a média é 3,65 e a mediana 1. Em 12,9 % das decisões,
há 10 ou mais. No comedouro, a média é 2,26; no perto, 0,58.

### 10.3 A leitura

- **A regra registrada aponta a L-2,** o compromisso da viagem, no cérebro. Pelo PL-2, essa é a opção. Pelo PL-5, o mundo do motor não
  muda: o M-L1 não deu a evidência que a L-1 pediria.
- **O que pesa dentro da L-2:** no longe, 80 % das buscas trocadas são quebradas pelo reflexo do sono, e 20 % por outra unidade. **A parte
  (b), a intenção que sobrevive ao sono, é a que os dados apontam primeiro.** A histerese da parte (a) fica com os 20 %.
- **O que fica como ressalva:**
  - o critério da decisão passa em todo lugar; o que distingue o longe é a contagem (dez vezes a do comedouro);
  - o cheiro aponta para a mais próxima em só dois terços das decisões do longe. A percepção não pesa pela regra, mas não é perfeita;
  - a distância não explica toda a diferença: na mesma faixa de 6 a 12 células, o longe fecha 0,52, e o comedouro, 0,81.
- **O que o diagnóstico não diz:** que a L-2 vai consertar o longe. Isso é a pergunta do próximo plano, por episódio, como o PL-3 decidiu.

## 11. O piloto da L-2 (2026-10-29, worker D, Claude Code, Opus 5.5; adendo 5, A5.8)

**Antes dos números:**
- **o piloto só fixa o K** (A5.8). Nenhum critério é lido, e nenhum número de efeito entra nesta leitura. O `resultado.json` traz as
  médias dos braços e o bloco do mecanismo, que esta seção não lê;
- **a regra e os limiares** são os da A5.8, escritos antes do piloto, PROPOSTOS e SEM FONTE. Nada aqui os muda.

**Como rodou:**
- **o comando:** `experiments/run_v2_digibrain_l2.py`, do commit `0d11e02` (a `main` com o conserto do #439), com a árvore limpa
  (`git_limpo` = true no `meta.json`) e 4 processos;
- **as vidas:** as bases 67101 e 67202, com K = 5 (10 unidades), os 4 braços nas 12 células, 14 dias: **480 vidas,** em 293 s de parede,
  das 14h22 às 14h27 de 2026-10-29;
- **as conferências:** toda vida foi rejogada do disco bit a bit (o G1), com o T-CENARIO-1, o G-MECANISMO e o crédito conferidos em cada
  uma;
- **os artefatos,** em `artifacts_v2_digibrain_prototipo/l2/piloto/`:
  - o `meta.json` (sha256 `f75e52af…41cb`);
  - o `medidas.json` (sha256 `922c22f2…f6ad`);
  - o `resultado.json` (sha256 `0480de0f…1931`);
  - as 480 vidas ficam fora do git.
- **O piloto que caiu antes** (o registro "DIGIBRAIN-MODULAR-L2-CREDITO") foi movido, inteiro, para `piloto_caido_1/`, ao lado:
  - o `meta.json` dele tem o mesmo sha256 de antes de mover (`26f43a8b…bb9c`), e os 477 logs são os mesmos;
  - **o determinismo:** as 477 vidas que existem nas duas pastas têm o mesmo sha256 de log, e as 3 que só existem no piloto novo são as
    que não tinham rodado (`artifacts_v2_digibrain_prototipo/l2/piloto_caido_1_conferencia.json`).

**As 10 comparações do C-L2-3,** o par primário (M3\*+S − M3\*), as 10 unidades:

| a comparação | margem | σ(M3\*) | σ(M3\*+S) | rho | σ_d | poder com K = 12 | 21 | 30 | 51 | 102 | 201 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| episódio, comedouro | −0,03 | 0,0595 | 0,0593 | 0,956 | 0,0177 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 |
| episódio, perto | −0,03 | 0,0192 | 0,0161 | 0,856 | 0,0099 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 |
| ração, comedouro | −0,03 | 0,0445 | 0,0355 | 0,554 | 0,0386 | 0,688 | 0,930 | 0,986 | 1,000 | 1,000 | 1,000 |
| ração, perto | −0,03 | 0,0298 | 0,0282 | 0,991 | 0,0042 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 |
| exaustão, comedouro | +0,02 | 0,0265 | 0,0312 | 0,950 | 0,0103 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 |
| exaustão, perto | +0,02 | 0,0273 | 0,0277 | 0,995 | 0,0027 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 |
| **exaustão, longe** | +0,02 | 0,0252 | 0,0524 | **0,297** | 0,0510 | 0,200 | 0,387 | 0,541 | 0,786 | 0,976 | 1,000 |
| privação, comedouro | +0,02 | 0,0589 | 0,0587 | 0,965 | 0,0157 | 0,987 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 |
| privação, perto | +0,02 | 0,0602 | 0,0609 | 1,000 | 0,0019 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 |
| **privação, longe** | +0,02 | 0,0756 | 0,1076 | **0,140** | **0,1226** | 0,051 | 0,090 | 0,125 | 0,200 | 0,369 | **0,634** |

**A conjunção** (o produto dos 10 poderes): 0,0069 com K = 12; 0,0325 com 21; 0,0666 com 30; 0,1569 com 51; 0,3598 com 102; **0,6337 com
201.**

**O K da regra: nenhum.** Nenhum K da grade chega a 0,8, e **o K volta ao Matheus** (A5.8). A A5.9 não foi escrita, e a avaliação não roda.

**A leitura** (só da dispersão, sem número de efeito):
- **no comedouro e no perto,** as duas vidas de cada par andam juntas (rho de 0,55 a 1,0), e as 8 comparações deles têm o poder de 0,93 ou
  mais já com K = 21 (a mais baixa é a ração no comedouro);
- **no longe,** a suspensão separa as duas vidas do par: o rho cai a 0,30 na exaustão e a 0,14 na privação. A diferença pareada fica tão
  dispersa quanto a de duas vidas independentes;
- **a privação no longe domina:** com a margem +0,02 e o σ_d de 0,1226, ela sozinha deixa a conjunção abaixo de 0,8 em toda a grade.

**O custo, para o Matheus** (`artifacts_v2_digibrain_prototipo/l2/custo_k.json`, sha256 `2ac49090…c7be`; 48 vidas por unidade e o tempo de
parede do piloto, 0,61 s por vida com 4 processos):

| K (unidades) | vidas | parede com 4 processos | a conjunção |
|---|---|---|---|
| 51 | 2 448 | 0,41 h | 0,157 |
| 102 | 4 896 | 0,83 h | 0,360 |
| 201 | 9 648 | 1,63 h | 0,634 |
| **297** (fora da grade, só informação) | **14 256** | **2,42 h** | 0,801 |

O K = 297 é o menor múltiplo de 3 com a conjunção a 0,8, pela mesma conta e com os σ_d do piloto. Ele está fora da grade da A5.8 e não
é o K da regra: fica só como o custo do que a regra pede. A faixa 67xxx tem as bases 67303, 67404 e 67505 para a avaliação. Com 297
unidades, seriam 99 por base.

**O que fica para o Matheus:**
- **o K:** a regra não dá um K na grade, e o K volta a ele com o custo (A5.8). As saídas possíveis:
  - um K maior que a grade, com o custo da tabela;
  - a margem da privação no longe revista, o que reabre a LS-7;
  - rodar com um K da grade sabendo que o C-L2-3 tem o poder da tabela;
- **nada roda** antes da decisão dele.

## 12. A avaliação da L-2 (2026-10-29, worker D, Claude Code, Opus 5.5; adendo 5, A5.4, A5.5 e A5.9)

**Antes dos números:**
- **os critérios e as margens** são os da A5.4, copiados da espec (seção 7.3), **PROPOSTOS e SEM FONTE.** A LS-7 os aprovou sem mudá-los,
  e nada aqui os ajusta. Cada um é lido como está registrado, pelo `criterios` do orquestrador do #438;
- **a leitura não afirma** que a L-2 conserta o longe, que o modular supera o A (o A11 não está na avaliação) nem que algum cérebro está
  pronto (a espec, seção 8);
- **o par M0 × M0+S é só descritivo** (a LS-6), sem critério;
- **as S-1 a S-6** são leituras, sem critério próprio; a S-1 e a S-2 entram no C-L2-4, e a S-5 no C-L2-3.

**Como rodou:**
- **o comando:** `experiments/run_v2_digibrain_l2.py --config experiments/configs/v2_digibrain_prototipo/l2_avaliacao.json --processos 4`,
  do commit `0a27d97` (a `main`), com a árvore limpa (`git_limpo` = true no `meta.json`), uma vez;
- **as vidas:** as bases 67303, 67404 e 67505, com K = 150 por base (450 unidades, a A5.9), os 4 braços nas 12 células, 14 dias:
  **21 600 vidas,** das 16h26 às 21h43 de 2026-10-29 (19 036 s; 19 019 s de parede para as vidas). Nenhum processo caiu;
- **o tempo:** 0,88 s de parede por vida, acima dos 0,61 s do piloto; a run durou cerca de 5 h 17 min, e não as 3,7 h estimadas;
- **as conferências:** toda vida foi rejogada do disco bit a bit (o G1), com o T-CENARIO-1, o G-MECANISMO e o crédito conferidos em cada
  uma;
- **os artefatos,** em `artifacts_v2_digibrain_prototipo/l2/avaliacao/`:
  - o `meta.json` (sha256 `97bd5bcb…b83c`);
  - as 12 partes das medidas, uma por braço e lugar (1 800 vidas e de 16,0 a 17,6 MB cada), com o `medidas_indice.json` (sha256
    `cd276329…761b`, o mesmo do `meta.json`), que guarda o sha256, as vidas e o tamanho de cada parte;
  - o `resultado.json` (sha256 `6c41fda4…7a15`), que a run calculou das partes relidas;
  - as 21 600 vidas ficam fora do git;
- **a leitura:** `experiments/leitura_l2_digibrain.py` relê as 12 partes pelo índice, confere que o `resultado.json` se refaz igual e
  soma as S-1 a S-6 por braço e lugar em `artifacts_v2_digibrain_prototipo/l2/avaliacao_leitura.json` (sha256 `59c1d911…c72a`).

### 12.1 Os critérios (o par primário, M3\*+S − M3\*, 450 unidades)

| # | a medida | M3\* | M3\*+S | a diferença [IC95] | a regra | lido como registrado |
|---|---|---|---|---|---|---|
| **C-L2-1** | buscas trocadas + expiradas por vida, no longe | 25,69 | 18,43 | −7,26 [−7,61; −6,91] | M3\*+S ≤ 12,85 (a metade) e o limite superior < 0 | **não passa:** o IC fica abaixo de 0, mas a queda é de 28 %, e não à metade |
| **C-L2-2** | a taxa por episódio no longe | 0,4264 | 0,4367 | +0,0103 [+0,0032; +0,0174] | o limite inferior > 0 | **passa** |
| **C-L2-3** | as 10 comparações (abaixo) | | | | todas | **passa** |
| **C-L2-4** | as suspensões em "expirou" (S-1) | | 34 de 42 868 (0,08 %) | | ≤ 25 % | sim |
| | meta ou achou: as buscas suspensas contra as nunca suspensas (S-2) | | 0,155 contra 0,840 | | as suspensas ≥ 0,740 | não; **o C-L2-4 não passa** |

**As 10 comparações do C-L2-3:**

| a comparação | margem | M3\* | M3\*+S | a diferença [IC95] | passa |
|---|---|---|---|---|---|
| episódio, comedouro | −0,03 | 0,8160 | 0,8188 | +0,0028 [−0,0022; +0,0079] | sim |
| episódio, perto | −0,03 | 0,9561 | 0,9560 | −0,0001 [−0,0008; +0,0006] | sim |
| ração, comedouro | −0,03 | 0,4209 | 0,4222 | +0,0013 [−0,0027; +0,0053] | sim |
| ração, perto | −0,03 | 0,6893 | 0,6897 | +0,0004 [−0,0008; +0,0016] | sim |
| exaustão, comedouro | +0,02 | 0,1750 | 0,1755 | +0,0005 [−0,0008; +0,0019] | sim |
| exaustão, perto | +0,02 | 0,1564 | 0,1561 | −0,0003 [−0,0007; +0,0001] | sim |
| exaustão, longe | +0,02 | 0,3235 | 0,3165 | −0,0071 [−0,0109; −0,0033] | sim |
| privação, comedouro | +0,02 | 0,1547 | 0,1546 | −0,0001 [−0,0025; +0,0023] | sim |
| privação, perto | +0,02 | 0,1421 | 0,1422 | +0,0001 [−0,0002; +0,0003] | sim |
| privação, longe | +0,02 | 0,5563 | 0,5403 | −0,0160 [−0,0249; −0,0072] | sim |

**Como se leem juntos** (A5.4, como está):
- **a suspensão não segue para o jogo:** pede o C-L2-1, o C-L2-3 e o C-L2-4, e o C-L2-1 e o C-L2-4 não passam
  (`segue_para_o_jogo` = false);
- **o C-L2-2 passa** (`o_longe_melhorou` = true): a taxa por episódio no longe subiu 0,0103, com o IC acima de 0. A A5.4 não diz o que
  fazer com o C-L2-2 passando e o C-L2-1 e o C-L2-4 falhando; a leitura volta ao Matheus (12.6).

**A regra da parte (a)** (A5.5, como está): pede o C-L2-1 e o C-L2-3, as trocas por outra unidade com ração a menos de R no longe acima
do dobro das do comedouro, e o C-L2-2 sem melhora. As trocas são 18,39 por vida no longe e 1,84 no comedouro (acima do dobro), mas o
C-L2-1 não passa e o C-L2-2 passa: **a (a) não volta ao Matheus pela regra** (`volta_ao_matheus` = false).

**Ao lado, sem critério:** a taxa por ração no longe, 0,0802 no M3\* e 0,0819 no M3\*+S, +0,0017 [−0,0008; +0,0042] (o teto de cerca de
0,13 declarado na espec).

### 12.2 O mecanismo (por vida, 1 800 vidas por braço e lugar)

| | M3\* longe | M3\*+S longe | M3\* comedouro | M3\*+S comedouro | M3\* perto | M3\*+S perto |
|---|---|---|---|---|---|---|
| buscas trocadas pelo reflexo | 20,55 | 0 | 1,90 | 0 | 0,07 | 0 |
| buscas trocadas por outra unidade, com ração a menos de R | 5,13 | 18,39 | 0,61 | 1,84 | 0,04 | 0,06 |
| buscas expiradas | 0 | 0,018 | 0 | 0,001 | 0 | 0 |
| o C-L2-1 | 25,69 | 18,43 | 2,51 | 1,84 | 0,11 | 0,06 |
| intenções suspensas que acabaram | 0 | 19,85 | 0 | 3,59 | 0 | 0,38 |
| retomadas | 0 | 24,01 | 0 | 3,73 | 0 | 0,20 |

**Os fins das buscas no longe,** somados nas 1 800 vidas: no M3\*, 81 435 buscas (achou 32 643, trocou 46 243, sumiu 2 528, desistiu
21); no M3\*+S, 70 779 (achou 34 268, trocou 33 138, sumiu 3 034, saciou 256, desistiu 51, expirou 32).

**Quem venceu a busca trocada no longe:** no M3\*, o dormir em 38 859 das 46 243 (o reflexo e o sorteio juntos); no M3\*+S, o chamar a
atenção em 9 432, o explorar um ponto em 7 067, o dormir pelo sorteio em 6 911, o explorar vagando em 4 686 e o explorar pelo cheiro em
4 632 das 33 138.

### 12.3 As S-1 a S-6 no M3\*+S (só leitura)

| | longe | comedouro | perto |
|---|---|---|---|
| **S-1:** suspensões que acabaram | 35 724 | 6 456 | 688 |
| S-1: o `n_susp` médio (decisões de reflexo somadas) | 1,49 | 1,29 | 1,19 |
| S-1: a fração em "expirou" | 0,0009 | 0,0003 | 0 |
| **S-2:** meta ou achou, as buscas suspensas | 0,139 (29 654) | 0,300 (3 190) | 0,235 (115) |
| S-2: meta ou achou, as buscas nunca suspensas | 0,733 (41 125) | 0,948 (21 851) | 0,995 (13 360) |
| **S-3:** o andado líquido médio da retomada até o fim, em passos | 0,150 | 0,085 | 0,020 |
| S-3: a fração com o andado ≤ 0 | 0,821 | 0,918 | 0,980 |
| **S-4:** retomadas com um reflexo nas 2 decisões seguintes | 0,865 | 0,804 | 0,724 |
| **S-5:** a exaustão por vida (no M3\*) | 0,316 (0,324) | 0,176 (0,175) | 0,156 (0,156) |
| S-5: a privação por vida (no M3\*) | 0,540 (0,556) | 0,155 (0,155) | 0,142 (0,142) |
| **S-6:** retomadas em que a persistência decidiu | 0,238 | 0,261 | 0,159 |

- **A S-2 do orquestrador conta só as buscas** (`comer/cheiro`); a S-1 conta as suspensões de toda intenção, a busca e a ida.
- **As buscas nunca suspensas do M3\*+S não são as buscas do M3\*:** são as que nenhum reflexo interrompeu. No longe, a fração de meta ou
  achou de todas as buscas do M3\* é 0,401.

### 12.4 O par descritivo, M0+S − M0 (sem critério; a LS-6)

| a medida | M0 | M0+S | a diferença [IC95] |
|---|---|---|---|
| o C-L2-1, no longe | 21,91 | 15,35 | −6,57 [−6,88; −6,25] |
| episódio, longe | 0,4636 | 0,4726 | +0,0090 [+0,0028; +0,0152] |
| episódio, comedouro | 0,7079 | 0,7191 | +0,0112 [+0,0048; +0,0175] |
| episódio, perto | 0,9071 | 0,9075 | +0,0004 [−0,0013; +0,0021] |
| ração, comedouro | 0,2473 | 0,2515 | +0,0043 [+0,0003; +0,0083] |
| ração, perto | 0,5313 | 0,5314 | +0,0001 [−0,0017; +0,0019] |
| exaustão, comedouro | 0,1785 | 0,1752 | −0,0033 [−0,0054; −0,0011] |
| exaustão, perto | 0,1483 | 0,1482 | −0,0001 [−0,0007; +0,0006] |
| exaustão, longe | 0,2759 | 0,2731 | −0,0027 [−0,0056; +0,0001] |
| privação, comedouro | 0,2047 | 0,1919 | −0,0128 [−0,0203; −0,0053] |
| privação, perto | 0,1254 | 0,1257 | +0,0002 [−0,0003; +0,0007] |
| privação, longe | 0,5768 | 0,5685 | −0,0083 [−0,0156; −0,0010] |

No M0+S, as S seguem a mesma forma do M3\*+S: no longe, a S-2 dá 0,192 contra 0,757 e a S-4 dá 0,835 (`avaliacao_leitura.json`).

### 12.5 A leitura (descritiva, pós hoc; nenhum critério novo)

- **O reflexo saiu das trocas da busca,** de 20,55 por vida a 0 no longe, como a forma de medir da A5.3 previa. **As trocas por outra
  unidade subiram,** de 5,13 a 18,39, e o C-L2-1 caiu 28 %, e não à metade.
- **A busca retomada volta a ser interrompida:** em 86 % das retomadas do longe, outro reflexo vem nas 2 decisões seguintes (S-4); o
  andado líquido até o fim fica em 0,15 passo, e em 82 % delas é ≤ 0 (S-3). As buscas suspensas acabam em meta ou achou em 14 %, contra
  73 % das nunca suspensas (S-2), e quase nenhuma expira (S-1). Pela LS-3, a retomada passa pelo sorteio, e as vencedoras da troca no
  M3\*+S são o chamar a atenção, o explorar e o dormir pelo sorteio.
- **O C-L2-2 e o C-L2-3 passam:** a taxa por episódio no longe sobe 0,0103, e nenhuma das 10 comparações piora além da margem; a exaustão
  e a privação no longe descem um pouco.
- **Esta leitura não diz** por que a busca retomada perde no sorteio, nem quanto do +0,0103 vem da suspensão e quanto do aprendizado que
  ela muda. O par M0 × M0+S, sem o aprendizado do M3\*, mostra uma diferença da mesma ordem, só descritiva.

### 12.6 O que fica para o Matheus

- **A suspensão não segue para o jogo** pela regra da A5.4 (o C-L2-1 e o C-L2-4 não passam).
- **A parte (a) não volta pela regra da A5.5.** A A5.4 não prevê o caso do C-L2-2 passando com o C-L2-1 e o C-L2-4 falhando: o próximo
  passo da L-2 (parar, uma espec nova, ou outra coisa) é dele.
- **Os limiares** seguem PROPOSTOS, SEM FONTE; nada aqui os muda.

## 13. A C1, o longe regular (2026-10-31, worker da C1, etapa 3b, Claude Code, Opus 5.5; adendo 6, A6.4 a A6.8)

**Antes dos números:**
- **as regras** são as do adendo 6 (APROVADO em 2026-10-30), lidas como estão: o primário de A6.4, a classe de A6.6 com a margem
  δ = 0,022, a regra de leitura de A6.7 e os descritivos de A6.8. **Todo número é PROPOSTO,** e os limiares (a margem, os 3 lugares, o
  0,15 da C5, o −0,5 do g1) são SEM FONTE externa (A6.11);
- **é a repetição da mesma validação** (A6.15): a run de A6.13 caiu pelo orquestrador (#507) sem gravar nenhum resultado, o #508
  consertou só a lista de fins (A6.14), e a run rodou de novo, uma vez, com a mesma config e as mesmas sementes;
- **a leitura não afirma** que o modular supera o A (o A11 não está na run), que o protótipo está pronto, nem um tamanho de efeito fora
  das condições da run (o `nao_demonstra` do `resultado.json`).

**Como rodou:**
- **o comando** de A6.13 e A6.15, do commit `7683c0e` (o registro de A6.15, empurrado antes da primeira vida), com a árvore limpa
  (`git_limpo` = true), 4 processos, depois da suíte e sem sobrepor (V3-D8);
- **as vidas:** as 150 unidades da faixa 71101…71505 × 3 braços × 8 células, 14 dias: **3 600 vidas,** das 14h18 às 15h22 de 2026-10-31
  (3 842 s). Nenhum processo caiu; o orquestrador saiu com 0;
- **as conferências da run:** toda vida rejogada do disco bit a bit (o G1, `orq.conferir_replay`), o corpo do replay igual ao que o
  cérebro viu, a LP-2 (nenhum `retomou` nem `n_susp`) e os fins de intenção (nenhum fora de `MOTIVOS_FIM`), todas falhando alto; a
  contagem de 3 600 vidas conferida no fim;
- **a conferência com a run caída** (A6.15): os 3 268 logs de vida de `caido_1/vidas/` têm o mesmo sha256 que os logs de mesmo nome da run
  nova (3 268 iguais, 0 diferentes, 0 faltando; o `conferencia_caido_1.json`). O `caido_1/` não foi mexido e não entra em nenhum cálculo;
- **os artefatos,** em `artifacts_v2_digibrain_prototipo/longe_regular/run/`:
  - o `meta.json` (sha256 `b2cb111a…4770`), com o `git_head` `7683c0e`, o sha256 da config (`9996cf83…20c9`), do orquestrador
    (`59b90341…7473`), do plano com A6.15 (`449ac0b5…47d0`) e dos módulos;
  - o `medidas.json` (sha256 `5a4fb207…722d`, 32,7 MB) e o `resultado.json` (sha256 `b1872745…1209`), os mesmos do `meta.json`;
  - o `run.log` (a saída da run, em LF; sha256 `71eb06b8…9bf8`), o `conferencia_caido_1.json` (sha256 `95eac333…881d`) e o
    `vidas.tar.gz` com as 3 600 vidas (sha256 `a1fb0010…f7ee`, 18,0 MB).

### 13.1 O primário (A6.4): M3\* − M2 por episódio, nas 4 células do `longe_fixo`, 150 unidades

| a medida | o valor |
|---|---|
| a média das diferenças por unidade | **+0,0489** |
| o IC95 pelo t (gl 149) | **[+0,0355; +0,0624]** |
| o t e o p unilateral | 7,20; 1,4 × 10⁻¹¹ |
| o g1 das 150 diferenças | +0,115 (acima de −0,5: sem a ressalva da assimetria) |
| o IC95 percentil do bootstrap (a convenção da seção 5.2.1, anticonservadora com 5 bases, A4.4) | [+0,0399; +0,0581] |
| a margem efetiva (o menor efeito com poder 0,8 pelo dp observado) | 0,019 (a planejada: 0,022) |
| **passa** (o limite inferior acima de 0) | **sim** |
| **a classe** (A6.6) | **"> 0"** (o IC inteiro acima de 0 e fora de (−0,022; +0,022)) |

**As premissas** (A6.4) passam as duas, e o primário é **conclusivo:**
- **G-PESA da memória** (no M3\*, nas 4 células do `longe_fixo`, a fração das decisões com `memoria_decidiu`): **0,122 [0,116; 0,127]**,
  acima de 0,01;
- **G-ELEGIVEL-EP:** **0,942** das 600 vidas do M3\* no `longe_fixo` com 3 episódios ou mais, acima de 0,80.

### 13.2 A C1-E1: a previsão por nível de regularidade (A6.1)

| nível | o lugar da ração | a previsão | o que saiu (M3\* − M2 por episódio) | a previsão |
|---|---|---|---|---|
| um lugar | o comedouro | > 0 | **não rodou de novo:** o registrado na reavaliação, +0,137 [0,114; 0,160] por episódio (A6.1) | confirmada antes |
| poucos lugares (3) | o `longe_fixo` | > 0 | **+0,0489 [+0,0355; +0,0624], "> 0"** (13.1) | **confirmada** |
| nenhum | o longe sorteado | ≈ 0 | **−0,0106 [−0,0236; +0,0024], "indeterminado"** | **não confirmada** |

**O sorteado, como está:** o IC cruza o 0 e passa da margem por baixo (o limite inferior, −0,0236, fica 0,0016 abaixo de −0,022). Pela
regra de A6.6 a classe é **"indeterminado"**: nem o "≈ 0" que a C1-E1 previa, nem o "< 0" da 66xxx (−0,031 [−0,051; −0,012]), que a
simulação de A6.6 dizia que se repetiria. **A previsão "≈ 0" do sorteado é registrada como não confirmada,** e a margem e a regra não
mudam (AD6-3). O dp observado entre as unidades é 0,0805.

### 13.3 A regra de leitura (A6.7) e a C1-E2

- **A linha:** `longe_fixo` "> 0" e sorteado "indeterminado". Nenhuma das duas linhas da seção 1.3 da tarefa se aplica (as duas pedem o
  sorteado "≈ 0"). Pelo complemento de A6.7, a linha é a do **"indeterminado (em qualquer dos dois)": registrado como indeterminado; nada
  se decide com ele** (a `leitura.linha` do `resultado.json`).
- **A C1-E2:** a L-3 só ganha tarefa com o primário "> 0" e o sorteado "≈ 0". **A L-3 fica fora** (`l3_ganha_tarefa` = false).
- **A terceira linha da seção 1.3 (a distância domina): não** (`distancia_domina` = false). No M0, a leitura principal, a diferença
  `longe_fixo` − longe por faixa de d₀ é "> 0" na visão (+0,027 [+0,005; +0,049]) e só no cheiro (+0,061 [+0,039; +0,084]) e
  "indeterminado" além do cheiro (+0,005 [−0,028; +0,038]); nenhuma faixa fica "≈". **Com a ressalva da geometria (A6.2):** o
  `longe_fixo` fica todo a leste do comedouro e ancora no comedouro, e o sorteado ancora no pet e usa as 16 direções; a diferença entre os
  estilos mistura a regularidade com o lado do mapa e com a âncora, e a faixa de d₀ só separa a distância.
- **A persistência:** o adendo 6 não registra leitura nem premissa da persistência (a `intencao_suspensa` estava desligada). A G-PESA do
  módulo da persistência sai só como descritivo (0,005 no M3\* do `longe_fixo`), e nada se lê dela.

### 13.4 Os descritivos (A6.8, sem gate; nenhum muda 13.3)

Todos com o IC95 do t sobre as 150 unidades. **Os contrastes entre braços usam só medidas da vida inteira;** os subgrupos que o próprio
mecanismo cria saem só por braço (a LP-2).

**1. A taxa por faixa de d₀** (somas sobre as 600 vidas de cada estilo e braço; o n de episódios e a taxa):

| faixa de d₀ | `longe_fixo` M0 | M2 | M3\* | longe M0 | M2 | M3\* |
|---|---|---|---|---|---|---|
| na visão | 3 411, 0,844 | 1 677, 0,899 | 1 870, 0,897 | 2 409, 0,814 | 1 315, 0,881 | 1 279, 0,870 |
| só no cheiro | 4 996, 0,462 | 4 840, 0,512 | 5 078, 0,558 | 5 314, 0,394 | 5 233, 0,423 | 4 803, 0,405 |
| além do cheiro | 1 207, 0,175 | 1 377, 0,214 | 1 278, 0,250 | 1 389, 0,179 | 1 618, 0,205 | 1 290, 0,215 |

A diferença `longe_fixo` − longe por faixa no M2 e no M3\* (com a ressalva da LP-2): M2 +0,014 [−0,011; +0,039] na visão, +0,079
[+0,058; +0,101] no cheiro e +0,015 [−0,020; +0,050] além; M3\* +0,026 [−0,002; +0,054], +0,146 [+0,122; +0,170] e +0,044 [+0,005;
+0,083]. Nenhuma unidade ficou fora de uma faixa.

**2. As visitas ao lugar lembrado** (só o M3\*; a regra corrigida da DX-1, com a v1 ao lado):

| estilo | vidas | visitas | vazias (a v1) | a fração que acha |
|---|---|---|---|---|
| `longe_fixo` | 600 | 12 704 | 12 704 (12 704) | **0,000** |
| longe | 600 | 21 954 | 21 942 (21 954) | 0,0005 |

**3. As trocas de meta** (por vida, a LP-2; o `desistiu` à parte, A6.14):
- **as trocas por vida:** `longe_fixo` M0 16,6, M2 18,3, M3\* 46,1; longe M0 26,5, M2 28,9, M3\* 75,9. M3\* − M2: +27,9 [+26,4; +29,3]
  no `longe_fixo` e +47,0 [+45,5; +48,6] no longe; M2 − M0: +1,6 [+1,1; +2,1] e +2,4 [+1,7; +3,0];
- **a ida ao lugar lembrado** (só o M3\*; somas): no `longe_fixo`, 12 704 terminam em `meta` e 17 603 em `trocou` (pelo reflexo 14 023,
  pelo dormir sorteado 1 026, por outra unidade 2 554); no longe, 21 954 e 27 177 (22 975, 1 072 e 3 130);
- **as buscas pelo cheiro** (somas de `achou`, `trocou`, `sumiu` e `desistiu`): `longe_fixo` M0 10 347, 7 871, 414, 11; M2 9 465, 8 835,
  452, 11; M3\* 8 409, 7 970, 322, 11; longe M0 13 463, 13 228, 1 073, 7; M2 12 790, 14 542, 1 075, 7; M3\* 10 917, 15 701, 927, 6.
  Nenhum `expirou` (a suspensa desligada).

**4. As medidas da C5** (do replay; os cinco estados abaixo de 0,15; DECIDIDAS, AD6-4, SEM FONTE):

| medida | janela | `longe_fixo` M3\* − M2 | `longe_fixo` M3\* − M0 | longe M3\* − M2 | longe M3\* − M0 |
|---|---|---|---|---|---|
| a fração do tempo com algum estado fora | a vida | −0,025 [−0,032; −0,018] | −0,052 [−0,061; −0,044] | +0,041 [+0,030; +0,052] | +0,001 [−0,009; +0,011] |
| | dias 8 a 14 | −0,040 [−0,052; −0,027] | −0,092 [−0,106; −0,078] | +0,054 [+0,037; +0,072] | −0,023 [−0,040; −0,006] |
| a menor necessidade, média | a vida | +0,011 [+0,008; +0,014] | +0,021 [+0,018; +0,025] | −0,014 [−0,019; −0,010] | +0,001 [−0,003; +0,005] |
| | dias 8 a 14 | +0,017 [+0,012; +0,022] | +0,037 [+0,032; +0,043] | −0,018 [−0,025; −0,010] | +0,012 [+0,005; +0,019] |
| a menor necessidade, mínimo | a vida | +0,008 [+0,004; +0,011] | +0,015 [+0,011; +0,019] | 0,000 [0,000; 0,000] | 0,000 [0,000; 0,000] |

Os níveis da fração fora, na vida: `longe_fixo` M0 0,400, M2 0,373, M3\* 0,348; longe M0 0,446, M2 0,406, M3\* 0,447. A privação de hoje
(as decisões; fome, higiene e energia), ao lado: `longe_fixo` 0,453, 0,406, 0,366; longe 0,580, 0,513, 0,548. No longe, o mínimo da menor
necessidade fica em 0 (até a quarta casa) nos três braços.

**5. Os outros descritivos:**
- **a taxa por episódio:** `longe_fixo` M0 0,534, M2 0,510, M3\* 0,559; longe M0 0,466, M2 0,451, M3\* 0,440. M2 − M0: −0,025 [−0,039;
  −0,011] no `longe_fixo` e −0,015 [−0,030; −0,001] no longe; M3\* − M0: +0,024 [+0,010; +0,039] e −0,026 [−0,039; −0,013];
- **o efeito da regularidade** (`longe_fixo` − longe, pareado por unidade, com a ressalva da geometria): M0 +0,069 [+0,046; +0,091], M2
  +0,059 [+0,036; +0,083], M3\* +0,119 [+0,096; +0,141];
- **a taxa por ração** (a PL-3: no longe ela não informa): M3\* − M2 +0,040 [+0,034; +0,047] no `longe_fixo` e −0,005 [−0,009; 0,000] no
  longe; com a W(d), +0,037 [+0,030; +0,044] e −0,018 [−0,023; −0,012];
- **a G-PESA por módulo** (M2 e M3\*, no `longe_fixo` e no longe): a memória 0 e 0,122, 0 e 0,191; o aprendido 0,125 e 0,226, 0,115 e
  0,255; o hábito 0,120 e 0,116, 0,111 e 0,089; o afeto, o incentivo e a persistência abaixo de 0,015 em todos;
- **os episódios por vida:** `longe_fixo` M0 16,0, M2 13,2, M3\* 13,7; longe 15,2, 13,6 e 12,3. **A exaustão:** `longe_fixo` 0,225,
  0,225 e 0,236; longe 0,275, 0,271 e 0,320;
- **por dono:** só no `resultado.json` (`descritivo.outros.por_dono`), sem leitura.

### 13.5 O que é verificado, o que é resultado e o que é interpretação

- **Verificado por testes e hashes:** a suíte antes da run (43 falhas, todas dos hooks; nenhuma do G1, do G2 ou do G-MECANISMO, A6.10); o
  replay bit a bit de cada vida; a LP-2 e os fins de intenção em cada vida; as 3 600 vidas; os 3 268 logs iguais aos do `caido_1/`; o
  `meta.json` com o commit, a árvore limpa e os sha256 de A6.15.
- **Resultado** (do `resultado.json`, pelas regras do adendo 6): 13.1 a 13.4.
- **Interpretação** (do worker, não testada, PROPOSTA):
  - no `longe_fixo` a memória ajuda por episódio, com cerca de um terço do efeito do comedouro (+0,049 contra +0,137), acima da margem.
    Com a ração em 3 lugares fixos, o M-MEM deixa de atrapalhar e passa a ajudar. Isso vai na direção de Giannakakis et al. (2023) e de
    Khan e Cañamero (2018), que dão a direção e não o tamanho (A6.11);
  - **o ganho não vem de achar a ração no lugar lembrado:** das 12 704 visitas no `longe_fixo`, nenhuma achou ração. O caminho do ganho
    fica em aberto. Uma leitura possível, **não testada e que a LP-2 não deixa virar contraste,** é que a ida ao lugar lembrado deixa o
    pet perto dos 3 pontos fixos quando a ração cai (no M3\*, a taxa do `longe_fixo` só no cheiro é 0,558, contra 0,512 no M2);
  - no sorteado, a run não separa um efeito pequeno negativo de nenhum: o IC fica entre −0,024 e +0,002;
  - **a C1 não mostra que o modular é superior** a nada além do M2 nestas condições: o A11 não rodou. O M3\* também troca de meta muito
    mais (+28 por vida no `longe_fixo`) e tem mais exaustão no longe.
