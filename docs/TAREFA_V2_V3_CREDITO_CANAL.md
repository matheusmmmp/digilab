# TAREFA V2 — V3_CREDITO_CANAL: o crédito do "querer" por canal até o alvo (2026-10-19)

Coordenador: Gerente (Claude Code). Worker do desenho: Claude Code (worker B). Worktree e branch: `v2-v3-credito-canal`. Status: ABERTA
(só o desenho; o código não começou).

Categoria: implementacao (a tarefa); o PR deste desenho é `arquitetura`. Origem: Matheus, 2026-10-19: seguiu a recomendação V3-9 de
`docs/futuro/v3_espaco_acoes.md` (seção 8), antes da V3-3/V3-4 e da V3-10.

Todo o desenho é **PROPOSTO**. As marcas seguem as do `v3_espaco_acoes.md`: [IMPLEMENTADO] (está no código da `main`), [OBSERVADO] (tem
artefato), [HIPÓTESE] e [PROPOSTA].

## 0. Duas coisas que o desenho mostrou antes de tudo

**Elas mudam o que a V3-9 pode prometer. Por isso vêm primeiro.**

1. **Separar por canal, sozinho, não muda nada.** [IMPLEMENTADO, conta]
   - A regra da L1 nas classes do alvo (`atualizar_fruta`, `digilab/policies/lobos.py`) é linear no sinal:
     `Δw = div_arred(f · passo · X · fator, S² · W)`.
   - O contrato K-6 garante que os canais somam o escalar.
   - Logo, tabelas por canal lidas pela soma dão o mesmo peso de hoje, a menos de dois desvios: o arredondamento (até uma unidade por
     canal e por crédito) e o corte no teto.
   - **O comportamento só muda com uma destas três peças:**
     - o teto por canal;
     - uma leitura que pese os canais de forma diferente;
     - um aprendizado diferente por canal: o passo ou a fonte.
   - A decisão CC-1 (seção 8) escolhe essa peça.
2. **O T1 do J5, como está escrito, não pode ver um crédito que só aprende com as próprias decisões.** [IMPLEMENTADO no plano]
   - O T1 conta só as oportunidades até o primeiro consumo da x no mapa depois de `T_m` (o corte da reexperiência,
     `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`, seção 4).
   - A x na mão não credita os pesos de decisão nem os de alvo do A (a G-SEM-CREDITO, gate de mecanismo).
   - O P1 é, por desenho, o controle do hábito (Adams e Dickinson, 1981, referência do plano).
   - **Portanto, qualquer forma de crédito que aprende só com a própria escolha prevê P1-canal = P1 no T1.** Só um "querer" que aprenda
     também com a mão pode mudar o T1, e esse muda a G-SEM-CREDITO e o sentido do braço (seção 8, CC-1, opção C2).

**Correção à minha leitura no `v3_espaco_acoes.md`** (seção 3), registrada em `docs/registro/2026-10.md`:
- **as 36 vezes** em que o P1 come a x depois da mudança são reexperiência, fora da janela que o T1 conta;
- **"o planejador revaloriza"** vale para o piloto do adendo 7 (0,67 → 0,46). No piloto do adendo 8, a escolha da x **não** cai com o
  planejador (0,52 → 0,55 a 0,68) e cai um pouco no P1 (0,62 → 0,54) (`docs/RESULTADO_V2_PILOTO_PET_QUE_PENSA_ADENDO8.md`, seção 3).
  Os dois são descritivos de piloto.

O que continua de pé [HIPÓTESE]: depois da reexperiência, o gosto da x compensa no mesmo peso boa parte da perda no humor (o sinal médio
foi −87 nos drives e +66 no gosto no P1, `artifacts_v2_v3/espaco_acoes.json`). Por isso o peso desaprende devagar. É isso que a
V3-9 pode atacar, e o teste certo é o da reexperiência (seção 4).

## 1. Pergunta

O crédito por canal até as classes do alvo de comer (o humor, o gosto e a nutrição separados) faz o pet sem o planejador deixar de escolher
a favorita **depois de reexperimentar** que ela passou a fazer mal, mais depressa do que o crédito somado de hoje?

- Vem da H1, fase 1 (a plasticidade durante a vida; `docs/PLANO_V2_PESQUISA.md`) e do J5 (o pet que pensa, `docs/ROADMAP_V2.md`, seção 8).
- É o nó V3-9 do `docs/futuro/v3_espaco_acoes.md`.

## 2. Depende de

- **Na `main`:** o alvo aprendido com o paladar (PL-5, `CLASSES_COMER_PALADAR`), os CANAIS-REFORCO (`_creditar_canais`) e o mundo do J5
  (adendo 8). Tudo já está lá.
