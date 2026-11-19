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

## 5. O diagnóstico da C2.5: por que a D sobe a privação no comedouro (2026-11-19)

O Matheus respondeu "Sim, diagnosticar" ao CHECKPOINT C2.5: nenhum braço vai ao jogo, e o diagnóstico usa só as vidas e o código que já
existem. **Nenhuma vida nova:** o `experiments/diagnostico_v3_corpo_c25.py` rejoga do log gravado as vidas das 50 primeiras unidades
(104001…104050) no comedouro e no `longe_fixo`, nos braços CTRL, D e D + E (1 200 vidas). Cada replay refaz o log byte a byte, e a
privação rejogada de cada vida tem de sair igual à do `medidas.json` (falha alta). Por decisão da janela dos dias 8 a 14, o script lê o
`Estado` (fome, higiene, energia, saúde, dormindo, noite) e a química (combustível, fome). A saída é o
`artifacts_v3_corpo/diagnostico_c25/diagnostico.json` (sha256 `a9c17057…25d0`). As contas por dono nas 200 unidades vêm do
`medidas.json` da run.

### 5.1 O que sobe é a fome, com o pet acordado

No comedouro, nas 50 unidades (D − CTRL):

| componente da privação | CTRL | D | D − CTRL |
|---|---|---|---|
| a privação | 0,158 | 0,232 | +0,074 [+0,067; +0,081] |
| só a fome abaixo de 0,15 | 0,079 | 0,155 | **+0,075** [+0,070; +0,080] |
| a higiene abaixo de 0,15 | 0,076 | 0,077 | +0,000 |
| só a energia abaixo de 0,15 | 0,001 | 0,000 | −0,001 |
| a fome baixa, acordado | 0,050 | 0,124 | **+0,074** |
| a fome baixa, dormindo | 0,059 | 0,074 | +0,015 |

- **Toda a privação a mais é de fome.** A energia quase nunca fica abaixo de 0,15, nem no CTRL: o cansaço da falta de combustível aparece
  na exaustão (o limiar de 0,25), e não na privação.
- **É acordado, e não no sono.** A hipótese de que a fome subiria demais durante a noite não se sustenta: o sono contribui com +0,015.
- **Toda decisão com a fome abaixo de 0,15 tem o combustível abaixo de C/4,** nos dois braços, e nenhuma tem comida no estômago.

### 5.2 Vem dos donos que deixam faltar comida

Por dono, nas 200 unidades da run (D − CTRL, `medidas.json`):

| lugar | dono | privação CTRL | D − CTRL | refeições por dia, D − CTRL | exaustão, D − CTRL |
|---|---|---|---|---|---|
| comedouro | atencioso | 0,016 | −0,009 ± 0,006 | **+1,02** | −0,046 |
| comedouro | relapso | 0,134 | **+0,201 ± 0,007** | −0,01 | −0,035 |
| comedouro | aleatório | 0,438 | **+0,114 ± 0,007** | +0,01 | −0,059 |
| comedouro | incoerente | 0,016 | −0,009 ± 0,006 | +1,02 | −0,046 |
| `longe_fixo` | atencioso | 0,290 | **−0,133 ± 0,034** | +1,14 | −0,097 |
| `longe_fixo` | relapso | 0,281 | **+0,142 ± 0,013** | +0,10 | −0,046 |
| `longe_fixo` | aleatório | 0,496 | **+0,096 ± 0,010** | +0,10 | −0,069 |
| `longe_fixo` | incoerente | 0,300 | **−0,135 ± 0,034** | +1,10 | −0,101 |

(± é a meia largura do IC95 aproximado, 1,96 × dp / √200.)

- **Com o atencioso e o incoerente,** que põem comida quando o pet precisa, a D faz o pet comer cerca de uma refeição a mais por dia e
  baixa a privação nos dois lugares.
- **Com o relapso e o aleatório,** a comida é o limite: as refeições por dia quase não mudam (no comedouro, −0,01 e +0,01). A falta de
  combustível é a mesma, mas a D a põe na fome, e a privação sobe.
