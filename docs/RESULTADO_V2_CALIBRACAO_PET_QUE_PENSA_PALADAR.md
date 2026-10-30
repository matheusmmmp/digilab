# Resultado — V2: a calibração do pet que pensa com o paladar (J5, adendo 3)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Data: 2026-10-14. Plano: `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`, adendo 3 (A3.2 a A3.5), com os números congelados no adendo 4.
Autorizada pelo Matheus em 2026-10-14.

**Fonte dos números:** `artifacts_v2_pet_que_pensa/calibracao_paladar/`:
- `ganho_gosto/ganho_gosto.json`, `ganho_gosto/ganho_<g>/{medidas,meta}.json` e o `meta.json` do passo;
- `g_plano/g_plano.json`, `g_plano/g_plano_<g>/{medidas,meta}.json` e o `meta.json` do passo;
- `reval.json`;
- `g_plano/piloto/piloto.json` e `g_plano/piloto/<braço>/{medidas,meta}.json`.

As vidas (`vidas/*.jsonl`) ficam fora do git e saem de novo da config e do código.

- **O comando,** um por passo: `python experiments/run_v2_calibracao_pet_que_pensa_paladar.py --config
  experiments/configs/v2_pet_que_pensa/calibracao_paladar.json --saida artifacts_v2_pet_que_pensa/calibracao_paladar --passo <passo>`,
  com `--processos 3` (o `ganho_gosto` e o `g_plano`) e `--processos 4` (o piloto).
- **A run:** a `main` `9b1f5c6`, com a árvore limpa, numa worktree própria; Python 3.13.0, Windows. O `meta.json` de cada passo traz o
  sha256 do pacote da bancada.
- **O tempo:** o `ganho_gosto` levou 36 s, o `g_plano` 43 s e o piloto 126 s. A run inteira levou cerca de 5 min.
- **As sementes:** as bases 49101…49505 (K_u = 4, prefixo `pet_que_pensa`, 20 unidades). A validação (46101…) não rodou.
- **O replay:** toda vida foi gravada e rejogada do texto do disco, bit a bit, e o replay da medição também foi conferido. Os gates de
  mecanismo (G-SEM-CREDITO, o congelamento, o G2) passaram em toda vida.

## Resumo

- **O `ganho_gosto` = S/2 (512), "não fechou".** Nenhum ponto da grade põe a fração de fruta em [0,25; 0,60]: a média ficou em 0,202
  (S/2), 0,196 (S) e 0,196 (2S). Pela regra, fica o mais perto da faixa, o S/2, a 0,048 abaixo dela.
- **O `g_plano` = S (1024), fechou** (0,1155 em [0,10; 0,40]).
- **A G-REVAL-POSSIVEL passa:** nenhuma unidade falha.
- **O piloto repete o adendo 1:** nenhum braço escolhe a x antes da mudança (`f_antes` = 0 em toda unidade com oportunidade), então
  `Δ_T1` = 0. O `Δ_T2` = 0,30, mas nenhuma unidade de nenhum braço teve busca da x depois da mudança.
- **Pela seção 6, a validação não roda, e o plano volta ao Matheus.** O N não foi calculado.

## 1. O `ganho_gosto` (o P1, só a fase 1)

| `ganho_gosto` | média da fração de fruta (dias 4 a 6) | por unidade | consumos no mapa | frutas maduras | CPU por vida |
|---|---|---|---|---|---|
| **S/2 (512)** | **0,2024** | 0,000 a 0,419 | 575 | 120 | 0,42 s |
| S (1024) | 0,1960 | 0,000 a 0,350 | 575 | 116 | 0,42 s |
| 2S (2048) | 0,1960 | 0,000 a 0,350 | 575 | 116 | 0,42 s |

- **O `ganho_gosto` quase não muda a vida:** 19 das 20 unidades têm a mesma fração nos três pontos. O S e o 2S são iguais nas 20.
- **Não é o teto dos pesos:** nenhum peso das classes `comida:<tipo>` chega a prior ± teto no fim da fase 1, em nenhum ponto.
- **Não é um gosto fraco:** o f_gosto quando o pet come a x é, em média, 135 (S/2) e 546 (2S). Na ração, de 1 a 4, porque o `salgado`
  satura.
- **O que o descritivo sugere:** o pet come a fruta que encontra, e o gosto mexe pouco no quanto ele a procura. A ração continua sendo o
  que ele mais come nas 20 unidades. É leitura do descritivo, não teste.

## 2. O `g_plano` (o P1-plan, só a fase 1, no `ganho_gosto` = S/2)

