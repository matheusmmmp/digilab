# Plano da segunda rodada de equilíbrio do combate em tempo real (em cima do candidato v14)

Worker: Claude Code, Opus 5.5, worktree `v2-combate-tr`, branch `v2-combate-tr-rodada2`, 2026-10-30. **Aprovado pelo Matheus em 2026-10-30** (no chat da coordenação: as recomendações DR2-1 a DR2-6, seção 5).
Os números novos da rodada seguem PROPOSTOS. Nenhuma luta roda
antes de o Matheus aprovar este plano e de as faixas novas entrarem na `FAIXAS_RESERVADAS` num commit próprio.

**Por quê:** a conferência única da primeira rodada (`docs/EQUILIBRIO_COMBATE_TR.md`, fase 5; os artefatos em
`web/app/scripts/medicoes/equilibrio_tr/fase5/`) deixou 15 metas sem fechar. O Matheus decidiu (2026-10-30, no chat da coordenação) que **a
v14 não é ligada agora** e que se abre uma segunda rodada em cima do candidato v14.

**O que vale da primeira rodada** (`docs/PLANO_EQUILIBRIO_COMBATE_TR.md`):
- **as metas** da seção 2, com a mesma faixa e a mesma fonte. Nenhuma meta muda nesta rodada;
- **o que pode e o que não pode mudar** (seção 4), **o que fica fora** (seção 6) e **as decisões DE-1 a DE-10** (seção 7). Duas delas pesam
  aqui:
  - **a DE-9:** o T-1 fica reprovado como exceção à DE-7, então ele não é meta a fechar;
  - **a DE-3:** o chip coberto só ganha aviso. O I-5 depende de revertê-la (a DR2-1, abaixo).

## 1. O ponto de partida

**O candidato v14:**
- o `RELOGIO_V14`, com o disparo a 6× (DE-9);
- as `LISTAS_V14`;
- a reserva fixa no fim (`GambitsPet.reservaNoFim`, DE-10);
- os `FATORES_V14`.

**Como estavam as metas**, na calibração da primeira rodada e na conferência (`fase4/depois/` e `fase5/`):

| passam | não passam |
|---|---|
| T-3, T-4, T-5, F-3, P-1, P-2, P-4, G-2, G-4, G-5, G-6, I-2 | T-1 (exceção, DE-9), T-2, F-1, F-2, F-4, F-5, F-6, F-7, P-3, G-1, G-3, I-1, I-3, I-4, I-5 |

**A fase 0 desta rodada** mede o ponto de partida nas sementes novas de calibração, sem mudar nada: as mesmas bancadas e opções da
reconferência da fase 4 (`fase4/depois/`). Ela fixa o "antes" de cada fase e a lista das metas já fechadas, que a regra "volta atrás" da
seção 4 protege. Ela vai no PR da fase 1.

## 2. O escopo

São as questões abertas da fase 5, nesta ordem. A ordem segue a dependência: as formas embaixo de tudo, o aprendizado em cima das listas,
os líderes e a Liga em cima das formas, e as cartas por último.

| fase | o quê | as metas | as alavancas (todas do candidato v14, PROPOSTAS, só na bancada até o fim) |
|---|---|---|---|
| **R2-1, as formas** | uma rodada das formas por cima do candidato, como a fase 2 da primeira rodada | F-1, F-2, F-4, F-5, F-6, F-7, T-2 e I-3 (a tita passa de 0,60 já sem item; é o F-1) | as `LISTAS_V14` (a lista de cada forma, com a capacidade e as condições do estágio) e as passivas do tempo real. A base do combate (`CV`, `CV21`, `CSO`) não muda |
| **R2-2, o aprendizado** | uma regra própria do tempo real para a nota-base da semeadura e a ordem pela nota | P-3 (e P-4, que não pode cair) | um bloco novo do candidato, por exemplo `APRENDIZADO_V14` em `combate_tr/constantes_tr.ts`: a nota-base pela posição na semeadura e o peso do resultado na ordem. O `GA` comum, conferido contra o Python, não muda. A DE-10 fica |
| **R2-3, os líderes e a Liga** | as listas dos líderes que reprovam, e os fatores de novo por cima das formas novas | G-1 e I-1 (a Floresta, a Cidadela, o Lago e a Espiral), G-3 (o vigia a 0,94 na conferência); G-2, G-4, G-5, G-6 e P-4 não podem cair | uma lista candidata por líder que reprova (`GAMBITS_ARENA` para o candidato, só nos 4; hoje a Floresta tem lista de arena, e a Cidadela, o Lago e a Espiral usam o estilo `v2c` do NPC) e os `FATORES_V14` |
| **R2-4, as cartas** | o efeito com número da carta de Foco e o Fôlego | I-4 | o Foco ganha um efeito com número, ajustável (DR2-4); o Fôlego, o valor dele e o teto do guts no começo da luta. Os valores entram como cartas candidatas (`--cartas` da bancada), e o `CIT` dos pets v13 não muda |
| **R2-5, a conferência única** | todas as metas, uma vez, nas sementes de conferência novas | todas | nenhuma: nada se ajusta olhando para ela |

