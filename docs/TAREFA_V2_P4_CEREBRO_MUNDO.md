# TAREFA V2 — P4_CEREBRO_MUNDO: o cérebro A com o planejador no mundo 3D (2026-10-21)

Coordenador: Gerente (Claude Code). Worker do esboço: Claude Code (worktree `v2-gatec-p4`). Worker da execução: a definir. Worktree e
branch da execução: `v2-p4-cerebro-mundo`, um branch por etapa. Status: **ABERTA** (o esboço entregue, #377; as P4-1 a P4-8
DECIDIDAS pelo Matheus em 2026-10-21, pela recomendação; o plano da etapa 4 em `docs/PLANO_ANALISE_V2_P4_CORPORIFICADO.md`, PROPOSTO;
nenhuma etapa de código começou).

Categoria: implementacao (a tarefa, com as runs das etapas 4 e 5 como experimento); o PR deste esboço é `arquitetura`. Origem: Matheus,
2026-10-21: o Gate C aprovado em parte (a validação do J5 com o adendo 8, #370) libera a P4 do `docs/futuro/mundo_3d.md` com o
planejador.

As marcas seguem as do `docs/TAREFA_V2_V3_CREDITO_CANAL.md`: [IMPLEMENTADO] (está no código da `main`), [OBSERVADO] (tem artefato),
[HIPÓTESE] e [PROPOSTA].

## 0. De onde a tarefa parte

- **O Gate C, em parte** [OBSERVADO], `docs/RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8.md`:
  - o G-T1 passa: `q`(P1-plan) − `q`(P1) = 0,197, IC95 [0,075; 0,323], o Holm rejeita;
  - o G-T1-DESF passa: o modelo do desfecho sozinho basta para a revalorização;
  - o G-T2 é inconclusivo por premissa: o mapa não foi testado;
  - o rótulo "pensa" (R-7) não vale.
- **O Gate B** [OBSERVADO], `docs/TAREFA_V2_WORLD_POC_02.md`: o POC fecha o laço do contrato sensório-motor com o corpo do jogo, mas com
  o cérebro de teste e só em TS. Pela CP-7, **a paridade do mundo com o Python é o critério de entrada da P4**.
- **O que existe hoje, e onde** [IMPLEMENTADO]. Cada peça de que a P4 precisa mora num lugar só:

| peça | Python (`digilab/`) | TS do motor (`web/app/motor/`) | TS do POC (`web/app/poc/mundo3d/`) |
|---|---|---|---|
| o mundo do J1 (o mapa, as árvores, a comida, a bola, a visão em disco, os alvos) | `mundo.py` | `mundo.ts`, com o G-PAR (`web/app/test/mundo.test.ts`) | não: um mundo próprio (a sala com paredes, a comida e a bola) |
| o mundo do J5 (os troncos, a fruta ao lado, a fruta na mão, a troca e a parada das árvores) | `mundo.py`, atrás das chaves | não | não |
| o contrato da seção 4 do `mundo_3d.md` (o cone com oclusão, os bigodes, o contato, o resultado percebido, a Intenção, o controlador com A* inteiro, o empurrão) | não | não | sim (`sensores.ts`, `controlador.ts`, `fisica.ts`, `tipos.ts`) |
| o corpo | `corpo.py` | `corpo.ts` | o `corpo.ts` do motor (CP-6) |
| o cérebro A | `policies/lobos.py`, com todas as chaves | `lobos.ts`: o v11 **sem** as chaves do mundo, das frutas e do plano | o cérebro de teste (`cerebro.ts`) |
| o planejador (o `ModeloMundo` e o lobo `planejamento`) | `modelo_mundo.py`, `policies/lobos.py` | não | não |

**A tarefa é juntar as três colunas:** o contrato, que só existe no POC, vai ao mundo do motor, onde moram o J5 e o cérebro com o
planejador; e o cérebro com o planejador vai ao TS, para o POC mostrar o pet de verdade.

## 1. Pergunta

**O pet com o planejador ainda deixa de escolher a fruta que passou a fazer mal quando percebe e anda pelo contrato sensório-motor** (o
cone com oclusão e o controlador), e não pela visão em disco e pelo passo reto de hoje?

- É a replicação corporificada do G-T1 do J5 (P4-3), com a mesma pergunta (DS-1 do `docs/futuro/pet_que_pensa.md`) e o mesmo contraste.
- Na seção 7 do `mundo_3d.md`, é a P4 ("percepção espacial e autonomia corporificada"). A saída dela é o segundo Gate C, já
  corporificado.
- **O que ela não pergunta:** se o pet "pensa", nem se o mapa funciona (o T2 fica com o plano próprio do J5).

## 2. Depende de

- **Na `main`:**
  - o J5 e o mundo dele (#289, #290, #294, #295, o adendo 8 no código);
  - o POC-02 (#362, #363);
  - o porte do A v11 para a web (#343), como modelo da paridade do cérebro.
- **As decisões que já valem:**
  - a W-1 (a física no motor, em inteiros);
  - a W-3 (a posição absoluta fica, marcada como acesso privilegiado);
  - a W-4 (as paredes atrás de chave desligada);
  - a W-5, cumprida em parte pelo Gate C de 2026-10-21;
  - a CP-7 (a paridade como entrada).
- **As decisões:** as P4-1 a P4-8 (seção 8), DECIDIDAS em 2026-10-21, pela recomendação.
- **Não depende do crédito por canal** (V3-9): o P1-plan não ganha a chave (`docs/TAREFA_V2_V3_CREDITO_CANAL.md`, seção 6).

## 3. O desenho e a mudança mínima

### 3.1 A rota: o contrato vai ao mundo do motor (P4-1, DECIDIDA)

- **O contrato do POC entra no mundo do motor,** atrás de uma chave desligada (`ConfigMundo.contrato`, PROPOSTO), em `digilab/mundo.py`
  e em `web/app/motor/mundo.ts`. Se o `mundo.py` ficar grande demais, a parte nova vai num módulo próprio que ele usa.
- **Duas chaves, não uma** (PROPOSTO): a dos **sensores** (o cone com oclusão, os bigodes, o contato e o resultado percebido) e a do
  **controlador** (o A* inteiro, o bloqueio e o deslize, no lugar do `passo_ate`). Assim o piloto separa o que muda pela percepção do que
  muda pelo andar (R-P5).
- **A referência é o código do POC.** Os números dele (o cone de 120°, os 8 bigodes, o `TICKS_BLOQUEADO`, os `k` = 4 sub-passos da seção
  4.5) entram em `digilab/config.py` como PROPOSTOS e SEM FONTE. Hoje o `config.ts` do POC diz que nenhum deles entra no motor; esta
  tarefa muda isso, com a chave.
- **O POC passa a desenhar o mundo do motor,** e a vista continua só lendo. O mundo próprio do POC fica como está, para o POC-01a e o
  POC-02 se refazerem.
- **Por quê:** fica um mundo só, o do J5, que já tem a paridade do J1 e as chaves do J5. O POC tem o contrato, mas não tem as árvores,
  as frutas nem o dono do J5.

### 3.2 O cérebro lê o contrato por um adaptador no motor (P4-2, DECIDIDA)

- **A percepção:** com a chave dos sensores ligada, o motor monta a `PercepcaoMundo` de hoje a partir dos sensores do contrato.
  - Os `vistos` e os `troncos` passam pelo cone e pela oclusão.
  - O `dx`, o `dy` e a posição do pet continuam (W-3).
  - O `ModeloMundo` já confere os `troncos` contra a conta da visão ("diverge, falha alto"); com a chave, a conta passa a ser a do cone.
- **O que é registrado:** o `resultado` percebido e o `contato` entram no registro de cada decisão (seção 5.1 do `mundo_3d.md`) e no
  `ocorrido`. O cérebro A **não ganha entrada nova**: nenhum peso novo e nenhuma calibração.
- **A decisão:** o cérebro continua escolhendo a `AcaoPet` e o `Alvo` entre os candidatos do motor (o `escolher_alvo`). O motor traduz
  a escolha na Intenção da tabela 4.3 do `mundo_3d.md`, e o controlador a executa nos 15 ticks.
- **O que isso testa:** o mesmo cérebro, com outra percepção e com um corpo que anda de outro jeito.

### 3.3 O lado TS do cérebro (P4-7, DECIDIDA)

Para o POC mostrar o cérebro de verdade, o TS precisa do que o `lobos.ts` e o `mundo.ts` ainda não têm:
- as chaves do mundo do cérebro A: o alvo aprendido, as classes por árvore e o paladar;
- o `ModeloMundo` e o lobo `planejamento`;
- as chaves do mundo do J5 no `mundo.ts`.

Cada peça entra com o G-PAR contra os gabaritos do Python, como no porte do A v11 (#343). A G-FRONTEIRA do POC muda: ele passa a
importar o fecho do `mundo.ts` e do `lobos.ts`, além do do `corpo.ts`. O motor e o jogo continuam sem importar o POC.

### 3.4 O que não muda

- o `digilab/engine.py`;
- o cérebro A: os pesos, as regras, o planejador e os números do adendo 9 (o `ganho_gosto` = S/2 e o `g_plano` = S);
- as vidas com as chaves desligadas (o G2), o J5 e os planos dele;
- o POC-01a e o POC-02, com as chaves deles;
- o jogo: a Tela Pet usa a cena do POC desde #373, mas nesta tarefa ela não muda.

## 4. As etapas e os gates

| etapa | o que | gate (falha para a tarefa) | onde |
|---|---|---|---|
| **0, gabaritos** | num commit próprio, antes de tudo: no Python, as vidas do J1 e a fumaça do J5 (os quatro braços) com as chaves desligadas; no TS, os do `mundo.test.ts`, do `lobos_v11.test.ts` e do POC-01a e POC-02 | **G2:** um teste confere os gabaritos byte a byte | `tests/gabaritos/`, `web/app/test/` |
| **1, o contrato no Python** | a seção 3.1 no `mundo.py`, atrás das duas chaves, com testes de resposta conhecida: o cone, a oclusão, o A*, o bloqueio, o contato e o empurrão | G2; **G1** (o replay bit a bit); **G-INT** (nenhum float na física e nos sensores, conferido pela AST); **G-CUSTO** (PROPOSTO, SEM FONTE: o CPU de uma vida de 12 dias com as chaves fica abaixo de 3 vezes o de hoje, que é de 1,09 a 1,10 s com o planejador) | PR `implementacao` |
| **2, a paridade** (a entrada da CP-7) | o mesmo no `mundo.ts`, e os gabaritos do Python com as chaves ligadas | **G-PAR-CONTRATO:** o mesmo log e a mesma semente dão, decisão a decisão e campo a campo, o mesmo estado do mundo, a mesma percepção e o mesmo resultado, com o cérebro de teste dos dois lados, nas sementes dos testes | PR `implementacao` |
| **3, o cérebro no contrato** (Python) | a seção 3.2: o adaptador, os troncos pelo cone e o cérebro A com o planejador nas vidas do J5 com as chaves | G2; G1; a G-RECEPTOR, o G-SEM-DIRECAO, a G-SEM-CREDITO e o congelamento continuam passando; uma fumaça dos braços (P4-5) roda até o fim | PR `implementacao` |
| **4, o plano** | `docs/PLANO_ANALISE_V2_P4_CORPORIFICADO.md` (escrito em 2026-10-21, PROPOSTO): a pergunta da seção 1, os braços (P4-5), as premissas do T1 do J5 (a G-APRENDEU, a G-OPORTUNIDADE e a G-REVAL-POSSIVEL; a G-EXPOSICAO é do T2, que não roda), o contraste, a margem, o N com o poder e as faixas (P4-8) | — (o plano é commitado antes da primeira vida) | PR próprio |
| **5, piloto e validação** | o piloto (as premissas, a margem, o N) e a validação **uma vez**, cada um com o sim do Matheus | os do plano | runs nas faixas da P4-8 |
| **6, o cérebro no POC** (TS) | a seção 3.3, em paralelo às etapas 4 e 5 (não lê resultado): as peças no TS, e o POC desenhando uma vida do motor com o cérebro A e o planejador | **G-PAR-CEREBRO:** o motivo, o estado interno e os modelos, decisão a decisão, contra o Python; a G-FRONTEIRA nova; o G2 do jogo (o v11 sem as chaves sai igual); o e2e do POC | PR `implementacao` |

**Nenhum número se calibra** (P4-6): o cérebro usa os números do adendo 9, e o contrato, os do POC. Se o piloto mostrar que eles não
cabem (uma premissa falha), o plano volta ao Matheus, como no J5.

## 5. Os riscos

| # | risco | o que a tarefa faz |
|---|---|---|
| R-P1 | **O cone tira oportunidades:** com 120°, o pet vê menos, e a G-OPORTUNIDADE do T1 pode voltar a falhar, como na história do J5 (adendos 5 a 8) | o piloto mede, com um descritivo do que o cone escondeu em cada oportunidade perdida. Se a premissa falhar, o plano volta |
| R-P2 | **A paridade bit a bit da oclusão e do A* é cara:** a ordem dos vizinhos e os empates têm de ser os mesmos nos dois lados | o POC já é inteiro (`inteiros.ts`), e o Python porta a mesma ordem. A G-PAR-CONTRATO falha alto, mostrando o primeiro campo que diverge |
| R-P3 | **O custo:** o A* a cada tick deixa a vida lenta no Python | a G-CUSTO na etapa 1, antes do plano, e o N da validação conta com ela |
| R-P4 | **O mapa entra sem ter sido testado:** o P1-plan usa o desfecho e o mapa, e só o desfecho passou (G-T1-DESF) | o P1-plan-desfecho fica como braço (P4-5), e o relato não credita o mapa |
| R-P5 | **O andar muda a dinâmica do J5 além da percepção:** o tempo até chegar, o orçamento do dia, o corte da reexperiência | as duas chaves separadas (3.1). O piloto mostra o efeito de cada uma como descritivo, e o plano diz se alguma vira braço |
| R-P6 | **O escopo cresce:** as paredes, o EXP-1, a tela do jogo e o proprioceptivo pedem para entrar | a seção 6 |
| R-P7 | **A leitura vai além do que o resultado mostra:** um G-T1 corporificado que passa não é "pensar" nem "3D". É o mesmo cérebro com outra percepção, e a vista não muda a ciência (arranjo V) | o relato diz isso, e o rótulo R-7 continua sem valer |
| R-P8 | **Um pet "corporificado" com GPS:** o pet continua sabendo a posição absoluta (W-3), e o mapa do planejador depende dela | fica marcado como acesso privilegiado, e trocar pede uma pergunta própria |

## 6. Fora desta tarefa

- a busca do J5 (o T2, o mapa), que fica com um plano próprio;
- as paredes e os obstáculos (W-4): a chave vem com o contrato, mas fica desligada no plano (P4-4). O EXP-2 é quem as usa;
- o EXP-1 (a bola e o tédio) e o EXP-3, cada um com tarefa e plano próprios, depois da etapa 3;
- o cérebro lendo a Observação nova (o setor, os bigodes e o contato como entradas), a alternativa da P4-2;
- trocar a posição absoluta (W-3);
- o jogo: a Tela Pet e o produto. Levar o planejador ao jogo pede uma decisão própria (o M6; "pesquisa no Python, um DigiBrain na web");
- o crédito por canal (V3-9);
- os dois pets no contrato (J7);
- **a integração completa do pet** (o Gate I, `docs/futuro/gate_integracao_pet.md`, com a GI-1 a GI-5 DECIDIDAS em 2026-10-21 e a tarefa em `docs/TAREFA_V2_GATE_I.md`). A P4 é integração sensório-motora:
  troca a percepção e o andar, com o mesmo cérebro, corpo e protocolo do J5. Um G-T1 corporificado que passe é uma evidência do
  aprendizado com o contrato, mas não fecha o Gate I nem a genética.

## 7. Critérios de aceitação

- **Etapa 0:** o commit dos gabaritos vem antes de qualquer commit de código, e um teste os confere.
- **Etapas 1, 2, 3 e 6:**
  - os testes novos passam (PROPOSTO: `tests/test_mundo_contrato.py`, `web/app/test/mundo_contrato.test.ts` e o
    `web/app/test/poc_mundo3d.test.ts` com a fronteira nova);
  - a suíte inteira passa, com a contagem no corpo do PR;
  - com as chaves desligadas, os gabaritos saem iguais;
  - cada chave e cada número novo têm status e fonte em `digilab/config.py`.
- **Etapa 2:** a G-PAR-CONTRATO passa, e o `mundo_3d.md` registra a CP-7 como cumprida.
- **Etapa 4:** o plano está commitado antes de qualquer vida, e as faixas estão na `FAIXAS_RESERVADAS`.
- **Em toda etapa:** o desvio vai em `docs/registro/AAAA-MM.md` e no índice; o resumo vai no corpo do PR e na seção 9 deste arquivo.

## 8. Precisa do Matheus

**Todas DECIDIDAS pelo Matheus em 2026-10-21, pela recomendação** (pelo Gerente):
- **P4-1:** o contrato vai ao mundo do motor (o `mundo.py` e o `motor/mundo.ts`), com o POC como referência;
- **P4-2:** o cérebro lê o contrato por um adaptador no motor, sem entrada nova;
- **P4-3:** o primeiro experimento é a replicação do T1 do J5 com o contrato (o plano: `docs/PLANO_ANALISE_V2_P4_CORPORIFICADO.md`);
- **P4-4:** as paredes desligadas, e os troncos opacos à visão, sem colisão;
- **P4-5:** os quatro braços do J5, com o G-T1 como primário;
- **P4-6:** nenhum número se recalibra;
- **P4-7:** a etapa 6 (o cérebro no POC) em paralelo às etapas 4 e 5, sem mudar o jogo;
- **P4-8:** as faixas novas, escolhidas pelo plano sem colisão.

Os números novos (os do contrato, a G-CUSTO) continuam PROPOSTOS. A tabela abaixo é a do esboço, como foi levada ao Matheus.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **P4-1** (DECIDIDA) | a rota | **o contrato vai ao mundo do motor** (o `mundo.py` e o `motor/mundo.ts`), com o código do POC como referência (3.1) | portar o mundo do POC para o Python: ficam dois mundos para manter, e o do POC não tem as árvores, as frutas nem o dono do J5. A replicação teria de refazer o mundo do J5 dentro dele |
| **P4-2** (DECIDIDA) | como o cérebro lê o contrato | **por um adaptador no motor:** a `PercepcaoMundo` de hoje, filtrada pelo cone e pela oclusão. O cérebro não ganha entrada (3.2) | o cérebro lendo a Observação nova: pesos novos, calibração nova e duas mudanças de uma vez (a percepção e o cérebro). Um resultado negativo não diria qual das duas falhou |
| **P4-3** (DECIDIDA) | o primeiro experimento | **a replicação do T1 do J5 com o contrato:** a mesma pergunta e o mesmo contraste, num mundo corporificado. O EXP-1 vem depois, com plano próprio | o EXP-1 primeiro: uma pergunta nova num mundo novo, sem resultado anterior para comparar. **Seguir a recomendação muda a letra da seção 7 do `mundo_3d.md`,** que pedia o EXP-1 validado como saída da P4; o EXP-1 continua, só que depois |
| **P4-4** (DECIDIDA) | o que tapa a visão | **as paredes desligadas (W-4); os troncos opacos à visão, sem colisão** (PROPOSTO). Hoje nada é sólido no mundo do J5 (o `mundo.py` não tem colisão), e os troncos são os únicos objetos fixos dele | as paredes ligadas: duas mudanças de uma vez, e o layout do J5 muda. Os troncos transparentes: o cone é a única diferença, e a oclusão não é exercitada |
| **P4-5** (DECIDIDA) | os braços | **os quatro do J5** (P1, P1-plan, P1-plan-desfecho e P1-plan-cong), com o G-T1 como primário e os mesmos secundários | só o P1 e o P1-plan: custa menos, mas sem o G-T1-DESF o desfecho não se separa do mapa, e o mapa entra sem controle (R-P4) |
| **P4-6** (DECIDIDA) | os números | **nenhum se recalibra:** os do adendo 9 no cérebro, e os do POC no contrato, todos PROPOSTOS; o piloto diz se cabem | recalibrar antes: uma rodada a mais, que lê a fase 1 de um mundo novo. Não recalibrar quando o cone muda muito: as premissas falham, e o custo é um piloto |
| **P4-7** (DECIDIDA) | a ordem do TS | **a etapa 6 em paralelo às etapas 4 e 5, só no POC;** o jogo não muda | o TS primeiro: a pesquisa espera a web, e a paridade do cérebro se refaz quando o mundo mudar. Sem o TS: o POC continua com o cérebro de teste, e a CP-7 fica pela metade |
| **P4-8** (DECIDIDA) | as faixas | **pedir ao coordenador duas faixas novas quando o plano existir** (o piloto e a validação). As etapas 0 a 3 usam só as sementes dos testes | usar uma faixa do J5: as unidades já foram vistas, e as faixas do J5 não voltam |

## 9. Resumo da etapa (o esboço, 2026-10-21)

- **O que saiu:** este esboço, todo PROPOSTO.
- **O que o esboço achou:** as três peças da P4 (o contrato, o mundo do J5 e o cérebro com o planejador) moram hoje em lugares
  diferentes, e nenhuma está nos três (seção 0).
- **O que se propõe:**
  - levar o contrato ao mundo do motor, em duas chaves;
  - ligar o cérebro por um adaptador, sem entrada nova;
  - replicar o T1 do J5 no mundo corporificado;
  - portar o cérebro com o planejador para o POC, em paralelo.
- **O que não se fez:** nenhum código mudou, nenhuma vida rodou, e nenhuma faixa foi reservada.

### Etapa 0, os gabaritos (worker D, 2026-10-21)

- **O commit dos gabaritos** (`70ecadf`) vem antes de qualquer código da P4, e dois testes os conferem (o G2).
- **No Python** (`tests/gabarito_p4.py` → `tests/gabaritos/p4_vidas_de_hoje.json`, conferido por `tests/test_p4_gabaritos.py`):
  - o J1 pela bancada: 36 vidas do mundo físico (P0, P0z, P1 e P3, os dois layouts, o comedouro e longe, na montagem simples; o P1 e o
    P3 na completa);
  - o J5 com o adendo 8: os quatro braços, T1 e T2, nas sementes 101 e 202 (16 vidas).
- **No TS** (`web/app/test/p4_etapa0.test.ts` → `web/app/test/gabaritos/p4_etapa0_ts.json`):
  - o sha256 dos gabaritos do Python que o `mundo.test.ts` e o `lobos_v11.test.ts` leem;
  - os hashes do POC-01a (as três sementes do e2e);
  - os do POC-02 (as mesmas sementes, com o corpo ligado, 3000 ticks).
- **Interpretações** em `docs/registro/2026-10.md`.

### Etapa 1, o contrato no Python (worker D, 2026-10-21)

- **As faixas** 61101…61505 (o piloto) e 62101…62505 (a validação) entraram na `FAIXAS_RESERVADAS`, com o plano da P4 como fonte.
- **O código, atrás da `ConfigContrato`** (`digilab/config.py`; desligada por padrão, os números do POC PROPOSTOS e SEM FONTE):
  - `digilab/contrato.py`: o porte do POC em inteiros (o cone, a oclusão, os bigodes, o bloqueio e o deslize, o A\*, o controlador e o
    empurrão da bola);
  - `digilab/mundo.py`: a chave `sensores` monta a `PercepcaoContrato` (a de hoje, filtrada pelo cone e pela oclusão dos troncos, mais
    a `orientacao`); a chave `controlador` anda pelo controlador nos 15 ticks da decisão; as `paredes` ficam desligadas (W-4). O
    registro de cada decisão com alvo vai para `contrato_decisoes`;
  - `digilab/modelo_mundo.py`: com a percepção do contrato, o mapa do planejador vê as árvores pelos troncos do cone.
- **O cérebro não ganha entrada** (P4-2): os campos de hoje, mais a orientação, que nenhum lobo lê.
- **Os gates:**
  - **G2:** os gabaritos da etapa 0 e os do mundo do J5, com a chave explícita desligada, saem iguais;
  - **G1:** o replay das vidas com as chaves (o instinto, o cérebro A e a vida de 12 dias do J5 com o planejador);
  - **G-INT:** nenhum float no `contrato.py`, pela AST;
  - **G-CUSTO:** a razão 2,17 numa vida de 12 dias do P1-plan (`tools/custo_p4_contrato.py`).
- **O achado para o adendo 1:** com a orientação do último deslocamento, o pet chega menos ao alvo (de 69% a 46% das decisões com alvo
  na vida da G-CUSTO) e oscila no alvo do cheiro, chegando de costas para a comida. A regra não mudou.
- **Interpretações** em `docs/registro/2026-10.md`.

### Etapa 2, a paridade Python/TS (worker D, 2026-10-21)

- **O código, no TS, atrás da chave desligada** (o jogo não a liga):
  - `web/app/motor/contrato.ts`: o espelho, função a função, do `digilab/contrato.py`, com a mesma conta inteira, a mesma ordem dos
    vizinhos do A\* e os mesmos empates (o heap de (f, h, índice));
  - `web/app/motor/mundo.ts`: a opção `contrato` do `Mundo`, com a percepção pelo cone e pela oclusão (a `orientacao` na percepção só com
    os sensores), os troncos opacos sem colisão, as paredes (desligadas no plano), o controlador, a orientação e o registro de cada
    decisão com alvo, como no Python.
- **O gabarito:** `experiments/exportar_gabarito_contrato.py` grava `web/app/test/gabaritos/contrato_python.json`, e
  `tests/test_gabarito_contrato_web.py` confere que ele está em dia. Ele traz as contas em casos sorteados (o controlador com muros
  finos, contatos e o pet preso numa caixa) e 7 vidas de 3 dias com as chaves (juntas, separadas e com as paredes), com o instinto, o
  cérebro aleatório, os lobos e um cérebro de teste que explora até a borda.
- **A G-PAR-CONTRATO passa** (`web/app/test/contrato.test.ts`, 18 testes): o mundo em TS rejoga cada vida decisão a decisão (a
  percepção, os candidatos, o ocorrido com o registro do contrato, o estado e a percepção depois), o resumo e os próximos sorteios. A
  falha mostra o primeiro campo que diverge (R-P2); duas mutações de propósito (a borda do cone e o custo da diagonal) a fizeram falhar.
- **O G2 do jogo:** com a chave explícita desligada, as 4 vidas do gabarito do mundo saem iguais; a suíte do TS e a da etapa 0 passam.
- **A CP-7** fica registrada como cumprida no `docs/futuro/mundo_3d.md`.
- **Interpretações** em `docs/registro/2026-10.md`.

## Referências

Nenhuma referência externa: o esboço só usa os documentos do repositório citados no texto e não alega novidade.