- **As decisões do Matheus na seção 8:** CC-1 a CC-5 antes da etapa 2. A CC-6 (as faixas) só antes de uma run.
- **O J5:** nada. O plano do J5 fica como está (CC-5).

## 3. O desenho e a mudança mínima

### 3.1 Onde o crédito vai hoje [IMPLEMENTADO]

- Com os canais ligados (todas as configs do J5), `_creditar_canais` manda cada canal ao seu grupo (`ROTA_CANAIS`, `ROTA_CANAL_GOSTO`):
  - `corpo` recebe os drives (fome, higiene, energia e os novos);
  - `fruta` recebe o humor e o gosto.
- A classe do alvo do mundo físico (`alvo_mundo`) recebe **o sinal inteiro da decisão**, todos os canais somados. É a decisão do Matheus
  de 2026-10-13 (MUNDO-ALVO, saída 1), comentada no código.
- A classe do alvo (`comida:a`, `comida:b`, `comida:c`, `comida:racao`…) tem um peso por chave `regra:acao`:
  - começa em `w0_alvo` = 64;
  - fica cortada em `w0_alvo ± teto` (teto = 1024 = S);
  - é lida como `max(0, w)/S`, mais 1 se for a classe do alvo padrão do motor.

### 3.2 O que muda [PROPOSTA]

**Atrás de uma chave nova, `ConfigLobos.credito_canal_alvo` (bool, False; PROPOSTO, SEM FONTE),** só nas chaves de comer
(`pedido_necessidade:comer`, `fome_moderada:comer`, `fruta_no_cenario:comer`; CC-3):

1. **Os grupos (CC-2):** cada classe tem um peso por grupo:
   - **o humor** (o canal `humor`);
   - **o gosto** (o canal `gosto`);
   - **a nutrição** (todos os outros: fome, energia, higiene e os drives novos).

   O prior fica todo na nutrição (`w0_alvo`); o humor e o gosto começam em 0. A soma dos priores é a de hoje.
2. **O crédito:** cada grupo recebe a soma dos canais dele, pela mesma regra (`atualizar_fruta`, o mesmo passo, o mesmo registro da
   sub-decisão).
   - A soma dos três créditos é o `f_S` da decisão (K-6), conferida (falha alto).
   - Só pela consequência, como hoje.
   - A x na mão continua sem creditar (G-SEM-CREDITO), salvo se a CC-1 escolher a C2.
3. **A peça que faz o canal importar (CC-1; a recomendada é a C1):** cada grupo é cortado no seu próprio `prior ± teto`.
   - O gosto, que satura positivo, deixa de anular a queda do humor dentro do mesmo peso.
   - A faixa da soma passa de `w0 ± S` para `w0 ± 3S`.
4. **A leitura:** a soma dos grupos, como hoje (`max(0, Σ_g w_g)/S` + o padrão).
5. **O registro:** o motivo da decisão ganha `alvo_canal`, com o crédito de cada grupo e os pesos de cada classe antes e depois, para a
   etapa 0 e para a sonda.
6. **Sem a chave, nada muda:** a vida de hoje sai byte a byte (G2).

**O que não muda:**
- `engine.py`, o motor, o mundo, o corpo e o paladar;
- o planejador e o `ModeloMundo`;
- as chaves de explorar e de brincar;
- os pesos de decisão;
- o bandit, a web e as runs antigas.

**Os arquivos:**
- `digilab/policies/lobos.py`: a tabela por grupo, o crédito e o registro;
- `digilab/config.py`: a chave, com status;
- os testes novos em `tests/test_lobos_credito_canal.py`;
- os gabaritos em `tests/gabaritos/` (G2).

### 3.3 O que conferir na conta antes do código [HIPÓTESE]

A C1 só muda o comportamento onde um peso satura. No P1 do J5, a soma das classes `comida:x` chegou a 2.694
(`artifacts_v2_v3/espaco_acoes.json`). Isso está perto do máximo 3 × (64 + 1024) = 3.264, **se** as três chaves de comer existem
nessa vida. A etapa 0 confere isso antes de qualquer linha em `digilab/`.

## 4. Como o J5 testa (o P1 sem o planejador)

**O mundo é o do J5** (o adendo 8: a fruta ao lado, a x sai das árvores no T1, `n_mao` = 2 em `T_m`), com dois braços: **P1** (hoje) e
**P1-canal** (a chave ligada).

- **O T1, como está, vira o controle negativo:**
  - **a previsão:** `q`(P1-canal) ≈ `q`(P1) (seção 0, item 2);
  - **se não for:** a G-SEM-CREDITO ou o corte da reexperiência têm um furo, e isso para a tarefa.
