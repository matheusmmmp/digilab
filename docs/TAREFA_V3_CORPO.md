# TAREFA V3 — CORPO (2026-11-18)

Coordenador: a sessão "Auditoria de projeto com LLM". Worker: Claude Code (Opus 5.5, a sessão lateral da CORPO_ACOPLAMENTO). Worktree e
branch: `v3-corpo-mapa` para a C0 (o `v3-corpo` fica para as fases seguintes). Status: ABERTA; a C0 APROVADA ("Aprovado", 2026-11-18, CHECKPOINT C1); a C1, o plano, no PR empilhado no #999, esperando o CHECKPOINT C2.

Categoria: documentacao. Origem: Matheus, 2026-11-18: o programa C0-C5 do corpo, colado pelo Matheus na sessao lateral da CORPO_ACOPLAMENTO em 2026-11-18.

## 1. Pergunta

O corpo de hoje deixa o pet comer e descansar sem que uma necessidade anule a outra? Se não, qual redesenho, atrás de chave, reduz a tensão
entre a fome e a energia sem piorar o bem-estar e cria substrato para o social? Vem da A1, da VALUATION (V2 e V3) e da CORPO_ACOPLAMENTO.

## 2. Depende de

- A CORPO_ACOPLAMENTO até o plano (#994, #995 e #996, na `main`).
- A run da opção D (`docs/PLANO_ANALISE_V3_CORPO_ACOPLAMENTO.md`), rodando em 2026-11-18: o resultado dela entra na prioridade da C1.
- O "aprovado" do Matheus em cada CHECKPOINT (C1, C2, C2.5, C3, C4 e C5).

## 3. Mudança mínima

As fases, em ordem, cada uma num PR:
- **C0:** o `docs/MAPA_CORPO.md`, só papel.
- **C1:** o `docs/PLANO_ANALISE_V3_CORPO.md`, só papel.
- **C2:** a run de ablação, uma vez.
- **C3:** o conserto atrás de chave, no Python e no TS.
- **C4:** a validação, uma vez.
- **C5:** a síntese e a especificação.

O que não muda: o `engine.py`, os saves de hoje (toda mudança atrás de chave desligada), a métrica da A1 e a da V2, e nenhum mecanismo
social (M1–M4, SP-3, CO6/CO7).

## 4. Experimento e gate (se houver run)

- Plano de análise: `docs/PLANO_ANALISE_V3_CORPO.md`, commitado antes da run.
- Sementes reservadas: a pedir ao coordenador na C1 (a ablação) e na C4 (a validação).
- Métrica e gate: o forrageio (a taxa por episódio da A1), a privação e a exaustão (a V2), lidos juntos; a regra na C1, PROPOSTA.
- GPU: não.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2). **Não edite o índice
  `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge. Um conflito nele se resolve
  rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

- O mecanismo social, a limpeza da complexidade acidental e as decisões de produto (o que é JOGO, o que é LAB).

## 7. Critérios de aceitação

- **C0:** o `docs/MAPA_CORPO.md` cobre as ações e as taxas do corpo v11, com arquivo e linha; cada opção tem uma predição e um custo; a
  prioridade é explícita.
- **As fases seguintes:** os critérios do programa, fase a fase, com o plano commitado antes da primeira vida.

## 8. Precisa do Matheus

- **CHECKPOINT C1:** aprovar o mapa e a prioridade (a recomendação e o custo de errar estão na seção 8 do mapa).
- **Antes da C1, três pontos em que o programa bate com as regras do projeto:**
  - o harness da ablação em TS, contra a pesquisa no Python;
  - o K = 200 sementes independentes, contra a derivação das runs anteriores;
  - o worker regenerar o índice de desvios, contra o CLAUDE.md.

  A recomendação para os três é ficar com a regra do projeto.

## 9. O código das chaves da ablação (C2, a primeira parte; 2026-11-18)

O plano da C1 (`docs/PLANO_ANALISE_V3_CORPO.md`, seção 7) pede as chaves dos braços na `main` antes de qualquer vida. Este PR põe as duas
que faltavam, desligadas, no Python e no TS. Nenhuma vida de faixa rodou, e nenhum pet do jogo liga nenhuma das duas.

- **A E, a digestão inteira** (`ConfigDigestaoCorpo.inteira`, em `digilab/config.py`; `Corpo._converter_excedente`, em
  `digilab/corpo.py`).
  - Ligada, a comida que sobra no estômago com a fome em 0 vai inteira ao combustível, pela fração do metabolismo, com o teto C.
  - A fome cai como hoje, e nada vai ao `descartado_total`.
  - Exige a digestão e o metabolismo.
  - O `MotorCorpo` recebe a `cfg_digestao_corpo`.
- **A C5, o reflexo suave** (`ConfigConsertoValuation.reflexo_suave` e `peso_reflexo_suave` = S, em `digilab/config.py`;
  `Arbitragem._suave`, em `digilab/digibrain/arb.py`).
  - Ligado, o `reflexo()` dá False. No `escolher`, com a energia abaixo de `lambda_sono`, o `dormir` ganha +S no peso, no sorteio e nas
    sondas, e a escolha segue pelo sorteio.
  - Ele não convive com a guarda da fome da VALUATION, porque cada braço muda uma coisa.
  - No TS, ele é a `ConfigReflexoSuave` do `web/app/motor/digibrain/arb.ts`.
- **"Desliga não muda":** o gabarito das vidas de hoje (`tests/gabaritos/corpo_acoplamento_de_hoje.json`) e o da VALUATION
  (`tests/gabaritos/valuation_conserto_de_hoje.json`) passam byte a byte.
  - Os dois foram gravados antes de qualquer chave do corpo, e nenhum foi regravado.
  - O `tests/test_corpo_chaves.py` também confere cada chave passada desligada explicitamente.
- **A paridade:** o `experiments/exportar_gabarito_corpo_chaves.py` grava o `tests/gabaritos/corpo_chaves_python.json`, num arquivo
  próprio. O gabarito tem duas partes:
  - a E, sozinha e com a D, nos três corpos do gabarito da D;
  - 400 casos do `escolher` com a C5.

  O `web/app/test/corpo_chaves.test.ts` o reproduz inteiro a inteiro.

## 10. O orquestrador da ablação (C2, a segunda parte; 2026-11-18)

- **O orquestrador:** `experiments/run_v3_corpo.py`. As configs são `experiments/configs/v3_corpo/run.json` e
  `experiments/configs/v3_corpo/fumaca.json`, e o teste é o `tests/test_run_v3_corpo.py`.
- **O bloco I:** a vida do `run_v3_corpo_acoplamento.viver`, com as três chaves do braço. O CTRL e o D saem iguais, byte a byte, às vidas
  do REL e do D da run da D; o teste confere.
- **O bloco II:** um par VIVO por unidade e braço, no instrumento da SOCIAL_PAR A0, com as chaves nos dois pets e o replay pelo
  `reproduzir_grupo`.
- **A conferência de cada vida, com falha alta:**
  - as chaves do corpo e do M-ARB;
  - a ponte;
  - o cansaço sem a falta nos braços com a D;
  - na E, nada descartado;
  - na C5, nenhum reflexo e um peso suave por decisão com a energia baixa;
  - nos outros braços, o reflexo de hoje;
  - o replay e as conferências da VALUATION.
- **A faixa** 104001…104400 e o prefixo `corpo_par` entraram em `experiments/bancada/faixas.py`, num commit antes da run.
- **O custo medido na fumaça:**
  - um par de 5 dias leva cerca de 2,3 s, então o bloco II leva cerca de 4 min com 4 processos;
  - o bloco I, pela run da D (4 800 vidas em 1 h 27 min), leva cerca de 3 h para as 9 600 vidas, e não as 2 h da seção 4 do plano.
- **A run** espera:
  - o #999, o #1002, o #1003, o #1005 e este PR na `main`;
  - nenhuma outra run de pesquisa rodando;
  - o `pre_run` sem motivo de recusa.

## 11. A ablação rodada (C2, 2026-11-19)

A run única, pelo `docs/PLANO_ANALISE_V3_CORPO.md`: 9 600 vidas e 400 pares, em 2 h 6 min com 4 processos, a partir da `main` em
`eedfb2f4`. O resultado está no `docs/RESULTADO_V3_CORPO.md`.

**A leitura: os três braços saem em "perda".** O F sobe nos três (D +0,120, D + E +0,110, D + C5 +0,168 na taxa por episódio do
`longe_fixo`, todos com o Holm rejeitando). Mas a privação do comedouro sobe nos três, e na D + C5 a exaustão quase dobra. O S1 não mede
(zero chutes). **O programa para no CHECKPOINT C2.5:** o diagnóstico e o trade-off vão ao Matheus.

## 12. O diagnóstico da C2.5 (2026-11-19)

O Matheus respondeu "Sim, diagnosticar". O diagnóstico está no `docs/RESULTADO_V3_CORPO.md`, seção 5, feito só com as vidas gravadas,
rejogadas do log (`experiments/diagnostico_v3_corpo_c25.py`).

**A causa:** a D tira a falta de combustível do cansaço, que o sono resolve, e a põe na fome, que só a comida resolve. Com o atencioso e o
incoerente, o pet come mais e a privação cai. Com o relapso e o aleatório, não há comida a mais, a fome fica acima do limiar, e o dano da
privação baixa a saúde (−0,12 a −0,24). O comedouro só sai em "> 0" porque ali a privação com os donos bons já está perto de 0. **As
opções da C3** (a ponte com teto, a ponte dividida ou nenhuma mudança) vão ao Matheus.

## 13. O plano da C3, a ponte com teto (2026-11-19)

O Matheus escolheu "Ponte com teto". O plano é o `docs/PLANO_ANALISE_V3_CORPO_C3.md`, PROPOSTO. Os braços são CTRL, D, DTL (o teto no
limiar da privação, T_L = 382 500) e DTB (o teto em C/2, se a D-C3-2 for aprovada), nas 12 células × 200 unidades e no bloco II. **O que o
mecanismo prevê:** o teto no limiar tira pouco do dano, porque o dano da privação é um degrau e vem da chegada mais cedo ao limiar.
Há uma guarda nova da saúde (D-C3-4). A pergunta do incoerente igual ao atencioso vai como pergunta do plano (D-C3-6). A faixa
106001…106400 está pedida ao coordenador. Nenhuma vida antes da aprovação e do código.

## 14. O código da C3 (2026-11-19)

Pelo `docs/PLANO_ANALISE_V3_CORPO_C3.md`, seção 7. Nenhuma vida da faixa rodou.
- **A chave:** a `ConfigTetoFomeCorpo` (`digilab/config.py`), numa config própria para nenhum dump de hoje mudar, com `teto = None` por
  padrão. Com um teto, num tick com a falta de combustível, a ponte da D soma à fome `min(500, max(0, teto − fome))`
  (`digilab/corpo.py`, a fase 2 do tick). O `ticks_teto` conta os ticks em que o teto cortou a ponte. O teto exige a D e não passa de C.
- **O DTL e o DTB:** `CONFIG_TETO_FOME_LIMIAR` (382 500, igual ao `t.limiar_privacao`, conferido por teste) e `CONFIG_TETO_FOME_BAIXO`
  (225 000, C/2, SEM FONTE).
- **O web:** o espelho em `web/app/motor/corpo.ts` (`opcoes.tetoFome`, desligada por padrão) e o gabarito
  `tests/gabaritos/corpo_teto_python.json` (`experiments/exportar_gabarito_corpo_teto.py`), reproduzido inteiro a inteiro em
  `web/app/test/corpo_teto.test.ts`.
- **O orquestrador:** o `experiments/run_v3_corpo_c3.py`, um arquivo próprio para o `run_v3_corpo.py` da C2 ficar intacto (o sha256 dele
  está no `meta.json` da C2). Ele reaproveita as vidas e a análise da C2, com os braços CTRL, D, DTL e DTB, as oito guardas do bem-estar
  (com a saúde), o S2 e o descritivo (braço − D, por dono, a decomposição da privação, os ticks no teto e o incoerente). As configs ficam
  em `experiments/configs/v3_corpo_c3/`.

## 15. A run da C3, a ponte com teto (2026-11-19)

A run única do `docs/PLANO_ANALISE_V3_CORPO_C3.md`, no commit `f720d684`: 9 600 vidas e 400 pares, em 3 h 4 min, com 4 processos. O relato
é o `docs/RESULTADO_V3_CORPO_C3.md`.
- **DTB, o teto em C/2: "ganho".** O F sobe +0,120 [+0,105; +0,135], nenhuma das oito guardas do bem-estar reprova, e o S2 passa.
- **DTL, o teto no limiar: "perda".** O F sobe +0,123, e reprovam a privação do comedouro (+0,072) e as duas guardas da saúde (−0,040 e
  −0,162). Ele sai quase igual à D, como o plano previa.
- **A ressalva do DTB:** com o aleatório no comedouro, a saúde ainda cai −0,048. A guarda passa na média das seis células dos donos que
  deixam faltar comida. O T_B = C/2 é SEM FONTE.
- **O incoerente:** no comedouro, 799 de 800 vidas saem iguais às do atencioso. A leitura nas 11 células distintas é a mesma.

**O programa para no CHECKPOINT da C3.** Pela seção 8 do plano, o ganho leva à C4, a validação; a decisão é do Matheus. Nenhum braço está
ligado no jogo.
