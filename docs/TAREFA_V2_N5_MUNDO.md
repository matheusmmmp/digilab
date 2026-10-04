# TAREFA V2 — N5-MUNDO (2026-10-04)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat A. Worktree e branch: `v2-n5-mundo`. Status: ABERTA.

## 1. Pergunta

Infraestrutura do mundo para o N5 (dono informante, braços P2 e P2e): o dono passa a poder **informar** sobre uma fruta (por exemplo,
"esta faz bem" ou "esta faz mal"), e o mundo registra isso. Junto vai a medida nova da saciedade (decisão N1).

## 2. Depende de

Frutas (#132) na `main`. O desenho fino do N5 é do chat C (`docs/TAREFA_V2_N5_PLANO.md`). Combinar com ele os nomes dos eventos antes do
código; se o plano do C ainda não existir, use o mínimo abaixo e registre como provisório.

## 3. Mudança mínima (só o chat A mexe em `ambiente.py` e `frutas.py`)

- **Evento de informação do dono** no fim de `AcaoUsuario`, com a fruta e o sinal (certo ou errado decidido pelo braço, não pelo
  evento). Informar **não é cuidado nem reforço**: não mexe no estado nem chega ao aprendiz como sinal (D-A da arquitetura). Ele só fica
  disponível para a **percepção**, por uma janela de tempo.
- **Fora do orçamento**, pelo mesmo canal das ofertas de fruta (B2), para não deslocar o cuidado.
- **Dono informante** (sintético): informa certo (P2) ou errado (P2e) sobre o efeito real da fruta, com a mesma frequência nos dois.
- **N1:** em `digilab/metrics.py`, a medida da saciedade sensório-específica com o termo da preferência inata (ou a queda da avaliação
  por fruta), para o próximo plano. Teste com dados sintéticos; nenhuma releitura dos dados gravados.
- **Não muda:** `engine.py`, `AcaoPet`, `lobos.py` (chat B), as vidas da bola e das frutas com o evento desligado, a web.

## 4. Gates (sem run de pesquisa)

G1 replay; G2 (sem evento de informação no log = vida das frutas de hoje, byte a byte); o evento não altera o estado nem o orçamento
(teste); a medida N1 recupera, em dados sintéticos, uma queda específica conhecida sem confundir com a preferência inata.

## 5. Entrega

Um PR. `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`. Relato no corpo do PR.
Merge só pelo Matheus.

## 6. Fora desta tarefa

A percepção da informação pelos lobos (chat B, rodada 6), qualquer run com faixa reservada, a web.
