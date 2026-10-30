# TAREFA V2 — METABOLISMO ENERGÉTICO: conversão, reserva e mobilização no corpo (2026-10-08)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: Gerente. Workers: **B** (o corpo e o grafo, depois do Digicorpo), **D** (o regime na bancada), **A** (o porte para a web,
depois) e **C** (o adendo do plano do corpo). Worktree e branch de cada etapa: `v2-metabolismo-<etapa>`. Status: **ABERTA.** **ME-1 a ME-7
DECIDIDAS pelo Matheus em 2026-10-11, todas pela recomendação** (seção 9).

**O que já está decidido** (Matheus, 2026-10-08):
- **o Metabolismo energético entra agora,** antes da calibração do corpo (as sementes 33101…33505 do
  `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, seção 6);
- **a calibração do corpo** só roda depois dele (o adendo 3 do plano, neste PR).

**O nome:** "Metabolismo energético" é o item 1 da lista de sistemas a acrescentar (`docs/DEFINICOES_CORPO_V2.md`, seção 8.1, no #259).

**O que muda numa decisão anterior.** A `docs/TAREFA_V2_CORPO_DRIVES.md` (seção 1, "Fica fora") deixou de fora "o ATP como químico
próprio: o cansaço de hoje faz esse papel". Esta tarefa não cria um ATP. Ela põe o **combustível** por baixo do cansaço e deixa o cansaço
como está (ME-1).

## 1. O ponto de partida (conferido no código, 2026-10-08)

- **Não há químico de energia.** Os químicos de hoje são `fome`, `desconforto`, `cansaco`, `tristeza` e `dano` (`corpo.QUIMICOS`), mais
  os dos órgãos e da etapa 6.
- **A digestão** (`corpo.grafo_do_corpo`, a `Reacao("digestao")`) consome `alimento` e `fome` na mesma quantidade, até `taxa_digestao`
  por tick. Com o banheiro, ela põe 1/3 do digerido na `vontade`. O alimento que sobra com a fome em 0 é descartado: é o corte de hoje.
- **O cansaço** sobe por emissores:
  - acordado de dia, `C / 900` = 500 por tick;
  - acordado à noite, × 1,8;
  - as atividades: o brincar do pet e o do dono, o explorar e o andar no mundo físico (75 por subunidade).

  Ele cai dormindo, `C / 240` por tick.
- **Não há conversão nem reserva.** Comer não dá energia, e a energia de hoje não depende do que o pet comeu.
- **A fome** sobe `C / 1200` = 375 por tick, sempre.
- **O teto de pesos:** o cérebro A com o corpo e o banheiro tem **998 pesos** (`tests/test_banheiro_cerebros.py`, linha 198: 756 + 48
  + 192 + 2), e o teto é 1000 (`ConfigLobos.maximo_pesos`). Cada receptor novo nas entradas custa **24 pesos**: 3 regras de tempo
  livre × 8 ações. Um receptor a mais daria 1022.

## 2. A pergunta

**O pet sente o custo de energia do que faz, e esse custo depende do que ele comeu?** Hoje brincar cansa igual com o pet bem alimentado ou
faminto, e comer não dá energia. Com o metabolismo:
- **a comida vira combustível;**
- **o excedente vira reserva;**
- **a reserva volta quando o combustível cai;**
- **sem combustível nem reserva,** o pet cansa mais depressa.

## 3. O desenho (PROPOSTO)

Tudo em inteiros na escala C = 450000, no grafo do corpo (`digilab/corpo_grafo.py`), atrás da sub-chave `metabolismo` da `ConfigCorpo`.
Ela exige a `digestao`, pela regra E-9 (um órgão por vez).

**Dois químicos novos**, guardados como concentração (e não como falta), sem receptor para o cérebro (ME-2):

| químico | o que é | começa em | teto |
|---|---|---|---|
| `combustivel` | a energia disponível | C/2 | C, com descarte |
| `reserva` | o estoque | C/4 | C, com descarte |

**As reações e os emissores:**

| peça | tipo | conta (por tick, ou por estímulo) | o que faz |
|---|---|---|---|
| **conversão** | a reação `digestao` passa a produzir também | `combustivel += div_arred(t · rend_num, rend_den)`, com o resto guardado (como a vontade) | a comida digerida vira combustível. `t` é o que a digestão tirou de `alimento` e de `fome` no tick |
| **gasto basal** | emissor, acordado / dormindo | `combustivel −= 375` acordado, `−= 187` dormindo | o corpo gasta para viver |
| **gasto das atividades** | os mesmos estímulos de hoje | o brincar, o explorar, o andar e o brincar do dono tiram do `combustivel` o mesmo número que somam ao `cansaco` | o que o pet faz custa combustível. **O cansaço de hoje não muda** |
| **armazenamento** | reação com limiar (acima de 3C/4) | `combustivel → reserva`, até 375 por tick | o excedente vira reserva |
| **mobilização** | reação com limiar (abaixo de C/2) | `reserva → combustivel`, até 375 por tick | a reserva volta quando o combustível cai |
| **falta de combustível** | emissor com limiar (abaixo de C/4), um degrau | `cansaco += 500` por tick | **a única ponte** entre o combustível e o cansaço (ME-1) |

**Os números** são PROPOSTOS, SEM FONTE:
- o gasto basal acordado é igual à subida da fome. Assim, um pet que come o que a fome pede mantém o combustível;
- dormindo, o gasto é a metade;
- a falta soma o cansaço de um dia acordado.

O passo 0 da calibração (seção 7) escala o gasto.

**Por que não há um segundo cansaço (ME-1):**
- o cérebro não vê o combustível nem a reserva;
- o único efeito deles sobre o pet é o emissor da falta, que sobe o cansaço de sempre;
- **com o combustível acima de C/4, o cansaço é exatamente o de hoje**, tick a tick (o G-HOJE-M);
- quando a falta aparece, o pet a sente pelo receptor `energia` que já existe.

**O que o grafo precisa de novo:**
- **as reações com limiar** (o armazenamento e a mobilização) e a produção com fração e resto (como a vontade, na conversão);
- **um gatilho "abaixo"**, o espelho do "acima" do banheiro, para a mobilização e a falta.

O B decide se isso vira um campo da `Reacao` ou um tipo novo, e declara no PR.

**As quatro checagens:**
1. **fechado:** os químicos novos estão na tabela;
2. **sumidouro:**
   - o `combustivel` é gasto pelo basal, pelas atividades e pelo armazenamento;
   - a `reserva`, pela mobilização;
   - os dois têm teto;
3. **automantido:**
   - o `combustivel` é reposto pela conversão e pela mobilização;
   - a `reserva`, pelo armazenamento;
4. **laço de ganho:** há duas retroalimentações **negativas**:
   - menos combustível dá mais mobilização;
   - mais combustível dá mais armazenamento.

   A ponte da falta para o cansaço não volta ao combustível. O sono muda o gasto, mas quem decide dormir é o cérebro, e isso não é aresta
   do grafo. Se a checagem 4 contar a retroalimentação negativa como laço positivo, o B ajusta a leitura do sinal e registra.

## 4. O que fica igual

- **`engine.py`, o `AcaoPet`, o mundo, o cérebro (sem receptor novo, ME-2) e o motor:** não mudam. Os estímulos já passam pelo `Corpo`
  (`acao_pet`, `acao_dono`, `estimulo_andar`), e o gasto entra lá dentro.
- **A fome:** é a de hoje (ME-5).
- **O excedente do estômago com a fome em 0:** continua descartado (ME-4).
- **Com a sub-chave desligada,** a vida de hoje, byte a byte (G2).
- **O Digicorpo** (a rede de si) não vê o combustível. Ele prevê os receptores, e a falta chega a ele pelo `energia`.

## 5. Etapas e donos

| etapa | dono | arquivos | entrega | gates |
|---|---|---|---|---|
| **0. gabaritos** | B | `tests/gabaritos/metabolismo_vidas_de_hoje.json` | as vidas do corpo inteiro (química, etapa 6, banheiro, mundo físico), gravadas **antes** | — |
| **1. a química** | B, **depois do Digicorpo** | `digilab/corpo.py`, `digilab/corpo_grafo.py`, a sub-chave `metabolismo` e os números no fim da `ConfigCorpo` | os químicos, as reações e os emissores da seção 3 | **G2**, **G-GRAFO**, **G-MEC-M**, **G-HOJE-M**, **G-CONS-M**, **G-RECEPTOR-M**, **G1** |
| **2. a bancada** | D | `experiments/bancada_v2.py` | o metabolismo nos regimes do bloco do corpo (ME-6); a medida descritiva (seção 6) | o G1 de toda vida; o G-P0C do plano com o metabolismo |
| **3. o adendo do plano** | C | `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, adendo 3 | o passo 0 da calibração (ME-7) | commitado antes da calibração (vai neste PR) |
| **4. a web** | A | `web/app/motor/corpo.ts` e o gabarito do corpo | o metabolismo em TypeScript, quando o corpo for ao jogo | **G-PAR** |

**A ordem:** 0 → 1 → 2. O adendo vai neste PR. **A calibração do corpo (33101…) espera a etapa 2.**

## 6. Gates e medidas

- **G2:** com a sub-chave desligada, os gabaritos do corpo de sempre saem byte a byte:
  - `corpo_vidas_de_hoje.json`, `corpo_mundo_vidas_de_hoje.json` e `banheiro_vidas_de_hoje.json`;
  - o da etapa 0.
- **G-GRAFO:** as quatro checagens passam com o metabolismo em toda combinação de sub-chaves. Tabelas feitas para falhar (o combustível
  sem gasto, a reserva sem armazenamento) falham alto.
- **G-MEC-M:** a conta exata de cada peça:
  - a conversão, com o resto;
  - o gasto basal acordado e dormindo;
  - o gasto de cada atividade, igual ao cansaço dela;
  - o armazenamento e a mobilização nos limiares;
  - a falta subindo o cansaço só abaixo de C/4.
- **G-HOJE-M:** em malha aberta (as mesmas ações forçadas, tick a tick), com o combustível mantido acima de C/4, todos os químicos de
  antes são **iguais** aos do corpo sem metabolismo, nos três mundos e no mundo físico. Também há um caso em que a falta dispara e o cansaço
  passa a diferir só a partir do tick dela.
- **G-CONS-M:** a conservação:
  - o combustível produzido é o alimento digerido × rend_num / rend_den, com o resto;
  - o que sai do combustível é o gasto, o armazenamento e o descarte no teto, e o que entra é a conversão e a mobilização;
  - a contabilidade fecha por tick.
- **G-RECEPTOR-M:**
  - o cérebro não lê `combustivel` nem `reserva` (AST, mais um espião na `PercepcaoCorpo`);
  - o `n_pesos` com o metabolismo é o de sem ele (998 com o banheiro);
  - nenhum emissor novo sobe o `cansaco` fora da falta.
- **G1:** o replay refaz o combustível e a reserva.
- **A medida descritiva** (bancada, etapa 2), por vida:
  - a fração do tempo acordado com a falta;
  - o combustível e a reserva no fim de cada dia;
  - quantas vezes a falta disparou;
  - o tempo entre comer e brincar no P1-c.

  É só relato: o plano do corpo não ganha gate novo.

## 7. O reflexo no plano do corpo

- **O adendo 3** de `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md` (neste PR, PROPOSTO, depende das ME-1 a ME-7) põe o metabolismo no bloco do
  corpo e um **passo 0** na calibração.
- **O G-HOJE do plano (hoje × química) fica sem o metabolismo:** ele mede a química dos drives contra hoje, e o metabolismo é outra
  pergunta.
- **O bloco do corpo, com o metabolismo** (ME-6):
  - o P0-q, o P1-q, o P0-c, o P1-c e os acoplados;
  - o P0-q e o P0-c ganham o mesmo metabolismo. Assim o G-P0C segue valendo: o instinto não lê os químicos novos, e o combustível
    depende só das ações e da comida, que são as mesmas.

## 8. Fora desta tarefa

- **As três fomes** (proteína, amido, gordura), a sede, o ATP como moeda de cada órgão e o custo de manter órgãos.
- **A fome que lê o combustível** (ME-5).
- **A morte por falta de combustível:** não há morte no corpo.
- **A reserva no corpo visível** (o pet mais gordo): é tela, depois.
- **O Creatures é só pista.** O Gerente cita a mitocôndria e o fígado como órgãos do Creatures ligados à energia. Nada disso foi conferido
  em fonte primária (`docs/referencias/G_REVISAO_CORPO_QUIMICO.md`, P1), e nada aqui depende disso. Não há alegação de novidade.

## 9. Decisões do Matheus

**DECIDIDAS em 2026-10-11: ME-1 a ME-7, todas como recomendado.** O adendo 3 do plano do corpo segue as sete (conferido no mesmo dia).
**Revisão da grade da ME-7 (PCD-9, DECIDIDA em 2026-10-12, pela recomendação):** o mesmo multiplicador no basal e no gasto das atividades, em {¼, ½, 1}.
Está em `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, A3.2b. O texto da ME-7 abaixo fica como foi decidido.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| ME-1 | Como a energia e o cansaço se relacionam | **(b) alimentar:** o combustível fica por baixo; o cansaço de hoje segue sendo a fadiga e o sono; só a falta de combustível sobe o cansaço, por um emissor com limiar. As outras opções: **(a) substituir** (o drive `energia` passa a ler o combustível) e **(c) coexistir** (dois drives que o cérebro vê) | **(a):** o sono deixaria de descansar sem comida, toda vida de hoje muda, e o G-HOJE do plano perde a base. **(c):** é o segundo cansaço: o mesmo custo entra duas vezes no sinal, e um receptor novo passa do teto de pesos |
| ME-2 | O que o cérebro vê, e a saída do teto de 1000 pesos | **(i) nenhum receptor novo:** a falta chega pelo `energia` que já existe (0 pesos). As saídas, se um receptor for preciso: **(ii)** um receptor só no sinal, sem entrada de decisão (0 pesos: os canais não custam peso); **(iii)** trocar o susto pelo receptor novo nas entradas (o susto já está fora do sinal; 24 por 24, fica em 998); **(iv)** subir o `maximo_pesos` | **(ii):** dá recompensa por encher a reserva, o que é um incentivo a comer demais. **(iii):** muda o cérebro da etapa 6 com a chave ligada. **(iv):** mexe num teto PROPOSTO "para o replay", que vale para todos os cérebros |
| ME-3 | O que o combustível paga | **o gasto basal (acordado e, pela metade, dormindo) e as atividades**, com o mesmo número que elas somam ao cansaço | só o basal: brincar não custaria combustível, e o metabolismo não mudaria nenhuma escolha. Só as atividades: o pet parado nunca ficaria sem combustível |
| ME-4 | O alimento que sobra com a fome em 0 | **continua descartado** (o corte de hoje); a reserva vem do combustível acima de 3C/4 | ir para a reserva: o pet ganha por comer além da fome, e o dono que alimenta demais passa a "engordar" o pet, outra pergunta |
| ME-5 | A fome passa a ler o combustível? | **não, por ora:** a fome é a de hoje | sim: a fome muda em toda vida com a chave, e o G-HOJE-M perde a igualdade exata |
| ME-6 | Em que regimes da bancada o metabolismo entra | **no bloco do corpo:** o P0-q, o P1-q, o P0-c, o P1-c e os acoplados, todos com ele. O G-HOJE do plano (hoje × química) fica sem | só no regime "corpo": o P0-c deixa de decidir igual ao P0-q quando a falta dispara, e o G-P0C quebra |
| ME-7 | Como os números entram na calibração | **um passo 0 da calibração do corpo, antes da grade dela:** o gasto em {½, 1, 2} × (375, 187), só no P0-q; fica o mais perto de 1 em que a fração do tempo acordado com falta cai em [0,05; 0,30] | calibrar junto da grade do corpo: 3 × 9 pontos, o triplo do custo. Não calibrar: com os números PROPOSTOS a falta pode nunca disparar (o metabolismo não faz nada) ou disparar sempre (o pet vive cansado) |

## 10. Etapa 4, entregue (2026-10-18)

Pedida pelo W-PORTE: o corpo do pet v11 tem o metabolismo (`docs/TAREFA_V2_W_PORTE_CEREBRO_A.md`, seção 11). O Matheus decidiu portar o
metabolismo antes da etapa 4 do W-PORTE, com o ponto do v11 como está.

- **O porte:** `web/app/motor/corpo.ts`, de `digilab/corpo.py` e `digilab/corpo_grafo.py`, só o motor e a paridade.
  - O `configCorpo` deixou de falhar com o `metabolismo` ligado e confere o que o `__post_init__` do Python confere: a digestão, os
    inteiros positivos, os iniciais em [0, C] e os limiares em ordem.
  - Os químicos `combustivel` e `reserva`, sem receptor, e a contabilidade (`CONTAS_METABOLISMO`), no `paraDict` como no Python.
  - A conversão na digestão, com o resto (`resto_combustivel`) e o descarte no teto; o gasto basal acordado e dormindo (fase 1).
  - O gasto das atividades: `gastoDaAtividade`, com o fator `gasto_atividades_num`/`gasto_atividades_den`, no brincar do pet e do dono,
    no explorar e no andar.
  - O armazenamento e a mobilização, como reações com limiar, entre a fase 1 e a 2; a falta pelo gatilho `abaixo` (fase 2).
  - O grafo ganhou o que o Python ganhou: a `Reacao` com `fracoes`, `le`, `lado` e `limiar` (campos opcionais, a tabela de antes não
    muda), as arestas das transferências e as checagens 2b e 3b.
  - A constante nova `CCO_V11` (`motor/constantes.ts`): o que o corpo do ponto do v11 muda sobre o `CCO`. O `corpo.ts` a completa em
    `CCO_CORPO_V11`. O `constantes.test.mjs` confere as 7 folhas contra a `config_v11.corpo` do gabarito do cérebro A.
- **O gabarito:** `experiments/exportar_gabarito_corpo.py` ganhou a seção `metabolismo_v11`, o corpo do ponto do v11, sem o mundo
  físico. A config vem do exportador do cérebro A, a mesma que as vidas do v11 usaram: o gasto 4/5 (basal 300/150) e o ponto (2, 1) do
  adendo 4. A seção traz a config, as taxas das atividades, o grafo, uma grade de 713 casos (com os receptores do v11) e uma sequência de
  3000 operações com o sha256. As outras seções saem iguais, conferido chave a chave contra o arquivo de antes.
- **G-PAR, passa** (`web/app/test/metabolismo.test.ts`, no Node, 30 testes):
  - as seções `metabolismo` e `metabolismo_gasto`: a config, o grafo (a tabela e o relato), a grade, a grade com a conversão 2/3, as
    grades com o gasto × 1/2 e × 2 e as taxas delas, e a sequência longa, com o sha256 de q, da janela, do resto e das contas;
  - a seção `metabolismo_v11`, do mesmo jeito, com os receptores do v11 em cada caso e no fim. O `CCO_CORPO_V11` é igual, campo a campo,
    à `config_v11.corpo` dos dois gabaritos. Um controle negativo (o basal 375, ou o gasto 1/1) é pego;
  - o paladar não depende do metabolismo (as configs dele no gabarito não o ligam) e fica para a etapa 5 do paladar.
- **Os gates do Python, em TS, onde o gabarito permite:**
  - G-GRAFO: as checagens passam em 7 combinações, com e sem o mundo, sem laço novo; as tabelas feitas para falhar falham alto;
  - G-MEC-M: a conversão com o resto, o basal (375/187 e o 300/150 do v11), cada atividade (1/1 e 4/5), os limiares e a falta;
  - G-CONS-M: as contas fecham depois de cada operação, nas grades, nas sequências e numa sequência de 6000 com a conversão 2/3;
  - G-HOJE-M em malha aberta: as vidas de hoje do gabarito (com a digestão e a Vida), rejogadas com o metabolismo. Com o corpo cheio,
    duas das três vidas não entram em falta, e os químicos de antes dão o mesmo sha256 do Python. Do nascimento, as três entram em falta,
    e até o tick dela tudo é igual; no tick dela, só o cansaço difere, +500;
  - G-RECEPTOR-M: os receptores são os mesmos com e sem o metabolismo, e nenhum emissor novo sobe o cansaço fora da falta.
- **Sem o metabolismo, o corpo sai igual:** os testes de antes do `corpo.ts` passam sem mudança.
- **O que não foi feito: o laço do corpo do v11.** As quatro vidas da seção `v11` de `lobos_python.json` ainda passam só pelos ganchos
  (etapa 3 do W-PORTE). Para rodar o laço de verdade em TS, faltam duas peças, as duas fora desta etapa:
  - o `Motor` do v11 com o corpo por tick, o `_laco` e o `_decidir` de `digilab/motor_corpo.py`: decidir, `acao_pet`, a atividade, o
    gancho, `passo` e `avancar_um_tick`, mais os gestos do dono. É a etapa 4 do W-PORTE;
  - a sujeira das vidas, que sai da `rng_ambiente` do Python (`random.Random`, Mersenne Twister). O TS só tem o mulberry32
    (`motor/rng.ts`). A etapa 4 do W-PORTE precisa de um porte do `random.Random` ou de um gabarito com a sujeira e o sono por tick.
- **Os desvios:** em `docs/registro/2026-10.md`, 2026-10-18.
- `npm run tipos` limpo; `npm test` com 35 arquivos e 417 testes passando; `tests/test_corpo_quimica.py` e `tests/test_metabolismo.py`
  passam (72).
