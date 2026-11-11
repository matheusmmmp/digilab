# PLANO DE ANÁLISE V3 — INDIVIDUALIDADE, I2: a linha de base descritiva (2026-11-07, Claude Code, Opus 5.5)

**Status: APROVADO pelo Matheus em 2026-11-07 ("Aprovo todas").** As decisões IP-1 a IP-9 (seção 11) estão DECIDIDAS, todas pela
recomendação. **Nenhuma vida da faixa roda antes de cinco coisas:**
1. este cabeçalho com a marca "APROVADO pelo Matheus";
2. a faixa reservada em `experiments/bancada/faixas.py`, pedida ao Gerente da V3, num commit próprio;
3. o código do I2a na `main` (seção 9): as métricas em `digilab/metrics.py` com os testes delas, a sonda do longe trocada (IP-3) com o
   gabarito da bateria regravado num commit próprio, e o orquestrador `experiments/run_v3_individualidade.py`;
4. a fumaça do orquestrador com as sementes dos testes (101…505);
5. o registro da run (seção 10), num commit empurrado antes da primeira vida.

**De onde vem:** a IN-3 (a linha de base antes de qualquer mecanismo), na `docs/futuro/individualidade_pet.md`, seções 3 a 5, e a
`docs/TAREFA_V3_INDIVIDUALIDADE.md`. A ferramenta é a bateria do I1 (`experiments/sondas_individualidade.py`, #695).

**Este plano é descritivo.** Não há gate, previsão com IC nem contraste que decida. A run mede quanta individualidade o modular de hoje
já produz só pela história (genoma vazio), com os quatro donos, e devolve três coisas ao Matheus:
- quais traços entram no I3 (a regra da 7.4);
- a referência contra a qual o I3 (o genoma) e o I4 (o dono) vão ser lidos;
- o custo real por vida, para o tamanho do I3.

**O que este plano não afirma:** que o pet "tem personalidade", que um traço é um traço de personalidade animal, nem que o modular
supera o A. Os traços são nomes de medida. As referências (seção 0) dão o formalismo, não a correspondência. **Nenhuma alegação de
novidade.**

## 0. O que existe hoje (os fatos que o desenho usa)

- **A bateria** (I1, #695): em cada dia da vida, o momento é a primeira decisão acordada da vida real a partir das 10 h, até as 18 h. Uma
  cópia do pet sai do replay do log até ali, e cada réplica é uma cópia profunda dela, com a rng de política derivada.
  - São cinco janelas de 240 ticks (16 decisões): `nula`, `comida_nova`, `longe`, `bola` e `susto`.
  - A bateria grava, por janela, as ações, a contagem, a latência da ação-chave e as posições. A vida real sai igual (G2).
- **A vida** é a da C4 (`run_v2_memoria_autobio.viver`): o mundo do produto, o corpo do braço P1-c-tapa (com os drives novos e os gestos)
  e o `CanalSemEnsino`, em que o dono cuida só pelos gestos do mundo.
  - Os quatro donos do protótipo são atencioso, relapso, aleatório e incoerente (`run_v2_digibrain_prototipo.DONOS`).
  - São 14 dias e 16 interações por dia.
- **Os cérebros:**
  - o **REL** é o modular do jogo: a `memoria_autobio`, sem facetas (`facetas_mem` falha alto fora do laboratório,
    `web/app/motor/digibrain/arb.ts`);
  - o **REL+F** é o mesmo com as três facetas (`cautela_comida`, `apego_dono`, `ousadia_longe`; a M5, #535).
- **A visão e o cheiro:** a visão alcança 6 células (`raio_visao_celulas`) e o cheiro, 24 (`raio_cheiro_celulas`, `digilab/config.py`).
  O mapa tem 64 × 30 células de 16 subunidades. A ração no canto mais longe, como na sonda do I1, fica a até cerca de 60 células, fora do
  cheiro.
- **A fumaça do I1** (semente de teste 101, comedouro, REL+F, 14 dias; descritiva, sem artefato):
  - o pet comeu a ração do longe em 0 de 42 janelas, coerente com o item anterior;
  - a fruta nova, em 16 de 42;
  - brincou com a bola em 27 de 42;
  - chamou a atenção na `nula` em 32 de 42.
  Uma vida de 14 dias com a bateria levou cerca de 40 s.
- **As referências do formalismo** (verificadas, `docs/referencias/referencias_verificadas.csv`, lidas pelo resumo):
  - a repetibilidade e a norma de reação (intercepto e inclinação): Dingemanse et al. (2010), `10.1016/j.tree.2009.07.013`;
  - os traços correlacionados em síndromes: Sih, Bell e Johnson (2004), `10.1016/j.tree.2004.04.009`.
  As contas abaixo (os componentes de variância, o ICC e os cortes) são SEM FONTE como escolha deste plano.

## 1. A pergunta, escrita antes

**Q-I2: com o genoma vazio, os pets do modular ficam diferentes entre si de um jeito que se repete de dia para dia, e quanto dessa
diferença acompanha o dono e as facetas?**

As expectativas abaixo não são previsões com gate. Ficam escritas para a leitura não se ajustar ao resultado:
- **E1:** a repetibilidade entre pets (R_pet, seção 4.2) é baixa no REL. Com o genoma vazio, só a história separa os pets.
- **E2:** no REL+F, o R_pet do apego, da neofilia e da ousadia é maior que no REL. Esses são os três traços perto de uma faceta.
- **E3:** uma parte visível da diferença entre pets acompanha o dono (η²_dono, seção 4.3), sobretudo pelo relapso, que deixa o pet com
  fome e só.

## 2. O desenho

- **Braços:** REL e REL+F (IP-1).
- **Donos:** os quatro (IP-2).
- **Lugar:** o `comedouro`, o mundo do produto (IP-2).
- **Dias:** 14.
- **A unidade:** a semente, (base, k) como na C4. Cada semente vive com cada dono nos dois braços (pareado): a mesma semente dá o mesmo
  ambiente e a mesma rng de política de partida.
  - Um "pet" da análise é a tripla (braço, dono, semente).
  - A individualidade se mede entre pets do mesmo braço.
- **O tamanho** (IP-6): 5 bases × K = 12 = 60 sementes; 60 × 4 donos × 2 braços = 480 vidas. Com cerca de 40 s por vida e 4 processos, são
  perto de 80 min (seção 6).
- **A bateria:** 3 réplicas por janela por dia. A sonda do longe vem trocada (IP-3, seção 3).
- **A faixa (IP-9):** a **85101…85505**, com as bases 85101, 85202, 85303, 85404 e 85505 e K = 12, no esquema (base, k) da C4. Ela foi
  conferida livre e proposta pelo Gerente da V3 em 2026-11-07 e **aprovada pelo Matheus em 2026-11-07 ("Aprovo a faixa")**, em
  `FAIXAS_RESERVADAS`. As 81101…81505 caem na reserva da linhagem E1, e as 83xxx e 84xxx são da rodada 3 da luta (#697).

## 3. A mudança na bateria antes da run (o I2a)

- **O longe (IP-3):** a ração vai a **16 células** do pet (256 subunidades), na direção sorteada pela rng da posição. É fora da visão (6)
  e dentro do cheiro (24), que é onde o `ousadia_longe` age: o `explorar` com alvo fora da vista, pelo cheiro ou pelo lugar lembrado
  (`digilab/digibrain/pers.py`). Se o ponto cair fora do mapa, ele é cortado para dentro (`deslocar`), e a distância real fica gravada
  na janela.
- **A distância gravada:** a janela do longe e a da comida nova passam a gravar a distância do pet à comida posta (`dist0`).
- **O gabarito** da bateria (`tests/gabaritos/sondas_individualidade.json`) é regravado num commit próprio, antes da troca, com a
  explicação no registro.

Nada mais muda na bateria: as janelas, a hora, as réplicas e a vida continuam as do I1.

## 4. As medidas

### 4.1 Os traços (por janela, réplica r, dia d, pet p)

As frações contam só as decisões acordadas da janela: n_acordadas = n − contagem[`dormir`]. Uma janela com n_acordadas = 0 fica fora do
traço (None) e é contada à parte.

| traço | janela | a medida | perto de |
|---|---|---|---|
| **T-APEGO** | `nula` | fração de `chamar_atencao` | `apego_dono` |
| **T-TEDIO** | `nula` | fração de `explorar` | (o drive do tédio) |
| **T-NEOFILIA** | `comida_nova` | 1 se comeu a fruta posta na janela, 0 se não | `cautela_comida` (no sentido contrário) |
| **T-OUSADIA** | `longe` | 1 se comeu a ração posta na janela, 0 se não | `ousadia_longe` |
| **T-BRINCAR** | `bola` − `nula` | fração de `brincar` na bola menos a da `nula` da mesma réplica e do mesmo dia | — |
| **T-SUSTO** | `susto` − `nula` | fração de `emburrar` no susto menos a da `nula` da mesma réplica e do mesmo dia | — |

A latência da ação-chave e a distância andada (|pos1 − pos0|) entram só no descritivo (seção 8).

### 4.2 A repetibilidade

Por braço e por traço, sobre os pets do braço (os quatro donos juntos):
- **R_pet:** o ICC(1) de uma ANOVA de um fator, com o pet como grupo e todas as janelas válidas dele (dias × réplicas) como observações.
  É σ²_pet / (σ²_pet + σ²_dentro), com o n₀ das amostras desiguais e os componentes negativos truncados em 0.
- **R_dia:** o mesmo ICC(1), com as médias de cada dia (a média das réplicas) como observações. Ele tira o acaso da sonda e mede a
  consistência de dia para dia.
- **R_rep:** o ICC das réplicas dentro do dia (o dia como grupo, dentro de cada pet, juntado). É o quanto a sonda se repete no mesmo
  momento: um R_rep perto de 0 quer dizer que a sonda só mede o acaso da janela.
- **O IC95** de cada R é o bootstrap percentil sobre os pets (2 000 reamostras, rng `derivar_semente("individualidade-boot", braço,
  traço)`).

### 4.3 A parte do dono

- **η²_dono:** a soma dos quadrados entre os donos sobre a soma total, nas médias por pet, por braço e por traço.
- **O IC95:** o bootstrap sobre as sementes, mantendo o pareamento (a semente leva os quatro donos juntos).

### 4.4 As facetas (só o REL+F)

- **A correlação de Spearman entre a média do traço e o valor da faceta no fim da vida** (`estado_interno`):
  - T-APEGO com `apego_dono`;
  - T-NEOFILIA com `cautela_comida` (esperado negativo);
  - T-OUSADIA com `ousadia_longe`.
- **A sonda `sem_faceta`:** fica fora desta run. Ela é do I4.

### 4.5 A síndrome e a norma de reação

- **A síndrome:** a matriz de Spearman entre os seis traços, nas médias por pet, por braço.
- **A norma de reação:** por pet, a reta de mínimos quadrados do traço (a média do dia) contra o dia.
  - O intercepto é o nível, e a inclinação é a mudança ao longo da vida.
  - Gravam-se a média e a variância das inclinações, por braço e por dono.

### 4.6 Onde as contas moram

O ICC(1) com o n₀, os componentes, o η² e a reta por pet vão para o `digilab/metrics.py`, cada um com teste contra um caso feito à mão
("métricas existem uma vez só"). O bootstrap e a leitura ficam no orquestrador.

## 5. O que a run grava

`artifacts_v3_individualidade/`, com a mesma forma das runs da C4:
- `meta.json`: o commit, os sha256, a config e o comando;
- por vida: o log (`vidas/`, empacotado depois como na DC3), a bateria inteira (JSON) e o `estado_interno` final das facetas;
- `tracos.jsonl`: uma linha por janela válida, com (braço, dono, base, k, dia, réplica, traço, valor);
- `analise.json`: os R com os IC, o η², as correlações, a matriz e as inclinações;
- `custo.json`: o tempo por vida.

Cada vida é rejogada do disco (G1), e a bateria é conferida (G2), como no I1.

## 6. O tamanho

Não há poder a calcular, porque não há gate. O K = 12 por base (60 sementes) dá, por braço, 240 pets e cerca de 240 × 14 × 3 janelas
por traço. É o bastante para um IC do R_pet com a largura de poucos centésimos se o R for pequeno; isto é estimativa, SEM FONTE.

O custo: cerca de 40 s por vida na fumaça do I1. 480 vidas com 4 processos dão perto de 80 min, dentro da V3-D8 (no máximo 4 processos e
uma run por vez).

## 7. A leitura (descritiva)

### 7.1 A tabela

Por braço e por traço: R_pet, R_dia e R_rep com o IC95, η²_dono com o IC95, a média e o desvio entre pets e a fração de janelas válidas.
No REL+F, também as três correlações com as facetas.

### 7.2 As frases que a leitura pode escrever

- "o traço X se repete entre pets no braço B" só se o IC95 do R_dia excluir 0;
- "o dono acompanha o traço X" só se o IC95 do η²_dono excluir 0;
- "a faceta acompanha o traço" só se o IC95 bootstrap do Spearman excluir 0;
- fora disso, "não se distingue de zero nesta run". Nada vira "a personalidade não existe".

### 7.3 As expectativas E1 a E3

Elas são relidas contra a tabela, sem nenhum ajuste.

### 7.4 A regra dos traços para o I3 (escrita antes, IP-5)

Um traço **sai** da bateria do I3 se, no REL, valer qualquer uma das três condições:
- (a) a fração de janelas válidas for menor que 50 %;
- (b) for binário e a fração de 1 estiver fora de [5 %, 95 %];
- (c) o R_rep tiver o IC95 inteiro abaixo de 0,05.

O (c) é o caso em que a sonda só mede o acaso da janela. Os traços que ficam são os do I3. Se sobrarem menos de três, a bateria volta ao
Matheus antes do I3.

## 8. O descritivo (sem leitura)

- a latência da ação-chave por traço;
- a distância andada;
- os dias sem sonda (o pet dormiu a janela de busca);
- o susto no corpo no fim da janela do susto;
- tudo isso por dono e por braço.

## 9. As missões (cada uma num PR)

| missão | o quê |
|---|---|
| **I2-plano** | este documento (PROPOSTO) e as IP-1 a IP-9 |
| **faixa** | o Gerente reserva a faixa num commit próprio |
| **I2a** | o gabarito da bateria regravado antes; o longe a 16 células e a `dist0`; as métricas da 4.6 no `digilab/metrics.py` com testes; o orquestrador `run_v3_individualidade.py` com a trava (o cabeçalho APROVADO, a faixa, no máximo 4 processos, nada por cima de uma pasta existente) e a fumaça com as sementes dos testes |
| **I2b** | o registro, a run uma vez e o `docs/RESULTADO_V3_INDIVIDUALIDADE.md` |

## 10. O registro da run

Antes da primeira vida, numa seção nova no fim deste plano, ficam:
- o commit, os sha256 do orquestrador, da bateria e do `metrics.py`;
- a config, o comando, a faixa e a contagem da suíte do dia.

## 11. As decisões (DECIDIDAS pelo Matheus em 2026-11-07, todas pela recomendação; cada uma com o custo de errar)

| | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **IP-1** | os braços | **REL e REL+F**: o REL é o pet do jogo, e o REL+F é o único com as facetas que a 4.4 lê | só o REL: a parte da história que as facetas explicam fica sem leitura; só o REL+F: a linha de base não é a do jogo |
| **IP-2** | os donos e o lugar | **os quatro donos do protótipo, no `comedouro`** | o `longe_fixo` mede o longe em vez do pet; menos donos tiram o η² |
| **IP-3** | o longe | **a 16 células, fora da visão e dentro do cheiro**, no lugar do canto | no canto, o pet não sente a ração e o traço sai pela 7.4 sem ter medido nada |
| **IP-4** | os traços | **os seis da 4.1**, com o T-BRINCAR e o T-SUSTO como diferença contra a `nula` | traços brutos sem a `nula` misturam a sonda com o estado do pet no momento |
| **IP-5** | a regra dos traços para o I3 | **a da 7.4**, escrita antes | escolher os traços olhando os R da run seria ajustar a medida ao resultado |
| **IP-6** | o tamanho | **5 bases × K = 12 = 60 sementes, 480 vidas**, cerca de 80 min | menor deixa o IC do R largo demais para separar o I3 da linha de base; maior só custa tempo |
| **IP-7** | as réplicas e a janela | **as do I1:** 3 réplicas, 240 ticks, às 10 h | mudar agora pede regravar o gabarito de novo; o R_rep da run mostra se faltam réplicas |
| **IP-8** | onde as contas moram | **ICC, componentes, η² e a reta no `digilab/metrics.py`**; o bootstrap no orquestrador | as contas no orquestrador ficam duplicadas no I3 e no I4 |
| **IP-9** | a faixa | **pedida ao Gerente**, com 60 sementes em 5 bases, como as da C4 | uma faixa improvisada quebra a regra das sementes |

## 12. O registro da run

Escrito em 2026-11-08, antes da primeira vida da faixa, no branch `v3-individualidade-i2b`.
- **O commit do código:** `ad207f7` (a `main` com o I2a, #707). O registro entra num commit próprio por cima dele, que não muda código.
- **Os sha256** (o conteúdo no commit `ad207f7`):
  - o orquestrador `experiments/run_v3_individualidade.py`: `b702ee2c7aaae7bfef3c0d76d04d2254ef5f8db9aee0de57f17407b4aa5b04d8`;
  - a bateria `experiments/sondas_individualidade.py`: `569088c5ce135d97f961ea2e9c71ba9acb1b925a7d95840ada4da69f3e10f621`;
  - o `digilab/metrics.py`: `46d0022ae6dd6c2f58346d1b8425fdb1441c065540668fe9ea767021a509ac54`;
  - a config: `c82081abde15e771976483a8a4c5a3818501874ae443de7c9e8e972860eb0958`.
- **A config:** `experiments/configs/v3_individualidade/individualidade.json`: o REL e o REL+F, os quatro donos, o `comedouro`, 14 dias,
  16 passos do dono por dia, as bases 85101, 85202, 85303, 85404 e 85505 com K = 12, num total de 480 vidas.
- **O comando:**
  `python experiments/run_v3_individualidade.py --config experiments/configs/v3_individualidade/individualidade.json --processos 4`,
  com a saída em `artifacts_v3_individualidade/` (fora do git).
- **A faixa:** 85101…85505, reservada em `experiments/bancada/faixas.py` e aprovada pelo Matheus em 2026-11-07 ("Aprovo a faixa").
- **A suíte do dia:** `python -m pytest tests/ -q` no commit `ad207f7`: 5108 passed, 7 skipped, em 3 h 13 min (Python 3.13.0).
- **A run roda uma vez.** Se ela cair por bug, a pasta vai para `artifacts_v3_individualidade/caida_1/`, o conserto vai num PR e o
  desvio vai para o registro, antes de rodar de novo.

## 13. Adendo 1: as facetas dentro do dono (descritivo, sem run; 2026-11-09)

**Status do adendo: DECIDIDO pelo Matheus em 2026-11-09** (a escolha "Descritivo dentro do dono", depois do resultado do I2). Escrito e
commitado antes da conta.

- **A pergunta:** as três correlações da 4.4 saíram no sentido contrário ao esperado (`docs/RESULTADO_V3_INDIVIDUALIDADE.md`, seção 2).
  Como o dono move muito o traço (η² alto), a inversão pode vir do dono mover o traço e a faceta juntos. O adendo olha a mesma
  correlação dentro de cada dono.
- **Os dados:** só os artefatos do I2 (`artifacts_v3_individualidade/medidas.json`). Nenhuma vida nova, nenhuma semente nova.
- **A conta:** a mesma da 4.4 (`facetas` do orquestrador), com o mesmo bootstrap (2 000 reamostras sobre os pets, a mesma rng), sobre
  os pets do REL+F de cada dono, separadamente:
  - o atencioso, o relapso e o aleatório, com 60 pets cada;
  - o incoerente fica fora, porque as vidas dele são as do atencioso (D-IND-I2b-1).
- **O artefato:** `artifacts_v3_individualidade/facetas_por_dono.json`, gravado por `experiments/descritivo_individualidade_facetas.py`,
  com o sha256 do `medidas.json` lido.
- **A leitura:** só descritiva, com as frases da 7.2: "a faceta acompanha o traço dentro do dono D" só se o IC95 excluir 0.
  - **Não se lê causa:** a correlação dentro do dono ainda não separa a faceta que move o traço do traço que move a faceta. Isso é da
    sonda `sem_faceta` do I4.
  - **Não se ajusta nada:** o adendo não muda o I2, a regra 7.4 nem o I3.