- **O comedouro não é especial.** O efeito é o mesmo nos dois lugares e depende do dono. No `longe_fixo`, a queda com os donos bons
  (−0,13) compensa a subida com os outros, e a média fica em "≈ 0". No comedouro, a privação com os donos bons já está perto de 0 (0,016)
  e não tem como cair, e a média sobe.

### 5.3 É dano de verdade, não só um sinal maior

A saúde, nas 50 unidades (D − CTRL, a média na janela dos dias 8 a 14):

| lugar | dono | saúde CTRL | D − CTRL | combustível médio, D − CTRL (fração de C) |
|---|---|---|---|---|
| comedouro | atencioso | 0,996 | +0,004 ± 0,003 | +0,125 |
| comedouro | relapso | 0,962 | **−0,119 ± 0,017** | +0,009 |
| comedouro | aleatório | 0,411 | **−0,216 ± 0,042** | +0,013 |
| `longe_fixo` | atencioso | 0,771 | +0,132 ± 0,070 | +0,164 |
| `longe_fixo` | relapso | 0,791 | **−0,236 ± 0,064** | −0,004 |
| `longe_fixo` | aleatório | 0,317 | **−0,165 ± 0,047** | +0,012 |

**O mecanismo** (pelo código: `digilab/corpo.py`, os emissores `falta_combustivel` e `dano_privacao`):
1. **No CTRL,** a falta de combustível abaixo de C/4 sobe o **cansaço**, e o cansaço cai dormindo. O pet dorme, o cansaço desce, e a
   necessidade quase nunca passa do limiar da privação (85 % de C).
2. **Na D,** a mesma falta sobe a **fome**: 875 por tick em vez de 375, e a fome só cai comendo. Com comida, o pet come mais (o ganho com
   os donos bons). Sem comida, a fome fica acima do limiar.
3. **Acima do limiar,** o emissor `dano_privacao` sobe o dano, e a saúde cai. Por isso a viabilidade do corpo piora nos donos que deixam
   faltar comida (`corpo.dias_8_14.fracao_fora` no comedouro: relapso +0,195, aleatório +0,162), e a saúde cai mesmo com o mesmo
   combustível.

**Em uma frase:** a D tira a falta de combustível de um canal que o sono resolve e a põe num canal que só a comida resolve. Com comida, é
melhor para o pet. Sem comida, é pior, e o corpo cobra em saúde.

**A E não muda o quadro:** na D + E, a fome a mais do comedouro é quase a mesma (só a fome: +0,069 contra +0,075). A E guarda melhor a comida que sobra, mas
não cria comida onde o dono não põe.

### 5.4 Um achado à parte: o incoerente é o atencioso no comedouro

No comedouro, as 400 vidas do incoerente (CTRL e D × 200) saem iguais às do atencioso em todas as medidas. No longe e no `longe_fixo`
elas diferem pouco. As 12 células da C4 têm, no comedouro, só 3 donos distintos. Isso não muda a leitura (os contrastes são pareados),
mas pesa o atencioso duas vezes nas médias das 12 células. Fica como questão aberta para o instrumento.

### 5.5 O que a C3 poderia tentar (opções para o Matheus, nenhuma decidida)

1. **A ponte da D com teto:** a falta de combustível sobe a fome só até o limiar da privação, e não acima dele. Ela manteria o empurrão
   para comer e tiraria o dano da fome que o pet não pode resolver. É a opção mais direta pelo mecanismo.
2. **A ponte dividida:** parte da falta vai à fome e parte ao cansaço, como hoje. Ela suavizaria os dois lados, sem resolver o dano.
3. **Nenhuma mudança no corpo:** aceitar que a D só serve com um dono que alimenta, e ler a privação por dono.

**O custo de errar:** com a opção 1, os tamanhos e o teto seriam números novos (PROPOSTOS, SEM FONTE) e precisariam de um plano novo e de
uma run nova. Ligar a D como está leva ao jogo um pet que perde saúde com um dono que deixa faltar comida.
