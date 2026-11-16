# RESULTADO V3 — LONGE_GEOMETRIA: a regularidade do longe separada da geometria (2026-11-16, Claude Code, Opus 5.5, sessão do Matheus, branch `v3-longe-geometria-resultado`)

**A leitura é a primeira linha da seção 7 do plano: a regularidade explica o ganho.** Os dois primários passam com o Holm e ficam "> 0":
- **I-M3:** +0,052, IC95 [+0,037; +0,068];
- **I-PAD:** +0,071, IC95 [+0,054; +0,087].

A M-ANCORA fica "≈ 0" nos dois. Com o lado e a âncora iguais aos do `longe_fixo`, mas um ponto novo a cada ração, a memória deixa de ganhar
sobre o M2. Nestas condições, **a memória paga quando os lugares se repetem**, e a leitura da C1 e da C4 fica de pé, agora sem a mistura
com a geometria. O I-M3 e o I-PAD concordam, e a linha do PAD é a que vale para o jogo.

- **O plano:** `docs/PLANO_ANALISE_V3_LONGE_GEOMETRIA.md`, APROVADO pelo Matheus em 2026-11-16. O texto da run é o do commit `58a22928`
  (sha256 `bd671e56…d0d0`, igual ao `meta.json`).
- **A tarefa:** `docs/TAREFA_V3_LONGE_GEOMETRIA.md`.
- **Os artefatos:** em `artifacts_v3_longe_geometria/run/`. Cada número abaixo traz o campo do `resultado.json`, salvo onde outro arquivo é
  indicado.

## 1. A run

