# TAREFA V2 — BANCADA-N5 (2026-10-04)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat D. Worktree e branch: `v2-bancada-n5`. Status: ABERTA. **Fazer
primeiro na rodada 6: destrava o chat B.**

## 1. Pergunta

Infraestrutura: a bancada passa a criar os lobos **vendo o mundo** (bola e frutas, #141) e ganha os braços do N5 (P2, P2e, P2a), para o
N5 e o experimento maior rodarem sem orquestrador novo.

## 2. Depende de

#140, #141 e #144 na `main` (já estão).

## 3. Mudança mínima (só `experiments/bancada_v2.py` e, se precisar de medida, `digilab/metrics.py`)

- **Lobos com o mundo:** nos mundos da bola e das frutas, a bancada passa `cfg_bola`/`cfg_frutas` à `PoliticaLobos` (#141). No mundo padrão,
  nada muda. Os gates antigos da bancada continuam passando; onde a vida muda porque os lobos agora veem o mundo, o teste novo diz isso.
- **Fonte `informacao`** (hoje `NotImplementedError`): P2 (o `DonoInformante` certo), P2e (errado) e P2a (acoplado, do chat A,
  `docs/TAREFA_V2_N5_ACOPLADO.md`), com as ofertas do `CalendarioFrutas` (decisão do coordenador no plano do N5). A informação chega à
  percepção pelo `MotorFrutas`; nunca pelo `receber_acao_dono`. A consequência (P1 com a E2) continua sendo o único reforço.
- **Medidas do N5** que o plano pede (consumos até a metade do caminho, `taxa_fruta_ruim` nas janelas inicial e final) prontas na tabela
  braço × condição.
- **Não muda:** `engine.py`, `lobos.py` (chat B), `ambiente.py`/`frutas.py` (chat A), a web.

## 4. Gates (sem run de pesquisa; só as sementes dos testes)

G1 de toda vida nova; aprendizado desligado nos mundos das frutas = instinto das frutas byte a byte pela bancada; P2 sem nenhuma informação
no registro = P1 byte a byte (G2 do plano do N5); P2 e P2e com informações nos mesmos ticks; o aprendiz nunca recebe a informação como sinal
(espião, como no #140).

## 5. Entrega

Um PR, com o relato no corpo. `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`.
Merge só pelo Matheus.
