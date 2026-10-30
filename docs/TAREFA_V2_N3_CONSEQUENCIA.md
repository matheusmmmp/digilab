# TAREFA V2 — N3-CONSEQUENCIA (2026-10-01)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat B. Worktree e branch: `v2-n3-consequencia`. Status: ABERTA.

## 1. Pergunta

O mesmo aprendiz da L1, recebendo como sinal só a **consequência da própria ação** (o valor homeostático), aprende a cuidar de si melhor
do que a predisposição herdada? É o braço **P1** da pergunta maior (`docs/PLANO_V2_PESQUISA.md`, seção 2; nó N3 do `docs/ROADMAP_V2.md`).

## 2. Depende de

L1 (#119, #123) e bancada (#126) na `main`. Nada mais.

## 3. Mudança mínima

- **Fonte `consequencia` na bancada** (`experiments/bancada_v2.py`, hoje `NotImplementedError`): o braço P1 entrega ao aprendiz um sinal
  calculado da transição que ele já recebe em `observar` (`observacao` → `observacao_seguinte`). O motor mede essa transição logo depois
  do efeito da ação do pet, **antes** do tempo passar e de qualquer ação do dono (`engine._avancar`; validação V2 do roadmap), então o
  sinal não tem o cuidado do dono misturado. Nada do dono chega ao P1.
- **O sinal (desenho no plano de análise, antes da run):** redução do déficit homeostático pela própria ação (Keramati e Gutkin,
  `10.7554/elife.04811`, VERIFICADA). Decidir e justificar no plano: quais drives entram (a fome, a higiene e a energia; o humor fica
  fora, por ser o canal da bola e o do efeito ruim das frutas, F6), a forma (diferença de uma distância ao ponto de ajuste) e **a janela
  de crédito** (só o efeito imediato, como na L1, é o mínimo; consequência atrasada é variante declarada).
- **A regra de atualização é a da L1**, sem mudança (`lobos.Aprendiz._aplicar_sinal`): só a fonte do sinal muda. Se precisar de um gancho
  em `lobos.py` para um sinal que não vem do dono, ele é seu (só o chat B mexe em `lobos.py`).
- **Não muda:** `engine.py`, `AcaoPet`, o bandit, a L0, a L1 (P3 continua byte a byte), a web.

## 4. Experimento e gate

- Plano `docs/PLANO_ANALISE_V2_N3.md` commitado **antes** de qualquer run.
- Braços na bancada: P0 (herdado), **P1**, P3 (referência da L1), e o "só cuidado" acoplado; mundo `padrao`; donos da L1.
- Sementes: calibração **8101…8505**; validação **9101…9505**, uma vez.
- Medidas (já na bancada): `desempenho_no_ambiente` (tempo fora de privação, saúde), `custo_da_plasticidade`, mortes, G4 do aprendido, G6.
- Gates (PROPOSTOS): P1 reduz a privação em relação ao P0 com IC fora de zero; **sem mortes novas**; G6 (nenhum peso preso no teto); G1 e
  G2 (com a fonte desligada, a vida é a do P0 byte a byte).
- Pela decisão de 2026-10-01, uma falha é registrada e não para a V2.

## 5. Entrega

Dois PRs (plano + código + calibração; validação). `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do
`docs/REGISTRO_DESVIOS.md`. Merge só pelo Matheus.

## 6. Fora desta tarefa

P2/P2e (N5), frutas (N4), vários canais de reforço (H-R2), o experimento maior, a web.
