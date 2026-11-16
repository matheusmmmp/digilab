# TAREFA V3 — VALUATION (2026-11-16)

Coordenador: a sessão da LONGE_GEOMETRIA e da LIMPEZA (Claude Code). Worker: Claude Code, Opus 5.5, sessão filha. Worktree e branch:
`v3-valuation`. Status: ABERTA, na Fase V1 (CHECKPOINT V2). O CHECKPOINT V1 foi aprovado em 2026-11-16.

Categoria: experimento. Origem: Matheus, 2026-11-16. O pedido é diagnosticar por que o modular sente a fome e não fecha o episódio de fome
(o elo Valuation), nas fases V0 a V5.

## 1. Pergunta

Por que o DigiBrain modular (o REL da C4) fecha menos episódios de fome que a baseline trivial da A1 no `longe_fixo` (REL − TRIV = −0,083
[−0,128; −0,038], PR #943)? E qual elo, do drive à escolha, falha? A frente vem do resultado da EVIDENCIA A1 (`docs/TAREFA_V3_EVIDENCIA.md`
no branch `v3-evidencia-a1`). A V0 conferiu que o REL come mais ração por dia (2,96 contra 1,49). A pergunta que vale para a V1 é a da
janela: por que o REL não fecha o episódio a tempo. A seção 1 do [MAPA_VALUATION.md](MAPA_VALUATION.md) traz a conta.

## 2. Depende de

