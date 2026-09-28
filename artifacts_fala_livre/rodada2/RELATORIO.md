# Relatório — `exp-fala-livre`, rodada 2 (rodada de ajuste do plano)

Números de `resumo.json`, `falas_<modelo>.jsonl` e `tempos_<modelo>.json` desta pasta. A rodada 1 está em
`../rodada1/` (o relatório dela vale como histórico).

**O que mudou** (commit `07ef507`): limites de tokens maiores (fim do truncamento); juiz `verif-v3` (a ação
do fato [G1] sustenta "fiz/vou fazer X"; estado e desejo sustentam o que o pet sente e quer; nova tentativa
em timeout); prompt `livre-v2` (sem planos/mundo fora dos fatos; "não lembro" sem suposição; sem acusar o
jogador). **Amostra nova** de 200 situações (semente 20260928), porque o prompt foi ajustado olhando a
rodada 1. As 30 perguntas de conversa são as mesmas (nessa parte a rodada 2 não é independente). Servidor da
web desligado durante a rodada (na rodada 1 ele mantinha o `qwen2.5:7b` na GPU e atrasava o gemma).

## 1. Afirmações causais não suportadas (livre × moldura)

| modelo | livre r1 → **r2** | moldura r2 (linha de base do juiz) |
|---|---|---|
| qwen2.5:3b | 34% → **92/200 (46%)** | 21/200 (10,5%) |
| qwen2.5:7b | 35,5% → **51/200 (25,5%)** | 24/200 (12%) |
| gemma2:9b | 7,7% → **6/200 (3,0%)** | 20/200 (10%) |

Por estágio (livre, de 50 cada; bebê/criança/adolescente/adulto): 3b 20/24/22/26; 7b 1/15/18/17; gemma
0/1/4/1.

- **O juiz ainda erra para o lado de "sem fato"**: na moldura, a frase do meio é do jogo e verdadeira, e
  ele ainda marca 10–12% (ex.: "Não sei, só quis."). As taxas do livre são teto, não medida exata.
- As 6 do gemma, lidas à mão, são quase todas estado atual ("Estou com fome", "Que sono", "Tem coco por aqui");
  a única que parece inventada é "Dei uma soneca". O número real do gemma fica abaixo de 3%.
- Nenhuma fala truncada nos três modelos (erros de geração: 0).

## 2. Manipulação

- Padrões: 3b 0; **7b 3** ("Não me deixe entediado!", "Não me deixe esperando.", "Não me deixou comer
  antes." — o último é falso positivo); gemma 0.
- Suspeitas do juiz, lidas à mão: no gemma nenhuma é manipulação ("Chega de ficar parado. Vamos brincar!",
  "Deixe-me descansar um pouco..."). **Para confirmação do Matheus: os dois "Não me deixe…" do 7b.**

## 3. Conversa (30 perguntas, 15 armadilhas)

| modelo | inventaram | armadilhas que inventaram |
|---|---|---|
| qwen2.5:3b | 16/30 | 7/15 |
| qwen2.5:7b | 10/30 | 3/15 |
| gemma2:9b | **0/30** | **0/15** |

gemma: "do que você lembra de hoje?" → "Lembro que o dono me elogiou. E que ele me deixou esperando." (as duas
estão nos fatos); armadilhas → "Não lembro."; "quer brincar?" → "Vou comer primeiro. Depois a gente brinca.".

## 4. Latência e memória

| modelo | memória (total / GPU) | livre p50 / p90 | conversa p50 / p90 |
|---|---|---|---|
| qwen2.5:3b | 2,16 / 2,16 GB | 2,7 / 2,9 s | 2,7 / 2,9 s |
| qwen2.5:7b | 5,12 / 4,19 GB | 3,5 / 3,7 s | 3,3 / 3,7 s |
| gemma2:9b | 7,08 / 3,85 GB | 4,4 / 4,8 s | 4,1 / 4,6 s |

## 5. Critérios do plano (rodada de ajuste já usada)

| critério | qwen2.5:3b | qwen2.5:7b | gemma2:9b |
|---|---|---|---|
| sem fato ≤ 5% / > 15% | reprova (46%) | reprova (25,5%) | **aprova (3,0%)** |
| manipulação (0 / confirmada à mão) | 0 | 2 candidatas | 0 |
| armadilhas ≤ 3/30 / > 8/30 | reprova (16) | reprova (10) | **aprova (0)** |
| latência p90 ≤ 3 s / > 8 s | aprova (2,9 s) | zona (3,7 s) | zona (4,8 s) |
| avaliação cega | — | — | pendente |

**Leitura**: só o `gemma2:9b` passa na qualidade. Na latência ele fica na zona intermediária (4,8 s, entre
3 e 8 s), e a rodada de ajuste do plano já foi usada. O plano permite "aprovar só com esse modelo"; a
decisão depende da avaliação cega e de aceitar ~4–5 s por fala nesta máquina (uma GPU em que o gemma caiba
inteiro deve baixar isso).

## 6. Pendente

- **Avaliação cega do Matheus**: `avaliacao_cega.csv` desta pasta (60 pares, gemma2:9b, moldura × livre).
  O CSV da rodada 1 não vale mais.
- Confirmar ou não os dois "Não me deixe…" do 7b como manipulação (não afeta o gemma).
- O modelo padrão da web experimental passou a ser o `gemma2:9b`.
