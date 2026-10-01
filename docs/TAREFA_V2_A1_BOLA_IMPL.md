# TAREFA V2 — A1-BOLA, implementação (2026-10-01)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat A. Worktree e branch: `v2-a1-bola-impl`. Status: ABERTA
**condicionada**: só começa com o desenho (`docs/V2_A1_BOLA_DESENHO.md`, PR #113) aprovado pelo Matheus e mesclado.

## 1. Pergunta

1a-pet: com a bola no cenário, o comportamento do pet muda (e o dono muda a situação, não o pet), com o cuidado controlado? Nó N2
do `docs/ARQUITETURA_V2_VALIDACAO.md`; primeiro objeto do mundo com consequência.

## 2. Depende de

- #113 aprovado e mesclado (opção A: brincar com a bola no cenário conta como brincar; efeito só no humor; nenhuma rng nova; bola
  sozinha antes da L1).
- Nada da L1: a bola roda **com o aprendizado desligado** (instinto, ou lobos L0 = instinto byte a byte).

## 3. Mudança mínima

- O que o desenho define: as ações do dono `por_bola`/`tirar_bola` no fim de `AcaoUsuario` (o bandit usa `tuple(AcaoPet)`, não
  `AcaoUsuario`: confirmar no teste que a v1 reproduz), a entrada `bola` na percepção, `ConfigBola.ligada = False`, o
  `MotorAmbiente` como subclasse do `MotorEducacao`.
- **Não mexer em `digilab/policies/lobos.py`.** A regra `bola_no_cenario` e os pesos novos do lobo de decisão (desenho, seção 2.1)
  são do chat B, junto com o A1 + L1 (rodada 4). Nesta tarefa a bola entra pelo instinto, com a chave.
- **Não muda:** `engine.py`, `AcaoPet`, o bandit, runs da v1, a web (pets v12 só se a bola for para o produto: `ROADMAP_V2.md`, M8).

## 4. Experimento e gate

- Plano de análise `docs/PLANO_ANALISE_V2_A1.md` commitado **antes** de qualquer run (os gates da seção 6 do desenho).
- Sementes: calibração 6101…6505; validação 7101…7505, uma vez.
- Gates: G1 (replay); G2 (`ConfigBola.ligada = False` = vida de hoje byte a byte); 1a-pet com o "só cuidado" acoplado (D4). A
  pergunta 1a-dono é registrada como sem apoio na literatura (D6).
- GPU: não.

## 5. Entrega

- Dois PRs: (1) plano + código + calibração; (2) validação.
- `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`. Merge só pelo Matheus.

## 6. Fora desta tarefa

Bola com aprendizado (A1 + L1, chat B na rodada 4), frutas, porte para a web, corpo 2D.
