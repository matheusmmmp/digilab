# Plano do equilíbrio da luta em tempo real (LUTA_POC, LP5)

Worker: Claude Code, Opus 5.5, worktree `D:\Trab\digilab\v3-luta-poc-lp5`, branch `v3-luta-poc-lp5`, 2026-11-10, a pedido do Gerente de
sprites e luta (a sessão `local_a6f79153`). A tarefa é a `docs/TAREFA_V3_LUTA_POC.md`, a linha da LP5 na seção 5.1.

**Status: APROVADO.** As decisões D-LP5-1 a D-LP5-10 (seção 8) estão DECIDIDAS como recomendadas: o Matheus, em 2026-11-10, "Tá, então
faz toda a recomendação aí que você deu" (repassado pelo Gerente, que autorizou a reserva das faixas). Os números novos deste plano (as
faixas das metas, os tamanhos das amostras) seguem PROPOSTOS, SEM FONTE: a régua foi aprovada, não a fonte deles. As faixas de sementes
estão na `FAIXAS_RESERVADAS` desde o commit próprio da LP5-0 (seção 5).

**A autorização:** o Matheus, em 2026-11-10: "Pode já fazer a LP5" (repassado pelo Gerente). Ela libera este plano, no papel. A calibração
começa só depois da aprovação.

**O que vale e o que não vale:**
- **não valem** as 27 metas das rodadas R2 e R3 do combate por turnos, nem as D-R3-1 a D-R3-9 (a LP-9 e a LP-10). O
  `docs/PLANO_EQUILIBRIO_COMBATE_TR_R3.md` serviu só de forma: as metas com critério e medida, as fases, a regra de parada, a conferência
  única, as decisões numeradas;
- **valem** a LP-3 (a IA é a mesma para os dois lados; o pet traz os 6 stats; "evoluir isso, não o nível de luta"), a LP-4 (o mapa de cada
  lugar), a LP-5 (os torneios), a LP-8 (o golpe de longe), as LP2-1 a LP2-6, a D-7 (a aritmética do replay) e a regra "equilíbrio só no
  fim, numa rodada só".

## 1. O ponto de partida: o que se sabe sem medir