- **O teste da V3-9 é o T1-R, a revalorização com reexperiência** (CC-4):
  - **a mesma oportunidade do T1** (a decisão com a fome ≤ S/2 e um alvo de x à mão), **sem o corte da reexperiência;**
  - **`f_R`:** a fração de x nas 3 últimas oportunidades da janela de 3 dias depois de `T_m`;
  - **`q_R` = `f_antes` − `f_R`.**
  - **O contraste primário candidato:** `q_R`(P1-canal) − `q_R`(P1).
  - **O descritivo junto:** o número de consumos da x pela própria decisão entre `T_m` e cada oportunidade. Ele separa "desaprendeu
    mais depressa" de "comeu mais vezes".
- **A G-REVAL-POSSIVEL e a G-APRENDEU** do plano do J5 valem iguais para os dois braços. A G-APRENDEU importa aqui: se o P1-canal não
  aprende a x antes (`f_antes`), não há o que desaprender.
- **Um gate novo de mecanismo, G-CANAL-SOMA:** em toda vida do P1-canal, a soma dos créditos dos grupos é o `f_S` de cada decisão de
  comer. Sem corte no teto, a soma dos pesos dos grupos difere da tabela sombra escalar (etapa 0) em no máximo uma unidade por crédito.

A forma exata (a janela, o N, a margem, o bootstrap, as categorias) fica para o plano de análise da etapa 3, antes de qualquer run.

## 5. As etapas e os gates

| etapa | o que | gate (falha para a tarefa) | onde |
|---|---|---|---|
| **0, medir sem mexer** | uma medição em `experiments/` (como o `medir_v3_espaco_acoes.py`): embrulha o `_aplicar_sinal` e mantém **tabelas sombra** por grupo, com e sem teto por grupo, que não entram na escolha. Nas vidas da fumaça do adendo 8 (P1, as sementes dos testes): a fração dos créditos de `comida:x` cortados no teto; o crédito por grupo antes e depois de `T_m`; e a sonda "a escolha mudaria": a P(x) pela leitura sombra contra a de hoje, em cada oportunidade do T1-R | **G0-PODE-MUDAR:** se a mediana de \|ΔP(x)\| nas oportunidades do T1-R depois de `T_m` for < 0,05 (PROPOSTO), a C1 não tem o que mudar. A tarefa para e relata, sem tocar em `digilab/` | PR próprio, `implementacao`; artefato `artifacts_v2_v3/credito_canal_etapa0.json` |
| **1, gabarito antes** | grava, num commit próprio e antes da mudança, os gabaritos com a chave desligada: o A v11 (`bancada_v11`, `experiments/exportar_gabarito_lobos.py`), o mundo com o alvo (a fumaça do `P1-alvo`) e a fumaça do adendo 8 (P1 e P1-plan): o sha do estado interno e do log de cada vida | **G2:** um teste confere os gabaritos byte a byte | `tests/gabaritos/` |
| **2, o código** | a seção 3.2, atrás da chave | G2 continua passando; **G-CANAL-SOMA** (com sinais sintéticos); **G-PESOS:** `n_pesos()` < `maximo_pesos` do plano com a chave ligada (+42 pesos nas três chaves de comer com o paladar); o replay bit a bit; a G-SEM-CREDITO continua passando | o mesmo PR da etapa 1, depois do commit do gabarito |
| **3, o plano** | `docs/PLANO_ANALISE_V2_V3_CREDITO_CANAL.md`: o T1-R, o T1 como controle negativo, o N (com o poder), a margem, as faixas (CC-6) | — (o plano é commitado antes da primeira vida) | PR próprio |
| **4, piloto e validação** | o piloto (as premissas, a margem, o N) e a validação **uma vez** | os do plano | runs nas faixas da CC-6 |

**Nenhum número se calibra:** a C1 usa o teto e o passo de hoje. Se a CC-1 escolher a C3 ou a C4, entra um número novo, e com ele uma
calibração nas sementes dela, antes do piloto.

## 6. Fora desta tarefa

- **a competição entre as regras** (V3-3 e V3-4): vem depois, numa tarefa própria;
- **as ações novas como ações com alvo** (V3-10);
- **o crédito por canal nas chaves de explorar e brincar** (o T2 do J5);
- **o planejador e o `ModeloMundo`:** o P1-plan não ganha a chave;
- **mudar o plano do J5:** nem braço novo nem adendo. O J5 segue para a validação do adendo 8 (55101…55505) como o Matheus decidir;
- **a web:** o jogo roda o A v11 sem o mundo físico, onde esta chave não tem o que mudar. Ela só vai à web se o Matheus a escolher para o
  produto.

