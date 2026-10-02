# Resultado — V2, A1: a bola sem aprendizado (validação única, 2026-10-01)

Plano `docs/PLANO_ANALISE_V2_A1.md` (commitado antes de qualquer run); desenho `docs/V2_A1_BOLA_DESENHO.md` (opção A, #113); calibração no
PR #127 (`artifacts_v2_a1/calibracao/`). Validação: sementes **7101…7505, uma vez**, no ponto da calibração (duração 120 min, ganho 0,15,
`w_bola` 6; `experiments/configs/v2_a1/validacao.json`). Números de `artifacts_v2_a1/validacao/` (`resultado.json`, `pet.json`,
`sembola.json`, `so_cuidado.json`, `meta.json`). Nada mudou por causa da validação.

## Gates

| gate | critério | resultado | leitura |
|---|---|---|---|
| G1 replay | vida bit a bit pelo log | **passa** (o orquestrador conferiu as 120 vidas e as 10 do acoplado; `tests/test_ambiente.py`) | — |
| G2 equivalência | desligado = motor de hoje, byte a byte | **passa** (`tests/test_ambiente.py`: (a) V3, (b) instinto da v1, (c) ligado sem bola) | — |
| **1a-pet** | limite inferior do IC de Δp > 0 | **PASSA**: Δp **+0,310 [+0,245; +0,375]** (por semente +0,336, +0,423, +0,268, +0,317, +0,208) | com a bola no cenário o pet brinca mais; o controle sem o instinto ver a bola fica em +0,036 [−0,025; +0,107] |
| **cuidado controlado** | mortes 0 e IC da privação contendo 0 | **FALHA**: privação bola − sem bola **+0,017 [+0,009; +0,028]**; mortes 0 | ver abaixo: é o orçamento do dono aleatório, não o pet |
| 1a-dono | — | **não testada** (sem apoio na literatura, D6; exige o aprendiz, A1 + L1) | — |

## Por que o cuidado controlado falha

| dono | privação sem bola | com bola | com bola que o pet não vê | bolas por vida | alimentar (sem → com) | limpar (sem → com) |
|---|---|---|---|---|---|---|
| atencioso | 0,000 | 0,000 | 0,000 | 56,0 | 37,0 → 37,0 | 47,6 → 49,0 |
| relapso | 0,088 | 0,088 | 0,088 | 1,4 | 42,0 → 42,0 | 42,0 → 42,0 |
| aleatório | 0,266 | 0,333 | 0,334 | 34,2 | 40,6 → 33,4 | 39,4 → 33,8 |
| incoerente | 0,000 | 0,000 | 0,000 | 56,0 | 37,0 → 37,0 | 48,6 → 48,6 |

(`pet.json` e `sembola.json`, médias de 5 vidas por dono.) Toda a diferença vem do **aleatório**: ele sorteia `por_bola` entre 7 ações e,
com o orçamento fixo de 224, cada bola toma o lugar de uma ação qualquer, inclusive alimentar e limpar. O braço em que o pet não vê a bola
tem a mesma privação, então não é o brincar do pet. Nos donos coerentes a privação fica em zero e a bola (56 por vida) desloca o ensino:
elogios 93,0 → 61,4 e broncas 46,0 → 20,0 no atencioso; 72,2 → 44,0 e 66,0 → 37,8 no incoerente.

**Humor:** bola − sem bola −0,024 [−0,042; −0,008]. A bola tira elogios e carinhos (que dão humor) e só devolve humor quando o pet a usa.

## Descritivos

- p(brincar | bola) 0,627 [0,560; 0,706]; o relapso quase não põe a bola (1,4 por vida: nas visitas ele sempre tem cuidado a fazer).
- Acoplado só cuidado (D4): 81–96 interações (contra 224), privação 0; humor do atencioso com bola − acoplado +0,120. A variante sem carinho
  sai igual (o atencioso não acaricia).
- Sensibilidade `bolas_por_dia`: 2 → Δp +0,299, privação +0,017; 8 → Δp +0,311, privação +0,017 (o limite diário quase não pesa:
  o atencioso já fica perto de 4 por dia).

## Leitura

1. **O primeiro objeto do mundo muda o comportamento do pet**, mesmo sem aprendizado: a política que vê a bola brinca mais com ela no
   cenário, e o dono muda a situação, não o pet. É o que a 1a-pet pedia, e passa com folga.
2. **A bola não é neutra para o cuidado**, mas por um caminho que o desenho não previu: o orçamento do dono. O desenho garantia que a
   consequência para o pet ficasse fora da cadeia que leva à morte, e isso se confirma (o braço em que o pet não vê a bola tem a mesma
   privação). O que entra na cadeia é a troca que o dono faz: num orçamento fixo, uma bola é um cuidado a menos para quem escolhe ao acaso
   e um sinal de ensino a menos para quem ensina.
3. **Para a 1a-dono (A1 + L1)** isso importa mais que a privação: com o orçamento fixo, o dono coerente que põe bolas dá cerca de 35% menos
   sinais de ensino. Um efeito da bola sobre o ensino terá de se separar dessa perda de sinais.

## Decisões para o Matheus

**Decididas pelo Matheus em 2026-10-01 (recomendação do coordenador):** B1 = (c), tirar `por_bola` do sorteio do dono aleatório nas
runs seguintes com a bola (o teste volta a medir o pet, não o orçamento do dono); B2 = a bola **fora** do orçamento na A1 + L1 (não
tira sinais do ensino); B3 = aceitar (é a regra do dono relapso). O resultado desta validação fica como está.

| # | decisão | opções |
|---|---|---|
| B1 | O que fazer com o critério "cuidado controlado" | (a) aceitar o resultado como está (a bola compete com o cuidado pelo orçamento); (b) tirar a bola do orçamento; (c) tirar `por_bola` do sorteio do aleatório; (d) medir o critério só nos donos que não deslocam cuidado |
| B2 | Orçamento na A1 + L1 | manter a bola dentro do orçamento (e medir a perda de sinais) ou fora dele |
| B3 | O relapso quase não põe a bola | aceitar (é a regra do dono) ou dar a ele uma regra própria |