**A luta de um ovo novo hoje** é a da v21 (`web/app/motor/luta_poc.ts`, `web/app/motor/arena/`), ligada para todos desde a LP4 (#757):

- **Os números do pet** saem dos 6 stats pelo `MAPA_STATS` (a LP2-2): o pet neutro (10 em cada stat) recebe os `STATS_PADRAO` da POC
  (vida 900, ataque 100, defesa 50, movimento 70, ciclo 2 000 ms, recarga 8 s, crítico 10 %, erro de mira 18 px), e cada número escala na
  razão do stat: o vigor na vida, a força no ataque, a guarda na defesa, o fôlego no movimento, a recuperação (inversa) no ciclo e na
  recarga, a mira no crítico e (inversa) no erro. A vida leva também o `multEstagio` (0,6 no Rookie, 0,8 no Champion, 1 no Ultimate, 1,15 no
  Mega) e a condição do cuidado (0,95 a 1,05).
- **Os stats do pet** são os do `statsDe` (a espécie, o caráter e a forma, renormalizados à soma da espécie, 60) mais `3 ×` os pontos de
  treino e de chip (`CTR.pesoPontoCombate`).
- **O treino** tem teto em pontos (10 por stat, 10/12/14/16 por estágio do Rookie ao Mega, 36 na vida e 40 no Mega; `CTR` e `CMG`), mas
  quase nenhum no tempo: 10 ticks entre sessões e a fadiga (D-LP2b-6). O treino típico de cada estágio é o `CIT.tipico`: 8, 22, 36 e 40
  pontos. Só no Rookie o típico fica abaixo do teto (8 de 10); do Champion em diante, o típico é o próprio teto acumulado (22, 36 e 40).
  O teto que falta é o da luta: o que cada ponto vale nela (o item abaixo).
- **Os NPCs** saem do `statsNpc`: o total do NPC (`bots.ts`) dividido igualmente pelos 6 stats, no estágio do lugar dele.
- **Os rivais da Arena e dos torneios** são formas do jogo com o perfil canônico, sem treino, condição 1.
- **A IA** é a "normal" da POC para os dois lados (a LP-3).

**O que se lê do código, sem luta medida** (são contas sobre as constantes, não resultado; a LP5-0 mede):
- **Por que o Gazimon trava.** Ele tem total 96, ou 16 em cada stat, contra a soma 60 de um Rookie sem treino. Com o treino típico (8
  pontos, `3 × 8 = 24`), o Rookie chega a 84. No combate por turnos, o total 96 vinha com o `eps` de 0,5 do NPC ("forte mas desastrado"):
  metade das escolhas eram ao acaso. Na luta da POC a IA é a mesma para os dois lados, e o `eps` não existe mais. O Gazimon ficou forte e
  deixou de ser desastrado. Os outros 9 NPCs da v21 também tinham `eps` de 0,4 ou 0,5 (`bots.ts`).
- **Por que o treino quase não tem teto na luta.** Os números escalam em linha com o stat, e vários se multiplicam na luta: a vida, o
  ataque e o ciclo (o dano por segundo é o ataque sobre o ciclo, contra a vida do outro). Um pet com todos os stats `k` vezes maiores tem
  `k` vezes a vida e cerca de `k²` vezes o dano por segundo; a força relativa sobe mais rápido que o stat (HIPÓTESE, SEM FONTE; a LP5-0
  mede a curva).
- **Por que a espécie pesa demais.** O mapeamento dá o mesmo peso a cada stat, mas a mira (no crítico e no erro) move menos a vitória do
  que a vida e o ataque. O cirro (na espécie: vigor 7, força 7, mira 15) e o ferrugem (vigor 13, guarda 15) ficam longe: na D-LP4-6, o mesmo treino de
  8 pontos dá ao Rookie cirro 0 % contra o Gazimon e ao ferrugem 32 % (HIPÓTESE sobre a causa, SEM FONTE; a LP5-0 mede o peso de cada stat).

**O que já foi medido** (cada número com o artefato):

| o quê | o valor | o artefato |
|---|---|---|
| um Rookie sem treino contra o Gazimon, no Campo | 0 % em 5 pets (cirro, ferrugem, brasa) | `web/app/scripts/medicoes/lp4_gazimon.json` |
| o mesmo Rookie com 8 pontos (2 em vigor e força, 1 nos outros) | 0 % (cirro, 3 pets), 19,5 % (brasa), 32 % (ferrugem) | idem |
| a vida do Gazimon e a do Rookie | 864 contra 397 a 737 sem treino e 737 a 1 077 com 8 pontos | idem |
| o dono simulado que luta contra o próprio estágio | fica no Champion: não chega a 0,8 de vitória para o Ultimate | D-LP4-6 (`docs/registro/2026-11.md`), em `test/evolucao_canonica.test.ts`; sem JSON próprio |
| o relógio médio de 5 formas na LP3b | de 11,0 s (Gabumon Rookie) a 22,3 s (um Champion) | `web/app/scripts/medicoes/lp3b_lp8.json` |
| os empates do Gabumon Rookie | 6,25 % das 448 lutas | idem |
| o relógio médio das 480 lutas do gabarito da POC | 19,1 s, com os stats genéricos da POC | `web/app/scripts/medicoes/arena_custo_lp1.json` |
| o custo de uma luta no Node | ~0,6 a 0,7 ms | idem |
| a faixa "de 8 a 30 s" de duração | a do Gerente, sem um artefato que a dê inteira | a LP5-0 mede |

## 2. As metas

**As palavras das metas** (as definições exatas são a D-LP5-2):
- **o pet bem cuidado:** condição 1 (a saúde do meio da faixa), sem lesão, sem chip;
- **o treino típico:** os pontos do `CIT.tipico` do estágio (8, 22, 36 e 40), distribuídos como um dono que treina todos os exercícios
  (seção 3.2);
- **o pet sem treino:** o mesmo pet, com 0 ponto;
- **o pet no teto:** os pontos máximos que o treino permite até aquele estágio (10, 22, 36 e 40);
- **o rival canônico:** uma forma do jogo com o perfil canônico, sem treino, condição 1 (como a Arena de hoje);
- **a taxa:** a fração das lutas que o lado vence; o empate conta como não vitória, como no jogo. A Cidadela conta a série de 3 sem cura.

**Os critérios são sobre a estimativa pontual** (como nas rodadas de antes). O intervalo de Wilson a 95 % vai ao lado de cada número no
relatório, para leitura, e não decide.

| # | a meta | o critério de passar (PROPOSTO, SEM FONTE) | a medida que a produz |
|---|---|---|---|
| **P1** | a primeira medalha não trava: o Gazimon | **desde a D-LP5-17:** o Rookie sem treino ≤ 0,41; com o treino típico ≥ 0,59 na média; a pior espécie só na leitura. (Antes: ≤ 0,20, ≥ 0,70 e a pior espécie ≥ 0,50) | a bancada `lideres`: os Rookies das 4 espécies e das formas do jogo contra o Gazimon, no Campo |
| **P2** | cada líder é vencível com o treino típico | os 6 líderes, cada um no estágio do lugar dele. **Desde a D-LP5-17:** sem treino ≤ 0,41, 0,35, 0,30 e 0,27, do Rookie ao Mega; com o típico ≥ 0,59, 0,65, 0,70 e 0,73; a pior espécie só na leitura. Na Cidadela, a série de 3 | a bancada `lideres`, nos mapas fixos da LP-4 |
| **P3** | os desafiantes: mais fáceis que o líder do lugar | os 4 desafiantes (o Tortomon, o Devidramon, o Puppetmon e o Machinedramon). **Desde a D-LP5-17:** o limite do líder do estágio, +0,15 no sem treino e +0,05 no típico (no Champion ≤ 0,50 e ≥ 0,70; no Mega ≤ 0,42 e ≥ 0,78). Antes: ≤ 0,35 e ≥ 0,75 | a bancada `lideres`, contra os desafiantes |
| **P4** | a evolução não trava pela taxa de vitória | o pet com o treino típico, contra os rivais da Arena do estágio dele (o sparring): ≥ 80 % dos pets chegam a 0,8 (o `CLE.limiarTaxa`) no Champion e no Ultimate | a bancada `sparring`: cada pet contra as formas do estágio, no Campo, e a fração dos pets acima de 0,8 |
| **P5** | o dono simulado chega ao fim | a vida do dono simulado de `test/evolucao_canonica.test.ts` (o atencioso, que treina e luta contra o próprio estágio) chega ao Mega em ≥ 80 % das vidas | a bancada `vida`: as vidas inteiras pelo motor, com o registro, até o Mega ou o fim da vida |
| **T1** | o treino pesa | o pet com o treino típico vence o mesmo pet sem treino de 0,80 a 0,97, em cada estágio | a bancada `treino`: o pet contra ele mesmo sem treino, nos 8 mapas |
| **T2** | nenhum stat morto, nenhum dominante | 8 pontos num stat só, contra o mesmo pet sem treino: cada stat ganha ≥ 0,60; do stat que mais ganha ao que menos ganha, ≤ 0,25 | a bancada `treino`, um stat por vez, no Rookie e no Ultimate |
| **T3** | o teto do treino | o pet no teto, contra os rivais canônicos do próprio estágio, ≤ 0,95 (o treino não zera a luta); a curva da taxa pelos pontos, contra os mesmos rivais, sobe sem degrau maior que 0,25 a cada 4 pontos; no Rookie, o pet no teto (10) contra o mesmo pet com o típico (8) ≤ 0,70 | a bancada `treino`, na grade de 0 ao teto, de 2 em 2 pontos |
| **E1** | a evolução pesa mais que o treino | o pet com o típico de um estágio contra o rival canônico do estágio seguinte: de 0,10 a 0,35. Dois estágios acima: ≤ 0,05. O pet no teto contra o rival do estágio seguinte: ≤ 0,50 | a bancada `estagio`: os pets de cada estágio contra as formas do seguinte e do outro |
| **D1** | a duração | a mediana do relógio em cada estágio de 15 a 40 s (a D-LP5-8); o p90 ≤ 60 s; nenhuma forma com mediana < 8 s | todas as bancadas, o relógio de cada luta |
| **D2** | sem fim e empate | as lutas que chegam ao `LIMITE_MS` ≤ 0,5 %; os empates ≤ 2 % em cada forma | todas as bancadas |
| **D3** | a Cidadela cabe | a série de 3 no p90 ≤ 3 min de relógio | a bancada `lideres`, a Cidadela |
| **A1** | de longe × de perto | as formas que atiram (com projétil na tabela, a LP-8 incluída) contra as que lutam de perto, do mesmo estágio, perfil canônico: de 0,45 a 0,55 na soma dos 8 mapas, em cada estágio; em cada mapa, de 0,30 a 0,70 | a bancada `formas`: todos os pares do estágio, nos 8 mapas |
| **A2** | a distância do tiro (a D-LP5-12; PROPOSTA, SEM FONTE) | quem atira contra quem luta de perto, do mesmo estágio, perfil canônico, nos dois lados e nos 8 mapas: a mediana da distância no instante do tiro ≥ 90 px, e no máximo 15 % dos tiros a 48 px ou menos, em cada estágio. Contra quem atira, a mediana vai ao lado, só para leitura | a bancada `tiro` |
| **V1** | a variedade dentro do estágio | cada forma contra as outras do estágio, perfil canônico, sem treino: de 0,35 a 0,65; da mais forte à mais fraca ≤ 0,30; toda forma vence ≥ 2 das outras | a bancada `formas` |
| **V2** | a espécie não decide sozinha | as 4 espécies com o treino típico, contra os mesmos rivais canônicos do estágio: da melhor à pior ≤ 0,15, em cada estágio | a bancada `sparring`, por espécie |
| **G1** | a Liga | o Mega bem cuidado com o típico (40 pontos) ganha o título (6 vitórias sem cura) em ≥ 0,25 das tentativas; nenhuma forma Mega acima de 0,85 | a bancada `torneios` |
| **G2** | a Torre de Batalha | o recorde mediano do Mega típico de 3 a 30 vitórias seguidas; o teto de 100 em ≤ 5 % das tentativas | a bancada `torneios` |
| **G3** | a Fábrica | uma série de 3 vencida em ≥ 0,25 das séries, com os alugados sorteados | a bancada `torneios`, pelo `motor/fabrica.ts` |
| **G4** | o Salão | o pet com o típico vence o rival do Salão de 0,70 a 0,95 em cada estágio | a bancada `torneios` |
| **S1** | a sanidade: o espelho | o mesmo lutador dos dois lados: o lado A vence de 0,45 a 0,55 em cada mapa, **só nas lutas com vencedor** (a D-LP5-11; os empates ficam no D2). **Fora da Praia** (a D-LP5-13): a Praia vai ao lado, só para leitura | a bancada `formas`, as formas contra elas mesmas |

**As metas protegidas.** A lista das que passam na LP5-0 fica protegida pela regra "volta atrás" (seção 4). O S1 é protegido desde o
começo: se ele falha na LP5-0, a rodada para e o achado vai ao Gerente antes de qualquer ajuste (é o núcleo, não o equilíbrio). **Desde a D-LP5-13** (2026-11-10): o V2 e o P4 saem da lista (passavam na LP5-0 só pelo teto) e viram metas da LP5-1 e da LP5-2; o T2 e o V1 ficam aceitos como reprovados nesta rodada (a D-LP5-5); o S1 vale nos 7 mapas fora da Praia. **Desde a D-LP5-15** (2026-11-11): o V2 fica aceito como reprovado (vai à tarefa da tabela das formas); o A1 por mapa e o D2 vão à investigação do núcleo com a Praia; a LP5-2 parte do `lp5_1_r2`, com o S1 vigiado no Ringue do Rookie.

**O que as metas não pedem.** Nenhuma meta mede o pet com o cérebro modular (a ponte com o DigiBrain lê o resultado da luta, mas a luta
não lê o cérebro), os itens além do chip de stat, nem o tempo de tela dos efeitos.

## 3. As alavancas

### 3.1 O que a rodada pode mexer (só no candidato da bancada, seção 4.3)

| alavanca | onde está hoje | o que pode mudar | as metas que move |
|---|---|---|---|
| **as bases do mapeamento** | `MAPA_STATS` (`motor/luta_poc.ts`) | os números do lutador neutro (a vida, o ataque, a defesa, o movimento, o ciclo, a recarga, o crítico, o erro) | D1, D2, A1, T1 |
| **o peso de cada stat** | o mesmo `MAPA_STATS`, hoje 1 para todos | um peso por stat na razão (`(s / 10)^γ_stat`, com `γ` de 1 hoje) e, no expoente abaixo de 1, o rendimento decrescente que dá o teto (a D-LP5-4) | T2, T3, V2, E1 |
| **o peso do ponto de treino na luta** | `CTR.pesoPontoCombate` (3), lido pelo `statsDoPet` | um número próprio da luta, ao lado; o `CTR` do treino não muda | T1, T3, P1–P5 |
| **o multiplicador do estágio na luta** | o `multEstagio` do `perfilDe`, na vida | um número próprio da luta por estágio, na vida e, se preciso, no ataque; o `CAT.estagio` não muda | E1, P2, P4 |
| **os NPCs** | o total de cada um (`bots.ts`) e a divisão igual pelo `statsNpc` | o total de cada um dos 10 e, só se o total não fechar, a divisão pelos stats (a D-LP5-9) | P1, P2, P3, D3 |
| **os rivais por lugar** | a Arena e o Salão com a forma canônica sem treino; os Megas da Liga, da Torre e da Fábrica sem treino | o treino dos rivais de cada lugar, em pontos (hoje 0) | P4, E1, G1–G4 |

### 3.2 O que fica fora, com o motivo

| o quê | por que fica fora |
|---|---|
| **o núcleo da POC** (`EQ`, `ACAO`, `DIFIC`, `OPCOES_PADRAO`, as regras dos 8 mapas em `cenas.ts`) | é a POC; a fidelidade da LP1 (480 de 480 lutas iguais ao harness) é a prova disso. A D-LP5-5 diz o que fazer se uma meta só fechar por ele |
| **a tabela das formas** (`formas.ts`: o golpe, o tempo, o projétil, o atributo) | são os dados do jogo (a LP-2), gerados pelo `tools/gerar_tabela_arena.py`. A lista da LP-8 também fica: ela foi decidida pelo que é de longe na série, não pelo equilíbrio |
| **o treino** (o `CTR`: os ganhos, as aptidões, a fadiga, o intervalo, os tetos em pontos) e o `CIT.tipico` | é o cuidado, espelhado do Python (`ConfigTreino`); o teto da luta se faz no mapeamento (a D-LP5-4) |
| **as regras da evolução** (o `CLE.limiarTaxa`, o `CAT.sparring`, as medalhas do `CMD`, o vínculo do Mega) | são da evolução, espelhadas do Python; a rodada ajusta a luta para que elas sejam alcançáveis |
| **os mapas de cada lugar** (a LP-4 e os D-LP2b-1) | decididos; a rodada mede cada lugar no mapa dele |
| **a IA igual para os dois lados** (a LP-3) | decidida; os NPCs ficam mais fáceis pelos números, não por uma IA pior |
| **os números visuais** (os efeitos E1–E5 e o palco) | não mudam nenhuma luta; ficam para a rodada visual, como na D-R3-9 de antes |
| **o Python** (`digilab/combate_v2`) | congelado (a LP-7) |
| **a ração do bebê, o vagar** | são do cuidado e do cérebro, para a rodada geral do jogo inteiro |

## 4. O método

### 4.1 As lutas e a bancada

- **CPU contra CPU**, com semente, pelo motor do jogo (`lutarNucleoPoc` e os `Motor` de verdade para os pets), sem tela.
- **A bancada é nova** (`web/app/scripts/equilibrio_poc/`, na LP5-0): o `scripts/equilibrio_tr/` do combate por turnos saiu na LP4. Uma
  bancada por grupo de metas (`lideres`, `sparring`, `vida`, `treino`, `estagio`, `formas`, `torneios`), um `medir_tudo` que as roda em até
  4 processos e um `resumo_metas` que lê os JSON e dá a tabela da seção 2.
- **Os pets** saem do `Motor` com a semente do pet, como na `medir_lp4_gazimon.ts`: avançados até o estágio, com os pontos de treino
  postos pelo dono da seção 3.2 (a D-LP5-2). As formas e as espécies saem da semente, e o relatório traz a conta por espécie e por forma.
- **Os artefatos** vão em `web/app/scripts/medicoes/equilibrio_poc/<fase>/`, em JSON, com o commit, a faixa, as sementes e o candidato.
  **Nenhum número sem o JSON que o produz.**
- **A prova de reprodução** (na LP5-0, antes das sementes novas): a bancada `lideres`, com as sementes da `medir_lp4_gazimon.ts` (os pets
  11, 21, 23, 101 e 202, as lutas 0 a 199) e o `TREINO_8` dela, refaz o `lp4_gazimon.json` campo a campo. São sementes de teste, já usadas,
  e não contam como calibração.

**O tamanho das amostras** (PROPOSTO, SEM FONTE; a LP5-0 confere o custo):
- **por base**, 20 pets por estágio e 20 lutas por par (pet, rival, mapa); com 5 bases, 100 pets por estágio, ~25 por espécie;
- **as formas** (A1, V1, S1): todos os pares do estágio, nos 8 mapas, 25 lutas por par e mapa em cada base;
- **as vidas** (P5): 20 vidas por base, 100 no total;
- **os torneios:** 20 tentativas por pet de cada torneio.

Com ~0,7 ms por luta (`arena_custo_lp1.json`; os pets treinados lutam mais tempo), uma medida inteira deve ficar perto de 1 milhão de
lutas, ~12 min num processo e ~4 min em 4, mais as vidas do P5 (SEM FONTE; a LP5-0 mede e registra).

### 4.2 As fases

A ordem vai de baixo para cima: o mapeamento muda tudo, os NPCs ficam por cima dele, e os torneios por cima dos dois.

| fase | o quê | as metas | as alavancas |
|---|---|---|---|
| **LP5-0, o ponto de partida** | a bancada nova, a prova de reprodução e a medida de todas as metas na calibração, sem mudar nada. Também a curva da taxa pelo treino (T3) e o peso de cada stat (T2), que dizem se as hipóteses da seção 1 valem | todas | nenhuma |
| **LP5-1, o mapeamento** | o pet contra o pet e as formas contra as formas: o peso do treino, o teto, a evolução, a duração, o alcance e a variedade | T1, T2, T3, E1, D1, D2, A1, V1, V2; o S1 vigia | as bases, o peso de cada stat (com o expoente), o peso do ponto e o multiplicador do estágio da luta |
| **LP5-2, os NPCs e a progressão** | os líderes e os desafiantes por cima do mapeamento novo, a começar pelo Gazimon; o sparring e a vida do dono | P1, P2, P3, P4, P5, D3 | o total dos 10 NPCs (e a divisão, pela D-LP5-9); o treino dos rivais da Arena (P4) |
| **LP5-3, os torneios** | a Liga, a Torre, a Fábrica e o Salão | G1, G2, G3, G4 | o treino dos rivais dos torneios |
| **LP5-4, a conferência única** | todas as metas, uma vez, nas sementes de conferência, com o candidato final | todas | nenhuma: nada se ajusta olhando para ela |
| **LP5-5, ligar no jogo** | o candidato como a versão nova do pet (a D-LP5-7), com o gabarito das vidas v21 gravado antes, num commit próprio | — | — |

**A regra de parada de cada fase:** a fase para quando as metas dela passam ou depois de **3 rodadas de ajuste**. A meta que não fecha é
relatada com o melhor valor e o porquê, e a fase seguinte parte do melhor candidato.

**A regra de escolha:** um número muda só quando uma meta dele não passa e algum valor da grade a faz passar. Entre os que passam, fica o
de maior folga na meta pior. Entre empates, fica o mais perto do de hoje.

**Em qualquer fase:**
- um ajuste que reprova uma meta protegida (a lista da LP5-0, ou uma que a rodada já fechou) **volta atrás**;
- um teste de replay ou de determinismo que quebre **para tudo** até o conserto (`CLAUDE.md`).

### 4.3 O candidato e os pets que já existem

- **Os ajustes ficam num candidato da rodada** (`MAPA_STATS_LP5` e os totais dos NPCs ao lado, só na bancada), sem versão de pet e sem
  mudar o jogo: o `MAPA_STATS`, o `statsNpc` e os rivais da v21 não mudam até a LP5-5.
- **As vidas v21 dos gabaritos** (`lp2_vidas_v21`, `lp2b_torneios_v21`) conferem iguais em cada PR da calibração.
- **Ligar no jogo** é a LP5-5, depois da conferência, pela D-LP5-7.

### 4.4 A conferência única (LP5-4)

- roda **uma vez**, no fim, nas sementes de conferência, com o candidato fechado num commit antes dela (o sha vai no JSON);
- nenhum número muda por causa dela: **a meta que reprova fica registrada como está**, com o valor da calibração ao lado, e o Matheus
  decide o que fazer;
- a calibração não usa as sementes de conferência, nem para conferir o custo.

### 4.5 A carga na máquina

- **no máximo 4 processos** e **uma medição por vez** (a V3-D8; as medições da luta contam como carga);
- **o gate:** o H10 (`.claude/hooks/h10_pre_run.py`) e o `tools/pre_run.py --medicao` reconhecem hoje só `scripts/equilibrio_tr/`, que
  saiu na LP4. A LP5-0 estende os dois ao `scripts/equilibrio_poc/`, no mesmo PR, para a regra de uma carga por vez valer na bancada nova;
- **antes de cada medida**, o PR da fase registra o comando, as metas, as sementes e o tempo estimado.

**O custo da rodada** (SEM FONTE): cada medida inteira ~5 a 15 min em 4 processos; uma grade de 10 a 20 pontos de 1 a 4 h; até 3 rodadas
nas fases 1 a 3, mais a LP5-0 e a LP5-4: **de 6 a 30 h de máquina**, em cargas separadas.

## 5. As sementes (DECIDIDAS, D-LP5-6; reservadas no commit próprio da LP5-0)

| uso | faixa | como |
|---|---|---|
| **a calibração** (LP5-0 a LP5-3) | **`86101…86505`**: as bases 86101, 86202, 86303, 86404 e 86505 | por base, a semente do pet `i` é `hashSemente("equilibrio-poc-pet", base, i)` e a da luta `k`, `hashSemente("equilibrio-poc", base, k)` |
| **a conferência** (LP5-4) | **`87101…87505`** | a mesma derivação; roda uma vez e não volta |

**Conferido em 2026-11-10, na `origin/main` (`4387121a`):**
- as duas faixas estão fora da `FAIXAS_RESERVADAS` e da `FAIXAS_QUEIMADAS` (`experiments/bancada/faixas.py`). A reservada mais perto é a
  `85101…85505` (a INDIVIDUALIDADE, I2);
- nenhum documento, script ou ferramenta da `main` cita `86101` ou `87101` como palavra;
- nenhum PR aberto mexe no `faixas.py`;
- **as faixas da rodada 3 ficam fora:** a `83101…83505` foi usada pela R3-0 (#720, fechado sem merge), e a `84101…84505` foi reservada no
  mesmo PR. Nenhuma das duas entrou na `main`, mas a primeira já tem lutas medidas.

**Como elas entram:** na `FAIXAS_RESERVADAS`, com a fonte "equilibrio da luta em tempo real (jogo web, LUTA_POC LP5): a calibracao
(docs/PLANO_EQUILIBRIO_LUTA_POC.md, secao 5; D-LP5-6)" e "…: a conferencia, uma vez (…)". Num commit próprio do PR da LP5-0, depois da
aprovação e do pedido ao coordenador. No mesmo commit, o mapa `FAIXAS` da bancada nova ganha `calibracao: 86101` e `conferencia: 87101`, e
a bancada falha alto com um nome fora dele.

**As sementes 101…505 seguem só nos testes.**

## 6. A entrega

| fase | o PR |
|---|---|
| **este** | só o plano, com a seção no registro |
| **LP5-0** | o commit das faixas, a bancada nova, o gate estendido, a prova de reprodução e o ponto de partida na calibração |
| **LP5-1 a LP5-3** | a calibração (a D-LP5-10): a tabela das metas de cada fase, os artefatos, as metas protegidas |
| **LP5-4** | a tabela de todas as metas, na calibração e na conferência, e o que não fechou |
| **LP5-5** | o candidato no jogo, pela D-LP5-7, com os gabaritos |

Os relatórios de cada fase vão numa seção "Resultado da LP5-n" no fim da `docs/TAREFA_V3_LUTA_POC.md`; os desvios, na seção "LUTA_POC, LP5"
do `docs/registro/AAAA-MM.md` do mês, com o índice regenerado. **O merge é só do Matheus.**

## 7. As questões abertas (nenhuma se resolve neste plano)

1. **As hipóteses da seção 1** (o treino que compõe, a mira que pesa pouco, o Gazimon sem o `eps`) vêm das contas, não de lutas. Se a
   LP5-0 as desmentir, as alavancas da LP5-1 continuam as mesmas, mas a ordem das grades muda.
2. **O D-LP4-6 do dono simulado** (o Champion que não chega a 0,8): pode ser a luta (os rivais do sparring sem treino ainda vencem o pet
   típico) ou o dono (quanto ele treina). O P4 separa a luta do dono; o P5 mede os dois juntos.
3. **Os empates do Gabumon Rookie** (6,25 % na LP3b): a LP5-0 diz de onde vêm (o duplo nocaute, o limite) antes do D2.
4. **O custo no celular** segue SEM FONTE, como na LP2. A rodada não o mede.
5. **A duração alvo** (a D-LP5-8) é gosto do jogo, não medida: a faixa proposta é um ponto de partida para o Matheus.

## 8. As decisões (todas DECIDIDAS como recomendadas, 2026-11-10)

| # | a pergunta | a recomendação | o custo de errar |
|---|---|---|---|
| **D-LP5-1** (as metas) | as 20 metas da seção 2 (21 com o A2, D-LP5-12), com as faixas propostas, são a régua da rodada? | **sim, como estão.** O P1 é a meta que motivou a rodada; o P5 e o P4 são o "não trava" do resto do caminho; o T1 a T3 e o E1 são a LP-3 ("evoluir os stats"); o A1 e o V1, a variedade | uma faixa errada faz a rodada calibrar para o lugar errado: larga demais, nada muda e o Gazimon continua difícil; estreita demais, as 3 rodadas acabam sem fechar. Trocar a régua depois de ver a calibração é o erro que a conferência única evita |
| **D-LP5-2** (o pet típico) | o "treino típico" é o `CIT.tipico` posto por um dono que treina todos os exercícios pelo `Treino.sessao`? | **sim.** O dono alterna os 6 exercícios até chegar aos pontos do `CIT.tipico`, e a aptidão da espécie entra como no jogo. A condição fica em 1 | um treino posto à mão (como o `TREINO_8` da LP4) não é o que um jogador faz e esconde a aptidão; um dono que só treina força e vigor faria o P1 passar com um pet que ninguém tem |
| **D-LP5-3** (as alavancas) | as alavancas são as da seção 3.1, e fica fora o da 3.2? | **sim.** A rodada mexe no mapeamento, nos NPCs e no treino dos rivais; o núcleo, a tabela das formas, o treino, a evolução e os mapas ficam | mexer no treino ou na evolução muda o cuidado e quebra o espelho com o Python; deixar os NPCs fora deixa o P1 só para o mapeamento, que muda todo o resto junto |
| **D-LP5-4** (o teto pelo expoente) | o mapeamento ganha o rendimento decrescente (`(s / 10)^γ`, com `γ` por stat e menor que 1 se a grade pedir), como a forma do teto? | **sim, só no candidato.** É a única alavanca que põe teto na luta sem mexer no treino | sem ele, o teto só se faz baixando o peso do ponto, que também tira o peso do treino (T1); com um `γ` baixo demais, o treino deixa de pesar no fim |
| **D-LP5-5** (o núcleo da POC) | e se uma meta (o A1, o D1) só fechar mexendo no núcleo da POC? | **a fase para pela regra das 3 rodadas, e a meta volta ao Matheus com os números**, sem mexer no núcleo. Ele decide entre aceitar a meta reprovada e abrir uma alavanca do núcleo (por exemplo, o `ACAO.alcanceDist` ou o `pvel`) | mexer no núcleo sem decisão quebra a promessa da LP-1 ("é a POC") e a fidelidade da LP1; proibir de vez pode deixar o A1 sem saída |
| **D-LP5-6** (as sementes) | reservar a `86101…86505` para a calibração e a `87101…87505` para a conferência? | **sim, num commit próprio da LP5-0, pedidas ao coordenador.** As da R3 (83xxx e 84xxx) ficam fora | uma faixa errada mistura resultados; usar a 83xxx partiria de sementes já medidas na R3-0 |
| **D-LP5-7** (a versão) | como o candidato entra no jogo, na LP5-5? | **como a v22**, ao lado da v21: o núcleo é o mesmo, e só a tabela do mapeamento, os NPCs e os rivais mudam por versão. Os pets v21 continuam abrindo e lutando com os números deles, sem descarte. A v20 é do ARVORE_SACODE (#694) | mudar a v21 no lugar muda o replay e a assinatura dos pets que nasceram desde a LP4, o contrário da regra "uma versão por mecânica"; descartar a v21 perde pets de jogadores sem necessidade, porque guardar duas tabelas custa pouco |
| **D-LP5-8** (a duração) | a mediana de 15 a 40 s por estágio, com o p90 até 60 s, é a duração que o jogo quer? | **sim, como ponto de partida.** Hoje vai de 11 a 22 s nas 5 formas da LP3b; a faixa deixa a luta do Rookie curta e a do Mega mais longa | uma luta curta demais esconde o tiro e a habilidade (o Matheus quis ver a rajada voar); longa demais cansa, e a Cidadela (3 lutas) e a Torre ficam lentas. É gosto: o Matheus pode trocar a faixa agora, antes da calibração |
| **D-LP5-9** (o perfil dos NPCs) | o NPC pode ter os stats divididos de outro jeito (o Tortomon com mais guarda, o Devidramon com mais força), além do total? | **só se o total não fechar o P1 a P3 em 2 rodadas.** O total é a alavanca primeira; a divisão é a segunda, e cada uma vem com a frase do NPC na tela | dividir desde o começo dobra a grade e mexe na identidade dos líderes; nunca dividir pode deixar um líder impossível para uma espécie (a V2) |
| **D-LP5-10** (os PRs) | um PR por fase, como na R3, ou um PR para a calibração inteira? | **três PRs:** a LP5-0 (as faixas, a bancada e o ponto de partida), a calibração (LP5-1 a LP5-3, com uma seção por fase) e a conferência; a LP5-5 num quarto. O worker para depois de cada um | um PR por fase dá 6 esperas de merge para uma rodada só; um PR só esconde a LP5-0, que é onde as hipóteses se confirmam ou não antes de gastar a máquina |
| **D-LP5-11** (a régua do S1; DECIDIDA em 2026-11-10, depois da LP5-0) | o S1 falhou na LP5-0 pelos empates do espelho (11 a 17 %), com o lado A de 0,48 a 0,51 sem eles (o desvio D-LP5-0-6). O S1 conta só as lutas com vencedor? | **sim:** o lado A das lutas com vencedor, de 0,45 a 0,55 em cada mapa; os empates seguem medidos pelo D2. O Matheus: "faça a recomendação." | contar o empate como derrota do lado A mede o empate, não o lado; o empate já tem a régua dele (o D2). Trocar a régua depois da LP5-0 é a exceção da regra "o S1 para a rodada": foi decidida antes da LP5-1, antes de qualquer ajuste |
| **D-LP5-12** (a distância do tiro; DECIDIDA em 2026-11-10, depois da rodada 1 da LP5-1) | uma revisão dos sprites mediu que quem atira de longe atira colado em quem luta de perto: a mediana da distância no tiro é 49 px, 46 % dos tiros saem a 48 px ou menos, e o voo dura de 1 a 3 passos. Contra outro atirador, a mediana é 134 px e o voo, 13 passos. A causa está no núcleo (`motor/arena/sim.ts`): o tiro sai sem distância mínima, o recuo só começa abaixo da metade do alcance, o recuo tem a velocidade do avanço (`EQ.recuo` 1), e o atirador fica parado na preparação enquanto o oponente investe 58 px. A distância do tiro entra na LP5 como mudança do núcleo (a exceção da D-LP5-5)? | **sim.** O núcleo ganha o `Tiro` (`motor/arena/constantes.ts`): a distância mínima de tiro e a espera máxima abaixo dela, a fração do alcance onde o recuo começa, a velocidade do recuo de quem atira e o recuo na preparação do tiro. Ele só vale quando a entrada da luta o traz, então a luta de hoje sai igual byte a byte. O candidato da bancada (e a v22, na LP5-5) leva os números dele. A meta nova é o A2. O Matheus: "Desenho agora, motor na LP5" (repassado pelo Gerente). O desenho (a origem do tiro, os Megas, o fim da luta) é da LP3c, em outra sessão | sem a distância, o tiro não voa e o A1 mede outra coisa (o atirador perde porque luta de perto sem golpe de perto); com uma distância mínima sem espera, quem atira encurralado na borda nunca atira, e a luta não acaba (a espera máxima evita isso) |
| **D-LP5-13** (as 4 decisões da rodada 1; DECIDIDAS em 2026-11-10) | o PR #772 levou 4 decisões: (1) o S1 que falha na Praia, também com o v21; (2) o V2 e o P4, protegidos, que só passavam pelo teto; (3) o T2 (o fôlego) e o V1 (a variedade), que o mapeamento não move; (4) quem atira, forte demais quando mantém distância | **as 4 como recomendadas.** (1) uma investigação curta do núcleo na Praia, fora da LP5, como pendência; a calibração segue com o S1 vigiado nos outros 7 mapas. (2) o V2 e o P4 saem das protegidas: o V2 é meta da LP5-1, o P4 da LP5-2. (3) o T2 e o V1 ficam aceitos como reprovados nesta rodada, pela D-LP5-5; o núcleo e a tabela das formas ficam para uma tarefa própria. (4) o `Tiro` ganha o dano do projétil (`danoProj`, no lugar do `EQ.danoDist`) e a velocidade dele (`velProj`, sobre o `OPCOES_PADRAO.pvel`), na grade das rodadas 2 e 3. O Matheus: "Aprovo as 4" (repassado pelo Gerente) | (1) ignorar a Praia deixa uma vantagem de lado num mapa da Campanha até a investigação; (2) sem a proteção, um candidato pode piorar a espécie e o sparring, mas os dois seguem medidos; (3) aceitar deixa o fôlego sem peso e formas fortes demais do Champion em diante; (4) a alavanca do projétil muda mais o núcleo, e a fidelidade da LP1 só vale sem o `tiro` |
| **D-LP5-14** (a esquiva pela perspicácia e pela velocidade; DECIDIDA em 2026-11-10, pelo Matheus nesta sessão) | a esquiva da POC é igual para todos (45 %, 260 ms de reação, um pulo de 380 px/s por 180 ms) e só contra o tiro; o fôlego e a mira não ganham luta (o T2). A perspicácia de luta (perceber o golpe e reagir antes) e a velocidade (o pulo) entram na esquiva? Qual stat é a perspicácia? | **sim, no núcleo, desligada** (a `Esquiva`, `motor/arena/constantes.ts`): a perspicácia sobe a chance e encurta a reação, a agilidade acelera o pulo, e há uma leitura nova do golpe de perto (pular para trás na preparação dele) e um contra-ataque depois dela. **A perspicácia é a mira junto com o caráter atento; a agilidade é o fôlego.** O Matheus: "Vamos daí fazer com o Mira e o Caráter Atento juntos". Os números são PROPOSTOS, SEM FONTE, e entram na grade | esquiva demais deixa a luta longa ou sem fim e o pet lento de perto sem chance (o D1, o D2 e o A1 vigiam); ligar a perspicácia só à mira deixaria o caráter sem papel na luta |
| **D-LP5-15** (as 4 decisões do fim da LP5-1; DECIDIDAS em 2026-11-11) | o resultado da LP5-1 (o `lp5_1_r2`, 6 de 21 metas) levou 4 decisões: (1) o V2 (a espécie), que o mapeamento não leva a 0,25–0,35; (2) o A1 por mapa (o Ringue e o Castelo pendem para quem luta de perto; o Deserto e a Caverna, para quem atira); (3) o D2 (os empates, 3,6 %); (4) de onde a LP5-2 parte | **as 4 como recomendadas.** (1) o V2 fica aceito como reprovado e vai para a tarefa da tabela das formas; (2) o A1 por mapa vai para a investigação do núcleo, junto com a Praia (a D-LP5-13); (3) o D2 vai para a mesma investigação; (4) a LP5-2 parte do `lp5_1_r2`, com o S1 vigiado no Ringue do Rookie (0,449 na LP5-1). O Matheus: "Aprovo as 4." A esquiva (a D-LP5-14) segue desligada no candidato, e a arena do Ultimate e do Mega fica em aberto, até a resposta dele | o mapeamento das stats não move a espécie nem o mapa: os dois dependem da tabela das formas e do núcleo, que ficam fora da calibração; partir do `lp5_1_r2` guarda as 6 metas que passam |
| **D-LP5-16** (a esquiva ligada no candidato; DECIDIDA em 2026-11-11) | a esquiva da D-LP5-14 entra no candidato da LP5? Com qual ponto? | **sim:** o candidato `lp5_1_esq` é o `lp5_1_r2` com a esquiva ligada, no ponto `m6_f6_p0` da grade `lp5_1/r4e` (a perspicácia `(mira/10)^0,6 × (1 + 0,5 × atento)`, a agilidade `(fôlego/10)^0,6`, a leitura do golpe de perto desligada). O Matheus: "pode ligar esquiva nova e fazer o merge". No jogo, a luta segue no v21: a esquiva só entra com o v22, na LP5-5 | o `m6_f6_p0` é o único ponto da grade com 6 metas (o P4 passa a mais); com a leitura do golpe de perto ligada (0,35), o E1 reprova e o A1 pende para quem atira. Os números são PROPOSTOS, SEM FONTE |
| **D-LP5-17** (o critério do P1 a P3 e os totais; DECIDIDA em 2026-11-11) | o total dos NPCs não fecha o P1 a P3 em 2 rodadas (o PR #784): o "sem treino ≤ 0,20 e típico ≥ 0,70" pede uma distância que o treino de hoje não dá (o T1 do Rookie é 0,83), e a pior espécie é a forma. O que fazer com o critério, e com o MarinBullmon e o Tortomon, que fechavam sozinhos? | **as 2 como recomendadas.** O Matheus: "Segue sua recomendação". (1) o critério novo (PROPOSTO, SEM FONTE): o líder fica no meio do caminho entre o pet sem treino e o típico, na escala logística do T1 do `lp5_1_esq` (0,832, 0,902, 0,942, 0,959), com 0,10 de folga: sem treino ≤ σ(−d/2) + 0,10 e típico ≥ σ(d/2) − 0,10, d = logit(T1). Dá 0,41/0,59, 0,35/0,65, 0,30/0,70 e 0,27/0,73, do Rookie ao Mega. O desafiante mantém a folga de antes sobre o líder (+0,15 e +0,05). A pior espécie sai do critério, como o V2 (a D-LP5-15), e vai à leitura. Depois, uma rodada ajusta o total de cada NPC pelo critério novo; (2) o MarinBullmon e o Tortomon entram na mesma rodada | o critério antigo e o T1 se contradizem na conta logística: com o T1 entre 0,80 e 0,97, só o topo da faixa cabe. Os limites saem do T1, não das grades da LP5-2, e o código está em `web/app/scripts/equilibrio_poc/criterios.ts` |
| **D-LP5-18** (os 7 NPCs que o total não fecha, e o P5; DECIDIDA em 2026-11-11) | depois da rodada 3 (o PR #784), o Guardromon, o Youkomon, o Myotismon, o Piedmon, o Devidramon, o Puppetmon e o Machinedramon não passam em nenhum total: a distância entre o sem treino e o típico fica de 0,10 a 0,25, e o critério pede de 0,20 a 0,46. E o P5 fica fora das alavancas da LP5-2. O que fazer? | **as 2 como recomendadas.** O Matheus: "Aprovo como recomendadas." (1) uma rodada da divisão dos stats (a D-LP5-9) só para os 7: o total de cada um dividido pelos 6 stats com pesos que somam 6 (PROPOSTOS, SEM FONTE), cruzados com 4 totais da faixa da rodada 3. Os que não fecharem ficam reprovados e vão à investigação do núcleo e à tarefa da tabela das formas; (2) uma leitura curta da vida, sem mudar número nenhum, para explicar os 0,67 do pet da vida no sparring do Champion contra os 0,85 do pet típico na bancada (a saúde, o caráter, o treino perto de 21) | a divisão é a segunda alavanca da D-LP5-9 e custa uma grade curta; a leitura do P5 vem antes de qualquer alavanca da vida. Se uma divisão entrar, a frase do NPC na tela (a lição do `bots.ts`) muda junto, numa etapa do jogo |