- **A A1:** o resultado e os artefatos estão no branch `v3-evidencia-a1` (PR #943, aberto). A V1 os cita por esse branch enquanto o PR não
  entrar na `main`.
- **A LIMPEZA** (`docs/TAREFA_V3_LIMPEZA.md`): o `afeto.py`, o `sens.py` e o `_comum.py` importam do `digilab/policies/lobos.py`, que sai
  com o A. A run da V2 precisa de uma `main` estável nesse ponto (D-VAL-6).
- **O "aprovado" do Matheus** em cada checkpoint (V1, V2, V2.5, V3, V4, V5).

## 3. Mudança mínima

- **V0 (este PR):** só documentos. Entram o `docs/MAPA_VALUATION.md`, esta tarefa e a seção do registro.
- **Da V1 em diante,** como o pedido diz: o plano (`docs/PLANO_ANALISE_V3_VALUATION.md`), a ablação (`experiments/run_v3_valuation.py`,
  rodada uma vez) e o conserto atrás de chave desligada, com o teste "liga melhora, desliga não muda".
- **O que não muda:**
  - o `engine.py`, a métrica da A1 (a taxa por episódio) e os saves antigos (opção (a): a chave desligada);
  - nenhuma versão nova de pet sem o Matheus, e nenhum mecanismo novo;
  - o A nunca entra como controle nem como braço;
  - o `D:\Trab\digilab\backup_limpeza_2026-11` nunca é lido.

## 4. Experimento e gate (se houver run)

- Plano de análise: `docs/PLANO_ANALISE_V3_VALUATION.md`, commitado antes da run (a V1).
- **Sementes reservadas:** uma faixa nova, pedida na V1. Já estão ocupadas a 93101…93505 (LONGE_GEOMETRIA), a 96xxx e a 97xxx (A1) e a
  98xxx (A2).
- **Métrica e gate:**
  - o primário é a taxa por episódio no `longe_fixo`, um braço por hipótese contra o REL completo, com o IC95;
  - a privação e a exaustão não podem piorar;
  - a regra de leitura é escrita na V1.
- **A máquina:** CPU só, até 4 processos e uma run de pesquisa por vez. A run só roda com a máquina livre.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2). **Não edite o índice
  `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge. Um conflito nele se resolve
  rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.
- Um PR por fase, sem merge.

## 6. Fora desta tarefa

- **A hipótese D** (P1 e P2): fica com a A2.
- **Mudar a métrica da A1** e decidir o produto.
- **Refatorar o código de produto.**
- **Calibrar o equilíbrio do cuidado** (a frente EQUILIBRIO_CUIDADO).

## 7. Critérios de aceitação

- **V0:**
  - o `docs/MAPA_VALUATION.md` existe, com o fluxo de `sens.falta` a `arb.escolher`, todos os termos da ativação, a tabela das hipóteses A,
    B, C, E, F e G (arquivo, linha e predição falsificável) e a prioridade;
  - as linhas citadas foram conferidas na `main` de hoje;
  - os links resolvem (o `verificar_relato.py`, categoria documentacao).
- **As fases seguintes:** os critérios do pedido, seção "As fases" abaixo.

## 8. Precisa do Matheus

As decisões do CHECKPOINT V1, cada uma com a recomendação e o custo de errar:

- **D-VAL-1, a pergunta da V1.**
  - **A recomendação:** trocar "por que não come" por "por que não fecha o episódio na janela". O primário segue o da A1. O consumo de
    ração por dia e a fração de decisões de dormir no episódio entram como descritivos.
  - **O custo de errar:** com a pergunta antiga, a ablação procuraria um déficit de consumo que os artefatos não mostram. Um conserto que
    "faz comer mais" pode subir as decisões de `comer` sem subir o fechamento.
- **D-VAL-2, a hipótese R (o reflexo do sono) entra?**
  - **A recomendação:** sim, com dois braços que só usam o que já existe:
    - a `intencao_suspensa`, que segura a intenção e não mexe no sono;
    - o `lambda_sono` menor, que mexe no sono e deve subir a exaustão.
  - **O porquê:** é o sinal mais forte nos descritivos (20,4 % das decisões em reflexo, 44,3 % das decisões do episódio em `dormir`).
  - **O custo de errar:** sem R, a V2 pode sair "causa não localizada" com a causa mais provável fora da lista. Com R, ficam dois braços a
    mais na run.
- **D-VAL-3, uma chave de ablação para F e G.**
  - **O problema:** não há controle que já exista para tirar só o V e o E do z (F), nem para trocar o sorteio pelo maior peso (G).
  - **A recomendação:** duas chaves de ablação, desligadas, só para a pesquisa, com o teste "desligada, a vida de hoje byte a byte". Não
    são mecanismo novo, porque só zeram um termo ou usam o caminho de maior peso que o M-ARB já tem (`arb.py:98-99`).
  - **A alternativa:** F pelo `p2 = False`, que confunde F com o hábito inteiro, e G só descritivo, gravando o maior peso de cada decisão.
  - **O custo de errar:** sem as chaves, F e G ficam sem ablação limpa. Com elas, entra código de pesquisa no cérebro (atrás de chave).
- **D-VAL-4, a ablação de A.**
  - **A recomendação:** usar a `ConfigDecisaoNaComida`, que já existe e decide no tick em que a comida cai.
  - **O porquê:** a TRIV decide na mesma cadência de 15 ticks. Trocar o `intervalo_decisao_ticks` muda a física de todo pet e não isola o
    cérebro.
  - **O custo de errar:** com o intervalo, o braço mistura cadência com física e não se lê.
- **D-VAL-5, onde a ablação roda.**
  - **A recomendação:** só no Python (`experiments/run_v3_valuation.py`), que é onde a A1 rodou. O `web/app/scripts/valuation_ablacao.ts`
    do pedido fica para a V3, se o conserto for ao jogo.
  - **O custo de errar:** rodar nos dois dobra a run, e a paridade não é correção (a regra do pedido).
- **D-VAL-6, a ordem com a LIMPEZA e a A1.**
  - **A recomendação:** a V2 roda numa `main` fixa, com o commit no `meta.json`, e depois do merge do PR #943. Se a LZ2 mover os imports do
    `lobos.py`, roda depois dela, com o teste de replay verde.
  - **O custo de errar:** uma run no meio da LIMPEZA pode não se reproduzir no commit seguinte.

## O pedido do Matheus (2026-11-16, como veio da sessão de origem)

Esta sessão trata só do gargalo do Valuation, o elo que converte drives em peso de ação. O pedido não deixa refatorar código de produto nem
adicionar mecanismo novo. O objetivo é diagnosticar por que o cérebro modular sente (38 % de privação) e não age (come 10× menos que uma
regra trivial), e consertar o elo que falha sem perder a vantagem de bem-estar que a A1 revelou.

**A A1:**
- REL − TRIV = −0,083 [−0,128; −0,038], "< 0".
- O REL tem 38 % de privação, contra 98,6 % da TRIV, e 24 % de exaustão, contra 100 %.
- A TRIV come 614 820 vezes, contra 59 925 do REL.
- O gargalo está no Valuation, o elo entre o Drive e o Executive.

**As hipóteses** (a D, P1/P2, fica com a A2):
- **A**, a frequência de decisão: o modular decide a cada 15 min (`motor_corpo_mundo.ts`, `proximaDecisao = tick + intervalo`).
- **B**, o `g_exp` alto suprime o comer (`afeto.ts`, `arb.ts`).
- **C**, a memória de lugar atrapalha (`mem.ts`, `impulso.ts`, a unidade `ponto` do explorar).
- **E**, o limiar de fome alto (`constantes.ts`, `w0.comer.u_fome = 3072`, viés −1088).
- **F**, o V e o E deprimem o comer (`afeto.ts`, `impulso.ts`).
- **G**, o número de alvos dilui o comer (`arb.ts`, o sorteio proporcional).

**As regras:**
- não quebrar o replay;
- nenhum mecanismo novo;
- paridade não é correção;
- CI verde não é suíte verde (registrar as falhas conhecidas);
- não mudar a métrica da A1;
- não decidir produto;
- um critério que falha para a fase, com o relato;
- o plano commitado antes da primeira vida;
- os artefatos em `artifacts_v3_valuation/`, com `meta.json`.

**As fases** (um PR por fase, sem merge):
- **V0:** o mapa (documento). Para no CHECKPOINT V1.
- **V1:** o `docs/PLANO_ANALISE_V3_VALUATION.md`, com:
  - um braço por hipótese contra o modular completo;
  - o consumo e a taxa por episódio no `longe_fixo`;
  - a privação e a exaustão;
  - o IC95, a regra de leitura e uma faixa nova.

  Para no CHECKPOINT V2.
- **V2:** a run da ablação (`web/app/scripts/valuation_ablacao.ts`, `experiments/run_v3_valuation.py`), uma vez. Para no CHECKPOINT V2.5.
  Se nenhuma hipótese se confirmar, a frente para com "causa não localizada".
- **V3:** o conserto atrás de chave, com:
  - o teste "liga melhora, desliga não muda";
  - a privação e a exaustão sem piorar.

  Para no CHECKPOINT V3.
- **V4:** a validação contra a TRIV, com a regra escrita antes (ganho, perda, nulo, indeterminado). Para no CHECKPOINT V4.
- **V5:** o `docs/SINTESE_VALUATION.md` e uma linha no PAINEL. Para no CHECKPOINT V5.

**As adaptações da sessão de origem, que valem sobre o texto:**
1. **A limpeza:** o A, o bandit, o B, o C, a camada única e a v1 saem do repositório. O A nunca é proposto como controle nem como braço, e o
   backup da limpeza nunca é lido.
2. **O índice dos desvios:** o worker não edita o `docs/REGISTRO_DESVIOS.md` nem roda o gerador (o `CLAUDE.md`).
3. **Os saves v21 a v37:** fecham com aviso na LZ3 (D-LZ-1). Vale a opção (a), a chave desligada. Versão nova de pet é decisão do Matheus.
4. **A máquina:** no máximo 4 processos e uma run de pesquisa por vez. A suíte inteira e as runs da V2 e da V4 só rodam com a máquina
   livre.

## Resumo das etapas

### V0, o mapa (2026-11-16, Claude Code, Opus 5.5)

O [MAPA_VALUATION.md](MAPA_VALUATION.md) segue o fluxo de uma decisão do REL, do M-SENS ao M-ARB, termo a termo, com as linhas do Python
(onde a A1 rodou) e as do TS ao lado. Os achados que mudam a V1:
- **O "come 10× menos" conta decisões `comer`, não refeições.** O REL come 2,96 rações por dia, e a TRIV, 1,49 (`longe_fixo`). O que falha
  é o fechamento dentro da janela: 39 % dos episódios do REL vencem a janela, contra 9 % da TRIV.
- **O reflexo do sono decide 20,4 % das decisões do REL**, e 44,3 % das decisões do episódio são `dormir`. Daí a hipótese R, PROPOSTA.
- **A** não separa os braços: a TRIV decide na mesma cadência de 15 ticks.
- **C** tem evidência contra no mesmo primário: na C4, REL − SEM = +0,065. Mas todas as visitas ao lugar lembrado saem vazias.
- **B e F** têm predição de nulo pelas sondas e pela forma do código: nenhuma linha de W0 lê V nem E.
- **F e G** não têm controle que já exista (D-VAL-3).

Status: o Matheus aprovou o CHECKPOINT V1 em 2026-11-16 ("Aprovado, siga a V1"). As D-VAL-1 a D-VAL-6 ficaram DECIDIDAS pela
recomendação.

### V1, o plano de análise (2026-11-16, Claude Code, Opus 5.5)

O [PLANO_ANALISE_V3_VALUATION.md](PLANO_ANALISE_V3_VALUATION.md) desenha a ablação: oito braços (o REL e uma ablação por hipótese A, B, C,
E, F, G e R) nas 4 células do `longe_fixo`, com 200 unidades pareadas e 6 400 vidas, rodadas uma vez.
- **O primário:** a taxa por episódio da A1, braço − REL, com o IC95 pelo t e o Holm sobre os 7 contrastes.
- **A guarda do bem-estar:** a privação e a exaustão, sem gate na V2 e vinculante na V3.
- **A regra de leitura:** confirmada, efeito trivial, refutada ou indeterminada, escrita antes. Sem nenhuma confirmada, a frente para com
  "causa não localizada".
- **A faixa:** a 99101…99505, reservada em `faixas.py` como PROPOSTA.

O segundo braço da R (a `intencao_suspensa`) não pode ser montado, porque a config recusa a combinação com a `memoria_autobio`
(D-VAL-7).

Status: PROPOSTO, no CHECKPOINT V2, com as D-VAL-7 a D-VAL-10 (seção 10 do plano).
