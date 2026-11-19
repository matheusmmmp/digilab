# TAREFA V3 — SOCIAL_PAR (2026-11-17)

Coordenador: Matheus, nesta sessão. Worker: Claude Code (Opus 5.5). Worktree e branch: `v3-social-par`. Status: ABERTA, só o papel.

Categoria: arquitetura. Origem: Matheus, 2026-11-17: investigar como dois pets podem perceber um ao outro, ajustar as ações reciprocamente,
aprender sobre o parceiro, comunicar e fazer atividades conjuntas, com uma recomendação baseada na literatura e no código, um plano
experimental incremental e a especificação da primeira etapa.

## 1. Pergunta

Como transformar o contato entre dois pets numa relação que afete funcionalmente as decisões e a experiência deles? As capacidades são
avaliadas por critérios observáveis (`docs/INVESTIGACAO_V3_SOCIAL_PAR.md`, seção 1.3): discriminar o parceiro responsivo de um objeto
móvel, a reciprocidade, a coordenação, a comunicação que muda a decisão do receptor, o aprendizado sobre um parceiro, a atividade
conjunta com papéis, a recuperação depois de uma interrupção e a generalização.

## 2. Depende de

- **A investigação e a espec:** nada. Elas leem a `main` 358895585 e os artefatos já versionados.
- **A E1 (código):** as decisões SP-1, SP-2 e E1-1 a E1-6 do Matheus.

## 3. Mudança mínima

- **Novo:**
  - `docs/INVESTIGACAO_V3_SOCIAL_PAR.md`, o diagnóstico, as matrizes, os experimentos A a F, os mecanismos, a ordem e as decisões;
  - `docs/ESPEC_V3_SOCIAL_PAR_E1.md`, a primeira etapa;
  - as referências em `docs/referencias/v3_social_par_*`.
- **Alterado:** `docs/registro/2026-11.md`.
- **O que não muda:** nenhum código, nenhuma config, nenhuma faixa.

## 4. Experimento e gate

- **Sem run nesta tarefa.** Os experimentos A a F são desenhos. Cada um terá um plano de análise próprio, commitado antes da primeira
  vida, e uma faixa nova.
- **Os gates da E1** estão na espec, seção 4.

## 5. Entrega

- **Os testes:** `python -m pytest tests/test_infra_verificar_relato.py tests/test_infra_indice_desvios.py -q` e o `tools/verificar_relato.py`
  no corpo do PR. Os testes sociais de hoje (`tests/test_grupo*.py`, `tests/test_cooperacao*.py`, `tests/test_sentidos_mundo.py`) foram
  rodados para registrar o estado de partida.
- **O registro:** uma seção no fim de `docs/registro/2026-11.md`. O `docs/REGISTRO_DESVIOS.md` não é editado.
- **O PR:** contra a `main`, na categoria arquitetura. O worker para e espera o Matheus.

## 6. Fora desta tarefa

- o código da E1;
- as runs A0 e B0;
- os mecanismos M1 a M4;
- qualquer mudança no jogo web.

## 7. Critérios de aceitação

- A investigação tem o diagnóstico com o commit, a matriz das capacidades, a matriz das referências, os seis experimentos com o esqueleto
  de validade, os mecanismos, a ordem, as decisões anteriores com pergunta nova, a situação jogável e as decisões SP-1 a SP-8.
- A espec da E1 tem as interfaces, o pseudocódigo, os gates e os critérios de aceitação.
- Toda referência citada está na tabela verificada desta rodada, com o conteúdo lido declarado.
- O `tools/verificar_relato.py` passa no corpo do PR.

## 8. Precisa do Matheus

As SP-1 a SP-8 (investigação, seção 9) e as E1-1 a E1-6 (espec, seção 8), cada uma com a recomendação e o custo de errar.

## E1, o código do parceiro sob intervenção (2026-11-17, Claude Code, Opus 5.5, branch `v3-social-par-e1`)

- **O que entrou:**
  - a `ConfigIntervencaoSocial`, desligada;
  - o `Grupo.levar_pet` com a origem `intervencao`, e o replay dele;
  - o `MotorMundo.aceitar_ponto_gravado` (D-SP-10, um desvio da espec);
  - seis medidas em `digilab/metrics.py`;
  - o `experiments/bancada/parceiro.py`;
  - a conferência dos controles, `experiments/conferir_controles_social_par_e1.py`.
- **O que passa** (`tests/test_social_par_e1.py`, 15 testes):
  - o G2: desligada, o grupo de hoje byte a byte, e dois vivos sem perturbação dão o registro do `simular_grupo`;
  - o G-GRAV-IDENT: sem perturbação, o modular gravado refaz a vida ao vivo com zero desvios, em 2 sementes, e o par de seguidores
    também, com os contatos;
  - o G-GRAV-CEGA, o G-LEVAR, o G-METRICAS e o G-ENGINE.
- **O que falhou:** os dois controles positivos da espec, seção 3 (D-SP-13). O seguidor × seguidor não separa a VIVO da GRAV, porque um
  seguidor sozinho fecha o d0 em uma decisão (o teto). O evitador não foge de perto, porque o vetor de fuga some no contato (um defeito do
  desenho). A etapa parou aqui, sem mudar os controles.