| `g_plano` | média da fração da sonda (dias 4 a 6) | por unidade | decisões com alvo | o plano mudou a escolha |
|---|---|---|---|---|
| S/4 (256) | 0,0447 | 0,000 a 0,092 | 1.062 | 48 |
| S/2 (512) | 0,0801 | 0,036 a 0,151 | 1.029 | 85 |
| **S (1024)** | **0,1155** | 0,000 a 0,289 | 1.040 | 119 |

É o mesmo ponto do adendo 1 (lá, 0,1001).

## 3. A G-REVAL-POSSIVEL (sem vida, no `ganho_gosto` = S/2)

- **Passa:** 0 de 20 unidades falham. A x sorteou `a` em 9 unidades, `b` em 6 e `c` em 5.
- **A x depois da mudança** fica abaixo da ração em todas as unidades. Em 19, ela fica abaixo também das duas outras frutas; na outra, de
  uma.
- **O sinal da x** vai de 6 a 540, e o da ração é 1046. A menor folga até a alternativa mais perto é 17.

## 4. O piloto (os 4 braços, T1 e T2, no `ganho_gosto` = S/2 e no `g_plano` = S)

**As premissas (só relato):**

| premissa | P1 | P1-plan | P1-plan-desfecho | P1-plan-cong |
|---|---|---|---|---|
| G-APRENDEU (`f_antes`, IC95) | 0 [0; 0], n 16 | 0 [0; 0], n 15 | 0 [0; 0], n 15 | 0 [0; 0], n 15 |
| G-OPORTUNIDADE, T1 (sem oportunidade) | 6 de 20 | 7 de 20 | 7 de 20 | 7 de 20 |
| G-OPORTUNIDADE, T2 | 20 de 20 | 20 de 20 | 20 de 20 | 20 de 20 |
| G-EXPOSICAO (sem exposição) | 12 de 20 | 10 de 20 | 10 de 20 | 10 de 20 |

As três premissas falham em todos os braços, como no adendo 1.

**As margens:** `Δ_T1` = 0,000 (15 unidades com oportunidade antes, nenhuma escolha de x) e `Δ_T2` = 0,300 (10 unidades com busca
antes). **O T1 fica sem espaço (≤ 0,05).**

**Os contrastes** (descritivo, não é evidência): o G-T1 e o G-T1-DESF têm média 0, e o G-T1-CONG 0,051 (13 unidades). O G-T2 e os
secundários dele não têm nenhuma unidade com valor.

**O descritivo do paladar** (P1-plan, T1):
- **A fração de fruta na fase 1** vai de 0,04 a 0,36 por unidade, e a ração é o tipo mais comido nas 20 unidades.
- **A x comida antes da mudança:** de 0 a 12 vezes por unidade (0 em 6 unidades).
- **Os pesos das classes no fim da fase 1** (o retrato do dia 7, média sobre as unidades):

  | regra | `comida:<x>` | `comida:racao` |
  |---|---|---|
  | `fome_moderada` | 49 | 165 |
  | `fruta_no_cenario` | 72 | 175 |
  | `pedido_necessidade` | 64 | 67 |

  O querer aprendido vai à ração, não à favorita.
- **A leitura** (sem teste): a oportunidade do T1 pede a fome ≤ S/2, e é com fome que a nutrição da ração pesa mais. O próprio desenho
  diz isso (`docs/futuro/paladar.md`, seção 3.4: "com fome alta, a nutrição da ração ainda pesa mais; com a fome baixa, o gosto decide").
  O gosto age onde a oportunidade do T1 não olha.

**O custo:** 0,61 s de CPU por vida no P1 e de 0,74 s nos braços com o planejador (0,71 s em média). Com 8 vidas por unidade, N = 50
daria 400 vidas, cerca de 5 min de CPU.

## 5. O que fica para o Matheus

- **O plano volta pela seção 6:** o T1 não tem margem, e o paladar, nos números PROPOSTOS, não mudou isso.
- **Opções** (para decisão, não aplicadas; nada foi recalibrado olhando o piloto):
  - **mudar a definição da oportunidade do T1:** a fome ≤ S/2 olha justo onde a nutrição domina. Mexer nela muda a primária (um adendo
    novo, antes de rodar de novo);
  - **mexer no mundo,** pelo RP-2 do desenho (`docs/futuro/paladar.md`, seção 10): o dono pôr a fruta ao lado da ração. É uma peça fora
    deste desenho;
  - **aceitar o resultado como negativo:** com o paladar e o mundo de hoje, o pet não escolhe a favorita na hora em que o T1 mede.
- **A faixa do `ganho_gosto` não fechou,** e a grade quase não muda a vida. Se o paladar continuar, o número a calibrar talvez não seja
  o ganho.
