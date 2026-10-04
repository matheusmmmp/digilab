# TAREFA V2 — LOBOS-MUNDO (2026-10-04)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat B. Worktree e branch: `v2-lobos-mundo`. Status: ABERTA.

## 1. Pergunta

Infraestrutura do aprendiz, sem pesquisa: os lobos passam a **perceber** a bola e as frutas e a **escolher a fruta** pelo lobo de decisão,
para que os braços P1, P2 e P3 tenham o que aprender na condição descasado (`docs/V2_RODADA_4.md`, achado 1). Junto vai a decisão E2 do
plano do experimento maior: **o sinal do P1 inclui o humor quando a mudança vem de comer fruta.**

## 2. Depende de

Bola (#127), frutas (#132), N3 (#135) e bancada de mundos (#137) na `main`.

## 3. Mudança mínima (só o chat B mexe em `lobos.py`)

- **Percepção:** entradas `bola` e frutas no cenário (o que o `MotorAmbiente`/`MotorFrutas` já injeta na `Observacao`) entram no lobo de
  percepção.
- **Impulsos:** as regras `bola_no_cenario` e `fruta_no_cenario` do instinto (`PoliticaInstintoBola`, `PoliticaInstintoFrutas`) passam a
  ser regras dos lobos, executadas pelo mesmo código do instinto (como a L0 fez com as 7 regras de antes).
- **Decisão:** pesos novos, iniciados no prior do instinto, para essas regras e para a **sub-decisão da fruta** (qual fruta comer). Hoje ela
  sorteia pelo `incentivo` na `rng_fruta`; com os lobos, essa escolha passa a ter pesos aprendíveis, iniciados de modo que o aprendizado
  desligado dê o sorteio de hoje byte a byte.
- **E2:** `sinal_homeostatico` (ou uma variante dele, documentada) soma a variação do humor **só** quando a ação foi comer uma fruta.
  Nas outras ações, o humor continua fora, como no N3.
- **Não muda:** `engine.py`, `AcaoPet`, o bandit, a L1 e o N3 com os mundos de antes (byte a byte), a web.

## 4. Gates (sem run de pesquisa; só as sementes dos testes)

- **G2:** com o aprendizado desligado, os lobos no mundo da bola = `PoliticaInstintoBola`, e no mundo das frutas = `PoliticaInstintoFrutas`,
  byte a byte, inclusive a escolha da fruta e a `rng_fruta`.
- **G1:** replay bit a bit.
- A L0, a L1, o N3 e a bancada reproduzem como antes.
- **E2:** teste do sinal: comer fruta com efeito ruim dá sinal negativo pelo humor; as outras ações ignoram o humor.

## 5. Entrega

Um PR. `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`. O relato vai no corpo do PR.
Merge só pelo Matheus.

## 6. Fora desta tarefa

O dono informante (N5), qualquer run com faixa reservada, a revisão do teto dos pesos.
