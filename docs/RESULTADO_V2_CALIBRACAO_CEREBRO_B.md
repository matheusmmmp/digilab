# Resultado — calibração do cérebro B (comparação dos DigiBrains)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Tarefa `docs/TAREFA_V2_CALIBRACAO_CEREBROS_B_C.md` (rodada 11); plano `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`, adendo 1.1 (grades e
regras conferidas pelo coordenador). Run única em 2026-10-06, commit `d9b28a1` (orquestrador `experiments/run_v2_calibracao_cerebro_b.py`,
cérebro `digilab/policies/cerebro_b.py`; os sha256 de ambos e do plano estão no `meta.json`). Sementes de calibração 28101…28505, K = 4
(20 unidades), prefixo `comparacao-cerebros`, 14 dias, dono atencioso; nas peças comuns, o ponto da K2 do A (ganho 4, T3, K4, montagem
completa). **660 vidas em 25 min**, todas gravadas e rejogadas do disco bit a bit. Teto: 1260 vidas e 4 × 15.093 s (a K2 do A). Todo
número abaixo vem de `artifacts_v2_comparacao_cerebros/calibracao_B/` (`{B-A,B-B,B-C,B-D}/resultado.json`, `piloto.json`,
`escolha.json`, `meta.json`, `pontos/*/*/medidas.json`, `run.log`); as vidas ficam fora do git e se regeneram da config e do código.

**Status: o B NÃO FECHA, pelo critério "não aprende" (seção 7).** No ponto escolhido, a parte aprendida muda a escolha em menos de 1% das
decisões do P1. Pelo plano, o B sai da escolha M6, com o motivo registrado como resultado; a comparação segue com o A e o C.

## 1. O ponto escolhido

| etapa | parâmetro | grade | escolhido | a regra fechou? | medida |
|---|---|---|---|---|---|
| B-A | `taxa_ator` | 0,01; 0,03; 0,1 | **0,01** | sim | nenhuma vida com logit no limite; razão da deriva 2,70, 3,62 e 4,22 |
| B-B | `taxa_critico` | 0,01; 0,03; 0,1 | **0,1** | sim | razão 2,87, 2,70 e 2,63 |
| B-C | `lambda_elegibilidade` | 0,5; 0,8; 0,95 | **0,95** | sim | razão 2,70, 2,63 e 2,15 |
| B-D | `w0_info` | 0,5; 1,0; 2,0 | **0,5** | sim | escolhas de fruta decididas pela informação 0,154 [0,130; 0,180]; 0,286 e 0,355 nos outros |

- **Estabilidade (B-A a B-C):** nenhuma vida chegou ao limite do logit (|z| = 20) em nenhum ponto, então a regra escolhe pela menor razão
  da deriva (JSD ao instinto, dia 14 / dia 7, média das três condições). Em todos os pontos a razão fica acima de 2: a deriva ainda cresce
  no fim da vida, como no A (2,72 na K2).
- **Manipulação (B-D):** o menor `w0_info` já passa o piso de 0,069 com folga. A referência descritiva com `w0_info` 0: 1 de 1541 escolhas
  decididas pela informação (o B quase não aprende a ler a informação sozinho).

## 2. O piloto do "não aprende" (seção 7)

Nas 60 vidas do P1 no ponto escolhido (o `w0_info` não age no P1, que não tem informante), IC 95% por unidade, as três condições juntas:

| critério | medida | limiar | resultado |
|---|---|---|---|
| deriva ao instinto no dia 14 | 4,30 × 10⁻⁵ bit [3,50 × 10⁻⁵; 5,09 × 10⁻⁵] | limite inferior ≤ 0 | não dispara (a deriva é positiva) |
| o aprendido muda a escolha | **0,0077 [0,0065; 0,0089]** | limite superior < 0,01 | **dispara: não aprende** |

Descritivo, P2 no ponto escolhido: deriva 4,50 × 10⁻⁵ e fração 0,0075 [0,0064; 0,0087].

## 3. O que a run mostra além da regra (descritivo, sem mudar nada)

A fração das decisões em que o aprendido muda a escolha, por ponto do P1 (as 60 vidas):

| ponto (ator, crítico, λ) | fração |
|---|---|
| 0,1; 0,03; 0,8 | 0,203 |
| 0,03; 0,03; 0,8 | 0,064 |
| 0,01; 0,01; 0,8 | 0,024 |
| 0,01; 0,03; 0,8 | 0,022 |
| 0,01; 0,1; 0,5 | 0,022 |
| 0,01; 0,1; 0,8 | 0,016 |
| **0,01; 0,1; 0,95 (o escolhido)** | **0,008** |

A regra de estabilidade escolhe, em cada etapa, o ponto de menor razão da deriva, e isso empurrou a cadeia para o ponto em que o B menos
aprende: a taxa do ator mais baixa, o crítico mais alto (que absorve o sinal antes do ator) e o λ mais alto. Com a taxa do ator 0,1 o
aprendido decidiria 20% das decisões, acima do limiar. É o risco 2 do plano (o B pode não aprender com tão poucas consequências), com uma
parte que vem da regra: a regra herdada da K-4 premia a deriva que assenta, e no B a deriva só assenta quando quase não há aprendizado. Pelo plano, nada é
recalibrado olhando o piloto; a leitura e o que fazer ficam para o coordenador e o Matheus.

## 4. Decisões e interpretações (no `REGISTRO_DESVIOS`)

- **A memória do B só anda com a decisão observada** (mudança no `cerebro_b.py` antes da run): a sonda da deriva sorteia várias decisões
  no mesmo estado e não pode mover o estado oculto. Nas vidas é o mesmo de antes.
- **A deriva no meio e no fim da vida** (dias 7 e 14), não em todo dia: são os que as regras e o piloto leem.
- **Regra de manipulação pela régua da K-3:** limite inferior do IC 95% > 0,069, sobre as escolhas com duas frutas ou mais **e informação
  vigente**, a vida inteira, as três condições juntas por unidade (o adendo não traz janela de dias).
- **O piloto reaproveita as vidas do P1 no ponto escolhido** (já rodadas na B-C): nenhuma vida a mais.
- **Empates:** o menor valor da grade, como na K2.
