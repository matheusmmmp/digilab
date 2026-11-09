# TAREFA V3 — DESEMPENHO (2026-11-08)

Coordenador: o Gerente da V3 (sessão do Claude Code). Worker: Claude Code, Opus 5.5. Worktree e branch: `v3-desempenho-perfil`. Status:
ENTREGUE (PR aberto, sem merge).

Categoria: implementacao. Origem: Claude Code, 2026-11-08. O Gerente da V3 pediu, para o Matheus, que se medisse onde vai o tempo das
runs e se testassem o PyPy, o NumPy/Polars e o orjson/msgspec.

## 1. Pergunta

Onde vai o tempo de uma run de pesquisa (o motor e o mundo, o cérebro, o corpo, o JSON e o gzip dos logs, as métricas e a análise)? E vale
a pena usar (1) o PyPy, (2) o NumPy ou o Polars só na análise, ou (3) o orjson ou o msgspec na leitura dos logs? Não vem de uma hipótese
da pesquisa: é infraestrutura.

## 2. Depende de

Nada na `main`. O download do PyPy, do orjson e do msgspec precisava da autorização do Matheus, que foi dada na sessão em 2026-11-08,
numa pasta própria e sem mexer no PATH.

## 3. Mudança mínima

- **O que muda:**
  - o script de medição `experiments/medir_desempenho_perfil.py`;
  - os artefatos em `artifacts_v3_desempenho/`;
  - o relatório `docs/DESEMPENHO_PERFIL_2026-11.md`;
  - uma linha na lista de donos do `tests/test_memoria_autobio.py`, porque o script importa o orquestrador da C4.
- **O que NÃO muda:** o `digilab/` (inclusive o `engine.py`), os orquestradores, os gabaritos e as regras.

## 4. Experimento e gate (se houver run)

Não há run de pesquisa. Só vidas das sementes dos testes (101…505), uma medição por vez, sem gate.

## 5. Entrega

- Testes: `python -m pytest tests/test_memoria_autobio.py -q`, e a suíte inteira no CPython e no PyPy, em
  `artifacts_v3_desempenho/suite_*.txt`.
- Registro: a seção de 2026-11-08 no fim de `docs/registro/2026-11.md`.
- O PR vai contra a `main`, com o corpo no modelo do relato. Sem merge.

## 6. Fora desta tarefa

- implementar qualquer uma das três opções;
- consertar o `_idx` e o `quantil_t` da análise;
- trocar o `sum()` do `metrics.py`;
- mexer nas falhas da suíte que já estavam na `main`.

## 7. Critérios de aceitação

- O `docs/DESEMPENHO_PERFIL_2026-11.md` existe, e cada número dele cita um artefato em `artifacts_v3_desempenho/` ou o `meta.json` da
  C4.
- O `python experiments/medir_desempenho_perfil.py <modo> ...` refaz cada artefato.
- O `tests/test_memoria_autobio.py` não acusa o script novo.

## 8. Precisa do Matheus

As três recomendações e o achado do `sum()` estão na seção 7 e na seção 8 do relatório, com o custo de errar de cada uma:
- (1) adotar ou não o PyPy;
- (2) adotar ou não o NumPy/Polars;
- (3) adotar ou não o orjson/msgspec;
- (4) fixar o CPython ≥ 3.12 ou trocar o `sum()` por `math.fsum`.

## Resultado

O tempo está na simulação e no replay G1. O log e as métricas pesam menos de 3 % de uma vida, e a análise 0,2 % de uma run.

- **O PyPy:** 1,72× mais rápido, com o log e o estado iguais nas 5 sementes; só as medidas mudam no último dígito, por causa do
  `sum()`. 36 testes falham só no PyPy.
- **A recomendação:** não adotar nenhuma das três agora (PROPOSTO). Detalhes e números em `docs/DESEMPENHO_PERFIL_2026-11.md`.
