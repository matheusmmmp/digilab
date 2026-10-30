# ESPEC — COMBATE-TR: a batalha em tempo real como o combate do jogo (R0, 2026-10-29)

Tarefa: `docs/TAREFA_V2_COMBATE_TR.md` (etapa R0). Worker: Claude Code, Opus 5.5, worktree `v2-combate-tr`. Status: as decisões D-1 a D-9
(seção 8) foram **DECIDIDAS** pelo Matheus em 2026-10-29, como recomendadas; os números seguem PROPOSTOS, menos os da D-5. Na R0, nenhum código de jogo mudou; a única peça nova foi a
medida do custo (item 4), com o script e a saída em disco.

Leia junto: a seção 3 da tarefa (o levantamento), `web/app/motor/combate.ts` (o combate por turnos V2.1), `web/app/arena/sim.ts` (a
simulação do #446) e `docs/historico/claude/combate.md`.

**A ideia em cinco linhas.** A luta continua sendo do DigiLab: o Guts, as ações, as técnicas, as passivas e os atributos do `perfilDe`.
O que muda é o relógio: o turno vira um tempo de ação **T = 2 s**, cada ação ocupa o lutador por um tempo, os dois lados agem sem se
esperar, e a distância vira posição. O pet e o rival são comandados pela lista de regras SE/ENTÃO, avaliada quando o lutador fica livre.
Do Digimon UP vêm só o desenho, ou seja, o clipe, o instante do golpe dentro do clipe, o projétil e o efeito (E5). **O resultado da luta
não depende dos dados do UP,** e o replay não precisa da pasta `Assets/` (D-1). O log grava o mesmo `"l"`, e o replay refaz a luta: a
medida dá 3 a 5 ms por luta de 100 s.

## 0. As convenções desta espec

- **T** é o tempo de turno: **2 000 ms = 125 passos de 16 ms.** PROPOSTO. Fonte: o ciclo de ataque padrão do protótipo
  (`arena/constantes.ts`, `STATS_PADRAO.cad` = 2 000 ms), igualado a 1 turno, em que hoje cabe um golpe rápido. Todo número "por turno"
  de hoje vira "por T", e todo "N turnos" vira "N × T". É essa conversão que a coluna "fonte" chama de **"turnos × T"**.
- **O passo** é o da arena: 16 ms (`PASSO_MS`, PROPOSTO, fonte: a medição do `arena_equilibrio.md`). O `dt` do quadro da tela nunca entra
  na simulação.
- **"Livre"** quer dizer que o lutador não está em ação nem atordoado: só aí ele decide.
- Números com status **PROPOSTO** e fonte, ou **SEM FONTE**. Nenhum deles foi calibrado: o equilíbrio fica para a rodada do fim.
- **"hoje"** é o combate V21E dos pets v9–v12 (`regrasDaVersao(9..12)`). As variantes V21C e V21D dos pets v1–v8 saem com o descarte (E2,
  item 6).

## 1. A tabela, mecânica por mecânica

Uma linha por mecânica da seção 3 da tarefa. "Como fica" descreve a R1. Na coluna "número", a fonte vem entre parênteses.

### 1.1 O lutador e os recursos

| mecânica (hoje) | como fica em tempo real | número PROPOSTO (fonte) |
|---|---|---|
| 6 atributos → `perfilDe` (hpMax, guts0, gutsMax, regen, mPerto, mDisparo, mGuarda), com o multiplicador de estágio | **igual**: o `perfilDe` e o `perfilNPC` de hoje dão o perfil (E5). Os status do UP (hp, atk, def, crit, esquiva, atordoa) não entram | os de `CV21` (os de hoje) |
| Guts: custo por ação | gasto **no começo** da ação; sem Guts, a ação é ilegal, como hoje | `CV.custo`, `CV21.custo` (os de hoje) |
| Guts: regeneração por turno | contínua: `regen / T` por segundo, somada a cada passo | `regen / 2` por s (turnos × T) |
| Guts: +5 ao defender | entra no fim da postura de defesa (e +3 na muralha) | `CV.gutsDef`, `CV21.muralha` (os de hoje) |
| Guts: +25 ao carregar | entra no fim da ação de carregar | `CV.gutsCarregar` (o de hoje) |
| Vida, morte (KO) | KO com a vida ≤ 0; os dois no mesmo passo dão empate, como hoje (`fimV2`) | — |
| Limite de 40 turnos | **limite por tempo:** 40 × T | **80 s** (turnos × T) |
| Morte súbita a partir do turno 25, dano × 1,5 | a partir de 25 × T, todo dano × 1,5 | **50 s**, × 1,5 (turnos × T; `CV.multMS`) |
| Limite: do desafiado (pets v6+), senão pela fração de vida | **igual** (`Desafiado`) | — |
| Escala da campanha (dano × E_oponente / E_próprio) | **igual**, aplicada a cada golpe que acerta | `escalaDe` (a de hoje, `CESC_V9`) |
| Condição do cuidado (vida e Guts × 0,95–1,05) | **igual**, no `perfilDe` | `CCOND` (o de hoje) |
| Pontos de treino | **igual**, no `perfilDe` (normalizado na arena, absoluto na campanha) | `CTR.pesoPontoCombate` (o de hoje) |
| Lutas seguidas sem cura (Cidadela, Liga, instalações, Fábrica) | **igual**: a vida e o Guts do fim de uma luta são o `ini` da seguinte; a cura parcial da Liga dos v9 também | `curaLiga` (o de hoje) |

### 1.2 O espaço: as 3 distâncias

| mecânica (hoje) | como fica | número PROPOSTO (fonte) |
|---|---|---|
| perto / médio / longe | **faixas de distância real** entre os centros dos dois, num chão plano (a elipse da arena, sem obstáculos: E7) | perto ≤ **62 px** (`EQ.alcanceCorpo` 44 + `EQ.raio` 18); médio ≤ **150 px** (`ACAO.alcanceDist`); longe > 150 px |
| começa em médio | os dois entram a 130 px um do outro | **±65 px** do centro (`estadoV2`: dist = 1); SEM FONTE para o valor exato |
| avançar / recuar (1 faixa por turno) | movimento contínuo na direção do rival (ou contrária), durante a ação | velocidade **70 px/s** igual para todos (`STATS_PADRAO.vel`, PROTOTIPO): 140 px por T, cerca de uma faixa |
| "avançar ilegal em perto, recuar ilegal em longe" | igual, pela faixa do momento da decisão; avançar para ao entrar em perto | — |
| fuga condicionada: recuar não afasta se o rival avança | **recuo mais lento que o avanço:** quem recua anda a 80%, e quem avança o alcança | recuo **0,8** (SEM FONTE; a arena de hoje usa `EQ.recuo` = 1) |
| a cerca | a elipse da arena prende os dois (`nucleo.prender`); recuar contra a cerca não afasta | `ELIPSE` (PROTOTIPO) |
| corpos não se sobrepõem | igual ao `passo()` de hoje | `EQ.raio` (EQ) |

### 1.3 As ações

Cada ação dura um tempo e ocupa o lutador. O efeito cai num **instante** dentro dela: o instante do golpe do clipe do UP, como fração do
clipe, aplicado à duração do DigiLab (D-1). Os números de dano são os de hoje.

| ação (hoje) | como fica | duração; instante (fonte) |
|---|---|---|
| golpe rápido (perto, 8 × mPerto, custo 10) | golpe corpo a corpo: acerta se o rival estiver em perto e à frente no instante do golpe; senão, é golpe no ar | T; instante = fração do `Attack_1` do Digimon (UP, só a fração) |
| preparar pesado → pesado (perto, 25 × mPerto, custo 15) | **preparo interrompível** de T, com o clipe `Skill_1` parado no começo; depois, a execução de T. O golpe cai no instante dela e só acerta em perto; fora de perto, erra (`errou`), como hoje | T + T (turnos × T) |
| interromper o preparo | golpe rápido, investida ou finta que **acerta** durante o preparo o interrompe (sem pele dura): o lutador vai para `Stun` por T/4 e perde o Guts do preparo | atordoamento **500 ms** (SEM FONTE) |
| fintar (no turno do pesado) | troca a execução do pesado por um golpe rápido que acerta quem esquiva e não quebra a guarda, como hoje | T |
| disparo (médio ou longe, 6 × mDisparo, custo 20) | **projétil** que sai no instante e viaja em linha reta até o rival; acerta se não for esquivado | T; projétil a **300 px/s** igual para todos (SEM FONTE). O desenho do projétil é do UP (E5) |
| defender | **postura** de T: todo golpe que acerta nela leva × 0,3 (pesado × 0,6) × mGuarda; golpe rápido ou finta contra a defesa devolve 5 ao atacante (parry); a investida contra a defesa é aparada (× 0, e quem investiu não avança) | T (`CV.multDef`, `CV.multDefPesado`, `CV.parry`, `CV21.parry`) |
| esquivar | **janela** de T: o pesado e o disparo que caem nela não acertam (o duelista leva 4 e recupera o Guts do preparo, como hoje); o golpe rápido acerta | T; o desenho é o dash de desvio do protótipo (`ACAO.desvioCpuMs` 180 ms) |
| carregar | postura de T: o dano recebido nela é × 1,5; +25 de Guts no fim | T (`CV.multCarregar`) |
| a regra final (`sempre → defender` ou `carregar`) | igual: é o que o lutador faz quando nenhuma regra vale | — |

### 1.4 As técnicas (adolescente em diante) — habilidades com recarga

Hoje a "recarga" das técnicas é a duração do efeito (não se marca quem já está marcado, não se usa pele dura com pele ativa) mais o Guts.
**A proposta não cria recarga nova**: a recarga é a mesma regra, em tempo.

| técnica (hoje) | como fica | número PROPOSTO (fonte) |
|---|---|---|
| investida (só em médio, 8 × mPerto, custo 20) | arrancada até perto e golpe no fim; a defesa a apara (× 0, sem avanço) | T (turnos × T); arrancada a **420 px/s** (`ACAO.investidaJogador`, PROTOTIPO) |
| contra-golpe (perto; em qualquer distância no espelho; custo 15) | postura de T: o golpe corpo a corpo que acerta nela é reduzido como na defesa e devolve 0,5 do bruto (1,0 no bastião); no espelho, o disparo também devolve | T (`CV21.fracCG`, `CSO.fracBastiao`, `CV21.espelho`) |
| marcar (médio ou longe, sem marca ativa, custo 10) | a marca dura 3 × T; o próximo disparo dela tem × 2 e ignora a redução da postura; ela se perde ao levar golpe corpo a corpo ou **ao entrar em perto** | **6 s** (turnos × T; `CV21.turnosMarca`, `CV21.multMarca`) |
| pele dura (sem pele ativa, custo 20) | por 2 × T, todo dano recebido × 0,5, e o preparo não é interrompido | **4 s** (turnos × T; `CV21.turnosPele`, `CV21.multPele`); colosso partido 3 × T = 6 s |

### 1.5 As passivas (formas adultas e sombrias) — modificadores

| passiva (hoje) | como fica | número PROPOSTO (fonte) |
|---|---|---|
| duelista: o pesado esquivado ainda dá 4 e devolve o Guts do preparo | igual, no instante do pesado | `CV21.duelista` |
| furioso: corpo a corpo × 1,25 com vida < 50%; não defende | igual | `CV21.limFurioso`, `CV21.multFurioso` |
| espelho: contra-golpe em qualquer distância; devolve o disparo | igual | `CV21.espelho` |
| muralha: +3 de Guts ao defender | igual | `CV21.muralha` |
| sentinela: recuar com a passiva pronta afasta de quem avança e para o avanço dele; recarga de 4 turnos | o recuo da sentinela pronta é a 100% e trava o avanço do rival pela ação; recarga **8 s** | 4 × T (`CV21.recargaSent`) |
| emboscador: o primeiro disparo da luta × 2 | igual | `CV21.multEmb` |
| vigia: vê a intenção do rival (`oponente_vai_preparar`) | igual: a intenção é o que a lista do rival escolheria agora, sem ε e sem RNG, calculada no passo da decisão do vigia | — |
| titã: pesado × 1,3 | igual | `CV21.multTita` |
| devastador (sombria): corpo a corpo × 1,3; não defende, não esquiva | igual | `CSO.multDev` |
| bastião rachado (sombria): o contra-golpe devolve 1,0; defender não dá Guts | igual | `CSO.fracBastiao` |
| predador (sombria): disparo × 1,4; não recua | igual | `CSO.multPred` |
| colosso partido (sombria): regen × 0,85; pele dura de 3 turnos | igual, em tempo | `CSO.multRegenColosso`; 6 s |
| sombria: ε ≥ 0,2 | igual (item 2) | `CSO.epsMin` |

### 1.6 As regras de luta das versões e os itens

| mecânica (hoje) | como fica |
|---|---|
| V21D/V21E: o preparo sob pele não aparece em `oponente_preparando`; as listas variantes da muralha, do vigia, do duelista, do titã e do espelho | **ficam todas ligadas** (são as regras dos pets v9–v12, as de hoje). As listas variantes ficam em `bots.ts` como estão |
| V21C, V21D sozinha (pets v1–v8) | **saem**, com o descarte (item 6) |
| carta de Fôlego (+Guts no começo) | igual (`comCarta`) |
| carta de Foco (ε = 0) | igual |
| carta de Cura (abaixo de x da vida, cura y, uma vez) | conferida a cada passo, depois do dano do passo; o resto, igual |
| chips de stat e de regra (pets v6+, v9) | iguais: o stat entra no `perfilDe`, e a regra entra no fim da lista (`comChips`) |
| itens só com o treino mínimo (v9) | igual |

### 1.7 O que sai da simulação de hoje (`arena/sim.ts`)

| peça da arena do #446 | destino | por quê |
|---|---|---|
| dano do UP (atk, def, variação ±10%, crítico, esquiva e atordoamento por sorteio, triângulo de atributos, `fatorRitmo`) | **sai da luta** | E5: os atributos são os do DigiLab. Com isso, a luta não sorteia nada além do ε |
| IA da CPU (`desviar`, mira com erro, `cpuTroca`, contorno de obstáculo, dificuldade) | **sai** | o controlador do item 2 a substitui nos dois lados |
| modo jogador (`aplicarEntrada`, `controlarJogador`) | **sai** | "não é para pressionar botão nenhum" |
| equipes de 3 e a troca | **saem** | E6: sempre 1 contra 1 |
| regras das 8 arenas (`CENAS[...].tick/guia/mov/projVel/erro`, obstáculos) | **desligadas** | E7: o mapa vira só o cenário. Os obstáculos também saem, porque bloquear projétil e corpo é regra |
| empurrão do golpe (6 px) | **fica** como movimento | SEM FONTE: sem ele, o corpo a corpo vira uma troca parada. PROPOSTO, 6 px (`ACAO.empurrao`) |
| geometria (`nucleo.ts`: elipse, cerca, corpos) | **fica** | é o chão da luta |

## 2. O pet como controlador

- **Quando decide.** O lutador livre decide no primeiro passo múltiplo de **R = 16 passos (256 ms)**. PROPOSTO, com fonte: a reação da CPU
  "normal" do protótipo (`DIFIC.normal.reacao` = 260 ms). A ação escolhida vai até o fim: não há troca no meio, e por isso há **uma
  decisão por ação**, como hoje há uma por turno.
- **Como decide.** Igual ao `decidirV2`:
  - com o lutador preparando o pesado, a primeira regra de fintar que valer troca a execução; senão, ele executa;
  - senão, com probabilidade ε, uma ação legal sorteada (exploração);
  - senão, **a primeira regra válida decide**: as condições valem e a ação é legal agora;
  - senão, a final (o furioso cai para carregar).
  - O motivo (o índice da regra, "exploracao" ou "pesado_automatico") vai junto com a ação, para o aprendizado e o "por quê".
- **O ε** é o de hoje (`estiloDoPet`): a base 0,05, o piso 0,2 da sombria, a disciplina dos v4+ (como o `Motor.disciplina` a lê hoje), a
  experiência de combate e a confiança M1. Ele é sorteado **uma vez por decisão**, na RNG de política do lado (item 4).
- **As condições do catálogo**, reescritas para o tempo real. Os domínios dos parâmetros não mudam, então as listas, o repertório, as
  travas e os vetos de hoje continuam válidos:

| condição (hoje) | em tempo real |
|---|---|
| `sempre` | igual |
| `distancia_eh(d)` | a faixa da distância agora (1.2) |
| `hp_proprio_abaixo(f)`, `oponente_hp_abaixo(f)` | a fração da vida agora |
| `guts_proprio_abaixo(g)`, `guts_proprio_acima(g)`, `oponente_guts_abaixo(g)` | o Guts agora (o mesmo número, a mesma unidade) |
| `oponente_preparando` | o rival está na fase de preparo do pesado (menos o preparo sob pele, V21D) |
| `oponente_repete(a, k)`, `oponente_frequente(a)` | as últimas k (ou 5) **ações começadas** pelo rival |
| `turno_execucao(t)`, t ∈ {5, 10, 20} | o relógio da luta ≥ t × T: **10, 20 ou 40 s**. A regra da Floresta ("muda no turno 10") vira 20 s |
| `oponente_vai_preparar` (vigia) | a intenção do rival agora (`intencaoV2` com as condições daqui) |
| `executando_pesado` | o lutador está na execução do pesado |

- **A lista, a capacidade e as condições por estágio ficam iguais:** 3, 5 e 8 regras (`CV21.maxRegras`), até 2 condições por regra, as
  condições liberadas por estágio (`CONDICOES_ESTAGIO`), a semeadura pela forma, o repertório e as candidatas.
- **Travar e Vetar (E4)** ficam entre as lutas, na tela Crescer (`intervirGambit`, o evento `"g"`), como hoje. Durante a luta não há
  controle nenhum.
- **O rival** (bot clássico, forma adulta, NPC, líder, Mega da Liga, alugado e rival da Fábrica, rival do Salão e das instalações) usa
  **o mesmo controlador**, com a lista e o ε dele (`lutadorBot`, `gambitNPC`, `gambitsAdulto`).
- **O oráculo** (o bot "oraculo", que é a melhor resposta de um passo sobre `resolverV2`) não tem tradução: um passo em tempo real não é
  um turno. **Proposta: sai da lista de rivais** (D-6).

## 3. O aprendizado e o que o resultado alimenta

**O que `GambitsPet.aprender` recebe.** Hoje ele lê, por turno, o motivo do pet (`tr.ma`, o índice da regra) e o saldo de dano do turno,
`(dano[1] − dano[0]) / hpMax`. Em tempo real, o "turno" vira **a ação**:
- o resultado da luta traz a lista de ações do pet, cada uma com o motivo e o saldo de dano dela;
- o dano que um golpe do pet causa conta para a ação que soltou o golpe, mesmo que o projétil chegue depois;
- o dano que o pet recebe conta para a ação em curso quando o golpe cai;
- a média por regra, o bônus do resultado (`GA.bonusResultado × (pontos − 0,5)`), o passo `GA.alfa × novidade`, a troca da pior regra
  abaixo de `GA.limiarTroca` e a RNG `hashSemente("propor", semente)` **ficam iguais**.

A assinatura de `aprender` muda só no tipo do resultado: um `ResultadoLutaTR` com `acoes: { motivo, saldo }[]`, `pontosA`, `fim` e `E0`.

**O que o resultado alimenta** continua igual. A R2 confere cada item com teste:

| o quê | onde, hoje | muda? |
|---|---|---|
| aprendizado das regras | `gp.aprender(res, s, M.usadas, novidade)` | só o tipo do `res` |
| sparring | `this.sparring++` no adolescente | não |
| lutas, vitórias, derrotas, empates | `this.lutas` (v4+) | não |
| vitórias da vida (experiência de combate) | `vitoriasVida += novidade` | não |
| lesão e morte por lesões | `hashSemente("lesao", s)` na derrota; `CLE.lesoesMorte` | não |
| confiança M1 e novidade do rival | `conf.registrar(...)`, `rivalDaConfianca` | não |
| campanha (vitórias por desafio; a Cidadela só com a série) | `this.campanha[rival]++` | não |
| Liga (tentativas, títulos) | `this.liga` | não |
| Salão (tentativas, vitórias) | `this.salao` | não |
| instalações (tentativas, última, recorde) | `this.instalacoes[id]` | não |
| `vida5.lutas` (v7+) | push com tick, rival, lesão, resultado | não |
| a história | `_hist(...)`, "venceu/perdeu/empatou" | o texto não fala mais de turnos |
| evolução: adulto pede sparring ≥ 10 e taxa ≥ 0,8; Mega pede ≥ 10 lutas, ≥ 0,8 e vínculo ≥ 0,4; medalhas do Tamer | `motor.ts` ~1139–1175 | não |
| medalhas, revanche, campeão, recordes, cartas da revanche | `src/tamer.ts` | não (lêem `venceu` e os contadores) |
| registro do Tamer da Fábrica | `fabrica.ts`, `tamer.ts` (`fabrica_luta`) | só a luta por baixo |

## 4. O log, o replay e o custo

**O evento.** Fica **o mesmo `"l"`, `[tick, "l", {r, s}]`**, com o `"k"` da carta antes. A versão do pet (E3) decide se a luta é por
turnos ou em tempo real, e nenhum evento novo é preciso. O resultado não é guardado: o replay refaz a luta.

**A semente e as RNG.**
- A luta em tempo real **não sorteia nada além do ε** (1.7). O dano, o acerto e o tempo são todos determinados pelo estado.
- Há dois fluxos de **política**, um por lado: `criarRng` com os 32 bits baixos de `derivarSemente("combate_tr", s, "politica", lado)`.
  O ε do pet nunca muda o que o rival sorteia, e vice-versa.
- Fica reservado um fluxo de **ambiente/combate**, `derivarSemente("combate_tr", s, "combate")`, hoje sem nenhum sorteio. Se a rodada de
  equilíbrio trouxer a variação de dano ou as regras de arena (E7), elas sorteiam ali, e trocar de política não muda o mundo.
- As outras RNG de hoje (`"lesao"`, `"propor"`, as das séries e instalações) ficam como estão.

**O determinismo entre navegadores (risco novo).** O combate por turnos só faz + − × ÷, e por isso dá o mesmo resultado em todo motor de
JavaScript. A simulação de hoje usa `Math.hypot`, `Math.sin` e `Math.pow`, que o padrão não obriga a sair iguais entre motores. No V8 (o
Node e o Chrome) a medida abaixo deu as mesmas 240 lutas, mas Firefox e Safari não foram medidos. **Regra proposta para a R1:** o núcleo da
luta só usa + − × ÷, `Math.sqrt` (o IEEE exige o arredondamento correto), `Math.floor`, `Math.min` e `Math.max`. Um teste confere pela
fonte, como o `arena_sem_dom`. A senoide do andar de lado e o `fatorRitmo` saem: o `fatorRitmo` já sai pela E5, e a senoide, por esta
regra.

**A medida do custo.** O script é `web/app/scripts/medir_replay_tr.ts`, com a bancada em `web/app/scripts/replay_tr_bancada.ts`, e a
saída é `web/app/scripts/medicoes/replay_tr.json`. Ele roda a mesma bancada no Node 24 e no Chrome instalado (o `@playwright/test` do
e2e, headless), sem dependência nova, e falha alto se os dois derem lutas diferentes. Deram as mesmas.

O que ele mede é a simulação de hoje, a do #446, no campo, CPU contra CPU, com os fluxos do jogo. A luta da R1 ainda não existe.
- **1 contra 1:** 200 lutas de um parceiro Rookie ou Champion de cada lado.
- **3 contra 3:** 40 lutas, as da medição da UP-ARENA, de cerca de 100 s e 6 000 passos: o caso "luta de ~100 s" da tarefa.
- **O controlador:** o `decidirV2` com a lista do Duelista (V21E), chamado 200 000 vezes, como substituto do da R1.
- **A linha de base:** o `jogarV2` de hoje, com as 8 formas adultas umas contra as outras, em 2 000 lutas.

Máquina: Intel i7-14700KF, Windows 11. Cada número é a mediana de 5 repetições, depois do aquecimento.

| medida | Node v24.19.0 | Chrome 156.0.8078.49 |
|---|---|---|
| 1 × 1, duração no jogo (média; p90) | 29,6 s; 35,3 s (1 853 passos) | igual |
| 1 × 1, custo por luta | 1,19 ms | 0,88 ms |
| 3 × 3, duração no jogo (média; p90) | 96,6 s; 109,2 s (6 038 passos) | igual |
| 3 × 3, custo por luta; por passo | 4,02 ms; 0,67 µs | 2,72 ms; 0,45 µs |
| controlador, por decisão | 0,63 µs | 0,35 µs |
| combate por turnos de hoje, por luta (24,3 turnos) | 0,086 ms | 0,068 ms |
| **luta de 100 s** (6 250 passos e o controlador a cada 16 passos, nos dois lados) | **4,66 ms** | **3,08 ms** |
| refazer 100 / 200 / 500 / 1 000 lutas de 100 s | 0,47 / 0,93 / 2,33 / 4,66 s | 0,31 / 0,62 / 1,54 / 3,08 s |
| refazer 1 000 lutas que chegam ao limite de 300 s da arena de hoje | 14,0 s | 9,3 s |
| refazer 1 000 lutas por turnos (hoje) | 0,09 s | 0,07 s |

**Leitura.**
- Em tempo real, a luta de 100 s custa cerca de 50 vezes a luta por turnos: 4,7 ms contra 0,09 ms no Node.
- Com o limite proposto de 80 s (1.1), a luta mais longa custa no máximo cerca de 3,7 ms no Node e 2,5 ms no Chrome. Uma luta típica (por
  volta de 24 T, ou 48 s) custa perto da metade disso.
- Uma vida com até ~500 lutas abre em menos de 2,5 s no Node e de 1,6 s no Chrome, nesta máquina.
- **O que não foi medido:** um celular, que deve ser várias vezes mais lento (SEM FONTE); a luta da R1, que tem mais regras por passo
  (Guts, posturas, técnicas) e menos IA do UP; quantas lutas uma vida de verdade tem. A Torre de Batalha chega a 100 lutas por tentativa
  (`LUTAS_MAX_INSTALACAO`), e o Salão refaz **todos os pets guardados** (`fronteira.copiaSincronizada`), então o custo de lá é a soma das
  vidas.

**Recomendação (D-2): refazer sempre, sem cache.** O custo cabe com folga até algumas centenas de lutas por vida, e o cache traria um
segundo lugar de verdade (o resultado guardado), o que vai contra o event sourcing. A R1 regrava a medida com a luta de verdade, e a R2 põe
um teste de custo: uma vida sintética de 1 000 lutas tem de abrir abaixo de um teto no Node (PROPOSTO: 10 s, SEM FONTE). Se a R1 sair mais
cara, há uma ordem de recuos:
1. o cache do resultado por índice de evento, só na memória da aba, nunca no save;
2. depois, um limite menor (60 s).

"Passo maior só no replay" **não serve**: muda o resultado.

## 5. Onde a simulação mora

- **Hoje:** `web/app/arena/` fica fora do `motor/`, importa a RNG do motor, e o motor nunca importa a arena (a regra da UP-ARENA, seção
  10.4).
- **Proposta (D-3):** a R1 cria um núcleo novo, sem DOM, **dentro do motor**: `web/app/motor/combate_tr/` (`luta.ts`, `controlador.ts`,
  `condicoes.ts`, `constantes_tr.ts`).
  - Ele copia de `arena/nucleo.ts` só a geometria (a elipse, a cerca, os corpos).
  - Não lê os JSON do UP, porque o resultado não depende deles (D-1). Então o replay de um pet nunca precisa da pasta `Assets/`, que fica
    fora do git.
  - O `motor_sem_dom` e a regra de aritmética do item 4 cobrem o núcleo novo.
- **Por que não importar `arena/`:**
  - o motor passaria a depender de uma pasta cujo resultado depende dos dados do UP (o status, o atlas, os golpes);
  - a regra "o motor nunca importa da arena" cairia;
  - a luta do pet herdaria a IA da CPU e as equipes, que saem (1.7).
- **O que sai da UP-ARENA** (na R3, quando nenhuma tela usar):
  - a tela separada `src/telas/lutar/arena_tr/`, a rota `#/lutar/tempo-real` e a chave `ARENA_TEMPO_REAL`;
  - os 3 × 3, a troca e o modo jogador de `arena/sim.ts`.
- **O que fica da UP-ARENA:**
  - `arena/medicao.ts` e `scripts/medir_arena.ts`, se o Matheus quiser guardar a medição do protótipo como referência; senão saem
    também (D-3);
  - na tela, o carregamento dos dados do UP (`src/arenaTempoReal.ts`: o atlas, os golpes, os efeitos, os cenários), que passa a servir
    só ao desenho.
- **A tela** recebe do motor a linha do tempo da luta: os eventos por passo, com tipo (o mesmo desenho dos eventos da arena de hoje).
  Ela desenha os clipes por cima. Para animar a luta do registro, ela refaz a luta pelo motor, como faz hoje com `montarLuta`.

## 6. O descarte (E2)

- **A versão nova:** a próxima livre quando a R2 entrar na `main`; hoje, a **v13** (E3). A v13 é a v12 (o cérebro A, o corpo e o mundo)
  com a luta em tempo real.
  - O `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` registra, na R2, que o cérebro modular passa para a seguinte.
- **O aviso na tela (R2):** ao abrir um save ou um pet guardado de versão < 13, o app não o abre como pet novo. Ele mostra um aviso fixo:
  "Este pet é de uma versão antiga do jogo, com o combate por turnos, e não abre mais." Há dois botões:
  - **Baixar o arquivo do pet**, que é o export de hoje (`src/importar.ts`), antes de descartar;
  - **Começar um pet novo**.
  - O Tamer (as medalhas, os itens, os recordes) fica, e o registro da Fábrica dele também. A Fábrica é refeita em tempo real (D-4).
- **O que sai do motor e dos testes, e quando:**

| o quê | etapa | por quê nessa etapa |
|---|---|---|
| os pets v1–v12 no `Motor` (os ramos `versao < 13` que só existem para as versões antigas: a educação, a mentira, o bandit v1, a obediência, os vínculos A/B, as escalas CESC/CESC_V6) | **R2**, no mesmo PR da v13 | o aviso já impede abrir; manter o código seria manter o replay de saves que não abrem |
| `motor/combate.ts` por turnos (`resolverV2`, `legalV2`, `jogarV2`, `oraculoV2`, `RegrasV21`, as variantes V21C e V21D) | **R3** | `PalcoLuta`, `TelaCenarios` (o Lab) e `luta.ts` ainda desenham por turnos até a R3 |
| os gabaritos `test/gabaritos/` de combate (v21d, v21e, os das campanhas e arenas por turnos) e os testes de paridade de combate com o Python | **R3** | são só do combate por turnos |
| os gabaritos de vidas v1–v12 que só testam versões antigas | **R2** | os saves dessas versões não abrem mais |
| **ficam:** a paridade do cérebro A (`lobos_python.json`), do corpo e do mundo com o Python; elas passam a rodar sobre a v13 (com a luta fora do caminho, ou numa vida sem luta) | — | a paridade do cérebro é requisito do DigiBrain modular |
| **ficam, congelados:** `digilab/combate_v2/` e todo o Python (E1), e os exportadores `experiments/exportar_*.py` | — | pesquisa da v1 |

A lista exata de arquivos sai no relato de cada etapa (E2).

## 7. As telas (R3) e os modos (R4)

**A tela da luta é uma só (R3):** um `PalcoTR` novo no lugar do `PalcoLuta`.
- Ele desenha os dois lutadores com os clipes do UP (`Run`, `Attack_1`, `Skill_1`, `Stun`, `Die`, do UP-ATLAS) sobre o cenário do lugar
  (E7).
- Tem a barra de vida e a de Guts dos dois, o relógio e o aviso da morte súbita.
- **Não tem controle nenhum durante a luta.** Tem "Pular para o fim", que hoje já existe e não muda o resultado, a pausa e o rápido.
- Depois da luta, mostra o resultado e **o "por quê"**: as regras que dispararam, quantas vezes e com qual saldo, como no `ModalResultado`
  de hoje.

| lugar (seção 3 da tarefa) | tela | cenário do UP (E7), PROPOSTO, SEM FONTE | etapa |
|---|---|---|---|
| Arena: bots clássicos e formas adultas | `TelaArena` → `PalcoTR` | campo | R3 |
| Melhor de 10 | `TelaArena`, sem animação (10 lutas no registro) | — | R3 |
| Campanha e Exploração (mapa, desafiantes) | `TelaCampanha`, `MapaExploracao` → `PalcoTR` | Campina: campo; Torre de pedra: castelo; Floresta: floresta; Cidadela: castelo; Lago: praia; Montanha Espiral: caverna | R3 |
| líderes das medalhas (as regras de cada arena v6) | `TelaCampanha` → `PalcoTR` | o do lugar; a regra de cada arena **fica**, porque é do DigiLab, não do UP: Paciência (a lista do líder), Leitura (troca aos 20 s), Resistência (3 lutas sem cura), Vínculo (sem as travas e os vetos), Chefe | R3 |
| Liga dos Líderes (6 Megas em série) | `TelaFronteira` → `PalcoTR` em série | coliseu | R4 |
| Torre de Batalha (sequência até perder) | `TelaFronteira` | castelo | R4 |
| Palácio (a lista que o pet faria sozinho) | `TelaFronteira` | castelo | R4 |
| Salão (o rival do estágio, pets guardados) | `FabricaSalao` | coliseu | R4 |
| Fábrica (Megas alugados, séries de 3, troca pelo derrotado, só no log do Tamer) | `FabricaSalao` | deserto | R4 |
| sparring dos pets de exemplo (`pets.ts`, `donos.ts`) | sem tela (só o motor) | — | R2 |
| Cenário pet (luta contra um pet de cenário, fora do log) | `TelaArena` → `PalcoTR` | campo | R3 |
| Lab (`TelaCenarios`, N lutas fora do log) | `TelaCenarios`, sem animação | — | R3 |

**O que a Fábrica precisa (R4):**
- o alugado e o rival lutam pelo mesmo núcleo, com as listas V21E;
- o registro do Tamer (`fabrica`, `fabrica_luta`, `fabrica_troca`) continua o mesmo, e só a luta por baixo muda;
- o registro do Tamer ganha uma versão nova (a 7) para as tentativas em tempo real. As tentativas gravadas com a Fábrica por turnos (`v`
  ausente ou 9) não se refazem mais, e o app avisa, como no item 6 (D-4).

**O que o Salão precisa (R4):** ele refaz os pets guardados para escolher quem luta. Com o descarte, só os v13 entram. O custo é a soma
das vidas (item 4).

**O Lab e o Melhor de 10:** N lutas sem animação custam N × ~3–5 ms. O Lab de hoje roda até centenas de lutas; acima de ~200, a tela roda
em blocos, para não travar o quadro (R3).

## 8. As decisões do Matheus

**DECIDIDAS (Matheus, 2026-10-29, no chat da coordenação):** as nove recomendações abaixo foram aceitas como estão. Os números da
D-5 (T, o limite e a morte súbita) passam a DECIDIDOS como o ponto de partida da R1; os outros números da espec seguem PROPOSTOS até a rodada de equilíbrio.


| | decisão | recomendação (DECIDIDA) | custo de errar |
|---|---|---|---|
| **D-1** | O tempo das ações vem do DigiLab (T = 2 s para todos, e o clipe do UP esticado para caber), ou do UP (cada Digimon com a duração e o instante do golpe dele)? | **DigiLab.** Do UP fica só a fração do instante dentro do clipe (E5: "o instante do golpe"), aplicada à duração do DigiLab | Com o tempo do UP, a forma vira um atributo escondido: duas formas com os mesmos stats lutam diferente por causa do sprite. Além disso, o replay passa a depender dos JSON do UP, que estão fora do git: sem a pasta `Assets/`, o pet não abre. Com o tempo do DigiLab, o golpe fica um pouco mais lento ou mais rápido que o clipe original |
| **D-2** | O replay refaz sempre, ou guarda o resultado? | **Refaz sempre** (item 4), com o teste de custo na R2 e a ordem de recuos | Sem cache, uma vida enorme demora para abrir (1 000 lutas: ~3–5 s no desktop, mais no celular). Com cache, aparece um segundo lugar de verdade, e um cache velho mostraria um pet errado sem erro |
| **D-3** | O núcleo vai para `motor/combate_tr/`, novo, ou o motor importa `arena/`? E a `arena/` (a medição do protótipo, os 3 × 3, o modo jogador) fica? | **Núcleo novo no motor;** a `arena/` sai na R3. A medição do protótipo fica só se você quiser guardá-la como referência | Importar a `arena/` amarra o pet aos dados do UP e à IA da CPU, e quebra a regra "o motor nunca importa a arena". Apagar a medição perde a reprodução das tabelas do `arena_equilibrio.md`, mas os números continuam no JSON gravado |
| **D-4** | A Fábrica e o Tamer: as tentativas antigas da Fábrica (por turnos, no registro do Tamer) se descartam junto com os pets? | **Sim:** o Tamer guarda as medalhas, os itens e os recordes, as tentativas antigas da Fábrica saem com aviso, e o registro do Tamer vai à versão 7 | Manter exige o combate por turnos vivo só para refazer a Fábrica antiga, e o `combate.ts` não sai. Descartar zera o recorde da Fábrica (o número pode ficar como texto na história) |
| **D-5** | O T (2 s), o limite (80 s) e a morte súbita (50 s) | **Os propostos**, até a rodada de equilíbrio | Com T maior, a luta fica arrastada e cara; com T menor, rápida demais para se ler o "por quê". O limite define o custo máximo do replay (item 4) |
| **D-6** | O bot "oraculo" | **Sai** da lista de rivais clássicos | Ele é uma referência da pesquisa da v1 (a melhor resposta de 1 passo) e não tem tradução em tempo real. Se ficar, é preciso inventar um oráculo novo, sem fonte |
| **D-7** | A regra de aritmética do núcleo (só + − × ÷ e `sqrt`) | **Sim**, com um teste pela fonte | Sem ela, um pet criado no Chrome pode ter outra vida no Safari ou no Firefox (o mesmo log, outro resultado), e isso só aparece quando alguém abrir lá |
| **D-8** | A fuga condicionada vira o recuo a 80% (1.2)? | **Sim** | Com o recuo a 100%, quem foge nunca é alcançado e a luta acaba no limite. Com um recuo bem mais lento, a distância deixa de ser uma escolha |
| **D-9** | Saem na R2 os ramos do motor das versões v1–v12 (a educação, a mentira, o bandit v1, a obediência, os vínculos), ou só o combate por turnos na R3? | **Saem na R2** os que só servem às versões que não abrem; a paridade do cérebro A, do corpo e do mundo fica | Tirar na R2 deixa o PR grande (e a revisão mais longa). Deixar mantém código que nenhum save abre, e os testes dele custam tempo de suíte |
