# Plano de análise V3: CREDITO_INTERVALO, o R2 (o crédito do intervalo, com o ELOGIO)

**Status: APROVADO pelo Matheus em 2026-11-19,** com as CI-R2-1 a CI-R2-9 DECIDIDAS pela recomendação: "Aprovo todas", na sessão coordenadora, confirmado nesta sessão ("Sim, aprovei"). Os adendos 1 (a linha de base) e 2 (o corpo), no fim, foram APROVADOS pelo Matheus em 2026-11-20 ("Aprovo e confirmo"), com as AD1-1 a AD1-3 e a AD2-1 pela recomendação. O R2 espera a C4 da CORPO (AD2-1). Escrito em 2026-11-19 (Claude Code, Opus 5.5, worktree `v3-valuation`, branch `v3-credito-intervalo-plano`), a pedido
do Matheus na sessão coordenadora: "Manda o valuation, escrever o plano do R2". Só o plano: nenhum código e nenhuma vida antes da
aprovação. A tarefa é a [TAREFA_V3_CREDITO_INTERVALO.md](TAREFA_V3_CREDITO_INTERVALO.md), da gerência. O orquestrador vai conferir este
cabeçalho e recusar sem o APROVADO.

**Duas seções ficam a fechar depois, por adendo, antes do código:**
- a linha de base (seção 4), com o replay R-a da sessão da cadeia;
- o corpo (seção 5.1), com o CHECKPOINT da C3 do corpo.

## 0. O contexto

