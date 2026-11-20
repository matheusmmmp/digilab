# RESULTADO V3 — CORPO: a ponte com teto (C3), a run única (2026-11-19, Claude Code, Fable 5.2)

**O plano:** [PLANO_ANALISE_V3_CORPO_C3.md](PLANO_ANALISE_V3_CORPO_C3.md), APROVADO pelo Matheus em 2026-11-19 ("Aprovo todas"), na `main`
antes da primeira vida (#1016), com o código (#1024). A tarefa: [TAREFA_V3_CORPO.md](TAREFA_V3_CORPO.md). A run anterior e o diagnóstico:
[RESULTADO_V3_CORPO.md](RESULTADO_V3_CORPO.md).

**A leitura, pela regra da seção 5 do plano:**
- **DTB, o teto baixo (C/2): "ganho".** O forrageio sobe (+0,120, o Holm rejeita), nenhuma das oito guardas do bem-estar reprova, e o S2
  passa.
- **DTL, o teto no limiar: "perda".** O forrageio sobe igual (+0,123), mas três guardas reprovam: a privação do comedouro e as duas da
  saúde. O DTL sai quase igual à D em tudo. É o que o plano escreveu antes (seção 1): o dano da privação é um degrau, e cortar a ponte só
  no limiar tira pouco.

**O veredito do orquestrador:** "ao menos um teto com ganho: a C4 (seção 8)". Pelo programa, o ganho leva à C4, a validação. **A decisão é
do Matheus (o CHECKPOINT da C3).** Nenhum braço está ligado no jogo.

**As hipóteses do plano (seção 1):**
- **H1, o teto no limiar sai perto da D e em "perda":** confirma. Além da privação do comedouro, reprovam as duas guardas da saúde.
- **H2, o teto baixo deixa a privação e a saúde dos donos que deixam faltar comida perto do CTRL, e o F sobe menos que na D:** a primeira
  parte confirma na média das seis células (a saúde +0,007 [−0,002; +0,015]), com a ressalva do aleatório no comedouro. A segunda não
  aparece: o F do DTB não se separa do da D (−0,004 [−0,015; +0,007]).

**Três ressalvas, antes de ler os números:**
- **O T_B = C/2 é SEM FONTE.** A run testou dois tetos e nenhum outro. Ela não diz nada sobre um teto entre C/2 e o limiar.
- **O ganho do DTB não é igual em todos os donos.** Com o aleatório no comedouro, a saúde ainda cai (−0,048) e a privação ainda sobe
  (+0,024). A guarda da saúde passa na média das 6 células dos donos que deixam faltar comida (seção 3.2).
- **Esta é a run que escolheu o braço.** Ela não é a validação: a validação é a C4, em sementes novas.

## 1. A run

| comando (o do `meta.json`) | commit | vidas | sementes | duração |
|---|---|---|---|---|
| `python experiments/run_v3_corpo_c3.py --config experiments/configs/v3_corpo_c3/run.json --processos 4` | `f720d684` (a `main` com o #1024) | 9 600 (4 braços × 12 células × 200 unidades) e 400 pares (4 braços × 100) | bloco I 106001…106200, k = 1, derivação `digibrain_prototipo`; bloco II 106301…106400, k = 1, prefixo `corpo_par` | 3 h 4 min (18:13–21:17 de 2026-11-19) |

- **O ambiente:** Python 3.13.0 e Node v24.19.0; o Node só fica gravado.
- **O pre_run:** o `tools/pre_run.py` recusou a run enquanto o replay do R1 da PET_VIVO rodava ("há outra run em andamento"). Quando ele
  terminou (18:13), saiu "pre_run: pode rodar": o plano igual ao da `origin/main`, a faixa reservada e nenhuma outra run.
- **A saída:** código 0, o `run.err` vazio. As conferências rodaram vida a vida (o replay, o T-CENARIO-1, as da C4 e a de cada braço).
- **A árvore:** o `meta.json` grava `git_limpo = true`. Os logs ficaram fora da worktree (`D:\Trab\digilab\logs_run_corpo_c3`).
- **A duração:** 3 h 4 min, acima das ~2 h do plano. O bloco II levou 3 min 29 s. Durante a run, outra sessão rodou um `pytest tests/`
  na mesma máquina (visto às 20:51). O quanto isso pesou não foi medido. Desvio de forma no registro.

**Os artefatos,** em `artifacts_v3_corpo/c3/`. O sha256 de cada arquivo no disco é igual ao do `meta.json`:

| arquivo | sha256 | tamanho |
|---|---|---|
| `resultado.json` | `b3260812…b21d` | 365 kB |
| `medidas.json.gz` | `eeaebb24…9a43` | 13,0 MB; descomprime no `825a122a…a018` do `meta.json` |
| `pares.json` | `6f6f4b1b…ab43` | 0,5 MB |
| `vidas.tar.gz` | `03426106…c3d2` | 44,7 MB, as 9 600 vidas |
| `pares.tar.gz` | `bdc7d30a…4292` | 1,2 MB, os 400 pares |
| `meta.json` | `3832cdf9…133f` | |

- **O `medidas.json`** tem 108 MB, acima do limite de 100 MB do GitHub. Ele vai como o `medidas.json.gz` (gzip com `mtime = 0`), como diz
  a seção 6 do plano.
- **As medidas sem o relógio:** cada vida grava o tempo que levou (`custo.vida_cpu` e `custo.vida_parede`), e por isso o sha256 do
  `medidas.json` muda de uma réplica para outra. Sem a chave `custo`, na mesma serialização do orquestrador, o sha256 é
  `af99800f…0329` (107 397 027 bytes). É esse que uma réplica deve comparar.
- **A pasta crua:** os dois `.tar.gz` foram conferidos arquivo a arquivo contra as pastas `vidas/` e `pares/` (9 600 e 400 arquivos, nenhum
  diferente), e as pastas foram apagadas.

## 2. Os critérios (seção 5 do plano)

O contraste é braço − CTRL, pareado por unidade (n = 200 no bloco I, 100 pares no bloco II), com o IC95 pelo t e as classes da A6.6, com
δ = 0,032 no bloco I. No bloco II, δ é 10 % do nível do CTRL na própria run (1,069 decisão, SEM FONTE).

**F, o primário:** a taxa por episódio no `longe_fixo` (CTRL 0,561). O Holm é sobre o DTL e o DTB, com α = 0,025. A D é a referência.

| braço | braço − CTRL | IC95 | classe | p do Holm | nível |
|---|---|---|---|---|---|
| D (referência) | +0,124 | [+0,109; +0,139] | > 0 | fora do Holm | 0,685 |
| DTL | **+0,123** | [+0,109; +0,138] | > 0 | 2,1 × 10⁻³⁹, rejeita | 0,684 |
| DTB | **+0,120** | [+0,105; +0,135] | > 0 | 3,0 × 10⁻³⁷, rejeita | 0,680 |

**B, o bem-estar** (a privação e a exaustão reprovam com "> 0"; a saúde reprova com "< 0"):

| guarda | CTRL | D − CTRL | DTL − CTRL | DTB − CTRL |
|---|---|---|---|---|
| privação, comedouro | 0,157 | **+0,074** [+0,070; +0,078], **reprova** | **+0,072** [+0,068; +0,076], **reprova** | +0,005 [+0,002; +0,008], ≈ 0 |
| privação, longe | 0,547 | −0,016 [−0,030; −0,001], ≈ 0 | −0,008 [−0,023; +0,006], ≈ 0 | −0,087 [−0,101; −0,072], < 0 |
| privação, `longe_fixo` | 0,378 | −0,009 [−0,022; +0,004], ≈ 0 | −0,016 [−0,029; −0,003], ≈ 0 | −0,070 [−0,082; −0,057], < 0 |
| privação, 12 células | 0,361 | +0,017 [+0,010; +0,023], ≈ 0 | +0,016 [+0,009; +0,023], ≈ 0 | −0,050 [−0,057; −0,044], < 0 |
| exaustão, `longe_fixo` | 0,239 | −0,086 [−0,093; −0,079], < 0 | −0,089 [−0,095; −0,082], < 0 | −0,099 [−0,106; −0,092], < 0 |
| exaustão, 12 células | 0,242 | −0,082 [−0,085; −0,079], < 0 | −0,083 [−0,086; −0,080], < 0 | −0,095 [−0,098; −0,092], < 0 |
| saúde, 12 células | 0,629 | **−0,040** [−0,048; −0,032], **reprova** | **−0,040** [−0,048; −0,031], **reprova** | +0,051 [+0,044; +0,058], > 0 |
| saúde, o relapso e o aleatório | 0,521 | **−0,168** [−0,179; −0,158], **reprova** | **−0,162** [−0,172; −0,151], **reprova** | +0,007 [−0,002; +0,015], ≈ 0 |

**S, o substrato social** (bloco II):

| medida | CTRL | D − CTRL | DTL − CTRL | DTB − CTRL |
|---|---|---|---|---|
| S2, T\* até o reencontro, em decisões (reprova com "> 0") | 10,69 | −3,39 [−5,67; −1,11], < 0, passa | −3,39 [−5,68; −1,10], < 0, passa | −2,34 [−4,53; −0,15], < 0, passa |
| S1, chutes por dia (descritivo) | 0,0 | 0,0 | 0,0 | 0,0 |

**O S1 continua sem medir nada:** nenhum dos 400 pares chutou uma bola (a `fracao_pares_com_chute` é 0 nos quatro braços), como na C2.

| braço | F | B | S2 | **leitura** |
|---|---|---|---|---|
| D (referência) | > 0 | a privação do comedouro e as duas da saúde | passa | (a "perda" da C2, repetida) |
| DTL | > 0, o Holm rejeita | a privação do comedouro e as duas da saúde | passa | **perda** |
| DTB | > 0, o Holm rejeita | nenhuma reprova | passa | **ganho** |

**A D se repete pela terceira vez,** em sementes novas. No F: +0,124 aqui, +0,120 na C2 e +0,115 na run da D. Na privação do comedouro:
+0,074, +0,074 e +0,072.

## 3. O descritivo (sem teste)

Os números vêm do `resultado.json` (`descritivo`). Salvo onde dito, são as médias das 12 células.

### 3.1 O que cada braço muda no pet

| medida | CTRL | D | DTL | DTB |
|---|---|---|---|---|
| reflexos do sono por vida | 273,2 | 182,7 | 181,4 | 166,4 |
| fração de ticks dormindo | 0,466 | 0,375 | 0,375 | 0,377 |
| conflitos (fração das decisões) | 0,153 | 0,102 | 0,101 | 0,088 |
| refeições por dia | 3,12 | 3,64 | 3,63 | 3,56 |
| episódios de fome por vida | 13,9 | 14,8 | 15,5 | 17,5 |
| fração dos ticks com combustível abaixo de C/4 | 0,525 | 0,414 | 0,416 | 0,453 |
| fração do tempo com energia baixa | 0,203 | 0,136 | 0,135 | 0,124 |
| saúde média, dias 8 a 14 | 0,629 | 0,589 | 0,589 | 0,680 |
| fração das decisões com a saúde abaixo do limiar | 0,256 | 0,290 | 0,289 | 0,204 |
| fração dos ticks com a ponte cortada pelo teto | 0 | 0 | 0,281 | 0,368 |

**O teto, sobre a D** (braço − D, pareado):

| medida | DTL − D | DTB − D |
|---|---|---|
| F, a taxa por episódio no `longe_fixo` | −0,001 [−0,009; +0,008] | −0,004 [−0,015; +0,007] |
| privação, comedouro | −0,002 [−0,003; −0,001] | −0,069 [−0,071; −0,066] |
| privação, 12 células | −0,001 [−0,005; +0,004] | −0,067 [−0,072; −0,062] |
| saúde, 12 células | +0,001 [−0,004; +0,005] | +0,091 [+0,085; +0,098] |
| exaustão, 12 células | −0,001 [−0,002; 0,000] | −0,013 [−0,015; −0,012] |
| refeições por dia | −0,010 [−0,024; +0,003] | −0,082 [−0,099; −0,066] |

- **O DTL quase não muda a D,** mesmo cortando a ponte em 28 % dos ticks. O corte acontece com a fome já no limiar, e aí o dano já corre.
- **O DTB devolve a privação e a saúde** que a D tirava, e custa pouco no forrageio: o IC do F contra a D inclui o zero, e o pet come
  0,08 refeição a menos por dia.
- **O DTB tem mais episódios de fome por vida** (17,5 contra 14,8 da D e 13,9 do CTRL). A taxa por episódio é quase a mesma. Por que os
  episódios aumentam não foi medido.

### 3.2 Por dono (a saúde média e a privação, braço − CTRL)

| dono, lugar | saúde no CTRL | D | DTL | DTB | privação no CTRL | D | DTL | DTB |
|---|---|---|---|---|---|---|---|---|
| relapso, comedouro | 0,965 | −0,112 | −0,105 | −0,007 | 0,133 | +0,206 | +0,201 | +0,023 |
| relapso, longe | 0,432 | −0,233 | −0,233 | +0,096 | 0,438 | +0,094 | +0,087 | −0,033 |
| relapso, `longe_fixo` | 0,787 | −0,226 | −0,203 | +0,026 | 0,281 | +0,143 | +0,132 | −0,007 |
| aleatório, comedouro | 0,419 | −0,200 | −0,197 | **−0,048** | 0,464 | +0,112 | +0,108 | +0,024 |
| aleatório, longe | 0,191 | −0,090 | −0,087 | −0,008 | 0,608 | +0,068 | +0,064 | −0,016 |
| aleatório, `longe_fixo` | 0,331 | −0,148 | −0,144 | −0,018 | 0,515 | +0,095 | +0,092 | +0,012 |
| atencioso, comedouro | 0,996 | +0,003 | +0,003 | +0,003 | 0,015 | −0,011 | −0,010 | −0,012 |
| atencioso, longe | 0,521 | +0,129 | +0,106 | +0,143 | 0,580 | −0,118 | −0,094 | −0,147 |
| atencioso, `longe_fixo` | 0,688 | +0,127 | +0,136 | +0,142 | 0,352 | −0,121 | −0,134 | −0,144 |
| incoerente, longe | 0,542 | +0,117 | +0,097 | +0,144 | 0,560 | −0,106 | −0,091 | −0,151 |
| incoerente, `longe_fixo` | 0,678 | +0,149 | +0,151 | +0,133 | 0,365 | −0,152 | −0,155 | −0,140 |

O incoerente no comedouro sai igual ao atencioso no comedouro (seção 4) e não está na tabela.

- **Com os donos que alimentam** (o atencioso e o incoerente), os três braços melhoram o pet, como na C2.
- **Com o relapso e o aleatório,** a D e o DTL baixam a saúde em todas as seis células (−0,09 a −0,23). O DTB tira quase todo esse dano.
- **O que sobra no DTB:** com o aleatório no comedouro, a saúde ainda cai −0,048 [−0,058; −0,037], e com o aleatório no `longe_fixo`,
  −0,018 [−0,035; −0,002]. A privação ainda sobe um pouco no comedouro com os dois donos (+0,023 e +0,024).
- **Por que a guarda passa:** a guarda da saúde é a média das seis células. O ganho do relapso no longe (+0,096 [+0,060; +0,133]) compensa
  a queda do aleatório no comedouro. A regra do plano é a média, e por ela o DTB passa. Célula a célula, ele não é neutro em todas.
- **As refeições não mudam no comedouro com o relapso e o aleatório** (2,99 e 2,63 por dia nos quatro braços): o pet come tudo o que o dono
  põe. O que muda entre os braços é quanto a fome sobe entre uma refeição e outra.

### 3.3 A decomposição da privação (fração das decisões dos dias 8 a 14)

| medida | CTRL | D | DTL | DTB |
|---|---|---|---|---|
| só a fome abaixo do limiar | 0,141 | 0,199 | 0,196 | 0,134 |
| a fome abaixo do limiar, com ou sem as outras | 0,301 | 0,333 | 0,332 | 0,252 |
| com a higiene abaixo do limiar | 0,217 | 0,177 | 0,179 | 0,175 |
| só a energia abaixo do limiar | 0,001 | 0,000 | 0,000 | 0,001 |
| só a fome, no comedouro | 0,080 | 0,156 | 0,154 | 0,087 |

A privação a mais da D é privação só de fome, como no diagnóstico da C2.5. O DTL a mantém. O DTB a leva ao nível do CTRL (um pouco
abaixo nas 12 células, um pouco acima no comedouro: +0,007 [+0,006; +0,008]).

### 3.4 A ponte no teto

A fração dos ticks em que o teto cortou a ponte:

| lugar | DTL | DTB |
|---|---|---|
| comedouro | 0,179 | 0,267 |
| longe | 0,378 | 0,465 |
| `longe_fixo` | 0,286 | 0,373 |
| 12 células | 0,281 | 0,368 |

A fome química média nesses ticks não foi medida (o desvio de forma já registrado no código da C3, #1024).

### 3.5 O bloco II

O tempo até o reencontro cai nos três braços (CTRL 10,69 decisões; D e DTL 7,30; DTB 8,35). Nenhum par chutou a bola.

## 4. A pergunta do instrumento: o incoerente e o atencioso (D-C3-6)

**(a) Quantas vidas saem iguais** (o sha256 do log da vida, por semente):

| lugar | CTRL | D | DTL | DTB |
|---|---|---|---|---|
| comedouro | 200 de 200 | 200 de 200 | 200 de 200 | 199 de 200 |
| longe | 0 de 200 | 0 de 200 | 0 de 200 | 0 de 200 |
| `longe_fixo` | 0 de 200 | 0 de 200 | 0 de 200 | 0 de 200 |

**(b) Por que, pelo código** (leitura, sem medir e sem consertar):
- **O que os dois donos têm de igual:** o cuidado. Os dois chamam o mesmo `cuidados_necessarios` (`digilab/donos.py`).
- **O que têm de diferente:** só o feedback. Quando está atrasado no orçamento, ou quando precisa completar o mínimo do passo, o
  atencioso elogia ou repreende pelo que o pet fez, e o incoerente sorteia.
- **No comedouro,** o log da vida sai igual em 799 de 800 vidas. Então esse feedback quase nunca muda a vida do pet ali. A vida que
  difere (uma, no DTB) mostra que ele pode mudar.
- **No longe e no `longe_fixo`,** as vidas diferem em todas as sementes, mas há outra causa além do feedback: a rng do lugar leva o nome
  do dono na semente (`derivar_semente("dono-lugar", semente, rotulo_dono)`, no `DonoComLugar` do `digilab/mundo.py`). A ração do
  incoerente cai em pontos diferentes dos da ração do atencioso.
- **NÃO CONFIRMADO:** se, no comedouro, o feedback não é emitido, ou se é emitido e não muda nada no pet. A leitura do código não separa
  as duas coisas; isso pede olhar as vidas gravadas.

**(c) A sensibilidade, nas 11 células distintas** (sem a cópia do comedouro). O F não muda, porque é medido no `longe_fixo`, onde as
quatro células são distintas. As guardas:

| guarda | D | DTL | DTB |
|---|---|---|---|
| privação, comedouro (3 donos) | +0,102, reprova | +0,100, reprova | +0,011, passa |
| privação, 11 células | +0,019, passa | +0,018, passa | −0,054, passa |
| exaustão, 11 células | −0,085, passa | −0,087, passa | −0,099, passa |
| saúde, 11 células | −0,044, reprova | −0,043, reprova | +0,055, passa |

As outras guardas não mudam. **A leitura é a mesma** nas 12 e nas 11 células: o DTL em "perda" e o DTB em "ganho".

## 5. O que fica em aberto

- **O CHECKPOINT da C3 (do Matheus):** levar o DTB à C4, a validação em sementes novas, ou não mudar o corpo. A regra do plano diz
  "ganho"; a decisão é dele.
- **O T_B é um número só, e SEM FONTE.** A run não mostra se C/2 é o melhor teto, nem onde o dano começa entre C/2 e o limiar.
- **O aleatório no comedouro** ainda perde saúde com o DTB (−0,048). Se isso é aceitável é uma decisão, e uma C4 precisa dizer como lê
  essa célula.
- **Os episódios de fome a mais do DTB** (17,5 por vida) não foram explicados.
- **O S1 não mede o social,** pela segunda run seguida.
- **O incoerente no comedouro** é o atencioso: as "12 células" têm 11 distintas. A causa exata fica para um replay das vidas gravadas.

**O que esta run não demonstra** (o `nao_demonstra` do `resultado.json`): nada sobre o jogo web, onde a chave fica desligada; nada sobre
outros tetos além do limiar e de C/2, nem sobre a ponte dividida ou o transbordo (D-C3-3); nada sobre a E e a C5 com o teto; nada sobre o
social além do substrato, onde nenhum mecanismo social entra.