**Fica fora:**
- **a alavanca de estrutura das formas de longe e do tita** (o alcance ou o tempo do disparo contra quem avança, a pele dura do tita):
  decidida pelo Matheus em 2026-10-30, depois da R2-1, pela recomendação do worker. Vai para depois da conferência e não entra nesta
  rodada;
- **a troca de regra que escolhe a candidata pelo resultado** (em vez de sortear; o P-3 do Ultimate): decidida pelo Matheus em
  2026-10-30, depois da R2-2, pela recomendação do worker. Vai para depois da conferência, junto com a alavanca de estrutura;
- **o I-5** entra pela DR2-1 (DECIDIDA) como fase R2-4b, depois das cartas e antes da conferência: o chip antes da primeira regra com a
  mesma condição, só no candidato v14;
- **ligar a v14 no jogo** (a DE-1), que é o passo seguinte, com o ok do Matheus;
- tudo o que a seção 6 do plano da primeira rodada deixa fora.

## 3. As sementes (proposta; reservadas num commit próprio, antes da primeira luta)

A conferência da primeira rodada (`70101…70505`) já foi usada uma vez e não volta como conferência. A calibração dela (`68101…68505`) fica
para a reprodução da primeira rodada.

| uso | faixa proposta | estado hoje (`experiments/bancada/faixas.py`) |
|---|---|---|
| calibração da segunda rodada (fases R2-0 a R2-4) | `72101…72505` (as bases 72101, 72202, 72303, 72404, 72505; 20 sementes por base, `hashSemente("equilibrio-tr", base, k)`) | livre: nem em `FAIXAS_RESERVADAS` nem em `FAIXAS_QUEIMADAS` |
| conferência da segunda rodada (fase R2-5) | `74101…74505` | livre |

