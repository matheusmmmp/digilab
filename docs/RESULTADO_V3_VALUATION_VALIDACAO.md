# RESULTADO V3 — VALUATION, a V4: a validação contra a baseline trivial (2026-11-19, Claude Code, Opus 5.5)

**O plano:** [PLANO_ANALISE_V3_VALUATION_VALIDACAO.md](PLANO_ANALISE_V3_VALUATION_VALIDACAO.md), APROVADO pelo Matheus em 2026-11-18
("Aprovo os dois", confirmado nesta sessão: "Sim, aprovei"), na `main` pelo #1008 antes da primeira vida. A tarefa é a
[TAREFA_V3_VALUATION.md](TAREFA_V3_VALUATION.md).

**A leitura, pela regra da seção 3.2: indeterminado.** CON − TRIV = −0,003 [−0,042; +0,036] na taxa por episódio do `longe_fixo`. O IC
cruza o 0 e não cabe em ±0,032. A média fica praticamente em zero, mas a run não tem precisão para chamar de "nulo" com a régua da A1
(a margem efetiva é 0,056, seção 4). **Nenhuma leitura liga o conserto** (seção 3.4 do plano): ele continua reprovado pela exaustão.

## 1. A run

| comando (o do `meta.json`) | commit, árvore | vidas | sementes | duração |
|---|---|---|---|---|
| `python experiments/run_v3_valuation_validacao.py --config experiments/configs/v3_valuation/validacao.json --processos 4` | `62f5f6c0`, limpa | 7 200 (TRIV, REL e CON × 12 células × 200 unidades) | 69101…69505, K = 40, derivação `digibrain_prototipo` | 1 h 13 min (03:25–04:37 de 2026-11-19) |

- **O ambiente:** Python 3.13.0 e Node v24.19.0, este só gravado.
- **A saída:** código 0, sem falha alta (o replay, o T-CENARIO-1, as conferências da C4 e a do reflexo, o sha256 da calibração da A1). A
  run rodou **uma vez**, depois do `pre_run` liberar (ela esperou a run do SOCIAL_PAR S terminar).
- **A `main` antes de soltar:** a run esperou 48 commits. O único que toca o cérebro modular (`d4972db5`, a chave `reflexo_suave` da
  CORPO) entra desligado por padrão, e os testes da V4 e do conserto passaram na `main` nova (18 de 18).
- **A TRIV:** o ponto da A1 (fome 0,4, energia 0,1, tédio 0,5), lido de `artifacts_v3_baseline_trivial/calibracao/resultado.json` com o
  sha256 `a7e71bd3…` conferido.

**Os artefatos** em `artifacts_v3_valuation/validacao/`, com o sha256 no disco igual ao do `meta.json`:

| arquivo | sha256 | tamanho e observação |
|---|---|---|
| `resultado.json` | `72b3afdb…` | |
| `medidas.json` | `825ed1c7…` | 59,3 MB |
| `vidas.tar.gz` | `d5259b37…` | 33,7 MB, determinístico |
| `meta.json` | | com o sha256 do plano (`94445f50…`), da config, dos orquestradores e da calibração |

## 2. O primário e as secundárias (seções 3.1 a 3.3)

Os contrastes são pareados por unidade (n = 200), com o IC95 pelo t e as classes da A6.6 com δ = 0,032.

| contraste, taxa por episódio | níveis | diferença | IC95 | classe | leitura |
|---|---|---|---|---|---|
| **CON − TRIV, `longe_fixo` (o primário)** | TRIV 0,681; CON 0,678 | **−0,003** | [−0,042; +0,036] | indeterminado, p = 0,56 | **indeterminado** |
| REL − TRIV, `longe_fixo` (a réplica da A1) | TRIV 0,681; REL 0,579 | −0,102 | [−0,141; −0,062] | < 0 | a A1 se repete |
| CON − TRIV, comedouro | TRIV 0,945; CON 0,954 | +0,009 | [−0,018; +0,035] | indeterminado | |
| CON − TRIV, longe sorteado | TRIV 0,815; CON 0,510 | −0,306 | [−0,315; −0,296] | < 0 | a TRIV fecha mais |

