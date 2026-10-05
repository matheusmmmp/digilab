# TAREFA V2 — BANCADA-LIGA-N6-N7 (2026-10-05)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat D. Worktree e branch: `v2-bancada-liga-n6-n7`. Status: ABERTA.
Fecha a etapa C3 do `docs/ROADMAP_V2.md`: o cérebro (PR #167) e o mundo do pedido (PR #166) já estão na `main`.

## 1. Mudança mínima (só `experiments/bancada_v2.py` e `digilab/metrics.py`)

A lista que o próprio D deixou no #165:
- tirar o N6 e o N7 de `NOS_PENDENTES`;
- **N6:** M0, MR, MT e ME montados por cima do ponto (`cfg_lobos_do_ponto`) com as chaves `memoria_*` de `ConfigLobos`; o ME com
  `memoria_permutacao = desarranjo_n6(semente)` por vida;
- **N7:** P0+ped, P1+ped e P3+ped com `DonoPedinte.da_semente(semente, CONFIG_PEDIDO_LIGADA, bronca=...)` (bronca só no P3+ped), a
  `ConfigPedido` ligada no motor e `w0_pedido` no cérebro; os pedidos (e as broncas do pedido) **fora do orçamento**, em `FORA_DO_ORCAMENTO`;
  `contar_acoes` não os conta;
- `sem_ensino` e os filtros `sem_pedido`/`sem_ensino_sem_pedido` tiram os pedidos e as broncas (plano do N7, 4.2);
- as medidas do #165 lendo as sondas que o cérebro grava no motivo/estado interno (memória e pedido).

**Não muda:** `engine.py`, `lobos.py`, `frutas.py`, a web. O K4 (chat A) e os canais (chat B) chegam na rodada 10; deixe só o lugar.

## 2. Gates (só as sementes dos testes)

- G1 de toda vida dos braços novos e dos acoplados.
- Braços antigos byte a byte (as vidas de hoje, por gabarito gravado antes).
- M0 = P0 nas decisões; o pedido não muda o orçamento do dono; o `sem_ensino` do P3+ped tira pedidos e broncas e guarda as ofertas.
- As medidas do N6 e do N7 saem de uma vida real (não só sintética) com valor finito.
- Fumaça não canônica com os blocos N6 e N7 (sem artefato).

## 3. Entrega

Um PR, relato no corpo. Suíte inteira. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`. Merge só pelo Matheus. Próximo para o D
(rodada 10): ligar o K4 e os canais, depois o cérebro B (CfC/A2C).
