# TAREFA V2 — A1-BOLA, desenho (2026-10-01)

Coordenador: chat "Principais jogos Digimon com diálogo" (coordenação da V2). Worker: o mesmo da F0-INVENTARIO (chat A), **depois** da F0-LIMPEZA.
Worktree e branch: `v2-a1-bola`. Status: ABERTA.

## 1. Pergunta

Como entra a **bola** como interação mínima com consequência da fase 1a (decisão do Matheus, 2026-10-01, a partir de `docs/V2_INVENTARIO_JOGO.md`), sem
mudar a canônica e com a consequência fora da cadeia que leva à morte? Hipótese H1, alavanca 1a do `docs/PLANO_V2_PESQUISA.md`.

## 2. Depende de

PR #106 (inventário) e a F0-LIMPEZA na `main`.

## 3. Mudança mínima — **só desenho nesta tarefa**

Entrega `docs/V2_A1_BOLA_DESENHO.md` e para. Sem código. Conteúdo:
1. O que o pet percebe (a bola posta pelo dono), o que decide (perseguir, ignorar, …), a consequência (no humor ou outro canal fora de
   fome/higiene/energia → saúde → morte) e o que o dono muda (onde e quando a bola aparece).
2. **A restrição achada no inventário:** uma ação nova não pode entrar em `events.AcaoPet` sem mudar a canônica (braço do bandit, `ORDEM_TRACOS`, sondas).
   Propor como a decisão da bola entra sem isso (por exemplo, um evento e uma escolha numa camada por cima, como o `MotorPersonalidade`), com prós e contras.
3. Eventos novos no log, determinismo, RNG própria se houver sorteio, replay.
4. Como a 1a roda **sozinha** (com o instinto ou a `PoliticaLobos` sem aprendizado) e depois junto com a L1, sem duas alavancas no mesmo braço antes de cada
   uma passar.
5. Web: pets **v12** (reservado), o que muda na tela (só o necessário).
6. Gates da 1a (os G1–G6 do plano) e o que o plano de análise vai precisar.
7. Recomendação em 3 frases e a pergunta ao Matheus para aprovar o desenho.

## 4. Experimento e gate

Sem run nesta tarefa. A implementação vira tarefa própria depois da aprovação do desenho.

## 5. Entrega

PR contra a `main` só com o documento. Aviso ao coordenador. Merge só pelo Matheus.

## 6. Fora desta tarefa

Implementar; comida posta; corpo 2D completo; outras interações.
