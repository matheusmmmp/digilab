# TAREFA V2 — BANCADA (2026-10-01)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat D. Worktree e branch: `v2-bancada`. Status: ABERTA
(começa depois de o D fechar o conflito do #115).

## 1. Pergunta

Infraestrutura, não pesquisa: um orquestrador único para os braços da pergunta maior (`docs/ARQUITETURA_V2_VALIDACAO.md`, seção
6): P0 (só herdado), P1 (só consequências), P2/P2e (ensino contextual certo/errado), P3 (feedback explícito), todos sobre **o
mesmo aprendiz**, em que só a **fonte do sinal** muda (validação V1 do `docs/ROADMAP_V2.md`). Sem ela, cada nó montaria o próprio
orquestrador e os braços deixariam de ser comparáveis.

## 2. Depende de

- Nada para começar. Para ligar o P3 de verdade, a L1 mesclada (chat B). Até lá, a bancada roda o P0 e um P3 "de teste" pela
  interface do `Aprendiz`, sem mexer em `lobos.py`.

## 3. Mudança mínima

- `experiments/bancada_v2.py` (nome PROPOSTO): monta vida = (genoma, mundo, dono, braço, semente), com as rngs de ambiente,
  política e dono separadas, como hoje.
- **Fonte de sinal como parâmetro do braço:** `nenhuma` (P0), `consequencia` (P1, chega no N3), `informacao` (P2/P2e, chega no
  N5), `dono` (P3). Nesta tarefa só `nenhuma` e `dono` funcionam; as outras levantam `NotImplementedError` com o nó que as
  implementa.
- **Modo acoplado** (malha aberta), generalizando `log_so_cuidado`/`vidas_acopladas` de `experiments/run_v2_l1.py`: reproduzir o
  registro de eventos de uma vida em outro braço ou outro cérebro.
- **Métricas da pergunta maior** em `digilab/metrics.py` (uma vez só): desempenho no próprio ambiente (tempo fora de privação,
  saúde média, acerto na tarefa reaproveitando `acerto_na_tarefa`), custo da plasticidade (deriva ao prior, tempo até metade do
  caminho), e a tabela braço × condição.
- **Não muda:** `engine.py`, `lobos.py` (é do chat B), o bandit, runs da v1, a web.

## 4. Gate (sem run de pesquisa)

- **P0 = instinto byte a byte** pela bancada (mesmos testes de G2 da L0).
- **Acoplado reproduz:** a vida acoplada com o sinal desligado é byte a byte a vida de origem com os sinais retirados.
- Replay bit a bit de toda vida da bancada (G1).
- Sementes: só as dos testes (101…505). Nenhuma run com faixa reservada.

## 5. Entrega

- `python -m pytest tests/ -q` inteiro.
- Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`.
- PR contra a `main`. Merge só pelo Matheus.

## 6. Fora desta tarefa

Os sinais de consequência (N3) e de informação (N5), os modos casado/descasado/mutável (rodada 4), qualquer cérebro além dos
lobos, a comparação N11.
