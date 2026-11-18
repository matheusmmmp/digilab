# MAPA VALUATION (V0): do `sens.falta` ao `arb.escolher` (2026-11-16, Claude Code, Opus 5.5)

**Status: PROPOSTO.** Este é o documento da Fase V0 da frente VALUATION ([TAREFA_V3_VALUATION.md](TAREFA_V3_VALUATION.md)). É só um
mapa: não roda vida, não muda código e não decide nada. Ele para no **CHECKPOINT V1**, e a V1 (o plano de análise) só começa com o
"aprovado" do Matheus.

**A base:**
- O código é o da `origin/main` em `100421b2` (2026-11-16). O pedido foi escrito no snapshot `f8fa9ad2`. Toda linha citada abaixo foi
  conferida no código de hoje. Desde o snapshot, mudaram 7 arquivos do cérebro e do motor, com +158 e −27 linhas. As mudanças são as
  chaves `comer_bebe` e `guarda_fome_brincar` da EQ-7, as duas desligadas por padrão. Nenhum número citado no pedido mudou.
- A A1 ainda não está na `main`. O resultado, os artefatos e o plano estão no branch `v3-evidencia-a1` (`73c2abbb`, PR #943, aberto). Os
  números da A1 abaixo saem de lá:
  - o `resultado.json` (`706a687a…`);
  - o `medidas.json` da validação (`cdaa5170…`, conferido igual ao `meta.json`).
- Os números marcados **descritivo** foram somados do `medidas.json` da A1 nesta sessão. O cálculo está na seção 7. Não têm gate nem IC e
  não substituem a métrica da A1.

## 1. O que a A1 mede de fato (a premissa do pedido, conferida)

O pedido diz que o modular "sente (38 % de privação) e não age (come 10× menos que uma regra trivial)". Os artefatos da A1 dizem outra
coisa em dois pontos, e isso muda o que a V1 deve medir.

**1.1 O "come 10× menos" conta decisões, não refeições.** O 614 820 contra 59 925 é o `descritivo.acoes` do `resultado.json`, o número de
decisões em que a ação foi `comer`, no `longe_fixo`. Os dois braços têm as mesmas 1 075 200 decisões (800 vidas × 1 344). A diferença
vem de como cada braço chega à comida:
- **A TRIV** chama `comer` com a fome abaixo de 0,4, e o motor usa o alvo padrão (`mundo.alvo_padrao_de`). Sem comida à vista, o alvo é o
  cheiro. Por isso a caminhada até a comida conta como `comer`.
- **O REL** chega à comida também pelo `explorar`: a unidade `explorar/cheiro` e o lugar lembrado, `explorar/ponto`.

O consumo de verdade sai do `cadeia.refeicoes_por_dia` (as refeições de ração por dia, `metrics.py:2150`):

| lugar | REL | TRIV |
|---|---|---|
| `longe_fixo` | **2,96** | **1,49** |
| comedouro | 4,04 | 2,11 |
| longe | 2,45 | 2,38 |

(descritivo, média das 800 vidas de cada braço e lugar)

**O REL come mais ração por dia que a TRIV.** O que ele faz pior é fechar o episódio dentro da janela.

**1.2 A privação não é a fome.** A privação da A1 é a fração das decisões com min(fome, higiene, energia) < 0,15. Ela mistura os três
drives. Os 38 % são do REL. A TRIV tem 98,6 %, e a diferença vem sobretudo da energia: a TRIV fica exausta em todas as decisões da segunda
semana.

**1.3 O que falha é a janela.** O primário da A1 é a taxa de fechamento por episódio de fome (`metrics.episodios_de_fome`,
`metrics.py:2313`). O episódio abre com a fome < 0,5 e a ração do dono no chão. Ele fecha se o pet come essa ração dentro de W(d0)
decisões, de 8 a 17. Nos episódios do `longe_fixo` (descritivo, somado sobre os episódios):

| | REL | TRIV |
|---|---|---|
| fins "fechou" | 0,601 | 0,903 |
| fins "janela_vencida" | 0,393 | 0,094 |
| episódios por vida | 12,9 | 18,0 |

Uma ressalva sobre essa tabela: ela é a fração somada sobre os episódios. A média por vida, que é a da A1, sai 0,562 e 0,645. A diferença
mostra que os episódios não se espalham por igual entre as vidas.

**Nas decisões do REL dentro de um episódio** (96 315 decisões; descritivo, do bloco `cheiro`):
- 44,3 % são `dormir`;
- 8,2 % são `comer/cheiro`;
- 4,8 % são `explorar/cheiro`.

**O reflexo do sono decide 20,4 % de todas as decisões do REL** (273,7 de 1 344 por vida, o campo `reflexos`). A TRIV só dorme com a energia
abaixo de 0,1, e a regra 1 dela, comer, vem antes da regra 2, dormir.

**A pergunta que a V0 passa à V1 é, então:** por que o modular não fecha o episódio de fome dentro da janela, se come mais ração por dia?
A métrica da A1 continua a mesma (a regra do pedido: não mudar a métrica). O consumo e as decisões de dormir no episódio entram como
descritivos.

## 2. O fluxo de uma decisão, do `sens.falta` ao `arb.escolher`

As vidas da A1 são do Python. O braço REL é `SUBCHAVES_C4["REL"]` (`experiments/run_v2_digibrain_prototipo.py:129`): o M3 com as subchaves
`cheiro_inato`, `intencao_cheiro` e `memoria_autobio`, e o `controle_mem = "rel"`.
- **Ligados** (os padrões do `ConfigDigibrain`, `digilab/config.py:2798`): o P1, o P2, o M-MEM e a persistência.
- **Desligados:** o `modula_g_apr`, a `intencao_suspensa`, a `redecidir_evento`, as `facetas_mem`, o `passeio`, a `fala_unidades`, o
  `olhar`, o sono que segura e as duas chaves da EQ-7.

O jogo web espelha cada passo em `web/app/motor/digibrain/`; a linha TS vai ao lado.

A ordem é a do `ModularAdapt.agir` (`digilab/digibrain/adapt.py:291-355`). O motor chama o `agir` a cada 15 ticks, a cadência igual
para todo cérebro (`digilab/engine.py:87-96`; no TS, `motor_corpo_mundo.ts:404-418`). A ação dura o intervalo inteiro.

### 2.1 M-SENS, `Sens.codificar` (`sens.py:327-365`; TS `sens.ts`)

- `falta[r] = S − leitura` nos drives (`falta_receptor`, `digilab/policies/lobos.py:2825`), S = 1024.
- As linhas dos objetos à vista, `prox = clamp(S − d·S/R, 0, S)`, com R = 96 subunidades, ou 6 células (`sens.py:285`;
  `config.py:1802`).
- As conjunções:
  - `comida_vista` = a maior `prox` entre as comidas boas;
  - `sem_comida = S − comida_vista`.
- `ha_cheiro` = há direção de cheiro, com o raio do cheiro de 384 subunidades (`config.py:1806`).

**No `longe_fixo`, a ração do dono fica longe do pet** (`mundo.py:2857`). Fora do raio de 96, o comer não tem unidade da comida: só o
`comer/cheiro`, se houver cheiro.

### 2.2 M-AFETO, `Afeto.ler` (`afeto.py:104-131`; TS `afeto.ts:84-108`)

- **A urgência** (`afeto.py:95-97`; TS `afeto.ts:69`):
  - `u = clamp(mul(S/2, falta) + mul(3S/2, max(0, falta − S/2)), 0, S)`;
  - a mesma curva nos onze receptores (`config.py:2921-2923`; TS `constantes.ts:54-56`).
- **O ganho da exploração** (`afeto.py:121`; TS `afeto.ts:105`):
  - `g_exp = clamp(e0 + mul(β_T, falta do tédio) − mul(β_U, max_r u_r), 0, e_max)`;
  - os valores: e0 = S/2, β_T = β_U = S/2, e_max = S;
  - com uma urgência no teto e o tédio 0, `g_exp` = 0.
- **A valência V e a excitação E** saem da consequência (`afeto.py:136-151`) e entram no z.
- **O `g_apr`** = g0 = S no REL (o `modula_g_apr` desligado). O `g_apr_media` da A1 é 1 024 em todas as vidas.

### 2.3 O reflexo do sono, `Arbitragem.reflexo` (`arb.py:102-115`; TS `arb.ts:102-111`)

- O `adapt.py:314` chama o reflexo antes do M-ESTADO.
- Com a energia abaixo de `lambda_sono` = S/4 (`config.py:2954`; TS `constantes.ts:32`), o pet **dorme sem sorteio** (`arb.py:142-145`).
- Fica fora da disputa das unidades: nenhum termo da ativação pesa.
- Sem a `intencao_suspensa`, a intenção de comer em curso acaba como "trocou" (`estado.py:247-275`), e o F sobe.

### 2.4 M-ESTADO, `EstadoDinamico.contexto` (`estado.py:144-155`)

- **O F decai** a cada decisão.
- **A persistência** `h = mul(w_pers, C)` vai só à intenção em curso, com `w_pers` = 4S (`config.py:2964`).
- **O compromisso:** como `tau_c` = 15 = Δ, `k_C` = S e o C vai a S na primeira escolha (`estado.py:109`, 277). A persistência sai 4S, o
  teto `a_max` da ativação (`config.py:2909`).
- **As intenções** são `comer/comida`, `brincar/bola`, `explorar/ponto` e, com a `intencao_cheiro`, a busca `comer/cheiro`.

### 2.5 M-MEM, `Memoria.recuperar` (`mem.py:393-421`; TS `mem.ts:359-365`)

- **A pista:** a urgência da fome acima de `lambda_busca` = S/4 (`config.py:2981`) e nenhuma comida boa à vista.
- **A escolha do lugar:** com a pista, o lugar de maior `nota = mul(valor, S − min(S, d·S/d_max))`. Com a `memoria_autobio`, o valor é a
  soma dos sigma (MA-2).
- **O termo:** `M = mul(w_mem, valor)`, com `w_mem` = S (`config.py:2983`).

### 2.6 M-IMPULSO, `Impulso.unidades` (`impulso.py:156-247`; TS `impulso.ts:158-230`)

**O contexto z** (`impulso.py:104-114`; TS `impulso.ts:115`):
- o viés S e as onze urgências;
- noite, dormindo e o tempo sem cuidado;
- `comida_vista`, `sem_comida` e `bola_vista`;
- `fome_sem_comida = mul(u_fome, sem_comida)` e `cuidado_humor`;
- F, V e E.

**As unidades** (`impulso.py:117-154`; TS `impulso.ts:125-150`), nesta ordem:
- ocioso e dormir;
- **comer:** uma unidade por comida à vista, mais o `comer/cheiro` se há cheiro;
- brincar: a bola ou sem alvo;
- chamar_atencao;
- **explorar:** o `vagar`, o `cheiro` se há cheiro e o `ponto` se o M-MEM recuperou um lugar;
- emburrar.

**A ativação de cada unidade** (`impulso.py:208-246`) é `a = phi(soma dos termos, a_max)`, com `phi` = clamp em [0, 4S]
(`_comum.py:24-26`). Os termos são:

| termo | conta | linha | no REL |
|---|---|---|---|
| inato | `Σ_j W0[b,j]·z_j + W0_tipo[b, tipo]` | `impulso.py:173`, 212-213 | ligado |
| prox | `mul(W0_prox[b], prox_o)` (comer S/2, brincar S/4) | 224 | só com objeto |
| nov | `mul(W0_nov[b], nov_o)` (só brincar) | 225 | só com objeto |
| incentivo | `mul(G_classe, prox_o)`, com G do P1 | 226-230 | só comer e brincar com objeto |
| hábito | `Σ_j mul(H[b,j], z_j)`, do P2 | 231; `plast.py:84-92` | ligado (η_h = S/256, \|H\| ≤ S/2) |
| memória | M, só no `explorar/ponto` | 232-233 | ligado |
| persistência | h, só a intenção em curso | 234 | ligado |
| lembrança | L, nas unidades que casam com o episódio lembrado | 235-236 | ligado (`memoria_autobio`) |
| faceta, gosto, enjoo, `bola_do_dono`, `bebe` | — | 176-185, 237-244 | desligados (termo 0 ou ausente) |

**A linha do comer** (`config.py:2940`; TS `constantes.ts:57`): `W0[comer] = (viés −17S/16 = −1 088, u_fome 3S = 3 072)`, com
`W0_tipo[comer]` de S/4 = 256 na ração e nas frutas e −2S na podre (`config.py:2951`). O `comer/cheiro` soma o `w0_tipo_cheiro` = S/4
(`config.py:2968`, a DX-3).

**Nenhuma linha de W0 tem peso em V nem em E** (`config.py:2936-2946`; TS `constantes.ts:57`). V e E só chegam a uma unidade pelo hábito H,
que o P2 aprende.

**Os limiares inteiros**, calculados com as funções do código (seção 7), só com os termos da fome:

| unidade | a soma passa de 0 a partir de |
|---|---|
| `comer/cheiro`, sem comida à vista | fome < 0,489 (falta 523) |
| `chamar_atencao`, só o `fome_sem_comida` | fome < 0,499 (falta 513) |
| `comer/cheiro` passa do `chamar_atencao` | fome < 0,468 (falta 545) |
| `comer/comida` na borda da visão (d = 95) | fome < 0,490 |
| `comer/comida` a meio raio (d = 48) | fome < 0,624 |
| `comer/comida` encostado (d = 0) | fome < 0,792 |

O episódio da A1 abre com a fome < 0,5. Entre 0,499 e 0,468, o chamar vale mais que o comer pelo cheiro. A TRIV come a partir de 0,4.

### 2.7 M-ARB, `Arbitragem.escolher` (`arb.py:122-175`; TS `arb.ts:119-170`)

1. **O reflexo**, se houver (2.3).
2. **Os pesos** `w = a + mul(g_exp, ε)` só nas unidades com a > 0 (`arb.py:84-86`; TS `arb.ts:81-83`).
   - O ε é S/8 = 128 (`config.py:2953`; TS `constantes.ts:16`).
   - O acréscimo vai de 0 a 128, igual em toda unidade positiva.
3. **O sorteio proporcional**, com uma `rng.random()` (a única rng do cérebro) quando há dois candidatos ou mais (`arb.py:146-153`,
   `sortear_inteiro` em 42-53). O caminho do maior peso já existe, sem rng (`arb.py:98-99`; TS `arb.ts:96`), e as sondas o usam.
4. **As sondas "quem decidiu"** (`arb.py:154-168`) refazem a escolha com o termo de um módulo zerado e o mesmo u. São só de leitura. A A1 as
   grava em `influencia`.

Depois, o `estado.escolhida` (`adapt.py:355`) abre ou renova a intenção. O motor aplica a ação por 15 ticks.

## 3. As hipóteses

Cada linha diz:
- onde a hipótese mora;
- o que os artefatos que já existem dizem dela;
- a predição falsificável para a ablação da V1, escrita antes;
- o controle que já existe para a ablação, porque a regra do pedido é nenhum mecanismo novo.

Os sinais da predição são do REL ablado menos o REL completo, na taxa por episódio no `longe_fixo`. O "≥ δ" usa a margem da A1,
δ = 0,032 (SEM FONTE), até a V1 fixar a regra de leitura.

| H | onde (Python; TS) | o que já se sabe | predição falsificável | o controle que já existe |
|---|---|---|---|---|
| **A**, a frequência de decisão | `engine.py:87-96`; `motor_corpo_mundo.ts:404-418` (`proximaDecisao = tick + intervalo`, 418) | A TRIV decide na **mesma** cadência de 15 ticks e fecha 0,645 por vida. A cadência sozinha não separa os dois braços. | Se A causa a perda, decidir assim que a ração cai sobe a taxa do REL em ≥ δ e baixa a fração de "janela_vencida". Se a taxa não muda (\|Δ\| < δ), A cai. | A `ConfigDecisaoNaComida` (`config.py:3217`, desligada; TS `motor_corpo_mundo.ts:313`), que antecipa a decisão quando a comida cai. Trocar o `intervalo_decisao_ticks` muda a física de todo pet, e por isso não serve de ablação. |
| **B**, o `g_exp` alto suprime o comer | `afeto.py:121`, `arb.py:84-86`; `afeto.ts:105`, `arb.ts:81-83` | O acréscimo é de no máximo 128 (S/8) e cai a 0 com uma urgência no teto. A sonda `sem_afeto` (o g_exp = e0) mudou a escolha em **1,5 %** das decisões (descritivo, `influencia.afeto`). | Se B causa a perda, ε = 0 sobe a taxa em ≥ δ e a fração de `comer` nas decisões do episódio. A prioridade é baixa: as sondas apontam para \|Δ\| < δ. | O `ConfigDigibrainInatos.epsilon` = 0. É um número, não um mecanismo. |
| **C**, a memória de lugar atrapalha | `mem.py:393-421`, `impulso.py:145-148` e 232-233 (a unidade `explorar/ponto`); `mem.ts:359-365`, `impulso.ts:141-144`, 227 | **Contra C:** na C4, a memória ajuda, REL − SEM = +0,065 [0,052; 0,078] (`artifacts_v2_digibrain_prototipo/memoria_autobio/run/resultado.json`, na `main`). **A favor de C:** na A1, todas as visitas ao lugar lembrado saem vazias (57,6 de 57,6 por vida, descritivo, `visitas_vazias`), e a sonda `sem_memoria` mudou a escolha em 19,4 % das decisões. | Se C causa a perda, o `controle_mem = "sem"` sobe a taxa em ≥ δ. A C4 prevê o contrário (Δ ≈ −0,065). Se a ablação baixar a taxa, C cai, e as visitas vazias ficam como custo de bem-estar, não como a causa. | `controle_mem = "sem"`, o braço SEM da C4 (`config.py:2794`; `mem.py:363`). |
| **E**, o limiar de fome alto | `config.py:2940` (`W0[comer]`: viés −1 088, `u_fome` 3 072); `constantes.ts:57` | O `comer/cheiro` só passa de 0 com a fome < 0,489. Entre 0,499 e 0,468, o chamar vale mais (2.6). O episódio abre a 0,5, e a TRIV come a 0,4. | Se E causa a perda, um viés menos negativo sobe a taxa em ≥ δ, e a decisão do primeiro `comer` no episódio vem antes. Se a taxa não muda, E cai. O valor da ablação fica para a V1. A rodada 3 trocou o viés de −S para −17S/16, e o −S é o candidato natural. | O `ConfigDigibrainInatos.w0`, uma linha da tabela. É um número, não um mecanismo. |
| **F**, o V e o E deprimem o comer | `afeto.py:146-149` (V e E), `impulso.py:111` (no z); `afeto.ts`, `impulso.ts:115` | Nenhuma linha de W0 lê V nem E (`config.py:2936-2946`). Eles só pesam pelo H, que o P2 aprende devagar (η_h = S/256). O `g_apr` fica constante no REL. A sonda `sem_habito` mudou a escolha em 11,1 % das decisões, e essa conta mistura todas as colunas de H. | Se F causa a perda, tirar o V e o E do z sobe a taxa em ≥ δ. Pela forma do código, a predição é \|Δ\| < δ. | **Não existe controle só para o V e o E no z.** O mais perto é o `p2 = False`, que tira o H inteiro e confunde F com o hábito. A ablação limpa pede uma chave nova de ablação (D-VAL-3). |
| **G**, o número de alvos dilui o comer | `arb.py:146-153` e 42-53 (o sorteio proporcional); `arb.ts:93-97` | O episódio sem comida à vista tem de 7 a 10 unidades, várias com a > 0. As unidades positivas somam o mesmo acréscimo do `g_exp`. A A1 não grava a fração de decisões em que o comer tinha o maior peso e perdeu o sorteio. | Se G causa a perda, escolher o maior peso, em vez de sortear, sobe a taxa em ≥ δ. A assinatura: nas decisões do episódio, o comer tinha o maior peso e não saiu em uma fração alta delas. | O caminho do maior peso já existe (`arb.py:98-99`), mas só vale sem u. Ligá-lo no sorteio pede uma chave de ablação (D-VAL-3). A `guarda_fome_brincar` da EQ-7 (`arb.py:117-120`, desligada) é um caso parcial: tira o brincar com a fome urgente. |

**Fora da lista do pedido: R, o reflexo do sono.** É PROPOSTA, e o Matheus decide se entra (D-VAL-2).
- **Onde:** `arb.py:102-115` e 142-145; `config.py:2954`; TS `arb.ts:102-111` e `constantes.ts:32`.
- **O que já se sabe:**
  - o reflexo decide 20,4 % das decisões do REL;
  - 44,3 % das decisões do REL no episódio são `dormir`;
  - sem a `intencao_suspensa`, o reflexo troca a intenção de comer e sobe o F;
  - a TRIV come antes de dormir e só dorme abaixo de 0,1.
- **A predição:** se R causa a perda, um `lambda_sono` menor sobe a taxa em ≥ δ **e** sobe a exaustão. É a troca que o pedido proíbe ("sem
  perder a vantagem de bem-estar"). Uma ablação que só segura a intenção, a `intencao_suspensa` (subchave que já existe, a L-2), não mexe na
  exaustão. Se ela sobe a taxa, a causa é a intenção perdida, não o sono.
- **O controle:** `lambda_sono` (um número) e a `intencao_suspensa` (subchave que já existe).

**A D (P1 e P2) fica com a A2**, como o pedido diz.

**A persistência não vira hipótese.** A sonda `sem_persistencia` mudou a escolha em 0,4 % das decisões, apesar do h no teto (2.4).

## 4. A prioridade

A ordem vem de quanto os artefatos de hoje sustentam cada hipótese e de quanto custa a ablação. A V1 continua com um braço por hipótese,
como o pedido diz. A ordem só serve para ler os resultados e decidir o que entra se a máquina não der para todos.

1. **R** (se entrar) **e E.** Os dois mexem no tempo do comer dentro da janela, o que falha (1.3), e os dois saem de um número ou de uma
   subchave que já existe. R tem o sinal mais forte nos descritivos.
2. **G.** É plausível pela forma do sorteio, mas não há medida dele hoje e a ablação pede uma chave.
3. **A**, pela `ConfigDecisaoNaComida`. A cadência é a mesma da TRIV. Se A ajudar, é pela decisão no tick da comida, não pela cadência.
4. **C.** A C4 já mediu o sinal contrário no mesmo primário, mas as visitas vazias pedem a ablação.
5. **B e F.** As sondas e a forma do código apontam para nulo.

## 5. O que muda na V1 por causa deste mapa (para o CHECKPOINT V1)

As decisões D-VAL-1 a D-VAL-6, com a recomendação e o custo de errar, estão na [TAREFA](TAREFA_V3_VALUATION.md), seção 8. Em resumo:
1. **A pergunta:** "por que não fecha na janela", com o consumo e o dormir no episódio como descritivos. A métrica da A1 fica.
2. **A hipótese R:** entra ou não.
3. **F e G:** pedem uma chave de ablação nova, desligada.
4. **A ablação de A:** pela `ConfigDecisaoNaComida`, não pelo intervalo.
5. **Onde a run roda:** no Python, que é onde está a A1. O script TS do pedido, `web/app/scripts/valuation_ablacao.ts`, ficaria só se o
   Matheus quiser a ablação também no jogo.
6. **A ordem com a A1 e com a LIMPEZA:**
   - a V1 cita a A1 por um branch que ainda não está na `main` (PR #943);
   - o `afeto.py`, o `sens.py` e o `_comum.py` importam `div_arred`, `falta_receptor`, `sinal_corpo` e `contribuicoes_corpo` do
     `digilab/policies/lobos.py`, o A que a LIMPEZA tira. A run da V2 precisa da `main` em que esses imports já mudaram de lugar, ou de
     antes da LZ2. Qualquer um serve, desde que o `meta.json` grave o commit.

## 6. O que este mapa não demonstra

- Que alguma das hipóteses é a causa. As predições são para a ablação da V2, que ainda não tem plano.
- Nenhum número dos descritivos tem IC nem gate. São somas sobre as vidas da A1, para orientar a V1.
- Nada sobre o jogo web. As vidas são do Python, e os pets do jogo (v38, v39) têm chaves que o REL da A1 não liga.
- Que a baseline trivial é a melhor regra possível (a ressalva da A1).

## 7. Como refazer os números descritivos

Os artefatos da A1 estão no branch `v3-evidencia-a1`. Na raiz da worktree:

```bash
git show origin/v3-evidencia-a1:artifacts_v3_baseline_trivial/validacao/medidas.json > medidas_a1.json
```

```python
import json, statistics as st, collections as C
r = json.load(open("medidas_a1.json"))                     # sha256 cdaa5170bccd8c12...
for b in ("REL", "TRIV"):
    x = [e for e in r if e["lugar"] == "longe_fixo" and e["braco"] == b]
    mot = C.Counter(ep[4] for e in x for ep in e["episodios_fome"]["episodios"])
    print(b, st.mean(e["cadeia"]["refeicoes_por_dia"] for e in x), {k: v / sum(mot.values()) for k, v in mot.items()})
    if b == "REL":
        n = sum(e["cheiro"]["decisoes_nos_episodios"] for e in x)
        print(sum(e["cheiro"]["decisoes_dormir"] for e in x) / n, st.mean(e["reflexos"] for e in x) / 1344,
              {k: st.mean(e["influencia"][k] for e in x) for k in x[0]["influencia"]},
              st.mean(e["visitas_lugar_lembrado"] for e in x), st.mean(e["visitas_vazias"] for e in x))
```

**Os limiares da seção 2.6** saem da `urgencia` do M-AFETO e do `mul` (`digilab/digibrain/_comum.py`), com os valores do
`CONFIG_DIGIBRAIN_INATOS`. Para cada falta f de 0 a S, conta-se a soma de cada unidade só com os termos da fome. O limiar é o primeiro f em
que a soma passa de 0.