## 7. Critérios de aceitação

- **Etapa 0:** o artefato existe e se refaz igual. Um teste confere que o embrulho não muda a vida (o sha do estado interno contra a vida
  sem ele) e que as tabelas sombra somam o escalar dentro do arredondamento.
- **Etapas 1 e 2:**
  - o commit do gabarito vem antes do commit do código;
  - `python -m pytest tests/test_lobos_credito_canal.py -q` passa, e a suíte inteira passa, com a contagem no corpo do PR;
  - com a chave desligada, os gabaritos saem iguais;
  - a chave tem status em `config.py`.
- **Etapa 3:** o plano está commitado antes de qualquer vida nas faixas novas.
- **Em toda etapa:** o desvio vai em `docs/registro/AAAA-MM.md` e no índice; o resumo vai no corpo do PR e na seção 9 deste arquivo.

## 8. Precisa do Matheus

Todas PROPOSTAS, com a recomendação primeiro.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **CC-1** | a peça que faz o canal importar (seção 0, item 1) | **C1, o teto por grupo,** com a etapa 0 como porta. Não traz número novo e não toca a G-SEM-CREDITO. Testa exatamente a hipótese (o gosto saturado mascara o humor no mesmo peso). As outras: **C2,** o grupo aprende também com a x na mão (passa a poder mudar o T1, mas a G-SEM-CREDITO deixa de valer no braço, e ele vira um "desfecho de um passo", que repete o P1-plan sem o mapa); **C3,** a leitura pesada pela falta de cada drive (logo depois da x na mão, o humor cai e **aumenta** o peso do humor velho, positivo, da x: piora antes de melhorar); **C4,** o passo por grupo (um número novo, SEM FONTE, com calibração) | sem nenhuma peça: o código entra, e o pet se comporta como hoje (a linearidade). Com a C2 sem querer: o J5 perde o controle do hábito. Com a C1 sem saturação: a etapa 0 pega isso antes do código |
| **CC-2** | os grupos | **três: o humor, o gosto e a nutrição** (o resto do corpo) | um por drive: até 12 grupos por classe, os pesos se multiplicam, e a soma volta a misturar o que importa. Dois (corpo e fruta, a rota de hoje): o humor e o gosto ficam juntos, e é a mistura que a V3-9 quer desfazer |
| **CC-3** | onde | **só nas três chaves de comer** | também no explorar e no brincar: mais pesos, e o T2 do J5 (as árvores) passa a depender da chave, sem pergunta para isso |
| **CC-4** | o teste no J5 | **o T1-R** (com reexperiência) como primário do plano novo, com o T1 como controle negativo | o T1 como primário: com a C1 o resultado nulo é certo por desenho, e uma faixa de validação se gasta para confirmar o desenho |
| **CC-5** | a ordem com o J5 | **um plano próprio,** com o mundo do adendo 8 e o P1 como controle, sem tocar no plano do J5 | um braço novo no plano do J5: muda um plano que já tem piloto e faixa de validação (55101), e mistura a pergunta do planejador com a do crédito |
| **CC-6** | as faixas, se houver run | **pedir ao coordenador 56101…56505** (piloto) e **57101…57505** (validação). Nenhuma das duas está em `experiments/bancada/faixas.py` nem nas configs. A etapa 0 usa só as sementes dos testes | usar uma faixa do J5: as calibrações e validações do J5 ficam comprometidas, e as faixas queimadas não voltam |

## 9. Resumo da etapa (o desenho, 2026-10-19)

- **O que saiu:**
  - esta tarefa, com o desenho todo PROPOSTO;
  - a correção da leitura do `v3_espaco_acoes.md` (seção 3);
  - o desvio no registro.
- **O que o desenho achou:**
  - o crédito por canal, lido pela soma, é o de hoje (a linearidade da L1);
  - o T1 do J5 não pode ver um crédito que só aprende com a própria escolha.
- **O que se propõe:**
  - a V3-9 entra com o teto por grupo (C1);
  - antes do código, uma medição com tabelas sombra decide se há o que mudar;
  - o teste no J5 é o da reexperiência (T1-R), num plano próprio.
- **O que não se fez:** nenhum código mudou, nenhuma vida rodou, e nenhuma faixa foi reservada.

## Referências

- **Adams e Dickinson (1981):** já VERIFICADA no plano do J5 (`10.1080/14640748108400816`, resumo). É usada só para o T1 como teste do
  hábito, como lá.
- **SEM FONTE:**
  - o teto por grupo;
  - o T1-R;
  - os grupos;
  - o limiar de 0,05 da G0-PODE-MUDAR.