- **As duas entram na `FAIXAS_RESERVADAS`** com a fonte ("equilíbrio do combate em tempo real, segunda rodada: calibração" e "…:
  conferência"), num commit próprio, depois da aprovação deste plano e antes da primeira luta.
- **Elas são pedidas ao coordenador,** como manda a regra das faixas.
- **As bancadas** ganham as faixas novas no mapa `FAIXAS` delas (`calibracao2`, `conferencia2`) no mesmo commit.
- **As sementes 101…505** seguem só nos testes.

## 4. O método e o critério de parada (como na primeira rodada)

- **As lutas e as bancadas:**
  - CPU contra CPU, com semente, pelo motor do jogo, sem tela;
  - as bancadas de `web/app/scripts/equilibrio_tr/` (fases 1 a 4), com as alavancas novas como opções de linha de comando e o candidato
    por padrão;
  - os artefatos em `web/app/scripts/medicoes/equilibrio_tr/r2_<fase>/`, em JSON, com o commit, as sementes e o candidato;
  - nenhum número sem o JSON que o produz.
- **No máximo 4 processos ao mesmo tempo.**
- **Um PR por fase.** O worker para depois de cada PR; o merge é do Matheus.
- **A regra de parada de cada fase:** ela para quando as metas dela passam ou depois de **3 rodadas de ajuste**. A meta que não fecha é
  relatada com o melhor valor e o porquê.
- **Em qualquer fase:**
  - um ajuste que reprova uma meta já fechada (a lista da fase R2-0, ou uma que a própria rodada fechou) **volta atrás**;
  - um teste de replay ou de determinismo que quebre para tudo.
- **A regra de escolha** (a da fase 4): um número muda só quando a meta dele não passa e algum valor da grade a faz passar. Entre os que
  passam, fica o de maior folga.
- **Os pets v13 não mudam.** Toda alavanca nova é do candidato v14, atrás de uma chave ou de uma tabela da bancada. O gabarito das vidas
  v13 confere igual em cada PR.
- **Os relatos e os desvios:**
  - o relatório de cada fase vai numa seção nova de `docs/EQUILIBRIO_COMBATE_TR.md` ("Rodada 2, fase …");
  - os desvios vão em `docs/registro/2026-10.md` (ou no mês da data), com a linha no índice.
- **A conferência única (R2-5)** roda uma vez, no fim, nas sementes `74101…74505`. Nenhum número muda por causa dela; o que reprovar é
  relatado, e o Matheus decide.

## 5. As decisões (DECIDIDAS pelo Matheus em 2026-10-30, todas pela recomendação; o custo de errar fica registrado)

| # | a pergunta | a recomendação | o custo de errar |
|---|---|---|---|
| **DR2-1** (DECIDIDA, 2026-10-30, pela recomendação; I-5; reverte a DE-3) | o chip de regra entra antes da primeira regra da lista com a mesma condição, em vez de no fim? | **sim, só no candidato v14**. Hoje o chip quase nunca dispara (de 0 a 0,0975 das lutas na conferência), porque entra no fim e a primeira regra que vale decide. O I-3 (o item não desequilibra a forma) e o I-1 vigiam o efeito. Entra como fase R2-4b | com a mudança, todo pet com chip luta diferente, e um chip forte pode passar o I-3; a regra encoberta deixa de decidir. Sem ela, os chips de regra seguem quase cosméticos, e o I-5 fica reprovado |
| **DR2-2** (DECIDIDA, 2026-10-30, pela recomendação; as sementes) | reservar `72101…72505` para a calibração e `74101…74505` para a conferência? | **sim**: as duas estão livres, e a conferência da primeira rodada já foi usada | uma faixa errada (já usada por outra frente) mistura resultados; a conferência repetida deixa de ser uma validação |
| **DR2-3** (DECIDIDA, 2026-10-30, pela recomendação; a ordem das fases) | as formas antes do aprendizado e dos líderes? | **sim**: as listas das formas mudam o que o pet aprende e contra quem os líderes são medidos | na ordem inversa, os líderes e o aprendizado seriam calibrados em cima de formas que ainda vão mudar, e a regra "volta atrás" reprovaria o trabalho anterior |
| **DR2-4** (DECIDIDA, 2026-10-30, pela recomendação; o efeito da Foco) | a Foco hoje zera a exploração (`eps` 0), o que muda pouco (de 0,013 a 0,014 contra o líder). Que efeito com número ela ganha no candidato? | **uma fração do ritmo das decisões do pet na luta** (decide mais rápido; o número calibrado na R2-4), mantendo o `eps` 0. É o efeito mais próximo de "o pet não se distrai" no tempo real | um efeito de ritmo forte demais quebra o P-1 com itens (o I-2) e o T-1; um número fraco não fecha o I-4. A outra opção (o guts ou a cura) repete as outras duas cartas |
| **DR2-5** (DECIDIDA, 2026-10-30, pela recomendação; o aprendizado próprio do tempo real) | a regra nova do aprendizado (a R2-2) entra como um bloco próprio do candidato, sem mexer no `GA`? | **sim**: o `GA` é conferido contra o Python (`constantes.test.mjs`), e o tempo real não existe no Python | mais um conjunto de números do tempo real sem a pesquisa por trás; se o P-3 só fecha mexendo na base comum, ele fica reprovado nesta rodada |
| **DR2-6** (DECIDIDA, 2026-10-30, pela recomendação; o T-2) | o T-2 (o pior par no limite: 0,52 na conferência) entra como meta a fechar na R2-1, ou fica como a T-1, uma exceção da DE-9? | **entra na R2-1**: o pior par é um espelho (o vigia contra o vigia) que as listas das formas podem resolver | se ficar como exceção, a luta sem fim do espelho do vigia continua; se entrar e não fechar, é só mais uma meta relatada |

## 6. A entrega de cada fase

- **R2-0 e R2-1 (um PR):**
  - o commit das faixas;
  - o ponto de partida nas sementes novas;
  - a rodada das formas.
- **R2-2, R2-3 e R2-4:** um PR cada.
- **R2-4b**, se a DR2-1 for aprovada: um PR.
- **R2-5:** um PR, com a tabela de todas as metas na calibração e na conferência e a lista do que não fechou.
