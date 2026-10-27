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
