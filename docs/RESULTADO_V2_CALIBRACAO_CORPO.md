# Resultado — V2: a calibração do corpo (2026-10-12/13)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Plano: `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, seções 6 e 7, adendos 1 a 3 e o adendo 4 (os números congelados). Autorizada pelo Matheus
em 2026-10-12. Sementes de calibração 33101…33505 (K = 4, prefixo `corpo`, 20 unidades). **A validação (34101…34505) não rodou: precisa
de outro sim.** Interpretações em `docs/REGISTRO_DESVIOS.md`.

## O que rodou

| etapa | config | vidas | parede | saída |
|---|---|---|---|---|
| passo 0 (A3.2b) | `experiments/configs/v2_corpo/calibracao_passo0.json` | 480 | 57 min | `artifacts_v2_corpo/calibracao/passo0/` |
| grade (6.1), piloto (6.3), sensibilidades (6.4, A1.2) | `experiments/configs/v2_corpo/calibracao.json` | 4.320 | 80 min (6 processos) | `artifacts_v2_corpo/calibracao/grade_piloto/` |

Toda vida foi gravada e rejogada do disco bit a bit. As vidas ficam fora do git (regeneráveis da config e do código); o `meta.json` de
cada etapa traz os sha256 de `corpo.py`, `config.py`, `lobos.py`, `engine.py`, da bancada e do plano.

## Os números escolhidos

| parâmetro | valor | fechou? |
|---|---|---|
| `m_gasto` (passo 0) | **½** (basal 188/94, atividades ½) | **não**: ¼ dá 0,000 de falta, ½ dá 0,0004, 1 dá 0,49; nenhum em [0,05; 0,30] |
| (`m_sobe`, `m_reduz`) | **(2, 1)** | **não**: a solidão não chega a 0,10 sem o tédio e o estresse passarem do teto |
| `w_novos` | **2** | sim: a mediana da parcela dos novos é 0,394 |
| margens | `Δ_BE` 0,2235; `Δ_priv` 0,0295; `Δ_saude` 0,0334; `Δ_TED` 0,1633 | — |
| N da validação | **K = 4, N = 20** | todo gate com poder ≥ 0,968 |
| custo da validação | 2.400 vidas, 3,6 h de CPU, ~0,6 h com 6 processos | — |

Tabelas e regras: adendo 4 do plano.

## As duas faixas que não fecharam

- **O metabolismo quase não pesa no ponto escolhido.** Com o gasto pela metade, o combustível fica em falta em 0,04% do tempo acordado; com
  o gasto inteiro, em metade. A grade de três pontos salta por cima da faixa. A regra escolhe o ½; uma grade mais fina entre ½ e 1 seria
  decisão do Matheus.
- **A solidão quase nunca enche.** Em 8 dos 9 pontos a fração com a solidão ≥ 0,75 fica abaixo de 0,03: os donos da v1 acariciam o bastante
  (o carinho tira 180000 de uma vez). Só subindo tudo e reduzindo pela metade (2, ½) ela passa de 0,10, e aí o tédio e o estresse ficam
  cheios em ~80% do tempo. A regra escolhe o (2, 1): tédio 0,213 e estresse 0,137 na faixa, solidão 0,028 fora.

## O piloto (só para o N e as margens; **não é evidência**)

Médias por braço, nas 8 células e nos dias 8 a 14 (o `bola` e o `padrao` juntos):

| braço | `BE` | privação | saúde | tédio |
|---|---|---|---|---|
| P0-q / P0-c | 0,638 / 0,638 | 0,118 | 0,866 | — / 0,334 |
| P1-q | 0,168 | 0,108 | 0,879 | — |
| P1-c | 0,878 | 0,106 | 0,881 | 0,330 |
| P1-q^ac / P1-c^ac | 0,158 / 0,848 | 0,109 / 0,108 | 0,879 / 0,881 | — / 0,333 |
| P1-hoje / P1-química | 0,150 / 0,152 | 0,107 / 0,105 | 0,885 / 0,883 | — |

- O P1-q repete o pet parado do N3 (`BE` 0,17). O P1-c sai do parado no piloto (P1-c − P1-q em `BE`, `bola`: +0,67 [+0,64; +0,70]), sem
  piorar o cuidado (privação −0,002 [−0,005; +0,001]). **Esses contrastes só calculam o N:** a leitura é da validação.
- O G-P0C vale no piloto (160 de 160 células).
- Nas vidas que aprendem pela consequência, quase nenhum peso no teto (o P3, pelo dono, 9 e 11 vidas de 160).

## O que fica para o Matheus

1. **A validação do corpo** (34101…34505, K = 4, 2.400 vidas, ~0,6 h com 6 processos): precisa de outro sim.
2. **As duas faixas que não fecharam:** seguir com os pontos da regra (½ no gasto; (2, 1) no corpo) ou uma grade mais fina antes da validação.
   Uma grade nova seria uma calibração de novo, nas mesmas sementes, e pede um adendo antes.

## Adendo 5 (2026-10-13): só o passo 0 fino rodou

Decisão do Matheus (2026-10-13): uma grade mais fina antes da validação, pelo adendo 5 do plano, nas mesmas sementes. Depois, outra
decisão: faixa que não fecha não bloqueia, e do adendo 5 fica **só o passo 0**.

**O passo 0 fino (A5.1, A5.6)** rodou o P0-q em `m_gasto` ∈ {3/5, 7/10, 4/5, 9/10}, nas 20 unidades e nas 8 células (640 vidas, 24 min
com 4 processos). A regra lê os sete pontos juntos (os três da A3.2c vêm do passo0.json de antes). Os números estão em
`artifacts_v2_corpo/calibracao/adendo5/passo0/passo0.json`:

| `m_gasto` | ¼ | ½ | 3/5 | 7/10 | **4/5** | 9/10 | 1 |
|---|---|---|---|---|---|---|---|
| fração acordado com a falta | 0,000 | 0,0004 | 0,0023 | 0,0064 | **0,2018** | 0,3678 | 0,4903 |

- **`m_gasto` = 4/5, fechou** (basal 300/150; atividades 4/5). Só ele fica em [0,05; 0,30].
- A falta salta de 0,6% em 7/10 para 20% em 4/5: entre os dois, o gasto passa a exceder o que a digestão repõe.

**O que não rodou (A5.7):** a grade da solidão (27 pontos com o `m_sol`), o piloto, as sensibilidades, as margens, o N e o custo.
- A config está em `experiments/configs/v2_corpo/calibracao_adendo5.json`. Ela valida, mas não tem saída.
- O ponto (2, 1) e os números do adendo 4 seguem registrados, mas foram medidos com o gasto em ½.
- Como o gasto mudou, eles não valem como estão para o corpo com 4/5. A calibração final será com a estrutura completa.