- **Os dois adendos:**
  - **o adendo 1** (C1 passivo × seguidor, o evitador refeito) passou só em 4 e 3 das 5 sementes, porque as necessidades do corpo passam na
    frente da regra social (D-SP-18);
  - **o adendo 2** (a estátua como focal, parceiros de regra pura, janela de 8 decisões) passou nas 5 (D-SP-21). O G-CONTROLE-POS e o
    G-MET-NULO entraram nos testes.
- **Os desvios aceitos:** o D-SP-10 (o ponto gravado pela porta no motor) e o D-SP-11 (o alvo resolvido), pelas A1-5 e A1-6.
- **Os testes:** `tests/test_social_par_e1.py`, 15 passados; a suíte inteira, 2 falhas antigas (D-SP-22), 5907 passados.
- **O que fica para o A0:** o instrumento separa VIVO e GRAV com certeza só em controles de regra pura. Com pets que se movem e têm
  necessidades, separou na maioria das sementes.

## O plano do A0 e do B0 (2026-11-17, Claude Code, Opus 5.5, branch `v3-social-par-a0`)

- **O que é:** `docs/PLANO_ANALISE_V3_SOCIAL_PAR_A0.md`, PROPOSTO. São as três condições (VIVO, GRAV, OUTRA) no pet de hoje, o modular com a CO7
  nos dois, com uma perturbação por vida. Os primários são o tempo até o reencontro (A0) e o excesso de alternância nos chutes de F para P
  (B0), e o N sai de um piloto que só dá o σ̂ e as frequências.
- **Aprovado** pelo Matheus em 2026-11-17 ("Aprovo todas"), com as faixas (D-SP-26).
- **O que falta:** o código da seção 4 do plano, num PR à parte; depois o piloto e a decisão do N.

## O código do A0 e do B0 (2026-11-17, Claude Code, Opus 5.5, branch `v3-social-par-a0-codigo`)

- **O que entrou:** a seção 4 do plano. As faixas e os prefixos, a fábrica do par de hoje com a CO7, o T\*, o orquestrador (as cinco vidas,
  o G-INSTR, o G1, a análise das seções 5, 7 e 8) e o piloto (só o dp, as frequências e a regra do N).
- **O que passa:** `tests/test_social_par_a0.py`, 10 testes. Entre eles, o G-GRAV-IDENT-CO7 (D-SP-28) e o G-ORQ (a fumaça, D-SP-30).
- **O que falta:** rodar o piloto (`python experiments/piloto_social_par_a0.py --processos 4`) depois do merge, e o Matheus decidir o N e o K.

## O piloto do A0 e do B0 (2026-11-18, branch `v3-social-par-a0-piloto`)

- **O que rodou:** `python experiments/piloto_social_par_a0.py --processos 2`, uma vez, no commit 82d658e4, ao lado da validação do
  ELOGIO, por decisão do Matheus ("Rode já assim"; D-SP-31).
- **O que mostra** (`artifacts_v3_social_par_a0/piloto.json`): no A0, 96 % dos pares são elegíveis, todos com reencontro na janela, e o dp
  do D_A é 0,664. O N = 200 basta, com K = 42 por base. No B0, nenhum par é elegível: o B0 sai inconclusivo por premissa (D-SP-33).
- **O que falta:** o Matheus decidir o N e o K. Depois, num commit que atualiza a seção 6 do plano e o `K_RUN`, a run.

## A run do A0 e do B0 (2026-11-18, branch `v3-social-par-a0-run`)

- **O que rodou:** a run única, em 2026-11-18, das 15:47 às 15:54, no commit 4a2bf0ea. Foram 210 pares e 1.050 vidas, com o G-INSTR e o
  G1 em todos (D-SP-36).
- **O resultado** (`docs/RESULTADO_V3_SOCIAL_PAR_A0.md`): o A0 é ≈ 0 (D_A = −0,119 decisão, IC95 [−0,300; +0,061], δ = 4), como previsto.
  O B0 é inconclusivo por premissa, com 0 pares elegíveis. Nenhum secundário rejeita.

## S0, a observação do que os dois pets fazem juntos (2026-11-18, branch `v3-social-par-s0`)

- **O que é:** `docs/OBSERVACAO_V3_SOCIAL_PAR.md`, feita sem vida nova. As 210 VIVO da run do A0 foram refeitas e conferidas pelo sha256
  (D-SP-37).
- **O que mostra:** perto é o estado normal (64 % da vida). F volta sozinho, e P não muda o T\* em 193 de 201 pares. A bola quase nunca é
  chutada, e a CO7 muda 7 de 201.600 decisões (D-SP-40).
- **O que falta:** o checkpoint S1, a aprovação do Matheus. Depois vem o plano da S1, com a ordem proposta: B1 e depois B2.

## S1, o plano do substrato (2026-11-18, branch `v3-social-par-s1`)

- **O que é:** `docs/PLANO_ANALISE_V3_SOCIAL_PAR_S.md`, PROPOSTO. Tem os braços C, B1 (fora da casa) e B2 (a bola perto), e o G-DET com o
  `SeguidorPuro` como controle positivo. K = 200 bases independentes, e a faixa 103001…103400 (D-SP-41 a D-SP-44).
- **O que falta:** o checkpoint S2, a aprovação do Matheus, com as decisões S-1 a S-8. Depois vem o código da S2.
