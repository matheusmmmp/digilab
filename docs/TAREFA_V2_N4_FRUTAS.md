# TAREFA V2 — N4-FRUTAS (2026-10-01)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat A. Worktree e branch: `v2-n4-frutas`. Status: ABERTA.

## 1. Pergunta

Frutas no mundo, com nutrição e valor hedônico separados, criam escolhas do pet que a necessidade sozinha não explica, sem passar pelo
canal de cuidado? Nó N4 do `docs/ROADMAP_V2.md`: é a condição **descasado** da pergunta maior (o mundo pode contradizer a preferência inata).

## 2. Depende de

`docs/DEFINICOES_FRUTAS_V2.md` (#125; decisões F1–F11 tomadas em 2026-10-01, todas como recomendadas) e a bola (#127) na `main`.

## 3. Mudança mínima (sem aprendizado de política: o aprendiz fica desligado, como a bola sozinha)

- **Frutas como sub-decisão de comer** (F3, validação V5): o dono **oferece** (um botão por fruta no fim de `AcaoUsuario`, como os treinos
  e a bola); parte das ofertas com pelo menos duas frutas ao mesmo tempo; o pet escolhe ao comer. `AcaoPet` não muda; `alimentar` continua a
  ração de cuidado. Estender o `MotorAmbiente` (`digilab/ambiente.py`).
- **Dois registros por fruta** (F1): `incentivo` (antes de comer) e `avaliacao` (depois); registros derivados, reconstruídos pelo replay.
  Nomes e falas só operacionais (F2): nada diz que o pet sente prazer.
- **Saciedade sensório-específica:** a `avaliacao` de **uma** fruta cai com o consumo recente dela, sem passar pela fome (definição 3 do
  documento).
- **Genoma:** preferência inata por fruta (F5) e neofobia como gene próprio (F4), com rng própria, fora do `Temperamento`.
- **Efeito:** nutrição separada do gosto; o efeito ruim no **humor**, fora de `em_privacao` (F6); só o efeito imediato.
- **Orçamento do dono:** ofertas de fruta seguem as decisões da bola: fora do sorteio do dono aleatório e fora do orçamento (B1, B2).
- **Não muda:** `engine.py`, `AcaoPet`, o bandit, `lobos.py` (é do chat B), a bola desligada, a web. Vício fica fora (N9, F9).

## 4. Experimento e gate

- Plano `docs/PLANO_ANALISE_V2_N4.md` commitado **antes** de qualquer run.
- Sementes: calibração **10101…10505**; validação **11101…11505**, uma vez.
- Gates (PROPOSTOS): G1, G2 (chave desligada = vida de antes, byte a byte); os dois registros se separam (a escolha não é função só da fome);
  a saciedade específica aparece sem mudar a fome; o critério ensino × cuidado do documento (F7: "só cuidado" acoplado **com as mesmas
  ofertas**, sem diferença de saúde e mortes).
- Falha é registrada e não para a V2.

## 5. Entrega

Dois PRs. `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`. Merge só pelo Matheus.

## 6. Fora desta tarefa

Aprender preferência pela consequência (vem com o N3 no experimento maior), vício (N9), números de balanceamento do produto, a web.
