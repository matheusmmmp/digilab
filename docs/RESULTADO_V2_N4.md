# Resultado — V2, N4: frutas no mundo, sem aprendizado de política (validação única, 2026-10-04)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Plano `docs/PLANO_ANALISE_V2_N4.md` (commitado antes de qualquer run); definições `docs/DEFINICOES_FRUTAS_V2.md` (F1–F11); calibração no
PR #132 (`artifacts_v2_n4/calibracao/`, que **não fechou**). Validação: sementes **11101…11505, uma vez**, no ponto da calibração
(`w_fruta` 6, `k_saciedade` 1,0, duração 120; `experiments/configs/v2_n4/validacao.json`). Números de `artifacts_v2_n4/validacao/`
(`resultado.json`, `vidas.json`, `so_cuidado.json`, `meta.json`). Nada mudou por causa da validação.

## Gates

| gate | critério | resultado |
|---|---|---|
| G1 replay | vida bit a bit pelo log | **passa** (o orquestrador conferiu as 60 vidas, as 20 do acoplado e as 20 sem carinho; `tests/test_frutas.py`) |
| G2 equivalência | desligado = motor de antes, byte a byte | **passa** (`tests/test_frutas.py`: V3, instinto da v1, ligado sem oferta, a vida da A1 com a bola) |
| **G-SEP** | (i) e (ii) com limite inferior do IC > 0 | **FALHA** pela (ii). (i) comer ou não pelo incentivo, na mesma faixa de fome: **+0,094 [+0,049; +0,136]** (passa). (ii) qual fruta: **+0,110 [−0,007; +0,213]** (falha por 0,007; por semente +0,121, +0,275, +0,116, +0,136, −0,095) |
| **G-SSE** | IC de β_recente < 0 e IC de β_fome contendo 0 | **FALHA** pelo β_fome. β_recente **−0,778 [−0,901; −0,635]** (passa); β_fome **−0,070 [−0,159; −0,014]** (não contém 0) |
| **G-F7** | IC da saúde frutas − acoplado contendo 0, mortes iguais | **PASSA**: −0,004 [−0,008; 0,000]; mortes 0 e 0 |

## Por que o G-SSE falha (e o que isso diz)

A avaliação de uma fruta é `max(0, preferência inata − k × consumo recente daquela fruta)`: a fome não entra na conta (código em
`digilab/frutas.py`, `MotorFrutas._comer`; teste `tests/test_frutas.py::test_avaliacao_cai_com_o_consumo_recente_da_fruta_e_nao_com_a_fome`, em
que a mesma fruta com fome 0,2 e 0,6 dá a mesma avaliação). A regressão do plano, `avaliacao ~ 1 + recente + fome`, **não tem o termo da
preferência inata**, que varia de fruta para fruta e de genoma para genoma; o β_fome capta a parte da preferência que anda junto com a fome
na hora de comer. É uma falha da **medida pré-registrada**, não do mecanismo, e já aparecia na calibração (β absurdos nos pontos com poucos
consumos; `docs/REGISTRO_DESVIOS.md`). A próxima medida da saciedade precisa pôr a preferência no modelo, ou medir a queda
`preferência inata − avaliação`.

## Por que o G-SEP(ii) falha

Por vida há de 4 a 24 escolhas com duas frutas ou mais no cenário (o relapso, de 4 a 16), e uma semente sai negativa (11505, −0,095). A
escolha é proporcional ao incentivo, então a fruta de maior incentivo ganha só quando a diferença entre os incentivos é grande; com
incentivos parecidos a escolha fica perto do acaso. O efeito é do tamanho esperado, a amostra é que não basta.

## Descritivos

| medida | valor |
|---|---|
| p(comer \| fruta no cenário, tempo livre) | 0,208 [0,171; 0,240] (a faixa do plano, 0,30 a 0,80, não foi alcançada) |
| fração dos consumos na fruta que faz mal (descasado) | 0,389 [0,365; 0,415] (três frutas) |
| **custo do descasado**: humor descasado − efeito igual | **−0,023 [−0,030; −0,014]** |
| G-SEP(i) no mundo de efeito igual | +0,101 [+0,064; +0,139] |
| privação frutas − sem frutas | −0,011 [−0,021; −0,003] (as frutas alimentam) |
| humor frutas − sem frutas | −0,013 [−0,026; +0,006] |
| saúde final frutas − sem frutas | −0,015 [−0,031; −0,001] |
| saúde frutas − acoplado sem carinho | +0,022 [−0,022; +0,075] |
| mortes | 0 em todos os braços |

## Leitura

1. **As frutas criam uma escolha que a fome sozinha não explica**, no nível de "comer ou não": na mesma faixa de fome, o pet come mais quando
   o incentivo é alto (G-SEP(i) passa na calibração e na validação). No nível de "qual fruta", o efeito tem o sinal certo e falta amostra.
2. **O canal de cuidado não aparece entre braços com as mesmas ofertas** (G-F7 passa, sem mortes), mas **as frutas em si alimentam**: com
   elas a privação cai um pouco. Elas não são neutras para o cuidado, como a definição 2.6 avisava.
3. **O mundo descasado já cobra seu preço** sem aprendizado: o pet come a fruta que faz mal em quase 40% dos consumos e o humor cai.
   Nada o afasta dela, porque o incentivo segue o gosto e não o efeito. É a linha de base para o N3 (aprender pela consequência).

## Decisões para o Matheus

**Decididas pelo Matheus em 2026-10-04 (recomendação do coordenador):**
- **N1 = (a):** a falha do G-SSE fica como falha da medida. O próximo plano troca a regressão (com o termo da preferência inata, ou medindo
  a queda da avaliação por fruta). Nada de releitura pós hoc agora.
- **N2:** ampliar a grade de `w_fruta` na calibração do experimento maior, porque o P1 precisa de exposição à fruta para aprender
  (p(comer | fruta) foi 0,208).
- **N3:** manter a nutrição. O acoplado com as mesmas ofertas já controla isso, e zerar mudaria o mundo de novo.
- **N4:** a herança dos genes das frutas fica para quando a linhagem usar frutas (fase 3).

| # | decisão | opções |
|---|---|---|
| N1 | A medida da saciedade (G-SSE) | (a) aceitar a falha como da medida e trocar a regressão no próximo plano (pôr a preferência inata ou medir a queda); (b) reler os dados gravados com o modelo corrigido, como análise pós hoc rotulada |
| N2 | A faixa de p(comer) e o peso da fruta | aumentar a grade de `w_fruta` no próximo uso, ou aceitar que o pet come pouca fruta com o instinto atual |
| N3 | A nutrição das frutas | manter (as frutas também alimentam, e o acoplado com as mesmas ofertas controla isso) ou zerar a nutrição para isolar o gosto |
| N4 | A herança dos genes das frutas | deixar para quando a linhagem usar frutas, ou levar ao `Genitor` agora |
