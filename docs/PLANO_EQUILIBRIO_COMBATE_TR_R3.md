# Plano da terceira rodada de equilíbrio do combate em tempo real (em cima da luta v18)

Worker: Claude Code, Opus 5.5, worktree `D:\Trab\digilab\v3-luta-equilibrio-r3`, branch `v3-luta-equilibrio-r3`, 2026-11-07.
**Status: PROPOSTO.** As decisões D-R3-1 a D-R3-9 (seção 6) ficam com o Matheus, e os números novos da rodada seguem PROPOSTOS até ele
decidir. **Nenhuma luta roda** antes de o Matheus aprovar este plano e de as faixas novas entrarem na `FAIXAS_RESERVADAS` num commit
próprio.

**A autorização:** em 2026-11-07, o Matheus perguntado "Começo o I1 da individualidade e o plano da rodada 3 da luta?" respondeu "Sim, os
dois" (repassado pela sessão que coordena). Isso libera este plano, no papel, e nada além dele.

**Por quê agora:**
- **A conferência da rodada 2** (R2-5, #502; `docs/EQUILIBRIO_COMBATE_TR.md`) deixou 14 das 27 metas sem fechar, e o Matheus ligou a
  v14 mesmo assim (B2, 2026-10-30; `docs/TAREFA_V3_COMBATE_V14.md`), contra a recomendação de esperar uma rodada 3.
- **Depois disso, as mecânicas da luta fecharam:**
  - a ponte com o cérebro (PE0 a PE4; `docs/TAREFA_V3_PONTE_LUTA.md`);
  - o empurrão de verdade, a v18 (#661; `docs/TAREFA_V3_LUTA_EMPURRAO.md`);
  - os efeitos visuais E1 a E5 (#690; `docs/TAREFA_V3_LUTA_EFEITOS.md`);
  - o "levar pet", a v19 (`docs/TAREFA_V3_PEGAR_PET.md`), que luta como a v18.
- **A regra do projeto:** equilibrar só no fim das mecânicas. Esta é a rodada do combate.

**O que vale das rodadas 1 e 2** (`docs/PLANO_EQUILIBRIO_COMBATE_TR.md` e `docs/PLANO_EQUILIBRIO_COMBATE_TR_R2.md`):
- **as 27 metas** da seção 2 da primeira rodada, com a mesma faixa e a mesma fonte, salvo o que a D-R3-1 mudar;
- **o que pode e o que não pode mudar** (seção 4 da primeira), **o que fica fora** (seção 6) e as decisões **DE-1 a DE-10** e **DR2-1 a
  DR2-6**. Pesam aqui:
  - a **DE-9**, a exceção do T-1;
  - a **DE-10**, a reserva fixa no fim;
  - a **DR2-1**, o chip antes da regra que o cobre;
  - a **DR2-5**, o aprendizado como um bloco próprio do tempo real, sem mexer no `GA`;
- **o método e o critério de parada** da rodada 2 (seção 4 dela), repetidos na seção 4 abaixo.

## 1. O ponto de partida: a luta de um ovo novo hoje

**A luta que um ovo novo luta hoje é a da v18.** Lido na `main` em 2026-11-07:

| versão | a luta | de onde |
|---|---|---|
| v14 | o candidato inteiro da R2-5: o `RELOGIO_V14` (disparo a 6×), as `LISTAS_V14`, a reserva fixa, o `APRENDIZADO_V14`, as `LISTAS_LIDER_V14`, os `FATORES_V14`, as `CARTAS_V14` vazias e o chip antes da regra (`CHIP_ANTES_V14`) | `docs/TAREFA_V3_COMBATE_V14.md`, seção 9 |
| v15, v17 | a da v14 (a bola no golpe; o cérebro trocável) | `web/app/motor/constantes.ts`, o comentário do `VERSAO_PET` |
| **v18** | **a da v14 mais o empurrão de quem leva o golpe** (`RELOGIO_V18` = `RELOGIO_V14` com o `EMPURRAO_V18`): a investida 20 px e derruba, o pesado 60 px e derruba, a queda de 62 passos, o deslize de 10 passos, a pele dura corta pela metade (`guarda` 0,5), a defesa e o contra-golpe não são empurrados (`defesa` 0) | `web/app/motor/combate_tr/constantes_tr.ts`; a medição A, aceita pelo Matheus em 2026-11-07 (`docs/TAREFA_V3_LUTA_EMPURRAO.md`, seção 9.7) |
| **v19** | **a da v18** (`CV21E_TR18`); o "levar pet" não toca a luta | `docs/TAREFA_V3_PEGAR_PET.md`, seção da P1 |

**O que mudou desde a R2-5 e não muda a luta:**
- **os efeitos E1 a E5** são só da vista (`web/app/src/telas/lutar/palcoTR/`). Cada etapa conferiu que `git diff origin/main -- web/app/motor
  digilab` sai vazio. Nenhuma meta muda por eles, exceto talvez o tempo de tela do T-3 (a D-R3-6);
- **a ponte, PE3 e PE4:** a dor da luta e o episódio `luta` chegam ao corpo e ao M-MEM, e o ε da luta passa a sair do `g_exp` nos pets
  v16 e v17 em diante com a marca `"pl"` e o modular ativo. **A bancada da luta não roda o modular** (PL-8): ela luta com o perfil canônico
  e o ε de hoje, que é o ε da ponte com `g_exp = e0` (T-PL-4). A rodada mede a luta do `GambitsPet`, não o pet com o cérebro (a D-R3-4).

**Como estão as metas na luta v18:** a medição A do empurrão, na calibração da rodada 2 (`72101…72505`), com o comando da conferência e
a opção `--empurrao v18` (`web/app/scripts/medicoes/equilibrio_tr/empurrao/resumo_r_a_inv20.txt`; os JSON em `empurrao/r_a_inv20/`):
- **passam 12:** T-3, T-4, T-5, F-3, P-1, P-2, P-4, G-3, G-4, G-5, G-6 e I-2;
- **falham 15:** T-1 (a exceção da DE-9), T-2, F-1, F-2, F-4, F-5, F-6, F-7, P-3, G-1, G-2, I-1, I-3, I-4 e I-5.

**Diferença contra a R2-5:** o G-2 passou a falhar. O Tortomon contra os pets sem treino dá 0,31, para um teto de 0,30. O Matheus aceitou
esse valor em 2026-11-07, e ele vem para esta rodada.

**A medição A não é uma conferência:** ela rodou nas sementes em que o empurrão foi escolhido, e nenhuma validação da v18 rodou
(`docs/TAREFA_V3_LUTA_EMPURRAO.md`, seção 9.7).

## 2. As 27 metas: o estado e o que mudou

**As colunas da tabela:**
- a **R2-5** é a conferência da v14 (`74101…74505`; `docs/EQUILIBRIO_COMBATE_TR.md`, R2-5);
- a **v18** é a medição A, nas sementes de calibração (`72101…72505`; `empurrao/resumo_r_a_inv20.txt`);
- o **"na R3"** é a proposta desta rodada (seção 3):
  - **protegida** quer dizer que a meta passa e não pode cair (a regra "volta atrás");
  - **exceção** quer dizer que a meta fica relatada, sem ser meta a fechar.

As metas, as faixas e as fontes são as da seção 2 da primeira rodada.

| # | a meta (curta) | R2-5 (v14, conferência) | v18 (calibração) | o que mudou desde a R2 | na R3 |
|---|---|---|---|---|---|
| **T-1** | a luta média de 40 a 60 s | não: 34,0 s; mediana 32,2 s | não: 35,1 s; 35,0 s | o empurrão alonga um pouco a luta | **exceção** (DE-9), relatada |
| **T-2** | no limite de 80 s, ≤ 5% em cada confronto | não: total 0,013; pior par 0,175 | não: 0,014; pior par 0,135 (duelista × sentinela) | o pior par trocou; o duelista × muralha, que o empurrão levava a 0,93, voltou com a defesa e o contra-golpe sem empurrão | R3-1 |
| **T-3** | a Cidadela cabe em 3 min de tela no p90 | sim: 60,3 s | sim: 64,1 s | o empurrão alonga a série; os efeitos põem tempo de tela que a bancada não conta (a D-R3-6) | protegida |
| **T-4** | o lado A vence de 0,45 a 0,55 no espelho | sim: 0,509 | sim: 0,50 | — | protegida |
| **T-5** | a regra "rival preparando" decide ≥ 50% | sim: 0,707 | sim: 0,681 | cai um pouco com o empurrão | protegida |
| **F-1** | as 8 formas adultas de 0,40 a 0,60 | não: 3 fora (espelho 0,373, muralha 0,638, tita 0,677) | não: 4 fora (duelista 0,332, espelho 0,362, emboscador 0,39, tita 0,86) | **o tita sobe para 0,86:** a pele dura segura a queda e corta o empurrão pela metade. O duelista cai | R3-1 |
| **F-2** | da mais forte à mais fraca, ≤ 0,20 | não: 0,304 | não: 0,528 | piora muito, pelo tita | R3-1 |
| **F-3** | toda forma vence ≥ 2 das outras 7 | sim | sim, com folga mínima: o duelista vence 2 (o emboscador 0,74, o vigia 0,723) | era 3 na v14; foi a meta da rodada curta do empurrão | protegida (a mais frágil) |
| **F-4** | as linhas do Rookie e do Champion de 0,40 a 0,60 | não: o caçador 0,694; o Rookie 0,548 | não: o caçador 0,705, o brigão 0,387, o guardião 0,381; o Rookie 0,495 | o brigão e o guardião saem da faixa por baixo | R3-1 |
| **F-5** | de longe × de perto de 0,45 a 0,55 | não: Champion 0,559; Ultimate 0,261 | não: 0,589; 0,238 | o Champion se afasta mais da faixa | R3-1 |
| **F-6** | nenhuma passiva muda a força em mais de 0,10 | não: espelho 0,12, sentinela 0,13, tita 0,105 | não: espelho 0,115, sentinela 0,129, tita 0,181 | a pele dura do tita pesa mais com o empurrão | R3-1 |
| **F-7** | cada sombria de 0,45 a 0,65 | não: o bastião 0,658 | não: o predador 0,652, o colosso partido 0,662 (o bastião 0,649, dentro) | a falha mudou de forma | R3-1 |
| **P-1** | estágio vizinho ≤ 0,10; dois acima, 0 | sim | sim | — | protegida |
| **P-2** | o pet típico vence o sem treino ≥ 0,80 | sim | sim | — | protegida |
| **P-3** | a lista aprendida vence a semente de 0,55 a 0,70 | não: Champion 0,647; Ultimate 0,493 | não: 0,6669; 0,4803 | — | R3-2 |
| **P-4** | ≥ 80% dos pets chegam a 0,8 no sparring | sim: 0,85; 0,9513 | sim: 0,9125; 0,9713 | o achado D-LAB-CEN-3 (2026-11-07): nos Cenários do Laboratório, os pets v19 param no Champion (a questão aberta 2) | protegida |
| **G-1** | os 6 líderes: sem ≤ 0,05; com ≥ 0,80; a pior ≥ 0,50 | não: fora a Cidadela, o Lago e a Espiral | não: fora a Cidadela (com 0,73; a pior, a sentinela, 0,28), o Lago (sem 0,0738; a pior 0,44) e a Espiral (sem 0,0575; a pior 0,43) | igual na essência | R3-1 e R3-3 |
| **G-2** | os desafiantes: sem ≤ 0,30; com ≥ 0,80; a pior ≥ 0,50 | sim | **não:** o Tortomon (`npc_tier2_sentinela`) sem treino 0,31 | **o empurrão:** o brigão e o colosso sem treino vencem mais quem recua. O Matheus aceitou o 0,31 em 2026-11-07, e o valor vem para esta rodada | R3-3 |
| **G-3** | a Liga: toda forma ≥ 0,25 e nenhuma > 0,85 | sim: de 0,51 a 0,71 | sim: de 0,40 a 0,81 | a faixa se abre para os dois lados | protegida |
| **G-4** | a Torre e o Palácio: melhor ≥ 0,70, pior ≥ 0,40 | sim: 1,00 e 0,73 | sim: 1,00 e 0,74 | — | protegida |
| **G-5** | a Fábrica: uma série em ≥ 0,25 | sim: 0,37 | sim: 0,35 | — | protegida |
| **G-6** | o Salão, cada nível de 0,70 a 0,95 | sim: de 0,8525 a 0,95 (o Rookie no limite) | sim: de 0,7975 (adolescente) a 0,91 (criança) | a ponta de cima sai do limite | protegida |
| **I-1** | sem treino com os melhores itens × cada líder ≤ 0,05 | não: 0,0625 | não: 0,0738 | é o sem treino do Lago | R3-1 e R3-3 |
| **I-2** | com os melhores itens, o P-1 continua | sim | sim | — | protegida |
| **I-3** | com o melhor item, cada forma ≤ 0,60 | não: 0,7332 | não: 0,7782 | é o tita do F-1 (passa de 0,60 sem item) | R3-1 |
| **I-4** | cada carta muda a taxa contra o líder em ≥ 0,03 | não: a Foco 0,022; o Fôlego 0,018 | não: a Foco 0,0098, o Fôlego 0,01 (a Cura 0,0521 passa) | — | R3-4 (a D-R3-1) |
| **I-5** | cada chip de regra dispara em ≥ 1 de 2 lutas | não: de 0,0075 a 0,3875 | não: o Aparo 0,0775, o Oportunista 0,25, o Recuo 0,31, o Perseguidor 0,3537 | — | R3-4 |

**O que se lê da tabela, sem medição nova:**
- o empurrão ajudou o tita. Com a pele dura, ele leva metade do empurrão e não cai: o F-1, o F-2, o F-6 e o I-3 pioram por ele;
- o empurrão também ajudou o pet sem treino contra quem recua (o G-2 do Tortomon);
- as de longe e a sentinela seguem onde a rodada 2 as deixou: a alavanca de estrutura que o Matheus mandou para depois da conferência
  (2026-10-30) é o centro desta rodada.

A conta "29 metas" do plano da medição do empurrão (`docs/TAREFA_V3_LUTA_EMPURRAO.md`, seção 4.1) é um engano de contagem: a lista dele
tem as mesmas 27 (5 T, 7 F, 4 P, 6 G e 5 I), e o `resumo_metas.py` lê 27. O registro guarda isso (D-R3P-4).

## 3. As fases

A ordem segue a da rodada 2 (DR2-3): as formas embaixo de tudo, o aprendizado em cima das listas, os líderes e a Liga em cima das formas, e
as cartas e os chips por último.

| fase | o quê | as metas | as alavancas (todas PROPOSTAS, de um candidato próprio da rodada, só na bancada até o fim; a D-R3-2) |
|---|---|---|---|
| **R3-0, o ponto de partida** | a luta v18 medida nas sementes novas de calibração, sem mudar nada. Antes, a mesma medida em `72101…72505`, conferida campo a campo contra `empurrao/r_a_inv20/` (a prova de que a `main` de hoje, com os efeitos, a v19 e a ponte, luta como a medição A) | todas | nenhuma |
| **R3-1, a alavanca de estrutura** | as formas de longe e o tita. A sentinela contra quem persegue é a mesma questão nos líderes da Cidadela, do Lago e da Espiral, e o G-1 e o I-1 desses três são lidos junto | F-1, F-2, F-5, F-6, T-2, I-3; F-4 e F-7 pelas listas; o G-1 e o I-1 dos três líderes lidos ao lado | o disparo contra quem fecha a distância (o alcance ou o tempo dele) e a pele dura do tita, com o `guarda` do empurrão (a D-R3-7). Num segundo passo, as `LISTAS_V14` do caçador, do brigão, do guardião e das sombrias |
| **R3-2, o aprendizado** | a troca de regra escolhida pelo resultado, em vez de sorteada | P-3 (o Ultimate); o P-4 não pode cair | um bloco do candidato ao lado do `APRENDIZADO_V14` (a D-R3-8). O `GA` comum não muda (DR2-5) |
| **R3-3, os líderes, os desafiantes e a Liga** | as listas e os fatores do que a R3-1 não fechar, mais o Tortomon | G-1, I-1, G-2 (o Tortomon); o G-3 protegido | as `LISTAS_LIDER_V14` e os `FATORES_V14` (a lista do NPC e o `CESC_V9.fatorNpc` do Tortomon) |
| **R3-4, as cartas e os chips** | o chip que nenhuma regra cobre vai para o topo da lista. As cartas são medidas de novo depois das formas e dos líderes novos | I-5; I-4 (a D-R3-1); o I-2 e o I-3 vigiam | o chip no topo (só no candidato) e as `CARTAS_V14` com os efeitos `ritmo` e `gutsTeto` da R2-4 |
| **R3-5, a conferência única** | todas as metas, uma vez, nas sementes novas de conferência | todas | nenhuma: nada se ajusta olhando para ela |

**A R3-0 também fixa a lista das metas protegidas.** É a lista que passa nela: hoje, as 12 da seção 1. Se o G-2 passar nas sementes novas,
ele entra na lista. A regra "volta atrás" (seção 4) protege essa lista.

**A R3-1 vem antes de tudo por três motivos:**
- as listas das formas não fecharam as de longe nem o tita na rodada 2 (R2-1);
- os três líderes que reprovam reprovam pela sentinela (R2-3);
- o empurrão piorou o tita.

Mexer nos líderes ou nas cartas antes dela seria calibrar em cima de formas que ainda vão mudar.

## 4. O método e o critério de parada (os da rodada 2)

**As lutas e as bancadas:**
- CPU contra CPU, com semente, pelo motor do jogo e sem tela;
- as bancadas de `web/app/scripts/equilibrio_tr/` (fases 1 a 4, `medir_tudo.py` e `resumo_metas.py`), com a opção `--empurrao v18` em
  todas as medidas, porque o ponto de partida é a v18;
- as alavancas novas entram como opções de linha de comando, por cima da v18;
- os artefatos vão em `web/app/scripts/medicoes/equilibrio_tr/r3_<fase>/`, em JSON, com o commit, as sementes e o candidato;
- **nenhum número sem o JSON que o produz.**

**Um PR por fase.** O worker para depois de cada PR, e o merge é do Matheus.

**A regra de parada de cada fase:** a fase para quando as metas dela passam ou depois de **3 rodadas de ajuste**. A meta que não fecha é
relatada com o melhor valor e o porquê.

**Em qualquer fase:**
- um ajuste que reprova uma meta protegida (a lista da R3-0, ou uma que a própria rodada fechou) **volta atrás**;
- um teste de replay ou de determinismo que quebre **para tudo** até o conserto (`CLAUDE.md`).

**A regra de escolha** (a da fase 4 da primeira rodada): um número muda só quando a meta dele não passa e algum valor da grade a faz passar.
Entre os que passam, fica o de maior folga.

**Os pets que já existem não mudam:**
- as vidas v13 a v19 e os gabaritos delas conferem iguais em cada PR;
- toda alavanca nova é do candidato da rodada, atrás de uma chave ou de uma tabela da bancada (a D-R3-2);
- o `RELOGIO_V18`, o `EMPURRAO_V18` e as listas, os fatores e as cartas da v14 que a v18 usa não mudam no motor.

**Os relatos e os desvios:**
- o relatório de cada fase vai numa seção nova de `docs/EQUILIBRIO_COMBATE_TR.md` ("Rodada 3, fase …");
- os desvios vão no fim de `docs/registro/2026-11.md` (ou no mês da data), e o índice sai de `tools/gerar_indice_desvios.py`.

**A conferência única (R3-5):**
- roda uma vez, no fim, nas sementes de conferência da rodada 3;
- nenhum número muda por causa dela: o que reprovar é relatado, e o Matheus decide;
- ligar o candidato no jogo é uma tarefa própria depois dela (a D-R3-2).

### 4.1 As sementes (PROPOSTA; reservadas num commit próprio, depois da aprovação e antes da primeira luta)

As faixas das rodadas anteriores:
- **as da primeira** (`68101…68505` e `70101…70505`) ficam para a reprodução dela;
- **a conferência da segunda** (`74101…74505`) já rodou uma vez e não volta como conferência;
- **a calibração da segunda** (`72101…72505`) já serviu a 7 medidas depois da R2-5 (o "antes" e 6 variantes do empurrão, as medições 4.1 a 4.4 da
  `docs/TAREFA_V3_LUTA_EMPURRAO.md`), e o empurrão foi escolhido nela. Nesta rodada, ela só serve à prova de reprodução da R3-0.

| uso | faixa PROPOSTA | o estado hoje (`experiments/bancada/faixas.py`, `origin/main` 9b5409f6) |
|---|---|---|
| a calibração da rodada 3 (R3-0 a R3-4) | **`83101…83505`**: as bases 83101, 83202, 83303, 83404 e 83505, com 20 sementes por base (`hashSemente("equilibrio-tr", base, k)`, como as outras faixas da bancada) | livre: fora da `FAIXAS_RESERVADAS` e da `FAIXAS_QUEIMADAS`. A vizinha mais perto é a `80001…82004` (linhagem E1) |
| a conferência da rodada 3 (R3-5) | **`84101…84505`** | livre, também fora das duas tabelas |

Conferido também em 2026-11-07: nenhum branch remoto e nenhum PR aberto acrescenta uma faixa ao `faixas.py`. Nenhum documento cita
`83101` ou `84101`.

**Como elas entram:**
- **na `FAIXAS_RESERVADAS`**, com a fonte: "equilibrio do combate em tempo real (jogo web), terceira rodada: a calibracao
  (docs/PLANO_EQUILIBRIO_COMBATE_TR_R3.md, secao 4.1; D-R3-5…)", e "…: a conferencia, a validacao unica (…; roda uma vez, nao volta)";
- **num commit próprio**, depois da aprovação, como na DE-6 e na DR2-2, e **pedidas ao coordenador**, como manda a regra das faixas;
- **no mesmo commit**, os mapas `FAIXAS` das quatro bancadas (`fase1_relogio.ts`, `fase2_formas.ts`, `fase3_estagio.ts` e
  `fase4_progressao.ts`) ganham `calibracao3: 83101` e `conferencia3: 84101`.

**As sementes 101…505 seguem só nos testes.**

**Por que não entram neste PR:**
- este PR é só de documento, como o do plano da rodada 2 (#474);
- uma faixa só se reserva com o plano aprovado;
- o `verificar_relato.py` da categoria documentação recusa uma mudança fora de `docs/`.

### 4.2 A carga na máquina

**Uma medida inteira** é `python scripts/equilibrio_tr/medir_tudo.py --faixa calibracao3 --empurrao v18 --saida
scripts/medicoes/equilibrio_tr/r3_<fase>/…`, rodada em `web/app`:
- ela roda as 15 bancadas em 4 processos (`ThreadPoolExecutor(4)`);
- leva cerca de 7 min, a duração da medição A do empurrão (`docs/TAREFA_V3_LUTA_EMPURRAO.md`, seção 9.1);
- as grades (`grade_*_r2.py` e as novas desta rodada) também usam 4 processos.

**Uma de cada vez**, pela V3-D8: no máximo 4 processos e uma carga de pesquisa por vez. As medições do combate contam como carga.

**O gate antes de cada uma:**
- o hook H10 (`.claude/hooks/h10_pre_run.py`) acha o `scripts/equilibrio_tr/*.py` no comando e chama o
  `python tools/pre_run.py <script> --medicao`;
- o `pre_run.py` recusa se houver outra run de pesquisa ou outra medição do combate em andamento (a regra 4 dele);
- ele não confere a faixa de uma medição, porque a bancada recebe a faixa por nome. Por isso a faixa entra nos mapas `FAIXAS` no mesmo
  commit da `FAIXAS_RESERVADAS` (4.1), e a bancada falha alto com um nome fora do mapa.

**Antes de cada medida, o PR da fase registra:** o comando, as metas, as sementes e o tempo estimado.

**O custo estimado da rodada, SEM FONTE além da medição A:**
- cada medida de todas as metas leva ~7 min;
- uma rodada de grade de 10 a 20 pontos leva de 30 min a 2 h e meia, pelo tamanho das grades da rodada 2;
- até 3 rodadas por fase, em 4 fases de ajuste, mais a R3-0 e a R3-5: **de 4 a 30 h de máquina**, em cargas separadas.

## 5. O que fica fora, com o motivo

| o quê | por que fica fora | onde vai |
|---|---|---|
| **a ração que o bebê não come** (o pet só come abaixo de 0,45, e a fome do bebê fica acima; `docs/registro/2026-10.md`, PRODUTO_FOME, #450) | é o cuidado e o corpo, não a luta. Nenhuma bancada da luta passa por ela | a rodada de equilíbrio geral do fim, a do jogo inteiro (`docs/FECHAMENTO_V2.md`, PRODUTO_FOME) |
| **o limiar e o raio do vagar** (o `urgencia_lambda` e o raio; `docs/RESULTADO_V3_ACOES_NOVAS.md`, seção 8, opção (a)) | são do cérebro e do mundo, não da luta | a mesma rodada geral do fim |
| **os números visuais da luta** (`IMPACTO`, `VOO`, `ELEMENTO_SEM_LINHAGEM`, `CHAO`, `POSTURA`, `BARRA`, `NOCAUTE`, `CAMERA` e `PAUSA_FIM_KO`; PROPOSTOS, SEM FONTE) | não mudam nenhuma luta, e a bancada mede o motor sem tela. Eles se calibram olhando as capturas e jogando, não com sementes | a "rodada de equilíbrio visual" que a `docs/TAREFA_V3_LUTA_EFEITOS.md` (seção 13) deixou para depois (a D-R3-9). A única ponte com esta rodada é o tempo de tela do T-3 (a D-R3-6) |
| **a PE5, a lembrança do rival na luta** (PL-6) | é uma mecânica do cérebro, e a bancada da luta não roda o modular (PL-8) | depois da conferência, com papel próprio (a D-R3-3) |
| **o pet com o cérebro na bancada** (o ε pelo `g_exp` da PE4, a dor da PE3) | medir se o pet luta melhor com a ponte pede plano e faixa próprios (PL-8) | fora (a D-R3-4) |
| **mudar o empurrão de ida** (a força da investida e do pesado, a queda, o deslize; EMP-1, EMP-2, EMP-6) | o Matheus o decidiu e escolheu a medição A em 2026-11-07, depois de 6 variantes medidas. A rodada parte dele | fica; só o `guarda` da pele dura entra como alavanca, se a D-R3-7 aceitar |
| **ligar o candidato no jogo** | a regra "uma versão por mecânica": é uma versão nova de pet e uma tarefa própria, como a COMBATE_V14 | depois da R3-5, com o ok do Matheus (a D-R3-2) |
| **o Python da pesquisa** e o `digilab/engine.py` | o tempo real não existe no Python, e o `engine.py` não muda (`CLAUDE.md`) | — |
| **a base do combate** (`CV`, `CV21`, `CSO`), o `GA` comum e as chaves da V21E | são conferidos contra o Python (`constantes.test.mjs`) | — |
| **as regras de ambiente das arenas do UP, os clipes do UP e a B3** | os mesmos motivos da seção 6 da primeira rodada | — |

**O lugar desta rodada no equilíbrio geral:**
- **a rodada de equilíbrio geral de 2026-09-30** (`docs/PLANO_EQUILIBRIO_GERAL.md` e `docs/EQUILIBRIO_GERAL.md`) foi a do combate por
  turnos, nos pets v9. As metas do tempo real são a extensão dela: o F-1 é o M-A1, o G-1 é o M-B2, e assim por diante (a coluna "fonte" da
  primeira rodada);
- **esta rodada é a parte do combate** da rodada de equilíbrio do fim;
- **o cuidado, o corpo, o vagar e a vista** são as outras partes dela e ficam para a rodada geral do jogo inteiro, que ainda não tem plano.

## 6. As decisões para o Matheus (PROPOSTAS; cada uma com a recomendação e o custo de errar)

| # | a pergunta | a recomendação | o custo de errar |
|---|---|---|---|
| **D-R3-1** (as metas) | quais metas da R2 continuam e quais mudam? | **as 27 continuam com a mesma faixa e a mesma fonte.** O T-1 segue a exceção da DE-9. O **G-2 volta a ser meta a fechar** na R3-3: o 0,31 aceito em 2026-11-07 vale até esta rodada, não como exceção permanente. O **I-4 não muda nesta rodada:** a carta é medida de novo na R3-4, depois das formas e dos líderes novos. Na R2-4, ela pesava até 0,09 na Campina e na Floresta e perto de zero nos três líderes que reprovam. Se ainda falhar, a troca da meta (medir só onde a carta decide) volta ao Matheus depois da conferência, com os números | mudar uma meta agora seria escolher a régua antes de ver a luta nova. Manter o I-4 pode deixar a meta reprovada mais uma vez, por uma régua que talvez seja a errada. Tratar o G-2 como exceção deixaria o Tortomon fácil demais para o pet sem treino |
| **D-R3-2** (a versão) | a rodada mede a v18/v19 ou cria a v20? | **mede a luta v18, que é a da v19, como ponto de partida.** Os ajustes ficam num candidato próprio da rodada (por exemplo, `RELOGIO_R3` e `LISTAS_R3`), só na bancada, sem versão de pet. Ligar no jogo é uma tarefa própria depois da R3-5, com a próxima versão livre. A **v20 já está pedida pelo ARVORE_SACODE** (#694, aberto); seria a v21 ou a seguinte | criar a v20 agora: briga pelo número com o #694, e uma versão nasceria antes de se saber se algum número muda. Mudar a v18 e a v19 direto: as lutas já jogadas mudam, e a regra "uma versão por mecânica" quebra |
| **D-R3-3** (a PE5) | onde a PE5, a lembrança do rival na luta, entra? | **depois da R3-5, com papel próprio** (a PE5 da ponte, com o Opus). A bancada não roda o modular (PL-8), então a PE5 não muda nenhuma meta como a rodada a mede. Pô-la antes atrasaria a rodada por uma mecânica que ela não vê | se a PE5 mudar como o pet de verdade luta contra um rival repetido, a rodada não cobre esse pet. Ela já não cobre o ε da PE4, que fica fora (D-R3-4). Pôr antes: a rodada espera um papel, um código e um gabarito, e "equilibrar só no fim" pede a ordem inversa só para o que a bancada mede |
| **D-R3-4** (o pet com o cérebro) | a rodada mede também o pet com o modular e a ponte (o ε pelo `g_exp`)? | **não:** a rodada mede o `GambitsPet` com o perfil canônico e o ε de hoje, que é o da ponte com `g_exp = e0`. Medir o pet com o cérebro pede um plano de análise e uma faixa próprios (PL-8) | o pet de verdade, com o modular, luta com um ε que se move, e as metas não dizem nada sobre ele. Medir aqui seria pôr um número do jogo como resultado sem gate |
| **D-R3-5** (as sementes) | reservar `83101…83505` para a calibração e `84101…84505` para a conferência? | **sim, num commit próprio depois da aprovação.** A `72101…72505` fica só para a prova de reprodução da R3-0 | uma faixa errada mistura resultados. Calibrar de novo na 72101: a rodada partiria de sementes em que o empurrão já foi escolhido, e o "antes" sairia ajustado a elas |
| **D-R3-6** (o T-3 com os efeitos) | o T-3 passa a contar o tempo de tela que os efeitos põem (a pausa do impacto, a câmera lenta do nocaute, a espera do fim de 1,8 s)? | **sim, como uma coluna ao lado, com a meta igual.** O tempo de tela sai dos eventos da luta pelas funções puras da vista (`efeitosTR.ts`, `nocauteTR.ts` e a pausa de `src/luta.ts`), sem navegador. Entra na bancada da fase 1 no PR da R3-0, atrás de uma opção | sem contar, o T-3 mede menos tempo do que a tela mostra. A folga hoje é grande (64 s contra 180 s), então o risco é baixo. Contar exige código na bancada e um número de tela que é PROPOSTO, SEM FONTE |
| **D-R3-7** (as alavancas da R3-1) | a alavanca de estrutura entra como (a) um número próprio do tempo real para o disparo contra quem fecha a distância e (b) a pele dura do tita, com o `guarda` do empurrão (EMP-5)? | **sim às duas, só no candidato.** O `guarda` entra porque o tita subiu de 0,694 a 0,86 com o empurrão (seção 2). A força da investida e do pesado, a queda e o deslize não mudam | mexer no `guarda` reabre a EMP-5, que o Matheus decidiu. Sem ele, o tita fica acima de 0,60, e o F-1, o F-2 e o I-3 não fecham. Um disparo forte demais devolve a luta curta (o T-1 da primeira rodada) e pode quebrar o F-3, que está no limite |
| **D-R3-8** (o aprendizado) | a R3-2 usa a troca escolhida pelo resultado (a candidata pela nota das lutas que ela teria decidido)? | **sim, como um bloco próprio do candidato**, sem mexer no `GA` (DR2-5) | sem ela, o Ultimate fica perto de 0,5. Com ela, a troca deixa de explorar, e o pet pode fixar uma lista ruim cedo: o P-4 vigia |
| **D-R3-9** (os números visuais) | os números PROPOSTOS dos efeitos (E1 a E5) entram nesta rodada? | **não:** ficam para a rodada de equilíbrio visual, com as capturas e jogando. Eles não mudam nenhuma luta | calibrá-los aqui não teria régua: a bancada não vê a tela. Deixá-los para depois mantém o combate com números de vista não calibrados, que o Matheus já aprovou nas capturas |

**A ordem das fases** (seção 3) e **o chip no topo** (R3-4) repetem as recomendações que o Matheus já decidiu para depois da conferência
(2026-10-30: "a alavanca de estrutura das formas de longe e do tita", "a troca pelo resultado", "a Cidadela, o Lago e a Espiral", "o I-4"
e "o chip no topo"; `docs/EQUILIBRIO_COMBATE_TR.md`, R2-5). O plano as põe aqui em ordem, sem decisão nova.

## 7. As questões abertas (nenhuma se resolve neste plano)

1. **Uma alavanca de estrutura pode bastar para as de longe sem quebrar o F-3?** O F-3 passa por uma forma só (o duelista vence 2), e o
   disparo mais forte já o quebrou na rodada 2 (R2-1, rodada 2). Se a R3-1 não achar um ponto que passe os dois, a fase para pela regra das
   3 rodadas e relata.
2. **O P-4 e os Cenários do Laboratório:** o achado D-LAB-CEN-3 (2026-11-07) diz que, nos Cenários, os pets v19 param no Champion pela
   qualificação do sparring. A bancada mede o P-4 a 0,9125 no Champion. A diferença pode vir do dono simulado (que não tratava a lesão,
   D-LAB-CEN-2) ou do rival. A R3-0 só registra a medida; achar a causa não é desta rodada.
3. **O tempo de tela do T-3** (a D-R3-6) depende de números da vista que não estão calibrados (a D-R3-9). A coluna nova é uma estimativa
   com os números de hoje.

## 8. A entrega de cada fase

| fase | o PR |
|---|---|
| **R3-0** | um PR com o commit das faixas (a D-R3-5), a prova de reprodução em `72101…72505`, a coluna de tela do T-3 (a D-R3-6) e o ponto de partida nas sementes novas |
| **R3-1 a R3-4** | um PR cada, com a tabela das metas da fase na calibração, os artefatos e as metas protegidas |
| **R3-5** | um PR com a tabela de todas as metas, na calibração e na conferência, e a lista do que não fechou |

**O merge é só do Matheus.**
