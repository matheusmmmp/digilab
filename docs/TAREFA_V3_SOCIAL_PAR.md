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
