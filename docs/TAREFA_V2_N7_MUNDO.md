# TAREFA V2 — N7-MUNDO (2026-10-05)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat A. Worktree e branch: `v2-n7-mundo`. Status: ABERTA.

## 1. Pergunta

O lado do mundo do N7 (`docs/PLANO_ANALISE_V2_N7.md`, N7-1 a N7-10 aprovadas em 2026-10-05): o dono pode **pedir** "deixe a fruta X".

## 2. Mudança mínima (só `events.py` no fim do enum, `frutas.py`/`ambiente.py`, `policy.py` no campo novo)

- **Evento de pedido** "deixe a fruta X", novo e separado da informação do N5 (N7-1), **fora do orçamento** e sem mexer no estado.
- **Percepção:** campo novo na `Observacao` com o pedido vigente, com padrão neutro e injetado só pelo `MotorFrutas`, como `info_frutas`.
- **Dono que pede** (sintético): a fruta X sorteada por vida, independente da preferência inata, por rng própria (N7-6); pedidos nos dias
  1–10 e extinção nos dias 11–14 (N7-7); a bronca da desobediência só no braço P3+ped, fora do orçamento, no primeiro passo do dono depois do
  consumo (N7-8).
- **Não muda:** `engine.py`, `AcaoPet`, `lobos.py` (chat B), a bancada (chat D), as vidas de hoje.

## 3. Gates (sem run de pesquisa)

G1; G2 (sem pedido no log = vida de hoje, byte a byte, por gabarito gravado antes da mudança, como no #154); o pedido não altera o estado nem
o orçamento; as fases e o sorteio da fruta conferidos por teste; a rng do pedido não mexe nas outras.

## 4. Entrega

Um PR, com o relato no corpo. `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`. Merge só
pelo Matheus.
