# TAREFA V3 — LONGE_GEOMETRIA (2026-11-13)

Coordenador: Gerente da V3. Worker: Claude Code (sessão do Matheus, Opus 5.5). Worktree e branch: `v3-longe-geometria`. Status: ABERTA.

Categoria: arquitetura. Origem: Matheus, 2026-11-13: a regularidade do longe separada da geometria (lado e ancora), pedida pelo Matheus em 2026-11-13 depois das auditorias externas.

## 1. Pergunta

O ganho da memória do modular no `longe_fixo` (C1: M3\* − M2 +0,0489; C4: REL − SEM +0,0646) vem de a ração voltar aos mesmos lugares (a regularidade) ou de onde e a partir de onde ela é posta (o lado leste e a âncora no comedouro)? É a ressalva da geometria da A6.2 (`docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`), que nenhuma run separou. Trilha C (cérebro) do `docs/PLANO_V3.md`.

## 2. Depende de

- As runs da C1 (71101…71505) e da C4 (77101…77505), já na `main`: a variância do poder vem delas.
- As decisões LG-1 a LG-8 do plano (seção 9) e a faixa confirmada pelo coordenador.

## 3. Mudança mínima

Esta etapa (este PR) só registra o plano e a tarefa: `docs/PLANO_ANALISE_V3_LONGE_GEOMETRIA.md` (PROPOSTO) e este arquivo. Nenhum código.

A etapa de código, depois das decisões: o estilo `longe_ancora` e o rótulo `longe_um` no `DonoComLugar` (`digilab/mundo.py`, `digilab/config.py`), com o gabarito dos estilos; o orquestrador `experiments/run_v3_longe_geometria.py`; o script `experiments/poder_longe_geometria.py`.

Não muda: o `engine.py`, o motor, o corpo, o mundo, o cheiro, o A, o cérebro modular, os estilos que já existem (byte a byte) e o jogo web.

## 4. Experimento e gate (se houver run)

- Plano de análise: `docs/PLANO_ANALISE_V3_LONGE_GEOMETRIA.md`, commitado antes da run.
- Sementes reservadas: sem calibração; a run única na faixa proposta 93101…93505, a confirmar com o coordenador.
- Métrica e gate: a taxa de fechamento por episódio; os primários I-M3 e I-PAD (a interação do ganho da memória entre o `longe_fixo` e o `longe_ancora`), com Holm; K = 150 e δ pelo script de poder (cerca de 0,027 pela conta de bolso). Todos PROPOSTOS.
- GPU: não. CPU, 4 processos, cerca de 2 h 20 a 3 h 30 para 9 600 vidas.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2). **Não edite o índice
  `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge. Um conflito nele se resolve
  rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

Separar o lado da âncora (pede um mapa maior); o teste causal das idas da D-C1-3; qualquer mudança no jogo; a comparação com o A.

## 7. Critérios de aceitação

- Esta etapa: o plano e esta tarefa existem na `main`, com o status PROPOSTO, e os links resolvem.
- A etapa de código: o teste da construção do `longe_ancora` (a mesma distribuição de um ponto do `longe_fixo`) e o gabarito dos estilos passam; o `artifacts_v3_longe_geometria/poder.json` existe.
- A run: o `meta.json` com o G1 em todas as vidas e o `RESULTADO_V3_LONGE_GEOMETRIA.md` com cada número ligado ao artefato.

## 8. Precisa do Matheus

As LG-1 a LG-8 do plano (seção 9), cada uma com a recomendação e o custo de errar.
