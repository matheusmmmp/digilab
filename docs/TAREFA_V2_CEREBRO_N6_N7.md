# TAREFA V2 — CEREBRO-N6-N7 (2026-10-05)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat B (dono de `lobos.py`). Worktree e branch:
`v2-cerebro-n6-n7`. Status: ABERTA. Etapa C1 do `docs/ROADMAP_V2.md` (revisão 3).

## 1. O que muda na estratégia

Decisão do Matheus (2026-10-05): **montar tudo, calibrar junto, validar uma vez.** A calibração e a validação do N5 **não rodam**
(a nota `a810d03` na branch `v2-n5-calibracao` fica como registro; a faixa 13101…13505 fica intacta). Esta tarefa é só
construção, com testes de mecanismo.

## 2. Mudança mínima (só `lobos.py` e `config.py`)

- **N6, memória** (`docs/PLANO_ANALISE_V2_N6.md`, N6-1 a N6-10): episódios de consumo de fruta com a valência do humor, nos espaços
  (4 + 2, 12 h, desempate da seção 2.1), sem decaimento contínuo, sem relembrar (N6-4); a memória entra **só** na escolha de qual
  fruta, com ganho `g` < S (N6-1); a sonda contrafactual (a mesma decisão com a memória zerada e o mesmo `u`) registrada no estado
  interno. Atrás de chave; ganho padrão 0.
- **N7, arbitragem** (`docs/PLANO_ANALISE_V2_N7.md`, N7-1 a N7-10): a entrada do pedido do dono (campo do chat A, `TAREFA_V2_N7_MUNDO.md`;
  se ainda não estiver na `main`, deixe a leitura pronta atrás da chave e combine o nome com o A) na decisão de comer (`fome_moderada`,
  `fruta_no_cenario`) e na escolha da fruta, com um peso compartilhado e `w0_pedido` configurável (N7-2, N7-4); as regras urgentes não
  leem o pedido (N7-3). Atrás de chave; `w0_pedido` padrão 0.
- **Não muda:** `engine.py`, `AcaoPet`, o bandit, o mundo (A), a bancada (D), a web.

## 3. Gates (mecanismo; só as sementes dos testes; nenhuma faixa reservada)

- G1 replay, inclusive o estado interno com memória e pedido.
- Chaves desligadas (ou ganho 0, `w0_pedido` 0) = vida de hoje byte a byte, por gabarito gravado antes da mudança (como no #154).
- Memória: um episódio ruim recente com a fruta X baixa a chance de escolher X **só** quando a memória está ligada; a sonda contrafactual
  reproduz a decisão sem memória.
- Arbitragem: com pedido vigente, a decisão urgente não muda (G-URG); na fome moderada, o pedido pesa na medida do `w0_pedido`.

## 4. Entrega

Um PR, com o relato no corpo. `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`.
Merge só pelo Matheus. Próximo para o B (rodada 9): canais de reforço (C4), depois a calibração conjunta (K2).
