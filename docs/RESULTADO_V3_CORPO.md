# RESULTADO V3 — CORPO: a ablação do corpo (C2), a run única (2026-11-19, Claude Code, Opus 5.5)

**O plano:** [PLANO_ANALISE_V3_CORPO.md](PLANO_ANALISE_V3_CORPO.md), APROVADO pelo Matheus em 2026-11-18 com três ressalvas ("Aprovar o C1
com essas três ressalvas"; a forma confirmada em "Confirmo, siga"), na `main` antes da primeira vida (#1003). O código dos braços entrou
antes também (#1005, as chaves; #1007, o orquestrador). A tarefa: [TAREFA_V3_CORPO.md](TAREFA_V3_CORPO.md). O mapa: [MAPA_CORPO.md](MAPA_CORPO.md).

**A leitura, pela regra da seção 5 do plano: os três braços saem em "perda".** O forrageio (F) sobe nos três, com o Holm rejeitando, mas
cada um tem pelo menos uma guarda do bem-estar em "> 0":
- **D** e **D + E:** só a privação no comedouro (+0,074 e +0,064). É o desfecho que o plano escreveu antes da run (seção 5, "a consequência
  da ressalva 3").
- **D + C5:** cinco das seis guardas, com a exaustão quase dobrando (0,232 → 0,435 nas 12 células).

**O veredito do orquestrador:** "tensão não localizada por estas opções (seção 1): o programa para no CHECKPOINT C2.5". Pela regra do
programa, a perda vai ao Matheus pelo trade-off. Nenhum braço é um conserto do jogo, e as chaves continuam desligadas no jogo.

## 1. A run

| comando (o do `meta.json`) | commit | vidas | sementes | duração |
|---|---|---|---|---|
| `python experiments/run_v3_corpo.py --config experiments/configs/v3_corpo/run.json --processos 4` | `eedfb2f4` (a `main` com o #1007) | 9 600 (4 braços × 12 células × 200 unidades) e 400 pares (4 braços × 100) | bloco I 104001…104200, k = 1, derivação `digibrain_prototipo`; bloco II 104301…104400, k = 1, prefixo `corpo_par` | 2 h 6 min (01:17–03:23 de 2026-11-19) |

- **O ambiente:** Python 3.13.0 e Node v24.19.0; o Node só fica gravado.
- **O pre_run:** antes de soltar a run, o `tools/pre_run.py` saiu com "pode rodar". Ele conferiu que o plano estava igual ao da
  `origin/main`, que a faixa estava reservada e que nenhuma outra run rodava.
- **A saída:** código 0, sem falha alta. As conferências rodaram vida a vida:
  - o replay e o T-CENARIO-1;
  - as conferências da C4;
  - a do conserto, desligado nos braços sem a C5;
  - a de cada braço: na D + C5, nenhum reflexo e os pesos suaves iguais às decisões com a energia baixa; nos outros, nenhum peso suave;
    na D + E, nenhum descarte de comida.
- **A árvore:** o `meta.json` grava `git_limpo = false`. Os únicos arquivos fora do commit eram os dois logs do `Start-Process`
  (`run_v3_corpo.log` e `.err`), que eu criei na raiz da worktree ao lançar a run e que o git não rastreia. O `git diff eedfb2f4` saiu
  vazio: o código é o do commit. Desvio de forma no registro.
- **A duração:** 2 h 6 min, abaixo das ~3 h do plano. O bloco II levou 3 min 24 s.

**Os artefatos,** em `artifacts_v3_corpo/ablacao/`. O sha256 de cada arquivo no disco é igual ao do `meta.json`:

| arquivo | sha256 | tamanho |
|---|---|---|
| `resultado.json` | `daf59ef8…2eb8` | 170 kB |
| `medidas.json.gz` | `dac0abba…c5c2` | 10,1 MB; descomprime no `06de6baa…2baa` do `meta.json` |
| `pares.json` | `f52193a7…653d` | 0,5 MB |
| `vidas.tar.gz` | `73f31feb…c189` | 44,5 MB, as 9 600 vidas |
| `pares.tar.gz` | `0288dc70…fc2d` | 1,2 MB, os 400 pares |
| `meta.json` | `14ad5c07…4d66` | |

O `medidas.json` tem 104 MB, acima do limite de 100 MB do GitHub, e não vai ao git solto. Ele vai como o `medidas.json.gz` (gzip com
`mtime = 0`), como na LONGE_GEOMETRIA.

## 2. Os critérios (seção 5 do plano)

O contraste é braço − CTRL, pareado por unidade (n = 200 no bloco I, 100 pares no bloco II), com o IC95 pelo t e as classes da A6.6, com
δ = 0,032 no bloco I. No bloco II, δ é 10 % do nível do CTRL na própria run (SEM FONTE).

**F, o primário:** a taxa por episódio no `longe_fixo` (CTRL 0,579). O Holm é sobre os 3 braços, com α = 0,025.

| braço | braço − CTRL | IC95 | classe | p do Holm | nível |
|---|---|---|---|---|---|
| D | **+0,120** | [+0,105; +0,136] | > 0 | 3,6 × 10⁻³⁵ | 0,700 |
| D + E | **+0,110** | [+0,095; +0,125] | > 0 | 3,6 × 10⁻³⁴ | 0,689 |
| D + C5 | **+0,168** | [+0,154; +0,182] | > 0 | 1,1 × 10⁻⁵⁹ | 0,747 |

**B, o bem-estar** (uma guarda reprova com "> 0"):

| guarda | CTRL | D − CTRL | D + E − CTRL | D + C5 − CTRL |
|---|---|---|---|---|
| privação, comedouro | 0,151 | **+0,074** [+0,071; +0,078], **reprova** | **+0,064** [+0,060; +0,067], **reprova** | **+0,115** [+0,112; +0,119], **reprova** |
| privação, longe | 0,535 | −0,016 [−0,031; −0,002], ≈ 0 | −0,083 [−0,099; −0,068], < 0 | +0,005 [−0,009; +0,020], ≈ 0 |
| privação, `longe_fixo` | 0,342 | −0,007 [−0,022; +0,007], ≈ 0 | −0,039 [−0,055; −0,022], < 0 | **+0,039** [+0,023; +0,055], **reprova** |
| privação, 12 células | 0,343 | +0,017 [+0,010; +0,024], ≈ 0 | −0,019 [−0,027; −0,012], ≈ 0 | **+0,053** [+0,046; +0,061], **reprova** |
| exaustão, `longe_fixo` | 0,222 | −0,078 [−0,085; −0,071], < 0 | −0,084 [−0,092; −0,076], < 0 | **+0,195** [+0,184; +0,205], **reprova** |
| exaustão, 12 células | 0,232 | −0,079 [−0,082; −0,076], < 0 | −0,087 [−0,091; −0,084], < 0 | **+0,203** [+0,197; +0,209], **reprova** |

**S, o substrato social** (bloco II):

| medida | CTRL | D − CTRL | D + E − CTRL | D + C5 − CTRL |
|---|---|---|---|---|
| S1, chutes por dia (reprova com "< 0") | 0,0 | 0,0, indeterminado, passa | 0,0, indeterminado, passa | 0,0, indeterminado, passa |
| S2, T\* até o reencontro, em decisões (reprova com "> 0") | 10,92 | −4,24 [−6,32; −2,16], < 0, passa | −1,02 [−3,57; +1,53], indeterminado, passa | −2,91 [−5,20; −0,62], < 0, passa |

**S1 não mede nada nesta run:** nenhum dos 400 pares chutou uma bola, em nenhum braço (a `fracao_pares_com_chute` é 0 nos quatro). A
fumaça já mostrava isso, com 2 pares. A guarda "passa" porque o IC é [0; 0], e não porque o social foi preservado. É uma questão aberta
(seção 4).

| braço | F | B | S | **leitura** |
|---|---|---|---|---|
| D | > 0, Holm rejeita | a privação do comedouro | passa | **perda** |
| D + E | > 0, Holm rejeita | a privação do comedouro | passa | **perda** |
| D + C5 | > 0, Holm rejeita | cinco guardas | passa | **perda** |

## 3. O descritivo (o que cada braço muda no pet)

As médias das 12 células, salvo onde dito; os números vêm do `resultado.json` (`descritivo`).

| medida | CTRL | D | D + E | D + C5 |
|---|---|---|---|---|
| reflexos do sono por vida | 265,6 | 178,2 | 170,9 | 0 (vira peso) |
| fração de ticks dormindo | 0,465 | 0,376 | 0,377 | 0,351 |
| conflitos (fração das decisões) | 0,148 | 0,099 | 0,092 | 0,281 |
| refeições por dia | 3,18 | 3,70 | 3,23 | 3,73 |
| episódios de fome por vida | 14,0 | 15,0 | 13,1 | 15,7 |
| fração dos ticks com combustível abaixo de C/4 | 0,517 | 0,404 | 0,296 | 0,380 |
| fração do tempo com energia baixa | 0,198 | 0,133 | 0,127 | 0,378 |
| privação no comedouro | 0,151 | 0,225 | 0,215 | 0,267 |

**A D se repete:** os números do D aqui saem perto dos da run da D (#1002), em outras sementes. Na taxa por episódio do `longe_fixo`, deu
+0,120 aqui contra +0,115 lá. Na privação do comedouro, +0,074 contra +0,072. Na exaustão, −0,079 contra −0,078.

**A E, sobre a D** (descritivo, sem teste):
- **O que ela faz:** a comida que sobra vira combustível, e o pet come menos vezes (3,70 → 3,23 refeições por dia), com menos tempo de
  combustível baixo (0,404 → 0,296).
- **A privação:** cai no longe (−0,016 → −0,083) e no `longe_fixo` (−0,007 → −0,039). No comedouro, desce só um pouco
  (+0,074 → +0,064) e continua acima de δ.
- **O F:** fica um pouco abaixo do D (+0,110 contra +0,120).

**A C5, sobre a D:**
- **O que ela faz:** sem o reflexo, nenhum comer é trocado pelo sono à força (o `comer_trocado_no_reflexo` vai a 0, por construção). O
  pet come mais no episódio de fome (0,191 → 0,309 das decisões nas 12 células) e fecha mais episódios (F +0,168).
- **O custo:** a energia baixa quase triplica (0,133 → 0,378), a exaustão sobe muito acima do CTRL (0,435) e os conflitos sobem
  (0,281). O peso +S no dormir não basta para segurar o sono: o dormir passa a concorrer no sorteio, e o pet adia o sono.

**A privação do comedouro nos três:** ela sobe com a D, e nenhuma das duas opções a segura. O mecanismo não foi medido aqui; o diagnóstico
é a C2.5.

## 4. O que fica em aberto

- **O trade-off da D (CHECKPOINT C2.5, do Matheus):** a D e a D + E trocam mais forrageio, menos exaustão e menos reflexos por mais
  privação no comedouro (0,151 → 0,225). Se isso vale é uma decisão, não uma conta: a regra do plano diz "perda".
- **O S1 não mede o social:** com zero chutes em todos os pares, o substrato do bloco II não dá chance à bola. Uma guarda social precisa
  de outra medida, ou de pares com chute. Fica para o desenho de uma próxima run, se houver.
- **O mecanismo da privação no comedouro:** é o diagnóstico da C2.5.

**O que esta run não demonstra** (o `nao_demonstra` do `resultado.json`): nada sobre o jogo web, onde as chaves ficam desligadas; nada
sobre a calibração do cuidado (E1 e E2) nem sobre o I-PAD da LONGE_GEOMETRIA; nada sobre outros tamanhos nem sobre combinações fora dos
braços; nada sobre o social além do substrato, onde nenhum mecanismo social entra.