- **O primário em detalhe:** t = −0,15 com 199 graus de liberdade. O IC95 do bootstrap, rotulado, é [−0,049; +0,037], e o g1 é 1,06.
- **A réplica da A1:** a A1 (97xxx) mediu −0,083 [−0,128; −0,038]. Na 69xxx, o REL − TRIV sai −0,102, no mesmo sentido e com os ICs
  sobrepostos.

## 3. O descritivo (sem classe)

| medida | lugar | TRIV | REL | CON |
|---|---|---|---|---|
| exaustão | `longe_fixo` | 1,000 | 0,230 | 0,423 |
| exaustão | comedouro | 1,000 | 0,169 | 0,275 |
| exaustão | longe | 1,000 | 0,307 | 0,522 |
| privação | `longe_fixo` | 0,986 | 0,362 | 0,380 |
| privação | comedouro | 0,982 | 0,158 | 0,198 |
| privação | longe | 0,976 | 0,534 | 0,487 |
| episódios de fome por vida | `longe_fixo` | 18,3 | 13,2 | 15,2 |
| episódios de fome por vida | comedouro | 27,6 | 17,1 | 17,9 |
| episódios de fome por vida | longe | 21,6 | 11,6 | 15,0 |

Os ICs de cada diferença estão no `resultado.json`, em `descritivo`.

## 4. O que isso diz

- **Com o conserto, o modular empata com a TRIV no `longe_fixo` pela média, mas a run não fecha a pergunta.** A diferença média é −0,003,
  e o IC vai de −0,042 a +0,036. Os dois limites passam um pouco de δ, então a classe é "indeterminado", não "≈ 0".
- **Achado, a precisão:** a margem efetiva (o menor efeito com poder 0,8 pelo dp observado, A6.5) é 0,056, maior que δ = 0,032. Com
  o dp das diferenças nesta célula (0,28), 200 unidades não bastam para chamar de "nulo" com a régua da A1. O plano não calculou isso
  antes, e não se ajusta nada agora: a leitura fica "indeterminado".
- **O gap da A1 se repete, e o conserto o cobre no `longe_fixo`.** Sem conserto, o REL fecha −0,102 a menos que a TRIV. Com o conserto,
  o CON fecha +0,099 a mais que o REL, nas mesmas sementes.
- **Fora do `longe_fixo`, o quadro muda:**
  - no comedouro, os três fecham quase tudo, e o CON − TRIV também sai indeterminado, perto de zero;
  - no longe sorteado, a TRIV fecha 0,815 contra 0,510 do CON. O conserto não cobre esse gap, que é três vezes o da A1.
- **A TRIV vive no limite:** exaustão 1,000 e privação perto de 0,98 nos três lugares. Ela fecha os episódios, mas passa a vida com fome e
  cansada. O CON fica com a exaustão em 0,42 e a privação em 0,38 no `longe_fixo`. Esta comparação é só descritiva, sem gate.
- **O que a run não demonstra** (o `nao_demonstra` do `resultado.json`):
  - que o conserto pode entrar num pet: ele reprovou na V3 pela exaustão (G2), e esta run não muda isso;
  - que a baseline é a melhor política trivial possível (só a grade da A1);
  - nada sobre o jogo web;
  - nada fora das 12 células, dos 14 dias e do mundo do MVP.

## 5. O que fica para o Matheus

O CHECKPOINT V4: o resultado vai como saiu. A frente volta ao estado da V5 (encerrada com o diagnóstico), com a V4 agora rodada. As chaves
continuam desligadas. Uma pergunta nova, como o gap do longe sorteado ou uma V4 com mais unidades, só com plano novo.
