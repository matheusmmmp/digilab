# TAREFA V2 — INFRA_PREFIXO_V3 (2026-10-30)

Coordenador: Gerente. Worker: Claude Code (Sonnet 5.5). Worktree e branch: `v3-infra-prefixo` (de `origin/main` `b3643bb`). Status: ENTREGUE.

Categoria: implementacao. Origem: Matheus, 2026-10-30: decisão V3-D1 (docs/PLANO_V3.md, PR #476): os documentos novos usam o prefixo V3, e o CI e as ferramentas têm de aceitá-lo.

Esta tarefa usa o prefixo V2 de propósito: o CI da `main` ainda só aceita `TAREFA_V2_*`. É a última tarefa criada assim.

## 1. Pergunta

Nenhuma hipótese de pesquisa: é infraestrutura. Uma `docs/TAREFA_V3_*.md` ou um `docs/PLANO_ANALISE_V3_*.md` reprova hoje no `tools/verificar_relato.py`, e as
ferramentas que geram ou listam tarefas só conhecem a V2. A V3-D1 manda que os documentos novos usem o prefixo V3 e que os V3 antigos do
repositório fiquem como estão.

## 2. Depende de

A V3-D1, aprovada pelo Matheus em 2026-10-30 (`docs/PLANO_V3.md`, seção 6.1, no PR #476, ainda sem merge). Este PR não depende do #476 para
passar no CI.

## 3. Mudança mínima

- `tools/verificar_relato.py`: o campo Tarefa aceita `docs/TAREFA_V2_*.md` ou `docs/TAREFA_V3_*.md`; a categoria experimento aceita
  `docs/PLANO_ANALISE_V2_*.md` ou `docs/PLANO_ANALISE_V3_*.md`. A mensagem de erro cita os dois.
- `docs/modelos/TAREFA_V3_MODELO.md`: cópia do modelo V2 com V3 no lugar de V2.
- `tools/nova_tarefa.py`: a opção `--fase {V2,V3}` (padrão V2) escolhe o modelo, o prefixo do arquivo e o branch.
- `tools/gerar_estado_atual.py`: lista também `TAREFA_V3_*` e `PLANO_ANALISE_V3_*`. Sem nenhum arquivo V3, a saída é a de hoje, byte a byte.
- `.github/pull_request_template.md`: os campos Tarefa e Branch aceitam V2 ou V3.
- Os testes `tests/test_infra_*` dessas ferramentas ganham casos V3; nenhum caso V2 muda.

**Não muda:** `CLAUDE.md` (V3-D7, PR próprio), `digilab/`, `experiments/`, `web/`, o modelo V2, nenhum `TAREFA_V2_*.md`. Nada é renomeado.

## 4. Experimento e gate (se houver run)

Não há run.

## 5. Entrega

- Testes: `python -m pytest tests/test_infra_verificar_relato.py tests/test_infra_nova_tarefa.py tests/test_infra_estado_atual.py -q`.
- Registro: seção no fim de `docs/registro/2026-10.md` e linha no fim de `docs/REGISTRO_DESVIOS.md`.
- PR contra a `main` com o relato no corpo. Merge só pelo Matheus.

## 6. Fora desta tarefa

Regenerar o `docs/ESTADO_ATUAL.md` (o da `main` já está defasado em relação ao gerador, por causa de PRs anteriores); a atualização do
`CLAUDE.md` (V3-D7); o glossário V2/V3 (V3-D1, vem com o `PLANO_V3`).

## 7. Critérios de aceitação

- Uma `docs/TAREFA_V3_*.md` que existe passa em `a tarefa existe`; uma que não existe reprova (teste em `tests/test_infra_verificar_relato.py`).
- Um plano `PLANO_ANALISE_V3_*` é aceito na categoria experimento (mesmo arquivo de teste).
- `nova_tarefa.py INFRA --fase V3 ...` cria `TAREFA_V3_INFRA.md` no branch `v3-infra` (`tests/test_infra_nova_tarefa.py`).
- `gerar_estado_atual.py` sem arquivo V3 gera o mesmo arquivo de antes (conferido por `cmp` antes e depois da mudança, e por teste dos títulos).
- Os casos V2 dos testes passam sem alteração.

## 8. Precisa do Matheus

Nenhuma decisão. O merge.

## Resultado (2026-10-30)

Entregue no PR desta tarefa; o relato completo está no corpo do PR.
