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
