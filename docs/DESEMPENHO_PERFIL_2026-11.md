# Desempenho das runs de pesquisa: onde vai o tempo, e PyPy, NumPy/Polars, orjson/msgspec (2026-11-08)

Tarefa: `docs/TAREFA_V3_DESEMPENHO.md`. Só medição e proposta: nada mudou no motor, no cérebro, no `digilab/` nem nas regras. Todas as
vidas usam as sementes dos testes (101, 202, 303, 404 e 505), nunca uma faixa reservada. As decisões da seção 7 são do Matheus.

## 1. Em uma tela

- **O tempo de uma vida de pesquisa está na simulação, não no log nem na análise.** Na vida da C4, o cérebro tem 36 %, o corpo 35 % e o
  motor com o mundo 20 %. O json com o gzip fica em 1,6 % e as métricas em 1,4 %.
- **O replay G1 custa tanto quanto viver.** Cada vida é vivida e depois refeita do log: 1,27 s + 1,30 s de 2,73 s.
- **PyPy: 1,72× mais rápido depois do aquecimento, com as mesmas vidas.** O log, o estado interno do cérebro e o resumo do motor saem
  idênticos nas 5 sementes. Mudam só as medidas no último dígito, porque o `sum()` de floats do PyPy é ingênuo e o do CPython 3.12+ é
  compensado. Com isso, 36 testes falham só no PyPy: os gabaritos byte a byte e os artefatos que "se refazem iguais".
- **A análise inteira da C4 (14 400 vidas) leva ~23 s** de uma run de 3,2 h. NumPy ou Polars não têm o que ganhar ali. Os dois pontos
  quentes são algoritmos que se resolvem na biblioteca padrão.
- **O json e o gzip do log somam ~5 ms por vida (0,2 %).** O orjson e o msgspec leem 5× mais rápido, mas não escrevem o formato do log
  (os separadores `", "` e `": "`). Trocar a escrita mudaria o sha256 de todo log. Na leitura, o ganho é de ~1 ms por vida.
- **Achado:** o resultado já depende da versão do CPython. A regra diz "Python 3.10 ou mais novo", e o 3.10 e o 3.11 somam como o PyPy
  (seção 6).

## 2. Como foi medido

- **O script:** `experiments/medir_desempenho_perfil.py` (modos `perfil`, `tempo`, `analise`, `logs`, `comparar` e `gabaritos`; o
  docstring diz o que cada um faz).
- **A vida medida:** a vida de pesquisa típica do cérebro modular, a da C4 (`run_v2_memoria_autobio._vida`), aberta em fases:
  - viver;
  - gravar o log;
  - o replay G1 (`conferir_replay`);
  - as conferências e as medidas.
  É o braço REL com o dono atencioso, no `longe_fixo`, por 14 dias e 16 interações por dia: 1 563 eventos e 76 657 bytes de log na
  semente 101.
