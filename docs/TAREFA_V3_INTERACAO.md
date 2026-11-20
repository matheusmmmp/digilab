# TAREFA V3 — INTERACAO (2026-11-12)

Coordenador: a sessão do Matheus. Worker: Claude Code. Worktree e branch: `v3-interacao`. Status: o plano ENTREGUE (PR); as etapas IT1 a IT7 abrem cada uma com a sua espec.

Categoria: documentacao. Origem: Matheus, 2026-11-12: o Matheus pediu a interação direta no mapa, o arco de comandos e uma entrada sem pausa, e decidiu as IN, EN e TU pela recomendação (2026-11-12).

## 1. Pergunta

Não é pesquisa: é o plano de produto da interação direta (o gesto no mundo, o arco de comandos e a entrada sem pausa), em [`PLANO_V3_INTERACAO.md`](PLANO_V3_INTERACAO.md).

## 2. Depende de

As decisões IN-1 a IN-8, EN-1 a EN-8 e TU-1 a TU-9 (Matheus, 2026-11-12, pela recomendação). A IT7 depende da loja (MO3 do plano da moeda).

## 3. Mudança mínima

Neste PR, só documentos. Nada muda no código, no motor, no `engine.py` nem nos pets.

## 4. Experimento e gate (se houver run)

Sem run: é só jogo web.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2). **Não edite o índice
  `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge. Um conflito nele se resolve
  rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

Todo código; a luta (sem botão, LP-3 e LP-10); o Python.

## 7. Critérios de aceitação

O plano existe e os links relativos resolvem (`tools/verificar_relato.py`, categoria documentacao).

## 8. Precisa do Matheus

Nenhuma neste PR. Os números (tempos do anel, janelas, o presente do Rookie) ficam PROPOSTOS para a rodada de equilíbrio.