- **O comando:** `python experiments/run_v3_longe_geometria.py --config experiments/configs/v3_longe_geometria/longe_geometria.json --processos 4`.
  - A run saiu da `main` em `58a22928` (o merge do #939), com a árvore limpa: `git_head` e `git_limpo` = true no `meta.json`.
  - Usou 4 processos e Python 3.13.0.
- **As vidas:** 200 unidades × 4 braços × 16 células, 14 dias e orçamento de 16, o que dá **12 800 vidas** (`vidas`, `unidades`). As
  unidades vêm das bases 93101, 93202, 93303, 93404 e 93505, com K = 40 e o prefixo `digibrain_prototipo`.
- **O tempo:** das 15h34 às 18h23 de 2026-11-16, 10 105 s de parede nas vidas e 10 111 s com a análise, cerca de 2 h 49 min (`meta.json`,
  `inicio`, `fim`, `vidas_parede_s`, `duracao_s`). O processo saiu com 0. Ficou dentro da estimativa do plano, de 3 h a 4 h.
- **A faixa (o desvio D-LGR-1):** a run rodou na 93101…93505, a faixa que a LG-6 aprovou. Na `main`, a LONGE_GEOMETRIA tinha trocado para
  a 96101…96505 (D-EQ2-11), mas a worktree da run tinha sido criada antes da troca e não foi atualizada. A 93xxx é a da calibração E0/E1
  da EQUILIBRIO_CUIDADO no jogo web. O Matheus aceitou a run nesta faixa ("Aceitar na 93xxx"). Este PR:
  - devolve à `main` o orquestrador, a config, a fumaça, o teste e o plano exatos da run, iguais aos sha256 do `meta.json`;
  - deixa a 96xxx livre.
- **A máquina (o desvio D-LGR-2):** a run rodou ao lado de outros processos pesados, por escolha do Matheus ("Começar junto"): o PM2.5 dele,
  a calibração da BASELINE_TRIVIAL de outra sessão (4 processos) e uma ingestão. Isso fura a V3-D8. A carga não muda nenhuma vida, porque o
  G1 confere cada uma bit a bit, e a run terminou sem erro.
- **As conferências da run** falham alto e rodaram em cada vida (o orquestrador do #939): o replay bit a bit do disco (o G1), o
  T-CENARIO-1, o G-MECANISMO com o crédito, e a conferência da memória da C4 no PAD.
- **A conferência depois da run,** feita neste PR sem nenhuma vida:
  - os sha256 do `medidas.json` e do `resultado.json` são os do `meta.json` (`artefatos_sha256`);
  - os sha256 do orquestrador, da config e do plano na árvore deste PR são os do `meta.json`;
  - a análise refeita do `medidas.json` gravado (`analisar`, sem mudança) sai igual ao `resultado.json`, byte a byte;
  - há 3 200 vidas por braço, e nenhuma taxa por episódio deu `None`;
  - o `vidas.tar.gz` tem as 12 800 vidas, e o `medidas.json.gz` descomprime no mesmo sha256 do `meta.json`.
- **Os artefatos,** em `artifacts_v3_longe_geometria/run/`:
  - o `meta.json` (sha256 `6ddaa2a1…30f4`), com os sha256 da config (`bc9bc585…a6aa`), do orquestrador (`b1bb3819…0e127`) e do plano
    (`bd671e56…d0d0`);
  - o `resultado.json` (`6760525f…bc96`);
  - o `medidas.json.gz` (`ff379334…3d08`, 10,8 MB). O `medidas.json` tem 117 MB, acima do limite de 100 MB, e não vai ao git solto. Ele
    descomprime em `63a0c1b3…5f1c`, o sha256 do `meta.json`;
  - o `vidas.tar.gz` (`471941bb…e669`, 60,7 MB), com a ordem por nome, o dono 0 e o `mtime` do fim da run, como na C1;
  - o `run.log`, com a saída da run.

## 2. Os primários (seção 5)

O I é o ganho da memória (X − M2) na taxa de fechamento por episódio no `longe_fixo`, menos o mesmo ganho no `longe_ancora`, pareado por
unidade. O critério (A6.4) é o limite inferior do IC95 acima de 0, com o Holm sobre os dois p unilaterais e a margem δ = 0,034.

| primário | média | IC95 (t) | t (gl 199) | p unilateral | Holm | classe | passa |
|---|---|---|---|---|---|---|---|
| **I-PAD** | +0,0709 | [+0,0544; +0,0874] | 8,47 | 2,6 × 10⁻¹⁵ | 1º passo, limiar 0,0125: rejeita | > 0 | sim |
| **I-M3** | +0,0524 | [+0,0367; +0,0682] | 6,58 | 2,1 × 10⁻¹⁰ | 2º passo, limiar 0,025: rejeita | > 0 | sim |

(`primarios.I-PAD`, `primarios.I-M3`.)

- **A margem efetiva** (a meia largura do IC95) saiu 0,0235 no I-PAD e 0,0224 no I-M3 (`margem_efetiva`), abaixo da δ de 0,034 que o poder
  previa. O critério não muda.
- **O bootstrap,** rotulado como anticonservador com 5 bases (A4.4), dá IC95 [+0,0585; +0,0833] no I-PAD e [+0,0372; +0,0676] no I-M3
  (`bootstrap.ic95`). Ele fica ao lado e não decide nada.

## 3. As premissas (G-PESA e G-ELEGIVEL-EP)

As duas premissas passam nos dois braços com memória e nos dois lugares, e as duas leituras são conclusivas (`premissas.*.conclusivo`).

| braço | lugar | G-PESA da memória (média, limiar 0,01) | G-ELEGIVEL-EP (fração de vidas, limiar 0,8) |
|---|---|---|---|
| PAD | `longe_fixo` | 0,1889 [0,1852; 0,1926] | 0,959 |
| PAD | `longe_ancora` | 0,1789 [0,1759; 0,1818] | 1,000 |
| M3\* | `longe_fixo` | 0,1188 [0,1142; 0,1234] | 0,954 |
| M3\* | `longe_ancora` | 0,1135 [0,1089; 0,1180] | 1,000 |

(`premissas.<braço>.<lugar>`.) A memória pesa nas decisões tanto no `longe_fixo` quanto no `longe_ancora`. O que muda entre os dois lugares
não é se a memória entra, e sim se ela paga.

## 4. A M-ANCORA e a leitura (seção 7)

| braço | M-ANCORA (X − M2 no `longe_ancora`) | IC95 | classe |
|---|---|---|---|
| PAD | −0,0159 | [−0,0272; −0,0046] | ≈ 0 (sinal −) |
| M3\* | −0,0098 | [−0,0202; +0,0005] | ≈ 0 |

(`M-ANCORA`.) O IC inteiro fica dentro de (−0,034; +0,034) nos dois, então a classe é "≈ 0". No PAD o limite superior fica abaixo de 0, e
o orquestrador registra o sinal "−" ao lado. Pela tabela da seção 7, o "≈ 0" e o "< 0" levam à mesma linha.

**A linha** (`leitura`): "a regularidade explica o ganho: a memoria paga quando os lugares se repetem, com o lado e a ancora iguais; a
leitura da C1 e da C4 fica de pe, sem a mistura". O I-M3 e o I-PAD concordam (`leitura.concordam` = true), e a linha que vale para o jogo é
a do I-PAD (`leitura.vale_para_o_jogo`).

## 5. O descritivo (seção 8; sem gate, nada aqui muda a seção 7)

**A conferência da construção nas vidas** (`descritivo.conferencia_da_construcao`):

| lugar | rações | distância média ao comedouro (células) | direções | pontos distintos por ração |
|---|---|---|---|---|
| `longe_um` | 83 002 | 23,15 | 5 | 0,010 |
| `longe_fixo` | 80 750 | 22,67 | 5 | 0,030 |
| `longe_ancora` | 77 025 | 22,78 | 5 | 0,740 |
| `longe` | 82 933 | 24,23 | 16 | 0,852 |

O `longe_ancora` tem a geometria do `longe_fixo` (o mesmo lado, as mesmas 5 direções e a mesma distância, a 0,1 célula) e a repetição do
`longe` (74 % de pontos novos por ração, contra 3 % do `longe_fixo`). A run manipulou o que o plano queria manipular. A distância média e a
média das contagens saem do histograma gravado, e as contagens por direção estão no artefato.

**A escada do ganho (X − M2 por lugar,** `descritivo.escada_do_ganho`):

| lugar | M3\* − M2 | classe | PAD − M2 | classe |
|---|---|---|---|---|
| `longe_um` | +0,1309 [+0,1183; +0,1435] | > 0 | +0,1889 [+0,1751; +0,2027] | > 0 |
| `longe_fixo` | +0,0426 [+0,0310; +0,0542] | > 0 | +0,0550 [+0,0420; +0,0679] | > 0 |
| `longe_ancora` | −0,0098 [−0,0202; +0,0005] | ≈ 0 | −0,0159 [−0,0272; −0,0046] | ≈ 0 |
| `longe` | −0,0271 [−0,0391; −0,0151] | < 0 | −0,0163 [−0,0299; −0,0028] | ≈ 0 |

- O ganho cai junto com a repetição: um ponto, três pontos, um ponto novo com a geometria fixa, e um ponto novo com a geometria sorteada.
- **O R-UM** (`descritivo.R-UM`), a previsão "> 0" do degrau de um ponto para três, sai +0,0884 [+0,0707; +0,1061] no M3\* e +0,1339
  [+0,1148; +0,1531] no PAD, os dois "> 0".
- **No `longe` sorteado,** o M3\* fica "< 0", a memória custando 2,7 pontos ao M3\*. É descritivo, sem gate.
- O ganho do M3\* no `longe_fixo` (+0,0426) fica perto do da C1 (+0,0489, `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`), com outras
  sementes.

**O GEO, a geometria sem aprendizado** (a taxa no `longe_ancora` menos a no `longe`, `descritivo.GEO`): +0,1270 [+0,1161; +0,1378] no M0,
+0,1377 no M2, +0,1550 no M3\* e +0,1382 no PAD, todos "> 0".
- A leitura principal é a do M0, que não aprende: cerca de 12,7 pontos da diferença entre o `longe_ancora` e o `longe` já existem sem
  memória nenhuma, só pela geometria (o lado e a distância).
- É a parte que o I desconta, porque ela aparece igual nos dois lados da subtração.

**As taxas por episódio** (`descritivo.episodio_por_lugar_braco`), para dar a escala:

| lugar | M0 | M2 | M3\* | PAD |
|---|---|---|---|---|
| `longe_um` | 0,525 | 0,481 | 0,612 | 0,670 |
| `longe_fixo` | 0,539 | 0,513 | 0,555 | 0,568 |
| `longe_ancora` | 0,594 | 0,597 | 0,588 | 0,582 |
| `longe` | 0,467 | 0,460 | 0,433 | 0,443 |

**As visitas ao lugar lembrado que acham a ração** (`descritivo.visitas`, só nos braços com memória):

| lugar | visitas do M3\* | fração que acha | visitas do PAD | fração que acha |
|---|---|---|---|---|
| `longe_um` | 15 332 | 0,000 | 43 986 | 0,000 |
| `longe_fixo` | 17 177 | 0,000 | 43 944 | 0,000 |
| `longe_ancora` | 23 193 | 0,0014 | 39 632 | 0,0007 |
| `longe` | 28 686 | 0,0007 | 54 485 | 0,0001 |

- A visita ao lugar lembrado quase nunca acha a ração no próprio lugar, nem no `longe_fixo`, onde o ganho existe.
- Isso não contradiz o caminho que a D-C1-3 achou na C1: as idas e a queda das perdas para o sono (o plano, a abertura), e não o ato de
  achar a ração no próprio lugar.
- O teste desse caminho nesta run é a decomposição da D-C1-3 (item 3 da seção 8), que sai num script à parte (D-LG-3). Não está neste PR.

**O corpo** (`descritivo.corpo`, a C5, com o limiar 0,15):
- No `longe_fixo` e no `longe_um`, a memória diminui a fração do tempo com algum sistema abaixo do limiar. Nos dias 8 a 14: M3\* − M2
  −0,0445 e PAD − M2 −0,0536 no `longe_fixo`, os dois "< 0".
- No `longe_ancora`, as diferenças ficam "≈ 0".
- No `longe` sorteado, a memória aumenta essa fração: +0,0615 no M3\* e +0,0467 no PAD, os dois "> 0".
- O corpo segue o mesmo padrão da taxa de fechamento.

**As faixas de d₀** (`descritivo.faixas_d0`) e **os donos** (`descritivo.por_dono`) ficam no artefato, só descritivos. A faixa de d₀ depende
do cérebro (LP-2), e a leitura entre lugares é primeiro a do M0.

## 6. O que este resultado não demonstra

Como no `resultado.json` (`nao_demonstra`), este resultado não demonstra:
- que o longe fica consertado;
- que o modular supera o A;
- a prontidão de algum cérebro;
- a separação do lado e da âncora (seção 10 do plano): o `longe_ancora` mantém os dois iguais aos do `longe_fixo`, então esta run não diz
  qual dos dois importa para o GEO;
- um tamanho de efeito fora das condições da run.

Também não diz por qual caminho a repetição paga. Essa é a pergunta da decomposição da D-C1-3, descritiva e geradora de hipótese.

## 7. Os desvios

Estão em `docs/registro/2026-11.md`, na seção "2026-11-16 — LONGE_GEOMETRIA: o resultado da run": D-LGR-1 (a faixa), D-LGR-2 (a máquina)
e D-LGR-3 (os artefatos).