- **O R1** ([RESULTADO_V3_PET_VIVO_R1.md](RESULTADO_V3_PET_VIVO_R1.md), #1029 na `main`) mediu, sem mudar nenhuma decisão:
  - **perto de 78 % do sinal do corpo cai no intervalo entre as decisões**, fora do r de hoje (`F_sinal` 0,776 a 0,780 nos 3 lugares);
  - **o que o intervalo distingue é dormir de estar acordado:** o dormir é a única ação com o `r_int_n` positivo (+102 a +108), e o r
    dele no mesmo tick é 0 em todas as decisões;
  - **a linha de base por contexto (acordado e dormindo) apaga o sinal do sono por construção:** o resto do dormir fica em 0, e o η²
    entre comportamentos cai de 0,46–0,50 para 0,011–0,019.
- **O ELOGIO** ([RESULTADO_V3_ELOGIO.md](RESULTADO_V3_ELOGIO.md)): o G-EL1 confirma contra o E-sorteado (+0,073), mas o E-imed fica igual
  ao E0 (−0,003). O carinho na hora não ensina X além do E0, e um g maior só volta com plano novo. A chave segue desligada.
- **A VALUATION** (V3 e V4): o sono e a fome disputam o mesmo intervalo, e o conserto do reflexo reprovou pela exaustão. É o risco que a
  guarda de forrageio deste plano vigia.
- **As decisões que valem:** as INT-1 a INT-9 (D-INT-9). Delas vêm a ordem (INT-1), uma estrutura de traço só (INT-5), o `tau_c` fora
  (INT-6) e a checagem do v38 (INT-8). O mecanismo é o da seção 3.3 da
  [análise da cadeia](futuro/integracao_cadeia_digibrain.md) e da seção 3 da tarefa.

## 1. O que as vidas gravadas já respondem, e por que não bastam

| pergunta | as vidas gravadas respondem? | de onde | por que não basta |
|---|---|---|---|
| há sinal fora do r? | **sim:** 78 % | o R1, sobre o HOJE do PV-2 (2 400 vidas) | medir o sinal não mostra que creditá-lo ensina |
| qual canal e qual ação? | **sim:** a energia (0,84–0,86 fora) e o dormir | o R1, M-FORA e M-AÇÃO | idem |
| qual linha de base deixa o que creditar além do sono? | **sim, sem vida nova:** é o replay R-a (seção 4) | as medidas do R1 | o R-a diz o resto que cada linha de base daria, não o que o pet faria com ele |
| o crédito muda o H na direção certa (T4)? | **não** | — | o crédito muda o H, o H muda a escolha, e a vida diverge do log na primeira decisão diferente: o replay não refaz o contrafactual |
| o efeito atrasado com uma ação no meio (T4) | **não existe nas vidas** | — | nenhum mundo gravado tem um efeito que siga uma comida com atraso fixo; ele é um instrumento novo da bancada (seção 3.3) |
| o tapa independente da comida (T5) | **não** | a contagem da seção 6 | os donos da C4 não dão tapa nenhum (0 em 120 vidas nas sementes dos testes) |
| o crédito tira o pet da comida (a guarda)? | **não** | — | é o mesmo motivo da T4: só vidas novas mostram a escolha com o H mudado |

**A consequência:** o R2 precisa de vidas novas para a T4, a T5 e a guarda. O R-a é feito antes, sem vida nova, e fecha a linha de base
(seção 4). Nada que o R-a responda é medido de novo aqui.

## 2. A pergunta, as hipóteses e as previsões

**A pergunta:** creditar o intervalo entre duas decisões, por um traço curto das decisões recentes, ensina ao pet o que vem depois da
ação, sem tirá-lo da comida?

| id | hipótese | previsão | o que a refuta |
|---|---|---|---|
| **H-T4** | com o R2, um efeito que segue o `comer` de uma classe com atraso fixo sobe o H do `comer` mais que o da ação que caiu no meio | D_T4 > 0 (seção 7.1) | D_T4 ≤ 0; ou o placebo de tempo sorteado dá o mesmo |
| **H-T5** | um tapa num horário independente da comida não derruba o H do `comer` nem o d̂ das classes | D_T5 "≈ 0" | D_T5 "< 0": o pet atribui à comida o que veio do dono |
| **H-G** | o R2 não piora o forrageio | a taxa por episódio, a privação e a exaustão "não piora" | qualquer uma com o IC acima do corte |

Os tamanhos são SEM FONTE.

## 3. O desenho

### 3.1 O que não muda

- O `engine.py`, o motor, o mundo do MVP, o reflexo do sono, o `tau_c` (INT-6), a digestão (a `taxa_digestao` fica como está; a
  digestão lenta é depois do R2, D-CI-1).
- A chave do PV-2 desligada (D-PV2R-13); a `ConfigElogio` desligada por padrão; a `VERSAO_PET`; os saves e os logs de hoje.
- **O cérebro:** o REL da C4 (`orq.config_do_braco("REL", ...)`), como no R1 e no PV-2.

### 3.2 O mecanismo (a seção 3 da tarefa, sem mudança)

- **A chave:** `ConfigDigibrain.traco_intervalo`, desligada. Os inatos `k_traco`, `lambda_traco`, `eta_int` e `k_base` ficam PROPOSTOS e
  SEM FONTE até a calibração (seção 8).
- **O traço:** as últimas `k_traco` opções, cada uma com o `e = z`, o comportamento e a classe; nasce com τ = S; decai `τ ← mul(λ, τ)` por
  decisão; a mesma opção volta a S sem somar.
- **O crédito:** `δ = clamp(div_arred(r_int − b, R_n), −S, S)`, com a linha de base `b` da seção 4, e
  `H[b_i, j] += mul(mul(g_apr, η_int), mul(mul(τ_i, δ), e_ij))`, com o corte em ±H_max.
- **Cada intervalo uma vez só:** o par (tick de `pc1_k`, tick de `pc0_{k+1}`) fica registrado; um teste confere.
- **A INT-5, uma estrutura de traço só:** a janela do ELOGIO (W decisões, o peso linear S − j·S/W) passa a ser um traço com a forma
  linear; o R2 usa a forma geométrica. Um teste confere que o ELOGIO ligado pelo traço dá o mesmo log que o código de hoje
  (`tests/gabaritos/elogio_de_hoje.json` desligado e um gabarito novo ligado, gravados antes da mudança). O registro separa o r do
  intervalo e o sinal do carinho.
- **Nenhuma rng nova e nenhum evento novo no log:** tudo é estado do cérebro, refeito pelo replay.

### 3.3 Os braços e os mundos

| braço | o que é |
|---|---|
| **OFF** | o REL de hoje, o `traco_intervalo` desligado |
| **R2** | o REL com o `traco_intervalo` ligado, nos inatos da calibração |

| mundo | para quê | o que tem |
|---|---|---|
| **M-T4** | a T4 | o mundo do MVP com um **emissor de teste** da bancada: uma classe de fruta, `c`, dá humor +X 30 ticks (2 decisões) depois de comida. Entre a comida e o efeito, o pet faz o que fizer; a contagem da seção 6 mostra que o `brincar` no meio é raro, e a T4 usa a ação do meio, qualquer que seja |
| **M-T4-placebo** | o controle da T4 | o mesmo emissor, com o efeito num tick sorteado pelo `u` do motor, sem relação com a comida (o placebo do PV-2) |
| **M-T5** | a T5 | o mundo do MVP com um **dono de teste** que dá um tapa por relógio, em ticks sorteados pela rng do ambiente, independente do que o pet comeu |
| **M-G** | a guarda | o mundo do MVP e as 12 células da C4 (4 donos × comedouro, `longe_fixo` e longe), sem emissor |

- **O emissor e o dono de teste são instrumentos da bancada** (`experiments/bancada/`), atrás de uma chave da bancada, como o placebo
  do PV-2. Não entram no `digilab/`, no jogo nem no corpo.
- **O X do emissor** é o humor de uma fruta (o `sinal_corpo` dela, sem ganho novo), PROPOSTO no PR do código, SEM FONTE.
- **A rng do emissor e do dono de teste** é a do ambiente, derivada por `derivar_semente` com um rótulo novo; trocar de braço não muda o
  mundo (a regra das rngs separadas).

### 3.4 A checagem do v38 (INT-8)

Na validação, um bloco ao lado com a config do v38 (`pv2.fabricas(..., v38=True)`), só nos lugares que ele tem (longe e `longe_fixo`), 40
unidades, OFF e R2. Descritivo, sem gate.

## 4. A linha de base (a fechar com o R-a)

**O problema:** a linha de base por contexto do R1 (acordado e dormindo) apaga o dormir por construção, e o dormir é o caso que motivou a
etapa (L-AÇÃO do R1). O plano não escolhe a linha de base no escuro: a escolha sai do replay R-a.

- **Quem faz:** a sessão da cadeia ([DigiBrain: análise da cadeia](#local_cdf5c69c-785f-4c0b-b670-3c7b6f196502)), pelo
  `docs/PLANO_ANALISE_V3_PET_VIVO_RA.md` (APROVADO, PR #1030; o código no PR #1032), sobre as vidas do HOJE da run do PV-2, sem vida nova
  e sem faixa. Em 2026-11-19 o replay ainda não rodou: espera os merges, o fim da C3 e o `pre_run`. **Este plano não repete o R-a e não
  muda nada nele.**
- **As candidatas são as do R-a (RB-1), nenhuma olhando a ação escolhida:**
  - GLOBAL, a média da vida (a do R1);
  - CTX, acordado e dormindo (a do R1, só como referência: dá 0 para o dormir por construção);
  - FASE, dia e noite, pelo tick do começo do intervalo;
  - ESTADO, o quartil da carga do corpo (a soma dos quadrados das faltas dos 11 receptores logo depois da ação);
  - MÓVEL-k, a média móvel exponencial dos `r_int_n` anteriores, sem o atual, com k = 4, 16 e 96 decisões; global, não por comportamento.
- **As saídas do R-a que este plano usa,** por linha de base e por lugar, com o IC95 (n 200): o resto do dormir, o η² entre os 7
  comportamentos, o η² do acordado (com o piso de 5 decisões por comportamento, RB-3) e o resto por comportamento, o do comer incluído.
  O R-a já lê duas coisas pela regra dele, escrita antes: a L-SONO (a linha de base "preserva o sono") e a L-ALÉM ("há o que creditar
  além do sono" ou "só o sono"). O desfecho que o R-a espera é "só o sono".
- **A regra de escolha do R2, escrita antes do resultado do R-a:**
  1. ficam as linhas de base que a L-SONO marca como "preserva o sono" (sem isso, o R2 não ensina o caso que o motivou);
  2. entre elas, se a L-ALÉM disser "há o que creditar além do sono", fica a que tem o maior limite de baixo do η² do acordado; se disser
     "só o sono", fica a de menos parâmetros, e no empate a MÓVEL (a única causal, a forma do PV-3);
  3. **se nenhuma preservar o sono,** o R2 para antes do código, e a leitura vai ao Matheus.
- **A forma causal no cérebro:** a GLOBAL, a FASE e a ESTADO do R-a são médias da vida inteira, que o pet vivo não conhece na hora. No
  R2, a escolhida vira uma média móvel por estrato (o estrato dela, com o `k_base` da calibração), sem olhar o intervalo atual. O k do
  R-a não escolhe o `k_base` (RB-2).
- **A leitura "só o sono" não para o R2 sozinha,** mas muda o que a T4 mede: o traço creditaria quase só o sono, e a guarda de forrageio
  vira o critério que mais pesa. Isso vai ao Matheus no adendo 1, com a recomendação.
- **Fora do R-a, e não pedido aqui:** a média móvel por comportamento e a energia em faixas de S/4. Se o adendo 1 precisar delas, é
  outro replay (~40 min) com um adendo próprio aprovado.
- **O adendo 1 deste plano** traz o resultado do R-a e a linha de base escolhida, antes do código.

## 5. O corpo e os donos

### 5.1 O corpo (a fechar depois do CHECKPOINT da C3)

- **Hoje,** o corpo das vidas do R1, do PV-2 e do R-a é o CTRL, o de hoje, sem a D, a E nem o teto; as leituras deles valem para ele.
- **A C3 da CORPO** roda até perto das 20:15 de 2026-11-19. Ela testa a ponte da falta de combustível com a D (a falta sobe a fome) e o
  teto novo (`ConfigTetoFomeCorpo`). Isso muda o que o corpo faz entre as decisões, no caminho da fome: é o que o R2 credita.
- **A regra, escrita antes do resultado da C3:**
  - se o CHECKPOINT da C3 mantiver o corpo de hoje, o R2 usa o CTRL;
  - se o Matheus escolher um corpo novo para o pet, o R2 usa esse corpo, e o R-a se refaz sobre ele se as vidas existirem;
  - o R2 **não** roda num corpo que ainda está em decisão.
- **O adendo 2** fecha esta seção depois do CHECKPOINT da C3, antes do código.

### 5.2 Os donos distintos por lugar

Contado nas sementes dos testes (seção 6), pelo sha256 do log de cada vida, e confirmado pelo R1 nas 200 unidades da run do PV-2:

| lugar | donos distintos por unidade | o par igual |
|---|---|---|
| comedouro | **3** em 10 de 10 (no R1, 200 de 200) | o incoerente sai igual ao atencioso, log a log |
| `longe_fixo` | 4 em 10 de 10 | nenhum |
| longe | 4 em 10 de 10 | nenhum |

- **A consequência:** a média das 12 células pesa o comedouro do atencioso duas vezes. A guarda do R2 (seção 10) lê as 12 células como
  na C4, para comparar com a VALUATION e a C4, e lê ao lado, rotulada, a média das **11 células distintas** (sem o incoerente no
  comedouro). Uma diferença de classe entre as duas vai ao relato.
- **Por que acontece:** no comedouro, o incoerente e o atencioso dão os mesmos gestos nas mesmas horas (os donos da C4 só alimentam, limpam
  e brincam; nenhum dá carinho nem tapa, seção 6). A causa exata é da sessão do corpo (o R-c da fila); este plano só a registra.

## 6. A contagem do evento da premissa, nas sementes dos testes

**As vidas da contagem:** o HOJE do PV-2 (o REL com o rastro do R1 ligado, só leitura), 14 dias, orçamento 16, nas 12 células da C4, nas
bases dos testes 101, 202, 303, 404 e 505 com k = 0 e 1 (prefixo `digibrain_prototipo`): 120 vidas, 7 min com 1 processo, ao lado da C3.
O script fica fora do repositório (só leitura, sem artefato de pesquisa); os números abaixo são descritivos e não entram em resultado.

| evento | média por vida | mínimo | mediana | por dono (média) |
|---|---|---|---|---|
| decisões | 1 343 | 1 343 | 1 343 | iguais |
| `comer` | 78,2 | 0 | 82 | atencioso 73,5; relapso 89,1; aleatório 74,4; incoerente 75,7 |
| `comer` seguido de outra ação nas 3 decisões seguintes | 77,4 | 0 | 81 | quase todo `comer` |
| `comer` seguido de um `brincar` nas 3 decisões seguintes | **4,1** | 0 | 4 | atencioso 6,2; **relapso 0,6**; aleatório 4,2; incoerente 5,6 |
| `dormir` | 621,6 | 551 | 628 | 603 a 644 |
| intervalos com tapa ou repreensão | **0** | 0 | 0 | 0 nos 4 |
| intervalos com carinho ou elogio | **0** | 0 | 0 | 0 nos 4 |

- **Os gestos que os donos da C4 dão:** só alimentar, limpar e brincar. **Nenhum tapa e nenhum carinho** em 120 vidas.
- **Três vidas do `longe_fixo` não comem nada nos 14 dias** (o incoerente nas bases 202 e 505, k = 0) ou quase nada (o atencioso na 303,
  7 vezes). Só descritivo; a morte está desligada.
- **Por lugar,** o `comer` seguido de `brincar` fica em 4,8 (comedouro), 4,3 (`longe_fixo`) e 3,4 (longe) por vida, e 21 % das vidas não
  têm nenhum.

**O que isso muda no desenho:**
- **A T4 com o `brincar` no meio fica abaixo do piso.** Com 4 eventos por vida em todas as classes de comida (e o emissor só numa classe),
  a medida "H do `brincar` que caiu no meio" teria perto de 1 evento por vida, e quase 0 no relapso. **A T4 compara o `comer` com a ação
  do meio, qualquer que seja:** A = h_comer − h_meio, com h_meio a média de h nos comportamentos das decisões entre a comida e o efeito
  (seção 10.1). O `brincar` fica como recorte descritivo.
- **A T5 não tem premissa nas vidas de hoje:** sem tapa nenhum, ela só existe com o dono de teste (M-T5, seção 3.3).
- **O ELOGIO não entra nas vidas da guarda:** os donos da C4 não dão carinho, então o traço do R2 não recebe sinal de carinho em M-G. A
  INT-5 se testa pelo gabarito (seção 3.2), não pela run.

**Os pisos, escritos antes, conferidos na fumaça do PR do código (falha alta abaixo deles):**
- **T4:** no M-T4, a mediana dos eventos "comida da classe c seguida de outra ação antes do efeito" ≥ 10 por vida, e ≥ 90 % das vidas
  com pelo menos 1, em cada dono;
- **T5:** no M-T5, ≥ 20 tapas por vida (o dono de teste dá 2 por dia, PROPOSTO, SEM FONTE), e ≥ 3 deles por vida dentro das 4 decisões
  depois de um `comer` (para haver o que atribuir errado);
- **a guarda:** ≥ 5 episódios de fome por vida na mediana de cada célula (a VALUATION teve 13 a 18 no `longe_fixo`).

## 7. A precisão, calculada antes

**A conta é a da A6.5** (`run_v2_longe_regular.margem_efetiva`): a margem efetiva é (t₀,₉₅ + z₀,₈) × dp / √N, o menor efeito com poder 0,8.
Ela tem de ficar abaixo de δ = 0,032.

### 7.1 A guarda, com o dp de uma run anterior da mesma célula

A run mais parecida é a V3 da VALUATION (73xxx): o CON contra o REL, nas mesmas sementes, uma mudança no cérebro que mexe no sono e na
fome, como o R2. O dp das diferenças por unidade (`artifacts_v3_valuation/conserto/resultado.json`):

| medida | dp, `longe_fixo` | margem efetiva com N = 200 | dp, 12 células | margem efetiva com N = 200 |
|---|---|---|---|---|
| taxa por episódio | 0,088 | 0,016 | 0,043 | 0,008 |
| privação | 0,065 | 0,011 | 0,046 | 0,008 |
| exaustão | 0,099 | 0,017 | 0,046 | 0,008 |

**N = 200 basta para a guarda:** a margem efetiva fica entre 0,008 e 0,017, abaixo de 0,032, se o dp do R2 for parecido com o do conserto.
Com o dp até 1,8 vez maior, ainda cabe.

### 7.2 A T4 e a T5, sem run anterior

- **Nenhuma run mediu A(braço, mundo)**, então não há dp. A calibração mede o dp de D_T4 e de D_T5 na célula escolhida.
- **A regra, escrita antes:** o N da validação é o menor N ≥ 200 com a margem efetiva ≤ 0,032 pelo dp da calibração, até o teto de 400
  unidades.
  - **Se o N passar de 400,** o plano escreve que "indeterminado" é o desfecho provável, e o Matheus decide por adendo antes da validação:
    rodar com 400, ou parar.
- **Uma referência só ilustrativa, de outra medida:** no ELOGIO, a M2 (E-imed − E-sorteado) teve o dp perto de 0,22. Com esse dp, N = 200
  daria 0,039, e o N pela regra seria cerca de 300.

### 7.3 O custo previsto

| fase | vidas por unidade | unidades | vidas | tempo com 4 processos (pela V4, 7 200 vidas em 1 h 13) |
|---|---|---|---|---|
| calibração | 8 células × (M-T4 e placebo) × 4 donos + OFF; a guarda no `longe_fixo` | 100 | cerca de 10 400 | cerca de 1 h 45 |
| validação | M-T4, placebo e OFF; M-T5 com e sem tapa; M-G nas 12 células, OFF e R2 | 200 a 400 | 8 800 a 17 600 | 1 h 30 a 3 h |
| v38 | OFF e R2, 2 lugares × 4 donos | 40 | 640 | cerca de 7 min |

## 8. A calibração e a validação

- **A calibração** escolhe os inatos do traço numa grade pequena, nas sementes dela:
  - `k_traco` ∈ {2, 4}, `lambda_traco` ∈ {S/4, S/2}, `eta_int` ∈ {η_h/4, η_h/2}: 8 células;
  - o `k_base` é o da linha de base escolhida no adendo 1;
  - só a T4 (M-T4, R2 contra OFF) e a guarda (M-G, só o `longe_fixo`);
  - **a regra:** entre as células em que a guarda passa, a de maior D_T4; no empate dentro de 0,01, a de menor `eta_int`;
  - **o dp de D_T4 da calibração dimensiona o N da validação** (seção 7).
- **A validação,** uma vez, na célula escolhida: a T4 (com o placebo), a T5, a guarda nas 12 células e a checagem do v38.
- **As faixas** são pedidas ao coordenador depois da aprovação e entram no `FAIXAS_RESERVADAS` antes da run.

## 9. A medida de bem-estar (decisão do Matheus)

- **O que mudou:** a síntese da EVIDENCIA (#974, aberto) conclui que "o diferencial não está na taxa de fechamento por episódio" e que,
  para dizer que o modular cuida melhor de si, "a medida tem de ser outra (bem-estar), definida num plano novo antes de rodar". Três runs
  seguidas deram "o primário sobe, a guarda reprova" ou "indeterminado" com a taxa por episódio como primária.
- **Neste plano, a guarda é tripla:** a taxa por episódio, a privação e a exaustão, cada uma com o seu corte. Nenhuma é o primário: o
  primário é a T4.
- **A decisão do Matheus, CI-R2-6:**
  - **(a) recomendada:** manter as três como guarda, cada uma com o corte da seção 10, sem medida composta. Custo baixo; não espera a
    EVIDENCIA.
  - **(b)** trocar a guarda por uma medida de bem-estar única, definida pela EVIDENCIA antes deste plano rodar. Custo: o R2 espera o
    merge do #971 e do #974 e um plano novo da medida.
  - **(c)** acrescentar uma medida composta ao lado, descritiva. Custo: uma conta nova no `metrics.py`, sem regra.

## 10. A regra de leitura, escrita antes

### 10.1 As medidas

- **A(braço, mundo):** por vida, a média, nas decisões dos 2 últimos dias com a fome urgente, de (h_comer − h_meio) / H_max, com
  h_b = Σ_j H[b, j] · z_j na decisão e h_meio a média de h nos comportamentos que caíram entre a comida da classe c e o efeito, pesada
  pela frequência deles na vida (seção 6). O recorte só com o `brincar` fica descritivo. A conta vai ao `metrics.py` no PR do código, sem mudar depois da calibração.
- **D_T4 (o primário):** A(R2, M-T4) − A(R2, M-T4-placebo), pareado pela unidade. O placebo é o controle estrito: o mesmo traço, o mesmo
  efeito, só sem a ligação no tempo com a comida.
- **D_T4-off (secundário):** A(R2, M-T4) − A(OFF, M-T4).
- **D_T5:** a média, nas mesmas decisões, de h_comer / H_max e do d̂ das classes consumidas, R2 em M-T5 menos R2 no mesmo mundo sem o tapa.
- **A guarda:** R2 − OFF em M-G, na taxa por episódio (`episodios_fome.taxa`), na privação e na exaustão, nas 12 células e no
  `longe_fixo`.

### 10.2 As classes e a leitura

As classes são as de A6.6 (`run_v2_longe_regular.classe`), com o IC95 pelo t pareado sobre as unidades; o bootstrap e o g1 ao lado,
rotulados. As margens são SEM FONTE: δ_T4 = δ_T5 = 0,032 (em fração de H_max) e δ_G = 0,032 (a régua da A1, da C4 e da VALUATION).

| critério | passa se | leitura se falha |
|---|---|---|
| **T4** | D_T4 "> 0" | "≈ 0" ou "indeterminado": o traço não liga o efeito à ação certa; "< 0": liga ao contrário |
| **T5** | D_T5 "≈ 0" nas duas medidas | "< 0": o pet culpa a comida pelo tapa |
| **G, taxa** | o limite de baixo do IC95 de R2 − OFF > −0,032 | o R2 tira o pet da comida |
| **G, privação e exaustão** | o limite de cima do IC95 de R2 − OFF < +0,032 | o R2 piora o bem-estar (o caso do conserto da VALUATION) |

**A leitura do R2:**
- **"ensina sem custo":** a T4, a T5 e as quatro guardas passam;
- **"ensina com custo":** a T4 passa e alguma guarda falha. O traço não vai a nenhum pet sem um conserto novo, com plano;
- **"não ensina":** a T4 não passa. O R2 para, e a digestão lenta continua sem caminho (D-CI-1);
- a T5 falhando entra junto, como "atribui errado", em qualquer uma das três.

**O que a leitura não faz:** nenhuma leitura liga o traço no jogo. A web só depois da validação e de uma decisão do Matheus.

## 11. Se algo falhar

Uma falha alta para a run, que volta ao Matheus com o comando, a saída e a lacuna. Falha alta é qualquer uma destas:
- o replay (o G1 com o traço ligado);
- o gabarito de hoje com o `traco_intervalo` desligado, byte a byte;
- o `elogio_de_hoje.json` com a `ConfigElogio` desligada;
- um intervalo creditado duas vezes;
- a premissa da seção 6 abaixo do piso.

Nada se conserta para o número sair.

## 12. Uma vez, e o que fica no git

- **A validação roda uma vez.** O orquestrador recusa gravar por cima de uma pasta que existe.
- **Em `artifacts_v3_credito_intervalo/<fase>/`:** o `meta.json` (o commit, o `git_limpo`, o comando, as versões, os sha256 do plano, da
  config, do orquestrador e dos artefatos), o `resultado.json`, o `medidas.json` e o `vidas.tar.gz` determinístico; as vidas soltas fora
  do git.
- **O resultado** vai em `docs/RESULTADO_V3_CREDITO_INTERVALO.md`.
- **A ordem dos PRs** (a seção 5 da tarefa): este plano; os adendos 1 e 2; o gabarito de hoje num commit próprio e o código; a calibração;
  a validação; o resultado.
- **A máquina:** uma run de pesquisa por vez, no máximo 4 processos, pelo `pre_run`; o espaço livre no D: conferido antes de soltar.

## 13. As decisões para o Matheus

| id | decisão | a recomendação | o custo de errar |
|---|---|---|---|
| CI-R2-1 | o desenho: OFF e R2; os mundos M-T4, M-T4-placebo, M-T5 e M-G; o primário D_T4 contra o placebo | sim | sem o placebo, a T4 não separa a ligação no tempo do simples crédito a mais |
| CI-R2-2 | o emissor e o dono de teste como instrumentos da bancada, fora do `digilab/` | sim: o jogo e o corpo não mudam | dentro do `digilab/`, uma mecânica nova sem pedido |
| CI-R2-3 | a linha de base pela regra da seção 4, fechada no adendo 1 com o R-a | sim | escolher sem o R-a repete o 0 do dormir por construção |
| CI-R2-4 | o corpo pela regra da seção 5.1, fechado no adendo 2 depois da C3 | sim | calibrar num corpo que depois muda |
| CI-R2-5 | a T4 contra a ação do meio, qualquer que seja (o `brincar` só descritivo), e os pisos da seção 6, com a falha alta abaixo deles | sim: o `comer` seguido de `brincar` tem 4 eventos por vida, quase 0 no relapso | com o `brincar` só, a T4 ficaria sem evento; sem piso, uma T4 vazia sairia "≈ 0" |
| CI-R2-6 | a guarda de bem-estar (seção 9) | (a): as três guardas separadas | (b) atrasa o R2 até a medida da EVIDENCIA; sem guarda, repete o conserto da VALUATION |
| CI-R2-7 | a precisão e o teto do N (seção 7) | sim | sem o teto, uma validação de horas; sem a conta, outro "indeterminado" |
| CI-R2-8 | a grade da calibração e a regra de escolha (seção 8) | sim | uma grade maior custa horas; a regra depois dos números deixa de valer |
| CI-R2-9 | as margens δ = 0,032 (seção 10) | sim: a régua das runs anteriores | outra margem: o R2 deixa de comparar com a VALUATION e a C4 |

## 14. Referências

As da seção 2 da análise da cadeia, sem nenhuma nova: o traço de elegibilidade de três fatores (Izhikevich 2007,
`10.1093/cercor/bhl152`; Gerstner et al. 2018, `10.3389/fncir.2018.00053`; Frémaux e Gerstner 2016, `10.3389/fncir.2015.00085`) só na
forma; nenhum número se transfere. O "substituir em vez de somar" tem só a pista do título de Singh e Sutton 1996 (`10.1007/bf00114726`).
A recompensa homeostática é a de Keramati e Gutkin 2014 (`10.7554/eLife.04811`), que já é o r do modular. Os cortes e as margens são SEM
FONTE.

## Adendo 1: a linha de base, com o R-a (APROVADO, 2026-11-20)

**Status: APROVADO pelo Matheus em 2026-11-20,** nesta sessão: "Aprovo e confirmo". As AD1-1 a AD1-3 ficam DECIDIDAS pela recomendação: a MÓVEL global, o `k_base` ∈ {16, 96} na grade da calibração (16 células), e seguir o R2 com o descritivo do sono. Escrito como PROPOSTO. Escrito em 2026-11-19 (Claude Code, Opus 5.5, branch `v3-credito-intervalo-adendo1`), depois de a sessão da cadeia
avisar que o replay do R-a rodou. Nada do plano acima muda além do que este adendo diz. Nenhuma vida antes da C4 (o adendo 2).

**A fonte:** o [RESULTADO_V3_PET_VIVO_RA.md](RESULTADO_V3_PET_VIVO_RA.md) e o `artifacts_v3_pet_vivo/ra/run/resultado.json`, no PR
#1036 (branch `v3-pet-vivo-ra-resultado`, commit `4b639fd1`), **ainda sem merge.** Os números abaixo vêm daquele documento e não foram
reconferidos aqui contra o `resultado.json`. Este adendo só vale depois do merge do #1036; se o resultado mudar antes, o adendo é
refeito.

### A1.1 O que o R-a deu (o HOJE, n 200 por lugar, IC95)

- **L-SONO:** a FASE, a ESTADO e as MÓVEL com k 4, 16 e 96 "preservam o sono". O resto do dormir fica entre +153,7 e +165,5, com o
  limite de baixo acima de 0 nos 3 lugares. A GLOBAL dá +156,1 a +159,4; só a CTX dá 0.
- **L-ALÉM: "só o sono".** O η² do acordado fica entre 0,014 e 0,034; o maior limite de cima é 0,037 (MÓVEL-16, `comedouro`), abaixo
  do corte de 0,05 (SEM FONTE) em todas.
- **A H-MÓVEL não se confirma:** a MÓVEL-4 não apaga o sono. No HOJE ela dá o maior resto do dormir; na checagem do v38 (n 40,
  descritivo), o menor, de +84 a +96.
- **O R-a não separa uma linha de base melhor entre as cinco.** A FASE difere da GLOBAL em menos de 0,4 no resto do dormir.
- O OLF-0 lê igual.

### A1.2 A regra da seção 4, aplicada como escrita

1. **Ficam as que preservam o sono:** a FASE, a ESTADO, a MÓVEL-4, a MÓVEL-16 e a MÓVEL-96. O passo 3 (parar o R2) não se aplica.
2. **"Só o sono" → a de menos parâmetros, e no empate a MÓVEL.** Na forma causal da seção 4, cada uma vira uma média móvel por estrato:
   - a FASE, 2 estratos (dia e noite);
   - a ESTADO, 4 estratos, mais os 3 cortes dos quartis da carga, que o R-a tirou da vida inteira e o pet vivo não conhece;
   - a MÓVEL, 1 estrato, global.

   A MÓVEL é a de menos parâmetros e a única causal já no R-a. **Fica a MÓVEL global:** b é a média móvel exponencial dos `r_int_n`
   anteriores, sem o intervalo atual, começando em 0 (D-RB-6). A GLOBAL do R-a, na forma causal, é esta mesma.

### A1.3 O `k_base`: uma inconsistência do plano, a decidir (AD1-2)

A seção 4 diz que o `k_base` sai "da calibração", e o RB-2 diz que o k do R-a não o escolhe. A grade da seção 8 não tem o `k_base`.
As duas saídas:

- **(a) recomendada:** pôr o `k_base` ∈ {16, 96} na grade da calibração, que passa de 8 para 16 células. O k 4 fica fora: no v38 ele é
  o que mais encolhe o resto do dormir (descritivo, n 40), e o R-a usa o v38 só como checagem. O R-a delimita a faixa; não escolhe o
  valor. O custo: a calibração passa de cerca de 10 400 para cerca de 20 800 vidas, de 1 h 45 para cerca de 3 h 30 (estimativa pela
  seção 7, SEM FONTE). A regra de escolha da seção 8 não muda: no empate dentro de 0,01, o menor `eta_int` e, depois, o maior `k_base`
  (a média mais lenta, mais perto da GLOBAL do R1).
- **(b)** fixar `k_base` = 16, PROPOSTO, SEM FONTE. A calibração segue com 8 células. O custo de errar: um k que acompanha o bloco de
  sono pode encolher o crédito do dormir no corpo de depois da C3, e o R2 não veria isso.

### A1.4 O que "só o sono" muda no R2 (AD1-3)

A seção 4 pede esta decisão. Nas vidas da C4 (M-G), o traço vai creditar quase só o dormir: o resto do dormir é de cerca de +155, e o
das ações acordadas é quase igual entre elas. A T4 não depende disso: o M-T4 é um mundo de bancada com o emissor do humor atrasado, e
mede se o mecanismo ensina a ação do meio.

- **(a) recomendada:** seguir o R2 como está. Na M-G, a guarda de forrageio e a de exaustão viram o critério que mais pesa, porque um
  crédito positivo ao dormir pode puxar o pet a dormir mais e a comer menos. A leitura "ensina com custo" da seção 10 já cobre esse
  caso. Acrescenta-se só um descritivo, sem regra: a fração dos ticks dormindo, R2 − OFF, nas 12 células. Custo baixo: uma conta.
- **(b)** parar o R2 aqui: o que sobra para ensinar é o sono, e o reflexo do sono já o decide no corpo de hoje. O custo de errar: o
  ELOGIO (INT-5) espera o mesmo traço e fica parado junto.

### A1.5 As decisões para o Matheus

| id | o quê | recomendação | custo de errar |
|---|---|---|---|
| AD1-1 | a linha de base: a MÓVEL global, pela regra da seção 4 | sim | outra escolha contraria a regra escrita antes do R-a |
| AD1-2 | o `k_base`: (a) na grade, {16, 96}; (b) fixo em 16 | (a) | (a) custa ~1 h 45 a mais; (b) arrisca um k que encolhe o crédito do sono |
| AD1-3 | "só o sono": (a) seguir, com o descritivo do sono; (b) parar o R2 | (a) | (a) gasta a calibração num crédito que talvez só mova o sono; (b) para o ELOGIO junto |

## Adendo 2: o corpo, depois do CHECKPOINT da C3 (APROVADO, 2026-11-20)

**Status: APROVADO pelo Matheus em 2026-11-20,** nesta sessão: "Aprovo e confirmo". A AD2-1 fica DECIDIDA na opção (a), esperar a C4, e o CHECKPOINT "Levar o DTB à C4" fica confirmado aqui. Escrito como PROPOSTO. Escrito em 2026-11-20 (Claude Code, Opus 5.5, branch `v3-credito-intervalo-adendo1`). Nada do plano acima muda além
do que este adendo diz.

**A fonte:**
- o [RESULTADO_V3_CORPO_C3.md](RESULTADO_V3_CORPO_C3.md), no PR #1035 (branch `v3-corpo-c3-run`, commit `ff8f04cd`), **ainda sem merge**;
- o CHECKPOINT da C3, decidido pelo Matheus na sessão coordenadora e repassado a esta sessão: "Levar o DTB à C4". Por ser repassado, ele
  se confirma com o Matheus nesta sessão, junto com a AD2-1.

### A2.1 O que a C3 deu e o que o Matheus decidiu

- **O DTB (a D com o teto em C/2, PROPOSTO, SEM FONTE) saiu em "ganho"** (F +0,120 [+0,105; +0,135], nenhuma das oito guardas reprova).
  **O DTL saiu em "perda".**
- **O DTB não está validado:** a C3 é a run que escolheu o braço, e a validação é a C4, em sementes novas, com plano novo da sessão do
  corpo. Nada foi ligado no jogo.
- **O CHECKPOINT:** "Levar o DTB à C4". O corpo do pet fica, então, **em decisão até a C4.**

### A2.2 A regra da seção 5.1, aplicada como escrita

A seção 5.1 diz: "o R2 **não** roda num corpo que ainda está em decisão". Depois do CHECKPOINT, nem o CTRL nem o DTB são o corpo
decidido: os dois dependem da C4. A regra, sozinha, faz o R2 esperar a C4:
- **se a C4 validar o DTB** e o Matheus o escolher, o R2 usa o DTB, e o R-a se refaz sobre ele (as vidas da C4 existem). É outro replay,
  de cerca de 40 min, com um adendo próprio. A contagem da premissa (seção 6) também se refaz nas sementes dos testes, com o DTB: cerca de
  10 min, só leitura. O dp da guarda (seção 7.1) passa a sair da C4;
- **se a C4 não validar o DTB,** o R2 usa o CTRL, e o adendo 1 vale como está.

### A2.3 A decisão para o Matheus (AD2-1)

- **(a) recomendada: esperar a C4.** O R2 roda no corpo que sair dela, pela regra acima. Custo: o R2 espera o plano e a run da C4 (cerca
  de 2 a 3 h de máquina, estimativa pela C3), mais o replay do R-a se o DTB ficar.
- **(b) rodar o R2 agora no CTRL.** Contraria a regra da seção 5.1 e pede a mudança dela. Custo de errar: se o DTB passar na C4, o R2
  credita um caminho da fome que o pet não tem mais, e a calibração e a validação se refazem (de 3 a 6 h).
- **(c) rodar o R2 nos dois corpos, o corpo como fator.** Também contraria a regra. Custo: a calibração e a validação dobram. Metade da
  conta se perde quando a C4 decidir.

| id | o quê | recomendação | custo de errar |
|---|---|---|---|
| AD2-1 | o corpo do R2 depois de "Levar o DTB à C4" | (a), esperar a C4 | (b) e (c) gastam horas num corpo que a C4 pode trocar; (a) só atrasa |