- **Os interpretadores:**
  - CPython 3.13.0, o mesmo da C4 (`meta.json` da run);
  - PyPy 3.12 v8.0.1 (Python 3.12.15). O zip veio de downloads.python.org, com o sha256 conferido, e foi aberto em
    `D:\Trab\digilab\_ferramentas\`, fora do PATH. O Matheus autorizou o download.
  - o orjson 3.13.0 e o msgspec 0.22.0 ficaram num venv separado (`_ferramentas\venv-json`).
- **A máquina:** um processo de medição por vez, sem outra run rodando. O i7-14700KF tem núcleos P e E, e o mesmo processo foi de 2,95 s
  para 4,91 s por vida quando o Windows o trocou de núcleo. Por isso os tempos da seção 4 rodaram com a afinidade do processo fixada num
  núcleo P (`ProcessorAffinity = 4`, só no processo; nada no sistema mudou).

## 3. Onde vai o tempo de uma vida (CPython, cProfile, semente 101)

Artefato: `artifacts_v3_desempenho/perfil_vida_101/medida.json`. Também há um `.prof` e o top 30 por fase. O tempo de cada função da
biblioteca padrão e de cada builtin vai para a categoria de quem a chamou.

| categoria | arquivos | s (com profiler) | % |
|---|---|---|---|
| cérebro | `digilab/digibrain/`, `policies/lobos.py` … | 2,42 | 35,6 |
| corpo | `corpo.py`, `corpo_grafo.py`, `motor_corpo.py` … | 2,41 | 35,5 |
| motor e mundo | `engine.py`, `mundo.py`, `state.py` … | 1,39 | 20,4 |
| fala | `digilab_fala_livre/` (nas medidas) | 0,20 | 3,0 |
| orquestrador | `experiments/run_v2_*` | 0,16 | 2,4 |
| json e gzip | `json`, `gzip` | 0,11 | 1,6 |
| métricas | `digilab/metrics.py` | 0,09 | 1,4 |
| log de eventos | `digilab/events.py` | 0,01 | 0,1 |

- **Por fase, com o profiler:** viver 3,32 s, replay G1 3,36 s, conferências e medidas 0,36 s, gravar o log 0,012 s.
- **Sem o profiler** (`artifacts_v3_desempenho/tempo_cpython.json`, 5 sementes × 2 repetições), a mediana é 2,73 s por vida: viver
  1,27 s, replay 1,30 s, medidas 0,10 s.
- **As funções mais caras ao viver** (`perfil_vida_101/viver_top30.txt`):
  - o `corpo.passo` (0,73 s acumulado, 20 160 chamadas);
  - o `dataclasses.replace` (0,32 s, 73 900 chamadas);
  - o `mem.lembrar` (0,50 s);
  - o `lobos.div_arred` (426 mil chamadas).
  É Python puro do começo ao fim, o perfil em que um JIT ajuda.
- **Na C4 inteira** (`D:/Trab/digilab/v3-memoria-run/artifacts_v2_digibrain_prototipo/memoria_autobio/run/meta.json`): 14 400 vidas em
  4 processos levaram 11 608,8 s, dos quais 11 597,6 s nas vidas. A análise e a escrita levaram ~11 s (0,1 %).

## 4. PyPy

### 4.1 As vidas saem iguais?

Artefato: `artifacts_v3_desempenho/comparacao_cpython_pypy.json`, que o modo `comparar` gera de `tempo_cpython.json`, `tempo_pypy.json`,
`medidas_cpython/` e `medidas_pypy/`.

- **Iguais nas 5 sementes:** o sha256 do log, o do `estado_interno()` do cérebro e o do `resumo_motor`. Ou seja, as mesmas decisões, o
  mesmo log e o mesmo estado final.
- **Diferentes nas 5 sementes:** as medidas, sempre no 15º ou 16º dígito. Mudam o `d_fe` e o `d_fe_vida` em todas as sementes, e o
  `entropia_dia` na 101. Por exemplo, `d_fe` 0.8750279017857142 no CPython e 0.8750279017857151 no PyPy.
- **A causa é o `sum()`.** A sonda que cada artefato grava (`interpretador.sonda_soma`) soma `[0.1]*10 + [1e16, 1.0, -1e16]`: o CPython
  3.13 dá 2.0 e o PyPy dá 0.0. O `math.fsum` dá 2.0 nos dois. O `metrics.py` usa o `sum()` em 192 lugares (por exemplo, o
  `deficit_fome_energia` e a entropia).

### 4.2 A suíte inteira no PyPy

Artefatos:
- `artifacts_v3_desempenho/suite_pypy.txt`;
- `suite_cpython.txt`;
- `suite_falhas_comparadas.txt`;
- `gabaritos_pypy.json` (o modo `gabaritos`).

No PyPy ficaram de fora 2 arquivos que importam pacotes de terceiros: `test_planilha_progressao.py` e `test_sprites_geracao.py`.

| | falhas | passam | puladas |
|---|---|---|---|
| CPython 3.13.0 | 7 | 5 170 | 8 |
| PyPy 3.12 v8.0.1 | 43 | 5 095 | 8 |

As 7 falhas do CPython também falham no PyPy. São varreduras estáticas que acham scripts novos de outras frentes
(`auditoria_pet_vivo.py`, `entradas_dc4.py`) e três artefatos que não se refazem. Já estavam na `main` e não são deste PR. Das 36 que
falham só no PyPy:

| grupo | testes | o que difere |
|---|---|---|
| gabaritos byte a byte | 9 (`test_gabarito_*`, `genoma_g0`, `carater_v11_web`) | as medidas das vidas (a contagem por chave está em `gabaritos_pypy.json`); o log e a trajetória, não |
| "as vidas de hoje saem iguais" | 5 (`pqp_adendo7/8`, `p4_contrato`, `p4_gabaritos`, `genoma_g0` E2) | as medidas que entram na impressão da vida |
| estado interno em float | 4 (`personalidade` ×2, `emocao_habituacao`, `confianca` G1 69001) | o `A_inv` e o `theta` do bandit v1, e o caráter da confiança (por exemplo, `atento` -0.07499999999999997 no CPython e -0.07500000000000002 no PyPy) |
| planejador | 8 (`test_g2_g_plano_zero…`) | só o hash dos `motivos` (os floats do motivo); as ações são iguais |
| artefatos de análise "se refazem iguais" | 9 (`custo_k_l2`, `digibrain_l2`, `l2_k`, `reavaliacao`, `leitura_l2`, `medir_carater_v11`, `painel_v21d`, `motivo_expressao`, `plano_an3_poder`) | floats no último dígito |
| ambiente | 1 (`test_pre_run`, a lista de processos) | a linha de comando do PyPy não tem o que o teste procura |

- **Os 7 gabaritos de vidas, regerados no PyPy** (`gabaritos_pypy.json`, 852 vidas): as chaves `log`, `decisoes` e `estado` são iguais
  em todas as vidas. Só divergem as `medidas`:

  | gabarito | vidas com `medidas` diferentes |
  |---|---|
  | `modular` | 155 de 192 |
  | `conserto` | 227 de 264 |
  | `memoria_autobio` | 52 de 60 |
  | `habito_intencao` | 73 de 80 |
  | `redecidir_evento` | 35 de 40 |
  | `conversa_dc3` | 17 de 20 |

  No `gabarito_digibrain`, a `impressao` difere em 8 de 196 vidas.
- **Nenhuma decisão muda nas vidas testadas.** O que muda são as somas de floats.
- **Mesmo assim, o grupo "estado interno" é um risco real.** No bandit v1 e na confiança, o estado do cérebro já difere no último bit com
  o mesmo log. Numa vida mais longa, um empate quase exato numa comparação pode virar para o outro lado, e a vida diverge.

### 4.3 Velocidade

Artefatos: `tempo_cpython.json` e `tempo_pypy.json`. São as mesmas 5 sementes, o mesmo núcleo P e um processo por vez.

| | por vida | viver | replay G1 | medidas |
|---|---|---|---|---|
| CPython 3.13.0 (10 vidas) | 2,73 s | 1,27 s | 1,30 s | 0,10 s |
| PyPy, vidas 1 a 5 (aquecimento) | 3,76 → 2,32 s | | | |
| PyPy, vidas 11 a 30 (estável) | 1,59 s | 0,65 s | 0,79 s | 0,05 s |
| razão | **1,72×** | 1,96× | 1,64× | 2,05× |

- **Na C4:** a run levou 3,2 h. Na mesma razão, levaria **~1,9 h**. É uma estimativa: supõe que a razão de um processo vale com 4, e não
  mede a memória do PyPy.
- **O aquecimento** (~10 vidas, ~24 s) se dilui nas ~3 600 vidas de cada processo.

### 4.4 Custo de errar

- **Se adotar o PyPy e ele estiver errado:**
  - uma vida de pesquisa diverge do gabarito do CPython por um empate em float (o risco da seção 4.2);
  - todo número de resultado passa a depender do interpretador;
  - os gabaritos de hoje precisariam ser regerados ou ganhar um segundo gabarito;
  - a paridade Python/TypeScript precisaria ser conferida de novo.
- **Se não adotar:** as runs continuam ~1,7× mais lentas, sem risco novo.

## 5. NumPy ou Polars na análise

Artefato: `artifacts_v3_desempenho/analise_c4/medida.json`, com o `.prof` e o top 30. É a análise da C4 sobre o `medidas.json`
gravado, com 14 400 vidas.

- **Ler o `medidas.json`:** o `json.loads` de 138 MB leva 0,78 s, e o `gzip.decompress` 0,17 s.
- **O `analisar`:** 22,8 s com o profiler. O resultado é igual ao `resultado.json` gravado nas 7 chaves.
- **Para onde vai o tempo da análise:** 64 % no orquestrador e 36 % no `metrics.py`. Dois pontos dão ~2/3 do total, e nenhum é conta
  vetorizável:
  - **o `_idx`** do `run_v2_digibrain_prototipo` (7,7 s): o índice das 14 400 vidas é refeito em cada uma das 576 chamadas do
    `por_unidade`. Calcular o índice uma vez basta;
  - **o `quantil_t`** (7,2 s): uma bisseção de 200 passos sobre a beta incompleta em 592 chamadas, com poucos `gl` distintos. Um cache
    por `gl` basta.
- **O bootstrap** (`_medias_bootstrap_agrupadas`) leva 0,9 s.

O ganho máximo do NumPy ou do Polars é, então, uma fração de ~23 s numa run de 3,2 h (< 0,2 %).

**Custo de errar:**
- **Se adotar e estiver errado:**
  - quebra a regra "só biblioteca padrão" e as métricas passam a viver fora do `digilab/metrics.py`;
  - entra uma dependência no CI;
  - o `np.sum` soma em pares e muda o último dígito de toda métrica: todo artefato de análise "se refaz igual" seria regerado.
- **Se não adotar:** perde-se no máximo ~20 s por run.

## 6. orjson ou msgspec nos logs

Artefatos:
- `artifacts_v3_desempenho/logs_cpython.json`;
- `logs_pypy.json`;
- `logs_venv_json.json` (o CPython com o orjson e o msgspec).

O log é o da semente 101, e cada tempo é o melhor de 5.

| por vida (ms) | CPython `json` | orjson | msgspec | PyPy `json` |
|---|---|---|---|---|
| escrever (dumps por linha) | 1,96 | 1,06 | 0,13 | 2,42 |
| ler (loads por linha) | 1,27 | 0,25 | 0,21 | 0,67 |
| `para_jsonl` / `de_jsonl` inteiros | 2,06 / 1,99 | | | 2,49 / 0,68 |
| gzip nível 9 / descompactar | 0,80 / 0,84 | | | 1,23 / 1,33 |

- **O peso:** o json e o gzip do log somam ~5 ms numa vida de 2 730 ms (0,2 %).
- **A escrita não serve.** Os dois escrevem o JSON compacto (`bytes_identicos_ao_json: true`), não o formato do `para_jsonl`, que
  usa os separadores padrão (`bytes_identicos_ao_log: false`). Trocar a escrita muda o sha256 de todo log.
- **A leitura dá o mesmo dicionário** (`loads_igual: true`) e ganharia ~1 ms por vida (0,04 %).
- **O orjson não roda no PyPy.**

**Custo de errar:**
- **Se adotar e estiver errado:** entra uma dependência fora da biblioteca padrão no `digilab/events.py` e o PyPy fica bloqueado,
  para ganhar 0,04 %.
- **Se não adotar:** nada se perde.

## 7. Recomendações (DECIDIDAS)

**Decisão:** o Matheus aprovou as recomendações em 2026-11-09, com as palavras "Faça as recomendações". A decisão foi dada no chat e
repassada pelo Gerente da V3, com um comentário no PR #737. Ficou assim:
- o PyPy, o NumPy/Polars e o orjson/msgspec não são adotados agora;
- o achado do `sum()` (seção 8) se resolve fixando o CPython ≥ 3.12.

| opção | recomendação | ganho medido | custo de errar |
|---|---|---|---|
| PyPy | **não adotar agora.** Se o tempo das runs pesar, primeiro tornar as somas independentes do interpretador; depois rodar o PyPy numa run de calibração e comparar com o CPython antes de usar em validação | ~1,7× por vida (C4: 3,2 h → ~1,9 h, estimado) | divergência silenciosa de uma vida por um empate em float; resultados que dependem do interpretador; gabaritos em dobro |
| NumPy/Polars | **não adotar.** Se a análise incomodar, consertar o `_idx` e pôr um cache no `quantil_t`, na biblioteca padrão e com o resultado bit a bit igual (uma tarefa à parte) | < 23 s por run (< 0,2 %) | quebra a regra da biblioteca padrão e muda o último dígito de toda métrica |
| orjson/msgspec | **não adotar** | ~1 ms por vida na leitura (0,04 %); a escrita não serve | dependência no `digilab/`, sha256 dos logs e PyPy bloqueado |

O tempo das runs está na simulação (cérebro, corpo e mundo) e no replay G1, que dobra cada vida. São os únicos lugares onde um ganho
grande é possível. Mexer neles é mexer no motor, fora desta tarefa.

## 8. A versão do Python já muda os resultados (achado)

O CPython 3.12 mudou o `sum()` de floats para uma soma compensada (Neumaier). O 3.10 e o 3.11 somam de forma ingênua, como o PyPy, e o
CLAUDE.md diz "Python 3.10 ou mais novo". Daí, num CPython 3.11, as medidas e os gabaritos byte a byte deveriam falhar como no PyPy.
Isso é inferido do PyPy e da sonda, não foi rodado num 3.11. Já os runs gravam o `python: 3.13.0` no `meta.json`.

Havia duas saídas:
- **fixar o CPython ≥ 3.12 na regra;** é o mais barato;
- **trocar o `sum()` de floats do `metrics.py`** pelo `math.fsum`, que é exato e igual em todo interpretador. Muda o último dígito de
  parte das métricas no CPython de hoje e obriga a regerar os gabaritos.

**DECIDIDO (2026-11-09):** fixar o CPython ≥ 3.12. O `docs/MAPA_REPOSITORIO.md` já diz isso. A linha "Python 3.10 ou mais novo" do
`CLAUDE.md` muda à parte, com o ok direto do Matheus, porque esse arquivo só muda assim.

O registro está em `docs/registro/2026-11.md`.

## 9. O que não foi medido

- a memória do PyPy;
- 4 processos PyPy em paralelo;
- uma run inteira no PyPy;
- o CPython 3.11;
- a paridade com o TypeScript, que soma com `reduce` (ingênuo) e não foi conferida aqui.
